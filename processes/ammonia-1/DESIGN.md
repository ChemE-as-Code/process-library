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
  Recovered heat is counted once: radiant heat to the tubes (Q9), convection coils (Q3-Q7;
  since D-024 two-stream exchangers on the flue gas, S80-S84),
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
Decision: methanator feed heated to 553 K by heat from E-201 (energy stream Q14; since D-024 the
HTS effluent itself heats it in the gas/gas exchanger E-401, between E-201 and the LTS); complete
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

## D-023 Class 5 capital estimate and screening TEA (2026-10-29)
Decision question (for the owner, `estimate/tea.yaml`): proceed to basic engineering of the
1500 t/d plant in the Rotterdam area, judged by whether its levelised cost of production (LCOP)
is at or below the price of imported ammonia (439 EUR/t: the 2025 US Gulf Coast average from
USGS at the Eurostat 2025 exchange rate, without freight, ASSUMED as the import parity).
Capital (AACE class 5, capacity-factored): reference IEAGHG Technical Report 2017-03, Case 4A-1
(SMR with air-blown secondary reformer, north-east Netherlands, 1350 t/d NH3 with a urea plant;
Table 1, 4Q2014 EUR): process plant installed cost 493 MEUR for ammonia and urea together. The
report does not split it: the ammonia share is ASSUMED 0.70 (scenario 0.60). Scaled to
1500 t/d with an ASSUMED exponent 0.67 and escalated 2014 to 2025 by the Eurostat producer
price index of machinery (NACE C28, NL; 1.397, a proxy, ASSUMED). OSBL 0.109, owner's cost 0.07
and contingency 0.20 follow the reference's own build-up. Result: ISBL 517 MEUR, fixed capital
737 MEUR (2025), class 5 range about 368-589 MEUR at the low end to 958-1473 MEUR at the high
end. core's equipment correlations (`cheme assess equipment`) were not used: they need
exchanger areas, compressor fluid powers and material factors that the concept does not have,
and the two columns lie outside the correlation range.
Prices (2025): natural gas 11.397 EUR/GJ (GCV) and electricity 100.65 EUR/MWh, Eurostat
non-household prices NL, bands I6 and IG, excluding VAT (QUOTED: a published series); NH3
439 EUR/t (ASSUMED proxy); MP steam export 38.39 EUR/t as the gas a 90 % boiler would burn
(ASSUMED); CO2 74 EUR/t (EU ETS 2025 average, ESMA via a secondary report, ASSUMED), on all
direct CO2 because free allocation for ammonia is phased out by 2034 under CBAM. Demineralised
water, blowdown treatment and cooling water are **not priced** (`tea-price-missing`): no
sourced price was found; they are small next to gas and lower the LCOP that is shown. Fixed
cost (maintenance 3 %, insurance 1 % of fixed capital, 60 operators at 80 kEUR), discount rate
8 % real and 25-year life are ASSUMED screening values; Dutch corporate tax 25.8 %.
Result (`estimate/tea.md`): LCOP 739 EUR/t (gas 351, electricity 57, CO2 116, steam credit
-34, fixed cost 69, capital and tax 181); cash cost 558 EUR/t; NPV -1019 MEUR at 8 %. The
criterion is **not met** in the baseline or any scenario (no carbon price 624, 2024 gas price
661, ammonia share 0.60 705 EUR/t). Dominant premises: the gas price (LCOP 599-950 EUR/t
over x0.6-1.6; the decision turns only at 1.66 EUR/GJ), then the ammonia price and plant
output, capital and the carbon price.
Consequence: on these premises a new conventional plant in the Netherlands does not compete
with imported ammonia; that is the owner's investment question (I-02), not a design defect. The
issue #86 brief commissions this plant as a design case, so the design continues to basic
engineering; the verdict and the premises go with the concept sign-off for the owner. Next:
price the three missing utilities, a Rotterdam delivered import price with freight, and the
steam-turbine alternative (I-09), which trades the 57 EUR/t of electricity against the
steam credit.

## D-024 Process simulation: scope, model and what it found (2026-10-29, S2)
Decision: the plant is simulated with DWSIM 9.0.5 through `cheme process simulate` (core
v1.0.0, Peng-Robinson, D-025; model in process/simulation.yaml, run record
process/simulation-run.json). Simulated and filled as `calculated` (58 streams, design case,
the only case of the design basis, D-003): REF without the radiant section, SHF, CO2R, MET,
with their three recycles converged (convection coils S4, S9; methanator feed heater S27).
Left out (`exclude`) and why:
- **H101** (furnace radiant section): its radiant heat Q9 is R-101's duty; core refuses an
  energy stream shared by two units and has no adjust to set the fuel from the radiant
  balance. S65 stays `calculated` by `cheme process propagate` from the simulated S64.
- **U801** (steam system) is an energy-only package balance; raising steam from the boiler
  duties needs flows set from duties (an adjust), which core does not offer. Its streams stay
  the concept balance's (ASSUMED); the simulated boiler duties (Q8, Q10, Q13) are written.
- **SYN and PGR** (synthesis loop, product flash, refrigeration, purge recovery): modelled in
  DWSIM but not converged in core's terms (superseded by D-026: simulated and converged on core
  v1.0.1; the record below stays as the first session found it). Evidence (runs of 2026-10-29, saved DWSIM files):
  with the loop torn at S46 and S48 (or S47/S39, S46/S51), the first recycle settles exactly
  (S47 and its copy equal to the last digit, 85.05577895954663 kg/s), while the second
  recycle's copy never leaves its guess (S39-R stays 240,150.9 kg/h against 240,077.3 kg/h
  computed, run after run; S48-R and the flash-gas tear S71-R the same in the full plant), and
  DWSIM still ends with "Recycle reached the maximum number of iterations"; core then writes
  nothing. The loop as solved reached 306.2-306.5 t/h at the converter with a 0.1 kg/h
  difference between runs, far inside the 0.5 % balance tolerance; core's recycle criteria
  (1e-7 kg/s absolute, no acceleration, 500 iterations) are not met. This is a core/DWSIM
  problem to report (orchestrator), not worked around. Until it is fixed, SYN and PGR keep the
  concept balance's loop model, re-solved on the simulated make-up gas S34 at the flowsheet's
  purge fraction (scripts/loop_on_simulated_makeup.py, values ASSUMED with that source); the
  refrigeration duties Q26-Q28, Q29, Q30 are the concept balance's, not re-solved.
  The DWSIM-ready loop model (kept here for the fix): V-701 as a flash at 110 kPa(a) /
  240.15 K whose flash gas is compressed in two cooled stages to 1700 kPa(a) (K-701 duty),
  chilled to 258.15 K and separated in the receiver (vent to the HRU, liquid back to V-701,
  D-017); the HRU split into an NH3 wash (99 % NH3), a cold box (D-013 recoveries) and a
  hydrogen compressor to 2850 kPa(a) inside the X-601 package (the mixed HRU feed is at the
  vent pressure, below the make-up gas compressor suction); tears S44, S46, S48, S71; the loop
  specs remain in process/simulation.yaml.
