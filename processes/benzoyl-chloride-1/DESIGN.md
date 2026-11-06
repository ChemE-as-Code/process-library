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
ASSUMED. Product: 99.993 wt% benzoyl chloride, 58 ppm benzoic acid and 12 ppm benzotrichloride
by mass in the model (SRC-1: above 99.5 %, free of benzotrichloride).
Reason: no open market or plant figure was used; a few thousand tonnes a year is a plausible
size for a dedicated batch train of a fine acid chloride. The LCI is per kg and does not depend
on the scale; the batch size does (D-003).

## D-003 Batch basis and recipe (2026-11-05)
Decision: one batch makes 1229.47 kg of distilled benzoyl chloride (stream S11); the recipe
(`process/recipe.yaml`) has three unit procedures: MELT on M-101 (charge, melt and heat to
413 K, transfer: 3.0 h), REACT on R-101 (nitrogen purge, receive the melt, dose 2 h and react
1.37 h to 0.999 conversion of the benzotrichloride, both from R101's model, sample, transfer:
4.87 h) and DISTIL on C-101 with its column K-101 (`units: [ST101, K101, M102]`: receive,
evacuate, distil 1.22 h from ST101's boil-up, cool and break the vacuum, drain the residue:
3.22 h). R-101 is the bottleneck: cycle time 4.869 h, 1626.7 batches in 7920 h; one batch takes
10.09 h from the melter's charge to the residue's drain. The flowsheet's flows are the year
averages of the recipe: 1229.47 kg x 1626.72 / 7920 h = 252.53 kg/h of S11; `cheme process
recipe` checks this (no `cheme.recipe-basis` finding).
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
Off-gas (`cheme process recipe`): 164 kg (4.50 kmol) of HCl a batch, peak 0.62 mol/s, 75 m3/h at
413 K and 101 kPa(a), 0.12 h into the dosing, when the acid's concentration is highest. The
off-gas line and A-101 are sized for the larger gas release at a cooling failure, 81.6 m3/h at
the MTSR, with a margin: 100 m3/h of HCl (D-014, equipment list). That holds for the assumed
rate law only: at k/10 the release at the MTSR is 164.3 m3/h, 1.64 times it (D-011, D-014).

