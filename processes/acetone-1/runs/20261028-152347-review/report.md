I reviewed acetone-1 at commit `1d5bfda` and found nothing critical or high, so the branch can be merged. I committed the review record (`reviews/2026-10-28-pfd-lci-review.md`) as `b3190a3`; it is not pushed, and I changed no design files.

**What I re-ran myself**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme check`: all concept gates pass except the layout plot plan, which is out of scope. With the review committed, the `design-review` gate now passes as "agent-reviewed only".
- `cheme process streams`: every block and step balances within 1 kg/h. `propagate --check` shows nothing stale.
- `cheme maturity`: reaches no level, and warns that the `concept` claim in `process.yaml` is higher than the evidence supports.
- `cheme assess lca --coverage`: mass, element and carbon balances close. There are 13 gaps, each with a description of what should fill it.

**What checks out**
- **Route and boundary:** the cumene hydroperoxide route with the boundary issue #132 asks for. Every changed file is inside `processes/acetone-1/`.
- **Numbers recomputed by hand:**
  - air and spent air (5 mol% O₂, 1,240 Nm³ per tonne phenol)
  - fresh cumene, 1.33 t per tonne phenol
  - air compressor power, 2,716 kW
  - leftover cumene in the spent air, the hydrogen vent and the salt in the brine
  - the phenol balance and the steam duties
- **LCI:** the LCI is per kg acetone with mass allocation (acetone share 0.386) and matches the flowsheet. Inputs and outputs are both 2.0264 kg/kg. Nothing is zero-filled, there are no licensed values, and the per-process overrides are in `lca/mappings.yaml`.
- **Sources:** no third-party content is copied. I did not open the EU reference document (LVOC BREF) again, so its figures are not re-checked against the original.

**Findings (all open)**
- **R-01, medium:** the aqueous effluent is 64 kg per tonne phenol (0.039 kg per kg acetone in the LCI). That is 15–60 times below the 1–4 t/t water figure the design's own source register cites for that document, and `DESIGN.md` never reconciles the two. The effluent in the LCI is probably far too low.
- **R-02, low:** the `concept` maturity claim triggers the warning. It is the lowest value allowed and the notes explain it, but some feed compositions could already be given a source, which may help.
- **R-03, low:**
  - The oxidiser heat is calculated on a gas basis, probably about 30 % low, and the side reactions carry no heat.
  - The spent-air condenser duty (330 kW) looks low; my estimate is about 1 MW.
  - The reaction heats are labelled "given" although they are calculated.
  - The "independent" 2.7 % energy closure is mostly true by construction.
- **R-04, low:** acetone comes out at 0.627 t per tonne phenol, above the stoichiometric 0.617, because the model loses almost no acetone.
- **R-05, low:** the acid loading comes from a patent of which only the abstract was read; one handbook is cited second-hand; and two encyclopedia articles that were not read are listed as references.
- **R-06, low:** the excluded emissions (vacuum vents, off-gas methane, leaks) have no amounts, so the 1 % cut-off rule cannot be checked; the cited ranges would bound them. The LCI dataset also lacks a product classification code, and the N₂ and O₂ emissions have no compartment.

The merge is pending: a human or the reviewer has to merge `case/acetone-1`.

VERDICT: merge