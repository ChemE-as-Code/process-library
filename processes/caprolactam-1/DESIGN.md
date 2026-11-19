# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Caprolactam by the conventional route, issue ChemE-as-Code/process-library#464, coverage rank 51
(`caprolactam`). Concept stage: design basis, balanced BFD/PFD with three recycles, the
reactors' duties from formation enthalpies, a preliminary gate-to-gate LCI. Out of scope here:
P&IDs, layout (the concept gate `layout-plot-plan` fails, as for cumene-1), HAZOP, TEA,
datasheets.

Starting point (2026-11-19): library `main` at c241d8d7 with the core pin 0e85885 (v1.12.0 plus
#254). Templates: `oxalyl-chloride-1` (source register, limits, LCI with economic shares),
`hydroxylamine-1` (the salts as molecular components) and `phosphorus-oxychloride-1` (a
continuous conversion step with its duty from core). The feed hydroxylammonium sulfate solution
is hydroxylamine-1's product; this entry is sized on its whole output (D-002).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (Google Patents machine text, the BREF PDF, NIST and PubChem pages, Wikipedia; the
values of the open-source packages queried).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 4,804,754 A, E. De Decker, J. Oostvogels, G. Van Wauwe, G. Neubauer (BASF), priority DE 3642314, 1986-12-11: Preparation of caprolactam from cyclohexanone oxime by Beckmann rearrangement, https://patents.google.com/patent/US4804754A/en | description: oxime fed as a melt at about 80 to 95 C with 0 to 7 (advantageously 3.5 to 6) wt% water; oleum of 24 to 35 wt% SO3 at 1.1 to 1.8 kg per kg oxime; circulating rearrangement at 70 to 130 C (claims 108 to 118 C), H2SO4 to lactam 1.0 to 2.0 by weight and 1 to 14 wt% free SO3 in the circulating mixture, 40 to 150 system volumes per hour, 30 to 120 min; a delay zone at 70 to 110 C before neutralisation; the mixture fed into a 35 to 45 wt% ammonium sulfate solution and neutralised with gaseous ammonia to pH 4 to 5; the crude lactam (about 30 % water) separates from the almost saturated solution, is extracted with benzene and distilled under reduced pressure. Example and Comparative Example: oxime with 4.2 wt% water at 85 C, oleum with 32 wt% SO3 at 1.17 kg/kg, 115 C, about 60 min, neutralised to pH 4.6 with 40 to 43 % ammonium sulfate; no yield stated | read (Google Patents); patent, facts only | D-001, D-006, D-007, D-008 |
| SRC-2 | US 4,031,139 A, G. Rapp, H. Fuchs, E. Thomas (BASF), priority DE 2508247, 1975-02-26: Manufacture of cyclohexanone oxime, https://patents.google.com/patent/US4031139A/en | cyclohexanone reacted counter-currently with a hydroxylammonium/ammonium sulfate solution above the oxime's melting point, at pH 0.5 or less (no neutralising salts), at 90 C in a pulsed column; over 90 % of the cyclohexanone converted; the aqueous phase extracted with fresh cyclohexanone, which returns the residual hydroxylamine and oxime. Example: oxime product with 0.6 % cyclohexanone and 4.6 % water | read (Google Patents); patent, facts only | D-004 |
| SRC-3 | US 4,931,592 A, H. Fuchs, D. Agab, G. Neubauer, J. Ritz (BASF), priority DE 3839448, 1988-11-23: Storability of molten cyclohexanone oxime, https://patents.google.com/patent/US4931592A/en | the prior art (US 3,941,838) neutralises the oximation with ammonia; the oxime is washed with 10 to 42 wt% ammonium sulfate solution at pH 4.5 to 5.8, held with ammonia, at 75 to 90 C | read (Google Patents); patent, facts only | D-004 |
| SRC-4 | US 7,339,056 B2, J. A. W. Lemmens, F. Mostert, T. M. Smeets (DSM), priority 2003-05-23: Continuous process for preparing caprolactam, https://patents.google.com/patent/US7339056B2/en | three rearrangement stages in series, molar ratio (SO3 + H2SO4) / lactam 1.2 to 2.2, 1.0 to 1.6 and 1.0 to 1.4; Comparative Experiment A: 7.1 t/h oxime with 4.7 wt% water and 9.2 t/h oleum of 25 wt% SO3 into the first stage at 102 C, 1.9 and 1.1 t/h oxime into the second and third at 86 C (about 0.91 kg oleum per kg oxime in all), ratios 1.68 / 1.32 / 1.18, yield 98.9 %; Examples 2 to 4 with oxime below 0.1 wt% water: 99.3 to 99.5 %; more oleum gives more ammonium sulfate on neutralisation; the by-products are not named | read (Google Patents); patent, facts only | D-006 |
| SRC-5 | US 6,448,395 B1, A. J. F. Simons, L. A. Groot Zevert (DSM), priority BE 9700230, 1997-03-17: Process for purifying caprolactam, https://patents.google.com/patent/US6448395B1/en | crude lactam from the rearrangement in sulfuric acid, neutralised with ammonia, extracted counter-currently with benzene (3 to 25 theoretical stages, 20 to 80 C) and back-extracted into water (10 to 60 C); Comparative Experiment A: about 2.8 volumes of benzene per volume of feed, extract about 22 wt% lactam, raffinate 0.4 wt%, yield 99.5 %; Example I 99.8 %; Comparative Experiment D: back-extraction to about 28 wt% lactam in the water, yield 99.0 %; Example IV 99.9 % | read (Google Patents); patent, facts only | D-008 |
| SRC-6 | US 3,852,273 A, A. H. De Rooij (Stamicarbon), priority NL 7106341, 1971-05-07: Process for preparing and recovering lactams, https://patents.google.com/patent/US3852273A/en | background: about 1.7 to 1.9 t of ammonium sulfate per t of caprolactam from the rearrangement; with hydroxylammonium sulfate from the Raschig synthesis 2.5 to 2.7 t from the oximation, 4.2 to 4.6 t in all | read (Google Patents, OCR text); patent, facts only | D-001, D-012, benchmarks |
| SRC-7 | EP 1 193 251 A2, W. F. Holderich, G. Dahlhoff, H. Ichihashi, K. Sugita (Sumitomo Chemical), priority JP 2000-300265, 2000-09-29: Method for producing epsilon-caprolactam and reactor for the method, https://patents.google.com/patent/EP1193251A2/en | gas-phase Beckmann rearrangement over a zeolite (e.g. [B]-MFI) at 250 to 500 (preferably 300 to 400) C with a lower alcohol (methanol, ethanol); Example 3: fixed bed, 380 C, oxime : methanol 1 : 1.8, WHSV 8 1/h; Table 1: conversion 99.7 to 100 % and selectivity 96.2 to 97.6 % over the first 20 h, 98.5 to 99.7 % and 96.5 to 96.8 % after a regeneration; the catalyst cokes and is regenerated with nitrogen (and air) | read (Google Patents); patent, facts only | D-001 |
| SRC-8 | US 6,333,411 B1, D. F. Echegaray, A. A. M. Velloso, M. L. Wagner (Praxair), filed 1998-12-24: Method for production of hydroxylammonium phosphate in the synthesis of caprolactam, https://patents.google.com/patent/US6333411B1/en | background: the HPO process makes nitric oxide from ammonia and air, absorbs it in a phosphoric acid buffer to nitrate, hydrogenates the nitrate over palladium to hydroxylammonium phosphate and oximates cyclohexanone in toluene; the conventional route treats the oxime with sulfuric acid and neutralises with ammonia | read (Google Patents); patent, facts only | D-001 |
| SRC-9 | European Commission JRC (2017), Best Available Techniques (BAT) Reference Document for the Production of Large Volume Organic Chemicals, EUR 28882 EN (Falcke et al.), https://eippcb.jrc.ec.europa.eu/sites/default/files/inline-files/JRC109279LvocBref.pdf | section 2.1.4.7.1 Caprolactam, p. 45: four plants (cyclohexanone from phenol and hydrogen; HPO oxime with ammonium nitrate, phosphoric acid and toluene; HSO oxime and the rearrangement by the sulfate route; finishing by benzene extraction, water wash, benzene stripper, ion exchange, catalytic hydrogenation, evaporation and distillation); emissions of cyclohexanone and benzene from vents and vacuum systems, SO2 and NOx; effluent 0.1 to 1 m3/t with 1 to 10 kg COD/t from cyclohexanone to caprolactam; ammonia loads treated by nitrification/denitrification | read (PDF text); EU document, reuse with attribution (Commission Decision 2011/833/EU), facts only | D-001, D-008 to D-010, D-012 |
| SRC-10 | The open-source packages chemicals 1.5.2 and thermo 0.6.1 (core's environment), queried 2026-11-19 | formation enthalpies (kJ/mol): cyclohexanone (l) -271.2 (CRC), cyclohexanone oxime (s) -153.2 (NIST WebBook as packaged), caprolactam (s) -329.4 (CRC), H2SO4 (l) -814.0, SO3 (l) -441.0, (NH4)2SO4 (s) -1180.9, NH4NO3 (s) -365.6, HNO3 (l) -174.1, NH2OH (s) -114.2 (CRC), water (l) -285.825 and NH3 (g) -45.558 (ATcT); NH3's heat of vaporisation at 298.15 K 19.8545 kJ/mol (thermo, HEOS_FIT); water's heat of vaporisation at 373.15 K 2256.4 kJ/kg (thermo EnthalpyVaporization, HEOS_FIT); the saturation temperatures of water at 500 and 1500 kPa(a), 425.0 and 471.4 K (chemicals, iapws95_Tsat); the liquid heat capacities of process/materials.yaml (CRC_standard_data, ZABRANSKY_SPLINE, POLING_CONST, HEOS_FIT); boiling and melting points | open-source packages; single values with their source, not open data (library ADR 0037). The underlying works, as the packages' documentation names them, none of them read here: the CRC Handbook of Chemistry and Physics (Haynes, Bruno, Lide; the tables packaged in `chemicals`, the printed licensed handbook not read); the NIST WebBook and ATcT tables as packaged; Zabransky, Ruzicka, Majer and Domalski, Heat Capacity of Liquids: Critical Review and Recommended Values (1996) for ZABRANSKY_SPLINE; Poling et al., The Properties of Gases and Liquids, 5th ed. (2000) for POLING_CONST; for HEOS_FIT, thermo's polynomial fits to Helmholtz equations of state as calculated with REFPROP (no single work named); Wagner and Pruss, The IAPWS Formulation 1995 (J. Phys. Chem. Ref. Data 31, 2002) for iapws95_Tsat | materials, reactions, D-008, D-009, D-013 |
| SRC-11 | NIST Chemistry WebBook, SRD 69, caprolactam (C105602), phase change data | enthalpy of vaporization 62.3 +/- 0.2 kJ/mol at 440 K (Steele et al. 2002); boiling point 410.2 K at 0.013 bar | read | D-009 |
| SRC-12 | PubChem CIDs 7768 (caprolactam), 7967 (cyclohexanone), 7517 (cyclohexanone oxime) | identity (formula, InChIKey, CAS, ChEBI) | read (PUG REST) | registry |
| SRC-13 | Wikipedia, Caprolactam, https://en.wikipedia.org/wiki/Caprolactam | about 90 % made from cyclohexanone via the oxime and its acid-induced Beckmann rearrangement, the bisulfate neutralised with ammonia; the largest source of ammonium sulfate; about 10 % by a route that makes the oxime from cyclohexane with nitrosyl chloride (the article gives no conditions); melting point 69.2 C; N2O of 0 to 9 kg/t from production (a German-commissioned study) | read; CC BY-SA, facts only | D-001, D-012 |
| SRC-14 | processes/hydroxylamine-1, ammonia-1, sulfuric-acid-1, ammonium-sulfate-1, cumene-1, ethylbenzene-1 (this library) | hydroxylammonium sulfate solution (S24: 36683.34 kg/h, 25.4 wt% HAS, 1.86 wt% AS, 1.30 wt% H2SO4, 0.26 wt% HNO3); liquid ammonia; 98.5 wt% acid (no oleum product); ammonium sulfate by neutralisation; the undecided benzene supplier | library, internal | D-002, D-003, D-012 |

Searched and not found openly (2026-11-19): kinetics or calorimetry of the oximation, the
rearrangement in oleum and the neutralisation; a heat of rearrangement measured in oleum; the
by-products of the rearrangement's 1.1 % loss; the composition of the crude lactam (salt,
organics); the recoveries and stages of the lactam distillation; specific steam and power
consumption of a plant; the ammonium sulfate per tonne of the HPO process (one patent snippet
named a reduction "by as much as two thirds" for HPO Plus, not read in full); prices.
Not read (licensed or not open): Ullmann's Encyclopedia, Caprolactam; Weissermel and Arpe,
Industrial Organic Chemistry; process economics reports.

