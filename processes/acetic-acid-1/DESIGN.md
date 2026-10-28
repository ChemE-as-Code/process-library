# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Acetic acid by methanol carbonylation, issue ChemE-as-Code/process-library#128. First bounded
run (2026-10-28): design basis -> balanced BFD/PFD -> preliminary gate-to-gate LCI. Starting
point: library commit 11d50ef, cheme 0.8.0 (pyDEXPI 2.1.0). Numbers live in the YAML
(`process/*.yaml`, `lca/lca.yaml`); this file keeps the decisions, the evidence and what is open.

## Route and boundary memo

- **Product:** glacial acetic acid (>= 99.85 wt%), the commercial grade of carbonylation plants;
  an aqueous product is not considered.
- **Route:** liquid-phase methanol carbonylation, CH3OH + CO -> CH3COOH, the dominant route for
  new acetic acid capacity (Budsberg et al. 2020, Introduction, open access CC BY 4.0, citing the
  Ullmann article; Sanders 2010 abstract: carbonylation about 90 % of new production). Variants
  compared (D-003): Monsanto rhodium/methyl iodide at higher water; the low-water rhodium
  variants with an iodide salt stabiliser; the iridium/ruthenium (Cativa type) low-water
  process. Ethylene/acetaldehyde oxidation, butane/naphtha liquid-phase oxidation and
  fermentation are other routes, not designed here.
