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
  heat 292.81 -> 333.15 K 0.53 h (from the jacket on hot water at 353 K), dose 3.0 h and
  post-reaction 2.30 h to 0.99 conversion of the PPh3 (both from R101's model), cool to 313 K
  0.55 h (jacket), precipitation hold 0.5 h, vent and sweep 0.5 h, press the slurry to F-101
  0.5 h: 9.64 h;
- ISOLATE on F-101 over F101, W101, F102 and D101: receive 0.5 h, filtration 1.17 h and 0.46 h
  (Ruth, from the filters' data, on the vessel's bottom), reslurry wash 0.5 h, drying 6.57 h
  (D101's 315.3 kg of vapour a batch at 4 kg/(m2 h) on 12 m2), cool and discharge 1.0 h:
  10.20 h;
- RECOVER on C-101 over ST101 and X101: receive 0.5 h, boil-up 1.66 h (ST101's model at 250 kW),
  drain 0.5 h: 2.66 h.
F-101 is the bottleneck: cycle 10.198 h, 776.6 batches in 7920 h; R-101 is 95 % occupied; one
batch takes 20.99 h from the purge to the still's drain. The flowsheet's flows are the recipe's
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
- C-101 is not sized by core (a still has no batch content to size, L-1); about 6.3 m3 for the
  4.21 t of liquor a batch, ASSUMED.
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
Decision: every unit but two is calculated by `cheme process propagate` (core 1.8.0): the
semi-batch R101, the crystallizers CR101 and W101, the filters F101 and F102, the dryer D101,
the still ST101, the mixers M101, M201, M202 and the pass-through E101. The hand splits are
DG101 (the vent losses, D-007) and E201 (the vacuum condenser, D-008): core has neither a
degassing nor a condenser with non-condensables. No balance script.
The recovered toluene to the charge (S3) and to the wash (S11) are assumed tear streams:
propagate does not converge recycles. With them, the fresh PPh3, toluene and methyl bromide
(S1, S2, S6) follow the per-batch charges of D-004 and the hand splits follow their rules; all
were converged by successive substitution over `cheme process propagate --fill` (a scratch
driver outside the folder, as sodium-azide-1 did) until the change was below 2e-7 relative, and
then the cycle, which sets the hourly flows of the per-batch charges, to a fixed point. X101,
DG101 and E201 then balance within the flowsheet's tolerance (abs 0.02 kg/h, rel 0.001), which
`cheme validate` checks; a change to an upstream value unbalances them, so the loop must be
re-converged (L-5).

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
sets end below that (toluene at 384.66 K).
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
Decision (year averages, hand arithmetic from cheme's reports, given in the flowsheet's
sources; `tests/test_methyltriphenylphosphonium_bromide_1.py` recomputes them):
- LP steam 350 kPa(a), as heat delivered:
  - Q1 8.562 kW: the charge S4 heated from 292.81 to 333.15 K (618.7 kJ/(K h)), and R-101's metal
    (3000 kJ/K, about 6 t of glass-lined steel, ASSUMED) from 313.15 to 333.15 K each batch.
    S4's temperature is the adiabatic mix of S1, S2 and S3 less the PPh3's heat of solution,
    20 MJ/kmol ASSUMED (its heat of fusion by Walden's rule, about 56 J/(mol K) at its 353 K
    melting point; no measured value found), 60 MJ per batch (5.9 MJ/h), so Q1 counts the
    dissolution;
  - Q4 10.347 kW: the dryer (core's model, D-008);
  - Q7 60.628 kW: the still: the boil-up, 414.7 kWh a batch (`cheme process stills`), plus what
    core's still leaves out: the charge S17 heated from 308.47 K to its 383.5 K bubble point, and
    C-101's metal (2500 kJ/K, about 5 t, ASSUMED) from 308.47 to 386.48 K each batch.
  R-101 and F-101 are heated with hot water at 353 K from LP steam, C-101 with the steam at
  412 K: below every temperature limit the design states (R-101's MTT 415.29 K, D-011; the
  salt's melting point, about 503 K). The steam is only 3 K below R-101's MTT, so it must never
  reach R-101's jacket directly: R-101 sees only the 353 K hot-water circuit. No decomposition
  temperature of the salt, PPh3 or the still residue is known (open input, D-011).
- cooling water 298/308 K:
  - Q2 7.878 kW: the heat of quaternisation (0.29123 kmol/h x 100 MJ/kmol) less the dose warmed
    from 298 to 333 K;
  - Q3 5.186 kW: the slurry cooled from 333.15 to 313.15 K (CR101's energy block) and R-101's
    metal by 20 K;
  - Q6 3.359 kW: the product cooled from 333.15 to 313.15 K in F-101 and F-101's metal cooled
    back to the cake's 307.95 K each batch (as core's dryer model assumes);
  - Q8 56.426 kW: the still's condenser (the distillate at its components' heats of
    vaporisation) and the distillate cooled from the still's mean 384.99 K to 303.15 K.
- chilled brine 258/263 K: Q5 4.308 kW, F-101's vacuum condenser E-201: 30.90 kg/h of toluene
  condensed (391 kJ/kg), the condensate cooled from 333 to 268 K and the vent gas by 65 K. It is
  on brine: toluene's dew point at the filter-dryer's 5 kPa(a) is about 304 K (303.6 K by the
  Antoine set of `process/materials.yaml`), so cooling water at 298/308 K cannot condense it; at
  the 268 K outlet its vapour pressure is 0.65 kPa.
- electricity 15.5 kW: R-101's 5.5 kW agitator at 94 % occupancy and the dosing pump (5.4 kW),
  F-101's 7.5 kW agitator half the time and the 5.5 kW vacuum pump over the drying (7.3 kW),
  C-101's agitator and the transfer pumps (2.8 kW). All ASSUMED.
Per kg of salt: LP steam 0.767 kWh, cooling water 0.703 kWh, brine 0.042 kWh, electricity
0.150 kWh.
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
Result (`cheme process reactor-hazards`, core ADR 0050): R101 T_p 333.15 K, adiabatic rise of the
whole batch dT_ad 46.0 K; the largest accumulation of the dosed methyl bromide 14.7 % at the
end of the dosing; the MTSR at the worst moment (10132 s) 339.1 K.
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
a vessel above atmospheric pressure (it asks for `hazard.mtt`); at atmospheric pressure it would
take the
lowest boiling point of what stays in the liquid, methyl bromide's 276.55 K, below T_p (L-4).
No TD24 is known for the reaction mass, the salt or the still residue (never estimated): no
criticality class (`cheme.reactor-hazard-missing`, info). With MTSR below MTT, core's
criticality() gives class 1 (TD24 above the MTT), 2 (TD24 between MTSR and MTT, or at the MTT)
or 5 (TD24 below the MTSR); the TD24 decides which.
Sensitivity (a scratch copy with the rate constant of QUAT divided by 10 and by 100; nothing else
changed, the same batch and recycle; not committed):

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
electricity 0.150 kWh, LP steam 0.767 kWh, cooling water 0.703 kWh removed, brine 0.042 kWh
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

## Core features used (cheme-as-code 1.8.0)

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
Not used: `batch.vent` and `dosing.absorbed` (ADR 0054): no gas leaves R101 while it reacts (the
vessel is closed) and the methyl bromide is dosed as a liquid (D-001); the excess leaves after
the reaction, which a vent on the reacting step cannot express (L-3).

## Core limits hit (for core issues)

- L-1: a batch still is not sized as a vessel: a recipe unit holding only a still has "no batch
  content to size" (`cheme.recipe-reference` when a vessel is given), so C-101's volume is a
  hand estimate (D-003). A still's charge is a batch content; core could size its pot from it.
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
  VLE at the vessel's pressure) would make both calculated.
- L-4: no MTT for a closed vessel: above atmospheric pressure core asks for `hazard.mtt`, and at
  atmospheric pressure it would take methyl bromide's boiling point (276.55 K, below T_p). The
  MTT of a closed, padded vessel (the temperature at the relief's set pressure from the
  vapour pressures and the pad, the pad compressed by the liquid's thermal expansion, which
  alone lowers it by 16 K here) is hand arithmetic (D-011), and it differs per sensitivity case;
  the screening also reports no pressure at the worst moment.
- L-5: propagate does not converge recycles: the recovered toluene (S3, S11) is a tear stream
  converged by hand with the fresh feeds that follow the charge ratios (D-006), as in
  sodium-azide-1.
- L-6 (as NBS L-6): core propagates from the feeds and does not solve them for a product rate,
  and the per-batch charges over the cycle set the hourly feeds; batch size and cycle were
  iterated by hand to a fixed point.
- L-7: the heat-up and the vessel's metal are outside the still's and the jacket's models: the
  still's duty is the boil-up alone (no heat-up of the charge, no sensible heat of the pot), and
  the recipe's heating and cooling times count the content but not the vessel's steel; Q1, Q3,
  Q6 and Q7 add them by hand, and the times are short by that share.
- L-8: no heat of solution or mixing: the PPh3's dissolution in M101 (60 MJ a batch) is put
  into S4's temperature by hand, and a dosed liquid's mixing heat is not counted
  (p-toluenesulfonyl-chloride-1's L-2).

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R101: composition, accumulation, MTSR, peak cooling | done in cheme, kinetics ASSUMED | D-005, D-011, `cheme process reactors`, `reactor-hazards` |
| MTT of the closed vessel | hand (Raoult and the pad) | D-011, L-4 |
| batch recipe, cycle time, basis check, vessels, jackets | done in cheme | D-003, `cheme process recipe` |
| precipitation and wash losses | done in cheme: crystallizers with spectators, solubility ASSUMED | D-007, D-008, core ADR 0056 |
| filtration | specified split in cheme; time by Ruth, cake data ASSUMED | D-008, core ADR 0057 |
| drying: outlets, duty Q4, drying time | done in cheme, moisture and rate ASSUMED | D-008, core ADR 0057 |
| toluene recovery: cuts, residue, boil-up time and energy | done in cheme (Rayleigh, Raoult) | D-009, core ADR 0055 |
| vent losses DG101, vacuum condenser E201 | hand splits, shares ASSUMED | D-007, D-008, L-3 |
| recycle tears and the cycle | hand (successive substitution over propagate) | D-006, L-5, L-6 |
| the other duties | hand arithmetic in the sources, recomputed by the test | D-010 |
| per-batch exchange (nitrogen) | done in cheme, amount ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, PPh3 and methyl bromide unmapped | D-012 |

## Open inputs
Kinetics and heat of reaction (calorimetry), TD24 of the reaction mass, the salt and the still
residue; the solubility of the salt in toluene and the methyl bromide's vapour-liquid equilibrium
over the reaction mass; the stripping of the excess methyl bromide (D-007) and its recovery from
the vent; filtration, wash and drying data from trials; the product specification (assay, PPh3
and its oxide, water, toluene); PPh3's solubility and heat of solution in toluene; the relief
scenario of R-101; a TEA (`operation.batch: {recipe: true}`).
