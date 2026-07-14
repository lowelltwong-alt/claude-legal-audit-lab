# Scope boundary

## What this public repository is

The repository is a public implementation layer for legal plugins and managed-agent templates. It contains prompts/instructions, practice-profile templates, connector declarations, scheduled-agent definitions, and deployment/orchestration utilities.

## What it is not

It does not contain the complete source for:

- Claude model inference;
- Claude Desktop/Cowork/Code request assembly;
- hosted Managed Agents;
- Anthropic server logs, abuse monitoring, product analytics, support systems, or feedback processing;
- model training, fine-tuning, evaluation, distillation, or data-selection pipelines;
- the implementation of third-party MCP servers;
- enterprise admin retention and deletion controls;
- commercial contracts or customer-specific deployment configurations.

## Consequence

A repository review can establish that the product is designed to **capture and operationalize firm-specific workflows**. It cannot, by itself, establish that Anthropic secretly trains on those workflows or intends to replace law firms.

A source review should therefore produce two outputs:

1. **Observed behavior and capability.**
2. **Proof gaps and tests required for closed systems.**
