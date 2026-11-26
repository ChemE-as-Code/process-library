You are the independent senior reviewer (process, safety, drawing, consistency) for stage
S6 of this plant repository. You did not do the work. Do not modify tracked files except
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
Draw P-301 (cell removal S-301 machines in parallel with their feed and cake handling, acidulation R-301 with the 93 wt% acid dosing on ratio/pH and its cooling sized on D-007, gypsum belt filter S-302 with vacuum system, filtrate receiver and pumps, gypsum cake discharge) and then P-401 (four-effect evaporator E-401 with effects, separators, condenser, vacuum system, condensate and pumps). Render each sheet (cheme render --png, crops of dense parts) and LOOK at it before committing; keep the equipment, line and instrument lists in step (skill lists-sync); commit each sheet when it validates. Of the FIX FIRST list do only item 0 (S5b#1: the SIP header set point below every vessel's design pressure, or per-vessel SIP pressure control, recorded in D-037) first; leave the other carry-over items to the close-out stage S9 and spend the rest of the budget on the two downstream sheets.

Stage result (Claude Code JSON, tail):
-acid-fermentation`**\n1. **S5b#1 (`d0e8fffa`):** the SIP header set point PIC-2205 drops from 3 to 1.5 barg (recorded in D-037).\n   - 1.5 barg is 60 % of the fermenters' 2.5 barg design pressure and disc set point, and below the seed vessels' 3.0 and 6.0 barg, so a normal SIP no longer bursts a disc.\n   - Steam at 1.5 barg is about 127 C, which still leaves margin for the 121 C vessel SIP.\n   - PV-2205 fails closed and alarms high at 1.8 barg (both assumed). I did not add per-vessel pressure control.\n   - At the new pressure the DN80 bottom SIP inlets reach about 60 m/s at heat-up peak. I accepted that as assumed and left it for detail engineering to check.\n2. **P-301 (`eba0eac0`, D-038):** cell removal, acidulation and gypsum filtration.\n   - Three centrifuges S-301A to C, each on its own feed flow loop; the cell mass cake goes through hopper V-301 and pumps P-301A/B to anaerobic digestion.\n   - R-301 gets agitator A-301 (newly listed). The 93 % acid is dosed in ratio to the clarified broth flow, trimmed by a pH loop (pH about 2.5, assumed).\n   - The heat is removed by a pump-around through E-301, sized on 2.0 MW.\n   - The belt filter S-302 drains to filtrate receiver V-303 with vacuum pumps K-301A/B and filtrate pumps P-306A/B.\n   - One change to an earlier decision: the acid now goes into the tank at the impeller, not into the pump-around as D-025 said (avoids local heat and gypsum scale in the slurry line and exchanger). The reason is in D-038.\n3. **P-401 (`3406a099`, D-039):** four-effect falling-film evaporator E-401A to D in forward feed.\n   - Each effect has a circulation pump P-403x and a sump level loop on the transfer to the next effect; LP steam to E-401A is flow-controlled.\n   - The vapour cascades to the surface condenser E-402; condensates go to receiver V-401 under vacuum pumps K-401A/B.\n   - The concentrate leaves by P-402A/B on a density loop.\n   - The effect pressures (1.0, 0.6, 0.3, 0.12 bar(a)) are assumed, and the vapour line sizes (DN600 to DN1400) follow from them.\n\n**What to know about the drawings**\n- Each sheet has crossings that cannot be drawn away, accepted in `checks.yaml` as proposals for the design review: 2 on P-301 and 7 on P-401.\n- About 10 cosmetic drawing warnings remain on P-401: effect tags sitting on their symbol outline, the DIC-4002 measuring line through its valve actuator, and a product off-page note crowding a pump label.\n- DEXPI's diameter standard has no DN250 to DN1400, so those sizes appear only in the line numbers and the line list, not on the nozzles.\n\n**What is left**\n- Carry-over items S5b#2 to #10 and the S5 findings are for close-out stage S9.\n- P-402 and P-403 are not drawn.\n- New items are not yet in the layout (A-301 at least). The layout gates still fail: no plant model, no zones, no layout review.\n- Open on P-301: R-301 level trips, vacuum pressure indication, belt filter interlocks.\n- Open on P-401: vacuum control, evaporator CIP, relief of E-401A's steam chest.\n\nA merge is pending: the branch is waiting for the independent review, and a human or the reviewer has to merge it.","ttft_ms":5073,"type":"result","duration_ms":1389308,"uuid":"2a2bc346-69d7-4ce5-806a-b1d7f8f7d31f","ttft_stream_ms":4657,"time_to_request_ms":41,"time_to_request_phases_ms":{"other":7,"system_prompt":6,"resume_other":0,"process_user_input":1,"input_attachments":9,"input_hooks":1,"transcript_persist":1,"tool_pool_refresh":2,"init_message":2,"engine_pickup":0,"message_prep":0,"model_config_wait":1,"autocompact":1,"query_setup":0,"model_gates":0,"tool_schema_build":6,"message_normalization":1,"client_creation":0,"request_build":3},"turn_start_resume_kind":"none","process_turn_index":0,"time_to_request_loop_lag_ms":0,"time_to_request_cpu_ms":72,"time_to_request_major_faults":0,"input_attachments_detail":{"slowest_producer":"deferred_tools_delta","slowest_producer_ms":6,"cpu_ms":15,"major_faults":0},"first_content_frame_ms":4657,"queued_turn_count":0,"result_index":0}


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
1. `reviews/<today>-S6-review.md` in the format of reviews/README.md: front matter with
   topic design, reviewed_commit (`git rev-parse HEAD`), scope, reviewer "independent review
   agent", reviewer_kind agent, branch and merge; findings with ids, severity, status open;
   a Previous findings section with the current status of every earlier open finding
   (closed <commit> only with the fixing commit). Commit it alone.
2. `build/agent-run/S6/review.json` (not committed):
   {"scores": {"process": 0-5, "safety": 0-5, "drawing": 0-5, "consistency": 0-5},
    "acceptable": true|false,
    "findings": [{"id", "severity", "where", "finding", "fix"}],
    "carry_over": ["the concrete fixes the next stage should do first, most important first"]}
