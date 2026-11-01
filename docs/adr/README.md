# Architecture decision records

These records explain **why the process library is built the way it is**. An Architecture
Decision Record (ADR) records one decision about the library's **structure, file formats and
schemas, and build pipelines** (the Atlas catalog, the LCI database, publication and releases):
its context, the decision, and its consequences, including the negative ones.

They are not the place for engineering decisions about a plant. **Each process's engineering
decisions live in its own `DESIGN.md`** (`processes/<id>/DESIGN.md`, numbered D-NNN), next to
the files they govern. An ADR may cite a D-NNN; it does not repeat it. Decisions about
ChemE-as-Code core (the `cheme` tool, its dataset contracts) are recorded in core's own
`docs/adr`.

## Status

- **Proposed**: drafted and applied where noted, but awaiting the owner's (or an expert's)
  decision. The library's methodology and governance documents that are drafts are Proposed.
- **Accepted**: in force.
- **Superseded by NNNN** / **Deprecated**: kept for the record; never deleted.

ADRs 0002 to 0014 were written **retroactively** on 2026-10-25 from the repository history.
Their Status date is the date the decision reached `main` (the merge of its pull request), and
each cites the commits and pull requests that introduced it in its Evidence section.

## Adding an ADR

A change to the library structure, a schema, the LCI pipeline or the publication rules comes
with an ADR in the same pull request.

1. Copy [template.md](template.md) to `NNNN-kebab-title.md` with the next free number.
2. Fill in Status (normally Proposed until the pull request is merged), Context, Decision,
   Consequences and Evidence. Name the files that hold or enforce the rule.
3. Add it to the index below and to the `nav` of `mkdocs.yml` (the docs build is strict and
   warns about pages missing from the nav).
4. To reverse a decision, write a new ADR that supersedes it and set the old one's Status to
   "Superseded by NNNN". Do not rewrite an accepted ADR's decision.

## Index

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted, 2026-10-25 |
| [0002](0002-one-folder-per-process-single-source.md) | One folder per process; the library is the single source of the Atlas and its LCI database | Accepted, 2026-10-23 |
| [0003](0003-move-example-asu-into-processes-asu-1.md) | Turn example-asu into the library by moving the ASU to processes/asu-1 with its history | Accepted, 2026-10-23 |
| [0004](0004-process-manifest-and-entry-kinds.md) | process.yaml: an Atlas manifest with honest maturity, review and publication status | Accepted, 2026-10-23 |
| [0005](0005-chemicals-registry-and-family-taxonomy.md) | Chemicals registry with slugs and grades; family taxonomy mapped to ISIC/NACE | Accepted, 2026-10-25 |
| [0006](0006-unallocated-datasets-allocated-at-build.md) | LCI data enters as unallocated datasets; the build allocates per co-product | Accepted, 2026-10-23 |
| [0007](0007-cut-off-system-model-and-allocation-hierarchy.md) | Attributional cut-off system model, substitution as a separate database, allocation hierarchy | **Proposed**, 2026-10-25 |
| [0008](0008-brightway-workbook-linked-by-name.md) | Brightway Excel workbook and installer, background linked by name, no licensed data | Accepted, 2026-10-23 |
| [0009](0009-ci-validates-every-plant-and-the-library.md) | CI validates every engineering project with cheme and builds the library | Accepted, 2026-10-23 |
| [0010](0010-public-and-preview-builds-fail-closed.md) | Preview and public builds; the public build fails closed | Accepted, 2026-10-23 |
| [0011](0011-benchmark-registry-with-cited-ranges.md) | Benchmark registry of KPIs with cited open reference ranges | Accepted, 2026-10-25 |
| [0012](0012-versioning-releases-and-dois.md) | Semantic versions; releases drafted by CI, decided by the owner | **Proposed**, 2026-10-25 |
| [0013](0013-licences-and-no-third-party-content.md) | MIT for code, CC BY 4.0 for data; never copy third-party content | Accepted, 2026-10-23 |
| [0014](0014-coverage-roadmap-as-a-plan.md) | Ranked coverage roadmap with planned tiers, a plan not a commitment | Accepted as a working plan, 2026-10-25 |
| [0015](0015-datapackage-documents-every-activity.md) | datapackage.json documents every exported activity; the Atlas renders it without LCI logic | **Proposed**, 2026-10-26 |
| [0016](0016-scenario-comparability-in-the-catalog.md) | Carry core's scenario comparability verdict and factor scope into the catalog | **Proposed**, 2026-10-26 |
| [0017](0017-recorded-check-of-background-mappings.md) | Verify background mappings by a recorded check against a licensed copy | **Proposed**, 2026-10-27 |
| [0018](0018-stored-benchmark-report-per-build.md) | Store each build's benchmark comparison as benchmarks.json | Accepted, 2026-10-28 |
| [0019](0019-process-development-tracking.md) | Process issues and Project workflow separate from evidence and maturity | **Proposed**, 2026-10-27 |
| [0020](0020-run-records-per-process.md) | Record each design run with its process, organised by run, kept out of publication | **Proposed**, 2026-10-27 |
| [0021](0021-design-maturity-calculation-maturity-review-status.md) | Name the three axes design maturity, calculation maturity and review status; labels only | **Proposed**, 2026-10-27 |
| [0022](0022-lci-gaps-for-unpublished-processes-and-per-process-mappings.md) | Report LCI mapping gaps of unpublished processes; keep a process's overrides with it | Accepted, 2026-10-28 |
| [0023](0023-reactions-in-the-catalog.md) | List the processes' reactions in the catalog as reactions.json, each reaction once | **Proposed**, 2026-10-30 |
| [0026](0026-no-total-when-every-contribution-is-a-gap.md) | Give no total, with the reason, when every contribution to a category is a gap | **Proposed**, 2026-10-30 |
