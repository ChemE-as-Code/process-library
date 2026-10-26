# Flaring of methane-rich waste gas

Library utility (process-library#45), manifest only. Combustion of 1 kg of waste gas, taken as methane, in an elevated flare at an ASSUMED combustion efficiency of 98 %: CO2 and water of the burnt fraction, the unburnt methane to air.

## How it is built

`lca/datasets/flare-methane-per-kg.yaml` is a hand-written LCI dataset (`cheme/lci_dataset/v2`) in core's Tier 1
form (core#182): every amount is the `formula` of the dataset's `parameters`, which core's
validator re-checks, and `generation.balance` records the element balance (closed).
Physical properties and stoichiometry have their sources (IAPWS-95 and humid-air properties
evaluated with CoolProp 8.0.0, IUPAC 2021 atomic weights, the chemicals registry). **Every
design parameter is ASSUMED**, with its reason and a TODO to source it: the dataset is a
first-principles screening model, not sourced plant data. Its pedigree is therefore no better
than `[4, 4, 3, 4, 4]` and `maturity` stays `concept`.

## Linking

Its product has a registry slug (`flare-gas`). A consumer's output of gas to the flare (kg) of that slug links to this
dataset by default (`install(prefer_atlas=True)`) and to the background alternative in
`lci/mappings.yaml` otherwise.

## Operating range

Methane-rich gas only. Other gases need a composition-based variant (carbon and hydrogen content); nothing refuses them yet, so a consumer must not link a gas of another composition here.

## Not counted yet (TODO)

- Pilot, purge and assist gas or steam (per flare, from its design).
- CO, soot, NOx.
- A composition-based dataset; a background alternative (no curated name yet: a consumer of `flare-gas` fails the build until one is added).

Infrastructure is excluded. The full list is in the dataset's `system_boundary.excluded`.
