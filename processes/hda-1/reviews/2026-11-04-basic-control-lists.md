---
topic: design
reviewed_commit: d3afa8689ba2f5f438b23f7426c160d371168ab6
scope: [control/, process/narrative.md, pid/, plant.yaml, equipment/equipment-list.yaml, piping/line-list.yaml, piping/special-items.yaml, process/flowsheet.yaml, process/PFD.xml, estimate/, lca/, scripts/s4_pump_powers.py, scripts/s4_fail_positions.py, DESIGN.md, PROGRESS.md]
reviewer: review-agent
reviewer_kind: agent
branch: stage/hda-1-basic-control-lists
merge: pending
---
# Review: design (control and lists of hda-1, S4, PR #357, re-review round 1)

This is an independent re-review of PR #357 (issue #302) at d3afa86. It follows the fix commits
f125d37e, 7d85d78b, b3cd4719 and d3afa868, which answer the panel's round-1 findings. The
panel's findings had no record of their own, so they are listed here as #1 to #17 with their
resolution. #18 and #19 are new. The reviewer re-ran the following with core v1.4.1 (core main
ab9d91e) at d3afa86:

- `cheme validate`: 39 files, 0 errors, 5 warnings. Four are `pydexpi_composition_fractions`
  (S19 in the BFD and PFD; S22 and S26 in the PFD), the shortcut-column sums of
  2026-11-03-simulation-closeout#18 (core#130). The fifth is `cheme.layout-model-outdated`
  (#28 of the previous record). The drawing lint reports 0 on all eight sheets for every check.
  The cross-checks of the lists against the sheets, of the interlocks against the lists and
  sheets, and of the control records against the lists, P&IDs, C&E and operating cases are clean.
- `cheme control report`: 0 errors, 0 warnings, 0 infos. Loops, sequences, C&E, narrative and
  philosophy are reported as drafted (no review covered them until this record).
- `cheme check`: control-complete, process-basic, process-links, pids-valid, drawing-clean,
  pids-exist, maturity-balanced and every concept gate pass. This record answers design-review.
  layout-3d, lifting-study, mto, layout-review, layout-detail, electrical, hvac and datasheets
  fail. They belong to later sections of runs/plan.md (see #28 of the previous record).
- `cheme maturity`: balanced is reached. Predictive fails only on the three items documented in
  D-021 (model-basis, property-regime, formation-data) and on the datasheets of a later section.
- `cheme assess equipment|tea|lca --check`: all current. The one remaining warning is
  `estimate-equipment-partial` on K-102 (purchased only, no reciprocating FBM), which D-026 and
  the `purchased_installation` source now state.
- `cheme fmt --check`: P-07 and P-08 "would reformat". This PR does not touch either file. Both
  are checked out with CRLF line endings in this Windows worktree (index LF), so this is local
  noise. The PR's `validate (processes/hda-1)` CI job passes.
- Hand checks: there are 34 actuated valves, and each one has a fail position in the instrument
  list (22 F.C., 12 F.O.). F-AIR lists the same 22 closed and 12 open valves. TZ-128 (P-01),
  US-311 and XV-310 (P-03, F.C. fail-action label) are on the sheets, and the C&E ids on the
  P-01, P-02 and P-03 notes match cause-effect.yaml. The D-026 start-up estimate is
  0.3 x 41.1 K / 0.95 = about 13 K, so about 886 K. That is reproducible and below the
  E-101 rating of 918.15 K. The reflux drums V-201..V-203 now carry the vertical-vessel FBM
  2.0098, so purchased-only covers 2 items (H-101, K-102). core#153 is open, and the three hand
  values of the setpoints still match flowsheet.yaml.

Verdict: **approve**. No critical or high finding is open. The one high finding (#1, loss of
quench) is closed. I-106 trips the firing and the feed on an independent TZ-128 after the quench
point, or when both quench pumps stop. So I-201 now leads to it, and the scenario is handed to S6.
The section's target holds. The lists are complete and linked (validate: 0 errors). Loops,
sequences, C&E, narrative and philosophy are written and agree with the P&IDs and the
simulation. The control report is clean, and control-complete passes. Every actuated valve has
a fail position, and the equipment/TEA/LCA checks are current. The open findings are low.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-04-basic-control-lists#1 | control/cause-effect.yaml, P-01 | loss of quench | Panel (process-control): no protective function, and I-201 caused it. Now I-106 trips on TZ-128 TAHH (a new element on PG-108 after the quench point, independent of TIC-115) or on P-102 and P-102B both stopped. It acts on US-112 and US-122. The TAHH lies between 893 K and the E-101 rating of 918 K. The S6 scenario is stated in I-106 and D-026. The I-201 notes now point to I-106. | high | closed 7d85d78b | - |
| 2026-11-04-basic-control-lists#2 | control/sequences.yaml | start-up quench order | Panel (process-control): the quench stays in SEQ-START-RXN S6. S5 states that E-101 takes the unquenched effluent (about 886 K, own estimate, ASSUMED, D-026) and completes only with TZ-128 below its alarm. The TZ-128 leg is never bypassed. The header, TIC-115 and the narrative agree. | medium | closed 7d85d78b | - |
| 2026-11-04-basic-control-lists#3 | control/cause-effect.yaml, P-03 | K-102 / PSA protection | Panel (process-control): I-301 (package cause) stops K-102, holds the PSA and closes the new purge shutdown valve XV-310 (F.C., HG-113) through US-311. FV-211 stays the loop's valve. SEQ-START-PSA aborts on I-301 and opens XV-310 only in S2. | medium | closed 7d85d78b | - |
| 2026-11-04-basic-control-lists#4 | control/sequences.yaml | K-101 in SEQ-EDP | Panel (process-control): K-101 keeps running in S1. A new S2 stops it at the vendor's minimum suction pressure (PT-219) or at once on I-203. | low | closed 7d85d78b | - |
| 2026-11-04-basic-control-lists#5 | DESIGN.md, control/philosophy.md | global instrument air failure | Panel (process-control): handed to S8 as a simultaneous relief and flare load case (XV-209 with PV-104, PV-504, PV-404, UV-207 and PV-303) in D-026 and F-AIR. | low | closed d3afa868 | - |
| 2026-11-04-basic-control-lists#6 | control/loops.yaml | LIC-506 pairing rationale | Panel (process-control): the rationale now states that the reflux is the larger outlet at R 2.18, so the LV configuration is chosen deliberately. A dynamic check follows at S7. | low | closed 7d85d78b | - |
| 2026-11-04-basic-control-lists#7 | control/sequences.yaml | SEQ-TRIP-RXN after I-104/I-105 | Panel (consistency): S1 now has the operator close XV-120 and XV-121, so it completes after a fuel or BMS trip. I-104, I-105 and I-106 are in the reset conditions of SEQ-TRIP-RXN and SEQ-START-RXN. F-FUEL agrees. | medium | closed 7d85d78b | - |
| 2026-11-04-basic-control-lists#8 | control/loops.yaml | TIC-115 operator note | Panel (consistency): the note now says the quench goes into service in SEQ-START-RXN S6. | medium | closed 7d85d78b | - |
| 2026-11-04-basic-control-lists#9 | P-01, P-02, instrument list | I-105 / I-203 not referenced | Panel (consistency): the US-112 service and P-01 note now name I-101, I-102, I-104, I-105 and I-106. US-122 and its note name I-101, I-102, I-106, I-202 and I-203. The P-02 notes name I-203, and P-03 names I-301 (grepped). | medium | closed f125d37e | - |
| 2026-11-04-basic-control-lists#10 | control/philosophy.md | F-AIR closed list | Panel (consistency): LV-102 (and XV-310) are added. The counts match the instrument list, with 22 closed and 12 open. | low | closed 7d85d78b | - |
| 2026-11-04-basic-control-lists#11 | DESIGN.md | I-104 light-off bypass | Panel (consistency): D-026 and the philosophy now name the BMS's own bypass of the I-104 low-low leg during light-off. | low | closed d3afa868 | - |
| 2026-11-04-basic-control-lists#12 | control/instrument-list.yaml | TI-124 / FFI-217 S4 deferrals | Panel (consistency): both are at the S4 state. Voting is deferred to S6, and FFAL is recorded under FIC-103 at the D-007 limit, with its value set in S6. | low | closed f125d37e | - |
| 2026-11-04-basic-control-lists#13 | piping/special-items.yaml | PSV-413 relief case | Panel (consistency): it now reads "if LV-202 and XV-204 stick open or pass (both fail closed, D-026)". | low | closed 7d85d78b | - |
| 2026-11-04-basic-control-lists#14 | estimate/tea.yaml, cost-basis.yaml | purchased_installation scope | Panel (integrity): V-201..V-203 are priced like V-100 (vertical-vessel FBM 2.0098). The factor now covers H-101 and K-102 only, and its source gives the K-102 reason (ASSUMED, likely low, replaced in S5). The outputs were regenerated and are current. | low | closed b3cd4719 | - |
| 2026-11-04-basic-control-lists#15 | lca/lca.yaml | small-pumps-power reason | Panel (integrity): the reason gives the s4_pump_powers.py values (about 10 kW shaft, about 90 MWh/a against the 120 MWh/a upper estimate). The TEA power omission (about 2 %) is stated in D-026. The LCA is current. | low | closed b3cd4719 | - |
| 2026-11-04-basic-control-lists#16 | control/loops.yaml, DESIGN.md | flow setpoints unlinked (core#153) | Panel (integrity): tracked as open input I-13 in DESIGN.md (restore the stream links of FIC-103, FIC-108 and FIC-211 once core#153 is fixed; core#153 still open). The FIC-103 source names the propagated S3 provenance. The core limit remains and is documented. | low | closed d3afa868 | - |
| 2026-11-04-basic-control-lists#17 | control/cause-effect.yaml, DESIGN.md | practice citations | Panel (integrity): the I-105 note says that no burner-management code was read, that EN 746-2 and NFPA 86 are named for orientation only, and that the code is the vendor's and S6's to set. API Std 521 7th ed. section 5.20 is named, with the caveat that it comes from a secondary index and the standard was not read, so S8 confirms it. | low | closed d3afa868 | - |
| 2026-11-04-basic-control-lists#18 | control/cause-effect.yaml, control/sequences.yaml | I-106 reset text vs start-up | New. The reset comment of I-106 asks for "a quench pump runs with TIC-115 in control". But SEQ-START-RXN needs I-106 reset in its permissives, and P-102 only starts in S6. SEQ-SD-PLANT S4 also says I-106 "is reset before the next start" with the pumps stopped. The start-up bypass of the pumps-stopped leg makes this workable, but the reset text does not say so. | low | open | reword the reset: TZ-128 below the trip point, and either a quench pump running or the pumps-stopped leg in its start-up bypass |
| 2026-11-04-basic-control-lists#19 | P-01 | TZ-128 trip signal not drawn | New. The TZ-128 signal to US-112 is in the DEXPI model and the C&E, and the P-01 note names TZ-128. The signal line is not drawn, because any route crosses PG-106 and NG-137 (D-026). The previous record had the same kind of gap for FZ-110 (2026-11-04-basic-pids#14), and it was closed by drawing the line. | low | open | draw the signal (with an accepted crossing or an off-sheet reference) with the detail P&IDs (S9) |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-27-pfd-lci-review#9 | fuel-gas credit methods side by side | low | open | carried (I-11); outside this PR |
| 2026-11-03-concept-closeout#5 | H-101 bare-module factor 2.5 without a read source | low | open | carried to the class 4 estimate (S5); core#129. The factor now also covers K-102, with its reason stated (#14) |
| 2026-11-03-concept-closeout#16 | EUA price from a secondary report | low | open | carried to the next TEA revision |
| 2026-11-03-concept-closeout#18 | ammonia-1 attributes the ISO 6976 methane value to NIST | low | open | outside this PR (processes/ammonia-1); process-library#321 |
| 2026-11-03-simulation-closeout#18 | composition sums of shortcut-column streams | low | open | 4 pydexpi_composition_fractions warnings at d3afa86; core#130 open |
| 2026-11-03-simulation-closeout#19 | process/reactions.yaml R101B wording | low | open | unchanged at d3afa86 (line 9) |
| 2026-11-03-simulation-closeout#20 | process.yaml catalog leftovers | low | open | process.yaml not changed by this PR |
| 2026-11-04-basic-psa#12 | superseded scripts/purge_h2_recovery.py kept on HEAD | low | open | still present at d3afa86 |
| 2026-11-04-basic-psa#13 | D-024 break-even rounding 0.73 vs 0.735 | low | open | DESIGN.md line 1146 still "below about 0.73" |
| 2026-11-04-basic-psa#14 | what checks the road clearances (layout-plot-plan vs cheme validate) | low | open | not changed by this PR |
| 2026-11-04-basic-pids#11 | P-204A/B minimum flow | low | open | kept as the pump-selection open item (D-025, S5) |
| 2026-11-04-basic-pids#15 | blind header ends as off-page connectors | low | open | core#151 still open; P-07/P-08 not changed |
| 2026-11-04-basic-pids#19 | slanted measuring and signal lines | low | open | not changed by this PR (detail P&IDs) |
| 2026-11-04-basic-pids#27 | derived assessments not current | low | closed 06f9619d | `cheme assess equipment/tea/lca --check` all current at d3afa86 (b3cd4719 regenerated them again after #14/#15); the K-102 FBM gap is stated in D-026 and tea.yaml |
| 2026-11-04-basic-pids#28 | 3D model outdated | low | open | `cheme.layout-model-outdated` still reported; belongs to the 3D section |
| 2026-11-04-basic-pids#29 | XV-209 and other valves without a fail position | low | closed cdd2890b | all 34 actuated valves have an F.O./F.C. on P-01 to P-06 and in the instrument list; XV-209 F.O. (D-026) |
