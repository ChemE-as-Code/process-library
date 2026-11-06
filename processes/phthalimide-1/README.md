# Phthalimide by continuous reaction of phthalic anhydride with ammonia

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of phthalimide, from molten phthalic anhydride and ammonia, mixed in an ejector in about equal moles and reacted in a heated tube at about 265 °C. The melt is separated and flaked. The phthalimide carried off with the off-gas is recovered by absorbing the off-gas in water.

## Route and operation

The route runs continuously. Both BASF patents read here describe continuous processes, US 4,419,519 for the ejector and tube and US 4,001,273 for the countercurrent column. Both describe the older melt processes, where ammonia is passed into a batch of anhydride, as batch prior art. A secondary summary (Chemcess, which cites Ullmann's) says industrial phthalimide plants run continuously. Ullmann's chapter itself is licensed and was not read.

## How it is built

`lca/datasets/phthalimide-pa-ammonia-continuous.yaml` is a hand-written **Tier 0** dataset, a stoichiometric screening. Tier 1 would need a sourced figure for each of yield, electricity and heat. Here the yield has a source, but no open source gives the energy. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance (C, H, N, O).

| Item | Source | Standing |
|---|---|---|
| Yield of 0.996 of theory on anhydride | US 4,419,519, Examples 1 and 2 (0.994 and 0.998) | Midpoint of two pilot-scale patent examples; not plant data |
| Ammonia ratio of 1.002 mol/mol | US 4,419,519, Examples 1 and 2 (1.000 and 1.003) | Midpoint of the two examples that give the yield; the description prefers 1 to 1.02, in particular 1 |
| Phthalic anhydride: 1.0107 t/t | Stoichiometry with that yield | Inside the examples' 1.0085 to 1.0127 t/t, but that is the same source. The benchmark binds the only other open figure, Chemcess's 98 % yield (1.027 t/t) for the older co-current tube, and the dataset sits about 1.6 % below it with a reason (`benchmarks/nitrogen-organics.yaml`) |
| Ammonia: 0.1164 t/t | Stoichiometry with the ratio and the yield | Matches the examples' 0.1164 to 0.1165 t/t by construction; no independent open figure, so the benchmark records `no_open_reference` |
| Reaction water, excess ammonia, unconverted anhydride | Close the balance | Sent to wastewater treatment with the absorber water (fate ASSUMED); the water links to wastewater treatment, the two dissolved loads (0.70 and 4.0 kg/t) stay reported gaps |
| Electricity of 333 kWh/t and heat of 556 kWh/t | None read | Core's Tier 0 defaults (ASSUMED, dated 2000 site averages, not specific to phthalimide), each with a TODO |

## What is weak

- **The energy figures are generic defaults.** The patent calls the reaction exothermic. The heat users are melting and heating the anhydride, vaporising and heating the ammonia to about 260 °C, and the heated tube, so the default heat may overstate the demand. The flaker and absorber need cooling water, which is not counted. In the LCI the heat is mapped to natural-gas-fired heat, which is also ASSUMED.
- **The patent's yields are from pilot-scale tubes** of 25 and 100 mm. The patent counts the yield on the product as obtained, which is 99.6 to 99.8 wt% phthalimide with phthalic anhydride as the rest. The dataset counts that product as pure phthalimide. On that reading about 7 kg/t of anhydride is left unconverted: about 3 kg/t stays in the product as impurity, and the rest, about 4.1 kg/t, matches the dataset's effluent figure. So the effluent load is about right, and the simplification is the product's 0.2 to 0.4 wt% anhydride.
- **The absorption water is not counted.** The effluent is therefore only the reaction water plus small residues. Drying the phthalimide recovered from the absorber is not described and not counted. Vent emissions to air are not quantified, so all unconverted material goes to the effluent, because the patent absorbs the off-gas in water. That departs from core's Tier 0 loss split, which would put 0.2 % of each reactant's input mass to air (about 2.0 kg anhydride and 0.23 kg ammonia per t). These are TODOs, not zeros.
- The source is 1983, so `valid_until` (1988) has long lapsed.

## Linking

- **Product:** registry slug `phthalimide`. No library process consumes it yet.
- **`feed:ammonia`:** linked to `ammonia-1` (`product:NH3`, refrigerated liquid) in `lca/mappings.yaml`.
- **`feed:phthalic-anhydride`:** registry slug `phthalic-anhydride`, a reported gap. No library process makes it, and the shared vocabulary has no entry for it. A phthalic anhydride process (o-xylene oxidation, LVOC BREF) would close it.
- **`output:ammonia-effluent` and `output:phthalic-anhydride-effluent`:** reported gaps, as `hydrogen-iodide-1`'s iodine load is. The shared wastewater entry counts the water, not a dissolved load, and no entry treats a nitrogen or organic load. The reaction water (`output:wastewater`) links to wastewater treatment by mass.

## Not counted yet (TODO)

Absorption water, drying, vent emissions, cooling water, nitrogen blanketing and melt-line tracing, and impurities in technical-grade anhydride. The countercurrent-column variant, the urea route and o-xylene ammoxidation are not modelled. The full list is in the dataset's `system_boundary.excluded`.
