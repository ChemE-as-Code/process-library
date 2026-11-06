# Benzyl alcohol by continuous hydrolysis of benzyl chloride

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of reagent-grade benzyl alcohol (at least 99.8 wt%), from benzyl chloride and aqueous sodium carbonate, hydrolysed continuously in a countercurrent reactor column with toluene as inert solvent and purified in two vacuum columns.

## Route and operation

Benzyl alcohol is made mainly by hydrolysis of benzyl chloride with a base. The open sources read say this runs both batchwise and continuously:

- CS 216044 B1 says production runs batchwise in stirred reactors and continuously in tubular and other flow reactors. Its own process is a continuous cascade of 2 to 4 stirred vessels with soda solution at 90 to 150 degC.
- EP 0 064 486 A1 (Eka AB, 1982) contrasts batch hydrolysis, which can take 20 to 30 h, with continuous operation. It describes a continuous countercurrent column and gives a worked example with raw materials and energy per kg (Tables 1 to 3).
- US 5,750,801 (Bayer AG, 1998) names the continuous alkaline processes as the line of development, with EP 0 064 486 among them. It then patents a continuous process with water only, no base.

So the route is continuous in documented practice, but no open source says what share of today's output is continuous rather than batch. The dataset models the continuous soda process of EP 0 064 486, because it is the only open source found with raw materials and energy per kg of product.

## How it is built

`lca/datasets/benzyl-alcohol-continuous-soda-hydrolysis.yaml` is a hand-written **Tier 0** dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance (C, H, O, Cl, Na).

| Item | Source | Standing |
|---|---|---|
| Benzyl chloride 1.193 kg/kg, soda 0.551 kg/kg (10 % molar excess) | EP 0 064 486 A1, Example 1, Second Product: benzyl chloride from the Table 1 flows (48.3 against 40.5 kg/h, which Table 2 rounds to 1.19), soda from Table 2 | pilot example, not plant data |
| Dibenzyl ether 0.55 wt% of the alcohol, water 6.0 kg/kg | EP 0 064 486 A1, Table 1, Example 1 | as above |
| Steam 955 kWh/t (reactor column 153, two columns 802) | EP 0 064 486 A1, Table 3, Example 1, Second Product | the table gives energy without its carrier; heat from steam is our reading |
| Brine NaCl and excess soda, CO2 vented | stoichiometry of 2 C7H7Cl + Na2CO3 + H2O -> 2 C7H8O + 2 NaCl + CO2 | the patent vents the CO2 at degassing; IPCC 2006 Vol. 3, Table 2.1, as a cross-check |
| Benzyl alcohol losses, 12.8 kg/t | closes the balance | lumped as benzyl alcohol (ASSUMED); the rounded Table 2 figure would give 10.6 kg/t |
| Electricity | none read | core's Tier 0 default, 333 kWh/t (ASSUMED, dated), with a TODO |

The overall yield is 98.2 % of theory. That is above the 95.0 to 95.5 % of the continuous stirred cascade in CS 216044 B1. The cascade converts less and forms more by-products: its organic layer still holds about 1.2 % benzyl chloride, 7 % dibenzyl ether and 2.7 % benzaldehyde, against 99.9 % conversion and 0.55 % ether here. Which design feature accounts for the gap is not established: the cascade's example with chlorobenzene as inert solvent still gives 95.2 %. US 5,750,801 gives 94 to 96 % for its water-only process. These are recorded in `benchmarks/oxygenates.yaml`.

## What is weak

- **All numbers come from one pilot example of 1982.** A plant may differ, especially in energy. `valid_until` is 1987, so it has long lapsed. No newer open figure was found.
- **The carrier of the energy figure is a reading.** The patent's Table 3 says "energy consumption" and leaves out pumping as negligible. The text heats the soda solution with steam, so the dataset counts all of it as steam heat.
- **The CO2 is significant**, about 207 kg/t, from the carbonate. The excess soda (52 kg/t) goes to the brine. If neutralised there, it would release about 21 kg CO2/t more, which is not counted. IPCC's full-release factor on all the soda fed gives 229 kg/t.
- The brine carries about 550 kg NaCl/t to surface water after treatment, counted as dissolved solids.
- Toluene make-up, cooling water, the vacuum system and organics in the brine are not counted (TODO).

## Linking

The product has the registry slug `benzyl-alcohol`. Soda ash links explicitly to `soda-ash-1` (`lca/mappings.yaml`). Benzyl chloride is a reported gap, because no library process makes it yet (side-chain chlorination of toluene, which would consume `chlor-alkali-1`'s chlorine). The dibenzyl ether and benzyl alcohol residues are gaps, because their treatment is not stated. One library process consumes benzyl alcohol: `benzyl-chloroformate-1`, whose `feed:BNOH` links this entry's product in that process's own `lca/mappings.yaml` (kg for kg, its dry alcohol taken as this reagent grade).

## Not counted yet (TODO)

Toluene make-up, cooling water, vacuum system, organics in the brine, benzaldehyde, CO2 from the excess soda, infrastructure. The full list is in the dataset's `system_boundary.excluded`.
