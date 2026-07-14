# Threat model: legal workflow sovereignty

## Assets

- privileged and confidential matter content;
- work product and precedents;
- playbooks, fallback positions, and deal-breakers;
- partner and committee risk tolerance;
- escalation routes and delegated authority;
- attorney rationales for exceptions;
- accepted/rejected AI suggestions;
- deviation and outcome history;
- matter taxonomy and ontology extensions;
- model evaluation sets;
- connector tokens and access scopes;
- agent/tool execution traces.

## Trust boundaries

1. Lawyer or administrator to local Claude client.
2. Local files/configuration to model context.
3. Claude client to Anthropic API or another model provider.
4. Claude runtime to MCP connector.
5. Connector to DMS/CLM/email/chat/research platform.
6. Managed-agent orchestration to hosted skills and agents.
7. Community/vendor plugin to the privileged legal environment.
8. Support, feedback, analytics, and abuse-monitoring systems.
9. Model/product development organization.

## Threats

- excessive connector scope;
- prompt injection from adversarial legal documents;
- cross-matter or cross-client context contamination;
- unintended persistence or logging;
- feedback submission changing data-use terms;
- workflow lock-in and non-portability;
- supply-chain compromise of skills or MCP servers;
- provider-side derivation of generalized workflow/evaluation signals;
- product adjacency and vertical envelopment;
- false assurances based on “no training” language that does not cover metadata, support, or product discovery.

## Key distinction

A provider can gain strategic leverage without training a foundation model on raw files. It may gain leverage through customer-specific configurations, hosted orchestration, integration depth, product analytics, aggregate demand signals, and proprietary evaluation/control layers. Those mechanisms must still be evidenced separately.
