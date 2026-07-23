# Path-level license map

**Copyright holder:** Lowell T Wong (2026)  
**Not legal advice.** This map states how this repository licenses *original* project material. Third-party and upstream works keep their own terms.

## Summary

| Class | License | Text |
|---|---|---|
| Software & machine artifacts | [Apache License 2.0](../LICENSE) | `LICENSE`, `NOTICE` |
| Original research prose | [CC BY 4.0](../LICENSES/CC-BY-4.0.txt) | `LICENSES/CC-BY-4.0.txt`, `NOTICE` |
| Upstream / third-party | **Not relicensed** | Keep vendor licenses |

## Apache-2.0 (software commons)

Unless a path is listed under CC BY 4.0 or Excluded below, original project material is Apache-2.0, including:

- `scripts/`, `tests/`, `schemas/`, `rust/`, `runtime-lab/`
- `registry/*.json` (machine registries and authored JSON contracts)
- `patterns/`, `prompts/`, `templates/`
- `Makefile`, `requirements-dev.txt`, CI/config under `.github/`, `.codex/`
- builders/validators and generated public machine outputs that are project-authored tooling products (hashes/graphs/exports remain **candidate evidence**, not source truth)

SPDX: `Apache-2.0`

## CC BY 4.0 (original scholarly prose)

Original human-readable research commentary and narrative analysis authored for this project:

- `README.md`
- `docs/**/*.md` (including thesis, Ajax Line, licensing briefs, threat/scope docs)
- `audit/**/*.md` and `audit/**/*.csv` (project-authored audit prose/tables)
- `research/**/*.md` (project-authored interrogatory / research notes)
- `AI_FRONT_DOOR.md`, `AI_TABLE_OF_CONTENTS.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md`
- `public/generated-release-artifacts/candidate/**/*.md` (project-authored candidate prose; still **release-blocked** as a product publication)

When sharing or adapting CC BY material, provide attribution as in `NOTICE` (creator: Lowell T Wong; link to this repository; note modifications).

SPDX: `CC-BY-4.0`

## Excluded / not covered by these grants

| Path / class | Reason |
|---|---|
| `upstream/claude-for-legal/` | Third-party upstream; keep Anthropic/upstream license terms |
| `private/`, `.private/` | Not part of the public distribution |
| Raw third-party captures under ignored private trees | No redistribution grant unless separately documented |
| Trademarks / project branding | No trademark license; Anthropic marks not authorized |
| Facts, ideas, methods as such | Copyright licenses do not own facts or abstract methods |

## Dual-licensed files

If a file mixes substantial original prose and executable material, follow the dominant class in this map. Prefer keeping executable logic under Apache-2.0 paths and scholarly narrative under `docs/` / `audit/` / `research/`.

## Decision record

Owner decision 2026-07-22: Apache-2.0 for software; CC BY 4.0 for original research prose; copyright holder Lowell T Wong. See `registry/release-readiness.json` (`REL-DEC-002`, `REL-DEC-003`) and `docs/LICENSING_OPTIONS.md`.
