# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Ethylene and propylene from methanol by methanol-to-olefins (MTO), issue
ChemE-as-Code/process-library#466, coverage item `mto-olefins` (rank 61). Concept stage: design
basis, balanced BFD/PFD with a sourced reactor yield model and an oxygenate recycle, shortcut
duties, equipment list and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout,
HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` with the core pin 0e85885 (v1.12.0 with QSDsan).
Templates: `ethylene-1` (the recovery-train conventions: quench, five-stage compression with a
caustic wash and dryers, cold separation with refrigeration, mass allocation, the steam
exchanges as heat), `oxalyl-chloride-1` (structure and depth of a recent entry), `methanol-1`
(the feed). Requires cheme-as-code 1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (Google Patents machine text, 2026-11-19).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 7 138 557 B2, J. J. Senetar (UOP LLC), priority 2003-04-22, granted 2006-11-21: Selective dimethylether recovery and recycle in a methanol-to-olefin process, https://patents.google.com/patent/US7138557B2/en | Examples 1 and 2 (common part) and Table 1: fluidised-bed MTO on a SAPO-34 catalyst (40 mass-% sieve, 70 to 80 micron particles), feed 99.85 wt-% methanol in water entering at about 100 C, effluent about 475 C, about 239 kPa, WHSV 2.4 h-1 on total catalyst, 2 to 5 mass-% coke on the circulating catalyst, regenerated to about 1 mass-% or less; 99.5 mass-% methanol conversion; Table 1 yield structure in mass-% of methanol equivalent (methane 0.85, ethylene 33.50, ethane 0.65, propylene 44.50, propane 0.30, butylene 9.5, butane 0.01, C5+ 5.00, coke 2.85, unreacted methanol 0.50, DME 1.05, others (H2, CO, CO2, dienes) 1.29); quench to about 40 C and 200 kPa, the oxygenates of the quench water stripped and recycled to the reactor; compression to about 2069 kPa, entering the primary product separator at about 38 C for a three-phase separation (a vapour; a heavy hydrocarbon liquid, which a DME stripper strips of DME and light olefins; an aqueous phase); DME scrubbed from the vapour with a methanolic solvent (feed methanol) at 54.4 C, 2020 kPa and a solvent-to-vapour mass ratio of about 1.32:1, the scrubbed gas then washed free of methanol with by-product water at about 25 C, 1813 kPa and about 3:1 (methanol recovery zone); the description notes that a scrubber with a 99.85 mass-% methanol solvent at about 2020 kPa co-absorbs at least 12.3 mass-% of the C2 and 40.3 mass-% of the C3 olefins fed to it | read; patent, facts only | D-003 to D-006, D-008, D-009 |
| SRC-2 | US 6 166 282 A, L. W. Miller (UOP LLC), filed 1999-08-20, granted 2000-12-26: Fast-fluidized bed reactor for MTO process, https://patents.google.com/patent/US6166282A/en | detailed description: oxygenate conversion over SAPO-34 (or SAPO-17) at about 200 to 600 C, preferably 300 to 500 C, about 1 to 200 psia, preferably 20 to 100 psia; essentially complete conversion; the catalyst partly regenerated (carbon on the regenerated catalyst preferably 0 to 10 %) or regenerated to below 1 wt-%; oxidative regeneration; the reaction is exothermic and the catalyst is quickly deactivated, which is why a fluidised bed with regeneration is used | read; patent, facts only | D-001, D-004, D-007 |
| SRC-3 | US 9 233 350 B2, G. Qi, S. Zhong, Z. Yu, Y. Jin (China Petroleum and Chemical Corp, Sinopec Shanghai Research Institute of Petrochemical Technology), priority CN 201210005496 (2012-01-10), granted 2016-01-12: Start-up method for reaction-regeneration unit used to prepare light olefins from methanol, https://patents.google.com/patent/US9233350B2/en | description and claims: a fast fluidised-bed reactor and a dense-phase regenerator on SAPO-34; the low coke yield makes the reaction-regeneration system "big reactor, small regenerator"; coke burns from about 400 C; claim 1: the regenerator heated above about 580 C by the coke burn; claim 10: start-up heaters off when the reactor reaches at least about 480 C and the regenerator at least about 650 C; Example 1: 4.2 t/h methanol, average light-olefin yield 82.48 wt-% over 60 days (basis not stated) | read; patent, facts only | D-001, D-007, D-013 |
| SRC-4 | US 7 256 318 B2, J. R. Lattner, K. H. Kuechler, N. P. Coute, P. N. Chisholm (ExxonMobil Chemical Patents), filed 2003-03-28, granted 2007-08-14: Regeneration temperature control in a catalytic reaction system, https://patents.google.com/patent/US7256318B2/en | description: the coked catalyst regenerated at 500 to 700 C (most preferred range); because of the high heat of reaction and the frequent regeneration a fluidised bed reactor and regenerator are used and the heat of reaction is removed by steam generation; part of the feed may enter liquid to take up heat; the recovery system may include a demethaniser, deethaniser, depropaniser, caustic wash tower, quench tower, absorbers, C2 and C3 splitters | read; patent, facts only | D-001, D-007, D-010 |
| SRC-5 | US 6 403 854 B1, L. W. Miller, J. J. Senetar (UOP LLC), filed 2000-10-19, granted 2002-06-11: Two-stage quench tower for use with oxygenate conversion process, https://patents.google.com/patent/US6403854B1/en | description: the hot effluent is quenched in two stages to recover the heat of reaction; organic acids in the effluent are neutralised with caustic, ammonia or amines in the quench pumparound and leave with a drag stream; catalyst fines carried over are washed out | read; patent, facts only | D-008, D-012 |
| SRC-6 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (core's environment) | via materials.yaml of ethylene-1 and methanol-1 and `cheme chemistry thermo`: ideal-gas formation enthalpies (methods ATCT_G, Active Thermochemical Tables, and CRC); standard entropies (method CRC, and method YAWS, Yaws' handbook, for propane, 1,3-butadiene, 1-butene, n-butane and 1-pentene); ideal-gas heat capacities (method Poling, Poling, Prausnitz and O'Connell, The Properties of Gases and Liquids, 5th ed., for methanol; Cp/R fitted to thermo's TRCIG method, the coefficients of the TRC thermodynamic tables, for most components, and to HEOS_FIT for water); critical constants (method HEOS, CoolProp's equations of state). In scripts/balance.py: the CRC tables `phase_change.Hvap_data_CRC` (heats of vaporisation at the normal boiling point: methanol 35.21, DME 21.51, water 40.65, ethylene 13.53, propylene 18.42, propane 19.04, ethane 14.69, 1-butene 22.07, 1,3-butadiene 22.47, n-butane 22.44, 1-pentene 25.20 kJ/mol, with the table's normal boiling points) and `heat_capacity.CRC_standard_data` (liquid heat capacities: methanol 81.1, water 75.3 J/(mol K)); `reaction.Hfs`/`Hfl`, method CRC (solid NaOH -425.8, solid Na2CO3 -1130.7, liquid water -285.825 kJ/mol); `iapws.iapws95_Psat` (water vapour pressure by IAPWS-95, 7.385 kPa at 313.15 K); thermo's `VaporPressure` (its default methods) and its Peng-Robinson equation of state with ChemSep's PR binary interaction parameters (`IPDB`, 'ChemSep PR'); thermo's `HeatCapacitySolid` for graphite, method JANAF (NIST-JANAF tables; mean 14.72 J/(mol K) over 298.15 to 748.15 K) | open-source packages queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). The underlying works were not read here: the CRC Handbook, Yaws' handbook and Poling et al. (licensed), the TRC tables, the Active Thermochemical Tables, the IAPWS-95 release, the NIST-JANAF tables and ChemSep's parameter set; the values are the ones packaged in `chemicals` and `thermo` | materials, reactions, scripts/balance.py |
| SRC-7 | processes/methanol-1, ethylene-1, chlor-alkali-1 (this library) | Grade AA methanol (the feed); the recovery-train conventions (compressor efficiency 0.78, refrigeration at 60 % of the Carnot COP, 3 mol NaOH per mol CO2, steam levels, mass allocation, steam counted as heat); 50 wt% caustic soda | library, internal | D-003, D-009 to D-012 |
| SRC-8 | Ye, M., Tian, P., Liu, Z. (2021) DMTO: A Sustainable Methanol-to-Olefins Technology. Engineering 7(1):17-21, doi:10.1016/j.eng.2020.12.001 | the DMTO reactor-regenerator description (turbulent fluidised bed, bubbling-bed regenerator); section 2: about 2.97 t of methanol per t of light olefins (ethylene and propylene) in a continuous 72 h performance test of the first commercial DMTO unit (Shenhua Baotou, designed for 1800 kt/a of methanol); section 5.1: 2.85 t/t in the Baofeng Ningxia phase II unit with a newer DMTO catalyst | read (publisher's page, 2026-11-19); facts only. Not retracted: Crossref records no retraction, correction or other update for the DOI, and the publisher's retraction query for the article returns none (corrected 2026-11-19: an earlier note read the page's hidden, empty notice templates as a retraction) | route lead (D-001); the benchmark of the methanol consumption (D-002) |

Searched and not read or not found openly (2026-11-19): an open-access review of MTO (RSC J.
Mater. Chem. A 2025, blocked by the publisher's bot check); Tian et al. (2015) ACS Catal. 5:1922
(licensed); the UOP/Hydro and DMTO licensors' yield, utility and catalyst make-up figures; open
kinetics of methanol conversion on SAPO-34 suited to a fluidised-bed model; the regenerator's
CO, NOx and dust in the flue gas; an open specification of polymer-grade propylene (its C2
limit here is ASSUMED, D-010).

## D-001 Route and boundary (2026-11-19)
Decision: methanol-to-olefins on a SAPO-34 catalyst in a fluidised-bed reactor with continuous
catalyst circulation to a fluidised-bed regenerator (the UOP/Hydro MTO and DMTO type, SRC-1 to
SRC-4), followed by the product recovery of an olefin plant:
- E101/R100/R101: methanol vaporised and converted at 475 C and 239 kPa(a); the coke goes with
  the spent catalyst (X101) to the regenerator R201, where it is burnt off with air;
- T201/T202 (lumped) and T203: quench of the product gas with water, the oxygenates (methanol,
  DME) scrubbed out, stripped from the water and recycled (tear S37);
- K301, V301, T310, K302, D320: compression in five stages to 2.07 MPa(a), caustic wash for
  CO2, drying;
- T401 to T503: front-end deethaniser, demethaniser, C2 splitter, depropaniser, C3 splitter,
  debutaniser; K701 propylene/ethylene refrigeration.
Boundary: methanol at the battery limit (methanol-1) to polymer-grade ethylene and propylene,
a C4 olefin cut, a C5+ cut and a tail gas to the site's fuel header; utilities from the site.
Rejected:
- a fixed-bed MTO (or the fixed-bed Lurgi MTP process, propylene only): SAPO-34 cokes within
  hours and the reaction is strongly exothermic, which is why the open patents choose a
  fluidised bed with continuous regeneration (SRC-2, SRC-4); MTP also makes a different product
  slate (propylene and gasoline);
- DMTO-II or UOP's olefin cracking of the C4+ back to ethylene and propylene: no open yield of
  that step was read; the C4 cut leaves as a co-product instead, and a cracking step is an
  extension;
- a ZSM-5 methanol-to-gasoline/olefins route: a gasoline process, not a light-olefin one;
- a front-end demethaniser (as ethylene-1): the MTO gas holds little hydrogen and methane
  (8 and 2 mol% of the dry gas here), so the deethaniser goes first and only the small C2 cut
  is chilled (SRC-4 lists both columns, without an order).

## D-002 Capacity and operating hours (2026-11-19)
Decision: 1800 kt/a methanol fed, 225 t/h at 8000 h/a (ASSUMED: one reactor train of world
scale; SRC-3's example unit takes 4.2 t/h; SRC-8's first commercial DMTO unit was designed for
the same 1800 kt/a). The products follow from the yields: 33.30 t/h ethylene (266 kt/a) and
43.67 t/h propylene (349 kt/a), 2.92 kg methanol per kg of ethylene and propylene
(scripts/balance.py prints it), between SRC-8's 2.85 and 2.97 t/t of two commercial DMTO units
(the benchmark in benchmarks/olefins.yaml).

## D-003 Feed (2026-11-19)
Decision: methanol from methanol-1, at 313 K and 500 kPa(a) (ASSUMED), modelled as the feed of
SRC-1's examples, 99.85 wt% methanol and 0.15 wt% water. methanol-1 delivers Grade AA
(at most 0.10 wt% water, its design target 0.05 wt%), the grade the LCI links to: the
modelled feed is 0.05 to 0.10 wt% wetter than that product, about 0.1 to 0.2 t/h of water
against 125 t/h of reaction water, which changes no result at the stated precision; the
patent's composition is kept as the sourced basis. No diluent steam (SRC-1 uses none; the
reaction water dilutes the gas).

## D-004 Reactor conditions (2026-11-19)
Decision: vapour feed at 393 K and 350 kPa(a) (ASSUMED), outlet 748.15 K and 239 kPa(a) (SRC-1,
475 C and about 239 kPa, inside SRC-2's preferred 300 to 500 C and 20 to 100 psia). SRC-1's
feed enters at about 100 C; at 350 kPa(a) the feed's dew point is 373.6 K (Raoult with
thermo's vapour pressures, SRC-6), so the feed is superheated by 20 K (ASSUMED) to keep liquid
out of the distributor. A hotter feed would only move heat from the vaporiser's MP steam to the
catalyst cooler's HP steam, both counted gross in the LCI (D-012). The bed is
taken as isothermal at the outlet temperature, its heat removed in a catalyst cooler raising HP
steam (SRC-4: heat of reaction removed by steam generation).
Rejected: a partly liquid feed that takes up part of the heat (SRC-4): no open fraction was
read, and the vaporiser keeps the energy accounting explicit (D-011).

## D-005 Reactor yield model R101 (2026-11-19)
Decision: a conversion step with `selectivity:` (core): key methanol, 99.5 % converted per pass
(SRC-1), and the selectivities, in kmol per kmol of methanol converted, from SRC-1's Table 1
read as shares of the methanol's carbon ("mass-% of methanol equivalent", i.e. of its CH2,
"based on an appropriate carbon balance"; our reading, ASSUMED): each product's share divided
by 99.5 and by its carbon number. The 1.29 of "others (H2, CO, CO2, dienes)" is split into CO
0.45, CO2 0.25 and 1,3-butadiene 0.59 (ASSUMED; the table gives no split, and hydrogen follows
from the element balance). Each product has one formation reaction from methanol, balanced in
its elements (process/reactions.yaml); paraffins take hydrogen, and coke (as carbon), dienes,
CO and CO2 release it, so 0.034 kmol of hydrogen per kmol of methanol converted leaves with the
gas. Lumps: 1-butene for the butylenes, 1,3-butadiene for the dienes, 1-pentene for C5+, carbon
for the coke (a coke with hydrogen would leave less hydrogen in the gas and water vapour in the
flue gas).
Heats of reaction: the sums of the ideal-gas formation enthalpies of materials.yaml (SRC-6),
coke as graphite with 0 kJ/mol (ASSUMED). Result: of the methanol's carbon, 33.7 % to
ethylene, 44.7 % to propylene (E/P mass ratio 0.76), 2.9 % to coke.
Rejected: kinetics (none read openly that suits a fluidised bed), and a yield fitted to an
E/P ratio of choice (the patent's measured slate is the evidence; DMTO-type operation shifts
it towards ethylene, an alternative case for later).

## D-006 Oxygenate recycle and the DME model step R100 (2026-11-19)
Decision: the unconverted methanol and the DME are recovered (T201, T203) and recycled to the
reactor (SRC-1). Core's `selectivity:` has one key (L-2), so the recycled DME is counted as the
two methanol molecules it is made of in a model step R100 before R101 (DME + H2O -> 2 CH3OH,
conversion 1, adiabatic, equipment R-101): recycled DME is ASSUMED to give the yields of
methanol, which SRC-1's recycle presumes. The step's heat of reaction (+22.7 MJ/kmol, 0.23 MW
for the recycled DME) is taken from the feed: S4 leaves 2.4 K colder than S3
(scripts/balance.py), so R101's catalyst cooler raises that much less steam, as the DME's
smaller heat release in the real reactor would. The recycle converges at the tear S37 (Wegstein, 5
iterations): 4.11 t/h of methanol, DME and water.

## D-007 Catalyst regeneration and steam raising (2026-11-19)
Decision: all coke leaves the reactor with the spent catalyst (X101, recovery 1; the
cyclones' fines loss not modelled) and burns completely to CO2 in R201 at 923 K (SRC-3: above
580 C, 650 C at the end of start-up; within SRC-4's 500 to 700 C), with air for 2 vol% O2 in
the dry flue gas (ASSUMED): 30.8 t/h of air for 2.44 t/h of coke (scripts/balance.py). The
blower K-201 compresses the air to 300 kPa(a). The regenerator's heat (the coke burn less the
flue gas leaving at 473 K after a flue gas steam generator) and the reactor's heat of reaction
both raise HP steam at 4000 kPa(a) (ASSUMED level): Q2 5.36 MW and Q3 22.10 MW, core's
conversion-step duties (core ADR 0059); Q2 is what the bed's heat of reaction leaves after
heating the feed from 391 to 748 K. Only the coke moves between reactor and regenerator in
the model; the catalyst's sensible heat circulating between them is not (L-3), so the sum of
Q2 and Q3 holds but not their split.
Not modelled: the steam of the spent catalyst stripper (and any lift or aeration steam). No open
catalyst circulation rate was read; ASSUMED order of magnitude: a coke difference of 1 to 4
mass-% across the catalyst (SRC-1: 2 to 5 % spent, about 1 % or less regenerated) gives 60 to
240 t/h of circulating catalyst for 2.44 t/h of coke, and a few kg of steam per t of catalyst
(ASSUMED) under 1 t/h of steam, below 1 MW and under 1 % of the steam counted.
Rejected: partial regeneration with CO in the flue gas (SRC-2 allows it): no open CO/CO2
ratio; the CO would need a CO boiler.

## D-008 Quench and oxygenate recovery (2026-11-19)
Decision: T201 cools the gas from 748 K to 313 K at 200 kPa(a) (SRC-1) and condenses the
water until the gas leaves saturated with it (98.39 % of the water: the recovery that
scripts/balance.py prints from the IAPWS-95 vapour pressure, ideal gas; an equilibrium stage,
ASSUMED). SRC-1's DME scrubber is lumped into this step (99 % of the DME and 99.9 % of the
methanol into the water, ASSUMED). Why: SRC-1's scrubber uses feed methanol as its solvent and
sends its DME-rich bottoms to the reactor, so outside the recovery section its net effect is
the one modelled, DME and methanol back to R101. What the lumping departs from: SRC-1 scrubs
after compression, at 54.4 C and 2020 kPa with methanol (water at 200 kPa(a) would absorb DME
poorly), so the compressors carry about 1.7 t/h more DME than modelled (1.7 % of their gas);
and such a scrubber co-absorbs C2 and C3 olefins (SRC-1: at least 12.3 and 40.3 mass-% in the
scrubber it compares against), an olefin recycle through the reactor that is not modelled.
A DME scrubber with its solvent loop is the step to add when the recovery section is
simulated. The quench heat goes to cooling water through the pumparound coolers (143.6 MW,
no heat recovery counted, D-011). T203 strips the oxygenates with 1 % of the water overhead
and recycles them (ASSUMED); the stripped water (125.4 t/h, 5 ppm(mol) methanol) goes to
wastewater treatment. The organic acids that SRC-5
neutralises in the quench are not modelled (an open item, D-012).

## D-009 Compression, caustic wash and drying (2026-11-19)
Decision: K-301 compresses the gas in three stages to 900 kPa(a); V301 knocks out water until
the gas leaves saturated at 313 K (78.95 % of the remaining water, scripts/balance.py's
IAPWS-95 recovery, ideal gas, ASSUMED); a Peng-Robinson flash of S13 forms no hydrocarbon
liquid there. The caustic tower T310 removes the CO2 with 10 wt% caustic at 3 mol NaOH per mol
CO2 (ASSUMED excess, as ethylene-1) to a polymer-grade residue (conversion 0.9999); the spent
liquor takes 98 % of the water it holds (ASSUMED). The heat of neutralisation goes to a liquor
cooler on cooling water that holds the tower at 313 K (Q26, ASSUMED cooler): 0.85 MW for
17.8 kmol/h of CO2 at -171.5 kJ/mol, the reaction of the solids on CRC formation enthalpies
(SRC-6), an upper bound (the heats of solution, not read, make the reaction in solution less
exothermic). Two more stages compress the gas to 2069 kPa(a), and the aftercooler takes it to
311 K (SRC-1), where it forms three phases, as in SRC-1's primary product separator. V302, the
discharge drum, separates them by a Peng-Robinson three-phase flash of S20 (thermo with
ChemSep's binary parameters, SRC-6; scripts/balance.py prints it): 2.7 mol% of the gas
condenses; 45 % of its water forms an aqueous phase (0.18 t/h) that joins the process water to
the oxygenate stripper (SRC-1 sends its aqueous phase to oxygenate recovery), and a hydrocarbon
liquid of 3.1 t/h takes 16 % of the C5+, 7 % of the butenes and 3 % of the propylene. SRC-1
strips its hydrocarbon liquid of DME and light olefins in a DME stripper; with no DME scrubber
here (D-008) the condensate is dried in D-320's condensate dryer and joins the dried gas to
T401. The aftercooler duty Q11 includes the condensate's latent heat (0.39 MW). The
molecular-sieve dryers D-320 remove the water left in the gas and the condensate (0.22 t/h).
Their regeneration gas and heat are not modelled: ASSUMED order of magnitude 0.5 MW (about
three times the 0.15 MW that desorbing 0.22 t/h of water takes at its heat of vaporisation, for
heating the beds and the regeneration gas), under 1 % of the steam counted.

## D-010 Olefin recovery train (2026-11-19)
Decision: specified recoveries (ASSUMED), not rigorous columns (L-1): deethaniser T401 (C2 and
lighter overhead, 0.1 % of the propylene with it; 10 ppm of the ethylene and 0.01 % of the
ethane to the bottoms, because nothing downstream removes C2 from the propylene: no
pasteurisation section or light-ends vent on the C3 splitter), demethaniser T402 (hydrogen,
CO, CO2 and 99.5 % of the methane to the tail gas, 0.2 % of the ethylene with it; bottoms at
their bubble point, 243.6 K at 1950 kPa(a), Raoult with thermo's vapour pressures,
scripts/balance.py), C2 splitter T403 (99.7 % of the ethylene overhead, ethane to the tail
gas), depropaniser T501, C3 splitter T502 (98.5 % of the propylene overhead; propane, the
residual DME and 1.5 % of the propylene to the tail gas), debutaniser T503 (C4 cut overhead,
C5+ bottoms). Results: ethylene 99.97 mol% (methane 255 ppm, ethane 39 ppm), propylene
99.96 mol% (propane 340 ppm, ethylene 12 ppm, ethane 2 ppm), both inside the specifications of
design-basis.yaml, whose purities and C2 limit are this study's choices (ASSUMED; no open
polymer-grade specification was read). Not modelled: acetylene (SRC-1's table has none, so no
acetylene converter), oxygenate traces in the products, the CO, CO2 and water limits of
polymer-grade specifications. The ethane and propane go to fuel, not back to a cracker (none in this plant).

## D-011 Utilities and shortcut duties (2026-11-19)
Decision: every duty but Q2 and Q3 comes from scripts/balance.py (balance-output contract, ADR
0027 of the library) on ideal-gas enthalpies and SRC-6's heats of vaporisation:
- E101: liquid methanol to its boiling point, vaporised, superheated to 393 K (D-004), on MP
  steam (79.5 MW). No heat integration: in a plant the effluent and the quench water supply
  most of this heat (SRC-5), so this is an upper bound;
- K-201 blower (efficiency 0.80) and K-301 (0.78, ASSUMED as ethylene-1): 1.17, 4.34 and 2.36 MW
  electric, the coolers to cooling water with the latent heat of what condenses in V301 and
  V302 (D-009); the caustic tower's liquor cooler 0.85 MW (Q26, D-009);
- T203: 0.06 kg LP steam per kg of feed (ASSUMED), 4.58 MW;
- columns: (R + 1) x distillate x heat of vaporisation at the normal boiling point, reboiler =
  condenser, reflux ratios ASSUMED: T401 1, T402 1.5 mol per mol of tail gas, T403 3.5, T501 1,
  T502 12, T503 1. The reboilers of T401, T501, T502 and T503 take LP steam; those of T402 and
  T403 (Q24 1.89 MW, Q25 20.08 MW) take condensing propylene refrigerant at 253 K and 273 K,
  10 K above their bottoms' bubble points of 243.6 K and 262.5 K at 1950 kPa(a) (ASSUMED
  approach), so their heat comes from the refrigeration system, not from steam;
- K701 (60 % of the Carnot COP, as ethylene-1): T401's condenser (11.6 MW at -30 C) lifted to
  313 K; T402's and T403's condensers (1.9 MW at -103 C, 20.1 MW at -40 C) lifted only to their
  reboilers, which take that heat back, and the compression work of that lift then to 313 K:
  14.9 MW electric, 26.5 MW to cooling water (Q23).
Totals: power 22.7 MW, MP steam 79.5 MW, LP steam 98.3 MW, HP steam raised 27.5 MW, cooling
water 265.9 MW. scripts/balance.py cross-checks the plant's first law over its feeds, products
and utilities (ideal-gas enthalpies with formation enthalpies, the liquid streams less their
heats of vaporisation, the caustic loop left out): it closes within 1.7 MW of about 290 MW of
utilities. Not counted, each estimated below 1 MW: the catalyst stripping steam (D-007) and
the dryers' regeneration heat (D-009). Drives ASSUMED electric (steam turbines on the raised
steam are usual).

## D-012 Preliminary gate-to-gate LCI (2026-11-19)
Decision: `cheme assess lca --write` per kg of ethylene from the flowsheet. Methanol is linked to
methanol-1 (Grade AA) and the steam exchanges to the shared `steam-heat` entry (kWh), as
ethylene-1 does (`lca/mappings.yaml`). Every other background is a gap with the activity it
should connect to: electricity, cooling water, wastewater treatment of the reaction water and
of the spent caustic, and the 10 wt% caustic (chlor-alkali-1 exports 50 wt% caustic per kg of
solution; a kg-for-kg link would count five times the NaOH, so it stays a gap with its proxy:
0.2 kg of chlor-alkali-1's caustic and 0.8 kg of water per kg). The catalyst make-up is
excluded (`emission_exclusions` catalyst-fines), not counted as zero: no open make-up rate was
read, and a `consumables:` entry needs one; it is an open item of the inventory.
Allocation: mass among ethylene, propylene, the C4 cut, the C5+ cut and the tail gas (ethylene
34.6 %), as ethylene-1; the exported HP steam is outside the allocation and without a burden,
so the figures are gross. Per kg of any hydrocarbon product (mass allocation): methanol 2.335 kg,
electricity 0.236 kWh, MP steam 0.825 kWh, LP steam 1.021 kWh, HP steam exported 0.285 kWh,
cooling water 2.76 kWh removed, caustic solution 0.222 kg, CO2 0.093 kg (fossil, from the coke),
reaction water 1.30 kg, spent caustic 0.230 kg. Unallocated per kg of ethylene: CO2 0.268 kg.
Not counted (`emission_exclusions`): the regenerator's CO, NOx and dust, catalyst fines,
fugitives, flaring, the organic acids of the reaction water and the spent caustic's
hydrocarbons.

## D-013 Thermal hazards (2026-11-19)
The reaction is strongly exothermic and the catalyst cokes quickly (SRC-2, SRC-4); the
fluidised bed with its catalyst cooler and the regenerator's heat balance are the design's
temperature control. Not screened here: core's reactor-hazards screening addresses batch and
semi-batch reactors and cooled fixed beds, not a fluidised bed with catalyst circulation.
Open for basic engineering: loss of the catalyst cooler, afterburning in the regenerator's
dilute phase, a methanol or hydrocarbon breakthrough into the regenerator, air into the
reactor through the catalyst transfer lines (SRC-3 back-flushes the slide valves), and the
cold box's hydrogen and ethylene inventories.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| reactor R101 (conversion, selectivities) | done in cheme, yields sourced | D-005, SRC-1 |
| oxygenate recycle (tear S37) | done in cheme (Wegstein) | D-006, core ADR 0060 |
| regenerator R201, caustic tower | done in cheme (conversion steps) | D-007, D-009 |
| separator and column outlets | done in cheme from ASSUMED recoveries | D-008 to D-010 |
| reactor and regenerator duties Q2, Q3 | done in cheme (conversion-step duty) | D-007, core ADR 0059 |
| air, caustic, every other duty; S4 and S26 temperatures; the saturation recoveries of T201 and V301 and the three-phase split of V302 (printed); the plant energy balance cross-check | script (scripts/balance.py) | D-006 to D-011 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core features used (core 1.12.0)

- A conversion step with `selectivity:` (key, per-pass conversion, kmol per kmol converted)
  for R101's thirteen parallel reactions.
- `recovery:` on component separators (X101, T201, T202, V301, V310, D320, T401 to T503), solved
  by `cheme process propagate`.
- `tears:` with Wegstein `convergence` for the oxygenate recycle.
- `energy_port` on R101 and R201 for core's conversion-step duties (ADR 0059), with given heats
  of reaction and the coke's heat capacity (L-3).
- `simulation.yaml` heat mode for the adiabatic R100 (its outlet temperature from
  scripts/balance.py, so that core reports no duty for it).
- A component separator with two listed outlets (V302: aqueous and hydrocarbon liquid, the
  vapour the rest) and one with two inlets (D320: the gas and the condensate).

## Core limits hit (each a candidate core issue)

- L-1: no qualified property package for C2+ hydrocarbons with methanol, DME and water: the
  separations are specified recoveries (V302's from a Peng-Robinson flash run in the script),
  the quench condensation, compression and column duties are the script's ideal-gas shortcut
  estimates, and the energy balance is not evaluable beyond
  the conversion steps (`property_method` stays a placeholder).
- L-2: a step's `selectivity:` has a single key: a recycled second feed of the same reactor
  (DME) cannot be converted alongside methanol, hence the model step R100 (D-006). A selectivity
  per key, or a lumped "methanol equivalent" key, would remove it.
- L-3: the conversion-step duty has no solid phase: the coke carries graphite's mean heat
  capacity in `liquid_heat_capacity` and its formation enthalpy only through the given heats of
  reaction; the circulating catalyst, which carries the heat between reactor and regenerator,
  is not a stream core can hold (an inert solid with a heat capacity and no composition role),
  so Q2 and Q3 are right in sum but not in split (D-007).
- L-4: a component separator's outlets carry every upstream component, most at zero, so the
  templates list all components, and the regenerator flue gas lists zero emissions of every
  hydrocarbon that the LCA must name (lca.yaml).
- L-5: the DEXPI class `Heating` is not a pass-through for `cheme process propagate` (its
  subclasses `HeatingElectrical`, `HeatingInFurnace` are), so E101 is `ExchangingThermalEnergy`.
- L-6: propagate writes the tear's mole fractions rounded to six figures, which the DEXPI export
  can flag (S37 summed to 0.999999 in the first version, two validate warnings; none in the
  current one).

## Open inputs
A licensor's or an operating unit's yield slate, catalyst make-up, coke yield and utility
figures (to replace SRC-1's single example and the ASSUMED recoveries); the regenerator's flue
gas (CO, NOx, dust) and the catalyst fines; the reaction water's organic acids and its
treatment; heat integration (feed vaporisation on effluent and quench water, steam turbine
drives); a C4+ cracking step (DMTO-II or olefin cracking) as an alternative case; prices for an
economic allocation; the hazards of D-013.
