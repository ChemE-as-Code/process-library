I closed the two layout findings, but the one high finding (2026-10-29-design#1) is still open. Closing it would mean accepting a gate or inventing data, so it needs a decision from you or the orchestrator.

**Closed (commit 2d93219):**
- **layout#4 (medium):** the H-101 fuel-gas line FG-1002 and tail-gas line FG-1010 now have a hazardous zone (zone 2, `Z-HAZ-FUEL`), as the review asked. The review suggested using the line numbers as sources, but cheme refuses that for a line without an open end. I used the burner inlet nozzles H-101/B2 and B1 instead.
- **layout-r2#1 (low):** the hand-set routes PC-1048 and PC-1084 now fall steadily towards U-801. PC-1048 no longer dips 6 cm, and PC-1084 drops instead of rising 1.5 m. My first PC-1084 change clashed with PC-1136; the second one has no clash.
- After both changes I rebuilt the layout model, material take-off and lifting study, updated D-031 in DESIGN.md, and added the responses to PROGRESS.md (commit 8362a82).

**Still open, design#1 (high):**
- **Lifting study (26 blocked lanes):** 9 are blocked by other equipment, which depends on erection order. 17 are blocked only by piping, which is normally lifted before the pipes go in or with spools removed. Either a human accepts the lanes with the lifting plan's reason, or the gate moves to detail by a plan change.
- **Class 4 estimate:** it needs equipment sizes from the datasheets (S7), a sourced cost index (CEPCI) and material factors, and sourced bulk unit rates. `estimate/rates.yaml` is still the example file, and none of these can be made up.
- **maturity-balanced:** it needs a sourced natural-gas feed and sourced conversions for R100, R102A and H101. That is S1/S2 work and would change the simulation basis.

**Other medium/low findings left open:** layout#3 waits for S7. layout#5 and #8 need rework that isn't quick. layout#6 and #7 need GitHub issues, which this job can't open; the proposed issue texts are in `build/pr-comment.md`.

**Checks:**
- `cheme validate`: 0 errors, 183 warnings.
- Layout model, take-off and lifting study are all current.
- `cheme check` (basic) fails on lifting-study and maturity-balanced. design-review and layout-review also fail now, because this fix changed DESIGN.md and the layout, so both reviews need another round.
- `cheme maturity`: still none.

The PR comment is in `build/pr-comment.md`. Nothing is pushed, and the merge is pending: not merged, no sign-off. This was the last fix round the plan allows, so it is now a stop-and-ask point.

STATUS: BLOCKED: design#1 (high) needs a human decision. The 26 lifting lanes need a human to accept them or a plan change. The class 4 estimate needs sourced rates, a cost index and the S7 datasheets. maturity-balanced needs a sourced feed and conversions from S1/S2.