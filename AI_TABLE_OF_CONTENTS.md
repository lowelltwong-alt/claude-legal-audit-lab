# AI Table of Contents

**Single entrypoint:** [`AI_FRONT_DOOR.md`](AI_FRONT_DOOR.md)  
This file is a **branching map of every important public endpoint**, not a competing front door.  
**“Candidate”** means useful for investigation but **not source truth**.  
**Release** remains [`blocked`](registry/release-readiness.json). Do not treat any export as publishable.

**How to use**

1. Start at [`AI_FRONT_DOOR.md`](AI_FRONT_DOOR.md).  
2. Pick a **route** in §1 (Endpoint map).  
3. Open the **Path** links in that section’s table.  
4. For findings → provenance → line proof, use [`docs/AI_FINDINGS_PROVENANCE_PROOF_ROUTE.md`](docs/AI_FINDINGS_PROVENANCE_PROOF_ROUTE.md).

Every table below keeps the required contract columns: Path | What it is | Tags | Use when | Authority.

---

## 1. Endpoint map (front-door routes)

Machine authority: [`registry/ai-front-door-registry.json`](registry/ai-front-door-registry.json). Highest matching priority wins; ties fail closed.

| Path | What it is | Tags | Use when | Authority |
|---|---|---|---|---|
| `registry/ai-front-door-registry.json` | Deterministic task→path router (`route_id`, triggers, priority, `read[]`). | routing, endpoints, machine | Selecting the smallest relevant read set for a question. | Navigation authority |
| `AI_FRONT_DOOR.md` | Official human/AI entrypoint: identity, required read order, genealogy, question→route table. | front-door, entrypoint | Starting any session. | Single entrypoint |
| `docs/AI_FINDINGS_PROVENANCE_PROOF_ROUTE.md` | Task route: locked findings → claim provenance → exact upstream lines. | findings, provenance, proof | Onboarding another AI to Ajax Line proof without a second front door. | Navigation / task route |
| `MACHINE_NAVIGATION_MANIFEST.json` | Machine navigation contract: entrypoint, TOC, genealogy keys, validation commands, upstream pin. | manifest, machine | Automation and navigation validation. | Navigation authority |

