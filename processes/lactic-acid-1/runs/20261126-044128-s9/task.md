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

THIS STAGE (S9, towards stage basic):
Close-out under a hard time limit (the session is stopped after about 50 minutes; commit after each step). In this order: (0) draw XV-3013 on P-301 (S6#1 reopened, high; quick) and commit; (1) draw P-404 (product concentrator E-404A/B, product cooler E-405, product tanks T-401A/B and pumps, ethanol make-up tank T-402 with the make-up ratio control and LSHH overfill trips; consistent with P-403's off-page connectors; render and look at it) and commit; (2) run cheme layout build once so layout/plant-model.yaml is current with P-404, then cheme assess mto --write and cheme layout lifting --write, and commit; (3) update README.md (stage basic in progress, the sheet list, what the fermentation area shows) and PROGRESS.md, and add to DESIGN.md a short 'Basic-engineering status' section: each basic gate, ok or failing and why, and the open review findings by area; commit. (4) only if budget is left: record the S8 layout review's fermenter-deck findings (S8#1 to S8#3) as open in DESIGN.md with the intended fix, and the quick fermentation-area findings (S5#2 T-201 vent/overflow/LAHH, S5#1 lists for the typicals). No HAZOP in this session. Do not sign off.

Already drawn (edit them only to fix findings, never draw them again): P-101, P-102, P-201, P-205, P-208, P-202, P-203, P-204, P-301, P-401, P-402, P-403, P-103, P-206, P-207
Not drawn yet: P-404 (empty)
Next sheet to draw: P-404
Failing gates up to stage basic: [basic] drawing-clean: 1 cheme.line-crossing not accepted; first: pid/P-403.xml#line-crossing:Line_65ET4505_S2_P2+Line_80RV4406_S1_P2; 1 warning(s); run `cheme validate --fail-on info` (fix, or accept with a reason under accept:); [basic] design-review: reviews/2026-11-26-S7b-review.md: changed since 5fee05d301f5: DESIGN.md, checks/checks.yaml, equipment/equipment-list.yaml, plant.yaml | reviews/2026-11-26-S6-review.md: changed since 27564b21b787: DESIGN.md, checks/checks.yaml, control/instrument-list.yaml, equipment/equipment-list.yaml, pid/P-301.xml, pid/P-401.xml and 1 more | reviews/2026-11-26-S5b-review.md: changed since 4f9b80d3d977: DESIGN.md, checks/checks.yaml, control/cause-effect.yaml, control/instrument-list.yaml, equipment/equipment-list.yaml, pid/P-204.xml and 4 more (and 6 more record(s)); [basic] layout-3d: 200 cheme.layout-clash-pipe, 63 cheme.layout-clash-pipe-equipment, 15 cheme.layout-clash-pipe-steel, 158 cheme.layout-headroom not accepted; first: layout/plant-model.yaml#layout-clash-pipe:P-101/Line_150PM1008_S1+P-101/Line_50PM1010_S1; fix them (via points, pins, moves) or accept them with a reason; [basic] lifting-study: 3 lifting findings: S-301A, S-301B, S-301C not accepted; see cheme layout lifting: a crane pad within reach, a clear lane, a laydown and a crane chart that carries the lift, or accept with the lifting plan's reason
cheme validate now: 0 error(s), 1267 warning(s) (not on a P&ID, by sheet: P-201 3, P-202 9, P-205 3, P-208 3, P-301 1, P-404 18)

FIX FIRST (open findings of the previous independent review, most important first):
1) Draw XV-3013 on P-301 (S6-review#1 reopened, high).
2) Fermenter branch access and clashes (S8#1): branch valves at the deck or a rack walkway, one riser lane per service per fermenter, no VP platforms, no clashes in A-200.
3) Rework the top-deck concept: deck at head-tangent level, drives supported on the vessel or a stated decoupling (S8#2, S8#3), in D-043.
4) Add a middle stair per fermenter deck and declare escape zones (S8#4).
5) Accept the L-11 headroom artefacts by id; fix the R-5 road crossings and the T-201 drops (S8#5).
6) S9 close-out: draw P-404 (ethanol make-up ratio control and tank LSHH), fix the P-403 crossing (drawing-clean), the PSV readability and RV sizing (S7b#1), R-402 pressure (S7b#2), R-401 (S7b#4), the fermenter typicals and T-201 protection (S5#1, #2), the CIP divert and permissives (S5b#2, #3), XV-1025A (S2#1) and the slaker interlock (S2#2).
7) Lifting: per-bay crane pads, the drive lift weight, a centrifuge removal lane (S8#6).
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
- open review finding 2026-11-26-S5b-review#10 (low): 
- open review finding 2026-11-26-S6-review#1 (high): 
- open review finding 2026-11-26-S6-review#3 (medium): 
- open review finding 2026-11-26-S6-review#5 (medium): 
- open review finding 2026-11-26-S6-review#7 (low): 
- open review finding 2026-11-26-S6-review#8 (low): 
- open review finding 2026-11-26-S6-review#9 (low): 
- open review finding 2026-11-26-S7b-review#1 (medium): 
- open review finding 2026-11-26-S7b-review#2 (medium): 
- open review finding 2026-11-26-S7b-review#3 (medium): 
- open review finding 2026-11-26-S7b-review#4 (medium): 
- open review finding 2026-11-26-S7b-review#5 (low): 
- open review finding 2026-11-26-S7b-review#6 (low): 
- open review finding 2026-11-26-S7b-review#7 (low): 
- open review finding 2026-11-26-S8-review#1 (high): The stage task asked for clean, readable rows, top structure and rack. The model has 201 or more pipe clashes, mostly the fermenter branches (D-043), plus 63 pipe-through-equipment and 15 pipe-through-steel. It also generates 216 one-valve access platforms, many at 21.78 m with their own stairs from grade, in the shell-to-rack strip (seen in the x = 159 section). In the model, the header branch valves sit on the risers, where nobody can reach them from the deck or the rack.
- open review finding 2026-11-26-S8-review#2 (medium): D-043 puts the 12 t drives on bridges of the independent top frame, with the shaft through the head nozzle. The vessel and the frame then move apart vertically. One part is the SIP thermal growth of a 24 m SS304 shell: about 17e-6/K x 24 m x 100 K, roughly 40 mm (ASSUMED temperatures). The others are hydrostatic stretch and foundation settlement under about 1100 t operating. The double mechanical seal at the sterile boundary and the shaft alignment are fixed to the vessel and cannot follow that. The rejected alternative ("12 t head reinforcement per vessel") is not quantified.
- open review finding 2026-11-26-S8-review#3 (medium): The deck TD is at 24.5 m, 0.7 m above the head top at 23.8 m. A 2:1 ellipsoidal head on 9 m is 2.25 m deep, so the top-head nozzles stand between about 21.6 and 23.8 m. Their valves sit 0.7 to 2.9 m below the grating: vent and filters, PSV, SIP and steam-block valves, medium and inoculum inlets, spray devices. D-043 says the top-head valves are "worked from the deck". That is not possible from there, and the model answers it with the 21.78 m valve platforms (#1).
- open review finding 2026-11-26-S8-review#4 (medium): Each deck has two stairs, at the row ends only (offsets 0.5 and 107.5 m, both on the outer side). From mid-deck that is about 55 m of travel at 24.5 m, on a deck used for drive and seal work during or after SIP. Usual practice is a stair within about 25 to 45 m (ASSUMED, site standard to confirm). 25 layout-escape-ways findings remain. The stage task asked for escape zones, but zones.yaml declares none.
- open review finding 2026-11-26-S8-review#5 (medium): There are 158 headroom findings. Most come from the whole-floor platform levels in B-201 (L-11), so the model cannot show whether the seed building works. The real findings sit among them and are not separated: drops over T-201's roof platform, and pipes crossing road R-5 at 5.9 m (below the usual 6 to 7 m road clearance, ASSUMED).
- open review finding 2026-11-26-S8-review#6 (low): D-043 relies on mobile-crane lifts of the drives, seals and filters from CP-201/CP-202 to the 24.5 m deck, but A-201A to P are not in the study (lift_weight 3 t is below heavy_lift_t 5 t). The heaviest drive piece (gearbox, 12 t drive in total) is not stated. The radii are measured from the centres of 110 m long pads: up to 55 m against reach_m 40. S-301A to C are blocked by their own lines, so the lifting-study gate fails on them.
- open review finding 2026-11-26-S8-review#7 (low): P-404 is "drafted" with no content, to get past the build (L-10). `cheme status` now reports it as empty with 18 items not drawn. That is honest, but the sheet status overstates it.
- open review finding 2026-11-26-S8-review#8 (low): validate shows 1266 warnings, 318 of them line-crossing. The S7b record had 209 warnings in total, and S8 changed no P&ID content. Neither DESIGN.md nor PROGRESS.md explains where the extra line-crossing warnings come from (layout routes or sheets).

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
