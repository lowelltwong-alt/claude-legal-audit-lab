from __future__ import annotations

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_thesis_map import markdown, validate  # noqa: E402


class ThesisMapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads((ROOT / "registry" / "thesis-map.json").read_text(encoding="utf-8"))

    def test_candidate_map_and_generated_markdown_are_current(self) -> None:
        self.assertFalse(validate(self.payload))
        self.assertEqual(markdown(self.payload), (ROOT / "docs" / "THESIS_MAP.md").read_bytes())

    def test_node_edge_cardinality_mismatch_is_reported_without_crashing(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["nodes"][0]["evidence_paths"][0]["edge_types"].pop()
        errors = validate(mutated)
        self.assertIn("evidence path length mismatch", "\n".join(errors))

    def test_absent_graph_edge_and_premature_export_are_rejected(self) -> None:
        absent = deepcopy(self.payload)
        absent["nodes"][0]["evidence_paths"][0]["edge_types"][0] = "CONTRADICTS"
        self.assertIn("evidence path edge absent", "\n".join(validate(absent)))

        premature = deepcopy(self.payload)
        premature["nodes"][0]["review_state"] = "reviewed"
        premature["nodes"][0]["export_eligibility"] = "eligible"
        self.assertIn("includes blocked claims", "\n".join(validate(premature)))


if __name__ == "__main__":
    unittest.main()
