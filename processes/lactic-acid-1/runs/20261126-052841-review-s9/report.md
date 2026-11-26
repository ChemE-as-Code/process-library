I've reviewed S9 and committed the record as `reviews/2026-11-26-S9-review.md` (dffccaa2). It has 7 new findings: 4 medium, 3 low, none high. The scores are in `build/agent-run/S9/review.json`, which is not committed: process 4, safety 3, drawing 3, consistency 3. I marked the S9 work acceptable, but the branch still can't be signed off because S8#1 (high) is open. A merge is pending.

**What I checked**
- `cheme validate`: 0 errors and 1250 warnings, and `cheme fmt --check` is clean.
  - Expected warnings: layout clashes, headroom and supports (S8#1, S8#5), the provenance-script info, and the old review records' status format.
  - One warning is not expected: `layout-model-outdated`. The line list changed in 430b92e2, after the layout model was rebuilt in a46d755e.
- Gates for stage basic: 6 ok, 4 failing (design-review, layout-3d, lifting-study, layout-review), each for a stated reason. `cheme check --stage basic` also names the outdated model under lifting-study.
- I rendered and looked at the whole of P-404, a crop of the T-401A/B tanks, and a crop of the T-301 fill line on P-301.

**Closed:**
- **S6#1 (high):** XV-3013 is on P-301 with its tag label and the LSHH-3013 signal; I saw it on the render.
- **S7b#3:** drawing-clean now passes.
- **S7b#7:** the ethanol tank overfill and low-level trips (I-403, I-404) are in.
- **S8#7:** P-404 is drawn.

I also answered S8#8: the 318 line-crossings in S8 were 123 unaccepted plus 195 already accepted on P-203/P-206, unchanged since S7b.

**New findings, all on P-404 or the layout**
1. **Trip valves without tags (medium):** XV-4807A/B and XV-4704 show no tag on the sheet. The acceptances added in S9 say the tag is printed as the valve's label, and the render shows that isn't true. The seven control valves on the sheet are also untagged.
2. **Layout model out of date (medium):** the take-off and lifting study were written from the earlier model. Rebuild them at the final commit.
3. **Ethanol tank blanketing not drawn (medium):** T-402's nitrogen supply, blanketing regulator and pressure-vacuum valve are missing; the vent is only a stub labelled "PVRV + FA".
4. **No pump valves or minimum flow (medium):** none of the 8 pumps has isolation or check valves, so the parallel spares would back-flow. P-472A/B have no minimum-flow path.
5. **Purge to an open drain (low):** the author asked me to confirm this end, and I don't. The purge carries ethanol and ester traces into an open drain hub in the ethanol area. It should be a connector to a closed drain to waste-water treatment.
6. **Smaller drawing and control points (low):**
   - PIC-4610 has no signal to the K-461A/B pump speed.
   - The remote input to FFIC-4701 is not drawn.
   - One connector label sits above the product line, so it reads as that line's destination.
   - There is no relief basis for E-404A/B or E-461.
   - The condenser duty (13.1 MW) doesn't match the roughly 11.8 MW I get for the vapour flow.
7. **Status table partly unchecked (low):** the DESIGN.md basic-engineering table marks two gates "ok expected" without running them at the final commit.

The main balance checks out: 14.2 t/h of product at 88 wt% is 12.5 t/h of lactic acid, which is 100 000 t/a over 8000 h. S9 changed nothing in the fermentation area, so its open findings (S5#1, S5#2, S5b#2/#3, S2#1, S8#1 to #4) remain. The JSON's carry-over list gives the order in which the next stage should fix things.
