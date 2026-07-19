#!/usr/bin/env python3
"""Validate the candidate white-paper argument mesh and its reverse links."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MESH_PATH = ROOT / "registry" / "argument-mesh.json"
SOURCES_PATH = ROOT / "registry" / "source-registry.json"
CLAIMS_PATH = ROOT / "registry" / "claim-registry.json"
SCHEMA_PATH = ROOT / "schemas" / "argument-mesh.schema.json"

INVERSES = {
    "HAS_THESIS": "PART_OF_THEORY",
    "PART_OF_THEORY": "HAS_THESIS",
    "SUPPORTED_BY": "SUPPORTS",
    "SUPPORTS": "SUPPORTED_BY",
    "CHALLENGED_BY": "CHALLENGES",
    "CHALLENGES": "CHALLENGED_BY",
    "ANSWERED_BY": "ANSWERS",
    "ANSWERS": "ANSWERED_BY",
    "FALSIFIED_BY": "FALSIFIES",
    "FALSIFIES": "FALSIFIED_BY",
    "WEAKENED_BY": "WEAKENS",
    "WEAKENS": "WEAKENED_BY",
    "HAS_PROOF_GAP": "PROOF_GAP_OF",
    "PROOF_GAP_OF": "HAS_PROOF_GAP",
    "PRESENTED_IN": "PRESENTS",
    "PRESENTS": "PRESENTED_IN",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(mesh: dict, source_ids: set[str], claim_ids: set[str]) -> list[str]:
    errors: list[str] = []
    schema = load(SCHEMA_PATH)
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        return [f"invalid argument-mesh JSON Schema: {exc}"]
    schema_errors = sorted(
        Draft202012Validator(schema).iter_errors(mesh), key=lambda error: list(error.absolute_path)
    )
    for error in schema_errors:
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"schema violation at {location}: {error.message}")
    if mesh.get("schema") != "claude-legal-audit.argument-mesh.v1":
        errors.append("unexpected argument-mesh schema")
    if mesh.get("status") != "candidate":
        errors.append("argument mesh must remain candidate")
    if mesh.get("method_document") != "docs/ARGUMENT_MESH_STANDARD.md":
        errors.append("argument mesh must cite the governing method")

    objects = mesh.get("objects", [])
    object_ids = [row.get("object_id") for row in objects]
    if len(object_ids) != len(set(object_ids)):
        errors.append("duplicate argument object IDs")
    object_map = {row.get("object_id"): row for row in objects}
    for object_id, row in object_map.items():
        if row.get("review_status") != "candidate":
            errors.append(f"{object_id} must remain candidate")
        if not row.get("does_not_prove"):
            errors.append(f"{object_id} lacks a does-not-prove boundary")
        if not row.get("applies_when") or not row.get("does_not_apply_when") or not row.get("danger_if_misapplied"):
            errors.append(f"{object_id} lacks contextual-learning boundaries")
        for source_id in row.get("source_ids", []):
            if source_id not in source_ids:
                errors.append(f"{object_id} references unknown source {source_id}")
        for claim_id in row.get("claim_ids", []):
            if claim_id not in claim_ids:
                errors.append(f"{object_id} references unknown claim {claim_id}")

    edges = mesh.get("edges", [])
    edge_ids = [row.get("edge_id") for row in edges]
    if len(edge_ids) != len(set(edge_ids)):
        errors.append("duplicate argument edge IDs")
    triples = {(row.get("source"), row.get("relation"), row.get("target")) for row in edges}
    for edge in edges:
        edge_id = edge.get("edge_id")
        source = edge.get("source")
        target = edge.get("target")
        relation = edge.get("relation")
        expected_inverse = INVERSES.get(relation)
        if source not in object_map or target not in object_map:
            errors.append(f"{edge_id} has a missing endpoint")
        if expected_inverse is None:
            errors.append(f"{edge_id} has unknown relation {relation}")
            continue
        if edge.get("inverse_relation") != expected_inverse:
            errors.append(f"{edge_id} declares the wrong inverse relation")
        if (target, expected_inverse, source) not in triples:
            errors.append(f"{edge_id} lacks reverse dependency {target} {expected_inverse} {source}")
        if edge.get("review_status") != "candidate":
            errors.append(f"{edge_id} must remain candidate")

    thesis = "THS-0001"
    required_thesis_relations = {"SUPPORTED_BY", "CHALLENGED_BY", "HAS_PROOF_GAP", "PRESENTED_IN"}
    actual = {relation for source, relation, _target in triples if source == thesis}
    missing = required_thesis_relations - actual
    if missing:
        errors.append(f"{thesis} lacks required challenge paths: {sorted(missing)}")
    for row in objects:
        if row.get("object_type") == "falsifier":
            related = {
                relation
                for source, relation, target in triples
                if target == row.get("object_id") and relation in {"FALSIFIED_BY", "WEAKENED_BY"}
            }
            if not related:
                errors.append(f"unconnected disconfirmation condition: {row.get('object_id')}")
    incoming = Counter(edge["target"] for edge in edges)
    for row in objects:
        if row["object_type"] not in {"theory", "paper_section"} and incoming[row["object_id"]] == 0:
            errors.append(f"orphan argument object: {row['object_id']}")

    return errors


def main() -> int:
    mesh = load(MESH_PATH)
    source_ids = {row["source_id"] for row in load(SOURCES_PATH)["sources"]}
    claim_ids = {row["claim_id"] for row in load(CLAIMS_PATH)["claims"]}
    errors = validate(mesh, source_ids, claim_ids)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"argument mesh valid: {len(mesh['objects'])} objects, {len(mesh['edges'])} directed edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
