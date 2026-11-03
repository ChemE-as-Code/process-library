# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Issue: ChemE-as-Code/process-library#302. Run of 2026-10-27 (concept: design basis to balanced
PFD and preliminary LCI: a cradle-to-gate study, foreground inventory only). Starting library commit 79a7cd4, cheme-as-code 0.8.0
(pyDEXPI 2.1.0, Python 3.15), thermo/chemicals as bundled with cheme.

## Route and boundary memo

**Route.** Thermal (non-catalytic) hydrodealkylation of toluene with hydrogen:
C7H8 + H2 -> C6H6 + CH4 (exothermic, -41.8 MJ/kmol at 298 K), with the reversible side
reaction 2 C6H6 <=> C12H10 + H2 (biphenyl, +15.0 MJ/kmol). Catalytic HDA (Cr/Mo oxide
catalysts, lower temperature) and toluene disproportionation (benzene plus xylenes) were not
chosen: the issue asks for the thermal HDA route with a diphenyl by-product, and
disproportionation has a different product slate.

**Plant boundary (battery limits).** From fresh toluene and make-up hydrogen at the battery
limit to benzene, biphenyl and fuel gas at the battery limit. Outside: toluene and hydrogen
production, product and feed storage, the site fuel gas system that burns the purge, utility
generation (steam boilers, cooling tower, power), flare. No process wastewater, on the
assumption of a dry vacuum pump on C-203 (D-008; steam ejectors would add an aromatic-bearing
condensate). This is the plant's design boundary; the LCA is a cradle-to-gate study of which
only the foreground inventory exists so far (D-013). Utilities
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

