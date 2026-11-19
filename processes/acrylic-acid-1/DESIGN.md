# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Acrylic acid by two-stage catalytic oxidation of propylene, issue
ChemE-as-Code/process-library#475, a continuous Tier 2 entry of the library. Concept stage:
design basis, balanced BFD/PFD with core's conversion reactors, component separators and a
converged recycle, equipment list and a preliminary gate-to-gate LCI. Out of scope here: P&IDs,
layout, HAZOP, TEA, datasheets, kinetics and rigorous VLE.

Starting point (2026-11-19): library `main` (c241d8d7) with the core pin 0e85885 (v1.12.0).
Templates: `oxalyl-chloride-1` (structure, depth, LCA layout), `cumene-1` and `methanol-1` (the
exergy allocation of exported steam), `phosgene-1` (an adiabatic oxidiser), `benzyl-bromide-1` (a
toluene recycle at a tear). Requires cheme-as-code 1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (Google Patents machine text, the Arkema data sheet as extracted text, Wikipedia and
PubChem pages, the packages' values).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 4 873 368 A, K. Kadowaki, K. Sarumaru, T. Shibano (Mitsubishi Petrochemical), priority JP 1979-11-19, granted 1989-10-10: Process for producing acrylic acid, https://patents.google.com/patent/US4873368A/en | two-stage vapour-phase oxidation of propylene with air and steam: first stage over a Mo-Bi multicomponent oxide in shell-and-tube reactors (tubes 15 to 40 mm, 2 to 8 m) at 280 to 350 C, 0.4 to 1.5 kg/cm2 gauge, propylene 7 to 15 %, O2/propylene 1.17 to 1.66, steam/propylene at most 4; a cooling zone after the catalyst bed brings the gas to at most 280 C (preferably 260 C) to stop acrolein oxidising by itself; air and steam added before the second stage (Mo-V oxide, 220 to 320 C, totals O2/propylene 1.75 to 2.5, steam/propylene 1 to 5); the outlet cooled to 100 to 180 C and contacted with cold inhibited water to an aqueous acid, then extraction or azeotropic distillation. Example 2 (Table 1): 12 % propylene, 10 % steam, 78 % air, 310 C: conversion 98.5 %, acrolein 80.2 %, acrylic acid 11.7 %. Example 5 (Table 2): after that first stage, totals 7.5 % propylene, 15 % steam, 77.5 % air, 265 C: conversion 98.6 %, acrolein 0.4 %, acrylic acid 87.8 %. Table 3: acrolein gas burns by itself in an empty tube at 300 to 320 C (1.1 to 4.6 % lost), not below 280 C | read (Google Patents); patent, facts only | D-001, D-004, D-005, D-006, D-007 |
| SRC-2 | US 4 365 087 A, same inventors (Mitsubishi Petrochemical), priority JP 1979-01-30, granted 1982-12-21: Production of acrylic acid, https://patents.google.com/patent/US4365087A/en | the same two stages; 20 to 70 % of the second stage's off-gas recycled as diluent between the stages; the outlet gas cooled to about 50 to 5 C and the acids condensed with an inhibitor; acrolein stripped from the aqueous acid and recycled; Example 8: propylene conversion 97.9 to 98.4 %, acrolein conversion 99.0 to 99.2 %, acrylic acid yield 83.5 to 85.5 % over 60 days with off-gas recycle | read (Google Patents); patent, facts only | D-001 (recycle rejected), D-007 |
| SRC-3 | US 5 910 607 A, Y. Sakakura, M. Yamagishi, H. Hosaka (Mitsubishi Chemical), priority JP 1994-08-04, granted 1999-06-08: Process for producing acrylic acid, https://patents.google.com/patent/US5910607A/en | the reactor gas scrubbed with water to a crude of 40 to 80 wt% acrylic acid, 1 to 5 wt% acetic acid; azeotropic dehydration with an entrainer boiling at 80 to 130 C (toluene, heptane, MIBK, isopropyl acetate...), 100 to 300 mmHg top, 5 to 20 theoretical plates, bottoms at most 100 C with at most 0.5 wt% water and 5 to 30 wt% entrainer against polymer; the aqueous phase back to the scrubber; acetic acid column at 50 to 200 mmHg; hydroquinone and phenothiazine fed at the top (800 and 500 ppm in the bottoms) and air at the bottom; product with at most 0.1 wt% each of acetic acid and water (claim 18). claim 13: entrainer refluxed at 1 to 10 times the weight of the water fed. Example 1: 55 wt% acrylic acid, 1.5 wt% acetic acid feed at 280 g/h, toluene, 180 mmHg, operated continuously for 7 h, top 49 C, bottoms 90 C (170.5 g/h); 'the amount of the entrainer phase returned to the top of the column as reflux was 830 ml', with no time basis (every other rate of the example is per hour); bottoms 2.3 % acetic acid, 0.5 % water, 7 % toluene; aqueous phase 0.2 % acetic acid, 0.1 % acrylic acid | read (Google Patents); patent, facts only | D-001, D-005, D-007, D-008 |
| SRC-4 | Arkema, Acrylic acid (AA) data sheet, BU/V8/05.23, https://www.arkema.com/files/live/sites/shared_arkema/files/downloads/products-documentations/acrylicmonomers/data-sheet-aa-v8.pdf | specification: purity at least 99.5 %, water at most 1000 ppm, dimer at most 2000 ppm, MEHQ 180 to 220 ppm; standard inhibition 200 ppm MEHQ; storage at 15 to 25 C under air (at least 5 vol% oxygen activates the inhibitor); dimer forms at about 100 ppm a day at room temperature; local overheating above 25 C risks exothermic polymerisation; crystallised acid is thawed by tempered water of at most 35 C circulated through coils, the acid kept mixed; boiling point 141 C, freezing point 13 C, liquid heat capacity 2.05 kJ/(kg K), latent heat 634 kJ/kg, heat of polymerisation 1077 kJ/kg, flash point 48.5 C | read (manufacturer literature; text extracted from the PDF) | D-002, D-009, D-010, D-013 |
| SRC-5 | Wikipedia, Acrylic acid, https://en.wikipedia.org/wiki/Acrylic_acid | made by two-step oxidation of propylene through acrolein; more than a million tonnes a year (citing Ullmann's); flammable, corrosive; explosive limits 2.4 to 8.02 % | read; CC BY-SA, facts only | D-001, D-013 |
| SRC-6 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (Caleb Bell, MIT licence; the versions core pins), through `cheme chemistry thermo` and `thermo.Chemical` in the scripts: ideal-gas formation enthalpies, entropies and heat capacities as `cheme chemistry thermo` prints them (ATCT_G, API_TDB_G, WEBBOOK, CRC, YAWS; heat capacities fitted to TRCIG and HEOS); liquid formation enthalpies (chemicals `Hfl`: acrylic acid -383.80 kJ/mol from CRC, acetic acid -483.58, water -285.83 and toluene 12.36 kJ/mol from ATCT_L), against which the liquids are referenced; boiling points (HEOS, CRC tables). thermo's default methods, per component: water and toluene liquid heat capacity, heat of vaporisation and density by HEOS_FIT (fits to CoolProp's reference equations of state; toluene 862.2 kg/m3 at 298.15 K), water's vapour pressure IAPWS; acrylic acid's vapour pressure DIPPR_PERRY_8E (15 kPa at 361.4 K; 8 and 10 kPa at 347.0 and 352.0 K) and liquid heat capacity ZABRANSKY_SPLINE_C (141.7 kJ/(kmol K) at 330 K); acetic acid's vapour pressure WAGNER_MCGARRY (McGarry 1983), heat of vaporisation DIPPR_PERRY_8E (23.4 kJ/mol at 298 K) and liquid heat capacity VDI_TABULAR (136.5 kJ/(kmol K) at 330 K); the relative volatility of acetic to acrylic acid from these vapour pressures (2.50 at 361.4 K); IAPWS-95 for steam; propylene's flammability limits in air, LFL 2.0 % and UFL 11.1 % at ambient conditions (`chemicals.safety`, from IEC 60079-20-1 (2010) and NFPA 497 (2008)) | values in materials.yaml, the scripts and their printout | open-source packages queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). The underlying works were not read here: DIPPR_PERRY_8E is Perry's Chemical Engineers' Handbook, 8th ed., drawing on DIPPR 801; VDI_TABULAR the VDI Heat Atlas; ZABRANSKY_SPLINE_C Zabransky et al.'s evaluated liquid heat capacities; WAGNER_MCGARRY McGarry 1983 (Ind. Eng. Chem. Process Des. Dev.); CRC the CRC Handbook of Chemistry and Physics; ATCT the Active Thermochemical Tables; the IEC and NFPA standards | materials, reactions, D-005, D-007 to D-010, D-012, D-013 |
| SRC-7 | PubChem CIDs 6581 (acrylic acid), 7847 (acrolein), 785 (hydroquinone), 9015 (4-methoxyphenol), PUG REST | formula, InChIKey, CAS and ChEBI cross-references | read | registry |
| SRC-8 | processes/propylene-pdh-1, btx-1, utility-steam-ng-boiler, cumene-1, methanol-1 (this library) | propylene; toluene; process steam; the exergy method for exported steam and Szargut's element exergies as methanol-1's script cites them | library, internal | D-003, D-012 |

