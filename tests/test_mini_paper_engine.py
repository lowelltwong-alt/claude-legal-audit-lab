from __future__ import annotations

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_mini_papers import (  # noqa: E402
    BASE,
    COMPARISON,
    OUT,
    PLAN,
    PLAN_SCHEMA,
    PROFILES,
    SIDECAR_SCHEMA,
    build,
    load,
    ordered_units,
    validate_plan,
)

RELATED_WORK = ROOT / "registry" / "mini-paper-related-work.json"
RELATED_WORK_SCHEMA = ROOT / "schemas" / "mini-paper-related-work.schema.json"
SOURCE_REGISTRY = ROOT / "registry" / "source-registry.json"


class MiniPaperEngineTest(unittest.TestCase):
    def test_deterministic_replay_and_strict_schemas(self) -> None:
        outputs, comparison = build()
        for path, expected in outputs.items():
            self.assertEqual(path.read_bytes(), expected)
        plan = load(PLAN)
        self.assertFalse(list(Draft202012Validator(load(PLAN_SCHEMA)).iter_errors(plan)))
        for profile_id in PROFILES:
            sidecar = load(OUT / f"{profile_id}.sidecar.json")
            self.assertFalse(list(Draft202012Validator(load(SIDECAR_SCHEMA)).iter_errors(sidecar)))
        self.assertIsNone(comparison["universal_winner"])
        self.assertEqual(comparison["mode"], "compare_only")

    def test_anchor_sidecar_and_genealogy_invariants(self) -> None:
        sidecars = {profile: load(OUT / f"{profile}.sidecar.json") for profile in PROFILES}
        expected_units = {f"MPU-{index:04d}" for index in range(1, 8)}
        genealogies: dict[str, set[str]] = {unit_id: set() for unit_id in expected_units}
        for profile, sidecar in sidecars.items():
            paper = (OUT / f"{profile}.md").read_text(encoding="utf-8")
            self.assertEqual({unit["unit_id"] for unit in sidecar["units"]}, expected_units)
            self.assertEqual(len({unit["anchor"] for unit in sidecar["units"]}), 7)
            for unit in sidecar["units"]:
                self.assertEqual(unit["anchor"], unit["unit_id"].lower())
                self.assertEqual(paper.count(f'<a id="{unit["anchor"]}"></a>'), 1)
                genealogies[unit["unit_id"]].add(unit["genealogy_sha256"])
                self.assertTrue(unit["assertion_ids"])
                self.assertTrue(unit["genealogy"]["source_ids"])
                self.assertTrue(unit["genealogy"]["graph_edge_ids"])
        self.assertTrue(all(len(values) == 1 for values in genealogies.values()))

    def test_structure_simulation_is_bounded_and_non_promotional(self) -> None:
        comparison = load(COMPARISON)
        self.assertEqual(len(comparison["profiles"]), 3)
        for profile in comparison["profiles"]:
            simulation = profile["simulation"]
            self.assertEqual(simulation["permutations_evaluated"], 5040)
            self.assertTrue(simulation["planned_is_optimal"])
            self.assertEqual(simulation["planned_score"]["total_basis_points"], 10000)
            self.assertGreater(simulation["optimal_order_count"], 0)
        self.assertIn("cannot promote evidence", comparison["warning"])

    def test_plan_rejects_unknown_tags_and_incomplete_profiles(self) -> None:
        plan, base = load(PLAN), load(BASE)
        bad_tag = deepcopy(plan)
        bad_tag["units"][0]["tags"].append("tag:unknown:invented")
        self.assertIn("unknown tag", "\n".join(validate_plan(bad_tag, base)))
        missing = deepcopy(plan)
        missing["profiles"][0]["sections"][0]["unit_ids"].pop()
        self.assertIn("cover every unit exactly once", "\n".join(validate_plan(missing, base)))

        duplicate = deepcopy(plan)
        duplicate["profiles"][2]["profile_id"] = "executive"
        self.assertIn("executive, academic, and adversarial exactly once", "\n".join(validate_plan(duplicate, base)))

    def test_sidecar_schema_rejects_undeclared_fields(self) -> None:
        sidecar = load(OUT / "executive.sidecar.json")
        sidecar["profile"]["undeclared"] = True
        errors = list(Draft202012Validator(load(SIDECAR_SCHEMA)).iter_errors(sidecar))
        self.assertTrue(errors)

    def test_related_work_receipt_resolves_registered_sources(self) -> None:
        receipt = load(RELATED_WORK)
        self.assertFalse(list(Draft202012Validator(load(RELATED_WORK_SCHEMA)).iter_errors(receipt)))
        registered = {source["source_id"] for source in load(SOURCE_REGISTRY)["sources"]}
        self.assertTrue(set(receipt["sources"]).issubset(registered))
        self.assertTrue(receipt["search_receipt"]["queries"])
        limitations = " ".join(receipt["search_receipt"]["limitations"])
        self.assertIn("not a systematic review", limitations.lower())

    def test_profile_order_changes_do_not_change_unit_identity(self) -> None:
        plan = load(PLAN)
        orders = {profile["profile_id"]: ordered_units(profile) for profile in plan["profiles"]}
        self.assertNotEqual(orders["executive"], orders["adversarial"])
        for profile_id in PROFILES:
            sidecar = load(OUT / f"{profile_id}.sidecar.json")
            self.assertEqual({unit["anchor"] for unit in sidecar["units"]}, {f"mpu-{index:04d}" for index in range(1, 8)})

    def test_no_private_paths_external_requests_or_mojibake(self) -> None:
        for path in OUT.glob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for marker in ("private/", ".private/", "C:/Users/", "C:\\Users\\", "\ufffd", "\u00c2", "\u00c3", "\u251c", "\u2562"):
                self.assertNotIn(marker, text)
            for token in ("fetch(", "XMLHttpRequest", "WebSocket", "<script src="):
                self.assertNotIn(token.lower(), text.lower())


if __name__ == "__main__":
    unittest.main()
