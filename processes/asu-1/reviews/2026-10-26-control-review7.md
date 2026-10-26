---
topic: control
reviewed_commit: a793d37d4b397f229afa41db8163fac005b93d9e
scope: [control/loops.yaml, control/sequences.yaml, control/cause-effect.yaml, control/instrument-list.yaml, control/philosophy.md, process/narrative.md, pid/P-02.xml, pid/P-03.xml, pid/P-04.xml, DESIGN.md]
reviewer: Claude (independent control review agent; did not author D-114 or D-115)
reviewer_kind: agent
branch: claude/keen-lovelace-sd87qc
merge: pending
---
# Review: control intent of ASU-1, seventh review (confirming the D-114 fixes)

This is an independent review of branch `claude/keen-lovelace-sd87qc` at a793d37. It checks each
finding of control-review6 against D-114 (commit 0841d30) and, where the HAZOP carries the fix,
D-115 (a793d37). It also looks for defects that the fixes introduced. The scope is the same as
control-review6. Every record is still "PROPOSED". This agent record approves none of them, and
the merge is a human's decision.

Checks run at a793d37:
- `cheme validate` (all rules, with generators): `129 file(s): 0 error(s), 97 warning(s)`.
  - The 2 warnings more than at 8ccc323 are the new `layout-tray-span` warnings for
    IT-JB-A1-S1 and IT-JB-A3-S1 (layout-review29).
  - There is no `instrument-no-interlock` and no `cheme.control-*` warning.
  - PSLL-1116 shows as `instrument-not-on-pid` (info, accepted in checks/checks.yaml).
  - Control infos: 59 `control-unresolved`, each naming its issue; 34 `control-shared-element`;
    15 `control-logic-text`; 10 `control-incomplete`.
