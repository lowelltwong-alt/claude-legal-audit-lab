#!/usr/bin/env python3
"""Link a captured public PR list to locally available Git commits and diffs."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from capture_github_pr_evidence import canonical_endpoint_path, verified_next_url
from public_safety import public_content_violations

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream" / "claude-for-legal"
CAPTURE_DIRS = (
    ROOT / "private" / "raw" / "sources" / "SRC-0013",
    ROOT / ".private" / "raw-research" / "sources" / "SRC-0013",
)
OUTPUT = ROOT / "results" / "pr-commit-diff-linkage.json"


def canonical(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(UPSTREAM), *args], capture_output=True, text=True, check=check)


def capture_files(pattern: str):
    for root in CAPTURE_DIRS:
        if root.is_dir():
            yield from root.rglob(pattern)


def custody_id(metadata: dict) -> str:
    material = f"{metadata.get('retrieved_at', '')}\0{metadata.get('sha256', '')}".encode("utf-8")
    return "custody:sha256:" + hashlib.sha256(material).hexdigest()


def find_pull_capture() -> tuple[dict, list[dict]]:
    candidates = []
    for metadata_path in capture_files("*.capture.json"):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if "/pulls?" in metadata.get("requested_url", ""):
            candidates.append((metadata["retrieved_at"], metadata_path, metadata))
    if not candidates:
        raise SystemExit("no pull-list capture metadata found")
    _, metadata_path, metadata = max(candidates)
    payload_path = ROOT / metadata["payload_path"]
    body = payload_path.read_bytes()
    if hashlib.sha256(body).hexdigest() != metadata["sha256"]:
        raise SystemExit("pull-list capture hash mismatch")
    payload = json.loads(body)
    if not isinstance(payload, list):
        raise SystemExit("pull-list capture is not a JSON list")
    return metadata, payload


def verified_api_capture(path: str) -> tuple[dict, dict] | None:
    """Return the newest hash-verified JSON capture for one exact API path."""
    matches = []
    for metadata_path in capture_files("*.capture.json"):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if urlparse(metadata.get("requested_url", "")).path == path:
            matches.append((metadata.get("retrieved_at", ""), metadata_path, metadata))
    if not matches:
        return None
    _, _, metadata = max(matches)
    payload_path = ROOT / metadata["payload_path"]
    body = payload_path.read_bytes()
    if hashlib.sha256(body).hexdigest() != metadata["sha256"]:
        raise SystemExit(f"public API capture hash mismatch: {metadata['payload_path']}")
    if metadata.get("status_code") != 200:
        return None
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"public API capture is not JSON: {metadata['payload_path']}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"public API capture is not an object: {metadata['payload_path']}")
    return metadata, payload


def public_linkage(pr_number: int, merge_sha: str | None) -> dict:
    detail = verified_api_capture(f"/repos/anthropics/claude-for-legal/pulls/{pr_number}")
    if detail is None:
        return {"status": "unknown", "detail": None, "commit": None, "files": None}
    detail_meta, detail_payload = detail
    if detail_payload.get("number") != pr_number:
        raise SystemExit(f"PR detail number mismatch for PR {pr_number}")
    detail_evidence = {"observed_at": detail_meta["retrieved_at"], "sha256": detail_meta["sha256"], "custody_id": custody_id(detail_meta)}
    detail_merge_sha = detail_payload.get("merge_commit_sha")
    if not detail_payload.get("merged_at"):
        files = verified_file_capture(pr_number, detail_payload.get("changed_files"))
        if files is None:
            return {
                "status": "captured_incomplete_unknown",
                "reason": "open or unmerged detail snapshot lacks complete PR-file pagination",
                "detail": detail_evidence,
                "commit": None,
                "files": None,
            }
        return {
            "status": "captured_open_or_unmerged_snapshot",
            "reason": "detail snapshot does not report a merged event",
            "detail": detail_evidence,
            "commit": None,
            "files": files,
        }
    if not merge_sha or detail_merge_sha != merge_sha:
        return {"status": "captured_conflicting_snapshot_unknown", "reason": "PR index and detail do not establish the same merged-commit linkage", "detail": detail_evidence, "commit": None, "files": None}
    commit = verified_api_capture(f"/repos/anthropics/claude-for-legal/commits/{merge_sha}")
    if commit is None:
        return {"status": "captured_incomplete_unknown", "reason": "matching public commit capture is unavailable", "detail": detail_evidence, "commit": None, "files": verified_file_capture(pr_number, detail_payload.get("changed_files"))}
    commit_meta, commit_payload = commit
    if commit_payload.get("sha") != merge_sha:
        raise SystemExit(f"public commit SHA mismatch for PR {pr_number}")
    files = verified_file_capture(pr_number, detail_payload.get("changed_files"))
    commit_evidence = {"observed_at": commit_meta["retrieved_at"], "sha256": commit_meta["sha256"], "custody_id": custody_id(commit_meta)}
    if files is None:
        return {"status": "captured_incomplete_unknown", "reason": "complete PR-file pagination is unavailable", "detail": detail_evidence, "commit": commit_evidence, "files": None}
    return {"status": "linked_verified_capture", "reason": "detail, merged commit, and terminally verified file pages agree", "detail": detail_evidence, "commit": commit_evidence, "files": files}


def verified_file_capture(pr_number: int, expected_count: int | None) -> dict | None:
    candidates = []
    for manifest_path in capture_files("*.capture-set.json"):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("capture_kind") == f"pull-{pr_number}-files":
            candidates.append((manifest.get("created_at", manifest.get("captured_at", "")), manifest))
    if not candidates:
        return None
    _, manifest = max(candidates)
    if manifest.get("schema") == "claude-legal-audit.github-public-history-capture-set.v2" and (
        manifest.get("completion_state") != "complete" or manifest.get("terminal_page_verified") is not True
    ):
        return None
    pages = manifest.get("pages", [])
    if manifest.get("pagination_expected") is not True or manifest.get("page_count") != len(pages) or [page.get("page") for page in pages] != list(range(1, len(pages) + 1)):
        raise SystemExit(f"PR file capture pagination receipt invalid for PR {pr_number}")
    files, hashes, observations, custody_ids = [], [], [], []
    for index, page in enumerate(pages):
        metadata_path = ROOT / page["metadata_path"]
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        body = (ROOT / metadata["payload_path"]).read_bytes()
        endpoint = f"/pulls/{pr_number}/files"
        if (canonical_endpoint_path(metadata.get("requested_url", "")) != endpoint or canonical_endpoint_path(metadata.get("final_url", "")) != endpoint or page.get("sha256") != metadata.get("sha256") or metadata.get("status_code") != 200 or hashlib.sha256(body).hexdigest() != metadata.get("sha256")):
            raise SystemExit(f"PR file capture hash or status invalid for PR {pr_number}")
        link = metadata.get("response_headers", {}).get("link", "")
        try:
            actual_next = verified_next_url(metadata["requested_url"], link)
        except RuntimeError as exc:
            raise SystemExit(f"PR file capture pagination link invalid for PR {pr_number}: {exc}") from exc
        expected_next = pages[index + 1].get("requested_url") if index + 1 < len(pages) else None
        if actual_next != expected_next:
            position = "intermediate" if expected_next else "final"
            raise SystemExit(f"PR file capture {position} pagination proof invalid for PR {pr_number}")
        if page.get("next_url") not in {None, actual_next}:
            raise SystemExit(f"PR file capture page receipt next link mismatch for PR {pr_number}")
        payload = json.loads(body)
        if not isinstance(payload, list):
            raise SystemExit(f"PR file capture is not a list for PR {pr_number}")
        files.extend(payload)
        hashes.append(metadata["sha256"])
        observations.append(metadata["retrieved_at"])
        custody_ids.append(custody_id(metadata))
    if not isinstance(expected_count, int) or expected_count < 0:
        raise SystemExit(f"PR detail changed_files is invalid for PR {pr_number}")
    if len(files) != expected_count:
        # GitHub's /pulls/{n}/files listing can terminate before detail.changed_files
        # (observed public ceiling near 3000). Preserve as incomplete/unknown rather
        # than treating a terminal page as a complete inventory or aborting rebuild.
        return None
    return {"status": "captured_complete", "page_count": len(pages), "file_count": len(files), "page_sha256": hashes, "observed_at": observations, "custody_ids": custody_ids}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    metadata, pulls = find_pull_capture()
    local_commits = set(git("rev-list", "--all").stdout.splitlines())
    records = []
    for pr in sorted(pulls, key=lambda row: row["number"]):
        merge_sha = pr.get("merge_commit_sha")
        base_sha, head_sha = pr["base"]["sha"], pr["head"]["sha"]
        merge_available = merge_sha in local_commits
        base_available, head_available = base_sha in local_commits, head_sha in local_commits
        diff = None
        if merge_available and base_available:
            stats = git("diff-tree", "--no-commit-id", "--numstat", "-r", base_sha, merge_sha).stdout.splitlines()
            additions = sum(int(row.split("\t", 1)[0]) for row in stats if row.split("\t", 1)[0].isdigit())
            deletions = sum(int(row.split("\t", 2)[1]) for row in stats if len(row.split("\t", 2)) > 1 and row.split("\t", 2)[1].isdigit())
            diff = {"comparison": "base_to_merge_commit", "files_changed": len(stats), "additions": additions, "deletions": deletions}
        records.append({
            "pr_number": pr["number"], "html_url": pr["html_url"], "state": pr["state"], "title": pr["title"],
            "event_time": {"created_at": pr["created_at"], "updated_at": pr["updated_at"], "merged_at": pr["merged_at"], "closed_at": pr["closed_at"]},
            "base_sha": base_sha, "head_sha": head_sha, "merge_commit_sha": merge_sha,
            "local_availability": {"base_commit": base_available, "head_commit": head_available, "merge_commit": merge_available},
            "public_capture_linkage": public_linkage(pr["number"], merge_sha),
            "diff_summary": diff,
            "limitation": "Identifiers and diff statistics describe the captured public PR record and locally available Git objects only. They do not establish reviewer intent, product strategy, runtime behavior, or complete remote history."
        })
    linked_count = sum(record["public_capture_linkage"]["status"] == "linked_verified_capture" for record in records)
    open_snapshot_count = sum(record["public_capture_linkage"]["status"] == "captured_open_or_unmerged_snapshot" for record in records)
    unknown_count = len(records) - linked_count - open_snapshot_count
    output = {
        "schema": "claude-legal-audit.pr-commit-diff-linkage.v2",
        "capture": {
            "url": metadata["requested_url"],
            "observed_at": metadata["retrieved_at"],
            "sha256": metadata["sha256"],
            "custody_id": custody_id(metadata),
            "item_count": len(pulls),
            "pagination_terminal_observation": not bool(metadata.get("response_headers", {}).get("link")),
        },
        "records": records,
        "summary": {
            "pr_count": len(records),
            "local_merge_commit_count": sum(record["local_availability"]["merge_commit"] for record in records),
            "diff_available_count": sum(record["diff_summary"] is not None for record in records),
            "publicly_linked_capture_count": linked_count,
            "captured_open_or_unmerged_snapshot_count": open_snapshot_count,
            "public_linkage_unknown_count": unknown_count,
            "coverage_statement": f"{linked_count} of {len(records)} captured public PR index records have hash-verified detail, merged-commit, and terminal file-page linkage; {open_snapshot_count} have bounded open/unmerged detail and file snapshots; {unknown_count} remain unknown or incomplete.",
        },
        "limitation": "This normalized public artifact contains hashes, timestamps, source URLs, and opaque custody IDs only. Raw API payloads remain in ignored private custody.",
    }
    violations = public_content_violations(output)
    if violations:
        raise SystemExit("refused private path or raw-custody field in public PR linkage: " + "; ".join(violations))
    data = canonical(output)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != data:
            print("ERROR: PR linkage is stale; run scripts/build_pr_linkage.py", file=sys.stderr)
            return 1
        print(f"PR linkage current: {len(records)} PRs, {output['summary']['diff_available_count']} local diffs")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(data)
    print(f"wrote {OUTPUT.relative_to(ROOT)}: {len(records)} PRs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
