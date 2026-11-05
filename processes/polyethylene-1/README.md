# High-density polyethylene by low-pressure polymerisation

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of HDPE pellets, from ethylene with 1-butene as comonomer and hydrogen for molecular-weight control, on Ziegler or chromium catalysts in continuous low-pressure reactors, followed by monomer and diluent recovery, extrusion and pelletising.

## How it is built

`lca/datasets/hdpe-low-pressure-eu-average.yaml` is a hand-written Tier 1 dataset: every amount is the `formula` of its `parameters`, and `generation.balance` records the closed C, H and O balance.

| Item | Source | Standing |
|---|---|---|
| Electricity, net thermal energy, hydrogen, diluent make-up, CO2, CO, CH4, NOx, SO2, PM10, ethylene to air | Plastics Europe eco-profile of polyolefins (2026), Table 5, HDPE column | 12-month averages of 2011 from 19 European HDPE units, measured by the producers |
| Effluent | same report, Table 8 | after the plants' own treatment |
| 1-butene | branch count of HDPE in the same report (p. 6), 3 to 5 per 1000 C, midpoint 4 | 16 kg/t; 1-butene as the comonomer is ASSUMED (the BREF POL names butene-1 and hexene-1) |
| Ethylene | stoichiometry | the polymer less the 1-butene units, plus ethylene to air, plus the ethylene whose carbon leaves as the sourced CO2, CO and CH4 once the burnt diluent is taken off |
| Combustion oxygen and water | stoichiometry | complete combustion of the purge and vent gases at a flare or thermal oxidiser (ASSUMED) |

The eco-profile is an open report (PDF) of Plastics Europe. Only its gate-to-gate polymerisation table was used. Its aggregated cradle-to-gate results and ILCD datasets were not used.

The ethylene comes out at 989.8 kg/t, so ethylene plus 1-butene is 1005.8 kg/t. The eco-profile states 1.00 kg/kg ethylene, rounded to two decimals, so at least 995 kg/t. The stoichiometric figure is therefore 5 to 15 kg/t (0.5 to 1.5 %) below the source's own value: ethylene that leaves in ways the source does not itemise (wastes, hydrocarbons to air other than ethylene and methane). The BREF POL's 1999 data collection gives 1008 to 1066 kg/t for HDPE monomer consumption, so the dataset is 2 kg/t below that range (`benchmarks/polyolefins.yaml`, explained). Electricity and heat add up to 806 kWh/t, inside the BREF's 570 to 940 kWh/t direct energy. Both checks come from industry data collections with producers in common, and they cover a different period, so they are not checks against independent plants.

## What is weak

- **It is not the slurry route alone.** Both sources average every HDPE plant, slurry (loop and stirred tank) and gas phase together. Only the diluent, taken as isobutane, is specific to the slurry route. The pedigree's technological score says so.
- **The heat is net.** The eco-profile gives "thermal energy (net)", 1.345 MJ/kg, without its gross import and export. It may embed a credit for exported heat, which docs/system-model.md section 2 does not allow. This is a recorded deviation (dataset `modelling`). It is counted as steam heat, which is ASSUMED.
- **The hydrocarbon losses are a lower view.** The source reports ethylene and methane to air, 0.26 kg/t together. The BREF gives 0.65 to 5.75 kg/t of VOC for HDPE plants. The diluent loss is burnt in the model (ASSUMED). The VOC KPI is outside its range, with the reason recorded.
- The PM10 of 1.4 g/t from the eco-profile is far below the BREF's HDPE dust, 56 to 175 g/t (Table 3.11; Germany 16 to 30 g/t, Table 3.12). PM10 is only part of the dust, but the gap is large and not explained by the sources. No KPI checks it.
- The CO2 of 35 kg/t is the source's process emission without on-site energy production. Reading it as combustion of purge and vent gases is ASSUMED, and so are the hydrogen and diluent being burnt.
- The effluent is linked to a treatment activity although the source's figure has passed the plants' own treatment. Treatment is counted twice, which is conservative, and the source's COD (0.035 kg/t) is not added. Water input is ASSUMED equal to the effluent (1.6 t/t; the withdrawal is 1.5 t/t).
- The source gives averages without ranges. Uncertainty is ASSUMED where it states no range, and for electricity and heat it comes from the spread of the BREF's direct energy.
- The data are 2011 (a 2020 survey of the producers found no major change). `valid_until` is the reference year + 5, 2016, so it has already lapsed.

## Linking

The product has the registry slug `polyethylene` (new, with no grade split yet). `feed:ethylene` links ethylene-1's polymer-grade ethylene explicitly, as ethanol-1 does. ethylene-1 cracks ethane, while the European plants behind this dataset are mostly fed by naphtha crackers. Hydrogen links the shared background entry (`atlas: false`): hydrogen-1 and chlor-alkali-1 both make it, and the supplier is not chosen here. 1-butene and isobutane are reported mapping gaps: no Atlas process makes them and the shared vocabulary has no entry (`lca/mappings.yaml`). PM10 is a gap too, because core's elementary-flow crosswalk has PM2.5 only.

## Not counted yet (TODO)

Cooling water (8.6 t/t withdrawn, but no duty in kWh), catalysts and cocatalysts (0.26 kg/t of inorganics), other organic auxiliaries such as additives and aluminium alkyls (about 6 kg/t), propylene (0.02 kg/t), process wastes (about 2.2 kg/t), purge and conveying nitrogen, and hydrocarbons to air other than ethylene and methane. LLDPE and LDPE are not modelled. The full list is in the dataset's `system_boundary.excluded`.
