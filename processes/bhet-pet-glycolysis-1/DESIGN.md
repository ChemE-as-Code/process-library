# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
BHET (bis(2-hydroxyethyl) terephthalate) by glycolysis of post-consumer PET, issue
ChemE-as-Code/process-library#516, a batch entry of the library and its first depolymerisation of
a condensation polymer. Concept stage: design basis, batch recipe, balanced BFD/PFD, thermal
screening and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA,
datasheets.

Starting point (2026-11-19): library `main` with the core pin v1.13.0 (b97a833). Core models what
the route needs: the crystallizer with spectator solutes, imposed yields and a reslurry
redissolution (core ADRs 0056, 0076), the dryer and the recipe (ADRs 0051, 0052, 0057), recycles
with tear streams (ADR 0060), design specifications and component separators (ADR 0070), the
models' duties (ADR 0059) and the thermal screening (ADR 0058). Library ADR 0035: one dedicated
train, campaigns out of scope (D-013). Templates: `salicylic-acid-1` (batch crystallisation,
centrifuges, dryer, recycles, the structure of this file) and `oxalyl-chloride-1` (batch entry
structure), `vcm-1`, `pet-1` (continuous entries, the PET value chain). Issue #516 proposed the id
`pet-glycolysis-1`; the entry is named after its product, `bhet-pet-glycolysis-1`.

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work. The `chemicals` and `thermo` Python packages (SRC-7) were queried for single values,
facts only with their source; the licensed works behind them were not read (library ADR 0037).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | Luo, Y.; Selvam, E.; Vlachos, D. G.; Ierapetritou, M. (2023) ACS Sustainable Chem. Eng. 11, 4209-4218, doi:10.1021/acssuschemeng.2c07203, NSF public-access copy https://par.nsf.gov/servlets/purl/10429439 | Methods (500 mg PET, 5 mL EG, 5 mg ZnO; water added and heated to 80 C, oligomers filtered, BHET crystallised at 4 C); Results: 100 % conversion and 95 % BHET in 10 min at 210 C; the water-antisolvent case cooled to 5 C with the EG/water distillation the leading utility; the cooling case crystallises from EG at 30 C, the EG recycled; preheat by the reactor outlet to 196 C; DEG and TEG below 0.3 %; 837 kg BHET/h; GWP 0.636 vs 4.37 kg CO2-eq/kg for the DMT route | read (text extracted from the PDF) | D-001, D-005, D-009, D-012 |
| SRC-2 | Goh, H. W.; Salmiaton, A.; Abdullah, N.; Idris, A. (2015) Bull. Chem. React. Eng. Catal. 10(2), 143-154, doi:10.9767/bcrec.10.2.7195.143-154 | 2.1: PET:EG 1:5 by mass, 1.5 % zinc acetate on PET, 196 C, 8 h under reflux and nitrogen; 2.2: hot water (about 75 C) to the glycolysed solid, cooled 1 to 30 C; 3.1: BHET melts at 106 to 110 C; 3.4-3.5: 5:1 water, 2 C, 3 h gave 93 % BHET in the product | read (journal PDF, free to read) | D-001, D-003, D-007 |
| SRC-3 | EP 0 723 951 A1, Pilati, F. et al., filed 1996-01-24: Process to prepare bis(2-hydroxyethyl) terephthalate, https://patents.google.com/patent/EP0723951A1/en | description: catalysts (Zn, La, Ce acetates, Ti(OBu)4), 0.2 to 1.5, preferably 0.5 g per kg of PET and EG; EG/PET 1 to 5, preferably 2 to 3; 190 to 210 C; methods A, B and C; the quench at 60 to 90 C (preferably 65 to 75) that keeps BHET dissolved and the oligomers out; crystallisation at -10 to +30 C (preferably 5 to 15); the second crystallisation from 4 to 10 (preferably 6 to 8) kg water per kg BHET at 70 to 100 C; the aqueous solutions distilled and water and EG recycled, the oligomers recycled; Examples 1 to 5; claims 1 to 7 (over 90 % with the oligomers recycled) | read (Google Patents text) | D-001, D-004 to D-008 |
| SRC-4 | US 4 078 143 A (1978): Process for depolymerizing waste ethylene terephthalate polyester, https://patents.google.com/patent/US4078143A/en | DEG formed at 0.08 to 0.35 mol % per hour at 225 to 235 C (Table I), less with sodium acetate and water; glycolysis at 200 to 240 C; continuous hold-up 4 to 15 h | read (Google Patents text) | D-001, D-005 |
| SRC-5 | CN 110 590 551 A: Method for producing bis(2-hydroxyethyl) terephthalate and method for producing polyethylene terephthalate, https://patents.google.com/patent/CN110590551A/en | the solubility of BHET in water at 20 C, 0.5 % (w/v); hot water at 65 to 85 C dissolves crude BHET, 3 to 10 parts per part | read (Google Patents machine translation, the passages on solubility) | D-007 |
| SRC-6 | US 7 211 193 B2: Processes for the purification of bis(2-hydroxyethyl)terephthalate, https://patents.google.com/patent/US7211193B2/en | crude BHET crystallised from its glycol solution at 15 to 30 C for 1 h or more after deionisation; glycolysis at 190 to 220 C | read (Google Patents text, the crystallisation passages) | D-001 |
| SRC-7 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (core's environment) | chemicals: normal boiling points of water and EG (method HEOS) and DEG (CRC_ORG: CRC Handbook tables), BHET's melting point 382.65 K (CRC_ORG), the InChIKeys and PubChem CIDs of BHET and zinc acetate, IAPWS-95 saturation, vapour pressure and enthalpies of water; thermo: HEOS_FIT (a fit to the CoolProp equation of state) for the density, heat capacity, vapour pressure and latent heat of water and EG, ZABRANSKY_SPLINE (Zabransky et al., not read) and "Fit 2023" for DEG, the estimates YEN_WOODS_SAT and DADGOSTAR_SHAW for BHET | single values queried; facts with the package and method named, not open data (ADR 0037) | materials.yaml, D-005, D-006, D-008, D-009 |
| SRC-8 | processes/ethylene-glycol-1, demineralised-water-1, pet-1 (this library) | MEG of EO hydration; demineralised water; PET from PTA and MEG | library, internal | D-004, D-012 |

Searched and not found openly (2026-11-19): kinetics or calorimetry of the glycolysis with zinc
acetate at atmospheric reflux; a formation enthalpy of BHET or PET; a TD24 of the glycolysate;
BHET's solubility in water as a function of temperature (SRC-3's graph 1 is a figure, not read
as data) and in water-glycol mixtures (Yuan et al. 2022, J. Chem. Eng. Data 67, 2693, was found
but is not open); the drying rate of BHET; the dewatering column's design.

