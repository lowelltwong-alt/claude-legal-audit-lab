from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_chunk_registry import (  # noqa: E402
    CHUNK_PREFIX,
    EDGE_PREFIX,
    FORBIDDEN_PUBLIC_SUBSTRINGS,
    MIGRATION_OUT,
    build_outputs,
    canon,
    git_tree_snapshot,
    partition_static_file,
    validate_migration_payload,
    validate_policy,
    validate_registry_payload,
)


class ChunkRegistryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry_path = ROOT / "registry" / "chunk-registry.json"
        cls.registry_bytes = cls.registry_path.read_bytes()
        cls.payload = json.loads(cls.registry_bytes.decode("utf-8"))
        cls.migration = json.loads(MIGRATION_OUT.read_text(encoding="utf-8"))
        cls.policy = json.loads((ROOT / "registry" / "chunk-policy.json").read_text(encoding="utf-8"))
        cls.commit = cls.payload["pinned_commit"]
        cls.tree = {
            path: (blob_oid, data)
            for path, blob_oid, data in git_tree_snapshot(
                str((ROOT / "upstream" / "claude-for-legal").resolve()), cls.commit
            )
        }
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "build_chunk_registry.py"),
                "--check",
                "--verify-reconstruction",
            ],
            check=True,
            cwd=ROOT,
        )
        cargo = shutil.which("cargo")
        if cargo is None:
            raise unittest.SkipTest("cargo is required for Python/Rust parity")
        subprocess.run(
            [cargo, "build", "--quiet", "--manifest-path", str(ROOT / "rust" / "chunk-engine" / "Cargo.toml")],
            check=True,
            cwd=ROOT,
            env={**os.environ, "CARGO_TERM_COLOR": "never"},
        )
        binary_name = "claude-legal-chunk-engine.exe" if os.name == "nt" else "claude-legal-chunk-engine"
        cls.rust_binary = ROOT / "rust" / "chunk-engine" / "target" / "debug" / binary_name
        if not cls.rust_binary.is_file():
            raise AssertionError(f"Rust chunk binary was not built: {cls.rust_binary}")

    def assert_invalid(self, payload: dict, expected_fragment: str | None = None) -> list[str]:
        errors = validate_registry_payload(payload)
        self.assertTrue(errors, "mutated registry unexpectedly passed production validation")
        if expected_fragment:
            self.assertIn(expected_fragment.lower(), "\n".join(errors).lower())
        return errors

    def test_lossless_git_blob_partitions_and_full_ids(self) -> None:
        groups: dict[str, list[dict]] = defaultdict(list)
        for chunk in self.payload["chunks"]:
            self.assertRegex(chunk["chunk_id"], rf"^{CHUNK_PREFIX}[0-9a-f]{{64}}$")
            groups[chunk["parent"]["path"]].append(chunk)
        self.assertEqual(set(groups), set(self.tree))
        for path, chunks in groups.items():
            blob_oid, data = self.tree[path]
            ordered = sorted(chunks, key=lambda item: item["exact_locator"]["byte_start"])
            reassembled = bytearray()
            offset = 0
            for chunk in ordered:
                locator = chunk["exact_locator"]
                self.assertEqual(locator["byte_start"], offset)
                span = data[locator["byte_start"] : locator["byte_end_exclusive"]]
                self.assertEqual(hashlib.sha256(span).hexdigest(), chunk["content_sha256"])
                reassembled.extend(span)
                offset = locator["byte_end_exclusive"]
                self.assertEqual(chunk["identity"]["locator"], locator)
                self.assertEqual(chunk["identity"]["parent_id"], chunk["parent"]["parent_id"])
            self.assertEqual(bytes(reassembled), data)
            self.assertEqual(offset, len(data))
            self.assertEqual(chunks[0]["parent"]["git_blob_oid"], blob_oid)
            self.assertEqual(hashlib.sha256(data).hexdigest(), chunks[0]["parent"]["sha256"])

    def test_fixture_corpus_preserves_utf8_and_newlines(self) -> None:
        fixtures = json.loads((ROOT / "tests" / "fixtures" / "chunk-adversarial.json").read_text(encoding="utf-8"))
        for case in fixtures["cases"]:
            if "text" in case:
                data = case["text"].encode("utf-8")
            else:
                data = (case["repeat"] * case["repeat_count"]).encode("utf-8")
            spans = partition_static_file(data, case["lines_per_chunk"])
            self.assertEqual(b"".join(data[start:end] for start, end in spans), data, case["name"])
            for start, end in spans:
                data[start:end].decode("utf-8")
                if start < len(data):
                    self.assertNotEqual(data[start] & 0xC0, 0x80)
                if end < len(data):
                    self.assertNotEqual(data[end] & 0xC0, 0x80)
        bom_case = fixtures["cases"][0]["text"].encode("utf-8")
        self.assertTrue(bom_case.startswith(b"\xef\xbb\xbf"))
        self.assertIn(b"\r\n", bom_case)

    def test_typed_adjacency_edges_are_complete_and_invertible(self) -> None:
        edges = self.payload["edges"]
        self.assertEqual(len(edges), 246)
        edge_by_id = {edge["edge_id"]: edge for edge in edges}
        self.assertEqual(len(edge_by_id), len(edges))
        for edge in edges:
            self.assertRegex(edge["edge_id"], rf"^{EDGE_PREFIX}[0-9a-f]{{64}}$")
            inverse = edge_by_id[edge["inverse_edge_id"]]
            self.assertEqual(inverse["inverse_edge_id"], edge["edge_id"])
            self.assertEqual(inverse["source_chunk_id"], edge["target_chunk_id"])
            self.assertEqual(inverse["target_chunk_id"], edge["source_chunk_id"])
        self.assertFalse(validate_registry_payload(self.payload))

    def test_production_validator_rejects_partition_identity_and_order_mutations(self) -> None:
        mutations: list[tuple[str, callable]] = []

        def gap(payload: dict) -> None:
            candidate = next(chunk for chunk in payload["chunks"] if chunk["exact_locator"]["byte_end_exclusive"] > 1)
            candidate["exact_locator"]["byte_start"] += 1
            candidate["identity"]["locator"] = deepcopy(candidate["exact_locator"])

        def overlap(payload: dict) -> None:
            groups: dict[str, list[dict]] = defaultdict(list)
            for chunk in payload["chunks"]:
                groups[chunk["parent"]["path"]].append(chunk)
            ordered = next(sorted(items, key=lambda item: item["exact_locator"]["byte_start"]) for items in groups.values() if len(items) > 1)
            ordered[1]["exact_locator"]["byte_start"] = ordered[0]["exact_locator"]["byte_end_exclusive"] - 1
            ordered[1]["identity"]["locator"] = deepcopy(ordered[1]["exact_locator"])

        mutations.extend(
            [
                ("gap", gap),
                ("overlap", overlap),
                ("reordered chunks", lambda p: p["chunks"].__setitem__(slice(0, 2), list(reversed(p["chunks"][:2])))),
                ("stale parent", lambda p: p["chunks"][0]["parent"].__setitem__("sha256", "0" * 64)),
                ("bad content", lambda p: p["chunks"][0].__setitem__("content_sha256", "0" * 64)),
                ("bad line hint", lambda p: p["chunks"][0]["exact_locator"].__setitem__("line_start", 99)),
                ("zero length", lambda p: p["chunks"][0]["exact_locator"].__setitem__("byte_end_exclusive", 0)),
            ]
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                payload = deepcopy(self.payload)
                mutate(payload)
                self.assert_invalid(payload)

    def test_production_validator_rejects_duplicates_collisions_sources_and_privacy(self) -> None:
        duplicate = deepcopy(self.payload)
        duplicate["chunks"].append(deepcopy(duplicate["chunks"][0]))
        self.assert_invalid(duplicate, "duplicate")

        collision = deepcopy(self.payload)
        other = deepcopy(collision["chunks"][0])
        other["identity"]["content_sha256"] = "1" * 64
        collision["chunks"].append(other)
        self.assert_invalid(collision, "collision")

        unknown_source = deepcopy(self.payload)
        unknown_source["chunks"][0]["source_ids"] = ["SRC-9999"]
        self.assert_invalid(unknown_source, "unknown source")

        inactive = deepcopy(self.payload)
        inactive["chunks"][0]["chunk_kind"] = "pr_file_record"
        self.assert_invalid(inactive, "inactive")

        for unsafe_path in ["private/raw.json", ".private/raw.json", "C:\\Users\\example\\raw.json", "../raw.json"]:
            payload = deepcopy(self.payload)
            payload["chunks"][0]["parent"]["path"] = unsafe_path
            self.assert_invalid(payload)

        embedded = deepcopy(self.payload)
        embedded["chunks"][0]["payload"] = "not-public"
        self.assert_invalid(embedded, "embed field")

        rendered = self.registry_bytes.decode("utf-8").lower()
        for needle in FORBIDDEN_PUBLIC_SUBSTRINGS:
            self.assertNotIn(needle.lower(), rendered)

    def test_production_validator_rejects_edge_and_cycle_mutations(self) -> None:
        missing_inverse = deepcopy(self.payload)
        missing_inverse["edges"].pop()
        self.assert_invalid(missing_inverse, "edge set mismatch")

        unknown_endpoint = deepcopy(self.payload)
        unknown_endpoint["edges"][0]["target_chunk_id"] = CHUNK_PREFIX + "f" * 64
        self.assert_invalid(unknown_endpoint, "unknown chunk")

        wrong_id = deepcopy(self.payload)
        wrong_id["edges"][0]["edge_id"] = EDGE_PREFIX + "f" * 64
        self.assert_invalid(wrong_id, "canonical identity")

        reordered = deepcopy(self.payload)
        reordered["edges"][:2] = reversed(reordered["edges"][:2])
        self.assert_invalid(reordered, "canonical")

        cycle = deepcopy(self.payload)
        first = cycle["edges"][0]
        extra = deepcopy(first)
        extra["source_chunk_id"], extra["target_chunk_id"] = first["target_chunk_id"], first["source_chunk_id"]
        cycle["edges"].append(extra)
        self.assert_invalid(cycle, "edge set mismatch")

    def test_policy_and_migration_fail_closed(self) -> None:
        bad_policy = deepcopy(self.policy)
        del bad_policy["format_version"]
        self.assertTrue(validate_policy(bad_policy))
        weakened_privacy = deepcopy(self.policy)
        weakened_privacy["privacy"]["forbidden_path_prefixes"] = ["private/"]
        self.assertTrue(validate_policy(weakened_privacy))
        premature = deepcopy(self.policy)
        premature["activated_chunk_kinds"].append("pr_file_record")
        self.assertTrue(validate_policy(premature))

        self.assertFalse(validate_migration_payload(self.migration, self.payload))
        self.assertEqual(len(self.migration["mappings"]), len(self.payload["chunks"]))
        duplicate = deepcopy(self.migration)
        duplicate["mappings"][1]["old_chunk_id"] = duplicate["mappings"][0]["old_chunk_id"]
        self.assertTrue(validate_migration_payload(duplicate, self.payload))
        stale = deepcopy(self.migration)
        stale["target_registry_sha256"] = "0" * 64
        self.assertTrue(validate_migration_payload(stale, self.payload))

    def test_python_rust_and_authoritative_bytes_match_without_authority_swap(self) -> None:
        before = self.registry_path.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            python_out = tmp_path / "python.json"
            rust_out = tmp_path / "rust.json"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_chunk_registry.py"), "--output", str(python_out)],
                check=True,
                cwd=ROOT,
            )
            subprocess.run(
                [str(self.rust_binary), "--repo-root", str(ROOT), "--output", str(rust_out)],
                check=True,
                cwd=ROOT,
            )
            self.assertEqual(python_out.read_bytes(), rust_out.read_bytes())
            self.assertEqual(python_out.read_bytes(), before)
        self.assertEqual(self.registry_path.read_bytes(), before)

    def test_cli_rejects_stale_candidate_without_touching_authority(self) -> None:
        stale = deepcopy(self.payload)
        stale["chunks"] = stale["chunks"][:-1]
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "stale.json"
            candidate.write_bytes(canon(stale))
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_chunk_registry.py"), "--validate-file", str(candidate)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid", (result.stdout + result.stderr).lower())
        self.assertEqual(self.registry_path.read_bytes(), self.registry_bytes)

    def test_rebuild_is_deterministic(self) -> None:
        registry, migration = build_outputs()
        self.assertEqual(canon(registry), self.registry_bytes)
        self.assertEqual(canon(migration), MIGRATION_OUT.read_bytes())


if __name__ == "__main__":
    unittest.main()
