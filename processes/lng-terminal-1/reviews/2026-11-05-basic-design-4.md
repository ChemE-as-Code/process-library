---
topic: design
reviewed_commit: 546486794c289ec5c16600356c90c5adf782a1f7
scope: [pid/P-01.xml, pid/P-02.xml, pid/P-03.xml, pid/P-04.xml, pid/P-05.xml, pid/P-06.xml, pid/P-07.xml, pid/P-08.xml, equipment/equipment-list.yaml, piping/line-list.yaml, piping/special-items.yaml, control/instrument-list.yaml, control/cause-effect.yaml, control/loops.yaml, control/sequences.yaml, DESIGN.md]
basis:
  - {path: process/flowsheet.yaml, revision: 546486794c289ec5c16600356c90c5adf782a1f7, relation: depends-on}
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: design, third follow-up (basic stage P&IDs P-01 to P-08, lists, C&E, loops, sequences)

## Summary

This is the independent follow-up to `2026-11-05-basic-design-3`. It reviews HEAD `54648679`
on `stage/lng-terminal-1-concept`, after the branch was rebased on `origin/main`. I did not write
any of this design. The scope files in the working tree are the same as HEAD. The only
uncommitted paths during the review were `safety/hazop/H-01..H-05` (another agent) and two files
outside the plant folder; none is in this scope.

The rebase rewrote the commits named in the earlier records:

| commit in the earlier records | commit at HEAD | content |
|---|---|---|
| `589c9ca7` | `7bf89f18` | response to review 1 (D-025) |
| `fac0bbb5` | `13a1261f` | response to review 2 (D-026.1 to .13) |
| (new) | `886b0ad5` | response to review 3 (D-026.14) |
| (new) | `54648679` | P&IDs, BFD/PFD and 3D model rebuilt with core 1.7.0 |

Neither `589c9ca7` nor `fac0bbb5` is an ancestor of HEAD (`git merge-base --is-ancestor`
fails). A sign-off is refused while a critical or high finding is closed by a commit that is not
in HEAD's history. Every critical and high finding closed by one of them is therefore listed
again below under Previous findings, with the rewritten commit and fresh evidence at HEAD. The
medium and low findings closed by `589c9ca7` or `fac0bbb5` stay closed by `7bf89f18` or
`13a1261f`, by the mapping above.

What holds up on the drawn sheets and in the control files:
- The vapour return switch is safe on an air failure. XV-4131 / XV-4132 fail closed again
  (`FailClose` at P-04 lines 198 / 221) and XV-4135 / XV-4136 fail open.
- I-511 / I-611 now carry "I-501 / I-601 not tripped", so ESD-1 has priority over the flare
  valve.
- The O2 reject interlock I-514 / I-614 exists.
- The S3 ESD-1 test no longer aborts SEQ-LOAD. XV-4101 / XV-4102 are reopened afterwards.
- SEQ-HOLD lines up XV-4101 / XV-4102 with FV-4101 / FV-4102 open.
- I-802 starts both KO drum pumps and yields to I-803.
- The sheets are declared as generated, with their frames committed.

Of the 15 open or accepted findings carried from the three records, 8 are closed by `886b0ad5`,
4 stay open and 3 are accepted. The eight items that the adversarial check raised against
review 3 are all closed on control-file evidence (section below).

The set is **not ready for basic-engineering issue**. One new **high** finding blocks it: a
loss of instrument air closes every fail-closed ESD and ERS valve on the jetty while the loading
pumps keep running. Nothing in the C&E stops the pumps or trips the carrier first, and PI-8122
on the air header only indicates. The stop-the-pumps-first closure order is what D-016, D-023,
I-501 and I-507 rely on against surge. It is therefore not kept on the commonest common-cause
failure, and the control philosophy F-AIR describes this case without noticing it.

New findings: 1 high, 1 medium and 7 low. Merge pending. #1 must be closed before the stage is
signed off.

## Branch diff

`cheme diff origin/main --list`: every sheet is new on the branch. There are 1,044 plant-item
lines, all of them "added":

```
pid/P-01.xml: (sheet added)    113 plant-item lines
pid/P-02.xml: (sheet added)    125
pid/P-03.xml: (sheet added)    125
pid/P-04.xml: (sheet added)    113
pid/P-05.xml: (sheet added)    136
pid/P-06.xml: (sheet added)    136
pid/P-07.xml: (sheet added)    114
pid/P-08.xml: (sheet added)     76
process/BFD.xml: (sheet added)  51
process/PFD.xml: (sheet added)  55
```

Since the review 3 record (`cheme diff 9111e9d6 --list`) there are 200 lines. P-01 has 18, P-04
19, P-05 33, P-06 33, P-07 34 and P-08 5. P-02 and P-03 are unchanged. BFD and PFD have 28 and
30, all of them regeneration changes. The changes are:
- Actuator, signal and measuring-line geometry on P-01 and P-04..P-07. This is the 1.7.0
  regeneration, which turned the actuators off the pipes and routed the position-switch
  measuring lines with sensing points.
- XV-4131 / XV-4132 FailOpen -> FailClose (`886b0ad5`).
- The P-04 and P-08 notes.

