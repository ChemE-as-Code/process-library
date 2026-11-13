# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Oxalyl chloride from anhydrous oxalic acid and phosphorus pentachloride made in situ, issue
ChemE-as-Code/process-library#144, a batch entry of the library. Concept stage: design basis,
batch recipe, balanced BFD/PFD, thermal screening with a rate-constant sensitivity and a
preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-12): library `main` with the core pin v1.11.0. An earlier scout judged
oxalyl chloride not credible at Tier 2 while core had no batch distillation and no gas handling.
Core now has both: semi-batches with a gas vent, the liquid's vapour and a partial vent
condenser (core ADRs 0050, 0054, 0062), batch stills with a rectifying column (ADRs 0055, 0061),
recycles with tear streams (ADR 0060), the models' duties on their energy streams (ADR 0059),
heats of solution and heat-up (ADR 0063) and the batch recipe (ADRs 0051, 0052, 0057). Library
ADR 0035: one dedicated train, campaigns out of scope (D-013). Templates: `acetyl-chloride-1`
(HCl vent, batch still with a column), `potassium-tert-butoxide-1` (recycle tears, a balance
script for what core cannot model). Requires cheme-as-code 1.11 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (Google Patents machine text; NIST WebBook, PubChem and Wikipedia pages; the open
data tables packaged in the `chemicals` Python package).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 4 341 720 A, A. Vogel, G. Steffan, K. Mannes, V. Trescher (Bayer AG), priority DE 2840435, 1978-09-16, published 1982-07-27: Process for the preparation of oxalyl chloride, https://patents.google.com/patent/US4341720A/en | description: oxalic acid (or a lower dialkyl oxalate) with PCl5 in POCl3, with a tertiary amine, pyridine or carboxamide (e.g. 2,4-dimethylpyridine) at 0.001 to 0.5, preferably 0.01 to 0.05 part per part of PCl5; 10 to 115 C (preferably 40 to 80 C) at 0.02 to 2 bar (preferably 0.15 to 0.5 bar); at least 1.7 (preferably 1.8 to 2.0) mol of PCl5 consumed per mol of acid; overall equation 2 PCl5 + (COOH)2 -> (COCl)2 + 2 HCl + 2 POCl3; the oxalyl chloride distils off as it forms, with POCl3 (0 to 20 parts per part), and is rectified; the PCl5 left over stays in the reactor and is re-used; the half acid chloride is unstable and decomposes to CO, CO2 and HCl, which gave the prior art its gas evolution, its safety problems and its 45 to 55 % yields. Example 19: 1340 g POCl3, 65 g 2,4-dimethylpyridine and 1769 g PCl3, 930 g chlorine over 6 h at 85 C, the excess chlorine taken off under vacuum, cooled to 60 C; 375 g oxalic acid in 375 g POCl3 added over 4 h at 60 C and 250 mbar, then 0.5 h at 70 C and 250 mbar; 2052 g crude distillate with 21.9 wt% oxalyl chloride, 445 g isolated by fractional distillation. Example 20: 1025 g PCl3 added to Example 19's residue, 570 g chlorine over 3 h at 85 C under reflux, then the same acid charge, the same crude and the same 445 g. Yields of the other examples 70 to 91 % of theory; Example 18 continuous | read (Google Patents); patent, facts only | D-001, D-003 to D-008 |
| SRC-2 | US 4 390 708 A, R. J. Stokowski, G. Tertzakian, T. C. S. Ruo (Terochem Laboratories), filed 1981: Process for producing oxalyl chloride and intermediates, https://patents.google.com/patent/US4390708A/en | ethylene carbonate photochlorinated (mercury lamps, 70 to 100 C, 5 to 6 days in a 100 L vessel) to tetrachloroethylene carbonate (91 %), split with about 1 % DMF at 60 to 85 C to oxalyl chloride (79 %) and phosgene; describes the oxalic acid + PCl5 reaction as a solid-solid reaction with endothermic and exothermic stages, hard to control, 30 to 50 % yields and more than the stoichiometric POCl3 | read (Google Patents); patent, facts only | D-001, D-005 |
| SRC-3 | US 2 816 141 A, E. K. Ellingboe (E. I. du Pont de Nemours), 1957: Process for oxalyl chloride production, https://patents.google.com/patent/US2816141A/en | bis(trichloromethyl) oxalate (from dimethyl oxalate photochlorinated in CCl4) split with a tertiary amine, activated charcoal or DMF at 50 to 60 C to oxalyl chloride and phosgene; states that conventional acid chloride methods fail on oxalic acid (the half chloride decomposes to HCl, CO and CO2) and that PCl5 needs a large excess | read (Google Patents); patent, facts only | D-001 |
| SRC-4 | Wikipedia, Oxalyl chloride, https://en.wikipedia.org/wiki/Oxalyl_chloride | made commercially from ethylene carbonate (photochlorination, then the split to oxalyl chloride and phosgene, citing Ullmann's); first made with PCl5 from diethyl oxalate, also from oxalic acid and PCl5 (citing DE 2840435); with water it gives only HCl, CO2 and CO (after Staudinger); bp 63 to 64 C, density 1.4785 g/mL; toxic by inhalation (H331), corrosive (H314), over ten times less acutely toxic than phosgene | read; CC BY-SA, facts only | D-001, D-010, D-011 |
| SRC-5 | The `chemicals` 1.5.2 package (core's environment): its packaged CRC Handbook tables (`heat_capacity.CRC_standard_data`: formation enthalpies; `miscdata.CRC_organic_data`, `CRC_inorganic_data`: densities, boiling and melting points; `phase_change.Hvap_data_CRC`), Poling et al.'s ideal-gas heat capacities and ATcT formation enthalpies | formation enthalpies (kJ/mol): oxalyl chloride (l) -367.6 and (g) -335.8, POCl3 (l) -597.1 and (g) -558.5, PCl3 (l) -319.7, PCl5 (s) -443.5, oxalic acid (s) -829.9, H3PO4 (l) -1271.7, water (l) -285.8, HCl (g) -92.3, CO (g) -110.5, CO2 (g) -393.5; boiling points oxalyl chloride 336.65 K, PCl3 349.15 K, POCl3 378.65 K, 2,4-dimethylpyridine 431.55 K; melting points POCl3 274.33 K, oxalyl chloride 257.15 K; densities and liquid heat capacities of materials.yaml | open data package queried 2026-11-12/13; facts only. The CRC values come from the tables packaged in `chemicals`, not from the printed (licensed) handbook (library ADR 0037) | materials, reactions, D-005, D-009 |
| SRC-6 | NIST Chemistry WebBook, SRD 69: PCl3 (C7719122), POCl3 (C10025873), oxalyl chloride (C79378), water | Antoine constants of PCl3 (221.6 to 347.3 K), POCl3 (275 to 378.3 K) and water, each fitted by NIST to Stull (1947); POCl3 melts at 274.2 to 274.35 K (Witschonke 1954); oxalyl chloride: boiling point 336.7 K at 1.02 bar, heat of vaporization 32 +/- 4 kJ/mol (Walker and Prophet 1967), no Antoine fit | read | materials, D-007 |
| SRC-7 | PubChem CIDs 65578 (oxalyl chloride), 971 (oxalic acid), 7936 (2,4-dimethylpyridine), 24813 (phosphoryl chloride) | identity (formula, InChIKey, CAS, ChEBI cross-references); POCl3 reacts with water to phosphoric acid and HCl (HSDB) | read (PUG REST) | registry, reactions |
| SRC-8 | Wikipedia, Oxalic acid, https://en.wikipedia.org/wiki/Oxalic_acid | made mainly by oxidising carbohydrates (glucose) with nitric acid or with air over vanadium pentoxide; the dihydrate turned anhydrous by heating or azeotropic distillation; about 120 kt/a (citing Ullmann's) | read; CC BY-SA, facts only | D-004, D-012 (proxy) |
| SRC-9 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and the criticality classes of a semi-batch (method, implemented in core ADR 0050) | method reference, no data taken | D-011 |
| SRC-10 | processes/chlor-alkali-1, asu-1, phosphorus-oxychloride-1, nitric-acid-1, acetyl-chloride-1 (this library) | dry chlorine; gaseous nitrogen; POCl3 (and PCl3 as an internal block, not exported); nitric acid; the PCl3 proxy of acetyl-chloride-1 | library, internal | D-004, D-012 |
| SRC-11 | Ullmann's Encyclopedia of Industrial Chemistry, Oxalic Acid (doi:10.1002/14356007.a18_247) and its oxalyl chloride coverage | - | not read (licensed); named by SRC-4 and SRC-8 for the ethylene carbonate route and the oxalic acid volume | route lead only |

Searched and not found openly (2026-11-12/13): kinetics or calorimetry of oxalic acid with PCl5
in POCl3 or of PCl3 with chlorine in POCl3, a measured heat of reaction, a TD24 of the reaction
mass or of the heel, the solubility of PCl5, HCl, CO or chlorine in POCl3 and oxalyl chloride,
VLE data of oxalyl chloride with POCl3, an Antoine fit or measured liquid heat capacity of
oxalyl chloride, the purity of oxalyl chloride on this route at plant scale, a plant's specific
consumptions and prices.

## D-001 Route and boundary (2026-11-12)
Decision: Bayer's one-pot route of SRC-1 (Examples 19 and 20), as a batch plant on one
reactor-still R-101 and one rectification still C-201 with its column K-201:
- R101: PCl3 + Cl2 -> PCl5, chlorine dosed into fresh PCl3 charged to the heel (the previous
  batch's residue: excess PCl5 suspended in POCl3 with the amine catalyst);
- R102: (COOH)2 + 2 PCl5 -> (COCl)2 + 2 POCl3 + 2 HCl, the anhydrous acid suspended in recycled
  POCl3 dosed into the PCl5 slurry; the loss (COOH)2 + PCl5 -> CO + CO2 + POCl3 + 2 HCl, the
  half chloride's decomposition SRC-1 names;
- ST101: the crude (oxalyl chloride with POCl3) stripped off the heel under vacuum in R-101;
  5 % of the heel purged, the rest kept for the next batch;
- ST201: the crude rectified at atmospheric pressure, the product cut overhead, an off-cut back
  to the next acid slurry, the POCl3 left in the still partly back to the acid slurry, the rest a
  co-product;
- A101: the off-gas (HCl, CO, CO2, the vapours past the vent condenser) absorbed in water to
  30 wt% hydrochloric acid; CO, CO2 and chlorine traces to the site's thermal oxidiser.
Boundary: gate to gate, from PCl3, chlorine, anhydrous oxalic acid, the catalyst and water to
the product, POCl3, hydrochloric acid, the heel purge and the tail gas.
Reason: SRC-1 is the one open source with plant-like quantities for every step (its examples
give the charges, the dosing times, the temperatures and pressures, the crude's assay and the
isolated product) of a batch process, and it re-uses the PCl5 heel. The route needs gas
evolution with a vent, a heel recycle, a solids slurry, vacuum stripping and rectification, all
of which core 1.11.0 now models (D-005 to D-008).
Rejected:
- the ethylene carbonate route (SRC-2, SRC-4: photochlorination to tetrachloroethylene
  carbonate, then the split to oxalyl chloride and phosgene). SRC-4 names it the commercial one,
  citing a licensed work not read here (SRC-11). Its first step is a photochlorination of 5 to 6
  days, which core has no model for (no photochemistry), and it co-produces one mol of phosgene
  per mol of oxalyl chloride, which then needs its own outlet. A candidate for a later entry.
- bis(trichloromethyl) oxalate (SRC-3): photochlorinated dimethyl oxalate split to oxalyl
  chloride and phosgene, the same objections, and a small-scale example only.
- oxalic acid with thionyl chloride or phosgene: SRC-3 states that conventional acid chloride
  methods fail with oxalic acid (the half chloride decomposes to CO, CO2 and HCl); no open source
  with quantities was found for either.
- dialkyl oxalates with PCl5 (SRC-1 claims them too; SRC-4: Fauconnier's first preparation): an
  alkyl chloride by-product and no example with quantities read.
- reaction under 250 mbar with the crude distilling off as it forms (SRC-1's examples): a
  reacting semi-batch that boils is outside core's semi-batch model (it refuses a content at its
  boiling point, ADR 0062). The plant reacts at atmospheric pressure, then strips the crude off
  under vacuum in the same vessel (D-007, L-1).
Assumptions: the amine's role (catalyst, kept in the heel as its hydrochloride) as SRC-1
describes; no side reactions beyond DEC (no phosgene formation is stated by SRC-1; D-011).

## D-002 Capacity, product and operating hours (2026-11-12)
Decision: 500 t/a of the distilled product cut (stream S17) in 7920 h (330 days of 24 h), the
library's fine-chemical batch scale, ASSUMED (no open market figure used). The product cut is
collected while its mean is at least 99.5 wt% oxalyl chloride (ASSUMED specification; SRC-1
claims high purity without a number). Model: 99.50 wt% oxalyl chloride, 0.44 wt% POCl3, 0.06 wt%
PCl3 (D-008).
Reason: a reagent-grade product; POCl3, the main impurity, is the still's heavy key.
Assumptions: the specification is the concept's, not a customer's.

## D-003 Batch basis, recipe and vessels (2026-11-13)
Decision: `process/recipe.yaml` (core ADRs 0051, 0052, 0057): R-101 holds M101, E101, R102,
ST101 and SP101 (`units`) and is sized from R102, which holds the most and vents; the
chlorination R101 runs in the same vessel but is not in `units` (core refuses a vessel over two
semi-batch steps, ADR 0057, L-5), its dosing and post-reaction take their times from its model
(`from: R101`). C-201 holds ST201, E202 and SP201. Durations: charge 0.5 h, sample 0.25 h,
vacuum break and purge 0.5 h, C-201's receive 0.5 h, cooling 1.0 h, drain 0.5 h (ASSUMED); the
warming from the jacket (`temperatures`), the dosing and post-reactions from R101's and R102's
models, the strip and the rectification from ST101's and ST201's boil-up.
Result (`cheme process recipe`): R-101 is the bottleneck, occupied 20.27 h a batch (C-201 9.5 h,
47 %); 390.7 batches a year of 1280.5 kg, which gives 63.18 kg/h against the flowsheet's 63.13
(0.07 %, no `cheme.recipe-basis` finding). The batch size is the fixed point of batch size =
rate x cycle, since the strip's time grows with the batch. R-101: 12.5 m3 (73 % full with
9.17 m3 at the end of R102, D 2.37 m); C-201: 6.3 m3 (80 % full with 5.01 m3).
The chlorine dosing time, 8 h, is set by R-101's jacket: at 3 h (SRC-1, Example 20) R101's
peak is 45.1 kW/m3, about 2.2 times what the jacket on cooling water removes; at 6 h (Example
19) about 1.1 times. At 8 h the peak is 16.36 kW/m3 x 6.46 m3 = 105.6 kW
against U A dT = 0.3 kW/(m2 K) x 14.93 m2 (at R101's charge, 6.23 m3, core's `wetted_area`) x
29.72 K = 133.1 kW (0.79), checked by hand (L-5). R102's peak, 23.2 kW, is checked by core:
136.5 kW at its charge (15.3 m2). The cooling water's log-mean temperature: (35 - 25) / ln(35/25)
= 29.72 K below the 333.15 K mass, entered as a constant coolant temperature of 303.43 K.
Warming and the strip use R-101's hot-water loop at 353/348 K (mean 350.65 K), below both MTTs
(D-009, D-011).
Rejected: chilled water on R-101's jacket for a 3 h chlorination (refrigeration energy, and
the chilled water's 278 K supply would freeze POCl3 on the wall, 274.33 K, only 4 K away);
chlorination at SRC-1's 85 C (358 K, 2.7 K below R101's MTT, D-011).

## D-004 Feeds, charge and the heel (2026-11-13)
Decision: per mol of oxalic acid 1.915 mol of fresh PCl3 (the 1.85 the reactions consume at
the selectivity 0.85, D-006, and the heel's purge; SRC-1, Example 20 adds 1.79 to the previous
residue), 1.005 mol of chlorine per mol of fresh PCl3 (a slight excess: the little left
dissolved goes with R102's vent), and the catalyst's make-up equal to the purge's, 3.137 g per kg
of PCl3. The heel's purge is 5 % a batch (SP101, ASSUMED): it bleeds the catalyst's degradation
and the oxalic acid left (0.1 % of the acid) and fixes the heel at the steady state: 6941 kg a
batch (S3), PCl5 and POCl3 with 3.1 wt% catalyst. Per batch: 3421.5 kg PCl3, 1775.4 kg chlorine,
1171.4 kg anhydrous oxalic acid, 10.7 kg catalyst; R102's charge then holds 3.12 mol of PCl5
per mol of acid (Example 20, about 3) and 0.025 kg of catalyst per kg of PCl5 (SRC-1: preferably
0.01 to 0.05). The acid is suspended in 1932.9 kg of the still's POCl3 (36 % of it, SP201) and
the 1103.4 kg off-cut (V-102, M102), about 2.6 parts of liquid per part of acid (SRC-1: one
part of POCl3).
`scripts/balance.py` scales every feed to 500 t/a: the plant is linear in its feeds at fixed
ratios (L-6).
Assumptions: all feeds pure and dry; the anhydrous acid from the supplier (SRC-8: the dihydrate
is the usual form; water entering with it hydrolyses PCl5, D-011).

## D-005 Reactors R101 and R102: semi-batches, kinetics and heats (2026-11-13)
Decision: two isothermal semi-batches at 333.15 K and 101.325 kPa(a) (core ADR 0050), each with a
power-law rate law, ASSUMED (no open kinetics or calorimetry found):
- R101 (CHL): chlorine dosed as a gas over 8 h and taken up entirely (`absorbed: 1.0`), with its
  heat of solution (`dosing.heat_of_solution`, ADR 0063) of -20.41 kJ/mol (minus its heat of
  vaporization, an ideal solution, ASSUMED); k = 0.1 m3/(kmol s) at 333 K, Ea 40 kJ/mol, first
  order in PCl3 and in chlorine, so fast that the dosing limits it (SRC-1 chlorinates as fast as
  it feeds); to 0.999 of the PCl3. Heat of reaction on the dissolved basis -103.4 kJ/mol (CRC:
  PCl5 (s) less PCl3 (l), -123.8, less the heat of solution). Result: the post-reaction after
  the 8 h dosing takes 0.159 h.
- R102 (OXC, DEC): the acid slurry dosed over 4 h (SRC-1), to 0.999 of the acid; k = 1.2e-3
  m3/(kmol s) at 333 K for the sum, Ea 60 kJ/mol, first order in the acid and in PCl5, sized so
  that the acid reacts within about the examples' 0.5 h after-reaction (0.42 h), split 0.85 to
  OXC and 0.15 to DEC (D-006). Heats from CRC formation enthalpies with the solids as solids and
  HCl, CO and CO2 formed as gases (ADR 0054): OXC -29.5, DEC -12.3 kJ/mol. SRC-2 says the
  classic reaction has endothermic and exothermic stages; the model has one heat per reaction.
  HCl, CO and CO2 leave as they form (`batch.vent`), none dissolved (no Henry constant found,
  L-2); the gas leaves saturated with the liquid's oxalyl chloride, POCl3 and chlorine
  (`vent.vapour`, Raoult) through the vent condenser E-102 at 283.15 K, its condensate back
  (`vent.condenser`, ADR 0062, D-010).
- The solids (PCl5, the acid) are pseudo-homogeneous in the slurry (L-1).
Result (`cheme process reactors`): R101's duty 41.45 kW to cooling water (reaction 35.25, heat
of solution 7.00, less the chlorine warmed 0.80 kW); R102's duty 0.136 kW to cooling water: the
reaction's 4.80 kW less the dose warmed (0.91), the vapour the gas carries off (3.22) and the
condensate returned cold (0.53), near balance. Its sign depends on the dose's temperature (it
was 0.72 kW into R102 with the slurry at 300 K): the jacket must heat and cool. R102's peak
cooling duty is 2.54 kW/m3, 23.2 kW for the batch (`cheme process recipe`).
Rejected: R102 at SRC-1's 60 C and 250 mbar boiling (D-001); a heat of reaction from the
literature (none found).

