# Master multi-pass audit prompt

Read `AGENTS.md`, `UPSTREAM.lock.json`, and every document in `docs/` that defines scope or terminology.

## Preflight

1. Confirm `upstream/claude-for-legal` exists and its HEAD equals the locked commit.
2. Run `make audit` and inspect all generated artifacts.
3. Create `results/run-manifest.json` with timestamp, commit, tool/model identity if known, and the commands actually run.
4. Never execute upstream hooks, installers, connector calls, deployment scripts, or untrusted code. Static review is read-only.

## Round 1: independent discovery

Spawn six read-only agents. Give every agent the exact prompt in `prompts/10-independent-discovery-worker.md`, the same entire repository scope, and separate output paths. Do not reveal one worker's candidates to another.

Wait for all six. Verify each has line-coverage receipts and schema-valid output.

## Round 2: merge and new-pattern generation

Run `prompts/20-merge-and-pattern-mine.md`. Produce:

- `results/canonical-candidates.json`;
- `results/claim-ledger.csv`;
- `patterns/generated-patterns.json`;
- `results/novelty-round-1.json`;
- a list of files/lines not yet read in full.

## Round 3: specialized review

Spawn the project agents `dataflow_tracer`, `prompt_semantics`, `permission_surface`, `runtime_gap`, `skeptical_reviewer`, and `evidence_mapper` against the canonical candidate inventory and remaining coverage gaps. Each must return new evidence, disconfirming evidence, or an explicit no-new-evidence result.

## Round 4: counterfactual mechanism

Execute `prompts/30-counterfactual-trojan-horse.md` without assuming the mechanism is real. Map required components to Confirmed / Inferred / Unknown / Contradicted evidence.

## Round 5: falsification

Execute `prompts/40-skeptical-rebuttal.md`. Any finding that cannot survive the strongest alternative explanation must be narrowed or rejected.

## Round 6: runtime and contract evidence plan

Execute `prompts/50-runtime-validation.md`. Produce tests that use synthetic data and authorized environments only.

## Later rounds

Use generated patterns to search again. A completed round is saturated only when it adds no new material pattern class, no new source-to-sink path, and no new proof gap. Stop after one zero-novelty completed round or ten total rounds, whichever comes first.

## Final output

Write `results/REPORT.md` and `results/REPORT.json` conforming to `schemas/final-report.schema.json`. The first paragraph must state that the open repository cannot reveal Anthropic's full runtime or internal intent.
