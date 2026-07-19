# Pinned Codebase Research Report

## Scope

This report covers only the public `anthropics/claude-for-legal` source pinned at
commit `5ceb305b30b4c82653c9b6642499c12e946ec319`. Six independent passes reviewed
all 315 text files and 49,365 lines with exact SHA-256 and line-count
reconciliation. It does not assess Anthropic's closed runtime, private history,
executed customer contracts, or any other user repository.

## Calibrated conclusion

The source confirms a product design that can encode and repeatedly apply
firm-specific professional interaction graphs: playbooks, positions, fallbacks,
escalation rules, risk posture, matter context, choices, rationales, outcomes,
and proposed policy updates. It also confirms declared remote connector and
hosted-agent trust boundaries.

The source does **not** establish that Anthropic retains, trains on, pools, or
generalizes those firm-specific signals across customers. No reviewed static
file completes that provider-side source-to-sink chain. Claims of covert
ontology capture therefore remain unsupported by the registered code evidence.

A targeted second round adjudicated all 1,212 generated-pattern matches using
full-line hashes. It classified 987 as canonical rediscoveries, 180 as false
positives, and 45 as counterevidence, with zero new material static pattern
classes or source-to-sink candidates. Static saturation is therefore bounded to
this pinned revision and these reviewed pattern families; runtime, contract,
inaccessible-history, and future-revision questions remain open.

## Material evidence clusters

1. Firm-specific operating policy is explicit in
   `commercial-legal/CLAUDE.md:66-72`,
   `privacy-legal/skills/cold-start-interview/SKILL.md:93-101`, and
   `ai-governance-legal/CLAUDE.md:75-96`.
2. Decision-to-policy feedback loops appear in
   `commercial-legal/agents/deal-debrief.md:15-20`,
   `commercial-legal/agents/playbook-monitor.md:18-24`, and
   `regulatory-legal/skills/cold-start-interview/SKILL.md:197-214`.
3. Durable matter and investigation memory appears in
   `product-legal/skills/matter-workspace/SKILL.md:28-38`,
   `employment-legal/skills/internal-investigation/SKILL.md:113-155`, and
   `litigation-legal/skills/matter-intake/SKILL.md:11-16`.
4. Remote and hosted boundaries appear in `commercial-legal/.mcp.json:2-44`,
   `scripts/deploy-managed-agent.sh:4-12`, and
   `managed-agent-cookbooks/diligence-grid/subagents/doc-reader.yaml:17-35`.
5. A governed third-party skill boundary appears in
   `legal-builder-hub/skills/auto-updater/SKILL.md:24-67` and
   `legal-builder-hub/skills/skill-installer/SKILL.md:17-23`.

## Counterevidence

The repository repeatedly uses default-off cross-matter reads, explicit input,
read-only or schema-limited untrusted-document agents, separated writer or
network authority, human approval, provenance, allowlists, and fresh install
approval. These controls support a benign customer-adaptation architecture.
They do not prove deployed enforcement, but they materially constrain any fair
interpretation of the static design.

## History coverage

The public PR index contains 76 records. Current normalized evidence includes
14 hash-verified merged PR linkages and 29 bounded open/unmerged snapshots; 33
records remain unknown or incomplete. Unknown never means “no change.” Deleted,
private, inaccessible, and closed-runtime history is outside the demonstrated
record.

## Thesis implication

The evidence supports a governance recommendation, not an accusation: firms
should independently control professional interaction graphs, derivatives,
telemetry, evaluation, portability, and exit because cross-firm reuse could
create a sector-level externality **if** material signals leave firm custody and
reuse is permitted. Current registered evidence does not establish that a named
provider is doing so.

## Proof gaps

- Actual inference request and telemetry payloads.
- Feature-specific retention, deletion, support-access, evaluation, and
  training terms.
- Tenant configuration, connector grants, and observed traffic.
- Runtime enforcement of isolation and approval controls.
- Evidence of cross-customer normalization or generalized reuse.
- The remaining 33 unknown or incomplete public PR records.

The required next step is an authorized synthetic runtime and contract audit,
not stronger inference from static code.
