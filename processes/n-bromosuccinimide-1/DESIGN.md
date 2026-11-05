# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
N-Bromosuccinimide (NBS) by the caustic bromination of succinimide, issue
ChemE-as-Code/process-library#140, the batch pilot of ChemE-as-Code/core#158. Concept stage:
design basis, batch recipe, balanced BFD/PFD, thermal screening and a preliminary gate-to-gate
LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-05): library `main` at 256f1dc9; cheme-as-code 1.7.0 (core#158:
`reactor: semibatch`, `process/recipe.yaml` with batch vessels, per-batch LCA consumables; core
ADRs 0050 to 0053). Work-up re-expressed (D-014, 2026-11-05) on core main 7334d7c, released as
1.8.0 (core#165: the crystallizer with spectators, the dryer and recipe units over several
steps; core ADRs 0056, 0057).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine text; no paragraph numbers, so the locator is the part
of the document).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US2971960A, T. D. and R. C. Waugh, 1961: Production of N-brominated imides and hydantoins, https://patents.google.com/patent/US2971960A/en | background (column 1): N-brominated imides were made by treating the imide in water with bromine and a strong base (or a separately made hypobromite); NaOH takes up the HBr; only half of the bromine enters the product, the other half becomes alkali bromide; the product is contaminated with bromide unless much water dissolves it away, which lowers the yield. Examples 1-4 (its own acid route with chlorine or hypochlorite, not used): the slurry is cooled to 5-10 C, filtered, washed with ice water and dried at 60 C; yields 66-76 % of theory | read; patent, facts only | D-001, D-007, D-008 |
| SRC-2 | PubChem CID 67184, N-Bromosuccinimide, https://pubchem.ncbi.nlm.nih.gov/compound/67184 | identity (C4H4BrNO2, InChIKey PCLIMKBDDGJMGD-UHFFFAOYSA-N, CAS 128-08-5); section Solubility (HSDB record): 1.47 g per 100 g water at 25 C | read (PUG REST and PUG View) | D-005, chemicals registry |
| SRC-3 | PubChem CID 11439, Succinimide | identity (C4H5NO2, InChIKey KZNICNPSHKQLFF-UHFFFAOYSA-N, CAS 123-56-8) | read | chemicals registry |
| SRC-4 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | the accumulation and MTSR of a semi-batch (method, implemented in core ADR 0050) | method reference, no data taken | D-011 |
| SRC-5 | processes/bromine-1 and processes/chlor-alkali-1 (this library) | dry bromine 99.96 wt%; caustic soda 50 wt% | library, internal | feed links (D-004, D-012) |
| SRC-6 | Ullmann's Encyclopedia of Industrial Chemistry, Bromine Compounds, doi:10.1002/14356007.a04_405 | - | not read (licensed); named by the issue's literature note | route reference lead only |

Searched and not found openly (2026-11-05): an industrial NBS production description with
capacity, kinetics or calorimetry of the caustic bromination, a heat of reaction, the
solubility of NBS at 0-10 C or in NaBr brine, and a market volume. A laboratory procedure of
the caustic route with a 75-81 % yield exists only on a hobbyist archive page without
attribution; it is not used.

## D-001 Route and boundary (2026-11-05)
Decision: the caustic route (SRC-1, background): succinimide dissolved in aqueous NaOH, bromine
added to the cold solution, C4H5NO2 + NaOH + Br2 -> C4H4BrNO2 + NaBr + H2O; NBS precipitates and
is filtered, washed with ice water and dried, on a dedicated train (D-013). Boundary feeds: succinimide, bromine, caustic
soda 50 wt%, process water, electricity, LP steam; returns: chilled brine; outputs: dried NBS,
one wastewater stream (mother liquor, wash filtrate, dryer condensate).
Reason: it is the route the issue names and the one SRC-1 describes as the usual one; it uses
the library's bromine (bromine-1) and caustic (chlor-alkali-1). It exercises a dosed exothermic
step, a precipitation, a filtration and a drying: the batch capabilities core#158 adds.
Rejected: bromine with chlorine or hypochlorite in acid solution (SRC-1's own invention: all of
the bromine enters the product, the chlorine leaves as NaCl): better bromine use, but a second
oxidant and a pH-controlled feed; a candidate variant (`n-bromosuccinimide-2`). Sodium bromide
with hypochlorite and acid (patented, not read): a variant as well.
Links: bromine-1, chlor-alkali-1. No library process makes succinimide (from succinic acid or
its anhydride and ammonia).