## D-006 Selectivity calibration and the yield (2026-11-13)
Decision: DEC's share 0.15 of the acid (OXC 0.85, the same Ea so the split holds at every
moment), calibrated to the oxalyl chloride in SRC-1's crude distillate: 2052 g at 21.9 wt%, 449 g
or 3.54 mol from 375 g (4.17 mol) of acid, 85.0 % of theory; 445 g (84.2 %) were isolated.
Result: 84.9 % of the acid forms oxalyl chloride (0.85 of the 0.999 converted); 7.41 % of the
acid's worth passes E-102 to the absorber (D-010), 0.34 % leaves with the co-product POCl3 and
0.08 % with the heel's purge; the product S17 holds 77.16 % of theory on the oxalic acid. The crude S13 holds 20.4 wt% oxalyl
chloride (SRC-1: 21.9 wt%).
Reason: the crude's assay is the measured quantity closest to what the reactions form; the
isolated yield also holds the examples' losses, which this plant has its own of.
Assumptions: the yield, 77.2 %, is a model result below SRC-1's isolated 84.2 %: an upper bound
for this plant only in so far as the losses not modelled (the vacuum pump, the vacuum break,
D-010) lower it by about 1.2 %.

## D-007 The strip ST101 at 15 kPa(a) (2026-11-13)
Decision: after R102, R-101 is put under 15 kPa(a) and the crude distilled off the heel to the
receiver T-201 through the chilled-water condenser E-103 (a batch still, ADR 0055, one stage,
`heat_up: true`), until oxalyl chloride is 0.5 mol% of the residue; then the vacuum is broken
with nitrogen and 5 % of the heel purged. Boil-up 80 kW from R-101's hot-water loop (ASSUMED:
U 300 W/(m2 K), about 15 m2 at a mean driving force of about 18 K). Result (`cheme process
stills`): 7753 kg of crude a batch at 20.4 wt% oxalyl chloride, 6.19 h, 494.8 kWh; the still
from 318.06 to 337.22 K.
Reason: core counts the suspended PCl5 and the catalyst in the still's liquid (Raoult over all
of it, L-1), which raises its bubble points: at 25 kPa(a) (SRC-1's 250 mbar) the still ends at
352.8 K, above the hot-water loop's 350.65 K, so the strip could not finish. At 15 kPa(a) it ends
13.4 K below the loop.
What the model leaves out: R102's mass enters at 333.15 K, 15.1 K above its bubble point at
15 kPa(a); core does not model that flash (no heat-up, and no credit). The heat above the bubble
point, 2.81 kW year average, evaporates part of the crude for nothing, so Q5 and Q6 (24.40 kW
each) are upper bounds by about 12 % (scripts/balance.py prints it, L-4).
Assumptions: an ideal liquid (no VLE data); oxalyl chloride's vapour pressure a
Clausius-Clapeyron line through its boiling point with NIST's 32 kJ/mol, ASSUMED (SRC-6; it
gives 18.6 kPa at 293 K); PCl3's and chlorine's lines used slightly beyond their ranges (core
notes them).

