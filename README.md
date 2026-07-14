# Claude for Legal — Workflow Sovereignty Audit Lab

This repository is an evidence-first audit harness for the public Anthropic repository [`anthropics/claude-for-legal`](https://github.com/anthropics/claude-for-legal).

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
Read AGENTS.md in full. Bootstrap the pinned upstream repository if it is absent. Then execute prompts/00-master-orchestrator.md. Do not infer malicious intent from capability. Maintain line-level coverage receipts and a Confirmed / Inferred / Assumed / Unknown claim ledger.
```

For Codex Security:

```text
Use $codex-security:deep-security-scan to run a deep security scan of upstream/claude-for-legal. Treat Markdown prompts, YAML, JSON, MCP manifests, scripts, and GitHub Actions as executable behavior. Use the concrete threat-model guidance in prompts/01-codex-security-deep-scan.md.
```

OpenAI documents `AGENTS.md` as the repository-level instruction mechanism, supports project-scoped custom subagents in `.codex/agents/`, and documents deep scans as the lower-variance repository scan mode. The project configuration here caps concurrent subagents at six and keeps them read-only.

## What the initial static review found

### Confirmed

- The setup workflow asks teams for recent signed agreements and playbooks, extracts actual positions, and writes a reusable local practice profile.
- A shared company profile can contain risk appetite, jurisdictions, regulators, and escalation contacts for use across legal plugins.
- A deal-debrief agent records deviations from the playbook and the attorney's stated rationale.
- A playbook-monitor agent detects repeated deviations and proposes changes to the firm's playbook.
- Managed-agent deployment uploads skill packages to Anthropic's `/v1/skills` endpoint and creates agents through `/v1/agents`.
- MCP manifests expose legal repositories and collaboration systems to Claude subject to connector configuration and permissions.
- The reviewed first-party hooks are empty or absent, and the open repository did not reveal a separate covert analytics or exfiltration client.

### Inferred

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

See [`audit/INITIAL_ASSESSMENT.md`](audit/INITIAL_ASSESSMENT.md) and [`audit/CLAIM_LEDGER.csv`](audit/CLAIM_LEDGER.csv).

## Repository layout

```text
AGENTS.md                         Codex's controlling audit instructions
.codex/                           Six read-only custom agents and concurrency settings
prompts/                          Multi-round investigation prompts
scripts/                          Bootstrap, inventory, pattern scan, worklist, validation
schemas/                          Stable output schemas for AI passes
patterns/                         Seed pattern catalog; agents may add, not overwrite
runtime-lab/                      Safe synthetic dynamic-validation plan
docs/                             Threat model, partner ontology, Kirkland connection
research/                         Questions for Anthropic, firms, and infrastructure vendors
audit/                            Initial evidence map and claim ledger
upstream/                         Pinned source checkout after bootstrap
results/                          Generated inventories, receipts, findings, and reports
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
