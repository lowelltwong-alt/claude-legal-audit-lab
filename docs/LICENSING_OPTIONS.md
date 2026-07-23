# Licensing Options and Decision Gate

This is a decision brief, not legal advice.

## Owner decision (2026-07-22)

| Item | Decision |
|---|---|
| Copyright holder | **Lowell T Wong** |
| Software / schemas / scripts / tests / registries | **Apache License 2.0** (full text in root `LICENSE`) |
| Original scholarly prose (`docs/`, `audit/` prose, etc.) | **CC BY 4.0** (`LICENSES/CC-BY-4.0.txt`) |
| Path-level map | [`docs/LICENSE_MAP.md`](LICENSE_MAP.md) |
| Attribution / NOTICE | root [`NOTICE`](../NOTICE) |
| Trademark / Anthropic marks | Not granted; no Anthropic-cooperative branding |
| Public product release | Remains **blocked** (license clarity ≠ READY) |
| Outside contribution intake | Remains closed until separately activated |

## Prior blocker (resolved for license text)

The root `LICENSE` previously held only an Apache-2.0 application notice without
a named holder. That is replaced by the full Apache-2.0 text, named copyright
holder, CC BY 4.0 companion license, NOTICE, and path-level map.

## What “protection” can mean

Different controls protect different interests:

- copyright license: reuse, modification, distribution, and reciprocity;
- patent terms: patent grants and termination;
- database terms: extraction and reuse where database rights exist;
- trademark policy: project name, logo, and implied endorsement;
- contribution process: contributor authority and provenance;
- private/public architecture: material never published at all;
- platform terms: separate rights granted to the hosting platform.

No license creates ownership over facts, ideas, methods, or an industry's
underlying ontology. It can govern original expression and, in some
jurisdictions, protected selection/arrangement or database rights.

## Options considered

| Model | Protection | Tradeoff |
|---|---|---|
| Apache-2.0 for everything | Simple, permissive, express patent grant, attribution notices | Commercial reuse and proprietary forks are allowed; little reciprocity |
| **Apache-2.0 software + CC BY 4.0 research (chosen)** | Familiar software license, clear attribution for prose | Commercial reuse remains allowed; dual-license boundary must stay mapped |
| MPL-2.0 for software; CC BY 4.0 for original research | File-level software copyleft plus scholarly attribution | Mixed-license boundary must be meticulous; commercial use remains allowed |
| Apache-2.0 for software; CC BY 4.0 for original research; CC0 for deliberately open metadata | Familiar software license, clear attribution for prose, interoperable metadata | Commercial reuse remains allowed; CC0 waives attribution where effective |
| Apache-2.0 or MPL-2.0 for software; CC BY-SA 4.0 for original research; ODbL for a qualifying database | Reciprocity for adapted research/database | Higher compliance burden and compatibility risk |
| Software license plus CC BY-NC-SA 4.0 for original research | Reserves commercial research reuse for separate permission | Not open source/open knowledge in the conventional sense; “noncommercial” can be fact-specific and may deter academic/industry contribution |
| Bespoke source-available or “no AI” terms | Can target a particular commercial concern | Legal review burden, weak ecosystem compatibility, and cannot override hosting-platform terms or upstream licenses |

Creative Commons recommends software-specific licenses for software. OSI-open
software licenses cannot restrict a field of endeavor, including commercial or
AI use. MPL-2.0 requires sharing modifications to covered files while allowing
combination with larger proprietary works. Apache-2.0 permits broad reuse and
includes copyright and patent grants but does not grant trademark rights.

Authoritative starting points:

- [Open Source Definition](https://opensource.org/osd) (`SRC-0025`)
- [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) and
  [application guidance](https://www.apache.org/legal/apply-license) (`SRC-0026`)
- [Mozilla MPL 2.0 FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/) (`SRC-0027`)
- [Creative Commons FAQ](https://creativecommons.org/faq/) (`SRC-0028`)
- [Developer Certificate of Origin 1.1](https://developercertificate.org/) (`SRC-0029`)
- [GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service)
  (`SRC-0030`)

## Implemented path

For this public research commons:

- **software, executable schemas, validators, configuration, tests, and machine registries:**
  Apache-2.0;
- **original scholarly prose and human-readable research commentary:**
  CC BY 4.0;
- **normalized factual metadata in registries:** treated as Apache-2.0 machine artifacts (not CC0);
- **raw third-party captures:** excluded unless redistribution rights are
  individually documented;
- **name and logo:** reserved; no Anthropic marks;
- **private raw research, agent workflows, and unpublished private theses:** not part of
  the public distribution (`private/` / `.private/`).

## Contributor rights

Start with DCO 1.1 plus an explicit inbound-equals-outbound rule for each path
when intake opens. Do not adopt a CLA by default. A counsel-reviewed CLA may be
warranted if you need future relicensing, copyright assignment, or proprietary
dual licensing.

## Remaining human gates (not completed by this license install)

Before opening intake or marking public READY, still record/confirm as needed:

1. trademark/name policy details beyond “no Anthropic marks”;
2. DCO-only versus a counsel-reviewed CLA;
3. hosting-platform acceptance;
4. whether the private workspace moves to a physically separate repository;
5. separate public READY / contribution-activation authorization.
