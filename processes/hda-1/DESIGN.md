# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Issue: ChemE-as-Code/process-library#42. Run of 2026-10-27 (concept: design basis to balanced
PFD and preliminary gate-to-gate LCI). Starting library commit 79a7cd4, cheme-as-code 0.8.0
(pyDEXPI 2.1.0, Python 3.15), thermo/chemicals as bundled with cheme.

## Route and boundary memo

**Route.** Thermal (non-catalytic) hydrodealkylation of toluene with hydrogen:
C7H8 + H2 -> C6H6 + CH4 (exothermic, -41.8 MJ/kmol at 298 K), with the reversible side
reaction 2 C6H6 <=> C12H10 + H2 (biphenyl, +15.0 MJ/kmol). Catalytic HDA (Cr/Mo oxide
catalysts, lower temperature) and toluene disproportionation (benzene plus xylenes) were not
chosen: the issue asks for the thermal HDA route with a diphenyl by-product, and
disproportionation has a different product slate.

**Boundary (gate-to-gate).** From fresh toluene and make-up hydrogen at the battery limit to
benzene, biphenyl and fuel gas at the battery limit. Outside: toluene and hydrogen production,
product and feed storage, the site fuel gas system that burns the purge, utility generation
(steam boilers, cooling tower, power), wastewater (none from the process), flare. Utilities
cross the boundary as energy streams (power, fired heat, three steam levels, cooling water).

```
 toluene ─┐                                   ┌─> purge ─────────────────┐
          ├─> RXN: pump, mix, FEHE, heater,   │                          ├─> fuel gas
 H2 make-up┘   adiabatic reactor, quench,  ───┤                          │
               cooler, HP separator,          └─> liquid ─> SEP: stabiliser ─> off-gas
               recycle compressor (gas recycle)              benzene column ─> benzene
          ^                                                  toluene column ─> biphenyl
          └──────────────── toluene recycle <────────────────┘
```

