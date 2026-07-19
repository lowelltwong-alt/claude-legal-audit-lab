#!/usr/bin/env python3
"""Capture bounded public GitHub PR evidence with pagination receipts.

The tool uses no credentials and writes only to the ignored local raw-research
workspace. Captures are observations of public endpoint responses, not proof of
complete history, intent, strategy, merge semantics, or runtime behavior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "private" / "raw" / "sources" / "SRC-0013" / "github-pr-history"
PRIVATE_CUSTODY_ROOT = ROOT / "private" / "raw" / "sources" / "SRC-0013"
API_ROOT = "https://api.github.com/repos/anthropics/claude-for-legal"
NUMERIC_REPOSITORY_ROOT = "https://api.github.com/repositories/1217153065"
MAX_BYTES = 20 * 1024 * 1024
MAX_PAGES = 100
API_SUFFIX = re.compile(r"^/(?:pulls(?:/[1-9][0-9]*(?:/files)?)?|commits/[0-9a-f]{40})$")
LINK_ITEM = re.compile(r'^\s*<([^>]+)>\s*;\s*rel="([^"]+)"\s*$')
RATE_HEADER_NAMES = {
    "date",
    "content-type",
    "content-length",
    "etag",
    "last-modified",
    "link",
    "retry-after",
    "x-github-api-version",
    "x-github-request-id",
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
    "x-ratelimit-resource",
    "x-ratelimit-used",
}
DEFAULT_RESERVE = 15
DEFAULT_COHORT_SIZE = 5


@dataclass
class RequestBudget:
    reserve_remaining: int = DEFAULT_RESERVE
    requests_made: int = 0
    first_observed_remaining: int | None = None
    last_observed_remaining: int | None = None

    def observe(self, headers: dict[str, str]) -> None:
        self.requests_made += 1
        raw = headers.get("x-ratelimit-remaining")
        if raw is None:
            return
        try:
            remaining = int(raw)
        except ValueError as exc:
            raise RuntimeError("GitHub returned a non-integer rate-limit remainder") from exc
        if remaining < 0:
            raise RuntimeError("GitHub returned a negative rate-limit remainder")
        if self.first_observed_remaining is None:
            self.first_observed_remaining = remaining
        self.last_observed_remaining = remaining

    def permits_another_request(self) -> bool:
        return self.last_observed_remaining is None or self.last_observed_remaining > self.reserve_remaining

    def receipt(self) -> dict[str, int | None]:
        return {
            "reserve_remaining": self.reserve_remaining,
            "requests_made": self.requests_made,
            "first_observed_remaining": self.first_observed_remaining,
            "last_observed_remaining": self.last_observed_remaining,
        }


class NoRedirect(HTTPRedirectHandler):
    """Make a redirect an observable failure instead of following it."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def endpoint(args: argparse.Namespace) -> tuple[str, bool, str]:
    if args.command == "index":
        return f"{API_ROOT}/pulls?" + urlencode({"state": "all", "per_page": 100}), True, "pull-index"
    if args.command == "detail":
        return f"{API_ROOT}/pulls/{args.number}", False, f"pull-{args.number}-detail"
    if args.command == "files":
        return f"{API_ROOT}/pulls/{args.number}/files?" + urlencode({"per_page": 100}), True, f"pull-{args.number}-files"
    if args.command == "commit":
        if not re.fullmatch(r"[0-9a-f]{40}", args.sha):
            raise SystemExit("commit SHA must be a full lowercase 40-hex object ID")
        return f"{API_ROOT}/commits/{args.sha}", False, f"commit-{args.sha}"
    raise AssertionError(args.command)


def canonical_endpoint_path(url: str) -> str | None:
    parsed = urlparse(url)
    for prefix in ("/repos/anthropics/claude-for-legal", "/repositories/1217153065"):
        if parsed.path.startswith(prefix):
            suffix = parsed.path[len(prefix):]
            return suffix if API_SUFFIX.fullmatch(suffix) else None
    return None


