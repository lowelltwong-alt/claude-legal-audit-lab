# Source-Aware Chunk Contract

This contract governs deterministic candidate chunks. A chunk is a retrieval
and citation unit, never a factual finding or source authority.

## Public surfaces

- `registry/chunk-policy.json` is authored method: declared input classes,
  boundary rules, and format version.
- `registry/chunk-registry.json` is a generated candidate projection. It may
  expose stable IDs, source IDs, public paths, revisions, hashes, locators, and
  structural metadata. It must never contain ignored raw-capture payloads,
  client data, credentials, or reconstructed private text.
- A deterministic builder and `--check` mode must rebuild the registry
  byte-for-byte from the pinned public inputs and policy.

## Identity and boundaries

Each ID is `chk:sha256:` plus the complete 64-character lowercase SHA-256 over
canonical compact UTF-8 JSON containing chunk kind, source ID, source revision,
parent ID, discriminated locator, content hash, and policy revision. Exact
UTF-8 byte offsets are authoritative; line ranges are human-facing aids. The
builder fails on a duplicate ID or conflicting identity preimage. Whitespace,
line endings, Unicode, and source bytes are never normalized before hashing.
`registry/chunk-id-migration.json` maps the unpublished v1 IDs to v2.

The initial corpus has three kinds:

| Kind | Boundary | Citation round-trip |
|---|---|---|
| `static_file_span` | Half-open byte range in a pinned Git blob | pinned commit, blob OID, path, byte range, line hints |
| `pr_file_record` | One captured public PR-file record | PR number, capture page hash, item index, path/status/blob SHA when supplied |
| `web_capture_span` | One captured public response span, represented by approved metadata until activated | source ID, capture hash, retrieval time, locator; raw bytes stay private |

Static text boundaries must preserve line endings and reconstruct exactly when
their ordered byte ranges are concatenated. A partition must cover every parent
byte exactly once, with no overlap, gap, or split inside a UTF-8 code point.
Markdown and code may additionally
record heading, symbol, or syntax hints, but hints may not alter the boundary.
PR records must retain pagination page order and never treat a missing or
truncated patch as empty content. Public captures are opaque custody nodes;
the public registry identifies their hash and limits but does not copy content.

## Genealogy and edges

Every chunk records direct input identity, source IDs, and a candidate authority
label. Cross-file, PR-to-file, source-to-claim, and chunk-to-chunk relations are
separate typed edges with an exact locator and a `does_not_prove` limit. An edge
does not promote either endpoint. Multiple edges between the same nodes are
allowed only when their type and locator differ.

## Required rejection tests

The builder or validator must fail for an overlapping/gapped/reordered static
partition, stale input hash, changed byte or line boundary, duplicate ID,
unknown source, invalid PR page order or endpoint, missing terminal-pagination
proof, capture hash mismatch, a PR detail/file-count mismatch, guessed rename,
or any attempt to emit `.private/` or `private/` paths or payload text into a
public candidate artifact.

## Retrieval task and limits

The initial retrieval task is exact evidence drill-down: given a chunk ID, a
reader can identify the pinned file lines, public PR-file observation, or
private-custody source hash from which it derives. Semantic similarity, vector
ranking, chunk-size optimization, and generated centrality are outside this
contract and cannot promote a claim.

## Activation-gated families (designed, not enabled)

Static `static_file_span` chunks are the only family the builders may emit
today. Policy field `activated_chunk_kinds` is the machine gate; it currently
lists only `static_file_span`. The following families are specified so a later
activation can remain deterministic; they must not appear in
`registry/chunk-registry.json` until they are added to `activated_chunk_kinds`
with matching builder support and tests.

### `pr_file_record`

- **Input:** `results/pr-commit-diff-linkage.json` only.
- **Eligibility:** emit a chunk only when
  `public_capture_linkage.status == "linked_verified_capture"` and the files
  capture reports complete pagination (`captured_complete` with matching
  `file_count`). Records with `unknown` or any other linkage status stay out of
  the public chunk projection.
- **Boundary:** one public PR-file metadata record per chunk. Locator fields
  may include PR number, files-page hash, item index, path, status, and blob
  SHA when the public capture supplies them.
- **Prohibitions:** never embed patch text, diff bodies, or private raw response
  bytes; never invent a rename; never treat a missing page as empty content.

### `web_capture_span` / public-capture metadata

- **Input:** `registry/source-registry.json` public capture metadata only.
- **Boundary:** one opaque custody node per capture, identified by source ID,
  capture hash, retrieval time, and content type.
- **Prohibitions:** never copy raw private response payloads, `.private/` or
  `private/` paths, or reconstructed response text into the public registry.
  The chunk proves custody identity, not content.
