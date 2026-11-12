---
topic: design
reviewed_commit: fac0bbb5ce0b1703839d4d4c1db97736c8b65a4d
scope: [pid/P-01.xml, pid/P-02.xml, pid/P-03.xml, pid/P-04.xml, pid/P-05.xml, pid/P-06.xml, pid/P-07.xml, pid/P-08.xml, equipment/equipment-list.yaml, piping/line-list.yaml, piping/special-items.yaml, control/instrument-list.yaml, control/cause-effect.yaml, control/loops.yaml, control/sequences.yaml, DESIGN.md]
basis:
  - {path: process/flowsheet.yaml, revision: fac0bbb5ce0b1703839d4d4c1db97736c8b65a4d, relation: depends-on}
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: design, second follow-up (basic stage P&IDs P-01 to P-08, lists, C&E, loops, sequences)

## Summary

This is the independent follow-up to `2026-11-05-basic-design-2` (reviewed `75e0b9fc`). It
reviews HEAD `fac0bbb5` on `stage/lng-terminal-1-concept`. The author answered review 2 and
the six disputed closures in `fac0bbb5` (DESIGN.md D-026). I did not write any of this design.
The scope files in the working tree are the same as HEAD. During the review the only
uncommitted changes were `safety/hazop/H-01` and `H-02`, which another agent is editing and
which are outside this scope.

What holds up on the drawn sheets and in the C&E:
- ESD-2 now trips ESD-1 at once. I-501 takes I-503 as a cause, I-503 has no delay, and I-507
  closes the ERS valves 5 s later.
- The trestle and fill thermal relief outlets tie in on the sheet: on P-04 on the tank side of
  XV-4135, on P-01 into BOG-1001.
- PZT-1105 now trips I-102.
- The tank relief valves have their locked-open inlet isolation drawn.
- The compressor trips are complete: the vendor trip list and I-705A-C.
- LIC-8101 now acts on the pumps by signal line, and I-803 gives a low-low pump stop.
- PSV-7105 is removed with a sound reason.

Of the 21 previous findings listed below, 16 are closed by `fac0bbb5`. Four stay open: review 2
#2, #9 and #11, and review 1 #23. One stays accepted: review 2 #10. All six disputed closures of
review 2 are now closed on the drawn sheet.

The set is **not ready for basic-engineering issue** yet. One new **high** finding blocks it,
and again it comes from the response itself. To make the vapour return switch
make-before-break, `fac0bbb5` changed the flare valves XV-4131 / XV-4132 from fail closed to
fail open. The tank-side valves XV-4135 / XV-4136 also fail open. On an instrument-air failure
both valves of each switch are therefore open, and the tank vapour header vents continuously to
the flare while the make-up PV-1111 fails closed. D-025 removed exactly this combination for
XV-1115. Loss of the ZSO-4135 signal or of the I-513 output opens the same path while the berth
is loading.

New findings: 1 high, 2 medium and 7 low. Merge pending. New #1 must be closed before the stage
is signed off.

## Branch diff since the previous review (`cheme diff 437b37d4 --list`)

Commits since the reviewed `75e0b9fc`:
- `437b37d4`: the review records 2026-11-05-basic-design-2 and 2026-11-05-basic-layout.
- `fac0bbb5`: the response (D-026).
- `8b531655`, the layout pass, comes before `437b37d4` and is outside this scope.

`git show fac0bbb5 --stat` lists 32 files. Among them are the eight sheets, the four list and
control files, sequences, loops, the equipment list, special-items, five datasheets (D-7101,
D-8101, P-8101A/B), `checks/checks.yaml` (two on-sheet gates, three accepted crossings), the
draft scripts, DESIGN.md and PROGRESS.md. `process/BFD.xml` and `PFD.xml` are unchanged.

`cheme diff 437b37d4 --list` gives 137 plant-item lines:

