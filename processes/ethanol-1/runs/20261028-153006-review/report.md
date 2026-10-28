I reviewed ethanol-1 at 1e9890d and found no critical or high issues: 3 medium and 7 low findings, all open. The record is committed as 8c84154 (`reviews/2026-10-28-pfd-lci-review.md`). I changed no design files and did not push.

**What I re-ran myself:**
- **`cheme validate`:** 0 errors, 0 warnings, still clean after adding the review record.
- **`cheme check`:** every concept gate passes except the plot plan, which is out of scope. The basic and detail gates fail as expected (no P&IDs or layout).
- **`cheme process propagate --check`:** nothing stale.
- **`cheme process streams`:** every block and step balances. Overall, 8,076 kg/h ethylene + 8,473 kg/h water in equals 12,502 kg/h product + 646 kg/h off-gas + 3,401 kg/h wastewater out.
- **`cheme maturity`:** calculation maturity is "none", so the `concept` claim in `process.yaml` triggers a warning. `concept` is the lowest value the schema allows, so it cannot be lowered.
- **`cheme assess lca --coverage`:** "partial screening", 16 gaps, mass and carbon/hydrogen/oxygen balances close.
- **Library LCI build:** I also ran `build_lci.py`, which gives 10 gaps instead of 16 (finding #2).

**Medium findings:**
1. **Overstated separator credit:** `cheme maturity` credits V-101, V-102, C-201 and C-202 as "predictive, sourced" models. They are assumed fixed splits from `scripts/balance.py`; cheme infers the credit from the step type. The run report repeats the error.
2. **LCI gap count disagrees:** `lca.yaml`, `lca/mappings.yaml` and DESIGN.md D-013 say every background is unmapped (16 gaps). The library build actually links six of them: water, power, cooling water and wastewater through shared mappings, and both steam levels through the folder's own override. Only 10 remain as gaps.
3. **Main steam figure is unchecked:** the C-202 reboiler (16.6 MW, 74 % of the steam) rests on a reflux ratio of 3 chosen by judgement and on an unsourced 18 % return from the molecular-sieve regeneration. DESIGN.md already flags it as the first number to check.

**Low findings:**
- **C-101 scrubber:** 99 % ethanol recovery with this little wash water was never checked and may be impossible. The effect on the LCI is negligible, because the unrecovered ethanol is recycled rather than lost.
- **K-102 flash-gas compressor:** liquid will form in the intercoolers, but there is no knock-out drum or condensate route.
- **Molecular sieve:** no feed superheater, so a small steam duty is missing.
- **Sources:** one patent (US 4329520) was only seen as a search summary but is cited without a caveat. The EN 15376 water limit was not re-read.
- **Wrong registry entries:** the off-gas is mapped to `flare-gas` although it is burned as fuel gas. Steam is mapped to a per-kg entry while the inventory counts it in kWh.
- **Maturity note:** `process.yaml` does not say that the calculation maturity is "none".
- **Data quality score:** the default scoring rates the data as very recent, though the reactor data come from 1977 and 1994 patents.

**What looks sound:**
- The route and boundary match the issue.
- Conversion, yield (94 %), heat of reaction, temperature rise and duties are plausible for this technology.
- Every key value is sourced with a locator or marked ASSUMED.
- No third-party content is copied and no licensed values are used.
- The LCI is per kg of product and consistent with the flowsheet.
- Nothing outside `processes/ethanol-1/` changed.

The merge is pending; it is for a human or reviewer to do, not the author.

VERDICT: merge