# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
N-Bromosuccinimide (NBS) by the caustic bromination of succinimide, issue
ChemE-as-Code/process-library#140, the batch pilot of ChemE-as-Code/core#158. Concept stage:
design basis, batch recipe, balanced BFD/PFD, thermal screening and a preliminary gate-to-gate
LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-05): library `main` at 256f1dc9; cheme-as-code from the core branch
`feat/158-batch-recipe` (core#161 `reactor: semibatch`, core#162 `process/recipe.yaml`, on 1.5.0).
The library's pinned core lacks both; the pin is bumped once they are released (core#158).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine text; no paragraph numbers, so the locator is the part
of the document).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US2971960A, T. D. and R. C. Waugh, 1961: Production of N-brominated imides and hydantoins, https://patents.google.com/patent/US2971960A/en | background (column 1): N-brominated imides were made by treating the imide in water with bromine and a strong base (or a separately made hypobromite); NaOH takes up the HBr; only half of the bromine enters the product, the other half becomes alkali bromide; the product is contaminated with bromide unless much water dissolves it away, which lowers the yield. Examples 1-4 (its own acid route with chlorine or hypochlorite, not used): the slurry is cooled to 5-10 C, filtered, washed with ice water and dried at 60 C; yields 66-76 % of theory | read; patent, facts only | D-001, D-007, D-008 |
| SRC-2 | PubChem CID 67184, N-Bromosuccinimide, https://pubchem.ncbi.nlm.nih.gov/compound/67184 | identity (C4H4BrNO2, InChIKey PCLIMKBDDGJMGD-UHFFFAOYSA-N, CAS 128-08-5); section Solubility (HSDB record): 1.47 g per 100 g water at 25 C | read (PUG REST and PUG View) | D-005, chemicals registry |
| SRC-3 | PubChem CID 11439, Succinimide | identity (C4H5NO2, InChIKey KZNICNPSHKQLFF-UHFFFAOYSA-N, CAS 123-56-8) | read | chemicals registry |
| SRC-4 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | the accumulation and MTSR of a semi-batch (method, implemented in core ADR 0048) | method reference, no data taken | D-011 |
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
is filtered, washed with ice water and dried. Boundary feeds: succinimide, bromine, caustic
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
Decision: one batch makes 315.66 kg of dried NBS (stream S14); the recipe
(`process/recipe.yaml`) has three unit procedures: DISSOLVE on M-101 (charge, dissolve, cool,
transfer: 2.5 h), BROMINATE on R-101 (receive, dose 2 h and react 0.5 h from R101's model, a
0.5 h precipitation hold, transfer, clean: 5.0 h) and ISOLATE in two agitated filter-dryers
F-101 (filter, reslurry wash, dry 5 h, discharge, clean: 8.5 h, 4.25 h each in turn). The
brominator is the bottleneck: cycle time 5.0 h, 1584 batches in 7920 h; one batch takes 14 h
from charging to discharge. The flowsheet's flows are the year averages of the recipe: 315.66
kg x 1584 / 7920 h = 63.13 kg/h of S14; `cheme process recipe` checks this (no
`cheme.recipe-basis` finding).
Reason: core ADR 0049 puts the batch basis in one place, so the balance, the LCI per kg and a
later TEA share it; the dosing and post-reaction times come from the reactor model, so a change
of the dosing changes the cycle. The durations of the other operations are ASSUMED concept
values; the dryer is doubled so that it is not the bottleneck.
Per batch: 1.27 m3 of slurry in R-101 at the end of the dosing (R101's 0.255 m3 per hour of the
year average x 5 h); about 1.6 m3 at an 80 % fill (ASSUMED; core#158 package 3 would size it).

## D-004 Feeds and charge (2026-11-05)
Decision: succinimide and NaOH 1.02 mol each per mol of bromine (the bromine limiting, so that
no free bromine is left), 30 mol of water per mol of bromine in the charge (the caustic's water
included), all ASSUMED. Bromine from bromine-1 (100 % Br2 in the model), caustic 50 wt% from
chlor-alkali-1, technical succinimide (100 % in the model).
Reason: one equivalent of base per bromine is the stoichiometry of the caustic route (SRC-1);
a small excess of imide and base keeps the bromine from accumulating as hypobromite. The
dilution keeps the NBS solids in a stirrable slurry (about 20 wt% solids) and the NaBr far below
its solubility.

## D-005 Brominator R-101: semi-batch model, kinetics and solubility (2026-11-05)
Decision: R101 is `reactor: semibatch` (core ADR 0048): the charge S4 at 278.15 K, the bromine
S5 (293.15 K) dosed at a constant rate over 2 h, 30 min post-reaction, isothermal at 278.15 K.
Rate law of BROM: first order in dissolved bromine, k = 0.05 1/s at 278 K (Ea 40 kJ/mol), and a
heat of reaction of -80 kJ/mol, both ASSUMED. The model gives full conversion of the bromine.
The NBS is carried dissolved in the reactor model (the liquid model has one phase) and
precipitates in the hold CR101 (reaction PPT, conversion 0.95388): the liquor leaves saturated at
14.7 g NBS per kg of water, the 25 C solubility (SRC-2) taken at 278 K as well.
Reason: no open kinetics or calorimetry of the caustic bromination exists (searched 2026-11-05).
The bromination of the imide anion is an ionic reaction known to be fast at 0-10 C (the
bromine is added "at once" in the laboratory procedures), so a fast effective rate is the
plausible assumption; with it the step is dosing-controlled. The heat of reaction is of the
order of the neutralisation of HBr by NaOH (about -57 kJ/mol) plus the N-bromination. The 25 C
solubility overstates what stays dissolved at 5 C: the loss in D-007 is conservative.
**The low accumulation in D-011 is a consequence of the assumed rate law** and must be
confirmed by reaction calorimetry (heat flow during the dosing) before basic engineering.
Rejected: core's crystallizer (`crystallizer: basis: solubility`): it refuses any component
besides its one solute and solvent, and the mother liquor holds NaBr, NaOH and succinimide
(D-006, lesson for core#158 package 4).

## D-006 Balance method and property gate (2026-11-05)
Decision: cheme propagates every stream up to the dryer: the mixers, the semi-batch R101, the
precipitation CR101 and the wash dissolution W101 as conversion steps (reactions PPT, DISS: a
phase change written as a reaction, balanced on elements), and the filters F101 and F102 as
specified `solid_separation`. The independent script `scripts/balance.py` repeats the same
algebra and gives the dryer's outlets (S14, S15) and every duty, cited in the flowsheet as
ASSUMED (library ADR 0027).
Reason: no property package of core covers the alkaline bromide liquor, and core has no dryer
model; the liquid enthalpies (heat capacities, heat of reaction) are simple enough for a script.
The liquor is a molecular pseudo-component inventory (NaOH, NaBr, succinimide and NBS
dissolved), not a speciation.

## D-007 Filtration and washing (2026-11-05)
Decision: agitated filter-dryer F-101 (two units). Filtration F101: 99.8 % of the solid to the
cake, 0.3 kg of liquor per kg of solid (ASSUMED). Reslurry wash W101 with 1.5 kg of ice water
(278 K) per kg of solid, the wash water leaving saturated with NBS (reaction DISS, conversion
0.02205 = 1.5 x 0.0147), then filtration F102 as F101. Result: 93.3 % of the bromine's NBS in
the dried product; 4.3 % stays dissolved in the mother liquor, 2.0 % in the wash, 0.4 % passes
the filters as solid.
Reason: SRC-1 names the bromide contamination of the caustic route's product and the yield
lost to the washing water; a reslurry wash with ice water (the work-up SRC-1's examples use)
takes the NaBr in the cake from 15.3 wt% of its liquor to 2.5 %, at a loss of NBS the
solubility sets. An agitated filter-dryer keeps the wet NBS (an oxidant, light- and
moisture-sensitive) in one closed vessel.

## D-008 Drying and product (2026-11-05)
Decision: vacuum drying at 333 K in F-101 to 0.2 wt% moisture (ASSUMED); the salts and NBS
dissolved in the cake liquor dry onto the crystals. Product 303 K to packing.
Reason: SRC-1's examples dry at 60 C; NBS decomposes when heated, so a low-temperature vacuum
drying is the usual choice. The dissolved NBS of the cake liquor is counted as NBS in the
product (it crystallises on drying).

## D-009 Utilities and heat (2026-11-05)
Decision: chilled brine at 263/268 K for the dissolver's cool-down (Q1, 5.42 kW year average:
the charge from 298 to 278 K at 3.8 kJ/(kg K)) and the brominator (Q2, 8.49 kW: the heat of
reaction and the bromine cooled from 293 K); LP steam 350 kPa(a) to the filter-dryer's hot-water
circuit (Q3, 19.49 kW: the cake heated to 333 K at 1.6 kJ/(kg K), the water evaporated at 2358
kJ/kg, 70 % efficiency); electricity 6 kW year average (agitators 1 + 2 kW, filter-dryers and
vacuum pump 3 kW). All ASSUMED. The brominator's agitator power is booked on the dissolver's
energy stream P1: an energy inlet on R101 counts as a second charge stream of the semi-batch in
the core build used (lesson L-1). The precipitation hold CR101 and the wash W101 are declared
adiabatic (`process/simulation.yaml`): their heats of crystallisation are small and unknown.
The dryer's vacuum condenser cooling water is not counted (small).
During the 2 h dosing the brominator removes about 21 kW (16.6 kW per m3 of the final content,
`cheme process reactors`), 2.5 times the year average Q2.

## D-010 Bromide and waste (2026-11-05)
Decision: the mother liquor, wash filtrate and dryer condensate (5.54 kg/kg NBS, 10.9 wt% NaBr)
go to the site wastewater treatment; the bromide is not recovered.
Reason: half of the bromine leaves as NaBr (SRC-1); recovering it (oxidation back to bromine,
e.g. in bromine-1) is the obvious integration but outside this concept. The NaBr carries 0.48
kg of bromine per kg of NBS: a heavy burden on the LCI if it is discharged.

## D-011 Thermal screening of the semi-batch (2026-11-05)
Result (`cheme process reactor-hazards`, core ADR 0048): adiabatic temperature rise of the whole
batch 31.5 K; largest accumulation of the dosed bromine 0.28 % (at the quasi-steady state of the
dosing); MTSR at the worst moment 278.2 K, against an MTT of 331.9 K (the normal boiling point
of bromine, the lowest of the liquor's components). No TD24 is known (NBS decomposes on
heating; never estimated): no criticality class (`cheme.reactor-hazard-missing`, info).
Interpretation: with the assumed fast kinetics the step is dosing-controlled. Even all at once
(a batch, X_ac = 1) the MTSR would be 309.7 K, below the MTT, so the dilute charge, not the
dosing, keeps this step below the boiling point of bromine. A 100 times slower rate (k =
5e-4 1/s) accumulates 27 % of the bromine and gives an MTSR of 286.7 K. Open for the next stage:
calorimetry (heat of reaction, heat-flow profile, TD24 of NBS and of the wet cake), the dosing
interlock with the cooling and the agitator, the bromine vent to a caustic scrubber, and the
dryer's temperature limit for NBS. Screening values only, not a reaction-hazard assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-05)
Decision: `cheme assess lca --write` per kg of dried NBS from the flowsheet's year averages;
bromine and caustic soda linked to bromine-1 and chlor-alkali-1 (`lca/mappings.yaml`), the LP
steam counted as heat (kWh); every other background a gap with the activity it should connect
to. Not counted: the rinses between batches (recipe operations clean: per-batch exchanges are
core#158 package 5), the vents of R-101 and the dryer (no P&ID).
Per kg NBS: bromine 0.953 kg, succinimide 0.603 kg, caustic 50 wt% 0.487 kg, water 4.50 kg,
electricity 0.095 kWh, LP steam 0.309 kWh, brine 0.220 kWh removed, wastewater 5.54 kg.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101: composition, accumulation, cooling-failure temperature, peak cooling | done in cheme, kinetics ASSUMED | D-005, D-011, `cheme process reactors`, `reactor-hazards` |
| batch recipe, cycle time, basis check | done in cheme | D-003, `cheme process recipe` |
| precipitation and wash loss | conversion steps from the solubility (25 C value) | D-005, D-007; core crystallizer refuses the impurities |
| filtration | specified split in cheme | D-007 |
| drying, duties | script | D-006, D-008, D-009; no dryer model in core |
| vessel and jacket sizing | by hand (D-003, D-009) | core#158 package 3 |
| per-batch exchanges (rinses) | not counted | core#158 package 5 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Lessons for core#158

- L-1: the semi-batch rules (`_dosing_rules` in core `domains/process/model.py`) and the
  screening (`reaction_hazards.screen_node`) count an energy stream into the step as an inlet:
  a power stream to R101 made it "2 charge streams". Worked around (D-009).
- L-2: the crystallizer refuses a mother liquor with other dissolved components; a batch
  precipitation from a reaction liquor needs it (package 4).
- L-3: a recipe's unit procedure names one flowsheet step; the filter-dryer F-101 spans four
  (F101, W101, F102, D101). The recipe names D101 for it.
- L-4: the reactor's volumes are per hour of the year average; the batch volume (x cycle time)
  and the vessel at its fill fraction are worked out by hand (package 3).
- L-5: the phase-change steps CR101 and W101 appear in the thermal screening as reactors with
  missing data (info findings).

## Open inputs
Kinetics and heat of reaction (calorimetry), TD24 of NBS and the wet cake; solubility of NBS at
0-10 C and in NaBr liquor; filtration and wash data (cake liquid, wash ratio) from trials;
product specification (assay, active bromine, free bromine, succinimide, colour); dryer
temperature limit; bromide recovery (D-010); a TEA (`operation.batch: {recipe: true}`).