## D-001 Route and boundary (2026-11-19)

**Decided:** zinc-acetate-catalysed glycolysis of washed post-consumer PET flake with ethylene
glycol at its atmospheric reflux, and recovery of BHET by crystallisation from water, SRC-3's
method B (Example 2): the hot glycolysate is filtered of coarse impurities and quenched with
water to about 70 C, the oligomers are filtered off, the BHET crystallised at 15 C, redissolved
in hot water and recrystallised at 15 C; the aqueous liquors are distilled and the water and the
glycol recycled, and so are the oligomers. A batch plant on a dedicated train (D-013).

**Why:** SRC-3 is the one open source read that gives a complete batch route, glycolysis to
purified BHET, with amounts at every step of a worked example, a quality of product (white,
116 C melting point, Zn 6 ppm for method A) and recycles of the liquors and the oligomers. Zinc
acetate is its fastest catalyst (its relative speed 100, the highest at 190 C) and the one SRC-2
uses. The glycol's reflux at atmospheric pressure needs no pressure vessel.

**Rejected:**
- SRC-3 method A (the excess glycol filtered off the cooled paste before the hot water): one more
  separation of a viscous paste; method C (crystallised before the oligomers are removed): one
  more filtration and the oligomers co-crystallise with BHET (SRC-3 Example 4).