def allowed_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.netloc == "api.github.com" and canonical_endpoint_path(url) is not None


def custody_path(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(PRIVATE_CUSTODY_ROOT.resolve()):
        raise SystemExit("--out must remain within the ignored SRC-0013 private custody root")
    return resolved


def canonical(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def page_chain_projection(pages: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "page": page.get("page"),
            "requested_url": page.get("requested_url"),
            "final_url": page.get("final_url"),
            "next_url": page.get("next_url"),
            "status_code": page.get("status_code"),
            "sha256": page.get("sha256"),
            "metadata_sha256": page.get("metadata_sha256"),
            "etag": page.get("etag"),
        }
        for page in pages
    ]


def page_chain_sha256(pages: list[dict[str, object]]) -> str:
    return sha256(canonical(page_chain_projection(pages)))


def selected_headers(headers: object) -> dict[str, str]:
    return {
        key.lower(): value
        for key, value in headers.items()  # type: ignore[attr-defined]
        if key.lower() in RATE_HEADER_NAMES
    }


def parse_link_header(link: str) -> dict[str, str]:
    """Parse GitHub's structural Link header and reject ambiguity."""
    if not link.strip():
        return {}
    relations: dict[str, str] = {}
    for raw_item in link.split(","):
        match = LINK_ITEM.fullmatch(raw_item)
        if match is None:
            raise RuntimeError(f"malformed GitHub Link item: {raw_item!r}")
        url, relation_text = match.groups()
        for relation in relation_text.split():
            if relation in relations:
                raise RuntimeError(f"duplicate GitHub Link relation: {relation}")
            relations[relation] = url
    return relations


def page_number(url: str) -> int:
    values = parse_qs(urlparse(url).query).get("page", ["1"])
    if len(values) != 1 or not values[0].isdigit() or int(values[0]) < 1:
        raise RuntimeError("pagination URL has an invalid page number")
    return int(values[0])


def verified_next_url(current: str, link: str) -> str | None:
    relations = parse_link_header(link)
    next_url = relations.get("next")
    if next_url is None:
        return None
    if not allowed_url(next_url):
        raise RuntimeError("refused pagination link outside target repository API")
    current_parsed = urlparse(current)
    next_parsed = urlparse(next_url)
    if canonical_endpoint_path(current) != canonical_endpoint_path(next_url):
        raise RuntimeError("pagination next link changed endpoint path")
    query = parse_qs(next_parsed.query)
    if query.get("per_page") != ["100"]:
        raise RuntimeError("pagination next link must preserve per_page=100")
    if page_number(next_url) != page_number(current) + 1:
        raise RuntimeError("pagination next link is not the immediate next page")
    return next_url


def write_exclusive(path: Path, payload: bytes) -> None:
    """Atomically refuse a collision, including concurrent same-second runs."""
    try:
        with path.open("xb") as handle:
            handle.write(payload)
    except FileExistsError as exc:
        raise SystemExit("refused capture-path collision; retry after the clock advances") from exc


def fetch(url: str, etag: str | None = None) -> tuple[int, bytes, dict[str, str], str]:
    request_headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "claude-legal-audit-lab/1.0 public-history-capture",
    }
    if etag:
        request_headers["If-None-Match"] = etag
    request = Request(url, headers=request_headers)
    try:
        with build_opener(NoRedirect()).open(request, timeout=30) as response:
            body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                raise RuntimeError("response exceeds 20 MiB limit")
            headers = selected_headers(response.headers)
            if not allowed_url(response.geturl()):
                raise RuntimeError("refused redirect or final URL outside target repository API")
            return response.status, body, headers, response.geturl()
    except HTTPError as exc:
        body = exc.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise RuntimeError("error response exceeds 20 MiB limit") from exc
        headers = selected_headers(exc.headers)
        if exc.code == 304:
            if not allowed_url(exc.geturl()):
                raise RuntimeError("refused not-modified response outside target repository API") from exc
            return exc.code, body, headers, exc.geturl()
        if 300 <= exc.code < 400:
            raise RuntimeError("refused redirect response") from exc
        if not allowed_url(exc.geturl()):
            raise RuntimeError("refused error response outside target repository API") from exc
        return exc.code, body, headers, exc.geturl()
    except URLError as exc:
        raise RuntimeError(f"network failure: {exc}") from exc