Commits on the branch since the review 3 record:
- `886b0ad5`: response to review 3.
- `e11eb12a`: layout pass, outside this scope.
- `54648679`: core 1.7.0 regeneration.

Each commit message gives its reasons, and PROGRESS.md has the entries. `--verbose` reports
`not drawn` only for the BFD/PFD provenance notes, diagram extents and engineering-model
versions, which are metadata and not plant items.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-design-4#1 | P-05, P-06, P-04, P-08, C&E, philosophy | IA-8001 / PI-8122; XV-5101 / XV-6101, XV-4101 / XV-4102, ERS XV-5131..5144 / XV-6131..6144, arm valves XV-5121..5125, XV-5122; P-2101A-D / P-3101A-D; I-501 / I-601, I-507 / I-607; D-016, D-023; F-AIR | A loss of instrument air closes every jetty ESD and ERS valve while the loading pumps keep running. All of them fail closed: the shore ESD valves, the tank-end valves, the eight ERS ball valves per berth, the arm isolations and the vapour arm valve XV-5122. The fail actions were read from every ActuatingSystem on P-04 / P-05 / P-06. No C&E entry has an air-header cause. PI-8122 on IA-8001 (P-08) is an indicator only. Nothing therefore stops P-2101 / P-3101 or trips the carrier through the ship-shore link before the valves stroke. The pumps keep running on their fail-open minimum-flow valves, and each valve closes at its own spring or vent speed. The ERS ball valves "close in seconds" (review 1 #4). The surge philosophy depends on the opposite order. D-023 records the 25 s closure as a safety requirement, gives the estimate with "ESD-1 stops the pumps first", and adds 1,753 kPa for an instant closure against the 15 barg design of the arms and lines. I-501 and I-507 stop the pumps first and close the ERS valves 5 s later for exactly this reason. Control philosophy F-AIR describes the case as "the ESD and ERS valves and the fill valves close (loading stops)" and lists I-501, but nothing initiates I-501. Review 1 #4 asked for the air failure to be added to the surge analysis. The ESD-2 part was closed, but the air-failure part was never answered, and PSV-5131 / PSV-6131 list only "surge on a fast ERS / ESD-2 closure". The consequence is a surge in the arms and the platform header at full loading flow. That is a loss of containment of LNG at the berth on a common-cause utility failure. | high | open | Add an instrument-air header low-low pressure trip: PZT on IA-8001, voted (for example 2oo3), set above the stroke threshold of the actuators. It initiates I-501 and I-601 (pumps stopped, carrier tripped through the link) before the valves move. Specify the ESD and ERS actuators so that their closure time on air loss equals the commanded one: local accumulators and speed control on XV-5101 / XV-6101, and the ERS valves on the arm vendor's hydraulic power unit with an accumulator, or fail-last on air with closure only by ESD-2. Record this in D-016 / D-023. Add the air-failure closure to the D-023 surge cases and to the relief case of PSV-5131 / PSV-6131. Rewrite F-AIR (see #7). |
| 2026-11-05-basic-design-4#2 | C&E, P-05, P-06, instrument list | I-514 / I-614, AI-4133 / AI-4134, XV-5122 / XV-6122 (HS-5122 / HS-6122), XV-5125 / XV-6125 | The new O2 reject interlock has three gaps. (1) Its logic has no mode condition: `{tag: AI-4133, state: O2 AHH (5 vol %)}` with a 10 s delay. The notes say "only during gassing-up and cool-down", but the logic decides. A single analyser (1oo1) that fails high, or air ingress at the carrier, therefore closes the only vapour arm during full-rate loading in line-up (a). I-514 neither stops the loading nor trips the carrier: its only effect is to close XV-5122, latching. The carrier keeps receiving 12,000 m3/h with its vapour return shut, so its tank pressure rises to its own relief at the berth. (2) In line-up (b) the hybrid vapour path XV-5125 joins BOG-5001 downstream of XV-5122 (P-05 tile B3), so I-514 does not stop the vapour it is meant to reject. (3) Neither the AI-4133 / AI-4134 nor the HS-5122 / HS-6122 instrument-list notes name I-514 / I-614, and no P-05 / P-06 note refers to it. | medium | open | Arm I-514 / I-614 only in SEQ-LOAD S1 to S3 (permissive or mode condition), and alarm only after S3. Or let it trip ESD-1 (I-501 / I-601) when it acts while liquid is being transferred. Add XV-5125 / XV-6125 to its effects. Use a voted or validated O2 measurement. Name I-514 / I-614 in the AI-4133 / AI-4134 and HS-5122 / HS-6122 notes and in the P-05 / P-06 notes. |
| 2026-11-05-basic-design-4#3 | sequences | SEQ-LOAD S3, I-501, XV-4101 / XV-4102, XV-5101, FIC-4101 | S3 runs the ESD-1 test twice. The first test is followed by a reset of I-501 and the reopening of XV-4101 / XV-4102 / XV-5101, which closes the adversarial item. The complete condition then requires the "ESD test repeated after cooldown (S-01)". No action follows that second test: no I-501 reset, no reopening of XV-4101 / XV-4102 / XV-5101, no FIC-4101 back to auto. S4 then starts the loading pumps against closed ESD valves and runs into its 2 h timeout. The test-mode inhibit of the abort ("for the test only") also has no end condition or time limit. | low | open | Add after the repeated test the same reset and reopening actions as after the first one, or move the second test to the start of S4 with them. Give the test mode an automatic end (time limit, or cleared by the reset of I-501). |
| 2026-11-05-basic-design-4#4 | DESIGN.md, sequences | D-026.1, D-026.7; I-501 / I-513, AI-4133; SEQ-LOAD S3 | Split from review 3 #2 (its C&E conflict is closed). On ESD-1, I-501 opens XV-4135 and I-513 closes XV-4131, so the carrier's vapour goes to the tanks whatever AI-4133 reads. The S3 ESD-1 test is made "before cooldown", during gassing-up, when the vapour can be off specification and carry up to 5 vol % O2 (D-026.7). The test thus routes that vapour into the tank vapour space each time, against the 1 vol % O2 limit for the tanks in D-026.7. D-026.1 does not state what reaches the tanks in that case (the carrier's ESD stops its return compressor, so only the residual flow). | low | open | State in D-026.1 the amount and O2 content that reach the tanks after an ESD-1 with off-specification vapour, and why it is acceptable. Or make the S3 test only once AI-4133 reads below 1 vol % O2. |
| 2026-11-05-basic-design-4#5 | P-08, special-items | P-8101A/B, CV-8102A/B, HV-8108A/B, PSV-8109 | Split from review 3 #3 (the pump casing is closed). The vented-ball HV-8106x relieves the pump and its discharge up to the check valve CV-8102x into D-8101. The short spool between CV-8102x and HV-8108x cannot relieve back through the check valve, and PSV-8109 sits downstream of HV-8108A/B (P-08 tile B2). With a pump isolated for maintenance, that spool is a blocked-in LNG section without relief, against D-017. The P-08 note "a pump blocked in between HV-8106x and HV-8108x relieves into D-8101" is true only up to the check valve. | low | open | Give CV-8102A/B a disc with a pressure-equalising hole, as CV-2121A-D on the pump columns, or vent the HV-8108x cavity to the pump side. Correct the P-08 note. |
| 2026-11-05-basic-design-4#6 | sequences, C&E | SEQ-BOG-START; XV-7123A (B, C), I-702 / I-703A / I-705A, XV-7130 / I-704 | SEQ-BOG-START opens the suction XV-7121A and starts K-7101A on recycle, but no step opens the discharge isolation XV-7123A. XV-7123A fails closed and is closed, latching, by I-701, I-702, I-703A and I-705A. After any trip, the restarted machine therefore stays on full recycle behind a closed discharge valve, and S2 ("PIC-7101 auto") cannot load it. The sequence also does not check that XV-7130 is open again (I-704 resets automatically). | low | open | Add to S2: XV-7123A open (with ZSO or position feedback), then XV-7130 proven open, then PIC-7101 in auto. State that the sequence is run per machine (B, C). |
| 2026-11-05-basic-design-4#7 | philosophy, C&E | F-AIR; I-705A-C, XV-7121A-C, ZSO-7121A-C | F-AIR says that on a loss of instrument air "the compressors keep running on their guide vanes". The suction valves XV-7121A-C fail closed, and I-705A-C stop every running machine once ZSO-7121x leaves the open position. All BOG compressors therefore trip on an air failure, and the boil-off goes to the flare only through XV-1115 on I-203 / I-303 (accumulator) or the tank PSVs. F-AIR also lists I-501, which nothing initiates on that failure (#1). | low | open | Rewrite F-AIR from the fail positions and the C&E: compressors stopped by I-705A-C, tank pressure to XV-1115 / PSVs, loading stopped by the air-header trip of #1. |
| 2026-11-05-basic-design-4#8 | P-01, P-05, P-06, P-07 | ZSC-5125 / ZSC-6125, ZSO-7121A-C, HS-5125 / HS-6125, UZ-7125C, UZ-1115 / PIC-1111 | The 1.7.0 regeneration (`54648679`) left drawing defects that the lint does not count. (a) The measuring lines of ZSC-5125 / ZSC-6125 start at (261, 175) mm and those of ZSO-7121A-C about 3 mm right of and below their valves, in free space. They do not touch XV-5125 / XV-6125 / XV-7121x on the sheet. The data model is right: `cheme show` gives "senses ... at XV5125" and "at XV7121A". But D-026.14 says the switches "are tied to their valves", and the sheet does not show it (crop `build/P-05_crop-225-165-290-195.png`; tiles `build/P-07_tile-A2.png`, `A3`). (b) The actuating signal lines of HS-5125 / HS-6125 and UZ-7125C run through their own bubbles (crops `build/P-05_crop-225-165-290-195.png`, `build/P-07_crop-365-125-400-155.png`). (c) On P-01 the PIC-1111 signal turns towards PV-1111 on the top edge of the UZ-1115 bubble, and that bubble overlaps the XV-1115 actuator. PIC-1111 reads as if it drove UZ-1115 (crop `build/P-01_crop-330-45-395-90.png`). | low | open | Put the sensing points on the valve symbols (as ZSO-4131..4136 and ZSC-1102 / 1103). Route the HS and UZ signal lines to the bubble edge. Move UZ-1115 clear of the PIC-1111 signal and of the XV-1115 actuator. Report the three patterns to cheme-as-code as missing drawing rules. |
| 2026-11-05-basic-design-4#9 | DESIGN.md, line list | D-020; N-8001 | Split from review 2 #9 (the drawn and undrawn users are now listed). D-020 still names N2 for "blanketing" without saying what is blanketed: no blanketing user is drawn, listed or deferred. The N-8001 line-list note still gives the line's duties as "seal gas, blanketing (D-020)", although N-8001 ends at LNG-5001 and serves only the berth purge and leak test. | low | open | Drop "blanketing" from D-020, or name its user. Limit the N-8001 note to the berth purge and leak test. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-design-3#1 | Flare valves XV-4131 / XV-4132 changed to fail open: tank header open to the flare on air failure | high | closed 886b0ad5 | P-04 lines 198 and 221: `FailActionClassification.FailClose`, `F.C.` for Inst_HS4131_System / Inst_HS4132_System. XV-4135 / XV-4136 are FailOpen (lines 244 / 267). P-04 note: "XV-4135 / -4136 fail open, XV-4131 / -4132 fail closed (D-026.1)" (tile `build/P-04_tile-C2.png`). The HS-4131 / HS-4132 notes agree. On an air failure the return goes to the tanks, and the flare branch BOG-4013 (berth side of XV-4135, tile C2) is shut. |
| 2026-11-05-basic-design-3#2 | XV-4131 commanded both ways during ESD-1 with off-specification vapour | medium | closed 886b0ad5 | C&E I-511 `all: [AI-4133 AAH, {interlock: I-501, state: not tripped}]`, and I-611 likewise with I-601. I-513 closes on `ZSO-4135 open` and (`AI-4133 normal` or `I-501 tripped`). The two never command XV-4131 at once. The unstated consequence for the tanks is split into new #4. |
| 2026-11-05-basic-design-3#3 | KO drum pump blocked in between HV-8106x and HV-8108x without relief | medium | closed 886b0ad5 | P-08 note at HV-8106A/B "cavity vent: drum side", and the sheet note: cryogenic vented-ball valves, unidirectional, so a pressure rise on the pump side relieves past the seat into D-8101 (tiles `build/P-08_tile-B1.png`, `B2`, `C3`). The line-list notes for LNG-8002 / 8003 and D-026.14 agree. The spool between the check valve and HV-8108x is split into new #5. |
| 2026-11-05-basic-design-3#4 | Single open-position switch per switching valve; a stuck ZSO closes the return at both valves | low | open | Not answered. D-026.14 says "one open-position switch per switching valve is enough because only the proven-open state is used", which is the very state a switch stuck in "open" fakes. I-512 still closes XV-4135 on ZSO-4131 alone. There is no closed-position switch and no discrepancy alarm against the command. The proposed action of review 3 stands. |
| 2026-11-05-basic-design-3#5 | LIC-8101 duty/standby drawn as a chain through HS-8101A | low | accepted: the standby no longer depends on the chain for the hazard. I-802 starts both pumps directly on LZT-8105 (independent of LIC-8101 and of the HS chain), non-latching, and I-803 stops both. The residual is availability of the level band only. By Claude (independent review agent), for the human reviewer to confirm at sign-off | P-08 tile `build/P-08_tile-B1.png`: LIC-8101 -> HS-8101A -> HS-8101B still drawn as a chain (D-026.14 keeps it). C&E I-802 effects P-8101A start and P-8101B start; I-803 effects both stop. |
| 2026-11-05-basic-design-3#6 | PZT-7113 1oo1 stops every running compressor | low | accepted: a spurious trip sends the BOG to the flare through PV-1110 / XV-1115, a production and flaring loss with no hazard. The 5 s on-delay limits spurious trips, and the voting is left to the SIL screening, as recorded in the I-705A-C notes. By Claude (independent review agent), for the human reviewer to confirm at sign-off | C&E I-705A / B / C: `PZT-7113 PALL` with `delay: 5 s` inside the `any`. The notes give the 1oo1 choice and its consequence. |
| 2026-11-05-basic-design-3#7 | SEQ-LOAD S6 closes XV-5161 before the N2 purge | low | closed 886b0ad5 | SEQ-LOAD S6: XV-5161 open, drain, N2 purge "leaves through XV-5161, D-5101 and its vent BOG-5002", then XV-5161 close. D-026.13 states "XV-5161 / XV-6161 stay open during that purge". |
| 2026-11-05-basic-design-3#8 | Top/bottom fill change make-before-break not written anywhere | low | open | D-026.4 now states the operator step and that a change closing both branches trips I-102 through PZT-1105. But neither `control/sequences.yaml` nor `process/narrative.md` (grep for the fill change, XV-1106, "selection valve": no hit) nor `control/philosophy.md` writes it as a step. XV-1106..1109 (HS, fail last) have no position feedback, so "proven open" cannot be checked. The finding asked for the step in a control file, and DESIGN.md text alone does not close it. |
| 2026-11-05-basic-design-3#9 | D-7101 fire case missing from the tank PSV relief cases | low | closed 886b0ad5 | special-items lines 13-15 and 22-24, PSV-2131A-C / PSV-3131A-C: "..., fire on D-7101 and the BOG suction header (D-026.12)". |
| 2026-11-05-basic-design-3#10 | Sheets rebuilt from scripts but not declared as generated; frames in `build/` | low | closed 886b0ad5 | plant.yaml lines 31-46: `generator: {script: scripts/draft_P-0N.py, frame: pid/frames/P-0N.xml}` for all eight sheets. `pid/frames/P-01..P-08.xml` are committed. `cheme validate` at HEAD reports no `generator-undeclared` and no `generated-sheet-drift` (the generated sheets are rebuilt and compared). D-021 is corrected. |
| 2026-11-05-basic-design-2#2 | Hybrid-arm permissives written as trips on the valve in service | medium | open | The effect moved from XV-5123 to `{tag: HS-5123, action: trip}`, but the logic is unchanged: `all: [XV-5123 open command, ZSC-5125 not closed]`. With XV-5123 open, its open command held and ZSC-5125 failing to "not closed", the logic is true. Tripping the hand switch of a fail-closed valve with a held open command closes it under full flow. The notes say "an open valve is never closed by it", but the logic decides. The condition that review 3 proposed, `{tag: ZSC-5123, state: closed}`, is still missing from I-504 (I-505 with ZSC-5125, I-604 / I-605). |
| 2026-11-05-basic-design-2#9 | N2 users of D-020 not drawn or listed | low | closed 886b0ad5 | D-020 now names the drawn N2 users (berth tie-ins N-8001 / N-8002, pump-column hose connections) and the undrawn ones (compressor seal gas and purge, tank inerting, trestle purge points; D-026.9). The P-07 note says "N2 purge connections per machine: vendor package, not drawn (D-026.9)". The leftover "blanketing" is split into new #9. |
| 2026-11-05-basic-design-2#10 | No relief device sized against its governing case | medium | accepted: relief sizing is a detail-stage calculation; D-025 records the cases and D-026.8 / D-026.14 add the FO-1117 blow-by and the D-7101 fire. By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged. The air-failure surge case for PSV-5131 / PSV-6131 is part of new #1. |
| 2026-11-05-basic-design-2#11 | No O2 limit for carrier vapour to the flare | low | closed 886b0ad5 | D-026.7 states the limits. C&E I-514 / I-614 (AI-4133 / AI-4134 "O2 AHH (5 vol %)", 10 s, latching) close XV-5122 / XV-6122. BOG-5002 / BOG-6002 join BOG-5001 / BOG-6001 downstream of XV-5122 / XV-6122 (tile `build/P-05_tile-B3.png`, line-list note of BOG-5002), so the jetty relief path stays open. The gaps of I-514 are new #2. |
| 2026-11-05-basic-design#23 | Design case: three liquid arms leave one vapour arm (~23.5 t/h) against the 45.6 t/h return | medium | open | D-026.6 now calls the 45.6 t/h "a conservative envelope that no line-up returns through the arms": line-up (a) is arm-limited at ~23.5 t/h, (b) gives ~34 t/h. The compressors and the DN 750 lines keep it as margin. That settles the sizing basis. The flowsheet still contradicts it: stream S5 "Carrier return vapour", loading case 45,571 kg/h, is linked to BOG-5012 / BOG-6012, the outboard line of the single vapour arm (`process/flowsheet.yaml` lines 319-333). The issued heat and material balance thus routes through one arm twice its capacity, in a line-up that D-026.6 says does not exist. Proposed: label the loading case as the BOG envelope with S5 split into the arm-limited return and the balance burnt on board (or recomputed for line-up (b)). |
| 2026-11-05-basic-design#1 | DR-5001 / DR-6001 header drain without a valve | critical | closed 7bf89f18 | Rewritten from `589c9ca7` (review 2). At HEAD: XV-5161 / HS-5161 on DR-5001 between the LNG-5001 tee and the relief tees, PSV-5131 downstream of it (tile `build/P-05_tile-B1.png`). P-06 is the same with XV-6161 (`build/P-06_tile-B1.png`). The drum vent BOG-5002 stays open. |
| 2026-11-05-basic-design#2 | Drain pump without check valve, isolation or minimum flow | high | closed 7bf89f18 | Rewritten from `589c9ca7`. At HEAD on P-05: HV-5115, FO-5118 to the drum, HV-5119, CV-5116, PSV-5118, HV-5117 (tiles `build/P-05_tile-A1.png`, `B1`). P-06 is the same. |
| 2026-11-05-basic-design#3 | Hybrid arm liquid/vapour isolations not interlocked | high | closed 7bf89f18 | Rewritten from `589c9ca7`. ZSC-5123 / ZSC-5125 and I-504 / I-505 (I-604 / I-605) at HEAD. How they are written is review 2 #2 (open, medium). |
| 2026-11-05-basic-design#4 | ESD-2 does not trip ESD-1; delay holds back the pump stop | high | closed 13a1261f | Rewritten from `fac0bbb5` (review 3). At HEAD: I-501 `any` contains `{interlock: I-503, state: tripped}`. I-503 has no delay. I-507 closes the ERS valves on I-503 tripped with `delay: 5 s`. I-601 / I-603 / I-607 are the same. The air-failure case that #4 also named is new #1. |
| 2026-11-05-basic-design#5 | Fill branches without thermal relief | high | closed 7bf89f18 | Rewritten from `589c9ca7`. PSV-1122 on LNG-1002 below XV-1102 and PSV-1123 on LNG-1001 beside XV-1103, into BOG-1001 (tiles `build/P-01_tile-B1.png`, `B2`). |
| 2026-11-05-basic-design#6 | Tank-end headers, crossover and circulation return without thermal relief (and the PSV-4113 / 4114 outlets, disputed) | high | closed 13a1261f | Rewritten from `fac0bbb5`. PSV-2141 / 2142 (P-02 tiles A1 / A2), PSV-3141 / 3142 (P-03), PSV-4113 on LNG-4006 and PSV-4114 on LNG-4005 (P-04 tiles A1 / B1). BOG-4015 / BOG-4016 join BOG-4001 on the tank side of XV-4135 (tiles `build/P-04_tile-B1.png`, `C1`). |
| 2026-11-05-basic-design#7 | Liquid arm sections without thermal relief | high | closed 7bf89f18 | Rewritten from `589c9ca7`. PSV-5171 / 5173 / 5174 into DR-5001 downstream of XV-5161 (tiles `build/P-05_tile-B1.png`, `B2`), and PSV-6171 / 6173 / 6174 on P-06. |
| 2026-11-05-basic-design#8 | Rundown dead-headed when no tank can take it (ZSC-1102 / 1103 tie, disputed) | high | closed 13a1261f | Rewritten from `fac0bbb5`. ZSC-1102 / ZSC-1103 measuring lines start at the XV-1102 / XV-1103 valve symbols (tile `build/P-01_tile-B2.png`). I-102 is `any: [all: [ZSC-1102 closed, ZSC-1103 closed], PZT-1105 PAHH]`, and PZT-1105 is drawn on LNG-1001 (tile B1). |
| 2026-11-05-basic-design#9 | Anti-surge recycle uncooled; no high discharge temperature trip | high | closed 7bf89f18 | Rewritten from `589c9ca7`. The recycles BOG-7008 / 7009 / 7012 return to BOG-1001 upstream of the spray TV-7103 (P-07 note, tiles `build/P-07_tile-B1.png`, `C1`). TZT-7112A-C (tiles B2 / B3) trip through I-703A-C. |
| 2026-11-05-basic-design-2#1 | De-inerting switch lets ESD-1 close the vapour return at both valves | high | closed 13a1261f | Rewritten from `fac0bbb5`. I-501 / I-601 open XV-4135 / XV-4136 and do not act on XV-4131 / XV-4132. I-512 closes XV-4135 only with ZSO-4131 open and I-501 not tripped. I-513 closes XV-4131 only with ZSO-4135 open. ZSO-4131 / 4132 / 4135 / 4136 measuring lines start at their valve symbols (tiles `build/P-04_tile-C1.png`, `C2`). |

