# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml` and `lca/lca.yaml`; the stream table is generated:
`cheme process streams --md` (provenance letter per value). Issue:
ChemE-as-Code/process-library#86.

Run record of this stage (2026-10-27): library branch `case/ammonia-1` from `79a7cd4`;
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0; chemicals, thermo and scipy in cheme's
interpreter; DWSIM not used. Core #315 (process-library readiness follow-ups) is open
(checked 2026-10-27): no property package covers hot syngas with CO above 500 K or CH4 above
625 K, NH3 in a mixture, liquid NH3 or water, so separators and duties stay specified values
here (D-006).

## 1. Route and boundary memo

- **Route** (issue #86 brief): natural gas -> hydrodesulfurisation -> adiabatic prereformer ->
  fired primary reformer -> air-blown secondary reformer (process air brings the nitrogen) ->
  HT and LT shift -> CO2 removal (activated MDEA, CO2 vented) -> methanation -> drying ->
  synthesis gas compression -> Haber-Bosch loop (three-bed converter, waste heat boiler,
  feed/effluent and cold exchangers, water cooler, ammonia chiller, separator, purge) ->
  let-down and product flash to refrigerated liquid NH3. Purge, let-down gas and the
  refrigeration inert vent go to an NH3 wash and a cryogenic hydrogen recovery unit; the
  recovered hydrogen returns to the synthesis gas compressor, the tail gas fuels the reformer.
  No separate ASU (the secondary reformer's air supplies the nitrogen), no urea, no CCS.
- **Boundary** (full conventional plant, the first of the two scopes the handoff names):
  natural gas, air and demineralised water in; refrigerated liquid NH3, vented process CO2,
  flue gas, exported MP steam and boiler blowdown out; electricity in, heat to cooling water
  out. Inside: the furnace and its convection section, the steam system and the ammonia
  refrigeration. Outside: storage and loading, cooling tower, water treatment, wastewater
  treatment, flare, power generation.
- **Feed and fuel kept apart**: SPL101 splits the natural gas into process feed (S3,
  29.5 t/h) and furnace fuel (S2, 8.2 t/h); the HRU tail gas (S59) is the only other fuel.
  Recovered heat is counted once: radiant heat to the tubes (Q9), convection coils (Q3-Q7),
  the rest of the convection heat to steam (Q8); waste heat boilers (Q10, Q13, Q23) feed the
  steam system, which supplies process steam and exports the surplus (S68).
- **The other scope** (synthesis loop with sourced front-end blocks) was not built: the full
  plant tests the feed/fuel/steam accounting the issue asks for; the loop alone would leave
  the LCI without its dominant flows.
- **Comparisons**: no benchmark values were looked up or used. The literature named in the
  issue is design-visible; none of its numbers is in this design (section 5).

## 2. Decisions

## D-001 Scope and boundary (2026-10-27)
Decision: full conventional natural-gas plant as in section 1; process CO2 vented.
Reason: the #86 brief (Rotterdam-area, 1500 t/d, SMR + air-fed secondary reformer, no CCS,
urea, storage or loading) and the run scope (design basis to a balanced PFD and a gate-to-gate
LCI). Rejected: loop-only scope (section 1); a nitrogen ASU (the air-fed reformer makes it
unnecessary). Assumptions: storage and loading excluded, product refrigeration included.

## D-002 Capacity, product and hours (2026-10-27)
Decision: 1500 t/d contained NH3 (62,500 kg/h on-stream); product NH3 >= 99.5 wt% as
refrigerated liquid at 240.15 K and 110 kPa(a); 8000 h/a declared separately (ASSUMED).
Reason: the issue's proposed brief; 110 kPa(a) is chosen so that 240 K is a subcooled liquid
(pure NH3 boils at about 241.6 K at 110 kPa(a), thermo vapour pressure), which settles the
issue's request for a phase-consistent delivery state. Assumptions: the brief is a proposal,
not a frozen basis (open input I-02).

## D-003 Design case only (2026-10-27)
Decision: one steady design case. Turndown, winter/summer and catalyst end-of-run cases are
not modelled. Reason: concept stage, fixed budget.

## D-004 Feed, air and sulfur (2026-10-27)
Decision: an ASSUMED benchmark lean natural gas (CH4 91.0, C2H6 4.0, C3H8 1.0, CO2 1.0, N2
3.0 mol%), 4500 kPa(a), 288.15 K; dry air (N2 78.080, O2 20.946, Ar 0.934, CO2 0.040 mol%);
sulfur a trace removed by hydrogenation and ZnO and not balanced.
Reason: the issue asks for a complete, sourced feed; none could be retrieved in this run (the
ISO 12213-2 example gases are in a paid standard). The benchmark gas is a placeholder chosen
to exercise C2+ reforming and N2/CO2 inerts; it is **not** Rotterdam pipeline gas and not
sourced. This is the main reason `cheme maturity` reaches no level (open input I-01).
Rejected: pure methane (the issue forbids the silent substitution). Assumptions: no H2
recycle to the hydrogenation (small, I-05); air humidity neglected.

## D-005 Reactor model basis (2026-10-27)
Decision: no kinetics. Equilibrium reactors from cheme's reaction library (stoichiometry
`steam_reforming`, `ht_shift`, `lt_shift`, `ammonia`; ideal-gas formation data of
materials.yaml): primary and secondary reformer (SMR + WGS, approach -10 K, i.e. K 10 K
colder: less methane conversion), HT and LT shift (WGS, approach +10 K: less CO conversion),
converter (NH3, approach +15 K, Peng-Robinson fugacity without kij). Complete-conversion
reactors where equilibrium lies fully on the product side at the conditions used:
prereformer (C2H6, C3H8), secondary burner zone (all O2 burns H2; the bed re-equilibrates, so
the choice of fuel does not change the outlet), methanator (CO, CO2 to CH4), furnace
(complete combustion). `cheme process reactors` confirms ln(Q/K) of about 0 for every
equilibrium step and large positive ln K for the complete conversions (ln K 15.2 and 11.8 for
CO and CO2 methanation at 589 K).
Reason: sourced kinetics and catalyst data were not gathered (no
`process/reaction-evidence.yaml` yet); equilibrium with an approach is the usual concept basis
and is labelled as such. The approaches are ASSUMED, not sourced (I-04).
Rejected: invented rate laws or vendor catalyst volumes.

