# Ammonium hydroxide (aqueous ammonia) by continuous dilution

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of aqueous ammonia at 25 wt% NH3, made by mixing liquid anhydrous ammonia with water and cooling the solution. Commercial "ammonium hydroxide" is this solution; the dataset does not model a pure NH4OH fluid.

## How it is built

`lca/datasets/ammonium-hydroxide-25wt-dilution.yaml` is a hand-written **Tier 0** dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance. Tier 1 would need electricity and losses from a source, and no open source gives either.

| Item | Source | Standing |
|---|---|---|
| Route, product strength | US 4,752,452 (Union Oil, 1988), Background of the Art and example | a patent: 20 to 30 wt% NH3 for this dilution process; 25 wt% is the midpoint, our choice, and the example's volume flows work out at 24 to 25 wt% |
| Ammonia and water | the product's strength | stoichiometry of a dilution; the product is modelled as (NH3)6(H2O)17, 25.02 wt% |
| Heat to cooling water, 26 kWh/t | NBS tables (Wagman et al. 1982), Table 18:N p. 2-64; ammonia equation of state (Gao et al. 2020) in CoolProp 8.0.0 | calculated: heat of solution to 2.83 mol H2O per mol NH3, less the enthalpy the refrigerated liquid feed takes up |
| Electricity, 0.62 kWh/t | none | ASSUMED pump work (5 bar, 50 % efficiency) for the two feeds and the product |
| Densities | ATSDR (2004) Table 4-2; IAPWS-95 in CoolProp 8.0.0 | used only for the pump estimate |

**Continuous operation.** The patent describes a flow process: metered streams in gallons per minute, a mixing nozzle, an evaporative cooler and an exchanger in which the cold liquid feed takes the last heat from the product. It does not use the word "continuous"; we read it from the flows. The same text says large commercial plants do the same with their own cooling and refrigeration. Dealers also make the solution on demand from stored ammonia, so small sites may run intermittently. The dataset per tonne is the same either way.

## What is weak

- **The feed state sets the cooling duty.** Refrigerated liquid at -33 °C, the state of `ammonia-1`'s product, takes up most of the heat of solution while it vaporises: 26 kWh/t is rejected. Pressurised liquid at 20 °C, close to the patent's example, would give about 43 kWh/t, and gaseous ammonia about 131 kWh/t. The heat of solution is read at 2.0 and 5.0 mol water and interpolated linearly to 2.83 (ASSUMED). The tabulated values are convex in the water ratio, so the straight line is a lower bound: a quadratic through the 1.0, 2.0 and 5.0 rows gives 27 to 29 kWh/t.
- **Electricity is an estimate, not data.** core's Tier 0 default of 333 kWh/t is a site average for reaction and separation plants, so it is not used. The cooling circuit's own pumps and fans are counted in the cooling-water utility.
- **Losses are not counted.** The patent names a relief valve, a vapour return line and a hose bleed but quantifies no loss. Storage and loading emissions are left out too. These are TODO exclusions, not zeros.
- The product temperature of 25 °C and demineralised water are ASSUMED; the patent only softens its water. The year is that of the calculation: no plant data were used.

## Linking

`feed:ammonia` links to `ammonia-1` (`lca/mappings.yaml`). The product has the registry slug `ammonium-hydroxide`. It is a different node from `ammonia`, so the anhydrous ammonia consumers do not link to this solution. Water, electricity and cooling water resolve by their slugs.

## Not counted yet (TODO)

Ammonia losses at the mixer, storage and loading; flushing and cleaning; water treatment. The absorption of ammonia-plant purge or flash gas is another route to the same product and is not modelled. The full list is in the dataset's `system_boundary.excluded`.
