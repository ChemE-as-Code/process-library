# 0004. process.yaml: an Atlas manifest with honest maturity, review and publication status

- **Status:** Accepted, 2026-10-23
- **Scope:** `schemas/process.schema.json`, `templates/process/`, `scripts/build_catalog.py`

## Context

The Atlas must list, find and link every process, but processes come in very different depths:
a full ChemE-as-Code engineering project (the ASU: P&IDs, PFD, layout, LCA) or only a sourced
inventory without any engineering files. The engineering project already has `plant.yaml` as its
manifest, and the catalog can derive sheets, gates, design basis and LCA results from it.
Readers of the Atlas must not mistake a screening design or a design that passed automated
checks for a reviewed one.

## Decision

- Every process folder has a `process.yaml` (`schema: cheme-as-code/process/v1`) holding only
  what cannot be derived: `id`, `title`, `summary`, `families`, `chemistry` (inputs, outputs,
  utilities by registry slug), `maturity`, `validation`, and optional `facets`, `basis`,
  `references`, `maintainers`, `repository`, `publication`, `lca`.
- Two kinds of entry share this manifest:
  - **engineering project:** the folder also holds a cheme-as-code project (`plant.yaml`); the
    catalog records `engineering_project: true` and derives the rest;
  - **manifest-only:** `process.yaml` alone, optionally with hand-written LCI datasets in
    `lca/datasets/*.yaml`.
- Three separate status axes, never folded into one:
  - `maturity`: how far the design is taken (`concept`, `screening`, `basic-engineering`,
    `detail-engineering`, `operating-reference`);
  - `validation.status`: who has checked it (`unreviewed`, `internally-reviewed`,
    `peer-reviewed`, `industry-validated`). Passing automated checks is not a review;
  - `publication.status`: whether it may be published (`internal` by default, `candidate`,
    `public`), see [0010](0010-public-and-preview-builds-fail-closed.md).
- The manifest has no version of its own; versions belong to LCI datasets and releases
  ([0012](0012-versioning-releases-and-dois.md)).

## Consequences

- A new process costs one YAML file; depth can grow later in the same folder without moving it.
- Maturity and review are self-declared in the manifest. The schema cannot verify them; the ASU's
  maturity is backed by `cheme maturity` and recorded reviews, but a manifest-only entry relies on
  its author's honesty (CONTRIBUTING.md asks for it).
- The planned entry tiers (0 stoichiometric, 1 sourced conceptual data, 2 flowsheet design) are
  recorded per coverage entry (`coverage.yaml` `tier`, [0014](0014-coverage-roadmap-as-a-plan.md)),
  not as a field of `process.yaml` yet; tiers 0 and 1 have no example process today.

## Evidence

- `986803b` (schema, template, ASU manifest), [#15](https://github.com/ChemE-as-Code/process-library/pull/15).
- `28bb7b9` `publication` block, [#20](https://github.com/ChemE-as-Code/process-library/pull/20);
  `1f661b6` facets, [#28](https://github.com/ChemE-as-Code/process-library/pull/28).
- `schemas/process.schema.json`, `templates/process/process.yaml`, docs/manifest.md,
  lci/README.md ("manifest-only process"), `build_catalog.py` (`engineering_project`).
