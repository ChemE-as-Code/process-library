# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes. The
numbers live in the YAML (`process/design-basis.yaml`, `process/flowsheet.yaml`,
`process/reactions.yaml`, `lca/lca.yaml`); `cheme process streams` prints the stream table and
balances. Issue: ChemE-as-Code/process-library#119. Run of 2026-10-27, started from library
main `79a7cd4`, cheme-as-code 0.8.0 (pyDEXPI 2.1.0), thermo 0.6.1, chemicals 1.5.2,
CoolProp 8.0.0. Agent-generated, not reviewed.

## Source register

| # | source | locator | access / read | reuse terms | used for |
|---|---|---|---|---|---|
| S1 | IPCC (2006) 2006 IPCC Guidelines for National GHG Inventories, Vol. 3 Ch. 3 Chemical Industry Emissions, https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/3_Volume3/V3_3_Ch3_Chemical_Industry.pdf | section 3.3; Table 3.3 "Default factors for nitric acid production", printed p. 3.23; Table 3.2 (abatement approaches) p. 3.20 | open PDF, section 3.3 and Table 3.3 read (text extracted 2026-10-27) | facts and numbers cited, no table copied | N2O formed (medium-pressure combustion plants, 7 kg N2O/t HNO3, +/-20 %) and N2O emitted with tail-gas N2O destruction (2.5 kg N2O/t HNO3, +/-10 %): D-005, D-009 |
| S2 | European Commission JRC (2007) LVIC-AAF BREF, Chapter 3 Nitric acid, https://bureau-industrial-transformation.jrc.ec.europa.eu/sites/default/files/2022-03/LVIC-AAF.pdf | section 3.2 from printed p. 96 (PDF p. 124): oxidation, absorption, mono/dual-pressure; sections 3.3/3.4 consumption, emissions, techniques | not re-read in this run (locator from the issue's literature note); no number taken from it | facts only | qualitative process description (unit sequence, dual-pressure scheme, tertiary abatement as a technique): D-001, D-003, D-009. Its consumption and emission ranges are the next check (open input O-1) |
| S3 | `cheme chemistry library nitric_acid` (core reaction library; cites Ullmann's article on nitric acid) | entry nitric_acid | packaged | stoichiometry only | reactions NH3_OX, NH3_N2, NO_OX (D-005) |
| S4 | skill `tech-heavy-chem-nitric-acid-and-fertilizers` (Speight 2002, Part 2; Ray and Das 2020, Ch 10) | gauze 750-920 degC, about 7 bar, 2-10 % Rh; absorption product about 65 %, azeotrope 68.4 % | packaged skill | facts | plausibility of the gauze temperature and the product strength below the azeotrope (D-002, D-005) |
| S5 | `thermo` 0.6.1 / `chemicals` 1.5.2 (ideal-gas heat capacities, gas formation enthalpies); CoolProp 8.0.0 (NH3 reference EOS) | as called in `scripts/hno3_balance.py` | open-source packages | MIT | enthalpies and machine discharge temperatures of the balance (D-010) |
| S6 | NIST-JANAF / NBS standard formation enthalpies of liquid water (-285.83 kJ/mol) and liquid HNO3 (-174.1 kJ/mol) | standard values at 298.15 K | well-known reference values, typed in the script | facts | liquid enthalpies in the cooler-condenser and absorber duties (D-010) |

No vendor, licensor or licensed-database value is used. Nothing above is copied (tables,
figures, text); the flowsheet and its drawings are our own.

## Basis table (sourced / proposed / missing)

| item | value | status |
|---|---|---|
| product grade | 60.0 wt% HNO3, NOx-free after bleaching | proposed (D-002; case note "~60 wt%") |
| contained-acid capacity | 1000 t/d HNO3 (100 %), 41 667 kg/h | proposed (D-002) |
| solution rate | 1666.7 t/d, 69 444 kg/h | derived from the two above |
| operating hours | 8000 h/a | proposed |
| NH3 feed | liquid, pure, 1600 kPa(a), 288 K | proposed (D-004); purity specification missing |
| air | 1 mol% humidity, 288 K | proposed (D-004) |
| burner NO selectivity | 0.955 | proposed, not sourced (D-005) |
| N2O formed | 7 kg/t HNO3 | sourced, S1 Table 3.3 (an inventory default, not plant data) |
| N2O emitted, abated | 2.5 kg/t HNO3 | sourced, S1 Table 3.3 |
| tail-gas NOx before / after SCR | 500 / 50 ppmv as NO | proposed (D-008, D-009); permit missing |
| cooling water | 298/308 K | proposed (D-011) |
| steam export | 4000 kPa(a), 673 K, BFW 378 K | proposed (D-011) |
| site, permit limits, prices | — | missing |

## Method and dependency table

| step | method here | core capability | status |
|---|---|---|---|
| burner R101 | conversion reactor (cheme propagate), conversions D-005 | conversion reactor: supported | done; a specification, not predictive |
| cooler-condenser E105 | conversion reactor, conversions from the script (D-007) | supported (conversion) | done |
| weak-acid separator V101, absorber C101, bleacher C102 | outlets specified from the script (D-007, D-008); reactions named, cheme checks extents | no aqueous HNO3 VLE/electrolyte package, no reactive-absorption model | gated: core's property-package qualification (open), core's electrolyte support (closed 2026-10-27 for NaCl-H2O only: "no acids"; not in the installed 0.8.0 either) |
| tertiary reactor R102 | conversion reactor (D-009) | supported | done |
| exchangers, machines | gas-phase part: DWSIM (D-016); acid section: pass-through propagate, duties from the script | stream enthalpies: no package covers H2O/NO/NO2/HNO3 (`props --coverage`) | gas-phase part simulated (unqualified package); acid section closed by the script (D-010) |
| BFD/PFD | `cheme process build` | supported; Pumping step crashes the build (D-012) | done with a workaround |
| LCI | `cheme assess lca --inventory --write` | supported | done, backgrounds unmapped (D-014) |
| DWSIM simulation | `process/simulation.yaml`, gas-phase part only (D-015, D-016) | runs (cheme 1.2.1, DWSIM 9.0.5; PR unqualified for this mixture); HNO3 with water refused, shaft-coupled machines and two-inlet reactors not mapped | gas-phase part converged and filled 2026-11-01 (D-016) |

## D-001 Route and boundary (2026-10-27)
Decision: weak nitric acid by the dual-pressure Ostwald process: ammonia evaporation, air
compression, catalytic ammonia oxidation over Pt/Rh gauze at medium pressure, heat recovery to
HP steam, cooler-condenser, NOx compression, absorption in water at high pressure, bleaching
with secondary air, tertiary tail-gas treatment (N2O decomposition and SCR) and a tail-gas
expander on the compressor train. Boundary: liquid ammonia, ambient air and demineralised water
in; 60 wt% acid, treated tail gas and exported HP steam out; power, LP steam and cooling water as
utilities. Ammonia and acid storage, the boiler-feed-water system (deaerator, BFW pumps),
cooling tower and water treatment are outside.
Reason: the issue's first job and case note; dual pressure is the usual choice for weak acid
at large capacity (S2 section 3.2 describes mono- and dual-pressure plants).
Rejected: mono-pressure (medium or high) plants (another comparison basis, S1 assigns high-pressure
plants a higher N2O default); atmospheric-pressure combustion; concentrated acid (>68 %, needs
extractive distillation, outside the issue's initial boundary).
Assumptions: the pressure levels of D-003.

## D-002 Capacity and product (2026-10-27)
Decision: 1000 t/d of contained HNO3 (100 % basis) as 60.0 wt% acid (1666.7 t/d solution),
8000 h/a. The functional unit of the LCI is 1 kg contained HNO3.
Reason: the issue asks for product strength and contained-acid throughput frozen separately;
60 wt% follows the case note and stays below the 68.4 % azeotrope (S4). 1000 t/d is a common
single-train size for dual-pressure plants, ASSUMED, not a client figure.
Rejected: a solution-tonnes basis (not comparable across strengths).

## D-003 Pressure scheme (2026-10-27)
Decision: air compressor discharge 520 kPa(a), burner outlet 490 kPa(a); NOx compressor to
1150 kPa(a), absorber 1130 kPa(a), tail gas 1100 kPa(a) at the top; expander to 105 kPa(a).
Pressure drops per item ASSUMED (5-20 kPa per exchanger, 30 kPa over R-102). Bleacher at
oxidation pressure, its gas returned to the NOx compressor suction.
Reason: typical dual-pressure levels (combustion about 0.4-0.6 MPa, absorption about 1.0-1.2 MPa);
ASSUMED within the window of the reaction library entry (100-1200 kPa(a), S3).

## D-004 Feeds (2026-10-27)
Decision: liquid ammonia at 1600 kPa(a), 288 K, modelled pure (purity, water and oil
specification are open inputs); ambient air at 288 K, 101.325 kPa(a), 1 mol% water (about 60 %
relative humidity), dry composition with CO2 lumped into N2 (no carbon in the model); process
water demineralised at 1300 kPa(a), 303 K.
Reason: concept basis; leaving out CO2 removes a carbon species that is inert here (0.04 %).

## D-005 Burner model (2026-10-27)
Decision: adiabatic Pt/Rh gauze, 10.0 mol% NH3 in the feed, complete NH3 conversion, conversion
model with three parallel reactions: NH3_OX 0.955 (NO selectivity ASSUMED), NH3_N2O set so that
7 kg N2O/t HNO3 form (S1 Table 3.3, medium-pressure combustion plants: a dual-pressure plant burns
at medium pressure), NH3_N2 the remainder (0.026). Gauze outlet 1144 K from the adiabatic
balance (within S4's 750-920 degC).
Reason: no sourced selectivity was read in this run; a specification model is the declared basis
(cheme maturity: conversion, unsourced). The N2O formation uses an inventory default because the
issue asks to keep N2O formation apart from removal; it is not a gauze performance claim.
Rejected: equilibrium or kinetic gauze models (the selectivity is kinetic, catalyst- and
age-dependent; no rate law was sourced).
Assumptions: NH3 slip nil; Pt/Rh loss not modelled (open input O-3); the flammability of the
ammonia-air mixture makes the 10 % a controlled ratio (human judgement, not checked here).

## D-006 Components (2026-10-27)
Decision: NH3, N2, O2, Ar, H2O, NO, NO2, N2O, HNO3; N2O4 lumped into NO2; dissolved NOx in the
acid expressed as NO2. "NO" is quoted in every YAML file (unquoted it parses as false).
Reason: enough for nitrogen, oxygen and hydrogen balances across HNO3, NOx, N2O and N2, as the
issue requires.

## D-007 Cooler-condenser and weak acid (2026-10-27)
Decision: the process gas is cooled to 313 K in E-105; along it NO is oxidised and a 42 wt% weak
acid condenses; the gas leaves V-101 with 0.9 mol% water and NO2/(NO+NO2) = 0.5. E-105 is a
conversion reactor (NO_ABS 0.2981 and NO_OX 0.35095 of the NO entering, from the script); V-101
separates gas and acid (values from the script). The weak acid is pumped (P-101) to the absorber.
Reason: a specification model; strength, water content and oxidation degree are ASSUMED typical
values, not calculated (no HNO3-water VLE in core).

## D-008 Absorber and bleacher: specification model (2026-10-27)
Decision: C-101 is a specification model: the raw acid is 60 wt% HNO3 with 0.5 wt% dissolved
NOx (as NO2); the tail gas carries 500 ppmv NOx (all as NO), 3.0 mol% O2 and 0.4 mol% H2O. The
secondary air (15.3 % of the air) is set by the 3 % O2 and strips all dissolved NOx in C-102;
the bleacher gas returns to the NOx compressor. Process water follows from the water balance.
The overall reactions NO_ABS and NO2_ABS explain the extents (cheme checks them).
Reason: a conversion-only absorber does not establish predictive acid absorption (issue note);
core has no reactive-absorption or aqueous HNO3 model (the electrolyte issue closed for NaCl only).
This is the "sourced conceptual absorber" level the issue allows; the specifications are
ASSUMED, not sourced. No tray count, height or residence time is claimed.

## D-009 Tail-gas treatment and the unabated comparison (2026-10-27)
Decision: design case with tertiary treatment in R-102 at 703 K: N2O decomposed from the 7 kg/t
formed to the IPCC default 2.5 kg N2O/t HNO3 for plants with tail-gas N2O destruction (S1 Table
3.3), i.e. a conversion of 1 - 2.5/7 = 0.643, and SCR of 90 % of the NO with NH3 (no slip,
ASSUMED), NH3 vaporised on LP steam (E-108) above the tail-gas pressure. The tail gas is heated by
E-106 and E-103 and expanded in X-101.
Unabated alternative (same plant without N2O destruction, everything else equal): the N2O formed
leaves the stack, 7.0 g N2O/kg HNO3 instead of 2.5 (stream S27 carries the formed N2O to R-102:
291.7 kg/h; S29 104.2 kg/h). With the packaged IPCC AR6 GWP100 (273) the direct N2O is
1.91 kg CO2-eq/kg HNO3 unabated against 0.68 abated.
Reason: the issue asks for an unmitigated vs N2O-abatement comparison without silently importing
an abatement efficiency: the destruction here is not a catalyst performance but the ratio of two
published inventory defaults. S1 notes tertiary measures can exceed 99 % removal; plant-specific
performance needs measurements or a vendor guarantee (open input O-4).
Rejected: a second flowsheet case: step conversions are not per case in the flowsheet schema; the
comparison is derived from the formed and emitted N2O of the one balanced case.

## D-010 Independent heat and material balance (2026-10-27)
Decision: `scripts/hno3_balance.py` (run with `cheme run`) solves the fixed point of NH3 feed,
secondary air and the NOx recycle for D-002 to D-009 and the duties from ideal-gas enthalpies
(S5), liquid water and acid with formation enthalpies (S6), an ASSUMED heat of mixing of
-17 kJ/mol HNO3 (60 wt%) and -22 kJ/mol (42 wt%) and an ASSUMED acid heat capacity of
2.7 kJ/(kg K). Its values enter the flowsheet as `assumed` with the script as source; cheme
calculates the reactor outlets itself and propagates flows through machines, mixers and splitters,
and they agree with the script. Mass closes exactly; the script's energy balance closes to 6.7 kW
(the pump work) of 62 MW.
Reason: core cannot evaluate enthalpies for this mixture (`cheme process energy`: not evaluable).
Accuracy not stated; the heat of mixing and acid heat capacity move only the cooling-water duties.

## D-011 Utilities and machine train (2026-10-27)
Decision: cooling water 298/308 K; HP steam 4000 kPa(a), 673 K raised in E-102 and preheated in
E-104 (29.5 MW heat, about 38 t/h from BFW at 378 K), all exported; LP steam 450 kPa(a) only for
E-108. One train: X-101 (14.3 MW) drives K-101 (12.1 MW) and part of K-102 (6.4 MW); an electric
motor supplies the deficit (4.2 MW); drive and gear losses neglected. Isentropic efficiencies
ASSUMED: K-101 0.85, K-102 0.80, X-101 0.85, P-101 0.65. The NH3 evaporator E-101 (4.0 MW) takes
its heat from the absorber's chilled-water loop (energy stream C-101 -> E-101).
Reason: keeps steam export and compressor power separate, as the issue asks.
Rejected: a steam-turbine drive on the train (the common alternative: less steam export, no
power import); it is the main sensitivity of the LCI (about 4.2 MW of shaft from steam instead
of the grid).

## D-012 Core findings and workarounds (2026-10-27)
- Energy and phase properties: no property package covers the streams (`cheme process props
  --coverage`); the energy balance of every block is not evaluable in core (open).
- Aqueous nitric acid and reactive absorption: not supported; the core electrolyte issue was closed on 2026-10-27
  with NaCl-H2O Pitzer only ("no acids") and is not in the installed cheme 0.8.0.
- `cheme process build` (0.8.0, Python 3.15) crashes on a `Pumping` step: pyDEXPI's `method`
  annotation of Pumping is a union (`PumpingMethod | Undefined | None`) and `step_method` iterates
  it ("'typing.Union' object is not iterable"). Workaround: P-101 is a `TransportingFluids` step.
  To be reported to core.
- `process/simulation.yaml` only declares R-101 and R-102 adiabatic (boundary check), no
  simulation model. Superseded on 2026-10-30 by D-015 (a DWSIM input for the gas-phase part).
- `cheme maturity` prints V-101 (`SeparatingByFlash`) as "equilibrium-stage, predictive,
  sourced" although its outlets are script specifications (D-007) and no property package
  covers HNO3-water: the model basis is inferred from the step class without a model or package
  (review 2026-10-27-pfd-lci-review#4). Overstated in the printout only; the level (none) is
  unaffected. To be reported to core.

## D-013 Equipment list at concept stage (2026-10-27)
Decision: the 18 items the PFD needs, design pressure = highest operating + 10 % (at least
+2 bar), design temperature + 25 K, ASSUMED; materials first indications (austenitic stainless
304L for acid and wet nitrous gas below the azeotrope, heat-resistant alloy at the gauze and
boiler inlet), to be confirmed. No line or instrument list yet (no P&ID; lines come with the
P&IDs).

## D-014 Preliminary LCI: cradle-to-gate scope, backgrounds open (2026-10-27)
Decision: functional unit 1 kg contained HNO3 (1.667 kg of 60 wt% acid); every foreground
exchange from the balanced flowsheet (feeds NH3, air, process water; power, LP steam; products
acid, stack gas with its components, HP steam, heat to cooling water). Every background is left
unmapped (`missing:` with the activity it should connect to). The study boundary is
cradle-to-gate with every background open, so only the foreground is quantified; the generated
`dataset.yaml` calls itself "gate-to-gate foreground of the plant", which is the same thing seen
from the dataset (an unallocated foreground inventory). The exported HP steam is a co-product,
allocated by shares 1/0 (all burdens to the acid, the steam leaves without burden or credit;
system model cutoff, revised 2026-10-27 after the library's strict LCI export refused
substitution, PR #191 CI). This is a recorded deviation (`allocation.deviation`) from the
library hierarchy (energy or exergy for exported steam): the acid has no energy content, no
property package gives the acid's exergy (D-012), and the steam is counted in kWh so the WBCSD
price ratio does not apply. Substitution (avoided site steam, unmapped) stays as a comparison.
Catalysts (review 2026-10-27-pfd-lci-review#1): the Pt/Rh gauze loss is a consumable,
never cut, without a background, ASSUMED 0.15 g/t HNO3 gross loss (50 kg/a, Pt/Rh 90/10, no
catchment credit) until O-3 gives a sourced value; gauze fabrication and refining, the
N2O-decomposition and the SCR catalysts are `cutoff:` entries with unknown amounts (O-4, O-5).
The Pt consumable has no composition in core's dataset, so the element balance became
"not assessable" (mass balance still closes); to be raised with cheme-as-code. Direct emissions are
elementary flows to air (high stack); N2O is characterised by the packaged IPCC AR6 GWP100, NO
and the zero NH3/NO2/HNO3 are not characterised by it (gaps in the climate category). Equipment
leaks are excluded until a P&ID count exists; no tank, combustion unit or wastewater is inside
the boundary. Construction, catalysts and Pt loss are not in the inventory (open inputs O-3, O-5).
Result (`cheme assess lca --coverage`): partial screening carbon footprint; 0.68 kg CO2-eq/kg
HNO3 is the plant's direct N2O emission only, not the product's footprint (ammonia, power and
the other backgrounds are open); 10 gaps (9 before the Pt consumable, the HPS substitution gap
no longer counted under shares). Balance (`--balance`): mass and the
Ar, H, N, O element balances close (< 0.01 %); the reported energy closure (57.9 %) counts only
delivered utilities, not the reaction enthalpy (D-010 closes the energy).
Reason: the run's scope: a preliminary inventory, no background data and nothing from licensed
databases.

## D-015 DWSIM simulation inputs: boundary of the simulated part (2026-10-30)
Decision: `process/simulation.yaml` is now a complete DWSIM input for the gas-phase part of the
plant, so that `cheme process simulate` can run it where DWSIM is installed. It has not been run:
the authoring machine has neither DWSIM nor Docker, so no stream value comes from it and nothing
was filled (`--fill` not run). (Run since: D-016, 2026-11-01.) Checked offline with the cheme the library CI pins (core v1.2.1,
8042b716; first written against 1.1.0, core c2a45135, and core main 1.2.0, same results): the
file translates into a DWSIM model for case `design` (13 units, 8 compounds, no recycle;
`cheme maturity`: `predictive.simulation-spec` ok), `cheme validate` 0 errors.

Simulated (13 steps): ammonia split S-101, evaporator E-101, SCR ammonia vaporiser E-108, air
compressor K-101, air split S-102, mixer M-101, burner R-101 (adiabatic conversion reactor,
reactions.yaml conversions, D-005), waste-heat boiler E-102, tail-gas heater E-103 (both sides),
economiser E-104, NOx junction M-102, tail-gas exchanger E-106 (both sides) and NOx gas cooler
E-107. Every spec repeats a design choice already in D-003 to D-011 or in
`scripts/hno3_balance.py` (outlet temperatures, efficiencies, pressure levels), ASSUMED as the
choice it repeats. Two lumpings, ASSUMED: the let-down from the 1600 kPa(a) liquid ammonia is put
on E-101 (to 600 kPa(a)) and on E-108 (to 1300 kPa(a)), since the flowsheet has no valve steps;
DWSIM mixes at the lowest inlet pressure, so the 10 kPa the concept balance gave M-101 is put on
R-101 (30 kPa in all, D-003). M-102 has no next simulated item, so its outlet S20 will be at
465 kPa(a) against 460 assumed (a deviation warning, not an input change).

Left out (`exclude`), and why:

- the cooler-condenser E-105, the weak-acid separator V-101 and pump P-101, the absorber C-101
  and the bleacher C-102: they form, carry or absorb aqueous nitric acid. The DWSIM route has no
  electrolyte package and refuses HNO3 with water outright (`cheme.process-sim-electrolyte`,
  checked: the full flowsheet does not translate), and the absorption is a reactive absorption
  with no model in core (D-008; core #315). E-105 holds the NO oxidation (NO_OX) and the
  weak-acid formation (NO_ABS) in one step, so the NO oxidation cannot be simulated without the
  acid; it stays a specification (D-007).
- the absorber is not a `component_separator` (the core ADR 0019 / 0024 pattern of a specified
  split). Checked against core 1.1.0: that unit takes one material inlet and two outlets and
  keeps every component's flow; C-101 has three inlets (nitrous gas, weak acid, process water)
  and forms HNO3 from NO, NO2, O2 and water, so no set of recoveries represents it, and its HNO3
  would trip the electrolyte refusal anyway. C-102 has two inlets. Representing the absorption
  as a specified unit would need either a flowsheet split into a mixer, a conversion reactor and
  a component separator (still refused while HNO3 meets water in DWSIM) or a core unit for a
  specified reactive separator; neither is done here (follow-up F-1).
- the tertiary reactor R-102: two material inlets (tail gas S27 and SCR ammonia S05), the DWSIM
  conversion reactor takes one; the flowsheet has no mixer for the ammonia injection (F-2). Its
  `mode: adiabatic` stays in the file for the boundary check.
- the NOx compressor K-102 and the tail-gas expander X-101: the machine train is drawn as energy
  streams between units (Q01 X-101 -> K-101, Q02 X-101 -> K-102, Q03 motor -> K-102). Core 1.1.0
  (and core main 1.2.0, same code) refuses an energy stream between two simulated units and a
  unit with two energy streams in one direction (`cheme.process-sim-unmapped`), so X-101 can never
  be simulated with this flowsheet and K-102 neither; K-101 is simulated with X-101 left out (its
  power goes to Q01). The specs of K-102 and X-101 are written and translate once the train is
  decoupled (checked on a scratch copy with Q01 and Q02 removed: 15 units, no error); F-3.

Streams from the excluded steps into the simulated part (S16, S19, S21, S25) are feeds with their
flowsheet values; streams into them (S05, S14, S20, S23, S27) are simulated outlets.

Against the scope asked for this change (absorber as a specified `component_separator`, NO
oxidation and the tail-gas expander simulated), three parts are not met, each checked on a
scratch copy of this process with cheme 1.1.0, core main 1.2.0 and core v1.2.1 (same result):
the absorber as a `component_separator` is refused twice (`cheme.process-sim-unmapped`: three
material inlets, the unit takes one; `cheme.process-sim-electrolyte`: HNO3 with water); E-105
taken into the simulation is refused (`cheme.process-sim-electrolyte`), so the NO oxidation is
not simulated; X-101 with K-101 left out instead is still refused (`cheme.process-sim-unmapped`:
two energy streams Q01, Q02 out of the expander). The refusal of HNO3 applies to the whole model
as soon as HNO3 and water are among its compounds, whichever unit carries them, so no unit
choice in this file gets the absorber in. Meeting the asked scope needs the flowsheet changes
or the core units of F-1 to F-3, which are left for review (below).

Property package: Peng-Robinson. The recorded selection (polar, no interaction parameters,
1150 kPa) recommends PSRK or PR/RKS with modified Huron-Vidal mixing; the route runs none of them
and methods.yml names Peng-Robinson as their substitute. The substitution is not recorded as
accepted: that is a reviewer's call, so `cheme.process-sim-method-not-recommended` stays a
warning (and `predictive.property-package` fails) until a person accepts it. Known weak spots of
the gas-phase model: NO2 dimerisation to N2O4 is not modelled (D-006 lumps it into NO2), which
matters most in the cold, high-pressure NOx gas (E-106, E-107); water condenses in E-107 (water
partial pressure about 10.3 kPa against 7.4 kPa saturation at 313 K, CoolProp), and the model
keeps the condensate in the one outlet as water without NO2 dissolving or acid forming; the
absorber tail gas S25 (0.4 mol% water at 1100 kPa(a), 303 K) is slightly above its dew point
(4.4 against 4.25 kPa), so DWSIM may show a trace of liquid in that feed (D-008's water content
is a round ASSUMED figure).

Consequence for `cheme maturity`: `predictive.simulation-spec` now passes; `predictive.coverage`
fails (eight steps excluded) and stays failing until F-1 to F-3. V-101 is no longer reported as
"equilibrium-stage, predictive, sourced" (the overstatement of D-012): excluded, it shows as
stream values, specified.
Spec provenance: D-003 states only the pressure levels (520/490, 1150/1130/1100, 105 kPa(a)) and
ranges (5-20 kPa per exchanger, 30 kPa over R-102); the intermediate pressures and per-item drops
in simulation.yaml are the constants of scripts/hno3_balance.py and are cited as such. The script
takes 20 kPa over R-102 (P_E103C 1070 -> P_R102 1050), not D-003's 30 kPa; the X-101 inlet (1040)
follows the script. Left open for review (no change to the balance numbers here).
`vapor_association_expected` is recorded true (NO2/N2O4 is physically expected) although the
association is not modelled; at 1150 kPa the method recommendation does not change.
Rejected: changing the flowsheet (valves, an injection mixer, decoupled machine energy streams)
in this change: it would alter the BFD/PFD and the utility accounting the LCI uses, and is a
design decision for review, not a simulation input.
Follow-ups: F-1 aqueous HNO3 and reactive absorption in core (core #315; a specified reactive
separator unit as an interim); F-2 an ammonia-injection mixer step ahead of R-102 in the
flowsheet; F-3 a shaft-coupled machine train in core's DWSIM translation, or per-machine energy
streams in the flowsheet with the shaft balance stated outside; then run `cheme process simulate
--check` and, after review, `--fill`.

## D-016 First DWSIM run of the gas-phase part (2026-11-01)
Decision: the gas-phase model of D-015 is run with `cheme process simulate` (core v1.2.1, DWSIM
9.0.5 in the core Docker image `cheme-dwsim:9.0.5`, Peng-Robinson) and its results are filled:
the outlet streams and duties of the 13 simulated steps are now `calculated` (origin
`simulated`) in `process/flowsheet.yaml`, and the run is recorded in
`process/simulation-run.json`. The run converged on the first attempt (no recycle, one solver
pass, no solver message) with the specs of D-015 unchanged; no spec, guess or exclusion was
added. Energy closure: R-101 on the formation basis 3e-5 kW (tolerance 9.9 kW), plant 9e-5 kW
(tolerance 402 kW).

Stream values removed before `--fill`, so that the simulation writes them (they were pasted from
`scripts/hno3_balance.py` or propagated, and would otherwise stay and be reported as
deviations): outlet temperatures of K-101 (S07, S08, S09), M-101 (S10), R-101 (S11), E-103 hot
side (S13), M-102 (S20) and E-106 hot side (S22); the intermediate pressures that D-003 does not
state (S10, S12, S13, S14, S20, S22, S26, S27; script constants, D-015); every propagated flow
and composition of the simulated outlets; and the duties Q01 (K-101), Q05 (E-102), Q06 (E-104),
Q08 (E-107), Q11 (E-101), Q12 (E-108). Kept as ASSUMED: the feeds, the design choices that are
also specs (outlet temperatures of E-101, E-108, E-102, E-104, E-107, the E-103 and E-106 cold
outlets; the pressure levels of D-003, D-009, D-011), and every value of the excluded part. The
flows and compositions downstream of the excluded part that `cheme process propagate` writes
(S15, S21, S28) were propagated again from the simulated values (numbers unchanged to the
fifth digit). BFD/PFD rebuilt and the LCI outputs rewritten (`cheme assess lca --write`).

Simulation against the concept balance (`scripts/hno3_balance.py`, D-010; the values the
flowsheet held before this run):

| item | balance script | DWSIM (PR) | deviation |
|---|---|---|---|
| S07 K-101 discharge temperature | 487.82 K | 487.78 K | -0.04 K |
| Q01 K-101 power | 12055.9 kW | 12056.6 kW | +0.01 % |
| S10 burner inlet temperature | 463.04 K | 462.14 K | -0.9 K |
| S10 burner inlet pressure | 510 kPa(a) | 520 kPa(a) | +2.0 % (a) |
| S11 burner outlet temperature | 1143.72 K | 1144.07 K | +0.35 K |
| Q05 E-102 waste-heat boiler | 23574.0 kW | 23590.3 kW | +0.07 % |
| E-103 tail-gas heater (no energy stream) | 15224.9 kW | 15315.7 kW | +0.60 % (b) |
| S13 E-103 process-gas outlet | 551.21 K | 549.95 K | -1.3 K |
| Q06 E-104 economiser | 5939.8 kW | 5890.0 kW | -0.84 % |
| HP steam export (Q05 + Q06) | 29513.8 kW | 29480.3 kW | -0.11 % |
| S20 NOx compressor suction pressure | 460 kPa(a) | 465 kPa(a) | +1.1 % (a) |
| E-106 tail-gas exchanger (no energy stream) | 4610.6 kW | 4710.5 kW | +2.2 % (b) |
| S22 E-106 NOx-gas outlet | 345.11 K | 344.58 K | -0.5 K |
| Q08 E-107 NOx gas cooler | 1768.1 kW | 2035.7 kW | +15.1 % (c) |
| Q11 E-101 NH3 evaporator | 4003.3 kW | 4113.0 kW | +2.7 % (d) |
| Q12 E-108 SCR NH3 vaporiser | 16.2 kW | 16.7 kW | +3.0 % (d) |
| mass flows of all simulated streams | | | 0.00 % |

Reasons for the deviations:

- (a) model convention, not a balance difference: DWSIM mixes at the lowest inlet pressure, so the
  10 kPa the script gives M-101 sits on R-101 (S11 is 490 kPa(a) in both) and M-102's outlet is
  at the separator-gas pressure 465 kPa(a) (both foreseen in D-015).
- (b) the script uses ideal-gas enthalpies (D-010); Peng-Robinson adds the pressure dependence of
  the heat capacity at 1.1 MPa(a) on the tail-gas side. E-106 also evaporates the trace of liquid
  water DWSIM finds in the absorber tail gas S25 (D-015: S25 is slightly above its dew point;
  `sim-exchanger-zones` reports the phase change). Not separated further in this run.
- (c) water condenses in E-107 in the simulation and not in the script. Rough estimate, ASSUMED
  (round numbers, not a DWSIM output): S22 carries about 6750 kmol/h with 0.92 mol% water; at
  1130 kPa(a) and 313 K the saturated gas holds about 0.65 mol% (7.4 kPa, D-015), so about
  18 kmol/h condense, about 0.21 MW at about 43 kJ/mol, most of the 0.27 MW difference; the rest
  is again the real-gas heat capacity. The condensate stays in the one outlet S23 as pure water:
  in the plant it would take up NO2 and form weak acid, which neither model represents (D-015).
  The script's E-107 duty is the less complete figure; the absorber's cooling duty, which the
  script closes against it (D-010), is not re-balanced here.
- (d) property methods: the script takes liquid and vapour ammonia from CoolProp (a reference
  equation of state for ammonia); DWSIM takes them from Peng-Robinson, which is not qualified for
  liquid ammonia (below). The CoolProp figures are the better ones; the 2.7 % on E-101 is a
  property-method difference, not a balance error. The let-down lumped into E-101 and E-108
  (D-015) does not change the duty (an isenthalpic valve ahead of the evaporator gives the same
  total).

Property package, qualification status: unqualified for this mixture. Core's
`thermodynamics/methods.yml` benchmarks Peng-Robinson only for N2/O2/Ar (air separation) and NRTL
only for ethanol/water; nothing for NH3, H2O, NO, NO2 or N2O together with air (core #315).
`cheme process props --coverage` confirms that no package of core covers any stream here, and
`cheme maturity` fails `predictive.property-regime` and `predictive.property-package` (the
substitution of PR for PSRK / PR-MHV of D-015 is still not accepted by a reviewer). The
simulated values are therefore a consistency check of the concept balance with a second,
independent property method, not a qualified prediction. Formation enthalpies: DWSIM's (ChemSep)
differ from the ATcT values core falls back on by up to 839 kJ/kmol (NO); the burner reaction
heat differs by 88 kW, within the data tolerance (444 kW); no `dHf_298` is declared in
`process/materials.yaml` yet.

Findings left open (no change in this run):

- `cheme.process-sim-utility-level` (warning) on E-104: the economiser heats boiler feed water
  (378 K, D-011), but its energy stream Q06 goes to the HP steam terminal HPS, which declares
  673 K; the check therefore reports a level E-104's 453 K outlet cannot reach, and
  `predictive.exchangers` fails. A boiler-feed-water terminal (or one HP steam system terminal
  with the BFW inlet) would fix the declaration; it changes the flowsheet, the PFD and the LCI
  utility accounting, so it is left for review.
- no `min_approach` declared for E-103 (least approach 90 K) and E-106 (30 K) (info).
- the shaft balance: Q01 (K-101) is now simulated (12056.6 kW) while Q02 and Q03 stay the
  script's values computed with 12055.9 kW; 0.7 kW, below the balance tolerance.
- the absorber cooling duty Q09 and the CW total stay the script's; the LCI cooling-water output
  moves from 46741 to 47009 kWh/h (+0.6 %) through E-107 only; HP steam export from 29514 to
  29480 kWh/h (-0.1 %).

Checks run: `cheme process simulate --check` (converged; afterwards no stale value and no
deviation), `cheme process propagate --check`, `cheme validate` 0 errors / 0 warnings,
`cheme fmt`, `cheme assess lca --check` (current after `--write`), `cheme maturity` (above).
Reason: D-015 prepared the inputs on a machine without DWSIM; this is the run it left open.
Rejected: tuning specs, or treating the simulated values as better than the script's where the
simulation is the weaker model (ammonia enthalpies, the undrained E-107 outlet); the script stays
the balance of the excluded acid section.
Follow-ups: the open items above, and F-1 to F-3 of D-015 for the excluded part.

## Open inputs
- O-1: check D-005, D-008, D-011 against the BREF consumption and emission ranges (S2 sections 3.3, 3.4) with exact locators: NH3 per t HNO3 (here 0.285 t/t), steam export, power, cooling water, tail-gas NOx.
- O-2: a sourced NO selectivity for medium-pressure gauzes (with catalyst age), replacing 0.955.
- O-3: Pt/Rh loss per t HNO3 and gauze recovery (a precious-metal flow, never cut off).
- O-4: tertiary-abatement and SCR catalyst performance, volume and life (vendor or literature); permit limits for NOx and N2O.
- O-5: construction and consumables (catalysts) for the LCI; equipment weights.
- O-6: Atlas export of lca/dataset.yaml (library work outside this folder): the strict `scripts/build_lci.py` needs a chemicals-registry entry for ammonia (feed:NH3), `lci/mappings.yaml` entries for emission:NO, emission:HNO3 and consumable:pt-rh-gauze-loss, and a per-kWh steam-heat mapping for feed:LPS (the `steam` slug is per kg).
- O-6: ammonia purity, air filter, site conditions, steam-turbine vs motor drive (D-011).

## Chemicals registry items missing (for the consolidated library PR)
`ammonia` (substance; grade liquid anhydrous), `nitric-acid` (substance; grade 60 wt% aqueous,
reference product of this process), `nitrous-oxide` (emission), `nitric-oxide` or
`nitrogen-oxides` (emission). Present and used: air, water, steam, electricity, cooling-water,
nitrogen.
