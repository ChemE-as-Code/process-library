---
topic: design
reviewed_commit: 79d5c7ad9fef48cdb32fd165ad0294e2598c50b4
scope: [pid/P-01.xml, pid/P-02.xml, pid/P-03.xml, pid/P-04.xml, pid/P-05.xml, pid/P-06.xml, pid/P-07.xml, pid/P-08.xml, equipment/equipment-list.yaml, piping/line-list.yaml, piping/special-items.yaml, control/instrument-list.yaml, control/cause-effect.yaml, control/loops.yaml, control/sequences.yaml, DESIGN.md]
basis:
  - {path: process/flowsheet.yaml, revision: 79d5c7ad9fef48cdb32fd165ad0294e2598c50b4, relation: depends-on}
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: design, fifth follow-up (basic stage P&IDs P-01 to P-08, lists, C&E, loops, sequences)

## Summary

This is the independent follow-up to `2026-11-05-basic-design-5`. It reviews HEAD `79d5c7ad` on
`stage/lng-terminal-1-concept`. I did not write any of this design. The working tree was clean
during the review. The round under review:
- `94e503de`: HAZOP H-01..H-05 revised to `f5d925f6` (outside this scope);
- `262683b4`: review records design-5 and layout-3, with their adversarial checks in
  `build/adversarial-design-r5.json` and `build/adversarial-layout-r5.json`;
- `79d5c7ad`: the response to both (D-030 design, D-031 layout, and edits to D-016, D-018,
  D-023, D-026, D-028, D-029).

Every commit that closes a finding below (`79d5c7ad`) is HEAD itself.

Review 5 closed no high and left five medium and four low findings open, plus review 1 #23
(medium). At HEAD, on the drawn sheets and the control files:
- 9 of these 10 are closed: review 5 #1 to #8 and review 1 #23.
- Review 5 #9 (low) stays open. The holds of D-030 are a table in DESIGN.md, not issues that a
  gate can see.
- The three accepted findings stay accepted.

The five items of the adversarial check against review 5 are closed as well:
- The selection valves XV-1106..1109 have the 30 s closure, and permissive I-103 blocks their
  close command.
- The manual and fire-and-gas causes are written into the I-501 / I-601 logic.
- ZSO-5122 / ZSO-6122 are drawn on the vapour arm valves and are ESD-1 causes.
- F-POWER now covers the ERS supplies.
- The berth that is transferring is tripped through its own link when the other berth's ESD-1
  stops the shared pumps. There is no latch-up between I-501 and I-601.

The fix introduced or exposed eight new findings, two medium and six low. None is critical or
high.
1. **#1 (medium).** The "liquid transfer" state now sets the arming of I-514 / I-614 and of the
   new I-501 / I-601 causes. It rests on the regulatory flow loops FIC-4101 / FIC-4102 and on a
   DCS open command. When one loading line carries the flow, as in the S3 cooldown, a single
   FIC-4101 transmitter failing low drives FV-4101 open. In the same fault, it disarms the
   ESD-1 causes of the berth and arms the O2 reject, which can then close the vapour return
   while LNG flows.
2. **#2 (medium).** The ERS valves now use 2oo2 de-energise-to-trip solenoids. Both channels
   are fed from the one UPS, so "both channels lost together" is still a single cause. D-023 (5)
   itself says that a spurious closure in 5 s at full flow can exceed the 15 barg design. On
   demand, either solenoid sticking keeps the valve open. The couplers release only once the
   valves are proven closed, so the same stuck solenoid also blocks the arm release on a
   drift-off. No fallback is stated.

Both medium findings have a safeguard behind them and sit inside a recorded hold (H-01, H-02,
H-06). Neither leaves a credible hazard unprotected at the basic stage.

The holds H-01..H-06 of D-030 are legitimate deferrals of analysis and vendor data. Each names
its case and the design change it may trigger. Two parts of H-02 / H-06 are basic-design
choices, not vendor data: the supply arrangement of the ERS solenoids and the independence of
the arming input. They are new #1 and #2.

Verdict: **ready for basic-engineering issue on the design topic**. No critical or high finding
is open. Before detail engineering, close or disposition:
- the two medium findings;
- the seven open low findings: new #3 to #8 and review 5 #9.

Merge pending. The layout-review gate is outside this scope.

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

