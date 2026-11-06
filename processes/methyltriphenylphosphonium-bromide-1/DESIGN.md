# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Methyltriphenylphosphonium bromide (MTPPB, [Ph3PCH3]Br, CAS 1779-49-3) by the quaternisation of
triphenylphosphine with methyl bromide in toluene, issue ChemE-as-Code/process-library#133.
Concept stage: design basis, batch recipe, balanced BFD/PFD, thermal screening with a rate
sensitivity and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA,
datasheets.

Starting point (2026-11-06): library `main` at b8043f4c, which pins cheme-as-code 1.8.0
(4e8fd80): the batch vent and gas dosing (core ADR 0054), the batch still (0055), precipitation
from a mixed liquor (0056), the dryer and recipe units over several steps (0057), on top of the
semi-batch and the recipe of 1.7.0 (core ADRs 0050 to 0053). The NBS pilot
(`n-bromosuccinimide-1`), `p-toluenesulfonyl-chloride-1`, `carbon-tetrabromide-1`,
`benzoyl-chloride-1` and `sodium-azide-1` (its recycle tears) are the templates;
`methylmagnesium-bromide-1` is the library's other methyl bromide consumer.

Moved to core **1.9.0** (314642c) on 2026-11-06 with the library's pin (D-015): the recovered
toluene's recycle is converged by propagate at the tear S11 instead of by hand (ADR 0060, D-006);
the models write the duties of R101 (Q2), CR101 (Q3) and the still ST101 (Q7) at their
`energy_port` (ADR 0059), and what they leave out, R-101's metal cooled with the slurry and the
still's charge and metal heated to the boil, is on its own streams Q10 and Q9 (D-010); the
screening's default MTT at R-101's pressure is checked and the hand MTT of the closed vessel kept
(ADR 0058, D-011). R101 has no vent, so there is no gas release to compare with a vent capacity.
`plant.yaml` requires `cheme-as-code>=1.9`.

