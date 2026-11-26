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

THIS STAGE (S5b, towards stage basic):
First bring seed train A on P-201 up to the S3 review (S3#1 N2 pressure limitation and relief of R-211A/R-212A, S3#2 aseptic sampling valves, S3#4 high-level protection, S3#5 steam block on the CIP inlet; S3#7 T-215 fill, vent and check valves) briefly, then draw P-205 (seed trains B and C as typicals of train A, a generator script) and P-204 (CIP station: caustic, acid if decided, water and recovered-rinse tanks, supply pumps, LP-steam heater, return pumps, conductivity and temperature on the return, supply and return headers to the fermentation area; SIP: filtered LP steam header and condensate). Render each sheet (cheme render --png, crops of dense parts) and LOOK at it before committing; keep the equipment, line and instrument lists in step (skill lists-sync); commit each sheet when it validates.

Already drawn (edit them only to fix findings, never draw them again): P-101, P-102, P-201, P-202, P-203, P-103, P-206, P-207
Not drawn yet: P-205 (missing), P-204 (missing), P-301 (missing), P-401 (missing), P-402 (missing), P-403 (missing)
Next sheet to draw: P-205
Failing gates up to stage basic: [basic] layout-3d: no layout/plant-model.yaml: run cheme layout build and commit it; layout/zones.yaml declares no zone; no review record of topic layout: render the plot plan and 2 sections (cheme layout render --png), look at them and record the layout review; [basic] lifting-study: no layout/plant-model.yaml: run cheme layout build and commit it; no layout/lifting-study.csv: run cheme layout lifting --write and commit it; [basic] mto: no layout/plant-model.yaml; run cheme layout build; [basic] layout-review: no review record for topic layout
cheme validate now: 0 error(s), 54 warning(s) (not on a P&ID, by sheet: P-202 9, P-204 19, P-205 12, P-301 21, P-401 16, P-402 14, P-403 38)

FIX FIRST (open findings of the previous independent review, most important first):
1) P-201 train A: close S3#1 (seed vessel relief vs N2 PV failure), S3#2 (aseptic sampling), S3#4 (fill high level), S3#5 (CIP inlet steam blocks), then draw P-205 trains B and C with the generator
2) Extend instrument list, special-items and cause-effect to R-201B to P (S5#1) and name PSE/PSV/PV in the typical note
3) T-201: vent, overflow, LAHH trip of P-202A/B in C&E, CIP connections (S5#2)
4) Draw P-204 CIP station and SIP steam with the CIP return pump location (S1#9) and steam quality (S1#10); route T-201 condensate to it (S5#6)
5) P-207 pump isolation, drains, PI and P-203A minimum flow (S5#3)
6) Sterile-boundary steam-block symbols on typical branches and header ends (S5#4, S5#5); P-206 title (S5#7)
7) XV-1025A double seat on P-103 (S2#1), slaker interlock (S2#2)
8) Layout gates: cheme layout build, zones, plan and sections, layout review (S8)
- open review finding 2026-11-25-S1-review#8 (low): 
- open review finding 2026-11-25-S1-review#9 (low): 
- open review finding 2026-11-25-S1-review#10 (low): 
- open review finding 2026-11-25-S2-review#1 (medium): 
- open review finding 2026-11-25-S2-review#2 (medium): 
- open review finding 2026-11-25-S2-review#3 (medium): 
- open review finding 2026-11-25-S2-review#6 (low): 
- open review finding 2026-11-25-S2-review#7 (low): 
- open review finding 2026-11-25-S2-review#8 (low): 
- open review finding 2026-11-26-S3-review#1 (medium): 
- open review finding 2026-11-26-S3-review#2 (medium): 
- open review finding 2026-11-26-S3-review#4 (medium): 
- open review finding 2026-11-26-S3-review#5 (medium): 
- open review finding 2026-11-26-S3-review#7 (low): 
- open review finding 2026-11-26-S3-review#8 (low): 
- open review finding 2026-11-26-S3-review#9 (low): 
- open review finding 2026-11-26-S3-review#10 (low): 
- open review finding 2026-11-26-S4-review#9 (low): 
- open review finding 2026-11-26-S5-review#1 (medium): The typicals are listed as equipment and lines (195 branch lines), but not as instruments, relief devices or trips. The instrument list has only R-201A's loops (TIC/AIC/LIC/PIC-20xxA). `special-items.yaml` has only PSE-2045A and PSV-2046A, and C&E I-201 to I-204 only R-201A. The sheet note names the instruments and trips "as R-201A" but not the rupture disc, the vacuum relief or the vent control valve PV-2041x. On the sheets the vent goes from F-201x straight to "atm". 15 x 2 relief devices and about 15 x 6 loops are therefore in no list. An I/O count, a relief register or a HAZOP built from the lists would miss them.
- open review finding 2026-11-26-S5-review#2 (medium): T-201 (2500 m3, design 0.05 barg) has no vent or breather, no overflow, no vacuum or overpressure protection and no high level. P-202A/B fill it at 280 m3/h, and nothing stops them at high level. The tank is also not connected to CIP or SIP, although it holds the live broth upstream of the centrifuges. D-035 leaves only the CIP and the overflow open; the vent is not mentioned.
- open review finding 2026-11-26-S5-review#3 (low): P-202A/B and P-203A/B have check valves only: no suction or discharge block valves, no casing drains, no pressure gauges. A spare cannot be isolated for maintenance. P-203A runs at variable speed on LIC-2051 with no minimum-flow protection or recycle.
- open review finding 2026-11-26-S5-review#4 (low): Each sterile branch (SM, IN, CS, ML) is drawn as one valve; the note says it stands for R-201A's double block and bleed with steam. The sterile boundary is what a bioprocess audience looks for, and on the typicals it shows only in a footnote.
- open review finding 2026-11-26-S5-review#5 (low): The sterile headers 100-IN-2004 and 200-SM-2001 and the CIP header 100-CS-2015 end in a single valve to "drain". During SIP of a sterile header the low point needs a steam trap or a steam-blocked bleed, as on 150-SS-2019. A single valve is also a sterile-boundary break.
- open review finding 2026-11-26-S5-review#6 (low): Condensate 25-CD-2055 goes through the trap to "drain", not to condensate return. TV-2052 is printed but not listed, as D-035 says.
- open review finding 2026-11-26-S5-review#7 (low): The title "Fermenters R-201J to P, headers" reaches the right frame line of the title cell in the render; validate reports 0 `title-text-overflow`.
- open review finding 2026-11-26-S5-review#8 (low): Pumps P-201x, P-202A/B and P-203A/B share their numbers with the drawings P-201, P-202 and P-203. "P-202A (P-207)" or "P-203A/B on P-207" reads ambiguously in notes and on slides.

Rules: you have a hard API budget of USD 10 for this session, so work efficiently (plan,
then batch edits; do not re-read huge files; use cheme show and grep). Stay on the current
branch stage/basic-lactic-acid-fermentation (do not create or switch branches; never push).
The branch starts at c49d86cd (origin/main): use `cheme diff c49d86cd --list` for the branch's
changes (the local `main` is stale). Commit in logical commits BEFORE the budget runs out (at
least once midway; `git add` the files you changed by name). Append to PROGRESS.md. Keep cheme validate free of errors at every commit. Do not
review or sign off your own work: an independent reviewer follows. Never bypass a git hook
(no `--no-verify`, no `-c core.hooksPath=...`): when a hook fails, fix what it reports, or stop
and say so in the summary. End with a short summary of
what you did, what is left and whether a merge is pending.
