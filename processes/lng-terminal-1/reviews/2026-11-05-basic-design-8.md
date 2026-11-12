---
topic: design
reviewed_commit: aedd8dbdc3c575f0013f845251febb5dd289143a
scope: [pid/P-01.xml, pid/P-02.xml, pid/P-03.xml, pid/P-04.xml, pid/P-05.xml, pid/P-06.xml, pid/P-07.xml, pid/P-08.xml, equipment/equipment-list.yaml, piping/line-list.yaml, piping/special-items.yaml, control/instrument-list.yaml, control/cause-effect.yaml, control/loops.yaml, control/sequences.yaml, DESIGN.md]
basis:
  - {path: process/flowsheet.yaml, revision: aedd8dbdc3c575f0013f845251febb5dd289143a, relation: depends-on}
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: design, seventh follow-up (basic stage P&IDs P-01 to P-08, lists, C&E, loops, sequences)

## Summary

This is the independent follow-up to `2026-11-05-basic-design-7`. It reviews HEAD `aedd8dbd` on
`stage/lng-terminal-1-concept`. I did not write any of this design. The working tree was clean
during the review. The round under review:
- `fd540b21`: HAZOP H-01..H-05 revised to `709fcf20` (outside this scope);
- `0bb82928`: review records design-7 and layout-5, with their adversarial checks in
  `build/adversarial-design-r7.json` and `build/adversarial-layout-r7.json`;
- `aedd8dbd`: the response to both (D-034 design, with the loading hydraulics
  `build/r7_hydraulics.py` and the spill flows of D-034.3; D-035 layout; edits to D-008, D-011,
  D-013, D-016, D-018, D-023, D-024, D-026, D-032, D-033).

Every commit that closes a finding below (`aedd8dbd`) is HEAD itself.

Review 7 left one high, five mediums and three lows open, plus review 5 #9 (low). At HEAD, on the
drawn sheets, `cheme show` and the control files:
- **Review 7 #1 (high) is closed.** The DN 800 platform crossover LNG-4010 with its ESD valve
  XV-4107 is drawn on P-04. It runs T4A5_N3 -> XV4107 -> T4B5_N3, all DN 800. It is in the line
  list and in SEQ-LOAD S0 / S3, SEQ-HOLD S1 and SEQ-ESD. My own hydraulic calculation of every
  line-up the sequences allow confirms the recorded one: 832 kPa against the 834 kPa of D-034
  for the governing line-up, so the re-rated pumps (835 kPa) carry 12,000 m3/h at 3.4 m/s per
  line.
- Review 7 #2 to #8 are closed. Review 7 #9 is superseded by #8 of this record, because its
  part (a), D-014, was not edited.
- Review 5 #9 (low) stays open. The three accepted findings stay accepted.

The three items of the adversarial check against review 7 are answered, and the reason given for
each is sound (section "Items raised against review 7 by its adversarial check").

This pass found nine new findings: no critical, no high, three mediums and six lows. Most come
from the pump re-rating and the new crossover.
1. **#1 (medium).** The re-rated pumps' shut-off now reaches ~12-12.6 barg at the carrier
   manifold, against a carrier design pressure that the design never states. The back-pressure
   trip has no set point.
2. **#2 (medium).** The flowsheet's BOG design case (56.5 t/h) needs the installed spare
   compressor. The D-010 sizing rule no longer holds.
3. **#3 (medium).** P-8102 is sized for a 12.5 m pit, but T-8101 is now 19.5 m deep. It is
   specified in carbon steel at 40 degC, on the floor of an LNG impoundment.
4. **#4 to #9 (low):**
   - #4: no head margin on the pumps;
   - #5: XV-4107 has no position proof;
   - #6: the Berth 1 cooldown line-up;
   - #7: the post-reset hold of I-n14 rests on a timer;
   - #8: stale texts;
   - #9: rain in T-8102 during a transfer.

Verdict: **ready for basic-engineering issue on the design topic**. No critical or high finding
is open. Before issue or at detail engineering:
- close or disposition the three mediums, recording the reason;
- close the six lows and review 5 #9.

The stage sign-off still needs a current layout review and a human approver. The HAZOP studies
need their restamp (20 `hazop-input-changed` and 9 `hazop-unknown-tag` warnings, outside this
scope). Merge pending.

## Branch diff

`cheme diff origin/main --list`: every sheet is new on the branch. The summary lines are:

