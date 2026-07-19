#!/usr/bin/env python3
"""Build deterministic, evidence-bound mini white-paper variants and JSON sidecars."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from public_safety import public_content_violations

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "registry" / "mini-paper-plan.json"
PLAN_SCHEMA = ROOT / "schemas" / "mini-paper-plan.schema.json"
SIDECAR_SCHEMA = ROOT / "schemas" / "mini-paper-sidecar.schema.json"
BASE = ROOT / "registry" / "white-paper-export.json"
OUT = ROOT / "public" / "generated-release-artifacts" / "candidate" / "mini-papers"
COMPARISON = OUT / "comparison.json"
PROFILES = ("executive", "academic", "adversarial")
FORBIDDEN_UNICODE = ("\ufffd", "\u00c2", "\u00c3", "\u00e2", "\u251c", "\u2562", "\u0442\u0410")


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def compact(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ordered_units(profile: dict) -> list[str]:
    return [unit_id for section in profile["sections"] for unit_id in section["unit_ids"]]


def score_order(order: tuple[str, ...] | list[str], profile: dict, unit_meta: dict[str, dict], weights: dict[str, int]) -> dict:
    positions = {unit_id: index for index, unit_id in enumerate(order)}
    total = sum(weights.values())
    dimensions = {
        "genealogy": weights["genealogy"] if all(unit_meta[item]["genealogy_complete"] for item in order) else 0,
        "boundary": weights["boundary"] if positions["MPU-0007"] <= 1 else 0,
        "objections": weights["objections"] * sum(unit_meta[item]["has_objection"] for item in order) // len(order),
        "falsifiers": weights["falsifiers"] * sum(unit_meta[item]["has_falsifier"] for item in order) // len(order),
        "profile_order": weights["profile_order"] * sum(positions[left] < positions[right] for left, right in profile["order_constraints"]) // len(profile["order_constraints"]),
        "proof_gaps": weights["proof_gaps"] * sum(unit_meta[item]["has_proof_gap"] for item in order) // len(order),
    }
    return {"total_basis_points": sum(dimensions.values()) * 10000 // total, "dimensions": dimensions, "maximum_basis_points": total}


def simulate(profile: dict, unit_meta: dict[str, dict], weights: dict[str, int]) -> dict:
    planned = tuple(ordered_units(profile))
    best_score = -1
    best_orders: list[tuple[str, ...]] = []
    evaluated = 0
    for candidate in itertools.permutations(planned):
        evaluated += 1
        score = score_order(candidate, profile, unit_meta, weights)["total_basis_points"]
        if score > best_score:
            best_score, best_orders = score, [candidate]
        elif score == best_score:
            best_orders.append(candidate)
    planned_score = score_order(planned, profile, unit_meta, weights)
    return {
        "mode": "structural_stress_test_not_truth_or_persuasion",
        "permutations_evaluated": evaluated,
        "planned_order": list(planned),
        "planned_score": planned_score,
        "maximum_total_basis_points": best_score,
        "optimal_order_count": len(best_orders),
        "planned_is_optimal": planned in best_orders,
        "example_optimal_order": list(best_orders[0]),
    }


def validate_plan(plan: dict, base: dict) -> list[str]:
    errors = [error.message for error in Draft202012Validator(load(PLAN_SCHEMA)).iter_errors(plan)]
    units = plan.get("units", [])
    unit_ids = [unit.get("unit_id") for unit in units]
    thesis_ids = {item["stable_id"] for item in base["thesis_nodes"]}
    vocabulary = set(plan.get("tag_vocabulary", []))
    profile_ids = [profile.get("profile_id") for profile in plan.get("profiles", [])]
    if sorted(profile_ids) != sorted(PROFILES): errors.append("profiles must contain executive, academic, and adversarial exactly once")
    if len(unit_ids) != len(set(unit_ids)): errors.append("duplicate mini-paper unit ID")
    for unit in units:
        if unit.get("thesis_node_id") not in thesis_ids: errors.append(f"unknown thesis node: {unit.get('thesis_node_id')}")
        if not set(unit.get("tags", [])).issubset(vocabulary): errors.append(f"unknown tag in {unit.get('unit_id')}")
        if set(unit.get("text_by_profile", {})) != set(PROFILES): errors.append(f"profile text mismatch in {unit.get('unit_id')}")
    for profile in plan.get("profiles", []):
        order = ordered_units(profile)
        if len(order) != len(set(order)) or set(order) != set(unit_ids): errors.append(f"profile does not cover every unit exactly once: {profile.get('profile_id')}")
        for pair in profile.get("order_constraints", []):
            if not set(pair).issubset(set(unit_ids)): errors.append(f"unknown order constraint unit: {pair}")
    if sum(plan.get("scoring", {}).get("weights_basis_points", {}).values()) != 10000: errors.append("scoring weights must total 10000 basis points")
    return errors


def render_markdown(profile: dict, rendered: list[dict], base: dict) -> bytes:
    by_unit = {item["unit_id"]: item for item in rendered}
    lines = [
        "<!-- Generated by scripts/build_mini_papers.py; do not hand-edit. -->",
        f"# {profile['title']}", "", f"_{profile['subtitle']}_", "",
        "> **Blocked, unpublished research candidate.** Structural scoring compares inspectable paper properties only. It does not measure truth, persuasiveness, legal sufficiency, or publication readiness.", "",
        f"Evidence gate: {base['evidence_coverage']['eligible_claim_count']} of {base['evidence_coverage']['claim_count']} claims eligible; release remains blocked.", "",
    ]
    for section in profile["sections"]:
        lines.extend([f"## {section['title']}", ""])
        for unit_id in section["unit_ids"]:
            item = by_unit[unit_id]
            lines.extend([
                f"<a id=\"{item['anchor']}\"></a>",
                f"### {item['unit_id']} - {item['semantic_role'].replace('_', ' ').title()}", "",
                item["selector"]["exact"], "",
                f"**Evidence boundary:** {item['does_not_prove']}", "",
                f"**Tags:** {', '.join(item['tags'])}", "",
                f"**Genealogy:** claims {', '.join(item['assertion_ids'])}; sources {', '.join(item['genealogy']['source_ids'])}; hash `{item['genealogy_sha256']}`.", "",
            ])
    lines.extend(["## Release boundary", "", "This version is a rhetorical projection of the same registered evidence. It cannot add evidence, promote a claim, or authorize release. Runtime, contractual, and incomplete-history gaps remain explicit.", ""])
    return "\n".join(lines).encode("utf-8")


def build() -> tuple[dict[Path, bytes], dict]:
    plan, base = load(PLAN), load(BASE)
    errors = validate_plan(plan, base)
    if errors: raise ValueError("; ".join(errors))
    base_paragraphs = {item["genealogy"]["thesis_node_ids"][0]: item for item in base["paragraphs"]}
    base_thesis = {item["stable_id"]: item for item in base["thesis_nodes"]}
    units = {item["unit_id"]: item for item in plan["units"]}
    weights = plan["scoring"]["weights_basis_points"]
    unit_meta = {}
    for unit_id, unit in units.items():
        paragraph = base_paragraphs[unit["thesis_node_id"]]
        arguments = paragraph["genealogy"]["argument_ids"]
        unit_meta[unit_id] = {
            "genealogy_complete": all(paragraph["genealogy"].get(key) for key in ("claim_ids", "graph_path_ids", "graph_edge_ids", "source_ids", "locators")),
            "has_objection": any(item.startswith("OBJ-") for item in arguments),
            "has_falsifier": any(item.startswith("FAL-") for item in arguments),
            "has_proof_gap": any(item.startswith("GAP-") for item in arguments),
        }
    outputs: dict[Path, bytes] = {}
    comparison_profiles = []
    for profile in plan["profiles"]:
        profile_id = profile["profile_id"]
        rendered = []
        section_by_unit = {unit_id: section for section in profile["sections"] for unit_id in section["unit_ids"]}
        for order, unit_id in enumerate(ordered_units(profile), start=1):
            unit = units[unit_id]
            thesis = base_thesis[unit["thesis_node_id"]]
            base_paragraph = base_paragraphs[unit["thesis_node_id"]]
            text = unit["text_by_profile"][profile_id]
            genealogy = base_paragraph["genealogy"]
            rendered.append({
                "unit_id": unit_id,
                "render_id": f"MPR-{profile_id}-{unit_id.split('-')[1]}",
                "profile_id": profile_id,
                "section_id": section_by_unit[unit_id]["section_id"],
                "order": order,
                "anchor": unit_id.lower(),
                "tags": sorted(unit["tags"] + [f"tag:audience:{profile_id}"]),
                "assertion_ids": sorted(genealogy["claim_ids"]),
                "semantic_role": unit["semantic_role"],
                "epistemic_status": thesis["epistemic_status"],
                "does_not_prove": thesis["does_not_prove"],
                "genealogy": genealogy,
                "genealogy_sha256": digest(compact(genealogy)),
                "render_sha256": digest(text.encode("utf-8")),
                "selector": {"type": "TextQuoteSelector", "exact": text, "prefix": section_by_unit[unit_id]["title"], "suffix": thesis["does_not_prove"]},
            })
        paper_path = OUT / f"{profile_id}.md"
        paper = render_markdown(profile, rendered, base)
        simulation = simulate(profile, unit_meta, weights)
        sidecar = {
            "schema": "claude-legal-audit.mini-paper-sidecar.v1", "revision": "1.0.0", "status": "blocked_unpublished_candidate",
            "profile": {key: profile[key] for key in ("profile_id", "audience", "title", "subtitle")},
            "paper": {"path": paper_path.relative_to(ROOT).as_posix(), "sha256": digest(paper)},
            "inputs": {PLAN.relative_to(ROOT).as_posix(): digest(PLAN.read_bytes()), BASE.relative_to(ROOT).as_posix(): digest(BASE.read_bytes())},
            "units": rendered,
            "structure_score": simulation,
            "standard_mappings": {
                "w3c_web_annotation": "selector fields use the TextQuoteSelector concept; internal genealogy remains authoritative",
                "w3c_prov": "paper units are entities generated by this deterministic build activity",
                "cito": "reviewed internal evidence edges may later map to a controlled citation-intent subset",
                "jats": "unit_id is reserved for future paragraph or section IDs",
                "ro_crate": "a future frozen release may package papers, sidecars, inputs, and build activity",
                "nanopublication": "reviewed claims may later export as assertion/provenance/publication-info graphs"
            }
        }
        schema_errors = [error.message for error in Draft202012Validator(load(SIDECAR_SCHEMA)).iter_errors(sidecar)]
        if schema_errors: raise ValueError("; ".join(schema_errors))
        for violation in public_content_violations(sidecar): raise ValueError(f"forbidden sidecar content: {violation}")
        for marker in FORBIDDEN_UNICODE:
            if marker in paper.decode("utf-8") or marker in canonical(sidecar).decode("utf-8"): raise ValueError(f"mojibake marker: {marker!r}")
        outputs[paper_path] = paper
        outputs[OUT / f"{profile_id}.sidecar.json"] = canonical(sidecar)
        comparison_profiles.append({"profile_id": profile_id, "audience": profile["audience"], "simulation": simulation})
    dimension_leaders = {}
    for dimension in weights:
        scores = {item["profile_id"]: item["simulation"]["planned_score"]["dimensions"][dimension] for item in comparison_profiles}
        maximum = max(scores.values())
        dimension_leaders[dimension] = {"maximum_earned_basis_points": maximum, "profiles": sorted(key for key, value in scores.items() if value == maximum)}
    comparison = {
        "schema": "claude-legal-audit.mini-paper-comparison.v1", "revision": "1.0.0", "status": "blocked_unpublished_candidate",
        "mode": "compare_only", "universal_winner": None,
        "warning": "Scores compare inspectable structure only; they cannot promote evidence, measure truth or persuasion, or authorize publication.",
        "profiles": comparison_profiles, "dimension_leaders": dimension_leaders,
    }
    outputs[COMPARISON] = canonical(comparison)
    return outputs, comparison


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        outputs, comparison = build()
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: mini-paper build failed: {exc}", file=sys.stderr)
        return 1
    if args.check:
        stale = [path.relative_to(ROOT).as_posix() for path, data in outputs.items() if not path.is_file() or path.read_bytes() != data]
        if stale:
            print("ERROR: stale mini-paper artifacts: " + ", ".join(stale), file=sys.stderr)
            return 1
        print(f"mini-paper engine current: {len(PROFILES)} profiles; {sum(item['simulation']['permutations_evaluated'] for item in comparison['profiles'])} structures simulated; release blocked")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for path, data in outputs.items(): path.write_bytes(data)
    print(f"wrote {len(PROFILES)} mini papers, sidecars, and comparison; release blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
