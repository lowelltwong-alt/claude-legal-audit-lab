Use `$codex-security:deep-security-scan` to run a deep security scan of `upstream/claude-for-legal`.

Concrete threat-model guidance:

- Treat Markdown prompts, skill instructions, agent files, YAML/JSON manifests, MCP declarations, GitHub Actions, shell scripts, and Python scripts as executable behavior.
- Sensitive assets include privileged/client documents, firm playbooks, risk appetite, escalation matrices, attorney rationales, deviation logs, accepted/rejected policy proposals, connector credentials, matter workspaces, and evaluation data.
- Trace prompt injection from untrusted legal documents into tool calls, cross-agent handoffs, writes, Slack/email notifications, connector queries, and generated HTML/Excel.
- Trace supply-chain paths through community skills, update logic, mutable sources, external plugins, GitHub Actions, and skill uploads.
- Trace overbroad MCP wildcards, connector permissions, cross-matter/cross-plugin reads, and local configuration persistence.
- Trace all remote endpoints, especially `/v1/skills`, `/v1/agents`, MCP URLs, web fetching, and notification tools.
- Do not treat legitimate inference requests as covert exfiltration; identify authorization, expected destination, and secondary-use evidence.
- Report proprietary-runtime and contract gaps separately from source-code vulnerabilities.

After the security scan, run the non-security strategic audit in `prompts/00-master-orchestrator.md`; security findings alone do not answer the intent or platform-learning question.