```
pid/P-01.xml: (sheet added)
pid/P-02.xml: (sheet added)
pid/P-03.xml: (sheet added)
pid/P-04.xml: (sheet added)
pid/P-05.xml: (sheet added)
pid/P-06.xml: (sheet added)
pid/P-07.xml: (sheet added)
pid/P-08.xml: (sheet added)
process/BFD.xml: (sheet added)
process/PFD.xml: (sheet added)
```

The changes of this round (`cheme diff 0bb82928 --list`):
- **P-04.** Added: Line_LNG4010 [LNG-4010], tees T4A5 / T4B5, BallValve XV4107 [XV-4107] and
  Inst_UZ4107 with its actuating system. Changed: LNG-4001 / LNG-4002. Moved: T4A4 / T4B4 and
  the two off-page connectors. Changed: PI-4105 / 4106 and TI-4103 / 4104.
- **P-05.** HS5100 and HS5107 are removed. Added: HS-5100A/B/C, HS-5107A/B/C, HS-5109 and
  UY-5135..5138. Changed: AI-5126, XA-5130A/B and XS-5108.
- **P-06.** The same with the 6xxx tags.
- **P-08.** W-8001 is removed. Changed: LI-8103, TSL-8102, W-8002, P-8102 (nozzle removed) and
  T-8101 (nozzles removed).
- **BFD / PFD.** Regenerated (S2, S3, S5..S11, S13, S14, E1, E2), with no `generated-sheet-drift`.
- **P-01, P-02, P-03, P-07.** No change. Only the notes of their scripts changed.