## D-006 Balance method and where the numbers come from (2026-10-27)
Decision: `scripts/plant_balance.py` (run with `cheme run`) solves the whole plant per 1000
kmol/h process gas and scales to 1500 t/d: cheme's own `equilibrate` / `equilibrate_real` and
`IdealGas` functions for reactors and enthalpies (so cheme reproduces its reactor outlets), a
thermo Peng-Robinson flash with ChemSep kij for the loop separator, let-down and loop cold-end
duties, water knock-out at IAPWS-95 saturation with insoluble gases, ideal-gas compressors,
IAPWS-IF97 steam. One fsolve closes the loop recycle, the HRU hydrogen recycle, H2/N2 = 3.0 at
the converter inlet (process air) and the inert level (purge fraction). In the flowsheet the
reactor outlets, mixers, splitters and pass-through steps are `calculated` by cheme; separator,
CO2 removal, HRU, steam system and two-stream exchanger outlets and every duty are ASSUMED with
the script as source.
Reason: core #315: no property package covers these streams, so cheme cannot calculate
flashes or duties here. The methods in the script are not qualified by ChemE-as-Code (PR for
NH3-H2-N2-CH4-Ar at 263 K / 147 bar is a screening method).
Checks: every block and step balance closes (mass, components, elements); `cheme process
reactors` gives the R-101 duty as 68,388 kW (script 68,386 kW) and |duty| < 2 kW for the
adiabatic reactors, i.e. the script's adiabatic temperatures agree with cheme's enthalpies.
Known limits: the secondary reformer burner zone (S16, 1561 K) is above the 1500 K range of the
fitted heat capacities; molar masses of materials.yaml are not exactly atom-consistent (NH3
17.031 vs 17.030), which leaves 2.4 kg/h across the converter (within tolerance). The
block-level reaction extents that `cheme process streams` prints for REF (e.g. CH4_COMB 0
although H101 burns 495.9 kmol/h) are not the sums of the step extents: the reaction set
(reforming, shift, H2 oxidation, combustion) is linearly dependent, so block extents are not
unique. Read the step extents; the balances are unaffected (review 2026-10-27-pfd-lci-review#5,
to be reported to cheme-as-code core).

