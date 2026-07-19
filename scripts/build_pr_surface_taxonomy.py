#!/usr/bin/env python3
"""Classify changed paths in locally available PR diffs by observable surface."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream" / "claude-for-legal"
LINKAGE = ROOT / "results" / "pr-commit-diff-linkage.json"
OUTPUT = ROOT / "results" / "pr-surface-taxonomy.json"


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(UPSTREAM), *args], text=True)


def classify(path: str) -> str:
    lower = path.lower()
    if lower.startswith(".github/") or "cla" in lower and ("workflow" in lower or "contributing" in lower):
        return "contribution_or_automation_governance"
    if "managed-agent" in lower or "managed_agent" in lower:
        return "managed_agent_deployment"
    if any(term in lower for term in ("cocounsel", "lexis", "external_plugins", "partner")):
        return "partner_or_external_integration"
    if lower.endswith(("readme.md", "claude.md", ".md")):
        return "documentation_or_instruction"
    if lower.startswith("scripts/") or lower.endswith((".sh", ".py")):
        return "automation_or_script"
    if lower.endswith((".mcp.json", ".json", ".yaml", ".yml")):
        return "configuration_or_metadata"
    if "/skills/" in lower or lower.startswith("skills/"):
        return "skill_or_workflow_instruction"
    return "other_observable_surface"


def canonical(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    linkage = json.loads(LINKAGE.read_text(encoding="utf-8"))
    records = []
    for pr in linkage["records"]:
        if not pr["diff_summary"]:
            continue
        rows = []
        for line in git("diff-tree", "--no-commit-id", "--name-status", "-r", pr["base_sha"], pr["merge_commit_sha"]).splitlines():
            status, path = line.split("\t", 1)
            rows.append({"status": status, "path": path, "surface": classify(path)})
        counts = Counter(row["surface"] for row in rows)
        records.append({"pr_number": pr["pr_number"], "html_url": pr["html_url"], "merge_commit_sha": pr["merge_commit_sha"], "base_sha": pr["base_sha"], "changed_paths": rows, "surface_counts": dict(sorted(counts.items())), "bounded_observation": "Categories classify changed path names and Git status only. They do not establish purpose, priority, customer usage, provider behavior, or strategy."})
    payload = {"schema": "claude-legal-audit.pr-surface-taxonomy.v1", "input_linkage_capture_sha256": linkage["capture"]["sha256"], "records": records, "summary": {"locally_linked_pr_count": len(records), "surface_counts": dict(sorted(Counter(surface for record in records for row in record["changed_paths"] for surface in [row["surface"]]).items()))}}
    data = canonical(payload)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != data:
            print("ERROR: PR surface taxonomy is stale; run scripts/build_pr_surface_taxonomy.py", file=sys.stderr); return 1
        print(f"PR surface taxonomy current: {len(records)} PRs")
        return 0
    OUTPUT.write_bytes(data); print(f"wrote {OUTPUT.relative_to(ROOT)}: {len(records)} PRs"); return 0


if __name__ == "__main__": raise SystemExit(main())
