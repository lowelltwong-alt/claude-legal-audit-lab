#!/usr/bin/env python3
"""One-way claim-registry v1 repair plus strict v2 validation."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "claim-registry.json"
SCHEMA = ROOT / "schemas" / "claim-registry.schema.json"
SOURCES = ROOT / "registry" / "source-registry.json"

STATUS_MAP = {"Confirmed": "observed", "Inferred": "hypothesis", "Hypothesis": "hypothesis", "Unknown": "unknown"}
REPAIRS = {
    "CLM-0001": {
        "proposition": "The pinned repository and captured official product pages document a static design that invites legal users to encode playbooks, fallbacks, deviations, rationales, risk posture, and house style.",
        "repair_note": "Narrowed to observed static design; deployed runtime behavior is split into CLM-0017.",
    },
    "CLM-0003": {
        "epistemic_status": "counterevidence",
        "repair_note": "Classified as contractual control and counterevidence to default-training allegations.",
    },
    "CLM-0004": {
        "proposition": "Registered official documentation describes feature-dependent retention and zero-data-retention policy boundaries for hosted services.",
        "repair_note": "Narrowed to documented feature policy; tenant-specific behavior is split into CLM-0018.",
    },
    "CLM-0005": {
        "publication_eligibility": "quarantined",
        "repair_note": "Quarantined until the cited dynamic feedback source is recaptured and hash-bound.",
    },
    "CLM-0008": {
        "epistemic_status": "hypothesis",
        "repair_note": "Kept explicitly as a switching-cost hypothesis rather than an observed outcome.",
    },
    "CLM-0009": {
        "lifecycle": "retired",
        "publication_eligibility": "retired",
        "repair_note": "Retired because the cited inconsistency has not been reproduced from a registered source-to-locator path.",
    },
    "CLM-0010": {
        "proposition": "No evidence currently registered in this project establishes covert pooling of identifiable law-firm ontologies or default training on ordinary commercial content.",
        "epistemic_status": "unknown",
        "repair_note": "Rewritten as a bounded statement about this registry, not a claim about the complete public record.",
    },
    "CLM-0015": {
        "epistemic_status": "hypothesis",
        "repair_note": "Retained only as a conditional, falsifiable sector-externality hypothesis.",
    },
}


def canonical(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def new_split_claims() -> list[dict]:
    return [
        {
            "claim_id": "CLM-0017",
            "lifecycle": "active",
            "epistemic_status": "unknown",
            "review_state": "candidate",
            "publication_eligibility": "blocked_review",
            "proposition": "Whether the static repository design maps to a deployed legal-product runtime, and how that runtime moves or retains tenant data, remains unknown in the registered evidence.",
            "evidence": [{"source_id": "SRC-0002", "locator": "Pinned repository static design boundary", "locator_kind": "repository_scope", "evidence_grade": "locator_only", "support_type": "scope_boundary"}],
            "does_not_prove": "That deployed behavior is unsafe, safe, equivalent to the repository, or different from the repository.",
            "confidence": "high",
            "hypotheses": {"H0": "supports", "H1": "supports", "H2": "neutral"},
            "repair_note": "Created as the unknown-runtime half of the CLM-0001 split.",
        },
        {
            "claim_id": "CLM-0018",
            "lifecycle": "active",
            "epistemic_status": "unknown",
            "review_state": "candidate",
            "publication_eligibility": "blocked_review",
            "proposition": "A particular tenant's negotiated terms, enabled features, retention settings, connector behavior, and operational compliance remain unknown in the registered evidence.",
            "evidence": [
                {"source_id": "SRC-0009", "locator": "Feature-dependent retention and ZDR policy boundary", "locator_kind": "section_description", "evidence_grade": "locator_only", "support_type": "scope_boundary"},
                {"source_id": "SRC-0006", "locator": "Customer-specific processing instructions and agreement boundary", "locator_kind": "section_description", "evidence_grade": "locator_only", "support_type": "scope_boundary"},
            ],
            "does_not_prove": "Any tenant's actual configuration, data movement, retention, training use, breach, or compliance failure.",
            "confidence": "high",
            "hypotheses": {"H0": "supports", "H1": "supports", "H2": "neutral"},
            "repair_note": "Created as the unknown-tenant-behavior half of the CLM-0004 split.",
        },
    ]


def upgrade(payload: dict) -> dict:
    if payload.get("schema") == "claude-legal-audit.claim-registry.v2":
        return payload
    if payload.get("schema") != "claude-legal-audit.claim-registry.v1":
        raise SystemExit("ERROR: unsupported claim-registry schema")
    claims = []
    for old in payload.get("claims", []):
        claim_id = old["claim_id"]
        claim = {
            "claim_id": claim_id,
            "lifecycle": "active",
            "epistemic_status": STATUS_MAP[old["status"]],
            "review_state": old["review_status"],
            "publication_eligibility": "eligible" if old["review_status"] == "reviewed" else "blocked_review",
            "proposition": old["claim"],
            "evidence": old["evidence"],
            "does_not_prove": old["does_not_prove"],
            "confidence": old["confidence"],
            "hypotheses": old["hypotheses"],
            "repair_note": "Migrated without substantive expansion; remains bounded by its evidence and does-not-prove field.",
        }
        claim.update(REPAIRS.get(claim_id, {}))
        claims.append(claim)
    claims.extend(new_split_claims())
    claims.sort(key=lambda item: item["claim_id"])
    return {
        "schema": "claude-legal-audit.claim-registry.v2",
        "revision": "2.0.0",
        "reviewed_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "claims": claims,
    }


def validate(payload: dict) -> list[str]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = [error.message for error in validator.iter_errors(payload)]
    claims = payload.get("claims", [])
    ids = [claim.get("claim_id") for claim in claims if isinstance(claim, dict)]
    if len(ids) != len(set(ids)):
        errors.append("claim IDs must be unique")
    source_ids = {source["source_id"] for source in json.loads(SOURCES.read_text(encoding="utf-8"))["sources"]}
    for claim in claims:
        if claim.get("publication_eligibility") == "eligible" and claim.get("review_state") != "reviewed":
            errors.append(f"{claim.get('claim_id')} is export-eligible without reviewed evidence")
        if claim.get("lifecycle") == "retired" and claim.get("publication_eligibility") != "retired":
            errors.append(f"{claim.get('claim_id')} is retired but not publication-retired")
        for evidence in claim.get("evidence", []):
            if evidence.get("source_id") not in source_ids:
                errors.append(f"{claim.get('claim_id')} references unknown source {evidence.get('source_id')}")
    required_repairs = {
        "CLM-0003": ("epistemic_status", "counterevidence"),
        "CLM-0005": ("publication_eligibility", "quarantined"),
        "CLM-0009": ("lifecycle", "retired"),
        "CLM-0015": ("epistemic_status", "hypothesis"),
    }
    by_id = {claim.get("claim_id"): claim for claim in claims}
    for claim_id, (field, expected) in required_repairs.items():
        if by_id.get(claim_id, {}).get(field) != expected:
            errors.append(f"{claim_id} required repair {field}={expected!r} is absent")
    for required in ("CLM-0017", "CLM-0018"):
        if required not in by_id:
            errors.append(f"missing split claim {required}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    current = json.loads(REGISTRY.read_text(encoding="utf-8"))
    upgraded = upgrade(current)
    errors = validate(upgraded)
    if errors:
        print("ERROR: claim registry invalid:\n" + "\n".join(errors), file=sys.stderr)
        return 1
    data = canonical(upgraded)
    if args.check:
        if current.get("schema") != "claude-legal-audit.claim-registry.v2" or REGISTRY.read_bytes() != data:
            print("ERROR: claim registry is stale or still v1", file=sys.stderr)
            return 1
        print(f"claim registry current: {len(upgraded['claims'])} claims")
        return 0
    REGISTRY.write_bytes(data)
    print(f"wrote {REGISTRY.relative_to(ROOT)}: {len(upgraded['claims'])} claims")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
