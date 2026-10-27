I fixed what can be fixed inside this folder and committed it in two commits (`7ac6c8b`, `110e08b`), not pushed. **CI on PR #192 will still fail**, because the last three errors can only be fixed outside `processes/ammonia-1/`.

## CI
The two library tests failed because the LCI export refuses `allocation: substitution` as a dataset's default.
- **Fixed:** `lca/lca.yaml` now shares the burdens between ammonia and the exported steam by exergy, with system model cut-off. Substitution is kept as a comparison. I calculated the exergy values myself: NH3 20,190 kJ/kg (published chemical exergy plus a Peng-Robinson calculation) and MP steam 1,262 kJ/kg (IAPWS-IF97 steam tables). Both are marked ASSUMED with their sources. NH3 now carries 94.8 % of the burdens. I added an `allocation.deviation` so the strict build doesn't raise a finding, and recorded the change in DESIGN.md D-021.
- **Still failing** (I re-ran the library build locally; these errors were hidden behind the first one):
  - `feed:NG: no mapping (chemical 'methane')`
  - `emission:C2H6` and `emission:C3H8`: no biosphere3 flow identity

  All three need entries in `lci/mappings.yaml`. For example, an `exchanges` override `"ammonia-1/feed:NG"` pointing at the existing `natural-gas` entry, and `biosphere` entries for ethane and propane to air. I tried two ways of doing this from `lca/lca.yaml` and cheme rejected both, so I reverted them.

## Review findings
The review (`reviews/2026-10-27-pfd-lci-review.md`) has **no critical or high findings**. I closed these medium and low ones:
- **#1 (medium):** DESIGN.md D-020 and `process.yaml` now say the printed 1.48 kg CO2-eq per kg NH3 is the plant's direct fossil CO2 only, not a carbon footprint. The run record still has the old wording, because run records are not edited.
- **#2 (medium):** added `emission_exclusions` for the furnace H-101 and the CO2 vent C-302 (open input I-07). The CH4, H2, C2H6 and C3H8 source texts now say NOT ESTIMATED, and the `lci-emissions-incomplete [H-101]` warning is gone. The excluded sources show up as cut-off limitations in `--coverage`, not in `gaps.csv`.
- **#4 (low):** `validation.notes` now states that `cheme maturity` reaches no level.
- **#5 (low):** added a note in DESIGN.md D-006 on the non-unique block reaction extents. It still needs reporting to cheme-as-code core.

**Left open:**
- **#3 (medium):** a sourced Dutch natural-gas composition and supply pressure. This needs a published source, a rerun of `scripts/plant_balance.py` and a regenerated LCI, so it isn't a quick fix.

## Checks after the changes
- **`cheme validate`:** 0 errors, 0 warnings.
- **`cheme process streams`:** all balances ok.
- **`cheme assess lca --coverage`:** "partial screening", 10 gaps, each one described.
- **`cheme maturity`:** level none (unchanged).
- **`cheme check`:** the same gates fail as before (layout, P&IDs, datasheets, all outside this stage's scope). The `design-review` gate now fails too, because the files the review covered have changed, so a fresh independent review is needed.

**Merge pending:** the branch needs pushing, the `lci/mappings.yaml` entries to make CI pass, and a new review.
