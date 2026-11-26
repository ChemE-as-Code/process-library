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

THIS STAGE (S8, towards stage basic):
3D layout for gate layout-3d (skills layout-yaml, structures-access, pipe-routing, area-classification): building.yaml and structures.yaml (production fermenters in two rows with the top access structure and the rack between them, or a fermentation hall, as DESIGN.md decides; the clad seed/media/CIP building; downstream structures for columns and evaporators; tank farm), equipment-placement.yaml updated (every item placed, elevated items mounted on levels, sensible spacing for maintenance and the separations), piping/routing.yaml with racks and tiers, zones.yaml (ethanol and solvent areas, keep-clear, laydown, escape), then cheme layout build, cheme layout route / report; fix clashes and headroom findings or accept them with a reason in checks/checks.yaml; render the plot plan and at least two sections (one through the fermenter rows) with cheme layout render --png and LOOK at them; run cheme layout lifting --write and cheme assess mto --write; commit layout/plant-model.yaml. Record the layout decisions in DESIGN.md. This stage is layout only: of the FIX FIRST list do only layout items (unplaced items such as A-301 and the items added since S1, racks for long lines); leave the P&ID and list findings to the close-out stage S9. P-404 is still planned (drawn in S9): place its items anyway. The 16 production fermenters (about 9 m diameter, 23.8 m high) dominate the plot: make their rows, the top access structure and the rack between them clean and readable in 3D. Commit layout/plant-model.yaml at the end even if some findings remain, and list the remaining layout findings in DESIGN.md.

Already drawn (edit them only to fix findings, never draw them again): P-101, P-102, P-201, P-205, P-208, P-202, P-203, P-204, P-301, P-401, P-402, P-403, P-103, P-206, P-207
Not drawn yet: P-404 (missing)
Next sheet to draw: P-404
Failing gates up to stage basic: [concept] layout-plot-plan: 13 equipment-list items not placed: F-241B, F-242B, F-243B and 10 more (layout/equipment-placement.yaml); [basic] drawing-clean: 1 cheme.line-crossing not accepted; first: pid/P-403.xml#line-crossing:Line_65ET4505_S2_P2+Line_80RV4406_S1_P2; 1 warning(s); run `cheme validate --fail-on info` (fix, or accept with a reason under accept:); [basic] layout-3d: no layout/plant-model.yaml: run cheme layout build and commit it; layout/zones.yaml declares no zone; no review record of topic layout: render the plot plan and 2 sections (cheme layout render --png), look at them and record the layout review; [basic] lifting-study: no layout/plant-model.yaml: run cheme layout build and commit it; no layout/lifting-study.csv: run cheme layout lifting --write and commit it; [basic] mto: no layout/plant-model.yaml; run cheme layout build; [basic] layout-review: no review record for topic layout
cheme validate now: 0 error(s), 210 warning(s) (not on a P&ID, by sheet: P-201 3, P-202 9, P-205 3, P-208 3, P-301 1, P-404 18)