| Route ID | Priority | Triggers (examples) | Read endpoints |
|---|---:|---|---|
| `roadmap_and_release` | 116 | roadmap, what next, publish, rename | [`docs/ROADMAP.md`](docs/ROADMAP.md), [`registry/project-roadmap.json`](registry/project-roadmap.json), [`registry/release-readiness.json`](registry/release-readiness.json) |
| `evidence_control_plane` | 115 | chunk registry, evidence graph, exact genealogy | [`registry/chunk-policy.json`](registry/chunk-policy.json), [`registry/chunk-registry.json`](registry/chunk-registry.json), [`registry/edge-type-library.json`](registry/edge-type-library.json), [`registry/evidence-graph.json`](registry/evidence-graph.json), [`registry/thesis-map.json`](registry/thesis-map.json), [`public/generated-release-artifacts/candidate/index.html`](public/generated-release-artifacts/candidate/index.html) |
| `ajax_line` | 114 | ajax line, collective alpha, sector externality | [`docs/THESIS_MAP.md`](docs/THESIS_MAP.md), [`registry/thesis-map.json`](registry/thesis-map.json), [`registry/evidence-graph.json`](registry/evidence-graph.json), [`registry/argument-mesh.json`](registry/argument-mesh.json), [`registry/claim-registry.json`](registry/claim-registry.json), [`registry/source-registry.json`](registry/source-registry.json) |
| `findings_provenance_proof` | 113 | findings, provenance, line of code, proof route, CLM-0002 | [`docs/AI_FINDINGS_PROVENANCE_PROOF_ROUTE.md`](docs/AI_FINDINGS_PROVENANCE_PROOF_ROUTE.md), [`docs/THESIS_MAP.md`](docs/THESIS_MAP.md), [`registry/claim-registry.json`](registry/claim-registry.json), [`UPSTREAM.lock.json`](UPSTREAM.lock.json), [`upstream/claude-for-legal/`](upstream/claude-for-legal/) |
| `counterfactual_capture` | 112 | frontier lab, judgment ontology, flatten law firms | [`docs/FRONTIER_LAB_ONTOLOGY_CAPTURE_COUNTERFACTUAL.md`](docs/FRONTIER_LAB_ONTOLOGY_CAPTURE_COUNTERFACTUAL.md), [`registry/law-firm-value-chain.json`](registry/law-firm-value-chain.json), [`registry/counterfactual-capture-patterns.json`](registry/counterfactual-capture-patterns.json), [`registry/counterfactual-exposure-graph.json`](registry/counterfactual-exposure-graph.json), [`docs/COUNTERFACTUAL_CAPTURE_DECISION.md`](docs/COUNTERFACTUAL_CAPTURE_DECISION.md), [`registry/source-registry.json`](registry/source-registry.json) |
| `contribution` | 110 | contribute, pull request | [`CONTRIBUTING.md`](CONTRIBUTING.md), [`docs/RESEARCH_CONTRIBUTION_MODEL.md`](docs/RESEARCH_CONTRIBUTION_MODEL.md), [`templates/`](templates/) |
| `licensing` | 108 | license, trademark, DCO | [`docs/LICENSING_OPTIONS.md`](docs/LICENSING_OPTIONS.md), [`docs/LICENSE_MAP.md`](docs/LICENSE_MAP.md), [`docs/CONTRIBUTION_RADAR_DECISION.md`](docs/CONTRIBUTION_RADAR_DECISION.md), [`LICENSE`](LICENSE), [`NOTICE`](NOTICE), [`LICENSES/CC-BY-4.0.txt`](LICENSES/CC-BY-4.0.txt) |
| `cross_industry` | 106 | industry, healthcare, finance | [`docs/CROSS_INDUSTRY_ONTOLOGY_RISK.md`](docs/CROSS_INDUSTRY_ONTOLOGY_RISK.md), [`registry/industry-research-taxonomy.json`](registry/industry-research-taxonomy.json), [`templates/industry-research-profile.template.md`](templates/industry-research-profile.template.md) |
| `research_radar` | 104 | radar, monitor, watchlist | [`docs/RESEARCH_RADAR.md`](docs/RESEARCH_RADAR.md), [`registry/research-radar-watchlist.json`](registry/research-radar-watchlist.json), [`templates/research-signal.template.json`](templates/research-signal.template.json) |
| `genealogy` | 100 | source, genealogy, lineage | [`registry/evidence-graph.json`](registry/evidence-graph.json), [`registry/derivation-registry.json`](registry/derivation-registry.json), [`registry/claim-registry.json`](registry/claim-registry.json), [`registry/source-registry.json`](registry/source-registry.json) |
| `argument_and_white_paper` | 95 | thesis, white paper, argument | [`docs/THESIS_MAP.md`](docs/THESIS_MAP.md), [`registry/thesis-map.json`](registry/thesis-map.json), [`registry/white-paper-export.json`](registry/white-paper-export.json), [`public/generated-release-artifacts/candidate/white-paper.md`](public/generated-release-artifacts/candidate/white-paper.md), [`docs/ARGUMENT_MESH_STANDARD.md`](docs/ARGUMENT_MESH_STANDARD.md) |
| `telemetry_and_retention` | 90 | telemetry, retention, training | [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md), [`docs/RUNTIME_VALIDATION_PLAN.md`](docs/RUNTIME_VALIDATION_PLAN.md), [`research/QUESTIONS_TO_ANTHROPIC.md`](research/QUESTIONS_TO_ANTHROPIC.md) |
| `claim_check` | 80 | claim, prove, confidence | [`registry/claim-registry.json`](registry/claim-registry.json), [`registry/source-registry.json`](registry/source-registry.json) |
| `code_evidence` | 70 | code, line, file, implementation | [`UPSTREAM.lock.json`](UPSTREAM.lock.json), [`registry/chunk-registry.json`](registry/chunk-registry.json), [`audit/EVIDENCE_MAP.md`](audit/EVIDENCE_MAP.md), [`upstream/claude-for-legal/`](upstream/claude-for-legal/) |
| `run_audit` | 60 | scan, audit, agents, workflow | [`AGENTS.md`](AGENTS.md), [`prompts/00-master-orchestrator.md`](prompts/00-master-orchestrator.md), [`schemas/pass-result.schema.json`](schemas/pass-result.schema.json) |
| `generated_results` | 50 | results, matches, report | [`registry/source-of-truth.json`](registry/source-of-truth.json), [`results/`](results/) |
| `orientation` | 10 | what is this, scope, overview | [`README.md`](README.md), [`docs/SCOPE_BOUNDARY.md`](docs/SCOPE_BOUNDARY.md) |

Fallback route: `orientation`.

---

## 2. Bootstrap / authority

| Path | What it is | Tags | Use when | Authority |
|---|---|---|---|---|
| `AGENTS.md` | Controlling epistemic and audit protocol (H0/H1/H2; Confirmed/Inferred/Unknown; source-to-sink). | instructions, epistemics, scope | Starting any audit or agent run. | Governing method |
| `CLAUDE.md` | Short pointer telling coding agents to start at the front door and follow `AGENTS.md`. | agents, bootstrap | Claude/coding-agent sessions. | Governing pointer |
| `registry/source-of-truth.json` | Precedence and authority classification for disagreements. | authority, precedence | Deciding which artifact wins a conflict. | Authority registry |
| `registry/design-authority.json` | Which files may define which contracts (schemas, policy, sources, outputs). | governance, ownership | Changing a shared contract or generated surface. | Design authority |
| `README.md` | Public orientation and high-level assessment. | overview, public | Explaining the project to a new reader. | Derived synthesis |
| `LICENSE` | Repository license text. | license | Legal reuse questions. | Legal authority |
| `SECURITY.md` | Safe disclosure and authorized-testing boundary. | security, privacy, disclosure | Reporting boundary problems without public exposure. | Governing method |

