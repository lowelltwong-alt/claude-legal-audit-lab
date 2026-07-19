# Argument Mesh Standard

## Goal

Support exploration from a universal theory or white-paper section down through
multiple theses, arguments, objections, falsifiers, claims, exact evidence
locators, source revisions, PR captures, Git objects, and hashed bytes.

```text
paper / theory
-> thesis
-> argument, objection, rebuttal, falsifier, or proof gap
-> bounded claim
-> exact evidence locator
-> source or repository revision
-> immutable or captured bytes
```

Every downward link must have a reverse dependency so source drift identifies
all affected arguments, theories, and paper sections.

## Authority boundary

The argument mesh is a semantic projection, never a replacement for source,
claim, capture, or lineage registries. Graph centrality, agent agreement, and a
persuasive narrative do not increase evidence strength.

Deterministic code owns identities, hashes, reference resolution, cycles,
capture completeness, source closure, contradiction preservation, coverage,
promotion eligibility, and export hashes. AI systems may propose connections,
counterarguments, falsifiers, missing evidence, and paper structures; all begin
as candidate records.

## Required argument objects

- theory;
- thesis;
- supporting argument;
- objection and rebuttal;
- bounded falsifier, weakening evidence, and confirmation condition;
- proof gap, including missing source-to-sink steps;
- paper section plan;
- review and promotion decision.

Each load-bearing object needs a stable ID, epistemic status, review status,
scope, `does_not_prove` boundary, qualified references, counterevidence, and
visibility/export class.

A normative thesis is not made empirically falsifiable merely by attaching a
test to it. `FALSIFIED_BY` is reserved for a bounded empirical proposition that
the stated result would actually refute. Use `WEAKENED_BY` when evidence removes
one pathway, product, configuration, benchmark, or period but leaves the larger
thesis or other mechanisms intact.

## Promotion gates

Promotion fails when a reference is stale, a source revision is missing, a
claim is locator-only, a required PR capture is partial, an objection is erased,
a falsifier is untested, a proposer reviews its own work, or a public section
depends on an unpublished origin or workflow record.

An unresolved hypothesis may appear publicly only if it is expressly labeled,
its proof gaps and falsifiers remain visible, and a human approves the exact
export hash.

## Subagent harness

Use bounded read-only roles for evidence linking, argument architecture,
adversarial falsification, and independent lineage checking. The orchestrator
owns the single semantic write and deterministic rebuild. Only the human editor
may authorize public export or final thesis promotion.

## Public export

Build a positive allowlist from approved argument, claim, source, and excerpt
IDs. Never publish by copying an internal workspace and subtracting files. A
public export manifest must record included and excluded dependencies, citation
and privacy reviews, lineage completeness, evidence reproducibility, human
approval, and the final export SHA-256.
