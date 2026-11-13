# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
tert-Butyldimethylsilyl chloride (TBSCl, tert-butylchlorodimethylsilane), the silylating agent
of the TBS protecting group, by the batch Grignard route, issue
ChemE-as-Code/process-library#147. An earlier scout kept it at Tier 1 until batch distillation
and a source for dichlorodimethylsilane were available; core 1.10.0 added the rectifying batch
still, the vent's vapour and condenser and the heats a batch model left out, so the entry is
built at Tier 2. It follows the library's batch entries (library ADR 0035): the Grignard
initiation screening of methylmagnesium-bromide-1, the vented semi-batch with a vent condenser
and the solvent loop of potassium-tert-butoxide-1, the filter-dryer of
methyltriphenylphosphonium-bromide-1 and the rectifying still of acetyl-chloride-1.
Concept stage: design basis, batch recipe with the reactors' vessels and jackets, balanced
BFD/PFD with the solvent recycle converged at its tear, thermal screening of the Grignard
initiation and both semi-batches, and a preliminary gate-to-gate LCI. Out of scope here: P&IDs,
layout, HAZOP, TEA, datasheets.

Starting point (2026-11-12): library `main` pinned to cheme-as-code 1.11.0, which this entry
needs (`plant.yaml` requires `cheme-as-code>=1.11`): the still's column, the vent's vapour and
condenser and the vessel's metal of core 1.10.0, and the generated sheets of 1.11.0.

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in the sessions that built this entry (2026-11-12 and 13).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | Shirahata, A. (Dow Corning Toray Silicone), US 5 068 386 A, Preparation of tertiary-hydrocarbylsilyl compounds, granted 1991-11-26 (priority JP 1989-06-28), https://patents.google.com/patent/US5068386A/en | Examples 1 and 3: magnesium (12.2 g, 0.5 mol) and tert-butyl chloride (46.3 g, 0.5 mol) in 250 mL of THF to the Grignard reagent; copper cyanide (1 mol%, Example 1) or sodium thiocyanate (0.34 g, 0.004 mol, Example 3) added at room temperature, dichlorodimethylsilane (64.5 g, 0.5 mol) dripped in, the mixture rising to 60 C, then 3 h at reflux; 100 mL of hexane added, the salt filtered off, the solvent distilled and the product distilled at ambient pressure: 60 g (80 %, Example 1) and 59 g (78 %, Example 3) of tert-butyldimethylchlorosilane, identified by NMR, IR and GC-MS (no purity given); claims 1 and 6 to 9: a cyano or thiocyanate compound catalyses the reaction, 0.01 to 10 mol%, preferably 0.1 to 2 mol%; the description says that the reaction was held not to occur without one | read (Google Patents full text); an expired patent, facts only | D-001, D-002, D-004, D-005, D-007 |
| SRC-2 | Cannady, J. P. and Nguyen, B. T. (Dow Corning), US 5 872 274 A, Method for preparation of tertiary-hydrocarbylsilyl compounds, published 1999-02-16, https://patents.google.com/patent/US5872274A/en | Example 10: tert-butylmagnesium chloride in diethylene glycol dibutyl ether (the Grignard solution of its Example 1, not THF) with dichlorodimethylsilane and without a catalyst gave only a trace of product after 18 h at 23 C and 4 more at 65 C; Examples 11 to 16: copper salts (acetate, cyanide, chloride, nitrate, sulfate, hydroxide) catalyse it in diethylene glycol dibutyl ether, the silane and the catalyst charged first and the Grignard solution added, two liquid phases within 5 min at 23 C; copper cyanide named as highly toxic; the work under nitrogen or argon | read (Google Patents full text); an expired patent, facts only | D-001, D-004, D-005 |
| SRC-3 | PubChem CID 28928 (tert-butylchlorodimethylsilane), https://pubchem.ncbi.nlm.nih.gov/compound/28928 | GHS notifications aggregated from the ECHA C&L inventory: H228 flammable solid (58 % of 236 notifiers), H314 severe skin burns and eye damage (76 %), H318, H335, H411; reacts with water to hydrochloric acid (the hazards summary, citing the Merck Index); a white hygroscopic solid; identity (InChIKey BCNZYOJHNLTNEZ-UHFFFAOYSA-N, ChEBI 85071) | read (PUG View and PUG REST); facts only | D-002, D-011, chemicals registry |
| SRC-4 | Hessel, G., Hulzer, G., Kryk, H., Palitzsch, P., Schmitt, W., Tefera, N., Weiss, F.-P. (2000) Calorimetric investigation of the formation of Grignard reagents, in: Forschungszentrum Rossendorf, Institute of Safety Research, Annual Report 1999, FZR-284, pp. 29-34, https://www.hzdr.de/publications/Publ-5058 | a bromobenzene derivative and magnesium in THF in a closed RC1 calorimeter: the initiation at 70 C after an induction time, then a steep, autocatalytic rise; molar reaction enthalpy 270 +/- 6 kJ/mol over 40 to 70 C (Table 1); the main stage controlled by the dosing, its rate constants at 40 C 0.65e-2 to 1.57e-2 L/(mol s) (Table 2); a large amount of halide dosed during a long induction time can end in a thermal explosion | read (the report's PDF, pp. 29-33) | D-005, D-011 |
| SRC-5 | NIST Chemistry WebBook, Methylmagnesium bromide (C75161), reaction thermochemistry, https://webbook.nist.gov/cgi/cbook.cgi?ID=C75161&Mask=8 | HBr(g) + CH3MgBr -> CH4 + MgBr2 (solution), -274.5 +/- 2.2 kJ/mol, Holm (1981) J. Chem. Soc. Perkin Trans. 2, 464 | read (by the session of 2026-11-12, as for methylmagnesium-bromide-1); US government data | D-005 |
| SRC-6 | NIST Chemistry WebBook, phase-change data of tetrahydrofuran (C109999), n-hexane (C110543), tert-butyl chloride (C507200), dichlorodimethylsilane (C75785) and tert-butylchlorodimethylsilane (C18162486), https://webbook.nist.gov | normal boiling points (THF 339 +/- 1 K, tert-butyl chloride 324.1 K, dichlorodimethylsilane 342.52 K); the Antoine coefficients NIST calculated for THF (Scott 1970, 296.29-372.8 K), n-hexane (Willingham, Taylor et al. 1945, 286.18-342.69 K), tert-butyl chloride (Stull 1947, 254-324 K) and dichlorodimethylsilane (Jenkins and Chambers 1954, 300.9-345.3 K; its heat of vaporization 31.5 kJ/mol at 316 K); tert-butyl chloride's melting point 247 K and dichlorodimethylsilane's triple point 199 K; TBSCl: boiling point 397 to 399 K (two catalogues of 1990), enthalpy of fusion 5.6 kJ/mol at 358.1 K (Braeuninger et al. 2010, DTA/DSC), no vapour pressure | read (each page, 2026-11-12 and 13); US government data | D-007, D-008, materials.yaml |
| SRC-7 | chemicals 1.5.2 and thermo 0.6.1, the packages of core's environment (open source, MIT; the versions core pins) | formation enthalpies (tert-butyl chloride liquid -211.3, isobutene gas -17.6, HCl gas -92.17 kJ/mol); liquid densities, heat capacities and heats of vaporization per component with the method each used (named in materials.yaml): DIPPR_PERRY_8E (THF), HEOS_FIT (n-hexane, isobutene, isobutane), MMSNM0, Zabransky's spline, Dadgostar-Shaw, Morgan-Kobayashi, Yamada-Gunn; TBSCl's Ambrose-Walton vapour pressure from estimated critical constants | packages queried; single values, facts only. The DIPPR_PERRY_8E and HEOS_FIT values are single facts with their package, version and method named (library ADR 0037), with no coefficients copied; Perry's Handbook and the DIPPR 801 database behind them were not read | D-005, D-006, D-007, materials.yaml |
| SRC-8 | PubChem CID 6398 (dichlorodimethylsilane), HSDB Methods of Manufacturing, https://pubchem.ncbi.nlm.nih.gov/compound/6398 | made by the action of silicon on methyl chloride with a copper catalyst (the direct process), or by a Grignard reaction of methyl chloride with silicon tetrachloride (HSDB, citing Hawley's dictionary, which was not read) | read (PUG View) | D-012 |
| SRC-9 | Wikipedia, tert-Butyl chloride, https://en.wikipedia.org/wiki/Tert-Butyl_chloride | made by the reaction of tert-butyl alcohol with hydrogen chloride (concentrated hydrochloric acid in the laboratory); melting point 247 K, boiling point 324 K; used for tert-butylphenol and neohexyl chloride | read; CC BY-SA, facts only | D-012 |
| SRC-10 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | the accumulation, MTSR and criticality classes of a semi-batch (method, implemented in core ADRs 0050 and 0058) | method reference, no data taken | D-011 |
| SRC-11 | processes/methylmagnesium-bromide-1, potassium-tert-butoxide-1, methyltriphenylphosphonium-bromide-1, acetyl-chloride-1, thf-1, tert-butanol-1, hydrogen-chloride-1, chloromethane-1, asu-1 (this library) | the Grignard initiation screening, the vent condenser and solvent loop, the filter-dryer, the rectifying still; THF and nitrogen linked; tert-butanol, HCl and chloromethane named as proxies | library, internal | D-004, D-006, D-007, D-011, D-012 |