**Reference model (not used as data).** The IDAES HDA examples (issue #42) model this route
with a specified reaction, flash separation and recycle/purge. Their flowsheet values are not
used: feeds, scale, conversion, specifications and topology here are this study's own
choices (D-001). Not a reference reconstruction: a comparison with IDAES is a separate job
whose expected outputs are held by the evaluator.

## Decisions

### D-001 Independent concept design of thermal HDA (2026-10-27)
Decision: design the plant from the route chemistry and openly cited facts, with the units of
the issue: reactor, quench, flash, H2 recycle with purge, stabiliser, benzene and toluene
columns, toluene recycle, diphenyl by-product.
Reason: the case notes ask for an independent design; the issue's IDAES reference may be cited
but not copied.
Rejected: reconstructing the IDAES tutorial (a separate, reproduction-type job).

### D-002 Capacity and product specification (2026-10-27)
Decision: 100 kt/a benzene product stream at 8000 h/a = 12.5 t/h; 99.9 mol% benzene
(99.88 wt%), toluene the only impurity; turndown 60 % not checked.
Reason: a mid-size single train chosen for the study (ASSUMED, no client figure).
Assumptions: a commercial benzene grade (ASTM D2359 / D4734) also limits thiophene,
non-aromatics, colour and freezing point; none is modelled (open input I-03).

### D-003 Feeds (2026-10-27)
Decision: fresh toluene pure, 303 K, 300 kPa(a); make-up hydrogen 95 mol% H2 / 5 mol% CH4 at
3700 kPa(a), 313 K, available above loop pressure (no make-up compressor).
Reason: a reformer-type hydrogen purity is the usual basis of HDA design studies; ASSUMED.
Open: real feed purities and supply pressure (I-01, I-02).

### D-004 Reactor loop conditions (2026-10-27)
Decision: adiabatic empty-vessel reactor, inlet 895.15 K / 3450 kPa(a), outlet 3380 kPa(a);
effluent quenched with separator liquid to 893.15 K; feed/effluent exchanger to 840 K cold
outlet; fired heater 840 -> 895 K; trim cooler to 313.15 K; HP separator 3250 kPa(a);
recycle compressor 3250 -> 3600 kPa(a); toluene feed drum at 150 kPa(a). Pressure drops
(70 kPa per heater/exchanger side, 60 kPa cooler) ASSUMED.
Reason: Douglas (1988) gives a reactor inlet of at least about 895 K (1150 F) for an adequate
rate, an outlet below about 980 K (1300 F) to limit hydrocracking, about 3.45 MPa (500 psia),
H2/aromatics of at least 5 at the inlet, and a quench of the effluent (recalled, not read in
this run: locator to verify, I-06). The tech-petchem-aromatics skill (Speight 2011, Ch. 11)
gives 500-600 C and up to about 69 bar: the temperature ranges disagree (see evidence table);
the inlet chosen is in Douglas's range and above Speight's. The adiabatic outlet (936.8 K) is
below the hydrocracking limit.
Results: FEHE minimum internal approach 53 K (20-point profile, scripts/hda_balance.py), duty
24.5 MW; combined feed vapour fraction 0.92 at 321 K.

### D-005 Reaction model: specified conversion, sourced selectivity (2026-10-27)
Decision: conversion reactor (cheme `reactor: conversion` with `selectivity:`): toluene
conversion X = 0.75 per pass (ASSUMED design variable); benzene formed per toluene converted
S = 1 - 0.0036/(1 - X)^1.544 = 0.96939 (Douglas 1988 HDA selectivity correlation); the rest of
the benzene goes to biphenyl (0.0153 kmol per kmol toluene converted). No kinetics: the
reactor volume is not sized. No other side reactions (hydrocracking to light paraffins,
methylbiphenyls, coke) until sourced selectivities exist.
Reason: a published, widely used selectivity correlation for this route at the concept stage;
no rate law is invented. The conversion of 0.75 is a typical design choice; it trades reactor
size against biphenyl make and recycle.
Results: extents HDA 167.865 kmol/h, BIPH 2.569 kmol/h, calculated identically by cheme and by
the script; benzene yield 0.949 mol per mol fresh toluene. cheme's ideal-gas reactor duty with
the given outlet temperature is -45 kW (against ~7 MW reaction heat): the script's adiabatic
outlet is consistent with cheme's formation data.
Open: the correlation's validity range (temperature, pressure, H2 ratio) and the exact form
are to be verified in the book (I-06). BIPH is reversible: cheme `process reactors` reports
ln(Q/K) = +0.14 at the outlet (937 K, ideal gas), i.e. the correlation's biphenyl make is
slightly beyond equilibrium. Within the accuracy of a correlation used at the concept stage,
but flagged: an equilibrium-limited biphenyl model would give a little less biphenyl.

### D-006 Independent balance script; property method not qualified (2026-10-27)
Decision: separator, column, exchanger-side and duty values come from scripts/hda_balance.py
(thermo 0.6 Peng-Robinson with the ChemSep kij set, ideal-gas heat capacities of thermo,
formation enthalpies of process/materials.yaml), given in the flowsheet as `assumed` with the
script as source. cheme calculates mixers, splitters, pass-throughs and the reactor and checks
every balance.
Reason: core has no qualified package for aromatics with H2/CH4 (packaged ones: air,
syngas; core #315), so `props --fill` and `process simulate` cannot be used; the methanol-1
pattern.
Results: loop residual 3.5e-10; overall mass 16334.02 in / 16334.04 kg/h out; overall energy
closure 7978.3 kW in / 7958.4 kW out (19.9 kW, 0.25 %; the neglected pump temperature rise is
36.5 kW).

### D-007 Recycle and purge (2026-10-27)
Decision: specify H2/aromatics = 5 mol/mol at the reactor inlet and 40 mol% H2 in the purge;
the script finds purge fraction 0.11136 of the separator gas and make-up 815.7 kg/h. Purge to
the fuel gas header; no hydrogen recovery (membrane/PSA) in this design.
Reason: the ratio of 5 is Douglas's lower limit against coking; the purge H2 fraction is the
usual economic decision variable of this loop (ASSUMED value, not optimised).
Results: recycle gas 2353 kmol/h (26.0 t/h), loop methane 49-59 mol%; hydrogen utilisation
(H2 consumed / H2 fed) about 56 %; aromatics lost to fuel gas 258 kg/h (mostly benzene in the
purge). Open: purge H2 recovery and a vent absorber that keeps benzene out of the fuel header
(skill tech-petchem-aromatics question) are basic-engineering options (I-07).

### D-008 Separation train (2026-10-27)
Decision: stabiliser C-201 at 800 kPa(a), partial condenser at 313.15 K, L/D 1, all H2 and CH4
overhead with the aromatics in equilibrium with an aromatic reflux; benzene column C-202 at
150/170 kPa(a), 99.5 % benzene recovery, distillate 99.9 mol%; toluene column C-203 under
vacuum at 30/45 kPa(a) so that the biphenyl bottoms (2 mol% toluene, 479 K) can be reboiled
with HP steam; reflux 1.3 x Underwood minimum (constant relative volatility from vapour
pressures), at least 0.5 (C-203's Underwood minimum is 0.02). Benzene product subcooled to
313 K in the condenser train. Duties from column energy balances with the arriving feed
enthalpy. Stage numbers not calculated.
Reason: the issue's unit list; vacuum avoids a fired or hot-oil reboiler on C-203.
Results: C-201 reboiler 1.43 MW (MP steam), C-202 R 1.28, reboiler 2.30 MW (LP steam),
condenser 3.34 MW, C-203 reboiler 0.65 MW (HP steam). The vacuum system (ejector steam or
vacuum pump power) is not counted (I-08). Reflux and distillate pumps other than P-101 not
counted (each below about 5 kW, ASSUMED).

### D-009 Fuel and co-product dispositions (2026-10-27)
Decision: H-101 fired with purchased natural gas (energy feed `FUEL`, absorbed duty 2.96 MW);
purge and stabiliser off-gas exported as fuel gas (3433 kg/h, LHV 54.3 MJ/kg); biphenyl sold
or burned (401 kg/h).
Reason: keeps the flowsheet free of a combustion section at the concept stage. Burning the
purge in H-101 (its LHV, ~49 MW, far exceeds the heater duty) is the usual alternative and
would make the plant a net fuel gas exporter either way.

### D-010 Utilities and machines (2026-10-27)
Decision: cooling water 298.15/308.15 K; LP steam 450 kPa(a) (420.8 K), MP 1500 kPa(a)
(471.4 K), HP 4200 kPa(a) (526.4 K), saturated; electric drives; compressor isentropic
efficiency 0.75, pump efficiency 0.65 (P-101 power counted from 30 kPa(a), i.e. it includes
the C-203 distillate pump); fired-heat supply temperature 1200 K and minimum approach 50 K
(concept values). All ASSUMED.
Results: power 266 kW, fired heat 2957 kW, steam 4381 kW (MP 1431, LP 2300, HP 650), cooling
water 9207 kW.

### D-011 Core findings met in this run (2026-10-27)
- `cheme process build` (0.8.0) fails with `TypeError: 'typing.Union' object is not iterable`
  in `build.step_method` for step classes whose DEXPI `method` is optional (`Pumping`,
  `HeatingInFurnace`, `HeatingElectrical`, `SupplyingThermalEnergy`). Worked around: P101 is
  `GeneratingFlow`, H101 `ExchangingThermalEnergy` (both comments in flowsheet.yaml). To report
  to core; revert once fixed.
- `cheme process propagate` treats `Heating` as unknown; `HeatingInFurnace` is a pass-through.
- No property package for aromatics + H2 (core #315, as for methanol-1): energy closure,
  simulation and column design stay in the script.

### D-012 Lists (2026-10-27)
Decision: equipment list of the PFD items (18) and one line per PFD material stream (24).
Design pressure: highest operating pressure + 10 % (at least + 2 bar), one 42 barg design for
the reactor loop; design temperature + 25 K. Line DN from velocity (gas 15 m/s above 1000
kPa(a), 20 below, two-phase 10, liquid 1.5 m/s) on PR densities. Materials in hot hydrogen
(E-101, H-101, R-101) are an open input (Nelson curves, refractory lining, I-09). All ASSUMED.

### D-013 Preliminary gate-to-gate LCI (2026-10-27)
Decision: `lca/lca.yaml` with functional unit 1 kg benzene at the gate (product BENZENE),
design case; every foreground exchange from the flowsheet; no background linked: every feed,
utility and avoided product `missing:` with the activity it should connect to. Co-products
BIPHENYL and FUELGAS by system expansion (substitution, ISO 14044 preference;
`system_model: substitution`), energy (LHV) and mass allocation compared (benzene share 71.5 %
and 76.5 %). LHVs calculated from the formation enthalpies of materials.yaml with CODATA CO2
and H2O values (benzene product 40.58, biphenyl product 39.65, fuel gas 54.25 MJ/kg).
H-101 combustion emissions are excluded from the foreground because the intended background
(heat from natural gas at an industrial furnace, per MJ) includes them; storage tanks are
outside the boundary. Fugitive emissions (benzene, toluene, H2, CH4 from flanges, seals,
valves) are not estimated: they need a P&ID component count (I-10). No construction inventory.
The allocation method and the backgrounds are the LCA practitioner's decisions (proposal only).
Results: see the LCI summary below.

## LCI summary (lca/inventory.csv, per kg benzene)

| exchange | amount | unit | provenance (flowsheet) | background to link later |
|---|---|---|---|---|
| feed:TOLF toluene | 1.24146 | kg | S1 (assumed, script) | toluene, market for (reformate/pygas extraction) |
| feed:H2MU make-up H2 (95/5 mol% H2/CH4) | 0.06526 | kg | S4 | hydrogen from SMR / refinery network (+ CH4) |
| feed:POWER | 0.02130 | kWh | Q1, Q2 | electricity, medium voltage, site grid |
| feed:FUEL fired heat | 0.23652 | kWh | Q3 | heat from natural gas, industrial furnace |
| feed:MPS steam 1500 kPa(a) | 0.11451 | kWh | Q5 | steam in chemical industry (MP) |
| feed:LPS steam 450 kPa(a) | 0.18402 | kWh | Q7 | steam in chemical industry (LP) |
| feed:HPS steam 4200 kPa(a) | 0.05196 | kWh | Q9 | steam in chemical industry (HP) |
| product:CW heat rejected | 0.73658 | kWh | Q4, Q6, Q8, Q10 | cooling water circulation |
| product:BENZENE | 1 | kg | S21 | functional unit |
| product:DIPHENYL biphenyl | 0.03208 | kg | S24 | avoided biphenyl or fuel oil |
| product:FUELGAS | 0.27464 | kg | S13 + S19 | avoided natural gas firing |

Checks: `cheme assess lca --balance` mass 16334 kg/h in and out (residual -0.01 kg/h), C
14340.4/14340.5, H 1993.58/1993.57 kg/h: closed. By hand against the flowsheet: in 1.30672 kg
(1.24146 + 0.06526), out 1.30672 kg (1 + 0.03208 + 0.27464). Stoichiometric toluene minimum
1.180 kg/kg benzene: the 5 % above it is biphenyl make and aromatics in the fuel gas.
`--coverage`: result "partial screening carbon footprint" with no total (all 10 contributions
are gaps), boundary check: no gap, DQR 2.33 (weakest technological representativeness),
primary data share 0 %. No impact result is claimed.

## Reaction and model evidence

| item | value used | source | status |
|---|---|---|---|
| Stoichiometry HDA, BIPH | as reactions.yaml | route chemistry | sourced (textbook chemistry) |
| Heats of reaction | -41.76, +15.04 MJ/kmol | formation enthalpies (chemicals: ATcT, CRC) | calculated |
| Reactor T range | inlet >= ~895 K, outlet <= ~980 K | Douglas 1988, HDA case study | recalled, not read in this run; locator to verify |
| Reactor T range (conflict) | 500-600 C, up to ~69 bar | Speight 2011 Ch. 11, via skill tech-petchem-aromatics | cited in library skill; disagrees with Douglas (may refer to catalytic processes); to resolve |
| Pressure | 3.45 MPa | Douglas 1988 | recalled; within Speight's limit |
| H2/aromatics >= 5 | 5 | Douglas 1988 | recalled |
| Selectivity correlation | S = 1 - 0.0036/(1 - X)^1.544 | Douglas 1988 | recalled; validity range to verify |
| Conversion per pass | 0.75 | design choice | ASSUMED |
| Kinetics | none | - | not used; reactor volume not sized |
| IDAES HDA examples | none used | issue #42 links | read only as context; no data taken |

## Source register

| source | locator | access in this run | terms | use |
|---|---|---|---|---|
| Douglas (1988) Conceptual Design of Chemical Processes, McGraw-Hill | HDA case study (chapter and equation to verify) | not read (recalled) | book, facts cited only | reactor window, H2 ratio, selectivity correlation |
| Speight (2011) Handbook of Industrial Hydrocarbon Processes, Elsevier | Ch. 11 | via the library skill tech-petchem-aromatics | facts cited only | HDA temperature/pressure range |
| `chemicals`/`thermo` Python packages (bundled with cheme) | ATcT, CRC, Yaws, HEOS, IUPAC, TRC ideal-gas, ChemSep PR kij | used | MIT; underlying data facts | formation data, critical constants, PR flash |
| Cox, Wagman, Medvedev (1989) CODATA Key Values | CO2(g), H2O(g) formation enthalpies | recalled values | facts | LHV for allocation |
| IDAES examples-pse v2.0.0 HDA documentation | URLs in issue #42 | not opened in this run | BSD-style licence of IDAES (to record before any reuse) | context only |

## Method and dependency table

| step | method | status |
|---|---|---|
| Mass, component, element balances | cheme validate / process streams | closed |
| Reactor outlet | cheme conversion reactor with selectivity | calculated by cheme |
| Mixers, splitters, pass-throughs | cheme process propagate | calculated by cheme |
| Flashes, column splits, duties | scripts/hda_balance.py, PR (thermo) | ASSUMED values; gated by core #315 for qualification |
| Energy closure in core | `cheme process props --fill` | gated: no package for aromatics + H2 (core #315) |
| Simulation | `cheme process simulate` (DWSIM) | not run: property regime not qualified (core #315) |
| BFD/PFD build | `cheme process build` | works with class workarounds (D-011) |
| LCI | `cheme assess lca --inventory/--coverage/--balance` | written; backgrounds open |

## Open inputs

- I-01 Fresh toluene specification (purity, C8 aromatics, non-aromatics, sulfur, water).
- I-02 Make-up hydrogen purity and supply pressure (source of hydrogen).
- I-03 Benzene product grade to meet (thiophene, non-aromatics, freezing point).
- I-04 Capacity and operating hours from an owner (100 kt/a and 8000 h/a are assumed).
- I-05 Site (utilities, grid, climate).
- I-06 Verify the Douglas (1988) values at their locator (reactor window, ratio, correlation and
  its validity range); resolve the conflict with Speight's 500-600 C.
- I-07 Purge hydrogen recovery and a benzene absorber on the purge; purge to H-101 as fuel.
- I-08 Vacuum system of C-203 (ejector steam or vacuum pump power) and the small pumps.
- I-09 Materials for hot hydrogen service (E-101, H-101, R-101) and reactor lining.
- I-10 Fugitive emission estimate (needs P&ID component counts) and non-routine emissions.
- I-11 Background datasets for every LCI exchange (all gaps) and the allocation decision.

## Missing library registry entries (chemicals/chemicals.yaml, for the consolidated PR)

toluene, benzene (with a product grade, e.g. 99.9 mol%), biphenyl (diphenyl), natural gas
(or fired heat from natural gas), fuel gas (refinery/plant off-gas), steam grades at 4.5,
15 and 42 bar(a) (only `steam/mp-11bara` exists).