## D-001 Route and boundary (2026-11-19)
Decision: the conventional route with hydroxylammonium sulfate (the "HSO" or sulfate route of
SRC-9) and the rearrangement in oleum:
- R101 oximation: (NH3OH)2SO4 + 2 C6H10O + 2 NH3 -> 2 C6H11NO + (NH4)2SO4 + 2 H2O, counter-current
  at 363 K (SRC-2), ammonia neutralising the liberated acid and the solution's free acid (SRC-3);
- R201 Beckmann rearrangement of the oxime melt in oleum in a circulating loop (SRC-1, SRC-4);
- R301 neutralisation of the acid mixture with ammonia in a circulating ammonium sulfate
  solution; the crude lactam separates (SRC-1);
- C401/C402 benzene extraction and back-extraction into water, E501 evaporation, C501 vacuum
  distillation (SRC-1, SRC-5, SRC-9);
- EV601 ammonium sulfate crystallisation from the neutraliser's solution, the oximation liquor
  and the raffinate.
Boundary: gate to gate, from cyclohexanone, the hydroxylammonium sulfate solution, ammonia,
oleum, benzene make-up and water to caprolactam, ammonium sulfate crystals, a mother-liquor
purge, organic residues and surplus condensate. Outside: the cyclohexanone plant, the
hydroxylamine plant (hydroxylamine-1, with its N2O), oleum making, the ammonium sulfate's
storage and bagging, utilities, effluent treatment and incineration.
Reason: about 90 % of caprolactam comes from cyclohexanone via the oxime and its acid
rearrangement (SRC-13); the oleum rearrangement with ammonia neutralisation is described with
plant-like quantities in open BASF and DSM patents (SRC-1, SRC-2, SRC-4, SRC-5), and the
library already holds the hydroxylamine (hydroxylamine-1, the BASF NO-reduction route whose
product is made for this oximation), the ammonia and, for the co-product, ammonium-sulfate-1.
Core 1.12 models every step with conversion steps, component separators and tear streams.
Rejected:
- DSM's HPO process (SRC-8, SRC-9): hydroxylammonium phosphate from nitrate hydrogenation over
  palladium in a phosphoric acid buffer loop with ammonium nitrate, oximation in toluene. It
  avoids the oximation's ammonium sulfate, but its oxime still goes to the oleum rearrangement
  (SRC-9: the HPO oxime is converted by the sulfate route), and its buffer loop (nitrate
  absorption, degassing, a Pd hydrogenation and the organic/inorganic counter-current loop) has
  no open source with quantities read here; the library has no hydroxylammonium phosphate.
  A candidate for a later entry, sharing this entry's rearrangement and finishing.