Searched and not found openly (2026-11-19): kinetics of either stage usable without a licensed
paper, a plant's by-product distribution (CO, formaldehyde, acetaldehyde, propionic acid), a
plant's specific steam and power consumptions, VLE data of acrylic acid with water, acetic acid
and toluene, the EBAM handling brochure (named by SRC-4, not retrieved), and an EU BREF chapter
on acrylic acid (the LVOC BREF 2017 has none).

## D-001 Route and boundary (2026-11-19)
Decision: the two-stage gas-phase oxidation of propylene with air and steam of SRC-1 (Mo-Bi oxide
to acrolein, Mo-V oxide to acrylic acid, multitubular salt-cooled reactors), a water quench
absorber, azeotropic dehydration with toluene, an acetic acid column and a glacial acid column
after SRC-3, and a catalytic oxidiser for the absorber's off-gas. Boundary: gate to gate, from
propylene, air, process steam, process water, toluene, hydroquinone and MEHQ to the glacial acid,
the exported HP steam, the wastewater, two liquid wastes to incineration and the flue gas.
Reason: SRC-5 names the two-step oxidation of propylene the production route; SRC-1 gives the
feed ratios, temperatures, conversions and yields of both stages from one consistent set of
examples, and SRC-3 a dehydration with stated compositions. Every step is a model core 1.12 has:
conversion reactors with selectivities, component separators and a recycle at a tear.
Rejected:
- solvent absorption of the reactor gas in a high-boiling solvent (the BASF type, named in the
  patents read, no example with quantities read): no open source with its compositions;
