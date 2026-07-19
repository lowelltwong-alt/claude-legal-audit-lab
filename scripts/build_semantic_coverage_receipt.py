#!/usr/bin/env python3
"""Build a deterministic per-file receipt from assigned semantic-review worklists.

The receipt is intentionally a coverage and integrity record.  It proves which
immutable file version was attested as reviewed; it does not turn static review
into evidence of runtime behavior or external data handling.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default="results/inventory.json")
    parser.add_argument("--worklists", default="results/worklists")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--coverage", default="results/coverage.csv")
    parser.add_argument("--receipt", default="results/semantic-coverage-receipt.jsonl")
    args = parser.parse_args()

    inventory = json.loads(Path(args.inventory).read_text(encoding="utf-8"))["files"]
    expected = {row["path"]: row for row in inventory if row.get("text")}
    attestations = json.loads(Path(args.attestations).read_text(encoding="utf-8"))
    assignments: dict[str, dict[str, object]] = {}
    for attestation in attestations["attestations"]:
        for worker in attestation["workers"]:
            rows = read_csv(Path(args.worklists) / f"worker-{worker}.csv")
            for row in rows:
                path = row["path"]
                if path in assignments:
                    raise SystemExit(f"duplicate worklist assignment: {path}")
                source = expected.get(path)
                if source is None:
                    raise SystemExit(f"worklist path not in text inventory: {path}")
                if row["sha256"] != source["sha256"] or int(row["lines"]) != source["lines"]:
                    raise SystemExit(f"worklist integrity mismatch: {path}")
                assignments[path] = attestation
    if set(assignments) != set(expected):
        missing = sorted(set(expected) - set(assignments))
        extra = sorted(set(assignments) - set(expected))
        raise SystemExit(f"assignment coverage mismatch; missing={missing[:3]} extra={extra[:3]}")

    receipt_path = Path(args.receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    with receipt_path.open("w", encoding="utf-8", newline="\n") as handle:
        for path in sorted(expected):
            source, attestation = expected[path], assignments[path]
            record = {
                "path": path,
                "sha256": source["sha256"],
                "lines_reviewed": source["lines"],
                "status": attestation["status"],
                "reviewer": attestation["reviewer"],
                "review_timestamp": attestation["review_timestamp"],
                "deferred_reason": None,
                "finding_refs": attestation["finding_refs"],
                "scope_limit": attestation["scope_limit"],
            }
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    coverage_path = Path(args.coverage)
    coverage = read_csv(coverage_path)
    fields = list(coverage[0]) if coverage else []
    for row in coverage:
        if row["path"] in assignments:
            attestation = assignments[row["path"]]
            row["status"] = str(attestation["status"])
            row["reviewer"] = str(attestation["reviewer"])
            row["notes"] = "receipt=" + receipt_path.as_posix()
    with coverage_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(coverage)

    print(f"wrote {receipt_path}: {len(expected)} reviewed text files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
