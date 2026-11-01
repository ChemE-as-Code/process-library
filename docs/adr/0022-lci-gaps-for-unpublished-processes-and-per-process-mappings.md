# 0022. Report LCI mapping gaps of unpublished processes; keep a process's overrides with it

- **Status:** Accepted, 2026-10-28. Partly superseded by
  [ADR 0026](0026-public-processes-may-be-preliminary.md): a gap of a public process or in a
  `--public` build is no longer an error.
- **Deciders:** the owner (implemented by an agent session)
- **Scope:** the LCI pipeline (`scripts/build_lci.py`, `scripts/export_formats.py`,
  `scripts/lci_activities.py`), the mappings (`lci/mappings.yaml`, the new
  `processes/<id>/lca/mappings.yaml`, `schemas/lci-mappings.schema.json`,
  `schemas/lci-process-mappings.schema.json`) and the publication rules (`scripts/publication.py`
  `is_public`)

## Context

The strict LCI build (CI, `tests/test_utilities.py`, `tests/test_export_formats.py`) failed on
every exchange without a mapping in the shared `lci/mappings.yaml`. New case studies start as
internal processes (`publication.status: internal`). Their LCI is a preliminary gate-to-gate
inventory, and its background is connected later. In the batch of 2026-10-27, the case agents
were not allowed to touch shared files. So every case PR (#189-#192, #194-#196) failed CI until
#198 added the mappings for all of them in one change, prepared in an integration checkout with
every case branch merged.

The shared file also mixed two things. One is a vocabulary that every process uses:
technosphere entries by chemical or utility, biosphere identities, proxies, pass-through
decisions, cut-off exclusions, allocation. The other is per-process overrides (`exchanges:`,
keyed `"<pid>/<key>"`). Parallel PRs that each add their own process's overrides conflict on
that one file.

Options considered:

1. **One shared mapping PR per batch** (as #198): keeps today's rule. But every case PR stays red
   until the batch PR lands, the batch PR needs an integration checkout of all branches, and a
   late case reopens it.
2. **Agents edit the shared file in their case PRs**: each PR can go green on its own. But
   parallel PRs conflict on `lci/mappings.yaml`, the shared vocabulary changes without its own
   review, and a preliminary inventory is pushed towards guessed background links just to pass
   CI.
3. **This design**: an unmapped exchange of an unpublished process is a reported gap, not an
   error, and a process's overrides live in its own folder.

## Decision

- **Gaps, not errors, for unpublished processes.** An exchange of a process that is not public
  (`is_public` false) with no technosphere mapping or no biosphere identity is a *gap*
  (`GapError` in `build_lci.py`). A gap:
  - is reported per process: `gap:` lines of the build report, `lci/gaps.json`
    (`cheme-as-code/lci-gaps/v1`, always written, `count` 0 without gaps), `datapackage.json`
    `processes[].gaps` and `index.json` `gaps`, plus a caveat;
  - never fails `--strict` (it is neither an error nor a warning);
  - is exported **unlinked and marked**, never linked to a guess, dropped or zero-filled. The
    workbook exchange keeps its amount and unit, has no `database`, categories, reference
    product or Atlas alternative, and carries `atlas gap` (the reason). The activity gets
    `atlas gaps` (the count) and an `UNLINKED` line in its comment, and its Atlas page entry
    has `gap`. `install()` therefore reports the exchange unlinked and writes nothing.
  - The openLCA JSON-LD gives a gap a flow of its own in the category `ChemE-as-Code
    Atlas/unlinked (mapping gaps)`, with no default provider, and the process description notes
    it. The multifunctional file keeps `atlas gap` without a database. Both formats can carry an
    unlinked exchange, so the dataset is flagged, not skipped.
- **Public processes and `--public` builds keep today's rule exactly:** unmapped is an error.
  Every other finding (unit mismatch with a mapping, an override using an unknown entry, an
  uncurated free emission, schema errors, an incomplete flow identity) stays an error or
  warning for every process.
- **Per-process overrides live with the process.** `processes/<id>/lca/mappings.yaml`
  (`cheme-as-code/lci-process-mappings/v1`, `schemas/lci-process-mappings.schema.json`) holds
  that process's `exchanges:` overrides. Its keys are `<kind>:<id>` without the process id, and
  its entries have the schema of the shared file's (`$defs/exchange_override`). The build
  validates each file, reports problems with the file's path, and merges it as `"<id>/<key>"`.
  An exchange overridden in both files is an error. Every existing `exchanges:` entry of
  `lci/mappings.yaml` moved to its process's file unchanged. The shared file keeps the
  vocabulary; its `exchanges:` section remains valid for library-wide `"<key>"` overrides.

## Consequences

- A case PR builds strictly on its own. Its preliminary LCI is in the preview database with its
  gaps listed, and parallel PRs touch only their own folders.
- Mapping becomes an explicit step before publishing. Setting `publication.status: public` turns
  every gap of the process into an error, so a process cannot be published with one. `gaps.json`
  is the list to work through.
- The shared vocabulary still needs its own PR whenever a process needs a new technosphere
  entry (a new chemical or utility), biosphere identity, proxy or pass-through decision. A
  per-process override can only `use` entries that already exist.
- A preview database with gaps cannot be installed with `install()` until the gaps are mapped,
  by design: an unlinked exchange is never linked by name to whatever the background holds.
  Users of the preview see the gaps in `gaps.json` and the `atlas gap` column.
- Free emissions not in `pass_through:` and market losses or legs without a mapping stay errors
  for every process; they are curated decisions, not background links.

## Evidence

- `scripts/build_lci.py` (`GapError`, `Report.gaps`, `merge_process_mappings`, `build_activities`,
  `lci/gaps.json`), `scripts/export_formats.py` (`exchange_flow`), `scripts/lci_activities.py`
  (`_exchange`).
- `schemas/lci-process-mappings.schema.json`; `schemas/lci-mappings.schema.json`
  (`$defs/exchange_override`).
- Tests in `tests/test_build_lci.py`: an internal process with an unmapped feed and emission
  builds strictly with both gaps unlinked in every format; the same process marked public fails
  (also with `--public`); a per-process override applies; a duplicate override and schema
  violations are errors with the file; every process's file is valid.
- The move: commit "Move the per-process exchange overrides out of lci/mappings.yaml". A build
  before and after gives a byte-identical workbook, JSON-LD and multifunctional file.
- The batch that motivated it: #189-#192, #194-#196 and #198.
