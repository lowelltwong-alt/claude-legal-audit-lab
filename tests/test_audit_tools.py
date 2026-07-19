from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/mini-upstream'
sys.path.insert(0, str(ROOT/'scripts'))
from validate_navigation import evidence_is_exact, resolve_route, source_is_reproducible
from capture_github_pr_evidence import allowed_url, custody_path, write_exclusive
from validate_research_radar import research_priority

class AuditToolsTest(unittest.TestCase):
    def test_navigation_and_lineage(self):
        subprocess.run([sys.executable, str(ROOT/'scripts/build_lineage.py'), '--check'], check=True)
        subprocess.run([sys.executable, str(ROOT/'scripts/validate_research_radar.py')], check=True)
        subprocess.run([sys.executable, str(ROOT/'scripts/validate_navigation.py')], check=True)

    def test_local_history_capture_receipt_is_current_and_bounded(self):
        subprocess.run([sys.executable, str(ROOT/'scripts/build_history_capture_receipt.py'), '--check'], check=True)
        manifest = json.loads((ROOT/'registry/repository-history-capture.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['capture_scope'], 'local_ref_snapshot_only')
        self.assertEqual(manifest['completeness']['remote_pagination_verified'], False)

    def test_pr_linkage_is_current_and_does_not_require_remote_objects(self):
        subprocess.run([sys.executable, str(ROOT/'scripts/build_pr_linkage.py'), '--check'], check=True)
        linkage = json.loads((ROOT/'results/pr-commit-diff-linkage.json').read_text(encoding='utf-8'))
        self.assertEqual(linkage['capture']['item_count'], len(linkage['records']))
        self.assertEqual(linkage['summary']['pr_count'], 76)

    def test_research_priority_methodology(self):
        self.assertEqual(research_priority({'O': 3, 'F': 2, 'X': 2, 'C': 3, 'P': 2, 'E': 2}), 'P0')
        self.assertEqual(research_priority({'O': 3, 'F': 2, 'X': 2, 'C': 3, 'P': 2, 'E': 1}), 'P1')
        self.assertEqual(research_priority({'O': 3, 'F': None, 'X': 2, 'C': 3, 'P': 2, 'E': 2}), 'P1')
        self.assertEqual(research_priority({'O': 2, 'F': 2, 'X': 0, 'C': 0, 'P': 0, 'E': 2}), 'P2')
        self.assertEqual(research_priority({'O': 1, 'F': 1, 'X': 1, 'C': 1, 'P': 1, 'E': 2}), 'P3')

    def test_route_overlap_and_tie_fail_closed(self):
        registry = json.loads((ROOT/'registry/ai-front-door-registry.json').read_text(encoding='utf-8'))
        self.assertEqual(resolve_route('Prove this code claim', registry), 'claim_check')
        self.assertEqual(resolve_route('UNRECOGNIZED REQUEST', registry), 'orientation')
        tied = {
            'fallback_route_id': 'fallback',
            'routes': [
                {'route_id': 'a', 'priority': 10, 'triggers': ['claim']},
                {'route_id': 'b', 'priority': 10, 'triggers': ['claim']},
                {'route_id': 'fallback', 'priority': 1, 'triggers': ['overview']}
            ]
        }
        with self.assertRaises(ValueError):
            resolve_route('claim', tied)

    def test_claim_evidence_reproducibility_gate(self):
        self.assertTrue(evidence_is_exact({'locator_kind': 'path_lines', 'locator': 'scripts/example.py lines 10-20'}))
        self.assertFalse(evidence_is_exact({'locator_kind': 'repository_scope', 'locator': 'repository-wide review'}))
        self.assertFalse(source_is_reproducible({'revision_binding': {'kind': 'dated_dynamic_page', 'content_sha256': None}}))
        self.assertTrue(source_is_reproducible({'revision_binding': {'kind': 'git_commit', 'content_sha256': None}}))

    def test_inventory_and_pattern_scan(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            subprocess.run([sys.executable, str(ROOT/'scripts/inventory.py'), str(FIXTURE), '--out', str(out)], check=True)
            inv = json.loads((out/'inventory.json').read_text())
            self.assertEqual(len(inv['files']), 3)
            subprocess.run([sys.executable, str(ROOT/'scripts/pattern_scan.py'), str(FIXTURE), '--patterns', str(ROOT/'patterns/seed-patterns.json'), '--out', str(out/'matches.jsonl')], check=True)
            matches = [json.loads(x) for x in (out/'matches.jsonl').read_text().splitlines()]
            ids = {m['pattern_id'] for m in matches}
            self.assertIn('WF-001', ids)
            self.assertIn('DF-001', ids)
            self.assertIn('PR-002', ids)

    def test_worklist_balance(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            subprocess.run([sys.executable, str(ROOT/'scripts/inventory.py'), str(FIXTURE), '--out', str(out)], check=True)
            subprocess.run([sys.executable, str(ROOT/'scripts/build_worklists.py'), str(out/'inventory.json'), '--workers', '2', '--out', str(out/'worklists')], check=True)
            summary = json.loads((out/'worklists/summary.json').read_text())
            self.assertEqual(len(summary), 2)
            self.assertEqual(sum(x['files'] for x in summary), 3)

    def test_jsonl_validator_reads_utf8_on_windows(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'matches.jsonl'
            path.write_text(
                json.dumps({
                    'pattern_id': 'UTF-001',
                    'category': 'encoding',
                    'name': 'non-ASCII evidence',
                    'path': 'examples/strategy.md',
                    'line': 1,
                    'text': 'Move 37 — stratégie',
                }, ensure_ascii=False) + '\n',
                encoding='utf-8',
            )
            subprocess.run([
                sys.executable,
                str(ROOT/'scripts/validate_jsonl.py'),
                str(path),
                '--kind',
                'pattern-match',
            ], check=True)

    def test_public_history_capture_refuses_path_escape_and_public_output(self):
        self.assertTrue(allowed_url('https://api.github.com/repos/anthropics/claude-for-legal/pulls?state=all&per_page=100'))
        self.assertTrue(allowed_url('https://api.github.com/repos/anthropics/claude-for-legal/commits/' + 'a' * 40))
        self.assertFalse(allowed_url('https://api.github.com/repos/anthropics/claude-for-legal/commits/../users/octocat'))
        self.assertFalse(allowed_url('https://api.github.com/repos/anthropics/claude-for-legal/issues'))
        self.assertFalse(allowed_url('https://api.github.com/repos/other/repo/pulls'))
        with self.assertRaises(SystemExit):
            custody_path(ROOT / 'results' / 'not-private')
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'capture.json'
            write_exclusive(path, b'first')
            with self.assertRaises(SystemExit):
                write_exclusive(path, b'second')
            self.assertEqual(path.read_bytes(), b'first')

if __name__ == '__main__':
    unittest.main()