- SRC-1's cooling crystallisation from the glycol at 30 C with a heterogeneous ZnO catalyst under
  microwave heating: it avoids the water and its distillation, the largest heat duty here
  (D-009), and SRC-1 finds it far lower in GWP; but its product purity is not reported, its
  crystals come from a glycol liquor with the dyes and additives of the waste, the microwave
  heating at industrial scale is open, and it is continuous. Recorded as the lower-energy
  alternative (D-009).
- SRC-6's crystallisation from the glycol after deionisation and activated carbon (and a BHET
  distillation in its family): more units than a concept needs.
- SRC-4's continuous glycolysis of in-plant fibre waste with BHET as the solvent, sodium acetate
  and water injection: it makes a BHET-oligomer mix for direct repolymerisation, not purified
  BHET from post-consumer waste.
- Methanolysis to DMT and hydrolysis to terephthalic acid: other products, higher pressures
  (SRC-3's background).

**Boundary:** from the washed, dried flake (sorting, washing and grinding outside, D-012) and
purchased glycol, catalyst and water to the dried BHET at packing; the wastes to incineration and
wastewater treatment outside; steam, cooling water, chilled water and power from the site.

## D-002 Capacity, product and operating hours (2026-11-19)

5000 t/a of dried BHET (ASSUMED), 7920 h/a: a regional chemical-recycling train of about
4900 t/a of washed flake, between SRC-1's modular 132 kg PET/h line and its 50 000 t/a plant.
The product is BHET crystals for PET polycondensation (pet-1 makes PET from PTA and MEG; a
recycled-BHET feed to it is not linked yet).

## D-003 Batch basis, recipe and vessels (2026-11-19)

The recipe (process/recipe.yaml) holds one batch of 3944.66 kg of BHET every 6.248 h, 1268
batches a year: the fixed point of batch size = rate x cycle that cheme.recipe-basis names (the
drying time grows with the batch). R-101's procedure takes 6 h (charging 1.5 h, heat-up 1.5 h,
2 h at reflux from SRC-3 Example 1, hot filtration 1 h; all ASSUMED but the 2 h); D-201's takes
6.248 h with 4.75 h of drying from D201's rate and sets the cycle (`cheme process recipe`:
bottleneck DRY), R-101 close behind. The crystallisers take 3 h to cool (SRC-2 crystallises 3 h,
SRC-3 samples after about 3 h), the centrifuges 2 h (ASSUMED). The recipe sizes D-201 (12.5 m3);
core sizes no vessel from a conversion step or a crystallizer (L-5), so R-101 (16 m3), V-201 and
V-202 (50 m3), V-203 (40 m3) and the second mother liquor's tank T-304 (40 m3, D-006) are sized
by hand from one batch's content (equipment list).

## D-004 Feeds and charge (2026-11-19)

- Washed, dried PET bottle flake with 0.5 wt% non-PET solids (cap and label fragments, lumped as
  polyolefin IMP), ASSUMED; its moisture, dyes, additives and PVC traces not modelled.
- The charge holds 2 kg of glycol per kg of PET (SRC-3: 1 to 5, preferably 2 to 3; Examples 1 to
  3: 600 g per 300 g), the recovered glycol counted in it; a design specification sizes the fresh
  glycol (0.315 kg/kg BHET; the stoichiometric 0.244).
- 1.5 g of zinc acetate per kg of PET in the charge (SRC-3 Example 1: 0.45 g per 300 g, the
  preferred 0.5 g per kg of the mix), the catalyst returned with the recovered glycol counted;
  a design specification sizes the make-up (0.06 g/kg BHET). Counted anhydrous (SRC-2 used the
  dihydrate).
- Fresh glycol from ethylene-glycol-1, make-up water from demineralised-water-1 (SRC-8).
- Four design specifications (core ADR 0070) size the flake for 5000 t/a, the fresh glycol, the
  catalyst and the make-up water (D-007).

