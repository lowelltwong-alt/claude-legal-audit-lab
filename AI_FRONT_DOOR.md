# AI Front Door

This is the single entrypoint for AI systems and human investigators working in
this public repository. It routes readers to controlling instructions, source
authority, claim genealogy, the audit workflow, and generated candidate
evidence without treating any one of those layers as interchangeable.

## Repository identity

- Repository role: evidence-first audit harness for `anthropics/claude-for-legal`.
- Pinned upstream revision: `5ceb305b30b4c82653c9b6642499c12e946ec319`.
- Authority boundary: this repository analyzes public evidence; it is not
  authority for Anthropic's closed runtime, internal intent, or a law firm's
  executed commercial terms.
- Publication boundary: unpublished working material is excluded from the
  public release surface. Its existence never makes a public claim true.
- Current execution and release state: `registry/project-roadmap.json` is the
  machine project controller; `registry/release-readiness.json` is the
  fail-closed release gate. The current release state is `blocked`.

## Required read order

1. `AGENTS.md` — controlling epistemic and audit rules.
2. `MACHINE_NAVIGATION_MANIFEST.json` — machine-readable routes and versions.
3. `registry/source-of-truth.json` — precedence and authority classes.
4. `registry/design-authority.json` — which files may define which contracts.
5. `registry/ai-front-door-registry.json` — task-to-path routing.
6. `AI_TABLE_OF_CONTENTS.md` — shallow human-readable branch map.
7. Only the task-relevant sources, claims, methods, and candidate outputs.

## Evidence genealogy

Use this chain for any factual statement:

```text
primary source or immutable revision
-> byte-exact chunk or hash-bound capture
-> typed evidence edge
-> bounded claim
-> argument or thesis node
-> stable paper paragraph
-> read-only explorer view
```

The machine surfaces are:

- `registry/source-registry.json` — public source identities and revision limits.
- `registry/claim-registry.json` — bounded claims and evidence locators.
- `registry/chunk-policy.json` and `registry/chunk-registry.json` — full-SHA
  chunk identities, byte-exact locators, and reconstruction authority.
- `registry/edge-type-library.json` and `registry/evidence-graph.json` — typed
  inverse edges from source and revision through chunks, claims, and arguments.
- `registry/thesis-map.json` and `docs/THESIS_MAP.md` — the seven-node
  candidate thesis spine with objections, falsifiers, gaps, and boundaries.
- `registry/white-paper-export.json` — positive-allowlist paragraph genealogy;
  release remains blocked.
- `docs/MINI_WHITE_PAPER_ENGINE.md`, `registry/mini-paper-plan.json`, and
  `public/generated-release-artifacts/candidate/mini-papers/` — three
  evidence-identical rhetorical versions with stable anchors, JSON sidecars,
  and compare-only structure simulation.
- `public/generated-release-artifacts/candidate/index.html` — local read-only
  exact-ID and lexical explorer with no external requests.
- `registry/lineage-policy.json` — authored parent/source/claim declarations.
- `registry/derivation-registry.json` — deterministic hashes and transitive
  primary-source closure generated from that policy.
- `scripts/build_lineage.py` — deterministic builder.
- `scripts/validate_navigation.py` — fail-closed navigation and genealogy gate.
- `docs/AI_NAVIGATION_AND_LINEAGE_STANDARD.md` — reusable human contract.
- `docs/ARGUMENT_MESH_STANDARD.md` — theory-to-thesis-to-evidence and white-paper export contract.
- `CONTRIBUTING.md` — preview contribution lanes and activation gates.
- `docs/CROSS_INDUSTRY_ONTOLOGY_RISK.md` — cross-industry research-priority methodology.
- `registry/industry-research-taxonomy.json` — machine-readable candidate industry map.
- `docs/RESEARCH_RADAR.md` and `registry/research-radar-watchlist.json` — candidate-only monitoring policy and watchlist.
- `docs/LICENSING_OPTIONS.md` — human-gated license decision brief; it does not change `LICENSE`.

- `docs/FRONTIER_LAB_ONTOLOGY_CAPTURE_COUNTERFACTUAL.md` — defensive, synthetic-only model of operational and professional-judgment exposure.
- `registry/law-firm-value-chain.json` and `registry/counterfactual-capture-patterns.json` — authored lifecycle and exposure contracts.
- `registry/counterfactual-exposure-graph.json` — deterministic candidate graph; never source truth.

- `docs/FEATURE_EVIDENCE_MATRIX.md` provides a bounded policy, static-repository, and runtime-unknown comparison for retention, connectors, workflows, and safeguards.

The white-paper argument surfaces are:

- `audit/FINAL_REPORT.md` — calibrated conclusion from six exact-coverage
  discovery passes, specialist falsification, and bounded public PR history.
- `results/semantic-coverage-round-1.md` and `results/pass-results/` —
  candidate review receipts and specialist analyses; these are not source truth.

- `registry/argument-mesh.json` — candidate theory, thesis, support, objection,
  rebuttal, falsifier, proof-gap, and paper-section graph with reverse links.
