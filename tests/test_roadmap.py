from __future__ import annotations

import json
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_roadmap import unlock_frontier, validate


class RoadmapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads((ROOT / "registry/project-roadmap.json").read_text(encoding="utf-8"))

    def test_current_roadmap_is_valid(self):
        self.assertEqual(validate(self.payload), [])
        subprocess.run([sys.executable, str(ROOT / "scripts/validate_roadmap.py")], check=True)

    def test_frontier_uses_only_reviewed_dependencies(self):
        frontier = unlock_frontier(self.payload)
        self.assertNotIn("CLAO-WS-00", frontier)
        self.assertNotIn("CLAO-WS-01", frontier)
        self.assertIn("CLAO-WS-02", frontier)
        self.assertIn("CLAO-WS-03", frontier)
        self.assertNotIn("CLAO-WS-04", frontier)

    def test_adversarial_mutations_fail(self):
        mutations = []

        passed_without_receipt = deepcopy(self.payload)
        passed_without_receipt["workstreams"][0]["acceptance_evidence"][0]["evidence_refs"] = []
        mutations.append(passed_without_receipt)

        stale_fingerprint = deepcopy(self.payload)
        stale_fingerprint["coverage"]["input_fingerprint"] = "sha256:" + "0" * 64
        mutations.append(stale_fingerprint)

        stale_graph_count = deepcopy(self.payload)
        stale_graph_count["resume_capsule"]["last_acceptance_evidence"] = [
            item.replace("1058 nodes", "1046 nodes")
            for item in stale_graph_count["resume_capsule"]["last_acceptance_evidence"]
        ]
        mutations.append(stale_graph_count)

        invalid_timestamp = deepcopy(self.payload)
        invalid_timestamp["as_of"] = "not-a-timestamp"
        mutations.append(invalid_timestamp)

        false_delivery = deepcopy(self.payload)
        false_delivery["workstreams"][2]["state"] = "delivered"
        mutations.append(false_delivery)

        hidden_overflow = deepcopy(self.payload)
        hidden_overflow["wip_overflow"].append(hidden_overflow["today"][0])
        mutations.append(hidden_overflow)

        unleased_active = deepcopy(self.payload)
        unleased_active["workstreams"][2]["state"] = "active"
        mutations.append(unleased_active)

        reviewed_cycle_payload = deepcopy(self.payload)
        reviewed_cycle_payload["dependencies"].append({
            "dependent": "CLAO-WS-00",
            "prerequisite": "CLAO-WS-01",
            "strength": "required",
            "review_status": "reviewed",
            "evidence": "Adversarial cycle fixture for validator testing.",
        })
        mutations.append(reviewed_cycle_payload)

        missing_blocker = deepcopy(self.payload)
        missing_blocker["workstreams"][3]["state"] = "blocked/waiting"
        missing_blocker["workstreams"][3]["blocker_ids"] = []
        mutations.append(missing_blocker)

        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                self.assertTrue(validate(mutation))


if __name__ == "__main__":
    unittest.main()
