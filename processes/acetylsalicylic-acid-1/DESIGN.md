# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Acetylsalicylic acid (aspirin) from salicylic acid and acetic anhydride, issue
ChemE-as-Code/process-library#476, a batch entry of the library. Concept stage: design basis,
batch recipe, balanced BFD/PFD, thermal screening with a rate-constant sensitivity and a
preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` with the core pin 0e85885 (cheme-as-code 1.12.0 with
the QSDsan worker). The entry uses core's semi-batch (core ADR 0050), the crystallizer with
spectators (ADR 0056), the filter-dryer's filters and dryer and recipe units over several steps
(ADR 0057), the batch still (ADRs 0055, 0063), the models' duties on their energy streams (ADR
0059), recycle tears (ADR 0060), the batch recipe (ADRs 0051, 0052) and the thermal screening
(ADR 0058). Library ADR 0035: one dedicated train, campaigns out of scope (D-013). Templates:
`methyltriphenylphosphonium-bromide-1` (crystallisation, filter-dryer, solvent still, tears) and
`oxalyl-chloride-1` (depth of the batch entry). Requires cheme-as-code 1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (Google Patents machine text; NIST WebBook and PubChem pages; the data packaged in
the `chemicals` Python package).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 2 731 492 A, J. Kamlet, filed 1954-04-29, published 1956-01-17: Process for the manufacture of acetylsalicylic acid, https://patents.google.com/patent/US2731492A/en | description: salicylic acid with at least an equimolar amount of acetic anhydride in a diluent (glacial acetic acid preferred; benzene, toluene, xylenes and others named) at 50 to 120 C, preferably 85 to 95 C, about 0.5 h with a catalyst or up to 24 h without; catalysts sulfuric acid, alkyl- or arylsulfonic acids, POCl3 or tertiary amines, good yields also without; cooled to 0 to 50 C (preferably 0 to 25 C), slow cooling giving larger crystals; filtered or centrifuged; the mother liquor's acetic acid turned back into anhydride with ketene and the liquor recycled. Example I: 1382 kg salicylic acid added to the recycled liquor in a 6000 L enamelled reactor, 90 to 92 C reached in about 0.5 h and held about 1 h, cooled quickly to 15 to 25 C; the filtrate holds 180 to 451 kg aspirin, 1800 kg acetic acid and 4.0 kg sulfuric acid (66 Be); the cake washed with water and dried in warm air at 60 to 70 C. Example II: toluene diluent without catalyst, 20 h at 88 to 92 C, cooled over 3 to 4 days | read (Google Patents); patent, facts only | D-001, D-003, D-004, D-005, D-007 |
| SRC-2 | US 2 987 539 A, W. C. Stoesser, W. R. Surine (The Dow Chemical Company), filed 1957-10-10, published 1961-06-06: Process for the production of aspirin, https://patents.google.com/patent/US2987539A/en | claims: salicylic acid with an excess of acetic anhydride and acetic acid at about 70 to 100 C, crystallised, washed with acetic acid and then water; 30 to 70 % of the combined mother liquor and acid washes returned to the first reactor, the rest reacted with more salicylic acid in a second reactor and then distilled. Example, Step 1: 552 g salicylic acid, 572 g acetic anhydride and 240 g glacial acetic acid heated over about 1 h to 85 C and held 1.5 h, seeded, crystallisation starting at about 77 C, cooled to 15 C; Step 2: 53 % of Step 1's filtrate and washings returned; Step 5: the second mother liquor and washes distilled to a pot temperature of 154 C at 35 mm Hg, distillate 96.5 % acetic acid and 3.5 % anhydride (reused for the cake wash), the residue hydrolysed to recover salicylic acid; overall 88 % of tablet-grade aspirin on the salicylic acid, 93 % with the recovery; no catalyst | read (Google Patents); patent, facts only | D-001, D-005, D-006, D-008, D-009 |
| SRC-3 | US 6 278 014 B1, E. Handal-Vega, A. P. D. Loupy, J. M. Collazo Garcia, published 2001-08-21: Synthetic procedure for the manufacture of aspirin, https://patents.google.com/patent/US6278014B1/en | background: the industrial method described as salicylic acid with excess acetic anhydride in a pressure reactor at 98 C for 2 to 3 h, cooled to about 0 C to crystallise, centrifuged and washed, about 90 % yield; prior art with sulfuric acid (1901) and acetic acid solvent at 90 C cooled to 20 C (1936); the invention: stoichiometric anhydride with CaO or ZnO, no solvent, the product about 30 % calcium acetate | read (Google Patents); patent, facts only | D-001 |
| SRC-4 | US 7 544 831 B2 and US 1 604 472 A (search results only: solid acid catalysts with a water quench; an older route criticised for its fractional crystallisation) | - | not read beyond the search snippets: not used as a source for any number | route lead only, D-001 |
| SRC-5 | NIST Chemistry WebBook, SRD 69: acetic acid (C64197), acetic anhydride (C108247), salicylic acid (C69727), aspirin (C50782), water (C7732185), https://webbook.nist.gov/chemistry/ | formation enthalpies (kJ/mol): acetic acid (l) -483.52 (Steele et al. 1997), acetic anhydride (l) -625.0 (Guthrie 1974 reanalysed by Pedley et al.), water (l) -285.83 (CODATA), salicylic acid (s) -589.7 (Colomina et al. 1980; not used in the arithmetic); aspirin's heat of hydrolysis, solid phase, -27.2 kJ/mol (Nelander 1964); liquid heat capacities acetic acid 123.1 J/(mol K) at 298.15 K, acetic anhydride 168.2 at 303.2 K, salicylic acid (s) 160.9 at 298.15 K; Antoine parameters acetic acid 4.68206 / 1642.54 / -39.764 (290.26 to 391.01 K) and acetic anhydride 4.24655 / 1427.77 / -75.113 (335.99 to 412.57 K), both McDonald, Shrader et al. (1959); boiling points acetic acid 391.2 K, acetic anhydride 412 K; melting points acetic acid 289.6 K, salicylic acid 432 K, aspirin 405 K (average of 103 values); heats of vaporization acetic acid 23.7 kJ/mol at 391.1 K (Majer and Svoboda 1985), acetic anhydride 44.2 kJ/mol at 351 K | read (HTML pages fetched 2026-11-19); facts only | materials, reactions, D-005, D-009, D-010 |
| SRC-6 | The `chemicals` 1.5.2 package (core's environment): its packaged CRC Handbook tables (`miscdata.CRC_organic_data`, `CRC_inorganic_data`) and its `Tb` | densities: acetic acid 1044.6, acetic anhydride 1082.2, salicylic acid (solid) 1443.2, sulfuric acid 1830.2 kg/m3; no density of aspirin; boiling points salicylic acid 529.0 K, sulfuric acid 610.15 K | open-source package queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). The printed (licensed) handbook was not read | materials |
| SRC-7 | PubChem CIDs 2244 (aspirin) and 338 (salicylic acid), PUG REST; NIST WebBook InChIKeys | identity (formula, InChIKey, ChEBI cross-references CHEBI:15365 and CHEBI:16914) | read (PUG REST, 2026-11-19) | registry |
| SRC-8 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and the criticality classes of a semi-batch (method, implemented in core ADR 0050) | method reference, no data taken | D-011 |
| SRC-9 | processes/acetic-anhydride-1, sulfuric-acid-1, asu-1, acetic-acid-1, cumene-1, chlor-alkali-1 (this library) | acetic anhydride by the ketene route (its feed is acetic acid); sulfuric acid 98.5 wt%; gaseous nitrogen; phenol and sodium hydroxide for the salicylic acid proxy | library, internal | D-004, D-012 |

Searched and not found openly (2026-11-19): kinetics or calorimetry of the sulfuric-acid
catalysed acetylation of salicylic acid in acetic acid, a TD24 of aspirin in the liquor, a
measured solubility of aspirin in acetic acid over temperature, cake and filtration data of
aspirin, and an open product specification (a pharmacopoeia monograph is not open). Each is an
ASSUMED value below, named as such.

## D-001 Route and boundary (2026-11-19)

**Decided.** Aspirin by the acetylation of salicylic acid with acetic anhydride in an acetic-acid
diluent with a small sulfuric acid charge (SRC-1, Example I), the acetic anhydride dosed into the
salicylic acid at 358 K (D-005), crystallisation by cooling in the same vessel, an agitated
filter-dryer with a reslurry wash in recovered acetic acid, 60 % of the combined liquors returned
to the next charge as in SRC-2's claims, and the rest distilled in a vacuum batch still. The
boundary is the plant gate: salicylic acid, acetic anhydride and sulfuric acid are bought (feeds,
D-004); the recovered acetic acid leaves as a co-product to the acetic anhydride plant, which uses
acetic acid as its feed (`acetic-anhydride-1`); the still residue goes to incineration. Packing
and a recrystallisation to a particular pharmacopoeia grade are outside the boundary.

**Why.** The acetylation in acetic acid is the route both process patents describe at plant scale
(SRC-1: a 6000 L enamelled reactor; SRC-2: a mother-liquor recycle with a distillation) and SRC-3
names as the industrial method. Acetic acid is the reaction's own co-product, so the liquor needs
no foreign solvent, and its recovery closes the acid loop with the anhydride plant.

**Rejected.**
- *All reactants charged and heated together* (SRC-1, SRC-2, SRC-3's description of the
  industrial practice): the screening (D-011) gives an all-in batch an MTSR of about 404.8 K,
  above the boiling point of the acetic acid mass (391.2 K); dosing the anhydride keeps the MTSR at
  365.5 K. The patents' small scale or their reflux condensers may tolerate the all-in charge; a
  concept design without calorimetry should not.
- *Ketene treatment of the mother liquor* (SRC-1): it turns the liquor's acetic acid back into
  anhydride inside the aspirin plant, with a ketene generator (acetone or acetic acid pyrolysis)
  on site. The library already has the ketene route as `acetic-anhydride-1`, so the acid goes there
  instead; the aspirin plant stays a fine-chemical batch train.
- *No catalyst* (SRC-2): the uncatalysed reaction needs hours at 85 C (SRC-1: up to 24 h); a
  dosing semi-batch then accumulates most of the anhydride (D-011, the k/100 case). The task's
  scope names an acid catalyst; sulfuric acid is SRC-1's first-named one.
- *A toluene or aromatic diluent* (SRC-1, Example II): 20 h of reaction and 3 to 4 days of slow
  cooling, and a second solvent to recover.
- *Solvent-free with CaO or ZnO* (SRC-3): the product holds about 30 % calcium acetate, not a
  pure active.
- *Solid acid catalysts with a water quench* (SRC-4, not read): water hydrolyses the excess
  anhydride and dilutes the acid, which then needs a water-acetic acid separation; not assessed.
- *A water wash of the cake* (SRC-1, SRC-2): it removes the sulfuric acid better but makes an
  aqueous acetic acid stream that needs its own recovery or treatment, and wets an ester that
  hydrolyses; the acid wash alone gives 0.018 wt% sulfuric acid in the product (D-008), a
  decision for the product specification, open (Open inputs).
- *Salicylic acid recovery from the still residue* (SRC-2, Step 5: hydrolysis with caustic and
  reacidification): it raises the yield by about 5 points, but needs a caustic hydrolysis, an
  acidification and a second filtration; left out of the concept (D-009), an improvement for later.

**Family.** The taxonomy has no pharmaceutical family; `oxygenates` (oxygenated organic
intermediates, ISIC 2011) is the nearest. The LCI dataset is classified ISIC 2100
(pharmaceuticals).

## D-002 Capacity, product and operating hours (2026-11-19)

1171 t/a of dried aspirin in 7920 h (330 days of 24 h), ASSUMED: what one 5 m3 reactor and one
5 m3 filter-dryer make at the recipe's cycle (D-003); no open market figure was used. The batch
is SRC-1 Example I's charge, 10.0 kmol salicylic acid. The product is modelled 99.85 wt% aspirin
(97.20 wt% crystals and 2.65 wt% the aspirin dissolved in the cake liquor that the dryer leaves
behind), 0.037 wt% salicylic acid, 0.018 wt% sulfuric acid and 0.10 wt% acetic acid and
anhydride; a model result, not a pharmacopoeia release (no open specification read).

## D-003 Batch basis, recipe and vessels (2026-11-19)

`process/recipe.yaml`: one batch makes 1710.65 kg of dried aspirin (stream S15). Three unit
procedures, each one vessel over several steps (core ADR 0057):

- REACT, R-101 (M101, E101, R101, CR101): receive the liquor 0.5 h and charge the salicylic acid
  and catalyst 0.75 h (ASSUMED), heat to 358 K on the jacket (2.01 h, core's recipe from the
  jacket with the vessel's metal), dose 1.5 h and post-react 0.99 h (from R101's model), cool to
  293 K (2.17 h), hold 1 h, transfer 0.5 h: 9.41 h.
- ISOLATE, F-101 (F101, W101, F102, D101): receive 0.5 h, filter 1.82 h and refilter 0.70 h
  (Ruth, D-008), reslurry 0.5 h, dry 7.05 h (D101's rate on 16 m2), discharge 1 h: 11.57 h, the
  bottleneck.
- RECOVER, C-301 (ST101, X301): receive 0.5 h, heat-up 0.245 h (hand arithmetic, L-5), boil-up
  0.48 h (ST101's model), drain 0.5 h: 1.72 h.

Cycle 11.5655 h, 684.8 batches a year, one batch takes 21.19 h. The recipe sizes R-101 at 5 m3
(3.29 m3 of batch, 66 % full) and checks its jacket: 168.5 kW at the charge against the semi-
batch's peak 159.5 kW. F-101 is 5 m3 and C-301 2 m3. The flowsheet's flows are the recipe's year
averages: the fresh feeds are per-batch amounts over the cycle, set by hand to the recipe's cycle
until `cheme process recipe` reports no `cheme.recipe-basis` finding (147.909 kg/h by the recipe,
147.911 in the flowsheet). Every duration not from a model is ASSUMED.

## D-004 Feeds and charge (2026-11-19)

- Salicylic acid: 10.0 kmol (1381.22 kg) a batch, technical grade taken as pure (its phenol and
  4-hydroxybenzoic acid not modelled), charged as a solid through a closed charging station.
- Acetic anhydride: 1.05 mol per mol of salicylic acid fresh (1071.93 kg a batch, ASSUMED,
  between SRC-1's equimolar recycle and SRC-2's 1.4-fold first charge), `acetic-anhydride-1`'s
  99.5 wt% product taken as pure. With the anhydride the recycled liquor brings, R-101 sees 1.14
  mol per mol.
- Sulfuric acid: 1.5 kg a batch as a make-up for what leaves with the liquor purge and the
  product (ASSUMED; SRC-1 Example I holds 4.0 kg in its recycled liquor for the same 10 kmol
  charge; here the liquor brings 1.8 kg). Taken as 100 %.
- The acetic acid diluent is the recycled liquor itself (D-006); no fresh acetic acid is bought.

## D-005 Reactor R101: semi-batch, kinetics and heat (2026-11-19)

**Decided.** R101 is core's semi-batch (`reactor: semibatch`): the charge (salicylic acid in the
recycled liquor with the catalyst) at 358.15 K, the acetic anhydride dosed over 1.5 h, then the
post-reaction to 0.995 conversion of the salicylic acid, isothermal. 85 C is SRC-2's reaction
temperature, inside SRC-1's 85 to 95 C. R-101 is open to its reflux condenser and the vent; no gas
forms.

**Heat of reaction**, -29.01 kJ/mol, by Hess's law on SRC-5's data (our arithmetic): the
hydrolysis of acetic anhydride, 2 x (-483.52) - (-625.0) - (-285.83) = -56.21 kJ/mol, less
aspirin's measured heat of hydrolysis in the solid phase, -27.2 kJ/mol: solid salicylic acid and
liquid anhydride to solid aspirin and liquid acetic acid. The heats of solution of the two acids
in the liquor are taken as equal and opposite (ASSUMED), so the same value stands for the
dissolved acids and CR101 adds no heat of crystallisation.

**Kinetics**, ASSUMED: second order, first in salicylic acid and in acetic anhydride, k 1.54e-3
m3/(kmol s) at 358.15 K, Ea 60 kJ/mol. No open kinetics were found. The value is set so that the
dosing is dosing-controlled (at most 19.5 % of the dosed anhydride accumulated) and so that the
start, when the recycled liquor's anhydride meets the whole salicylic acid charge, stays inside
R-101's jacket (159.5 kW against 168.5 kW). A 6.7 times faster rate (k 1.03e-2, as SRC-1's "about 0.5
h with a catalyst" would suggest for an all-in batch) gives a 1005 kW peak at the start, beyond
any jacket of this vessel: the reason for the slower assumption, and a finding for calorimetry
(what the recycled anhydride does while the charge heats is not modelled: core's semi-batch starts
at the dosing temperature, L-1). D-011 screens k/10 and k/100.

**Salicylic acid as a dissolved component.** The charge holds 48 wt% salicylic acid; at 358 K
part of it is suspended. Core's semi-batch is liquid only, so it is carried dissolved, and its
dissolution (rate and heat) is not modelled (L-1).

## D-006 The recycles and their tears (2026-11-19)

Two loops: the mother liquor S3 (X201 -> M101 -> R101 -> CR101 -> F101 -> M201 -> X201) and the
recovered acid to the cake wash S11 (X301 -> W101 -> F102 -> M201 -> X201 -> M202 -> ST101 ->
X301). Both are torn (`tears:`, core ADR 0060) and converged by `cheme process propagate` with
Wegstein's method (17 iterations, residual below 1e-6 kg/h). X201 returns 60 % of the combined
mother liquor and wash filtrate to the next charge (SRC-2: 30 to 70 %, ASSUMED the upper part of
the range for the yield); the rest goes to the still, purging the excess anhydride, the
unreacted salicylic acid and the catalyst. S11's flow is the wash ratio (D-008) and stays fixed;
X301's other outlet, the acid co-product S23, is the remainder. In steady state the charge holds 0.90
kg of acetic acid per kg of salicylic acid (1.33 kg after the reaction); the slurry is 44 wt%
crystals, about as thick as SRC-1 Example I's (about 1.8 t of aspirin with 1.8 t of acid).

## D-007 Crystallisation CR101 and the solubility (2026-11-19)

**Decided.** CR101 is core's crystallizer with spectators (core ADR 0056): aspirin from the liquor
in R-101 by cooling to 293.15 K, the acetic anhydride, salicylic acid and sulfuric acid carried as
spectators; a 1 h hold (ASSUMED).

**Solubility**, 0.0998 kg of aspirin per kg of solute-free liquor (`measured_in: mother_liquor`),
derived from SRC-1 Example I: after cooling to 15 to 25 C its filtrate holds 180 to 451 kg of
aspirin with 1800 kg of acetic acid and 4.0 kg of sulfuric acid; the lower end, 180 / 1804, is
taken at 293 K. The liquor here also holds 6.8 wt% acetic anhydride and 0.3 wt% salicylic acid,
taken to change nothing (ASSUMED; no salting-out data). The same value is used in the reslurry
wash W101 at 296.35 K, inside the example's range. The value has no temperature dependence (L-2).

**Liquor freezing.** Acetic acid melts at 289.6 K (SRC-5); the liquor, with 9 wt% aspirin and
7 wt% anhydride dissolved, freezes lower, but R-101's jacket at 283/288 K could crust at the wall
(L-6). The tempered water is held above 283 K for this reason; a lower end temperature would
recover more aspirin but needs the liquor's freezing point measured (Open inputs).

## D-008 Filter-dryer F-101: filtration, wash, drying (2026-11-19)

One agitated filter-dryer (one recipe vessel over F101, W101, F102, D101; core ADR 0057), all
values ASSUMED unless noted:

- Filters F101 and F102: every crystal retained (the fines through the cloth dissolve in the next
  charge and are not modelled), 0.3 kg of liquor per kg of crystals in the cake; Ruth's
  filtration time with a specific cake resistance of 5e9 m/kg, a medium resistance of 1e10 1/m,
  200 kPa of nitrogen and the liquor's 1.4 mPa s (no open data for any of them): 1.82 h and 0.70 h.
- Wash W101: a reslurry in recovered acetic acid, 0.4 kg per kg of crystals (SRC-2's Step 3
  washed with about 0.19 kg per kg; a little more taken for the catalyst); the slurry's
  temperature the adiabatic mix, 296.35 K. At the liquor's solubility the wash dissolves 4.0 % of
  the crystals, which go back with the filtrate (60 % to the next charge). A displacement wash
  would dissolve less but is not modelled (L-3). SRC-1 and SRC-2 finish with a water wash: not
  taken (D-001).
- Dryer D101: core's dryer to 0.1 wt% acetic acid at 333.15 K and 10 kPa(a) (acetic acid boils at
  329 K at 10 kPa(a) by SRC-5's Antoine set, so the vacuum dries at 333 K), 4 kg/(m2 h) on 16 m2
  of heated jacket, bottom and agitator (7.05 h), the wet cake's 1.328 kJ/(kg K) from the
  components' heat capacities, the latent heats of materials.yaml, F-101's metal 5000 kJ/K heated
  each batch, 70 % efficiency: 16.08 kW year average (Q4).
- The vapour is condensed on cooling water (E-201, a pass-through E201; its dew point at 10 kPa(a),
  about 329 K, lies above the cooling water's return); its vacuum-pump losses are not modelled
  (L-7). The product and F-101 cool to 313 K and the cake's temperature on cooling water (Q8).

## D-009 Vacuum still C-301 and the recovered acid (2026-11-19)

ST101 is core's batch (Rayleigh) still at 15 kPa(a): the liquor purge and the dryer condensate
(1436.8 kg a batch) heated to the bubble point (`heat_up`, with C-301's metal 2500 kJ/K) and 90 %
of the charge's mass distilled with a 300 kW boil-up, Raoult's law with SRC-5's Antoine sets,
the ideal liquid ASSUMED (L-4); salicylic acid, aspirin and sulfuric acid non-volatile. The pot
runs from 339.2 to 355.3 K, inside both Antoine ranges and far below SRC-2's 154 C pot. The
distillate is 96.5 mol% (94.1 wt%) acetic acid with the anhydride, close to SRC-2's 96.5 %
acetic acid and 3.5 % anhydride. 692.8 kg of it a batch wash the next cake; the rest, 0.351 kg per
kg of aspirin, goes to the acetic anhydride plant (D-012). The residue (0.084 kg per kg; 62 wt%
aspirin, 23 wt% acetic acid, 13 wt% anhydride, 1.8 wt% salicylic acid, 0.8 wt% sulfuric acid) is
drained at 355 K to the waste tank and incinerated; 90 % was chosen to leave it a pumpable melt
(aspirin melts at 405 K). It carries 5.0 % of the salicylic acid as aspirin: the yield is 94.8 %
on the salicylic acid, against SRC-2's 88 % of tablet-grade aspirin (93 % with its salicylic acid
recovery, D-001).

## D-010 Utilities and heat: every energy flow (2026-11-19)

LP steam at 350 kPa(a) (hot water at 368 K for R-101, 353 K for F-101, and the still), cooling
water at 298/308 K, tempered chilled water at 283/288 K for R-101's jacket, all ASSUMED. Every
duty, year average:

| stream | what | kW | basis |
|---|---|---|---|
| Q1 | R-101 heat-up of the charge (295.60 to 358.15 K) and its metal (4000 kJ/K from 293.15 K) | 12.97 | hand arithmetic (L-5) |
| Q2 | heat of acetylation less the dose warmed, to tempered chilled water | 4.41 | R101's model (core ADR 0059) |
| Q3 | slurry and R-101 metal cooled to 293 K | 15.99 | CR101's model with the metal (ADR 0063) |
| Q4 | dryer heat | 16.08 | core's dryer model |
| Q5 | F-101 vacuum condenser | 4.96 | hand arithmetic |
| Q6 | still heat-up, metal and boil-up | 18.68 | ST101's model |
| Q7 | still condenser and distillate cooler | 15.10 | hand arithmetic |
| Q8 | product and F-101 metal cool-down | 5.36 | hand arithmetic |
| P1-P3 | agitators, dosing and vacuum pumps, transfer pumps | 10.5 | ASSUMED motor sizes and run times |

The mixers' temperatures (S4, S12, S18, S20) are adiabatic mixes on the components' heat
capacities; the salicylic acid's heat of solution in M101 is lumped into ACET (D-005). The test
file recomputes the hand values from the stream table.

## D-011 Thermal screening and the rate-constant sensitivity (2026-11-19)

`cheme process reactor-hazards` (core ADR 0058) on R101: dT_ad 46.6 K, the largest accumulation
19.5 % of the dosed anhydride at the end of the dosing, MTSR 365.5 K at the worst moment (1.28 h
into the dosing), against an MTT of 391.2 K, core's default: acetic acid's normal boiling point,
the mass being open to its reflux condenser. No TD24 is known (aspirin decomposes above its
melting point, but no open decomposition data in the liquor were found), so no criticality class
is given.

| rate | accumulation | MTSR | vs MTT 391.2 K | R-101 cycle |
|---|---|---|---|---|
| k (design) | 0.195 | 365.5 K | 25.7 K below | 9.41 h |
| k/10 | 0.471 | 380.4 K | 10.8 K below | 21.22 h, R-101 the bottleneck |
| k/100 | 0.871 | 400.6 K | 9.4 K above | 143.1 h |

The k/100 case stands for a batch without its catalyst (SRC-1: up to 24 h without, 0.5 h with):
the dosed anhydride then accumulates and a cooling failure boils the mass. **Design finding:** the
dosing is interlocked with the catalyst charge and with the reaction's heat flow (the jacket's
temperature difference), so that it stops when the anhydride does not react; the reflux condenser
must take the boil-up a cooling failure gives at the k/100 accumulation (to be sized at basic
engineering). An all-in batch (D-001, rejected) accumulates everything: MTSR about 358.15 + 46.6
= 404.8 K, above the MTT at any rate. The MTT holds for the liquid at 101 kPa; the screening does
not assess the decomposition of aspirin or the anhydride's reaction with water ingress (water
from a jacket leak hydrolyses the anhydride, -56.2 kJ/mol, D-005; to be covered in the HAZOP).

## D-012 Preliminary gate-to-gate LCI (2026-11-19)

`lca/lca.yaml`, per kg of dried aspirin, written by `cheme assess lca --write`. Linked:
acetic anhydride to `acetic-anhydride-1`, the sulfuric acid make-up to `sulfuric-acid-1`, the
nitrogen to `asu-1` and the LP steam as heat (lca/mappings.yaml). Gaps (never zero):

- Salicylic acid, 0.807 kg/kg: no library process makes it. Recorded proxy, not linked: the
  Kolbe-Schmitt stoichiometry C6H5OH + NaOH + CO2 + 1/2 H2SO4 -> C7H6O3 + 1/2 Na2SO4 + H2O, 0.681
  kg phenol (`cumene-1` makes phenol), 0.290 kg sodium hydroxide (`chlor-alkali-1`), 0.319 kg CO2
  and 0.355 kg sulfuric acid per kg (our arithmetic); the carboxylation's yield, energy and the
  sodium sulfate brine are not known openly, so a linked proxy would understate it. A shared
  estimate proxy (library ADR 0039) is for a separate change.
- Electricity, cooling water, tempered chilled water, the still residue's incineration and the
  nitrogen's passage through the scrubber.

Nitrogen per batch, 68.8 kg (about 55 Nm3: R-101 purged, F-101 pressed twice and its vacuum
broken, the tanks blanketed; ASSUMED), is a `per_batch` consumable (core ADR 0053). No rinse
between batches: the next batch's liquor takes up what stays in the vessels.

**Allocation.** Economic, as shares: aspirin 0.966, the recovered acetic acid 0.034, at ASSUMED
relative prices 1 : 0.1 per kg (147.911 x 1 against 51.904 x 0.1 kg/h). The library hierarchy has
no physical relationship between them, and the price ratio of a pharmaceutical active to a
recovered bulk acid is far above 5, so the WBCSD rule gives economic allocation; the bounds are
all burdens to the aspirin (share 1) and mass allocation (0.740). Sourced prices replace the
ratio. The acid holds 5.9 wt% anhydride, which the anhydride plant takes back with it.

## D-013 Dedicated train (2026-11-19)

Per library ADR 0035, the folder describes one dedicated train (R-101, F-101, T-201, C-301,
T-301 and E-201) making aspirin batch after batch all year. Aspirin is often made on such trains;
where it is made on a multipurpose plant, the changeover cleaning between products, the idle time
and shared tank farms are outside the boundary and not gaps.

## Method and dependency table

| result | method | inputs |
|---|---|---|
| R101 outlet, Q2, the cycle's dosing and post-reaction | core semi-batch (ADR 0050) | ACET's rate and heat (D-005), S5, S6 |
| CR101, W101 | crystallizers with spectators (ADR 0056) | solubility (D-007) |
| F101, F102 | specified splits, Ruth times (ADR 0057) | cake data (D-008) |
| D101, Q4, drying time | dryer to a residual moisture (ADR 0057) | D-008 |
| ST101, Q6 | Rayleigh still on Raoult's law with heat-up (ADRs 0055, 0063) | Antoine sets (SRC-5), D-009 |
| S3, S11 | recycle tears, Wegstein (ADR 0060) | X201's 0.6, the wash ratio |
| cycle, vessels, jacket check | batch recipe (ADRs 0051, 0052, 0057) | process/recipe.yaml |
| MTSR, MTT, accumulation | thermal screening (ADR 0058) | R101 |
| Q1, Q5, Q7, Q8, mixing temperatures | hand arithmetic | stream table, materials.yaml |

## Core features used (core 1.12.0)

Semi-batch with dosing and isothermal post-reaction to a target conversion; crystallizers with
spectators and a mother-liquor solubility; a crystallizer fed by the cake and the wash (the
reslurry); specified filters with Ruth's filtration time; the dryer with its energy and drying
time; the batch still with `heat_up` and the vessel's metal; recipe units over several steps,
vessel sizing and the jacket check; two recycle tears; the models' duties at `energy_port`;
`cheme process reactor-hazards` with the dosed reactant's accumulation over the batch.

## Core limits hit (each a candidate core issue)

- **L-1** The semi-batch is liquid only: the salicylic acid suspended in the charge is carried
  dissolved, with no dissolution rate or heat; the batch starts at the dosing temperature, so the
  reaction of the recycled anhydride during the heat-up is not modelled (it appears as the start
  peak instead).
- **L-2** One solubility value at one temperature: no solubility curve over temperature, so the
  cooling profile, the seeding and the crystal size are not modelled; liquor-measured data are
  taken at a composition the source states, not checked against the solved liquor (ADR 0056).
- **L-3** No displacement wash: the reslurry wash dissolves crystals to saturation (4 % here);
  a washing efficiency would lower the loss.
- **L-4** The still's Raoult's law takes the vapour as monomers: acetic acid's vapour association
  (which also makes its calorimetric heat of vaporization, 23.7 kJ/mol, half the Antoine slope's)
  is not modelled; the boil-up's duty uses the calorimetric value.
- **L-5** The recipe's heat-up report starts the vessel's metal at the charge's temperature, not
  where the last cool-down left it, so Q1 is by hand; the still's distil operation times the
  boil-up only, so its heat-up is an operation by hand (as methyltriphenylphosphonium-bromide-1's
  L-9).
- **L-6** One coolant temperature per jacket, and no wall temperature: the freezing of the
  acetic-acid liquor at a cold wall is not checked.
- **L-7** No condenser model with non-condensables: E-201's and C-301's condensers are total, the
  vacuum pumps' acid losses not estimated (an emission exclusion in lca.yaml).
- **L-8** The fresh feeds' per-batch amounts were set to the recipe's cycle by hand; a design
  specification (core ADR 0070) on the product rate was not used, since the cycle itself moves
  with the per-batch amounts through the filtration and drying times.

## Open inputs

- Reaction calorimetry of the catalysed acetylation in the recycled liquor (rate, heat,
  accumulation) and a TD24 of the mass: replaces D-005's ASSUMED kinetics and closes D-011.
- Aspirin's solubility in the liquor over 283 to 300 K, and the liquor's freezing point.
- Cake resistance, cake liquid and the drying rate from a filter-dryer trial.
- The product specification (free salicylic acid, sulfate, residual solvent, particle size):
  whether the acid wash suffices or a water wash or recrystallisation is needed.
- Prices for the allocation (D-012), and a source for the capacity.
