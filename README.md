# Claude for Legal — Workflow Sovereignty Audit Lab

AI systems and new investigators should start at [`AI_FRONT_DOOR.md`](AI_FRONT_DOOR.md). Its table of contents and machine registries preserve the distinction between primary sources, reviewed claims, derived analysis, and generated candidate evidence.

The executable project plan is [`docs/ROADMAP.md`](docs/ROADMAP.md), backed by
`registry/project-roadmap.json`. Public release is currently **BLOCKED** by the
separate fail-closed `registry/release-readiness.json` gate; structural validation
of that blocked record is not permission to rename, stage, or publish the repository.

This repository is an evidence-first audit harness for the public Anthropic repository [`anthropics/claude-for-legal`](https://github.com/anthropics/claude-for-legal). It now also contains a candidate-only cross-industry ontology-exposure research method and the manual **Cassandra Radar** for tracking public developments.

It also includes an offline, synthetic-only **Odysseus counterfactual**: a 23-stage model of how a frontier provider could infer a firm's operational and professional-judgment ontologies from ordinary product signals, plus the controls and evidentiary limits that prevent that model from becoming an extraction system. Start at [`docs/FRONTIER_LAB_ONTOLOGY_CAPTURE_COUNTERFACTUAL.md`](docs/FRONTIER_LAB_ONTOLOGY_CAPTURE_COUNTERFACTUAL.md).

The candidate **Ajax Line** thesis argues that law firms should hold a
collective boundary around attorney brain-trust data and derived professional
knowledge because peer exposure may weaken even a protective holdout through
overlapping ontology. It preserves the no-current-pooling objection, the
AlphaGo Zero counterpoint, falsifiers, and proof gaps. Start at
[`docs/AJAX_LINE_COLLECTIVE_BRAIN_TRUST.md`](docs/AJAX_LINE_COLLECTIVE_BRAIN_TRUST.md).

The current controlled spine is [`docs/THESIS_MAP.md`](docs/THESIS_MAP.md),
backed by `registry/thesis-map.json`. The unpublished local explorer is
`public/generated-release-artifacts/candidate/index.html`. It is self-contained,
read-only, makes no external requests, and is explicitly **not** an authorized
release.

Current deterministic coverage:

- 438 full-SHA byte-exact static chunks and 246 inverse adjacency edges;
- 14 verified merged-PR linkages, 5 bounded open/unmerged snapshots, and 57
  unknown or incomplete PR linkages;
- 994 typed evidence nodes and 4,738 inverse-paired graph edges;
- 18 claims: only `CLM-0002` is reviewed and export-eligible; the other 17 are
  blocked, quarantined, or retired;
- 7 candidate thesis nodes and 7 hash-genealogized preview paragraphs, all
  release-blocked.

New raw captures and internal build journals belong only under ignored
`private/`. Legacy `.private/` remains read-only hold. Neither path may appear
in a public builder or export.

## Contributions and licensing status

The contribution model is documented, but outside intake is **preview/closed**.
The current root `LICENSE` is only an Apache-2.0 application notice rather than
the complete license text, and its copyright holder is not identified. Read
[`CONTRIBUTING.md`](CONTRIBUTING.md) and
[`docs/LICENSING_OPTIONS.md`](docs/LICENSING_OPTIONS.md) before proposing work.
No monitoring automation or license change is authorized by these files.

For research beyond law, start with
[`docs/CROSS_INDUSTRY_ONTOLOGY_RISK.md`](docs/CROSS_INDUSTRY_ONTOLOGY_RISK.md)
and [`docs/RESEARCH_RADAR.md`](docs/RESEARCH_RADAR.md).

It is designed to answer four different questions without collapsing them into one:

1. **What does the public plugin code actually do?**
2. **What institutional knowledge does it ask a legal team to encode?**
3. **What data can reach Anthropic or third-party systems at inference time?**
4. **Is there evidence that Anthropic retains, trains on, generalizes from, or productizes customer-specific legal workflows?**

The first three questions can be investigated from code, runtime observation, and contracts. The fourth cannot be answered from suggestive language alone. It requires a source-to-sink path, retention evidence, product-use evidence, contractual rights, internal documents, or independently verifiable runtime behavior.

## Important scope boundary

The public repository is mostly Markdown prompts, YAML/JSON manifests, MCP connector declarations, and a small deployment/orchestration harness. It is **not** the full proprietary Claude runtime, server-side logging stack, model-training pipeline, product analytics system, or connector implementation. A clean review of this repository cannot establish that those closed systems are clean. Conversely, workflow-capture language in this repository does not by itself prove covert training or an intent to replace law firms.

See [`docs/SCOPE_BOUNDARY.md`](docs/SCOPE_BOUNDARY.md).

## Upstream version reviewed

The audit is pinned to:

- Repository: `anthropics/claude-for-legal`
- Commit: `5ceb305b30b4c82653c9b6642499c12e946ec319`
- Review date: `2026-07-14`

Run:

```bash
make bootstrap
make audit
make test
```

`make bootstrap` clones the exact upstream commit into `upstream/claude-for-legal/` and verifies the commit hash. The upstream source is not duplicated in this package because the current build environment could not reach GitHub directly. The bootstrap script is pinned and fail-closed.

## Fast start with Codex

Open this repository in Codex and use:

```text
Read AGENTS.md in full. Bootstrap the pinned upstream repository if it is absent. Then execute prompts/00-master-orchestrator.md. Do not infer malicious intent from capability. Keep claim lifecycle, epistemic status, review state, and publication eligibility separate, and preserve exact source/chunk genealogy.
```

For Codex Security:

```text
Use $codex-security:deep-security-scan to run a deep security scan of upstream/claude-for-legal. Treat Markdown prompts, YAML, JSON, MCP manifests, scripts, and GitHub Actions as executable behavior. Use the concrete threat-model guidance in prompts/01-codex-security-deep-scan.md.
```

OpenAI documents `AGENTS.md` as the repository-level instruction mechanism, supports project-scoped custom subagents in `.codex/agents/`, and documents deep scans as the lower-variance repository scan mode. The project configuration here caps concurrent subagents at six and keeps them read-only.

## Legacy static orientation — candidate, not export-eligible

The bullets below preserve the original orientation only. They are not a
publication-ready claim set. Resolve current status through
`registry/claim-registry.json`, `registry/evidence-graph.json`, and each
`does_not_prove` boundary; only `CLM-0002` currently passes the reviewed exact
chunk-genealogy gate.

### Candidate static observations

- The setup workflow asks teams for recent signed agreements and playbooks, extracts actual positions, and writes a reusable local practice profile.
- A shared company profile can contain risk appetite, jurisdictions, regulators, and escalation contacts for use across legal plugins.
- A deal-debrief agent records deviations from the playbook and the attorney's stated rationale.
- A playbook-monitor agent detects repeated deviations and proposes changes to the firm's playbook.
- Managed-agent deployment uploads skill packages to Anthropic's `/v1/skills` endpoint and creates agents through `/v1/agents`.
- MCP manifests expose legal repositories and collaboration systems to Claude subject to connector configuration and permissions.
- The reviewed first-party hooks are empty or absent, and the open repository did not reveal a separate covert analytics or exfiltration client.

### Candidate hypotheses

- The design is a closed-loop institutional-learning system at the customer level: it converts examples, corrections, exceptions, rationales, and approvals into an evolving operating policy.
- That operating policy can approximate a **partner-judgment ontology**: not a copy of a lawyer's mind, but a structured map from facts and issues to preferred positions, exceptions, escalation thresholds, rationale, and outcomes.
- Even where files persist locally, relevant portions necessarily reach the selected model during inference unless the architecture performs local decomposition or uses a self-hosted model.
- The principal visible strategic risk is workflow dependence and control-plane lock-in, not demonstrated covert training.

### Unknown

- Server-side retention by feature and deployment mode.
- Product analytics, support access, abuse-monitoring access, and human review outside the public repository.
- Whether customer-specific workflows are used for generalized evaluation, fine-tuning, product discovery, or cross-customer product development.
- Whether a deployed connector copies, indexes, caches, or only retrieves content.
- Anthropic's internal intent.

See [`audit/INITIAL_ASSESSMENT.md`](audit/INITIAL_ASSESSMENT.md) and [`audit/CLAIM_LEDGER.csv`](audit/CLAIM_LEDGER.csv) as legacy orientation only.

## Repository layout

```text
AGENTS.md                         Codex's controlling audit instructions
.codex/                           Six read-only custom agents and concurrency settings
prompts/                          Multi-round investigation prompts
scripts/                          Bootstrap, inventory, pattern scan, worklist, validation
schemas/                          Stable output schemas for AI passes
registry/                         Authority, chunk, graph, claim, thesis, and export manifests
patterns/                         Seed pattern catalog; agents may add, not overwrite
runtime-lab/                      Safe synthetic dynamic-validation plan
docs/                             Threat model, partner ontology, Kirkland connection
research/                         Questions for Anthropic, firms, and infrastructure vendors
audit/                            Initial evidence map and claim ledger
upstream/                         Pinned source checkout after bootstrap
results/                          Generated inventories, receipts, findings, and reports
private/                          Ignored raw research and internal journals; never public
public/generated-release-artifacts/candidate/  Blocked paper preview and local explorer
tests/                            Offline tests for the audit scripts
```

## Evidentiary rule

A “Trojan horse” conclusion requires more than evidence that a product learns a customer's workflow. At minimum, require a supported chain such as:

```text
protected workflow artifact
  -> code/runtime access
  -> transmission to a remote party
  -> retention or derivation
  -> secondary use outside the customer's requested service
  -> strategic product or model benefit
```

Every missing arrow must be marked **Unknown**, not filled with rhetoric.

## Legal and ethical note

Use only authorized repositories, test tenants, synthetic documents, and data you are permitted to inspect. Do not test cross-tenant leakage against real customers, attempt credential access, or place privileged/client information into an experimental environment.
