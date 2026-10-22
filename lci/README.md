# Atlas LCI export for Brightway

The Process Atlas publishes its processes as one versioned **foreground database** for
[Brightway 2.5](https://docs.brightway.dev): a workbook in bw2io's Excel format that you import
into your own project and link to the background databases you are licensed for, in one call.

> **Bring your own ecoinvent.** The export contains only the Atlas's own foreground data.
> Background activities (electricity, steel, transport, ...) are referenced by name, reference
> product, unit and location; no ecoinvent data is shipped or needed to build it. You need your
> own licensed background database in the project you install into.

## Import

```python
import bw2data as bd
from cheme_as_code_lci import install       # pip install ./python (cheme-as-code-lci)

bd.projects.set_current("my-lca")           # a project that already holds ecoinvent + biosphere
report = install(
    "cheme-as-code-atlas-0.1.0.xlsx",       # or the downloaded folder with index.json
    background="ecoinvent-3.11-cutoff",     # your background database's name
    location="FR",                          # the plant site: grid electricity and other site inputs
)
print(report.summary())

goxp = bd.get_node(database="cheme-as-code-atlas-0.1.0", code="asu-1:asu-1-500-t-d-gox:product:GOXP")
```

`install(path_or_version, background="ecoinvent-3.11-cutoff", biosphere=None, location=None,
prefer_atlas=True, overwrite=False)`:

- runs `bw2io.ExcelImporter` and its standard strategies, then `match_database` against
  `background` (name, reference product, unit, location) and the biosphere (name, categories,
  unit); `biosphere` defaults to `biosphere3`, else the one `*biosphere` database in the project;
- `location` replaces the location of every input marked `atlas location rule: site`; without it
  the workbook's default (`DE`) is used and the report says so;
- `prefer_atlas=True` links an input that another Atlas process makes (e.g. hydrogen from an
  Atlas electrolyser) to that Atlas activity instead of the background;
- writes the database **only if every exchange is linked**; otherwise nothing is written and
  `report.unlinked` lists each exchange that found no partner (fix the name in your background
  or in `lci/mappings.yaml`). Nothing is dropped silently;
- refuses to replace an existing database of the same name unless `overwrite=True`.

Without the helper, plain bw2io works too (`bi.ExcelImporter(path)`, `apply_strategies()`,
`match_database(...)`), but then site locations, Atlas links and treatment signs (below) are yours
to handle.

## What is in the download

| file | |
|---|---|
| `lci/cheme-as-code-atlas-<version>.xlsx` | the database `cheme-as-code-atlas-<version>`: an `about` sheet (skipped by the importer), a `database` sheet, one sheet per process, a `proxies` sheet |
| `lci/datapackage.json` | version, library commit, per process: title, maturity, review, data status (exchanges by provenance), factor status of the study, allocation and shares, functional unit, activities |
| `lci/index.json` | what the Atlas site reads: file names, sizes, sha256, activities per process, caveats |

Activity codes are stable: `<process>:<dataset>:<product key>` (e.g.
`asu-1:asu-1-500-t-d-gox:product:GOXP`) and `proxy:<id>`.

## Modelling rules

Written into each activity's `comment` as well.

- **Source.** Core's unallocated LCI dataset of each process (`kind: lci_dataset`):
  `processes/<id>/lca/dataset.yaml` of a plantcode project (`cheme assess lca --write`), or
  hand-written `processes/<id>/lca/datasets/*.yaml` of a manifest-only process.
- **Co-products.** One single-output activity per co-product, per 1 unit (kg) of it, with the
  study's allocation (`lca/lca.yaml`), else the dataset's default, else mass. Proportional methods
  (mass, economic, energy, exergy, shares) only; substitution and `none` are refused. The
  unallocated multi-output form is not exported (bw2io's Excel importer has no clean
  representation of it).
- **Construction, maintenance, transport, end of life** are technosphere inputs per unit of
  product, already spread over the plant's life (hours x years) by core.
- **Amounts** are quantities of the linked activity's reference product, as in core's study. A
  link to a treatment activity (production -1, ecoinvent's convention for wastes) gets its sign
  flipped at install, so the result is the same.
- **Not exported:** free inputs (ambient air), outputs released to the environment (counted by
  their `emission:*` exchanges), and free pass-through emissions (below).
- **Uncertainty:** an exchange with a lognormal `gsd2` gets Brightway's lognormal (type 2,
  `scale = ln(gsd2)/2`); pedigree scores are not exported.

## Linking (`lci/mappings.yaml`)

Curated, library level, schema `schemas/lci-mappings.schema.json`. Per exchange: an override in
`exchanges:`, else the dataset exchange's own `link` (a Brightway activity, biosphere flow or
another Atlas dataset), else its chemical slug, else its `link.factor` id, in `technosphere:`.
Emissions by component in `biosphere:`. A missing mapping fails the build.

