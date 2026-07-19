# Mini White-Paper Research and Build Engine

## Purpose and boundary

This portable-core workflow turns the existing evidence graph into several
rhetorical projections without allowing prose, scores, or model output to add
evidence or promote a claim. The evidence system decides what may be said; the
mini-paper plan decides how the same bounded material is arranged for a stated
audience.

All generated papers remain blocked, unpublished candidates. Structural scores
measure inspectable completeness and ordering only. They do not measure truth,
persuasion, legal sufficiency, originality, or publication readiness.

## What already exists elsewhere

No reviewed primary description found in this research combines all of this
project's layers: revision-bound source chunks, paragraph-stable anchors,
typed claim/evidence/objection/falsifier graphs, deterministic genealogy,
multi-version rendering, and fail-closed release gates. The engine is novel in
its integration, not because its individual components are unprecedented.
The exact queries, inclusion rule, limitations, and registered source IDs are
preserved in `registry/mini-paper-related-work.json`. This bounded scan is not a
systematic review or proof of universal novelty.

| System or standard | What it contributes | Engine decision |
|---|---|---|
| [W3C Web Annotation](https://www.w3.org/TR/annotation-model/) | Shareable JSON annotations and fragment, position, and exact-text selectors. | Borrow redundant selectors for anchors; retain stricter internal source and revision authority. |
| [W3C PROV](https://www.w3.org/TR/prov-overview/) | Entity, Activity, Agent, derivation, generation, and attribution vocabulary. | Provide a future interchange adapter for build activities; do not replace epistemic or argumentative fields. |
| [JATS 1.4](https://jats.nlm.nih.gov/) | Publisher-grade article structure, citations, references, and internal identifiers. | Add as a later export adapter after Markdown/JSON parity; do not make XML the evidence core. |
| [RO-Crate](https://www.researchobject.org/ro-crate/specification/1.3/index.html) | Portable JSON-LD packaging of files, software, workflows, and provenance. | Package a future frozen release; do not substitute crate-level metadata for paragraph genealogy. |
| [Nanopublications](https://nanopub.net/docs/) | Atomic assertion, assertion provenance, and publication information. | Optional reviewed-claim export; avoid mandatory RDF for draft paragraphs. |
| [Manubot](https://manubot.org/) | Git/Markdown authoring, identifier-based citations, and automated HTML/PDF/DOCX builds. | Borrow reproducible multi-format publishing; keep the project's own paragraph manifests and release gates. |
| [Argdown](https://argdown.org/) | Human-readable arguments, support/attack/undercut relations, tags, and multiple views. | Generate an optional author view from the validated graph; never treat imported syntax as reviewed truth. |
| [Argument Interchange Format](https://www.arg-tech.org/wp-content/uploads/2011/09/aif-spec.pdf) | Separation of information nodes from inference, conflict, and preference nodes. | Borrow conceptual distinctions only; the internal graph also needs review, freshness, source hashes, and release state. |
| [CiTO](https://sparontologies.github.io/cito/current/cito.html) | Typed citation intent and inverse citation relationships. | Map a small reviewed subset of internal edge types for outward interchange. |
| [STORM](https://aclanthology.org/2024.naacl-long.347/) | Multi-perspective research and question asking before outline construction. | Use as an untrusted candidate-generation stage; independently evidence-gate every proposed perspective and outline. |
| [PaperQA2](https://arxiv.org/abs/2409.13740) | Iterative search, citation traversal, evidence ranking, contradiction search, and abstention. | Borrow evaluation ideas; pin every configuration and never auto-accept generated claims or citations. |
| [PRISMA-S](https://www.prisma-statement.org/prisma-search) | Reproducible reporting of literature searches. | Record query, source, date, filters, counts, deduplication, and selection decisions even when the work is not a formal systematic review. |

## Canonical build chain

```text
registered source revision
-> byte-exact chunk
-> reviewed or bounded claim
-> argument / objection / falsifier / proof gap
-> thesis node
-> stable mini-paper unit
-> audience-specific rendered paragraph
-> Markdown plus JSON sidecar
-> future JATS / PDF / DOCX / RO-Crate adapters
```

The canonical plan is `registry/mini-paper-plan.json`. It defines stable
`MPU-####` units, a closed tag vocabulary, audience profiles, authored prose,
and versioned comparison weights. The builder derives all claims, sources,
chunks, objections, falsifiers, proof gaps, paths, locators, and hashes from the
existing white-paper evidence export. Authors do not duplicate genealogy.

## Generated versions

- `executive`: begins with the present evidence boundary and decision-relevant
  asset, then moves through observed design, conditional exposure, externality,
  recommendation, and research horizon.
- `academic`: frames the research boundary and construct before method-like
  observations, mechanism, hypothesis, governance conclusion, and benchmark
  agenda.
- `adversarial`: starts with the strongest counterevidence, tests each causal
  step, and permits only the recommendation that survives those objections.

Every version uses the same seven logical units and identical genealogy. Text,
section, and order can vary; evidence cannot.

## Sidecar and anchoring contract

Each rendered paragraph contains an HTML-compatible anchor such as
`<a id="mpu-0004"></a>`. Its sidecar records the stable unit ID, profile render
ID, section and order, controlled tags, claim IDs, semantic and epistemic roles,
`does_not_prove`, complete genealogy, genealogy hash, rendered-text hash, and a
W3C-Annotation-inspired exact-text selector with prefix and suffix.

Identity does not depend on display order. Moving `MPU-0004` leaves its anchor
and genealogy intact; changing its prose changes the render hash. Changing its
evidence changes the genealogy hash and every affected sidecar.

## Structure simulation

The engine exhaustively evaluates all `7! = 5,040` unit orders for each profile,
or 15,120 structures in the current build. It uses integer basis points for:

- genealogy completeness;
- early evidence-boundary visibility;
- objection coverage;
- falsifier visibility;
- profile-specific causal ordering; and
- proof-gap visibility.

The result is `compare_only`. There is no universal winner. A structure can be
optimal for a declared profile while remaining equally valid or inferior for a
different audience. Scores cannot modify review state, evidence, claim status,
or release eligibility.

## Next useful extensions

1. Add an immutable search-receipt schema modeled on PRISMA-S reporting.
2. Generate Argdown and CiTO adapters from reviewed internal edges.
3. Add JATS, PDF, and DOCX rendering only after byte/hash parity tests.
4. Package a human-approved frozen export as RO-Crate.
5. Add remove-one-evidence, contradiction-propagation, common-source
   independence, and reversed-claim counterfactual simulations.
6. Evaluate retrieval or multi-agent prewriting only against a protected paper
   quality and citation-recall set; direct long context and lexical lookup
   remain the baseline.

No extension may activate publishing, live monitoring, external model calls,
or claim promotion without the existing human and release gates.
