---
topic: design
reviewed_commit: 367e915af2019b540c40bc49d394d774ea71149c
scope: [pid/, plant.yaml, equipment/equipment-list.yaml, piping/line-list.yaml, piping/special-items.yaml, control/, process/flowsheet.yaml, process/BFD.xml, process/PFD.xml, DESIGN.md, PROGRESS.md]
reviewer: review-agent
reviewer_kind: agent
branch: stage/hda-1-basic-pids
merge: pending
---
# Review: design (basic P&IDs of hda-1, S3b, PR #328, re-review round 1)

This is an independent re-review of PR #328 (issue #302) at 367e915. It follows the fix commits
13f44830, 8c2601ad, d97ddb33, 6592383c, fc961ce6, 46081047 and 74817191, which answer the
panel's round-1 findings. The panel's findings had no record of their own, so they are listed
here as #1 to #26 with their resolution. The panel's P-06 tag and line finding is split into
#18 and #19, because one part is closed and the other is open. The reviewer re-ran the
following with core v1.4.1 at 367e915:

- `cheme fmt --check`: clean.
- `cheme validate`: 36 files, 0 errors, 5 warnings. All five are `pydexpi_composition_fractions`
  (S19 in the BFD and PFD; S19, S22 and S26 in the PFD), the shortcut-column sums of
  2026-11-03-simulation-closeout#18 (core#130). The drawing lint reports 0 on all eight sheets
  for every check. The cross-checks of the equipment, line, instrument, piping-item and
  interlock lists against the sheets are clean.