## Items raised against review 3 by its adversarial check

These eight were not findings of a record. Each one was judged on the C&E and sequences at HEAD.

1. **I-802 starting the wrong pump: closed.** I-802 now starts P-8101A and P-8101B ("whichever
   is not running"), so the standby starts whatever the duty selection.
2. **I-802 / I-803 priority: closed.** Both use LZT-8105, so high-high and low-low exclude each
   other. I-802 is non-latching, and the I-802, I-803, LZT-8105 and HS-8101A/B notes state the
   priority of I-803. The schema has no priority field.
3. **The S3 ESD-1 test aborting SEQ-LOAD: closed.** The abort condition is now `all: [I-501
   tripped, "not the ESD-1 test of S3 (test mode)"]`, or I-503 tripped. The missing end of the
   test mode is part of new #3.
4. **XV-4101 / 4102 not reopened after the S3 test: closed for the first test.** S3 resets I-501
   and opens XV-4101, XV-4102, XV-5101 and XV-5121. The repeated test after cooldown is new #3.
5. **SEQ-LOAD unable to run line-up (b) of D-026.6: closed.** S4 carries both line-ups. Line-up
   (b) opens XV-5125 under I-505, with P-2101A/B/C and FIC-4101 / 4102 at 4,000 m3/h each. S0
   only requires XV-5125 closed before S4. The I-514 gap in line-up (b) is new #2.
6. **SEQ-HOLD not lining up XV-4101 / 4102: closed.** SEQ-HOLD S1 opens XV-4101 and XV-4102,
   puts FIC-4101 / 4102 in manual with FV-4101 / 4102 fully open, and its complete condition
   includes both valves open.
7. **The I-705A-C bypass note: closed.** The "no start bypass is needed" note is consistent
   with the logic. The `all` contains "K-7101x running", SEQ-BOG-START S1 opens XV-7121A before
   the start so ZSO-7121A is open when the machine runs, and the PZT-7113 PALL term has its
   5 s on-delay. The trip is latching with manual reset, so it holds after the machine stops.
8. **The I-611 note naming BOG-4013: closed.** It now reads "through BOG-4014". BOG-4014 joins
   BOG-4013 (P-04 tile C2, line list).

## Drawing

`cheme validate` drawing lines at `54648679` (core 1.7.0 adds line-through-valve, line-on-pipe
and line-not-orthogonal):

- P-01, P-02, P-03, P-05, P-06: 0 line-through-label, 0 line-crossing, 0 label-overlap,
  0 label-far-from-owner, 0 text-outside-frame, 0 title-text-overflow, 0 line-through-symbol,
  0 line-through-valve, 0 line-on-pipe, 0 line-not-orthogonal.
- P-04: 0 line-crossing (+2 accepted: BOG-4011 x LNG-4002 and BOG-4015 x LNG-4002, reason
  D-026.11). I agree: line B runs across the sheet between off-page connectors, so any outlet
  from the line-A side must cross it once to reach BOG-4001. All other counts are 0.
- P-07: 0 line-crossing (+2 accepted: BOG-7001 x BOG-7009 and BOG-7002 x FL-7004, reason
  D-025, unchanged). All other counts are 0.
- P-08: 0 line-crossing (+1 accepted: the HS-8101B measuring line x LNG-8001, reason
  D-026.11). It stays while the chain of review 3 #5 is kept (accepted above). All other counts
  are 0.

The counts are 0, but the lint misses the defects of new #8: measuring lines that start off
their valve, signal lines through their own bubbles, and a bubble on another loop's signal
corner.

Tiles read (`cheme render pid/<sheet>.xml --png --tiles auto`, 3x3 at scale 8):
- P-01: A1-C3, all nine.
- P-02: A1-C3, all nine.
- P-03: A1, A2, B1, B2, C1, C2. The three right-hand tiles A3, B3 and C3 hold only off-page
  arrows, open frame and the title block. They are identical in layout to P-02 A3 / B3 / C3,
  which I read.
- P-04: A1-C3, all nine.
- P-05: A1, A2, A3, B1, B2, B3, C1, C2, C3.
- P-06: A1, B1, B2, B3, C1. A2, A3, C2 and C3 are the same layout as P-05 (identical diff
  counts since review 3, 33 lines each).
- P-07: A1-C3, all nine.
- P-08: A1-C3, all nine.

Close crops at scale 12-14:
- `build/P-01_crop-330-45-395-90.png` (PV-1111, UZ-1115, XV-1115);
- `build/P-05_crop-225-165-290-195.png` (XV-5123 / XV-5125, ZSC, HS);
- `build/P-07_crop-365-125-400-155.png` (UV-7104C, XV-7125C).

Topology and fail positions:
- Settled with `cheme show` for ZSC-5125, HS-5125 and ZSO-7121A.
- The FailAction of every ActuatingSystem on the eight sheets was read from the XML. P-08 has
  no actuated valve.

## Mechanical checks (non-layout)

- `cheme validate`: 82 files, 0 errors, 23 warnings. All 23 warnings are
  `cheme.hazop-input-changed` in safety/hazop/H-01..H-05, which another agent is restamping and
  which are outside this scope. The last line compares 10 sheets and 25 lists. The lists vs
  P&IDs cross-checks report 0 findings: equipment, lines and DN, instruments, piping items and
  interlocks. Non-layout infos in scope:
  - 18 `cheme.instrument-no-interlock`:
    - UZ-1115, UZ-7121 / 7123 / 7125 A-C and UZ-7130: a naming convention, their XV are the
      effects;
    - HS-4131, which is new: its notes name I-511 / I-513, whose effects are XV-4131;
    - LIC-5111 / 6111, LIC-8101, LI-8103 and HS-8101A/B: regulatory start/stop.
  - 8 `cheme.control-shared-element`: the compressor stop shared by PIC-7101, and LV-7102 with
    I-802. These are meant.
  - 30 `cheme.control-logic-text`: sequence text, acceptable at basic.
  - 12 `cheme.offpage-mismatch`: accepted under D-021.4.
  - 5 `cheme.line-crossing`: the accepted crossings above.
  - 114 `cheme.label-tag`: I sampled them on the sheet notes. None names a removed tag:
    PSV-7105, FL-7001 and PV-2111 appear nowhere in the sheets and lists.
- `cheme check --stage basic`:
  - ok: design-basis, concept-lists, process-concept, process-balances, process-links-concept,
    process-basic, process-links, assumptions-marked, pids-valid, drawing-clean, pids-exist,
    layout-plot-plan, layout-3d, lifting-study, mto, issues-concept, issues-basic,
    tank-protection-on-pid, berth-arms-on-pid, bog-compressors-on-pid,
    relief-inlet-isolation-on-pid, trip-sensors-on-pid.
  - FAIL design-review, before this record: the three earlier records name `reviewed_commit`s
    that the rebase removed from HEAD's history (`7bcea968`, `75e0b9fc`, `fac0bbb5`). On a
    re-run with this record (`--only-stage`) the gate is ok ("agent review of 546486794c28").
    A sign-off is still refused while #1 (high) is open.
  - FAIL layout-review, before this record: `reviews/2026-11-05-basic-layout.md` names
    `0603eeed`, which is also no longer an ancestor of HEAD. On the re-run it is ok, through
    `reviews/2026-11-05-basic-layout-2.md`, which another agent wrote during this review. That
    is layout scope, not reviewed here.
- `cheme validate --only 'cheme.review-*'` after writing this record: 0 errors, 0 warnings.

## Checked and fine

- **Vapour return switch at HEAD.** In every state the C&E allows, the berth relief path stays
  open to the tanks or to the flare:
  - on an air failure: XV-4135 opens and XV-4131 closes;
  - on ESD-1: I-501 opens XV-4135, then I-513 closes XV-4131;
  - in normal switching: make-before-break by I-511 / I-512 / I-513.

  A spurious closure of XV-4131 while XV-4135 is closed drops ZSO-4131. I-512 is non-latching,
  so XV-4135 then reopens within its stroke time.
- **Air failure, apart from #1.**
  - The tanks: PV-1110, PV-1111 and XV-1115 close, and XV-1115 still opens on I-203 / I-303
    from its accumulator.
  - The trestle lines between XV-4101 / 4102 and XV-5101 / 6101 relieve through PSV-4111 /
    4112 into BOG-4001 on the tank side of XV-4135.
  - The arm sections relieve through PSV-5171 / 5173 / 5174 into DR-5001 downstream of
    XV-5161.
  - The vapour arm XV-5122 closes. The drum vent BOG-5002 joins downstream of it, so D-5101 and
    the jetty PSVs still vent to the tanks.
- **Blocked-in cryogenic sections.** I walked every valved LNG section on P-01, P-02, P-04,
  P-05 and P-08 for thermal relief: the fill branches, the pump and circulation headers, the
  crossover and circulation return, the trestle lines, each arm, the drain pump, and the KO
  drum pumps up to their check valves. All have relief except the spool of new #5.
- **Flare paths.** On P-08, FL-8001 takes PV-1110 / XV-1115, PSV-7111, the compressor vents
  FL-7003 and BOG-4013 / BOG-4014. FL-8001 has a continuous fuel-gas purge (FG-8001, FO) and
  goes through D-8101 to FL-8101.
- **The compressors.** Each machine is isolated at suction and discharge on its trips and keeps
  its recycle open, and PSV-7111 sits between XV-7123x and XV-7130.
- **ESD / ERS logic.**
  - I-501 / I-601 stop the pumps, close XV-5101 / 6101, XV-4101 / 4102 and XV-5161 / 6161, and
    open XV-4135 / 4136.
  - I-503 / I-603 trip them at once.
  - I-507 / I-607 close the ERS valves 5 s later.
  - SEQ-ESD S1 agrees with all of this.
- **Vacuum protection.** I-204 / I-304 stop the withdrawal and the compressors. The vacuum
  relief valves PSV-2133 / 3133A-C are N+1 with locked-open isolation (P-02 / P-03 tiles B2 /
  C2). No air-failure state opens a vent, so the tanks are not depressurised.
- **Sequences.**
  - SEQ-HOLD S1 now circulates the whole trestle loop.
  - SEQ-LOAD S6 purges with XV-5161 open.
  - The two line-ups of S4 respect I-504 / I-505.
  - S0 stops the circulation for up to about 3 h before the cooldown. With 200 mm PIR on the
    DN 800 lines the heat-in is of the order of 0.3 K in that time, so no vapour forms in the
    lines (my estimate, not a finding).
- **Lists and sheets.**
  - The line-list notes of BOG-4013 / 4014, BOG-5002, DR-5001 and LNG-8001 / 8002 / 8003 agree
    with the drawn order of the items.
  - The relief cases in special-items agree with the drawn devices.
  - The equipment list was cross-checked by validate.

## Not checked

- Tiles: P-03 A3 / B3 / C3 and P-06 A2 / A3 / C2 / C3 were not read. They were compared with
  their twin sheets, as stated under Drawing.
- The Berth 1 interlocks I-601..I-614 were compared with Berth 2 in the C&E text, and on the
  P-06 tiles read. They were not traced one by one on the drawing.
- Calculations for the designer and the vendors:
  - relief, vacuum valve and flare sizing (accepted review 2 #10);
  - the surge transient with the ERS and ESD closure times, including the air-failure closure
    of #1;
  - the stroke and accumulator capacity of XV-1115 and of the ESD / ERS actuators;
  - the trains' fuel-gas capacity for the make-up;
  - the vented-ball behaviour of HV-8106A/B, to be confirmed by the valve vendor.
- The SIL study: the voting of PZT-7113, AI-4133 / 4134 (I-514), ZSO-4131..4136 and the
  proposed air-header trip.
- process/narrative.md was searched only for the fill change (review 3 #8). control/loops.yaml
  was checked only for fail positions.
- process/flowsheet.yaml was used as a basis only, read for the stream S5 of review 1 #23.
- The HAZOP studies (safety/hazop): another agent was editing them, and their 23
  `hazop-input-changed` warnings remain.
- Layout, routing, the 3D model and the stale layout review record.
- Area classification, materials, fire and gas, and the vendor packages: arms, ERS couplers,
  compressor UCP, flare derrick.