The changes since review 5 (`cheme diff f5d925f6 --list --verbose`):
- P-01: notes 4, 8 and 9.
- P-02: `Inst_ZSC2123` added (ZSC-2123 sensing XV-2123); note 2.
- P-03: `Inst_ZSC3123` added; note 2.
- P-04: note 4.
- P-05: `Inst_ZSO5122` added (ZSO-5122 sensing XV-5122); notes 3 to 9 and 11.
- P-06: `Inst_ZSO6122` added; notes 3 to 9 and 11.
- P-07 / P-08: no change.
- BFD / PFD: S5 description and label.

The control and list changes (`git diff 262683b4 79d5c7ad`) are:
- the C&E: I-103, I-205 and I-305 new; I-201 / I-301, I-501 / I-601, I-507 / I-607, I-514 /
  I-614, I-506 / I-606 and I-804 changed;
- the instrument list, sequences, philosophy (F-AIR, F-POWER), special items and flowsheet (S5);
- a new gate, `return-and-vapour-arm-switches-on-pid`.

Every change has its reason in D-030 and in PROGRESS.md. No changed plant item is `not drawn`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-design-6#1 | C&E, P-04, P-05, P-06, sequences | I-501 / I-601 (transfer-gated causes), I-514 / I-614 (arming); FIC-4101 / FIC-4102, FV-4101; XV-5101 / XV-6101 open command; SEQ-LOAD S3 | The D-030 fix defines "liquid transfer at Berth 2" as XV-5101 open command and (FIC-4101 or FIC-4102 above 50 m3/h). I-514 is armed on the complement. Four I-501 causes count only inside that state: ZSO-5122 not open, the 2oo2 O2 high-high, the ERS supply loss and I-601 tripped. FIC-4101 / FIC-4102 are the regulatory flow loops of the loading lines (P-04 tiles A2 and B2; loops.yaml). Each measures one line and controls it through FV-4101 / FV-4102. The open command is a DCS state, and XV-5101 has no position switch. When one line carries the flow, a single fault defeats the state. In SEQ-LOAD S3, FIC-4101 controls the 500 m3/h cooldown from P-2102 alone, so FIC-4101 failing low is enough. That one failure does three things: (1) FIC-4101 drives FV-4101 open, so the cooldown flow rises; (2) it disarms ZSO-5122 and the O2 high-high as ESD-1 causes; (3) it arms I-514. An O2 high-high on AI-4133 then closes XV-5122 and XV-5125 while LNG still flows to the carrier, which is the case review 5 #4 closed. A spurious XV-5122 closure goes undetected as well. The same sensor is the initiating fault and the disabled safeguard. The SIL screening (H-06) does not list this dependence. Two independent events are needed for the hazard, and the carrier's own pressure control, relief and ESD remain, so it is medium, not high. | medium | open | Base the transfer state on safety-system inputs that are independent of the loops: XV-5101 / XV-6101 not proven closed (add ZSC-5101 / ZSC-6101), or that alone. If a flow term is wanted, use a dedicated flow switch, or two transmitters that are not the control loops. Write the chosen inputs as tags in the C&E rather than as text. Add "BPCS measurements used in the arming of I-501 / I-514" to H-06. |
| 2026-11-05-basic-design-6#2 | DESIGN.md D-016, D-023 (5), philosophy F-POWER, C&E I-507 / I-607, instrument list UZ-n13x / n14x | ERS solenoids (2oo2, de-energise-to-trip), solenoid supply, coupler release; H-01, H-02 | D-016 and F-POWER now give each ERS valve two de-energise-to-trip solenoids in a 2oo2 arrangement, both fed from the UPS of the ESD logic. That removes the single coil, wire or output fault of review 5 #3. Two gaps remain, and both are basic-design choices, not vendor data. (a) Spurious side. "Both channels lost together" still follows one fault: the UPS output, a shared distribution breaker or fuse, or the HPU control supply. D-023 (5) states that the resulting closure in 5 s at full flow is about 1.2 times 2L/a and "can exceed the 15 barg design". The 2oo2 vote does not cover this most likely cause of a spurious closure. (b) Demand side. Under 2oo2, either solenoid failing to vent keeps the ERS valve open on a real ESD-2. That makes a dangerous failure on demand about twice as likely as with one solenoid. The couplers release "only after the ERS valves are proven closed", so one stuck solenoid on a drift-off blocks both the closure and the release. The arm is then pulled past its envelope with the coupler clamped. Neither D-016 nor I-507 says what happens when an ERS valve does not prove closed: a release on time-out or at stage 3, or a manual hydraulic release. The deferral of the analysis to H-01 / H-02 is legitimate, and PSV-5131 / 6131 carry the case, so this is medium. | medium | open | Feed the two solenoid channels from independent protected supplies, and alarm the loss of each. Otherwise show in H-01 that a 5 s closure at full flow stays inside the design, and state it. State the drift-off behaviour when an ERS valve does not prove closed: release after a time-out or at stage 3, the vendor's mechanical sequence, or a manual hydraulic release. Put the 2oo2 versus 1oo2 choice and the proof testing of the solenoids into H-02 / H-06 with the vendor. |
| 2026-11-05-basic-design-6#3 | C&E, instrument list | I-205 / I-305, ZSC-2123 / ZSC-3123, the 15 s timer | The schema defines `delay` as "the condition must hold this long (on-delay)". The 15 s sits on the `ZSC-2123 not closed` leaf of I-205, not on the trip. In holding, when the circulation return is lined up to T-2101, XV-2123 has stood open (ZSC not closed) for hours. The leaf is therefore already true when I-201 trips, and I-205 stops P-2102 / P-3102 / P-5101 / P-6101 at once. The notes describe "15 s after the trip (stroke time plus margin)". The action is on the safe side, a pump stop in holding, but the specification the SIS is programmed from says something other than its intent. I-305 is the same. In addition, ZSC-2123 / ZSC-3123 have no command discrepancy alarm, unlike ZSO-5122 / 6122 ("one stuck open is found by the command discrepancy alarm"). A switch stuck "closed" is a dormant failure that defeats I-205 when it is needed. | low | open | Put the 15 s on the trip: `interlock: I-201, state: tripped, delay: 15 s`, or a row delay on the conjunction. Add "ZSC-2123 / 3123 closed while XV-2123 / 3123 is commanded open: discrepancy alarm" to the switch notes. |
| 2026-11-05-basic-design-6#4 | C&E, instrument list, P-05, P-06 | I-501 / I-601 causes: manual ESD-1 push buttons, platform fire and gas, ERS solenoid supply monitoring; ZSO-5122 / 6122 bypass | The adversarial item closed by D-030.7 adds the causes as `text:` entries with no instrument tag: "manual ESD-1 push button (control room, jetty, platform)", "platform fire and gas confirmed (voted ... ASSUMED)" and "ERS solenoid supply ... lost". None is in the instrument list or on P-05 / P-06. The interlock cross-checks of `cheme validate` therefore cannot see them, and no I/O follows from the C&E. The C&E also gives no bypass or override rule for ZSO-n122. Once ZSO-5122 is a 1oo1 ESD-1 cause, a failed switch stops every transfer at the berth until it is repaired, unless a bypass is defined. | low | open | Tag the push buttons (for example HS-5100A/B/C), the F&G voted output and the HPU supply monitoring (for example XA-5130 / 6130). List them, with their sheet or a P-05 / P-06 note. State the maintenance override of ZSO-n122 (permit, time limit, compensating measure) in the C&E `bypass` field. |
| 2026-11-05-basic-design-6#5 | C&E, instrument list, DESIGN.md D-016 | I-501 / I-601 cross-berth causes; XS-5100 / XS-6100, ZS-n151..n154 at an idle berth | With D-030.9, "I-601 tripped" trips the transferring Berth 2 carrier through I-501. That is right for a real Berth 1 ESD-1. But XS-6100 trip and the Berth 1 arm-envelope switches are I-601 causes with no "berth not in use" state. The record does not say what the link reads when no carrier is connected, or when the idle carrier disconnects its link and leaves during a Berth 2 transfer (D-027.5 allows two carriers alongside). If a disconnected link reads "trip", every departure at Berth 1 ends the loading at Berth 2 with a carrier ESD, and I-601 stays latched with the shared pumps stopped. No hazard follows, since ESD-1 is the designed safe sequence. It is an operability gap made visible by the new cause. | low | open | State the link and envelope-switch states of a berth with no carrier connected in the XS-n100 / ZS-n15x notes and in D-016: the link's own "not connected" mode, not a bypass. State the order of disconnection that leaves I-601 untripped. |
| 2026-11-05-basic-design-6#6 | sequences | SEQ-LOAD S0 / S1, XV-5122 / ZSO-5122, XV-5132 / XV-5142, the vapour arm N2 leak test | D-030 makes "ZSO-5122 open" a complete condition of S0 and S1. S0 opens XV-5122 before S1 connects LA-5102 and leak-tests it with N2 at 2.5 bar. No step names the boundary of that test. The ERS valves XV-5132 / 5142 appear only as "open" in the S1 complete condition. With XV-5122 and the ERS valves open, the test gas goes into BOG-5001 and on to the tanks (PSV-2131 at 0.29 barg) or the flare, and the test cannot hold pressure. With them closed, the sequence does not say when they open. Berth 1 is the same. | low | open | Name the test boundary in S1 (for example the inboard ERS valve closed, or XV-5122 closed during the test). Open it after the test, and move the "ZSO-5122 open" proof to after the test. |
| 2026-11-05-basic-design-6#7 | DESIGN.md D-014, D-023 (2), P-05 / P-06 notes, sequences S4 | LA-5103 / LA-6103 "spare vapour arm"; ZSO-5122 / 6122 as ESD-1 cause | D-014, D-023 (2) and the P-05 / P-06 notes still call the hybrid arm "the spare vapour path" (tile `build/P-05_tile-C1.png`). Since D-030 the vapour arm isolation must read open during any liquid transfer, or ESD-1 trips. Both line-ups of S4 use the vapour arm, and line-up (b) uses the hybrid arm only as a second vapour path. With LA-5102 out of service, no transfer is possible unless ZSO-5122 is bypassed. The design does not say whether that is intended. | low | open | Either state that the vapour arm is required for every transfer and drop "spare", or define a hybrid-only vapour line-up with its own proven-open switch (a ZSO on XV-5125 / 6125) in the gating of I-501 / I-601. |
| 2026-11-05-basic-design-6#8 | line list, DESIGN.md D-023 (3) | LNG-1001 / 1002 / 1003 / 1004, LNG-1011..1014 (Class 150); hold H-05 | D-023 (3) and PSV-1121 now carry "blocked outlet against the trains' rundown pumps" as an open case, with the rundown header's design pressure to be confirmed (H-05). The line list still shows the rundown lines as Class 150, with no hold (`piping/line-list.yaml` lines 9 and 13 onward). Class 150 austenitic steel is rated at about 16 to 19 barg near ambient, depending on the material group. If the trains' shut-off head comes in above that, the pipe class changes. That is a basic deliverable, and as issued it looks final. | low | open | Mark the class and design pressure of the rundown lines "HOLD H-05" in the line-list notes until the trains answer. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-design-5#1 | I-201 / I-301 stop both circulation pumps and both drain pumps, latching, whatever the line-up | medium | closed 79d5c7ad | I-201 / I-301 effects are now the fill and return valves only (C&E lines 164-188, 296-320). The new I-205 / I-305 stop P-2102 / P-3102 / P-5101 / P-6101 only while I-n01 is tripped and ZSC-n123 does not read closed. ZSC-2123 / ZSC-3123 are drawn on the valves: `cheme show ZSC-2123` senses XV-2123 (pid/P-02.xml:3565); tiles `build/P-02_tile-C2.png` and `build/P-03_tile-C2.png`. SEQ-LOAD S0 proves both closed, so in loading the spray (LNG-4008, P-04 tile A1) and the drain pumps keep running. I-506 / I-606 notes corrected. The timer placement is new #3. |
| 2026-11-05-basic-design-5#2 | Air-header trip sees only the battery-limit end; jetty-end air loss closes the vapour isolation with the transfer running | medium | closed 79d5c7ad | ZSO-5122 / ZSO-6122 are drawn on XV-5122 / XV-6122 (`cheme show ZSO-5122`: senses XV5122, pid/P-05.xml:1648; tiles `build/P-05_tile-B3.png`, `build/P-06_tile-B3.png`). "ZSO-5122 not open" during a liquid transfer is an I-501 cause, and I-601 likewise. XV-5122 has no accumulator, so it is the first jetty valve to stroke on a platform-end air loss, while the liquid-path valves hold on their non-return valves (D-016). The pumps-first order therefore holds. F-AIR names the case, and the platform-end transmitters are hold H-04. The gate `return-and-vapour-arm-switches-on-pid` passes. The dependence of the gating on FIC-4101 is new #1. |
| 2026-11-05-basic-design-5#3 | ERS valves de-energise-to-trip: one circuit fault closes them in 5 s at full flow | medium | closed 79d5c7ad | D-016, I-507 / I-607 and the UZ-n13x / n14x notes: 2oo2 line-monitored solenoids, so one coil, wire or output fault no longer closes a valve. The supply loss is an ESD-1 cause. The couplers are energise-to-release after the valves are closed. "Spurious ERS closure at full flow" is D-023 (5) and in the PSV-5131 / 6131 relief cases (`piping/special-items.yaml`). The P-05 / P-06 notes state it (tile `build/P-05_tile-C1.png`). The single supply and the demand side of 2oo2 are new #2. |
| 2026-11-05-basic-design-5#4 | I-514 armed in S3, a liquid transfer, and on a sequence step | medium | closed 79d5c7ad | The I-514 / I-614 logic now uses the plant state "XV-5101 not commanded open, or FIC-4101 and FIC-4102 both below 50 m3/h", and the sequence step is gone. In a transfer, S3 included, the same 2oo2 O2 high-high is an I-501 cause. I checked that the two conditions are exact complements, so no state is uncovered. SEQ-LOAD S3 proves ZSO-5122 open before the cooldown flow starts. D-026.7, the AI / HS notes and the P-05 / P-06 notes are corrected. The choice of inputs is new #1. |
| 2026-11-05-basic-design-5#5 | Rundown blocked-outlet protection rests on an ASSUMED shut-off head; no hold | medium | closed 79d5c7ad | Hold H-05 (TQ to the trains) is in the D-030 table. D-023 (3) and the PSV-1121 relief case carry "blocked outlet against the trains' rundown pumps" as an open case of the header, with its design pressure to be confirmed. The missing line-list hold is new #8. |
| 2026-11-05-basic-design-5#6 | XV-4101 / XV-4102 residual fast closure not named | low | closed 79d5c7ad | D-023 (4) names the pump-header rise (up to rho a v on top of the discharge pressure) and the column separation in the trestle line. It states that the shut-off head does not cover the case. The PSV-2141 / 3141 relief cases name it as a check case of H-01 and do not credit the DN 25 valves. |
| 2026-11-05-basic-design-5#7 | Sheet notes behind the control files | low | closed 79d5c7ad | P-04 note: "UZ-4101 / UZ-4102: C&E I-501, I-601 (also ESD-2, I-503 / I-603, and the air trip I-804); air accumulator, closure 25-30 s" (tile `build/P-04_tile-C1.png`). P-01 note: "I-102: ZSC-1102 / -1103 both closed, PZT-1105, I-201 / I-203 or I-301 / I-303 with the other fill valve closed, I-804", and "HS-1106..1109: last open fill branch not closed (I-103)" (tiles `build/P-01_tile-C1.png`, `C2`). P-02 / P-03 note: "XV-2123 fails closed: C&E I-201, I-205 (ZSC-2123)" (tile `build/P-02_tile-C1.png`). |
| 2026-11-05-basic-design-5#8 | Segment id S1 reused across sheets for LNG-4005 / LNG-4009; D-029.14 wrong | low | closed 79d5c7ad | D-030.12 corrects D-029.14: the valves sit alike, and the difference is the reused segment id. The 3D model qualifies the segment by its sheet: `layout/plant-model.yaml` line 160826 gives XV-2123 `pipe: P-02/Line_LNG4005_S1` at [966.8, 3017.8], so it is not attached to the P-04 piece. Reporting the missing lint to cheme-as-code stays with the layout owner. |
| 2026-11-05-basic-design-5#9 | Deferred safety inputs not registered as issues, holds or TQs | low | open | D-030.13 registers H-01..H-06 in a table in DESIGN.md, against the detail-engineering gate. `cheme issues --all` lists one issue (#362, the process development) and no hold or TQ. The issues gates therefore still cannot see them. The reason given, that no issue can be opened from an agent session, is fair, but the action is with the project owner: open the six issues with the plant.yaml forms. |
| 2026-11-05-basic-design#23 | Design case S5 45.6 t/h linked to the single vapour arm line | medium | closed 79d5c7ad | `process/flowsheet.yaml`: S5 is now "Carrier return vapour, BOG design envelope", linked to sheets P-05 / P-06 (role "berth vapour system (envelope ...)"), no longer to BOG-5012 / BOG-6012. A comment gives the arm-limited returns (~23.5 t/h in line-up (a), ~34 t/h in (b)). The BFD / PFD label changed (`cheme diff f5d925f6`: Stream S5 description, label). A downstream user of the issued stream table can no longer read 45.6 t/h as an arm-line flow. The values are unchanged on purpose: they are the stated envelope of the compressors and the DN 750 lines. |
| 2026-11-05-basic-design-3#5 | LIC-8101 duty/standby drawn as a chain through HS-8101A | low | accepted: the standby no longer depends on the chain for the hazard; I-802 starts both pumps on LZT-8105 and I-803 stops both; availability of the level band only. By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged at HEAD. P-08 has no change since `f5d925f6`, and C&E I-802 / I-803 are unchanged. |
| 2026-11-05-basic-design-3#6 | PZT-7113 1oo1 stops every running compressor | low | accepted: a spurious trip sends the BOG to the flare, a production and flaring loss with no hazard; the voting is left to the SIL screening (now hold H-06). By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged: C&E I-705A-C `PZT-7113 PALL` with a 5 s delay. H-06 names PZT-7113. |
| 2026-11-05-basic-design-2#10 | No relief device sized against its governing case | medium | accepted: relief sizing is a detail-stage calculation; D-025 records the cases, and D-026.8, D-026.14, D-028 and D-030 add the FO-1117 blow-by, the D-7101 fire, the air-failure residual, the spurious ERS closure, the XV-4101 / 4102 residual and the open rundown blocked-outlet case. By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged. The relief cases of review 5 #3, #5 and #6 are now in `piping/special-items.yaml` (PSV-5131 / 6131, PSV-1121, PSV-2141 / 3141). |