FIX FIRST (open findings of the previous independent review, most important first):
1) Make drawing-clean pass: accept or reroute the P-403 crossing 80-RV-4406/65-ET-4505 in checks.yaml, and resolve the 20 pump line-through-symbol warnings (S7b#3)
2) Draw P-404 with the ethanol make-up ratio FIC-4701 and LSHH overfill trips on T-401A/B and T-402 (S7b#7)
3) Tag the PSVs on P-402/P-403, label their vent-header off-pages, size or TBD the RV lines, and decide a reboiler steam trip on high column pressure (S7b#1)
4) R-402 pressure control, vent or blanket, TI in the vessel, and operating pressure in D-042 (S7b#2)
5) Resolve R-401's conversion basis against what is drawn: reboiler/overhead, or an equilibrium-limited pre-reactor (S7b#4, D-041/D-008)
6) Fermentation-area medium carry-overs before the presentation: S5#1 typicals' instruments/relief/trips, S5#2 T-201 protection, S5b#2/#3 CIP divert and permissives, S2#1 double seat at the sterile boundary, S2#2 slaker interlock
7) Downstream mediums deferred to S9: S6#3 centrifuge margin, S6#5 E-401A steam-chest relief and NC vents
8) Layout stage: place the 13 unplaced items and build the plant model
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
- open review finding 2026-11-26-S5b-review#2 (medium): 
- open review finding 2026-11-26-S5b-review#3 (medium): 
- open review finding 2026-11-26-S5b-review#4 (medium): 
- open review finding 2026-11-26-S5b-review#5 (low): 
- open review finding 2026-11-26-S5b-review#6 (low): 
- open review finding 2026-11-26-S5b-review#7 (low): 
- open review finding 2026-11-26-S5b-review#8 (low): 
- open review finding 2026-11-26-S5b-review#9 (low): 
- open review finding 2026-11-26-S5b-review#10 (low): 
- open review finding 2026-11-26-S6-review#3 (medium): 
- open review finding 2026-11-26-S6-review#5 (medium): 
- open review finding 2026-11-26-S6-review#7 (low): 
- open review finding 2026-11-26-S6-review#8 (low): 
- open review finding 2026-11-26-S6-review#9 (low): 
- open review finding 2026-11-26-S6-review#10 (low): 
- open review finding 2026-11-26-S7b-review#1 (medium): All five PSVs (PSV-4105, -4206, -4309, -4406, -4509) are drawn as small check-valve triangles, and none prints a tag. The relief and vacuum-pump exhaust lines end in off-page arrows with no destination text (seen on both renders and the crop). Nobody reading the sheet can find a relief device. The relief lines are also too small. PSV-4309's named case is loss of cooling water with E-431 on 5.1 MW: about 6 kg/s of ethanol vapour at about 4.5 bar(a), roughly 0.9 m3/s, needs well over DN80 (80-RV-4309 would run at about 180 m/s). PSV-4509 (6.1 MW) is the same. Neither D-041 nor D-042 discusses a reboiler steam trip on high column pressure that would reduce the relief load.
- open review finding 2026-11-26-S7b-review#2 (medium): The flowsheet runs R-402 at 300 kPa(a) [A] and 363 K. The hydrolysate holds about 7 mol% ethanol, which boils near this temperature at 1 atm. The sheet shows no PI or PIC, no vent or blanket for filling and draining the 260 m3 vessel, and no TI in the vessel: TIC-4401 sits on E-441's outlet. The agitator is drawn inside the symbol with no motor tag. D-042 does not state the operating pressure.
- open review finding 2026-11-26-S7b-review#3 (medium): D-042 accepts the 80-RV-4406 / 65-ET-4505 crossing, but checks.yaml has no `accept:` entry, so the gate went from ok to fail. The 20 `line-through-symbol` warnings at P-403's pump nozzles also remain unexplained: at sheet scale the pumps read normally, so they look like a nozzle-position fault in the builder call.
- open review finding 2026-11-26-S7b-review#4 (medium): R-401 is a packed "reactive distillation" column with no reboiler, no condenser and no reflux. Its only heat is E-411 (Q6 214 kW, about 0.3 t/h of vaporisation). Esterification of lactic acid with ethanol is equilibrium-limited. Without stripping the water, a liquid-phase packed bed stays near equilibrium, not at the 98 % (ASSUMED) on the sheet note. As drawn, R-401 is a fixed-bed reactor, and the water removal the conversion depends on happens in C-401.
- open review finding 2026-11-26-S7b-review#5 (low): D-042 says the mixed hydrolysis feed (S25, 60 m3/h) is DN150 "in intent", but the sheet and the line list keep 80-PL-4401 at DN80 up to E-441 (about 3.3 m/s, dn-mismatch at E-441). The water recycle 100-PL-4402 joins a smaller line.
- open review finding 2026-11-26-S7b-review#6 (low): PIC-4201's bubble is touched by the line to PV-4201 at its right edge. "MPC" and "MP steam" crowd each other at the P-402 bottom edge. P-403's 150-PL-4403 label stands nearer the E-441 riser than C-402's bottoms line. The pumps have check valves but no isolation valves (as S5#3).
- open review finding 2026-11-26-S7b-review#7 (low): The ethanol make-up ratio controller and the overfill protection of T-401A/B and T-402 are deferred to P-404 (D-042). Until P-404 is drawn, the ethanol balance of the recycle loop has no drawn control.

Rules: you have a hard API budget of USD 13 for this session, so work efficiently (plan,
then batch edits; do not re-read huge files; use cheme show and grep). Stay on the current
branch stage/basic-lactic-acid-fermentation (do not create or switch branches; never push).
The branch starts at c49d86cd (origin/main): use `cheme diff c49d86cd --list` for the branch's
changes (the local `main` is stale). Commit in logical commits BEFORE the budget runs out (at
least once midway; `git add` the files you changed by name). Append to PROGRESS.md. Keep cheme validate free of errors at every commit. Do not
review or sign off your own work: an independent reviewer follows. Never bypass a git hook
(no `--no-verify`, no `-c core.hooksPath=...`): when a hook fails, fix what it reports, or stop
and say so in the summary. End with a short summary of
what you did, what is left and whether a merge is pending.
