from __future__ import annotations

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_evidence_graph import edge_identifier, validate  # noqa: E402


class EvidenceGraphTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads((ROOT / "registry" / "evidence-graph.json").read_text(encoding="utf-8"))

    def assert_invalid(self, payload: dict, fragment: str) -> None:
        errors = validate(payload)
        self.assertTrue(errors, "mutated evidence graph unexpectedly passed")
        self.assertIn(fragment.lower(), "\n".join(errors).lower())

    def test_authoritative_graph_passes_all_contracts(self) -> None:
        self.assertFalse(validate(self.payload))

    def test_chunk_review_state_is_preserved_without_blocking_reproducibility(self) -> None:
        chunks = json.loads((ROOT / "registry" / "chunk-registry.json").read_text(encoding="utf-8"))["chunks"]
        expected = {chunk["chunk_id"]: chunk["review_status"] for chunk in chunks}
        actual = {
            node["node_id"]: node["review_state"]
            for node in self.payload["nodes"]
            if node["node_type"] == "chunk"
        }
        self.assertEqual(actual, expected)

    def test_orphan_and_missing_inverse_are_rejected(self) -> None:
        orphan = deepcopy(self.payload)
        orphan["edges"][0]["target_node_id"] = "missing:node"
        self.assert_invalid(orphan, "unknown graph edge endpoint")

        missing = deepcopy(self.payload)
        inverse_id = missing["edges"][0]["inverse_edge_id"]
        missing["edges"] = [edge for edge in missing["edges"] if edge["edge_id"] != inverse_id]
        self.assert_invalid(missing, "missing required inverse")

    def test_containment_cycle_and_authority_inversion_are_rejected(self) -> None:
        cycle = deepcopy(self.payload)
        original = next(edge for edge in cycle["edges"] if edge["edge_type"] == "CONTAINS" and edge["source_node_id"] == "THY-0001" and edge["target_node_id"] == "THS-0001")
        reverse = deepcopy(original)
        reverse["source_node_id"], reverse["target_node_id"] = "THS-0001", "THY-0001"
        reverse["edge_id"] = edge_identifier("CONTAINS", "THS-0001", "THY-0001")
        reverse["inverse_edge_id"] = edge_identifier("CONTAINED_BY", "THY-0001", "THS-0001")
        inverse = deepcopy(original)
        inverse["edge_type"] = "CONTAINED_BY"
        inverse["source_node_id"], inverse["target_node_id"] = "THY-0001", "THS-0001"
        inverse["edge_id"] = reverse["inverse_edge_id"]
        inverse["inverse_edge_id"] = reverse["edge_id"]
        cycle["edges"].extend([reverse, inverse])
        cycle["summary"]["edge_count"] += 2
        self.assert_invalid(cycle, "forbidden CONTAINS cycle")

        inversion = deepcopy(self.payload)
        edge = next(item for item in inversion["edges"] if item["authority"] == "candidate_analysis")
        edge["authority"] = "primary_source"
        self.assert_invalid(inversion, "authority inversion")

    def test_source_to_claim_and_eligible_chunk_genealogy_are_enforced(self) -> None:
        unsupported = deepcopy(self.payload)
        removed_ids = {
            edge["edge_id"]
            for edge in unsupported["edges"]
            if (edge["source_node_id"], edge["edge_type"], edge["target_node_id"])
            in {("SRC-0001", "EVIDENCES", "CLM-0001"), ("CLM-0001", "EVIDENCED_BY", "SRC-0001")}
        }
        unsupported["edges"] = [edge for edge in unsupported["edges"] if edge["edge_id"] not in removed_ids]
        unsupported["summary"]["edge_count"] -= len(removed_ids)
        self.assert_invalid(unsupported, "unsupported source-to-claim path")

        ungrounded = deepcopy(self.payload)
        node_types = {node["node_id"]: node["node_type"] for node in ungrounded["nodes"]}
        removed_ids = {
            edge["edge_id"]
            for edge in ungrounded["edges"]
            if (
                edge["edge_type"] == "EVIDENCES"
                and edge["target_node_id"] == "CLM-0002"
                and node_types.get(edge["source_node_id"]) == "chunk"
            )
            or (
                edge["edge_type"] == "EVIDENCED_BY"
                and edge["source_node_id"] == "CLM-0002"
                and node_types.get(edge["target_node_id"]) == "chunk"
            )
        }
        ungrounded["edges"] = [edge for edge in ungrounded["edges"] if edge["edge_id"] not in removed_ids]
        ungrounded["summary"]["edge_count"] -= len(removed_ids)
        self.assert_invalid(ungrounded, "eligible claim lacks exact reproducible genealogy")

        disconnected = deepcopy(self.payload)
        located_chunks = {
            edge["target_node_id"]
            for edge in disconnected["edges"]
            if edge["source_node_id"] == "SRC-0002" and edge["edge_type"] == "LOCATES"
        }
        exact_chunk = next(
            edge["source_node_id"]
            for edge in disconnected["edges"]
            if edge["target_node_id"] == "CLM-0002"
            and edge["edge_type"] == "EVIDENCES"
            and edge["source_node_id"] in located_chunks
        )
        removed_ids = {
            edge["edge_id"]
            for edge in disconnected["edges"]
            if (
                edge["source_node_id"], edge["edge_type"], edge["target_node_id"]
            ) in {
                ("SRC-0002", "LOCATES", exact_chunk),
                (exact_chunk, "LOCATED_BY", "SRC-0002"),
            }
        }
        disconnected["edges"] = [edge for edge in disconnected["edges"] if edge["edge_id"] not in removed_ids]
        disconnected["summary"]["edge_count"] -= len(removed_ids)
        self.assert_invalid(disconnected, "eligible claim lacks exact reproducible genealogy")

        unreviewed_path = deepcopy(self.payload)
        for edge in unreviewed_path["edges"]:
            if (edge["source_node_id"], edge["edge_type"], edge["target_node_id"]) in {
                ("SRC-0002", "LOCATES", exact_chunk),
                (exact_chunk, "LOCATED_BY", "SRC-0002"),
            }:
                edge["review_state"] = "candidate"
        self.assert_invalid(unreviewed_path, "eligible claim lacks exact reproducible genealogy")

        false_derivative = deepcopy(self.payload)
        exact_chunk_node = next(node for node in false_derivative["nodes"] if node["node_id"] == exact_chunk)
        exact_chunk_node["creation_method"] = "candidate_authoring"
        self.assert_invalid(false_derivative, "eligible claim lacks exact reproducible genealogy")

    def test_private_path_leakage_is_rejected(self) -> None:
        leaked = deepcopy(self.payload)
        file_node = next(node for node in leaked["nodes"] if node["node_type"] == "file")
        file_node["attributes"]["path"] = "private/raw/source.json"
        self.assert_invalid(leaked, "forbidden public graph content")

        for absolute_path in ("C:/Users/lowel/secret.txt", r"\\server\share\secret.txt", "/home/lowel/secret.txt"):
            leaked = deepcopy(self.payload)
            file_node = next(node for node in leaked["nodes"] if node["node_type"] == "file")
            file_node["attributes"]["path"] = absolute_path
            self.assert_invalid(leaked, "stale file node identity")


if __name__ == "__main__":
    unittest.main()
