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
prefer_atlas=True, overwrite=False, expect=None)`:

- runs `bw2io.ExcelImporter` and its standard strategies, then `match_database` against
  `background` (name, reference product, unit, location) and the biosphere (name, categories,
  unit); `biosphere` defaults to `biosphere3`, else the one `*biosphere` database in the project;
- `location` replaces the location of every input marked `atlas location rule: site`; without it
  the workbook's default (`DE`) is used and the report says so;
- `prefer_atlas=True` links an input that another Atlas process makes (e.g. hydrogen from an
  Atlas electrolyser) to that Atlas activity instead of the background;
- links an elementary flow by its biosphere3 UUID (`atlas flow uuid`) when the biosphere
  database has a flow of that code and unit, else by name, categories and unit; writes the
  `atlas pedigree` scores as Brightway's `pedigree`;
- reports the database's **system model** and methodology version (`report.system_model`,
  `report.methodology_version`, in `summary()`), and lists deprecated activities with their
  successors (`report.superseded`);
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
| `lci/cheme-as-code-atlas-<version>.xlsx` | the database `cheme-as-code-atlas-<version>`: an `about` sheet (skipped by the importer), a `database` sheet, one sheet per process, a `proxies` sheet. Exchange columns beyond bw2io's: `atlas key`, `atlas flow uuid`, `atlas pedigree`, `atlas carrier` and the linking fields |
| `lci/datapackage.json` | version, library commit, per process: title, maturity, review, data status (exchanges by provenance), factor status of the study, allocation and shares, functional unit, activities (each with its `chemical` slug and registry `grade`, null when none), and per dataset its `property_checks` and `benchmarks` (below) |
| `lci/index.json` | what the Atlas site reads: file names, sizes, sha256, activities per process, caveats, system model |
| `lci/changes.json`, `lci/CHANGES.md` | with `--previous`: the change report against the earlier build (below) |

`datapackage.json` also records the **system model** (`system_model`: id, label, methodology
document and version, the exchanges excluded under cut-off with their decisions, allocation
findings) and, per dataset, its **version**, `methodology_version`, `content_sha256`, `review`
record (`unreviewed` by default), `valid_until`, and the allocation with the rule of the
hierarchy that justifies it. These come from the dataset itself when it states them (core's
dataset contract v2, below); otherwise the build's methodology version and `0.1.0`. A dataset
also carries its `system_model` (null when it states none), its `data_quality` rating from
`lca/manifest.json` (below), a `documentation` block (uuid, geography, time, technology,
classification, production volume, data generator, as the dataset gives them) and, when it is
deprecated, `deprecated: true` and `superseded_by`.

Activity codes are stable: `<process>:<dataset>:<product key>` (e.g.
`asu-1:asu-1-500-t-d-gox:product:GOXP`) and `proxy:<id>`.

## Modelling rules

The methodology is [docs/system-model.md](../docs/system-model.md) (methodology version in every
build); governance (versions, change reports, releases, review) is
[docs/governance.md](../docs/governance.md). Written into each activity's `comment` as well.

- **System model: attributional, cut-off** (`system_model: cutoff` in `lci/mappings.yaml`). The
  default build has no avoided-burden credits: an exchange that resolves to an id in
  `cutoff_exclusions:` (material recycling, energy recovery) is not exported, and its decision is
  written into the comment and `datapackage.json`; any negative technosphere amount fails the
  build; a proxy with a negative input outside `substitution:` fails to load.
- **Substitution variant.** `--system-model substitution` builds a separate database,
  `cheme-as-code-atlas-<version>-substitution`, that adds the credits of `substitution:`
  (technosphere entries and proxies). Never mix it with the cut-off database in one study.
- **Source.** Core's unallocated LCI dataset of each process (`kind: lci_dataset`):
  `processes/<id>/lca/dataset.yaml` of a plantcode project (`cheme assess lca --write`), or
  hand-written `processes/<id>/lca/datasets/*.yaml` of a manifest-only process. The builder
  reads `schema: cheme/lci_dataset/v2` (core#294) and the v1 files (`cheme/lca/v1`,
  `plantcode/lca/v1`); `cheme migrate --write` rewrites a hand-written v1 dataset to v2.
- **Co-products.** One single-output activity per co-product, per 1 unit (kg) of it, allocated
  by the hierarchy of docs/system-model.md: a curated rule in `lci/mappings.yaml` `allocation:`
  first; else the study's (`lca/lca.yaml`) or the dataset's method if it is the WBCSD
  price-ratio choice (economic above a ratio of 5 of the prices per kg, else mass); else the
  method of the study or dataset with its `allocation.deviation` (core allows the field in both;
  the study's first), as rule `deviation` and no finding; else the price-ratio choice, with a
  finding; else the given method, with a finding. A curated `rule: deviation` in the mappings
  still works and wins over the study's. Findings are
  warnings (`--strict` fails). Proportional methods (mass, economic, energy, exergy, shares)
  only; substitution and `none` are refused. The unallocated multi-output form is not exported
  (bw2io's Excel importer has no clean representation of it).
- **Construction, maintenance, transport, end of life** are technosphere inputs per unit of
  product, already spread over the plant's life (hours x years) by core.
- **Amounts** are quantities of the linked activity's reference product, as in core's study. A
  link to a treatment activity (production -1, ecoinvent's convention for wastes) gets its sign
  flipped at install, so the result is the same.
- **Not exported:** free inputs (ambient air), outputs released to the environment (counted by
  their `emission:*` exchanges), and free pass-through emissions (below).
- **Uncertainty and pedigree:** an exchange with a lognormal `gsd2` gets Brightway's lognormal
  (type 2, `scale = ln(gsd2)/2`). An exchange without its own distribution gets the lognormal of
  its pedigree on its `basic_uncertainty` (required: the build refuses a pedigree without one; core fills it from its table by exchange type), `gsd2 = exp(sqrt(ln(basic)^2 +
  sum(ln(U_i)^2)))` with the empirically based factors of Ciroth et al. (2016), as core
  computes it. Normal, triangular and uniform distributions are not exported (a warning names
  the exchange; Brightway sees it as deterministic). The five scores are written in the `atlas pedigree` column (`r,c,t,g,f`);
  `install()` turns them into Brightway's `pedigree` field. The study's default distributions
  (`lca/lca.yaml` `uncertainty.defaults`) are not known to the dataset and are not applied, so
  a Monte Carlo in Brightway can differ from core's where a study default wins there.
- **Units.** Quantities are brought to one unit per kind before allocation: g and t to kg, MWh to
  kWh, GJ to MJ, km to m, L to m3; m2*a (land occupation) becomes `square meter-year` and kBq
  `kilo Becquerel`, biosphere3's units. Gas volumes at a reference state keep their unit
  (`Nm3` is bw2io's `normal cubic meter`, `Sm3` its `standard cubic meter`; biosphere3 counts
  `Gas, natural` in Sm3), without conversion between the two. Item-time (`ea*h`, `ea*a`) has no
  Brightway unit: the build refuses it with the reason (state the amount as items). An amount is never converted to a unit the linked
  activity does not count in: a mapping in kWh refuses an exchange in MJ.
- **Carriers and product state.** A `carrier` (kind, temperature, pressure, level, LHV) is
  written in the exchange's `atlas carrier` column and a product's `state` (phase, pressure,
  purity, grade) in the activity's `atlas product state` and its comment, and in
  `datapackage.json` activities. They document the exchange; the background link is still chosen
  by the mapping (a steam or heat carrier does not yet pick a different activity).
- **Reference product.** A product whose flow has a grade in the chemicals registry
  (`chemical: <slug>/<grade>` in `process.yaml`, or the registry's `flow_grades`) is named after
  the grade: ASU-1's `Oxygen, GOX to pipeline` is now `Oxygen, gaseous, >= 99.5 mol%, 30 barg`.
  Without a grade it is the substance's name with the exchange title, as before. Activity codes do
  not change, so match on the code, not on the name. An input whose grade another Atlas process
  makes prefers that producer.
- **Property checks.** Each product's study `exergy` and `energy` (per kg) are compared with its
  grade's (else its substance's) registry `exergy` and `lhv`. `datapackage.json` records each as
  `match`, `mismatch`, `overridden` (a `properties_reason` in `lci/mappings.yaml`) or
  `unchecked` (no registry value, or a product not counted in kg). A mismatch over 2 % is a
  warning, so it fails `--strict` ([registry rules](https://github.com/ChemE-as-Code/process-library/blob/main/docs/registry.md), "Study properties against the registry").
- **Benchmarks.** Each dataset's KPIs of the benchmark registry (`benchmarks/<family>.yaml`,
  e.g. ASU-1's specific power per t GOX) are recorded in `datapackage.json` with their value,
  allocated value, status (`inside`, `outside`, `explained`, `no-reference`, `unchecked`) and
  reference. A value outside its range without an `out_of_range_reason`, and a public process
  with fewer than two KPIs, are warnings, so they fail `--strict` ([benchmarks](https://github.com/ChemE-as-Code/process-library/blob/main/docs/benchmarks.md)).

## Linking (`lci/mappings.yaml`)

Curated, library level, schema `schemas/lci-mappings.schema.json`. Per exchange: an override in
`exchanges:`, else the dataset exchange's own `link` (a Brightway activity, biosphere flow or
another Atlas dataset), else its chemical slug, else its `link.factor` id, in `technosphere:`.
A missing mapping fails the build.

Emissions and resources (the `resource` exchange type of the v2 contract: water, CO2 in air,
land) are biosphere exchanges, identified by the **biosphere3 UUID** of the dataset exchange's
`flow:` identity, which core writes from its curated crosswalk
(`data/elementary-flows.yaml`, UUIDs read from ecoinvent's published elementary-exchange list as
shipped with bw2io, BSD-3-Clause). The identity's name, categories and unit are exported and
its `per_unit` converts the amount (water is derived in kg and exported in m3, 0.001 m3/kg). The
UUID goes in the `atlas flow uuid` column. `biosphere:` of the mappings is keyed by flow
identity too: an entry keyed by a UUID corrects the name and categories the dataset gives; an
entry keyed by component (`CO2/biogenic`, `CH4/fossil`, ...) serves a dataset without identities
(v1, hand-written), and its optional `flow.uuid` is exported the same way. `install()` links an
elementary flow by its code in the biosphere database first (when the unit agrees) and falls back
to name, categories and unit; the report counts both. EF 3.1 identities are not used here: core
records none yet (`uuid: null`).

Decisions for ASU-1:

- **Electricity:** market for electricity, high voltage, at the site's location: ASU-1 takes
  its power at 33 kV (D-036), which ecoinvent counts as high voltage (above 24 kV). Medium voltage
  stays the library default for a process that does not state its supply voltage.
- **Materials** as the dataset counts them: steel (low-alloyed, hot rolled), stainless (18/8),
  aluminium (primary ingot), concrete (m3), zeolite for the adsorbent, lubricating oil, lorry
  transport.
- **Screening proxies** where the dataset counts a flow in a unit ecoinvent has no activity for:
  cooling water as heat rejected (0.01 kWh electricity per kWh), pipe per m (20 kg steel), fittings
  per piece (15 kg steel), grating per m2 (30 kg steel), insulation per m2 (2 kg aluminium
  cladding; insulant not yet counted). The masses are assumptions chosen to be plausible and
  consistent with the example factors.
- **Allocation: exergy** (`allocation.asu-1`, rule `physical-exergy`): one separation, products
  in different thermodynamic states; the same method as the study (D-056).
- **End-of-life recycling: excluded under cut-off** (`cutoff_exclusions`): the steel and
  aluminium scrap leave burden-free, with no credit. The study's credits (-0.5 kg steel per kg
  steel scrap, -0.7 kg aluminium per kg aluminium scrap, ASSUMED) are proxies of the
  substitution variant only. `processes/asu-1/` is unchanged: its study keeps the credits for
  its own question.
- **Atmospheric pass-through** (N2, O2, Ar, H2O, and CO2 taken from the air and returned by the
  TSA): not exported, nor the air intake. Never as "Carbon dioxide, fossil" (that would add about
  2 kg CO2-eq/t GOX); writing both an "in air" resource and an emission is a net zero that LCIA
  methods do not all score as zero. Core's study treats them as free in the same way.

The background names follow ecoinvent 3.11 conventions but have **not** been checked against a
licensed copy here; `install()` reports any that do not link.

## Governance fields and deprecated datasets

A dataset's own `version`, `methodology_version`, `review`, `valid_until` and `system_model`
(core#179) are read when present. A dataset that states a system model must fit the build: the
cut-off build takes `cutoff`; the substitution variant takes `cutoff` or `substitution`; `apos`
and `consequential` datasets are refused rather than mixed into one database.

`superseded_by: {id, version}` marks a dataset as deprecated. It stays in the database, so links
to it still resolve, with a pointer to its successor:

- `datapackage.json`: the dataset has `deprecated: true` and `superseded_by` (id, version,
  process, the successor's activity codes, `resolved`); its activities list `superseded_by`;
- the workbook: the activity is named `<title> [superseded by <id> <version>]` (two activities
  must differ in name, reference product, location or unit), has the `atlas superseded by`
  metadata (the successor's activity code for the same product) and a `DEPRECATED` line in its
  comment;
- `install()`: installs it, and `report.superseded` and the summary list each deprecated
  activity with its successor. An input another Atlas process makes links to a current producer
  before a deprecated one;
- a successor that is not in the build, or has another version than named, is a warning.

## Data quality rating

`processes/<id>/lca/manifest.json` (written by `cheme assess lca --write`) carries the rating of
the plant's dataset in `data_quality` (core#178): the TfS DQR with TeR, GeR and TiR, the
PEF-style P, C and DQR, the primary data share, the basis it is weighted by and the weakest
indicator. It is copied unchanged into the dataset's `data_quality` in `datapackage.json`; a
dataset without a manifest, or with one written before core#178, has `null`.

## Caveats

- ASU-1's characterisation factors (`lca/factors.yaml`, `example: true`) are placeholders: the
  plantcode results they give are not meaningful numbers. The LCI itself carries no factors.
- The datasets are screening level (concept-stage flows and duties, about +/-30 %); each process
  states its maturity and review status (`datapackage.json`, activity comments).
- The ASU dataset is from example-asu PR #11 (in review): numbers may still change.

## Build

```sh
uv run scripts/build_lci.py --library <process-library> --out <dir> --version 0.1.0 [--strict] \
    [--public] [--system-model substitution] [--previous <earlier build>]
# -> <dir>/lci/cheme-as-code-atlas-0.1.0.xlsx, <dir>/lci/datapackage.json, <dir>/lci/index.json
#    (+ changes.json, CHANGES.md with --previous)
```

`<dir>/lci/` is replaced; nothing else in `<dir>` is touched. Mappings come from
`<library>/lci/mappings.yaml`, else this staged copy. Two runs on the same input are
byte-identical (the workbook's document dates and zip entry dates are fixed).

The build first validates `chemicals/chemicals.yaml` against its schema and the registry checks
(`scripts/registry.py` `check`: CAS check digits, InChIKeys, properties against the formula,
duplicate crosswalk names, unknown `flow_grades` grades) and stops on any problem, before it
reads a process.

## Change reports

`--previous <dir>` (a folder holding an earlier build's `lci/`, or that `lci/` itself; not the
output folder) writes `lci/changes.json` and `lci/CHANGES.md`: per dataset its status (by content
hash and its allocation method and shares), version before and after and whether a changed
dataset's version was raised; per
activity the exchanges added, removed and changed (amount with relative change, or link). The
report is **exchange level only**: no impact delta is computed, because the CI stub background
(below) is built from one process's example factors inside the Brightway test and is not a
reference background for the library. Releases: docs/governance.md and
`.github/workflows/release.yml` (started by hand; drafts the artefacts and the Zenodo metadata,
publishes nothing).

## Verification

`tests/test_lci_brightway.py` (marker `brightway`) builds ASU-1's export, installs it with
`install()` into a temporary Brightway project (bw2io's packaged default biosphere3, no network)
against a **stub background** in which every mapped activity emits its example factor as fossil
CO2, and checks that an LCA of 1 t GOXP in the **substitution variant** reproduces plantcode's
baseline (`results.csv`, which includes the study's recycling credits) to the precision
plantcode prints, and that the default **cut-off** database differs from it by exactly those
credits. It also covers Atlas-internal linking, treatment signs, the overwrite
refusal and the unlinked report on the fixture library.

```sh
uv run --python 3.12 --with pytest --with pyyaml --with jsonschema --with openpyxl \
  --with ./python --with bw2calc pytest -m brightway tests
```
