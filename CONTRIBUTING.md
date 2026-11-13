# Contributing to the process library

Thank you for helping build an open library of chemical processes. This guide covers:

- [Adding a process](#adding-a-process)
- [Sources, licences and what may not be copied](#sources-licences-and-what-may-not-be-copied)
- [Publishing a process](#publishing-a-process)
- [Changing the library](#changing-the-library)
- [Issues](#issues)
- [Planning and developing processes](#planning-and-developing-processes)

The terms (design maturity, calculation maturity, review status, …) follow core's
[glossary](https://github.com/ChemE-as-Code/core/blob/main/docs/concepts/glossary.md).

---

## Contribution terms

By submitting a contribution to this repository, you agree to make it available under the public license applicable to that part of the repository. You also grant a non-exclusive, worldwide, perpetual, irrevocable, royalty-free license to use, reproduce, modify, distribute, and sublicense your contribution under other terms. You retain ownership of your contribution.

## Adding a process

### 1. Create the folder

```sh
cp -R templates/process processes/<id>
```

`<id>` is a lowercase slug. It never changes once the process is listed, because it is the
process's URL in the Atlas.

### 2. Fill in `process.yaml`

Keep the template's `publication: {status: public, license: CC-BY-4.0}`: a new entry is public
([Publishing a process](#publishing-a-process)), so write its `README.md` and `DESIGN.md` for the
public.

Be honest about two fields:

- **`maturity`: the design maturity.** How far the design is taken. It is a claim, capped by
  evidence:
  - in an engineering project, by the **calculation maturity** that `cheme maturity` evaluates
    into `checks/maturity.json`;
  - beside a Tier 0/1 LCI dataset, at `concept`.
- **`validation.status`: the review status.** Who has checked it. Passing automated checks is
  not a review.

Optional **`facets`** let the Atlas filter processes. List only what the design has, and reuse
the slugs other processes already use:

| Facet | Values |
| --- | --- |
| `feedstock_basis` | any of `fossil`, `biogenic`, `atmospheric`, `mineral`, `recycled`, `water`, `electricity` |
| `product_classes` | slugs, e.g. `industrial-gases`, `fuels`, `fertilizers`, `polymers`, `chemicals`, `materials` |
| `unit_operations` | slugs, e.g. `cryogenic-distillation`, `adsorption`, `compression`, `reaction`, `electrolysis` |
| `region` | e.g. `generic`, `EU` |

### 3. Chemicals, families and coverage

- **Chemicals.** Every chemical under `chemistry` must be a slug of `chemicals/chemicals.yaml`.
  Add new ones in the same change, with CAS, InChIKey and ChEBI where they exist, and properties
  only with a source.
- **Grades.** A product in a defined state and purity (GOX at 30 barg, LOX) is a registry grade:
  name it as `chemical: oxygen/lox`, and add the grade under the substance's `grades` if it is
  new. The graph joins by substance; the LCI export names the grade. Rules:
  [docs/registry.md](docs/registry.md).
- **Families.** `families` take slugs of `taxonomy/families.yaml` (mapped to ISIC Rev.4). A new
  family goes there and into the `process.schema.json` enum together.
- **Coverage.** Add the process to its entry in `coverage.yaml` (`covered_by`,
  [docs/coverage.md](docs/coverage.md)).

### 4. Optional, as the process matures

#### An engineering project in the same folder

Start one with `cheme init`, then add P&IDs, the process YAML, the layout and the LCA. The
catalog derives its sheets, gates, design basis and LCA results.

#### A batch process

A batch or semi-batch process folder describes one dedicated train (campaigns on a
multipurpose plant are out of scope; [ADR 0035](docs/adr/0035-batch-processes-on-a-dedicated-train.md)).
A Tier 2 batch entry states its batch size and recipe in `process/recipe.yaml` (`cheme process
recipe`), and its flowsheet holds the recipe's year averages, with no `cheme.recipe-basis`
warning. A dosed exothermic step is `reactor: semibatch`, so that `cheme process
reactor-hazards` screens its accumulation. Cleaning, rinses and purges between its own batches
that the flowsheet does not carry are `lca/lca.yaml` consumables with `per_batch`; those it
carries are streams at their year-average rate (per-batch amount x batches / hours, the
arithmetic in the `source`). Changeovers between products are outside the boundary. Like every
entry, a batch entry is written public with CC-BY-4.0 in the change that adds it.

#### A balance script whose numbers go into the flowsheet

When core cannot calculate the flowsheet yet, a standalone script
(`processes/<id>/scripts/<name>.py`, run with `cheme run`) may supply its stream values and
duties; the flowsheet gives each as `provenance: assumed` with a `source` that starts with the
script's path (`"scripts/<name>.py: ..."`). Such a script follows the balance-output contract
([ADR 0027](docs/adr/0027-balance-scripts-reproduce-the-flowsheet.md)): when the environment
variable `BALANCE_OUTPUT` names a file, it writes there, as JSON, every value the flowsheet
cites from it (`{"contract": "balance-output/1", "script": "scripts/<name>.py", "cases":
{"design": {"<stream id>": {"flow": ..., "composition": {...}}}}}`), in the flowsheet's units
and basis. Copy `write_balance_output()` from a migrated script (e.g.
`processes/hydrogen-1/scripts/h2_balance.py`). CI re-runs it and compares:

```sh
uv run scripts/check_balance_scripts.py --library . --process <id>
```

When the script changes, update the flowsheet values it sources in the same commit; a drift
fails the `balance-scripts` job. A duty that `cheme process propagate --fill` writes for a
conversion step (`provenance: calculated`) stays out of the script's balance output (print it as
a cross-check instead): the checker reports it as `duplicate`, which fails the job too.

#### An LCI dataset, its mappings, gaps and allocation

- The dataset is `lca/dataset.yaml`, written by `cheme assess lca --write`, or hand-written
  `lca/datasets/*.yaml` (a manifest-only process). An engineering project with a second
  computed design (another flowsheet case) also commits that case's own dataset,
  `lca/datasets/<dataset id>-<case>.yaml`, written by `cheme assess lca --write --case <case>` and
  never edited; a `kind: command` gate `cheme assess lca --check --case <case>` keeps it current,
  and the build names its activities `<title>, case <case>`
  ([ADR 0034](docs/adr/0034-design-case-lci-datasets.md)).
- **Overrides for this process's exchanges** go in its own `lca/mappings.yaml`, not in the shared
  file: `use` an existing technosphere entry, a `chemical` slug, a `dataset` (an Atlas producer),
  `atlas: false`, a `properties_reason`.
- **Shared vocabulary** gets its own PR in `lci/mappings.yaml`: a new technosphere entry,
  biosphere identity, proxy or pass-through decision.
- **Gaps.** An exchange without a mapping is a gap, in a public process too: the strict build
  passes, lists it (`gap:` lines, `lci/gaps.json`), exports it unlinked and marks the process
  preliminary. Never map to a guess to close a gap: a correct gap is better than a doubtful link
  ([ADR 0026](docs/adr/0026-public-processes-may-be-preliminary.md),
  [lci/README.md](lci/README.md) "Linking").
- **Estimate proxies.** A feed no library entry makes but that has a sound estimate from other
  products (a stoichiometry, a mixture) may link a shared estimate proxy in `lci/mappings.yaml`:
  a `chemical`, a `basis` (mass, stoichiometric with its `reaction`, or non-mass with its
  reason) and inputs that are background entries or library products (`dataset: {path,
  product}`) with an amount per kg. The build checks the mass and a mixture's content against
  its library product's stated composition (a content on a background entry is refused),
  refuses a missing product and a circular link, always prefers a library producer once one
  exists, and marks every linked exchange as an estimate with a pedigree and DQR penalty; the
  catalog keeps such a process preliminary and `estimated`. Record the proxy and what it leaves
  out in the consumer's `DESIGN.md`; when a part fits nothing, keep the gap
  ([ADR 0039](docs/adr/0039-estimate-proxies-may-name-library-products.md)).
- **No total from gaps alone.** A category whose every contribution in `lca/gaps.csv` is a gap
  (a background not linked yet; flows outside the method do not count) has no footprint: the
  catalog leaves it out of `lca.totals`, lists it in `lca.no_total` and gives the headline and
  route footprint `value: null`, `not_computed: true` and
  `not_computed_reason: every-contribution-a-gap`, never 0. A category without such gaps keeps
  its total, also 0, but a baseline 0 with nothing contributing is still no footprint
  ([ADR 0029](docs/adr/0029-no-total-when-every-contribution-is-a-gap.md), on
  [ADR 0026](docs/adr/0026-public-processes-may-be-preliminary.md)).
- **Several outputs.** A multi-output process needs an allocation that follows the hierarchy of
  [docs/system-model.md](docs/system-model.md), often a curated `allocation:` entry in the
  mappings. Recycling or energy-recovery outputs need a `cutoff_exclusions:` decision.

#### Markets for the products other processes consume

Add the process as a supplier of the product's market in `markets/<substance>.yaml` (or a new
market), with its production volume and the transport and losses to the consumer, each with a
source or marked ASSUMED ([docs/markets.md](docs/markets.md)). An Atlas input whose grade has no
market is linked at the plant gate, which is a build warning.

#### Benchmarks for its LCI dataset

A public process needs at least two KPIs in `benchmarks/<family>.yaml`, each with a range from a
cited open source or a recorded `no_open_reference` ([docs/benchmarks.md](docs/benchmarks.md)).
Never invent a range.

### 5. Check

```sh
uv run scripts/build_catalog.py --library . --out dist --strict
uv run scripts/build_lci.py ... --strict   # with an LCI dataset
```

CI runs the same, and the public build (`--public`, see [Publishing a process](#publishing-a-process)).

CI installs core and pyDEXPI anonymously (both are public), so a pull request from a fork runs
every job too. Run the commands above yourself as well and say so in the pull request.

---

## Sources, licences and what may not be copied

The library is published: process data and designs under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (`LICENSE-DATA`); code, skills and scripts, including those inside process folders, under
AGPL-3.0-or-later (`LICENSE`); the LCI data installer in `python/` under MIT (`python/LICENSE`).
Contribute only what may be published under these licences.

| | |
| --- | --- |
| ❌ **Never copy third-party content** | Tables, figures, drawings, P&IDs, datasheet or manual text, screenshots or text from papers, books, standards, vendor documents or websites. No values from licensed databases (ecoinvent factors or results, commercial property data). |
| ✅ **Facts and numbers in your own form, with their source** | `source:` / `provenance:` fields, `references:` in `process.yaml`, `DESIGN.md`. Estimates are marked ASSUMED. A value an open-source package computes from its bundled coefficients or tables (thermo's DIPPR_PERRY_8E, the CRC tables of `chemicals`) is such a fact, even where the coefficients go back to DIPPR 801: name the package, its version, the method and the underlying work, do not call it open data, and copy no table or coefficient set ([ADR 0037](docs/adr/0037-package-property-values-are-single-facts.md)). |
| ✅ **Draw and write everything yourself** | Drawings are generated from the library's own files. |
| ⚠️ **Openly licensed material** | Only with its licence and attribution in a `NOTICE.md` next to it, and only if that licence is compatible with the licence of the place it goes (see above). |

By contributing you agree that your contribution is published under these licences.

---

## Publishing a process

The Atlas has two builds:

- **Preview build** (the default): every process as the library has it.
- **Public build** (`--public` of `build_catalog.py`, `build_lci.py` and `export_snapshots.py`):
  what may be published. Its data is public as a whole.

What the public build contains:

- **Every entry is public, and a new one is written public.** Write
  `publication: {status: public, license: CC-BY-4.0}` in a new `process.yaml` (the template has
  it); the pull request that adds the entry publishes it, with no separate maintainer change
  ([ADR 0036](docs/adr/0036-public-is-the-default-publication-status.md)).
- **Only public processes, and the build fails closed.** Only processes with
  `publication.status: public` and a `publication.license` in `process.yaml` are in the public
  build; `internal`, `candidate`, a missing status and a public status without a licence are left
  out entirely, so a forgotten field never publishes
  ([ADR 0010](docs/adr/0010-public-and-preview-builds-fail-closed.md)). Use `internal` only for an
  entry that must not be published (data whose licence does not allow it, an unfinished private
  study), and state its own reason in its `process.yaml`, in a comment beside the status (the
  template's generic comment is not a reason).
- **A stated licence.** `publication.license` names the licence it is published under (an SPDX
  id). For data and designs it is `CC-BY-4.0`, the library's licence (`LICENSE-DATA`), still
  written explicitly and has no default: the schema requires it on a public entry, the public
  build leaves a public entry without one out, and the library tests fail on it.
- **The repository** is shown only when its `access` is `public`.
- **LCA results only when publishable.** An LCA's footprint values are shown only when core's
  committed run manifest (`lca/manifest.json`) says the result is publishable under its sources'
  terms and is current (`scripts/publication.py` `lca_withheld`). Placeholder factors, a missing
  or stale manifest and restricted or local sources withhold them. The values are the totals,
  contributions, PCF breakdown and headline value, the viewer's LCA answer, and `lca/results.*`,
  `lca/gaps.csv`, `lca/uncertainty.csv` and `lca/scenarios/*.json`. Its goal, functional unit,
  boundary, inventory, class and data sources (with their attribution) stay.
- **The viewer snapshot leaves out internal files.** These paths are always excluded in public
  builds (kept in `scripts/publication.py`; change both together):
  - `.claude/**`, `AGENTS.md`, `CLAUDE.md`
  - `reviews/**`, `runs/**`, `PROGRESS.md`, `scripts/agent-run/**`
  - `**/.gitattributes`
  - `process.yaml` itself (the catalog publishes what of it may be public)

  Add your own under `publication.exclude`: globs relative to the process folder, where `**`
  spans directories, `*` stays in one, and a plain name is the file at the folder root (for
  example `DESIGN.md` or `docs/private/**`).

> **Important:** everything else in the folder, including `README.md` and `DESIGN.md`, is
> published as text from the entry's first pull request: write it for the public, or exclude it.
> The rules on [sources and licences](#sources-licences-and-what-may-not-be-copied) apply in
> full.

```yaml
publication: {status: public, license: CC-BY-4.0, exclude: ["docs/private/**"]}
```

Do not rewrite another process's engineering files; change them through that process's own
review (its `DESIGN.md`, `reviews/`).

---

## Changing the library

A change to the library structure, a schema, the LCI pipeline or the publication rules comes
with an Architecture Decision Record in the same pull request: a new or superseding record in
[`docs/adr/`](docs/adr/README.md). A process's engineering decisions stay in its `DESIGN.md`.

---

## Issues

Open points of a process are tracked as issues in the vocabulary of a design office's action
register, so an engineer reads them as they would a project's open items list.

- Core's `docs/framework/issues.md` defines the labels.
- `cheme issues` lists a plant's items.
- The `kind: issues` gates in `checks/checks.yaml` hold a stage sign-off while items before that
  gate are open.

### Forms

| Form | Label (`type:`) | Use for |
| --- | --- | --- |
| Action item | `type:action` | a task from a review, HAZOP or meeting, owned and closed out |
| Engineering hold | `type:hold` | design that cannot be fixed until an input arrives (vendor data, a client decision, a study) |
| Technical query (TQ) | `type:tq` | a question to the client, a vendor or another discipline that needs an answer |
| Design change | `type:change` | a change to frozen design, with its reason and the documents it touches |
| Library work item | `scope:library` | schemas, catalog builder, LCI database, Atlas data |

### Fields set labels

The `issue-labels` workflow turns the form fields into labels:

| Field | Label | Values |
| --- | --- | --- |
| Process | `process:<id>` | the process ids |
| Discipline | `discipline:` | process, control, piping, mechanical, electrical, layout, safety, civil |
| Close before gate | `gate:` | concept, basic, detail |
| Source | `source:` | design-review, hazop, layout-review, control-review, vendor, client, internal |

- The workflow acts for members and collaborators only, since these labels hold stage gates. An
  outside issue is triaged and labelled by hand.
- Values outside the vocabulary are ignored, and an edit replaces the labels of these fields.
- A new engineering hold gets `waiting:input`.
- When you add a process folder, add its id to every form's Process dropdown; the workflow
  creates its label.

### Status

| Label | Meaning |
| --- | --- |
| *(none)* | open |
| `status:in-progress` | someone works it |
| `status:for-verification` | the close-out evidence is in, for a second person to check. Only the checker closes it. |
| `waiting:input` | waits for a vendor, the client, a HAZOP / LOPA session |
| `waiting:work` | waits for another issue or branch |

### Gates and filters

- **Gates.** An item closes before its gate. An item of an earlier gate that is still open also
  holds every later gate.
- **Filter** by process with `label:process:asu-1`, and combine with `label:gate:basic`,
  `label:type:hold` and so on.
- **In the Atlas.** The Process Atlas shows each process's open items by gate
  (`scripts/fetch_issues.py` before `build_catalog.py --issues`). The public build of a private
  repository shows titles and status only, without links.
- **Files and issues point at each other.** An open point recorded in a process's files
  (`unresolved:` in `control/*.yaml`, Open in a `DESIGN.md` decision) names its issue, and the
  issue names the files. Close the issue only once the files no longer carry the point.

---

## Planning and developing processes

- Use the **Process development** form for a canonical chemical or process issue, and the
  **Process development tracker** form for batches.
- See [the tracking guide](docs/process-development.md) and
  [tracker #306](https://github.com/ChemE-as-Code/process-library/issues/306) for issue links,
  reference records, labels and GitHub Project setup.
- Workflow status, entry tier, calculation maturity, design maturity, review status and
  publication status are separate; a new entry is public by default
  ([ADR 0036](docs/adr/0036-public-is-the-default-publication-status.md)).
- The existing engineering forms and gate-label workflow remain in use for engineering action
  items.
