# Lineage Contract Decision

- Risk tier: **high**.
- Decision date: 2026-07-14.
- Scope: public AI navigation and source genealogy; local research genealogy
  follows the same fail-closed contract without becoming a public authority.

## Why this is high risk

The contract will shape future research, agent routing, knowledge-graph edges,
and a potential white paper. A false parent edge or silently stale artifact can
propagate unsupported claims across many downstream products.

## Options considered

1. Markdown citations only. Simple, but cannot deterministically find missing
   parents, stale files, cycles, or transitive multi-source ancestry.
2. One machine registry edited by hand. Traceable, but hashes and transitive
   closure would drift from the authored documents.
3. **Chosen:** an authored policy plus a deterministic generated registry. Human
   judgment declares semantic parents; code owns hashes, closure, and gates.

## Premortem

- A source page changes after capture. Mitigation: retain access date, revision
  type, locator, and explicit reproducibility limitation.
- A synthesis cites a claim but omits its counterevidence. Mitigation: the claim
  registry keeps `does_not_prove`, status, confidence, and hypothesis effects.
- A generated graph is mistaken for truth. Mitigation: authority registries and
  validation prohibit generated outputs from primary-source classification.
- A legacy document contains incomplete citations. Mitigation: preserve it only
  as `candidate_legacy`; block promotion until repaired.
- The policy becomes burdensome and people bypass it. Mitigation: one compact
  record per artifact and a builder that computes hashes and closure.

## Rollback and kill criteria

The change is file-local and reversible. Roll back the contract if two
independent clean builds produce different bytes, if the validator permits a
reviewed synthesis with no source closure, or if the public navigation surface
reveals unpublished working material. Do not weaken those gates to make a build
green; repair the source or declaration.

