S5b round 2 gets a **fix** verdict: two of the section's gates still fail. The high finding 2026-10-29-design#1 stays open. Nothing is merged, and the merge is still pending.

**What I re-ran myself:**
- `cheme validate`: 0 errors, 203 warnings, and nothing flagged on any of the 14 P&IDs.
- `cheme check --stage basic`: process, P&ID, `layout-3d`, `mto` and `tea` pass. With my record committed, `design-review` passes too (agent review only).
- **`lifting-study` fails** on 8 blocked lanes: H-101, E-104, E-402, K-501, E-501, E-502, E-505 and E-504. That is down from 11, and the reduction came from real design changes. None was accepted. The 8 left can only be cleared by an erection sequence, so they are put to the owner in `build/lifting-acceptance-proposal.md`.
- **`maturity-balanced` fails** for two reasons:
  - The feed rates (S1, S12/S61, S26/S70) are results of this design, so no published source can give them. That needs the owner's feed specification.
  - The furnace's two H2/NH3 burnout conversions are now honestly marked `assumed`, which is what my round-1 finding asked for, so no source covers them yet.
- `layout-review` also fails because the layout review is out of date; the separate S5r layout review covers that.
- `cheme layout build --check`: the 3D model is current and has no clashes.
- `cheme assess equipment --check`: the equipment cost files are current.
- No bulk estimate exists, because `estimate/rates.yaml` still holds the example values.

**Spot-checks:**
- I downloaded the cited Chemical Engineering PDF. It gives the 2023 annual CEPCI as 797.9, which matches `estimate/cost-basis.yaml`.
- I recomputed the vessel cost correlation for V-101 by hand. The 2001 base cost of about 71.1k USD and the escalation ratio of 2.0098 both match the file.
- The R-501 converter feed of 294 t/h is plausible for 1500 t/d of ammonia.

**The estimate:** it is honestly declared class 5, not the class 4 the plan asked for. It prices 14 of 52 items, at purchased cost only, and the reasons are stated in D-035.

**New findings:**
- **Medium (s5b-r2#1):** the installation, indirect and contingency factors in `rates.yaml` were left as the example. D-035 argues nothing publishable exists, but factors from published cost-engineering textbooks are facts we may cite with a source; the licence rule only excludes licensed databases.
- **Low (s5b-r2#2):** the crane chart is ruled out with the same argument. A few capacity-at-radius values for the heaviest lifts (R-501, C-301) could be cited and checked.
- **Low (s5b-r2#3):** the fans K-102 and K-103 already have simulated sizes, yet the estimate leaves them unpriced.

**Earlier findings:**
- Closed: s5b#1, #3 and #4, and layout-s5b#1 and #2.
- Still open: s5b#2 (medium) and s5b#5 (low: the PR description is still the S5 round-0 text).

The record is `reviews/2026-10-30-design-s5b-r2.md`, committed as 2b6bd0f and pushed. The verdict is posted as a comment on PR #257. Most of what blocks the stage now needs the owner: the lifting acceptances and the feed basis. The remaining agent work is s5b-r2#1 and a published source for the furnace burnout.

FINDINGS: critical=0 high=0 medium=1 low=2
VERDICT: fix
STATUS: DONE