## D-008 Rectification ST201 with its column K-201 (2026-11-13)
Decision: a batch still at 101.325 kPa(a) with a column of 15 theoretical stages at a constant
reflux ratio of 6 (`still.column`, ADR 0061), ASSUMED (SRC-1 states no column), two cuts: the
product overhead while its mean is at least 99.5 wt% oxalyl chloride, then an off-cut until 0.2
mol% oxalyl chloride is left in the POCl3; reboiler 150 kW on LP steam, `heat_up: true`.
Result (`cheme process stills`): product cut 1280.5 kg a batch at 99.50 wt% (0.44 wt% POCl3,
0.06 wt% PCl3), 80.6 % of the crude's oxalyl chloride, ending at 4.18 h; off-cut 1103.4 kg at
27.0 wt% oxalyl chloride, back to V-102; the still's POCl3 (5369 kg, 99.8 wt%, 0.17 wt% oxalyl
chloride) cooled in the still (E202), 36 % to V-102 and 64 % the co-product (SP201). Reboiler
60.83 kW year average (the boil-up at reflux 6, 55.43 kW, and the charge's heat-up from its
309.4 K bubble point at 15 kPa(a) to 362.3 K, 5.40 kW), condenser 55.43 kW, 7.50 h of boil-up.
The two recycles (the off-cut and the POCl3 with the heel) are converged by core at the tears S3
and S13 (Wegstein, ADR 0060).
Rejected: a reflux raised to hold 99.8 mol% overhead (`constant_distillate`) up to a ratio of 6:
it stayed at 6 from the start to the end, the same column.
Assumptions: an ideal liquid; the off-cut's and POCl3's return change nothing but the dilution
of the acid slurry (D-004).

