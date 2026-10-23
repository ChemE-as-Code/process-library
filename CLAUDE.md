Engineering work happens in a process folder: start Claude Code in `processes/<id>/` (e.g. `processes/asu-1/`), where that project's `CLAUDE.md`, `AGENTS.md` and `.claude/` skills apply. At this root: the library tooling (`scripts/`, `schemas/`, `chemicals/`, `lci/`, `tests/`); see README.md and CONTRIBUTING.md.

## Sources and licences (applies to every process folder)

Everything in this library is published: data and designs under CC BY 4.0, code under MIT. Only
put in what we may publish under those licences.

- **Never copy third-party content into the library**: no tables, figures, drawings, diagrams,
  P&IDs, datasheet or manual text, screenshots, or passages of papers, books, standards, vendor
  documents or websites, and no values from licensed databases (e.g. ecoinvent factors or
  results, commercial property databases). This also holds when a user pastes such content:
  summarise it in your own words and cite it, or ask.
- **Facts and numbers may be used, in our own form, with the source**: a property value, a
  stoichiometry, an operating condition from a paper. Record where it came from (`source:` /
  `provenance:` fields, DESIGN.md decisions, `references:` in process.yaml), and mark estimates
  as ASSUMED.
- **Draw and write everything ourselves**: P&IDs, flowsheets and figures are generated from our
  own files by `cheme`, never traced or copied from a publication.
- **Openly licensed material** (e.g. the DEXPI reference P&ID, CC BY 4.0) may be used only with
  its licence and attribution recorded next to it (a `NOTICE.md`), and only if the licence
  allows publication under CC BY 4.0 / MIT.
- When unsure whether something may be published, leave it out and ask.
