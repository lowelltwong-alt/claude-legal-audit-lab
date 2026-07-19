# Defensive counterfactual: how a frontier lab could map a law firm's ontology

## Scope and safety boundary

This is a threat model, not an extraction plan. It asks:

> If a frontier AI provider wanted to learn a law firm's operating system and
> institutional judgment without receiving a folder labeled "client data,"
> which ordinary product interactions would be valuable, what could they
> actually reveal, and what controls would keep the firm's alpha under firm
> custody?

The executable code in this repository is deliberately unable to collect that
information. It reads committed public registries, uses no network, credentials,
home directory, clipboard, browser state, production logs, telemetry SDK, or
real user input, and produces only a deterministic candidate graph. Do not turn
this model into deceptive elicitation, covert collection, cross-firm
aggregation, individual attorney scoring, or privilege circumvention.

This is not a factual allegation that Anthropic, Palantir, or any other company
performs the modeled acts. The pinned public `claude-for-legal` code establishes
a customer-level workflow-learning design; it does not establish provider
retention, generalized training, cross-customer normalization, product
discovery, or concealed intent.

## The four assets that must not be collapsed

| Plane | What it contains | Relative inferability | Core boundary |
|---|---|---|---|
| Operational/process ontology | Stages, roles, queues, templates, task codes, tools, handoffs, approvals, exceptions, time, billing, and cash cycle | Often inferable from metadata and sequences without document text | Metadata combinations may still identify a client, matter, lawyer, or strategic priority |
| Professional-judgment ontology | Issue framing, option selection, risk weighting, fallbacks, edits, escalation, rationales, quality standards, and outcomes | Requires context–choice–rationale–outcome links; much harder without matter content | It is an operational representation of judgment, not mind reading or ground truth |
| Client/matter content | Identities, facts, communications, evidence, drafts, objectives, advice, financial and personal data | Semantically richest and most restricted | Ethical confidentiality is broader than attorney-client privilege; privilege, work product, privacy, and trade secrets remain distinct |
| Public-derived evidence | Dockets, filed documents, opinions, public deal records, biographies, and public statements | Useful for visible advocacy, timing, actors, and outcomes | It cannot reveal sealed material, unfiled work, abandoned arguments, confidential settlements, client objectives, or internal deliberation |

The machine-readable definitions and full 23-stage law-firm lifecycle are in
`registry/law-firm-value-chain.json`. They cover business development,
pre-intake, conflicts, acceptance, engagement, matter opening, staffing, facts,
research, strategy, drafting, negotiation or advocacy, quality, client advice,
resolution, timekeeping, billing, collections and cash, closure, knowledge,
talent, technology, and firm governance.

## The counterfactual frontier-lab workflow

The strongest hypothetical path is not "steal the documents." It is a gradual
conversion of ordinary service interactions into structured operating evidence:

```text
useful product earns deployment
  -> transparent or opaque configuration maps declared policy
  -> workflow and tool traces map operating topology
  -> edits, overrides, and escalations reveal decision boundaries
  -> rationales and debriefs link context, choice, and outcome
  -> evaluation sets define what the firm considers good or dangerous
  -> cross-matter normalization proposes an effective playbook
  -> hosted orchestration, connectors, and evaluation create control-plane dependency
  -> the provider can explore adjacent workflow products
```

Every arrow is separate. Observing the first three does not prove the later
ones. Retention, secondary use, cross-customer combination, training, and
strategic product use each require their own evidence.

### 1. Earn the right to sit inside the workflow

A high-value assistant solves research, review, drafting, intake, billing, or
knowledge problems well enough that users repeatedly supply context and accept
integration. The defensive question is not whether the product is useful. It is
which system of record, ontology, evaluation, and logging layers become
provider-controlled as usefulness grows.

### 2. Map the declared ontology

Onboarding, playbooks, templates, escalation matrices, matter taxonomies, and
quality rubrics can reveal the formal operating model without raw client files.
This can be consensual and beneficial. The risk changes when purpose, derived
rights, retention, or refusal consequences are vague.

### 3. Map the operational ontology from metadata

Tool names, workflow identifiers, role and handoff sequences, input/output/cache
token counts, latency, recurrence, approvals, retries, task codes, time, invoice
rejections, and collections can reveal workload shape, systems of record,
bottlenecks, economic priorities, and automation boundaries.

Token counts alone are weak semantic evidence. They do **not** reveal a legal
position or prove strategy. Their value comes from joins with stage, tool, role,
time, correction, and outcome. Those same joins increase re-identification and
confidentiality risk.

### 4. Map the professional-judgment ontology

The highest-value sequence is:

```text
facts or issue context
  -> proposed option
  -> accept / reject / edit / escalate
  -> rationale
  -> final disposition
  -> outcome or debrief
  -> proposed playbook update
```

Redline deltas reveal fallback language and issue priority. Overrides reveal
automation limits. Escalations reveal authority. Evaluation sets reveal the
definition of "good." Debriefs reveal why a rule bent. Outcomes add value but
are confounded by facts, counterparties, judges, markets, budgets, and client
preferences; they cannot be treated as causal proof.

