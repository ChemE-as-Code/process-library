# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml` and `scripts/balance.py`; the stream table is generated:
`cheme process streams --md` (provenance letter per value). Issue:
ChemE-as-Code/process-library#168.

Run record of this stage (2026-10-28): library branch `case/sodium-nitrite-1` from `9493d54`
(main at `11d50ef`); cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0; DWSIM not used. Core
state as installed: `cheme process methods` lists ENRTL-PR and PITZER-RKS as unsupported and
the electrolyte route as NaCl-H2O only (issue #168 comment on core PR #394), so the
nitrite/nitrate/carbonate liquors, nitric acid and the salts are **not covered** by any phase,
property or simulation route (`cheme process props --coverage`: every stream outside the
supported mixtures). The bounded crystalliser of core PR #395 (`crystallizer:`) is predictive
only for a single salt from water; this mother liquor holds three salts, so it would stay at
an imposed yield and is not used (D-008). The core issues themselves (#364, #365) could not be
opened from this run (not visible to `gh`); their state is taken from the issue #168 comments.

## 1. Route and boundary memo

- **Route** (issue #168 case notes): ammonia burnt with air over a Pt/Rh gauze to nitric oxide;
  the nitrous gas, partly oxidised so that NO and NO2 are about equimolar, absorbed in soda
  (Na2CO3) solution to sodium nitrite (Na2CO3 + NO + NO2 -> 2 NaNO2 + CO2), with some nitrate
  from excess NO2 (Na2CO3 + 2 NO2 -> NaNO2 + NaNO3 + CO2); the liquor evaporated, sodium nitrite
  crystallised by cooling, centrifuged and dried; the nitrate-rich mother liquor purge inverted
  with nitric acid to sodium nitrate (3 NaNO2 + 2 HNO3 -> 3 NaNO3 + 2 NO + H2O), the NO returned
  to the absorbers. Sources: SRC-2 (soda absorption, crystallisation, mother liquor), SRC-3
  (burner, WHB, alkaline absorption to nitrite liquor), SRC-4 (inversion with NO return),
  SRC-6 (production summary).
- **Absorbent: soda ash, not caustic** (D-003). Both are documented (SRC-2 soda, SRC-3 NaOH).
- **Product form**: dried technical-grade crystalline NaNO2, 99.0 wt-% (D-002). Solutions
  (e.g. 40 % liquor, SRC-3) and food/pharma grades (recrystallised) are outside this case.
- **Nitrate disposition** (issue: "define the nitrogen balance and nitrate disposition"): every
  nitrate formed leaves either in the product (0.83 wt-%, from the cake liquor) or with the
  mother-liquor purge, which is inverted completely to sodium nitrate sold as co-product (D-009).
  Rejected: drying the purge to a mixed nitrite/nitrate salt (SRC-2's graining pan, about
  55/40) - a lower-value product without a clear market today; discharging it - a nitrogen load
  to water.
- **Boundary**: gate-to-gate from liquid ammonia, air, soda ash, 60 wt-% nitric acid,
  electricity, LP steam and cooling water to dried NaNO2 and NaNO3 at the dryer outlets, tail
  gas to stack, dryer exhaust and surplus condensate. Inside: ammonia vaporiser (E-101), air
  blower (K-101), burner with integral WHB (R-101), soda dissolver (T-201), oxidation volume and
  absorption towers (C-201, lumped), double-effect evaporator (E-301), NaNO2 crystalliser and
  centrifuge (CR-301, S-301), dryer (D-301), inversion reactor (R-401), NaNO3 crystalliser and
  centrifuge (CR-401, S-401), dryer (D-401). Outside: storage, screening/anti-caking/bagging,
  ammonia storage, BFW treatment, utility generation, tail-gas abatement (open, D-006).
- **What crosses the boundary**: NH3, AIR, SODA, HNO3 (raw materials), POWER, LPS (utilities
  in), NANO2 (product), NANO3 (by-product), TAIL, DRYVENT (emissions), COND (waste water),
  CW (utility out).
- **Normalisation**: per kg of dried NaNO2 product (S18).
- **Link to other library processes** (boundary feeds, not integrated): ammonia from
  ammonia-1, soda ash from soda-ash-1, 60 wt-% nitric acid from nitric-acid-1 (its product
  state). The WHB steam stays inside (D-010). The utility processes utility-steam-ng-boiler,
  utility-cooling-tower and utility-wwtp are the natural backgrounds of LPS, CW and COND.

## 2. Source register

Read status: "read" = the cited locator was read (full text via the web page) in this run;
"summary" = facts taken from a web search summary of the page, locator not checked in full;
"metadata" = only the identity was checked. Facts are in our own words; nothing copied.

| id | source | locator | status | terms | used for |
|---|---|---|---|---|---|
| SRC-1 | Laue et al., "Nitrates and Nitrites", Ullmann's Encyclopedia, doi:10.1002/14356007.a17_265 | none | metadata (issue #168 lead) | licensed | route identity only; no number taken |
| SRC-2 | US 2 032 699 A (Hayes and Britton, Solvay Process Co., 1936), https://patents.google.com/patent/US2032699 | Description (background: NO excess favours nitrite; equal NO and NO2 is the theoretical ratio) and the example: about 9 vol-% NOx gas from ammonia oxidation; soda solution about 215 g/l in three towers countercurrently; liquor about 40:1 nitrite:nitrate; liquor to storage 25 % NaNO2, 5 % NaNO3; evaporated to about 1000 g/l at about 125 degC; vacuum crystalliser about 65 to 55 degC; mother liquor about 33 % NaNO2, 17 % NaNO3, 1.1 % Na2CO3, split 45/45/10; residue grained to about 55/40 nitrite/nitrate | read (Google Patents text) | patent: facts only | D-003, D-006, D-008 |
| SRC-3 | US 12 565 427 B2, "Apparatus and process for conversion of ammonia into oxides of nitrogen", https://patents.google.com/patent/US12565427B2/en | Detailed Description and claims: air 8 600-9 460 Nm3/h with NH3 988-1 090 Nm3/h (about 10.3 mol-% NH3); gauze 850-950 degC, 1-4 bar; Pt/Rh 95/5 gauzes; WHB cooling to 200-250 degC raising about 1.94 t/h steam; absorption in NaOH towers; liquor 38-40 % w/w; calculated 92 % conversion for six gauzes | read (Google Patents text; no paragraph numbers on the page) | patent: facts only | D-005 |
| SRC-4 | US 2 013 984 A, "Process for the oxidation of nitrites to nitrates", https://patents.google.com/patent/US2013984A/en | Description: nitrite of absorption liquors converted to nitrate with nitric acid, the nitrogen oxides set free returned to the absorption | summary | patent: facts only | D-009 |
| SRC-5 | IPCC 2006 Guidelines, Vol. 3 Ch. 3, Table 3.3, https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol3.html | N2O default for atmospheric-pressure (low-pressure) nitric acid plants: 5 kg N2O per t HNO3 (100 %) | from the library's prior use (nitric-acid-1 cites the same table) and memory; page not re-read in this run | IPCC: facts with citation | D-005 N2O analogy |
| SRC-6 | Wikipedia, "Sodium nitrite", https://en.wikipedia.org/wiki/Sodium_nitrite | section Production: NOx absorbed in NaOH or Na2CO3 solution, nitrate as by-product | not opened in this run; route identity only, the same facts are read in SRC-2/3 | CC BY-SA: facts only | route identity |
| SRC-7 | ATcT / CRC / Poling 5th ed. via `cheme chemistry thermo` | printed records in process/materials.yaml | read (tool output) | data facts | burner duty, gas enthalpies |
| SRC-8 | Wagman, D. D. et al. (1982) NBS tables of chemical thermodynamic properties, J. Phys. Chem. Ref. Data 11 Suppl. 2 | dHf (298.15 K) of NaNO2(aq) -344.8, NaNO3(aq) -447.48, Na2CO3(aq) -1157.38, Na2CO3(cr) -1130.68, HNO3(aq) -207.36 kJ/mol; dHsol NaNO2 about +13.9 kJ/mol | values as recalled by the agent, **not re-read in this run: to be verified against the tables** | US government data | D-010 absorption and crystallisation heats |
| SRC-9 | nitric-acid-1 (this library), process/design-basis.yaml | air composition, ammonia and acid delivery states | read | CC BY 4.0 (own) | D-004 |
| SRC-10 | IAPWS-IF97 | psat 313.15 K 7.385 kPa; saturation 450 kPa(a) 420.8 K | standard values | open standard | D-006, D-010 |

Searched without an open result (open inputs, section 7): an open nitrite-plant material
balance or consumption figures per tonne (Indian environmental-clearance documents found were
for whole complexes, e.g. RCF Trombay; commercial project reports are paid), a NaNO2/NaNO3
solubility table with its source, product prices, a BREF chapter on sodium nitrite.

## 3. Reaction and model evidence

| step | reactions (process/reactions.yaml) | model basis | evidence | limits |
|---|---|---|---|---|
| R101 burner | NH3_OX, NH3_N2O, NH3_N2 | conversion (specified selectivities 0.97 / 0.014 / 0.016, complete NH3 conversion); outlet and duty calculated by cheme | SRC-3 (conditions, calculated 92 % at six gauzes), SRC-5 (N2O by analogy) | selectivity ASSUMED; no gauze kinetics; Pt loss not modelled |
| C201 absorbers | NO_OX, NITRITE_ABS, NITRATE_ABS | specified outlet streams (stream values), element balance checked by cheme | SRC-2 (ratio 40:1, liquor), SRC-3 (liquor 38-40 %) | no rate-based NOx absorption model (NO oxidation kinetics, N2O3/N2O4 equilibria, mass transfer) - an executable reactive-absorption model is not in core; nitrate ratio ASSUMED 20:1 |
| E301, CR301, D301 | none | specified splits (stream values) | SRC-2 (concentrate, crystalliser temperatures, mother liquor) | no solubility model for the ternary salt system (core#364/#365) |
| R401 inversion | INVERSION, CARB_NEU | conversion 1 (specified), stream values | SRC-4 | acid excess, NO stripping air and NO oxidation not modelled |

The burner reactions are far from equilibrium in the reverse direction (`cheme process
reactors`: ln K about 250-340 at 473 K), so specifying them by conversion is consistent.

**NO/NO2 ratio control (stated)**: the nitrite reaction consumes NO and NO2 1:1 (as N2O3);
every NO2 beyond that forms nitrate. The plant therefore holds the oxidation degree
NO2/(NO+NO2) of the gas entering the absorbers near 0.5 and slightly below rather than above
(SRC-2: an NO excess favours nitrite). The handles are the residence time and temperature of the
gas between the WHB and the first tower (the oxidation volume, cooled), the secondary air
admitted there, and the NO returned from inversion. In the balance the absorbers need 21.9
kmol/h NO2 from 40.9 kmol/h NOx, i.e. an overall oxidation degree of 0.537 consistent with a
20:1 nitrite:nitrate mass ratio. Oxygen is not limiting (3.8 vol-% dry left in the tail gas).
Measurement for the control (NOx and NO2 analysers before the absorbers, liquor nitrite/nitrate
analysis) is a P&ID-stage item.

## 4. Basis table (sourced / assumed / missing)

| item | value | status |
|---|---|---|
| capacity | 2 500 kg/h dried NaNO2, 8000 h/a = 20 kt/a | ASSUMED (D-002) |
| product grade | 99.0 wt-% NaNO2 (calc. 99.02), 0.83 % NaNO3, 0.1 % moisture | ASSUMED (D-002), follows from D-008 |
| NH3 in burner feed | 10.3 mol-% | sourced SRC-3 |
| gauze conditions | 850-950 degC, about 1.3 bar(a) inlet | sourced SRC-3 (range 1-4 bar) |
| NO selectivity | 0.97 | ASSUMED (D-005) |
| N2O formation | 1.4 % of NH3 | ASSUMED by analogy to SRC-5 |
| WHB outlet | 200 degC | sourced SRC-3 (200-250 degC) |
| soda solution | 20 wt-% Na2CO3 | ASSUMED near SRC-2 (215 g/l) |
| NaNO2:NaNO3 formed | 20:1 by mass | ASSUMED (SRC-2 reports 40:1) |
| NOx absorption | 99.5 % of N | ASSUMED (D-006) |
| concentrate | about 125 degC, 57 wt-% NaNO2 | SRC-2 temperature; composition calculated |
| crystalliser | 55 degC; mother liquor 33/17/1.1 wt-% NaNO2/NaNO3/Na2CO3 | sourced SRC-2 (example) |
| cake liquid | 0.05 kg/kg crystals | ASSUMED (D-008) |
| mother liquor recycle | 1.5 kg/kg crystals (internal, no effect on the external balance) | ASSUMED (D-008) |
| inversion | complete, stoichiometric 60 wt-% HNO3 | ASSUMED (D-009), route SRC-4 |
| evaporator economy | 1.8 kg/kg (double effect) | ASSUMED (D-010) |
| dryer efficiency | 0.5 | ASSUMED (D-010) |
| electric loads other than the blower | 105 kW in total | ASSUMED (D-011) |
| tail-gas abatement | none | open (D-006) |
| Pt/Rh loss | not quantified | missing |
| product prices | none | missing (allocation, D-013) |

## 5. Method and dependency table

| need | method used | core support (0.8.0) | gate |
|---|---|---|---|
| element/mass balance | cheme validate, process streams | supported | closed |
| burner outlet and duty | conversion reactor, ideal-gas data | supported | calculated; agrees with the script (1 964.2 kW) |
| NOx absorption with chemistry | specified outlets | no reactive-absorption model | specified (balanced target) |
| electrolyte enthalpies (liquors) | NBS formation enthalpies, constant cp 2.8 kJ/kg K | unsupported (core#364: NaCl only) | duties C201, E301, CR301 are estimates; energy closure not evaluable in core |
| NaNO2 crystallisation | specified splits | `crystallizer:` (core PR #395) predictive only for one salt; multi-solute -> imposed yield | not used: would add no predictive content |
| property filling | none | `props --coverage`: no package | gated (core#364) |
| simulation | none | DWSIM refuses electrolytes with water | gated (core#364) |

## D-001 Route and boundary (2026-10-28)
Decision: ammonia oxidation, soda absorption, evaporative/cooling crystallisation, inversion of
the purge to sodium nitrate; gate-to-gate boundary as in section 1.
Reason: the issue's case notes name this route; SRC-2 and SRC-3 document it in open text.
Rejected: NOx from a nitric acid plant's tail gas or by-product gases as the source (plant
specific); reduction of sodium nitrate with lead or carbon (historic).
Assumptions: storage, bagging and utility generation outside.

## D-002 Capacity and product (2026-10-28)
Decision: 2 500 kg/h dried sodium nitrite, 8000 h/a (20 kt/a); 99.0 wt-% NaNO2 with 0.1 wt-%
moisture.
Reason: a single absorption train of the size of SRC-3's burner (about 1 t/h liquor NaNO2 per
546 kg/h NH3 there; this case uses 680 kg/h NH3); the grade is the usual technical grade,
ASSUMED - no standard cited.
Rejected: a solution product (SRC-3 sells 38-40 % liquor in places) - the issue asks for the
crystallisation and separation.

## D-003 Soda ash as absorbent (2026-10-28)
Decision: 20 wt-% Na2CO3 solution made from dense soda ash and evaporator condensate.
Reason: the case notes allow soda ash or caustic; soda ash is the classic absorbent (SRC-2),
cheaper per mol Na and made in this library (soda-ash-1). Its CO2 (0.36 kg/kg NaNO2) leaves
with the tail gas and is reported (D-013). Dissolving it in the evaporator condensate closes
the water loop (only 0.31 kg/kg condensate surplus).
Rejected: caustic soda (SRC-3) - no CO2 release, higher liquor strength (38-40 %) and less
evaporation, but the NaOH comes from chlor-alkali electrolysis with its electricity; a
scenario for the next stage.

## D-004 Feeds (2026-10-28)
Decision: liquid ammonia pure at 288.15 K, 1600 kPa(a); humid air N2 77.34, O2 20.74, Ar 0.92,
H2O 1.00 mol-% at 288.15 K; soda ash pure Na2CO3; nitric acid 60 wt-% at 313.15 K (as
nitric-acid-1, SRC-9).
Reason: consistent with the library processes that make them.
Assumptions: impurities (water/oil in NH3, NaCl in soda ash) not modelled; NaCl would
accumulate in the mother liquor and leave with the purge into the NaNO3.

## D-005 Burner and waste heat boiler (2026-10-28)
Decision: 10.3 mol-% NH3 in air (SRC-3), Pt/Rh gauze at about 1.3 bar(a); complete NH3
conversion with selectivities NO 0.97, N2O 0.014, N2 0.016 (ASSUMED); gas leaves the integral
WHB at 200 degC (SRC-3: 200-250 degC); 3 % of the heat released lost (ASSUMED).
Reason: near-atmospheric burners reach higher NO yields than pressure burners; 0.97 is an
assumption inside the usual 0.93-0.98 band (not sourced in this run; SRC-3 calculates 92 % for
its configuration, so 0.97 is optimistic - a sensitivity). The N2O share is the IPCC
atmospheric-pressure default for nitric acid plants (SRC-5, 5 kg N2O per t HNO3) carried over
per mol of product nitrogen: an analogy, the same gauze chemistry at the same pressure.
Result: R101 duty 1 964.2 kW by `cheme process reactors` (equal to scripts/balance.py); 1 887.8
kW steam (about 2.9 t/h at 1000 kPa(a)) after the loss.

## D-006 Absorption model (2026-10-28)
Decision: C201 lumps the oxidation volume and the absorption towers; specified outlets: 99.5 %
of the NOx nitrogen absorbed (ASSUMED), NaNO2:NaNO3 = 20:1 by mass in the liquor (ASSUMED,
half of SRC-2's 40:1 as a conservative value), unabsorbed NOx counted as NO, tail gas
water-saturated at 40 degC and 105 kPa(a), liquor at 40 degC.
Result: liquor 22.1 wt-% NaNO2 (SRC-2: 25 %); tail gas 670 ppmv NOx and 916 ppmv N2O (dry),
3.8 vol-% O2 dry.
Open: 670 ppmv NOx is above what a modern permit allows; a tail-gas treatment (extended
absorption, SCR with ammonia or an oxidising scrubber) must be chosen at the next stage, and
an N2O abatement catalyst in the burner would cut the dominant climate emission (D-013).

## D-007 Balance model and components (2026-10-28)
Decision: an independent mass and energy balance (scripts/balance.py, run with `cheme run
scripts/balance.py [--yaml]`) gives every stream except S5 (calculated by cheme) as
`assumed`; salts carried as neutral components without phase distinction.
Reason: no core method covers these electrolytes (section 5); a component without phase keeps
the component balances of the crystalliser and dryers exact.
Checks: overall mass in = out 13 118.55 kg/h; element balances N, H, O, Ar, Na, C closed in
the script and in every cheme step (absorber and inversion by elements over their reactions).

## D-008 Evaporation, crystallisation and drying (2026-10-28)
Decision: double-effect evaporator to about 125 degC concentrate (SRC-2), vacuum cooling
crystalliser at 55 degC with the mother liquor of SRC-2's example (33 % NaNO2, 17 % NaNO3,
1.1 % Na2CO3), centrifuge cake holding 0.05 kg mother liquor per kg crystals (ASSUMED), 1.5 kg
mother liquor per kg crystals returned to the evaporator (ASSUMED, internal), the purge sized
to remove the nitrate formed; the dryer leaves 0.1 wt-% moisture.
Result: crystals 2 435 kg/h, purge 671 kg/h, evaporation 8 996 kg/h; condensate 8 657 kg/h to
the dissolver, 338 kg/h surplus.
Rejected: core's `crystallizer:` with basis solubility - single solute only.

## D-009 Inversion and sodium nitrate (2026-10-28)
Decision: the purge's nitrite and carbonate converted completely with stoichiometric 60 wt-%
nitric acid in R-401; the NO released (64 kg/h) and CO2 return to C201 (SRC-4); the nitrate
liquor evaporated in a single-effect crystalliser, centrifuged (0.05 kg liquor of 51 wt-%
NaNO3 per kg crystals, ASSUMED) and dried to 0.1 wt-% moisture; its mother liquor is recycled
inside CR-401 without a purge (ASSUMED).
Result: 239.5 kg/h acid, 399.4 kg/h NaNO3 (0.160 kg per kg NaNO2).
Assumptions: in practice air strips the NO and part of it oxidises before the absorbers; the
small acid excess and the impurity purge of CR-401 are not modelled.

## D-010 Utilities and duties (2026-10-28)
Decision: WHB steam (about 1000 kPa(a)) feeds the first effect of E-301 (not exported); site
LP steam 450 kPa(a) for the balance of E-301, the ammonia vaporiser, the NaNO3 crystalliser and
the dryers; cooling water 25/35 degC.
Estimates (all ASSUMED): evaporator economy 1.8 kg/kg with 2 257 kJ/kg; second-effect vapour
condensed on CW; crystalliser cooling from 125 to 55 degC with cp 2.8 kJ/kg K plus the heat of
crystallisation of NaNO2 (13.9 kJ/mol, SRC-8); absorber heat = gas cooling 200 to 25 degC +
condensation (44.0 kJ/mol) + NO oxidation (57.1 kJ/mol NO2) + absorption (-50.8 and -96.4
kJ/mol from SRC-8 formation enthalpies, dilute standard state); dryers 2 500 kJ/kg water at
efficiency 0.5; ammonia latent heat about 1 180 kJ/kg.
Result: LP steam 1 837 kW (0.735 kWh/kg NaNO2), internal WHB steam 1 888 kW, CW 5 504 kW (2.20
kWh/kg).
Gated: energy closure of the liquor steps by cheme needs electrolyte enthalpies (core#364).

## D-011 Machines and electricity (2026-10-28)
Decision: air blower 101.3 to 131.3 kPa(a) at isentropic efficiency 0.75 (84.5 kW); other loads
ASSUMED: absorber circulation 30, evaporator 15, crystalliser/centrifuge 25, NaNO2 dryer 15,
inversion 5, NaNO3 crystalliser 10 and dryer 5 kW. Total 189.5 kW (0.076 kWh/kg).

## D-012 Equipment list at concept stage (2026-10-28)
Decision: one item per PFD step (two for the crystalliser-centrifuge pairs), design pressures
and temperatures as placeholders for the materials question; austenitic stainless steel for
the nitrous-gas and liquor service. No sizing, no datasheets (out of scope).

## D-013 Preliminary LCI: gate-to-gate, mass allocation, backgrounds open (2026-10-28)
Decision: lca/lca.yaml per kg dried NaNO2; every feed and utility declared `missing:` with the
background it should connect to (ammonia-1, soda-ash-1, nitric-acid-1, LP steam from a gas
boiler, cooling tower, wastewater treatment); air `free`; tail-gas CO2, N2O and NO as
elementary emissions to air (CO2 from the soda's mineral carbon reported as fossil), N2, O2,
Ar, H2O free. Sodium nitrate shares the burdens by mass (86.2 % NaNO2); economic allocation is
the better choice once prices are sourced. Exclusions: start-up/upsets, fugitive leaks,
dryer dust, Pt/Rh loss, dissolver breathing.
Result (cheme assess lca, after allocation, per kg NaNO2): NH3 0.2346 kg, soda ash 0.7465 kg,
nitric acid 60 % 0.0826 kg, electricity 0.0654 kWh, LP steam 0.634 kWh, CW 1.898 kWh,
condensate 0.267 kg, CO2 0.310 kg, N2O 4.24 g, NO 2.12 g (unallocated values are these / 0.862).
Partial screening carbon footprint of the direct emissions only: 1.47 kg CO2-eq/kg, 79 % from
N2O; every background is a gap (8 gaps), so this is not a footprint of the product. Inventory
mass and element balances closed (cheme); checked by hand against the flowsheet: inputs 4.5246
kg = outputs 1 + 3.2351 + 0.0228 + 0.2667 kg (allocated), i.e. 13 118.55 kg/h at the plant.

## 6. Core findings and gated steps
- Electrolyte thermodynamics (core#364): the duties of C201, E301, CR301, CR401 and the dryers
  are estimates; `cheme process props` and `simulate` refuse these streams; energy closure of
  those steps is not evaluable by cheme. Only the gas-phase burner duty is calculated.
- Crystallisation (core#365, PR #395): supported for a single salt; this ternary system stays at
  specified splits.
- `cheme maturity`: calculation maturity none - feed flows are design choices (not given with
  a source), absorber and crystalliser are specified stream values; this is the honest level
  of this stage.
- `cheme.lca-elementary-uncharacterised` for NO in climate change is correct (NOx has no GWP100
  in the method); the crosswalk has no NO (CAS 10102-43-9) flow identity yet.

## 7. Open inputs
- NO selectivity and N2O formation of a nitrite-plant burner (measured or licensor data).
- Nitrate ratio of the absorbers and the achievable NOx absorption; tail-gas abatement choice.
- NaNO2-NaNO3-Na2CO3-H2O solubility data (open source) to replace the example mother liquor.
- Verify the NBS formation enthalpies of SRC-8 against the published tables.
- Prices of NaNO2 and NaNO3 for economic allocation.
- Pt/Rh gauze loss rate; dryer dust emission; start-up emissions.
- Ullmann chapter (SRC-1) not read: production section, consumption figures.

## 8. Chemicals registry items missing (for the consolidated library PR)
`sodium-nitrite` (main product, CAS 7632-00-0), `sodium-nitrate` (co-product, 7631-99-4),
`ammonia` (7664-41-7), `sodium-carbonate` (soda ash, 497-19-8), `nitric-acid` (7697-37-2, with
a 60 wt-% solution grade), `nitrous-oxide` and `nitric-oxide` (emissions); in
lci/mappings.yaml a nitric-acid entry per kg of 60 wt-% solution; the elementary-flow crosswalk
lacks NO (10102-43-9) to air.
