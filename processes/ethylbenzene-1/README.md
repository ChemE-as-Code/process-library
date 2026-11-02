# Ethylbenzene by liquid-phase zeolite alkylation

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of ethylbenzene, from benzene and ethylene on fixed-bed zeolite with transalkylation.

## How it is built

`lca/datasets/ethylbenzene-zeolite-liquid-phase.yaml` is a hand-written Tier 1 dataset: every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance. The source is chapter 5 of the EU LVOC BREF (facts in our own form, each with its section in `parameters`).

The feeds are calculated from stoichiometry with the sourced tar. They come out at 0.7395 t benzene and 0.2649 t ethylene per t, inside the BREF's 0.735 to 0.746 and 0.254 to 0.265. That is not an independent check: the feeds are about 99.5 % stoichiometry, and all the numbers come from one document (`benchmarks/styrenics.yaml`). The BREF's lower bounds lie below the stoichiometric 0.7358 t/t benzene and 0.2642 t/t ethylene, so its range ends are not a closed mass balance.

## What is weak

- **Steam is the largest uncertainty.** The source gives 100 to 2600 kWh/t. The dataset takes the midpoint, 1350 kWh/t, gross. Heat recovery of 700 to 2600 kWh/t in the same source is not credited, so an integrated plant can be far lower. Its uncertainty is gsd2 5.1, from the range, and its pedigree is lowered.
- Midpoints of ranges are our choice; the source does not recommend them.
- The tar compound (1,1-diphenylethane) and its hydrogen off-gas are ASSUMED model choices that close the balance.
- Fugitive VOC are upper bounds. Water input is ASSUMED equal to the effluent.
- The data are EU plants of 2007 to 2012, integrated with styrene units on site. `valid_until` is the reference year + 5, 2017, so it has already lapsed.
- Uncertainty: `gsd2 = sqrt(high / low)` where the source gives a range (our convention), ASSUMED values elsewhere.

## Linking

Its product has the registry slug `ethylbenzene`. `styrene-1` links to it explicitly. Benzene and ethylene are reported mapping gaps: their suppliers are not chosen (`lca/mappings.yaml`).

## Not counted yet (TODO)

Heat recovery, off-gas combustion at shared abatement, organics in the effluent, guard-bed adsorbents, storage emissions, the AlCl3 route. The full list is in the dataset's `system_boundary.excluded`.
