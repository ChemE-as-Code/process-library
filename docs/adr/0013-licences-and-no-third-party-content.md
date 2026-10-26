# 0013. MIT for code, CC BY 4.0 for data and designs; never copy third-party content

- **Status:** Accepted, 2026-10-23
- **Scope:** `LICENSE`, `LICENSE-DATA`, CLAUDE.md, CONTRIBUTING.md, every process folder

## Context

Everything in the library is meant to be published: designs, LCI datasets and the tooling.
Chemical engineering work leans on licensed and copyrighted material (papers, standards, vendor
datasheets, ecoinvent). Much of the content is written by agents, which may reproduce what a
user pastes. One unlicensed table or ecoinvent value would make a public build unpublishable.

## Decision

- Code is under **MIT** (`LICENSE`); data and designs under **CC BY 4.0** (`LICENSE-DATA`).
  Contributors agree that their contributions are published under these licences.
- **Never copy third-party content**: no tables, figures, drawings, P&IDs, datasheet or manual
  text, screenshots, passages of publications, and no values from licensed databases.
- **Facts and numbers** may be used in our own form, with their source recorded (`source:`,
  `provenance:`, `references:`, DESIGN.md); estimates are marked ASSUMED.
- Drawings and figures are generated from the library's own files by `cheme`.
- Openly licensed material only with its licence and attribution in a `NOTICE.md`, and only if
  compatible with CC BY 4.0 / MIT. When unsure, leave it out and ask.
- The rule is in the root CLAUDE.md, so it binds agents in every process folder.

## Consequences

- Public builds and releases can be published without a per-item licence check.
- Sourcing takes more effort: benchmarks cite ranges in our own form
  ([0011](0011-benchmark-registry-with-cited-ranges.md)), and ecoinvent is linked, never copied
  ([0008](0008-brightway-workbook-linked-by-name.md)).
- The repository mixes two licences, which matters for archive deposits
  ([0012](0012-versioning-releases-and-dois.md)).

## Evidence

- `0a519d2` "Licences (MIT code, CC BY 4.0 data) and the rule never to copy third-party
  content", [#24](https://github.com/ChemE-as-Code/process-library/pull/24).
- `LICENSE`, `LICENSE-DATA`, CLAUDE.md "Sources and licences", CONTRIBUTING.md.
