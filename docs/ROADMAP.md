# Project Roadmap

## Outcome

Build an evidence-reproducible, privacy-safe research system for the public
evolution and operation of `anthropics/claude-for-legal`. It must connect every
material thesis to exact primary evidence, preserve counterevidence and proof
gaps, support source-aware chunking and a typed knowledge graph, enable only
authorized synthetic runtime research, and eventually produce a scrubbed public
repository and white paper.

The machine-authoritative project packet is
`registry/project-roadmap.json`. Run `python scripts/validate_roadmap.py` to
validate states, dependencies, blockers, execution leases, acceptance evidence,
Today/WIP limits, and the current unlock frontier.

## Non-goals

- alleging retention, training, secondary use, intent, or competitive harm
  without evidence;
- processing client, privileged, confidential, sealed, or restricted material;
- probing tenants, vendors, lawyers, clients, or live systems without written
  authority;
- activating monitoring, contribution intake, or publication from this plan;
- changing the repository name, license, branch, Git history, or hosting state
  without a separate human decision.

## Dependency-ordered phases

| Phase | Workstreams | Exit evidence |
|---|---|---|
| 0. Control and truth baseline | `CLAO-WS-00`, `CLAO-WS-01` | Machine roadmap, pinned upstream receipt, inventory, matches, worklists, hashes, validators, and independent check |
| 1. Temporal and source reproducibility | `CLAO-WS-02`, `CLAO-WS-03`, `CLAO-WS-06` | PR/revision coverage receipt; exact URLs, revisions, hashes, and locators; unresolved arrows remain `Unknown` |
| 2. Source-aware chunking | `CLAO-WS-04` | Stable lossless chunk identities, line/diff/heading boundaries, citation round-trip, and adversarial fixtures |
| 3. Evidence knowledge graph | `CLAO-WS-05` | Typed inverse edges from source/revision/PR/file/line/chunk through claim/argument/paper; deterministic rebuild and no authority inversion |
| 4. Runtime and thesis falsification | `CLAO-WS-07`, `CLAO-WS-08` | Authorized synthetic experiment receipts and a Kirkland/Ajax comparison that retains objections, falsifiers, and missing evidence |
| 5. Radar and cross-industry research | `CLAO-WS-09` | Manual candidate-only pilot with source rights, failure receipts, freshness, and no claim promotion |
| 6. White paper and explorer | `CLAO-WS-10` | Human-readable thesis plus executive, academic, and adversarial mini papers with stable anchors, JSON sidecars, structure comparison, exact source drill-down, export hashes, and independent evidence/privacy/legal review |
| 7. Public release | `CLAO-WS-11` | Name, holder, license map, security contact, allowlist, privacy/history scans, reproducible frozen candidate, and named human approval |

## Current unlock frontier

The chunk-control plane (`CLAO-WS-04`) and typed evidence graph
(`CLAO-WS-05`) are delivered for their activated public scope. Temporal PR
capture, source repair, and Anthropic primary-evidence work remain active or
ready. The white-paper/explorer lane has a deterministic blocked preview and
three compare-only mini-paper variants, but
17 of 18 claims and all seven thesis nodes still fail publication gates.
Proposed dependencies do not create release authority.
`Today` is capped at three workstreams; overflow stays visible rather than being
silently discarded.

## What was executed in this tranche

1. Verified the upstream checkout at the pinned commit.
2. Inventoried 315 upstream files and 49,365 text lines.
3. Indexed 162 URLs.
4. Produced and validated 4,481 heuristic pattern matches.
5. Built six balanced read-only worklists and a SHA-256 receipt under the
   ignored `results/` workspace.
6. Fixed Windows UTF-8 handling in the JSONL validator and added a regression
   test.
7. Added this roadmap control plane and a separate fail-closed release-readiness
   gate. Release remains intentionally blocked.
8. Integrated both gates into the AI front door, design authority, source-of-truth
   precedence, lineage policy, navigation validator, and test harness.
9. Promoted chunk-registry v2 with 438 full-SHA chunks, 246 inverse adjacency
   edges, exact Git-blob reconstruction, a v1 migration map, adversarial
   fixtures, and byte-identical Python/Rust output.
10. Hardened five-PR cohort capture with a 15-request reserve, resumable
    checkpoints, ETags/rate receipts, and structural multipage verification.
    Current coverage is 14 verified merged PRs, 29 bounded open/unmerged
    snapshots, and 33 unknown or incomplete records.
11. Repaired the claim model into separate lifecycle, epistemic, review, and
    publication states; split static design from unknown runtime/tenant
    behavior; quarantined `CLM-0005`; and retired `CLM-0009`.
12. Built a 1,046-node, 4,842-edge typed graph, a seven-node Ajax Line thesis map,
    and a seven-paragraph hash-genealogized paper/explorer preview. Every
    generated surface remains candidate and release-blocked.
13. Completed six independent semantic passes over all 315 files and 49,365
    lines, then adjudicated all 1,212 generated-pattern matches in a targeted
    second round with per-record ledgers and full-line hashes. Independent
    recomputation found 987 rediscoveries, 180 false positives, 45
    counterevidence matches, and zero new material static classes.

These receipts now include bounded static semantic review for all 315 text
files and an independent reconciliation of every path, SHA-256, and line count.
Scoped static saturation is established only for the pinned revision and
reviewed pattern families. These receipts still do not establish runtime
behavior, external data handling, or that
any candidate claim is publication-ready.

## Human decisions that remain gates

The owner must separately decide the public name and Trojan War alias, rights
holder/entity, software and research licenses, metadata treatment, trademark
policy, security contact, release approver, private-workspace separation, and
whether monitoring or live runtime work is ever authorized. See
`registry/release-readiness.json` and `docs/LICENSING_OPTIONS.md`.

## Quiet option and resume condition

The safe quiet option is to preserve the validated local candidate, perform no
Git, monitoring, runtime, contribution, or publication mutation, and resume
when an owner decision or new primary source unlocks a lane. Bounded public PR
cohorts may continue under the existing capture contract. Review the plan after
a five-PR or source-repair tranche, or
immediately on any privacy, provenance, source-rights, or reproducibility
failure.