## D-002 Capacity, product and operating hours (2026-11-05)
Decision: 500 t/a dried NBS, 7920 h/a (330 days of 24 h), ASSUMED. Product: 99.0 wt% NBS (98.6
wt% crystals and the NBS of the dried cake liquor), 0.75 wt% NaBr, 0.2 wt% water (D-008).
Reason: no open market or plant figure was found; NBS is a fine-chemical reagent, so a
hundreds-of-tonnes batch plant is the plausible scale. The LCI is per kg and does not depend on
the scale; the batch size does (D-003).

## D-003 Batch basis and recipe (2026-11-05)
Decision: one batch makes 334.41 kg of dried NBS (stream S14); the recipe
(`process/recipe.yaml`) has three unit procedures: DISSOLVE on M-101 (charge, dissolve, cool,
transfer: 2.5 h), BROMINATE on R-101 (receive, dose 2 h and react 0.80 h to 0.999 conversion of
the bromine, both from R101's model, a 0.5 h precipitation hold, transfer, clean: 5.30 h) and
ISOLATE in three agitated filter-dryers F-101, one vessel over the steps F101, W101, F102 and
D101 (filter 1.94 h and refilter 0.83 h by Ruth from F101's and F102's filtration data, a
0.5 h reslurry, dry 7.99 h from D101's drying rate, cool and discharge, clean: 12.75 h, 4.25 h
each in turn; D-014). The brominator is the bottleneck: cycle time 5.30 h, 1495 batches in
7920 h; one batch takes 18.55 h from charging to discharge (14.3 h before D-014). The
flowsheet's flows are the year averages of the recipe: 334.41 kg x 1495.15 / 7920 h = 63.13
kg/h of S14; `cheme process recipe` checks this (no `cheme.recipe-basis` finding).
Reason: core ADR 0051 puts the batch basis in one place, so the balance, the LCI per kg and a
later TEA share it; the dosing and post-reaction times come from the reactor model, so a change
of the dosing changes the cycle, and since D-014 the filtration and drying times come from
F-101's models, so a change of the cake data or the drying rate does too. The durations of the
other operations are ASSUMED concept values; F-101 is installed three times so that it is not
the bottleneck (D-014).
Per batch: 1.35 m3 of slurry in R-101 at the end of the dosing; the recipe sizes R-101 from
R101's model (core ADR 0052, fill fraction 0.8 and H/D 1.2 ASSUMED): a 2 m3 vessel (the R10
preferred size), 68 % full, 1.29 m diameter. M-101 holds 1.26 m3 of charge (0.238 m3/h x
5.30 h).

## D-004 Feeds and charge (2026-11-05)
Decision: succinimide and NaOH 1.02 mol each per mol of bromine (the bromine limiting, so that
little free bromine is left), 30 mol of water per mol of bromine in the charge (the caustic's water
included), all ASSUMED. Bromine from bromine-1 (100 % Br2 in the model), caustic 50 wt% from
chlor-alkali-1, technical succinimide (100 % in the model).
Reason: one equivalent of base per bromine is the stoichiometry of the caustic route (SRC-1);
a small excess of imide and base keeps the bromine from accumulating as hypobromite. The
dilution keeps the NBS solids in a stirrable slurry (about 20 wt% solids) and the NaBr far below
its solubility.