## D-005 Glycolysis R101: heat-up distillation, conversion step and reactions (2026-11-19, revised 2026-11-20)

R101 is a conversion step at 470.15 K and 101.325 kPa(a), the glycol's reflux (SRC-3 Example 1;
the glycol boils at 470.31 K, SRC-7).

**The charge's water is distilled off in the heat-up (X101; revised 2026-11-20 after review).**
The charge S4 holds 4.3 wt% water (17.5 mol %): about 54 kg/h from the wet oligomer cake S21
(36 wt% water) and 18 kg/h from the recovered glycol S20 (2.2 wt%). At 470 K water's vapour
pressure is 1460 kPa (IAPWS-95, SRC-7), so that liquid cannot exist at 470 K and 101.325 kPa: its
bubble point is 424.6 K by Raoult's law (the glycol's vapour pressure from thermo HEOS_FIT, the
BHET and solids non-volatile). As R-101 heats, the water boils off first; a short packed section
under the overhead condenser E-101 returns the glycol and takes the water (99 %, with 0.2 % of the
glycol, ASSUMED) to the liquor tank T-301 and the dewatering column (S33, 0.46 t a batch). The
glycolysate S5 keeps 0.27 mol % water, below the 1.39 mol % a liquid with its glycol can hold at
470.15 K; its bubble point by the same law is 476.1 K, inside SRC-3's 190 to 210 C, so the batch
boils at about 470 to 476 K as the BHET forms (the split, D-005 below, is taken at 470.15 K).
Rejected: refluxing the water back (the pot would boil near 425 K, not at the reflux SRC-3's 2 h
assume) and leaving it in the liquid (the model the review found impossible). The step is a
component separator before R101: the dewatered charge S32 is kept at the charge's 320 K so that
core's conversion duty Q1 counts its heat-up and Q10 the water's evaporation (D-009).

