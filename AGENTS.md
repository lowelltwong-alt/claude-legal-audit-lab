# AGENTS.md — Evidence-First Deep Audit Instructions

## Mission

Audit the pinned `upstream/claude-for-legal` repository to determine:

1. what legal workflows and judgment signals it captures;
2. where those artifacts are stored and transmitted;
3. which actors and systems can access them;
4. which feedback loops convert attorney behavior into reusable operating policy;
5. whether any source-to-sink path supports covert exfiltration, generalized training, cross-customer learning, or adjacent-market productization;
6. what cannot be answered because the relevant runtime or commercial evidence is closed.

The investigation is not an exercise in proving a preselected accusation. Test three competing hypotheses:

- **H0 — benign adaptation:** customer-specific configuration is used only to perform the customer's requested work.
- **H1 — workflow capture and dependency:** the platform legitimately encodes institutional workflows but gains bargaining power, lock-in, or product insight without violating no-training commitments.
- **H2 — covert secondary use:** customer-specific legal workflows or feedback are retained or used beyond the requested service for generalized model/product improvement or disintermediation.

H2 requires materially stronger evidence than H1.

## Non-negotiable epistemic rules

Classify every material claim:

- **Confirmed:** directly supported by repository lines, runtime capture, contract text, logs, or cited primary sources.
- **Inferred:** logically derived from confirmed facts, with the inference explained.
- **Assumed:** a temporary premise used for a test or counterfactual.
- **Unknown:** not observable in the available evidence.
- **Contradicted:** affirmative evidence weighs against the claim.

Do not describe capability as intent. Do not describe inference-time processing as training. Do not describe local persistence as provider retention. Do not describe an external URL as exfiltration unless user-controlled data can reach it. Do not call the system a Trojan horse unless the secondary-use chain is supported.

## Scope

Treat all of these as potentially executable or security-relevant:

- Markdown system prompts, skills, agents, and instructions;
- YAML and JSON manifests;
- `.mcp.json` connectors;
- hooks;
- GitHub Actions;
- shell and Python scripts;
- update/install workflows;
- documentation that governs actual setup or deployment;
- commit history, issues, and pull requests where available.

The proprietary Claude runtime, hosted connectors, logging, telemetry, support systems, and training infrastructure are out of source scope. Record them as proof gaps and design runtime or contractual tests.

## High-value assets

Trace these separately:

1. client and matter documents;
2. practice profiles and shared company profiles;
3. playbook positions and fallback rules;
4. risk appetite and deal-breakers;
5. escalation and approval matrices;
6. attorney corrections, accepted/rejected proposals, and rationales;
7. deviation logs and outcome history;
8. matter taxonomies and ontology mappings;
9. tool traces, agent traces, and audit logs;
10. connector credentials and permission scopes;
11. benchmark/evaluation sets;
12. prompt/skill definitions and local customizations.

## Required investigation surfaces

Inspect and cross-reference at least:

- every `cold-start-interview` skill;
- every practice-profile `CLAUDE.md` template;
- shared company-profile handling;
- `deal-debrief`, `playbook-monitor`, review-proposal, and matter-workspace logic;
- every `.mcp.json` and wildcard MCP tool declaration;
- scheduled/managed agent manifests and subagents;
- `/v1/skills` upload and `/v1/agents` deployment;
- hooks and update/install logic;
- external plugins and registry trust boundaries;
- telemetry/analytics/support/feedback references;
- cross-plugin, cross-matter, and prior-session context rules;
- output, audit, and provenance handling;
- security controls that weigh against the hostile hypothesis.

## Source-to-sink standard

For any exfiltration or secondary-use candidate, document:

```text
source asset
-> read authority
-> transformation
-> transmission mechanism
-> destination/operator
-> retention evidence
-> secondary-use evidence
-> customer control/consent
```

A missing retention or secondary-use step prevents a finding of covert training. It may still support a privacy, privilege, lock-in, or architectural-risk finding.

## Line-level coverage

1. Run `make audit` to generate `results/inventory.json`, `results/coverage.csv`, pattern matches, and six balanced worklists.
2. Every assigned file must receive a receipt in `results/coverage-receipts/<worker>.jsonl`.
3. A receipt must include path, SHA-256, lines reviewed, status, and notes.
4. Do not mark a file reviewed from a search snippet alone. Read it in full or mark deferred with a reason.
5. Include negative evidence: files and searches that materially weigh against a hypothesis.

## Multi-pass method

### Phase A — six independent discovery passes

Spawn six read-only workers with the same brief in `prompts/10-independent-discovery-worker.md`. Do not show workers one another's findings. The purpose is variance reduction, not specialization.

Collect all six outputs before merging.

### Phase B — merge and pattern mining

Use `prompts/20-merge-and-pattern-mine.md` to:

- deduplicate only where one remediation/test would resolve all merged candidates;
- extract new search patterns from completed findings;
- add generated patterns to `patterns/generated-patterns.json` without overwriting seed patterns;
- create a new targeted worklist.

### Phase C — specialized passes

Use the project-scoped custom agents for:

- data-flow tracing;
- prompt/instruction semantics;
- permission and connector review;
- runtime-boundary/proof-gap analysis;
- skeptical falsification;
- commit/issue history when available.

### Phase D — counterfactual Trojan-horse analysis

Use `prompts/30-counterfactual-trojan-horse.md`. First construct the strongest plausible mechanism, then compare every required component with observed evidence. Mark absent components explicitly.

### Phase E — falsification

Use `prompts/40-skeptical-rebuttal.md`. Search for benign explanations, local-storage controls, permission constraints, human-approval gates, explicit no-cross-context rules, and architecture that keeps artifacts customer-controlled.

### Phase F — runtime and contract plan

Use `prompts/50-runtime-validation.md`. Do not claim runtime tests occurred unless logs and artifacts exist.

### Saturation rule

Continue rounds until a completed round yields no new material pattern classes or source-to-sink candidates. Partial or failed rounds do not establish saturation. Cap at ten rounds and state if capped.

## Finding format

Each candidate must contain:

- stable ID;
- title;
- claim status;
- affected assets;
- exact file and line evidence;
- source-to-sink chain;
- what the evidence proves;
- what it does not prove;
- strongest alternative explanation;
- confidence and risk;
- test or evidence needed to confirm/refute;
- relation to H0, H1, and H2.

Use `schemas/pass-result.schema.json` for machine-readable pass output.

## Special issue: partner-judgment ontology

Treat “partner thought ontology” as a testable operational construct, not mind reading. Look for code that captures:

```text
issue/fact pattern
-> preferred position
-> fallback
-> prohibited outcome
-> severity
-> escalation threshold
-> contextual exception
-> rationale
-> final decision/outcome
-> later acceptance/rejection of a proposed policy update
```

Determine whether those fields remain local, are sent to a model for inference, are uploaded as skills, or are available to remote connectors. Separate the firm's ontology from generic legal taxonomy.

## Final report

Lead with the scope boundary. Then present:

1. confirmed architecture;
2. workflow/judgment assets captured;
3. data-flow map;
4. evidence for and against H0/H1/H2;
5. validated findings;
6. proof gaps;
7. runtime/contract tests;
8. implications for law firms and the Kirkland/Palantir sovereign-build comparison.

Do not use sensational labels in the conclusion unless the evidence meets the stated threshold.
