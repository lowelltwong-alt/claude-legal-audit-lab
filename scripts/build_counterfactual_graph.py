#!/usr/bin/env python3
"""Build and validate a deterministic, synthetic-only ontology-exposure graph.

This module has no network, telemetry, credential, home-directory, or production
data access. It converts two authored public registries into candidate graph
evidence for defensive review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUE_CHAIN_PATH = ROOT / "registry" / "law-firm-value-chain.json"
PATTERNS_PATH = ROOT / "registry" / "counterfactual-capture-patterns.json"
SOURCES_PATH = ROOT / "registry" / "source-registry.json"
OUTPUT_PATH = ROOT / "registry" / "counterfactual-exposure-graph.json"

REQUIRED_FORBIDDEN_ACTIONS = {
    "covert_collection",
    "deceptive_elicitation",
    "privilege_circumvention",
    "cross_tenant_probing",
    "nonconsensual_personnel_monitoring",
    "regulatory_evasion",
    "real_client_data_processing",
}

PUBLIC_RECORD_CONSTRAINTS = {
    "lawful_public_access_only": True,
    "sealed_or_restricted_material": False,
    "selection_bias_acknowledged": True,
    "internal_deliberation_inferred": False,
}

ACQUISITION_CONSTRAINTS = {
    "evasion_design": False,
    "transaction_playbook": False,
    "jurisdiction_specific_review": True,
}

EDGE_TYPES = {
    "PRECEDES": "A workflow stage can normally lead to another stage; this is not a mandatory path.",
    "PRODUCES_ARTIFACT": "A stage creates or maintains an artifact class.",
    "CLASSIFIED_IN_PLANE": "An artifact or pattern belongs to an analytic asset plane.",
    "EMITS_OPERATIONAL_SIGNAL": "A stage may emit a process or workflow signal.",
    "EMITS_JUDGMENT_SIGNAL": "A stage may emit a professional-judgment signal.",
    "COULD_OBSERVE_STAGE": "A counterfactual pattern could be associated with a stage; it does not assert actual collection.",
    "SEEKS_SIGNAL_CLASS": "A counterfactual pattern values a signal class for the stated hypothetical objective.",
    "COULD_INFER_PLANE": "A pattern could support a bounded inference about an asset plane.",
    "RESTRICTED_BY_CONTROL": "A defensive control limits a stage or counterfactual pattern.",
    "DOES_NOT_PROVE": "A limitation blocks an evidentiary leap from the source node.",
    "SUPPORTED_OR_CONSTRAINED_BY_SOURCE": "A public source supports or materially constrains the modeled statement.",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_id(prefix: str, value: str) -> str:
    token = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16].upper()
    return f"{prefix}-{token}"


def serialize(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def validate(value_chain: dict, patterns: dict, sources: dict) -> list[str]:
    errors: list[str] = []

    if value_chain.get("schema") != "claude-legal-audit.law-firm-value-chain.v1":
        errors.append("unexpected value-chain schema")
    if patterns.get("schema") != "claude-legal-audit.counterfactual-capture-patterns.v1":
        errors.append("unexpected counterfactual-pattern schema")

    value_policy = value_chain.get("use_policy", {})
    pattern_policy = patterns.get("use_policy", {})
    if value_policy.get("mode") != "defensive_synthetic_only":
        errors.append("value-chain mode must be defensive_synthetic_only")
    exact_policy = {
        "mode": "defensive_synthetic_only",
        "capture_mode": "conceptual",
        "collection_enabled": False,
        "network_access": False,
        "identity_linkage": False,
        "cross_customer_linkage": False,
        "training_use": "prohibited",
        "secondary_use": "prohibited",
    }
    for key, expected in exact_policy.items():
        if pattern_policy.get(key) != expected:
            errors.append(f"pattern use_policy.{key} must equal {expected!r}")
    forbidden = set(pattern_policy.get("forbidden_actions", []))
    missing_forbidden = REQUIRED_FORBIDDEN_ACTIONS - forbidden
    if missing_forbidden:
        errors.append(f"missing forbidden actions: {sorted(missing_forbidden)}")
    binding_contract = patterns.get("evidence_binding_contract", {})
    if binding_contract.get("child_edge_source_inheritance") is not False:
        errors.append("child edge source inheritance must remain false")

    source_ids = {row["source_id"] for row in sources.get("sources", [])}
    planes = {row["plane_id"] for row in value_chain.get("asset_planes", [])}
    stages = {row["stage_id"]: row for row in value_chain.get("stages", [])}
    expected_stages = {f"LF-{number:02d}" for number in range(1, 24)}
    if set(stages) != expected_stages:
        errors.append(f"value chain must contain exactly LF-01 through LF-23; got {sorted(stages)}")

    artifact_ids: set[str] = set()
    for stage_id, stage in stages.items():
        for next_stage_id in stage.get("next_stage_ids", []):
            if next_stage_id not in stages:
                errors.append(f"{stage_id} references unknown next stage {next_stage_id}")
        for source_id in stage.get("source_ids", []):
            if source_id not in source_ids:
                errors.append(f"{stage_id} references unknown source {source_id}")
        for artifact in stage.get("artifacts", []):
            artifact_id = artifact.get("artifact_id")
            if artifact_id in artifact_ids:
                errors.append(f"duplicate artifact id {artifact_id}")
            artifact_ids.add(artifact_id)
            for plane_id in artifact.get("asset_planes", []):
                if plane_id not in planes:
                    errors.append(f"{artifact_id} references unknown plane {plane_id}")
        if not stage.get("defensive_controls"):
            errors.append(f"{stage_id} has no defensive controls")
        if not stage.get("does_not_prove"):
            errors.append(f"{stage_id} has no does-not-prove statement")

    pattern_ids: set[str] = set()
    for pattern in patterns.get("patterns", []):
        pattern_id = pattern.get("pattern_id", "<missing>")
        if pattern_id in pattern_ids:
            errors.append(f"duplicate pattern id {pattern_id}")
        pattern_ids.add(pattern_id)
        if pattern.get("implementation_status") != "analysis_only":
            errors.append(f"{pattern_id} must remain analysis_only")
        if pattern.get("client_content_required") == "yes" and pattern.get("defensive_test_mode") != "synthetic_fixture_only":
            errors.append(f"{pattern_id} requires client content conceptually and must be synthetic_fixture_only")
        for stage_id in pattern.get("stage_ids", []):
            if stage_id not in stages:
                errors.append(f"{pattern_id} references unknown stage {stage_id}")
        for plane_id in pattern.get("derived_asset_planes", []):
            if plane_id not in planes:
                errors.append(f"{pattern_id} references unknown plane {plane_id}")
        pattern_source_ids = pattern.get("source_ids", [])
        if not pattern_source_ids:
            errors.append(f"{pattern_id} must cite at least one contextual source")
        for source_id in pattern_source_ids:
            if source_id not in source_ids:
                errors.append(f"{pattern_id} references unknown source {source_id}")
        for field in ("what_it_can_infer", "what_it_cannot_prove", "countercontrols", "applies_when", "does_not_apply_when"):
            if not pattern.get(field):
                errors.append(f"{pattern_id} has no {field}")
        authority = pattern.get("consent_and_authority", {})
        if not authority.get("basis") or not authority.get("decline_path") or not authority.get("human_gate"):
            errors.append(f"{pattern_id} has incomplete consent and authority controls")
        if pattern.get("defensive_test_mode") != "public_primary_sources_only" and authority.get("required") is not True:
            errors.append(f"{pattern_id} must require consent and authority outside the public-source-only lane")

    if len(pattern_ids) < 12:
        errors.append("pattern catalog must contain at least 12 patterns")
    acquisition = next((row for row in patterns.get("patterns", []) if row.get("pattern_id") == "CF-016"), None)
    if not acquisition or acquisition.get("defensive_test_mode") != "contract_and_policy_review_only":
        errors.append("CF-016 acquisition scenario must remain contract_and_policy_review_only")
    public_record = next((row for row in patterns.get("patterns", []) if row.get("pattern_id") == "CF-011"), None)
    if not public_record or public_record.get("defensive_test_mode") != "public_primary_sources_only":
        errors.append("CF-011 public-record reconstruction must remain public_primary_sources_only")
    elif public_record.get("scenario_constraints") != PUBLIC_RECORD_CONSTRAINTS:
        errors.append("CF-011 public-record safety constraints changed")
    if acquisition and acquisition.get("scenario_constraints") != ACQUISITION_CONSTRAINTS:
        errors.append("CF-016 acquisition safety constraints changed")

    return errors


def build() -> tuple[dict, list[str]]:
    value_chain = load(VALUE_CHAIN_PATH)
    patterns = load(PATTERNS_PATH)
    sources = load(SOURCES_PATH)
    errors = validate(value_chain, patterns, sources)
    if errors:
        return {}, errors

    nodes: dict[str, dict] = {}
    edges: dict[tuple[str, str, str], dict] = {}

    def add_node(node_id: str, node_type: str, label: str, **extra: object) -> None:
        candidate = {"node_id": node_id, "node_type": node_type, "label": label, **extra}
        existing = nodes.get(node_id)
        if existing is not None and existing != candidate:
            errors.append(f"conflicting node definition: {node_id}")
        nodes[node_id] = candidate

    def add_edge(
        source: str,
        relation: str,
        target: str,
        basis: str,
        source_ids: list[str] | None = None,
        *,
        binding_type: str = "model_derived",
        exact_locator: str | None = None,
    ) -> None:
        key = (source, relation, target)
        edge = {
            "edge_id": stable_id("EDGE", "|".join(key)),
            "source": source,
            "relation": relation,
            "target": target,
            "basis": basis,
            "source_ids": sorted(set(source_ids or [])),
            "evidence_scope": "catalog_statement_only" if binding_type == "catalog_context" else "authored_model_relation",
            "binding_type": binding_type,
            "exact_locator": exact_locator or basis,
            "review_status": "candidate",
        }
        existing = edges.get(key)
        if existing is None:
            edges[key] = edge
        else:
            existing["source_ids"] = sorted(set(existing["source_ids"]) | set(edge["source_ids"]))

    source_rows = {row["source_id"]: row for row in sources["sources"]}
    used_source_ids = {
        source_id
        for stage in value_chain["stages"]
        for source_id in stage["source_ids"]
    } | {
        source_id
        for pattern in patterns["patterns"]
        for source_id in pattern["source_ids"]
    }

    for plane in value_chain["asset_planes"]:
        add_node(plane["plane_id"], "asset_plane", plane["name"], definition=plane["definition"], boundary=plane["boundary"])
    for source_id in sorted(used_source_ids):
        row = source_rows[source_id]
        add_node(
            source_id,
            "public_source",
            row["title"],
            publisher=row["publisher"],
            url=row["url"],
            locator=row["locator"],
            accessed_at=row["accessed_at"],
            status=row["status"],
            revision_binding=row["revision_binding"],
            limitation=row["limitation"],
        )

    for stage in value_chain["stages"]:
        stage_id = stage["stage_id"]
        add_node(stage_id, "law_firm_stage", stage["name"], scope=stage["scope"], public_evidence_availability=stage["public_evidence_availability"])
        for next_stage_id in stage["next_stage_ids"]:
            add_edge(stage_id, "PRECEDES", next_stage_id, f"{VALUE_CHAIN_PATH.name}:{stage_id}")
        for artifact in stage["artifacts"]:
            artifact_id = artifact["artifact_id"]
            add_node(artifact_id, "artifact_class", artifact["name"], sensitivity=artifact["sensitivity"])
            add_edge(stage_id, "PRODUCES_ARTIFACT", artifact_id, f"{VALUE_CHAIN_PATH.name}:{stage_id}")
            for plane_id in artifact["asset_planes"]:
                add_edge(artifact_id, "CLASSIFIED_IN_PLANE", plane_id, f"{VALUE_CHAIN_PATH.name}:{artifact_id}")
        for signal in stage["operational_signals"]:
            signal_id = stable_id("SIG-OP", signal)
            add_node(signal_id, "operational_signal", signal)
            add_edge(stage_id, "EMITS_OPERATIONAL_SIGNAL", signal_id, f"{VALUE_CHAIN_PATH.name}:{stage_id}")
        for signal in stage["judgment_signals"]:
            signal_id = stable_id("SIG-JD", signal)
            add_node(signal_id, "judgment_signal", signal)
            add_edge(stage_id, "EMITS_JUDGMENT_SIGNAL", signal_id, f"{VALUE_CHAIN_PATH.name}:{stage_id}")
        for control in stage["defensive_controls"]:
            control_id = stable_id("CTRL", control)
            add_node(control_id, "defensive_control", control)
            add_edge(stage_id, "RESTRICTED_BY_CONTROL", control_id, f"{VALUE_CHAIN_PATH.name}:{stage_id}")
        for limitation in stage["does_not_prove"]:
            limitation_id = stable_id("LIMIT", limitation)
            add_node(limitation_id, "evidentiary_limitation", limitation)
            add_edge(stage_id, "DOES_NOT_PROVE", limitation_id, f"{VALUE_CHAIN_PATH.name}:{stage_id}")
        for source_id in stage["source_ids"]:
            add_edge(
                stage_id,
                "SUPPORTED_OR_CONSTRAINED_BY_SOURCE",
                source_id,
                f"{VALUE_CHAIN_PATH.name}:{stage_id}",
                [source_id],
                binding_type="catalog_context",
                exact_locator=source_rows[source_id]["locator"],
            )

    for pattern in patterns["patterns"]:
        pattern_id = pattern["pattern_id"]
        add_node(
            pattern_id,
            "counterfactual_pattern",
            pattern["name"],
            epistemic_status=pattern["epistemic_status"],
            implementation_status=pattern["implementation_status"],
            defensive_test_mode=pattern["defensive_test_mode"],
        )
        for stage_id in pattern["stage_ids"]:
            add_edge(pattern_id, "COULD_OBSERVE_STAGE", stage_id, f"{PATTERNS_PATH.name}:{pattern_id}")
        for signal in pattern["signal_classes"]:
            signal_id = stable_id("SIG-CF", signal)
            add_node(signal_id, "counterfactual_signal_class", signal)
            add_edge(pattern_id, "SEEKS_SIGNAL_CLASS", signal_id, f"{PATTERNS_PATH.name}:{pattern_id}")
        for plane_id in pattern["derived_asset_planes"]:
            add_edge(pattern_id, "COULD_INFER_PLANE", plane_id, f"{PATTERNS_PATH.name}:{pattern_id}")
        for control in pattern["countercontrols"]:
            control_id = stable_id("CTRL", control)
            add_node(control_id, "defensive_control", control)
            add_edge(pattern_id, "RESTRICTED_BY_CONTROL", control_id, f"{PATTERNS_PATH.name}:{pattern_id}")
        for limitation in pattern["what_it_cannot_prove"]:
            limitation_id = stable_id("LIMIT", limitation)
            add_node(limitation_id, "evidentiary_limitation", limitation)
            add_edge(pattern_id, "DOES_NOT_PROVE", limitation_id, f"{PATTERNS_PATH.name}:{pattern_id}")
        for source_id in pattern["source_ids"]:
            add_edge(
                pattern_id,
                "SUPPORTED_OR_CONSTRAINED_BY_SOURCE",
                source_id,
                f"{PATTERNS_PATH.name}:{pattern_id}",
                [source_id],
                binding_type="catalog_context",
                exact_locator=source_rows[source_id]["locator"],
            )

    for edge in edges.values():
        if edge["source"] not in nodes or edge["target"] not in nodes:
            errors.append(f"edge has missing endpoint: {edge['edge_id']}")
        if edge["relation"] not in EDGE_TYPES:
            errors.append(f"edge has unknown relation: {edge['relation']}")

    payload = {
        "schema": "claude-legal-audit.counterfactual-exposure-graph.v1",
        "status": "generated_candidate_evidence",
        "safety_contract": {
            "mode": "defensive_synthetic_only",
            "collection_enabled": False,
            "network_access": False,
            "actual_actor_intent_inferred": False,
            "authority": "Authored registries and cited public sources; named human review is required for promotion or release.",
        },
        "generated_from": {
            "builder_sha256": digest(Path(__file__).resolve()),
            "law_firm_value_chain_sha256": digest(VALUE_CHAIN_PATH),
            "counterfactual_capture_patterns_sha256": digest(PATTERNS_PATH),
            "source_registry_sha256": digest(SOURCES_PATH),
        },
        "edge_type_library": [
            {"edge_type": edge_type, "definition": EDGE_TYPES[edge_type]}
            for edge_type in sorted(EDGE_TYPES)
        ],
        "nodes": [nodes[node_id] for node_id in sorted(nodes)],
        "edges": [edges[key] for key in sorted(edges)],
    }
    return payload, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the generated graph is missing or stale")
    parser.add_argument("--validate-only", action="store_true", help="validate authored inputs without writing")
    args = parser.parse_args()

    payload, errors = build()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    expected = serialize(payload)
    if args.validate_only:
        print(f"counterfactual inputs valid: {len(payload['nodes'])} nodes, {len(payload['edges'])} edges")
        return 0
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_bytes() != expected:
            print("ERROR: registry/counterfactual-exposure-graph.json is stale; run scripts/build_counterfactual_graph.py", file=sys.stderr)
            return 1
        print(f"counterfactual graph current: {len(payload['nodes'])} nodes, {len(payload['edges'])} edges")
        return 0

    OUTPUT_PATH.write_bytes(expected)
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}: {len(payload['nodes'])} nodes, {len(payload['edges'])} edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
