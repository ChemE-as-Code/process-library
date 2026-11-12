---
topic: design
reviewed_commit: f5d925f6b9112898b43cde87311ec7d6dde48dd5
scope: [pid/P-01.xml, pid/P-02.xml, pid/P-03.xml, pid/P-04.xml, pid/P-05.xml, pid/P-06.xml, pid/P-07.xml, pid/P-08.xml, equipment/equipment-list.yaml, piping/line-list.yaml, piping/special-items.yaml, control/instrument-list.yaml, control/cause-effect.yaml, control/loops.yaml, control/sequences.yaml, DESIGN.md]
basis:
  - {path: process/flowsheet.yaml, revision: f5d925f6b9112898b43cde87311ec7d6dde48dd5, relation: depends-on}
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: design, fourth follow-up (basic stage P&IDs P-01 to P-08, lists, C&E, loops, sequences)

## Summary

This is the independent follow-up to `2026-11-05-basic-design-4`. It reviews HEAD `f5d925f6` on
`stage/lng-terminal-1-concept`. I did not write any of this design. The working tree was clean
during the review. The round under review:
- `54648679`: core 1.7.0 regeneration (reviewed in review 4);
- `a00658de`: review records design-4 and layout-2;
- `f5d925f6`: the response to both records (D-028 design, D-029 layout, and edits to D-016,
  D-018, D-020, D-023, D-025, D-026, D-027).

The commits that close earlier findings (`7bf89f18`, `13a1261f`, `886b0ad5`, `f5d925f6`) are
all in HEAD's history.