- `docs/AJAX_LINE_COLLECTIVE_BRAIN_TRUST.md` — the hold-the-line thesis and
  dedicated collective-alpha research lane.
- `scripts/validate_argument_mesh.py` — fail-closed argument and inverse-edge
  validator.

No generated report, graph, chunk, search match, or synthesis is source truth.
It is candidate evidence until a claim record binds it to an exact source
locator and preserves what the evidence does and does not prove.

## Route by question

| Question | Start here | Then inspect |
|---|---|---|
| What are the findings, provenance, and line-of-code proofs? | `docs/AI_FINDINGS_PROVENANCE_PROOF_ROUTE.md` | `docs/THESIS_MAP.md`, `registry/claim-registry.json`, then open the upstream locators |
| What is the roadmap, what is unblocked, and what happens next? | `docs/ROADMAP.md` | `registry/project-roadmap.json` and `scripts/validate_roadmap.py` |
| Is this ready to rename, stage, or publish? | `registry/release-readiness.json` | Run `python scripts/validate_release_readiness.py --require-ready`; human approval is still required |
| What is this repository and what is out of scope? | `README.md` | `docs/SCOPE_BOUNDARY.md` |
| What does the pinned code do? | `audit/EVIDENCE_MAP.md` | `upstream/claude-for-legal/` at the locked commit |
| What did the completed codebase research conclude? | `audit/FINAL_REPORT.md` | Inspect the six pass receipts, merged clusters, specialist rebuttal, and saturation check under `results/` |
| What is claimed, with what confidence? | `registry/claim-registry.json` | `audit/CLAIM_LEDGER.csv` |
| Where did a synthesis come from? | `registry/derivation-registry.json` | Follow `parent_artifacts`, `claim_ids`, and `primary_source_closure` |
| How do theses and white-paper arguments connect? | `docs/ARGUMENT_MESH_STANDARD.md` | Follow only approved argument exports into claims and source genealogy |
| How are mini white papers generated and compared? | `docs/MINI_WHITE_PAPER_ENGINE.md` | Inspect the plan, three sidecars, and compare-only structure receipt; scores cannot promote evidence |
| How do I drill from a paper paragraph to exact evidence? | `public/generated-release-artifacts/candidate/index.html` | Follow thesis → argument → claim → source/chunk; the candidate is release-blocked |
| How are static, temporal, and captured-source chunks identified without losing citation fidelity? | `docs/SOURCE_AWARE_CHUNK_CONTRACT.md` | Chunks are candidate evidence; preserve raw-byte and source-custody limits |
| What does the published material, static repository, and runtime evidence each establish about a feature? | `docs/FEATURE_EVIDENCE_MATRIX.md` | Preserve the listed unknowns; do not promote them to operational findings |
| Why should law firms collectively hold the line around attorney brain-trust data? | `docs/AJAX_LINE_COLLECTIVE_BRAIN_TRUST.md` | Traverse `registry/argument-mesh.json`, including objections, falsifiers, proof gaps, claims, and sources |
| How can Iliad Line 37 and AlphaGo Move 37 be used without converting analogy into an allegation? | `docs/ILIAD_MOVE_37_RESEARCH_LANE.md` | Verify editions and primary sources; preserve contractual and technical counterevidence |
| How can I contribute? | `CONTRIBUTING.md` | Intake is preview/closed until licensing and maintainer gates are approved |
| Which other industries should be researched? | `docs/CROSS_INDUSTRY_ONTOLOGY_RISK.md` | `registry/industry-research-taxonomy.json` and its exact source IDs |
| What developments are being monitored? | `docs/RESEARCH_RADAR.md` | `registry/research-radar-watchlist.json`; signals are candidate-only |
| Which license should this use? | `docs/LICENSING_OPTIONS.md` | Owner/legal decision required before any license mutation or public intake |
| What would prove or refute secondary use? | `docs/HOW_A_TROJAN_HORSE_WOULD_WORK.md` | `docs/RUNTIME_VALIDATION_PLAN.md` |
| If a frontier lab wanted to map a law firm's alpha, how could the exposure path work and how would we stop it? | `docs/FRONTIER_LAB_ONTOLOGY_CAPTURE_COUNTERFACTUAL.md` | Follow the value-chain, pattern, generated graph, and decision registries |
| What should be asked of Anthropic? | `research/QUESTIONS_TO_ANTHROPIC.md` | Relevant proof gaps in the claim registry |
| How should agents conduct the audit? | `AGENTS.md` | `prompts/00-master-orchestrator.md` |
| Are generated results authoritative? | `registry/source-of-truth.json` | They are candidate evidence only |

## Stop conditions

Stop and mark the proposition `Unknown` when a source, exact locator, required
parent, content revision, or source-to-sink arrow is missing. Stop publication
when `python scripts/validate_navigation.py` reports a broken route, stale hash,
cycle, incomplete primary-source closure, or authority inversion.
Also stop release when the release-readiness validator reports `BLOCKED`; a
passing structural validation of a truthful blocked record is not publication approval.
