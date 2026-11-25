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

THIS STAGE (S2, towards stage basic):
Draw P-101 (medium preparation and continuous sterilisation: syrup and CSL tanks, V-101, E-101 as regenerative exchanger, steam heater, holding tube, back-pressure valve, divert to V-101 on low holding temperature, sterile medium header to the seed train and the fermenters) and then P-102 (quicklime silo and feeder, slaker R-101 with its cooling, milk-of-lime tank and the circulating ring main with its pumps to the seed and production fermenters). Render each sheet (cheme render --png, crops of dense parts) and LOOK at it before committing; keep the equipment, line and instrument lists in step (skill lists-sync); commit each sheet when it validates.

Not drawn yet: P-101 (missing), P-102 (missing), P-201 (missing), P-202 (missing), P-203 (missing), P-204 (missing), P-301 (missing), P-401 (missing), P-402 (missing), P-403 (missing)
Next sheet to draw: P-101
Failing gates up to stage basic: [basic] pids-exist: nothing matches pid/*.xml; [basic] layout-3d: no layout/plant-model.yaml: run cheme layout build and commit it; layout/zones.yaml declares no zone; no review record of topic layout: render the plot plan and 2 sections (cheme layout render --png), look at them and record the layout review; [basic] lifting-study: no layout/plant-model.yaml: run cheme layout build and commit it; no layout/lifting-study.csv: run cheme layout lifting --write and commit it; [basic] mto: no layout/plant-model.yaml; run cheme layout build; [basic] layout-review: no review record for topic layout
cheme validate now: 0 error(s), 2 warning(s)

FIX FIRST (open findings of the previous independent review, most important first):
1) Close #1 before merge: a sterile-side booster pump and an E-101 differential-pressure divert in D-015, the equipment list and P-101
2) Write the timed fermenter turnaround with SIP (#3), and the seed transfer hydraulics against R-213's design pressure (#2)
3) Size the vacuum protection on uncontrolled steam collapse, with N2 permissives and vent-filter CIP isolation (#4), before drawing P-202
4) Move steriliser standby and divert water off V-101 and account for the standby steam (#5) before drawing P-101
5) Decide the CIP return arrangement (#9) and the SIP steam quality (#10) before P-204; then the low findings #6 to #8
- open review finding 2026-11-25-S1-review#1 (high): D-015 says the back-pressure valve after E-103 keeps the sterile side of the regenerator above the raw side. In series it cannot: the raw side of E-101 is upstream of E-102 and X-101, so it carries their pressure drop plus the holding pressure, while the sterile side is downstream of X-101. A plate leak then goes from raw to sterile, so unsterilised medium contaminates the sterile header.
- open review finding 2026-11-25-S1-review#2 (medium): D-013 transfers the stage-5 inoculum by N2 pressure: 72 m3 in about 1 h at 2.5 m/s, through about 250 m of DN 100 (validate estimate) to the R-201 inlets on the 23.8 m vessels. Friction is about 1.3 to 1.7 bar (Darcy f about 0.016, fittings, ASSUMED), the lift about 2 bar, and the headspace 0.3 barg. That is about 3.6 to 4 bar over the R-213 headspace, against its 3.0 barg design.
- open review finding 2026-11-25-S1-review#3 (medium): D-003 splits the 12 h turnaround into fill 4 h, harvest 4 h and CIP 4 h. SIP is not budgeted: heating about 100 t of steel by 71 K (about 3.6 GJ, about 1.6 h at the 3 t/h of LP steam of D-019, ASSUMED), 30 min at 121 C (D-021) and a cool-down of at least 60 min (D-019) add about 3 h. With pre-rinse, caustic, rinse and final rinse (about 1.5 to 2 h), cleaning and SIP do not fit in 4 h.
- open review finding 2026-11-25-S1-review#4 (medium): D-019 sizes the gas inlet and vacuum protection on a controlled cool-down of at least 60 min. The governing vacuum case for a steamed 1291 m3 vessel is uncontrolled steam collapse: the coil cooling valve open, cold medium or CIP water entering a hot vessel, or rain on an outdoor shell. The relief path through F-202A also adds the cartridge pressure drop. The hydrophobic vent filter F-201A also has no stated protection against wetting during CIP.
- open review finding 2026-11-25-S1-review#5 (medium): D-014 keeps the steriliser hot between campaigns on water "circulating back to V-101". The divert and the 30 min re-sterilisation also return to V-101. Water put into V-101 dilutes the next batch's medium and moves the titer specification (D-002). The standby steam, about 6 h of every 9.88 h, is not in Q17 or the LCI.
- open review finding 2026-11-25-S1-review#6 (low): The campaign arithmetic of D-014 (761 t in 4 h, 190 t/h on a 200 t/h design) does not show what happens when a stage-5 seed fill (about 65 m3 in 1 h, D-013) falls inside a production fill: either 255 t/h, or a production fill cut back for that hour. "About 107 m3 at 72 % fill" for R-213 is 67 %. The seed medium is the full-strength production medium (about 240 g/L sugar) without dilution, and that is not stated as a decision or as ASSUMED.
- open review finding 2026-11-25-S1-review#7 (low): The tempered-water loop of D-017 only cools, by cooling-water injection. The fermenters stand outdoors (D-026), and the lag phase, a cold start or winter conditions need heat into a 323 K broth.
- open review finding 2026-11-25-S1-review#8 (low): D-018 keeps the ring-main return above 1.4 m/s with 80 m3/h against 35 m3/h of draws. 35 m3/h is the average. With 15 fermenting vessels at a 3.5 m3/h peak, simultaneous draws reach about 52 m3/h, and the return falls to about 1 m/s in DN 100.
- open review finding 2026-11-25-S1-review#9 (low): The CIP return pumps stand in B-201, about 117 m along the racks from the fermenter bottoms (validate estimate), on a sloped DN 150 return. Self-priming pumps at the end of such a run are unlikely to hold the return, so the vessel bottom floods and the clean fails.
- open review finding 2026-11-25-S1-review#10 (low): D-021 uses filtered plant steam for SIP of medium-contact surfaces. The product grade (food or technical 88 wt% lactic acid) is not stated, nor the boiler-treatment chemicals that this steam carries into the broth.

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