## Items raised against review 5 by its adversarial check

These five were judged on the drawn sheets and the control files at HEAD
(`build/adversarial-design-r5.json`).

1. **Fill selection valves XV-1106..1109 (disputed closure and missed medium): closed.**
   - Closure time and permissive.
     - The HS-1106..1109 notes give at least 30 s from a speed controller on the exhaust.
     - I-103 (C&E lines 103-163) blocks the close command of the last open branch of the only
       lined-up tank. "Lined-up" means the fill ESD valve is not proven closed and a selection
       valve is commanded open.
     - SEQ-FILL-CHANGE S2 names it, and D-023 (3) and D-026.4 include the selection valves.
     - The P-01 note says so (tile `build/P-01_tile-C2.png`).
   - Failure modes.
     - I-103 works on commands, not positions. The selection valves are fail last and have no
       position switch. A new branch that fails to open on its command therefore passes the
       permissive, and only the local check of SEQ-FILL-CHANGE S1 and PI-1104 stand in front of
       the close.
     - I-103 is a permissive that only blocks a command. A logic fault does not move a valve.
     - A closure that runs all the same is limited by the 30 s and caught by PZT-1105 -> I-102.
       After that comes the open blocked-outlet case of H-05.
     - Whether position switches are needed is in H-06. I accept that residual at basic.
