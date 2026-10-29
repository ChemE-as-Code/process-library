The library test now passes. I committed the fix as `c71e354` on `case/hydrazine-1` and did not push.

**The cause wasn't the allocation.** After merging `origin/main`, the test failed on a different warning from the ethylene one:

> `hydrazine-1: feed:N2F: several Atlas producers: market:nitrogen/gan-8barg-10ppm:RER is used, and does not take asu-1: Cryogenic air separation unit … link one explicitly (link.dataset) to choose`

`process.yaml` listed the nitrogen feed `feed:N2F` as plain `nitrogen`, with no grade. ASU-1 makes two nitrogen products: gaseous pipeline nitrogen (GANP) and liquid nitrogen (LIN). Both were therefore possible sources. The build picked the gaseous-nitrogen market, and the liquid-nitrogen plant outside that market caused the warning.

**Fix (in `process.yaml` only):** the feed now names its grade, `nitrogen/gan-8barg-10ppm`. That matches D-015, which already says the nitrogen comes from site supply or a pipeline. The build now rejects liquid nitrogen as the wrong grade and links the gaseous-nitrogen market without a warning. No balance, amount or dataset changed. I also added a line to `PROGRESS.md`.

**Checks:**
- `tests/test_utilities.py`: 33 passed (it failed 1 of 33 before the fix).
- The full library test suite: 434 passed.
- `cheme validate`: 0 errors, 0 warnings. One info note remains: `checks.yaml` cites D-023, which has no entry in `DESIGN.md`. I didn't touch it.
- The pre-commit hook passed.

The commit message is the one you specified, "consistent LCA allocation", although the change actually names the nitrogen grade. A merge is still pending: the branch needs review and merging by someone other than me.

STATUS: DONE