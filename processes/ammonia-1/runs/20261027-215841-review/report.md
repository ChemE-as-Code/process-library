I reviewed the ammonia case at `ab23125` and found nothing critical or high: three medium and two low findings. The record is `reviews/2026-10-27-pfd-lci-review.md`, committed as `c755492` on `case/ammonia-1`; nothing is pushed and the merge is pending.

**Re-runs (my own, not the run report's):**
- **`cheme validate`:** 0 errors, 0 warnings.
- **`cheme check`:** every concept gate passes except the plot plan. The P&ID, layout, take-off and datasheet gates fail, but those are outside this stage's scope. The `design-review` gate now passes with this record.
- **`cheme maturity`:** level none.
- **`cheme process streams`:** all 7 blocks and 51 steps balance; the largest gap is 2.4 kg/h, which DESIGN.md explains.
- **`cheme process propagate --check`:** no deviations.
- **`cheme assess lca --coverage`:** mass, element and carbon balances closed; 11 gaps, each described.
- **Scope:** only files inside `processes/ammonia-1/` changed. The route and boundary match option A of issue #86.

**Plausibility, from my own hand estimates:**
- The carbon closes: 0.603 kg of the assumed gas gives 1.561 kg CO2 per kg NH3, against 1.563 kg in the inventory.
- Gas use is about 27.8 GJ/t NH3 on a lower-heating-value basis, plus 2.0 GJ/t electricity and 0.88 t/t of exported steam. That is plausible for a conventional plant with electric drives.
- The process-air and synthesis-gas compressor powers, the process steam rate and the converter, purge and methane-slip figures all match my estimates.
- I found no copied third-party content, no licensed background values, and every key value is either sourced or marked ASSUMED.

**Findings** (record ids `2026-10-27-pfd-lci-review#1` to `#5`):
- **R-01 (medium):** DESIGN.md D-020 says no impact result is claimed. But the generated `lca/results.md` reports 1.563 kg CO2-eq per kg NH3 as a "partial screening carbon footprint". That number is only the plant's direct CO2. It leaves out the gas supply chain, the electricity and the steam credit, so it is not a footprint of the product.
- **R-02 (medium):** Six air emissions (methane, CO, hydrogen, ammonia, ethane, propane) sit in the inventory at 0 kg because of modelling choices, such as complete combustion and no gas carried out with the CO2 vent. Methane is even scored as 0 kg CO2-eq instead of being listed as a gap. The furnace (H-101) has no declared emission estimates or exclusions. The run report's line "nothing is set to zero" is therefore wrong.
- **R-03 (medium):** The natural-gas composition is an assumed benchmark gas. The issue's brief asks for one given with a source. The design says so openly, but the feed drives every LCI figure and blocks every maturity level.
- **R-04 (low):** `process.yaml` claims `maturity: concept` without saying that `cheme maturity` finds no level. Concept is the lowest value the schema allows, so a one-sentence note is enough.
- **R-05 (low):** In the stream table, the reaction extents reported for the reforming block are not the sum of its steps. For example, it shows 0 for methane combustion although the furnace inside it burns 495.9 kmol/h. The balances still close; this is a reporting issue in the `cheme` tool (core) itself, to report there.

**Not checked:** the rendered BFD/PFD drawings, the balance script's code and its energy closure, and a one-by-one comparison of the equipment list with the PFD.

VERDICT: merge
