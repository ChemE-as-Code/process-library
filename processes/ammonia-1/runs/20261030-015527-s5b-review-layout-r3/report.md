My verdict on S5b (PR #257), round 3, is **fix**. The review record is `reviews/2026-10-30-layout-s5b-r3.md`, reviewed at 498efa2, committed as 50aa305 and pushed. The verdict is also posted as a PR comment. I did not merge: the section ends with a stage sign-off, and the verdict is fix anyway, so the merge is still pending.

**Checks I re-ran myself**
- `cheme validate`: 0 errors, 202 warnings.
- `cheme layout build --check`, `cheme assess mto --check` and `cheme assess estimate --check`: all up to date.
- `cheme check --stage basic` still fails two gates:
  - **lifting-study:** 8 blocked lanes, none accepted.
  - **maturity-balanced:** the feed flows and compositions have no source, and the H-101 fuel burnout values (H2_COMB, NH3_COMB) are still assumed.
- Every other basic gate passes. The layout-review gate now passes because of this record.
- No gate was relaxed and nothing was accepted.

**Last round's three layout findings are closed:**
- DW-1073 no longer crosses crane pad CP-203. Its run west to V-302 is now raised to 8.0 m, over the access from the north road (R-2).
- Five crane pads were moved and one added (CP-213). My own check confirms none of them is under a pipe.
- The proposed E-504 move was tried, and the proposal now says why it was dropped.

**New findings**
- **Medium (r3#1):** two more lanes are blocked in substance, so the real count is 10, not 8.
  - The E-301 and V-701 lanes show as clear only because the blocking pipe (AM-1059, AG-1121) lies over the crane pad itself, which the tool's lifting check does not look at.
  - When I moved CP-211 off the pipe, the same tool reported AM-1059 as blocking the E-301 lane.
  - Every pipe-free pad position I tried around V-701 is blocked by AL-1128.
  - DESIGN.md (D-033) admits these two pads are "not yet shown to be workable". But the proposal for the owner counts both lanes as cleared and leaves them out of its list.
- **Low (r3#2):** that proposal still says no crane chart may be used for licence reasons. D-033 withdrew that reason last round.
- **Low (r3#3):** the DW-1073 re-route drops from 8 m to grade and back, leaving a low point with no drain and two unsupported 7.4 m vertical runs. Its grade section also runs 1 m from X-401's east face.

**Source spot-checks**
- **EP 1586535 A2:** the applicant, date and statement match. The patent page shows no paragraph numbers, so "[0003]" is unverified.
- **Al-Dhfeery & Jassem (2012):** page 2 and Table 2 match the citation. In the paper, complete oxygen use in the combustion zone is a model assumption backed by a comparison with plant data, not a measurement. I noted this in the record without making it a finding.

The high finding 2026-10-29-design#1 stays open. As the design review says, closing it now mostly needs the owner: accepting the lifting lanes, a feed specification and real unit rates. A published source for hydrogen burnout in a fired heater has also still not been found.

FINDINGS: critical=0 high=0 medium=1 low=2
VERDICT: fix
STATUS: DONE