### 5. Reconstruct what is visible from public records

Public dockets can support graphs of counsel, judges, issues, authorities,
filing sequences, visible arguments, timing, and disposition. They cannot
recover confidential advice, internal alternatives, unfiled discovery,
settlement authority, private negotiation history, or why a client chose a
position. Federal records also exclude sealed and restricted material. A public
strategy model is therefore a partial, selection-biased prior—not the firm's
brain trust.

### 6. Deepen control through co-development or ownership

Co-development can expose architecture, taxonomy, evaluation, exception, and
roadmap information even when client documents remain firm-controlled. An
investment or acquisition could create deeper operating access, but it is not a
privilege shortcut. Ownership, fee sharing, nonlawyer control, professional
independence, conflicts, confidentiality, fiduciary duties, unauthorized
practice, and client rights are jurisdiction-specific. The ABA Model Rule 5.4
model generally restricts nonlawyer ownership and control; regulated alternatives
exist in some jurisdictions. This repository models only the governance
questions and contains no transaction or evasion playbook.

## What data would be valuable without client documents?

| Signal class | What it may reveal | What it does not prove | Defensive default |
|---|---|---|---|
| Input/output/cache tokens, latency, cost | Workload size, recurrence, stage bottlenecks, model dependence | Legal meaning, quality, strategy, or training | Aggregate firm-side; remove stable identities; short retention; separate billing/security from product analytics |
| Prompt and output categories | Issue classes, desired work products, workflow gaps | Retention, secondary use, or correctness | Content logging off; task-minimum context; matter gateway; verified deletion |
| Accept/reject/regenerate/edit | Trust thresholds, resisted proposal classes, candidate policy drift | Ground truth or reason without context | Keep decision object local; no individual ranking; coarse approved export only |
| Redline deltas | Preferred language, drafting standards, fallback and concession hierarchy | Why a change occurred or whether it generalizes | Local extraction; matter isolation; no raw-text retention; human abstraction review |
| Tool and handoff sequence | Process graph, system dependency, role and approval topology | Substantive legal reasoning | Allowlist names; exclude parameters/results; firm-owned observability |
| Escalations and exceptions | Authority graph, severity thresholds, risk posture | Individual competence or universal policy | Role-level aggregation; suppress names and rationales; minimum cohorts |
| Rationales and debriefs | Context-dependent professional judgment and policy evolution | Causation, authority for reuse, or provider intent | Local-only narrative; matter/client authority; source genealogy; no provider-default telemetry |
| Evaluation sets | Quality standards, failure boundaries, definition of "good" | General legal competence | Firm-owned synthetic evaluation; model portability; prohibit provider reuse |
| Time, billing, and cash traces | High-resolution task map, rework, pricing judgment, cash-cycle dependencies | Work quality, value, satisfaction, or solvency | Exclude narratives and payment rails; aggregate locally; segregate duties |
| Support and feedback | Rare failures, edge cases, product gaps | Routine frequency or hostile intent | Feedback off; exact-scope preview; separate rating from transcript consent |

The full 18-pattern catalog, including applicability, non-applicability, danger
if misapplied, sources, consent gates, and countercontrols, is
`registry/counterfactual-capture-patterns.json`.

## Anthropic-specific calibration

The visible repository asks a customer to encode playbooks, fallbacks,
escalation, deviations, rationales, and accepted or rejected policy changes.
That supports the conclusion that the product can create a customer-specific
institutional-learning loop. Some relevant context necessarily reaches the
selected model when the model performs the task, while other configuration may
remain in customer-local files.

The pinned upstream locators for that visible loop are:

| Component | Exact public source | Bounded observation |
|---|---|---|
| Onboarding sources | `commercial-legal/skills/cold-start-interview/SKILL.md` lines 23-25 | Requests playbooks and recent signed agreements as source material |
| Declared practice model | `commercial-legal/skills/cold-start-interview/SKILL.md` lines 72-74 | Describes learning how the team handles commercial contracts and writing a living practice profile |
| Deviation and rationale | `commercial-legal/agents/deal-debrief.md` lines 89-118 | Records signed positions, deviations, bases, and attorney context |
| Pattern-to-rule proposal | `commercial-legal/agents/playbook-monitor.md` lines 50-74 | Groups deviations by direction and basis and proposes candidate rules |
| Human policy decision | `commercial-legal/agents/playbook-monitor.md` lines 135-166 | Captures accept, reject, edit, or defer decisions on proposed changes |

All locators refer to commit
`5ceb305b30b4c82653c9b6642499c12e946ec319`. They establish visible prompt and
workflow behavior only. They do not establish provider-side retention,
cross-customer use, training, or intent.

Anthropic's currently registered public commercial sources state that customer
content is not used to train models under the standard commercial terms, subject
to product, feature, feedback, opt-in, retention, and negotiated-agreement
details. Those statements materially constrain a claim of default training.
They do not, by themselves, answer every question about service processing,
operational metadata, support access, product analytics, derived labels,
subprocessors, deletion, or product discovery. Each proposition must remain
separate and dated.