Moved to core **1.10.0** (c55e9c7) on 2026-11-06 (D-016): the still's charge heated to its
bubble point (`still.heat_up`) and the vessels' metal (`vessel.metal_heat_capacity` on the
recipe's vessels R-101 and C-101, ADR 0063) are in the models' duties Q7 and Q3, so the hand
streams Q9 and Q10 went; R-101's heating and cooling times count its metal; C-101 is sized by the
recipe (L-1 resolved). The batch rectification (ADR 0061) and the vent's vapour and condenser
(ADR 0062) were checked and not adopted (D-016). `plant.yaml` requires `cheme-as-code>=1.10`.

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US3334144A, Monsanto Research Corp., 1967: Process for making alkyltriaryl-phosphonium compounds, https://patents.google.com/patent/US3334144A/en | background: phosphonium salts are made by heating a tertiary phosphine with an alkyl halide; for methyltriphenylphosphonium bromide, PPh3 with methyl bromide, usually in benzene; this needs a pressure vessel, since methyl bromide boils at a few C and 50 C or more is needed for a reasonable rate. Example 1: PPh3 with dibromomethane in refluxing methanol for 24 h under nitrogen, about 30 % conversion, the salt precipitated from the evaporated syrup with benzene, mp 224-226 C, identified by its infrared spectrum | read (Google Patents text); patent, facts only | D-001, D-005, D-007 |
| SRC-2 | Wikipedia, Methyltriphenylphosphonium bromide, https://en.wikipedia.org/wiki/Methyltriphenylphosphonium_bromide | the route Ph3P + CH3Br -> Ph3PCH3Br, a white salt soluble in polar organic solvents, the precursor of the Wittig reagent; cites Wittig and Schoellkopf, Org. Synth. 40, 66 (1960) | read; CC BY-SA, facts only | D-001, D-007 |
| SRC-3 | Wittig, G.; Schoellkopf, U. (1960) Methylenecyclohexane, Org. Synth. 40, 66, doi:10.15227/orgsyn.040.0066 | - | **not read**: orgsyn.org answered with a browser check (2026-11-06); not worked around. Nothing is taken from it | lead only |
| SRC-4 | PubChem CID 74505 (MTPPB), 11776 (PPh3), 6323 (methyl bromide), 13097 (Ph3PO), https://pubchem.ncbi.nlm.nih.gov | identities (formula, InChIKey); MTPPB: white hygroscopic powder; PPh3 (HSDB): mp 80.5 C, density 1.075 g/cm3 at 80 C and 1.194 at 25 C, freely soluble in ether, soluble in benzene, practically insoluble in water; methyl bromide made from methanol and hydrogen bromide (HSDB, Methods of Manufacturing, as methylmagnesium-bromide-1 records it) | read (PUG REST and PUG View, 2026-11-06) | materials, registry, D-004, D-012 |
| SRC-5 | Wikipedia, Bromomethane, https://en.wikipedia.org/wiki/Bromomethane | boiling point about 4 C, vapour pressure 190 kPa at 20 C, water solubility 17.5 g/L; NIOSH IDLH 250 ppm, ACGIH TLV-TWA 1 ppm, effects delayed by hours, a potential occupational carcinogen (NIOSH); added to the Montreal Protocol's phase-out list by the 1990 London Amendment | read; CC BY-SA, facts only | D-011, D-014 |
| SRC-6 | Property data of core's environment and the NIST WebBook: the `chemicals` 1.5.2 package (its packaged CRC tables: `CRC_organic_data` for the density of liquid PPh3, `heat_capacity.CRC_standard_data` for PPh3's solid heat capacity, `phase_change.Tb` and `Tm`, the Wagner (McGarry) vapour pressure of methyl bromide and the Helmholtz equation of state of toluene), thermo 0.11 (liquid densities, heat capacities and heats of vaporisation of methyl bromide and toluene), CoolProp's IAPWS water (LP steam saturation), and the NIST Chemistry WebBook, SRD 69 (toluene's Antoine set and heats of vaporisation, methyl bromide's heat of vaporisation; `cheme chemistry props --source NIST`) | per component in `process/materials.yaml`, the dryer's latent heats (D-008) | open data packages queried and WebBook pages read (2026-11-06); facts only. The CRC values come from the tables packaged in `chemicals`, not from the printed (licensed) handbook | materials, D-005, D-008, D-009, D-011 |
| SRC-7 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR, the MTT (for a closed system the temperature at the maximum permitted pressure) and the criticality classes (method, implemented in core ADR 0050) | method reference, no data taken | D-011 |
| SRC-8 | processes/btx-1, asu-1, methylmagnesium-bromide-1, methanol-1, hydrogen-bromide-1, phosphorus-oxychloride-1 (this library) | toluene (a co-product of reformate extraction), gaseous nitrogen; the methyl bromide proxy (methanol + HBr) as methylmagnesium-bromide-1 records it; PCl3, internal to phosphorus-oxychloride-1 | library, internal | feed links and proxies (D-012) |
| SRC-9 | US5527966A (PPh3 from PCl3, chlorobenzene and sodium) and CN107840792A (PPh3 with methanol and 48 % HBr) | - | **not read** in this session (named by the route scouting; CN107840792A seen only as a supplier page's citation) | leads only, nothing taken |
| SRC-10 | Ullmann's Encyclopedia of Industrial Chemistry, Phosphorus Compounds, Organic | - | not read (licensed) | not cited as read |

Searched and not found openly (2026-11-06): kinetics or reaction calorimetry of PPh3 with
methyl bromide, a formation enthalpy of the salt (the NIST WebBook lists none), the salt's
solubility in toluene, its density and heat capacity, a TD24 of the salt or the reaction mass,
a plant's specific consumptions, a product specification beyond the supplier records, and a
market volume.

## D-001 Route and boundary (2026-11-06)
Decision: Ph3P + CH3Br -> [Ph3PCH3]Br (SRC-2) in toluene in a closed glass-lined pressure vessel
(SRC-1: a pressure vessel, 50 C or above), on a dedicated train (D-013):
- R-101: PPh3 dissolved in recovered toluene (20 wt%), heated to 333 K, liquefied methyl bromide
  pumped in over 3 h (a semi-batch), post-reaction to 0.99 conversion of the PPh3; the salt
  precipitates (it separates from benzene, SRC-1 Example 1, and toluene is as non-polar);
  cooled to 313 K; depressurised and swept with nitrogen to the thermal oxidiser;
- F-101 (agitated filter-dryer): filtration, one reslurry wash with recovered toluene, its
  filtration, vacuum drying at 333 K; E-201 condenses the dryer's toluene on brine;
- C-101 (batch still): the mother liquor, wash filtrate and dryer condensate distilled; the
  toluene with the remaining methyl bromide reused for the next charge and the wash; the residue
  to incineration.
Boundary feeds: PPh3, liquefied methyl bromide, toluene make-up, nitrogen (per batch),
electricity, LP steam; returns: cooling water, chilled brine; outputs: the dried salt, the vent
gas to the site's thermal oxidiser, the still residue to incineration.
Reason: the issue names this route, and it is the textbook one with 100 % atom economy; the
only open industrial statement (SRC-1) is the pressure vessel at 50 C or above.
Rejected:
- benzene as the solvent (SRC-1's usual one): toluene does the same job with a far lower
  toxicity; ASSUMED equivalent for the reaction and the precipitation;
- methyl bromide dosed as a gas with `dosing.absorbed` (as methylmagnesium-bromide-1 does): the
  source names a pressure vessel, not a sparged gas; liquid dosing keeps the vessel closed, so
  no methyl bromide leaves while it reacts;
- SRC-1's own route (dibromomethane in methanol): about 30 % conversion in 24 h and
  triphenylphosphine oxide as a by-product; a variant;
- PPh3 with methanol and HBr (SRC-9, not read): a laboratory lead only.
Links: toluene from btx-1, nitrogen from asu-1. No library process makes PPh3 or methyl bromide
(D-012).

## D-002 Capacity, product and operating hours (2026-11-06)
Decision: one 6.3 m3 R-101 with 3.0 kmol of PPh3 per batch (ASSUMED), 7920 h/a (330 days of
24 h); the recipe gives 776.6 batches a year of 1057.10 kg, 820.9 t/a of dried salt. Modelled
product: 99.87 wt% salt as crystals (99.88 wt% with the salt the residual liquor holds), 0.10 wt%
toluene, 0.02 wt% PPh3.
**The 99.87 wt% and the 98.5 % yield (D-005) are ASSUMED upper bounds, not a specification**: no
open source of this route gives a yield or an assay (SRC-3 not read), and triphenylphosphine
oxide (from traces of air), water (the salt is hygroscopic, SRC-4) and other impurities are not
modelled. The product specification is an open input.
Reason: no open market or plant figure was found; the salt is a fine-chemical reagent (the Wittig
methylenation, SRC-2). The LCI is per kg and does not depend on the scale; the batch size does
(D-003).

## D-003 Batch basis, recipe and vessels (2026-11-06)
Decision: one batch makes 1057.10 kg of dried salt (stream S15); `process/recipe.yaml` has three
unit procedures:
- REACT on R-101, one vessel over M101, E101, R101, CR101 and DG101 (`units`, core ADR 0057):
  nitrogen purge and pressure test 0.5 h, charge the recovered toluene 0.5 h and the PPh3 0.75 h,
  heat 292.81 -> 333.15 K 0.79 h (from the jacket on hot water at 353 K, with R-101's metal since
  core 1.10.0, D-016; 0.53 h without it), dose 3.0 h and post-reaction 2.30 h to 0.99 conversion
  of the PPh3 (both from R101's model), cool to 313 K 0.81 h (jacket, with the metal; 0.55 h
  without), precipitation hold 0.5 h, vent and sweep 0.5 h, press the slurry to F-101 0.5 h:
  10.15 h;
- ISOLATE on F-101 over F101, W101, F102 and D101: receive 0.5 h, filtration 1.17 h and 0.46 h
  (Ruth, from the filters' data, on the vessel's bottom), reslurry wash 0.5 h, drying 6.57 h
  (D101's 315.3 kg of vapour a batch at 4 kg/(m2 h) on 12 m2), cool and discharge 1.0 h:
  10.20 h;
- RECOVER on C-101 over ST101 and X101: receive 0.5 h, heat-up to the bubble point 0.81 h
  (ASSUMED, the heat ST101's duty holds at its 250 kW, D-016), boil-up 1.66 h (ST101's model at
  250 kW), drain 0.5 h: 3.47 h.
F-101 is the bottleneck: cycle 10.198 h, 776.6 batches in 7920 h; R-101 is 99.5 % occupied
(10.15 h, 0.05 h short of the bottleneck: its heating time is conservative, D-016); one batch
takes 22.31 h from the purge to the still's drain. The flowsheet's flows are the recipe's
year averages: 1057.10 kg x 776.6 / 7920 h = 103.655 kg/h of S15 (no `cheme.recipe-basis`
finding). The feeds are the per-batch charges over the cycle, and the cycle was iterated to a
fixed point with them (lesson L-6).
Vessels (fill 0.8, H/D 1.2 for R-101 and 1.0 for F-101, ASSUMED), sized by the recipe:
- R-101 6.3 m3 (4.435 m3 of batch, 70 %, D 1.88 m). Its jacket (U 300 W/(m2 K), glass-lined,
  12.1 m2 wetted at the charge) on cooling water: core takes one constant coolant temperature,
  so the log-mean equivalent of the 298.15/308.15 K water at the 333.15 K content is entered,
  333.15 - (35 - 25)/ln(35/25) = 303.43 K, not the supply temperature. It removes 107.5 kW
  against R101's peak 27.25 kW (`cheme process recipe`). For the cool-down to 313 K the same
  mean is conservative (the return falls towards the supply as the content cools).
- F-101 6.3 m3 (4.417 m3 of batch, 70 %, D 2.0 m), its heated area 12 m2 (jacket, heated bottom
  and agitator, ASSUMED).
- C-101 6.3 m3 (4.852 m3 of liquor a batch, 77 %, D 1.88 m; fill 0.8 and H/D 1.2 ASSUMED, as
  R-101), sized by the recipe from what ST101 takes in since core 1.10.0 (ADR 0063, L-1
  resolved, D-016); the hand estimate it replaces was the same 6.3 m3. No jacket check: core
  checks none on a still's vessel; the boil-up's 250 kW is ASSUMED (D-009).
- The metal of R-101 (3000 kJ/K) and C-101 (2500 kJ/K), ASSUMED (D-010), is given on their
  recipe vessels (`metal_heat_capacity`, core 1.10.0): in R-101's heat and cool times and in
  the duties of CR101 (Q3) and ST101 (Q7). F-101's metal stays in D101's dryer model (its own
  vessel heat capacity, 4000 kJ/K) and Q6.
Reason: core ADR 0051 puts the batch basis in one place; the dosing, reaction, heating, cooling,
filtration, drying and boil-up times come from the models, so a change of the kinetics, the
jacket, the cake or the drying rate changes the cycle (D-011 shows by how much). There is no
rinse between batches: the train is kept dry and closed (the salt is hygroscopic, D-012).

## D-004 Feeds and charge (2026-11-06)
Decision, per batch:
- PPh3 3.0 kmol (786.9 kg), technical grade, modelled pure (its oxide not modelled);
- toluene 4.0 kg per kg PPh3 in the charge (20 wt% PPh3; 3147.5 kg): recovered toluene from
  T-202 (S3) and the make-up (S2, 59.1 kg a batch, 0.056 kg per kg salt), dry;
- methyl bromide 1.05 mol per mol PPh3 in R-101 (3.150 kmol): the fresh dose S6 (3.134 kmol,
  297.5 kg) and the 0.016 kmol the recovered toluene brings back. The fresh methyl bromide is
  1.045 mol per mol of PPh3 fed, 0.281 kg per kg salt: most of the excess goes to the oxidiser
  (D-007). From a liquefied store at 298 K (190 kPa vapour pressure at 293 K, SRC-5), pumped at
  800 kPa(a), above R-101's relief set pressure.
Reason: a small excess of the cheap, volatile alkylating agent drives the PPh3 to a high
conversion; 20 wt% PPh3 keeps the slurry at about 25 wt% solids for the agitator and the
filter. PPh3 is soluble in benzene (SRC-4); its solubility in toluene at 20 wt% is ASSUMED (it is
charged into the warm toluene and dissolved on heating).

## D-005 Reaction model, kinetics and heat (2026-11-06)
Decision:
- R101 is `reactor: semibatch` (core ADR 0050) at 333.15 K, isothermal, 230 kPa(a) (the
  nitrogen pad): the charge S5 (with the recycled methyl bromide), the liquid methyl bromide S6
  dosed over 3 h at a constant rate, then the post-reaction to 0.99 conversion of the PPh3
  (`batch.target`; 2.30 h). No vent: the vessel is closed and the methyl bromide stays in the
  liquid (its partial pressure over the liquor is in D-011).
- Rate law, ASSUMED: QUAT second order in PPh3 and methyl bromide, k 5.0e-3 m3/(kmol s) at
  333 K, Ea 70 kJ/mol. No open kinetics were found; SRC-1's "a reasonable rate at 50 C or above"
  is the only anchor. It makes the dosing nearly dosing-controlled: 14.7 % of the methyl bromide
  accumulates at the end of the dosing (D-011).
- Heat of reaction, ASSUMED: -100 kJ/mol from dissolved PPh3 and liquid methyl bromide to the
  precipitated salt, its heat of crystallisation included (CR101 adds none). No calorimetry and
  no formation enthalpy of the salt were found; a Menshutkin alkylation forming a crystalline
  salt is of the order of -80 to -120 kJ/mol, the upper end taken for the screening.
- The salt is carried dissolved (MTPPB) in R101, since core's semi-batch is liquid only; it
  crystallises in CR101 (L-2).
Result: QUAT 0.29123 kmol/h (2.970 kmol a batch); the PPh3 0.99 converted.
**The low accumulation in D-011 is a consequence of the assumed rate law** and must be
confirmed by reaction calorimetry before basic engineering.

## D-006 Balance method and the recycles (2026-11-06)
Decision: every unit but two is calculated by `cheme process propagate` (core 1.9.0): the
semi-batch R101, the crystallizers CR101 and W101, the filters F101 and F102, the dryer D101,
the still ST101, the mixers M101, M201, M202, the pass-through E101 and the recycle splitter
X101 (S3 its remainder). The hand splits are DG101 (the vent losses, D-007) and E201 (the vacuum
condenser, D-008): core has neither a degassing nor a condenser with non-condensables. No
balance script.
The recovered toluene's recycle is converged by propagate at a declared tear (core 1.9.0, ADR
0060; flowsheet `tears:`): the wash S11. Every loop propagate sees runs through it (X101 -> S11
-> W101 -> F102 -> S14 -> M201 -> ST101 -> S19 -> X101), so the plant is torn once. The
charge's path (X101 -> S3 -> M101 ... R101 -> CR101 -> DG101) is no loop for propagate: DG101 is
a hand split whose assumed outlets it does not derive, so S3 is simply X101's remainder (S19 less
S11), calculated. S11's flow is the ASSUMED wash ratio of D-008 (1 kg of recovered toluene per kg
of salt in the cake, 103.673 kg/h), a design input held fixed on the tear; its composition is
iterated by Wegstein's method from a first guess (the hand-converged values rounded to 4
digits) to 1e-6 kg/h + 1e-9 relative per component, far tighter than the balances' tolerance
(abs 0.02 kg/h, rel 0.001), so that the six digits written are the fixed point's (as
sodium-azide-1 does): 3 iterations, worst residual 2.15e-16 kg/h (`cheme.process-recycle`,
info). The loop's gain is small: S11 brings a quarter of the still's charge, and only its
methyl bromide content is iterated.
The fresh PPh3, toluene and methyl bromide (S1, S2, S6) stay ASSUMED at the per-batch charges of
D-004 at the converged recycle, and the cycle, which sets the hourly flows of those charges, at
its fixed point (L-6): core has no design specification on a feed (ADR 0060, core#181 part 2).
DG101 and E201 follow their rules from the calculated S8 and S21 (S23 90 % of S8's methyl
bromide with the toluene that saturates the nitrogen, S18 all of S21's methyl bromide with the
toluene that saturates it at 268 K, S22 and S16 the remainders), re-derived after the tear moved
S8 and S21 and repeated with `propagate --fill` until S22, S23, S16 and S18 no longer change in
their written digits (two rounds); with X101 they balance within the flowsheet's tolerance,
which `cheme validate` checks.
Until core 1.9.0, S3 and S11 were ASSUMED tear streams converged by hand (successive
substitution over `cheme process propagate --fill` with a scratch driver outside the folder,
until the change was below 2e-7 relative, L-5). Against that, every calculated flow written is
the same to its six digits (S3 302.99 kg/h, the product S15 103.655 kg/h) but the vent header's,
S24 2.2757 to 2.27572 kg/h, which follows the re-derived hand splits S23 (2.25764 to 2.25766)
and S18 (0.0180598 to 0.0180586 kg/h); the largest change of a fraction is 6.8e-5 relative
(methyl bromide in the charge S5, 0.000438416 to 0.000438386 mol fraction), inside the
balances' tolerance. A change to an upstream value now makes the tear stale, and `propagate --fill`
converges it again; what stays set by hand has to be reset after such a change: S11's flow (1 kg
per kg of salt in S9, D-008: the tear iterates only its composition, so a change of the yield or
the solubility would otherwise break the wash ratio), the fresh feeds S1, S2 and S6 (the charge
ratios, D-004), the cycle (L-6) and the hand splits DG101 and E201 (L-3).

