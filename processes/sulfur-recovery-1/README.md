# Sulfur recovery by the modified Claus process

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of liquid sulfur, from the H2S of a refinery acid gas, in a modified Claus unit with a catalytic direct oxidation tail gas stage (SuperClaus type) and a thermal incinerator.

## Why this route

Recovered sulfur is a by-product of removing H2S from natural gas and refinery streams. US EPA AP-42 (section 8.13.1) puts 90 to 95 % of recovered sulfur on the Claus process. USGS MCS 2024 (pp. 172-173) says most sulfur comes from processing fossil fuels, and in the US from refineries, gas plants and coking plants in that order. The Claus unit runs continuously: its furnace, waste heat boiler and catalytic stages work in steady state on the acid gas from the amine regenerators. Catalytic direct oxidation is the largest tail gas category in the BREF's recovery measurements (26 of 61 data sets, Table 4.89) and in its eight-unit sample (5 of 8, Table 4.103), so the dataset models that category. In the 47-site installed base (Figure 3.36) SuperClaus is the most frequent single tail gas process (10 sites, our count of the figure), but the amine-based units together (SCOT, HCR, RAR: about 12) are more, and about a third of the sites run Claus with no tail gas unit. The choice is therefore a representative middle, not the majority configuration.

## How it is built

`lca/datasets/sulfur-claus-catalytic-oxidation-tgtu.yaml` is a hand-written Tier 1 dataset: every amount is the `formula` of its `parameters`, and `generation.balance` records the closed S, H, C and O balance. The sources are the EU REF BREF (2015) and US EPA AP-42 section 8.13. Facts are in our own form, each with its table in `parameters`.

| Item | Value per t S | Source |
|---|---|---|
| Recovery | 98.5 %, so 1079 kg H2S in and 30.4 kg SO2 out | REF BREF Table 4.89: median for catalytic direct oxidation; also the EU installed-base median (section 3.23.2) |
| Fuel | 1300 MJ, as 26.0 kg methane, giving 71.3 kg CO2 | REF BREF Table 4.85: midpoint of 1000 to 1600 MJ/t |
| Electricity | 67.5 kWh | REF BREF Table 4.85: midpoint of 60 to 75 kWh/t |
| Steam | 1750 kg produced, all taken as exported (ASSUMED), a co-product | REF BREF Table 4.85: midpoint of 1500 to 2000 kg/t |
| Cooling water | 10 m3 at a 10 K rise, 116 kWh of heat | REF BREF Table 4.85: midpoint of 0 to 20 m3/t |
| NOx, CO, hydrocarbons | 0.11, 0.65, 0.02 kg | AP-42 Table 8.13-2, factors per sulfur produced |

Every sulfur atom that misses the pit leaves the incinerator as SO2, as AP-42 assumes for its factors. The oxygen comes from free ambient air. The water from the H2S and the fuel goes to the stack.

## What is weak

- **The steam has no pressure and no burden.** The BREF gives kg/t of steam produced only; that none of it is used inside the unit (reheaters, sulfur pit and line heating) is ASSUMED. AP-42 says the waste heat boiler raises high- to medium-pressure steam, without amounts. The hierarchy in docs/system-model.md would allocate it by exergy or energy, which needs its state. The dataset gives all burdens to the sulfur (shares 1/0, recorded as a deviation), as sulfuric-acid-1 does for its steam.
- **The acid gas is H2S only.** A real feed also carries CO2, NH3 from sour water stripper gas, hydrocarbons and water. These change the air, the fuel and the stack gas, and their CO2 passes through. The REF BREF's one site example (Table 3.88) reports 283 kg CO2/t and 1460 kWh of fuel per t, both well above this dataset. The dataset is a lower view of the energy and of the direct CO2.
- The utility ranges are for one 20 000 t/yr SRU whose configuration the BREF does not state. Midpoints are our choice. AP-42's NOx, CO and hydrocarbon factors are US source tests, not EU data.
- The recovery is a daily-average median. Units differ widely: 95.5 to 99.3 % for this tail gas category. The SO2 moves by about 7 times across that range.
- The data are from 2004 to 2012. `valid_until` is the reference year + 5, 2015, so it has already lapsed.
- Uncertainty is `gsd2 = sqrt(high / low)` where the source gives a range (our convention), and ASSUMED elsewhere.

## Linking

The product is the registry's `sulfur`, but the main product carries no `inventory_key` on purpose. With one, the LCI build would switch the sulfur feeds of `sulfuric-acid-1` and `thionyl-chloride-1` from the background market to this plant gate. There is no sulfur market yet, and this dataset's H2S feed is still a gap. Those processes should decide that link in their own `lca/mappings.yaml`. Adding the key is a one-line change once they do.

The H2S feed (`hydrogen-sulfide`, added to the registry with this entry) is a reported mapping gap. No Atlas process makes acid gas: `natural-gas-processing-1` treats a gas with no H2S. Natural gas is not linked to an Atlas producer, as in `styrene-1`.

## Benchmarks

`benchmarks/sulfuric-acid.yaml` has four KPIs, two with an independent reference:

- **Recovery**: checked against AP-42's 99 to 99.9 % for Claus plants with tail gas treatment. The dataset sits below that range, with an explanation. The BREF's 95.5 to 99.3 % for the modelled category is recorded as a second reference, but it is not independent.
- **NOx**: checked against the BREF's site example, which is independent of the AP-42 factor the dataset uses. The dataset sits below it, with an explanation.
- **Electricity and steam**: no independent open source was found, so both record `no_open_reference`. The only open figures are the BREF table the dataset takes its midpoints from. The steam entry also records a rough stoichiometric upper bound of about 2.4 t/t, from AP-42's 80 % heat recovery.

## Not counted yet (TODO)

- Acid gas components other than H2S.
- COS, CS2, H2S and sulfur slip, which are counted as SO2.
- Claus and oxidation catalysts.
- Sour water from knock-out drums.
- Particulates.
- Sulfur degassing, storage and loading.
- Boiler blowdown.

The full list is in the dataset's `system_boundary.excluded`.