## D-009 Utilities and heat: every energy flow (2026-11-13)
Decision: utilities of the design basis, ASSUMED: LP steam 350 kPa(a) (412 K), cooling water
298/308 K, chilled water 278/283 K (above POCl3's melting point, 274.33 K, and oxalyl chloride's,
257.15 K, which condense on E-102 and E-103), R-101's hot-water loop at 353/348 K heated by LP
steam (its supply below R101's MTT, 360.72 K, and R102's, 367.16 K). C-201's jacket on LP steam:
it holds only oxalyl chloride and POCl3 (no reaction), so no stated limit applies.
Every energy stream and where its value comes from (year averages):

| stream | what | kW | from |
|---|---|---|---|
| Q1 | R101's charge warmed from its mixed 323.96 K to 333.15 K (hot-water loop) | 1.12 | scripts/balance.py |
| Q2 | R101 to cooling water | 41.45 | core's semi-batch model |
| Q3 | R102 to cooling water | 0.14 | core's semi-batch model (near balance, D-005) |
| Q4 | E-102 to chilled water (condensation 2.52, vapour cooled 0.69, gases cooled 0.61) | 3.81 | core's vent condenser (the gases' ideal-gas data in materials.yaml) |
| Q5, Q6 | the strip's heat in (hot-water loop) and E-103 to chilled water | 24.40 each | core's still model (upper bounds by 2.81 kW, D-007) |
| Q7 | C-201's reboiler (LP steam) | 60.83 | core's still model with its column |
| Q8 | K-201's condenser to cooling water | 55.43 | core's still model |
| Q9 | the product cut cooled from 336.73 to 303.15 K | 0.70 | scripts/balance.py |
| Q10 | the POCl3 cooled in C-201 from 378.08 to 303.15 K | 4.99 | scripts/balance.py |
| Q11 | the absorber to cooling water | 24.64 | scripts/balance.py (D-010) |
| P1, P2, P3 | agitators, the vacuum pump, pumps, the fan | 6.5, 2.0, 1.5 | ASSUMED |

