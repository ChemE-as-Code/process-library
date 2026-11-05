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
| `processes/<id>/lca/dataset.yaml`, `lca/datasets/*.yaml` | optional: unallocated LCI datasets (core's `lci_dataset`), the input of the LCI database: the study's `lca/dataset.yaml` (`cheme assess lca --write`), hand-written datasets of a manifest-only process, and a design case's own dataset `lca/datasets/<dataset id>-<case>.yaml` of an engineering project (`cheme assess lca --write --case <case>`, never edited; its activities are named `<title>, case <case>`, ADR 0034) |
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

The library has 50 process folders: 44 engineering projects (a `plant.yaml` with a process
flowsheet) and 6 library utilities (manifest and LCI dataset only). The table is generated
from each folder's `process.yaml` and `checks/maturity.json`; `coverage.yaml` names the
coverage entry and tier of each ([docs/coverage.md](docs/coverage.md)).

| id | process | design maturity | engineering project |
|---|---|---|---|
| [`acetaldehyde-1`](processes/acetaldehyde-1/) | Acetaldehyde by the one-stage Wacker oxidation of ethylene (100 kt/a) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`acetic-acid-1`](processes/acetic-acid-1/) | Acetic acid by low-water iridium methanol carbonylation (60 t/h glacial acid, concept) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`acetic-anhydride-1`](processes/acetic-anhydride-1/) | Acetic anhydride by the ketene route (acetic acid cracking, 50 kt/a, concept) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`acetone-1`](processes/acetone-1/) | Acetone and phenol from cumene (cumene hydroperoxide route, 200 kt/a phenol; cumene bought in, no alkylation step) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`acetylene-1`](processes/acetylene-1/) | Acetylene by partial oxidation of natural gas with NMP recovery (6.25 t/h, synthesis-gas co-product) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`alumina-1`](processes/alumina-1/) | Alumina by the Bayer process (3000 t/d smelter-grade alumina, concept) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`aluminium-1`](processes/aluminium-1/) | Primary aluminium by Hall-Heroult electrolysis with point-feed prebaked anodes (NFM BREF ranges, IPCC 2006 PFC) | concept (Tier 1 form, sourced conceptual inventory with ASSUMED parts; not reviewed) | no (manifest and LCI dataset only) |
| [`ammonia-1`](processes/ammonia-1/) | Ammonia from natural gas (1500 t/d, steam reforming with air-fed secondary reformer, Haber-Bosch loop) | concept (calculation maturity: not recorded; not reviewed) | yes (DEXPI P&IDs (14), BFD/PFD, flowsheet, LCI dataset) |
| [`aniline-1`](processes/aniline-1/) | Aniline by adiabatic gas-phase hydrogenation of nitrobenzene (25 t/h) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`asu-1`](processes/asu-1/) | Cryogenic air separation unit, 500 t/d GOX | screening (calculation maturity: balanced; not independently reviewed) | yes (DEXPI P&IDs, BFD/PFD, 3D layout, MTO, LCA, DWSIM checks) |
| [`bromine-1`](processes/bromine-1/) | Bromine from bromide brine by chlorine oxidation and steaming-out (Smackover-type brine) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`catalytic-reforming-1`](processes/catalytic-reforming-1/) | Catalytic reforming of naphtha with continuous catalyst regeneration (REF BREF ranges; reformate, hydrogen, LPG, fuel gas) | concept (Tier 1 form, sourced conceptual inventory with ASSUMED parts; not reviewed) | no (manifest and LCI dataset only) |
| [`cement-clinker-1`](processes/cement-clinker-1/) | Portland cement clinker in a dry kiln with preheater and precalciner (CLM BREF ranges, IPCC defaults) | concept (Tier 1 form, sourced conceptual inventory with ASSUMED parts; not reviewed) | no (manifest and LCI dataset only) |
| [`chlor-alkali-1`](processes/chlor-alkali-1/) | Chlor-alkali by membrane-cell electrolysis (100 kt/a Cl2, 50 wt-% caustic soda, hydrogen) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`chloromethane-1`](processes/chloromethane-1/) | Chloromethane from methanol and hydrogen chloride (gas-phase hydrochlorination, 100 kt/a) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`cumene-1`](processes/cumene-1/) | Cumene by zeolite alkylation of benzene with propylene (licensor figures, EPA emissions) | concept (Tier 0 form, stoichiometric screening with some sourced values; not reviewed) | no (manifest and LCI dataset only) |
| [`dmf-1`](processes/dmf-1/) | N,N-Dimethylformamide by carbonylation of dimethylamine (50 kt/a, sodium methoxide in methanol) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`ethanol-1`](processes/ethanol-1/) | Ethanol by direct hydration of ethylene (100 000 t/a anhydrous, phosphoric acid catalyst) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`ethylbenzene-1`](processes/ethylbenzene-1/) | Ethylbenzene by liquid-phase zeolite alkylation (LVOC BREF ranges) | concept (Tier 1 form, sourced conceptual inventory with ASSUMED parts; not reviewed) | no (manifest and LCI dataset only) |
| [`ethylene-1`](processes/ethylene-1/) | Ethylene and propylene by ethane steam cracking (1000 kt/a ethylene, concept) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`ethylene-glycol-1`](processes/ethylene-glycol-1/) | Ethylene glycol by ethylene oxide hydration (glycols-only EO/EG plant, 1200 t/d MEG) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`fcc-1`](processes/fcc-1/) | Fluid catalytic cracking of vacuum gas oil, full-combustion regenerator (REF BREF ranges, five co-products) | concept (Tier 1 form, sourced conceptual inventory with ASSUMED parts; not reviewed) | no (manifest and LCI dataset only) |
| [`formaldehyde-1`](processes/formaldehyde-1/) | Formaldehyde by methanol oxidation over iron molybdate (Formox type, 20 t/h formalin 50 wt%) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`formic-acid-1`](processes/formic-acid-1/) | Formic acid 85 wt% by methanol carbonylation and methyl formate hydrolysis (50 kt/a) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`glycerol-1`](processes/glycerol-1/) | Refined glycerol (USP) from biodiesel crude glycerol (10 000 t/a, concept) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`hda-1`](processes/hda-1/) | Toluene hydrodealkylation to benzene (100 kt/a, thermal HDA) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`hydrazine-1`](processes/hydrazine-1/) | Hydrazine hydrate by the peroxide process (PCUK, methyl ethyl ketazine route, 16 kt/a) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`hydrocracking-1`](processes/hydrocracking-1/) | Hydrocracking of vacuum gas oil, single-stage recycle (REF BREF ranges, products unsplit) | concept (Tier 1 form, sourced conceptual inventory with ASSUMED parts; not reviewed) | no (manifest and LCI dataset only) |
| [`hydrogen-1`](processes/hydrogen-1/) | Hydrogen by natural-gas steam methane reforming with PSA (100 000 Nm3/h, steam export) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`hydrogen-bromide-1`](processes/hydrogen-bromide-1/) | Hydrogen bromide synthesis burner with catalytic finishing and absorption (48 wt-% hydrobromic acid) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`hydrogen-chloride-1`](processes/hydrogen-chloride-1/) | Hydrogen chloride synthesis burner and absorption (33 wt-% hydrochloric acid, steam recovery) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`hydrogen-peroxide-1`](processes/hydrogen-peroxide-1/) | Hydrogen peroxide by the anthraquinone autoxidation process (50 kt/a H2O2, 50 wt%) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`hydrotreating-1`](processes/hydrotreating-1/) | Gas oil hydrodesulfurisation to ultra-low-sulfur diesel (REF BREF ranges, model formulas) | concept (Tier 1 form, sourced conceptual inventory with ASSUMED parts; not reviewed) | no (manifest and LCI dataset only) |
| [`hydroxylamine-1`](processes/hydroxylamine-1/) | Hydroxylammonium sulfate by catalytic NO hydrogenation (30 kt/a NH2OH, 25 wt% solution) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`iodine-1`](processes/iodine-1/) | Iodine from natural iodide brine by chlorine oxidation, air blowing-out and SO2 absorption (1000 t/a) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`iron-steel-1`](processes/iron-steel-1/) | Crude steel by the integrated blast furnace and BOF route (Iron and Steel BREF data, IPCC carbon balance) | concept (Tier 1 form, sourced conceptual inventory with ASSUMED parts; not reviewed) | no (manifest and LCI dataset only) |
| [`isobutene-1`](processes/isobutene-1/) | Isobutene by MTBE cracking (50 kt/a, gas-phase cleavage) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`kraft-pulp-1`](processes/kraft-pulp-1/) | Bleached softwood kraft pulp with chemical recovery (1000 ADt/d market pulp, concept) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`lime-1`](processes/lime-1/) | Quicklime by calcination of limestone in a natural-gas-fired parallel flow regenerative kiln (CLM BREF ranges) | concept (Tier 1 form, sourced conceptual inventory with ASSUMED parts; not reviewed) | no (manifest and LCI dataset only) |
| [`methanol-1`](processes/methanol-1/) | Methanol synthesis loop and purification (2500 t/d Grade AA, natural-gas syngas) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, no LCI dataset yet) |
| [`methylamines-1`](processes/methylamines-1/) | Methylamines (MMA, DMA, TMA) from methanol and ammonia | concept (calculation maturity: balanced, report from core 0.8.0, re-checked with core v1.2.1; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`n-bromosuccinimide-1`](processes/n-bromosuccinimide-1/) | N-Bromosuccinimide by semi-batch bromination of succinimide in aqueous NaOH (500 t/a, the first batch entry) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, batch recipe, LCI dataset) |
| [`natural-gas-processing-1`](processes/natural-gas-processing-1/) | Natural gas processing (amine CO2 removal, TEG dehydration, turbo-expander NGL recovery) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`nitric-acid-1`](processes/nitric-acid-1/) | Weak nitric acid by dual-pressure ammonia oxidation (1000 t/d HNO3 as 60 wt% acid) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`phosgene-1`](processes/phosgene-1/) | Phosgene from CO and chlorine over activated carbon (17.3 t/h liquid phosgene, captive) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`phosphorus-oxychloride-1`](processes/phosphorus-oxychloride-1/) | Phosphorus oxychloride from white phosphorus, chlorine and oxygen via PCl3 (4.0 t/h) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`potassium-permanganate-1`](processes/potassium-permanganate-1/) | Potassium permanganate from MnO2 ore by KOH roasting and electrolysis (1250 kg/h, concept) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`refinery-distillation-1`](processes/refinery-distillation-1/) | Crude oil distillation, atmospheric and vacuum units (one crude assay, REF BREF ranges) | concept (Tier 1 form, sourced conceptual inventory with ASSUMED parts; not reviewed) | no (manifest and LCI datasets only) |
| [`silicon-carbide-1`](processes/silicon-carbide-1/) | Silicon carbide by the Acheson process (5000 kg/h crude SiC, concept) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`soda-ash-1`](processes/soda-ash-1/) | Soda ash by the Solvay ammonia-soda process (1000 t/d light ash, concept) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`sodium-cyanide-1`](processes/sodium-cyanide-1/) | Solid sodium cyanide from Andrussow HCN (6.25 t/h, 50 kt/a) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`sodium-nitrite-1`](processes/sodium-nitrite-1/) | Sodium nitrite from ammonia oxidation and soda absorption (with sodium nitrate by inversion) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`styrene-1`](processes/styrene-1/) | Styrene by dehydrogenation of ethylbenzene (LVOC BREF ranges) | concept (Tier 1 form, sourced conceptual inventory with ASSUMED parts; not reviewed) | no (manifest and LCI dataset only) |
| [`sulfur-recovery-1`](processes/sulfur-recovery-1/) | Sulfur recovery by the modified Claus process with a catalytic oxidation tail gas unit (REF BREF ranges, EPA factors) | concept (Tier 1 form, sourced conceptual inventory with ASSUMED parts; not reviewed) | no (manifest and LCI dataset only) |
| [`sulfuric-acid-1`](processes/sulfuric-acid-1/) | Sulfuric acid from sulfur burning, double contact / double absorption (1000 t/d, 98.5 wt%) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`thf-1`](processes/thf-1/) | Tetrahydrofuran from 1,4-butanediol (50 kt/a, cyclodehydration and pressure-swing distillation) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`thionyl-chloride-1`](processes/thionyl-chloride-1/) | Thionyl chloride from sulfur, chlorine and SO2 over activated carbon (3.75 t/h) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, LCI dataset) |
| [`urea-1`](processes/urea-1/) | Urea by CO2 stripping, total recycle, prilling (2000 t/d, concept) | concept (calculation maturity: not recorded; not reviewed) | yes (BFD/PFD, flowsheet, no LCI dataset yet) |
| [`utility-chiller`](processes/utility-chiller/) | Chilled water at 6 degC, electric chiller (library utility; refrigerant losses not yet counted) | concept (Tier 1 form, design parameters ASSUMED; not reviewed) | no (manifest and LCI dataset only) |
| [`utility-cooling-tower`](processes/utility-cooling-tower/) | Cooling water, evaporative cooling tower, 25/35 degC (library utility) | concept (Tier 1 form, design parameters ASSUMED; not reviewed) | no (manifest and LCI dataset only) |
| [`utility-flare`](processes/utility-flare/) | Flaring of methane-rich waste gas (library utility) | concept (Tier 1 form, design parameters ASSUMED; not reviewed) | no (manifest and LCI dataset only) |
| [`utility-instrument-air`](processes/utility-instrument-air/) | Instrument air, dried, 8 bar(a) (library utility) | concept (Tier 1 form, design parameters ASSUMED; not reviewed) | no (manifest and LCI dataset only) |
| [`utility-steam-ng-boiler`](processes/utility-steam-ng-boiler/) | Steam, saturated 11 bar(a), natural-gas boiler (library utility) | concept (Tier 1 form, design parameters ASSUMED, combustion emissions from EPA AP-42; not reviewed) | no (manifest and LCI dataset only) |
| [`utility-wwtp`](processes/utility-wwtp/) | Wastewater treatment, activated sludge (library utility) | concept (Tier 1 form, design parameters ASSUMED; not reviewed) | no (manifest and LCI dataset only) |

Three separate axes, named as in core's [glossary](https://github.com/ChemE-as-Code/core/blob/main/docs/concepts/glossary.md):

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
`not comparable`, ADR 0016), the study `boundary`, and each link's factor `scope`.
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
