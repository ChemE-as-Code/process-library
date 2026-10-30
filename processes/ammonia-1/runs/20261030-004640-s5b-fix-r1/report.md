I closed the five quick review findings. The high finding `2026-10-29-design#1` stays open, and both basic gates you named still fail: `lifting-study` and `maturity-balanced`.

**Closed (commits 0dc4ea6, 762a248)**
- **layout-s5b#1:** I re-routed the two small lines blocking lanes and added three crane pads. AL-1129 now leaves the pipe rack east of V-701 and drops to its tee at grade, with pad CP-703 south of the drum. DW-1073 now goes east of X-401 and reaches V-302 from the north, with pads CP-211 (for E-301) and CP-212 (for E-303). Blocked lanes went from 11 to 8, and the layout build reports no clash or headroom problem.
- **layout-s5b#2:** laydown LD-204 moved off access road R-5.
- **design-s5b#1:** the H2 and NH3 burnout conversions of the reformer furnace H-101 are back to `assumed`, with the reasoning written out; the values are unchanged.
- **design-s5b#3:** the pad search script is now in `scripts/pad_search.py`, referenced from D-033.
- **design-s5b#4:** the PROGRESS row now says the E-504 move was tried and reverted.

**Partly done**
- **Estimate (design#1 c, commit 222de79, D-035):** I used a published cost index, CEPCI 2023 = 797.9, which I checked in [Chemical Engineering, Sept 2024, p. 45](https://www.chemengonline.com/wp-content/uploads/2024/08/19_CHE_0924_EconInd_p45.pdf). I generated draft datasheets for all 52 items to get the sizes. Only 14 items have a purchased cost (none with installation factors), and 38 are not covered:
  - exchangers have no area yet;
  - no materials are chosen;
  - K-101, K-501, C-301 and C-302 are outside the cost correlations' ranges.

  So I declared it **class 5, not the class 4 you asked for**. `estimate/rates.yaml` is still the example: I found no published bulk rates we're allowed to publish (the usual databases are licensed). So there is no bulk estimate, and the TEA is unchanged.
- **design-s5b#2 (steam-package jump):** the script just adds four simulated boiler duties, mapped correctly, so the jump came from the simulation itself. Finding which boiler moved means rerunning the published-gas feed case, which belongs with the feed decision below.
- **design-s5b#5:** I can't edit the PR. `build/pr-body.md` is updated; apply it with `gh pr edit 257 --body-file build/pr-body.md`.

**Checks**
- `cheme validate`: 0 errors, 203 warnings (12 new ones come from the draft datasheets).
- `cheme check --stage basic`: everything passes except:
  - **lifting-study:** 8 lanes left (H-101, E-104, E-402, K-501, E-501, E-502, E-505, E-504). Each is blocked by the item's own or its neighbour's piping, a pipe-rack bent, or H-101's own tubes, so only an erection-sequence decision clears them. They're listed for the owner in `build/lifting-acceptance-proposal.md`, and none is accepted. There's also no crane chart: a manufacturer's load chart can't be copied into the library, so it has to come from the crane contractor.
  - **maturity-balanced:** the natural-gas, air and water feed rates are outputs of this design, so no published source gives them; they need the owner's specification. Separately, the model-basis check now fails on H-101 because of the relabelling. Closing it needs a published source for H2 and NH3 burnout in an excess-air furnace, which I didn't find.
  - **design-review, layout-review:** outdated by this round; the S5r reviews come next.
- `cheme maturity`: none. Layout model, lifting study, take-off and equipment cost are all current.

All work is committed, and the PR comment is in `build/pr-comment.md`. Merge pending: nothing is merged or signed off.

STATUS: BLOCKED: lifting-study has 8 lanes only an owner's erection-sequence decision can clear; maturity-balanced needs the owner's specification of the natural-gas, air and water feed rates, plus a published source for H-101's H2/NH3 burnout; the class 4 estimate needs sourced bulk rates and S7 sizes and materials.