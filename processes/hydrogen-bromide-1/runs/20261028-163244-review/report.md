I've reviewed the hydrogen-bromide-1 case and found nothing critical or high. There are 2 medium and 6 low findings. The review is committed as `b734d90` in `reviews/2026-10-28-pfd-lci-review.md`, covering commit `0004c58`; it is not pushed.

**What I re-ran myself:**
- **`cheme validate`:** 0 errors and 0 warnings, before and after adding the review.
- **`cheme check`:** every concept gate passes except the plot plan, which was out of scope. The design-review gate now passes, but the review is agent-only, not approved by a human.
- **`cheme maturity`:** calculation maturity is "none". The `concept` claim is flagged as exceeding the evidence, and `process.yaml` states this openly.
- **Balances:** every block and step balances (`cheme process streams`), and `propagate --check` is clean.
- **LCI:** `--coverage` reports a partial screening carbon footprint with 8 gaps, each with a description, and mass and element balances close.
- **Scope of changes:** compared from where the branch started, only files under `processes/hydrogen-bromide-1/` changed. A plain diff against today's main also shows thf-1 files, but only because thf-1 was merged after this branch was cut.

**Hand checks:**
- **Mass:** stoichiometry, the 5 % hydrogen excess, the water balance, the vent composition and the 0.036 mg HBr per kg in the vent all reproduce.
- **Duties:** the vaporiser (58 kW), burner (≈167 kW), gas cooler (11.5 kW) and absorber (232 kW) duties all match my rough recalculation.
- **LCI per kg HBr:** mass in and out per kg HBr is 2.084265 kg both ways, and it matches the flowsheet.
- **Plausibility:** the amounts per kg are reasonable for a pressure-fed burner and absorber.
- **Licences:** I found no copied third-party content and no licensed database values.
- **Route:** the route and the choice of aqueous acid over anhydrous gas match issue #130.

**Medium findings:**
- **#1 Heat of solution:** the absorber cooling is 57 % of all cooling, and it rests on values nobody read at source. They are a search-summary figure plus a ratio carried over from the HCl case, which was itself recalled. The fix is to read the published NBS tables for HBr at about 5 mol water and cite the table.
- **#2 Activated carbon:** the finishing bed's routine carbon make-up and spent carbon are excluded as "non-routine" with no amount. They show up neither as a gap nor as a checkable cut-off.

**Low findings:**
- #3: Br2 is declared burden-free in the LCI.
- #4: the weak acid flows from the scrubber to the absorber with no pump and no stated elevation to drive it.
- #5: DESIGN.md:74 gives the reaction heat in "kJ per kmol", off by a factor of 1 000.
- #6: some source locators are vague, and one Wikipedia URL is missing from `process.yaml`.
- #7: R-101's 300 °C design temperature doesn't say which part it covers, given a flame above 1 600 °C.
- #8: the maturity claim exceeds the evidence, but it is openly disclosed.

The merge is pending: it is for a human or reviewer to do, not the author.

VERDICT: merge