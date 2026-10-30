My verdict on the layout review of PR #257 (S5 of ammonia-1, at commit b0cb9d7) is **fix**. The record is `reviews/2026-10-29-layout.md`, committed as 958a739 and pushed to `stage/basic-layout`. The verdict is also posted as a PR comment. Nothing is merged; the branch still waits on review approval before the sign-off.

**Checks I re-ran myself:**
- `cheme validate`: 0 errors, 182 warnings.
- `cheme layout build --check`: the 3D model is current and has no clashes.
- Every process line of DN25 and larger is routed or skipped with a reason. The 20 cooling-water lines are unrouted, but the gate excludes them; that exclusion was already on main.
- With this record committed, gates `layout-3d` and `layout-review` now pass.
- Gates `lifting-study` (26 findings) and `tea` (no price for demineralised water, blowdown and cooling water) still fail. So does `maturity-balanced`.
- The class 4 estimate is not done: the unit rates file is still the example.
- No gate was relaxed. The only change to `checks.yaml` uncomments the `tea` gate as written.

**Source spot-checks:**
- **Ammonia price:** USGS gives 450 USD per short ton for 2025, which matches the cited value.
- **Electricity price:** I could not confirm the Eurostat band IG figure; my search did not return it. The averaging arithmetic is correct.

**New findings: 0 critical, 0 high, 6 medium, 2 low**
- **#1 (medium):** E-401 has no crane pad within reach. `DESIGN.md` (D-031) and the PR body both say every heavy item has one.
- **#2 (medium):** no east rack connects the south rack PR-7 to the main rack PR-1. The ammonia product line AL-1128 runs 432 m where about 100 m would do, and other lines from the south-east areas detour the same way.
- **#3 (medium):** the material take-off has no pipe classes and no insulation, even on cold ammonia and hot reformed-gas lines. It leaves out the two DN1400 cooling-water headers and the furnace ducts.
- **#4 (medium):** hazardous-zone sources are incomplete. Only compressor seals and three natural-gas flanges are declared. The 15 MPa synthesis loop, the ammonia systems, X-601 and the fuel gas have none.
- **#5 (medium):** access and escape defects on the declared platforms: 4 ladders reach no floor, 9 have pipes through the cage or rails, and 12 pipe risers leave less than 0.6 m of walkway.
- **#6 (medium):** the toppling rule (keep a tall item one height away from a rack) is dropped for the area racks, and nothing tracks it. X-601, 20 m high, stands 2 m from PR-7.
- **#7 (low):** 13 exchanger bundle-pull spaces are blocked and 31 valves are out of reach, with nothing tracking them.
- **#8 (low):** the four routes corrected by hand step up and down at rack junctions, leaving low and high points (e.g. PC-1136).

**Carried forward:** the high finding from the design review is still open: `lifting-study` and `tea` fail and the class 4 estimate is missing. Also carried: equipment weights for the high-pressure exchangers about ten times too low (I confirmed E-501 at about 140 t against 13 t listed, which affects the lifting study), X-601's spacing to area A-900, and the other earlier findings by reference.

Sources:
- [USGS MCS 2026 Nitrogen](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-nitrogen.pdf)
- [Statista NL non-household electricity](https://www.statista.com/statistics/596254/electricity-non-household-price-netherlands)

FINDINGS: critical=0 high=0 medium=6 low=2
VERDICT: fix
STATUS: DONE