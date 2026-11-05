# Hydrocracking of vacuum gas oil

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. The basis is one tonne of hydrocracked products, the LPG-to-diesel range taken as one product. They come from fresh vacuum gas oil (VGO) and hydrogen on a fixed-bed catalyst at high pressure. The unconverted oil is recycled to 97 to 98 % conversion.

## Route

The route is VGO hydrocracking, single stage with recycle. It is the main hydrocracker service the REF BREF describes: vacuum distillate is the main feed (section 2.13, p. 80). The BREF also covers once-through units (80 to 90 % conversion), two-stage units for heavy refractory feeds, mild hydrocracking and residue hydroconversion. None of these is modelled. Hydrocracking is a continuous fixed-bed process. The catalyst is regenerated off site every one to four years (section 3.13.2).

## How it is built

`lca/datasets/hydrocracking-vgo-single-stage-recycle.yaml` is a hand-written Tier 1 dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed C, H, O and S balance. The sources are the EU REF BREF (2015) and the IPCC 2006 Guidelines, Vol. 2. Their facts are written in our own form, and `parameters` gives the table or section for each.

Per tonne of fresh feed, from the REF BREF:

| Item | Value used | Source range |
|---|---|---|
| Hydrogen, chemical consumption | 330 Nm3/t (29.7 kg) | 260 to 400 Nm3/t, Table 3.62 |
| Fuel to the heaters | 800 MJ/t | 400 to 1200 MJ/t, Table 3.66 |
| Electricity | 85 kWh/t | 20 to 150 kWh/t, Table 3.66 |
| Sour water, and the wash water taken equal to it | 80 kg/t | 50 to 110 l/t, section 3.13.2 |
| Catalyst | 0.0574 kg/t | 57.4 t/Mt, section 3.13.2 |
| Unconverted-oil bleed | 2.5 % | 2 to 3 %, section 2.13 |
| C1-C2 gas | 1 % | "normally less than 1 %", section 2.13 |

Each midpoint is our choice. The source does not recommend one.

Per tonne of product, this gives 1.017 t of VGO, 30.2 kg of hydrogen, 16.3 kg of natural gas and 86 kWh of electricity. The co-products are 10.2 kg of C1-C2 gas and 25.4 kg of bleed. 11.1 kg of H2S goes to sulfur recovery, and 44.6 kg of CO2 comes from the heaters.

- **Element balance.** The feed and products are modelled as surrogate compounds, all ASSUMED:
  - VGO as C225H395S: 1.0 % S, the sulfur of the linked crude's vacuum gas oil (Johan Sverdrup assay, 375 to 565 degC cut, 1.00 wt%), and 12.7 % H (the assay gives none). The BREF's hydrocracker feeds of Table 3.62 carry 2 to 3 % S, and its hydrogen range is for them; this feed needs about 2 kg/t less hydrogen for its sulfur, well inside the range, so the midpoint is kept;
  - the product as tetradecane (C14H30);
  - the bleed as triacontane (C30H62);
  - the light gas as ethane.

  The carbon balance fixes the feed. All sulfur leaves as H2S. An explicit residual closes the hydrogen.
- **Fuel.** It is modelled as natural gas taken as methane, with complete combustion. That gives 54.9 t CO2 per TJ. Refinery fuel gas would give 57.6 t/TJ (the IPCC 2006 default), about 5 % more. CH4 and N2O use the IPCC 2006 defaults for gaseous fuels in energy industries (Vol. 2, Table 2.2).
- **Allocation.** The three products share the burdens by energy content (LHV), the hierarchy's rule for co-produced fuels. The values are IPCC 2006 default NCVs (Vol. 2, Table 1.2):
  - jet kerosene, 44.1 MJ/kg, for the unsplit product (ASSUMED);
  - refinery gas, 49.5 MJ/kg, for the light gas;
  - gas/diesel oil, 43.0 MJ/kg, for the bleed.

  The main product carries about 96 %. The rule is the curated entry `allocation.hydrocracking-1` in `lci/mappings.yaml` (rule physical-energy).

## What is weak

