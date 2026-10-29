I fixed the CI failure and closed six of the eight review findings. The review (`reviews/2026-10-28-pfd-lci-review.md`) had no critical or high findings, so all of this was medium and low work. Everything is committed in four commits on `case/hydrogen-bromide-1`, all inside `processes/hydrogen-bromide-1/`. Nothing is pushed.

**CI (PR #229).** The `library` job's tooling tests rejected the LCI dataset for two reasons:
- **Steam unit:** the LP steam feed (`feed:LPS`) fell back to the library's steam entry, which counts kg, while the exchange is in kWh. `lca/mappings.yaml` now maps it to the kWh steam-heat entry.
- **Bromine to air:** Br2 was declared a burden-free emission, which the shared library mappings don't allow. It is now an emission to air with its own entry, which also closes review finding #3.

The two tests that failed now pass, and the full `tests/` suite passes locally in the CI environment (412 passed). CI itself has not been re-run because nothing is pushed.

**Findings closed** (each has a Response entry in PROGRESS.md with its commit):
- **#2 (medium), 77e5b89:** the activated carbon of the finishing bed R-102 was left out with no amount. The fresh carbon and the spent carbon are now cut-off flows of 130 kg/a each. That figure is assumed from a bed volume at an assumed gas space velocity and one change a year, and recorded in a new decision D-013. At 0.0008 % of the input mass, the 1 % cut-off rule now actually checks it.
- **#3 (low), be4b902:** see the bromine-to-air fix above.
- **#4 (low), 9eebaf5:** decision D-008 now says the scrubber sits above the absorber, so weak acid flows down by gravity through about 2 m of liquid head (assumed). A pump was considered and rejected.
- **#5 (low), 77e5b89:** the heat-of-reaction unit is corrected to kJ per mol (MJ per kmol).
- **#6 (low), 9eebaf5:** the steam-table source now cites the standard's equations, with values I recomputed with CoolProp. This corrected the LP steam saturation temperature from 420.8 K to 421.1 K, and I rebuilt the PFD. The Hydrogen bromide Wikipedia page and the steam standard are now separate references in `process.yaml`.
- **#7 (low), 9eebaf5:** the equipment list now says R-101's 300 °C design temperature covers only the chamber shell and jacket. The burner tube's design temperature is left to be set at the datasheet stage.

**Findings left open:**
- **#1 (medium):** the heat of solution behind the absorber cooling duty (57 % of the cooling) still needs to be read from the NBS tables. That is not a quick fix: once read, the absorber duty and the LCI have to be recalculated.
- **#8 (low):** kept on purpose. The reviewer asked to keep the disclosure that `cheme maturity` reaches no level until the feeds and absorber recoveries have sources.

**Checks after the changes:**
- **`cheme validate`:** 0 errors, 0 warnings.
- **`cheme process streams`:** every block and step balances, with the same reaction extents as before.
- **`cheme assess lca --coverage`:** still a partial screening carbon footprint. It now shows 9 gaps instead of 8, because Br2 to air (0 kg) is counted as one. Mass and element balances close and the dataset is publishable.
- **`cheme maturity`:** unchanged: calculation maturity none, with the over-claim warning that #8 covers.
- **`cheme check`:** the concept gates pass except the layout plot plan, which is out of scope. The `design-review` gate now fails because files changed after the reviewed commit. It needs a new independent review; I can't write that myself.

Merge is pending: it needs a fresh independent review of these commits, then a human merge.

STATUS: DONE