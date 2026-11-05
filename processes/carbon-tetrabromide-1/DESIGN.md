# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Carbon tetrabromide (CBr4) by the aqueous haloform route, issue
ChemE-as-Code/process-library#152. Concept stage: design basis, batch recipe, balanced BFD/PFD,
thermal screening of both dosed steps and a preliminary gate-to-gate LCI. Out of scope here:
P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-05): library `main` at a8f53ee4; cheme-as-code 1.8.0 (4e8fd80), the
library's pin. Template: processes/n-bromosuccinimide-1 (#370, #382), the library's first batch
entry; this folder follows its structure and library ADR 0035 (a dedicated train).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine translation; no paragraph numbers, so the locator is
the part of the document).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | CN101885665A, Method for preparing tetrabromomethane, https://patents.google.com/patent/CN101885665A/en | claims 1-4: water and NaOH charged, cooled to 0 C, bromine dripped in at no more than 5 C and stirred 20 min; tetrabutylammonium bromide as phase-transfer catalyst; acetone dripped in, then 3-5 h of stirring, standing, the solid separated and air-dried; bromine to acetone 10:1 by mass, bromine to NaOH 2:1 to 2:1.4 by mass. Embodiments 1-3: 500 mL water, 100, 120 or 140 g NaOH, 200 g bromine, 20 g acetone, 1 g catalyst; a white solid forms while the acetone is added. Description: bromoform not detected, a reagent-grade product. No yield, dosing time, drying temperature or assay | read (machine translation); patent, facts only | D-001, D-004, D-005 |
| SRC-2 | Wikipedia, Carbon tetrabromide, https://en.wikipedia.org/wiki/Carbon_tetrabromide | infobox: CAS 558-13-4, 331.627 g/mol, density 3.42 g/mL, melting point 94.5 C, solubility 0.024 g/100 mL water at 30 C; body: two polymorphs, the transition at 46.9 C; routes: methane bromination (mixed bromomethanes and HBr) and the halogen exchange of CCl4 with AlBr3 (cited there to Greenwood and Earnshaw); uses (Appel and Corey-Fuchs reactions, an intermediate). The haloform route is not mentioned | read; most infobox values carry no footnote | D-001, D-007, D-008, materials |
| SRC-3 | NIST Chemistry WebBook, SRD 69, https://webbook.nist.gov/chemistry/ | carbon tetrabromide (C558134): solid enthalpy of formation +29.4 kJ/mol (Bickerton et al. 1984), solid heat capacity 145.9 J/(mol K) at 298 K; bromoform (C75252): liquid enthalpy of formation +9.4 kJ/mol (Papina et al. 1982); acetone (C67641): liquid enthalpy of formation -249.4 kJ/mol (Wiberg et al. 1991), liquid heat capacity 125.45 J/(mol K) at 298 K, boiling point 329.3 K (mean of 117 values), enthalpy of vaporization 31.9 kJ/mol at 300 K | read (condensed-phase and phase-change pages) | D-005, materials, D101 |
| SRC-4 | Wikipedia, Standard enthalpy of formation, https://en.wikipedia.org/wiki/Standard_enthalpy_of_formation | table of inorganic substances: OH-(aq) -230, Br-(aq) -121, H2O(l) -285.8 kJ/mol (no source named for the table) | read | D-005 |
| SRC-5 | Wagman, D. D. et al. (1982) The NBS tables of chemical thermodynamic properties, J. Phys. Chem. Ref. Data 11, Suppl. 2 | BrO-(aq) -94.1, BrO3-(aq) -67.1, CH3COO-(aq) -486.0 kJ/mol | **not re-read in this session**: values recalled for the estimate and marked ASSUMED; a web snippet gave -91.5 kJ/mol for BrO-(aq) (a university wiki, not opened) | D-005 (estimate only) |
| SRC-6 | PubChem CID 11205 (carbon tetrabromide) and CID 74236 (tetrabutylammonium bromide); EBI OLS (ChEBI) | identity: formulas, InChIKeys; CHEBI:47875, CHEBI:51993 | read (PUG REST, OLS search) | chemicals registry |
| SRC-7 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | the accumulation and MTSR of a semi-batch, the criticality classes (method, implemented in core ADR 0050) | method reference, no data taken | D-011 |
| SRC-8 | processes/bromine-1, chlor-alkali-1, acetone-1, asu-1 (this library) | dry bromine; caustic soda 50 wt%; acetone from the cumene process; gaseous nitrogen | library, internal | feed links (D-004, D-012) |
| SRC-9 | Fuson, R. C.; Bull, B. A. (1934) The haloform reaction, Chem. Rev. 15, 275-309 | that CBr4 forms from bromoform with hypobromite | lead only: seen as a search snippet by the route scout, not read | D-001 (mechanism lead) |
| SRC-10 | Ullmann's Encyclopedia of Industrial Chemistry, Bromine Compounds, doi:10.1002/14356007.a04_405 | - | not read (licensed) | route reference lead only |