```
pid/P-01.xml: 28  (4 added, 15 changed, 6 moved, 3 removed: PZT-1105, tees T1112..T1114 into BOG-1001;
                   off-page connectors of BOG-1004/1010/1011 removed; ZSC-1102/1103 measuring lines added)
pid/P-02.xml: 13  (6 added, 7 changed: HV-2134A-C, HV-2135A-C on BOG-2002..2004 and A-2001..2003)
pid/P-03.xml: 13  (the same for T-3101: HV-3134A-C, HV-3135A-C)
pid/P-04.xml: 47  (8 added, 34 changed, 1 moved, 4 removed: ZSO-4131/4132/4135/4136, tees T4V4..T4V7
                   on BOG-4001; off-page connectors of BOG-4011/4012/4015/4016 removed; XV-4131/4132
                   actuators FailClose -> FailOpen)
pid/P-05.xml:  1  (notes: ESD-2 / I-507, the hybrid permissives, the arm purge route)
pid/P-06.xml:  1  (the same for Berth 1)
pid/P-07.xml: 12  (4 added, 3 changed, 1 moved, 4 removed: PZT-7113, ZSO-7121A-C; PSV-7105, T7P1 and
                   FL-7001 removed)
pid/P-08.xml: 22  (4 added, 11 changed, 4 moved, 3 removed: HV-8108A/B, HS-8101A/B; FL-7001 and T8F1
                   removed; LIC-8101 signal line)
```

