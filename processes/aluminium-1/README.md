# Primary aluminium by Hall-Heroult electrolysis

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of liquid primary aluminium tapped from point-feed prebake (PFPB) cells, from alumina, bought-in prebaked carbon anodes, aluminium fluoride and electricity.

## Why this route

Hall-Heroult electrolysis is the only industrial route to primary aluminium (2006 IPCC Guidelines, Vol. 3, section 4.4.1). Of its cell types, prebake dominates: point-feed prebake is about 90 % of EU capacity and Soederberg the rest (NFM BREF, Table 4.2), and the IAI's 2019 LCI report gives 95 % prebake worldwide. The cells run continuously for years; the metal is siphoned off periodically and the anodes are changed in rotation, so the potline is a continuous process with periodic tapping.

## How it is built

`lca/datasets/aluminium-prebake-electrolysis.yaml` is a hand-written Tier 1 dataset: every amount is the `formula` of its `parameters`, and `generation.balance` records the closed balance of Al, C, O and S.

| Item | Source | Value used |
|---|---|---|
| Alumina, net anode, AlF3, electricity | NFM BREF (2017), Table 4.9, p. 398 | midpoints: 1935 kg, 430 kg, 21.5 kg, 14 650 kWh per t |
| Anode sulfur | IPCC 2006 Vol. 3, Table 4.11 default (2 wt%) | model anode C130S (2.01 wt% S) |
| CO2, SO2 | anode carbon and sulfur to CO2 and SO2 (IPCC Equation 4.21 form) | 1544 kg, 17.3 kg per t |
| Oxygen from air | closes the balance (air burn and CO re-oxidation) | 242 kg per t, free |
| CF4, C2F6 | IPCC Tier 2 slope method (Equation 4.26, Table 4.16, CWPB) with the BREF's anode effects (0.1 to 0.5 per pot-day, 0.5 to 2 min) | 0.054 and 0.0065 kg per t |
| Gaseous fluoride, dust, NOx | NFM BREF 4.2.3.2.2, Table 4.13, 4.2.3.2.8 | 0.63 kg HF, 1.15 kg dust, 0.15 kg NO2 per t |
| Spent pot lining, wastewater | NFM BREF 4.2.3.4.1 and 4.2.3.3 | 35 kg, about 1 m3 per t |
| Alumina residual | closes the Al balance (ASSUMED) | 44 kg per t |

The CO2 is 1.54 t/t, inside the IPCC Tier 1 prebake factor of 1.6 t/t plus or minus 10 %. The SO2 from the IPCC sulfur default is 17.3 kg/t, inside the BREF's 10 to 25 kg/t. The electricity is inside the 13 to 20 kWh/kg of the US DOE report (2007). The PFC total of 0.06 kg/t is inside the BREF's 0.01 to 0.1 kg/t for modern plants, but that check shares its source with the anode effect figures. See `benchmarks/aluminium.yaml`.

## What is weak

- **Electricity dominates every impact, and its supply is not modelled.** The dataset links the default grid electricity at medium voltage. Smelters usually take power at high voltage, often from their own or contracted plants (hydro, coal or gas), which the source does not state. Link a smelter power mix explicitly before using a result.
- **PFCs are a calculation, not a measurement.** The anode effect figures are the BREF's ranges for modern plants, and the IPCC 2006 coefficients count high-voltage anode effects only. Low-voltage PFC emissions, added in the IPCC 2019 Refinement, were not read and are not counted. Older plants emit far more: the IPCC Tier 1 CWPB default is 0.4 kg CF4/t.
- The fluorine balance is not closed. Aluminium fluoride, HF, CF4 and C2F6 are outside the element balance, and the fluoride leaving in excess bath and spent lining is not stated.
- The alumina residual (44 kg/t) is a closing term. The source does not say where the alumina above stoichiometry goes.
- The anode's 0.4 wt% ash is counted as carbon. That raises CO2 by about 0.3 % against IPCC Equation 4.21 (1539 kg/t).
- The data are from industry submissions of 2008 and 2012, BREF citations of 1997 and 1998 (gaseous fluoride, NOx, anode effect performance) and IPCC coefficients measured up to 2005. `valid_until` is the reference year + 5, 2017, so it has already lapsed.
- Midpoints of ranges are our choice; the source does not recommend them. Uncertainty is `gsd2 = sqrt(high / low)` where the source gives a range (our convention), and ASSUMED elsewhere.

## Linking

Its product has the registry slug `aluminium`. Alumina links to `alumina-1` (`lca/mappings.yaml`). The anode and aluminium fluoride are reported mapping gaps, as are the dust, the alumina residual and the spent pot lining: no supplier, treatment or elementary flow is chosen. CF4, C2F6 and HF carry their biosphere3 names and UUIDs in the dataset.

## Not counted yet (TODO)

Anode production (baking fuel, pitch volatiles, packing coke), the casthouse, cathode and lining materials, particulate fluoride, freshwater intake, other site wastes and the Soederberg route. The full list is in the dataset's `system_boundary.excluded`.