- The gas-phase Beckmann rearrangement over a high-silica zeolite with methanol (Sumitomo,
  SRC-7), usually with ammoximation (cyclohexanone, ammonia and hydrogen peroxide over TS-1). It
  makes no ammonium sulfate, but SRC-7 gives a selectivity of 96 to 98 % against 98.9 to 99.5 %
  in oleum (SRC-4), a coking catalyst regenerated in cycles, and a methanol loop; no open source
  read gives the ammoximation's quantities; core has no deactivation or regeneration model. A
  candidate for a later entry (it would use hydrogen-peroxide-1).
- The oxime from cyclohexane with nitrosyl chloride (SRC-13, about 10 % of production): no
  source with its conditions or quantities was read.
- Raschig hydroxylamine (SRC-6): 2.5 to 2.7 t of extra ammonium sulfate per t from the oximation;
  the library's hydroxylamine-1 is the NO-reduction route.

## D-002 Capacity and operating hours (2026-11-19)
Decision: the plant takes hydroxylamine-1's whole output (its S24, 36683.34 kg/h, 30 kt/a NH2OH
at 8000 h/a) and makes 12516.6 kg/h caprolactam, 100.1 kt/a at 8000 h/a (ASSUMED hours, as
hydroxylamine-1), with 31012.7 kg/h (248 kt/a) of ammonium sulfate crystals.
Reason: hydroxylamine-1 was sized as "the hydroxylamine of a ~100 kt/a caprolactam train" (its
D-002); taking all of it ties the two entries to one site and one link.

