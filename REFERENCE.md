# Process library reference

Versioned designs of chemical processes, one folder per process, kept as plain files in git. It
is the source of the [Process Atlas](https://atlas.cheme-as-code.org) (built in
[`ChemE-as-Code/website`](https://github.com/ChemE-as-Code/website), `apps/atlas`) and of its
LCI database. The [README](README.md) introduces the library; [CONTRIBUTING.md](CONTRIBUTING.md)
says how to add a process.

| path | what |
|---|---|
| `processes/<id>/process.yaml` | the Atlas manifest of a process (schema `schemas/process.schema.json`): title, families, inputs and outputs by chemical, design maturity, review status, references |
| `processes/<id>/plant.yaml` and the rest | optional: a ChemE-as-Code engineering project: P&IDs, BFD/PFD, lists, layout, LCA. Its own README says how to work in it |
| `processes/<id>/lca/dataset.yaml`, `lca/datasets/*.yaml` | optional: unallocated LCI datasets (core's `lci_dataset`), the input of the LCI database |
| `processes/<id>/lca/scenarios/<id>.json` | optional: core's per-scenario records (`cheme assess lca-scenarios --write`): the design case, regional background scenarios (geography, year, electricity), linked exchanges and their states, totals per functional unit; the catalog publishes them (see below) |
| `chemicals/chemicals.yaml` | chemicals and products registry: the slugs processes name, which link them in the Atlas graph, with identity (CAS, InChIKey, ChEBI), grades (`oxygen/lox`) for LCI reference products, sourced properties, CPC/HS codes and crosswalk names ([docs/registry.md](docs/registry.md)) |
| `taxonomy/families.yaml` | process families mapped to ISIC Rev.4 and NACE Rev. 2; `process.yaml` `families` are validated against it |
| `markets/<substance>.yaml` | market datasets: per product grade and region, the Atlas producers weighted by production volume, transport by mode and distance, and losses, each number with its source or marked assumed; activities `market:<product>:<region>` of the LCI database, the default link of an Atlas input ([docs/markets.md](docs/markets.md)) |
| `benchmarks/<family>.yaml` | the benchmark registry: KPIs per process family with reference ranges from cited open sources (or a recorded "no open reference"), evaluated on each LCI dataset by both builders and stored per build in `benchmarks.json` ([docs/benchmarks.md](docs/benchmarks.md)) |
| `coverage.yaml` | the coverage roadmap: ranked products and processes with variants, value-chain links, open sources and the planned tier ([docs/coverage.md](docs/coverage.md)) |
| `lci/mappings.yaml` | how LCI exchanges link to Brightway background and biosphere data (by name; no licensed data), the system model (cut-off), its exclusions and the substitution variant, and the database's allocation per process: the shared vocabulary. A process's own exchange overrides are in `processes/<id>/lca/mappings.yaml` (ADR 0022) |
| `lci/mapping-checks/` | the recorded checks of those names against a licensed background (`scripts/check_mappings.py`, ADR 0017); the build reports the latest as `verified`, `failed`, `stale` or `unchecked` |
| `docs/` | `system-model.md` (the LCI database's methodology: system model, allocation hierarchy, cut-off rules), `markets.md` (markets, their layers and the chaining of Atlas processes), `governance.md` (versions, change reports, releases and DOIs, review, contribution policy draft), `registry.md`, `coverage.md`, `benchmarks.md`, and `adr/` (architecture decision records: why the library is built this way) |
| `schemas/` | JSON Schemas of process.yaml, the registry, the mappings, the taxonomy, the coverage roadmap, the benchmarks and the markets |
| `templates/process/` | starter folder for a new process |
| `scripts/` | `build_catalog.py` (catalog for the Atlas), `build_lci.py` (Brightway workbook), `render_previews.py` and `export_snapshots.py` (drawings and viewer snapshots, via `cheme`); `publication.py` (the rules of `--public`); `registry.py` (grades and registry checks); `benchmarks.py` (KPI evaluation); `reactions.py` (the reactions of the catalog, `reactions.json`); `check_mappings.py` (the check of the background names against a licensed copy); `markets.py` (market files and the default market of an input); `reference_impacts.py` (reference GWP deltas of the LCI change report) |
| `python/` | `cheme-as-code-lci`, the one-call Brightway installer of the LCI database |
| `tests/` | tests of the scripts, with a synthetic fixture library |

## Processes

| id | process | design maturity | engineering project |
|---|---|---|---|
| [`asu-1`](processes/asu-1/) | Cryogenic air separation unit, 500 t/d GOX | screening (calculation maturity: balanced; not independently reviewed) | yes (DEXPI P&IDs, BFD/PFD, 3D layout, MTO, LCA, DWSIM checks) |
| [`utility-steam-ng-boiler`](processes/utility-steam-ng-boiler/) | Steam, saturated 11 bar(a), natural-gas boiler (library utility) | concept (Tier 1 form, design parameters ASSUMED; not reviewed) | no (manifest and LCI dataset only) |
| [`utility-cooling-tower`](processes/utility-cooling-tower/) | Cooling water, evaporative cooling tower, 25/35 degC (library utility) | concept (Tier 1 form, design parameters ASSUMED; not reviewed) | no (manifest and LCI dataset only) |
| [`utility-wwtp`](processes/utility-wwtp/) | Wastewater treatment, activated sludge (library utility) | concept (Tier 1 form, design parameters ASSUMED; not reviewed) | no (manifest and LCI dataset only) |
| [`utility-flare`](processes/utility-flare/) | Flaring of methane-rich waste gas (library utility) | concept (Tier 1 form, design parameters ASSUMED; not reviewed) | no (manifest and LCI dataset only) |
| [`utility-chiller`](processes/utility-chiller/) | Chilled water at 6 degC, electric chiller (library utility; refrigerant losses not yet counted) | concept (Tier 1 form, design parameters ASSUMED; not reviewed) | no (manifest and LCI dataset only) |
| [`utility-instrument-air`](processes/utility-instrument-air/) | Instrument air, dried, 8 bar(a) (library utility) | concept (Tier 1 form, design parameters ASSUMED; not reviewed) | no (manifest and LCI dataset only) |

Three separate axes, named as in core's [glossary](https://github.com/ChemE-as-Code/core/blob/main/docs/concepts/glossary.md) (ChemE-as-Code/core#323):

- **design maturity** is `process.yaml` `maturity` (`concept` to `operating-reference`): how far
  the design is claimed to be taken. The claim is capped by evidence: in an engineering project
  `cheme maturity` warns (`cheme.maturity-claim-exceeds`) when it exceeds what the calculation
  maturity supports; beside a Tier 0/1 LCI dataset it is at most `concept`
  (`cheme.lci-tier-maturity`).
- **calculation maturity** is `checks/maturity.json` (`sourced`, `balanced`, `predictive`,
  `engineering`): the level `cheme maturity` evaluates from the files of an engineering project.
  `sourced` supports at most `concept`, `balanced` and `predictive` at most `screening`,
  `engineering` at most `basic-engineering`.
- **review status** is `process.yaml` `validation.status` (`unreviewed` to `industry-validated`):
  who has checked the design. Only people set it; passing automated checks is not a review.

## Working on a process

Each engineering project is self-contained: run `cheme` and Claude Code **in its folder**
(`cd processes/asu-1`). `cheme` finds the plant by walking up to `plant.yaml`, and what its
docs call "the repository root" is that folder. Once per clone, in a process folder:
`cheme git-setup` (readable P&ID diffs and the pre-commit check of that plant).

## Adding a process

See [CONTRIBUTING.md](CONTRIBUTING.md): copy `templates/process/` to `processes/<id>/`, fill in
`process.yaml`, add new chemicals to the registry. No change to the Atlas is needed.

## Building the catalog and the LCI database

```sh
uv run scripts/build_catalog.py --library . --out dist [--artifacts <previews>] [--snapshots <snapshots>] [--strict] [--public] [--cheme cheme]
uv run scripts/build_lci.py --library . --out dist --version 0.1.0 [--strict] [--public] [--system-model substitution] [--previous <earlier build>]
uv run --python 3.12 --with pytest --with pyyaml --with jsonschema --with openpyxl --with ./python --with bw2calc pytest -q tests
```

**Benchmarks need core.** The KPIs of `benchmarks/` are converted to their units by core's
`foundation.units` ([docs/benchmarks.md](docs/benchmarks.md)). Without core a KPI is
`unchecked`, which fails `--strict`, and the tests that need core are skipped. Add core with
`--with "cheme-as-code[units] @ git+https://github.com/ChemE-as-Code/core.git"` (or a local
clone) to the `uv run` of the builds and the tests; CI does, with core pinned to one commit
(`.github/workflows/validate.yml`), and sets `ATLAS_REQUIRE_CORE` so a missing core fails the
tests there.

**Reactions.** The catalog's `reactions.json` lists every reaction of the processes'
`process/reactions.yaml` once (`scripts/reactions.py`, ADR 0023): the same species (by the
component's CAS number in `process/materials.yaml`) with the same coefficients up to a factor,
in the same direction unless reversible. Each reaction has its slug (from the equation with each
formula in one order, stable while the reaction is), equation, species (with the registry chemical of the same CAS number,
else none), the processes and families that use it and its variants (the same stoichiometry
reversible or written the other way); each process's statement of it keeps its own id,
equation, conversion, heat of reaction (kJ/kmol, as given and `per_equation` for the merged
equation), equilibrium constant, rate, catalyst (with its `process/catalysts.yaml` entry and
window: K, kPa), phase, sources, and the process's maturity and review status. Each statement
also has its element balance (`balance`), core's rule (`cheme.reaction-element-balance`, with
core's formula parser when core is installed, else a copy of it): the atoms per element of its
own stoichiometry with its components' formulas, `balanced` within 1e-9, `unbalanced` (with
`change`, atoms created per element) or `not-checkable` (with `missing`: each component not in
`materials.yaml`, without a formula, with one the parser does not read, or withheld from a
public build); never balanced when not checked. A reaction sums them per process, as a process
can state it more than once (a process balances only when each of its statements does;
`balance`: `balanced` in every process, `unbalanced` in any, `not-checkable` when none balances,
else `partial`; with the counts of processes and the `reasons` a statement was not checkable)
and says whether any statement cites a source (`has_sources`: a non-blank source for the
reaction, its conversion, its heat of reaction or its catalyst entry). A public build
lists the published processes only, without a file their `publication.exclude` covers
(core's glob rules, `publication.excluded`). With
`--cheme <command>`, a reaction also names the templates of core's reaction library
(`cheme chemistry library --json`) of the same stoichiometry (`templates`, and the command to
add one); without it, or when the command fails (a warning), `templates` is null.

**Design cases and regional scenarios.** One engineering project serves several operating
cases (flowsheet `cases:`, each with its declared `capacity`) and several geographical
backgrounds (`scenarios:` in `lca/lca.yaml` with `location`, `year`, `electricity`, `missing:`,
`proxy:`; core docs/framework/lci-scenarios.md). No folder is copied per region or capacity.
Run `cheme assess lca-scenarios --write` in the process folder and commit `lca/scenarios/`; the
catalog gives each process `lca.design_cases` and `lca.scenarios` and copies the records to
`scenarios/<id>/<scenario>.json`. A scenario whose values may not be published, or whose record
is stale, keeps its geography, states and gaps but loses its totals. Each scenario also carries
core's comparability verdict against the baseline (`comparability`: `like-for-like`, `proxy`,
`not comparable`; core#306, ADR 0016), the study `boundary`, and each link's factor `scope`.
ASU-1 has `nl-grid` and `de-grid` on core's packaged EEA 2024 grid factors (D-107). They are
**not comparable** with the UK baseline (D-110): EEA counts direct emissions at generation,
while the baseline factor is at the consumer with T&D and well-to-tank, a difference in basis
that a declared proxy discloses but does not bridge. A scenario missing data the baseline has
is not comparable as well.

CI (`.github/workflows/validate.yml`): every `processes/*/plant.yaml` is validated with `cheme`
in its folder; the library job runs the tests (including the Brightway round trip) and builds
the catalog and the LCI database, and the public catalog (`--public`: only processes with
`publication.status: public`, placeholder footprints withheld; see CONTRIBUTING.md). Nothing is
published. `.github/workflows/release.yml` (started by hand) drafts an LCI release with its
change report and archive metadata as a workflow artifact; it publishes nothing, as the release
decision is the owner's (docs/governance.md).

## Repository size

A DEXPI P&ID is 1 to 3 MB of XML (ASU-1's folder is about 14 MB), and every revision stays in
the history, so the clone grows with each process and each P&ID change. To keep that cheap:

- **Shallow clones where no history is needed.** CI checks out with `fetch-depth: 1`, except
  the library job, which builds the catalog: its git facts (each folder's last commit, whether
  previews and snapshots are behind it) need the history, so it uses `fetch-depth: 0`. A
  catalog built from a shallow clone gives every folder the head commit. For work on one
  process, a shallow sparse clone is enough:
  `git clone --depth 1 --filter=blob:none --sparse <url> && git sparse-checkout set processes/<id>`.
- **Keep generated output out of git.** `build/` and `dist/` are ignored: previews, viewer
  snapshots (about 14 MB per process) and the catalog are rebuilt from the sources.
  `export_snapshots.py --cache DIR` reuses a snapshot until its folder, the `cheme` version or
  the export options change.
- **Git LFS only for large generated binaries** that must be versioned (renders, meshes,
  spreadsheets exported for others), should they ever be committed. Never for the DEXPI XML or
  other engineering sources: they must stay text, diffable (`diff=dexpi`, `.gitattributes`) and
  reviewable. Blobs committed before a file moves to LFS stay in the history unless it is
  rewritten (`git lfs migrate`), so decide before the first commit.