Reactions (process/reactions.yaml):
- GLY 0.87 and OLF 0.13 of the PET repeat units, to BHET and to oligomers lumped as the BHET
  dimer C22H22O10: SRC-3 Example 2's 45 g of oligomer solid per 300 g PET is 0.101 mol of dimer,
  12.9 % of the 1.561 mol of repeat units (ASSUMED that the solid is all oligomer). All the PET
  reacts (SRC-1: 100 % conversion; SRC-3's hot filtration takes off only coarse impurities).
- DEP 0.87 and DSO 0.13 of the recycled oligomers: glycolysed to the same share as the fresh PET
  (ASSUMED), the rest dissolved back as oligomer.
- DEG 0.0006 of the glycol charged: about 0.2 mol of DEG per 100 mol of repeat units a batch,
  the low end of SRC-4's 0.08 to 0.35 mol % per hour at 225 to 235 C taken for 2 h at 470 K
  (ASSUMED). The DEG builds up in the recovered glycol to 1.0 wt% (S20), bounded by the purge.
- Every heat of reaction ASSUMED 0: the glycolysis exchanges one ethylene ester for another; no
  open calorimetry or formation enthalpy of BHET found. R101's duty Q1 (137.7 kW year average) is
  the dewatered charge's heat-up to 470 K, core's conversion duty. The water's evaporation and
  the reflux boil-up over the 2 h hold (ASSUMED 500 kg/h of glycol, about 5 % of the charge an
  hour, at its 879.3 kJ/kg latent heat, SRC-7) are Q10 (88.9 kW, HP steam) and the condenser
  E-101's Q11 (89.5 kW, cooling water), by hand (L-2, D-009).

R101 converts the 487.2 kg/h of PET in the charge and the 74.8 kg/h of recycled oligomers: model
yield 97.7 % of the fresh repeat units to dried BHET (SRC-3 claims over 90 % with the oligomers
recycled; the glycol recycle here also returns the BHET of the first mother liquor, D-008).

## D-006 Quench and oligomer removal (2026-11-19, revised 2026-11-20)

The hot glycolysate runs into the second mother liquor of the batch before last (about 2.6 kg per
kg of glycolysate: SRC-3 preferred 0.5 to 2, range 0.1 to 10; ASSUMED all of it, so the water is
used twice) in V-201 at 343.15 K (SRC-3: 65 to 75 C preferred, Example 2 at 70 C). The liquor
cannot come from the batch just before: the recipe runs C-204 at 14.5 to 16.5 h of a batch, after
the next batch has taken its quench liquor at 11.25 h (cycle 6.248 h), so the batch after next
(17.5 h) is the first that can use it. It waits in its own tank T-304 (40 m3, one batch's 26.1 t);
V-201, idle from 14.75 to 17.5 h, could hold it instead, but C-204 starts before F-201 has
emptied V-201 and V-201 would be occupied the whole cycle (rejected). After a start-up the first
two batches quench with make-up water from T-302. The year averages and the tear S19 do not
depend on this lag. CR201 precipitates
98 % of the oligomers there (ASSUMED from SRC-3 Example 4: the higher oligomers insoluble near the
boiling point, the dimers and trimers dissolved above 80 to 90 C, BHET dissolved above 60 C). The
cold liquor outweighs the glycolysate's heat, so V-201 takes 130.9 kW of LP-steam heat (Q2, core's
crystallizer duty). Core's crystallizer balances its two inlets at one heat capacity and their
mass-weighted mean temperature (L-7), which gave 15.1 kW; CR201 is therefore given its inlets' own
heat capacities (thermo's mean values over each inlet's range, SRC-7) as a mean heat capacity at
the heat-capacity-weighted feed temperature (320.81 K), so that core's duty is the exact sum of
the glycolysate cooled from 470 K and the liquor heated from 288 K (the arithmetic in CR201's
source). F201 takes all the oligomers
with 1 kg of liquor per kg (ASSUMED); 90 % of the cake goes back to the next charge, 10 % is
purged to incineration to bound the impurities the oligomers carry (ASSUMED).

## D-007 First crop, redissolution and second crop (2026-11-19)

- CR202 cools the oligomer-free liquor to 288.15 K (SRC-3: 5 to 15 C preferred, Example 2 at
  15 C) and crystallises 90 % of the dissolved BHET (an imposed yield, ASSUMED from SRC-3
  Example 2: about 305 g of the about 338 g of BHET recovered as the residue of 485 g; no
  solubility of BHET in water-glycol mixtures was found openly, L-3).
- CR203 redissolves the crude cake in 6 kg of water per kg of BHET at 353.15 K (SRC-3: 6 to 8
  preferred, 70 to 100 C; a design specification sizes the make-up water). The solution stays
  undersaturated against a lower bound of 0.18 kg/kg (SRC-3 Example 4: 180 g of BHET dissolved in
  1000 g of water above 60 C), so all the crystals dissolve.
- CR204 recrystallises at 288.15 K to BHET's water solubility, 0.005 kg/kg (SRC-5: 0.5 % w/v at
  20 C, taken per kg of water and used at 15 C, an upper bound since the solubility falls with the
  temperature): 96.7 % of the BHET crystallises.
- The second mother liquor (S19, 98 % water with 0.5 % BHET and 1.6 % glycol) quenches the batch
  after next, held in T-304 (D-006). No salting-out correction by the glycol (coefficients 0, L-3). The heats of
  crystallisation and solution of BHET are not counted (no open value).

## D-008 Separations, drying and recovery (2026-11-19)

- F101 hot filter: all the non-PET solids with 0.5 kg of glycolysate per kg, to incineration.
- Centrifuges: C-202 0.6 kg of liquor per kg of crude cake (SRC-3 Example 2's residue holds about
  0.59), C-204 0.15 kg of water per kg of the needle crystals (as salicylic-acid-1's peeler
  centrifuge); all the crystals to the cake (ASSUMED).