The commit message and D-026 give a reason for every change. The PROGRESS.md entry is
present. `--verbose` reports `not drawn` only for the Diagram group list of two PlantModels,
which is not a plant item. No changed plant item is undrawn.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-design-3#1 | P-04, P-01, C&E | XV-4131 / XV-4132 (Inst_HS4131_System / Inst_HS4132_System), XV-4135 / XV-4136, I-513 / I-613, BOG-1001, BOG-4001 / 4002, BOG-4013 / 4014, D-8101, PV-1111 | `fac0bbb5` changed the flare valves of the vapour return switch from fail closed to fail open: the FailAction at P-04 lines 198 / 221 is FailClose at `437b37d4` and FailOpen now. D-026.1 says "Both valves fail open", and the tank-side XV-4135 / XV-4136 also fail open. On an instrument-air failure each switch therefore has both valves open. The tank vapour header BOG-1001 is then open through BOG-4001 / 4002 (DN 750), the tees T4V1 and BOG-4013 / 4014 (DN 300) to D-8101 and the flare FL-8101 (`cheme show BOG-4001`: T4V1, the BOG-4013 branch, is on the berth side of XV-4135). At the same time the make-up PV-1111 fails closed, and the SIS vent XV-1115 was made fail closed in D-025 for exactly this reason ("a fail-open vent together with the fail-closed make-up would depressurise the tanks"). The same path opens in normal operation: in on-specification service XV-4131 is held closed only by the energised output of I-513 (non-latching), so a lost ZSO-4135 signal or a lost output opens XV-4131 while XV-4135 is open and the pumps keep withdrawing. The tanks then vent to the flare continuously, the tank pressure falls to the flare back-pressure, the margin to the vacuum valves (-0.3 kPa(g), which admit air) is lost and the BOG is flared. The berth relief path does not need XV-4131 to fail open, because XV-4135 failing open already reopens the return to the tanks on air failure. | high | open | Return XV-4131 / XV-4132 to fail closed: XV-4135 / XV-4136 fail open keep the berth relief path open on air failure. I-513 / I-613 then close the flare valve once ZSO-4135 / 4136 prove the tank side open. If the flare valve must stay fail open (to keep off-specification vapour out of the tanks on air failure), stop reverse flow from the tank header into BOG-4013 / 4014 (for example a check valve between T4V1 and XV-4135, upstream of the trestle relief tees T4V4..T4V7). Then record this air-failure case and its consequence in D-026 and in the PSV-2133 / 3133 vacuum cases. |
| 2026-11-05-basic-design-3#2 | C&E, P-04, sequences | I-511 / I-513 (I-611 / I-613), XV-4131 / XV-4132, AI-4133 / 4134, SEQ-LOAD S3 | The C&E gives XV-4131 two opposite commands during ESD-1 when the vapour is off specification. I-511 opens XV-4131 on AI-4133 AAH and has no ESD-1 condition. I-513 closes XV-4131 when ZSO-4135 is open and I-501 is tripped. I-512 does carry "I-501 not tripped", but I-511 does not. SEQ-LOAD S3 makes the ESD-1 test "before cooldown", when the cooldown vapour is still off specification, so this is exactly the state of the test. The C&E states no priority. Implemented one way, XV-4131 stays open with XV-4135 open (the path of #1). Implemented the other way, the off-specification vapour goes to the tanks. D-026.7 allows that vapour up to 5 vol % O2 to the flare but only 1 vol % O2 to the tanks. | medium | open | Add `{interlock: I-501, state: not tripped}` to I-511 (I-601 to I-611), so that ESD-1 wins. State in D-026.1 what reaches the tanks after an ESD-1 with off-specification vapour (the carrier's ESD has stopped its return; only relief and residual vapour), or keep the berth on the flare path after ESD-1 if O2 to the tanks is not acceptable. |
| 2026-11-05-basic-design-3#3 | P-08 | P-8101A/B, HV-8106A/B, CV-8102A/B, HV-8108A/B, PSV-8109, FO-8107 | The new discharge isolations HV-8108A/B (closing review 2 #7) make each KO drum pump a section of LNG that can be blocked in between HV-8106x and HV-8108x. It has no thermal relief, no casing vent and no drain to the drum. PSV-8109 and the minimum-flow orifice FO-8107 sit on the common header LNG-8001, downstream of HV-8108A/B (crop `build/P-08_crop-80-110-240-205.png`). D-017 asks for thermal relief on every blocked-in cryogenic section. A pump isolated for maintenance while still full of drained LNG is that case. | medium | open | Add a thermal relief per pump between the pump and its discharge check valve, to D-8101 (as PSV-5118 on the drain pump), or a vent and drain per pump casing back to D-8101 with the isolation procedure (drain before blocking in) stated in D-021 or on the sheet note. |
| 2026-11-05-basic-design-3#4 | P-04, C&E | ZSO-4131 / 4132 / 4135 / 4136, I-512 / I-513 (I-612 / I-613) | The make-before-break rests on one open-position switch per valve. If ZSO-4131 fails in the "open" state while XV-4131 is closed (stuck contact, misadjusted cam), I-512 closes XV-4135 and the vapour return is closed at both valves. That is the state that review 2 #1 was about, now reached by a single sensor fault. | low | open | Add a closed-position switch per valve (ZSC-4131 / 4135 and the B pair) and require "open and not closed" in I-512 / I-513, with a discrepancy alarm against the command. Alternatively, give the berth side of the switch its own relief to the flare. |
| 2026-11-05-basic-design-3#5 | P-08, instrument list | LIC-8101, HS-8101A, HS-8101B | The duty/standby drive is drawn as a chain: LIC-8101 sends its signal to HS-8101A, and HS-8101A sends it on to HS-8101B (D-021.9, D-026.11; the instrument-list notes say the command passes "through HS-8101A"). A fault of P-8101A's motor control function, its MCC module, is the usual reason to need the standby, but on the sheet that fault also cuts the level control's path to P-8101B. Only I-802 at high-high would then start it. | low | open | Draw LIC-8101 to both HS (or to a duty selector, for example HY-8101, that drives both) instead of a chain, and say in the HS notes that the duty/standby selection is a DCS function independent of either motor control. |
| 2026-11-05-basic-design-3#6 | P-07, C&E | PZT-7113, I-705A / B / C | One transmitter, PZT-7113 on the common suction header, stops every running compressor at low-low suction pressure. A single spurious PALL (1oo1) during loading stops the whole BOG system, and the tank pressure then goes to the flare through PV-1110 / XV-1115. | low | open | Vote the suction low-low 2oo3 (PZT-7113A/B/C), or use one transmitter per machine downstream of its XV-7121x. Record the choice for the SIL study. |
| 2026-11-05-basic-design-3#7 | sequences, DESIGN.md, P-05 / P-06 | SEQ-LOAD S6, XV-5161, D-5101, BOG-5002, HV-5151 / 5152 / 5153 | D-026.13 and the new P-05 / P-06 note send the after-loading purge N2 from the arms through D-5101 and its vent BOG-5002 into the vapour return. SEQ-LOAD S6 closes XV-5161 before the N2 purge (open XV-5161, drain, close XV-5161, then the purge). The drum is therefore isolated from the header and the arms during the purge, and the purge outlet of D-026.13 is closed. | low | open | Keep XV-5161 open during the S6 purge and close it after "below 2 % hydrocarbons", or state the actual purge outlet in D-026.13. |
| 2026-11-05-basic-design-3#8 | DESIGN.md, control | D-026.4; XV-1106..1109; I-102, PZT-1105 | D-026.4 says the top/bottom fill change is made by opening the new selection valve before closing the old one, "SEQ text in the narrative". No such text is in `process/narrative.md`, `control/philosophy.md` or `control/sequences.yaml`. A change made the other way round now trips I-102 through PZT-1105, which closes the battery-limit valves and trips the trains. That is a spurious plant trip, not a dead-head, but it should not happen. | low | open | Write the fill change as a short sequence (or as an operator step in the narrative), with the new selection valve proven open before the old one closes, and point D-026.4 to it. |
| 2026-11-05-basic-design-3#9 | special-items, DESIGN.md | PSV-2131A-C / PSV-3131A-C, D-7101; D-026.12 | D-026.12 removes PSV-7105 and credits the tank PSVs PSV-2131 / 3131 for a fire on D-7101 and its suction header. Their relief cases in special-items list the loss of the BOG compressors, fire on the tank, rollover and the FO-1117 blow-by, but not the D-7101 fire case. | low | open | Add "fire on D-7101 and the suction header (D-026.12)" to the PSV-2131A-C / 3131A-C relief cases and to the detail-stage relief sizing list of D-025. |
| 2026-11-05-basic-design-3#10 | DESIGN.md, plant.yaml, scripts | D-021 (new paragraph), scripts/draft_P-0x.py, build/P-0N-frame.xml | D-021 now says every sheet is rebuilt from its script on the frame `build/P-0N-frame.xml`, but `plant.yaml` declares none of them as generated (4 `cheme.generator-undeclared` infos). `build/` is git-ignored (`.gitignore:1`), so the frames these sheets were built from are not in the repository: the sheets cannot be rebuilt from a clone, and `generated-sheet-drift` cannot see a hand edit being lost. AGENTS.md says the script of a hand-maintained sheet is provenance only and is never rerun over the sheet. | low | open | Either declare the sheets as generated (`generator: {script, frame}` with a committed frame) and use `cheme regen`, or keep them hand-maintained and stop rerunning the scripts over them. Correct the D-021 paragraph to match. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-design-2#1 | De-inerting switch lets ESD-1 close the vapour return at both valves | high | closed fac0bbb5 | I-501 / I-601 now open XV-4135 / XV-4136 and no longer act on XV-4131 / XV-4132. I-512 closes XV-4135 only with AI-4133 AAH, ZSO-4131 open and I-501 not tripped. I-513 closes XV-4131 only with ZSO-4135 open. ZSO-4131 / 4132 / 4135 / 4136 are drawn with their measuring lines at their valves (crop `build/P-04_crop-60-70-230-215.png`, `build/P-04.png`). PSV-4111..4114 discharge through BOG-4011 / 4012 / 4015 / 4016 into BOG-4001 at T4V6 / T4V7 / T4V5 / T4V4, between XV-4135 and the off-page to P-01 (`cheme show BOG-4001`, line list). SEQ-LOAD S1 completes on ZSO-4131 or ZSO-4135 open. The fail-open change, the C&E conflict and the single switch are new #1, #2 and #4. |
| 2026-11-05-basic-design-2#2 | Hybrid-arm permissives written as trips on the valve in service | medium | open | Not closed in the C&E. I-504 now reads `all: [XV-5123 open command, ZSC-5125 not closed]`, effect `close XV-5123`, non-latching. The schema has no "inhibit" action, and an open command is held while the arm is in service. As written, a ZSC-5125 that drops to "not closed" still closes XV-5123 under full flow. The note says the opposite, but the logic decides. I-505, I-604 and I-605 are the same. Proposed: add `{tag: ZSC-5123, state: closed}` to I-504's `all` (I-505 with ZSC-5125, and the Berth 1 pair), so it can only hold a closed valve closed, or move the permissive into SEQ-LOAD S4 as a step permissive. |
| 2026-11-05-basic-design-2#3 | XV-4106 never closed again; holding short-circuits the trestle | medium | closed fac0bbb5 | SEQ-HOLD S1 closes XV-4106 first and completes on `{XV-4106 closed, TI-4102 < 3 K}`. SEQ-LOAD S6 closes XV-4106 before it runs SEQ-HOLD. XV-4106 is in the SEQ-HOLD equipment. |
| 2026-11-05-basic-design-2#4 | I-102 blind to a fill branch closed by its selection valves | medium | closed fac0bbb5 | PZT-1105 is drawn on LNG-1001 with its own tapping (`build/P-01_tile-B1.png`, `build/P-01.png`) and listed. I-102 is `any: [all: [ZSC-1102 closed, ZSC-1103 closed], PZT-1105 PAHH]`. The make-before-break text of D-026.4 is missing: new #8. |
| 2026-11-05-basic-design-2#5 | Text left behind after D-025 | low | closed fac0bbb5 | The PIC-1111 purpose, alarm response, target source (-0.3 kPa(g)) and rationale are corrected. D-017 now names FG-1001 / FO-1117 / PV-1111. The TZT-7112A-C notes name C&E I-703A/B/C. The ZS-5151..5154 notes name I-501, I-503 and I-507 (instrument list lines 94-103). |
| 2026-11-05-basic-design-2#6 | SEQ-LOAD never starts P-2101A; double block and bleed not operated | low | closed fac0bbb5 | SEQ-LOAD S4 starts P-2101A..D. S2 closes HV-5153, opens HV-5151 and HV-5152, and after the purge closes HV-5152 and HV-5151 and opens HV-5153. |
| 2026-11-05-basic-design-2#7 | KO drum pumps without discharge isolation | low | closed fac0bbb5 | HV-8108A/B drawn downstream of CV-8102A/B, with PSV-8109 kept on the common section (crop `build/P-08_crop-80-110-240-205.png`). The blocked-in pump section this creates is new #3. |
| 2026-11-05-basic-design-2#8 | Pump-column vents to atmosphere at the roof | low | closed fac0bbb5 | The procedure alternative of the proposed action is taken. D-026.9 and the P-02 / P-03 note say the vents are opened only after the column has been displaced with N2 into the tank, and the vendor's lifting procedure governs. |
| 2026-11-05-basic-design-2#9 | N2 users of D-020 not drawn or listed | low | open | D-026.9 now lists the undrawn N2 points (compressor purge, tank inerting, trestle purge). But D-020 (DESIGN.md lines 173-175) is unchanged and still names "seal gas and blanketing", and D-026.9's statement that "D-020 lists them as users of the site N2 system" is not true of the text. Proposed: rewrite D-020 to name the drawn users (the berth tie-ins N-8001) and the undrawn ones of D-026.9, and drop blanketing, or say where it is used. |
| 2026-11-05-basic-design-2#10 | No relief device sized against its governing case | medium | accepted: relief sizing is a detail-stage calculation; D-025 records the cases (tank fire, rollover, utility failure with both vents closed, the surge analysis) and D-026.8 adds the FO-1117 blow-by. By Claude (independent review agent), for the human reviewer to confirm at sign-off | The FO-1117 blow-by is now in the PSV-2131A-C / 3131A-C relief cases (special-items lines 13-15). The D-7101 fire case is still missing: new #9. |
| 2026-11-05-basic-design-2#11 | No O2 limit for carrier vapour to the flare | low | open | The limits are stated (D-026.7: flare below 5 vol % O2, tanks below 1 vol %; the AI-4133 / 4134 notes). The C&E still has one undifferentiated cause, "AI-4133 AAH", for I-511 / I-512, and nothing implements "above 5 % the berth does not take the vapour": there is no O2 high-high cause and no effect on the vapour arm or the ship-shore link. The proposed action's separate N2 (flare) and O2 (reject) logic is not done. Proposed: split the AI-4133 / 4134 cause into the hydrocarbon / N2 switch and an O2 high-high interlock (alarm, then the action of D-026.7: close the vapour arm's ERS valves XV-5132 / XV-5142 (XV-6132 / XV-6142) without releasing the coupler, or a ship-shore stop request), and write the operator response into SEQ-LOAD S1. |
| 2026-11-05-basic-design#4 | ESD-2 does not trip ESD-1; delay holds back the pump stop | high | closed fac0bbb5 | I-501's `any` contains `{interlock: I-503, state: tripped}`. I-503 has no delay and stops P-2101A-D / P-3101A-D and closes XV-5101. I-507 (cause I-503 tripped, delay 5 s) closes XV-5131..5134 / 5141..5144. I-601 / I-603 / I-607 are the same. The P-05 / P-06 notes and SEQ-ESD S1 agree. |
| 2026-11-05-basic-design#12 | Compressor trips incomplete; nothing stops a machine when its suction valve closes | medium | closed fac0bbb5 | I-702 / 702B / 702C name the vendor UCP trips (vibration and bearings, dry gas seal, lube oil, motor, discharge pressure high-high below PSV-7111) as logic text, to be confirmed with the vendor. I-705A-C stop a running machine on ZSO-7121x not open or on PZT-7113 PALL, and close XV-7123x. ZSO-7121A-C and PZT-7113 are drawn and tied (crop `build/P-07_crop-90-20-190-80.png`, `build/P-07.png`). The single transmitter is new #6. The UZ-7121/7123/7125 and UZ-7130 `instrument-no-interlock` infos remain a naming convention (their valves are the effects). |
| 2026-11-05-basic-design#23 | Design case: three liquid arms leave one vapour arm (~23.5 t/h) against the 45.6 t/h return | medium | open | Answered in D-026.6 with two line-ups, but the contradiction has only moved. D-009 derives the 45.6 t/h at a loading rate of 12,000 m3/h (displaced vapour plus 85 % of the pump and line heat). D-026.6 says the 45.6 t/h "occurs only in line-up (b)", which runs at ~8,000 m3/h on two liquid arms, where the displacement and pump heat terms of D-009 are about a third lower. In line-up (a), at 12,000 m3/h, the return is limited to one arm (~23.5 t/h). As written, the 45.6 t/h occurs in neither line-up, yet D-010 sizes the compressors on it (27 t/h each = 50 % + 10 %). The "up to ~47 t/h" of (b) is the capacity of two arms, not a return the balance produces. Proposed: give the flowsheet's loading case the line-up it represents ((a) with the arm-limited return, or (b) recomputed at ~8,000 m3/h), and state in D-010 / D-026.6 which case governs the compressors and the DN 750 lines. |
| 2026-11-05-basic-design#27 | D-8101 notes name PV-2111/3111 | low | closed fac0bbb5 | `equipment/datasheets/D-8101.yaml` line 130 now reads "PV-1110 and the SIS vent XV-1115 to flare". |
| 2026-11-05-basic-design#8 | Rundown dead-head: ZSC-1102/1103 free bubbles not tied to XV-1102/1103 (closure disputed) | high | closed fac0bbb5 | ZSC-1102 has a measuring line to LNG-1002 directly below XV-1102 and senses Line_LNG1002_S1, the segment that carries XV-1102. ZSC-1103 has a measuring line to LNG-1001 beside XV-1103 and senses Line_LNG1001_S6 (`cheme show ZSC-1102`, `cheme show ZSC-1103`; `build/P-01_tile-B2.png`). The on-sheet gate trip-sensors-on-pid passes. |
| 2026-11-05-basic-design#15 | Tank PSVs / vacuum valves without their inlet isolation (closure disputed) | medium | closed fac0bbb5 | P-02: HV-2134A-C (LO) upstream of PSV-2131A-C on BOG-2002..2004, and HV-2135A-C (LO) upstream of PSV-2133A-C on A-2001..2003 (crop `build/P-02_crop-190-90-330-175.png`, `build/P-02.png`). The mechanical N-of-N+1 interlock is in the sheet note. P-03 is the same (HV-3134 / 3135A-C, same diff counts). The gate relief-inlet-isolation-on-pid passes. |
| 2026-11-05-basic-design#26 | PSV-7105 without a credible relief case (closure disputed) | low | closed fac0bbb5 | PSV-7105, tee T7P1 and FL-7001 are removed from P-07 and P-08. BOG-1001 has no valve from the tank nozzles to D-7101 N1 (`cheme show BOG-1001 --sheet pid/P-07.xml`: T7R0, T7R1, T7S1, then D7101_N1; none on P-01 / P-02 either), so the drum is protected by the tank PSVs (D-026.12; equipment list D-7101 notes). The missing relief case on the tank PSVs is new #9. |
| 2026-11-05-basic-design#20 | LIC-8101 start/stop of P-8101A/B not drawn; no low-level pump stop (closure disputed) | medium | closed fac0bbb5 | P-08: LIC-8101 has a signal line to HS-8101A and on to HS-8101B, and each HS is tied to its pump by a measuring line (run feedback) (crop `build/P-08_crop-80-110-240-205.png`). I-803 (LZT-8105 LALL) stops P-8101A/B. The chained drawing is new #5. |
| 2026-11-05-basic-design#6 | PSV-4113 / 4114 outlets end at off-page arrows although BOG-4001 is on the sheet (closure disputed) | high | closed fac0bbb5 | The off-page connectors Line_BOG4015_To / Line_BOG4016_To are removed (diff). BOG-4015 / 4016 join BOG-4001 at T4V5 / T4V4 on the tank side of XV-4135 (`cheme show BOG-4001`, crop `build/P-04_crop-60-70-230-215.png`). Their crossings of line B are accepted as a topological minimum (see Drawing). |
| 2026-11-05-basic-design#18 | Arm purge outlet route not stated or drawn (closure disputed) | medium | closed fac0bbb5 | D-026.13 and the P-05 / P-06 note state the route: before loading into the carrier's manifold, after loading through DR-5001, XV-5161, D-5101 and the vent BOG-5002 into the vapour return, all drawn on P-05 / P-06. The arm vents and the O2 sample point stay in the arm package. The S6 valve order that closes this route is new #7. |

