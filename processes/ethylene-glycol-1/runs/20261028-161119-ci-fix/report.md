I fixed the CI failure and committed it. The review's findings had already been answered in earlier commits on this branch, and the re-runs confirm the critical and high fixes hold.

## CI failure (PR #212)
- **Cause:** both failed `library` jobs failed the same tooling test, `test_the_library_builds_strict_with_the_utilities`. The strict LCI build warned that this study's allocation method (`mass`) differs from the dataset's (`None`). `lca/lca.yaml` stated `method: mass`, but cheme never writes mass into `lca/dataset.yaml` because mass is the default.
- **Fix (08c2240):** I removed the explicit method from `lca/lca.yaml`, with a comment saying why, and regenerated the LCA outputs. The allocation is still mass, so no number changed.
- **Checked locally** with the CI's core version pinned: the full tooling suite passes (402 tests), and the strict LCI build gives no error or warning. The catalog build gives only "no preview rendered" warnings for the BFD and PFD, which CI allows. `cheme validate`: 0 errors, 0 warnings.

## Review 2026-10-28-pfd-lci-review
- **Closed (high): #1.** Commits f243f12, b00677a and 0e764e7 already did this. Re-checked: steam raised is now 66.3 MW (Q1+Q2+Q3), MP steam import is 3.95 GJ/t MEG, and every block and step balance closes.
- **Closed (medium/low): #2, #4, #5, #6, #7, #8**, in the same earlier commits.
  - #6 is closed as an accepted warning: the maturity claim still exceeds the evidence.
  - #7 is closed by a sensitivity only; the glycol bleed stream is still not modelled.
- **Partly open: #3 (medium).** A sensitivity is in D-005, but the EO-with-glycol relative rate is still unsourced. The LCA scenario would need a second flowsheet case, which isn't a quick change.
- PROGRESS.md already had a Response entry for each finding. I added the CI fix and the re-check results (160a5a6).

## Re-runs
- **`cheme check`:** all concept gates pass or are n/a.
  - `design-review` fails because the review is now out of date: the design changed after the reviewed commit. A new independent review is needed, and I can't write it myself.
  - The other basic and detail gates (P&IDs, layout, datasheets) fail as expected, since they are out of scope.
- **`cheme maturity`:** unchanged. Calculation maturity is none, with the accepted claim warning.
- **`cheme process streams`:** every balance ok.
- **`cheme assess lca --coverage`:** a partial screening carbon footprint with 12 declared gaps, publishable.

Everything is committed and nothing is pushed. A merge is pending: the branch needs a fresh independent review before a human merges it.

STATUS: DONE