---

## 3. Project control and release

| Path | What it is | Tags | Use when | Authority |
|---|---|---|---|---|
| `docs/ROADMAP.md` | Human-readable phased roadmap, frontier, gates, executed tranche. | roadmap, status | Deciding what to do next without activating blocked work. | Project control view |
| `registry/project-roadmap.json` | Machine roadmap: workstreams, dependencies, blockers, human decisions, Terminal Local Completion / quiet hold. | roadmap, machine, wip | Routing execution and validating lifecycle truth. | Project execution authority |
| `schemas/project-roadmap.schema.json` | JSON Schema for the project roadmap packet. | schema, roadmap | Validating roadmap structure. | Schema authority |
| `scripts/validate_roadmap.py` | Fail-closed roadmap and unlock-frontier validator. | validation, roadmap | Checking state, acceptance evidence, WIP, blockers, leases. | Governing method |
| `docs/ROADMAP_CONTROL_REVIEW.md` | Independent roadmap/release control red-team record. | review, roadmap | Checking control-plane review evidence. | Reviewed analysis |
| `registry/release-readiness.json` | Blocked/ready release record: inventory, decisions, receipts, export gates (`status: blocked`). | release, privacy | Determining whether rename/stage/publish may proceed. | Release-readiness authority; not human approval |
| `schemas/release-readiness.schema.json` | JSON Schema for release readiness. | schema, release | Validating release records. | Schema authority |
| `scripts/validate_release_readiness.py` | Structural gate; `--require-ready` must fail until every condition + human approval exists. | validation, release | Preventing a passing blocked record from being mistaken for publish permission. | Governing method |
| `scripts/public_safety.py` | Public-surface privacy/safety scanner for tracked artifacts. | privacy, safety | Before staging/publishing public paths. | Governing method |

---

## 4. Findings, thesis, claims, arguments

| Path | What it is | Tags | Use when | Authority |
|---|---|---|---|---|
| `docs/AI_FINDINGS_PROVENANCE_PROOF_ROUTE.md` | Ordered path from locked findings to provenance to upstream line proof. | findings, proof, handoff | Teaching another AI the proof chain. | Navigation / task route |
| `docs/THESIS_MAP.md` | One-page human view of the seven-node Ajax Line spine (blocked candidate). | thesis, overview | Reviewing the bounded argument at a glance. | Generated candidate |
| `registry/thesis-map.json` | Machine thesis: `bounded_thesis`, TMN nodes, TEP paths, objections, falsifiers, export gate. | thesis, falsifiers | Inspecting what each proposition does/does not prove. | Candidate analytic registry |
| `schemas/thesis-map.schema.json` | Schema for thesis-map. | schema, thesis | Validating thesis structure. | Schema authority |
| `scripts/build_thesis_map.py` | Builds `docs/THESIS_MAP.md` from the thesis registry. | builder, thesis | Regenerating the human thesis view. | Governing method |
| `registry/claim-registry.json` | Bounded claims with epistemic/review/publication states and evidence locators (`CLM-####`). | claims, evidence | Quoting, testing, or challenging a proposition. | Claim authority; only eligible may export |
| `schemas/claim-registry.schema.json` | Schema for claims. | schema, claims | Validating claim records. | Schema authority |
| `scripts/upgrade_claim_registry_v2.py` | Claim-registry v2 check/upgrade tool. | claims, validation | Checking claim registry integrity. | Governing method |
| `audit/CLAIM_LEDGER.csv` | Legacy human-readable claim table. | claims, legacy | Orientation only; prefer claim-registry for genealogy. | Candidate legacy |
| `docs/ARGUMENT_MESH_STANDARD.md` | Theory→thesis→objection→falsifier→paper drill-down contract. | arguments, standard | Connecting ideas to claims without promoting suggestions. | Governing method |
| `registry/argument-mesh.json` | Theory/thesis/support/objection/rebuttal/falsifier/proof-gap/paper-section graph. | argument-graph, machine | Drilling Ajax Line with dissent preserved. | Candidate research registry |
| `schemas/argument-mesh.schema.json` | Schema for argument mesh. | schema, arguments | Validating argument mesh. | Schema authority |
| `scripts/validate_argument_mesh.py` | Fail-closed argument-mesh validator. | validation, arguments | Changing or checking the mesh. | Governing method |
| `docs/AJAX_LINE_COLLECTIVE_BRAIN_TRUST.md` | Hold-the-line narrative: peer exposure, externality, holdout, Move 37, controls, research program. | ajax-line, white-paper | Researching collective-alpha without alleging provider conduct. | Candidate analytic model |
| `docs/ILIAD_MOVE_37_RESEARCH_LANE.md` | How to use Iliad/Move 37 analogy without converting it into an allegation. | analogy, move-37 | Framing research-horizon language safely. | Governing method |
| `docs/PARTNER_JUDGMENT_ONTOLOGY.md` | Partner-judgment ontology construct (operational, not mind-reading). | ontology, judgment | Defining judgment fields to search for in product design. | Reviewed analysis |
| `docs/FEATURE_EVIDENCE_MATRIX.md` | Feature-level split: policy docs vs static repo vs runtime unknown. | evidence, retention, mcp | Evaluating data-flow questions without collapsing evidence types. | Candidate evidence matrix |
| `audit/FINAL_REPORT.md` | Calibrated conclusion from discovery passes, falsification, PR history. | report, synthesis | Reading the completed codebase-research conclusion. | Candidate evidence |
| `docs/KIRKLAND_CONNECTION.md` | Comparative Kirkland/sovereign notes and proof gaps. | comparative, kirkland | Comparative custody questions; primary architecture unavailable. | Candidate analysis |
| `docs/HOW_A_TROJAN_HORSE_WOULD_WORK.md` | Counterfactual Trojan-horse mechanism vs observed evidence. | counterfactual, threat | Phase-D style mechanism tests. | Candidate analytic model |

