You are the independent senior reviewer (process, safety, drawing, consistency) for stage
S4b of this plant repository. You did not do the work. Do not modify tracked files except
the review record named below; scratch files go in build/.

Specification:
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

Stage task:
Fix P-202 (R-201A, the typical fermenter and the lecture's showpiece) to the S4 review: carry-over items 0 to 5 (every valve tag printed, PCV-2042A as a self-acting regulator with its sensing line; A-201A drawn as a top-entry agitator with motor and seal barrier, using the catalogue shapes the dexpi-xml skill names, or a clear note-labelled symbol; the half-pipe coil/jacket the tempered-water loop connects to; I-204 completed; the relief load of PSE-2045A from the full-open SIP capacity or a restriction orifice, burst indication; TIC-2011A placed readably with labelled split-range outputs; PSV-2046A labelled; recipe vs the 12.5 h turnaround) and item 6 (explicit crossing ids on P-201). Render P-202 at --scale 2 and crops of the vessel, the left loop and the right loops, and LOOK at them: the sheet must be readable on a projected slide. Do not start P-203.

Stage result (Claude Code JSON, tail):
ed. **A merge is pending**: an independent reviewer still has to review the branch (`cheme diff c49d86cd --list`). I did not push, merge or sign anything off.\n\n**What changed on P-202** (recorded as D-033 in DESIGN.md, and in PROGRESS.md):\n- **S4#1, valve tags:** tag labels are now printed for XV-2033A/2034A, TV-2011A/B, PV-2041A, XV-2043A/2044A, AV-2021A and PSV-2046A. PCV-2042A is drawn as a field regulator with its impulse line taken downstream of the valve, and a \"self-acting\" note.\n- **S4#2, agitator:** A-201A is now a top-entry drive: motor (160 kW), gearbox, a shaft through the top head, and a double mechanical seal with a sterile barrier. To clear the head SIP line, the shaft is drawn 8 mm right of the vessel centre.\n- **S4#3, coils:** the half-pipe coils are outlined outside the straight shell, so the tempered-water lines now visibly connect to the coils, not the broth.\n- **S4#4, I-204:** the trip now also stops the loop pump P-201A and the CIP supply pumps P-221A/B. D-033 also states the loop condition during SIP: P-201A stopped, TV-2011A/B closed.\n- **S4#5, relief load:** I recalculated PSE-2045A for both SIP steam lines fully open from the 4.5 bar(a) header. That gives about 2.5 kg/s against about 6.7 kg/s choked capacity for the DN 150 disc, so DN 150 stays and no restriction orifice is needed. The pipe resistance (K = 10) and the disc coefficient (0.62) are ASSUMED. I added a burst indicator, XA-2045A, to the sheet and the instrument list.\n- **S4#6 and #7:** TIC-2011A is moved off the riser and its measuring line is straight. Its two outputs are labelled \"TV-2011A: 50-100 % (CW)\" and \"TV-2011B: 0-50 % (LP steam)\". PSV-2046A is labelled \"vacuum relief -0.2 barg\".\n- **S4#8, turnaround:** `process/recipe.yaml` now follows D-031's steps and still totals the 12 h, using two 0.25 h overlaps:\n  - the CIP pre-rinse starts during the harvest drain;\n  - the fill starts at the end of the SIP cool-down.\n\n  The 1.5 h inoculum transfer runs inside the fill. The 16 fermenters and the 9.88 h harvest interval are unchanged.\n- **S3#6:** the P-201 wildcard acceptances in `checks/checks.yaml` are replaced by 37 explicit ids. I also accepted the two P-202 crossings where the TIC outputs cross the riser, with a reason.\n\nI rendered the whole sheet at `--scale 2` and looked at crops of the vessel top, the left loop and the right loops; they read cleanly.\n\n**Still open:**\n- `cheme validate` still warns that TV-2011A/B, AV-2021A, XV-2033A/2034A and PV-2041A are instrument-not-on-pid, even though their tags are now printed. The check apparently only counts tags shown on instrument bubbles or actuators, not valve labels. The reviewer should judge this; it may be a core issue.\n- The SIP-line label 100-SS-2020A may still be more than 15 mm from its line after my last nudge. I didn't re-run the check, so this is unconfirmed.\n- The drive and coil outlines are drawing only: the motor has no tag of its own.\n- S4#9 (vent filter housing heating), the seed-vessel relief check (S3#1), and the other S1 to S3 carry-overs are left for S9.\n- I did not start P-203.","ttft_ms":3276,"type":"result","duration_ms":689655,"uuid":"9f09f837-cc4e-4f43-81a9-1d6693e1fb66","ttft_stream_ms":2955,"time_to_request_ms":35,"time_to_request_phases_ms":{"other":6,"system_prompt":4,"resume_other":1,"process_user_input":1,"input_attachments":7,"input_hooks":0,"transcript_persist":2,"tool_pool_refresh":1,"init_message":2,"engine_pickup":0,"message_prep":1,"model_config_wait":0,"autocompact":1,"query_setup":0,"model_gates":0,"tool_schema_build":6,"message_normalization":0,"client_creation":1,"request_build":2},"turn_start_resume_kind":"none","process_turn_index":0,"time_to_request_loop_lag_ms":0,"time_to_request_cpu_ms":60,"time_to_request_major_faults":0,"input_attachments_detail":{"slowest_producer":"deferred_tools_delta","slowest_producer_ms":5,"cpu_ms":12,"major_faults":0},"first_content_frame_ms":2955,"queued_turn_count":0,"result_index":0}


Check: `cheme status`, `cheme validate` (and `--fail-on warning`, saying which warnings
are expected for later sheets), `cheme fmt --check`, `git log` / `cheme diff <stage start
commit> --list` of the stage (the branch stage/basic-lactic-acid-fermentation starts at
c49d86cd; the local `main` is stale, do not diff against it), the YAML lists against the sheets, DESIGN.md decisions and numbers (sanity-check
the main balances), `cheme check --stage basic`, and for P&ID stages render each new or
changed sheet to PNG (`cheme render --png`, `--crop` on dense areas) and READ the images:
say only what you saw. Review the fermentation area as an industrial bioprocess engineer
would (seed train, sterilisation, sterile boundary, CIP/SIP, pH and temperature control,
vent and vacuum protection, the schedule arithmetic), and check that every number is
sourced or marked ASSUMED. You have a budget of USD 1.5: be efficient. Stay on the
current branch; never push, merge or sign off.

For a layout stage (S8), the review record's topic is `layout` (not design) and it cites the
rendered plot plan and at least two sections by file name (`cheme layout render --plan --png`,
`--section ... --png`), which you render and look at.

Write two things:
1. `reviews/<today>-S4b-review.md` in the format of reviews/README.md: front matter with
   topic design, reviewed_commit (`git rev-parse HEAD`), scope, reviewer "independent review
   agent", reviewer_kind agent, branch and merge; findings with ids, severity, status open;
   a Previous findings section with the current status of every earlier open finding
   (closed <commit> only with the fixing commit). Commit it alone.
2. `build/agent-run/S4b/review.json` (not committed):
   {"scores": {"process": 0-5, "safety": 0-5, "drawing": 0-5, "consistency": 0-5},
    "acceptable": true|false,
    "findings": [{"id", "severity", "where", "finding", "fix"}],
    "carry_over": ["the concrete fixes the next stage should do first, most important first"]}