**Reference model (not used as data).** The IDAES HDA examples (issue #302) model this route
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

### D-005 Reaction model: specified conversion, selectivity from a recalled correlation (2026-10-27)
Decision: conversion reactor (cheme `reactor: conversion` with `selectivity:`): toluene
conversion X = 0.75 per pass (ASSUMED design variable); benzene formed per toluene converted
S = 1 - 0.0036/(1 - X)^1.544 = 0.96939 (Douglas 1988 HDA selectivity correlation, recalled and not read in this run, not verified: I-06); the rest of
the benzene goes to biphenyl (0.0153 kmol per kmol toluene converted). No kinetics: the
reactor volume is not sized. No other side reactions (hydrocracking to light paraffins,
methylbiphenyls, coke) until sourced selectivities exist.
Reason: a selectivity correlation for this route from the literature, used from memory at the concept stage;
no rate law is invented. The conversion of 0.75 is a typical design choice; it trades reactor
size against biphenyl make and recycle.
Results: extents HDA 167.865 kmol/h, BIPH 2.569 kmol/h, calculated identically by cheme and by
the script; benzene yield 0.949 mol per mol fresh toluene. cheme's ideal-gas reactor duty with
the given outlet temperature is -45 kW (against ~1.95 MW (7.0 GJ/h) reaction heat, i.e. 2.3 %): the script's adiabatic
outlet is consistent with cheme's formation data.
Open: the correlation's validity range (temperature, pressure, H2 ratio) and the exact form
are to be verified in the book (I-06). BIPH is reversible: cheme `process reactors` reports
ln(Q/K) = +0.14 at the outlet (937 K, ideal gas), i.e. the correlation's biphenyl make is
slightly beyond equilibrium. Within the accuracy of a correlation used at the concept stage,
but flagged: an equilibrium-limited biphenyl model would give a little less biphenyl.

### D-006 Independent balance script; property method not qualified (2026-10-27)
(Superseded in part by D-014: separator, column and duty values are now simulated; the
script is the comparison basis.)
Decision: separator, column, exchanger-side and duty values come from scripts/hda_balance.py
(thermo 0.6 Peng-Robinson with the ChemSep kij set, ideal-gas heat capacities of thermo,
formation enthalpies of process/materials.yaml), given in the flowsheet as `assumed` with the
script as source. cheme calculates mixers, splitters, pass-throughs and the reactor and checks
every balance.
Reason: core has no qualified package for aromatics with H2/CH4 (packaged ones: air,
syngas), so `props --fill` and `process simulate` cannot be used; the methanol-1
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
Results (C-202 values superseded by D-014: R 2.18, reboiler 3.48 MW, condenser 4.20 MW
without subcooling): C-201 reboiler 1.43 MW (MP steam), C-202 R 1.28, reboiler 2.30 MW (LP steam),
condenser 3.34 MW, C-203 reboiler 0.65 MW (HP steam). The vacuum system is taken as a dry
vacuum pump (ASSUMED, about 15 kW, not sized; I-08): no motive steam and no ejector
condensate, hence no process wastewater. Reflux and distillate pumps other than P-101 not
counted (each below about 5 kW, together about 15 kW, ASSUMED). Both are declared in
`lca/lca.yaml` as cut-off flows with these amounts (review 2026-10-27-pfd-lci-review#3).

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
(concept values). All ASSUMED. Two pressure rises have no pumping step on the PFD (D-011):
S17 leaves the splitter SPL2 at 3450 kPa(a) (implicit quench pump P-102, under 1 kW) and S23
leaves C-203 at 150 kPa(a) (implicit distillate pump); counting P-101 from 30 kPa(a) for its
whole flow over-states its power by under 1 kW and stands in for the distillate pump.
Results (superseded by D-014: fired heat 2915 kW, LP steam 3482 kW, HP 649 kW, cooling water
about 10.0 MW; MP steam stays 1431 kW from the script): power 266 kW, fired heat 2957 kW, steam
4381 kW (MP 1431, LP 2300, HP 650), cooling water 9207 kW.

### D-011 Core findings met in this run (2026-10-27)
- `cheme process build` (0.8.0) fails with `TypeError: 'typing.Union' object is not iterable`
  in `build.step_method` for step classes whose DEXPI `method` is optional (`Pumping`,
  `HeatingInFurnace`, `HeatingElectrical`, `SupplyingThermalEnergy`). Worked around: P101 is
  `GeneratingFlow`, H101 `ExchangingThermalEnergy` (both comments in flowsheet.yaml). To report
  to core; revert once fixed. Resolved 2026-11-03: core v1.4.1 builds both classes; reverted
  (D-016).
- `cheme process propagate` treats `Heating` as unknown; `HeatingInFurnace` is a pass-through.
- No property package for aromatics + H2 (as for methanol-1): energy closure,
  simulation and column design stay in the script.
- `cheme assess lca --write` writes a `total` row of 0 into `lca/results.csv` (and 0 in the
  allocation table of `results.md`) although every contribution is a gap, and the library's
  catalog builder takes that row with `lca: {source: auto}`, which would publish 0 kg CO2-eq
  per kg benzene. Worked around: process.yaml `lca: {source: none}` until a background is
  linked (review 2026-10-27-pfd-lci-review#1). To report to core and the library tooling.

### D-012 Lists (2026-10-27)
Decision: equipment list of the PFD items (18) and one line per PFD material stream (24).
Design pressure: highest operating pressure + 10 % (at least + 2 bar), one 42 barg design for
the reactor loop; design temperature + 25 K. Line DN from velocity (gas 15 m/s above 1000
kPa(a), 20 below, two-phase 10, liquid 1.5 m/s) on PR densities. Materials in hot hydrogen
(E-101, H-101, R-101) are an open input (Nelson curves, refractory lining, I-09). All ASSUMED.

### D-013 Preliminary LCI: cradle-to-gate study, foreground inventory only (2026-10-27)
Decision: `lca/lca.yaml` with functional unit 1 kg benzene at the gate (product BENZENE),
design case; every foreground exchange from the flowsheet; no background linked: every feed,
utility and avoided product `missing:` with the activity it should connect to. Co-products
BIPHENYL and FUELGAS by energy (LHV) allocation in the exported dataset (benzene share
71.5 %; `dataset.system_model: cutoff`), system expansion (substitution, ISO 14044's
preference) and mass allocation (benzene 76.5 %) computed for comparison. Revised
2026-10-27 from substitution as the default: the library's LCI export (`scripts/build_lci.py`)
writes one activity per co-product and refuses a non-proportional default, which failed the
PR #189 tooling tests; the WBCSD price-ratio rule cannot apply without prices, so the choice
of energy is stated as `allocation.deviation` (the fuel gas is an energy carrier and all
products are hydrocarbons with similar LHVs). LHVs calculated from the formation enthalpies of materials.yaml with CODATA CO2
and H2O values (benzene product 40.58, biphenyl product 39.65, fuel gas 54.25 MJ/kg).
H-101 combustion emissions are excluded from the foreground because the intended background
(heat from natural gas at an industrial furnace, per MJ) includes them; storage tanks are
outside the boundary. Fugitive emissions (benzene, toluene, H2, CH4 from flanges, seals,
valves) are not estimated: they need a P&ID component count (I-10). No construction inventory.
The allocation method and the backgrounds are the LCA practitioner's decisions (proposal only).
Boundary label: `cradle-to-gate` (lca.yaml `boundary`), not the schema's `gate-to-gate`, which
would map every feed free and hide the missing upstream; the study is cradle-to-gate with only
its foreground inventory so far, every background a gap. Declared omissions in lca.yaml:
fugitive leaks (not estimated, not claimed negligible, I-10), no process effluent (dry vacuum
pump, D-008), and the vacuum-pump and small-pump power as cut-off flows with their ASSUMED
amounts (D-008). Benzene and biphenyl LHVs are kept on the gas basis like the fuel gas (a liquid
basis moves benzene's energy share by about 0.2 percentage points). The catalog gets no LCA
result while every background is a gap (process.yaml `lca.source: none`, D-011).
Publication: `publication: public` in `lca/manifest.json` and `results.md` is cheme's verdict on
the licences of the sources the results rest on (no restricted source), i.e. that they *may* be
published; whether the process *is* published is process.yaml `publication.status`, which is
`internal` and governs (review 2026-10-27-pfd-lci-review#10).
Note 2026-11-01: the owner has since marked all 50 processes public, so this one is no longer internal.
Results: see the LCI summary below.

### D-014 First DWSIM simulation of the whole plant (2026-11-01)
Decision: run `cheme process simulate` on the whole flowsheet with nothing excluded (core
v1.2.1, DWSIM 9.0.5 in the `cheme-dwsim:9.0.5` container, Peng-Robinson). The script's
`assumed` stream values and duties are replaced by the simulated ones (`calculated`), except
the stabiliser duties Q5 and Q6. The specs are in `process/simulation.yaml`; each repeats a
D-004, D-007, D-008 or D-010 choice or is marked ASSUMED. The run converged in 11 iterations.
cheme tore three loops (S9, S15, S23) and needed no guesses. The plant enthalpy closure is
-0.3 kW (tolerance 19 kW); the R-101 closure on the formation basis is -0.001 kW. The run
record is `process/simulation-run.json`.
Changes the run needed (none moves a design target):
- R-101: DWSIM takes one conversion per reaction, not a selectivity. The D-005 model is written
  as two toluene-keyed reactions in `reactions.yaml`: HDA at X * S = 0.7270415, and the lumped
  HDABP (TOL + 0.5 H2 -> 0.5 BIPH + CH4, i.e. HDA twice plus BIPH) at X * (1 - S) = 0.0229585.
  The extents are those of the selectivity (HDA 162.73 kmol/h, HDABP 5.139 kmol/h, i.e.
  2.570 kmol/h biphenyl) and do not depend on the inlet benzene. BIPH stays declared.
- C-202 reflux: the D-008 rule R = 1.3 Rmin is kept, but applied to DWSIM's Underwood minimum
  of 1.674 (R = 2.18) instead of the script's 0.985 (R = 1.28). The script takes the feed as
  saturated liquid (q = 1), a simplification it states itself. In fact the stabiliser bottoms
  arrive at 800 kPa(a) and 448 K and partly flash at 150 kPa(a). R = 1.28 is below DWSIM's
  minimum, and the run did not converge with it.
- C-201 and C-202 are DWSIM shortcut (Fenske-Underwood-Gilliland) columns with the D-002/D-008
  key specs. Where the script puts none of a key in a product, a small value is ASSUMED (C-201:
  1e-5 CH4 in the bottoms).
- C-203 is a rigorous column, because its shortcut result gave bottoms fractions that add up
  to 1.004. Specs: 10 stages and feed stage 5 (ASSUMED, from the shortcut's 5.97 stages at
  R 0.5), R 0.5, bottoms 401.05 kg/h. The bottoms flow is D-008's 2 mol% toluene applied to
  the simulated biphenyl make; a mole-fraction spec did not converge. Result: 2.06 mol% toluene
  in the bottoms.
- P-101 needs `unit: pump` (it is drawn as GeneratingFlow, D-011).
Kept with the deviation visible (the `sim-deviation` warnings are not silenced):
- Pressures behind the implicit pumps (D-010). DWSIM's mixers take the lowest inlet pressure,
  so S2 and S23 are at 30 kPa(a) (the C-203 top), not 150 kPa(a). S9 to S11 are 130 kPa below
  the D-004 values, because Q-101 takes S17's 3250 kPa(a) instead of the 3450 kPa(a) pump
  discharge. The V-101 flash pressure (3250 kPa(a)) is a spec, so the loop pressure does not
  change. The fix is the pumping steps of review #6, once core's Pumping bug (D-011) is fixed.
- S21 is specified at 313.15 K (D-008: subcooled product) but simulated at 366.2 K. The
  flowsheet has no product cooler step, so Q8 is the condenser duty alone. The subcooling duty
  is not counted: about 0.3 MW (ASSUMED estimate: 12.5 t/h of liquid benzene cooled from 366 K
  to 313 K at about 1.8 kJ/(kg K)). Open (I-12).
- C-201: the off-gas S19 stays at 313.15 K, and the duties Q5 and Q6 stay from the script.
  DWSIM's shortcut column with a partial condenser put the off-gas at anywhere from 58 to 201 K
  in repeated runs, while the dew point of that composition is 313.4 K (thermo PR). Its
  condenser duty (24-102 kW) and reboiler duty (1284-1325 kW) are therefore not used. C-201's
  split (from the key specs) is used. A review rerun reproduced the split, S20's temperature
  and every downstream C-202/C-203 value identically while the C-201 duties and the S19
  temperature varied (30/1286 kW, 173.7 K), so the split is repeatable. S19's composition
  and flow come from that shortcut: its toluene (0.00113) is less than half the script's
  equilibrium value (0.00295), about 1 kg/h of fuel gas. S19 and S22 fractions sum to
  1.00002 and 1.00017 (shortcut residue).
- S17 is simulated at 3250 kPa(a), not the assumed 3450 kPa(a) quench-pump discharge
  (D-010, implicit P-102); same cause as S9 to S11.
Values that are set by a spec, not predicted, although flowsheet.yaml records them as
simulated: S19 benzene fraction 0.0269 (C-201 heavy key in distillate, from the script's S19),
the C-202 benzene in bottoms 0.0142627 (the script's 99.5 % recovery) and the S24 flow
401.05 kg/h (C-203 bottoms spec).
Simulation compared with the old balance (scripts/hda_balance.py, the values on main before
this run):

| quantity | script | DWSIM | deviation |
|---|---|---|---|
| R-101 outlet T (S8) | 936.82 K | 937.92 K | +1.1 K |
| E-101 hot outlet T (S10) | 394.53 K | 393.48 K | -1.0 K |
| E-101 duty | 24.5 MW | 24.39 MW | -0.5 % |
| H-101 duty (Q3) | 2956.5 kW | 2914.6 kW | -1.4 % |
| E-102 duty (Q4) | 4926.0 kW | 4891.2 kW | -0.7 % |
| K-101 power (Q2) | 229.7 kW | 229.5 kW | -0.1 % |
| P-101 power (Q1) | 36.5 kW | 36.7 kW | +0.6 % |
| separator gas S12 | 29278.8 kg/h, 40.00 mol% H2 | 29287.7 kg/h, 40.00 mol% H2 | +0.03 % |
| separator liquid S16 | 23504.2 kg/h | 23502.6 kg/h | -0.01 % |
| purge S13 | 3260.5 kg/h | 3261.5 kg/h | +0.03 % |
| H2/aromatics at R-101 inlet | 5.00 | 5.00 (4.997) | -0.06 % |
| stabiliser off-gas S19 | 172.5 kg/h | 171.2 kg/h | -0.8 % |
| benzene product S21 | 12500 kg/h, 99.9 mol% | 12498.5 kg/h, 99.89 mol% | -0.01 % |
| toluene recycle S23 | 4935.9 kg/h | 4935.8 kg/h | 0.00 % |
| biphenyl S24 | 401.03 kg/h, 478.6 K | 401.05 kg/h (spec), 473.1 K | -5.5 K |
| C-202 Underwood Rmin / R | 0.985 / 1.28 | 1.674 / 2.18 | +70 % |
| C-202 reboiler (Q7) | 2300.3 kW | 3481.8 kW | +51 % |
| C-202 condenser (Q8) | 3336.4 kW (incl. subcooling) | 4202.7 kW (condenser only) | +26 % |
| C-203 reboiler (Q9) | 649.5 kW | 649.2 kW | -0.05 % |
| C-203 condenser (Q10) | 788.0 kW | 790.5 kW | +0.3 % |

The reactor loop, the flash and C-203 agree within about 1.5 % (1 K for temperatures). Both
sides are implementations of Peng-Robinson, with different kij sets and ideal-gas data, so the
agreement checks the arithmetic, not the property model. The one large difference is C-202's
energy (+1.2 MW LP steam, +0.9 MW cooling water), which comes from the feed condition the
script simplified. The utility totals move with it (LP steam 3.48 MW, cooling water about
10.0 MW).
IDAES tutorial reference (PR #296, IDAES/examples-pse at commit b9606ee, base case): not
numerically comparable. The tutorial shares two specs with this design: the per-pass toluene
conversion of 0.75 and the adiabatic stoichiometric reactor. It differs in scale (0.3 mol/s
toluene), pressure (350 kPa), reactor inlet temperature (600 K), property basis (ideal VLE,
four components, no biphenyl) and separation (two flashes, no columns). The quantities it
reports have no counterpart here: the benzene purity of the second flash's vapour, that
flash's duty, and an operating cost on its own price factors. A three-way check needs the
reference case itself run through DWSIM (open decision). The IDAES adapter run of this design
(PR #297) has not converged, so there is no second simulator result yet.
Property package: not qualified. core's `methods.yml` benchmarks Peng-Robinson only for
N2/O2/Ar and NRTL only for ethanol-water. Aromatics with H2 and CH4 at 30-37 bar(a) and up to
938 K lie outside every benchmarked claim (core#315). `cheme maturity` therefore fails
`predictive.property-regime`, and the run is a cross-check, not validated data. DWSIM's ChemSep
formation enthalpies differ from materials.yaml by -14 to +300 kJ/kmol (biphenyl -688). That
is 1.2 kW on the reaction heat, within the data tolerance.
What it supersedes for the simulated values: D-006's statement that `process simulate` cannot
be used (it runs; the qualification gap stays), the C-202 results of D-008, the utility
results of D-010, and the notes of equipment-list.yaml C-202/E-203/E-204 (updated). The file
fingerprints in simulation-run.json differ from the committed files only through later
comment and `propagate --fill`/`fmt` edits; the model fingerprint is current. The LCI outputs in `lca/` were regenerated
from the simulated duties. The LCI summary table below predates this run;
`lca/inventory.csv` is current.

### D-015 IDAES cross-check of the toluene feed section (2026-11-02)
Decision: the plant's simulation stays the DWSIM model of D-014 (`process/simulation.yaml`,
`process/simulation-run.json`). The IDAES backend (core ADR 0039, core#104, released in core
v1.4.0) was run as a second, independent implementation on the part of the flowsheet it can
represent; its spec and run record are in git at commit 118c0de7 (`process/simulation.yaml`
with `simulator: idaes`, `process/simulation-run.json`), on the flowsheet as it was before
D-014's values were merged (script values, D-006). They are not kept as files: a plant has one
`process/simulation.yaml`, and on the current flowsheet IDAES refuses every boundary (below).
Boundary: M100 + P101 (feeds S1, S23), the rest excluded:
- biphenyl (BIPH, CAS 92-52-4) is not a compound of either IDAES package (benzene, toluene,
  hydrogen, methane only); on the script's flowsheet every stream from M101 on carries it (the
  recycle gas S15 1.5e-7 mol/mol, so S5-S7 too), so M101, H101, R101, Q101, E102, V101, SPL1,
  K101 and SPL2 were refused (reproduced with M101 alone and H101 alone in the boundary);
- E101 (two-sided exchanger) and the columns are unit kinds the backend does not build.
- Since D-014, S23 is DWSIM's result and carries 4.7e-9 biphenyl, so M100 and P101 are refused
  too: on the current flowsheet IDAES can simulate no part of hda-1 without changing a design
  value. Extending it needs core changes (biphenyl in an IDAES package, a two-sided exchanger, a
  column), not design changes.
Convergence: the first IDAES run (2026-11-01) stopped at IPOPT's iteration limit on M100 alone.
Root cause, found by running core's worker directly, fixed in core#124: (1) IDAES's smooth VLE
puts the equilibrium temperature between the bubble and dew points with a 5e-4 K smoothing;
for S1, pure toluene with the worker's 1e-8 benzene trace, the two points are about 3e-7 K
apart, so a subcooled S1 had no solution (or, smoothed tighter, a free vapour fraction); (2)
IDAES's `BT_ideal` liquid heat-capacity coefficients were read a thousand times too small
(labelled J/kmol/K, numerically kJ/kmol/K), so the mixer's energy balance had no physical
answer. Not the benzene trace itself: S1 stays pure toluene. With core#124 the run converged
(IPOPT optimal, 3 iterations; M100 and P101 enthalpy closures within 1e-10 kW). The run record
at 118c0de7 was written by the core#124 branch before its release (it reports cheme-as-code
1.3.0); core#124 is released in core v1.4.1, and `cheme process simulate --check` of the
118c0de7 files with v1.4.1 (2026-11-02) gives the same values (P101 35.5147 kW, S3 314.87 K,
plant closure within 2e-11 kW). The run record's enthalpy-reference label names DWSIM's basis;
that is a core labelling fault for IDAES runs (core#125), not a property of this run.
Property packages: `IDAES ideal VLE` (Raoult's law, ideal gas, IDAES's example component data)
is not benchmarked by cheme-as-code (`process-sim-method-unbenchmarked`); `IDAES
Peng-Robinson` still does not converge on the pure-toluene S1; the script's Peng-Robinson
(thermo, ChemSep kij) and DWSIM's are not qualified for this mixture either (core#315). The
comparison is a consistency check between implementations, not a validation.

| Quantity | scripts/hda_balance.py | IDAES ideal VLE (118c0de7) | DWSIM PR (D-014) | IDAES - script | Why |
| --- | --- | --- | --- | --- | --- |
| S2 temperature | 313.70 K | 313.62 K | 313.75 K | -0.08 K | ideal vs PR liquid enthalpies |
| S2/S3 flow | 20454.2 kg/h | 20454.2 kg/h | 20454.1 kg/h | 0 | same mass balance |
| S3 temperature (P-101 outlet) | 313.70 K | 314.87 K | 315.85 K | +1.17 K | the script neglects the pump's temperature rise (D-010) |
| Q1 P-101 power | 36.5 kW | 35.51 kW | 36.7 kW | -2.7 % | IDAES pumps from 150 kPa(a); the script and DWSIM from 30 kPa(a) (C-203 distillate pump included, D-010, D-014). Scaled by hand to 150-3600 kPa(a) the script's is 36.5 x 3450/3570 = 35.27 kW (IDAES +0.7 %, liquid density) |
| R-101, V-101, K-101, columns | D-006 | out of scope (BIPH, E101) | D-014 | n/a | |

Rejected: replacing D-014's whole-plant DWSIM model by the IDAES feed-section model (it would
drop a converged, reviewed simulation of the whole plant); lumping biphenyl into toluene or
dropping its traces to fit the backend (changes the design's balance, D-005, D-008); raising
S1's benzene to make the smooth VLE solvable (a design change to work around a solver
formulation).

### D-016 Concept close-out: review findings, open inputs and the PFD classes (2026-11-03)
Decision: close the concept stage (section S1 of `runs/plan.md`) with core v1.4.1 (DWSIM 9.0.5
unchanged). The last four open findings of review 2026-10-27-pfd-lci-review and the open
inputs I-01 to I-12 are closed or carried below; each carried item names the reason and the
section of `runs/plan.md` that takes it up.
PFD classes (review #7): core v1.4.1 builds `Pumping` and `HeatingInFurnace` (tested in a copy
of the plant, then here). P101 is `Pumping` and H101 `HeatingInFurnace` again, so the PFD draws
a pump and a fired heater. The workaround of D-011 is reverted, and no core issue is needed.
`cheme process build` rebuilt the BFD and PFD with core v1.4.1. `cheme process simulate --check`
(DWSIM 9.0.5, 2026-11-03) on the changed flowsheet gives the D-014 values: P101 36.72 kW, E101
24388 kW, H101 2914.64 kW, C202 3481.76/4202.66 kW, plant closure -0.36 kW. Its only warnings
are the `sim-deviation` warnings D-014 keeps visible. It reports no stale record.
Skills: `cheme skills update` installed the 132 bundled skill files (skills are not in git);
`cheme skills status` reports 132 current, 0 outdated, 0 modified, so no outdated skill was
left to update.
Open inputs:
- I-01 fresh toluene specification: kept ASSUMED (pure toluene, D-003). No supplier, and the
  commercial grade standards (e.g. ASTM D841 nitration-grade toluene) are not open, so no
  values were taken from them. Effect: `cheme maturity` fails `maturity-sourced-boundary`
  (S1 flow and composition not given with a source). Taken up when a supplier or an owner
  gives the grade.
- I-02 make-up hydrogen: kept ASSUMED (95/5 mol% H2/CH4 at 3700 kPa(a), D-003). The TEA prices
  it as grey (SMR) hydrogen bought over the fence (D-019). Same maturity effect for S4.
- I-03 benzene grade: kept ASSUMED (99.9 mol%, D-002). Thiophene and non-aromatics are not
  modelled: the feeds carry no sulfur or paraffins. The ASTM refined-benzene standards
  (D2359, D4734) are not open.
- I-04 capacity and hours: kept ASSUMED (100 kt/a, 8000 h/a). No owner figure exists.
- I-05 site: resolved as a notional site in the Rotterdam area (ASSUMED), the same region as
  ammonia-1. It gives the price basis (Eurostat NL series, D-019) and the plot plan (D-018).
  Climate, grid and utility conditions stay those of D-010.
- I-06 Douglas (1988) values: carried (review #4). No open copy of the book was available, and
  copies circulating without the publisher's licence are not used. No openly licensed source
  that states the correlation with its locator was found. The reactor window, the H2 ratio and
  the selectivity stay labelled recalled and unsourced. Effect: `maturity-balanced-model-basis`
  fails for R101 (conversions assumed). Needs a person with the book to give the chapter and
  equation (S2 or before).
- I-07 purge hydrogen recovery: carried to S2 (simulation close-out). The TEA puts a figure on
  the question. The purge S13 carries about 238 kg/h of H2 (3261 kg/h at 40 mol% H2, mass
  fraction 0.073), credited as fuel at about 1.37 EUR/kg (11.397 EUR/GJ x 120 MJ/kg LHV,
  ASSUMED). Make-up hydrogen is priced at 2.78 EUR/kg. Recovering it would be worth at most
  about 2.7 MEUR/a gross, before the recovery unit's cost and power.
- I-08 C-203 vacuum system and small pumps: carried to S7 (datasheets). The class 5 estimate
  covers them with the uncovered allowance (D-019).
- I-09 hot-hydrogen materials: carried to S3 and S7 (the P&IDs and datasheets: Nelson-curve
  check after API RP 941, lining of R-101). The estimate prices E-101 in stainless steel and
  R-101 as a refractory-lined carbon-steel shell (ASSUMED, D-019).
- I-10 fugitive emissions: carried to S4 (component counts from the P&IDs).
- I-11 LCI backgrounds and allocation: carried. They are the LCA practitioner's decisions, and
  no section of `runs/plan.md` covers the LCA. Effect: no LCA result (process.yaml
  `lca.source: none`).
- I-12 benzene product cooler and the stabiliser model: carried to S2. The subcooling duty
  (about 0.3 MW) is in the TEA neither as cooling water nor as equipment; the uncovered
  allowance names the cooler.
Review findings: #4 carried (as I-06); #7 closed (classes above); #9 carried (as I-11: the
side-by-side result needs linked backgrounds); #12 closed (plot plan, D-018, gate
`layout-plot-plan` passes).

### D-017 Concept sizes for the plot plan and the class 5 estimate (2026-11-03)
Decision: give every equipment-list item overall `dimensions` from a concept sizing
(`scripts/concept_sizing.py`, run with `cheme run`). It works on the simulated duties and
streams of `process/simulation-run.json` (D-014) and the script's C-201 duties. The results are
rounded up into the equipment list. Every coefficient is a concept choice of this design
(ASSUMED), not a value from a publication, and the datasheets (S7) replace all of them.
- Exchangers: A = Q/(U LMTD), counter-current, clean. U is 300 W/(m2 K) for E-101 (gas/gas
  with phase change) and E-201, 400 for E-102, 600 for E-205, 700 for E-203 and E-206, and 800
  for the reboilers E-202 and E-204. Areas: E-101 1309 m2 (two shells in series), E-102 302,
  E-201 20, E-202 76, E-203 96, E-204 265, E-205 32, E-206 17 m2. The C-201 condensing range
  (350 to 313 K) is ASSUMED.
- Columns: diameter from the larger of the top and bottom vapour loads at an F-factor of
  2.0 Pa^0.5 and 85 % active area. Height from the theoretical stages at a tray efficiency of
  0.7, 0.6 m spacing and 5 m for sump, top and skirt. Latent heats are the simulated condenser
  duties over the condensed vapour (benzene 381, toluene 384 kJ/kg; the toluene value is also
  used for the biphenyl bottoms). Stages: C-202 38.0 (DWSIM shortcut), C-203 10 (D-014), C-201
  8 (ASSUMED, more than the shortcut's 3.0 for a stabiliser). Results: C-201 D 0.82 m to 1.0 m,
  H 12.5 m; C-202 D 2.05 m to 2.2 m, H 38 m; C-203 D 1.25 m to 1.4 m, H 14 m.
- V-101: Souders-Brown K 0.07 m/s with a mesh pad, liquid density 850 kg/m3 (ASSUMED). D 1.17 m
  to 1.4 m, H 5 m including 5 min of liquid. V-100: 10 min of liquid at half full, 8.0 m3, so a
  horizontal drum D 1.8 m x 3.6 m.
- R-101: no rate law (D-005), so no volume follows from the model. D 2.5 m x 9 m (44 m3, about
  25 s at the 1.72 m3/s inlet gas flow) is a placeholder for the layout and the estimate only.
- Machines: P-101 36.7 kW and K-101 229.5 kW (DWSIM), P-102 0.55 kW (calculated), H-101
  2914.6 kW absorbed. A vertical cylindrical heater D 4 m x 14 m and the package sizes of the
  pumps and K-101 are ASSUMED.
Reason: the plot plan needs footprints and heights, and the class 5 estimate needs a size per
item. Without kinetics or rating, a duty-based concept size is the most that can be defended.
Rejected: sizes from memory of similar plants (no basis to cite).

### D-018 Concept plot plan (2026-11-03)
Decision: a notional 180 m x 125 m plot in the Rotterdam area (`layout/site-plan.yaml`), with
one east-west pipe rack PR-1 (y = 50 m from x = 20 to 160 m, 8 m wide, tiers 6 and 8 m, bents
every 10 m) and the two process areas north of it. A-100 holds reaction and gas recycle, with
the fired heater H-101 at its west end, away from the hydrogen machinery and the distillation
area. A-200 holds stabilisation and distillation: C-201 and C-203 within 30 m of the rack for
their lines, C-202 (38 m) set back one height from it, reboilers beside their columns and
condensers in a row next to the rack. South of the rack are three reserved plots: A-900
(control room and substation), A-800 (utility interface) and A-300 (the interface to the tank
farm outside the boundary). Roads on all four sides and road R-5 between the process areas
give each process area access from at least two sides. All 18 items are placed
(`layout/equipment-placement.yaml`) at grade. Condensers, reboilers and the column structures
get their elevations at basic engineering (gate `layout-3d`).
Spacing criteria (separations): all are ASSUMED screening values chosen in this design, not
taken from a standard. The owner's spacing standard and a QRA replace them at basic.
- H-101: 30 m from the site boundary, K-101, the A-200 area and the A-900 plot; 15 m from
  V-101, V-100 and P-101.
- Toppling (one height): C-201, C-202, C-203, R-101 and H-101 from PR-1.
- A-900: 45 m from K-101 and C-202, and 30 m from V-101.
Measured (`cheme show <tag> --layout`, 2026-11-03):
- H-101: 31.0 m to the site boundary, 35.5 m to K-101, 26.3 m to V-100, 27.6 m to P-101,
  58.0 m to A-200, 50.0 m to A-900, 36.0 m to PR-1.
- C-202: 44.9 m to PR-1 (height 38 m); C-201 25.5 m (12.5 m); C-203 25.3 m (14 m); R-101
  36.8 m (9 m).
- A-900: 60.4 m to K-101, 91.1 m to C-202, 43.2 m to V-101.
- V-101: 25.3 m to PR-1.
`cheme layout build`: 18 items, no clash, no steel in a road (the bents at x = 90 and 100 m
stand clear of R-5), no blocked maintenance envelope. `cheme validate` reports no
`layout-separation` or `layout-line-route` finding. A first arrangement with the columns
further north left the toluene recycle TO-123 out of the rack's 30 m reach, and a rack
spanning to x = 165 m put a bent in R-5. Both were moved, not accepted. The plan was not
rendered as a picture: PNG output needs the `resvg` extra, which is not installed with core
v1.4.1 here, and the SVG (`cheme layout render --plan`) was not viewed. The layout review at
basic engineering looks at it.
Reason: concept gate `layout-plot-plan`. An area layout in process order along one rack is the
usual arrangement, and it keeps the flame of H-101 away from the hydrogen and benzene.
Open: the real plot, wind rose and neighbours (I-05), nozzles and line routes (with the
P&IDs), hazardous-area zones, and the tank farm, flare and utilities outside the boundary.

### D-019 Class 5 capital estimate and screening TEA (2026-11-03)
Decision question: proceed to basic engineering of the 100 kt/a thermal HDA plant in the
Rotterdam area? It is answered by whether the levelised cost of producing benzene (LCOP) is at
or below the benzene price, 673.6 EUR/t (`estimate/tea.yaml`, metric `lcop`).
Capital (AACE class 5, `estimate/cost-basis.yaml`, `estimate/equipment-cost.md`):
- Bare module costs of the 18 items from the Turton et al. CAPCOST correlations of the core
  package at the D-017 sizes, CEPCI 797.9 (2023, the openly readable annual value, as
  ammonia-1). The result is 5.08 MUSD for 16 items.
- E-101 is priced as two shells of 654 m2 (upper estimate, its area is over the correlation's
  range), 1.64 MUSD, in stainless steel. K-101 is priced at the correlation's minimum of 450 kW
  and P-102 at 1 kW, both upper estimates below the range. V-100 is priced with the vertical
  vessel correlation, the only vessel correlation with a bare module factor.
- H-101 has a purchased cost only, 1.11 MUSD, installed x 2.5 (ASSUMED).
- USD to EUR at 1/1.0813 (Eurostat 2023). Escalation 2023 to 2025 x 1.052 (Eurostat NL NACE
  C28 producer prices, the ammonia-1 proxy). Location factor 1.0 (ASSUMED, no open factor
  found). Uncovered allowance 15 % (ASSUMED: trays and internals, the R-101 lining, the vacuum
  pump, small pumps, spares, the product cooler).
- ISBL 10.6 MEUR. OSBL 0.30 (ASSUMED, a unit on an existing site); owner's cost 0.07 and
  contingency 0.20 (IEAGHG 2017-03 values used as an analogue, ASSUMED). Fixed capital
  17.7 MEUR; class 5 range 8.9 to 35.4 MEUR.
Prices (2025 EUR):
- Toluene 668.1 EUR/t and benzene 673.6 EUR/t: Eurostat Comext 2025 unit values of Dutch
  toluene imports and benzene exports, trade statistics used as price proxies, ASSUMED.
- Make-up hydrogen 2.78 EUR/kg H2: European Hydrogen Observatory, Netherlands SMR levelised
  cost 2024, incl. CO2 cost, the latest published year. Its methane is priced at the gas price.
- Natural gas 11.397 EUR/GJ GCV and power 100.65 EUR/MWh (Eurostat NL bands I6 and IG, 2025,
  excluding VAT). Fired heat 53.56 EUR/MWh absorbed (efficiency 0.85 LHV, ASSUMED). Steam
  45.59 EUR/MWh (boiler 0.90 on GCV, ASSUMED, all levels alike). Cooling water 2.85 EUR/MWh
  (the calculation of ammonia-1's product:CW price, same 10 K rise).
- Fuel gas and biphenyl credited as fuel at the gas price per GJ LHV (ASSUMED, conservative).
  No open biphenyl price was found.
- CO2 of H-101 at 0.2376 t/MWh absorbed (IPCC 2006 default 56.1 t/TJ) at 74 EUR/t (EUA 2025),
  no free allocation (ASSUMED). The fuel gas and steam CO2 is emitted outside the boundary and
  not charged.
- Fixed cost: 25 operators at 80 kEUR, maintenance 3 % and insurance 1 % of fixed capital.
  Real discount rate 8 %, tax 25.8 %, 25 years, 8000 h/a (all as ammonia-1, ASSUMED).
Results (`cheme assess tea --write`, `estimate/tea.md`):
- LCOP 874.3 EUR/t against 673.6 EUR/t: not met. Cash cost 853.6 EUR/t, NPV -147 MEUR, no IRR.
  P(meets) 5.9 % (Monte Carlo P10/P50/P90 LCOP 707/876/1084 EUR/t).
- Cost of production per t benzene: feeds 969.5, utilities 37.2, CO2 4.1, co-product credits
  -184.3, fixed 27.1, capital and tax 20.6 EUR/t.
- The toluene price dominates (Spearman +0.94). The decision turns at toluene 506.5 EUR/t
  (-24 %), i.e. a benzene-toluene spread of at least about 167 EUR/t against 5.5 EUR/t in the
  2025 trade values. Capital never turns it within the tested range (class 5 high x 2:
  902 EUR/t).
- Scenario prices-2024 (benzene 978.7, toluene 818.5 EUR/t, spread 160 EUR/t): LCOP 1061 EUR/t
  against benzene at 978.7 EUR/t, still short.
What it means for the next stage: at 2025 and 2024 price levels a stand-alone thermal HDA unit
buying toluene does not pay. Its economics are a benzene-toluene spread and a hydrogen
question (I-07), not a capital question. The engineering of the case study goes on as a design
exercise (issue #302). An investment case would need a contract spread or an integrated site
with cheap hydrogen and its own toluene. That is the owner's decision, not this file's.
Rejected: a scaled reference plant cost (no open, citable HDA plant cost was found); the
WBCSD-style co-product price split (the LCA keeps energy allocation, D-013).
Not covered: working capital, the product subcooling duty (I-12), storage and loading.
`cheme assess tea` reports two infos: the hydrogen price is of 2024, and P(meets) is below the
decision's confidence.

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
| IDAES HDA examples | none used | issue #302 links | read only as context; no data taken |

## Source register

| source | locator | access in this run | terms | use |
|---|---|---|---|---|
| Douglas (1988) Conceptual Design of Chemical Processes, McGraw-Hill | HDA case study (chapter and equation to verify) | not read (recalled) | book, facts cited only | reactor window, H2 ratio, selectivity correlation |
| Speight (2011) Handbook of Industrial Hydrocarbon Processes, Elsevier | Ch. 11 | via the library skill tech-petchem-aromatics | facts cited only | HDA temperature/pressure range |
| `chemicals`/`thermo` Python packages (bundled with cheme) | ATcT, CRC, Yaws, HEOS, IUPAC, TRC ideal-gas, ChemSep PR kij | used | MIT; underlying data facts | formation data, critical constants, PR flash |
| Cox, Wagman, Medvedev (1989) CODATA Key Values | CO2(g), H2O(g) formation enthalpies | recalled values | facts | LHV for allocation |
| IDAES examples-pse v2.0.0 HDA documentation | URLs in issue #302 | not opened in this run | BSD-style licence of IDAES (to record before any reuse) | context only |

## Method and dependency table

| step | method | status |
|---|---|---|
| Mass, component, element balances | cheme validate / process streams | closed |
| Reactor outlet | cheme conversion reactor with selectivity | calculated by cheme |
| Mixers, splitters, pass-throughs | cheme process propagate | calculated by cheme |
| Flashes, column splits, duties | `cheme process simulate` (DWSIM 9.0.5, PR), D-014; C-201 duties from scripts/hda_balance.py | calculated; property package not qualified (core#315) |
| Energy closure in core | `cheme process props --fill` | gated: no package for aromatics + H2 |
| Simulation | `cheme process simulate` (DWSIM) | converged, whole plant (D-014); property regime not qualified |
| BFD/PFD build | `cheme process build` | works; P101 `Pumping`, H101 `HeatingInFurnace` since core v1.4.1 (D-016) |
| LCI | `cheme assess lca --inventory/--coverage/--balance` | written; backgrounds open |

## Open inputs

Status 2026-11-03 (D-016): I-05 resolved (notional Rotterdam-area site); I-01 to I-04 kept
ASSUMED; I-06 to I-12 carried, each with its reason and section in D-016.

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
- I-12 A benzene product cooler step (S21 to 313 K) and a stabiliser model whose partial
  condenser DWSIM solves (a rigorous column with a vapour product), D-014.

## Missing library registry entries (chemicals/chemicals.yaml, for the consolidated PR)

toluene, benzene (with a product grade, e.g. 99.9 mol%), biphenyl (diphenyl), natural gas
(or fired heat from natural gas), fuel gas (refinery/plant off-gas), steam grades at 4.5,
15 and 42 bar(a) (only `steam/mp-11bara` exists).
