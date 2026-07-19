# Cross-Industry Ontology Exposure Research

## The research question

Which industries combine (a) deeply encoded expert judgment, (b) large digital
workflow traces, (c) feedback about accepted, rejected, corrected, or successful
decisions, and (d) growing frontier-model integration? Those conditions can
make an institutional ontology economically important and technically exposed.
They do **not** prove that a provider captures, owns, trains on, or misuses it.

Public provider statements now show frontier models being connected to systems
of record, internal tools, agent workflows, and industry-specific platforms in
finance, healthcare, life sciences, insurance, manufacturing, banking, energy,
communications, airlines, government, cybersecurity, and creative production.
The registry records those statements as evidence of market direction—not
evidence of covert intent or secondary use.

Primary-source starting points include Anthropic's
[financial-services](https://www.anthropic.com/news/claude-for-financial-services),
[healthcare and life-sciences](https://www.anthropic.com/news/healthcare-life-sciences),
[DXC regulated-industries](https://www.anthropic.com/news/dxc-anthropic-alliance),
[UST physical-AI](https://www.anthropic.com/news/ust-claude), and
[creative-work](https://www.anthropic.com/news/claude-for-creative-work)
announcements, plus OpenAI's
[Frontier](https://openai.com/business/frontier/),
[Travelers claims](https://openai.com/index/travelers/), and
[PwC finance](https://openai.com/index/openai-pwc-finance-collaboration/)
pages. Exact source identities and limitations are in
`registry/source-registry.json` (`SRC-0017` through `SRC-0024`).

## What counts as an ontology here

An institutional ontology is more than a document collection. The highest-value
layer may include:

- preferred rules, positions, and classifications;
- acceptable fallbacks and prohibited outcomes;
- context-specific exceptions;
- risk thresholds and escalation authority;
- rationale for a decision;
- corrections, approvals, and rejections;
- realized outcomes and policy revisions;
- evaluation sets that distinguish good from merely plausible work.

## Research-priority methodology v1.0.0

This is a deterministic research-routing method, not a probability of harm and
not a finding that ontology capture occurs.

Each industry receives six separately evidenced ordinal facets:

| Facet | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| `O` ontology depth | documents only | procedures | rules, exceptions, escalation | plus rationale, outcomes, revision |
| `F` feedback capture | none evidenced | use/output counts | correction or accept/reject | plus rationale, outcomes, recurring update |
| `X` external exposure | customer-local | transient external processing | hosted state or connected systems | evidenced telemetry, aggregation, or secondary-use path |
| `C` consequence | low | operational inconvenience | regulated, confidential, or material | safety-critical, fiduciary, privileged, or irreversible |
| `P` portability/control dependency | open export and tested replacement | portable but untested | material provider-specific integration | provider controls ontology/evaluation/orchestration |
| `E` evidence readiness | no primary source | primary source identified | captured metadata and locator | reproducible bytes/exact span plus independent review |

Priority is computed exactly:

- `P0`: `O >= 2`, `F >= 2`, `C >= 2`, either `X >= 2` or `P >= 2`, and `E >= 2`.
- `P1`: the same structural profile, but `E < 2`; acquire primary evidence.
- `P2`: exactly two or three of `O`, `F`, `X`, `C`, and `P` are at least `2`,
  and `E >= 2`.
- `P3`: every other discovery lead.

Tie-breaker order for a bounded work queue is `E`, then `C`, then `O`, then
stable `industry_id`, all descending except the ID. Unknown facet values are
stored as `null`, never silently converted to zero, and force `P1` or `P3`
until resolved. A validator recomputes every priority.

## Initial map

The public registry starts with candidate profiles, not accusations.

| Research lane | Why the ontology may matter | Publicly observed market direction |
|---|---|---|
| Healthcare payer/provider | coverage policy, coding, prior authorization, clinical criteria, appeals, handoffs | connectors and skills for coverage, records, coding, prior authorization, and claims workflows |
| Life sciences/pharma | protocols, target selection, trial operations, safety escalation, regulator strategy | provider support across discovery, trials, regulatory work, and commercialization |
| Financial services | risk appetite, models, due diligence, compliance, portfolio decisions | connected market/internal data and agentic analysis workflows |
| Insurance | underwriting rules, claims triage, exceptions, loss outcomes | underwriting and claims systems connected to frontier models |
| Manufacturing/semiconductors | design rules, tolerances, validation, root cause, sign-off, corrective action | model integration into schematics, tests, digital twins, and factory/validation processes |
| Accounting, tax, and corporate finance | materiality, controls, close, tax positions, review hierarchy | agents aimed at forecasting, reporting, procurement, payments, treasury, tax, and close |
| Cybersecurity | detection thresholds, response playbooks, exceptions, escalation, postmortems | security subagents entering managed security operations |
| Energy/utilities | operational constraints, failure response, siting, mitigation, asset knowledge | frontier-agent deployments for production and disaster-impact decisions |
| Aviation and airlines | maintenance, dispatch, safety, disruption recovery, operating procedures | forward-deployed model integration into mission-critical airline systems |
| Government/public administration | eligibility, procurement, case handling, enforcement, public-service procedures | industry-specific deployments into government systems |
| Creative/design production | style systems, tool chains, asset decisions, iterative feedback | connectors spanning design, 3D, audio, video, and production pipelines |

These lanes are hypotheses about where research is valuable. A high priority
means “investigate carefully,” not “harm is occurring.”

## Falsifiers and protective evidence

The radar must actively seek:

- customer-local execution and storage;
- zero or short retention with auditable deletion;
- no-training and no-secondary-use contractual controls;
- scoped connectors and least-privilege permissions;
- customer-owned skills, evaluation sets, orchestration, and encryption keys;
- complete export and tested provider replacement;
- tenant isolation and customer-visible audit logs;
- evidence that corrections and outcomes stay inside the customer boundary.

The strongest research product will show both ontology exposure paths and the
controls that make a deployment genuinely customer-sovereign.
