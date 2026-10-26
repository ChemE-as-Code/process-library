---
topic: control
reviewed_commit: 8ccc3234de6b689b057ce5164e4ad940c7718d29
scope: [control/loops.yaml, control/sequences.yaml, control/cause-effect.yaml, control/instrument-list.yaml, control/philosophy.md, process/narrative.md, pid/P-02.xml, pid/P-03.xml, pid/P-04.xml, DESIGN.md]
reviewer: Claude (independent control review agent; did not author D-109, D-110, D-111, D-112 or D-113)
reviewer_kind: agent
branch: claude/keen-lovelace-sd87qc
merge: pending
---
# Review: control intent of ASU-1, sixth review (fail positions, turndown, C&E and screening LOPA)

This is an independent process-control review of branch `claude/keen-lovelace-sd87qc` at 8ccc323
against origin/main (87f65f0). The branch has five commits (d818b97 D-109, 3d958b6 D-110,
c5e643d D-111, d3d9a98 D-112 and the regeneration and HAZOP commits ef7ad14 / 8ccc323). The agent
made these proposals on the owner's delegation. It does not claim that the HAZOP team accepted
any of them.

The review looks at the engineering, not only at consistency:
- the D-109 fail positions as one set on loss of air, and one by one on loss of a single signal;
- the D-111 screening LOPA, row by row: the arithmetic, the independence of the IPLs, and the
  targets against D-083 and safety/risk-matrix.yaml;
- I-14 as the independent limit on the GOX draw;
- the D-110 ratio limits;
- the three new instruments on P-02, P-03 and P-04;
- D-112's issue references.

Checks run at 8ccc323:
- `cheme validate` (all rules, with generators): `126 file(s): 0 error(s), 95 warning(s)`.
  - The warnings are 63 `review-finding-status` and 6 `review-unknown-commit` in older layout
    and control records, 12 `template-metadata`, 2 `titleblock-sheet`, 9 `line-crossing` (all
    accepted earlier, see Drawing) and 3 `process-energy-balance`.
  - There is no `instrument-no-interlock` and no `cheme.control-*` warning.
  - Control infos: 59 `control-unresolved`, and every one names its issue. Also 25
    `control-shared-element` (the new ones are the K-4101 loops against I-13 / I-14 / I-17, as
    expected for a machine trip), 15 `control-logic-text` and 10 `control-incomplete`. The
    incomplete ones are vendor loops without an action and LICA-3102 / TIC-3109 / PIC-4106
    without a final element; all are recorded as unresolved.
- `cheme check --no-write` fails three gates:
  - `layout-review`: the layout records are out of date because of the cable schedule, the
    electrical list, the C-3102 datasheet and the model regeneration. A layout reviewer must
    re-stamp them. This record does not review the layout.
  - `issues-basic`: #56, #57, #60, #61 and #79 are still open. The branch answers them, but they
    are not closed.
  - `issues-detail`: 16 items.

  Every other gate is ok, including `pids-valid` and `drawing-clean`.
- `cheme cause-effect`: build/cause-effect.html / .csv has 18 rows (I-01 .. I-18) and 26 effect
  columns. No row has instrument air as its cause.
- `cheme diff origin/main --list`:
  ```
  pid/P-02.xml:
  added ProcessInstrumentationFunction Inst_FSLL2117 [2117]: 21 added, 0 removed, 0 modified
  changed PipingNetworkSystem Line_RG2001 [RG-2001]: 1 added, 0 removed, 0 modified
  pid/P-03.xml:
  added ProcessInstrumentationFunction Inst_LSLL3125 [3125]: 21 added, 0 removed, 0 modified
  changed ProcessColumn C3102 [C-3102]: 4 added, 0 removed, 0 modified
  pid/P-04.xml:
  added ProcessInstrumentationFunction Inst_PSHH4152 [4152]: 21 added, 0 removed, 0 modified
  changed ProcessInstrumentationFunction Inst_PIC4102 [PIC-4102]: 0 added, 0 removed, 1 modified
  changed ProcessInstrumentationFunction Inst_TSHH4104 [TSHH-4104]: 0 added, 0 removed, 1 modified
  changed ProcessInstrumentationFunction Inst_TSLL4113 [TSLL-4113]: 0 added, 0 removed, 1 modified
  changed ProcessInstrumentationFunction Inst_TSLL4114 [TSLL-4114]: 0 added, 0 removed, 1 modified
  changed PipingNetworkSystem Line_GOX4002 [GOX-4002]: 1 added, 0 removed, 0 modified
  ```
  Nothing changed is `not drawn`. Every commit has its PROGRESS.md row and its decision.

