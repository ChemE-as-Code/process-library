---
topic: control
reviewed_commit: e6f59b82d912d0f6538829429b0206a3277f671e
scope: [control/loops.yaml, control/sequences.yaml, control/philosophy.md, process/narrative.md, DESIGN.md]
reviewer: Claude (independent control review agent; did not author e6f59b8, D-094, D-095 or D-096)
reviewer_kind: agent
branch: stage/basic-control
merge: pending
---
# Review: control intent of ASU-1, fourth review (confirming D-096)

This is an independent process-control review of branch `stage/basic-control` at e6f59b8
("D-096 products on pressure with flow as limit; PIC-4101 split, new suction low limit PIC-4150
on P-04"). It checks the findings that reviews/2026-10-24-control-review3.md left open: review 2
#8 and review 3 #1 to #8. It also judges, as a control engineer, the strategy that the project
owner decided in D-096 and how e6f59b8 builds it.

The changes were checked against:
- DESIGN.md D-013, D-019, D-024 and D-094 to D-096;
- the instrument list and the cause-and-effect list (I-03);
- P-04, read with `cheme show PIC-4150`, `GOX-4001`, `GOX-4002`, `XV-4117`, and the sensing
  locations and measuring-line anchors of PT-4101, PT-4102, PT-4105 and PT-4150 in the XML;
- the HAZOP study H-04 (H04-N1, H04-S01, H04-S02, H04-S75, H04-S20, H04-S27, H04-SG06,
  H04-A14, H04-A22 and H04-A23).

Checks run at e6f59b8:
- `cheme validate` (all rules, with generators): `112 file(s): 0 error(s), 45 warning(s)`.
  - 9 warnings are `hazop-input-changed` (H-01 .. H-04). They are expected: the HAZOP owner
    re-stamps after the merge.
  - The rest are the 13 `instrument-no-interlock` trips that D-094 lists, template metadata,
    two title blocks, 6 line crossings and 3 energy balances.
  - None is a `cheme.control-*` warning. PIC-4102, FIC-4148, PIC-4150, PIC-4101, FIC-3107 and
    PIC-4105 report only `control-incomplete` (fail positions) and `control-unresolved` infos.
    These match the open points the register declares.
- `cheme diff 04515c4 HEAD --list` (the commit before e6f59b8): on P-04, Inst_PIC4150 is added
  (21 objects) and GOX-4001 gets one addition (the PT-4150 tap). Nothing else changes on any
  sheet, which matches D-096's "drawing counts unchanged".

**On D-096.** The decision is sound and is the usual structure for a pipeline ASU:
- the product compressors hold the customers' pressures;
- the draw is clamped at what the column makes;
- the vent is a separate loop with its own set point.

Built as it is, the three-way low select is correct:
- **PIC-4102** (reverse): a rising header pressure lowers its output;
- **FIC-4148** (reverse): a flow above the limit lowers its output;
- **PIC-4150** (direct): a falling suction pressure lowers its output.

So whichever loop asks for the least vane opening wins. Each loop links the other two with
`override` / `select: low`, as docs/framework/control.md requires. The GAN cascade is declared
on the slave (`cascade` link on FIC-3107, normal mode `cascade`), and the master PIC-4105 has no
final element, which the convention allows. The sequence order is right:
- the machines run on recycle with manual vanes;
- the limits go to auto before the master;
- the loops go to manual before a planned stop.

Both review 3 highs are closed. The open items are named in D-096, the register, the narrative
and the philosophy.

One new high finding remains. It does not come from D-096 itself, but D-096 makes it decisive:
**PT-4101 senses behind the suction ESD XV-4117** (#1). PIC-4101 now has only one job, venting
the GOX when K-4101 does not take it. In both cases where it has to do that job, at start-up
before S6 and on a trip that closes XV-4117, its transmitter is isolated from the cold box. The
vent then never opens.

Verdict:
- review 3 #1, #2, #3, #5, #7 and #8 are closed by e6f59b8;
- review 3 #4 is accepted;
- review 3 #6 stays open (low, partly addressed);
- review 2 #8 is closed by e6f59b8, with a residual (new #5).

New findings: 1 high, 2 medium, 4 low. Every record still carries "PROPOSED ... not approved for
implementation", and this agent record approves none of them. The branch cannot be signed off
while #1 is open.

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-control-review2#8 | SEQ-MAC-START aborts on a control deviation | low | closed e6f59b8 | The abort runs no shutdown sequence any more. It puts FIC-1101 in manual and stops P-1101A and P-1102A, with the note "the DCAC pumps stop after the MAC (H01-A4). Nothing downstream runs yet". The SEQ-SHUTDOWN S1 wait for the customers no longer applies at an aborted start. Residual: the abort also runs on I-03 tripped, and I-03 only closes XV-1115. The MAC is then not stopped, and the pumps stop while it runs: new #5. |
| 2026-10-24-control-review3#1 | PIC-4101 cannot be a low limit and a high vent with one set point | high | closed e6f59b8 | D-096 (3): PIC-4101 acts on PV-4101B alone, and its set point is above the normal suction pressure. The new PIC-4150, on its own transmitter PT-4150 (P-04, GOX-4001 S1, `cheme show PIC-4150`), is the low limit (`kind: low`) in the guide-vane select. The split range is gone from loops.yaml, the instrument list, the narrative and the philosophy. The structure is now realisable. Where PIC-4101 measures is a separate defect: new #1. |
| 2026-10-24-control-review3#2 | The export pressures have no mass-balance handle left | high | closed e6f59b8 | D-096 (1), (2). GOX: PIC-4102 holds the header on the K-4101 vanes through the low select. PT-4102 is on GOX-4002 S7_P2, downstream of the check valve and upstream of the backup tee (XML measuring-line anchor), so it sees the header that the backup also feeds. GAN: PIC-4105 sets FIC-3107's set point in cascade, and PV-4105 is normally fully open. "IGV or recycle" is gone from PIC-4102. The narrative, the philosophy, the instrument list and SEQ-CB-START S7 tell the same story. Missing clamps and anti-windup: new #2 and #3. |
| 2026-10-24-control-review3#3 | The suction low limit acts late on a GOX over-draw | medium | closed e6f59b8 | PIC-4150's operator text says that it acts late and that the over-draw shows first in LICA-3102 and AI-3104. D-096 ("Not credited") and the philosophy ("The limits are not protection layers") say it is not a protection layer, and H04-A23 remains. FIC-4148 keeps the H04-A23 / H03-A4 open point. Two sentences still overstate the protection ("so the plant never draws more GOX than the column makes"): new #6. |
| 2026-10-24-control-review3#4 | The anti-surge flow input misses the recycle | medium | accepted: recorded as an open point for the K-4101 vendor's anti-surge package (detail engineering) | Recorded as an open point: UIC-4103 `unresolved`, D-096 "Open", the philosophy and the narrative. The answer is the K-4101 vendor's anti-surge package, so it belongs to detail engineering. Accepted on the condition that it stays open there. The instrument-list note of UIC-4103 still names FT-4148 as the input without the caveat, and H04-SG06 still credits UIC-4103 on FIC-4148; both are for the H-04 owner (#7). |
| 2026-10-24-control-review3#5 | The GAN train has no outlet between S5 and S7 | medium | closed e6f59b8 | The S5 completion now reads "it is still diverted through XV-3105 to VNT-4004". The S6 `FIC-3107 auto` is removed, and S6 states "guide vanes in manual" on recycle. S7 opens XV-4120 / XV-4134, then closes XV-3105, then puts the limits, the master and the cascade in auto. The bumpless start (initialisation) is not stated: part of new #2. |
| 2026-10-24-control-review3#6 | The machine stops leave the new loops in auto; texts keep PIC-4101's old role | low | open | Done: SEQ-SHUTDOWN S2 puts PIC-4102, FIC-4148, PIC-4150, PIC-4105 and FIC-3107 in manual before the stops, and F-GOXC and the S2 texts give the LP column pressure to PIC-3110. Not done: (a) F-GOXC's loops are still `[PIC-4101, PIC-4111]`, without PIC-3110 or the loops it says "go to manual". On a trip nothing (no sequence, no C&E effect) does that switch. (b) The PV-3110A/B capacity for the full GOX make is neither stated nor recorded as open; #1 makes it the only path. (c) There is still no failure mode for a K-4102 trip (FIC-3107 in cascade on a stopped machine, the GAN with no outlet while XV-3105 is closed). |
| 2026-10-24-control-review3#7 | PIC-4105's action is stated while its tap side is open | low | closed e6f59b8 | As cascade master, PIC-4105 is reverse (a rising pressure lowers the GAN flow set point) whichever side of a fully open PV-4105 it taps. The rationale says so. If PV-4105 later becomes a back-pressure valve, the tap and the action have to be revisited. That is recorded under PV-4105's role (open). |
| 2026-10-24-control-review3#8 | Citations and open-point lists after D-095 | low | closed e6f59b8 | H04-A14 is now cited only for PV-4101B, which it lists. The K-4101 / K-4102 guide vanes and PV-4105 read "no HAZOP action lists it yet". The narrative and the philosophy list D-096's open items (PV-4105, the K-4101 anti-surge flow, the ratio of the maximum draw to the air flow). The H-04 wording itself (H04-A22, the FIC-4148 role) was not changed, which is correct, because H-04 is outside this commit. What the H-04 owner now has to reassess is listed in new #7. |

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-control-review4#1 | P-04 | PIC-4101 / PT-4101, XV-4117, SEQ-CB-START S1, F-GOXC, SEQ-SHUTDOWN S2 | **The GOX vent's transmitter is isolated in exactly the cases it vents for.** PT-4101 senses on GOX-4001 S3, and its measuring line is anchored on S3_P2, between the suction ESD XV-4117 and K-4101 N1 (`cheme show GOX-4001`, `Inst_PIC4101_ML_LineShape` source `Line_GOX4001_S3_P2_I1`). The vent PV-4101B is on the tee upstream of XV-4117, on S1. (a) **Start-up:** SEQ-CB-START puts PIC-4101 in auto in S1, "with K-4101 stopped", and opens XV-4117 only in S6. Through the whole cool-down, PIC-4101 measures the isolated machine casing, not the GOX the column makes. (b) **Trip:** XV-4117 is the emergency isolation that closes on a K-4101 trip (D-013; TSHH-4104 "closes ESD valves, depressurizes to vent"). PT-4101 then reads the blown-down casing, and a direct-acting PIC-4101 drives PV-4101B shut. In both cases the GOX from the LP column is blocked in. Only PIC-3110 and the waste path remain, and their capacity for the full GOX make is not stated (review3#6). H04-S01 analyses PV-4101B failing to open, but not PIC-4101 being blind by design. Since D-096, PIC-4101 has no other job, so its one stated function is not realised. The arrangement is inverted: the low limit PIC-4150, which protects the machine suction, taps S1 (cold-box side), and the vent taps the machine side. | high | open | Move PIC-4101's sensing point upstream of XV-4117, on GOX-4001 S1 or S2, where PV-4101B also sits (`cheme copy --sense-at` or a re-pointed SensingLocation and measuring line on P-04). Then decide where PIC-4150 should tap. Upstream of XV-4117 it reads the cold-box outlet, the better over-draw signal. Between XV-4117 and K-4101 it reads the true machine suction, the better guard against a sub-atmospheric suction. Record the choice in D-096, the instrument list and loops.yaml. Hand H04-N1 and H04-S01 to the H-04 owner. |
| 2026-10-24-control-review4#2 | P-04 | PIC-4102 / FIC-4148 / PIC-4150 select, PIC-4105 / FIC-3107 cascade | **Anti-windup and initialisation are no longer recorded.** In normal operation FIC-4148 and PIC-4150 are not selected. Their errors stay one-sided (flow below the limit, pressure above the low limit), so their integral winds to 100 %. When an over-draw starts, each must unwind from 100 % to the actual vane position before it can take over. The limit then acts only after a delay set by its integral time, which is when it is needed. The same happens to PIC-4102 whenever a limit holds the vanes (the header pressure is below set point, and the master winds up), and to PIC-4105 if FIC-3107 is ever limited (PIC-4106, H04-A22). D-095 recorded the external reset feedback as open. D-096 dropped the point along with the split range, although the three-way select needs it more. S7 also switches FIC-3107 to `cascade` while PIC-4105 is still in manual. Unless PIC-4105's output tracks FIC-3107's set point, this bumps the guide vanes. Review3#5 asked for the ramp, and it is not stated. | medium | open | Add to PIC-4102, FIC-4148 and PIC-4150: "external reset feedback from the selected output (or an equivalent anti-windup) so that the unselected loops track the vane position". Add the same for PIC-4105 from FIC-3107's set point. Add to FIC-3107 the transition `{from: auto, to: cascade, condition: {loop: PIC-4105, state: "in auto, output initialised to FIC-3107's set point"}}`, as in the framework example. Say in S7 that each loop starts bumpless from the current flow or position. |
| 2026-10-24-control-review4#3 | P-04 | FIC-3107 / PIC-4105, PIC-4106, H04-S20, H04-S27 | **The GAN cascade has no maximum draw.** On the GOX side, D-096 puts the master under a maximum-draw limit (FIC-4148) "so the plant never draws more GOX than the column makes". On the GAN side, PIC-4105 sets FIC-3107's set point with no clamp at all. When the customer takes more than the HP column makes, or the GAN header leaks, PIC-4105 raises the set point without bound. K-4102 then draws the HP column down (less LN reflux, falling purity), until AIA-3105 opens XV-3105, closes XV-4120 and the customer loses the GAN. This is the consequence of H04-S20 ("PIC-4106 or FIC-3107 fails high") and H04-S27, here reached by normal control, not by a fault. It is the GAN counterpart of review3#3 / H04-S75. PIC-4106, the suction low limit, is still undecided ("override or limit; vendor"). | medium | open | Give FIC-3107 set-point limits in the cascade: a high clamp at the design GAN make (12510 kg/h at the design air flow, later a ratio to FIC-1101, as for FIC-4148) and a low clamp at the K-4102 minimum. Then the GAN header falls to the backup (SEQ-BACKUP-GAN) as on the GOX side. Record PIC-4106 as the intended low-select partner on the vanes, with the vendor confirming it, and keep H04-A22 for the independent limit. Write the asymmetry or its removal into D-096. |
| 2026-10-24-control-review4#4 | - | PIC-3110 / PIC-4101 set points, FIC-1101 open point | **Where the GOX goes at a low off-take is not stated.** With the pressure as master, a lower customer draw closes the K-4101 vanes. The GOX the column still makes then either leaves with the waste N2 (PIC-3110 opens PV-3110A/B) or is vented (PIC-4101 opens PV-4101B). Which of the two happens depends on how the PIC-3110 and PIC-4101 set points relate, and on the suction rise when the vanes close. The register only says "above the normal suction pressure". If the margin is too small, PV-4101B becomes the turndown path in normal operation. Nothing brings the air flow down with the demand either. FIC-1101 still carries "whether the set point comes from the GOX header pressure in cascade". Since D-096 that would be a second loop on the header pressure, beside PIC-4102. | low | open | State the intent: at a low off-take the column rejects the surplus O2 to the waste N2 under PIC-3110, and the operator, or later a load controller, turns down FIC-1101. Give PIC-4101's set point as "above the highest suction pressure that PIC-3110 allows at the minimum GOX draw" (unresolved). Reword FIC-1101's open point to "the air flow following the GOX demand (FIC-4148 flow or vane position), not the header pressure, which is PIC-4102's". |
| 2026-10-24-control-review4#5 | P-01 | SEQ-MAC-START abort, I-03, P-1101A/B, P-1102A/B | **The start abort stops the DCAC pumps while the MAC may still run.** The abort condition includes I-03 tripped. I-03 only closes XV-1115 (cause-effect.yaml) and does not stop K-1101. The abort then stops P-1101A and P-1102A, while its own note says the pumps stop after the MAC (H01-A4). On blow-off little air reaches C-1101, but nothing in the record says so or waits for the MAC. The abort also stops only the A pumps; the B pumps, if they run as duty, keep running. | low | open | Either stop K-1101 in the abort first, with `complete: K-1101 stopped` before the pump stops, or split the abort: on K-1101 tripped stop the pumps after the MAC; on I-03 tripped hold on blow-off with the pumps running. Name the pumps as "the running DCAC pumps (P-1101A/B, P-1102A/B)". |
| 2026-10-24-control-review4#6 | P-04 | Inst_PIC4102 label, instrument list (PIC-4101), D-019, D-096 / PIC-4102 rationale | **P-04 and some texts still tell the old story.** (a) The P-04 text at Inst_PIC4102 (pid/P-04.xml:38625) reads "K-4101 load (with PIC-4101); HH trips K-4101". Since D-096 the vanes are limited by FIC-4148 and PIC-4150, not by PIC-4101. (b) The instrument-list note of PIC-4101 and D-096 refer to "the 'IGV (output A)' label of D-019" as now standing for PIC-4150. No such text exists on any sheet (grep on pid/). (c) Neither the low select nor the cascade is drawn on P-04. D-096 lists only PV-4105's signal as open, not the select and FIC-4148 / PIC-4150 / PIC-4102 to the vanes. (d) D-019 still describes the split range, with no pointer to D-096. (e) D-096 (1) and the PIC-4102 rationale say "never exceeds / never draws more GOX than the column makes". The limit is fixed at the design make, so it is above the make at turndown (its own open point), and PIC-4150 acts late (#3 of review 3). | low | open | Correct the PIC-4102 label on P-04 (`cheme set` or edit the text, then `cheme fmt`), and drop the phantom label reference from the instrument list and D-096. Add "the low select and the PIC-4102 / FIC-4148 / PIC-4150 signals to the K-4101 vanes, and the PIC-4105 to FIC-3107 cascade, are not drawn" to D-096 Open. Add "Revised by D-096" under D-019. Write "limits the draw to the design make" instead of "never more than the column makes". |
| 2026-10-24-control-review4#7 | - | H-04 (H04-N1, H04-S02, H04-S75, H04-A23, H04-SG06), D-096 | **D-096 does not hand the H-04 owner what changed.** In e6f59b8, H-04 still: (a) gives PIC-4101 output A on the guide vanes (H04-N1 design intent); (b) gives the over-draw causes of H04-S02 and H04-S75 as "PIC-4101 fails high on its output A"; (c) asks in H04-A23 for a limit "independently of PIC-4101"; (d) lists FIC-4148 as the "anti-surge flow input" only; (e) has PIC-4150 in no node. The new structure also brings a new cause to reassess: a GOX header leak or a customer over-draw now opens the vanes by design, up to the FIC-4148 limit. D-095 named its H-04 hand-over. D-096 names none, and `hazop-input-changed` says only that something changed. | low | open | Add to D-096 a short "HAZOP H-04 to reassess" list: H04-N1 intent and members (PIC-4150, PIC-4102 on the vanes), the causes of H04-S02 and H04-S75 (now PIC-4102, FIC-4148 or PIC-4150 failing high), the wording of H04-A23 (independent of the guide-vane select), the FIC-4148 role in H04-SG06, the new cause above, and #1 for H04-S01. |

## Drawing
P-04 changed only by the PIC-4150 bubble and its tap on GOX-4001 S1 (see the diff above). The
validate counts at e6f59b8 are the same as at review 3:
- P-01: 0 line-through-label, 2 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-02: 0 line-through-label, 0 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-03: 0 line-through-label, 3 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-04: 0 line-through-label, 1 line-crossing, 0 label-overlap, 0 label-far-from-owner

The crossings are outside the scope of this review. No tiles were read. Two drawing points
were noted:
- the stale PIC-4102 text and the undrawn select and cascade signals (#6);
- the PT-4101 tap behind XV-4117 (#1).

## Checked and fine
- **Actions and selector direction:**
  - PIC-4102 is reverse, FIC-4148 is reverse with `kind: high`, and PIC-4150 is direct with
    `kind: low`. All three are in a low select on K-4101, linked from all sides;
  - PIC-4101 is direct on PV-4101B alone;
  - PIC-4105 is a reverse cascade master, and FIC-3107 is a reverse slave with
    `normal_mode: cascade`;
  - validate reports no `control-conflict` (one element, three loops, overrides declared).
- **Stream links:**
  - PIC-4102 takes S8 pressure (31 bara);
  - FIC-4148 takes S7 flow (20860 kg/h) as its limit;
  - PIC-4105 takes S9B pressure (9 bara);
  - FIC-3107 takes S9 flow (12510 kg/h);
  - PIC-4150 and PIC-4101 carry no design value. Their set points are unresolved, with the
    margins named.
- **Measurement points (P-04 XML):**
  - PT-4102 is downstream of the GOX check valve and upstream of the backup tee, so PIC-4102
    and PIC-4111 see the same header. The hand-back of SEQ-BACKUP-GOX S2 / S3 is physically
    right;
  - PT-4150 is a separate tap from PT-4101.
- **Sequence order:**
  - SEQ-CB-START S6 runs both machines on recycle with the vanes in manual;
  - S7 opens the battery limits, closes XV-3105 after XV-4120 / XV-4134 are open, puts FIC-4148
    and PIC-4150 in auto before PIC-4102, and puts FIC-3107 in cascade before PIC-4105 goes to
    auto;
  - S7 completes on PV-4101B shut and both export pressures held;
  - SEQ-SHUTDOWN S2 puts all five product loops in manual before K-4101 / K-4102 stop.
- **Backup set points:** PIC-4111 and PIC-4112 stay "below the export pressure" (unresolved).
  When a limit holds the vanes, the backup therefore tops up the header instead of fighting
  PIC-4102, as PIC-4102's operator text says.
- **One story across the files:** loops.yaml, the instrument list, philosophy.md ("What sets
  what", the open points), narrative.md (PRD normal operation, open points) and D-096 agree on
  the master, the limits, the vent and the cascade. grep finds no "split range" left on
  PIC-4101 outside D-019 / D-024 / D-095 (history) and H-04 (#7).
- **The open points are honest:** the fail positions (the vanes and PV-4105 "no HAZOP action
  lists it yet"), the anti-surge flow, the ratio to the air flow, the role of PV-4105,
  H04-A22 and H04-A23. The limits are explicitly not credited as protection layers (D-093).
- D-095 carries "Revised by D-096", and D-094's trip list is unchanged.

## Not checked
- The K-4101 and K-4102 vendors' capacity control, anti-surge, and stop and trip sequences
  (whether every K-4101 stop closes XV-4117; #1 holds for any trip that does).
- The PV-3110A/B capacity for the full GOX make.
- Dynamics and tuning: no dynamic simulation exists.
- The HAZOP studies beyond the scenarios and actions named above. Their reassessment is the
  H-04 owner's (`hazop-input-changed`).
- The P&IDs beyond the `cheme show` reads and the XML anchors named above. No tiles were read.
- `cheme check` was not run.
