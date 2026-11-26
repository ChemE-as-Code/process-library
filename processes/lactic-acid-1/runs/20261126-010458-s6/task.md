You are the process engineer for this plant repository. Work as AGENTS.md and the skills in
.claude/skills say (dexpi-xml, pid-draft, pid-edit, lists-sync, layout-yaml, pipe-routing,
structures-access, area-classification, review). Start with
`cheme status`; use cheme commands (validate, fmt, render --png --crop to LOOK at
drawings, show, copy, fragment, diff --list, check). Change files with Edit and Write only and
run one command per Bash call (AGENTS.md, "How to run commands").

PLANT SPECIFICATION
<!-- The plant specification for the agent run of 2026-11-25/26: lactic-acid-1 from concept to
basic engineering with the 3D layout, the fermentation area in detail. Every stage prompt
includes it. -->

# lactic-acid-1, basic engineering: a typical industrial bioprocess

The concept (PR #561, merged 2026-11-19) is the starting point: 100 000 t/a of lactic acid (as
100 %) in an 88 wt% solution, 8000 h/a; glucose syrup 70 wt% fermented batch-wise by lactic acid
bacteria at 323 K in **16 production fermenters** (about 1291 m3 each, 1033 m3 of broth at 80 %
fill), titer 130 g/L at 0.89 g/(L h), 146.07 h fermentation + 12 h turnaround, a harvest every
9.88 h; pH 5 to 6 held with milk of lime (20 wt%, slaked from quicklime in R-101); broth hold
tank T-201; cell mass centrifuge S-301; acidulation R-301 with 93 wt% sulfuric acid; gypsum belt
filter S-302; four-effect evaporator E-401; esterification with ethanol by reactive
distillation R-401, ester column C-401, ethanol column C-402, hydrolysis R-402, stripper C-403,
concentrator E-404, cooler E-405. Read README.md, DESIGN.md (D-001 to D-012, L-1 to L-8,
Open inputs), process/recipe.yaml, process/flowsheet.yaml (`cheme process streams --md`) and
equipment/equipment-list.yaml before changing anything. **Keep the concept's numbers** unless
a sourced reason changes one; record every change and every new decision in DESIGN.md as D-013
and onward (decision, reason, rejected alternatives, what is ASSUMED), and append PROGRESS.md.

The result is shown on 26 Nov 2026 to bioprocess engineers (industrial process development,
MSAT, fermentation companies, academic bioprocess groups). They will look hard at the
**fermentation area**. It must read like a typical industrial fermentation plant, drawn and
listed at basic-engineering level.

## Library rules (strict)
- Every number is sourced (DESIGN.md source register, SRC-n) or marked ASSUMED. No invented
  data. No web access in these sessions: what is not in the register is ASSUMED, and saying so
  is better than a fake source. Usual industry practice may be used as an ASSUMED engineering
  choice, stated as such.
- Never copy third-party drawings or text; draw everything ourselves (cheme).
- Edit with Edit/Write only, one command per Bash call, `cheme fmt` + `cheme validate` after
  every change, no errors at any commit, small described commits. Do not push, do not merge, do
  not sign off (`cheme check --write` is forbidden). Stay on the current branch
  `stage/basic-lactic-acid-fermentation` (do not create or switch branches).