Mixed temperatures from their inlets (scripts/balance.py): the charge S4 323.96 K (fresh PCl3 at
298.15 K on the heel at the strip's 337.22 K), the acid slurry S10 316.57 K (the acid at 298.15
K, the POCl3 at 303.15 K, the off-cut at its 358.49 K bubble point). Stream temperatures of the
stills are their bubble points as the still counts them (S13 309.38 K at 15 kPa(a), S14 337.22
K, S16 336.73 K, S18 378.08 K).
Recorded exclusions, each with its number: the ST101 flash (2.81 kW, D-007); the heel left in
R-101 at 337 K between batches, cooling to the charge's mixed temperature (counted in S4's
temperature, so not lost); the vessels' metal (no masses sourced; R-101's warming is 0.25 h,
C-201's heat-up 5.40 kW without it); the vacuum pump's and the vacuum break's vapour (about 1.2 %
of the product's oxalyl chloride, lca.yaml emission exclusions, D-010); V-102's slurry, mixed
without heat (no heat of suspension sourced).
Per kg of product: LP steam 1.368 kWh, cooling water 2.017 kWh removed, chilled water 0.447 kWh
removed, electricity 0.158 kWh.

## D-010 Vent, vent condenser, absorber and tail gas (2026-11-13)
Decision: R-101's one vent line through the vent condenser E-102 (chilled water, gas out at
283.15 K, 5 K above the supply) to the absorber A-101 (a falling-film absorber with a packed
tail scrubber), water to 30 wt% hydrochloric acid (ASSUMED); the oxalyl chloride and POCl3
vapour past E-102 hydrolysed in the water (A101: OXH, POH, conversion 1; SRC-4: oxalyl chloride
gives only HCl, CO and CO2 with water; SRC-7: POCl3 gives phosphoric acid and HCl); the tail
gas (CO, CO2, chlorine traces) to the site's thermal oxidiser with its caustic flue-gas
scrubber; D101 the specified split of the absorber's outlet (all HCl, phosphoric acid and water
to the acid, the gases to the tail).
Result: per batch 1297 kg of vent (26.0 kmol HCl, 1.95 kmol each of CO and CO2, 0.96 kmol
oxalyl chloride, 0.49 kmol POCl3, 0.14 kmol chlorine; `cheme process recipe`), peak 182 m3/h at
283 K in the first 14 min of the acid dosing; 2499 kg of water to 3575 kg of 30 wt% acid with
1.3 wt% phosphoric acid; absorber heat 24.64 kW (the hydrolyses 1.78 kW, the HCl's heat of
solution at an ASSUMED -63 kJ/mol to about 30 wt%, 25.38 kW, less 2.52 kW warming the water and
the gas to 313 K).
The vent passes 7.41 % of the acid's worth of oxalyl chloride (6.04 kg/h, 9.6 % of the product):
E-102 cannot go colder, since its condensate is mostly POCl3, which melts at 274.33 K and would
freeze on a brine-cooled wall. Recovering it (a second, colder condenser after a POCl3
knock-out, or a scrubber with chilled POCl3 that returns to V-102) is the first yield lever of
the next stage.
Not in the balance (lca.yaml emission exclusions, numbers there): the vacuum break's nitrogen
displaced through E-102 (about 3 kg of oxalyl chloride a batch), the vacuum pump's discharge
(about 13 kg a batch at an ASSUMED 1 kg/h air leak: a cold trap after the pump, to the
absorber), the tanks' breathing. PCl3 vapour in the vent: none (R101 leaves 0.1 % of it, below
the vapour components R102 carries).

