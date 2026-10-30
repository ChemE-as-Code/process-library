Round 3 of the layout review for PR #257 is done, and the verdict is **fix**. The record is `reviews/2026-10-30-layout-r3.md`, reviewed at a989903. It is committed as aacbaa0 and pushed to `stage/basic-layout` (the push also carried run record a989903, which wasn't on the remote yet). The verdict is posted as a comment on the PR.

**Checks I re-ran myself:**
- **Validation:** `cheme validate` reports 0 errors and 183 warnings, and every drawing count is 0.
- **3D model:** `cheme layout build --check` says the model is up to date, with no clash or zone finding. Every process line of DN25 and larger is routed or skipped with a reason. The only unrouted lines are the cooling-water lines and the furnace ducts, which are skipped as package scope.
- **Take-off:** the MTO is current (10,682.5 m of pipe, 1,210 elbows).
- **Estimate:** no estimate has been written (`cheme assess estimate --check` says it is not current).
- **Basic gates (`cheme check`):** three fail.
  - lifting-study fails: 26 crane lanes are blocked and none is accepted.
  - maturity-balanced fails: the feed and conversion data are not sourced.
  - layout-review failed before this record and passes with it.
- **Maturity:** `cheme maturity` gives calculation maturity none.

**Findings:**
- **Closed:** layout-r2#1. The hand-set routes for the condensate lines PC-1048 and PC-1084 now fall steadily to their destination, with no high or low point and no clash.
- **New, medium (layout-r3#1):** the new fuel-gas hazardous zone Z-HAZ-FUEL does not cover the valves it is declared for.
  - It is two 1 m spheres at the reformer burner inlets, 22 m up.
  - The model already places those valves elsewhere: PV-1101 and XV-1102 (with their access platform) about 18 m away, and XV-1105 about 77 m away.
  - So the zone's stated reason, that the valves aren't placed yet, is wrong. The fix is to add zone volumes at the valves themselves; the zone format allows that. This replaces the older zone finding layout#4, now closed.
- **Carried, high (2026-10-29-design#1):** lifting-study fails, there is no class 4 estimate, and maturity-balanced fails. The author's reasoning holds: an agent cannot close these without accepting a gate or inventing data. This is the third fix verdict on S5, so under the plan's stop rules the next step is your or the orchestrator's decision.
- **Carried, medium and low:** the other open findings from earlier rounds are unchanged.

**Spot-checked values:**
- The tail-gas composition behind the zone (stream S59): 53.5% methane, 9.2% hydrogen.
- The fuel natural-gas composition (stream S2).

Both are consistent with the zone text. I found no third-party content in the changed files.

Merge is pending: the PR is not merged and there is no sign-off.

FINDINGS: critical=0 high=0 medium=1 low=0
VERDICT: fix
STATUS: DONE