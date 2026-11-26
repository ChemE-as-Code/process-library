I'd hold the merge: the review found two high findings and judged the stage not acceptable. One is new from this stage and one is an earlier fix I reopened. The review record is committed alone as `5654308d`; nothing was pushed, merged or signed off.

**Checks**
- **`cheme validate`:** 0 errors, 1266 warnings and 679 info items.
  - The largest warning counts are line crossings (318), pipe clashes (201, where the listing stops), operability, missing supports, free spans and headroom (158).
  - Expected for later sheets: P-404's 18 undrawn items (it is still to be drawn in S9) and the open P&ID and list findings left for the S9 close-out.
  - Not explained: the 318 line crossings. S7b had 209 warnings in total and S8 changed no P&ID.
  - I did not run `cheme validate --fail-on warning` separately.
- **`cheme fmt --check`:** clean.
- **Stage basic gates:** 5 pass, 5 fail. The failures are `drawing-clean` (the P-403 crossing), `design-review`, `layout-3d` (200 pipe clashes, 63 pipes through equipment, 15 through steel, 158 headroom), `lifting-study` (the centrifuges S-301A to C) and `layout-review`. `layout-plot-plan` and `mto` pass.

**What I looked at:** the plot plan (`build/layout-plan.png`), the section across both fermenter rows (`build/layout-section-x159.png` and its 1:100 crop) and the section along row 1 (`build/layout-section-y122.png`).

**Findings** (in `reviews/2026-11-26-S8-review.md`, topic `layout`):
1. **High – the fermenter rows are not clean in 3D.** Besides the clashes, the model generates 216 one-valve access platforms. Many are at 21.78 m with their own stairs from grade, in the 5 m strip between each shell and the rack; I saw them on the section. The header branch valves sit on the risers, where nobody can reach them from the deck or the rack.
2. **Medium – drives on separate steel.** The 12 t agitator drives stand on the independent top frame while the shaft passes through the head nozzle. The vessel and frame move apart: roughly 40 mm of heat growth during steam sterilisation (my own ASSUMED estimate), plus hydrostatic stretch and foundation settlement. That movement crosses the double mechanical seal at the sterile boundary.
3. **Medium – top-head valves under the grating.** The deck is 0.7 m above the head top, but the head is 2.25 m deep. The top-head valves therefore sit 0.7 to 2.9 m below the deck and cannot be worked from it, as DESIGN.md (D-043) claims.
4. **Medium – escape from the top decks.** Each 112 m deck at 24.5 m has stairs only at its two ends, about 55 m of travel from the middle. No escape zones are declared, although the stage task asked for them.
5. **Medium – headroom.** The seed-building workaround (L-11, the core limit recorded in DESIGN.md) produces most of the 158 headroom findings. They hide real ones: pipes crossing road R-5 at 5.9 m and drops over T-201's roof.
6. **Low:**
   - The drive lifts to the deck are not in the lifting study.
   - The crane radii are measured from the centres of 110 m long crane pads.
   - The centrifuge removal lanes are blocked by their own lines.
   - P-404 is marked "drafted" but is an empty template.
   - The 318 line-crossing warnings have no stated cause.

**Previous findings:**
- **Closed:** the unplaced items (S6#10, by `57de7dfe`) and the 15-NA-2152 route (S5b#9, by `b4910b49`).
- **Reopened, high:** the T-301 overfill finding (S6#1). `cheme status` lists XV-3013 for P-301 but it is not drawn. The S7b review had closed this finding from the lists without rendering the sheet.

The scores and the carry-over list for the next stage are in `build/agent-run/S8/review.json`, which is not committed. Scores: process 3, safety 2, drawing 2, consistency 3.

Merge pending: the branch should not be merged or signed off while the two high findings are open.
