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
| SRC-1 | US 3 383 416 A, R. G. Benner, filed 1965-07-08, granted 1968-05-14: Process for preparing aminophenol, https://patents.google.com/patent/US3383416A/en | description: nitrobenzene reduced with hydrogen at 60 to 120 C (preferably from 75 C) in 5 to 20 wt% (preferably 10 to 15 wt%) sulfuric acid, 1.0 to 5.0 (preferably 1.75 to 2.25) acid equivalents per mol, over Pt, Pd or both on carbon, with a water-soluble quaternary ammonium wetting agent (C10 to C18), atmospheric to 20 psig; the rate rises with the hydrogen pressure and the yield falls with it, the yield rises with the temperature; the reduction is stopped with at least 5 % of the nitrobenzene left, whose layer keeps the catalyst suspended so that it is separated and reused (claims 1, 6, 8); agitation about 15 to 25 HP per 1000 gallons; thiophene-free nitrobenzene. Example 1(A): 271 g (2.2 mol) nitrobenzene, 205 g 98 % H2SO4, 1700 g water, 1.4 g 5 % Pt/C, 1.0 g dodecyltrimethylammonium chloride; 88 % reduced in about 5.5 h; 33 g nitrobenzene layer (12 %); 300 cm3 of water distilled, pH 6.0, aniline distilled; 8 g carbon, 5 min at 98 to 100 C, filtered; pH 7.2 with ammonia, cooled under nitrogen; 154 g PAP, 99.1 %, 73 % on the nitrobenzene reduced, 12.5 g more (6 %) from the filtrate; 28 g aniline. Example 1(B): run to 100 %, 7.5 h, the catalyst then lost to the aqueous mass. Examples 2 to 4: the heel and the 300 g distillate recycled, three reuses without fresh catalyst (73, 76, 78 %), then 0.4 g fresh catalyst (74 %). The reaction temperature of Example 1 and several figures are illegible in the machine text | read (Google Patents); patent, facts only | D-001, D-004 to D-008, D-012 |
| SRC-2 | US 4 307 249 A, E. L. Derrenbacker (Mallinckrodt), filed 1981-01-07, granted 1981-12-22: Process for the selective preparation of p-aminophenol from nitrobenzene, https://patents.google.com/patent/US4307249A/en | a water-soluble dimethylalkylamine oxide (C8 to C20, preferably mostly n-dodecyl) at 0.1 to 0.4 vol% of the aqueous medium instead of the quaternary ammonium chloride, whose chloride gives chloroanilines and whose isopropanol carrier isopropoxyanilines in the aniline co-product; background: the commercial process in 10 to 13 % sulfuric acid, stopped before all the nitrobenzene is used, the aqueous layer decanted and PAP precipitated by neutralisation. Example 1: 650 mL water, 0.25 g 3 % Pt/C, 2 mL surfactant solution (30 to 35 %); heated to 70 C under hydrogen, 110 g 95 to 98 % H2SO4 added, the temperature rising to 90 to 95 C; 185 g nitrobenzene; hydrogen at about 10 in. of water gauge, 7 h at 85 C; nitrogen purge, phases separated below 60 C; neutralised to pH 7 to 8 with ammonium hydroxide at 4 C, stirred 1 h at 5 to 10 C. Runs 1 to 4: 57.1 to 75.2 % conversion, 83 to 102 mg/mL PAP in the aqueous phase, PAP/aniline 4.1 to 4.5 | read (Google Patents); patent, facts only | D-001, D-004, D-005, D-009 |
| SRC-3 | US 3 953 509 A, N. P. Greco (Koppers), priority 1972-10-10, granted 1976-04-27: Hydrogenation of nitrobenzene to p-aminophenol, https://patents.google.com/patent/US3953509A/en | sulfided catalysts (MoS3/C, PtS/C) in sulfuric acid at 135 to 155 C and 200 to 500 psi, to complete conversion without a nitrobenzene recovery; the rearrangement of the hydroxylamine is faster at the higher temperature, else aniline forms; Pt catalysts over-hydrogenate PAP and must be stopped early. Example 3: 160 g nitrobenzene, 275 g H2SO4, 450 g water, MoS3/C, 155 C, 300 psi, 11 h; 65.6 % PAP plus 13 % crude, 22 % aniline. Example 19: 300 g nitrobenzene, 300 g 96 % H2SO4, 300 g water, 2 g 5 % PtS/C, 132 to 135 C, 200 to 500 psi, 18 h; 78 % crude PAP, 7.5 % aniline | read (Google Patents); patent, facts only | D-001 (rejected alternative) |
| SRC-4 | PubChem CID 403 (4-aminophenol), PUG View "Solubility" | solubility in water 0.39 % at 0 C, 0.65 % at 24 C, 0.80 % at 30 C (HSDB citing The Merck Index); 1.6 g/L at 20 C (citing Yalkowsky and He); identity (InChIKey, ChEBI) | read (PUG REST); facts only | D-008, registry |
| SRC-5 | PubChem CIDs 7416 (nitrobenzene) and 6115 (aniline), PUG View "Solubility" | nitrobenzene in water 0.19 % at 20 C and 0.8 % at 80 C (HSDB citing Kirk-Othmer); aniline 3.5 parts per 100 parts water at 25 C and 6.4 at 90 C (HSDB citing Kirk-Othmer) | read (PUG REST); facts only | D-006, D-007, D-008 |
| SRC-6 | PubChem CID 6097028 (ammonium sulfate), PUG View "Solubility" | 70.6 g per 100 g water at 0 C, 76.7 at 25 C (HSDB citing The Merck Index) | read (PUG REST); facts only | D-008 |
| SRC-7 | The `thermo` 0.6.1 and `chemicals` 1.5.2 packages (core's environment) | formation enthalpies (J/mol): nitrobenzene(l) 12500 and aniline(l) 31600 (CRC), 4-aminophenol(s) -192814.5 (WEBBOOK method), water(l) -285825 (ATCT_L), sulfuric acid(l) -814000 (CRC), ammonia(g) -45558 (ATCT_G), ammonium sulfate(s) -1180900 (CRC); liquid densities and heat capacities, normal boiling points, heats of vaporization and the vapour pressures of nitrobenzene (2.814 kPa, VDI_PPDS), aniline (6.108 kPa, WAGNER_MCGARRY) and water (101.42 kPa, IAPWS) at 373.15 K (materials.yaml) | open-source packages queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). The CRC values come from the tables packaged in `chemicals`; the printed (licensed) handbook was not read here | materials, reactions, D-005, D-007, D-009 |
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
  hydroxylamine and its rearrangement, HYDA to aniline), settled and decanted (V101);
