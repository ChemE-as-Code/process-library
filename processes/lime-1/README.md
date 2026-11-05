# Quicklime in a parallel flow regenerative kiln

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. The dataset covers 1 t of high-calcium quicklime, made by burning limestone in a natural-gas-fired parallel flow regenerative kiln (PFRK).

## Why this route

The CLM BREF (2013) reports the kiln mix for EU commercial lime in 2004. PFRKs made 46 % of it, more than any other kiln type, followed by annular shaft kilns at 16 % (section 2.1.3, p. 176). It also reports the fuels: gas supplied 64 % of PFRK fuel (Table 2.11, p. 186), so natural gas is the fuel modelled here.

A PFRK runs in production campaigns of several years. It has two shafts that swap between firing and preheating every 8 to 15 minutes, and stone is charged to each shaft in turn (section 2.2.7.2, p. 205). The plant produces lime continuously, so this is a continuous process, not a batch one.

## How it is built

`lca/datasets/quicklime-pfrk-natural-gas.yaml` is a hand-written Tier 1 dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed balance of Ca, C, O and H.

| Item | Basis | Source |
|---|---|---|
| Limestone, calcination CO2 | stoichiometry, 0.785 t CO2 per t CaO, applied to the product plus 3 % by-product lime | IPCC 2006 Vol. 3, Table 2.4; CLM BREF 2.3.4 (by-product 1 to 5 %, midpoint) |
| Fuel | 3.7 GJ/t, the midpoint of 3.2 to 4.2, burnt as methane | CLM BREF Table 2.23 and BAT-AEPL Table 4.6 |
| Electricity | 30 kWh/t, the midpoint of 20 to 40, kiln only | CLM BREF Table 2.23 |
| NOx, SO2 | 0.9 kg/t (midpoint) and 0.2 kg/t (low end, for gas firing) | CLM BREF 2.3.3.2, 2.3.3.3 |
| CO | 0.75 kg/t, the midpoint of the PFRK range 0.3 to 1.2 kg/t (100 to 400 mg/Nm3 at 3000 Nm3/t) | CLM BREF 2.3.3.4.2, p. 236 |
| Dust | 10 mg/Nm3 (fabric-filter BAT-AEL upper bound) at 3000 Nm3/t | CLM BREF Table 4.8, 2.3.3.2 |

The results per t are 1840 kg of limestone, 74 kg of natural gas, 809 kg of calcination CO2 and 203 kg of combustion CO2. The total CO2 is 1.012 t/t, inside the BREF's 0.987 to 1.210 t/t for PFRK lime. That agreement is partly by construction, because the heat range comes from the same document. The calcination CO2 of 0.809 t/t is above the IPCC Tier 1 default of 0.75 t/t. There are two reasons. The product is counted as pure CaO, while IPCC assumes 95 % CaO, and the by-product lime is calcined too. All four KPIs are in `benchmarks/cement-lime.yaml`.

## What is weak

- **The product and the stone are treated as pure.** Quicklime is counted as CaO and limestone as CaCO3. In reality, limestone is above 90 % CaCO3 and carries silica, alumina and iron (BREF Table 2.10). As a result, the rock mass bought is understated by a few per cent, and the residual CO2 in the lime (0.5 to 5 %) is left out.
- **One fuel only.** Natural gas, taken as methane, stands in for the whole PFRK fuel mix. Coal, petcoke, oil and waste fuels raise the combustion CO2, and with them SO2 and metals.
- Midpoints of ranges are our choice; the source does not recommend them. SO2 at the low end (for gas firing) and the fabric filter for dust are ASSUMED readings.
- The data are EU kilns of 2004 to 2008. `valid_until` is the reference year + 5, 2012, so it has already lapsed.
- Uncertainty: `gsd2 = sqrt(high / low)` where the source gives a range (our convention), ASSUMED values elsewhere.

## Linking

The product has the registry slug `calcium-oxide` and is counted per kg CaO. `alumina-1` (`feed:LIME`) and `kraft-pulp-1` (`feed:CAO`) count their lime in the same way, and both now link to this dataset in their own `lca/mappings.yaml`, as does `iron-steel-1` (`feed:lime`). `soda-ash-1` runs its own lime kiln and does not buy lime. Limestone links to the shared background `limestone` entry. Natural gas goes to the shared by-mass proxy and is not linked to an Atlas producer.

The build reports two mapping gaps. The first is the by-product lime, which has no cut-off decision for lime sent to other uses. The second is the kiln dust, because the source states no particle size.

## Not counted yet (TODO)

- Limestone impurities and moisture, and residual CO2 in the lime.
- Fuels other than natural gas.
- HCl, HF, TOC, PCDD/F and metals.
- Diffuse dust, and the electricity for crushing and screening.
- The refractory lining.
- Rotary, annular and mixed-feed shaft kilns, and dolime.

The full list is in the dataset's `system_boundary.excluded`.