Searched and not found openly (2026-11-05, here and in the route scout): an industrial CBr4
production description with capacity, yield, kinetics or calorimetry of the haloform step, the
solubility of CBr4 below 30 C or in brine, and a market volume (only market-report pages, not
usable as sources).

## D-001 Route and boundary (2026-11-05)
Decision: the aqueous haloform route of SRC-1: bromine dosed into cold caustic soda to sodium
hypobromite, Br2 + 2 NaOH -> NaOBr + NaBr + H2O; acetone dosed into the cold hypobromite with
tetrabutylammonium bromide, C3H6O + 4 NaOBr -> CBr4 + CH3COONa + 3 NaOH (our own element
balance); overall C3H6O + 4 Br2 + 5 NaOH -> CBr4 + CH3COONa + 4 NaBr + 4 H2O. CBr4 precipitates
and is filtered, washed with water and dried, on a dedicated train (D-013). Boundary feeds:
bromine, caustic soda 50 wt%, acetone, the catalyst, process water, electricity, LP steam,
nitrogen (per batch); returns: chilled brine; outputs: dried CBr4, one wastewater stream.
Reason: the only route with an open, detailed source (charges, temperatures, order of
addition), a liquid batch process with a dosed exothermic step, a precipitation, a filtration
and a drying: what core 1.8.0 models. It uses the library's bromine (bromine-1), caustic
(chlor-alkali-1) and acetone (acetone-1). Mechanism: the methyl group is tribrominated through
its enolate, the trihaloketone cleaved by hydroxide to bromoform and acetate, and the bromoform
brominated further by hypobromite to CBr4 (SRC-9, a lead only); the phase-transfer catalyst
carries the hydrophobic bromoform's reaction (SRC-1 says it suppresses the bromoform).
**Caveat on relevance:** this route's industrial use rests on one Chinese patent and the
haloform literature; it is not shown to be how CBr4 is made at scale.
Rejected: the halogen exchange of CCl4 with AlBr3 at about 100 C (SRC-2): called the more
economical route there, but CCl4 is an ozone-depleting substance (feedstock use only), AlBr3
would be made from aluminium and bromine, there is no CCl4 in the library and no open process
description; a candidate variant (`carbon-tetrabromide-2`). Methane bromination (SRC-2): gas
phase, mixed bromomethanes and HBr, no open conditions found.
Links: bromine-1, chlor-alkali-1, acetone-1, asu-1 (nitrogen). No library process makes the
catalyst.

## D-002 Capacity, product and operating hours (2026-11-05)
Decision: 7920 h/a (330 days of 24 h), ASSUMED. Capacity 325 t/a dried CBr4, the result of the
ASSUMED feed basis of 80 kg of bromine per hour of the cycle (879 kg per batch) and the cycle
the models give (D-003): core sizes no feeds for a product rate (lesson L-7), so the capacity is
stated as what the chosen charge makes, not solved for a round number. Product: 99.6 wt% CBr4
(crystals and the CBr4 of the dried cake liquor), 0.19 wt% NaBr, 0.07 wt% NaOH, 0.04 wt% sodium
acetate, 0.1 wt% water (D-008). SRC-1 claims a reagent-grade product with no bromoform detected;
the bromoform is not modelled (D-005).
Reason: no open market or plant figure was found; CBr4 is a fine-chemical reagent and
intermediate, so a few hundred tonnes a year on a batch plant is the plausible scale. The LCI is
per kg and does not depend on the scale; the batch size and vessels do.

