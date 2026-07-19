from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, call, patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_pr_linkage as linkage  # noqa: E402
import capture_github_pr_evidence as capture  # noqa: E402
from capture_github_pr_evidence import RequestBudget, parse_link_header, verified_next_url  # noqa: E402


API = "https://api.github.com/repos/anthropics/claude-for-legal"


class CapturePolicyTest(unittest.TestCase):
    def test_structural_next_link_requires_immediate_same_endpoint_page(self) -> None:
        first = f"{API}/pulls/7/files?per_page=100"
        second = f"{API}/pulls/7/files?per_page=100&page=2"
        self.assertEqual(verified_next_url(first, f'<{second}>; rel="next"'), second)
        self.assertIsNone(verified_next_url(second, ""))
        numeric_second = "https://api.github.com/repositories/1217153065/pulls/7/files?per_page=100&page=2"
        self.assertEqual(verified_next_url(first, f'<{numeric_second}>; rel="next"'), numeric_second)
        for invalid in (
            f'<{API}/pulls/7/files?per_page=100&page=3>; rel="next"',
            f'<{API}/pulls/8/files?per_page=100&page=2>; rel="next"',
            f'<{API}/pulls/7/files?per_page=50&page=2>; rel="next"',
            '<https://example.com/repos/anthropics/claude-for-legal/pulls/7/files?page=2&per_page=100>; rel="next"',
            '<https://api.github.com/repositories/999/pulls/7/files?page=2&per_page=100>; rel="next"',
        ):
            with self.subTest(invalid=invalid), self.assertRaises(RuntimeError):
                verified_next_url(first, invalid)
        with self.assertRaises(RuntimeError):
            parse_link_header(f'<{second}>; rel="next", <{second}>; rel="next"')

    def test_request_budget_holds_fifteen_requests_in_reserve(self) -> None:
        budget = RequestBudget()
        budget.observe({"x-ratelimit-remaining": "16"})
        self.assertTrue(budget.permits_another_request())
        budget.observe({"x-ratelimit-remaining": "15"})
        self.assertFalse(budget.permits_another_request())
        self.assertEqual(budget.receipt()["requests_made"], 2)


class FilePaginationReceiptTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.capture_root = self.root / "private" / "raw" / "sources" / "SRC-0013"
        self.capture_root.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_capture(self, *, first_link: str, final_link: str, completion: str = "complete", numeric_second: bool = False) -> None:
        first_url = f"{API}/pulls/7/files?per_page=100"
        second_url = (
            "https://api.github.com/repositories/1217153065/pulls/7/files?per_page=100&page=2"
            if numeric_second
            else f"{API}/pulls/7/files?per_page=100&page=2"
        )
        pages = []
        for number, (url, link, body_payload) in enumerate(
            ((first_url, first_link, [{"filename": "a"}]), (second_url, final_link, [{"filename": "b"}])),
            start=1,
        ):
            body = (json.dumps(body_payload) + "\n").encode("utf-8")
            digest = hashlib.sha256(body).hexdigest()
            payload_path = self.capture_root / f"page-{number}.json"
            metadata_path = self.capture_root / f"page-{number}.capture.json"
            payload_path.write_bytes(body)
            metadata = {
                "requested_url": url,
                "final_url": url,
                "retrieved_at": f"2026-07-16T00:00:0{number}Z",
                "status_code": 200,
                "response_headers": {"link": link},
                "sha256": digest,
                "payload_path": payload_path.relative_to(self.root).as_posix(),
            }
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            pages.append(
                {
                    "page": number,
                    "metadata_path": metadata_path.relative_to(self.root).as_posix(),
                    "status_code": 200,
                    "sha256": digest,
                    "requested_url": url,
                    "final_url": url,
                    "next_url": second_url if number == 1 and first_link else None,
                }
            )
        manifest = {
            "schema": "claude-legal-audit.github-public-history-capture-set.v2",
            "created_at": "2026-07-16T00:00:03Z",
            "capture_kind": "pull-7-files",
            "pagination_expected": True,
            "completion_state": completion,
            "terminal_page_verified": completion == "complete",
            "page_count": 2,
            "pages": pages,
        }
        (self.capture_root / "files.capture-set.json").write_text(json.dumps(manifest), encoding="utf-8")

    def verify(self):
        with patch.object(linkage, "ROOT", self.root), patch.object(linkage, "CAPTURE_DIRS", (self.capture_root,)):
            return linkage.verified_file_capture(7, 2)

    def test_intermediate_next_and_final_terminal_links_are_required(self) -> None:
        second = f"{API}/pulls/7/files?per_page=100&page=2"
        self.write_capture(first_link=f'<{second}>; rel="next"', final_link="")
        evidence = self.verify()
        self.assertEqual(evidence["status"], "captured_complete")
        self.assertEqual(evidence["file_count"], 2)

    def test_numeric_repository_alias_is_accepted_in_complete_capture(self) -> None:
        second = "https://api.github.com/repositories/1217153065/pulls/7/files?per_page=100&page=2"
        self.write_capture(first_link=f'<{second}>; rel="next"', final_link="", numeric_second=True)
        evidence = self.verify()
        self.assertEqual(evidence["status"], "captured_complete")

    def test_missing_intermediate_next_is_rejected(self) -> None:
        self.write_capture(first_link="", final_link="")
        with self.assertRaises(SystemExit):
            self.verify()

    def test_next_link_on_final_page_is_rejected(self) -> None:
        second = f"{API}/pulls/7/files?per_page=100&page=2"
        third = f"{API}/pulls/7/files?per_page=100&page=3"
        self.write_capture(first_link=f'<{second}>; rel="next"', final_link=f'<{third}>; rel="next"')
        with self.assertRaises(SystemExit):
            self.verify()

    def test_interrupted_capture_remains_unknown(self) -> None:
        second = f"{API}/pulls/7/files?per_page=100&page=2"
        self.write_capture(first_link=f'<{second}>; rel="next"', final_link="", completion="interrupted_rate_budget")
        self.assertIsNone(self.verify())


class CaptureResumeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.capture_root = self.root / "private" / "raw" / "sources" / "SRC-0013"
        self.out = self.capture_root / "github-pr-history"
        self.checkpoint = self.capture_root / "pull-7-files.checkpoint.json"
        self.capture_root.mkdir(parents=True)
        self.first = f"{API}/pulls/7/files?per_page=100"
        self.second = f"{API}/pulls/7/files?per_page=100&page=2"
        self.clock = 0

    def tearDown(self) -> None:
        self.temp.cleanup()

    def fake_stamp(self) -> str:
        self.clock += 1
        return f"2026-07-16T00:00:{self.clock:02d}Z"

    def patch_context(self, mocked_fetch):
        return (
            patch.object(capture, "ROOT", self.root),
            patch.object(capture, "PRIVATE_CUSTODY_ROOT", self.capture_root),
            patch.object(capture, "stamp", side_effect=self.fake_stamp),
            patch.object(capture, "fetch", mocked_fetch),
        )

    def initial_capture(self) -> None:
        body = b'[{"filename":"a"}]\n'
        headers = {
            "content-type": "application/json",
            "etag": '"etag-page-1"',
            "link": f'<{self.second}>; rel="next"',
            "x-ratelimit-remaining": "15",
        }
        mocked = Mock(return_value=(200, body, headers, self.first))
        root_patch, custody_patch, stamp_patch, fetch_patch = self.patch_context(mocked)
        with root_patch, custody_patch, stamp_patch, fetch_patch:
            manifest, _ = capture.capture_set(
                self.first,
                True,
                "pull-7-files",
                self.out,
                RequestBudget(),
                checkpoint=self.checkpoint,
            )
        self.assertEqual(manifest["completion_state"], "interrupted_rate_budget")
        self.assertEqual(mocked.call_args_list, [call(self.first, None)])

    def test_resume_revalidates_last_page_with_its_etag_before_next_page(self) -> None:
        self.initial_capture()
        second_body = b'[{"filename":"b"}]\n'
        mocked = Mock(
            side_effect=[
                (304, b"", {"etag": '"etag-page-1"', "x-ratelimit-remaining": "16"}, self.first),
                (200, second_body, {"content-type": "application/json", "etag": '"etag-page-2"', "x-ratelimit-remaining": "15"}, self.second),
            ]
        )
        root_patch, custody_patch, stamp_patch, fetch_patch = self.patch_context(mocked)
        with root_patch, custody_patch, stamp_patch, fetch_patch:
            manifest, _ = capture.capture_set(
                self.first,
                True,
                "pull-7-files",
                self.out,
                RequestBudget(),
                checkpoint=self.checkpoint,
                resume=True,
            )
        self.assertEqual(mocked.call_args_list, [call(self.first, '"etag-page-1"'), call(self.second, None)])
        self.assertEqual(manifest["completion_state"], "complete")
        self.assertTrue(manifest["terminal_page_verified"])
        self.assertEqual(manifest["page_count"], 2)

    def test_resume_stops_at_reserve_after_conditional_revalidation(self) -> None:
        self.initial_capture()
        mocked = Mock(return_value=(304, b"", {"etag": '"etag-page-1"', "x-ratelimit-remaining": "15"}, self.first))
        root_patch, custody_patch, stamp_patch, fetch_patch = self.patch_context(mocked)
        with root_patch, custody_patch, stamp_patch, fetch_patch:
            manifest, _ = capture.capture_set(
                self.first,
                True,
                "pull-7-files",
                self.out,
                RequestBudget(),
                checkpoint=self.checkpoint,
                resume=True,
            )
        self.assertEqual(mocked.call_args_list, [call(self.first, '"etag-page-1"')])
        self.assertEqual(manifest["completion_state"], "interrupted_rate_budget")
        checkpoint = json.loads(self.checkpoint.read_text(encoding="utf-8"))
        self.assertEqual(checkpoint["next_url"], self.second)

    def test_resume_rejects_initial_url_and_custody_tampering_before_fetch(self) -> None:
        self.initial_capture()
        mocked = Mock()
        root_patch, custody_patch, stamp_patch, fetch_patch = self.patch_context(mocked)
        with root_patch, custody_patch, stamp_patch, fetch_patch, self.assertRaises(SystemExit):
            capture.capture_set(
                f"{API}/pulls/8/files?per_page=100",
                True,
                "pull-7-files",
                self.out,
                RequestBudget(),
                checkpoint=self.checkpoint,
                resume=True,
            )
        mocked.assert_not_called()

        state = json.loads(self.checkpoint.read_text(encoding="utf-8"))
        metadata = json.loads((self.root / state["pages"][0]["metadata_path"]).read_text(encoding="utf-8"))
        (self.root / metadata["payload_path"]).write_bytes(b"tampered")
        mocked = Mock()
        root_patch, custody_patch, stamp_patch, fetch_patch = self.patch_context(mocked)
        with root_patch, custody_patch, stamp_patch, fetch_patch, self.assertRaises(SystemExit):
            capture.capture_set(
                self.first,
                True,
                "pull-7-files",
                self.out,
                RequestBudget(),
                checkpoint=self.checkpoint,
                resume=True,
            )
        mocked.assert_not_called()

    def test_fetch_accepts_304_but_rejects_redirects(self) -> None:
        class ErrorOpener:
            def __init__(self, code: int) -> None:
                self.code = code

            def open(self, request, timeout):  # noqa: ANN001, ANN201
                raise HTTPError(request.full_url, self.code, "test", {}, io.BytesIO(b""))

        with patch.object(capture, "build_opener", return_value=ErrorOpener(304)):
            status, body, _, final_url = capture.fetch(self.first, '"etag-page-1"')
        self.assertEqual((status, body, final_url), (304, b"", self.first))

        with patch.object(capture, "build_opener", return_value=ErrorOpener(302)), self.assertRaises(RuntimeError):
            capture.fetch(self.first)


if __name__ == "__main__":
    unittest.main()