Not read and not cited as read: Ullmann's Encyclopedia, Silicon Compounds, Organic (licensed;
named in the issue's literature notes as a lead only), Organic Syntheses procedures, supplier
data sheets and catalogues of TBSCl (its sold melting range and assay were not read; D-002).
Searched and not found openly (2026-11-12): a rate law or calorimetry of tert-butylmagnesium
chloride's formation or of its silylation, the selectivity of the tertiary halide's Grignard
formation, a TD24 of any mixture of the route, vapour pressures of TBSCl, VLE data of the
solvent pairs, a product specification, a plant's specific consumptions and a market volume.

## Core features used (cheme-as-code 1.11.0)

| feature | where | ADR |
|---|---|---|
| `reactor: semibatch` with `dosing.profile` and a `target` | R101 (5 % of the halide, a 30 min hold, then 95 %), R102 (the Grignard solution dosed into the silane) | 0050 |
| `batch.vent` with `vapour` and a `condenser` that returns the condensate, on its own `energy_port` | R101: isobutene and isobutane leave as they form, saturated with the liquid's volatiles, through E-103 at 268 K (Q2 by the model) | 0054, 0062 |
| a solid reactant (`phase: solid`) in the liquid semi-batch | magnesium in R101 (order 2/3 in its pseudo-concentration) | 0050 |
| the screening's default MTT of what boils, `per_reaction`, the MTSR profile, the gas release at the MTSR with the liquid's vapour against `hazard.vent_capacity` | R101, R102 (D-011) | 0058, 0062 |
| duties written by the models at `energy_port` | Q1 and Q2 (R101), Q3 (R102), Q5 and Q6 (ST101) | 0059, 0061 |
| recycle `tears:` with Wegstein | S29, the solvent loop (D-014) | 0060 |
| `still.column` (Diwekar's shortcut, constant reflux), two cuts, `still.heat_up`, `still.condenser_port` | ST101 with K-101 (D-007) | 0055, 0061, 0063 |
| `solid_separation` with `filtration:` (Ruth), `dryer:` with energy, drying rate and cake density; recipe `filter` and `dry` `from:`; `vessel.heated_area` | F101, F102, D101 in F-101 (D-006) | 0057 |
| recipe `units:` (one vessel over several steps), vessel sizing and jacket check, `heat` times from the jacket with `vessel.metal_heat_capacity` | R-101 (M101, E101, R101), R-102, F-101 (F101, M102, F102, D101), C-101 | 0052, 0057, 0063 |
| per-batch LCA consumables | nitrogen, sodium thiocyanate | 0053 |

Not used: `dosing.heat_of_solution` (ADR 0063): the halide and the silane are liquids that mix
into ether solvents with no sourced heat of mixing; `vent.henry`: no sourced Henry constants of
isobutene or isobutane in THF (they are taken to leave whole as they form, D-008);
`batch.heat_up`: R-101's warm-up is a recipe `heat` operation on hot water and its reaction on
brine, which one model duty on one stream would net (as potassium-tert-butoxide-1 L-11), and
R-102 runs at its charge's temperature (D-005); `dosing.absorbed`: nothing is dosed as a gas;
`hazard.reactions`: in R101 the largest reaction, GRIG, already sets the MTSR (DISP alone gives
316.1 K against GRIG's 317.7 K), R102 has one reaction; `still.purity` and `constant_distillate`:
the product cut ends on the residue (D-007); crystallizers: TBSCl is distilled and flaked, not
crystallised.

## D-001 Route and boundary (2026-11-12)
Decision: the Grignard route of SRC-1, Example 3: tert-butylmagnesium chloride from magnesium
turnings and tert-butyl chloride in THF (with the n-hexane of the solvent loop, D-014), then
dichlorodimethylsilane with sodium thiocyanate as the catalyst, the magnesium chloride filtered
off, the solvent recovered and the product distilled at ambient pressure; here with a rectifying
column (D-007) and flaked. A dedicated batch train (D-013). Boundary feeds: magnesium turnings,
tert-butyl chloride, dichlorodimethylsilane, THF and n-hexane make-up, sodium thiocyanate and
nitrogen (per batch), electricity, LP and MP steam; returns: chilled brine, tempered and cooling
water; outputs: TBSCl flakes to packing, the dried salt cake to quench and hazardous-waste
treatment, the still residue and the solvent purge to incineration, the vent gas to a thermal
oxidiser with an acid-gas scrubber.
Reason: SRC-1 is the one open source read that makes TBSCl from tert-butyl chloride at a scale
beyond a single flask with an isolated yield (78 %), and its work-up (filtration, solvent
distillation, product distillation) maps onto the core's batch models. A tertiary Grignard
reagent does not react with dichlorodimethylsilane without a catalyst (SRC-1's description,
SRC-2 Example 10, in diethylene glycol dibutyl ether): the catalyst is essential, and sodium thiocyanate (SRC-1 Example 3) avoids
copper cyanide, which SRC-2 names as highly toxic.
Rejected: copper cyanide (SRC-1 Example 1, 80 %): toxic, a cyanide in the salt cake. Copper
salts in diethylene glycol dibutyl ether (SRC-2 Examples 11-16): only the top phase's GC was
reported, no isolated yield, and the solvent's two-phase work-up has no basis here; a candidate
variant `tert-butyldimethylsilyl-chloride-2`. tert-Butyllithium with dichlorodimethylsilane: no
open source read, and tert-butyllithium (pyrophoric) is itself made from the chloride and
lithium metal. The direct process (silicon with methyl chloride) gives no tert-butyl silanes.
Tier 1 only (as the scout proposed): not needed, since core now models every step but the
flaking (L-7).
Links: thf-1 (the THF make-up) and asu-1 (nitrogen). No library process makes magnesium,
tert-butyl chloride, dichlorodimethylsilane, n-hexane or sodium thiocyanate: cited proxies and
LCI gaps (D-012).

## D-002 Capacity, product and operating hours (2026-11-12)
Decision: 721.9 kg of TBSCl flakes per batch (what one R-101 charge gives, ASSUMED), 7920 h/a
(330 days of 24 h), 803.3 batches a year from the recipe (D-003): 579.6 t/a. Product in the
model: 99.58 wt% TBSCl, 0.14 wt% THF, 0.20 wt% n-hexane and 0.09 wt% dichlorodimethylsilane
(`cheme process stills`). This is an upper bound on the assay: the siloxane from moisture, the
products of a double substitution or of a tert-butyl group's rearrangement, the catalyst's
residues and colour are not modelled, and no open product specification or supplier assay was
read. The yield is 74.6 % on the tert-butyl chloride bought (0.4835 kmol/h of TBSCl in the flakes
over 0.6478 kmol/h of halide), below SRC-1's 78 % isolated, and 97.7 % on the silane bought.
TBSCl is a solid (it melts at 358.1 K, SRC-6), flammable, corrosive and reacts with moist air to
HCl (SRC-3): flaked and packed under nitrogen.
Reason: no open market or plant figure was found. A 6.3 m3 Grignard reactor is a common size of a
fine-chemicals train; the capacity follows from it and the cycle. The LCI is per kg and does not
depend on the scale; the vessel sizes do (D-003).
Open: the specification (assay, the siloxane, chloride, colour) and the melting range as sold.

## D-003 Batch basis and recipe (2026-11-12)
Decision: one batch makes 721.9 kg of TBSCl flakes (stream S25); `process/recipe.yaml` has four
unit procedures:
- REACT on R-101 (`units: [M101, E101, R101]`): nitrogen inerting 1 h, charging the magnesium
  0.5 h and the recycled solvent with the make-up 1 h, the warm-up from 302.9 to 313.15 K from
  the jacket with the vessel's metal (0.415 h), the dosing with its initiation hold (3.25 h)
  and the post-reaction to 0.999 conversion of the halide (0.194 h), both from R101's model,
  sampling and titration 0.5 h, and the dosing of the Grignard solution into R-102, 3 h (R102's
  dosing time): 9.86 h;
- SILYL on R-102, started with R-101's dosing (`start: {after: REACT, operation: dose}`):
  inerting 0.5 h, charging the silane, the heel and the catalyst 0.75 h, a wait of 2.694 h,
  charged, until the Grignard solution is ready, the dosing of the Grignard solution 3 h and the
  post-reaction 1.61 h (R102's model), sampling 0.5 h, pressing the slurry to F-101 0.5 h:
  9.554 h. The Grignard solution leaves R-101 only as fast as R-102 doses it, so R-102's dosing
  must run exactly in R-101's transfer (6.86-9.86 h of the batch, a test checks it); the wait is
  R-101's dosing, post-reaction and sampling (3.25 + 0.194 + 0.5 h) less R-102's inerting and
  charging (1.25 h). Core's `start` names only an operation's start, with no offset, so the wait
  is set by hand and must follow a change of R101's times (L-15);
- FILTER on F-101 (`units: [F101, M102, F102, D101]`): receiving 0.5 h, the filtration 1.98 h and
  the wash's filtration 0.25 h from Ruth's equation, the reslurry 0.5 h, the drying 5.51 h from
  D101's drying rate, discharging 1 h: 9.746 h;
- DISTIL on C-101: receiving 1 h, the two cuts 6.67 h (ST101's boil-up), draining 0.5 h: 8.166 h.
R-101 is the bottleneck: cycle 9.86 h, 803.3 batches in 7920 h; one batch takes 28.88 h from
inerting R-101 to draining C-101. The flowsheet's flows are the recipe's year averages, `per
batch x 803.3 / 7920 h`: per batch 155.3 kg (6.390 kmol) of magnesium, 591.5 kg (6.390 kmol) of
tert-butyl chloride, 630.2 kg (4.883 kmol) of dichlorodimethylsilane, 87.8 kg of THF and 24.4 kg
of n-hexane make-up. `cheme process recipe` checks the basis (73.22 against 73.18 kg/h, no
`cheme.recipe-basis` finding); the batch size was set to the flakes one charge gives at the
cycle, which hardly depends on it (the dosing times are fixed by the jackets, D-010; only the
warm-up, the filtrations, the drying and the boil-up scale with the batch).
Vessels (core ADR 0052, fill 0.8 and H/D 1.2 ASSUMED): R-101 holds 4.97 m3 at the end of its
dosing in 6.3 m3 (R10 preferred size, 79 % full, D 1.88 m); R-102 6.37 m3 in 8 m3 (80 %); F-101
6.37 m3 in 8 m3 with a heated area of 12 m2; C-101 6.64 m3 in 10 m3 (66 %).
Two reactors, not one: SRC-1 makes the Grignard reagent and silylates it in one flask. A recipe
unit procedure holds one batch or semi-batch step (core: "several batch or semibatch steps, name
one as unit"), so the vessel could neither be sized nor its jacket checked for both steps (L-2);
and the order of addition of D-004 needs the silane in a second vessel anyway. R-101 is then
free for the next Grignard charge while R-102 finishes. R-102 is occupied 9.554 h of the 9.86 h
cycle (its wait included), 0.3 h short of becoming the bottleneck.
Reason: core ADR 0051 keeps the batch basis in one place; the dosing times come from the jackets
(D-010), the post-reactions, warm-up, filtrations, drying and boil-up from models, so a change of
the kinetics, a jacket, the cake or the still changes the cycle (D-011 shows by how much). The
other durations are ASSUMED concept values. No rinse between batches: the train is kept dry and
inert (a Grignard reagent and the chlorosilanes react with water).

## D-004 Feeds, charges and the order of addition (2026-11-12)
Decision:
- Magnesium turnings, 1.00 mol per mol of tert-butyl chloride, as SRC-1 (modelled as pure Mg, the
  oxide skin not modelled); 12.2 % of it is left unreacted with the salt (D-005, D-006).
- tert-Butyl chloride into R-101 at 313 K: 5 % in 15 min, a 30 min hold in which the initiation
  is confirmed (a temperature rise against the jacket, the heat flow, or in-situ IR, as SRC-4 did
  in the calorimeter), then 95 % over 2.5 h (`dosing.profile`). No activator (iodine, a heel of
  Grignard reagent) is modelled; one is usual for a sluggish initiation and stays an open input.
- The solvent: the recycled THF/n-hexane (D-014) with the THF and n-hexane make-up, dried on site
  below 100 ppm of water (a sieve; not modelled). In R-101's charge it gives 5.7 mol of THF and 1.3
  mol of n-hexane per mol of halide, against SRC-1's 6.2 mol of THF; SRC-1 adds its hexane (1.5
  mol per mol) only before the filtration, but THF and n-hexane cannot be parted in the still
  (normal boiling points 339 and 342 K), so the recycled solvent carries the n-hexane into the
  Grignard step (ASSUMED: a Grignard formation in an ether diluted with a hydrocarbon may start
  more slowly; an open input for the calorimetry).
- Sodium thiocyanate, 0.8 mol% on the tert-butyl chloride as SRC-1 Example 3: 4.14 kg per batch
  (0.0511 kmol, my arithmetic: 6.390 kmol x 0.008 x 81.07 kg/kmol), added to R-102 as a solid; an
  LCA consumable, not a component (L-5).
- Dichlorodimethylsilane: 630.2 kg per batch charged to R-102 with a heel of 15 % of the
  recovered solvent; the silane the recycle returns (in R-101's charge and in the heel) comes
  with them, so that R-102 ends with an excess: S9 carries 0.1732 kmol/h of silane unconsumed,
  35 % of the 0.4898 kmol/h R-102 consumes (D-014).
- The order of addition (reverse addition): the Grignard solution from R-101, with its excess
  magnesium and the salt of the side reaction, is dosed into the silane and the catalyst in
  R-102 over 3 h, as SRC-2 added its Grignard solution to the silane and catalyst. SRC-1 drips the
  silane into the Grignard solution instead. Here the recycled solvent carries silane into
  R-101's charge (0.1389 kmol/h, 28 % of the Grignard reagent formed, D-014), where it is taken
  not to react, ASSUMED: there is no catalyst in R-101, but the evidence is an extrapolation.
  SRC-2's Example 10, the one uncatalysed run read, was in diethylene glycol dibutyl ether at 23
  and 65 C, not in THF/n-hexane at 313 K with fresh magnesium present, and SRC-1 only states that
  the reaction was held not to occur, without a control run. If SIL ran uncatalysed in R-101, the
  0.1389 kmol/h at 200 kJ/mol would add about 7.7 kW year average, about 17 % of Q1, to the heat
  R101's model and its screening (GRIG and DISP only) count: an open input for the calorimetry
  (D-011). With SRC-1's order, the catalyst added to that Grignard
  solution would set off all of it at once: in a scratch copy with SRC-1's order (and a 630 kg batch)
  the model's peak in R-102 was 730 kW against the 243 kW its jacket removes at the charge
  (`cheme.recipe-jacket`). With the reverse order the heat follows the Grignard dose (at the
  ASSUMED rate 8.6 % of the dosed Grignard reagent is still unreacted at the end of the dosing,
  D-011), the peak is 95 kW (D-010).
Reason: SRC-1's catalyst and amount, SRC-2's order; the magnesium ratio is SRC-1's. The
initiation charge and hold are the established practice against a delayed initiation (SRC-4,
methylmagnesium-bromide-1 D-004).

## D-005 Reactions, heats and rate laws (2026-11-12)
Decision: three reactions (process/reactions.yaml), every rate law ASSUMED (no open kinetics of
any of them, searched 2026-11-12):
- GRIG, Mg + tert-C4H9Cl -> tert-C4H9MgCl, -270 kJ/mol: the HZDR's 270 +/- 6 kJ/mol for an aryl
  bromide in THF (SRC-4) as the analogue. First order in the halide, as the HZDR fitted the
  main stage, and of order 2/3 in the magnesium's pseudo-concentration (a surface proxy, as
  methylmagnesium-bromide-1); k = 0.01 (m3/kmol)^(2/3)/s at 313 K, inside the HZDR's 0.65e-2 to
  1.57e-2 L/(mol s) at 40 C; Ea 40 kJ/mol.
- DISP, tert-C4H9MgCl + tert-C4H9Cl -> isobutene + isobutane + MgCl2, the side reaction of a
  tertiary halide's Grignard formation (the tert-butyl radical gives up or takes a hydrogen
  atom), -173 kJ/mol, derived (my arithmetic): Holm's -274.5 kJ/mol for CH3MgBr + HBr (SRC-5)
  as the analogue of tert-C4H9MgCl + HCl -> isobutane + MgCl2, plus tert-butyl chloride (liquid)
  -> isobutene + HCl (gases), +101.5 kJ/mol from the formation enthalpies (SRC-7), both
  hydrocarbons as gases (they leave by the vent as they form). k = 1.5e-3 m3/(kmol s) at 313 K,
  set so that the yield stays below SRC-1's 78 %: DISP takes 12.2 % of the halide and as much of
  the Grignard reagent (0.0787 of 0.6478 kmol/h), 24.3 % of the tert-butyl groups.
- SIL, tert-C4H9MgCl + Me2SiCl2 -> TBSCl + MgCl2 with the thiocyanate, -200 kJ/mol, ASSUMED: no
  open value; of the order of a Grignard reagent's reaction with an electrophile; SRC-1's batch
  heating itself to 60 C as the silane was dripped in bounds it only from below (about 50 kJ/mol,
  my arithmetic). k = 5e-3 m3/(kmol s) at 313 K, Ea 40 kJ/mol: fast, as SRC-1's self-heating and
  SRC-2's phases forming within 5 min suggest; the catalyst is not a component (L-5). No reaction
  of the silane in R-101, ASSUMED (no catalyst there; an extrapolation to THF at 313 K of SRC-2
  Example 10, run in diethylene glycol dibutyl ether, and of SRC-1's statement; its size if it
  were wrong, about 7.7 kW or 17 % of Q1: D-004): SIL is not among R101's reactions.
The Grignard solution is carried as molecular pseudo-components (tert-butylmagnesium chloride
dissolved in the solvent, an inventory basis): the Schlenk equilibrium and the THF solvates of
the magnesium species are not modelled (materials.yaml).
R101 is isothermal at 313.15 K (40 C, below SRC-1's 60 C peak and 11 K below the screening's MTT),
at 101.3 kPa(a) under nitrogen. R102 is isothermal at 301.3 K, the temperature its charge (the
silane at 298 K and the heel at 303 K) mixes to: SRC-2's copper-catalysed runs went at 23 C, and
the colder vessel leaves more margin to the boiling liquor (D-011); SRC-1's 3 h at reflux is
replaced by the modelled post-reaction to 0.999 conversion of the Grignard reagent (1.61 h).
Result (year averages): GRIG 0.5690, DISP 0.0787 kmol/h (12.2 % of the magnesium left), SIL
0.4898 kmol/h; 99.9 % of the halide converted in R-101.
Reason: the calorimetry of SRC-4 is the one open, measured heat and rate of a Grignard formation
in THF found; a tertiary chloride is slower to start and more prone to the side reaction than an
aryl bromide, so both its heat and its rate are uncertain (D-011 takes the rate down by 10 and
100). **The low accumulation of D-011 is a consequence of the assumed rate laws** and must be
confirmed by reaction calorimetry before basic engineering.

## D-006 Filtration, wash and drying of the salt (2026-11-12)
Decision: F-101 is an agitated filter-dryer under nitrogen (as methyltriphenylphosphonium-bromide-1
D-006): `solid_separation` F101 with 99.8 % of the solids to the cake and 0.5 kg of liquor per kg
of solid (ASSUMED), the cake reslurried in 14 % of the recovered solvent (M102), filtered again
(F102, 99.9 %), then dried under vacuum at 343 K to 2 wt% solvent (D101, `dryer:` with an ASSUMED
drying rate of 4 kg/(m2 h) on 12 m2 and a cake density of 1100 kg/m3). Filtration times from
Ruth's equation with a specific cake resistance of 2e10 m/kg and a medium resistance of 1e10 1/m
under 200 kPa of nitrogen (all ASSUMED). The dried salt, 562 kg a batch (MgCl2 532 kg, the excess
magnesium 18.8 kg, solvent 11.3 kg; S15 x 9.865 h), is discharged warm into a quench drum. The
dryer's vapour is condensed after the dry vacuum pump in E-201 at 268 K; 1 % of the condensable
solvent leaves with the nitrogen bleed to the oxidiser (SP201, ASSUMED). The wet cake enters the
dryer at 302.4 K, the reslurried cake's temperature; the filter-dryer's steel (4000 kJ/K) is
reheated from it each batch and cools on the next slurry (its heat leaves with the filtrate).
Hazard of the quench: each mol of magnesium left gives one mol of hydrogen with water (Mg + 2 H2O
-> Mg(OH)2 + H2): 0.775 kmol of magnesium a batch (S15's 0.07855 kmol/h x 9.865 h) is about
0.775 kmol, 1.56 kg or 17 Nm3 of hydrogen per batch (my arithmetic), with the solvent's vapour
and the heat of the anhydrous MgCl2 dissolving. The quench drum must be inerted with nitrogen and
vented to a safe place (no air in its head space), and the water dosed against the gas rate;
its sizing and the vent's route are open inputs.
Reason: the salt must leave dry enough to be handled, and the solvent it holds (a third of the
wet cake) is worth recovering; a filter-dryer does filtration, wash and drying in one closed
vessel under nitrogen.

## D-007 Batch rectification of the filtrates and flaking (2026-11-12)
Decision: the filtrates (S21, 5.56 t a batch) go to the batch still C-101 with the packed column
K-101: `still:` at 101.325 kPa(a), Raoult's law with the NIST Antoine lines (SRC-6) and TBSCl's
ASSUMED line, `heat_up: true`, a boil-up of 250 kW (C-101's jacket and coil on MP steam, ASSUMED),
`column: {stages: 10, reflux: constant, ratio: 2}` (ASSUMED: SRC-1 distilled at ambient pressure
without stating a column). Two cuts: the recovered solvent with the excess silane and the
unreacted halide until the still holds 0.1 mol% of dichlorodimethylsilane (to T-301), then the
product cut until TBSCl is half of the residue's moles (the rest the salt fines that passed the
cloth). Result (`cheme process stills`): the still runs from 342.3 to 425.2 K in 6.67 h; the
recovered cut takes 99.97 % of the THF, 99.84 % of the n-hexane, 99.74 % of the silane and
22.38 % of the TBSCl (returned in the recycle, D-014); the product cut is 721.9 kg at 99.58 wt%
(D-002), 77.24 % of the still's TBSCl; the residue 5.82 kg. Year averages: reboiler 191.9 kW
(boil-up 168.9, the charge's heat-up 12.5, the pot's metal 10.5 kW), condenser 168.9 kW, both
written by the model (Q5, Q6).
The product cut is condensed at its boiling point, 398 K, on the tempered-water loop's hot
supply, 368.15 K, 10 K above TBSCl's melting point (358.1 K, SRC-6): the condenser is switched
from the cold supply (303/313 K, the recovered cut) before the TBSCl-rich vapour of the end of
the first cut reaches it, so that no product freezes on its tubes (L-9); the receiver and lines
to the flaker are traced on LP steam (Q11). The molten cut is solidified on the flaker E-102 on
cooling water and cooled to 308 K (Q7, hand arithmetic, L-7).
Heating medium: MP steam at 453 K for a still ending at 425 K; no decomposition temperature of
TBSCl or of the residue (the salt fines with traces of Grignard reagent) was found, so no limit
is stated; a TD24 of the residue is an open input.
Vapour pressures outside their fits: THF's Antoine line is used above its 372.8 K, n-hexane's
above 342.69 K and tert-butyl chloride's above 324 K and below 254 K, dichlorodimethylsilane's
outside 300.9-345.3 K (`cheme.process-still-note`, info); TBSCl's whole line is ASSUMED (thermo's
Ambrose-Walton from estimated critical constants, fitted over 300-440 K, giving 101.5 kPa at the
listed boiling point 398.15 K). The product's purity and the share of TBSCl recycled follow from
it and from the ideal-liquid assumption; no VLE data were found.
Reason: SRC-1's work-up; a column, not a simple still, separates the solvent (339-344 K) from the
product (398 K) with a small loss and returns the excess silane with the solvent. TBSCl is a
solid at ambient temperature, so it is sold as a solid; flaking is the simplest solidification.

## D-008 R-101's vent and vent condenser (2026-11-12)
Decision: isobutene and isobutane leave R-101 as they form (`batch.vent`, components [IB, IBA],
their whole amount: no sourced solubility in THF), saturated with the liquid's volatile
components at 313.15 K (`vapour`, Raoult with the Antoine lines; the Grignard reagent counted in
the liquid), through the vent condenser E-103 on chilled brine, the gas out at 268.15 K and the
condensate back to R-101 (`condenser: {returns: vessel}`). Per batch (`cheme process recipe`):
94.6 kg of vent gas, 0.777 kmol each of isobutene and isobutane with 0.063 kmol of THF, 0.012 of
n-hexane and traces of the halide and the silane; peak 34.0 m3/h at 268 K at the end of the
dosing. E-103's duty 0.75 kW year average (Q2, the model). The gas goes with the dryer's bleed
(S18) to the thermal oxidiser with an acid-gas scrubber (S31).
Coolant above every condensate's freezing point: brine at 263 K against tert-butyl chloride's
247 K (SRC-6, SRC-9), dichlorodimethylsilane's 199 K and lower values for THF and n-hexane;
the TBSCl the recycle brings (1.3e-5 kmol a batch past E-103) stays dissolved.
Reason: isobutene (a flammable gas) and isobutane must not accumulate in the head space; the
condenser keeps the solvent, the halide and the silane in the vessel and out of the oxidiser.

## D-009 Utilities and heat (2026-11-12)
Decision (year averages; the models' duties written by `cheme process propagate`, the others
typed with their arithmetic in the stream's `source`, all ASSUMED where not stated):
- chilled brine 263/268 K: Q1, R-101's reactions 45.20 kW (R101's model, with the doses warmed
  and the vent's vapour); Q2, E-103 0.75 kW; Q3, R-102's reaction 29.97 kW (R102's model); Q9,
  E-201 5.10 kW (the dryer's vapour condensed at 268 K, 3.98 kW, and the vacuum pump's 1.12 kW);
  Q12 and Q13, the agitators' work, which ends as heat in contents held on brine and which no
  model counts (L-12): R-101's 5 kW over its dosing, post-reaction, sampling and transfer (6.944
  of 9.86 h), 3.52 kW, and R-102's 6 kW over its charge, dosing, post-reaction, sampling and
  transfer (6.36 h), 3.87 kW; they do not change the jacket checks (R-101 178.1 + 5 = 183 kW against 233.8 kW,
  R-102 95.1 + 6 = 101 kW against 128.1 kW, D-010);
- LP steam 350 kPa(a) through hot-water loops: Q4, R-101's warm-up 3.014 kW (the recipe's heat
  of the warm operation with the vessel's metal, 107 MJ a batch); Q8, the dryer 12.23 kW
  (core's dryer model, `cheme process crystallizers`, copied at its precision); Q11, the tracing
  of the product's receiver and lines 2 kW;
- MP steam 1000 kPa(a): Q5, the still's reboiler 191.9 kW (ST101's model);
- tempered water 303/313 K (368/373 K for the product cut): Q6, the still's condenser 168.9 kW;
- cooling water 298/308 K: Q7, the flaker 3.98 kW (liquid cooling, fusion 5.6 kJ/mol and solid
  cooling of the cut); Q10, the recycle cooler E-301 9.55 kW (S26 from its 336.6 K mix to 303 K);
- electricity: P1, R-101's agitator 5 kW; P4, R-102's 4.17 kW (6 kW over its 6.86 h of
  operations in the 9.86 h cycle, stopped in the 2.694 h wait, D-003); P2,
  F-101's agitator and vacuum pump 5.07 kW; P3, the flaker 0.08 kW: 14.32 kW.
Mixed-stream temperatures are taken from their inlets with the liquid heat capacities of
materials.yaml: S6 302.9 K, S12 302.4 K, S21 301.4 K, S26 336.6 K (from S22 at its bubble point,
340.3 K, and S19 at 268.15 K), S33 301.3 K.
Per kg of TBSCl (73.18 kg/h): chilled brine 1.21 kWh removed (Q12 and Q13 0.101 of it), LP steam
0.236 kWh, MP steam 2.62 kWh, tempered water 2.31 kWh, cooling water 0.185 kWh, electricity 0.196
kWh.
Not counted, with their size: the warm salt's and the filter-dryer's heat after the drying (the
salt, 562 kg at about 0.75 kJ/(kg K), leaves at about 343 K into the quench drum, about 19
MJ a batch, 0.5 kW, and the steel cools on the next slurry, whose filtrate the still heats
anyway); the pipes' and tanks' heat losses other than the product's tracing; R-101's agitator
work before its dosing, over the inerting, the magnesium charge, the solvent charge and the
warm-up (1 + 0.5 + 1 + 0.415 = 2.915 h, about 52 MJ a batch, 1.48 kW year average), which goes
to the steel, the dry turnings and the charge before the warm-up and would shorten the warm-up on
hot water, so Q4 (107 MJ a batch) is high by at most that (in the empty vessel and the dry
turnings the agitator draws far less than 5 kW, so P1 is high there rather than the brine low);
R-102's agitator work over the inerting of the empty vessel (0.5 h, about 11 MJ a batch, 0.30 kW),
before its charge, likewise far below 6 kW unloaded, so P4 is high by up to that; F-101's agitator
work (4 kW), which ends in the cake and the filtrate, whose heat the dryer and the still supply
anyway. With these, Q12 and Q13 and the exclusions add up to P1 and P4 (5 = 3.52 + 1.48 kW,
4.17 = 3.87 + 0.30 kW).
Reason: the models give the reactions', the vent condenser's, the still's and the dryer's
duties; the rest are small sensible and latent heats from the stream table (L-7, L-12). The
refrigeration unit and the tempered-water loop are outside the boundary (LCA gaps, D-012).

## D-010 Heat removal sets the dosing times; the heating media (2026-11-12)
Decision: R-101 and R-102 have half-pipe jackets, U 400 W/(m2 K) for a stirred stainless-steel
vessel with brine (ASSUMED), on chilled brine 263/268 K; the recipe takes the coolant at the
log-mean driving force against the content (core takes the coolant temperature as constant):
265.69 K for R-101 at 313.15 K ((50 - 45) / ln(50/45) = 47.46 K) and 265.71 K for R-102 at
301.3 K ((38.15 - 33.15) / ln(38.15/33.15) = 35.59 K). The recipe checks them (core ADR 0052):
- R-101: 12.3 m2 wetted at the charge removes 233.8 kW against the model's peak 178.1 kW at the
  end of the 2.5 h main dosing.
- R-102: its charge (the silane and the heel, about 1.5 m3) wets only about 6.2 m2 of the 8 m3
  vessel, which would remove about 89 kW, below the peak of the Grignard dose; R-102 therefore
  has a jacket on the bottom head and an internal coil of about 6 m2, 9 m2 covered from the start
  (ASSUMED), which removes 128.1 kW against the model's peak 95.1 kW at a 3 h dosing.
Cooling water at 298 K would give a fifth of the brine's driving force and dosings of many hours.
Reflux cooling of the boiling solvent is not credited (core checks only a jacket or a coil).
Heating media against the stated limits: R-101 is warmed on hot water at 323.15 K, below the
screening's MTT, tert-butyl chloride's boiling point 324.1 K, and the liquor's bubble point,
340.3 K (D-011): a jacket left on hot water or a failed hot-water control cannot boil the
content. F-101's hot water at 353 K dries the salt under vacuum, its purpose. The still's MP
steam: D-007. A permissive for R-101's dosing that the jacket is on brine stays open (D-011).
Reason: the heat release, 1.61 GJ per batch in R-101 and 1.06 GJ in R-102 (Q1 and Q3 over the
cycle), must leave through the jackets; the dosing times were set by hand to the jackets' limits
(L-10).

## D-011 Thermal screening: initiation, accumulation, the vent, toxic gases and water (2026-11-12)
Result at the base rates (`cheme process reactor-hazards`, core ADRs 0050, 0058, 0062):
- R101: adiabatic rise of the whole batch 202.5 K; largest accumulation of the halide 2.21 %, at
  the end of the dosing (3.25 h); MTSR 317.7 K against an MTT of 324.1 K. Each reaction alone:
  GRIG MTSR 317.7 K, DISP 316.1 K, so GRIG sets it (the default) and `hazard.reactions` is not
  needed. The MTSR over the batch rises from 313.4 K at the start to 317.7 K at the end of the
  dosing; the initiation charge is not the worst moment at the base rate.
- R102: adiabatic rise 91.1 K; MTSR 309.3 K against 324.1 K, at the end of the 3 h dosing. The
  Grignard reagent dosed and not yet reacted is then 8.6 %: core's accumulation profile gives
  0.324 there, but of the dichlorodimethylsilane, not of the Grignard reagent (L-14), so of the
  0.663 kmol/h of silane charged (S33, 0.5243) and dosed with the recycle (S7, 0.1387) 0.215 is
  left, 0.448 has reacted, and of the 0.490 kmol/h of Grignard reagent dosed 0.042 has not (my
  arithmetic); the MTSR agrees, (309.3 - 301.3) / 91.1 = 8.7 %. The screening's headline 0.791 is
  likewise the silane's: the silane charged over the silane charged and dosed, 0.5243 / (0.5243 +
  0.1387), at the start of the dosing; it is not an accumulation of the Grignard reagent.
- No TD24 is known (none estimated): no criticality class (`cheme.reactor-hazard-missing`,
  info). With the MTSR below the MTT, core's criticality() gives class 1 or 2 if the TD24 lies
  above the MTSR (1 when it is also above the MTT) and class 5 if it lies below the MTSR; at k/10
  and k/100, with the MTSR above the MTT, it gives 3, 4 or 5. Only a TD24 from calorimetry
  decides between them.
The MTT: core's default is the normal boiling point of the most volatile component in the liquid,
here tert-butyl chloride, 324.1 K, also where it is only the dosed and accumulated reactant (in
R102 a trace from the recycle). The liquor's own bubble point is higher: 340.3 K for R-101's
charge and 342.5 K for R-102's slurry (Raoult, my arithmetic with the Antoine lines); the
default is conservative by about 16 K, and an accumulated halide does lower the liquor's boiling
point (L-6). Not set by hand.
Vent and gas release (`hazard.vent_capacity`, rule `cheme.reactor-hazard-vent`): R-101's vent
line through E-103 to the oxidiser's header is sized (ASSUMED) at 100 m3/h, three times the
normal peak (34.0 m3/h past E-103). At a cooling failure at the base rate the side reaction at
the MTSR forms isobutene and isobutane at 47.9 m3/h, with the liquid's vapour 80.1 m3/h at 317.7 K
(0.80 of the capacity); run to completion from the worst moment DISP would form 0.283 kmol (7.4
m3; 12.3 m3 with the vapour).
Sensitivity of the rate (all three rate constants divided; scratch copies, not in the files):

| case | R101 accumulation | R101 MTSR | gas at the MTSR (R101) | R102 Grignard reagent accumulated (core's X_ac of the silane) | R102 MTSR | cycle | batches/a | screening reading |
|---|---|---|---|---|---|---|---|---|
| base (ASSUMED k) | 2.21 % | 317.7 K | 80.1 m3/h | 8.6 % (0.324) | 309.3 K | 9.86 h | 803.3 | both MTSR below the MTT (324.1 K) and the liquor's bubble point; gas within the vent |
| k/10 | 15.5 % | 345.1 K | 109.8 m3/h | 37.9 % (0.541) | 336.2 K | 25.04 h | 316.3 | both above the MTT; R-101's content boils (105.2 kPa at the MTSR); the non-condensables alone 1.1 times the vent |
| k/100 (sluggish or delayed initiation) | 62.9 % | 441.1 K | 582.2 m3/h | 83.8 % (0.880) | 377.8 K | 214.8 h | 36.87 | far above: the solvent boils off, the C4 gases alone 5.8 times the vent |
| initiation charge uninitiated (5 % only, k/10000) | 99.9 % of the 5 % | 324.9 K | - | - | - | - | - | the 5 % alone reaches the MTT (the halide's boiling point), 15 K below the liquor's |
| whole dose uninitiated (k/10000, dosing not stopped) | 99.4 % | 514.5 K | - | - | - | - | - | the classic Grignard runaway (SRC-4) |

R102's accumulation is the Grignard reagent's at the end of the dosing, from the silane balance
as in the base case (the MTSR gives 8.7, 38.3 and 84.0 %); core's X_ac of the silane is in
brackets (L-14). The cycles of k/10 and k/100 are R-102's occupancy (the bottleneck there) with
R-102 inerted and charged just before R-101's later transfer, without an idle wait; the start
of the files (with R-101's dosing) would add a wait of 5.5 h and 38.3 h to align the dosing
with that transfer, which core's `start` cannot shorten by an offset (L-15).
The gas release of the k/10 and k/100 cases takes the rate laws at the MTSR, far outside their
ASSUMED 293-343 K range, and the content boils there, which the screening does not size: an
order of magnitude, not a value.
Interpretation: while the reactions run at their dosing rates, a cooling failure stays below the
boiling liquor in both reactors. If the Grignard formation is slow or delayed (k/100 stands for an
induction period, which core cannot model, L-1), most of the halide accumulates and a cooling
failure would boil the solvent; dosing into a reactor that never initiated makes nearly the
whole 202.5 K available. Each 1 % of accumulated halide adds about 2 K. The design consequences,
open for the next stage: the initiation charge must not exceed about 5 % (5 % uninitiated
already reaches the halide's boiling point); R-101's main dosing must be interlocked on a
positive initiation signal and stopped on low heat flow, high temperature, loss of brine or of
the agitator; R-102's dosing likewise on its temperature and cooling (at k/10 the accumulated
Grignard reagent takes R-102 above the MTT).
Design finding, the vent: R-101's vent passes the base case's gas release, but not that of a
slower reaction: at k/10 the C4 gases alone are 109.8 m3/h, 1.1 times the 100 m3/h, and the
content boils; at k/100 582.2 m3/h, 5.8 times. No credible process vent passes the k/100 case;
it is not hidden by a larger `vent_capacity`. It is met by not letting it arise (the dosing
interlocks above, with the calorimetry that sets the real accumulation) and by an emergency
relief of R-101 and of R-102, separate from the process vent, sized for the boiling-solvent case
with the gases (two-phase venting likely, a DIERS-type sizing) and routed to a containment or the
oxidiser, never to atmosphere. Both are open safeguards for basic engineering.
Flammable and toxic releases: what accumulates in R-101 is tert-butyl chloride (a flammable
liquid boiling at 324 K, SRC-6), about 13 kg at the base rate (2.21 % of the 591.5 kg dosed per
batch, my arithmetic), about 92 kg at k/10, about 372 kg at k/100 and about 30 kg for an
uninitiated 5 % initiation charge; a cooling failure drives it out first, with the isobutene and
isobutane (flammable gases) and the solvent. None of them is acutely toxic like the methyl
bromide of methylmagnesium-bromide-1; the relief's route is set by flammability.
Water ingress: the chlorosilanes and the Grignard reagent react with water. Water reaching R-102
(a leaking jacket or coil, the brine being water-based) would turn the silane into HCl (two mol
per mol of Me2SiCl2) and siloxanes, and the Grignard reagent into isobutane: R-102's charge holds
5.17 kmol of silane a batch (S33's 0.5243 kmol/h x 9.865 h), up to about 10.3 kmol (232 Nm3) of
HCl, a toxic, corrosive gas, and R-101's Grignard solution 4.84 kmol of reagent, up to 4.84 kmol
(108 Nm3) of isobutane (my arithmetic, 22.414 Nm3/kmol). The HCl goes through the vent to the
oxidiser's acid-gas scrubber: a loss of the scrubber's water (or of its circulation) would pass
it to the stack. Open safeguards: a non-aqueous heat-transfer fluid in R-101's and R-102's
jackets and coil, or leak detection on the brine (a conductivity or pressure test of the jacket),
and an interlock of the vent's routing on the scrubber's water flow; the same holds for E-103
and E-201, whose brine also meets chlorosilane-bearing liquid. TBSCl and the cake's traces of
silane give HCl with moist air in packing and in the quench drum (SRC-3).
Open: calorimetry (the heats and rates of GRIG and SIL, the induction time, the side reaction's
share, whether the recycled silane reacts uncatalysed in R-101's THF at 313 K (up to about 7.7
kW, D-004), TD24 of both reaction masses, of the still residue and of the wet salt), the reliefs of
R-101 and R-102, the dosing interlocks, the brine's water path, the quench drum.
Screening values only, not a reaction-hazard assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-12)
Decision: `cheme assess lca --write` per kg of TBSCl flakes from the flowsheet's year averages.
Linked (`lca/mappings.yaml`), kg for kg with the grade checked: the THF make-up to thf-1 (99.95
wt% THF with 0.05 wt% water, dried on site to the Grignard grade, the drying not modelled), the
nitrogen consumable to asu-1's gaseous nitrogen, the LP and MP steam as heat (kWh). Every other
background is a gap with the activity it should connect to. Feeds without a library producer,
with their cited proxies recorded in `lca.yaml` and **not linked** (never map to a guess; library
ADR 0039, in review, would allow proxies with library inputs, and this entry does not depend on
it):
- magnesium: the primary metal by the silicothermic (Pidgeon) process, a background-database
  ingot plus turning, as methylmagnesium-bromide-1;
- tert-butyl chloride: made from tert-butyl alcohol and hydrogen chloride (SRC-9); the proxy is
  the stoichiometric inputs of tert-butanol-1 and hydrogen-chloride-1, 0.801 kg and 0.394 kg per
  kg (C4H9OH + HCl -> C4H9Cl + H2O). A step of this entry from those two library products was
  considered and not built: the conversion of a tertiary alcohol with hydrochloric acid is a
  continuous or separate batch operation with its own aqueous waste, and the chloride is a
  merchant chemical;
- dichlorodimethylsilane: the direct process, silicon with methyl chloride over copper (SRC-8);
  the proxy is the stoichiometric inputs, 0.218 kg of metallurgical silicon and 0.782 kg of
  chloromethane (chloromethane-1) per kg (Si + 2 CH3Cl -> Me2SiCl2), without the process's other
  silanes;
- n-hexane (a solvent cut of naphtha or natural-gas liquids) and sodium thiocyanate (from sodium
  cyanide and sulfur): no library producer, named as gaps.
Per batch and not in the flowsheet (library ADR 0035, core ADR 0053): nitrogen 168.3 kg (134.6
Nm3: inerting R-101, 18.9, and R-102, 24; pressing the slurry, 19; the two filtrations' push,
20; the dryer's bleed, 10, and vacuum break, 8; blanketing C-101 and the tanks, 15; the vent
header's purge at 2 Nm3/h over the 9.86 h cycle, 19.7; ASSUMED), leaving through the oxidiser;
sodium thiocyanate 4.14 kg (D-004), ending in the salt cake (not in the balance:
`cheme.lci-balance-unassessable`, info).
Wastes: the dried salt cake (0.779 kg/kg) to quench and hazardous-waste treatment; the still
residue (8.1 g/kg) and the solvent purge (0.141 kg/kg, D-014) to incineration with acid-gas
scrubbing; the vent gas (0.135 kg/kg) to the thermal oxidiser with an acid-gas scrubber.
Per kg of TBSCl: magnesium 0.215 kg, tert-butyl chloride 0.819 kg, dichlorodimethylsilane 0.873
kg, THF 0.122 kg, n-hexane 0.034 kg, nitrogen 0.233 kg, sodium thiocyanate 5.7 g, electricity
0.196 kWh, LP steam 0.236 kWh, MP steam 2.62 kWh, brine 1.21 kWh removed, tempered water 2.31 kWh,
cooling water 0.185 kWh. The stoichiometric floors are 0.614 kg of tert-butyl chloride, 0.161 kg
of magnesium and 0.856 kg of the silane per kg.
KPIs (`benchmarks/inorganic-chemicals.yaml`): tert-butyl chloride and dichlorodimethylsilane per
kg of TBSCl, both `no_open_reference`.

## D-013 Dedicated train (2026-11-12)
Decision: R-101, R-102, F-101 and C-101 with their exchangers and tanks make only TBSCl, batch
after batch: 803.3 batches in 7920 h on a dedicated train (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train cannot
be checked without the other products' campaigns. Silylating agents are often made on
multipurpose Grignard trains; this LCI is then a lower bound. Out of scope, so not LCI gaps: the
changeover cleaning between campaigns, the idle time of a multipurpose train, shared tank farms,
the oxidiser and the packing station.

## D-014 The solvent loop and its purge (2026-11-12)
Decision: the recovered cut (S22) and the dryer's condensate (S19) are mixed in T-301, cooled to
303 K in E-301, 2 % purged (SP301) and split (SP302): 14 % to the cake wash, 15 % to R-102's
heel and the rest to R-101's next charge. The loop is torn at S29 and converged by `cheme process
propagate` (Wegstein, core ADR 0060; 88 iterations, the tear's tolerance 1e-5 kg/h absolute and
1e-8 relative, far tighter than the balances' 0.05 kg/h, as the loop's gain is near 1).
What the loop carries (S29, year averages): 505.9 kg/h, THF 5.013, n-hexane 1.116, the silane
0.1956, TBSCl 0.1516 and the halide 0.0009 kmol/h. The THF and n-hexane make-ups (S2, S3) replace
what the purge, the vent, the dried salt and the product take, and so set the loop's size: about
5.7 mol of THF and 1.3 of n-hexane per mol of halide in R-101's charge (D-004). The silane feed is
set a little above what R-102 consumes and the purge, the cake and the vent take (63.88 kg/h
against SIL's 0.4898 kmol/h, 63.21 kg/h), so that R-102 ends with an excess: R-102's slurry holds
0.1732 kmol/h of silane against the 0.4898 kmol/h it consumed (35 %). A make-up that held a
charge ratio, or a silane feed that held R-102's excess, had to be set by hand (L-8).
The purge (S28, 10.32 kg/h, 0.141 kg/kg) takes the loop's light and heavy impurities (in reality
the siloxane, isobutene dissolved, thiocyanate-derived traces; none modelled) and 2 % of the
TBSCl and silane the loop carries. TBSCl in the loop (22.4 % of the still's, D-007) passes R-101
unchanged (a hindered chlorosilane, ASSUMED inert to the Grignard reagent) and returns to the
still.
Reason: THF and n-hexane cannot be parted by the batch still (D-004), and the silane boils with
them (342.5 K), so the three are recycled together; the purge keeps what does not leave
otherwise from building up.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101 with the vent's vapour and condenser: composition, accumulation, MTSR, peak cooling, off-gas | done in cheme, kinetics and heats ASSUMED | D-004, D-005, D-008, D-011 |
| semi-batch R-102 (reverse addition) | done in cheme, kinetics and heat ASSUMED | D-004, D-005, D-011 |
| magnesium as a solid reactant | done in cheme (pseudo-concentration) | D-005 |
| batch recipe, cycle time, basis check | done in cheme | D-003, `cheme process recipe` |
| vessel sizing, jacket checks, warm-up time | done in cheme, U and media ASSUMED | D-003, D-010 |
| filtration, wash, drying (F-101) | specified splits, Ruth time and dryer model in cheme, cake data ASSUMED | D-006 |
| batch rectification (C-101 with K-101) | done in cheme (shortcut column), ideal liquid, TBSCl's vapour pressure ASSUMED | D-007 |
| solvent recycle | converged in cheme at its tear | D-014 |
| flaking (E-102) | pass-through, duty by hand | D-007, D-009, L-7 |
| duties | Q1, Q2, Q3, Q5, Q6 in cheme; Q8 from core's dryer model; Q4 from the recipe's heat; the others (with the agitators' heat Q12, Q13) by hand | D-009 |
| per-batch exchanges (nitrogen, sodium thiocyanate) | done in cheme, amounts ASSUMED | D-012 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core limits hit (for core issues)

- L-1 (as methylmagnesium-bromide-1 L-1): **no induction period or initiation model.** A delayed
  initiation can only be shown by a rate that is slow for the whole batch (k/100 in D-011), and
  the dosing cannot be made conditional on the initiation.
- L-2: **a recipe unit procedure holds one batch or semi-batch step.** SRC-1 makes the Grignard
  reagent and silylates it in one flask; a vessel over two semi-batches (R101 then R102) is
  refused ("several batch or semibatch steps, name one as unit"), so neither its size nor its
  jacket can be checked for both. The entry uses two vessels (D-003), which the order of
  addition needs anyway (D-004). A unit procedure could size its vessel on the largest content
  of its steps and check its jacket against each step's peak.
- L-3 (as methylmagnesium-bromide-1 L-3): **propagate writes the vented components into the
  liquid outlet** at 0, so the liquid's template lists IB and IBA, and the still lists them as
  `nonvolatile` to ask no vapour pressure of them (ST101's comment).
- L-4 (as methylmagnesium-bromide-1 L-4): **a solid reactant works, as a pseudo-liquid**, with no
  surface-area rate.
- L-5: **no catalyst.** The thiocyanate's effect is only in SIL's ASSUMED rate constant, and a
  reaction that needs the catalyst is kept out of R101 by not listing it (ASSUMED, D-004, D-005). A
  catalyst component with an amount, an activity on a rate law and an addition time in the recipe
  would let the screening show what a late or forgotten catalyst does (the silane accumulates
  in R-102 and reacts when the catalyst comes).
- L-6: **the default MTT is the lowest normal boiling point of any component in the liquid**, here
  the dosed halide at 324.1 K, also when it is a trace (R102); the liquor boils at 340-343 K. A
  bubble-point MTT of the liquid at the worst moment (Raoult, as the vent's vapour already
  computes) would follow the accumulation instead of the component list (D-011).
- L-7: **no solidification model.** The flaker E102 is a pass-through and its duty (liquid
  cooling, fusion, solid cooling) hand arithmetic; core has no melting point, so it cannot warn
  that the product cut freezes on a condenser whose coolant is below 358 K (L-9).
- L-8 (as potassium-tert-butoxide-1 L-8): **no design specification on a recycle.** The silane
  feed that leaves R-102 a set excess, and the make-ups that hold a charge ratio, were set by hand
  (D-014); with the loop's gain near 1 the excess is sensitive to the feed's surplus.
- L-9 (as potassium-tert-butoxide-1 L-9): **no condenser is checked against the condensate's
  freezing point**: the still's condenser must switch to its hot supply for the TBSCl cut, and
  E-201's condensate holds TBSCl; both were checked by hand (D-007, D-009, the ideal solubility of
  TBSCl from its enthalpy of fusion: 53 mol% at 268 K against E-201's 4.4 mol%).
- L-10 (as methylmagnesium-bromide-1 L-10): **the dosing times are found by hand against the
  jackets**; the jacket check takes the wetted area at the charge, so R-102 needed a coil given as
  an area (D-010).
- L-11: **an isothermal semi-batch runs at its charge's temperature** unless its outlet's
  temperature is given: R102 runs at the 301.3 K its charge mixes to (D-005), which was kept; a
  warm-up of a charge that is not the batch's first step (R-102 before its dosing) has no model
  of its own apart from `batch.heat_up`, which nets the heating into the cooling duty.
- L-12 (as potassium-tert-butoxide-1 L-12): the agitators' power is not part of any model's energy
  balance: the reactors' agitator heat to brine is typed by hand as Q12 and Q13 (7.39 kW, 0.101
  kWh/kg, 8 % of the brine), the rest (R-101's inerting, charges and warm-up, R-102's inerting)
  excluded with its size (1.78 kW, D-009), so that both add up to P1 and P4.
- L-13 (library, not core): the taxonomy has no organosilicon or organometallics family;
  inorganic-chemicals is the nearest (coverage.yaml).
- L-14: **a semi-batch cannot name the dosed reactant whose accumulation it reports.** Core takes
  the first component, in the charge's order, that is dosed and a reactant. R-102's dose (the
  Grignard solution) carries recycled dichlorodimethylsilane, which the charge lists before the
  Grignard reagent, so the screening's accumulation of R102 (0.791 headline, 0.324 at the end of
  the dosing) is the excess silane's, not the Grignard reagent's (8.6 %); the MTSR, from the
  reactants left, is right. D-011 derives the Grignard reagent's from the silane balance and the
  MTSR. A `hazard.accumulation_of` (or `dosing.reactant`) would name it.
- L-15: **a unit procedure's `start` names only an operation's start, with no offset or end
  alignment.** R-102's dosing must run in R-101's transfer, so R-102 starts with R-101's dosing
  and waits 2.694 h, a hold set by hand from R101's times (D-003); a change of the kinetics needs
  the wait changed (a test checks the alignment). A start relative to an operation's end, or a
  dosing tied to another vessel's transfer, would follow the models.

## Open inputs
Calorimetry of both steps (heats, rates, the induction time, the side reaction's share, an
uncatalysed silylation in R-101, TD24 of
the reaction masses, the still residue and the wet salt); an activator for the initiation; the
reliefs of R-101 and R-102 for the boiling-solvent case and the dosing interlocks (D-011); the
brine's water path to the chlorosilanes and the scrubber's water (D-011); the quench drum's
inerting and hydrogen vent (D-006); the cake's resistance, liquor and drying rate (D-006); VLE
data of THF, n-hexane, the silane and TBSCl, and TBSCl's vapour pressure (D-007); the product
specification (D-002); a TEA (`operation.batch: {recipe: true}`).
