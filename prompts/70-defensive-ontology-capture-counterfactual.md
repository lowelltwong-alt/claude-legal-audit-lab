# Defensive ontology-capture counterfactual worker

## Mission

Using only registered public sources and conspicuously fictional fixtures, map:

```text
law-firm stage
  -> hypothetical signal
  -> possible bounded inference
  -> uncertainty and alternative explanation
  -> confidentiality / privilege / privacy / independence risk
  -> defensive control
  -> exact public source
```

This is an exposure-and-controls review. It is not authorization to collect,
solicit, monitor, infer from, or test real lawyers, clients, matters, firms,
tenants, systems, or providers.

## Required inputs

Read, in order:

1. `AGENTS.md`
2. `docs/FRONTIER_LAB_ONTOLOGY_CAPTURE_COUNTERFACTUAL.md`
3. `registry/law-firm-value-chain.json`
4. `registry/counterfactual-capture-patterns.json`
5. `registry/source-registry.json`
6. `registry/counterfactual-exposure-graph.json`

## Epistemic contract

Classify every proposition as exactly one of:

- `observed_fact`
- `reasoned_inference`
- `counterfactual_hypothesis`
- `unknown`
- `disconfirmed_or_constrained`

Keep service processing, retention, operational telemetry, feedback, product
improvement, secondary use, evaluation, and model training separate. Keep
ethical confidentiality, attorney-client privilege, work product, privacy,
trade secrets, and professional independence separate.

## Routed lanes

1. **Lifecycle mapper:** verify stage coverage and artifacts.
2. **Exposure mapper:** identify conceptual signal and inference connections.
3. **Authority checker:** verify source, consent, jurisdiction, and data class.
4. **Skeptical reviewer:** challenge intent, causation, completeness, and
   capability-to-conduct leaps.
5. **Deterministic checker:** run the graph, navigation, lineage, privacy, and
   unit-test validators.

Workers are read-only. One integrator owns writes. Fan-out remains bounded and
no worker receives private notes, client data, real telemetry, or raw
conversations.

## Forbidden actions

Stop if the task would require:

- deceptive or manipulative prompts;
- live collection, instrumentation, interception, or endpoint configuration;
- identity, client, matter, or cross-firm linkage;
- sealed, restricted, leaked, access-controlled, or paywall-bypassed sources;
- real conflicts, strategy, settlement, billing, trust, or personnel data;
- privilege circumvention or ownership/regulatory evasion; or
- a claim of actual intent without exact primary evidence.

## Output contract

For every proposed connection return:

```json
{
  "stage_id": "LF-00",
  "pattern_id": "CF-000",
  "signal_class": "synthetic_example_only",
  "possible_inference": "bounded description",
  "epistemic_status": "counterfactual_hypothesis",
  "source_ids": ["SRC-0000"],
  "alternative_explanations": ["..."],
  "what_it_cannot_prove": ["..."],
  "countercontrols": ["..."],
  "requires_human_decision": true
}
```

Do not invent a confidence score. If evidence is insufficient, mark the
proposition `unknown` and state the exact evidence needed.
