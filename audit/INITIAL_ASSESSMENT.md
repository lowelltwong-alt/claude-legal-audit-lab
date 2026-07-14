# Initial static assessment

## Scope reviewed

A GitHub API/static review of the official public repository at commit `5ceb305b30b4c82653c9b6642499c12e946ec319`. A full local clone was not available in the originating environment, so this assessment is an orientation, not a completed exhaustive scan. The packaged bootstrap and worklist tooling is intended to make the next review reproducible.

## Material observations

### 1. The repository openly captures firm-specific operating intelligence

The commercial cold-start workflow asks for recent signed agreements and an escalation matrix, extracts actual playbook positions, notes differences between stated and signed positions, and writes a durable practice profile. It explicitly says its purpose is to learn how *that team* works rather than generic commercial-contract practice.

**Assessment:** Confirmed workflow capture; not evidence of covert provider training.

### 2. The design captures decision rationales and policy drift

The deal-debrief agent records clause deviations, severity, the basis for the deviation, attorney context, and whether a deal should be excluded as a one-off. The playbook monitor groups repeated deviations and proposes precise playbook changes, subject to attorney approval.

**Assessment:** Confirmed customer-level feedback loop approximating institutional judgment.

### 3. Customer-specific configuration is represented as local

Practice profiles and logs are directed to `~/.claude/plugins/config/claude-for-legal/...` and some onboarding instructions explicitly prohibit filling profiles from ambient context, prior sessions, unrelated conversations, or user memory without approval.

**Assessment:** Material negative evidence against a simple hidden-local-file-exfiltration claim. It does not establish what request context or hosted services retain.

### 4. Remote boundaries are explicit but limited in the open source

The deployment script zips and uploads skills to `/v1/skills`, creates agents through `/v1/agents`, and tags managed-agent deployments. MCP manifests declare remote legal and productivity systems. The orchestrator uses the Anthropic SDK for managed-agent sessions and handoffs.

**Assessment:** Confirmed remote execution boundaries. The uploaded skill definitions are not necessarily customer playbooks; deployed runtime payloads require observation.

### 5. No obvious separate covert analytics client was identified in the reviewed open files

Searches for common telemetry/analytics clients and hidden network code did not identify an obvious first-party exfiltration path. Reviewed first-party hooks were empty. The executable network code identified was the documented Anthropic agent deployment/orchestration path and declared connectors.

**Assessment:** Negative evidence within a limited source scope, not proof of absence in closed products.

### 6. The code contains meaningful security controls

The repository includes tool-scope linting, schema validation, target/intent allowlists, read-only subagents, human approval gates, update diffs, pinned commit guidance, prompt-injection warnings, and explicit treatment of legal documents as untrusted data.

**Assessment:** These controls weigh against a simplistic malicious-code narrative. Some controls are prompt instructions rather than hard runtime enforcement and must be tested.

## Preliminary conclusion

The public repository strongly supports the proposition that Claude for Legal is designed to encode and continuously refine a legal organization's workflows and judgment rules. It does not currently support the stronger allegation that Anthropic covertly retains or trains on those artifacts to replace law firms. The visible strategic issue is that a frontier-model platform may become the execution and feedback layer for the firm's operating intelligence, creating exposure and dependency even under a no-foundation-model-training commitment.
