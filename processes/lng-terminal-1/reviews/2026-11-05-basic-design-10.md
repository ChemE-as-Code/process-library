---
topic: design
reviewed_commit: ae718797ed39e8224860598165180cb4e7f60a7c
scope: [pid/P-01.xml, pid/P-02.xml, pid/P-03.xml, pid/P-04.xml, pid/P-05.xml, pid/P-06.xml, pid/P-07.xml, pid/P-08.xml, equipment/equipment-list.yaml, piping/line-list.yaml, piping/special-items.yaml, control/instrument-list.yaml, control/cause-effect.yaml, control/loops.yaml, control/sequences.yaml, DESIGN.md]
basis:
  - {path: process/flowsheet.yaml, revision: ae718797ed39e8224860598165180cb4e7f60a7c, relation: depends-on}
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-basic
merge: pending
---
# Review: design, ninth follow-up (basic stage P&IDs P-01 to P-08, lists, C&E, loops, sequences)

## Summary

This is the independent follow-up to `2026-11-05-basic-design-9`. It reviews HEAD `ae718797` on
`stage/lng-terminal-1-basic`, branched from main `0b155d62` (PR #432). I did not write any of this
design. The working tree was clean during the review. The commits since review 9 (`c257902c`):
- `6f57c6c2`: migration to core 1.11.0 (D-038): BFD / PFD generator 7, off-page connectors on the
  sheet edges. Drawing only.
- `fd39c222`: fix round 10, the response to design review 9 (D-039) and layout review 7 (D-040).
- `1dd46636`: the response to the round-10 independent design check (`build/check-design-r10.json`,
  D-039.9 (a)..(i)).
- `ae718797`: the response to the re-check of that repair (D-039.9 (j)).

Review 9 left one high, three mediums and four lows open, plus review 5 #9 (low). At HEAD, judged on
the drawn sheets, `cheme show` and the control files:
- **Review 9 #1 to #8 are closed.**
  - #1 (high): T-8101 is kept dry, with P-8102 in a floor pocket. I-801 has LNG detections that
    never stand under water: TSL-8102 above the start level, TSL-8120 in the riser and AT-8124 at
    the rim. LZT-8113 is an independent trip level (I-809) and gives a rate-of-rise inhibit (I-810).
  - #2: the arm thermal reliefs are set at 8.0 barg, below the carrier's 10 barg, and SEQ-ESD has
    a let-down.
  - #3: low N2 no longer aborts; the station has a regulator and a rate basis, and the N2 is a hold
    (H-07).
  - #4: LZT-8119 is an independent trip level.
  - #5 / #6: the bleeds are locked closed, and the gauges read the line beyond the check valve.
  - #7: the loops and the philosophy are brought up to date.
  - #8: the stale texts are corrected.
- Review 5 #9 stays open. The three accepted findings stay accepted.

I judged the two items the adversarial check raised against review 9, the nine items of the round-10
design check and its re-check (j). Each answer is sound, with two exceptions:
- One reason in (j) does not hold: "the tank-limit causes are made unlikely by the permissive". That
  is the new #1.
- The S2 timeout of (j) contradicts the rule that low N2 is no abort. That is #2.

This pass found seven new findings: one medium and six lows, one of them accepted.
1. **#1 (medium).** The SEQ-LINE-EMPTY permissive keeps 1,100 m3 below the receiving tank's
   high-high and ignores the rundown. ESD-1 does not stop the rundown, which carries ~7,560 m3/h.
   If it fills the same tank, the margin lasts ~9 min. In holding the tanks are near full, so I-201
   becomes the expected abort. The abort's hold is the case the design itself records as feeding
   the leak beyond the 240 min of PFP.
2. **#2 to #7 (low):**
   - #2: the S2 timeout aborts a displacement that is still making progress.
   - #3: the berth N2 tie-in bleeds stay open to the atmosphere on the platform.
   - #4: the CV-8114 drain-back hole against the "no back-flow" text.
   - #5: local gauges are drawn as control-room instruments.
   - #6: the six carrier connections stay off the edge (accepted).
   - #7: no detector-to-damper transit time is stated for the B-SUB intake trip.

Verdict: **ready for basic-engineering issue on the design topic.** No critical or high finding is
open. Before issue, disposition #1 and record the reason. The stage sign-off also needs:
- a current layout review (the layout-review gate fails on its stale records, outside this scope);
- a human approver;
- the HAZOP restamp of H-01..H-05 against these sheets (32 `hazop-input-changed` warnings), for its
  owner.

Merge pending.

## Branch diff

`cheme diff origin/main --list`, summary of the plant items changed on the branch:

```
pid/P-01.xml: HS-1108 / HS-1109, XV-1108 / XV-1109, tees T1003 / T1114, BOG-1003, BOG-1010, FG-1001,
  LNG-1001, LNG-1003 and the off-page connectors LNG-1001..1004_To, BOG-1003_From, FG-1001_From
  (modified: moved to the edges, D-038)
pid/P-02.xml / pid/P-03.xml: off-page connectors of LNG-n001 / n002, BOG-n001..n004, BOG-n011..n015,
  A-n002 / n003 (texts added or moved, D-038)
pid/P-04.xml: added PI-4163, PI-4164, PCV-4159, PCV-4160; moved CV-4151, CV-4152; changed FO-4151 / 4152,
  HV-4151..4154, HV-4161 / 4162, PI-4155..4158, LNG-4001, LNG-4005, LNG-4009, LNG-4010, N-4001, N-4002,
  T4N1 / T4N2 and the connectors N-4002_From, N-4003_To, N-4004_To, LNG-4005_To, LNG-4009_To
pid/P-05.xml / pid/P-06.xml: SR-5102 / SR-6102 (re-typed Strainer), LNG-n001, BOG-n012 (connector)
pid/P-07.xml: PSV-7111, FL-7002, connectors DR-7001_To, FL-7002_To, LNG-4008_From
pid/P-08.xml: added AT-8124, AT-8141A/B/C, HS-8103, LZT-8113, LZT-8119, TSL-8120, UZ-8142..8144;
  changed LI-8103, PI-8121, TSL-8102, TSL-8104, T-8101, T-8102, N-8001, N-8002, W-8002, W-8003, T8N1
  and the connectors IA-8001_To, LNG-8001_To, N-8001_From / _To, N-8002_To, W-8002_To, W-8003_To
process/BFD.xml, process/PFD.xml: provenance note only (generator 7)
```

The `[4163]`-style labels that `cheme diff` prints for the added functions are only the diff's
display. Their XML carries category, functions and number as PI-4155 does (`pid/P-04.xml:5053`).

Every change has its reason in D-038 / D-039 / D-039.9 and in PROGRESS.md. No changed plant item is
`not drawn`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-design-10#1 | P-04, P-01 / P-02 / P-03, SEQ-LINE-EMPTY (permissive LZT-2102, abort, abort actions), C&E I-201 / I-301, DESIGN.md D-039.9 (d) / (j) | Tank-limit permissive of SEQ-LINE-EMPTY ignores the rundown into the receiving tank | The permissive asks for "at least 1,100 m3 below the high-high level of the receiving tank", the volume of the line to be displaced. ESD-1 (I-501 / I-601) does not stop the rundown. The trains keep filling the tanks at ~7,560 m3/h (D-003), and S1 does not move the rundown away from the receiving tank. If T-2101 takes both the return and the rundown, the 1,100 m3 margin lasts ~9 min. Over the ~3.5 h of the sequence the rundown brings ~26,000 m3. In holding, before a carrier, the tanks are near full, so I-201 is the expected outcome, not a fault. I-201 closes XV-2123 and the sequence aborts into the hold. D-039.9 (j) states that the 240 min of PFP are kept only if the restart comes within ~0.45 h of an early abort. A longer hold leaves the leak fed to ~6.5 h, with ~65 m3 of T-8102's 87 m3 used. It accepts that hold as a residual of H-07, because "the tank-limit causes are made unlikely by the permissive". That reason does not hold while the rundown can enter the same tank. The restart onto the other tank "at once" depends on that tank too not taking the rundown. Medium: a defect in the permissive of a recorded abnormal procedure. The operator can still recover by switching the fill (SEQ-FILL-CHANGE), and no safeguard is missing. | medium | open | Make the permissive the tank that does not take the rundown: the rundown lined up to the other tank (SEQ-FILL-CHANGE, ZSC-1102 / ZSC-1103) before S1, or a margin of 1,100 m3 plus the rundown into that tank over the sequence (~4 h). Name the second tank's margin the same way for the restart. Correct the reason in the abort actions and D-039.9 (j). |
| 2026-11-05-basic-design-10#2 | P-04, SEQ-LINE-EMPTY S2 (timeout, on_timeout), D-039.9 (j) | S2 timeout aborts a displacement that is still progressing | S2 now times out at 5 h, with `on_timeout: abort`. The reason given is that 5 h is "longer than the ~4.6 h displacement at 2,000 Nm3/h, the lowest N2 rate S2 runs on", so low N2 is no abort. But the "no N2 entering" abort only acts below ~100 m3/h of return, which is ~900 Nm3/h. Between ~900 and ~1,800 Nm3/h the displacement is still going (5.1-10 h), yet the timeout aborts it. The abort closes the crossover and the return, and the leak is then fed from what is left of the line under the N2. That is the outcome D-039.3 (a) removed for low N2. | low | open | On the S2 timeout raise an alarm and an operator decision, and keep the displacement running while the return on FIC-4102 / FIC-4101 stays above the no-N2 threshold. Abort only on the stated causes (I-201, tank pressure, no N2). Alternatively, base the timeout on the expected end from the measured return. |
| 2026-11-05-basic-design-10#3 | P-05 / P-06, line list N-5001 / N-6001, HV-5151..5153 / HV-6151..6153 | Berth N2 tie-in bleeds open to the atmosphere on the platform | Review 9 #5 removed the open bleeds of the tank-end N2 stations: D-039.5 locks them closed, and gauges show a passing block. The berth N2 tie-ins have the same double block and bleed. N-5001 is "open to atmosphere while the N2 tie-in is isolated". There, LNG at up to ~5.5 barg in a transfer (more at a closure) stands behind the check valve and HV-5152 / HV-6152. A passing pair vents LNG continuously at the bleed outlet on the loading platform, and no drip tray or release source is stated for it. Low, as review 9 #5: the flow through passing seats is small, and the platform is classified anyway. | low | open | Treat it as the tank end: lock the bleed closed, with a gauge between the blocks read on rounds and before the purge. Or state the bleed outlet's position, drip collection and zone on the platform. |
| 2026-11-05-basic-design-10#4 | P-08, line list W-8002, C&E I-801 notes, equipment list P-8102 | CV-8114 drain-back hole against the "no back-flow" statement | D-039.1 (e) gives CV-8114 a ~6 mm drain-back hole. The line list still says "check valve ... (no back-flow into the impoundment)". The I-801 notes say that CV-8114 with HV-8115 "keeps the oily water system from flowing back". The pump's head allows ~10.2 m (1.0 barg) at the oily water battery limit. If that system can stand pressurised, it flows back through the hole and the stopped pump into the pocket: ~1 m3/h at ~1.5 bar. That includes the time when I-801 holds P-8102 off with LNG in the pit. Low: the flow is small, but the stated function and the basis now disagree. | low | open | State whether the oily water battery limit is free-discharging, non-pressurised at no flow. If it is not, add the means that stops back-flow (HV-8115 closed with P-8102 tripped, or a second check valve above the hole) and correct the line list and the I-801 notes. |
| 2026-11-05-basic-design-10#5 | P-04 (also P-05..P-08), instrument list PI-4155..4158, PI-4163 / 4164 | Local gauges drawn as control-room instruments | Every ProcessInstrumentationFunction on the sheets has `Location` CentralLocation, the generators' default. The renderer therefore draws the local gauges of the N2 stations with the control-room bar: PI-4155..4158, and the new PI-4163 / 4164 that SEQ-ESD S2 and SEQ-LINE-EMPTY read at the station. The instrument list calls them local gauges, and S1 completes on PI-4163 by an operator at the PR1 joint. A reader of the sheet would take the line pressure as visible in the control room. | low | open | Set the field location for the local gauges and switches in the generators (`draft_P-04.py` and the others; `cheme set <tag> Location=...`), or add a sheet note naming the local instruments. Keep the central bar for the transmitted indications (PI-4105, LI-8103, PDI-n102). |
| 2026-11-05-basic-design-10#6 | P-05 / P-06, LNG-5011 / 5013 / 5014, LNG-6011 / 6013 / 6014 | Carrier connections not on the sheet edge (6 `cheme.offpage-not-on-edge`) | The ship manifold is the terminal's battery limit (D-001). The six "to carrier" connectors stay 95 mm inside the bottom edge under their arms (D-038.3 (b), D-039.9 (i)). A route to the edge crosses the berth header, the other arms' risers and the vapour line, two to four crossings each. The rule's open-end forms (atm., vent, drain, hose) misdescribe a loading-arm coupler. Under its arm is the clearest presentation of the coupler, and the six warnings are not accepted in `checks/checks.yaml`. The drawing-clean gate passes because it does not list the rule. | low | accepted: the connector under its arm, at the coupler, reads better than six to twelve crossings; the reason in D-038.3 (b) / D-039.9 (i) is sound. By Claude (independent review agent), for the human reviewer to confirm at sign-off | Record the acceptance per connector in `checks/checks.yaml` (id `pid/P-05.xml#offpage-not-on-edge:Line_LNG5011_To` and the five others) with this reason once a human confirms it. Ask the library for an open-end form for a ship connection. |
| 2026-11-05-basic-design-10#7 | P-08, C&E I-811, instrument list AT-8141A/B/C / UZ-8142, layout/hvac.yaml AHU-1 | B-SUB intake trip: no detector-to-damper transit time stated | The refuge's gas-tightness rests on I-811 (D-039.6 (b)). The detectors sit "in the LV1 intake duct downstream of the louvre". The damper UZ-8142 is the gas-tight damper "of the outdoor-air intake LV1 (east wall)". If the damper sits at the louvre, gas passes it before the 2oo3 vote, plus the damper's stroke, so some gas is drawn in before the trip. Nothing states the duct length or the air transit time that must exceed the detection, vote and closure time, and the HVAC engineer and the F&G vendor have no criterion to meet. Low: it is a detail-engineering arrangement, and the trip itself is drawn and in the C&E. | low | open | State the requirement in the I-811 notes and in `layout/hvac.yaml`: the detectors at the intake ahead of the damper, and the duct transit time from the detectors to the damper longer than the detector response, the vote and the damper closure (ASSUMED values, HVAC / F&G). |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-design-9#1 | TSL-8102 at the floor of a pit that always holds water; LNG pumped to the oily water system | high | closed fd39c222 | **Drawn** (`build/P-08_tile-C1.png`, `B1.png`): P-8102 in T-8101; TSL-8102 and LI-8103 from the cover; AT-8124 on N4 and LZT-8113 on N3; TSL-8120 on W-8002 upstream of CV-8114 (`cheme show W-8002`); LI-8103 -> HS-8103 -> P-8102 (`cheme show HS-8103`). The gate `dry-tank-area-sump-on-pid` passes. **C&E:** I-801 trips on any of TSL-8102 / TSL-8120 / AT-8124, opens the feeder and latches. I-809 (LAHH 1.30 m) is a transfer-gated cause of I-501 / I-601. I-810 is the rate-of-rise inhibit. **Numbers reproduced:** 2.25 m2 x 1.2 m = 2.7 m3; a 4.0 m3/s run-out rises ~1.2 m/min over 201 m2; 0.1 m x 201 m2 = ~20 m3. The VSD added in `1dd46636` has a minimum speed corrected in `ae718797`. On a parabolic curve through 45 m at 50 m3/h and 59 m at shut-off, with ~7 m of friction at 50 m3/h, the pump delivers ~21 m3/h at 84 % and ~23 m3/h at 85 % against the 38 m fixed head. The worst cycling is ~10 starts an hour, under the 15 taken as the vendor limit. **Residuals, stated with an owner:** the pocket water up to the start level (~2 m3; siting study, H-05); small inflows on TSL-8120 alone (H-05 / H-06); water on the floor in holding after a pump failure (rundown spill, siting study). The new #4 is a text residual. |
| 2026-11-05-basic-design-9#2 | Berth header and arms blocked in against the carrier's manifold after ESD-1 | medium | closed fd39c222 | `piping/special-items.yaml`: PSV-5171 / 5173 / 5174 and PSV-6171 / 6173 / 6174 are set at 8.0 barg into D-n101. Each is drawn on the arm riser above the arm isolation (`build/P-05_tile-B1.png` / `B2.png`, `build/P-06_crop-0-95-285-201.png`), so it stays on the carrier side when the isolation closes. 8.0 x 1.1 + 0.9 = 9.7 barg < 10 barg. The operating ratio against the ~5.5 barg arm base is 0.69. The 10 barg is in `process/design-basis.yaml` (delivery note). SEQ-ESD S2: the let-down through XV-n161 after the I-n01 reset, closed by I-506 at drum high-high; I-n02 reset below 5.0 barg; restart from SEQ-LOAD S3. The P-05 / P-06 notes read "8.0 barg (below the carrier, D-039)". |
| 2026-11-05-basic-design-9#3 | N2 push-back: abort on low N2, unconfirmed N2 rate, line pressure in S3 | medium | closed 1dd46636 | (a) The abort is now on I-201, tank pressure or no N2 entering (return below ~100 m3/h for 5 min), not on low N2 pressure. Its action holds the line isolated under N2. (b) The rate basis (4,000 / 3,500 / 3,000 / 2,000 Nm3/h) is in the S2 operator text and in the design basis, with H-07 holding the minimum at 3,500 Nm3/h. (c) PCV-4159 / 4160 are set at 4.5 barg (`1dd46636`). I reproduced the 3.4 barg the displacement needs: 0.29 + 2.21 (48 m at 470 kg/m3) + 0.9 bar. At that limit the orifice is just unchoked: ~4.5 bar(a) outlet against 8 bar(a). The restart from S1 after an abort followed in `ae718797`. **Residuals:** the permissive (new #1) and the S2 timeout (new #2). |
| 2026-11-05-basic-design-9#4 | One transmitter for the dry-sump control, the transfer hold and the I-805 trip | medium | closed fd39c222 | LZT-8119 is drawn on T-8102 on its own nozzle (`build/P-08_tile-C1.png`). The I-805 cause and the LAH hold are on LZT-8119, and LZT-8106 is control only (I-806 / I-807, loop LC-8106). A deviation alarm runs between the two, and a bad signal is a hold (C&E I-805 notes, SEQ-LOAD S0 / S4). |
| 2026-11-05-basic-design-9#5 | N2 station bleeds HV-4161 / HV-4162 open to the atmosphere at grade | low | closed 1dd46636 | Line list N-4003 / N-4004: locked closed, opened only under permit with a gas test. On P-04, "LC" is printed at each bleed with the sheet note (`build/P-04_tile-A2.png`, `B3.png`). PI-4155 / 4156 (4157 / 4158) between the blocks are read on rounds. The same arrangement on the berth tie-ins is the new #3. |
| 2026-11-05-basic-design-9#6 | Isolated trestle line pressure not measured | low | closed 1dd46636 | `cheme show N-4001`: HV-4152 -> FO-4151 -> PCV-4159 -> T4N1 (bleed) -> HV-4151 -> CV-4151 -> T4A6. PI-4163 is drawn between CV-4151 and LNG-4001 (`build/P-04_tile-A2.png`), and PI-4164 likewise on line B (`B2.png`). They read the line with no valve opened. SEQ-ESD S2 and the SEQ-LINE-EMPTY permissive use them. The section between the inner block and the check valve relieves forward through the check valve. LNG reaches the section between the blocks only back through both. The station is Class 150 austenitic stainless (line list), so no section is blocked in liquid-full against carbon steel. |
| 2026-11-05-basic-design-9#7 | Loop register and philosophy behind the sheets | low | closed fd39c222 | `control/loops.yaml` has LIC-5111 (line 734), LIC-6111, LIC-8101, LC-8103 and LC-8106. I-501 / I-601 stop P-5101 / P-6101. `control/philosophy.md` names SEQ-LINE-EMPTY, SEQ-FILL-CHANGE, F-TRESTLE-LEAK, F-LINK (the link-lost carrier closure) and OBJ-5 (the dry sumps). `cheme control report`: 0 errors, 0 warnings. |
| 2026-11-05-basic-design-9#8 | Stale or inconsistent texts after D-036 | low | closed fd39c222 | (a) P-5101 datasheet: "into the berth header downstream of XV-5101 in the SEQ-LOAD S3 cooldown (~445 kPa(a))", with the discharge basis in its notes. (b) Electrical list line 213: "1.85 MW compressors and the 1.05 MW in-tank". (c) `process/design-basis.yaml` line 32: the carrier's 10 barg. (d) The I-801 notes describe the dry pocket. |
| 2026-11-05-basic-design-5#9 | Deferred safety inputs not registered as issues, holds or TQs | low | open | `cheme issues --all`: still one issue (#362), no hold or TQ. H-07 (site N2 rate and back-up) is added to the D-030 table only (D-039.5). |
| 2026-11-05-basic-design-3#5 | LIC-8101 duty/standby drawn as a chain through HS-8101A | low | accepted: the standby no longer depends on the chain for the hazard; I-802 starts both pumps on LZT-8105 and I-803 stops both; availability of the level band only. By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged (`build/P-08_tile-B1.png` / `B2.png`). LIC-8101 is now registered in `control/loops.yaml`. |
| 2026-11-05-basic-design-3#6 | PZT-7113 1oo1 stops every running compressor | low | accepted: a spurious trip sends the BOG to the flare, a production and flaring loss with no hazard; the voting is left to the SIL screening (now hold H-06). By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged: PZT-7113 (`build/P-07_tile-A1.png`) and I-705A-C. |
| 2026-11-05-basic-design-2#10 | No relief device sized against its governing case | medium | accepted: relief sizing is a detail-stage calculation; D-025 records the cases, and D-026.8, D-026.14, D-028, D-030, D-032, D-034, D-036 and D-039 add the FO-1117 blow-by, the D-7101 fire, the air-failure residual, the spurious ERS closure, the XV-4101 / 4102 / 4107 residual, the open rundown blocked-outlet case, the 31.1 t/h compressors and the post-ESD carrier section. By Claude (independent review agent), for the human reviewer to confirm at sign-off | The arm reliefs PSV-n17x now carry the blocked-in carrier section at 8.0 barg, and they also lift on a closure transient (special items). Their size, DN 25 for the warm-up, stays with the surge analysis H-01. |

## Items raised against review 9 by its adversarial check

I judged these on the drawn sheets and the control files at HEAD
(`build/adversarial-design-r9.json`).

1. **Missed medium: W-8002 freezes above the cover.** Answered. CV-8114 has a ~6 mm drain-back hole
   and the PR8 run falls to the battery limit, as W-8003 has since D-037.17 (line list W-8002,
   datasheet, P-8102 notes). The reason is sound. The residual, the "no back-flow" text against the
   hole, is #4.
2. **Missed medium: T-8101 has no level alarm.** Answered. LZT-8113 is independent of LI-8103 and
   gives the LAH at the pocket rim (a transfer hold in SEQ-LOAD S0 / S4), the LAHH as I-809 and the
   rate of rise as I-810. LC-8103 is registered, and LI-8103 drives HS-8103 by a drawn signal line.
   D-035's 100 m3 rain allowance is withdrawn, and the 2,761 m3 below the inlet hold the 2,400 m3
   spill. The reason is sound.

## Round-10 design check and its re-check

`build/check-design-r10.json` (three mediums, six lows) and D-039.9 (a)..(j):

1. **N2 station section blocked in liquid-full (medium).** Answered by moving CV-4151 / 4152 to the
   line side of the inner block. That is drawn (`build/P-04_tile-A2.png`) and confirmed by
   `cheme show N-4001`. The reason is sound: a check valve relieves forward, and no extra relief
   valve has to be proven.
2. **Regulator set at 3.0 barg (medium).** Answered: 4.5 barg, with the 3.4 barg need and the 0.5 bar
   offset stated. PI-4156 is corrected to ~2.8 barg. The no-N2 test is on the return flow
   (bidirectional meters ASSUMED, instrument vendor). Sound. I reproduced the figures.
3. **P-8102 start frequency (medium).** Answered with a VSD. (j) corrects the minimum speed against
   the full fixed head. Sound: my curve gives the same speed band (see review 9 #1).
4. **Abort residual (low).** Answered, with the hold's leak rate, its time to the PFP and T-8102, and
   the restart from S1. One reason is unsound: that the tank-limit abort is unlikely (#1).
5. **LZT-8113 bad signal (low).** Answered as a transfer hold, in the C&E I-809 notes, the instrument
   list and SEQ-LOAD S0 / S4. The PR8 sentence of the electrical list is corrected. Sound.
6. **I-801 coverage (low).** Answered as a stated residual for H-05 / H-06. Sound: a drip-sized inflow
   pumped for seconds is not a basic-design hazard.
7. **P-04 drawing of the stations (low).** Answered with a sheet note and "LC" at each bleed
   (`build/P-04_tile-B3.png`). No self-acting regulator symbol exists in the library. Sound.
8. **Stale texts (low).** Answered:
   - electrical list P-8102: 45 m, 10.2 kW, floor pocket, VSD;
   - AT-8141A/B/C and UZ-8142..8144: 6 cables in `electrical/cable-schedule.csv`;
   - the datasheet's suction source is corrected;
   - PDI-n102 keeps its tag as the control-room function, stated in the instrument list.

   Sound.
9. **Off-page connectors (low).** Four are moved to the edges, with five accepted crossings
   (`checks/checks.yaml`). I agree with each reason: each is a single crossing of a line that closes
   the connector's cell, and FL-7002 crosses twice. The six carrier connections are #6.
10. **(j) re-check.** The minimum speed and the restart from S1 are sound. The 5 h S2 timeout is #2.

## Drawing

`cheme validate` drawing lines at `ae718797`:

- P-01, P-02, P-03, P-08: every rule 0 (line-through-label, line-crossing, label-overlap,
  label-far-from-owner, text-outside-frame, title-text-overflow, line-through-symbol,
  line-through-valve, line-on-pipe, line-not-orthogonal, offpage-not-on-edge). P-08 has 1
  accepted line-crossing (HS-8101B measuring line, D-026.11).
- P-04: 0 line-crossing (+3 accepted: BOG-4011 x LNG-4002 and BOG-4015 x LNG-4002, D-026.11;
  N-4002 x LNG-4001, D-039.9). All other counts are 0, including offpage-not-on-edge.
- P-05 / P-06: 3 offpage-not-on-edge each, the carrier connections (#6, accepted). All other counts
  are 0.
- P-07: 0 line-crossing (+6 accepted: two from D-025; LNG-4008 x BOG-7012, DR-7001 x BOG-7008 and
  FL-7002 x BOG-7002 / FL-7003, D-039.9). All other counts are 0.

Tiles rendered with `cheme render pid/<sheet>.xml --png --tiles auto` (3x3 at scale 8):
- P-04: A1-C3 rendered; A1, A2, A3, B1, B2, B3, C1, C2 read. The two N2 stations in flow order, with
  LC and the regulator note, are in A2 / B2 / B3. PI-4163 / 4164 sit beyond the check valves. The
  accepted crossings are in A2 (N-4002 over LNG-4001) and B1.
- P-08: A1, A2, A3, B1, B2, B3, C1, C2, C3 read.
  - C1: T-8101 with P-8102, TSL-8102, AT-8124, LZT-8113, TSL-8120, CV-8114 / HV-8115, and W-8002
    and W-8003 down to the bottom edge.
  - B1: HS-8103 with the LI-8103 signal.
  - C2: T-8102 with LZT-8119 / TSL-8104 / LZT-8106 / TSL-8118 / P-8103.
  - B3: AT-8141A/B/C, UZ-8142..8144 and the I-811 note.
- P-05: A2, B1, B2, B3, C1, C2 read. B1: SR-5102 and PSV-5171 on the arm riser above XV-5121.
  B2: PSV-5173 / 5174 and the "to carrier" connectors. C1 / C2: the "8.0 barg (below the carrier,
  D-039)" note.
- P-06: crop `build/P-06_crop-0-95-285-201.png` read; it mirrors P-05.
- P-07: A1, B2, C2 read (LNG-4008 from the top edge; PSV-7111 and FL-7002 to the bottom edge across
  BOG-7002 and FL-7003).
- P-01: B2, C2 read (the four fill connectors on the bottom edge, BOG-1010 passing between the
  arrows and the notes).
- P-02: A1, A2 read (the "vent" texts on the pump column vents).

No overlap or ambiguous tag was seen in what was read. Crossings are drawn as plain four-way
intersections, and tees as three-way, so they can be told apart. The local / central bubble of the
gauges is #5.

## Mechanical checks (non-layout)

- `cheme validate`:
  - 95 files, 0 errors, 38 warnings. 32 are `cheme.hazop-input-changed` (H-01..H-05 against P-01..P-08,
    the C&E, the loops, the sequences and the special items), outside this scope, for the HAZOP owner
    to restamp. 6 are `cheme.offpage-not-on-edge` (#6).
  - The last line compares 10 sheets and 25 lists. It cross-checks equipment, lines and DN,
    instruments, piping items, tags in texts, interlocks, control records, electrical, HAZOP, layout,
    datasheets, datasheet nozzles and review records, with no error or warning in scope.
- `cheme check --stage basic`, before this record:
  - FAIL design-review: records stale ("changed since c257902c9115").
  - FAIL layout-review, outside this scope.
  - Every other gate ok, including the four new D-039 gates: `dry-tank-area-sump-on-pid`,
    `independent-sump-trip-level-and-n2-station-limits-on-pid`, `permanent-shore-strainers-on-pid` and
    `refuge-intake-gas-trip-on-pid`.
- `cheme control report -o build/r10rev-control`: 0 errors, 0 warnings. The loops, sequences and C&E
  are "drafted, changed since the review of c257902c9115". The narrative and the philosophy are not
  covered by a review record; they are outside this record's scope list, which is kept as review 9's.
- `cheme validate --only 'cheme.review-*'` after writing this record: 0 errors.

## Checked and fine

- **Arm thermal reliefs at 8.0 barg.**
  - Each PSV inlet sits on the arm riser between the arm isolation and the swivel, and its outlet
    goes into DR-n00x -> D-n101 downstream of XV-n161. On ESD-2, with the isolation closed, the PSV
    stays with the arm.
  - It lifts on a carrier-closure transient (bound 8.3 barg at the arm end) into D-n101. That is on
    the safe side and is stated in the special items. Sizing stays with H-01.
- **SEQ-ESD S2 let-down.**
  - The reset of I-n01 reopens no valve. XV-n161 is opened by the operator with XV-n101 proven
    closed. I-506 closes it at drum high-high. The drum vent goes to the vapour return, which
    I-501 keeps open (XV-4135).
  - The restart is from S3, which refills the arms and empties D-n101 with P-n101.
- **N2 stations.**
  - Flow order on the sheet matches the line list: outer block, PI-4155, orifice, regulator, PI-4156,
    bleed LC, inner block, check valve, PI-4163, tee.
  - The station is Class 150 austenitic stainless from the battery-limit spec break. Regulator
    failed open: 7 barg, below the 15 barg design. Lock-up ~4.7 barg in S3.
  - The S1 completion on PI-4163 < 4.0 barg keeps the inner block shut until the line is open to
    the tank.
  - S2 pressurises the station to lock-up before the inner block opens, so no LNG enters it.
- **SEQ-LINE-EMPTY numbers.**
  - 450 m3/h of return at 4,000 Nm3/h, and ~9 Nm3 of N2 per m3 of line at ~3.7 bar(a) and ~113 K.
  - The 3.4 barg bound reproduces.
  - The leak fed at ~1.3 kg/s in the S3 hold: sqrt(4.7 / 2.7) = 1.32.
  - From the earliest abort, 87 m3 lasts ~8.5 h at ~10 m3/h.
- **T-8101.**
  - The probes' set points (-60 degC) are below the -20 degC ambient and far above LNG.
  - I-801 is on the feeder, latching; I-810 acts on the control circuit, not credited.
  - AT-8124 is a third cause, and the foam starts from the F&G on any of the three.
  - The bad signal of LZT-8113 is a hold.
  - The pocket and floor geometry, the 2,761 m3 below the inlet and the pump's static of 27.8 m are
    consistent across the equipment list, datasheet, line list, C&E and loops.
- **T-8102.** LZT-8119 has its own nozzle and SIS input. LZT-8106 is control only. I-805 is a
  transfer-gated cause of I-501 / I-601, and so is I-809.
- **SR-n102 / PDI-n102.** Permanent T-type strainers with a top cover (DEXPI Strainer). PDI is
  transmitted with a PDAH, so nobody is needed at the header bay during a transfer.
- **B-SUB I-811.** It is 2oo3 at 25 % LFL, a fault counts as tripped, and it latches. The fan stops
  and the intake and exhaust dampers close (spring-return, fail closed). The tags agree across P-08,
  the instrument list, the C&E, `layout/hvac.yaml` and the cable schedule. The detector-to-damper
  arrangement is #7.
- **D-038 migration.**
  - BFD / PFD: provenance only. The `process-basic` gate passes.
  - The connector moves on P-01..P-03, P-07 and P-08 are graphics only: no item, nozzle, line number
    or DN changed (`cheme diff`).
- **Lists against sheets and control files.** 0 errors in every cross-check. The P-8102 figures are
  45 m, 10.2 kW, a 15 kW motor, shut-off 59 m and design 10 barg. They agree across the equipment
  list, the datasheet, the electrical list (line 73) and HS-8103.

## Not checked

- Tiles not read:
  - P-04 C3;
  - P-05 A1, A3, C3;
  - P-06 beyond the crop named above (it mirrors P-05);
  - P-07 A2, A3, B1, B3, C1, C3;
  - P-01 A1-B1, B3, C1, C3;
  - P-02 beyond A1 / A2;
  - P-03 (it mirrors P-02; D-038 texts only).
- Transient analyses (H-01): the arm reliefs lifting on a closure transient, the two-phase N2
  displacement, and the carrier closure shorter than its stroke.
- Vendor data:
  - P-8102: the converter-fed Ex d motor, its cooling at minimum speed and its start limit;
  - the radars of LZT-8113 / LI-8103 aimed at a 1.5 m pocket from ~20 m, their beam and the
    obstructions;
  - the regulator offset and lock-up, the check valve's cracking pressure and the cavity vents;
  - the bidirectional loading meters;
  - the B-SUB detectors and dampers.
- For named others:
  - the site N2 capacity and back-up (H-07, the trains' utility owner);
  - the SIL screening (H-06: I-801, I-805, I-809, I-810, I-811, I-n02);
  - the pocket and floor fall of T-8101 (civil);
  - the boil-off and rapid phase transition of the pocket water (the siting study).
- Outside this scope:
  - the layout, routing, 3D model, PFP and the layout-review gate (D-040);
  - the HAZOP studies (32 warnings, for their owner to restamp against `ae718797`);
  - `process/narrative.md` and `control/philosophy.md` beyond the names checked for review 9 #7;
  - the electrical design beyond the entries named above, area classification, and the fire and gas
    system.
