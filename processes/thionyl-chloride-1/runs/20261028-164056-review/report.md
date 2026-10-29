I've reviewed the thionyl chloride case and found nothing critical or high: one medium and seven low findings, all open. The review is in `reviews/2026-10-28-pfd-lci-review.md` against HEAD `b83cdb1`, committed as `5701a33` and not pushed. `cheme check` now reports the `design-review` gate as ok.

**Checks I re-ran myself:**
- **`cheme validate`:** 0 errors and 0 warnings.
- **`cheme process streams`:** all 5 blocks and 20 steps close (largest residual 0.02 kg/h).
- **`cheme process propagate --check`:** no deviations.
- **`cheme assess lca --coverage`:** mass and element balances closed; 15 gaps, each with a description, and no zero-filled or licensed background values. `lca/mappings.yaml` is empty, with the reason given.
- **`cheme check`:** the one failing concept gate is the plot plan (`layout-plot-plan`), and layout was out of scope for this run.
- **`cheme maturity`:** it reaches no level and warns that the `concept` claim exceeds the evidence. `concept` is the lowest value the manifest allows, and the manifest's notes already say this, so the claim is honest.

**Numbers checked by hand:**
- Raw materials per kg are close to the stoichiometric minimum. The gap is explained by the 1 % purge, which loses about 1.9 % of the SO2.
- The utility totals match the energy streams and the LCI amounts.
- My estimates of the reaction heat, the two chlorinator duties, compressor power, and the degasser and column duties all land within concept accuracy of the design's values.
- The LCI's 1.113 kg in equals 1.113 kg out, consistent with the flowsheet.
- Nothing outside the process folder changed relative to where the branch started. The `thf-1` renames in the diff come from `main` moving on since then.
- The source references paraphrase the patents; I found no copied text, tables or figures.

**Findings:**
- **R-01 (medium):** the degasser is modelled as removing all SO2 and Cl2. By the design's own vapour-pressure model, its stated bottoms temperature is too low for that, so about 1.5–2 mol% of SO2 and Cl2 would stay in the crude. The purification column has no outlet for these light gases, so they would end up in the 99.7 wt% product. The fix is to raise the degasser bottoms temperature to about 352 K or give the column a vent.
- **R-02 to R-08 (low):**
  - The run report gives the plant balance as 3805 kg/h in and out; the correct figure is 3778 kg/h, and the balance does close. The run record can't be edited, so the correction belongs in `PROGRESS.md`.
  - The reactor's effective conversion is about 68 %, not the 75 % implied; that is still within the patent's range.
  - One reactor conversion value has no provenance.
  - The maturity notes should name the warning.
  - Oxygen is carried dissolved through the liquid chlorinators.
  - Several heat-integration options are missing from the open items.
  - Patent page references are coarse.
  - Small labelling gaps remain in the LCI flows.

The merge is still pending, for a human to do, and no stage has been signed off.

VERDICT: merge