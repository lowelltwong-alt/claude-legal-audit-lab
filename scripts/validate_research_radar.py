#!/usr/bin/env python3
"""Fail-closed validator for contribution, industry taxonomy, and radar records."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACETS = ("O", "F", "X", "C", "P", "E")
EPISTEMIC_STATES = {"Observed", "Inferred", "Hypothesis", "Unknown"}
FRESHNESS_STATES = {"current", "watch", "stale", "superseded", "unknown"}
REVIEW_STATES = {"candidate", "under_review", "reviewed", "rejected", "retracted"}
PUBLIC_GOVERNANCE_PATHS = (
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/CROSS_INDUSTRY_ONTOLOGY_RISK.md",
    "docs/RESEARCH_CONTRIBUTION_MODEL.md",
    "docs/RESEARCH_RADAR.md",
    "docs/LICENSING_OPTIONS.md",
    "docs/CONTRIBUTION_RADAR_DECISION.md",
    "registry/industry-research-taxonomy.json",
    "registry/research-radar-watchlist.json",
)


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def parse_time(value: str | None, field: str, errors: list[str]) -> None:
    if value is None:
        return
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        errors.append(f"invalid ISO timestamp {field}: {value!r}")


def structural_p0(facets: dict[str, int]) -> bool:
    return (
        facets["O"] >= 2
        and facets["F"] >= 2
        and facets["C"] >= 2
        and (facets["X"] >= 2 or facets["P"] >= 2)
    )


def research_priority(facets: dict[str, int | None]) -> str:
    """Implement methodology v1.0.0 exactly; this is urgency, not harm risk."""
    if any(facets[name] is None for name in FACETS):
        possible = {name: 3 if facets[name] is None else facets[name] for name in FACETS}
        return "P1" if structural_p0(possible) else "P3"
    known = {name: int(facets[name]) for name in FACETS}
    if structural_p0(known) and known["E"] >= 2:
        return "P0"
    if structural_p0(known) and known["E"] < 2:
        return "P1"
    high_structural = sum(known[name] >= 2 for name in ("O", "F", "X", "C", "P"))
    if high_structural in {2, 3} and known["E"] >= 2:
        return "P2"
    return "P3"


def validate_signal(path: Path, source_ids: set[str], industry_ids: set[str], families: set[str], errors: list[str]) -> None:
    try:
        signal = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid signal JSON {path.relative_to(ROOT)}: {exc}")
        return
    label = signal.get("signal_id", path.name)
    if signal.get("schema") != "claude-legal-audit.research-signal.v1":
        errors.append(f"{label}: invalid signal schema")
    if not re.fullmatch(r"SIG-[0-9]{4}-[0-9]{4}", signal.get("signal_id", "")):
        errors.append(f"{label}: invalid signal ID")
    if signal.get("candidate_only") is not True:
        errors.append(f"{label}: signal must remain candidate_only")
    if signal.get("signal_family") not in families:
        errors.append(f"{label}: unknown signal family")
    if signal.get("epistemic_status") not in EPISTEMIC_STATES:
        errors.append(f"{label}: invalid epistemic status")
    if len(signal.get("does_not_prove", "")) < 20:
        errors.append(f"{label}: does_not_prove is missing or too short")
    if not signal.get("confirmation_tests") or not signal.get("falsifiers"):
        errors.append(f"{label}: confirmation tests and falsifiers are required")
    for ref in signal.get("source_refs", []):
        if ref.get("source_id") not in source_ids:
            errors.append(f"{label}: unknown source {ref.get('source_id')}")
        if not ref.get("revision") or not ref.get("locator"):
            errors.append(f"{label}: source reference lacks revision or locator")
    for industry_id in signal.get("industry_ids", []):
        if industry_id not in industry_ids:
            errors.append(f"{label}: unknown industry {industry_id}")
    for name, value in signal.get("times", {}).items():
        parse_time(value, f"{label}.times.{name}", errors)
    freshness = signal.get("freshness", {})
    if freshness.get("status") not in FRESHNESS_STATES:
        errors.append(f"{label}: invalid freshness status")
    for name in ("last_verified_at", "next_review_at"):
        parse_time(freshness.get(name), f"{label}.freshness.{name}", errors)
    review = signal.get("review", {})
    if review.get("status") not in REVIEW_STATES or review.get("human_promotion_required") is not True:
        errors.append(f"{label}: invalid review or human-promotion gate")
    if review.get("status") == "reviewed" and (
        not review.get("independent_reviewer")
        or review.get("independent_reviewer") == review.get("author")
    ):
        errors.append(f"{label}: reviewed signal lacks an independent reviewer")


def main() -> int:
    errors: list[str] = []
    sources = load("registry/source-registry.json")["sources"]
    source_ids = {row["source_id"] for row in sources}
    taxonomy = load("registry/industry-research-taxonomy.json")
    watchlist = load("registry/research-radar-watchlist.json")

    if taxonomy.get("methodology_version") != "1.0.0":
        errors.append("industry taxonomy must cite methodology version 1.0.0")
    if taxonomy.get("methodology_document") != "docs/CROSS_INDUSTRY_ONTOLOGY_RISK.md":
        errors.append("industry taxonomy methodology document is not authoritative")

    industries = taxonomy.get("industries", [])
    industry_ids = [row.get("industry_id") for row in industries]
    if len(industry_ids) != len(set(industry_ids)):
        errors.append("duplicate industry IDs")
    for row in industries:
        industry_id = row.get("industry_id", "<missing-industry-id>")
        if row.get("epistemic_status") not in EPISTEMIC_STATES:
            errors.append(f"{industry_id}: invalid epistemic status")
        facets = row.get("facets", {})
        if set(facets) != set(FACETS):
            errors.append(f"{industry_id}: facet keys must be exactly {FACETS}")
            continue
        for name, value in facets.items():
            if value is not None and (not isinstance(value, int) or not 0 <= value <= 3):
                errors.append(f"{industry_id}: facet {name} outside 0-3 or null")
        expected = research_priority(facets)
        if row.get("priority") != expected:
            errors.append(f"{industry_id}: priority {row.get('priority')} != methodology result {expected}")
        for source_id in row.get("source_ids", []):
            if source_id not in source_ids:
                errors.append(f"{industry_id}: unknown source {source_id}")
        if len(row.get("does_not_prove", "")) < 20:
            errors.append(f"{industry_id}: does_not_prove is missing or too short")

    if watchlist.get("automation_authorized") is not False or watchlist.get("status") != "manual_candidate_only":
        errors.append("research radar automation must remain unauthorized and candidate-only")
    watch_ids = [row.get("watch_id") for row in watchlist.get("source_classes", [])]
    if len(watch_ids) != len(set(watch_ids)):
        errors.append("duplicate watch IDs")
    for row in watchlist.get("source_classes", []):
        if not isinstance(row.get("cadence_days"), int) or row["cadence_days"] < 1:
            errors.append(f"{row.get('watch_id')}: invalid cadence")
        for source_id in row.get("source_ids", []):
            if source_id not in source_ids:
                errors.append(f"{row.get('watch_id')}: unknown source {source_id}")

    families = set(watchlist.get("signal_families", []))
    signal_dir = ROOT / "research" / "signals"
    for path in sorted(signal_dir.glob("*.json")) if signal_dir.exists() else []:
        validate_signal(path, source_ids, set(industry_ids), families, errors)

    for rel in PUBLIC_GOVERNANCE_PATHS:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing public governance path: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?i)(^|[/\\])\.private([/\\]|$)", text) and rel not in {
            "CONTRIBUTING.md", "SECURITY.md", "docs/CONTRIBUTION_RADAR_DECISION.md"
        }:
            errors.append(f"unexpected private path reference in public governance file: {rel}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        f"research radar valid: {len(industries)} industries, "
        f"{len(watch_ids)} watch classes, "
        f"{len(list(signal_dir.glob('*.json'))) if signal_dir.exists() else 0} signals"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