## D-007 Reforming conditions (2026-10-27)
Decision: steam to (hydrocarbon) carbon 3.0; NG preheat 643 K before the desulfuriser;
mixed feed 773 K to the prereformer, reheat to 893 K; primary reformer outlet 1083 K,
3500 kPa(a); process air compressed to 3600 kPa(a) in four intercooled stages and preheated
to 773 K; secondary reformer adiabatic (outlet 1265 K, CH4 slip 0.26 mol% wet); air flow set
by H2/N2 = 3.0 at the converter inlet. Pressure drops ASSUMED (50-600 kPa per item).
Reason: usual concept values (the skill tech-petchem-ammonia-and-urea quotes about 40-42 bar
and 800-850 degC primary reformer outlet; 810 degC at 35 bar is chosen); ASSUMED, not
optimised. Rejected: a heat-exchange reformer (not the brief).

## D-008 Shift (2026-10-27)
Decision: HTS inlet 643 K (outlet 717 K), LTS inlet 478 K (outlet 508 K, CO 0.28 mol% wet),
both adiabatic equilibrium with approach 10 K. Assumptions: catalysts Fe-Cr (HTS) and Cu-Zn
(LTS) are usual choices, not selected with a vendor; by-product methanol from the LTS not
modelled (I-07).

## D-009 CO2 removal (2026-10-27)
Decision: activated MDEA absorber/regenerator modelled as a specified separator: 500 ppmv CO2
in the treated gas; CO2 product water-saturated at 313 K and 150 kPa(a), co-absorbed H2/N2/CH4
neglected; make-up water to close the water balance; regeneration heat 1.0 MJ/kg CO2 supplied
entirely by the process-gas reboiler E-202 (the LTS effluent; its outlet temperature, 424 K,
follows from that duty); solvent pumping 21 kWh/t CO2 (18 m3 solvent per t CO2 at 31 bar and
pump efficiency 0.75, both ASSUMED); all regeneration heat and pump work rejected to cooling
water. Reason: no solvent model in core; the specific heat and slip are ASSUMED values to be
replaced by a licensor or a rigorous model (I-06). Rejected: hot potassium carbonate (either is
usual; aMDEA chosen for the lower regeneration heat it is generally credited with, unsourced).

## D-010 Methanation and drying (2026-10-27)
Decision: methanator feed heated to 553 K by heat from E-201 (energy stream Q14); complete
methanation (outlet 589 K); cooling to 313 K, knock-out, and a molecular sieve dryer removing
all water before the loop, so that the product is anhydrous and the make-up can join the loop
ahead of the converter. Regeneration of the dryer not modelled (I-05).