## D-003 Feeds (2026-11-19)
Decision: cyclohexanone pure at 298 K; the hydroxylammonium sulfate solution as hydroxylamine-1
gives it (25.4 wt% HAS, 1.86 wt% AS, 1.30 wt% H2SO4, 0.26 wt% HNO3, 313 K, 180 kPa(a), SRC-14);
liquid ammonia at 298 K and 1200 kPa(a), injected as liquid into both reactors (D-007); oleum of
32 wt% SO3 (SRC-1's Example) at 303 K;
benzene and demineralised water pure. Impurities of the feeds are not modelled (ASSUMED).
The solution's HNO3 is neutralised to ammonium nitrate (NEUTN) and leaves with the purge.

## D-004 Oximation R101 and the oxime separator D101 (2026-11-19)
Decision: a conversion step at 363 K (SRC-2's 90 C): OXIM converts all the hydroxylammonium
sulfate (ASSUMED complete: SRC-2's counter-current contact with fresh cyclohexanone returns the
residual hydroxylamine), NEUTA and NEUTN all the free acids. The cyclohexanone feed is set by a
design specification (SP-CHN, core ADR 0070) so that the melt carries SRC-2's 0.6 wt%
cyclohexanone: 0.73 % above the hydroxylamine; ammonia by SP-NH3OX, stoichiometric plus 0.5
kg/h. D101 sends all the oxime and cyclohexanone and 4.6 wt% water (SRC-2's Example) to the melt,
the rest to the liquor (24.2 wt% ammonium sulfate and 0.34 wt% ammonium nitrate), which goes to
the neutraliser as part of its diluent (D-007). The melt is cooled from 363 to SRC-1's 358 K in
E-101 (D-013).
Reason: SRC-2's oximation is the acid variant without ammonia (its liquor, ammonium bisulfate,
goes back to the hydroxylamine synthesis); the library's hydroxylamine-1 does not take a
bisulfate liquor back, so the classic variant with ammonia to pH 4.5 to 5.8 (SRC-3) is used,
with SRC-2's temperature and melt composition (ASSUMED transferable).
Results: Q1 = 3538 kW to cooling water (core's conversion-step duty), an upper bound: the heat
of reaction leaves out the heat of forming hydroxylammonium sulfate from hydroxylamine and acid
(D-008, L-3), and Q1 could be near zero.

## D-005 Components (2026-11-19)
Decision: the salts are molecular components (HAS, AS, AN), dissolved; the lactam in the oleum is
counted as caprolactam and H2SO4, not as its bisulfate; one template `process` with every
component for the streams below the reactors, because propagate writes every component that
reaches a stream.
Reason: core has no speciation or electrolyte model beyond aqueous NaCl (L-1); as hydroxylamine-1.

## D-006 Beckmann rearrangement R201 (2026-11-19)
Decision: oleum 32 wt% SO3 at 1.17 kg per kg of melt (SRC-1's Example; the ratio is read per kg
of the oxime as fed, the melt with its water; set by the specification SP-OLEUM), 388 K (SRC-1's
115 C), a circulating loop with its cooler E-201 and pump P-201. Conversion step: BECK 98.9 % of
the oxime, ASSUMED transferable from SRC-4 Comparative Experiment A: that yield was measured in
three stages at 102 and 86 C with 25 wt% SO3 oleum (about 0.91 kg per kg oxime in all), not in
this single loop at 115 C with 32 wt% oleum at 1.17 kg/kg; only the oxime's water (4.7 wt%
against this melt's 4.6) matches. The 1.1 % loss as HYDR,
hydrolysis back to cyclohexanone and hydroxylammonium sulfate (ASSUMED representation: SRC-4
names no by-product, only that impurities stay in the water phase); SO3W takes up the melt's
water with free SO3. The mixture leaves with 8.2 wt% free SO3, inside SRC-1's 1 to 14 wt%; the
molar ratio (SO3 + H2SO4) / lactam is 1.54 (SRC-4's single first stage 1.2 to 2.2).
Rejected for now: SRC-4's three stages with a final ratio of 1.18 (less oleum, less ammonium
sulfate). SRC-4 gives the wet case fully (the oxime and oleum per stage, the stage temperatures
and ratios); the single loop was chosen to keep the rearrangement on SRC-1, whose BASF loop also
sets the neutralisation and the crude lactam that follow, in one conversion step. The staged
DSM design, with less oleum per kg, is a later option (open item O-3).
Results: Q2 = 5752 kW to cooling water, without the oleum's heats of solution and the lactam's
protonation (L-3).

## D-007 Neutralisation R301 and the crude lactam separator D301 (2026-11-19)
Decision: the acid mixture, liquid ammonia (stoichiometric plus 0.5 kg/h, SP-NH3NE), the
oximation liquor and recycled crystalliser condensate into a circulating solution at 353 K
(ASSUMED; SRC-1 gives pH 4 to 5 but no temperature). NEUT and NEUT3 neutralise all the H2SO4 and
SO3 on a liquid-ammonia basis. The condensate split X601 (0.4938 of it) is set by the
specification SP-AS40 so that the solution leaving D301 holds 40 wt% ammonium sulfate (SRC-1's
Example, 40 to 43 %). D301 sends 99.9 % of the lactam (ASSUMED), all the cyclohexanone, 1.5 wt%
salt (ASSUMED) and 30 wt% water (SRC-1) to the crude lactam, which E-302 cools to the
extraction's 323 K (D-013).
Departure from SRC-1 (ASSUMED): SRC-1 passes in gaseous ammonia; here the pressurised liquid is
injected into the loop, so that the ammonia's latent heat (345.4 kmol/h x 19.85 kJ/mol = 1.9
MW) is taken from the loop instead of from a vaporiser. With SRC-1's gaseous feed the plant
would need a 1.9 MW ammonia vaporiser and Q3 would be 1.9 MW higher (about 13.9 MW); the net
utility is the same if the vaporiser is heated by the loop. Whether liquid injection is
acceptable for the loop's pH control and local boiling is open (O-9).
Reason: the oximation liquor and the condensate are the plant's own water; no fresh water
reaches the neutraliser.
Results: Q3 = 11957 kW to cooling water; at 353 K, below the plant's LP steam level (425 K,
500 kPa(a)), the heat cannot raise steam; it could at most drive a vacuum effect of the
crystalliser (O-4). 1.82 kg ammonium sulfate per kg of caprolactam is formed from the rearrangement's acid,
inside SRC-6's 1.7 to 1.9.

## D-008 Extraction and heats (2026-11-19)
Decision: C401 extracts 99.6 % of the lactam (between SRC-5's 99.5 and 99.8 %) and all the
cyclohexanone into benzene, with no water or salt in the extract (ASSUMED); the benzene
circulation (44.7 t/h) gives SRC-5's 22 wt% extract. C402 returns 99.9 % of the lactam into water
(SRC-5 Example IV) at 28 wt% (SRC-5), with the cyclohexanone (ASSUMED, so that it leaves the
solvent loop) and 0.05 % of the benzene (ASSUMED loss, the make-up S13, 1.8 g/kg). The raffinate
goes to the crystalliser. The loops: benzene (tear S14), back-extraction water (S19).
Heats: the three reactors' duties are core's conversion-step duties (core ADR 0059) from the
heats of reaction of process/reactions.yaml (SRC-10) and the constant liquid heat capacities of
process/materials.yaml; the bases are ASSUMED (salts as solids, oxime and lactam as solids, HAS as
2 NH2OH + H2SO4 without a heat of salt formation, no heats of solution, dilution or protonation).
The HAS basis matters most: of OXIM's -343.3 kJ/mol, -236.1 kJ/mol is NEUTA's neutralisation of
free sulfuric acid, which in HAS is already bound to the hydroxylamine; the omitted heat of salt
formation comes straight off it. No formation enthalpy of HAS was found openly (neither package
has one; the NBS tables' scan has no text layer to search). Each 100 kJ/mol of it lowers Q1 by
1.58 MW (56.77 kmol/h), and a heat of the order of NEUTA's would take Q1 to about zero. Q1 =
3.5 MW is therefore an upper bound, safe for sizing R-101's cooling, not an estimate (L-3, O-1).
Rejected: an NRTL extraction model (`cheme process extract`): no binary parameters for lactam,
benzene, water and ammonium sulfate were found openly (L-2).

## D-009 Purification and utilities (2026-11-19)
Decision: E501 evaporates the aqueous lactam to 99 wt% in three effects (ASSUMED) with LP steam
500 kPa(a) and sends the benzene and cyclohexanone to the organic residues (the BREF's benzene
stripper, ASSUMED not recovered); its condensate is the back-extraction water, with a make-up of
128 kg/h. The last condenser takes the vapour of one effect (Q5 6732 kW = 32220 kg/h x 2256.4
kJ/kg (SRC-10) / 3); the steam Q4 = 7284 kW adds the sensible heat the 383 K concentrate takes
out (D-013). C501 distils under vacuum: 99.0 % of the lactam as product, 0.3 % with the water in
the lights, 0.7 % in the residue (ASSUMED); reboiler Q6 3920 kW of MP steam at reflux 1
(ASSUMED) with caprolactam's 62.3 kJ/mol at 440 K (SRC-11); the condenser and the product cooler
Q7 = 4360 kW take the reboiler's heat, the vacuum system's power and the feed's sensible heat.
The ion exchange and the catalytic hydrogenation SRC-9 names are not modelled; the product's
commercial specification (permanganate and UV numbers, SRC-1) is not modelled (O-2). Cooling
water 298/308 K; power per step ASSUMED (P1 to P6, 1.9 MW in all, no open source). All ASSUMED.

## D-010 Ammonium sulfate crystallisation (2026-11-19)
Decision: the neutraliser's solution and the raffinate (84.4 t/h) are evaporated in a
three-effect crystalliser (Q8 10774 kW of LP steam = 51569 kg/h x 2256.4 kJ/kg / 3, ASSUMED
effects), the crystals centrifuged and dried: 98 % of the salt as crystals (ASSUMED), a purge of
35 wt% ammonium sulfate (ASSUMED) taking every impurity (hydroxylammonium sulfate, ammonium
nitrate, lactam, ammonia) to biological treatment (SRC-9). The last condenser and the product
coolers take Q9 = 14387 kW: the steam, the 900 kW of power and the sensible heat of the 350 K feed
above the products at 313 to 323 K (D-013). The dryer: a centrifuge cake of 3 wt% moisture
(ASSUMED, 959 kg/h) dried with steam-heated air at 60 % efficiency (ASSUMED), Q13 = 1002 kW of LP
steam, leaving with the exhaust air (Q14 to the ambient). Conservative: the model counts the
cake's moisture in the condensate and in Q8 as well (about 0.2 MW). The condensate (51.6 t/h):
25.5 t/h to the neutraliser (tear S32), 26.1 t/h surplus.
Reason: the plant's salt leaves as a sellable solid; the purge keeps the impurities from
building up. The surplus condensate (2.09 m3/t) is clean water; the BREF's 0.1 to 1 m3/t of
effluent (SRC-9) implies its reuse on site (O-5).

## D-011 Lists at concept (2026-11-19)
Decision: equipment list with the PFD's 20 items (no P&ID yet), design pressure = highest
operating + 10 % (at least + 2 bar), design temperature + 25 K; first-choice materials (316L for
the salt solutions, an oleum-resistant alloy for the rearrangement loop, an open input). Line and
instrument lists empty until P&IDs. All ASSUMED.

## D-012 Preliminary gate-to-gate LCI (2026-11-19)
Decision: `cheme assess lca --write` per kg of caprolactam. Linked (lca/mappings.yaml): the
hydroxylammonium sulfate solution to hydroxylamine-1's product:PROD (same composition, kg for
kg), the ammonia to ammonia-1's product:NH3, the LP and MP steam as heat (steam-heat). The benzene
make-up is `atlas: false` (supplier undecided, as cumene-1). Gaps with recorded proxies:
cyclohexanone (phenol hydrogenation, SRC-9, or cyclohexane oxidation; adipic-acid-1 keeps its KA
oil internal); oleum (0.68 kg sulfuric acid of sulfuric-acid-1 and 0.32 kg SO3 per kg; a shared
estimate proxy, ADR 0039, is a separate change of lci/mappings.yaml). The rest are gaps.
Allocation: economic between caprolactam and the ammonium sulfate crystals, written as shares
0.8522 and 0.1478 at an ASSUMED relative price per kg of 1 : 0.07: no physical relationship of the
library hierarchy applies, and the WBCSD rule gives economic allocation above a price ratio of 5.
Mass allocation would leave the caprolactam 28.8 %; the conservative bound is 100 %. The
ammonium sulfate has no inventory_key in process.yaml, so this plant is not offered as an Atlas
producer of it beside ammonium-sulfate-1 (as cumene-1's steam).
Per kg of caprolactam, unallocated: cyclohexanone 0.897 kg, hydroxylammonium sulfate solution
2.931 kg, ammonia 0.640 kg, oleum 1.267 kg, benzene 1.8 g, water 0.010 kg, electricity 0.152
kWh, LP steam 1.523 kWh, MP steam 0.313 kWh, cooling water 3.791 kWh (with Q1 an upper bound,
D-008), the dryer's exhaust heat 0.080 kWh (free); out: ammonium sulfate 2.478 kg, purge 0.144
kg, organic residues 0.038 kg, condensate 2.086 kg.
Not counted (`emission_exclusions`): tank breathing, vacuum vents, SO2 and NOx (SRC-9 names
them, no amount found). The N2O of 0 to 9 kg/t (SRC-13) comes from the hydroxylamine's ammonia
oxidation, which is in hydroxylamine-1's boundary, not this plant's.

## D-013 Energy balance of the non-reacting steps (2026-11-19)
Decision: every step without a reaction closes its energy balance on the same basis core uses for
the reactors' duties (ADR 0059): the constant liquid heat capacities of process/materials.yaml,
sensible enthalpy from 298.15 K, the stream temperatures, flows and compositions of the
flowsheet, a step's electric power counted as heat into it. `scripts/energy_balance.py` computes
it (the library's balance-output contract, checked by scripts/check_balance_scripts.py):
- where the design sets an outlet temperature below the inlet, a cooler: E-101 on the oxime melt
  (Q10, 46 kW, to SRC-1's 358 K), E-302 on the crude lactam (Q11, 436 kW, to the extraction's
  323 K), E-402 in the back-extraction (Q12, 241 kW, to 313 K);
- where nothing cools, the outlet temperature follows: C401 adiabatic (the extract and the
  raffinate at 321.3 K, with the column's 150 kW of power), M601 adiabatic (the crystalliser feed
  at 350.3 K);
- the evaporators' and the column's coolers and steam close their steps (D-009, D-010): the
  steam of E501 includes the concentrate's sensible heat, the condensers of C501 and EV601 take
  the power and the feed's sensible heat above the products.
Reason: the first version set Q5, Q7 and Q9 equal to their steam and left the coolers the
temperatures imply without a duty: about 5.3 MW of cooling (12 % of the cooling water) and 0.55
MW of steam were missing (review of PR #499). The mixers M401, M402, M502 and the splitter X601
close within 5 kW without a duty and keep their set temperatures.
Assumes: constant heat capacities (the dissolved salts with the solids' values, HAS by analogy,
SRC-10), no heats of solution, dilution or crystallisation of the salts (L-3), no heat losses
except the dryer's exhaust.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| oximation, rearrangement, neutralisation (R101, R201, R301) | done in cheme (conversion steps) | D-004, D-006, D-007 |
| their duties Q1 to Q3 | done in cheme (core ADR 0059), heat bases ASSUMED | D-008, SRC-10 |
| separators D101, D301, C401, C402, E501, C501, EV601 | done in cheme (component separators), fractions sourced or ASSUMED | D-004, D-007 to D-010 |
| benzene, back-extraction water and condensate recycles | done in cheme (tears S14, S19, S32, solved with the specifications) | core ADR 0060, 0070 |
| feed flows S01, S03, S07, S09 and the condensate split | done in cheme (design specifications SP-CHN, SP-NH3OX, SP-OLEUM, SP-NH3NE, SP-AS40) | core ADR 0070; D-004, D-006, D-007 |
| energy balance of the non-reacting steps: coolers, evaporators' and column's duties, adiabatic temperatures | balance script scripts/energy_balance.py on core's heat basis; economies, reflux, dryer and power ASSUMED | D-009, D-010, D-013 |
| extraction equilibria, distillation stages | not done (no open parameters) | L-2 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core features used (core 1.12.0)

- Conversion steps (`reactor: conversion`) with several parallel reactions keyed on different
  components; their duties written by `process propagate` from `heat_of_reaction` and
  `liquid_heat_capacity` (ADR 0059) on cooling-water terminals, with the steps' power taken as
  work in.
- Component separators with several outlets (`recovery.outlets`, ADR 0070), a splitter.
- Design specifications (`specs:`, ADR 0070): four feed flows (component fraction, component
  flow and mass ratio targets) and a splitter fraction (a component fraction target), solved
  with the three tear streams (ADR 0060).
- `lca.yaml` with `allocation: shares`, `emission_exclusions`, wastes with `treatment`.

## Core limits hit (each a candidate core issue)

- L-1: no aqueous electrolyte or speciation model beyond NaCl: the salts are molecular
  components; the lactam's bisulfate in oleum and the pH of the oximation and the neutraliser
  are not represented.
- L-2: no property package for the salt solutions, the lactam in oleum or lactam/benzene/water;
  no published NRTL pairs for them; so the extraction, evaporation and distillation are
  specified splits, and their duties come from a balance script on constant heat capacities
  (D-013).
- L-3: a conversion step takes declared heats only (ADR 0059): the oleum's heats of solution, the
  lactam's protonation, the salts' heats of solution and the oxime's and lactam's heats of fusion
  have no term, so Q2 and Q3 are split between the rearrangement and the neutraliser in a way the
  real plant does not (their sum is the meaningful number). Where a formation enthalpy is
  missing (hydroxylammonium sulfate), the basis chosen leaves out a heat that may be as large as
  the duty itself: Q1 is an upper bound (D-008). The same constant heat capacities without
  heats of solution carry the non-reacting steps' balance (D-013).
- L-4: a design specification (ADR 0070) varies a feed's flow or a splitter's fraction, not a
  separator's `recovery:` fraction: the water and salt fractions of D101, D301, E501 and EV601
  were computed by hand from their targets (4.6 and 30 wt% water, 1.5 wt% salt, 1 wt% water, a
  35 wt% purge; the arithmetic is in each `source`) and drift slightly when the feeds move.
- L-5: a recycle with a loop gain near 1 (the benzene loop loses 0.05 % per pass) converges slowly
  from a poor guess; the tear guesses are the hand balance's values.

## Open inputs

| id | what | why it matters |
|---|---|---|
| O-1 | heats of rearrangement in oleum and of neutralisation by calorimetry; the formation enthalpy of hydroxylammonium sulfate | the cooling duties Q2, Q3; Q1, now an upper bound |
| O-2 | product specification (permanganate, UV, volatile bases), ion exchange and hydrogenation | product quality, the residue and lights |
| O-3 | staged rearrangement with a lower final acid ratio (SRC-4) and a dry oxime | ammonium sulfate per kg, yield |
| O-4 | heat recovery from the neutraliser (12 MW at 353 K, below the LP steam level) into a vacuum effect of the crystalliser | steam use |
| O-5 | reuse of the surplus condensate; effluent per tonne against the BREF's 0.1 to 1 m3/t | water |
| O-6 | crude lactam composition, distillation recoveries, evaporator economies, power | yields, utilities |
| O-7 | prices for the allocation | the LCI shares |
| O-8 | hazards: oleum and SO3 handling, the runaway of the rearrangement at loss of cooling or circulation, ammonia, benzene (carcinogen) exposure | HAZOP at basic engineering |
| O-9 | liquid against gaseous ammonia into the neutraliser (SRC-1 uses gas): pH control, local boiling; a 1.9 MW vaporiser if gas | Q3, equipment (D-007) |