- `cheme check --no-write` fails three gates:
  - `layout-review`, because no layout record was current at a793d37 (layout-review29 is
    written for it);
  - `issues-basic` (#56, #57, #60, #61, #79);
  - `issues-detail` (17 items, including the new #106).

  Every other gate is ok.
- `git diff --stat 8ccc323 a793d37` shows no P&ID changed (`cheme diff 8ccc323 --list`: "No
  P&ID changed"). The control files changed in 0841d30: cause-effect.yaml (I-14, new I-19),
  instrument-list.yaml (PSLL-1116 and access notes), loops.yaml (FIC-4148, FIC-3107, PIC-4101)
  and philosophy.md (F-AIR, F-AIR-POWER-ON, F-GOXC). DESIGN.md gained D-114 and D-115.

**LOPA arithmetic of D-114 (3), row by row.**
- Row 3: 0.1 x 0.1 x 0.1 x 0.1 = 1e-4 against 1e-5, so RRF 10 and SIL 1.
- Row 4: 0.3 x 0.1 = 3e-2 against 1e-1, so RRF < 1.
- Row 6: 0.4 against 0.1, so RRF 4 and SIL a.
- Row 8: unchanged at 1e-3 against 1e-5, so RRF 100. It is now conditional on a redundant
  seal-gas supply.
- Row 9: unchanged, RRF 10.
- Row 10: 0.1 x 0.1 x 0.1 = 1e-3 against 1e-5, so RRF 100 and SIL 2.
- Row 14: 1 x 0.1 = 0.1 against 0.1, so RRF 1.
- Row 15: 0.1 x 0.1 = 1e-2 against 1e-3, so RRF 10 and SIL 1.

Every product, ratio and IEC 61511 band is right. What is wrong lies in what goes into the
products:
- row 10's initiating frequency (#2);
- a new ignition modifier in rows 3 and 10 (#3);
- row 4's cross credit (control-review6#7, still open);
- row 14's clamp credit (control-review6#6, still open);
- the asset targets (control-review6#5, still open).

**Verdict.** Both high findings of control-review6 are closed:
- I-14 now stops the air and K-4101 through their motor breakers.
- I-19 stops the plant on instrument air low-low.

Of the 14 findings, 10 are closed and 1 (#12) is accepted. Three medium findings stay open: #5,
#6 (row 14) and #7 (row 4).

This record raises 3 medium and 4 low new findings. None is high. The most important is #1:
after the trip, the HP column inventory keeps E-3103 boiling for a while. "Once the air stops,
nothing boils" is the basis of I-14 in the C&E and in five HAZOP credits, so the LSLL-3125
margin has to cover that boil-off.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-26-control-review7#1 | P-03 | I-14 (LSLL-3125), D-114 (1), C&E I-14 note, E-3103, C-3101 | **"Once the air stops, E-3103 stops boiling" is not true at the moment of the trip.** D-114 (1) and the I-14 note rest the function on this claim: "with no air the HP column sends no vapour to E-3103, so the condenser stops boiling whatever still drains the sump ... and nothing concentrates in it". When the MAC trips, two sources of vapour are left. (a) The air held at about 6 bara in the DCAC, the TSA vessels and the main exchanger keeps flowing into the HP column until the pressures equalise; the check valve on AIR-1002 only stops back-flow. (b) The HP column vapour, and the HP sump liquid and reflux that flash as the HP pressure falls, keep condensing in E-3103. This continues until the HP condensing temperature drops to the LP sump boiling temperature. Every kg condensed boils LP sump liquid. Meanwhile a failed-open FV-3111 or PV-4101B (the causes I-14 is now credited for) keeps draining. The boil-down therefore goes on for some minutes past the trip point, and so does the concentration of hydrocarbons, though at a falling rate. Whether that boil-down uncovers E-3103 depends on the margin between the LSLL-3125 trip and the E-3103 top. That margin is "by the supplier's margin" (#103), and it is not sized for a post-trip boil-off. The "Not checked" item of control-review6 (the HP inventory after air loss) has now become load-bearing. | medium | open | Estimate the post-trip boil-off: the HP column and the air-path inventory against the pressure decay (a hand estimate or the dynamic check, #103). Set the LSLL-3125 trip so that the sump level after the boil-off and after the worst remaining drain (FV-3111 full open) still covers E-3103. Reword the I-14 note, D-114 (1) and the HAZOP bases from "stops boiling" to "the boil-off ends within N min and is covered by the trip margin". |
| 2026-10-26-control-review7#2 | - | LOPA row 10 (I-14) initiating event, D-114 (3) / (4), H04-S80 | **Row 10 still takes its initiating frequency from the ratio limit that D-114 (4) itself says does not cover the cause.** D-111 row 10 sets "over-draw or refrigeration deficit 0.1 (with the D-110 ratio limit, which takes the no-failure causes of S80 out)". D-114 (3) recalculates row 10, but it keeps that initiating event. Yet D-114 (4) states that a make which falls at a constant air flow (the TSA switchover dip, a purity upset) is not tracked by the ratio. D-115 accordingly rates the H04-S80 cause frequency E (about once a year or more often: the dip comes every cycle). At about 1 /yr, with the same modifiers, row 10 needs RRF 1000, which is the SIL 2 / 3 boundary. The no-failure branch is not initiated by the control system, so the LICA-3102 low alarm (removed from row 10 because "the initiator may be the control system") could be credited on that branch. That would bring it back to RRF 100, but only with the row split by initiator. | medium | open | Split row 10 by initiator. (a) Control-system failures (selector, FT-4148, PT-4150, FV-3111 / FIC-3111, PV-4101B): 0.1, no alarm credit. (b) A make that falls at a constant air flow: the frequency that H04-S80 uses, with the LICA-3102 alarm credited once. (c) A refrigeration deficit. Take the highest RRF, and make the row's text and H04-S80 agree. |
| 2026-10-26-control-review7#3 | - | LOPA rows 3 and 10, D-114 (3) | **A new "ignition" modifier replaces each removed credit one for one, so neither SIL changes.** Row 3 lost the LOX purge credit (0.1) and gained "ignition given an accumulation 0.1". Row 10 lost the LICA-3102 alarm (0.1) and had its modifier split: D-111's "hydrocarbons concentrated to ignition while uncovered 0.1" became "hydrocarbons concentrated 0.1" x "ignition 0.1". The D-111 modifier already included the ignition, so row 10 now counts it twice. The CCPS ignition-probability modifiers are meant for flammable releases to the open air. In a dry-boiling bath condenser, the ignition (deposits, particle impact, the dry boiling itself) comes from the same mechanism that concentrates the hydrocarbons, so it is not an independent condition. Without the new modifier, row 3 needs RRF 100 (SIL 2, the second analyser that H02-A1 already names conditionally) and row 10 needs RRF 1000. | medium | open | Drop the separate ignition modifier, or justify it with a source specific to hydrocarbon ignition in LOX condensers and show that it is independent of the concentration modifier. Recompute rows 3 and 10 (with #2) and hand both to the LOPA / SIL session (#106) with the 1oo2 options (H02-A1, H03-A4). |
| 2026-10-26-control-review7#4 | P-03 | I-14 reset and restart, philosophy F-GOXC, C&E I-14 bypass | **After a genuine I-14 trip there is no stated way back.** I-14 latches on a low LP sump with the MAC stopped. With no air, the sump level cannot rise, so I-14 cannot be reset. F-GOXC nevertheless says the operator "restores the LP sump level with the purge still on ... and restarts the MAC first". The only bypass in the C&E is "start-up only, until the sump level is above the trip during the cool-down (SEQ-CB-START)". A warm restart after a trip is not a cool-down. Separately, F-GOXC's `interlocks:` list is [I-13, I-14, I-17], although its text and D-114 (8) name I-19. | low | open | State the restart after an I-14 trip: the MAC restart under the I-14 start-up bypass (timed, with a permit, K-4101 stopped) until the level is above the trip. Let the bypass condition in the C&E cover a restart. Add I-19 to F-GOXC's `interlocks:`. |
| 2026-10-26-control-review7#5 | P-01 .. P-04 | D-114 (5), D-109 table | **The single-signal check leaves out several D-109 elements.** D-114 (5) does not mention these elements: XV-3105 (opens alone: GAN diverted to VNT-4004 continuously in normal operation, an N2 release at the vent and the product lost); XV-3117 (closes alone: the expander stops, which is a refrigeration deficit that ends in an I-14 demand); XV-2109 (opens alone: the heater is bypassed, caught by I-08); XV-2111A/B and XV-2112A/B (close alone: a step held); LV-1114 / XV-1115 (closed alone); UV-3120, UV-4103 and UV-4131 (open alone: recycle and throughput loss); XV-4136 / XV-4137 and the BL valves. Most of these are probably acceptable. XV-3105 and XV-3117 should be stated. | low | open | Add the missing elements to the D-114 (5) list with the alarm or trip that catches each, and hand XV-3105 (a continuous N2 vent) and XV-3117 to the team with H04-A26 and H03-A1. |
| 2026-10-26-control-review7#6 | - | D-114 (4), loops FIC-4148 / FIC-3107 | **The validated air flow and the liquid correction are incomplete.** (a) The second flow, "the MAC vendor's own flow measurement (UIC-1102's)", has no tag in the instrument list, and UIC-1102's only measurement is UIC-1102 itself. Whether it is independent of FT-1101 (its own element, or FT-1101 again) is not recorded. (b) The GOX limit subtracts the LOX drawn above design, but the FIC-3107 GAN clamp does not subtract the LIN drawn above design. (c) The FIC-3107 rationale says "the validated, lagged air flow of FIC-4148", which reads as if FIC-4148 measured air. | low | open | List the MAC vendor's flow element (or note it with #58) and state that it is not FT-1101. Add the LIN correction to the GAN clamp, or say why none is needed. Reword (c) to "the validated, lagged air flow (as FIC-4148's limit)". |
| 2026-10-26-control-review7#7 | - | I-19, PSLL-1116, checks/checks.yaml accept | **The SIL 1 plant-stop sensor exists only in lists.** PSLL-1116 has no sheet, and C&E I-19 has no `sheet:`. The acceptance of `instrument-not-on-pid` says it "is drawn with the utility P&ID in detail engineering", but it names no issue, and no issue tracks a utility P&ID. As the only 1oo1 cause of a full plant stop, its spurious trip rate matters as much as its PFD. The set point is "above the pressure at which the actuators start to move (ASSUMED, IA package)", with no issue for that value either. | low | open | Name an issue (or #103 / #106) in the acceptance and in the I-19 note for the utility P&ID and the set point. State the architecture (1oo1, or 2oo3 to limit spurious plant stops) in the I-19 note for the SRS. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-26-control-review6#1 | I-14 does not end the over-draw in several causes it is credited for. | high | closed 0841d30 | C&E I-14 effects are now K-1101 trip, UV-1102 open, P-1101A/B and P-1102A/B trip, K-4101 trip, XV-4117 / XV-4118 close, XV-4116 open. FV-3111 is no longer an effect. Stopping the air ends the condenser's vapour feed, whatever drains the sump: PV-4101B, FV-3111 or a refrigeration deficit. The "no more than the make" claim is removed. Row 10 and the H-03 / H-04 bases were revised (a793d37). The remaining caveat on the post-trip boil-off is #1. |
| 2026-10-26-control-review6#2 | On instrument-air loss with power on, nothing stops the running machines. | high | closed 0841d30 | New C&E I-19: PSLL-1116, 10 s delay, latching, trips K-1101 (with UV-1102 and the DCAC pumps), K-3101, K-4101 and K-4102. Philosophy F-AIR-POWER-ON states it, LOPA row 15 is SIL 1, and H01-S45 / H04-S95 carry it (a793d37). The sensor's documentation gap is #7. |
| 2026-10-26-control-review6#3 | I-14 closes FV-3111 and stops the LOX purge, against D-010 (2) and OBJ-3. | medium | closed 0841d30 | FV-3111 is removed from the I-14 effects, and the instrument-list, loops, philosophy and C&E texts now agree that the purge stays on (F-GOXC "with the purge still on"). H03-S35 no longer names I-14 (a793d37). |
| 2026-10-26-control-review6#4 | Fail positions checked on air loss only, not on a single signal loss. | medium | closed 0841d30 | D-114 (5) checks the elements one at a time, with the alarm or trip that catches each. The two cases needing the team are in H04-S92 and H04-S94 (a793d37). The elements it leaves out are #5. |
| 2026-10-26-control-review6#5 | D-111 asset tolerable frequencies disagree with the proposed risk matrix and D-083. | medium | open | The targets are unchanged. D-114 (3) now says they "sit in the matrix's medium (ALARP) band, not its low band". That is wrong: in safety/risk-matrix.yaml, 1e-1 at severity 3 is the D/E boundary (high), 1e-2 at 4 is C/D (high) and 1e-3 at 5 is B/C (high). H04-S95's notes show the effect: it "meets" the asset target and stays high. The decision is deferred to #106; the statement needs correcting. |
| 2026-10-26-control-review6#6 | BPCS layers credited in the LOPA, contrary to the records and the independence rules. | medium | open | Rows 3 and 10 are fixed: no purge credit, one or no alarm. Row 14 still credits the D-110 clamp as the one control-system layer "for the demand causes", which D-110 (4) and loops.yaml call "not protection layers". For the demand cause it does not track (a make that falls at a constant air flow, D-114 (4)), the clamp does not act, and H04-S85 refuses that same credit (a793d37). Without it, row 14 is 1 against 0.1: RRF 10, or the PIC-4106 alarm credit, so "no SIF on K-4102" is not shown. |
| 2026-10-26-control-review6#7 | I-08 and I-10 are credited for each other and each is left without a SIL. | medium | open | Row 6 is fixed (no I-08 credit, RRF 4, SIL a). Row 4 still credits I-10 at PFD 0.1. D-114 itself puts I-08, I-09 and I-10 in one heater protection relay, switching the same E-2101 supply, so I-10 is not independent of I-08, and I-10 stays SIL a with no PFD 0.1 requirement. D-115 accordingly credits the pair once in the HAZOP. Without the credit, row 4 is RRF 3, SIL a. |
| 2026-10-26-control-review6#8 | The seal-gas LOPA row starts optimistic and the trip does not stop the mechanism. | medium | closed 0841d30 | The C&E I-12 note and D-114 (3) make 1e-2 /yr conditional on a redundant seal-gas supply with automatic backup, as a requirement to the compander vendor (#58). They state SIL 2 / 3 at the boundary with a single supply, and give the run-down oil to the vendor (#58). |
| 2026-10-26-control-review6#9 | The D-110 ratio limits rest on FT-1101 alone and ignore the liquid draws. | medium | closed 0841d30 | The FIC-4148 rationale uses the lower of FT-1101 and the MAC vendor's flow with a deviation alarm, a 15 min lag (column supplier to confirm), and subtracts the LOX above 470 kg/h. H04-S80 names FT-1101 high (a793d37). The gaps left are #6. |
| 2026-10-26-control-review6#10 | The oxygen-fire trip I-13 is credited against an outcome that ignition already causes. | low | closed 0841d30 | The C&E I-13 note and D-114 row 9 restate the consequence as the escalation (a fire fed by the header and the LP column), with detection and closing within the vendor's burn-through time (#58). |
| 2026-10-26-control-review6#11 | The SIL 2 architectures are not stated, and FV-3111 is a final element of I-14. | low | closed 0841d30 | The C&E notes for I-11, I-12 and I-14 state voting, solenoids, final elements, proof tests and SIS junction boxes (ASSUMED, for the SRS). FV-3111 is dropped from I-14. |
| 2026-10-26-control-review6#12 | The LSLL-3125 tap is drawn above the LICA-3102 tap on P-03. | low | accepted: a P&ID shows the connection, not the elevation; drawing the tap below would cross LICA-3102's measuring line, and the elevations (I4 1.0 m below I3 1.6 m) are in the placement and the C-3102 datasheet with LSLL-3125's own vapour leg (D-114 (7)); by the author agent on the owner's delegation, agreed by this reviewer | C-3102 datasheet I1 / I3 / I4 with face, orientation and elevation. layout/equipment-placement.yaml C-3102 I3 / I4 / I1. P-03 unchanged (no P&ID in the diff). |
| 2026-10-26-control-review6#13 | The machine-trip responses in the philosophy do not name the new interlocks. | low | closed 0841d30 | F-GOXC names I-13, I-14, I-17, I-19 and the post-I-14 response. F-AIR names I-19, and F-AIR-POWER-ON lists the trips that air loss defeats (I-04 only). D-114 (8) corrects D-111 (6). The missing I-19 in F-GOXC's `interlocks:` list is part of #4. |
| 2026-10-26-control-review6#14 | Not every open point in D-109 .. D-111 names its issue. | low | closed 0841d30 | D-114 (8) maps them to #102 .. #105 and the new #106 (LOPA / SIL session, SRS, SIS). `cheme check` lists #106 under issues-detail. |
| 2026-10-26-layout-review28#1 | C-3102 I1 / I3 / I4 placed by default high on the shell. | medium | closed 0841d30 | The placement gives I4 1.0 m below I3 1.6 m on the north side (model z 21.0 / 21.6). Details, and the new finding on the stands, are in layout-review29. |
| 2026-10-26-layout-review28#2 | C-3102 manways turned by the default tappings. | low | closed 0841d30 | Back on the west face (layout-review29). |
| 2026-10-26-layout-review28#3 | PSHH-4152 modelled out of reach of VP-5, no operator declared. | medium | open | The stand on VP-5 is in the instrument list only. There is no `operators:` entry and no point in the electrical list, and the model point is unchanged (layout-review29). |
| 2026-10-26-layout-review28#4 | FSLL-2117 modelled at 5.7 m with no platform or operator. | low | open | The 1 m drop is in the instrument list only, and the model point is unchanged (layout-review29). |
| 2026-10-26-layout-review28#5 | Three junction boxes over their declared capacity. | medium | closed 0841d30 | Every box is at 24 field cables or fewer (layout-review29). |
| 2026-10-26-layout-review28#6 | SIF sensors share junction boxes and home runs with the BPCS. | low | closed 0841d30 | The SIS boxes JB-A1-S1, JB-A3-S1 and JB-A4-S1 are declared. The remaining gaps are layout-review29#3. |
| 2026-10-24-control-review5#3 | PIC-4101's tap drawn on S2 but modelled on S1. | low | open | No P&ID changed since 8ccc323 (`cheme diff 8ccc323 --list`: "No P&ID changed"). |
| 2026-10-24-layout-review23#2 | The model has no tap point per line-mounted instrument; no rule checks the reach of line-mounted transmitters. | low | open | D-114 (6) still cites #66 for it. PSHH-4152 and FSLL-2117 keep their old model points (layout-review29). |
| 2026-10-24-layout-review24#1 | The AI-3104 and FIC-4148 bubbles on P-04 are 0.5 mm apart and read as touching. | low | open | P-04 is unchanged since 8ccc323. |

## Drawing
No P&ID changed in 0841d30 or a793d37. `cheme validate` at a793d37 gives the same counts as at
8ccc323:
- P-01: 0 line-through-label, 2 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-02: 0, 0, 0, 0
- P-03: 0 line-through-label, 3 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-04: 0 line-through-label, 4 line-crossing, 0 label-overlap, 0 label-far-from-owner

All four sheets have 0 text-outside-frame, 0 title-text-overflow and 0 line-through-symbol.
These are the crossings accepted earlier, and `drawing-clean` is ok. Since no sheet changed, no
crop or tile was rendered for this record.

## Checked and fine
- **I-14 effect set:** the trip set of I-05 / I-06 (MAC, blow-off, DCAC pumps) plus the K-4101
  set. Its final elements are the motor breakers, apart from FV-3111, the selector and the BPCS.
  UV-1102 opening is protective and fails open anyway. The bypass excludes K-4101 running.
  The new H03-S54 consequence (a spurious trip stops the plant) is the right price to state.
- **I-19:** the effect list is complete for the running drives. XV-3117 and the ESD valves need
  no effect because they fail safe with the air. The 10 s delay is short against the minutes a
  machine can run on recycle. Row 15 arithmetic is right. The cable IC-PSLL-1116 goes to the
  SIS box JB-A1-S1.
- **D-110 revision:** taking the lower of two flows and of the 15 min lag acts in the safe
  direction. The LOX correction is 1:1 in O2 mass, which is right. D-114 (4) says honestly
  that a make falling at a constant air flow is not tracked.
- **D-114 (5):** the cases listed are caught as stated (spot checks of UV-1102, LV-1106 by I-06,
  FV-2105 by H02-S16, PV-4111 / PV-4112 by the header alarm).
- **Consistency:** the I-14 / I-19 texts in cause-effect.yaml, the instrument list, loops.yaml
  (FIC-4148 notes, PIC-4101 PAL response), philosophy.md and D-114 tell one story. The SIS
  junction boxes in the C&E notes match electrical/electrical-list.yaml.
- I found no third-party content in the changed control files.

## Not checked
- The HAZOP revision D-115 beyond the scenarios named here (hazop-review7).
- The layout, cable and junction-box changes of D-114 (6) (layout-review29).
- The post-trip dynamics of #1 (no dynamic model exists), the PV-3110A/B and PV-4101B capacities
  and PIC-4101's set-point window (#59).
- The machine vendors' protection and run-down (#58), and the SRS (#106).
