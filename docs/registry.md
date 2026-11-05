# Chemicals and products registry

[`chemicals/chemicals.yaml`](https://github.com/ChemE-as-Code/process-library/blob/main/chemicals/chemicals.yaml) (schema
`schemas/chemicals.schema.json`, `cheme-as-code/chemicals/v2`) holds the substances, mixtures
and utilities that processes name, together with the product master data an LCI database needs
(process-library#46). The shared rules live in `scripts/registry.py`, which both builders use.

## Substances and grades

An entry is a **substance** (or mixture or utility) by slug: `oxygen`. The Atlas graph joins
processes at this level, so there is one oxygen node whoever makes or uses it.

A **grade** is a product of that substance in a defined state and purity:
`oxygen/gox-30barg-99.5`, `oxygen/lox`, `nitrogen/gan-8barg-10ppm`, `nitrogen/lin`. A grade has
a `name` (the reference product name in the LCI export), a `phase`, a `purity` or
`concentration`, `impurities`, a reference `state` (pressure, temperature), and its own
`properties`, `crosswalk` and `classification`. A grade inherits its substance's properties and
overrides them with its own. For example, `oxygen/lox` has a density and an exergy of its own
and takes its molar mass from `oxygen`.

Grade slugs may contain dots (`gox-30barg-99.5`). Substance slugs may not.

## How a flow names its grade

A flow in `process.yaml` may name `chemical: <slug>/<grade>`. When it names only the substance,
the registry's `flow_grades` map can give the grade:

```yaml
flow_grades:
  asu-1/product:GOXP: oxygen/gox-30barg-99.5   # "<process-id>/<inventory_key>": "<slug>/<grade>"
```

Resolution (`registry.flow_grade`):

1. the flow's own `<slug>/<grade>`;
2. else `flow_grades["<process>/<inventory_key>"]`;
3. else no grade. The flow is the substance, and the LCI export names the reference product as
   before (the substance name with the exchange title).

If a flow names a grade that `flow_grades` contradicts, or a grade the registry does not have,
the build fails.

**Why a mapping, not a field with a default.** ASU-1's `process.yaml` is changed by its own
review, not here, so its four products could not be relabelled in the same change. The options
were an optional `grade:` field on the flow (which still means editing `process.yaml`), a
default grade per substance (wrong for oxygen, which has two ASU grades) or a mapping beside the
registry. The mapping keeps `process.yaml` untouched and is explicit per flow. Because it lives
in `chemicals.yaml`, it travels with the registry. Once a process names its grades itself, its
`flow_grades` entries can go. They must agree in the meantime.

## Properties

Each property has `value`, `unit` and `source`, plus `conditions` where the state matters.
Units are fixed per property so that values compare:

| property | unit | used for |
|---|---|---|
| `molar_mass` | g/mol | balances; checked against the formula |
| `elemental_composition` | kg/kg | element balances; checked against the formula |
| `carbon_content` | kg C/kg | carbon balances, biogenic carbon reporting |
| `biogenic_carbon_fraction` | kg/kg of the carbon | the biogenic share where it is a property of the grade |
| `lhv`, `hhv` | MJ/kg | energy allocation, fuels |
| `density` | kg/m3 | volume to mass (`conditions` required) |
| `standard_chemical_exergy` | kJ/mol | exergy allocation (Szargut reference environment) |
| `exergy` | kJ/kg | a grade's specific exergy at its state (`conditions` required) |
| `price` | `<CUR>/<unit>` | economic allocation (below) |

Sources used so far:

- molar masses and elemental compositions: IUPAC 2021 abridged standard atomic weights
  (Prohaska et al. 2022, Pure Appl. Chem. 94:573), applied to the formula;
- standard chemical exergies: Szargut, Morris and Steward (1988), reference environment model
  II, 298.15 K and 101.325 kPa;
- heating values of hydrogen and methane: derived from standard enthalpies of formation (CODATA
  Key Values, Cox, Wagman and Medvedev 1989; CH4 from the NIST-JANAF tables, Chase 1998);
- densities: NIST Chemistry WebBook, SRD 69 (fluid properties), queried 2026;
- dry-air composition: U.S. Standard Atmosphere 1976; CO2 from NOAA GML (global mean 2023).

**Carbon.** Carbon-free substances carry `carbon_content: 0`, so their biogenic carbon content is
0 too and still reported (decision on carbon). Where the biogenic share depends on the source
(CO2 from a fossil or a biogenic point source, or from DAC), it belongs to the flow or a grade,
never to the substance.

### Grade exergy

A grade's `exergy` is its standard chemical exergy per kg plus its physical exergy at the
grade's state, relative to the dead state T0 = 298.15 K, p0 = 1.01325 bar:

    e = e_ch / M + (h - h0) - T0 (s - s0)

with h and s of the pure fluid from the NIST Chemistry WebBook (SRD 69, default reference
state), as below. Purity of 99.5 % or more is treated as pure.

| grade | state | h (kJ/kg) | s (kJ/kg K) | h0 | s0 | e_ch/M | e (kJ/kg) |
|---|---|---|---|---|---|---|---|
| `oxygen/gox-30barg-99.5` | 31.01325 bar, 298.15 K | 263.636 | 5.49831 | 271.010 | 6.40716 | 124.07 | 387.7 |
| `oxygen/lox` | saturated liquid, 1.01325 bar (90.18 K) | -133.381 | 2.94171 | 271.010 | 6.40716 | 124.07 | 752.9 |
| `nitrogen/gan-8barg-10ppm` | 9.01325 bar, 298.15 K | 307.491 | 6.18110 | 309.267 | 6.83529 | 25.70 | 219.0 |
| `nitrogen/lin` | saturated liquid, 1.01325 bar (77.35 K) | -122.029 | 2.83404 | 309.267 | 6.83529 | 25.70 | 787.4 |

ASU-1's study takes its exergies from its own flowsheet. They agree with these within 1 % for
GOX, GAN and LOX. Its LIN is the stream to storage, subcooled at 5.2 bar and -181 °C, about
710 kJ/kg by the same method, against the study's 707 kJ/kg. That is 10 % below the grade's
saturated-liquid state, which is recorded as an override (below).

### Missing prices

No price is recorded yet, because no open source has been read for these products. The rule:

1. A registry price needs an **open** source (statistical unit values such as Eurostat PRODCOM
   or UN Comtrade, published under terms that allow reuse), with `year`, `currency`, `region`
   and, where the source gives one, a `range`. Prices from licensed market reports are never
   recorded.
2. Without a registry price, a study that allocates economically gives its own price with a
   source (core's `allocation.prices` or `properties.<product>.price`).
3. With neither, economic allocation cannot be computed. Following the WBCSD rule of the
   system model (economic only when the price ratio is above 5), the fallback is mass, stated
   as such. The registry never fills in a guess.

So mass and exergy allocation of ASU-1 can be computed from registry data with sources today.
Economic allocation waits for an open price.

**Where a price will come from.** `scripts/fetch_prices.py` turns UN Comtrade's annual trade
records of one HS subheading and year into a registry `price`: the unit value (sum of traded
value over sum of net weight, USD/kg, exports FOB by default), a range (lowest and highest unit
value of the reporters trading at least 1000 t) and the request URL as the source. It reads the
HS code from the entry's `classification.hs` (oxygen 2804.40, nitrogen 2804.30, argon 2804.21)
and prints the entry for review; it does not edit the registry. It fetches, or converts a
response saved from the same URL (`--input`):

    uv run scripts/fetch_prices.py --slug oxygen --year 2023 [--input saved.json]

An HS subheading covers every grade (gaseous and liquid oxygen alike), so a trade unit value is
a price of the substance, which its grades inherit, not of a grade. Before the first price is
recorded, the owner checks that UN Comtrade's terms allow the derived value to be published
under CC BY 4.0, and that the live response has the fields the script reads (it has not been
run against the live API yet: the development environment's network policy blocks it).
Eurostat PRODCOM sold-production values are the other open source named in #46; the script
does not read them yet.

**The export does not read registry prices yet.** `build_lci.py` takes a price from the study
(`allocation.prices`, `properties.<product>.price`) or the dataset only. Without one, economic
allocation fails with "no price of <product> in the study or the dataset, and the export takes
no registry price". Taking the registry's price as a fallback needs a rule for currencies (a
study's price carries none) and comes with the first recorded price.

## Classification and crosswalks

`classification` holds the UN CPC Ver. 2.1 subclass and the HS 2022 subheading (e.g. oxygen:
CPC 34210, HS 2804.40). `crosswalk` holds reference product names in ecoinvent and the EF
reference package. These are **names only, no data** (licence rule). They have not been checked
against a licensed copy, so the installer reports any name that does not link. A name belongs to
one registry entry (substance or grade). The EF 3.1 names are still empty: they are to be
taken from the EF reference package (eplca.jrc.ec.europa.eu), which was not reachable when the
registry was written, and are not filled in from memory. ecoinvent names are checked by the
owner against a licensed copy.

## Fuel mixtures

Raw natural gas (`raw-natural-gas`) and pyrolysis gasoline are in the registry as mixtures
without a composition. Sales gas is not a separate entry: natural-gas-processing-1 and the
library's natural-gas consumers take it as `methane`. Crude oil and the crude distillation cuts
(`refinery-fuel-gas`, `liquefied-petroleum-gas`, `naphtha`, `kerosene`, `gas-oil`,
`atmospheric-residue`, `vacuum-gas-oil`, `vacuum-residue`) came with refinery-distillation-1,
without a composition and with the IPCC 2006 default net calorific value of their fuel category as
`lhv` (a category default, not a value of the cut). Catalytic-reforming-1 and fcc-1 use the same
naphtha, liquefied petroleum gas and refinery fuel gas entries (catalytic-reforming-1's dataset
uses ASSUMED pseudo-formulas of its own). A typical composition is added, with its source, with the
first process that needs one. A mixture entry may go in
without a composition (the schema allows it), but no composition is entered without a source.

## Identities and how they are verified

A substance's identity is its `cas`, `inchikey`, `formula` and, where checked, `chebi` and
`pubchem_cid`. The entries added for issue #251 (the main products and feeds of the processes)
were verified when they were added, in this order:

1. CAS -> InChIKey, formula and molar mass in the offline database of the `chemicals` Python
   package (1.5.2, a dev dependency of core), and InChIKey -> the same CAS (cross-check);
2. the PubChem CID against the same InChIKey (PubChem PUG REST);
3. the ChEBI id against the same InChIKey (ChEBI web service); an id that could not be checked
   is left out.

Where the sources disagree, the entry says so in its `note` and keeps what PubChem gives for the
CAS (hydroxylammonium sulfate: the package has the 1:1 salt), or leaves the field out (aluminium
oxide has no InChIKey: the package and PubChem give different keys for CAS 1344-28-1).
`tests/test_registry.py` repeats step 1 offline wherever the `chemicals` package is installed (CI
installs 1.5.2 for the tooling tests),
and checks everywhere that a CAS, InChIKey, ChEBI id or CID names one entry only.

Molar mass, elemental composition and carbon content of these entries are derived from the
formula with the IUPAC 2021 atomic weights. Their standard chemical exergy is not given yet (a
follow-up with its Szargut-type source); exergy allocation of their products is therefore not
possible from registry data.

## How processes name these chemicals

Every process lists its main product (`role: main-product`) and its feeds under `chemistry`, so
that the Atlas graph links producers to consumers. Feeds added for issue #251 carry **no**
`inventory_key` (the note starts with the key, e.g. `feed:CUM: ...`): with a key the LCI build
would resolve the exchange through the registry slug and link it to a background or another
Atlas process, which is a change of the LCI that each process decides with its own mapping
review. Main products carry their `inventory_key` where the process had no reason against it,
so that the LCI export names the chemical in the reference product and the catalog labels the
functional unit with the product's name (issue #249). The catalog build warns for a process
without a main product.

## Build-time checks

`registry.check`, run by `build_catalog.py` and `build_lci.py`, fails the build on:

- a CAS number whose check digit is wrong;
- an InChIKey that is not a standard key (14-10-1 letters, `SA` at the end of the second block).
  Checking the key against the formula would need an InChI implementation, which the builders
  do not depend on;
- a molar mass (0.1 %), elemental composition or carbon content (0.001 kg/kg) that differs from
  the formula. Formulas are plain elements and counts;
- a mixture composition that does not sum to 100 % (0.5 % tolerance) or names an unknown
  chemical;
- the same crosswalk name on two entries, a duplicate grade, or a `flow_grades` entry naming an
  unknown grade.

The catalog build also warns (failing `--strict`) for a `flow_grades` key that no process flow
has: an entry left behind after an inventory key was renamed, or after the process named the
grade itself.

## Study properties against the registry

`build_lci.py` compares each product's allocation properties in the study (core's
`ProductProperties`: `exergy` and `energy`, per unit of the product) with the registry's grade (or substance)
values: `exergy` with `exergy`, and `energy` with `lhv`. Each comparison goes into the
datapackage (`datasets[].property_checks`) as `match`, `mismatch`, `overridden` or `unchecked`
(the registry has no value, or the product is not counted in kg: the registry's values are per
kg, and a product in m3, kWh or pieces is not converted). A difference of more than 2 % is a build warning, which fails
`--strict`, unless the process's own `lca/mappings.yaml` (ADR 0022) gives the exchange a
`properties_reason`:

```yaml
# processes/asu-1/lca/mappings.yaml
exchanges:
  "product:LIN":
    properties_reason: "The study's LIN is the subcooled stream to storage, not the grade's state ..."
```

Prices are not compared yet, because core's study price carries no currency.