- extraction of the aqueous acid with a solvent (SRC-1, SRC-3 name it): azeotropic dehydration has
  the stated compositions of SRC-3, Example 1;
- recycling 20 to 70 % of the off-gas as diluent (SRC-2): it lowers the steam use but adds a gas
  loop; SRC-1's Example 5 reaches 87.8 % with steam alone; an option for a later stage;
- one-step oxidation of propylene to acrylic acid, propane oxidation, the acrylonitrile
  hydrolysis (SRC-5: abandoned, ammonium by-products) and bio-based routes (glycerol, lactic
  acid, 3-hydroxypropionic acid): not the route that makes the volume (SRC-5) or no open plant
  data read;
- pure oxygen instead of air: no source with its ratios read; air is what SRC-1 runs.
Assumptions: by-products lumped (D-005); off-gas burnt on site (D-011).

## D-002 Capacity, product and operating hours (2026-11-19)
Decision: 12 500 kg/h of glacial acrylic acid (S27), 100 kt/a in 8000 h, ASSUMED (a world-scale
order of magnitude; no open capacity figure used). Specification of SRC-4: at least 99.5 wt%,
water at most 1000 ppm, MEHQ 180 to 220 ppm; acetic acid at most 0.1 wt% (SRC-3, claim 18).
Model: 99.92 wt% acrylic acid, 0.057 wt% acetic acid, 200 ppm MEHQ, no water or toluene (D-008,
D-009).