Flowsheet changes this needed (the BFD/PFD are regenerated): the convection coils E-101,
E-102, E-103, E-104, E-106 are two-stream exchangers on the flue gas (hottest coil first:
E-103, E-102, E-104, E-101, E-106, then E-107, S80-S84; Q3-Q7 removed); E-401 is a gas/gas
exchanger heated by the HTS effluent between E-201 and the LTS (S75; Q14 removed; E-201's
outlet 611.2 K ASSUMED from the concept balance's split of that heat); the make-up water to the
CO2 removal is pumped (P301, a ProcessStep with `unit: pump`: `cheme process build` fails on the
DEXPI class Pumping in core v1.0.0) and mixed in M301 ahead of C301, which is now a one-inlet
component separator; K-101's fourth stage is a step of its own (K101D, uncooled, as D-016),
because core's intercooled machine also cools its last stage; the condensate stripper vent S87
takes the gases dissolved in the simulated condensates (294.8 kg/h, 99.5 mol% CO2) out of the
steam system to the CO2 vent (D-015 had neglected them).
Model basis: specified splits, not predictions, for C301 (D-009: CO2 fraction 0.002273 and
water 0.176006 to the treated gas, from the concept balance at the design flows) and X401
(D-010); conversion reactors R100, R102A, R401 as before. DWSIM 9.0.5's equilibrium reactor in
adiabatic mode fails its flash through core v1.0.0 (reproduced on R201 alone, with and without
the approach), so the adiabatic beds R102B, R201, R202 run at the concept balance's adiabatic
outlet temperatures and their duty is the check: 384 kW (R102B), 240 kW (R201) and 172 kW
(R202), i.e. 0.4 to 2.6 % of their reaction heats; R101 68,616 kW (concept 68,386 kW).
Mixers take no pressure drop in DWSIM: the drop the concept balance gave M101 and C301 is put on
the next item (E-102, E-401).
Findings (deviations kept, not edited away):
- **Stack temperature 395.9 K, not 423 K** (S66): with the concept fuel flow the convection
  coils take 1.75 MW more than in the concept balance (E-102 +0.9 MW, E-103 +0.4 MW, E-101
  +0.3 MW). The furnace balance (fuel from the radiant balance, D-014) has to be redone once
  H101 can be simulated; E-107's duty (589.5 kW) is held at the concept value.
- **E-203 duty 34.7 MW** against 31.2 MW in the concept balance (water condensation in
  Peng-Robinson against the IAPWS knock-out of the script); E-402 17.7 MW (17.5 MW).
- **S28 (CO2 vent) and S35 (dryer water) pressures**: a component separator leaves its outlets
  at the inlet pressure (3100, 2900 kPa(a)); the assumed 150 and 300 kPa(a) are the real
  conditions and stay.
- **Q18** (CO2 removal coolers): not written; the component separator's energy imbalance
  (290 kW) is a bookkeeping residual of its split, the 21.9 MW stays ASSUMED (D-009).
- **H2/N2 at the converter inlet 2.85, not 3.0** (D-007) in the re-solved concept loop: the
  make-up H2/N2 fell from 3.005 to 3.000 with the simulated front end and the fixed purge
  lets N2 accumulate; the process air (S12) would need to be retuned when the loop is
  simulated. Product 62,438.8 kg/h (1,498.5 t/d, -0.1 %); inerts 12.2 % at the converter.
- **LCA boundary check**: it reads the reactor modes of process/simulation.yaml and now flags
  R102B, R201 and R202 (run at their outlet temperature, above) as exchanging heat with no
  utility; their simulated duties (0.4 to 2.6 % of the reaction heat) are the residual of that
  workaround, not a utility. lca/ was regenerated; the per-kg figures of section 3 are the
  concept stage's and are superseded by lca/inventory.csv.
Energy audit (`cheme process energy`, run record): every simulated reactor closes on the
formation basis (residuals below 1e-4 kW); DWSIM's formation enthalpies differ from
materials.yaml within the data tolerance (largest CO2, 36 kJ/kmol); no temperature cross in
any exchanger (least approaches 35-348 K; no min_approach declared beyond D-012's 5 K for
cooling water); utilities of the simulated part: hot 69.4 MW (radiant heat and the
regenerator duty), cold 165.6 MW, power 9.2 MW, recovered between process streams 71.0 MW. The
plant closure is not evaluated by core while component separators (C301, X401) are in the
flowsheet ("sign of the component separator's energy imbalance not established"), and block
energy balances need stream enthalpies that `cheme process props` cannot give: no property
package covers H2O, O2 or C2H6 (core #315).
Reason: build the simulation the brief asks for as far as core runs it, and keep every
limitation visible. Rejected: tuning tolerances, tears or values to make the loop "converge",
a relaxed recycle test, or writing the unconverged loop values by hand.

## D-025 Property package for the simulation (2026-10-29, S2)
Decision: Peng-Robinson (DWSIM 9.0.5's PR with its own kij) for the whole simulated plant.
The model selection (skill thermodynamic-model-selection, Carlson's tree, facts recorded in
process/simulation.yaml `method_selection`) with the facts polar (water, ammonia), no
electrolytes in the simulated part, no pseudocomponents, 155 bar(a), no sourced PR kij for the
loop pairs (uncertain, so answered conservatively), no liquid-liquid split, no association
recommends PSRK or PR/RKS with modified Huron-Vidal mixing; the DWSIM route runs none of
them, and Peng-Robinson is their executable substitute (methods.yml; it loses the polar
mixing rule). The S2 brief (runs/plan.md) prescribes a cubic equation of state for the syngas
and the loop; the substitution is recorded as `method_selection.substitution` and stays
visible (`sim-method-substituted`) for the reviewer to accept or reject.
The aMDEA CO2 removal needs an electrolyte model (amine protonation, carbamate/bicarbonate
speciation, e.g. electrolyte NRTL) and rate-based absorption; `cheme process methods` lists
ENRTL-PR and PITZER-RKS as unsupported on both routes, and core refuses electrolytes in
simulation (`process-sim-electrolyte`). C301 therefore stays a specified separator (D-009),
marked `basis: specified` in the run record.
Known weak spots: NH3 condensation with dissolved H2/N2/CH4/Ar at 263 K and 147 bar (loop
separator, let-down, flash) and CO2 solubility in the process condensate rest on DWSIM's own
kij, not on sourced data (open input: kij for NH3-H2, NH3-N2, NH3-CH4, NH3-Ar, CO2-H2O).

## D-026 Synthesis loop and purge recovery simulated on core v1.0.1 (2026-10-29, S2 round 2)
Decision: with core v1.0.1 (core#57 fixed: tear iteration with Anderson acceleration, ADR 0033;
core#59 fixed: the DEXPI class Pumping) the whole process side is simulated in one DWSIM
solve: REF (without H101), SHF, CO2R, MET, SYN and PGR, one case (design, D-003), converged
with seven tears (S4, S9, S27 as before; S44 the converter feed/effluent exchanger, S46 every
loop path through E-501's hot side including the purge recovery's return, S48 the cold
exchanger, S88 the product flash gas with its returned liquids). DWSIM 9.0.5, Peng-Robinson
(D-025), core v1.0.1; run record process/simulation-run.json; 105 streams written as
`calculated`. Left out: H101 (as D-024), the steam system U801 and the chiller refrigeration
circuit K701: energy-only packages whose flows follow from duties (an adjust core does not
offer); their values are evaluated on the simulated duties by
scripts/packages_on_simulated_duties.py with the concept models (0.55 of Carnot, IAPWS-IF97;
D-015, D-017) and stay ASSUMED with that source. scripts/loop_on_simulated_makeup.py is removed:
none of its values is left.
The loop model is D-024's DWSIM-ready description, with these changes found while running it:
- **Let-downs are valves.** A DWSIM vessel given only a pressure holds its inlet temperature
  (core's flash maps a pressure to OverrideP), which is no let-down: the first run flashed the
  product at 313 K and the flash-gas loop ran away. The separator liquid is let down in a valve
  LV501 to 2500 kPa(a) and V-502 flashes adiabatically (S53/S54 at 266.05 K, as the concept's
  isenthalpic let-down, 266.07 K).
- **The product flash runs at its adiabatic temperature.** An adiabatic let-down to 110 kPa(a)
  fails DWSIM's PH flash for this mixture ("Unable to calculate PV Flash with P = 110000 and
  VF = 0.01"); V-701 is therefore a TP flash at 110 kPa(a) whose temperature was set so that its
  duty Q26 is about zero (238.7 K: -32 kW), the same device as the adiabatic beds of D-024. At
  the design basis's 240.15 K the drum would need 3.0 MW of heat, because the dissolved inerts
  carry NH3 vapour at its saturation pressure. D-017 had 238 K for this level.
- **Flash gas, receiver and vent (D-017).** The flash gas S88 (7.27 t/h, 86 mol% NH3) is
  compressed in K-701's flash-gas stages (K702, two stages, 0.78, 1.05 MW) to 1700 kPa(a) and
  cooled to 313 K (0.85 MW to cooling water); at 1700 kPa(a) its NH3 partial pressure stays below
  the vapour pressure at 313 K, so nothing condenses in the receiver V702 (S90 = 0) and the vent
  chiller E702 condenses it all at 258 K (2.32 MW, to the refrigeration package); the vent S55,
  1.26 t/h with 16 mol% NH3, goes to the HRU (concept 1.24 t/h, 14 mol%).
- **HRU (D-013) at the vent pressure.** M601 mixes purge, let-down gas and vent at 1700 kPa(a)
  (S57, 252.6 K, 3.95 t/h); X601 (NH3 wash, 99 % NH3) and X602 (cold box, D-013 recoveries) are
  specified splits; K601 compresses the H2-rich gas S36 to 2850 kPa(a) (53 kW); E601 chills the
  recovered NH3 to 240.15 K and lets it down to 110 kPa(a) (pressure drop in the step, a cooler
  takes no outlet pressure in core).
- **Converter at its outlet temperature.** DWSIM's adiabatic equilibrium reactor fails its flash
  at R501 as it did for the beds (D-024): "TP Flash: one or more flash specification values are
  invalid". R501 runs at 703.15 K (D-011) and its duty is the adiabatic check: 31 kW, 0.1 % of
  the reaction heat, after the retune below.
- **P301** is a Pumping step (core#59 fixed); no `unit:` override.
Retuned (design choices, ASSUMED; the simulated values were not edited):
- **Process air S12 67,184.1 kg/h** (concept 67,281.6): H2/N2 at the converter inlet 3.007
  (D-007 asks 3.0; D-024 found 2.85 on the re-solved concept loop, the first converged run here
  2.74). The loop ratio is very sensitive to the air: 2.4 kg/h of air (0.004 %) moved it from
  3.012 to 2.993; 3.0 +/- 0.01 is what the tear tolerance resolves. The plant needs an H2/N2
  analyser trimming the process air (a control loop for S4).
- **E-502 outlet 532.6 K** (concept 547.21 K) so that the converter runs adiabatic (D-011:
  overall adiabatic converter); at 547.21 K R501 needed -3.3 MW. Converter inlet 493.8 K (concept
  505.2 K).
Results (design case): product S60 62,470.7 kg/h at 238.7 K, 99.981 mol% NH3 (CH4 96, Ar 89 ppm
by mole; 1,499.3 t/d, contained NH3 within 0.1 % of D-002); converter feed 294.0 t/h, NH3
3.34 -> 18.44 mol%, inerts 12.1 %; purge S50 1.69 t/h; separator gas 229.7 t/h; duties: K-501
12.72 MW (cooling 12.88 MW), K-502 1.61 MW, E-501 46.6 MW, E-502 43.2 MW (concept 39.7), E-503
7.52 MW, E-505 7.80 MW, E-504 22.5 MW (22.7); refrigeration package (script) 10.08 MW power,
34.96 MW condenser; steam (script) 153.4 t/h raised, 60.1 t/h exported (concept 55.1), DMW
105.1 t/h. Utilities of the simulated plant (run record): hot 69.5 MW, cold 254.8 MW, power
24.7 MW, recovered between process streams 125.3 MW.
Findings (deviations kept, not edited away):
- **Product at 238.7 K, not 240.15 K** (S56, S60): the adiabatic flash at 110 kPa(a) (above).
  The design basis's product state is an assumption to revisit with the owner (I-02).
- **S59 tail gas** leaves the cold box at the HRU feed state (252.6 K, 1700 kPa(a)) in the model,
  against D-013's 303 K and 400 kPa(a): a component separator neither rewarms nor lets down. The
  assumed values are the package's real outlet and stay; the fuel side (H101) is not simulated.
- **S36** 305.5 K after K601 against D-013's 303.15 K (uncooled compressor).
- Also still open from D-024: S66 stack 396.7 K (423.15 K), S28 and S35 pressures, Q18.
- **Product purity**: 190 ppm (mol) of dissolved CH4 and Ar in the product; the concept assumed
  NH3 1.0 (D-017); that assumed composition of S56 is replaced by the simulated one.
- **E505** carries a phase change on its hot side (S46 condenses); its internal approach is not
  checked by core (`sim-exchanger-zones`), least approach on the composites 10 K.
- **K601 energy balance** with the stream enthalpies of `cheme process props` (thermo PR with
  ChemSep kij, filled for the six streams inside the package's claim) differs from DWSIM's power
  by 2.2 kW (4 %): two Peng-Robinson implementations with different kij.
- LCA boundary check: R501 now runs at its outlet temperature too and is flagged like R102B,
  R201, R202 (`boundary-utility-unassigned`); its 31 kW is the residual, not a utility.
Energy audit (`cheme process energy`): every simulated unit closes (largest residual 0.17 kW at
E-501; reactors on the formation basis, R501 residual 0); every exchanger without temperature
cross (least approaches E-505 10 K, E-501 31 K); utility levels ok. The plant closure stays
unsupported by core while component separators are in the flowsheet (C301, X401, X601, X602:
"the sign of the component separator's energy imbalance is not established", core#60); block
energy balances need stream enthalpies that `cheme process props` gives for 6 of 121 streams
(core#315: no package covers H2O, O2, C2H6, or NH3 liquid and the loop above 5-15 MPa).
Maturity (`cheme maturity`, 2026-10-29, after this run): calculation maturity none. Requirements
that fail, exactly: `sourced.boundary` (feed flows and compositions not given with a source:
S1 natural gas, R-03/I-01, the process and combustion air S12, S61 and the demineralised
water S26, S70, all ASSUMED; flows and compositions of each); `balanced.model-basis` (the complete conversions of R100, R102A, R401
and H101 are assumed, unsourced); `predictive.coverage` (H101, K701, U801 excluded);
`predictive.model-basis` (specified conversions and splits: R100, R102A, H101, R401, C301,
X401, X601, X602); `predictive.property-regime` (core#315: core's benchmarked claim for DWSIM 9.0.5
Peng-Robinson covers nitrogen, oxygen and argon only, so every feed and stream with CH4, C2H6,
C3H8, CO, CO2, H2, H2O or NH3 is outside it: 266 cases); `predictive.energy-closure` unsupported (core#60, component
separators). What passes: process rules, balances evaluable and closed, simulation spec, run
record current and converged, solver recorded, property package with its recorded
substitution, stream properties inside the claim, exchangers, formation data. The gate
`maturity-balanced` therefore fails on `sourced.boundary` and `balanced.model-basis`; neither is
a core limit: both need sources (I-01 for the gas; reaction evidence for the complete
conversions).
Reason: the brief asks for the whole plant simulated and converged on v1.0.1; every change
above is a modelling necessity or a retune of an ASSUMED design choice, recorded here.
Rejected: loosening tolerances or tears, writing simulated values by hand, keeping the
concept's loop values where the simulation covers them.

## D-027 Front-end P&IDs P-101 to P-104 (2026-10-29, S3a)
Decision: the front end is drawn on four A3 sheets, one per PFD section of blocks REF and SHF:
P-101 feed gas, desulphurisation V-101, process steam addition, prereformer R-100; P-102
reformer furnace H-101 with the catalyst tubes R-101 drawn in its radiant box, the convection
coils in flue gas order (E-103, E-102, E-104, E-101, E-106, E-107, D-024), FD fan K-102 and ID
fan K-103; P-103 process air compressor K-101, secondary reformer R-102, waste heat boiler E-105
with a hot bypass, HT shift R-201 and E-201; P-104 LT shift R-202, the process-gas side of the
regenerator reboiler E-202, final cooler E-203 and condensate separator V-201. The split
follows the flowsheet blocks: everything of SHF, including E-202, E-203 and V-201, is on P-104,
so the CO2 removal sheets (S3b) start at C-301 and C-302 and the loop and utility sheets (S3c)
at U-801. The sheets are hand-maintained; `scripts/draft_P-10x.py` wrote their first
revision (provenance, run with `cheme run`), and two DN corrections were made after it with
`cheme set` (NG-1004 is DN 400 with a DN 200 first segment; the builder takes one DN per line).
Lines: number `<fluid code>-<serial>` (NG natural gas, FG fuel and tail gas, SM steam, PG
process gas, PA process air, CA combustion air, FL flue gas, BW boiler water, CWS/CWR cooling
water, PC process condensate, AM aMDEA solution), serials 1001-1055 (51 lines). A line drawn on two
sheets keeps its number; the off-page text names the sheet when it is a front-end sheet.
Interfaces to S3b/S3c, by line number, to be continued there: PG-1035 (S75 to E-401), PG-1043
(S20 from E-401), PG-1047 (S24 to C-301), AM-1049/AM-1050/AM-1051 (E-202 shell side with C-302),
SM-1005 (S6 from U-801), BW-1024/BW-1025 (E-107), BW-1037/SM-1038 (E-105), BW-1039/SM-1040
(E-201), PC-1048 (S25 to U-801), FG-1010 (S59 from X-601), CWS-1041/CWR-1042, CWS-1052/CWR-1053.
DN: first pass on the design-case stream of `process/flowsheet.yaml` with an ideal-gas density
and ASSUMED velocities (process gas and air 20 m/s, MP steam 30 m/s, low-pressure air and flue
gas 15 m/s, liquids 1.5 m/s); air and flue gas ducts above DN 1600 carry an equivalent
diameter (no DEXPI DN standard). Boiler water downcomers and risers use a natural-circulation
ratio of 5 (ASSUMED) on the waste heat boiler duties; the E-202 shell side, the anti-surge
blow-off and the E-105 bypass have ASSUMED DN: the solvent rate and the bypass fraction are not
calculated.
Instruments: one loop number per measurement (sheet series 10xx-13xx), the regulatory loops a
basic P&ID needs (feed flow, steam-to-carbon ratio, fuel pressure reset by the reformer outlet
temperature, excess air by O2, draft, process air flow, anti-surge, HT and LT shift inlet
temperatures, separator level, cooler outlet temperature) and four trips proposed in
`control/cause-effect.yaml` (I-101 low-low process steam, I-102 furnace pressure high-high,
I-103 secondary reformer outlet high-high, I-104 separator level high-high). Equipment-list
change: E-106 was typed AirCoolingSystem (an air-cooled exchanger); it is a flue gas / air
preheater and is now TubularHeatExchanger, as drawn.
Relief: PSV-1212 on the K-101 discharge (before the check valve) and PSV-1310 on V-201,
listed in `piping/special-items.yaml` without set pressure or relief case (no relief study
yet, S8). The builder has no safety-valve class: each was drawn as a globe valve and turned
into a SpringLoadedGlobeSafetyValve (tag in PositionNumber, catalogue shape
SAFETY_VALVE_SPRING_LOADED_SHAPE) by a hand edit of the XML. Whether the reformers, shift
converters and waste heat boilers need their own devices depends on the design pressures
against the 4500 kPa(a) gas supply, which are not set yet.
Not drawn yet (open, for the reviews and S4/S8): further relief devices (see above), burner
management of H-101, control valve block and bypass valves, vents, drains and
sample points, the K-101 intercoolers and drive (inside its package), the stack (not a listed
item), steam drums (U-801, S3c).
Reason: S3a of runs/plan.md; the block split keeps every PFD step on exactly one sheet.
Rejected: drawing E-202 and V-201 with the CO2 removal (they are in block SHF), one sheet for
the whole furnace and reforming (too dense for A3).

## D-028 Mid-section P&IDs P-105 to P-108 (2026-10-29, S3b)
Decision: the CO2 removal, methanation and make-up gas compression are drawn on four A3 sheets:
P-105 CO2 absorber C-301 with the lean solvent pumps P-301A/B and the lean solvent cooler E-302;
P-106 CO2 regenerator C-302 with the lean/rich exchanger E-301, the overhead condenser E-303,
the reflux drum V-302 and the reflux pumps P-302A/B; P-107 E-401 (HTS effluent in the tubes,
treated gas in the shell), methanator R-401, effluent cooler E-402, knock-out drum V-401 and the
molecular sieve package X-401 (one adsorber symbol for the package); P-108 synthesis gas
compressor K-501 (three stages, intercoolers and aftercooler in the package as for K-101 in
D-027) with the recovered hydrogen junction M501. The recycle circulator K-502 is in the loop
and left to S3c. Sheets hand-maintained; `scripts/draft_P-105.py` .. `draft_P-108.py` wrote
their first revision (provenance, run with `cheme run`).
Solvent loop items: the flowsheet lumps the aMDEA loop in step C301 (D-009), so a P&ID needs
items the PFD does not have. Added to the equipment list and the plot plan as the generic amine
absorber/regenerator loop (lean/rich exchange, lean pumps and cooler, overhead condenser, reflux
drum and pumps; skill `tech-gas-acid-gas-removal`): E-301, E-302, E-303, V-302, P-301A/B,
P-302A/B, every size and position ASSUMED, no duty calculated. E-301 is a plate exchanger
(ASSUMED, the usual choice for lean/rich service). Not drawn: a rich solvent flash drum (the
flowsheet has no co-absorption, I-07; its flash gas would be a stream the PFD lacks), a
semi-lean split, solvent filtration, storage and drain system, antifoam injection. The make-up
water of step P301 (S26) is drawn into V-302 on FIC-1508; the lean solvent pumps raise it to
absorber pressure, as D-024 describes (the P301 step stays linked to C-301). The E-202 kettle
overflow AM-1051 goes to E-301 (P-104 off-page text and line-list `to:` changed from C-302).
Lines: numbers continue D-027 (serials 1056-1092; CO2 for CO2 vapour, DW demineralised water).
Gas DN as D-027 (20 m/s, ideal gas; CO2 vent CO2-1068 at 15 m/s, 150 kPa(a), DN 900); PG-1081
is DN 350 on both sheets (S34 needs 0.345 m, S37 after the hydrogen joins 0.351 m: 20.1 m/s
accepted). Solvent lines from the ASSUMED 18 m3 per t CO2 of D-009: 1,313 m3/h at 1.5 m/s gives
DN 600, the pump discharges DN 500 (1.9 m/s). Regenerator overhead DN 1200 and reflux DN 100
ASSUMED (about one mole of water per mole of CO2 in the overhead, not calculated). Cooling water
10 K rise and up to 2.2 m/s (ASSUMED); E-302 and E-303 each take half of Q18 (ASSUMED split).
Small liquid lines DN 25 minimum (ASSUMED). Bypass, anti-surge and relief lines have ASSUMED DN.
Instruments: loop numbers by sheet (14xx P-105, 15xx P-106, 16xx P-107, 17xx P-108). Regulatory
loops: absorber level on the rich solvent (LIC-1405), lean solvent flow (FIC-1407) and
temperature (TIC-1408 on the E-302 water), regenerator pressure on the CO2 vent (PIC-1505),
reflux drum level on the reflux (LIC-1506), make-up water flow (FIC-1508), LT shift inlet
temperature by an E-401 hot-side bypass (TIC-1601, PG-1082: the loop D-027 lists, now drawn),
V-401 inlet temperature on the E-402 water (TIC-1608), V-401 level (LIC-1609), K-501 anti-surge
(UIC-1703, recycle PG-1089 from after the aftercooler to upstream of the suction flow
measurement). The methanator inlet temperature (TI-1603) has no independent control: it follows
the TV-1601 bypass; a start-up heater is not drawn (open, S4). Trips proposed in
`control/cause-effect.yaml`: I-105 C-301 level low-low closes XV-1406 (gas blow-by into the
low-pressure regenerator), I-106 R-401 bed temperature high-high closes XV-1604 (CO/CO2
breakthrough, runaway methanation); whether K-501 trips is left for the HAZOP. Analysers: CO2
slip (AI-1403), CO + CO2 before and after R-401 (AI-1604, AI-1607), moisture after X-401
(AI-1610).
Relief: PSV-1513 on C-302 (cases include gas blow-by through LV-1405) and PSV-1704 on the K-501
discharge, drawn as globe valves and made SpringLoadedGlobeSafetyValve by hand as in D-027;
listed in `piping/special-items.yaml` without set pressure (S8). Spec break at the K-501
discharge noted on P-108, pipe classes not chosen.
Not drawn yet (open, for the reviews and S4/S8): pump minimum-flow lines and discharge gauges,
control valve block and bypass valves, vents, drains and sample points, the X-401 regeneration
circuit (inside the package, I-05), K-501 seal gas, lube oil and drive, further relief devices
(V-401, V-302, E-401 shell, depending on design pressures not set yet).
Reason: S3b of runs/plan.md; the split follows blocks CO2R, MET and the compressor of SYN.
Rejected: one sheet for absorber and regenerator (too dense for A3 with the auxiliaries); drawing
the solvent loop as two bare columns as the PFD does (a P&ID needs the pumps, exchangers and the
level and blow-by protection between the two pressures).

## D-029 Loop and utility P&IDs P-109 to P-114 (2026-10-29, S3c)
Decision: the rest of block SYN, blocks PGR and STM and the main utility headers are drawn on
six A3 sheets: P-109 make-up / recycle junction M502, circulator K-502 with anti-surge recycle,
feed/effluent exchanger E-501 (feed in the shell, effluent in the tubes) with the converter
inlet bypass, converter R-501 (three beds drawn, interbed exchange inside) and waste heat boiler
E-502; P-110 loop water cooler E-503, cold exchanger E-505, chiller E-504, separator V-501 with
the purge take-off (SPL501), the separator let-down (LV501 as LV-1903) and let-down vessel
V-502; P-111 product flash drum V-701, refrigeration package K-701 with condenser E-701 and the
product to the storage interface (battery limit) with the recovered NH3 joining (M701); P-112
the purge gas recovery package X-601 as one symbol (M601, NH3 wash, E601, cold box X602 and
hydrogen compressor K601 inside, as the flowsheet links them); P-113 the steam system U-801 as
one lumped symbol (deaerator, condensate stripper, steam drum, superheater, LP let-down: the
flowsheet's U801 step, D-015) with the BFW pump P-801, the boiler water circuits of E-107, E-105,
E-201 and E-502, the MP steam header, LP steam, condensate returns, make-up and blowdown; P-114
the cooling water supply and return headers with a branch to each of the nine CW users and the
flare header collecting five relief lines. Sheets hand-maintained; `scripts/draft_P-109.py` ..
`draft_P-114.py` wrote their first revision (provenance, run with `cheme run`). Every PFD step of
SYN (except K-501, P-108), PGR and STM is on a sheet, as an item or inside a listed package.
Package boundaries (ASSUMED, as the flowsheet links them): the K-701 package holds the chiller
and flash-gas compressor stages, the flash-gas intercooler, the receiver V702, the vent chiller
E702 and its knock-out V703; the X-601 package as above. No equipment was added to the list:
P-801 is drawn single (spare and three-element drum level control open, S4); the product pumps
and storage are outside the battery limit.
Lines: numbers continue D-028 (serials 1093-1146; 1094, 1103, 1110, 1112 not used; AL liquid
ammonia, AG ammonia vapour, SL LP steam, BD blowdown, FLR relief gas). A line drawn on two
sheets keeps its number (PG-1088, PG-1093, PG-1102, PG-1109, PG-1113, AL-1114, AL-1117,
AG-1118, PG-1126, PG-1087, FG-1010, AL-1124, AG-1125, AL-1129, SL-1135, PC-1136, the boiler water
circuits, the CW branches and the relief lines). DN from the design-case streams as D-027
(build/ scratch calculation, ideal-gas density; gas 20 m/s, liquids 1.5 m/s, steam 30 m/s, CW
2.2 m/s with 10 K rise, all ASSUMED); liquid NH3 density and the refrigerant properties
(saturation pressure 236 kPa(a) at 258 K and 1555 kPa(a) at 313 K, heat of vaporisation, liquid
heat capacity) from thermo's pure-component correlations in cheme's interpreter. Refrigerant
flows follow from the simulated chiller duties (Q25 22.5 MW, Q34 2.3 MW, Q30 7 kW): 21.4 kg/s to
E-504 (AG-1118 DN 900 at 236 kPa(a), AL-1117 DN 200); K-701 discharge DN 450 with an ASSUMED
380 K discharge temperature. E-502 downcomer BW-1100 DN 400 from 25.9 kg/s steam (Q23 over the
heat of vaporisation at 4600 kPa(a)) and the circulation ratio 5 of D-027; riser DN 250 in
D-027's riser/downcomer ratio. MP steam header SM-1140 DN 350 for the 153.4 t/h raised, process
steam SM-1005 DN 300 branching from it (as on P-101), export through PV-2203 at the header DN.
LP steam level 450 kPa(a) ASSUMED (D-015 names an LP let-down without a pressure): SL-1135 DN 65
for Q29. Cooling water headers DN 1400 for the 136.5 MW of CW duties (Q2, Q16, Q18, Q19, Q21,
Q24, Q28, Q33). Flare header DN 300 and every relief line DN ASSUMED (no relief loads, S8). Small
lines DN 25 minimum (ASSUMED). Two-phase let-down downstream of LV-1903 (S99, 0.243 m at 20 m/s)
is drawn in the line's DN 150; the valve outlet size is open with the valve sizing.
Instruments: loop numbers by sheet (18xx P-109 ... 23xx P-114). Regulatory loops: K-502
anti-surge on the suction flow (UIC-1802), converter inlet temperature by the E-501 bypass
(TIC-1803), separator level on the let-down valve (LIC-1903), purge flow (FIC-1905), V-502
pressure (PIC-1906) and level (LIC-1907), chiller refrigerant level (LIC-1908), V-701 level on
the product (LIC-2005), receiver vent pressure (PIC-2007), tail gas pressure (PIC-2104), LP steam
to the NH3 distillation (FIC-2106), steam drum level on the BFW (LIC-2201), deaerator level on
the make-up water (LIC-2202), MP header pressure on the export (PIC-2203), LP steam pressure
(PIC-2206). Analysers: H2/N2 of the converter feed (AI-1804; D-026 asks it to trim the process
air, the loop is S4's), H2 of the recovered gas (AI-2103). Trip proposed in
`control/cause-effect.yaml`: I-107 V-501 level low-low closes XV-1904 (gas blow-by from
14,700 kPa(a) into V-502 at 2500 kPa(a)). Converter high-temperature trips, K-502 and K-701 trips
are left for S4 and the HAZOP.
Relief: PSV-1911 (V-501), PSV-1912 (V-502), PSV-2010 (V-701) to the flare header, PSV-2210 on the
MP steam header to atmosphere through a silencer; drawn as globe valves and made
SpringLoadedGlobeSafetyValve by hand as in D-027; listed in `piping/special-items.yaml` without
set pressure (S8). Whether ammonia reliefs need a separate NH3 flare system is open (S8).
Changes to earlier sheets (S3a/S3b), texts only: the off-page notes of SM-1005 (P-101), BW-1024,
BW-1025, FG-1010 (P-102), BW-1037, SM-1038, BW-1039, SM-1040, CWS-1041, CWR-1042 (P-103),
PC-1048, PG-1055, CWS-1052, CWR-1053 (P-104), the CW pairs of P-105 to P-107, PC-1083, PC-1084
(P-107), PG-1087, PG-1088, PG-1090 and the CW pair (P-108) now name the S3c sheet; six CW
connectors on P-103, P-104 and P-108 moved 3 mm inwards (`cheme move`) so the longer texts stay
inside the frame.
Not drawn yet (open, for the reviews and S4/S8): control valve block and bypass valves, vents,
drains and sample points, the converter start-up heater and catalyst reduction, K-502 and K-701
seal, lube oil and drives, the steam drum's internals and its own relief (inside U-801), the
deaerator relief, BFW pump minimum-flow line and spare, chemical dosing, refrigerant charge and
oil drain of K-701, the X-601 internals.
Reason: S3c of runs/plan.md; the split follows the loop's hot and cold parts, the refrigeration
package, the recovery package and the steam system.
Rejected: one sheet for the whole loop (too dense for A3 with the auxiliaries); drawing the
packages' internals as separate items (the flowsheet and the equipment list keep them in the
packages; splitting them would add items the PFD does not link).

## D-030 Control: loops, sequences, trips, narrative and philosophy (2026-10-29, S4)
Decision: the control records are written for the P&IDs as drawn in S3, PROPOSED for review and
the HAZOP (S6): `control/loops.yaml` with one loop per controller on P-101 to P-114 (38 loops,
three cascades TIC-1103/PIC-1101, AIC-1109/FIC-1110, AIC-1804/FIC-1201, two ratios on the load
setter FIC-1002: steam FIC-1006 and process air FIC-1201); `control/sequences.yaml` with five
sequences (SEQ-START-REF, SEQ-START-CO2R, SEQ-START-SYN, SEQ-SD-PLANT, SEQ-TRIP-FE);
`control/cause-effect.yaml` completed with delay, latching, reset and bypass for I-101 to I-107;
`process/narrative.md` (eight sections: the seven flowsheet blocks and the utilities) and
`control/philosophy.md` (seven objectives, six failures). The strategy follows the usual practice
of a natural-gas reforming ammonia plant (the guidance of skill `control-loops`, after Toghraei, *Piping and Instrumentation Diagram Development*, Wiley 2019,
ch. 14): one load setter, steam and air as ratios to the gas, slow H2/N2 trim of the air at the
converter, furnace fired on fuel pressure reset by the reformer outlet temperature, excess air by
O2, anti-surge on every compressor, temperatures by bypasses of the process exchangers and by
the cooling water of the utility coolers, levels on the outlet valves between pressure levels.
P&ID change: the converter-feed analyser AI-1804 (P-109) is renamed AIC-1804 (`cheme rename`,
tag, labels and ids) and its note text updated, because it is the master of the process air
(D-026 asked for the trim; the P-103 note already said "FIC-1201 setpoint from the H2/N2
ratio"); the instrument list follows. No other sheet changed.
Setpoints: where a setpoint is a value of the design case it names its stream and property, so
`cheme validate` keeps the two in step (17 loops); the rest are ASSUMED here: levels 50 % of
span; anti-surge control line 10 % in flow from the vendor's surge line; furnace arch draft
-25 Pa(g) (balanced draft; the flowsheet gives the radiant box 103 kPa(a), a value of the
concept balance, not a draft); lean solvent 313.15 K (the absorber temperature of D-009); minimum
burner fuel pressure 150 kPa(a) (low limit of PIC-1101 until the burner vendor gives it); LP
steam to X-601 657 kg/h (Q29 386.8 kW over 2120 kJ/kg, the heat of vaporisation of water at
450 kPa(a) and 421 K, from thermo's pure-water correlations in cheme's interpreter); ratios 3.146 kg/kg steam and 2.277 kg/kg air from S6/S3
and S12/S3; O2 1.69 mol% wet from S66; H2/N2 3.0 from S42 (3.007 simulated).
Fail positions (each for the HAZOP to confirm): feed gas, fuel, tail gas, process air, purge and
make-up valves closed; process steam open (too little steam forms carbon); combustion air damper
open; anti-surge valves open; cooling water valves open; level valves between pressure levels
closed (blow-by), except the reflux LV-1506 (open, no pressure step) and the BFW and deaerator
make-up valves (open, the boilers keep their water); the shift bypasses TV-1207 and TV-1601
closed (cooler bed inlet), the converter bypass TV-1803 open (cooler converter feed); the MP
export PV-2203 closed (process steam keeps priority, PSV-2210 is the relief of a blocked export);
the ID fan drive holds its last speed. Trip delays 2 s (3 s for the furnace pressure, 5 s for the
I-104 alarm), latching with manual reset, timed start-up bypasses for I-105 and I-107 (ASSUMED,
usual practice). I-104 no longer opens LV-1307: a trip acting on the control valve of the loop
it backs up is not independent of it; it is an alarm until the HAZOP decides on a feed trip.
Sequence step times and start-up rates (30 % of the design gas and steam, 60 % load before
shutdown, 673 K reformer outlet before steam) are ASSUMED and are not a licensor's procedure.
Open (for the design review, the HAZOP and the P&ID revision): the sequences need connections
the P&IDs do not show: start-up nitrogen to the reformers, a front-end vent to flare (start-up
before the CO2 removal, a K-501 trip) and the converter start-up heater; four sequence actions
name them as text (`cheme.control-logic-text`, info). Also open: burner management of H-101 and
the fuel/air cross-limit; tube skin thermocouples; a three-element steam drum level control and
a drum low-low trip; BFW pump spare; machine protection (seal, lube oil, vibration) of K-101,
K-501, K-502 and K-701 inside the vendor packages; no loop pressure control (the loop floats on
the conversion, the purge is set by the operator); no analyser on the feed gas; no turndown case
in the flowsheet, so part-load behaviour of the loops is not checked; SIL screening (S6).
Open for the HAZOP (S6), added in the S5r fix (reviews 2026-10-29-design#2, #3, #5; no
interlock is proposed here because each needs sensors and valves that the P&IDs do not draw yet,
and the HAZOP is to decide whether it is wanted): (1) a converter R-501 bed high-high
temperature trip on TI-1805..TI-1808 (catalyst damage, hot spot and hydrogen attack of the
15 MPa shell), and the K-502 and K-701 trips that D-029 left for S4 and that S4 did not add;
(2) gas blow-by from V-502 (2500 kPa(a)) into V-701 (110 kPa(a)) on loss of the V-502 level:
LV-1907 failing closed and PSV-2010 are the only layers, unlike I-107 on the V-501 let-down;
either a V-502 low-low trip (LZ and an XV on the liquid outlet) or PSV-2010 sized for the full
LV-1907 gas capacity (S8), with the reason; (3) the same question for V-201 into the process
condensate system (LIC-1307 failing closed is the only layer; I-104 alarms only).
Reason: S4 of runs/plan.md.
Rejected: a loop pressure controller on the make-up (K-501 capacity) without a turndown case to
size it; a separate H2/N2 controller acting directly on FV-1201 (it would fight the ratio);
opening the anti-surge valve UV-1703 from I-103/I-106 (UIC-1703 does it as a loop, and a trip
sharing the loop's valve is not independent).

## D-031 Basic 3D layout, zones, lifting study, take-off and TEA gate (2026-10-29, S5)
Decision, racks: the concept rack PR-1 (D-022) left most nozzles more than the 30 m rack reach
from it (34 `direct` fallback routes, 6 process lines unrouted, 98 clash and headroom findings).
Area racks in a comb on PR-1 (`layout/site-plan.yaml`, positions, widths and tiers ASSUMED):
PR-2 (A-100, east-west at y 142 between the reactor row and the furnace), PR-3 (A-100 east edge to
K-101), PR-4 (A-200, east-west at y 162 between the exchanger row and the columns, over R-6 to
PR-5), PR-8 (A-200 east edge), PR-5 (A-800, west of U-801, 8 m, three tiers), PR-6 (PR-1 to the
south rack at the west edge of A-500), PR-7 (south rack at y 55 through A-600, A-500 and A-700,
over R-5 and R-6), PR-10 (west connector from PR-7 over PR-1 to PR-2, east of X-601), PR-11
(S5r fix, review 2026-10-29-layout#2: east connector from PR-7, extended to x 338, up to PR-1 at
the east edge of A-700; the A-500/A-700 exports had run west to PR-6 and back east on PR-1:
AL-1128 432 -> 77 m; the rerouted PC-1048 and PC-1084 met BD-1141, BW-1025 and SM-1040 in A-800
and are pinned clear of them; pipe 10,875 -> 10,687 m, steel 539 -> 554 t). East-west
racks carry their tiers at 6/8(/10) m, north-south racks at 7/9(/11) m, so lines change
elevation where they change direction; bent spacings are chosen so that no bent stands in a
road or among the lanes of a rack it joins. Moved for them: K-101 9 m west, E-301 3.5 m north,
V-502 3 m south. Toppling (1 x height, D-022) is kept as a criterion to the main rack PR-1 only
(measured: C-301 58.5 m, R-501 29.2 m, X-601 41.0 m); the area racks stand next to the columns
as in a rack-type layout (C-301 to PR-4 7.5 m, R-501 to PR-7 15.2 m, X-601 to PR-7 2.0 m): open
for the QRA and the owner's spacing standard.
Decision, routing (`piping/routing.yaml`): battery limits at the PR-1 ends (natural gas and
demineralised water west; NH3 product, steam export, blowdown and the flare header east;
ASSUMED: the flare, storage and utilities are outside the boundary, D-001); the CO2 vent stack
represented by its foot north-east of V-302; FLR-1146 starts at V-201, its first tie-in (the line
list's "relief valves" left the header with no end to start from); the furnace ductwork
(CA-1012, CA-1013, FL-1014 to FL-1021, DN 1800-4000) skipped as package scope (the coil banks
stand in the flue gas duct, D-022); nozzle orientations of U-801, H-101, the convection banks,
E-202, E-301, V-201 and X-601 set towards their racks (ASSUMED until vendor drawings); vias for
AM-1061 and PA-1022, the relief lines PG-1119/PG-1120/AG-1134 at 9.6 m over the vessel
platforms, the CO2 vent and relief outlets raised clear of the platforms (`vents`); six
routes pinned after review, four of them corrected by hand where they met another line at a
rack junction (NG-1001, BD-1141, SL-1135, PC-1136; the comments in the file say where).
Result: every DN 25+ process line routed or skipped with a reason; no pipe, steel, equipment or
headroom clash; 186 generated and 6 pinned pipes, 10,875 m of pipe in the take-off; 3 chains
still `direct`/`rack+direct` without a clash (review). Utilities (cooling water) stay unrouted
for the detail gate.
Decision, access: the platforms the build proposed for nozzles and valves above 2.5 m are
declared at their elevations; arcs stop 8 degrees short of a pipe crossing them below 2.1 m;
the top platforms of V-201, V-501 and V-701 lowered under the pipes leaving their heads (6.0,
5.8, 5.8 m); three low platforms that served only a piped flange left out (C-301 N6, C-302 N4,
R-501 N2: mobile platform). Left as review findings, not gate items: 31 operability, 11 escape
ways (one ladder on long platforms), 13 access-blocked, 74 free-span and 63 support-missing.
Decision, zones (`layout/zones.yaml`, screening, radii from the package table, ASSUMED):
zone 2 around the K-501/K-502 and K-701 seals (ammonia drawn as flammable gas until the
competent person decides) and the natural gas flanges of V-101/R-100; an oxygen-deficient zone
around the CO2 vent CO2-1068 and the CO2 relief outlet CO2-1076. Not a classification.
S5r fix (review 2026-10-29-layout#4): zone 2 also at the flanges and valves of the synthesis
loop (R-501, E-501..E-505, V-501, V-502 at its let-down valve), the purge gas recovery X-601
and the ammonia items V-701 and E-701, same table and grade; the rebuilt model reports no zone
finding. S5r fix round 2 (review 2026-10-29-layout#4): the H-101 fuel-gas (FG-1002: PV-1101,
XV-1102) and tail-gas (FG-1010: XV-1105) valve trains get zone 2 Z-HAZ-FUEL with the burner
inlet nozzles H-101/B2 and H-101/B1 as their sources (a line source must have an open end, so
the line numbers cannot be used); same table and grade, ASSUMED until the burner-management
package places its trains; no zone finding after the rebuild.
S5r fix round 2 (review 2026-10-29-layout-r2#1): the pins of PC-1048 (P-113) and PC-1084
(P-113) fall towards U-801 without a pocket: PC-1048 stays at 9.07 m from the PR-1 tier
change to the north-south run (the 6 cm low point at 9.01 m is gone); PC-1084 drops from its
8.0 m run to 6.5 m below the A-800 lines instead of rising to 9.5 m, then to its 5.5 m nozzle
(1.5 m high point gone); no clash. The older hand pins of layout#8 are unchanged.
Decision, lifting: screening empty weights for every item (`scripts/estimate_weights.py`:
thin-wall shell at 1.1 x operating pressure, CS 138 MPa, factors for internals; envelope
densities for machines and packages; lift weights for the field-erected furnace and the
packages; all ASSUMED), 14 crane pads (40 m working radius, no crane chosen) and 12 laydowns
within 30 m of their pads. S5r fix (review 2026-10-29-design#4): the shell pressure is now the
higher of the item's notes and the design-case pressures of the streams at the flowsheet step
linked to it alone (both sides for an exchanger, the outlets for a vessel fed through a let-down
valve; a step standing for several items, CO2R, is not used), so the loop exchangers are taken
at 14,750-15,500 kPa(a) (E-501 167.5 t instead of 13.0 t, E-502 168.8 t, E-504 133.0 t) and the
shift, methanation and prereformer items at 2950-4150 kPa(a). S5r fix (review
2026-10-29-layout#1): E-401 had no pad within reach; CP-204 added between PR-1 and E-401.
`layout/lifting-study.*`: every heavy item now has a pad and a laydown; **26 lanes are blocked**
by piping (often the item's own connections, E-401 by PC-1083 and PG-1079, V-701 by AL-1128 and
AL-1129 since they leave east to PR-11) or neighbours over
the item (H-101 by R-101 on its roof: an erection-sequence question the rule cannot see). Not
accepted: the gate `lifting-study` fails until the lifting plan reroutes or sequences them.
Decision, cost: `estimate/mto.*` written (gate `mto` passes). What the take-off leaves out
(S5r, review 2026-10-29-layout#3), so that no estimate reads it as complete: pipe classes and
insulation (the line list carries no `pressure_class` or `insulation` yet, so every pipe is
`bare` without a class, including the cold liquid ammonia AL-1128 and the hot reformed-gas and
waste-heat lines; classes and insulation by service come with the line list revision and
`piping/pipe-specs.yaml` at the datasheets, S7); the cooling water headers (unrouted until the
detail gate); the furnace ductwork CA-1012, CA-1013, FL-1014..FL-1021 (package scope); small
bore below DN 25, supports and the field-run vents and drains. Until then a bulk estimate built on
it must carry these as allowances, not as zero. The class 4 estimate is **not
done**: the bulk take-off has no sourced unit rates (`estimate/rates.yaml` is still the example),
and the equipment estimate (`cheme assess equipment`) covers 13 of 52 items, purchased cost only:
exchanger areas, compressor fluid powers, fan flows, pump powers and materials come with the
datasheets (S7), and no CEPCI value with an exact source was found in this job. The TEA keeps
the class 5 capital of D-023. Gate `tea` enabled as the template documents it; the vented CO2
and the flue gas are listed `free` (their CO2 is charged under `emissions:`, a price would count
it twice). The three utilities without a price (open since D-023 and review
2026-10-29-concept#2) are priced in the S5r fix on this design's premises, all ASSUMED, no quote:
demineralised water 2.0 EUR/t bought at the battery limit (swing 0.5-2.0); heat to cooling water
-2.85 EUR/MWh, the cooling tower's operating cost outside the boundary (pump 40 m at 0.75 and
fans at 150 Pa and 0.65 for the D-012 10 K rise, 0.0173 MWh(e) per MWh at the feed:POWER price,
plus make-up at 5 cycles of concentration and 0.60 EUR/t raw water including treatment; the
calculation is in the price's source); blowdown `free`, ASSUMED to go to the cooling-tower make-up
outside the boundary. The LCOP rises from 738.6 to 748.2 EUR/t.
Reason: S5 of runs/plan.md; review 2026-10-29-design#1 (a).

## D-033 Crane lanes cleared by design (2026-10-30, S5b)
Decision: of the 26 lanes blocked in S5, 15 are cleared by layout changes, without accepting
any:
- **13 crane pads beside the items**, on their clear side, so that the lane runs over the item
  only. They were searched with core's own lane rule (`scripts/pad_search.py`, provenance only,
  run with `cheme run scripts/pad_search.py`; it was in the ignored build/ until the S5b fix,
  design-s5b#3). The pads are CP-105 (E-103), CP-106 (K-102), CP-107 (K-103),
  CP-108 (E-105), CP-205 (R-201), CP-206 (R-401), CP-207 (E-201), CP-208 (E-202), CP-209
  (E-203), CP-210 (E-401), CP-504 (K-502), CP-505 (E-503) and CP-506 (V-502). Each is 10 x 10 m
  on open ground (no rack, structure, building, equipment or pipe below 4 m in plan), and each
  is ASSUMED like the S5 pads.
- **Laydowns**: LD-104 (beside CP-107, for K-101 and K-103) and LD-204 (beside CP-205, for
  R-201) are new. LD-202 moved 18 m east and LD-503's west edge moved 6 m east, so that no
  laydown lies on a pad.
- **PG-1120** (V-502 relief to the flare header) now runs at x = 246 m, west of V-501, instead
  of over it (piping/routing.yaml).
- **E-504** was tried 2 m north, which cleared the PR-7 bents from its lane, but the reroute
  that followed put PG-1107 under the V-501 platform (`layout-headroom`). It stays at
  (235, 60).

S5b fix (review layout-s5b#1, #2): three of the 11 lanes left were blocked by small routed
lines, not by the item's own piping, and are now cleared by re-routing them:
- **AL-1129** (DN 25 recovered NH3 from X-601) leaves PR-7 at x = 326 m, east of V-701, and drops
  to the T1129 tee at grade, instead of running north along the drum's crown at 8.85 m. New pad
  CP-703 (8 x 8 m) south of V-701 between PR-7 and the drum.
- **DW-1073** (DN 25 DMW make-up) leaves PR-4 at x = 230.5 m, east of X-401, runs north at
  sleeper height (0.6 m) and reaches V-302 from the north, instead of running north at 8.85 m
  over E-301, E-302 and E-303. New pads CP-211 (E-301) and CP-212 (E-303), 8 x 8 m, between the
  exchanger row and X-401.
- **LD-204** moved 2.5 m east, off access road R-5 (x 152-158).
The build reports no clash or headroom finding after the change; the two lines get the
generic free-span support proposals (layout#8 kind, detail).

The 8 lanes left are blocked by the item's own piping, the adjacent exchanger's piping, the
PR-7 bents (E-504) or, for H-101, its own catalyst tubes and headers. `scripts/pad_search.py`
finds no open-ground pad that clears them; only the erection sequence does: H-101, E-104,
E-402, K-501, E-501, E-502, E-505, E-504. E-402's blockers PG-1056 and PG-1077 are process
lines between C-301, E-401 and E-402, a larger re-route than a utility via.
They are listed for the owner, with the lifting plan's reason for each, in
build/lifting-acceptance-proposal.md (copied into the PR). None is accepted, so the gate
`lifting-study` fails until a competent person decides. No crane chart exists yet: a
manufacturer's load chart is a third-party table that may not be copied into the library, so
the chart has to come from the crane contractor or the owner. The
heaviest lifts, R-501 (658 t) and C-301 (514 t), need a crawler crane of the 1,000 t class.
Reason: S5b item 2 (runs/interventions.md O-032); review 2026-10-29-design#1 (b).

## D-034 Reactor model basis sourced; feed basis left open (2026-10-30, S5b)
Decision: the specified conversions of R100, R102A, R401 and H101 keep their D-005 values
(1.0), now `given`, each with its published source and locator in process/reactions.yaml:
- **Prereformer, C2H6/C3H8**: EP 1586535 A2 (Air Products, 2005), para. [0003]: substantially
  all higher hydrocarbons are converted.
- **Secondary reformer burner, O2**: Al-Dhfeery & Jassem (2012), Int. J. Ind. Chem. 3:14, p. 2.
  Complete O2 consumption in the combustion zone; their model is checked against plant data in
  Table 2.
- **Methanation, CO and CO2**: BREF LVIC-AAF (2007), §2.2.3.6, p. 42: usually below 10 ppmv left.
- **Furnace, hydrocarbons**: AP-42 §1.4, Table 1.4-2, footnote b: about 100 % of the fuel carbon
  goes to CO2.
- **Furnace, NH3**: Lin et al. (2024), Engineering 40, doi:10.1016/j.eng.2024.06.003: below 1 ppm
  NH3 at the furnace outlet.
- **Furnace, H2**: complete burnout is an inference. The secondary-reformer source shows H2 burns
  even with O2 limiting, and the furnace runs with 10 % excess O2. No source measures it directly.

`cheme maturity`: `balanced.model-basis` passed with these six.

S5b fix (review design-s5b#1): the last two entries were relabelled `assumed`. The H2 entry is
an inference, and the NH3 source is a coal boiler co-firing NH3, an analogy for traces of NH3
in the tail-gas fuel; neither is a published fact for this duty. Values unchanged (1.0), so no
stream changes. `balanced.model-basis` now fails again on exactly these two: H101 H2_COMB and
NH3_COMB. What would close it is a published source that states fuel H2 and NH3 burnout in an
excess-air fired heater or furnace. None was found in this job, so this is left open and is not
relabelled.

What was tried and left out:
- **Sourced feed basis.** I tried the EBTF (2011) Table 2-2-3 natural gas (with i/n-butane and
  i/n-pentane) and the U.S. Standard Atmosphere 1976 air, rescaled the feed and fuel, and ran
  DWSIM to convergence. That needed 2 % more fuel for the convection coils. The packages script
  (`scripts/packages_on_simulated_duties.py`) then gave boiler duties of 197.5 MW (130 MW before)
  and a chiller duty 21 % higher. These jumps are not explained, and the job's budget did not
  allow tracing them or carrying them through the PFD, datasheets and TEA. The change was
  reverted, and the flowsheet is as before.
- **Gibbs and equilibrium models for H101.** Both were tried as alternatives to sourced
  conversions. Core's `propagate` reports "no step lowers the Gibbs energy" for the Gibbs model,
  and no Newton convergence in 200 steps for the equilibrium model (combustion K is very large).
  Reverted to conversion.

Still open: `sourced.boundary`. The flows of S1 (natural gas), S12 and S61 (air) and S26 and
S70 (demineralised water) are design results: the radiant balance, H2/N2 = 3, 10 % excess O2
and the water balances. Their compositions are ASSUMED (D-004). A published composition exists
(EBTF, above). No published source gives these flows for this flowsheet. Recording them as
`given` would need an owner's specification of the gas, air and water rates (as asu-1's owner
gave its air rate). The agent may not invent one. BREF Table 2.6 (EFMA 2000: 22.1 GJ/t feed,
7.2-9.0 GJ/t fuel, LHV) is a check on the design: feed 21.8 GJ/t, fuel 6.1 GJ/t plus tail gas.
Reason: S5b item 1 (O-032); reviews 2026-10-29-simulation#1, 2026-10-27-pfd-lci-review#3.

## 3. Results of this stage (design case)

Basic stage, S2 (the simulated flowsheet, D-026; lca/inventory.csv regenerated): per kg of NH3
product (62,470.7 kg/h), before allocation: natural gas 0.6037 kg, ambient air 3.723 kg,
demineralised water 1.706 kg, electricity 0.586 kWh, heat to cooling water 2.185 kWh; outputs
MP steam 0.962 kg, blowdown 0.049 kg, CO2 to air 1.564 kg. With the exergy allocation of D-021
(NH3 94.3 %, steam 5.7 %) the inventory gives 1.475 kg CO2 per kg NH3, gate-to-gate direct
fossil CO2 only (lca/results.md: a partial screening carbon footprint, backgrounds missing).
Concept stage, for comparison: natural gas 0.6034 kg, electricity 0.563 kWh, MP steam 0.881
kg, CO2 1.563 kg per kg NH3. These are the outputs of one design on assumed inputs, not
validated performance figures.

## 4. Model and dependency table

Concept stage (D-006), superseded for the simulated part by S2 (D-024, D-026; table below):

| item | model / basis | status |
|---|---|---|
| reformers, shifts, converter | equilibrium (cheme), approaches ASSUMED | calculated by cheme |
| prereformer, burner zone, methanator, furnace | complete conversion (cheme) | calculated by cheme |
| flashes (loop separator, let-down) | thermo PR + ChemSep kij in the script | ASSUMED, unqualified (core #315) |
| water knock-outs, CO2 removal, dryer, HRU, vent | specified splits in the script | ASSUMED |
| duties, compressors, steam, refrigeration | script: cheme ideal-gas enthalpies, PR, IAPWS-IF97 | ASSUMED; energy closure not evaluable in core |
| stream properties (`props --fill`) | no package covers the mixtures (water, NH3 mixtures, hot CO/CH4) | gated: core #315 |
| rigorous simulation (`process simulate`) | not attempted: needs a method accepted for syngas/NH3/water | gated: core #315 |

Basic stage, S2 (core v1.0.1, DWSIM 9.0.5, Peng-Robinson):

| item | model / basis | status |
|---|---|---|
| REF (without H101), SHF, CO2R, MET, SYN, PGR | DWSIM, one solve, 7 tears converged | calculated (`simulate --fill`) |
| equilibrium reactors R101, R102B, R201, R202, R501 | DWSIM equilibrium; the adiabatic beds at their outlet temperature, duty the check | calculated; approaches ASSUMED |
| conversion reactors R100, R102A, R401 | complete conversion, DWSIM | calculated; conversions ASSUMED (unsourced) |
| flashes V201, V401, V501, V502, V701, V702, V703 | DWSIM PR flash (DWSIM's kij) | calculated; kij unsourced (D-025) |
| CO2 removal, dryer, NH3 wash, cold box | specified splits (component separators) | ASSUMED recoveries (D-009, D-010, D-013) |
| furnace radiant section H101 | complete combustion, `propagate` from the simulated S64 | calculated by cheme; fuel from the concept |
| steam system U801, chiller refrigeration K701 | scripts/packages_on_simulated_duties.py on simulated duties | ASSUMED |
| stream properties (`props --fill`) | syngas-pr-vapor for 6 of 121 streams | calculated where covered; rest gated: core #315 |
| plant energy closure | not evaluated with component separators | unsupported: core #60 |

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
| IEA Ammonia Technology Roadmap (2021); Mayer et al. (2023); Lee et al. (2022) | issue comments | no | not used (design-visible benchmarks; kept out). Also kept out: Musa et al. (2025), Sci. Rep. 16:661, whose SMR CAPEX is back-calculated from Lee et al. (2022) |
| Gasunie Transport Services, "The transmission network" and "Gas quality and metering" / FAQ pages | gasunietransportservices.nl/en/network-operations/the-transmission-network; .../connected-parties/gas-quality-and-metering | yes (2026-10-29) | I-01/R-03: no public composition for a connection; HTL carries H-gas, RTL almost only G-gas |
| IEAGHG Technical Report 2017-03, Techno-Economic Evaluation of HYCO Plant Integrated to Ammonia/Urea or Methanol Production with CCS (Amec Foster Wheeler), Feb. 2017; free download, all rights reserved (numbers used, nothing copied) | Case 4A-1, Table 1 (report sheet 26 of 80); section 2.8.1 | yes (2026-10-29, read by a research sub-agent of this job) | D-023: reference installed cost, OSBL, owner's cost, contingency |
| Eurostat nrg_pc_203, nrg_pc_205, ert_bil_eur_a, sts_inppd_a (CC BY 4.0) | NL, bands I6 / IG, excl. VAT, 2024-S1 to 2025-S2; USD per EUR 2025; PPI NACE C28 2014 and 2025 | yes (API, 2026-10-29) | D-023: gas and electricity prices, exchange rate, escalation |
| USGS, Mineral Commodity Summaries 2026, Nitrogen (fixed)-ammonia (public domain) | salient statistics, price f.o.b. Gulf Coast, 2025e | via the search index of the document (the PDF text could not be extracted here) | D-023: NH3 price proxy, ASSUMED |
| ESMA annual report on EU carbon markets 2026, as reported by Lovguiden (2026-07-09) | EUA annual average 2025 | secondary only | D-023: carbon price, ASSUMED |
| NIST Chemistry WebBook | standard enthalpies of combustion of CH4, C2H6, C3H8 | values used | D-023: gross calorific value of the D-004 gas |

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

### Concept close-out (S1, 2026-10-29)

Each open input is either resolved or kept ASSUMED, with the reason and where it is taken up:

| input | status at concept sign-off | reason | taken up in |
|---|---|---|---|
| I-01 natural gas | **kept ASSUMED** (benchmark lean gas, 4500 kPa(a), 288.15 K) | no open, citable composition exists for an H-gas connection in the Rotterdam area: GTS supplies composition data per connection as a customer information service, and its public network description says only that the HTL main network carries H-gas and the RTL almost only G-gas, with no composition or pressure figures (gasunietransportservices.nl, "The transmission network" and "Gas quality and metering"/FAQ pages, read 2026-10-29). A different gas would need a rerun of scripts/plant_balance.py and a regenerated LCI (R-03 below) | S2 (the flowsheet is re-solved by simulation; owner's gas quality or a measured GTS composition) |
| I-02 brief | kept: the #86 proposed brief is the basis | only the owner can freeze it; no change proposed | owner, before basic sign-off |
| I-03 ambient, cooling water | **kept ASSUMED** (ISO ambient, CW 298/308 K) | site data change the balance; the plot plan (D-022) also needs the wind rose | S2 (simulation cases) and S5 (layout) |
| I-04 approaches, kinetics | **kept ASSUMED** | reaction evidence not gathered; it is also what `cheme maturity` (`balanced.model-basis`) asks for | S2 |
| I-05 HDS recycle, dryer regeneration, condensate stripper | kept: not modelled | small flows; they come with the simulation and the P&IDs | S2, S3 |
| I-06 CO2 removal | **kept ASSUMED** (D-009) | licensor data or a solvent model is not available in this run | basic (licensor) |
| I-07 emissions not quantified | kept NOT ESTIMATED, declared in `emission_exclusions` (D-020) | no sourced factor or guarantee; never set to a silent zero | basic (burner and licensor data) |
| I-08 HRU recoveries | **kept ASSUMED** (D-013) | vendor data | basic |
| I-09 drives | kept: electric drives (D-016) are the concept base | the comparison with steam turbines is a design alternative, not needed to close concept; the screening TEA (D-023) shows the weight of electricity | basic, as a branch alternative |
| I-10 LCI backgrounds | kept missing (D-020) | licensed backgrounds may not be copied into the library; linking them is outside S1 | LCA stage |

Review 2026-10-27-pfd-lci-review: closing or carrying each finding (the reviewer of this branch
records the status; an author does not close a finding in someone else's record):

| finding | response | evidence |
|---|---|---|
| R-01 (medium) | fixed, for closing: D-020 and process.yaml `validation.notes` say the printed figure is gate-to-gate direct fossil CO2 only, not a footprint | commit 7ac6c8b; the run report is a run record and is not edited |
| R-02 (medium) | fixed, for closing: `emission_exclusions` for H-101 and the C-302 CO2 vent (I-07); the CH4, H2, C2H6, C3H8 source texts say NOT ESTIMATED; `lci-emissions-incomplete [H-101]` gone | commit 7ac6c8b, `lca/lca.yaml` |
| R-03 (medium) | **carried** to S2 with the reason of I-01. Effect on `cheme maturity` (run 2026-10-29): calculation maturity none; `sourced.boundary` fails on S1 (natural gas) and also on S12, S61 and the other feeds whose flows are results of the balance, not given; `balanced.model-basis` fails independently on the unsourced specified conversions and splits (R100, R102A, H101, R401, C301, X401, X601). Sourcing the gas alone would therefore not raise the level | `cheme maturity` |
| R-04 (low) | fixed, for closing: `validation.notes` states that `cheme maturity` reaches no level and concept is the lowest manifest value (D-019) | commit 7ac6c8b |
| R-05 (low) | **carried**: the D-006 note (read step extents; block extents of a dependent reaction set are not unique) is in; reporting it to cheme-as-code core is the orchestrator's (runs/plan.md: one core issue per platform problem, linked in the ledger), which this job cannot do | commit 7ac6c8b |

Chemicals registry entries missing (to add in the consolidated PR, not here): `ammonia` (with
a refrigerated anhydrous liquid grade), `natural-gas`, `ethane`, `propane`, a demineralised
`water` grade, an MP `steam` grade at 46 bar(a) / 673 K; optionally `flue-gas`.
