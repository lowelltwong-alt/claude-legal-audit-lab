#!/usr/bin/env python3
"""Build a deterministic public artifact-to-primary-source genealogy."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "registry" / "lineage-policy.json"
SOURCE_PATH = ROOT / "registry" / "source-registry.json"
CLAIM_PATH = ROOT / "registry" / "claim-registry.json"
OUTPUT_PATH = ROOT / "registry" / "derivation-registry.json"
INCOMPLETE_SOURCE_STATUSES = {"missing_url_and_capture"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_id(path: str) -> str:
    return "ART-" + hashlib.sha256(path.encode("utf-8")).hexdigest()[:16].upper()


def serialize(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def build() -> tuple[dict, list[str]]:
    policy = load(POLICY_PATH)
    sources = {row["source_id"]: row for row in load(SOURCE_PATH)["sources"]}
    claims = {row["claim_id"]: row for row in load(CLAIM_PATH)["claims"]}
    records = {row["path"]: row for row in policy["records"]}
    errors: list[str] = []

    for path, row in records.items():
        if not (ROOT / path).is_file():
            errors.append(f"declared artifact does not exist: {path}")
        for parent in row["parent_artifacts"]:
            if parent not in records:
                errors.append(f"{path} references undeclared parent {parent}")
        for source_id in row["source_ids"]:
            if source_id not in sources:
                errors.append(f"{path} references unknown source {source_id}")
        for claim_id in row["claim_ids"]:
            if claim_id not in claims:
                errors.append(f"{path} references unknown claim {claim_id}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(path: str, stack: list[str]) -> None:
        if path in visiting:
            errors.append("lineage cycle: " + " -> ".join(stack + [path]))
            return
        if path in visited:
            return
        visiting.add(path)
        for parent in records[path]["parent_artifacts"]:
            if parent in records:
                visit(parent, stack + [path])
        visiting.remove(path)
        visited.add(path)

    for path in sorted(records):
        visit(path, [])

    if errors:
        return {"schema": "claude-legal-audit.derivation-registry.v1", "generated_from": {}, "records": []}, errors

    closure_cache: dict[str, set[str]] = {}

    def source_closure(path: str) -> set[str]:
        if path in closure_cache:
            return closure_cache[path]
        row = records[path]
        closure = set(row["source_ids"])
        for claim_id in row["claim_ids"]:
            claim = claims.get(claim_id)
            if claim:
                closure.update(item["source_id"] for item in claim["evidence"])
        for parent in row["parent_artifacts"]:
            if parent in records:
                closure.update(source_closure(parent))
        closure_cache[path] = closure
        return closure

    output_records = []
    for path in sorted(records):
        row = records[path]
        claim_lineage = []
        for claim_id in sorted(row["claim_ids"]):
            claim = claims[claim_id]
            evidence = claim.get("evidence", [])
            reproducible = bool(evidence) and claim.get("review_state") == "reviewed" and all(item.get("evidence_grade") == "reproducible" for item in evidence)
            claim_lineage.append({
                "claim_id": claim_id,
                "source_ids": sorted({item["source_id"] for item in evidence}),
                "review_status": claim.get("review_state", "candidate"),
                "evidence_reproducible": reproducible
            })
        claim_source_ids = sorted({
            evidence["source_id"]
            for claim_id in row["claim_ids"]
            for evidence in claims.get(claim_id, {}).get("evidence", [])
        })
        closure = sorted(source_closure(path))
        primary = sorted(source_id for source_id in closure if sources.get(source_id, {}).get("authority_tier", 99) <= 2)
        incomplete_sources = sorted(source_id for source_id in closure if sources.get(source_id, {}).get("status") in INCOMPLETE_SOURCE_STATUSES)
        output_records.append({
            "artifact_id": artifact_id(path),
            "path": path,
            "sha256": sha256(ROOT / path) if (ROOT / path).is_file() else None,
            "artifact_class": row["artifact_class"],
            "authority_class": row["authority_class"],
            "parent_artifacts": sorted(row["parent_artifacts"]),
            "direct_source_ids": sorted(row["source_ids"]),
            "claim_ids": sorted(row["claim_ids"]),
            "claim_lineage": claim_lineage,
            "claim_source_ids": claim_source_ids,
            "source_closure": closure,
            "primary_source_closure": primary,
            "lineage_status": row["lineage_status"],
            "lineage_complete": not incomplete_sources,
            "evidence_reproducible": all(item["evidence_reproducible"] for item in claim_lineage) if claim_lineage else True,
            "lineage_warnings": [f"incomplete source metadata: {source_id}" for source_id in incomplete_sources]
        })

    payload = {
        "schema": "claude-legal-audit.derivation-registry.v1",
        "generated_from": {
            "builder_sha256": sha256(Path(__file__).resolve()),
            "lineage_policy_sha256": sha256(POLICY_PATH),
            "source_registry_sha256": sha256(SOURCE_PATH),
            "claim_registry_sha256": sha256(CLAIM_PATH)
        },
        "records": output_records
    }
    return payload, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when the committed projection differs")
    args = parser.parse_args()
    payload, errors = build()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    expected = serialize(payload)
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_bytes() != expected:
            print("ERROR: registry/derivation-registry.json is stale; run scripts/build_lineage.py", file=sys.stderr)
            return 1
        print(f"lineage projection current: {len(payload['records'])} artifacts")
        return 0
    OUTPUT_PATH.write_bytes(expected)
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}: {len(payload['records'])} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
