#!/usr/bin/env python3
"""Validate the release gate without granting release authority."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry" / "release-readiness.json"
SCHEMA_PATH = ROOT / "schemas" / "release-readiness.schema.json"
PRIVATE_PREFIXES = (".private/", "private/")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_paths(*args: str) -> list[str]:
    raw = subprocess.check_output(["git", *args, "-z"], cwd=ROOT)
    return sorted(
        part.decode("utf-8", errors="surrogateescape").replace("\\", "/")
        for part in raw.split(b"\0")
        if part
    )


def compute_inventory() -> dict:
    tracked = git_paths("ls-files", "--cached")
    untracked = git_paths("ls-files", "--others", "--exclude-standard")
    public_paths = sorted(set(tracked + untracked))
    digest = hashlib.sha256(("\n".join(public_paths) + "\n").encode("utf-8")).hexdigest()
    return {
        "tracked_file_count": len(tracked),
        "untracked_public_candidate_count": len(untracked),
        "public_path_sha256": digest,
        "tracked_paths": tracked,
        "untracked_paths": untracked,
    }


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def tracked_tree_is_clean() -> bool:
    return not subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True
    ).strip()


def file_sha256(relative: str) -> str | None:
    path = ROOT / relative
    if not path.is_file() or not path.resolve().is_relative_to(ROOT.resolve()):
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def allowlist_paths(relative: str) -> set[str] | None:
    path = ROOT / relative
    if not path.is_file() or not path.resolve().is_relative_to(ROOT.resolve()):
        return None
    return {
        line.strip().replace("\\", "/")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def valid_datetime(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate(payload: dict, inventory: dict) -> list[str]:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = [
        f"schema violation at {'.'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload),
            key=lambda error: list(error.absolute_path),
        )
    ]
    if not valid_datetime(payload.get("as_of")):
        errors.append("as_of must be an ISO-8601 timestamp with timezone")
    approval = payload.get("human_approval")
    if isinstance(approval, dict) and not valid_datetime(approval.get("approved_at")):
        errors.append("human approval approved_at must be an ISO-8601 timestamp with timezone")
    expected = payload.get("inventory_snapshot", {})
    for key in ("tracked_file_count", "untracked_public_candidate_count", "public_path_sha256"):
        if expected.get(key) != inventory.get(key):
            errors.append(f"release inventory snapshot is stale: {key}")

    patterns = tuple(payload.get("private_path_patterns", []))
    if patterns != PRIVATE_PREFIXES:
        errors.append("private path patterns must be the hardcoded .private/ and private/ prefixes")
    for path in inventory.get("tracked_paths", []):
        if path.startswith(PRIVATE_PREFIXES):
            errors.append(f"tracked private path: {path}")

    decisions = payload.get("decisions", [])
    receipts = payload.get("receipts", [])
    decision_ids = [row.get("decision_id") for row in decisions]
    receipt_ids = [row.get("receipt_id") for row in receipts]
    if len(decision_ids) != len(set(decision_ids)):
        errors.append("duplicate release decision IDs")
    if len(receipt_ids) != len(set(receipt_ids)):
        errors.append("duplicate release receipt IDs")
    known_blockers = set(decision_ids + receipt_ids)
    for blocker in payload.get("release_blockers", []):
        if blocker not in known_blockers:
            errors.append(f"unknown release blocker: {blocker}")
    if payload.get("status") == "blocked" and not payload.get("release_blockers"):
        errors.append("blocked release must name at least one blocker")
    return errors


def readiness_errors(payload: dict, inventory: dict) -> list[str]:
    errors: list[str] = []
    candidate = payload["release_candidate"]
    if payload.get("status") != "ready":
        errors.append("release status is not ready")
    if inventory.get("untracked_public_candidate_count") != 0:
        errors.append("release candidate contains untracked public paths")
    if not candidate.get("frozen") or not candidate.get("commit"):
        errors.append("release candidate is not frozen to a commit")
    elif candidate.get("commit") != git_head():
        errors.append("release candidate commit does not match HEAD")
    if not tracked_tree_is_clean():
        errors.append("tracked working tree is not clean")
    for field in ("allowlist_path", "allowlist_sha256", "export_path", "export_sha256"):
        if not candidate.get(field):
            errors.append(f"release candidate lacks {field}")
    if candidate.get("allowlist_path") and candidate.get("allowlist_sha256"):
        if file_sha256(candidate["allowlist_path"]) != candidate["allowlist_sha256"]:
            errors.append("release allowlist hash does not match its bytes")
        paths = allowlist_paths(candidate["allowlist_path"])
        if paths is None or paths != set(inventory.get("tracked_paths", [])):
            errors.append("release allowlist does not exactly match tracked paths")
    if candidate.get("export_path") and candidate.get("export_sha256"):
        if file_sha256(candidate["export_path"]) != candidate["export_sha256"]:
            errors.append("release export hash does not match its bytes")
    for row in payload["decisions"]:
        if row["status"] != "decided" or not row.get("value") or not row.get("evidence_refs"):
            errors.append(f"release decision incomplete: {row['decision_id']}")
    for row in payload["receipts"]:
        if row["status"] != "passed" or not row.get("evidence_refs"):
            errors.append(f"release receipt incomplete: {row['receipt_id']}")
    if payload.get("release_blockers"):
        errors.append("release blockers remain")
    if payload.get("human_release_approved") is not True:
        errors.append("named human has not approved the exact export hash")
    approval = payload.get("human_approval")
    if not isinstance(approval, dict):
        errors.append("named timestamped human approval receipt is absent")
    elif approval.get("export_sha256") != candidate.get("export_sha256"):
        errors.append("human approval is not bound to the exact export hash")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    payload = load(REGISTRY_PATH)
    inventory = compute_inventory()
    errors = validate(payload, inventory)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    blockers = readiness_errors(payload, inventory)
    if args.require_ready and blockers:
        for blocker in blockers:
            print(f"BLOCKED: {blocker}", file=sys.stderr)
        return 1
    print(
        f"release gate valid: {payload['status'].upper()}; "
        f"{inventory['tracked_file_count']} tracked, "
        f"{inventory['untracked_public_candidate_count']} untracked public candidates, "
        f"{len(blockers)} readiness blockers"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
