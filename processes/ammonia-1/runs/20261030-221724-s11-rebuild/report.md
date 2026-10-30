The rebuild on core v1.2.1 removed the three `layout-clash-pipe` findings on CWS-1144 and changed nothing else. It is committed on `stage/detail-core120` as a5f5ffc, and the working tree is clean.

- **Skills:** `cheme skills update` wrote nothing; all 131 skill files were already current.
- **Layout model:** apart from its hashes, `layout/plant-model.yaml` changed in only 6 coordinates. The ends of the three supply header segments moved 1 mm (219.652 → 219.653, 221.652 → 221.653, 223.652 → 223.653), onto the points where their branch pipes start.
- **Findings:** no layout finding other than the three clashes changed. Supports without steel are still 87, as in D-048, and there are still no headroom, buried-cover or tray-fill findings. `cheme validate` gives 0 errors and 228 warnings, against 231 in the earlier S11 run; the difference is exactly the three clashes. Nothing was accepted or worked around.
- **Other outputs:** I rewrote the lifting study, cable schedule, material take-off and bulk estimate. Only the model fingerprint in their headers changed: the CSV files are identical and the estimate stays at 103,367.80. The LCA and TEA were already current and needed no rewrite.
- **Gates:** `layout-3d` and `layout-detail` now pass (they had failed only on the clashes), and so do `lifting-study` and `electrical`. Three still fail, none because of this rebuild:
  - `design-review` and `layout-review`: the review records are out of date, and the S10 round 2 layout review has no `## Findings` section. This is for the independent reviewer.
  - `datasheets` (detail stage): equipment weights and nozzle locations need mechanical and vendor data. This was already open before S11.
- **Maturity:** `cheme maturity` is unchanged at calculation maturity "balanced".
- **Records:** D-048 has a new paragraph with the rebuild result (no new decision, since no design input changed), and PROGRESS.md has a new line. The PR comment is in `build/pr-comment.md`. No ASSUMED values or sources were added.

The merge is pending: the orchestrator pushes the branch, and the independent reviewer reviews and merges it.

STATUS: DONE