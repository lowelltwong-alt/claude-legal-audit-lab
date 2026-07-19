from __future__ import annotations

import json
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_argument_mesh import validate


class ArgumentMeshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mesh = json.loads((ROOT / "registry/argument-mesh.json").read_text(encoding="utf-8"))
        cls.sources = json.loads((ROOT / "registry/source-registry.json").read_text(encoding="utf-8"))
        cls.claims = json.loads((ROOT / "registry/claim-registry.json").read_text(encoding="utf-8"))

    def validate(self, mesh: dict) -> list[str]:
        return validate(
            mesh,
            {row["source_id"] for row in self.sources["sources"]},
            {row["claim_id"] for row in self.claims["claims"]},
        )

    def test_mesh_and_reverse_dependencies_are_valid(self):
        self.assertEqual(self.validate(self.mesh), [])
        subprocess.run([sys.executable, str(ROOT / "scripts/validate_argument_mesh.py")], check=True)

    def test_thesis_keeps_objections_and_gaps_and_arguments_keep_disconfirmation(self):
        edges = self.mesh["edges"]
        relations = {row["relation"] for row in edges if row["source"] == "THS-0001"}
        self.assertTrue({"SUPPORTED_BY", "CHALLENGED_BY", "HAS_PROOF_GAP", "PRESENTED_IN"}.issubset(relations))
        weakened = {row["target"] for row in edges if row["relation"] == "WEAKENED_BY"}
        self.assertEqual(weakened, {"FAL-0001", "FAL-0002", "FAL-0003"})

    def test_adversarial_mutations_fail(self):
        mutations = []

        promoted = deepcopy(self.mesh)
        promoted["objects"][0]["review_status"] = "reviewed"
        mutations.append(promoted)

        missing_boundary = deepcopy(self.mesh)
        missing_boundary["objects"][1]["does_not_prove"] = ""
        mutations.append(missing_boundary)

        missing_reverse = deepcopy(self.mesh)
        missing_reverse["edges"] = [row for row in missing_reverse["edges"] if row["edge_id"] != "AME-0002"]
        mutations.append(missing_reverse)

        missing_objection = deepcopy(self.mesh)
        missing_objection["edges"] = [
            row for row in missing_objection["edges"]
            if not (row["source"] == "THS-0001" and row["relation"] == "CHALLENGED_BY")
        ]
        mutations.append(missing_objection)

        missing_statement = deepcopy(self.mesh)
        del missing_statement["objects"][0]["statement"]
        mutations.append(missing_statement)

        invalid_epistemic_status = deepcopy(self.mesh)
        invalid_epistemic_status["objects"][0]["epistemic_status"] = "Certain"
        mutations.append(invalid_epistemic_status)

        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=index):
                self.assertTrue(self.validate(mutation))


if __name__ == "__main__":
    unittest.main()
