# Styrene by dehydrogenation of ethylbenzene

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of styrene monomer, by adiabatic dehydrogenation over iron oxide. The PO/SM co-production variant is not modelled.

## How it is built

`lca/datasets/styrene-eb-dehydrogenation.yaml` is a hand-written Tier 1 dataset: every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance. The source is chapter 5 of the EU LVOC BREF (facts in our own form, each with its section in `parameters`).

The ethylbenzene consumption (1070 kg/t) is the midpoint of the BREF's range. Styrene, tar and an ASSUMED benzene take their share of it, and toluene closes the balance at 23.6 kg/t. That sits inside the BREF's 16 to 94 kg/t only because of the chosen midpoint: toluene is a residual, -2.4 kg/t at EB 1040, and below 16 kg/t under EB about 1061. Neither KPI is an independent check (`benchmarks/styrenics.yaml`). No energy KPI is bound, because the fuel is in kg and an expression cannot add it to kWh; by hand, electricity, steam and fuel give 4485 kWh/t gross against the source's total of 3200 to 4700, from the same list.

The effluent of 2150 kg/t is mainly condensed dilution steam (BREF 5.3.3.2, pp. 276-277). That water belongs to the steam exchange, so `feed:water` is free and only closes the element balance.

Off-gas hydrogen, methane and ethylene burn in the steam superheater, as three of the BREF's plants do with the off-gas. Natural gas makes up the rest of the fuel.

## What is weak

- **The fuel reading is ASSUMED.** The midpoint of 1100 to 2900 kWh/t is read as including the off-gas hydrogen. If the range excludes it, natural gas and CO2 are understated. In the other direction, the heat of the off-gas methane and ethylene is not credited against the natural gas, which overstates CO2 by about 7 %.
- Steam is gross: the 210 to 840 kWh/t of heat recovery in the same source is not credited.
- Benzene is half of an upper bound, not a measured value.
- Superheater emissions come from one plant, whose fuel differs from the model's.
- Mass allocation is a preliminary deviation, since no sourced prices exist yet (dataset `allocation`).
- The data are EU plants; Table 5.9 gives 2011 and a 2007-2011 average. `valid_until` is the reference year + 5, 2016, so it has already lapsed.
- Uncertainty: `gsd2 = sqrt(high / low)` where the source gives a range (our convention), ASSUMED values elsewhere.

## Linking

`feed:ethylbenzene` is pinned to `ethylbenzene-1` in `lca/mappings.yaml`. Its benzene co-product takes the registry slug `benzene`, so a consumer of benzene without a chosen supplier needs `atlas: false` or an explicit link.

## Not counted yet (TODO)

Heat recovery, spent solvents, gums, coke, organics in the effluent, vacuum vents to shared abatement, storage emissions, hydrogen recovered for sale. The full list is in the dataset's `system_boundary.excluded`.
