# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
4-Aminophenol (p-aminophenol, PAP) by the hydrogenation of nitrobenzene in dilute sulfuric acid
with the Bamberger rearrangement in situ, issue ChemE-as-Code/process-library#506, a batch entry
of the library and the feed of paracetamol-1 (#481). Concept stage: design basis, batch recipe,
balanced BFD/PFD, thermal screening with a rate-constant sensitivity and a preliminary
gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` with the core pin 0e85885 (v1.12.0 with #254).
Templates: `oxalyl-chloride-1` (a batch entry with gas handling and stills) and the sibling
`paracetamol-1` (crystallisation, centrifuge and dryer on the same core). Library ADR 0035: one
dedicated train, campaigns out of scope (D-013). Requires cheme-as-code 1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (Google Patents machine text; PubChem PUG View; the values the `thermo` and
`chemicals` Python packages compute).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 3 383 416 A, R. G. Benner, filed 1965-07-08, granted 1968-05-14: Process for preparing aminophenol, https://patents.google.com/patent/US3383416A/en | description: nitrobenzene reduced with hydrogen at 60 to 120 C (preferably from 75 C) in 5 to 20 wt% (preferably 10 to 15 wt%) sulfuric acid, 1.0 to 5.0 (preferably 1.75 to 2.25) acid equivalents per mol, over Pt, Pd or both on carbon, with a water-soluble quaternary ammonium wetting agent (C10 to C18), atmospheric to 20 psig; at constant temperature and acid the rate rises with the hydrogen pressure and the yield falls with it; at constant pressure and acid the rate falls as the temperature rises and the yield rises with it (the temperature and pressure chosen for a reasonable yield in a reasonable time); the reduction is stopped with at least 5 % of the nitrobenzene left, whose layer keeps the catalyst suspended so that it is separated and reused (claims 1, 6, 8); agitation about 15 to 25 HP per 1000 gallons; thiophene-free nitrobenzene. Example 1(A): 271 g (2.2 mol) nitrobenzene, 205 g 98 % H2SO4, 1700 g water, 1.4 g 5 % Pt/C, 1.0 g dodecyltrimethylammonium chloride; 88 % reduced in about 5.5 h; 33 g nitrobenzene layer (12 %); 300 cm3 of water distilled, pH 6.0, aniline distilled; 8 g carbon, 5 min at 98 to 100 C, filtered; pH 7.2 with ammonia, cooled under nitrogen; 154 g PAP isolated, 99.1 %, 73 % on the nitrobenzene reacted; the filtrate held 12.5 g more by analysis (6 %, not isolated), a total yield of 79 %; 28 g aniline in the aniline distillate. Example 1(B): run to 100 %, 7.5 h, the catalyst then lost to the aqueous mass. Examples 2 to 4: the heel and the 300 g distillate recycled; Example 2 and the three reductions of Example 3 reuse Example 1's catalyst without fresh catalyst (five batches on one charge; Example 3: 73, 76 and 78 % isolated on new nitrobenzene charged), Example 4 adds 0.4 g fresh catalyst (74 % on new nitrobenzene charged). The reaction temperature of Example 1 and several figures are illegible in the machine text | read (Google Patents); patent, facts only | D-001, D-004 to D-008, D-012 |
| SRC-2 | US 4 307 249 A, E. L. Derrenbacker (Mallinckrodt), filed 1981-01-07, granted 1981-12-22: Process for the selective preparation of p-aminophenol from nitrobenzene, https://patents.google.com/patent/US4307249A/en | a water-soluble dimethylalkylamine oxide (C8 to C20, preferably mostly n-dodecyl) at 0.1 to 0.4 vol% of the aqueous medium instead of the quaternary ammonium chloride, whose chloride gives chloroanilines and whose isopropanol carrier isopropoxyanilines in the aniline co-product; background: the commercial process in 10 to 13 % sulfuric acid, stopped before all the nitrobenzene is used, the aqueous layer decanted and PAP precipitated by neutralisation. Example 1: 650 mL water, 0.25 g 3 % Pt/C, 2 mL surfactant solution (30 to 35 %); heated to 70 C under hydrogen, 110 g 95 to 98 % H2SO4 added, the temperature rising to 90 to 95 C; 185 g nitrobenzene; hydrogen at about 10 in. of water gauge, 7 h at 85 C; nitrogen purge, phases separated below 60 C; neutralised to pH 7 to 8 with ammonium hydroxide at 4 C, stirred 1 h at 5 to 10 C. Runs 1 to 4: 57.1 to 75.2 % conversion, 83 to 102 mg/mL PAP in the aqueous phase, PAP/aniline 4.1 to 4.5 (Table 2; the ratio's basis, mass or moles, is not stated) | read (Google Patents); patent, facts only | D-001, D-004, D-005, D-009 |
| SRC-3 | US 3 953 509 A, N. P. Greco (Koppers), priority 1972-10-10, granted 1976-04-27: Hydrogenation of nitrobenzene to p-aminophenol, https://patents.google.com/patent/US3953509A/en | sulfided catalysts (MoS3/C, PtS/C) in sulfuric acid at 135 to 155 C and 200 to 500 psi, to complete conversion without a nitrobenzene recovery; the rearrangement of the hydroxylamine is faster at the higher temperature, else aniline forms; Pt catalysts over-hydrogenate PAP and must be stopped early. Example 3: 160 g nitrobenzene, 275 g H2SO4, 450 g water, MoS3/C, 155 C, 300 psi, 11 h; 65.6 % PAP plus 13 % crude, 22 % aniline. Example 19: 300 g nitrobenzene, 300 g 96 % H2SO4, 300 g water, 2 g 5 % PtS/C, 132 to 135 C, 200 to 500 psi, 18 h; 78 % crude PAP, 7.5 % aniline | read (Google Patents); patent, facts only | D-001 (rejected alternative) |
| SRC-4 | PubChem CID 403 (4-aminophenol), PUG View "Solubility" | solubility in water 0.39 % at 0 C, 0.65 % at 24 C, 0.80 % at 30 C (HSDB citing The Merck Index); 1.6 g/L at 20 C (citing Yalkowsky and He); identity (InChIKey, ChEBI) | read (PUG REST); facts only | D-008, registry |
| SRC-10 | The Merck Index's entry for p-aminophenol as reproduced by DrugFuture's Chemical Index Database, https://www.drugfuture.com/chemdata/p-Aminophenol.html | solubility in water 0.39 % at 13 C, 0.65 % at 24, 0.80 % at 30, 1.5 % at 50, 4.7 % at 80 and 8.5 % at 96 C (the lowest point at 13 C here, at 0 C in SRC-4's HSDB text; the crystallisation keeps SRC-4's 0 C, the higher loss) | read 2026-11-19 (a website's reproduction of a licensed handbook); single facts only | D-008 |
| SRC-5 | PubChem CIDs 7416 (nitrobenzene) and 6115 (aniline), PUG View "Solubility" | nitrobenzene in water 0.19 % at 20 C and 0.8 % at 80 C (HSDB citing Kirk-Othmer); aniline 3.5 parts per 100 parts water at 25 C and 6.4 at 90 C (HSDB citing Kirk-Othmer) | read (PUG REST); facts only | D-006, D-007, D-008 |
| SRC-6 | PubChem CID 6097028 (ammonium sulfate), PUG View "Solubility" | 70.6 g per 100 g water at 0 C, 76.7 at 25 C (HSDB citing The Merck Index) | read (PUG REST); facts only | D-008 |
| SRC-7 | The `thermo` 0.6.1 and `chemicals` 1.5.2 packages (core's environment) | formation enthalpies (J/mol): nitrobenzene(l) 12500 and aniline(l) 31600 (CRC), 4-aminophenol(s) -192814.5 (WEBBOOK method), water(l) -285825 (ATCT_L), sulfuric acid(l) -814000 (CRC), ammonia(g) -45558 (ATCT_G), ammonium sulfate(s) -1180900 (CRC); liquid densities and heat capacities, normal boiling points, heats of vaporization and the vapour pressures of nitrobenzene (2.814 kPa, VDI_PPDS), aniline (6.108 kPa, WAGNER_MCGARRY) and water (101.42 kPa, IAPWS) at 373.15 K, each with its method named in materials.yaml: HEOS/HEOS_FIT (fits to the reference Helmholtz equations of state), DADGOSTAR_SHAW and LASTOVKA_S (estimation methods from the molecular structure), ZABRANSKY_SPLINE_C (Zabransky, Ruzicka, Majer and Domalski's review of liquid heat capacities), PERRY151 (a table of Perry's Chemical Engineers' Handbook, 8th ed.), CRC_ORG, CRC_INORG_L_CONST, CRC_INORG_S and the CRC formation enthalpies (the CRC Handbook of Chemistry and Physics), VDI_PPDS (the VDI Heat Atlas, 2nd ed.), WAGNER_MCGARRY (McGarry's Wagner-equation coefficients), WEBBOOK and ATCT (the NIST Chemistry WebBook and the Active Thermochemical Tables) | open-source packages queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). The coefficients come from the tables packaged in `thermo` and `chemicals`; the underlying works (the CRC Handbook, Perry's Handbook, the VDI Heat Atlas, Zabransky et al., McGarry) were not read here | materials, reactions, D-005, D-007, D-009 |
| SRC-8 | processes/hydrogen-1, sulfuric-acid-1, ammonia-1, asu-1, aniline-1, paracetamol-1 (this library) | hydrogen 99.9 mol%; sulfuric acid 98.5 wt%; anhydrous ammonia; gaseous nitrogen; aniline-1 also buys nitrobenzene; paracetamol-1 buys 4-aminophenol | library, internal | D-004, D-012 |
| SRC-9 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and the criticality classes of a semi-batch (method, implemented in core ADR 0050) | method reference, no data taken | D-011 |

Searched and not found openly (2026-11-19): kinetics or calorimetry of the three-phase
hydrogenation or of the Bamberger rearrangement in this medium, a TD24 of the reaction mass or of
N-phenylhydroxylamine, the solubility of 4-aminophenol in ammonium sulfate liquor or in sulfuric
acid (a J. Chem. Eng. Data paper on PAP in sulfuric acid and water exists and was not read), a
plant's specific consumptions, catalyst losses and prices.

## D-001 Route and boundary (2026-11-19)
Decision: the Pt/C hydrogenation of nitrobenzene in dilute sulfuric acid with a surfactant, at
358 K and near atmospheric pressure, stopped at 0.88 conversion so that the nitrobenzene layer
keeps the catalyst for the next batch (SRC-1, SRC-2), as a batch plant on one dedicated train:
- R-101: charge on the heel (M101), hydrogen dosed (R101: HYDP to 4-aminophenol via the
  hydroxylamine and its rearrangement, HYDA to aniline), purged, cooled to 333 K, settled and
  decanted (V101);
- R-102: strip of 15 % of the aqueous layer with its dissolved nitrobenzene, back to the next
  charge (ST101), neutralisation with ammonia (N101);
- R-103: the aniline distilled with water at pH about 6 while process water is fed at constant
  level (ST102), separated in V-102 into crude aniline (a co-product) and aniline-saturated
  water back to the next charge; carbon treatment and hot filtration (F-101);
- K-101, C-101, D-101: ammonia to pH 7.2 and cooling crystallisation at 283 K (CR101), the
  crystals washed with cold water on the centrifuge (W101) and vacuum-dried (D101); the
  ammonium sulfate liquor collected (M103).
Boundary: gate to gate, from the feeds at the battery limit to the dried product to packing,
the crude aniline to an aniline purification and the ammonium sulfate liquor to its recovery
(D-008), all outside.

Rejected alternatives:
- the sulfided-catalyst route of SRC-3 (MoS3/C or PtS/C at 132 to 155 C and 1.4 to 3.4 MPa):
  complete conversion and no heel, but a pressure autoclave, longer batches (11 to 18 h) and
  more aniline with MoS3 (22 %); the issue's sources run the Pt/C route at low pressure in
  batch, which is also what the paracetamol producers of SRC-2 describe;
- the reduction of 4-nitrophenol (from 4-nitrochlorobenzene) with hydrogen or iron: a longer
  chain from chlorobenzene and a chloride waste; no open source read for it here;
- a continuous hydrogenation: the sources describe batches stopped at a set conversion, with
  the catalyst carried in the heel; a continuous three-phase reactor with catalyst separation
  has no open basis.
Assumes: the overall reactions lump the hydroxylamine (L-2); no other by-products (the
4,4'-diaminodiphenyl ether and other impurities are not modelled).

## D-002 Capacity, product and operating hours (2026-11-19)
1000 t/a of dried 4-aminophenol (ASSUMED: a dedicated batch train of fine-chemical size; the
paracetamol-1 train needs about 1750 t/a, so it is fed by more than one such train or a larger
one; the LCI per kg does not depend on it). 7920 h/a (330 days, ASSUMED). The spec CAP of the
flowsheet varies the fresh nitrobenzene, with the other charge feeds in fixed ratios to it, until
the dried product S26 makes 1000 t/a in 7920 h. Product: technical 4-aminophenol for
paracetamol, modelled 99.6 wt% with 0.20 wt% ammonium sulfate and 0.2 wt% water (SRC-1: 99.1 %).

## D-003 Batch basis, recipe and vessels (2026-11-19)
The recipe (process/recipe.yaml) makes 1209.4 kg per batch; R-101 is the bottleneck at a
9.578 h cycle (1.5 h charge, 5.5 h hydrogen dosing from R101's model, 0.25 h purge, 1.33 h
cool-down from 358 to 333 K on the jacket, timed by core from the mass, the metal and the
jacket, 0.5 h settling, 0.5 h decant), 826.9 batches a year. R-102 (heat-up 1.8 h, strip 3.6 h
at 390 kW from ST101's model, neutralisation 2.1 h, 8.6 h), R-103 (heat-up 0.4 h, aniline
distillation 5.7 h at 600 kW from ST102's model, carbon and hot filtration, 7.9 h), K-101
(7.8 h), C-101 (4 h) and D-101 (6.8 h, 5.3 h of drying from D101's rate) each take a batch
within the cycle. Timed by hand in scripts/balance.py, because core times no still's heat-up
with constant volatilities and no crystalliser (L-4, L-5): R-102's heat-up (Q11, about 710 kWh
a batch, at the 390 kW boil-up), R-103's (its jacket's share of Q13, about 220 kWh, at 600 kW),
the neutralisation (Q4 and Q17, about 990 kWh a batch, on R-102's jacket on cooling water:
U 300 W/(m2 K) x 25 m2 x 65 K = 487 kW, 2.04 h, taken as 2.1 h) and K-101's cool-down (Q7 and
Q16, 1298 kWh a batch, from 371 to 283 K on chilled water at 278 K through about 32 m2 of jacket
and coil at U 300 W/(m2 K): 4.5 h, taken as 5 h). The recipe sizes R-101 at 25 m3 (15.2 m3 of
batch, 75 % fill at most for the gas hold-up), R-102 at 25 m3 (15.1 m3), R-103 at 25 m3 (18.6 m3
at its fullest with the water fed) and D-101 at 3.15 m3 (core ADRs 0052, 0057) and checks
R-101's jacket (peak 350 kW against 451 kW at the charge's 27.4 m2 on cooling water). The
flowsheet's flows are the recipe's year averages (no cheme.recipe-basis finding). Every
duration not from a model or the hand checks is ASSUMED.

## D-004 Feeds and the charge (2026-11-19)
Per kg of nitrobenzene charged (SRC-1 Example 1(A)): 6.27 kg of water (spec WAT: the make-up S1
is what the recycled distillates S21 and S22 leave) and 0.741 kg of H2SO4 as 98 wt% acid (1.86
equivalents per mol, inside SRC-1's 1.75 to 2.25; 10.6 wt% acid in the water, inside 10 to 15
wt%). The fresh nitrobenzene (1.415 kg/kg product) is set by the spec CAP; the 98 % acid (0.858
kg per kg of fresh nitrobenzene), the ammonia (2 mol per mol of acid, 0.292 kg/kg) and the cake
wash (0.73 kg/kg) follow it in fixed ratios. Hydrogen: the spec CONV doses what reduces 0.88 of
the nitrobenzene charged (2.17 mol per mol reduced), 0.0502 kg/kg product. Process water fed to
R-103 during the aniline distillation (S29, spec ANL, D-007). Catalyst: 5 % Pt/C, SRC-1's
make-up of 0.4 g per 5 batches on about 246 g of fresh nitrobenzene, 0.557 kg per batch; the
heel keeps the rest (lca/lca.yaml consumable). Surfactant: the amine oxide of SRC-2 (no
chloride, so no chloroanilines in the aniline), about 1 g of active per kg of water, ASSUMED
70 % returned with the recycled water: 3.7 kg per batch (consumable). Feeds at 298 K.

## D-005 Reactor R101: semi-batch, kinetics and heats (2026-11-19)
R101 is a semi-batch (`reactor: semibatch`): the charge at 358.15 K (SRC-2: 85 C), hydrogen dosed
at a constant rate over 5.5 h (SRC-1: 88 % in about 5.5 h) and taken up (`absorbed: 1.0`), the
batch ending with the dose. In the plant hydrogen is fed on demand at a constant pressure,
103.8 kPa(a) (SRC-2's 10 in. water gauge); the model's constant dose is the dosing-controlled
limit. The rate laws are ASSUMED (no open kinetics): both first order in nitrobenzene and in
dissolved hydrogen, k = 0.042 and 0.008 m3/(kmol s) at 358.15 K with one activation energy of
40 kJ/mol, so that 0.84 of the nitrobenzene goes to 4-aminophenol and 0.16 to aniline at any
temperature (SRC-1 Example 1(A): 28 g of aniline, 0.301 mol on the 1.936 mol reduced, 15.5 %,
the rest taken as 4-aminophenol; SRC-2's PAP/aniline of 4.1 to 4.5, its basis not stated, is
about 3.5 to 3.8 by moles if it is by mass (ASSUMED), a little more aniline either way). They
are fast enough that the hydrogen is used as it is dosed: at most 0.37 % of the dosed hydrogen
accumulates (cheme process reactor-hazards).
The rest of the reduced nitrobenzene: SRC-1 accounts for 79 % as 4-aminophenol (73 % isolated,
6 % found in the filtrate) and 15.5 % as aniline, about 94.5 %; the other 5.5 % (by-products
such as the 4-aminocyclohexanol SRC-1 names, tars and losses) is not modelled and is taken as
4-aminophenol here, an upper bound (D-008 compares the yield).
Temperature: SRC-1 states that at constant pressure the rate of reduction falls as the
temperature rises (and the yield rises). The model's positive activation energy deliberately
departs from that statement: near atmospheric total pressure the water's vapour pressure over
the mass rises with the temperature (about 58 of the 104 kPa(a) at 358 K) and lowers the
hydrogen's partial pressure, which SRC-1 also states sets the rate, so the observed fall need
not mean a falling intrinsic rate; a rate that rises with the temperature is the conservative
choice for a temperature excursion with hydrogen on demand (D-011 (a)). The k/10 and k/100 cases
of D-011 cover a slower intrinsic rate at the process temperature. Calorimetry with the
hydrogen uptake replaces it (open input). The single liquid phase lumps the nitrobenzene layer, the aqueous acid and the
catalyst (L-1). Heats of reaction from SRC-7, hydrogen as a gas (core ADR 0054), 4-aminophenol
as the solid: HYDP -491.1 kJ/mol, HYDA -552.6 kJ/mol; the heats of solution and protonation are
not counted. R101's duty, 200.4 kW year average (Q2 to cooling water), is the model's: the heats
of reaction and the dosed hydrogen warmed to 358 K.

## D-006 Phase split V101 and the heel (2026-11-19)
After the dose the mass is purged with nitrogen, cooled on R-101's jacket from 358 to 333 K
(Q10, 46.9 kW year average with the vessel's metal, D-009) and settled (SRC-2: below 60 C). The
aqueous layer takes the acid, the 4-aminophenol, the aniline (as its sulfate) and 0.4 of the
nitrobenzene reaching the split, 0.75 wt% of its water (SRC-5: 0.19 wt% at 20 C and 0.8 wt% at
80 C, about 0.6 at 60 C: the rest taken as droplets carried over, ASSUMED); the other 0.6
(14.6 kg/h, about 7 % of the nitrobenzene charged; SRC-1 kept 12 % with the dissolved part in
it) stays in R-101 as the heel with the catalyst (tear S20). The dissolved hydrogen goes to the
vent with the nitrogen (S8, 0.18 g per kg). No heel purge is modelled: the catalyst's poisons and the heel's impurities need
one in the plant (open input).

## D-007 Strip ST101, neutralisation N101 and aniline still ST102 (2026-11-19)
- ST101: R-102 heats the layer from 333 K to the boil (Q11) and boils off 15 % of it by mass
  (SRC-1: 300 cm3 of about 1.9 kg), which takes 99.1 % of the dissolved nitrobenzene back to the
  next charge (tear S21). The aniline is a sulfate in the acid and stays (non-volatile,
  ASSUMED).
- N101: ammonia, 2 mol per mol of the acid fed, sparged into R-102 and taken up to 0.999 (a
  conversion step, NEU: H2SO4 + 2 NH3 -> (NH4)2SO4). Its heat is that of the dilute acid:
  -275.8 kJ/mol from the formation enthalpies of the pure liquid acid (SRC-7), less the acid's
  heat of dilution, 59.2 kJ/mol, which the charge already released (Q1, D-009), -216.6 kJ/mol;
  with the liquor cooled from 373 to 363 K, 100.4 kW year average (Q4), and R-102's metal (Q17),
  to cooling water on R-102's jacket (2.1 h, D-003). SRC-1 adjusts to pH 6.0 before the aniline
  distillation and to 7.2 after the hot filtration; the model neutralises all of the acid in
  one step (L-3), while the plant doses the ammonia in those two steps (R-102 and K-101, the
  recipe), so that the hot liquor stays at pH 6 as SRC-1's does (D-008).
- ST102: R-103 heats the liquor from 363 K to the boil (Q13) and distils the aniline with water
  while process water (S29, 4.49 kg per kg of product, preheated to 363 K in E-105 on LP steam)
  is fed as fast as the still boils (core's still feed, `constant_level`), until 0.0005 mole
  fraction of aniline is left (spec ANL; ASSUMED: SRC-1 does not say how far), 5.7 h at 600 kW
  (R-103's jacket and an internal coil, ASSUMED). The water fed keeps the liquor's water, so the
  4-aminophenol stays at about SRC-1's concentration (D-008); boiling the liquor down instead, as
  the first version of this entry did, took off about half its water.
- Both stills use constant relative volatilities to water (core's batch still, `volatility:
  constant`), estimated for a solute dilute in water as alpha = gamma_inf x Psat / Psat(water)
  at 373.15 K with gamma_inf taken as 1/x at saturation (SRC-5, SRC-7): nitrobenzene 23.5,
  aniline 4.92 (ASSUMED). Core's Raoult's-law still would make both less volatile than water;
  the immiscible pairs boil as heteroazeotropes, which core does not model (L-4).
- Boil-up 390 kW in R-102: U 400 W/(m2 K) (glass-lined, ASSUMED) x about 25 m2 wetted x
  (412 - 373) K; 600 kW in R-103 with a coil of about 13.5 m2 added; checked by hand, core
  checks no still's jacket (L-4). The duties Q3, Q5 and the condensers' Q3C, Q6 are the stills'
  models (the vapour's latent heat only); the heat-ups (Q11, Q13) and the distillates' cooling
  (Q12 to 313 K for T-101, Q14 to 298 K for V-102) are added in scripts/balance.py (D-009).

## D-008 Separations, crystallisation, wash, drying and the liquors (2026-11-19)
- V102: the distillate cooled to 298 K separates into crude aniline and water. Recoveries
  (ASSUMED): 0.535 of the aniline and 0.0022 of the water to the aniline layer, so that the
  water layer leaves with 3.5 parts of aniline per 100 parts of water (SRC-5's saturation at
  25 C) at the converged recycle; the crude aniline holds 6.1 wt% water (the water's
  solubility in aniline not sourced, ASSUMED) and the nitrobenzene traces. The water layer goes
  back to the next charge (tear S22), where its aniline is inert.
- The hot liquor: R-103's water feed keeps the liquor at 0.124 kg of 4-aminophenol per kg of
  water (S13), about SRC-1's own (about 167 g of 4-aminophenol in about 1.4 kg of water after its
  300 cm3 strip, 0.12 kg/kg), which SRC-1 carbon-treats at 98 to 100 C and filters hot at pH 6.0
  without a loss stated. Pure water dissolves only 8.5 wt% at 96 C, 0.093 kg/kg (SRC-10), so the
  liquor must stay at pH 6 (part of the 4-aminophenol as its sulfate) until it is filtered, as
  SRC-1 does: the ammonia to pH 7.2 is added in K-101 after F-101 (recipe). The solubility of
  4-aminophenol in this liquor at pH 6 and 371 K is not sourced (open input).
- Carbon treatment: SRC-1's 8 g per 154 g of isolated product at 98 to 100 C, filtered hot
  through F-101; 8 / 154 x 1209.4 kg = 62.83 kg per batch, to incineration (lca/lca.yaml
  consumable); not in the balance.
- CR101: cooling crystallisation at 283.15 K (SRC-2: 5 to 10 C) from the solubility of
  4-aminophenol in water (SRC-4, three points from 273 to 303 K, interpolated; SRC-10 puts the
  lowest at 13 C, which would give a lower loss); the ammonium sulfate (0.19 kg per kg of
  water, below its solubility of 0.706 at 0 C, SRC-6), aniline and other solutes are spectators
  with no salting-out (ASSUMED: no open data; ammonium sulfate is likely to salt the
  4-aminophenol out, so the loss to the mother liquor is overstated). The slurry is centrifuged
  in the crystallizer's separation (99.5 % of the crystals to the cake, 0.12 kg of liquor per
  kg of crystals, ASSUMED). The mother liquor keeps 6.0 kg/h of 4-aminophenol, 4.5 % of it
  (SRC-1 found 7.5 % of its total in the filtrate).
- No second crop. The first version of this entry concentrated the mother liquor under vacuum
  for a second crop, reading SRC-1's 6 % as recovered; SRC-1 only found it in the filtrate by
  analysis and isolated no second crop. A second crop would recover little (the mother liquor
  is at saturation) for an evaporation of about 0.4 of its water whose vapour at 283 K could
  not be condensed on the chilled water: rejected.
- W101: the crop reslurried on the centrifuge with 0.73 kg of cold water per kg of fresh
  nitrobenzene (about 0.9 kg per kg of cake) at 283 K and spun to 0.12 kg per kg (ASSUMED); the
  wash dissolves 0.5 % of the product and 0.5 % passes the centrifuge.
- D101: vacuum drying at 333 K under nitrogen to 0.2 wt% volatiles (ASSUMED; 4-aminophenol
  darkens in air), mean rate 4 kg/(m2 h), 70 % efficiency, the dryer's metal heated each batch
  (core's dryer model; its duty Q9 from cheme process crystallizers); the vapour condensed in
  E-103 on cooling water at about 313 K (Q15), the dryer under about 10 kPa(a) (ASSUMED).
- Result: 99.6 wt% product; 79.4 % of the fresh nitrobenzene as dried 4-aminophenol. SRC-1
  isolated 73 % on the nitrobenzene reacted in Example 1(A) (79 % with the 6 % left in the
  filtrate) and 73 to 78 % on new nitrobenzene with the heel and the distillate recycled
  (Examples 3, 4). The model is 1.4 to 6.4 points above the isolated yields, because it takes
  the 5.5 % of the reduced nitrobenzene that SRC-1 does not account for as 4-aminophenol (D-005):
  an upper bound; the nitrobenzene per kg (1.415 kg) may be up to about 9 % low against the
  source's lowest isolated yield.
- The ammonium sulfate liquor (11.2 kg/kg: 14.3 wt% ammonium sulfate, 0.5 wt% 4-aminophenol,
  0.2 wt% aniline; 42.8 kg/h of ammonium nitrogen) is not fit for a site biological plant
  without nitrogen removal (processes/utility-wwtp leaves nitrogen removal out of its scope).
  ASSUMED route, as acrylonitrile-1's quench liquor: an
  ammonium sulfate recovery by evaporative crystallisation outside the boundary (fertiliser
  grade), its condensate to biological treatment and its organic purge to incineration; the
  recovery's evaporation (about 0.85 kg of water per kg of liquor) belongs to that treatment's
  inventory (lca/lca.yaml product:WW). The liquor is about SRC-1's own water per kg of product,
  as its liquor is not boiled down (above).

## D-009 Utilities and heat: every energy flow (2026-11-19)
Utilities (ASSUMED): LP steam 350 kPa(a), 412 K; cooling water 298/308 K; chilled water
278/283 K; electricity. Every heat flow of the batch is on an energy stream, year averages over
the 9.578 h cycle; the models' duties from core, the heats they leave out from
scripts/balance.py at the liquid heat capacities of materials.yaml (ideal mixing) and the
vessels' metal (recipe.yaml; K-101's 5100 kJ/K, ASSUMED):
- Q1 (73.9 kW, LP steam): the charge heated to 358.15 K: the inlets S1, S2, S3, S22 from
  298.15 K, the heel S20 from 333.15 K and the distillate S21 from 313.15 K, 93.3 kW, and R-101's
  metal back from 333 K, 5.8 kW, less the acid's heat of dilution, 59.2 kJ per mol of H2SO4,
  25.2 kW. The 59.2 kJ/mol is derived from SRC-2 Example 1's rise from 70 to 92.5 C when 110 g
  of 96.5 % acid enters 650 g of water: (650 x 4.202 + 110 x 1.073) J/K x 22.5 K / 1.0827 mol, a
  lower bound (heat losses and the vessel not counted; ASSUMED). The same heat is taken off
  NEU's heat of reaction, which the formation enthalpies give for the pure acid (D-007), so it
  is counted once.
- Q2 (200.4 kW, cooling water): R101's model (core's semi-batch).
- Q10 (46.9 kW, cooling water): R-101's mass and metal cooled from 358 to 333 K for the
  settling (cheme process recipe's cool-down gives the same).
- Q3 (148.7 kW, LP steam) and Q3C (the same, cooling water): ST101's model; Q11 (74.1 kW, LP
  steam): the layer and R-102's metal heated from 333 K to the boil; Q12 (16.7 kW, cooling
  water): the distillate S21 subcooled in E-102 to 313 K.
- Q4 (100.4 kW, cooling water): N101's conversion model; Q17 (2.2 kW): R-102's metal from 373
  to 363 K with the liquor.
- Q5 (355.9 kW, LP steam) and Q6 (the same, cooling water): ST102's model; Q13 (65.7 kW, LP
  steam): the water fed warmed from 298 to 363 K in E-105 (43.0 kW) and the liquor, the water
  fed and R-103's metal to the boil (22.8 kW); Q14 (50.5 kW, cooling water): the distillate S12
  cooled to 298 K for V-102.
- Q7 (122.5 kW, chilled water): CR101's lumped duty, 3.547 kJ/(kg K) from 371 to 283 K (S13's
  heat capacity from materials.yaml, ASSUMED constant); Q16 (13.0 kW): K-101's metal. All of it
  on chilled water; a first stage on cooling water down to about 313 K would move about two
  thirds of it off the refrigeration (a basic-engineering option, not modelled).
- Q9 (22.2 kW, LP steam): D101's dryer model; Q15 (9.8 kW, cooling water): its vapour condensed
  in E-103.
- Power (60.3 kW): R-101's gas-inducing agitator at SRC-1's lower end, 15 HP per 1000 US
  gallons (2.95 kW/m3), on the 15.24 m3 batch, 45.0 kW while it runs (charge, dose, purge and
  cool-down, 8.58 h of the cycle), 40.3 kW year average (P1); R-102's, R-103's and K-101's
  agitators 3, 3 and 2 kW, C-101 8 kW, the dryer's agitator and vacuum pump 4 kW (ASSUMED).
- Not counted: heat losses of the vessels and lines, and the vessels' cooling between batches
  to the ambient (R-102 and R-103 receive their next charge cooler than they ended); the
  pumps.
Per kg of product (unallocated): LP steam 5.86 kWh, cooling water 7.38 kWh, chilled water 1.07
kWh, electricity 0.478 kWh.

## D-010 Recycles and design specifications (2026-11-19)
Three recycles are converged at the tears S20 (heel), S21 (strip distillate) and S22 (aniline
water) by Broyden (core ADR 0060), with four design specifications solved together (ADR 0070):
CAP (S2 for 1000 t/a of S26), WAT (S1 for 6.27 kg of water per kg of nitrobenzene in S4), CONV
(S5 for 0.12 kg of nitrobenzene left per kg charged) and ANL (S29, the water fed to R-103, for
0.0005 mole fraction of aniline left in S13).

## D-011 Thermal screening and the release cases (2026-11-19)
`cheme process reactor-hazards` on R101 (method of SRC-9): T_p 358.15 K; dT_ad 129.7 K (HYDP
over the charge's nitrobenzene); accumulation of the dosed hydrogen at most 0.37 % (at the end of
the dose); MTSR 358.6 K against an MTT of 373.12 K (water's normal boiling point at about
atmospheric pressure; the acid raises the bubble point a little); no criticality class without
a TD24 (no calorimetry). Sensitivity (the rate constants divided, the flows kept; run on a copy
and not committed): k/10 2.8 % and 361.8 K; k/100 14 % and 376.5 K, above the MTT: a design
finding.
What the screening does not cover, and the cases for basic engineering (each reasoned, none
quantified by core):
- (a) Hydrogen on demand: in the plant hydrogen is fed at constant pressure, not dosed, so a
  cooling failure with the hydrogen still open lets the whole charge react: up to 129.7 K of
  adiabatic rise from 358 K, far above the MTT. Required: hydrogen supply shut off on high
  temperature, loss of agitation (no gas induction, no reaction) and loss of cooling water, by an
  independent trip; R-101's relief sized for the boiling mass with hydrogen; the agitator as the
  rate-limiting element (stopping it stops the reaction).
- (b) Accumulated N-phenylhydroxylamine: the model lumps it (L-2). If the rearrangement is slow
  (low acid, low temperature) the hydroxylamine builds up and can decompose exothermically; the
  rearrangement itself releases heat later. Calorimetry of the mass is required (DSC/ARC: TD24 of
  the mass and of the hydroxylamine).
- (c) Hydrogen in the head space: R-101 is purged with nitrogen before and after the hydrogen and
  vented to a stack; oxygen ingress during charging of a vessel holding a dry or nitrobenzene-wet
  Pt/C catalyst is a fire risk (SRC-1 names the pyrophoric catalyst); the heel keeps it wet.
- (d) The dissolved hydrogen the model releases on a cooling failure (0.22 kg per batch; 8.5 kg at
  k/100) is a model artefact of a homogeneous liquid: in the plant the hydrogen is in the head
  space, about 10 m3 at 104 kPa(a) less the water's vapour pressure (about 58 kPa at 358 K), some
  0.3 kg, purged to the stack with the nitrogen (the vent S8 carries the model's 0.22 kg); R-101
  is vented to the stack without a condenser of its own, and the vent's capacity is a
  basic-engineering item.
- (e) Ammonia into the hot liquor (N101) is exothermic but dosed and self-limiting (cheme screens
  no conversion step).

## D-012 Preliminary gate-to-gate LCI (2026-11-19)
`cheme assess lca --write` from the flowsheet's year averages per kg of dried 4-aminophenol, with
per-batch consumables (core ADR 0053): activated carbon 62.83 kg (to incineration), Pt/C make-up
0.557 kg, amine oxide 3.7 kg and nitrogen 80 kg per batch (ASSUMED: R-101's head space of about
10 m3 purged six times, and the dryer's breaks). Linked to library producers (lca/mappings.yaml):
sulfuric acid to sulfuric-acid-1 (98.5 wt%, by mass of acid), hydrogen to hydrogen-1 (pinned by
dataset, since the slug alone picks the first producer), ammonia to ammonia-1, nitrogen to asu-1,
LP steam as heat delivered. Gaps: nitrobenzene (no library producer; a nitration process of
benzene would close it), process water, power, cooling and chilled water, the ammonium sulfate
liquor's recovery (D-008), the carbon and its incineration, the catalyst and the surfactant.
Allocation: mass between the 4-aminophenol and the crude aniline (0.863 / 0.137), an agent proposal for the LCA
practitioner (the conservative bound: all to the 4-aminophenol). The hydrogen vented is an
emission to air (0.18 g/kg, a gap); vent and breathing losses of nitrobenzene and aniline are
declared exclusions. paracetamol-1 can now link its 4-aminophenol feed to this entry's product
`product:PAPP` (its own mappings, its own PR).

## D-013 Dedicated train (2026-11-19)
Library ADR 0035: the train (R-101, R-102, R-103, K-101, C-101, D-101 and their tanks)
makes only 4-aminophenol, batch after batch. A plant that also makes other aminophenols or
reductions on the same vessels is described as if dedicated; campaigns and changeovers are out
of scope.

## Method and dependency table

| result | method | inputs |
|---|---|---|
| feeds, charge | design specifications CAP, WAT, CONV, ANL (core ADR 0070) | SRC-1 ratios, D-002, D-004, D-007 |
| R101 | semi-batch with a dosed gas (core ADRs 0050, 0054, 0063) | ASSUMED rate laws (D-005), SRC-7 heats |
| V101, V102 | component separators (ADR 0070) | SRC-5 solubilities (D-006, D-008) |
| ST101, ST102 | batch stills, constant volatility (ADR 0055) | SRC-5, SRC-7 (D-007) |
| N101 | conversion step | SRC-7 (D-007) |
| CR101, W101 | crystallizers with spectators (ADR 0056) | SRC-4, SRC-10 (D-008) |
| D101 | dryer (ADR 0057) | ASSUMED rate and efficiency (D-008, D-009) |
| Q1, Q10 to Q17, P1; heat-up, neutralisation and K-101 times | scripts/balance.py (library ADR 0027) | materials.yaml heat capacities, recipe metals, SRC-1 agitation (D-003, D-009) |
| tears S20, S21, S22 | Broyden (ADR 0060) | D-010 |
| recipe, vessels | batch recipe (ADRs 0051, 0052, 0057) | D-003 |
| screening | reactor-hazards (ADRs 0058, 0069) | D-011 |
| LCI | assess lca (ADR 0053) | D-012 |

## Core features used (core 1.12.0)
`reactor: semibatch` with a dosed gas taken up and the thermal screening; component separators
(`recovery:`); batch stills with constant volatility and a condenser port, one with a feed at
constant level; a conversion step with its duty; a crystallizer with spectators and its own
separation, and a reslurry wash; the dryer; three tears with Broyden; four design
specifications with `with:` ratios; the batch recipe with its vessels, jacket check and a
jacket-timed cool-down; per-batch LCA consumables.

## Core limits hit (each a candidate core issue)
- L-1: the semi-batch is one liquid phase: the nitrobenzene layer, the aqueous acid and the
  suspended catalyst are lumped, so the concentrations and the volume are those of a homogeneous
  liquid, and the gas-liquid mass transfer that sets the real rate (the agitator's gas induction)
  is not modelled.
- L-2: no intermediate in the screening's sense: the hydroxylamine could be carried as a
  component with consecutive reactions (ADR 0069's network potential), but without kinetics of
  the rearrangement the model would only restate an assumption; the screening counts its heat
  in HYDP.
- L-3: no electrolyte speciation: the pH steps of SRC-1 (6.0 and 7.2) and the salts of
  4-aminophenol and aniline are not resolved; N101 neutralises all of the acid at once.
- L-4: the batch still has no heteroazeotrope (two liquid phases in the pot or the condensate)
  and no jacket check; the volatilities are constant estimates and the boil-up is checked by
  hand; with constant volatilities core counts no heat-up of the charge or the feed (`heat_up`
  needs Raoult's law), and a still's procedure takes no `temperatures:` heat-up (no batch
  content), so the heat-ups' heat and time are by hand (scripts/balance.py).
- L-5: a crystallizer is no batch unit of the recipe: core sizes no crystalliser vessel and gives
  no cool-down time from its jacket, so K-101's 5 h is by hand (scripts/balance.py).
- L-7: a component separator exchanges no heat and a still's model only the vapour's latent
  heat: the sensible heats around V101, ST101 and ST102 and the vessels' metal are hand duties
  on energy streams of their own (Q10 to Q17).
- L-6: the hydrogen is modelled as a constant dose; core has no constant-pressure gas feed on
  demand, so the screening of case (a) of D-011 is reasoned, not calculated.

## Open inputs
Reaction calorimetry with the hydrogen uptake and the hydroxylamine's accumulation; TD24 of the
mass; the solubility of 4-aminophenol in the ammonium sulfate liquor, cold and hot at pH 6; the
by-products behind SRC-1's unaccounted 5.5 % (the yield's upper bound, D-008); the heel's purge
and the catalyst's life at plant scale; the crude aniline's water and its purification; the
ammonium sulfate liquor's recovery and its inventory; K-101's cooling in two stages (cooling
water, then chilled water); prices for the allocation; P&IDs, relief and interlocks (D-011).
