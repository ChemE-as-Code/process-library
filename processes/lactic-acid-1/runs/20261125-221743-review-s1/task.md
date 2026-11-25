You are the independent senior reviewer (process, safety, drawing, consistency) for stage
S1 of this plant repository. You did not do the work. Do not modify tracked files except
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
Basic-engineering basis, no P&ID XML yet: (a) DESIGN.md decisions D-013 onward for the fermentation area as the specification lists (seed train with its schedule arithmetic and number of trains, continuous steriliser parts and the fill-rate decision, production fermenter design R-201A..P: agitator, jacket, pH by milk-of-lime ring main, no aeration with the reason, N2 overlay or sterile vent, sterile filter, relief and vacuum protection, steam blocks and the sterile boundary, CIP station and SIP steam, harvest and broth hold; the sheet split; tag and line-numbering conventions), and the SRC-1 facts of the specification added to the source register; (b) equipment/equipment-list.yaml: R-201 split into R-201A to R-201P, the seed fermenters, CIP station items, tanks, pumps, filters, the steriliser's parts, and the downstream items basic engineering needs (pumps, drums, reboilers, condensers, vacuum systems), each with type, service, sheet, design pressure/temperature, material and dimensions (diameter/height or length/width/height, ASSUMED where not sourced) so the layout can use them; (c) plant.yaml: stage basic and every sheet of the specification declared status planned; (d) first line list entries for the fermentation-area lines (number, from, to, DN with the basis) and the instrument list for P-101 to P-204 as far as decided; (e) the plot plan for gate layout-plot-plan (layout/site-plan.yaml with site, areas, roads, racks and separations; layout/equipment-placement.yaml with every equipment-list item placed; skill layout-yaml). Run cheme validate (planned sheets hold back not-on-pid findings) and cheme check; commit in logical pieces.

Stage result (Claude Code JSON, tail):
 medium and sterilising it in 4 h campaigns at the fill rate (200 t/h) rather than adding a sterile buffer tank. E-101 is split into its parts: regenerative exchanger, steam heater E-102, holding tube X-101 (413 K for 120 s, ASSUMED), trim cooler E-103, back-pressure valve, and a divert valve back to V-101. The year-average steam stays at the concept's Q17 of 1.48 MW.\n- **Fermenters (D-016 to D-020):** R-201A to P, each with:\n  - a 160 kW agitator (127 kW absorbed) with a sterile-barrier seal;\n  - half-pipe coils on its own tempered-water loop, with the temperature and lost-cooling agitator trip from D-012;\n  - two pH probes dosing from a DN 100 milk-of-lime ring main;\n  - no aeration (from SRC-1), a nitrogen overlay at 0.3 barg, DN 150 sterile vent and inlet filters;\n  - a rupture disc sized on the SIP steam case, and a vacuum relief;\n  - steam blocks on every sterile entry, which mark the sterile boundary.\n- **Other decisions:** D-021 CIP and SIP, D-022 lime, D-023 sheet split and tag/line/instrument numbering, D-024 harvest and broth hold, D-025 downstream items, D-026 plot plan (fermenters outdoors in two rows of eight; a fermentation hall was rejected).\n- **D-027:** the CSL protein lump has no formula, so its five component balances cannot be evaluated. Inventing a formula would be invented data, so I accepted these findings in `checks/checks.yaml` with that reason. This is my proposal; the reviewer should confirm or reject it.\n- **Source register:** the SRC-1 seed-train facts from the specification are added to its row.\n\n**Files**\n- **Equipment list:** about 270 items, each with type, service, sheet, design pressure and temperature, material and dimensions, ASSUMED where not sourced.\n- **`plant.yaml`:** stage set to basic, with the ten P&IDs (P-101 to P-403) declared as planned.\n- **Line list:** 36 fermentation-area lines, each DN with its velocity basis.\n- **Instrument list:** the instruments decided so far for P-101 to P-204, with R-201A as the typical and seed train A.\n- **Layout:** `site-plan.yaml` (areas, roads, racks PR-1 to PR-6, separations around the ethanol area), `building.yaml` (B-201 for media, seed and CIP; control room; substation), and every listed item placed with no clashes.\n\n**Gates still failing, each for a stated reason**\n- `pids-exist`: no P&IDs are drawn yet; that is the next stage.\n- `layout-3d`, `lifting-study`, `mto`: these need the 3D model, zones and structures, including the access structure on the fermenter tops where the filters are placed now but not yet mounted.\n- `design-review`, `layout-review`: these need an independent reviewer.\n\n**Not done yet:** the P&IDs, `control/loops.yaml` and `control/cause-effect.yaml` (they follow once P-101 and P-202 are drawn), the relief items in `piping/special-items.yaml`, R-201B to P's own lines and instruments, the tank bunds, and the HAZOP draft.\n\nThe commits carry an automatically set git identity (machine username and hostname); `git config` should be set before more commits. Nothing is pushed or signed off, and a merge is pending a human review of the branch.","ttft_ms":3295,"type":"result","duration_ms":1287484,"uuid":"12510c6e-81cf-471b-9c35-599b53225993","ttft_stream_ms":2825,"time_to_request_ms":41,"time_to_request_phases_ms":{"other":7,"system_prompt":4,"resume_other":0,"process_user_input":1,"input_attachments":9,"input_hooks":1,"transcript_persist":2,"tool_pool_refresh":1,"init_message":2,"engine_pickup":0,"message_prep":0,"model_config_wait":1,"autocompact":0,"query_setup":1,"model_gates":0,"tool_schema_build":7,"message_normalization":1,"client_creation":0,"request_build":4},"turn_start_resume_kind":"none","process_turn_index":0,"time_to_request_loop_lag_ms":0,"time_to_request_cpu_ms":61,"time_to_request_major_faults":136,"input_attachments_detail":{"slowest_producer":"deferred_tools_delta","slowest_producer_ms":6,"cpu_ms":12,"major_faults":31},"first_content_frame_ms":2825,"queued_turn_count":0,"result_index":0}