## Drawing

`cheme validate` drawing lines at `fac0bbb5`:

- P-01, P-02, P-03, P-05, P-06: 0 line-through-label, 0 line-crossing, 0 label-overlap,
  0 label-far-from-owner, 0 text-outside-frame, 0 title-text-overflow, 0 line-through-symbol.
- P-04: 0 line-through-label, 0 line-crossing (+2 accepted), all other counts 0. The
  accepted crossings are BOG-4011 x LNG-4002 and BOG-4015 x LNG-4002, from `checks/checks.yaml`,
  reason D-026.11. I agree: line B runs across the whole sheet between off-page connectors, so
  any outlet from line A or the line-A side of the crossover must cross it once to reach
  BOG-4001.
- P-07: 0 line-through-label, 0 line-crossing (+2 accepted: BOG-7001 x BOG-7009 and BOG-7002
  x FL-7004, reason D-025, unchanged since review 2), all other counts 0.
- P-08: 0 line-through-label, 0 line-crossing (+1 accepted: the HS-8101B measuring line x
  LNG-8001, reason D-026.11), all other counts 0. The crossing comes from where HS-8101B is
  placed. If #5 is fixed by redrawing the LIC-8101 signals, re-check it.

What I read:
- Full sheets: `cheme render pid/P-0x.xml --png --scale 3` gave `build/P-01.png`,
  `build/P-02.png`, `build/P-04.png`, `build/P-07.png` and `build/P-08.png`, and I read all five.
