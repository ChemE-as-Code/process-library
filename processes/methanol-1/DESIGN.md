# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml`; the stream table is generated: `cheme process streams
--md` (provenance letter per value). Issue: ChemE-as-Code/process-library#118.

Run record of this stage (2026-10-27): library branch `case/methanol-1` from `b43b479`;
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0; thermo 0.6.1, chemicals 1.5.2, scipy 1.18.1
in cheme's interpreter; DWSIM not used. Core #315 open (checked 2026-10-27): the syngas
package extension (CH3OH, CO above 500 K) and a polar / activity-coefficient benchmark are
still open; liquid-phase reactor energy closure was verified in core #393 (not used here: the
converter is vapour phase).

## 1. Route and boundary memo

- **Route**: natural gas -> synthesis gas (reforming) -> low-pressure methanol synthesis on
  Cu/ZnO/Al2O3 -> crude methanol distillation. The issue keeps the natural-gas route as the
  priority; CO2/H2 e-methanol is a separate variant with another upstream (not here).
- **Boundary of this case** (the first bounded job of the handoff in #118): from the make-up
  synthesis gas at the battery limit to Grade AA methanol to storage. Inside: make-up
  compression, synthesis loop (circulator, feed/effluent exchanger, converter, cooler, HP
  separator, purge), let-down and LP flash, topping column, refining column. Outside: natural
  gas treatment, reforming, reformer gas cooling and condensate removal (they make the
  boundary feed), hydrogen recovery from the purge, fuel and steam systems, storage, wastewater
  treatment.
- **What crosses the boundary** (flowsheet terminals): SYNGAS (raw material), MEOH (product),
  PURGE and FUELGAS (off-gases to fuel), WW (wastewater), and the utilities POWER, LPS, MPS
  (steam raised in the converter) and CW.
- **Comparisons**: only with cases of the same boundary (no reforming, no storage), the same
  carbon source and the same purification; IRENA cost outlooks are not comparable with this
  boundary.

## 2. Decisions

## D-001 Boundary: synthesis loop and purification, reforming outside (2026-10-27)
Decision: model the loop and purification only; the make-up synthesis gas is a boundary feed.
Reason: the #118 handoff asks to isolate synthesis and purification before adding the front end;
the reformer's design (steam-to-carbon, oxygen, pressure) sets the make-up gas but needs its
own evidence.
Rejected: a whole natural-gas-to-methanol plant at this stage (reforming would dominate the
uncertainty and the energy balance).
Assumptions: the reformer delivers a dry gas at the battery limit (D-004).

## D-002 Capacity and product grade (2026-10-27)
Decision: 2500 t/d of product stream (104,167 kg/h), US Federal Specification O-M-232 Grade
AA methanol (methanol at least 99.85 wt%, water at most 0.10 wt%), 8400 h/a.
Reason: a single-train world-scale size gives a normalised basis for later literature
reconciliation; Grade AA is the usual chemical grade. ASSUMED: the capacity is a study choice,
not an owner figure; it scales every flow linearly (the loop is solved per unit of make-up gas).
Rejected: fuel-grade methanol (would allow a single column; the product use is not decided).
Assumptions: the O-M-232 limits above are quoted from the specification as generally cited;
the current revision has not been read in this run (open input I-07). Only methanol and water
are modelled: the other Grade AA limits (acetone, ethanol, acidity, permanganate time,
distillation range) cannot be checked without by-products (D-005).

## D-003 Converter type and loop conditions (2026-10-27)
Decision: boiling-water, steam-raising tubular converter (catalyst in the tubes), feed 498.15 K
and 8100 kPa(a), outlet 528.15 K and 7900 kPa(a), shell raising MP steam at 2800 kPa(a)
(saturation 503.4 K, 25 K below the outlet). Circulator 7500 -> 8150 kPa(a); feed/effluent
exchanger, loop cooler and HP separator at 7500 kPa(a). Pressure drops ASSUMED (50 kPa per
exchanger side, 200 kPa converter, 300 kPa cooler and separator).
Reason: a near-isothermal converter keeps the copper catalyst inside its window (cheme's
CU_ZNO window 473-573 K, 5000-10000 kPa(a), itself ASSUMED from the library entry) and
recovers the reaction heat as steam. All values ASSUMED, within the typical low-pressure range
the cheme library entry gives (493-553 K, 5000-10000 kPa(a)).
Rejected: adiabatic quench or multi-bed converters (more catalyst models and intercoolers for
a concept balance); higher pressure (more compression, not needed for an equilibrium model).

## D-004 Make-up synthesis gas (2026-10-27)
Decision: dry gas, H2 68.0, CO 21.5, CO2 7.5, CH4 2.5, N2 0.5 mol%, at 2600 kPa(a) and
313.15 K. Stoichiometric number SN = (H2 - CO2)/(CO + CO2) = 2.09.
Reason: methanol synthesis wants SN slightly above 2 (a well-known target for combined or
two-step reforming; the Ullmann's article is the reference to extract it from, I-01). The
composition is ASSUMED, not taken from a source: it is the main open input (I-01) and keeps
cheme maturity below `sourced`. Sulphur, chlorides and carbonyls (copper catalyst poisons)
must be below the catalyst vendor's limits (I-03); they are not components of the model.
Rejected: steam-reforming gas (SN near 3: a large hydrogen excess and purge, a different
upstream).

## D-005 Reaction set and converter model basis (2026-10-27)
Decision: reactions MEOH_CO (CO + 2 H2 = CH3OH), MEOH_CO2 (CO2 + 3 H2 = CH3OH + H2O) and WGS
(CO + H2O = CO2 + H2) from `cheme chemistry library methanol`; the converter names the two
independent ones (MEOH_CO, WGS; MEOH_CO2 is their sum, so it is at equilibrium too) and is
solved by cheme as `reactor: equilibrium`, `fugacity: peng_robinson` (no interaction
parameters), `approach: 10` K (K taken at 538.15 K). No by-products.
Reason: the #118 handoff accepts a sourced equilibrium/conversion model at this stage and asks
not to choose a catalyst or kinetic law before review. The equilibrium constants come from the
components' formation data (ATcT formation enthalpies, CRC entropies, Poling / thermo heat
capacities, through the `chemicals` package), not from a fitted methanol-specific correlation.
The 10 K approach is ASSUMED: it stands for an unknown kinetic distance from equilibrium and is
not predicted. Sensitivity (`cheme run scripts/loop_balance.py 0` and `... 20`, recycle ratio
held at 4): approach 0 / 10 / 20 K gives per-pass CO conversion 71 / 63 / 54 %, make-up gas
130.3 / 131.5 / 133.3 t/h and make-up carbon to product 96.6 / 95.7 / 94.5 %, with duties
within 1 %. In a recycle loop the approach therefore moves the per-pass conversion, the
inerts level and the purge loss much more than the plant-level balance; it matters for
catalyst volume (not sized here).
Rejected: a conversion reactor (conversions would be invented); a PFR with Vanden Bussche and
Froment (1996) kinetics (rate basis, units and fit range not audited yet; Slotboom et al. 2020
warn that kinetic models and parameters may not be mixed).
Assumptions: by-products (dimethyl ether, ethanol and higher alcohols, methyl formate,
ketones) are left out until sourced selectivities exist (I-04); the crude therefore contains
methanol, water and dissolved gases only.

## D-006 Balance method: independent script, cheme checks (2026-10-27)
Decision: solve the recycle loop and the purification in `scripts/loop_balance.py` (thermo
0.6.1, Peng-Robinson with ChemSep kij for flashes and enthalpies; the converter with the same
equilibrium model as cheme) and enter its outlet values of the separators, columns and the
duties in `process/flowsheet.yaml` as `assumed`, with the script as source. cheme calculates
the converter outlet itself and propagates every pass-through, mixer and splitter stream.
Reason: core cannot yet qualify the property regime: `cheme process props --coverage` covers
only the make-up gas S1/S2 (syngas-pr-vapor excludes methanol and water, and CO2/H2 at 313 K
and 7500 kPa(a)); DWSIM PR is benchmarked for N2/O2/Ar only and the activity-coefficient
benchmark (core #399) covers ethanol-water bubble points only. So `process simulate` would not
be qualified (core #315), and `props --fill` refuses every loop stream.
Check: cheme's equilibrium converter reproduces the script's extents (MEOH_CO 3267.50 vs
3267.51 kmol/h, WGS -783.394 vs -783.397 kmol/h) and `ln(Q/K)` is about -2e-6 at the outlet;
every block and step balance closes (mass, components, elements). The converter duty differs:
cheme 63.9 MW on the ideal-gas formation basis, the script 65.7 MW with Peng-Robinson
departures (2.8 %); Q4 carries the script's value, the difference is the real-gas departure.
Rejected: typing stream values without a calculation; widening a property package's range.

## D-007 Recycle ratio and purge (2026-10-27)
Decision: recycle ratio 4.0 (recycle / make-up, molar), giving a purge of 2.18 % of the HP
separator gas (SPL `split`), 10.6 t/h.
Reason: ASSUMED typical loop design; with the D-004 gas it gives 63 % CO conversion per pass
and 96.0 % of the make-up carbon in the crude (95.7 % in the product). Inerts build up to
21 % CH4 and 4 % N2 at the converter inlet: high; a lower recycle ratio with more purge, or a
purge-gas hydrogen recovery, is a basic-engineering trade-off (I-08).
Rejected: hydrogen recovery from the purge (outside the boundary, D-001).

## D-008 Crude separation and purification (2026-10-27)
Decision: HP separator 313.15 K / 7500 kPa(a); isenthalpic let-down to an LP flash drum at
600 kPa(a); topping column (top 150 kPa(a), off-gas at 313.15 K with all dissolved gases and
methanol at its vapour pressure, 33.9 kPa; bottom 200 kPa(a)); refining column (top 110 kPa(a),
bottom 200 kPa(a)) with distillate water 0.05 wt% (margin below Grade AA) and bottoms
100 ppm(wt) methanol; product subcooled to 313.15 K, 300 kPa(a). Reflux ASSUMED: topping 0.3
kmol per kmol feed, refining reflux ratio 1.5; reboiler duties from each column's energy
balance with the Peng-Robinson enthalpies. All ASSUMED.
Reason: the classic two-column purification for Grade AA. Stage numbers, feed stages and the
minimum reflux are not calculated (no qualified methanol-water VLE, D-006).
Rejected: a three-column (pressure-staged) refining train (saves steam; a basic-engineering
option once the duties are qualified); a single column (fuel grade only).
Open: a fusel-oil side draw of the refining column (needs by-products, I-04); a pump between
the columns (CM-117) and the LP flash relief case (gas blow-by from V-101).

## D-009 Utilities (2026-10-27)
Decision: cooling water 298.15/308.15 K (min approach 5 K), LP steam 450 kPa(a) for the
reboilers, MP steam 2800 kPa(a) raised in the converter, electric drives; all ASSUMED, no site
chosen. The loop cooler is a cooling-water cooler in the PFD; an air cooler with a trim cooler
is the usual alternative.
Note: the reboilers take 106 MW of LP steam against 66 MW of MP steam raised: without the
reformer's waste heat (outside the boundary) the purification is a net steam importer.

## D-010 Compression (2026-10-27)
Decision: make-up compressor K-101 2600 -> 7550 kPa(a) in one casing in the PFD, recycle
circulator K-102 separate, isentropic efficiency 0.75 (ASSUMED) for both. K-101 discharges at
456 K: intercooling and the casing count are a basic-engineering choice.

## D-011 First-pass line sizes (2026-10-27)
Decision: DN in `piping/line-list.yaml` from velocity (ASSUMED limits: gas 15 m/s above
1000 kPa(a), 20 m/s below, two-phase 10 m/s, liquid 1.5 m/s) on the script's Peng-Robinson bulk
densities, inside diameter taken equal to DN. PR underestimates the methanol-water liquid
density (about 670-690 against roughly 790 kg/m3 for methanol near 313 K), so the liquid lines
are on the large side.

## D-012 Equipment design conditions (2026-10-27)
Decision: design pressure = highest operating pressure + 10 % (at least + 2 bar), one value for
the HP loop (89 barg); design temperature = highest operating temperature + 25 K. ASSUMED
concept values; relief and materials (hydrogen service) at basic engineering.

## D-013 DWSIM simulation inputs: scope, specs and property package (2026-10-30)
Decision: `process/simulation.yaml` declares the whole flowsheet for `cheme process simulate`
(nothing excluded), with Peng-Robinson (PR) as the one property package and the recorded method
selection. Not run: no DWSIM or Docker was available on the machine this was written on, so
no stream value comes from it and `process/simulation-run.json` does not exist. The flowsheet's
values stay those of D-006 (script and propagate).
- Specs repeat D-003, D-008, D-009 and D-010 (all ASSUMED): K-101 to 7550 kPa(a), K-102 to
  8150 kPa(a), both isentropic 0.75 (shaft power: no motor efficiency is stated, so no
  `drive_efficiency`); E-101 and E-103 to 313.15 K; E-102 cold outlet 498.15 K; pressure drops
  as the D-003 stream pressures give them; V-101 adiabatic at its inlet; the purge split on
  SPL (D-007).
- Converter R-101: DWSIM's equilibrium reactor (MEOH_CO and WGS, 10 K approach of D-005) at the
  outlet temperature 528.15 K, duty = heat to MP steam (Q4). It is a cooled reactor, so the
  adiabatic mode that fails in DWSIM 9.0.5 (core #58, open) is not used; it must not be
  switched to adiabatic until that is fixed. `reactions.yaml` gives no equilibrium constant,
  so DWSIM takes ln K from its own formation data and its S7 can differ from cheme's (formation
  data of `materials.yaml`, PR fugacity, D-006): that difference is the check.
- LP flash V-102: no valve step precedes it, and a DWSIM vessel given only a pressure keeps its
  inlet temperature (found in ammonia-1). It is therefore run at 600 kPa(a) and the script's
  isenthalpic let-down temperature 315.10 K; its duty, about 0 if both agree, is the check.
  Adding a let-down valve step to the flowsheet is the cleaner alternative (it changes the PFD;
  left for review).
- Topping column C-201: a Fenske-Underwood-Gilliland shortcut with a partial condenser (the
  off-gas is its vapour distillate), keys CO2 / CH3OH, methanol in the off-gas 0.2257 (script
  S16), reflux ratio L/D = 36.09 (D-008's 0.3 kmol reflux per kmol feed: 1219.8 kmol/h against
  33.80 kmol/h of off-gas), 150 / 200 kPa(a). The light key in the bottoms, 1e-6, is ASSUMED:
  D-008 sends all dissolved gas overhead, and the shortcut needs a value above zero. A shortcut
  with non-condensable light components is a stretch of the Underwood method; if it does not
  converge, the next step is a rigorous column, not new numbers.
- Refining column C-202: shortcut, keys CH3OH / H2O at D-008's product and bottoms purities
  as mole fractions (0.00088895 water in the distillate, 0.00005623 methanol in the bottoms),
  reflux ratio 1.5, total condenser, 110 / 200 kPa(a). The shortcut's minimum reflux and stage
  count are the first numbers of a rigorous column; a reflux ratio below its minimum would not
  converge and means D-008's 1.5 is too low.
- Tears: S12 (recycle) and S6 (feed/effluent exchanger loop: the converter feed is E-102's
  cold outlet, the converter effluent its hot inlet), guesses from the flowsheet's values.
Property package: one per simulation (the schema takes no package per unit), so the loop sets
it. Facts (recorded in `simulation.yaml`): 81.5 bar(a) at the circulator discharge, polar
(methanol, water), no electrolytes, no pseudocomponents, interaction parameters not available
(uncertain; the conservative answer), no liquid-liquid split, no vapour association. The
selection recommends PSRK or PR / RKS with modified Huron-Vidal mixing rules; the DWSIM route
runs none of them. methods.yml names PR as the executable substitute for PR-MHV2 (it loses the
polar mixing rule) and RKS for PSRK and RKS-MHV2; PR is chosen to match the balance script
(D-006): recorded as `method_selection.substitution` (`sim-method-substituted`, info).
For the columns alone the same facts at 2 bar(a) recommend NRTL when interaction parameters
are known (UNIFAC otherwise, which the DWSIM route does not run). NRTL with an ideal-gas vapour
cannot carry the loop's supercritical H2, CO, CO2, CH4 and N2, so it is not used for the
whole flowsheet. Neither package is qualified for this mixture: core's methods.yml
benchmarks DWSIM's PR for nitrogen, oxygen and argon only, and DWSIM's NRTL for ethanol-water
bubble points at 101.3 kPa only, not methanol-water. A run will therefore fail
`predictive.property-regime` until core qualifies a package for syngas with methanol and
water (I-06).
Expected deviations once it runs (to be read, not silenced): S18 leaves the shortcut column at
its bubble point at 110 kPa(a), while the flowsheet's S18 is the subcooled, pumped product at
313.15 K and 300 kPa(a) (no product cooler or pump step), and Q9 includes that subcooling; S16's
313.15 K against the partial condenser's dew point; the flash splits S10/S13 and S14/S15 and
the column duties, where DWSIM's PR kij differ from the ChemSep kij of the script; S7 and Q4
(formation data and real-gas reactor duty, D-006).
Reason: the simulation is the independent check of the script's separator, column and duty
values that D-006 asks for, and the specs are the existing decisions, so it adds no new design
choice except the column representation and the 1e-6 above.
Rejected: NRTL for the whole flowsheet (above); excluding the columns to simulate them later
with NRTL (simulate takes one package per process, so a column-only NRTL run needs a separate
setup or a core change); rigorous columns now (no stage numbers or feed stages exist yet, D-008).
Note for review: with this file present `cheme maturity` (cheme 1.1.0 and 1.2.1, the library CI
pin since #282) passes `balanced.model-basis` and `predictive.model-basis` and lists V-101,
V-102, C-201 and C-202 as predictive, although nothing has been simulated; the
`predictive.run-record` and later checks stay missing. The calculation maturity stays none (S1
is ASSUMED, `sourced.boundary`). V-102's 315.10 K is the script's value, not a prediction.
Accepted for this draft only: the model-basis credit from the declaration alone is a core
question (it should need a run record) and is not settled here; the PR stays draft until a run
exists or that is decided. The let-down valve step ahead of V-102 (ammonia-1 D-026) remains the
cleaner fix and is left for review because it changes the PFD.

## 3. Reaction and model evidence

| item | basis in this case | source and status | consistency check |
|---|---|---|---|
| CO hydrogenation, CO + 2 H2 = CH3OH | stoichiometry; K from formation data | `chemicals` (ATcT dHf, CRC S298, heat capacities), via cheme library; given | dHr(298 K) -90.6 kJ/mol in reactions.yaml agrees with the formation data (no `process-heat-of-reaction` warning); dHr(538 K) -98.2 kJ/mol (`cheme process reactors`) |
| CO2 hydrogenation, CO2 + 3 H2 = CH3OH + H2O | sum of the other two | as above | at equilibrium whenever MEOH_CO and WGS are |
| Water-gas shift, CO + H2O = CO2 + H2 | stoichiometry; K from formation data | as above | extent -783 kmol/h (reverse shift: the loop makes water from CO2); dHr(538 K) -39.5 kJ/mol |
| Converter outlet | equilibrium at T_out + 10 K, PR fugacity, kij 0 | model basis ASSUMED (approach), cheme calculated | script and cheme extents agree within 1e-5; ln(Q/K) ~ -2e-6 |
| Equilibrium constants vs a methanol-specific correlation | not compared | Graaf et al. (1986) is the usual reference; not read in this run (I-05) | open |
| Kinetics | none | Vanden Bussche and Froment (1996): citation verified in #118, equations, units and fit range not audited; Slotboom et al. (2020): model/parameter mixing caveat | not used; reactor size not calculated |
| By-products | none | no sourced selectivity | open (I-04) |
| Catalyst window | 473-573 K, 5000-10000 kPa(a) | cheme library, ASSUMED typical range | the converter streams lie inside it |

Still required before a reactor can be sized: a rate law with its rate basis (per kg or per m3
of catalyst), pressure units, fugacity convention, temperature and pressure range of the fit,
the catalyst it was measured on and the equilibrium constants it was fitted with; the
catalyst's bulk density, particle size and activity profile (vendor); and for the phase
equilibrium, a benchmarked package for methanol-water with dissolved H2, CO, CO2, CH4, N2 at
up to 8 MPa, and methanol-water VLE at 100-200 kPa for the columns.

## 4. Source register

| source | locator | read status | reuse terms | used for |
|---|---|---|---|---|
| Ott, J. et al. (2012) Methanol, Ullmann's Encyclopedia of Industrial Chemistry, doi:10.1002/14356007.a16_465.pub3 | sections on production and purification | not read in this run (subscription); #118 checked identity and contents | cite only | route description, SN target, two-column purification (to be confirmed with locators, I-01) |
| cheme reaction library, entry `methanol` | `cheme chemistry library methanol` (cheme-as-code 0.8.0) | read | MIT (core) | reactions, catalyst window (ASSUMED), components |
| `chemicals` 1.5.2 / `thermo` 0.6.1 (C. Bell et al.) | ATcT and CRC data, Poling heat capacities, ChemSep PR kij | used | MIT | formation data, critical constants, PR flashes and enthalpies |
| US Federal Specification O-M-232, Methanol, Grade AA | Grade AA requirements | not read in this run | US government specification | product limits (to be verified, I-07) |
| Vanden Bussche, K.M.; Froment, G.F. (1996) J. Catal. 161, 1-10, doi:10.1006/jcat.1996.0156 | whole paper | citation verified in #118, content not audited | cite only | not used (candidate kinetics) |
| Slotboom, Y. et al. (2020) Chem. Eng. J. 389, 124181, doi:10.1016/j.cej.2020.124181 | abstract | abstract reviewed in #118 | cite only | guardrail on kinetic models |
| IRENA and Methanol Institute (2021) Innovation Outlook: Renewable Methanol | chapters 2-3 | inspected in #118 | cite only | not used (other boundaries) |
| Graaf, G.H. et al. (1986) Chemical equilibria in methanol synthesis, Chem. Eng. Sci. 41 (bibliographic details to be verified) | equilibrium constants | not read | cite only | candidate check of the formation-data K (I-05) |

No table, figure or text of these sources is reproduced here.

## 5. Methods and core dependencies

| step | method | status |
|---|---|---|
| Mass, component and element balances | cheme validate / process streams | done, all closed |
| Pass-through, mixer, splitter streams | cheme process propagate --fill | done (calculated) |
| Converter outlet | cheme equilibrium reactor, PR fugacity | done (calculated); model basis equilibrium + ASSUMED approach |
| Converter duty | cheme process reactors (formation basis, ideal gas) | done: 63.9 MW; script 65.7 MW (real gas) |
| HP/LP flash, column splits, exchanger and compressor duties | scripts/loop_balance.py (PR, thermo) | done, values ASSUMED; **gated**: no qualified package (core #315) |
| Stream enthalpies, block energy closure | cheme process props --fill / process energy | **gated**: props refuses S3-S19 (CH3OH outside syngas-pr-vapor; S3 outside its CO2/H2 box) |
| Predictive simulation (DWSIM) | cheme process simulate | inputs written (`process/simulation.yaml`, D-013), translation checked with `--check` up to `sim-unavailable`; **not run** (no DWSIM here) and not qualified: no benchmarked package for this mixture (core #315, #399 covers ethanol-water bubble points only) |
| Column stages and reflux | shortcut (DWSIM, D-013), then rigorous | shortcut specs written, not run; needs qualified methanol-water VLE |
| Converter sizing | PFR with a rate law | not done: kinetics input missing (process input, not a core gap) |

`cheme maturity` reports level none: `sourced.boundary` fails because the make-up gas (S1) is
ASSUMED, and `balanced.model-basis` fails because V-101, V-102, C-201 and C-202 are specified
values (assumed, from the script). Both are honest: the first needs a sourced or owner-given
feed (I-01, I-02), the second a qualified separation model or sourced split values.

## 6. Open inputs

- I-01 Make-up gas composition and state from a source with a locator (reformer design or an
  open reference), and the SN target from Ott et al. (2012) with its locator.
- I-02 Capacity and product grade confirmed by the owner (D-002).
- I-03 Catalyst: vendor window, poison limits, activity / end-of-run approach to equilibrium.
- I-04 By-product selectivities (DME, ethanol, higher alcohols, methyl formate, ketones) for the
  Grade AA impurity limits and a fusel-oil draw.
- I-05 Check the formation-data equilibrium constants against Graaf et al. (1986).
- I-06 A qualified property method for methanol-water-syngas (core #315) to replace D-006's
  script values and close the energy balances.
- I-07 Read the current O-M-232 Grade AA limits.
- I-08 Recycle ratio / purge / inerts trade-off and purge hydrogen recovery.
