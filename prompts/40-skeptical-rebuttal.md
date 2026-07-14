# Skeptical falsification pass

Try to disprove the current leading thesis.

Search specifically for:

- local-only storage and user-controlled configuration;
- explicit limits on ambient context, prior conversations, and cross-matter reads;
- human approval gates before writes or external actions;
- read-only subagents, schema validation, allowlists, and tool scoping;
- warnings that customer documents are untrusted data;
- controls against prompt injection and supply-chain updates;
- code that tells users to review training, retention, and data-use terms;
- architecture allowing the customer to use its own workflow engine;
- absence of telemetry, analytics, hidden hooks, arbitrary outbound endpoints, or generalized upload paths.

For each hostile candidate, give the strongest alternative explanation and say whether the candidate survives. Also identify controls that exist only as prompt instructions rather than enforced code.
