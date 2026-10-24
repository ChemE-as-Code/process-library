---
topic: control
reviewed_commit: 30d4cf9fd385de658396881b87248e737edc0180
scope: [control/loops.yaml, control/sequences.yaml, control/philosophy.md, process/narrative.md, DESIGN.md]
reviewer: Claude (independent control review agent; did not author 302b42e, 7508c3e, 30d4cf9, D-094 or D-095)
reviewer_kind: agent
branch: stage/basic-control
merge: pending
---
# Review: control intent of ASU-1, third review (confirming the review 2 fixes and D-095)

This is an independent process-control review of branch `stage/basic-control` at 30d4cf9
("D-095 LP column pressure on the waste N2, GOX draw on flow (FIC-4148), GAN export pressure
(PIC-4105 / PV-4105)"). It checks the two findings that review 2 left open
(reviews/2026-10-24-control-review1.md #1, #2) and the ten new findings of
reviews/2026-10-24-control-review2.md. It also judges, as a control engineer, whether the
strategy that the project owner decided in D-095 is carried out consistently and correctly.

**On the commit that closes the review 2 findings.** The review 2 fixes were handed over as
7508c3e. That commit is not in HEAD's history (`git merge-base --is-ancestor 7508c3e HEAD`
fails). The branch carries the same change as 302b42e, with the same subject and parent
8b2b324. `git diff 7508c3e 302b42e` shows no difference in the control records, only in
`lca/manifest.json` and two library files. Closures below therefore cite **302b42e**. A
closure that cites 7508c3e would count as open at sign-off (skill `review`, step 7).

The changes were checked against:
- DESIGN.md D-019, D-024, D-094 and D-095;
- the instrument and line lists;
- the flowsheet (S7, S8, S9, S9B);
- P-04, read with `cheme show GOX-4001`, `GAN-4001`, `GAN-4002`, `FIC-4148`, `FIC-3107`,
  `PV-4101B`, `UV-4103` and `PV-4105`;
- the HAZOP studies (H04-S75, H04-A14, H04-A22, H04-A23, H03-A4).

Checks run at 30d4cf9:
- `cheme validate` (all rules, with generators): `111 file(s): 0 error(s), 45 warning(s)`. Of
  these warnings, 9 are `hazop-input-changed`. They are expected, because H-04 is re-stamped by
  its owner after the merge. The rest are the 13 `instrument-no-interlock` trips that D-094
  lists, plus template metadata, title blocks, 6 line crossings and 3 energy balances. None is
  a `cheme.control-*` warning. The control infos are `control-incomplete`,
  `control-unresolved`, `control-logic-text`, and the intended `control-shared-element`
  (TICA-3124 / I-04 / TV-3124). FIC-4148 and PIC-4105 add only their open fail positions,
  together with the open points they declare.
- `cheme diff main --list`: on P-04, FV-4105, Inst_FI4148 and Inst_FIC4105 are replaced by
  PV-4105, Inst_FIC4148 and Inst_PIC4105, and GAN-4002 has 4 modified values (the valve
  reference). On the BFD and PFD, S7 and S9B change (their instrument links). Nothing else
  changes, which matches D-095's "retagged, no geometry changed".

**On D-095.** The decision is the right family of control structure for an LP double-column
cycle:
- the LP column pressure is held on the waste path, and every file now agrees on that;
- the products are taken on flow;
- the two series flow loops on the GAN are gone.

The actions are consistent. FIC-4148 and FIC-3107 are reverse acting on their guide vanes,
PIC-3110 is direct on the waste valves, and PIC-4101 is direct. In PIC-4101's low select, a
falling suction pressure lowers its output and closes the guide vanes, which is the right
direction. The records are also honest about the independent limits that are still open
(H04-A22, H04-A23).

Two problems remain in how the strategy is realised, and both are high:
1. **PIC-4101 cannot be realised as one controller with one set point.** A single split-range
   controller cannot be both a low limit below the normal suction pressure and a vent above it
   (#1). The S7 end state of SEQ-CB-START cannot be reached as recorded.
2. **The export pressure is set by the product flow loops.** D-095 puts the product flows on
   the guide vanes (FIC-4148, FIC-3107), and the records still say that PIC-4102 and PIC-4105
   "hold" the export pressures. With the flow fixed upstream, nothing left can move the mass
   balance of the header (#2). That is the review1#2 conflict in another form. Review1#2 is
   therefore superseded rather than closed.

Verdict:
- review1#1 is closed by 30d4cf9;
- review1#2 is superseded by #2 below;
- review 2 #1 .. #7, #9 and #10 are closed by 302b42e;
- review 2 #8 stays open (low, partly addressed).

New findings: 2 high, 3 medium, 3 low. Every record stays PROPOSED. This agent record approves
none of them. The branch cannot be signed off while #1 and #2 are open.

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-control-review1#1 | Two pressure controllers on the LP column pressure (PIC-3110, PIC-4101) | high | closed 30d4cf9 | D-095 (1), decided by the project owner: PIC-3110 is the LP column pressure master, FIC-4148 sets the GOX draw, and PIC-4101 is a limit. loops.yaml (PIC-3110 rationale, FIC-4148, PIC-4101), the instrument list, the philosophy ("What sets what"), the narrative (CB, PRD) and SEQ-CB-START S1 all agree, and grep finds no file that still makes PIC-4101 the master. How PIC-4101 is realised is wrong: new finding #1. Leftover wording in F-GOXC and SEQ-SHUTDOWN S2: #6. |
| 2026-10-24-control-review1#2 | Two flow controllers in series on the GAN flow (FIC-3107, FIC-4105) | high | superseded by 2026-10-24-control-review3#2 | D-095 (2) removed the second flow loop: FIC-4105 / FV-4105 became PIC-4105 / PV-4105, retagged on P-04. But PIC-4105 throttles PV-4105 in series with K-4102, whose flow FIC-3107 fixes on the guide vanes. A pressure loop in series with a fixed flow can hold the header only while the customer happens to take exactly the FIC-3107 set point. The same holds for PIC-4102 against FIC-4148 on the GOX. See #2. |
| 2026-10-24-control-review2#1 | Air reaches the cold box before the TSA and cold-box permissives | high | closed 302b42e | SEQ-MAC-START S3 is now "Hold on blow-off". It names the missing isolation (AIR-2002), and the MAC stays at minimum load on UV-1102. FIC-1101 goes to auto only in SEQ-CB-START S1, after its permissives: SEQ-TSA running, AIA-2102, PDSLL-3115, PIC-3113. "Regeneration gas available" moved from the SEQ-TSA permissive to the S2 (heat) entry, which breaks the circle. The first-start regeneration source stays unresolved with H02-A10, which is honest. Residual, not a finding: the AIA-2102 "below 1 ppm" permissive is read with almost no air through the bed, so it confirms the bed state only once air flows. |
| 2026-10-24-control-review2#2 | K-4101 started with its suction ESD closed | high | closed 302b42e | SEQ-CB-START S6 closes XV-4116 and opens XV-4117 before K-4101 starts, with UIC-4103 in auto and UV-4103 open (the S6 entry). S7 adds the GAN battery-limit opening (XV-4135 closed, XV-4120 / XV-4134 open), after S5 has required AIA-3105 below 10 ppm. The XV-3105 order that this exposes: #5. |
| 2026-10-24-control-review2#3 | I-03 permissive before the step that can meet it | medium | closed 302b42e | The I-03 reset is now the S2 entry (before K-4101 starts), and S1 fills the tray. That matches H01-A10. |
| 2026-10-24-control-review2#4 | Purge from the first liquid at the design set point | medium | closed 302b42e | S3 sets FIC-3111 to 43 kg/h (ASSUMED, 0.2 % of the O2 product, D-010). S4 raises it to the 470 kg/h of S10 once LICA-3102 is above LAL. The route (T-4101 or V-3101, H03-A5) is stated as open. |
| 2026-10-24-control-review2#5 | Hand-back before the ASU delivers | medium | closed 302b42e | SEQ-BACKUP-GOX S2 completes on PIC-4102 held by K-4101 delivering, with PV-4111 throttling back. SEQ-BACKUP-GAN S2 completes on PIC-4105 (30d4cf9) held by K-4102 delivering. Each says that XV-4119 / XV-4120 are open throughout. |
| 2026-10-24-control-review2#6 | Narrative keeps statements removed elsewhere | medium | closed 302b42e | PUR: AIA-2102 / AIA-2103 watch the bed on line, and the CO2 high-high answer is an operator action pending H02-A1. CB modes include the E-3104 check (H03-A11). |
| 2026-10-24-control-review2#7 | TIC-3109 put in auto without a final element | low | closed 302b42e | The action is removed from SEQ-COMPANDER-TRIP S3. |
| 2026-10-24-control-review2#8 | SEQ-MAC-START aborts on a control deviation | low | open | The abort is now on K-1101 tripped or I-03 tripped, so control noise no longer aborts the start. The second half is still open: the abort still runs SEQ-SHUTDOWN, whose S1 waits for "the customers confirm" while nothing is delivered yet. The proposed MAC stop (unload, stop, then the DCAC pumps, H01-A4) is not there. |
| 2026-10-24-control-review2#9 | TSA held before the MAC is unloaded | low | closed 302b42e | SEQ-SHUTDOWN S4 puts FIC-1101 in manual and stops K-1101. S5 then holds the TSA and stops the DCAC pumps after the MAC (H01-A4). |
| 2026-10-24-control-review2#10 | Casing purge N2 at first start | low | closed 302b42e | Recorded as an unresolved permissive of SEQ-CB-START (UN-3001 from the GAN export or backup header, D-024). |

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-control-review3#1 | P-04 | PIC-4101, FIC-4148, SEQ-CB-START S7 | **PIC-4101 cannot be a low limit and a high vent with one set point.** The register keeps one direct-acting PIC-4101 with a single set point, split range A [0, 50] to the guide vanes through the low select with FIC-4148, and B [50, 100] to PV-4101B. Its target says "the low limit below the normal 1.15 bara, the vent above it". One controller has one set point, and its integral action drives the output to an end whenever the pressure is not at that set point. Case 1, set point below normal (the low limit): in normal operation the measurement is above the set point, the output winds to 100 % and PV-4101B vents the GOX continuously. Case 2, set point above normal (the vent): the output winds to 0 %, output A wins the low select and shuts the guide vanes. Then FIC-4148 can never be selected, and the S7 completion ("PV-4101B closed" and "FIC-4148 at set point") cannot be reached. External reset feedback, the open point D-095 names, stops the integral winding up in the unselected controller. It does not give one output two set points: with it, the proportional term on (P - low limit) still pushes the output into the B range. This is a defect of the recorded structure, not a detail. | high | open | Split PIC-4101 into two controllers on PT-4101 (P-04: one more controller bubble, the D-019 label). (a) A suction low-limit controller, direct acting, set point below normal, into the low select with FIC-4148, with external reset feedback from the selector output. (b) A vent controller, direct acting, set point above normal and above PIC-3110's equivalent, on PV-4101B alone. Then put (b) in auto at SEQ-CB-START S1, and (a) and FIC-4148 in auto at S7. Record both set points as unresolved with their margins. If the owner prefers to keep one tag, record a split range with a gap and two set points, and say how the vendor's controller does it. |
| 2026-10-24-control-review3#2 | P-04 | PIC-4102 / FIC-4148, PIC-4105 / PV-4105 / FIC-3107 | **The export pressures have no mass-balance handle left.** GOX: FIC-4148 fixes the draw on the K-4101 guide vanes, and FT-4148 sits upstream of the vent and recycle tees (`cheme show GOX-4001`). The recycle through UV-4103 therefore does not change the delivered flow, yet the narrative says that "PIC-4102 holds the export pressure", and PIC-4102 still lists "IGV or recycle" as its candidate final elements. The IGV is now FIC-4148's, and the recycle cannot move the header's mass balance. GAN: FIC-3107 fixes the K-4102 flow, and PIC-4105 throttles PV-4105 in series downstream. When the customer takes less than the FIC-3107 set point, PV-4105 closes, the discharge pressure rises and FIC-3107 opens the guide vanes against it: both wind up and K-4102 goes to its anti-surge. When the customer takes more, PV-4105 opens fully and PIC-4105 holds nothing. In both trains a flow loop and a pressure loop share one series path. That is the review1#2 conflict in another form. The backup loops (PIC-4111 and PIC-4112 hold the header when the ASU does not) show that the ASU is the header's pressure source, so the header pressure is not set elsewhere. | high | open | An owner decision, like D-095, for each train. Either (a) pressure master: PIC-4102 sets FIC-4148's set point (and from there FIC-1101's, the GOX-header cascade FIC-1101 already names), and PIC-4105 sets FIC-3107's. PV-4105 then becomes a back-pressure or high limit, or is removed. Or (b) flow master: the products follow the customers' nominations, and PIC-4102 / PIC-4105 become high-pressure overrides (with a select on the guide vanes) rather than holding the pressure. Write the choice into D-095, loops.yaml, the narrative and the philosophy. Remove "IGV" from PIC-4102's candidates unless it goes into a select. |
| 2026-10-24-control-review3#3 | P-03 / P-04 | PIC-4101 low select, D-095 (1), H04-S75 | **The suction low limit acts late on a GOX over-draw.** With PIC-3110 holding the LP column pressure, an over-draw first closes PV-3110A/B: the extra vapour is taken from the waste path. The suction pressure falls only once those valves are shut. Before that, the over-draw shows as a falling LP sump level (LICA-3102) and a falling GOX purity (AI-3104), which is the H04-S75 mechanism. So D-095 and the philosophy overstate the protection when they say that the low select "throttles the draw before an over-draw boils the LP sump down". In addition, the low select is in the same BPCS as the initiating loop FIC-4148, so it cannot be credited for H04-S75 (D-093). The records do keep H04-A23 open for that. | medium | open | Say that PIC-4101's low limit protects the K-4101 suction (sub-atmospheric suction, surge), not the sump. Add the sump-side limit as an unresolved point of FIC-4148, to be decided with H03-A4 / H04-A23: LICA-3102 low, or AI-3104 low purity, overriding the FIC-4148 set point. Correct the D-095 and philosophy sentence. |
| 2026-10-24-control-review3#4 | P-04 | UIC-4103, FT-4148 | **The anti-surge flow input misses the recycle.** UIC-4103 uses FT-4148 (D-024; restated in D-095 and on UIC-4103). FT-4148 is on GOX-4001 S1, upstream of both the vent tee (VNT-4003, PV-4101B) and the recycle return tee (GOX-4003, UV-4103), so it measures the draw from the cold box, not the flow through K-4101. When UV-4103 opens, the machine flow rises but FT-4148 does not, so the anti-surge keeps opening and drives the recycle fully open. On a K-4101 stop, FT-4148 also counts the vented GOX. The location suits FIC-4148 but not anti-surge: the same transmitter cannot serve both. This was there before (D-024), but D-095 confirms the double use. | medium | open | Give UIC-4103 a flow element between Tee_GOX4001_R and K-4101 N1 (GOX-4001 S3, O2-clean; K-4101 vendor). Keep FT-4148 for FIC-4148 only, and correct the UIC-4103 measurement in loops.yaml and the instrument list. Raise it with the H-04 owner (H04-SG06 credits UIC-4103 on FIC-4148). |
| 2026-10-24-control-review3#5 | P-04 | SEQ-CB-START S5 / S6 / S7, FIC-3107, XV-3105 | **The GAN train has no outlet between S5 and S7, and FIC-3107 goes to auto against a closed discharge.** The S5 completion requires "AIA-3105 below 10 ppm (XV-3105 closed)". But K-4102 starts only in S6 and the GAN battery limit opens only in S7, so with the divert XV-3105 closed the HP column GAN has nowhere to go for those steps. The S7 operator note ("off-spec GAN still goes to XV-3105 / VNT-4004 until AIA-3105 is below 10 ppm") contradicts S5. S6 also puts FIC-3107 in auto while XV-4120 is closed and K-4102 is on full recycle. FT-3107 (GAN-4001 S2) sits between the divert tee and the anti-surge return, so its net flow is near zero, the set point of 12510 kg/h cannot be reached, and the guide vanes wind open. This is inconsistent with FIC-4148, which D-095 puts in auto only at S7. | medium | open | S5: require AIA-3105 in specification with the GAN still on the divert (XV-3105 open). S6: keep FIC-3107 in manual on recycle. S7: after XV-4120 / XV-4134 open, put FIC-3107 and PIC-4105 in auto (in the order #2 decides) and close XV-3105. Ramp each product loop from the current flow rather than switching to the design set point (FIC-4148 too). |
| 2026-10-24-control-review3#6 | P-04 | F-GOXC, SEQ-SHUTDOWN S2, FIC-4148, FIC-3107, PIC-4105 | **The machine stops leave the new loops in auto, and two texts keep PIC-4101's old role.** SEQ-SHUTDOWN S2 and failure F-GOXC stop or trip K-4101 / K-4102 without putting FIC-4148, FIC-3107 or PIC-4105 to manual, with the guide vanes at their start position. FT-4148 then measures the vented GOX, and FIC-4148 winds the guide vanes of a stopped machine. F-GOXC ("PIC-4101 vents the GOX through PV-4101B so the LP column pressure stays controlled") and the SEQ-SHUTDOWN S2 completion ("LP column pressure held") still give PIC-4101 the pressure role that D-095 gave to PIC-3110. With D-095, PV-4101B takes the GOX only above its vent limit, and the extra vapour first goes to PV-3110A/B. Whether those have the capacity is not stated. | low | open | On a K-4101 / K-4102 stop or trip, put the product flow loops (and PIC-4105) in manual at the start position, in SEQ-SHUTDOWN S2, F-GOXC and the restart. Reword F-GOXC and S2: "PIC-3110 holds the LP column pressure; the GOX goes to PV-4101B above the vent limit". Add PIC-3110 to F-GOXC's loops, and state or leave open the PV-3110A/B capacity for the GOX. |
| 2026-10-24-control-review3#7 | P-04 | PIC-4105 action | **PIC-4105's action is stated while its tap side is open.** The register gives `action: reverse` ("a rising pressure closes it"). That is right only for a tap downstream of PV-4105, where the loop reduces the pressure. PT-4105 is on GAN-4002 S3, which holds the check valve and PV-4105, and the register itself leaves the side open. With an upstream tap the loop is a back-pressure controller and must be direct. | low | open | Leave the action out (control-incomplete) or make it conditional until the tap side is fixed. #2 may change the loop's job anyway. |
| 2026-10-24-control-review3#8 | - | loops.yaml FIC-4148 / PIC-4105, narrative and philosophy open points, H-04 | **Citations and open-point lists after D-095.** H04-A14 is cited for the fail positions of the K-4101 guide vanes (FIC-4148) and of PV-4105 (PIC-4105), but H04-A14 names neither. It lists PV-4101B, PV-4109 .. PV-4112, UV-4103, XV-4116 .. XV-4118 and XV-3105. The mechanical rename made H04-A22 read "independent of FIC-3107 / PIC-4105", but PIC-4105 does not act on the guide vanes. H-04 line 75 calls FIC-4148 the "anti-surge flow input" only. The narrative's and the philosophy's open points list H04-A22 / H04-A23, but not D-095's own open items (the PIC-4101 realisation, the PIC-4105 tap). | low | open | Cite H04-A14 only once its valve list includes PV-4105 and the K-4101 guide vanes, or cite the plant-wide fail-position list (H01-A6, H02-A6, H03-A1, H04-A14). Hand the H04-A22 wording and the FIC-4148 role to the H-04 owner for the re-stamp. Add D-095's open items to the narrative and the philosophy. |

## Drawing
P-04 changed only by the retag (`cheme rename`; see the diff above). The validate counts at
30d4cf9 are the same as at review 2:
- P-01: 0 line-through-label, 2 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-02: 0 line-through-label, 0 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-03: 0 line-through-label, 3 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-04: 0 line-through-label, 1 line-crossing, 0 label-overlap, 0 label-far-from-owner

The crossings are outside the scope of this review. No tiles were read. Two drawing points
were noted:
- PV-4105 has no actuating signal from PIC-4105 on the sheet (`cheme show PV-4105`: no
  instrumentation), as FV-4105 had none before.
- The FIC-4148 signal to the guide vanes and the low select are not drawn, which D-095 states.

## Checked and fine
- **Actions:**
  - FIC-4148, FIC-3107 and FIC-1101 are reverse acting on guide vanes;
  - PIC-3110 is direct on the waste valves;
  - PIC-4101 is direct, with A [0, 50] on the guide vanes and B [50, 100] on PV-4101B;
  - the low select is linked from both sides (`override`, `select: low`), as
    docs/framework/control.md requires.

  The direction of each selector is right. Only the single set point is wrong (#1).
- **Stream links:**
  - FIC-4148 takes over S7 flow (20860 kg/h, 500 t/d);
  - PIC-4105 takes S9B pressure (9.0 bara = 8 barg);
  - PIC-4101 no longer carries a design value.

  Validate shows 0 `control-*` warnings.
- **Retag carried through:** no FI-4148, FIC-4105 or FV-4105 is left in the control records, the
  instrument list, the narrative or the philosophy (grep). The flowsheet links and H-04
  follow, and the BFD and PFD were rebuilt.
- **One story across the files:** the LP column pressure master (PIC-3110) is the same in
  loops.yaml, the instrument list, philosophy.md, narrative.md, SEQ-CB-START S1 and D-095. The
  wording left over in F-GOXC and SEQ-SHUTDOWN S2 is #6.
- **Sequence points for the new loops:** PIC-4101 (vent) is in auto from S1, while K-4101
  stands. FIC-4148 goes to auto only in S7, when the trains open and K-4101 can take the GOX.
  That is the right point, apart from #1, and #5 for the GAN side.
- **SEQ-BACKUP-GAN S2** completes on PIC-4105 held by K-4102 delivering. The backup riser joins
  GAN-4002 downstream of PV-4105 (Tee_GAN4002_BK on S4), so the hand-back order is physically
  right.
- **D-094** now says that D-095 decided its two conflicts, and its trip list is unchanged.
- **D-095** names its open points honestly: the PIC-4101 realisation, H04-A22 / H04-A23 and the
  PIC-4105 tap. The first is mischaracterised (#1).
- Every record still carries "PROPOSED ... not approved for implementation".

## Not checked
- The machine vendors' capacity control and anti-surge (K-4101, K-4102), and whether the PV-3110A/B
  capacity covers the GOX on a K-4101 trip.
- Dynamics and tuning: no dynamic simulation exists.
- The HAZOP studies beyond the scenarios and actions named above. Their reassessment after the
  retag is the H-04 owner's (`hazop-input-changed`).
- The P&IDs beyond the `cheme show` reads named above; no tiles were read.
- `cheme check` was not run.
