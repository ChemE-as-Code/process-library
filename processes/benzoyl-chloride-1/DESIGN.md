# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Benzoyl chloride from benzotrichloride and benzoic acid, issue
ChemE-as-Code/process-library#156, a batch entry of core#158. Concept stage: design basis,
batch recipe, balanced BFD/PFD, thermal screening with a rate-constant sensitivity and a
preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-05): library `main` at a8f53ee4 (core pin v1.8.0, 4e8fd80); cheme-as-code
1.8.0: `reactor: semibatch` with `batch.vent` (core ADRs 0050, 0054), the batch still `still:`
(ADR 0055), `process/recipe.yaml` with vessel, jacket and `distil from:` (ADRs 0051, 0052, 0055),
per-batch LCA consumables (ADR 0053). Library ADR 0035: one dedicated train, campaigns out of
scope (D-013).

Core pin v1.9.0 (2026-11-06, 314642c): the models write the duties of their energy streams
(core ADR 0059), so R101's Q2 and the still's net boil-up Q4 are now `calculated` by `cheme
process propagate --fill` and the reboiler's share for the column's reflux is its own stream Q6
(D-009); the semi-batch screening gives the MTSR over the batch and the HCl released at the
MTSR, against R-101's vent capacity (ADR 0058, D-014). Requires cheme-as-code 1.9 (plant.yaml).
No recycle is modelled (the residue's recycle is a variant, D-008), so the tears of ADR 0060 are
not used.

Core pin v1.10.0 (2026-11-06, c55e9c7): the still takes its column (`still.column`, Diwekar's
shortcut, ADR 0061), so K101's specified split, its return stream S12, the residue mixer M102
and the typed reflux share Q6 go, and the reboiler Q4 and the condenser Q5 are written by the
still's model; R101's vent carries the liquid's vapour through the reflux condenser E-102, whose
duty Q8 the vent model writes and whose condensate returns to R-101 (`batch.vent.vapour`,
`vent.condenser`, ADR 0062). The model disagreed with the hand values in two places, both
recorded: the column of D-008's old assumption (about 5 stages, reflux 1) sends 60 % of the
benzotrichloride into the product, not 2 %, so the column is now 15 stages at reflux 2; and the
gas released at the MTSR with the liquid's vapour, 107.2 m3/h, exceeds the 100 m3/h vent capacity
set for the HCl alone, so the off-gas system is sized for 130 m3/h (D-014, D-015). Requires
cheme-as-code 1.10 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine text; NIST WebBook and PubChem pages).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 4 276 231 A, W. Bockmann, K.-A. Lipper, F. Bruhne (Bayer AG), 1981: Process for preparing optionally substituted benzoyl chloride, https://patents.google.com/patent/US4276231A/en | description: catalysts (acids and metal halides, ZnCl2 and FeCl3 among the preferred, 0.005-10 wt% of the benzoyl chloride formed), 70-200 C (preferably 120-160 C), 0.8-2 bar, a 1-20 mol% (preferably 3-8 %) excess of acid or water, vacuum distillation at about 12-190 mbar; off-gas washed with benzotrichloride (and cold toluene) before absorption to very pure hydrochloric acid; bottoms of 20-70 % benzoyl chloride, 20-70 % benzoic acid and the catalyst, re-reacted with excess benzotrichloride; yields 96-98 % of theory, purity above 99.5 %. Example 1: 13.6 g ZnCl2 in 1832 g (15.0 mol) benzoic acid at 140 C, 2737 g (14.0 mol) benzotrichloride added over 2 h, held 2 h; crude with 3.5 wt% benzoic acid and anhydride; distilled at 50 mbar to 3805 g benzotrichloride-free product, 96.7 % of theory; off-gas washed with the 2737 g benzotrichloride gave about 30 % hydrochloric acid with 18 ppm organic carbon. Example 2 (water route, 3 % H2SO4 at 150 C): 92.6 %, 97.3 % with the bottoms re-reacted; 3255 g product and 210 g bottoms. Example 3: continuous, FeCl2, 97.9 % | read; patent, facts only | D-001, D-004, D-005, D-007, D-008, D-010, benchmarks |
| SRC-2 | NIST Chemistry WebBook, SRD 69: benzoyl chloride (C98884), benzotrichloride (C98077), benzoic acid (C65850) | Antoine constants (NIST fits to Stull 1947: benzoyl chloride 305-470 K, benzotrichloride 319-487 K, benzoic acid 369-522 K); heats of vaporization (benzoyl chloride 49.6 kJ/mol at 320 K, benzotrichloride 52.0 at 333 K, Stephenson and Malanowski 1987; benzoic acid 63.3 at 401-416 K, Pena et al. 2003); normal boiling points (benzoyl chloride 471 +/- 2 K, mean of 8; benzotrichloride 493.8 K; benzoic acid 522.2 K); liquid heat capacities (benzoyl chloride 187.0 J/(mol K), von Reis 1881; benzoic acid 259 at 413 K, Pacor 1967); benzoic acid's melting point 395.2 K and heat of fusion 18.0 kJ/mol (Ginnings and Furukawa 1953), solid cp 146.8 J/(mol K) at 298 K; formation enthalpies of liquid benzoyl chloride (-157.3 kJ/mol) and benzoic acid (-385 kJ/mol); none for benzotrichloride | read | materials.yaml, D-005, D-007, D-009 |
| SRC-3 | PubChem CIDs 7412 (benzoyl chloride), 7367 (benzotrichloride), 243 (benzoic acid), 5727 (zinc chloride) | identity (formula, InChIKey, ChEBI cross-reference); densities (HSDB): benzoyl chloride 1.2070 g/cm3 at 25 C, benzotrichloride 1.3756 at 20 C, benzoic acid 1.029 (liquid) at 180 C, ZnCl2 2.907 at 25 C | read (PUG REST, PUG View) | materials.yaml, chemicals registry |
| SRC-4 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and the criticality classes of a semi-batch (method, implemented in core ADR 0050) | method reference, no data taken | D-011 |
| SRC-5 | processes/asu-1 (this library) | gaseous nitrogen to the battery limit | library, internal | D-012 |
| SRC-6 | Ullmann's Encyclopedia of Industrial Chemistry, Benzoic Acid and Derivatives, doi:10.1002/14356007.a03_555 | - | not read (licensed); named by the route scouting as a lead that describes the same two variants | route lead only |
| SRC-7 | US 5 514 254, EP 0 612 707, US 3 816 287 (toluene side-chain chlorination to benzotrichloride) | - | not read in full; leads only | D-001 (boundary), lca.yaml gap text |
| SRC-8 | chemicals 1.5.2 (Caleb Bell, MIT licence), as packaged with cheme-as-code (`cheme chemistry thermo`) | HCl's ideal-gas data: formation enthalpy (ATcT), entropy (CRC), heat capacity polynomial (Poling et al., The Properties of Gases and Liquids, 5th ed.) | open-source package, facts only | materials.yaml, D-010 (E-102's gas cooling), scripts/balance.py (29.1 kJ/(kmol K)) |

Searched and not found openly (2026-11-05): kinetics or calorimetry of the benzotrichloride /
benzoic acid reaction, its heat of reaction (no formation enthalpy of benzotrichloride in the
NIST WebBook), a TD24 of the crude, the solubility of HCl in hot benzoyl chloride, vapour-liquid
equilibrium data of benzoyl chloride with benzoic acid, and a plant's specific consumptions.

