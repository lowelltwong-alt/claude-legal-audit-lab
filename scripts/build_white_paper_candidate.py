#!/usr/bin/env python3
"""Build a blocked, positive-allowlist paper preview and self-contained explorer."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from public_safety import public_content_violations

ROOT = Path(__file__).resolve().parents[1]
THESIS = ROOT / "registry" / "thesis-map.json"
CLAIMS = ROOT / "registry" / "claim-registry.json"
SOURCES = ROOT / "registry" / "source-registry.json"
GRAPH = ROOT / "registry" / "evidence-graph.json"
PR_LINKAGE = ROOT / "results" / "pr-commit-diff-linkage.json"
RELEASE = ROOT / "registry" / "release-readiness.json"
SCHEMA = ROOT / "schemas" / "white-paper-export.schema.json"
OUT = ROOT / "registry" / "white-paper-export.json"
CANDIDATE_DIR = ROOT / "public" / "generated-release-artifacts" / "candidate"
PAPER = CANDIDATE_DIR / "white-paper.md"
EXPLORER = CANDIDATE_DIR / "index.html"
ALLOWLIST = [
    "schema", "revision", "status", "title", "release", "evidence_coverage",
    "allowlist", "input_sha256", "content_sha256", "sections", "paragraphs",
    "thesis_nodes", "argument_objects", "graph_edges", "claims", "sources",
    "chunks", "contribution_lanes",
]
MOJIBAKE = ("\ufffd", "\u00c2", "\u00c3", "\u00e2", "\u251c", "\u2562", "\u0442\u0410")


def canonical(payload: object, *, compact: bool = False) -> bytes:
    if compact:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_claim(claim: dict) -> dict:
    return {key: claim[key] for key in ("claim_id", "lifecycle", "epistemic_status", "review_state", "publication_eligibility", "proposition", "evidence", "does_not_prove")}


def selected_source(source: dict) -> dict:
    return {key: source[key] for key in ("source_id", "title", "publisher", "url", "source_class", "accessed_at", "locator", "revision_binding", "status", "limitation")}


def selected_thesis_node(item: dict, argument_ids: list[str]) -> dict:
    selected = {key: item[key] for key in ("stable_id", "order", "role", "proposition", "epistemic_status", "claim_ids", "evidence_paths", "objections", "falsifiers", "does_not_prove", "proof_gaps", "paper_sections", "review_state", "export_eligibility")}
    selected["argument_ids"] = argument_ids
    return selected


def selected_argument(node: dict) -> dict:
    attributes = node["attributes"]
    return {
        "argument_id": node["node_id"],
        "node_type": node["node_type"],
        "argument_type": attributes.get("argument_type", node["node_type"]),
        "title": attributes["title"],
        "statement": attributes["statement"],
        "epistemic_status": attributes.get("epistemic_status", "Unknown"),
        "review_state": node["review_state"],
        "evidence_refs": node["evidence_refs"],
    }


def selected_graph_edge(edge: dict) -> dict:
    return {key: edge[key] for key in ("edge_id", "inverse_edge_id", "source_node_id", "edge_type", "target_node_id", "review_state")}


def content_projection(payload: dict) -> dict:
    return {key: payload[key] for key in ("sections", "paragraphs", "thesis_nodes", "argument_objects", "graph_edges", "claims", "sources", "chunks", "contribution_lanes")}


def build_export() -> dict:
    thesis = load(THESIS)
    claims_raw = load(CLAIMS)
    sources_raw = load(SOURCES)
    graph = load(GRAPH)
    linkage = load(PR_LINKAGE)
    release = load(RELEASE)
    claims_by_id = {claim["claim_id"]: claim for claim in claims_raw["claims"]}
    sources_by_id = {source["source_id"]: source for source in sources_raw["sources"]}
    graph_nodes = {node["node_id"]: node for node in graph["nodes"]}
    graph_edges = {(edge["source_node_id"], edge["edge_type"], edge["target_node_id"]): edge for edge in graph["edges"]}

    paragraphs = []
    referenced_sources: set[str] = set()
    referenced_chunks: set[str] = set()
    referenced_claims: set[str] = set()
    referenced_arguments: set[str] = set()
    for item in thesis["nodes"]:
        claim_ids = sorted(item["claim_ids"])
        referenced_claims.update(claim_ids)
        source_ids = {evidence["source_id"] for claim_id in claim_ids for evidence in claims_by_id[claim_id]["evidence"]}
        chunk_ids: set[str] = set()
        argument_ids = set(item["objections"] + item["falsifiers"] + item["proof_gaps"])
        path_ids, edge_ids = [], []
        for path in item["evidence_paths"]:
            path_ids.append(path["path_id"])
            for node_id in path["node_ids"]:
                if node_id.startswith("SRC-"): source_ids.add(node_id)
                elif node_id.startswith("chk:sha256:"): chunk_ids.add(node_id)
                elif node_id.startswith(("ARG-", "OBJ-", "REB-", "FAL-", "GAP-", "THS-", "THY-")): argument_ids.add(node_id)
            for source, relation, target in zip(path["node_ids"][:-1], path["edge_types"], path["node_ids"][1:], strict=True):
                edge_ids.append(graph_edges[(source, relation, target)]["edge_id"])
        referenced_sources.update(source_ids); referenced_chunks.update(chunk_ids)
        referenced_arguments.update(argument_ids)
        locators = []
        hashes = []
        for claim_id in claim_ids:
            for evidence in claims_by_id[claim_id]["evidence"]:
                locators.append({key: evidence[key] for key in ("source_id", "locator", "locator_kind", "evidence_grade")})
        for source_id in sorted(source_ids):
            binding_hash = sources_by_id[source_id].get("revision_binding", {}).get("content_sha256")
            if isinstance(binding_hash, str): hashes.append(binding_hash)
        for chunk_id in sorted(chunk_ids):
            chunk = graph_nodes[chunk_id]
            attrs = chunk["attributes"]
            file_node = graph_nodes[attrs["parent_file_id"]]
            locators.append({"chunk_id": chunk_id, "path": file_node["attributes"]["path"], "locator": attrs["locator"], "content_sha256": attrs["content_sha256"]})
            hashes.append(attrs["content_sha256"])
        genealogy = {
            "thesis_node_ids": [item["stable_id"]],
            "argument_ids": sorted(argument_ids),
            "claim_ids": claim_ids,
            "graph_path_ids": sorted(path_ids),
            "graph_edge_ids": sorted(set(edge_ids)),
            "source_ids": sorted(source_ids),
            "chunk_ids": sorted(chunk_ids),
            "locators": locators,
            "content_hashes": sorted(set(hashes)),
        }
        paragraphs.append({
            "paragraph_id": f"WPP-{item['order']:04d}",
            "section_id": item["paper_sections"][0],
            "order": item["order"],
            "label": item["epistemic_status"],
            "text": item["proposition"],
            "does_not_prove": item["does_not_prove"],
            "review_state": item["review_state"],
            "publication_eligibility": item["export_eligibility"],
            "genealogy": genealogy,
            "genealogy_sha256": sha(canonical(genealogy, compact=True)),
        })

    for argument_id in sorted(referenced_arguments):
        for reference in graph_nodes[argument_id]["evidence_refs"]:
            if reference.startswith("CLM-") and reference in claims_by_id:
                referenced_claims.add(reference)
            elif reference.startswith("SRC-") and reference in sources_by_id:
                referenced_sources.add(reference)
    for claim_id in sorted(referenced_claims):
        referenced_sources.update(evidence["source_id"] for evidence in claims_by_id[claim_id]["evidence"])

    chunks = []
    for chunk_id in sorted(referenced_chunks):
        chunk = graph_nodes[chunk_id]
        attrs = chunk["attributes"]
        file_node = graph_nodes[attrs["parent_file_id"]]
        chunks.append({"chunk_id": chunk_id, "chunk_kind": attrs["chunk_kind"], "content_sha256": attrs["content_sha256"], "parent_file_id": attrs["parent_file_id"], "path": file_node["attributes"]["path"], "locator": attrs["locator"], "source_ids": chunk["evidence_refs"]})
    section_ids = sorted({paragraph["section_id"] for paragraph in paragraphs})
    sections = [
        {
            "section_id": section_id,
            "order": index,
            "title": graph_nodes[section_id]["attributes"]["title"],
            "paragraph_ids": [paragraph["paragraph_id"] for paragraph in paragraphs if paragraph["section_id"] == section_id],
        }
        for index, section_id in enumerate(section_ids, start=1)
    ]
    public_node_ids = referenced_sources | referenced_chunks | referenced_claims | referenced_arguments | set(section_ids)
    argument_objects = [selected_argument(graph_nodes[argument_id]) for argument_id in sorted(referenced_arguments)]
    graph_edges = [
        selected_graph_edge(edge)
        for edge in graph["edges"]
        if edge["source_node_id"] in public_node_ids and edge["target_node_id"] in public_node_ids
    ]
    lanes = [
        ("LANE-0001", "Source corrections"), ("LANE-0002", "Contrary evidence"),
        ("LANE-0003", "Falsifiers"), ("LANE-0004", "Runtime evidence"),
        ("LANE-0005", "Upstream history capture"), ("LANE-0006", "Analogous-industry research"),
        ("LANE-0007", "Chunk and graph tooling"),
    ]
    payload = {
        "schema": "claude-legal-audit.white-paper-export.v1",
        "revision": "1.1.0",
        "status": "blocked_unpublished_candidate",
        "title": "The Ajax Line",
        "release": {
            "release_eligible": False,
            "status": "blocked",
            "blockers": release["release_blockers"],
            "human_decisions": [{key: decision[key] for key in ("decision_id", "subject", "status")} for decision in release["decisions"]],
        },
        "evidence_coverage": {
            "claim_count": len(claims_raw["claims"]),
            "eligible_claim_count": sum(claim["publication_eligibility"] == "eligible" for claim in claims_raw["claims"]),
            "blocked_claim_count": sum(claim["publication_eligibility"] != "eligible" for claim in claims_raw["claims"]),
            "thesis_node_count": len(thesis["nodes"]),
            "eligible_thesis_node_count": sum(item["export_eligibility"] == "eligible" for item in thesis["nodes"]),
            "verified_merged_pr_count": linkage["summary"]["publicly_linked_capture_count"],
            "open_unmerged_snapshot_count": linkage["summary"]["captured_open_or_unmerged_snapshot_count"],
            "unknown_pr_count": linkage["summary"]["public_linkage_unknown_count"],
        },
        "allowlist": ALLOWLIST,
        "input_sha256": {path.relative_to(ROOT).as_posix(): sha(path.read_bytes()) for path in (THESIS, CLAIMS, SOURCES, GRAPH, PR_LINKAGE, RELEASE)},
        "content_sha256": "0" * 64,
        "sections": sections,
        "paragraphs": paragraphs,
        "thesis_nodes": [
            selected_thesis_node(
                item,
                next(paragraph["genealogy"]["argument_ids"] for paragraph in paragraphs if paragraph["genealogy"]["thesis_node_ids"] == [item["stable_id"]]),
            )
            for item in thesis["nodes"]
        ],
        "argument_objects": argument_objects,
        "graph_edges": graph_edges,
        "claims": [selected_claim(claims_by_id[claim_id]) for claim_id in sorted(referenced_claims)],
        "sources": [selected_source(sources_by_id[source_id]) for source_id in sorted(referenced_sources)],
        "chunks": chunks,
        "contribution_lanes": [{"lane_id": lane_id, "title": title, "required_fields": ["source_url", "source_revision_or_observation_time", "reproducible_locator", "classification", "content_hash_or_reason_unavailable"], "status": "draft_inactive"} for lane_id, title in lanes],
    }
    payload["content_sha256"] = sha(canonical(content_projection(payload), compact=True))
    return payload


def validate(payload: dict) -> list[str]:
    errors = [error.message for error in Draft202012Validator(load(SCHEMA)).iter_errors(payload)]
    if list(payload.keys()) != sorted(payload.keys()):
        # Canonical serialization sorts keys; construction order is intentionally irrelevant.
        pass
    if sorted(payload.keys()) != sorted(ALLOWLIST): errors.append("export top-level fields are not the positive allowlist")
    if payload.get("content_sha256") != sha(canonical(content_projection(payload), compact=True)): errors.append("export content_sha256 is stale")
    paragraphs = payload.get("paragraphs", [])
    paragraph_ids = [item.get("paragraph_id") for item in paragraphs]
    if len(paragraph_ids) != len(set(paragraph_ids)): errors.append("paragraph IDs must be unique")
    claims = {claim.get("claim_id"): claim for claim in payload.get("claims", [])}
    sources = {source.get("source_id"): source for source in payload.get("sources", [])}
    chunks = {chunk.get("chunk_id"): chunk for chunk in payload.get("chunks", [])}
    thesis = {item.get("stable_id"): item for item in payload.get("thesis_nodes", [])}
    arguments = {item.get("argument_id"): item for item in payload.get("argument_objects", [])}
    graph_edges = {item.get("edge_id"): item for item in payload.get("graph_edges", [])}
    public_node_ids = set(claims) | set(sources) | set(chunks) | set(arguments) | {item.get("section_id") for item in payload.get("sections", [])}
    for paragraph in paragraphs:
        genealogy = paragraph.get("genealogy", {})
        if paragraph.get("genealogy_sha256") != sha(canonical(genealogy, compact=True)): errors.append(f"stale paragraph genealogy hash: {paragraph.get('paragraph_id')}")
        if not genealogy.get("graph_edge_ids") or not genealogy.get("graph_path_ids") or not genealogy.get("locators"): errors.append(f"incomplete paragraph genealogy: {paragraph.get('paragraph_id')}")
        for reference in genealogy.get("claim_ids", []):
            if reference not in claims: errors.append(f"paragraph references absent claim: {reference}")
        for reference in genealogy.get("source_ids", []):
            if reference not in sources: errors.append(f"paragraph references absent source: {reference}")
        for reference in genealogy.get("chunk_ids", []):
            if reference not in chunks: errors.append(f"paragraph references absent chunk: {reference}")
        for reference in genealogy.get("thesis_node_ids", []):
            if reference not in thesis: errors.append(f"paragraph references absent thesis node: {reference}")
        for reference in genealogy.get("argument_ids", []):
            if reference not in arguments: errors.append(f"paragraph references absent argument object: {reference}")
        if paragraph.get("publication_eligibility") == "eligible":
            if paragraph.get("review_state") != "reviewed": errors.append(f"eligible paragraph is unreviewed: {paragraph.get('paragraph_id')}")
            if any(claims[claim_id]["publication_eligibility"] != "eligible" for claim_id in genealogy["claim_ids"]): errors.append(f"eligible paragraph includes blocked claim: {paragraph.get('paragraph_id')}")
    for item in payload.get("thesis_nodes", []):
        for reference in item.get("argument_ids", []):
            if reference not in arguments: errors.append(f"thesis references absent argument object: {reference}")
        expected_argument_ids = sorted({
            reference
            for paragraph in paragraphs
            if item.get("stable_id") in paragraph.get("genealogy", {}).get("thesis_node_ids", [])
            for reference in paragraph.get("genealogy", {}).get("argument_ids", [])
        })
        if item.get("argument_ids") != expected_argument_ids:
            errors.append(f"thesis argument projection is incomplete: {item.get('stable_id')}")
    for edge in graph_edges.values():
        if edge.get("source_node_id") not in public_node_ids or edge.get("target_node_id") not in public_node_ids:
            errors.append(f"export graph edge references absent endpoint: {edge.get('edge_id')}")
        inverse = graph_edges.get(edge.get("inverse_edge_id"))
        if not inverse or inverse.get("inverse_edge_id") != edge.get("edge_id"):
            errors.append(f"export graph edge lacks inverse: {edge.get('edge_id')}")
    for violation in public_content_violations(payload):
        errors.append(f"forbidden export content: {violation}")
    rendered = canonical(payload).decode("utf-8", errors="strict")
    for marker in MOJIBAKE:
        if marker in rendered: errors.append(f"mojibake marker in export: {marker!r}")
    if payload.get("release", {}).get("release_eligible") is not False: errors.append("candidate export must remain release-ineligible")
    return errors


def paper_markdown(payload: dict) -> bytes:
    lines = [
        "<!-- Generated by scripts/build_white_paper_candidate.py; do not hand-edit. -->",
        "# The Ajax Line",
        "",
        "> **Blocked, unpublished research candidate.** This document is not a factual accusation, legal advice, or an authorized public release.",
        "",
        f"Evidence gate: {payload['evidence_coverage']['eligible_claim_count']} of {payload['evidence_coverage']['claim_count']} claims eligible; {payload['evidence_coverage']['eligible_thesis_node_count']} of {payload['evidence_coverage']['thesis_node_count']} thesis nodes eligible.",
        "",
    ]
    for paragraph in payload["paragraphs"]:
        genealogy = paragraph["genealogy"]
        lines.extend([
            f"## {paragraph['paragraph_id']} · {paragraph['label'].upper()}",
            "",
            paragraph["text"],
            "",
            f"**Boundary:** {paragraph['does_not_prove']}",
            "",
            f"Genealogy: thesis {', '.join(genealogy['thesis_node_ids'])}; claims {', '.join(genealogy['claim_ids'])}; sources {', '.join(genealogy['source_ids'])}; paths {', '.join(genealogy['graph_path_ids'])}; hash `{paragraph['genealogy_sha256']}`.",
            "",
        ])
    lines.extend([
        "## Release boundary",
        "",
        f"Release remains blocked with {len(payload['release']['blockers'])} registered decision/receipt blocker IDs; the readiness validator may report additional derived conditions. Human approval of an exact frozen export hash is mandatory and has not been supplied.",
        "",
        "Move 37 is analogy and benchmark motivation only. Iliad and Trojan-War material is outside the causal evidence chain.",
        "",
    ])
    return "\n".join(lines).encode("utf-8")


def explorer_html(payload: dict) -> bytes:
    embedded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    title = html.escape(payload["title"])
    document = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ · blocked evidence explorer</title>
<style>
:root{--ink:#18202a;--muted:#5c6877;--paper:#f6f3ec;--card:#fff;--line:#d6d0c4;--red:#9b2c2c;--amber:#9a6700;--blue:#275dad}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 system-ui,sans-serif}header{padding:28px;max-width:1200px;margin:auto}h1{margin:0;font-size:clamp(30px,5vw,56px)}.status{border:2px solid var(--red);background:#fff1f1;padding:12px 16px;margin-top:14px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:18px}.card,section{background:var(--card);border:1px solid var(--line);padding:16px}.metric{font-size:28px;font-weight:700}main{max-width:1200px;margin:auto;padding:0 28px 40px;display:grid;grid-template-columns:minmax(260px,1fr) minmax(0,2fr);gap:18px}input{width:100%;padding:11px;border:1px solid var(--line);font:inherit}button{display:block;width:100%;text-align:left;padding:10px;margin:6px 0;border:1px solid var(--line);background:white;cursor:pointer}button:hover,button:focus{border-color:var(--blue)}button.ref{display:inline-block;width:auto;padding:4px 8px;margin:3px;border-radius:12px}code{word-break:break-all}.blocked{color:var(--red)}.unknown{color:var(--amber)}.stale{color:#6d4c9c}.missing,.malformed{color:var(--red);font-weight:700}.small{font-size:13px;color:var(--muted)}article{border-top:1px solid var(--line);padding-top:8px;margin-top:8px}@media(max-width:760px){main{grid-template-columns:1fr}}
</style></head><body>
<header><div class="small">READ-ONLY · LOCAL · NO EXTERNAL REQUESTS</div><h1>__TITLE__</h1><div id="state" class="status blocked">Blocked unpublished candidate. No release authorization exists.</div><div id="cards" class="cards"></div></header>
<main><section><h2>Exact-ID / lexical search</h2><input id="search" type="search" autocomplete="off" placeholder="SEC-0001, TMN-0004, CLM-0015, sector externality…"><div id="results"></div></section><section id="detail"><h2>Evidence map</h2><p>Drill-down: paper section → thesis → argument/objection/falsifier → claim → source/chunk locator.</p></section></main>
<script id="evidence-data" type="application/json">__DATA__</script>
<script>
(()=>{'use strict';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let data;const state=document.getElementById('state'),detail=document.getElementById('detail');
try{const raw=document.getElementById('evidence-data');if(!raw||!raw.textContent.trim()){state.className='status missing';state.textContent='Missing embedded evidence data.';return}data=JSON.parse(raw.textContent)}catch(e){state.className='status malformed';state.textContent='Malformed embedded evidence data.';return}
if(data.status.includes('stale')){state.className='status stale';state.textContent='Stale candidate data; rebuild required.'}else if(!data.release.release_eligible){state.className='status blocked';state.textContent=`BLOCKED · ${data.release.blockers.length} registered blocker IDs · content ${data.content_sha256.slice(0,12)}…`}
const c=data.evidence_coverage;document.getElementById('cards').innerHTML=[[c.eligible_claim_count,'eligible claims'],[c.eligible_thesis_node_count,'eligible thesis nodes'],[c.blocked_claim_count,'blocked claims'],[c.verified_merged_pr_count,'verified merged PRs'],[c.open_unmerged_snapshot_count,'open/unmerged'],[c.unknown_pr_count,'unknown PRs']].map(x=>`<div class="card"><div class="metric">${x[0]}</div><div>${x[1]}</div></div>`).join('');
const wrap=(id,type,value)=>({id,type,text:JSON.stringify(value),value});
const items=[...data.sections.map(x=>wrap(x.section_id,'section',x)),...data.paragraphs.map(x=>wrap(x.paragraph_id,'paragraph',x)),...data.thesis_nodes.map(x=>wrap(x.stable_id,'thesis',x)),...data.argument_objects.map(x=>wrap(x.argument_id,'argument',x)),...data.claims.map(x=>wrap(x.claim_id,'claim',x)),...data.sources.map(x=>wrap(x.source_id,'source',x)),...data.chunks.map(x=>wrap(x.chunk_id,'chunk',x)),...data.graph_edges.map(x=>wrap(x.edge_id,'edge',x))];
const byId=Object.fromEntries(items.map(x=>[x.id,x])),edges=data.graph_edges;
const ref=(id,label=id)=>byId[id]?`<button class="ref" data-id="${esc(id)}">${esc(label)}</button>`:`<span class="unknown">${esc(id)} (missing)</span>`;
const refs=ids=>[...new Set(ids)].map(id=>ref(id)).join('');
const relations=id=>edges.filter(e=>e.source_node_id===id).map(e=>`<article><code>${esc(e.edge_type)}</code> ${ref(e.target_node_id)}<div class="small">${ref(e.edge_id,e.edge_id.slice(0,24)+'…')}</div></article>`).join('')||'<p class="small">No allowlisted outgoing edge.</p>';
function wire(){detail.querySelectorAll('[data-id]').forEach(button=>button.addEventListener('click',()=>show(byId[button.dataset.id])))}
function show(item){if(!item)return;const v=item.value;let body='';
if(item.type==='section'){const paragraphs=v.paragraph_ids.map(id=>byId[id].value),thesis=paragraphs.flatMap(p=>p.genealogy.thesis_node_ids);body=`<div class="small">paper section</div><h2>${esc(v.section_id)} · ${esc(v.title)}</h2><h3>Paragraphs</h3>${refs(v.paragraph_ids)}<h3>Thesis nodes</h3>${refs(thesis)}`}
else if(item.type==='paragraph'){const g=v.genealogy;body=`<div class="small">${esc(v.paragraph_id)} · ${esc(v.label)} · <span class="blocked">${esc(v.publication_eligibility)}</span></div><h2>${esc(v.text)}</h2><p><b>Does not prove:</b> ${esc(v.does_not_prove)}</p><h3>Thesis</h3>${refs(g.thesis_node_ids)}<h3>Arguments, objections, falsifiers, proof gaps</h3>${refs(g.argument_ids)}<h3>Claims</h3>${refs(g.claim_ids)}<h3>Sources and chunks</h3>${refs([...g.source_ids,...g.chunk_ids])}<h3>Genealogy hash</h3><code>${esc(v.genealogy_sha256)}</code>`}
else if(item.type==='thesis'){body=`<div class="small">thesis node · ${esc(v.epistemic_status)} · <span class="blocked">${esc(v.export_eligibility)}</span></div><h2>${esc(v.stable_id)} · ${esc(v.role)}</h2><p>${esc(v.proposition)}</p><p><b>Does not prove:</b> ${esc(v.does_not_prove)}</p><h3>Supporting, rebuttal, objection, falsifier, and proof-gap arguments</h3>${refs(v.argument_ids)}<h3>Claims</h3>${refs(v.claim_ids)}<h3>Paper section</h3>${refs(v.paper_sections)}`}
else if(item.type==='argument'){body=`<div class="small">${esc(v.node_type)} · ${esc(v.argument_type)} · ${esc(v.epistemic_status)} · ${esc(v.review_state)}</div><h2>${esc(v.argument_id)} · ${esc(v.title)}</h2><p>${esc(v.statement)}</p><h3>Registered evidence references</h3>${refs(v.evidence_refs)}<h3>Typed relationships</h3>${relations(v.argument_id)}`}
else if(item.type==='claim'){const sourceIds=v.evidence.map(e=>e.source_id),chunkIds=edges.filter(e=>e.edge_type==='EVIDENCES'&&e.target_node_id===v.claim_id&&String(e.source_node_id).startsWith('chk:')).map(e=>e.source_node_id);body=`<div class="small">claim · ${esc(v.epistemic_status)} · ${esc(v.lifecycle)} · <span class="blocked">${esc(v.publication_eligibility)}</span></div><h2>${esc(v.claim_id)}</h2><p>${esc(v.proposition)}</p><p><b>Does not prove:</b> ${esc(v.does_not_prove)}</p><h3>Sources</h3>${refs(sourceIds)}<h3>Exact chunks</h3>${refs(chunkIds)}<h3>Typed relationships</h3>${relations(v.claim_id)}`}
else if(item.type==='source'){body=`<div class="small">primary/source record · ${esc(v.status)}</div><h2>${esc(v.source_id)} · ${esc(v.title)}</h2><p>${esc(v.locator)}</p><div class="small">${esc(v.url)}</div><p><b>Limitation:</b> ${esc(v.limitation)}</p><h3>Located chunks and bounded claims</h3>${relations(v.source_id)}`}
else if(item.type==='chunk'){body=`<div class="small">byte-exact chunk</div><h2><code>${esc(v.chunk_id)}</code></h2><p>${esc(v.path)} · bytes ${esc(v.locator.byte_start)}–${esc(v.locator.byte_end_exclusive)}</p><code>${esc(v.content_sha256)}</code><h3>Typed relationships</h3>${relations(v.chunk_id)}`}
else if(item.type==='edge'){body=`<div class="small">typed graph edge · ${esc(v.review_state)}</div><h2><code>${esc(v.edge_id)}</code></h2>${ref(v.source_node_id)} <code>${esc(v.edge_type)}</code> ${ref(v.target_node_id)}<p>Inverse: ${ref(v.inverse_edge_id)}</p>`}
else{body=`<h2>${esc(item.id)}</h2><pre>${esc(JSON.stringify(v,null,2))}</pre>`}
detail.innerHTML=body;wire()}
function search(){const q=document.getElementById('search').value.trim().toLowerCase();let found=q?items.filter(x=>x.id.toLowerCase()===q):[...data.sections.map(x=>byId[x.section_id]),...data.paragraphs.map(x=>byId[x.paragraph_id])];if(q&&!found.length)found=items.filter(x=>x.text.toLowerCase().includes(q)).slice(0,40);document.getElementById('results').innerHTML='';found.forEach(item=>{const b=document.createElement('button');b.textContent=`${item.id} · ${item.type}`;b.addEventListener('click',()=>show(item));document.getElementById('results').appendChild(b)})}
function firstScreen(){detail.innerHTML='<h2>Evidence map</h2><p>Drill-down: paper section → thesis → argument/objection/falsifier → claim → source/chunk locator.</p><h3>Pending human decisions</h3>'+data.release.human_decisions.map(x=>`<div><code>${esc(x.decision_id)}</code> ${esc(x.subject)} · <span class="unknown">${esc(x.status)}</span></div>`).join('')+'<h3>Registered blocker IDs</h3>'+data.release.blockers.map(x=>`<code>${esc(x)}</code> `).join('');wire()}
document.getElementById('search').addEventListener('input',search);search();firstScreen();
})();
</script></body></html>'''.replace("__TITLE__", title).replace("__DATA__", embedded)
    return document.encode("utf-8")


def validate_html(data: bytes) -> list[str]:
    text = data.decode("utf-8", errors="strict")
    errors = []
    for token in ("fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "<script src=", "<link rel=", "<form", "method=\"post\""):
        if token.lower() in text.lower(): errors.append(f"explorer external request or mutation token: {token}")
    for required in ("missing", "malformed", "stale", "blocked", "READ-ONLY", "NO EXTERNAL REQUESTS"):
        if required not in text: errors.append(f"explorer lacks distinct state marker: {required}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_export()
    errors = validate(payload)
    paper = paper_markdown(payload)
    explorer = explorer_html(payload)
    errors.extend(validate_html(explorer))
    if errors:
        print("ERROR: white-paper candidate invalid:\n" + "\n".join(errors), file=sys.stderr)
        return 1
    data = canonical(payload)
    if args.check:
        stale = [path.relative_to(ROOT).as_posix() for path, expected in ((OUT, data), (PAPER, paper), (EXPLORER, explorer)) if not path.exists() or path.read_bytes() != expected]
        if stale:
            print("ERROR: white-paper candidate artifacts stale: " + ", ".join(stale), file=sys.stderr)
            return 1
        print(f"white-paper candidate current: {len(payload['paragraphs'])} paragraphs; release blocked")
        return 0
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(data); PAPER.write_bytes(paper); EXPLORER.write_bytes(explorer)
    print(f"wrote blocked candidate: {len(payload['paragraphs'])} paragraphs, content {payload['content_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