## D-003 Batch basis and recipe (2026-11-05)
Decision: one batch makes 450.91 kg of dried CBr4 (stream S16); the recipe
(`process/recipe.yaml`) has three unit procedures:
- HYPOBROMITE on M-101, one vessel over the mixer M100 and the semi-batch M101 (`units:`):
  charge 0.75 h, cool 1 h, dose the bromine 1.5 h and react 0.03 h (both from M101's model), a
  0.33 h hold (the patent's 20 min of stirring), transfer 0.5 h: 4.11 h;
- HALOFORM on R-101: nitrogen purge 0.25 h, receive 0.5 h, dose the acetone 4 h and react 4.23 h
  to 0.999 conversion of the hypobromite (both from R101's model; the patent stirs 3-5 h after
  the addition), a 0.5 h precipitation hold (CR101), transfer 0.5 h, rinse 1 h: 10.98 h;
- ISOLATE in two agitated filter-dryers F-101, one vessel over F101, W101, F102 and D101
  (`units:`, `parallel: 2`): filter 2.63 h and refilter 0.55 h by Ruth from F101's and F102's
  filtration data, a 0.5 h reslurry, dry 8.96 h from D101's drying rate, cool and discharge
  0.5 h, rinse 1 h: 14.14 h, 7.07 h each in turn.
The haloform reactor is the bottleneck: cycle time 10.98 h, 721.0 batches in 7920 h; one batch
takes 27.23 h from charging to discharge. The flowsheet's flows are the year averages of the
recipe: 450.91 kg x 721.02 / 7920 h = 41.05 kg/h of S16; `cheme process recipe` checks this (no
`cheme.recipe-basis` finding). Per batch: 878.8 kg of bromine, 83.8 kg of acetone, 967.7 kg of
caustic 50 wt%, 1713 kg of dilution water, 4.4 kg of catalyst, 878.8 kg of wash water.
Vessels (core ADR 0052, 0057; fill 0.8, H/D 1.2 for the reactors and 1.0 for the filter-dryer,
ASSUMED): M-101 2.76 m3 of liquor in 4 m3 (69 % full, D 1.62 m), R-101 2.79 m3 in 4 m3 (70 %,
D 1.62 m), F-101 2.79 m3 of slurry in 4 m3 (D 1.72 m, the cake wetting 2.93 m2). Jackets
(U 300 W/(m2 K), brine at 258 K, ASSUMED for glass-lined steel): M-101's peak duty 42.8 kW
while the bromine is dosed against 48.4 kW the jacket removes at the charge's wetted area;
R-101's 51.3 kW against 53.3 kW. **R-101's jacket sets the acetone's 4 h dosing**: a 2 h dosing
raises the peak duty to 99.5 kW, which the jacket cannot remove (`cheme.recipe-jacket` in a scratch copy; X_ac 16.7 %, MTSR 288.5 K).
Reason: core ADR 0051 puts the batch basis in one place; the dosing and post-reaction times come
from the reactor models and the filtration and drying times from F-101's models, so a change of
the kinetics, the cake data or the drying rate changes the cycle. The other durations are
ASSUMED concept values. F-101 is installed twice: one unit, occupied 14.14 h a batch, would be
the bottleneck (cycle 14.5 h, 545 batches a year).
Rejected: the patent's one pot (hypobromite and haloform in one vessel). Core's recipe cannot
hold two semi-batch steps in one vessel (lesson L-2), and a separate hypobromite vessel lets
M-101 prepare the next batch's hypobromite while R-101 runs; the hypobromite then waits about
0.8 h (hold and transfer), in which its disproportionation is not modelled (D-005).

## D-004 Feeds and charge (2026-11-05)
Decision, per mol of bromine: NaOH 2.2 mol (2 for the hypobromite and a 10 % excess; SRC-1's
range is 2.0-2.8), water 2.5 kg per kg of bromine in the charge with the caustic's water (SRC-1:
500 mL per 200 g), catalyst 5 g per kg of bromine (SRC-1: 1 g per 200 g), acetone 1.05 mol per
4 mol of bromine (SRC-1's 10:1 by mass is 1.10). Bromine from bromine-1 (100 % Br2 in the
model), caustic 50 wt% from chlor-alkali-1, technical acetone from acetone-1 (100 % in the
model), technical TBAB (100 %). The catalyst is charged with the caustic (SRC-1 adds it after
the bromine): in the model it takes part in no reaction, so the order does not matter; its
stability in the hypobromite is not assessed.
Reason: acetone is kept in a small excess, as SRC-1 does, so that the hypobromite (the bromine)
is used up and no oxidant is left for the wastewater; the excess is halved against the patent's
to lose less acetone. The NaOH excess keeps the hypobromite alkaline (it disproportionates
faster near neutral). The dilution keeps the CBr4 in a stirrable slurry (12 wt% solids) and the
NaBr far below its solubility.
Rejected: hypobromite in excess (full use of the acetone): it leaves oxidant in the liquor and
would need a quench reagent (sulfite), a further feed.

## D-005 Reactors M-101 and R-101: semi-batch models, kinetics, heats (2026-11-05)
Decision:
- M101 is `reactor: semibatch` (core ADR 0050): the charge S4 at 278.15 K, the bromine S5 (293 K)
  dosed at a constant rate over 1.5 h, then the post-reaction to 0.9999 conversion of the
  bromine, isothermal. Reactions HYPO and DISP.
- R101 is `reactor: semibatch`: the hypobromite S6 as charge, the acetone S7 (293 K) dosed over
  4 h (D-003), then the post-reaction to 0.999 conversion of the hypobromite, isothermal at
  278.15 K. Reactions HALO and DISP.
- Rate laws, all ASSUMED (no open kinetics found, 2026-11-05):
  - HYPO, second order in bromine and NaOH, k = 0.1 m3/(kmol s) at 278 K (k c_NaOH,0 = 0.5 1/s),
    Ea 40 kJ/mol: an ionic, effectively instantaneous reaction;
  - HALO, lumped, second order in acetone and hypobromite, k = 0.002 m3/(kmol s) at 278 K, Ea
    60 kJ/mol, chosen so that the post-reaction takes a few hours (4.2 h), as the patent's 3-5 h
    of stirring after the addition;
  - DISP, 3 NaOBr -> NaBrO3 + 2 NaBr, second order in hypobromite, k = 2e-7 m3/(kmol s) at
    278 K (about 0.5 % of the hypobromite an hour at 2 kmol/m3), Ea 80 kJ/mol: the known
    instability of hypobromite, made the yield loss of this concept (0.82 % of the hypobromite
    to bromate: 0.23 % in M101, 0.59 % in R101).
- Heats, ASSUMED Hess's-law estimates from SRC-3, SRC-4 and SRC-5 (the hydrated Na+ cancels):
  HYPO -40.9 kJ per mol of bromine; HALO -520.8 kJ per mol of acetone (CBr4 as the solid, so its
  heat of crystallisation is in it; of it about -405 kJ for acetone to bromoform and acetate and
  -116 kJ for bromoform to CBr4); DISP -28 kJ per mol of bromate. The hypobromite, bromate and
  acetate values are from SRC-5, not re-read: an uncertainty of a few kJ/mol on HYPO and some
  10 kJ/mol on HALO.
- The CBr4 is carried dissolved in R101's model (the liquid model has one phase) and
  precipitates in the hold CR101, core's crystallizer in the same block (D-007); the patent sees
  it precipitate during the addition. The free bromine left by M101 (0.01 %) passes R101 as a
  spectator (in the alkaline liquor it would be hypobromite, not modelled).
Reason: the lumped haloform reaction is what core's screening can assess honestly: with the
series steps written out (acetone to bromoform, bromoform to CBr4), the screening's cooling-
failure temperature would take the largest single reaction run to completion, not the series,
and the accumulation only of the dosed acetone, not of the bromoform intermediate that holds
most of the unreleased heat (lesson L-3). The lumped law cannot predict the bromoform impurity;
SRC-1 reports none, and the model's product has none.
**The low accumulation in D-011 is a consequence of the assumed rate law**; reaction calorimetry
(heat flow during the dosing, the heat of reaction, the onset of the hypobromite's decomposition)
must confirm it before basic engineering.

## D-006 Balance method and property gate (2026-11-05)
Decision: cheme propagates every stream: the mixers M100 and M103, the semi-batches M101 and
R101, the precipitation CR101 and the reslurry wash W101 as crystallizers with spectators (core
ADR 0056), the filters F101 and F102 as specified `solid_separation`, and the dryer D101 to its
residual moisture (core ADR 0057). No balance script: the feeds are the design inputs (D-002,
D-004), the reactor duties Q2 and Q3 are the heat that `cheme process reactors` reports for the
isothermal models plus the doses' sensible heat, the dryer's Q4 is core's (`cheme process
crystallizers`), and Q1 and the powers are hand estimates with their arithmetic in the stream's
`source` (D-009), all `provenance: assumed`.
Reason: no property package of core covers the alkaline hypobromite and bromide liquor; the
liquor is a molecular pseudo-component inventory (NaOH, NaOBr, NaBr, NaBrO3, sodium acetate,
acetone, catalyst, CBr4 dissolved), not a speciation. A script only for Q1 would be more code
than arithmetic.

## D-007 Precipitation, filtration and washing (2026-11-05)
Decision:
- CR101 (in R-101, block REACT with R101) and W101 (the reslurry wash, fed by the cake S10 and
  the wash water S12) are `crystallizer: basis: solubility` steps for CBr4 in water, crystal
  CBR4_S, with the liquor's other solutes as `spectators: [NAOH, BR2, NAOBR, NABR, NABRO3, ACET,
  TBAB, NAOAC]`, at 278.15 K (CR101) and 291.15 K (W101, about the mass-weighted mean of the
  cold cake and the wash water at 298 K).
- Solubility: 0.24 g per kg of water, SRC-2's 30 C value (0.024 g per 100 mL, taken per kg of
  water), at 278 and 291 K as well (ASSUMED: no lower-temperature value found). Entered as a
  single `value`, because core refuses a single 303 K point at another temperature (ADR 0025, no
  extrapolation; lesson L-4, n-bromosuccinimide-1 L-8). `salting_out:` coefficients 0 for every
  spectator (ASSUMED): a nonelectrolyte is salted out by NaBr and NaOH, so the pure-water value
  overstates the loss; no open coefficient exists. The loss is small either way: 0.12 % of the
  CBr4 stays dissolved in the mother liquor, 0.05 % dissolves in the wash.
- F101 and F102: 99.8 % of the solid to the cake, 0.15 kg of liquor per kg of solid (ASSUMED for
  dense crystals, 3.42 g/cm3), a Ruth filtration time (`filtration:` ASSUMED: specific cake
  resistance 1e10 m/kg, medium 1e10 1/m, 200 kPa of nitrogen; the mother liquor at 278 K 1.8
  mPa s and 1250 kg/m3, the wash filtrate 1.1 mPa s and 1030 kg/m3, estimated from water's with
  the dissolved salts). Wash: about 2 kg of water per kg of cake solid (80 kg/h), a reslurry.
Result: the wash takes the salts in the cake liquor from 28 wt% to 2 wt%; 0.4 % of the CBr4
passes the two filters as solid.
Reason: SRC-1 separates and air-dries the solid without a wash; a reagent grade with a
caustic bromide liquor of 28 wt% salts in the cake needs one (0.15 kg of that liquor per kg would
leave about 4 wt% salts in the product). An agitated filter-dryer keeps the volatile product in
one closed vessel.

## D-008 Drying and product (2026-11-05)
Decision: vacuum drying at 308 K in F-101 to 0.1 wt% volatiles (water, the acetone and bromine
traces in their inlet ratio, ASSUMED), core's `dryer:` D101; the salts of the cake liquor dry
onto the crystals. Energy: wet cake 0.9 kJ/(kg K) (CBr4 0.44 kJ/(kg K), SRC-3, with 0.15 kg of
liquor), latent heats water 2418 kJ/kg at 308 K (steam tables), acetone 549 kJ/kg (31.9 kJ/mol,
SRC-3), bromine 187.5 kJ/kg (as n-bromosuccinimide-1), the vessel's metal 1000 kJ/K (about 2 t
of steel) heated from 291 K each batch, 70 % efficiency, all ASSUMED; drying rate 2.5 kg/(m2 h)
(a wall flux of about 1.7 kW/m2 at a 15 K approach), wet-cake bulk density 2000 kg/m3, ASSUMED.
Result: 65.6 kg of vapour and 262 MJ a batch, 8.96 h of drying, Q4 6.63 kW year average.
Product cooled in F-101 and discharged at 303 K to packing.
Reason: CBr4 sublimes and changes polymorph at 320 K (SRC-2): a low drying temperature keeps it
in one crystal form and limits the sublimation loss; SRC-1 air-dries. The sublimation loss itself
is not modelled (lesson L-5).

## D-009 Utilities and heat (2026-11-05)
Decision: chilled brine at 258/263 K (ASSUMED) for M-101 and R-101:
- Q1 8.56 kW: the caustic diluted from 50 to 18 wt%, -12 kJ per mol of NaOH (ASSUMED, of the
  order of NaOH's integral heats of solution), 3.67 kW, and the charge from 298 to 278 K at
  3.6 kJ/(kg K), 4.89 kW;
- Q2 5.85 kW: M101's heat release, 1612.22 kJ per kmol of charge and dose x 12.705 kmol/h (HYPO
  and DISP, `cheme process reactors`), 5.69 kW, and the bromine cooled from 293 K, 0.16 kW;
- Q3 18.01 kW: R101's, 5032.57 kJ/kmol x 12.836 kmol/h, 17.94 kW, and the acetone cooled from
  293 K, 0.07 kW.
LP steam 350 kPa(a) to the filter-dryers' hot-water circuit: Q4 6.63 kW from core's dryer model.
Electricity 8.0 kW year average, ASSUMED: M-101's agitator 3 kW while occupied (4.11 of 10.98 h:
1.1 kW), R-101's 3 kW, the filter-dryers' agitators and vacuum pump 3 kW while a batch is in one
(14.14 h a batch: 3.9 kW). The precipitation hold CR101 and the wash W101 are declared
adiabatic (`process/simulation.yaml`): CBr4's heat of crystallisation is in HALO's heat
(D-005). The vacuum and vent condensers' cooling water is not counted (small). During the
dosing the reactors remove 42.8 kW (M-101) and 51.3 kW (R-101) at peak (D-003), 7.3 and 2.8
times the year averages.

## D-010 Bromide and waste (2026-11-05)
Decision: the mother liquor, wash filtrate and dryer condensate (9.04 kg per kg CBr4: 13.9 wt%
NaBr, 5.1 wt% NaOH, 2.7 wt% sodium acetate, 0.12 wt% acetone, 0.11 wt% catalyst, 0.06 wt%
bromate) go to the site wastewater treatment; the bromide is not recovered.
Reason: half of the bromine leaves as NaBr (0.98 kg of bromine per kg of CBr4, 50.1 % of the
bromine fed; 49.2 % is in the product, 0.14 % in the bromate), as in n-bromosuccinimide-1;
recovering it (oxidation back to bromine, e.g. in bromine-1) is the obvious integration but
outside this concept. The bromate (a toxic oxidant) and the alkalinity need treatment before
discharge; both are named in the LCI's treatment route, not modelled.

## D-011 Thermal screening and sensitivity of the semi-batches (2026-11-05)
Result (`cheme process reactor-hazards`, core ADR 0050), with `hazard.mtt` stated on each reactor
(the lowest boiling point of the liquor: M-101 and R-101 run at atmospheric pressure with a vent
condenser to a caustic scrubber, ASSUMED):

| step | dT_ad (whole batch) | X_ac max | MTSR | MTT | TD24 | class |
|---|---|---|---|---|---|---|
| M101 (bromine into caustic) | 21.8 K | 0.43 % at the end of the dosing | 283.1 K | 331.9 K (bromine) | unknown | none |
| R101 (acetone into hypobromite) | 68.3 K | 12.6 % at the end of the dosing | 285.5 K (at 3.78 h) | 329.3 K (acetone) | unknown | none |

No TD24 is known (the hypobromite's decomposition and that of the product; never estimated):
no criticality class (`cheme.reactor-hazard-missing`, info). M101's MTSR, 5 K above the
process temperature with almost no bromine accumulated, is the potential of the hypobromite's
disproportionation (DISP run to completion), which the screening takes as the largest reaction
(lesson L-8). No gas forms in either step, so no `batch.vent` (D-012).
Sensitivity (a scratch copy, the HYPO and HALO pre-exponential factors divided by 10 and 100,
DISP unchanged; nothing committed):

| case | M101 X_ac / MTSR | R101 X_ac / MTSR | R101 post-reaction | cycle | yield on bromine |
|---|---|---|---|---|---|
| assumed k | 0.43 % / 283.1 K | 12.6 % / 285.5 K | 4.2 h | 10.98 h | 98.5 % |
| k/10 | 3.0 % / 283.1 K | 34.9 % / 301.1 K | 44.4 h | 51.2 h | 98.0 % |
| k/100 | 13.9 % / 283.1 K | 79.5 % / 330.1 K | 318 h | 324 h | 94.4 % |

Interpretation: with the assumed kinetics both steps are dosing-controlled and the MTSR stays far
below the MTT: Stoessel class 1 or 2 if the TD24 lies above the MTSR. R101 carries the hazard:
the whole batch's adiabatic rise (68 K from 278 K) would boil the acetone, so the haloform step
is safe only as long as the acetone reacts while it is dosed. At a hundredth of the rate the
acetone accumulates to 80 % and the MTSR (330.1 K) passes the MTT: class 3 at best, 4 or 5 if a
decomposition sets in below it; at that rate the cycle (324 h) would rule out the design before
the screening did, but a slow start of a normally fast reaction (catalyst missing, too cold a
charge) is exactly that case. Open for the next stage: reaction calorimetry of both steps (the
heat flow during the dosing, the accumulation, the onset of the hypobromite's and the wet cake's
decomposition), the dosing interlocks with the temperature, the cooling and the agitator, the
catalyst charge check before the acetone dosing, the acetone vapour in R-101's vent (nitrogen
inerting) and the bromine vent of M-101. Screening values only, not a reaction-hazard
assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-05)
Decision: `cheme assess lca --write` per kg of dried CBr4 from the flowsheet's year averages;
bromine, caustic soda, acetone and nitrogen linked to bromine-1, chlor-alkali-1, acetone-1 and
asu-1 (`lca/mappings.yaml`), the LP steam counted as heat (kWh); every other background a gap
with the activity it should connect to. Per-batch consumables (core ADR 0053, library ADR 0035),
ASSUMED: the rinses of R-101 and F-101 (2 x 0.5 m3 per batch) with their disposal to the
wastewater treatment, 2.22 kg per kg CBr4; nitrogen 30 Nm3 (37.5 kg) per batch for R-101's purge
and blanket while the acetone (flash point below 0 C) is dosed and for pressing F-101's two
filtrations, 0.083 kg per kg CBr4. M-101 is not rinsed (the same hypobromite batch after
batch). No gas forms in the reactions, so the balance has no emission to air; the vents (acetone
vapour in R-101's nitrogen, bromine traces from M-101, CBr4 vapour and dust from the dryers) are
`emission_exclusions`, not estimated.
Per kg CBr4: bromine 1.949 kg, caustic 50 wt% 2.146 kg, acetone 0.186 kg, catalyst 9.7 g,
water 5.75 kg (plus 2.22 kg of rinse water), nitrogen 0.083 kg, electricity 0.195 kWh, LP steam
0.161 kWh, brine 0.790 kWh removed, wastewater 9.04 kg (plus the rinses).

## D-013 Dedicated train (2026-11-05)
Decision: M-101, R-101 and the two F-101 make only CBr4, batch after batch: 721 batches in
7920 h on a dedicated train (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train
cannot be checked without the other products' campaigns.
Out of scope, so not LCI gaps: the changeover cleaning between campaigns of other products, the
idle time of a multipurpose train, shared tank farms. CBr4 is likely made on multipurpose
plants: there the burden per kg is higher, and this LCI is a lower bound for it.

## D-014 Core features used and not used (2026-11-05)
Used (core 1.8.0):
- `reactor: semibatch` twice (ADR 0050), each with `batch.target` (the post-reaction from the
  model), `heat: isothermal` and `hazard.mtt` with its source; `cheme process reactor-hazards`
  for both;
- `process/recipe.yaml` (ADR 0051): `from:` durations of every dose, react, filter and dry
  operation; `units: [M100, M101]` (a mixer and a semi-batch in one vessel, sized from the
  semi-batch) and `units: [F101, W101, F102, D101]` (ADR 0057); `parallel: 2`;
- vessel sizing and the jacket check of both reactors (ADR 0052): the jacket set R-101's dosing
  time;
- `crystallizer.spectators` with a pure-water solubility and zero `salting_out:` coefficients
  (ADR 0056), twice, the second as a reslurry wash with two inlets;
- `solid_separation.filtration:` (Ruth) and `dryer:` with energy, drying rate and cake density
  (ADR 0057);
- per-batch `lca.yaml` consumables with a disposal (ADR 0053).
Not used, with the reason: `batch.vent` and `dosing.absorbed` (ADR 0054): no gas forms in either
reaction and both doses are liquids; `still:` (ADR 0055): no distillation in this route;
`kind: phase-change`: the precipitation is a crystallizer, not a reaction.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batches M-101 and R-101: composition, accumulation, cooling-failure temperature, peak cooling | done in cheme, kinetics ASSUMED | D-005, D-011, `cheme process reactors`, `reactor-hazards` |
| heats of reaction | Hess's-law estimates, ASSUMED | D-005 |
| batch recipe, cycle time, basis check, vessels and jackets | done in cheme | D-003, `cheme process recipe` |
| precipitation and wash loss | done in cheme: crystallizers with spectators, the 30 C solubility as a `value` (a workaround, L-4), no salting-out | D-007, core ADRs 0025, 0056 |
| filtration | specified split in cheme; time by Ruth, cake data ASSUMED | D-007, core ADR 0057 |
| drying: outlets, duty, time | done in cheme, moisture and rate ASSUMED | D-008, core ADR 0057 |
| reactor duties Q2, Q3 | cheme's heat release plus the doses' cooling, by hand | D-009, L-1 |
| dilution heat Q1, powers | hand estimates, ASSUMED | D-009, L-1 |
| feeds for a capacity | not solved: the capacity is the result of the stated feed basis | D-002, L-7 |
| per-batch exchanges (rinses, nitrogen) | done in cheme, amounts ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core limits hit (lessons for core)

Each is a candidate core issue; none blocked the entry, each forced a workaround or an
assumption recorded above.
- L-1: no enthalpy model of an aqueous electrolyte liquor and no duty written by the semi-batch
  model onto its energy stream: the dilution heat of the caustic (Q1) is a hand estimate, and
  Q2 and Q3 are worked out by hand from the heat release `cheme process reactors` prints (per
  kmol of charge and dose) and the doses' sensible heat. A dryer compares its duty with its
  energy stream (`cheme.process-dryer-duty`); a semi-batch has no such check, so Q2 and Q3 can
  drift from the model unnoticed.
- L-2: two semi-batch steps cannot share one recipe vessel (`cheme.recipe-reference`: a unit
  holding several batch or semi-batch steps is refused, ADR 0057). The patent's one pot
  (bromine into caustic, then acetone into the same vessel) had to become two vessels (D-003).
  Core needs a unit procedure over several batch steps in sequence, the vessel sized from the
  largest and each step's model starting from the previous one's end state.
- L-3: the semi-batch screening reports the accumulation of the first dosed reactant only and
  takes the cooling-failure temperature as the largest single reaction run to completion (ADR
  0050). For series reactions (acetone to bromoform to CBr4) the heat held in an intermediate,
  and the series' combined potential, are not counted, so the haloform steps had to be lumped
  into one reaction (D-005) and the bromoform impurity cannot be predicted. Core needs the
  potential of every reaction path from the current content (all reactions to completion, in
  sequence) and the accumulated heat, not only one reagent's accumulation.
- L-4: a single solubility datum away from the operating temperature has no honest form (as
  n-bromosuccinimide-1 L-8, still open in 1.8.0): `points: [[303.15, 0.00024]]` is refused at
  278 and 291 K, so CR101 and W101 use `value`, and `cheme process crystallizers` reports
  "solubility given at the operating conditions", which it is not.
- L-5: the dryer drives off only its `volatiles` in their inlet ratio (ADR 0057): the product's
  own sublimation (CBr4 has a noticeable vapour pressure) cannot be modelled as a loss, and a
  volatile kept below the residual moisture keeps the inlet ratio (no selective drying).
- L-6: the semi-batch is one liquid phase (ADR 0050): the CBr4 that precipitates during the
  dosing (the patent's observation) and the bromoform's second phase are carried dissolved, and
  the solid's volume counts in the liquid's concentrations; the precipitation is applied after
  the reaction (CR101). The phase-transfer catalyst's role cannot be expressed except through the
  assumed rate constant.
- L-7: core propagates from the feeds and cannot size them for a product rate (as
  n-bromosuccinimide-1 L-6): the capacity is stated as the result of the chosen feeds (D-002),
  and the batch size had to be set by hand to the product rate times the cycle (iterated twice,
  since the Ruth filtration time depends on the batch).
- L-8: a slow side reaction of a charged reagent (the hypobromite's disproportionation) enters
  the cooling-failure temperature as "the largest reaction run to completion": M101's MTSR (283.1
  K) is set by it, not by the dosed bromine, and the screening reports it as accumulation-driven.
  A decomposition-like side reaction is neither a TD24 nor the desired reaction; core does not
  tell them apart.
- L-9: the model does not run during the recipe's holds and transfers: the hypobromite's
  disproportionation over M-101's hold and the transfer (0.83 h) is not counted (a few 0.1 % of
  yield).

## Open inputs
Kinetics and heats of both steps (reaction calorimetry), the onset of decomposition (TD24) of
the hypobromite and of the wet cake; the yield and the bromoform content of a real batch (the
patent gives neither); solubility of CBr4 at 5-20 C and in the liquor; filtration and wash data
and the drying rate and sublimation loss from trials; product specification (assay, bromoform,
colour, water); the catalyst's fate; bromide recovery and bromate treatment (D-010); market and
capacity; a TEA (`operation.batch: {recipe: true}`).