## D-007 Precipitation and the vent losses (2026-11-06)
Decision:
- CR101 (in R-101) is `crystallizer: basis: solubility` for MTPPB in toluene, crystal MTPPB_S,
  at 313.15 K, with the dissolved PPh3 and methyl bromide as spectators (core ADR 0056).
  Solubility 0.5 g per kg toluene, `measured_in: pure_solvent`, ASSUMED (no measured value: the
  salt separates from benzene, SRC-1, and dissolves in polar solvents, SRC-2), with `salting_out`
  coefficients of 0 (no data). Its energy block gives the slurry's cool-down from 333.15 K
  (1.54 kJ/(kg K), the components' heat capacities). 0.15 % of the salt stays dissolved in the
  mother liquor.
- DG101 (a hand split, L-3): R-101 is depressurised and swept with 10 Nm3 of nitrogen to the
  vent header before the transfer, and F-101's two filtrations are pressed with 38 Nm3 of
  nitrogen at 300 kPa(a); together they take 90 % of the slurry's dissolved methyl bromide
  (ASSUMED) and the toluene that saturates that nitrogen at 313 K (7.84 kPa: 0.0829 kmol a
  batch). Per batch 15.4 kg of methyl bromide and 7.6 kg of toluene go to the vent header (S23),
  joined by the vacuum condenser's exhaust (S18: 0.16 kg methyl bromide, 0.02 kg toluene) to
  the site's thermal oxidiser (S24, 0.022 kg per kg salt). The headspace alone would hold about
  1.1 kg of methyl bromide (1.87 m3 at the liquor's 16.6 kPa partial pressure, x 0.0048 x 344
  kPa at 313 K, Raoult; my arithmetic); the sweep and the pressing gas take the rest.
- The methyl bromide is not recovered from the vent: a condenser on brine or an adsorber could
  return most of the 15.4 kg a batch; a variant (D-014).
Reason: the slurry must be free of most of the dissolved methyl bromide before the filter-dryer
is opened to the nitrogen and the vacuum system (SRC-5: IDLH 250 ppm, TLV 1 ppm); routing the
excess to the oxidiser, not to the recovered toluene, keeps the recycled toluene nearly free of
it (0.05 wt%). The 90 % is an ASSUMED stripping efficiency; the vent fraction stands in for a
vapour-liquid equilibrium core does not model in a batch (core ADR 0054's known limits, L-3).

## D-008 Filtration, wash and drying (2026-11-06)
Decision:
- F101, F102: specified splits, 99.8 % and 99.9 % of the solid to the cake, 0.3 kg of liquor per
  kg of solid, ASSUMED; Ruth filtration times from ASSUMED cake data (specific cake resistance
  1e10 m/kg, medium 1e10 1/m, 200 kPa of nitrogen; toluene's viscosity at the liquors'
  temperatures, 0.47 and 0.50 mPa s, thermo) on F-101's bottom.
- W101: one reslurry wash with 1 kg of recovered toluene per kg of salt (1057 kg a batch,
  ASSUMED), a crystallizer fed by the cake and the wash (core ADR 0056), its crystals dissolving
  to saturation (0.05 %). It is adiabatic (`process/simulation.yaml`), so its temperature is the
  mix of its inlets with the components' liquid heat capacities: the cake S9 (163.24 kJ/(K h) at
  313.15 K) and the wash S11 (176.71 kJ/(K h) at 303.15 K) give 307.95 K (S12, S13, S14). It
  takes the PPh3 the cake carries from 0.075 to 0.017 wt% of the product.
- D101: vacuum drying at 333.15 K and about 5 kPa(a) to 0.1 wt% volatiles (toluene and methyl
  bromide in their inlet ratio, ASSUMED; core's `dryer:`). Energy: the wet cake 1.21 kJ/(kg K)
  (the salt's 1.064 with 0.3 kg toluene at 1.705 per kg), latent heats at 333 K toluene 391 kJ/kg
  (36.0 kJ/mol, NIST WebBook) and methyl bromide 234 kJ/kg (22.2 kJ/mol, thermo; SRC-6),
  F-101's steel 4000 kJ/K (about 8 t, ASSUMED) heated each batch from the cake's 307.95 K, 70 %
  efficiency; 10.35 kW year average. Drying rate 4 kg/(m2 h) (ASSUMED, toluene at 333 K with hot
  water at 353 K) on 12 m2; wet-cake density 950 kg/m3 (ASSUMED). The product is cooled in
  F-101 to 313 K on cooling water and discharged under nitrogen (it is hygroscopic).
- E201 (a hand split, L-3): the dryer's vapour S21 is condensed on brine at about 268 K; all of
  its methyl bromide stays a gas (its vapour pressure at 268 K, about 60 kPa, is far above its
  partial pressure at the 5 kPa(a) vacuum) and leaves with the toluene that saturates it
  (0.65 kPa against 5 kPa(a): 0.148 mol per mol of gas; the leak nitrogen not counted) by the
  vacuum pump to the vent header (S18); the toluene condensate (S16) goes to T-201.
Reason: a filter-dryer keeps the toxic, hygroscopic product closed from the slurry to the drum
(NBS's and carbon-tetrabromide-1's choice); drying at 333 K stays far below the salt's melting
point (about 503 K, SRC-6; 224-226 C for SRC-1's sample) and the hot water's 353 K below every
temperature limit of the batch (D-010).

## D-009 Toluene recovery in the batch still (2026-11-06)
Decision: the mother liquor, the wash filtrate and the dryer condensate (M201, mixed adiabatically
to 308.47 K) go to C-101, a batch still at 101.325 kPa(a) (`still:`, core ADR 0055) on Raoult's
law with the Antoine vapour pressures of `process/materials.yaml` (toluene and methyl bromide;
PPh3 and the salt non-volatile, `nonvolatile`), boiled up at 250 kW on LP steam, until 98.5 % of
the charge's mass is distilled. Per batch: 4210 kg charged, 4147 kg of distillate (99.95 mol%
toluene, 0.05 mol% methyl bromide) condensed and cooled to 303 K on cooling water, split in
X101 to the next charge (S3) and the wash (S11); 63.2 kg of residue (toluene with 12.2 wt% PPh3,
8.1 wt% salt) drained at 386.5 K to the waste tank and to incineration. The still runs from
383.5 to 386.5 K; the vapour pressures are fitted by us over 300-420 K (SRC-6) because the NIST
sets end below that (toluene at 384.66 K). The charge enters at 308.47 K and is heated to its
383.50 K bubble point first: since core 1.10.0 in ST101's duty (`still.heat_up`, with C-101's
metal, D-016).
Reason: the toluene is 4 kg per kg PPh3 and must be reused; PPh3 and the salt do not distil
(below 3 Pa vapour pressure at 384 K, thermo), so one stage separates them: **a recovery cut by
a single-stage still is credible here**, unlike a product purification. Distilling everything
rather than recycling the mother liquor directly keeps PPh3 oxide and other impurities from
building up (none is modelled), at the cost of the unconverted PPh3 (1 % of the charge) in the
residue.
Rejected: the mother liquor recycled directly with a purge (sodium-azide-1's pattern): it would
return the unconverted PPh3 but carry the excess methyl bromide and the oxide round the loop; a
variant once an impurity balance exists.

## D-010 Utilities and heat (2026-11-06)
Decision (year averages; since core 1.9.0 the models write Q2, Q3 and Q7 at their
`energy_port`, `calculated` by `cheme process propagate --fill`, ADR 0059, and since core 1.10.0
Q3 and Q7 hold the vessels' metal and Q7 the charge's heat-up, ADR 0063, D-016; the rest is hand
arithmetic from cheme's reports, given in the flowsheet's sources;
`tests/test_methyltriphenylphosphonium_bromide_1.py` recomputes them):
- LP steam 350 kPa(a), as heat delivered:
  - Q1 8.562 kW: the charge S4 heated from 292.81 to 333.15 K (618.7 kJ/(K h)), and R-101's metal
    (3000 kJ/K, about 6 t of glass-lined steel, ASSUMED) from 313.15 to 333.15 K each batch.
    S4's temperature is the adiabatic mix of S1, S2 and S3 less the PPh3's heat of solution,
    20 MJ/kmol ASSUMED (its heat of fusion by Walden's rule, about 56 J/(mol K) at its 353 K
    melting point; no measured value found), 60 MJ per batch (5.9 MJ/h), so Q1 counts the
    dissolution. It stays hand arithmetic (E101 is a pass-through, no model; D-016): core
    1.10.0's recipe reports R-101's heat-up as 10.224 kW (375.4 MJ a batch), the same content's
    254.3 MJ but the metal heated from the charge's 292.81 K (121.0 MJ), since core starts the
    metal at the content's temperature; it was left at 313.15 K by the previous batch's
    cool-down, so the hand 60.0 MJ stands and the 1.662 kW difference is that start;
  - Q4 10.347 kW: the dryer (core's model, D-008);
  - Q7 60.6328 kW: ST101's model duty (`energy_port: steam`, `calculated`), 618.3 kWh a batch:
    the boil-up's latent heat 40.6685 kW (414.7 kWh), the charge S17 heated from 308.47 K to its
    383.50 K bubble point 14.6525 kW (149.4 kWh, `still.heat_up`) and C-101's metal (2500 kJ/K,
    about 5 t, ASSUMED) from 308.47 to the end's 386.48 K 5.3118 kW (the RECOVER vessel's
    `metal_heat_capacity`), core 1.10.0 (D-016).
  Until core 1.9.0 one typed stream Q7 held all three, 60.628 kW; core 1.9.0 wrote the boil-up
  alone at the `energy_port` and the heat-up and metal were the hand stream Q9 (19.9639 kW),
  60.6324 kW together; core 1.10.0 writes all three on Q7, 0.0004 kW above that sum (Q9's
  rounded kJ/h).
  R-101 and F-101 are heated with hot water at 353 K from LP steam, C-101 with the steam at
  412 K: below every temperature limit the design states (R-101's MTT 415.29 K, D-011; the
  salt's melting point, about 503 K). The steam is only 3 K below R-101's MTT, so it must never
  reach R-101's jacket directly: R-101 sees only the 353 K hot-water circuit. No decomposition
  temperature of the salt, PPh3 or the still residue is known (open input, D-011).
- cooling water 298/308 K:
  - Q2 7.8775 kW: the heat of quaternisation (0.29123 kmol/h x 100 MJ/kmol) less the dose warmed
    from 298 to 333 K; R101's semi-batch model writes it (`energy_port: q`, `calculated`), equal
    to the hand value it replaced (7.8775 kW);
  - Q3 5.1858 kW: CR101's model duty (`energy_port: q`, `calculated`): the slurry S7 cooled
    from 333.15 to 313.15 K, its lumped duty (its energy block, 1.54 kJ/(kg K)), 3.55153 kW, and
    since core 1.10.0 R-101's metal (3000 kJ/K, as Q1, the REACT vessel's
    `metal_heat_capacity`) cooled by the same 20 K each batch, 1.63427 kW (D-016). Until core
    1.9.0 a typed Q3 held both, 5.1858 kW; core 1.9.0 wrote the slurry alone and the metal was
    the hand stream Q10 (1.6342 kW), which core 1.10.0's term equals; the recipe's cool-down
    report gives the same 190.3 MJ a batch (5.185 kW);
  - Q6 3.359 kW: the product cooled from 333.15 to 313.15 K in F-101 and F-101's metal cooled
    back to the cake's 307.95 K each batch (as core's dryer model assumes);
  - Q8 56.426 kW: the still's condenser (the distillate at its components' heats of
    vaporisation, 40.669 kW, the boil-up term of Q7) and the distillate cooled from the still's
    mean 384.99 K to 303.15 K (15.758 kW). It stays hand arithmetic: core 1.10.0's
    `still.condenser_port` would write the latent heat alone (D-016).