## D-011 Thermal screening, the rate-constant sensitivity and the release cases (2026-11-13)
MTT (`hazard.mtt`, given by hand: core's default takes a pure component's boiling point, L-7):
the bubble point at 101.325 kPa(a), where the vented vessel boils, of R101's charge, 360.72 K
(its PCl3 turns into solid PCl5, so the charge's is the lowest), and of R102's final liquid,
367.16 K (the oxalyl chloride it forms is the most volatile); Raoult over the liquid with the
solids left out, which gives a lower (conservative) bubble point than the still's convention.
Result (`cheme process reactor-hazards`, core ADRs 0050, 0058, 0062, 0063):
- R101: dT_ad 293.0 K (48.5 K of it the chlorine's heat of solution, released as it dissolves,
  not accumulated); accumulation 0.96 % at the end of the dosing; MTSR 335.11 K, 25.6 K below
  the MTT.
- R102: dT_ad 28.18 K (OXC sets it; DEC alone 11.7 K, so `hazard.reactions` is not needed);
  accumulation 2.93 % at the end of the dosing; MTSR 333.98 K, 33.2 K below the MTT. Gas
  released at a cooling failure at the MTSR: 282.8 m3/h with the liquid's vapour (206.7 m3/h of
  non-condensables) at 334 K, 0.81 of R-101's vent capacity of 350 m3/h
  (`hazard.vent_capacity`: that release plus about 20 %, rounded up); the largest
  non-condensable release over the batch, core's `vent_gas_rate` along the cooling profile,
  208.0 m3/h at 2.01 h into the dosing.
No TD24 is known (never estimated): no criticality class (`cheme.reactor-hazard-missing`,
info). With the MTSR below the MTT in every case below, the class is 1 or 2 if the TD24 lies
above the MTSR (1 above the MTT, 2 between), and 5 if it lies below: core's `criticality()`
tests the TD24 against the MTSR first (SRC-9).
Sensitivity (scratch copies of the folder, every rate's A divided, everything else as designed;
`cheme process recipe`, `reactors`, `reactor-hazards` on the design inlets; not committed):

| k at 333 K | R101 accumulation, MTSR | R102 accumulation, MTSR | gas at R102's MTSR (non-condensables) | of 350 m3/h | largest non-condensable release over the batch | cycle | class without TD24 |
|---|---|---|---|---|---|---|---|
| design | 0.96 %, 335.11 K | 2.93 %, 333.98 K | 282.8 (206.7) m3/h | 0.81 | 208.0 m3/h at 2.01 h | 20.27 h | 1, 2 or 5 |
| k/10 | 2.57 %, 339.31 K | 20.0 %, 338.79 K | 339.3 (241.5) m3/h | 0.97 | 241.6 m3/h at 3.74 h | 28.47 h | 1, 2 or 5 |
| k/100 | 7.75 %, 353.16 K | 69.7 %, 352.80 K | 473.7 (321.5) m3/h | 1.35 | 321.5 m3/h at 4.0 h | 120.0 h | 1, 2 or 5 |