- R-102: strip of 15 % of the aqueous layer with its dissolved nitrobenzene, back to the next
  charge (ST101), neutralisation with ammonia (N101);
- R-103: the aniline distilled with water at pH about 6 (ST102), separated in V-102 into crude
  aniline (a co-product) and aniline-saturated water back to the next charge; carbon treatment
  and hot filtration;
- K-101, K-102, C-101, D-101: cooling crystallisation at 283 K (CR101), a second crop from the
  mother liquor concentrated under vacuum (CR102), both crops washed with cold water on the
  centrifuge (W101) and vacuum-dried (D101); the liquors to wastewater treatment (M103).
Boundary: gate to gate, from the feeds at the battery limit to the dried product to packing,
the crude aniline to an aniline purification and the liquors to the site's wastewater
treatment, all outside.

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
paracetamol, modelled 99.5 wt% with 0.34 wt% ammonium sulfate and 0.2 wt% water (SRC-1: 99.1 %).

## D-003 Batch basis, recipe and vessels (2026-11-19)
The recipe (process/recipe.yaml) makes 1073.2 kg per batch; R-101 is the bottleneck at an
8.5 h cycle (1.5 h charge, 5.5 h hydrogen dosing from R101's model, 1 h purge and settle,
0.5 h decant), 931.8 batches a year. R-102 (strip 3.1 h at 390 kW from ST101's model and
neutralisation, 5.6 h), R-103 (aniline distillation 6.9 h from ST102's model, carbon and hot
filtration, 8.4 h), K-101 and K-102 (8.5 h, the cool-down 5 h by hand: Q7 x 8.5 h = 644 kWh at a
mean 129 kW), C-101 (4 h) and D-101 (6.6 h, 5.1 h of drying from D101's rate) each take a batch within the
cycle. The recipe sizes R-101 at 20 m3 (13.1 m3 of batch, 75 % fill for the gas hold-up), R-102
at 20 m3, R-103 at 16 m3 and D-101 at 3.15 m3 (core ADRs 0052, 0057) and checks R-101's jacket
(peak 300 kW against 410 kW at the charge's 24.9 m2 on cooling water). The flowsheet's flows are
the recipe's year averages (no cheme.recipe-basis finding). Every duration not from a model is
ASSUMED.

## D-004 Feeds and the charge (2026-11-19)
Per kg of nitrobenzene charged (SRC-1 Example 1(A)): 6.27 kg of water (spec WAT: the make-up S1
is what the recycled distillates S21 and S22 leave) and 0.741 kg of H2SO4 as 98 wt% acid (1.86
equivalents per mol, inside SRC-1's 1.75 to 2.25; 10.6 wt% acid in the water, inside 10 to 15
wt%). The fresh nitrobenzene (1.366 kg/kg product) is set by the spec CAP; the 98 % acid (0.858
kg per kg of fresh nitrobenzene), the ammonia (2 mol per mol of acid, 0.292 kg/kg) and the cake
wash (0.73 kg/kg) follow it in fixed ratios. Hydrogen: the spec CONV doses what reduces 0.88 of
the nitrobenzene charged (2.16 mol per mol reduced), 0.0485 kg/kg. Catalyst: 5 % Pt/C, SRC-1's
make-up of 0.4 g per 5 batches on about 246 g of fresh nitrobenzene, 0.48 kg per batch; the
heel keeps the rest (lca/lca.yaml consumable). Surfactant: the amine oxide of SRC-2 (no
chloride, so no chloroanilines in the aniline), about 1 g of active per kg of water, ASSUMED
70 % returned with the recycled water: 3.0 kg per batch (consumable). Feeds at 298 K.

## D-005 Reactor R101: semi-batch, kinetics and heats (2026-11-19)
R101 is a semi-batch (`reactor: semibatch`): the charge at 358.15 K (SRC-2: 85 C), hydrogen dosed
at a constant rate over 5.5 h (SRC-1: 88 % in about 5.5 h) and taken up (`absorbed: 1.0`), the
batch ending with the dose. In the plant hydrogen is fed on demand at a constant pressure,
103.8 kPa(a) (SRC-2's 10 in. water gauge); the model's constant dose is the dosing-controlled
limit. The rate laws are ASSUMED (no open kinetics): both first order in nitrobenzene and in
dissolved hydrogen, k = 0.042 and 0.008 m3/(kmol s) at 358.15 K with one activation energy of
40 kJ/mol, so that 0.84 of the nitrobenzene goes to 4-aminophenol and 0.16 to aniline at any
temperature (SRC-1 Example 1(A): 28 g of aniline, 0.301 mol on the 1.936 mol reduced, 15.6 %,
the rest taken as 4-aminophenol; SRC-2's PAP/aniline of 4.1 to 4.5 by mass in the aqueous phase
is about 3.5 to 3.8 by moles, a little more aniline). They are fast enough that the hydrogen is
used as it is dosed: at most 0.37 % of the dosed hydrogen accumulates (cheme process
reactor-hazards). The single liquid phase lumps the nitrobenzene layer, the aqueous acid and the
catalyst (L-1). Heats of reaction from SRC-7, hydrogen as a gas (core ADR 0054), 4-aminophenol
as the solid: HYDP -491.1 kJ/mol, HYDA -552.6 kJ/mol; the heats of solution and protonation are
not counted. R101's duty, 193.5 kW year average (Q2 to cooling water), is the model's.

## D-006 Phase split V101 and the heel (2026-11-19)
After the dose the mass is purged with nitrogen and settled at 333 K (SRC-2: below 60 C). The
aqueous layer takes the acid, the 4-aminophenol, the aniline (as its sulfate) and nitrobenzene to
about 0.6 wt% of its water (SRC-5: 0.19 wt% at 20 C and 0.8 wt% at 80 C, about 0.6 at 60 C,
ASSUMED): 0.4 of the nitrobenzene reaching the split; the other 0.6 (13.9 kg/h, about 7 % of the
nitrobenzene charged; SRC-1 kept 12 % with the dissolved part in it) stays in R-101 as the heel
with the catalyst (tear S20). The dissolved hydrogen goes to the vent with the nitrogen (S8,
0.18 g per kg). No heel purge is modelled: the catalyst's poisons and the heel's impurities need
one in the plant (open input).

## D-007 Strip ST101, neutralisation N101 and aniline still ST102 (2026-11-19)
- ST101: R-102 boils off 15 % of the aqueous layer by mass (SRC-1: 300 cm3 of about 1.9 kg),
  which takes 97 % of the dissolved nitrobenzene back to the next charge (tear S21). The aniline
  is a sulfate in the acid and stays (non-volatile, ASSUMED).
- N101: ammonia, 2 mol per mol of the acid fed, sparged into R-102 and taken up to 0.999 (a
  conversion step, NEU: H2SO4 + 2 NH3 -> (NH4)2SO4); its heat (SRC-7, -275.8 kJ/mol) with the
  liquor cooled from 373 to 363 K, 123.4 kW year average (Q4), to cooling water. SRC-1 adjusts
  to pH 6.0 and later to 7.2; the model neutralises all of the acid in one step, and the salts
  of 4-aminophenol and aniline are not resolved (L-3).
- ST102: R-103 distils the aniline with water until 0.0005 mole fraction of aniline is left
  (ASSUMED: SRC-1 does not say how far), 6.9 h at 390 kW.
- Both stills use constant relative volatilities to water (core's batch still, `volatility:
  constant`), estimated for a solute dilute in water as alpha = gamma_inf x Psat / Psat(water)
  at 373.15 K with gamma_inf taken as 1/x at saturation (SRC-5, SRC-7): nitrobenzene 23.5,
  aniline 4.92 (ASSUMED). Core's Raoult's-law still would make both less volatile than water;
  the immiscible pairs boil as heteroazeotropes, which core does not model (L-4).
- Boil-up 390 kW in each still: U 400 W/(m2 K) (glass-lined, ASSUMED) x about 25 m2 wetted x
  (412 - 373) K, checked by hand; core checks no still's jacket (L-4). The duties Q3, Q5 and
  the condensers' Q3C, Q6 are the stills' models.

## D-008 Separations, crystallisation, wash, drying and the liquors (2026-11-19)
- V102: the distillate cooled to 298 K separates into crude aniline and water. Recoveries
  (ASSUMED): 0.535 of the aniline and 0.0022 of the water to the aniline layer, so that the
  water layer leaves with 3.5 parts of aniline per 100 parts of water (SRC-5's saturation at
  25 C) at the converged recycle; the crude aniline holds 5.3 wt% water (the water's
  solubility in aniline not sourced, ASSUMED) and the nitrobenzene traces. The water layer goes
  back to the next charge (tear S22), where its aniline is inert.
- Carbon treatment: SRC-1's 8 g per 154 g of product at 98 to 100 C, filtered hot through F-101;
  55.6 kg per batch, to incineration (lca/lca.yaml consumable); not in the balance.
- CR101: cooling crystallisation at 283.15 K (SRC-2: 5 to 10 C) from the solubility of
  4-aminophenol in water (SRC-4, three points from 273 to 303 K, interpolated); the ammonium
  sulfate, aniline and other solutes are spectators with no salting-out (ASSUMED: no open data;
  ammonium sulfate is likely to salt the 4-aminophenol out, so the loss to the mother liquor is
  overstated). The slurry is centrifuged in the crystallizer's separation (99.5 % of the
  crystals to the cake, 0.12 kg of liquor per kg of crystals, ASSUMED).
- CR102: the mother liquor concentrated under vacuum by evaporating 0.4 of its water and
  crystallised at 283.15 K for a second crop (SRC-1 recovers 6 % more from the filtrate, the
  method not stated): the ammonium sulfate stays at 0.59 kg per kg of water, below its
  solubility of 0.706 at 0 C (SRC-6). The model's second crop is small (1.7 kg/h, 1.3 %),
  because the first crop already leaves the liquor at saturation (no salting-out).
- W101: both crops reslurried on the centrifuge with 0.73 kg of cold water per kg of fresh
  nitrobenzene (about 1.0 kg per kg of cake) at 283 K and spun to 0.12 kg per kg (ASSUMED); the
  wash dissolves 0.5 % of the product and 0.5 % passes the centrifuge.
- D101: vacuum drying at 333 K under nitrogen to 0.2 wt% volatiles (ASSUMED; 4-aminophenol
  darkens in air), mean rate 4 kg/(m2 h), 70 % efficiency, the dryer's metal heated each batch
  (core's dryer model; its duty Q9 from cheme process crystallizers).
- Result: 99.5 wt% product; 82.1 % of the fresh nitrobenzene as dried 4-aminophenol, against
  SRC-1's 79 % (73 % first crop, 6 % second) on the nitrobenzene reduced. The liquors (6.82 kg/kg:
  23 wt% ammonium sulfate, 0.3 wt% 4-aminophenol, 0.2 wt% aniline) go to the site's wastewater
  treatment; the ammonium sulfate is not recovered (an option for basic engineering).

## D-009 Utilities and heat: every energy flow (2026-11-19)
Utilities (ASSUMED): LP steam 350 kPa(a), 412 K; cooling water 298/308 K; chilled water
278/283 K; electricity. Every heat flow is on an energy stream:
- Q1 (65.8 kW, LP steam): the charge heated to 358.15 K, by hand: the inlets S1, S2, S3, S22 from
  298.15 K, the heel S20 from 333.15 K and the distillate S21 from 313.15 K with the liquid heat
  capacities of materials.yaml, 90.1 kW, less the acid's heat of dilution, 59.2 kJ per mol of
  H2SO4 x 1.4801 kmol/h = 24.3 kW. The 59.2 kJ/mol is derived from SRC-2 Example 1's rise from 70
  to 92.5 C when 110 g of 96.5 % acid enters 650 g of water: (650 x 4.202 + 110 x 1.073) J/K x
  22.5 K / 1.0827 mol, a lower bound (heat losses and the vessel not counted; ASSUMED). R-101's
  metal is not counted (the vessel stays hot between batches).
- Q2 (193.5 kW, cooling water): R101's model (core's semi-batch).
- Q3, Q5 (143.7, 315.5 kW, LP steam) and Q3C, Q6 (the same, cooling water): the stills' models.
- Q4 (123.4 kW, cooling water): N101's conversion model.
- Q7 (75.8 kW, chilled water): CR101's lumped duty, 3.6 kJ/(kg K) from 371 to 283 K (the
  liquor's heat capacity from materials.yaml, ASSUMED constant).
- Q8 (144.5 kW, LP steam): CR102's evaporation at 283 K (water's latent heat 2477 kJ/kg, SRC-7).
- Q9 (22.5 kW, LP steam): D101's dryer model.
- Power (33 kW, ASSUMED): R-101's gas-inducing agitator 15 kW (SRC-1's 15 to 25 HP per 1000
  gallons, at its lower end on 13 m3), R-102 and R-103 6 kW, C-101 8 kW, D-101 4 kW.
- Not counted: the condensers of K-102's evaporation and of the dryer (E-103), the cooling of the
  crude aniline and of the recycled water to 298 K, R-103's carbon treatment hold.
Per kg of product: LP steam 5.48 kWh, cooling water 6.15 kWh, chilled water 0.600 kWh,
electricity 0.261 kWh.

## D-010 Recycles and design specifications (2026-11-19)
Three recycles are converged at the tears S20 (heel), S21 (strip distillate) and S22 (aniline
water) by Broyden (core ADR 0060), with three design specifications solved together (ADR 0070):
CAP (S2 for 1000 t/a of S26), WAT (S1 for 6.27 kg of water per kg of nitrobenzene in S4) and
CONV (S5 for 0.12 kg of nitrobenzene left per kg charged).

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
- (d) The dissolved hydrogen the model releases on a cooling failure (0.19 kg per batch; 7.3 kg at
  k/100) is a model artefact of a homogeneous liquid: in the plant the hydrogen is in the head
  space at 104 kPa(a); the vent's capacity for it is a basic-engineering item.
- (e) Ammonia into the hot liquor (N101) is exothermic but dosed and self-limiting (cheme screens
  no conversion step).

## D-012 Preliminary gate-to-gate LCI (2026-11-19)
`cheme assess lca --write` from the flowsheet's year averages per kg of dried 4-aminophenol, with
per-batch consumables (core ADR 0053): activated carbon 55.6 kg (to incineration), Pt/C make-up
0.48 kg, amine oxide 3.0 kg and nitrogen 60 kg per batch (ASSUMED: R-101's head space of about 7
m3 purged six times, and the dryer's breaks). Linked to library producers (lca/mappings.yaml):
sulfuric acid to sulfuric-acid-1 (98.5 wt%, by mass of acid), hydrogen to hydrogen-1 (pinned by
dataset, since the slug alone picks the first producer), ammonia to ammonia-1, nitrogen to asu-1,
LP steam as heat delivered. Gaps: nitrobenzene (no library producer; a nitration process of
benzene would close it), process water, power, cooling and chilled water, the wastewater
treatment, the carbon and its incineration, the catalyst and the surfactant. Allocation: mass
between the 4-aminophenol and the crude aniline (0.860 / 0.140), an agent proposal for the LCA
practitioner (the conservative bound: all to the 4-aminophenol). The hydrogen vented is an
emission to air (0.18 g/kg, a gap); vent and breathing losses of nitrobenzene and aniline are
declared exclusions. paracetamol-1 can now link its 4-aminophenol feed to this entry's product
`product:PAPP` (its own mappings, its own PR).

## D-013 Dedicated train (2026-11-19)
Library ADR 0035: the train (R-101, R-102, R-103, K-101, K-102, C-101, D-101 and their tanks)
makes only 4-aminophenol, batch after batch. A plant that also makes other aminophenols or
reductions on the same vessels is described as if dedicated; campaigns and changeovers are out
of scope.

## Method and dependency table

| result | method | inputs |
|---|---|---|
| feeds, charge | design specifications CAP, WAT, CONV (core ADR 0070) | SRC-1 ratios, D-002, D-004 |
| R101 | semi-batch with a dosed gas (core ADRs 0050, 0054, 0063) | ASSUMED rate laws (D-005), SRC-7 heats |
| V101, V102 | component separators (ADR 0070) | SRC-5 solubilities (D-006, D-008) |
| ST101, ST102 | batch stills, constant volatility (ADR 0055) | SRC-5, SRC-7 (D-007) |
| N101 | conversion step | SRC-7 (D-007) |
| CR101, CR102, W101 | crystallizers with spectators (ADR 0056) | SRC-4 (D-008) |
| D101 | dryer (ADR 0057) | ASSUMED rate and efficiency (D-008, D-009) |
| tears S20, S21, S22 | Broyden (ADR 0060) | D-010 |
| recipe, vessels | batch recipe (ADRs 0051, 0052, 0057) | D-003 |
| screening | reactor-hazards (ADRs 0058, 0069) | D-011 |
| LCI | assess lca (ADR 0053) | D-012 |

## Core features used (core 1.12.0)
`reactor: semibatch` with a dosed gas taken up and the thermal screening; component separators
(`recovery:`); batch stills with constant volatility and a condenser port; a conversion step with
its duty; crystallizers with spectators, an evaporation and their own separation, and a reslurry
wash; the dryer; three tears with Broyden; three design specifications with `with:` ratios; the
batch recipe with its vessels and jacket check; per-batch LCA consumables.

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
  hand.
- L-5: a crystallizer is no batch unit of the recipe: core sizes no crystalliser vessel and gives
  no cool-down time from its jacket, so K-101's 5 h is by hand.
- L-6: the hydrogen is modelled as a constant dose; core has no constant-pressure gas feed on
  demand, so the screening of case (a) of D-011 is reasoned, not calculated.

## Open inputs
Reaction calorimetry with the hydrogen uptake and the hydroxylamine's accumulation; TD24 of the
mass; the solubility of 4-aminophenol in the ammonium sulfate liquor; the heel's purge and the
catalyst's life at plant scale; the crude aniline's water and its purification; the ammonium
sulfate's recovery; prices for the allocation; P&IDs, relief and interlocks (D-011).
