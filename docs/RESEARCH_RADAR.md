# Research Radar

The **Cassandra Radar** is the project's early-warning research surface. The
name indicates that a signal deserves investigation; it does not make the
signal true.

## Signal families

- vertical product, skill, or connector launches;
- access to a system of record or private knowledge base;
- forward-deployed engineering and co-development;
- workflow templates encoding exceptions, escalation, or preferred decisions;
- telemetry, evaluation, feedback, retention, training, or data-use changes;
- customer-owned versus provider-owned orchestration and storage;
- export, interoperability, portability, and tested replacement;
- acquisitions, investments, partnerships, and platform consolidation;
- security, privacy, residency, zero-retention, and audit-control changes;
- regulator, standards-body, procurement, litigation, or enforcement changes;
- repository releases, pull requests, issues, terms, and documentation revisions.

## Candidate-only pipeline

```text
allowlisted public source
-> metadata and revision observation
-> optional permitted private capture
-> deterministic diff
-> untrusted candidate signal
-> independent evidence review
-> claim-impact review
-> human publication decision
```

No watcher may edit a claim, thesis, argument, or white paper. Silence is not
“no change”: rate limits, truncation, parser failure, inaccessible pages, and
stale sources must produce explicit failure receipts.

## Time model

Every signal records:

- `event_time`: when the underlying event occurred;
- `observed_at`: when the project learned of it;
- `valid_from` and `valid_to`: the asserted validity interval;
- `captured_at`: when bytes or metadata were captured;
- `last_verified_at` and `next_review_at`;
- `freshness_status`: `current`, `watch`, `stale`, `superseded`, or `unknown`;
- `freshness_reason` and any `supersedes_id`.

Default review windows are deterministic:

- immutable Git revision: current for that revision;
- terms, regulation, or official standards: on amendment and before
  publication, otherwise 90 days;
- retention, training, data-use, privacy, or security page: 30 days;
- vendor product documentation: 60 days;
- official partnership statement: 180 days;
- dynamic page without a content hash: always `watch`;
- missing URL or revision: `unknown`.

## Safe monitoring contract

Monitoring is not activated by this repository. Any future automation requires
explicit owner approval and must:

1. use an allowlist with purpose, method, rights review, cadence, and retention;
2. run outside the public repository's privileged CI context;
3. have no private-corpus, publication-token, or claim-promotion access;
4. treat all fetched content as hostile and non-executable;
5. use conditional requests, pagination receipts, bounded retries, backoff, and
   rate-limit receipts where supported;
6. store hashes and locators by default, with full captures only when permitted;
7. preserve a first-capture boundary and disclose archive gaps;
8. stop on repeated access errors, rights conflicts, schema failures, or any
   public/private-boundary crossing.

For a future GitHub watcher, reverify GitHub's official
[REST API best practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api)
and [secure-use guidance for Actions](https://docs.github.com/en/actions/reference/security/secure-use)
before activation. Those dynamic pages are registered as `SRC-0031` and
`SRC-0032`.

## Manual operating rhythm

The `WATCH-COLLECTIVE-ALPHA` lane, also called the **Ajax Line** research lane,
tracks collective professional-knowledge externalities, derived-data rights,
legal self-play or simulation, frontier strategy methods, algorithmic
efficiency, compute, firm-owned ontologies, and portability. Its signals must
route to the objections, falsifiers, and proof gaps in
`registry/argument-mesh.json`; a new signal cannot promote the thesis.

- Weekly: product, repository, partnership, and customer-deployment signals.
- Monthly: privacy, retention, training, security, portability, and terms.
- Quarterly: industry profiles, regulatory landscape, and thesis implications.
- Before publication: reverify every dynamic load-bearing source.

The watchlist and methodology live in
`registry/research-radar-watchlist.json` and
`registry/industry-research-taxonomy.json`.
