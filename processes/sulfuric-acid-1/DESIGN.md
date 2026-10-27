# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml`; the stream table is generated: `cheme process streams
--md` (provenance letter per value). Issue: ChemE-as-Code/process-library#175.

Run record of this stage (2026-10-27): library branch `case/sulfuric-acid-1` from `79a7cd4`;
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0, CoolProp 8.0.0 in cheme's interpreter;
DWSIM not used. Core #315 open (checked 2026-10-27); core #364 closed by core PR #394 with an
electrolyte route for aqueous NaCl only: sulfuric acid stays unsupported, and the phase and
DWSIM routes refuse acid with water (issue comment of 2026-10-27).

## 1. Route and boundary memo

- **Route**: molten elemental sulfur burned in dried air -> waste heat boiler -> four-bed
  V2O5 converter, 3+1, with intermediate absorption after bed 3 (double contact / double
  absorption, DCDA) -> final absorption -> tail gas to stack. 98.5 wt% product acid, HP steam
  exported (case brief of #175).
- **Rejected for this case**: metallurgical (smelter off-gas) and spent-acid regeneration
  acid: different feed gas (SO2 strength, impurities, gas cleaning, no sulfur combustion heat)
  and so a different boundary; the issue notes them as separate feed cases. Single absorption:
  cannot reach the overall conversion of the brief. Wet-gas (WSA-type) processes for weak or
  H2S gases: not a sulfur-burning case. Oleum production: excluded by the brief (98.5 wt% only).
- **Boundary**: from molten sulfur at the burner pumps, atmospheric air at the filter and
  dilution water at the pump tank, to product acid at 313 K to storage, tail gas at the stack
  base and HP steam at the battery limit. Inside: drying tower, main blower, sulfur furnace,
  waste heat boiler, converter, gas/gas exchangers, superheater, economisers, intermediate and
  final absorption towers, acid pump tank, pump and coolers. Outside: sulfur melting, storage
  and filtration; acid storage and loading; the boiler feed water system (deaerator, BFW pumps,
  chemical dosing, blowdown) and the cooling-water system; start-up preheater fuel.
- **What crosses the boundary** (flowsheet terminals): SULFUR, AIR, PW (raw materials), ACID
  (product), STACK (off-gas), POWER, HPS (steam export, as heat above BFW) and CW.
- **Comparisons**: only with cases of the same boundary (sulfur burning, DCDA, BFW at the
  battery limit, no tail-gas scrubber, no heat recovery from the absorption acid).

## 2. Decisions

## D-001 Route and arrangement: sulfur burning, 3+1 DCDA (2026-10-27)
Decision: four adiabatic V2O5 beds with interbed cooling, intermediate absorption after the
third bed, reheat of the intermediate gas by two gas/gas exchangers (cold E-203 after bed 3,
hot E-201 after bed 1), steam superheating after bed 2 (E-202), economisers before each
absorption tower (E-204, E-205). One drying tower ahead of the main blower.
Reason: the arrangement the tech skill (`tech-heavy-chem-sulfuric-acid`, after Speight 2002)
describes for double absorption; the interpass exchanger placement is one common option and was
chosen so that the reheat closes with the bed 1 and bed 3 heat (scripts/balance.py).
Rejected: 2+2 arrangement (lower overall conversion at the same bed count for this gas
strength, not evaluated); heat recovery from the absorption acid to LP steam (D-012).
Assumptions: blower on the dry side, after the drying tower (dry-air compression, ASSUMED).

## D-002 Capacity and product (2026-10-27)
Decision: 1000 t/d H2SO4 (100 % basis) as 98.5 wt% acid, 42.3 t/h; 8000 h/a.
Reason: the brief fixes the strength; no client capacity is given, so a common single-train
size is ASSUMED. The LCI is per kg of product and does not depend on scale at concept level.
Assumptions: product impurities (Fe, SO2, NOx, colour) not modelled.

## D-003 Sulfur feed (2026-10-27)
Decision: pure molten sulfur at 413 K (ASSUMED).
Reason: commercial bright sulfur is above 99.5 % S; its carbon (bitumen), ash, water and H2S
would add CO2 and water to the gas and a minor heat input. Neglected until a sulfur
specification is given (open input).

## D-004 Air and burner gas strength (2026-10-27)
Decision: ambient air 298 K, 60 % RH (ASSUMED site); dry air N2 78.12 / O2 20.95 / Ar 0.93
mol% (CO2 lumped into N2); burner gas 11.5 mol% SO2, so O2/SO2 = 0.82 at the furnace exit.
Reason: the strength sets the air flow and the bed 1 temperature rise. 11.5 % keeps the bed 1
outlet inside the catalyst window (899 K, D-005) at 63 % bed 1 conversion; stronger gas (the
skill quotes 16-18 % for burner gas generally) would overheat bed 1 of a four-bed DCDA
converter without dilution air. ASSUMED, to be optimised.

## D-005 Reaction set and converter model basis (2026-10-27)
Decision: conversion reactors. Furnace: S + O2 -> SO2, complete. Beds: SO2 + 1/2 O2 <=> SO3
with cumulative conversion 63 / 87 / 95 % after beds 1-3 and 99.7 % overall, i.e. per-bed
fractions of the bed inlet SO2 of 0.63, 0.648649, 0.615385 and 0.94. Bed inlets 688 / 713 /
708 / 683 K (ASSUMED).
Reason: the values are within the ranges the tech skill gives from Speight (2002): first layer
60-65 %, about 95 % after the third layer, about 99.7 % overall with double absorption. A
sourced conversion model, not kinetics: no rate law or catalyst volume is claimed.
Check: `cheme process reactors` puts every bed short of the ideal-gas equilibrium at its
outlet temperature: ln(Q/K) = -0.063 (bed 1, close to equilibrium as expected), -0.298,
-0.381, -1.22 (bed 4); the bed duties evaluate to 0.0 +/- 0.1 kW, so the adiabatic outlet
temperatures of the script agree with core's ideal-gas enthalpies. Bed 1 at 693 K inlet gave
904 K, just above the library's V2O5 window (903 K, `cheme validate` warned): the inlet was
lowered to 688 K.
Rejected: equilibrium reactors with an approach temperature (an approach would be a further
unsourced number); kinetic beds (no sourced rate law selected).

## D-006 Balance method: independent script, cheme checks (2026-10-27)
Decision: `scripts/balance.py` (run with `cheme run`) computes what propagate cannot: the
tower outlets, the adiabatic furnace and bed outlet temperatures, the gas/gas exchanger and
steam-side duties, the tower acid circulation from each tower's energy balance, the blower and
pump power. Those values are entered as `assumed` with this decision as source; cheme
propagates the furnace, the beds, the exchanger sides, the pump tank and the acid splitter
(`calculated`) and must agree.
Energy basis of the script: ideal-gas Cp/R and formation enthalpies of materials.yaml (Poling,
CRC), liquid H2SO4 -813.99 and H2O -285.83 kJ/mol (NBS tables, Wagman et al. 1982), sulfur
fusion 1.721 kJ/mol (thermo), constant Cp of strong acid 1.45 kJ/(kg K) (ASSUMED), steam and
BFW enthalpies from CoolProp (IAPWS-95). Heat of mixing of water into 98-99.5 wt% acid
neglected (a few % of the absorption heat; it understates the cooling duty). Furnace outlet
(1402 K) extrapolates the Cp/R fits beyond their 1000 K range. Whole-plant energy residual:
0.00 kW (adiabatic plant, no losses).
Why not core: no property package covers SO2/SO3 gas or aqueous acid (`cheme process props
--coverage`, `cheme process methods`: electrolyte models unsupported; core #315, #364), so
`cheme process energy` cannot evaluate stream enthalpies and core cannot close the energy
balance: **gated step**. `process/simulation.yaml` records only the adiabatic modes.
The gas/gas exchangers are written as two steps each (hot side, cold side) joined by an energy
stream, so propagate passes flow and composition through each side.

## D-007 Absorption and acid system (2026-10-27)
Decision: one common acid header at 343 K (98.5 wt%) feeds the drying tower, the intermediate
and the final tower; all three return to one pump tank where dilution water is added; product
is drawn after the acid cooler. SO3 absorption 99.9 % in each tower (ASSUMED); gas leaves every
tower at 348 K; acid outlets 338 / 383 / 363 K (ASSUMED); circulation from the tower energy
balances: 325 / 1080 / 387 t/h. Moisture of the air removed completely.
Reason: the simplest system with the structure the skill names (circulation loop per tower,
water make-up, product draw as the loop's purge). Real plants usually separate the drying and
absorption acids and run the drying acid cooler and weaker: basic-engineering choice.
Assumptions: the drying acid leaves cooler than it enters, because heating the air takes more
heat than its moisture's condensation gives in this model (heat of dilution neglected).
Gas into the intermediate tower at 453 K, final tower 443 K: above the acid dew point is to be
checked (open).

## D-008 Steam (2026-10-27)
Decision: HP steam 4100 kPa(a), 673 K, raised from BFW at 4600 kPa(a), 378 K supplied by the
site. Heat to steam: waste heat boiler 26.4 MW, superheater 3.0 MW, economisers 7.44 and 6.76
MW, total 43.6 MW = 56.7 t/h steam = 1.34 kg per kg product (2769 kJ/kg). Exported as heat
above BFW (energy terminal HPS).
Reason: steam export is the main co-product of a sulfur-burning plant (brief). Level ASSUMED.
Open: the split of evaporation, superheat and BFW heating between the exchangers is not checked
(the superheater duty alone is small against the superheat of 56.7 t/h); deaerator steam and
BFW pumping belong to the site system and are not netted from the export.

## D-009 Emissions (2026-10-27)
Decision: stack SO2 = 0.3 % of the sulfur (99.7 % conversion): 81.9 kg/h = 1.94 g/kg product;
SO3 slip 1.64 kg/h = 0.039 g/kg (leaves as H2SO4 mist), explicit in stream S19 and the LCI. No
tail-gas scrubber in the base case.
Open: whether 99.7 % meets the applicable emission limit (BREF LVIC-AAF levels not yet read with
locators); 99.9 % (caesium-promoted last bed) would give about 0.65 g/kg. Furnace NOx, fugitive
SO2 and tank-vent mist are declared exclusions in lca/lca.yaml until sourced factors exist.

## D-010 Machines and pressure profile (2026-10-27)
Decision: electric main blower, 98 -> 160 kPa(a), isentropic 0.80, motor 0.96: 2.05 MW; acid
pump 35 m, 0.70, motor 0.96: 0.26 MW. Pressure drops 3-4 kPa per item down to 107 kPa(a) at the
stack base. All ASSUMED. Steam turbine drive of the blower is the common alternative; it would
lower the steam export and the power import (to be decided with the steam balance).
cheme 0.8.0 `process build` fails on a `Pumping` step (pyDEXPI 2.1.0 method field is an
optional union): P301 uses the parent class `GeneratingFlow` until core fixes it (report to core).

## D-011 Materials (2026-10-27)
Not decided (basic engineering): strong acid service, the wet/dry gas interfaces, acid coolers
(anodic protection or alloy), stack lining. The skill's carbon-steel statement for strong acid
is uncited and needs review.

## D-012 Heat recovery from the absorption acid (2026-10-27)
Rejected for the base case: recovering the absorption heat (about 20 MW to cooling water here)
as LP steam in a high-temperature intermediate tower. A variant for later; it would turn part
of the 0.49 kWh/kg to cooling water into LP steam.

## D-013 Preliminary LCI scope (2026-10-27)
Decision: functional unit 1 kg of 98.5 wt% acid at the gate; foreground exchanges from the
balanced flowsheet (design case); every background unmapped (`missing:` with the activity it
should connect to); air and the atmospheric components of the tail gas free; SO2 and SO3 to
air as elementary flows (non-urban high stack). `boundary: cradle-to-gate` is kept in
lca.yaml only so that the purchased inputs stay gaps (the schema's gate-to-gate maps every feed
free). Unallocated: the treatment of the steam co-product (system expansion against
natural-gas steam, or allocation) is the LCA practitioner's choice for the next stage.
Construction, catalyst (initial charge, screening losses, spent V2O5 as hazardous waste),
transport and end of life are not included; the catalyst amounts are vendor data (open input).
Result: `cheme assess lca --coverage`: "partial screening carbon footprint" with 8 gaps; no
impact number is claimed. Mass balance of the dataset closed (residual +0.32 kg/h of
129,259 kg/h), elements closed (S +1.3 kg/h, 0.01 %). Its "energy closure 188.8 %" counts only
the utilities (power in; steam and heat to cooling water out) and not the reaction enthalpy of
the sulfur (about 9.3 MJ/kg S burnt to SO2, plus oxidation and absorption): not an imbalance;
the energy closure is the script's (D-006).

## D-014 Steam co-product and declared-zero sulfur for the library build (2026-10-27)
Decision: the exported HP steam (`product:HPS`, Q3-Q6, 43,611 kWh/h, unchanged) is a co-product
of the acid with `allocation: shares` ACID 1 / HPS 0 and an `allocation.deviation`, as
nitric-acid-1 D-014 does for its exported steam: every burden on the acid, the steam leaves
without a burden and without a credit. `emission:S` (0 kg in the tail gas) is a declared zero,
`free` like H2O, instead of `missing:`. The dataset stays unallocated; amounts are unchanged.
Reason: the strict library build refused both. As an `output` with `missing:` the steam was
linked by its registry slug to `steam`, which is counted per kg, while the flowsheet counts it as
heat in kWh; docs/system-model.md treats exported steam as a co-product, allocated, never
credited, in the cut-off build. Energy allocation would put every burden on the steam (the acid
has no energy content), the acid's exergy cannot be calculated (no aqueous sulfuric acid
property package, D-006), and the WBCSD price ratio needs both products in kg. Elemental sulfur
has no emission flow to air, and the furnace burns it completely. Rejected: credit against
natural-gas steam (substitution study only; kept as `allocation.substitution` `missing:`).
This supersedes the "Unallocated" sentence of D-013 for the study's own allocation.

## 3. Reaction and model evidence

| step | model | basis | status |
|---|---|---|---|
| R101 furnace | conversion, S complete | excess air (O2/SO2 0.82); standard thermochemistry | assumed, standard |
| R201-R204 beds | conversion 63 / 87 / 95 / 99.7 % cumulative | Speight (2002) via skill `tech-heavy-chem-sulfuric-acid` (ranges, needs review against Ullmann's / BREF) | sourced ranges, values ASSUMED within them |
| R201-R204 | equilibrium check | ideal-gas K from materials.yaml formation data (CRC); cheme process reactors | all beds ln(Q/K) < 0 |
| T301, T302 | SO3 + H2O -> H2SO4, 99.9 % absorbed | ASSUMED | no source yet |
| T101 | moisture removed completely | ASSUMED | no source yet |

No kinetics, catalyst volumes or vendor data are used. Ideal-gas equilibrium is adequate at
110-160 kPa(a); fugacity corrections are negligible there.

## 4. Source register

| source | locator / access | use | reuse |
|---|---|---|---|
| Speight, Chemical Process and Design Handbook (McGraw-Hill 2002), Part 2, sulfuric acid | via the skill `tech-heavy-chem-sulfuric-acid` (not read directly) | arrangement, conversion ranges, burner-gas temperature | facts only, cited |
| Ullmann's, Sulfuric Acid and Sulfur Trioxide, doi:10.1002/14356007.a25_635 | reaction library entry `sulfuric_acid` (catalyst window); full text not audited | catalyst window, reaction | facts only, cited |
| JRC LVIC-AAF BREF (2007) | landing page only (issue note); chapter not read | emission context (open) | EU public document, facts only |
| chemicals/thermo packages (via `cheme chemistry thermo`) | Poling 5th ed., CRC, ATcT values | Cp/R, dHf, S of the gases | MIT-licensed code, facts |
| Wagman et al. (1982), NBS tables of chemical thermodynamic properties | H2SO4(l), H2O(l) dHf | absorption heat | facts |
| CoolProp 8.0.0 (IAPWS-95) | in cheme's interpreter | steam, BFW enthalpy, water vapour pressure | MIT, facts |

No benchmark or published plant balance was copied; the specific figures (1.34 kg steam, 0.055
kWh, 0.49 kWh to cooling water per kg) are this design's and have not been compared with a
sourced benchmark yet.

## 5. Methods and core dependencies

| need | status in core 0.8.0 | here |
|---|---|---|
| mass / element balances | supported | closed (cheme validate, process streams) |
| conversion reactors, extents | supported | furnace, beds, absorbers |
| ideal-gas equilibrium check | supported | beds, ln(Q/K) |
| gas enthalpy of SO2/SO3 mixtures | no benchmarked package (core #315) | script with ideal-gas Cp |
| aqueous H2SO4 (electrolyte) | unsupported, refused (core #364 covers NaCl only) | molecular pseudo-component, liquid formation enthalpy, constant Cp |
| block energy balances (cheme process energy) | not evaluable without stream enthalpies | gated; script closes to 0.00 kW |
| DWSIM simulation | refused for acid/water | not run |
| BFD/PFD build | Pumping step crashes (D-010) | GeneratingFlow workaround |

## 6. Open inputs

1. Capacity, site, operating hours (client).
2. Sulfur specification (carbon, ash, water, H2S).
3. Emission limits for SO2 and acid mist; tail-gas treatment need.
4. Sourced conversions per bed for the chosen catalyst (vendor) and absorption efficiencies.
5. Steam system: steam level, superheat feasibility, blower drive, BFW/deaerator boundary.
6. Catalyst charge and replacement (for the LCI).
7. Acid properties (Cp, heat of mixing) from a sourced correlation; acid dew point at the tower
   inlets.
8. PFD layout: only the drying block is pinned (below the furnace); the rest is generated.
