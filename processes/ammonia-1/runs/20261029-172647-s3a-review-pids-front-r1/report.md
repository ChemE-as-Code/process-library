I approved S3a (PR #246) and merged it into main as merge commit `0a8f671`, so no merge is pending. The branch already contained everything on main, and all 93 CI checks passed before the merge.

**Checks, re-run at d95ef58:**
- **`cheme validate`:** 0 errors and 110 warnings. The PR body says 106; the extra 4 are notices that the four drawing scripts are not declared as sheet generators, which is expected because the sheets are maintained by hand. The other warnings are the layout model's (S5's work) and one carried over from S2.
- **Drawing checks:** 0 problems on all four sheets.
- **The five S3a gates:** pids-exist, pids-valid, drawing-clean, process-basic and process-links all pass.
- **Gates that still fail:** design-review, layout-3d, lifting-study, mto, maturity-balanced and layout-review belong to later sections, and none was relaxed.
- **Coverage:** every front-end equipment item is on a sheet. The only flowsheet change is the stream-to-line links.

**Engineering:** I looked at all four sheets. I recalculated the pipe sizes (DN) of seven lines from the stream table and they are right. I also checked the values taken from earlier design decisions (D-014, D-015) against the simulated streams, and they match. Assumed values are marked as such, and I found no third-party content.

**New findings** (the record is `reviews/2026-10-29-pids-front.md`; my verdict comment is on the PR):
1. **Medium:** the waste-heat-boiler risers are smaller than their downcomers: SM-1038 is DN 300 against DN 450, and SM-1040 is DN 125 against DN 200. At the stated circulation ratio of 5 the steam-water mixture would move at about 30 m/s, so the risers need resizing.
2. **Medium:** trip I-101 (low-low process steam) does not close the tail-gas valve XV-1105, so the furnace keeps firing the reformer tubes with no process flow through them. The record also doesn't say that XV-1001, which sits before the fuel split, cuts the natural-gas fuel as well.
3. **Medium:** trip I-104 acts through the level control valve LV-1307, so it is not independent of the control loop that most likely caused the high level. Gas breaking through from V-201 into the low-pressure condensate stripper is not recorded as an open case.
4. **Low:** the cooling-water lines are sized at about 2 m/s, not the stated 1.5 m/s basis.
5. **Low:** the combustion-air damper is tagged FV-1108, a loop number that already belongs to the furnace pressure trip PZ-1108; its controller is FIC-1110.
6. **Low:** the equipment-list duties for E-203 and E-105 are the concept values, not the simulated ones the line list uses.

I carried forward 10 open findings from the earlier review records unchanged; none of their files changed on this branch.

The review record says `merge: pending` because it was written before the merge, and records are not edited afterwards.

FINDINGS: critical=0 high=0 medium=3 low=3
VERDICT: approve
STATUS: DONE