- The process model (process/*.yaml, BFD, PFD) stays as solved unless a decision changes it;
  if it does, rebuild with `cheme process build` and propagate.

## Facts already sourced for the fermentation area (SRC-1, BioSTEAM lactic `_units.py`, read 2026-11-25)
- Seed train: `SeedTrain` costed as **5 stages, 2 trains**; seed turnaround 12 h ("the same as
  ref [1]", i.e. Humbird et al. 2011, NREL, not read here); seed productivity 0.95 x 0.89
  g/(L h); seed temperature 50 C; a `SeedHoldTank` after the seed train (tank, agitator, pump).
- `CoFermentation.inoculum_ratio = 0.07`: 7 % of the fermentation feed is split to the seed
  train (the inoculum is a side-draw of the same medium).
- Main fermentation `mode='batch'`; no air or oxygen input, no CO2 product in the reactions
  (lactic and acetic acid and cell mass only): the fermentation is **not aerated**.
Add these to the SRC-1 row of the source register (what was read, 2026-11-25).

## Fermentation area: what basic engineering must show (priority 1)
Make decisions D-013 onward for each point, with the arithmetic in DESIGN.md:
1. **Seed train.** SRC-1's 5 stages at about **1:10 per step** (ASSUMED ratio; consistent with
   the 7 % inoculum: about 72 m3 of seed into a 1033 m3 batch, then about 7, 0.7, 0.07 and
   0.007 m3). Stages 1 and 2 (flask, lab fermenter) in the microbiology lab, off-plot, named in
   a note; stages 3 to 5 are plant seed fermenters (about 1, 10 and 100 m3 vessels, ASSUMED).
   The number of trains follows from the schedule: a production fermenter must be inoculated
   every 9.88 h. SRC-1 sizes its seed batch on the main titer and productivity (about 154 h),
   which no seed schedule can follow; state that, and choose a seed growth time (ASSUMED,
   e.g. to late exponential phase) plus the 12 h turnaround, and from that the number of
   parallel trains (SRC-1 has 2; more if the cycle needs it). Give the seed train its own sterile
   medium (side-draw of the sterile medium header) and milk of lime or another base for pH, and
   a sterile transfer line to the production fermenters. Decide whether SRC-1's seed hold tank
   is needed (ASSUMED either way).
2. **Media preparation and continuous sterilisation.** Syrup and CSL receipt/day tanks, the
   medium tank V-101, the continuous steriliser E-101 drawn as its real parts: regenerative
   exchanger, steam heater, **holding tube**, final trim cooler if needed, back-pressure valve,
   and a **divert valve back to V-101 when the holding-tube temperature is low** (an interlock
   in control/cause-effect.yaml). Sterilising temperature and hold time ASSUMED (no source
   read). Resolve the flow mismatch: the flowsheet carries the year-average medium (about 77 t/h)
   but a fermenter fills in 4 h (recipe), so either E-101 runs at the fill rate in campaigns or a
   sterile medium buffer is added; decide and record.
3. **Production fermenters R-201A to R-201P** (16 tags in the equipment list, each placed in the
   layout). Draw **R-201A in full detail** as the typical one, and the other 15 on an overview
   sheet with the common headers and their branch valves ("instrumented as R-201A, typical").
   R-201A shows: top-entry agitator with motor (about 127 kW, D-012) and a sealed shaft
   (double mechanical seal with sterile barrier, ASSUMED); jacket or half-pipe coils on a
   tempered cooling-water circuit, **temperature loop** (TIC on the broth to the jacket
   valve), high temperature alarm and the open safeguard of D-012 (agitator trip on high
   temperature or lost cooling, in cause-effect); **pH loop** (two steam-sterilisable pH probes,
   AIC to the milk-of-lime dosing valve on a branch of a circulating **milk-of-lime ring main**,
   with a flush connection against plugging); **level** (radar, LT/LIC on filling, high-level
   trip of the fill valve); **headspace pressure** with a back-pressure control valve on the
   vent; the **vent through a steam-sterilisable sterile filter** (with condensate drain);
   relief device sized for the SIP steam case and **vacuum protection** for cooling after SIP
   (sterile gas admitted through the filter, and a vacuum relief); **no aeration train**: state
   on the sheet (note) and in DESIGN.md that the fermentation is anaerobic/microaerophilic; the
   headspace gets a low sterile-filtered nitrogen overlay at slight overpressure (ASSUMED,
   to keep the sterile boundary under positive pressure; no source read), or a plain sterile
   vent if you decide so; **aseptic sampling valve** (steam/condensate flushed); sterile
   medium inlet and inoculum inlet each with a **steam block** (double block and bleed with
   steam, the sterile boundary); bottom harvest valve to the harvest header; **CIP** supply to
   spray devices and CIP return; **SIP** steam inlets (headspace and bottom) with condensate
   traps at the low points. Mark the **sterile boundary** on the sheets (notes or spec breaks).
4. **CIP and SIP**: a CIP station (caustic, acid if decided, water and recovered-rinse tanks,
   supply pump, heater on LP steam, return pump; the concept's 20 t of rinse water and 50 kg of
   NaOH per fermenter cleaned stay, D-003) with supply and return headers to the fermenters,
   seed fermenters and transfer lines; SIP steam (filtered plant steam, ASSUMED) distribution
   with condensate. Concentrations, temperatures, times: ASSUMED, stated as such.
5. **Broth hold and harvest**: harvest header, harvest pumps, T-201 (agitated, kept at or above
   323 K, D-005), feed pumps to the centrifuges.
6. Lime: quicklime silo and feeder, slaker R-101, milk-of-lime tank and the ring main pumps.

## Downstream (priority 2), normal basic-engineering P&IDs
Cell removal S-301 (machines in parallel), acidulation R-301 with acid dosing and its cooling
(D-007: size on about 1.5 to 2 MW), gypsum belt filter S-302 with vacuum system and filtrate
receiver, evaporator E-401 (four effects, condenser, vacuum), esterification R-401 with C-401
(vacuum), C-402, R-402, C-403, E-404, E-405, product tank; reflux drums, reboilers, condensers
and pumps as basic engineering needs them; ethanol areas noted for area classification.

## Sheets (plant.yaml), tags and areas
Areas: 100 media and lime, 200 fermentation (seed, production, CIP/SIP, broth hold), 300 cell
removal, acidulation and gypsum, 400 evaporation and purification. Planned sheets:
P-101 medium preparation and continuous sterilisation; P-102 lime slaking and milk-of-lime ring
main; P-201 seed train; P-202 production fermenter R-201A (typical, detailed); P-203 fermenters
R-201B to P with headers, harvest and broth hold T-201; P-204 CIP station and SIP steam;
P-301 cell removal, acidulation and gypsum filtration; P-401 evaporation; P-402 esterification
and ester column; P-403 ethanol recovery, hydrolysis and product. A sheet may be merged or
split if the drawing needs it: change plant.yaml and the lists' `sheet:` together. Use a
generator script (`scripts/draft_<sheet>.py`, `cheme run`) where it helps (16 fermenters,
several seed trains), as processes/hda-1 and asu-1 do.

## Layout (priority 3, gate layout-3d)
A plot plan with areas, roads, racks and separations (gate layout-plot-plan); buildings and
structures: production fermenters in two rows outdoors on a foundation with a steel access
structure at their tops (agitator drives) and the rack between the rows, or in a fermentation
hall (decide and record); a clad seed/media/CIP building; downstream structures; tank farm
(syrup, CSL, acid, ethanol, product); lime silo and slaker; gypsum handling; control room and
substation. Every equipment-list item placed, elevated items mounted, process lines DN 25 and
above routed or skipped with a reason, zones (ethanol area classification), clashes resolved
or accepted with a reason, `cheme layout build` committed, plan and two sections rendered and
reviewed (layout review, topic layout).

## Control, instruments, safety (priority 4)
control/loops.yaml for the fermenter loops (temperature, pH, level, pressure), the
steriliser's temperature and divert, the seed fermenters, the ring main; instrument list in
step with the sheets; control/cause-effect.yaml with the trips (holding tube low temperature
divert, fermenter high temperature/lost cooling agitator trip, high level, CIP/SIP
permissives); a HAZOP study draft of the fermentation area (status proposed) if the stage
allows.

## Quality expected
Readable sheets (render and look at them), no line through labels, lists in step with the
sheets (`cheme validate` 0 errors, warnings explained), every gate of stage basic either ok or
failing for a stated reason.

THIS STAGE (S6, towards stage basic):
Draw P-301 (cell removal S-301 machines in parallel with their feed and cake handling, acidulation R-301 with the 93 wt% acid dosing on ratio/pH and its cooling sized on D-007, gypsum belt filter S-302 with vacuum system, filtrate receiver and pumps, gypsum cake discharge) and then P-401 (four-effect evaporator E-401 with effects, separators, condenser, vacuum system, condensate and pumps). Render each sheet (cheme render --png, crops of dense parts) and LOOK at it before committing; keep the equipment, line and instrument lists in step (skill lists-sync); commit each sheet when it validates. Of the FIX FIRST list do only item 0 (S5b#1: the SIP header set point below every vessel's design pressure, or per-vessel SIP pressure control, recorded in D-037) first; leave the other carry-over items to the close-out stage S9 and spend the rest of the budget on the two downstream sheets.

Already drawn (edit them only to fix findings, never draw them again): P-101, P-102, P-201, P-205, P-208, P-202, P-203, P-204, P-103, P-206, P-207
Not drawn yet: P-301 (missing), P-401 (missing), P-402 (missing), P-403 (missing)
Next sheet to draw: P-301
Failing gates up to stage basic: [concept] layout-plot-plan: 12 equipment-list items not placed: F-241B, F-242B, F-243B and 9 more (layout/equipment-placement.yaml); [basic] layout-3d: no layout/plant-model.yaml: run cheme layout build and commit it; layout/zones.yaml declares no zone; no review record of topic layout: render the plot plan and 2 sections (cheme layout render --png), look at them and record the layout review; [basic] lifting-study: no layout/plant-model.yaml: run cheme layout build and commit it; no layout/lifting-study.csv: run cheme layout lifting --write and commit it; [basic] mto: no layout/plant-model.yaml; run cheme layout build; [basic] layout-review: no review record for topic layout
cheme validate now: 0 error(s), 164 warning(s) (not on a P&ID, by sheet: P-201 3, P-202 9, P-205 3, P-208 3, P-301 21, P-401 16, P-402 14, P-403 38)

FIX FIRST (open findings of the previous independent review, most important first):
1) S5b#1: bring the SIP header set point below the vessel design pressures (or add per-vessel SIP control) and record it in D-037
2) S5b#2/#3: CIP return divert valves on conductivity, tank levels and pump trips, CIP/SIP permissives in C&E
3) S5-review#1: instruments, relief devices and trips for R-201B to P in the lists
4) S5-review#2: T-201 vent, overflow, high-level trip, CIP connections
5) S5b#4: settle the generator status of the seed sheets
6) S5b#5 to #8 and #10: DN, line endpoints, acceptances, label, condensate
7) Layout stage: plant-model build, zones, layout review; then P-301, P-401 to P-403
- open review finding 2026-11-25-S1-review#8 (low): 
- open review finding 2026-11-25-S2-review#1 (medium): 
- open review finding 2026-11-25-S2-review#2 (medium): 
- open review finding 2026-11-25-S2-review#3 (medium): 
- open review finding 2026-11-25-S2-review#6 (low): 
- open review finding 2026-11-25-S2-review#7 (low): 
- open review finding 2026-11-25-S2-review#8 (low): 
- open review finding 2026-11-26-S3-review#9 (low): 
- open review finding 2026-11-26-S3-review#10 (low): 
- open review finding 2026-11-26-S4-review#9 (low): 
- open review finding 2026-11-26-S4b-review#1 (low): 
- open review finding 2026-11-26-S5-review#1 (medium): 
- open review finding 2026-11-26-S5-review#2 (medium): 
- open review finding 2026-11-26-S5-review#3 (low): 
- open review finding 2026-11-26-S5-review#4 (low): 
- open review finding 2026-11-26-S5-review#5 (low): 
- open review finding 2026-11-26-S5-review#6 (low): 
- open review finding 2026-11-26-S5-review#7 (low): 
- open review finding 2026-11-26-S5-review#8 (low): 
- open review finding 2026-11-26-S5b-review#1 (high): PV-2205/PIC-2205 holds the SIP header 150-SS-2019 at 3 barg (D-037, line list). R-201A to P are designed for 2.5 barg with PSE-2045A set at 2.5 barg. R-211x/R-212x are designed for 3.0 barg with discs at 3.0 barg. The vessel SIP basis is 121 C at about 1.05 barg (D-016, D-021). No pressure or temperature control between the header and the vessel during SIP is drawn or described. The SIP inlets 100-SS-2020x and 80-SS-2021x come straight off the header. A normal SIP step can therefore bring a fermenter to the header pressure, above its design pressure and its disc set point. The relief capacity was checked for the full-open case (D-033/D-034), so the vessel is protected, but every such SIP would burst a disc and break the sterile boundary.
- open review finding 2026-11-26-S5b-review#2 (medium): AIT-2203 (conductivity) and TT-2204 are drawn on 150-CR-2017, but they act on nothing. The recovery header 100-CR-2226 goes to T-221, T-222 or T-224, or to the drain, with no actuated divert valves, no loop and no sequence. The phase separation of caustic, rinse and acid on conductivity is the central function of a recovery CIP station, and the bioprocess audience will look for it.
- open review finding 2026-11-26-S5b-review#3 (medium): T-221 to T-225 have no level measurement. P-221A/B and P-222A/B have no low-level or dry-run protection. The 50 wt% NaOH tanker fill of T-225 has no high level. P-223 fills T-221 and T-215 with nothing to stop it. The pumps have no block valves or drains. The CIP/SIP permissives that the specification asks for (for example: no CIP supply to a fermenter that is not empty and isolated, and no SIP before CIP) are not in control/cause-effect.yaml. D-037 lists these as left open.
- open review finding 2026-11-26-S5b-review#4 (medium): D-036 calls the three seed sheets hand-maintained and then says "changes go through the script and a redraw of all three". AGENTS.md says a hand-maintained sheet's script is provenance only and is never rerun. A sheet rebuilt from its script must be declared `generator: {script, frame}` so that `cheme regen` and `generated-sheet-drift` protect it.
- open review finding 2026-11-26-S5b-review#5 (low): The pipe Line_DIS_B_S1_P2 joins the P-221B outlet nozzle (DN100) to the discharge junction DIS_J (DN80).
- open review finding 2026-11-26-S5b-review#6 (low): The line list has 150-CR-2017 from R-201A and 150-SS-2019 to R-201P. On P-204 the return ends at P-222A/B and the SIP header starts at F-231A/B and PV-2205 (validate `line-endpoint-mismatch`).
- open review finding 2026-11-26-S5b-review#7 (low): There are 9 `label-tag-unknown` for PSE-2115x/2125x/2135x on P-201/P-205/P-208. These discs are listed in `special-items.yaml`; this is the same RuptureDisc limitation as PSE-2045A, which is accepted. The 8 `offpage-mismatch` of the P-201 and P-202 CIP and SIP branches to P-204 follow the pattern that D-035 accepted for P-203.
- open review finding 2026-11-26-S5b-review#8 (low): The text F-241x overlaps the F-242x housing (validate, and seen on the P-201 crop), so the two stacked vent filters read ambiguously.
- open review finding 2026-11-26-S5b-review#9 (low): The 50 wt% NaOH line from P-223 (CIP area) to T-215 runs 37 m, and no rack carries it (`layout-line-route`).
- open review finding 2026-11-26-S5b-review#10 (low): The E-221 condensate (about 3.4 t/h at 2.0 MW) and the SIP drip leg go to "condensate drain" / DRAIN. Dumping this much clean LP condensate is not usual, and D-009 counts no such loss.

Rules: you have a hard API budget of USD 9 for this session, so work efficiently (plan,
then batch edits; do not re-read huge files; use cheme show and grep). Stay on the current
branch stage/basic-lactic-acid-fermentation (do not create or switch branches; never push).
The branch starts at c49d86cd (origin/main): use `cheme diff c49d86cd --list` for the branch's
changes (the local `main` is stale). Commit in logical commits BEFORE the budget runs out (at
least once midway; `git add` the files you changed by name). Append to PROGRESS.md. Keep cheme validate free of errors at every commit. Do not
review or sign off your own work: an independent reviewer follows. Never bypass a git hook
(no `--no-verify`, no `-c core.hooksPath=...`): when a hook fails, fix what it reports, or stop
and say so in the summary. End with a short summary of
what you did, what is left and whether a merge is pending.
