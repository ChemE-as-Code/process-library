---
topic: control
reviewed_commit: 3346c49c816042354a736742f70d2aa3dec19d0b
scope: [control/loops.yaml, control/sequences.yaml, control/philosophy.md, process/narrative.md, DESIGN.md]
reviewer: Claude (independent control review agent; did not author 8bb1311, ef612f6, 3346c49 or D-094)
reviewer_kind: agent
branch: stage/basic-control
merge: pending
---
# Review: control intent of ASU-1, second review (confirming the review 1 fixes)

This is an independent process-control review of branch `stage/basic-control` at 3346c49
("control review 1 fixes"). It checks the 22 findings of reviews/2026-10-24-control-review1.md
(reviewed commit ef612f6) against `git diff ef612f6 HEAD -- processes/asu-1`. That diff changes
control/loops.yaml, control/sequences.yaml, control/philosophy.md, process/narrative.md,
DESIGN.md D-094 and PROGRESS.md. The review also looks for new problems that the fixes
introduced. The changes are judged against DESIGN.md (D-006, D-010, D-013, D-014, D-019, D-024,
D-067, D-077, D-094), the line and instrument lists, the C&E, the P&IDs (`cheme show UV-1102`,
`AIR-2002`, `GOX-4001`, `XV-4117`) and the actions of the HAZOP drafts H-01 .. H-04.

Checks run at 3346c49:
- `cheme validate` (all rules, with generators): `109 file(s): 0 error(s), 39 warning(s)`.
  None of the warnings is a `cheme.control-*` rule. The warnings were already there before this
  branch: 13 `instrument-no-interlock` (the trips D-094 lists), the template metadata, the title
  blocks, 6 line crossings, the generated-version and layout-model-version warnings, and three
  energy balances. The control infos are `control-incomplete`, `control-unresolved`,
  `control-logic-text`, and one `control-shared-element` (TICA-3124 / I-04 / TV-3124, which is
  meant). The stream-linked set points are now 12 (PIC-1103, TIC-3109 and PIC-4106 no longer
  carry a design-case value), as D-094 says.
- `cheme diff main --list`: `process/BFD.xml:` and `process/PFD.xml:` with no changed plant
  item. No P&ID changed on this branch.

**On the open conflicts.** The author did not invent the GOX / waste N2 split or the GAN flow
pairing. These are recorded as unresolved in loops.yaml (PIC-3110, PIC-4101, FIC-3107,
FIC-4105, PIC-4106), the philosophy, the narrative and D-094. As an interim record that is
honest, and it is better than a made-up scheme. But it does not close #1 or #2, for three
reasons:
1. The HAZOP actions the records name do not decide the pairing. H04-A23 asks for a limit on
   the GOX draw independent of PIC-4101, and H03-A4 for the LICA-3102 alarms. H04-A22 asks for a
   guide-vane limit independent of FIC-3107 / FIC-4105. These are protection layers around the
   loops. Which loop holds the LP column pressure, and what sets the GOX draw and the GAN flow,
   is a control-structure decision that no action and no owner is assigned to.
2. The records still operate the conflicting loops together. SEQ-CB-START S1 puts PIC-3110 and
   PIC-4101 in auto, and FIC-4105 keeps `normal_mode: auto`.
