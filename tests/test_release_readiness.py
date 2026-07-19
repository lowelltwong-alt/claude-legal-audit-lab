from __future__ import annotations

import json
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_release_readiness import compute_inventory, readiness_errors, validate


class ReleaseReadinessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads((ROOT / "registry/release-readiness.json").read_text(encoding="utf-8"))
        cls.inventory = compute_inventory()

    def test_truthful_blocked_registry_is_valid(self):
        self.assertEqual(validate(self.payload, self.inventory), [])
        self.assertTrue(readiness_errors(self.payload, self.inventory))
        subprocess.run([sys.executable, str(ROOT / "scripts/validate_release_readiness.py")], check=True)

    def test_require_ready_fails_closed(self):
        result = subprocess.run([
            sys.executable,
            str(ROOT / "scripts/validate_release_readiness.py"),
            "--require-ready",
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("BLOCKED:", result.stderr)

    def test_adversarial_release_mutations_fail(self):
        stale = deepcopy(self.payload)
        stale["inventory_snapshot"]["tracked_file_count"] += 1
        self.assertTrue(validate(stale, self.inventory))

        tracked_private = deepcopy(self.inventory)
        tracked_private["tracked_paths"] = tracked_private["tracked_paths"] + [".private/raw/secret.txt"]
        self.assertTrue(validate(self.payload, tracked_private))

        mutable_private_prefixes = deepcopy(self.payload)
        mutable_private_prefixes["private_path_patterns"] = ["not-private/", "also-public/"]
        self.assertTrue(validate(mutable_private_prefixes, self.inventory))

        false_ready = deepcopy(self.payload)
        false_ready["status"] = "ready"
        self.assertTrue(readiness_errors(false_ready, self.inventory))

        approval_only = deepcopy(self.payload)
        approval_only["human_release_approved"] = True
        self.assertTrue(readiness_errors(approval_only, self.inventory))

        arbitrary_commit = deepcopy(self.payload)
        arbitrary_commit["release_candidate"]["frozen"] = True
        arbitrary_commit["release_candidate"]["commit"] = "0" * 40
        self.assertIn("release candidate commit does not match HEAD", readiness_errors(arbitrary_commit, self.inventory))

        asserted_artifacts = deepcopy(self.payload)
        asserted_artifacts["release_candidate"].update({
            "allowlist_path": "README.md",
            "allowlist_sha256": "0" * 64,
            "export_path": "README.md",
            "export_sha256": "1" * 64,
        })
        artifact_errors = readiness_errors(asserted_artifacts, self.inventory)
        self.assertIn("release allowlist hash does not match its bytes", artifact_errors)
        self.assertIn("release export hash does not match its bytes", artifact_errors)

        mismatched_approval = deepcopy(asserted_artifacts)
        mismatched_approval["human_release_approved"] = True
        mismatched_approval["human_approval"] = {
            "approver": "repository owner",
            "approved_at": "2026-07-14T23:45:00-04:00",
            "export_sha256": "2" * 64,
            "evidence_refs": ["docs/ROADMAP_CONTROL_REVIEW.md"],
        }
        self.assertIn("human approval is not bound to the exact export hash", readiness_errors(mismatched_approval, self.inventory))

        invalid_timestamp = deepcopy(mismatched_approval)
        invalid_timestamp["human_approval"]["approved_at"] = "not-a-timestamp"
        self.assertTrue(validate(invalid_timestamp, self.inventory))


if __name__ == "__main__":
    unittest.main()
