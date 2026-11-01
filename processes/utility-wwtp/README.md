# Wastewater treatment, activated sludge

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; most of it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Library utility (process-library#45), manifest only. Biological treatment of 1 m3 (1000 kg) of industrial wastewater at an ASSUMED design COD of 1 kg/m3. The organics are a CH2O model substrate, the biomass C5H7NO2: the oxygen demand is the COD removed minus the COD of the biomass grown, the CO2 that of the carbon oxidised (fossil, ASSUMED). Excess sludge goes to incineration with energy recovery (ASSUMED route), which the cut-off model leaves burden-free.

## How it is built

`lca/datasets/wwtp-activated-sludge-per-m3.yaml` is a hand-written LCI dataset (`cheme/lci_dataset/v2`) in core's Tier 1
form: every amount is the `formula` of the dataset's `parameters`, which core's
validator re-checks, and `generation.balance` records the element balance (closed).
Physical properties and stoichiometry have their sources (IAPWS-95 and humid-air properties
evaluated with CoolProp 8.0.0, IUPAC 2021 atomic weights, the chemicals registry). **Every
design parameter is ASSUMED**, with its reason and a TODO to source it: the dataset is a
first-principles screening model, not sourced plant data. Its pedigree is therefore no better
than `[4, 4, 3, 4, 4]` and `maturity` stays `concept`.

## Linking

Its product has a registry slug (`wastewater`). A consumer's output of wastewater (kg) of that slug links to this
dataset by default (`install(prefer_atlas=True)`) and to the background alternative in
`lci/mappings.yaml` otherwise (`wastewater`: the background's average wastewater treatment, per m3).

## Operating range

No temperature or pressure level. The design COD is a fixed parameter: a consumer whose wastewater carries much more or less COD (cooling blowdown carries almost none) is charged for 1 kg/m3, which is why a per-kg-COD dataset is the next step.

## Not counted yet (TODO)

- N2O and CH4 of treatment.
- Nitrogen and phosphorus removal, nutrient dosing, precipitants, dewatering polymer.
- A per-kg-COD dataset, so each consumer brings its own load; the sludge route of the site.

Infrastructure is excluded. The full list is in the dataset's `system_boundary.excluded`.
