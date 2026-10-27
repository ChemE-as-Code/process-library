# Adding a process

1. `cp -R templates/process processes/<id>`: `<id>` is a lowercase slug and never changes once
   listed (it is the Atlas URL).
2. Fill in `process.yaml`. Be honest about `maturity` (how far the design is taken) and
   `validation.status` (who has checked it): passing automated checks is not a review.
   Optional `facets` let the Atlas filter processes; list only what the design has:
   `feedstock_basis` (any of `fossil`, `biogenic`, `atmospheric`, `mineral`, `recycled`,
   `water`, `electricity`), `product_classes` (slugs, e.g. `industrial-gases`, `fuels`,
   `fertilizers`, `polymers`, `chemicals`, `materials`), `unit_operations` (slugs, e.g.
   `cryogenic-distillation`, `adsorption`, `compression`, `reaction`, `electrolysis`) and
   `region` (e.g. `generic`, `EU`). Reuse the slugs other processes already use.
3. Every chemical under `chemistry` must be a slug of `chemicals/chemicals.yaml`; add new ones in
   the same change, with CAS, InChIKey and ChEBI where they exist, and properties only with a
   source. A product in a defined state and purity (GOX at 30 barg, LOX) is a registry grade:
   name it as `chemical: oxygen/lox` (add the grade under the substance's `grades` if it is
   new). The graph joins by substance; the LCI export names the grade. Rules:
   [docs/registry.md](docs/registry.md). `families` take slugs of `taxonomy/families.yaml`
   (mapped to ISIC Rev.4); a new family goes there and into the `process.schema.json` enum
   together. Add the process to its entry in `coverage.yaml` (`covered_by`,
   [docs/coverage.md](docs/coverage.md)).
4. Optional, as the process matures:
   - a cheme-as-code engineering project in the same folder (`cheme init`, then P&IDs, process
     YAML, layout, LCA): the catalog derives its sheets, gates, design basis and LCA results;
   - an LCI dataset (`lca/dataset.yaml`, written by `cheme assess lca --write`, or hand-written
     `lca/datasets/*.yaml`), and if it needs new background links, entries in `lci/mappings.yaml`.
     A multi-output process needs an allocation that follows the hierarchy of
     [docs/system-model.md](docs/system-model.md) (often a curated `allocation:` entry in the
     mappings), and recycling or energy-recovery outputs a `cutoff_exclusions:` decision.
   - a market for each product other processes consume: add the process as a supplier of the
     product's market in `markets/<substance>.yaml` (or a new market), with its production
     volume and the transport and losses to the consumer, each with a source or marked ASSUMED
     ([docs/markets.md](docs/markets.md)). An Atlas input whose grade has no market is linked at
     the plant gate, which is a build warning.
   - benchmarks for its LCI dataset: a public process needs at least two KPIs in
     `benchmarks/<family>.yaml`, each with a range from a cited open source or a recorded
     `no_open_reference` ([docs/benchmarks.md](docs/benchmarks.md)). Never invent a range.
5. Check: `uv run scripts/build_catalog.py --library . --out dist --strict` (and
   `scripts/build_lci.py ... --strict` with an LCI dataset). CI runs the same, and the public
   build (`--public`, below).

## Sources, licences and what may not be copied

The library is published: process data and designs under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (LICENSE-DATA), code under MIT
(LICENSE). Contribute only what may be published under these licences:

- **Never copy third-party content**: tables, figures, drawings, P&IDs, datasheet or manual
  text, screenshots or text from papers, books, standards, vendor documents or websites, and no
  values from licensed databases (ecoinvent factors or results, commercial property data).
- **Facts and numbers are fine in your own form, with their source** (`source:`/`provenance:`
  fields, `references:` in `process.yaml`, DESIGN.md); estimates are marked ASSUMED.
- **Draw and write everything yourself**: drawings are generated from the library's own files.
- **Openly licensed material** only with its licence and attribution in a `NOTICE.md` next to it,
  and only if that licence is compatible with CC BY 4.0 / MIT.

By contributing you agree that your contribution is published under these licences.

## Publishing a process

The Atlas has two builds. The preview build (the default) shows every process as the library
has it. The public build (`--public` of `build_catalog.py`, `build_lci.py` and
`export_snapshots.py`) is what may be published, and its data is public as a whole:

- Only processes with `publication.status: public` in `process.yaml` are in it; `internal`
  (the default) and `candidate` are left out entirely. Setting `public` is the maintainers'
  decision, made in its own change.
- `publication.license` names the license it is published under (an SPDX id, e.g.
  `CC-BY-4.0`). There is no default: state it when you set `public`.
