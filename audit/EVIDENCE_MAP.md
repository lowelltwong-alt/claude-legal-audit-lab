# Pinned evidence map

Review these files first after bootstrap. All URLs are pinned to commit `5ceb305b30b4c82653c9b6642499c12e946ec319`.

| Surface | Path | Why it matters |
|---|---|---|
| Repository scope | `README.md` | Describes plugins, cold-start interviews, connectors, agents, and deployment choices |
| Repository architecture | `CLAUDE.md` | States most content is prompts/config, gives layout and local config behavior |
| Marketplace | `.claude-plugin/marketplace.json` | Enumerates first-party legal verticals and external CoCounsel plugin |
| Commercial connector surface | `commercial-legal/.mcp.json` | Ironclad, DocuSign, iManage, Slack, Drive, and other endpoints |
| Practice-profile template | `commercial-legal/CLAUDE.md` | Positions, fallbacks, never-accept rules, escalation, house style |
| Workflow onboarding | `commercial-legal/skills/cold-start-interview/SKILL.md` | Seed agreements, actual positions, risk appetite, company profile |
| Judgment feedback | `commercial-legal/agents/deal-debrief.md` | Deviations, rationales, one-offs, outcomes |
| Policy adaptation | `commercial-legal/agents/playbook-monitor.md` | Pattern detection and proposed playbook updates |
| Hosted deployment | `scripts/deploy-managed-agent.sh` | Uploads skills and creates hosted agents |
| Cross-agent flow | `scripts/orchestrate.py` | Handoffs, audit log, Anthropic SDK, injection controls |
| Tool-scope control | `scripts/lint-tool-scope.py` | Prevents parent orchestrator write/MCP/Slack grants |
| Managed-agent example | `managed-agent-cookbooks/renewal-watcher/agent.yaml` | Model, tools, MCP servers, leaf delegation |
| Connector reader | `managed-agent-cookbooks/renewal-watcher/subagents/repo-reader.yaml` | Reads CLM/DMS fields under schema constraints |
| Community supply chain | `legal-builder-hub/skills/skill-installer/SKILL.md` | Installer trust model and prompt-injection risks |
| Update supply chain | `legal-builder-hub/skills/auto-updater/SKILL.md` | Update diff, SHA pinning, approval, rescan |
| QA threat model | `legal-builder-hub/skills/skills-qa/SKILL.md` | Exfiltration, credential, hidden-content, and prompt-injection patterns |
| Vendor AI terms | `ai-governance-legal/skills/vendor-ai-review/SKILL.md` | Explicitly identifies training, retention, stacked-vendor, and telemetry risks |

GitHub repository: `https://github.com/anthropics/claude-for-legal`
