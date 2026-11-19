# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Biodiesel (fatty acid methyl esters, FAME) by base-catalysed transesterification of refined
soybean oil, issue ChemE-as-Code/process-library#515, a continuous Tier 2 entry of the library.
Concept stage: design basis, balanced BFD/PFD solved for its design specifications with the
methanol recycle converged, equipment list, preliminary gate-to-gate LCI. Out of scope here:
P&IDs, layout (the concept gate `layout-plot-plan` stays open on purpose, as in acetic-acid-1
and bromine-1), HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` with the core pin 0e85885 (v1.12.0 with #254).
Core can now solve feeds for design specifications and split component separators on their
recoveries (core ADR 0070), converge recycles at tear streams (ADR 0060) and write a conversion
step's duty (ADR 0059). It has no qualified liquid-liquid or vapour-liquid model for
FAME-glycerol-methanol (L-1). Templates: `oxalyl-chloride-1` (structure, LCA) and
`glycerol-1` (the downstream glycerol refinery, its lumps). Requires cheme-as-code 1.12
(plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (PDF text extracted and read; the NIST WebBook page; the Python packages queried).
Page numbers of SRC-1 are the report's printed page numbers (PDF page minus 4).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | Van Gerpen, J.; Shanks, B.; Pruszko, R. (Iowa State University); Clements, D.; Knothe, G. (2004) Biodiesel Production Technology, August 2002-January 2004. NREL/SR-510-36244, National Renewable Energy Laboratory; mirror https://fischer-tropsch.org/DOE/DOE_reports/510/510-36244/510-36244%207-01-04.pdf | p. 4: triolein with 100 % excess methanol, per 100 lb oil 21.71 lb methanol give 100.45 lb esters, 10.40 lb glycerol and 10.86 lb excess methanol, about 1 % NaOH on the oil, mostly to the glycerol; densities triolein 0.8988, methyl oleate 0.8739, glycerol 1.2613 kg/L. p. 5: triolein holds 10.4 % bound glycerol; 0.24 % total glycerol allowed, so 97.7 % completion at least. p. 23: ASTM D6751 table (water and sediment 0.050 vol%, total glycerin 0.240 wt%). pp. 31-32: base catalysis at 6:1 methanol to oil to approach the 99.7 % yield fuel grade needs; methanol recycled. p. 33: NaOH, KOH and sodium methoxide (25 % in methanol, more active per weight); residence 5 min to 1 h; HCl as neutraliser. p. 34: batch at about 65 C (25 to 85 C), 4:1 to 20:1, completions 85 to 94 %, two steps with glycerol removal 95 %+. p. 35: CSTRs in series, glycerol decanted after the first, 98 %+ completion in the second; mixing and dispersion. p. 36: tubular reactors 6 to 10 min. pp. 36-39: high-FFA, Biox co-solvent, supercritical (42:1, 350 to 400 C, above 80 atm). p. 40: crude of 50 % or less worth under 5 US cents per lb, at 88 % a credit; small plants batch, continuous 24/7 larger. p. 52: refined oils below 0.05 % FFA; sodium methoxide 0.25 % of the oil. pp. 67-68: decanters 1 to 8 h, L/D 5 to 10, centrifuges in continuous plants; wash at 120 to 140 F, slightly acid soft water, methanol removed before the wash. p. 69: water in the washed esters above the specification, vacuum dryers or falling-film evaporators; filtering to 5 micrometres. p. 75: methanol bp 64.7 C, flash point; methanol 60:40 between ester and glycerol phases at 90:10 ester to glycerol. p. 76: methanol by flash, distillation or falling-film evaporator; pH control (low pH dehydrates the glycerol, high pH polymerises it; no numeric limit given); physical processing of glycerol at 150 to 200 F. p. 77: about 1 gallon of wash water per gallon of ester per wash | read; US government report, facts only | D-001 to D-010 |
| SRC-2 | Pradhan, A.; Shrestha, D. (2009) Life Cycle Analysis of Soybean Biodiesel Production. ASABE Annual International Meeting, Reno, Paper No. 096669 (meeting paper, not peer reviewed), https://biodieseleducation.org/Literature/Journal/2009_Anup_Life_Cycle_Analysis_.pdf | pp. 7-8: oil refining yield about 96 %; biodiesel 82.4 % and crude glycerin (about 80 %) 17.6 % by mass, used as the allocation; p. 9: USDA-ARS model (Haas et al. 2006) of a plant making 9.8 million gallons of biodiesel and 4,380 tons of crude glycerin a year, boiler efficiency 80 %; p. 13: heat integration generally adopted in the industry (said of plants in general, not of the model); p. 10, Table 4: conversion inputs 439 Btu/gal electricity and 3,550 Btu/gal natural gas/steam (energy equivalents, the boiler at 80 %), methanol, sodium methoxide, NaOH and HCl in Btu/gal | read; meeting paper, facts only | D-002, D-011, benchmarks |
| SRC-3 | thermo 0.6.1 and chemicals 1.5.2 (Caleb Bell, MIT; core's environment) | liquid heat capacities at 333.15 K (kJ/(kmol K)): triolein 1844.1 (thermo method ZABRANSKY_SPLINE_C, coefficients from Zabransky et al.'s compilation of liquid heat capacities), methyl oleate 676.9, methanol 89.33, water 75.39 (HEOS_FIT), glycerol 235.15 (ZABRANSKY_SPLINE_C); liquid enthalpies of formation (kJ/mol, chemicals `Hfl`): methyl oleate -734.5 and glycerol -669.6 (method CRC), methanol -238.4 (method ATCT_L, the Active Thermochemical Tables, the package default; CRC -239.2, WEBBOOK -238.8); normal boiling points (chemicals `Tb`): methanol 337.8 K (method WEBBOOK), water 373.12 K (method HEOS); heats of vaporisation (HEOS_FIT): methanol 36.55 kJ/mol at 315.73 K and 35.56 at 333.15 K, water 43.09 at 318.96 K; ideal-gas heat capacities (HEOS_FIT, mean over the range): methanol 47.26 J/(mol K) 316-373 K, water 33.84 and methanol 47.19 J/(mol K) 319-368 K; vapour pressures: methanol 40 kPa at 315.73 K and 353.7 kPa at 373.15 K (HEOS_FIT), water 10 kPa at 318.96 K, 450 kPa at 421.1 K and 1000 kPa at 453.0 K (IAPWS_PSAT), glycerol (VDI_PPDS) for the bubble point of the crude glycerol (D-008); Dortmund UNIFAC (thermo `UNIFAC`, parameters DOUFIP2016; methyl oleate as 2 CH3, 13 CH2, 1 CH=CH, 1 CH2COO): methanol's activity coefficient in the esters 2.93 at 373.15 K and x = 0.039 | open-source package queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). The underlying works (Zabransky's compilation, the CRC Handbook, CoolProp's reference equations) were not read here | materials, reactions, D-009 |
| SRC-4 | NIST Chemistry WebBook, SRD 69, triolein (C122327), condensed-phase thermochemistry, https://webbook.nist.gov/cgi/cbook.cgi?ID=C122327&Mask=2 | liquid enthalpy of formation -2193.7 kJ/mol and enthalpy of combustion -35099.6 +/- 1.3 kJ/mol, Freedman, Bagby and Khoury (1989, J. Am. Oil Chem. Soc. 66, 595) | read | reactions (TRANS), D-009 |
| SRC-5 | processes/methanol-1, hydrogen-chloride-1, glycerol-1, oxalyl-chloride-1 (this library) | Grade AA methanol; 33 wt% hydrochloric acid; the crude-glycerol refinery and its lumps; the template's structure and LCA | library, internal | D-005, D-008, D-011 |
| SRC-6 | Haas, M. J.; McAloon, A. J.; Yee, W. C.; Foglia, T. A. (2006) A process model to estimate biodiesel production costs. Bioresource Technology 97, 671-678, doi:10.1016/j.biortech.2005.03.039 | - | not read (not open); the plant model behind SRC-2 | capacity lead only |

Searched and not found openly (2026-11-19): an open full text of Haas et al. (2006) or of a
continuous plant's design data (residence times, decanter sizes, column specifications), the
kinetics of the three consecutive transesterification steps on soybean oil in an open source
read here, liquid-liquid equilibrium data or NRTL parameters for FAME-glycerol-methanol, an open
price of crude glycerol and biodiesel of the same year and region, and an open figure of the
world or EU production volume.

## D-001 Route and boundary (2026-11-19)
Decision: homogeneous base-catalysed transesterification of refined soybean oil with methanol
and sodium methoxide, in two continuous stirred tanks in series with the glycerol decanted after
each (SRC-1 pp. 33-35), then: methanol flashed off the esters, the esters washed once with warm
water acidified with HCl and dried under vacuum; the two glycerol phases neutralised with HCl and
stripped of methanol in a column; the recovered methanol (dry) recycled to the reactors.

Rejected alternatives:
- Batch stirred tanks (SRC-1 p. 34): completions of 85 to 94 % per batch, 95 %+ with two steps;
  SRC-1 p. 40 places batch plants at small capacities and with variable feedstock. At 32 kt/a
  (D-002), continuous operation with two CSTRs is the variant SRC-1 p. 35 describes as popular.
  The batch variant would need a recipe and a dedicated train (library ADR 0035) for no gain in
  this boundary.
- Tubular reactors with intense mixing at higher temperature and pressure (SRC-1 p. 36): short
  residence (6 to 10 min), but no open data read on their conversions or conditions.
- Acid catalysis (SRC-1 pp. 33-34): slow, 20:1 alcohol and more; used for FFA pretreatment,
  which a refined oil does not need (D-004).
- Enzymatic (lipase) catalysis (SRC-1 pp. 33-34): slow (4 to 40 h), yields below the 99.7 %
  needed, costly enzymes.
- Supercritical methanol without catalyst (SRC-1 pp. 38-39): 42:1, 350 to 400 C and above 80 atm;
  higher capital and energy, laboratory scale in the source.
- Biox co-solvent process (SRC-1 p. 38): a licensed variant; no open data read.
- Heterogeneous base catalysts: not assessed (no open source read in this work).
- NaOH or KOH instead of sodium methoxide (SRC-1 p. 33): the hydroxide forms water with the
  methanol, which favours soaps; sodium methoxide is more active per weight; glycerol refiners
  prefer sodium. Methoxide is chosen.

Boundary: gate to gate, from refined oil, methanol, the catalyst solution, hydrochloric acid and
wash water to biodiesel, crude glycerol and wastewater, with LP steam, cooling water and power.
Outside: oil extraction and refining, glycerol refining (glycerol-1 is a downstream consumer of
crude glycerol, D-008), wastewater treatment, storage and loading, methanol vent condensers.

## D-002 Capacity, product and operating hours (2026-11-19)
Decision: 32 420 t/a of biodiesel, the USDA model plant's 9.8 million US gallons a year (SRC-2
p. 9) at 0.8739 kg/L (methyl oleate, SRC-1 p. 4): 9.8e6 x 3.785412 L x 0.8739 kg/L = 32 420 t.
8000 h/a, continuous (ASSUMED; continuous plants run 24/7, SRC-1 p. 40): 4052.5 kg/h. The spec
`rate` of process/flowsheet.yaml solves the oil feed S1 (4071.78 kg/h) for it.

Product: biodiesel to ASTM D6751 as SRC-1 p. 23 lists it; the modelled product has 0.032 wt%
total glycerol (free 0.0002, bound 0.031 in the 0.30 wt% unreacted glycerides, at 10.4 % bound
glycerol, SRC-1 p. 5) against 0.240, and 0.023 wt% water against 0.050 vol% water and sediment.

## D-003 Continuous operation (2026-11-19)
Decision: continuous, 24/7, one train. No recipe and no batch thermal screening: the reactors
are continuous, near thermoneutral (D-009) and run liquid-full at 333 K (D-005); `cheme process
reactor-hazards` applies to batch and semi-batch reactors and is not needed here.

## D-004 Feeds and lumps (2026-11-19)
Decision: the oil is one triglyceride lump with the formula of triolein (C57H104O6), the esters
one lump with the formula of methyl oleate, as SRC-1 p. 4 calculates its mass balance. The
unreacted lump TG stands for tri-, di- and monoglycerides together: their bound glycerol is what
the specification counts (SRC-1 p. 5). The oil is refined and dry: refined oils have below
0.05 % FFA (SRC-1 p. 52), which SRC-1 says can be ignored below 0.5 %; no FFA, soaps, water,
phospholipids or unsaponifiables are carried (limit L-3). Real soybean oil is a mixture
(palmitic, stearic, oleic, linoleic, linolenic chains), whose average molar mass differs a few
per cent from triolein's; not modelled.

## D-005 Reaction section (2026-11-19)
Decision:
- 6 mol of methanol per mol of oil to the reactors in total (SRC-1 pp. 31-32, 34): the spec
  `methanol-ratio` solves the fresh methanol S3 (422.69 kg/h) for it, the catalyst solution's
  methanol and the recycle counted.
- Sodium methoxide 0.25 wt% of the oil (SRC-1 p. 52), dosed as its 25 wt% solution in methanol
  (SRC-1 p. 33): S4 = 0.01 x S1.
- 80 % of the methanol and catalyst to R-101, 20 % to R-102 (ASSUMED: fresh methanol and
  catalyst for the second reactor, after the first decanter removed 40 % of the methanol and
  90 % of the catalyst with the glycerol).
- 333.15 K (60 C) in both reactors (SRC-1 p. 34: usually about 65 C, 25 to 85 C), at 250 and
  200 kPa(a) (ASSUMED), above methanol's vapour pressure, so the reactors run liquid-full.
- Conversions of the triglyceride: 90 % in R-101 (ASSUMED, within SRC-1 p. 34's 85 to 94 % of a
  batch) and 97 % of the rest in R-102 (ASSUMED), 99.7 % overall, the completion SRC-1 p. 32
  names for fuel grade. The reaction is a reversible sequence of three steps whose equilibrium
  the excess methanol and the glycerol removal shift; no kinetics or equilibrium model (L-2).

## D-006 Decanters and the methanol loop (2026-11-19)
Decision: V-102 and V-103 split each reactor effluent on specified recoveries to the glycerol
phase: 90 % of the catalyst (SRC-1 p. 4: mostly to the glycerol), 98 % of the glycerol and 0.5 %
of the esters, no glycerides (ASSUMED; no LLE model, L-1). Methanol: V-102 sends 40 % of it to
the glycerol phase, as SRC-1 p. 75 states it for 90:10 ester to glycerol; its feed S8 is 91.5:8.5,
inside that condition. V-103's feed S11 is about 99:1 (48.7 kg/h of glycerol against 4072 kg/h
of esters and glycerides), outside it: there the methanol's distribution coefficient of V-102
(mass fraction in the glycerol phase over that in the ester phase, 5.4) is held constant
(ASSUMED), which sends 12.0 % of its methanol (38 kg/h) to the second glycerol phase instead of
40 %. Rejected: the 40 % at V-103, which would make a "glycerol phase" of 64 wt% methanol, a
coefficient of 14, against no source. The recovered methanol from the ester flash
(D-007) and the glycerol column (D-008) is dry and is collected in V-501 and recycled; the loop
is torn at S20 and converged by propagate (Broyden with the specs, 3 iterations; tolerance
1e-6 kg/h absolute, 1e-8 relative). The loop's only component is methanol; its exits are the
reaction and the small losses to the wastewater and the crude glycerol.

## D-007 Ester finishing (2026-11-19)
Decision:
- E-201: falling-film flash of the esters at 373 K and 40 kPa(a), one equilibrium stage,
  condensed at 315.7 K on cooling water (at least the 313.15 K of the cooling-water return plus
  its 5 K approach, D-009). Its methanol recovery is the equilibrium of that stage with the
  vapour taken as pure methanol: x = P / (gamma Psat) = 40 / (2.933 x 353.7 kPa) = 0.0386 (SRC-3,
  Dortmund UNIFAC), 17.6 kg/h of methanol left in the esters, 93.8 % of S13's off (ASSUMED as
  that value). Methanol is removed before the wash, as SRC-1 pp. 68 and 76 advise. Rejected:
  99 % at 363 K and 50 kPa(a), the first draft's value, which the equilibrium does not allow
  (x = 0.064 there; 99 % would need about 3.7 kPa(a), where methanol condenses near 272 K, below
  the cooling water); a stripping section or a second stage would recover more and is left to
  the next stage (L-7).
- C-202 / V-203: one wash with softened water, about 1 gallon per gallon of ester (SRC-1 p. 77):
  1.14 kg per kg of oil (ASSUMED rounding, 1.145 kg per kg of biodiesel), acidified with 33 wt%
  HCl 5 % over the residual methoxide (ASSUMED), which becomes NaCl and methanol (NEUT). The water
  comes in at the design ambient, 298 K, and the wash runs at 333 K (SRC-1 p. 68: 120 to 140 F):
  the hot esters (373 to 333 K, 103 kW) and LP steam (Q5, core's conversion duty, 85.5 kW) warm
  it (189 kW from 298 to 333 K). The settler sends the salts, the acid, 99 % of the glycerol,
  95 % of the methanol and 99.8 % of the water to the wastewater (ASSUMED; the split is clean,
  SRC-1 p. 69): 16.8 kg/h of methanol (0.36 wt% of the wash water) goes to treatment.
- D-204: vacuum dryer at 368 K and 10 kPa(a), 90 % of the water and all the methanol off
  (ASSUMED), condensate to the wastewater; product to 0.023 wt% water.
- E-205: product cooled to 313 K; a 5 micrometre filter to storage (SRC-1 p. 69).

## D-008 Glycerol phase and crude glycerol (2026-11-19)
Decision: the two glycerol phases are collected (V-301) and neutralised in R-302 with 33 wt% HCl
(HCl named as the usual neutraliser, SRC-1 p. 33) dosed under pH control to the methoxide's
equivalent, modelled as equal to it (ASSUMED): the crude is left near neutral, with no free acid,
as SRC-1 p. 76 asks pH control because low pH dehydrates glycerol and high pH polymerises it (the
report gives no numeric limit). C-303, a packed column at 40 kPa(a) at the top and 42 kPa(a) at
the bottom (2 kPa packing pressure drop) with reflux 1 (ASSUMED), takes 99.5 % of the methanol
overhead dry (ASSUMED), condensed at 315.7 K on cooling water, and leaves the water in the
bottoms: crude glycerol of 86.8 wt% glycerol, 8.0 wt% esters, 2.8 wt% water, 2.2 wt% NaCl,
0.17 wt% methanol, near SRC-1 p. 40's 88 %. The bottoms' bubble point at 42 kPa(a) is 404.9 K by
Raoult's law on SRC-3's vapour pressures (mole fractions water 0.133, methanol 0.0046, glycerol
0.807; the esters and salt taken as non-volatile); the reboiler runs at 405 K (S31). The real
bubble point is some K higher: glycerol-water deviates from Raoult's law and the salt lowers the
water's activity (not modelled; Dortmund UNIFAC, which has no salt, gives a lower value, 375 K,
so the ideal value is kept). LP steam (421.1 K, at most 411 K on the process side with the 10 K
approach) leaves too little margin, so the reboiler takes MP steam (1000 kPa(a), 453.0 K).
Rejected: atmospheric pressure, where the bottoms boil at 437 K by Raoult's law, out of LP
steam's reach and hotter for the glycerol; a reboiler at the 150 to 200 F at which SRC-1 p. 76
says glycerol is processed physically, which would need about 12 kPa(a), where methanol
condenses near 291 K, below the cooling water (chilled water or a vapour compressor). At 405 K
the reboiler is above that range; the pH is neutral and the reboiler's hold-up small (ASSUMED),
for the next stage to confirm (D-012). It is a co-product to sale or refining. glycerol-1 refines crude glycerol, but its feed is an
unneutralised, unstripped glycerol phase (about 60 wt% glycerol, 29 wt% methanol) of another
plant (glycerol-1 D-004); this entry does not change glycerol-1, and the two are linked by the
substance (crude-glycerol), not by composition. A soap split and a fatty-acid layer (as in
glycerol-1) do not arise without FFA (D-004).

## D-009 Utilities and duties (2026-11-19)
Decision:
- LP steam 450 kPa(a) (421 K), MP steam 1000 kPa(a) (453 K) for C-303's reboiler only (D-008),
  cooling water 298/308 K, power; minimum approaches 10 K (steam) and 5 K (cooling water)
  (ASSUMED; saturation temperatures SRC-3).
- Reactor, wash and neutraliser duties are core's (ADR 0059), from the heats of reaction and the
  components' liquid heat capacities at 333 K (SRC-3; constant, ASSUMED). Core counts a
  conversion step's other energy streams as work that ends as heat in its fluid, so each of
  these duties is net of the agitator and pump power booked on that step, and each power
  stream is booked on the step where its work is dissipated:
  - R101's Q1, 131.3 kW from LP steam: reaction 41.2 kW and the oil's warming from 298 K
    105.2 kW, less R-101's agitator and the oil feed pump (P2, 15 kW);
  - R102's Q2, 5.8 kW removed to cooling water: reaction 4.4 kW and sensible 4.8 kW, less
    R-102's agitator and the ester transfer pump (P5, 15 kW), whose work exceeds what R-102
    needs;
  - R201's Q5, 85.5 kW from LP steam: the wash water warmed from 298 to 333 K (188.9 kW) less
    the esters cooled from 373 to 333 K (103.3 kW) (D-007);
  - R301's Q9, 6.2 kW removed: reaction -2.8 kW and sensible 0.7 kW, less the neutraliser's
    agitator (P4, 4 kW).
  The methanol pumps (P1), the wash, dryer and vacuum pumps (P3) and the column's pumps and
  vacuum pump (P6) are booked on steps without a computed duty (the mixer M101, the dryer D201
  and the column C301), so they are not counted as heat.
  TRANS: +35.8 kJ/mol from the liquid enthalpies of formation (SRC-3, SRC-4), a small difference
  of large numbers whose uncertainty is of its own size: near thermoneutral. NEUT: -55.8 kJ/mol,
  ASSUMED as glycerol-1 D-005. NaOMe, NaCl and HCl get ASSUMED heat capacities (dilute; their
  effect is below 0.1 kW).
- The flash, dryer, column and cooler duties are hand estimates with their arithmetic in the
  energy streams' sources (Q3, Q4, Q6, Q7, Q8, Q10, Q11, Q12): sensible heat on the same liquid
  heat capacities, latent heats and vapour heat capacities from SRC-3 (L-4). Each condenser
  follows its vapour's path (cooled to its dew point, condensed, subcooled), and each heater is
  the condenser's duty plus the net enthalpy change of the step's liquids, so that every step's
  energy balance closes on the entry's own heat capacities.
- Power: 74 kW in all (agitators, pumps, vacuum pumps; ASSUMED), 0.018 kWh per kg; SRC-2's
  model plant uses 439 Btu/gal, 0.039 kWh per kg (benchmark).
- Steam: 502.2 kW of LP-steam heat (Q1, Q3, Q5, Q6) and 128.5 kW of MP-steam heat (Q10),
  0.124 and 0.032 kWh per kg, 0.156 in all; 389.3 kW to cooling water, 0.096 kWh per kg. SRC-2's
  model plant uses 3,550 Btu/gal of natural gas and steam (0.31 kWh per kg as fuel, 0.25 as
  steam at the boiler's 80 %, SRC-2 p. 9).
- No heat integration (L-6): the dryer's feed heated from 333 to 368 K and its product cooled
  back (Q6 and Q8, about 96 and 141 kW), the flash's feed heated and the column's bottoms cooled
  could exchange heat; the wash already takes the flashed esters' heat.

## D-010 Equipment sizes (2026-11-19)
Decision: first sizes from the flows (equipment/equipment-list.yaml, ASSUMED): R-101 8 m3 (1 h,
SRC-1 p. 33's upper end), R-102 4 m3 (0.5 h), decanters 8 m3 each (1 h, SRC-1 p. 67 gives 1 to
8 h and L/D 5 to 10; a centrifuge is the alternative), wash settler 10 m3. Design pressures,
temperatures and materials are left to basic engineering.

## D-011 Preliminary gate-to-gate LCI (2026-11-19)
Decision: `lca/lca.yaml` with every exchange of the flowsheet, per kg of biodiesel S27, mass
allocation between biodiesel and crude glycerol (0.8931 / 0.1069 by the streams S27 and S32):
the library hierarchy (docs/system-model.md) would take energy content only for co-produced
fuels, and crude glycerol goes to a glycerol refinery here; the WBCSD rule needs prices, which
are not sourced, so mass is used, as SRC-2 (pp. 7-9) allocates the conversion energy. The
deviation (prices, economic allocation) is recorded in lca.yaml. Links: methanol to methanol-1,
both hydrochloric acid feeds to hydrogen-chloride-1, LP steam as heat (lca/mappings.yaml).
Gaps with recorded proxies: refined soybean oil (crushing, degumming and alkali refining; the
meal as the crushing's co-product), sodium methoxide 25 wt% in methanol (from NaOH and methanol
with water removal, or from sodium; its methanol from methanol-1 and its sodium from
chlor-alkali-1, not linked); power, cooling water, process water and wastewater treatment
unmapped. The biogenic carbon of the oil's chains goes to the esters; the methanol's carbon is
fossil (about 5 % of the ester's carbon by the stoichiometry: 1 C of 19). `carbon_accounting`
in lca.yaml declares the oil's carbon biogenic (fraction 1.0) and the methanol and the
methoxide solution fossil: of 3320 kg C/h in, 3148 is biogenic (`cheme assess lca --balance`).
MP steam (D-008) is linked as heat like the LP steam.

## D-012 Hazards (2026-11-19)
Methanol is highly flammable (flash point near 10 C) and toxic (SRC-1 pp. 32, 75); sodium
methoxide solution is flammable and corrosive and reacts with water; hydrochloric acid is
corrosive. Hazards for the next stage: methanol inventory in the reactors, decanters, glycerol
collection tank, flash, column and drums (inerting, vent condensers, area classification; the
vents are emission exclusions in lca.yaml, not estimated); vacuum equipment (E-201, D-204,
C-303: air ingress into methanol vapour); hot oil and esters; chloride corrosion in the
neutraliser, the wash and C-303's reboiler. The glycerol at C-303's reboiler (405 K, MP steam at
453 K on the tubes) is hotter than the 150 to 200 F at which SRC-1 p. 76 says glycerol is
processed physically; acid or base there would dehydrate or polymerise it (SRC-1 p. 76), so the
neutraliser's pH control (D-008) and the reboiler's skin temperature and hold-up are for the
HAZOP. The transesterification is near thermoneutral (D-009) in liquid-full continuous
reactors: no runaway screening applies (D-003). No HAZOP at this stage.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| oil feed for 32 420 t/a, fresh methanol for 6:1 | done in cheme (design specs) | D-002, D-005, core ADR 0070 |
| methanol recycle | done in cheme (tear S20) | D-006, core ADR 0060 |
| reactors and neutralisations | done in cheme (conversion), conversions ASSUMED | D-005, D-007, D-008 |
| decanters, flash, wash, dryer, column | done in cheme (component separators), recoveries ASSUMED | D-006 to D-008, core ADR 0070 |
| reactor and neutraliser duties | done in cheme (conversion duties) | D-009, core ADR 0059 |
| flash, dryer, column and cooler duties | by hand (sources of Q3, Q4, Q6 to Q8, Q10 to Q12) | D-009 |
| ester flash's methanol recovery | by hand: one equilibrium stage, Dortmund UNIFAC (thermo) | D-007, SRC-3 |
| glycerol column's bottoms temperature | by hand: bubble point by Raoult's law (thermo) | D-008, SRC-3 |
| stream properties | not done: no package covers these liquids | L-1 |
| LCI inventory | done, most backgrounds unmapped | D-011 |

## Core features used (core 1.12.0)

- `specs:` (ADR 0070): an `annual` target on the product with four followers at fixed ratios to
  the oil, and a molar `ratio` target of methanol to oil solved by the fresh methanol.
- `tears:` (ADR 0060) for the methanol recycle, solved together with the specs.
- `recovery:` component separators (ADR 0070) for V101, V102, E201, V201, D201 and C301.
- Conversion reactors with a step `conversion:` override (R102) and `energy_port:` beside a
  power stream; the conversion duties (ADR 0059) with `liquid_heat_capacity` of every component,
  net of the step's power streams (counted as work into its fluid).
- `carbon_accounting` (biogenic content of the oil) in the LCA.
- `cheme assess lca` with `allocation: shares`, `emission_exclusions` and the dataset.

## Core limits hit (each a candidate core issue)

- L-1: no qualified liquid-liquid model for FAME-glycerol-methanol (an NRTL system in core's
  LLE data) and no property package for triglycerides, esters and glycerol: the decanters', the
  wash's and the column's splits are specified, not predicted, and no stream property or
  enthalpy is calculated (`cheme process props --coverage`: no package). V-103's methanol split
  holds V-102's distribution coefficient constant outside the source's condition (D-006); the
  flash's recovery and the column's bottoms temperature are hand calculations outside core
  (D-007, D-008), the latter without the salt's effect.
- L-2: no liquid-phase kinetics or equilibrium of the three consecutive transesterification
  steps on a lumped oil: the conversions are design specifications (a `cstr` model would need
  sourced rate laws per step and the two-phase character of the reaction).
- L-3: lumps: one triglyceride and one ester for a mixture of chains; mono- and diglycerides,
  FFA, soaps and water side reactions (saponification) are not represented.
- L-4: a component separator has no temperature, pressure or duty model: the flash's, dryer's
  and column's duties are hand estimates; a shortcut continuous column or a flash on an activity
  model would replace them.
- L-5: a conversion step's duty uses constant liquid heat capacities (given at 333 K) and the
  given temperatures; a temperature-dependent cp would refine Q1 and Q5.
- L-6: no heat integration done (the pinch tools need stream data with properties, L-1).
- L-7: about 17 kg/h of methanol (0.0041 kg per kg of biodiesel) leaves the flash with the esters
  and goes with the wash water to treatment (D-007); a stripping section on E-201 or a methanol
  stripper on the wash water would recover it (not designed).

## Open inputs
Kinetics and equilibrium of the transesterification on soybean oil; LLE data or NRTL parameters
for FAME-glycerol-methanol(-water); the oil's fatty-acid profile and FFA; residence times and
decanter performance from a plant or pilot; the product specification to EN 14214 (not read
here) or ASTM D6751; prices of biodiesel and crude glycerol for the allocation; a TEA; P&IDs,
layout, HAZOP.
