My verdict on S5b of ammonia-1 (PR #257, round 2, topic `layout`) is **fix**. The layout record is `reviews/2026-10-30-layout-s5b-r2.md`, reviewed at d09e1e1 and committed in cd6d0fd. The branch is pushed and the PR comment is posted. Nothing was merged, and the merge is still pending.

**Checks I re-ran:**
- `cheme validate`: 0 errors, 202 warnings (my record adds none).
- `cheme layout build --check`: the model is current, with no clash or headroom finding.
- `cheme check --stage basic`: `layout-review` now passes on this record. Two gates still fail:
  - **lifting-study**: 8 lanes are blocked and none is accepted: H-101, E-104, E-402, K-501, E-501, E-502, E-505, E-504.
  - **maturity-balanced**: the feed flows and compositions have no source (`sourced.boundary`), and two H-101 conversions are still assumed (`model-basis`).
- `cheme assess estimate --check`: no bulk estimate exists, because `estimate/rates.yaml` still holds the example values.

No gate was relaxed and nothing was accepted. The fix round did clear the V-701, E-301 and E-303 lanes by re-routing AL-1129 and DW-1073, and moved laydown LD-204 off the road. That closes both findings from the round-1 layout review.

**New findings:**
- **medium #1:** the re-routed DW-1073 runs at 0.6 m across crane pad CP-203, the pad for X-401. It is also a 52 m run at grade with no declared vehicle crossing, so it closes off X-401, the new pads CP-211/CP-212 and laydown LD-201 from the north road.
- **medium #2:** several crane pads lie under process piping 4.75 to 9.1 m up. On CP-703, the new V-701 pad, AG-1121 runs through the middle and two other lines run at about 9 m on either side. CP-205, CP-206 and CP-207 have pipes over them, and CP-204, CP-211 and CP-212 have one just inside an edge. `cheme layout lifting` does not check this; it lists it under "Not covered". So the lanes it reports clear from these pads are not shown to be workable.
- **low #3:** the E-504 row of the owner proposal offers a layout change (move it 2 m north). It is still put to the owner as an erection-sequence case.

The high finding 2026-10-29-design#1 stays open: S5's targets are not met. The two failing gates are listed above, and the estimate is class 5, not class 4.

FINDINGS: critical=0 high=0 medium=2 low=1
VERDICT: fix
STATUS: DONE