Check: `cheme status`, `cheme validate` (and `--fail-on warning`, saying which warnings
are expected for later sheets), `cheme fmt --check`, `git log` / `cheme diff <stage start
commit> --list` of the stage (the branch stage/basic-lactic-acid-fermentation starts at
c49d86cd; the local `main` is stale, do not diff against it), the YAML lists against the sheets, DESIGN.md decisions and numbers (sanity-check
the main balances), `cheme check --stage basic`, and for P&ID stages render each new or
changed sheet to PNG (`cheme render --png`, `--crop` on dense areas) and READ the images:
say only what you saw. Review the fermentation area as an industrial bioprocess engineer
would (seed train, sterilisation, sterile boundary, CIP/SIP, pH and temperature control,
vent and vacuum protection, the schedule arithmetic), and check that every number is
sourced or marked ASSUMED. You have a budget of USD 2: be efficient. Stay on the
current branch; never push, merge or sign off.

For a layout stage (S8), the review record's topic is `layout` (not design) and it cites the
rendered plot plan and at least two sections by file name (`cheme layout render --plan --png`,
`--section ... --png`), which you render and look at.

Write two things:
1. `reviews/<today>-S1-review.md` in the format of reviews/README.md: front matter with
   topic design, reviewed_commit (`git rev-parse HEAD`), scope, reviewer "independent review
   agent", reviewer_kind agent, branch and merge; findings with ids, severity, status open;
   a Previous findings section with the current status of every earlier open finding
   (closed <commit> only with the fixing commit). Commit it alone.
2. `build/agent-run/S1/review.json` (not committed):
   {"scores": {"process": 0-5, "safety": 0-5, "drawing": 0-5, "consistency": 0-5},
    "acceptable": true|false,
    "findings": [{"id", "severity", "where", "finding", "fix"}],
    "carry_over": ["the concrete fixes the next stage should do first, most important first"]}