Every change has its reason in D-034 / D-035 and in PROGRESS.md. No changed plant item is
`not drawn`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-design-8#1 | P-05, P-06, C&E I-502 / I-602, instrument list, design basis, DESIGN.md D-011 / D-023 / D-034 | P-2101A-D / P-3101A-D shut-off against the carrier; PZT-5103 / PZT-6103 | D-034 re-rated the loading pumps to 191 m. D-011 and D-023 check the shut-off (1.25 x 191 m, ASSUMED) only against the shore's 15 barg. My numbers, with the tank full (41 m), at its +29 kPa(g) design and at 445 kg/m3 (scratch `rev8_hyd.py`): 12.5 barg at the pump, ~12.6 barg at the platform header, and ~12.0-12.6 barg at the carrier manifold, for a manifold between ~11 m above the tank floor and deck level. With a shut-off ratio of 1.35 the figures are 13.3 / 13.4 / 12.9 barg. Before D-034 they were ~9.3 barg at the pump and ~8.8 barg at the manifold. Neither `process/design-basis.yaml` (only "delivery 350 kPa(a) at the ship manifold") nor DESIGN.md states the carrier's cargo-piping or manifold design pressure, which is commonly 10 barg on LNG carriers (to be confirmed against S-01 and the ship-shore compatibility). PZT-5103 / PZT-6103 have no PAHH set point. A ship-side ESD valve closure is an ordinary ESD event. If it happens with the linked ESD not reaching the shore, the carrier's manifold piping sees up to the shut-off plus the closure surge. Only I-502 / I-602 protect it, and they have no set point and no basis. The re-rating turned an inherently low shut-off into one that needs that trip. It is medium, not high: the link is fail-safe (a link that is not healthy trips I-n01) and I-502 exists. What is missing is the interface limit and the set point, and no deferral is recorded. | medium | open | State the carrier manifold design pressure (S-01 terminal information guide or the compatibility study) in the design basis and D-016. Set PZT-n103 PAHH below it with its response time, and check the shut-off plus the closure surge of a ship valve against it (holds H-01 / H-02). Or specify a lower shut-off ratio, a flatter curve, for the loading pumps. |
| 2026-11-05-basic-design-8#2 | DESIGN.md D-009 / D-010 / D-026.6, equipment list K-7101A-C / D-7101, flowsheet S5 / S6 / S14 / S9, special items PSV-2131 / 3131 | BOG compressors 3 x 27 t/h against the 56.5 t/h loading case | The flowsheet's loading case (`cheme process streams --case loading`) sends S14 = S9 = 56,538 kg/h to the compressors, with S5 / S6 at 52.5 t/h. D-010's own rule, "50 % of the loading case + 10 %", gives 31.1 t/h per machine. The K-7101A-C equipment-list notes still say that rule gives 27 t/h, which is no longer true. Two machines make 54 t/h, so the design case needs the installed spare (D-026.6: "covered by the installed spare"). D-7101 is sized at ~54 t/h. The stated reason is that no line-up returns more than ~38 t/h through the arms. That contradicts the flowsheet keeping 52.5 t/h as the design case of the BOG system (D-009) and as the PSV-2131 / 3131 relief case. Either the flowsheet case is not the design case, or the compressors lack N+1 at it. The compressor datasheet, a basic-engineering deliverable, rests on a rule that its own case no longer meets. It is medium: the shortfall goes to the flare through PIC-1110 / PV-1110, the tank PSVs stay behind it, and the deferral to carrier data is recorded. | medium | open | Decide the BOG design case. Either: (a) restate S5 / S6 as the arm-limited return (line-up (b) ~38 t/h; line-up (a) ~23.5 t/h with the carrier's gas combustion unit) and keep 52.5 t/h only as the relief envelope; or (b) re-rate K-7101A-C to ~31 t/h and recheck D-7101. Make D-009, D-010, the K-7101 notes and datasheets, and the D-7101 notes say the same. |
| 2026-11-05-basic-design-8#3 | P-08, equipment list P-8102 / T-8101, datasheets P-8102 / T-8101, C&E I-801, electrical list, zones Z-HA-SUMP-T8101 | Submersible P-8102 on the floor of the LNG impoundment T-8101 | The D-034.8 arrangement closes review 7 #6, with no suction lift and no wall penetration. Four gaps remain or are new. (a) Head: the P-8102 datasheet and the electrical list are sized for "the 12.5 m pit", but T-8101 is now 19.5 m deep (equipment list, datasheet T-8101 at 3,920.7 m3, Z-HA-SUMP-T8101; D-035.2). The static rise to the PR8 rack is then ~26.6 m, and with the ~10.2 m at the battery limit and ~6 m friction the duty is ~43 m, against the 36 m rated. At the rated head the pump cannot deliver 50 m3/h from the floor. A ~43 m pump's shut-off also exceeds the 5 barg design. (b) Material: the equipment list gives CS, design 40 degC, for a machine at the first point that any spill reaches, where the riser W-8002 and the casing would see -160 degC. (c) Ignition and trips: the motor and its cable are inside the pit, which is zone 2 inside (Z-HA-SUMP-T8101), but no Ex or cold rating is stated. I-801 "stops" P-8102 on TSL-8102 and does not say that it isolates the feeder. TSL-8102 hangs "to the pit floor beside P-8102", and its height against the pump intake is not given, so it is not shown to trip before the pump draws LNG. (d) W-8002 has no check valve and no isolation: there is back-flow from the oily water system, and the pump has to be pulled on its guide rail (tile `build/P-08_tile-C1.png`). It is medium, as review 7 #6 was. Rainwater removal from an LNG impoundment is safety-relevant (rapid phase transition), and I-801 and the foam stay in place. | medium | open | Re-rate P-8102 (head, shut-off and design pressure) for the 19.5 m pit and correct the datasheet and the electrical list. Specify the material and design temperature for LNG exposure (SS, -170 degC), or state the pump as sacrificial with the riser in SS. Give the motor an Ex rating for the pit zone, suitable for cold. Make I-801 isolate the feeder, and set the TSL-8102 tip below the pump intake. Add a check valve and an isolation valve on W-8002 above the cover. |
| 2026-11-05-basic-design-8#4 | DESIGN.md D-011 / D-034.1, equipment list and datasheets P-2101A-D / P-3101A-D, electrical list | Loading pump rating 835 kPa against the 834 kPa governing need | The rating equals the calculated need of the governing line-up (T-3101 alone to Berth 1), with only the 25 kPa control allowance. My base set reproduces 832 kPa. A pessimistic but plausible set needs 968 kPa (222 m): tee branch K 1.3, FV wide open 0.6, check valve 2.0, strainer at alarm 3.0, swivel 0.3, a loop every 80 m, a 45 m arm and 50 kPa control. The governing line-up would then reach ~10,900 m3/h, not 12,000, and S4 would time out. The arm losses are vendor data (H-02). The motors (928 kW) equal the shaft power at the rated point, while D-034.3 credits run-out at 14,400 m3/h. Not a hazard. | low | open | Add a stated head margin (for example 10 % on the dynamic losses) or record the reduced rate of the governing line-up in SEQ-LOAD S4. Size the motors for the end of the curve. |
| 2026-11-05-basic-design-8#5 | P-04, instrument list UZ-4107, SEQ-LOAD S0 / S3, SEQ-HOLD S1, DESIGN.md D-034.3 | XV-4107 open and closed states | XV-4107 has no position switch (`cheme show XV-4107`: UZ-4107 only). Yet the complete conditions of S0 / S3 ("XV-4107 open") and SEQ-HOLD S1 ("XV-4107 closed") use its state. The spill basis of D-034.3 for a leak upstream of XV-n101, one line of ~1,020 m3, rests on XV-4107 closing on ESD-1. If it fails to close, both lines (~2,050 m3) feed the leak, and nothing reveals it. A spurious closure in loading is revealed only through FIC-4102. | low | open | Add ZSC-4107 (and ZSO-4107) or the actuator's position feedback, alarm a discrepancy with UZ-4107, and use it in the complete conditions. |
| 2026-11-05-basic-design-8#6 | control/sequences.yaml SEQ-LOAD S3 (Berth 1 mirror) | Cooldown line-up at Berth 1 after the first ESD-1 test | SEQ-LOAD says "Berth 1 runs the same with the 6xxx tags". At Berth 1 the direct line is B, and line A reaches it only through XV-4107. The first S3 ESD-1 test closes XV-4107, and the sequence reopens it only after the second test, so FIC-4101's 500 m3/h cooldown has no path between the tests. P-2102's flow then goes through XV-4106 and line B, with FV-4102 still fully open in manual from SEQ-HOLD. The cooldown rate is uncontrolled, against the "cool slowly" requirement of S3. At Berth 2 the line-up works, because line A is direct. | low | open | Write the Berth 1 line assignment into SEQ-LOAD: cooldown on FIC-4102 / line B, or reopen XV-4107 after the first test. Put FIC-4102 in auto at its cooldown setpoint. |
| 2026-11-05-basic-design-8#7 | C&E I-511 / I-512 / I-514 (I-611 / I-612 / I-614), SEQ-LOAD S1, P-05 / P-06 | Post-reset hold of the O2 reject; reset condition; fast-loop isolation | The 30 min hold rests on an ASSUMED minimum carrier return of ~0.9 m3/s "agreed with the carrier" (I-511 logic text). No flow on the vapour return is measured. Below that flow the timer ends with the slug still in the line. AI-4133's response and its 10 s vote then let the leading part reach the flare before I-514 re-trips, and D-034.4 says the slug goes "never to the flare". The reset permissive (both AI-n126 cells below 5 vol %) exists only in notes, while the C&E reset field says "manual". The fast-loop isolation used during the S1 leak test is neither tagged nor drawn. | low | open | End the hold when AI-4133 / 4134 has seen the slug pass (O2 rise and fall), or on a totalised return flow, not on a timer. Write the reset condition into I-514 / I-614. Tag the fast-loop isolation, in the analyser package, as a permissive of the leak test. |
| 2026-11-05-basic-design-8#8 | DESIGN.md D-009 / D-010 / D-014 / D-022 / D-023 (2) / D-034.3, datasheets LA-5102 / LA-6102, equipment list D-8101, electrical list, instrument list UY-n135..n138, C&E I-510 / I-610, flowsheet S3 | Stale or inconsistent texts after D-034 | The texts below disagree with the design at HEAD. (a) Design decisions: D-009 says the carrier returns 45.6 t/h; D-010 gives 27 t/h as "50 % of the loading case + 10 %" with a 3.5 t/h spray; D-022 says 132 m and ~640 kW; D-023 (2) says 45.6 t/h; none carries a correction note. D-014 still says the hybrid arm "is the spare vapour arm" (review 7 #9 (a) not done). The D-034.3 table says "~12 m fall, D-013", against D-013 / D-035.8 at ~3.3 m. (b) Datasheets and lists: LA-5102 / LA-6102 give the carrier return as 45.6 t/h; the electrical list's motor-starting note says "0.64 MW in-tank" pumps and P-8102 is given "for the 12.5 m pit"; the D-8101 notes give the compressor-trip relief as ~54 t/h. (c) Control files: the UY-n135..n138 notes say "commanded by C&E I-507", but it is I-510 / I-610; the I-510 / I-610 cause text keeps the template placeholders "I-{n}03 and I-{n}07". (d) Flowsheet: S3, "LNG at the jetty", reads 858.9 kPa(a) because DP_JETTY lumps in the column, headers, crossovers and loops; that is not the ~626 kPa(a) at XV-n101 that D-023 uses. | low | open | Add "corrected by D-034" notes to D-009, D-010, D-022 and D-023 (2), and edit D-014 to the D-032.7 wording and D-034.3 to ~3 m. Correct the LA-n102 datasheets, the electrical-list notes, the D-8101 notes, the UY notes and the I-n10 cause text. Split the jetty pressure in `scripts/terminal_sizing.py` so that S3 is the berth header pressure. |
| 2026-11-05-basic-design-8#9 | P-08, equipment list T-8102, SEQ-LOAD permissives | T-8102 water removal during a transfer | T-8102 has no fixed pump. It is checked dry before each transfer and after heavy rain. During a transfer of ~15-20 h nothing removes water. The ~87 m3 left below the inlet is ~93 mm of rain on its ~935 m2 catchment, which is within a heavy rain day at the site. Any standing water then meets a spill, which the equipment list and D-034 say must not happen (rapid phase transition). The design volume still holds. | low | open | State the rule for rain during a transfer (suspend, or pump down with the portable pump while TSL-8104 is normal, above a stated rainfall), or give T-8102 a fixed submersible pump with the low-temperature trip that P-8102 has. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-design-7#1 | DN 250 platform crossover was the only path from loading line B to Berth 2 | high | closed aedd8dbd | **Drawn.** `cheme show LNG-4010`: one DN 800 segment T4A5_N3 -> XV4107 (BallValve, UZ-4107) -> T4B5_N3; tiles `build/P-04_tile-A3.png` / `B3.png`. Line list LNG-4010 DN800 Class 150. S0 opens XV-4107 and closes XV-4103; SEQ-HOLD closes XV-4107; I-501 / I-601 close it. **Own hydraulics** (scratch `rev8_hyd.py` on the routed lengths of `build/r7_routes.json`, Colebrook iterated, independent of `build/r7_hydraulics.py`): (a) at 12,000 m3/h needs 808 / 803 kPa (T-2101 alone to Berth 2 / Berth 1), 827 / 832 kPa (T-3101 alone) and 767 / 762 kPa (both tanks); (b) at 8,000 m3/h needs 674 kPa at most; holding at 500 m3/h with XV-4107 closed needs ~52 kPa against P-2102's 262 kPa. 3.40 m/s per trestle line, 6.8 m/s in the pump and berth headers, 9.3 m/s per arm. **Recorded script checked:** inputs plausible (rho 445, 0.115 mPa s, 0.045 mm, IDs, K values, loops every 100 m, a 54 m column, a 40 m arm, a 366 kPa fixed part from 350 kPa(a), 115 kPa(a) and 30 m); its table reproduces D-034's 834 kPa (191.2 m). The DN 250 alone would be 32.9 m/s and 576 kPa. **Residuals:** #1, #4, #5, #6. |
| 2026-11-05-basic-design-7#2 | Berth O2 analyser downstream of the valves it closes; reset undefined | medium | closed aedd8dbd | `build/P-05_tile-B3.png`: AI-5126 senses BOG-5001 between the arm riser and XV-5122. AI-6126 is the same (`build/P-06_tile-B3.png`). I-511 / I-512 are blocked for 30 min after a reset of I-514 and while AI-4133 reads O2 at or above 5 vol % (logic text). The I-514 notes give the reset on both AI-5126 cells. Residual: #7. |
| 2026-11-05-basic-design-7#3 | 'No carrier connected' mode had no exit | medium | closed aedd8dbd | The I-501 / I-601 XS-n100 state trips once the mode has ended because an arm left its stowed position. The mode ends on a healthy link. I-508 / I-608 keep UZ-n101 de-energised unless the link is in carrier mode and healthy. The S1 complete condition includes `XS-5100: in carrier mode and healthy`. D-016 marks ZS-n15x stowed as ASSUMED (H-02). The alarm I asked for is no longer needed, since the mode now ends by itself. |
| 2026-11-05-basic-design-7#4 | Coupler release on a fixed timer; arm isolations not closed | medium | closed aedd8dbd | I-507 now closes XV-5121 / 5123 / 5124 at set speed and XV-5122 / 5125. I-510 releases UY-5135..5138 (drawn, `build/P-05_tile-C1.png`) on both ERS valves proven closed, or at 7.5 s (1.5 x the vendor's closure time, H-02), never before the I-507 commands. D-016 restates the spill: ~15 m3, onto the water first. The UY note text is in #8. |
| 2026-11-05-basic-design-7#5 | ERS single causes outside the two supplies | medium | closed aedd8dbd | (a) I-509 / I-609: HS-n109 is enabled only with ZSC-n101 closed, UZ-n101 de-energised and all arms stowed, hard-wired. (b) The I-507 notes state separate output modules and give the logic solver to H-06. (c) XA-n130A / B now include each solenoid circuit's line monitoring, inside the I-n01 transfer gate. (d) UPS-A / UPS-B are in `electrical/electrical-list.yaml` lines 41-42, with the feeders F-ERS-5100A/B and 6100A/B. |
| 2026-11-05-basic-design-7#6 | P-8102 at grade could not lift from the 10.5 m pit; pit-bottom suction | medium | closed aedd8dbd | P-08 (`build/P-08_tile-C1.png`): P-8102 is drawn inside T-8101, W-8001 and T-8101 N3 are removed, and LI-8103 / TSL-8102 come through the cover. No suction lift and no wall penetration. The head for the 19.5 m pit of D-035, the material and the trips are the new #3. |
| 2026-11-05-basic-design-7#7 | One tag for three ESD push buttons, wired in parallel | low | closed aedd8dbd | HS-5100A/B/C, HS-5107A/B/C (and the 6xxx tags) are drawn (`build/P-05_tile-C1.png`, `build/P-06_tile-C1.png`). They are causes of I-n01 / I-n03 as "normally closed contact open or input line fault", and the instrument-list notes say NC and line-monitored. The gate `berth-esd-causes-on-pid` passes. |
| 2026-11-05-basic-design-7#8 | Vapour arm N2 test connection not named | low | closed aedd8dbd | SEQ-LOAD S1 names it: "the arm package's test connection between LA-5102 and XV-5122". The P-05 / P-06 note reads "Arm vents, drains, vapour arm N2 test point: arm package; O2: AI-5126" (`build/P-05_tile-C2.png`). |
| 2026-11-05-basic-design-7#9 | Stale texts after D-032 / D-033 | low | superseded by 2026-11-05-basic-design-8#8 | Done: (b) the P-05 / P-06 note; (c) the P-08 note and the T-8101 service; (d) T-8102, with one statement in the equipment list and on P-08 (`build/P-08_tile-C2.png`). Not done: (a) D-014 still says "is the spare vapour arm", so it is carried in #8. |
| 2026-11-05-basic-design-5#9 | Deferred safety inputs not registered as issues, holds or TQs | low | open | `cheme issues --all` lists one issue (#362) and no hold or TQ. D-034.11 leaves the holds to the project owner. |
| 2026-11-05-basic-design-3#5 | LIC-8101 duty/standby drawn as a chain through HS-8101A | low | accepted: the standby no longer depends on the chain for the hazard; I-802 starts both pumps on LZT-8105 and I-803 stops both; availability of the level band only. By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged: the P-08 KO drum pumps are unchanged (`build/P-08_tile-B2.png`), and C&E I-802 / I-803 are unchanged. |
| 2026-11-05-basic-design-3#6 | PZT-7113 1oo1 stops every running compressor | low | accepted: a spurious trip sends the BOG to the flare, a production and flaring loss with no hazard; the voting is left to the SIL screening (now hold H-06). By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged: P-07 has no change, and neither do C&E I-705A-C. |
| 2026-11-05-basic-design-2#10 | No relief device sized against its governing case | medium | accepted: relief sizing is a detail-stage calculation; D-025 records the cases, and D-026.8, D-026.14, D-028, D-030, D-032 and D-034 add the FO-1117 blow-by, the D-7101 fire, the air-failure residual, the spurious ERS closure, the XV-4101 / 4102 / 4107 residual and the open rundown blocked-outlet case. By Claude (independent review agent), for the human reviewer to confirm at sign-off | The PSV-5131 / 6131 relief cases now quote the D-034 recheck (one ERS valve ~11 barg, every ERS valve ~23 barg). PSV-2131 / 3131 quote the 52.5 t/h envelope. |

