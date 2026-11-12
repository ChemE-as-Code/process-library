---
topic: design
reviewed_commit: 709fcf201fb0e10073d2c486dfa1188c2eafb954
scope: [pid/P-01.xml, pid/P-02.xml, pid/P-03.xml, pid/P-04.xml, pid/P-05.xml, pid/P-06.xml, pid/P-07.xml, pid/P-08.xml, equipment/equipment-list.yaml, piping/line-list.yaml, piping/special-items.yaml, control/instrument-list.yaml, control/cause-effect.yaml, control/loops.yaml, control/sequences.yaml, DESIGN.md]
basis:
  - {path: process/flowsheet.yaml, revision: 709fcf201fb0e10073d2c486dfa1188c2eafb954, relation: depends-on}
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: design, sixth follow-up (basic stage P&IDs P-01 to P-08, lists, C&E, loops, sequences)

## Summary

This is the independent follow-up to `2026-11-05-basic-design-6`. It reviews HEAD `709fcf20` on
`stage/lng-terminal-1-concept`. I did not write any of this design. The working tree was clean
during the review. The round under review:
- `d80ce66c`: HAZOP H-01..H-05 revised to `79d5c7ad` (outside this scope);
- `c0554145`: review records design-6 and layout-4, with their adversarial checks in
  `build/adversarial-design-r6.json` and `build/adversarial-layout-r6.json`;
- `709fcf20`: the response to both (D-032 design, D-033 layout, and edits to D-016, D-018,
  D-023, D-026, D-030, D-031).

Every commit that closes a finding below (`709fcf20`) is HEAD itself.

Review 6 left two medium and six low findings open, plus review 5 #9 (low). At HEAD, on the drawn
sheets and the control files:
- Review 6 #1 to #8 are closed. The fixes are drawn (ZSC-5101 / 6101, AI-5126 / 6126, HS-n100,
  HS-n107, XS-n108, XA-n130A / B on P-05 / P-06) and written as tags in the C&E.
- Review 5 #9 (low) stays open. The holds are still not issues.
- The three accepted findings stay accepted.

The five items of the adversarial check against review 6 are answered. The reason given for each
is sound for what it addresses (section "Items raised against review 6 by its adversarial check").
Three of the fixes introduced new gaps, and those are findings of this record.

This pass found nine new findings: one high, five medium and three low.
1. **#1 (high).** It is not new in this round, but no earlier record raised it. The only path from
   loading line B to the Berth 2 header is the DN 250 platform crossover LNG-4003, and line A
   reaches the Berth 1 header only the same way. D-008, the S0 line-up and the line list say that
   both DN 800 lines feed the loading berth at 6,000 m3/h each. Through DN 250 that is ~30 m/s,
   and the pressure drop is several times the hydraulic budget of D-011. The 12,000 m3/h design
   case cannot run on the drawn plant.
2. **#2 to #6 (medium).** Each is a gap in the fixes of D-032 or D-033:
   - #2: the berth O2 analyser sits downstream of the valves it closes;
   - #3: the "no carrier connected" link mode has an entry condition but no exit;
   - #4: the couplers release on a timer, so a release can come before the ERS valves close;
   - #5: single causes of an ERS closure at full flow remain outside the two supplies;
   - #6: the rainwater pump P-8102 cannot work with the 10.5 m deep basin.

