# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
General-purpose polystyrene (GPPS) by continuous bulk polymerisation of styrene, issue
ChemE-as-Code/process-library#467, coverage rank 54 (`polystyrene`). Concept stage: design
basis, balanced BFD/PFD with the recycle and the feeds solved by design specifications, an
independent balance script, an equipment list, a hand screening of the continuous reactors'
runaway and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA,
datasheets.

Starting point (2026-11-19): library `main` with the core pin 0e85885 (v1.12.0 with #254).
Styrene comes from `processes/styrene-1` (registry slug `styrene`, its LCI dataset). Core
features used: conversion reactors that write their own duties (core ADR 0059), component
separators with a specified recovery and design specifications that solve a feed and a purge
split together with a recycle tear (ADRs 0060, 0070). Templates: `oxalyl-chloride-1` (structure
and depth of a recent entry), `styrene-1` (a continuous entry with a balance script) and core's
`examples/process-design-spec` (a loop with a purge spec). Requires cheme-as-code 1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied (no table, figure or passage). "Read"
means the passage named was read in this work (the BREF's PDF, Google Patents' machine text,
Wikipedia, EBI OLS, the tables packaged in the `chemicals` Python package).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | European Commission JRC (2007) Reference Document on Best Available Techniques in the Production of Polymers (POL BREF), August 2007, https://eippcb.jrc.ec.europa.eu/sites/default/files/2019-11/pol_bref_0807.pdf | section 4.2.1 (pp. 72-74): one reactor or a train; heat removed by the incoming feed, by evaporating solvent or by a heat-transfer medium; the crude at 60 to 90 % solids heated to about 220 to 260 C and devolatilised under high vacuum in one or two stages, the monomer and solvent recycled; about 710 kJ/kg released (the double bond's heat of hydrogenation); density 0.905 (monomer) to 1.045 g/cm3 (polymer); 200 000 to 300 000 g/mol; initiation by heat or peroxides (below 1000 ppm); mercaptans as chain transfer agents; TBC 10 to 15 ppm in storage, at least 4 to 5 ppm; self-polymerisation in storage a runaway reaction; mineral oil 0 to 8 % in PS; no stabiliser needed in GPPS by continuous bulk polymerisation. Section 4.2.2 (pp. 75-77, Tables 4.4, 4.5): CSTRs and/or PFRs; styrene the solvent, up to 10 % ethylbenzene for better reaction control; 110 to 180 C; up to 1 MPa in a PFR, atmospheric or sub-atmospheric in a CSTR; 60 to 90 % conversion; one or two devolatilisers at 220 to 260 C and below 40 mbar, water stripping between them possible; condensed styrene and ethylbenzene recycled with a purge; strands cut dry or under water, dried, conveyed to silos; reactors 5 to 120 m3. Section 4.2.4 (p. 81): EPS by batch suspension polymerisation. Section 4.3.1 (p. 84, Table 4.10, APME 2002): per t of GPPS, among others VOC 85 / 120 / 300 g, wastewater 0.8 / 1.1 / 6 t, total energy 1.08 and 1.80 GJ, styrene 0.985 and 1.020 t, mineral oil 0.02 and 0.06 t, process water 0.596 and 0.600 t, nitrogen 0.022 and 0.050 t, cooling water 50 and 100 t; Table 4.11 (p. 85) the sources of the emissions. Section 13.3 (pp. 262-263, Table 13.6): BAT for polystyrene (storage emissions, purge streams and reactor vents recovered or oxidised, pelletising air treated) and the BAT-associated levels for GPPS | read; EU publication, reuse with acknowledgement, facts only | D-001 to D-012 |
| SRC-2 | US 8 912 296 B1, G. Bouquet, U. Reifert, N. M. A. Hermans (Styron Europe), priority GB 1122017.5, 2011-12-20, granted 2014-12-16: Process for preparing polystyrene having a high melt flow rate, https://patents.google.com/patent/US8912296B1/en | example: feed of 95.8 wt% styrene and 4.2 wt% ethylbenzene; an initial plug-flow reactor (three zones, about 66 min, 122 to 133 C, 30 ppm peroxide) and two downstream plug-flow reactors (about 54 min each, 140 to 170 C, n-dodecyl mercaptan added); 72 wt% conversion; a devolatiliser separates a recycle of styrene and ethylbenzene, used to make up the feed; Mw 147 000 g/mol; general description 200 to 300 C under vacuum | read (Google Patents); patent, facts only | D-004, D-005 |
| SRC-3 | US 4 017 498 A, B. Hopkins (Monsanto), filed 1975-04-18, granted 1977-04-12: Recycle control system for continuous polymerization, https://patents.google.com/patent/US4017498A/en | a horizontal stirred reactor of styrene at about 327 F (437 K) and 21 psia (145 kPa), about 65 % full; its vapour condensed in a reflux condenser and returned, the vapour rate setting temperature and pressure; effluent about 65 wt% polymer; a wiped-film devolatiliser at about 100 mm Hg (13 kPa) leaving about 1 wt% monomer; the condensed monomer recycled | read (Google Patents); patent, facts only | D-005, D-007, D-010 |
| SRC-4 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (core's environment), each value with the method that gives it: the CRC Handbook tables packaged in `chemicals` (`heat_capacity.CRC_standard_data`, `miscdata.CRC_organic_data`, `phase_change.Hvap_data_CRC`); critical temperatures from `chemicals.critical.Tc` (styrene: method CRC, the critical constants of the CRC Handbook, 95th edition, 2014; ethylbenzene: method HEOS, the values of NIST REFPROP's high-accuracy Helmholtz equations of state); ideal-gas heat capacities from `thermo.HeatCapacityGas` (styrene: method JOBACK, the group contributions of Joback and Reid, Chem. Eng. Commun. 57 (1987) 233; ethylbenzene: method HEOS_FIT, thermo's polynomial fit to REFPROP's Helmholtz equation of state); vapour pressures from `thermo.VaporPressure` (styrene: method WAGNER_MCGARRY, the Wagner coefficients of McGarry, Ind. Eng. Chem. Process Des. Dev. 22 (1983) 313; ethylbenzene: method HEOS_FIT); autoignition and flash points from `chemicals.safety` (method IEC 60079-20-1 (2010)) | styrene: Tb 418.45 K, 901.6 kg/m3, Cp(l) 182.0 J/(mol K), dHvap 38.70 kJ/mol at 418.15 K, Tc 635.0 K, vapour pressure 66.3 kPa at 403.15 K, autoignition 763.15 K, flash point 303.15 K; ethylbenzene: Tb 409.35 K, 862.6 kg/m3, Cp(l) 183.2 J/(mol K), dHvap 35.57 kJ/mol at 409.31 K, Tc 617.12 K (HEOS; the CRC table's 617.1 K), vapour pressure 85.6 kPa at 403.15 K, autoignition 704.15 K, flash point 288.15 K; water: Cp(l) 75.3 J/(mol K), dHvap 40.65 kJ/mol | open-source packages queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). The printed (licensed) handbook and REFPROP were not read | materials, D-005, D-006, D-008, D-010 |
| SRC-5 | Wikipedia, Polystyrene, https://en.wikipedia.org/wiki/Polystyrene | CAS 9003-53-6; density 0.96 to 1.05 g/cm3; glass transition about 100 C; heat capacity 1.3 kJ/(kg K) (the solid); made by addition polymerisation started by heat or peroxide; expandable beads by suspension polymerisation in water with pentane; food-contact polystyrene at most 1 % (0.5 % for fatty foods) styrene by weight | read; CC BY-SA, facts only | D-001, D-006, D-007 |
| SRC-6 | ChEBI via EBI OLS, CHEBI:53276 poly(styrene) | (C8H8)n, cross-reference CAS 9003-53-6 | read (OLS API, 2026-11-19) | registry |
| SRC-7 | processes/styrene-1, asu-1, hda-1 (this library) | the styrene feed (its product stream, 0.99849 mole fraction styrene with ethylbenzene); gaseous nitrogen; fired heat counted as heat absorbed | library, internal | D-003, D-011 |
| SRC-8 | US EPA AP-42, section 6.6.3 Polystyrene | - | not read (the download was refused, 2026-11-19); named by a search result as describing the continuous process and its emission factors | lead only |

Searched and not found openly (2026-11-19): a rate law of the thermal polymerisation of styrene
with its source read here, a measured heat capacity of the polystyrene melt between 400 and
520 K, the phase equilibrium of styrene and ethylbenzene over the polymer melt (Flory-Huggins
parameters), a plant's specific electricity and heat split, a residual-monomer specification of
a GPPS grade.

## D-001 Route and boundary (2026-11-19)
Decision: GPPS by continuous bulk (mass) polymerisation of styrene initiated by heat, in the
train SRC-1 describes (section 4.2.2): a stirred prepolymeriser R-101 boiling under vacuum with
a reflux condenser (SRC-3's stirred reactor), three liquid-full stirred tower reactors R-102 in
series (plug flow), the solution heated to 513 K and devolatilised in two vacuum stages (V-101,
V-102), the vapours condensed (E-103) and recycled with a purge (T-201), the melt pumped through
a die plate and pelletised under water with drying and conveying (X-301). Reaction: STY -> PS,
one kmol of repeat units per kmol of styrene (reactions.yaml).
Boundary: gate to gate, from styrene (styrene-1's product), process water, nitrogen and the
utilities to the pellets at the silos, the purge, the vacuum vent and the pelletiser's water.
Storage of styrene beyond the feed tank, packing materials and the silos' logistics are outside.
Reason: SRC-1 states that GPPS is made continuously in CSTRs and/or plug-flow reactors with
devolatilisation (sections 4.2.1, 4.2.2), and gives the conditions, the consumption and emission
levels and the BAT for it; the suspension process it describes is the EPS process (section
4.2.4). The continuous route is what core models best: conversion steps, component separators
and a recycle with design specifications.
Rejected:
- batch suspension polymerisation (the issue's alternative): SRC-1 names it for expandable
  polystyrene (EPS, with pentane, section 4.2.4), not for GPPS; it needs suspending agents, a
  stepwise temperature schedule, centrifuging, washing and drying of beads and a water phase
  several times the polymer, none of which this product needs. A candidate for a later EPS
  entry (`cheme process recipe`, `reactor: semibatch` with a reactor-hazards screening).
- peroxide initiation in the continuous train (SRC-1: none or organic peroxides, below 1000
  ppm; SRC-2 uses 30 ppm): it raises the line's rate at lower temperature but adds a feed with
  no library producer; a heat-initiated train is the simpler concept, and the conversion model
  does not distinguish the two (L-1).
- anionic polymerisation (SRC-1 names anionic initiation among the techniques): no open source
  with plant quantities was read.
- high-impact PS (rubber dissolved in the feed, SRC-1 section 4.2.3): a different product with a
  rubber feed that has no library producer.
- water stripping between the devolatilisers (SRC-1: possible): it lowers the residual monomer
  but adds a water-styrene separation to the recycle; two vacuum stages give about 520 ppm
  without it (D-007).
Assumptions: thermal initiation alone; no chain transfer agent, no mineral oil, no zinc stearate
or dye (SRC-1: 0 to 8 % mineral oil, additives about 0.005 t/t): the model's product is the
neat polymer (D-003).

## D-002 Capacity, product and operating hours (2026-11-19)
Decision: 100 kt/a of GPPS pellets (stream S14) in 8000 h, 12.5 t/h, ASSUMED: one line whose
reactors fall inside SRC-1's 5 to 120 m3 (D-005). The flowsheet's spec `rate` solves the fresh
styrene for it (ADR 0070). Product: the neat polymer with about 520 ppm styrene and
ethylbenzene (D-007), dried pellets at 323 K.
Reason: a single-line scale of the commodity polymer; no open market figure was used.
Assumptions: the residual-monomer level is the concept's, not a grade's specification (SRC-5
gives the 1 % limit for food contact as an upper bound).

## D-003 Feed (2026-11-19)
Decision: styrene from styrene-1 (SRC-7): 99.85 wt% styrene with 0.15 wt% ethylbenzene (its
product's mole fractions 0.99849 and 0.00151, taken as mass fractions: both have about the same
molar mass), at 298 K and 300 kPa(a) from T-101. The TBC inhibitor (10 to 15 ppm, SRC-1) is not
in the balance; an adsorber to take it out before R-101 is optional (SRC-1, Table 4.5) and is not
modelled. No initiator, chain transfer agent, mineral oil or additive is fed (D-001).
Result: 12 581.6 kg/h (spec `rate`), 1.006 kg of this feed per kg of pellets (S1 / S14), the
basis of the LCI and of the benchmark: the styrene in it is 1.0045 kg per kg of pellets, 1.0050 per
kg of polymer (scripts/ps_balance.py). Inside SRC-1's 0.985 to 1.020 t/t (D-012).

## D-004 Ethylbenzene diluent and purge (2026-11-19)
Decision: the reactor feed S3 holds 7 wt% ethylbenzene (spec `purge`, ASSUMED; SRC-1: up to
10 % for better reaction control; SRC-2: 4.2 wt%). No ethylbenzene is bought: what comes in
with the fresh styrene (18.9 kg/h) builds up in the recycle until the purge (X201, from the
recycle tank T-201) takes it out. Propagate solves the purge fraction, 0.01366 of the condensate
(74.0 kg/h, 77 % styrene), together with the rate and the tear S2 (converged in 2 Broyden
iterations to 1.5e-6 kg/h). The purge goes to the site's thermal oxidiser or is burned as fuel
(SRC-1, BAT 2).
Reason: the ethylbenzene lowers the solution's viscosity and the rate; the purge is the loop's
exit for it, and also for the dimers, trimers and other light impurities the model does not
carry (SRC-1: a purge of undesirable components).
Assumptions: 7 wt% sets the purge; at 10 wt% the purge would be 52.8 kg/h, 29 % smaller, and
the fresh styrene 1.6 kg per t of polymer less (scripts/ps_balance.py with the target changed).

## D-005 Reactors: conversion, temperature, pressure and heat (2026-11-19)
Decision: two conversion steps (core's `reactor: conversion`, ADR 0059 writes their duties):
- R101, the prepolymeriser R-101: 35 % of its inlet styrene at 403.15 K, boiling under 65
  kPa(a), about the solution's bubble pressure at that temperature: Raoult's law over its
  polymer-free volatiles (89.8 mol% styrene) with SRC-4's vapour pressures gives 68.3 kPa, and
  64.7 to 67.6 kPa with a Flory-Huggins solvent activity for an interaction parameter chi of 0
  to 0.5 (ASSUMED; polymer volume fraction 0.293), scripts/ps_balance.py; under 50 kPa(a) the
  solution would boil near 393 K. The heat of polymerisation goes to warming the cold feed
  (302.6 K) and, the rest, to the boiling: the vapour (87 mol% styrene) is condensed on cooling
  water in the reflux condenser E-102 from about 401 K, its dew point under 65 kPa(a), and
  returned. Q1 366.7 kW = 276.8 kW net heat of the step plus the agitator's 90 kW (P1).
- R102, the tower reactors R-102: 61.5 % of the remaining styrene, the temperature rising to
  443.15 K at the last tower's outlet (SRC-2: 160 to 170 C in its last reactor), liquid-full at
  400 kPa(a) (SRC-1: up to 1 MPa in a PFR); the heat by coils in a heat-transfer-oil loop to
  cooling water: Q2 1056.7 kW with the towers' agitators (P2, 90 kW).
Overall 75 % of the styrene fed (SRC-1: 60 to 90 %; SRC-2: 72 %); the solution leaves R-102 with
69.7 wt% polymer, 23.3 % styrene, 7.0 % ethylbenzene. The heat of polymerisation is SRC-1's
710 kJ/kg (73 948 kJ/kmol), taken at 298.15 K (the BREF states no temperature).
Sizes (equipment list, ASSUMED residence times, no rate law): R-101 about 75 m3 with 50 m3 of
liquid (2.5 h); three towers of about 20 m3 (about 3 h in all, SRC-2: about 2.9 h).
Reason: SRC-1's train and conditions; SRC-3's boiling stirred reactor removes the heat at a
temperature its pressure fixes, the inherent limit of the prepolymeriser (D-010).
Rejected: R-101 at SRC-3's 437 K and 145 kPa: a 65 wt% polymer solution in one stirred tank is
the viscous end of what a CSTR handles; the concept keeps the CSTR at low conversion and leaves
the viscous range to the towers. Tower heat used in E-101 (the oil loop at about 430 K cannot
heat the solution to 513 K; a part of it could preheat): heat integration not studied.
Assumptions: the conversions and residence times (no open rate law read, L-1); R-101's boiling
pressure rests on Raoult's law with an assumed Flory-Huggins chi, not on a measured
polymer-solvent equilibrium (L-3); in operation the pressure controller sets it, and with it the
temperature.

## D-006 Heat capacities (2026-11-19)
Decision: constant liquid heat capacities at 298.15 K (SRC-4): styrene 182.0, ethylbenzene
183.2, water 75.3 kJ/(kmol K); the polymer 182.0 kJ/(kmol K) per repeat unit (1.747 kJ/(kg K)),
ASSUMED equal to the liquid monomer's.
Reason: core's conversion model takes one heat capacity per component (L-2); no open measured
heat capacity of the melt was read. SRC-5's 1.3 kJ/(kg K) is the glassy solid's; the melt's is
higher above the glass transition.
Assumptions: the liquids' heat capacities rise with temperature, so the sensible heats between
300 and 513 K (the feed's warming in R-101, the heat-up in E-101, the melt's cooling in X-301)
are low by roughly 15 to 25 %: R-101's and R-102's cooling duties are then overstated, E-101's
and X-301's understated, by amounts of that order. The mixed feed's temperature, 302.61 K, is
the heat-capacity-weighted mean of S1 (298.15 K) and S2 (313.15 K) (scripts/ps_balance.py).

## D-007 Devolatilisation, condensation, vent and recycle (2026-11-19)
Decision: two flash stages at 513.15 K (SRC-1: 220 to 260 C), V-101 at 4 kPa(a) and V-102 at 1
kPa(a) (SRC-1: below 40 mbar), as component separators (`recovery:`, ADR 0070): 97 % of the
styrene and ethylbenzene to V-101's vapour, leaving about 1.3 wt% in the melt (SRC-3: about 1
wt% after one devolatiliser at 13 kPa(a)), then 96 % of what is left to V-102's vapour: 6.5 kg/h,
about 520 ppm, stays in the pellets. The polymer never leaves with a vapour. V-102's vapour is
raised to 4 kPa(a) by the booster K-101 and joins V-101's; E-103 condenses both on cooling water
to 313 K; the vacuum pumps draw the non-condensables (leak air, not modelled) from V-103 to the
thermal oxidiser with 0.02 % of the condensed volatiles, 1.08 kg/h or 86 g/t, set to SRC-1's VOC
level for GPPS (85 g/t, Table 13.6, which is after treatment: the vent's own load is an upper
bound we do not know); the condensate goes to the recycle tank T-201 and back to M101 (tear S2).
Reason: SRC-1's two-stage devolatilisation; the recoveries are what high vacuum at 513 K gives
in SRC-3's order of magnitude.
Assumptions: the recoveries (no polymer-solvent phase equilibrium in core, L-3); the booster's
heat of compression neglected (S10 at 513.15 K; its power is in P3, D-008's energy balance); styrene dissolved in the pelletiser's water
not modelled.

## D-008 Heat supply and the condenser (2026-11-19)
Decision: E-101, a vertical tube bundle on V-101 in which the volatiles flash, heats the
solution from 443.15 to 513.15 K on hot oil at 563/543 K from a natural-gas-fired heater; its
duty includes the latent heat of all the volatiles that leave V-101 and V-102 (V-102's jacket
lumped in): Q3 1043.8 kW (scripts/ps_balance.py: 608.6 kW sensible, 435.2 kW latent at 513 K,
Watson's correlation from the CRC heats of vaporization and critical temperatures, SRC-4). E-103
cools the vapours as ideal gas from 513.15 to 313.15 K and condenses them at 313.15 K: Q4 1108.7
kW (the enthalpy is a state function, so the path through the condensation at 313 K stands for
the real one at the dew point near 330 K under 4 kPa(a)).
Energy balance of the plant (scripts/ps_balance.py, the liquids at 298.15 K the reference): in
4169.0 kW (electricity 660.0, hot oil Q3 1043.8, heat of polymerisation 2465.3), out 4017.8 kW
(cooling water Q1, Q2, Q4 and Q5 3649.3, the products' sensible heat above 298.15 K 368.5); it
does not close by 151.2 kW (3.6 % of the input), all of it explained: (1) 300.0 kW of
electricity no modelled sink takes: the vacuum system P3 (120 kW), P5's dryer, conveying and
packing (160 kW) and 10 % of the gear pump's, cutter's and water pump's power, which leave to
the air and the vacuum pumps' own cooling (D-009); less (2) 148.8 kW by which E-103's path
exceeds E-101's for the same vapour S16: from liquid at 313.15 K to vapour at 513.15 K it takes
959.9 kW with the constant liquid heat capacity and Watson's heat of vaporization at 513 K
(Q3's path), 1108.7 kW with the ideal-gas heat capacities and the heat of vaporization at 313 K
(Q4's path). The second is the liquid heat capacities' understatement of D-006 in one loop: Q3,
and the hot oil, are likely low by up to that order.
Reason: core's separators and coolers do not write duties (L-4); the script gives them with its
own mass balance, which agrees with propagate's (12 581.6 kg/h, purge 0.01366).
Assumptions: ideal-gas heat capacities of `thermo` 0.6.1 (Joback's estimate for styrene); heat
losses neglected.

## D-009 Pelletising, process water, electricity and utilities (2026-11-19)
Decision: the melt gear pump P-201 (110 kW: 12.5 t/h raised by about 15 MPa, 52 kW hydraulic, at
50 % with the drive) feeds an underwater pelletiser; the pellets are dried in a centrifugal
dryer and conveyed to the silos (X-301, 250 kW with the water pump, conveying and packing). The
water loop is held at 323 K by a cooler on cooling water: Q5 1117.2 kW, the melt cooled from 513.15
to 323.15 K less the make-up warmed from 298.15 to 323.15 K (937.2 kW), plus the shaft work
that ends in the melt and the water, 180 kW: 90 % of the gear pump's 110 kW and of the cutter's
60 and the water pump's 30 kW (ASSUMED; the rest is the drives' losses to the air). Its make-up, 0.592 kg per kg of fresh
styrene (spec `rate`), gives 0.5956 kg per kg of polymer, SRC-1's 0.596 (Table 13.6), and
leaves as the loop's purge to wastewater treatment (S15). Electricity in all 660 kW (P1 to P5:
agitators 180 kW, vacuum 120 kW, melt pump 110 kW, pelletising, drying and conveying 250 kW),
all ASSUMED (the reactors' 180 kW are agitators with the reflux, feed and transfer pumps).
Cooling water 298/308 K.
Assumptions: the powers are concept estimates, and so is the share of them that ends in the
water; the rest of the electricity, 300 kW, is in no modelled sink (D-008's energy balance).

## D-010 Hazards of the continuous reactors (2026-11-19)
Decision: a hand screening, since core's `cheme process reactor-hazards` screens batch and
semi-batch reactors only (L-5). Styrene polymerises by heat alone and the heat (710 kJ/kg, SRC-1)
is large against the solution's heat capacity: 406 K per unit mass fraction of styrene
converted (710 / 1.747). If the cooling failed and the remaining styrene polymerised:
- R-101's content (60.4 wt% styrene) would rise 246 K, from 403 to about 649 K;
- R-102's outlet (23.3 wt%) 95 K, from 443 to about 538 K; its inlet, the R-101 content, 246 K;
- the reactor feed itself (93.0 wt%) 378 K.
These are ceilings of a cooling failure, not of a design (no rate law: no time to maximum rate,
no MTSR in the batch sense). R-101 is tempered by its own boiling: its temperature follows the
pressure, so a loss of E-102 or of the cooling water shows as a rising pressure with the
temperature, and the relief has to pass styrene vapour (and foaming polymer solution) at the
rate the polymerisation then boils it. R-102 is liquid-full and has no such tempering. Design
findings for basic engineering: (1) relief of R-101 and the towers for the cooling-failure case,
two-phase with a viscous liquid, to a catch tank and the thermal oxidiser; (2) interlocks: feed
stop and short-stop (an inhibitor injection) on high temperature or pressure of R-101 and each
tower, and on loss of agitation or of cooling water; (3) the recycle tank T-201 holds styrene
without polymer but hot from E-103's 313 K: it needs its inhibitor dosed and its temperature
held low (SRC-1: self-polymerisation in storage is a runaway; TBC needs oxygen present);
(4) air ingress into the vacuum system at 513 K (styrene vapour), and a leak of the process
liquid at 403 to 513 K, far above the flash points of styrene (303 K) and ethylbenzene (288 K),
are fire cases for the HAZOP, and so is a leak of the hot oil at 563 K by the oil's own flash
and autoignition points (the oil is not chosen). The process's and the oil's temperatures stay
below the autoignition temperatures of styrene (763 K) and ethylbenzene (704 K) (SRC-4): an
ignition needs a source, which the hazardous-area classification has to exclude. The polymer dust from pellet
conveying (SRC-1: 2 to 7 g/t) is a dust-explosion case for the silos.
Assumptions: the heat capacities of D-006 (a higher melt heat capacity lowers the rises by up to
about a fifth).

## D-011 LCA (2026-11-19)
Decision: a preliminary gate-to-gate inventory per kg of pellets (lca/lca.yaml), one product (no
allocation). Linked by the library's LCI build (lca/mappings.yaml): the styrene to styrene-1's
dataset, the hot oil's heat as heat from natural gas (kWh absorbed, as hda-1), the nitrogen to
asu-1; electricity, cooling water, wastewater and the process water through the shared entries
(the process water as `water`, deionised water: a conservative proxy for the pelletiser's
make-up, ASSUMED). Gaps (never 0): the purge's and the vent's thermal oxidation, the nitrogen's
release. Nitrogen:
SRC-1's 0.022 kg/kg (2200 t/a), ASSUMED for this plant, as a consumable leaving with the vents.
The purge and the vent are waste treatments under cut-off. Emission exclusions recorded for
fugitives, the reactors' vents, storage breathing and pellet dust.
Reason: the foreground for a cradle-to-gate polystyrene once the backgrounds are linked; the
styrene carries almost all of the burden (1.006 kg of styrene-1's product per kg of pellets).

## D-012 Cross-check against the POL BREF (2026-11-19)
Per t of GPPS, the dataset against SRC-1's Table 4.10 / Table 13.6 (benchmarks/polymers.yaml):
- styrene: 1.006 t of styrene-1's product (feed:SM, 0.15 wt% ethylbenzene in it; 1.0045 t of
  styrene itself), inside 0.985 to 1.020 t, which is the monomer as bought; the BREF's product carries about 0.02 t of mineral
  oil and 0.005 t of additives that ours does not, so 0.985 t of styrene in 1 t of the BREF's
  product compares with about 1.01 t in ours;
- total energy 0.49 GJ (53 kWh electricity, 83 kWh heat from the hot oil), below the BREF's 1.08
  to 1.80 GJ (outside, explained in the benchmark): the dataset counts only the line's motors and
  the heat delivered to E-101; the hot-oil heater's losses, cooling-water and other utility
  energy, tracing, HVAC, start-ups and buildings are not in it, and the BREF does not say how it
  adds fuel and power;
- cooling water: 0.292 kWh/kg, 25 t/t circulated at a 10 K rise, below the BREF's 50 to 100 t;
- process water 0.596 t and nitrogen 0.022 t, VOC 86 g: the BREF's figures by construction (not
  bound as benchmarks); wastewater 0.596 t, below the BREF's 0.8 t (its other sources, such as
  the styrene adsorber's regeneration and cleaning, are not in this concept).

## Core features used and limits hit

Used: conversion reactors with their duties (ADR 0059), component separators (`recovery:`) and
design specifications on a feed and a purge split solved with a recycle tear (ADRs 0060, 0070),
`cheme assess lca` with a consumable and its disposal.

| id | limit | effect here | workaround |
|---|---|---|---|
| L-1 | No polymerisation kinetics: the `cstr` and `pfr` models need rate laws (`pfr` is a gas-phase catalyst bed), and no model carries a chain-length (molar-mass) distribution, the gel effect or the viscosity | reactors are conversion steps with ASSUMED per-pass conversions; volumes from ASSUMED residence times; no molar mass, melt flow rate or productivity per volume | D-005; a rate law with its source would allow `reactor: cstr` for R-101 |
| L-2 | The conversion-step duty uses one constant liquid heat capacity per component | sensible heats between 300 and 513 K low by about 15 to 25 % | D-006 |
| L-3 | No property package covers styrene, ethylbenzene or a polymer; no polymer-solvent phase equilibrium (Flory-Huggins) | `props --fill` calculates nothing; the devolatilisers' recoveries are not predicted, R-101's boiling pressure only bounded (Raoult's law with an assumed Flory-Huggins chi) | D-005 (scripts/ps_balance.py), D-007: specified splits |
| L-4 | Separators, flashes and coolers write no duty | E-101, E-103 and the pelletiser's heats from the balance script | D-008, D-009, scripts/ps_balance.py |
| L-5 | `cheme process reactor-hazards` screens batch and semi-batch reactors only | the continuous reactors' runaway screened by hand | D-010 |
| L-6 | No solid or glassy polymer phase: the pellets are carried as a liquid template | the pelletiser is a component separator; the melt's heat capacity is used down to 323 K | D-006, D-009 |

## Open inputs

A rate law of the thermal polymerisation (and of a peroxide-initiated variant) with its source;
the melt's heat capacity; the phase equilibrium of styrene and ethylbenzene over the melt;
the product's grade (molar mass, melt flow rate, mineral oil, residual monomer); the plant's
measured electricity and heat; the relief and interlock design of D-010; the site.