## Items raised against review 7 by its adversarial check

I judged these on the drawn sheets and the control files at HEAD
(`build/adversarial-design-r7.json`).

1. **Missed medium: the spill design basis took per-line or per-arm flows.** Answered by the
   D-034.3 table, D-018 (h) and the T-8101 / T-8102 dimensions. The reason is sound. My
   arithmetic, on D-034.3's own figures:
   - Tank area: 14,400 m3/h for 10 min is 2,400 m3. T-8101 is 16 m x 19.5 m = 3,920.7 m3, and
     2,400 m3 stands 11.94 m above the floor, at -7.56 m. That matches the datasheet.
   - Platform: 12,000 m3/h for 30 s is 100 m3, plus 41.7 m3 over the 25 s run-down, plus 27 m3
     of drainable header and arm inventory: 168 m3.
   - T-8102: 6 m x 13 m holds 367.6 m3, with 257 m3 below the -3.91 m inlet.

   One observation, not a finding: the 10 min is the default duration for an impounding area.
   The design states that it has no automatic stop of the loading pumps on a tank-area release.
   A tank-area fire and gas cause of ESD-1, like XS-n108 on the platform, would justify a
   shorter basis; that is for the fire and gas design.
2. **Missed low: the consequences of #1 were not all listed.** Answered. D-023 is rechecked, and
   its numbers reproduce with `build/r7_hydraulics.py`: +322 kPa slow closure, ~8.5 barg peak,
   one ERS valve ~11 barg, every ERS valve ~22.6 barg. The S4 operator text and D-018 (h)
   follow. The reason is sound. My check finds that S4 completes, but with no margin (#4).
3. **Missed low: the T-8101 suction drew differently on P-08 and in the layout.** Answered and
   sound. W-8001 and N3 are removed, and the nozzles come through the cover (P-08 tile C1). The
   H-05 study still names W-8001 (`hazop-unknown-tag`); that is for the study's owner.

## Drawing

`cheme validate` drawing lines at `aedd8dbd`:

- P-01, P-02, P-03, P-05, P-06: every rule 0 (line-through-label, line-crossing, label-overlap,
  label-far-from-owner, text-outside-frame, title-text-overflow, line-through-symbol,
  line-through-valve, line-on-pipe, line-not-orthogonal).
- P-04: 0 line-crossing (+2 accepted: BOG-4011 x LNG-4002 and BOG-4015 x LNG-4002, D-026.11),
  all other counts 0.
- P-07: 0 line-crossing (+2 accepted, D-025), all other counts 0.
- P-08: 0 line-crossing (+1 accepted, D-026.11), all other counts 0.

The accepted crossings are unchanged since review 7, and I agree with their reasons.

Tiles rendered with `cheme render pid/<sheet>.xml --png --tiles auto` (3x3 at scale 8):
- P-04: A1-C3, all nine read. LNG-4010 DN 800 is labelled, with XV-4107 / UZ-4107 and XV-4103 /
  HS-4103 on the verticals (A3 / B3). The P-5101 / P-6101 returns enter LNG-4003 on either side
  of XV-4103. The new loading note is read in B3.
- P-05: A1-C3, all nine read. AI-5126 is on the arm side of XV-5122 (B3). The rows HS-5100A/B/C,
  HS-5107A/B/C, XS-5108, XA-5130A/B and UY-5135..5138, HS-5109 are in C1 / C2, with their notes.
- P-06: B1, B2, B3, C1 and C2 read. They mirror P-05 with the 6xxx tags.
- P-08: A1, B1, B2, C1 and C2 read. P-8102 in the T-8101 pit and the T-8102 note are read in C1 /
  C2.

No overlap or ambiguous tag was seen in the tiles read.

## Mechanical checks (non-layout)

- `cheme validate`:
  - 90 files, 0 errors, 29 warnings. All 29 are in safety/hazop, outside this scope: 20
    `cheme.hazop-input-changed` (H-01..H-05) and 9 `cheme.hazop-unknown-tag` (HS-5100 / HS-5107 /
    HS-6100 / HS-6107 in H-03, W-8001 in H-05).
  - The last line compares 10 sheets and 25 lists. It cross-checks equipment, lines and DN,
    instruments, piping items, interlocks, control records, tags in texts, HAZOP, layout,
    datasheets and review records. None reports an error or warning in scope.
- `cheme check --stage basic`, before this record:
  - FAIL design-review: review 7 "changed since 709fcf201fb0".
  - FAIL layout-review, outside this scope.
  - Every other gate ok. That includes the new `platform-crossover-on-pid` and
    `ers-release-and-test-on-pid`.
- `cheme validate --only 'cheme.review-*'` after writing this record: 0 errors.

## Checked and fine

- **Shut-off against the shore design.** At 12.5-13.4 barg (shut-off ratio 1.25-1.35, tank
  full), the shore is inside its 15 barg design: the pump header, trestle lines, LNG-4010 /
  LNG-4003, the berth header, SR-n102, the arms and ERS valves (LA design 15 barg), D-n101 / P-n101
  (15 barg) and LNG-2002 behind CV-2122. Every liquid PSV (PSV-2141 / 3141, 4111..4114, n131,
  n171..n174, n118) is set at 15 barg, so the shut-off is at most ~89 % of set. The carrier is
  the exception (#1).
- **XV-4107 failure modes.**
  - Fail closed, with the accumulator, non-return valve and speed controller of D-016, so I-804
    trips ESD-1 first.
  - A spurious closure at set speed with the pumps running: line B dead-ends at the platform but
    stays open to line A through XV-4106. Its pressure rises by ~255 kPa (my check: 2 rho L v /
    t = 2 x 445 x 2,313 x 3.4 / 25 = 280 kPa), then toward the shut-off: inside 15 barg. The
    closure at spring speed is in check case (4) under H-01.
  - When closed, no section is trapped: both sides stay open to their lines, and PSV-4111 /
    4112 cover each line.
- **SEQ-LOAD / SEQ-HOLD line-ups.** S0 opens XV-4107 and closes XV-4103. The S3 ESD-1 tests
  close XV-4107, and it is reopened after the second test. SEQ-HOLD closes XV-4107 and opens
  XV-4103, so circulation runs out on line A and back on line B (52 kPa against P-2102's 60 m).
  In loading, P-2102 is held on its check valve by the loading header (its ~6 bar(a) shut-off is
  below ~9.5 bar(a)), and the spray then comes from the loading header through LNG-2002, which
  matches flowsheet S7 at 949.5 kPa(a). The Berth 1 mirror is #6.
- **I-n08 / I-n09 / I-n10 / I-n14.** I compared all of I-508..I-510 with I-608..I-610, and
  I-511..I-514 with I-611..I-614: they differ only in tags. I-508 acts only on the UZ-n101 open
  command (non-latching). I-509 ends an enabled test when any condition is lost. I-510 never
  releases before the I-507 commands. In no state are both tank-end vapour valves commanded
  closed.
- **Per-station push buttons.** Each is its own NC, line-monitored SIS input, and an input fault
  trips (fail-safe).
- **Flowsheet consequences.** S2 / S7 949.5 kPa(a) = 115 + 835. E1 3,904 kW is 4 x 976 kW at
  the motor. The BFD / PFD are regenerated with no drift, and process-basic passes.

## Not checked

- Tiles not read:
  - P-06 A1-A3 and C3;
  - P-08 A2, A3, B3 and C3 (an unchanged region);
  - P-01, P-02, P-03 and P-07 (no sheet change since `709fcf20`; reviews 5 to 7 read them).
- Transient analyses, for the designer and the vendors (holds H-01, H-02):
  - the pump trip and column separation at the tank roof after the pump stop;
  - the ship-valve closure against the shore pumps (#1);
  - the spring-speed closure of XV-4101 / 4102 / 4107;
  - the ERS closures.

  My surge figures are the order-of-magnitude estimates of D-023.
- Vendor data for the design: the arm losses and envelope; the in-tank pump curve, shut-off ratio
  and run-out; the BOG compressor rating.
- The SIL screening (H-06): AI-n126 / AI-4133 voting, ZSC-n101 / ZSO-n122, the ERS solenoids and
  the logic solver.
- Outside this scope:
  - the layout, routing, 3D model, the D-035 spill collection and radiation screening, and the
    layout-review gate. T-8101 / T-8102 were checked only for their dimensions, datasheets, P-08
    and the pump.
  - the HAZOP studies: their 29 warnings remain, for their owner to restamp against `aedd8dbd`
    and to retag.
  - `process/narrative.md` beyond its transfer paragraph, and `control/loops.yaml` beyond FIC-4101
    / 4102.
  - the electrical design beyond the UPS and motor entries named above, area classification,
    materials beyond P-8102, the fire and gas system, and the vendor packages.