- chilled brine 258/263 K: Q5 4.308 kW, F-101's vacuum condenser E-201: 30.90 kg/h of toluene
  condensed (391 kJ/kg), the condensate cooled from 333 to 268 K and the vent gas by 65 K. It is
  on brine: toluene's dew point at the filter-dryer's 5 kPa(a) is about 304 K (303.6 K by the
  Antoine set of `process/materials.yaml`), so cooling water at 298/308 K cannot condense it; at
  the 268 K outlet its vapour pressure is 0.65 kPa.
- electricity 16.0 kW: R-101's 5.5 kW agitator at 99.5 % occupancy and the dosing pump (5.7 kW),
  F-101's 7.5 kW agitator half the time and the 5.5 kW vacuum pump over the drying (7.3 kW),
  C-101's agitator at 34 % occupancy and the transfer pumps (3.0 kW). All ASSUMED. Until core
  1.10.0 15.5 kW (R-101 94 %, 5.4 kW; C-101 26 %, 2.8 kW): the occupancies follow the recipe's
  longer heating and cooling and the still's heat-up (D-016).
Per kg of salt: LP steam 0.767 kWh, cooling water 0.703 kWh, brine 0.042 kWh, electricity
0.154 kWh (core 1.9.0's exact boil-up raised the LP steam from 0.76732 to 0.76737 kWh, the same
to three digits; core 1.10.0's Q7 and Q3 leave LP steam and cooling water the same to five
digits, and the electricity rises from 0.150 kWh).
Every energy flow of the batch is in the flowsheet and so in the LCI per kg (library ADR 0035),
including the dissolution of the PPh3, the vessels' metal, the still's heat-up and the vacuum
condenser. Recorded exclusions, with their size:
- the heat of mixing of the dosed liquid methyl bromide with toluene (both of low polarity; an
  excess enthalpy of at most 1 kJ/mol of methyl bromide ASSUMED, no data): at most
  0.30 kmol/h x 1 MJ/kmol = 0.08 kW, 1 % of Q2;
