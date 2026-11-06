# Ammonium sulfate by direct neutralisation

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of crystalline ammonium sulfate. Anhydrous ammonia and strong sulfuric acid react in a continuous vacuum saturator-crystallizer, whose vapour is condensed against cooling water. The crystals are then centrifuged, dried in a steam-heated rotary dryer with a wet scrubber, and screened.

## Why this route

Most ammonium sulfate is a by-product. The GEA brochure (2010, PDF p. 3) puts caprolactam, methyl methacrylate and acrylonitrile at 60 to 70 % of world output, of about 17 Mt/a. AP-42 section 8.4.2 names the three main routes: caprolactam by-product, synthetic and coke-oven by-product.

**Caprolactam by-product** is the largest single source, but it is not modelled here. In that route the salt comes out of the caprolactam plant, whose oleum is neutralised with ammonia. Its inventory is a co-product split of the caprolactam process, so it belongs in the multi-output dataset of the `caprolactam` coverage entry. Modelling it here would mean building the caprolactam plant inside this entry.

**Direct neutralisation** is the route whose purpose is ammonium sulfate. It links to `ammonia-1` and `sulfuric-acid-1`. Both UNIDO chapter VIII (Production Details) and GEA describe it as continuous saturator-crystallizers, vacuum or atmospheric. A reader who needs the market average should note that it is the smaller share.

## How it is built

`lca/datasets/ammonium-sulfate-neutralisation.yaml` is a hand-written **Tier 0** dataset, a stoichiometric screening. Tier 1 would need a sourced electricity figure and yield, and neither was found in an open source. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance (H, N, O, S), water included.

| Item | Source | Standing |
|---|---|---|
| Ammonia, sulfuric acid | stoichiometry plus the dryer dust | 257.8 kg NH3 and 753.6 kg of 98.5 wt% acid (742.2 kg as 100 %, the stoichiometric requirement printed in UNIDO chapter VIII, Table 1); other losses are not counted |
| No crystallizer heat | GEA brochure, PDF p. 4 and p. 6; UNIDO chapter VIII | with reasonably concentrated reactants, the heat of reaction evaporates the water without an external source |
| Heat to cooling water, 470 kWh/t | NBS tables (Wagman et al. 1982), Table 14:S p. 2-58 and Table 18:N pp. 2-64 and 2-71; ammonia equation of state in CoolProp 8.0.0 | calculated: heat of reaction with gaseous NH3 (274.6 kJ/mol) less what the refrigerated liquid feed takes up (51.2 kJ/mol). It evaporates about 0.7 t water per t, which is condensed (ASSUMED vacuum saturator) |
| Water | water balance | the dryer evaporates 15.8 kg/t to air; the acid brings 11.4 kg, and 4.4 kg of make-up closes it (condensate returned, ASSUMED) |
| Dryer steam, 20.9 kWh/t | our estimate | cake moisture 1 to 2.5 % (AP-42 8.4.2, midpoint), product 0.2 % (UNIDO), latent heat at 50 degC, dryer efficiency 0.5 (ASSUMED) |
| Dust to air, 0.02 kg/t | AP-42 Table 8.4-1 | rotary dryer with wet scrubber, rating A, one 1990 compliance test; older controlled rotary-dryer tests in the AP-42 background report (0.08 and 0.16 kg/t) set the uncertainty |
| Electricity, 42.5 kWh/t | LVIC-AAF BREF Table 9.3 (solid AN, new facility, 25 to 60 kWh/t) | an ASSUMED analogue from another fertiliser salt plant, the midpoint, with a TODO; no open ammonium sulfate figure was found |
| Anti-caking agent, 0.5 kg/t | AP-42 8.4.2 | recorded under `cutoff`: its identity is not stated |

## What is weak

- **Electricity is an analogue, not data.** It is the midpoint of the range for a new solid AN plant, which runs a neutraliser, liquor pumps, a particle-forming step, fans and scrubbers. An ammonium sulfate plant has a crystallizer circulation pump, a vacuum system and a centrifuge instead. No open ammonium sulfate figure was found (`benchmarks/fertilizers.yaml` records the search). core's Tier 0 default of 333 kWh/t is not used: it is a site average of organic chemistry and would be 8 times the analogue.
- **The condensate route is ASSUMED.** A vacuum saturator with a surface condenser is taken, so the heat of reaction goes to cooling water (470 kWh/t) and the condensate goes back to the crystallizer and the centrifuge wash. An atmospheric saturator would vent about 0.7 t of vapour per t to air and take the same water as make-up, with no cooling water. A plant that purges condensate takes more make-up. Ammonia slip, any vacuum-ejector steam and the purge liquors are TODO.
- **The dryer heat rests on an ASSUMED efficiency.** The type of dryer is a choice too. AP-42 also names fluidized-bed and directly fired dryers, which would change both the heat carrier and the dust.
- **Zero crystallizer heat holds only with concentrated reactants.** GEA (2010, PDF p. 4) puts 80 to 90 % of ammonium sulfate crystallizers in the steam-heated evaporative mode. AP-42 8.4.2 describes the liquor of every route passing through an evaporator. A synthetic plant that takes dilute or spent acid, or that adds more make-up water than the reaction heat can evaporate, needs evaporator steam that this dataset does not count.
- **The dust factor comes from one plant**, and its process type is not stated. The test recorded no production rate, so the background report divided by a rate estimated from TVA capacity data. Older controlled rotary-dryer tests gave 4 to 8 times as much. The NSPS limit of 0.15 kg/t (1980) is the benchmark.
- The sources are old: emission tests 1978 to 1990, a UNIDO chapter with literature to 1992, and a 2010 brochure. `valid_until` is 2015, so it has already lapsed.

## Linking

The product has the registry slug `ammonium-sulfate`. `lca/mappings.yaml` links two feeds to Atlas producers:

- `feed:ammonia` links to `ammonia-1`.
- `feed:sulfuric-acid` links to `sulfuric-acid-1`. Both count kg of 98.5 wt% acid; the dataset writes it as (H2SO4)12(H2O), 98.49 wt%, as `phosphoric-acid-1` does.

Water, electricity and cooling water resolve by their registry slugs. The dust emission has no biosphere entry yet and stays a reported gap.

## Not counted yet (TODO)

A condensate purge, ammonia to air, ejector steam, mother-liquor and scrubber purges, trace additives, and the by-product routes. The full list is in the dataset's `system_boundary.excluded`.