def checkpoint_write(path: Path, payload: dict) -> None:
    path = custody_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical(payload))
    temporary.replace(path)


def checkpoint_load(path: Path, label: str, initial_url: str, paginated: bool) -> dict:
    path = custody_path(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot resume malformed capture checkpoint: {exc}") from exc
    if (
        not isinstance(payload, dict)
        or payload.get("schema") != "claude-legal-audit.github-capture-checkpoint.v2"
        or payload.get("capture_kind") != label
    ):
        raise SystemExit("capture checkpoint does not match the requested capture kind or v2 contract")
    if payload.get("initial_url") != initial_url or payload.get("initial_url_sha256") != sha256(initial_url.encode("utf-8")):
        raise SystemExit("capture checkpoint initial URL binding mismatch")
    if payload.get("pagination_expected") is not paginated:
        raise SystemExit("capture checkpoint pagination contract mismatch")
    pages = payload.get("pages")
    next_url = payload.get("next_url")
    if not isinstance(pages, list) or not isinstance(next_url, (str, type(None))):
        raise SystemExit("capture checkpoint has invalid pages or next URL")
    if len(pages) > MAX_PAGES:
        raise SystemExit("capture checkpoint exceeds the page limit")
    expected_url: str | None = initial_url
    for index, page in enumerate(pages, start=1):
        if not isinstance(page, dict) or page.get("page") != index:
            raise SystemExit("capture checkpoint page numbering is not consecutive")
        requested_url = page.get("requested_url")
        final_url = page.get("final_url")
        saved_next = page.get("next_url")
        if requested_url != expected_url:
            raise SystemExit("capture checkpoint page chain is discontinuous")
        if not isinstance(requested_url, str) or not allowed_url(requested_url):
            raise SystemExit("capture checkpoint contains an out-of-scope requested URL")
        if not isinstance(final_url, str) or not allowed_url(final_url):
            raise SystemExit("capture checkpoint contains an out-of-scope final URL")
        if saved_next is not None and (not isinstance(saved_next, str) or not allowed_url(saved_next)):
            raise SystemExit("capture checkpoint contains an out-of-scope next URL")
        if saved_next is not None and (not paginated or verified_next_url(requested_url, f'<{saved_next}>; rel="next"') != saved_next):
            raise SystemExit("capture checkpoint next URL is not structurally immediate")
        metadata_path_value = page.get("metadata_path")
        if not isinstance(metadata_path_value, str):
            raise SystemExit("capture checkpoint page lacks metadata custody")
        metadata_path = custody_path(ROOT / metadata_path_value)
        try:
            metadata_bytes = metadata_path.read_bytes()
            metadata = json.loads(metadata_bytes)
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"capture checkpoint metadata custody is unreadable: {exc}") from exc
        if page.get("metadata_sha256") != sha256(metadata_bytes):
            raise SystemExit("capture checkpoint metadata hash mismatch")
        if any(
            metadata.get(key) != page.get(key)
            for key in ("requested_url", "final_url", "status_code", "sha256", "next_url", "etag")
        ):
            raise SystemExit("capture checkpoint page disagrees with metadata custody")
        payload_path_value = metadata.get("payload_path")
        if not isinstance(payload_path_value, str):
            raise SystemExit("capture checkpoint metadata lacks payload custody")
        payload_path = custody_path(ROOT / payload_path_value)
        try:
            body = payload_path.read_bytes()
        except OSError as exc:
            raise SystemExit(f"capture checkpoint payload custody is unreadable: {exc}") from exc
        if page.get("sha256") != sha256(body) or metadata.get("byte_count") != len(body):
            raise SystemExit("capture checkpoint payload hash or byte count mismatch")
        expected_link = metadata.get("response_headers", {}).get("link", "")
        structurally_observed = verified_next_url(requested_url, expected_link) if paginated and 200 <= int(page.get("status_code", 0)) < 300 else None
        if structurally_observed != saved_next:
            raise SystemExit("capture checkpoint next URL disagrees with captured Link header")
        expected_url = saved_next
    expected_next = initial_url if not pages else pages[-1].get("next_url")
    if next_url != expected_next:
        raise SystemExit("capture checkpoint pending next URL mismatch")
    if payload.get("page_chain_sha256") != page_chain_sha256(pages):
        raise SystemExit("capture checkpoint page-chain hash mismatch")
    terminal = bool(pages) and pages[-1].get("status_code") in range(200, 300) and pages[-1].get("next_url") is None
    if payload.get("terminal_page_verified") is not (terminal or not paginated):
        raise SystemExit("capture checkpoint terminal-page state mismatch")
    return payload


