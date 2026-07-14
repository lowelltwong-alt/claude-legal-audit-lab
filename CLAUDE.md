# Audit instructions for Claude and other coding agents

Read `AGENTS.md` first and follow it as the controlling protocol. This repository audits another prompt-heavy agent repository, so Markdown, YAML, JSON, hooks, connectors, and deployment scripts are all in scope.

Do not assume the hostile hypothesis. Separate workflow capture, inference-time access, provider retention, training, product analytics, and strategic intent. Maintain a line-level coverage ledger and a Confirmed / Inferred / Assumed / Unknown claim ledger.

The upstream checkout belongs at `upstream/claude-for-legal` and must match the commit in `UPSTREAM.lock.json`.
