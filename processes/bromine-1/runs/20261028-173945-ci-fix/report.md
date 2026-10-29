I fixed the cause of the CI failure, closed four review findings (R-01, R-02, R-03, R-05) and left two low ones open (R-04, R-06). The review had no critical or high findings. Everything is committed on `case/bromine-1` in five commits, nothing is pushed, and nothing outside `processes/bromine-1/` changed.

**CI failure (PR #232, `library` job, `test_the_library_builds_strict_with_the_utilities`):** the library's LCI build linked bromine-1's live LP steam (`feed:LPS`) to three Atlas steam producers and warned, and the strict test fails on any warning. None of the three makes LP steam, and the site boiler isn't chosen yet. `lca/mappings.yaml` now marks `feed:LPS` `atlas: false` and says why (commit 8971013). I re-ran that test locally and it no longer reports anything for bromine-1. It still fails locally on other warnings, because my environment lacks an optional unit-conversion extra of the core package that CI installs, so the full test is only proven once CI re-runs.

**Findings closed** (each has a Response entry in PROGRESS.md):
- **R-01 (medium), the tail-brine temperature drop with no basis.** The neutraliser T-107 is now a closed tank at 120 kPa(a), above the brine's boiling pressure, so the brine doesn't flash and no vapour goes missing. `scripts/balance.py` now calculates the outlet stream S17: the lime neutralisation releases 225 kW net and warms the brine by 0.30 K. S17 is now 382.89 K, replacing the 375 K that had no source. Recorded in D-009 (commit f8e4bda).
- **R-02 (medium), the missing tail-brine transfer pump.** S17 now leaves at the tank's 120 kPa(a) instead of 300 kPa(a). Of the two options the review offered, I took the boundary one rather than adding the pump: the pump that lifts the brine to the injection header now counts as part of the reinjection system outside the boundary. D-001, D-009 and D-011 say so, and D-011 states the effect: with the pump (about 50–60 kW) the plant's electricity would be about 0.047 instead of 0.0322 kWh/kg. The equipment list and the reinjection gap text in `lca/lca.yaml` match (commit f8e4bda).
- **R-03 (medium), the maturity claim.** The published notes in `process.yaml` now say the calculation maturity is none and that the concept claim exceeds the evidence. DESIGN.md is corrected and lists a maturity level below concept as a library request (commit 9740287).
- **R-05 (low), how close the brine basis is to the edge.** D-004 now gives the derived sodium (85.5 g/kg) and says the basis brine may be near halite (salt) saturation. D-006 gives the steam sensitivity to the assumed brine heat capacity: 0.21 kg steam per kg Br2 for each 0.1 kJ/kg K (commit 4c4fa45).

**Findings left open:**
- **R-04 (low):** the formation enthalpies behind the heats of reaction need re-reading against the source with table and entry locators. I had no copy of the source, and a locator given without re-reading it would be invented.
- **R-06 (low):** amounts for the emission exclusions need the vent scrubber and P&ID design, so any number now would be a guess. The bromine resource exchange waits for a brine-extraction background dataset.

**Checks after the changes:**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme check`: all concept gates pass except `layout-plot-plan`, as before (no layout yet). The `design-review` gate now fails because the reviewed files changed since the review; this is expected and needs a new review.
- `cheme maturity`: calculation maturity none, with the over-claim warning now also stated in the published notes.
- `cheme process streams`: every block and step balances; S17 shows 382.89 K and 120 kPa(a).
- `cheme assess lca --coverage`: partial screening result with 10 gaps, publishable; mass and element balances closed. The LCI outputs are current.

Merge pending: the branch needs a new independent review, then a push and a human merge.

STATUS: DONE