Decisions for ASU-1:

- **Electricity:** market for electricity, medium voltage, at the site's location.
- **Materials** as the dataset counts them: steel (low-alloyed, hot rolled), stainless (18/8),
  aluminium (primary ingot), concrete (m3), zeolite for the adsorbent, lubricating oil, lorry
  transport.
- **Screening proxies** where the dataset counts a flow in a unit ecoinvent has no activity for:
  cooling water as heat rejected (0.01 kWh electricity per kWh), pipe per m (20 kg steel), fittings
  per piece (15 kg steel), grating per m2 (30 kg steel), insulation per m2 (2 kg aluminium
  cladding; insulant not yet counted), and the study's end-of-life recycling credits (-0.5 kg
  steel per kg steel scrap, -0.7 kg aluminium per kg aluminium scrap; not cut-off logic). The
  masses are assumptions chosen to be plausible and consistent with the example factors.
- **Atmospheric pass-through** (N2, O2, Ar, H2O, and CO2 taken from the air and returned by the
  TSA): not exported, nor the air intake. Never as "Carbon dioxide, fossil" (that would add about
  2 kg CO2-eq/t GOX); writing both an "in air" resource and an emission is a net zero that LCIA
  methods do not all score as zero. Core's study treats them as free in the same way.

The background names follow ecoinvent 3.11 conventions but have **not** been checked against a
licensed copy here; `install()` reports any that do not link.

## Caveats

- ASU-1's characterisation factors (`lca/factors.yaml`, `example: true`) are placeholders: the
  plantcode results they give are not meaningful numbers. The LCI itself carries no factors.
- The datasets are screening level (concept-stage flows and duties, about +/-30 %); each process
  states its maturity and review status (`datapackage.json`, activity comments).
- The ASU dataset is from example-asu PR #11 (in review): numbers may still change.

## Build

```sh
uv run scripts/build_lci.py --library <process-library> --out <dir> --version 0.1.0 [--strict]
# -> <dir>/lci/cheme-as-code-atlas-0.1.0.xlsx, <dir>/lci/datapackage.json, <dir>/lci/index.json
```

`<dir>/lci/` is replaced; nothing else in `<dir>` is touched. Mappings come from
`<library>/lci/mappings.yaml`, else this staged copy. Two runs on the same input are
byte-identical (the workbook's document dates and zip entry dates are fixed).

## Verification

`tests/test_lci_brightway.py` (marker `brightway`) builds ASU-1's export, installs it with
`install()` into a temporary Brightway project (bw2io's packaged default biosphere3, no network)
against a **stub background** in which every mapped activity emits its example factor as fossil
CO2, and checks that an LCA of 1 t GOXP reproduces plantcode's baseline (`results.csv`) to the
precision plantcode prints. It also covers Atlas-internal linking, treatment signs, the overwrite
refusal and the unlinked report on the fixture library.

```sh
uv run --python 3.12 --with pytest --with pyyaml --with jsonschema --with openpyxl \
  --with ./python --with bw2calc pytest -m brightway tests
```
