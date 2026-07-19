from __future__ import annotations

import hashlib
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_white_paper_candidate import (  # noqa: E402
    ALLOWLIST,
    EXPLORER,
    OUT,
    PAPER,
    build_export,
    canonical,
    explorer_html,
    paper_markdown,
    validate,
    validate_html,
)


class WhitePaperExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUT.read_text(encoding="utf-8"))

    def test_positive_allowlist_and_deterministic_replay(self) -> None:
        rebuilt = build_export()
        self.assertEqual(sorted(rebuilt), sorted(ALLOWLIST))
        self.assertEqual(canonical(rebuilt), OUT.read_bytes())
        self.assertEqual(paper_markdown(rebuilt), PAPER.read_bytes())
        self.assertEqual(explorer_html(rebuilt), EXPLORER.read_bytes())
        self.assertFalse(validate(rebuilt))
        self.assertFalse(validate_html(EXPLORER.read_bytes()))

    def test_every_paragraph_has_hash_bound_genealogy_and_explicit_label(self) -> None:
        argument_ids = {item["argument_id"] for item in self.payload["argument_objects"]}
        for paragraph in self.payload["paragraphs"]:
            expected = hashlib.sha256(canonical(paragraph["genealogy"], compact=True)).hexdigest()
            self.assertEqual(paragraph["genealogy_sha256"], expected)
            self.assertTrue(paragraph["genealogy"]["claim_ids"])
            self.assertTrue(paragraph["genealogy"]["source_ids"])
            self.assertTrue(paragraph["genealogy"]["graph_edge_ids"])
            self.assertIn(paragraph["label"], {"observed", "counterevidence", "hypothesis", "normative", "unknown", "mixed"})
            self.assertNotEqual(paragraph["publication_eligibility"], "eligible")
            self.assertTrue(set(paragraph["genealogy"]["argument_ids"]).issubset(argument_ids))

    def test_explorer_exports_the_required_drilldown_layers(self) -> None:
        self.assertTrue(self.payload["sections"])
        self.assertTrue(self.payload["argument_objects"])
        self.assertTrue(self.payload["graph_edges"])
        html_text = EXPLORER.read_text(encoding="utf-8")
        self.assertIn("paper section → thesis → argument/objection/falsifier → claim → source/chunk locator", html_text)
        self.assertIn("data.argument_objects", html_text)
        self.assertIn("data.graph_edges", html_text)
        paragraphs_by_thesis = {
            paragraph["genealogy"]["thesis_node_ids"][0]: paragraph
            for paragraph in self.payload["paragraphs"]
        }
        for thesis_node in self.payload["thesis_nodes"]:
            self.assertEqual(
                thesis_node["argument_ids"],
                paragraphs_by_thesis[thesis_node["stable_id"]]["genealogy"]["argument_ids"],
            )

        incomplete = deepcopy(self.payload)
        incomplete["thesis_nodes"][0]["argument_ids"] = incomplete["thesis_nodes"][0]["argument_ids"][1:]
        self.assertIn("thesis argument projection is incomplete", "\n".join(validate(incomplete)))

    def test_missing_genealogy_and_release_promotion_fail_closed(self) -> None:
        missing = deepcopy(self.payload)
        missing["paragraphs"][0]["genealogy"]["locators"] = []
        missing["paragraphs"][0]["genealogy_sha256"] = hashlib.sha256(canonical(missing["paragraphs"][0]["genealogy"], compact=True)).hexdigest()
        self.assertIn("incomplete paragraph genealogy", "\n".join(validate(missing)))

        promoted = deepcopy(self.payload)
        promoted["release"]["release_eligible"] = True
        self.assertTrue(validate(promoted))

    def test_no_private_paths_mojibake_or_external_browser_requests(self) -> None:
        export_text = OUT.read_text(encoding="utf-8")
        for marker in (".private/", "private/", "C:\\Users\\", "C:/Users/", "\ufffd", "â€™"):
            self.assertNotIn(marker, export_text)
        html_text = EXPLORER.read_text(encoding="utf-8")
        for token in ("fetch(", "XMLHttpRequest", "WebSocket", "<script src=", "<link rel=", "<form"):
            self.assertNotIn(token.lower(), html_text.lower())

    def test_absolute_paths_and_protected_fields_fail_closed(self) -> None:
        for absolute_path in ("C:/Users/lowel/secret.txt", r"\\server\share\secret.txt", "/home/lowel/secret.txt"):
            leaked = deepcopy(self.payload)
            leaked["sources"][0]["locator"] = absolute_path
            self.assertIn("absolute machine path", "\n".join(validate(leaked)))

        protected = deepcopy(self.payload)
        protected["sources"][0]["raw_conversation"] = "redacted"
        self.assertIn("forbidden field", "\n".join(validate(protected)))


if __name__ == "__main__":
    unittest.main()
