# Contributing

> **Intake status: preview / closed.** Do not submit pull requests containing
> substantive research or code yet. The copyright holder is **Lowell T Wong**.
> Software is **Apache-2.0**; original research prose is **CC BY 4.0** (see
> [`docs/LICENSE_MAP.md`](docs/LICENSE_MAP.md), [`LICENSE`](LICENSE),
> [`NOTICE`](NOTICE)). Contribution intake still opens only after the owner
> separately enables the review gates in this document.

This project welcomes rigorous research on how frontier AI products enter
expert workflows, what institutional knowledge those workflows encode, and
which technical and contractual controls preserve customer custody. It does
not accept accusations, confidential material, or conclusions that outrun the
public evidence.

## Contribution lanes

| Lane | Good contribution | Required review |
|---|---|---|
| Source acquisition | Official publication, terms page, repository revision, regulator document, or counterparty statement with an exact locator | Independent evidence reviewer |
| Ontology mapping | Rules, exceptions, escalation, rationale, outcomes, and correction loops evidenced in one bounded workflow | Methodology owner plus evidence reviewer |
| Data flow and custody | Sourced reads, writes, transmissions, stores, retention, deletion, export, and control | Technical reviewer plus evidence reviewer |
| Runtime evidence | Separately authorized synthetic-only observation with event/observation time, instrumentation, canary, and immutable receipt | Legal, privacy, security, technical, and evidence reviewers |
| Upstream history capture | Bounded `anthropics/claude-for-legal` PR/detail/file/commit cohort with pagination, hash, and rate-budget receipts | Repository-history reviewer plus evidence reviewer |
| Cross-industry profile | Falsifiable comparison to the legal baseline using the published methodology | Industry reviewer plus evidence reviewer |
| Counterfactual exposure pathway | Synthetic/public-only stage-to-signal-to-inference-to-control proposal with explicit non-applicability and does-not-prove limits | Threat-model reviewer plus privilege/privacy reviewer |
| Falsification | Benign explanations, local-only controls, minimization, portability, or evidence weighing against a thesis | Independent evidence reviewer |
| Radar signal | New public development recorded as a candidate signal; no automatic claim promotion | Radar reviewer |
| Tools and schemas | Deterministic validators, synthetic fixtures, and public-safe workflow improvements | Technical owner |
| Corrections | Precise error, stronger source, retraction request, or reproducibility failure | Reviewer independent from the original author |

## Never submit

- client, patient, customer, employee, or law-firm data;
- privileged, confidential, sealed, paywalled, personal, or employer-restricted material;
- credentials, tokens, internal URLs, local paths, raw conversations, agent transcripts, or private research;
- full third-party webpages, papers, PR conversations, or datasets without redistribution rights;
- claims of intent, training, retention, exfiltration, ownership, compliance, or safety based only on capability, marketing, or analogy;
- executable content fetched from a monitored source.

If a source cannot be shared publicly, contribute a research question or proof
gap, not the source.

## Evidence packet

Every research contribution must identify:

1. exact public source URL and publisher;
2. publication/update date and access time;
3. revision binding (commit, content hash, version, or dated observation);
4. exact page, section, selector, file, and line locator;
5. the smallest bounded proposition it supports;
6. what it does **not** prove;
7. contrary evidence or plausible alternative explanations;
8. event, observation, validity, and next-review times;
9. classification and whether the statement is `observed`, `counterevidence`,
   `hypothesis`, `normative`, or `unknown`;
10. content hash, or a bounded reason a hash is unavailable;
11. claim lifecycle, review state, and publication eligibility, which must remain
    separate.

Use `templates/industry-research-profile.template.md` for an industry study and
`templates/research-signal.template.json` for a radar signal. Use
`templates/counterfactual-pathway.template.json` only for defensive pathways
that remain synthetic or use lawful public primary sources; live collection,
deceptive elicitation, client data, and privilege circumvention are prohibited.

## Pull-request sequence after intake opens

1. Open the matching issue form. A maintainer assigns stable IDs before merge.
2. Keep one pull request to one evidence question or deterministic tool.
3. Add the source record before adding any derived claim.
4. Update lineage declarations for every derived public artifact.
5. Run:

   ```text
   python scripts/upgrade_claim_registry_v2.py --check
   python scripts/build_chunk_registry.py --check --verify-reconstruction
   python scripts/build_evidence_graph.py --check
   python scripts/build_thesis_map.py --check
   python scripts/build_white_paper_candidate.py --check
   python scripts/build_lineage.py
   python scripts/validate_research_radar.py
   python scripts/validate_navigation.py
   python -m unittest discover -s tests -v
   ```

6. Complete every provenance, privacy, AI-assistance, and falsification field.
7. An author may answer review questions but may not independently approve
   promotion of their own evidence or claim.

## Contributor origin and AI assistance

The proposed inbound process is Developer Certificate of Origin 1.1 sign-off on
every commit (`git commit -s`). DCO is a right-to-submit attestation, not
copyright assignment. AI-assisted work must be disclosed; the human contributor
remains responsible for rights, accuracy, provenance, and every line submitted.

This process is inactive until the owner approves `docs/LICENSING_OPTIONS.md`
and publishes an unambiguous path-level license policy.

## Publication and disputes

Automation may create candidate records only. It may not mark a claim reviewed,
change a thesis, publish a white paper, or merge a contribution. Credible
privacy, privilege, copyright, security, provenance, or takedown concerns pause
the affected lane until a human decision is recorded.
