# How the Trojan-horse hypothesis would work — and what would prove it

“Trojan horse” is a claim about concealed purpose. The more neutral term is **platform-learning hypothesis** until concealment and secondary use are evidenced.

| Required component | What the public code shows | Current status |
|---|---|---|
| Useful entry product | Broad legal workflow automation | Confirmed |
| Workflow onboarding | Playbooks, profiles, signed examples, escalation rules | Confirmed |
| Ongoing judgment capture | Deviations, rationales, accepted/rejected playbook proposals | Confirmed |
| Remote model access to relevant context | Claude must process selected context in common deployments | Inferred from architecture; runtime payload needs capture |
| Provider retention/derivation | No conclusive implementation in public repo | Unknown |
| Cross-customer normalization | No conclusive implementation in public repo | Unknown |
| Generalized training/evaluation use | No conclusive implementation in public repo | Unknown |
| Adjacent legal-service productization | Strategic possibility; not proven by this repo | Unknown |
| Concealment or bad-faith intent | Not established | Unknown |

## Red flags that would materially change the assessment

- hidden upload of customer practice profiles, deviation logs, or corrections;
- telemetry containing clause positions, rationales, or decision outcomes;
- server-side synchronization not disclosed in product documentation;
- product-improvement rights covering customer-specific workflow artifacts;
- internal datasets or evaluation suites derived from customer workflows;
- cross-tenant retrieval or shared skill generation;
- roadmap documents explicitly linking customer onboarding to replacement of legal providers;
- inability to export/delete customer-specific skills and evaluation data.

## Evidence weighing against the hostile interpretation

- local configuration paths;
- explicit restrictions on ambient context and unrelated history in some onboarding prompts;
- human confirmation before playbook changes;
- empty first-party hooks in reviewed plugins;
- tool-scope linting, read-only subagents, allowlists, schema validation, and prompt-injection warnings;
- the option to deploy through a customer's own workflow engine.

These controls are relevant but not dispositive because some are prompt-level rather than independently enforced, and the hosted runtime remains outside the repository.
