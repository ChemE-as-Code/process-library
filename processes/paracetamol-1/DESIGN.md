# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Paracetamol (acetaminophen, N-acetyl-4-aminophenol) from 4-aminophenol and acetic anhydride in
aqueous acetic acid, issue ChemE-as-Code/process-library#481, a batch entry of the library.
Concept stage: design basis, batch recipe, balanced BFD/PFD with a mother-liquor recycle,
thermal screening with a rate-constant sensitivity and a preliminary gate-to-gate LCI. Out of
scope here: P&IDs, layout, HAZOP, TEA, datasheets, and the pharmacopoeial purification of the
product (D-001, D-008).

Starting point (2026-11-19): library `main` with the core pin 0e85885 (v1.12.0 with #254).
Core models every step of this route: the semi-batch with its thermal screening (core ADRs
0050, 0058, 0069), a batch digestion with its heat-up (ADR 0063), the cooling crystallisation
and the cake wash as crystallizers with spectators and a Setschenow correction (ADR 0056), the
centrifuge as a specified solid split and the vacuum dryer (ADR 0057), the mother-liquor recycle
at a tear (ADR 0060), the models' duties on their energy streams (ADR 0059) and the batch recipe
(ADRs 0051, 0052). Library ADR 0035: one dedicated train, campaigns out of scope (D-013).
Templates: `n-bromosuccinimide-1` (a precipitation from water, a wash, a dryer and a balance
script for the feeds) and `oxalyl-chloride-1` (recycle tears, rate-constant sensitivity).
Requires cheme-as-code 1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (Google Patents machine text, the open-access article's PDF, PubChem pages, the
values the `chemicals` and `thermo` Python packages return).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 3 917 695 A, A. Schulman, F. Baron, M. Weinberg (Mallinckrodt, Inc.), filed 1974-06-26 (continuation of applications of 1970 and 1973), issued 1975-11-04: Preparation of N-acetyl-p-aminophenol, https://patents.google.com/patent/US3917695A/en | description and claims: 4-aminophenol at 7 to 25 (preferably 10 to 16) wt% in aqueous acetic acid of 2 to 25 (preferably 7 to 10) wt%, treated with activated carbon before the acetylation, then 1.0 to 1.2 mol acetic anhydride per mol at about 40 C and above, the product crystallised by cooling to about 15 C, centrifuged, washed with cold water and dried; the acetic acid the anhydride forms serves the next batches. Example 1: 109 g of 4-aminophenol in 635 cm3 of 10 % acetic acid, about 0.2 g of sodium hydrosulfite to decolour it, 0.5 g of sodium sulfite and 4.3 g of carbon, at 85 C, 0.1 g more hydrosulfite, hot filtration (every step under nitrogen until the acetylation ends), cooled to 35 to 40 C, 114 g of acetic anhydride over about 5 min, heated to 85 C, cooled to 10 to 15 C, 110 g of white product, over 99 %, m.p. above 169 C, passing the N.F. after one recrystallisation; Examples 2 and 3: acetylated before the carbon or in water alone, pink product. Example 4: half of Example 1's filtrate made up with water to 635 cm3, 109 g of fresh aminophenol, 128 g; Example 5: 80 % of the filtrate, 140 g. Example 6: continuous carbon columns, 1.15 mol anhydride per mol | read (Google Patents; some numbers garbled in its OCR, the readable ones used); patent, facts only | D-001, D-003 to D-008 |
| SRC-2 | US 4 565 890 A (Mallinckrodt, filed 1983): Process for the preparation of N-acetyl-p-aminophenol, https://patents.google.com/patent/US4565890A/en | background: 4-aminophenol made by the catalytic hydrogenation of nitrobenzene in a mineral acid, purified and precipitated, redissolved in aqueous acetic acid and acetylated with acetic anhydride; the product crystallised and centrifuged; the mother liquor saturated with the product and holding much acetic acid; distilling it gave only 20 to 25 wt% acetic acid, a coloured second crop and SO2 corrosion. The invention: the mother liquor extracted with ethyl acetate (more than 90 % of the product and 99 % of the acid to the extract), the extract distilled (65 wt% or glacial acetic acid), the residue diluted with water, cooled and a second crop centrifuged, washed with cold water and dried at 70 C under vacuum; Example: 57 % of the product in 500 mL of mother liquor recovered | read (Google Patents); patent, facts only | D-001, D-004, D-008, D-012 (proxy) |
| SRC-3 | Jimenez, J. A.; Martinez, F. (2006) Thermodynamic study of the solubility of acetaminophen in propylene glycol + water cosolvent mixtures. J. Braz. Chem. Soc. 17(1), 125-134, doi:10.1590/S0103-50532006000100018 | Table 2, the mixtures with 0 % propylene glycol: the mole-fraction solubility of acetaminophen in water at 20.0, 25.0, 30.0, 35.0 and 40.0 C, five values, converted here to kg per kg of water (flowsheet CR101 and W101, scripts/balance.py `POINTS`; tests/test_paracetamol_1.py keeps the five mole fractions to check the conversion); the apparent enthalpy of solution from them, 27.17 kJ/mol, our least-squares van 't Hoff fit of ln x over 1/T (scripts/balance.py `vant_hoff()`; D-005, D-007) | read (SciELO PDF); CC BY-NC 4.0, facts only: five single values with their source, no table reproduced | D-005, D-007, D-009 |
| SRC-4 | US 4 524 217 A, K. G. Davenport, C. B. Hilton (Celanese Corp.), priority 1984: Process for producing N-acyl-hydroxy aromatic amines, https://patents.google.com/patent/US4524217A/en | 4-hydroxyacetophenone (Fries rearrangement of phenyl acetate or acetylation of phenol with HF) to its oxime with a hydroxylamine salt, the oxime's Beckmann rearrangement (e.g. Amberlyst 15 in acetic acid, or thionyl chloride in liquid SO2) to paracetamol; background: the 4-aminophenol route's difficulty of a clean mono-acetylation, oligomers and colour bodies | read (Google Patents); patent, facts only | D-001 |
| SRC-5 | PubChem CIDs 1983 (acetaminophen) and 403 (4-aminophenol), HSDB records | identity; densities 1.293 g/cm3 at 21 C (acetaminophen) and 1.290 g/cm3 (alpha-4-aminophenol); acetaminophen 14 g/L in water at 25 C, very slightly soluble in cold and soluble in boiling water, m.p. 168 to 172 C; 4-aminophenol 0.65 % in water at 24 C, m.p. 187.5 C | read (PUG View) | materials, registry, D-007 |
| SRC-6 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (core's environment) | formation enthalpies (kJ/mol) by `chemicals.reaction` Hfl/Hfs: acetic anhydride (l) -624.4 (CRC), acetic acid (l) -483.58 (ATcT) and -484.3 (CRC), water (l) -285.825 (ATcT), aniline (l) 31.6 (CRC), acetanilide (s) -209.4 (CRC); no value for paracetamol; normal boiling points acetic acid 391.05 K, acetic anhydride 412.65 K; `thermo` Chemical at 298.15 K: liquid densities, liquid heat capacities and latent heats at 343.15 K of water (method HEOS_FIT, a fit to IAPWS-95), acetic acid (densities and latent heat DIPPR_PERRY_8E, Perry's Chemical Engineers' Handbook 8th ed. drawing on DIPPR 801; heat capacity VDI_TABULAR, the VDI Heat Atlas) and acetic anhydride (DIPPR_PERRY_8E; heat capacity DADGOSTAR_SHAW, an estimation method); solid heat capacities of paracetamol and 4-aminophenol (LASTOVKA_S, an estimation method) | open-source packages queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). The CRC and ATcT values come from tables packaged in `chemicals`, the DIPPR/Perry's and VDI coefficients from tables packaged in `thermo`; none of the printed (licensed) handbooks was read here | materials, reactions, D-005, D-009 |
| SRC-7 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and the criticality classes of a semi-batch (method, implemented in core ADRs 0050, 0058) | method reference, no data taken | D-011 |
| SRC-8 | processes/acetic-anhydride-1, n-bromosuccinimide-1, oxalyl-chloride-1 (this library) | acetic anhydride 99.5 wt%; the precipitation, wash and dryer pattern and the balance script's form; the tear and rate-constant sensitivity pattern | library, internal | D-004, D-006, D-012 |

Searched and not used: open kinetics of the acetylation of 4-aminophenol or of the hydrolysis of
acetic anhydride in this liquor (none read; both ASSUMED, D-005); a formation enthalpy of
paracetamol (none in `chemicals` 1.5.2 or the NIST WebBook's condensed-phase data; D-005);
solubility of paracetamol in aqueous acetic acid (none read; calibrated, D-007); an open LCI or
plant consumption figure for paracetamol (none found; benchmarks record no open reference).

## D-001 Route and boundary (2026-11-19)

**Decision.** The acetylation of 4-aminophenol with acetic anhydride in aqueous acetic acid,
the route of SRC-1: the aminophenol is dissolved at 358 K in water and half of the last batch's
mother liquor, treated with activated carbon and polish-filtered, cooled to 313 K; the
anhydride (1.15 mol per mol) is dosed into it; the mass is digested at 358 K, cooled to 293 K,
and the crystals are centrifuged, washed with cold water and vacuum-dried at 343 K. Half of the
mother liquor goes back into the next charge (SRC-1 Example 4), the other half with the wash
filtrate and the dryer's condensate to the site's wastewater treatment.

C6H7NO + C4H6O3 -> C8H9NO2 + C2H4O2 (ACET); the anhydride's excess: C4H6O3 + H2O -> 2 C2H4O2
(HYD).

**Why.** It is the route the issue names and the one the open patents describe in enough detail
for a design: SRC-1 gives the ratios, temperatures, the carbon treatment, the work-up and the
mother-liquor recycle with yields; SRC-2 confirms the same industrial sequence (aminophenol from
nitrobenzene, acetylation in aqueous acetic acid, crystallisation and centrifuging). Water as
the solvent and a product that crystallises on cooling make a simple, inherently mild batch
(D-011).

**Rejected.**
- The 4-hydroxyacetophenone oxime route (SRC-4, Celanese): phenol acetylated with HF, the oxime
  made with hydroxylamine and rearranged (Beckmann); avoids the aminophenol but needs HF and
  hydroxylamine handling and a second plant section; no library producer of its feeds either.
- Acetylation in water alone, the anhydride added before the carbon treatment (SRC-1 Examples 2
  and 3): pink product that two recrystallisations do not decolour.
- Reductive acetylation of 4-nitrophenol (hydrogen and the anhydride in one step): not read in
  an open source in this work; recorded as an alternative, not designed.
- Acetylation in neat acetic anhydride or glacial acetic acid: more anhydride and a solvent
  recovery; SRC-1's aqueous route makes the acid it needs.
- Making the 4-aminophenol in the plant (nitrobenzene hydrogenation in sulfuric acid, SRC-2):
  a separate process with hydrogen and catalyst handling; it is a bought feed here (D-004,
  D-012), a candidate library entry of its own.

**Boundary.** From the bought 4-aminophenol, acetic anhydride, water and activated carbon to the
dried crude paracetamol at the packing station; the liquors to the site's wastewater treatment,
the spent carbon to incineration. Out of scope: the pharmacopoeial recrystallisation (SRC-1's
product passed the N.F. after one recrystallisation from water; D-008), milling, packing, the
recovery of acetic acid and paracetamol from the mother liquor (D-008).

## D-002 Capacity, product and operating hours (2026-11-19)

2000 t/a of dried paracetamol in 7920 h (330 days of 24 h), ASSUMED: a dedicated batch train of
fine-chemical scale; no open market figure was used. Product 99.8 wt% paracetamol with 0.19 wt%
water, 63 ppm acetic acid and below 1 ppm 4-aminophenol (model, D-008).

## D-003 Batch basis, recipe and vessels (2026-11-19)

`process/recipe.yaml`: 2602.10 kg per batch, 769 batches a year, cycle 10.30 h. R-101 is the
bottleneck (10.30 h: receive 0.5 h, dose 2.5 h from R101's model, heat-up 2.11 h and cool-down
3.74 h from its jacket, digestion 0.06 h from R102's model, 0.4 h to remove the heat of
crystallisation the cool-down does not count (L-7), hold and transfer 1 h); the dryer D-101
follows at 98 % (10.06 h; its drying time grows with the batch). The batch is the fixed point of
batch = rate x cycle (core ADR 0070's hint), so the flowsheet's 252.53 kg/h of product and the
recipe agree (no `cheme.recipe-basis` finding). The recipe sizes R-101 (25 m3, 78 % full at the
end of the dosing) and D-101 (8 m3); the centrifuge's durations are ASSUMED (no filtration data
for a centrifuge, L-4). One batch takes 32.8 h from M-101's charge to D-101's discharge; R-101
receives the charge when M-101 transfers it (the polish filtration is a `filter` operation, so
the recipe's hand-off is M-101's transfer). Other durations ASSUMED.

M-101 (8.45 h a batch, 82 %) has no batch content the recipe can size from (L-2): its heat-up
(1.65 h) and cool-down (3.8 h) are `scripts/balance.py` `m101_times()`'s estimate on an ASSUMED
jacket: M-101 is taken as R-101's vessel (25 m3, U 300 W/(m2 K), the 29.9 m2 the recipe gives
R-101 at the same charge, 7000 kJ/K of metal), the charge and the metal one lumped mass (61.4
MJ/K of charge a batch). Heating on LP steam in the jacket at 412 K, not R-101's 383 K loop:
M-101 holds no anhydride (D-011), and on the loop the heat-up would take about 2.66 h, leaving
M-101 at 92 % of the cycle with little margin for a slow filtration. Cooling on cooling water
entered as its log-mean equivalent at the end, 304.05 K. Per batch Q1 is about 4.2 GJ (about 700
kW over the heat-up) and Q2 about 3.1 GJ (about 225 kW over the cool-down).

## D-004 Feeds and the charge (2026-11-19)

- 4-aminophenol 100 % (technical grade; impurities and colour bodies not modelled), 0.954 kg per
  kg of product, the feed `scripts/balance.py` scales to 2000 t/a.
- Acetic anhydride 99.5 wt% from acetic-anhydride-1 (the rest taken as acetic acid), 1.15 mol per
  mol of fresh aminophenol (SRC-1 Example 6; claims 1.0 to 1.2), 1.032 kg per kg.
- The charge holds 5.87 kg of liquid per kg of fresh aminophenol (SRC-1 Example 1: 109 g in 635
  cm3 of 10 % acid, about 640 g at an ASSUMED 1.01 g/cm3): the recycled mother liquor and fresh
  process water to make it up, as Example 4 makes up half of the filtrate with water. The charge
  has 13.9 wt% aminophenol and 9.6 wt% acetic acid, inside SRC-1's preferred 10 to 16 and 7 to
  10 wt%.

## D-005 Reactors R101 and R102: kinetics and heats (2026-11-19)

- R101 (`reactor: semibatch`): the anhydride dosed at a constant rate over 2.5 h into the charge
  at 313.15 K, isothermal. SRC-1 adds it within minutes in the laboratory; at 2.4 t a batch the
  dosing is set by R-101's jacket on chilled water (peak 285.6 kW against the 291 kW the jacket
  removes at the charge's area, `cheme process recipe`).
- R102 (`reactor: batch`, same vessel): heated to 358.15 K (`heat_up: true`, the heat-up in Q4)
  and held until 0.9999 of the anhydride left is converted (SRC-1 Example 1 heats to 85 C after
  the acetylation). 0.06 h at the design rates.
- Rate laws, ASSUMED (no open kinetics read): ACET second order, k = 0.5 m3/(kmol s) at 313 K
  (Ea 50 kJ/mol); HYD pseudo-first order in the anhydride, k = 0.005 1/s at 313 K (Ea 45 kJ/mol),
  0.044 1/s at 358 K. With them the dosing is dosing-controlled: 11 % of the anhydride hydrolyses
  in R101 (most of the 13 % excess), the aminophenol is fully converted as the dosing ends
  (3e-7 left), and the 2.2 % of the anhydride left hydrolyses in R102. A first attempt with k(ACET)
  = 0.05 m3/(kmol s) let HYD take so much that the aminophenol stopped at 93 % conversion with 1.15
  equivalents; SRC-1's complete conversion at that ratio needs the amine to win by far, which the
  chosen k gives. Calorimetry must replace both.
- Heats: HYD -56.94 kJ/mol from the liquids' formation enthalpies (SRC-6). ACET has no formation
  enthalpy of paracetamol to work from (SRC-6), so it is ASSUMED equal to that of the analogue
  aniline + acetic anhydride -> acetanilide (solid) + acetic acid, -100.9 kJ/mol (SRC-6, CRC
  values): the product taken as formed solid, which counts its heat of crystallisation (27.17
  kJ/mol, SRC-3 by van 't Hoff) in R101, conservative for the screening and the jacket check; the
  crystallizer CR101 then counts none. The heats this moves, sized by `scripts/balance.py`
  `duties()` with the model's own solubility: at 313 K only 0.57 kmol/h of the 2.21 kmol/h formed
  is solid in the liquor (SRC-3's 313.15 K point with the salting in, D-007), so Q3 holds 12.4 kW
  of crystallisation heat that is really released in CR101's cool-down, where 1.68 kmol/h
  crystallise (12.7 kW); both are on the chilled water, whose total is right to 0.3 kW, but the
  recipe's cool-down time does not see the 12.7 kW, so the recipe adds the time to remove it
  (L-7). The 0.57 kmol/h of crystals redissolve
  in the heat-up to 358 K, 4.3 kW of LP steam, counted in Q7 (D-009). The aminophenol's heat of
  solution is not counted (L-1).

## D-006 Balance script and what core calculates (2026-11-19)

Every step is calculated by `cheme process propagate --fill`, the recycle converged at the tear
S16 in 9 Wegstein iterations. `scripts/balance.py` (library ADR 0027) gives only the feeds that
make 2000 t/a (S1, S2, S4, S11: core does not solve feeds for a product rate), the dissolver's
duties Q1 and Q2 and its heating and cooling times (a mixer step has no energy model, L-2), the
heats core's models leave out (Q7, Q8; D-009), the temperature of S18 and the Setschenow
coefficient's calibration (D-007). It repeats
core's algebra: the reactors' outlet by the atom balance (all the aminophenol converted, the
anhydride all hydrolysed; what the rate laws decide is only the split between ACET and HYD while
dosing, which the digestion then evens out), the crystallizers by the same solubility and
Setschenow coefficient, the centrifuge's splits and the dryer, the recycle by direct iteration.
Its product, 252.525 kg/h, and propagate's, 252.525 kg/h, agree.

## D-007 Crystallisation, solubility and the centrifuge (2026-11-19)

- CR101: core's crystallizer at 293.15 K with the solubility of paracetamol in water at 293.15 to
  313.15 K (SRC-3, five points, linear interpolation). SRC-1 cools to 10 to 15 C; core does not
  extrapolate below the data's 20 C (L-3), so the design crystallises at 293.15 K. Colder would
  also lengthen R-101's cool-down on the 278/283 K chilled water past the dryer's cycle (D-009).
- The mother liquor holds about 20 wt% acetic acid, which raises the solubility (a cosolvent; no
  solubility data in aqueous acetic acid read). A Setschenow coefficient of the acetic acid, k =
  -0.2182 kg/mol (salting in), is calibrated so that the crystallizer reproduces SRC-1 Example 1:
  110 g of product from 109 g of aminophenol, the 41 g not isolated taken as dissolved in the
  mother liquor's 574 g of water with 4.01 mol/kg of acetic acid (`scripts/balance.py`
  calibration()), at the temperature the example isolates at: it cools to 10 to 15 C, and the
  mid-point, 285.65 K, is taken (ASSUMED). There the pure water's solubility, 0.009529 kg/kg, is
  SRC-3's 293.15 K value extrapolated with the van 't Hoff enthalpy of its five points (27.17
  kJ/mol), ASSUMED. Calibrated at 288.15 K instead, k would be -0.2075 and the yield 78.0 %; at
  283.15 K, -0.2292 and 72.6 %. The solubility in the design's mother liquor at 293.15 K is then
  0.126 kg/kg water, 9.9 times the pure water's. The calibration lumps Example 1's handling losses
  into the solubility, so the purge's paracetamol is an upper estimate. The model's yield is 75.5
  % of theory with half the mother liquor recycled (the purge takes 23.1 % of theory, the wash
  1.4 %). Check like for like: the same plant crystallising at SRC-1's 285.65 K gives 81.6 %,
  against SRC-1 Example 4's 128 g isolated with half of the filtrate recycled once (84.8 %), lower
  as the lumped handling losses make it.
- F101 and F102: a vertical peeler centrifuge (SRC-1 centrifuges), 99.5 % of the crystals to the
  cake, 0.15 kg of liquor per kg of crystals, ASSUMED; no filtration time (L-4).
- W101: the cake washed with 0.8 kg of cold water (293 K) per kg of crystals, ASSUMED, modelled
  as a reslurry to saturation (core's crystallizer): the wash dissolves 1.4 % of the theoretical
  product; a displacement wash in the basket would dissolve less.

## D-008 Product, drying, mother liquor and carbon (2026-11-19)

- D101: core's dryer at 343.15 K under vacuum (SRC-2's example dries at 70 C) to 0.2 wt% volatiles
  (water, acetic acid, anhydride in their inlet ratio), ASSUMED. The product: 99.8 wt% paracetamol.
  Colour, related substances and the pharmacopoeial assay are not modelled: SRC-1's product passed
  the N.F. after one recrystallisation from water, which is outside this entry (the functional
  unit is the dried crude product). A follow-up adds the recrystallisation train.
- Mother liquor: half recycled into the next charge (SRC-1 Example 4: 128 g instead of 110 g); a
  higher share (Example 5: 80 %, 140 g) would raise the yield but concentrate colour bodies and
  the aminophenol's impurities, which this model does not carry; 50 % is taken. The other half,
  the wash filtrate and the condensate (4.32 kg per kg of product, 16 wt% acetic acid, 7.5 wt%
  paracetamol; the purge alone 19.5 wt% acetic acid and 9.0 wt% dissolved paracetamol) go to the
  site's biological wastewater treatment. Recovery by extraction with ethyl
  acetate and distillation (SRC-2: more than 90 % of the paracetamol and 99 % of the acid) is
  recorded as the next step and not designed; distilling the liquor directly gives only 20 to 25
  wt% acid and a coloured second crop (SRC-2).
- Decolourisation as SRC-1 Example 1 does it, under nitrogen: activated carbon 4.3 g, sodium
  hydrosulfite (dithionite) 0.3 g (0.2 g, and 0.1 g more before the filtration) and sodium sulfite
  0.5 g per 109 g of aminophenol; on the 2483 kg of fresh aminophenol a batch, 97.9 kg of carbon,
  6.8 kg of hydrosulfite and 11.4 kg of sulfite. The carbon is used once and incinerated; the two
  salts dissolve and leave with the liquors to the wastewater treatment, oxidised to sulfate there.
  All three are `lca/lca.yaml` consumables with `per_batch` (library ADR 0035), each with its
  disposal. They and the polish filter F-100 are not in the balance (charged and, for the carbon,
  filtered off in M-101's own cycle; the salts, 0.1 % of the batch's 17.9 t of charge, are not
  carried in the liquor's components).

## D-009 Utilities and heat: every energy flow (2026-11-19)

| stream | what | from | year average |
|---|---|---|---|
| Q1 | M-101's charge heated from 295.6 to 358 K and its metal from 313 K, LP steam in the jacket | scripts/balance.py (liquid heat capacities, metal ASSUMED 7000 kJ/K) | 112.0 kW |
| Q2 | M-101's charge and metal cooled to 313 K, cooling water 298/308 K | scripts/balance.py | 83.0 kW |
| Q3 | heat of acetylation and hydrolysis at 313 K, chilled water 278/283 K | core's semi-batch model | 64.6 kW |
| Q4 | the digestion's heat-up 313 to 358 K (the content), LP steam via the hot-water loop | core's batch model (`heat_up`) | 79.3 kW |
| Q5 | cooling crystallisation 358 to 293 K with R-101's metal, chilled water | core's crystallizer (energy, ADR 0063) | 128.2 kW |
| Q6 | the dryer at 343 K, the vessel's heat each batch, 70 % efficiency | core's dryer model | 44.9 kW |
| Q7 | R-101's metal in the heat-up (315 MJ a batch, 8.5 kW) and the crystals redissolved in it (4.3 kW, D-005), LP steam via the hot-water loop | scripts/balance.py | 12.8 kW |
| Q8 | the dryer's vapour condensed and cooled to 303 K in E-101 (24.8 kW) and the product with D-101's metal cooled from 343 to 303 K before the discharge (5.5 kW), cooling water | scripts/balance.py (D101's latent heats, liquid heat capacities) | 30.2 kW |
| P1 to P4 | agitators of M-101 and R-101, centrifuge, dryer agitator and vacuum pump | ASSUMED | 22 kW |

Per kg of product: LP steam 0.986 kWh (Q1, Q4, Q6, Q7), cooling water 0.449 kWh (Q2, Q8), chilled
water 0.763 kWh (Q3, Q5), electricity 0.087 kWh. R-101's jacket: U 300 W/(m2 K), chilled water
entered as its log-mean equivalent 280.71 K for 313.15 K; heating on a pressurised hot-water loop
at 383.15 K. M-101's jacket: D-003. Not counted: the aminophenol's heat of solution (L-1).

The crystallisation's cool-down runs on chilled water from 358 K to 293 K, although about 60 %
of its sensible heat (358 to 318 K) lies in the cooling water's range: R-101 is the bottleneck
(D-003), and a cooling-water stage would lengthen its cool-down. Estimated from the recipe's own
time constant (3.74 h from 358 to 293 K at 280.71 K, 2.05 h): cooling water to 318 K (entered as
303.72 K, the log-mean at the end) 2.72 h, then chilled water to 293 K 2.25 h, 4.97 h in all,
1.23 h more, R-101 at 11.5 h against 10.3 h: a cycle 12 % longer, for about 79 kW less chilled
water. Recorded as the trade-off for basic engineering (a larger R-101 or a second
vessel for the crystallisation); the concept keeps the chilled water. The chilled water's
refrigeration is outside the boundary (an LCI gap).

## D-010 Wastewater and emissions (2026-11-19)

The liquors (S18, 1092 kg/h) go to the site's wastewater treatment: acetic acid and paracetamol
are biodegradable organics with a high COD; with them, the decolourisation's sulfite and
hydrosulfite (18.2 kg a batch, D-008). The treatment is linked through the shared Atlas
wastewater proxy per kg (D-012); the sulfur salts are a gap. No emission to
air is in the balance; the vents of M-101, R-101, V-101 and the tanks and the dryer's vacuum
exhaust are declared exclusions in `lca/lca.yaml` (no P&ID yet).

## D-011 Thermal screening, the rate-constant sensitivity and the hazards (2026-11-19)

`cheme process reactor-hazards` (SRC-7's method, core ADRs 0058, 0069), screening values only:

| case | dT_ad | max. accumulation | MTSR | MTT | R-101 cycle |
|---|---|---|---|---|---|
| design k | 35.1 K | 2.18 % (end of dosing) | 313.6 K | 373.15 K | 10.30 h |
| k/10 (both reactions) | 35.1 K | 8.2 % | 315.0 K | 373.15 K | 10.83 h |
| k/100 | 35.1 K | 15.1 % | 317.1 K | 373.15 K | 17.31 h |

The MTT is water's normal boiling point, a lower bound of the mass's bubble point (acetic acid is
less volatile and forms no azeotrope with water). R102: dT_ad 0.5 K from the anhydride left.
No criticality class without a TD24 of the decomposition (calorimetry). Findings:
- Even with all the anhydride charged at once and the cooling lost, the mass rises about 38 K,
  from 313 to 351 K, below the MTT: core's dT_ad is the largest single reaction (ACET, 35.1 K),
  and the 0.15 mol excess then hydrolyses as well (HYD's 22.8 K for all 1.15 mol x 0.15/1.15 = 3.0
  K). The dosing protects the jacket, not the MTT. But the anhydride must not be dosed hot: from
  the digestion's 358 K the same charge would end above 373 K. The dosing needs a permissive
  below 330 K (the MTT less the 38 K rise, with a 5 K margin) and a trip on high temperature, loss
  of agitation or chilled water (for the P&ID).
- A cold charge (below the design 313 K) slows both reactions and lets the anhydride accumulate
  (k/100: 15 %); its heat then follows on warming. The dosing permissive also needs a low limit.
- The hot-water loop at 383 K is above the MTT: a failed temperature control in the heat-up boils
  the mass into R-101's condenser, a pressure and loss-of-containment case, not a runaway. M-101's
  jacket on LP steam at 412 K (D-003) can boil the aqueous charge the same way; it holds no
  anhydride, so no reaction heat follows.
- Acetic anhydride (flammable, corrosive, reacts with water) in V-101 and the dosing line;
  acetic acid vapour at 358 K; paracetamol dust at the dryer's discharge (dust explosion
  assessment open); 4-aminophenol is harmful and a skin sensitiser (handling with closed
  charging, open input).

## D-012 Preliminary gate-to-gate LCI (2026-11-19)

`lca/lca.yaml`, written by `cheme assess lca --write`: every exchange per kg of dried product
from the flowsheet's year averages, the activated carbon, sodium hydrosulfite and sodium sulfite
as per-batch consumables with their disposal (D-008). Linked in the Atlas build
(`scripts/build_lci.py`): the acetic anhydride to acetic-anhydride-1 and the LP steam as heat
(`lca/mappings.yaml`); the process and wash water, the electricity, the cooling water, the
wastewater (the shared per-kg proxy) and the sodium sulfite through the shared
`lci/mappings.yaml`. Gaps, as the build reports them: the 4-aminophenol (no library producer of
it or of nitrobenzene), the chilled water, the carbon and its incineration, the hydrosulfite,
and the two salts' disposal. This study's own `cheme assess lca` has no background at all
(`lca/gaps.csv`). The aminophenol's recorded proxy (not linked): the hydrogenation of nitrobenzene in
sulfuric acid (SRC-2), C6H5NO2 + 2 H2 -> C6H7NO + H2O, 1.128 kg nitrobenzene and 0.0369 kg hydrogen
per kg of aminophenol at the stoichiometry (registry molar masses), without the acid, its
neutralisation, the purification and the yield; a shared estimate proxy (library ADR 0039) needs a
nitrobenzene producer in the library first. No impact results.

## D-013 Dedicated train (2026-11-19)

Library ADR 0035: the train M-101, R-101, T-103, C-101, D-101 makes only paracetamol. Paracetamol
is in fact made on dedicated large plants as well as on multipurpose ones; changeovers and shared
tank farms are out of scope.

## Core features used (core 1.12.0)

- `reactor: semibatch` with two competing rate laws and `batch.target`, `reactor: batch` with
  `heat_up` (ADRs 0050, 0063); `cheme process reactor-hazards` over every reaction (ADRs 0058, 0069).
- `crystallizer:` with spectators, solubility `points` and a Setschenow `salting_out`, and its
  `energy:` with the vessel's metal (ADRs 0056, 0063); `solid_separation`; `dryer:` (ADR 0057).
- `tears:` with Wegstein (ADR 0060); the models' duties on their energy streams (ADR 0059).
- `process/recipe.yaml` with `from:` and `temperatures:` operations, vessel and jacket checks,
  the `cheme.recipe-basis` agreement (ADRs 0051, 0052, 0070).

## Core limits hit (each a candidate core issue)

- **L-1** Heats of solution of a dissolved solid charge and of a product precipitating inside a
  semi-batch are not modelled (the reactor carries the product dissolved); the heat of
  crystallisation is moved into ACET's heat instead, and the redissolution in the heat-up is
  scripted (Q7): sized in D-005.
- **L-2** A mixer step has no energy model and no batch content: M-101's heating and cooling and
  their times are scripted (Q1, Q2, `m101_times()`) and its vessel is not sized by the recipe
  (D-003, D-006).
- **L-3** Solubility `points` are never extrapolated: the crystallisation ends at 293.15 K, the
  lowest point of SRC-3's data, not SRC-1's 283 to 288 K (D-007). Correct, but the design's yield
  (75.5 %) is lower than at the source's temperature (81.6 % for the same plant); the script
  extrapolates by van 't Hoff only to calibrate the salting in.
- **L-4** `solid_separation` has a Ruth filtration time for filters but none for a centrifuge's
  loads: C-101's durations are ASSUMED (D-003).
- **L-5** A batch's `heat_up` counts the content, not the vessel's metal, while the recipe's heat
  operation reports both: Q4 leaves out R-101's metal, 315 MJ a batch, 8.5 kW, which the
  script adds in Q7 (D-009).
- **L-6** A recipe vessel holds one batch or semi-batch: R102 runs in R-101 but is named by its
  operation (`from: R102`), not in the unit's `units:` (D-003).
- **L-7** The recipe's cool-down time counts the content's sensible heat and the metal, not the
  heat of crystallisation: the 12.7 kW (about 470 MJ a batch) the crystals release in CR101's
  cool-down (counted in Q3, D-005) is not in R-101's 3.74 h. At the cool-down's mean 353 kW that
  is about 0.37 h more: the recipe adds it as an ASSUMED operation of 0.4 h (`release`), which
  makes R-101 the bottleneck instead of the dryer (D-003).

## Open inputs

Calorimetry of the acetylation and hydrolysis (rates, heats, TD24); the solubility of
paracetamol in aqueous acetic acid at 283 to 313 K; the 4-aminophenol's specification and
impurities; the centrifuge's and dryer's test data; the recrystallisation train; the mother
liquor's recovery (SRC-2); the wastewater treatment's capacity for the COD.