- P-01 tiles at scale 8: `build/P-01_tile-B1.png` and `build/P-01_tile-B2.png`, the fill
  branches, PZT-1105, ZSC-1102/1103 and PSV-1121..1123.
- Crops: `build/P-02_crop-190-90-330-175.png` (tank relief isolations),
  `build/P-04_crop-60-70-230-215.png` (relief tie-ins, switch valves and ZSO),
  `build/P-07_crop-90-20-190-80.png` (PZT-7113, ZSO-7121A) and
  `build/P-08_crop-80-110-240-205.png` (KO drum pumps, HS chain).
- Topology settled with `cheme show`: BOG-4001 (P-04), BOG-1001 (P-07), D-7101, LNG-1002,
  ZSC-1102, ZSC-1103, ZSO-4131, ZSC-5123, HV-2134A.
- Fail positions of XV-4131/4132/4135/4136: read from the ActuatingSystems in P-04 (lines
  191-267) and compared with `437b37d4`.

## Mechanical checks (non-layout)

- `cheme validate`: 79 files, 0 errors, 41 warnings (run twice, both times 0 errors). All the
  warnings are outside this scope:
  - 32 `cheme.hazop-input-changed`;
  - 6 `cheme.hazop-unknown-tag`: PSV-7105 and FL-7001 in H-04 / H-05, both removed by `fac0bbb5`;
  - 1 `cheme.layout-model-outdated`;
  - 2 `cheme.layout-routing-unknown-line`.

  HAZOP and layout are being updated by other agents. Non-layout infos in scope:
  - 17 `cheme.instrument-no-interlock`: UZ-1115, UZ-7121/7123/7125 A-C and UZ-7130 (a naming
    convention: their XV are effects); LIC-5111 / 6111, LIC-8101, LI-8103 and the new HS-8101A/B
    (their notes say "stops", but the start/stop is regulatory; I-803 covers the low-low).
  - 8 `cheme.control-shared-element`: the compressor stop shared by PIC-7101 with I-204, I-304,
    I-701, I-702, I-703A, I-704 and I-705A, and LV-7102 with I-802; meant.
  - 24 `cheme.control-logic-text`: sequence text, acceptable at basic.
  - 12 `cheme.offpage-mismatch`: accepted under D-021.
  - 5 `cheme.line-crossing`: the accepted crossings above.
  - 4 `cheme.generator-undeclared`: see #10.
  - 1 `cheme.accept-unused`: a layout entry.
  - The cross-checks of lines and DN, instruments, piping items and interlocks against the lists
    and P&IDs report 0 findings.