**The LOPA arithmetic is right, row by row.** Each row's mitigated frequency is the initiating
frequency times the credited PFDs and modifiers:
- row 1: 0.1; row 2: 0.1; row 3: 1e-4; row 4: 3e-2; row 5: 0.1; row 6: 0.13 (0.3 x 0.1 + 0.1);
- row 7: 1e-2; row 8: 1e-3; row 9: 1e-2; row 10: 1e-3; row 11: 1e-3; row 12: 1e-3; row 13: 0.1;
- row 14: 1e-2.

Each RRF is the mitigated frequency divided by the target, and each SIL is the IEC 61511 band of
that RRF.

The weaknesses are in what goes into those products:
- the targets (#5);
- which layers count as independent (#6, #7);
- one initiating frequency (#8);
- what two of the trips actually do (#1, #10).

**Verdict:**
- **2 high** findings. I-14 does not end the over-draw in several of the causes it is credited
  for (#1). On loss of instrument air with power still on, no trip stops the running drives
  against the closed fail positions (#2).
- 7 medium and 5 low findings.
- control-review5#3 stays open.

The branch should not merge before #1 and #2 are closed or accepted by the owner. The other
findings can be taken to the team's LOPA / SIL session with the proposals. Every record still
says "PROPOSED"; this agent record approves none of them, and the merge is a human's decision.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-26-control-review6#1 | P-03 / P-04 | I-14 (LSLL-3125), PIC-4101 / PV-4101B, D-111 (3), LOPA row 10, H03-S34, H04-S75 / S80 | **I-14 does not end the over-draw in several causes it is credited for.** I-14 trips K-4101 and closes XV-4117. PIC-4101 then vents through PV-4101B, which fails open. The C&E note says the vent takes "no more than the make". That is true only if PIC-4101's set point lies above the suction pressure at the design draw, and that window is still open (#59, control-review5#1). With a set point near 1.15 bara, the vent goes on drawing at the over-draw rate. I-14 also cannot stop the over-draw in three cases. (a) PT-4101 reads high, or PV-4101B's signal is lost: the valve fails open and the vent itself over-draws the sump. (b) The refrigeration deficit H03-S34: the MAC keeps feeding the column and the vent keeps taking the boil-off. (c) FV-3111 failed open, apart from the purge closure. In these cases the SIL 2 function stops only the compressor, while the sump keeps falling. "Acts on the hazard whatever over-draws the sump" (D-111 (3)) is therefore not established, and the credit in H03-S33 / S34 and H04-S75 / S80 is not valid as stated. | high | open | Give I-14 an effect that ends the draw whatever its path. Either force PV-4101B closed through its own SIS solenoid (the LP column stays relieved by PV-3110A/B under PIC-3110 and by PSV-3114, D-011), or unload or trip the MAC as well (that also stops the hydrocarbon input, see #3). Or limit the credit of I-14 to the K-4101 causes, and give the vent-path and refrigeration causes their own layer. Re-run row 10 and the H-03 / H-04 residual ratings with the chosen effect set. State that the "no more than the make" claim depends on #59. |
| 2026-10-26-control-review6#2 | P-01 / P-04 | D-109, F-AIR, C&E (no instrument-air cause), K-4101, XV-4117 / XV-4118 / XV-4116, P-1101A/B / P-1102A/B, H01-S45 | **On loss of instrument air with power on, nothing stops the running machines against the closed fail positions.** D-109 says the plant "stops isolated". In fact it only puts the valves in position: the guide vanes go to their minimum stop and the motors keep running. Two machines are then left running against closed valves. (a) K-4101: its suction ESD XV-4117 and discharge ESD XV-4118 close and the blowdown XV-4116 opens (D-109 table). The oxygen compressor runs on its anti-surge recycle UV-4103 inside an isolated, blown-down loop, with no throughput and with its seal and buffer-gas pressures collapsing. No C&E row, vendor trip or sequence stops it. (b) The DCAC pumps P-1101A/B and P-1102A/B run dead-headed (TV-1105 and FV-1108 closed), which H01-S45 found but D-109 leaves to H01-A17 / H01-A4. Instrument-air loss with power available (an air compressor or dryer failure) is a separate cause. The HAZOP's power-fail mode covers only air loss "where it follows" a power loss. | high | open | Add an interlock on the instrument-air header pressure low-low (its own transmitter(s), set above the pressure at which the actuators start to move). It should trip K-4101 (and K-4102 if its vendor wants it) and stop P-1101A/B and P-1102A/B before the valves stroke. Alternatively, trip K-4101 on XV-4117 or XV-4118 "not open" (limit switches). Record the MAC's intended state on air loss (running unloaded on blow-off, or tripped). Add the case "instrument air lost, power on" to H-01 and H-04 for the team. |
| 2026-10-26-control-review6#3 | P-03 | I-14 effect on FV-3111, D-010 (2), OBJ-3, LICA-3102 LAL response, FIC-3111 FAL | **I-14 stops the LOX purge while the MAC keeps feeding the column.** I-14 closes FV-3111 and latches until manual reset. Five records say the opposite. D-010 (2) requires a purge of at least 0.2 % of the O2 product (43 kg/h). The philosophy's top objective OBJ-3 says "the LOX purge never stops". LICA-3102's LAL response says "never stop the purge". FIC-3111's FAL alarm says "never run the column without the purge". F-HC says "keep the LOX purge flowing". After an I-14 trip, the MAC and the TSA keep delivering air, so traces of hydrocarbons still enter the sump. The sump is at its lowest level, which is when concentration is worst, and it has no purge until someone resets the trip. Closing a 470 kg/h purge does little against a GOX over-draw of thousands of kg/h. The C&E note's "losing the purge for minutes" is not guaranteed while the trip is latched and the reset is by hand. | medium | open | Either keep the purge: let I-14 close only the LOX route above the FIC-3111 minimum (43 kg/h), or not touch FV-3111 at all. Or, if the purge must close, have I-14 also unload or trip the MAC (see #1), so that no new hydrocarbon enters while the purge is stopped. Then make OBJ-3, the LICA-3102 / FIC-3111 responses and D-010 say the same thing. |
| 2026-10-26-control-review6#4 | P-01 .. P-04 | D-109 table, PV-4101B, PV-3110A/B, XV-2109, PV-4109 / PV-4110, LV-1106 | **The fail positions were checked on air loss only, not on a single signal loss in normal operation.** D-109's rule names both ("on loss of instrument air, or of the signal"). However, the "why" column argues only the plant-wide air-loss state. On a single signal loss, the rest of the plant keeps running. (a) PV-4101B fails open while K-4101 runs: it over-draws the LP sump to VNT-4003 (#1), and it is also a continuous O2 release in normal operation (the D-031 zone). (b) PV-3110A/B fail open: the LP column depressurises, the column and condenser balance shift, and the GOX suction falls. H03 has the PV-3110B scenario, but D-109 does not weigh it. (c) LV-1106 fails closed: the DCAC floods while the pumps run, which I-06 catches. That outcome is acceptable, but D-109 should say so. (d) PV-4109 / PV-4110 fail open: the tank pressure is lost, and with it the backup pumps' suction margin during a backup run. Each case may well be acceptable, but D-109 does not show that the set is right for single failures, and the HAZOP actions it answers (H01-A6, H02-A6, H03-A1, H04-A14) ask for both. | medium | open | Add a "single signal loss, rest running" column to the D-109 table, with the safeguard that catches each case (I-06 for LV-1106, I-14 with the fix of #1 for PV-4101B, the PV-3110 alarms, the tank pressure alarms). Hand the cases to the team with H01-A6 .. H04-A14. |
| 2026-10-26-control-review6#5 | - | D-111 (5) tolerable frequencies, safety/risk-matrix.yaml, D-083 | **The asset targets disagree with the proposed risk matrix and with D-083.** D-111 sets asset targets of 1e-1 / 1e-2 / 1e-3 per year for severity 3 / 4 / 5, and calls them "consistent with D-083 and the proposed matrix". The matrix uses the same cells for every category. At severity 3, a frequency of 1e-1 lies in likelihood D (1e-2 to 1e-1), which is band **high**: "not tolerable as it stands". 1e-2 at severity 4 (C/D boundary) and 1e-3 at severity 5 (B/C) are also high. So a scenario that meets its LOPA target would still be rated high, and the matrix would require an action for it. D-083 scenario B (an asset and production case) used 1e-2, not 1e-1. With matrix-consistent targets one order lower (or two), the outcome changes: rows 5 and 13 need RRF 10 (SIL 1), row 6 needs 13 (SIL 1), and row 14 (K-4102) needs RRF 10. That reverses "no SIF on the K-4102 guide vanes" (D-111 (4)). | medium | open | Derive the asset targets from the matrix: a residual likelihood that keeps the band at medium or lower, e.g. sev 3: C (1e-2), sev 4: B (1e-3), sev 5: A (1e-4). Alternatively, record why the asset category may use a looser criterion, and change the matrix to match. Re-run rows 1, 2, 4, 5, 6, 9, 13 and 14, and correct the "consistent with D-083" sentence. |
| 2026-10-26-control-review6#6 | - | LOPA rows 3, 10, 14; FIC-3111, the D-110 clamps, LICA-3102 / PIC-4106 alarms | **Layers in the basic process control system are credited, contrary to the branch's own records and the CCPS independence rules.** (a) Row 3 credits the LOX purge FIC-3111 (0.1), but loops.yaml calls FIC-3111 "a safety-relevant regulatory loop, but not a safeguard". The purge is also a continuous design feature, not a layer that responds to a breakthrough. Row 3 also credits the AIA-3103 alarm with operator response, which makes two BPCS layers in one row. (b) Row 14 credits the D-110 clamp as an IPL (0.1), and row 10 uses the D-110 ratio limit to lower the initiating frequency. D-110 (4) says "these limits stay in the control system (not protection layers, D-096)". (c) Rows 10 and 14 credit a BPCS alarm (LICA-3102, PIC-4106) while the initiators include BPCS failures (selector, FT-4148, PT-4150, PIC-4105) that may sit in the same controller. CCPS generic practice allows at most one BPCS credit per scenario, and none when the BPCS failure is the initiator, unless the alarm's sensor, logic and operator interface are shown to be independent. | medium | open | Credit the purge as a condition of design, not an IPL. Keep at most one BPCS credit per row, and state for each alarm credited why its controller is independent of the initiator. Make D-110 (4) and D-111 agree on whether the ratio limits are a layer. Recompute rows 3, 10 and 14. Row 3 then needs RRF 100 (SIL 2, or a second analyser, H02-A1), and row 14 needs RRF up to 10. |
| 2026-10-26-control-review6#7 | P-02 | LOPA rows 4 and 6, I-08 (FSLL-2117), I-10 (TSHH-2107) | **I-08 and I-10 are credited for each other, and each is then left without a SIL.** Row 4 credits I-10 (PFD 0.1) to find RRF < 1 for I-08. Row 6 credits I-08 (0.1) for the low-flow causes to find RRF 1.3 for I-10. Both come out SIL "a". A function credited as an IPL at 0.1 must itself be designed, independent and proof-tested to that PFD. A SIL "a" function has no such requirement, and if both sit in the BPCS they are not independent of the FIC-2105 / XV-2109 initiators either. The result is circular. | medium | open | Credit at most one of the two in the other's row, and give the credited one at least a PFD of 0.1 with its proof test (in effect a SIL 1 or an IPL outside the BPCS). Or drop the cross credit, which gives row 4 RRF 3 and row 6 RRF 1.3 against the present targets, more with #5. Record where each trip's logic runs (heater supplier's panel, SIS or BPCS). |
| 2026-10-26-control-review6#8 | P-03 | LOPA row 8, I-12 (PDSLL-3115), K-3101 / KT-3101 seal gas | **The seal-gas row starts optimistic, and the trip does not stop the mechanism.** Row 8 takes 1e-2/yr for "seal gas lost". The seal gas is a utility supply (filtered process air or N2 through a regulator and filter), and the CCPS generic values for a utility or regulator failure are of the order of 0.1/yr. At 0.1/yr row 8 needs RRF 1000, the SIL 2/3 boundary. The C&E note also says the lube oil keeps running through the run-down. Oil therefore keeps migrating past the seal for the run-down time after I-12 has acted. What actually protects the sump is restoring the seal gas (a backup supply) or the oil system stopping, and neither is in the function. | medium | open | Justify 1e-2 (a redundant seal-gas supply with automatic change-over would justify it) or use 0.1. Add the backup seal-gas supply or the oil system's response to the function, or credit it as a separate layer. Ask the compander vendor (#58) for the run-down oil quantity against the explosive-quantity modifier. |
| 2026-10-26-control-review6#9 | - | D-110 (4), FIC-4148 / FIC-3107 limits, FT-1101 | **The ratio limits rest on a single air-flow transmitter and ignore the liquid draws.** The direction of the min-select is right: on a ramp down the measured flow is the lower one, and on a ramp up the lagged one. But F_air comes from FT-1101 alone, which is also FIC-1101's measurement. If FT-1101 reads high, FIC-1101 cuts the real air (and the make) while the limit rises. One fault then both lowers the make and raises the limit, which is a new over-draw cause for H04-S80 that D-110 does not list. Also, R_GOX = S7/S2 holds only at the design LOX/LIN make. When the operator raises the LOX withdrawal (filling T-4101) or the liquid make (#62), the GOX make per kg of air falls but the limit does not. The 5 min lag is "of the order of the column's response", while the LP column's product response is usually tens of minutes. On a ramp up the limit can therefore run a little ahead of the make (2.5 % of design at 0.5 %/min). | medium | open | Use a validated air flow for the limits (a second flow measurement, or a check against the MAC guide-vane position or power, with the lower value taken on disagreement). Subtract the liquid draws above design from R_GOX x F_air (or the O2 equivalent of the LOX/LIN draws). Size the lag on the column's simulated or supplier response (#60 close-out). Add the FT-1101-high cause to H04-S80. |
| 2026-10-26-control-review6#10 | P-04 | LOPA row 9, I-13 (TSHH-4104) | **The oxygen-fire trip acts after ignition, but row 9 credits it against the outcome that ignition already causes.** TSHH-4104 detects a fire that has already started. An oxygen fire in a compressor can consume the stage within seconds, so the "loss of the machine" (asset 5) is largely done before the trip acts. What the trip can still prevent is escalation: fire carried into the header, more oxygen fed from the suction and discharge inventories, and the fire wall challenged for longer. As written, SIL 1 against "ignition in the machine 1e-2, asset 5" overstates what the function delivers. | low | open | Restate row 9's consequence as the escalation the trip prevents (the header and the inventories isolated within a stated response time), with its severity. Set the response time with the K-4101 vendor (#58). |
| 2026-10-26-control-review6#11 | P-03 | I-14 final elements and sensors, I-11 / I-12, FV-3111 | **The SIL 2 architectures are not stated, and one final element is a BPCS control valve.** I-14 (SIL 2) uses a 1oo1 LSLL-3125. One of its final elements is FV-3111, the BPCS control valve of FIC-3111: not tight-shut, shared with the loop (`control-shared-element`), with no separate solenoid recorded. PDSLL-3115 (I-12, SIL 2) is also 1oo1. A 1oo1 SIL 2 in low demand is allowed by IEC 61511-1, but only with SIL 2 capable devices, a separate actuating path for a shared valve, and a PFD that the three subsystems meet together at the proof-test interval. None of this is recorded beyond "SIL 2 capable devices". | low | open | Record the intended architecture of I-11, I-12 and I-14 for the SRS (voting, shared-valve solenoid, proof-test interval). Consider 1oo2 for LSLL-3125, the LP sump being the plant's dominant hazard. With #1 / #3, drop FV-3111 from I-14 or give it an SIS solenoid. |
| 2026-10-26-control-review6#12 | P-03 | LSLL-3125 drawing, C-3102 nozzle I4 | **The low-low tap is drawn above the level-control tap, and a DP level has one nozzle.** On P-03 (`build/P-03_crop-270-100-370-200.png`), LSLL-3125's measuring line meets C-3102 at about y 148.5 mm, above LICA-3102's at about y 153. A reader takes it to sense higher than the controller, while its trip must lie below the LAL. The datasheet adds one nozzle, I4. A cryogenic DP level needs a liquid and a vapour connection, and "own tapping" should cover both, or say that the vapour leg is shared. | low | open | Move the LSLL-3125 sense point below LICA-3102's on the drawing (`cheme move` or `cheme copy --sense-at`). On the C-3102 datasheet, state I4 as the liquid tap with its own vapour reference, or name the shared vapour leg. |
| 2026-10-26-control-review6#13 | - | philosophy F-GOXC, F-AIR, D-111 (6) | **The machine-trip responses do not name the new interlocks.** F-GOXC lists no interlocks, although I-13, I-14 and I-17 are now the K-4101 trips. After an I-14 trip it also says nothing on the operator's job: turn the air flow down, restore the purge, and check the sump before the reset. D-111 (6) says the sequences name the interlocks, yet I-14 appears only in a note of SEQ-CB-START. F-AIR's interlock list ([I-03, I-04]) does not show which trips are lost or defeated on air loss (I-04 by TV-3124, the backup by PV-4111 / PV-4112). | low | open | Add `interlocks: [I-13, I-14, I-17]` and the post-I-14 response to F-GOXC. Name in F-AIR the trips air loss defeats. Correct D-111 (6). |
| 2026-10-26-control-review6#14 | - | DESIGN.md D-109 .. D-111 open items | **Not every open point in the decisions names its issue.** D-112 closes this for the YAML and narrative records, and validate confirms all 59 there. In the decisions, some items have none: D-109's backup air supply points only to H04-A14 (#105 exists); D-111 "Not done" for the hydrocarbon limits (#104 exists) and for the SIS architecture (no issue); and the team's LOPA / SIL session that D-111 and D-113 depend on (no issue). | low | open | Add #105 and #104 where they apply. Open (or name) an issue for the SIS architecture / SRS and one for the LOPA / SIL session. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-control-review5#3 | PIC-4101's tap drawn on S2 but modelled on S1. | low | open | Not touched on this branch: Inst_PIC4101 is not in `cheme diff origin/main --list`, and the sense position is unchanged. The last records (maturity-review3, pid-review1) carry it open too. |
| 2026-10-24-layout-review23#2 | The model has no tap point per line-mounted instrument; no rule checks the reach of line-mounted transmitters. | low | open | Carried because DESIGN.md is in both scopes. Not examined here: ef7ad14 regenerated the model and the cables, but the review of the layout is the layout reviewer's (the `layout-review` gate fails). |
| 2026-10-24-layout-review24#1 | The AI-3104 and FIC-4148 bubbles on P-04 are 0.5 mm apart and read as touching. | low | open | `cheme show AI-3104 --sheet pid/P-04.xml` at 8ccc323: still at 21.25..34.75 mm, and FIC-4148's group starts at 35.25 mm. Not moved on this branch. |

## Drawing
`cheme validate` at 8ccc323 gave these drawing counts:
- P-01: 0 line-through-label, 2 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-02: 0 line-through-label, 0 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-03: 0 line-through-label, 3 line-crossing, 0 label-overlap, 0 label-far-from-owner
- P-04: 0 line-through-label, 4 line-crossing, 0 label-overlap, 0 label-far-from-owner

All four sheets have 0 text-outside-frame, 0 title-text-overflow and 0 line-through-symbol.

These are the same counts as at pid-review1 (P-04) and review 5. The crossings are the ones
accepted in checks/checks.yaml, and `drawing-clean` is ok. None of them involves an object this
branch added.

Rendered and read:
- `build/P-02_crop-100-90-230-160.png`: FSLL-2117 senses RG-2001 S2 (Tee_RG2001_B to E2101_N1).
  Its tap is on the E-2101 riser, after the bypass tee and away from the XV-2109 bypass leg.
  FIC-2105 is upstream of FV-2105 on S1. So the tap is on the heater side only, as D-111 says.
- `build/P-03_crop-270-100-370-200.png`: LSLL-3125 senses C-3102 nozzle I4, separate from
  LICA-3102's I3. The drawn tap order is #12.
- `build/P-04_crop-200-20-300-90.png`: PSHH-4152 has its own PT-4152 on GOX-4002 S7,
  downstream of XV-4118 and the check valve, beside PT-4102. The new note at PIC-4102 reads
  "K-4101 IGV master (D-096); HH: PSHH-4152, C&E I-17".

The reworded P-04 trip notes read "see C&E I-13", "LALL-4107 / TSLL-4113: see C&E I-01 / I-15"
and "LALL-4108 / TSLL-4114: see C&E I-02 / I-16". They name the right interlocks. "LALL-4107" is
LIA-4107's LALL condition, not a listed tag, as before this branch (`cheme.label-tag` info only).
No tiles were rendered.

## Checked and fine
- **LOPA arithmetic:** each row's product, RRF and SIL band is correct (see above).
- **SIL 2 for the compander overspeed (I-11):** plausible. Wheel burst is a people-4 hazard, a
  2oo3 speed trip is the industry's normal answer, and RRF 100 at the band boundary goes to SIL 2.
- **SIL 1 for I-17 with PSV-4122 credited:** reasonable. PSV-4122 is on the machine side, with
  the relief case "K-4101 blocked outlet (XV-4118 closed)". It limits the machine's discharge
  pressure, and with it the header pressure.
- **SIL 1 for I-15 / I-16 and SIL a for I-18:** reasonable at screening, with their modifiers
  marked ASSUMED.
- **I-07 depends on its modifier:** D-111 says honestly that I-07 holds SIL 1 only through the
  modifier, and names the second analyser if the intake survey finds sources (subject to #6).
- **FSLL-2117, LSLL-3125, PSHH-4152 independence:** each has its own primary element, tapping
  or transmitter, separate from the control loop it backs (P&ID reads above). The instrument
  list, the C&E and the C-3102 datasheet agree.
- **D-109, as one set on air loss:** the choices are coherent:
  - the cold box keeps its liquid (LV-3101, FV-3106 closed);
  - the LP column is never blocked in (PV-3110A/B and PV-4101B open, PSV-3114 last);
  - the DCAC water in and drain close together (TV-1105, FV-1108, LV-1106, LV-1107), so it
    cannot flood;
  - the TSA valves fail last, which is the only choice that meets H02-A6;
  - FV-2105 open with XV-2109 open puts the heater at low flow, and FSLL-2117 (I-08) trips it;
  - the BL blocks and bleeds, the backup valves closed, and the consequence for the backup
    (H04-S90, #105) are stated honestly.

  The gaps are #2 (running drives) and #4 (single signal loss).
- **D-112 TV-3124 fail open:** acceptable. A tight-shut fail-closed valve would lose the trim on
  a signal fault (D-067), and the D-077 restart permissive (E-3105 shell side checked dry)
  covers the leak case on both compander trip and air loss.
- **D-110 (1) to (3) and (5):** the range and ramp are plausible ASSUMED values for an LP
  double-column plant with one expander and are marked for the client. FIC-1101 is not slaved to
  the pipeline pressure, with the reason. The 30 min PV-4101B-open alarm makes turndown venting
  transient. The cap at the design make and the min of the measured and lagged flow act in the
  right direction (the remaining points are #9).
- **D-112 (1):** every `unresolved` entry in loops, sequences, philosophy and narrative ends with
  its issue (59 `control-unresolved` infos, none without "#").
- **Consistency:** loops.yaml `interlocks:` links, the instrument-list notes, the sequences'
  trip conditions (I-05 .. I-07 in the MAC start abort, I-07 .. I-10 in SEQ-TSA, I-11 / I-12 in
  SEQ-CB-START, I-15 / I-16 in the backup sequences) and narrative.md tell one story.

## Not checked
- The H-01 .. H-04 revisions of D-113 beyond the scenarios named above. They are the HAZOP
  reviewer's.
- The machine vendors' own protection, run-down times and actuators (#58).
- The cold box's behaviour after air loss with the HP column still holding pressure: E-3103
  keeps boiling the LP sump from the HP vapour inventory while FV-3111 is closed and the vents
  are open. This needs a dynamic check.
- The PV-3110A/B and PV-4101B capacities, and PIC-4101's set-point window (#59).
- The layout, cable and take-off regeneration of ef7ad14 (layout reviewer).
- Full-sheet tiles of P-02, P-03 and P-04 (only the three crops above were read).
- Dynamics and tuning. No dynamic simulation exists.