---

## 5. Sources, chunks, graph, genealogy

| Path | What it is | Tags | Use when | Authority |
|---|---|---|---|---|
| `UPSTREAM.lock.json` | Immutable identity of the reviewed upstream commit. | upstream, pin | Verifying which code version a claim concerns. | Source identity |
| `upstream/claude-for-legal/` | Checkout of the exact locked public source (line-of-code proof surface). | primary-source, code | Verifying code claims at exact files and lines. | Primary source when lock matches |
| `registry/source-registry.json` | Public source identities, locators, revision/capture bindings (`SRC-####`). | sources, citations | Following a claim to its originating publication or commit. | Source metadata |
| `schemas/source-registry.schema.json` | Schema for sources. | schema, sources | Validating source records. | Schema authority |
| `scripts/capture_public_source.py` | HTTPS-only public capture into ignored `private/raw/sources/`. | capture, private | Preserving dated public bytes before hashing into source metadata. | Governing method; capture ≠ publication |
| `docs/SOURCE_AWARE_CHUNK_CONTRACT.md` | Human contract for static/temporal/captured chunks without losing citation fidelity. | chunks, contract | Understanding chunk identity rules. | Governing method |
| `registry/chunk-policy.json` | Chunk-registry v2 identity, partition, activation, privacy policy. | chunks, policy | Changing chunk kinds or byte partition rules. | Governing method |
| `schemas/chunk-policy.schema.json` | Schema for chunk policy. | schema, chunks | Validating policy. | Schema authority |
| `registry/chunk-registry.json` | Full-SHA byte-exact chunks + inverse adjacency for the pinned Git tree. | chunks, locators | Resolving static code evidence to exact bytes/line hints. | Generated candidate evidence |
| `schemas/chunk-registry.schema.json` | Schema for chunk registry. | schema, chunks | Validating chunks. | Schema authority |
| `registry/chunk-id-migration.json` | v1→v2 chunk-ID compatibility map. | migration, ids | Translating legacy chunk references. | Generated candidate evidence |
| `schemas/chunk-id-migration.schema.json` | Schema for chunk-ID migration. | schema, migration | Validating migration map. | Schema authority |
| `scripts/build_chunk_registry.py` | Builds/checks chunk registry with reconstruction verification. | builder, chunks | Rebuilding or checking chunks. | Governing method |
| `docs/CURSOR_CHUNK_ENGINE_HANDOFF.md` | Handoff notes for the chunk engine work. | chunks, handoff | Continuing chunk-engine implementation. | Method notes |
| `registry/edge-type-library.json` | Governed inverse edge families, meanings, non-implications, cycle policy. | graph, ontology | Adding or interpreting typed edges. | Governing method |
| `schemas/edge-type-library.schema.json` | Schema for edge types. | schema, edges | Validating edge library. | Schema authority |
| `registry/evidence-graph.json` | Typed source/revision/chunk/claim/argument graph with proof gaps. | graph, evidence | Drilling primary evidence ↔ claims ↔ arguments. | Generated candidate evidence |
| `schemas/evidence-graph.schema.json` | Schema for evidence graph. | schema, graph | Validating graph. | Schema authority |
| `scripts/build_evidence_graph.py` | Builds/checks the evidence graph. | builder, graph | Regenerating graph after material registry changes. | Governing method |
| `docs/AI_NAVIGATION_AND_LINEAGE_STANDARD.md` | Reusable navigation + genealogy standard. | standard, lineage | Extending or porting this structure. | Governing method |
| `docs/LINEAGE_CONTRACT_DECISION.md` | Decision record for lineage contract choices. | lineage, decision | Understanding why genealogy is fail-closed. | Governing decision record |
| `registry/lineage-policy.json` | Authored parent/source/claim declarations for public derived artifacts. | lineage, policy | Adding or changing a synthesis’s declared parents. | Lineage declaration |
| `schemas/lineage-policy.schema.json` | Schema for lineage policy. | schema, lineage | Validating lineage policy. | Schema authority |
| `registry/derivation-registry.json` | Generated hashes + transitive primary-source closure. | genealogy, hashes | Tracing an artifact through parents to sources. | Generated candidate |
| `schemas/derivation-registry.schema.json` | Schema for derivation registry. | schema, derivation | Validating derivations. | Schema authority |
| `scripts/build_lineage.py` | Deterministic lineage/derivation builder. | builder, lineage | Refreshing derivation hashes. | Governing method |
| `scripts/validate_navigation.py` | Fail-closed navigation, authority, genealogy, and routing-fixture gate. | validation, navigation | After changing front door, TOC, routes, or genealogy. | Governing method |