- `cheme check --stage basic`:
  - ok: design-basis, concept-lists, process-concept, process-balances, process-links-concept,
    process-basic, process-links, assumptions-marked, drawing-clean, pids-exist, mto,
    issues-concept, issues-basic, tank-protection-on-pid, berth-arms-on-pid,
    bog-compressors-on-pid, and the two new gates relief-inlet-isolation-on-pid and
    trip-sensors-on-pid.
  - pids-valid: FAIL ("3 error(s)") in a first run, made while the HAZOP agent was writing
    H-01 / H-02. It was ok on the re-run after this record was written, and `cheme validate`
    reports 0 errors before and after, so the failure came from the concurrent edit, not from
    the scope files.
  - design-review: FAIL in the first run, because the earlier records are stale since
    `75e0b9fc` / `7bcea968`. It was ok on the re-run with this record. A sign-off is still
    refused while #1 (high) is open.
  - FAIL layout-3d, lifting-study, layout-review: layout scope (the model is outdated after
    `fac0bbb5`), not reviewed here.
- `cheme validate --only 'cheme.review-*'` after writing this record: 0 errors, 0 warnings.

## Checked and fine

- ESD sequence. ESD-1 (I-501 / I-601) is initiated by the ship-shore link, ZS stage 1, manual,
  fire and gas, and now ESD-2. It stops the pumps, closes XV-5101 in 25 s and XV-4101/4102,
  closes XV-5161 and opens XV-4135. ESD-2 has no delay. The ERS closure follows after 5 s in
  I-507 / I-607, and SEQ-ESD S1 / S2 describe the same.
