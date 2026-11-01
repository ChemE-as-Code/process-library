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
prefer_atlas=True, overwrite=False, expect=None, pin=())`:

- runs `bw2io.ExcelImporter` and its standard strategies, then `match_database` against
  `background` (name, reference product, unit, location) and the biosphere (name, categories,
  unit); `biosphere` defaults to `biosphere3`, else the one `*biosphere` database in the project;
- `location` replaces the location of every input marked `atlas location rule: site`; without it
  the workbook's default (`DE`) is used and the report says so;
- `prefer_atlas=True` (or `"market"`) links an input that another Atlas process makes (e.g.
  liquid nitrogen from ASU-1) to the Atlas **market** of its grade instead of the background:
  delivered, with transport and losses ([markets](../docs/markets.md)). `prefer_atlas="plant"`
  links it to the plant gate instead, and `pin=["<activity code>", "<code>/<atlas key>"]` does so
  for single inputs; `False` keeps the background. Without a market of the grade the link goes to
  the plant;
- the report lists **every Atlas-to-Atlas link** (`report.atlas_links`: inputs, a market's
  suppliers, `link.dataset`) with the build's compatibility check (grade, unit, system model,
  allocation, boundary) and the supply chains (`report.chains()`), prints the Atlas system model
  and methodology version, and warns (`report.warnings`) about an incompatible link, an unused
  pin, or a background that records another system model;
- links an elementary flow by its biosphere3 UUID (`atlas flow uuid`) when the biosphere
  database has a flow of that code and unit, else by name, categories and unit; writes the
  `atlas pedigree` scores as Brightway's `pedigree`;
- reports the database's **system model** and methodology version (`report.system_model`,
  `report.methodology_version`, in `summary()`), and lists deprecated activities with their
  successors (`report.superseded`);
- writes the database **only if every exchange is linked**; otherwise nothing is written and
  `report.unlinked` lists each exchange that found no partner (fix the name in your background
  or in `lci/mappings.yaml`; an `atlas gap` exchange of an unpublished process has no mapping
  yet and is never linked). Nothing is dropped silently;
- refuses to replace an existing database of the same name unless `overwrite=True`.

Without the helper, plain bw2io works too (`bi.ExcelImporter(path)`, `apply_strategies()`,
`match_database(...)`), but then site locations, Atlas links and treatment signs (below) are yours
to handle.

## What is in the download

| file | |
|---|---|
| `lci/cheme-as-code-atlas-<version>.xlsx` | the database `cheme-as-code-atlas-<version>`: an `about` sheet (skipped by the importer), a `database` sheet, one sheet per process, a `markets` sheet, a `proxies` sheet. Exchange columns beyond bw2io's: `atlas key`, `atlas flow uuid`, `atlas pedigree`, `atlas carrier` and the linking fields |
| `lci/datapackage.json` | version, library commit, per process: title, design maturity, review status, data status (exchanges by provenance), factor status of the study, allocation and shares, functional unit, activities (each with its `chemical` slug and registry `grade`, null when none), and per dataset its `property_checks` and `benchmarks` (below) |
| | `activities`: one entry per exported activity (datasets, markets and proxies) with what its Atlas page `/lci/<code>/` shows: exchanges per unit of the reference product with unit, provenance, source, pedigree and lognormal, background link target by name or Atlas activity by code, elementary flows with biosphere3 UUID and compartment, the flowsheet `streams` an exchange derives from, `used_by`, header (geography, time, technology, classification with ISIC from the families and CPC/HS and CAS from the registry), allocation share, `closure` (core#174, or `not-assessed` with the reason), citation (DOI null until deposited), each database file that holds it with how to find it there (workbook and multifunctional JSON by code, or the dataset code of the unallocated form; openLCA JSON-LD by process id and member), a market's suppliers, shares, transport and losses with status and source (`market`, from `markets`), and `publication` (a market is public when all its suppliers are). No impact values (ADR 0015, `scripts/lci_activities.py`) |
| `lci/benchmarks.json` | the stored benchmark report of the build: every KPI result (process, dataset, value, allocated value, status, reference, reason) and the counts by status, in total and per process ([benchmarks](../docs/benchmarks.md)) |
| `lci/cheme-as-code-atlas-<version>-olca-jsonld.zip` | the same database for **openLCA** (JSON-LD, olca-schema 2): one unallocated multi-output process per dataset with allocation factors (below); markets and proxies as single-output processes, the default provider of every exchange linked to them |
| `lci/cheme-as-code-atlas-<version>-multifunctional.json` | the **unallocated multi-output** datasets for Brightway's `multifunctional` package, with allocation properties (below); `install_multifunctional()` |
| `lci/gaps.json` | the mapping gaps of unpublished processes (`cheme-as-code/lci-gaps/v1`): per process, each unlinked exchange with dataset, path, key, type, the link it lacks (`technosphere` or `biosphere`) and the reason; `count` 0 without gaps (Linking, below) |
| `lci/index.json` | what the Atlas site reads: file names, sizes, sha256, `format` and `format_version` of every file, activities per process, exported markets, caveats, system model |
| `lci/changes.json`, `lci/CHANGES.md` | with `--previous`: the change report against the earlier build (below) |

`datapackage.json` also records the **system model** (`system_model`: id, label, methodology
document and version, the exchanges excluded under cut-off with their decisions, allocation
findings), the **markets** (every market of `markets/` with its status, suppliers and shares,
and each number with its status and source), the **Atlas links** (`atlas_links`: every
Atlas-to-Atlas link with its compatibility checks) and, per dataset, its **version**, `methodology_version`, `content_sha256`, `review`
record (`unreviewed` by default), `valid_until`, and the allocation with the rule of the
hierarchy that justifies it. These come from the dataset itself when it states them (core's
dataset contract v2, below); otherwise the build's methodology version and `0.1.0`. A dataset
also carries its `system_model` (null when it states none), its `data_quality` rating from
`lca/manifest.json` (below), a `documentation` block (uuid, geography, time, technology,
classification, production volume, data generator, as the dataset gives them) and, when it is
deprecated, `deprecated: true` and `superseded_by`.

Activity codes are stable: `<process>:<dataset>:<product key>` (e.g.
`asu-1:asu-1-500-t-d-gox:product:GOXP`), `market:<product>:<region>` (e.g.
`market:nitrogen/lin:RER`; a technology market adds `:<technology>`) and `proxy:<id>`.

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
  only; substitution and `none` are refused. bw2io's Excel importer has no clean representation
  of the unallocated multi-output form, so the workbook holds the allocated activities; the
  multi-output form is in the openLCA and multifunctional files ([Other formats](#other-formats)).
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
- **Markets** ([docs/markets.md](../docs/markets.md)): `markets/<substance>.yaml` gives per
  product and region the Atlas producers weighted by production volume (or sourced shares), the
  transport legs (ton kilometer of a `lci/mappings.yaml` entry) and the losses on the way, each
  number with its status (cited, calculated, assumed) and source. They are activities of the
  same database. An Atlas input links to the market of its grade by default, with the plant
  beside it for pinning; a producer of another grade is refused; a link at a plant gate because
  no market exists is a warning. ASU-1 supplies the first four: LOX and LIN by cryogenic road
  tanker with boil-off and transfer losses, GOX and GAN by pipeline; argon markets are planned.
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

Curated, library level, schema `schemas/lci-mappings.schema.json`: the shared vocabulary
(technosphere entries by chemical or utility slug or factor id, proxies, biosphere identities,
pass-through decisions, cut-off exclusions, the substitution variant, allocation). A process's
own overrides live with it in `processes/<id>/lca/mappings.yaml` (schema
`schemas/lci-process-mappings.schema.json`): `exchanges:` keyed by the dataset's exchange key
(`<kind>:<id>`), each entry `use`s a technosphere entry, gives the exchange's `chemical` slug,
`atlas: false` or a `properties_reason`. The build merges them; the same exchange overridden in
`lci/mappings.yaml` (`"<id>/<key>"`) too is an error (ADR 0022). Per exchange: an override, else
the dataset exchange's own `link` (a Brightway activity, biosphere flow or another Atlas
dataset), else its chemical slug, else its `link.factor` id, in `technosphere:`.

A missing mapping (no technosphere mapping, or an emission or resource without a biosphere
identity) fails the build for a **public** process and in a `--public` build. For a process
that is not public (`publication.status` internal, candidate or none) it is a **gap**: its
preliminary LCI is still built, the exchange exported **unlinked** (amount and unit kept, no
`database`, categories or Atlas alternative, column `atlas gap` with the reason; the activity's
`atlas gaps` count and an `UNLINKED` comment line), never linked to a guess, dropped or
zero-filled. Gaps are listed in the build report (`gap:` lines), `lci/gaps.json`,
`datapackage.json` `processes[].gaps` and `index.json` `gaps`, and do not fail `--strict`.
`install()` reports a gap as unlinked and writes nothing, so map every gap before a process is
published: setting it public turns each gap into an error.

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
  cooling water as heat rejected (0.01 kWh electricity per kWh; kept on it until ASU-1 decides
  its cooling configuration, see Library utilities), pipe per m (20 kg steel), fittings
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

The background names follow ecoinvent 3.11 conventions. They are verified only by a recorded
check against a licensed copy (ADR 0017):

```sh
# in a Brightway project that holds the licensed background and its biosphere
uv run --with bw2data --with pyyaml --with jsonschema --with openpyxl scripts/check_mappings.py \
    --project my-lca --background ecoinvent-3.11-cutoff --version 3.11 \
    --checked-by "<name>" --site DE --site NL --write