The high of review 4 (#1) is closed on control-file and sheet evidence:
- An instrument-air header low-low trip is drawn on IA-8001 (PZT-8123A/B/C, 2oo3, C&E I-804).
- It stops the loading pumps and trips both carriers and the trains.
- It initiates ESD-1 of both berths and the rundown trip I-102.
- The liquid-path fail-closed valves hold on a non-return valve and an accumulator, and close at
  a set speed.
- The ERS valves are moved to the arm vendor's hydraulic unit.

The four adversarial items raised against review 4 are closed as well:
- the rundown surge (closure of at least 30 s, XS-1100);
- XV-2123 / XV-3123, which now fail closed;
- XS-5100 / XS-6100, which are now effects of I-501 / I-601;
- I-502 / I-602, which are now named as late, non-preventive safeguards.

Of the 16 findings carried, 12 are closed, 3 stay accepted and 1 stays open (review 1 #23,
medium).

The fix introduced or exposed nine new findings, five medium and four low. None is critical or
high:
1. I-201 / I-301 now stop both circulation pumps and both jetty drain pumps, latching. That
   removes the desuperheater spray during loading and the emptying of the jetty drain drums.
2. The air-header trip sees only the battery-limit end of the air main. On a jetty-end air
   loss the vapour arm isolation, which has no accumulator, closes while the transfer continues.
3. The ERS valves are now de-energise-to-trip with a 5 s closure. A single circuit fault can
   therefore close them ahead of the pump stop, and that case is not named.
4. I-514 is armed in S3, which is a liquid transfer (the cooldown at 500 m3/h). It is armed
   through a sequence step state.
5. The rundown header's blocked-outlet protection rests on an ASSUMED shut-off head of the
   trains' pumps, and no hold is recorded.

Each of these medium findings has a safeguard behind it, and the transient and vendor parts are
recorded as deferred. None of them leaves a credible hazard unprotected.

Verdict: **ready for basic-engineering issue on the design topic**. No critical or high finding
is open. The six open medium findings should be closed or dispositioned before detail
engineering starts. Merge pending. The layout-review gate is outside this scope. On the re-run
after writing this record it passes through `reviews/2026-11-05-basic-layout-3.md`, which another
agent wrote during this review and which I did not review.

## Branch diff

`cheme diff origin/main --list`: every sheet is new on the branch. There are 1,048 plant-item
lines, all of them added:

```
pid/P-01.xml: (sheet added)    114 plant-item lines
pid/P-02.xml: (sheet added)    125
pid/P-03.xml: (sheet added)    125
pid/P-04.xml: (sheet added)    113
pid/P-05.xml: (sheet added)    136
pid/P-06.xml: (sheet added)    136
pid/P-07.xml: (sheet added)    114
pid/P-08.xml: (sheet added)     79
process/BFD.xml: (sheet added)  51
process/PFD.xml: (sheet added)  55
```

The changes since review 4 (`cheme diff 54648679 --list`) are:
- P-01:
  - XS-1100 added;
  - UZ-1115 / XV-1115 moved;
  - FL-1001 label.
- P-02 / P-03: the XV-2123 / XV-3123 actuators changed (FailRetainPosition -> FailClose).
- P-04: no change.
- P-05 / P-06:
  - HS-n125, ZSC-n123 and ZSC-n125 geometry;
  - the sheet notes.
- P-07: UZ-7125C and ZSO-7121A-C geometry.
- P-08:
  - PZT-8123A/B/C added;
  - CV-8102A/B modified (equalising hole);
  - PI-8122 and IA-8001 changed.

Every change has its reason in `f5d925f6`, in D-028 / D-029 and in PROGRESS.md. No changed plant
item is `not drawn`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-design-5#1 | C&E, P-02, P-03, P-04, P-07, P-05, P-06 | I-201 / I-301; P-2102 / P-3102, P-5101 / P-6101; TV-7103 / TIC-7103, LNG-4008; D-5101 / D-6101, I-506 / I-606 | The D-028.3 fix makes I-201 (T-2101 LAHH) and I-301 (T-3101 LAHH) stop both circulation pumps and both jetty drain pumps, latching with manual reset, whatever the line-up. Three consequences follow. (1) The desuperheater spray LNG-4008 is taken from the circulation header LNG-2002 (P-04 tile A1). SEQ-LOAD S0 starts P-2102 "so the circulation pump keeps the desuperheater spray", and the TIC-7103 TAH response says "check that a circulation pump runs". A tank high-high during loading is credible: one tank takes the rundown while the other loads. The trip then stops the spray, the -120 degC return goes to the compressors unsprayed against D-010, and TZT-7112x / I-703x can trip the running machines, with the BOG going to the flare. (2) In loading, S0 has already closed XV-2123 and XV-3123, so stopping the circulation pumps protects nothing. P-3102 is stopped on a T-2101 trip even when its return goes to T-3101. (3) P-5101 / P-6101 are the only way to empty D-5101 / D-6101, the receivers of PSV-5131 / 6131 and PSV-n171 / n173 / n174. The I-506 note still says "P-5101 empties it (LIC-5111)", but a latched I-201 now prevents that. | medium | open | Stop a source only while its return is lined up to the tripped tank and the return valve is not proven closed. For example, add ZSC-2123 / ZSC-3123 and stop P-2102 / P-3102 / P-n101 on "I-201 tripped and ZSC-2123 not closed after its stroke time". Or drop the pump stops and rely on the fail-closed XV-2123 with a position check. Keep the spray supply in loading. Correct the I-506 / I-606 notes. |
| 2026-11-05-basic-design-5#2 | P-08, P-05, P-06, C&E, DESIGN.md | PZT-8123A/B/C, IA-8001; XV-5122 / XV-6122, XV-5125 / XV-6125; I-804; D-020 | The three trip transmitters are drawn together at the battery-limit inlet of IA-8001 (P-08 tile C2). The jetty is fed over a ~2.45 km air main, and D-020 defers "a second set of transmitters at the platform end of the jetty air main" to detail engineering. A rupture of that main at the trestle or platform need not pull the battery-limit header below 4.5 barg. I-804 then does not act, and the loading pumps keep running. The liquid-path valves at the jetty hold on their non-return valves and accumulators for at least 5 min. The vapour arm isolation XV-5122 / XV-6122 and the hybrid vapour isolation XV-5125 / XV-6125 have no accumulator (D-016 lists only liquid-path valves). They close at spring speed while the carrier still receives up to 12,000 m3/h, and the carrier's return is shut. The remaining protection is the carrier's own tank pressure control and its ESD through XS-5100. Neither the C&E nor D-023 (4) names the case. Where the trip senses the air loss is a basic-design choice. It is not only a detail of the air distribution. | medium | open | Put a 2oo3 set (or at least one voted transmitter) at the platform end of the jetty air main now, initiating I-804 or I-501 / I-601. Or give XV-n122 / XV-n125 the same non-return valve and accumulator as the liquid-path valves. Name the jetty-end air loss in F-AIR and D-023 (4). |
| 2026-11-05-basic-design-5#3 | DESIGN.md, instrument list, special-items, C&E | UZ-5131..5144 / UZ-6131..6144 (ERS valves), I-507 / I-607, PSV-5131 / PSV-6131; D-016 | D-016 and the UZ-n13x / n14x notes now make the ERS valves "de-energise-to-trip", closing in 5 s (ASSUMED) from the hydraulic accumulator, also on a loss of the power unit. The 5 s delay after ESD-2 that keeps the pumps-first order sits in the logic (I-507 `delay: 5 s`). A de-energise-to-trip final element also closes on its own circuit fault: a solenoid coil, a wire break, an output card or the loss of the HPU control supply. That closure does not go through I-503 or I-501. A single fault can therefore close one or all of an arm's ERS valves in 5 s at full flow with the loading pumps running. That is about 1.2 times the 4.3 s 2L/a of the loading line: close to the instant closure of D-023 (1), which adds ~1,750 kPa. This is the fast closure ahead of the pump stop that review 4 #1 was about, now through the electrical side. The PSV-5131 / 6131 relief case names only "the ERS valves on ESD-2", which follows a pump stop. The notes also leave open whether the coupler release (I-507 effect) is de-energise-to-trip. A spurious dry-break release under flow would be worse. | medium | open | State the trip principle of the ERS valves and of the coupler release with the arm vendor so that one circuit fault cannot close or release ahead of the pump stop. Use energise-to-trip with line monitoring and the accumulator for availability, or a confirmed ESD-1 pump stop as a hydraulic permissive. Add "spurious ERS closure at full flow" to the D-023 surge cases and to the PSV-5131 / 6131 relief case, whichever principle is chosen. |
| 2026-11-05-basic-design-5#4 | C&E, sequences, instrument list | I-514 / I-614, AI-4133 / AI-4134, SEQ-LOAD S3, XV-5121, FIC-4101 | Split from review 4 #2, whose three gaps are closed: the mode condition, XV-5125 in the effects, and the notes. I-514 is now armed "in S1, S2 or S3 ... (gassing-up and cool-down, no liquid transfer)", but S3 is a liquid transfer. It opens XV-4101 / XV-4102 / XV-5101 / XV-5121 and sends 500 m3/h of LNG (FIC-4101 setpoint, P-2102) through LA-5101 to cool the arms and the carrier manifold. I-514 tripping in S3 closes both vapour paths, XV-5122 and XV-5125, but stops neither FIC-4101 / P-2102 nor the carrier. The carrier keeps receiving the cooldown LNG with its return shut, which is the gap (1) of review 4 #2 in the cooldown step. The arming also rests on a sequence step state (`sequence: SEQ-LOAD ... in S1, S2 or S3`). A gassing-up run by hand outside SEQ-LOAD leaves the O2 reject disarmed. | medium | open | Arm the closing action only in S1 and S2. In S3, let the O2 high-high trip ESD-1 (I-501 / I-601), which stops the cooldown flow and trips the carrier. Base the arming on plant states (for example no liquid isolation open and FIC-4101 / 4102 below a minimum), not on the sequence step alone. Correct the "no liquid transfer" text in the C&E, the AI / HS notes and D-026.7. |
| 2026-11-05-basic-design-5#5 | DESIGN.md, special-items, P-01 | LNG-1001 / LNG-1002 / LNG-1012..1014, XV-1111..1114, XV-1102 / XV-1103, PSV-1121..1123, XS-1100; D-023 (3) | D-023 (3) and the PSV-1121..1123 relief cases now state that a rundown closure is not a relief case. They rely on two things. First, the trains stop or recycle within the 30 s closure on XS-1100. Second, "the header can only reach the shut-off head of the trains' rundown pumps, which must stay below the 15 barg design (to be confirmed at the battery-limit interface; ASSUMED)". The PSVs are thermal relief only (DN 25 outlets). The blocked-outlet overpressure protection of ~1.2 km of DN 900 rundown header therefore rests on an unconfirmed interface value and a trip in the trains' SIS. No engineering hold or technical query records this: plant.yaml `issues:` has none open, and gates issues-basic and issues-concept pass. The deferral is stated, so it is medium. But the basic design must fix either the design pressure or the relief case before the rundown pressure rating is issued. | medium | open | Raise an engineering hold or technical query to the trains: shut-off head of the rundown pumps at the battery limit, and the response time of the trains' rundown trip on XS-1100. Until it is answered, carry "blocked outlet against the trains' rundown pumps" as an open relief case of the rundown header, with the design pressure to be confirmed. |
| 2026-11-05-basic-design-5#6 | DESIGN.md, special-items | XV-4101 / XV-4102 (UZ-4101 / 4102), PSV-2141 / 3141, PSV-4111 / 4112; D-023 (4) | D-023 (4) names the residual air-failure case of a valve closing at spring speed because its non-return valve or accumulator failed. It names it only for "a shore ESD valve or arm isolation", as a PSV-5131 / 6131 case. The tank-end valves XV-4101 / XV-4102 carry the same non-return valve and accumulator. Their fast closure with the loading pumps running is an upstream closure on the 2.45 km line: a pressure rise in the pump header LNG-2001 / 3001 and a column separation downstream in the trestle line. Neither case is named, and PSV-2141 / 3141 / 4111 / 4112 list thermal expansion only. | low | open | Add the XV-4101 / 4102 residual case (pump-header rise, column separation and rejoin in the trestle line) to the D-023 transient cases. Name the relief device that takes the pump-header side, or state why the pump shut-off head covers it. |
| 2026-11-05-basic-design-5#7 | P-04, P-01, P-02, P-03 | UZ-4101 / UZ-4102, XV-2123 / XV-3123; the P-01 I-102 note | Sheet notes are behind the control files. (a) The non-return valve, accumulator and exhaust speed controller of D-016 are not drawn on any actuator. P-01, P-05 and P-06 name them in a sheet note. P-04 says nothing about the air hold of XV-4101 / 4102 or about I-804: its note "UZ-4101 / UZ-4102: see C&E I-501, I-601 ..." (tile `build/P-04_tile-C1.png`). (b) The P-01 note still gives I-102 as "ZSC-1102 / ZSC-1103 (both closed) and PZT-1105". It omits the new causes I-201 / I-203 / I-301 / I-303 with the other fill valve closed, and I-804 (tile `build/P-01_tile-C1.png`). (c) XV-2123 / XV-3123 are fail closed on the sheets (FailClose), but no P-02 / P-03 note says so or names the I-201 / I-301 pump stops. | low | open | Add the air-hold note to P-04. Bring the P-01 I-102 note to the C&E causes. Name the fail position and I-n01 on P-02 / P-03. Or draw the accumulator and the non-return valve at the actuators as the instrument hook-up legend allows. |
| 2026-11-05-basic-design-5#8 | P-02, P-03, P-04, DESIGN.md | LNG-4005 S1 (P-02 and P-04), LNG-4009 S1 (P-03 and P-04), XV-2123 / XV-3123; D-029.14 | D-029.14 hands "XV-2123 / XV-3123 sit differently because P-02 and P-03 put the valve on different segments" to the design owner. On the sheets the two are drawn alike. `cheme show`: XV-2123 is on `Line_LNG4005_S1` of P-02 and XV-3123 on `Line_LNG4009_S1` of P-03, both at the tank end (tiles `build/P-02_tile-C2.png`, `build/P-03_tile-C2.png`). The difference is in the segment identities. LNG-4005 has segments S1..S3 on P-04, where S1 is the XV-4105 section, and its P-02 continuation is called S1 again. LNG-4009 has S1 on P-04 (the branch) and S1 again on P-03. The same id names two different pieces of pipe of one line on two sheets, so the 3D model can attach XV-2123 to the P-04 piece. | low | open | Number the continuing segments uniquely per line across sheets (for example S4 on P-02), or confirm how the layout maps a segment id reused across sheets. Correct D-029.14: it is a segment identity, not a different valve position. Report the reuse to cheme-as-code if validate should flag it. |
| 2026-11-05-basic-design-5#9 | plant.yaml issues, DESIGN.md | D-028 (detail-engineering list), D-016, D-020, D-023 | D-028 ends with the items left for detail engineering: the transient analysis of D-023 (1), (3) and (4), the accumulator and hold-time sizing, the air distribution and the jetty-end transmitters, and the trains' shut-off head. The ERS closure time and trip principle with the arm vendor are deferred in D-016. Each carries a safety function claimed at basic, yet none is registered as an issue, hold or technical query. The issues gates therefore pass with all of them open, and nothing ties their answer to the gate that needs it. | low | open | Open one hold or technical query per deferred safety input (surge transient, accumulator and hold sizing, ERS principle and closure time, jetty-end air trip, trains' shut-off head), each against the detail-engineering gate. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-design-4#1 | Loss of instrument air closes the jetty ESD and ERS valves with the loading pumps running | high | closed f5d925f6 | C&E I-804: vote 2oo3 of PZT-8123A/B/C PALL. Its effects stop P-2101A-D / P-3101A-D and trip XS-5100, XS-6100 and XS-1100. I-501 / I-601 logic `any` contains `I-804 tripped`; I-102 contains it too. PZT-8123A/B/C are drawn on IA-8001, each on its own tapping (tile `build/P-08_tile-C2.png`), with a sheet note naming I-804 (`build/P-08_tile-C1.png`). The non-return valve, accumulator (one stroke, 5 min hold) and exhaust speed controller of UZ-5101 / 6101, UZ-4101 / 4102, HS-n121 / n123 / n124 and UZ-1102 / 1103 / 1111..1114 are in the instrument list and in sheet notes (P-01 tile C1, P-05 / P-06 tile C1). The ERS valves are hydraulic (UZ-n13x / n14x notes; P-05 note). PSV-5131 / 6131 carry the air-failure residual as a relief case. F-AIR is rewritten. The gate `air-header-trip-on-pid` passes. The gaps left behind are new #2, #3, #6 and #7. |
| 2026-11-05-basic-design-4#2 | O2 reject I-514 without mode condition, missing XV-5125, notes silent | medium | closed f5d925f6 | I-514 / I-614 logic: `all: [vote 2oo2 O2 cells, delay 10 s; sequence SEQ-LOAD in S1, S2 or S3]`. The effects add XV-5125 / XV-6125. The AI-4133 / 4134, HS-5122 / 6122 and HS-5125 / 6125 notes and the P-05 / P-06 sheet note name it (tile `build/P-05_tile-C1.png`). The arming in S3, which is a cooldown transfer, is split into new #4. |
| 2026-11-05-basic-design-4#3 | SEQ-LOAD S3 second ESD-1 test without reset and reopening; test mode without end | low | closed f5d925f6 | S3 actions after the second test: I-501 reset, XV-4101 / 4102 / 5101 / 5121 open, FIC-4101 auto. The complete condition checks I-501 reset, the three valves open and FIC-4101 in auto. The test mode ends with the I-501 reset or after 15 min, and the abort condition names it. |
| 2026-11-05-basic-design-4#4 | What an ESD-1 with off-specification vapour sends to the tanks is not stated | low | closed f5d925f6 | D-026.1 now states it: the residual line pack of the DN 750 return (~1,100 m3, at most 5 vol % O2, about 55 m3 O2) into more than 40,000 m3 of tank vapour space, below 0.15 vol % O2 against the 1 vol % limit of D-026.7. I checked the arithmetic (0.442 m2 x 2,450 m = 1,083 m3). The S3 operator note refers to it. |
| 2026-11-05-basic-design-4#5 | Spool between CV-8102x and HV-8108x blocked in without relief | low | closed f5d925f6 | `cheme diff 54648679`: CV-8102A / B modified. The P-08 note reads "CV-8102A/B have a pressure-equalising hole in the disc, so a pump blocked in between HV-8106x and HV-8108x relieves into D-8101" (tile `build/P-08_tile-C3.png`). The LNG-8001 / LNG-8004 line-list notes agree. |
| 2026-11-05-basic-design-4#6 | SEQ-BOG-START never opens XV-7123A / XV-7130 | low | closed f5d925f6 | S2 opens XV-7123A and XV-7130 and proves both open before PIC-7101 goes to auto. The complete condition checks all three. The title states it is run per machine. |
| 2026-11-05-basic-design-4#7 | F-AIR wrong about compressors and initiators | low | closed f5d925f6 | F-AIR now says the compressors trip by I-705A-C, the tank pressure goes to XV-1115 (I-203 / I-303) and the PSVs, and I-804 acts first. The interlock list is [I-804, I-501, I-601, I-102, I-705A-C, I-203, I-303]. The fail positions quoted agree with the ActuatingSystems read from all eight sheets. |
| 2026-11-05-basic-design-4#8 | Measuring lines off their valves, signal lines through bubbles, UZ-1115 on the PIC-1111 corner | low | closed f5d925f6 | ZSC-5125 / 6125 start on XV-5125 / 6125 (tiles `build/P-05_tile-B2.png`, `build/P-06_tile-B2.png`). ZSO-7121A-C start on XV-7121A-C (`build/P-07_tile-A2.png`, `A3`). HS-5125 / 6125 and UZ-7125C sit under their actuators (`build/P-07_tile-B3.png`). UZ-1115 / XV-1115 are clear of the PIC-1111 signal (`build/P-01_tile-A3.png`). The missing lint rules are recorded in D-028.11. |
| 2026-11-05-basic-design-4#9 | "Blanketing" in D-020 and the N-8001 note | low | closed f5d925f6 | D-020: "no N2 blanketing user". The N-8001 note names only the purge and the leak test (S-01). |
| 2026-11-05-basic-design-3#4 | Single open-position switch per switching valve; a stuck ZSO fakes "proven open" | low | closed f5d925f6 | I-512 / I-513 / I-612 / I-613 logic adds "no ZSO discrepancy: did not read open while commanded closed for longer than its stroke time". A switch stuck open before the switch therefore stands in discrepancy and blocks the interlock, and the return stays open. The ZSO-41xx notes agree. Residual: a sheared stem with a correct switch is undetectable by any position switch on the actuator. That is left to the SIL screening (D-028.13), which I accept. |
| 2026-11-05-basic-design-3#5 | LIC-8101 duty/standby drawn as a chain through HS-8101A | low | accepted: the standby no longer depends on the chain for the hazard; I-802 starts both pumps on LZT-8105 and I-803 stops both; availability of the level band only. By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged at HEAD (tile `build/P-08_tile-B1.png`; C&E I-802 / I-803). |
| 2026-11-05-basic-design-3#6 | PZT-7113 1oo1 stops every running compressor | low | accepted: a spurious trip sends the BOG to the flare, a production and flaring loss with no hazard; the voting is left to the SIL screening. By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged: C&E I-705A-C `PZT-7113 PALL` with a 5 s delay. |
| 2026-11-05-basic-design-3#8 | Top/bottom fill change make-before-break not written in a control file | low | closed f5d925f6 | `control/sequences.yaml` SEQ-FILL-CHANGE: S1 opens the new selection valve and holds the open command for its stroke time with a local check and PI-1104 steady. S2 closes the old one. The abort is on a rising PZT-1105, and I-102 acts on its own. |
| 2026-11-05-basic-design-2#2 | Hybrid-arm permissives can act on a valve in service | medium | closed f5d925f6 | I-504 `all: [XV-5123 open command, ZSC-5123 closed, ZSC-5125 not closed]`, I-505 likewise with ZSC-5125 closed. I-604 / I-605 are the same. With XV-5123 open, ZSC-5123 is not closed, so the logic cannot be true. ZSC-5123 / 5125 are drawn on their valves (tile `build/P-05_tile-B2.png`). |
| 2026-11-05-basic-design-2#10 | No relief device sized against its governing case | medium | accepted: relief sizing is a detail-stage calculation; D-025 records the cases and D-026.8, D-026.14 and D-028 add the FO-1117 blow-by, the D-7101 fire and the air-failure residual. By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged. The cases still missing from the list are new #3, #5 and #6. |
| 2026-11-05-basic-design#23 | Design case: S5 45.6 t/h linked to the single vapour arm line | medium | open | `process/flowsheet.yaml` lines 318-333: S5 "Carrier return vapour", loading 45,571 kg/h, still linked to BOG-5012 / BOG-6012. D-028 leaves it open and hands it to the process design owner. On severity: the H&MB is an issue deliverable, and its design-case link puts about twice one arm's capacity (~71 m/s in the 16 inch arm line against the 40 m/s of D-023) through a line that D-026.6 says no line-up uses. It is not a hazard: no relief, line or machine is sized from that link, and the compressors and DN 750 lines keep 45.6 t/h as a stated envelope. So it is not high. It is also not low, because a downstream discipline sizing from the issued stream table would be misled. It stays medium and should be fixed before the H&MB is issued. The fix is small: link S5 to the berth vapour header, or split it into the arm-limited return and the balance burnt on board. |

## Items raised against review 4 by its adversarial check

These four were judged on the drawn sheets and the control files at HEAD.

1. **Rundown surge on XV-1102 / 1103 / 1111..1114: closed.**
   - Closure time. The UZ-1102 / 1103 / 1111..1114 notes give at least 30 s, set by a speed
     controller, with a non-return valve and an accumulator.
   - Train trip. I-101 and I-102 trip XS-1100, which is drawn on P-01 (tile
     `build/P-01_tile-B1.png`). I-102 now also acts on I-201 / I-203 with ZSC-1103 closed, on
     I-301 / I-303 with ZSC-1102 closed, and on I-804. The trains are therefore tripped as the
     only open fill valve starts to close, not once both are closed.
   - D-023 (3). I checked the estimate: 7,560 m3/h in DN 900 is 3.3 m/s, 2L/a is ~2.0 s over
     1,164 m, and 2 rho L v / t at 30 s is ~115 kPa.
   - The interface assumption behind it is new #5.
2. **XV-2123 / XV-3123 failing in place: closed.**
   - Both are `FailClose` on P-02 / P-03 (script output above).
   - I-201 / I-301 close them.
   - On an air failure, PSV-4114 relieves the blocked return.
   - I estimated the spring-speed closure at the circulation flow, with no accumulator: 500 m3/h
     is ~2.8 m/s in DN 250. Against the 4.9 km DN 800 loop at ~0.3 m/s, the slow-closure
     estimate is a few hundred kPa over the ~2.6 bar of P-2102. Not a finding.
   - The pump stops added with this fix are new #1.
3. **No XS-5100 / 6100 trip effect in I-501 / I-601: closed.** I-501 effects contain `XS-5100:
   trip`, and I-601 contains `XS-6100: trip`. ESD-2 (through I-503 / I-603) and I-804 therefore
   reach the carrier. I-804 also trips both links directly. The XS-5100 / 6100 notes agree.
4. **I-502 / I-602 as late non-preventive safeguards: closed.** Their notes say they act only
   once the header pressure has risen, are not credited against surge, and leave the stop-first
   order to I-501 and I-804. D-016 says the same.

## Drawing

`cheme validate` drawing lines at `f5d925f6`:

- P-01, P-02, P-03, P-05, P-06: 0 line-through-label, 0 line-crossing, 0 label-overlap,
  0 label-far-from-owner, 0 text-outside-frame, 0 title-text-overflow, 0 line-through-symbol,
  0 line-through-valve, 0 line-on-pipe, 0 line-not-orthogonal.
- P-04: 0 line-crossing (+2 accepted: BOG-4011 x LNG-4002 and BOG-4015 x LNG-4002, D-026.11),
  all other counts 0.
- P-07: 0 line-crossing (+2 accepted: BOG-7001 x BOG-7009 and BOG-7002 x FL-7004, D-025), all
  other counts 0.
- P-08: 0 line-crossing (+1 accepted: the HS-8101B measuring line x LNG-8001, D-026.11), all
  other counts 0.

The accepted crossings are unchanged since review 4, and I agree with their reasons.

Tiles read (`cheme render pid/<sheet>.xml --png --tiles auto`, 3x3 at scale 8):
- P-01: A1-C3, all nine. XS-1100 is at B1. UZ-1115 / XV-1115 at A3 are now clear of the
  PIC-1111 signal.
- P-02: A1-C3, all nine.
- P-03: C2 (XV-3123 / HS-3123) only.
- P-04: A1-C3, all nine.
- P-05: A1-C3, all nine.
- P-06: B2 (hybrid arm, ZSC-6123 / 6125, HS-6125) and C1 (notes) only.
- P-07: A1-C3, all nine.
- P-08: A1-C3, all nine. PZT-8123A/B/C are at C2.

Fail actions of every ActuatingSystem on the eight sheets were read from the XML with a
read-only script (`build/review5_fail.py`).
- `FailClose` on P-05 / P-06: the ERS valves XV-n131..n134 / n141..n144, XV-n101, XV-n121..n125
  and XV-n161.
- `FailClose` on P-01, P-02 / P-03 and P-04: XV-1102 / 1103 / 1111..1115, PV-1110 / 1111,
  XV-2123 / 3123, XV-4101 / 4102 and XV-4131 / 4132.
- `FailOpen`: XV-4135 / 4136, UV-7104x, XV-7125x and FV-n111x / n112.
- `FailRetainPosition`: FV-4101 / 4102, XV-4103 / 4105 / 4106 and XV-1106..1109.

The ERS actuators are drawn as generic fail-closed actuators. That is consistent with a
spring-return hydraulic actuator, but nothing on the sheet says it is hydraulic apart from the
P-05 / P-06 note.

## Mechanical checks (non-layout)

- `cheme validate`:
  - 84 files, 0 errors, 25 warnings. All 25 are `cheme.hazop-input-changed` in
    safety/hazop/H-01..H-05, which are outside this scope. The studies are stamped against the
    pre-`f5d925f6` inputs.
  - The last line compares 10 sheets and 25 lists.
  - Equipment, lines and DN, instruments, piping items, interlocks and control records against
    lists and P&IDs: no error or warning.
- `cheme check --stage basic`, before this record:
  - FAIL design-review: review 4 "changed since 546486794c28", and the older records name
    rewritten commits.
  - FAIL layout-review, outside this scope.
  - Every other gate ok, including the new `air-header-trip-on-pid` and
    `rundown-trip-link-on-pid`.
  - Re-run after writing this record: design-review ok ("agent review of f5d925f6b911").
    layout-review is also ok, through `reviews/2026-11-05-basic-layout-3.md` by another agent,
    outside this scope.
- `cheme validate --only 'cheme.review-*'` after writing this record: 0 errors, 0 warnings.

## Checked and fine

- **I-804 voting and set point.**
  - 2oo3 is right for a trip whose spurious action stops loading and trips the trains and both
    carriers. A single transmitter neither trips nor blocks it.
  - The trip at 4.5 barg sits 1 bar above the assumed start of stroke at 3.5 barg on a 7 barg
    header. That margin matters only for the valves without accumulators, all of which close
    after the trip. The liquid-path valves hold on their non-return valves whatever the margin.
  - The trip is latching, with reset once the header has recovered. SEQ-LOAD and SEQ-ESD both
    name I-804.
- **Spurious I-804.** It trips all trains through XS-1100. Without that, the rundown valves
  would close on their accumulators' decay against running trains. With 2oo3 voting, I judge
  the plant-wide consequence acceptable at basic.
- **Interaction with ESD-1, ESD-2 and the ERS.**
  - I-804 enters I-501 / I-601 like any other ESD-1 cause and never initiates ESD-2.
  - The hydraulic ERS valves do not move on air loss.
  - ESD-2 during an air failure still closes them through I-507 from the HPU accumulator.
  - I-501 opens XV-4135 (fail open anyway) and closes XV-5161 (fail closed anyway). On an air
    failure the vapour return stays open to the tanks.
  - SEQ-ESD S1 agrees.
- **Non-return valve and accumulator arrangement.** It is consistent between D-016, D-023 (4),
  F-AIR, the instrument-list notes and the P-01 / P-05 / P-06 notes. Every valve named is
  fail-closed on the sheets. "Closes as the accumulator decays, never faster than its set speed"
  is credible for a creeping decay through the exhaust speed controller.
- **XS-1100.** It is drawn on P-01. It is an effect of I-101, I-102 and I-804, and its
  instrument-list note agrees.
- **Hybrid-arm permissives, the switch discrepancy checks, SEQ-FILL-CHANGE, the SEQ-LOAD S3
  reset and SEQ-BOG-START S2.** Each was read in full at HEAD (see Previous findings).
- **Blocked-in sections.** The fail-closed XV-2123 / 3123 make a new blocked-in section between
  XV-4105 and the tank valves, relieved by PSV-4114 on LNG-4005 (P-04 tile B1). The CV-8102x
  spool relieves through the disc hole.
- **Lists and sheets.**
  - The new tags PZT-8123A/B/C and XS-1100 are in the instrument list with their sheets.
  - The IA-8001, N-8001, LNG-8001 and LNG-8004 notes agree with the drawn order of the items.
  - The PSV-1121..1123 and PSV-5131 / 6131 relief cases agree with D-023.

## Not checked

- Tiles not read:
  - P-03, all except C2. Its only change since review 4 is the XV-3123 fail action, read in the
    XML.
  - P-06, all except B2 and C1. It mirrors P-05, and the same 130 lines changed.
- Berth 1 I-6xx were compared with Berth 2 in the C&E text only.
- Calculations for the designer and the vendors:
  - the surge transient of D-023 (1), (3) and (4), and the closure times;
  - accumulator capacity and hold time;
  - the XV-1115 accumulator against a long air outage;
  - relief and flare sizing;
  - the ERS closure time;
  - the trains' rundown shut-off head and trip response.
- The SIL screening: the voting of PZT-8123A/B/C, the AI-4133 / 4134 O2 cells, the ZSO switches
  and PZT-7113.
- `control/loops.yaml`: checked only for the fail positions and the TIC-7103 spray response.
  `process/narrative.md`: not read beyond the spray. `process/flowsheet.yaml`: read only for S5.
- The HAZOP studies (safety/hazop): their 25 `hazop-input-changed` warnings remain. They need
  restamping against `f5d925f6` by their owner.
- Layout, routing, the 3D model, D-029 and the layout-review gate. The segment-identity part of
  new #8 is noted for the layout reviewer.
- Area classification, materials, fire and gas, and the vendor packages: arms, ERS couplers and
  HPU, compressor UCP, flare derrick.
