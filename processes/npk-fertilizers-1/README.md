# NPK 15-15-15 by the nitrophosphate (ODDA) route

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. The basis is one tonne of NPK 15-15-15 from phosphate rock digested in nitric acid. Calcium nitrate tetrahydrate (CNTH) is crystallised out and converted with ammonia and CO2 into ammonium nitrate and lime. Both are co-products, meant for CAN production (see Linking).

## How it is built

`lca/datasets/npk-nitrophosphate-odda.yaml` is a hand-written **Tier 0** dataset, a stoichiometric screening. Every amount is the `formula` of its `parameters`. `generation.balance` records the element balance, which closes over 11 elements.

| Item | Source | Standing |
|---|---|---|
| Rock | LVIC-AAF BREF Table 5.2 (Moroccan Khouribga: 33.4 % P2O5, 4 % F, 4.5 % CO2, 1.9 % SiO2) | the model rock of `phosphoric-acid-1`: 3 Ca10(PO4)6F2 + 4 CaCO3 + CaF2 + 5 SiO2 (33.6 % P2O5, 4.0 % F); the quartz (1.9 %) leaves as sand, the rest of the silica stands for the minor oxides and stays in the product |
| NP solution after crystallisation | EFMA BAT booklet No. 7 (2000), section 2.2.3: typical CaO/P2O5 0.25, 6 % NO3-N at 23 % P2O5 | sets how much Ca leaves as CNTH and how much free HNO3 there is |
| Product | grade 15-15-15, the booklet's reference grade (section 4) | modelled as NH4NO3, NH4H2PO4, CaHPO4, CaF2, KCl, the rock's residual silica and a dolomite filler (ASSUMED); the formula unit gives 15.000 % N, 15.000 % P2O5 and 14.998 % K2O |
| Feeds: 60 % HNO3, NH3, KCl, CO2 | stoichiometry of digestion, conversion and neutralisation | per t: 1.02 t acid, 0.20 t NH3, 0.24 t KCl, 0.15 t CO2, 0.45 t model rock (2.98 t per t P2O5) |
| Co-products | conversion CNTH + 2 NH3 + CO2 -> CaCO3 + 2 NH4NO3 + 3 H2O | 0.34 t CaCO3 and 0.42 t NH4NO3 per t, after 0.13 t AN is returned to the NPK |
| Electricity, steam, natural gas | BREF Table 7.3: AMI Linz and infoMil (2001), nitrophosphate route | midpoints of the two figures: 79.5 kWh, 240 kg steam, 12.4 kg CH4 per t |
| Compressed air | BREF Table 7.3, AMI Linz | 38 Nm3/t, a gap (no background) |
| Air emissions | EFMA section 8.1.1 for the acid and conversion units; AMI Linz combined scrubber (BREF Table 7.12) at 50 t/h for the NPK unit | NH3 0.24, NOx 0.31, HF 0.03 and dust 0.33 kg/t |
| Water emissions | EFMA sections 8.1.2 and 8.2.2 | N 0.38, P2O5 0.06 and F 0.135 kg/t |
| CO2 to air | rock calcite in the digestion, and the fuel | 54.8 kg/t |

The process runs as a continuous plant of typically about 50 t/h, integrated with ammonia, nitric acid and CAN plants (BREF 7.1 and 7.2.2). The CNTH crystallisers are an exception: the booklet describes a battery of batch crystallisers fed in turn, ahead of continuous filtration. Per tonne this makes no difference.

## What is weak

- **The rock is a mineral model**, the same as in `phosphoric-acid-1`. All P is fluorapatite, the excess fluorine is fluorite, all CO2 is calcite, and the rock's minor constituents (Al, Fe, Mg, Na, SO3, organics) are counted as silica. The rock per t of P2O5 (2.98 t) matches the Khouribga analysis (2.99 t) but is below the booklet's about 3.5 t, whose plant takes a leaner rock (`benchmarks/fertilizers.yaml`). P recovery is taken as complete: the nitrophosphate route has no gypsum to lose P to, and the 0.04 % to water is not added.
- **The dolomite filler (100 kg/t) is ASSUMED.** It stands in for every product component the model leaves out: the potash's NaCl, moisture and coating. The salt speciation is a model as well.
- **Utilities come from two figures of about 2001 (AMI Linz and Dutch infoMil notes), as reported in the 2007 BREF.** The two values differ by up to a factor of 2 (natural gas 116 kWh against 23 Nm3). Neither source says whether its figure covers the CNTH conversion and AN evaporation. `valid_until` (2007) has long lapsed.
- **NOx, HF and the water emissions are outside the element balance.** The feeds are not increased for them. They are below 0.2 % of the N and P fed, but about 1.2 % of the F.
- All net water is counted as vapour. Cooling water (17 m3/t), process and scrubbing water and the effluent volume are TODO.
- The emissions are BAT levels (an achievable level, not a measurement) mixed with one plant's measured loads.
- **Allocation.** The co-products are allocated by mass, as a recorded deviation, because there are no sourced prices. Mass gives the AN and the lime 43 % of every burden, including the potash, the filler, the dryer gas and the granulation that serve only the NPK. Subdivision would remove that, but the sources give the utilities only for the whole complex, so it would need an ASSUMED split of each (TODO). Allocation by nutrient content would give the NPK about 75 % instead of 57 %.

## Linking

The product has the registry slug `npk-fertilizer`. Ammonia links to `ammonia-1` and nitric acid (60 wt%, by mass of acid) to `nitric-acid-1`, both in `lca/mappings.yaml`. Phosphate rock, potassium chloride, dolomite, the CO2 feed and compressed air are reported gaps. Compressed air is counted in Nm3 at a pressure and dryness the source does not state, so it is not linked to `utility-instrument-air` (dried air at 8 bar(a), per kg).

The co-products are the AN solution (`ammonium-nitrate/solution`, counted as NH4NO3 contained) and precipitated `calcium-carbonate`. They are meant for CAN production, but nothing links them yet. `ammonium-nitrate-1`'s CAN dataset (`calcium-ammonium-nitrate-granulation`) makes its own AN solution and takes background limestone. A CAN dataset for a nitrophosphate complex, taking these co-products, is deferred (TODO).

## Not counted yet (TODO)

Cooling water, process water and effluent volume, the rock's minor constituents and trace metals, NOx-related HNO3 losses, coating agents, other grades and the mixed-acid route. The full list is in the dataset's `system_boundary.excluded`.
