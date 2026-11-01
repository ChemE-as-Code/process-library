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
evaluated with CoolProp 8.0.0, IUPAC 2021 atomic weights, the chemicals registry). **The design
parameters are ASSUMED**, with their reason and a TODO to source them; U.S. DOE steam tip sheets
guide the boiler efficiency and blowdown but do not settle them (see each parameter). The dataset
is a first-principles screening model, not sourced plant data, so `maturity` stays `concept`.

## Combustion emissions

NOx, CO, CH4 slip, N2O and particulates are EPA AP-42 Section 1.4 factors, read in the April 2026
edition. The five values and ratings are the same in the July 1998 and October 2026 editions.
Each `ef_*` parameter names its table and rating.

- **Boiler class: small (below 100 MMBtu/h heat input, about 29 MW), uncontrolled (ASSUMED).** The dataset has
  no plant size, its fan head is that of a packaged boiler, and AP-42 places most packaged units
  below 100 MMBtu/h. It models no NOx control, and uncontrolled is also the better-rated small-boiler
  NOx factor. A boiler with low-NOx burners emits about half this NOx by the same table, and less
  N2O: expect this dataset to overstate both for such a boiler. A variant would change `ef_nox`
  and `ef_n2o`.
- **Basis.** AP-42 states factors per 10^6 scf at a higher heating value of 1020 Btu/scf and scales
  them with heating value, so they are applied by fuel energy: kg emitted = kg fuel x `hhv` /
  (`hv_ap42` x 10^6 x `btu_kj`) x `ef` x `lb_kg`, which is 0.4215 mg per MJ (HHV) per lb/10^6 scf.
- **Balance.** The carbon of CO, CH4 and particulates comes out of the fuel carbon, so CO2 and water
  are slightly below complete combustion (99.86 % of the carbon reaches CO2). The nitrogen of NOx
  and N2O is taken from air (`feed:N2`, free). Particulates count as carbon in the balance (ASSUMED,
  AP-42 gives no composition).
- **Quality.** These are US class averages from tests compiled in 1998, with ratings from B to E
  (N2O is E, PM is D), not measurements of this boiler. The rating sets the pedigree's reliability
  score (3 for B, 4 for D and E). `basic_uncertainty` does not follow the rating: it is core's value
  per substance (`quality.py`: CH4, NOx and N2O 1.5, PM2.5 3.0, CO 5.0), so N2O (E) and CH4 (B) share
  1.5 and CO (B) has the widest. Core marks that table as working defaults, not yet checked against
  the ecoinvent guideline.

Their biosphere3 identities come from core's elementary-flow crosswalk, as for CO2. They are not in
`process.yaml` `chemistry.outputs`: the registry has no slug for CO, N2O or NOx.

## Linking

Its product has a registry slug (`steam/mp-11bara`). A consumer's input of that slug links to this
dataset by default (`install(prefer_atlas=True)`) and to the background alternative in
`lci/mappings.yaml` otherwise (`steam`: the background's heat from steam, converted by the steam's enthalpy).

## Operating range

Steam at 11 bar(a), saturated. It serves steam at 11 bar(a) or below (let down, carrying the MP steam's burden) and heat up to 184 degC; steam above 11 bar(a) or heat above 184 degC is refused. A consumer exchange that states a `carrier` outside this range is not linked here: the
build warns (which fails `--strict`) and keeps the background mapping, and an explicit
`link.dataset` to it is an error (`scripts/build_lci.py` `carrier_refusal`). An exchange without
a carrier cannot be checked and is linked.

Size: the emission class holds up to 100 MMBtu/h heat input, about 30.7 t/h of steam (100 / 3.2551
MMBtu HHV per t). Above that, AP-42's uncontrolled NOx is 170 (tangential-fired) to 280 (large
wall-fired) lb/10^6 scf against the 100 used here, so NOx may be understated by 1.7 to 2.8 times.
The build does not check this limit.

## Not counted yet (TODO)

- SO2, non-methane organics and metals of combustion (AP-42 Section 1.4 lists factors; not taken up).
- Feed pump and fan electricity from a source: the pump and fan efficiencies, heads and excess air stay ASSUMED.
- Boiler water chemicals.
- Condensate return (a variant), economiser and deaerator losses.
- Other pressure levels (LP, HP), biomass and electric boilers, CHP with its multi-output handling.
- Natural gas as a sourced composition instead of pure methane.

Infrastructure is excluded. The full list is in the dataset's `system_boundary.excluded`.
