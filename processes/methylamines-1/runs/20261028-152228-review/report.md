I've written the review to `reviews/2026-10-28-pfd-lci-review.md` and committed it as `66479f4` on `case/methylamines-1`. It is not pushed, and I changed no design files. It covers commit `ea4cc4f` and has 11 findings: one high, five medium and five low. The `design-review` gate now passes, but only as an agent review.

**What holds up**
- Nothing outside `processes/methylamines-1/` changed.
- `cheme validate` reports 0 errors and 0 warnings, and `cheme process propagate --check` is clean.
- I redid the main numbers by hand and they match the flowsheet:
  - **Feeds and products:** methanol 10,920 kg/h, ammonia 3,220 kg/h and wastewater 6,140 kg/h follow from the 8 t/h product split.
  - **Converter:** the methanol-to-ammonia feed ratio is 2.00, conversion per pass is 98.9 %, and the reaction heat (about 2.5 MW) fits the 88 K temperature rise.
  - **LCI:** every per-kg value reproduces with mass allocation at a 55 % DMA share.
- No background value is zero-filled or taken from a licensed database. Every unmapped background is listed as a gap with a description, the per-process mappings are in the folder's `lca/mappings.yaml`, and I found no copied third-party content.

**High (R-01)**
- `process.yaml` uses five chemical names that are not in `chemicals/chemicals.yaml`: methanol, ammonia, methylamine, dimethylamine and trimethylamine.
- With them, `scripts/build_catalog.py` exits 1 with five errors, all from this process. CI runs that script (`validate.yml:97,100`), so merging this branch breaks the library's CI.
- The fix is either to add the registry entries in this change, as CONTRIBUTING asks, or to do what ammonia-1 does: leave unregistered chemicals out of `chemistry` and name them in a note.

**Medium**
- **R-02, maturity claim:** `process.yaml` says `maturity: concept`, but `cheme maturity` rates the evidence at "none" and warns that the claim exceeds it. The reason is that the two feed flows are labelled assumed rather than given with a source. The run report's statement that maturity "stops at balanced" is wrong, and there is no `checks/maturity.json`.
- **R-03, no MMA product case:** the only functional unit is 1 kg DMA, although this case is issue #171 (methylamine) and the issue asks for separate product cases.
- **R-04, unconfirmed benchmark basis:** the only check of the equilibrium model against a source may compare weight fractions with mole fractions. If the patent's values are molar, the model misses TMA by about 16 points, not 6.
- **R-05, unread sources:** the ammonia–TMA recycle, the separation sequence and the DMA-led product split rest on search summaries or an abstract only.
- **R-06, zero totals:** `lca/results.csv` and the allocation table in `results.md` show 0 kg CO2-eq, although every contribution is a gap. cheme generates these files.

**Low:** five minor points. Two are tooling: cheme calls the five columns sourced shortcut models although their outputs are assumed sharp splits, and `checks.yaml` cites a decision D-023 that `DESIGN.md` does not have. The others are the energy cross-check being on an inconsistent basis (the hot wastewater's heat is not counted), the steam "upper estimate" caveat missing from the LCI exchanges, and a patent cited in `reactions.yaml` but not in the source register.

A merge is pending: R-01 has to be closed first, and the branch must be merged by a human, not by the author or me.

VERDICT: fix