---

## 6. History / PR archaeology

| Path | What it is | Tags | Use when | Authority |
|---|---|---|---|---|
| `registry/repository-history-capture.json` | Local-Git capture contract, snapshot hash, remote-history gaps. | history, git | Checking what local Git can establish vs still-needed public capture. | History-capture authority |
| `schemas/repository-history-capture.schema.json` | Schema for history capture. | schema, history | Validating history capture. | Schema authority |
| `scripts/build_history_capture_receipt.py` | Builds/checks the bounded history receipt. | builder, history | Rebuilding history completeness receipts. | Governing method |
| `scripts/capture_github_pr_evidence.py` | Captures public GitHub PR evidence (API metadata). | pr, capture | Refreshing public PR snapshots. | Governing method |
| `scripts/build_pr_linkage.py` | Links captured PRs to local commits/diffs without inferring intent. | pr, diffs, provenance | Verifying hash-linked PR coverage. | Governing method |
| `results/pr-commit-diff-linkage.json` | Generated PR linkage summary (linked / open snapshot / incomplete). | pr, results | Reading PR archaeology outcomes (e.g. PR 50 incomplete). | Generated candidate |
| `scripts/build_pr_surface_taxonomy.py` | Classifies changed PR paths into observable surfaces (no purpose inference). | pr, taxonomy | Comparing path-level PR surfaces. | Governing method |
| `results/pr-surface-taxonomy.json` | Generated PR surface taxonomy output. | pr, taxonomy, results | Inspecting path-class projections. | Generated candidate |

---

## 7. White paper / mini-papers / explorer (release blocked)

| Path | What it is | Tags | Use when | Authority |
|---|---|---|---|---|
| `docs/MINI_WHITE_PAPER_ENGINE.md` | Method for audience-specific mini papers with stable anchors/sidecars; scores ≠ truth. | mini-paper, methods | Understanding or extending the paper engine. | Governing method; release blocked |
| `registry/mini-paper-plan.json` | Authored units, profiles, tags, prose, comparison weights. | mini-paper, plan | Changing rhetoric without changing evidence authority. | Candidate plan; release blocked |
| `schemas/mini-paper-plan.schema.json` | Schema for mini-paper plan. | schema, mini-paper | Validating plan. | Schema authority |
| `registry/mini-paper-related-work.json` | Related-work search receipt and bounded comparative conclusion. | related-work, receipt | Reproducing the landscape scan. | Candidate research receipt |
| `schemas/mini-paper-related-work.schema.json` | Schema for related-work receipt. | schema, related-work | Validating related-work. | Schema authority |
| `schemas/mini-paper-sidecar.schema.json` | Schema for paragraph sidecars. | schema, sidecar | Validating sidecars. | Schema authority |
| `scripts/build_mini_papers.py` | Builds executive/academic/adversarial mini papers + comparison. | builder, mini-paper | Regenerating mini-paper candidates. | Governing method |
| `registry/white-paper-export.json` | Positive-allowlist paragraph genealogy + blocked export dataset. | export, paragraphs | Replaying unpublished candidate genealogy. | Generated candidate; release blocked |
| `schemas/white-paper-export.schema.json` | Schema for white-paper export. | schema, export | Validating export. | Schema authority |
| `scripts/build_white_paper_candidate.py` | Builds blocked white-paper candidate + explorer inputs. | builder, white-paper | Regenerating blocked candidate. | Governing method |
| `public/generated-release-artifacts/candidate/white-paper.md` | Blocked candidate white-paper Markdown. | paper, candidate | Reading the blocked prose candidate. | Generated candidate; release blocked |
| `public/generated-release-artifacts/candidate/index.html` | Local read-only evidence explorer (no external requests). | explorer, local | Searching IDs and drilling claim→source/chunk. | Generated candidate; release blocked |
| `public/generated-release-artifacts/candidate/mini-papers/` | Executive, academic, adversarial Markdown + JSON sidecars + comparison. | mini-paper, outputs | Comparing rhetorical versions with identical genealogy. | Generated candidate; release blocked |
| `public/generated-release-artifacts/candidate/mini-papers/executive.md` | Executive mini-paper version. | mini-paper, executive | Decision-oriented reading. | Generated candidate |
| `public/generated-release-artifacts/candidate/mini-papers/academic.md` | Academic mini-paper version. | mini-paper, academic | Research-design reading. | Generated candidate |
| `public/generated-release-artifacts/candidate/mini-papers/adversarial.md` | Adversarial/skeptical mini-paper version. | mini-paper, adversarial | Counterevidence-first reading. | Generated candidate |
| `public/generated-release-artifacts/candidate/mini-papers/comparison.json` | Structure comparison receipt across versions. | comparison, receipt | Checking ordering/completeness scores only. | Generated candidate |