## D-011 Synthesis loop (2026-10-27)
Decision: make-up compressed to 14,600 kPa(a) (three intercooled stages) and mixed with the
recycle ahead of the circulator (to 15,500 kPa(a)); converter inlet 503 K (overall adiabatic),
outlet 703 K at 15,100 kPa(a), equilibrium approach 15 K with Peng-Robinson fugacity (NH3 3.4
-> 17.8 mol%); waste heat boiler E-502 to 547 K; feed/effluent exchanger E-501 hot outlet 343 K
(above the NH3 dew point, about 334 K); water cooler to 313 K; cold exchanger E-505 (recycle gas
263 -> 303 K); chiller to 263 K; separator at 14,700 kPa(a); purge fraction 0.737 % of the
separator gas for 12 mol% inerts (CH4 + Ar) at the converter inlet; recycle/make-up 2.9 molar.
Reason: a mid-range pressure for magnetite catalyst (the skill and cheme's library window
10-35 MPa); E-505 recovers cold from the recycle gas and cut the chiller duty by about a
quarter in the first iteration; ASSUMED, not optimised (inerts, pressure, chiller
temperature trade compressor, refrigeration and purge losses).

## D-012 Cooling water and coolers (2026-10-27)
Decision: cooling water 298/308 K, process coolers to 313 K, minimum approach 5 K; air coolers
not considered. ASSUMED.

## D-013 Purge gas recovery (2026-10-27)
Decision: purge, let-down gas and refrigeration vent to one HRU package: NH3 wash with
distillation recovering 99 % of the NH3 as anhydrous liquid (chilled to product temperature;
LP steam 3 MJ/kg recovered NH3), cryogenic separation recovering 90 % H2, 25 % N2, 15 % Ar,
5 % CH4 to the H2-rich gas returned to the synthesis gas compressor suction; tail gas to fuel.
All recoveries and the steam figure ASSUMED (I-08).

