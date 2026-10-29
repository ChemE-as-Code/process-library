I've reviewed the acetaldehyde case at commit a5a06fd and committed the record as 0858ca9 (`reviews/2026-10-28-pfd-lci-review.md`). It has 12 findings: 3 medium, 9 low, no critical or high. I changed no design files and pushed nothing.

**What I re-ran**
- **Validate:** 0 errors, 0 warnings.
- **`cheme check`:** every concept gate passes except the plot plan, and layout is out of scope. The `design-review` gate now passes with this record.
- **`cheme maturity`:** reaches none, below the concept level `process.yaml` claims. DESIGN.md admits this, but `process.yaml` itself does not (R-08).
- **Balances:** every block and step closes, and propagate reports nothing stale. My own checks of chlorine, unconverted ethylene and yield (94.1 mol%) agree.
- **LCI:** inputs 9.7941 kg = outputs 9.7942 kg per kg product. All 13 background datasets are listed as gaps, each with a description. No zero-filled or licensed values, and the overrides are in this folder's `lca/mappings.yaml`.
- **Plausibility:** ethylene 0.677 kg/kg, oxygen 0.410 kg/kg, steam 1.42 t/t and waste water 8.7 m³/t. The scaled patent rates and the reaction and compressor energies all check out.
- **Scope:** against the branch point, nothing outside `processes/acetaldehyde-1/` changed. `main` has moved on since then, so the branch needs merging or rebasing onto current `main` before it goes in.

**Medium findings**
- **R-01:** the first distillation column's bottoms are set at 393.4 K, the boiling point of pure water at 200 kPa(a). But that liquid holds 11.6 wt% acetaldehyde, so its real bubble point is around 360 K (my own estimate; no property package covers this mixture). The error moves about 4.3 MW of cooling from the second column's condenser to the first. DESIGN.md's reflux ratio of about 2.5 would fall to about 0.4. Total cooling water, and so the LCI, barely changes.
- **R-02:** palladium and copper catalyst make-up appears nowhere in `lca/`, `gaps.csv` or `process.yaml`. DESIGN.md says it is "not set to zero", but in practice the inventory carries it as zero.
- **R-03:** the selectivities behind ethylene use, the largest LCI exchange, come from Wikipedia's summary of Ullmann's, which was not read. The issue asks for the source to be checked before its numbers are used. A cross-check against the patent agrees within 2%.

**Low findings**
- **R-04:** "0.8 CO2" in the source may mean mol CO2, not mol ethylene burnt; the second reading halves CO2 formation.
- **R-05:** two design pressures sit below DESIGN.md's own rule.
- **R-06:** pressure rises across the product cooler with no pump step.
- **R-07:** the claim that 8 mol% O2 is below the limiting oxygen concentration has no source.
- **R-08:** `process.yaml` doesn't say that `cheme maturity` reaches none.
- **R-09:** `process.yaml` lists the purge as a CO2 emission, while the LCI treats it as waste to treatment.
- **R-10:** the patent citations give no column or line numbers.
- **R-11:** the LCA manifest prints "energy closure 0.0%" with no explanation.
- **R-12:** a template comment in `checks/checks.yaml` cites decision D-023, which doesn't exist.

A merge is pending: a human or the reviewer should merge after the rebase onto current `main`.

VERDICT: merge