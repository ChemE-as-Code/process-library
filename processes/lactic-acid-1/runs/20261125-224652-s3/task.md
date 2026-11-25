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

THIS STAGE (S3, towards stage basic):
Draw P-201, the seed train (plant stages 3 to 5 of every train as decided in DESIGN.md, the lab stages 1 and 2 as a note; each seed fermenter agitated and jacketed with temperature, pH, level and pressure, sterile vent filter, steam blocks on the medium, base and transfer connections, CIP and SIP connections, sterile transfer to the next stage and to the production fermenter inoculum header). The sheet is A3: draw train A in full and readable; if three trains do not fit legibly, put trains B and C as typicals of train A on a further sheet (e.g. P-205, plant.yaml and lists updated, D-028's sheet-split record extended). Use a generator script or cheme copy for the repeated trains. Do the FIX FIRST items marked 'before P-201' and the quick P-102/P-103 fixes first, briefly. Render each sheet (cheme render --png, crops of dense parts) and LOOK at it before committing; keep the equipment, line and instrument lists in step (skill lists-sync); commit each sheet when it validates.

Already drawn (edit them only to fix findings, never draw them again): P-101, P-102, P-103
Not drawn yet: P-201 (missing), P-202 (missing), P-203 (missing), P-204 (missing), P-301 (missing), P-401 (missing), P-402 (missing), P-403 (missing)
Next sheet to draw: P-201
Failing gates up to stage basic: [concept] layout-plot-plan: 2 equipment-list items not placed: P-108A, P-108B (layout/equipment-placement.yaml); [basic] drawing-clean: 2 cheme.line-crossing, 1 cheme.line-through-label, 2 cheme.offpage-not-on-edge not accepted; first: pid/P-103.xml#line-crossing:Line_P108A_DB_S2_P1+Inst_US1025_Signal; 5 warning(s); run `cheme validate --fail-on info` (fix, or accept with a reason under accept:); [basic] layout-3d: no layout/plant-model.yaml: run cheme layout build and commit it; layout/zones.yaml declares no zone; no review record of topic layout: render the plot plan and 2 sections (cheme layout render --png), look at them and record the layout review; [basic] lifting-study: no layout/plant-model.yaml: run cheme layout build and commit it; no layout/lifting-study.csv: run cheme layout lifting --write and commit it; [basic] mto: no layout/plant-model.yaml; run cheme layout build; [basic] layout-review: no review record for topic layout
cheme validate now: 0 error(s), 11 warning(s) (not on a P&ID, by sheet: P-201 35, P-202 37, P-203 90, P-204 22, P-301 21, P-401 16, P-402 14, P-403 38)

FIX FIRST (open findings of the previous independent review, most important first):
1) Add a double block and bleed with steam barrier at the steriliser forward valve XV-1025A (S2#1) and reuse the pattern for the fermenter steam blocks on P-202
2) Add the slaker interlocks to cause-effect and the trip instruments to P-102 (S2#2); add C&E entries for the P-202 switches TSHH-2012A, FSLL-2014A, LSHH-2032A, PALL-2041A
3) Place P-108A/B in the layout to restore the layout-plot-plan gate (S2#5)
4) Clear or accept the five P-103 drawing warnings so drawing-clean passes (S2#4), and draw the PDT-1028 second tap and the PIC-1029 signal (S2#6, S2#7)
5) Tag and draw the R-101 and T-105 agitators (S2#3)
6) Before P-202: close S1#3 (SIP in the 12 h turnaround), S1#4 (governing vacuum case), S1#7 (loop heating) and decide the lime dosing sterile boundary (S2#9) and the ring-main peak draws (S1#8)
7) Before P-201: close S1#2 (seed transfer hydraulics) and S1#6 (campaign timeline with seed fills)
- open review finding 2026-11-25-S1-review#2 (medium): Seed transfer hydraulics against R-213 design pressure
- open review finding 2026-11-25-S1-review#3 (medium): SIP not budgeted in the 12 h turnaround
- open review finding 2026-11-25-S1-review#4 (medium): Governing vacuum case, F-201A wetting in CIP
- open review finding 2026-11-25-S1-review#6 (low): Campaign timeline with seed fills; R-213 fill figure; seed medium strength
- open review finding 2026-11-25-S1-review#7 (low): Tempered-water loop cools only
- open review finding 2026-11-25-S1-review#8 (low): Ring-main return velocity at peak draws
- open review finding 2026-11-25-S1-review#9 (low): CIP return pumps far from the fermenters
- open review finding 2026-11-25-S1-review#10 (low): SIP steam quality and product grade
- open review finding 2026-11-25-S2-review#1 (medium): The sterile boundary toward the header is a single on/off valve, XV-1025A, as drawn. During a divert, and during the 30 min water re-sterilisation to wastewater, the steriliser side is non-sterile. Only one closed seat stands between it and the sterile header 200-SM-2001, which feeds fermenters and seed vessels that may be filling. The spec asks for steam blocks as the sterile boundary.
- open review finding 2026-11-25-S2-review#2 (medium): The slaker has no interlock. Quicklime slaking is strongly exothermic (820 kW). Lime feed with lost slaking water, lost coil cooling or high R-101 temperature can boil the slaker and plug it with hard grit. TIC-1033 is a control loop, not a safeguard.
- open review finding 2026-11-25-S2-review#3 (medium): No agitator is drawn or tagged on R-101 ("agitated" in a note) or on T-105 ("agitated" in the list service). In the crop, both are plain vessels. 20 wt% milk of lime settles in minutes without agitation, and the equipment list carries no motor power for these drives.
- open review finding 2026-11-25-S2-review#4 (medium): The basic gate drawing-clean fails on P-103: the booster discharge 200-SM-1014 crosses two signal lines, the PIC-1029 measuring line runs through the label "200-SM-1006", and the E-103 CW connectors (150-CW-1023/1024) sit 106 to 121 mm inside the bottom edge. D-028 explains them but does not accept them in checks/checks.yaml.
- open review finding 2026-11-25-S2-review#5 (medium): P-108A/B are new and not placed, so the layout-plot-plan gate, which passed at S1, now fails. The lines 200-SM-1006 and 200-SM-1014 go unrouted.
- open review finding 2026-11-25-S2-review#6 (low): PDT-1028 is drawn with one sensing line, to the sterile outlet of E-101 (200-SM-1015). The raw-inlet tap that its service and D-015 name is not drawn. The instrument list service cites "C&E I-101", but its interlock is I-103.
- open review finding 2026-11-25-S2-review#7 (low): D-015 and the list say PIC-1029 sets the booster speed. On the sheet PIC-1029 has a measuring line only, with no signal to the P-108A/B drives.
- open review finding 2026-11-25-S2-review#8 (low): The holding tube is drawn and listed as a vertical Vessel (dished heads). A bioprocess reader expects a rising pipe or serpentine with its length and volume.
- open review finding 2026-11-25-S2-review#9 (low): Milk of lime from the ring main is non-sterile (Open inputs, D-018) and is dosed into sterile broth. P-102 does not say where the sterile boundary on the dosing branch is.

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
