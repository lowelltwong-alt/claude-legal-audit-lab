# AI Navigation and Lineage Standard

## Purpose

Make the repository easy for people and AI systems to interrogate without
flattening primary evidence, claims, analysis, and generated outputs into one
undifferentiated document set.

## Navigation contract

1. `AI_FRONT_DOOR.md` is the only start point.
2. The machine manifest provides versions, required read order, and entrypoints.
3. Every table-of-contents row states path, role, tags, use-when trigger, and
   authority class.
4. Task routing stays shallow. It points to the smallest authoritative surface
   instead of copying its content.
5. Graphs, chunks, matches, and reports are always labeled candidate evidence.

## Genealogy contract

Every public derived artifact in the configured scope must have exactly one
authored record in `registry/lineage-policy.json`. The record declares:

- artifact class and authority class;
- direct parent artifacts;
- direct source identifiers;
- claim identifiers used by the artifact;
- whether the lineage is reviewed or retained only as an incomplete legacy
  candidate.

`scripts/build_lineage.py` hashes every artifact, resolves each claim to its
registered evidence sources, follows parent artifacts recursively, rejects
cycles and unknown identifiers, and writes the transitive closure to
`registry/derivation-registry.json` in stable order.

## Deterministic gates

The validator fails when:

- a required public artifact lacks a lineage declaration;
- a declared path, parent, source, claim, or navigation route is missing;
- an artifact SHA-256 no longer matches its derivation record;
- a derivation cycle exists;
- a factual synthesis has no source closure;
- reviewed analysis depends on a source explicitly marked as missing;
- a generated surface is promoted to primary-source authority;
- the generated registry differs byte-for-byte from a clean rebuild.

Method and interrogatory documents may have no evidentiary source closure, but
their artifact class must say so. Incomplete inherited material may remain only
as `candidate_legacy`; it cannot be cited as reviewed analysis until its missing
source metadata and capture are repaired.

## Source revision strength

Lineage identity and content reproducibility are separate dimensions:

- A Git commit is an immutable source revision.
- A captured file is reproducible when its bytes have a SHA-256.
- A dynamic web page with an access date and locator is traceable but not fully
  reproducible; it must be refreshed or archived before a high-stakes quote.
- A named citation without a URL or capture is incomplete candidate evidence.

The registry preserves these weaknesses instead of inventing certainty.

## Adding a synthesis

1. Add or update source records first.
2. Add bounded claim records with exact locators and `does_not_prove` limits.
3. Write the artifact.
4. Declare its parents, sources, and claims in the lineage policy.
5. Run `python scripts/build_lineage.py`.
6. Run `python scripts/validate_navigation.py` and the test suite.
7. Review the transitive source closure before publication.

## White-paper export rule

A future white-paper paragraph should receive its own stable artifact or
section identifier and a derivation record. Multi-source synthesis must retain
every contributing claim and source, including counterevidence. Citations in the
paper are presentation; the derivation registry is the machine genealogy.