- **Boundary (gate-to-gate):** from the methanol and CO battery limits to glacial acid at the
  storage battery limit. Inside: reactor with cooler, HP vent knock-out, adiabatic flash, light-ends
  column with decanter, drying column, heavy-ends column, vent scrubbing with the feed methanol.
  Outside: methanol production (library process **methanol-1**, whose Grade AA product S18 is
  the feed composition), CO production and compression (a syngas cold box or partial oxidation:
  no library process yet), storage, the flare / thermal oxidiser, heavy-ends incineration, the
  utility plants, catalyst manufacture and recovery. A link to acetic anhydride (#131) is a
  later case.

## Source register

| # | source | locator | read status | reuse terms | used for |
|---|---|---|---|---|---|
| S1 | US 6,140,535 A (BP Chemicals, 2000), Iridium-catalyzed carbonylation process for the production of acetic acid, https://patents.google.com/patent/US6140535A/en | Description (operating ranges, FIG. 1/2 discussion); Examples 1-5 table | read (Google Patents full text) | patent document: facts used, no text or table copied | reactor T, P, water, CH3I, MeOAc; CO2 and CH4 make relative to carbonylation; H2 in CO feed; flash 1-4 bar(a); product limits <1500 ppm water, <400 ppm propionic; carbonylation rate 17.3-20.3 mol/(l h) |
| S2 | Jones, J.H. (2000) Platinum Metals Review 44(3) 94-105, doi:10.1595/003214000X44394105 | page not verified | **not read** (publisher returned 403); one statement seen only in a search-engine excerpt: propionic acid before the heavies column about one third of the rhodium process's 1200-2000 ppm | journal article: cite only | propionic-acid order of magnitude (D-004), route description |
| S3 | Sunley, G.J., Watson, D.J. (2000) Catal. Today 58, 293-307, doi:10.1016/S0920-5861(00)00263-7 | - | not read (paywalled) | cite only | route reference |
| S4 | Le Berre, C. et al. (2014) Acetic acid, Ullmann's Encyclopedia, doi:10.1002/14356007.a01_045.pub3 | - | not read (licensed) | cite only | route reference for the next source audit |
| S5 | Budsberg, E. et al. (2020) Biotechnol. Biofuels 13, 154, doi:10.1186/s13068-020-01784-y (PMC7469289) | Introduction | read (Europe PMC full text) | CC BY 4.0 | carbonylation is the main route (context only); no fossil inventory given |
| S6 | Dimian, A.C., Kiss, A.A. (2020) Chem. Eng. Res. Des. 159, 1-12, doi:10.1016/j.cherd.2020.04.013 | abstract metadata only | not read (403) | cite only | lead for a sourced energy basis (open input O-3) |
| S7 | Sanders, B.J. (2010) Zirconium corrosion resistance ..., ASTM MNL12127R, doi:10.1520/mnl12127r | abstract (Crossref) | abstract read | cite only | zirconium as the material of choice in carbonylation plants (D-011) |
| S8 | NIST Chemistry WebBook, https://webbook.nist.gov | standard formation enthalpies; enthalpies of vaporisation at the normal boiling point | rounded handbook values, not re-verified item by item this run | US public data | heats of reaction (process/reactions.yaml), shortcut energy data (D-008) |
| S9 | methanol-1 (this library), process/flowsheet.yaml stream S18 | S18 composition and delivery state | read | CC BY 4.0 (library) | methanol feed (D-005) |

No values were taken from licensed databases; no tables, figures or text were copied.

## Reaction and model evidence

| item | value used | basis | status |
|---|---|---|---|
| main reaction | CH3OH + CO -> CH3COOH, dH = -134.6 kJ/mol (liquid methanol and acid, gas CO) | stoichiometry; S8 formation enthalpies | sourced (rounded) |
| reactor conditions | 463 K, 2900 kPa(a) | S1 Examples 1-5: 189.0-191.2 C, 27.4-30.0 bar; preferred 181-195 C, 22-32 barg | design choice inside a sourced range |
| reactor liquid | water 6, CH3I 8, MeOAc 15 wt% | S1 Examples: water 4.6-7.8, CH3I 6.6-10.3, MeOAc 14.3-22.3 wt% | design choice inside a sourced range |
| CO2 make (water-gas shift) | 0.8 % of the carbonylation rate | S1 Examples 1-5: 0.63-0.98 % | sourced, mid value |
| CH4 make | 0.9 % of the carbonylation rate | S1 Examples 1-5: 0.81-1.02 % | sourced, mid value; stoichiometry CH3OH + H2 -> CH4 + H2O is a modelling choice |
| propionic acid | 500 ppm(wt) of the product formed | S2 (excerpt, unverified page): about 1/3 of 1200-2000 ppm; S1 Examples: 290-390 ppm in the product without a heavy-ends column | ASSUMED inside the reported order |
| propionic stoichiometry | CH3COOH + CO + 2 H2 -> C2H5COOH + H2O | balances elements; not the mechanism | modelling choice |
| methanol conversion per pass | 0.9545 (lumped) | follows from the loop balance, not kinetics | derived |
| kinetics | none | no rate law is used; the patent's carbonylation rate (17.3-20.3 mol/(l h)) gives a reaction liquid volume of about 53 m3 for 1000 kmol/h at the patent's catalyst concentrations (a first sizing hint, not a design) | open (O-5) |

The reactor model is `reactor: conversion` with four lumped reactions (process/reactions.yaml);
the conversions are the extents the sourced by-product ratios and the product rate require,
divided by the key's inlet flow: they hold for the design case only. The catalytic cycle
(methyl iodide, methyl acetate and HI equilibria, Ir/Ru complexes) is not modelled.

## Decisions

### D-001 Boundary: methanol and CO are boundary feeds (2026-10-28)
Decision: gate-to-gate from the methanol and CO battery limits to glacial acid at storage; see
the route and boundary memo. Methanol from methanol-1; CO from a cold box or POX outside.
Reason: the case notes; other library processes make the feeds. Rejected: an integrated
syngas/CO plant inside the boundary (separate case). Assumptions: storage, flare, incinerator,
utilities and catalyst recovery outside.

### D-002 Capacity and product (2026-10-28)
Decision: 60 t/h glacial acetic acid (504 kt/a at 8400 h), single train. Product limits:
water <= 1500 ppm(wt) and propionic acid <= 400 ppm(wt) (the product limits stated in S1), acid
>= 99.85 wt%. Reason: a world-scale single train; no client figure exists. ASSUMED.
Rejected: a published plant basis (none found that is open). The product water is not set:
it is the net water of the reactions and the methanol feed (691 ppm(wt)), inside the limit.

### D-003 Catalyst family and reactor conditions (2026-10-28)
Decision: low-water iridium/ruthenium with methyl iodide promoter (Cativa type), 463 K,
2900 kPa(a), water 6 wt%. Reason: one documented catalyst family (issue #128); the open patent
S1 gives conditions and by-product rates for it; low water reduces the drying load and the
water-gas shift (S2 per route description). Rejected: Monsanto rhodium at high water (more
drying, higher CO2 make); low-water rhodium with iodide salts (no open quantitative source found
this run).

### D-004 Lumped stoichiometric reactor from sourced by-product ratios (2026-10-28)
Decision: four reactions (carbonylation, water-gas shift, methanation, propionic acid) with
conversions set by the extents of S1 (CO2 0.8 %, CH4 0.9 % of carbonylation) and 500 ppm(wt)
propionic acid. Reason: no kinetics are available or invented; the issue accepts a sourced
conversion model at this stage. Assumptions: by-product ratios of the patent examples apply at
the design point; no acetaldehyde, higher iodides or formic acid modelled.

### D-005 Feeds (2026-10-28)
Decision: methanol = methanol-1 stream S18 (99.911 mol% methanol, water 0.05 wt%), 300 kPa(a),
313 K. CO gas ASSUMED 98.5 mol% CO, 1.0 % N2, 0.3 % H2, 0.2 % CH4, delivered at 3200 kPa(a)
and 313 K (the CO supplier compresses). Reason: H2 inside the 0.06-0.86 vol% of S1 examples and
enough H2 to close the hydrogen balance of methanation and propionic acid formation (the
water-gas shift alone gives less H2 than the patent's CH4 make consumes). Rejected: a CO
specification from a vendor (none open).

### D-006 Shortcut loop balance (2026-10-28)
Decision: the flash, columns, decanter and scrubber are specified splits of
`scripts/balance.py` (run with `cheme run scripts/balance.py`): reactor liquid composition
(D-003), flash vapour fractions per component (CH3I 0.90, MeOAc 0.75, water 0.50, methanol 0.80,
acid 0.25, propionic 0.20), acid recycles of 3 % (light-ends overhead), 10 % (light-ends
bottoms) and 8 % (drying overhead) of the acid output, 60 % of the flash-vapour water overhead in
C-201, decanter heavy-phase fractions. The values enter flowsheet.yaml as `assumed` with this
source; cheme recalculates the mixer, pumps and reactor and closes every balance. Reason: no
property package qualifies the acid/water/methyl iodide/methyl acetate system (pre-release issue
315, core #315; its current state could not be read from this environment) and `process
simulate` has no qualified method for it; the issue allows a specified model at a declared
lower level. All values ASSUMED; accuracy not stated. Rejected: an unqualified NRTL/UNIFAC
simulation presented as predictive.

### D-007 Vents and off-gas (2026-10-28)
Decision: 70 % of the non-condensables leave by the HP vent, 30 % by the flash and the
light-ends decanter (LP vent); both vents are scrubbed with the fresh methanol (one lumped
absorber T-101), which then feeds the reactor. Scrubbed off-gas: CO 45 mol% of the
non-condensables, methanol slip 0.3 mol%, CH3I slip 20 ppm(mol); to the site flare / thermal
oxidiser. Methyl iodide make-up = the slip only. Reason: the CO purge must carry the inerts and
by-product gases; 45 % CO is consistent with the patent's CO partial pressure (8-9 bar of
27-30 bar total, the rest largely condensable vapour). Result: yield 96.7 % on CO, 99.1 % on
methanol. ASSUMED; the CO loss is the most sensitive open value of the raw-material inventory.

### D-008 Utilities and duties (2026-10-28)
Decision: cooling water 298/308 K; MP steam 1100 kPa(a) (457 K) for reboilers (column bottoms
410-425 K); reactor heat partly removed by the adiabatic flash (the flash vapour carries 32.7
of the 37.7 MW reaction heat into the light-ends column), the rest (6.6 MW) by a cooler on
cooling water. Column duties from mass reflux ratios 1.0 (C-201), 3.0 (C-202), 1.0 (C-203),
rounded normal-boiling-point heats of vaporisation and constant liquid heat capacities (S8).
Reason: energy is not evaluable in core for these streams (no enthalpies). Check: steam plus
power (27.6 MW) equals the heat rejected minus the reaction heat (65.5 - 37.7 = 27.8 MW).
ASSUMED; steam raising in the reactor cooler and heat integration are not considered.

### D-009 Heavy ends (2026-10-28)
Decision: C-203 takes the product overhead; 90 % of the propionic acid leaves in the bottoms
with 2 kg acetic acid per kg, to incineration; the product keeps 50 ppm(wt). ASSUMED.

### D-010 Machines (2026-10-28)
Decision: electric pumps, efficiency 0.65; liquids returned to the reactor are pumped to
2900-3000 kPa(a). No compressor inside the boundary (CO delivered at pressure). ASSUMED; the
power is a known underestimate (no agitator, vacuum, cooling-water or tank-farm power).

### D-011 Materials of construction (2026-10-28)
Decision: none fixed. Wet iodide and acid at reaction temperature needs zirconium (S7) or
high-nickel alloys; open input for basic engineering.

### D-012 Pumps drawn as TransportingFluids (2026-10-28)
Decision: P101 and P102 use the DEXPI class TransportingFluids. Reason: `cheme process build`
(cheme 0.8.0) stops with `TypeError: 'typing.Union' object is not iterable` on a `Pumping` step
(its `method` field is a Union annotation in pyDEXPI 2.1.0): a core issue to report.

### D-013 Preliminary gate-to-gate LCI (2026-10-28)
Decision: lca/lca.yaml with functional unit 1 kg glacial acid (product HAC), allocation none
(one product), cut-off system model; every exchange from the flowsheet with its stream id; every
background `missing:` with the activity to link later (ADR 0022: a reported gap). Off-gas and
heavy ends are wastes to treatment (hazardous), their combustion emissions belong to the
treatment background. lca/mappings.yaml only counts the MP steam as heat (`steam-heat`). Minor
gas components in process.yaml carry no inventory_key (a slug would map the whole gas wrongly).
Catalyst (Ir/Ru) losses are not inventoried (no source, O-6): neither a zero nor a cut-off.

## Results (design case)

Per kg glacial acetic acid (lca/inventory.csv; flows from process/flowsheet.yaml):

| exchange | amount | streams | note |
|---|---|---|---|
| methanol (feed:MEOH) | 0.5390 kg | S01 | stoichiometric 0.5336: 99.1 % yield |
| CO gas (feed:COGAS) | 0.4880 kg | S03 | 0.4824 kg CO; stoichiometric 0.4664: 96.7 % yield |
| methyl iodide (feed:MEI) | 2.7e-6 kg | S04 | off-gas slip only |
| electricity (feed:POWER) | 0.0079 kWh | Q01, Q02, Q06, Q09, Q12 | pumps only, underestimate |
| MP steam (feed:MPS) | 0.452 kWh (1.63 MJ) | Q04, Q07, Q10 | shortcut |
| heat to cooling water (product:CW) | 1.092 kWh (3.93 MJ) | Q03, Q05, Q08, Q11 | shortcut |
| off-gas to flare/oxidiser (product:OFFGAS) | 0.0257 kg | S23 | 45 % CO, 20 % CH4, 14 % CO2 (mol) |
| heavy ends to incineration (product:HEAVY) | 0.00135 kg | S22 | 33 wt% propionic acid |

Balances: cheme validate 0 errors; every block and step closes; the reactor's extents explain
every component change (cheme process streams). LCI (cheme assess lca --balance): mass in
61,621.9 kg/h, out 61,621.8; C, H, I, N, O close within 0.05 %. Classification: partial (9
gaps, every exchange unmapped by design). Energy: not evaluable in core (no stream enthalpies).

## Method and dependency table

| step | needs | state | consequence |
|---|---|---|---|
| flash, columns, decanter, scrubber | qualified property package for acid/water/CH3I/MeOAc/CO (activity model with vapour association) | pre-release issue 315 / core #315 (not readable here) | specified splits (D-006), maturity none |
| energy closure, duties | stream enthalpies | same | shortcut duties (D-008) |
| reactor | kinetics or a sourced equilibrium | none open | lumped conversions (D-004) |
| HI/iodide speciation, corrosion | electrolyte model (core #364) | not needed at this level | not modelled |
| PFD build with pump steps | `Pumping` class in `cheme process build` | crashes (D-012) | TransportingFluids used |

## Open inputs

- O-1 Capacity, site and operating hours (ASSUMED, D-002).
- O-2 CO gas specification, pressure and its producer (ASSUMED, D-005); a library CO process.
- O-3 A sourced energy basis (steam, cooling water, power per t) to check D-008; S6 is a lead.
- O-4 CO loss in the off-gas (D-007) and the HP/LP vent split; scrubber design.
- O-5 Reactor sizing (rate model or the patent's space-time yield), reactor heat removal choice.
- O-6 Catalyst (Ir, Ru) and iodide losses and catalyst purge/recovery: no open rate found.
- O-7 Rigorous column design (stages, reflux) once a property method is qualified.
- O-8 Fugitive emissions, drains and aqueous effluents (not in the concept balance).

## Library items to add later (shared files, not edited here)

- chemicals/chemicals.yaml: methanol (the feed), carbon-monoxide (the feed gas), acetic-acid with
  a glacial grade (the main product), methyl-iodide (make-up), propionic-acid (heavy ends);
  methyl-acetate only as an internal component.
- lci/mappings.yaml: technosphere entries for methanol (or a link to methanol-1's dataset),
  carbon monoxide gas, methyl iodide, thermal oxidation of a CO-rich vent gas and hazardous
  incineration of organic acid waste.
