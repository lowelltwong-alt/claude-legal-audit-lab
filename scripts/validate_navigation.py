#!/usr/bin/env python3
"""Fail-closed validator for AI navigation, authority, and public genealogy."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_EPISTEMIC_STATUSES = {"observed", "counterevidence", "hypothesis", "normative", "unknown"}
EXEMPT_CLASSES = {"method", "interrogatory", "source_registry"}
TRUSTED_AUTHORITIES = {"reviewed_analysis"}
INCOMPLETE_SOURCE_STATUSES = {"missing_url_and_capture"}
PUBLIC_TOP_LEVEL = {
    "AGENTS.md", "AI_FRONT_DOOR.md", "AI_TABLE_OF_CONTENTS.md", "CLAUDE.md",
    "CONTRIBUTING.md", "LICENSE", "MACHINE_NAVIGATION_MANIFEST.json", "README.md",
    "SECURITY.md", "UPSTREAM.lock.json",
    "audit", "docs", "patterns", "prompts", "registry", "research", "results",
    "public", "runtime-lab", "schemas", "scripts", "templates", "tests", "upstream"
}


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def is_public_navigation_path(path: str) -> bool:
    return path.replace("\\", "/").split("/", 1)[0] in PUBLIC_TOP_LEVEL


def normalize_query(query: str) -> str:
    value = unicodedata.normalize("NFKC", query).casefold().replace("-", " ")
    return " ".join(value.split())


def resolve_route(query: str, registry: dict) -> str:
    normalized = normalize_query(query)
    matches = []
    for route in registry["routes"]:
        if any(normalize_query(trigger) in normalized for trigger in route["triggers"]):
            matches.append(route)
    if not matches:
        return registry["fallback_route_id"]
    highest = max(route["priority"] for route in matches)
    winners = [route["route_id"] for route in matches if route["priority"] == highest]
    if len(winners) != 1:
        raise ValueError(f"ambiguous highest-priority route tie: {sorted(winners)}")
    return winners[0]


def source_is_reproducible(source: dict) -> bool:
    binding = source["revision_binding"]
    return binding.get("kind") == "git_commit" or bool(binding.get("content_sha256"))


def evidence_is_exact(evidence: dict) -> bool:
    if evidence.get("locator_kind") == "path_lines":
        return bool(re.fullmatch(r".+ lines [0-9]+-[0-9]+", evidence.get("locator", "")))
    return evidence.get("locator_kind") in {"page_span", "captured_selector"}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    manifest = load("MACHINE_NAVIGATION_MANIFEST.json")
    routes = load("registry/ai-front-door-registry.json")
    sources_payload = load("registry/source-registry.json")
    claims_payload = load("registry/claim-registry.json")
    policy = load("registry/lineage-policy.json")
    derivations_payload = load("registry/derivation-registry.json")

    if manifest.get("single_entrypoint") != "AI_FRONT_DOOR.md":
        errors.append("AI_FRONT_DOOR.md is not the single entrypoint")
    required_paths = set(manifest["required_read_order"])
    required_paths.update(manifest["authority_registries"])
    required_paths.update(manifest["genealogy_entrypoints"].values())
    for path in sorted(required_paths):
        if not (ROOT / path).exists():
            errors.append(f"navigation target missing: {path}")
        if not is_public_navigation_path(path):
            errors.append(f"unpublished path exposed by public navigation: {path}")

    toc = (ROOT / "AI_TABLE_OF_CONTENTS.md").read_text(encoding="utf-8")
    if "| Path | What it is | Tags | Use when | Authority |" not in toc:
        errors.append("AI table of contents lacks the five-column routing contract")
    for path in manifest["required_read_order"]:
        if path not in toc and path != "AI_TABLE_OF_CONTENTS.md":
            errors.append(f"AI table of contents omits required path {path}")

    for route in routes["routes"]:
        if not isinstance(route.get("priority"), int):
            errors.append(f"route lacks integer priority: {route['route_id']}")
        for path in route["read"]:
            if not is_public_navigation_path(path):
                errors.append(f"route {route['route_id']} exposes unpublished path {path}")
            candidate = ROOT / path.rstrip("/")
            if not candidate.exists() and path not in {"upstream/claude-for-legal/", "results/"}:
                errors.append(f"route {route['route_id']} targets missing path {path}")
    route_ids = {route["route_id"] for route in routes["routes"]}
    if routes.get("fallback_route_id") not in route_ids:
        errors.append("fallback route is absent")
    for fixture in routes.get("routing_fixtures", []):
        try:
            actual = resolve_route(fixture["query"], routes)
        except ValueError as exc:
            errors.append(f"routing fixture failed closed unexpectedly: {fixture['query']}: {exc}")
            continue
        if actual != fixture["expected_route_id"]:
            errors.append(f"routing fixture mismatch: {fixture['query']}: {actual} != {fixture['expected_route_id']}")

    source_rows = sources_payload["sources"]
    source_ids = [row["source_id"] for row in source_rows]
    source_map = {row["source_id"]: row for row in source_rows}
    if len(source_ids) != len(set(source_ids)):
        errors.append("duplicate source IDs")
    for row in source_rows:
        if not row.get("locator") or not row.get("revision_binding"):
            errors.append(f"source lacks locator/revision binding: {row['source_id']}")
        if row.get("url") is None and row.get("status") not in INCOMPLETE_SOURCE_STATUSES:
            errors.append(f"source URL absent without incomplete status: {row['source_id']}")

    claim_rows = claims_payload["claims"]
    claim_ids = [row["claim_id"] for row in claim_rows]
    if len(claim_ids) != len(set(claim_ids)):
        errors.append("duplicate claim IDs")
    for claim in claim_rows:
        if claim.get("epistemic_status") not in ALLOWED_EPISTEMIC_STATUSES:
            errors.append(f"invalid claim epistemic status: {claim['claim_id']}")
        if claim.get("lifecycle") not in {"active", "superseded", "retired"}:
            errors.append(f"invalid claim lifecycle: {claim['claim_id']}")
        if not claim.get("does_not_prove"):
            errors.append(f"claim lacks does_not_prove boundary: {claim['claim_id']}")
        if not claim.get("evidence"):
            errors.append(f"claim lacks evidence: {claim['claim_id']}")
        claim_reproducible = True
        for evidence in claim["evidence"]:
            if evidence["source_id"] not in source_map:
                errors.append(f"claim {claim['claim_id']} references unknown source {evidence['source_id']}")
            if not evidence.get("locator"):
                errors.append(f"claim {claim['claim_id']} has evidence without locator")
            if evidence.get("evidence_grade") not in {"reproducible", "locator_only"}:
                errors.append(f"claim {claim['claim_id']} has invalid evidence grade")
            reproducible = evidence.get("evidence_grade") == "reproducible" and evidence_is_exact(evidence) and source_is_reproducible(source_map[evidence["source_id"]])
            claim_reproducible = claim_reproducible and reproducible
        if claim.get("review_state") == "reviewed" and not claim_reproducible:
            errors.append(f"reviewed claim lacks exact reproducible evidence: {claim['claim_id']}")
        if claim.get("publication_eligibility") == "eligible" and claim.get("review_state") != "reviewed":
            errors.append(f"export-eligible claim is not reviewed: {claim['claim_id']}")
        if claim.get("review_state") != "reviewed":
            warnings.append(f"{claim['claim_id']} remains candidate: public evidence is not yet fully reproducible")

    policy_rows = policy["records"]
    policy_paths = [row["path"] for row in policy_rows]
    if len(policy_paths) != len(set(policy_paths)):
        errors.append("duplicate lineage-policy paths")
    required_artifacts: set[str] = set()
    public_files = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
    ]
    for pattern in policy["required_globs"]:
        required_artifacts.update(
            rel for rel in public_files if fnmatch.fnmatch(rel, pattern)
        )
    missing_policy = sorted(required_artifacts - set(policy_paths))
    if missing_policy:
        errors.append("artifacts lack lineage policy: " + ", ".join(missing_policy))

    derivation_rows = derivations_payload["records"]
    derivations = {row["path"]: row for row in derivation_rows}
    if set(derivations) != set(policy_paths):
        errors.append("derivation registry paths differ from lineage policy")
    for path, row in derivations.items():
        if not (ROOT / path).is_file():
            errors.append(f"derived artifact missing: {path}")
            continue
        if digest(path) != row["sha256"]:
            errors.append(f"stale artifact hash: {path}")
        if row["artifact_class"] not in EXEMPT_CLASSES and row["authority_class"] != "candidate_legacy" and not row["primary_source_closure"]:
            errors.append(f"factual artifact lacks primary-source closure: {path}")
        incomplete = [source_id for source_id in row["source_closure"] if source_map[source_id]["status"] in INCOMPLETE_SOURCE_STATUSES]
        if row["authority_class"] in TRUSTED_AUTHORITIES and incomplete:
            errors.append(f"reviewed artifact depends on incomplete sources: {path}: {incomplete}")
        if row["authority_class"] in TRUSTED_AUTHORITIES and not row.get("evidence_reproducible"):
            errors.append(f"reviewed artifact has a non-reproducible claim lineage: {path}")
        for claim_lineage in row.get("claim_lineage", []):
            if not claim_lineage["source_ids"]:
                errors.append(f"artifact claim has empty source lineage: {path}: {claim_lineage['claim_id']}")
        if incomplete:
            warnings.append(f"{path} remains candidate because of incomplete sources {incomplete}")

    expected_inputs = derivations_payload["generated_from"]
    actual_inputs = {
        "builder_sha256": digest("scripts/build_lineage.py"),
        "lineage_policy_sha256": digest("registry/lineage-policy.json"),
        "source_registry_sha256": digest("registry/source-registry.json"),
        "claim_registry_sha256": digest("registry/claim-registry.json")
    }
    if expected_inputs != actual_inputs:
        errors.append("derivation registry input hashes are stale")

    check = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_lineage.py"), "--check"], capture_output=True, text=True)
    if check.returncode:
        errors.append(check.stderr.strip() or check.stdout.strip() or "lineage rebuild check failed")

    argument_check = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_argument_mesh.py")],
        capture_output=True,
        text=True,
    )
    if argument_check.returncode:
        errors.append(
            argument_check.stderr.strip()
            or argument_check.stdout.strip()
            or "argument mesh validation failed"
        )

    for validator in ("validate_roadmap.py", "validate_release_readiness.py"):
        control_check = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / validator)],
            capture_output=True,
            text=True,
        )
        if control_check.returncode:
            errors.append(
                control_check.stderr.strip()
                or control_check.stdout.strip()
                or f"{validator} failed"
            )

    for warning in sorted(set(warnings)):
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"navigation and lineage valid: {len(source_rows)} sources, {len(claim_rows)} claims, {len(derivation_rows)} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