## D-014 Reformer furnace (2026-10-27)
Decision: fuel = natural gas + tail gas, 10 % excess O2, combustion air preheated to 523 K by
flue gas, complete combustion, bridgewall 1323 K, casing loss 1.5 % of the fired duty (LHV),
stack 423 K; fuel flow from the radiant balance (radiant heat = R-101 duty), convection heat
to the process coils first, the rest (0.6 MW) to steam. Fans 5 kPa each, efficiency 0.70.
Radiant efficiency follows: 68.4 MW to the tubes of about 121.5 MW fuel LHV (56 %; the LHV
from the 1.5 % loss term of the radiant balance and cheme's H-101 duty of 70.2 MW). NOx, CO, CH4 and N2O in the flue gas
are not estimated: no sourced emission factor was used (I-07).

## D-015 Steam system (2026-10-27)
Decision: one raised level, MP steam 4600 kPa(a) / 673 K, from boiler feed water at 313 K
(deaerator heating inside the raising duty), 2 % blowdown; process condensate (V-201, V-401,
dryer) returns to the boiler feed after stripping (dissolved gases neglected); LP steam for the
HRU by let-down, its condensate returned. Steam raised 148 t/h: 92.8 t/h process steam,
0.4 t/h LP let-down, 55.1 t/h export. Reason: with electric drives (D-016) there is no turbine
to use HP steam, so a single MP level keeps the accounting transparent. ASSUMED.

## D-016 Drives and machine efficiencies (2026-10-27)
Decision: all machines electric (process air 8.6 MW, synthesis gas 12.5 MW, circulator
1.6 MW, refrigeration 10.0 MW, solvent pumps 1.5 MW, fans and BFW pumps 1.0 MW: 35.2 MW);
isentropic efficiency 0.78 per stage, ideal gas. Reason: a transparent electricity/steam
accounting for the LCI. Rejected for now: steam turbine drives (the common integrated
practice; they would turn most of the steam export into shaft power): a design alternative to
compare later (I-09).

## D-017 Refrigeration and product flash (2026-10-27)
Decision: an ammonia refrigeration package at 258 K (chiller) and 238 K (product flash),
condensing at 313 K, compressor power at 0.55 of the Carnot work; the let-down liquid is
flashed to 240 K / 110 kPa(a) and its dissolved gases (1.3 mol% after let-down by the PR
flash) leave through the refrigeration receiver's vent chiller at 258 K and 1700 kPa(a),
carrying NH3 at its saturation fraction, to the HRU. Reason: without the vent the product
would hold about 1.7 wt% dissolved CH4 and Ar (below specification). ASSUMED.

## D-018 Lists (2026-10-27)
Decision: equipment list with the 44 items the PFD links to, with duties and conditions from
the balance; no design pressures, materials or sizes yet; no line list (lines come with the
P&IDs, out of scope).

## D-019 Manifest claim (2026-10-27)
Decision: `process.yaml` keeps `maturity: concept`, `validation: unreviewed`,
`publication.status: internal`. `cheme maturity` reaches no level (feed not sourced; separators
specified by an unqualified script): concept is the manifest's lowest value and the
`maturity-claim-exceeds` warning is accepted and explained here, as in methanol-1.

## D-020 Preliminary gate-to-gate LCI (2026-10-27)
Decision: `lca/lca.yaml`, functional unit 1 kg NH3 at the gate, boundary gate-to-gate, case
design. Every foreground exchange comes from a flowsheet terminal (inventory.csv names the
streams). Backgrounds are not linked: natural gas, demineralised water, electricity, cooling
water, blowdown treatment and the steam credit are `missing:` with the activity each should
connect to; no factor and no licensed value is used. Corrected after review
2026-10-27-pfd-lci-review#1: the generated `results.md`/`results.csv` do print a number,
labelled "partial screening carbon footprint" by cheme (1.48 kg CO2-eq per kg NH3 after the
exergy allocation of D-021). That figure is **gate-to-gate direct fossil CO2 only** (process
vent plus stack, GWP100): it leaves out the natural-gas supply chain and its methane leakage,
the electricity, water, cooling water and blowdown backgrounds and the steam credit. It is not
a carbon footprint of the product and must not be quoted as one until the backgrounds are
linked (I-10). Elementary flows: CO2 to air (fossil; includes about 0.2 % atmospheric CO2
from the air), the zero-flow combustibles and NH3 mapped to air so that a later case is
characterised; N2, O2, Ar and H2O returned free. The zeros are modelling choices, not data
(review #2): `emission_exclusions` in `lca/lca.yaml` declare the furnace's incomplete
combustion (H-101) and the CO2-vent co-absorption (C-302) as not estimated, I-07.
Not quantified (open input I-07): furnace NOx, CO, CH4, N2O and particulates (cheme warns
`lci-emissions-incomplete` for H-101; no factor from memory), methanol and amines in the CO2
vent and process condensate, fugitive NH3 and CH4, catalysts, ZnO, molecular sieve, aMDEA
make-up, BFW and cooling water chemicals and their spent wastes (amounts not known).

## D-021 Co-product steam (2026-10-27)
Decision (revised 2026-10-27): exergy allocation between NH3 and the MP steam export, system
model cut-off; substitution (MP steam from a natural-gas boiler, declared missing) is kept as
the comparison in `lca/lca.yaml`. Reason for the revision: the library's LCI export (Atlas
build) publishes one activity per co-product and refuses substitution as the dataset's default
allocation (PR #192 CI). Of the proportional methods, mass would give 0.881 kg steam 47 % of
the burdens of an ammonia plant, no prices are recorded, and energy content is meaningless for
steam; exergy charges each product for the work it holds. Exergy per kg (ASSUMED calculation,
own work): NH3 20,190 kJ (standard chemical exergy 337.9 kJ/mol, Szargut, Morris and Steward
1988, plus 350 kJ physical exergy of the liquid at 240 K, Peng-Robinson in thermo); steam
1,262 kJ (IAPWS-IF97 at 4600 kPa(a), 673 K against liquid water at 298.15 K, plus 50 kJ chemical
exergy of water). NH3 then carries 94.8 % of the burdens. The original preference for system
expansion (ISO 14044) stands as the comparison once a steam background exists. Rejected:
allocation none (would hide the export); mass (above).

## D-022 Concept plot plan (2026-10-29)
Decision: a notional 360 m x 220 m port plot (`layout/site-plan.yaml`) with one east-west pipe
rack PR-1 (y = 110 m, 8 m wide, tiers 6/8/10 m, bents every 10 m so that none stands in the
access roads R-5 and R-6) and the process areas on both sides of it, upstream north and
downstream south: A-100 reforming, A-200 shift/CO2 removal/methanation/drying, A-800 steam
system (north); A-600 purge gas recovery, A-500 compression and loop, A-700 refrigeration and
product flash (south); A-900 reserved for control room, substation and workshops at the
south-west corner, as far as the plot allows from the loop and the ammonia inventory (its
position against the prevailing wind is open: the wind rose is not known, I-03). Roads on
all four sides and two north-south access roads give every area access from at least two
sides. All 44 items are placed (`layout/equipment-placement.yaml`), sized by ASSUMED overall
dimensions in the equipment list (engineering estimates for 1500 t/d, not sized from the
balance; the datasheets replace them). `cheme layout build` reports no clash, no blocked
bundle-pull space and no steel in a road.
Modelling choices: H-101 is the radiant box (40 x 20 x 22 m); R-101 is drawn as the tube inlet
headers on its roof (its heated tubes are inside H-101); the convection coils E-103, E-104,
E-102, E-101, E-107 and the air preheater E-106 are drawn as a row of coil banks against the
radiant box, hot end first. Their separations from H-101 are declared at 1 m because they are
part of the furnace; the package's 15 m fired-equipment spacing does not apply to them.
Spacing criteria (separations, all ASSUMED screening values chosen in this design, not taken
from a standard; the owner's spacing standard and a QRA replace them at basic): fired heater
H-101 30 m from the boundary, from K-501, X-601, K-701 and the A-900 plot, 15 m from V-101;
toppling (1 x height) of C-301, C-302, R-501 and the X-601 cold box to PR-1 and of R-501 to
K-501; V-701, V-501 and K-701 30 m from the boundary; A-900 60 m from K-501 and V-701.
Measured (`cheme show <tag> --layout`, 2026-10-29): H-101 to boundary 40.0 m, to PR-1 36.0 m,
to R-100 17.8 m, to A-900 50.0 m; R-501 to PR-1 29.2 m and to K-501 29.8 m (height 25 m); C-301
to PR-1 58.5 m (height 40 m); V-701 to boundary 38.5 m. `cheme validate` reports no
`layout-separation` finding.
Reason: concept gate `layout-plot-plan`; an area layout in process order along one rack is the
usual arrangement and keeps the reformer's flame away from the hydrogen and ammonia sections.
Open: real plot and wind rose (I-03), nozzles and line routes (with the P&IDs), the cooling
tower, flare and storage outside the boundary (D-001).

## 3. Results of this stage (design case)

Per kg NH3 (lca/inventory.csv, from the flowsheet): natural gas 0.6034 kg (process 0.4721,
fuel 0.1313), ambient air 3.723 kg, demineralised water 1.623 kg, electricity 0.563 kWh,
heat to cooling water 2.104 kWh; outputs 1 kg NH3, MP steam 0.881 kg, blowdown 0.047 kg, CO2
to air 1.563 kg (process vent 1.173, flue gas 0.390). Inventory mass balance: in 5.94962 kg,
out 5.94970 kg; cheme reports mass, element and carbon-origin balances closed. These are the
outputs of one concept design on assumed inputs, not validated performance figures.

## 4. Model and dependency table

| item | model / basis | status |
|---|---|---|
| reformers, shifts, converter | equilibrium (cheme), approaches ASSUMED | calculated by cheme |
| prereformer, burner zone, methanator, furnace | complete conversion (cheme) | calculated by cheme |
| flashes (loop separator, let-down) | thermo PR + ChemSep kij in the script | ASSUMED, unqualified (core #315) |
| water knock-outs, CO2 removal, dryer, HRU, vent | specified splits in the script | ASSUMED |
| duties, compressors, steam, refrigeration | script: cheme ideal-gas enthalpies, PR, IAPWS-IF97 | ASSUMED; energy closure not evaluable in core |
| stream properties (`props --fill`) | no package covers the mixtures (water, NH3 mixtures, hot CO/CH4) | gated: core #315 |
| rigorous simulation (`process simulate`) | not attempted: needs a method accepted for syngas/NH3/water | gated: core #315 |

Core findings for the core repository (not fixed here): `cheme process build` crashes
(`TypeError: 'typing.Union' object is not iterable` in `build.step_method`) on the DEXPI classes
`HeatingInFurnace` and `SupplyingThermalEnergy`, whose `method` field is an Optional enum; the
convection coils therefore use `ExchangingThermalEnergy` and the steam system `ProcessStep`.

## 5. Source register

| source | locator | read in this run | use |
|---|---|---|---|
| Issue #86 and comments (2026-10-27) | proposed brief, handoff | yes | capacity, product, site, route, boundary |
| cheme reaction library (Ullmann's; Twigg, Catalyst Handbook 2nd ed.) | `cheme chemistry library ammonia, steam_reforming, ht_shift, lt_shift, methanation` | yes (library entries) | stoichiometry, catalyst types |
| chemicals / thermo (ATcT, CRC, HEOS, TRCIG) | `cheme chemistry thermo ... --fit 298.15,1500` | yes | formation data, heat capacities, critical constants |
| thermo IPDB "ChemSep PR" kij | scripts/plant_balance.py | yes | loop flash |
| IAPWS-IF97 / IAPWS-95 (chemicals.iapws) | scripts/plant_balance.py | yes | steam enthalpies, water vapour pressure |
| skill tech-petchem-ammonia-and-urea (Speight 2011, ch. 8) | conditions table | yes | plausibility of reformer conditions and loop pressure window |
| EC LVIC-AAF BREF (2007), ch. 2 | issue comments | no | route/boundary guide only; no values used |
| Appl, Ullmann's "Ammonia, 2. Production Processes" | doi 10.1002/14356007.o02_o11 | no | reference for the next stage |
| IEA Ammonia Technology Roadmap (2021); Mayer et al. (2023); Lee et al. (2022) | issue comments | no | not used (design-visible benchmarks; kept out) |

## 6. Open inputs and gated steps

- I-01 Sourced natural-gas composition, pressure, temperature and sulfur specification (the
  benchmark gas is a placeholder; blocks `sourced` maturity).
- I-02 Freeze the brief (capacity, purity, delivery state, hours) with the owner.
- I-03 Ambient and cooling-water conditions of the site (ISO conditions used).
- I-04 Sourced approaches to equilibrium / kinetics and catalysts (reaction evidence file).
- I-05 HDS hydrogen recycle, dryer regeneration, condensate stripper: not modelled.
- I-06 CO2 removal: licensor or rigorous solvent model for slip, regeneration heat, pumping,
  co-absorption and solvent losses.
- I-07 Emissions not quantified: furnace NOx/CO/CH4/N2O/PM (sourced factors or burner
  guarantee), LTS methanol and amines in vent and condensate, fugitives; consumables and
  spent catalysts.
- I-08 HRU recoveries and NH3 wash steam (vendor data).
- I-09 Drive alternative: steam turbines vs electric motors (changes electricity and steam
  export together).
- I-10 Background datasets for the LCI (section D-020), with licences recorded.
- Gated: stream properties and energy closure in core, rigorous simulation (core #315);
  `cheme process build` class bug (section 4).

Chemicals registry entries missing (to add in the consolidated PR, not here): `ammonia` (with
a refrigerated anhydrous liquid grade), `natural-gas`, `ethane`, `propane`, a demineralised
`water` grade, an MP `steam` grade at 46 bar(a) / 673 K; optionally `flue-gas`.