## Karp, Palantir, and the sovereignty thesis

Palantir publicly describes its Ontology as the layer that encodes enterprise
data, logic, action, security, and Human+AI decisions. That supports the
architectural comparison: a firm can keep its ontology and orchestration under
its own control while using replaceable models.

The stronger wording that Alex Karp specifically proposed "flattening" or
"eating" law firms is **not established by a captured primary source in this
repository**. Treat that wording as a user-supplied research hypothesis until an
exact dated recording or transcript is registered. Do not convert a current
market critique, competitive positioning, or general discussion of enterprise
IP into a claim about law-firm intent.

## The sector externality and Ajax Line

A firm-controlled architecture can protect one firm's source material and
control plane, but it may not eliminate a capability externality created by
other firms exposing substantially overlapping workflows, evaluations, and
judgment patterns. That protective-holdout problem is the subject of the
candidate **Ajax Line** thesis in
`docs/AJAX_LINE_COLLECTIVE_BRAIN_TRUST.md` and its machine-readable objections,
falsifiers, proof gaps, claims, and sources in `registry/argument-mesh.json`.

The thesis is precautionary and normative. It does not establish current
cross-firm pooling, provider intent, measurable competitive harm, or the actual
architecture of Kirkland or any other named firm.

## Defensive architecture

The target architecture is:

```text
firm-owned systems of record
  -> firm-owned ontology and policy
  -> firm-owned orchestration, authorization, telemetry, and evaluation
  -> local decomposition and minimization
  -> replaceable model receives the smallest task fragment
  -> output returns to firm-controlled validation and approval
  -> firm-owned lineage, correction, debrief, deletion, and audit
```

Required controls include matter and ethical-wall isolation, purpose limitation,
specific consent where applicable, content-free observability by default,
separation of security/billing/product analytics, no secondary model or product
use without separate authority, firm-controlled deletion, model portability,
and independent contract/runtime verification.

## Code and graph

Run:

```bash
python scripts/build_counterfactual_graph.py
python scripts/build_counterfactual_graph.py --check
```

The builder deterministically connects:

```text
law-firm stage
  -> artifact and signal
  -> counterfactual exposure pattern
  -> possible ontology inference
  -> evidentiary limitation
  -> defensive control
  -> public source
```

The generated `registry/counterfactual-exposure-graph.json` is candidate
evidence, never source truth. It contains no real telemetry and cannot be
configured into a collector.

Source IDs on authored patterns are catalog-level context. The builder does
not inherit them onto stage, signal, inference, control, or limitation edges.
Only a dedicated source edge may carry a source ID; that edge is labeled
`catalog_context` and carries the source registry's exact locator. All other
edges are labeled `model_derived`. This prevents a provider term, ethics
opinion, or repository locator from appearing to prove every child relation.

## Forbidden graph paths

The public model rejects these routes conceptually and in deterministic
invariants:

- user interaction → undisclosed collection → secondary product use;
- client or prospective-client content → cross-customer aggregation;
- privileged, work-product, or confidential material → unauthorized review;
- firm ontology → training, evaluation, or product discovery without separate explicit authority;
- feedback → transcript or file submission through bundled consent;
- telemetry → individual attorney performance score;
- Matter A → retrieval or inference for Matter B across an ethical wall;
- public filing → claimed complete internal strategy;
- acquisition → assumed privilege access or professional-independence bypass;
- prompt → deceptive or manipulative disclosure request;
- deletion request → undisclosed surviving derived artifact.

The machine gate, not safety prose alone, controls the two highest-risk lanes.
`CF-011` must encode lawful-public-access-only, no sealed or restricted
material, acknowledged selection bias, and no inference of internal
deliberation. `CF-016` must encode no evasion design, no transaction playbook,
and jurisdiction-specific review. Every non-public-source pattern must require
consent and authority, and every pattern must retain at least one contextual
source. Adversarial mutation tests prove these changes fail validation.

## Primary authorities and limitations

- `SRC-0033`: ABA Model Rule 1.6 and comments—confidentiality and reasonable safeguards; the Model Rules are not jurisdiction-specific law.
- `SRC-0034`: ABA Formal Opinion 512—fact-specific AI competence, confidentiality, communication, supervision, candor, and fee considerations.
- `SRC-0035`: ABA Model Rule 5.4—professional-independence model; ownership regimes vary.
- `SRC-0036` and `SRC-0037`: U.S. Courts and PACER—public federal records and important coverage exclusions.
- `SRC-0040`: Arizona's regulated alternative-business-structure program—evidence that ownership rules are not uniform.
- `SRC-0041`: Palantir's official Ontology description—vendor architecture statement, not evidence of any law-firm data custody.
- `SRC-0005`, `SRC-0007`, and `SRC-0009`: Anthropic commercial terms, training statement, and retention documentation—dated public commitments that require feature- and contract-specific verification.

Every legal or ethical source here is a research anchor, not individualized
legal advice. Governing rules, engagement terms, client instructions, product
tier, negotiated contract, runtime settings, and jurisdiction remain material
unknowns.