- the sensible heat of the residue drained hot (6.19 kg/h, 386.5 to about 300 K, about
  0.25 kW): it leaves to the waste tank, no utility removes it;
- the vent gas S24 leaves at 312.9 K (the adiabatic mix of S23 and S18, D-007) to the oxidiser,
  not cooled;
- heat losses and gains of the vessels and tanks; the heat of the nitrogen.
W101 is adiabatic (`process/simulation.yaml`); M201 and M202 mix adiabatically (S17 308.47 K,
S24 312.87 K, from their inlets' heat capacities).

## D-011 Thermal screening, pressure and the rate sensitivity (2026-11-06)
Result (`cheme process reactor-hazards`, core ADR 0050; the same on core 1.9.0): R101 T_p 333.15
K, adiabatic rise of the whole batch dT_ad 46.0 K; the largest accumulation of the dosed methyl
bromide 14.7 % at the end of the dosing; the MTSR at the worst moment (10132 s) 339.1 K. The
MTSR over the batch (core 1.9.0, `mtsr_profile`, ADR 0058): 333.4 K at the start, 335.0 K at
1.04 h, 336.6 K at 2.13 h, 339.1 K at 2.81 h, 336.6 K at 3.21 h and 333.6 K at 5.3 h: it rises
over the dosing and falls once the dose stops.
No vent: R101 is closed while it reacts and QUAT forms no gas (the salt is its only product), so
core 1.9.0 gives no gas release at the MTSR and `hazard.vent_capacity` has nothing to compare
(`cheme.reactor-hazard-vent` applies to a vented batch only); none is stated (D-015).
MTT: R-101 is closed and padded with nitrogen, so the boiling points do not bound the
temperature; the pressure does. The MTT (SRC-7, closed system) is the temperature at which the
vessel reaches its relief's set pressure, 700 kPa(a) for a 6 bar g glass-lined vessel
(ASSUMED), at the worst composition: the end of the dosing, 0.463 kmol of methyl bromide
unreacted (x 0.0133 in the liquid), by Raoult's law with the vapour pressures of
`process/materials.yaml`, plus the nitrogen pad: 230 kPa(a) at 333 K on the headspace before the
dose (1.78 m3 of the 6.3 m3), compressed to 255.8 kPa(a) by the dose's volume (1.60 m3 left), and
further as the liquid expands on heating. The toluene, 3.79 of the 4.70 m3 of liquid at 333 K,
is taken at its liquid density of thermo 0.11 (SRC-6; 830 kg/m3 at 333 K, 746 kg/m3 at 415 K, a
quadratic fit within 0.09 % over 290-440 K, in the test), the other components at their
`liquid_molar_volume`; the headspace falls to 1.17 m3 at the MTT, so the nitrogen's pressure is
the pad x (1.60 / V_gas(T)) x (T / 333.15). Result: 415.29 K (`hazard.mtt`, by hand; a test
recomputes it). Without the expansion it would be 430.99 K, 16 K too high. The pressure at T_p
is 282 kPa(a). Every MTT of this section lies inside the fitted ranges of the two vapour
pressures (toluene 300-420 K, methyl bromide 270-420 K): no extrapolation. Core gives no MTT for
a closed, padded vessel (L-4). Core 1.9.0's default (ADR 0058), which `hazard.mtt` overrides,
is 307.3 K: core's Clausius-Clapeyron estimate of pure methyl bromide's boiling point at R101's
230 kPa(a), from its normal boiling point with the `heat_of_vaporization` of
`process/materials.yaml`, which is taken at the still's 384 K (a scratch copy without
`hazard.mtt`, 2026-11-06). It is not the physical boiling point: the entry's own vapour pressure
(the Antoine set fitted over 270-420 K) gives 300.0 K at 230 kPa(a); a single latent heat taken
100 K above the range puts the estimate 7.3 K high. Both are below T_p. Core leaves
a dissolved gas out of the default only below 5 mol% of the charge and doses; methyl bromide is
7.8 % of them (3.15 of 40.3 kmol), so it counts, and core reads it as the liquor at its boiling
point, below T_p (with a `cheme.reactor-hazard-mtsr` warning, MTSR above the MTT). That does not
describe this vessel: closed and padded, its liquor does not boil, the pressure bounds the
temperature, and methyl bromide is 1.3 mol% of the liquid at the worst moment. The hand MTT stays
the basis (D-015).
No TD24 is known for the reaction mass, the salt or the still residue (never estimated): no
criticality class (`cheme.reactor-hazard-missing`, info). With MTSR below MTT, core's
criticality() gives class 1 (TD24 above the MTT), 2 (TD24 between MTSR and MTT, or at the MTT)
or 5 (TD24 below the MTSR); the TD24 decides which.
Sensitivity (a scratch copy with the rate constant of QUAT divided by 10 and by 100; nothing else
changed, the same batch and recycle; not committed; rerun on core 1.9.0 on 2026-11-06 with the
same accumulation, MTSR and cycle, the MTSR over the batch peaking at the end of the dosing:
k/10 351.7 K at 2.71 h, back to 342.7 K at 4.59 h; k/100 371.9 K at 3 h, 340.0 K at 41.6 h):

| case | accumulation (end of dosing) | MTSR (worst moment) | MTT of the closed vessel | post-reaction | cycle, batches/a |
|---|---|---|---|---|---|
| k (design) | 14.7 % | 339.1 K (10132 s) | 415.29 K | 2.30 h | 10.20 h, 776.6 (F-101) |
| k/10 | 42.0 % | 351.7 K (9769 s) | 409.12 K | 27.4 h | 34.79 h, 227.7 (R-101) |
| k/100 | 85.0 % | 371.9 K (10800 s) | 401.33 K | 284.9 h | 292.2 h, 27.1 (R-101) |

