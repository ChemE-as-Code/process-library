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
Reason: the brief asks for the whole plant simulated and converged on v1.0.1; every change
above is a modelling necessity or a retune of an ASSUMED design choice, recorded here.
Rejected: loosening tolerances or tears, writing simulated values by hand, keeping the
concept's loop values where the simulation covers them.

## 3. Results of this stage (design case)

Per kg NH3 (lca/inventory.csv, from the flowsheet): natural gas 0.6034 kg (process 0.4721,
fuel 0.1313), ambient air 3.723 kg, demineralised water 1.623 kg, electricity 0.563 kWh,
heat to cooling water 2.104 kWh; outputs 1 kg NH3, MP steam 0.881 kg, blowdown 0.047 kg, CO2
to air 1.563 kg (process vent 1.173, flue gas 0.390). Inventory mass balance: in 5.94962 kg,
out 5.94970 kg; cheme reports mass, element and carbon-origin balances closed. These are the
outputs of one concept design on assumed inputs, not validated performance figures.

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
