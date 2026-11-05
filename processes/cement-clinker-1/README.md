# Cement clinker in a dry kiln with preheater and precalciner

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of grey Portland cement clinker from a dry rotary kiln with a cyclone preheater, a precalciner and a grate cooler. The kiln line is a continuous process; the BREF's emission data are yearly averages of continuous measurements.

## How it is built

`lca/datasets/cement-clinker-dry-kiln-precalciner.yaml` is a hand-written Tier 1 dataset: every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance.

| Item | Source | Value per t clinker |
|---|---|---|
| Calcination CO2 | IPCC 2006 Vol. 3, section 2.2.1.2: 65 % CaO, all from CaCO3, CKD factor 1.02 | 520 kg |
| Raw meal | stoichiometry of a model clinker formula (below) | 1184 kg CaCO3, 357 kg oxides of the clay and correctives |
| Kiln fuel | CLM BREF Table 1.18: midpoint of 3000 to under 4000 MJ/t | 3500 MJ (972 kWh), as petroleum coke (ASSUMED) |
| Fuel CO2, CH4, N2O | IPCC 2006 Vol. 2, Table 2.3 for petroleum coke | 341 kg, 10.5 g, 2.1 g |
| Electricity | CSI/ECRA Technology Papers 2017, Annex II (GNR-2014 reference plant) | 70 kWh |
| NOx, SO2, kiln dust | CLM BREF BAT-AEL midpoints times the BREF's 2300 Nm3/t | 0.75, 0.52, 0.035 kg |
| CO, mercury | CLM BREF Table 1.23 | 2.5 kg, 46 mg |

The clinker is modelled as `Ca325Mg14Si109Al34Fe12O626`, an integer formula of its five main oxides: 65.0 % CaO (IPCC default), 2.0 % MgO and the rest as SiO2, Al2O3 and Fe2O3 in the oxide ratio of the typical phases C3S 65, C2S 15, C3A 10, C4AF 10 %. Those phases and the 2 % MgO are the BREF's typical composition of grey Portland cement (Table 1.5, from CEMBUREAU), not of clinker; using them for clinker is ASSUMED. The formula is not phase-consistent: the phases imply about 68.5 % CaO, and the model oxides give Bogue phases of about C3S 41, C2S 36 % (lime saturation factor 0.87, a low-lime clinker). The calcination CO2 depends on the CaO only, so it stays the IPCC default. The raw meal is then CaCO3 plus the remaining oxides, so the element balance closes by construction. It does not check the data.

## What is weak

- **Fuel energy is the largest choice.** 3500 MJ/t is the middle of the BREF's range for this kiln type. It sits at the top of the CSI/ECRA range for five-stage kilns (3100 to 3500 MJ/t) and below the GNR-2014 world average of 3510 MJ/t. Optimised kilns reach 2900 to 3300 MJ/t.
- **The fuel is 100 % petroleum coke (ASSUMED).** EU kilns also burn coal and waste fuels, some of them biogenic. A fuel mix would change the fuel CO2 and the background, and biogenic CO2 would be reported separately. TODO.
- **The raw meal is low.** The model gives 1.54 t/t against 1.57 (BREF) and 1.55 (CSI/ECRA). It leaves out combined water, organic carbon and sulfur, and it supplies the 2 % MgO as an oxide, not as MgCO3. MgCO3 would add about 22 kg/t to both the raw meal (1.56 t/t) and the calcination CO2 (543 kg/t, against 536 for CSI/ECRA). The organic carbon (1.5 to 6 g/kg clinker, BREF 1.3.4.4.2) would add up to about 22 kg CO2/t. IPCC lets it be ignored below 5 % of the fuel heat.
- **Stack emissions are BAT-AEL midpoints, not measured averages.** SO2 depends mostly on the raw materials (BAT-AEL <50 to 400 mg/Nm3). The dust split into PM2.5, PM2.5-10 and PM10+ is the BREF's ESP example applied to any filter.
- Electricity is a world average applied to an EU kiln. The source gives 70 kWh/t clinker as 51 % of the plant's electricity without naming the steps; reading it as raw meal preparation, fuel grinding and kiln line is ASSUMED (the source's split gives 53 % for those).
- The BREF data are of about 2004 to 2008, so the reference year is 2008, as lime-1 takes its year from the same BREF's data (the BAT-AELs are of 2013 and the electricity of 2014). `valid_until` is the reference year + 5, 2013, so it has already lapsed.
- Midpoints of ranges are our choice, not the source's. Uncertainty is `gsd2 = sqrt(high / low)` where the source gives a range (our convention), and ASSUMED elsewhere.

## Linking

The product has the registry slug `cement-clinker`. Limestone links to the shared `limestone` background entry, electricity to the grid, and lost kiln dust to inert landfill (`lca/mappings.yaml`). Clay and correctives and the petroleum coke are reported mapping gaps. The coke is counted in kWh by net calorific value so that the fuel energy KPI can be checked (a KPI expression cannot turn kg into MJ); a background in kg would need a unit proxy with `ncv_pc`. The `dry-kiln-ccs` variant of the coverage entry `cement-clinker` would add a carbon capture process (coverage `carbon-capture`) taking the kiln gas: about 0.86 t CO2/t clinker, emissions `emission:CO2` and `emission:CO2-fuel`.

## Not counted yet (TODO)

SNCR reagent and ammonia slip, TOC, HCl, HF, PCDD/F and other metals, cooler and mill stack dust, diffuse dust, refractories and grinding media, water, a fuel mix with waste fuels, raw-meal organic carbon. The full list is in the dataset's `system_boundary.excluded`.