- D201 dries to 0.2 wt% volatiles at 343.15 K and 10 kPa(a), well below BHET's melting point
  (382.65 K, SRC-7; SRC-2: 106 to 110 C); a horizontal paddle vacuum dryer at an ASSUMED 8 kg/m2h.
  After drying its jacket on cooling water cools the product and the dryer's metal to 313 K for
  packing (core's dryer `cooling`, Q12 14.0 kW; 313 K keeps a 15 K approach to the 298 K cooling
  water, so the product leaves at 313 K, not 303 K as first written); the next batch heats the
  metal from there. The dried BHET is 99.8 wt% (S22).
- X301, a packed dewatering column at atmospheric pressure, fed from T-301 with the first mother
  liquor, the dryer's condensate and R-101's heat-up distillate, takes 99.5 % of the water overhead
  with 0.2 % of the glycol (a specified split, ASSUMED; water and glycol boil 97 K apart); the
  BHET, oligomers, DEG and catalyst stay in the glycol bottoms. 95 % of the bottoms return to the
  charge and 95 % of the distillate to the redissolution (ASSUMED); the purges bound the DEG and
  the catalyst in the glycol loop and the glycol in the water loop.

## D-009 Utilities and heat (2026-11-19, revised 2026-11-20)

| stream | duty (kW, year average) | kWh/kg BHET | basis |
|---|---|---|---|
| Q1 R-101 heat-up of the dewatered charge to 470 K, HP steam | 137.7 | 0.218 | core's conversion duty |
| Q10 R-101 heat-up distillation of the water and reflux boil-up, HP steam | 88.9 | 0.141 | by hand: 49.8 kW for the water (IAPWS-95 enthalpies), 39.1 kW for an ASSUMED 500 kg/h boil-up over the 2 h hold (D-005) |
| Q11 R-101 overhead condenser E-101, cooling water | 89.5 | 0.142 | by hand: the distillate condensed to 313 K and the boil-up returned |
| Q2 quench V-201, LP steam | 130.9 | 0.207 | core's crystallizer duty with the inlets' own heat capacities (D-006, L-7) |
| Q3 first crop V-202, chilled water | 309.7 | 0.490 | core's crystallizer duty |
| Q4 redissolution V-203, LP steam | 249.4 | 0.395 | core's crystallizer duty |
| Q5 second crop V-203, chilled water | 354.1 | 0.561 | core's crystallizer duty |
| Q6 dryer D-201, LP steam | 122.7 | 0.194 | core's dryer model (reported, L-4) |
| Q12 product and dryer cooling to 313 K, cooling water | 14.0 | 0.022 | core's dryer cooling (reported, D-008) |
| Q7 dryer condenser E-201, cooling water | 62.8 | 0.099 | by hand (its source) |
| Q8 column reboiler C-301, HP steam | 4241.4 | 6.718 | by hand: Q9, the products from 290 K, a feed-bottoms interchanger, 5 % losses |
| Q9 column condenser, cooling water | 3901.0 | 6.179 | by hand: reflux ratio 0.5 (ASSUMED) |
| P1 to P6 drives | 37 | 0.059 | ASSUMED |

Steam heat is 7.9 kWh/kg BHET (HP 7.08, LP 0.80). The review of 2026-11-20 added the heat-up
distillation and reflux (Q10, Q11), corrected the quench (Q2 was 15.1 kW on one heat capacity) and
counted the product cooling (Q12): together 1.1 kWh/kg more than first written.
The column's reboiler is 85 % of the heat: 6.1 kg of water is distilled per kg of BHET, because
the redissolution needs 6 kg per kg and the quench reuses that water. This is SRC-1's finding for
its water-antisolvent case (the EG/water distillation the leading utility). Open options, not
modelled: mechanical vapour recompression or a two-effect column (the distillate is nearly pure
water), less redissolution water (SRC-3 allows 4), or SRC-1's crystallisation from the glycol
(D-001). Utility levels: HP steam 4100 kPa(a) (525 K) for R-101 at 470 K and the reboiler; LP
steam 350 kPa(a) (412 K); cooling water 298/308 K; chilled water 278/283 K from a refrigeration
unit outside the boundary.

## D-010 Wastes and emissions (2026-11-19)