The MTT of each case is its own (more methyl bromide unreacted, a lower MTT; by hand as above,
at the end of the dosing); the scratch runs kept the design's `hazard.mtt`, against which core
reports the same MTSR. MTSR stays below MTT in every case, so core's criticality() gives class
1, 2 or 5 in each, depending on the TD24. The largest possible rise (all the batch's PPh3
unreacted, dT_ad 46 K) would reach 379 K, below that case's own MTT: with all the methyl bromide
and all the PPh3 unreacted in the closed vessel (x 0.078 methyl bromide) the MTT is 399.04 K, by
the same method. The normal pressure at T_p rises from 282 kPa(a) (k) to 294 (k/10), 312
(k/100) and 318 kPa(a) (nothing reacted).
Interpretation: on this screening the quaternisation is thermally mild: its heat is modest (an
ASSUMED -100 kJ/mol in 4 kg of toluene per kg PPh3) and the closed vessel's MTT is high. The real
hazards are toxic and pressure ones: a slow reaction (k/10, k/100) accumulates methyl bromide
in a closed vessel, the dosing would have to be interlocked on the pressure and the conversion,
and the cycle becomes impractical before the batch becomes thermally critical. Calorimetry (heat
of reaction, heat-flow profile, accumulation, TD24 of the mass, the salt and the still residue)
and the solubility and vapour pressure of methyl bromide in the reaction mass decide this before
basic engineering. Screening values only, not a reaction-hazard assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-06)
Decision: `cheme assess lca --write` per kg of dried salt from the flowsheet's year averages; the
toluene make-up linked to btx-1 (a co-product of its reformate extraction, as
p-toluenesulfonyl-chloride-1 links it), the nitrogen consumable to asu-1's gaseous nitrogen
(`lca/mappings.yaml`), the LP steam counted as heat (kWh); every other background a gap with the
activity it should connect to. Cited proxies, recorded and not linked (CONTRIBUTING, "Gaps": a
correct gap rather than a doubtful link):
- methyl bromide: methylmagnesium-bromide-1's approach, the stoichiometric inputs from
  methanol-1 and hydrogen-bromide-1, 0.337 kg methanol and 0.852 kg HBr per kg (SRC-4, SRC-8);
  methyl bromide is a controlled ozone-depleting substance (SRC-5), used here as a feedstock and
  destroyed in the oxidiser, not emitted;
- PPh3: PCl3 + 3 C6H5Cl + 6 Na -> PPh3 + 6 NaCl, 0.524 kg PCl3, 1.287 kg chlorobenzene and 0.526 kg
  sodium per kg (my arithmetic; the route is a lead, SRC-9, not read); PCl3 is internal to
  phosphorus-oxychloride-1 and the library makes neither chlorobenzene nor sodium.
Per batch, not in the flowsheet (core ADR 0053, library ADR 0035): nitrogen 103 kg (about 82 Nm3:
R-101's purge, pad and sweep, F-101's pressing and vacuum break, blanketing; ASSUMED), 0.097 kg
per kg, leaving with the vent gas to the oxidiser (its disposal a gap). No rinses: the train is
kept dry.
Per kg of salt: PPh3 0.744 kg, methyl bromide 0.281 kg, toluene 0.056 kg, nitrogen 0.097 kg,
electricity 0.154 kWh (0.150 until core 1.10.0, D-016), LP steam 0.767 kWh, cooling water 0.703 kWh removed, brine 0.042 kWh
removed; vent gas to the oxidiser 0.022 kg (0.015 kg methyl bromide), still residue to
incineration 0.060 kg. Not counted (emission_exclusions): the tanks' breathing, the methyl
bromide store's losses, salt dust in the vacuum exhaust.