## D-001 Route and boundary (2026-11-05)
Decision: the benzoic acid variant of SRC-1 (Example 1): C7H5Cl3 + C7H6O2 -> 2 C7H5ClO + HCl over
zinc chloride, benzotrichloride dosed into molten benzoic acid at 413 K, the HCl leaving as gas
and absorbed to 30 wt% hydrochloric acid, the crude distilled under vacuum from its catalyst and
excess acid; one product on a dedicated train (D-013). Boundary feeds: benzotrichloride, benzoic
acid, zinc chloride, process water, electricity, MP and LP steam, nitrogen (per batch);
returns: cooling water; outputs: distilled benzoyl chloride, 30 wt% hydrochloric acid (a
by-product), the still residue to hazardous-waste incineration.
Reason: the route the scouting recommended as the best-sourced of its four (SRC-1 gives a batch
example with amounts, times, temperatures, the distillation pressure and the yield). It
exercises what the batch work-up of core 1.8.0 adds: a dosed step with gas evolution
(`batch.vent`) and a batch vacuum distillation (`still:`). The benzoic acid variant gives two
benzoyl chloride per benzotrichloride and one HCl, half the HCl of the water variant.
Rejected: the water variant (SRC-1, Example 2: water with 3 % H2SO4 dosed into benzotrichloride
at 150 C, 92.6 % without the bottoms recycle; two HCl per product); a candidate variant
(`benzoyl-chloride-2`), and the more interesting dosing hazard (water accumulating in hot
benzotrichloride). Benzoic acid with phosgene (phosgene-1) or thionyl chloride
(thionyl-chloride-1): other routes, not this one. The continuous cascade of Example 3 belongs on
the continuous track.
Links: none to library processes for the reactants; the route uses no phosgene, chlorine or HCl
feed, so phosgene-1, chlor-alkali-1 and hydrogen-chloride-1 are not linked. chlor-alkali-1 is
named only in the gap text of the benzotrichloride proxy (D-012).

## D-002 Capacity, product and operating hours (2026-11-05)
Decision: 2000 t/a of distilled benzoyl chloride (252.525 kg/h year average), 7920 h/a,
ASSUMED. Product: at least 99.99 wt% benzoyl chloride with benzotrichloride at about 12 ppm by
mass at most, ASSUMED (SRC-1: above 99.5 %, free of benzotrichloride; the 99.993 wt% with 12 ppm
of benzotrichloride and 58 ppm of benzoic acid that K101's specified split gave until core
1.10.0, taken as the specification since); the column's model gives 99.9989 wt%, 11.0 ppm of
benzotrichloride and benzoic acid below 0.01 ppm (D-008).
Reason: no open market or plant figure was used; a few thousand tonnes a year is a plausible
size for a dedicated batch train of a fine acid chloride. The LCI is per kg and does not depend
on the scale; the batch size does (D-003).

## D-003 Batch basis and recipe (2026-11-05)
Decision: one batch makes 1229.18 kg of distilled benzoyl chloride (stream S11); the recipe
(`process/recipe.yaml`) has three unit procedures: MELT on M-101 (charge, melt and heat to
413 K, transfer: 3.0 h), REACT on R-101 (nitrogen purge, receive the melt, dose 2 h and react
1.37 h to 0.999 conversion of the benzotrichloride, both from R101's model, sample, transfer:
4.87 h) and DISTIL on C-101 with its column K-101 and the product cooler E-101 (`units: [ST101,
E101]`: receive, evacuate, distil 1.81 h from ST101's boil-up at the column's reflux, cool and
break the vacuum, drain the residue: 3.81 h). R-101 is the bottleneck: cycle time 4.868 h,
1627.1 batches in 7920 h; one batch takes 10.67 h from the melter's charge to the residue's
drain. The flowsheet's flows are the year averages of the recipe: 1229.18 kg x 1627.11 / 7920 h
= 252.53 kg/h of S11; `cheme process recipe` checks this (no `cheme.recipe-basis` finding).
Until core 1.10.0 the batch was 1229.47 kg on a 4.869 h cycle; the vent's vapour (D-010) shortens
the post-reaction by about 4 s, and the batch was set again to the cycle (D-015).
Reason: core ADR 0051 puts the batch basis in one place; the dosing, post-reaction and distil
times come from the models, so a change of the rate law or the boil-up changes the cycle. The
other durations are ASSUMED concept values.
Per batch: 1.19 m3 of crude in R-101 at the end of the dosing; the recipe sizes R-101 from
R101's model (core ADR 0052, fill fraction 0.8 and H/D 1.2 ASSUMED): a 1.6 m3 vessel (the R10
preferred size), 75 % full, 1.19 m diameter; its jacket (U 300 W/(m2 K), tempered water at
363 K, ASSUMED) removes 45.6 kW at the charge's 3.04 m2 against the model's 22.8 kW peak.

## D-004 Feeds and charge (2026-11-05)
Decision: 15/14 mol of benzoic acid per mol of benzotrichloride (7.1 % excess) and 0.742 kg of
anhydrous ZnCl2 per 100 kg of benzoic acid, SRC-1 Example 1's ratios; the feeds sized by
scripts/balance.py for 2000 t/a. Benzotrichloride 100 % (its benzal chloride and
ring-chlorinated impurities, which would give benzaldehyde and chlorobenzoyl chlorides, not
modelled), benzoic acid flakes 100 %, both ASSUMED pure.
Reason: the excess acid drives the benzotrichloride to completion, so the distillate carries
little of it (SRC-1); the example's loading of catalyst. Neither benzotrichloride nor benzoic
acid has a library producer (D-012).

