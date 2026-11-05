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
production, product and feed storage, the site fuel gas system that burns the PSA tail gas and the stabiliser off-gas (D-024), utility
generation (steam boilers, cooling tower, power), flare. No process wastewater, on the
assumption of a dry vacuum pump on C-203 (D-008; steam ejectors would add an aromatic-bearing
condensate). This is the plant's design boundary; the LCA is a cradle-to-gate study of which
only the foreground inventory exists so far (D-013). Utilities
cross the boundary as energy streams (power, fired heat, three steam levels, cooling water).

```
 toluene ─┐                                   ┌─> purge ─> HRU: PSA ─> tail gas ─┐
          ├─> RXN: pump, mix, FEHE, heater,   │      (H2 back to K-101) K-102  ├─> fuel gas
 H2 make-up┘   adiabatic reactor, quench,  ───┤                                 │
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
Since D-024 (2026-11-04): the purge is drawn at the K-101 discharge and goes to a PSA; the specs
(ratio 5, 40 mol% H2 in the purge) are kept.

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
Since D-024 (2026-11-04): the exported fuel gas is the PSA tail gas and the stabiliser off-gas,
2968 kg/h at 50.66 MJ/kg (41.8 MW); H-101 would need 8.6 % of it.

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
  (350 to 313 K) is ASSUMED. The two E-101 shells (about 654 m2 each, as priced in D-019) are
  stacked (ASSUMED), so the list's D 1.6 m x 9 m is the footprint of both; the stacked height
  comes with the 3D layout at basic engineering.
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
  V-101, V-100, P-101 and E-101 (flanged, 42 barg hot hydrogen; added after the review of
  PR #320, measured 26.8 m).
- No openly readable spacing guideline with a citable locator was found for these values
  (the usual industry tables are paywalled), so they stay ASSUMED, as in ammonia-1 D-022.
- Toppling (one height): C-201, C-202, C-203, R-101 and H-101 from PR-1.
- A-900: 45 m from K-101 and C-202, and 30 m from V-101.
Measured (`cheme show <tag> --layout`, 2026-11-03):
- H-101: 31.0 m to the site boundary, 35.5 m to K-101, 26.3 m to V-100, 27.6 m to P-101,
  26.8 m to E-101, 58.0 m to A-200, 50.0 m to A-900, 36.0 m to PR-1.
- C-202: 44.9 m to PR-1 (height 38 m); C-201 25.5 m (12.5 m); C-203 25.3 m (14 m); R-101
  36.8 m (9 m).
- A-900: 60.4 m to K-101, 91.1 m to C-202, 43.2 m to V-101.
- V-101: 25.3 m to PR-1.
`cheme layout build`: 18 items, no clash, no steel in a road (the bents at x = 90 and 100 m
stand clear of R-5), no blocked maintenance envelope. `cheme validate` reports no
`layout-separation` or `layout-line-route` finding. A first arrangement with the columns
further north left the toluene recycle TO-123 out of the rack's 30 m reach, and a rack
spanning to x = 165 m put a bent in R-5. Both were moved, not accepted. Viewed 2026-11-03:
the SVG of `cheme layout render --plan` (build/layout-plan.svg), opened in a browser and
looked at as a whole-sheet screenshot. It shows the 18 items inside A-100 and A-200, the rack
PR-1 south of both areas with its bents, the four perimeter roads and R-5 between the areas,
and the three reserved plots south of the rack. No item lies on a road or the rack, and no
footprint overlaps another. At the A1 sheet scale the tags are small but readable when zoomed
in. Nothing was changed as a result. The drawing shows no separation circles; the distances
above come from `cheme show`. (PNG output needs the `resvg` extra, which is not installed.)
Wind: H-101 (40, 92) lies about 20 degrees east of north of the toluene feed drum V-100 (30, 64)
and the feed pump P-101 (40, 62). In S to SW winds, which are common on the Dutch coast, the
heater is therefore downwind of their possible leaks. The arrangement is kept for the concept,
because the distances meet the criteria, but it is a point for the layout review once the
real wind rose is known (I-05). If the prevailing wind is SW, move V-100/P-101 east or
north-east of H-101, or upwind of it.
Reason: concept gate `layout-plot-plan`. An area layout in process order along one rack is the
usual arrangement. It keeps the flame of H-101 at the separation distances from the hydrogen
and benzene inventories. Its position relative to the wind is still open (above).
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
- H-101 has a purchased cost only, 1.11 MUSD, installed x 2.5 (ASSUMED). The package holds no
  fired-heater bare module, pressure or material factor (a core limit, core#129). Turton et
  al., Appendix A, gives them, but the printed tables could not be read here. The 2.5 is
  likely low for alloy tubes at 42 barg in hot hydrogen, and the class 5 range covers it.
  The `estimate-equipment-partial` warning stays open until the factors come from the book.
- USD to EUR at 1/1.0813 (Eurostat 2023). Escalation 2023 to 2025 x 1.052 (Eurostat NL NACE
  C28 producer prices, the ammonia-1 proxy). Location factor 1.0 (ASSUMED, no open factor
  found). Uncovered allowance 15 % (ASSUMED: trays and internals, the R-101 lining, the vacuum
  pump, small pumps, spares, the product cooler, and the K-101 electric drive of about 300 kW,
  an explosion-proof motor with its starter, which the compressor correlation excludes and no
  package correlation covers, core#129).
- ISBL 10.6 MEUR. OSBL 0.30 (ASSUMED, a unit on an existing site); owner's cost 0.07 and
  contingency 0.20 (IEAGHG 2017-03 values used as an analogue, ASSUMED). The 20 % is a class 4
  contingency, low for class 5; the class 5 range applied in the uncertainty and in scenario
  capex-class5-high covers the difference. Fixed capital 17.7 MEUR; class 5 range 8.9 to
  35.4 MEUR.
Prices (2025 EUR):
- Toluene 668.1 EUR/t and benzene 673.6 EUR/t: Eurostat Comext 2025 unit values of Dutch
  toluene imports and benzene exports, trade statistics used as price proxies, ASSUMED. The
  difference between an import and an export unit value is not a traded spread. The flows
  have different delivery terms (CIF-like against FOB-like), grades and partners, and one
  year's value is weak evidence. The 2025 spread depends on the choice of flow: 5.5 EUR/t
  (benzene exports minus toluene imports, the baseline), 38.6 EUR/t (both imports: benzene
  706.7) or -134.7 EUR/t (both exports: toluene 808.3). It is not a market spread.
- Make-up hydrogen 2.78 EUR/kg H2: European Hydrogen Observatory, Netherlands SMR levelised
  cost 2024, incl. CO2 cost, the latest published year. Its methane is priced at the gas price.
  The generated `estimate/tea.md` row of feed:H2MU shows only the CH4 (Eurostat gas) source:
  `cheme assess tea --write` prints the last component's source only (core#129). The H2 part,
  about 12.8 MEUR/a, is sourced to the European Hydrogen Observatory ('Hydrogen production
  costs 2024.xlsx', Netherlands, SMR) in `estimate/tea.yaml`.
- Natural gas 11.397 EUR/GJ GCV and power 100.65 EUR/MWh (Eurostat NL bands I6 and IG, 2025,
  excluding VAT). Both are the bands of the existing site's total use, through which the unit
  buys its gas and power. The unit alone (about 2.1 GWh/a of power, about 0.3 PJ/a of gas)
  would fall in smaller, dearer bands. This is a premise of this design, ASSUMED; power is
  therefore ASSUMED, not QUOTED. Utilities are about 37 EUR/t, and the FUEL swing of 0.6 to 1.6
  covers the band difference. Fired heat 53.56 EUR/MWh absorbed (efficiency 0.85 LHV, ASSUMED;
  methane GCV from the NIST WebBook value 890.7 kJ/mol, Pittam and Pilcher 1972). Steam
  45.59 EUR/MWh (boiler 0.90 on GCV, ASSUMED, all levels alike). Cooling water 2.85 EUR/MWh
  (the calculation of ammonia-1's product:CW price, same 10 K rise).
- Fuel gas and biphenyl credited as fuel at the gas price per GJ LHV (ASSUMED, conservative).
  No open biphenyl price was found.
- CO2 of H-101 at 0.2376 t/MWh absorbed (IPCC 2006 default 56.1 t/TJ) and of the site boiler
  raising the steam at 0.2022 t/MWh of steam heat (0.90 on GCV), at 74 EUR/t (EUA 2025), with no
  free allocation (ASSUMED). The steam carries its CO2 as the make-up hydrogen does, so the
  carbon boundary is the same for all bought energy: 14.5 kt/a in total. The CO2 of the
  exported fuel gas and biphenyl is charged where they are burned, not here.
- Fixed cost: 25 operators at 80 kEUR, maintenance 3 % and insurance 1 % of fixed capital.
  Real discount rate 8 %, tax 25.8 %, 25 years, 8000 h/a (all as ammonia-1, ASSUMED).
Results (`cheme assess tea --write`, `estimate/tea.md`):
- LCOP 880.9 EUR/t against 673.6 EUR/t: not met. Cash cost 860.3 EUR/t, NPV -152 MEUR, no IRR.
  (Monte Carlo P10/P50/P90 LCOP 708/883/1088 EUR/t.)
- Cost of production per t benzene: feeds 969.5, utilities 37.2, CO2 10.8, co-product credits
  -184.3, fixed 27.1, capital and tax 20.6 EUR/t.
- The toluene price dominates (Spearman +0.93). With all else at 2025 values, the decision
  turns at toluene 501.1 EUR/t (-25 %), i.e. a benzene-toluene spread of at least about
  172 EUR/t at the 2025 benzene price. Because 1.18 t of toluene goes into each t of benzene,
  the break-even spread grows slowly with the price level. Capital never turns it within the
  tested range (class 5 high x 2: 909 EUR/t).
- The reported P(meets) of 5.3 % is not the decision result. The Monte Carlo samples the
  toluene price independently, while the threshold (the benzene price) stays fixed, so
  P(meets) is the chance that toluene falls while benzene does not. It is not a spread
  probability. Core v1.4.1 cannot correlate two price inputs, nor tie an `lcop` threshold to a
  price key (core#129).
- Spread evidence instead: scenarios prices-2019 to prices-2025 apply each year's Comext
  unit values from the same two flows (benzene exports, toluene imports). The NPV is computed
  against that year's benzene price; the LCOP column's 'meets' uses the fixed 2025 threshold
  and does not apply to other years.

  | year | benzene | toluene | spread | NPV, MEUR |
  |---|---|---|---|---|
  | 2019 | 624.8 | 615.1 | 9.7 | -140 |
  | 2020 | 522.3 | 418.5 | 103.8 | -36 |
  | 2021 | 897.7 | 549.0 | 348.7 | +121 (IRR 63 %) |
  | 2022 | 1028.6 | 942.5 | 86.1 | -142 |
  | 2023 | 865.0 | 897.6 | -32.6 | -221 |
  | 2024 | 978.7 | 818.5 | 160.2 | -65 |
  | 2025 | 673.6 | 668.1 | 5.5 | -152 |

  The proxy spread reached the break-even in one year of seven (2021). Its mean, about
  97 EUR/t, is well below it. The like-for-like 2025 flows give -128 MEUR (both imports) and
  -280 MEUR (both exports). Hydrogen, gas and power are held at 2025 values in every
  scenario.
What it means for the next stage: on the Comext trade-value proxy (not a traded spread), a
stand-alone thermal HDA unit buying toluene would have paid in one year of 2019 to 2025. This
conclusion is conditional on the proxy. Its economics are a benzene-toluene spread and a
hydrogen question (I-07), not a capital question. The engineering of the case study goes on as a design
exercise (issue #302). An investment case would need a contract spread or an integrated site
with cheap hydrogen and its own toluene. That is the owner's decision, not this file's.
Rejected: a scaled reference plant cost (no open, citable HDA plant cost was found); the
WBCSD-style co-product price split (the LCA keeps energy allocation, D-013).
Not covered: working capital, the product subcooling duty (I-12), storage and loading.
`cheme assess tea` reports two infos: the hydrogen price is of 2024, and P(meets) is below the
decision's confidence (read as above, not as the decision's probability).
EUA price: the 74 EUR/t 2025 average is cited from a secondary report of ESMA's figure,
cross-checked against Instrat's 73.43 EUR/t auction average, and labelled secondary and
ASSUMED. The ESMA report was not located with a page locator in this round.
Revised 2026-11-03 after the review of PR #320: steam CO2 added, power ASSUMED with the band
premise, NIST methane value corrected (890.7 kJ/mol; conversion 0.055516 to 0.055521), K-101
drive named in the allowance, spread scenarios added, P(meets) no longer quoted as the result.
LCOP 874.3 to 880.9 EUR/t.
Revised 2026-11-03 in S2 (D-020 to D-023): the TEA was rerun on the new feeds, reactor model,
product cooler and quench pump. LCOP 875.9 EUR/t, NPV -148.4 MEUR, fixed capital 17.87 MEUR
(ISBL 10.71 MEUR); the decision turns at toluene 504.2 EUR/t (-25 %). The values above are those
of S1.

### D-020 Feed specifications from published sources (2026-11-03, S2)
Decision: give both feeds a composition from a published source, with provenance `given`
(section S2 of `runs/plan.md`, item 1; supersedes the compositions of D-003):
- Fresh toluene S1: the commercial toluene data sheet of Bharat Petroleum Corporation Ltd
  (BPCL: TOLUENE, conforming to IS 537:2011, https://bharatpetroleum.in/images/files/Data-Sheet-Toluene.pdf,
  read 2026-11-03). Its table sets toluene at no less than 99.8 % by mass (row 1), benzene at
  no more than 500 mg/kg (row 8), non-aromatics at no more than 0.1 % by mass (row 7), C8+
  aromatics at no more than 1000 ppm (row 10) and water at no more than 500 ppm (row 13).
  Modelled: benzene at its limit, 0.05 % by mass, which is 0.000590 mol/mol. The other
  impurities (together at most 0.2 % by mass) are not components of the model. They are
  counted as toluene, ASSUMED. Their fate (C8 aromatics dealkylate too, non-aromatics
  hydrocrack to light ends, water goes to the separator) is not modelled.
- Make-up hydrogen S4: PSA purity, 99.9 mol% H2. Source: Matijasevic and Petric (2016),
  Integration of hydrogen systems in petroleum refinery, Chem. Biochem. Eng. Q. 30(3) 291-304,
  doi:10.15255/CABEQ.2015.2337. It was read in the authors' manuscript (hatz.hr copy, read
  2026-11-03). Table 1 (p. 3, after Patel et al. 2006) gives a PSA product purity of 99.9 %,
  and Fig. 3 (p. 8) shows a refinery PSA delivering 99.9 % v/v. The remaining 0.1 % is taken
  as methane, ASSUMED: the source does not name the PSA's impurity.
- Flows: S1 and S4 follow from the design capacity of `process/design-basis.yaml` (100 kt/a,
  12.5 t/h of benzene at 8000 h/a, D-002). `scripts/hda_balance.py` computes them with the loop
  specifications of D-007 and the reactor of D-021: S1 15432.33 kg/h (was 15518.29) and S4
  556.58 kg/h (was 815.73). They are given with that source, and the source text says so.
  The label `given` is no stronger than its premises. The capacity and the operating hours
  are ASSUMED (open input I-04, no owner figure, unlike ammonia-1's owner-approved capacity),
  and so are the loop specifications the script holds (D-007). Both source strings say so.
  This is a known limit of the `maturity-sourced-boundary` basis here: the requirement accepts
  a design-capacity derivation, and the derivation rests on assumed premises.
- Conditions (S1 300 kPa(a) and 303.15 K, S4 3700 kPa(a) and 313.15 K) stay ASSUMED battery
  limits. No published source gives the battery-limit conditions of a notional site.
Reason: `maturity-sourced-boundary` asks for sourced feed compositions and flows. A PSA grade
also matches the hydrogen price of D-019 (the European Hydrogen Observatory's SMR cost is for
SMR hydrogen, which modern plants purify by PSA), and the 5 % methane of D-003 had no source.
Rejected: ASTM D841 nitration-grade toluene (the standard is not openly readable); the 95/5
reformer gas of D-003 (no readable source found; the Politecnico di Milano course exercise of
D. Manca uses the same 5 % methane, but it is a teaching assumption, not a published
specification).
Effect: less methane enters with the make-up, so the purge needed to hold 40 mol% H2 falls from
0.1114 to 0.1017 of the separator gas. The purge falls from 3261 to 2967 kg/h, and the make-up
from 815.7 to 556.6 kg/h. The make-up as H2 is 552.2 kg/h, against 574.9 kg/h before.
I-01 and I-02 are answered for the composition; the supply conditions stay open.

### D-021 R-101 model basis: published per-pass conversion and biphenyl equilibrium (2026-11-03, S2)
Decision: model the adiabatic thermal reactor R-101 in two steps of the one vessel (`reactions.yaml`,
`flowsheet.yaml` R101 and R101B):
- R101 (conversion reactor): HDA at a toluene conversion per pass of 0.75, `provenance: given`.
  Source: US 3,291,849 A (C. C. King, J. F. Campagnolo, L. M. Lehman; Hydrocarbon Research,
  Inc., granted 1966-12-13), read in full text at https://patents.google.com/patent/US3291849.
  In the detailed description, the paragraph beginning "The reactor 44 is an internally
  insulated open chamber" describes a non-catalytic toluene reactor at about 600 psig with a
  residence time of 20 to 40 s. Its temperature stays at or below 1350 F at every point, and it
  is controlled so that about 75 % of the toluene in its total feed is converted. The patent's
  reactor temperatures run from 1100 to 1500 F (866 to 1089 K), its pressures from 500 to
  800 psig, and its hydrogen from at least 2 mol per mol of liquid aromatic feed.
  The 0.75 is adopted from the patent's reactor as the design value of R-101. R-101's volume
  and residence time are not designed to it. The configurations also differ: the patent's
  reactor holds its temperature profile with quench gas added at points along the reactor (a
  staged gas quench), while R-101 is a single adiabatic vessel without intermediate quench, at
  485 psig against the patent's about 600 psig. The evidence check of `cheme maturity`
  (`process/reaction-evidence.yaml` O1, revision below) leaves O1 out for that reason. It is
  not at R-101's pressure (4238 against 3450 kPa(a)), so the conversion counts as sourced
  only by its own source, as a transferred design value ("own source kept, not supported by
  the evidence").
- R101B (equilibrium reactor): the biphenyl reaction 2 BZ <=> BIPH + H2 at chemical
  equilibrium at the reactor outlet. The data are the ideal-gas formation data of
  `process/materials.yaml` (given, with their `chemicals` sources), so `cheme maturity` counts
  the basis as sourced. Its pressure drop is taken in R101.
- Reason for the equilibrium: a reversible biphenyl reaction is consistent with the background
  of US 3,607,960 A (Gulf Research & Development Co., 1971, read in full text at
  https://patents.google.com/patent/US3607960A/en). It says the benzene yield of thermal HDA
  "may be increased somewhat" by running it in the presence of diphenyl. The reversibility is
  this design's inference, not the patent's words. Starting from almost no biphenyl, the
  forward reaction can at most reach equilibrium, so the model gives the most biphenyl the
  benzene can form at the outlet. That bounds the biphenyl make only. It does not bound the
  selectivity loss: the same background says that the effluent of a primary thermal zone
  carries "polyphenyls (primarily diphenyl) and higher boiling polymers", and heavier
  polyaromatics and hydrocracking to light paraffins are excluded from the model only by the
  design basis's "ASSUMED no other side reactions". The modelled selectivity of 0.9734 is
  therefore an optimistic value, and so is the toluene consumption that drives the TEA (see the
  revision below). The recalled Douglas correlation of D-005 gave 0.9694, and D-005 had
  already found its biphenyl slightly beyond equilibrium (ln(Q/K) = +0.14).
- Results (DWSIM): HDA extent 166.83 kmol/h, BIPH extent 2.215 kmol/h. The benzene
  selectivity is therefore 1 - 2 x 2.215 / 166.83 = 0.9734 (the script gives 0.9731,
  ln(Q/K) = 2e-13). The reactor outlet is 938.2 K. Biphenyl make: 2.215 kmol/h (341.6 kg/h),
  against 2.570 kmol/h with D-005.
- Operating window, checked against readable sources instead of the recalled Douglas values:
  inlet 895 K (1151 F) and outlet 938 K (1229 F) lie inside US 3,291,849's 1100 to 1500 F and
  under its 1350 F maximum. The pressure, 3450 kPa(a) (485 psig), lies inside US 3,607,960's
  preferred 400 to 600 psig of its primary thermal zone (claim 4), but slightly below
  US 3,291,849's 500 to 800 psig. H2/aromatics 5 lies inside US 3,607,960's preferred 3 to 10
  and above US 3,291,849's minimum of 2. The 5 itself stays the design choice of D-007,
  ASSUMED. Speight's 500 to 600 C (from the library skill; the book was not read here) lies
  below both patents' thermal ranges. It is probably a catalytic range, but that is not
  verified, so the conflict is recorded, not resolved by Speight.
Rejected: kinetics. The open thermal HDA rate laws found (e.g. Hutabarat et al. 2026,
J. Chem. Eng. Res. Prog. 3(1) 88-93, doi:10.9767/jcerp.20563, eqs. 4 and 6, CC BY-SA) give
pre-exponential factors without units or a validity range and cite a secondary source. Core's
kinetic reactor (`reactor: pfr`) is a fixed catalyst bed and has no empty-vessel homogeneous
model. The one sourced value is the conversion, given with its source on the reaction itself.
Neither patent read in full reports a benzene selectivity at R-101's conditions: US 3,291,849
gives none, and US 3,607,960 gives one at a higher conversion (revision below). US 3,340,318
and US 3,390,200 were seen only as search snippets, at 89 to 94 % conversion, and give no
numbers here.
Simulation note: DWSIM 9.0.5's equilibrium reactor in adiabatic mode stops with "TP Flash: One
or more flash specification values are invalid", both from the old tear values and from the
converged ones. R101B is therefore isothermal at the R101 outlet. Its 17.4 kW (endothermic
BIPH plus DWSIM's own formation data) has no energy stream. Adiabatic, it would cool the
47.1 t/h of gas by about 0.4 K. `cheme assess lca` warns (`boundary-utility-unassigned`,
R101B), and the warning stays visible. DWSIM takes K from its own (ChemSep) formation data:
benzene differs by +300 kJ/kmol and biphenyl by -688 kJ/kmol. The reaction heat therefore
differs by 0.79 kW from materials.yaml (`predictive.formation-data` fails, against a 0.1 kW
tolerance). That is a predictive-level requirement and not a balanced one. The adiabatic
failure is a simulator limit, tracked as core#58 (opened from ammonia-1 on a shift bed). It
reproduces here when `R101B: mode: adiabatic` is set in `process/simulation.yaml` and
`cheme process simulate --check` is run (core v1.4.1, 2026-11-03). The run does not converge,
with "R101B: TP Flash: One or more flash specification values are invalid. ..." and
"R101B: 3600 kg/h of liquid formed in the reactor, which has one outlet" for an all-vapour feed
at 938 K. The hda-1 reproduction is to be added to core#58 (posting it was not authorised in
this run). The DWSIM limit stays an open item.
Superseded: the selectivity of D-005 and the lumped HDABP reaction of D-014. Review finding
2026-10-27-pfd-lci-review#4 and I-06 are answered here: no model value rests on Douglas (1988)
any more. What remains unsourced: the Douglas book itself was never read, and Speight's range
is unverified.
Maturity: `balanced` reached (R101 conversion specified and sourced, R101B equilibrium
predictive and sourced). Predictive stays out of reach for three reasons:
`predictive.model-basis` (R101 is a specified conversion; no readable thermal HDA kinetics with
units and range, and no homogeneous kinetic reactor in core), `predictive.property-regime`
(core#315: Peng-Robinson is not benchmarked for aromatics with H2/CH4) and
`predictive.formation-data` (DWSIM's formation data in R101B).
Revised 2026-11-03 in round 1 of the review of PR #326:
- Evidence recorded in `process/reaction-evidence.yaml` (skill `reaction-evidence-search`):
  O1, US 3,291,849 reactor 44 (75 % per pass, about 600 psig, 20 to 40 s, 922 to 1005 K); and
  O2, US 3,607,960 Example 1. Example 1's primary reactors (two in series, feed about 1215 F,
  outlet about 1340 F, about 460 psig, about 56 s, H2/aromatics 4.0) convert 85.0 % of the
  toluene per pass (derived: 501.6 to 75.2 mol/h). The patent states a "net selectivity 94.5
  percent for this primary reactor system" (benzene 36.9 to 439.8 mol/h; 9.4 mol/h of polymer
  in the effluent). The auxiliary reactor of that patent, which raises it to about 98.3 %, has
  no counterpart in R-101. The model basis is written there (route THDA, reactions HDA and BIPH,
  evidence O1, the assumptions above, decision D-021).
- O2 is at a higher conversion (85 against 75 %) and a lower pressure than R-101, where the
  selectivity is expected to be lower, so it is not R-101's value either. No source read in
  full gives R-101's selectivity. The model keeps 0.9734, now stated as optimistic (an upper
  bound on the benzene made, not a conservative value).
- TEA sensitivity (`estimate/tea.yaml`, scenarios `selectivity-0945` and
  `selectivity-0945-credited`, own scale factors on the DWSIM extents: toluene x 1.030, make-up
  hydrogen x 1.018). LCOP 902.9 EUR/t and NPV -168.1 MEUR with the lost aromatics not credited.
  LCOP 884.7 EUR/t and NPV -154.8 MEUR with them credited as heavy-ends fuel and methane.
  Baseline: 875.9 EUR/t and -148.4 MEUR. The decision of D-019 does not change; the gap to the
  benzene price grows by up to 27 EUR/t.

### D-022 Simulation close-out: product cooler, quench pump, stabiliser and column specs (2026-11-03, S2)
Decision, against each D-014 deviation (I-12, the review findings and the S2 plan row):
- Product cooler (I-12): a new step E207 (Cooling) and equipment item E-207 cool the C-202
  distillate S26 from 366.2 K to 313.15 K (S21). Duty 314.5 kW to cooling water, Q11. The area
  is 19.8 m2 at U 500 W/(m2 K), ASSUMED (`scripts/concept_sizing.py`). It is placed in the
  condenser row (layout/equipment-placement.yaml, x 140 m) and priced in the class 5 estimate.
  Its pressure drop is 0, ASSUMED, because the implicit distillate pump (D-010) makes it up.
  The D-014 deviation on S21 (366 K against 313 K) is gone, and so is the subcooling item in
  the uncovered allowance.
- Quench pump (review #6, D-010): a new Pumping step P102 (linked to the existing P-102)
  takes the quench liquid from 3250 to 3450 kPa(a), at 0.52 kW. The deviations on S9, S10, S11
  and S17 are gone.
- Implicit distillate pump of C-203 (S23 and S2 at 30 kPa(a) instead of 150): kept. There is
  no item for it in the equipment list. The reflux and distillate pumps of the three columns are
  drawn and listed with the P&IDs (S3) and sized in S7 (I-08). M100 shows an energy imbalance of
  1.26 kW (`sim-energy-unbalanced`, tolerance 0.31 kW), the mixer at 30 kPa(a) mixing the two
  liquids. The warning stays visible.
- Stabiliser C-201 (I-12): kept as the DWSIM shortcut, with the script's duties Q5 1423.2 kW and
  Q6 155.2 kW. The partial condenser again puts the off-gas at 191 to 205 K in DWSIM (the
  repeated runs of this section; the dew point is about 313 K), with condenser 22.8 to 25.7 kW
  and reboiler 1273 to 1277 kW. The rigorous alternative does not fit the design: core's
  rigorous column with `condenser: partial` always draws a liquid distillate beside the vapour
  (`vapor_flow`), and the stabiliser's distillate is all reflux. A reboiled stripper
  (`condenser: none`) would remove E-201 and change D-008. That is a design change for the
  basic-engineering stage, not made here.
- C-202 rigorous trial: 40 stages, feed on stage 20, R 2.18 and a bottoms flow of 5252.7 kg/h.
  It over-purified the distillate (13 ppm toluene) and stopped on DWSIM's mass-balance
  tolerance for the hydrogen traces (relative error 0.0029, against 0.001). The shortcut stays.
- C-203 bottoms: D-008's 2 mol% toluene would need about 345 kg/h at the simulated biphenyl
  make. DWSIM's rigorous column does not converge below about 350 kg/h here. The trials were
  341.9 and 345.4 kg/h with 10 and 14 stages, 346 kg/h at R 0.5 and 1.0, 349 kg/h, and a
  reboiler temperature of 473.4 K. The lowest flow that converges, 352 kg/h, is used. The
  biphenyl then carries 4.91 mol% toluene (about 6 kg/h more toluene than the 2 mol% target)
  at 456.5 K. This is a deviation from D-008, kept visible and not tuned away.
- Composition sums (closure finding 2026-11-03-concept-closeout#17): S19, S20, S22 and now S26
  miss 1 by up to 1.7e-4 (`pydexpi_composition_fractions`). All four streams leave the DWSIM
  shortcut columns C-201 and C-202, and the fractions are written by `simulate --fill` as
  calculated values. Normalising them by hand would put values in the file that no
  calculation produced. The fix is a rigorous model of C-201 and C-202, which the two bullets
  above could not give. The warnings stay. The cause is a core v1.4.1 / DWSIM limit, reported
  as core#130. The run record already holds the unclosed fractions, so they come from DWSIM's
  shortcut column. The key component holds its spec exactly (S26 TOL 0.001, S20 CH4 1e-5)
  and the remainder is not re-closed. `simulate --fill` writes them without a closure check
  or finding.
- Benzene purity (D-002 target 99.9 mol%): the simulated distillate S26 holds BZ 0.998925,
  TOL 0.001 (the heavy-key spec) and CH4/H2 traces 1.38e-5, which sum to 0.999939.
  Normalised, the benzene is 99.899 mol%, so the target is missed narrowly. The cause is the
  heavy-key spec of 0.001, which leaves no room for the light ends the shortcut C-202 carries
  into the distillate, together with the unclosed sum above. S21 keeps the design target as an
  assumed value, and its source now names this deviation. Not normalised by hand. A margin on
  `heavy_key_in_distillate` (e.g. 0.0009) is the fix for the next rerun of C-202.
Run (core v1.4.1, DWSIM 9.0.5, Peng-Robinson, `process/simulation-run.json`): converged in 3
iterations of the recycles (tears S9, S15, S23). The energy audit closes, as
`cheme process simulate --check` prints it: plant residual 0.833 kW against 22.24 kW, R101
-0.0009 kW against 3.04 kW, R101B 0 kW. The plant closure counts R101B's isothermal 17.4 kW as
a heat input. That duty has no energy stream (`hot_utility` with terminal null in the run
record), and the drawn R-101 is adiabatic. It is a model artefact of the isothermal workaround
(D-021, core#58), not heat the plant receives. The `boundary-utility-unassigned` warning stays.
The run's raw utility totals are hot 8320.3 kW, cold 10229.3 kW and power 268.0 kW, with
24.28 MW recovered between process streams. The TEA and the LCA use other totals: hot
8449.6 kW and cold 10360.4 kW, with the same power. Two differences explain it. C-201's duties
come from the script (Q5 1423.2 kW reboiler, Q6 155.2 kW condenser) instead of DWSIM's shortcut
values (1276.6 and 24.1 kW). R101B's 17.4 kW is in no utility. So the economics' hot utility is
8320.3 - 17.4 - 1276.6 + 1423.2 = 8449.6 kW, and their cold utility is
10229.3 - 24.1 + 155.2 = 10360.4 kW.
The E-101 least approach is 53.8 K. The remaining `sim-deviation` warnings are S2 and S23
(implicit pump), S19 temperature and Q5/Q6 (stabiliser), each kept above.
Simulation compared with the script (`scripts/hda_balance.py` on the same basis; its Python is
the core 1.2.1 environment with thermo 0.6.1, which reproduces the S1 values of main exactly):

| quantity | script | DWSIM | deviation |
|---|---|---|---|
| R-101 outlet T (S8) | 936.79 K | 938.21 K | +1.4 K |
| benzene selectivity | 0.9731 | 0.9734 | +0.03 % |
| biphenyl extent | 2.2415 kmol/h | 2.215 kmol/h | -1.2 % |
| H-101 duty (Q3) | 2944.2 kW | 2901.8 kW | -1.4 % |
| E-101 duty | 24345 kW | 24275 kW | -0.3 % |
| E-102 duty (Q4) | 4908.2 kW | 4903.6 kW | -0.1 % |
| K-101 power (Q2) | 231.2 kW | 231.0 kW | -0.1 % |
| purge S13 | 2967.1 kg/h, 40.00 mol% H2 | 2967.0 kg/h, 40.02 mol% H2 | 0.0 % |
| benzene distillate | 12500 kg/h (spec) | 12497.5 kg/h | -0.02 % |
| toluene recycle S23 | 4908.3 kg/h | 4900.0 kg/h | -0.2 % |
| C-202 reboiler (Q7) | 2299.3 kW (q = 1 feed) | 3484.2 kW | +52 % (as D-014) |
| C-203 reboiler (Q9) | 644.6 kW (2 mol%) | 640.4 kW (4.9 mol%) | -0.7 % |

Effects carried: stream table and PFD/BFD rebuilt (`cheme process build`: 18 steps, 39 streams).
Equipment list: E-207 added, notes of R-101, P-102, E-203 and E-206 updated. Cost basis sizes
from the new run (`scripts/concept_sizing.py`); E-101 is repriced at 2 x 646.2 m2
(1.627 MUSD). Estimate and TEA rerun (D-019 revision line). LCA inventory rewritten: LHVs of
the fuel gas 54.23 MJ/kg and biphenyl 39.68 MJ/kg, recomputed from the simulated streams.
The shared LCI proxy `hydrogen-methane-makeup` (lci/mappings.yaml, used by hda-1 only) now
splits a 99.9/0.1 mol% gas. Layout model rebuilt.

### D-023 Purge hydrogen recovery: passes the incremental test, not yet in the flowsheet (I-07) (2026-11-03, S2; revised in the review of PR #326)
Superseded by D-024 (2026-11-04): the PSA is in the flowsheet, with a sourced recovery, pressures and package cost; its routing and its economics below are replaced there (incremental NPV +0.27 MEUR, not +2.9 to +9.7 MEUR). Kept as the record of the S2 screening.
Decision: a PSA on the purge passes the incremental test on screening numbers. It is
recommended as a design change, but it is not in this flowsheet. The purge still goes to the
fuel gas header (D-007, D-009). I-07 stays open: the PSA step, its tail-gas compressor and a
rerun are to be added before the P&IDs (S3) or, if the owner decides otherwise, the reason is
to be recorded. The first version of this decision compared the PSA's gross benefit with the
whole plant's LCOP gap (202 EUR/t). That was the wrong test: an add-on unit is judged on
whether its own benefit pays for its own cost, which the revision below does.
Number (`scripts/purge_h2_recovery.py`, TEA premises of D-019 and the S2 run):
- Recovered hydrogen: the purge S13 carries 107.37 kmol/h of H2 (216.4 kg/h; 2967.0 kg/h at
  40.02 mol%). A PSA recovers 75 to 92 % of the hydrogen in its feed (Matijasevic and Petric
  2016, Table 1). At 85 %, ASSUMED as the middle of that range, it returns 184.0 kg/h, or
  1472 t/a.
- Value: each recovered kg saves the make-up price, 2.781 EUR/kg (EHO SMR 2024). It loses its
  fuel credit, 11.397 EUR/GJ x 0.11996 GJ/kg = 1.367 EUR/kg. The LHV of hydrogen is an own
  calculation: the formation enthalpy of H2O(g), -241.826 kJ/mol (Cox, Wagman, Medvedev 1989,
  CODATA Key Values), over the molar mass of H2, 2.01588 g/mol. That is the same basis as the
  LHVs of D-013. Net 1.414 EUR/kg, about 2.081 MEUR/a gross (20.8 EUR/t of benzene).
- Power: a PSA delivers its product near its feed pressure, so the product is not
  recompressed. It needs a boost from about 3150 kPa(a) (100 kPa below the feed, ASSUMED) into
  the K-101 suction at 3250 kPa(a), 2.8 kW, plus K-101's extra throughput, 8.9 kW. The
  tail gas (177.0 kmol/h, about 2.8 t/h, mostly methane) leaves at about 130 kPa(a)
  (ASSUMED). It must be compressed into the site fuel gas header, taken at 450 kPa(a)
  (ASSUMED, no site data, I-05): 245.4 kW (ideal gas, k 1.3, efficiency 0.75 of D-010). In
  total 257.1 kW, 0.207 MEUR/a at 100.65 EUR/MWh. Net before capital-related cost:
  1.874 MEUR/a.
- Capital, class 5. Tail-gas compressor: the package compressor correlation (Turton et al.,
  CAPCOST) at its 450 kW minimum, 814 126 USD 2023 bare module, the same as K-101's row in
  `estimate/equipment-cost.csv` (an upper estimate for 245 kW). With the D-019 exchange rate,
  escalation and capital factors (allowance 1.15, OSBL 1.30, owner's cost 1.07, contingency
  1.20) it comes to 1.52 MEUR of fixed capital. PSA package (adsorbers, adsorbent, valve
  skid, controls): no openly readable PSA cost correlation was reached in this round. The CC BY
  papers of Abdoos et al. 2025 (Chem. Eng. J. 526, 170994) and the MDPI Energies 18(10) 2440
  refused access (HTTP 403). Mivechian and Pakizeh 2013 (Korean J. Chem. Eng. 30(4) 937-948)
  could not be reached. Kreutz et al. are at a coal-to-hydrogen scale with no usable
  correlation. The PSA's fixed capital is therefore ASSUMED at 2 to 8 MEUR, a deliberately
  wide band (a factor of 4, the width of a class 5 range). It is not a published value. Together:
  3.5 to 9.5 MEUR.
- Incremental NPV at the D-019 discount rate of 8 % (construction 40/60, 25 years,
  straight-line depreciation, tax 25.8 %, maintenance and insurance 4 % of fixed capital a
  year, as in `cheme assess tea`): +9.7 MEUR at 3.5 MEUR and +2.9 MEUR at 9.5 MEUR. The
  break-even fixed capital is 12.0 MEUR (two thirds of the whole plant's 17.9 MEUR). Simple
  payback: 2.0 to 6.4 years. Pre-tax and annualised (capital recovery factor 0.0937), it takes
  about 6 to 14 EUR/t off the LCOP. It does not close the 202 EUR/t gap, so the decision of
  D-019 does not change. The PSA pays for itself at any capital inside the band.
Reason: the PSA pays on its own test unless its fixed capital exceeds about 12 MEUR. That
conclusion rests on the ASSUMED header pressure and the ASSUMED PSA cost band, so it needs a
vendor budget price, or a readable correlation, when the PSA is added. Adding it changes the
flowsheet (a new step, a tail-gas compressor, the fuel gas LHV and the LCI), which is more than
a review fix, so it is carried as I-07. A vent absorber that keeps benzene out of the fuel
header (about 237 kg/h of aromatics in S13 and S19) is also not included. It is a
basic-engineering option if the site asks for it.
Rejected: membrane recovery (85 to 95 % recovery at 90 to 98 % purity, same source). Its
permeate leaves at low pressure, so unlike a PSA it needs the product recompressed into the
loop, and its purity is lower. It was not costed.

### D-024 Purge hydrogen recovery: PSA PK-101 and tail-gas compressor K-102 in the flowsheet; I-07 closed (2026-11-04, S3a)
Decision: the purge goes to a hydrogen PSA, package PK-101. Its hydrogen returns to the
K-101 suction. Its tail gas is compressed by K-102 into the site fuel gas header and
cooled in E-103. The PSA is kept in the design, although with the numbers below it only
breaks even. If the vendor's budget price for the package is above the break-even price
(below), the PSA is to be dropped again. This decision closes I-07 and supersedes the routing
and the economics of D-023.

Flowsheet (`process/flowsheet.yaml`, new block HRU):
- The purge take-off SPL1 moves from the K-101 suction to the K-101 discharge (3600 kPa(a)).
  The PSA then works at the loop's highest pressure. Its product, after the adsorbers'
  pressure loss, is still above the suction pressure, so it reaches the suction through a
  pressure control valve (PV101) and no booster is needed. D-023 had assumed a booster from
  3150 to 3250 kPa(a): a machine for 2.8 kW, rejected. The mixer M102 joins the PSA hydrogen
  to the separator gas ahead of K-101. The price of this routing: K-101 now also compresses
  the purge itself (see the K-101 split under Results).
- The loop specifications of D-007 are kept: H2/aromatics 5 at the reactor inlet and 40 mol%
  H2 in the purge, now the purge at the K-101 discharge. `scripts/hda_balance.py` holds the PSA
  as a specified split and solves the loop again. The purge fraction becomes 0.0937615 of the
  K-101 discharge (it was 0.1017477 of the separator gas). The make-up S4 becomes 392.63 kg/h
  (from 556.58, -29.5 %) and the fresh toluene 15427.21 kg/h (from 15432.33). Q5/Q6 become
  1424.87/157.80 kW.
- Representation in DWSIM (core supports adsorbers only as a component separator, skill
  process-simulation). PK-101 is three steps. X100 is a valve for the adsorbers' 60 kPa loss.
  X101 is the component separator. X102 is a valve that lets the tail gas down to the
  desorption pressure. X100 and X102 are model steps inside the package, like R101B in R-101,
  and have no line of their own. X101's recoveries are specified, not predicted
  (`basis: specified`, `basis_source` and `operating_basis` in `process/simulation.yaml`):
  - H2 0.75. Matijasevic and Petric (2016), Table 1 (p. 3 of the authors' manuscript, after
    Patel et al. 2006), gives a PSA hydrogen recovery of 75-92 % for a feed above 40 vol% H2,
    with a product purity of 99.9 %. The purge has 40.0 mol% H2, right at that feed limit, so
    the low end of the range is taken. This is ASSUMED within the published range. For
    comparison, NETL (2022), Section 3.3.5.1 (p. 54), designs its reformer PSAs for 85 % on a
    feed of about 75 mol% H2.
  - CH4 0.000508672. This is the fraction that gives the 99.9 mol% product at the design feed
    (the source gives the purity, not the impurity). The 0.1 % remainder is ASSUMED to be
    methane.
  - Toluene, benzene and biphenyl 0. They are taken as fully adsorbed and leave with the tail
    gas (ASSUMED, no vendor data).
- Pressures from a published PSA:
  - Product: 60 kPa below the feed. NETL (2022), Exhibit 3-4, Case 1, has the PSA feed
    (stream 10) at 2.45 MPa and the product (stream 11) at 2.39 MPa.
  - Tail gas: 140 kPa(a), as stream 13 of the same exhibit (0.14 MPa).
  These values come from a reformer PSA and are ASSUMED to hold here.
- Fuel gas header: 450 kPa(a), still ASSUMED (D-023, I-05). K-102 discharges at 470 kPa(a), and
  its aftercooler E-103 (20 kPa drop, outlet 313.15 K) is modelled in the same compressor step.
  The tail gas does not condense: at 450 kPa(a) the benzene partial pressure is about 6 kPa,
  against a vapour pressure of about 24 kPa at 313 K. Own calculation: the partial pressure
  is 0.01238 x 450 = 5.6 kPa (S34 benzene mole fraction, `process/simulation-run.json`); the
  vapour pressure is that of `thermo` 0.6.1 (the property package of `scripts/hda_balance.py`,
  source register), `VaporPressure` of benzene at 313.15 K, its default method HEOS_FIT:
  24.39 kPa (its other correlations, Antoine, Wagner, DIPPR and VDI, give 24.30 to 25.00 kPa).

Simulation (`cheme process simulate --fill`, DWSIM 9.0.5, Peng-Robinson; then
`cheme process propagate --fill` and `simulate --fill` repeated until no stale value was
left):
- Convergence: converged in 13 iterations with four tears (S9, S28, S31, S23). The first
  guesses for the two new tears are in `simulation.yaml` (`guesses:`); they are not stream
  values.
- Energy audit: plant closure ok, residual +0.88 kW (tolerance 28.0 kW). This includes X101's
  -4.39 kW, which core reports as stated by the specified split (`sim-energy-stated`): the
  enthalpy out minus in of a split that conserves no energy. It is not a utility and not the
  real PSA's duty, which is nearly zero apart from the valve skid. R101B's unterminated
  17.4 kW is unchanged (D-022).
- Deviations: the same ones as in S2, no new deviation (implicit pumps S2/S23, C-201 shortcut
  off-gas temperature, Q5/Q6 from the script, M100's 1.26 kW).
- Balance script: energy closure 8673.5 kW in against 8649.9 kW out (0.27 %; 19.8 kW before,
  the pump temperature rise neglected, D-010).
- Results (S2 values in brackets):
  - PSA: feed S13 2956.2 kg/h (267.67 kmol/h, 40.03 mol% H2, 324 K). Hydrogen S30 163.3 kg/h
    at 99.9 mol%, which is 162.0 kg/h or 1296 t/a of H2.
  - Tail gas S34: 2792.9 kg/h (187.2 kmol/h; 14.3 mol% H2, 84.3 % CH4, 1.4 % aromatics),
    311.3 K after the let-down.
  - K-102: 249.0 kW. E-103: 247.8 kW.
  - The recycle gas to the reactor (S28) is 2587 kmol/h, against 2353 kmol/h before. The
    reactor inlet holds H2/aromatics 5, so the hydrogen that used to come as make-up now comes
    through the recycle, diluted with methane to 40 mol%. The reactor feed therefore carries
    more methane: 50.9 mol% (48.8), and the outlet is 936.2 K (938.2).
  - Effects of that dilution: K-101 278.8 kW (231.0), H-101 3042.2 kW (2901.8), E-101 25285 kW
    (24275), E-102 5072 kW (4904). Plant power 564.8 kW (268.0).
  - K-101 split (own calculation, review of PR #327): the +47.8 kW on K-101 is not all
    dilution. With SPL1 at the discharge, K-101 also compresses the purge itself, 267.7 kmol/h
    from 3250 to 3600 kPa(a). At the machine's mean 0.0977 kW per kmol/h (278.8 kW over
    S28 + S13, about 2855 kmol/h) that is about 26.1 kW; the dilution of the loop is the other
    about 21.7 kW. Against the rejected D-023 booster (2.8 kW) the chosen routing costs about
    23 kW more power, about 0.02 MEUR/a at the TEA's 100.65 EUR/MWh and 8000 h/a. It saves a
    second hydrogen machine (its capital, spare, seals and one more leak source in hydrogen
    service), which is judged worth more; the trade-off stays open with the make-up-line
    option below.
  - Returning the hydrogen into the make-up line M101 instead would avoid the dilution (worth
    about 0.1 MEUR/a). It needs the product above 3600 kPa(a), so a higher K-101 discharge
    pressure or a booster. This is left as an option for basic engineering.

Fuel gas and H-101: the exported fuel gas (S34 + S19) is 2968.1 kg/h at an LHV of 50.66 MJ/kg.
That is 41.8 MW LHV, against 3137.6 kg/h at 54.23 MJ/kg (47.3 MW) before. The LHV is an own
calculation from the formation enthalpies of `materials.yaml`, on the D-013 basis.
H-101 absorbs 3042 kW. At the fired efficiency of D-019 (0.85 on LHV) it needs 3.58 MW LHV,
which is 254 kg/h or 8.6 % of the fuel gas. If H-101 were fired from the header, 38.2 MW would
still be exported. The TEA keeps the accounting of D-009/D-019: H-101 on purchased natural
gas, the whole fuel gas credited.

Sizes, lists and layout:
- `scripts/concept_sizing.py`: E-103 47.1 m2 (U 100 W/(m2 K) ASSUMED; the K-102 discharge,
  about 436 K, follows from the simulated aftercooler duty at the mean cp of the balance
  script's Peng-Robinson run, 38.9 kJ/(kmol K); 439 K at an assumed 38 before the review of
  PR #327). E-101 is
  now 1351.9 m2 (2 x 676 m2) and E-102 312.1 m2.
- Equipment list: PK-101 (42 barg, the loop's design pressure, D-012; 80 degC), K-102 and
  E-103 (6 barg / 190 degC). All ASSUMED by the D-012 rule. PK-101's plot of 10 x 6 m (9 m
  high) is ASSUMED, as no vendor data were available.
- Lines: HG-113 (purge to the PSA, DN80), HG-125 (PSA hydrogen, DN40), FG-126 (tail gas,
  DN250), FG-127 (K-102 to E-103, DN200) and FG-128 (fuel gas to B/L, DN150), each with
  ASSUMED design conditions in its notes. HG-114 is gone, because the junction is now in
  HG-112. PG-108/109 go to DN450 for the larger loop flow (405 mm).
- Plot plan:
  - Placement: PK-101 (86, 85), K-102 (86, 74) and E-103 (86, 68), at the east edge of A-100
    between V-101 and road R-5. A first placement in A-200 left HG-113 and HG-125 out of the
    rack's 30 m reach (`layout-line-route`) and was moved, not accepted. The E-103 bundle
    pull is kept clear of K-102.
  - New separations (ASSUMED, as D-018): H-101 to PK-101 and to K-102 30 m; A-900 to PK-101
    45 m; PK-101 toppling to PR-1.
  - Measured (first placement): PK-101 is 47.0 m from A-900, 28.0 m from PR-1, 1.0 m from R-5
    and 2.9 m from V-101 (`cheme show`); see the correction below for the turned package. H-101 to PK-101 is 39.1 m and to K-102 44.0 m (footprints from the
    placement).
  - `cheme layout build`: 22 items, no clash, no blocked envelope. No separation or route
    finding.
  - Viewed 2026-11-04: `cheme layout render --plan` (build/layout-plan.svg) in a browser.
    Correction in the review of PR #327: that first placement (PK-101 unrotated, x 81-91)
    stuck 1 m out of A-100 (east edge x = 90) and stood 1.0 m from the edge of R-5, which the
    earlier sentence here missed. PK-101 is now turned by 90 degrees (long side north-south,
    footprint x 83-89, y 80-90): inside A-100 and 3.0 m from the edge of R-5 (x = 92). Road
    clearances of 3 m from R-5 for PK-101, K-102 and E-103 are now declared in
    `layout/site-plan.yaml` (ASSUMED as D-018: room for vehicle impact protection and
    maintenance access), so `layout-plot-plan` checks them.

Capital (`estimate/cost-basis.yaml`, class 5):
- PK-101: 4.06 MUSD 2023, priced as the package's bare module cost. The basis is NETL (2022),
  DOE/NETL-2022/3241, Exhibit 3-13 (Case 1 total plant cost details), account 7.1 Pressure
  Swing Adsorber: bare erected cost 17 434 kUSD plus engineering, CM, home office and fee
  3 487 kUSD (Dec 2018). NETL's contingencies are left out, as this estimate adds its own.
  - Scaling: on the adsorbed (non-hydrogen) flow, 160.5 against 3940 kmol/h (Exhibit 3-4,
    stream 10), with exponent 0.6 (ASSUMED, the six-tenths rule; the NETL scaling guideline,
    QGESS Rev. 4 of 2019, lists no adsorber).
  - Escalation: CEPCI 797.9/603.1 (2023/2018 annual, Chemical Engineering, Sept. 2024, p. 45).
    The 2018 annual average stands in for NETL's Dec 2018 cost base (ASSUMED: no monthly
    index was available; small at class 5).
  - This is an extrapolation by a factor of about 25 below the reference plant.
  - Range: 2.41 MUSD when scaled on the total feed flow, 5.59 MUSD with exponent 0.5.
  - This replaces D-023's unsourced 2 to 8 MEUR band. No vendor quotation was available.
- K-102: the CAPCOST compressor correlation at its 450 kW minimum, 814 126 USD (an upper
  estimate for 249 kW). E-103: 124 684 USD. Their motors are in the allowance.
- The 15 % allowance of the estimate also applies to PK-101, which overstates it slightly.

TEA (`cheme assess tea --write`), against the S2 run of PR #326:
- Plant: fixed capital 27.36 MEUR (17.87 MEUR before). LCOP 875.5 EUR/t (875.9). NPV
  -148.09 MEUR (-148.36).
- Incremental NPV at 8 %: +0.27 MEUR.
- Incremental cash flow, MEUR/a: hydrogen bought +3.626; fuel gas credit -1.805; power
  -0.239; H-101 fuel -0.060; toluene +0.027; cooling water -0.010; maintenance and insurance
  -0.379; CO2 -0.020 (+268 t/a). Net about +1.14 MEUR/a, for +9.48 MEUR of fixed capital.
  That capital includes the larger E-101 and H-101, and all the estimate's factors.
- Scenarios for the package price: psa-capex-low -144.57 MEUR (incremental +3.80) and
  psa-capex-high -151.37 MEUR (incremental -3.01).
- Break-even package price: about 4.18 MUSD 2023 bare module, about 7.8 MEUR of fixed capital
  with this estimate's factors.
- Scenarios for the PSA's hydrogen recovery (review of PR #327; the purge is at the source's
  40 % feed limit, so a vendor may offer less than 0.75): psa-recovery-070 -148.99 MEUR and
  psa-recovery-065 -149.89 MEUR, about -0.895 MEUR of NPV per 0.05 of recovery (screening
  scale factors on make-up hydrogen and fuel gas, `estimate/tea.yaml`; the loop is not solved
  again). Break-even recovery: 0.75 - 0.05 x 0.268 / 0.895 = about 0.735 (own calculation on
  the incremental NPV of +0.268 MEUR: baseline -148.095 against the S2 -148.363 MEUR).
- Why this is below D-023's +2.9 to +9.7 MEUR: a lower recovery (0.75 instead of 0.85), the
  loop dilution above (+140 kW fired; +48 kW on K-101, of which about 26 kW recompress the
  purge and about 22 kW are dilution, where D-023 assumed 8.9 kW), and the full capital
  factors on a sourced package price.
- The PSA does not change the D-019 decision: LCOP is still about 202 EUR/t above the benzene
  price.

LCI (`cheme assess lca --write`):
- Make-up hydrogen: 0.031410 kg per kg benzene (0.044526 before).
- Power: 0.045187 kWh/kg, which now includes K-102 (Q13). The aftercooler (Q14) is in
  product:CW.
- Fuel gas: 0.237446 kg/kg at 50.66 MJ/kg.
- Energy allocation: benzene 75.5 %, biphenyl 2.1 %, fuel gas 22.4 % (73.4/2.0/24.6 before).
- Balance: mass 15819.8 kg/h in, 15820.1 kg/h out, closed.

Reason: the PSA was the open design change of D-023. The task of this section was to add it
and carry its effects. With sourced recovery, pressures and cost, it pays for itself at the
central estimate, but only just. It is kept for three reasons:
- it is not negative at the central estimate;
- it cuts purchased hydrogen by 29.5 % (1296 t/a), which lowers the exposure to the
  hydrogen supply (I-02);
- grey hydrogen carries 9-12 t CO2 per t of hydrogen produced (Matijasevic and Petric 2016,
  p. 4), so its upstream emissions fall by about 12 to 16 kt CO2/a. Against that, the site
  burns about 155 TJ/a more natural gas for the hydrogen taken out of the fuel gas: about
  8.7 kt CO2/a at 56.1 t/TJ (D-019). This is a screening estimate, not an LCA result, as the
  backgrounds are open (I-11).

To reverse: either of two criteria makes the incremental NPV negative: a vendor budget price
for PK-101 above about 4.2 MUSD 2023 (bare-module equivalent), or a vendor hydrogen recovery
below about 0.73 at this purge (a 40 mol% H2 feed) with the price at 4.06 MUSD. Then the purge goes back to the fuel gas header
(D-007, D-009), unless the owner values the hydrogen and CO2 effects. A price within the range
does not change the decision of D-019.

Rejected:
- The D-023 routing (purge at the suction, booster on the product): a machine for 2.8 kW.
- Membranes: low-pressure permeate, recompression, lower purity (D-023).
- Firing H-101 directly on the tail gas at 140 kPa(a) without K-102: H-101 takes only 8.6 %
  of it, so the compressor stays for the rest. It is a basic-engineering option.
- Not assessed here; an open basic-engineering option instead: desorbing the tail gas at or
  near the fuel gas header pressure (about 450 kPa(a)), which removes K-102 (0.81 MUSD bare
  module, about 0.2 MEUR/a of power) and E-103, at the cost of a lower hydrogen recovery.
  The published basis used here (Matijasevic and Petric 2016, NETL 2022) gives no recovery at
  that desorption pressure, so the option cannot be priced without vendor data. It pays if
  the recovery lost is worth less than the compressor saved.

The benzene absorber of I-07 is not included. About 232 kg/h of aromatics (S34 + S19) go to
the site fuel gas header and are burned there. Recovering them (about 1.6 % of the benzene
make) is a basic-engineering option if the site's fuel gas specification asks for it.

Open (basic engineering, not I-07):
- the vendor's PSA performance (recovery at a 40 % H2 feed, number of beds, cycle, tail-gas
  surge drum) and a budget price;
- the site fuel gas header pressure (I-05);
- K-102's type: at a ratio of 3.36, about 240 kJ/kg of head and about 3460 m3/h of suction gas
  it is more likely reciprocating (two stages with an intercooler, since one stage discharges
  at about 436 K, above the usual limit of about 150 degC, ASSUMED as a rule of thumb) or an
  oil-flooded screw than the centrifugal machine of the list type and its CAPCOST price (an
  upper estimate). The discharge temperature for FG-127 and E-103 is taken from the simulated
  aftercooler duty at the balance script's Peng-Robinson cp (436 K; the script's own outlet
  is 431 K), not from an assumed cp;
- the tail-gas side's back-flow case: on a K-102 trip the suction (FG-126, the PSA tail-gas
  surge drum) settles out towards the header pressure through the machine and its non-return
  valve, so FG-126 is designed for 6 barg as K-102 and FG-127 (D-012 on the header pressure,
  review of PR #327); the relief scenario and the surge drum's design pressure go to the P&IDs
  and the vendor;
- whether the hydrogen returns to the make-up line instead of the K-101 suction;
- a new optimisation of the purge H2 fraction of D-007 now that the purge is recovered.

### D-025 P&IDs of the whole plant: sheet split, conventions and content (2026-11-04, S3b)
Decision: the simulated PFD (D-024) is drawn on seven DEXPI 2.0.1 sheets, one per PFD section,
declared in `plant.yaml`. Each sheet's first revision was written by `scripts/draft_P-0n.py`
(authoring API of core v1.4.1, shared bits in `scripts/pid_common.py`); the sheets are
hand-maintained from then on and the scripts are provenance only, as in ammonia-1.

| sheet | section | equipment |
|---|---|---|
| P-01 | feed, heater and reactor | V-100, P-101, P-101B, E-101, H-101, R-101 |
| P-02 | HP separator and recycle gas | E-102, V-101, P-102, P-102B, K-101 |
| P-03 | purge PSA and tail gas | PK-101, K-102, E-103 |
| P-04 | stabiliser | C-201, E-201, V-201, P-201A/B, E-202 |
| P-05 | benzene column and product | C-202, E-203, V-202, P-202A/B, E-204, E-207 |
| P-06 | toluene column, toluene recycle, biphenyl | C-203, E-205, V-203, P-203A/B, E-206, P-204A/B, PK-201 |
| P-07 | flare, nitrogen and natural gas headers | (headers only) |
| P-08 | cooling water and steam headers | (headers only) |

The utility headers were planned on one sheet (P-07). With every consumer branch drawn on the
header sheet (the off-page check asks the named sheet to carry the line), about 35 branches do
not fit one A3 frame legibly, so they are split: P-07 for the flare, nitrogen and natural gas,
P-08 for cooling water, steam and condensate (S3b, while drawing P-03).

Conventions (all ASSUMED where they set a value):
- Numbers. New lines n30 and up on sheet P-0n, headers on P-07 from 701 and on P-08 from 801;
  instruments n01
  and up on sheet P-0n. The PFD lines keep their numbers. A line that continues on another
  sheet is drawn on both with the same number, and each off-page connector names the other
  end and its sheet (`cheme.offpage-mismatch` checks it).
- Junctions. The drafting API continues a line through a tee and lets a line start or end only
  at a nozzle, a tee branch or an off-page connector, so the line number cannot change at a
  mixing point. Two PFD lines that were the continuation of another after a junction are
  therefore merged into the run they continue: PG-105 (S5, combined reactor feed) into HG-115,
  and PG-109 (S9, quenched effluent) into PG-108. Their streams are named in the notes of the
  run's line-list entry. HG-115 is DN300 over its whole length (the D-012 size of S5,
  two-phase 10 m/s): the recycle gas alone needs DN250 at 15 m/s and runs at about 11 m/s in
  DN300, ASSUMED.
- Spares. Every process pump has an installed spare with its own suction and discharge
  isolation, suction strainer and discharge check valve. P-101 and P-102 keep their tags for
  the running pump (the flowsheet, estimate, plot plan and LCA use them); their spares are
  P-101B and P-102B. New pumps are tagged A/B.
- Control valves are drawn as the final element with their instrument; block and bypass
  valves of the control valve stations are left to the detail P&IDs (S9) and listed as an
  open item, as ammonia-1 did.
- Relief. A relief valve is drawn wherever a credible overpressure exists; its set pressure is
  the protected item's design pressure (D-012) and the case that makes it necessary is named
  in `piping/special-items.yaml`; the governing case, the load and the orifice come from the
  relief study (S8). Hydrocarbon relief and vents go to the flare header (P-07), and so do the
  tube-rupture reliefs on cooling-water sides (PSV-215, PSV-414), which carry process gas;
  steam-side and thermal-only cooling-water-side relief (PSV-309, PSV-515, PSV-516, PSV-616)
  go to atmosphere at a safe location. The authoring API has no safety
  valve class (core#132, filed in S3b): the draft draws a globe valve and `pid_common.make_safety_valve` changes its
  class, tag property and symbol (the edit ammonia-1's D-027 made by hand).
- Trips go into `control/cause-effect.yaml`; the sheet only names the interlock.
- Vents and drains. Every vessel and column has a bottom drain with a block valve to the closed
  drain system (DR-138, DR-240, DR-445, DR-446, DR-551, DR-552, DR-651, DR-652); the process
  vents are the pressure-control vents to the flare (PV-104, PV-504, PK-201) and the relief
  lines. Exchanger and pump vents and drains, high-point vents, column top maintenance vents,
  sample points and the control valve block and bypass valves are left to the detail P&IDs
  (S9), as ammonia-1 did.
- Cooling water isolation. The CW inlet and outlet block valves of E-102, E-103, E-201, E-203,
  E-205 and E-207 are not drawn yet; they are an S9 open item with the exchanger vents and
  drains. They are what makes the blocked-in thermal relief case of PSV-309, PSV-515, PSV-516
  and PSV-616 credible, and those PSVs stay for that reason.
- Gas in the cooling water. A tube rupture in E-102 (loop gas) or E-201 (stabiliser overhead)
  also carries gas with the CW return to the cooling tower. Hydrocarbon / hydrogen detection on
  CWR-231 and CWR-441 (or a degassing point before the tower) is an open item for S6 (HAZOP)
  and S9.

P-01 (feed, heater and reactor):
- V-100: fresh toluene on level control (LIC-102, LV-102), toluene recycle TO-123 from
  P-203A/B (P-06), pressure by a nitrogen blanket through the self-acting regulator PCV-105 and
  a vent PV-104 to the flare (PIC-104), relief PSV-118 (blanket regulator failed open, fire).
- P-101/P-101B: the reactor toluene feed FIC-103/FV-103 sets the plant load; minimum flow
  FIC-106/FV-106 back to V-100 (high-head multistage service).
- M101: the make-up hydrogen (FIC-108, set point from the loop pressure PIC-205 on P-02) and
  the toluene join the recycle gas HG-115 ahead of E-101.
- Loop relief PSV-119 on the cold combined feed: from the E-101 inlet through the H-101 coil,
  R-101, the E-101 tube side and E-102 to V-101 there is no isolation valve, so one device
  protects the fired coil and the hot sections from the cold end (V-101 has its own, P-02).
  The sources of overpressure are P-101 at shut-off and the make-up hydrogen against a blocked
  loop, and fire.
- H-101: outlet temperature TIC-111 on the fuel valve TV-111. The main fuel has double block
  and bleed (XV-112 and XV-125 in series, bleed XV-126 on NG-139 to a safe location), closed by
  US-112 on coil flow low-low FZ-110 (I-101), R-101 outlet temperature high-high TZ-113 (I-102)
  or fuel pressure low-low / high-high PZ-127 (I-104). Pilot gas, flame detection and the
  burner management system are the heater vendor's (open item); the sheet draws the main fuel
  train outside the package.
- Reactor feed cut-off: XV-120 on the toluene feed TO-103 and XV-121 on the make-up hydrogen
  HG-104, both closed by US-122 on I-101, I-102 and I-202, so no toluene and hydrogen enter a
  loop without firing control, without recycle gas (below the H2/aromatics ratio of 5 against
  coking, D-007) or in a runaway, and E-101 has nothing left to preheat. HG-104 has a battery
  limit block valve and a check valve against loop gas flowing back into the hydrogen supply.
- I-102 also opens the depressuring valve XV-209 (P-02) automatically: a runaway of the
  exothermic HDA and hydrocracking reactions in a refractory-lined hot-hydrogen vessel is the
  case API 521 depressuring is meant for, and an operator action is too slow for it. The rate
  (the API 521 target pressure and time), the restriction orifice and the flare load are S8;
  the manual HS-209 stays for fire and leaks. R-101 bed/skin temperatures TI-124 (indication
  and alarm) are added; one TZ-113 sensor is not the final basis of I-102: sensor redundancy and
  voting (e.g. 2oo3), the SIL of every trip and the trip set points come from S4 (control and
  safeguarding) and S6 (HAZOP / LOPA), as `control/cause-effect.yaml` says.
- V-100: low-low level LZ-123 stops P-101/P-101B (I-103), as on every other pump suction drum.
- Quench: TIC-115 on the quenched effluent sets the quench valve TV-115 on AR-117.

P-02 (HP separator and recycle gas):
- E-102: effluent to cooling water (CWS-230/CWR-231, DN350 for 5.07 MW at the design-basis
  10 K range and 1.5 m/s, ASSUMED); TI-201 on the outlet. PSV-215 on the CW side (tube
  rupture of the 42 barg loop into the CW side: the CW-side design, 6 barg, is below 10/13 of
  the 42 barg process side, the API 521 criterion; blocked-in CW side), set at a 6 barg CW-side
  design pressure, ASSUMED (the design basis gives no CW pressure). It discharges through
  FL-238 into FL-234 and the flare, not to atmosphere: a tube-rupture relief carries hydrogen,
  methane and benzene. Whether a bursting disc is needed for the fast tube-rupture transient is
  for S8.
- V-101: level LIC-202 on the let-down valve LV-202 to C-201; separate low-low trip LZ-203
  closing the shutdown valve XV-204 (I-201: gas blow-by from the 32 barg separator into the
  9 barg stabiliser), high-high LZ-206 stopping K-101 (I-202: liquid carry-over). AR-118 (S18)
  is merged into AR-116, which keeps DN100 through the let-down (the liquid flashes after
  LV-202), as PG-105 and PG-109 on P-01. Relief PSV-214 (fire; blocked gas outlet with the
  make-up hydrogen and P-101 running), set 42 barg, to the flare.
- K-101: loop pressure PIC-205 on the suction sets the make-up hydrogen FIC-108 (P-01); the PSA
  hydrogen HG-125 joins the suction (M102). Anti-surge: UIC-207 with the recycle valve UV-207
  on HG-232 (DN200, 70 % of the rated flow, ASSUMED) from the discharge ahead of the check valve
  CV-115. HG-232 returns to PG-110 on P-01, upstream of the effluent cooler E-102, so the
  recycled gas is cooled by E-102 and passes the suction drum V-101 (skill
  pid-design-compressors, CCPS 4.4.11.2): a return straight into the suction would heat up on
  every pass during long recycle (start-up, turndown). UIC-207 takes the suction flow FT-218,
  the suction pressure PT-219 and the discharge pressure PT-220 (suction temperature from
  TI-201); TI-221 (discharge temperature) and VI-222 (vibration) with alarms. Open items for
  the compressor vendor: the surge line and the algorithm, the flow element type, the dead
  volume of the longer recycle loop in the surge transient, shaft vibration, axial position,
  lube oil, seals and the machine trips. No discharge PSV of its own: HG-115 has no isolation
  valve from K-101 to PSV-119 (P-01), which protects it. The type of CV-115 (DN300, swing as
  drawn) is chosen from the reverse-flow transient on a K-101 trip (usually a non-slam type),
  with the vendor (S5/S8).
- K-101 isolation: following the loop relief philosophy (no isolation valve between the loop
  equipment and PSV-119 / PSV-214), K-101 has no suction or discharge block valve. It is
  isolated for maintenance by depressuring the whole loop to the flare (XV-209), purging with
  nitrogen and fitting spectacle blinds at its suction and discharge flanges; the blinds,
  nitrogen purge connections and vents are drawn with the detail P&IDs (S9).
- Ratio: FI-216 measures the recycle gas on HG-115; FFI-217 computes the H2/aromatics ratio at
  the reactor inlet from FI-216, AIC-210, FIC-108 and FIC-103 with a low alarm at 5 mol/mol
  (D-007). The ratio is indicated and alarmed, not controlled: the toluene sets the load
  (FIC-103) and the make-up hydrogen holds the loop pressure (PIC-205 -> FIC-108), so the ratio
  follows the K-101 throughput. Whether a low-low ratio trip into US-122 is needed, and the
  ratio control intent of the loop register, are S4 items.
- Depressuring: XV-209 (FL-233) opens on I-102 or by hand (HS-209), to the flare; rate and
  orifice with S8.
- Purge: AIC-210 (hydrogen in the recycle gas) sets the purge flow FIC-211 / FV-211 on HG-113 to
  PK-101 (P-03): the purge holds the loop's 40 mol% H2 specification (D-007).
- P-102/P-102B take the quench liquid off AR-116 (SPL2, AR-235); continuous minimum flow
  AR-237 through the restriction globe valve HV-237 back to V-101, since TV-115 can close.

P-03 (purge PSA and tail gas):
- PK-101 is one package item (adsorber beds, switching valves, tail gas surge drum, cycle
  control, the vendor's relief); the sheet draws its tie-ins with block valves (HV-330 purge
  in, HV-331 hydrogen out, HV-332 tail gas out; HV-332 sits downstream of the PSV-307 take-off,
  so no block valve isolates the tail gas side from its relief). PIC-301 holds the adsorption pressure on the
  hydrogen product with PV-301 (step PV101 of the simulation, 3540 -> 3250 kPa(a)); AI-302
  reads the product purity.
- K-102: PIC-303 holds the tail gas pressure at the suction (the PSA desorption pressure,
  140 kPa(a)) on the spillback PV-303 / FG-330, which returns cooled gas from downstream of
  E-103 (DN150, full flow for start-up and PSA turndown, ASSUMED). Check valve CV-127 and the
  block valve HV-327 on the discharge to the fuel gas header. K-102 is drawn as a reciprocating
  compressor (DEXPI ReciprocatingCompressor), the positive-displacement machine D-024 assumes
  and PSV-308 protects. Machine protection in its package. Whether the PSA package relief alone
  covers the switching-valve-failed-open case is for the vendor (S8).
- Relief: PSV-307 on the tail gas side FG-126 (a switching valve failed open puts 36 bar feed
  gas into the 6 barg side; back-flow from the header on a K-102 trip); PSV-308 on the K-102
  discharge (blocked outlet; the likely machine is positive displacement, D-024); both 6 barg
  to the flare. PSV-309 thermal relief on the E-103 CW side to atmosphere; tube rupture is not
  a case there (both sides 6 barg).
- FG-128 leaves to the site fuel gas header at the battery limit (no header drawn: it is
  outside the plant, D-009), with FI-306 for the export.

P-04 (stabiliser):
- The simulation lumps the column, partial condenser, drum and reboiler in step C201. The sheet
  adds the reflux drum V-201 and the reflux pumps P-201A/B (equipment list, sizes ASSUMED). The
  overhead and reboiler lines are sized on the vapour rates of `scripts/concept_sizing.py`
  (top 350 kg/h, bottom 13.5 t/h); the reflux is about 175 kg/h, so the reflux lines are DN25.
- Control: the column pressure PIC-404 on the off-gas valve PV-404 (FG-119 to the site fuel gas
  header); V-201 level LIC-405 on the reflux LV-405, so all condensed liquid is refluxed and the
  off-gas is the only distillate (D-008); tray temperature TIC-402 on the MP steam TV-402;
  sump level LIC-408 on the bottoms LV-408 (AR-120 flows to C-202 by the pressure difference).
  The reboiler is a thermosyphon (AR-437 / PG-438) with a steam trap ST-444 on the condensate.
- Reflux pumps: continuous minimum flow AR-436 through HV-436 back to V-201; LZ-411 low-low
  stops them (I-401).
- Relief: PSV-413 on the column top protects C-201, the E-201 process side and V-201 (no
  isolation valve between them), set 9 barg, to the flare; the gas blow-by from V-101 is the
  likely governing case (S8), with I-201 on P-02 as the layer before it. PSV-414 on the E-201
  CW side: tube rupture is a case, since the CW-side design (6 barg) is below 10/13 of the
  9 barg process side (6/9 = 0.67 < 0.77); it discharges through FL-442 into FL-443 and the
  flare, as PSV-215 does.
- Steam lines are sized from saturated-vapour densities and latent heats of the NIST Chemistry
  WebBook (SRD 69, water, IAPWS-95 formulation, isobaric data at 0.45, 1.5 and 4.2 MPa, the
  saturation rows at 421.05, 471.44 and 526.41 K): vapour 2.416, 7.592 and 21.13 kg/m3, latent
  heat 2120.3, 1946.4 and 1698.1 kJ/kg (looked up 2026-11-04, review of PR #328; the earlier
  recalled values differed by less than 0.3 %, the DN stay LS-540 DN250, MS-439 DN100, HS-640
  DN50). The condensate lines stay ASSUMED for the flash.

P-05 (benzene column and product):
- Added: reflux drum V-202 and reflux / product pumps P-202A/B (lumped in step C202). Total
  condenser E-203; V-202 pressure by a nitrogen pad (self-acting PCV-505) and a vent PV-504 to
  the flare (PIC-504). Reflux on flow FIC-507 / FV-507 (R 2.18, D-014); distillate on the drum
  level LIC-506 / LV-506 through the product cooler E-207 to storage, with TI-509, the purity
  analyser AI-510 and FI-511 on BZ-121 (S21). Tray temperature TIC-502 on the LP steam TV-502
  (E-204 thermosyphon, steam trap ST-541); sump level LIC-508 on TO-122 to C-203.
- Relief: PSV-514 on the C-202 top (C-202, E-203 process side, V-202), 3.5 barg, to the flare;
  thermal relief PSV-515 / PSV-516 on the E-203 and E-207 CW sides. P-202A/B: minimum flow
  BZ-536 (HV-536), low-low LZ-512 stops them (I-501).
- E-207 benzene side and BZ-121 are rated for the P-202A/B shut-off (10 barg, the pump design)
  rather than protected by a process-side PSV: they sit on the pump discharge behind LV-506,
  and a closed storage inlet with LIC-506 opening blocks them in at the pump's shut-off head
  (about 0.5 barg in V-202 plus 4 to 5 bar). Rating removes the case; a relief valve would
  have to discharge benzene liquid to a closed system. The equipment list carries 10 barg
  (was 3.5 barg as C-202); the BZ-121 pipe class follows (S9).
- Layout: the DN450 overhead would have run 32 m from C-202 (set back from the rack, D-018) to
  E-203 in the condenser row with no rack to carry it, so E-203, V-202, P-202A/B and E-207 are
  placed beside C-202 (`layout/equipment-placement.yaml`, ASSUMED); the rack still carries the
  product and the bottoms.

P-06 (toluene column, toluene recycle, biphenyl):
- Added (lumped in step C203): reflux drum V-203, vacuum package PK-201 (not sized, D-008:
  load, type and power are vendor inputs), reflux and recycle pumps P-203A/B (the C-203
  distillate pump of D-010) and biphenyl bottoms pumps P-204A/B.
- Control: vacuum PIC-604 on the PK-201 suction PV-604; reflux FIC-607 / FV-607 (R 0.5);
  V-203 level LIC-606 on the toluene recycle LV-606 (TO-123 to V-100 on P-01, FI-609); tray
  temperature TIC-602 on the HP steam TV-602 (E-206 thermosyphon, steam trap ST-641); sump
  level LIC-608 on the biphenyl LV-608 (DP-124, traced, to storage).
- Relief: PSV-615 on the column top (C-203, E-205 process side, V-203), 3.5 barg, to the flare;
  an E-206 tube rupture (HP steam at 41 barg into the 3.5 barg column) is likely to govern it
  (S8). Loss of vacuum is not an overpressure case (full vacuum design). PSV-616 thermal relief
  on the E-205 CW side. P-203A/B: minimum flow TO-636, low-low LZ-612 stops them (I-601).
- Open: P-204A/B carry 352 kg/h, far below a centrifugal pump's best point; their type and
  minimum-flow or relief protection are for the pump selection (S5). The reboiler return under
  vacuum is DN700 by the D-012 two-phase velocity, to be checked with the reboiler design.

P-07 (flare, nitrogen and natural gas headers) and P-08 (cooling water and steam headers):
- Every utility or relief line that a process sheet sends to P-07 or P-08 is drawn there as a
  branch on its header, with the same number and an off-page connector naming the source and
  its sheet, so `cheme.offpage-mismatch` checks both ends.
- Flare header FL-701 collects the ten relief and vent lines (PSV-118, PSV-119, PSV-214,
  PSV-307, PSV-308, PSV-413, PSV-514, PV-504, PSV-615, PK-201) to the site flare at the battery
  limit; DN300 is a placeholder until the relief loads (S8). The knock-out drum, seal and stack
  are the site's; the header purge and slope are open (S8 / detail).
- Nitrogen header N2-702 (to PCV-105 and PCV-505) and natural gas header NG-703 (to the H-101
  burners) from the site networks, DN50 ASSUMED.
- Cooling water headers CWS-801 / CWR-802, DN500 for 10.8 MW at the design-basis 10 K range and
  1.5 m/s, with six users; LP, MP and HP steam headers LS-803, MS-804, HS-805 to the three
  reboilers; condensate header CD-806 DN80 to the site return (flash recovery open).
- The CW and flare branches to A-200 run along the main rack PR-1; to reach the benzene column
  group (set back one column height from PR-1, D-018) a spur rack PR-2 (x 127, y 50 to 95,
  one level at 6 m, ASSUMED) is added to `layout/site-plan.yaml`. The 3D model
  (`layout/plant-model.yaml`) is left for S5: rebuilt now, it routes the new P&ID nozzles and
  reports walkway-riser and escape-way findings that the 3D layout section resolves.

### D-026 Control and lists: loops, fail positions, sequences, trips, narrative, philosophy (2026-11-04, S4)
Decision: the control intent of hda-1 is recorded in `control/loops.yaml`, `sequences.yaml`,
`cause-effect.yaml`, `process/narrative.md` and `control/philosophy.md`, as ammonia-1's D-030
did. All of it is PROPOSED: it states intent for the HAZOP (S6) and the reviewers and claims no
SIL, no independence of layers and no safe operating limit.

Loops (28, one per controller on P-01 to P-06; `cheme control report` 0 findings):
- Load and recycle: FIC-103 sets the plant load (toluene, the limiting reactant); the fresh
  toluene is on the V-100 level (LIC-102) and the toluene recycle on the V-203 level (LIC-606),
  so the recycle balances itself. FIC-106 holds the P-101 minimum flow.
- H2/aromatics ratio: not a loop. The recycle gas is fixed by K-101 (no capacity control drawn)
  and the loop pressure, so the ratio follows the toluene; FFI-217 indicates it and its low alarm
  is on FIC-103 with the response "reduce the load". A low-low ratio trip into US-122 is not
  added: FFI-217 is computed from an analyser (AIC-210) and three flows, and composition
  measurements are avoided in safety functions (skill control-safeguarding-and-interlocks); the
  coil flow trip I-101 and the compressor trips I-202/I-203 cover the loss of recycle gas, which is
  the credible cause of a fast ratio drop. The HAZOP (S6) may revisit this.
- Reactor: TIC-111 on the fuel (setpoint S7), TIC-115 on the quench (setpoint S9); loop pressure
  PIC-205 cascades onto the make-up hydrogen FIC-108; the recycle gas hydrogen AIC-210 (40 mol%,
  D-007) cascades onto the purge FIC-211; UIC-207 anti-surge. PSA: PIC-301 on the product
  back-pressure (S30), PIC-303 on the K-102 spillback (S33). Columns: tray temperature on the
  reboiler steam, reflux on flow (C-202, C-203) or on the drum level (C-201, no liquid
  distillate, D-008), distillate or recycle on the drum level, bottoms on the sump level, pressure
  on the off-gas (C-201), the vent with a nitrogen pad (V-100, V-202) or the vacuum package
  suction (C-203).
- Setpoints: a design-case value of `process/flowsheet.yaml` wherever one exists (temperatures and
  pressures linked with `stream:` so validate keeps them in step). The three flow setpoints
  (FIC-103 S3, FIC-108 S4, FIC-211 S13) name their stream in `source` only: core 1.4.1 compares a
  kg/h target with a kg/h stream value only through Pint (`foundation/units._convert` sends every
  unit outside K, °C and the pressures to Pint, even an identical one), and the plant validate job
  installs core without the `units` extra, so a link would leave a `cheme.control-case` info that
  the gate `control-complete` fails on. Reported as core#153; the link is restored
  once core compares identical units. Reflux setpoints are R times the design distillate (FIC-507
  2.18 x 12498.2 = 27246 kg/h; FIC-607 0.5 x 4884.74 = 2442.4 kg/h), own calculation.
- ASSUMED (the reason in each target's source): levels 50 %; the V-100 and V-202 vents at
  155 kPa(a), 5 kPa above the 150 kPa(a) operating pressure with the pads 5 kPa below; the P-101
  minimum flow 6100 kg/h (30 % of S3) until the vendor; the K-101 control line 10 % from the surge
  line; the column tray setpoints at the simulated bottoms temperatures (S20, S22, S24) until the
  column design (S7) gives the control tray, since the shortcut models give no tray profile.

Fail positions (review 2026-11-04-basic-pids#29): all 33 actuated valves now carry one on the
P&IDs (FailAction and an F.C./F.O. label, `scripts/s4_fail_positions.py`) and in the instrument
list. The rule: the failure goes to the safe side of the valve's own hazard. Closed (F.C.): feed,
fuel and hydrogen (FV-103, LV-102, FV-108, TV-111, XV-112, XV-120, XV-121, XV-125), steam
(TV-402, TV-502, TV-602), let-down and bottoms between pressure levels and products (LV-202,
XV-204, LV-408, LV-506, LV-508, LV-606, LV-608), the purge and the PSA product (FV-211, PV-301)
and the vacuum suction PV-604 (isolates C-203 from the package and the flare when PK-201 stops;
C-203 is full-vacuum rated). Open (F.O.): the depressuring valve XV-209 (a depressuring valve
that fails closed does not depressure on loss of air or power, so loss of instrument air
depressures the loop: the hot hydrogen loop without firing control is safest at low pressure),
the fuel bleed XV-126, the anti-surge UV-207 and the spillback PV-303 (machine protection), the
minimum flow FV-106, the quench TV-115, the vents PV-104 and PV-504 and the off-gas PV-404 (no
overpressure), the refluxes LV-405, FV-507 and FV-607 (column tops kept cool). For the HAZOP (S6)
to confirm.

Trips (`control/cause-effect.yaml`): the nine S3b trips get a delay, latching, a manual reset
condition and their bypass (start-up bypasses removed by the operator only on I-101, I-103, I-201,
I-401, I-501, I-601, each at a named sequence step, and since the review of PR #357 on the
pumps-stopped leg of I-106; besides these, the burner management bypasses the low-low leg of I-104
by itself for its light-off period, the high-high leg never), all ASSUMED as usual practice for a first issue; no trip
setpoint is given (they need the design limits and S6). Added: I-105 burner management of the
H-101 package (flame failure, purge, air; acts on the plant fuel double block and bleed) and I-203
K-101 machine protection (stops K-101, cuts the feed as I-202 does). Both have the package item as
their cause, since the trip sensors are vendor scope and not on the P&IDs (D-025 open items). No
trip acts on a control valve of the loop register; UIC-207 opens UV-207 on a machine stop by its
own anti-surge function. Questions for S6: sensor voting of I-102 (one TZ-113 drawn), whether I-104
and I-105 should also cut the feed, the SIL of every trip.

Sequences (7): SEQ-START-RXN (nitrogen purge, hydrogen pressure-up, K-101 on full recycle,
heater light-off by the BMS and heat-up on circulating hydrogen, V-100 and P-101 on minimum
flow, toluene at 30 %, quench and let-down, design load and the cascades), SEQ-START-PSA,
SEQ-START-DIST, SEQ-SD-PLANT, SEQ-TRIP-RXN, SEQ-TRIP-PSA, SEQ-EDP. Rates, temperatures and step
times ASSUMED (start-up toluene 6100 kg/h = 30 % of S3, make-up 100 kg/h, heat-up hold 873.15 K =
22 K below S7, PSA purge 1000 kg/h) until the vendors' procedures. Connections the sequences need
that the P&IDs do not show, for S9: nitrogen purge points and loop vents, the PSA start-up and
the benzene off-specification routing, valve position feedback (limit switches) on the XV valves,
the nitrogen connection that breaks the C-203 vacuum. The control system and the trip logic are
taken to be on an uninterruptible supply (ASSUMED).

Derived assessments brought up to the S3b lists (review 2026-11-04-basic-pids#27): the 14 items
the P&IDs added are now in `estimate/cost-basis.yaml`. The spares P-101B and P-102B take their
running pump's simulated power; the column pumps the flowsheet lumps into the column steps get a
shaft power from `scripts/s4_pump_powers.py` (P = m / rho x dp / 0.65, densities from `thermo`,
differential pressures ASSUMED from the P&ID routing): P-202A/B 8.5 kW, P-203A/B 1.42 kW, and
P-201A/B (0.03 kW) and P-204A/B (0.07 kW) at the correlation's 1 kW minimum. PK-201 is excluded
from the correlation estimate (vendor package, no size, D-008) and stays in the 15 % uncovered
allowance, whose text in `estimate/tea.yaml` now says so (the fraction is unchanged). K-102 is
purchased cost only (the package FBM is centrifugal only), as is H-101; the K-102 and H-101
factors go to the class 4 estimate (S5). The reflux drums V-201/V-202/V-203 were purchased-only in
the first S4 commit; since the review of PR #357 they are priced like V-100 with the vertical vessel
correlation and its bare module factor (D-019), so the ASSUMED `purchased_installation` factor 2.5
of `estimate/tea.yaml` now multiplies only H-101 and K-102, and its source says why it is used for
the reciprocating K-102 too (the same screening factor rather than a second unsourced number, likely
low). `cheme assess equipment/tea/lca --write` after that fix: 36 items (31 bare module, 2 purchased
only, 2 the project's own cost, 1 excluded, 0 not covered); bare module total of the items with all
factors 5.74 MUSD (6.12 before S4), purchased-only items 1.42 MUSD x 2.5, fixed capital 28.06 MEUR
(27.36 before S4), LCOP 876.6 EUR/t (875.5), NPV -148.9 MEUR; the LCA result is unchanged (its
dataset and manifest record the new list hashes). The column pumps P-201..P-204 (about 10 kW shaft
running, about 90 MWh/a) stay outside the flowsheet's power feed and so outside the TEA power cost
(about 2 % of the plant's 4.5 GWh/a); the LCA covers them in its cut-off `small-pumps-power`
(120 MWh/a upper estimate), whose reason now gives these numbers.

Review of PR #357, round 1 (2026-11-05): protective functions and sequences made consistent.
- Loss of quench, I-106 (new). Without quench E-101 receives the reactor effluent at 936.2 K (S8,
  DWSIM) against its design temperature of 645 degC = 918.15 K; a P-102 trip, I-201 (which stops
  both quench pumps), TV-115 closed or AR-117 blocked all lead there, and TIC-115 is the control
  loop. I-106 trips on a new independent element TZ-128 on PG-108 after the quench point (P-01) or
  on both quench pumps stopped, and acts like I-101 on the firing (US-112) and the feed and make-up
  hydrogen (US-122). Its TAHH lies between the TIC-115 setpoint 893.15 K (S9) and 918.15 K; value,
  voting and SIL are S6's. Scenario handed to S6: loss of quench, E-101 above its design
  temperature in hot hydrogen. The TZ-128 signal to US-112 is in the DEXPI model and the C&E but
  not drawn: any route from PG-108 to US-112 crosses PG-106 and NG-137, and the crossings were not
  accepted; the P-01 note names the trip.
- Start-up quench. The quench liquid is V-101 liquid, which exists only after the first toluene, so
  SEQ-START-RXN keeps the quench in step S6 and states that E-101 takes the unquenched effluent in
  step S5. Estimate (own, ASSUMED): at the 873.15 K inlet hold and 30 % toluene with the full
  recycle gas the adiabatic rise is about 0.3 x 41.1 K (the design rise 936.2 - 895.15 K) / 0.95
  (the lower heat capacity flow without 70 % of the toluene) = about 13 K, so the outlet is about
  886 K, about 32 K below the E-101 design temperature and below the normal quenched 893 K (a lower
  inlet temperature also lowers the conversion, so the estimate is an upper one). S5 completes only
  with TZ-128 below its alarm, and the TZ-128 leg of I-106 is never bypassed. TIC-115's operator
  note and the sequences header now say the same.
- K-102 and PSA trip, I-301 (new). On a K-102 machine trip or a PSA package trip US-311 (P-03)
  stops K-102, holds the PSA cycle and closes the new purge shutdown valve XV-310 (BallValve DN 80 on
  HG-113 at the PSA inlet, fails closed); FV-211 stays the control valve of FIC-211 and is closed by
  the operator behind it (SEQ-TRIP-PSA). PSV-307/PSV-308 are no longer the answer to a foreseeable
  machine trip. SEQ-START-PSA aborts on I-301 and opens XV-310 only in step S2.
- SEQ-TRIP-RXN step S1 now closes XV-120 and XV-121 by the operator, so after I-104 or I-105 (which
  stop only the firing) the step completes and the toluene is stopped; I-104, I-105 and I-106 are
  in the reset conditions of SEQ-TRIP-RXN and SEQ-START-RXN. Philosophy F-FUEL says the same.
- SEQ-EDP keeps K-101 running during the depressuring (the recycle gas is the only heat sink of a
  runaway reactor) and stops it in a new step S2 at the vendor's low suction pressure or surge
  limit, or at once on I-203.
- Relief and flare load case for S8: global instrument air failure, in which XV-209 depressures the
  loop and the fail-open vents PV-104 and PV-504, the off-gas PV-404, the anti-surge UV-207 and the
  spillback PV-303 open at the same time; likely a governing flare load case. Also for S8: the
  PSV-413 blow-by case is now worded as LV-202 and XV-204 sticking open or passing (both fail
  closed).
- Practice citations: the depressuring practice is API Std 521, 7th ed. (2020), vapour
  depressuring section 5.20; the section number is taken from the NeqSim documentation's index of
  the standard (equinor.github.io/neqsim/safety/depressurization_per_API_521, read 2026-11-05), the
  standard itself was not read, so S8 confirms the clause and its criteria. The burner management
  codes EN 746-2 and NFPA 86 are named for orientation only (skill); the applicable code is the
  heater vendor's and S6's to set.
- Lists and sheets: TZ-128, US-311 and XV-310 added (instrument list; P-01, P-03); the sheet notes
  and the US-112/US-122 services name I-105, I-106 and I-203; the P-02 note names I-203; TI-124 and
  FFI-217 notes brought to the S4 state; LV-102 and XV-310 in F-AIR's closed list (now 22 closed
  and 12 open of the 34 actuated valves). The LIC-506 rationale now says that the LV configuration
  is chosen deliberately although the reflux is the larger outlet at R 2.18. The FIC-103 setpoint
  source names the propagated provenance of S3. The stream links of the three flow setpoints are
  open item I-13 (core#153).

## LCI summary (lca/inventory.csv, per kg benzene)

Regenerated in S3a (D-024) from the inventory with the purge hydrogen PSA (`cheme assess lca --write`,
`--balance`, `--coverage`). The "per kg" column is the plant flow over the 12 500 kg/h of benzene,
before allocation. `lca/inventory.csv` holds the quantities after energy allocation (benzene
75.5 %, biphenyl 2.1 %, fuel gas 22.4 %, D-013), e.g. toluene 0.932184 kg = 1.23418 x 0.755.

| exchange | plant | per kg benzene | provenance (flowsheet) | background to link later |
|---|---|---|---|---|
| feed:TOLF toluene (BPCL/IS 537 grade, D-020) | 15427.2 kg/h | 1.23418 kg | S1 (given, D-020, D-024) | toluene, market for (reformate/pygas extraction) |
| feed:H2MU make-up H2 (PSA grade 99.9/0.1 mol% H2/CH4, D-020) | 392.63 kg/h | 0.031410 kg | S4 (given, D-020; reduced by the PSA, D-024) | hydrogen, SMR with PSA / refinery network (+ CH4) |
| feed:POWER | 564.838 kWh/h | 0.045187 kWh | Q1, Q2, Q12, Q13 (K-102, D-024) | electricity, medium voltage, site grid |
| feed:FUEL fired heat | 3042.17 kWh/h | 0.243374 kWh | Q3 | heat from natural gas, industrial furnace |
| feed:MPS steam 1500 kPa(a) | 1424.87 kWh/h | 0.113990 kWh | Q5 (script, D-022, D-024) | steam in chemical industry (MP) |
| feed:LPS steam 450 kPa(a) | 3484.97 kWh/h | 0.278798 kWh | Q7 | steam in chemical industry (LP) |
| feed:HPS steam 4200 kPa(a) | 638.478 kWh/h | 0.051078 kWh | Q9 | steam in chemical industry (HP) |
| product:CW heat rejected | 10777.4 kWh/h | 0.862192 kWh | Q4, Q6, Q8, Q10, Q11, Q14 (E-103, D-024) | cooling water circulation |
| product:BENZENE | 12500 kg/h | 1 kg | S21 | functional unit |
| product:DIPHENYL biphenyl (95.2 mol%, D-024) | 352 kg/h | 0.02816 kg | S24 | avoided biphenyl or fuel oil |
| product:FUELGAS (PSA tail gas + stabiliser off-gas, 50.66 MJ/kg) | 2968.08 kg/h | 0.237446 kg | S34 + S19 | avoided natural gas firing |

Checks: `cheme assess lca --balance`: mass 15819.8 kg/h in, 15820.1 kg/h out (residual
-0.24 kg/h, 0.00 %); C 14079.5/14079.7 and H 1740.39/1740.37 kg/h: closed. By hand: in
1.26559 kg (1.23418 + 0.03141), out 1.26561 kg (1 + 0.02816 + 0.23745) per kg of benzene. The
stoichiometric toluene minimum is 1.1796 kg/kg benzene (92.138/78.112); the 4.6 % above it is
the biphenyl make and the aromatics in the fuel gas. `--coverage`: result "partial screening
carbon footprint" with no total (all 8 contributions are gaps). Boundary check: gap
`boundary-utility-unassigned` (R101B, D-021). DQR 2.33 (weakest technological
representativeness), primary data share 0 %. No impact result is claimed.

## Reaction and model evidence

| item | value used | source | status |
|---|---|---|---|
| Stoichiometry HDA, BIPH | as reactions.yaml | route chemistry | sourced (textbook chemistry) |
| Heats of reaction | -41.76, +15.04 MJ/kmol | formation enthalpies (chemicals: ATcT, CRC) | calculated |
| Reactor T range | inlet 895 K, outlet 938 K | US 3,291,849 (detailed description, reactor 44: 1100-1500 F, at most 1350 F); US 3,607,960 claim 4 (1050-1400 F) | sourced, read in full text (D-021); the recalled Douglas window is no longer used |
| Reactor T range (conflict) | 500-600 C, up to ~69 bar | Speight 2011 Ch. 11, via skill tech-petchem-aromatics | below both patents' thermal ranges; probably catalytic, not verified (book not read) |
| Pressure | 3.45 MPa (485 psig) | US 3,607,960 claim 4 (400-600 psig); US 3,291,849 (500-800 psig, about 600 psig) | inside the first, slightly below the second (D-021) |
| H2/aromatics | 5 (design choice, D-007) | US 3,607,960 claim 4 (3-10); US 3,291,849 (at least 2 per mol of liquid aromatic feed) | inside both; the value itself ASSUMED |
| Selectivity | 0.9734 (simulated) | biphenyl at equilibrium, formation data of materials.yaml (D-021) | calculated; bounds the biphenyl make only, optimistic as a selectivity (heavy ends and hydrocracking excluded) |
| Selectivity (evidence) | not used in the model; TEA scenario | US 3,607,960 Example 1: 94.5 % (primary reactors, 85 % conversion per pass, about 460 psig); reaction-evidence O2 | read in full text; at a higher conversion than R-101 (D-021) |
| Conversion per pass | 0.75 | US 3,291,849, detailed description (reactor 44: about 75 % of the toluene in its total feed); reaction-evidence O1 | given, transferred as the design value (staged gas quench at about 600 psig in the patent; not at R-101's pressure for the maturity evidence check, D-021) |
| Kinetics | none | - | not used: no readable thermal rate law with units and range; core has no homogeneous kinetic reactor (D-021) |
| IDAES HDA examples | none used | issue #302 links | read only as context; no data taken |

## Source register

| source | locator | access in this run | terms | use |
|---|---|---|---|---|
| Douglas (1988) Conceptual Design of Chemical Processes, McGraw-Hill | HDA case study (chapter and equation to verify) | not read (recalled) | book, facts cited only | none since D-021 (was: reactor window, H2 ratio, selectivity correlation) |
| US 3,291,849 A (Hydrocarbon Research, 1966), Hydrodealkylation | detailed description, paragraph "The reactor 44 is an internally insulated open chamber"; operating-conditions paragraph | full text, Google Patents, 2026-11-03 | patent, facts cited only | per-pass conversion 0.75, reactor window (D-021) |
| US 3,607,960 A (Gulf R&D, 1971), Thermal hydrodealkylation process | background (diphenyl in the feed; polyphenyls and higher boiling polymers in the effluent); claims 3 and 4; Example 1 | full text, Google Patents, 2026-11-03 | patent, facts cited only | biphenyl reversibility (as consistent with), window, Example 1 selectivity 94.5 % (D-021, reaction-evidence O2) |
| BPCL toluene data sheet (IS 537:2011) | table rows 1, 7, 8, 10, 13 | full text (PDF), 2026-11-03 | supplier data sheet, facts cited only | S1 composition (D-020) |
| Matijasevic and Petric (2016), Chem. Biochem. Eng. Q. 30(3) 291-304, doi:10.15255/CABEQ.2015.2337 | Table 1 (p. 3), p. 4, Fig. 3 (p. 8) of the authors' manuscript | full text (manuscript PDF at hatz.hr), 2026-11-03, Table 1 read again 2026-11-04 | journal article, facts cited only | S4 purity, PSA recovery, purity and feed limit (> 40 vol% H2), CO2 per t of hydrogen (D-020, D-023, D-024) |
| NETL (2022), Comparison of Commercial, State-of-the-Art, Fossil-Based Hydrogen Production Technologies, DOE/NETL-2022/3241 | Section 3.3.5.1 (p. 54); Exhibit 3-4, Case 1 streams 10, 11, 13 (p. 61); Exhibit 3-13, account 7.1 (p. 73) | full text (PDF at netl.doe.gov), 2026-11-04 | US government report (public domain), facts cited only | PSA pressure loss and tail gas pressure, PSA package cost scaled (D-024) |
| NETL (2019), QGESS Capital Cost Scaling Methodology, Revision 4 | exhibits of scaling exponents | full text (PDF at netl.doe.gov), 2026-11-04 | US government report | checked for a PSA exponent: none listed (D-024) |
| Chemical Engineering, Economic Indicators, Sept. 2024, p. 45 | CEPCI annual index 2018 = 603.1, 2023 = 797.9 | full text (PDF at chemengonline.com), 2026-11-04 | magazine, facts cited only | escalation of the PSA cost (D-024) |
| Hutabarat et al. (2026), J. Chem. Eng. Res. Prog. 3(1) 88-93, doi:10.9767/jcerp.20563 | eqs. 4 and 6 | full text, 2026-11-03 | CC BY-SA 4.0 | none (kinetics rejected, D-021) |
| Speight (2011) Handbook of Industrial Hydrocarbon Processes, Elsevier | Ch. 11 | via the library skill tech-petchem-aromatics | facts cited only | HDA temperature/pressure range |
| `chemicals`/`thermo` Python packages (bundled with cheme) | ATcT, CRC, Yaws, HEOS, IUPAC, TRC ideal-gas, ChemSep PR kij | used | MIT; underlying data facts | formation data, critical constants, PR flash |
| Cox, Wagman, Medvedev (1989) CODATA Key Values | CO2(g), H2O(g) formation enthalpies | recalled values | facts | LHV for allocation |
| IDAES examples-pse v2.0.0 HDA documentation | URLs in issue #302 | not opened in this run | BSD-style licence of IDAES (to record before any reuse) | context only |

## Method and dependency table

| step | method | status |
|---|---|---|
| Mass, component, element balances | cheme validate / process streams | closed |
| Reactor outlet | DWSIM conversion reactor (HDA, X 0.75 given) and equilibrium reactor (BIPH), D-021 | simulated; R101B isothermal (D-021) |
| Mixers, splitters, pass-throughs | cheme process propagate | calculated by cheme |
| Flashes, column splits, duties | `cheme process simulate` (DWSIM 9.0.5, PR), D-014, D-022; C-201 duties from scripts/hda_balance.py | calculated; property package not qualified (core#315) |
| Energy closure in core | `cheme process props --fill` | gated: no package for aromatics + H2 |
| Simulation | `cheme process simulate` (DWSIM) | converged, whole plant with the purge PSA, 13 iterations, 4 tears (D-024); energy audit closed (plant residual 0.88 kW, including R101B's unterminated 17.4 kW and X101's stated -4.39 kW); property regime not qualified |
| PSA PK-101 | DWSIM component separator, specified recoveries (H2 0.75 at 99.9 mol%, D-024) | specified, sourced (Matijasevic and Petric 2016, Table 1); not predicted |
| BFD/PFD build | `cheme process build` | works; P101 `Pumping`, H101 `HeatingInFurnace` since core v1.4.1 (D-016) |
| LCI | `cheme assess lca --inventory/--coverage/--balance` | written; backgrounds open |

## Open inputs

Status 2026-11-03 (D-016): I-05 resolved (notional Rotterdam-area site); I-01 to I-04 kept
ASSUMED; I-06 to I-12 carried, each with its reason and section in D-016.
Status 2026-11-03 after S2: I-01 and I-02 answered for the composition by published sources
(D-020); their supply conditions stay ASSUMED. I-06 answered (D-021): no model value rests on
the recalled Douglas values; the conversion and the window come from two patents read in full,
the biphenyl from equilibrium. Not covered by any readable source: the Douglas book itself,
whether Speight's 500-600 C is catalytic, and the benzene selectivity at R-101's conversion and
pressure (US 3,607,960 Example 1 gives 94.5 % at 85 %, D-021). I-07 closed (2026-11-04, D-024):
the PSA PK-101 and the tail-gas compressor K-102 are in the flowsheet, simulated, priced and in
the TEA (incremental NPV +0.27 MEUR, break-even package price about 4.2 MUSD); the benzene
absorber is not included, with its reason in D-024. I-12: product cooler E-207 added (D-022); the stabiliser stays a shortcut column
with the script's duties (D-022: core's rigorous partial condenser needs a liquid distillate).

- I-01 Fresh toluene specification (purity, C8 aromatics, non-aromatics, sulfur, water).
- I-02 Make-up hydrogen purity and supply pressure (source of hydrogen).
- I-03 Benzene product grade to meet (thiophene, non-aromatics, freezing point).
- I-04 Capacity and operating hours from an owner (100 kt/a and 8000 h/a are assumed).
- I-05 Site (utilities, grid, climate).
- I-06 Verify the Douglas (1988) values at their locator (reactor window, ratio, correlation and
  its validity range); resolve the conflict with Speight's 500-600 C.
- I-07 Purge hydrogen recovery and a benzene absorber on the purge; purge to H-101 as fuel.
  Closed (D-024): PSA and tail-gas compressor in the design; absorber and H-101 firing on the
  tail gas left to basic engineering with reasons.
- I-08 Vacuum system of C-203 (ejector steam or vacuum pump power) and the small pumps.
- I-09 Materials for hot hydrogen service (E-101, H-101, R-101) and reactor lining.
- I-10 Fugitive emission estimate (needs P&ID component counts) and non-routine emissions.
- I-11 Background datasets for every LCI exchange (all gaps) and the allocation decision.
- I-12 A benzene product cooler step (S21 to 313 K) and a stabiliser model whose partial
  condenser DWSIM solves (a rigorous column with a vapour product), D-014.
- I-13 Restore the `stream:` links of the flow setpoints FIC-103 (S3), FIC-108 (S4) and FIC-211
  (S13) in `control/loops.yaml` once core compares identical units without Pint (core#153, open
  since 2026-11-04); until then the setpoint-vs-case cross-check does not run for these three
  loops and their values are checked by hand (D-026).

## Missing library registry entries (chemicals/chemicals.yaml, for the consolidated PR)

toluene, benzene (with a product grade, e.g. 99.9 mol%), biphenyl (diphenyl), natural gas
(or fired heat from natural gas), fuel gas (refinery/plant off-gas), steam grades at 4.5,
15 and 42 bar(a) (only `steam/mp-11bara` exists).
