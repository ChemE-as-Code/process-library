I reviewed the acetylene-1 case at commit `3e163e7` and found nothing critical or high: one medium and six low findings. The review is in `reviews/2026-10-28-pfd-lci-review.md`, committed as `0926550` on `case/acetylene-1` and not pushed. I changed no design files.

**What I re-ran:**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme check`: every concept gate that applies passes. The plot-plan gate fails because the layout is out of scope; the basic and detail gates fail because there are no P&IDs, layout or datasheets yet.
- `cheme process streams`: every block and step balances.
- `cheme process propagate --check`: clean.
- `cheme maturity`: calculation maturity is "none", so the `concept` claim triggers a warning that it exceeds the evidence. `concept` is the lowest value the manifest allows, and DESIGN.md admits the gap.
- `cheme assess lca --coverage`: a partial screening carbon footprint. All 15 gaps are listed with descriptions; nothing is filled with zero and no licensed values are used.
- `cheme assess lca --check`: the LCA outputs are current.
- Every changed file is under `processes/acetylene-1/`.

**Hand checks.** I recomputed the main numbers from the stream table and they agree with it:
- Feeds: oxygen-to-gas ratio 0.602.
- Burner: soot ratio 22 kg/kg, and the dry cracked gas matches the patent composition it was fitted to.
- Recovery: 98.0 % of the acetylene formed reaches the product.
- Water circuit: in and out balance.
- Duties: quench, main cooler, preheat, compressor and fired heater are within a few percent of my estimates.
- LCI: energy allocation 27.0 %; mass per kg of product closes (15.659 kg in, 15.658 kg out).

Consumptions, yield and soot are plausible for this process. The cited sources are patents, used as facts in the design's own words with locators, and no third-party content is copied. I did not re-open the patents online, so their numbers are checked for consistency only.

**Findings:**
- **R-01 (medium):** DESIGN.md D-005 says the design needs 13 % more natural gas than the patent example and calls this consistent. The real gaps are +25 % natural gas, +26 % oxygen and +18 % syngas. About 8–10 % of that is unexplained, on the two largest LCI inputs.
- **R-02 (low):** the burner R-101 has no emission estimate or declared exclusion in `lca/lca.yaml`, so the coverage run warns about it.
- **R-03 (low):** the two stripper duties are split inconsistently with the solvent temperature between them. The total heat is right.
- **R-04 (low):** the rich-solvent pump is missing from the power, about 0.09 MW (roughly 1 % of the electricity).
- **R-05 (low):** `process.yaml` does not say that calculation maturity is "none", although that file is what Atlas readers see.
- **R-06 (low):** `process/design-basis.yaml` cites the wrong decision (D-009 instead of D-008) and has a duplicated phrase.
- **R-07 (low):** the per-kg inventory lists allocated inputs next to the unallocated syngas, and the `lca/` folder doesn't say so. A reader could take 1.28 kg natural gas per kg as the plant's use; the actual figure is 4.73.

The merge is pending: a human or the reviewer merges the branch, not its author.

VERDICT: merge