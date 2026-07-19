#!/usr/bin/env python3
"""Capture an authorized public source to the ignored local raw-research store.

The capture is evidence custody, not publication, legal advice, or proof that a
provider's statements describe any customer's actual deployment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "private" / "raw" / "sources"
PRIVATE_CUSTODY_ROOT = DEFAULT_ROOT
MAX_BYTES = 20 * 1024 * 1024
ALLOWED_TYPES = ("text/", "application/pdf", "application/json")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_id")
    parser.add_argument("url")
    parser.add_argument("--out-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    if not re.fullmatch(r"SRC-[0-9]{4}", args.source_id):
        raise SystemExit("source_id must use the registered SRC-0000 form")
    args.out_root = args.out_root.resolve()
    if not args.out_root.is_relative_to(PRIVATE_CUSTODY_ROOT.resolve()):
        raise SystemExit("--out-root must remain within ignored private/raw/sources custody")
    if not args.url.startswith("https://"):
        raise SystemExit("only HTTPS public URLs are permitted")
    retrieved_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    request = Request(args.url, headers={"User-Agent": "claude-legal-audit-lab/1.0 public-source-capture"})
    try:
        with urlopen(request, timeout=args.timeout) as response:
            content_type = response.headers.get_content_type()
            if not any(content_type.startswith(prefix) for prefix in ALLOWED_TYPES):
                raise SystemExit(f"refused unexpected content type: {content_type}")
            declared_length = response.headers.get("Content-Length")
            if declared_length and int(declared_length) > MAX_BYTES:
                raise SystemExit("refused response larger than 20 MiB")
            body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                raise SystemExit("refused response larger than 20 MiB")
            final_url = response.geturl()
            headers = {key.lower(): value for key, value in response.headers.items() if key.lower() in {"content-type", "content-length", "etag", "last-modified", "date", "link"}}
            status_code = response.status
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f"ERROR: capture failed: {exc}", file=sys.stderr)
        return 1
    suffix = mimetypes.guess_extension(content_type) or ".bin"
    capture_dir = args.out_root / args.source_id
    capture_dir.mkdir(parents=True, exist_ok=True)
    stamp = retrieved_at.replace(":", "").replace("-", "")
    payload_path = capture_dir / f"{stamp}{suffix}"
    metadata_path = capture_dir / f"{stamp}.capture.json"
    try:
        with payload_path.open("xb") as handle:
            handle.write(body)
    except FileExistsError as exc:
        raise SystemExit("refused capture-path collision; retry after the clock advances") from exc
    metadata = {"schema": "claude-legal-audit.public-source-capture.v1", "source_id": args.source_id, "requested_url": args.url, "final_url": final_url, "retrieved_at": retrieved_at, "status_code": status_code, "content_type": content_type, "byte_count": len(body), "sha256": hashlib.sha256(body).hexdigest(), "response_headers": headers, "payload_path": payload_path.relative_to(ROOT).as_posix(), "classification": "private_raw_public_source", "limitation": "A byte capture proves the retrieved response only; it does not prove a customer deployment, product behavior, training use, retention, provider access, or intent."}
    try:
        with metadata_path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    except FileExistsError as exc:
        raise SystemExit("refused metadata-path collision; retry after the clock advances") from exc
    print(json.dumps({key: metadata[key] for key in ("source_id", "final_url", "retrieved_at", "content_type", "byte_count", "sha256", "payload_path")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
