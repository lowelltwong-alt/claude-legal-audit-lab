# Research Contribution Model

## Purpose

The public contribution surface should make it easy to add verifiable evidence
and hard to launder analogy into fact. Contributions move through a typed mesh:

```text
public source revision
-> exact evidence locator
-> bounded observed claim
-> explicit inference or hypothesis
-> industry comparison
-> thesis or white-paper argument
```

Every arrow is reviewable. No downstream repetition upgrades the authority of
an upstream statement.

## Roles

- **Contributor:** submits one bounded evidence packet or deterministic change.
- **Evidence reviewer:** reproduces the source and locator without relying on
  the contributor's summary.
- **Methodology reviewer:** checks taxonomy and scoring semantics.
- **Technical reviewer:** checks schemas, scripts, fixtures, and generated data.
- **Release editor:** decides whether reviewed material enters a public thesis
  or white paper.
- **Repository owner:** retains license, privacy, automation, naming, and release
  authority.

The same person may fill several roles, but a contributor may not be the only
reviewer of a claim they authored.

## Epistemic states

| State | Meaning |
|---|---|
| `Observed` | Exact primary evidence establishes the bounded proposition. |
| `Inferred` | A stated reasoning chain connects observed propositions; alternatives remain visible. |
| `Hypothesis` | A falsifiable proposition names confirmation evidence and falsifiers. |
| `Unknown` | Available evidence cannot resolve the proposition. |

Provider integration, processing, persistence, telemetry, aggregation,
training, product improvement, and strategic intent are separate propositions.
Evidence of one does not silently establish another.

## Review gates

1. **Source gate:** public authority, exact revision, locator, lawful public
   pointer, and rights boundary are recorded.
2. **Claim gate:** proposition and `does_not_prove` are bounded.
3. **Counterevidence gate:** benign explanations and evidence weighing against
   the proposition are preserved.
4. **Lineage gate:** every synthesis reaches its primary sources.
5. **Freshness gate:** dynamic sources are rechecked before publication.
6. **Privacy gate:** no private, client, personal, privileged, or raw third-party
   payload crosses into the public surface.
7. **Human gate:** claim promotion, thesis changes, license changes, and releases
   are never automatic.

## Intake status

The design is ready for local testing, but public intake remains closed until
the activation criteria in `CONTRIBUTING.md` and
`docs/CONTRIBUTION_RADAR_DECISION.md` are satisfied.
