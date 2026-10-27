I've reviewed the nitric acid case at `9a12e03` and committed the record as `25068a7` (`reviews/2026-10-27-pfd-lci-review.md`). It has 6 findings, 3 medium and 3 low, with no critical or high. Nothing was pushed, and the merge is still pending a human or reviewer.

**What I re-ran myself:**
- **`cheme validate`:** 0 errors and 0 warnings, including after adding the review record.
- **`cheme check`:** the six in-scope concept gates pass. The layout, P&ID and datasheet gates fail, which is expected because those are out of scope for this stage.
- **`cheme maturity`:** level none, as the design files themselves say.
- **`cheme process streams` and `propagate --check`:** every block and all 21 steps close.
- **The balance script (`scripts/hno3_balance.py`):** it reproduces exactly what DESIGN.md claims. Mass in equals mass out, the nitrogen balance closes, and energy closes to within 6.7 kW of 62 MW (the 6.7 kW is the pump work).
- **`cheme assess lca --coverage`:** a partial screening carbon footprint with 10 gaps. Inputs and outputs are both 5.7426 kg per kg of contained acid.

**Plausibility:** I checked the key numbers by hand and they hold up:
- 0.285 t of ammonia per t of acid, with 94.7 % of the ammonia nitrogen ending up as acid.
- Gauze outlet at 1144 K and 3 % oxygen in the tail gas.
- Machine powers, exchanger approaches, 38 t/h of exported steam and 46.7 MW to cooling water.
- The two IPCC 2006 N2O defaults are used correctly: 7 kg/t formed and 2.5 kg/t emitted with abatement.

Every unsourced value is marked ASSUMED. I found no copied third-party content and no licensed or zero-filled background data, and nothing outside `processes/nitric-acid-1/` changed.

**Findings:**
- **R-01, medium:** platinum/rhodium gauze loss and the gauze, N2O and SCR catalyst consumption are missing from the LCI files. They appear only in DESIGN.md, so `gaps.csv` doesn't list them.
- **R-02, medium:** the LCI files say "cradle-to-gate" while DESIGN.md says "gate-to-gate". As a result the catalogue would show 0.68 kg CO2-eq/kg, which is only the direct N2O emission, under a cradle-to-gate label.
- **R-03, medium:** the generated PFD reads backwards. The oxidation section sits at the far right and long return lines cross most of the sheet.
- **R-04, low:** `cheme maturity` reports the weak-acid separator as "predictive, sourced", although its outlets come from the script. This is a fault in the tool and should be reported to cheme-as-code.
- **R-05, low:** `process.yaml` claims maturity "concept" while the tool says none. "concept" is the lowest value the schema allows and the gap is disclosed, so it isn't misleading.
- **R-06, low:** the unabated comparison exists only as text in DESIGN.md, not as an LCI scenario.

You asked for ids R-01 and so on, but `reviews/README.md` requires `2026-10-27-pfd-lci-review#n`, and `cheme validate` rejects other formats. So the table uses those ids, with R-01 to R-06 in brackets at the start of each finding.

I did not open the EU BREF or check the IPCC page number, and I did not render the BFD.

VERDICT: merge