---

## 8. Radar, industries, contribution, licensing

| Path | What it is | Tags | Use when | Authority |
|---|---|---|---|---|
| `docs/RESEARCH_RADAR.md` | Candidate-only monitoring policy and operating rhythm (automation off by default). | radar, monitoring | Tracking product/policy/partnership/repo drift. | Governing method |
| `registry/research-radar-watchlist.json` | Allowlisted watch classes, cadence, signal families (“Cassandra Radar”). | radar, watchlist | Selecting approved public source classes. | Radar policy registry |
| `schemas/research-radar-watchlist.schema.json` | Schema for radar watchlist. | schema, radar | Validating watchlist. | Schema authority |
| `schemas/research-signal.schema.json` | Schema for candidate radar signals. | schema, signal | Validating signal packets. | Schema authority |
| `scripts/validate_research_radar.py` | Fail-closed radar validator. | validation, radar | Checking radar policy integrity. | Governing method |
| `research/signals/README.md` | Where candidate radar signals would live when intake is open. | signals, contribution | Preparing signal submissions. | Method notes |
| `docs/CROSS_INDUSTRY_ONTOLOGY_RISK.md` | Cross-industry ontology-exposure research priority method. | industry, methodology | Comparing legal with healthcare/finance/etc. | Governing method |
| `registry/industry-research-taxonomy.json` | Machine industry profiles and facets. | industry, taxonomy | Routing industry research without harm-score misuse. | Candidate research registry |
| `schemas/industry-research-taxonomy.schema.json` | Schema for industry taxonomy. | schema, industry | Validating taxonomy. | Schema authority |
| `CONTRIBUTING.md` | Contribution lanes, prohibited material, activation gates (intake closed). | contribution | Preparing a future submission. | Governing method |
| `docs/RESEARCH_CONTRIBUTION_MODEL.md` | Contributor roles, epistemic states, independent review gates. | contribution, roles | Designing the public research workflow. | Governing method |
| `docs/LICENSING_OPTIONS.md` | License decision brief; records Apache-2.0 + CC BY 4.0 choice and Lowell T Wong copyright. | license, decision | Understanding the dual-license model. | Human decision brief |
| `docs/LICENSE_MAP.md` | Path-level map of Apache-2.0 vs CC BY 4.0 vs excluded upstream/private paths. | license, map | Determining which license applies to a path. | Governing license map |
| `LICENSE` | Full Apache License 2.0 text for software and machine artifacts. | license, apache | Software reuse terms. | Legal authority |
| `LICENSES/CC-BY-4.0.txt` | Full CC BY 4.0 text for original research prose. | license, cc-by | Prose reuse with attribution. | Legal authority |
| `NOTICE` | Copyright holder, dual-license pointer, and attribution guidance. | notice, copyright | Redistribution attribution. | Legal notice |
| `docs/CONTRIBUTION_RADAR_DECISION.md` | Risk tier, premortem, rollback, activation boundary for contribution/radar. | governance, risk | Reviewing load-bearing contribution architecture. | Governing decision record |
| `docs/TROJAN_WAR_NAMING_CONVENTION.md` | Plain-name-first mythic aliases for surfaces. | naming | Naming radar/review/privacy surfaces consistently. | Naming method |
| `templates/` | Public-safe contribution packet templates directory. | templates | Starting structured research submissions after intake opens. | Governing templates |
| `templates/industry-research-profile.template.md` | Industry profile submission template. | template, industry | Filing an industry research profile. | Governing template |
| `templates/research-signal.template.json` | Radar signal submission template. | template, signal | Filing a candidate monitor signal. | Governing template |
| `templates/counterfactual-pathway.template.json` | Counterfactual pathway submission template. | template, counterfactual | Filing a synthetic exposure pathway. | Governing template |

---

## 9. Counterfactual / threat / runtime (synthetic only)

