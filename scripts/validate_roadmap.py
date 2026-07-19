#!/usr/bin/env python3
"""Fail-closed validation and unlock-frontier projection for the project roadmap."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
ROADMAP_PATH = ROOT / "registry" / "project-roadmap.json"
SCHEMA_PATH = ROOT / "schemas" / "project-roadmap.schema.json"
LEASE_STATES = {"focus-window", "active"}
TODAY_STATES = {"ready", "focus-window", "active", "validate"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_errors(payload: dict) -> list[str]:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    return [
        f"schema violation at {'.'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in errors
    ]


def coverage_fingerprint(paths: list[str]) -> str:
    hasher = hashlib.sha256()
    for relative in sorted(paths):
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        hasher.update(relative.replace("\\", "/").encode("utf-8") + b"\0")
        hasher.update(path.read_bytes())
    return "sha256:" + hasher.hexdigest()


def durable_evidence_ref(ref: str) -> bool:
    candidate = ref.split(":", 1)[0].strip()
    return bool(candidate) and (ROOT / candidate).is_file()


def valid_datetime(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def reviewed_cycle(dependencies: list[dict], ids: set[str]) -> bool:
    outgoing: dict[str, list[str]] = defaultdict(list)
    indegree = {workstream_id: 0 for workstream_id in ids}
    for edge in dependencies:
        if edge.get("review_status") != "reviewed":
            continue
        prerequisite = edge.get("prerequisite")
        dependent = edge.get("dependent")
        if prerequisite in ids and dependent in ids:
            outgoing[prerequisite].append(dependent)
            indegree[dependent] += 1
    queue = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    seen = 0
    while queue:
        node = queue.popleft()
        seen += 1
        for target in outgoing[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return seen != len(ids)


def validate(payload: dict) -> list[str]:
    errors = schema_errors(payload)
    if not valid_datetime(payload.get("as_of")):
        errors.append("as_of must be an ISO-8601 timestamp with timezone")
    coverage = payload.get("coverage", {})
    try:
        actual_fingerprint = coverage_fingerprint(coverage.get("fingerprint_inputs", []))
        if coverage.get("input_fingerprint") != actual_fingerprint:
            errors.append("coverage input_fingerprint is stale")
    except FileNotFoundError as exc:
        errors.append(f"coverage fingerprint input is missing: {exc.args[0]}")
    graph_summary = load(ROOT / "registry" / "evidence-graph.json").get("summary", {})
    expected_graph_receipt = (
        f"typed evidence graph: {graph_summary.get('node_count')} nodes and "
        f"{graph_summary.get('edge_count')} inverse-paired edges with adversarial validation"
    )
    graph_receipts = [
        item
        for item in payload.get("resume_capsule", {}).get("last_acceptance_evidence", [])
        if item.startswith("typed evidence graph:")
    ]
    if graph_receipts != [expected_graph_receipt]:
        errors.append("resume capsule evidence-graph count is stale or ambiguous")
    workstreams = payload.get("workstreams", [])
    ids = [row.get("workstream_id") for row in workstreams]
    if len(ids) != len(set(ids)):
        errors.append("duplicate workstream IDs")
    workstream_map = {row.get("workstream_id"): row for row in workstreams}
    id_set = set(workstream_map)

    blockers = payload.get("blockers", [])
    blocker_ids = [row.get("blocker_id") for row in blockers]
    if len(blocker_ids) != len(set(blocker_ids)):
        errors.append("duplicate blocker IDs")
    blocker_map = {row.get("blocker_id"): row for row in blockers}

    decisions = payload.get("human_decisions", [])
    decision_ids = [row.get("decision_id") for row in decisions]
    if len(decision_ids) != len(set(decision_ids)):
        errors.append("duplicate human-decision IDs")
    decision_map = {row.get("decision_id"): row for row in decisions}

    evidence_ids: list[str] = []
    for row in workstreams:
        workstream_id = row.get("workstream_id")
        evidence = row.get("acceptance_evidence", [])
        evidence_ids.extend(item.get("evidence_id") for item in evidence)
        for item in evidence:
            if item.get("status") == "passed":
                refs = item.get("evidence_refs", [])
                if not refs:
                    errors.append(f"{item.get('evidence_id')} passed without evidence references")
                elif not any(durable_evidence_ref(ref) for ref in refs):
                    errors.append(f"{item.get('evidence_id')} passed without a durable repository evidence reference")
        if row.get("state") == "delivered" and any(item.get("status") != "passed" for item in evidence):
            errors.append(f"{workstream_id} is delivered without all acceptance evidence passed")
        if row.get("state") == "blocked/waiting" and not row.get("blocker_ids"):
            errors.append(f"{workstream_id} is blocked/waiting without a blocker")
        for blocker_id in row.get("blocker_ids", []):
            if blocker_id not in blocker_map or workstream_id not in blocker_map[blocker_id].get("workstream_ids", []):
                errors.append(f"{workstream_id} has an invalid or non-reciprocal blocker {blocker_id}")
        for decision_id in row.get("human_gate_ids", []):
            if decision_id not in decision_map or workstream_id not in decision_map[decision_id].get("blocks", []):
                errors.append(f"{workstream_id} has an invalid or non-reciprocal human gate {decision_id}")
    if len(evidence_ids) != len(set(evidence_ids)):
        errors.append("duplicate acceptance-evidence IDs")

    for blocker in blockers:
        for workstream_id in blocker.get("workstream_ids", []):
            if workstream_id not in id_set:
                errors.append(f"{blocker.get('blocker_id')} references unknown workstream {workstream_id}")
        for decision_id in blocker.get("human_decision_ids", []):
            if decision_id not in decision_map:
                errors.append(f"{blocker.get('blocker_id')} references unknown decision {decision_id}")
    for decision in decisions:
        for workstream_id in decision.get("blocks", []):
            if workstream_id not in id_set:
                errors.append(f"{decision.get('decision_id')} references unknown workstream {workstream_id}")

    dependencies = payload.get("dependencies", [])
    dependency_keys: list[tuple[str, str]] = []
    for edge in dependencies:
        dependent = edge.get("dependent")
        prerequisite = edge.get("prerequisite")
        dependency_keys.append((dependent, prerequisite))
        if dependent not in id_set or prerequisite not in id_set:
            errors.append(f"dependency references unknown workstream: {dependent} <- {prerequisite}")
        if dependent == prerequisite:
            errors.append(f"self dependency: {dependent}")
    if len(dependency_keys) != len(set(dependency_keys)):
        errors.append("duplicate dependency edges")
    if reviewed_cycle(dependencies, id_set):
        errors.append("reviewed dependency graph contains a cycle")

    today = payload.get("today", [])
    overflow = payload.get("wip_overflow", [])
    if set(today) & set(overflow):
        errors.append("Today and WIP overflow overlap")
    for workstream_id in today:
        if workstream_id not in workstream_map:
            errors.append(f"Today references unknown workstream {workstream_id}")
        elif workstream_map[workstream_id].get("state") not in TODAY_STATES:
            errors.append(f"Today contains ineligible state for {workstream_id}")
    for workstream_id in overflow:
        if workstream_id not in workstream_map:
            errors.append(f"WIP overflow references unknown workstream {workstream_id}")

    active_leases = {
        row.get("workstream_id")
        for row in payload.get("execution_leases", [])
        if row.get("status") == "active"
    }
    for lease in payload.get("execution_leases", []):
        for field in ("start", "expiry"):
            if not valid_datetime(lease.get(field)):
                errors.append(f"{lease.get('lease_id')} {field} must be an ISO-8601 timestamp with timezone")
    for row in workstreams:
        if row.get("state") in LEASE_STATES and row.get("workstream_id") not in active_leases:
            errors.append(f"{row.get('workstream_id')} requires an active execution lease")

    return errors


def unlock_frontier(payload: dict) -> list[str]:
    workstreams = {row["workstream_id"]: row for row in payload["workstreams"]}
    required: dict[str, list[str]] = defaultdict(list)
    for edge in payload["dependencies"]:
        if edge["review_status"] == "reviewed" and edge["strength"] == "required":
            required[edge["dependent"]].append(edge["prerequisite"])
    frontier = []
    for workstream_id, row in workstreams.items():
        if row["state"] not in {"ready", "validate"}:
            continue
        if all(workstreams[parent]["state"] == "delivered" for parent in required[workstream_id]):
            frontier.append(workstream_id)
    return sorted(frontier)


def main() -> int:
    payload = load(ROADMAP_PATH)
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    frontier = unlock_frontier(payload)
    print(
        f"roadmap valid: {len(payload['workstreams'])} workstreams, "
        f"{len(payload['dependencies'])} dependencies; unlock frontier: {', '.join(frontier) or 'none'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
