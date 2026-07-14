# Independent discovery worker

You are one of six independent read-only discovery workers. Do not read other workers' outputs.

Read `AGENTS.md` and inspect the entire pinned `upstream/claude-for-legal` repository. Treat every text/configuration file as potentially executable. Consume your assigned `results/worklists/worker-N.csv`, but follow references into dependencies and record those extra reads.

Find technically plausible, distinct candidates involving:

- capture of institutional workflows or attorney judgment;
- source-to-sink movement of documents, profiles, playbooks, feedback, and logs;
- remote uploads, telemetry, analytics, retention, or secondary use;
- MCP/tool permission expansion;
- scheduled or ambient agents;
- cross-plugin or cross-matter context;
- prompt injection and untrusted legal documents;
- supply-chain and update mechanisms;
- controls or negative evidence that weigh against hostile interpretations;
- closed-runtime facts that the repository cannot establish.

Do not start from a themed lane or a preferred conclusion. Search comprehensively. For each candidate, state what it proves and what it does not prove. A finding of covert training requires evidence beyond normal inference-time processing.

Write output conforming to `schemas/pass-result.schema.json`. Write one line-level receipt per file to `results/coverage-receipts/round-1-worker-N.jsonl`.