Design finding (k/100, `cheme.reactor-hazard-vent` warning on the scratch copy): a 100 times
slower acid reaction accumulates 70 % of the dosed acid; a cooling failure at the end of the
dosing then releases 474 m3/h of gas and vapour, 1.35 times the vent capacity, which would
pressurise R-101. The MTSRs stay 7.6 K (R101) and 14.4 K (R102) below the MTTs. The k/100 cycle,
120 h, already rules that plant out, but a slow start (an inhibited acid, a cold slurry) is the
same case. For the next stage: the acid dosing interlocked on the off-gas flow (no gas, no
dosing), reaction calorimetry with off-gas measurement (heat, its sign, accumulation, the gas
profile), the TD24 of the reaction mass and the heel, the vent line sized for the blocked and
the k/100 cases, a relief device for R-101.
Toxic gases and release cases (reasoning only; for the HAZOP of the next stage):
- (a) Water ingress into R-101 (a leak of the jacket's cooling or hot water, whose pressure is
  above the vessel's, wet acid, absorber water sucked back through the vent line when the HCl
  absorption pulls a vacuum). PCl5 + H2O -> POCl3 + 2 HCl gives 111 mol of HCl per kg of water,
  about 3.0 m3 at 333 K; with oxalyl chloride (CO, CO2 and 2 HCl per water) 222 mol, about 6.1
  m3 per kg. The vent's spare capacity, 67 m3/h above the release at the MTSR or 168 m3/h above
  the normal peak, passes about 11 to 28 kg/h of water reacting with oxalyl chloride (twice that
  with PCl5); a jacket leak or a suck-back can exceed it. Options: jacket-leak detection (the loop's conductivity) or a
  non-aqueous heat-transfer fluid on R-101; anti-suck-back protection on the vent line (a
  nitrogen-padded seal pot, a vacuum breaker on nitrogen); the acid's water content specified and
  checked.
- (b) Loss of the absorber's water while R102 doses: up to 182 m3/h of HCl with CO and the
  oxalyl chloride and POCl3 vapour to the tail gas line. The acid dosing should be interlocked on
  A-101's water flow and on HCl at its outlet.
- (c) Chlorine: R101 doses 1775 kg a batch; if it stops reacting (the catalyst missing, a cold
  charge) it accumulates dissolved and then bubbles through to the vent; the model has no
  chlorine solubility (L-2). The chlorine dosing should be interlocked on R-101's temperature
  rise and on chlorine at E-102's outlet; the absorber's water does not take chlorine (the tail
  gas line to the oxidiser's caustic scrubber).
- (d) CO: 1.95 kmol (55 kg) a batch from DEC and 0.96 kmol from the vented oxalyl chloride's
  hydrolysis leave in the tail gas, about half of it CO, about 35 m3/h at the vent's peak; the
  tail line closed to the oxidiser, CO detection in the building. Phosgene: SRC-1's prior art formed phosgene, SRC-1's route does not state it; CO and
  chlorine meet in the tail gas, so it must not pass activated carbon (which catalyses phosgene
  from them) and the oxidiser must take it. Oxalyl chloride itself is toxic by inhalation and
  corrosive (SRC-4), over ten times less acutely toxic than phosgene.
- (e) Loss of chilled water to E-102: the gas carries the full vapour off the 333 K liquid (0.13
  kmol/h oxalyl chloride and 0.21 kmol/h POCl3, year average) to the absorber, about 2.7 times the
  normal oxalyl chloride, hydrolysed to more HCl, CO and CO2 there. Chilled-water flow and E-102's
  outlet temperature should be interlocked with the acid dosing.
- (f) Failure of the hot-water loop's control: its supply is capped by design at 353 K, below
  both MTTs, so the loop cannot boil R-101's content; a steam valve failing open on the loop's
  exchanger must not let the loop exceed 358 K (a high-temperature trip on the loop's supply).
  C-201 on LP steam (412 K) holds no reacting mass.
Screening values only, not a reaction-hazard assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-13)
Decision: `cheme assess lca --write` per kg of the product cut from the flowsheet's year
averages. The chlorine is linked to chlor-alkali-1 (dry chlorine gas), the nitrogen consumable to
asu-1's gaseous nitrogen (`lca/mappings.yaml`), the LP steam counted as heat (kWh); every other
background is a gap with the activity it should connect to. The nitrogen per batch (15 Nm3, 18.8
kg, ASSUMED: R-101's vacuum break, the crude receiver's, the blankets of C-201 and the tanks) is
an `lca.yaml` consumable `per_batch` (core ADR 0053, library ADR 0035). No water rinse: the train
is kept dry.
Proxies (gaps, not links): PCl3 as acetyl-chloride-1 records it (P4 + 6 Cl2 -> 4 PCl3; white
phosphorus has no library producer; phosphorus-oxychloride-1 makes PCl3 only internally); oxalic
acid by nitric acid or air oxidation of carbohydrates, dried to the anhydrous acid (SRC-8;
nitric-acid-1 for its nitric acid); 2,4-dimethylpyridine a pyridine base (8.4 g per kg of
product, below the cut-off's 1 % of the input mass, kept as a gap). The heel purge goes to
hazardous-waste incineration and the tail gas to thermal oxidation, both treatment gaps.
Allocation: economic between the product, the POCl3 and the hydrochloric acid, written as shares
(lca.yaml `allocation`, agent proposal): 0.579, 0.389, 0.032. The library hierarchy
(docs/system-model.md) has no physical relationship here, so the WBCSD rule applies: the price
ratio of a fine acid chloride to merchant hydrochloric acid is well above 5, so it gives
economic allocation. No prices are sourced: the relative prices per kg 1 : 0.25 : 0.02 are
ASSUMED. The conservative bound is all burdens to the oxalyl chloride; mass allocation would
leave it 15.4 % (63.13 of 408.82 kg/h of products). A test keeps the shares equal to the
flowsheet's flows at those ratios.
Per kg of product, unallocated: PCl3 2.672 kg (2.164 for 2 mol per mol, stoichiometric), chlorine 1.386 kg, oxalic acid 0.915 kg (0.709 stoichiometric), catalyst 8.4 g, process
water 1.951 kg, nitrogen 14.7 g, electricity 0.158 kWh, LP steam 1.368 kWh, cooling water 2.017
kWh removed, chilled water 0.447 kWh removed; out: POCl3 2.683 kg, hydrochloric acid 30 wt%
2.792 kg, heel purge 0.285 kg, tail gas 0.172 kg (0.064 kg CO, 0.100 kg CO2, 0.008 kg chlorine).
Not counted: the vacuum pump's and the vacuum break's vapours and the tanks' breathing
(`emission_exclusions`, D-010).

## D-013 Dedicated train (2026-11-12)
Decision: R-101, V-102, E-102, E-103, C-201, K-201 and A-101 make only oxalyl chloride, batch
after batch: 390.7 batches in 7920 h (ASSUMED, library ADR 0035). The heel stays in R-101 from
batch to batch.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| the heel and POCl3/off-cut recycles | done in cheme (tears S3, S13, Wegstein) | D-004, D-008, core ADR 0060 |
| semi-batches R101 and R102: composition, accumulation, MTSR, peak cooling, duties Q2, Q3 | done in cheme, kinetics ASSUMED | D-005, D-011, core ADRs 0050, 0059, 0063 |
| R102's vent with the liquid's vapour and the vent condenser E-102 (Q4) | done in cheme, ideal liquid ASSUMED | D-005, D-010, core ADRs 0054, 0062 |
| gas release at the MTSR and over the batch against the vent capacity | done in cheme, vent capacity ASSUMED; k/100 above it a design finding | D-011, core ADR 0058 |
| batch recipe, cycle, basis check, R-101's vessel and R102's jacket check | done in cheme | D-003, core ADRs 0051, 0052, 0057 |
| R101's jacket check | by hand (in the tests with core's `wetted_area`) | D-003, L-5 |
| strip ST101 (Q5, Q6) and rectification ST201 with its column (Q7, Q8) | done in cheme (Rayleigh; Diwekar's shortcut), ideal liquid ASSUMED | D-007, D-008, core ADRs 0055, 0061, 0063 |
| absorber hydrolysis | done in cheme (conversion step), heats in the script | D-010 |
| feeds for 500 t/a, the absorber's water and split, temperatures, Q1, Q9, Q10, Q11, the MTTs | script | D-004, D-009, D-010, D-011 |
| per-batch nitrogen | done in cheme, amount ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core features used (core 1.11.0)

- `reactor: semibatch` with `batch.dosing`, `batch.target`, `heat: isothermal` (ADR 0050) for
  both reactions; the chlorine as a dosed gas taken up (`absorbed: 1.0`) with its
  `heat_of_solution` (ADR 0063).
- `batch.vent` with HCl, CO and CO2 (ADR 0054), `vent.vapour` with oxalyl chloride, POCl3 and
  chlorine and `vent.condenser` returning to the vessel on its own energy stream Q4 (ADR 0062),
  with the gases' `ideal_gas` data so the condenser's duty counts their cooling.
- `hazard.mtt` and `hazard.vent_capacity` (ADR 0058): `cheme process reactor-hazards` with the
  MTSR over the batch, per reaction, the gas release at the MTSR with the liquid's vapour, and
  `stirred_tank.vent_gas_rate` over the cooling profile for the largest release.
- `energy_port` on both semi-batches and both stills: the models write Q2 to Q8 `calculated`
  (ADR 0059); `still.condenser_port` for E-103 and K-201's condenser.
- `still:` (ADR 0055) for the strip at 15 kPa(a) with `nonvolatile` and `heat_up`, and
  `still.column` (ADR 0061) with `reflux: constant`, `ratio: 6`, `stages: 15` and two `cuts`
  (a `purity` end on a mass basis and a `residue` end) for the rectification.
- `tears:` with Wegstein `convergence` (ADR 0060) for the heel and the POCl3/off-cut recycles.
- `process/recipe.yaml` (ADRs 0051, 0052, 0057): `units` over several steps, `dose`/`react`
  `from:` R101 and R102, `distil from:` ST101 and ST201, a `heat` operation with `temperatures`,
  vessel sizing and the jacket check at the cooling water's log-mean temperature.
- A conversion step for the absorber's hydrolysis; `lca.yaml` `consumables` with `per_batch`
  (ADR 0053), `allocation: shares`, `emission_exclusions`.
- Not used: `batch.heat_up` (the charge is warmed on its own step E101 by the hot-water loop,
  Q1, while R101's duty goes to cooling water: one net model duty would mix the two);
  `vessel.metal_heat_capacity` (no vessel masses sourced, D-009); `vent.henry` (no Henry constant
  of HCl, CO or chlorine in POCl3, L-2); `hazard.reactions` (every reaction counts, the default);
  `reflux: constant_distillate` (tried, it stayed at its cap, D-008); the crystallizer, the
  filter and the dryer (no solids leave the plant).

## Core limits hit (each a candidate core issue)

- L-1: solids and boiling in a batch. The suspended PCl5 and acid are pseudo-homogeneous in the
  semi-batch (their rates and volumes as if dissolved), and the batch still counts the suspended
  PCl5 in its Raoult liquid, which raises its bubble points (at 25 kPa(a) the strip would end at
  352.8 K instead of about 338 K with the solids left out); a solid phase that does not dilute the
  liquid would let the strip run at SRC-1's 250 mbar. A reacting semi-batch that boils (SRC-1's
  reaction at 250 mbar with the crude distilling off) is refused (ADR 0062), so reaction and strip
  are sequential (D-001, D-007).
- L-2: no solubility data for the vented gases: all HCl, CO and CO2 leave as they form
  (`vent.henry` needs a Henry constant none of which was found for POCl3), and the chlorine of
  R101 is taken up entirely (`absorbed: 1.0`); a chlorine that accumulates undissolved, or
  degasses at a cooling failure, is outside the screening (D-011 case c).
- L-3: a semi-batch asks a liquid molar volume and heat capacity of every component its charge
  lists, even at zero: HCl, CO and CO2 carry placeholder liquid data (materials.yaml) because the
  recycled heel lists them at 0.
- L-4: the still neither credits nor heats a charge that enters above its bubble point (ST101:
  2.81 kW, Q5 and Q6 upper bounds, D-007); it extrapolates PCl3's and chlorine's Antoine lines a
  little beyond their ranges (a note); it does not size its vessel, jacket, column or condenser.
- L-5: a recipe vessel over two semi-batch steps is refused (ADR 0057): R-101 is sized and its
  jacket checked from R102; R101's jacket check, which set the 8 h dosing, is by hand (D-003, a
  test with core's `wetted_area`). A vessel that takes the largest volume and checks each step's
  peak would remove it.
- L-6 (as acetyl-chloride-1's L-7): core propagates from the feeds and cannot solve them for a
  product rate, and the batch size and the cycle depend on each other through the strip; both
  were iterated by hand (propagate, the script, the recipe, again; each propagate about 4 to 6
  minutes with the two tears).
- L-7 (as acetyl-chloride-1's L-5): the default MTT is the lowest pure-component boiling point
  of what boils in the liquid; for R102 that would be oxalyl chloride's 336.65 K, while the
  mixture boils at 367.16 K; `hazard.mtt` is given by hand as the bubble point (D-011).
- L-8: a semi-batch has one `heat_of_reaction` per reaction; SRC-2's endothermic and exothermic
  stages of the solid-solid reaction, and the PCl5's heat of dissolution, have no term.

## Open inputs
Kinetics, heat and sign of both reactions by reaction calorimetry with off-gas measurement; the
TD24 of the reaction mass and of the heel; the solubility of chlorine, HCl and PCl5 in POCl3; VLE
of oxalyl chloride with POCl3 and PCl3 (it sets the column's stages and reflux); the product's
specification; the recovery of the vented oxalyl chloride (D-010); the masses of R-101 and C-201
for their metal's heat; prices for the allocation; a TEA (`operation.batch: {recipe: true}`);
R-101's relief device and blocked-vent case, the vent line for the k/100 case, the water and
chlorine cases (D-011).
