I fixed the CI failure and responded to the review in two commits on `case/urea-1`. Nothing is pushed, and every change is inside `processes/urea-1/`.

**CI failure (PR #193, `library` job).** The strict LCI build and two library tests stopped on five exchanges in `lca/dataset.yaml` that have no link in `lci/mappings.yaml`: ammonia, CO2, MP steam (counted in kg in the mappings, kWh here), biuret and urea dust. Those links belong in `lci/mappings.yaml`, which is outside this folder. So I stopped committing `lca/dataset.yaml`: it is removed from git and listed in the folder's `.gitignore`, with the reason recorded as new decision D-013 in DESIGN.md. The inventory, gaps and results files are still committed.
- On a clean copy of the commit, the strict LCI build exits 0 and `tests/test_export_formats.py` plus `tests/test_utilities.py` pass (41 tests).
- **Trade-off:** urea-1 is out of the library's LCI database build until someone adds those mappings in a library PR and removes the `.gitignore` line. If you'd rather have the mappings now, that's your call.

**Review findings.** The review had no critical or high findings. I responded to all eight smaller ones, each with a Response entry in PROGRESS.md citing commit `8d94172`:
- **Closed: R-01, R-02, R-03, R-04, R-06, R-07, R-08.**
  - R-01: corrected the E-102 energy text; the 10–24 MW of unassigned heat is now an open energy item.
  - R-02: the power and cooling-water figures in the LCI are marked as known underestimates.
  - R-03: named the hydrogen/oxygen vent explosion hazard and added open input O-8 for basic engineering and the HAZOP.
  - R-04: corrected the fugitive-ammonia figure to 0.27 g/kg and gave its amount.
  - R-06: the CO2 feed is described as feed gas (98.5 mol%).
  - R-07: Ullmann removed from the reaction sources until it has been read.
  - R-08: the manifest says that `cheme maturity` reaches no level.
- **Partly open: R-05.** I corrected the prilling-exhaust comparison with the BREF figure: our flow is 1.6–1.8 times it, not "the same order". Still open (now listed under O-5): the scrubbed exhaust temperature doesn't match the assumed scrubber evaporation, and fixing it means changing and re-running the balance script.
- **Small leftover from R-04:** an info message asking for the cut-off amount in kg still appears, because the schema has no amount field for emission exclusions.

**Commands after the changes:**
- **`cheme validate`:** 0 errors and 1 known warning (S11 compositions sum to 0.999999).
- **`cheme process streams`:** every block and step balances.
- **`cheme assess lca --coverage`:** a partial screening carbon footprint with 7 declared gaps; mass, element and carbon balances close.
- **`cheme maturity`:** level none, as before.
- **`cheme check`:** 11 gates pass. The `design-review` gate now fails because the review covered files I changed, so it is no longer current. A fresh independent review is needed. The other failing gates (P&IDs, layout, datasheets) are outside the concept stage, as before.

**Merge:** pending. The branch needs that re-review and a human or the reviewer to merge it, not me.