## D-013 Dedicated train (2026-11-06)
Decision: R-101, F-101, E-201, C-101 and the tanks T-201 and T-202 make only this salt, batch
after batch: 776.6 batches in 7920 h on a dedicated train (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train
cannot be checked without the other products' campaigns.
Out of scope, so not LCI gaps: the changeover cleaning between campaigns of other products, the
idle time of a multipurpose train, shared tank farms. Phosphonium salts are usually made on
multipurpose fine-chemical plants: there the burden per kg differs.

## D-014 Process safety notes (2026-11-06)
- Methyl bromide is the dominant hazard: acutely toxic by inhalation with delayed effects (IDLH
  250 ppm, TLV-TWA 1 ppm, SRC-5) and ozone-depleting. It is handled closed: a pressurised store
  with a vapour return, a dosing pump into the closed R-101, the excess swept to the thermal
  oxidiser (D-007), and every vent (R-101, F-101, the vacuum pump, T-201, T-202, the relief) to
  the oxidiser, never to atmosphere.
- Loss of the thermal oxidiser (or its scrubber): R-101 stays closed (it holds its methyl
  bromide at 282 kPa(a)); the dosing, the sweep, the transfer to F-101 and the drying stop until
  it is back (an interlock on the oxidiser's running signal); the still keeps running only to its
  condenser. The relief of R-101 discharges to a catch pot and the oxidiser; its scenario is a
  basic-engineering item.
- Water ingress (a leaking jacket, wet toluene, a wet PPh3): methyl bromide hydrolyses slowly to
  methanol and HBr, which corrodes and is not in the balance; the salt is hygroscopic and the
  product wet. The jacket is on water, so a jacket leak is the credible cause: a moisture check
  of the charge and the recovered toluene, and a pressure test of the jacket, are proposed.
  Water also raises the methyl bromide's solubility loss to the vent; not quantified.
- Air ingress oxidises PPh3 to its oxide (not modelled) and can make a flammable toluene
  atmosphere: the train is inerted with nitrogen (D-012).
- A slow or stalled reaction accumulates methyl bromide (D-011): the dosing is interlocked on
  R-101's pressure (alarm 400, stop 500 kPa(a), ASSUMED), its temperature and the agitator.
These are proposals for the HAZOP, not accepted safeguards.

## D-015 Core 1.9.0: tears, duties from the models, the MTT and the vent (2026-11-06)
Decision, on the core pin's rise to 1.9.0 (314642c):
- **Recycle tear (ADR 0060).** The recovered toluene's recycle is torn at S11 (`tears:`), its
  flow the ASSUMED wash ratio held fixed, its composition converged by Wegstein's method; S3 is
  X101's remainder. This replaces the hand convergence of S3 and S11 (D-006, L-5 resolved); the
  fresh feeds stay ASSUMED at the charge ratios (no design specification in core).
- **Duties from the models (ADR 0059).** Under 1.9.0 the entry gave `cheme.process-duty`
  warning at CR101 (Q3 5.1858 kW typed against the model's 3.55153 kW) and info at ST101 (two
  heat streams, Q7 and Q8, so the model's duty was not written). Each was resolved, not
  silenced: R101 (`energy_port: q`, Q2), CR101 (`energy_port: q`, Q3) and ST101 (`energy_port:
  steam`, Q7) now carry their models' duties, `calculated`; the heat the models deliberately
  leave out is on its own ASSUMED stream with its hand arithmetic, both in the LCI: Q10 (R-101's
  metal cooled with the slurry, 1.634 kW) and Q9 (the still's charge and metal heated to the
  boil, 19.964 kW); core 1.10.0 put both into the models' duties Q3 and Q7 (D-016). The hand values were recomputed: Q3's difference is exactly the metal, Q7's
  the heat-up and the metal (D-010). R101's typed Q2 already agreed with its model and is now
  the model's. Q1 (a heater, no model), Q4 (the dryer, compared by `cheme.process-dryer-duty`),
  Q5, Q6 and Q8 (condensers and coolers, which ADR 0059 leaves typed) stay ASSUMED.
- **MTT (ADR 0058).** The default at R101's 230 kPa(a) is 307.3 K, core's Clausius-Clapeyron
  estimate of pure methyl bromide's boiling point with the 384 K heat of vaporization of
  `process/materials.yaml` (the entry's vapour pressure gives 300.0 K): methyl bromide boiling
  below T_p either way, which a closed, padded vessel does not do; `hazard.mtt` stays the hand MTT of the
  closed vessel, 415.29 K (D-011, L-4 still open).
- **No vent capacity.** R101 has no vent (closed while it reacts, D-005) and forms no gas, so
  there is no gas release at the MTSR, nor over the batch or in the k/10 and k/100 cases, to
  compare with `hazard.vent_capacity`; none is stated. R-101's relief (700 kPa(a), D-011) and its
  scenario stay a basic-engineering item (D-014).
- `plant.yaml` requires `cheme-as-code>=1.9`: 1.8.0 refuses `tears` and `energy_port`.
Reason: core 1.9.0 makes the recycle and the models' duties calculated, so they go stale when an
input changes, instead of being converged and copied by hand.

## D-016 Core 1.10.0: the still's heat-up, the vessels' metal and C-101 sized (2026-11-06)
Decision, on the core pin's rise to 1.10.0 (c55e9c7), each feature adopted only where it models
the step at least as credibly as the hand value it replaces, checked against it:
- **The still's heat-up (ADR 0063).** ST101 takes `heat_up: true` (Raoult): its duty Q7 holds the
  charge S17 heated from 308.47 K to its 383.50 K bubble point, 14.6525 kW (149.43 kWh a batch,
  the hand 52747 kJ/h of Q9 to the kJ/h).
- **The vessels' metal (ADR 0063).** `metal_heat_capacity` on the recipe's vessels: R-101 3000
  kJ/K and C-101 2500 kJ/K, the ASSUMED masses of D-010, given once. Core puts C-101's metal into
  Q7 from the charge's 308.47 K to the still's end 386.48 K, 5.31179 kW (the hand 19123 kJ/h of
  Q9), and R-101's into CR101's Q3 over the cool-down from 333.15 to 313.15 K, 1.63427 kW (the
  hand Q10, 1.6342 kW). Q7 is 60.6328 kW (40.6685 + 14.6525 + 5.3118), Q3 5.1858 kW (3.55153 +
  1.63427): the same as the hand sums, 60.6324 and 5.1857 kW, to their rounding. **The hand
  streams Q9 and Q10 are removed**, with the ports `ST101.steam_heatup`, `CR101.q_vessel`, the
  block ports `RECOV.steam2`, `REACT.cw3` and the utility ports `LPS.st101_heatup`,
  `CW.cr101_vessel`. LP steam and cooling water per kg are unchanged to five digits.
- **The recipe's heating and cooling with the metal (ADR 0063, L-7).** R-101's jacket times use
  `C + C_m`: heat 292.81 -> 333.15 K 0.789 h (0.535 h before), cool to 313.15 K 0.807 h (0.552
  h), the 0.25 h each that ADR 0063 states; R-101 is occupied 10.15 h of the 10.198 h cycle
  (99.5 %, 94.5 % before); F-101 stays the bottleneck, the cycle, the batches, every flow and
  the LCI's material exchanges unchanged. **Difference recorded, hand value kept:** the recipe's
  heat report for R-101's heat-up is 375.4 MJ a batch (10.224 kW), the content's 254.3 MJ and
  the metal's 121.0 MJ from the charge's 292.81 K; core starts the metal at the content's
  temperature (ADR 0063's limitation: a vessel left warm by the previous batch is not modelled),
  while R-101 is left at 313.15 K by its cool-down and is purged and charged within 1.75 h. The
  hand Q1 (metal from 313.15 K, 60.0 MJ, 8.5622 kW) is the better energy and stays; the 1.662 kW
  difference is exactly the metal's 20.34 K start. For the same reason the heating time is
  conservative: with the metal's heat only (about 0.66 h, my arithmetic: the metal's 3000 kJ/K
  weighted by 20/40.34 K) R-101 would be occupied about 10.0 h. Q1 stays on its hand stream: E101
  is a pass-through heater with no model; `batch.heat_up` on R101 would add nothing (its charge
  S5 enters at 333.15 K from E101) and the PPh3's dissolution heat is a charged solid's, which
  core 1.10.0 does not cover (L-8).
- **The still's heat-up time (a finding, recorded).** Core 1.10.0 puts the heat-up into ST101's
  duty but not into the recipe's `distil` time from ST101, which stays the boil-up's 1.659 h at
  250 kW. Heating 4210 kg and C-101's metal by 75 K at that rate takes 0.81 h (201.54 kWh, the
  charge's 149.43 and the metal's 52.11 kWh to the bubble point), so the RECOVER procedure gets a
  `heat` operation of 0.81 h, ASSUMED by that arithmetic (C-101 has no jacket model in core);
  C-101 is occupied 3.47 h (34 %, 26 % before), one batch takes 22.31 h (20.99 h before). L-9.
- **C-101 sized by the recipe (L-1 resolved).** The RECOVER unit procedure gives a `vessel`
  (fill 0.8, H/D 1.2, ASSUMED as R-101): 4.852 m3 of liquor a batch in 6.3 m3 (77 %, D 1.88 m),
  the R10 size the hand estimate had. No jacket check on a still's vessel.
- **Electricity** follows the occupancies: P1 5.4 -> 5.7 kW (R-101's agitator at 99.5 %), P3 2.8
  -> 3.0 kW (C-101's at 34 %), 15.5 -> 16.0 kW, 0.150 -> 0.154 kWh per kg (D-010).
- **Checked, not adopted:**
  - the batch rectification (`still.column`, ADR 0061): the distillate is to carry the excess
    methyl bromide back with the toluene (D-009), and PPh3 and the salt do not distil, so one
    stage is the credible model; a column would only raise the boil-up by `(R + 1)`. Nor a
    `purity` end: the recovery cut's end is its distilled share;
  - `still.condenser_port` (ADR 0061): it writes the condenser's latent heat only, 40.669 kW,
    while Q8 also holds the distillate cooled to 303 K (15.758 kW, no step of its own); adopting
    it would replace one hand stream by another. Q8's latent part equals Q7's boil-up term (the
    test checks it);
  - the vent's vapour, condenser and Henry split (`batch.vent.vapour`, `condenser`, `henry`,
    ADR 0062): R101 is closed while it reacts and has no vent (D-005); the excess methyl bromide
    leaves after the reaction (DG101), which is the degassing of a dissolved dose that core
    1.10.0 leaves open (core#179 item 2, naming this entry's L-3); E201 condenses a dryer's
    vapour, not a batch's vent. L-3 stays open;
  - a dose's `heat_of_solution` (ADR 0063) for the liquid methyl bromide in toluene: no value is
    known; the recorded exclusion (at most 1 kJ/mol ASSUMED, 0.08 kW, D-010) is a bound, not a
    heat to put into the model and the screening's dT_ad. The PPh3's heat of solution is a
    charged solid's, not covered (L-8);
  - `batch.heat_up` on R101 (no heat-up in that step, above).
- The thermal screening is unchanged (dT_ad 46.0 K, accumulation 14.7 %, MTSR 339.1 K, the hand
  MTT 415.29 K; `cheme process reactor-hazards` exits 0); R101's duty basis now says the
  vessel's metal is left out of it (no `heat_up`: E101 and Q1 hold the heat-up).
- `plant.yaml` requires `cheme-as-code>=1.10`: 1.9.0 refuses `heat_up`, `metal_heat_capacity`
  and a vessel on the still's unit procedure.
Reason: core 1.10.0 computes the heat-up and the metal from the models' own temperatures, so they
go stale with the duties when an input changes, instead of two hand streams to recompute.

## Core features used (core 1.9.0)

| feature | where | ADR |
|---|---|---|
| `reactor: semibatch` with a liquid dose and a `target` | R101 (liquid methyl bromide into the PPh3 solution) | 0050 |
| `hazard.mtt` and the screening of a semi-batch | R101, D-011 | 0050 |
| `crystallizer.spectators` with `measured_in: pure_solvent` and `salting_out`; an `energy:` block | CR101 (with its cool-down), W101 | 0056 |
| several crystallizer inlets (a reslurry wash) | W101 | 0056 |
| `solid_separation.filtration` and recipe `filter` `from:` | F101, F102 | 0057 |
| `dryer:` with energy, drying rate, cake density; recipe `dry` `from:`; `vessel.heated_area` | D101 | 0057 |
| recipe `units:` (one vessel over several steps) | R-101 (M101, E101, R101, CR101, DG101), F-101 (F101, W101, F102, D101), C-101 (ST101, X101) | 0057 |
| `still:` on Raoult's law with a `distilled` end, recipe `distil` `from:` | ST101 (toluene recovery) | 0055 |
| vessel sizing and jacket check, `heat`/`cool` times from the jacket | R-101, F-101 | 0052 |
| per-batch LCA consumables with a disposal | nitrogen | 0053 |
| `tears: [{stream, initial}]`, `convergence:` (1.9.0) | S11, the recovered toluene's recycle, its flow held as the wash ratio (D-006, D-015) | 0060 |
| the models' duties at `energy_port:` (1.9.0) | Q2 (R101 semi-batch), Q3 (CR101 crystallizer), Q7 (ST101 still), `calculated` (D-010, D-015) | 0059 |
| the MTSR over the batch (`mtsr_profile`); the default MTT at the vessel's pressure checked (1.9.0) | R101 (D-011, D-015) | 0058 |

Core 1.10.0 (D-016):

| feature | where | ADR |
|---|---|---|
| `still.heat_up: true`: the charge heated to its bubble point in the still's duty | ST101, Q7 (14.6525 kW of 60.6328) | 0063 |
| `vessel.metal_heat_capacity` on a recipe vessel: in the models' duties | REACT (R-101, 3000 kJ/K: CR101's Q3, 1.63427 kW), RECOVER (C-101, 2500 kJ/K: ST101's Q7, 5.31179 kW) | 0063 |
| the recipe's `heat` and `cool` times with the metal (`C + C_m`) and their heat report (`heats`) | R-101's heat-up 0.789 h and cool-down 0.807 h; the heat report checked against Q1 and Q3 | 0063 |
| a `vessel` on a unit procedure holding a still, sized from what it takes in | C-101, 6.3 m3 (L-1) | 0063 |

Checked in 1.10.0 and not used (D-016): `still.column`, `purity` and `still.condenser_port`
(ADR 0061: one stage is the credible recovery, Q8 holds the distillate's cooling too);
`batch.vent.vapour`, `condenser` and `henry` (ADR 0062: R101 has no vent, the degassing of the
dissolved excess stays open); `dosing.heat_of_solution` and `batch.heat_up` (ADR 0063: no value
for the dosed methyl bromide's mixing heat, no heat-up in R101).

Not used: `batch.vent` and `dosing.absorbed` (ADR 0054): no gas leaves R101 while it reacts (the
vessel is closed) and the methyl bromide is dosed as a liquid (D-001); the excess leaves after
the reaction, which a vent on the reacting step cannot express (L-3). Hence also not
`hazard.vent_capacity` (no gas release to compare, D-015), nor `hazard.reactions` (one
reaction); the default MTT is overridden by `hazard.mtt` (D-011).

## Core limits hit (for core issues)

Status on core 1.10.0 (2026-11-06): L-1 and L-5 are resolved, L-7 and L-8 partly; L-2 to L-4
and L-6 remain; L-9 is new.

- L-1 (resolved in core 1.10.0, ADR 0063): a batch still was not sized as a vessel: a recipe
  unit holding only a still had "no batch content to size" (`cheme.recipe-reference` when a
  vessel was given), so C-101's volume was a hand estimate. Core 1.10.0 sizes a still's
  unit procedure's vessel from what its steps take in: C-101 6.3 m3 (D-003, D-016).
- L-2: the semi-batch is liquid only, so the salt that precipitates as it forms is carried
  dissolved in R101 (with an ASSUMED liquid molar volume and heat capacity) and crystallised
  afterwards by CR101. The concentrations, the volume and the heat capacity during the dosing
  are those of a solution, not of a slurry, and the heat of crystallisation is lumped into the
  reaction's.
- L-3: no degassing, headspace or vapour-liquid equilibrium in a batch: the vent takes only what
  a reaction forms (core ADR 0054), so the excess methyl bromide, which is dosed, cannot leave
  by `batch.vent`; its removal after the reaction (DG101) and the vacuum condenser's
  non-condensables (E201) are hand splits with an ASSUMED stripping share. The toluene the
  nitrogen carries is hand arithmetic. A degassing or flash step (a share of each volatile, or a
  VLE at the vessel's pressure) would make both calculated. Still open on core 1.10.0: its vent
  vapour (ADR 0062) saturates a vent gas a reaction forms, and the degassing of a dissolved dose
  is left open (core#179 item 2, naming this limit); R101 forms no gas and has no vent (D-016).
- L-4: no MTT for a closed vessel. Up to 1.8.0 core asked for `hazard.mtt` above atmospheric
  pressure; core 1.9.0 (ADR 0058) gives a default there, the boiling point of what boils at the
  vessel's pressure by Clausius-Clapeyron, here 307.3 K for methyl bromide at 230 kPa(a) with its
  heat of vaporization at the still's 384 K (its vapour pressure gives 300.0 K), below T_p: a
  pure component's boiling point, from one latent heat, still not a closed vessel (still open). The
  MTT of a closed, padded vessel (the temperature at the relief's set pressure from the
  vapour pressures and the pad, the pad compressed by the liquid's thermal expansion, which
  alone lowers it by 16 K here) is hand arithmetic (D-011), and it differs per sensitivity case;
  the screening also reports no pressure at the worst moment (ADR 0058 names the blocked-vent
  pressure, with no head space or relief model, a known limitation).
- L-5 (resolved in core 1.9.0, ADR 0060): propagate did not converge recycles: the recovered
  toluene (S3, S11) was a tear stream converged by hand with the fresh feeds that follow the
  charge ratios (D-006), as in sodium-azide-1. It is now the flowsheet's tear S11, converged by
  propagate; the fresh feeds that follow the charge ratios stay ASSUMED (no design specification
  on a feed, core#181 part 2, L-6).
- L-6 (as NBS L-6): core propagates from the feeds and does not solve them for a product rate,
  and the per-batch charges over the cycle set the hourly feeds; batch size and cycle were
  iterated by hand to a fixed point.
- L-7 (partly resolved in core 1.9.0, ADR 0059; further in core 1.10.0, ADR 0063): the heat-up
  and the vessel's metal were outside the still's, the crystallizer's and the jacket's models.
  Since 1.9.0 the models write their own part (Q2, Q3, Q7); since 1.10.0 the still's charge
  heat-up and C-101's metal are in Q7, R-101's metal cooled with the slurry in Q3 (the hand
  streams Q9 and Q10 went), and the recipe's heating and cooling times count R-101's steel
  (resolved for these, D-016). Still hand arithmetic: Q1 (R-101's heat-up with its metal: E101
  is a pass-through, and core starts the metal at the content's temperature, not at the
  313.15 K the previous batch left it at, so its heat report is 1.662 kW high and its heating
  time conservative) and Q6 (F-101's product and metal cooled; no model in that step).
- L-8 (partly resolved in core 1.10.0, ADR 0063): no heat of solution or mixing. Core 1.10.0
  takes a dose's `heat_of_solution`, so the dosed liquid methyl bromide's mixing heat could be
  counted, but no value is known (the exclusion of D-010 is a bound). The PPh3's dissolution in
  M101 (60 MJ a batch), a charged solid's, is not covered (ADR 0063) and stays in S4's
  temperature by hand.
- L-9 (new on core 1.10.0): the still's `heat_up` enters its duty but not the recipe's `distil`
  time from the still, which stays the boil-up's at the boil-up rate; the heat-up time at the
  same 250 kW (0.81 h) is a hand `heat` operation on C-101 (D-016). Core could add the heat-up
  energy over the boil-up rate to the distil time, or give the still's vessel a jacket time.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R101: composition, accumulation, MTSR, peak cooling | done in cheme, kinetics ASSUMED | D-005, D-011, `cheme process reactors`, `reactor-hazards` |
| MTT of the closed vessel | hand (Raoult and the pad); core 1.9.0's default (307.3 K) checked, not used | D-011, D-015, L-4 |
| batch recipe, cycle time, basis check, vessels, jackets | done in cheme | D-003, `cheme process recipe` |
| precipitation and wash losses | done in cheme: crystallizers with spectators, solubility ASSUMED | D-007, D-008, core ADR 0056 |
| filtration | specified split in cheme; time by Ruth, cake data ASSUMED | D-008, core ADR 0057 |
| drying: outlets, duty Q4, drying time | done in cheme, moisture and rate ASSUMED | D-008, core ADR 0057 |
| toluene recovery: cuts, residue, boil-up time and energy, the charge's heat-up and C-101's metal | done in cheme (Rayleigh, Raoult; `heat_up` and the metal, core 1.10.0); the heat-up time hand arithmetic | D-009, D-016, core ADRs 0055, 0063, L-9 |
| vent losses DG101, vacuum condenser E201 | hand splits, shares ASSUMED | D-007, D-008, L-3 |
| recycle | done in cheme (tear S11, Wegstein); the fresh feeds' charge ratios and the cycle ASSUMED at the fixed point | D-006, D-015, L-6 |
| duties Q2, Q3, Q7 | done in cheme (the models at `energy_port`, core 1.9.0; with the vessels' metal and the still's heat-up, core 1.10.0) | D-010, D-015, D-016 |
| the other duties (Q1, Q5, Q6, Q8) | hand arithmetic in the sources, recomputed by the test | D-010 |
| vessels R-101, F-101, C-101 and R-101's heat and cool times with its metal | done in cheme (recipe, core 1.10.0 for C-101 and the metal) | D-003, D-016 |
| per-batch exchange (nitrogen) | done in cheme, amount ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, PPh3 and methyl bromide unmapped | D-012 |

## Open inputs
Kinetics and heat of reaction (calorimetry), TD24 of the reaction mass, the salt and the still
residue; the solubility of the salt in toluene and the methyl bromide's vapour-liquid equilibrium
over the reaction mass; the stripping of the excess methyl bromide (D-007) and its recovery from
the vent; filtration, wash and drying data from trials; the product specification (assay, PPh3
and its oxide, water, toluene); PPh3's solubility and heat of solution in toluene; the relief
scenario of R-101; a TEA (`operation.batch: {recipe: true}`).
