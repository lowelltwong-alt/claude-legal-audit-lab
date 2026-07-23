# AI route: findings → provenance → line-of-code proof

**Use this when another AI must understand the audit findings, their provenance, and the exact code/docs that support them.**

This is a **task route**, not a second front door. Always start at `AI_FRONT_DOOR.md`, then follow this path.

**Mode default:** read-only unless the owner authorizes writes.  
**Release:** stays `blocked`. Do not allege covert training. Do not contact Anthropic.

---

## 60-second orientation

| Layer | File | Role |
|---|---|---|
| Front door | `AI_FRONT_DOOR.md` | Official entry + genealogy contract |
| TOC | `AI_TABLE_OF_CONTENTS.md` | Shallow branch map |
| Protocol | `AGENTS.md` | Epistemic rules (H0/H1/H2; Confirmed/Inferred/Unknown) |
| Machine routes | `registry/ai-front-door-registry.json` | Task → path routing |
| Thesis (human) | `docs/THESIS_MAP.md` | Seven-node Ajax Line spine |
| Thesis (machine) | `registry/thesis-map.json` | Bounded thesis + evidence paths |
| Claims | `registry/claim-registry.json` | Propositions + locators + does_not_prove |
| Upstream pin | `UPSTREAM.lock.json` | Exact commit under audit |
| Line proof | `upstream/claude-for-legal/...` | Open the locator paths |

**Locked finding spine**

1. Design invites judgment capture → `CLM-0001`  
2. Covert training unproven → `CLM-0002` (reviewed), `CLM-0003`, `CLM-0010`  
3. Custody/governance is the live thesis → `registry/thesis-map.json` `#bounded_thesis`

---

## Required read order (findings + proof)

### Phase 1 — Authority (do not skip)

1. `AI_FRONT_DOOR.md`  
2. `AGENTS.md`  
3. `AI_TABLE_OF_CONTENTS.md` (skim)  
4. `registry/project-roadmap.json` — confirm Terminal Local / quiet hold / release blocked  
5. `registry/release-readiness.json` — confirm `status: blocked`

### Phase 2 — Findings (what is claimed)

6. `docs/THESIS_MAP.md` — one-page spine  
7. `registry/thesis-map.json` — machine thesis + path IDs (`TEP-####`)  
8. `registry/claim-registry.json` — read at least:

| Claim | Why |
|---|---|
| `CLM-0001` | Judgment-capture design |
| `CLM-0002` | Deploy script does **not** upload practice profiles / deviation logs (only reviewed+eligible claim) |
| `CLM-0003` | Terms counterevidence (no default training on Customer Content) |
| `CLM-0008` | Lock-in / H1 without proving H2 |
| `CLM-0010` | No registered evidence of covert ontology pooling |
| `CLM-0015` | Sector-externality **hypothesis** (weak) |
| `CLM-0017` | Runtime unknown |
| `CLM-0018` | Tenant config unknown |

9. Optional narrative: `audit/FINAL_REPORT.md`, `docs/AJAX_LINE_COLLECTIVE_BRAIN_TRUST.md`

### Phase 3 — Provenance (how a claim is allowed to exist)

For **each** claim you will cite, walk:

```text
claim_id in registry/claim-registry.json
  -> evidence[].source_id + locator (+ evidence_grade)
  -> registry/source-registry.json (source identity / capture limits)
  -> if path_lines / chunk: registry/chunk-registry.json or upstream file at UPSTREAM.lock commit
  -> optional: registry/evidence-graph.json edges (chunk ↔ claim ↔ thesis)
  -> optional: registry/derivation-registry.json for generated docs/exports
  -> thesis node in registry/thesis-map.json (TMN-#### / TEP-####)
```

**Hard rule:** a generated report, graph, or white-paper paragraph is **not** source truth until a claim binds it to an exact locator and states what it does **not** prove.

### Phase 4 — Line-of-code proof (open the files)

**Best strong proofs today**

| Finding | Claim | Open these paths under `upstream/claude-for-legal/` |
|---|---|---|
| Judgment capture | `CLM-0001` | `commercial-legal/skills/cold-start-interview/SKILL.md` (esp. seed docs + write practice profile; Purpose ~L70+) |
| Judgment capture | `CLM-0001` | `commercial-legal/agents/deal-debrief.md` (deviation basis + write `deviation-log.yaml`) |
| Judgment capture | `CLM-0001` | `commercial-legal/agents/playbook-monitor.md` (pattern → proposed playbook language) |
| No auto-upload of profiles | `CLM-0002` | `scripts/deploy-managed-agent.sh` (~L75–190: `/v1/skills` zip of skill dirs; `/v1/agents` JSON — not config/matter packs) |

**Counterevidence / boundary (not “line of code” alone)**

| Finding | Claim | Where |
|---|---|---|
| Default no-training terms | `CLM-0003` | `SRC-0005` capture via `registry/source-registry.json` (hash-bound commercial terms) |
| Covert pooling unproven | `CLM-0010` | Registry absence + terms; **not** impossibility |
| Runtime / tenant unknown | `CLM-0017`, `CLM-0018` | Explicit unknowns — do not invent runtime proof |

**Interactive drill-down (local, release-blocked)**

- Open `public/generated-release-artifacts/candidate/index.html`  
- Search `CLM-0002` / `CLM-0001` / thesis IDs → follow claim → source/chunk

---

## Optional local-only packet (if `private/` exists on disk)

Gitignored; **not** on the public remote. If present:

```text
private/white-paper/ajax-line-research-agenda/research-program/
  00_WRITING_AI_FRONT_DOOR.md
  01_PROVENANCE_CHAIN.md
  03_SIGNAL_MONITOR.md
  READ_ONLY_REVIEW_HANDOFF.md   # if asked to critique / find missed patterns
```

Ignore this section if you only have the GitHub checkout without `private/`.

---

## What “done understanding” looks like

You can answer, with file paths:

1. What is the Ajax Line thesis, and what does it **not** allege?  
2. Which single claim is reviewed + publication-eligible, and what lines support it?  
3. Which upstream files prove “design invites judgment capture”?  
4. Why H2 remains unproven?  
5. How would you walk `CLM-0001` from thesis node → claim → source → exact lines?

---

## Pasteable starter prompt for another AI

```text
Read-only. Start at AI_FRONT_DOOR.md, then follow docs/AI_FINDINGS_PROVENANCE_PROOF_ROUTE.md exactly.

Goal: understand the locked findings, provenance chain, and line-of-code proof.
Do not edit, commit, publish, contact Anthropic, or flip release to READY.

When done, summarize:
1) finding spine in 5 sentences
2) CLM-0002 proof with exact file:lines
3) CLM-0001 proof with exact file:lines
4) provenance chain for one thesis node (TMN → claim → source → lines)
5) what remains Unknown
```
