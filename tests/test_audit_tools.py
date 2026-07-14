from __future__ import annotations
import json, subprocess, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/mini-upstream'

class AuditToolsTest(unittest.TestCase):
    def test_inventory_and_pattern_scan(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            subprocess.run(['python3', str(ROOT/'scripts/inventory.py'), str(FIXTURE), '--out', str(out)], check=True)
            inv = json.loads((out/'inventory.json').read_text())
            self.assertEqual(len(inv['files']), 3)
            subprocess.run(['python3', str(ROOT/'scripts/pattern_scan.py'), str(FIXTURE), '--patterns', str(ROOT/'patterns/seed-patterns.json'), '--out', str(out/'matches.jsonl')], check=True)
            matches = [json.loads(x) for x in (out/'matches.jsonl').read_text().splitlines()]
            ids = {m['pattern_id'] for m in matches}
            self.assertIn('WF-001', ids)
            self.assertIn('DF-001', ids)
            self.assertIn('PR-002', ids)

    def test_worklist_balance(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            subprocess.run(['python3', str(ROOT/'scripts/inventory.py'), str(FIXTURE), '--out', str(out)], check=True)
            subprocess.run(['python3', str(ROOT/'scripts/build_worklists.py'), str(out/'inventory.json'), '--workers', '2', '--out', str(out/'worklists')], check=True)
            summary = json.loads((out/'worklists/summary.json').read_text())
            self.assertEqual(len(summary), 2)
            self.assertEqual(sum(x['files'] for x in summary), 3)

if __name__ == '__main__':
    unittest.main()
