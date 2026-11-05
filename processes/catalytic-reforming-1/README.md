# Catalytic reforming of naphtha (CCR)

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of C5+ reformate, from hydrotreated heavy naphtha in a low-pressure moving-bed reformer with continuous catalyst regeneration (CCR). Hydrogen, LPG and fuel gas are co-products.

## Route

CCR is the route modelled. The REF BREF (section 2.6) says that only continuous units are built today, and that new units above about 2 400 m3/d are typically CCR. The reactors run continuously; the catalyst moves through them and is regenerated in a loop, so the coke burn-off is a continuous vent too. Semi-regenerative units (also continuous in operation, with off-line regeneration every 3 to 24 months) and cyclic units are not modelled.

## How it is built

`lca/datasets/catalytic-reforming-ccr.yaml` is a hand-written Tier 1 dataset: every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance.

| Item | Source | Standing |
|---|---|---|
| Hydrogen, 350 Nm3 per t feed | REF BREF 2015, section 2.6, p. 57 | "around" one value for CCR units; counted as pure H2 |
| Electricity, fuel fired, cooling water | REF BREF Table 3.42, p. 171, midpoints of the ranges for all reformer types | sources of 1997 to 2000 |
| Coke burnt off, 0.05 to 0.5 kg/t | REF BREF section 3.6, p. 171 | burnt to CO2, the coke taken as carbon |
| Waste water, 1 to 3 L/t | REF BREF section 3.6, p. 172 | only units with a vent scrubber |
| Catalyst, 1.35 t per Mt/yr | REF BREF Table 3.42 | read as the yearly make-up |
| Pt and Sn, 0.3 wt% each | Hameed 2017, Table 1 | one industrial CCR catalyst |
| C1 + C2, 3.18 wt% of feed | US 8,668,824 B2, Table B, run 1 (standard CCR) | a simulation from pilot plant data, at 1300 kPa |
| LHVs for allocation | IPCC 2006 Vol. 2 ch. 1 Table 1.2; registry for H2 | reformate taken as motor gasoline |

**The balance.** A reformer's feed and products are mixtures, so the element balance uses pseudo-components (ASSUMED): naphtha C7H14 (14.4 wt% H), reformate C10H14 (10.5 wt% H, an aromatics-rich lump), LPG C7H18 (one mole each of propane and butane) and fuel gas C3H10 (methane plus ethane). With the sourced hydrogen, fuel gas and coke, the feed follows from the hydrogen balance and the LPG closes the mass balance. This gives 1188 kg of naphtha per t of reformate, a C5+ yield of 84.2 wt%, and 94 kg of LPG per t of feed. The C5+ yield sits in UOP's 82 to 86 wt% for CCR Platforming. That is not an independent check, because the reformate formula was chosen for that hydrogen content. The patent's run 1 gives 87.4 wt% at a higher pressure (`benchmarks/refining.yaml`).

## What is weak

- **The yields depend on the pseudo-formulas.** One point of hydrogen in the reformate, 10.5 instead of 11.5 wt%, moves the feed by about 14 %. The naphtha's real hydrogen content depends on its PONA analysis, which the dataset does not have.
- **The fuel gas and hydrogen come from different sources.** Hydrogen is the BREF's 350 Nm3/t (about 3.1 wt%). The C1 + C2 is one patent case, simulated at 13 barg, which is higher than the 3.5 to 10 bar of a modern CCR. Lower pressure cracks less. The same patent run gives 1160 SCF of hydrogen per barrel, about 23 kg/t (260 Nm3/t) at an ASSUMED feed density of 0.75 t/m3, so less than the BREF's 350 Nm3/t and below UOP's 300 to 600 Nm3/t. The two sources are not one consistent yield set.
- **The LPG has no source.** It is the rest of the mass balance.
- **Fuel fired is counted as heat delivered**, with no furnace efficiency, so the heat is an upper view. In practice the heaters burn refinery fuel gas; the background is natural-gas heat (`lca/mappings.yaml`).
- **The exported HP steam is not counted.** The BREF gives 50 to 90 kg/t from the convection section. Under cut-off it would be a co-product; here the other products carry its share.
- Midpoints of ranges are our choice. The utility data are old, so `valid_until` (2015) has already lapsed.
- Energy allocation follows the system model's step 2 (fuels and hydrogen) but is stated as the dataset's `allocation.deviation`, because `lci/mappings.yaml` has no curated rule for this process yet.

## Linking

The main product has the registry slug `reformate`, and the co-products `hydrogen`, `liquefied-petroleum-gas` and `refinery-fuel-gas`. Naphtha (`naphtha`) stays a reported gap: `refinery-distillation-1` makes untreated full-range naphtha, not the hydrotreated heavy naphtha this feed names. The catalyst stays a gap too. The hydrogen co-product is one more Atlas producer of `hydrogen`, beside `hydrogen-1`, `chlor-alkali-1`, `hda-1` and `co2-electrolysis-bpm-1`; consumers that pin `hydrogen-1` keep it. Fired heat links to the shared natural-gas heat entry (`lca/mappings.yaml`).

## Not counted yet (TODO)

Exported HP steam, the organic chloride promoter, regeneration vent traces (HCl, Cl2, CO, SO2, PCDD/F), fugitive hydrocarbons, chloride guard and dryer adsorbents, the net-gas purity. The full list is in the dataset's `system_boundary.excluded`.
