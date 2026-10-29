I've written the review in `reviews/2026-10-28-pfd-lci-review.md` and committed it on `case/chloromethane-1` (`ab51f57`, not pushed). It reviews commit `a581b36`. I changed no design files. The review found no critical or high findings: one medium and five low.

**What I re-ran myself:**
- **`cheme validate`:** 0 errors, 0 warnings, still clean with the review record added.
- **`cheme process streams`:** all 4 blocks and 12 steps balance. `propagate --check` is clean.
- **`cheme check`:** every concept gate passes except the plot plan. Layout, P&IDs and datasheets fail as expected for a concept case.
- **`cheme maturity`:** reaches no level, and warns that `process.yaml` claims `concept`. `concept` is the lowest value the schema allows, and the notes say plainly that no level is reached.
- **`cheme assess lca --coverage`:** mass, element and carbon balances close; mass in = mass out = 1.5209 kg per kg product. All 9 background flows are listed as gaps, each with a description. Nothing is zero-filled, no licensed data is used, and the two per-process overrides are in `lca/mappings.yaml`.
- **Changes outside the folder:** none compared with where the branch started. A plain diff against `origin/main` shows `processes/thf-1/` as deleted, but only because main merged thf-1 after this branch began.

**Plausibility, checked by hand:**
- **Feeds:** 0.646 kg methanol and 0.823 kg HCl per kg product, against 0.635 and 0.722 stoichiometric. The extra HCl leaves with the dilute acid, which is close to the HCl–water azeotrope. The design records this as open item I-04.
- **Reactor:** the duty (about 1.5 MW) matches my reaction-heat estimate.
- **Compressor:** about 0.5 MW, which also matches.
- **Overall energy:** closes within about 3 %.
- **Sources:** the facts cited from US 4,794,204 match the patent text. I could not open Schmidt et al. 2014 (the publisher blocked the fetch), so its 97.6 % conversion and 98.8 % selectivity are unverified by me. No third-party content is copied.

**Findings:**
- **#1 (medium):** the gas leaving the quench holds 2.6 mol% water, while the cited patent gives about 0.1–0.2 %. DESIGN.md never discusses the difference. Its "check" that the spent sulfuric acid comes out at about 80 % (as the patent says) only works because of that higher water content, so it is not independent support. With the patent's water content the spent acid would be about 95 %. The balance and the LCI still hold.
- **#2 (low):** D-005 misquotes the patent's temperature range as 300–400 °C; it is 350–400 °C, so the 340 °C outlet sits just below it.
- **#3 (low):** the methanol stripper's bottoms cooler appears in no energy stream, so about 5 % of the cooling water is missing from the LCI.
- **#4 (low):** the modelled dimethyl ether is 1.33 times its equilibrium value. DESIGN.md says so openly.
- **#5 (low):** the maturity claim warning described above.
- **#6 (low):** the patent is cited without column or line numbers.

The merge is pending, to be done by a human, not the author.

VERDICT: merge