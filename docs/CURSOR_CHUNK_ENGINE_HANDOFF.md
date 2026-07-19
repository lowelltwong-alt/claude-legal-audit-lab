# Cursor Handoff: Deterministic Chunk Engine

## Scope

Implement and verify the deterministic chunk-control plane only. Do not alter
claims, source interpretations, private raw research, release status, names,
licenses, Git history, or external systems.

## Current state

- Python reference builder: `scripts/build_chunk_registry.py`
- Authored policy: `registry/chunk-policy.json`
- Schemas: `schemas/chunk-policy.schema.json`,
  `schemas/chunk-registry.schema.json`
- Python output: `registry/chunk-registry.json`
- Rust parity implementation: `rust/chunk-engine/`
- Contract: `docs/SOURCE_AWARE_CHUNK_CONTRACT.md`

The completed implementation produces 438 candidate static-file chunks and 246
inverse adjacency edges from immutable Git blobs at the pinned revision. It
uses full-SHA v2 identities and 200-line, byte-exact spans and emits no source
text, `.private/`, or `private/` material.

## Implemented work

1. The Rust executable accepts an explicit repository root (defaulting to
   the current workspace root or a reliable ancestor search), rather than
   assuming its Cargo directory is the repository root.
2. Rust output is exactly byte-for-byte equal to the Python registry for the
   same workspace. Do not independently choose JSON formatting, ordering, ID
   composition, or boundary behavior.
3. A deterministic parity test runs Python, runs Rust into a temporary
   output, and compares bytes without modifying the authoritative registry.
4. Reconstruction tests enforce:
   - every static parent is partitioned with no gaps or overlaps;
   - each chunk content hash matches its exact byte span;
   - reassembled parent bytes match parent SHA-256;
   - CRLF/LF and Unicode bytes are not normalized;
   - a boundary cannot split a UTF-8 code point;
   - output contains no `.private/` or `private/` path, raw-capture path,
     credential, or source-text payload.
5. The production validator rejects malformed policy/schema data and stale
   registry bytes.
6. Static parity passes; the PR file-record and public-capture metadata chunk
   families remain designed but inactive. They must preserve
   existing `linked_verified_capture`/`unknown` boundaries and never copy raw
   private response payloads into public output.

## Commands

```powershell
python scripts/build_chunk_registry.py
python scripts/build_chunk_registry.py --check --verify-reconstruction
python -m unittest tests.test_chunk_registry -v
cargo run --manifest-path rust/chunk-engine/Cargo.toml -- --check
python -m unittest discover -s tests -v
```

## Acceptance criteria

- Rust and Python outputs are byte-identical.
- All chunk tests and existing repository tests pass.
- `python scripts/validate_navigation.py` passes.
- Release status stays `blocked`; do not stage, commit, push, rename, or
  publish anything.

## Epistemic and privacy rules

Chunks are generated candidate evidence, not factual findings. Do not state or
infer provider intent, training, retention, customer data flow, or ontology
capture. Never read, print, copy, hash into public artifacts, or transmit
`.private/` or `private/` contents.
