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
413 K and 101 kPa(a), 0.12 h into the dosing, when the acid's concentration is highest; the
off-gas line and A-101 are sized for it (equipment list).

## D-006 Balance method and property gate (2026-11-05)
Decision: cheme propagates the melter M101, the semi-batch R101 with both outlets, the absorber
A101 and the residue mixer M102 (mixers), and the still ST101 (one Rayleigh stage, D-007).
scripts/balance.py gives what core has no model for (library ADR 0027): the feeds S1, S2 and S4
that make 2000 t/a (core propagates from the feeds and does not solve them for a product rate;
the balance is linear in the feeds, so the script scales the benzotrichloride by the ratio of
the target to S11, converged in two passes); the column K101's specified split of the still's
distillate S9 into S11 and S12 (D-008); the absorber water S7 (D-010); the duties Q1 to Q5
(D-009). It reads the streams propagate wrote and follows the balance-output contract
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
kg of product) to hazardous-waste incineration, not recycled. Overall yield 97.19 % of theory
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

## D-009 Utilities and heat (2026-11-05)
Decision (scripts/balance.py, year averages, all ASSUMED unless sourced):
- Q1 12.1 kW of MP steam 1100 kPa(a) to the melter: benzoic acid from 298 K (solid cp 175
  J/(mol K), mean, ASSUMED from 146.8 at 298 K) to its melt at 395.2 K, its fusion (18.0 kJ/mol)
  and the liquid to 413 K (259 J/(mol K)), the catalyst, 10 % losses (SRC-2); 30 kW over the 2 h
  melt.
- Q2 5.4 kW from R-101 to cooling water through a pressurised tempered-water loop at 363 K: the
  reaction heat (-50 kJ/mol, D-005) less the benzotrichloride's heating from 298 to 413 K (250
  J/(mol K), ASSUMED); during the dosing about 23 kW (the model's peak, 22.8 kW).
- Q3 15.8 kW from the absorber to cooling water (D-010).
- Q4 50.2 kW of LP steam 450 kPa(a) to the still's jacket: the latent heat of the distillate S9
  (SRC-2's heats of vaporization) times 1 + the reflux ratio 1; 200 kW while distilling.
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
K, above it: lesson L-5). The vented HCl adds nothing to the MTSR; with the vent blocked it
pressurises the vessel, which the screening does not assess (core note: a peak of 0.52 mol/(s m3) of the final content).
No TD24 is known (never estimated): no criticality class (`cheme.reactor-hazard-missing`,
info). With MTSR below MTT the class is 1 or 2 once a TD24 is measured.
Sensitivity (a scratch copy of the folder, only A divided, everything else as designed;
`cheme process propagate --fill`, `reactor-hazards`, `reactors`, `recipe`):

| k at 413 K | accumulation (end of dosing) | MTSR | MTSR vs MTT 471.0 K | post-reaction to 0.999 | cycle | class without TD24 |
|---|---|---|---|---|---|---|
| 2.7e-3 (design) | 7.04 % | 421.9 K | 49 K below | 1.37 h | 4.87 h | 1 or 2 |
| k/10 | 25.8 % | 443.3 K | 28 K below | 15.4 h | 18.9 h | 1 or 2 |
| k/100 | 69.8 % | 484.8 K | 14 K above | 160 h | 164 h | 3, 4 or 5 |

Interpretation: the step is dosing-controlled only if the reaction is fast. All at once (a
batch, accumulation 1) the MTSR would be about 508 K, above the boiling point of benzoyl
chloride, so the dosing, not the dilution, keeps it below the MTT: the dosing must be interlocked
with the temperature, the agitator and the off-gas flow. The off-gas is an online measure of the
accumulation (HCl forms only as the benzotrichloride reacts): a dosing that runs without
off-gas means unreacted benzotrichloride is building up. At k/100 the cycle (164 h) already
rules out the design, before safety does; at k/10 the cycle quadruples and the MTSR is still
below the MTT. Open for the next stage: reaction calorimetry with off-gas measurement (heat of
reaction, heat-flow and gas-flow profile, the ZnCl2 dependence), TD24 of the crude and of the
residue, the gas-generation pressure with a blocked vent (Stoessel's separate criterion), and
the HCl release on a dosing restart after accumulation. Screening values only, not a
reaction-hazard assessment.

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
MP steam 0.048 kWh, LP steam 0.199 kWh, cooling water 0.310 kWh removed; out: 30 wt% acid 0.444
kg (0.133 kg HCl), residue 0.064 kg. Not counted: the vents (emission_exclusions).

## D-013 Dedicated train (2026-11-05)
Decision: M-101, R-101, A-101, C-101 and K-101 make only benzoyl chloride, batch after batch:
1626.7 batches in 7920 h (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train
cannot be checked without the other products' campaigns.
Out of scope, so not LCI gaps: changeover cleaning between campaigns, the idle time of a
multipurpose train, shared tank farms. Benzoyl chloride is also made on continuous plants (SRC-1
Example 3); this entry is the batch case.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101 with its HCl vent: composition, accumulation, cooling-failure temperature, peak cooling, off-gas rate | done in cheme, kinetics ASSUMED | D-005, D-011, core ADRs 0050, 0054 |
| batch recipe, cycle time, basis check, R-101's vessel and jacket | done in cheme | D-003, core ADRs 0051, 0052 |
| batch still ST101 (one stage): distillate, residue, boil-up time, net latent heat | done in cheme, ideal liquid ASSUMED | D-007, core ADR 0055 |
| column K-101 (rectification with reflux) | specified split in a script | D-008, core#173 |
| feeds for 2000 t/a, absorber water, duties Q1 to Q5 | script | D-006, D-009, D-010 |
| off-gas organics (reflux condenser, benzotrichloride wash) | not modelled | D-010, L-2 |
| per-batch nitrogen | done in cheme, amount ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core features used (cheme-as-code 1.8.0)

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
- Not used, not needed by this route: `dosing.absorbed` (no gas is dosed), the crystallizer, the
  dryer and the filter (no solids: the benzoic acid is charged molten).

## Core limits hit (each a candidate core issue)

- L-1 (core#173): no batch rectification with reflux. One Rayleigh stage cannot reach the
  product's purity (D-008); the column is a specified split in a script, and the still's
  `boilup` had to be entered as the net distillate rate (100 kW of a 200 kW reboiler at reflux
  ratio 1), so `cheme process stills` reports the net latent heat, not the reboiler's duty; the
  reboiler and condenser duties at reflux are in the script.
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
- L-6 (as n-bromosuccinimide-1's L-6): core propagates from the feeds and cannot solve them for a
  product rate; the script scales the feeds (two passes of propagate and the script).
- L-7: an isothermal semi-batch reports its peak cooling duty and the heat released, but no
  year-average duty for its energy stream (the reaction heat less the dose's sensible heat):
  Q2 comes from the script, with the same data the model uses.
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
allocation; a TEA (`operation.batch: {recipe: true}`).