## D-006 Balance method and property gate (2026-11-05)
Decision: cheme propagates the melter M101, the semi-batch R101 with both outlets, the absorber
A101 and the residue mixer M102 (mixers), and the still ST101 (one Rayleigh stage, D-007).
Since core 1.9.0 (ADR 0059) propagate also writes the duties of R101 (Q2) and of the still's net
boil-up (Q4) from those models (D-009).
scripts/balance.py gives what core has no model for (library ADR 0027): the feeds S1, S2 and S4
that make 2000 t/a (core propagates from the feeds and does not solve them for a product rate;
the balance is linear in the feeds, so the script scales the benzotrichloride by the ratio of
the target to S11, converged in two passes); the column K101's specified split of the still's
distillate S9 into S11 and S12 (D-008); the absorber water S7 (D-010); the duties Q1, Q3, Q5
and the reboiler's share for the column's reflux, Q6 (D-009). It prints its own Q2 and Q4 as a
cross-check of the models (5.442 and 25.098 kW, as propagate writes them). It reads the streams propagate wrote and follows the balance-output contract
(`scripts/check_balance_scripts.py`).
Reason: no property package of core covers these liquids (aromatic acid chlorides with an
organic acid, HCl in water), so the melter's, absorber's, reboiler's and condenser's heats are
simple heat capacities and latent heats in the script; core has no batch rectification
(core#173).

## D-007 Batch still ST101: one Rayleigh stage at 5 kPa(a) (2026-11-05)
Decision: ST101 is core's batch still (`still:`, core ADR 0055): the crude S5 boiled at 5 kPa(a)
(SRC-1, Example 1: 50 mbar), Raoult's law with the NIST Antoine constants of benzoyl chloride,
benzotrichloride and benzoic acid (SRC-2), ZnCl2 non-volatile, until benzoyl chloride is 40 mol%
of the residue (`end: residue`), ASSUMED so that the bottoms stay a mobile liquid (SRC-1: bottoms
of 20-70 % benzoyl chloride). Boil-up 100 kW net (the vapour that leaves as distillate: a 200 kW
reboiler at the column's reflux ratio 1, D-008), so the recipe's distil takes 1.22 h. Result
(`cheme process stills`): 1308.7 kg of crude a batch give 1243.5 kg of distillate (0.66 mol%
benzoic acid, 0.044 mol% benzotrichloride) and 65.2 kg of residue (53 mol% benzoic acid, 40 mol%
benzoyl chloride, 6.4 mol% ZnCl2), the still from 376.5 to 397.1 K.
Reason: what one stage can do here is separate the light product from a heavy, involatile
residue: at 376 K benzoic acid's vapour pressure is about 1/23 of benzoyl chloride's, so the
Rayleigh still takes off most of the benzoyl chloride while keeping the acid and the catalyst
back. The volatility is declared `assumed` (core reports the basis not sourced): benzoic acid
dimerises in the vapour and no VLE data of the pair show an ideal liquid.
Not modelled (core limits L-1, L-3, L-4): the crude arrives at 413 K, above its 376 K bubble
point at 5 kPa, so part of it flashes as the still is evacuated; the dissolved HCl the crude
holds (zero here, D-005) would leave first, to the vacuum system; no forerun cut, since the
model's crude has no component lighter than benzoyl chloride (the benzaldehyde of a benzal
chloride impurity would make one, D-004).

## D-008 Column K101 on the still: rectification as a specified split (2026-11-05; revisit with core#173)
Decision: the column on C-101 (about 5 theoretical stages, reflux ratio 1, ASSUMED) is a
specified split of ST101's distillate S9 in scripts/balance.py: 99.5 % of the benzoyl chloride,
1 % of the benzoic acid and 2 % of the benzotrichloride to the product S11; the rest, S12, is
the column's reflux returned to the pot and leaves with the residue (M102, S13). Result: 252.53
kg/h of 99.993 wt% product, 2.88 kg/h back to the pot; the residue S13 is 16.27 kg/h (64 g per
kg of product) to hazardous-waste incineration, not recycled. It is drained hot under nitrogen
at 373.15 K (ASSUMED), about 18 K above its ideal benzoic acid liquidus of 355 K (x_BA 0.537;
Tfus 395.2 K, dHfus 18.0 kJ/mol, SRC-2; the ideal liquid of D-007), so the acid does not
crystallise in the drain; ZnCl2 and the non-ideality move the liquidus either way. Overall yield 97.19 % of theory
on the benzotrichloride (SRC-1 Example 1: 96.7 %; description 96-98 %).
Reason: core 1.8.0's still is one stage with no reflux (ADR 0055); one stage gives 0.66 mol%
benzoic acid in the distillate, short of SRC-1's purity, which needs a few stages with reflux.
Core's Fenske-Underwood-Gilliland shortcut is for continuous columns, and a batch column at
constant reflux is the follow-up core#173, so the column's work is a stated split (as
phosphorus-tribromide-1's still was before core 1.8.0). The 0.5 % of the benzoyl chloride the
column returns stands for its hold-up and the intermediate cut at the end of the distillation.
Rejected: the still alone as the product's purification (it would present a one-stage
distillate as the product at 99.4 wt%); a cut sequence of the one-stage still (`cuts:`): with no
lighter component a forerun would have the main cut's composition; the residue's recycle with
excess benzotrichloride (SRC-1, Example 2: from 92.6 % to 97.3 %): a variant, with a tear stream.

## D-009 Utilities and heat (2026-11-05; the model duties and the reboiler's split 2026-11-06)
Decision (scripts/balance.py, year averages, all ASSUMED unless sourced):
- Q1 12.1 kW of MP steam 1100 kPa(a) to the melter: benzoic acid from 298 K (solid cp 175
  J/(mol K), mean, ASSUMED from 146.8 at 298 K) to its melt at 395.2 K, its fusion (18.0 kJ/mol)
  and the liquid to 413 K (259 J/(mol K)), the catalyst, 10 % losses (SRC-2); 30 kW over the 2 h
  melt.
