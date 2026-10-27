# 0021. Name the three axes design maturity, calculation maturity and review status

- **Status:** Proposed, 2026-10-27
- **Deciders:** the owner (core#323, #87)
- **Scope:** documentation and the descriptions of `schemas/process.schema.json`; no field, file
  or data changes

## Context

"Maturity" meant several things across the library and core. `process.yaml` `maturity`
(`concept` to `operating-reference`) is what a process claims about its design. `cheme
maturity` evaluates a different scale from the files of an engineering project (`sourced`,
`balanced`, `predictive`, `engineering`) into `checks/maturity.json`, and maps each level onto
the highest manifest label it supports, warning (`cheme.maturity-claim-exceeds`) when a manifest
claims more. `validation.status` is a third, independent thing: who has checked the design.
The README mixed them in one parenthesis per process, and the papers need one vocabulary. core#323
sets it for every repository in a glossary (`docs/concepts/glossary.md` in core).

Renaming the fields would have needed a schema version and a migration of every manifest, the
catalog and the LCI build, for a change of words only.

## Decision

The library follows core's glossary, with labels and documentation only:

- `process.yaml` `maturity` is the **design maturity**: claimed, capped by evidence;
- `checks/maturity.json` is the **calculation maturity**: evaluated by `cheme maturity`;
- `process.yaml` `validation.status` is the **review status**: set by people only.

The word "maturity" is qualified in user-facing text. The field names stay. The schema
descriptions of `maturity` and `validation` state the axis and link the glossary; the README,
CONTRIBUTING, `docs/coverage.md`, `docs/governance.md`, `templates/process/` and the process pages
of the docs site (`docs/hooks/library.py`) use the terms. The project is called ChemE-as-Code;
"Plant-as-Code" is used only when citing the Comment (Schweidtmann & Demeyer 2026).

## Consequences

- No migration: manifests, the catalog and the LCI database are unchanged.
- The field name `maturity` remains bare in files and in the catalog's JSON; consumers (the
  Atlas, the viewer) label it "design maturity" themselves (ChemE-as-Code/website#71).
- The glossary link points at core's `docs/concepts/glossary.md`, which core#323 adds; until it
  is merged the link does not resolve.
- Generated texts of the build scripts (e.g. the LCI comments "Maturity: ...") are not relabelled
  here: changing them changes build outputs and is left to a follow-up.
- The README no longer carries the "Formerly `ChemE-as-Code/example-asu`" note that ADR 0003
  lists; the history of that move stays in ADR 0003.

## Evidence

- core#323 (the glossary), #87 (this change).
- `schemas/process.schema.json` (`maturity`, `validation` descriptions), README.md (process table
  and the axes), CONTRIBUTING.md, `templates/process/`.
- core's `src/chemeascode/project/maturity.py` (`LEVELS`, `LIBRARY_MATURITY`,
  `cheme.maturity-claim-exceeds`).
