I reviewed `case/isobutene-1` at 04ddb0e and found no critical or high problems: the concept PFD and the preliminary LCI hold up. There are 7 low findings. The record is `reviews/2026-10-28-pfd-lci-review.md`, committed as f7520ee and not pushed. I changed no design files.

**What I re-ran myself:**
- **`cheme validate`:** 0 errors and 0 warnings, including after adding the review record.
- **`cheme process streams`:** every block and step balances. `propagate --check` reports no deviations.
- **`cheme assess lca --coverage`:** mass, element and carbon balances close. There are 8 gaps, each with a description.
- **`cheme check`:** every concept gate passes except the plot plan. The P&ID, layout, datasheet and design-review gates fail, which is expected because they were out of this run's scope.
- **`cheme maturity`:** reaches no level and warns that `process.yaml` claims more than the evidence supports. `concept` is already the lowest level the schema allows, and the notes in `process.yaml` say this openly.

**Numbers checked independently:**
- The heat of reaction (+65.4 kJ/mol), the equilibrium constant, the equilibrium conversion (about 0.996 for pure MTBE at 7.5 bar) and the reactor duty (about 1970 kW) all agree with the design.
- The 99.0 mol% isobutene yield, the water balance and the methanol balance close when I trace the losses by hand.
- My hand estimates of the column and exchanger duties agree with the design's within about 10%.
- The LCI's mass-allocation share (63.1%), the 1.0004 kg MTBE per kg isobutene and the plant mass balance (9960.29 kg/h in and out) are right.
- The operating ranges, the Example 2 conditions and most of the table references match the full patent text (US 8,633,345 B2). Nothing is copied from it.
- Nothing outside `processes/isobutene-1/` changed.

**Low findings:**
1. **R-01 (#1):** the C8 by-product figure is attributed to Example 2, Table 11, but my reading of the patent finds it in Example 1, Table 6. The design value stays conservative either way.
2. **R-02 (#2):** DESIGN.md says the C-201 reboiler (394 K) needs MP steam, but LP steam at 420.8 K would leave a 27 K approach, so the reason given doesn't hold.
3. **R-03 (#3):** about 30 kW of heater fan and hot-oil pump power is left out of the LCI as a cut-off, yet it is twice the 15.8 kW of electricity that is counted.
4. **R-04 (#4):** DESIGN.md says "the issue names this route", but issue #165 leaves the route open. The MTBE route came from the run's task, and the mixed-C4 separation cases the issue suggests comparing are not discussed.
5. **R-05 (#5):** `process.yaml` states 99.97 wt% isobutene without saying that linear butenes are not modelled, because the feed is assumed to be pure MTBE.
6. **R-06 (#6):** the failing gates above are out of scope. The concept stage can't be signed off until the plot plan exists or a human accepts it as out of scope.
7. **R-07 (#7):** the maturity warning is recorded for tracking only. It needs a sourced capacity and MTBE feed composition, or a lower level in the schema.

Not checked: the separations against rigorous phase-equilibrium models (blocked until core #315), the balance script line by line, line sizes, the Atlas LCI build, and a tile-by-tile reading of the PFD.

The merge is pending and is for a human, not the author.

VERDICT: merge