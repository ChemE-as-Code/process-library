# Fluid catalytic cracking of vacuum gas oil

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. It covers one tonne of fresh gas-oil feed cracked on zeolite catalyst, with the coke burnt off in a single-stage, full-combustion regenerator. The REF BREF says full combustion is typical for vacuum distillate feeds (section 2.5). FCC is a continuous process: the catalyst circulates between riser and regenerator and is regenerated all the time.

## How it is built

`lca/datasets/fcc-vgo-full-combustion.yaml` is a hand-written **Tier 1** dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed C, H and O balance. Facts are in our own form, and each one cites its table in `parameters`.

| Item | Source | Standing |
|---|---|---|
| Gasoline, C3/C4 cut, dry gas and coke yields | Jechura (2019), CBEN 409 course notes, slide 16. This is a worked example of the Gary et al. zeolite correlations at 72 vol% conversion, with a 25 degAPI feed of Watson K 12.0 | one textbook-correlation case, not plant data |
| Light and heavy cycle oil | close the C and H balances | 206.96 and 77.34 kg/t, against 206.0 and 78.4 in the example |
| Hydrogen contents of the lumps | PRELIM v1.0, Table 8: gasoline 14.5, LGO 9.8, HGO 8.0, coke 5.9 wt% | used to pick ASSUMED integer pseudo-formulas |
| Electricity, fuel, steam, cooling water, catalyst, sour water | REF BREF Table 3.33 and section 3.5.2.2 | midpoints of the FCC ranges (our choice) |
| CO, NOx, SOx, particulates | REF BREF Tables 3.34, 3.36 and 3.37 | midpoints, and the 20-unit average for particulates |
| Coke-burn CO2 and water | carbon and hydrogen of the coke (C4H3) | 168.5 kg CO2/t, inside the BREF's 160 to 220 kg/t (`benchmarks/refining.yaml`) |
| CH4, N2O from the coke burn | IPCC 2006 Vol. 2, Table 2.2 (petroleum coke, which includes catalyst coke by Table 1.1), at the BREF's 38 to 40 MJ/kg coke | defaults |
| Allocation default | energy, with IPCC 2006 Vol. 2 Table 1.2 NCVs, the curated rule `allocation.fcc-1` in `lci/mappings.yaml` | the inventory stays unallocated |

**The direct CO2 is the coke burn.** The BREF says virtually all of the unit's heat is generated in the regenerator, by burning coke off the catalyst, and that coke is fossil carbon from the feed. The fired fuel of Table 3.33 is counted separately, as purchased heat. The dataset computes the CO2 from the coke's carbon, not from the BREF's CO2 range. The coke yield, 4.9 wt%, sits just below the notes' "normal 5 to 8 %" (slide 27). A residue feed, or a deeper conversion, burns more coke.

## What is weak

- **The yields are one worked example.** Product slates move with feed quality, conversion and catalyst. No open plant dataset of FCC yields was found.
- **The pseudo-formulas are a balance device.** Each lump is a mixture, given one integer formula near the hydrogen content its source reports. The feed's C41H73, at 13.0 wt% H, was chosen so that the closed LCO/HCO split stays within 1.5 % of the example. PRELIM takes 12.5 wt% for a hydrotreated feed. The LCO/HCO split is sensitive to these choices.
- **Sulfur and nitrogen are not balanced.** SO2 and NOx come from the BREF's emission factors per m3 of feed, converted at the example's specific gravity of 0.9042. The H2S stays inside the dry gas.
- **Utilities are midpoints of wide ranges.** Fuel is 120 to 2000 MJ/t, counted as natural-gas heat, a proxy for refinery fuel gas. Its midpoint, 1060 MJ/t, is probably high for a full-combustion unit, whose heat comes almost all from the regenerator (the BREF's own statement under the table); the range is given alike for FCC and RCC, and no open feed-heater duty was found. The sour water (75 kg/t) exceeds the steam (60 kg/t); the rest, overhead wash water in practice, has no input in the inventory. The steam is gross: the 40 to 60 kg/t the unit raises and any expander power are not credited (cut-off model).
- The IPCC N2O default may be low where a platinum CO promoter is used (BREF p. 53).
- The particulates have no flow identity, because their size split is not stated, so they are a reported gap.
- Most of the KPIs share their source with the dataset, so they record `no_open_reference`. Only the CO2 check is bound to a range (`benchmarks/refining.yaml`).
- **Heater fuel is counted differently across the refining entries.** Here and in `catalytic-reforming-1` the fuel is in kWh on the shared natural-gas heat entry, whose combustion is in the background; `hydrotreating-1`, `hydrocracking-1` and `sulfur-recovery-1` burn methane in the dataset, and `refinery-distillation-1` keeps refinery gas a gap with its combustion in the dataset. No family rule (a refinery fuel gas entry) is decided yet, so direct CO2 per t is not comparable across them. The shared entry counts heat absorbed, and the dataset books the fuel fired, so the heat is an upper view.
- The sources are EU units of 1997 to 2010 and a US textbook basis. `valid_until` is 2015, so it has already lapsed.
- Uncertainty is `gsd2 = sqrt(high / low)` where the source gives a range (our convention), and ASSUMED values elsewhere.

## Linking

The products have the registry slugs `fcc-gasoline`, `liquefied-petroleum-gas`, `refinery-fuel-gas`, `light-cycle-oil` and `heavy-cycle-oil`, all mixtures added with this entry. The C3/C4 cut carries its sourced composition on the exchange: about 23 wt% propylene, or 3.3 wt% of the feed. It is not offered as `propylene`, because a propylene recovery unit (C3 splitter) would have to be added first. The feed `vacuum-gas-oil` links the vacuum unit of `refinery-distillation-1` explicitly; the catalyst and the spent catalyst are reported gaps (`lca/mappings.yaml`).

## Not counted yet (TODO)

These are not counted yet: steam and power exported from the waste heat or CO boiler, the sulfur and nitrogen of the products, regenerator hydrocarbons, aldehydes and NH3, the metals, dioxins and PAH in the particulates, sour-water organics, fugitives, feed hydrotreating, and the RCC and partial-combustion variants. The full list is in the dataset's `system_boundary.excluded`.