```

It checks every `technosphere` and `substitution.technosphere` activity (name, reference product,
unit, location; a `location: site` once per `--site`) and every `biosphere` flow (UUID, else name
and categories), exactly as the installer matches them, and writes
`lci/mapping-checks/<date>-<database>.yaml` (schema `schemas/lci-mapping-check.schema.json`):
the database and version, the date, who checked, the sites, and every unmatched name with the
reason (and, for a wrong location, the locations at which the name exists). It holds our own
names only, no background data. The build reads the latest record and writes
`datapackage.json` `brightway.background_check` with `status`:

| status | meaning |
|---|---|
| `unchecked` | no record in `lci/mapping-checks/` |
| `failed` | the latest record lists unmatched names |
| `stale` | a checked name in `lci/mappings.yaml` changed (or was added) after the latest record |
| `verified` | every name matched, and none changed since |

Anything but `verified` is also listed in `index.json` `caveats`. An invalid record fails the
build. Flows that a dataset links by its own crosswalk UUID are not in the mappings, so this
check does not cover them; `install()` reports any that do not link.

## Library utilities

Site utilities and end-of-pipe treatment are ordinary library processes (process-library#45),
so every process links to the same documented models instead of its own proxy:

| process | dataset, per | operating range |
|---|---|---|
| `utility-steam-ng-boiler` | saturated steam, natural-gas boiler, kg | steam at 11 bar(a) or below, heat up to 184 degC |
| `utility-cooling-tower` | heat rejected, evaporative tower, kWh | cooling water at 25 degC supply or warmer |
| `utility-wwtp` | wastewater, activated sludge, kg (1 m3 = 1000 kg) | a fixed design COD of 1 kg/m3 (ASSUMED) |
| `utility-flare` | gas flared, as methane, kg | methane-rich gas |
| `utility-chiller` | cold, chilled water, kWh | 6 degC or warmer |
| `utility-instrument-air` | dry instrument air, 8 bar(a), kg | 8 bar(a) (not checked yet) |

- **Where they live.** `processes/utility-*`, not a separate `utilities/` tree: both builders
  find processes as `processes/*/process.yaml`, the Atlas URL is the folder id, the taxonomy
  already has the families (`steam-and-heat`, `utilities`, `wastewater-treatment`,
  `waste-treatment`, ISIC 3530, 3600, 3700, 3821) and `coverage.yaml` names covering processes
  by id. A `utility-` prefix keeps them together without a second discovery path.
- **Datasets.** Manifest-only processes with one hand-written `lca/datasets/*.yaml` each, in
  core's Tier 1 form (core#182): every amount is a `formula` of the dataset's `parameters`, the
  element balance is recorded and closed, design maturity is `concept`. Physical properties and
  stoichiometry have their sources; every design parameter (efficiencies, cycles of
  concentration, heads, yields, the ambient state) is **ASSUMED** with a TODO, so the datasets
  are first-principles screening models with pedigree `[4, 4, 3, 4, 4]`. What each leaves out is
  in its `system_boundary.excluded` and README (e.g. NOx of the boiler, cooling-water chemicals,
  N2O of the WWTP, the chiller's refrigerant losses).
- **Linking: Atlas first, background as the alternative.** Each utility product has a registry
  slug of kind `utility` (`steam`, `cooling-water`, `wastewater`, `flare-gas`, `chilled-water`,
  `instrument-air`). A consumer's input of one, and also its *output* of a utility service (heat
  to cooling water, wastewater, gas to the flare), names the Atlas utility as `atlas activity`, so
  `install(prefer_atlas=True)` links it there; with `prefer_atlas=False` it keeps the background
  mapping of `technosphere:` (unit proxies convert kg of steam, gas and wastewater to the
  background's MJ and m3). An `exchanges:` override with `atlas: false` keeps an exchange on its
  background. Provider profiles that select a background per study (core#168) do not exist yet.
- **Operating range.** A utility product states its level as a `carrier` (steam pressure, cold
  temperature). An exchange whose own `carrier` is outside it is not linked to the utility: the
  build warns (failing `--strict`) and keeps the background; an explicit `link.dataset` outside the
  range is an error (`carrier_refusal`: steam serves steam at its pressure or below and heat up to
  its temperature; cold serves a need at its temperature or warmer). An exchange without a
  carrier is not checked. Core's carriers (core#177) describe energy only, so a gas product's
  pressure (instrument air) is not checked yet.
- **Nitrogen** needs no utility dataset: a consumer's `nitrogen` input links ASU-1's GANP (or
  LIN, by the grade it names) with `prefer_atlas`, and merchant LIN in the background otherwise.
- **ASU-1** keeps its cooling-water screening proxy (`exchanges: asu-1/product:CW: atlas:
  false`) until it decides its site's cooling configuration; removing the override links it to
  the cooling tower, with its make-up water resource.

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
  states its design maturity and review status (`datapackage.json`, activity comments).
- The ASU dataset is from example-asu PR #11 (in review): numbers may still change.

## Other formats

Written by `scripts/export_formats.py`, which `build_lci.py` calls after the workbook. Both read
the build's own activities and the unallocated datasets behind them (same mappings, same
linking): there is no second source of truth. `index.json` lists each file with its sha256,
`format` and `format_version`.

**openLCA JSON-LD** (`-olca-jsonld.zip`, olca-schema 2, written with the pinned `olca-schema`
2.6.2 package):

- one **multi-output unit process per dataset** with every co-product as an output, plus the
  screening proxies as single-output processes. Allocation factors: the build's method as the
  default allocation method, with exactly the build's shares (exergy, energy and mass as
  `PHYSICAL`, economic as `ECONOMIC`, given shares as `CAUSAL`), and beside it `PHYSICAL` by mass
  or `ECONOMIC` by price where every co-product has the property. openLCA's allocated result per
  unit of a product is then the workbook's activity; the process description lists the factors;
- an input another Atlas process makes is linked to that process (`defaultProvider`), as
  `install(prefer_atlas=True)`. A background input is a product flow named by its reference
  product (ecoinvent 3.11 cut-off naming, unchecked), with the provider by name, reference
  product and location in the exchange's description: map these flows to your background with
  openLCA's flow mapping. An input your background models as a waste treatment must be mapped to
  the waste flow as an output (the build cannot tell; the Brightway installer flips its sign);
- units and flow properties are **references to openLCA's reference data** (UUIDs from
  `olca_schema.units`); import into a database that has openLCA's reference units and flow
  properties. A unit openLCA has no reference unit for (Brightway's standard cubic meter) fails
  the build;
- the lognormal is written as openLCA's (geometric mean, GSD); the pedigree scores are in the
  exchange's description (no data quality system is referenced);
- identifiers (uuid5, namespace `uuid5(NAMESPACE_URL, "https://github.com/ChemE-as-Code/process-library/lci")`,
  `export_formats.atlas_uuid`): a dataset's process is the **dataset's own `uuid`** (core: uuid5
  of plant and dataset id) in the default build, `atlas_uuid("process", <code>)` without one, and
  `atlas_uuid("process", <system model>, <code>)` in a labelled variant, so that the
  substitution build does not overwrite the default in one openLCA database. Atlas product flows
  are `atlas_uuid("flow", <activity code>)`, background flows `atlas_uuid("flow", "background",
  <reference product>, <unit>)`, locations `atlas_uuid("location", <code>)` (Atlas locations,
  not openLCA's reference locations);
- **elementary flows** keep their **biosphere3 UUID** where the build has one (`atlas flow
  uuid`: ecoinvent's elementary exchange id as distributed with bw2io). A flow without one gets
  `atlas_uuid("flow", "elementary", <name>, <categories>, <unit>)` and says in its description
  that it is not an EF 3.1 or ecoinvent UUID: map it by name and category. EF 3.1 UUIDs are not
  recorded by core yet (core#313) and are never guessed. Whether a biosphere3 UUID matches a flow
  of your openLCA database depends on that database's elementary flow list.

**Brightway multifunctional** (`-multifunctional.json`, schema
`cheme-as-code/lci-multifunctional/v1`, for `multifunctional` 1.1, BSD-3-Clause): one
multi-output process per dataset (amounts per dataset basis, e.g. 1 h of operation), each
co-product a functional production edge with its allocation properties: `mass` (1 for a product
in kg), `exergy` and `energy` (kJ per unit, as the dataset or study states them; core
`ProductProperties`), `price` (only where stated) and `share` (the build's share). Nothing is
filled in that the dataset does not state: ASU-1 has mass, exergy and share, no price and no LHV.
Each process's `default_allocation` is the build's method (`exergy` for ASU-1), or `share` where
the properties cannot reproduce it. A single-output dataset is an ordinary process under its
activity code.

```python
from cheme_as_code_lci import install_multifunctional   # pip install "./python[multifunctional]"

report = install_multifunctional("lci/", background="ecoinvent-3.11-cutoff", location="FR")
mf = report.database                                       # cheme-as-code-atlas-<version>-multifunctional
node = bd.get_node(database=mf, code="asu-1:asu-1-500-t-d-gox")
node["default_allocation"] = "mass"                        # or exergy, energy, price, share, equal
node.save(); bd.Database(mf).process()                     # re-allocates
```

It links exactly as `install()` and refuses to write while anything is unlinked. The allocated
read-only activities carry the workbook's codes (`asu-1:asu-1-500-t-d-gox:product:GOXP`); with
the default strategy they are the workbook's activities. The strategies `exergy`, `energy` and
`share` are added to the project (`multifunctional.add_custom_property_allocation_to_project`).
The allocated workbook stays the default download.

**Not yet:** ILCD (EF 3.1 flavour) needs EF 3.1 elementary flow UUIDs (core#313) and the EC's
ILCD validator; EcoSpold2 / SimaPro CSV and PACT PCF are open (#51).

## Build

```sh
uv run scripts/build_lci.py --library <process-library> --out <dir> --version 0.1.0 [--strict] \
    [--public] [--system-model substitution] [--previous <earlier build>]
# -> <dir>/lci/cheme-as-code-atlas-0.1.0.xlsx, -olca-jsonld.zip, -multifunctional.json,
#    <dir>/lci/datapackage.json, benchmarks.json, gaps.json, index.json
#    (+ changes.json, CHANGES.md with --previous)
```

`<dir>/lci/` is replaced; nothing else in `<dir>` is touched. Mappings come from
`<library>/lci/mappings.yaml`, else the process library's own, plus each
`<library>/processes/<id>/lca/mappings.yaml`. `--strict` fails on warnings too, not on the gaps
of unpublished processes. Two runs on the same input are
byte-identical (the workbook's document dates and zip entry dates are fixed; the JSON-LD zip has
sorted entries, fixed dates and no `lastChange` stamps).

The build first validates `chemicals/chemicals.yaml` against its schema and the registry checks
(`scripts/registry.py` `check`: CAS check digits, InChIKeys, properties against the formula,
duplicate crosswalk names, unknown `flow_grades` grades) and stops on any problem, before it
reads a process.

## Change reports

`--previous <dir>` (a folder holding an earlier build's `lci/`, or that `lci/` itself; not the
output folder) writes `lci/changes.json` and `lci/CHANGES.md`: per dataset its status (by content
hash and its allocation method and shares), version before and after and whether a changed
dataset's version was raised; per
activity the exchanges added, removed and changed (amount with relative change, or link).

**Reference impacts** (`scripts/reference_impacts.py`): per dataset and activity, GWP100 per 1 unit
of the activity's reference product in both builds, with the absolute and relative delta; an added
or removed dataset or activity gets its one value and no delta. The report states its method and
background (`changes.json` `impact`, and the section "Reference impacts" of `CHANGES.md`):

- method: core's packaged characterisation of direct emissions, `ipcc2021-gwp100` (IPCC 2021 AR6,
  with its source, from `chemeascode/domains/assessment/lca/data/methods.yaml` of the installed
  `cheme-as-code`); flows are matched by biosphere3 UUID, else name and categories, through
  core's elementary-flow crosswalk. No factor is stored in the library;
- background: **none** (`none-atlas-foreground-only`). The value is the activity's own
  characterised emissions plus those of the Atlas activities it links to (as `install()` links
  them with `prefer_atlas=True`). Every background input (electricity, materials, construction,
  transport, treatment), the inputs of the proxies, the exchanges the build leaves out and the
  uncharacterised flows contribute 0; each activity lists its background inputs and
  uncharacterised flows (`excluded`). No licensed background (ecoinvent) is used or packaged.

So the value is a screening reference for comparing releases, not an LCA result: a process whose
burden is all in the background (ASU-1: electricity; its emissions are pass-through) shows 0.
An unchanged dataset can still show a delta when an Atlas activity it draws on changed
(`atlas_upstream`). Without core installed, the report says the impacts are not computed. The CI
stub background (below) is a test device, not a reference background. Releases: docs/governance.md and
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
refusal and the unlinked report on the fixture library, and the **multifunctional round trip**:
installed with `install_multifunctional()` and allocated with each process's default strategy,
the multi-output datasets give the workbook's activities code for code (fixture library and
ASU-1); re-allocated by mass, ASU-1 conserves the unallocated total.

`tests/test_export_formats.py` checks the **JSON-LD** structurally: every entity loads with
olca-schema and writes back unchanged, every reference resolves (in the package, or among
openLCA's reference units), elementary flows keep their biosphere3 UUIDs, and openLCA's
allocation of each multi-output process gives the workbook's amounts per unit of product. The
import into openLCA itself (olca-ipc against a running openLCA) is not run in CI.

```sh
uv run --python 3.12 --with pytest --with pyyaml --with jsonschema --with openpyxl \
  --with ./python --with bw2calc --with olca-schema==2.6.2 --with multifunctional==1.1.2 \
  pytest -m brightway tests
```
