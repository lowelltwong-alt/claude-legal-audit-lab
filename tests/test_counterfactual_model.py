from __future__ import annotations

import ast
import json
import subprocess
import sys
import unittest
from collections import Counter
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_counterfactual_graph import REQUIRED_FORBIDDEN_ACTIONS, build, validate
from validate_navigation import resolve_route


class CounterfactualModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value_chain = json.loads((ROOT / "registry/law-firm-value-chain.json").read_text(encoding="utf-8"))
        cls.patterns = json.loads((ROOT / "registry/counterfactual-capture-patterns.json").read_text(encoding="utf-8"))
        cls.graph = json.loads((ROOT / "registry/counterfactual-exposure-graph.json").read_text(encoding="utf-8"))

    def test_full_value_chain_and_safety_policy(self):
        self.assertEqual({row["stage_id"] for row in self.value_chain["stages"]}, {f"LF-{i:02d}" for i in range(1, 24)})
        policy = self.patterns["use_policy"]
        self.assertEqual(policy["mode"], "defensive_synthetic_only")
        self.assertEqual(policy["capture_mode"], "conceptual")
        self.assertFalse(policy["collection_enabled"])
        self.assertFalse(policy["network_access"])
        self.assertFalse(policy["identity_linkage"])
        self.assertFalse(policy["cross_customer_linkage"])
        self.assertEqual(policy["training_use"], "prohibited")
        self.assertEqual(policy["secondary_use"], "prohibited")
        self.assertTrue(REQUIRED_FORBIDDEN_ACTIONS.issubset(set(policy["forbidden_actions"])))

    def test_every_pattern_is_bounded_and_controlled(self):
        for pattern in self.patterns["patterns"]:
            with self.subTest(pattern=pattern["pattern_id"]):
                self.assertEqual(pattern["implementation_status"], "analysis_only")
                self.assertTrue(pattern["countercontrols"])
                self.assertTrue(pattern["what_it_cannot_prove"])
                self.assertTrue(pattern["applies_when"])
                self.assertTrue(pattern["does_not_apply_when"])
                self.assertTrue(pattern["danger_if_misapplied"])
                self.assertTrue(pattern["source_ids"])
                if pattern["client_content_required"] == "yes":
                    self.assertEqual(pattern["defensive_test_mode"], "synthetic_fixture_only")
                if pattern["defensive_test_mode"] != "public_primary_sources_only":
                    self.assertTrue(pattern["consent_and_authority"]["required"])
        by_id = {row["pattern_id"]: row for row in self.patterns["patterns"]}
        self.assertEqual(by_id["CF-011"]["defensive_test_mode"], "public_primary_sources_only")
        self.assertEqual(by_id["CF-016"]["defensive_test_mode"], "contract_and_policy_review_only")

    def test_adversarial_safety_mutations_fail_validation(self):
        sources = json.loads((ROOT / "registry/source-registry.json").read_text(encoding="utf-8"))

        mutations = []
        missing_source = deepcopy(self.patterns)
        missing_source["patterns"][0]["source_ids"] = []
        mutations.append(missing_source)

        missing_consent = deepcopy(self.patterns)
        missing_consent["patterns"][0]["consent_and_authority"]["required"] = False
        mutations.append(missing_consent)

        sealed_material = deepcopy(self.patterns)
        by_id = {row["pattern_id"]: row for row in sealed_material["patterns"]}
        by_id["CF-011"]["scenario_constraints"]["sealed_or_restricted_material"] = True
        mutations.append(sealed_material)

        evasion_design = deepcopy(self.patterns)
        by_id = {row["pattern_id"]: row for row in evasion_design["patterns"]}
        by_id["CF-016"]["scenario_constraints"]["evasion_design"] = True
        mutations.append(evasion_design)

        source_inheritance = deepcopy(self.patterns)
        source_inheritance["evidence_binding_contract"]["child_edge_source_inheritance"] = True
        mutations.append(source_inheritance)

        for index, mutated in enumerate(mutations):
            with self.subTest(mutation=index):
                self.assertTrue(validate(self.value_chain, mutated, sources))

    def test_builder_and_generated_projection_are_deterministic(self):
        payload, errors = build()
        self.assertEqual(errors, [])
        self.assertEqual(payload, self.graph)
        subprocess.run([sys.executable, str(ROOT / "scripts/build_counterfactual_graph.py"), "--check"], check=True)
        node_ids = {node["node_id"] for node in self.graph["nodes"]}
        self.assertGreaterEqual(len(node_ids), 500)
        self.assertGreaterEqual(len(self.graph["edges"]), 900)
        for edge in self.graph["edges"]:
            self.assertIn(edge["source"], node_ids)
            self.assertIn(edge["target"], node_ids)
            self.assertEqual(edge["review_status"], "candidate")
            if edge["binding_type"] == "catalog_context":
                self.assertEqual(len(edge["source_ids"]), 1)
                self.assertEqual(edge["evidence_scope"], "catalog_statement_only")
                self.assertGreater(len(edge["exact_locator"]), 10)
            else:
                self.assertEqual(edge["source_ids"], [])
                self.assertEqual(edge["evidence_scope"], "authored_model_relation")
        outgoing = Counter(edge["source"] for edge in self.graph["edges"])
        for pattern in self.patterns["patterns"]:
            self.assertGreaterEqual(outgoing[pattern["pattern_id"]], 5)

    def test_builder_has_no_network_or_credential_imports(self):
        source = (ROOT / "scripts/build_counterfactual_graph.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        prohibited = {"requests", "urllib", "socket", "httpx", "boto3", "keyring", "subprocess"}
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
        self.assertTrue(prohibited.isdisjoint(imported), imported & prohibited)

    def test_front_door_routes_counterfactual_queries(self):
        routes = json.loads((ROOT / "registry/ai-front-door-registry.json").read_text(encoding="utf-8"))
        self.assertEqual(resolve_route("How could a frontier lab capture a law firm ontology?", routes), "counterfactual_capture")
        self.assertEqual(resolve_route("Protect the attorney brain trust", routes), "counterfactual_capture")


if __name__ == "__main__":
    unittest.main()