- `repository` is shown only when its `access` is `public`.
- An LCA's footprint values (totals, contributions, the headline value, the viewer's LCA answer
  and `lca/results.*`, `lca/gaps.csv`, `lca/uncertainty.csv`, `lca/scenarios/*.json`) are shown only when core's
  committed run manifest (`lca/manifest.json`) says the result is publishable under its sources'
  terms and is current (`scripts/publication.py` `lca_withheld`); placeholder factors, a missing
  or stale manifest and restricted or local sources withhold them. Its goal, functional unit,
  boundary, inventory, class and data sources (with their attribution) stay.
- The viewer snapshot is exported without these paths, which always apply in public builds:
  `.claude/**`, `AGENTS.md`, `CLAUDE.md`, `reviews/**`, `PROGRESS.md`, `scripts/agent-run/**`,
  `**/.gitattributes` (kept in `scripts/publication.py`; change both together), and
  `process.yaml` itself (the catalog publishes what of it may be public). Add your own
  under `publication.exclude` (globs relative to the process folder: `**` spans directories,
  `*` stays in one, a plain name is the file at the folder root), for example `DESIGN.md` or
  `docs/private/**`. Everything else in the folder, including `README.md` and `DESIGN.md`, is
  published as text: write it for the public or exclude it.

```yaml
publication: {status: public, license: CC-BY-4.0, exclude: ["docs/private/**"]}
```

Do not rewrite another process's engineering files; change them through that process's own
review (its `DESIGN.md`, `reviews/`).

## Changing the library

A change to the library structure, a schema, the LCI pipeline or the publication rules comes
with an Architecture Decision Record in the same pull request: a new or superseding record in
[`docs/adr/`](docs/adr/README.md). A process's engineering decisions stay in its `DESIGN.md`.

## Issues

Open points of a process are tracked as issues in the vocabulary of a design office's action
register, so an engineer reads them as they would a project's open items list. Core's
`docs/framework/issues.md` defines the labels; `cheme issues` lists a plant's items and the
`kind: issues` gates in `checks/checks.yaml` hold a stage sign-off while items before that gate
are open.

- **Forms (the type, `type:`):**

  | Form | Label | Use for |
  | --- | --- | --- |
  | Action item | `type:action` | a task from a review, HAZOP or meeting, owned and closed out |
  | Engineering hold | `type:hold` | design that cannot be fixed until an input arrives (vendor data, a client decision, a study) |
  | Technical query (TQ) | `type:tq` | a question to the client, a vendor or another discipline that needs an answer |
  | Design change | `type:change` | a change to frozen design, with its reason and the documents it touches |
  | Library work item | `scope:library` | schemas, catalog builder, LCI database, Atlas data |

- **Fields set labels** (workflow `issue-labels`): Process → `process:<id>`, Discipline →
  `discipline:` (process, control, piping, mechanical, electrical, layout, safety, civil), Close
  before gate → `gate:` (concept, basic, detail), Source → `source:` (design-review, hazop,
  layout-review, control-review, vendor, client, internal). It acts for members and
  collaborators only, since these labels hold stage gates: an outside issue is triaged and
  labelled by hand. Values outside the vocabulary are ignored, and an edit replaces the labels
  of these fields. A new engineering hold gets `waiting:input`. When you add a process folder,
  add its id to every form's Process dropdown; the workflow creates its label.
- **Status:** an open item without a status label is open; `status:in-progress` while someone
  works it; `status:for-verification` once the close-out evidence is in, for a second person to
  check. Only the checker closes it. What an open item waits for: `waiting:input` (vendor,
  client, HAZOP / LOPA session) or `waiting:work` (another issue or branch).
- **Gates:** an item closes before its gate. An item of an earlier gate that is still open also
  holds every later gate.
- **Filter** by process with `label:process:asu-1`, and combine with `label:gate:basic`,
  `label:type:hold` and so on. The Process Atlas shows each process's open items by gate
  (`scripts/fetch_issues.py` before `build_catalog.py --issues`); the public build of a private
  repository shows titles and status only, without links.
- An open point recorded in a process's files (`unresolved:` in `control/*.yaml`, Open in a
  DESIGN.md decision) names its issue, and the issue names the files. Close the issue only once
  the files no longer carry the point.

## Planning and developing processes

Use the Process development form for a canonical chemical/process issue and the Process development
tracker form for batches. See [the tracking guide](docs/process-development.md) and
[tracker #114](https://github.com/ChemE-as-Code/process-library/issues/114) for issue links,
reference records, labels and GitHub Project setup. Workflow status, entry tier, calculation
maturity, independent review and publication approval are separate. The existing engineering
forms and gate-label workflow remain in use for engineering action items.