- `cheme check`: process-basic, process-links, pids-valid, drawing-clean, pids-exist,
  maturity-balanced, control-complete and every concept gate pass. This record answers
  design-review. layout-3d, lifting-study, mto, layout-review, layout-detail, electrical, hvac
  and datasheets fail, and they belong to later sections of runs/plan.md (see #28).
- `cheme maturity`: balanced is reached. Predictive fails only on the three items documented
  in D-021: model-basis, property-regime and formation-data. predictive.current, converged,
  coverage, balances and energy-closure pass.
- `cheme assess lca|tea|equipment --check`: not current (see #27).
- Sheets rendered with `cheme render` and inspected at about 11 px/mm in a browser: P-01
  (feed cut-off, fuel double block and bleed, V-100 LZ-123, E-101 S2, HG-104, HG-232 entry,
  TI-124), P-02 (V-101 drain, PSV-215 to FL-234, HG-232 take-off, UIC-207 inputs, FI-216 and
  FFI-217), P-03 (PSV-307 upstream of HV-332) and P-08 (steam branch arrows).
- Hand checks: the saturated-vapour densities 2.416, 7.592 and 21.13 kg/m3 at 0.45, 1.5 and
  4.2 MPa match steam-table values (D-025 cites NIST SRD 69). The 10/13 rule now reads
  correctly in special-items.yaml, D-025 and the PR body (6/9 = 0.67 < 0.77). E-207 and P-202A/B
  are both at 10 barg. core#151 (no blind flange or end cap in the authoring API) exists and is
  open.

Verdict: **approve**. No critical or high finding is open. The one high finding (#1, the
reactor loop feed cut-off) is closed. XV-120 and XV-121 by US-122 are drawn, they are effects
of I-101, I-102 and I-202, and I-102 opens XV-209 automatically. The section's target holds:
every PFD section is on a P&ID sheet declared in plant.yaml (P-01 to P-08). pids-exist,
pids-valid, drawing-clean, process-basic and process-links pass. The lists agree with the
sheets (0 errors). Relief devices and control loops are drawn where the design needs them, and
the off-page connectors are consistent. The open findings are low. #15 is a documented core
limit (core#151).

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-04-basic-pids#1 | P-01, P-02, control/cause-effect.yaml | reactor loop feed cut-off, depressuring | Panel (engineering): I-101, I-102 and I-202 left the toluene and make-up hydrogen flowing; depressuring was manual. Now XV-120 (TO-103) and XV-121 (HG-104) are drawn F.C. by US-122 and are effects of I-101, I-102 and I-202. I-102 also opens XV-209. SIL and voting are deferred to S4/S6 in the C&E header and D-025. Checked on the rendered P-01. | high | closed 46081047 | - |
| 2026-11-04-basic-pids#2 | P-02 | H2/aromatics ratio | Panel (engineering): FI-216 is now on HG-115 and FFI-217 computes the ratio, with a low alarm at 5 (D-007). The trip and the control intent are S4 items in D-025. | medium | closed 46081047 | - |
| 2026-11-04-basic-pids#3 | P-02, P-01 | K-101 anti-surge | Panel (engineering): HG-232 now leaves the discharge ahead of CV-115 and enters PG-110 upstream of E-102 (off-page connectors consistent on P-01 and P-02). FT-218, PT-219 and PT-220 are drawn as signal lines into UIC-207, with TI-221 and VI-222 added. The surge study is a vendor open item. | medium | closed fc961ce6 | - |
| 2026-11-04-basic-pids#4 | P-01 | H-101 fuel train | Panel (engineering): double block and bleed XV-112/XV-125 with the F.O. bleed XV-126 (NG-139) and PZ-127 (I-104). Pilots and BMS are in the heater package, stated on the sheet note and in D-025. | medium | closed 13f44830 | - |
| 2026-11-04-basic-pids#5 | P-03 | HV-332 vs PSV-307 | Panel (engineering): the PSV-307 take-off now sits upstream of HV-332 (rendered and checked). | medium | closed d97ddb33 | - |
| 2026-11-04-basic-pids#6 | P-02, P-04 | tube-rupture PSVs to atmosphere | Panel (engineering): PSV-215 now discharges via FL-238 into FL-234, and PSV-414 via FL-442 into FL-443, both to the flare. Gas detection on the CW return is an S6/S9 open item in D-025. | medium | closed 6592383c | - |
| 2026-11-04-basic-pids#7 | P-01, P-02 | V-100 low-low, quench pumps | Panel (engineering): LZ-123 now stops P-101/P-101B (I-103), and I-201 also stops P-102/P-102B. | medium | closed 13f44830 | - |
| 2026-11-04-basic-pids#8 | P-02, P-03 | K-101 isolation, K-102 class, CV-115 | Panel (engineering): the K-101 isolation philosophy (depressure, N2 purge, spectacle blinds, S9) is now in D-025. K-102 is ReciprocatingCompressor, HV-327 is downstream of CV-127, and the CV-115 type is open with the vendor. | low | closed 46081047 | - |
| 2026-11-04-basic-pids#9 | P-02 to P-06 | CW isolation valves | Panel (engineering): D-025 now lists them as an S9 open item, which is one of the fixes the finding offered. The thermal-relief PSVs are kept for the blocked-in case those valves create. | low | closed 46081047 | - |
| 2026-11-04-basic-pids#10 | P-01 | HG-104 backflow, R-101 temperatures | Panel (engineering): a B/L block valve and a check valve are now on HG-104, and TI-124 (bed and skin, multipoint) is on R-101. I-102 sensor voting comes from S4/S6. | low | closed 13f44830 | - |
| 2026-11-04-basic-pids#11 | P-06 | P-204A/B minimum flow | Panel (engineering): kept as the declared open item for the pump selection (D-025, S5). | low | open | add a minimum-flow line or relief when the pump type is chosen (S5) |
| 2026-11-04-basic-pids#12 | P-02 | V-101 drain on AR-116 | Panel (drawing): AR-116 was lowered, and DR-240 and its vertical note are now clear of AR-116, XV-204 and LV-202 (rendered and checked). | medium | closed 6592383c | - |
| 2026-11-04-basic-pids#13 | P-01 | E-101 nozzle S2 inside the body | Panel (drawing): S2 is now on the bottom outline, and PG-106 runs down and then right to H-101 (rendered and checked). | medium | closed 13f44830 | - |
| 2026-11-04-basic-pids#14 | P-01 | FZ-110 trip not drawn | Panel (drawing): the signal line from FZ-110 to US-112 is now drawn. | low | closed 13f44830 | - |
| 2026-11-04-basic-pids#15 | P-07, P-08 | blind header ends as off-page connectors | Panel (drawing): carried. core v1.4.1 has no blind flange or end cap in `cheme fragment` or the authoring API, filed as core#151 (open). The notes say "(blind)" and name no sheet. | low | open | end the headers at a blind or cap once core#151 lands, or with the S9 detail P&IDs |
| 2026-11-04-basic-pids#16 | P-01 to P-06 | drain note wording | Panel (drawing): all eight drains now read "to closed drain (S9)", placed clear of the arrows. | low | closed 6592383c | - |
| 2026-11-04-basic-pids#17 | P-02 | HG-115 note names M101 | Panel (drawing): the note now reads "to E-101, P-01". | low | closed 8c2601ad | - |
| 2026-11-04-basic-pids#18 | P-06 | P-204A/B tag placement | Panel (drawing, first part): the P-204B tag is now placed the same way as P-204A's. | low | closed 74817191 | - |
| 2026-11-04-basic-pids#19 | P-01, P-02, P-05, P-06 | slanted measuring and signal lines | Panel (drawing, second part): LIC-506, LIC-606, TIC-111, FIC-211, FI-609 and FIC-103 are still slanted. The lint reports nothing and the panel marked this optional. | low | open | make them orthogonal (`--points`) with the detail P&IDs |
| 2026-11-04-basic-pids#20 | P-08 | steam branch arrows mid-sheet | Panel (drawing): the MP and HP headers were moved down, and the branch arrows now sit clear of the next header (rendered and checked). | low | closed 74817191 | - |
| 2026-11-04-basic-pids#21 | P-05, equipment list | E-207 under-rated for the pump shut-off | Panel (integrity): the E-207 benzene side (and BZ-121 downstream) is now rated 10 barg, the P-202A/B design. The choice is recorded in D-025. | medium | closed 46081047 | - |
| 2026-11-04-basic-pids#22 | piping/line-list.yaml | tube-rupture PSVs to atmosphere (integrity lens) | Panel (integrity): duplicate of #6. FL-238 and FL-442 in the line list now go to the flare. | medium | closed 6592383c | - |
| 2026-11-04-basic-pids#23 | special-items.yaml, D-025, PR body | 10/13 rule inverted | Panel (integrity): it now reads "CW-side design below 10/13 of the process side" in all three places (checked). | low | closed 46081047 | - |
| 2026-11-04-basic-pids#24 | equipment and line lists, plant.yaml | stale header comments | Panel (integrity): the headers now describe the S3b state, and the obsolete planned-sheet line is gone. The remaining "status: planned" line in plant.yaml is the template's explanation of the field. | low | closed 46081047 | - |
| 2026-11-04-basic-pids#25 | DESIGN.md D-025, line list | steam densities recalled | Panel (integrity): the values are now cited from NIST SRD 69 (IAPWS-95) saturation rows. The reviewer checked them against steam tables, and the DN is unchanged. | low | closed 46081047 | - |
| 2026-11-04-basic-pids#26 | process/flowsheet.yaml | PV101 without a link | Panel (integrity): it now links to PIC-301 on P-03, and process-links passes. | low | closed 46081047 | - |
| 2026-11-04-basic-pids#27 | estimate/, lca/ | derived assessments not current | New. `cheme assess equipment`, `tea` and `lca --check` all report stale outputs at 367e915. The S3b equipment list grew from 22 to 36 items, and K-102 is now ReciprocatingCompressor, so it loses its centrifugal FBM and becomes purchased-only. In a scratch regeneration the bare-module total (items with all factors) changes from 6.12 to 5.31 MUSD, 11 new pumps/packages are "not covered" (no shaft power), fixed capital goes from 27.36 to 27.41 MEUR, LCOP from 875.5 to 875.6 EUR/t, and the LCA provenance hashes of the equipment list and flowsheet change. No gate reads these files, and the effect on the result is small, but the committed estimate no longer derives from the lists. | low | open | run `cheme assess equipment/tea/lca --write`, and state the K-102 FBM gap and the uncovered spares in the cost basis (or carry them to the S5 class 4 estimate) |
| 2026-11-04-basic-pids#28 | layout/plant-model.yaml | 3D model outdated | New. layout-3d and the gates after it report that plant-model.yaml is outdated against the equipment, line and special-item lists changed by S3b. Those gates belong to later sections, but the concept model was current at 77270ce. | low | open | run `cheme layout build` and commit the model (or at the start of the 3D section) |
| 2026-11-04-basic-pids#29 | P-02 | XV-209 and other P-02 valves without a fail position | New. Since D-025, I-102 opens XV-209 automatically, but P-02 shows no F.O./F.C. on any actuated valve (XV-204, XV-209, UV-207, the control valves). Neither the instrument list nor D-025 states XV-209's fail position. A depressuring valve that fails closed does not depressure on loss of air or power. P-01 marks its new XVs F.C./F.O. | low | open | mark XV-209 fail-open (or record the chosen fail position and why) and add the fail positions on P-02, as on P-01 |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-27-pfd-lci-review#9 | fuel-gas credit methods side by side | low | open | carried (I-11); outside this PR |
| 2026-11-03-concept-closeout#5 | H-101 bare-module factor 2.5 without a read source | low | open | carried to the class 4 estimate (S5); core#129; H-101 is still purchased-only in the regenerated estimate |
| 2026-11-03-concept-closeout#16 | EUA price from a secondary report | low | open | carried to the next TEA revision |
| 2026-11-03-concept-closeout#18 | ammonia-1 attributes the ISO 6976 methane value to NIST | low | open | outside this PR (processes/ammonia-1); process-library#321 |
| 2026-11-03-simulation-closeout#18 | composition sums of shortcut-column streams | low | open | 5 warnings at 367e915 (S19 BFD and PFD, S19, S22, S26 PFD); core#130 open |
| 2026-11-03-simulation-closeout#19 | process/reactions.yaml R101B wording | low | open | unchanged at 367e915 ("open item process-library issue", line 9) |
| 2026-11-03-simulation-closeout#20 | process.yaml catalog leftovers | low | open | unchanged at 367e915 (electricity note still names only the recycle compressor and the toluene pump) |
| 2026-11-04-basic-psa#12 | superseded scripts/purge_h2_recovery.py kept on HEAD | low | open | still present at 367e915 |
| 2026-11-04-basic-psa#13 | D-024 break-even rounding 0.73 vs 0.735 | low | open | DESIGN.md line 1146 still "below about 0.73" |
| 2026-11-04-basic-psa#14 | what checks the road clearances (layout-plot-plan vs cheme validate) | low | open | DESIGN.md line 1079 and PROGRESS.md line 93 unchanged |
