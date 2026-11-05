# Propylene by propane dehydrogenation

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of polymer-grade propylene, from propane over a platinum catalyst in moving-bed reactors with continuous catalyst regeneration (Oleflex type). The plant runs continuously: the catalyst circulates through the reactors and a separate regeneration section at steady state (Honeywell UOP 2019, p. 4; Ceyhan LCA report, section 3.1).

## How it is built

`lca/datasets/propylene-propane-dehydrogenation.yaml` is a hand-written Tier 1 dataset: every amount is the `formula` of its `parameters`, and `generation.balance` records the closed C, H and O balance.

The EU LVOC BREF names propane dehydrogenation (sections 2.2.7 and 3.2.1) but does not describe it, since Europe had only two plants in 2007. So the numbers come from the one open design inventory found: the life cycle assessment of a planned PDH-PP complex in Ceyhan, Turkey (RINA Consulting 2022, ESIA Annex S, published by the US DFC). Its Table 4.1 gives the inputs of the PDH unit per t of polypropylene, and its production rates convert them to propylene (59.981 t/h propylene for 59.0625 t/h polypropylene).

| Item | Source | Standing |
|---|---|---|
| Propane, 1188 kg/t | midpoint of the report's two figures, 1217 kg/t (Table 4.1) and 1159 kg/t (annual figures of section 3.1) | one preliminary design, not plant data |
| Electricity, 847 kWh/t | Table 4.1, PDH unit | one design value; grid at the site instead of the design's renewable contract |
| Catalyst, alumina, DMDS, caustic, phosphate, chlorine | Table 4.1, PDH unit | design values |
| Heat | no external fuel: the design burns its net gas (hydrogen and light ends) in the heaters and site boilers, section 3.1; Table 4.1 lists no natural gas for the PDH unit | |
| CO2 419 kg/t, water vapour | carbon and hydrogen balance, with the light ends modelled as methane and ethylene and burnt completely | ASSUMED model |

The propane gives a mass yield of 84.2 %, against 85 % in the licensor's paper (Honeywell UOP 2019, p. 3; `benchmarks/olefins.yaml`).

## What is weak

- **One design, not plants.** Every sourced number comes from one preliminary design, and its two propane figures disagree by 5 %. No second open source with electricity or consumables per tonne was found.
- **All of the net gas is burnt within the boundary**, as this stand-alone design does. Part of its heat raises steam for the polypropylene plant. The cut-off model gives no credit for that, so the dataset carries all of the combustion CO2. A plant that exports its hydrogen would have a hydrogen co-product, less CO2 and probably an external fuel. That variant is not modelled.
- The light ends are a model: all propane not converted to propylene is taken as cracked to methane and ethylene and burnt. Coke, ethane and C4+ are lumped into it.
- The utilities and off-sites shared with the polypropylene plant (cooling, water treatment, boilers, 269 kWh/t PP of electricity) are left out. They are not split in the source.
- Combustion emissions other than CO2 (NOx, CO, SO2 from the sulfur injection, HCl from the regeneration chloride) are named in the design's BAT evaluation but not quantified. They are TODO, not zero.
- Uncertainty: `gsd2 = sqrt(high / low)` for the two propane figures (our convention), ASSUMED values elsewhere.

## Linking

The product has the registry slug `propylene`. `cumene-1` buys propylene. Its feed stays unlinked (`atlas: false`) until a supplier is chosen; this entry is a candidate beside `ethylene-1`. Caustic soda and chlorine link to `chlor-alkali-1` (`lca/mappings.yaml`). Propane, the catalyst, the alumina (in and out), DMDS and phosphate are reported gaps.

## Not counted yet (TODO)

Shared utilities and off-sites, raw water, the site's natural-gas make-up, combustion and vent emissions other than CO2, fugitive emissions, flaring, spent caustic, and the hydrogen-export and cyclic fixed-bed variants. The full list is in the dataset's `system_boundary.excluded`.
