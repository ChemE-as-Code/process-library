The one high finding (#1) is closed, and so are all five mediums and most of the lows. #8 is only partly closed. Everything is committed in 5 commits on `case/methylamines-1`, nothing is pushed, and every change is inside `processes/methylamines-1/`. Each finding has a "Response" entry in `PROGRESS.md` with its commit.

**Findings closed**
- **#1 (high), 8c42651:** the five chemicals that have no registry entry yet (methanol, ammonia, MMA, DMA, TMA) are out of `chemistry` in `process.yaml`. They are now named, with their inventory keys, in `validation.notes`, as ammonia-1 does. With no registered feedstock left, the two steam flows are listed under inputs. `scripts/build_catalog.py` now exits 0, so merging this branch no longer breaks CI.
- **#2, e5361f9:** the fresh methanol and ammonia feeds (S1, S2) are now marked `given`, with the design basis as source; the capacity and slate behind them are still marked ASSUMED. `cheme maturity` now reaches **balanced**, `checks/maturity.json` is written, and the `concept` claim no longer raises a warning. The BFD/PFD and the LCA outputs were regenerated. DESIGN.md D-006 now corrects the earlier run report, which wrongly said the evaluation stopped at balanced.
- **#3, 9d2358a:** D-014 and `lca/README.md` now say that under mass allocation the inventory per kg MMA (#171) and per kg TMA is the same as per kg DMA.
- **#4, fdea259:** I re-read US 4,485,261 A. It does not say whether its equilibrium ratios are by weight or by mole. I recorded weight basis as an ASSUMED inference, because the patent's prior-art ratios are explicitly by weight and close to them. I also wrote down that on a mole basis the model would miss TMA by about 16 points instead of 6. The benchmark is still weak.
- **#5, fdea259:** I read US 7,309,403 B2 and US 2,206,584 A and recorded their locators in the source register; D-007 and D-008 match them. Neither gives the composition of the ammonia–TMA mixture. Two claims still rest on sources I could not read in full, and are now marked unverified: "DMA is the main demand" (abstract only) and the high reflux in C-102 (search summary only).
- **#6, 9d2358a:** the docs now say the `0` totals in the LCA results mean "no total", not a zero footprint. The output itself is still to be reported to core.
- **#7, e5361f9:** noted in D-011 that `cheme maturity` overstates the model basis of the columns. Still to be reported to core.
- **#9, #10, #11, 9d2358a:**
  - #9: the steam exchanges now carry the "upper estimate, no heat integration" caveat.
  - #10: the citation of US 7,754,921, which is not in the source register, was dropped.
  - #11: the leftover D-023 in `checks/checks.yaml` was replaced.

**Left open**
- **#8 (low), partly closed:** the energy cross-check in D-006 is restated on a consistent basis. The wastewater cooler (about 0.7 MW) is not in the flowsheet yet; adding it changes the flowsheet and the LCA, so I left it for the next stage.
- **Core issues for #6 and #7** still need reporting; that is outside this folder.
- **The registry entries themselves** still need adding in the registry PR, which is also outside this folder.

**Re-runs (final state)**
- **`cheme validate`:** 0 errors, 0 warnings.
- **`cheme check`:** concept gates pass except `layout-plot-plan`, which is out of scope. `design-review` now fails because the review record is older than these changes; it needs a new independent review.
- **`cheme maturity`:** balanced, against the `concept` claim.
- **`cheme process streams`:** every balance closes.
- **`cheme assess lca --coverage`:** partial screening carbon footprint with 7 gaps, and the output files are current.

Merge is pending: the branch needs a re-review by someone other than me and a human merge.

STATUS: DONE