- Q2 5.442 kW from R-101 to cooling water through a pressurised tempered-water loop at 363 K:
  the reaction heat (-50 kJ/mol, D-005, 12.822 kW) less the benzotrichloride's heating from 298
  to 413 K (250 J/(mol K), ASSUMED, 7.380 kW); during the dosing about 23 kW (the model's peak,
  22.8 kW). Since core 1.9.0 R101's semi-batch model writes it (`calculated`, ADR 0059; its one
  heat stream, to cooling water): 5.44216 kW, the 5.4422 kW the script gave until then.
- Q3 15.8 kW from the absorber to cooling water (D-010).
- The still's reboiler, 50.196 kW of LP steam 450 kPa(a) to the still's jacket, the latent heat
  of the distillate S9 (SRC-2's heats of vaporization) times 1 + the reflux ratio 1; 200 kW
  while distilling. It is two streams, both counted in the LCI (`feed:LPS`): Q4 25.0981 kW, the
  net boil-up that leaves as distillate, which core's still model writes (ADR 0059; ST101's
  `energy_port: steam`, `calculated`), and Q6 25.0982 kW, the boil-up the column condenses and
  returns as reflux (the reflux ratio 1 times the same latent heat), ASSUMED from the script,
  since the one-stage still holds no reflux (core#173, L-1). Until core 1.9.0 one typed stream
  held the 50.196 kW; core 1.9.0 compares a typed duty with its model and named the difference
  (`cheme.process-duty`: 50.1964 against 25.0981 kW), which was the reflux share, not an error.
  Rejected: entering the still's `boilup` as the reboiler's 200 kW (the model would then distil
  in half the time, 0.61 h, and present the reflux as distillate), and moving the reflux share
  to K101 (the steam heats the still's jacket, not the column).
- Q5 57.0 kW to cooling water: the column's condenser at the same reflux, and the product
  subcooled from 376.5 to 303 K (187 J/(mol K)).
- Electricity 7 kW: agitators of M-101 (1 kW) and R-101 (3 kW), P1; the still's agitator (1 kW)
  and a dry vacuum pump (5 kW while distilling, about 40 % of the time), P2.
Not counted: the still's heat-up (the crude arrives hot, D-007), heat losses of R-101 and C-101,
the vacuum pump's cooling, the reflux condenser on R-101's off-gas (D-010).

## D-010 HCl off-gas and absorption (2026-11-05)
Decision: the HCl off-gas S6 (33.66 kg/h year average) is absorbed in process water to 30 wt%
hydrochloric acid in A-101, a falling-film absorber with a water tail scrubber (a mixer in the
model, all HCl absorbed): 78.54 kg/h of water, 112.20 kg/h of acid (0.444 kg per kg of product),
the acid at 313 K; heat -64 kJ/mol (the integral heat of solution of HCl in about 4.7 mol of
water, ASSUMED order of magnitude) plus the gas cooled from 413 K.
Reason: SRC-1 absorbs the washed off-gas to about 30 % hydrochloric acid with 18 ppm organic
carbon; selling it as a by-product is the route's practice (D-012 for its allocation).
Not modelled (core limit L-2): at 413 K the off-gas leaving R-101 is saturated with the liquid's
vapour, about 20 kPa of benzoyl chloride (SRC-2's Antoine at 413 K) in 101 kPa; core's vent
carries only the named gas (ADR 0054). The design puts a reflux condenser on cooling water in
R-101's off-gas line (at 305 K, the low end of the Antoine fit, benzoyl chloride's vapour pressure falls to about 0.13 kPa) and
washes the cooled gas with the benzotrichloride feed on its way to R-101 (SRC-1), which returns
the organics to the reactor. Neither is in the balance; the organic carbon in the acid is not
estimated.

## D-011 Thermal screening of the semi-batch and the rate-constant sensitivity (2026-11-05)
Result (`cheme process reactor-hazards`, core ADR 0050, 0054): adiabatic temperature rise of the
whole batch 94.7 K (with -50 kJ/mol); largest accumulation of the dosed benzotrichloride 7.04 %,
at the end of the dosing; MTSR at that moment 421.9 K, against an MTT of 471.0 K
(`hazard.mtt`: the normal boiling point of benzoyl chloride, the liquid's main component; core's
default, the lowest boiling point of the charge and the dose, would be benzotrichloride's 493.8
K, above it: lesson L-5). The vented HCl adds nothing to the MTSR; at the MTSR it forms at 81.6
m3/h, which R-101's vent is sized for (D-014), but only with the assumed rate law: at k/10 and
k/100 the release exceeds the vent capacity (the table below, D-014); with the vent blocked it
pressurises the vessel, which the screening does not assess (D-014).
No TD24 is known (never estimated): no criticality class (`cheme.reactor-hazard-missing`,
info). With MTSR below MTT the class is 1 or 2 if the TD24 lies above the MTSR, and 5 if it
lies below (TD24 < 421.9 K: core's `criticality()` and Stoessel test the TD24 against the MTSR
first, SRC-4); it needs the TD24.
Sensitivity (a scratch copy of the folder, only A divided, everything else as designed,
`hazard.vent_capacity` kept at 100 m3/h; `cheme process propagate --fill`, `reactor-hazards`,
`reactors`, `recipe`; gas release rerun with core 1.9.0 on 2026-11-06):

| k at 413 K | accumulation (end of dosing) | MTSR | MTSR vs MTT 471.0 K | gas release at the MTSR (HCl, 101.3 kPa(a)) vs the vent's 100 m3/h | post-reaction to 0.999 | cycle | class without TD24 |
|---|---|---|---|---|---|---|---|
| 2.7e-3 (design) | 7.04 % | 421.9 K | 49 K below | 0.6547 mol/s, 81.6 m3/h: 0.82 x | 1.37 h | 4.87 h | 1, 2 or 5 |
| k/10 | 25.8 % | 443.3 K | 28 K below | 1.254 mol/s, 164.3 m3/h: 1.64 x (`cheme.reactor-hazard-vent`, warning) | 15.4 h | 18.9 h | 1, 2 or 5 |
| k/100 | 69.8 % | 484.8 K | 14 K above | 3.095 mol/s, 443.2 m3/h: 4.43 x (`cheme.reactor-hazard-vent` and `-mtsr`, warnings) | 160 h | 164 h | 3, 4 or 5 |

The release grows with the accumulation (more benzotrichloride left to react at the MTSR, which
is also hotter), so a slower reaction than assumed does not only raise the MTSR: at k/10 the
vent is exceeded by 64 % before the MTSR comes near the MTT (open design finding, D-014).

MTSR over the batch (core 1.9.0, ADR 0058): 413.1 K at the start, 415.0 K at 0.67 h, 416.6 K at
1.35 h, 421.9 K at the end of the dosing (2.0 h), back to 414.0 K at 2.68 h and 413.3 K at the
end of the post-reaction (3.37 h): the worst moment is the end of the dosing, as the single value
said. Gas release at the MTSR: D-014.
Interpretation: the step is dosing-controlled only if the reaction is fast. All at once (a
batch, accumulation 1) the MTSR would be about 508 K, above the boiling point of benzoyl
chloride, so the dosing, not the dilution, keeps it below the MTT: the dosing must be interlocked
with the temperature, the agitator and the off-gas flow. The off-gas is an online measure of the
accumulation (HCl forms only as the benzotrichloride reacts): a dosing that runs without
off-gas means unreacted benzotrichloride is building up. At k/100 the cycle (164 h) already
rules out the design, before safety does; at k/10 the cycle quadruples and the MTSR is still
below the MTT, but the gas released at the MTSR is 1.64 times R-101's vent capacity (D-014). Open for the next stage: reaction calorimetry with off-gas measurement (heat of
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
Per kg of benzoyl chloride: benzotrichloride 0.715 kg (stoichiometric 0.695), benzoic acid
0.479 kg (0.434), ZnCl2 3.6 g, process water 0.311 kg, nitrogen 8.1 g, electricity 0.028 kWh,
MP steam 0.048 kWh, LP steam 0.199 kWh (Q4 and Q6, D-009), cooling water 0.310 kWh removed; out: 30 wt% acid 0.444
kg (0.133 kg HCl), residue 0.064 kg. Not counted: the vents (emission_exclusions).

## D-013 Dedicated train (2026-11-05)
Decision: M-101, R-101, A-101, C-101 and K-101 make only benzoyl chloride, batch after batch:
1626.7 batches in 7920 h (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train
cannot be checked without the other products' campaigns.
Out of scope, so not LCI gaps: changeover cleaning between campaigns, the idle time of a
multipurpose train, shared tank farms. Benzoyl chloride is also made on continuous plants (SRC-1
Example 3); this entry is the batch case.

## D-014 R-101's vent capacity against the gas released at a cooling failure (2026-11-06)
Result (`cheme process reactor-hazards`, core 1.9.0, ADR 0058): at a cooling failure at the
worst moment (the end of the dosing, 7.04 % of the benzotrichloride accumulated) the reaction
runs on at the MTSR, 421.9 K, and gives off 0.6547 mol/s of HCl, 81.6 m3/h at 421.9 K and
101.3 kPa(a) (per batch of the recipe, from the worst moment's content): 8 % more by volume
(6 % more in moles; 0.6547 against 0.6166 mol/s) than the normal peak of 75.25 m3/h at 413 K
(`cheme process recipe`, D-005). Run to completion the accumulated benzotrichloride
gives 0.317 kmol (10.97 m3) more.
Decision: R-101's off-gas system (the line to A-101, the reflux condenser in it and A-101) is
sized for 100 m3/h of HCl at the vessel's pressure, `hazard.vent_capacity: 100`, ASSUMED: 1.2 x
the gas release at the MTSR with the assumed rate law (98 m3/h), rounded up; the normal peak is then 75 % of it and the
release at the MTSR 82 %, within it (`cheme.reactor-hazard-vent`, info). 100 m3/h of HCl at
421.9 K is 0.80 mol/s, about 54 kW to A-101's cooling at 66.9 kJ/mol (D-010), against 41 kW at
the normal peak. Not in core's comparison (L-2): the gas leaving R-101 carries the liquid's
vapour until the reflux condenser takes it back, about 23 mol% at the MTSR (benzoyl chloride
at x about 0.9 and 26.2 kPa, SRC-2's Antoine at 421.9 K); the vapour line from R-101 to the
condenser is sized for 100 / (1 - 0.23), about 130 m3/h (for example DN80, about 7.6 m/s),
ASSUMED.
Reason: the off-gas system was sized for the normal peak only (D-005), which a cooling failure
at the end of the dosing exceeds. With the assumed rate law the release at the MTSR is only 8 %
above the normal peak the off-gas system must pass anyway, so sizing the system for it (100
against 75.25 m3/h) costs little and is preferred to slowing the dosing. The 1.2 is a margin on
that one case, not on the kinetics: the rate law is ASSUMED (D-005, no calorimetry), and the
capacity is no more credible than the rate constant it was derived from.
Open (design finding, for the next stage): **the vent capacity holds only for the assumed
kinetics.** In D-011's own sensitivity cases the gas release at the MTSR exceeds it: at k/10
1.254 mol/s, 164.3 m3/h at 443.3 K, 1.64 times the 100 m3/h (64 % above it; about 84 kW to
A-101's cooling at 66.9 kJ/mol, against the 54 kW it is sized for), and at k/100 443.2 m3/h,
4.43 times (that case is ruled out by its 164 h cycle anyway, D-011). `cheme process
reactor-hazards` then reports `cheme.reactor-hazard-vent` as a warning and exits 1. Before basic
engineering either (a) the off-gas system (line, reflux condenser, A-101) is sized for the k/10
case, about 200 m3/h of HCl (1.2 x 164.3 m3/h, rounded up), with the vapour line to the reflux
condenser recomputed for the liquid's vapour at 443.3 K, or (b) the dosing rate is set from
reaction calorimetry with off-gas measurement so that the accumulation, and with it the release
at the MTSR, stays within the installed capacity. The flowsheet keeps 100 m3/h, the design
case's basis, until one of the two is decided.
Open (design finding, for the HAZOP and the relief study of the next stage): with the vent
blocked (a flooded or frozen absorber, benzoic acid sublimed into the line) the gas pressurises
R-101, which the screening does not assess (no head-space or relief model, ADR 0058): the 0.317
kmol of the accumulated benzotrichloride alone would raise the 0.41 m3 head space (1.6 m3 vessel,
1.19 m3 of crude) by about 2.7 MPa at 421.9 K, far above what a glass-lined vessel is usually
rated for, and during the dosing the HCl forms all the time. So R-101 needs a relief device
(rupture disc to a catch tank or the scrubber) sized for the gas generation, the benzotrichloride
dosing interlocked on R-101's pressure and on the off-gas flow (D-011), and the off-gas line
traced against benzoic acid deposits. Reasoning only, not a relief sizing.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101 with its HCl vent: composition, accumulation, cooling-failure temperature, peak cooling, off-gas rate, year-average duty Q2 | done in cheme, kinetics ASSUMED | D-005, D-009, D-011, core ADRs 0050, 0054, 0059 |
| MTSR over the batch, gas release at the MTSR against the vent capacity | done in cheme, vent capacity ASSUMED, holds for the assumed kinetics only (exceeded at k/10) | D-011, D-014, core ADR 0058 |
| batch recipe, cycle time, basis check, R-101's vessel and jacket | done in cheme | D-003, core ADRs 0051, 0052 |
| batch still ST101 (one stage): distillate, residue, boil-up time, net latent heat (Q4) | done in cheme, ideal liquid ASSUMED | D-007, D-009, core ADRs 0055, 0059 |
| column K-101 (rectification with reflux) | specified split in a script | D-008, core#173 |
| feeds for 2000 t/a, absorber water, duties Q1, Q3, Q5 and the reboiler's reflux share Q6 | script | D-006, D-009, D-010 |
| off-gas organics (reflux condenser, benzotrichloride wash) | not modelled | D-010, L-2 |
| per-batch nitrogen | done in cheme, amount ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core features used (cheme-as-code 1.8.0, and 1.9.0 since the pin of 2026-11-06)

- `reactor: semibatch` with `batch.dosing` and `batch.target` (ADR 0050) and `batch.vent` for the
  HCl (ADR 0054): two outlets, the vent's peak rate per m3 (`process reactors`) and per batch
  (`process recipe`), the vented gas left out of the MTSR (`process reactor-hazards`);
  `hazard.mtt` on the step.
- `still:` (ADR 0055): Raoult's law with Antoine `vapour_pressure` and `heat_of_vaporization` in
  materials.yaml, `nonvolatile`, `boilup` in kW, `end: residue`; `cheme process stills`.
- `process/recipe.yaml` (ADRs 0051, 0052, 0055, 0057): `dose`/`react` `from:` R101, `distil
  from:` ST101, `units: [ST101, K101, M102]` for one vessel over several steps, R-101's `vessel`
  and `jacket` check.
- `lca.yaml` `consumables` with `per_batch` (ADR 0053), `allocation: shares`.
- 1.9.0: the models' duties (ADR 0059): R101's Q2 on its one heat stream, ST101's Q4 by
  `energy_port: steam`, both written `calculated` by `propagate --fill`, the typed Q6 beside it
  (D-009); the semi-batch screening (ADR 0058): `mtsr_profile`, `gas_release` and
  `hazard.vent_capacity` (D-011, D-014).
- Not used in 1.9.0: `tears:` (ADR 0060; no recycle is modelled), `hazard.reactions` (one
  reaction), the default MTT (still not the product's boiling point, L-5).
- Not used, not needed by this route: `dosing.absorbed` (no gas is dosed), the crystallizer, the
  dryer and the filter (no solids: the benzoic acid is charged molten).

## Core limits hit (each a candidate core issue)

- L-1 (core#173): no batch rectification with reflux. One Rayleigh stage cannot reach the
  product's purity (D-008); the column is a specified split in a script, and the still's
  `boilup` had to be entered as the net distillate rate (100 kW of a 200 kW reboiler at reflux
  ratio 1), so `cheme process stills` reports the net latent heat, not the reboiler's duty. Since
  core 1.9.0 the model writes that net latent heat on Q4 (ADR 0059) and the reflux share is its
  own typed stream Q6; the condenser Q5 is in the script (ADR 0059 leaves condensers typed).
- L-2 (ADR 0054 limitation): the vent carries only the named gas, no vapour of the liquid. At 413
  K benzoyl chloride's vapour pressure is about 20 kPa, so the real off-gas carries roughly a
  fifth of its moles as organics until a reflux condenser and the benzotrichloride wash take them
  back (D-010). Core needs the solvent vapour in the off-gas from the vessel's VLE, with a
  partial (reflux) condenser on the vent.
- L-3 (ADR 0054): no solubility of the vented gas: the dissolved HCl of the crude (fraction 1
  stands in for "none dissolved") is not carried to the still, so the still has no lights cut and
  the vacuum system's HCl load is not known; a dissolved HCl could not be distilled anyway, since
  a still needs an Antoine (HCl is supercritical at 376 K) or an alpha that would be invented.
- L-4 (ADR 0055): the still has no heat-up, sensible heat or flash of a charge hotter than its
  bubble point (the crude arrives at 413 K, its bubble point at 5 kPa is 376 K), and does not size
  its vessel, jacket, condenser or vacuum system: C-101 and K-101 are sized by hand.
- L-5: the default MTT is the lowest boiling point of the charge and the doses; it ignores the
  product formed in the liquid. Here the product, benzoyl chloride (471 K), boils below both the
  charge (benzoic acid, 522 K) and the dose (benzotrichloride, 494 K), so the default would be 23 K
  too high; `hazard.mtt` was set by hand (phosphorus-tribromide-1's L-2 is the mirror case).
  Still so in core 1.9.0: ADR 0058 leaves out vent and dissolved gases, but the products are no
  candidates for the MTT (its known limitations).
- L-6 (as n-bromosuccinimide-1's L-6): core propagates from the feeds and cannot solve them for a
  product rate; the script scales the feeds (two passes of propagate and the script).
- L-7 (resolved in core 1.9.0, ADR 0059): an isothermal semi-batch reported its peak cooling
  duty and the heat released, but no year-average duty for its energy stream, so Q2 came from
  the script. Core 1.9.0 writes it (5.44216 kW, the script's 5.4422 kW), and the still's net
  boil-up Q4 likewise.
- L-8: no model for melting a solid feed (benzoic acid flakes to a melt) in a mixer: Q1 is a
  script value.
- L-9 (ADR 0055): an ideal liquid only; benzoic acid's vapour dimerisation and its non-ideality
  with benzoyl chloride are not representable, so the still's basis is "not sourced".

## Open inputs
Kinetics and heat of reaction by reaction calorimetry with off-gas measurement; TD24 of the crude
and the residue; HCl solubility in hot benzoyl chloride; VLE of benzoyl chloride with benzoic acid
and benzotrichloride at 5 kPa; the column's stages and reflux; the benzotrichloride's impurity
profile (benzal chloride, ring-chlorinated) and the forerun it would need; the residue's recycle
with excess benzotrichloride (SRC-1, Example 2); product specification; prices for the
allocation; a TEA (`operation.batch: {recipe: true}`); R-101's relief device and blocked-vent case,
the off-gas system's capacity against a slower reaction (200 m3/h for k/10, or the dosing rate
from calorimetry), and the off-gas line's hydraulics with the liquid's vapour (D-014).