- Vapour return switch in normal service. With I-501 healthy and the vapour off specification,
  I-511 opens XV-4131 first, and I-512 closes XV-4135 only once ZSO-4131 proves it open. Back on
  specification, I-512 drops and XV-4135 opens, and I-513 closes XV-4131 only once ZSO-4135
  proves that. After an ESD-1 is reset, the switch returns to the flare only through the same
  order. The defects are the fail positions (#1), the ESD-1 conflict (#2) and the single switch
  (#4).
- The trestle relief outlets and the berth relief outlets (through D-5101 and BOG-5002) can
  always reach either the tanks or the flare in every switch state the C&E allows.
- PSV-7105 removal (D-026.12). There is no valve between the tanks and D-7101, and the drum
  design (3.5 barg) is far above the tank PSV set point (0.29 barg). The compressor recycles
  return upstream of the drum into an open header.
- I-705A-C are written so that a stopped machine is not tripped (`K-7101x running` in the
  `all`), so SEQ-BOG-START needs no bypass.
- I-803 is non-latching with automatic reset, so LIC-8101 restarts the duty pump once the
  level recovers. I-802 and I-803 use LZT-8105, which is independent of LIC-8101.
- The P-01 thermal relief outlets BOG-1004 / 1010 / 1011 join BOG-1001 on the sheet at the
  T1112..T1114 tees, and the line list agrees (BOG-1010 / 1011 notes).
- The line list for BOG-4011 / 4012 / 4015 / 4016 names the tees T4V6 / T4V7 / T4V5 / T4V4, as
  `cheme show BOG-4001` does.
- SEQ-LOAD S4 operator text and D-014 / D-023 now point to the two arm line-ups of D-026.6. The
  numbers behind them are previous #23.

## Not checked

- Tiles: of the 3x3 tiles of each sheet only P-01 B1 and B2 were read. The rest of P-01, P-02,
  P-04, P-07 and P-08 was read on the full-sheet renders at A3 legibility and the crops above.
  P-03, P-05 and P-06 were not rendered: their changes are the mirrored relief isolations (P-03,
  by the P-02 render, the identical diff counts and the on-sheet gate) and note texts (P-05 /
  P-06, read from the diff).
- The Berth 1 interlocks (I-601..I-613) were compared with the Berth 2 ones by the diff text,
  not by a separate reading of P-06.
- Relief and vacuum sizing, the flare back-pressure and the depressurisation rate of the tanks
  through the path of #1 (a calculation for the designer), the surge transient with the ERS
  timing, and the trains' fuel-gas capacity.
- The SIL study: the independence of LZT-8105 for both I-802 and I-803, and the 1oo1 sensors
  of I-512 / I-513 / I-705.
- process/narrative.md and control/philosophy.md were searched only for #8. The HAZOP studies
  (safety/hazop), which another agent is updating, and their stale tags PSV-7105 / FL-7001.
- Layout, routing and the 3D model, the area classification, materials, fire and gas, and the
  vendor packages (arms, ERS couplers, compressor UCP).
