# Licensing Options and Decision Gate

This is a decision brief, not legal advice. No license change is authorized by
this document.

## Current blocker

The root `LICENSE` file is only an Apache-2.0 application notice, not the full
Apache License 2.0 text, and its copyright line does not identify a holder.
Public contribution intake should remain closed until the owner identifies the
rights holder, chooses a license model, installs complete license texts, and
publishes an exact path-level license map.

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

## Options

| Model | Protection | Tradeoff |
|---|---|---|
| Apache-2.0 for everything | Simple, permissive, express patent grant, attribution notices | Commercial reuse and proprietary forks are allowed; little reciprocity |
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

## Recommended decision path

For a genuinely public research commons, the cleanest default is:

- **software, executable schemas, validators, configuration, and tests:**
  Apache-2.0 or MPL-2.0 after a deliberate reciprocity choice;
- **original scholarly prose and human-readable taxonomy commentary:**
  CC BY 4.0;
- **normalized factual metadata:** CC0 only if you intentionally prioritize
  interoperability over legally required attribution; otherwise CC BY 4.0;
- **raw third-party captures:** excluded unless redistribution rights are
  individually documented;
- **name and logo:** reserved under a separate trademark policy;
- **private raw research, agent workflows, and unpublished theses:** not part of
  the public distribution.

If your priority is stopping a commercial actor from reusing the published
research without permission, choose a noncommercial or commercial-dual-license
model only after counsel review and accept that the repository should not be
described as fully open source. A public GitHub host may also receive rights
under its own platform terms independently of your repository license.

## Contributor rights

Start with DCO 1.1 plus an explicit inbound-equals-outbound rule for each path.
Do not adopt a CLA by default. A counsel-reviewed CLA may be warranted if you
need future relicensing, copyright assignment, or proprietary dual licensing.
Decide that before accepting outside contributions.

## Required human decision

Before opening intake, record:

1. copyright holder or governing entity;
2. open-commons versus commercial-protection objective;
3. Apache-2.0 versus MPL-2.0 for software;
4. CC BY, CC BY-SA, or CC BY-NC-SA for original research;
5. metadata/database treatment;
6. trademark/name policy;
7. DCO-only versus a counsel-reviewed CLA;
8. hosting-platform acceptance;
9. whether the private workspace moves to a physically separate repository.
