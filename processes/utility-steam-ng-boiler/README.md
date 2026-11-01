# Steam generation, natural-gas boiler, saturated 11 bar(a)

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Library utility (process-library#45), manifest only. Saturated steam at 11 bar(a) (184 degC) from a natural-gas fired boiler, per tonne of steam. Make-up water at 15 degC, no condensate return; continuous blowdown to wastewater treatment.

## How it is built

`lca/datasets/steam-mp-11bara-natural-gas-boiler.yaml` is a hand-written LCI dataset (`cheme/lci_dataset/v2`) in core's Tier 1
form: every amount is the `formula` of the dataset's `parameters`, which core's
validator re-checks, and `generation.balance` records the element balance (closed).
Physical properties and stoichiometry have their sources (IAPWS-95 and humid-air properties
evaluated with CoolProp 8.0.0, IUPAC 2021 atomic weights, the chemicals registry). **Every
design parameter is ASSUMED**, with its reason and a TODO to source it: the dataset is a
first-principles screening model, not sourced plant data. Its pedigree is therefore no better
than `[4, 4, 3, 4, 4]` and `maturity` stays `concept`.

## Linking

Its product has a registry slug (`steam/mp-11bara`). A consumer's input of that slug links to this
dataset by default (`install(prefer_atlas=True)`) and to the background alternative in
`lci/mappings.yaml` otherwise (`steam`: the background's heat from steam, converted by the steam's enthalpy).

## Operating range

Steam at 11 bar(a), saturated. It serves steam at 11 bar(a) or below (let down, carrying the MP steam's burden) and heat up to 184 degC; steam above 11 bar(a) or heat above 184 degC is refused. A consumer exchange that states a `carrier` outside this range is not linked here: the
build warns (which fails `--strict`) and keeps the background mapping, and an explicit
`link.dataset` to it is an error (`scripts/build_lci.py` `carrier_refusal`). An exchange without
a carrier cannot be checked and is linked.

## Not counted yet (TODO)

- NOx, CO, CH4 slip, N2O and particulates of combustion: the dataset is complete for fossil CO2 only.
- Boiler water chemicals.
- Condensate return (a variant), economiser and deaerator losses.
- Other pressure levels (LP, HP), biomass and electric boilers, CHP with its multi-output handling.
- Natural gas as a sourced composition instead of pure methane.

Infrastructure is excluded. The full list is in the dataset's `system_boundary.excluded`.