## D-005 Brominator R-101: semi-batch model, kinetics and solubility (2026-11-05)
Decision: R101 is `reactor: semibatch` (core ADR 0050): the charge S4 at 278.15 K, the bromine
S5 (293.15 K) dosed at a constant rate over 2 h, then the post-reaction to 0.999 conversion of
the bromine (`batch.target`; 0.80 h from the model), isothermal at 278.15 K. Rate law of BROM:
first order in dissolved bromine and in the imide (anion), k c_SUCC,0 = 0.05 1/s at 278 K and
the charge's initial imide concentration (Ea 40 kJ/mol), ASSUMED. Heat: -80 kJ/mol overall,
ASSUMED; of it -30 kJ/mol, the imide's deprotonation by NaOH (a weak acid neutralised by a
strong base), is released in the dissolver M-101 (D-009), so BROM in R101 carries -50 kJ/mol.
The 0.1 % of the bromine left unreacted is carried through the work-up as a spectator of the
crystallizers and leaves with the dryer's vapour (D101's volatiles, D-014); in the alkaline
liquor it would rather be hypobromite, not modelled.
The NBS is carried dissolved in the reactor model (the liquid model has one phase) and
precipitates in the hold CR101, core's crystallizer in the same block (D-014; until then a
conversion "reaction" PPT): the liquor leaves saturated at 14.7 g NBS per kg of water, the 25 C
solubility (SRC-2) taken at 278 K as well; 95.4 % of the NBS formed crystallises.
Reason: no open kinetics or calorimetry of the caustic bromination exists (searched 2026-11-05):
the fast effective rate is an ASSUMED placeholder for reaction calorimetry. The law is second
order because the imide is a co-reactant at only a 2 % excess: in a semi-batch it runs down
as the bromine is dosed, so the rate slows towards the end of the dosing, which a first-order
law in bromine alone would miss. The heat of reaction is an ASSUMED order of magnitude (no open
calorimetric value). The 25 C solubility overstates what stays dissolved at 5 C: the loss in
D-007 is conservative.
**The low accumulation in D-011 is a consequence of the assumed rate law** and must be
confirmed by reaction calorimetry (heat flow during the dosing) before basic engineering.
Rejected at first: core 1.7.0's crystallizer, which refused any component besides its one
solute and solvent while the mother liquor holds NaBr, NaOH and succinimide (lesson L-2). Core
1.8.0's crystallizer takes them as spectators: used since D-014.

## D-006 Balance method and property gate (2026-11-05)
Decision (as revised by D-014): cheme propagates every stream: the mixers, the semi-batch R101,
the precipitation CR101 and the reslurry wash W101 as crystallizers with spectators (core ADR
0056), the filters F101 and F102 as specified `solid_separation`, and the dryer D101 to its
residual moisture (core ADR 0057); the dryer's heat Q3 is core's (`cheme process
crystallizers`). The independent script `scripts/balance.py` repeats the same algebra to size
the feeds (S1, S2, S3, S5, S10) for 500 t/a of product and gives the duties Q1 and Q2 and the
temperature of S16, cited in the flowsheet as ASSUMED (library ADR 0027).
Reason: no property package of core covers the alkaline bromide liquor, and core propagates
from the feeds without solving them for a product rate; the liquid enthalpies (heat capacities,
heats of dilution and reaction) are simple enough for a script. The liquor is a molecular
pseudo-component inventory (NaOH, NaBr, succinimide and NBS dissolved), not a speciation.
Until D-014 the precipitation and the wash dissolution were conversion "reactions" (PPT, DISS)
and the script gave the dryer's outlets and Q3 as well.

