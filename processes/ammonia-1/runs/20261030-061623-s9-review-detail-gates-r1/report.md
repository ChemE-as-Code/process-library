I approve PR #264 (S9, ammonia-1). I did not merge it, because it is stacked on `stage/basic-layout`. The review record is `reviews/2026-10-30-detail-gates.md` (commit f06d2cd, pushed), and the verdict is posted as a PR comment.

**Checks I re-ran myself:** `cheme validate` gives 0 errors and 239 warnings, CI is green, and `cheme check --stage detail` matches the PR body's per-gate table:

| gate | result | why |
|---|---|---|
| hvac | ok | |
| control-complete | ok | |
| layout-detail | fails | a core limit: the road headroom rule has no case for buried pipes |
| electrical | fails | a core limit: only one power tray level per rack, so the overfull trunk tray can't be split |
| datasheets | fails | vendor and mechanical data are missing |
| issues-detail | n/a | the plant declares no issues |

Nothing was relaxed or accepted.

**Spot checks:**
- Compressor and pump powers match their datasheets, and stream S28 matches the stream table.
- The ventilation rate of 298 m³/h per kW is correct.
- The P-302 reflux-pump estimate is about 2 % high (S28 is 5 mol % water), which is immaterial.

**New findings (no critical or high):**
- **Medium #1 – merge order:** this PR makes two basic-stage gates worse on the branch it merges into. layout-3d goes from passing to failing on the 4 buried road crossings. The lifting study goes from 8 to 12 findings, because motor cable trays now run over K-101, K-102, K-103 and K-701. Merge S9 only after the basic sign-off is on main, then point the PR at main.
- **Medium #2 – branches not buried:** some cooling water branches are not at the 1.8 m depth DESIGN.md D-038 states. CWS-1063 (DN 400) runs at +0.2 m, on grade, across the main rack strip. CWS-1052 (DN 700) breaks grade, and CWS-1085 has about 0.55 m cover.
- **Medium #3 – overlapping routes:** the cooling water supply and return of K-101, K-501 and K-701 end at the same point, so their routes overlap. The model still counts them as routed.
- **Low #4:** DESIGN.md D-039 and the PR body say 274 cables; the schedule has 180.
- **Low #5:** the motor ratings and catalogue cable sizes are too small, so the tray fill is a lower bound. The 400 m low-voltage feeders lose about 15 % voltage, and the 35 mm² 10 kV cables would not survive the fault current.
- **Low #6:** the committed `plant-model.yaml` does not rebuild identically with cheme 1.0.1 here, although the inputs are the same. The run used core v1.0.0, and the gate findings are unchanged.
- **Low #7:** the yard for the 150 kV substation transformers is not placed in the layout. The control-room air intake has no ammonia detection or damper trip.

I carried the earlier open findings forward. One is high: 2026-10-29-design#1 (lifting-study and maturity-balanced still fail). It belongs to the base PR #257 and blocks the basic sign-off, not S9.

Merge pending: PR #264 is approved but stays unmerged until the basic sign-off is on main (finding #1).

FINDINGS: critical=0 high=0 medium=3 low=4
VERDICT: approve
STATUS: DONE