To incineration: the hot-filter residue (0.006 kg/kg), the oligomer purge (0.026 kg/kg) and the
glycol residue purge (0.071 kg/kg, 89 % glycol with DEG, BHET and the zinc); to the wastewater
treatment: the distillate purge (0.306 kg/kg, water with about 0.04 wt% glycol). Vents of R-101's
nitrogen purge, the tanks and the dryer are not estimated (lca.yaml emission_exclusions). The
zinc leaves in the glycol purge, a little in the product and the oligomer purge; its fate in the
incinerator's ash is not followed.

## D-011 Thermal screening and hazards (2026-11-19, revised 2026-11-20)

`cheme process reactor-hazards`: R101 dT_ad 0.0 K (every heat ASSUMED 0), accumulation 0.839 (the
outlet's unconverted glycol, which has no exotherm to release), MTSR 470.1 K against an MTT of
470.31 K, the glycol's boiling point (`hazard.mtt`: R-101 runs at reflux; the default, water's
boiling point, does not apply, because the charge's water, 4.3 wt% and mostly from the wet
oligomer cake, is distilled off in the heat-up, D-005). The liquid R101 holds is glycol with
dissolved BHET and 0.27 mol % water; its bubble point at 101.325 kPa is 476.1 K by Raoult's law,
so the glycol's 470.31 K is the lower bound of the boiling barrier. No TD24 (open input), no criticality class. The screening finds no runaway
potential from the glycolysis itself; the hazards are the hot glycol at 470 K far above its flash
point (fire, nitrogen blanket as SRC-2), steam at 4100 kPa(a) on R-101's jacket, hot-surface and
burn hazards of the 470 K glycolysate during the hot filtration and the quench (a steam flash if
the glycolysate meets water too fast: the quench runs the glycolysate into the water, ASSUMED to
be controlled by rate), BHET dust in drying and packing, and zinc acetate's handling (an SDS
value, not read here). Relief of R-101 (fire case) and of the jacket is an open input.

## D-012 Preliminary gate-to-gate LCI (2026-11-19, revised 2026-11-20)

The inventory per kg of dried BHET (lca/inventory.csv) is written by `cheme assess lca --write`.
Two gap counts differ and are kept apart:
- **Core's own assessment** (`cheme assess lca`, lca/gaps.csv) has no background project here,
  so all 13 exchanges of the inventory are unmapped there and its result is no total (every
  climate contribution a gap).
- **The Atlas LCI** (scripts/build_lci.py) links seven of them: the fresh glycol to
  ethylene-glycol-1 and the make-up water to demineralised-water-1 (this folder's
  lca/mappings.yaml), both steam levels as heat delivered (kWh), and, through the shared
  lci/mappings.yaml, power (`electricity`), cooling water (`cooling-water`, a screening proxy)
  and the wastewater (`wastewater`, a proxy per kg). Six stay Atlas gaps: the washed flake
  (under the cut-off model the waste itself is burden-free; its collection, sorting, washing and
  grinding, which no library process makes, is the gap), zinc acetate, chilled water and the
  incineration of the three purges. The catalog marks the process preliminary.

## D-013 Dedicated train (2026-11-19)

One dedicated train (library ADR 0035): R-101, V-201, V-202, V-203, the centrifuges and D-201
work one batch each in turn, T-304 holds the second mother liquor for the batch after next, the
column C-301 runs continuously from the liquor tank T-301.
Cleaning between batches is not needed (the next batch takes up the residues); campaign
changeovers are outside the boundary.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| feeds for 5000 t/a, the charge, the catalyst and the water | done in cheme (four design specifications) | D-004, D-007, core ADR 0070 |
| four recycles | done in cheme (tears S19, S20, S21, S29) | D-006 to D-008, core ADR 0060 |
| heat-up distillation of the charge's water X101 | specified split (component separator), its bubble points by Raoult's law with package vapour pressures | D-005 |
| glycolysis R101 and its duty Q1 | done in cheme (conversion step), split and heats ASSUMED | D-005 |
| crystallizers CR201 to CR204 and Q2 to Q5 | done in cheme; imposed yields and BHET's water solubility; CR201's heat capacity and feed temperature from its inlets | D-006, D-007, core ADRs 0056, 0076 |
| dryer D201, its time and its cooling | done in cheme; duties Q6 and Q12 from core's report | D-008, L-4 |
| filters, centrifuges, column split | specified | D-008 |
| R-101's heat-up distillation and reflux Q10, Q11; condensers and column duties Q7 to Q9 | by hand, arithmetic in each source | D-005, D-009 |
| batch recipe, cycle, D-201 | done in cheme; R-101 and the crystallisers by hand | D-003 |
| thermal screening | done in cheme (screening values) | D-011 |
| LCI inventory | done; in the Atlas LCI seven exchanges linked, six gaps | D-012 |

