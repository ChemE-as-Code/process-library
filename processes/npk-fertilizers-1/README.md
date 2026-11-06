# NPK 15-15-15 by the nitrophosphate (ODDA) route

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. The basis is one tonne of NPK 15-15-15 from phosphate rock digested in nitric acid. Calcium nitrate tetrahydrate (CNTH) is crystallised out and converted with ammonia and CO2 into ammonium nitrate and lime. Both are co-products, which go to CAN production.

## How it is built

`lca/datasets/npk-nitrophosphate-odda.yaml` is a hand-written **Tier 0** dataset, a stoichiometric screening. Every amount is the `formula` of its `parameters`. `generation.balance` records the element balance, which closes over 11 elements.

| Item | Source | Standing |
|---|---|---|
| Rock | LVIC-AAF BREF Table 5.2 (Moroccan Khouribga: 33.4 % P2O5, 4.5 % CO2, 1.9 % SiO2) | modelled as 15 fluorapatite, 10 calcite and 3 quartz per rock unit (36.5 % P2O5); the other 5.6 % of the rock is not modelled |
| NP solution after crystallisation | EFMA BAT booklet No. 7 (2000), section 2.2.3: typical CaO/P2O5 0.25, 6 % NO3-N at 23 % P2O5 | sets how much Ca leaves as CNTH and how much free HNO3 there is |
| Product | grade 15-15-15, the booklet's reference grade (section 4) | modelled as NH4NO3, NH4H2PO4, CaHPO4, CaF2, KCl and a dolomite filler (ASSUMED); the formula unit gives 14.999 % N, 15.000 % P2O5 and 14.997 % K2O |
| Feeds: 60 % HNO3, NH3, KCl, CO2 | stoichiometry of digestion, conversion and neutralisation | per t: 0.99 t acid, 0.19 t NH3, 0.24 t KCl, 0.15 t CO2, 0.41 t model rock |
| Co-products | conversion CNTH + 2 NH3 + CO2 -> CaCO3 + 2 NH4NO3 + 3 H2O | 0.33 t CaCO3 and 0.40 t NH4NO3 per t, after 0.13 t AN is returned to the NPK |
| Electricity, steam, natural gas | BREF Table 7.3: AMI Linz and infoMil (2001), nitrophosphate route | midpoints of the two figures: 79.5 kWh, 240 kg steam, 12.4 kg CH4 per t |
| Compressed air | BREF Table 7.3, AMI Linz | 38 Nm3/t, a gap (no background) |
| Air emissions | EFMA section 8.1.1 for the acid and conversion units; AMI Linz combined scrubber (BREF Table 7.12) at 50 t/h for the NPK unit | NH3 0.24, NOx 0.31, HF 0.03 and dust 0.33 kg/t |
| Water emissions | EFMA sections 8.1.2 and 8.2.2 | N 0.38, P2O5 0.06 and F 0.135 kg/t |
| CO2 to air | rock calcite in the digestion, and the fuel | 54.8 kg/t |

The process runs as a continuous plant of typically about 50 t/h, integrated with ammonia, nitric acid and CAN plants (BREF 7.1 and 7.2.2). The CNTH crystallisers are an exception: the booklet describes a battery of batch crystallisers fed in turn, ahead of continuous filtration. Per tonne this makes no difference.

## What is weak

- **The rock is a mineral model.** Taking all P as fluorapatite and all CO2 as calcite leaves out 5.6 % of the rock (Al, Fe, Mg, Na, SO3, organics) and its excess fluorine. The model rock is therefore richer than real rock, and the rock per t of P2O5 (2.74 t) is below the 2.99 t of the Khouribga analysis and the booklet's about 3.5 t (`benchmarks/fertilizers.yaml`).
- **The dolomite filler (129 kg/t) is ASSUMED.** It stands in for every product component the model leaves out: the rock's minor oxides, the potash's NaCl, moisture and coating. The salt speciation is a model as well.
- **Utilities come from two figures of about 2001 (AMI Linz and Dutch infoMil notes), as reported in the 2007 BREF.** The two values differ by up to a factor of 2 (natural gas 116 kWh against 23 Nm3). Neither source says whether its figure covers the CNTH conversion and AN evaporation. `valid_until` (2007) has long lapsed.
- **NOx, HF and the water emissions are outside the element balance.** The feeds are not increased for them. They are below 0.2 % of the N and P fed, but about 1.2 % of the F.
- All net water is counted as vapour. Cooling water (17 m3/t), process and scrubbing water and the effluent volume are TODO.
- The emissions are BAT levels (an achievable level, not a measurement) mixed with one plant's measured loads.
- The co-products are allocated by mass, as a recorded deviation, because there are no sourced prices.

## Linking

The product has the registry slug `npk-fertilizer`. Ammonia links to `ammonia-1` and nitric acid (60 wt%, by mass of acid) to `nitric-acid-1`, both in `lca/mappings.yaml`. Phosphate rock, potassium chloride, dolomite, the CO2 feed and compressed air are reported gaps. The co-products `ammonium-nitrate` and `calcium-carbonate` are feeds of CAN, which has no entry on main yet.

## Not counted yet (TODO)

Cooling water, process water and effluent volume, the rock's minor constituents and trace metals, NOx-related HNO3 losses, coating agents, other grades and the mixed-acid route. The full list is in the dataset's `system_boundary.excluded`.