## D-007 Filtration and washing (2026-11-05)
Decision: agitated filter-dryer F-101 (three units since D-014, two before). Filtration F101:
99.8 % of the solid to the cake, 0.3 kg of liquor per kg of solid (ASSUMED). Reslurry wash W101
with 1.5 kg of ice water (278 K) per kg of solid: core's crystallizer fed by the cake and the
wash water, its crystals dissolving until the liquid is saturated with NBS (D-014; until then
a conversion "reaction" DISS of 1.5 x 0.0147 = 0.02205 of the crystals), then filtration F102
as F101. Result: 93.2 % of the bromine as NBS in the dried product; 4.3 % stays dissolved in
the mother liquor, 2.0 % in the wash, 0.4 % passes the filters as solid.
Reason: SRC-1 names the bromide contamination of the caustic route's product and the yield
lost to the washing water; a reslurry wash with ice water (the work-up SRC-1's examples use)
takes the NaBr in the cake from 15.3 wt% of its liquor to 2.5 %, at a loss of NBS the
solubility sets. An agitated filter-dryer keeps the wet NBS (an oxidant, light- and
moisture-sensitive) in one closed vessel.

## D-008 Drying and product (2026-11-05)
Decision: vacuum drying at 333 K in F-101 to 0.2 wt% moisture (ASSUMED; since D-014 core's
`dryer:` D101, its volatiles water and the free bromine); the salts and NBS dissolved in the
cake liquor dry onto the crystals. Product cooled in F-101 and discharged at 303 K to packing.
Reason: SRC-1's examples dry at 60 C; NBS decomposes when heated, so a low-temperature vacuum
drying is the usual choice. The dissolved NBS of the cake liquor is counted as NBS in the
product (it crystallises on drying).

## D-009 Utilities and heat (2026-11-05)
Decision: chilled brine at 263/268 K for the dissolver (Q1, 10.77 kW year average: the
dilution of the 50 wt% caustic to about 6 wt%, -20 kJ/mol NaOH, of the order of NaOH's
published integral heats of solution; the imide's deprotonation, -30 kJ/mol; the charge from
298 to 278 K at 3.8 kJ/(kg K)) and the brominator (Q2, 5.35 kW: the bromination, -50 kJ/mol at
0.999 conversion, and the bromine cooled from 293 K); LP steam 350 kPa(a) to the
filter-dryer's hot-water circuit (Q3, 24.64 kW from core's dryer model since D-014, 19.49 kW
before: the cake heated to 333 K at 1.6 kJ/(kg K), the water evaporated at 2358 kJ/kg and the
bromine at 187.5 kJ/kg, the vessel's metal heated from 278 K each batch, 70 % efficiency);
electricity 6 kW year average (agitators of
M-101 1 kW (P1) and R-101 2 kW (P2), filter-dryers and vacuum pump 3 kW (P3); a third
filter-dryer does not change the energy per batch, so P3 stays). All ASSUMED. The precipitation
hold CR101 and the wash W101 are declared adiabatic (`process/simulation.yaml`): their heats of
crystallisation are small and unknown.
The dryer's vacuum condenser cooling water is not counted (small).
During the 2 h dosing the brominator removes about 14 kW (10.5 kW per m3 of the final 1.35 m3,
`cheme process reactors`), 2.6 times the year average Q2; the dissolver about 57 kW over its 1 h
cool-down (Q1 x the 5.30 h cycle).

## D-010 Bromide and waste (2026-11-05)
Decision: the mother liquor, wash filtrate and dryer condensate (5.54 kg/kg NBS, 10.9 wt% NaBr)
go to the site wastewater treatment; the bromide is not recovered.
Reason: half of the bromine leaves as NaBr (SRC-1); recovering it (oxidation back to bromine,
e.g. in bromine-1) is the obvious integration but outside this concept. The NaBr carries 0.48
kg of bromine per kg of NBS: a heavy burden on the LCI if it is discharged.

## D-011 Thermal screening of the semi-batch (2026-11-05)
Result (`cheme process reactor-hazards`, core ADR 0050): adiabatic temperature rise of the whole
batch 19.7 K (the -50 kJ/mol of the step in R-101); largest accumulation of the dosed bromine
3.75 %, at the end of the dosing, when the imide's excess has run low; MTSR at the worst moment
278.9 K, against an MTT of 331.9 K (the normal boiling point of bromine, the lowest of the
liquor's components). No TD24 is known (NBS decomposes on
heating; never estimated): no criticality class (`cheme.reactor-hazard-missing`, info).
Interpretation: with the assumed fast kinetics the step is dosing-controlled. Even all at once
(a batch, X_ac = 1) the MTSR would be about 297.9 K, below the MTT, so the dilute charge, not
the dosing, keeps this step below the boiling point of bromine. A 100 times slower rate
accumulates 42 % of the bromine (MTSR 286.5 K) and needs about 93 h to reach 0.999 conversion:
the cycle, not the safety screening, would then rule out the semi-batch as designed. Open for the next stage:
calorimetry (heat of reaction, heat-flow profile, TD24 of NBS and of the wet cake), the dosing
interlock with the cooling and the agitator, the bromine vent to a caustic scrubber, and the
dryer's temperature limit for NBS. Screening values only, not a reaction-hazard assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-05)
Decision: `cheme assess lca --write` per kg of dried NBS from the flowsheet's year averages;
bromine and caustic soda linked to bromine-1 and chlor-alkali-1 (`lca/mappings.yaml`), the LP
steam counted as heat (kWh); every other background a gap with the activity it should connect
to. The rinses between batches (recipe operations clean of R-101 and F-101, 2 x 0.5 m3 per
batch, ASSUMED) are an `lca.yaml` consumable `per_batch` with its disposal to the wastewater
treatment (core ADR 0053, library ADR 0035): 2.99 kg per kg NBS at 1495 batches a year. Not
counted: the vents of R-101 and the dryer (no P&ID).
Per kg NBS: bromine 0.954 kg, succinimide 0.603 kg, caustic 50 wt% 0.487 kg, water 4.50 kg
(plus 2.99 kg of rinse water), electricity 0.095 kWh, LP steam 0.390 kWh (0.309 kWh before
D-014), brine 0.255 kWh removed, wastewater 5.54 kg (plus the rinses).

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101: composition, accumulation, cooling-failure temperature, peak cooling | done in cheme, kinetics ASSUMED | D-005, D-011, `cheme process reactors`, `reactor-hazards` |
| batch recipe, cycle time, basis check | done in cheme | D-003, `cheme process recipe` |
| precipitation and wash loss | done in cheme: crystallizers with spectators, solubility the 25 C value, no salting-out | D-005, D-007, D-014, core ADR 0056 |
| filtration | specified split in cheme; time by Ruth, cake data ASSUMED | D-007, D-014, core ADR 0057 |
| drying: outlets, duty Q3, drying time | done in cheme, moisture and rate ASSUMED | D-008, D-009, D-014, core ADR 0057 |
| feeds for 500 t/a, duties Q1 and Q2, S16 temperature | script | D-006, D-009; no feed sizing to a product rate and no liquor enthalpy in core |
| vessel sizing | done in cheme (R-101, F-101) | D-003, D-014, core ADR 0052, 0057; jackets not checked (no U yet) |
| per-batch exchanges (rinses) | done in cheme, amounts ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Lessons for core#158

- L-1: the semi-batch rules and the screening counted an energy stream into the step as an
  inlet: a power stream to R101 made it "2 charge streams". Found by this pilot; fixed in core
  1.7.0 (core#161: energy streams are neither charge nor dose), and R101 now has its own
  agitator stream P2.
- L-2: the crystallizer refused a mother liquor with other dissolved components; a batch
  precipitation from a reaction liquor needs it (package 4). Resolved in core 1.8.0
  (core#165, ADR 0056: `crystallizer.spectators`, a solubility `measured_in: mother_liquor` or
  corrected by `salting_out:`); CR101 and W101 use it (D-014).
- L-3: a recipe's unit procedure named one flowsheet step; the filter-dryer F-101 spans four
  (F101, W101, F102, D101), so the recipe named D101 for it, and the drying time was a guess.
  Resolved in core 1.8.0 (core#165, ADR 0057: `units: [F101, W101, F102, D101]`, `filter` and
  `dry` `from:` the filters' `filtration:` and the `dryer:`); the recipe uses it (D-014).
- L-4: the reactor's volumes are per hour of the year average; the batch volume and the vessel
  were worked out by hand. Fixed in core 1.7.0: the recipe sizes the vessel (core ADR 0052).
- L-5: the phase-change steps CR101 and W101 appeared in the thermal screening as reactors with
  missing data (info findings). Resolved in core 1.8.0 (ADR 0056: phase changes are not
  screened), and here by removing the conversion "reactions" altogether: `cheme process
  reactor-hazards` lists R101 alone (D-014).
- L-6 (open, D-014): core propagates from the feeds and cannot solve them for a product rate,
  so the feeds for 500 t/a still come from scripts/balance.py; no liquor enthalpy, so Q1 and
  Q2 do too.
- L-7 (open, D-014): the dryer writes no temperature on its outlets (the product's cooling in
  the vessel before discharge and the vacuum condenser are not modelled, and nor is the heat of
  cooling the vessel back to 278 K for the next batch's cold filtration).

## D-013 Dedicated train (2026-11-05)
Decision: M-101, R-101 and the three F-101 (two before D-014) make only NBS, batch after batch:
1495 batches in 7920 h on a dedicated train (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train
cannot be checked without the other products' campaigns.
Out of scope, so not LCI gaps: the changeover cleaning between campaigns of other products, the
idle time of a multipurpose train, shared tank farms and solvent recovery. NBS is often made on
multipurpose plants: there the burden per kg is higher, and this LCI is a lower bound for it.

## D-014 Precipitation, wash and filter-dryer on core's crystallizer and dryer models (2026-11-05)
Decision: the work-up is written with core 1.8.0's models (core#165, core ADRs 0056 and 0057)
instead of conversion "reactions" and a script:
- CR101 (in R-101, block REACT with R101) and W101 (the reslurry wash, fed by the cake S8 and
  the wash water S10) are `crystallizer: basis: solubility` steps for NBS in water, crystal
  NBS_S, at 278.15 K, with the liquor's other solutes as `spectators: [NABR, NAOH, SUCC, BR2]`
  (the NaBr formed, the 2 % excess of NaOH and succinimide, the 0.1 % of free bromine). The
  reactions PPT and DISS are deleted.
- Solubility basis: 0.0147 kg per kg of water, the 25 C value in pure water (SRC-2), taken at
  278 K (ASSUMED, as in D-005: no open value at 0-10 C was found, searched again 2026-11-05),
  with `salting_out:` coefficients of 0 for every spectator (ASSUMED): no open salting-out
  data of NBS in a NaBr/NaOH liquor exists, and for a polar imide with a bromide salt even the
  sign is uncertain (bromide sits on the salting-in side of chloride in the Hofmeister series),
  so no correction is taken. The mother liquor (1.79 mol NaBr per kg of water) is therefore
  assumed to dissolve NBS as pure water does. Both assumptions overstate what stays dissolved
  if NBS is less soluble cold and salted out, so the loss stays on the conservative side.
- F101 and F102 keep their specified split (D-007) and give a Ruth filtration time
  (`filtration:` ASSUMED: specific cake resistance 1e10 m/kg, a free-filtering crystalline
  cake; medium 1e10 1/m; 200 kPa of nitrogen; the liquor at 278 K 1.6 mPa s and 1130 kg/m3, the
  wash filtrate 1.5 mPa s and 1010 kg/m3, estimated from water's with the dissolved NaBr).
- D101 is a `dryer:` to 0.2 wt% volatiles (water and the free bromine, kept in their inlet
  ratio) at 333.15 K; energy: the wet cake 1.6 kJ/(kg K), latent heats water 2358 kJ/kg at
  333 K (steam tables) and bromine 187.5 kJ/kg (29.96 kJ/mol at its boiling point, CRC
  Handbook), the vessel's metal 1250 kJ/K (about 2.5 t of steel, ASSUMED) heated from 278 K
  each batch, 70 % efficiency (D-009). Drying rate 5 kg/(m2 h) (ASSUMED: a wall flux of about
  3.3 kW/m2, U 110 W/(m2 K) at a 30 K approach, over 2358 kJ/kg), wet-cake bulk density 1400
  kg/m3 (ASSUMED from the crystal density 2.098 g/cm3, PubChem, 0.3 kg of liquor per kg and
  some gas in the voids). The product and condensate keep their stated 303 K (D-008).
- The recipe's ISOLATE names `units: [F101, W101, F102, D101]`, one vessel: `filter` and
  `refilter` `from:` F101 and F102, `dry` `from:` D101, a 0.5 h reslurry, 0.5 h cool and
  discharge, 1 h rinse; the vessel is sized from one batch's slurry (fill 0.8, H/D 1.0,
  ASSUMED): 2 m3, 68 % full, D 1.37 m, the cake wetting 2.36 m2 of heated wall.
- F-101 is installed three times (`parallel: 3`), not two: with the calculated times one unit
  is occupied 12.75 h per batch, so two would take 6.38 h a batch, making F-101 the bottleneck
  with 1242 batches and 415 t/a. Three keep the design basis (500 t/a, 334.41 kg a batch, D-002,
  D-003) with the brominator still the bottleneck (F-101 80 % utilised).
- scripts/balance.py is reduced to what core still lacks (L-6): the feeds for 500 t/a, Q1, Q2
  and the temperature of S16; it still follows the balance-output contract (library ADR 0027).
How the numbers moved (before, 1.7.0 with the conversion steps and the script, -> after):
- yield on bromine 93.2 % -> 93.2 %; NBS left dissolved in the mother liquor 4.3 % and in the
  wash 2.0 % (1.41 kg/h of crystals dissolved, 2.2 % of the cake's) -> unchanged: with zero
  salting-out the crystallizer's equilibrium is the script's algebra (the streams S7 to S13
  agree to 5 significant figures);
- product 63.131 kg/h, 98.6 wt% crystals, 99.0 wt% NBS, 0.2 wt% moisture -> unchanged (the
  moisture now holds 0.08 ppm (by mass) of the free bromine; before, all of it left with the
  vapour);
- dryer duty Q3 19.49 kW -> 24.64 kW (+26 %): the vessel's metal heated each batch, 5.15 kW, is
  new; LP steam per kg NBS 0.309 -> 0.390 kWh;
- F-101: filtration 1.0 h -> 1.94 h, wash and refiltration 1.0 h -> 1.33 h, drying 5.0 h
  (guessed) -> 7.99 h (94.3 kg of water a batch over 5 kg/(m2 h) x 2.36 m2), occupancy 8.5 h ->
  12.75 h, units 2 -> 3;
- cycle 5.30 h, 1495 batches a year, bottleneck R-101 -> unchanged; one batch from charging to
  discharge 14.3 h -> 18.55 h.
Reason: the solubility, the basis of both phase changes, now sits in the flowsheet where
`cheme process crystallizers` reports it, rather than in a conversion worked out by a script;
the screening no longer sees phase changes as reactors (L-5); the dryer's outlets and heat and
F-101's times follow from stated inputs, so a measured cake resistance, drying rate or moisture
changes the cycle and the steam directly (L-3).
Rejected: `measured_in: mother_liquor` with the pure-water value (it would present a pure-water
figure as liquor data); an ASSUMED non-zero Setschenow coefficient (no basis for its size or
sign; it would lower the loss without evidence); a heated agitator (`vessel.heated_area`) to
keep two filter-dryers: it would need a drying rate of at least 6.85 kg/(m2 h) on the cake's
2.36 m2, or about 37 % more heated area at 5 kg/(m2 h), neither known at this stage; the
choice of two or three units is to be revisited with drying trials.
Open: the solubility of NBS at 278 K in the liquor (it sets the 6.3 % loss), the cake
resistance, the drying rate and the critical moisture from trials; the heat of cooling the
product and the vessel back down (L-7) is not counted.

## Open inputs
Kinetics and heat of reaction (calorimetry), TD24 of NBS and the wet cake; solubility of NBS at
0-10 C and in NaBr liquor (or its salting-out coefficients); filtration and wash data (cake
liquid, wash ratio, specific cake resistance) and the drying rate from trials (D-014);
product specification (assay, active bromine, free bromine, succinimide, colour); dryer
temperature limit; bromide recovery (D-010); a TEA (`operation.batch: {recipe: true}`).