## Core features used (core 1.13.0)

- A conversion step with five reactions, a `hazard.mtt` and its duty on `energy_port` (ADRs 0058,
  0059).
- `crystallizer:` with `basis: yield` and `basis: solubility` (one `value`, `salting_out`),
  spectators, a two-inlet quench and a reslurry redissolution, and `energy` with a
  `feed_temperature` (ADRs 0056, 0076); `solid_separation:`; `dryer:` with `energy`,
  `drying_rate`, `cake_density`, `pressure` and `cooling` (ADR 0076).
- `recovery:` component separators (the heat-up distillation, the column), four `specs:` (an annual target, three mass ratios across
  streams) with four `tears:` (ADRs 0060, 0070).
- `process/recipe.yaml` with `units` over several steps and the dryer's time `from:` its model
  (ADRs 0051, 0052, 0057); `lca.yaml` with waste `treatment`s and `emission_exclusions`.

## Core limits hit (each a candidate core issue)

- L-1: no model of a solid polymer dissolving and depolymerising: PET is a solid repeat unit
  converted in a conversion step at an imposed split; a batch rate law with `solids` (ADR 0074)
  would need kinetics no open source gives for this catalyst at reflux.
- L-2: a conversion step at reflux: `heat: reflux` (ADR 0074) is a batch reactor's; the
  conversion step counts the charge's heat-up, not what boils off in it (the charge's water) nor
  the boil-up through the reflux condenser. The water's removal is a component separator before
  R101 (X101), and its heat and the boil-up's are entered by hand (Q10, Q11; D-005).
- L-3: no solubility of BHET in water-glycol liquors: the first crop is an imposed yield and the
  glycol's effect on the second crop is not corrected (`salting_out` 0).
- L-4: core's dryer reports its duty (`cheme process crystallizers`) but does not write it on its
  energy stream: Q6 is entered as assumed with the report's value.
- L-5: core sizes no vessel from a conversion step or a crystallizer: R-101 and the crystallisers
  are sized by hand.
- L-6: the dewatering column is a specified split with its duty by hand; a continuous shortcut
  column (Fenske-Underwood-Gilliland with the reboiler and condenser duties) in `propagate` would
  calculate Q8 and Q9.
- L-7: a crystallizer with two inlets balances them at their mass-weighted mean temperature with
  one heat capacity, exact only for equal heat capacities: for the quench it gave 15.1 kW instead
  of 130.9 kW. Worked around by giving CR201 the inlets' heat-capacity-weighted mean
  (`feed_temperature`, `heat_capacity`, by hand from the stream table, D-006); per-inlet heat
  capacities in core would remove the hand step.

## Open inputs

Kinetics of the glycolysis with zinc acetate at reflux and the oligomer split at the end of the
batch; the heats of glycolysis and of BHET's crystallisation and solution; BHET's solubility in
water from 288 to 353 K and in water-glycol liquors; a TD24 of the glycolysate; the flake's
specification (moisture, PVC, dyes, additives) and their fate; the product specification for
polycondensation (colour, acid value, DEG, metals); the drying rate; the dewatering column's
stages, reflux and an MVR or multi-effect option; R-101's relief; prices and a TEA.
