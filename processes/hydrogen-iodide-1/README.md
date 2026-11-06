# Anhydrous hydrogen iodide by gas-phase catalytic synthesis

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of anhydrous hydrogen iodide, made from hydrogen and iodine vapour over a supported metal catalyst (H2 + I2 -> 2 HI).

## Route and operation

The open sources are two patents that describe the same route, both run continuously at laboratory scale:

- **US 8 268 284 B2** (Nippoh Chemicals, priority 2008). Iodine is melted at about 120 degC and carried off as vapour by hydrogen, with two melting pots switched in turn so that the feed does not stop. The gas reacts over platinum on alumina at 350 degC for 100 hours of continuous operation, and the unreacted iodine is then scrubbed out with saturated aqueous HI.
- **US 11 554 956 B2** (Honeywell, priority 2019). A process for anhydrous HI at commercial scale over nickel on alumina. The unreacted iodine is frozen out in two trains that alternate, then melted and recycled. Hydrogen is recovered by compression and flash cooling, and the HI is purified by distillation. The claims cover continuous operation.

The swing iodine traps and melting pots run in cycles, but the synthesis itself runs without interruption. No open source describes how a commercial HI plant is operated; at the small volumes of HI it may well be run in campaigns, which this per-tonne screening does not represent (no cleaning, start-up or shutdown losses). The other routes named in the patents' backgrounds are hydrazine, hydrogen sulfide, red phosphorus and aqueous reduction to hydriodic acid. They are not modelled. The product here is anhydrous HI gas, not hydriodic acid.

## How it is built

`lca/datasets/hydrogen-iodide-catalytic-gas-phase.yaml` is a hand-written **Tier 0** dataset. Tier 1 would need electricity and heat from a source, and neither patent gives any utility figure. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed H and I balance. The amounts are the same as core's `cheme assess lci-estimate` gives for this reaction, yield and loss fate (checked in a scratch project).

| Item | Source | Standing |
|---|---|---|
| Efficiency 0.979 for both reactants | US 8 268 284 B2, Example 1: iodine conversion and HI yield after 100 h continuous | one laboratory run with a Pt catalyst. Reading it as a once-through efficiency, with no recycle, is ASSUMED |
| Iodine 1013.4 kg/t, hydrogen 8.05 kg/t | stoichiometry at that efficiency | the stoichiometric iodine is 992.1 kg/t |
| Unconverted iodine: 0.2 % of the feed to air, the rest (19.3 kg/t) to wastewater treatment | core's tier defaults, after Hischier et al. 2005, section 2.3 | generic screening rule |
| Unconverted hydrogen to air | calculated; venting all of it is ASSUMED (a gas) | applying the iodine efficiency to hydrogen takes the recycle of the excess hydrogen for granted (ASSUMED): the sources feed 2.4 to 6 mol H2 per mol I2 |
| Electricity 333 kWh/t, heat 556 kWh/t | core's Tier 0 defaults (Gendorf 2000 site averages) | ASSUMED, dated, not specific to HI |

## What is weak

- **Iodine use is an upper view.** Iodine is the costly feed and dominates the burden. US 11 554 956 B2 recycles the unconverted iodine and hydrogen, so a plant loses far less than the 2.1 % treated as lost here. No source gives the loss of a plant with recycle, so it is not credited. Hydrogen is the other way round: its excess (2.4 to 6 mol per mol of iodine in the sources) is taken to be recycled, with no recompression energy counted. Once-through hydrogen at 2.7 mol/mol would be about 22 kg/t fed and 14 kg/t vented, instead of 8.05 and 0.17.
- **Energy is not this process.** Both values are site-average defaults. The process melts and vaporises the iodine, heats the gas to about 300 to 350 degC and, in the Honeywell layout, compresses the HI and cools it to condense it (HI boils near -35 degC). None of these duties is quantified in an open source. As an order-of-magnitude check (review, not used in the dataset), the latent heats in the `chemicals` 1.5.2 CRC data (iodine fusion 15.5 and vaporisation 41.6 kJ/mol, HI vaporisation 19.8 kJ/mol) give about 63 kWh/t of HI to melt and vaporise the iodine fed and about 43 kWh/t to condense the HI. The gas-phase reaction is slightly exothermic (about -9.5 kJ/mol I2 at 25 degC, from the formation enthalpies in the same data). The 556 kWh/t heat default is several times the iodine duty. Sensible heating of the excess hydrogen, distillation and losses are not estimated, so it is not shown to be high or low.
- **The catalyst is not counted.** The catalyst may be platinum or nickel, and neither source gives a charge or a life. A platinum-group catalyst must never be cut, so it is listed as a TODO.
- The efficiency comes from one laboratory run with Pt. The nickel runs of US 11 554 956 B2 reach 89.5 to 95.8 % per pass (`benchmarks/inorganic-chemicals.yaml`, explained). The KPI therefore compares two single-pass laboratory figures, not plant data.
- `valid_until` is the reference year (2008) + 5, so it has already lapsed.

## Linking

The product has the registry slug `hydrogen-iodide`. `feed:iodine` links to `iodine-1` (iodine flakes, 99.8 wt%) and `feed:hydrogen` to `hydrogen-1` (99.9 mol% H2), through `lca/mappings.yaml`. `output:iodine-loss` stays a reported gap, because no shared entry treats an iodine load in wastewater. No library process uses HI yet.

## Not counted yet (TODO)

Catalyst, iodine and hydrogen recycle, the scrubbing liquor and purges, HI losses, refrigeration, compression and cooling water, inert gas and desiccant. The full list is in the dataset's `system_boundary.excluded`.
