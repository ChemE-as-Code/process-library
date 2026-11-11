# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Potassium tert-butoxide (KOtBu) from potassium metal and dry tert-butanol, issue
ChemE-as-Code/process-library#418: the feed `feed:KOTBU` of `di-tert-butyl-dicarbonate-1` links
to this entry's product kg for kg. Concept stage: design basis, batch recipe, balanced BFD/PFD,
thermal screening with a rate sensitivity and a preliminary gate-to-gate LCI. Out of scope here:
P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-06): library `main` at d5de92a1, which pins cheme-as-code 1.10.0
(c55e9c7). The batch entries `p-toluenesulfonyl-chloride-1`, `benzoyl-chloride-1`,
`acetyl-chloride-1` and `di-tert-butyl-dicarbonate-1` are the templates; the core features used
are listed below (Core features used), the limits hit at the end (Core limits hit).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents' text of the original; no paragraph numbers, so the locator is
the part of the document).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | Organic Syntheses, Coll. Vol. 4, p. 132 (1963); Vol. 30, p. 18 (1950): W. S. Johnson and W. P. Schneider, beta-Carbethoxy-gamma,gamma-diphenylvinylacetic acid, doi:10.15227/orgsyn.030.0018 | procedure: 2.15 g (0.055 g-atom) of potassium in 45 mL of dry tert-butanol boiled under reflux under nitrogen until dissolved, hydrogen liberated through a mercury trap; Note 2: tert-butanol dried by refluxing over sodium and distilling; Note 3: the safe handling of potassium (cut under dry xylene, residues destroyed at once with tert-butanol: they have exploded even under a protective liquid); Note 4: with dry alcohol and apparatus the dissolution is slow, more than 4 h of refluxing | read (the procedure's PDF from orgsyn.org); facts only | D-001, D-004, D-005, D-011 |
| SRC-2 | Organic Syntheses, Coll. Vol. 5, p. 1060 (1973); Vol. 41, p. 101 (1961): I. Ugi and R. Meyr, o-Tolyl isocyanide, doi:10.15227/orgsyn.041.0101 | procedure: 1250 mL of dry tert-butanol distilled into the flask under nitrogen, 100 g (2.6 g-atoms) of potassium added in about ten pieces; the stirred mixture warms by itself to the metal's melting point in 15-60 min, the metal disperses into droplets and dissolves, the temperature rising to the alcohol's boiling point; the rate, set by the stirring, kept to a gentle reflux, the stirrer stopped and the flask cooled if the boiling becomes too vigorous; the alkoxide precipitates as a thick suspension (Note 1: less alcohol than dissolves it) | read (PDF from orgsyn.org); facts only | D-001, D-005, D-011 |
| SRC-3 | Organic Syntheses, Coll. Vol. 6, p. 418 (1988); Vol. 57, p. 45 (1977): B. M. Pope, Y. Yamamoto, D. S. Tarbell, Di-tert-butyl dicarbonate, doi:10.15227/orgsyn.057.0045 | Note 3: alcohol-free potassium tert-butoxide (commercial); a 1:1 complex of the alkoxide with tert-butanol is much less soluble in ethereal solvents than the alcohol-free alkoxide | read (PDF from orgsyn.org); facts only | D-007, D-008 |
| SRC-4 | US4577045A, Dynamit Nobel AG, 1984/1986: Method for the production of anhydrous potassium tert.butoxide, https://patents.google.com/patent/US4577045A/en | from 50 wt% potash lye and tert-butanol (6 to 20 times its volume) with cyclohexane or hexane in a packed column, the water taken overhead, the sump a 10-18 wt% solution at its boiling point; the prior art: potassium metal with absolutely dry tert-butanol (difficult metal handling, the dry alcohol hard to make), transalcoholisation, and an azeotropic column that incrusts with KOH; Example 1: the product concentrated at 40 C and 100 mbar, dried at 160 C and 10 mbar, KOH 0.4 % | read; patent, facts only | D-001, D-004, D-008 |
| SRC-5 | US5053560A, Huels AG (R. Matthes, H. Rauleder, H.-J. Vahlensieck), published 1991-10-01: Method for the continuous production of potassium tert-butoxide, https://patents.google.com/patent/US5053560 | from 50-60 wt% KOH with excess tert-butanol and methylcyclohexane or n-heptane in a column; the alcohol may hold moisture up to 11.76 wt%, the composition of the tert-butanol/water azeotrope; 14 % solutions, 0.73-0.76 % KOH; the solid by removing the alcohol under vacuum | read; patent, facts only | D-001, D-004 |
| SRC-6 | US6150569A, Huels AG (C. H. Hamann, J. Helling, P. Schmittinger), priority 1998, granted 2000: Process for preparing alkali metal alkoxides, in particular potassium tert-butoxide, by microheterogeneous catalysis, https://patents.google.com/patent/US6150569 | potassium amalgam with tert-butanol over Mo2C or WC at reflux; prior art: higher alcohols react with the alkali metals above the metal's melting point, and KOtBu only in an unsatisfactory space-time yield even in an autoclave at 140 C and 7 bar; examples give 7-14 % solutions with 1.4-1.6 % KOH | read; patent, facts only | D-001 |
| SRC-7 | Wikipedia, Potassium tert-butoxide, https://en.wikipedia.org/wiki/Potassium_tert-butoxide | made from dry tert-butanol and potassium metal, the solid by evaporating the solution and heating it, purified by sublimation; molar mass 112.213; melting point 256 C (529 K); sublimes at 220 C at 1 mmHg and 140 C at 0.01 hPa; the solvate [tBuOK.tBuOH] and the tetramer; H228, H252 (self-heating in large quantities), H314 | read; CC BY-SA, facts only | D-001, D-008, D-011 |
| SRC-8 | Wikipedia, Potassium, https://en.wikipedia.org/wiki/Potassium; Wikipedia, Hydrogen safety, https://en.wikipedia.org/wiki/Hydrogen_safety | potassium: melting point 336.7 K, liquid density 0.828 g/cm3 at it, reacts vigorously with water and the heat ignites the hydrogen, handled air-free, made by reducing KCl with sodium (dominant since the 1950s) or by electrolysis of KOH; hydrogen: flammable at 4-75 vol% at atmospheric pressure, detonable at 18.3-59 vol% in air, minimum ignition energy 0.02 mJ | read; CC BY-SA, facts only | D-004, D-011, D-012 |
| SRC-9 | Property data of core's environment and the NIST WebBook: the NIST Chemistry WebBook, SRD 69 (https://webbook.nist.gov; tert-butanol C75650: Antoine constants of Brown, Fock et al. 1969 and Beynon and McKetta 1963, heats of vaporization 39.07 kJ/mol at 355.5 K (Majer and Svoboda), 40.0 at 349 K, 37.2 at 368 K, normal boiling point 355.5 K, fusion 298.3 K; water C7732185 Antoine constants of Stull 1947); the `chemicals` 1.5.2 and `thermo` 0.6.1 packages (MIT, the versions core pins): CRC Handbook tables as packaged in `chemicals` (KOH's formation enthalpy -424.6 kJ/mol, solid heat capacity 68.9 and density 2.044 g/cm3; potassium's solid heat capacity 29.6, its heat of fusion 2.27 kJ/mol and melting point 336.65 K; tert-butanol's -359.2 and water's -285.8 kJ/mol as liquids, their heat capacities 218.6 and 75.3; the printed handbook not read), the NIST WebBook values packaged there (NaOCH3 -374.4 kJ/mol), thermo's ZABRANSKY_SPLINE_C (tert-butanol's liquid heat capacity 229.1, 246.4, 257.0, 265.5 kJ/(kmol K) at 308, 331, 348, 365 K: Zabransky et al.'s evaluated data), TRCIG (tert-butanol's ideal-gas heat capacity 129.9-151.5 kJ/(kmol K) at 353-433 K), WEBBOOK_SHOMATE (molten potassium 32.03 kJ/(kmol K)), CRC_INORG_L (molten potassium 824 kg/m3 at 353 K), and DIPPR_PERRY_8E for tert-butanol's liquid molar volume (0.1023 m3/kmol at 348 K), whose coefficients thermo takes from Perry's Chemical Engineers' Handbook, 8th ed., drawing on DIPPR 801 (not read here; a single fact with this source, not open data, library ADR 0037); CoolProp's IAPWS water (steam saturation 412.0 K at 350 kPa(a) and 453.0 K at 1000 kPa(a), water's heat of vaporization 41.58 kJ/mol at 353 K) | per component in `process/materials.yaml`, `process/reactions.yaml`, the flowsheet's hand duties and `scripts/makeup_drying.py` | NIST WebBook pages read (2026-11-06); open-source packages queried; single values, facts only | materials, D-005, D-007, D-009 |
| SRC-10 | processes/tert-butanol-1, asu-1 (this library) | tert-butanol by direct hydration of isobutene, a Tier 0 dataset per kg of tert-butanol contained, the drying past the azeotrope left out (its README); gaseous nitrogen | library, internal | D-004, D-012 |
| SRC-11 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and the criticality classes of a semi-batch (method, implemented in core ADRs 0050, 0058) | method reference, no data taken | D-011 |
| SRC-12 | Ullmann's Encyclopedia of Industrial Chemistry, Alkoxides (and Potassium) | - | not read (licensed) | nothing taken |

Searched and not found openly (2026-11-06): kinetics or reaction calorimetry of potassium with
tert-butanol; a formation enthalpy of potassium tert-butoxide; its solubility in tert-butanol
against temperature, the solvate's decomposition temperature and heat; a TD24 or DSC onset of the
alkoxide or its solutions; a plant's specific consumptions; an open product specification; the
heat of adsorption of water on a 3A sieve at these conditions. A ChemicalBook page found by the
search (a laboratory preparation dried at 180-190 C) is not used.

## D-001 Route and boundary (2026-11-06)
Decision: potassium metal with an excess of dry tert-butanol (SRC-1, SRC-2, SRC-7), on a
dedicated train (D-013):
- V-102: the potassium melted at 353 K under nitrogen;
- R-101: the molten metal dosed over 3 h into 8.6 mol of dry tert-butanol per mol at 348 K,
  K + (CH3)3COH -> (CH3)3COK + 1/2 H2; the make-up's water reacts first, K + H2O -> KOH + 1/2 H2;
  the hydrogen vented as it forms through the vent condenser E-104 to the flare;
- C-101: the alcohol stripped at 101 kPa(a) down to the 1:1 solvate (SRC-3, SRC-7);
- DR-101: the solvate paste vacuum-dried at 433 K to the alcohol-free powder, cooled to 313 K and
  discharged under nitrogen;
- T-201: the stripped and the dried-off alcohol recycled to the next charge, 0.5 % purged;
- T-101, A-001: the make-up, tert-butanol of the azeotrope grade, dried on a vapour-phase 3A
  molecular sieve (D-004).
Boundary feeds: potassium metal, the azeotrope grade's tert-butanol (tert-butanol-1) and its
water, electricity, LP and MP steam, nitrogen (per batch); returns: the tempered-water loop's
heat to the site's cooling water (D-009); outputs: the
dried alkoxide, the vent gas to the flare, the alcohol purge to incineration, the sieve's
regeneration condensate to wastewater treatment.
Reason: the issue names this route; it is the one the open sources describe (SRC-7, SRC-1 and
SRC-2 at laboratory scale, SRC-4 as the prior art of its own route), and the one that makes the
alkoxide free of KOH and water save for what the make-up brings. It is the dosed, gas-evolving,
stripped and dried batch the 1.8.0 to 1.10.0 features are for.
Rejected, recorded as variants:
- aqueous KOH with excess tert-butanol and an entrainer (cyclohexane, hexane, methylcyclohexane
  or n-heptane) in a continuous column, the water taken overhead (SRC-4, SRC-5): no metal, and
  it tolerates the azeotrope's water, but it is a continuous column with its own entrainer
  recycle, and its product keeps 0.4-0.8 % KOH (SRC-4, SRC-5) against this route's 0.23 %; a
  continuous-track variant once a KOH producer is linked (chlor-alkali-1 makes NaOH, not KOH);
- potassium amalgam over a carbide catalyst (SRC-6): 7-14 % solutions after 17-20 h in the
  examples, and a mercury cell behind it;
- transalcoholisation of a lower potassium alkoxide (SRC-4's prior art): a large alcohol excess,
  an equilibrium against the product;
- hydrogen recovery (D-012): the hydrogen is 7.5 kg a batch, saturated with the alcohol and
  diluted by the header's nitrogen; it is flared, not credited.
Links: tert-butanol from tert-butanol-1 (kg of alcohol contained), nitrogen from asu-1. No
library process makes potassium metal (or the sodium its thermal route needs).

## D-002 Capacity, product and operating hours (2026-11-06)
Decision: 1000 t/a dried potassium tert-butoxide, 7920 h/a (330 days of 24 h), ASSUMED. Modelled
product: 99.47 wt% KOtBu, 0.23 wt% KOH (the make-up's water), 0.30 wt% tert-butanol (the
dryer's residual, D-008), 3.5 ppm(wt) of unreacted potassium. **The 99.47 wt% is an upper bound,
not a specification**: the metal's sodium (giving sodium tert-butoxide), moisture and CO2 picked up
in handling and packing, and any decomposition in the dryer are not modelled, and no open product
specification was read. The commercial grade's specification is an open input.
Reason: no open market figure was found; the alkoxide is a fine-chemical base, larger than the
500 t/a of di-tert-butyl-dicarbonate-1 (which needs 1.150 kg per kg, 575 t/a). The LCI is per kg
and does not depend on the scale; the batch size does (D-003).

## D-003 Batch basis, recipe and vessels (2026-11-06)
Decision: one batch makes 831.6 kg of dried alkoxide (stream S15); the recipe
(`process/recipe.yaml`) has three unit procedures:
- REACT on R-101, one vessel over E101 and R101 (`units`, core ADR 0057): nitrogen purge 0.5 h,
  charge 1.0 h, warm 316.87 -> 348.15 K 0.343 h (from the jacket, with the vessel's metal, core
  ADR 0063), dose 3.0 h and post-reaction 0.743 h to 0.99999 conversion of the potassium (both
  from R101's model), transfer 1.0 h: 6.586 h;
- STRIP on C-101: receive 1.0 h (R-101's transfer), distil 1.317 h (ST101's boil-up), transfer
  the paste 1.0 h: 3.317 h;
- DRY on DR-101 over D101 and E103: receive 1.0 h, dry 3.037 h (D101's drying rate on 15 m2),
  cool 1.5 h, discharge 0.5 h: 6.036 h.
R-101 is the bottleneck: cycle 6.586 h, 1202 batches in 7920 h; one batch takes 13.94 h from the
purge to the dryer's discharge. The flowsheet's flows are the recipe's year averages: 831.6 kg x
1202.4 / 7920 h = 126.26 kg/h of S15 (no `cheme.recipe-basis` finding); the batch size was found
by fixed-point iteration (the warm-up time depends on the vessel, so on the batch: L-7).
Dosing time: 3 h. R-101's jacket (stainless steel, U 400 W/(m2 K) ASSUMED, 15.7 m2 wetted at the
charge, tempered water 303/313 K at its log-mean equivalent 308.36 K, D-009) removes 249.2 kW against the
model's peak of 92.68 kW, so the jacket would allow a shorter dosing; the 3 h are kept for the
vent (the normal peak 102.5 m3/h before the vent condenser, D-006) and for the margin a
dosing-controlled reaction needs (D-011).
Vessels (fill 0.8, H/D 1.2, ASSUMED): R-101 10 m3 (6.55 m3 of batch, 65 %), C-101 10 m3 (the same
solution), DR-101 3.15 m3 (fill 0.6, 1.531 m3 of paste at an ASSUMED 900 kg/m3, 49 %), heated area
15 m2 (a paddle dryer's jacket and shaft). Metal: R-101 and C-101 about 6 t of steel each, 3000
kJ/K (core ADR 0063); DR-101 2000 kJ/K (D-008).
Reason: core ADR 0051 puts the batch basis in one place, so that the balance, the LCI per kg and
a later TEA share it; the dosing, reaction, warm-up, distillation and drying times come from the
models.

## D-004 Feeds and charge (2026-11-06)
Decision:
- Potassium: technical metal, 43.9613 kg/h (1.12439 kmol/h), taken as pure (its sodium and oxide
  not modelled); melted in V-102 on a closed thermal-oil circuit to 353.15 K, 16.5 K above its
  melting point, and pressed into R-101 with nitrogen.
- The charge: 8.60 kmol of tert-butanol per kmol of potassium dosed (S9 717.22 kg/h, 8.6046 on
  the propagated streams), the ratio of SRC-1 (45 mL, 35 g, 0.47 mol for 0.055 g-atom) and enough
  to keep the alkoxide dissolved at the end: 16.6 wt% KOtBu at 348 K (S10), within the 10-18 wt% SRC-4
  runs its boiling solution at (ASSUMED to hold at 348 K, L-2). SRC-2's 5 mol per mol gives a thick
  suspension (its Note 1), which the one-phase model cannot carry.
- The make-up: the azeotrope grade, 92.7064 kg/h of tert-butanol (S3) with its 11.76 wt% water
  (S4, 12.3553 kg/h; SRC-5), set so that R-101's charge holds the ratio above, from the
  recycle's steady state (D-007).
- **The drying past the azeotrope (A-001).** tert-butanol-1 counts the alcohol contained and
  leaves out the drying past the azeotrope (SRC-10), while the metal needs a dry alcohol (SRC-1,
  SRC-4: absolutely dry). Each kg of water left in the charge costs 2.17 kg of potassium as KOH
  and releases hydrogen. The make-up is therefore dried here, in a vapour-phase 3A molecular-sieve
  unit with an electrically heated nitrogen regeneration loop (ASSUMED design; the technique of
  ethanol dehydration, not sourced for tert-butanol), to 0.1 wt% water (ASSUMED; SRC-4's alcohol
  is below 0.1 %, preferably 0.05 %), 1 % of the make-up's alcohol going to the regeneration
  condensate (ASSUMED). Core has no adsorption model, so the unit is a specified split with its
  duties from `scripts/makeup_drying.py` (L-4, library ADR 0027): the evaporator 28.14 kW of LP
  steam, the product condenser 31.44 kW and the regeneration condenser 15.09 kW of cooling water,
  the regeneration heater and blower 19.40 kW of electricity (an ASSUMED heat of adsorption of 3.6
  MJ per kg of water, times 1.5 for the bed and the gas). The dried make-up's 0.1 wt% water is
  then 0.0919 kg/h (0.1 wt% of S6's 91.87 kg/h; 0.00510 kmol/h, the KOH of S10), which takes 0.45 %
  of the potassium to KOH.
Rejected: drying with sodium as in SRC-1 (a second metal, and a sodium alkoxide in the product);
buying an anhydrous grade (no library producer: the drying would be a gap); feeding the azeotrope
to R-101 (each kg of the azeotrope would take 0.26 kg of potassium to KOH).

## D-005 Reaction models, kinetics and heats (2026-11-06)
Decision (`process/reactions.yaml`):
- KTBA, K + tBuOH -> KOtBu + 1/2 H2, liquid phase, first order in the metal "dissolved" (the
  alcohol in large excess), k = 3.0e-3 1/s at 348.15 K, Ea 40 kJ/mol (A = 3010 1/s), ASSUMED: the
  metal disperses into droplets and dissolves at a rate the stirring sets (SRC-2), so this is an
  effective rate of the agitated dispersion, not a mechanism (L-1); the 6 min time constant makes
  the dosing control the heat (D-011). SRC-1's more than 4 h for undispersed pieces in a flask at
  reflux is the slow end, which the sensitivity covers (k/100, D-011).
- WAT, K + H2O -> KOH + 1/2 H2, k = 100 m3/(kmol s) at 348.15 K, ASSUMED fast: its extent is the
  water fed.
- Heats, ASSUMED (no open formation enthalpy of KOtBu, no calorimetry): KTBA -135 kJ/mol, the
  order of its analogues computed from the packaged formation enthalpies (SRC-9): Na + CH3OH(l) ->
  NaOCH3(s) + 1/2 H2, -136.0 kJ/mol, and K + H2O(l) -> KOH(s) + 1/2 H2, -138.8 kJ/mol; WAT -138.8
  kJ/mol. The hydrogen is formed as a gas at the vessel's temperature (core ADR 0054). The heat of
  solution of the alkoxide in the alcohol is not known and is inside the -135.
- Temperature: 348.15 K, above the metal's melting point (336.65 K) so that it stays molten and
  dispersed, and 7.3 K below the alcohol's boiling point, so that the batch does not reflux in
  normal operation (SRC-2 runs at reflux; here the boiling is kept as the margin, D-011).
Result (`cheme process reactors`): 1.11928 kmol/h of KTBA and 0.00510 kmol/h of WAT, the potassium
converted to 0.99999 after a 0.743 h post-reaction; the model's duty 24.51 kW year average (the
reactions' 42.17 kW less the vent vapour's 14.16 kW of evaporative cooling, less the condensate's
3.54 kW warmed back, the dose 0.05 kW) on Q2; the yield is 99.55 % on potassium.

## D-006 The vent, its vapour and condenser (2026-11-06)
Decision: the hydrogen leaves the liquid as it forms (batch.vent, core ADR 0054), saturated with
tert-butanol at 348.15 K (vent vapour, core ADR 0062: Raoult on the NIST line, the dissolved
alkoxide counted in the liquid), through the vent condenser E-104 at 308.15 K, whose condensate
returns to R-101. Core gives: 1.305 kmol/h of alcohol carried off, 1.241 kmol/h condensed, the
condenser's 17.38 kW written on Q3; the gas past it, S11, 0.5622 kmol/h of hydrogen with 0.0637
kmol/h of alcohol (10.2 % of the gas, its saturation at 308 K), to the flare. Per batch 38.58 kg:
7.47 kg of hydrogen and 31.1 kg of tert-butanol (`cheme process recipe`).
The condenser's 308.15 K is set by the alcohol's freezing point (298.3 K): a colder condenser on
brine would freeze the condensate. The gas outlet temperature is not enough: in the counter-current
E-104 the gas outlet end meets the coolant's supply, and with a gas of 90 mol% hydrogen (S11) the
gas-side film coefficient is low, so the tube wall there runs close to the coolant's temperature.
On the site's cooling water (298.15 K, colder in winter) that wall would be below the freezing
point and the condensate could freeze on the tubes and block R-101's vent (D-011). E-104 is
therefore on the tempered-water loop, supply 303.15 K, return 313.15 K (D-009): the wall cannot be
colder than 303.15 K, about 5 K above the freezing point, and the gas leaves 5 K above the supply
(the loop's minimum approach). The alcohol it lets pass, 4.72 kg/h, is the largest loss of
the alcohol (5.1 % of the make-up; 5.7 % with the dryer's bleed, D-008). A second, colder stage
with defrosting, or a scrubber of the vent gas, would recover most of it: a variant (open input).
Normal peak: 0.3817 mol/s past E-104 at the end of the dosing (34.75 m3/h at 308 K); before E-104,
in R-101's vent line, the 0.3428 mol/s of hydrogen carry their 0.656 vapour share (core): 0.997
mol/s, 102.5 m3/h at 348 K. The vent line and E-104 take 200 m3/h (`hazard.vent_capacity`,
ASSUMED, D-011).

## D-007 Alcohol strip and recycle (2026-11-06)
Decision: the solution is stripped in the batch still C-101 at 101.325 kPa(a) (core ADR 0055,
Raoult's law, an ideal liquid of tert-butanol with the alkoxide and KOH as non-volatile solutes,
ASSUMED: the solvation and the precipitation of the solvate are not modelled, L-2), with a
constant boil-up of 400 kW (LP steam on its jacket and coil), the charge heated to its bubble
point and the vessel's metal in the duty (`still.heat_up`, `metal_heat_capacity`, core ADR
0063), until tert-butanol is 50 mol% of the residue, the 1:1 solvate (SRC-3, SRC-7). Core gives:
the still from 358.65 to 374.25 K, 1.317 h of boil-up, 3597 kg of alcohol a batch (S12, 546.1
kg/h), the residue 1378 kg a batch (S13, 209.2 kg/h); the reboiler 90.12 kW year average (79.96
boil-up, 6.85 the charge's heat-up, 3.30 the metal) on Q4 and the condenser 79.96 kW on Q5 (core
ADRs 0059, 0061). The heat of vaporization is one value per component (39.07 kJ/mol, its normal
boiling point's), within 5 % of the values at 349 and 368 K (SRC-9). The distillate leaves the
total condenser at the alcohol's boiling point, 355.45 K (not subcooled).
Recycle: the distillate and the dryer's condensate (S18) mix in T-201 at 349.25 K (M201, adiabatic
on the components' liquid heat capacities), are cooled to 318.15 K in E-202 (18.82 kW, Q13) and
return to R-101's charge (S19, 625.4 kg/h); 0.5 % is purged to incineration (S22, ASSUMED, to keep
the loop's trace impurities from building up: isobutene, di-tert-butyl ether or the make-up's own
traces, none modelled). The loop is torn at S19 and converged by core (Wegstein, core ADR 0060);
its gain is 0.995, so the recycle's steady state is (1 - purge)/purge = 199 times sensitive to the
make-up's surplus: the make-up S3 is set by hand to hold the charge ratio (L-8). The charge S8 is
the mix of the dried make-up (308.15 K) and the recycle (318.15 K): 316.87 K.

## D-008 Drying and product (2026-11-06)
Decision: the solvate paste is dried in the vacuum paddle dryer DR-101 at 433.15 K (core ADR 0057)
to 0.3 wt% tert-butanol (ASSUMED), under a mean 5 kPa(a), ending at about 1 kPa(a), after SRC-4's
drying at 160 C and 10 mbar (Example 1) and SRC-7's "evaporating and heating". The heating medium
is MP steam at 453 K, below the alkoxide's sublimation at 493 K and 0.13 kPa (SRC-7) and its
melting point 529 K (SRC-7); the paste stays below 433 K (SRC-4's 160 C). At 433 K the alkoxide's
vapour pressure is about 0.004 kPa (Clausius-Clapeyron between SRC-7's two sublimation points,
493.15 K at 0.133 kPa and 413.15 K at 0.001 kPa), at most about 0.4 % of the vapour at the final 1
kPa: it condenses with the alcohol in E-201 and returns in the recycle (recorded exclusion, not
modelled).
Dryer energy (ASSUMED): the paste 2.2 kJ/(kg K) (60 wt% alkoxide at 1.34, 40 wt% alcohol at
3.47), the latent heat 800 kJ/kg (the alcohol's 527 kJ/kg at its boiling point and an ASSUMED 20
kJ/mol, 270 kJ/kg, to break the solvate's hydrogen bond; no open value), 80 % efficiency; DR-101's
metal, about 4 t of steel at 0.5 kJ/(kg K) = 2000 kJ/K, reheated each batch from the 313.15 K it
was cooled to, while core heats the vessel from the paste's inlet temperature (374.25 K), so 2000 x
120 / 58.9 = 4075 kJ/K is entered (L-5). Core's dryer gives 45.11 kW year average (sensible
27111.5, evaporation 66371.1, vessel 36441.9 kJ/h, at 80 %) on Q6 (45.1127 kW, copied from `cheme
process crystallizers` at its precision), 1070 MJ a batch, and 82.96 kg/h of vapour, 546.4 kg a
batch; the drying 3.037 h at an ASSUMED 12 kg/(m2 h) on 15 m2 (2.7 kW/m2 at 800
kJ/kg, less than n-bromosuccinimide-1's 5 kg/(m2 h) of water at 333 K, 3.3 kW/m2).
The vapour is compressed by a dry screw vacuum pump and condensed at atmospheric pressure at
308.15 K in E-201 (Q8, 21.02 kW: 19.18 kW for the vapour desuperheated, condensed and cooled,
1.845 kW the pump's work). The nitrogen bleed (10 Nm3 a batch, 0.446 kmol, D-012) leaves E-201
saturated with the alcohol at 308 K (10.32 kPa, 0.1134 kmol per kmol of nitrogen): 0.0506 kmol,
3.75 kg a batch, 0.6864 % of the 546.4 kg of vapour (SP201's split), to the flare.
The product is cooled in DR-101 to 313.15 K before discharge (E103, Q7 15.77 kW: the product's
20346 kJ/h and the metal's 240 MJ a batch) and packed under nitrogen.

## D-009 Utilities and heat (2026-11-06)
Decision: LP steam 350 kPa(a) (412.0 K), MP steam 1000 kPa(a) (453.0 K), tempered water 303/313 K
on a closed loop cooled by the site's cooling water 298/308 K, electricity (ASSUMED design basis).
Every cooling duty is on the tempered water (the flowsheet's CW): R-101's jacket and its vent
condenser E-104, C-101's condenser, DR-101's jacket (product cooling) and the dryer's vapour
condenser E-201, the recycle cooler E-202 and the sieve's condensers. tert-butanol freezes at
298.3 K, and a condenser's tube wall runs close to its coolant's temperature (D-006): the site's
cooling water, at 298 K and below in winter, would let the alcohol freeze on the walls. The loop's
supply is held at 303.15 K, and never below 303 K in tert-butanol service, by a three-way valve
bypassing its plate exchanger on the site's water (which fails to bypass; a low supply
temperature alarms and trips R-101's dosing, D-011); its heat ends in the site's cooling water,
so the LCI counts it as cooling water removed. Every energy flow of the batch is a stream of the
flowsheet:

| stream | what | kW | from |
|---|---|---|---|
| Q1 | R-101's charge warmed 316.87 -> 348.15 K, with its metal | 25.57 | cheme process recipe (heat operation) |
| Q2 | the heat of reaction less the vent vapour's cooling | 24.51 | R101's model |
| Q3 | R-101's vent condenser E-104 | 17.38 | R101's model |
| Q4 | the still's reboiler (boil-up, heat-up, metal) | 90.12 | ST101's model |
| Q5 | the still's condenser | 79.96 | ST101's model |
| Q6 | the paddle dryer | 45.11 | D101's dryer model |
| Q7 | the product and DR-101's metal cooled to 313 K | 15.77 | hand |
| Q8 | the dryer's vapour condenser E-201 with the vacuum pump's heat | 21.02 | hand |
| Q9 | potassium melted to 353 K | 1.23 | hand |
| Q10, Q11, Q12 | the sieve's evaporator, product and regeneration condensers | 28.14, 31.44, 15.09 | scripts/makeup_drying.py |
| Q13 | the recycle cooler E-202 | 18.82 | hand |
| Q14 | tank and line heating (T-101, T-201, V-102, the alcohol's lines), ASSUMED | 5.0 | hand |
| P1..P4 | agitators of R-101 (10.17) and C-101 (2.77), DR-101's drive and vacuum pump (8.72), the sieve's regeneration heater and blower (19.40) | 41.06 | hand, script |

Per kg of product: LP steam 1.188 kWh, MP steam 0.357 kWh, cooling water 1.774 kWh removed (through
the tempered-water loop), electricity 0.325 kWh. Recorded exclusions: the tempered-water loop's
circulation pump (sized on the peak, about 50 m3/h with C-101's condenser at its 400 kW boil-up,
about 5 kW, up to 0.04 kWh/kg if it runs at full speed the year round; ASSUMED, not designed); the
agitators' power ends as heat in the content (about
11 kW year average of R-101's and C-101's 12.9 kW); it lowers the steam of the warm-up and raises
the tempered water of the dosing by up to that much, and is not added to Q1, Q2 or Q4 (0.09 kWh/kg
at most); the heat losses of R-101, C-101 and DR-101 are not counted (no insulation design).
The still's and the dryer's heating media stay below the alkoxide's limits (D-008); R-101 is
warmed on steam before any metal or alkoxide is in it.

## D-010 Wastes (2026-11-06)
- Vent gas to the flare (S23, 6.43 kg/h): hydrogen 1.133 kg/h, tert-butanol 5.29 kg/h (R-101's
  vent and the dryer's bleed), with the nitrogen of D-012.
- Alcohol purge (S22, 3.14 kg/h) to the incineration of non-halogenated solvent waste.
- Sieve regeneration condensate (S7, 13.19 kg/h, 7.0 wt% tert-butanol) to biological wastewater
  treatment.
No aqueous waste from the reaction: the plant is kept dry (D-011).

## D-011 Thermal screening, the rate sensitivity and the hazards (2026-11-06)
Result (`cheme process reactor-hazards`, core ADRs 0050, 0054, 0058, 0062):
- R101: T_p 348.15 K, dT_ad 60.2 K (KTBA; WAT 0.3 K), accumulation of the dosed potassium 3.09 %
  at the end of the dosing, MTSR 350.1 K at that moment, against an MTT of 355.45 K, tert-butanol's
  normal boiling point (core's default, the vented hydrogen left out). The MTSR over the batch
  rises within the first 0.6 h to 350.0 K and stays there while the dosing runs.
- Gas release at the MTSR (with the liquid's vapour, no condenser credited): 0.371 mol/s, 133.4
  m3/h at 350.1 K (38.36 m3/h of hydrogen, the non-condensables, a vapour share of 0.713), against
  the vent capacity of 200 m3/h (`hazard.vent_capacity`, ASSUMED: about twice the normal peak of
  102.5 m3/h before E-104, D-006), 0.67 of it; the end of the dosing is also the largest release
  over the batch (core's `vent_gas_rate` at each point of the cooling profile at that point's
  MTSR). KTBA run to completion from that moment forms 0.114 kmol (11.4 m3 with the vapour).
- No TD24 of the solution, the solvate or the product is known (never estimated): no class
  (`cheme.reactor-hazard-missing`, info). With MTSR below MTT, core's `criticality()` leaves
  classes 1 (TD24 above the MTT), 2 (TD24 between the MTSR and the MTT) or 5 (TD24 below the
  MTSR).

Sensitivity (a scratch copy with both rate constants divided by 10 and by 100; nothing else
changed; not committed):

| case | accumulation | MTSR | post-reaction | hydrogen at the MTSR (non-condensables) | with the vapour | cycle, batches/a at the same batch |
|---|---|---|---|---|---|---|
| k (design) | 3.09 % | 350.1 K | 0.743 h | 38.36 m3/h | 133.4 m3/h, 0.67 of the vent | 6.586 h, 1202 |
| k/10 | 29.6 % | 366.9 K | 9.53 h | 72.2 m3/h | the content boils (vapour share 1.37) | 15.37 h, 515 |
| k/100 | 85.1 % | 399.9 K | 105.1 h | 66.7 m3/h | the content boils (vapour share 4.01) | 110.9 h, 71.4 |

MTT 355.45 K in every case. At k/10 and k/100 the MTSR is above the MTT: the alcohol would boil in
a cooling failure (core: `cheme.reactor-hazard-mtsr` and `cheme.reactor-hazard-vent`, the content
boils); core then gives the non-condensables only and asks for a two-phase relief study (L-10).
Without a TD24, core's `criticality()` leaves classes 3 (TD24 above the MTSR), 4 or 5 there.
**Design finding:** the reaction is dosing-controlled only if the dispersed metal reacts fast. A
slower reaction (a poorer dispersion: a stopped or slow agitator, a lower temperature near the
metal's melting point, a passivated metal) accumulates potassium, and a cooling failure then boils
the alcohol and releases hydrogen with it. Required, not yet designed: the dosing interlocked with
the agitator, the jacket's flow and temperature, the hydrogen flow (a hydrogen flow below the
dosing's stoichiometric rate shows the metal accumulating, and stops the dosing), R-101's pressure
and the differential pressure across E-104 and the vent line (a blocked vent, below); R-101's
emergency relief sized from calorimetry for the boiling alcohol with its hydrogen and for a
blocked vent; the reflux of the boiling alcohol through E-104 as a tempering barrier only once its
capacity is shown, on a coolant that cannot freeze the alcohol (D-006).
Calorimetry (heat of reaction, the dispersion's rate, accumulation, gas release, TD24 of the
solution and the dry product) decides this before basic engineering.
**Hydrogen.** The vent gas is mostly hydrogen (flammable at 4-75 vol%, detonable at 18.3-59 vol%
in air, ignited by 0.02 mJ, SRC-8), so R-101, C-101, DR-101, the vent header and the flare line
are inerted with nitrogen and kept free of air (purged header, D-012), the area classified for
hydrogen, and the flare line has a flame arrester or a seal. **Loss of the flare** (flame out,
blocked header): the dosing stops on the header's pressure or flow; the hydrogen of the metal
already dosed (at most 0.114 kmol after a cooling failure, 133.4 m3/h at the design rate) goes to
a vent stack at a safe height. **A blocked vent: frozen E-104.** On water below tert-butanol's
freezing point (298.3 K) the alcohol condensing at E-104's cold end would freeze on the tubes,
where the wall runs close to the coolant (D-006), and could close R-101's vent while the metal
reacts: R-101 would pressurise. A low hydrogen flow alone does not show it: it would be read as the
metal accumulating, and the dosing could go on into a closed vessel. Measures: every cooling duty
on the tempered-water loop, its supply held at 303 K or above (D-009), a low supply temperature
alarming and tripping the dosing; the dosing tripped on high R-101 pressure and on a high
differential pressure across E-104 and the vent line, as well as on the low hydrogen flow; R-101's
emergency relief sized for a blocked vent as well (the hydrogen of the metal already dosed, at most
0.114 kmol after a trip at the design rate and more at k/10 and k/100, with the alcohol's vapour),
on a relief path that does not pass E-104. C-101's condenser, E-201 and A-001's product condenser
condense nearly pure alcohol on the same loop; a frozen one blocks the still's, the dryer's or the
sieve's vapour path, with less consequence (no metal in them), and their relief is set in basic
engineering. **Water and potassium** (SRC-1, SRC-8): water reacts vigorously with
the metal and the heat ignites the hydrogen; with the alkoxide it gives KOH and tert-butanol. The
paths: the make-up's water (dried to 0.1 wt%, D-004), the tempered water of R-101's jacket, of E-104
(whose condensate runs back into R-101) and of the condensers, rinse water (none: every vessel is
kept dry), and air moisture. V-102 is heated by a closed thermal-oil circuit; R-101's jacket and
E-104 on tempered water are a leak path: the loop is closed, so basic engineering can fill it with a
non-aqueous heat-transfer fluid (its supply still held at 303 K or above for the alcohol), or
choose a double wall with leak detection on which the dosing trips (open input). Potassium residues
(SRC-1, Note 3: they have exploded even under a protective liquid) are destroyed with tert-butanol
at once. **The dry product** is self-heating (H252) and a flammable solid (H228) (SRC-7): DR-101
dries, cools and discharges under nitrogen. Screening values only, not a reaction-hazard
assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-06)
Decision: `cheme assess lca --write` per kg of dried alkoxide from the flowsheet's year averages;
the make-up's tert-butanol linked to tert-butanol-1 (`lca/mappings.yaml`) kg for kg on the alcohol
contained, the basis of its product and of the exchange `feed:TBAF` (S3); the azeotrope's water
`feed:TBAW` (S4) its own exchange, a gap; the drying past the azeotrope this plant's sieve unit,
its steam, electricity and cooling water counted (D-004); the nitrogen consumable linked to asu-1,
the steam counted as heat (kWh); every other background a gap with the activity it should connect
to.
- **Potassium metal** has no library producer, and no sodium producer either: its stoichiometric
  proxy by the thermal route (SRC-8: Na + KCl -> NaCl + K), 1.907 kg KCl and 0.588 kg sodium per
  kg, is recorded in lca.yaml and here and not linked (CONTRIBUTING, "Gaps").
- **Hydrogen**: flared with the alcohol it carries (product:FLARE, a waste treatment), no credit
  and no allocation: the plant has one product (D-001). processes/utility-flare is for
  methane-rich gas only and is not linked.
- Wastes: the purge to incineration, the regeneration condensate to wastewater treatment: gaps
  with their routes.
Per batch, not in the flowsheet (core ADR 0053, library ADR 0035): nitrogen 95.7 kg (76.5 Nm3:
R-101's purge 30, C-101's blanket 10, DR-101's bleed 10 and vacuum breaks 6.3, V-102's pressing 2,
the vent header's purge 13.2 over the cycle, the tanks 5, ASSUMED), 0.115 kg per kg, to the flare.
No rinse: the vessels are kept dry (D-011).
Per kg of product: potassium 0.348 kg, tert-butanol (contained) 0.734 kg, the azeotrope's water
0.098 kg, nitrogen 0.115 kg, electricity 0.325 kWh, LP steam 1.188 kWh, MP steam 0.357 kWh,
cooling water 1.774 kWh removed; vent gas to the flare 0.051 kg, purge 0.025 kg, regeneration
condensate 0.104 kg. Not counted: the flare's own emissions (about 0.10 kg of fossil CO2 from the
0.042 kg of alcohol per kg), the tanks' breathing, the alkoxide's sublimate (emission_exclusions).
The yield on the tert-butanol bought is 89.5 % (1.11926 kmol of alkoxide for 1.25071 kmol of
alcohol): 5.7 % to the flare, 3.4 % purged, 1.0 % to the regeneration, 0.4 % in the product.

## D-013 Dedicated train (2026-11-06)
Decision: V-102, R-101, C-101, DR-101, A-001 and the tanks make only potassium tert-butoxide,
batch after batch: 1202 batches in 7920 h on a dedicated train (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train cannot
be checked without the other products' campaigns. Out of scope, so not LCI gaps: changeover
cleaning between campaigns of other products (the sodium alkoxides are the usual neighbours), the
idle time of a multipurpose train, shared tank farms.

## D-014 The downstream link (2026-11-06)
Decision: `di-tert-butyl-dicarbonate-1` links its `feed:KOTBU` (stream S1, technical potassium
tert-butoxide, 1.150 kg/kg Boc2O, modelled as 100 % KOtBu) to this entry's `product:KOTBU` kg for
kg (its `lca/mappings.yaml`, as its feed:PHOS links phosgene-1). Grade and unit: both are kg of
the dry powder; this product's modelled 0.23 % KOH and 0.30 % tert-butanol are the technical
grade's impurities that entry leaves out (its D-004), so the link counts this entry's burden per
kg of powder, not per kg of KOtBu contained (0.53 % apart).

## Core features used (cheme-as-code 1.10.0)

| feature | where | ADR |
|---|---|---|
| `batch.vent.vapour` and `vent.condenser` with `returns: vessel` and its own `energy_port` | R101: the alcohol the hydrogen carries, E-104 at 308 K, Q3 17.38 kW written by the model | 0062 |
| `still.heat_up`, `still.condenser_port`, `vessel.metal_heat_capacity` | ST101 (the charge to its bubble point, C-101's metal; Q4, Q5 by the model), R-101's warm-up time and heat | 0061, 0063 |
| recipe heat report with the vessel's metal | Q1 (606.2 MJ a batch) | 0063 |
| `reactor: semibatch` with a `target` | R101 (molten potassium dosed) | 0050 |
| `batch.vent` | R101 (hydrogen) | 0054 |
| the screening's default MTT of what boils (the vent's hydrogen left out), the MTSR profile, the gas release at the MTSR against `hazard.vent_capacity` | R101, D-011 | 0058 |
| duties written by the models at `energy_port` | Q2 (R101), Q4 (ST101) | 0059 |
| recycle `tears:` with Wegstein | S19, the alcohol loop | 0060 |
| batch still (Rayleigh, Raoult, non-volatile solutes, residue end) and recipe `distil` `from:` | ST101 | 0055 |
| `dryer:` with energy, drying rate, cake density; recipe `dry` `from:`; `vessel.heated_area` | D101 | 0057 |
| recipe `units:` (one vessel over several steps) | R-101 (E101, R101), DR-101 (D101, E103) | 0057 |
| vessel sizing and jacket check, `heat` times from the jacket | R-101, C-101, DR-101 | 0052 |
| per-batch LCA consumables | nitrogen | 0053 |

Not used: `still.column` (ADR 0061): the alcohol strip needs no rectification, the residue's
solutes are non-volatile; `dosing.heat_of_solution` (ADR 0063): the metal reacts, it does not
dissolve, and the alkoxide's heat of solution is inside KTBA's ASSUMED heat; `vent.henry`: the
hydrogen's solubility is negligible and has no sourced constant here; `batch.heat_up` (ADR 0063):
the warm-up is on steam and the reaction on tempered water, and one model duty on one stream would
net them (L-11); `dosing.absorbed`: nothing is dosed as a gas; `hazard.reactions`: both reactions
count; crystallizers: the solvate's precipitation is not modelled (L-2).

## Core limits hit (for core issues)

- L-1: the semi-batch is one liquid phase. The molten potassium is a second, dispersed liquid that
  reacts at its surface; the model carries it as dissolved and its rate as first order in a
  pseudo-concentration (D-005). The dispersion (agitation, droplet size) that sets the real rate,
  and the metal's density difference, cannot be expressed.
- L-2: the batch still is an ideal liquid with non-volatile solutes. The alkoxide's solvation, the
  1:1 solvate's precipitation as the alcohol leaves and the paste's real vapour pressure (and the
  solvate's binding heat, ASSUMED in the dryer's latent heat) are not modelled; the residue end at
  50 mol% is a choice, not a phase boundary. The alkoxide's solubility in the alcohol, which
  decides the charge ratio (D-004), has no model either.
- L-3: a still asks a vapour pressure of every component its inlet's composition lists, even at
  0: R101 writes its vented hydrogen into the liquid outlet as 0, so H2 is listed under the
  still's `nonvolatile` to pass (ST101's comment).
- L-4: no adsorption model: the molecular-sieve dehydration A001 is a specified split with its
  duties from a balance script (scripts/makeup_drying.py, library ADR 0027).
- L-5: the dryer heats its vessel's metal from the wet cake's inlet temperature. When the same
  recipe vessel cools the product before discharge (E103), the metal starts the next batch from
  that cooled temperature: the dryer's `vessel_heat_capacity` is scaled by hand (D-008). The
  dryer could take the vessel's start temperature, or the recipe vessel's
  `metal_heat_capacity`, as ADR 0063 does for batches and stills.
- L-6: the cooling in a dryer's vessel (E103, a pass-through) has no model and no time from a
  jacket: the duty is hand arithmetic and the 1.5 h ASSUMED.
- L-7 (as n-bromosuccinimide-1 L-6): core propagates from the feeds and does not solve them for a
  product rate, and the batch size and the cycle depend on each other through the warm-up time;
  both were iterated by hand.
- L-8: a recycle with a fixed purge fraction converges, but the make-up that holds a charge ratio
  must be found by hand: there is no design specification (a feed adjusted to a target, such as
  the charge's alcohol per mol of metal). With a gain of 0.995 the recycle is 199 times as
  sensitive to the make-up's surplus.
- L-9: no condenser is checked against the condensate's freezing point, neither at its outlet
  temperature nor at its coolant's supply temperature, the lower bound of its tube wall: tert-butanol
  freezes at 298.3 K, so the vent condenser's 308 K and the tempered water's 303 K supply were
  chosen by hand (D-006, D-009). Core could compare a utility's supply temperature with the
  freezing point of what condenses on it (a vent condenser, a still's condenser).
- L-10: when the content boils at the MTSR, core gives the non-condensables only and flags it; it
  has no tempered (boiling) reaction model or relief load for a two-phase relief study (D-011).
- L-11: an isothermal batch has one model duty on one energy stream: with `batch.heat_up` the
  steam of the warm-up and the tempered water of the reaction would be netted on one stream, so the
  warm-up stays a pass-through E101 with its heat from the recipe (Q1).
- L-12: the agitators' power is not part of any model's energy balance (D-009).

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R101: composition, vent with vapour and condenser, accumulation, MTSR, peak cooling, gas release at the MTSR | done in cheme, kinetics ASSUMED | D-005, D-006, D-011 |
| duties Q2, Q3, Q4, Q5 | done in cheme (the models' duties) | D-009 |
| alcohol strip ST101 | done in cheme, ideal liquid ASSUMED | D-007 |
| drying: outlets, duty Q6, drying time | done in cheme, moisture and rate ASSUMED | D-008 |
| alcohol recycle | done in cheme (tear S19) | D-007 |
| make-up dehydration A001 | balance script, ASSUMED | D-004, L-4 |
| batch recipe, cycle time, basis check, vessels, jacket, vent load | done in cheme | D-003 |
| feeds for 1000 t/a, the other duties (Q1, Q7, Q8, Q9, Q13, Q14) | hand (ratios scaled; arithmetic in the sources) | D-004, D-009, L-7, L-8 |
| per-batch nitrogen | done in cheme, amount ASSUMED | D-012 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Open inputs
Kinetics, the heat of reaction and the gas release (calorimetry of the dispersed metal in the
alcohol), TD24 of the solution, the solvate and the dry product; R-101's emergency relief (D-011);
the alkoxide's solubility in tert-butanol against temperature and the solvate's behaviour in the
still and the dryer (its binding heat, the temperature it gives up its alcohol); the drying rate
and residual alcohol from trials; the sieve unit's design (vendor data: residual water,
regeneration energy, alcohol loss); a colder second vent stage or a vent scrubber for the alcohol
(D-006); the tempered-water loop's supply limit against the condensers' wall temperatures (E-104's
gas-side coefficient, a thermal design), its control and its pump (D-009, D-011); R-101's relief
for a blocked vent (D-011); a non-aqueous coolant or leak detection on R-101's jacket and E-104
(D-011); the product
specification (assay, KOH, sodium, residual alcohol); the purge's real need (D-007); a TEA
(`operation.batch: {recipe: true}`).
