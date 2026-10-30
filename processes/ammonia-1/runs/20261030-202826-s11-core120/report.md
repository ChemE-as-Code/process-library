S11 is done and committed on `stage/detail-core120` (6 commits, working tree clean). The electrical gate now passes, but `layout-3d` and `layout-detail` still fail on three clash findings caused by a 1 mm rounding difference in core's router (details under "Not done"). The PR description is in `build/pr-body.md`. The merge is pending: the orchestrator pushes, and an independent reviewer reviews and merges.

**What changed**
- **Buried cooling water:** all 20 cooling-water lines are now declared buried, with 1.0 m least cover (ASSUMED) and 1.2 m under roads (the package default). The four road-headroom findings at the header crossings no longer exist, so I removed only their four now-unused acceptances. No acceptance was added or widened.
- **Headers routed by the router:** the 20 pinned header segments are gone. Each header now runs along PR-1 between its battery limit and a dead-end point, and all 56 CW pipes are routed.
- **Branch layout:** the router places each tee near where its user is, not at the old S9 positions, so the old branch lanes no longer fitted. At the old depths, branches crossing each other were left with only 0.55–0.94 m of cover. I lowered the headers to 3.8 m and the branches to 2.4 m below grade (ASSUMED) and added three new lanes. The three return lines with control valves keep their valves above grade.
- **Checks on the CW changes:**
  - The same 8 crane lanes are blocked as at basic sign-off, by the same items; no lane reopened.
  - Support steel is unchanged: 260 generated posts, 3 stubs and 26 sleepers.
  - Missing-support notices dropped from 131 to 87, because the buried runs need no steel.
- **Electrical:** the power trays are now split by voltage class: PR-1 has two 10 kV trays and one 400 V tray; PR-10 and PR-7 have two 10 kV trays each. All 8 tray-fill findings are gone, with no voltage or separation findings. The cable schedule now has 11 power cables (3,339 m) and 169 instrument cables (9,941 m).
- **P-106:** a blind flange now closes the DW-1073 drain valve outlet (review finding s10-r2#3).
- **Outputs rewritten** (s10-r2#1):

  | Output | Before → after |
  |---|---|
  | Buried pipe in the take-off | 1,803.9 m, listed separately (DN 1400: 493 m) |
  | Bulk estimate (example rates, prices nothing real) | 103,353.55 → 103,367.80 |
  | LCA dataset | current again |
  | TEA | unchanged |

- **Records:** D-048 in `DESIGN.md` and a line in `PROGRESS.md`. The two outdated skills were updated; neither had local changes.

**Results**
- `cheme validate`: 0 errors, 231 warnings (236 at the start).
- `cheme maturity`: calculation maturity is balanced, unchanged.

| Stage | Pass | Fail | n/a |
|---|---|---|---|
| concept | design-basis, concept-lists, process-concept, process-balances, process-links-concept, assumptions-marked, layout-plot-plan | — | issues-concept |
| basic | process-basic, process-links, pids-valid, drawing-clean, pids-exist, lifting-study, mto, tea, maturity-balanced, relief-on-pid | design-review, layout-review, layout-3d | issues-basic |
| detail | electrical (failed before), hvac, control-complete | layout-detail, datasheets | issues-detail |

**Not done or open**
- **Core defect, not accepted and not worked around.** For three supply tees (CWS-1052, CWS-1063, CWS-1074), the router ends the header segment at x 219.652, 221.652 and 223.652 but starts the branch at 219.653, 221.653 and 223.653. The clash check then reports each branch 0.00 m from its own header segment. These three findings alone fail `layout-3d` and `layout-detail`; they need a core issue filed.
- The review records are stale, and `reviews/2026-10-30-layout-s10-r2.md` has no `## Findings` section; both are for the reviewer.
- The datasheets gate fails on missing weights and nozzle schedules, which were outside this job.
- The HAZOP team needs to reassess the P-106 node.
- Trench excavation for the buried network is in neither the take-off nor the estimate.
- The tee order on P-114 does not follow the plot, so some branches run back along the header. Reordering them is a change for the next revision of P-114.

STATUS: DONE