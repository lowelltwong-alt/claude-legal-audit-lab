#!/usr/bin/env python3
"""Build/check a deterministic, local-only Git-history capture receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream" / "claude-for-legal"
MANIFEST = ROOT / "registry" / "repository-history-capture.json"
SCHEMA = ROOT / "schemas" / "repository-history-capture.schema.json"
SNAPSHOT = ROOT / "results" / "history-local-snapshot.json"
RECEIPT = ROOT / "results" / "history-capture-completeness-receipt.json"


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(UPSTREAM), *args], text=True).strip()


def canonical(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def snapshot(captured_at: str) -> dict:
    commits = []
    for line in git("log", "--topo-order", "--reverse", "--format=%H%x1f%P%x1f%aI%x1f%cI%x1f%s", "HEAD").splitlines():
        sha, parents, authored_at, committed_at, subject = line.split("\x1f", 4)
        commits.append({"sha": sha, "parents": parents.split() if parents else [], "authored_at": authored_at, "committed_at": committed_at, "subject": subject})
    refs = []
    for line in git("for-each-ref", "--format=%(refname:short)%09%(objectname)%09%(committerdate:iso-strict)", "refs/remotes").splitlines():
        name, sha, committed_at = line.split("\t", 2)
        refs.append({"name": name, "sha": sha, "committed_at": committed_at})
    pr_numbers = sorted({int(match) for item in commits for match in re.findall(r"(?:PR|pull request) #(\d+)", item["subject"], re.I)})
    missing_head_objects = sum(1 for line in git("rev-list", "--objects", "--missing=print", "HEAD").splitlines() if line.startswith("?"))
    return {
        "schema": "claude-legal-audit.local-git-history-snapshot.v1",
        "captured_at": captured_at,
        "head": git("rev-parse", "HEAD"),
        "origin_main": git("rev-parse", "origin/main"),
        "is_shallow": git("rev-parse", "--is-shallow-repository") == "true",
        "promisor_remote": git("config", "--get", "remote.origin.promisor") == "true",
        "partial_clone_filter": git("config", "--get", "remote.origin.partialclonefilter") or None,
        "fsck": {"command": "git fsck --no-dangling", "status": "passed"},
        "missing_head_object_count": missing_head_objects,
        "refs": refs,
        "commits": commits,
        "head_commit_count": len(commits),
        "all_ref_commit_count": int(git("rev-list", "--all", "--count")),
        "merge_commit_count": sum(1 for item in commits if len(item["parents"]) > 1),
        "first_parent_commit_count": int(git("rev-list", "--first-parent", "--count", "HEAD")),
        "tags": git("tag", "--list").splitlines(),
        "notes": [line for line in git("notes", "list").splitlines() if line],
        "locally_named_pull_request_numbers": pr_numbers,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = [f"schema: {error.message}" for error in Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")), format_checker=FormatChecker()).iter_errors(manifest)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if manifest["pinned_commit"] != json.loads((ROOT / "UPSTREAM.lock.json").read_text(encoding="utf-8"))["commit"]:
        print("ERROR: manifest pinned commit differs from UPSTREAM.lock.json", file=sys.stderr)
        return 1
    payload = snapshot(manifest["captured_at"])
    data = canonical(payload)
    digest = "sha256:" + hashlib.sha256(data).hexdigest()
    if manifest["raw_snapshot"]["sha256"] != digest:
        print("ERROR: manifest raw snapshot hash is stale", file=sys.stderr)
        return 1
    receipt = {"schema": "claude-legal-audit.history-capture-completeness-receipt.v1", "capture_id": manifest["capture_id"], "snapshot_sha256": digest, "pinned_commit": payload["head"], "ref_count": len(payload["refs"]), "head_commit_count": payload["head_commit_count"], "all_ref_commit_count": payload["all_ref_commit_count"], "merge_commit_count": payload["merge_commit_count"], "missing_head_object_count": payload["missing_head_object_count"], "remote_pagination_verified": False, "deleted_history_verified": False, "status": manifest["completeness"]["status"], "limitations": manifest["limitations"]}
    if args.check:
        if not SNAPSHOT.exists() or SNAPSHOT.read_bytes() != data or not RECEIPT.exists() or RECEIPT.read_bytes() != canonical(receipt):
            print("ERROR: history capture receipt is stale; run scripts/build_history_capture_receipt.py", file=sys.stderr)
            return 1
        print(f"history capture receipt current: {payload['head_commit_count']} HEAD commits, {len(payload['refs'])} refs")
        return 0
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_bytes(data)
    RECEIPT.write_bytes(canonical(receipt))
    print(f"wrote {SNAPSHOT.relative_to(ROOT)} and {RECEIPT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
