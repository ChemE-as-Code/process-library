# Cooling water, evaporative cooling tower, 25/35 degC

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; most of it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Library utility (process-library#45), manifest only. Heat rejection from cooling water supplied at 25 degC and returned at 35 degC in a mechanical-draught wet tower, per MWh rejected. The dry air flow follows from the air-side energy balance (ambient 20 degC, 60 % RH; air leaving saturated at 30 degC, both ASSUMED); evaporation is that air flow times its humidity pick-up, about 1.18 kg per kWh rejected. Make-up (about 1.57 kg/kWh) is a water resource withdrawn from nature; blowdown goes to wastewater treatment.

## How it is built

`lca/datasets/cooling-tower-evaporative-25-35.yaml` is a hand-written LCI dataset (`cheme/lci_dataset/v2`) in core's Tier 1
form: every amount is the `formula` of the dataset's `parameters`, which core's
validator re-checks, and `generation.balance` records the element balance (closed).
Physical properties and stoichiometry have their sources (IAPWS-95 and humid-air properties
evaluated with CoolProp 8.0.0, IUPAC 2021 atomic weights, the chemicals registry). **Every
design parameter is ASSUMED**, with its reason and a TODO to source it: the dataset is a
first-principles screening model, not sourced plant data. Its pedigree is therefore no better
than `[4, 4, 3, 4, 4]` and `maturity` stays `concept`.

## Linking

Its product has a registry slug (`cooling-water`). A consumer's output of heat rejected (kWh) of that slug links to this
dataset by default (`install(prefer_atlas=True)`) and to the background alternative in
`lci/mappings.yaml` otherwise (`cooling-water`: the screening proxy of pump and fan electricity). ASU-1 is kept on the proxy (`atlas: false`) until it decides its cooling configuration.

## Operating range

Cooling water at 25 degC supply. It serves a duty that needs cooling water at 25 degC or warmer; a consumer that needs colder water is refused. A consumer exchange that states a `carrier` outside this range is not linked here: the
build warns (which fails `--strict`) and keeps the background mapping, and an explicit
`link.dataset` to it is an error (`scripts/build_lci.py` `carrier_refusal`). An exchange without
a carrier cannot be checked and is linked.

## Not counted yet (TODO)

- Water treatment chemicals (biocide, inhibitors, acid): needed by the acceptance criterion of #45.
- Raw-water pretreatment, and the solids and biocide carried by drift and blowdown.
- Climate: one ambient state; once-through and air cooling as alternatives per site.

Infrastructure is excluded. The full list is in the dataset's `system_boundary.excluded`.
