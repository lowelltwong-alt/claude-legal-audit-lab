# Feature Evidence Matrix

This is a candidate evidence map, not a conclusion about any customer or
provider. It separates what an Anthropic document states, what the pinned
`anthropics/claude-for-legal` repository statically declares, and what remains
unknown without authorized runtime, contractual, or audit evidence.

Pinned repository revision: `5ceb305b30b4c82653c9b6642499c12e946ec319`.

| Feature / question | Documented policy or product statement | Pinned static repository evidence | Unknown / not established |
|---|---|---|---|
| API and stateful-feature retention | `SRC-0009` is a locally hashed capture of Anthropic's feature-specific retention documentation. It is the source for stated eligibility and retention-policy analysis. | The repository contains `.mcp.json` declarations and workflow instructions, but no retention logs, policy enforcement trace, or provider storage record. | The effective retention, deletion, backups, access, analytics, training use, and legal-hold treatment for a particular legal workflow or account. |
| Commercial terms and data-processing commitments | `SRC-0005` and `SRC-0006` are locally hashed captures of Anthropic's Commercial Terms and DPA. They state terms about Customer Content, stated training restrictions, confidentiality, processing scope, stated security controls, audit/reporting, and deletion/return conditions within their respective scopes. | No local repository artifact proves a customer accepted either document or shows an executed order form, negotiated exception, or applied tenant policy. | Whether a particular firm is covered by either text; its exact contract hierarchy, feature eligibility, actual access, deletion, audit, enforcement, or data flow. |
| Remote MCP connector use | `SRC-0052` is a locally hashed capture of Anthropic's MCP connector documentation, including documented remote-server configuration, OAuth, multi-server use, and retention statements. | `commercial-legal/.mcp.json` lines 3-20 declares HTTP MCP endpoints and description-level access/permission statements. `CONNECTORS.md` lines 3-18 describes desired legal MCP connector qualities and review. | Installation, authentication, live connection, tool invocation, content transmitted, third-party-server handling, caching, or actual permission enforcement. |
| Managed-agent workflow | No source in this matrix establishes an executed managed-agent deployment. | `managed-agent-cookbooks/reg-monitor/agent.yaml` lines 19-38 scopes the orchestrator to local read/grep/glob tools, declares an MCP server and callable leaves, and labels the digest writer as the only write leaf. | Deployment, runtime tool scope, egress, actual agent execution, output delivery, or provider-side retention. |
| Legal review / approval | No policy statement proves a lawyer's review of any particular result. | `managed-agent-cookbooks/reg-monitor/agent.yaml` lines 13-17 instructs that a lawyer reviews each digest item before a screening call. `commercial-legal/CLAUDE.md` lines 259-270 and 313-341 describe reviewer notes, `[review]` flags, verification, and escalation instructions. | Whether a lawyer reviewed any item, whether a safeguard was enforced, or whether an instruction changed a legal outcome. |
| Connector and writer safeguards | No source in this matrix establishes that any safeguard executed in production. | `CONNECTORS.md` lines 7-11 and 15-18 calls for a safety review and explicit data handling before a connector is approved. `managed-agent-cookbooks/reg-monitor/subagents/digest-writer.yaml` lines 5-11 and 73-81 statically separates the designated write leaf from other workflow roles. `ai-governance-legal/CLAUDE.md` lines 8-18 and `skills/policy-monitor/SKILL.md` lines 97-102 describe a local customization and acknowledgment workflow. | Enforcement, bypass resistance, whether a particular configuration was adopted, and whether any content was transmitted or retained. |
| Practice profile and matter workspace | `SRC-0050` and `SRC-0051` are locally hashed product-announcement captures that discuss customization to playbooks, precedent, and house style. They do not establish where a customer stores those artifacts. | `commercial-legal/CLAUDE.md` lines 4-18 points user-specific configuration to a local `~/.claude/plugins/config/...` location and says the template must not receive user data; line 478 directs active-matter output to a local matter folder. | Actual local data, contents, access controls, transmission, retention, customer use, or whether any artifact reached Anthropic or another service. |

## Interpretation rule

Do not combine a product statement, static configuration declaration, and a
general policy into a finding of actual collection, training, secondary use,
ontology capture, or intent. Each such proposition requires feature- and
tenant-specific evidence with a reproducible source-to-sink path.

## Source custody

`SRC-0005`, `SRC-0006`, `SRC-0009`, `SRC-0050`, `SRC-0051`, and `SRC-0052` have content hashes in
`registry/source-registry.json`. Their raw public response bytes are retained
only under the ignored local raw-research workspace. That custody arrangement
binds the retrieved response, not any inference drawn from it.