## D-005 Reactor R-101: semi-batch with an HCl vent, kinetics and heat of reaction (2026-11-05)
Decision: R101 is `reactor: semibatch` (core ADR 0050): the molten charge S3 at 413.15 K, the
benzotrichloride S4 (298.15 K) dosed at a constant rate over 2 h (SRC-1, Example 1), then the
post-reaction to 0.999 conversion of the benzotrichloride (`batch.target`; 1.37 h from the
model), isothermal at 413.15 K and atmospheric pressure. `batch.vent: {stream: S6, components:
[HCL]}` (core ADR 0054): the HCl leaves the liquid as it forms, all of it (fraction 1, ASSUMED),
by the second outlet S6. Rate law of BZCL: first order in benzotrichloride and in benzoic acid,
k = 2.7e-3 m3/(kmol s) at 413 K (A 1.04e5, Ea 60 kJ/mol), ASSUMED; the ZnCl2 at the example's
loading is lumped into k. Heat: -50 kJ/mol with the HCl formed as a gas at 413 K, ASSUMED.
Reason: no open kinetics or calorimetry exists (searched 2026-11-05). k was sized so that the
post-reaction to 0.999 takes about as long as the example's 2 h hold (1.37 h here): a slower
rate would need a longer hold, a faster one a shorter. The law is second order because the acid
is a co-reactant at only a 7 % excess: in the semi-batch it runs down as the benzotrichloride is
dosed, so the rate slows towards the end of the dosing, where the accumulation peaks (7.0 %,
D-011). The heat of reaction cannot be derived (SRC-2 has no formation enthalpy of
benzotrichloride); -50 kJ/mol is an exothermic order of magnitude chosen so that the screening
is not optimistic (the HCl leaves as gas, which takes up heat, so the true value may be smaller
or of the other sign). Vented whole, HCl needs no liquid data (core ADR 0054) and adds nothing to
the liquid's volume or heat capacity.
**The low accumulation in D-011 is a consequence of the assumed rate law** and must be confirmed
by reaction calorimetry with off-gas measurement before basic engineering (D-011's sensitivity).
Off-gas (`cheme process recipe`): 164 kg (4.50 kmol) of HCl a batch, peak 0.62 mol/s, 75.25 m3/h
at 413 K and 101 kPa(a) as it leaves the liquid (with the liquid's vapour on top, D-010), 56.2
m3/h past the reflux condenser E-102 at 308 K, 0.11 h into the dosing, when the acid's
concentration is highest. The off-gas system is sized for the larger gas release at a cooling
failure, 107.2 m3/h at the MTSR with the liquid's vapour, with a margin: 130 m3/h (D-014,
equipment list). That holds for the assumed rate law only: at k/10 the release at the MTSR is
273.2 m3/h, 2.10 times it (D-011, D-014).

## D-006 Balance method and property gate (2026-11-05; core 1.10.0 2026-11-06)
Decision: cheme propagates the melter M101 and the absorber A101 (mixers), the semi-batch R101
with both outlets and the vapour its vent carries past the reflux condenser E-102 (D-005,
D-010), the still ST101 with its column (D-007, D-008) and the product cooler E101 (a
pass-through). It writes the duties of R101 (Q2), of E-102 (Q8) and of the still's reboiler (Q4)
and condenser (Q5) from those models (core ADRs 0059, 0061, 0062; D-009).
scripts/balance.py gives what core has no model for (library ADR 0027): the feeds S1, S2 and S4
that make 2000 t/a (core propagates from the feeds and does not solve them for a product rate;
the balance is linear in the feeds, so the script scales the benzotrichloride by the ratio of
the target to S11, converged in two to three passes); the absorber water S7 (D-010); the duties
Q1, Q3 and the product cooler's Q7 (D-009). It prints its own Q2 without the vent's vapour
terms (5.445 kW: the model's reaction and dose terms) and the reboiler's and condenser's (R + 1)
D lambda of the product (74.255 kW, as propagate writes Q4 and Q5) as cross-checks. It reads the
streams propagate wrote and follows the balance-output contract
(`scripts/check_balance_scripts.py`). Until core 1.10.0 it also gave K101's specified split
(S11, S12), the reflux share Q6 and the condenser Q5 (D-015).
Reason: no property package of core covers these liquids (aromatic acid chlorides with an
organic acid, HCl in water), so the melter's, absorber's and product cooler's heats are simple
heat capacities and heats of solution in the script.

## D-007 Batch still ST101 at 5 kPa(a) (2026-11-05; with its column since core 1.10.0, 2026-11-06)
Decision: ST101 is core's batch still (`still:`, core ADR 0055) with the column K-101 on it
(`still.column`, ADR 0061, D-008): the crude S5 boiled at 5 kPa(a) (SRC-1, Example 1: 50 mbar),
Raoult's law with the NIST Antoine constants of benzoyl chloride, benzotrichloride and benzoic
acid (SRC-2), ZnCl2 non-volatile, until benzoyl chloride is 40 mol% of the residue (`end:
residue`), ASSUMED so that the bottoms stay a mobile liquid (SRC-1: bottoms of 20-70 % benzoyl
chloride). Boil-up 200 kW, the reboiler's heat input (ASSUMED), of which 1/(R + 1), 67 kW, leaves
as distillate at the reflux ratio 2, so the recipe's distil takes 1.81 h. Result (`cheme process
stills`, basis `batch-shortcut`): 1308.2 kg of crude a batch give 1229.18 kg of product
(99.9989 wt%, D-008) and 79.0 kg of residue (54.0 mol% benzoic acid, 40 mol% benzoyl chloride,
5.3 mol% ZnCl2, 0.73 mol% benzotrichloride), the still from 376.5 to 396.9 K; 361.4 kWh a batch
on the reboiler and the same on the condenser. Until core 1.10.0 the still was one stage with
a 100 kW net boil-up (1.22 h; 1243.5 kg of distillate with 0.66 mol% benzoic acid, 65.2 kg of
residue), and K101 a split of its distillate.
Reason: what one stage can do here is separate the light product from a heavy, involatile
residue: at 376 K benzoic acid's vapour pressure is about 1/23 of benzoyl chloride's, so the
Rayleigh still takes off most of the benzoyl chloride while keeping the acid and the catalyst
back. The volatility is declared `assumed` (core reports the basis not sourced): benzoic acid
dimerises in the vapour and no VLE data of the pair show an ideal liquid.
Not modelled (core limits L-3, L-4): the crude arrives at 413 K, above its 376 K bubble point
at 5 kPa, so part of it flashes as the still is evacuated (`still.heat_up`, core 1.10.0, gives
no heat-up for a charge above its bubble point, and the flash is not modelled); the dissolved HCl
the crude holds (zero here, D-005) would leave first, to the vacuum system; no forerun cut,
since the model's crude has no component lighter than benzoyl chloride (the benzaldehyde of a
benzal chloride impurity would make one, D-004).

## D-008 Column K-101 on the still: 15 stages at reflux ratio 2 on core's batch shortcut (2026-11-05; the shortcut since core 1.10.0, 2026-11-06; the trade against 20 stages and the product at 308 K recorded on review, 2026-11-06)
Decision: the column on C-101, K-101, is ST101's `still.column` (core ADR 0061, Diwekar's batch
shortcut on Fenske-Underwood-Gilliland): 15 theoretical stages, the still included, at a
constant reflux ratio of 2, ASSUMED, with a total condenser (Q5) and the product cooler E-101
(E101, Q7) to storage at 308 K (10 K above the cooling water's supply, D-009). Result (`cheme process stills`): 252.53 kg/h of product, 99.9989
wt% benzoyl chloride with 11.0 ppm of benzotrichloride and below 0.01 ppm of benzoic acid; 97.31
% of the crude's benzoyl chloride, 1.54 % of its benzotrichloride and none of its benzoic acid
go over. The residue S13 is 16.24 kg/h (64 g per kg of product) to hazardous-waste incineration,
not recycled. It is drained hot under nitrogen at 373.15 K (ASSUMED), about 18 K above its ideal
benzoic acid liquidus of 355 K (x_BA 0.540; Tfus 395.2 K, dHfus 18.0 kJ/mol, SRC-2; the ideal
liquid of D-007), so the acid does not crystallise in the drain; ZnCl2 and the non-ideality move
the liquidus either way. Overall yield 97.15 % of theory on the benzotrichloride (SRC-1 Example
1: 96.7 %; description 96-98 %).
Reason: the stages and the reflux are a design choice (no source gives the column); they were
chosen on the model (a scan on a scratch copy, the same crude, the 200 kW reboiler, the end
unchanged):

| stages, reflux ratio | product, wt% benzoyl chloride | benzotrichloride in it | its share of the crude's benzotrichloride | boil-up a batch | reboiler and condenser, year average |
|---|---|---|---|---|---|
| 1 (the still alone), 1 | 99.361 | 615 ppm | 86.9 % | 1.22 h | 50.2 kW |
| 5, 1 (the specified split's column) | 99.938 | 429 ppm | 60.0 % | 1.21 h | 49.5 kW |
| 10, 2 | 99.9935 | 65 ppm | 9.0 % | 1.81 h | 74.2 kW |
| 10, 3 | 99.9969 | 31 ppm | 4.3 % | 2.41 h | 99.0 kW |
| 15, 1.5 | 99.9966 | 34 ppm | 4.7 % | 1.51 h | 61.9 kW |
| **15, 2 (chosen)** | **99.9989** | **11 ppm** | **1.5 %** | **1.81 h** | **74.3 kW** |
| 20, 1.5 | 99.9992 | 8 ppm | 1.2 % | 1.51 h | 61.9 kW |

The benzoyl chloride's recovery (97.31-97.34 %) is set by the residue's end, not by the column.
The split K101 stood for until core 1.10.0 (about 5 stages at reflux 1, 2 % of the
benzotrichloride over) is not what such a column does: the model sends 60 % of it over, 429 ppm
in the product, 35 times the 12 ppm the split gave. The split was the finding (D-015). The
design basis' product (D-002) is 99.99 wt% with about 12 ppm of benzotrichloride at most, a
carcinogen that SRC-1's product is free of. Of the cases scanned with at most 15 stages, 15 at
reflux 2 has the least boil-up that meets it (15 at reflux 1.5 gives 34 ppm, 10 at reflux 2 65
ppm); 10 stages at reflux 3 (the first estimate, ADR 0061's scratch copy) gives 31 ppm at a third
more steam. 20 stages at reflux 1.5 also meets it, with 8 ppm, at 17 % less boil-up: 61.9 against
74.3 kW year average, 12.4 kW (0.049 kWh/kg, about 98 MWh a year) less LP steam and as much less
heat to cooling water at the condenser, for 5 more theoretical stages, about 1.75 m more packing
with its pressure drop and liquid holdup under vacuum. It is rejected below; the choice is a
design trade, ASSUMED, not a result of the scan. 14 stages above the
pot are about 5 m of structured packing under vacuum (HETP about 0.35 m, ASSUMED). The shortcut
is conservative (a rigorous column at the same stages and reflux gives a purer distillate, core
ADR 0061), so the column is not undersized by the model; it has no holdup, no pressure drop (the
pot is a few mbar above the 5 kPa(a) at the top) and the volatilities of the still's
temperature for the whole column.
Rejected: 20 stages at reflux 1.5 (ASSUMED, on the reasoning, not on a cost estimate): 19
stages above the pot are about 6.7 m of packing against 4.9 m, so K-101 is a third taller, with
a third more pressure drop and holdup, which the shortcut does not model; a batch column's holdup
blurs its separation, so the shortcut's 8 ppm at 20 stages is less certain than its number, and
the pressure drop raises the pot's pressure and temperature (the pot ends at 396.9 K at the 5
kPa(a) of the top, 24 K below the LP steam's 421 K, so the reboiler would not be limited). No
equipment or steam cost is sourced at the concept stage, so the saving is not set against the
taller column; the shorter column is kept and 20 stages at reflux 1.5 is the first change to
take up when K-101 is sized with its pressure drop and holdup, or when the steam's cost or its
weight in the LCA (D-012: LP steam 0.294 against 0.245 kWh/kg) is to be lowered. The still's
time does not decide it: DISTIL is not the bottleneck (D-003), so the shorter boil-up (1.51
against 1.81 h) does not shorten the cycle.
Rejected: the specified split (D-015); a product cut to a `purity` end with an off-cut: the one
cut to the residue's end meets the specification on its mean, so an off-cut would only add a
stream to burn or recycle (with a tighter benzotrichloride specification it is the way, since the
distillate's benzotrichloride rises towards the end as the pot is depleted of benzoyl chloride);
the residue's recycle with excess benzotrichloride (SRC-1, Example 2: from 92.6 % to 97.3 %): a
variant, with a tear stream.

## D-009 Utilities and heat (2026-11-05; the model duties 2026-11-06, core 1.9.0 and 1.10.0; the product cooler's approach 2026-11-06)
Decision (year averages, all ASSUMED unless sourced; `calculated` where a core model writes the
duty):
- Q1 12.1 kW of MP steam 1100 kPa(a) to the melter (scripts/balance.py): benzoic acid from 298 K
  (solid cp 175 J/(mol K), mean, ASSUMED from 146.8 at 298 K) to its melt at 395.2 K, its fusion
  (18.0 kJ/mol) and the liquid to 413 K (259 J/(mol K)), the catalyst, 10 % losses (SRC-2); 30 kW
  over the 2 h melt.
- Q2 2.889 kW from R-101 to cooling water through a pressurised tempered-water loop at 363 K,
  R101's semi-batch model (`calculated`, ADR 0059): the reaction heat (-50 kJ/mol, D-005, 12.829
  kW) less the benzotrichloride's heating from 298 to 413 K (250 J/(mol K), ASSUMED, 7.384 kW),
  the latent heat of the vapour the HCl carries off the liquid (1.831 kW) and the condensate
  E-102 returns, warmed back from 308 K (0.725 kW) (core 1.10.0, ADR 0062, D-010); during the
  dosing the model's peak is 22.8 kW (the peak leaves the vapour's cooling out, conservative).
  Until core 1.10.0: 5.442 kW, without the vapour.
- Q8 3.330 kW from R-101's reflux condenser E-102 to cooling water, R101's vent model
  (`calculated`, `vent.condenser.energy_port`, ADR 0062): the vapour condensed (1.813 kW) and
  cooled as liquid to 308 K (0.732 kW), the HCl cooled from 413 to 308 K (0.785 kW, its ideal-gas
  cp, SRC-8). Until core 1.10.0 not counted.
- Q3 15.0 kW from the absorber to cooling water (scripts/balance.py, D-010); the gas now arrives
  at 308 K from E-102 (15.8 kW until core 1.10.0, the gas at 413 K).
- Q4 74.25 kW of LP steam 450 kPa(a) to the still's jacket, the reboiler, ST101's model
  (`calculated`, `energy_port: steam`, ADR 0061): (R + 1) times the latent heat of the product
  distilled, R = 2 (D-008); 200 kW while distilling. Until core 1.10.0 the reboiler was two
  streams, Q4 25.0981 kW (the net boil-up, the one-stage still's model) and Q6 25.0982 kW (the
  reflux ratio 1 times the same latent heat, typed): 50.196 kW in all. The reboiler takes 48 %
  more steam now, since the column of D-008 needs reflux 2 for the product.
- Q5 74.25 kW to cooling water, the column's total condenser, ST101's model (`calculated`,
  `still.condenser_port`, ADR 0061): the same latent heat out, no subcooling.
- Q7 6.29 kW to cooling water, the product cooler E-101 (scripts/balance.py): the product from
  375.5 K (benzoyl chloride's boiling point at 5 kPa(a), the column's top) to 308.15 K at 187
  J/(mol K), 10 K above the cooling water's 298.15 K supply at the cooler's cold end, the minimum
  approach that sets E-102's gas outlet too (D-010); the design basis' delivery is 308.15 K
  (ASSUMED, to storage under nitrogen; no storage temperature limit of the product is sourced).
  Until core 1.10.0 Q5 held the condenser and the cooler in one typed stream, 57.0
  kW, the product to 303 K, 5 K above the cooling water's supply, an approach below the minimum
  that the separate cooler made visible (review of the core 1.10.0 change, 2026-11-06); a 303 K
  delivery would need chilled water or a 5 K approach, neither of which the design basis gives.
- Electricity 7 kW: agitators of M-101 (1 kW) and R-101 (3 kW), P1; the still's agitator (1 kW)
  and a dry vacuum pump (5 kW while distilling, about 40 % of the time), P2.
Not counted: the still's heat-up (the crude arrives above its bubble point, D-007), the vessels'
metal (ADR 0063's `vessel.metal_heat_capacity` is not given: D-015), heat losses of R-101 and
C-101, the vacuum pump's cooling.

## D-010 HCl off-gas, its vapour, the reflux condenser and absorption (2026-11-05; the vapour since core 1.10.0, 2026-11-06)
Decision: R-101's off-gas leaves saturated with the liquid's vapour (`batch.vent.vapour`, core
ADR 0062: Raoult's law over the liquid at each moment of the batch, an ideal liquid ASSUMED, the
NIST Antoine constants of benzoyl chloride, benzotrichloride and benzoic acid, SRC-2) and passes
the reflux condenser E-102 on cooling water (`vent.condenser`), whose gas outlet is at 308.15 K,
10 K above the cooling water's supply (the design basis' minimum approach, ASSUMED), and whose
condensate returns to R-101. Over the year the HCl (0.924 kmol/h) carries 0.131 kmol/h of vapour
off the liquid (0.121 kmol/h of it benzoyl chloride; 0.189 of the gas over the liquid at the end
of the batch), E-102 returns all but 1.3 mol/h, and the off-gas S6 to A-101 is 33.86 kg/h with
about 0.54 wt% (0.14 mol%) of organics (0.18 kg/h of benzoyl chloride, 0.07 % of the product). It is absorbed in
process water to 30 wt% hydrochloric acid in A-101, a falling-film absorber with a water tail
scrubber (a mixer in the model, all HCl and all organics taken up): 78.58 kg/h of water, 112.44
kg/h of acid (0.445 kg per kg of product, 29.95 wt% HCl beside the organics), the acid at 313 K;
heat -64 kJ/mol (the integral heat of solution of HCl in about 4.7 mol of water, ASSUMED order of
magnitude) less the gas warmed from 308 to 313 K.
Reason: SRC-1 absorbs the washed off-gas to about 30 % hydrochloric acid with 18 ppm organic
carbon; selling it as a by-product is the route's practice (D-012 for its allocation). At 413 K
benzoyl chloride's vapour pressure is about 20 kPa, so the gas cannot leave dry: the model
carries what the hand note of D-010 said until core 1.10.0 (about a fifth of the gas over the
liquid as organics, not in the balance) and returns it as the reflux condenser does.
Not modelled: the wash of the cooled gas with the benzotrichloride feed on its way to R-101
(SRC-1), which returns most of the organics past E-102 to the reactor; so the model's acid holds
0.16 wt% benzoyl chloride (which hydrolyses in it to benzoic acid and HCl, not modelled either),
an upper bound against SRC-1's 18 ppm organic carbon after the wash. Benzoic acid, which melts at
395 K, condenses with the benzoyl chloride in E-102 and stays dissolved in it, but can deposit
where the condensate runs thin (the off-gas line is traced, D-014).

## D-011 Thermal screening of the semi-batch and the rate-constant sensitivity (2026-11-05)
Result (`cheme process reactor-hazards`, core ADR 0050, 0054): adiabatic temperature rise of the
whole batch 94.7 K (with -50 kJ/mol); largest accumulation of the dosed benzotrichloride 7.04 %,
at the end of the dosing; MTSR at that moment 421.9 K (the same with the vent's vapour of core
1.10.0, which the screening leaves out of the MTSR), against an MTT of 471.0 K
(`hazard.mtt`: the normal boiling point of benzoyl chloride, the liquid's main component; core's
default, the lowest boiling point of the charge and the dose, would be benzotrichloride's 493.8
K, above it: lesson L-5). The vented HCl adds nothing to the MTSR; at the MTSR it forms at 81.6
m3/h and leaves with the liquid's vapour at 107.2 m3/h (core 1.10.0), which R-101's off-gas
system is sized for (D-014), but only with the assumed rate law: at k/10 and k/100 the release
exceeds the vent capacity (the table below, D-014); with the vent blocked it pressurises the
vessel, which the screening does not assess (D-014).
No TD24 is known (never estimated): no criticality class (`cheme.reactor-hazard-missing`,
info). With MTSR below MTT the class is 1 or 2 if the TD24 lies above the MTSR, and 5 if it
lies below (TD24 < 421.9 K: core's `criticality()` and Stoessel test the TD24 against the MTSR
first, SRC-4); it needs the TD24.
Sensitivity (a scratch copy of the folder, only A divided, everything else as designed,
`hazard.vent_capacity` kept at 130 m3/h; `cheme process propagate --fill`, `reactor-hazards`,
`reactors`, `recipe`; rerun with core 1.10.0 on 2026-11-06, the gas release with the liquid's
vapour, no condenser credited):

| k at 413 K | accumulation (end of dosing) | MTSR | MTSR vs MTT 471.0 K | gas release at the MTSR (HCl with the liquid's vapour, 101.3 kPa(a)) vs the vent's 130 m3/h | post-reaction to 0.999 | cycle | class without TD24 |
|---|---|---|---|---|---|---|---|
| 2.7e-3 (design) | 7.04 % | 421.9 K | 49 K below | 0.6550 mol/s of HCl, 107.2 m3/h with 0.239 vapour: 0.82 x | 1.37 h | 4.87 h | 1, 2 or 5 |
| k/10 | 25.8 % | 443.3 K | 28 K below | 1.255 mol/s of HCl, 273.2 m3/h with 0.398 vapour: 2.10 x (`cheme.reactor-hazard-vent`, warning) | 15.4 h | 18.9 h | 1, 2 or 5 |
| k/100 | 69.8 % | 484.8 K | 14 K above | 3.096 mol/s of HCl, 2951 m3/h with 0.85 vapour: 22.7 x (`cheme.reactor-hazard-vent` and `-mtsr`, warnings) | 160 h | 163 h | 3, 4 or 5 |

The release grows with the accumulation (more benzotrichloride left to react at the MTSR, which
is also hotter, and the hotter liquid's vapour on top), so a slower reaction than assumed does
not only raise the MTSR: at k/10 the vent is exceeded 2.1 times before the MTSR comes near the
MTT (open design finding, D-014). At k/100 the liquid at 484.8 K is above benzoyl chloride's
normal boiling point, its vapour 0.85 of the gas: close to boiling (the screening's `boils`
needs the vapour at the vessel's pressure, not reached here). With the HCl alone (core 1.9.0) the
releases were 81.6, 164.3 and 443.2 m3/h against 100 m3/h: 0.82, 1.64 and 4.43 times.

MTSR over the batch (core 1.9.0, ADR 0058; the same in core 1.10.0): 413.1 K at the start, 415.0 K at 0.67 h, 416.6 K at
1.35 h, 421.9 K at the end of the dosing (2.0 h), back to 414.0 K at 2.68 h and 413.3 K at the
end of the post-reaction (3.37 h): the worst moment is the end of the dosing, as the single value
said. Gas release at the MTSR: D-014.
Interpretation: the step is dosing-controlled only if the reaction is fast. All at once (a
batch, accumulation 1) the MTSR would be about 508 K, above the boiling point of benzoyl
chloride, so the dosing, not the dilution, keeps it below the MTT: the dosing must be interlocked
with the temperature, the agitator and the off-gas flow. The off-gas is an online measure of the
accumulation (HCl forms only as the benzotrichloride reacts): a dosing that runs without
off-gas means unreacted benzotrichloride is building up. At k/100 the cycle (163 h) already
rules out the design, before safety does; at k/10 the cycle quadruples and the MTSR is still
below the MTT, but the gas released at the MTSR is 2.10 times R-101's vent capacity (D-014).
Open for the next stage: reaction calorimetry with off-gas measurement (heat of
reaction, heat-flow and gas-flow profile, the ZnCl2 dependence), TD24 of the crude and of the
residue, the gas-generation pressure with a blocked vent (Stoessel's separate criterion), and
the HCl release on a dosing restart after accumulation. Screening values only, not a
reaction-hazard assessment.
Open, water and HCl release (not assessed, reasoning only): both chlorides react with water and
give off HCl gas at once (C7H5Cl3 + H2O -> C7H5ClO + 2 HCl, SRC-1's Example 2 route; C7H5ClO +
H2O -> C7H6O2 + HCl), and the design has water on both sides of R-101. (a) Water ingress into
R-101 or C-101: from R-101's tempered-water jacket (a pressurised loop at 363 K, so a leak
runs inward), from C-101's LP steam jacket, or sucked back from A-101 through the off-gas line (HCl
absorption in water is strongly exothermic and pulls a vacuum once the gas evolution stops or
the reactor cools). 1 kg of water reacting with benzotrichloride gives 0.111 kmol of HCl, about
3.8 m3 at 413 K and 101 kPa, into the same off-gas line (75 m3/h peak) that a blocked or flooded
absorber would restrict. Options to assess: anti-suck-back protection on the off-gas line (a
nitrogen-padded seal pot or a barometric leg, or a vacuum breaker on nitrogen), a non-water
heat-transfer fluid on R-101's jacket or jacket-leak detection (conductivity or pressure of the
loop). (b) Loss of the absorber water while R-101 doses: up to 0.62 mol/s of HCl to the tail
scrubber or to air; stopping the dosing does not stop it, since the accumulated benzotrichloride
(7 %, about 0.32 kmol of HCl a batch) keeps reacting. The benzotrichloride dosing should also be
interlocked on A-101's water flow and on HCl breakthrough at the tail scrubber, and the scrubber
sized for the accumulated HCl. For the HAZOP of the next stage.

## D-012 Preliminary gate-to-gate LCI (2026-11-05)
Decision: `cheme assess lca --write` per kg of distilled benzoyl chloride from the flowsheet's
year averages; the nitrogen per batch (8 Nm3, 10.0 kg, ASSUMED: purges of R-101 and C-101, the
vacuum broken once, the crude transfer) is an `lca.yaml` consumable `per_batch` (core ADR 0053,
library ADR 0035), linked to asu-1; the MP and LP steam counted as heat (kWh); every other
background a gap with the activity it should connect to. No water rinse: the train is kept dry
(both chlorides hydrolyse).
Allocation: shares 1/0 between benzoyl chloride and the 30 wt% acid (lca.yaml `allocation`,
agent proposal): no physical relationship; the WBCSD rule gives economic allocation (the price
ratio is well above 5), which would leave the acid a few per cent; no prices are sourced at the
concept stage.
Proxies for the feeds without a library entry (gaps, not links): benzotrichloride from the
side-chain photochlorination of toluene with chlorine (SRC-7, leads only; its main burdens would
be chlorine from chlor-alkali-1 and toluene), benzoic acid from the liquid-phase air oxidation of
toluene, zinc chloride from zinc and HCl or chlorine. A correct gap is kept rather than a doubtful
link (library ADR 0026).
Per kg of benzoyl chloride: benzotrichloride 0.716 kg (stoichiometric 0.695), benzoic acid
0.479 kg (0.434), ZnCl2 3.6 g, process water 0.311 kg, nitrogen 8.1 g, electricity 0.028 kWh,
MP steam 0.048 kWh, LP steam 0.294 kWh (Q4, the reboiler at reflux 2, D-009), cooling water
0.403 kWh removed (Q2, Q3, Q5, Q7, Q8); out: 30 wt% acid 0.445 kg (0.133 kg HCl, 0.7 g of
benzoyl chloride, D-010), residue 0.064 kg. Not counted: the vents (emission_exclusions). Until
core 1.10.0: benzotrichloride 0.715 kg, LP steam 0.199 kWh (Q4 and Q6), cooling water 0.310 kWh,
acid 0.444 kg (D-015).

## D-013 Dedicated train (2026-11-05)
Decision: M-101, R-101 with E-102, A-101, C-101 with K-101 and E-101 make only benzoyl chloride,
batch after batch: 1627.1 batches in 7920 h (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train
cannot be checked without the other products' campaigns.
Out of scope, so not LCI gaps: changeover cleaning between campaigns, the idle time of a
multipurpose train, shared tank farms. Benzoyl chloride is also made on continuous plants (SRC-1
Example 3); this entry is the batch case.

## D-014 R-101's vent capacity against the gas released at a cooling failure (2026-11-06; with the liquid's vapour, core 1.10.0)
Result (`cheme process reactor-hazards`, core 1.10.0, ADRs 0058 and 0062): at a cooling failure at
the worst moment (the end of the dosing, 7.04 % of the benzotrichloride accumulated) the reaction
runs on at the MTSR, 421.9 K, and gives off 0.6550 mol/s of HCl, 81.64 m3/h at 421.9 K and 101.3
kPa(a), which leaves the liquid with its vapour (0.239 of the gas: benzoyl chloride at x about 0.9
and 26 kPa, SRC-2's Antoine): 107.2 m3/h (per batch of the recipe, from the worst moment's
content; no condenser credited, since E-102 is on the same cooling water as R-101's
tempered-water loop and fails with it). That is 8 % more HCl by volume (6 % more in moles;
0.6550 against 0.6166 mol/s) than the normal peak of 75.25 m3/h of HCl at 413 K (`cheme process
recipe`, D-005), and 42 % more with the vapour. Run to completion the accumulated
benzotrichloride gives 0.317 kmol (10.97 m3; 14.41 m3 with the vapour) more.
Decision: R-101's off-gas system (the vapour line from R-101, the reflux condenser E-102 in it
and A-101) is sized for 130 m3/h of gas with the liquid's vapour at the vessel's pressure,
`hazard.vent_capacity: 130`, ASSUMED: 1.2 x the gas release at the MTSR with the assumed rate
law (128.6 m3/h), rounded up; the release at the MTSR is then 82 % of it, within it
(`cheme.reactor-hazard-vent`, info). Since core 1.12.0 the finding quotes the larger of that and
the largest release over the batch (`gas_release.largest_over_batch`, core ADR 0069): 107.4 m3/h
at 1.94 h (its MTSR 421.1 K, a vapour share of 0.23), 0.826 of the capacity against 0.825 at the
MTSR, so the margin is the same. The vapour line from R-101 to E-102, for example DN80, runs
at about 7.6 m/s at 130 m3/h. Its non-condensables, about 99 m3/h of HCl at 421.9 K (0.79 mol/s),
are about 53 kW to A-101's cooling at 67 kJ/mol with the gas arriving hot (E-102 lost), against
39 kW at the normal peak through E-102 (D-010).
Until core 1.10.0 the capacity was 100 m3/h, 1.2 x the HCl alone (81.6 m3/h), and the vapour line
was sized by hand for 100 / (1 - 0.23), about 130 m3/h, from benzoyl chloride's vapour pressure
(L-2). With the vapour the release at the MTSR is 1.07 times those 100 m3/h
(`cheme.reactor-hazard-vent`, warning); the hand sizing of the line already held it, A-101's did
not. The model's vapour share, 0.239, confirms the hand 0.23; the capacity follows the same rule
(1.2 x the release at the MTSR) on the gas the model now carries (D-015).
Reason: the off-gas system was sized for the normal peak only (D-005), which a cooling failure
at the end of the dosing exceeds. With the assumed rate law the release at the MTSR is only 8 %
above the normal peak's HCl, so sizing the system for it with its vapour costs little and is preferred to slowing the dosing. The 1.2
is a margin on that one case, not on the kinetics: the rate law is ASSUMED (D-005, no
calorimetry), and the capacity is no more credible than the rate constant it was derived from.
Open (design finding, for the next stage): **the vent capacity holds only for the assumed
kinetics.** In D-011's own sensitivity cases the gas release at the MTSR exceeds it: at k/10
1.255 mol/s of HCl at 443.3 K, 273.2 m3/h with 0.398 of it vapour, 2.10 times the 130 m3/h
(about 84 kW to A-101's cooling at 67 kJ/mol, against the 53 kW it is sized for), and at k/100
2951 m3/h, 22.7 times, with the liquid near its boiling point (that case is ruled out by its
163 h cycle anyway, D-011). `cheme process reactor-hazards` then reports
`cheme.reactor-hazard-vent` as a warning and exits 1. Before basic engineering either (a) the
off-gas system (line, E-102, A-101) is sized for the k/10 case, about 330 m3/h with the liquid's
vapour (1.2 x 273.2 m3/h, rounded up; 200 m3/h for the HCl alone before core 1.10.0), or (b) the
dosing rate is set from reaction calorimetry with off-gas measurement so that the accumulation,
and with it the release at the MTSR, stays within the installed capacity. The flowsheet keeps 130
m3/h, the design case's basis, until one of the two is decided. The common cooling water of
R-101's loop and E-102 is the reason E-102 is not credited; a separate coolant for E-102 would
take the vapour out of A-101's load at a cooling failure, not out of the vapour line's.
Open (design finding, for the HAZOP and the relief study of the next stage): with the vent
blocked (a flooded or frozen absorber, benzoic acid sublimed into the line) the gas pressurises
R-101, which the screening does not assess (no head-space or relief model, ADR 0058): the 0.317
kmol of the accumulated benzotrichloride alone would raise the 0.41 m3 head space (1.6 m3 vessel,
1.19 m3 of crude) by about 2.7 MPa at 421.9 K, far above what a glass-lined vessel is usually
rated for, and during the dosing the HCl forms all the time. So R-101 needs a relief device
(rupture disc to a catch tank or the scrubber) sized for the gas generation with the liquid's
vapour, the benzotrichloride dosing interlocked on R-101's pressure and on the off-gas flow
(D-011), and the off-gas line traced against benzoic acid deposits. Reasoning only, not a relief
sizing.

## D-015 Core 1.10.0: the still's column and the vent's vapour from the models (2026-11-06)
Decision: the hand workarounds of the column and of the off-gas move onto core 1.10.0:
- ST101 takes its column (`still.column`, ADR 0061; D-007, D-008): K101's specified split, its
  heavies return S12, the residue mixer M102 and the typed reflux share Q6 are removed; the
  still's `boilup` is the whole reboiler (200 kW, not the 100 kW net); the reboiler Q4 and the
  condenser Q5 are written `calculated` (`energy_port`, `still.condenser_port`); the product's
  subcooling, which the old Q5 held, is the product cooler E101 (E-101) with its own typed Q7.
  The still's residue goes straight to incineration (S13). scripts/balance.py no longer splits S9
  and gives no Q5 or Q6.
- R101's vent carries the liquid's vapour (`batch.vent.vapour`) through the reflux condenser
  E-102 at 308.15 K (`vent.condenser`, `returns: vessel`, its duty on Q8 at `energy_port: q_vent`)
  (ADR 0062; D-010); HCl's ideal-gas heat capacity (SRC-8) is added so that E-102's duty counts the
  gas cooled. The vent and acid streams' template `acid` takes the organics.
Where the model disagrees with the hand values, and what was decided:
- The column: the split's 2 % of the benzotrichloride over is not what its stated column (about
  5 stages, reflux 1) does; the model sends 60 % (429 ppm in the product, 99.938 wt%). A model with
  stated stages and reflux is more credible than a split chosen to give a purity, so the model is
  adopted and the column redesigned to the design basis' product: 15 stages at reflux 2 (D-008's
  scan). Consequences: the reboiler's year average rises from 50.20 to 74.25 kW (LP steam 0.199 to
  0.294 kWh/kg), the condenser's (with the cooler) from 57.04 to 80.54 kW (the product now cooled to 308 K, D-009), the boil-up from 1.22 to
  1.81 h (DISTIL 3.22 to 3.81 h, still below R-101's 4.87 h cycle); the product from 99.993 to
  99.9989 wt% (benzotrichloride 12.4 to 11.0 ppm, benzoic acid 58 to below 0.01 ppm); the yield
  from 97.19 to 97.15 %.
- The off-gas: the model's vapour share at the MTSR, 0.239, agrees with D-014's hand 0.23; the
  model also returns 99 % of the vapour by E-102 and sends 0.18 kg/h of benzoyl chloride on to
  A-101, which the hand balance left out. The gas release at the MTSR with the vapour, 107.2 m3/h,
  exceeds the 100 m3/h vent capacity set for the HCl alone (`cheme.reactor-hazard-vent`, warning,
  1.07 x): the capacity is reset by D-014's own rule to 130 m3/h, the size the hand note had given
  the vapour line, now for the whole off-gas system. In the sensitivity the releases grow to
  273.2 m3/h at k/10 (2.10 x, against 1.64 x) and 2951 m3/h at k/100 (D-011).
- R101's duty Q2 falls from 5.442 to 2.889 kW (the vapour's latent heat and the returned
  condensate cool the content) and E-102's Q8, 3.330 kW, is new: the jacket and E-102 together
  remove 6.22 kW, 0.78 kW more than the jacket alone did, the HCl cooled to 308 K. The absorber's
  Q3 falls from 15.79 to 15.02 kW (the gas arrives at 308 K). The feeds rise by 0.05 % (the
  benzoyl chloride past E-102 and the column's recovery), the batch from 1229.47 to 1229.18 kg on
  a 4.868 h cycle (D-003).
- The product cooler E-101, its own unit now, shows that the 303 K delivery the old typed Q5 held
  was a 5 K approach to the cooling water's 298.15 K supply, below the design basis' 10 K minimum:
  the delivery is set to 308.15 K (S11, the design basis), Q7 from 6.75 to 6.29 kW, the cooling
  water from 0.405 to 0.403 kWh/kg (D-009).
Not used, with the reason:
- `vent.henry` (ADR 0062): no solubility of HCl in hot benzoyl chloride was found (searched
  2026-11-05); the vent keeps `fraction` 1 (L-3).
- `dosing.heat_of_solution` (ADR 0063): the benzotrichloride's heat of mixing into the melt is
  not known; none is invented.
- `batch.heat_up`: the charge S3 enters R-101 at the batch's 413.15 K (the melter heats it), so
  the term is zero; `still.heat_up`: the crude enters above its bubble point at 5 kPa(a), which
  takes no heat-up (D-007).
- `vessel.metal_heat_capacity`: R-101 is isothermal from its charge's temperature (no metal term
  without `heat_up`), and the still's metal from its bubble point to its end, 20 K, would add
  about 7 kWh to the 361 kWh a batch (2 %) on an assumed 2.5 t of steel (1250 kJ/K); left out
  rather than add an unsourced mass (D-009).
- A `purity` end with an off-cut (D-008) and `constant_distillate` reflux: the one cut meets the
  specification at constant reflux.
Checks after the change: `cheme validate` 0 errors and 0 warnings; `propagate --check` clean;
`reactor-hazards` exits 0 (info only); the balance script's values agree
(`check_balance_scripts.py --strict`).

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101 with its HCl vent: composition, accumulation, cooling-failure temperature, peak cooling, off-gas rate, year-average duty Q2 | done in cheme, kinetics ASSUMED | D-005, D-009, D-011, core ADRs 0050, 0054, 0059 |
| the liquid's vapour in R-101's off-gas, the reflux condenser E-102 (condensate back, duty Q8) | done in cheme, ideal liquid ASSUMED | D-010, core ADR 0062 |
| MTSR over the batch, gas release at the MTSR against the vent capacity | done in cheme, vent capacity ASSUMED, holds for the assumed kinetics only (exceeded at k/10) | D-011, D-014, core ADR 0058 |
| batch recipe, cycle time, basis check, R-101's vessel and jacket | done in cheme | D-003, core ADRs 0051, 0052 |
| batch still ST101 with its column K-101: product purity and recovery, residue, boil-up time, reboiler Q4 and condenser Q5 | done in cheme (batch shortcut), stages, reflux and ideal liquid ASSUMED | D-007, D-008, D-009, core ADRs 0055, 0059, 0061 |
| feeds for 2000 t/a, absorber water, duties Q1, Q3 and the product cooler Q7 | script | D-006, D-009, D-010 |
| the benzotrichloride wash of the off-gas; the organics' hydrolysis in the acid | not modelled | D-010 |
| per-batch nitrogen | done in cheme, amount ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core features used (cheme-as-code 1.8.0, 1.9.0 and 1.10.0, the pins of 2026-11-05 and 2026-11-06)

- `reactor: semibatch` with `batch.dosing` and `batch.target` (ADR 0050) and `batch.vent` for the
  HCl (ADR 0054): two outlets, the vent's peak rate per m3 (`process reactors`) and per batch
  (`process recipe`), the vented gas left out of the MTSR (`process reactor-hazards`);
  `hazard.mtt` on the step.
- `still:` (ADR 0055): Raoult's law with Antoine `vapour_pressure` and `heat_of_vaporization` in
  materials.yaml, `nonvolatile`, `boilup` in kW, `end: residue`; `cheme process stills`.
- `process/recipe.yaml` (ADRs 0051, 0052, 0055, 0057): `dose`/`react` `from:` R101, `distil
  from:` ST101, `units: [ST101, E101]` (until 1.10.0 `[ST101, K101, M102]`) for one vessel over several steps, R-101's `vessel`
  and `jacket` check.
- `lca.yaml` `consumables` with `per_batch` (ADR 0053), `allocation: shares`.
- 1.9.0: the models' duties (ADR 0059): R101's Q2 on its one heat stream, ST101's Q4 by
  `energy_port: steam`, both written `calculated` by `propagate --fill`, the typed Q6 beside it
  until 1.10.0 (D-009); the semi-batch screening (ADR 0058): `mtsr_profile`, `gas_release` and
  `hazard.vent_capacity` (D-011, D-014).
- 1.10.0: the still's column (ADR 0061): `still.column` with `stages: 15`, `reflux: constant`,
  `ratio: 2`, the `boilup` as the whole reboiler, `still.condenser_port` (Q5) beside
  `energy_port` (Q4), both written `calculated`; `cheme process stills` with the basis
  `batch-shortcut`, the product's mass fractions and recoveries (D-007, D-008). The vent's vapour
  and condenser (ADR 0062): `batch.vent.vapour` with the three organics, `vent.condenser` at
  308.15 K, `returns: vessel`, `energy_port: q_vent` (Q8), the vapour terms in R101's Q2, the
  gas release at the MTSR with the vapour in `reactor-hazards`, the vent's m3/h at the
  condenser's temperature in `recipe` (D-010, D-014). Ideal-gas data of HCl for the condenser's
  gas cooling (SRC-8).
- Not used in 1.10.0: `vent.henry`, `dosing.heat_of_solution`, `batch.heat_up`,
  `still.heat_up`, `vessel.metal_heat_capacity`, a `purity` end (D-015 gives the reasons);
  `tears:` (ADR 0060; no recycle is modelled), `hazard.reactions` (one reaction), the default MTT
  (still not the product's boiling point, L-5).
- Not used, not needed by this route: `dosing.absorbed` (no gas is dosed), the crystallizer, the
  dryer and the filter (no solids: the benzoic acid is charged molten).

## Core limits hit (each a candidate core issue)

- L-1 (core#173; **resolved in core 1.10.0**, ADR 0061): no batch rectification with reflux.
  One Rayleigh stage cannot reach the product's purity (D-008); the column was a specified split
  in a script, the still's `boilup` the net distillate rate (100 kW of a 200 kW reboiler at reflux
  ratio 1), the reflux share its own typed stream Q6 and the condenser Q5 in the script. Core
  1.10.0 integrates the column on Diwekar's shortcut and writes the reboiler and the condenser;
  the split and Q6 are gone (D-015). What stays: the shortcut's own limits (no holdup, no pressure
  drop, Gilliland's correlation, conservative) and the column is not sized.
- L-2 (ADR 0054 limitation; **resolved in core 1.10.0**, ADR 0062): the vent carried only the
  named gas, no vapour of the liquid. Core 1.10.0 saturates the gas with the liquid's vapour and
  takes it through the reflux condenser E-102 (D-010, D-014). What stays: the benzotrichloride wash
  on the off-gas, and the organics' hydrolysis in the absorber, are not modelled (D-010); the
  condenser is not credited in the screening (core ADR 0062, and here the same cooling water).
- L-3 (ADR 0054): no solubility of the vented gas: the dissolved HCl of the crude (fraction 1
  stands in for "none dissolved") is not carried to the still, so the still has no lights cut and
  the vacuum system's HCl load is not known; a dissolved HCl could not be distilled anyway, since
  a still needs an Antoine (HCl is supercritical at 376 K) or an alpha that would be invented.
  Core 1.10.0 has the Henry split (`vent.henry`, ADR 0062), but no solubility of HCl in hot
  benzoyl chloride is at hand (searched 2026-11-05): open on the data, not on core.
- L-4 (ADR 0055): the still has no flash of a charge hotter than its bubble point (the crude
  arrives at 413 K, its bubble point at 5 kPa is 376 K; core 1.10.0's `still.heat_up` gives such a
  charge no heat-up and its flash is not modelled), and does not size its column, condenser or
  vacuum system: C-101 and K-101 are sized by hand (core 1.10.0 could size the still's pot from
  the recipe, not used: C-101 is 1.6 m3 as R-101).
- L-5: the default MTT is the lowest boiling point of the charge and the doses; it ignores the
  product formed in the liquid. Here the product, benzoyl chloride (471 K), boils below both the
  charge (benzoic acid, 522 K) and the dose (benzotrichloride, 494 K), so the default would be 23 K
  too high; `hazard.mtt` was set by hand (phosphorus-tribromide-1's L-2 is the mirror case).
  Still so in core 1.9.0 and 1.10.0: ADR 0058 leaves out vent and dissolved gases, but the products are no
  candidates for the MTT (its known limitations).
- L-6 (as n-bromosuccinimide-1's L-6): core propagates from the feeds and cannot solve them for a
  product rate; the script scales the feeds (two to three passes of propagate and the script).
- L-7 (resolved in core 1.9.0, ADR 0059): an isothermal semi-batch reported its peak cooling
  duty and the heat released, but no year-average duty for its energy stream, so Q2 came from
  the script. Core 1.9.0 writes it (5.44216 kW, the script's 5.4422 kW), and the still's net
  boil-up Q4 likewise; since core 1.10.0 Q2 holds the vent's vapour terms too (2.889 kW, D-009).
- L-8: no model for melting a solid feed (benzoic acid flakes to a melt) in a mixer: Q1 is a
  script value.
- L-9 (ADR 0055): an ideal liquid only; benzoic acid's vapour dimerisation and its non-ideality
  with benzoyl chloride are not representable, so the still's basis is "not sourced".

## Open inputs
Kinetics and heat of reaction by reaction calorimetry with off-gas measurement; TD24 of the crude
and the residue; HCl solubility in hot benzoyl chloride; VLE of benzoyl chloride with benzoic acid
and benzotrichloride at 5 kPa; the column's stages and reflux, its packing, pressure drop and a
rigorous check of the shortcut (D-008); the benzotrichloride's impurity profile (benzal chloride,
ring-chlorinated) and the forerun it would need; the residue's recycle with excess
benzotrichloride (SRC-1, Example 2); the product specification, the benzotrichloride above all,
which sets the column (D-008); the benzotrichloride wash of the off-gas (D-010); prices for the
allocation; a TEA (`operation.batch: {recipe: true}`); R-101's relief device and blocked-vent
case, the off-gas system's capacity against a slower reaction (330 m3/h with the vapour for
k/10, or the dosing rate from calorimetry), and the off-gas line's hydraulics (D-014).
