# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Maleic anhydride by selective oxidation of n-butane, issue
ChemE-as-Code/process-library#478, a continuous Tier 2 entry of the library. Concept stage:
design basis, balanced BFD/PFD with the feeds solved for the rate, equipment list, hazard notes
and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` with the core pin 0e85885 (v1.12.0 with #254).
Core 1.12 solves conversion steps with their duties (core ADR 0059), component separators from
a specified split and feeds for a target by design specifications (ADR 0070), and recycles at
tear streams (ADR 0060): the whole mass balance is core's, only the heats of the separators,
coolers and machines are a script's. Templates: `oxalyl-chloride-1` (structure, a balance
script beside core's models), `formaldehyde-1` (a partial oxidation with heat recovery and a
steam export). Requires cheme-as-code 1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (Google Patents machine text; NIST WebBook, PubChem and Wikipedia pages; the paper's
open web page). Values queried from the `chemicals` and `thermo` Python packages are not
"read": SRC-6 names each package method and the underlying work it comes from, which was not
read here (library ADR 0037).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 7 589 217 B2, A. S. Padia, H. Sachs, M. Millman (SD Lizenzverwertungs GmbH), filed 2006-04-24, granted 2009-09-15: Yield improvement in the production of maleic anhydride, https://patents.google.com/patent/US7589217B2/en | description and Examples 1 to 5: VPO catalyst in a fixed-bed multitubular reactor (commercial tubes 0.5 to 1.5 in inside, 5 to 25 ft long), a eutectic nitrate-nitrite salt bath at 380 to 460 C (examples 395 to 402 C), hot spot 30 to 60 C above the salt and kept at or below about 480 C; feed 0.5 to 3.0 vol% butane (pilot 1.8), water 0.5 to 5 vol% (pilot 1.7), 15 to 35 vol% oxygen (air usual), inlet 0.6 to 4.0 kg/cm2 gauge (pilot 20 psig), GHSV 1000 to 4000 (pilot 1850); pilot tube 0.834 in inside with 15 ft of catalyst; conversion target 80 to 82 %; Example 3 (20.9 % O2, no CO added, salt 402 C) selectivity 69.5 mol%, yield 95.2 wt%; the invention adds CO to the feed; the gas cooled to 50 to 200 C and scrubbed with water or an organic solvent | read (Google Patents); patent, facts only | D-001, D-003 to D-005, D-011 |
| SRC-2 | US 4 118 403 A, J. E. White (Monsanto), filed 1976-11-18, granted 1978-10-03: Recovery of maleic anhydride, https://patents.google.com/patent/US4118403A/en | description and example: absorption in a dialkyl phthalate (dibutyl phthalate with up to 10 wt% phthalic anhydride); reactor gas about 18 000 m3 with 0.75 mol% MA at about 915 torr and 145 to 155 C, about 2200 kg of lean solvent at 32 to 36 C, 20-tray absorber, overhead 56 to 60 C at 825 to 885 torr, rich solvent out at 101 to 105 C; about 99.4 % of the MA, 0.6 % of the water, 10 % of the acetic acid and 53 % of the acrylic acid absorbed; 12-tray stripper, condenser 66 to 70 C at 48 to 52 torr, reflux 2, crude drawn near the top, reboiler 244 to 248 C at 85 to 89 torr, lean solvent about 0.3 wt% MA; a sponge absorber recovers about 77 % of the MA in the stripper's vapour; about 10 % of the solvent purified in a solvent still, filtered of fumaric acid; crude refined by distillation (about 100 torr, 140 C); overall recovery 98.5 to 99 %; water scrubbing turns MA into fumaric acid (losses, plugging) | read (Google Patents); patent, facts only | D-001, D-007, D-008 |
| SRC-3 | US 5 688 970 A, R. Ruggieri, S. Cassarino (Italiana Serie Acetica Sintetica, SISAS), priority 1994-06-30, published 1997-11-18: Process to recycle exhaust gases from n-butane conversion into maleic anhydride, https://patents.google.com/patent/US5688970A/en | Example 2 (conventional once-through, fixed bed, dibutyl phthalate absorption): 74 868 kg/h of air and 3289 kg/h of butane (2.1 vol%), air compressed in two stages to 3.55 bar for 3283 kW, conversion 86.5 %, selectivity 65 %, 3100 kg/h of MA recovered from the solvent (line 30, after the absorber and the stripping; the summary tables call it the MA produced), 0.94 kg per kg, the absorber's exhaust (75 057 kg/h) to an incinerator (no fuel or temperature stated); Example 1 (off-gas recycle): 3008 kg/h of butane and 2264 kW for the same MA; heat to a molten-salt coolant and from it to a steam generator; acetic and acrylic acid named as by-products | read (Google Patents); patent, facts only | D-001, D-002, D-010, benchmarks |
| SRC-4 | Wikipedia, Maleic anhydride, https://en.wikipedia.org/wiki/Maleic_anhydride | the benzene route (V2O5/MoO3, about a third of the carbon lost as CO2, few plants left by 2006) and the butane route over vanadium phosphate; C4H10 + 3.5 O2 -> C4H2O3 + 4 H2O, about -1236 kJ/mol; air-to-hydrocarbon ratio kept to avoid ignition; GHS H302, H314, H317, H334, H372; a skin and respiratory sensitiser | read; CC BY-SA, facts only | D-001, D-004, D-011 |
| SRC-5 | Zhang, X.; Wang, H.; Gou, L.; Li, L.; Duan, A.; Cao, Z. (2021) Reaction behaviors and crystal transformation of industrial VPO catalysts for n-butane oxidation, ACS Omega 6, 23558-23563, doi:10.1021/acsomega.1c03652 | section 3.1: an industrial VPO catalyst at 400 C, 1.392 vol% butane in air, GHSV 2000: CO selectivity 18.1 to 21.1 %, CO2 11.1 to 14.1 % over its run | read (PMC); CC BY-NC-ND 4.0: two numbers used as facts with the source, nothing adapted or copied | D-004 |
| SRC-6 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (core's environment), through `cheme chemistry thermo` and directly | materials.yaml: ideal-gas formation enthalpies, entropies and heat capacities by the methods named per component (ATCT_G, CRC, YAWS, WEBBOOK; Poling et al. 5th ed. heat-capacity coefficients; TRCIG; a Joback estimate for dibutyl phthalate); normal boiling points CRC_ORG / CRC_INORG (CRC Handbook tables), CO2's 194.7 K the YAWS sublimation point. scripts/balance.py, thermo's default methods: liquid heat capacity VDI_TABULAR (VDI Heat Atlas) for acetic acid, ZABRANSKY_SPLINE_C (Zabransky et al.'s liquid heat-capacity compilation) for acrylic acid and dibutyl phthalate, DADGOSTAR_SHAW (estimation method) for MA, HEOS_FIT (fits to CoolProp's reference equations of state) for n-butane and water; heat of vaporisation DIPPR_PERRY_8E (Perry's Chemical Engineers' Handbook 8th ed., from DIPPR 801) for acetic and acrylic acid, MORGAN_KOBAYASHI (correlation) for dibutyl phthalate, HEOS_FIT for n-butane and water (MA's from SRC-7); butane's vapour pressure HEOS_FIT. Butane's lower and upper flammable limits 1.4 and 9.3 vol% (the IEC 60079-20-1 (2010) table packaged in `chemicals`) | open-source packages queried 2026-11-19; single values, facts only, with the package and method; the underlying works (ATcT, the CRC Handbook, Yaws, Poling et al., TRC, the VDI Heat Atlas, Zabransky et al., Perry's 8th ed. / DIPPR 801, CoolProp's sources, IEC 60079-20-1) were not read here; not open data (library ADR 0037) | materials, D-003, D-010, D-011 |
| SRC-7 | NIST Chemistry WebBook, SRD 69, maleic anhydride (C108316) | solid formation enthalpy -469.6 +/- 0.3 kJ/mol (Parks et al. 1950), sublimation 71.5 +/- 5.0 kJ/mol (Winstrom and Kulp 1949), vaporisation 54.8 kJ/mol (326 to 350 K, Winstrom and Kulp), gas heat capacities at 273.15, 298.15, 500 and 800 K, S(298.15) 300.75 J/(mol K) (Joshi 1970), melting point 326.0 +/- 0.9 K | read | materials, D-008, D-010 |
| SRC-8 | PubChem CIDs 7923 (maleic anhydride), 3026 (dibutyl phthalate), 7843 (n-butane), 6581 (acrylic acid), 176 (acetic acid) | identity (formula, InChIKey, CAS, ChEBI cross-references) | read (PUG REST) | registry, materials |
| SRC-9 | processes/oxalyl-chloride-1, nitric-acid-1, sulfuric-acid-1, natural-gas-processing-1 (this library) | the balance-script pattern, the steam export at share 0, the NGL recovery without a butane cut | library, internal | D-010, D-012 |

Searched and not found openly (2026-11-19): a plant's specific steam export, electricity and
catalyst life for the butane route (the open hits were paid cost reports and a licensor review);
selectivities to acetic and acrylic acid on a commercial VPO catalyst; a fluid-bed process's
conversion and selectivity in an open patent read here; a destruction efficiency or NOx factor
for an MA plant's off-gas oxidiser; the solvent loss of a dibutyl phthalate recovery.

## D-001 Route and boundary (2026-11-19)
Decision: n-butane oxidised in air, once through, over a VPO catalyst in a multitubular
fixed-bed reactor cooled by molten salt that raises HP steam (SRC-1, SRC-3); the anhydride
recovered by absorption in dibutyl phthalate, vacuum stripping and vacuum distillation (SRC-2);
the off-gas and the liquid wastes burnt in a recuperative thermal oxidiser with a waste-heat
boiler (D-009).
Boundary: gate to gate, from liquid n-butane, ambient air, the solvent make-up and the utilities
to molten maleic anhydride, HP steam and the flue gas.
Reason: the butane route is the current one (SRC-4); the fixed bed is the reactor of the three
open sources with plant-like numbers read here (SRC-1's pilot and commercial tube data, SRC-3's
plant-scale example), and the solvent recovery is the one with an open example of every unit
(SRC-2). Core 1.12 models every step as a conversion step, a component separator or a
pass-through, so the mass balance is core's (D-007).
Rejected:
- benzene oxidation over V2O5/MoO3 (SRC-4): a third of the benzene's carbon (two of six atoms)
  is lost as CO2 by stoichiometry and few plants remain; a candidate for a separate entry.
- a fluid-bed VPO reactor (the issue's alternative): no open source with its conversion,
  selectivity and recovery was read; its usual aqueous or solvent recovery is the same, and a
  fluid bed would be modelled by the same conversion step, so the choice changes the reactor's
  equipment and hazards rather than the balance. Open for a second case once a source is read.
- water scrubbing to maleic acid and dehydration (SRC-1, SRC-2 background): SRC-2 states that
  it turns part of the MA into fumaric acid with yield losses and plugging, and it needs the
  acid's water evaporated; no open example with numbers was read.
- off-gas recycle (SRC-3's invention): about 9 % less butane and 30 % less compression per t,
  but the recycle loop's CO and CO2 build-up, its water scrubber and the lower oxygen need data
  of the invention's own catalyst; recorded as an improvement (open inputs).
- CO added to the feed (SRC-1's invention): about 4 points more selectivity, but it needs a pure
  CO supply; the entry takes SRC-1's reference example without CO.
Assumptions: n-butane without isobutane or propane (D-003); the phosphorus promoter SRC-1 doses
into the feed (0.5 to 4 ppm P) is not modelled.

## D-002 Capacity, product and operating hours (2026-11-19)
Decision: 25 000 t/a of molten maleic anhydride (stream S18) in 8000 h, 3125 kg/h, ASSUMED: one
reactor train of the scale of SRC-3's example (3100 kg/h). Product at least 99.5 wt% MA
(ASSUMED specification); modelled 99.99 wt% with 85 ppm acrylic acid (D-008). Delivered molten
at 343 K to storage (MA melts at 326 K, SRC-7); flaking or briquetting is outside the boundary.

## D-003 Feeds, air ratio and the reactor feed (2026-11-19)
Decision: the reactor feed of SRC-1's pilot: 1.8 mol% butane and 1.7 mol% water in air, at
239 kPa(a) (20 psig). The air carries the water (humid air, its humidity ASSUMED: a site may
add steam instead; the flowsheet does not model humidification). Dry air 78.084 N2, 20.946 O2,
0.934 Ar mol% (CO2 left out), normalised. That gives 98.2 kmol of humid air per 1.8 kmol of
butane, 27.0045 kg of air per kg of butane (scripts/balance.py), the `with:` ratio of the
design specification `rate`, which solves the butane S1 for 25 000 t/a (3337.25 kg/h). The
oxygen is 20.2 mol% of the feed. Liquid n-butane from pressure storage at 450 kPa(a), 298 K,
vaporised at 400 kPa(a) and superheated to 333 K on LP steam (E-101); the air compressed to
260 kPa(a) (K-102), about 20 kPa above the reactor inlet for the mixer and the feed train,
ASSUMED.
Note: 1.8 mol% lies above butane's lower flammable limit of 1.4 vol% at ambient conditions
(SRC-6): the feed is flammable (D-011).

## D-004 Reactor R201: conversion model, selectivities and heats (2026-11-19)
Decision: a conversion step (`reactor: conversion`): 81 % of the inlet butane converts (SRC-1,
the pilot's target of 80 to 82 %), 69.5 % of it to MA (SRC-1, Example 3: air, no CO, salt
402 C). Each reaction converts its share of the inlet butane in parallel (core's conversion
step): MAF 0.56295, COF 0.14094, CO2F 0.08586, AAF 0.01215, ACRF 0.0081.
- acetic acid 1.5 % and acrylic acid 1.0 % of the converted butane (molar), ASSUMED: SRC-2 and
  SRC-3 name both as by-products, SRC-2's absorber takes up part of each, no selectivity was
  found openly;
- the rest, 28.0 %, to carbon oxides, CO : CO2 = 0.62 : 0.38 on carbon after SRC-5's
  industrial VPO catalyst at 400 C (18.1 % CO, 11.1 % CO2 at its start), ASSUMED for this
  catalyst.
The heats are those of the formation enthalpies in materials.yaml at 298.15 K (MAF -1239.7
kJ/mol; SRC-4 gives about -1236). Core writes R201's duty Q2, 10 547.7 kW, to the salt and its
steam generator from the inlet at 407.0 K and the outlet at 683.15 K, 8 K above the salt at
675 K (ASSUMED); scripts/balance.py reproduces it.
Result: 3169.4 kg/h of MA in the reactor gas, 0.950 kg per kg of butane fed (SRC-1's Example
3: 95.2 wt%; SRC-3's once-through example gives 0.94 kg of MA recovered from the solvent per kg
of butane, about 0.95 in its reactor gas at its 86.5 % and 65 %); after the recovery (D-007),
1.068 kg of butane per kg of product, 55.5 mol% overall.
Rejected: a kinetic fixed-bed model (no open kinetics read and none in core with a coolant
temperature, L-3).

## D-005 Reactor R-201: catalyst volume, tubes and salt (2026-11-19)
Decision: about 39 m3 of catalyst: 71 500 Nm3/h of feed (3189.8 kmol/h) at SRC-1's pilot GHSV
of 1850 h-1. In tubes like SRC-1's pilot (21.2 mm inside, 4.57 m of catalyst, 1.61 L each),
about 24 000 tubes, ASSUMED (a commercial reactor may use longer tubes, SRC-1: up to 25 ft).
Salt: a nitrate-nitrite eutectic on the shell (SRC-1) at 675 K, circulated through the salt
cooler, which raises the HP steam. Inlet 239 kPa(a), outlet 160 kPa(a) (ASSUMED pressure drop).
Hot spot: SRC-1 states 30 to 60 K above the salt and keeps the gas at or below about 753 K
(480 C); the conversion model has no hot spot (L-3).

## D-006 Steam generation and the gas cooler (2026-11-19)
Decision: one HP steam level, 4500 kPa(a) saturated (530.6 K), ASSUMED: the salt at 675 K
leaves a 145 K approach. The reactor gas is cooled from 683 to 423 K (SRC-2's absorber inlet,
145 to 155 C) in E-202 (Q3 7526.9 kW, ideal gas): HP steam from the gas above about 551 K, the
boiler feed water preheated below; the whole duty is counted as HP steam, the feed-water
preheat being part of raising it. The gas stays above the dew points of MA and water at 423 K
(about 1.3 kPa of MA in 130 kPa).

## D-007 Absorption, stripping and the solvent loop (2026-11-19)
Decision: SRC-2's recovery:
- A301 (component separator): the off-gas keeps all the gases and 99.4 % of the water, 0.6 %
  of the MA, 90 % of the acetic acid and 47 % of the acrylic acid (SRC-2's absorbed shares);
  0.01 % of the solvent leaves with it (ASSUMED). Lean solvent at 307 K, gas in at 423 K and
  about 130 kPa(a), off-gas at 331 K and 115 kPa(a), rich solvent at 376 K (SRC-2).
- A-301's heat: at these four end temperatures the absorber's heat balance does not close by
  itself. Cooling the 93.5 t/h of gas from 423 to 331 K releases 2552 kW and condensing the
  absorbate (MA, water and the acids) 510 kW, while the lean solvent and the absorbate take up
  only 586 kW on their way to 376 K (scripts/balance.py). The other 2476 kW (Q10) go to
  pump-around coolers E-306 on cooling water: liquid drawn from the lower trays, cooled by 40 K
  and returned, about 123 t/h (ASSUMED arrangement; SRC-2 names no absorber cooling, only the
  gas cooling before it and the lean solvent's cooler). Without them the absorber could not
  hold SRC-2's rich-solvent and off-gas temperatures together.
- Circulation: 4.8 kg of lean dibutyl phthalate per kg of MA in the gas, from SRC-2's example
  (2200 kg per 18 000 m3 at 915 torr and about 423 K, which hold 4.68 kmol, 459 kg, of MA, ideal
  gas, our arithmetic): the design specification `solvent`, which solves the make-up S15
  (17.04 kg/h) for that ratio in S16.
- T302 (component separator): the crude side draw takes 98.1 % of the MA, 50 % of the acrylic
  acid, 20 % of the acetic acid, 5 % of the water; the lights (water, acids, 0.5 % of the MA
  after the sponge absorber) go to the vacuum system and the oxidiser; the lean solvent keeps
  1.4 % of the MA, about 0.3 wt% (SRC-2), and none of the water and acids. These splits are
  ASSUMED around SRC-2's numbers.
- SP303: 0.1 % of the lean solvent purged to the oxidiser, standing for the residue of SRC-2's
  solvent still (which treats about 10 % of the solvent) and the filter's fumaric acid,
  ASSUMED; made up with fresh solvent (5.45 g per kg of MA).
- The loop is torn at S17 (the cooled lean solvent) and converges in 2 Broyden iterations with
  the specifications (ADR 0070), its tolerance 1e-5 kg/h.
Result: overall MA recovery 98.6 % of the reactor's MA (SRC-2: 98.5 to 99 %).
Rejected: a stage model of the absorber and stripper (no property package of core covers
dibutyl phthalate with MA, L-1); a lean/rich interchanger (not in the concept balance: the
reboiler Q4 and the cooler Q6 are upper bounds, open inputs).
Not modelled: MA's hydrolysis to maleic acid by the absorbed water and its isomerisation to
fumaric acid (SRC-2), the phthalic anhydride SRC-2 allows in the solvent.

## D-008 Purification C401 (2026-11-19)
Decision: one vacuum column (about 13 kPa(a), 413 K at the top as SRC-2's refining), a
component separator: the product takes 99.7 % of the crude's MA, 3 % of the acrylic and 0.5 %
of the acetic acid; the lights all the water, 99.5 % of the acetic and 97 % of the acrylic acid
and 0.15 % of the MA; the residue the rest (0.15 % of the MA and the solvent). ASSUMED splits
for a product of at least 99.5 wt%; the model gives 99.99 wt%. Reflux 1.5 ASSUMED for the
reboiler's duty; the condenser on tempered cooling water above MA's 326 K melting point.

## D-009 Thermal oxidiser R501 (2026-11-19)
Decision: the absorber's off-gas (634 kg/h of butane, 907 kg/h of CO), the stripper's and the
column's lights and residue and the solvent purge are burnt in F-501 (a conversion step):
butane 99.9 %, CO 99.8 %, MA, the acids and the solvent 99.99 % destroyed, ASSUMED. The off-gas
holds 14.3 mol% O2 and needs no combustion air.
The off-gas is lean: 0.34 mol% butane and 1.0 mol% CO, about a third of its lower flammable
limit (Le Chatelier with the limits of SRC-6's IEC 60079-20-1 table, 1.4 vol% for butane and
10.9 vol% for CO): it cannot hold a flame of its own. Burnt as it
comes, at 331 K, it reaches only about 743 K (scripts/balance.py, ideal gas with
materials.yaml's data), too cold for the ASSUMED destruction without a catalyst. F-501 is
therefore a recuperative thermal oxidiser, ASSUMED: a gas-gas recuperator preheats the feed
from 331 to about 691 K against the flue gas (about 9.9 MW) so that the chamber runs at
1073 K (ASSUMED, a usual order for a thermal oxidiser; no source on this off-gas's oxidiser was
read, SRC-3 states neither fuel nor temperature); the flue gas leaves the recuperator at about
743 K into the waste-heat boiler and the economiser and leaves them at 453 K (ASSUMED). The
recuperator moves heat inside F-501 and does not change its balance: in normal operation the
combustion heat sustains the chamber without support fuel. Burner fuel for start-up and a
pilot is not modelled (open input). Rejected: support fuel instead of the recuperator (about
9 to 10 MW of natural gas, about 0.6 kg more fossil CO2 per kg of MA); a catalytic oxidiser
(lower temperature, but no open data on its destruction of this off-gas read).
Core writes the heat raised as HP steam, Q9 8116.6 kW, from the reactions' heats and the
ideal-gas data (the liquid feeds, 0.1 % of the mass, counted as gas, L-4). The induced-draught
fan (P4, 246.9 kW) is its own step K502 after the economiser: its work heats the stack gas to
461.9 K (S23) and raises no steam. Stack: 1.451 kg of fossil CO2 per kg of MA; NOx not
estimated (lca.yaml exclusion).

## D-010 Utilities and heat: every energy flow (2026-11-19)
Decision: scripts/balance.py gives what core does not:
- K-102 (P1): 90.1 t/h of humid air compressed adiabatically from 101.3 to 260 kPa(a) at an
  isentropic efficiency of 0.80 and a motor of 0.96 (ASSUMED): 3035.1 kW, outlet 412.4 K;
  SRC-3's once-through example needs 3283 kW for 74.9 t/h to 355 kPa(a) in two stages. A steam
  turbine on the exported steam is the usual alternative, not chosen.
- E-101 (Q1): 387.6 kW of LP steam (450 kPa(a)) to vaporise the butane at 315.1 K (400
  kPa(a)) and superheat it to 333 K (thermo 0.6.1).
- E-202 (Q3): D-006.
- A-301 (Q10): the pump-around coolers E-306, 2476.1 kW to cooling water (D-007).
- T-302 (Q4, Q5): the part of the rich solvent that leaves as lean solvent heated from 376 to
  519 K, the crude to its 400 K draw near the top (SRC-2) and the lights to their outlet; the
  crude boiled up and the lights at SRC-2's reflux 2 (MA's heat of vaporisation from SRC-7, the
  others thermo 0.6.1): 1858.5 kW of HP steam; the condensers 613.2 kW to cooling water. Q4 less
  Q5 is the outlets' enthalpy less the rich solvent's, so the stripper's heat balance closes.
  The reboiler at 519 K leaves 12 K to the 531 K steam: tight, to be checked against hot oil
  (open input).
- E-305 (Q6): the lean solvent from 519 to 307 K, 1803.4 kW to cooling water (no interchanger,
  D-007).
- C-401 (Q7, Q8): the residue heated to the 433 K bottom and the product and lights to the
  413 K top and boiled up, 1298.0 kW of HP steam; the overhead condensed and the product and
  lights cooled to 343 K, 1303.5 kW to cooling water; the column's heat balance closes the same
  way.
- P2, P3, P4: pumps at 0.60 (P2 with the absorber's pump-around pumps, 250 kPa), vacuum pumps
  30 and 15 kW, the oxidiser's induced-draught fan for 5 kPa at 0.70 (ASSUMED): 50.6, 15.9 and
  246.9 kW.
- The mixed temperatures S5 (407.0 K), S16 (519.0 K) and S21 (331.2 K); the stack gas after
  the fan S23 (461.9 K); the oxidiser's recuperator (D-009).
Per kg of MA: electricity 1.072 kWh, HP steam raised 8.38 kWh (Q2 + Q3 + Q9) and 1.010 kWh
drawn back for the reboilers (net export 7.37 kWh, 26.5 MJ), LP steam 0.124 kWh, cooling water
1.983 kWh (Q10 + Q5 + Q6 + Q8, the absorber's coolers 0.792 of it). The reboilers draw from the
site header (HPSI), which the plant feeds: the flowsheet keeps both so that each terminal has
one level and direction.
Utilities: cooling water 298/308 K, LP steam 450 kPa(a), HP steam 4500 kPa(a), all ASSUMED.

## D-011 Hazards (2026-11-19)
Screening notes for a later HAZOP (no study yet):
- Flammable feed: 1.8 mol% butane lies above its lower flammable limit of 1.4 vol% (SRC-6;
  the upper limit is 9.3 vol%) at ambient conditions, and the limits widen with temperature;
  SRC-4 notes the ratio is kept to avoid ignition. Measures to carry into basic engineering:
  butane-to-air ratio control with a high-ratio trip and a low-air-flow trip, a feed analyser,
  no ignition source from M-103 to R-201's outlet head (static, hot surfaces), deflagration
  venting or rupture discs on the reactor heads and the gas cooler's inlet.
- Runaway and hot spot: without salt cooling the reaction heat would take the gas to about
  1020 K at the model's conversion (scripts/balance.py; the conversion would rise further,
  towards total combustion, which is about twice as exothermic per mol, SRC-4). SRC-1 keeps the
  gas at or below about 753 K, 30 to 60 K above the salt; the salt temperature, tube-wall and
  hot-spot temperatures and the butane ratio set the trips.
- Molten nitrate-nitrite salt at 675 K: an oxidiser in contact with organics if a tube leaks;
  freezing on loss of heat tracing (start-up heaters, SRC-1).
- Maleic anhydride: corrosive and a skin and respiratory sensitiser (SRC-4: H314, H317, H334,
  H372); molten product handled hot (343 K), vents to the oxidiser.
- Carbon monoxide: about 1 % of the off-gas (907 kg/h) to the oxidiser; toxic on a leak of the
  absorber's overhead line.
- Vacuum columns (T-302, C-401): air ingress at 519 K into an organic solvent.
- No reactor hazard screening of core applies: `cheme process reactor-hazards` screens batch
  and semi-batch reactors (L-5).

## D-012 Preliminary gate-to-gate LCI (2026-11-19)
Decision: `lca/lca.yaml` with `boundary: cradle-to-gate` so that the purchased inputs stay open
gaps, as oxalyl-chloride-1. All burdens to the anhydride; the exported HP steam is a co-product
with share 0 (as nitric-acid-1 and sulfuric-acid-1), its credit left to the receiving site.
Linked: the LP and HP steam drawn, counted as heat delivered (steam-heat). Gaps in lca/lca.yaml
(the `cheme assess lca` view), each naming the activity it should connect to: n-butane (no
library producer; natural-gas-processing-1 recovers NGL without a butane cut), dibutyl
phthalate, electricity, cooling water, the VPO catalyst (39 m3 at an ASSUMED 0.9 t/m3, replaced
every 4 years, ASSUMED: 8.8 t/a). The library's Atlas build (scripts/build_lci.py) links
electricity and cooling water through the shared lci/mappings.yaml; there only butane, the
solvent, the catalyst and the oxidiser's organic slips stay unlinked. Emissions:
fossil CO2 (1.451 kg/kg) characterised; CO, butane, MA, the acids and the solvent at their
oxidiser slips as elementary flows without a GWP factor. The screening footprint (1.45 kg
CO2-eq/kg) is the direct CO2 only, a partial result.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component and element balances | done in cheme | cheme validate / process streams / propagate |
| reactor R201 (conversion, duty Q2) | done in cheme, by-product selectivities ASSUMED | D-004, core ADR 0059 |
| absorber, stripper, column (component separators) | done in cheme, splits sourced or ASSUMED | D-007, D-008, core ADR 0070 |
| feeds for 25 000 t/a, solvent make-up for the circulation | done in cheme (design specifications) | D-003, D-007, core ADR 0070 |
| solvent loop | done in cheme (tear S17, Broyden) | D-007, core ADR 0060 |
| thermal oxidiser R501 (conversion, duty Q9) | done in cheme, destruction ASSUMED | D-009 |
| air ratio, compressor, mixing and stack temperatures, Q1, Q3 to Q8, Q10, P1 to P4 | script | D-003, D-010 |
| absorber heat balance (Q10), the separators' heat balances closed | script | D-007, D-010 |
| oxidiser's adiabatic temperature, preheat and recuperator | script, chamber temperature ASSUMED | D-009 |
| R201's duty cross-check, the adiabatic outlet without cooling | script | D-004, D-011 |
| catalyst volume and tubes | by hand from SRC-1's GHSV and tube | D-005 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core features used (core 1.12.0)

- `reactor: conversion` with five parallel reactions on one key (R201) and six on separate
  keys (R501), each with its `heat_of_reaction`, and `energy_port`: core writes Q2 and Q9.
- `recovery:` on A301, T302 and C401 (component separators, ADR 0070), one outlet left out
  for the rest.
- `specs:` `rate` (annual target on S18, the air following the butane `with:` its ratio) and
  `solvent` (a mass ratio of S16's solvent to S7's MA), solved together with the tear S17.
- `tears:` with `convergence` (ADR 0060); `split:` on the purge SP303.
- `cheme chemistry thermo` for the ideal-gas data; `cheme assess lca` with `allocation:
  shares`, `consumables` (catalyst), `emission_exclusions`.
- Not used: `cheme process props` (no package covers these gases with MA or the liquids),
  `cheme process simulate` (no DWSIM run for the concept), `reactor-hazards` (batch only).

## Core limits hit (each a candidate core issue)

- L-1: no liquid property method for MA, dibutyl phthalate and the acids: the absorber, the
  stripper and the column are fixed splits without temperatures, stages or duties, and their
  heats are the script's, each closed over the unit from its inlets to its outlets at their
  stated temperatures (D-007, D-008, D-010).
- L-2: propagate writes no duty for a pass-through exchanger even where every component has
  ideal-gas data (E-202 on the reactor gas): the script computes Q3 with the same data core
  uses for the conversion steps.
- L-3: the conversion step has no coolant: a fixed bed with a salt temperature, a hot spot and
  the selectivity's fall with conversion cannot be represented; the conversion and the
  selectivities are inputs (D-004, D-005).
- L-4: a conversion step's duty counts every inlet as ideal gas: the oxidiser's liquid feeds
  (0.1 % of its mass) carry no heat of vaporisation, and dibutyl phthalate's Joback heat
  capacity is used below its range (D-009).
- L-5: no hazard screening for a continuous reactor (`reactor-hazards` screens batch and
  semi-batch steps), and no check of a gas stream against its flammable limits; both by hand
  (D-011).

## Open inputs
Commercial catalyst data (selectivities to the acids, CO/CO2, life, bulk density); a fluid-bed
case; the lean/rich interchanger and a heat-integration study (the reboilers and the solvent
cooler); the reboiler medium of T-302 (12 K approach to HP steam); the solvent loss and still;
the absorber's cooling arrangement (pump-arounds or intercoolers, their number and range); the
oxidiser's chamber temperature and residence time against its destruction, the recuperator or a
catalytic oxidiser, its NOx and its start-up and pilot fuel; a steam turbine drive for K-102; the off-gas
recycle of SRC-3; the receiving site of the steam and its credit; prices for a TEA; the
deflagration protection of the feed train (D-011).
