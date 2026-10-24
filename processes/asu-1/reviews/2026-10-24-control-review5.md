---
topic: control
reviewed_commit: 33fcaaa73307e73423811facfcfdc5d24ccfbad8
scope: [control/loops.yaml, control/sequences.yaml, control/philosophy.md, process/narrative.md, DESIGN.md]
reviewer: Claude (independent control review agent; did not author 33fcaaa, D-094, D-095 or D-096)
reviewer_kind: agent
branch: stage/basic-control
merge: pending
---
# Review: control intent of ASU-1, fifth review (confirming the review 4 fixes)

This is an independent process-control review of branch `stage/basic-control` at 33fcaaa
("control review 4 fixes: PIC-4101 / PIC-4150 swapped so the vent taps upstream of XV-4117;
bubble spacing, P-04 note, GAN clamp, windup and bumpless open points, F-GANC, H-04 hand-over
(D-096)"). It checks the findings that reviews/2026-10-24-control-review4.md left open: review 3
#6 and review 4 #1 to #7. It also looks for new problems, especially from the tag swap.

The changes were checked against:
- DESIGN.md D-019 and D-094 to D-096;
- the instrument list, the electrical list (junction boxes) and the cable schedule;
- P-04, read with `cheme show PIC-4101`, `PIC-4150`, `XV-4117`, `GOX-4001` and
  `Tee_GOX4001_V`, and the measuring-line anchors and sense positions in the XML;
- the HAZOP study H-04 (H04-N1, H04-S01, H04-S02, H04-S03, H04-S75, H04-SG06, H04-A23).

Checks run at 33fcaaa:
- `cheme validate` (all rules, with generators): `114 file(s): 0 error(s), 45 warning(s)`.
  - 9 warnings are `hazop-input-changed` (H-01 .. H-04). They are expected: the HAZOP owner
    re-stamps after the merge.
  - The rest are the 13 `instrument-no-interlock` trips that D-094 lists, template metadata,
    two title blocks, 6 line crossings and 3 energy balances. None is a `cheme.control-*`
    warning; the control findings are `control-incomplete`, `control-unresolved`,
    `control-logic-text` and the accepted `control-shared-element` (TICA-3124 / I-04), all info.
- `cheme diff 5918329 HEAD --list` (the commit before 33fcaaa), P-04 only:
  - Inst_PIC4101: 0 added, 4 removed, 9 modified;
  - Inst_PIC4102: 1 modified (the note);
  - Inst_PIC4150: 2 added, 9 modified;
  - GOX-4001: 1 added, 1 removed (the sense position moved with the swap);
  - PlantModel1: 1 modified.

  No other sheet changes, and the drawing counts are the same as at review 4.

**The swap works.** At HEAD:
- `cheme show PIC-4101`: PT4101 senses on GOX-4001 S1. Its measuring line starts at
  Inst_PIC4101_SensePosition (57, 45), upstream of XV-4117 (drawn at x 74 to 81) with no valve
  between. So PIC-4101 sees the column side when XV-4117 is shut, at start-up before S6 and
  after a trip. PV-4101B is on the vent tee Tee_GOX4001_V on the same side.
- `cheme show PIC-4150`: PT4150 senses on S3. Its measuring line is anchored on
  `Line_GOX4001_S3_P2_I1` (x 88), on the pipe from XV4117_N2 to K4101_N1, so it is on the machine
  side. Its dashed signal (Inst_PIC4150_Signal2) runs to the K-4101 guide vanes. No signal to
  PV-4101B is left on the sheet.
- The text at PIC-4102 reads "K-4101 IGV master (D-096); HH trips K-4101" (P-04.xml:38562).
  No "output A" text is left on any sheet.

Every reference to PIC-4101 and PIC-4150 in loops.yaml, sequences.yaml, philosophy.md,
narrative.md, the instrument list and D-096 matches the new roles and taps:
- PIC-4101 is the vent on the S1 tap;
- PIC-4150 is the low limit on the S3 tap, machine side.

Three places did not follow the swap or the new roles, all low:
- the electrical list still has PIC-4150 on JB-A3-2 and PIC-4101 on JB-A4-1 (#2);
- the drawn sense position of PIC-4101 lies on S2's drawn span (#3);
- PIC-3110's rationale still gives PIC-4101 the old role (#4).

Verdict:
- review 3 #6 and review 4 #1, #2, #4, #5, #6 and #7 are closed by 33fcaaa;
- review 4 #3 is accepted.

New findings: no critical, no high, 1 medium, 4 low.

**No critical or high finding is open in any of the five control reviews (review 1 to
review 5).** Every record still carries "PROPOSED ... not approved for implementation", and this
agent record approves none of them.

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-control-review3#6 | The machine stops leave the new loops in auto; texts keep PIC-4101's old role | low | closed 33fcaaa | (a) F-GOXC's loops are now `[PIC-4101, PIC-3110, PIC-4102, FIC-4148, PIC-4150, PIC-4111]`, and the response puts the guide-vane loops to tracking on the stop signal. This is marked "proposed", which is honest at basic engineering. (b) "Whether PV-3110A/B and PV-4101B together take the full GOX make" is in F-GOXC and D-096 Open. (c) F-GANC is new (loops PIC-4105, FIC-3107, PIC-4112; SEQ-BACKUP-GAN). It leaves the GAN path while K-4102 stands open, which is also in D-096 Open. One old-role text remains outside F-GOXC, in PIC-3110's rationale: new #4. |
| 2026-10-24-control-review4#1 | The GOX vent's transmitter is isolated in exactly the cases it vents for | high | closed 33fcaaa | The tags were swapped on P-04 (`cheme diff --list` above). PT4101 now senses on GOX-4001 S1, upstream of XV-4117 and on the same side as PV-4101B (`cheme show PIC-4101`, sense position at x 57; XV-4117 at x 74 to 81). PT4150 senses on S3_P2, between XV4117_N2 and K4101_N1 (`Inst_PIC4150_ML_LineShape` source `Line_GOX4001_S3_P2_I1`). PIC-4150's drawn signal goes to the guide vanes. SEQ-CB-START S1 (PIC-4101 auto with K-4101 stopped) and F-GOXC now work as written. D-096 (3), the instrument list and both loop rationales give the choice and the reason. The drawn tap position is a drawing detail: new #3. |
| 2026-10-24-control-review4#2 | Anti-windup and initialisation are no longer recorded | medium | closed 33fcaaa | Recorded as open again. PIC-4102 has "anti-windup of the three-way low select (external reset feedback, so the unselected loops track and act at once) and bumpless transfer to auto". PIC-4105 has "anti-windup when FIC-3107's set point is clamped ... and the initialisation of the cascade at start-up". D-096 Open has both. S7 now puts PIC-4105 in auto before FIC-3107 goes to cascade, with the comment "initialised to FIC-3107's set point (bumpless)". The framework-style `transitions:` entry on FIC-3107 was not added. That is acceptable while the cascade initialisation stays an open point. |
| 2026-10-24-control-review4#3 | The GAN cascade has no maximum draw | medium | accepted: the high clamp is in (FIC-3107 `kind: high` 12510 kg/h on S9, the design GAN draw, with the ratio to the air flow open in D-096). The low clamp falls to the K-4102 anti-surge (UIC-4131), and PIC-4106's role on the vanes stays the K-4102 vendor's open point, recorded on FIC-3107 and PIC-4106. | The GOX and GAN sides are now symmetric: each master is clamped at the design make. When the clamp holds, the GAN header falls to the backup, as on the GOX side. PIC-4106 is still "override or limit; vendor", and H04-A22 remains. |
| 2026-10-24-control-review4#4 | Where the GOX goes at a low off-take is not stated | low | closed 33fcaaa | The intent is now stated in PIC-4101's rationale and operator text and in D-096 (1): at a lower off-take the vanes close, the suction pressure rises, PIC-4101 vents the excess, and the operator turns FIC-1101 down. FIC-1101's open point no longer suggests a second loop on the header pressure ("whether it should follow PIC-4102's output or the FIC-4148 limit is for detail engineering"). Whether this intent can be realised with one PIC-4101 set point beside PIC-3110 is new #1. |
| 2026-10-24-control-review4#5 | The start abort stops the DCAC pumps while the MAC may still run | low | closed 33fcaaa | The abort condition is now `{tag: K-1101, state: tripped}` alone. The abort stops P-1101A/B and P-1102A/B, and the note says that I-03 does not stop the MAC. The note's "the start holds at S2" is not quite right for an I-03 trip after S2: new #4 (d). |
| 2026-10-24-control-review4#6 | P-04 and some texts still tell the old story | low | closed 33fcaaa | (a) The P-04 note at PIC-4102 is corrected. (b) The phantom "IGV (output A)" label reference is gone from the instrument list and D-096. (c) D-096 Open lists "drawing the low select, the cascade and PIC-4101's signal to PV-4101B". (d) D-019 carries "Revised by D-096". (e) D-096 (1) and the PIC-4102 rationale now say "a fixed limit at the design GOX make". FIC-4148's `purpose` still says "to what the column makes", a residual folded into new #4. |
| 2026-10-24-control-review4#7 | D-096 does not hand the H-04 owner what changed | low | closed 33fcaaa | D-096 has a "For the HAZOP owner (H-04)" list: H04-N1 / H04-S02 / H04-S75 causes, the H04-A23 wording, PIC-4150 in no node, the header-leak cause, and the renamed PV-4105 scenarios. It does not cover H04-S01 / H04-S03 and H04-SG06, and one cause is not precise for a low select: new #5. |

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-control-review5#1 | P-04 | PIC-4101 set point, PIC-3110, D-096 (1) / (3), VNT-4003 | **The turndown vent asks for a set-point window that the register does not state.** PIC-3110 holds the LP column top pressure. So the K-4101 suction pressure can only rise, as the vanes close, from about 1.15 bara at the design draw (S7) towards the LP column pressure less the static loss, at zero draw. The vent can act only if PIC-4101's set point lies inside that band, at turndown (D-096 (1), PIC-4101 rationale) and on a trip while PV-3110A/B still have capacity. PIC-4101's target only says "above the normal suction pressure of 1.15 bara, below the LP column relief case". A value in the upper part of that range never vents until PV-3110A/B saturate. D-096 (3) ("vents only when K-4101 does not take the GOX") and (1) ("vents the excess" at a low off-take) are two readings of the same set point. While PIC-4101 vents, it and PIC-3110 together set the GOX / waste split through a small pressure difference across E-3101. That is the D-094 conflict again, now at turndown only. Venting at turndown also makes VNT-4003 a normal-operation O2 release, not only a trip release, which the oxygen-enriched zone (D-031) may not assume. | medium | open | Give PIC-4101's target as the band "above the suction pressure at the design draw, below the suction pressure at zero draw with PIC-3110 at its set point" (unresolved, from the E-3101 / GOX-3001 pressure loss). Say which of D-096 (1) or (3) is meant. If turndown venting is meant, record that the split between GOX and waste N2 then follows the two set points. Say that the operator, or later a load controller, turns FIC-1101 down so the vent closes again. Tell the zones owner (skill `area-classification`) that VNT-4003 may release in normal operation. |
| 2026-10-24-control-review5#2 | - | electrical/electrical-list.yaml JB-A3-2 / JB-A4-1, cable schedule | **The junction boxes did not follow the swap.** JB-A3-2 ("product analysers and GOX flow east of the cold box") still lists PIC-4150, and JB-A4-1 ("GOX and GAN compressors") still lists PIC-4101. Their taps are now the other way round. PIC-4150's tap is on S3 at the K-4101 suction, and its cable grew from 15.7 m to 49.4 m (IC-PIC-4150). PIC-4101's tap is beside FIC-4148 on S1 (IC-PIC-4101, 34.9 m to 38.2 m). D-096 "Carried out" still says "PIC-4150 on JB-A3-2". This is outside the five control paths, but it follows from the swap. | low | open | Swap the two tags between JB-A3-2 and JB-A4-1 in the electrical list (or record why not), rebuild the cable schedule and the layout model, and correct the D-096 sentence. |
| 2026-10-24-control-review5#3 | P-04 | Inst_PIC4101_SensePosition, GOX-4001 S1 / S2 | **PIC-4101's tap is drawn on S2 but modelled on S1.** The PSGF senses on Line_GOX4001_S1 (`cheme show PIC-4101`). The sense position (57, 45) sits inside S1's drawing group, but at x 57. That is between the vent tee Tee_GOX4001_V (x 42, the end of S1) and the recycle tee Tee_GOX4001_R (x 65), on S2's drawn span. D-096, the instrument list and loops.yaml say S1. Hydraulically it makes no difference, because S1 and S2 are joined with no valve between, both upstream of XV-4117. But the drawing and the model disagree, and validate does not report it. | low | open | Move the sense position on S1, upstream of x 42 (`cheme move` or a hand edit of the node position, then `cheme fmt` and `cheme validate`). Or re-point the PSGF to S2 and write S2 in D-096, the instrument list and loops.yaml. |
| 2026-10-24-control-review5#4 | - | loops.yaml PIC-3110 / FIC-4148, D-094, SEQ-MAC-START abort note, narrative.md open points, PROGRESS.md | **Residual stale texts.** (a) PIC-3110's rationale (loops.yaml:321) still reads "the GOX draw is set by flow (FIC-4148), and PIC-4101 only limits the suction". Since D-096 the draw follows PIC-4102, FIC-4148 is the maximum, PIC-4150 is the low limit, and PIC-4101 vents. (b) FIC-4148's `purpose` reads "Limit the GOX draw to what the column makes". It is a fixed limit at the design make. (c) D-094 still names PIC-4101 as a split range (guide vanes first) and lists "what PIC-4102 ... act on" as open. Unlike D-019 and D-095, it has no "Revised by D-095 / D-096" pointer. (d) The SEQ-MAC-START abort note says that on an I-03 trip "the start holds at S2 until the seal is back". I-03 is checked only at S2 entry. A trip in S3 or after the end finds no step to hold in. The MAC simply stays on blow-off, which is the right outcome. (e) The narrative's open points do not list D-096's new open items: anti-windup and bumpless transfer, the GAN clamp as a ratio, the PV-3110A/B + PV-4101B capacity, and the GAN path while K-4102 stands. (f) The PROGRESS.md row of 33fcaaa names process/narrative.md, which the commit did not change. | low | open | (a) Rewrite PIC-3110's rationale to the D-096 roles. (b) Write "Limit the GOX draw to the design GOX make". (c) Add "Revised by D-095 and D-096" under D-094's heading. (d) Write "an I-03 trip keeps the MAC on blow-off; the start goes on only after I-03 is reset". (e) Add the four items to the narrative's open points, or point to D-096 Open. (f) Correct the PROGRESS row in the next commit. |
| 2026-10-24-control-review5#5 | - | D-096 "For the HAZOP owner (H-04)", H04-S01, H04-S03, H04-SG06, H04-N1 | **The H-04 hand-over is incomplete and imprecise in one point.** (a) It gives the new over-draw cause as "PIC-4102 or FIC-4148 failing high". In a low select, one loop failing high is masked by the others. The credible single causes are: FT-4148 reading low, or PT-4150 reading high, while PIC-4102 asks for more (header leak or customer over-draw); and the selector, the output stage or the vane positioner failing high. (b) It omits H04-S01 and H04-S03, whose causes still name "PIC-4101 output B". H04-S01 is now valid by design, because PT-4101 sees the column side after the swap. (c) It omits H04-SG06, which still credits FIC-4148 only as the anti-surge input. (d) It does not name the D-096 turndown vent (#1) as a new normal-operation cause of flow to VNT-4003 in H04-N1. (e) It does not say that PT-4150, now on the machine side, reads the blown-down casing after a trip. | low | open | Extend D-096's list: replace (a) with the low-select causes above; add H04-S01 / H04-S03 (output wording; S01 now realised by the S1 tap), H04-SG06 (FIC-4148 also the maximum draw), the turndown vent in H04-N1, and PT-4150's machine-side tap. The H-04 owner reassesses and re-stamps; this record changes nothing in H-04. |

## Drawing
P-04 changed only by the tag swap, the moved PIC-4101 bubble, its sense position and the
PIC-4102 note (see the diff above). The validate counts at 33fcaaa are the same as at review 4:
- P-01: 0 line-through-label, 2 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-02: 0 line-through-label, 0 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-03: 0 line-through-label, 3 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-04: 0 line-through-label, 1 line-crossing, 0 label-overlap, 0 label-far-from-owner

The crossings are outside the scope of this review. No tiles were rendered. Drawing points:
- the PIC-4101 sense position drawn on S2's span (#3);
- the low select, the cascade and PIC-4101's signal to PV-4101B are not drawn, which D-096
  Open declares.

## Checked and fine
- **Taps after the swap (P-04 XML):**
  - PT4101 is on the column side of XV-4117, PT4150 on the machine side;
  - PV-4101B is on the column side;
  - PIC-4150's drawn signal goes to the K-4101 guide vanes;
  - no PIC-4150 signal to PV-4101B remains.
- **Loop structure unchanged and consistent:**
  - PIC-4102 reverse, FIC-4148 reverse (`kind: high`), PIC-4150 direct (`kind: low`), in a low
    select linked from all sides;
  - PIC-4101 direct on PV-4101B alone;
  - PIC-4105 reverse cascade master; FIC-3107 reverse slave, `normal_mode: cascade`, now with
    a `kind: high` clamp on S9.
- **Sequences:**
  - SEQ-CB-START S1 puts PIC-4101 in auto with K-4101 stopped and XV-4117 shut. This now works,
    because PT-4101 sees the column.
  - S7 puts FIC-4148 / PIC-4150 in auto before PIC-4102, and PIC-4105 (initialised) before
    FIC-3107 goes to cascade.
  - SEQ-SHUTDOWN S2 puts the five product loops in manual and leaves PIC-4101 in auto to vent.
  - The MAC start abort runs on a K-1101 trip only and stops all four DCAC pumps.
- **Failures:**
  - F-GOXC and F-GANC name their loops, the backup sequence and their open points;
  - the "tracking" on the stop signal is marked proposed.
- **One story across the files** for the two tags: loops.yaml, sequences.yaml, philosophy.md,
  narrative.md, the instrument list and D-096 agree. The exceptions are #2 (electrical list),
  #3 (drawn position) and #4 (a), (b) and (c) (older texts).
- **Open points are honest:**
  - the vane, PV-4101B and PV-4105 fail positions;
  - the anti-surge flow of K-4101;
  - the ratios to the air flow;
  - anti-windup and bumpless transfer;
  - the vent and waste capacity on a trip;
  - the GAN path on a K-4102 trip;
  - H04-A22 and H04-A23.

  The limits are explicitly not credited as protection layers (D-093).

**Fit to merge at basic engineering.** The control records state a realisable regulatory
structure for every train. Measurement, action and final element agree with the P&IDs and the
lists, and what is not decided is marked `unresolved` or listed under D-096 Open, not invented.
No critical or high finding is open across reviews 1 to 5. The medium #1 and the lows can be
closed on the branch or carried into detail engineering. The merge decision and any sign-off
are a human's (AGENTS.md): this agent record has no `approved_by`.

## Not checked
- The K-4101 and K-4102 vendors' capacity control, anti-surge, and stop and trip sequences.
- The pressure losses of E-3101, GOX-3001 and GOX-4001 that set PIC-4101's window (#1), and the
  PV-3110A/B and PV-4101B capacities.
- Dynamics and tuning: no dynamic simulation exists.
- The HAZOP studies beyond the scenarios and actions named above. Their reassessment is the
  H-04 owner's (`hazop-input-changed`).
- The P&IDs beyond the `cheme show` reads and the XML anchors named above. No tiles were
  rendered.
- The oxygen-enriched zone of VNT-4003 (`layout/zones.yaml`).
- `cheme check` was not run.
