#!/usr/bin/env python3
"""Build and validate the typed evidence/argument graph from governed registries."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator

from public_safety import public_content_violations

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "registry" / "evidence-graph.json"
SCHEMA = ROOT / "schemas" / "evidence-graph.schema.json"
EDGE_LIBRARY = ROOT / "registry" / "edge-type-library.json"
EDGE_SCHEMA = ROOT / "schemas" / "edge-type-library.schema.json"
CHUNKS = ROOT / "registry" / "chunk-registry.json"
SOURCES = ROOT / "registry" / "source-registry.json"
CLAIMS = ROOT / "registry" / "claim-registry.json"
ARGUMENTS = ROOT / "registry" / "argument-mesh.json"
PR_LINKAGE = ROOT / "results" / "pr-commit-diff-linkage.json"
UPSTREAM = ROOT / "upstream" / "claude-for-legal"
REVISION = "1.0.0"
REPOSITORY = "anthropics/claude-for-legal"
REPOSITORY_NODE = "repo:anthropics/claude-for-legal"


def canonical(payload: object, *, compact: bool = False) -> bytes:
    if compact:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"ERROR: {path.relative_to(ROOT)} must be a JSON object")
    return payload


def fresh(status: str, as_of: str | None = None, stale_after: str | None = None) -> dict:
    return {"status": status, "as_of": as_of, "stale_after": stale_after}


def node(
    node_id: str,
    node_type: str,
    attributes: dict,
    *,
    authority: str,
    classification: str,
    creation_method: str,
    review_state: str = "candidate",
    evidence_refs: list[str] | None = None,
    observation_time: str | None = None,
    freshness: dict | None = None,
) -> dict:
    return {
        "node_id": node_id,
        "node_type": node_type,
        "revision": REVISION,
        "authority": authority,
        "classification": classification,
        "creation_method": creation_method,
        "review_state": review_state,
        "evidence_refs": sorted(set(evidence_refs or [])),
        "observation_time": observation_time,
        "validity": {"valid_from": None, "valid_to": None},
        "freshness": freshness or fresh("candidate", observation_time),
        "attributes": {"kind": node_type, **attributes},
    }


def file_node_id(path: str) -> str:
    material = canonical({"path": path, "repository": REPOSITORY}, compact=True)
    return "file:sha256:" + digest(material)


def edge_identifier(edge_type: str, source: str, target: str) -> str:
    return "gedge:sha256:" + digest(canonical({"edge_type": edge_type, "revision": REVISION, "source_node_id": source, "target_node_id": target}, compact=True))


def git_paths(base: str, commit: str) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(UPSTREAM), "diff-tree", "--no-commit-id", "--name-only", "-r", base, commit],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    paths = []
    for raw in result.stdout.splitlines():
        try:
            path = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            continue
        if path and "\\" not in path and not path.startswith("/") and ".." not in PurePosixPath(path).parts:
            paths.append(path)
    return sorted(set(paths), key=lambda value: value.encode("utf-8"))


class GraphBuilder:
    def __init__(self, library: dict) -> None:
        self.nodes: dict[str, dict] = {}
        self.specs: dict[tuple[str, str, str], dict] = {}
        self.inverse: dict[str, str] = {}
        self.pair: dict[str, dict] = {}
        for pair in library["pairs"]:
            self.inverse[pair["forward"]] = pair["inverse"]
            self.inverse[pair["inverse"]] = pair["forward"]
            self.pair[pair["forward"]] = pair
            self.pair[pair["inverse"]] = pair

    def add_node(self, value: dict) -> None:
        existing = self.nodes.get(value["node_id"])
        if existing is not None and existing != value:
            raise SystemExit(f"ERROR: conflicting graph-node preimage: {value['node_id']}")
        self.nodes[value["node_id"]] = value

    def add_relation(
        self,
        source: str,
        relation: str,
        target: str,
        basis: str,
        limitation: str,
        *,
        evidence_refs: list[str] | None = None,
        review_state: str = "candidate",
        observation_time: str | None = None,
        authority: str = "candidate_analysis",
        classification: str = "candidate_evidence",
        creation_method: str = "deterministic_builder",
    ) -> None:
        if relation not in self.inverse:
            raise SystemExit(f"ERROR: relation absent from edge library: {relation}")
        inverse = self.inverse[relation]
        common = {
            "basis": basis,
            "limitation": limitation,
            "evidence_refs": sorted(set(evidence_refs or [])),
            "review_state": review_state,
            "observation_time": observation_time,
            "authority": authority,
            "classification": classification,
            "creation_method": creation_method,
        }
        for key in ((source, relation, target), (target, inverse, source)):
            existing = self.specs.get(key)
            if existing is None:
                self.specs[key] = dict(common)
            else:
                existing["evidence_refs"] = sorted(set(existing["evidence_refs"]) | set(common["evidence_refs"]))
                if existing["basis"] != common["basis"]:
                    existing["basis"] = existing["basis"] + " | " + common["basis"]

    def finalized_edges(self) -> list[dict]:
        edges = []
        for (source, relation, target), spec in sorted(self.specs.items()):
            inverse = self.inverse[relation]
            edges.append(
                {
                    "edge_id": edge_identifier(relation, source, target),
                    "edge_type": relation,
                    "source_node_id": source,
                    "target_node_id": target,
                    "inverse_edge_id": edge_identifier(inverse, target, source),
                    "revision": REVISION,
                    "authority": spec["authority"],
                    "classification": spec["classification"],
                    "creation_method": spec["creation_method"],
                    "review_state": spec["review_state"],
                    "evidence_refs": spec["evidence_refs"],
                    "observation_time": spec["observation_time"],
                    "validity": {"valid_from": None, "valid_to": None},
                    "freshness": fresh("candidate", spec["observation_time"]),
                    "basis": spec["basis"],
                    "limitation": spec["limitation"],
                }
            )
        return edges


def build_graph() -> dict:
    library = load(EDGE_LIBRARY)
    graph = GraphBuilder(library)
    chunk_registry = load(CHUNKS)
    sources = load(SOURCES)
    claims = load(CLAIMS)
    arguments = load(ARGUMENTS)
    linkage = load(PR_LINKAGE)
    commit = chunk_registry["pinned_commit"]
    revision_node = f"rev:git:{commit}"
    graph.add_node(node(REPOSITORY_NODE, "repository", {"repository": REPOSITORY, "url": "https://github.com/anthropics/claude-for-legal"}, authority="primary_source", classification="public_primary", creation_method="git_object", review_state="reviewed", freshness=fresh("immutable")))
    graph.add_node(node(revision_node, "revision", {"repository_id": REPOSITORY_NODE, "commit_sha": commit}, authority="primary_source", classification="public_primary", creation_method="git_object", review_state="reviewed", evidence_refs=["SRC-0002"], freshness=fresh("immutable")))
    graph.add_relation(REPOSITORY_NODE, "CONTAINS", revision_node, "The repository contains the immutable pinned revision.", "This graph contains only the pinned revision, not complete remote history.", review_state="reviewed", authority="deterministic_derivative", classification="public_normalized", creation_method="git_object")

    source_by_id = {item["source_id"]: item for item in sources["sources"]}
    for item in sources["sources"]:
        source_id = item["source_id"]
        binding = item.get("revision_binding", {})
        immutable = binding.get("kind") in {"git_commit", "content_hash", "stable_doi", "stable_versioned_text", "stable_dated_pdf", "stable_proceedings"}
        graph.add_node(node(source_id, "source", {"title": item["title"], "url": item["url"], "source_class": item["source_class"], "status": item["status"], "revision_binding": binding}, authority="registered_source", classification="public_primary", creation_method="registered_manual_research", review_state="reviewed" if item["status"] in {"immutable_revision", "verified_content_hash"} else "candidate", observation_time=item.get("accessed_at"), freshness=fresh("immutable" if immutable else "current_observation", item.get("accessed_at"))))
        content_hash = binding.get("content_sha256")
        if isinstance(content_hash, str) and re.fullmatch(r"[0-9a-f]{64}", content_hash):
            capture_id = "capture:sha256:" + content_hash
            graph.add_node(node(capture_id, "capture", {"capture_kind": "registered_public_source_capture", "custody_id": "custody:sha256:" + content_hash, "sha256": content_hash, "url": item["url"]}, authority="registered_source", classification="public_normalized", creation_method="public_capture_receipt", review_state="reviewed", evidence_refs=[source_id], observation_time=item.get("accessed_at"), freshness=fresh("current_observation", item.get("accessed_at"))))
            graph.add_relation(capture_id, "CAPTURED_FROM", source_id, "The registered content-hash observation was captured from this public source URL.", "The hash binds the observed bytes, not later content or tenant behavior.", evidence_refs=[source_id], review_state="reviewed", observation_time=item.get("accessed_at"), authority="registered_source", classification="public_normalized", creation_method="public_capture_receipt")
            graph.add_relation(capture_id, "HASH_BINDS", source_id, "The capture digest binds the registered source observation.", "Hash identity is not substantive truth or remote completeness.", evidence_refs=[source_id], review_state="reviewed", observation_time=item.get("accessed_at"), authority="registered_source", classification="public_normalized", creation_method="public_capture_receipt")
        if binding.get("kind") == "git_commit" and binding.get("value") == commit:
            graph.add_relation(source_id, "AT_REVISION", revision_node, "The registered repository source is bound to the pinned Git commit.", "The pinned source is static design evidence, not deployed runtime evidence.", evidence_refs=[source_id], review_state="reviewed", authority="registered_source", classification="public_normalized")

    file_records: dict[str, dict] = {}
    chunks_by_path: dict[str, list[dict]] = defaultdict(list)
    for chunk in chunk_registry["chunks"]:
        parent = chunk["parent"]
        path = parent["path"]
        file_id = file_node_id(path)
        file_records[file_id] = {"path": path, "git_blob_oid": parent["git_blob_oid"], "content_sha256": parent["sha256"]}
        chunks_by_path[path].append(chunk)
    for file_id, record in sorted(file_records.items()):
        graph.add_node(node(file_id, "file", {"repository_id": REPOSITORY_NODE, **record}, authority="primary_source", classification="public_primary", creation_method="git_object", review_state="reviewed", evidence_refs=["SRC-0002"], freshness=fresh("immutable")))
        graph.add_relation(revision_node, "CONTAINS", file_id, "The immutable revision tree contains this UTF-8 file path.", "Tree membership does not establish semantic importance or runtime use.", evidence_refs=["SRC-0002"], review_state="reviewed", authority="deterministic_derivative", classification="public_normalized", creation_method="git_object")
    for chunk in chunk_registry["chunks"]:
        path = chunk["parent"]["path"]
        file_id = file_node_id(path)
        chunk_id = chunk["chunk_id"]
        graph.add_node(node(chunk_id, "chunk", {"chunk_kind": chunk["chunk_kind"], "content_sha256": chunk["content_sha256"], "parent_file_id": file_id, "locator": chunk["exact_locator"]}, authority="deterministic_derivative", classification="candidate_evidence", creation_method="deterministic_builder", review_state=chunk["review_status"], evidence_refs=chunk["source_ids"], freshness=fresh("immutable")))
        graph.add_relation(file_id, "CONTAINS", chunk_id, "The file parent contains this byte-exact partition span.", "Chunk boundaries are deterministic retrieval units, not semantic claims.", evidence_refs=chunk["source_ids"], review_state="reviewed", authority="deterministic_derivative", classification="public_normalized")
        graph.add_relation("SRC-0002", "LOCATES", chunk_id, "The pinned repository source locates this exact Git-blob span.", "Repository-wide location alone does not establish support for a particular claim.", evidence_refs=["SRC-0002"], review_state="reviewed", authority="deterministic_derivative", classification="public_normalized")
        graph.add_relation(chunk_id, "HASH_BINDS", file_id, "The chunk content and parent hashes bind this span to its immutable file.", "Hash binding proves byte identity and partition membership only.", evidence_refs=chunk["source_ids"], review_state="reviewed", authority="deterministic_derivative", classification="public_normalized")
    for edge in chunk_registry["edges"]:
        if edge["edge_type"] == "NEXT_IN_PARENT":
            graph.add_relation(edge["source_chunk_id"], "NEXT_IN_PARENT", edge["target_chunk_id"], "The target span immediately follows the source in one immutable parent.", edge["limitation"], evidence_refs=["SRC-0002"], review_state="reviewed", authority="deterministic_derivative", classification="public_normalized")

    claim_by_id = {claim["claim_id"]: claim for claim in claims["claims"]}
    for claim in claims["claims"]:
        claim_id = claim["claim_id"]
        evidence_sources = sorted({evidence["source_id"] for evidence in claim["evidence"]})
        graph.add_node(node(claim_id, "claim", {"lifecycle": claim["lifecycle"], "epistemic_status": claim["epistemic_status"], "publication_eligibility": claim["publication_eligibility"], "proposition": claim["proposition"], "does_not_prove": claim["does_not_prove"]}, authority="candidate_analysis", classification="candidate_evidence", creation_method="candidate_authoring", review_state=claim["review_state"], evidence_refs=evidence_sources, observation_time=claims.get("reviewed_at"), freshness=fresh("candidate", claims.get("reviewed_at"))))
        relation = "LEAVES_UNKNOWN" if claim["epistemic_status"] == "unknown" else ("CONSTRAINS" if claim["epistemic_status"] == "counterevidence" else "EVIDENCES")
        for evidence in claim["evidence"]:
            source_id = evidence["source_id"]
            graph.add_relation(source_id, relation, claim_id, f"Registered evidence locator: {evidence['locator']}", claim["does_not_prove"], evidence_refs=[source_id], review_state=claim["review_state"], observation_time=source_by_id[source_id].get("accessed_at"), authority="candidate_analysis", classification="candidate_evidence", creation_method="registered_manual_research")

    exact = claim_by_id["CLM-0002"]
    for chunk in chunks_by_path.get("scripts/deploy-managed-agent.sh", []):
        locator = chunk["exact_locator"]
        if locator["line_start"] <= 190 and locator["line_end"] >= 75:
            graph.add_relation(chunk["chunk_id"], "EVIDENCES", "CLM-0002", "The byte-exact chunk overlaps the registered lines 75-190 deployment-script locator.", exact["does_not_prove"], evidence_refs=["SRC-0002", chunk["chunk_id"]], review_state="reviewed", authority="candidate_analysis", classification="candidate_evidence")
            graph.add_relation("CLM-0002", "DERIVED_FROM", chunk["chunk_id"], "The reviewed bounded code observation is derived from this exact immutable chunk.", exact["does_not_prove"], evidence_refs=["SRC-0002", chunk["chunk_id"]], review_state="reviewed", authority="candidate_analysis", classification="candidate_evidence")

    design = claim_by_id["CLM-0001"]
    design_bindings = (
        ("commercial-legal/skills/cold-start-interview/SKILL.md", ((23, 25), (72, 74))),
        ("commercial-legal/agents/deal-debrief.md", ((89, 118),)),
        ("commercial-legal/agents/playbook-monitor.md", ((50, 74), (135, 166))),
    )
    for path, ranges in design_bindings:
        for chunk in chunks_by_path.get(path, []):
            locator = chunk["exact_locator"]
            if any(locator["line_start"] <= end and locator["line_end"] >= start for start, end in ranges):
                graph.add_relation(
                    chunk["chunk_id"],
                    "EVIDENCES",
                    "CLM-0001",
                    f"The byte-exact chunk overlaps a registered static-design locator in {path}.",
                    design["does_not_prove"],
                    evidence_refs=["SRC-0002", chunk["chunk_id"]],
                    review_state="candidate",
                    authority="candidate_analysis",
                    classification="candidate_evidence",
                )
                graph.add_relation(
                    "CLM-0001",
                    "DERIVED_FROM",
                    chunk["chunk_id"],
                    f"The bounded static-design observation is derived from an immutable chunk of {path}.",
                    design["does_not_prove"],
                    evidence_refs=["SRC-0002", chunk["chunk_id"]],
                    review_state="candidate",
                    authority="candidate_analysis",
                    classification="candidate_evidence",
                )

    object_type: dict[str, str] = {}
    for index, obj in enumerate(arguments["objects"], start=1):
        object_id = obj["object_id"]
        if obj["object_type"] == "proof_gap":
            node_type = "proof_gap"
            attributes = {"title": obj["title"], "statement": obj["statement"]}
            classification = "candidate_argument"
        elif obj["object_type"] == "paper_section":
            node_type = "paper_section"
            attributes = {"title": obj["title"], "order": index}
            classification = "candidate_paper"
        else:
            node_type = "argument_object"
            attributes = {"argument_type": obj["object_type"], "title": obj["title"], "statement": obj["statement"], "epistemic_status": obj["epistemic_status"]}
            classification = "candidate_argument"
        object_type[object_id] = node_type
        graph.add_node(node(object_id, node_type, attributes, authority="candidate_analysis", classification=classification, creation_method="candidate_authoring", review_state=obj["review_status"], evidence_refs=obj.get("claim_ids", []) + obj.get("source_ids", []), freshness=fresh("candidate")))
        for claim_id in obj.get("claim_ids", []):
            if claim_id in claim_by_id:
                if node_type == "paper_section":
                    relation = "PRESENTED_IN"
                elif node_type == "proof_gap":
                    relation = "EVIDENCES"
                else:
                    relation = "SUPPORTS"
                graph.add_relation(claim_id, relation, object_id, "The argument mesh explicitly registers this bounded claim in the target object.", claim_by_id[claim_id]["does_not_prove"], evidence_refs=[claim_id], review_state="candidate", authority="candidate_analysis", classification="candidate_argument")

    for old in arguments["edges"]:
        source, relation, target = old["source"], old["relation"], old["target"]
        mapped: tuple[str, str, str] | None = None
        if relation == "HAS_THESIS": mapped = (source, "CONTAINS", target)
        elif relation == "PART_OF_THEORY": mapped = (target, "CONTAINS", source)
        elif relation == "SUPPORTED_BY": mapped = (target, "SUPPORTS", source)
        elif relation == "SUPPORTS": mapped = (source, "SUPPORTS", target)
        elif relation == "CHALLENGED_BY": mapped = (target, "CHALLENGES", source)
        elif relation == "CHALLENGES": mapped = (source, "CHALLENGES", target)
        elif relation == "ANSWERED_BY": mapped = (target, "REBUTS", source)
        elif relation == "ANSWERS": mapped = (source, "REBUTS", target)
        elif relation == "WEAKENED_BY": mapped = (source, "FALSIFIES_IF", target)
        elif relation == "WEAKENS": mapped = (target, "FALSIFIES_IF", source)
        elif relation == "HAS_PROOF_GAP": mapped = (source, "HAS_PROOF_GAP", target)
        elif relation == "PROOF_GAP_OF": mapped = (target, "HAS_PROOF_GAP", source)
        elif relation == "PRESENTED_IN": mapped = (source, "PRESENTED_IN", target)
        elif relation == "PRESENTS": mapped = (target, "PRESENTED_IN", source)
        if mapped:
            graph.add_relation(*mapped, old["basis"], "The imported argument relation remains candidate and does not promote truth.", review_state=old["review_status"], authority="candidate_analysis", classification="candidate_argument", creation_method="candidate_authoring")

    for record in linkage["records"]:
        pr_number = record["pr_number"]
        pr_id = f"pr:anthropics/claude-for-legal:{pr_number}"
        status = record["public_capture_linkage"]["status"]
        observation = record["public_capture_linkage"].get("detail", {}).get("observed_at") if record["public_capture_linkage"].get("detail") else linkage["capture"].get("observed_at")
        graph.add_node(node(pr_id, "pr", {"pr_number": pr_number, "state": record["state"], "html_url": record["html_url"], "event_time": record["event_time"], "capture_status": status}, authority="registered_source", classification="public_normalized", creation_method="deterministic_builder", review_state="reviewed" if status in {"linked_verified_capture", "captured_open_or_unmerged_snapshot"} else "candidate", evidence_refs=[linkage["capture"]["custody_id"]], observation_time=observation, freshness=fresh("current_observation", observation)))
        public = record["public_capture_linkage"]
        for capture_kind in ("detail", "commit"):
            receipt = public.get(capture_kind)
            if not isinstance(receipt, dict):
                continue
            capture_id = "capture:" + receipt["custody_id"]
            url = f"https://api.github.com/repos/anthropics/claude-for-legal/pulls/{pr_number}" if capture_kind == "detail" else f"https://api.github.com/repos/anthropics/claude-for-legal/commits/{record['merge_commit_sha']}"
            target = pr_id
            if capture_kind == "commit":
                sha = record["merge_commit_sha"]
                target = f"commit:git:{sha}"
                graph.add_node(node(target, "commit", {"sha": sha, "repository_id": REPOSITORY_NODE}, authority="primary_source", classification="public_primary", creation_method="git_object", review_state="reviewed", evidence_refs=[receipt["custody_id"]], observation_time=receipt["observed_at"], freshness=fresh("immutable")))
                graph.add_relation(pr_id, "AT_REVISION", target, "The verified merged PR detail and public commit capture agree on this merge commit.", "The link does not establish reviewer intent or product strategy.", evidence_refs=[receipt["custody_id"]], review_state="reviewed", observation_time=receipt["observed_at"], authority="registered_source", classification="public_normalized", creation_method="public_capture_receipt")
            graph.add_node(node(capture_id, "capture", {"capture_kind": f"github_pr_{capture_kind}", "custody_id": receipt["custody_id"], "sha256": receipt["sha256"], "url": url}, authority="registered_source", classification="public_normalized", creation_method="public_capture_receipt", review_state="reviewed", evidence_refs=[receipt["custody_id"]], observation_time=receipt["observed_at"], freshness=fresh("current_observation", receipt["observed_at"])))
            graph.add_relation(capture_id, "CAPTURED_FROM", target, f"The hash-verified public GitHub {capture_kind} observation was captured from this record.", "The observation is bounded in time and does not prove complete or deleted history.", evidence_refs=[receipt["custody_id"]], review_state="reviewed", observation_time=receipt["observed_at"], authority="registered_source", classification="public_normalized", creation_method="public_capture_receipt")
        files_receipt = public.get("files")
        if isinstance(files_receipt, dict):
            for custody, page_hash, observed in zip(files_receipt.get("custody_ids", []), files_receipt.get("page_sha256", []), files_receipt.get("observed_at", []), strict=True):
                capture_id = "capture:" + custody
                url = f"https://api.github.com/repos/anthropics/claude-for-legal/pulls/{pr_number}/files"
                graph.add_node(node(capture_id, "capture", {"capture_kind": "github_pr_files_page", "custody_id": custody, "sha256": page_hash, "url": url}, authority="registered_source", classification="public_normalized", creation_method="public_capture_receipt", review_state="reviewed", evidence_refs=[custody], observation_time=observed, freshness=fresh("current_observation", observed)))
                graph.add_relation(capture_id, "CAPTURED_FROM", pr_id, "The terminally verified public PR-file page was captured from this PR.", "The file list does not establish strategy, intent, or runtime behavior.", evidence_refs=[custody], review_state="reviewed", observation_time=observed, authority="registered_source", classification="public_normalized", creation_method="public_capture_receipt")
        if status == "linked_verified_capture":
            commit_id = f"commit:git:{record['merge_commit_sha']}"
            for path in git_paths(record["base_sha"], record["merge_commit_sha"]):
                file_id = file_node_id(path)
                if file_id not in graph.nodes:
                    graph.add_node(node(file_id, "file", {"repository_id": REPOSITORY_NODE, "path": path, "git_blob_oid": None, "content_sha256": None}, authority="primary_source", classification="public_primary", creation_method="git_object", review_state="reviewed", freshness=fresh("immutable")))
                basis = "The verified base-to-merge Git comparison records this path as modified."
                limitation = "Path modification does not establish feature strategy, semantic importance, or runtime use."
                graph.add_relation(pr_id, "MODIFIES_PATH", file_id, basis, limitation, review_state="reviewed", authority="deterministic_derivative", classification="public_normalized", creation_method="git_object")
                graph.add_relation(commit_id, "MODIFIES_PATH", file_id, basis, limitation, review_state="reviewed", authority="deterministic_derivative", classification="public_normalized", creation_method="git_object")

    edges = graph.finalized_edges()
    nodes = [graph.nodes[key] for key in sorted(graph.nodes)]
    graph_payload = {
        "schema": "claude-legal-audit.evidence-graph.v1",
        "revision": REVISION,
        "status": "candidate",
        "edge_library_sha256": digest(EDGE_LIBRARY.read_bytes()),
        "input_sha256": {path.relative_to(ROOT).as_posix(): digest(path.read_bytes()) for path in (CHUNKS, SOURCES, CLAIMS, ARGUMENTS, PR_LINKAGE)},
        "summary": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "node_type_counts": dict(sorted(Counter(item["node_type"] for item in nodes).items())),
            "edge_type_counts": dict(sorted(Counter(item["edge_type"] for item in edges).items())),
            "eligible_claim_count": sum(claim["publication_eligibility"] == "eligible" for claim in claims["claims"]),
            "blocked_claim_count": sum(claim["publication_eligibility"] != "eligible" for claim in claims["claims"]),
        },
        "nodes": nodes,
        "edges": edges,
        "limitations": [
            "The graph is a deterministic candidate projection; generated edges do not promote truth or authority.",
            "Only the pinned anthropics/claude-for-legal revision and registered public observations are in repository-history scope.",
            "Similarity, centrality, and graph connectivity are never sufficient to promote a claim or edge.",
            "Raw captures, private paths, client material, and conversations are excluded from this public candidate artifact."
        ],
    }
    return graph_payload


def has_cycle(adjacency: dict[str, set[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(current: str) -> bool:
        if current in visiting: return True
        if current in visited: return False
        visiting.add(current)
        if any(visit(target) for target in adjacency.get(current, set())): return True
        visiting.remove(current); visited.add(current); return False
    return any(visit(node_id) for node_id in list(adjacency))


def validate(payload: dict) -> list[str]:
    schema = load(SCHEMA)
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(payload)]
    library = load(EDGE_LIBRARY)
    library_errors = [error.message for error in Draft202012Validator(load(EDGE_SCHEMA)).iter_errors(library)]
    errors.extend(f"edge library: {message}" for message in library_errors)
    relations: dict[str, tuple[str, list[str], list[str], str]] = {}
    forward_cycle_relations = set()
    for pair in library["pairs"]:
        relations[pair["forward"]] = (pair["inverse"], pair["source_types"], pair["target_types"], pair["forward"])
        relations[pair["inverse"]] = (pair["forward"], pair["target_types"], pair["source_types"], pair["forward"])
        if pair["cycle_policy"] == "forbidden_forward": forward_cycle_relations.add(pair["forward"])
    nodes = payload.get("nodes", [])
    node_by_id = {item.get("node_id"): item for item in nodes if isinstance(item, dict)}
    if len(node_by_id) != len(nodes): errors.append("node IDs must be unique")
    for item in nodes:
        if item.get("node_type") != item.get("attributes", {}).get("kind"):
            errors.append(f"node contract kind mismatch: {item.get('node_id')}")
        if item.get("node_type") == "file":
            path = item.get("attributes", {}).get("path")
            if not isinstance(path, str) or item.get("node_id") != file_node_id(path):
                errors.append(f"stale file node identity: {item.get('node_id')}")
    edges = payload.get("edges", [])
    edge_by_id = {item.get("edge_id"): item for item in edges if isinstance(item, dict)}
    if len(edge_by_id) != len(edges): errors.append("edge IDs must be unique")
    adjacency: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    authority_rank = {"candidate_analysis": 1, "deterministic_derivative": 2, "registered_source": 3, "primary_source": 4}
    for edge in edges:
        source, target, relation = edge.get("source_node_id"), edge.get("target_node_id"), edge.get("edge_type")
        if source not in node_by_id or target not in node_by_id: errors.append(f"unknown graph edge endpoint: {edge.get('edge_id')}"); continue
        if source == target: errors.append(f"self edge forbidden: {edge.get('edge_id')}")
        if edge.get("edge_id") != edge_identifier(relation, source, target): errors.append(f"stale edge identity: {edge.get('edge_id')}")
        contract = relations.get(relation)
        if contract is None: errors.append(f"edge type absent from library: {relation}"); continue
        inverse_type, source_types, target_types, forward = contract
        if node_by_id[source]["node_type"] not in source_types: errors.append(f"edge source type violates {relation}: {source}")
        if node_by_id[target]["node_type"] not in target_types: errors.append(f"edge target type violates {relation}: {target}")
        edge_rank = authority_rank.get(edge.get("authority"), 0)
        endpoint_rank = min(authority_rank.get(node_by_id[source].get("authority"), 0), authority_rank.get(node_by_id[target].get("authority"), 0))
        if edge_rank > endpoint_rank:
            errors.append(f"authority inversion on edge: {edge.get('edge_id')}")
        inverse = edge_by_id.get(edge.get("inverse_edge_id"))
        if not inverse or inverse.get("edge_type") != inverse_type or inverse.get("source_node_id") != target or inverse.get("target_node_id") != source or inverse.get("inverse_edge_id") != edge.get("edge_id"):
            errors.append(f"missing required inverse: {edge.get('edge_id')}")
        if relation == forward and relation in forward_cycle_relations:
            adjacency[relation][source].add(target)
    for relation, links in adjacency.items():
        if has_cycle(links): errors.append(f"forbidden {relation} cycle")
    claims = load(CLAIMS)
    edge_keys = {(edge.get("source_node_id"), edge.get("edge_type"), edge.get("target_node_id")) for edge in edges}
    for claim in claims["claims"]:
        claim_id = claim["claim_id"]
        for evidence in claim["evidence"]:
            source = evidence["source_id"]
            if not any((source, relation, claim_id) in edge_keys for relation in ("EVIDENCES", "CONSTRAINS", "LEAVES_UNKNOWN")):
                errors.append(f"unsupported source-to-claim path: {source} -> {claim_id}")
        if claim["publication_eligibility"] == "eligible":
            exact = False
            for evidence in claim["evidence"]:
                source_id = evidence["source_id"]
                for source, relation, target in edge_keys:
                    if source != source_id or relation != "LOCATES":
                        continue
                    if node_by_id.get(target, {}).get("node_type") != "chunk":
                        continue
                    locator_edge = edge_by_id.get(edge_identifier("LOCATES", source_id, target))
                    supporting_edge = edge_by_id.get(edge_identifier("EVIDENCES", target, claim_id))
                    chunk_node = node_by_id.get(target, {})
                    file_id = chunk_node.get("attributes", {}).get("parent_file_id")
                    hash_edge = edge_by_id.get(edge_identifier("HASH_BINDS", target, file_id)) if file_id else None
                    reviewed_chain = (
                        locator_edge,
                        edge_by_id.get(locator_edge.get("inverse_edge_id")) if locator_edge else None,
                        supporting_edge,
                        edge_by_id.get(supporting_edge.get("inverse_edge_id")) if supporting_edge else None,
                        hash_edge,
                        edge_by_id.get(hash_edge.get("inverse_edge_id")) if hash_edge else None,
                    )
                    reproducible_chunk = (
                        chunk_node.get("authority") == "deterministic_derivative"
                        and chunk_node.get("creation_method") == "deterministic_builder"
                        and chunk_node.get("review_state") in {"candidate", "reviewed"}
                    )
                    if (
                        all(item and item.get("review_state") == "reviewed" for item in reviewed_chain)
                        and node_by_id.get(source_id, {}).get("review_state") == "reviewed"
                        and reproducible_chunk
                        and node_by_id.get(claim_id, {}).get("review_state") == "reviewed"
                    ):
                        exact = True
                        break
                if exact:
                    break
            bounded = claim["review_state"] == "reviewed" and claim["epistemic_status"] in {"hypothesis", "normative", "counterevidence", "unknown"}
            if not exact and not bounded: errors.append(f"eligible claim lacks exact reproducible genealogy: {claim_id}")
    for violation in public_content_violations(payload):
        errors.append(f"forbidden public graph content: {violation}")
    expected_summary = payload.get("summary", {})
    if expected_summary.get("node_count") != len(nodes) or expected_summary.get("edge_count") != len(edges): errors.append("graph summary counts are stale")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_graph()
    errors = validate(payload)
    if errors:
        print("ERROR: evidence graph invalid:\n" + "\n".join(errors[:100]), file=sys.stderr)
        return 1
    data = canonical(payload)
    if args.check:
        if not OUT.exists() or OUT.read_bytes() != data:
            print("ERROR: evidence graph is stale; run scripts/build_evidence_graph.py", file=sys.stderr)
            return 1
        print(f"evidence graph current: {len(payload['nodes'])} nodes, {len(payload['edges'])} edges")
        return 0
    OUT.write_bytes(data)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(payload['nodes'])} nodes, {len(payload['edges'])} edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
