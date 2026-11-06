# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Phosphorus tribromide (PBr3) by the bromination of white phosphorus in a PBr3 heel, issue
ChemE-as-Code/process-library#134, the library's second semi-batch entry after
n-bromosuccinimide-1 (#140), whose pattern it follows (library ADR 0035, its D-013). Concept
stage: design basis, batch recipe with the brominator's vessel and jacket, balanced BFD/PFD,
thermal screening and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP,
TEA, datasheets.

Starting point (2026-11-05): library `main` at 0ed3b37a; cheme-as-code 1.7.0 (core main bd6cef7:
`reactor: semibatch`, `process/recipe.yaml` with vessels and jackets, per-batch LCA consumables;
core ADRs 0050 to 0053). Design analogue: phosphorus-oxychloride-1 (white phosphorus as a feed,
its D-003 and D-004).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine text, which has no column numbers, so the locator is the
part of the document).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US3409401A, H. Jenkner and O. Rabe (Chemische Fabrik Kalk), 1968: Method of producing phosphorus tribromide; family DE1281414B, GB1113288A, priority 1966-01-19; https://patents.google.com/patent/US3409401A/en | description (prior art): the older practice ran at 30-70 C in diluents with up to 25 % excess phosphorus against PBr5, which deposits as a solid in cooler parts, and left free phosphorus in the product (yellow colour, fire risk). Description and claims 1-5: air displaced by nitrogen or CO2; a PBr3 heel of about 2.5-3.5 times the phosphorus; heel warmed to about 60 C; reaction above 100 C, preferably 120-130 C; bromine 0.05-0.5 % above the stoichiometric need, throughout the reaction when both are fed together; feed rate limited by the heat removal; bromine into a phosphorus/PBr3 mixture (claim 2) or both fed at separate points (claim 3); batch: the product drawn off and the heel left for the next batch; crude slightly reddish; for a colourless product red phosphorus (description 0.5-5 wt%, claim 5 0.05-5 wt%) and a distillation under reduced pressure (no pressure or temperature given). Example: 600 kg PBr3 heel in a 1000 L enamelled stirred vessel under nitrogen at 60 C, 1552 kg bromine and 200 kg phosphorus fed over 2 h at separate points at 120-130 C with cooling, 2 kg more bromine, 600 kg kept as heel, the product distilled under vacuum over 2 kg red phosphorus: 1660 kg colourless PBr3 | read; patent, facts only | D-001, D-004, D-005, D-007, D-008, D-010 |
| SRC-2 | PubChem CID 24614, Phosphorus tribromide, https://pubchem.ncbi.nlm.nih.gov/compound/24614 | identity (Br3P, InChIKey IPNPIHIZVLFAFP-UHFFFAOYSA-N, CAS 7789-60-8 among the synonyms) | read (PUG REST) | chemicals registry |
| SRC-3 | chemicals and thermo packages (the open data of core's environment: CRC Handbook tables, NIST WebBook / JANAF, DIPPR fits, corresponding-states estimates) | printed per component in process/materials.yaml and scripts/balance.py: PBr3 liquid formation enthalpy -184.5 kJ/mol (CRC), gas -139.3 (CRC) and -146.0 (JANAF), normal boiling point 446.35 K, melting point 231.65 K, liquid density 2.80 g/cm3, vapour pressure and heat of vaporisation; molten phosphorus +0.62 kJ/mol per atom and liquid heat capacity 26.33 J/(mol K) per atom; white phosphorus solid density 1.823 g/cm3; bromine liquid density at 293 K | open data packages | D-005, D-006, D-008 |
| SRC-4 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | the accumulation and MTSR of a semi-batch (method, implemented in core ADR 0050) | method reference, no data taken | D-011 |
| SRC-5 | processes/bromine-1, processes/asu-1, processes/phosphorus-oxychloride-1 (this library) | dry bromine 99.96 wt%; gaseous nitrogen to the battery limit; white phosphorus held molten as a purchased feed (its D-003) | library, internal | D-004, D-012 |
| SRC-6 | Ullmann's Encyclopedia of Industrial Chemistry, Phosphorus Compounds, Inorganic (doi:10.1002/14356007.a19_527) and Bromine Compounds (doi:10.1002/14356007.a04_405) | - | not read (licensed); named by the issue's literature note | route reference leads only |

Searched and not found openly (2026-11-05): kinetics or reaction calorimetry of the bromination
of phosphorus, a TD24 of the crude or of PBr5, a measured liquid heat capacity of PBr3, the
cooling arrangement behind the patent's 2 h feed, the still's pressure and residue, a plant's
specific consumptions, and a market volume. A web search for PBr3 production consumption gave
only laboratory preparations and encyclopaedia summaries.

## D-001 Route and boundary (2026-11-05)
Decision: P4 + 6 Br2 -> 4 PBr3 in a PBr3 heel at 398 K with a small bromine excess (SRC-1), molten
white phosphorus and bromine dosed together; the heel kept in R-101 for the next batch; the rest
of the crude treated with red phosphorus and distilled under vacuum in a batch still C-101, on a
dedicated train (D-013). Boundary feeds: molten white phosphorus, bromine, red phosphorus,
nitrogen (per batch), electricity, LP steam; returns: cooling water; outputs: distilled PBr3,
the still residue to hazardous-waste incineration.
Reason: it is the industrial route of the one open process source (SRC-1); the small bromine
excess keeps free phosphorus out of the product, while the reaction temperature above 100 C
avoids the solid PBr5 that the older low-temperature practice suppressed with excess phosphorus
(SRC-1). It uses the library's bromine (bromine-1). All three reactants are liquid at the
reaction temperature and the reaction gives no gas, so the one-liquid-phase semi-batch of core
1.7.0 holds it (unlike the gas-evolving routes of #144, #159 and #160).
Rejected: bromine into a heel holding all the phosphorus (SRC-1 claim 2): the same chemistry,
but the whole phosphorus inventory is in the vessel when the cooling fails; co-feeding is the
mode of the patent's example. The older low-temperature route with excess phosphorus in a
diluent (SRC-1, prior art): free phosphorus in the product. Continuous operation with a siphon
draw-off (SRC-1 describes it too): a candidate variant (`phosphorus-tribromide-2`); the issue
asks for the batch entry. Red phosphorus as the main feed (a laboratory route): red phosphorus
is itself made from white.
Links: bromine-1 (bromine), asu-1 (nitrogen). No library process makes white or red
phosphorus (electrothermal furnace; thermal conversion of white to red), as in
phosphorus-oxychloride-1 D-001.

## D-002 Capacity, product and operating hours (2026-11-05)
Decision: 1000 t/a distilled PBr3, 7920 h/a (330 days of 24 h), ASSUMED. Product 99.9996 wt%
PBr3 in the model, with a trace of free bromine (D-008).
Reason: no open market or plant figure was found; PBr3 is a speciality reagent (brominations in
pharmaceutical and fine-chemical synthesis), so a batch plant of the order of the patent's
example (1.7 t per batch) is the plausible scale. The LCI is per kg and does not depend on the
scale; the batch size does (D-003).
Open: the product specification (assay, free bromine and PBr5, free phosphorus, colour, HBr).

## D-003 Batch basis and recipe (2026-11-05)
Decision: one batch makes 1421.23 kg of distilled PBr3 (stream S8); the recipe
(`process/recipe.yaml`) has two unit procedures: BROMINATE on R101 (nitrogen purge 0.25 h, the
dosing 10 h and the post-reaction 0.006 h to 0.9999 conversion of the phosphorus, both from
R101's model, sampling 0.5 h, transfer of the crude 0.5 h: 11.26 h) and DISTIL on C101 (receive
0.5 h, red-phosphorus treatment 1 h, evacuate and distil 4 h, break the vacuum and drain the
residue 1 h: 6.5 h). The brominator is the bottleneck: cycle 11.26 h, 703.6 batches in 7920 h;
one batch takes 17.26 h from the purge to the drained residue. The flowsheet's flows are the
year averages of the recipe: 1421.23 kg x 703.6 / 7920 h = 126.26 kg/h of S8; `cheme process
recipe` checks it (no `cheme.recipe-basis` finding). Per batch: 171.2 kg white phosphorus,
1330.5 kg bromine, 513.7 kg of heel, 1.71 kg red phosphorus, 82.2 kg of residue.
Reason: core ADR 0051 puts the batch basis in one place; the dosing time comes from the jacket
(D-010) and the post-reaction from the model, so a change of the dosing changes the cycle. The
other durations are ASSUMED concept values. There is no rinse between batches: the train stays
dry (PBr3 reacts with water), the heel stays in R-101 and the still is drained of its residue.
Vessel: the recipe sizes R-101 from R101's model (core ADR 0052, fill fraction 0.8 and H/D 1.2
ASSUMED): 0.72 m3 of crude at the end of the dosing in a 1 m3 vessel (the R10 preferred size),
72 % full, 1.02 m diameter; the patent's example ran its 1.75 t of product plus heel in a 1000 L
enamelled vessel (SRC-1), the same size. The still is not sized (no batch distillation model).

## D-004 Feeds, heel and charge (2026-11-05)
Decision: bromine 0.4 % above P4 + 6 Br2 -> 4 PBr3 (the patent example's 1554 kg on 200 kg of
phosphorus against a stoichiometric 1547.8 kg; claim 1: 0.05-0.5 %); a heel of 3.0 kg of crude
PBr3 per kg of phosphorus per batch (the example's 600 kg on 200 kg; the description's 2.5-3.5);
molten white phosphorus at 333 K, water-free, 100 % P4 in the model (phosphorus-oxychloride-1
D-003); bromine from bromine-1 at 293 K, 100 % Br2 in the model. Both dosed at constant rates
over the same 10 h, the bromine first in the dosing list (the reactant whose accumulation the
screening reports).
The heel is a recycle: X101 keeps back 45.64 kg/h of the crude (513.7 kg per batch) and R101 takes
it as its charge (S3). It is kept at the reaction temperature in R-101 between batches; the
patent warms its start-up heel to 60 C and lets the reaction heat it, which the isothermal model
does not follow (D-005).
Reason: the example is the one open set of quantities; the bromine excess keeps free phosphorus
out of the crude, at the price of a little PBr5 that the red phosphorus removes (D-007).

## D-005 Brominator R-101: semi-batch model, kinetics and heat of reaction (2026-11-05)
Decision: R101 is `reactor: semibatch` (core ADR 0050): the heel S3 at 398.15 K, the bromine
S2 and the phosphorus S1 dosed at constant rates over 10 h, then the post-reaction to 0.9999
conversion of the phosphorus (`batch.target`; 22 s from the model), isothermal at 398.15 K (125 C,
the middle of SRC-1's 120-130 C). Rate law of BROM: first order in dissolved bromine and in white
phosphorus, k = 1.0 m3/(kmol s) at 398 K, Ea 40 kJ/mol, ASSUMED. Heat of reaction -740.48 kJ
per mol of P4 (-185.1 kJ/mol PBr3, -684 kJ/kg PBr3): the CRC liquid formation enthalpy of PBr3
less that of molten white phosphorus, liquid bromine 0 (SRC-3). The gas formation enthalpies with
thermo's heat of vaporisation give -187.6 (CRC) to -194.2 (JANAF) kJ/mol for the liquid, 1.7 to
5.3 % more: the declared value is the smallest of them, to be confirmed by calorimetry.
The free bromine of the 0.4 % excess stays as Br2 in the model; in the crude it is bound as PBr5
(not a component). The liquid model holds the dosed bromine dissolved at 398 K, 66 K above its
normal boiling point: in the plant, bromine that does not react at once evaporates to the
reflux condenser.
Reason: no open kinetics or calorimetry of the bromination of phosphorus (searched 2026-11-05);
white phosphorus reacts vigorously with bromine, so a fast effective rate is the plausible
placeholder, and the second order makes the rate fall as either reactant runs low. The target
is 0.9999 rather than NBS's 0.999 because the fast rate reaches 0.999 before the dosing ends; a
target above the end-of-dosing conversion makes the outlet the target's, which the balance
script repeats exactly.
**The low accumulation of D-011 is a consequence of the assumed rate law** and must be
confirmed by reaction calorimetry (heat flow during the dosing) before basic engineering.

## D-006 Balance method and property gate (2026-11-05)
Decision: cheme propagates the semi-batch R101, the heel split X101 (S5 is the remainder of S4
after the given heel S3) and the red-phosphorus step T101 (conversion). The independent script
`scripts/balance.py` repeats the same algebra, converges the heel's composition (the recycle:
S3 has the crude's composition, which depends on S3) and gives the heel S3 as the tear stream,
the still's outlets S8 and S9 (D-008) and every duty, cited in the flowsheet as ASSUMED (library
ADR 0027). R101's extent from cheme (0.122774 kmol/h) and from the script agree.
White phosphorus is declared by hand in materials.yaml: the chemicals package returns monatomic
phosphorus gas for both P4 CAS numbers (+316.5 kJ/mol), which must not be used. No ideal-gas
data are given; the heat of reaction is declared (D-005). The PBr3 liquid heat capacity is
thermo's Rowlinson-Poling estimate, 132 kJ/(kmol K) at 398 K (ASSUMED); the default
Dadgostar-Shaw estimate (72) is below the ideal-gas value (79) and is not used.
Reason: propagate does not converge recycles, no property package of core covers PBr3 with
bromine and phosphorus, and core has no batch distillation (core#165).

## D-007 Red-phosphorus treatment (2026-11-05)
Decision: 1 kg of red phosphorus per 100 kg of white phosphorus dosed (the example's 2 kg on
200 kg, 0.1 wt% of the crude; within claim 5's 0.05-5 wt%) is stirred into the crude in the still
pot for 1 h before the distillation (T101); it takes up 99.9 % of the free bromine (2 P + 3 Br2
-> 2 PBr3, conversion ASSUMED). About 41 % of the red phosphorus reacts; the rest stays in the
residue. T101 is adiabatic (`process/simulation.yaml`): its heat, about 3 kJ per kg of product
(2 P + 3 Br2 -> 2 PBr3 at -334 to -369 kJ/mol, red phosphorus at -17.6 kJ/mol (CRC) or 0, on
0.0010 kmol/h: about 0.1 kW year average, an adiabatic rise of about 5 K in the still pot), is
not counted: S7 is kept at 398.15 K, so Q2 is about 0.1 kW (about 1 %) high.
Reason: SRC-1 adds red phosphorus before the vacuum distillation to get a colourless product;
the example's dose is enough for the 0.4 % excess.

## D-008 Vacuum distillation as a specified split (2026-11-05; revisit with core#165)
Decision: C-101 is a batch still with a short column at 4 kPa(a), where PBr3 boils at 345 K
(thermo's vapour pressure), reflux ratio 0.5 (ASSUMED). It is a **specified split** in
scripts/balance.py: all free bromine overhead, white and red phosphorus to the residue, and
94.6 % of the PBr3 overhead, set so that the overall yield on white phosphorus is the example's
95.0 % (1660 kg of 1747.8 kg theoretical, SRC-1). The residue (58 g/kg product: 98.7 wt% PBr3,
1.2 % red and 0.02 % white phosphorus) goes to hazardous-waste incineration. Product 308 K to
storage.
Reason: core has no batch (Rayleigh) distillation yet; core#165 is building it. The patent gives
no still pressure or residue: the 5 % loss of its example, which includes hold-up, fore-run and
handling losses, is put in the residue; this makes the residue large and the yield the
example's. **To revisit** when core#165 lands: model the still as a batch distillation (charge,
boil-up, cuts, the residue's PBr3 from the hold-up), give the distil operation its duration from
the model, and replace this split; then the yield is no longer taken from the example.
Rejected: a DWSIM shortcut column (no property package with PBr3).

## D-009 Utilities and heat (2026-11-05)
Decision (year averages, scripts/balance.py): R-101 to cooling water through a tempered-water
loop (Q1, 23.39 kW: the bromination less the doses' warming to 398 K); the still's reboiler on
LP steam 350 kPa(a) (Q2, 7.90 kW: 1.5 x the distillate evaporated at 45.6 kJ/mol, thermo, less
the crude's heat from 398 to 345 K); its condenser and product cooler to cooling water 298/308 K
(Q3, 9.50 kW); electricity 5 kW (R-101's agitator 2 kW, P1; the still's agitator and vacuum pump
3 kW, P2). All ASSUMED. Per kg PBr3: cooling water 0.260 kWh, LP steam 0.063 kWh, power 0.040
kWh. Over the 10 h dosing R-101 removes 28.4 kW at most (39.5 kW per m3 of the final content,
`cheme process reactors`); the reboiler about 22 kW over the 4 h distillation.

## D-010 Heat removal sets the dosing time (2026-11-05)
Decision: R-101's jacket, U 300 W/(m2 K) for an enamelled vessel with water (ASSUMED), on
tempered water at 333 K (ASSUMED: above the melting point of white phosphorus, 317 K, and not
cold enough to deposit PBr5 on the wall, SRC-1's prior-art problem); the recipe checks it
(core ADR 0052): 1.54 m2 wetted at the charge (the heel alone), 30.0 kW against the model's peak
28.4 kW at a 10 h dosing: the jacket check passes. A 6 h dosing (a batch of about 0.9 t in a
0.63 m3 vessel) needs about 30 kW where the jacket gives 22 kW at the charge
(`cheme.recipe-jacket`, a trial run), so 10 h it is.
Reason: SRC-1 limits the feed rate by the heat removal. Its example doses in 2 h, which is about
166 kW from a 1000 L vessel (1.20 GJ per batch); a jacket alone at a heel of 3 kg per kg of
phosphorus cannot remove that. The patent does not say how it cools; a reflux condenser, an
external cooler or a colder coolant could shorten the dosing and the cycle, but none is
evidenced, and core checks only a jacket or a coil (no external loop). Open for basic
engineering.

## D-011 Thermal screening of the semi-batch (2026-11-05)
Result (`cheme process reactor-hazards`, core ADR 0050): adiabatic temperature rise of the whole
batch 997 K (the reaction run to completion with the doses' heat capacity); largest accumulation
of the dosed bromine 0.575 %, at the end of the dosing (mostly the 0.4 % excess); MTSR at the
worst moment 399.6 K (81 s into the dosing, when the content is still the heel), against an MTT
of 446.35 K. No TD24 is known (none estimated): no criticality class
(`cheme.reactor-hazard-missing`, info).
MTT: `hazard.mtt` 446.35 K, the normal boiling point of PBr3 (SRC-3), the liquor's main
component: R-101 runs at atmospheric pressure under nitrogen with a reflux condenser (ASSUMED,
no P&ID yet). Without it
the screening takes the lowest normal boiling point of the liquor's components, bromine's
331.95 K, 66 K below the process temperature, which would flag every state of the batch.
Sensitivity (the rate constant divided, scratch runs, not in the files): by 10, accumulation 0.82
%, MTSR 405.7 K; by 100, 1.83 %, 426.1 K, post-reaction 1.6 h; by 1000, 5.1 %, 485 K, above the
MTT, post-reaction 17.5 h.
Interpretation: the step is safe in the screening only while it stays dosing-controlled: with an
adiabatic rise of about 1000 K, each 1 % of accumulated bromine adds roughly 10 K at the end of
the dosing and more early on, when the heel is small. The accumulated bromine also lowers the
liquor's boiling point below that of PBr3, so the MTT is optimistic for an accumulating batch.
Open for the next stage: calorimetry (heat of reaction, heat-flow profile, TD24 of the crude
with PBr5 and of the residue with red phosphorus), the dosing interlock with the cooling, the
agitator and the temperature, the bromine and HBr vent to a caustic scrubber, and white
phosphorus handling (pyrophoric, kept under water, transferred without air). Screening values
only, not a reaction-hazard assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-05)
Decision: `cheme assess lca --write` per kg of distilled PBr3 from the flowsheet's year
averages; bromine linked to bromine-1 and the nitrogen consumable to asu-1's gaseous nitrogen
(`lca/mappings.yaml`), the LP steam counted as heat (kWh); every other background a gap with the
activity it should connect to. The nitrogen for inerting R-101 and C-101 and breaking the still's
vacuum is an `lca.yaml` consumable `per_batch`, 6 Nm3 (7.5 kg) per batch, ASSUMED (core ADR 0053,
library ADR 0035): 5.3 g per kg PBr3 at 703.6 batches a year; it leaves through the vent to air
(no burden, no disposal exchange). Not counted: the vents of R-101 and of the vacuum pump, and the
water over the stored phosphorus (emission exclusions; no P&ID).
Per kg PBr3: bromine 0.936 kg, white phosphorus 0.120 kg, red phosphorus 1.2 g, nitrogen 5.3 g,
electricity 0.040 kWh, LP steam 0.063 kWh, cooling water 0.260 kWh rejected, residue 0.058 kg to
incineration.

## D-013 Dedicated train (2026-11-05)
Decision: R-101 and C-101 make only PBr3, batch after batch: 703.6 batches in 7920 h on a
dedicated train (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train
cannot be checked without the other products' campaigns. A dedicated PBr3 train is plausible:
the heel carries over from batch to batch and the train must stay dry.
Out of scope, so not LCI gaps: the changeover cleaning between campaigns of other products, the
idle time of a multipurpose train, shared tank farms and scrubbers. On a multipurpose plant the
burden per kg is higher, and this LCI is a lower bound for it.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101: composition, accumulation, cooling-failure temperature, peak cooling | done in cheme, kinetics ASSUMED | D-005, D-011, `cheme process reactors`, `reactor-hazards` |
| heel recycle | tear stream from the script | D-004, D-006; propagate does not converge recycles |
| batch recipe, cycle time, basis check | done in cheme | D-003, `cheme process recipe` |
| vessel sizing and jacket check (R-101) | done in cheme, U and coolant ASSUMED | D-003, D-010, core ADR 0052 |
| red-phosphorus treatment | conversion step in cheme | D-007 |
| vacuum distillation | specified split in the script | D-008; core#165 |
| duties | script | D-006, D-009 |
| per-batch exchanges (nitrogen) | done in cheme, amount ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Lessons for core

- L-1: a heel (part of a batch's content kept as the next batch's charge) has no core concept.
  It is a recycle around the semi-batch, which propagate does not converge, so the heel is an
  assumed tear stream from a script. A `batch.heel` (a fraction or mass of the outlet kept) would
  let the model and the recipe carry it.
- L-2: the default MTT (the lowest normal boiling point of the liquor's components) is the dosed
  bromine's 331.95 K, below the 398 K process temperature; `hazard.mtt` fixed it. A finding
  when the default MTT lies below the process temperature would point to `hazard.mtt`. The
  one-phase liquid model holds the dosed bromine 66 K above its boiling point; it neither flashes
  nor lowers the MTT as it accumulates.
- L-3: the jacket check compares the peak duty with the wetted area at the charge; with a heel
  of 3 kg per kg of phosphorus this sets a 10 h dosing where the patent doses in 2 h. There is no
  reflux-condenser or external-loop cooling, and no dosing profile checked against the area as
  it grows. The dosing time was found by hand (dosing time, cycle, batch size and vessel size
  depend on each other); a solve for the dosing time a jacket allows would help.
- L-4: no batch distillation (core#165): the still is a specified split in a script, and its
  distil duration and reboiler duty are not tied to each other.
- L-5: a recipe unit procedure names one step; the still C-101 holds T101 and C101 (as
  n-bromosuccinimide-1 L-3).
- L-6: an LCA consumable cannot carry a composition or a balance exclusion
  (`cheme.lci-balance-unassessable`, info, as for n-bromosuccinimide-1's rinse water), and a
  nitrogen purge leaving to air has no way to say so other than leaving out the disposal
  (`cheme.lca-disposal`, info).
- L-7: when the target conversion is reached before the dosing ends, the outlet holds the
  end-of-dosing conversion (0.9993 here at a 0.999 target), not the target; a balance script must
  then know the model's value. A target above it (0.9999) made the two agree.

## Open inputs
Kinetics and heat of reaction (calorimetry), TD24 of the crude and the residue; PBr3 liquid heat
capacity; R-101's cooling arrangement and U (D-010); the still's pressure, reflux, cuts and
residue (core#165, D-008); product specification; white phosphorus quality (arsenic, water);
the vent scrubber; a TEA (`operation.batch: {recipe: true}`).
