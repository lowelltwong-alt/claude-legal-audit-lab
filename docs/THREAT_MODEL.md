# Threat model: legal-workflow sovereignty audit lab

## Overview

This repository is a public research harness for auditing a pinned public
`anthropics/claude-for-legal` revision, preserving source and claim genealogy,
running synthetic-only runtime tests, and modeling legal-workflow sovereignty.
It is not a production legal system, a telemetry collector, a model-training
pipeline, or a repository for client, matter, personnel, or firm data.

The highest-value repository assets are:

- the public/private release boundary and ignored private research workspace;
- exact source identities, hashes, locators, claim status, and derivation
  genealogy;
- the distinction between observed fact, inference, assumption, unknown, and
  contradicted or constrained propositions;
- synthetic-only test and counterfactual boundaries;
- public contribution and release gates;
- connector, token, credential, and system-path non-disclosure; and
- the integrity of the pinned upstream source and generated coverage receipts.

## Threat Model, Trust Boundaries, and Assumptions

### Actors

- repository owner and named human reviewers;
- researchers and contributors;
- AI workers, checkers, and orchestrators;
- the pinned upstream publisher and mutable external public sources;
- Git hosting, CI, package, model, connector, and documentation providers;
- malicious or careless contributors and prompt authors; and
- readers who may mistake a capability, generated edge, or counterfactual for
  actual conduct or intent.

### Trust boundaries

1. Private working material to public tracked release surface.
2. Pinned upstream bytes to locally generated inventories, matches, and claims.
3. Mutable web source to dated source metadata and later white-paper use.
4. Untrusted Markdown, YAML, JSON, issue, PR, and upstream content to an AI or
   executable tool context.
5. Authored registry to deterministic generated graph or report.
6. Candidate evidence to reviewed claim or public conclusion.
7. Synthetic fixture to any proposed real-firm runtime test.
8. Local files and configuration to a model context.
9. Model runtime to MCP connector and third-party system.
10. Contribution preview to any future intake, automation, CI, or publication.

### Inputs by controller

- **Attacker-controlled:** public contributions, issue text, upstream content,
  Markdown instructions, fixtures, URLs, JSON/YAML, plugin or MCP manifests,
  and mutable web content.
- **Operator-controlled:** source and claim registries, private research,
  allowlists, runtime fixtures, configuration, approval, release, and retention.
- **Developer-controlled:** schemas, validators, build scripts, prompts,
  navigation, tests, and CI if later enabled.

### Security and epistemic invariants

- No private, secret, client, matter, prospective-client, conflicts, personnel,
  billing, trust, or real telemetry data enters the public repository.
- No untrusted upstream or contribution is executed merely because it appears
  in a repository or prompt.
- Generated graphs, chunks, matches, and reports remain candidate evidence.
- A claim cannot advance without exact evidence, locator, epistemic status,
  does-not-prove boundary, and human review.
- Processing, retention, telemetry, feedback, secondary use, and training are
  distinct propositions.
- Public filings do not establish complete internal legal strategy.
- Counterfactual code remains deterministic, offline, and synthetic-only.
- Acquisition or partnership does not imply privilege waiver, client authority,
  or permission to direct professional judgment.

## Attack Surface, Mitigations, and Attacker Stories

### Public/private boundary failure

An accidental commit, generated manifest, screenshot, local path, raw capture,
or Git history could expose private research or protected data. `.gitignore` is
only one control. Mitigations include an ignored private workspace, tracked-file
inventory, allowlist-based release, redacted privacy scanning, manual review,
and named human approval. Publishing remains blocked if a private path is
tracked or history exposure is plausible.

### Prompt and contribution injection

Markdown and structured files may contain instructions intended to redirect an
AI, access data, run tools, weaken evidence standards, or publish material.
Treat content as untrusted evidence, not authority. Repository `AGENTS.md`,
source-of-truth, design-authority, schema, and human gates control. Do not run
upstream code or contributor commands without review and authorization.

### Supply-chain and connector abuse

Scripts, CI actions, packages, plugins, MCP servers, and connectors could read
secrets, expand scope, mutate data, or transmit content. The present public
counterfactual builder uses only Python's standard library and local committed
registries. Any future dependency, automation, connector, or network path
requires separate threat modeling, pinning, least privilege, and approval.

### Lineage and claim-integrity attack

A contributor could bind a claim to the wrong source, omit a counterexample,
use a mutable URL without a date, overstate a generated match, or silently
change a parent artifact. Deterministic builders verify references, hashes,
cycles, source closure, routing, and stale projections. Human review remains
necessary for semantic correctness and source adequacy.

### Counterfactual-to-collector drift

A future change could add networking, telemetry SDKs, credentials, environment
or home-directory reads, real logs, identity linkage, deceptive prompts, or a
flag that turns the exposure graph into live collection. The safety policy,
tests, decision record, and human gate reject that transition. The repository
contains no authorized real-data mode.

### Legal-ontology overclaim

Token counts could be treated as substantive strategy; public filings as the
complete private process; ordinary service processing as training; optional
feedback as default use; or a partnership as proof of capture. Required
limitations, competing hypotheses, current official terms, and source-to-sink
standards mitigate these epistemic failures.

### Realistic attacker stories

- A contributor hides a local file or credential in a fixture or generated
  output and gets it published.
- An upstream Markdown file instructs an agent to ignore repository policy and
  exfiltrate local data.
- A mutable provider page changes, while a stale claim is presented as current.
- A generated graph edge is cited as proof of actual retention or intent.
- A new "test" silently reads real prompts, logs, files, identities, or matter
  metadata.
- A public docket model infers sealed or internal strategy without a limitation.

### Out-of-scope or lower-realism stories

The repository does not host an authentication service, production web server,
payment processor, client portal, or multi-tenant runtime. CSRF, session theft,
tenant authorization, and production database injection are not primary risks
unless such a runtime is later added. A provider's internal training or logging
system is outside this source tree; it must be tested through authorized runtime,
contractual, audit, or primary-source evidence rather than assumed here.

## Severity Calibration (Critical, High, Medium, Low)

### Critical

- Public release of real privileged, confidential, client, conflicts, trust,
  credential, or sealed material.
- Code that covertly collects or transmits real firm interactions or crosses
  client, matter, tenant, or ethical walls.
- A production-capable path for privilege circumvention, credential theft, or
  irreversible external mutation.

### High

- Tracking the ignored private workspace, publishing raw captures or sensitive
  local paths, or exposing protected Git history.
- Enabling deceptive elicitation, identity-linked attorney surveillance,
  cross-firm aggregation, or live telemetry through a simple flag.
- Validator or lineage failure that permits unsupported hostile-intent or
  secondary-use claims to appear reviewed.
- Executing untrusted upstream or contribution content with local write,
  credential, network, or connector authority.

### Medium

- Stale source metadata, broken source closure, ambiguous routing, or a missing
  does-not-prove statement that materially weakens a candidate analysis.
- Synthetic fixture re-identification risk, incomplete public-record warnings,
  or unreviewed provider-policy drift.
- Dependency or connector scope broader than documented but without evidence of
  protected-data access.

### Low

- Broken formatting, non-authoritative generated-file drift caught before
  release, stale descriptive navigation without authority inversion, or a
  non-sensitive local test failure.
- Research disagreement that preserves evidence and epistemic status. Such a
  disagreement belongs in the correction process, not security reporting.