| Path | What it is | Tags | Use when | Authority |
|---|---|---|---|---|
| `docs/FRONTIER_LAB_ONTOLOGY_CAPTURE_COUNTERFACTUAL.md` | Defensive synthetic model of judgment-ontology exposure without raw client corpora. | counterfactual, ontology | Testing capture theses without alleging conduct. | Candidate analytic model |
| `docs/COUNTERFACTUAL_CAPTURE_DECISION.md` | Why public code is offline/synthetic-only; kill criteria. | governance, risk | Reviewing rejection of live collection. | Governing decision record |
| `registry/law-firm-value-chain.json` | 23-stage lifecycle with artifacts, signals, sensitivity, controls. | law-firm, lifecycle | Drilling firm value-chain exposure points. | Candidate research registry |
| `schemas/law-firm-value-chain.schema.json` | Schema for value chain. | schema, lifecycle | Validating value chain. | Schema authority |
| `registry/counterfactual-capture-patterns.json` | Synthetic exposure patterns, consent gates, forbidden uses, countercontrols. | capture-patterns, controls | Comparing metadata/prompt/outcome exposure scenarios. | Candidate research registry |
| `schemas/counterfactual-capture-pattern.schema.json` | Schema for capture patterns. | schema, patterns | Validating patterns. | Schema authority |
| `schemas/counterfactual-pathway.schema.json` | Schema for pathways. | schema, pathway | Validating pathways. | Schema authority |
| `registry/counterfactual-exposure-graph.json` | Generated stage→signal→inference→control projection (never source truth). | graph, generated | Traversing many-to-many exposure links. | Generated candidate |
| `schemas/counterfactual-exposure-graph.schema.json` | Schema for exposure graph. | schema, graph | Validating exposure graph. | Schema authority |
| `scripts/build_counterfactual_graph.py` | Builds/checks counterfactual exposure graph. | builder, counterfactual | Regenerating synthetic graph. | Governing method |
| `prompts/70-defensive-ontology-capture-counterfactual.md` | Routed-agent workflow for extending/challenging the counterfactual. | prompts, red-team | Read-only lifecycle/exposure/skeptical lanes. | Governing workflow |
| `docs/SCOPE_BOUNDARY.md` | Observable vs closed-system boundary. | scope, proof-gaps | Preventing claims beyond available evidence. | Reviewed analysis |
| `docs/THREAT_MODEL.md` | Assets, trust boundaries, threat classes. | security, data-flow | Planning evidence collection or runtime tests. | Reviewed model |
| `docs/RUNTIME_VALIDATION_PLAN.md` | Planned synthetic runtime tests (do not claim run without logs). | runtime, plan | Designing authorized synthetic validation. | Governing method |
| `runtime-lab/` | Synthetic-only runtime validation harness directory. | runtime, synthetic | Testing transmissions/retention/portability safely. | Test method |

---

## 10. Audit workflow, prompts, patterns, schemas, results

| Path | What it is | Tags | Use when | Authority |
|---|---|---|---|---|
| `prompts/` | Bounded multi-pass audit procedures directory. | prompts, workflow | Running discovery, merge, Trojan, skeptical, runtime, or generic passes. | Governing workflow |
| `prompts/00-master-orchestrator.md` | Master orchestration prompt for multi-pass audit. | orchestrator | Starting a full audit campaign. | Governing workflow |
| `prompts/01-codex-security-deep-scan.md` | Security deep-scan prompt lane. | security, prompt | Security-focused static pass. | Governing workflow |
| `prompts/10-independent-discovery-worker.md` | Independent discovery worker brief (variance reduction). | discovery, prompt | Phase A independent passes. | Governing workflow |
| `prompts/20-merge-and-pattern-mine.md` | Merge + pattern-mining prompt. | merge, patterns | Phase B dedupe and pattern extraction. | Governing workflow |
| `prompts/30-counterfactual-trojan-horse.md` | Strongest-mechanism then evidence-gap counterfactual. | trojan, counterfactual | Phase D analysis. | Governing workflow |
| `prompts/40-skeptical-rebuttal.md` | Falsification / benign-explanation search. | skeptical, falsify | Phase E rebuttal. | Governing workflow |
| `prompts/50-runtime-validation.md` | Runtime validation planning prompt. | runtime, prompt | Phase F planning (not claiming tests occurred). | Governing workflow |
| `prompts/60-generic-ai-master.md` | Generic AI master prompt variant. | prompt, generic | Non-Claude agent orchestration. | Governing workflow |
| `patterns/` | Seed and generated search signatures directory. | patterns, discovery | Finding candidate evidence; matches ≠ proof. | Candidate discovery |
| `schemas/` | Machine contracts for audit/lineage/registry records. | schemas, validation | Producing or validating structured artifacts. | Schema authority |
| `schemas/pass-result.schema.json` | Schema for discovery/specialist pass results. | schema, pass | Validating pass JSON. | Schema authority |
| `schemas/final-report.schema.json` | Schema for final report structure. | schema, report | Validating final report shape. | Schema authority |
| `scripts/inventory.py` | Builds inventory of tracked text surfaces. | inventory, builder | Regenerating inventory inputs. | Governing method |
| `scripts/pattern_scan.py` | Runs pattern signatures against inventory. | patterns, scan | Producing candidate matches. | Governing method |
| `scripts/build_worklists.py` | Builds balanced worker worklists. | worklists, audit | Phase A assignment. | Governing method |
| `scripts/build_semantic_coverage_receipt.py` | Builds semantic coverage receipts. | coverage, receipt | Recording line-level review coverage. | Governing method |
| `scripts/validate_jsonl.py` | JSONL validation helper. | validation, jsonl | Checking receipt streams. | Governing method |
| `results/` | Generated inventories, matches, receipts, reports directory. | generated, candidate | Reviewing reproducible outputs after validation. | Candidate evidence only |
| `results/inventory.json` | Generated file/line inventory. | inventory, results | Coverage planning. | Generated candidate |
| `results/coverage.csv` | Coverage ledger CSV. | coverage, results | Tracking review status. | Generated candidate |
| `results/url-index.csv` | Extracted URL index. | urls, results | External-link review. | Generated candidate |
| `results/semantic-coverage-round-1.md` | Round-1 semantic coverage receipt. | coverage, receipt | Checking completed semantic review. | Generated candidate |
| `results/pass-results/` | Discovery/specialist/saturation pass JSON directory. | pass-results | Inspecting multi-pass audit outputs. | Candidate evidence |
| `results/pass-results/round-1-merged.json` | Merged discovery clusters from six workers. | merge, discovery | Reading Phase B merge. | Candidate evidence |
| `results/pass-results/independent-saturation-check-final.json` | Final independent saturation check. | saturation | Checking whether new material classes remain. | Candidate evidence |
| `audit/EVIDENCE_MAP.md` | High-value paths in pinned upstream. | code, locators | Beginning line-level code review. | Candidate index |
| `audit/INITIAL_ASSESSMENT.md` | Initial static orientation (revalidate before reliance). | assessment, legacy | Understanding starting hypotheses. | Candidate legacy |
| `research/` | Provider/counterparty proof-gap questions directory. | research, interviews | Preparing diligence questions (not answers). | Interrogatory method |
| `research/QUESTIONS_TO_ANTHROPIC.md` | Unanswered Anthropic research prompts (not sought under Terminal Local). | anthropic, questions | Knowing what remains closed / not pursued. | Interrogatory method |
| `research/QUESTIONS_TO_KIRKLAND_PALANTIR.md` | Comparative counterparty questions. | kirkland, questions | Comparative diligence prompts. | Interrogatory method |
| `tests/` | Unit/integration tests for builders and validators. | tests | Running acceptance suite. | Governing method |