def checkpoint_payload(
    *,
    label: str,
    initial_url: str,
    paginated: bool,
    pages: list[dict[str, object]],
    next_url: str | None,
    completion_state: str,
    terminal_page_verified: bool,
    budget: RequestBudget,
) -> dict:
    return {
        "schema": "claude-legal-audit.github-capture-checkpoint.v2",
        "capture_kind": label,
        "initial_url": initial_url,
        "initial_url_sha256": sha256(initial_url.encode("utf-8")),
        "pagination_expected": paginated,
        "next_url": next_url,
        "pages": pages,
        "page_chain_sha256": page_chain_sha256(pages),
        "terminal_page_verified": terminal_page_verified,
        "completion_state": completion_state,
        "updated_at": stamp(),
        "request_budget": budget.receipt(),
    }


def capture_set(
    initial_url: str,
    paginated: bool,
    label: str,
    out: Path,
    budget: RequestBudget,
    *,
    checkpoint: Path | None = None,
    resume: bool = False,
) -> tuple[dict, Path]:
    if not allowed_url(initial_url):
        raise SystemExit("refused non-repository API URL")
    out = custody_path(out)
    out.mkdir(parents=True, exist_ok=True)
    pages: list[dict[str, object]] = []
    current = initial_url
    terminal_page_verified = not paginated
    if checkpoint is not None and resume and checkpoint.exists():
        state = checkpoint_load(checkpoint, label, initial_url, paginated)
        pages = state.get("pages", [])
        current = state.get("next_url") or ""
        terminal_page_verified = state["terminal_page_verified"]
        if not isinstance(pages, list) or not isinstance(current, str):
            raise SystemExit("capture checkpoint has invalid pages or next URL")
        if current and not allowed_url(current):
            raise SystemExit("capture checkpoint contains an out-of-scope URL")

    attempt_at = stamp()
    completion_state = "complete"
    if pages and current:
        if not budget.permits_another_request():
            completion_state = "interrupted_rate_budget"
        else:
            last_page = pages[-1]
            last_etag = last_page.get("etag")
            if not isinstance(last_etag, str) or not last_etag:
                raise SystemExit("cannot resume without a URL-scoped ETag for the last captured page")
            status, body, headers, final_url = fetch(str(last_page["requested_url"]), last_etag)
            budget.observe(headers)
            if status == 304:
                if body or final_url != last_page.get("final_url"):
                    raise SystemExit("not-modified revalidation returned a body or changed the final URL")
            elif status == 200:
                observed_next = verified_next_url(str(last_page["requested_url"]), headers.get("link", "")) if paginated else None
                if sha256(body) != last_page.get("sha256") or observed_next != last_page.get("next_url") or final_url != last_page.get("final_url"):
                    raise SystemExit("resume revalidation changed the prior page body, final URL, or next-link chain")
            else:
                raise SystemExit("resume revalidation did not return 200 or 304; capture remains unknown")
            if not budget.permits_another_request():
                completion_state = "interrupted_rate_budget"
    while current:
        if len(pages) >= MAX_PAGES:
            raise SystemExit("refused pagination beyond 100 pages")
        if not budget.permits_another_request():
            completion_state = "interrupted_rate_budget"
            break
        observed_at = stamp()
        status, body, headers, final_url = fetch(current, None)
        budget.observe(headers)
        number = len(pages) + 1
        next_url = (
            verified_next_url(current, headers.get("link", ""))
            if paginated and 200 <= status < 300
            else None
        )
        suffix = ".json" if headers.get("content-type", "").startswith("application/json") else ".bin"
        prefix = f"{observed_at.replace(':', '').replace('-', '')}-{label}-page-{number:03d}"
        payload_path = out / f"{prefix}{suffix}"
        metadata_path = out / f"{prefix}.capture.json"
        write_exclusive(payload_path, body)
        metadata = {
            "schema": "claude-legal-audit.github-public-history-capture.v2",
            "classification": "private_raw_public_source",
            "requested_url": current,
            "final_url": final_url,
            "retrieved_at": observed_at,
            "status_code": status,
            "response_headers": headers,
            "etag": headers.get("etag"),
            "retry_after": headers.get("retry-after"),
            "rate_limit": {
                "limit": headers.get("x-ratelimit-limit"),
                "remaining": headers.get("x-ratelimit-remaining"),
                "reset": headers.get("x-ratelimit-reset"),
                "resource": headers.get("x-ratelimit-resource"),
                "used": headers.get("x-ratelimit-used"),
            },
            "next_url": next_url,
            "byte_count": len(body),
            "sha256": sha256(body),
            "payload_path": payload_path.relative_to(ROOT).as_posix(),
            "limitation": "This byte capture proves only the retrieved public endpoint response; it does not prove complete, deleted, private, permission-dependent, later-changed history, strategy, intent, merge semantics, or runtime behavior.",
        }
        metadata_bytes = canonical(metadata)
        write_exclusive(metadata_path, metadata_bytes)
        pages.append(
            {
                "page": number,
                "metadata_path": metadata_path.relative_to(ROOT).as_posix(),
                "status_code": status,
                "sha256": metadata["sha256"],
                "metadata_sha256": sha256(metadata_bytes),
                "etag": metadata["etag"],
                "requested_url": current,
                "final_url": final_url,
                "next_url": next_url,
            }
        )
        if not 200 <= status < 300:
            completion_state = "http_error_unknown"
            current = ""
        elif next_url is None:
            terminal_page_verified = True
            current = ""
        else:
            current = next_url
            if not budget.permits_another_request():
                completion_state = "interrupted_rate_budget"
        if checkpoint is not None:
            checkpoint_write(
                checkpoint,
                checkpoint_payload(
                    label=label,
                    initial_url=initial_url,
                    paginated=paginated,
                    pages=pages,
                    next_url=current or None,
                    completion_state=completion_state,
                    terminal_page_verified=terminal_page_verified,
                    budget=budget,
                ),
            )

    if checkpoint is not None:
        checkpoint_write(
            checkpoint,
            checkpoint_payload(
                label=label,
                initial_url=initial_url,
                paginated=paginated,
                pages=pages,
                next_url=current or None,
                completion_state=completion_state,
                terminal_page_verified=terminal_page_verified,
                budget=budget,
            ),
        )
    manifest = {
        "schema": "claude-legal-audit.github-public-history-capture-set.v2",
        "created_at": attempt_at,
        "capture_kind": label,
        "pagination_expected": paginated,
        "completion_state": completion_state,
        "terminal_page_verified": terminal_page_verified,
        "page_count": len(pages),
        "page_chain_sha256": page_chain_sha256(pages),
        "request_budget": budget.receipt(),
        "pages": pages,
        "limitation": "A structurally verified terminal page establishes only the observed public pagination boundary. Interrupted and inaccessible captures remain unknown, never no-change evidence.",
    }
    manifest_path = out / f"{attempt_at.replace(':', '').replace('-', '')}-{label}.capture-set.json"
    write_exclusive(manifest_path, canonical(manifest))
    return manifest, manifest_path


