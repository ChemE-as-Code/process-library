I fixed the CI failure and closed six of the eight review findings; the other two are partly closed. The review had no critical or high findings: R-01 was medium and R-02 to R-08 low. Everything is committed in three commits on `case/thionyl-chloride-1`, not pushed, and nothing outside `processes/thionyl-chloride-1/` was touched.

**CI fix (41e6e8d).** In PR #234 the `library` job failed two tests (`test_jsonld_identifiers`, `test_the_library_builds_strict_with_the_utilities`). The LP steam input is counted in kWh, but the build linked it to the shared `steam` entry, which is per kg. `lca/mappings.yaml` now points it at the shared `steam-heat` entry, as acetone-1 does. I re-ran both tests locally with CI's dependency set and both pass.

**Findings closed**
- **R-01 (medium):** the degasser T-201 bottoms temperature is now calculated as the bubble point of the degassed crude at 125 kPa(a), 350.12 K, instead of a fixed 345 K.
  - Q9 (degasser reboiler) goes from 464.85 to 471.01 kW; Q13 (column reboiler) from 684.47 to 678.05 kW. Mass flows are unchanged.
  - The S22/S30 temperatures, the equipment list and D-007 are updated, the BFD/PFD rebuilt and the LCI rewritten. LP steam stays at about 0.422 kWh per kg.
- **R-02:** the correct plant balance (3778.01 kg/h in against 3778.00 out) is recorded in PROGRESS.md; the run record is untouched.
- **R-03:** the 95 % S2Cl2-to-SCl2 conversion in R-201 was a bare number in the flowsheet, and the schema gives no way to attach a source there. It is now its own reaction, `SCL2_FORM_R201`, in `process/reactions.yaml`, marked ASSUMED with source D-005. D-005 now states the effective per-pass SCl2 conversion; I checked it at 67.9 %.
- **R-04:** the process.yaml notes now name the `cheme.maturity-claim-exceeds` warning and say `concept` is just the lowest value the schema allows.
- **R-05:** D-004 notes that oxygen is carried dissolved in the chlorinator liquids, and that the chlorinators need an off-gas vent when the P&IDs are drawn.
- **R-06:** D-010 and Open inputs list three heat-integration options (degasser feed/bottoms exchanger, SO2 vaporiser off steam, reactor heat to LP steam). No LCI scenario was added.

**Partly closed**
- **R-07:** the Ullmann wording now says "not read". The finer patent locators are still open because I did not re-read the patents. Reading the full text of SRC-4 and SRC-5 is listed as an open input.
- **R-08:** I added CPC code 34231. Only a third-party crosswalk supports it, so it is marked to be checked against the UNSD table. The O2 and H2O emissions still have no compartment: the schema rejects one on these zero-burden flows. Giving Cl2 and the sulfur chlorides a flow identity waits for the shared-files PR (D-013).

**Re-runs**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme check`: all concept gates pass except `layout-plot-plan` (out of scope). `design-review` now fails because the files the review covered have changed, so a fresh review is needed.
- `cheme maturity`: still reaches no level, as before (assumed feeds, unsourced conversions).
- `cheme process streams`: all blocks and steps balance.
- `cheme assess lca --coverage`: balances closed, still 15 gaps and no climate total; the CPC info is gone.

The CI fix is checked locally only, since nothing is pushed. Merge pending: a new independent review is needed, then a human or the reviewer merges.

Sources for the CPC lookup: [worldoftaxonomy HS 281212](https://worldoftaxonomy.com/codes/hs_2022/281212), [seair HS heading 2812](https://www.seair.co.in/hs-codes/heading-2812-halides-halide-oxides-non-metals.aspx)

STATUS: DONE