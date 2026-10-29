I fixed the CI failure on PR #226, and the review's only high finding (#1) was already closed before this session. Everything is committed (`4fd6cf7`, `5527e9a`) and not pushed. A merge is pending: the branch still needs a fresh independent review.

**CI failure.** Both failing `library` jobs came from the same two library tests. The library's LCI export refused `lca/dataset.yaml` for two reasons:
- **Allocation:** it cannot export `substitution` as one activity per co-product.
- **System model:** `substitution` doesn't fit the build, which expects `cutoff`.

What I changed:
- **Allocation** in `lca/lca.yaml` is now fixed shares: the pulp carries 100 % of the burdens and the exported electricity 0 %, with neither a burden nor a credit. The reason for leaving the library's default method is written in the file, the same way `sulfuric-acid-1` does it. The pulp has no energy content or exergy yet, the electricity isn't counted in kg, and substitution can't be exported.
- **System model** is now `cutoff`.
- **Outputs:** DESIGN.md D-014 is updated and the LCA outputs were regenerated with `cheme assess lca --write`. The climate result is unchanged at 0.0823 kg CO2-eq/kg pulp. The gap for the not-yet-linked electricity credit is gone, so there are now 13 gaps.
- **Tests:** I ran the full library test suite locally with the CI command: 407 passed. `cheme validate` reports 0 errors and 0 warnings.

**Review findings (`reviews/2026-10-28-pfd-lci-review.md`)**
- **Closed:**
  - **#1 (high):** closed in the earlier commit `b356adc`. I re-checked it after my change: fossil CO2 is still 0.0823 kg/kg and the caveat is still in `lca/README.md`. I added a PROGRESS.md entry recording the re-check.
  - **#2–#3 (medium) and #4–#9 (low):** all closed in `b356adc`, each with a Response entry in PROGRESS.md. There were no critical findings.
- **Left open:**
  - **#10 (low):** pinning a tidier PFD layout is deferred to the basic stage, as the review itself proposes.
  - **#11 (low):** the reviewer already marked it accepted; it needs no action.

The review record still shows every finding as `open`, because I may not edit review records.

**Checks re-run**
- **`cheme check`:** all concept gates pass. `design-review` now fails because the scope changed since the reviewed commit, so a new independent review is needed. The layout and P&ID gates fail, as expected at concept stage.
- **`cheme maturity`:** calculation maturity is none, and the `concept` claim is flagged as exceeding the evidence. Both were already true and are explained in `validation.notes`.
- **`cheme process streams`:** every block and step balances.
- **`cheme assess lca --coverage`:** partial screening carbon footprint, publishable. Mass, element and carbon-origin balances close; the 20.7 % energy-closure figure is explained in D-014 as not applying.

STATUS: DONE