def capture_payload(manifest: dict) -> object | None:
    pages = manifest.get("pages", [])
    if len(pages) != 1 or pages[0].get("status_code") != 200:
        return None
    metadata = json.loads((ROOT / pages[0]["metadata_path"]).read_text(encoding="utf-8"))
    body = (ROOT / metadata["payload_path"]).read_bytes()
    if hashlib.sha256(body).hexdigest() != metadata.get("sha256"):
        raise SystemExit("newly captured payload failed its custody hash")
    return json.loads(body)


def default_unknown_prs() -> tuple[list[int], str]:
    linkage = ROOT / "results" / "pr-commit-diff-linkage.json"
    try:
        raw = linkage.read_bytes()
        payload = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot select a cohort without current PR linkage: {exc}") from exc
    numbers = [
        record["pr_number"]
        for record in payload.get("records", [])
        if record.get("public_capture_linkage", {}).get("status")
        in {"unknown", "captured_incomplete_unknown", "captured_conflicting_snapshot_unknown"}
    ]
    return sorted(numbers), hashlib.sha256(raw).hexdigest()


def run_cohort(args: argparse.Namespace, out: Path) -> tuple[dict, Path]:
    if args.limit < 1 or args.limit > DEFAULT_COHORT_SIZE:
        raise SystemExit("cohort --limit must be between 1 and 5")
    if args.numbers:
        selected = sorted(set(args.numbers))
        linkage_hash = None
    else:
        selected, linkage_hash = default_unknown_prs()
    selected = selected[: args.limit]
    if not selected:
        raise SystemExit("no incomplete PRs are available for this cohort")
    checkpoint = custody_path(args.checkpoint or (out / "cohort.checkpoint.json"))
    previous: dict = {}
    if args.resume and checkpoint.exists():
        try:
            previous = json.loads(checkpoint.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"cannot resume malformed cohort checkpoint: {exc}") from exc
        if previous.get("schema") != "claude-legal-audit.github-pr-cohort-checkpoint.v1":
            raise SystemExit("cohort checkpoint schema mismatch")
        if previous.get("selected_prs") != selected or previous.get("input_linkage_sha256") != linkage_hash:
            raise SystemExit("cohort checkpoint is not bound to the current selection input")
    records = previous.get("records", []) if previous else []
    completed_numbers = {record.get("pr_number") for record in records}
    budget = RequestBudget(reserve_remaining=args.reserve)
    for pr_number in selected:
        if pr_number in completed_numbers:
            continue
        if not budget.permits_another_request():
            break
        record: dict[str, object] = {"pr_number": pr_number, "capture_sets": [], "status": "unknown_incomplete"}
        detail_url = f"{API_ROOT}/pulls/{pr_number}"
        detail_manifest, detail_path = capture_set(detail_url, False, f"pull-{pr_number}-detail", out, budget)
        record["capture_sets"].append({"kind": "detail", "manifest_path": detail_path.relative_to(ROOT).as_posix(), "manifest_sha256": hashlib.sha256(canonical(detail_manifest)).hexdigest()})
        detail = capture_payload(detail_manifest)
        if isinstance(detail, dict) and detail.get("number") == pr_number and budget.permits_another_request():
            files_url = f"{API_ROOT}/pulls/{pr_number}/files?" + urlencode({"per_page": 100})
            files_manifest, files_path = capture_set(files_url, True, f"pull-{pr_number}-files", out, budget)
            record["capture_sets"].append({"kind": "files", "manifest_path": files_path.relative_to(ROOT).as_posix(), "manifest_sha256": hashlib.sha256(canonical(files_manifest)).hexdigest()})
            merge_sha = detail.get("merge_commit_sha")
            merged_at = detail.get("merged_at")
            if merged_at and isinstance(merge_sha, str) and re.fullmatch(r"[0-9a-f]{40}", merge_sha) and budget.permits_another_request():
                commit_manifest, commit_path = capture_set(f"{API_ROOT}/commits/{merge_sha}", False, f"commit-{merge_sha}", out, budget)
                record["capture_sets"].append({"kind": "commit", "manifest_path": commit_path.relative_to(ROOT).as_posix(), "manifest_sha256": hashlib.sha256(canonical(commit_manifest)).hexdigest()})
                record["status"] = "captured_candidate_merged_linkage"
            elif merged_at:
                record["status"] = "unknown_missing_commit_capture"
            else:
                record["status"] = "captured_open_or_unmerged_snapshot"
        records.append(record)
        checkpoint_write(
            checkpoint,
            {
                "schema": "claude-legal-audit.github-pr-cohort-checkpoint.v1",
                "selected_prs": selected,
                "input_linkage_sha256": linkage_hash,
                "records": records,
                "updated_at": stamp(),
            },
        )

    cohort = {
        "schema": "claude-legal-audit.github-pr-cohort-receipt.v1",
        "created_at": stamp(),
        "selected_prs": selected,
        "input_linkage_sha256": linkage_hash,
        "records": records,
        "request_budget": budget.receipt(),
        "completion_state": "complete" if {record.get("pr_number") for record in records} == set(selected) else "interrupted_unknown",
        "records_sha256": hashlib.sha256(canonical(records)).hexdigest(),
        "limitation": "This bounded cohort receipt hash-binds observed captures. Any interrupted, inaccessible, open, or unverified linkage remains explicitly unknown.",
    }
    receipt_path = out / f"{stamp().replace(':', '').replace('-', '')}-pr-cohort.capture-receipt.json"
    write_exclusive(receipt_path, canonical(cohort))
    return cohort, receipt_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--reserve", type=int, default=DEFAULT_RESERVE)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--resume", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("index", help="capture all public PR-list pages")
    detail = sub.add_parser("detail", help="capture one public PR detail response")
    detail.add_argument("number", type=int)
    files = sub.add_parser("files", help="capture all public PR-file pages")
    files.add_argument("number", type=int)
    commit = sub.add_parser("commit", help="capture one public commit response")
    commit.add_argument("sha")
    cohort = sub.add_parser("cohort", help="capture at most five incomplete PR evidence bundles")
    cohort.add_argument("numbers", nargs="*", type=int)
    cohort.add_argument("--limit", type=int, default=DEFAULT_COHORT_SIZE)
    args = parser.parse_args()

    if args.reserve < DEFAULT_RESERVE:
        raise SystemExit("--reserve may not be lower than 15 requests")
    out = custody_path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.command == "cohort":
        result, receipt_path = run_cohort(args, out)
        print(canonical({"completion_state": result["completion_state"], "receipt_path": receipt_path.relative_to(ROOT).as_posix(), "selected_prs": result["selected_prs"]}).decode("utf-8"), end="")
        return 0

    current, paginated, label = endpoint(args)
    budget = RequestBudget(reserve_remaining=args.reserve)
    checkpoint = args.checkpoint or (out / f"{label}.checkpoint.json")
    manifest, manifest_path = capture_set(
        current,
        paginated,
        label,
        out,
        budget,
        checkpoint=checkpoint,
        resume=args.resume,
    )
    print(canonical({"capture_kind": label, "completion_state": manifest["completion_state"], "page_count": manifest["page_count"], "manifest_path": manifest_path.relative_to(ROOT).as_posix()}).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
