I merged `origin/main` into `stage/basic-layout` and committed it as `e264005`. Nothing is pushed, and `build/pr-body.md` is untouched. `cheme validate` shows **0 errors** (207 warnings), but `cheme check --stage basic` still fails 4 gates, so the stage does not pass yet.

**How the conflicts were settled**
- **Datasheets (52 files):** the only thing this branch's draft datasheets had that main's S7 ones lack is each item's empty weight. So I kept main's datasheets and added that weight to each, marked ASSUMED, with its source (the equipment list and `scripts/estimate_weights.py`). I regenerated the outline drawings.
- **Equipment list:** no field was changed on both sides. Each item takes main's line (design pressure, temperature, material) plus this branch's weight, lift weight and notes. A script checked all 52 items: no mismatches.
- **Line list:** for the flare header FLR-1146 I kept this branch's routing note and added main's relief-load note to it.
- **DESIGN.md and PROGRESS.md:** both sides' entries are kept. Two decision ids clashed, and main's are already on the default branch, so I renumbered this branch's:
  - D-031 (3D layout) became **D-036**;
  - D-033 (crane lanes) became **D-037**.

  I updated the references in the layout, routing, TEA and script files. The S5/S5b review and run records keep the old numbers; a note under D-036 explains the mapping. A merge entry is added to PROGRESS.md.
- **Regenerated rather than hand-merged:**
  - the layout model (`cheme layout build --force`), lifting study, take-off and bulk estimate: only fingerprints and decision ids changed, routing is the same;
  - the equipment cost estimate, which now uses main's S7 sizes. 8 items have a bare-module cost, 12 a purchased cost only, and 32 are not covered (21 are outside the cost correlations' ranges, 11 have no size). Purchased cost is USD 8.74 M, bare module USD 15.2 M. I added this as an update under D-035.
  - The flow diagrams didn't need rebuilding: main changed nothing under `process/`.

**`cheme check --stage basic`:** everything passes except four gates.
- **`lifting-study`:** 8 crane lanes are still blocked. This was already failing on the branch.
- **`maturity-balanced`:** some reactor and feed inputs have no source. Also already failing; `cheme maturity` gives calculation maturity "none".
- **`design-review` and `layout-review`:** they now fail because the merge changed files the round-3 reviews covered. A new review of the merged branch is needed.

Validation still warns that the HAZOP H-01 input `piping/special-items.yaml` changed since it was stamped. That warning comes from main (S8 edited the file after the HAZOP). Re-stamping is a HAZOP action, so I left it.

A merge is pending: the PR needs an independent re-review and merge by the reviewer.

STATUS: DONE