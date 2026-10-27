# Coverage roadmap

Which industrial products and processes the library covers, in which order and with which
technology variants. It turns "all industrial processes" into a plan that can be tracked
(process-library#47, part of the LCI gap analysis #43).

The source is [`coverage.yaml`](https://github.com/ChemE-as-Code/process-library/blob/main/coverage.yaml) (schema `schemas/coverage.schema.json`). The
catalog build reads it and writes `coverage.json`: each entry with the library processes that
cover it, plus a summary the Atlas can show ("N of the top 50 are covered, at these tiers").
The top 50 are the first 50 by `rank`, a judgement on the four criteria below, not by
production volume alone: most volumes are not sourced yet. `coverage.json` says so in
`summary.basis`.
The table below is generated from `coverage.yaml`. `tests/test_registry.py` checks that the two
agree.

## Ranking criteria

Entries are ranked by judgement on four criteria. No formula is applied, because most volumes
are not sourced yet:

1. **Global production volume**, as an order of magnitude only (Mt/a bands), each with its
   source. `n/a, to be sourced` means nobody has sourced it yet. It does not mean small. No
   precise figure is recorded.
2. **GHG and other burdens**: high where the cited sources show a large CO2, N2O or energy
   burden. Examples are N2O from nitric and adipic acid (IPCC 2006 Vol. 3), calcination CO2 in
   cement and lime, and the fossil hydrogen behind ammonia and methanol (IEA).
3. **Value-chain reach**: how many other entries an entry feeds (`feeds:`), and whether the
   Atlas graph needs it to connect processes. Examples: NH3 → HNO3 → AN, ethylene → EO → MEG,
   methanol → formaldehyde and acetic acid, ASU → N2/O2 for ammonia, EO, steel and e-fuels.
4. **Open sources**: EU BREFs (LVIC-AAF, LVIC-S, LVOC, CAK, POL, REF, CLM, IS, NFM, LCP, CWW,
   WI, WT), the IPCC guidelines, IEA reports and open reference flowsheets (IDAES HDA). These
   make Tier 1 or Tier 2 possible without licensed data. Sources are cited only. Nothing is
   copied from them (CLAUDE.md).

Utilities (steam, cooling water, wastewater treatment, demineralised water, refrigeration) are
ranked by reach rather than volume, because every process needs them (#45).

## Tiers

`tier` is the planned entry tier (core#182). **0** is stoichiometric, with the screening
defaults of Hischier et al. 2005, as reported in, capped in maturity (calculation maturity
`sourced`, design maturity at most `concept`) and DQR. **1** is sourced conceptual data (BREF
ranges, published balances). **2** is a flowsheet design (a ChemE-as-Code
project). Breadth (Tier 0/1) and depth (Tier 2) grow in parallel. An entry's `covered_by` gives
the tier each covering process reaches.

## Technology variants and market mixes

Each entry lists its technology variants. `market_mix: true` marks the variants a production or
consumption mix needs (#49). Examples: hydrogen from SMR, coal and by-product routes;
chlor-alkali from membrane and diaphragm cells; nitric acid with and without N2O abatement.
Emerging routes (PEM, alkaline and SOEC electrolysis, e-methanol, e-ammonia, DAC, plastic
pyrolysis, bio-ethylene) are variants or entries of their own. They are not in today's mixes.

## Route groups

Once a product has two or more routes, the catalog build compares them: `routes.json`
(`scripts/routes.py`, ChemE-as-Code/website#38) holds, per substance made, one row per process
and LCI dataset making it, with the technology, tier, design maturity and review status,
geography and year, the energy, feedstocks and key emissions per functional unit, the benchmark
KPIs and the footprint where the catalog keeps it (with the Monte Carlo interval of `lca/uncertainty.csv`).
Nothing is estimated for it: every value is read from the manifests, datasets and LCA files, and
a public build withholds a footprint exactly as it withholds the LCA.

The comparability of the routes is computed, criterion by criterion: the same reference product
(registry grade and state), functional unit, inventory boundary, system model, allocation, the
background data behind any impact numbers, and every route's TfS DQR within `DQR_SPREAD` (1.0,
ASSUMED: one step of the pedigree scale, a library convention, not a value from a standard) of
the best. A route that differs from most routes, or states nothing, carries the flag, so the
Atlas warns next to its row. The per-functional-unit inventory is unallocated, as KPIs are
reported: a co-product of a multi-output dataset gets none, since its share is the LCI build's
allocation. A comparative assertion disclosed to the public needs a critical review (ISO 14044);
the Atlas says so on every comparison. The test library is `tests/fixtures/routes/`.

## Families and ISIC

Every entry has a `family` from [`taxonomy/families.yaml`](https://github.com/ChemE-as-Code/process-library/blob/main/taxonomy/families.yaml), the same
taxonomy that `process.yaml` `families` is validated against. The taxonomy maps each family to
ISIC Rev.4 and NACE Rev. 2 classes, so coverage can also be reported by activity class.

## Next 10 (working plan, accepted 2026-10-25)

`next: true` marks the next batch. The list was accepted as the working plan on 2026-10-25
(#47). It is a plan, not a commitment: the order can change, and a change goes through
`coverage.yaml`.

1. **ammonia** (SMR): the first reactive process. It exercises element balances with carbon
   (core#174), combustion and flue gas outside the stream table (core#176), the CO2 co-product
   cut-off (decision 4) and steam and cooling water as library utilities (#45).
2. **hydrogen** (PEM and alkaline electrolysis; SMR as the reference variant).
3. **methanol** (natural gas; e-methanol as the variant that reuses the hydrogen and CO2).
4. **nitric acid**: N2O as a process emission (core#176) and the NH3 → HNO3 chain.
5. **urea**: consumes the ammonia plant's CO2 and closes the first fertiliser chain.
6. **chlor-alkali** (membrane): electricity-driven. Its sector PCR (Euro Chlor) overrides the
   allocation hierarchy, and it has a hydrogen co-product (energy allocation).
7. **steam generation**, 8. **cooling water** and 9. **wastewater treatment**: the utility
   datasets every process links to (#45). Cooling water replaces today's screening proxy.
10. **toluene HDA**: a case study with an open reference flowsheet (#42).

## The ranked list

| rank | id | product or process | family | volume (Mt/a) | GHG | variants | feeds | tier | covered |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `ammonia` **next** | Ammonia | ammonia | 100-1000 (iea-ammonia-2021) | high | smr, smr-ccs, coal-gasification, electrolytic | nitric-acid, urea, ammonium-nitrate, ammonium-sulfate, npk-fertilizers, acrylonitrile, caprolactam | 2 | - |
| 2 | `hydrogen` **next** | Hydrogen | hydrogen | 10-100 (iea-ghr-2023) | high | smr, smr-ccs, atr-ccs, coal-gasification, pem, alkaline, soec, by-product | ammonia, methanol, hydrotreating, hydrocracking, e-fuels, iron-steel, toluene-hda | 2 | - |
| 3 | `air-separation` | Oxygen, nitrogen and argon by air separation | air-separation | n/a, to be sourced | medium | cryogenic, psa-vsa, membrane | ammonia, ethylene-oxide, iron-steel, e-fuels, methanol | 2 | asu-1 (T2) |
| 4 | `ethylene` | Ethylene and propylene by steam cracking | olefins | 100-1000 (iea-petchem-2018) | high | naphtha, ethane, lpg, mto, bio-ethanol | ethylene-oxide, polyethylene, vcm, styrene, propylene-oxide, polypropylene, butadiene, btx | 1 | - |
| 5 | `methanol` **next** | Methanol | methanol | n/a, to be sourced | high | natural-gas, coal, e-methanol, biomass | formaldehyde, acetic-acid, mto-olefins, e-fuels | 2 | - |
| 6 | `nitric-acid` **next** | Nitric acid | nitric-acid | n/a, to be sourced | high | dual-pressure, mono-pressure, n2o-abatement | ammonium-nitrate, npk-fertilizers, adipic-acid | 2 | - |
| 7 | `urea` **next** | Urea | fertilizers | n/a, to be sourced | medium | co2-stripping, nh3-stripping | - | 1 | - |
| 8 | `chlor-alkali` **next** | Chlorine, caustic soda and hydrogen (chlor-alkali) | chlor-alkali | n/a, to be sourced | medium | membrane, diaphragm, mercury | vcm, propylene-oxide, mdi-tdi, hydrogen | 2 | - |
| 9 | `sulfuric-acid` | Sulfuric acid | sulfuric-acid | n/a, to be sourced | low | sulfur-burning, metallurgical | phosphoric-acid, ammonium-sulfate, titanium-dioxide, caprolactam | 1 | - |
| 10 | `cement-clinker` | Cement clinker | cement-lime | 1000-10000 (usgs-mcs-2024) | high | dry-kiln, dry-kiln-ccs | carbon-capture | 1 | - |
| 11 | `iron-steel` | Iron and steel | iron-steel | 1000-10000 (usgs-mcs-2024) | high | bf-bof, dri-gas-eaf, dri-h2-eaf, scrap-eaf | - | 1 | - |
| 12 | `refinery-distillation` | Crude oil distillation (atmospheric and vacuum) | refining | n/a, to be sourced | high | - | catalytic-reforming, hydrotreating, fcc, hydrocracking, ethylene | 1 | - |
| 13 | `steam-generation` **next** | Steam generation (boiler, CHP) | steam-and-heat | n/a, to be sourced | high | gas-boiler, chp, electric-boiler, heat-pump | ammonia, methanol, ethylene-oxide, styrene, bioethanol | 2 | utility-steam-ng-boiler (T1) |
| 14 | `ethylene-oxide` | Ethylene oxide and ethylene glycols | oxygenates | n/a, to be sourced | medium | oxygen-based, air-based, omega | pet | 1 | - |
| 15 | `polyethylene` | Polyethylene (HDPE, LLDPE, LDPE) | polyolefins | n/a, to be sourced | medium | hdpe-slurry, lldpe-gas-phase, ldpe-high-pressure | plastic-pyrolysis | 1 | - |
| 16 | `polypropylene` | Polypropylene | polyolefins | n/a, to be sourced | medium | - | plastic-pyrolysis | 1 | - |
| 17 | `propylene-pdh` | Propylene by propane dehydrogenation | olefins | n/a, to be sourced | medium | pdh, fcc, metathesis | polypropylene, propylene-oxide, acrylonitrile, cumene-phenol | 1 | - |
| 18 | `btx` | Benzene, toluene and xylenes | aromatics | n/a, to be sourced | medium | reformate, pygas, hda | styrene, cumene-phenol, terephthalic-acid, caprolactam, mdi-tdi | 1 | - |
| 19 | `soda-ash` | Soda ash | soda-ash | 10-100 (usgs-mcs-2024) | medium | solvay, trona, hou | - | 1 | - |
| 20 | `terephthalic-acid` | Purified terephthalic acid | oxygenates | n/a, to be sourced | medium | - | pet | 1 | - |
| 21 | `ammonium-nitrate` | Ammonium nitrate and calcium ammonium nitrate | fertilizers | n/a, to be sourced | medium | - | npk-fertilizers | 1 | - |
| 22 | `wastewater-treatment` **next** | Wastewater treatment (activated sludge) | wastewater-treatment | n/a, to be sourced | medium | - | - | 2 | utility-wwtp (T1) |
| 23 | `cooling-water` **next** | Cooling water system | utilities | n/a, to be sourced | low | - | air-separation, ammonia, methanol | 2 | utility-cooling-tower (T1) |
| 24 | `phosphoric-acid` | Phosphoric acid (wet process) | phosphoric-acid | n/a, to be sourced | low | dihydrate, hemihydrate | npk-fertilizers | 1 | - |
| 25 | `vcm` | Vinyl chloride monomer (balanced EDC process) | chlorinated-organics | n/a, to be sourced | medium | - | pvc | 1 | - |
| 26 | `pvc` | Polyvinyl chloride | polymers | n/a, to be sourced | medium | suspension, emulsion | - | 1 | - |
| 27 | `styrene` | Styrene (via ethylbenzene) | styrenics | n/a, to be sourced | medium | eb-dehydrogenation, po-sm | polystyrene | 1 | - |
| 28 | `pet` | Polyethylene terephthalate | polymers | n/a, to be sourced | medium | - | plastic-pyrolysis | 1 | - |
| 29 | `catalytic-reforming` | Catalytic reforming | refining | n/a, to be sourced | medium | - | btx, hydrotreating | 1 | - |
| 30 | `hydrotreating` | Hydrotreating and hydrodesulfurisation | refining | n/a, to be sourced | medium | - | sulfur-recovery | 1 | - |
| 31 | `fcc` | Fluid catalytic cracking | refining | n/a, to be sourced | high | - | propylene-pdh | 1 | - |
| 32 | `bioethanol` | Bioethanol | bioethanol | n/a, to be sourced | medium | corn-dry-mill, sugarcane, lignocellulosic | bio-ethylene, carbon-capture | 1 | - |
| 33 | `adipic-acid` | Adipic acid | oxygenates | n/a, to be sourced | high | - | - | 1 | - |
| 34 | `acetic-acid` | Acetic acid (methanol carbonylation) | oxygenates | n/a, to be sourced | low | - | - | 1 | - |
| 35 | `formaldehyde` | Formaldehyde | oxygenates | n/a, to be sourced | low | silver, metal-oxide | mdi-tdi | 1 | - |
| 36 | `propylene-oxide` | Propylene oxide | oxygenates | n/a, to be sourced | medium | chlorohydrin, hppo, po-sm | - | 1 | - |
| 37 | `butadiene` | Butadiene (C4 extraction) | olefins | n/a, to be sourced | low | - | - | 0 | - |
| 38 | `cumene-phenol` | Cumene, phenol and acetone | oxygenates | n/a, to be sourced | low | - | - | 0 | - |
| 39 | `carbon-capture` | CO2 capture and conditioning | carbon-capture | n/a, to be sourced | high | high-purity, amine-post-combustion, dac | e-fuels, methanol, urea | 1 | - |
| 40 | `lime` | Lime | cement-lime | 100-1000 (usgs-mcs-2024) | high | - | soda-ash, iron-steel | 0 | - |
| 41 | `aluminium` | Primary aluminium | aluminium | 10-100 (usgs-mcs-2024) | high | - | - | 0 | - |
| 42 | `npk-fertilizers` | NPK fertilisers | fertilizers | n/a, to be sourced | medium | nitrophosphate, mixed-acid | - | 0 | - |
| 43 | `ammonium-sulfate` | Ammonium sulfate | fertilizers | n/a, to be sourced | low | - | - | 0 | - |
| 44 | `toluene-hda` **next** | Benzene by toluene hydrodealkylation | aromatics | n/a, to be sourced | low | - | - | 2 | - |
| 45 | `e-fuels` | Synthetic fuels from H2 and CO2 (Fischer-Tropsch, methanol-to-fuels) | synthetic-fuels | n/a, to be sourced | high | rwgs-ft, mtj | - | 1 | - |
| 46 | `plastic-pyrolysis` | Plastic waste pyrolysis | chemical-recycling | n/a, to be sourced | medium | - | ethylene | 1 | - |
| 47 | `hydrocracking` | Hydrocracking | refining | n/a, to be sourced | medium | - | - | 0 | - |
| 48 | `sulfur-recovery` | Sulfur recovery (Claus) | sulfuric-acid | 10-100 (usgs-mcs-2024) | low | - | sulfuric-acid | 0 | - |
| 49 | `bio-ethylene` | Bio-ethylene by ethanol dehydration | bio-based-chemicals | n/a, to be sourced | medium | - | polyethylene | 0 | - |
| 50 | `waste-incineration` | Waste incineration with energy recovery | waste-treatment | n/a, to be sourced | medium | - | steam-generation | 1 | - |
| 51 | `caprolactam` | Caprolactam | nitrogen-organics | n/a, to be sourced | medium | - | - | 0 | - |
| 52 | `acrylonitrile` | Acrylonitrile (propylene ammoxidation) | nitrogen-organics | n/a, to be sourced | low | - | - | 0 | - |
| 53 | `mdi-tdi` | Isocyanates (MDI, TDI) | nitrogen-organics | n/a, to be sourced | medium | - | - | 0 | - |
| 54 | `polystyrene` | Polystyrene | polymers | n/a, to be sourced | low | - | - | 0 | - |
| 55 | `biogas` | Biogas and biomethane | biogas | n/a, to be sourced | medium | anaerobic-digestion, upgrading | steam-generation, hydrogen | 0 | - |
| 56 | `hydrogen-peroxide` | Hydrogen peroxide (anthraquinone process) | inorganic-chemicals | n/a, to be sourced | low | - | propylene-oxide | 0 | - |
| 57 | `titanium-dioxide` | Titanium dioxide | inorganic-chemicals | n/a, to be sourced | medium | sulfate, chloride | - | 0 | - |
| 58 | `power-generation` | Electricity generation (on-site and grid technologies) | power-generation | n/a, to be sourced | high | - | air-separation, chlor-alkali, hydrogen, aluminium | 0 | - |
| 59 | `demineralised-water` | Demineralised water | utilities | n/a, to be sourced | low | - | steam-generation, hydrogen | 1 | - |
| 60 | `refrigeration` | Refrigeration and compressed air | utilities | n/a, to be sourced | low | - | - | 0 | utility-chiller (T1), utility-instrument-air (T1) |
| 61 | `mto-olefins` | Methanol to olefins | olefins | n/a, to be sourced | high | - | polyethylene, polypropylene | 0 | - |

Volume sources (ids as in `coverage.yaml` `sources:`): `usgs-mcs-2024` U.S. Geological Survey,
Mineral Commodity Summaries 2024; `iea-ammonia-2021` IEA, Ammonia Technology Roadmap (2021);
`iea-ghr-2023` IEA, Global Hydrogen Review 2023; `iea-petchem-2018` IEA, The Future of
Petrochemicals (2018). The full source list is in `coverage.yaml`.

## Keeping it current

- Adding a process: add `covered_by: [{process: <id>, tier: <n>}]` to its entry. The build fails
  on an unknown process and warns when the process does not make the entry's product.
- Sourcing a volume: replace `band: "n/a"` with a band and a `source` id, and add the source to
  `sources:`.
- New entry or re-ranking: keep ranks contiguous, then regenerate the table above (the test
  says which rows differ).
