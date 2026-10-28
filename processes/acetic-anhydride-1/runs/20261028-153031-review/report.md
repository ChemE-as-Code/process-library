I've written the review as `reviews/2026-10-28-pfd-lci-review.md` and committed it as `2b1d957` on `case/acetic-anhydride-1`. It covers commit 589e80f, I changed no design files, and nothing is pushed. It has nine findings: none critical or high, three medium and six low.

**What I re-ran myself:**
- **`cheme validate`:** 0 errors and 0 warnings, including on the new review record.
- **`cheme check`:** every concept gate passes except the plot plan, which is out of scope for this issue. The basic-stage gates that need P&IDs, layout, datasheets or this review fail, as expected for a concept case.
- **`cheme maturity`:** calculation maturity is "none", because the feed flows and the separator and absorber settings are assumed values. `process.yaml` claims "concept", which is the lowest level the schema allows.
- **`cheme process streams`:** all 4 blocks and 16 steps close. The plant is 14 892 kg/h in and out.
- **`propagate --check`:** no output, exit code 0.
- **`assess lca --coverage`:** the mass, element and carbon balances close. All 11 missing backgrounds are listed as gaps, each with a description. No licensed values are in the files, and the result is publishable.
- **Scope:** nothing outside `processes/acetic-anhydride-1/` changed.

**Plausibility:** I recalculated the main numbers by hand and they agree with the design:
- **Cracker:** 84 % conversion and 0.92 ketene selectivity match the cited patent (US 4,455,439). The coil duty is 4.54 MW against my estimate of about 4.6 MW.
- **Dilute acid:** 39.5 wt% acid, against 38 wt% in the patent.
- **Acid use:** 1.246 kg per kg product, about 94 % of theory.
- **Firebox:** 0.915 efficiency, consistent with its stated stack temperature.
- **Direct CO₂:** 0.195 kg per kg product.
- **Utilities, line sizes and LCI:** steam, pump and vacuum-pump duties match within a few percent. Line sizes follow from the stated velocities. Every amount per kg in the LCI equals the flowsheet value divided by 6250 kg/h.
- **Sources:** cited patent facts are restated in the author's own words with locators. Nothing is copied.

**Medium findings:**
- **R-01:** the published LCI lists CO, CH₄, ethylene and ketene emissions as calculated 0 kg. The same file says these furnace emissions were not estimated, so a reader sees a zero instead of a gap.
- **R-02:** the balance assumes no acid or anhydride vapour leaves in the absorber vent. That only holds with a vent scrubber or a seal-fluid return, and neither is in the flowsheet or the equipment list. Without one, roughly 1 % of product could be lost.
- **R-03:** the notes in `process.yaml` don't say that `cheme maturity` gives calculation maturity "none".

**Low findings (R-04 to R-09):**
- **R-04:** the patent-sourced cracker conversion and selectivity are marked "assumed".
- **R-05:** the 3.0 MJ of steam per kg water for acid recovery, the largest energy assumption, has no source or sensitivity.
- **R-06:** three equipment-list items need a second look:
  - SS316L at a 725 °C design temperature for the cracked-gas cooler.
  - A furnace design temperature only 50 K above the outlet gas.
  - The liquid-ring vacuum pump typed as a centrifugal compressor.
- **R-07:** −10 °C brine is filed under the registry's chilled-water entry.
- **R-08:** the gap counts (11, 10 and 14) differ between `process.yaml`, `DESIGN.md` and the gap file.
- **R-09:** a leftover reference to a decision D-023, which doesn't exist, in a commented-out example in the template's `checks/checks.yaml`.

The merge is still pending: a human or the reviewer has to merge it, not the author.

VERDICT: merge