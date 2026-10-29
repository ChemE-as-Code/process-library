I fixed the CI failure on PR #218 and committed everything; nothing is pushed. The review's two high findings were already closed by an earlier commit, and I confirmed they still hold.

**Why CI failed:** both `library` jobs failed on one library test, `test_the_library_builds_strict_with_the_utilities`. The strict LCI build warned that this study allocates by `mass` but `lca/dataset.yaml` has no allocation method. The cause is in cheme itself: `mass` is the default, and cheme leaves default values out when it writes `dataset.yaml`. Glycerol is the only process in the library that uses `mass`, so only it hit this.

**What I changed (18e3250):** in `lca/lca.yaml` the baseline allocation is now `shares`. This treats the recovered methanol as a return to the biodiesel plant with a share of 0, and splits the burden by mass between glycerol (0.873) and the fatty layer (0.127). It is the treatment the review recommended under #5 and that decision D-013 already named as preferred. Plain `mass` (glycerol 0.594) and `none` are still reported alongside, so no variant is lost.

This is a method change, not only a fix: once backgrounds are linked, the glycerol baseline carries 87 % of the burden instead of 59 %. Right now every contribution is still a gap, so no result changes. I regenerated the LCA outputs and recorded the reason in D-013.

**Checks:**
- I reproduced the CI's strict build locally with the same core version: no warnings or errors, and `tests/test_utilities.py` passes (33 tests).
- `cheme validate`: 0 errors, 0 warnings.
- `cheme process streams`: every block and step balance closes.
- `cheme assess lca --coverage`: a partial screening carbon footprint with 15 declared gaps; mass, element and carbon-origin balances close.
- `cheme maturity`: calculation maturity none, with the same warning that the claimed maturity exceeds the evidence, already explained in `process.yaml`.
- `cheme check`: the concept gates pass except the plot plan; the P&ID, layout, datasheet and detail gates fail as expected at this stage. `design-review` now fails because the files changed since the review, so a new independent review is needed. I did not write it myself.

**Findings closed:** #1 and #2 (high) were closed in c0f8d04 and are still in place. #5 (medium) gets a follow-up in 18e3250. #3, #4, #6, #8 and #11 were closed earlier. PROGRESS entries are in c1da69a.

**Findings left open (all low):**
- **#7:** needs a re-read of the Thompson & He PDF to see which feed quantity they measured, which I can't do in this session.
- **#9:** needs a vent design for E-302 to give an assumed methanol vent loss. None of cheme's exclusion types fits, and I won't invent a number.
- **#10:** a bug in the `cheme` tool, outside this folder.

The branch has no stage sign-off; a merge is pending a new independent review and a human merge.

STATUS: DONE