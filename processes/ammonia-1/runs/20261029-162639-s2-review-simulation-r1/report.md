I approved PR #244 (S2 process simulation of ammonia-1) and merged it into `main` as `cd011e8` once all 93 CI checks passed. No merge is pending. The review record is `reviews/2026-10-29-simulation.md` (reviewed at `5173dd1`), and I posted the verdict as a comment on the PR.

**What I re-ran myself:**
- **`cheme validate`:** 0 errors and 1 warning (compressor K601 is 2.2 kW out between two Peng-Robinson calculations; DESIGN.md D-026 documents it).
- **`cheme process simulate --check`:** the design case, which is the only case in the design basis, converges with all 7 recycle loops torn and solved. It exits with code 1 only because of deviation warnings, and each one is documented rather than edited away.
- **`cheme process energy`:** every simulated unit's energy balance closes. The whole-plant energy closure can't be evaluated while component separators are in the flowsheet; that is a known core limit (core#60, still open).
- **`cheme maturity`:** calculation maturity is none. The `maturity-balanced` gate is enabled exactly as the template has it and fails, which meets the plan's target of "evaluated". The requirement that core#315 caps is correctly named as `predictive.property-regime`.
- **Outputs:** the LCA and TEA outputs are current, and the steam and refrigeration script reproduces the values in the flowsheet.

**Engineering:**
- **Provenance:** honest. No given value was overwritten; the only assumed values replaced are the concept balance script's, which the S2 brief allows.
- **Plausibility:** key numbers pass my order-of-magnitude checks: converter temperature rise, makeup compressor power, product flash split, carbon balance, refrigeration COP.
- **Spot-checked sources:** the NH₃, CH₄ and H₂O formation enthalpies match the cited `chemicals` ATcT values exactly.
- **Property package:** the author left the Peng-Robinson substitution for the reviewer to accept or reject. I judged it acceptable for the basic stage; formal acceptance is a human decision.

**New findings:**
- **#1 (medium):** the `maturity-balanced` gate fails partly because four reactor conversions are assumed rather than sourced (R100, R102A, R401, H101). These are standard and can be sourced from open literature. They must be sourced before the basic sign-off (S5r), or that gate will block it.
- **#2 (low):** D-026 gives its list of failing maturity requirements as exact but leaves out `balanced.energy-closure` (K601).
- **#3 (low):** three reactor beds held at fixed outlet temperatures draw 466, 237 and 170 kW from no utility. They were not retuned the way the ammonia converter R501 was.
- **#4 (low):** the steam system, refrigeration circuit and furnace stay script calculations because core has no adjust function. That limit is real, but no core issue is cited, and the furnace stack-temperature deviation has no owner.

Still open from earlier reviews: concept#1 and R-03 (medium), and concept#2–4 and R-05 (low).

FINDINGS: critical=0 high=0 medium=1 low=3
VERDICT: approve
STATUS: DONE