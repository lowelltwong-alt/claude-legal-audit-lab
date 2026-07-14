# Is an “ontology of partner thought” a real thing?

## Calibrated answer

Yes, as an **operational representation of institutional judgment**. No, as a literal copy of a partner's mind.

A legal judgment ontology can encode:

```text
matter type / issue
+ relevant facts
+ jurisdiction / client / counterparty context
-> preferred legal or negotiating position
-> acceptable fallback
-> prohibited outcome
-> severity and materiality
-> escalation threshold and approver
-> exception rationale
-> final disposition
-> later assessment of whether the rule should change
```

This becomes substantially more valuable when joined with outcome and feedback data:

- which redlines were accepted;
- which warnings attorneys dismissed;
- which exceptions partners approved;
- why a deviation was commercially justified;
- which AI-generated suggestion was edited, rejected, or adopted;
- whether repeated exceptions caused the playbook to change.

## Why the Anthropic plugin design is relevant

The visible design contains the components of such a loop:

1. onboarding asks for playbooks and signed examples;
2. the practice profile stores positions, fallbacks, “never accept” rules, risk posture, and escalation;
3. deal debrief records deviations and the attorney's rationale;
4. playbook monitor identifies repeated deviations;
5. the attorney accepts, rejects, edits, or defers proposed rule changes.

That is not merely retrieval over documents. It is a customer-level policy-learning loop.

## What remains unknown

The code says these artifacts are written to customer-local configuration paths. It does not reveal whether the provider also retains relevant prompts/outputs, derives aggregate patterns, or uses them for generalized model/product improvement. Because Claude performs the reasoning, the model provider may receive relevant context at inference time depending on deployment. Receipt is not the same as retention or training.

## Strategic implication

A firm should treat this ontology, and especially the feedback/evaluation layer, as crown-jewel operating intelligence. The safest architecture keeps the ontology, orchestration, evaluation set, corrections, and approval history firm-controlled, while sending only minimized task fragments to replaceable models.