3. The records disagree among themselves about who holds the LP column (see #1 below).

At basic engineering it is acceptable to leave the choice open. The acceptable form is a named
decision with an owner, or an explicit human acceptance of the deferral. An agent cannot give
the second, so both findings stay open.

Verdict: 19 of the 22 findings are closed by 3346c49, and #5 is superseded. #1 and #2 (high)
stay open. The fixes introduce two new high findings. One is the start-up air path into the cold
box before the TSA and cold-box permissives (it replaces #5). The other is K-4101 being started
with its suction ESD valve still closed. There are also four new medium and four new low
findings. All records stay PROPOSED. This agent record approves none of them, and the branch
cannot be signed off while the four high findings are open.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-control-review2#1 | P-01 / P-02 / P-03 | SEQ-MAC-START S3, SEQ-TSA permissives, SEQ-CB-START | **Air reaches the cold box before the TSA and cold-box permissives.** SEQ-MAC-START S3 now loads the MAC to "the start-up flow the TSA and the cold box vent can take". But AIR-1004 -> AIR-2001 -> AIR-2002 have no isolation or air vent between C-1101 and E-3101 (`cheme show AIR-2002`: no valve; the line list has no air vent on P-02). "The cold box vent" names no item. Any air that is not blown off through UV-1102 therefore flows through the TSA into the cold box during SEQ-MAC-START. That happens before the permissives of SEQ-CB-START hold (SEQ-TSA running, AIA-2102 CO2 below 1 ppm, seal gas PDSLL-3115, casing purge PIC-3113), and SEQ-MAC-START has no TSA permissive. The circle of review1#5 also remains in form: the only permissive of SEQ-TSA is "regeneration gas available". That blocks even its adsorption step S1, which needs no regeneration gas, and SEQ-CB-START needs SEQ-TSA running. The H02-A10 citation for the regeneration source is right. The order is still undefined. D-006 / D-010: no CO2 or water into the cold box. | high | open | Make a regenerated bed on line (KS-2101 adsorbing; the initial bed state, H02-A7 / H02-A10) a permissive of SEQ-MAC-START S3, or of any air past UV-1102. Move "regeneration gas available" to SEQ-TSA S2 (heat). Say that the start-up air goes through the cold box to PV-3110B. Either the seal gas and casing purge permissives of SEQ-CB-START hold before S3 of SEQ-MAC-START, or the order is marked unresolved with the supplier. |
| 2026-10-24-control-review2#2 | P-04 | SEQ-CB-START S6 / S7, XV-4117, XV-4116 | **K-4101 is started with its suction ESD closed.** S6 starts K-4101 (complete "at speed"). XV-4117, the suction ESD (D-024), opens only in S7. `cheme show GOX-4001` puts XV-4117 between the recycle tee (Tee_GOX4001_R, GOX-4003) and K-4101 N1, so the anti-surge recycle returns upstream of the closed valve and cannot feed the machine. The started compressor pulls its suction down against XV-4117: surge, and a sub-atmospheric GOX casing. The blowdown XV-4116 (opened by the K-4101 trip, H04-A01) is not closed before the start. The GAN battery-limit valves XV-4120 / XV-4134 (bleed XV-4135, D-013) have no opening step. | high | open | Open XV-4117 and close XV-4116 before K-4101 starts, with the machine on recycle (UIC-4103, UV-4103 open). Keep XV-4118 / XV-4119 for S7 behind the dP permissive. Add the GAN BL opening (XV-4135 closed, XV-4120 / XV-4134 open) once AIA-3105 is in specification. |
| 2026-10-24-control-review2#3 | P-01 | SEQ-MAC-START permissives, I-03 | **The I-03 permissive comes before the step that can meet it.** The sequence permissive requires I-03 reset with the chimney-tray level above its trip level before S1. But the tray fills only when P-1102A runs in S1, and I-03 holds XV-1115 closed until LSLL-1115 clears. So on a first or drained start the sequence can never begin. H01-A10 wants the seal established and I-03 reset before the MAC loads C-1101, which is S2, not S1. | medium | open | Move the I-03 reset (tray above trip level) to the entry of S2. S1 fills the tray with XV-1115 closed, and I-03 is reset in S1 once LSLL-1115 clears. |
| 2026-10-24-control-review2#4 | P-03 | SEQ-CB-START S3, FIC-3111 | **The purge from the first liquid runs at the design set point.** S3 puts FIC-3111 in auto, and its set point is 470 kg/h (S10, design). During cool-down the LP sump collects much less, so the loop draws the sump empty and S4 (LICA-3102 above LAL) cannot be reached. The register's own FV-3111 note says that drawing more than the column makes uncovers E-3103 (H03-S33). The cool-down purge rate is not stated, and neither is where the purge goes while T-4101 cannot take off-spec LOX (V-3101, H03-A5). | medium | open | In S3, give the purge rate during cool-down (the 43 kg/h minimum, or the supplier's value) and its route (V-3101 or T-4101, H03-A5). Raise it to the design set point in S4 / S5. |
| 2026-10-24-control-review2#5 | P-04 | SEQ-BACKUP-GOX S2, SEQ-BACKUP-GAN S2 | **The hand-back starts before the ASU delivers.** S2 completes on "K-4101 running and XV-4119 open" (GAN: "K-4102 running and XV-4120 open"). The backup risers GOX-4004 and GAN-4003 join their export headers upstream of XV-4119 / XV-4120 (D-024), so these valves are already open during the backup. K-4101 is "at speed" at SEQ-CB-START S6, before XV-4117 / XV-4118 open in S7. S3 then closes PV-4111 and stops the pump while K-4101 does not yet deliver. The header dips, and the backup restarts on low pressure. | medium | open | Complete S2 on the ASU product delivering at the header: SEQ-CB-START S7 complete (XV-4118 open, PIC-4102 holding). For GAN: K-4102 delivering in specification (AIA-3105 below 10 ppm) at the export pressure. |
| 2026-10-24-control-review2#6 | - | process/narrative.md (PUR, CB) | **The narrative keeps two statements that review1 #12 and #14 removed elsewhere.** PUR normal operation: "A bed goes back on line only with CO2 and the dew point below their limits (AIA-2102, AIA-2103)". That contradicts SEQ-TSA S5 and the analysers' location on the bed on line (AIR-2001). PUR modes: "On a CO2 high-high the beds are switched early, or the MAC trips (D-010)". That states as designed a trip that is not in the C&E (H02-A1), against F-TSA. CB modes leave out the E-3104 check before a restart (H03-A11), which F-COMPANDER and SEQ-COMPANDER-TRIP now include. | medium | open | Align the narrative with SEQ-TSA S5 (the supplier's regeneration-complete criteria, H02-A4 / H02-A7), with F-TSA (alarm and operator action pending H02-A1), and with the E-3104 check. |
| 2026-10-24-control-review2#7 | P-03 | SEQ-COMPANDER-TRIP S3, TIC-3109 | **A loop without a final element is put in auto.** After the review1 #9 fix, TIC-3109 has no final element and no action (validate `control-incomplete`). The S3 restart still puts it in auto. | low | open | Drop the action, or make it conditional on H03-A18 deciding what TIC-3109 acts on. |
| 2026-10-24-control-review2#8 | P-01 | SEQ-MAC-START abort | **The abort is on a control deviation.** The abort fires on "LIC-1114 level falling below its set point". Normal control noise around the set point then aborts the start and runs SEQ-SHUTDOWN. SEQ-SHUTDOWN's S1 waits for the customers, which means nothing while the MAC is still being started. | low | open | Abort on the LIC-1114 low alarm or on I-03 tripped. On a start-up abort, go to a MAC stop (unload to blow-off, stop, then the DCAC pumps, H01-A4) rather than the full normal shutdown. |
| 2026-10-24-control-review2#9 | P-01 / P-02 | SEQ-SHUTDOWN S4 / S5 | **The TSA is held before the MAC is unloaded.** S4 isolates the bed on line while K-1101 still runs. The MAC then runs blocked in against C-1101 until S5, and only the anti-surge saves it. | low | open | Unload the MAC to blow-off first (FIC-1101 to manual / minimum, UV-1102 open), then hold the TSA, then stop the MAC and the pumps. |
| 2026-10-24-control-review2#10 | P-03 / P-04 | SEQ-CB-START permissive PIC-3113 | **The casing purge needs N2 that the start-up has not made yet.** UN-3001 takes the casing purge N2 from the GAN export / backup header (line list), and K-4102 starts only in S6. On a first start the purge relies on the LIN backup (T-4102, SEQ-BACKUP-GAN) or on delivered LIN, and no record says so. | low | open | State the casing purge source at first start (backup header from T-4102, filled with delivered LIN) as a permissive or an unresolved point. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-control-review1#1 | Two pressure controllers on the LP column pressure (PIC-3110, PIC-4101) | high | open | Recorded as unresolved on PIC-3110 / PIC-4101, in the philosophy, the narrative and D-094. That is honest, but the cited H04-A23 / H03-A4 ask for an independent GOX draw limit and the LICA-3102 alarms, not for the pairing, so no owner decides it. SEQ-CB-START S1 still puts both in auto, and its operator note says "PIC-3110 holds the LP column". D-019, the narrative PRD section ("With K-4101 stopped it holds the LP column by the vent") and SEQ-SHUTDOWN S2 ("LP column pressure held" by PV-4101B) give that role to PIC-4101. Close with a decision (DESIGN.md, with owner), or a human accepts the deferral. |
| 2026-10-24-control-review1#2 | Two flow controllers in series on the GAN flow (FIC-3107, FIC-4105) | high | open | Recorded as unresolved on FIC-3107 / FIC-4105 / PIC-4106. S6 no longer puts FIC-4105 in auto, but `normal_mode: auto` remains. No loop holds the GAN export pressure. H04-A22 asks for an independent guide-vane limit, not for the pairing. Same route as #1. |
| 2026-10-24-control-review1#3 | PICA-4109 set point at the tank design pressure | high | closed 3346c49 | loops.yaml PICA-4109: set point unresolved, below the design pressure and the PSV-4123 set by the supplier's margin; the D-019 source corrected. |
| 2026-10-24-control-review1#4 | MAC started before the tray seal; pumps never started | high | closed 3346c49 | SEQ-MAC-START S1 starts P-1101A / P-1102A and establishes LIC-1114 before S2 starts K-1101. The I-03 reset and H01-A10 are in the permissives, and the LIC-1106 / LIC-1114 restart permissive (H01-A4) is in the reset. The I-03 permissive is in the wrong place: new finding review2#3. |
| 2026-10-24-control-review1#5 | Circular start-up; MAC loaded before the downstream accepts the air | high | superseded by 2026-10-24-control-review2#1 | The MAC now ends at a start-up flow, and the regeneration source is unresolved with H02-A10 (adequate). The air path into the cold box before the TSA and cold-box permissives, and the formal circle in the SEQ-TSA permissive, remain: review2#1. |
| 2026-10-24-control-review1#6 | LOX purge started only after the sump had filled | high | closed 3346c49 | FIC-3111 goes to auto in SEQ-CB-START S3, and S3 completes on the purge flowing. The rate during cool-down is a new finding: review2#4. |
| 2026-10-24-control-review1#7 | "Turn the liquid production down" has no handle; the LOX is the purge | high | closed 3346c49 | OBJ-4, F-CHW, the TICA-3124 TAH response and SEQ-COMPANDER-TRIP S1 now say there is no loop yet (H03-A7, a P&ID action) and that the purge must not be cut. The impossible instruction is removed. |
| 2026-10-24-control-review1#8 | PIC-1103 / PIC-4106 limits at the normal value | medium | closed 3346c49 | Both limits unresolved (vendor margin), with the normal value named as the reference. |
| 2026-10-24-control-review1#9 | TIC-3109 final element and override scheme invented | medium | closed 3346c49 | TIC-3109 has no final element or select, H03-A18 is cited, and SIC-3108's link is removed. The left-over auto action: review2#7. |
| 2026-10-24-control-review1#10 | TV-3124 cited as the fail-safe example | medium | closed 3346c49 | F-AIR and the fail-position rule now say that TV-3124 open defeats I-04 on air loss (H03-A12). I-04 added to F-AIR. |
| 2026-10-24-control-review1#11 | "A loop is never a safeguard" against D-093 | medium | closed 3346c49 | The philosophy's "Loops and safeguards" states the D-093 credit convention. |
| 2026-10-24-control-review1#12 | F-TSA, F-POWER, F-CW claim protection the design lacks | medium | closed 3346c49 | F-TSA is an alarm and operator action pending H02-A1. F-POWER no longer runs SEQ-SHUTDOWN. F-CW says there is no automatic trip. The same claim left in the narrative: review2#6. |
| 2026-10-24-control-review1#13 | Hydrocarbon alarm routed to the compander-trip sequence | medium | closed 3346c49 | The SEQ-CB-START abort has only the compander trips, and AIA-3103 goes to F-HC (S5 operator note). |
| 2026-10-24-control-review1#14 | TSA switch-over condition unmeasurable on the regenerated bed | medium | closed 3346c49 | SEQ-TSA S5 entry is S4 complete, and AIA-2102 / AIA-2103 watch the bed on line (S1). The narrative is not updated: review2#6. |
| 2026-10-24-control-review1#15 | Machines started before anti-surge in auto; GOX dP permissive as text | medium | closed 3346c49 | UIC-3120 is a permissive, UIC-4103 / UIC-4131 are the S6 entry, and S7 has the dP entry with the ESD / BL opening steps. The new order error at XV-4117: review2#2. |
| 2026-10-24-control-review1#16 | Backup blocked below LAL; no hand-back | medium | closed 3346c49 | I-01 / I-02 reset are the permissives, the cold standby is unresolved (H04-A08), S1 completes on the header pressure, S3 hands back, and H04-A20 is cited. The hand-back condition is too early: review2#5. |
| 2026-10-24-control-review1#17 | Durations without ASSUMED | medium | closed 3346c49 | The file header marks every timeout and delay as an ASSUMED placeholder, each sequence lists "the step times (ASSUMED placeholders)", and the 60 s delay is removed. |
| 2026-10-24-control-review1#18 | Statements and values without a design source | low | closed 3346c49 | Trip resets are marked "proposed" (H01-A3, H04-A01), FIC-2105 cites H02-A2, and AIA-3122 23 %, AIA-2102 1 ppm and AIA-2103 -70 C are marked ASSUMED. |
| 2026-10-24-control-review1#19 | The list of thirteen missing trips is inconsistent | low | closed 3346c49 | D-094 now lists the 13 validate warnings by function (SSHH-3108 named once, through SIC-3108's notes; PIC-4101 as the suction vent text that validate flags), with PIC-4102 as a further trip. The narrative and the philosophy refer to D-094 instead of keeping their own lists. This matches the 13 `instrument-no-interlock` warnings. |
| 2026-10-24-control-review1#20 | Wrong citation D-018 for turndown | low | closed 3346c49 | "not defined yet" in loops.yaml, the narrative and the philosophy. |
| 2026-10-24-control-review1#21 | FV-3111 fail-position hint leans against the HAZOP | low | closed 3346c49 | Both consequences named (closed: purge lost; open: H03-S33); the choice is left to H03-A1. |
| 2026-10-24-control-review1#22 | Trips as permissives; incomplete steps | low | closed 3346c49 | SEQ-COMPANDER-TRIP's permissive is removed. Its restart includes UIC-3120 and the E-3104 check. The SEQ-MAC-START abort leaves the trip action to the C&E. SEQ-SHUTDOWN holds the TSA and stops the DCAC pumps after the MAC. Order of the TSA hold: review2#9. |

## Drawing
No P&ID changed on this branch (`cheme diff main --list` shows no changed plant item). The
validate counts at 3346c49 are the same as on main:
- P-01: 0 line-through-label, 2 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-02: 0 line-through-label, 0 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-03: 0 line-through-label, 3 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-04: 0 line-through-label, 1 line-crossing, 0 label-overlap, 0 label-far-from-owner

These crossings are outside the scope of this control review. No tiles were read.

## Checked and fine
- **Controller actions and split ranges** are unchanged from review 1 and still consistent.
  TIC-3109 no longer claims an action.
- **Stream links:** 12 set points named by stream, and validate keeps them equal to the design
  case (0 `control-*` warnings).
- **D-094** now describes the records as they are: the one override (PIC-1103 / FIC-1101),
  the conflicts and missing handles recorded as open, the trip list, and the ASSUMED step times.
- **SEQ-MAC-START** order (water and tray seal, then the MAC on blow-off, then loading in steps)
  agrees with H01-A10 and D-076. UV-1102 is on AIR-1003 at the K-1101 discharge, upstream of
  C-1101 (`cheme show UV-1102`, line list), as S2 says.
- **SEQ-CB-START S7** follows D-024: XV-4133 bleed closed, the ESD and BL valves opened only
  after the dP is equalised through HV-4129 / HV-4130, and the dP measurement left to H04-A01.
- **SEQ-COMPANDER-TRIP** restart conditions follow D-077 (1) and H03-A11. "Keeping the booster
  stopped" with water found matches D-077's "bypassed by stopping the booster flow".
- **Philosophy**: F-AIR, F-POWER, F-CW, F-CHW, F-TSA and F-HC no longer claim protection the
  design does not have. The objectives' order is unchanged, with hydrocarbon safety first.
- Every record still carries "PROPOSED ... not approved for implementation".

## Not checked
- The machine vendors' start-up and protection logic (MAC, compander, K-4101 / K-4102), the
  TSA supplier's sequence, and the cold box supplier's cool-down: none of these is in the design.
- Dynamics and tuning: no dynamic simulation exists.
- The P&IDs beyond the items named above (`cheme show UV-1102`, `AIR-2002`, `GOX-4001`,
  `XV-4117`); no tiles were read. Whether XV-4119 and XV-4120 are downstream of the backup
  risers is taken from D-024's text and the line list, not from the drawing.
- The HAZOP studies were read only for the actions the control records cite. They were not
  re-reviewed.
- `cheme check` was not run.