Verdict: **not ready for basic-engineering issue on the design topic**. One high finding is open
(#1). Before issue:
- close #1;
- close or disposition the five medium findings, which can be done at detail engineering;
- close the three new low findings and review 5 #9.

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

The changes since review 6 (`cheme diff 79d5c7ad --list --verbose`):
- P-05: Inst_AI5126, Inst_ZSC5101 (senses XV5101), Inst_HS5100, Inst_HS5107, Inst_XS5108,
  Inst_XA5130A and Inst_XA5130B added; PDI-5102 moved; notes 1 to 11 moved or edited, and
  Note12 added.
- P-06: the same items with 6xxx tags.
- P-01 to P-04, P-07, P-08, BFD and PFD: no change. `draft_P-01.py`, `draft_P-04.py` and
  `draft_tank.py` changed, but their sheets did not, and there is no `generated-sheet-drift`.

The control and list changes (`git diff 79d5c7ad 709fcf20`) are:
- the C&E: I-501 / I-601, I-503 / I-603, I-507 / I-607, I-511..I-514, I-611..I-614 and
  I-205 / I-305;
- the instrument list, the sequences (SEQ-LOAD S0, S1, S3, S6; SEQ-ESD S1) and the philosophy
  (F-POWER);
- the special items (PSV-5131 / 6131), the line list (H-05 holds, BOG-n001 / n003 notes), the
  equipment list (LA-5103, T-8101, T-8102) and the datasheets T-8101, T-8102 and LA-5103;
- two new gates, `transfer-state-and-berth-o2-on-pid` and `berth-esd-causes-on-pid`.

Every change has its reason in D-032 / D-033 and in PROGRESS.md. No changed plant item is
`not drawn`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-design-7#1 | P-04, P-05, P-06, line list, DESIGN.md D-008 / D-011, SEQ-LOAD S0, philosophy objective | LNG-4003 platform crossover (DN 250, XV-4103), LNG-4001 / LNG-4002, LNG-5001 / LNG-6001 | D-008 sizes each DN 800 loading line for 6,000 m3/h "with both lines loading" (3.4 m/s, ~91 kPa over 2.45 km). The line list says LNG-4003 is "open while loading so both lines reach the loading berth". SEQ-LOAD S0 opens XV-4103 so that "line B carries LNG to the berth". The drawn plant has only one connection between line B and the Berth 2 header: LNG-4003, DN 250 through tees T4A4 / T4B4 and XV-4103 (`cheme show LNG-4003`: all three segments DN 250; crop `build/P-04_crop-280-60-420-130.png`). LNG-4002 runs only to LNG-6001 (Berth 1) and LNG-4001 only to LNG-5001 (Berth 2). Line B's 6,000 m3/h through DN 250 is ~30 m/s, about 200 kPa per velocity head. Across two branch tees and the valve that is several hundred kPa. D-011 has 577 kPa of differential in all, with 91 kPa for the line and 120 kPa for the arms, ERS, strainers and valves. The flow would therefore split unevenly. Line A alone at 12,000 m3/h runs at ~6.8 m/s and loses ~4 x 91 kPa. Either way the loading rate of objective 1 ("up to 12,000 m3/h"), the flowsheet loading case and the pump rating of D-011 cannot be met as drawn, and 30 m/s LNG in the crossover is not a buildable design. The crossover was sized for the ~314 m3/h holding circulation (2.8 m/s in DN 250, review 5) and was never checked for the loading case. Basic deliverables are affected: the line list DN, P-04, the pump head and the platform drip tray bay XO (D-033). | high | open | Give the loading berth a DN 800 connection to both loading lines: a DN 800 platform crossover with its own isolation (the DN 250 stays as the holding circulation bypass with XV-4103), or a common platform header. Update D-008, D-011, the line list, P-04, the drip tray bay XO and the layout. Alternatively restate the design case as one line per berth, with the pump head, line velocity and loading time that follow. |
| 2026-11-05-basic-design-7#2 | P-05, P-06, C&E I-514 / I-614, I-511 / I-611, DESIGN.md D-026.1 / D-026.7, D-032.3 | AI-5126 / AI-6126 location; reset of I-514 / I-614; trapped slug | AI-5126 senses Line_BOG5001_S3, downstream of XV-5122, XV-5125 and the BOG-5002 tee (`cheme show AI-5126`; tile `build/P-05_tile-B3.png`). I-514 closes exactly those valves. After a trip, the analyser therefore looks at the gas trapped in BOG-5001 and the return, which is the O2-rich slug of D-032.3. It does not see the carrier's vapour. I-514 is latching with manual reset, and its cause stays true while that gas stands, so it cannot be reset in the normal way. No step drains or purges BOG-5001, and no N2 connection is drawn on it. The way out is to override AI-5126, or to reopen XV-5122 once it reads low. In both cases the slug then flows to the tank end. With I-514 reset, I-511 / I-512 again route on AI-4133 AAH, and during gassing-up the line pack is N2-rich, so XV-4131 is open and XV-4135 closed. The slug goes to the flare until the backup O2 vote of AI-4133 (10 s plus the analyser response) re-trips I-514 and I-513 proves XV-4135 open. At ~5 m3/s that is most of the ~200 m3 slug. D-026.7 ("to the flare only below 5 vol % O2") and D-032.3 ("the slug never reaches the flare") hold only while the line stands still, not at the restart. Medium: AI-4133 is a backup that limits the volume, and the event needs an O2 excursion in gassing-up. But the placement is a basic-design choice, and the reset is not defined. | medium | open | Sample the carrier vapour where it can be measured with the isolations closed: on the arm side of XV-5122 (BOG-5012 or the arm section) and, for line-up (b), upstream of XV-5125, or switch one analyser between the two points. Make the reset condition that reading. Define how the trapped section is cleared: after a reset of I-n14, the return is held to the tanks (I-n11 blocked) until AI-4133 / 4134 O2 has read normal for at least one line volume of flow. Put it in SEQ-LOAD S1 and in D-026.1 / D-026.7. |
| 2026-11-05-basic-design-7#3 | DESIGN.md D-016 (idle berth), C&E I-501 / I-601, instrument list XS-5100 / XS-6100, ZS-n151..n154, SEQ-LOAD S1 / S6 | XS-n100 "no carrier connected" mode | The mode removes XS-n100 from I-n01 in both directions. The carrier's ESD no longer reaches the shore, and the shore's ESD-1 no longer trips the carrier. D-016 and the XS-n100 notes define only its entry condition: "selectable only with every arm stowed and XV-n101 proven closed". Nothing ends it. The C&E has no term for the mode: `grep "no carrier"` finds only notes, in I-501 / I-601 and the lists. No permissive blocks the open command of XV-n101 (UZ-n101), or the unstowing of an arm, while the link is in this mode. No alarm stands while an arm is off its rest in the mode. SEQ-LOAD S1 switches the link back by an operator text action, and the S1 complete condition does not check the switch. If that step is missed, the carrier is connected and loaded with the linked ESD defeated. The only barrier is the procedural ESD-1 test through the link in S3. A ship-initiated ESD, for example a cargo-tank high-high level at topping-off, then closes the ship's manifold valves against the running shore pumps. Only the late back-pressure trip I-502 stops the pumps. The mode is a bypass of the most important cause and effect of I-n01. D-016 says "it is not a bypass", and that is true only while no carrier is connected, which the design does not enforce. In addition, "ZS-n15x read stowed, not a stage" is a property of the arm vendor's envelope system and is stated without ASSUMED. Medium, not high: D-011's 577 kPa against a closed valve, plus the slow-closure surge of D-023 (1), stays inside the 15 barg design, and I-502 stops the pumps. | medium | open | Make the mode end automatically when any arm leaves its stowed position or a link cable is connected. Make "XS-n100 in carrier mode and healthy" a permissive of the XV-n101 open command (UZ-n101) in the C&E. Alarm the mode whenever an arm is not stowed. Add "XS-n100 in carrier mode" to the S1 complete condition. Mark the stowed reading of ZS-n15x ASSUMED (arm vendor, H-02). |
| 2026-11-05-basic-design-7#4 | C&E I-507 / I-607, DESIGN.md D-016 (drift-off fallback), D-032.2 (c), instrument list UZ-n13x / n14x | Coupler release on a timer (5 s closure + 2 s after the ERS close command) | The release is commanded at a fixed time after the close command, whatever the ERS valve position. That answers review 6 #2 (an arm kept clamped past its envelope), but it releases before the ERS valves have closed in two cases, not one: (a) by design, with a valve that failed to close; (b) whenever a valve is slower than 7 s. The 5 s closure is ASSUMED (vendor, H-02), and the 7 s is fixed, not tied to it. A cold HPU or a low accumulator would also slow the stroke. The stated consequence, "the spill of that side's arm inventory into the drip tray (D-031.2)", is understated. Behind a failed inboard ERS valve the shore side is open to the platform header LNG-5001, back to XV-5101, which takes 25-30 s to close. Neither I-503 nor I-507 closes the arm isolations XV-n121 / n123 / n124. The release point is at the outboard end of the arm, at the carrier's manifold, so the first part of the spill falls between ship and jetty, onto the water, not into the 6 x 6 m arm bay. In addition, the release is not an effect in the C&E. I-507 lists only the eight ERS valves, so the timer and its link to the closure exist only in notes. ERS designs commonly interlock the coupler hydraulically on the closure of both valves. The design cites "the vendor's own release sequence" without a source. Medium: it is a recorded trade-off inside hold H-02, and the alternative is also hazardous. | medium | open | Release on both ERS valves of the arm proven closed, or on a timeout taken from the vendor's closure time with margin (H-02). Do not use a fixed 7 s. Add the arm isolations XV-n121 / n123 / n124 to I-n07, so the shore side behind a failed ERS valve is bounded. Write the coupler releases (tag them, for example UY-n135..n138) as effects of I-n07 with the timer. Restate the spill consequence in D-016 with the header inventory and the release point over the water. |
| 2026-11-05-basic-design-7#5 | DESIGN.md D-016, D-023 (5), D-032.2, philosophy F-POWER, SEQ-LOAD S1, instrument list UZ-n13x / XA-n130A / B, electrical list | ERS single-fault closure outside the two supplies: vendor test function, SIS outputs, per-valve channel loss | D-032.2 makes "no single fault, neither a circuit nor a supply, breaker, fuse or UPS, closes an ERS valve ahead of the pump stop" (D-023 (5)). I checked it against the fix and found three gaps. (a) The new ERS function test of SEQ-LOAD S1 runs through "the arm vendor's test function, not I-507". That function vents both channels of a valve and strokes it closed outside the SIS. No permissive confines it to no transfer, so one operator action, or one fault in the vendor panel, closes ERS valves at full flow with the pumps running. That is case (5), which D-023 says "can exceed the 15 barg design". (b) The two channels' outputs come from the ESD logic, and F-POWER gives the logic only "uninterruptible supplies". Nothing states that channel A and channel B are on separate output modules, or that the logic solver's failure state is not both outputs off. A logic solver or common output fault de-energises both channels at once. (c) A fault on one valve's channel A branch (a fuse or a coil wire) is found only by the per-solenoid line monitoring, and that only alarms. XA-n130A / B monitor the UPS supply, not each valve's branch. That valve then runs on one channel for the rest of the transfer, which contradicts "the transfer never runs on one channel". UPS A / UPS B are not in `electrical/electrical-list.yaml`. Medium: the same class as review 6 #2 (a), with PSV-5131 / 6131 and hold H-01 behind it. | medium | open | Permit the vendor's ERS test function only with XV-n101 proven closed (ZSC-n101) and the liquid arms not connected, and write that as a permissive in the C&E. State that channels A and B are on separate SIS output modules, and give the logic solver's own power and fault behaviour (H-06). Make a per-valve channel discrepancy during a transfer an ESD-1 cause, or state the operator response (controlled stop). Add UPS A / UPS B to the electrical list. |
| 2026-11-05-basic-design-7#6 | P-08, equipment list T-8101 / P-8102, datasheets T-8101 / P-8102, DESIGN.md D-033.3 | T-8101 at 10.5 m deep; rainwater pump P-8102 | D-033.3 deepened the basin from 6 m to 10.5 m (equipment list; datasheet T-8101, volume 2,111 m3). I checked the numbers: the 1,000 m3 spill fills it to -5.53 m, and ~1,275 m3 lies below the -4.16 m inlet. The pump was not changed. The P-8102 datasheet still rests on "the 6 m deep sump": 30 m head, NPSH available 8.0 m, suction at 101.3 kPa(a). The pump is a vertical inline unit at grade (equipment list), drawn on P-08 taking suction from a nozzle at the pit bottom (crop `build/P-08_crop-0-195-150-250.png`). From a 10.5 m deep pit, a pump at grade cannot lift water: that is more than the atmospheric suction limit. A suction nozzle at the pit bottom means a wall penetration at the bottom of an LNG impoundment, which LNG impoundment practice avoids. The equipment list leaves "pump type and head for the deeper pit" to the "design owner", with no hold. Rainwater removal is safety-relevant: standing water takes up the ~274 m3 of margin and risks a rapid phase transition with spilled LNG. Medium: the deferral is recorded, and the low-temperature interlock I-801 stays. But the drawn and datasheet arrangement is inoperable. The jetty sump T-8102 (now 6 x 9.5 m) has the same issue under layout-3#4. | medium | open | Change P-8102 to a submersible or vertical can pump in the pit, with no wall penetration, suitable for a cryogenic exposure or interlocked on TSL-8102. Redo its datasheet (head from the pit bottom, NPSH) and P-08. Or register the pump type as a hold with the deferral. Align T-8102's water removal on P-08 ("portable pump") with the equipment list ("fixed water removal ... open"). |
| 2026-11-05-basic-design-7#7 | P-05, P-06, instrument list, C&E I-501 / I-503 | HS-5100 / HS-6100, HS-5107 / HS-6107 | HS-n100 is one tag for three push buttons in three places (control room, jetty head, platform). The list says they are "wired in parallel to the ESD logic". Parallel wiring means normally open contacts, so a broken wire is a dormant failure of the manual ESD-1 at that station. That is the opposite of the de-energise-to-trip principle of the rest of the SIS. With one tag, the SOE cannot tell which station tripped. The manual ESD-2 HS-n107 is on the platform only, and no control room or jetty-head ESD-2 is stated. | low | open | Give each station its own tag (HS-n100A/B/C). Wire them normally closed in series, or line-monitored, as de-energise-to-trip. State where manual ESD-2 can be initiated (at least the control room and the jetty head), or why the platform alone is enough. |
| 2026-11-05-basic-design-7#8 | SEQ-LOAD S1, P-05 / P-06 | Vapour arm N2 leak test (XV-n122 closed, carrier manifold closed) | Review 6 #6 is closed, since S1 now names the boundary. But the test volume, between XV-5122 and the carrier's manifold valve, has no N2 connection on P-05. The N2 header N-8001 enters the liquid header LNG-5001, not the vapour arm section. S1 does not say where the 2.5 bar N2 comes in. | low | open | Name the N2 test connection of the vapour arm (the arm package test point, or a drawn connection between LA-5102 and XV-5122) in S1 and on P-05 / P-06. |
| 2026-11-05-basic-design-7#9 | DESIGN.md D-014, P-05 / P-06 notes, P-08 note, equipment list T-8101 | Stale texts after D-032 / D-033 | Four texts disagree with the design at HEAD. (a) D-014 still says the hybrid arm "is the spare vapour arm". D-032.7 says D-014 "is read with this item" but leaves the text, which contradicts review 6 #7 as closed on the sheets and lists. (b) The P-05 / P-06 note "Arm vents, drains, O2 sample point: arm package" (tile `build/P-05_tile-C2.png`): the O2 sample point is now AI-5126 on the shore line BOG-5001. (c) The P-08 note "T-8101 / T-8102: LNG spill impoundment sumps, tank area and trestle troughs / loading platform" and the T-8101 service "(tank area and trestle)": since D-031 / D-033 the trestle has no drip tray to T-8101. (d) T-8102 water removal is "a portable pump" on P-08 and "fixed water removal ... open" in the equipment list (also layout-3#4). | low | open | Edit D-014 to the D-032.7 wording. Correct the P-05 / P-06 note to "arm vents, drains: arm package; O2: AI-n126". Correct the P-08 note and the T-8101 service. Make the T-8102 water removal one statement (#6). |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-design-6#1 | Transfer state rests on FIC-4101 / FIC-4102 and a DCS command; one loop transmitter disarms the ESD-1 causes and arms the reject | medium | closed 709fcf20 | C&E I-501 lines 458-463: "liquid transfer" is `ZSC-5101 not closed` or `UZ-5101 energised (open)`. I-514 lines 867-871 use the exact complement (`ZSC-5101 closed` and `UZ-5101 de-energised`). FIC-4101 / 4102 no longer appear in any gating. `cheme show ZSC-5101` senses XV5101 (pid/P-05.xml:5022), drawn at 28,191.5 mm (tile `build/P-05_tile-C1.png`). I checked on P-05 / P-04 that liquid reaches the berth only through XV-5101: the drain pump P-5101 returns into LNG-4003 on P-04, upstream of XV-5101. The gate `transfer-state-and-berth-o2-on-pid` passes, and H-06 says that no BPCS measurement is used in the arming. |
| 2026-11-05-basic-design-6#2 | ERS solenoids on one UPS; demand side of 2oo2; no drift-off fallback | medium | closed 709fcf20 | (a) UPS A / UPS B, with XA-5130A / B in I-501 lines 488-491 inside the transfer gate, drawn on P-05 (tile C1). (b) The ERS function test is in SEQ-LOAD S1 (action 1 and the complete condition). (c) The release is on a timer (I-507 notes). The residuals the fix leaves or adds are new #4 and #5. |
| 2026-11-05-basic-design-6#3 | I-205 / I-305 15 s on the switch leaf; no ZSC-2123 / 3123 discrepancy alarm | low | closed 709fcf20 | I-205 lines 195-202 and I-305 lines 329-336: `interlock: I-201 / I-301, state: tripped, delay: 15 s`. ZSC-2123 note (instrument list line 41) and the I-205 note give the discrepancy alarm (closed while commanded open for longer than the stroke time). |
| 2026-11-05-basic-design-6#4 | ESD-1 causes as untagged text; no bypass rule for ZSO-n122 | low | closed 709fcf20 | HS-5100, HS-5107, XS-5108, XA-5130A / B (and the 6xxx tags) are listed (instrument list lines 123-127) and drawn on P-05 / P-06 (tiles C1). The gate `berth-esd-causes-on-pid` passes. The I-501 `bypass` field allows only the ZSO-5122 override, for the transfer in progress, under a permit, alarmed, with a local check. The wiring and tagging of HS-n100 is new #7. |
| 2026-11-05-basic-design-6#5 | Idle berth link and envelope switch state not defined | low | closed 709fcf20 | D-016 "Idle berth", the XS-n100 and ZS-n15x notes, and SEQ-LOAD S1 / S6 define the "no carrier connected" mode and the order of disconnection. I-n01 stays untripped at an idle berth, so holding and the other berth are not blocked. The missing exit from the mode is new #3. |
| 2026-11-05-basic-design-6#6 | Vapour arm leak test boundary not named | low | closed 709fcf20 | SEQ-LOAD S1 names the boundary: XV-5122 closed on the shore side, the carrier's manifold valve on the ship side, the ERS valves open. XV-5122 opens after the test, and S0 no longer opens it. The missing N2 connection is new #8. |
| 2026-11-05-basic-design-6#7 | Hybrid arm still called the spare vapour path | low | closed 709fcf20 | P-05 / P-06 note 2 (tile `build/P-05_tile-C2.png`: "the vapour arm LA-5102 is needed for every transfer (D-032)"), D-023 (2), BOG-n001 / n003 line notes, and the LA-5103 equipment and datasheet notes are corrected. The left-over D-014 text is new #9 (a). |
| 2026-11-05-basic-design-6#8 | Rundown lines Class 150 with no H-05 hold in the line list | low | closed 709fcf20 | `piping/line-list.yaml` lines 9-15: LNG-1001, 1012, 1013, 1014, 1002, 1004 and 1003 carry "HOLD H-05" on their class and design pressure. There is no LNG-1011 (review 6 named it in error). |
| 2026-11-05-basic-design-5#9 | Deferred safety inputs not registered as issues, holds or TQs | low | open | `cheme issues --all` still lists one issue (#362) and no hold or TQ. D-032.8 leaves the six holds to the project owner. |
| 2026-11-05-basic-design-3#5 | LIC-8101 duty/standby drawn as a chain through HS-8101A | low | accepted: the standby no longer depends on the chain for the hazard; I-802 starts both pumps on LZT-8105 and I-803 stops both; availability of the level band only. By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged at HEAD: P-08 has no change since `f5d925f6`, and C&E I-802 / I-803 are unchanged. |
| 2026-11-05-basic-design-3#6 | PZT-7113 1oo1 stops every running compressor | low | accepted: a spurious trip sends the BOG to the flare, a production and flaring loss with no hazard; the voting is left to the SIL screening (now hold H-06). By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged: C&E I-705A-C. H-06 names PZT-7113. |
| 2026-11-05-basic-design-2#10 | No relief device sized against its governing case | medium | accepted: relief sizing is a detail-stage calculation; D-025 records the cases, and D-026.8, D-026.14, D-028, D-030 and D-032 add the FO-1117 blow-by, the D-7101 fire, the air-failure residual, the spurious ERS closure, the XV-4101 / 4102 residual and the open rundown blocked-outlet case. By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged in substance. PSV-5131 / 6131 relief case reworded to the two-supply residual (`piping/special-items.yaml` lines 34 and 40). |

## Items raised against review 6 by its adversarial check

I judged these on the drawn sheets and the control files at HEAD
(`build/adversarial-design-r6.json`).

1. **Disputed closure of review 5 #3 (single-fault ERS closure).** The adversarial check was
   right: at `79d5c7ad` one UPS fed both channels, so the closure was a narrowing.
   - At HEAD the supply cause is answered. There are two UPS on separate distribution, and the
     loss of either during a transfer trips ESD-1 while the other channel holds the valve (I-501;
     XA-5130A / B drawn).
   - The reason is sound for the faults it names: circuit, supply, breaker, fuse and UPS.
   - It is not shown for three single causes that the fix leaves or adds: the vendor's test
     function, the common SIS outputs, and a per-valve branch. They are new #5 (medium).
   - I record review 6 #2 as closed by `709fcf20`, with these residuals as new findings.
2. **O2 analyser at the tank end.** Answered: AI-5126 / 6126 sense BOG-n001 at the berth
   (`cheme show AI-5126`). I-n14 now also opens XV-4135 / 4136, I-n11 / I-n12 are blocked while
   I-n14 is tripped, and I-n13 closes the flare valve make-before-break.
   - I checked the logic. I-512 and I-513 cannot both act, since AI-4133 AAH and "normal" or
     either trip are exclusive. The return is never closed at both tank-end valves.
   - The transport-delay reason is sound for the slug at the time of the trip.
   - The analyser sits downstream of the valves it closes. That leaves the reset undefined and
     sends the slug to the flare at the restart: new #2.
3. **I-514 arming at the ESD-1 transition.** Closed, and the reason is sound. The arming needs
   ZSC-5101 closed and UZ-5101 de-energised, so after an ESD-1 the reject arms only once XV-5101
   has closed (25-30 s). The carrier is then no longer receiving LNG.
   - The residual is a ZSC-5101 stuck closed. It is revealed beforehand by its discrepancy with
     the open UZ-5101.
   - A switch stuck "not closed" fails the S0 complete condition (`ZSC-5101 closed`), so it is
     revealed before any gassing-up.
4. **Idle-berth state.** Closed for its stated scope. In the mode, XS-n100 and the stowed ZS-n15x
   do not trip I-n01, so an idle berth blocks neither SEQ-HOLD nor the other berth's transfer. The
   transfer-gated causes (XA-n130, ZSO-n122, O2, I-n01 of the other berth) are off at an idle
   berth. The mode can be left on with a carrier connected: new #3.
5. **P-2102 / P-3102 not stopped by ESD-1.** I accept the reason, and the numbers check:
   - 500 m3/h in DN 800 is 0.29 m/s, and rho a v is 450 x 1,150 x 0.29 = ~150 kPa. On top of the
     pump's head that is far inside 15 barg.
   - The pump keeps the desuperheater spray and runs on its fail-open minimum flow against the
     closed valves.
   - D-016 now limits "pumps first" to the loading pumps. The C&E notes of I-501 / I-601 and the
     S3 operator text say the same.

## Drawing

`cheme validate` drawing lines at `709fcf20`:

- P-01, P-02, P-03, P-05, P-06: every rule 0 (line-through-label, line-crossing, label-overlap,
  label-far-from-owner, text-outside-frame, title-text-overflow, line-through-symbol,
  line-through-valve, line-on-pipe, line-not-orthogonal).
- P-04: 0 line-crossing (+2 accepted: BOG-4011 x LNG-4002 and BOG-4015 x LNG-4002, D-026.11),
  all other counts 0.
- P-07: 0 line-crossing (+2 accepted, D-025), all other counts 0.
- P-08: 0 line-crossing (+1 accepted, D-026.11), all other counts 0.

The accepted crossings are unchanged since review 6, and I agree with their reasons.

Tiles rendered with `cheme render pid/<sheet>.xml --png --tiles auto` (3x3 at scale 8):
- P-05: A1-C3, all nine read. The new bubbles are clear of lines and labels:
  - ZSC-5101 under XV-5101, with its measuring line to the valve (C1);
  - HS-5100, HS-5107, XS-5108, XA-5130A, XA-5130B in a row (C1);
  - AI-5126 on BOG-5001 (B3).
  Notes 1-12 are read in C1 / C2.
- P-06: B1, B2, B3, C1 and C2 read. They mirror P-05 with the 6xxx tags and "from trestle line B".
- P-08: tiles rendered. The crop `build/P-08_crop-0-195-150-250.png` (T-8101, P-8102, T-8102)
  is read.
- P-04: crop `build/P-04_crop-280-60-420-130.png` (platform crossover) read.

No overlap or ambiguous tag was seen in the tiles read.

## Mechanical checks (non-layout)

- `cheme validate`:
  - 88 files, 0 errors, 17 warnings. All 17 are `cheme.hazop-input-changed` in
    safety/hazop/H-01..H-05, outside this scope. The studies are stamped against `79d5c7ad` and
    the C&E, sequences, special items and P-05 / P-06 changed in `709fcf20`.
  - The last line compares 10 sheets and 25 lists. It cross-checks equipment, lines and DN,
    instruments, piping items, interlocks, control records, tags in texts, HAZOP, layout,
    datasheets and review records. None reports an error or warning in scope.
  - The `cheme.label-tag` infos for the new P-05 / P-06 notes name the intended tags (AI-5126,
    ZSC-5101, XA-5130A, HS-5100, HS-5107, XS-5108, XS-5100).
- `cheme check --stage basic`, before this record:
  - FAIL design-review: review 6 "changed since 79d5c7ad9fef".
  - FAIL layout-review, outside this scope.
  - Every other gate ok. That includes the new `transfer-state-and-berth-o2-on-pid` and
    `berth-esd-causes-on-pid`.
- `cheme validate --only 'cheme.review-*'` after writing this record: 0 errors.

## Checked and fine

- **The complement of the transfer state and of the I-514 arming.** I-501 (lines 458-463) and
  I-514 (lines 867-871) are exact complements on ZSC-5101 / UZ-5101, and I-601 / I-614 mirror
  them. I compared all seven Berth 2 / Berth 1 interlock pairs, logic and effects; they differ
  only in tags and in sheet. I-501 / I-601 give "sheet: P-05 / P-06".
- **Transfer state failure modes.** If a lost SIS output closes XV-5101, ZSC-5101 keeps the state on
  until the valve is closed. A ZSC stuck closed is alarmed while UZ-5101 is energised. A ZSC stuck
  "not closed" fails S0. With ZSO-5122 closed in S0 / S1, a spurious transfer state also trips
  I-501 at once, which is safe and revealed.
- **Tank-end switch.** I-511 / I-611 and I-512 / I-612 are blocked while I-n01 or I-n14 is
  tripped. I-513 / I-613 close the flare valve only on proof of the tank-side valve. XV-4135 /
  4136 fail open. In no state of the C&E are both tank-end valves commanded closed. I found no
  path that opens the flare valve while I-n14 is tripped. The open path at the restart is new #2.
- **XA-n130A / B gating.** They are inside the transfer gate, so an idle berth's UPS fault does not
  stop the shared pumps.
- **SEQ-LOAD S0 / S1 / S3 / S6.**
  - The ERS function test comes before any arm is connected, the link is switched before the
    vapour arm is connected, and XV-5122 opens only after the leak test.
  - S0 proves ZSC-5101 closed, and S3 proves ZSO-5122 open before the cooldown flow.
  - The S3 test leaves I-514 armed while XV-5101 is closed, as stated.
- **H-05 holds** in the line list. **LA-5103** notes corrected.
- **T-8101 / T-8102 arithmetic.**
  - T-8101: pi/4 x 16^2 x 10.5 = 2,111 m3. The 1,000 m3 spill reaches -5.53 m, and 1,275 m3 lies
    below the -4.16 m inlet.
  - T-8102: pi/4 x 6^2 x 9.5 = 268.6 m3, 158 m3 below the -3.91 m inlet, and 125 m3 left after
    33 m3. That is ~129 mm on 972 m2.
  - The datasheets match the equipment list. The pump is #6.
- **PSV-5131 / 6131** relief cases match D-023 (5) as reworded.

## Not checked

- Tiles not read:
  - P-06 A1-A3 and C3;
  - P-01, P-02, P-03, P-07 and P-08 tiles (no sheet change since `79d5c7ad`; review 6 and
    review 5 read them), except the P-08 crop named above;
  - P-04, except the crossover crop.
- The hydraulics of #1 beyond the order-of-magnitude estimate. No line or network calculation
  was run. That needs the designer's hydraulic model.
- Calculations for the designer and the vendors (holds H-01..H-05):
  - the surge transients of D-023 (1), (3), (4) and (5);
  - the ERS closure time and the HPU;
  - the coupler release sequence of the arm vendor;
  - accumulator sizing;
  - relief and flare sizing;
  - the trains' shut-off head.
- The SIL screening (H-06): the voting of AI-n126 / AI-4133 / 4134, the ZSC-n101 / ZSO-n122
  switches and the ERS solenoids.
- The layout, routing, 3D model, D-033 (D-033.9 radiation screening table included) and the
  layout-review gate. T-8101 / T-8102 were checked only for their dimensions, datasheets, P-08
  and P-8102.
- The HAZOP studies: their 17 `hazop-input-changed` warnings remain, for their owner to restamp
  against `709fcf20`.
- `control/loops.yaml` (only checked that no loop is still an input of the arming) and
  `process/narrative.md` (not read).
- Area classification, materials, the fire and gas system, the electrical design (beyond the
  UPS listing of #5), and the vendor packages: arms, ERS couplers and HPU, ship-shore link,
  compressor UCP, flare derrick.
