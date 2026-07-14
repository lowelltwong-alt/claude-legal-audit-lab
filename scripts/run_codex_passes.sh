#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p results/codex

if ! command -v codex >/dev/null 2>&1; then
  echo "codex CLI not found; open the repository in Codex and use prompts/00-master-orchestrator.md" >&2
  exit 127
fi

# This sequential wrapper is reproducible, but the interactive master prompt is
# preferred when you want Codex to spawn the configured six read-only subagents.
for prompt in prompts/30-counterfactual-trojan-horse.md prompts/40-skeptical-rebuttal.md prompts/50-runtime-validation.md; do
  name="$(basename "$prompt" .md)"
  codex exec --ephemeral "Read AGENTS.md, then execute the task in $prompt against upstream/claude-for-legal. Write no source changes." \
    -o "results/codex/${name}.md"
done
