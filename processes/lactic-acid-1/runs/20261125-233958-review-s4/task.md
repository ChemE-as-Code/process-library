You are the independent senior reviewer (process, safety, drawing, consistency) for stage
S4 of this plant repository. You did not do the work. Do not modify tracked files except
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
Draw P-202, production fermenter R-201A in full detail as the typical one, everything item 3 of the specification lists (agitator and seal, jacket on tempered cooling water with the temperature loop, pH loop with two probes and the milk-of-lime dosing branch with flush, radar level, headspace pressure with vent back-pressure valve, steam-sterilisable vent filter, relief for the SIP steam case, vacuum protection, N2 overlay or sterile vent per DESIGN.md, note: no aeration (anaerobic), aseptic sampling valve, steam blocks on medium and inoculum inlets, harvest valve, CIP spray supply and return, SIP steam inlets and condensate traps, sterile boundary marked). Make it readable at slide size: one vessel large in the middle, loops clearly drawn. Render each sheet (cheme render --png, crops of dense parts) and LOOK at it before committing; keep the equipment, line and instrument lists in step (skill lists-sync); commit each sheet when it validates. Of the FIX FIRST list do only what P-202 needs (S1#3 SIP in the turnaround, S1#4 vacuum case and vent-filter protection, S1#7 tempered-water heating, S2#9 the lime-dosing sterile boundary, steam blocks on CIP inlets as S2#1/S3#5 ask, high-level protection, aseptic sampling, and the C&E entries of R-201A's trips) and design R-201A so the seed-train findings do not repeat there; leave the other carry-over items (P-201, P-102, P-103 drawing fixes) to the close-out stage S9.

Stage result (Claude Code JSON, tail):
 not wetted.\n  - The inlet filter F-202A also takes the vacuum relief PSV-2046A, which admits air through it.\n  - The rupture disc PSE-2045A is sized on the SIP steam case.\n- **Sterile boundary:**\n  - Steam blocks on the medium, inoculum, lime, CIP supply, CIP return and harvest lines.\n  - Head SIP steam enters through the CIP spray line; bottom SIP enters through the bottom valve cluster, with TI-2015A at the coldest point.\n  - Aseptic sampling valve, steam-flushed.\n  - A note marks the boundary, and another says the fermentation is not aerated.\n- **Trips (I-201 to I-204):** the four R-201A trips are in `control/cause-effect.yaml`, and R-201A's four control loops are in `control/loops.yaml`.\n\n**Decision D-031** records all of this, with the arithmetic and every ASSUMED value. It answers these findings:\n- **S1#3 (SIP in the turnaround):** the timed turnaround is 12.5 h, not 12 h. The harvest period goes from 9.88 to 9.91 h, about 0.3 % fewer batches a year. I kept 16 fermenters and left the flowsheet unchanged.\n- **S1#4 (vacuum):** the governing case is steam collapse after SIP, about 24 000 m3/h of gas demand. No filter path can pass that, so it is prevented by a trip and permissives rather than relieved. If the HAZOP does not credit that trip, the fermenters need a full-vacuum rating. This is an open HAZOP item.\n- **S1#7 (heating):** the steam injection above.\n- **S2#9 (lime and the sterile boundary):** the boundary is the steam block on the dosing branch; the non-sterile lime crossing it when dosing is an accepted risk.\n- **For R-201A only:** S2#1/S3#5 (steam block on the CIP inlet) and S3#4 (high-level protection).\n\n**List and drawing changes you should know about**\n- R-201A to P are now listed as DEXPI `Vessel`, the same class as the seed fermenters. The sterile filters are `GasFilter`.\n- The lime branch is renumbered 25-ML-2024A; the old number reused the sequence of a steam line.\n- I added 13 lines and created `piping/special-items.yaml`.\n- The authoring tools have no vacuum-relief valve, so PSV-2046A is drawn as a check valve. The rupture-disc symbol cannot carry a tag, so PSE-2045A is tagged by a note.\n- I accepted 13 findings explicitly in `checks/checks.yaml`, each with a reason and no wildcards:\n  - one measuring-line crossing at TIC-2011A;\n  - eight short steam/flush stubs drawn at their valves instead of the sheet edge;\n  - the 100-CS-2016A line labels, which are tight beside the CIP steam block;\n  - the PSE-2045A note.\n\n**What's left**\n- The carry-over items stay for S9, as asked: the seed-train findings (S3#1 to #10), P-102 and P-103 fixes, S2#2/S2#3, and the control sequences that hold the CIP, fill and cooling permissives.\n- I couldn't delete `pid/P-201.refused.xml` or the new `pid/P-202.refused.xml`: removing files needs your approval. Both are untracked.\n- The 3D layout, lifting and MTO gates are still failing for the reasons stated before.\n- The design-review gate fails until the independent review runs.\n\n**Merge is pending.** Nothing was pushed, merged or signed off; the branch waits for the independent review.","ttft_ms":3440,"type":"result","duration_ms":1376719,"uuid":"ceb46978-4a51-4616-b4cb-bfed04a647f9","ttft_stream_ms":3202,"time_to_request_ms":44,"time_to_request_phases_ms":{"other":7,"system_prompt":7,"resume_other":0,"process_user_input":1,"input_attachments":9,"input_hooks":1,"transcript_persist":2,"tool_pool_refresh":2,"init_message":2,"engine_pickup":0,"message_prep":0,"model_config_wait":1,"autocompact":1,"query_setup":0,"model_gates":0,"tool_schema_build":7,"message_normalization":0,"client_creation":1,"request_build":3},"turn_start_resume_kind":"none","process_turn_index":0,"time_to_request_loop_lag_ms":0,"time_to_request_cpu_ms":75,"time_to_request_major_faults":0,"input_attachments_detail":{"slowest_producer":"deferred_tools_delta","slowest_producer_ms":6,"cpu_ms":15,"major_faults":0},"first_content_frame_ms":3202,"queued_turn_count":0,"result_index":0}


Check: `cheme status`, `cheme validate` (and `--fail-on warning`, saying which warnings
are expected for later sheets), `cheme fmt --check`, `git log` / `cheme diff <stage start
commit> --list` of the stage (the branch stage/basic-lactic-acid-fermentation starts at
c49d86cd; the local `main` is stale, do not diff against it), the YAML lists against the sheets, DESIGN.md decisions and numbers (sanity-check
the main balances), `cheme check --stage basic`, and for P&ID stages render each new or
changed sheet to PNG (`cheme render --png`, `--crop` on dense areas) and READ the images:
say only what you saw. Review the fermentation area as an industrial bioprocess engineer
would (seed train, sterilisation, sterile boundary, CIP/SIP, pH and temperature control,
vent and vacuum protection, the schedule arithmetic), and check that every number is
sourced or marked ASSUMED. You have a budget of USD 2.5: be efficient. Stay on the
current branch; never push, merge or sign off.

For a layout stage (S8), the review record's topic is `layout` (not design) and it cites the
rendered plot plan and at least two sections by file name (`cheme layout render --plan --png`,
`--section ... --png`), which you render and look at.

Write two things:
1. `reviews/<today>-S4-review.md` in the format of reviews/README.md: front matter with
   topic design, reviewed_commit (`git rev-parse HEAD`), scope, reviewer "independent review
   agent", reviewer_kind agent, branch and merge; findings with ids, severity, status open;
   a Previous findings section with the current status of every earlier open finding
   (closed <commit> only with the fixing commit). Commit it alone.
2. `build/agent-run/S4/review.json` (not committed):
   {"scores": {"process": 0-5, "safety": 0-5, "drawing": 0-5, "consistency": 0-5},
    "acceptable": true|false,
    "findings": [{"id", "severity", "where", "finding", "fix"}],
    "carry_over": ["the concrete fixes the next stage should do first, most important first"]}