- **The product is not split** into LPG, naphtha, kerosene and diesel. No open source read for this entry gives a yield slate:
  - the REF BREF names the products but gives no split;
  - an open paper on an Iranian plant shows its yields only in figures (Sadighi et al. 2018, Int. J. Technol. 9:99);
  - the hydrocracker sections of the PRELIM documentation (University of Calgary, v1.5) name its yield correlations (after Gary et al. 2007) but print no values.

  A user who needs diesel or jet fuel alone cannot take it from this dataset.
- **Hydrogen closes with a small residual, by construction.** With these surrogates and the BREF midpoint, the hydrogen residual (`output:offgas`, to the refinery fuel gas) is 0.57 kg/t. That is a result of the choice of surrogates, not a measured purge. At 260 or 400 Nm3/t, the surrogates would need about 6.5 kg/t less or more hydrogen in the products. The product's hydrogen content (15.2 % for C14H30) is ASSUMED. Make-up hydrogen for solution and purge losses is not in the source and is not counted, so the hydrogen input is a lower view.
- **The data are old.** The utility figures come from Sema, Sofres 1991 and VROM 1999, and the hydrogen figures from Meyers 1997, all as cited by the BREF. `valid_until` (2004) has long lapsed.
- **Steam export is left out.** Table 3.66 gives 30 to 300 kg/t of steam produced. Under cut-off it would be a co-product. Its pressure is not stated, so it has no energy content for allocation. Leaving it out loads the products with all the burden.
- **Cooling water is left out.** The range is 10 to 300 m3/t, too wide for a midpoint to mean much.
- **No independent benchmark.** The three KPIs in `benchmarks/refining.yaml` (hydrogen, electricity and sour water per t of feed) record `no_open_reference`. The only open per-tonne ranges found are the REF BREF's, which are this dataset's own source, so they are not bound as references. A by-hand comparison with the US DOE refining profile of 1998 is in that file's header: about 17 to 42 kg/t of hydrogen and 870 MJ/t of fuel at an assumed VGO density. Both values agree with the dataset, but both sources cite Meyers 1997.
- **The ranges are wide.** Uncertainty is `gsd2 = sqrt(high / low)` where the source gives a range (our convention), and ASSUMED elsewhere. Electricity has gsd2 2.7 and fuel 1.7.

## Linking

- The main product has the registry slug `hydrocracked-products`. The feed is `vacuum-gas-oil`. The co-products are `refinery-fuel-gas` (the C1-C2 gas) and `unconverted-oil` (the bleed). All four are mixture entries without a composition.
- Hydrogen links to `hydrogen-1` (SMR, 99.9 mol%) explicitly. The BREF names a hydrogen plant as the hydrocracker's supplier (section 8.1.3); `catalytic-reforming-1`'s net gas is impure, another grade. Compression to reactor pressure is not counted.
- Vacuum gas oil links the vacuum unit of `refinery-distillation-1` explicitly; the feed's sulfur is that unit's crude's, so the link carries one crude. H2S (to sulfur recovery), the hydrogen residual to fuel gas (`output:offgas`), the catalyst and the spent catalyst are reported mapping gaps (`lca/mappings.yaml`); the H2S waits for the cut-off rule for acid gas sent to `sulfur-recovery-1`.
- Heater fuel: this entry, `hydrotreating-1` and `sulfur-recovery-1` burn methane in the dataset and take natural gas by mass; `catalytic-reforming-1` and `fcc-1` map fuel in kWh to natural-gas heat (combustion in the background); `refinery-distillation-1` keeps refinery gas a gap with its combustion in the dataset. No family rule (a refinery fuel gas entry) is decided yet.

## Not counted yet (TODO)

The following are not counted yet:

- the product split;
- make-up hydrogen losses;
- feed nitrogen and the ammonia it forms;
- H2S and NH3 in the sour water;
- heater NOx, SOx, CO and particulates;
- fugitive and vacuum-ejector VOC;
- steam export;
- cooling water;
- catalyst regeneration;
- hydrogen compression.

The full list is in the dataset's `system_boundary.excluded`.
