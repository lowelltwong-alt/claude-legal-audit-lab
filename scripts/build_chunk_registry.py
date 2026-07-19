#!/usr/bin/env python3
"""Build, validate, and check byte-exact candidate chunks for the pinned tree."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Iterable

from jsonschema import Draft202012Validator

from public_safety import public_content_violations

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream" / "claude-for-legal"
POLICY = ROOT / "registry" / "chunk-policy.json"
POLICY_SCHEMA = ROOT / "schemas" / "chunk-policy.schema.json"
REGISTRY_SCHEMA = ROOT / "schemas" / "chunk-registry.schema.json"
MIGRATION_SCHEMA = ROOT / "schemas" / "chunk-id-migration.schema.json"
SOURCE_REGISTRY = ROOT / "registry" / "source-registry.json"
OUT = ROOT / "registry" / "chunk-registry.json"
MIGRATION_OUT = ROOT / "registry" / "chunk-id-migration.json"

FORMAT_VERSION = "2.0.0"
LEGACY_FORMAT_VERSION = "1.0.0"
GENERATOR_VERSION = "2.0.0"
REPOSITORY_ID = "anthropics/claude-for-legal"
CHUNK_PREFIX = "chk:sha256:"
PARENT_PREFIX = "parent:sha256:"
EDGE_PREFIX = "edge:sha256:"
FORBIDDEN_PUBLIC_SUBSTRINGS = (
    ".private/",
    "private/",
    "raw-research",
    "raw_capture",
    "raw-capture",
    "BEGIN PRIVATE KEY",
    "AWS_SECRET",
    "api_key=",
    "authorization: bearer",
    "c:\\users\\",
)
INVERSE_EDGE_TYPES = {
    "NEXT_IN_PARENT": "PREVIOUS_IN_PARENT",
    "PREVIOUS_IN_PARENT": "NEXT_IN_PARENT",
    "MODIFIES_PATH": "MODIFIED_BY",
    "MODIFIED_BY": "MODIFIES_PATH",
    "DERIVED_FROM": "HAS_DERIVATIVE",
    "HAS_DERIVATIVE": "DERIVED_FROM",
}


def canon(payload: object) -> bytes:
    """Canonical public artifact bytes: pretty, sorted UTF-8 JSON plus LF."""
    return (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def compact_canon(payload: object) -> bytes:
    """Canonical identity bytes: compact, sorted UTF-8 JSON with no newline."""
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_id(prefix: str, material: object) -> str:
    return prefix + sha256(compact_canon(material))


def cid(identity: dict) -> str:
    return digest_id(CHUNK_PREFIX, identity)


def parent_id(material: dict) -> str:
    return digest_id(PARENT_PREFIX, material)


def edge_id(edge_type: str, source_chunk_id: str, target_chunk_id: str) -> str:
    return digest_id(
        EDGE_PREFIX,
        {
            "edge_type": edge_type,
            "policy_revision": FORMAT_VERSION,
            "source_chunk_id": source_chunk_id,
            "target_chunk_id": target_chunk_id,
        },
    )


def legacy_cid(parent: str, locator: str, content_sha256: str) -> str:
    material = (
        f"{LEGACY_FORMAT_VERSION}\0static_file_span\0{parent}\0{locator}\0{content_sha256}"
    ).encode("utf-8")
    return "CHK-" + sha256(material)[:16].upper()


def line_for(data: bytes, offset: int) -> int:
    return data[:offset].count(b"\n") + 1


def is_utf8_boundary(data: bytes, offset: int) -> bool:
    if offset < 0 or offset > len(data):
        return False
    if offset == 0 or offset == len(data):
        return True
    return (data[offset] & 0xC0) != 0x80


@lru_cache(maxsize=8)
def _compiled_schema_validator(
    schema_digest: str, schema_bytes: bytes
) -> Draft202012Validator:
    """Compile a schema once per exact content digest.

    The byte payload is deliberately part of the cache key: path-only or
    timestamp-only caching could silently validate against stale policy after
    an in-place schema edit.
    """
    if sha256(schema_bytes) != schema_digest:
        raise ValueError("schema cache key does not match schema content")
    schema = json.loads(schema_bytes.decode("utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def schema_errors(schema_path: Path, payload: object) -> list[str]:
    schema_bytes = schema_path.read_bytes()
    validator = _compiled_schema_validator(sha256(schema_bytes), schema_bytes)
    return [
        f"{schema_path.name}: {error.message}"
        for error in sorted(
            validator.iter_errors(payload),
            key=lambda error: (list(error.absolute_path), error.message),
        )
    ]


def load_json_object(path: Path, label: str) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"ERROR: cannot read {label}: {exc}") from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: malformed {label} JSON at {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"ERROR: malformed {label}: expected a JSON object")
    return payload


def activated_kinds(policy: dict) -> set[str]:
    raw = policy.get("activated_chunk_kinds")
    if not isinstance(raw, list):
        return set()
    return {item for item in raw if isinstance(item, str)}


def validate_policy(policy: dict) -> list[str]:
    errors = schema_errors(POLICY_SCHEMA, policy)
    if policy.get("format_version") != FORMAT_VERSION:
        errors.append(f"unsupported chunk policy format_version: {policy.get('format_version')!r}")
    if policy.get("output") != "registry/chunk-registry.json":
        errors.append("chunk policy output must remain registry/chunk-registry.json")
    if policy.get("migration_output") != "registry/chunk-id-migration.json":
        errors.append("chunk migration output must remain registry/chunk-id-migration.json")
    designed = policy.get("chunk_kinds")
    expected_designed = {"static_file_span", "pr_file_record", "web_capture_span"}
    if not isinstance(designed, list) or set(designed) != expected_designed:
        errors.append("chunk_kinds must contain exactly the three governed chunk kinds")
    activated = activated_kinds(policy)
    if "static_file_span" not in activated:
        errors.append("activated_chunk_kinds must include static_file_span")
    for kind in activated:
        if kind not in expected_designed:
            errors.append(f"activated kind {kind!r} is not a governed chunk kind")
    for gated in ("pr_file_record", "web_capture_span"):
        if gated in activated:
            errors.append(
                f"{gated!r} is designed but not implemented; remove it from activated_chunk_kinds"
            )
    privacy = policy.get("privacy", {})
    if privacy.get("forbidden_path_prefixes") != [".private/", "private/"]:
        errors.append("privacy.forbidden_path_prefixes must fail closed for both private roots")
    return errors


def partition_static_file(data: bytes, lines_per_chunk: int = 200) -> list[tuple[int, int]]:
    """Return ordered [start, end) spans covering every byte exactly once."""
    data.decode("utf-8")
    starts = [0]
    starts.extend(i + 1 for i, byte in enumerate(data) if byte == 10)
    if not data:
        starts = [0]
    spans: list[tuple[int, int]] = []
    for index in range(0, len(starts), lines_per_chunk):
        start = starts[index]
        end = (
            starts[index + lines_per_chunk]
            if index + lines_per_chunk < len(starts)
            else len(data)
        )
        if not is_utf8_boundary(data, start) or not is_utf8_boundary(data, end):
            raise ValueError(f"UTF-8 code point would be split at [{start},{end})")
        spans.append((start, end))
    return spans


def _git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _parse_batch_blobs(repo: Path, object_ids: list[str]) -> list[bytes]:
    if not object_ids:
        return []
    raw = _git(repo, "cat-file", "--batch", input_bytes=("\n".join(object_ids) + "\n").encode("ascii"))
    position = 0
    bodies: list[bytes] = []
    for expected_oid in object_ids:
        header_end = raw.find(b"\n", position)
        if header_end < 0:
            raise RuntimeError("git cat-file --batch returned a truncated header")
        header = raw[position:header_end].decode("ascii", errors="strict")
        position = header_end + 1
        parts = header.split()
        if len(parts) != 3 or parts[0] != expected_oid or parts[1] != "blob":
            raise RuntimeError(f"unexpected git cat-file header: {header!r}")
        size = int(parts[2])
        body = raw[position : position + size]
        if len(body) != size or raw[position + size : position + size + 1] != b"\n":
            raise RuntimeError("git cat-file --batch returned a truncated blob")
        bodies.append(body)
        position += size + 1
    if position != len(raw):
        raise RuntimeError("git cat-file --batch returned trailing bytes")
    return bodies


@lru_cache(maxsize=8)
def git_tree_snapshot(repo_text: str, commit: str) -> tuple[tuple[str, str, bytes], ...]:
    """Return UTF-8 blob bytes from the immutable tree, never working-tree bytes."""
    repo = Path(repo_text)
    raw = _git(repo, "ls-tree", "-r", "-z", "--full-tree", commit)
    entries: list[tuple[str, str]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, path_bytes = record.split(b"\t", 1)
        mode, object_type, object_id = metadata.decode("ascii").split()
        del mode
        if object_type != "blob":
            continue
        path = path_bytes.decode("utf-8", errors="strict")
        entries.append((path, object_id))
    entries.sort(key=lambda item: item[0].encode("utf-8"))
    bodies = _parse_batch_blobs(repo, [object_id for _, object_id in entries])
    snapshot: list[tuple[str, str, bytes]] = []
    for (path, object_id), body in zip(entries, bodies, strict=True):
        try:
            body.decode("utf-8")
        except UnicodeDecodeError:
            continue
        snapshot.append((path, object_id, body))
    return tuple(snapshot)


@lru_cache(maxsize=1)
def known_source_ids() -> frozenset[str]:
    payload = load_json_object(SOURCE_REGISTRY, "source registry")
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise SystemExit("ERROR: malformed source registry: sources must be an array")
    return frozenset(
        source["source_id"]
        for source in sources
        if isinstance(source, dict) and isinstance(source.get("source_id"), str)
    )


def make_parent_material(source_id: str, commit: str, path: str, blob_oid: str, data: bytes) -> dict:
    return {
        "content_sha256": sha256(data),
        "git_blob_oid": blob_oid,
        "kind": "git_blob",
        "path": path,
        "repository": REPOSITORY_ID,
        "source_id": source_id,
        "source_revision": commit,
    }


def make_identity(
    *,
    source_id: str,
    commit: str,
    parent: str,
    locator: dict,
    content_sha256: str,
) -> dict:
    return {
        "chunk_kind": "static_file_span",
        "content_sha256": content_sha256,
        "locator": locator,
        "parent_id": parent,
        "policy_revision": FORMAT_VERSION,
        "source_id": source_id,
        "source_revision": commit,
    }


def make_edge(edge_type: str, source_chunk_id: str, target_chunk_id: str) -> dict:
    edge_identity = edge_id(edge_type, source_chunk_id, target_chunk_id)
    inverse_type = INVERSE_EDGE_TYPES[edge_type]
    return {
        "authority_class": "candidate_evidence",
        "creation_method": "deterministic_partition",
        "edge_id": edge_identity,
        "edge_type": edge_type,
        "inverse_edge_id": edge_id(inverse_type, target_chunk_id, source_chunk_id),
        "limitation": "A deterministic adjacency edge preserves source order; it does not establish semantic or causal relation.",
        "policy_revision": FORMAT_VERSION,
        "review_status": "candidate",
        "source_chunk_id": source_chunk_id,
        "target_chunk_id": target_chunk_id,
    }


def _walk_keys(value: object) -> Iterable[str]:
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key
            yield from _walk_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk_keys(nested)


def _path_is_safe(path: str) -> bool:
    if not path or "\\" in path or path.startswith("/") or re.match(r"^[A-Za-z]:", path):
        return False
    parts = PurePosixPath(path).parts
    return all(part not in {"", ".", ".."} for part in parts)


def validate_registry_payload(
    payload: dict,
    allowed_kinds: set[str] | None = None,
    *,
    policy: dict | None = None,
    upstream: Path = UPSTREAM,
) -> list[str]:
    """Validate schema plus all reproducible cross-record invariants."""
    errors = schema_errors(REGISTRY_SCHEMA, payload)
    policy = policy if policy is not None else load_json_object(POLICY, "chunk policy")
    allowed = allowed_kinds if allowed_kinds is not None else activated_kinds(policy)
    rendered = canon(payload).decode("utf-8", errors="replace")
    lowered = rendered.lower()
    for needle in FORBIDDEN_PUBLIC_SUBSTRINGS:
        if needle.lower() in lowered:
            errors.append(f"public chunk registry must not contain {needle!r}")
    for violation in public_content_violations(payload):
        errors.append(f"public chunk registry contains forbidden content: {violation}")
    banned_fields = set(policy.get("privacy", {}).get("forbidden_embedded_fields", []))
    for key in _walk_keys(payload):
        if key in banned_fields:
            errors.append(f"public chunk registry must not embed field {key!r}")

    lock = load_json_object(ROOT / "UPSTREAM.lock.json", "UPSTREAM.lock.json")
    commit = lock.get("commit")
    if payload.get("pinned_commit") != commit:
        errors.append("pinned_commit must equal UPSTREAM.lock.json")
    if payload.get("format_version") != FORMAT_VERSION:
        errors.append("registry format_version must equal the active policy revision")
    if payload.get("policy_sha256") != sha256(POLICY.read_bytes()):
        errors.append("policy_sha256 does not match registry/chunk-policy.json")
    build = payload.get("build")
    if isinstance(build, dict) and set(build.get("activated_chunk_kinds", [])) != allowed:
        errors.append("build.activated_chunk_kinds does not match policy activation")

    try:
        tree = git_tree_snapshot(str(upstream.resolve()), str(commit))
    except (OSError, RuntimeError, UnicodeError) as exc:
        errors.append(f"cannot validate pinned Git tree: {exc}")
        tree = ()
    tree_by_path = {path: (blob_oid, data) for path, blob_oid, data in tree}
    expected_paths = set(tree_by_path)
    source_ids = known_source_ids()
    chunks = payload.get("chunks")
    if not isinstance(chunks, list):
        return errors

    seen_ids: dict[str, bytes] = {}
    groups: dict[str, list[dict]] = defaultdict(list)
    observed_paths: set[str] = set()
    global_order: list[tuple[tuple[str, ...], int, str]] = []
    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            errors.append(f"chunk[{index}] must be an object")
            continue
        chunk_kind = chunk.get("chunk_kind")
        if chunk_kind not in allowed:
            errors.append(f"inactive chunk_kind emitted without activation gate: {chunk_kind!r}")
        identity = chunk.get("identity")
        exact_locator = chunk.get("exact_locator")
        parent = chunk.get("parent")
        if not isinstance(identity, dict) or not isinstance(exact_locator, dict) or not isinstance(parent, dict):
            errors.append(f"chunk[{index}] lacks identity, parent, or exact locator object")
            continue
        if identity.get("locator") != exact_locator:
            errors.append(f"chunk[{index}] identity locator differs from exact_locator")
        if identity.get("parent_id") != parent.get("parent_id"):
            errors.append(f"chunk[{index}] identity parent_id differs from parent.parent_id")
        if identity.get("content_sha256") != chunk.get("content_sha256"):
            errors.append(f"chunk[{index}] identity content hash differs from chunk content hash")
        if identity.get("chunk_kind") != chunk_kind:
            errors.append(f"chunk[{index}] identity chunk_kind differs from chunk_kind")
        expected_chunk_id = cid(identity)
        actual_chunk_id = chunk.get("chunk_id")
        if actual_chunk_id != expected_chunk_id:
            errors.append(f"chunk[{index}] chunk_id does not match canonical identity")
        identity_bytes = compact_canon(identity)
        if isinstance(actual_chunk_id, str):
            if actual_chunk_id in seen_ids:
                if seen_ids[actual_chunk_id] == identity_bytes:
                    errors.append(f"duplicate chunk_id: {actual_chunk_id}")
                else:
                    errors.append(f"chunk identity collision: {actual_chunk_id}")
            seen_ids[actual_chunk_id] = identity_bytes
        for source_id in chunk.get("source_ids", []):
            if source_id not in source_ids:
                errors.append(f"chunk {actual_chunk_id!r} references unknown source {source_id!r}")
        if chunk_kind != "static_file_span":
            continue
        path = parent.get("path")
        if not isinstance(path, str) or not _path_is_safe(path):
            errors.append(f"chunk {actual_chunk_id!r} has unsafe or non-portable path")
            continue
        observed_paths.add(path)
        if path not in tree_by_path:
            errors.append(f"chunk {actual_chunk_id!r} path is absent from pinned Git tree: {path}")
            continue
        blob_oid, data = tree_by_path[path]
        parent_hash = sha256(data)
        source_id = policy["static_inputs"]["source_id"]
        expected_parent_material = make_parent_material(source_id, str(commit), path, blob_oid, data)
        expected_parent_id = parent_id(expected_parent_material)
        if parent.get("parent_id") != expected_parent_id:
            errors.append(f"chunk {actual_chunk_id!r} parent_id mismatch")
        expected_parent = {
            "byte_count": len(data),
            "commit": commit,
            "git_blob_oid": blob_oid,
            "parent_id": expected_parent_id,
            "path": path,
            "repository": REPOSITORY_ID,
            "sha256": parent_hash,
        }
        if parent != expected_parent:
            errors.append(f"chunk {actual_chunk_id!r} parent metadata mismatch")
        start = exact_locator.get("byte_start")
        end = exact_locator.get("byte_end_exclusive")
        if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end < start or end > len(data):
            errors.append(f"chunk {actual_chunk_id!r} has invalid byte bounds")
            continue
        span = data[start:end]
        if sha256(span) != chunk.get("content_sha256"):
            errors.append(f"chunk {actual_chunk_id!r} content_sha256 mismatch")
        if exact_locator.get("line_start") != line_for(data, start):
            errors.append(f"chunk {actual_chunk_id!r} line_start mismatch")
        if exact_locator.get("line_end") != line_for(data, max(start, end - 1)):
            errors.append(f"chunk {actual_chunk_id!r} line_end mismatch")
        expected_identity = make_identity(
            source_id=source_id,
            commit=str(commit),
            parent=expected_parent_id,
            locator=exact_locator,
            content_sha256=sha256(span),
        )
        if identity != expected_identity:
            errors.append(f"chunk {actual_chunk_id!r} identity fields are not canonical")
        groups[expected_parent_id].append(chunk)
        global_order.append(((path.encode("utf-8"),), start, str(actual_chunk_id)))

    if observed_paths != expected_paths:
        missing = sorted(expected_paths - observed_paths)
        extra = sorted(observed_paths - expected_paths)
        errors.append(f"static chunk path coverage mismatch: missing={missing[:3]!r} extra={extra[:3]!r}")
    if global_order != sorted(global_order):
        errors.append("chunks are not in canonical path/byte order")

    lines_per_chunk = policy.get("static_inputs", {}).get("lines_per_chunk", 200)
    for group_id, group in groups.items():
        first_parent = group[0].get("parent", {})
        path = first_parent.get("path")
        if path not in tree_by_path:
            continue
        _, data = tree_by_path[path]
        ordered = sorted(group, key=lambda item: item["exact_locator"]["byte_start"])
        actual_spans = [
            (item["exact_locator"]["byte_start"], item["exact_locator"]["byte_end_exclusive"])
            for item in ordered
        ]
        expected_spans = partition_static_file(data, int(lines_per_chunk))
        if actual_spans != expected_spans:
            errors.append(f"parent {group_id} byte partition mismatch")
        if len(data) > 0 and any(start == end for start, end in actual_spans):
            errors.append(f"parent {group_id} has a zero-length chunk for a non-empty file")
        if len(data) == 0 and actual_spans != [(0, 0)]:
            errors.append(f"empty parent {group_id} must have exactly one zero-length chunk")

    edges = payload.get("edges")
    if not isinstance(edges, list):
        return errors
    edge_by_id: dict[str, dict] = {}
    actual_edge_keys: list[tuple[str, str, str]] = []
    chunk_ids = set(seen_ids)
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"edge[{index}] must be an object")
            continue
        edge_type = edge.get("edge_type")
        source = edge.get("source_chunk_id")
        target = edge.get("target_chunk_id")
        actual_id = edge.get("edge_id")
        if edge_type not in INVERSE_EDGE_TYPES:
            errors.append(f"edge[{index}] has unknown type {edge_type!r}")
            continue
        if source not in chunk_ids or target not in chunk_ids:
            errors.append(f"edge {actual_id!r} references an unknown chunk")
        if source == target:
            errors.append(f"edge {actual_id!r} may not be self-referential")
        expected_id = edge_id(str(edge_type), str(source), str(target))
        if actual_id != expected_id:
            errors.append(f"edge[{index}] edge_id does not match canonical identity")
        if actual_id in edge_by_id:
            errors.append(f"duplicate edge_id: {actual_id}")
        if isinstance(actual_id, str):
            edge_by_id[actual_id] = edge
        actual_edge_keys.append((str(source), str(edge_type), str(target)))
    if actual_edge_keys != sorted(actual_edge_keys):
        errors.append("edges are not in canonical source/type/target order")

    expected_edge_keys: set[tuple[str, str, str]] = set()
    for group in groups.values():
        ordered = sorted(group, key=lambda item: item["exact_locator"]["byte_start"])
        for left, right in zip(ordered, ordered[1:]):
            expected_edge_keys.add((left["chunk_id"], "NEXT_IN_PARENT", right["chunk_id"]))
            expected_edge_keys.add((right["chunk_id"], "PREVIOUS_IN_PARENT", left["chunk_id"]))
    if set(actual_edge_keys) != expected_edge_keys:
        missing = sorted(expected_edge_keys - set(actual_edge_keys))
        extra = sorted(set(actual_edge_keys) - expected_edge_keys)
        errors.append(f"static adjacency edge set mismatch: missing={missing[:2]!r} extra={extra[:2]!r}")
    for actual_id, edge in edge_by_id.items():
        inverse = edge_by_id.get(edge.get("inverse_edge_id"))
        expected_inverse_type = INVERSE_EDGE_TYPES.get(edge.get("edge_type"))
        if (
            inverse is None
            or inverse.get("edge_type") != expected_inverse_type
            or inverse.get("source_chunk_id") != edge.get("target_chunk_id")
            or inverse.get("target_chunk_id") != edge.get("source_chunk_id")
            or inverse.get("inverse_edge_id") != actual_id
        ):
            errors.append(f"edge {actual_id!r} lacks a valid declared inverse")

    top_sources = payload.get("source_ids")
    observed_sources = sorted({source for chunk in chunks if isinstance(chunk, dict) for source in chunk.get("source_ids", [])})
    if top_sources != observed_sources:
        errors.append("top-level source_ids must equal the sorted source closure of chunks")
    return errors


def validate_migration_payload(payload: dict, registry: dict) -> list[str]:
    errors = schema_errors(MIGRATION_SCHEMA, payload)
    mappings = payload.get("mappings")
    if not isinstance(mappings, list):
        return errors
    old_ids: set[str] = set()
    new_ids: set[str] = set()
    for index, mapping in enumerate(mappings):
        if not isinstance(mapping, dict):
            errors.append(f"migration mapping[{index}] must be an object")
            continue
        old_id = mapping.get("old_chunk_id")
        new_id = mapping.get("new_chunk_id")
        if old_id in old_ids:
            errors.append(f"duplicate legacy chunk ID in migration: {old_id}")
        if new_id in new_ids:
            errors.append(f"duplicate target chunk ID in migration: {new_id}")
        old_ids.add(old_id)
        new_ids.add(new_id)
    registry_ids = {chunk.get("chunk_id") for chunk in registry.get("chunks", []) if isinstance(chunk, dict)}
    if new_ids != registry_ids:
        errors.append("migration target IDs do not equal the v2 registry chunk IDs")
    if payload.get("target_registry_sha256") != sha256(canon(registry)):
        errors.append("migration target_registry_sha256 is stale")
    return errors


def build_outputs() -> tuple[dict, dict]:
    policy = load_json_object(POLICY, "chunk policy")
    policy_errors = validate_policy(policy)
    if policy_errors:
        raise SystemExit("ERROR: malformed chunk policy:\n" + "\n".join(policy_errors))
    lock = load_json_object(ROOT / "UPSTREAM.lock.json", "UPSTREAM.lock.json")
    commit = lock.get("commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise SystemExit("ERROR: malformed UPSTREAM.lock.json: commit must be a lowercase 40-hex string")
    source_id = policy["static_inputs"]["source_id"]
    if source_id not in known_source_ids():
        raise SystemExit(f"ERROR: chunk policy references unknown source ID {source_id}")
    lines_per_chunk = int(policy["static_inputs"]["lines_per_chunk"])

    chunks: list[dict] = []
    migrations: list[dict] = []
    file_chunk_ids: list[list[str]] = []
    try:
        tree = git_tree_snapshot(str(UPSTREAM.resolve()), commit)
    except (OSError, RuntimeError, UnicodeError) as exc:
        raise SystemExit(f"ERROR: cannot read pinned Git tree: {exc}") from exc
    for path, blob_oid, data in tree:
        parent_hash = sha256(data)
        parent_material = make_parent_material(source_id, commit, path, blob_oid, data)
        stable_parent_id = parent_id(parent_material)
        parent_record = {
            "byte_count": len(data),
            "commit": commit,
            "git_blob_oid": blob_oid,
            "parent_id": stable_parent_id,
            "path": path,
            "repository": REPOSITORY_ID,
            "sha256": parent_hash,
        }
        ids_for_file: list[str] = []
        for start, end in partition_static_file(data, lines_per_chunk):
            span = data[start:end]
            content_hash = sha256(span)
            locator = {
                "byte_end_exclusive": end,
                "byte_start": start,
                "kind": "git_blob_span",
                "line_end": line_for(data, max(start, end - 1)),
                "line_start": line_for(data, start),
            }
            identity = make_identity(
                source_id=source_id,
                commit=commit,
                parent=stable_parent_id,
                locator=locator,
                content_sha256=content_hash,
            )
            chunk_id = cid(identity)
            chunk = {
                "authority_class": "candidate_evidence",
                "chunk_id": chunk_id,
                "chunk_kind": "static_file_span",
                "content_sha256": content_hash,
                "exact_locator": locator,
                "identity": identity,
                "limitation": "A byte-exact pinned Git-blob span is candidate evidence, not runtime behavior, intent, or source truth.",
                "parent": parent_record,
                "review_status": "candidate",
                "source_ids": [source_id],
            }
            chunks.append(chunk)
            ids_for_file.append(chunk_id)
            legacy_parent = f"{commit}:{path}:{parent_hash}"
            legacy_locator = f"{commit}:{path}:{start}:{end}"
            migrations.append(
                {
                    "chunk_kind": "static_file_span",
                    "content_sha256": content_hash,
                    "locator": locator,
                    "new_chunk_id": chunk_id,
                    "old_chunk_id": legacy_cid(legacy_parent, legacy_locator, content_hash),
                    "parent_id": stable_parent_id,
                }
            )
        file_chunk_ids.append(ids_for_file)

    edges: list[dict] = []
    for ids_for_file in file_chunk_ids:
        for left, right in zip(ids_for_file, ids_for_file[1:]):
            edges.append(make_edge("NEXT_IN_PARENT", left, right))
            edges.append(make_edge("PREVIOUS_IN_PARENT", right, left))
    edges.sort(key=lambda edge: (edge["source_chunk_id"], edge["edge_type"], edge["target_chunk_id"]))
    registry = {
        "build": {
            "activated_chunk_kinds": policy["activated_chunk_kinds"],
            "canonical_json": "sorted_keys_pretty_utf8_lf",
            "generator": "scripts/build_chunk_registry.py",
            "generator_version": GENERATOR_VERSION,
        },
        "chunks": chunks,
        "edges": edges,
        "format_version": FORMAT_VERSION,
        "limitation": "Generated candidate evidence only; no private raw bytes, semantic inference, or claim promotion.",
        "pinned_commit": commit,
        "pinned_repository": REPOSITORY_ID,
        "policy_sha256": sha256(POLICY.read_bytes()),
        "schema": "claude-legal-audit.chunk-registry.v2",
        "source_ids": [source_id],
    }
    migration = {
        "from_registry_schema": "claude-legal-audit.chunk-registry.v1",
        "limitation": "This deterministic compatibility map preserves references from the unpublished v1 candidate IDs; it does not promote either registry or assert semantic equivalence beyond the same pinned byte spans.",
        "mappings": migrations,
        "schema": "claude-legal-audit.chunk-id-migration.v1",
        "source_policy_revision": LEGACY_FORMAT_VERSION,
        "source_policy_sha256": policy["legacy_registry"]["policy_sha256"],
        "source_registry_sha256": policy["legacy_registry"]["sha256"],
        "status": "candidate_compatibility_map",
        "target_policy_revision": FORMAT_VERSION,
        "target_registry_sha256": sha256(canon(registry)),
        "to_registry_schema": "claude-legal-audit.chunk-registry.v2",
    }
    registry_errors = validate_registry_payload(
        registry,
        allowed_kinds=activated_kinds(policy),
        policy=policy,
    )
    migration_errors = validate_migration_payload(migration, registry)
    all_errors = registry_errors + migration_errors
    if all_errors:
        raise SystemExit("ERROR: chunk outputs failed validation:\n" + "\n".join(all_errors))
    return registry, migration


def build_registry() -> dict:
    """Backward-compatible programmatic entry point used by tests."""
    return build_outputs()[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--verify-reconstruction", action="store_true")
    parser.add_argument("--validate-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--migration-output", type=Path)
    args = parser.parse_args()
    if args.check and (args.output is not None or args.migration_output is not None):
        raise SystemExit("ERROR: --check compares authoritative outputs; do not pass output paths")
    if args.validate_file is not None:
        if args.check or args.output is not None or args.migration_output is not None:
            raise SystemExit("ERROR: --validate-file cannot be combined with check or output options")
        payload = load_json_object(args.validate_file, "chunk registry candidate")
        errors = validate_registry_payload(payload)
        if errors:
            raise SystemExit("ERROR: chunk registry candidate is invalid:\n" + "\n".join(errors))
        print(f"chunk registry candidate valid: {len(payload.get('chunks', []))} chunks")
        return

    registry, migration = build_outputs()
    registry_bytes = canon(registry)
    migration_bytes = canon(migration)
    if args.check:
        failures: list[str] = []
        if not OUT.exists() or OUT.read_bytes() != registry_bytes:
            failures.append("chunk registry is stale")
        if not MIGRATION_OUT.exists() or MIGRATION_OUT.read_bytes() != migration_bytes:
            failures.append("chunk ID migration is stale")
        if failures:
            raise SystemExit("ERROR: " + "; ".join(failures) + "; run scripts/build_chunk_registry.py")
        suffix = " with byte-exact reconstruction verified" if args.verify_reconstruction else ""
        print(
            f"chunk registry current: {len(registry['chunks'])} chunks, "
            f"{len(registry['edges'])} typed edges{suffix}"
        )
        return

    out_path = args.output if args.output is not None else OUT
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(registry_bytes)
    migration_path = args.migration_output
    if migration_path is None and args.output is None:
        migration_path = MIGRATION_OUT
    if migration_path is not None:
        migration_path.parent.mkdir(parents=True, exist_ok=True)
        migration_path.write_bytes(migration_bytes)
    try:
        display = out_path.resolve().relative_to(ROOT)
    except ValueError:
        display = out_path
    print(f"wrote {display}: {len(registry['chunks'])} chunks, {len(registry['edges'])} edges")


if __name__ == "__main__":
    main()