2. **Manual and F&G causes of I-501 / I-601: closed.** Both are in the `any:` logic of I-501 and
   I-601 (C&E lines 448-449), and SEQ-ESD S1 lists every cause. They are written as text with
   no tag (new #4).
3. **XV-5122 / XV-6122 without position feedback: closed.**
   - ZSO-5122 / 6122 are drawn on the valves (tiles `build/P-05_tile-B3.png`,
     `build/P-06_tile-B3.png`) and are listed.
   - They are complete conditions of SEQ-LOAD S0, S1, S3 and S4.
   - "Not open" during a transfer is an ESD-1 cause.
   - The fail-closed choice against the fail-open XV-4135 is argued in D-030.8: the jetty relief
     path joins downstream, and the O2 reject needs the valve to close. I agree.
   - The new spurious-trip source is a 1oo1 switch. A spurious ESD-1 is the designed safe
     sequence (pumps first, valves at 25-30 s, carrier tripped), so it is an availability
     matter for H-06.
   - Connection and purge (S1, S2, S6) are outside the transfer state, so no bypass is needed
     there. A maintenance override is not defined (new #4).
4. **F-POWER on the ERS supply: closed.** F-POWER states the HPU accumulator, the two channels on
   the UPS, the energise-to-release couplers and the residual. The shared UPS is new #2.
5. **The other berth's carrier on a shared-pump stop: closed.**
   - I-501 takes I-601 tripped only while Berth 2 transfers (XV-5101 commanded open and a
     loading line flow above 50 m3/h), and I-601 likewise.
   - Each trip removes its own shore valve's open command and stops the loading flow. The
     condition through which it could re-trip the other berth therefore drops as soon as it
     trips.
   - There is no trip loop and no latch-up: each can be reset on its own once its own causes
     have cleared.
   - When both berths' shore valves are open (not allowed by D-027.5, and not interlocked), the
     two trip together. That is the right answer for shared pumps.
   - The idle berth's link state is new #5.

## Holds H-01..H-06 (D-030)

| hold | judgement |
|---|---|
| H-01 transient surge analysis | Legitimate. The closure times are written as requirements (I-501, D-023 (1), (3)). Each case is named, the PSVs carry it, and D-023 (4) / (5) state the design change that follows if the analysis shows a PSV cannot answer. The part that the basic design must answer itself is new #2 (a). |
| H-02 ERS trip principle with the arm vendor | Legitimate for the vendor's closure time, accumulator and sequence. Not legitimate for the supply arrangement of the two channels and for the behaviour when an ERS valve does not prove closed. Those are basic choices (new #2). |
| H-03 accumulator and hold-time sizing | Legitimate. The function (one stroke, at least 5 min, speed controller) is specified, and only the sizing is deferred. |
| H-04 jetty air distribution, platform-end transmitters | Legitimate now. ZSO-5122 / 6122 detect the platform-end air loss at basic, so the hold is a refinement, not the only safeguard. |
| H-05 trains' shut-off head and trip response | Legitimate. It is interface data, the open relief case is named, and PSV-1121 says so. The issued line list should show the hold (new #8). |
| H-06 SIL screening | Legitimate. Add the BPCS inputs used in SIS arming (new #1) and the dangerous-failure side of the 2oo2 ERS solenoids (new #2 (b)). |

## Drawing

`cheme validate` drawing lines at `79d5c7ad`:

- P-01, P-02, P-03, P-05, P-06: every rule 0 (line-through-label, line-crossing, label-overlap,
  label-far-from-owner, text-outside-frame, title-text-overflow, line-through-symbol,
  line-through-valve, line-on-pipe, line-not-orthogonal).
- P-04: 0 line-crossing (+2 accepted: BOG-4011 x LNG-4002 and BOG-4015 x LNG-4002, D-026.11),
  all other counts 0.
- P-07: 0 line-crossing (+2 accepted: BOG-7001 x BOG-7009 and BOG-7002 x FL-7004, D-025), all
  other counts 0.
- P-08: 0 line-crossing (+1 accepted: the HS-8101B measuring line x LNG-8001, D-026.11), all
  other counts 0.

The accepted crossings are unchanged since review 5, and I agree with their reasons.

Tiles rendered for all eight sheets (`cheme render pid/<sheet>.xml --png --tiles auto`, 3x3 at
scale 8). Tiles read:
- P-01: B1, B2, C1, C2. These cover the rundown valves, XS-1100, PZT-1105, the selection
  valves and the notes with I-102 / I-103.
- P-02: B2, C1, C2. ZSC-2123 sits under XV-2123 on LNG-4005, with a clean measuring line. The
  XV-2123 note is there.
- P-03: C2. ZSC-3123 is on XV-3123, mirroring P-02.
- P-04: A1, A2, B1, B2, C1, C2. These cover the circulation header and the spray take-off,
  FIC-4101 / 4102, XV-4105 / PSV-4114, the vapour return switch and the UZ-4101 / 4102 note.
- P-05: A1-C3, all nine. ZSO-5122 is at B3, left of XV-5122, with HS-5122 on the right.
- P-06: B1, B2, B3, C1, C2. ZSO-6122 at B3 mirrors P-05.
- P-07, P-08: rendered, not re-read. Neither has changed since `f5d925f6`, where review 5 read
  all their tiles.

The new switches are drawn clear of labels and lines, and no overlap or ambiguous tag was seen
in the tiles read.

## Mechanical checks (non-layout)

- `cheme validate`:
  - 86 files, 0 errors, 25 warnings. All 25 are `cheme.hazop-input-changed` in
    safety/hazop/H-01..H-05, outside this scope. The studies are stamped against `f5d925f6` and
    the P&IDs and the C&E changed in `79d5c7ad`.
  - The last line compares 10 sheets and 25 lists. It cross-checks equipment, lines and DN,
    instruments, piping items, interlocks, control records, tags in texts, HAZOP, layout,
    datasheets and review records. None reports an error or warning in scope.
- `cheme check --stage basic`, before this record:
  - FAIL design-review: review 5 "changed since f5d925f6b911", and the older records name
    rewritten commits.
  - FAIL layout-review, outside this scope.
  - Every other gate ok. That includes the new `return-and-vapour-arm-switches-on-pid`,
    `air-header-trip-on-pid`, `rundown-trip-link-on-pid` and `trip-sensors-on-pid`.
- Re-run after writing this record: design-review ok ("agent review of 79d5c7ad9fef"). The
  layout-review gate still fails, outside this scope.
- `cheme validate --only 'cheme.review-*'` after writing this record: 0 errors, 0 warnings.

## Checked and fine

- **I-205 / I-305 against review 5 #1.** In loading, XV-2123 / 3123 are closed in S0 and proven
  by ZSC, so a tank high-high leaves the spray and the drain pumps running. P-3102 is no longer
  stopped on a T-2101 trip when the return goes to T-3101, because ZSC-2123 reads closed. A
  ZSC failing to "not closed" stops the pumps, which is safe.
- **The 15 s value.** XV-2123 / 3123 are DN 250 spring-return ball valves without a speed
  controller. A stroke of a few seconds is credible, so 15 s is a fair margin once the timer
  sits on the trip (new #3).
- **ZSO-n122 as an ESD-1 cause.**
  - It counts only during a liquid transfer, so connection, leak test, purge, drain and
    disconnection (S1, S2, S6) need no bypass.
  - On an air-main rupture, XV-5122 (no accumulator) starts to stroke while XV-5101, XV-4101 /
    4102 and the arm isolations hold. ESD-1 then stops the pumps first.
  - The vapour return closing during the pump run-down is a small displacement against the
    carrier's vapour space.
- **The arming complement.** "Transfer" (open command AND a flow above 50) and "no transfer"
  (NOT open OR both flows at or below 50) are exact complements. I-514 and the I-501 O2 cause
  never act together and never leave a gap.
- **The cross-berth causes.** There is no trip loop or latch-up (see adversarial item 5). The
  SEQ-ESD S1 text matches the C&E, and the SEQ-LOAD interlock list includes I-205, I-305 and
  I-601.
- **I-103 logic.** The four branches are symmetric, and the effects only block the HS. It is
  non-latching with automatic reset, which is right for a permissive.
- **ERS single-fault side.** One coil, wire or output fault no longer closes a valve. The
  energise-to-release couplers cannot release on any circuit or supply fault. I-507 / I-607
  are unchanged apart from the notes.
- **The relief cases** of PSV-5131 / 6131, PSV-1121 and PSV-2141 / 3141 match D-023 (3) to (5).
- **F-AIR** names the platform-end case and agrees with I-804 and I-501.
- **S5.** The relabel and the link to sheets close review 1 #23 without changing the balance.
  The process-links gate passes.
- **Lists and sheets.** ZSC-2123 / 3123 and ZSO-5122 / 6122 are in the instrument list with
  their sheets. Each senses its own valve (`cheme show`). The on-sheet gate with
  `connected: true` passes.

## Not checked

- Tiles not read:
  - P-01 A1-A3, B3 and C3;
  - P-02 A1-A3, B1, B3 and C3;
  - P-03, all except C2 (it mirrors P-02, and only ZSC-3123 and note 2 changed);
  - P-04 A3, B3 and C3;
  - P-06 A1-A3 and C3;
  - P-07 and P-08 (no change since `f5d925f6`).
- Berth 1 (I-6xx, SEQ-LOAD with 6xxx tags) was compared with Berth 2 in the C&E text and the
  P-06 tiles listed only.
- Calculations for the designer and the vendors (holds H-01..H-05):
  - the surge transients of D-023 (1), (3), (4) and (5), and the closure times;
  - accumulator capacity and hold time;
  - the ERS closure time and the HPU;
  - relief and flare sizing;
  - the trains' shut-off head.
- The SIL screening (H-06): the voting of PZT-8123A/B/C, the AI-4133 / 4134 O2 cells,
  PZT-7113 and the ZSO / ZSC switches.
- The transport delay between the berth and AI-4133 / 4134. They sit at the tank end of the
  2.45 km vapour returns (P-04 tiles B2, C2), and what that means for the O2 trip was not
  assessed.
- `control/loops.yaml`: checked only for FIC-4101 / 4102 and the fail positions.
  `process/narrative.md`: not read.
- The HAZOP studies: their 25 `hazop-input-changed` warnings remain. They need restamping
  against `79d5c7ad` by their owner.
- Layout, routing, the 3D model (beyond the XV-2123 segment reference), D-031 and the
  layout-review gate.
- Area classification, materials, fire and gas, and the vendor packages: arms, ERS couplers
  and HPU, compressor UCP, flare derrick.