## D-003 Propylene feed (2026-11-19)
Decision: chemical-grade propylene, 99.5 mol% with 0.5 mol% propane (ASSUMED), vapour at 313.15 K
and 1000 kPa(a) at the battery limit, from `propylene-pdh-1` (the LCI links it, D-012). The
propane passes the reactors and is burnt in the oxidiser.

## D-004 Air and steam ratios (2026-11-19)
Decision: per mol of propylene, 6.5 mol of air and 0.833 mol of steam to the first stage (12 %
propylene, 10 % steam, 78 % air, SRC-1 Example 2) and 3.833 mol of air and 1.167 mol of steam
before the second (to the totals 7.5 % propylene, 15 % steam, 77.5 % air of Example 5): O2 per
propylene 1.36 in the first stage and 2.16 in both. One compressor K-101 for all the air, split
63/37 (SP101). Air is dry, 20.95 mol% O2, the argon and CO2 lumped into N2. Steam is the site's
1100 kPa(a) saturated steam (registry grade steam/mp-11bara), 7.3 t/h.

## D-005 Reactors: conversions, selectivities and heats (2026-11-19)
Decision: two conversion steps (no kinetics found openly):
- R101 (selectivity spec): propylene conversion 98.5 %, per mol converted 0.8142 acrolein, 0.1188
  acrylic acid (SRC-1, Example 2) and the rest (6.6 % of the propylene) burnt to CO2 and water
  (R3), ASSUMED lumping of the by-products;
- R201 (three parallel conversions of the acrolein): 99.50 % converted, 94.89 % of the inlet
  acrolein to acrylic acid (R4), 3.58 % to acetic acid and CO2 (R5), 1.03 % burnt (R6), so that
  both stages give 87.8 % acrylic acid and 0.4 % acrolein on the propylene fed (SRC-1, Example
  5); the acetic acid at the ratio of SRC-3's crude (1.5 wt% beside 55 wt%, 0.0327 mol per mol of
  acrylic acid), ASSUMED to form in the second stage from acrolein. The propylene passes R201
  unconverted (Example 5's 98.6 % against Example 2's 98.5 %: 0.1 % neglected).
Heats of reaction from the ideal-gas formation enthalpies of materials.yaml (SRC-6). Core writes
the duties of both steps (`cheme process propagate`, its conversion-step duty, ADR 0059): R101
23.74 MW from 381 K in to 533 K out, R201 11.46 MW from 495 K to 538 K; scripts/aa_balance.py
gives the same (23 744.7 and 11 455.2 kW) as a cross-check.
Reason: the yields are what the open examples report; a lumped by-product set keeps the carbon
and oxygen balances.
Assumptions: CO, formaldehyde, acetaldehyde, propionic acid, maleic acid and the like are not
modelled (their carbon is in CO2 and acetic acid); the catalysts' ageing is not modelled.

