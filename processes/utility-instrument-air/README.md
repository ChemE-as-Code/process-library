# Instrument air, dried, 8 bar(a)

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; most of it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Library utility (process-library#45), manifest only. Dry instrument air at 8 bar(a) and a -40 degC pressure dew point, per kg. Compressor electricity is the isothermal work of the humid intake over an ASSUMED isothermal efficiency of 0.6; a heatless dryer purges 15 % (ASSUMED). The compressor heat goes to cooling water, the aftercooler condensate to wastewater treatment.

## How it is built

`lca/datasets/instrument-air-8bara-dried.yaml` is a hand-written LCI dataset (`cheme/lci_dataset/v2`) in core's Tier 1
form (core#182): every amount is the `formula` of the dataset's `parameters`, which core's
validator re-checks, and `generation.balance` records the element balance (closed).
Physical properties and stoichiometry have their sources (IAPWS-95 and humid-air properties
evaluated with CoolProp 8.0.0, IUPAC 2021 atomic weights, the chemicals registry). **Every
design parameter is ASSUMED**, with its reason and a TODO to source it: the dataset is a
first-principles screening model, not sourced plant data. Its pedigree is therefore no better
than `[4, 4, 3, 4, 4]` and `maturity` stays `concept`.

## Linking

Its product has a registry slug (`instrument-air`). A consumer's input (kg of dry air) of that slug links to this
dataset by default (`install(prefer_atlas=True)`) and to the background alternative in
`lci/mappings.yaml` otherwise (none curated yet: a consumer of `instrument-air` fails the build until one is added).

## Operating range

8 bar(a). The product states its pressure (`state`), but core's carriers cover energy only, so a consumer at a higher pressure is not refused yet (TODO: a pressure check for gas products).

## Not counted yet (TODO)

- Desiccant and filters; a sourced package efficiency; a heated or heat-of-compression dryer variant.
- A background alternative (no curated name yet).

Infrastructure is excluded. The full list is in the dataset's `system_boundary.excluded`.
