# Chilled water at 6 degC from an electric chiller

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Library utility (process-library#45), manifest only. Cold delivered as chilled water at 6 degC by an electric vapour-compression chiller, per MWh of cold. COP = 0.5 x the Carnot COP between 2 degC evaporating and 40 degC condensing (all ASSUMED), about 3.6. Its condenser heat (cold plus compressor work) goes to the cooling tower.

## How it is built

`lca/datasets/chiller-chilled-water-6c.yaml` is a hand-written LCI dataset (`cheme/lci_dataset/v2`) in core's Tier 1
form as far as it goes: every amount is the `formula` of the dataset's `parameters`,
which core's validator re-checks. It has no `generation` block, because it has no material
flow and core's Tier 1 form requires a closed element balance.
Physical properties and stoichiometry have their sources (IAPWS-95 and humid-air properties
evaluated with CoolProp 8.0.0, IUPAC 2021 atomic weights, the chemicals registry). **Every
design parameter is ASSUMED**, with its reason and a TODO to source it: the dataset is a
first-principles screening model, not sourced plant data. Its pedigree is therefore no better
than `[4, 4, 3, 4, 4]` and `maturity` stays `concept`.

## Linking

Its product has a registry slug (`chilled-water`). A consumer's input of cold (kWh) of that slug links to this
dataset by default (`install(prefer_atlas=True)`) and to the background alternative in
`lci/mappings.yaml` otherwise (none curated yet: a consumer of `chilled-water` fails the build until one is added).

## Operating range

Chilled water at 6 degC. It serves a duty that needs 6 degC or warmer; colder duties (brine, ammonia or propane refrigeration at lower levels) are refused and need their own level. A consumer exchange that states a `carrier` outside this range is not linked here: the
build warns (which fails `--strict`) and keeps the background mapping, and an explicit
`link.dataset` to it is an error (`scripts/build_lci.py` `carrier_refusal`). An exchange without
a carrier cannot be checked and is linked.

## Not counted yet (TODO)

- **Refrigerant losses are not counted.** An HFC loss may not be cut (docs/system-model.md section 4), so the dataset is incomplete until the refrigerant and its loss rate are sourced.
- Chilled-water pumps; further temperature levels; a sourced COP.
- The dataset has no material flows, so it carries no element balance and no `generation` block (core's Tier 1 form requires a closed balance).

Infrastructure is excluded. The full list is in the dataset's `system_boundary.excluded`.
