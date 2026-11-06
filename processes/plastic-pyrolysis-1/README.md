# Plastic waste pyrolysis to raw pyrolysis oil

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

This folder has a manifest and an LCI dataset only, with no flowsheet and no simulation. The basis is one tonne of raw (not upgraded) pyrolysis oil made from sorted, pretreated mixed polyolefin (PE and PP) waste by continuous thermal pyrolysis. Part of the non-condensable gas is burnt to heat the reactor. The rest of the gas leaves as a co-product, and the char leaves as a residue. After upgrading, the oil is a naphtha substitute in steam crackers, which is how this entry feeds `ethylene` in `coverage.yaml`.

## Why this route

- **Pyrolysis is the main chemical recycling technology in Europe.** It is 71 to 90 % of installed capacity in the counts that JRC 2026 collects (EUR 40766, Table 3, p. 19).
- **Its feed is mixed polyolefins.** JRC 2026 (section 5.2, p. 42) notes that most processes take MPO and treat other plastics as contaminants. Its model runs from mixed plastic waste to a naphtha-equivalent output. This dataset covers only the pyrolysis step (unit operation 4 of its Table 6).
- **Plants are fed continuously.** JRC 2023 (EUR 31423, section 3.4.4) names continuous feeding of the viscous melt as the first design challenge. Of the reactor types it lists, only fluidised beds and screw kilns are free of scale-up problems, and both run continuously. Small vendor-built batch units exist, but they are not modelled here. The sources do not give each plant's operating mode, so "continuous" describes the scalable designs and does not come from a plant census.
- **The WT BREF does not cover this process.** The `bref-wt` source named in `coverage.yaml` leaves pyrolysis out of its scope and points to the WI or LCP BREF (EUR 29362, doi:10.2760/407967, Scope, pp. xxvii-xxviii). This entry therefore does not cite it for any number.

## How it is built

`lca/datasets/plastic-pyrolysis-mixed-polyolefins.yaml` is a hand-written Tier 1 dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed C/H/O balance.

| Item | Source | Value |
|---|---|---|
| Oil yield | JRC 2026, Annex A.5, p. 99: literature and stakeholder data converge on 67 to 71 % | 0.69 kg oil per kg feed, so 1449 kg feed per t oil |
| Process heat | JRC 2026, Annex A.5, p. 99, reporting Netsch et al. (2024): 4 to 6 % of the feed's calorific value in theory, about 10 % in real reactors | 10 %, read as fuel fired (ASSUMED reading) |
| Feed calorific value | JRC 2023, section 3.2.2.1.4: PE film waste bales about 34 GJ/t | 34 MJ/kg, a proxy (ASSUMED) |
| Gas fired | the heat over the IPCC NCV of ethane (46.4 TJ/Gg, IPCC 2006 Vol. 2 Table 1.2) | 106 kg/t |
| Electricity | Benavides et al. 2017, Table 1: 87 % of 1775 MJ purchased energy per t of liquid, median of five US companies | 429 kWh/t |
| CH4, N2O from firing | IPCC 2006 Vol. 2 Table 2.3, refinery gas in manufacturing: 1 and 0.1 kg/TJ | 4.9 g and 0.49 g per t |
| Gas and char split | element balance of model compounds: feed (CH2)n, oil C10H20, gas C2H6, char C (all ASSUMED) | 321 kg gas (215 kg exported), 128 kg char |

The CO2 comes from the carbon of the gas fired, 311 kg/t, which is 63.1 t/TJ. That sits inside IPCC's range for ethane (56.5 to 68.6 t/TJ). The char of the model compounds comes out at 8.85 % of the feed. The median of the US survey is 9 wt% (Benavides et al. 2017, section 3.3). That survey is not where the char figure comes from, but the agreement is loose, because both depend on how contaminated the feed is.

## What is weak

- **Electricity is a US figure for a different product.** It covers pretreatment, pyrolysis and on-site upgrading to diesel and naphtha at small plants of about 2016. It is taken per tonne of raw oil, so it is an upper view. No second open figure was found (`benchmarks/chemical-recycling.yaml`).
- **Purchased electricity and own gas fired are added together.** This follows the survey's base case, in which the plants fire their own fuel gas for the process heat and buy the 1775 MJ on top (Benavides et al. 2017, sections 3 and 3.3, Tables 1 and 2). The survey does not say how much of the purchased electricity heats the reactor. If some of it does, the heat is counted twice. The electricity is then high, or the gas fired and its CO2 are high.
- **The CO2 and the water from firing carry pedigree 4.** They depend on the ASSUMED reading of the heat share and on the proxy calorific value, the same as the CH4 and N2O.
- **The heat share is reported through JRC 2026, not read in Netsch et al. (2024).** The feed's calorific value is a proxy taken from sorted PE film bales. Pure polyolefin has more, so the gas fired and its CO2 may be low.
- **The feed is modelled as pure (CH2)n.** Moisture, PET, PVC, fillers and other contaminants are left out. So is their chlorine, oxygen and metal, together with their fate. A real feed gives more char and gas and a contaminated oil.
- The products are model compounds that close the balance. Real oil is a C5 to C30+ mixture.
- **The yield is a central value of a narrow consolidated range.** Companies report 65 to 82 %, which JRC 2026 calls unverified. The US survey gives 60 to 80 % liquid after upgrading. The dataset sits inside that range, which serves as the bound KPI reference.
- **Allocation is by mass between the oil and the exported gas.** This is a recorded deviation in the dataset's `allocation`. Neither prices nor heating values of the two products come from an open source here.
- `valid_until` is 2030. The electricity data are older than the 10-year limit for secondary data.

## Linking

- **Feed:** the waste is `free`. Under the cut-off model it enters without burden, and collection, sorting and pretreatment belong to the waste system.
- **Electricity:** linked to the medium-voltage grid by `link.factor`.
- **Char:** a reported gap, because its fate is not decided. Landfill and energy recovery are treated differently under cut-off.
- **Oil:** no Atlas process consumes it yet. `ethylene-1` cracks ethane, not naphtha. A naphtha cracker or an upgrading entry would link to `product:plastic-pyrolysis-oil` explicitly.
- **Registry slugs:** `mixed-polyolefin-waste`, `plastic-pyrolysis-oil`, `plastic-pyrolysis-gas` and `pyrolysis-char`, all mixtures without a composition.

## Not counted yet (TODO)

- Natural gas, which is 13 % of the survey's purchased energy.
- NOx, CO, particulates and HCl from the firing.
- Nitrogen for inerting.
- Cooling water.
- Water and wastewater from feed moisture and washing.
- Heteroatoms of real waste.
- The fate of the char and of the exported gas.
- Upgrading of the oil.

The full list is in the dataset's `system_boundary.excluded`.
