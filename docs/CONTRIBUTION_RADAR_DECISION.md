# Contribution and Radar Decision Record

## Risk classification

- Contribution/radar schemas and manual candidate workflow: **medium risk**.
  They are reversible, introduce no deployed watcher, and cannot promote claims.
- Opening public contribution intake: **high risk** because contributor rights,
  privacy, evidentiary integrity, and release governance become externally
  consequential.
- Changing the repository license: **high risk** and explicitly blocked pending
  owner choice and appropriate legal review.

## Chosen bounded implementation

Build documentation, schemas, templates, a public watchlist, and deterministic
validation in preview mode. Do not activate monitoring, alter `LICENSE`, accept
outside contributions, publish raw captures, or move private material.

## Alternatives considered

1. Open contributions immediately under the apparent Apache notice. Rejected:
   the license text and holder are incomplete and review controls are absent.
2. Apply one permissive license to every file. Deferred: simple but may not
   protect scholarly identity or the desired commercial boundary.
3. Apply restrictive terms immediately. Rejected without a human decision:
   it changes the project's open/public character and can conflict with upstream
   or hosting expectations.
4. Build an automatic crawler now. Rejected: source rights, credential,
   execution, freshness, and publication boundaries need explicit approval.

## Premortem

| Failure | Early warning | Preventive gate |
|---|---|---|
| Confidential industry material is submitted | unverifiable or anonymized “client example” | public-source-only intake and default rejection |
| Marketing language becomes an accusation | intent/retention claim lacks exact evidence | typed epistemic state and `does_not_prove` |
| Split licensing becomes ambiguous | one file mixes code and research prose | path-level license map and SPDX validation before intake |
| Monitoring becomes an accusation engine | bot changes a claim or thesis | candidate-only permission model |
| Private work leaks | `.private`, local path, prompt, or raw capture enters diff/artifact | physically separate private repo plus allowlist exporter before release |
| Stale watcher looks quiet | access error recorded as unchanged | mandatory failure receipts and freshness state |
| Contributor cannot grant rights | employer or AI-generated origin is unclear | DCO, provenance disclosure, and rejection until resolved |

## Rollback and kill criteria

Pause the affected lane immediately for a credible privacy, privilege,
copyright, takedown, security, source-rights, or contributor-authority concern;
any private-data boundary crossing; automation with secrets or write authority;
automatic public claim promotion; repeated monitoring failures; or a failed
lineage/citation gate.

Rollback is: disable the surface, freeze publication, preserve a minimal
non-content incident receipt, rotate affected credentials, revert to the last
human-approved public release, assess current-branch and history remediation,
and resume only after the named human gates pass.

## Acceptance evidence

- deterministic priority recomputation;
- JSON and cross-reference validation;
- one public AI front door and fully routed TOC entries;
- clean public/private path scan;
- byte-identical rebuilds;
- independent evidence and privacy/license review;
- explicit unresolved license and automation gates.