---

## 11. Strongest line-of-code proof endpoints (upstream)

Open under [`upstream/claude-for-legal/`](upstream/claude-for-legal/) only when [`UPSTREAM.lock.json`](UPSTREAM.lock.json) matches.

| Path | What it is | Tags | Use when | Authority |
|---|---|---|---|---|
| `upstream/claude-for-legal/commercial-legal/skills/cold-start-interview/SKILL.md` | Cold-start interview: seed docs → playbook positions → write local practice profile. | judgment-capture, CLM-0001 | Proving design invites judgment encoding. | Primary source (pinned) |
| `upstream/claude-for-legal/commercial-legal/agents/deal-debrief.md` | Deal debrief: deviation bases → `deviation-log.yaml`. | judgment-capture, CLM-0001 | Proving rationale/deviation capture loop. | Primary source (pinned) |
| `upstream/claude-for-legal/commercial-legal/agents/playbook-monitor.md` | Playbook monitor: pattern → proposed playbook language. | judgment-capture, CLM-0001 | Proving policy-update feedback loop. | Primary source (pinned) |
| `upstream/claude-for-legal/scripts/deploy-managed-agent.sh` | Deploy script: `/v1/skills` + `/v1/agents` (not practice-profile packs). | negative-proof, CLM-0002 | Proving reviewed claim that deploy does not auto-upload profiles/logs. | Primary source (pinned) |

---

## 12. Local-only (not public endpoints)

These are **gitignored**. They have **no public authority** and may be absent on a remote-only clone.

| Path | What it is | Tags | Use when | Authority |
|---|---|---|---|---|
| `private/white-paper/ajax-line-research-agenda/` | Private drafts, portfolio, simulation, research-program packet. | private, white-paper | Local writing/research only. | None (unpublished) |
| `private/white-paper/ajax-line-research-agenda/research-program/00_WRITING_AI_FRONT_DOOR.md` | Private writing-AI packet entry. | private, writing-ai | Local paper drafting. | None (unpublished) |
| `private/white-paper/ajax-line-research-agenda/research-program/READ_ONLY_REVIEW_HANDOFF.md` | Read-only critique handoff for another AI. | private, review | Local pattern-hunt reviews. | None (unpublished) |
| `private/` / `.private/` | Ignored raw research, journals, captures. | private | Never copy into public artifacts. | Outside public authority |

---

## 13. Validation commands (navigation health)

From [`MACHINE_NAVIGATION_MANIFEST.json`](MACHINE_NAVIGATION_MANIFEST.json):

```text
python scripts/validate_navigation.py
python scripts/validate_roadmap.py
python scripts/validate_release_readiness.py
python scripts/validate_release_readiness.py --require-ready   # must FAIL while blocked
python scripts/public_safety.py
python scripts/validate_argument_mesh.py
python scripts/validate_research_radar.py
python scripts/build_lineage.py --check
```