## D-006 Reactor conditions, pressures and the steam raised (2026-11-19)
Decision: first stage at 310 C (salt) with the outlet after the cooling zone at 533.15 K (SRC-1:
at most 280 C, preferably 260 C); second stage at 538.15 K (265 C, Example 5); 220 kPa(a) at the
first stage's inlet to 170 kPa(a) at the second's outlet (SRC-1: 1.0 kg/cm2 gauge in the
examples, ASSUMED profile). The salt of both reactors raises saturated HP steam at 2500 kPa(a)
(497.1 K, ASSUMED level: 86 K below the first stage's salt, 41 K below the second's and 36 K below the first stage's gas outlet after the cooling zone) for export: 35.2 MW, 2.82 kWh per kg of
product. K-101 compresses the air from 101.3 to 230 kPa(a) at an isentropic efficiency of 0.80
and a motor efficiency of 0.95 (ASSUMED): 1751 kW, outlet 395.9 K. Mixers are adiabatic (script).

## D-007 Gas cooler and quench absorber (2026-11-19)
Decision: E-301 cools the gas to 443.15 K (SRC-1: 100 to 180 C), then T-301 absorbs the acids in
inhibited water: inerts, propylene, propane and acrolein to the off-gas, 99.8 % of the acrylic
acid and 97 % of the acetic acid to the bottoms (ASSUMED), the off-gas saturated with water at
313.15 K and 130 kPa(a) (SRC-2 cools to 5 to 50 C), the bottoms 55 wt% acrylic acid at 333.15 K
(SRC-3, Example 1's feed). The process water for 55 wt% is only 644 kg/h: the reaction water and
the process steam give nearly all of it, as SRC-1 says a low steam ratio gives a concentrated
acid. The absorber's heat (12.0 MW) goes to cooling water in a pump-around (script).
Rejected: stripping and recycling the acrolein (SRC-2): it is 0.4 % of the propylene and goes to
the oxidiser; returning the dehydration column's aqueous phase to the absorber (SRC-3): see D-008.

## D-008 Dehydration, acetic acid and the toluene loop (2026-11-19)
Decision: C-401 removes the water by azeotropic distillation with toluene at 24.0 kPa(a) (180
mmHg), top 322.15 K, bottoms 363.15 K (SRC-3, Example 1); its aqueous phase goes to wastewater,
its bottoms (90.2 wt% acrylic acid, 2.5 % acetic acid, 7.0 % toluene, 0.2 % water) to C-402 at
13.3 kPa(a), which returns the toluene and water to C-401 (S21, the tear, converged by propagate),
draws the acetic acid off as a side stream to incineration (74 wt% acetic acid, 24 % acrylic
acid) and sends the acid to C-404. Splits (ASSUMED, chosen to give SRC-3's compositions): C-401
aqueous phase 99.7 % of the water, 5 % of the acetic acid, 0.07 % of the acrylic acid, 0.5 % of
the toluene (0.18 wt% acetic and 0.09 wt% acrylic acid in it, the source's 0.2 and 0.1); C-402
top 99.5 % of the toluene, all water, 10 % of the acetic acid; side 0.5 % toluene, 88 % acetic
acid, 0.8 % acrylic acid. The toluene make-up (9.97 kg/h) holds 7 wt% toluene in C-401's
bottoms; hydroquinone (11.4 kg/h) gives 800 ppm there (SRC-3). C-401's reboiler: the source's
toluene reflux, 2.56 kg per kg of feed (830 ml at thermo's 0.862 kg/l on 280 g/h), and the
aqueous distillate condensed at 322 K (13.4 MW). SRC-3's Example 1 gives the 830 ml without a
time basis; it is read per hour (ASSUMED): the example states its other rates per hour, and per
hour the reflux is about 5.9 kg of toluene per kg of water fed, inside claim 13's 1 to 10, while
830 ml spread over the 7 h run would be about 0.84 kg/kg, below it.
C-402's boil-up is set by its hardest split (it was a reflux ratio of 3 on the overhead before
review): about 98 % of the acetic acid fed has to be stripped out of the acrylic acid below the
feed (2.5 wt% in S18, 0.056 wt% in S23). With the acetic acid dilute, the stripping factor
alpha V'/L' (L' = V' + B) has to exceed 1, so V' > B/(alpha - 1) = 117 kmol/h at alpha 2.50
(acetic to acrylic acid, thermo vapour pressures at the bottoms' 361.4 K, Raoult; an associating
acetic acid vapour would lower it, SRC-6). The boil-up is 1.25 times that minimum (ASSUMED),
147 kmol/h of acrylic acid at 634 kJ/kg: 1.86 MW, about 15 stripping stages by the Kremser
equation, an implied reflux ratio of about 13 on the overhead; condenser 1.91 MW.
Rejected: returning the aqueous phase to T-301 (SRC-3) and recovering the acetic acid: the water
of the reaction has to leave somewhere; with this concept's splits all of it leaves as
wastewater, the acetic acid by incineration. Both are options for the next stage.
Assumptions: no VLE model (L-2); phenothiazine and the inhibitor air of SRC-3 not modelled.

## D-009 Glacial acid column and stabiliser (2026-11-19)
Decision: C-404 distils the glacial acid at 8 kPa(a) (ASSUMED; top 347.0 K, bottoms 352.0 K at
10 kPa(a), thermo vapour pressure), reflux ratio 1 (ASSUMED), 98.5 % of the acrylic acid overhead
and 1.5 % with the hydroquinone to the heavy ends (standing for the dimer and the bleed,
ASSUMED). The distillate is subcooled to 303.15 K and dosed with 200 ppm MEHQ (SRC-4).
Duties with acrylic acid's latent heat of 634 kJ/kg (SRC-4; preferred to thermo's
DIPPR_PERRY_8E value, 389 to 392 kJ/kg at 322 to 361 K, which is far below it; the cause was
not investigated): reboiler 4.3 MW, condenser and subcooler 4.7 MW (the distillate subcooled from 347
to 303 K).

## D-010 Utilities and the balance script (2026-11-19)
Decision: `scripts/aa_balance.py` runs the plant on the same ratios and splits as the flowsheet,
scales it to the product and gives: the feeds, the mixers' and the oxidiser's temperatures, the
compressor's power and the duties of E-301, T-301 and the three columns (ideal gas from the
materials' data; a liquid at 298.15 K below its gas by chemicals' Hfg - Hfl, the same formation
basis as the ideal-gas data, then thermo's liquid heat capacities; the condensers' latent heats
from thermo, acrylic acid's from SRC-4; no heats of mixing or solution). The reboilers take LP
steam at 450 kPa(a) (421.1 K, at least 58 K above the bottoms): 19.6 MW, 1.57 kWh per kg.
Condensers and coolers reject 34.4 MW to cooling water at 298/308 K. (Review of PR #527: the
script first divided thermo's liquid heat capacity, already in kJ/(kmol K), by 1000 and so
dropped the liquids' sensible heat, and referenced the acids' liquids by latent heats that do
not match the monomer gas data; both corrected, T-301 12.2 to 12.0 MW, C-404's condenser 4.4 to
4.7 MW.) Power: K-101 only in the flowsheet; pumps and vacuum systems about 500 kW, ASSUMED, in
the LCA cut-off. The flowsheet cites these values; the library's balance checker re-runs the
script (ADR 0027). Heat recovery from E-301 into boiler feed water is an open option.

## D-011 Off-gas oxidiser (2026-11-19)
Decision: the absorber's off-gas (53.6 t/h, mostly nitrogen with 5.3 wt% oxygen) goes to a
recuperative catalytic oxidiser X-401 that burns 99 % of its propylene, propane, acrolein and
acids (ASSUMED), net adiabatic (`process/simulation.yaml`), outlet 482.7 K in the model; the flue
gas to the stack carries 0.235 kg of CO2 per kg of product (unallocated) and 1 % of the organics.
Start-up and support fuel, the oxidiser's own CO and NOx are not estimated (lca.yaml exclusion).

## D-012 Preliminary gate-to-gate LCI (2026-11-19)
Decision: `cheme assess lca --write` from the design case per kg of S27. Linked: the propylene to
propylene-pdh-1, the toluene to btx-1 (lca/mappings.yaml), the process steam by mass to
utility-steam-ng-boiler's 11 bar(a) steam, the reboiler steam as heat from steam. The exported HP
steam is not offered to other entries as an Atlas steam producer (no inventory_key in
process.yaml, as cumene-1).
Gaps (a gap, never 0): hydroquinone, MEHQ, process water, electricity, cooling water, the
wastewater and the two liquid wastes to incineration (no library producer or treatment chosen).
Process air is free (a resource without burden, as in every library entry with an air feed).
The flue gas is an emission with its CO2 (fossil) and organic slips. Allocation: the exported HP
steam is a co-product, allocated by exergy (library rule for exported steam, as cumene-1 and
methanol-1): 19 647 kJ/kg for the acid and 1373.4 kJ per kWh of steam (scripts/
allocation_exergy.py), so the acid carries 83.6 % of the burdens.
Rejected: a credit for the steam (not in the cut-off model); energy allocation (it would weigh
the steam's heat like the acid's heating value).

## D-013 Hazards to carry into the next stage (2026-11-19)
Decision: recorded, not designed at concept:
- The first-stage feed (12 % propylene, 16.4 % O2, 10 % steam; O2/propylene 1.36) is above
  propylene's upper flammable limit in air at ambient conditions (LFL 2.0 %, UFL 11.1 %, SRC-6),
  and the oxygen-lean, steam-diluted mixture narrows the range further; but the limits widen at
  the mixer's 381 K and 220 kPa(a) and at the reactor's 583 K, so the feed may lie at or inside
  the range there, and the injection point passes through it whatever the bulk composition
  (screening judgement, ASSUMED; no limits at temperature and pressure were read). The
  flammability limits at operating conditions, the oxygen margin, the mixing point, ratio and
  oxygen trips, flame arrestors and the reactors' relief are for the next stage's HAZOP.
- Acrolein (up to 18 wt% between the stages) is very toxic and burns by itself above 280 C
  (SRC-1, Table 3): the cooling zone and the short hot line between the stages.
- Acrylic acid polymerises with 1077 kJ/kg (SRC-4): with its liquid heat capacity of 2.05
  kJ/(kg K) the adiabatic rise of a full polymerisation would exceed 500 K. The columns run under
  vacuum below 100 C with hydroquinone and air, the product is stabilised with MEHQ under air and
  kept at 15 to 25 C, thawed only with tempered water of at most 35 C (SRC-4; steam is
  therefore excluded, our inference). Dimer forms in storage.
- Salt-cooled reactors: a salt-to-water leak in the steam generators; the reactors' runaway on a
  loss of salt flow.
- Toluene, propylene and acrylic acid (flash point 48.5 C) are flammable; area classification at
  basic engineering.

## Method and dependency table

| result | method | inputs |
|---|---|---|
| reactor outlets R101, R201 | core conversion steps (selectivity spec; parallel conversions) | D-005, SRC-1, SRC-3 |
| reactor duties Q2, Q3 | core conversion-step duty (ADR 0059) | materials' ideal-gas data, stream temperatures |
| separator outlets T301, C401, C402, C404 | core component separators (`recovery:`, ADR 0070) | D-007 to D-009 |
| toluene loop S21 | core tear, Wegstein (ADR 0060) | D-008 |
| feeds, mixer and oxidiser temperatures, separator and compressor duties | scripts/aa_balance.py | D-004 to D-011 |
| allocation exergies | scripts/allocation_exergy.py | D-012 |

## Core features used (core 1.12.0)
Conversion reactors with a selectivity spec and with parallel conversions; component separators
with recovery fractions; a tear with Wegstein convergence; the conversion-step duty written on
the reactors' energy streams; the adiabatic declaration of a reactor (simulation.yaml); the
generated BFD and PFD; the LCA with exergy allocation and the library's mappings.

## Core limits hit (each a candidate core issue)

- L-1: no fixed-bed reactor sizing from yields alone: the `pfr` model needs rate laws, none of
  which is open for these catalysts; the tube count, catalyst volume and salt flow are not sized.
- L-2: no property package of core covers the aqueous acids, toluene and the inhibitors (`cheme
  process props --coverage`): no flash, VLE or column model checks the splits of T-301, C-401,
  C-402 and C-404; their duties come from the script on pure-component data, and the
  heteroazeotrope of C-401 is not modelled.
- L-3: a component separator (`recovery:`) writes no duty: the absorber's and the columns'
  energy balances are the script's.
- L-4: core 1.12.0's validator (`_reactor_rules` in `domains/process/model.py`) reuses the name
  `declared` for the list of reactions with a conversion inside the selectivity check, so every
  step after the first selectivity step resolves none of its reactions: a second selectivity step
  is refused with "the key ACR is a reactant of none of its reactions", and later conversion
  steps (X401 here) skip the checks that use their reactions. R201 is therefore written with
  parallel conversions per reaction (the same extents), and X401's reactor checks did not run.
- L-5: propagate writes mole fractions to six significant digits; S5's sum to 1.000001251, over
  pyDEXPI's 1e-6 tolerance, so the generated PFD gives a composition warning, accepted in
  checks.yaml with this reason.
- L-6: propagate solves from the feeds and cannot size them for a product rate; the script scales
  the feeds (as oxalyl-chloride-1's L-6).

## Open inputs
Kinetics or licensor yields of both stages with the by-product distribution; the catalysts'
volumes and lives; VLE of acrylic acid, acetic acid, water and toluene (it sets the columns'
stages, reflux and splits); the aqueous phase's recycle and the acetic acid's recovery; the
inhibitor and air consumptions of the columns (phenothiazine, SRC-3); the oxidiser's fuel and
emissions; pump and vacuum power; prices for a TEA; the HAZOP of D-013.
