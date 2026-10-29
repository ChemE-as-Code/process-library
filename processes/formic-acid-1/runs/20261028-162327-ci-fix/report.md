I fixed the CI failure and closed all seven review findings. The review had no critical or high findings, so I also worked through the medium one and all six lows. Everything is committed in three commits (`24bf222`, `d0e5f25`, `1da3894`) and not pushed.

**CI (PR #220):** both failed runs broke on the same two library tests. The LCI build refused the low-pressure steam input (`feed:LPS`): `process.yaml` names it `steam`, which the library counts in kg, but the plant's inventory counts that steam as heat in kWh. I added the shared kWh entry `steam-heat` for it in `lca/mappings.yaml`, which is how hda-1 and nitric-acid-1 handle the same case. With CI's exact command, the full library suite passes locally (403 tests). After regenerating the LCI I re-ran the two failing test files and they still pass.

**Findings closed: R-01 to R-07**
- **R-01 (medium), C-301 reflux:** the reviewer was right. A new script, `scripts/c301_rmin.py`, estimates the minimum reflux at 1.96, so the assumed ratio of 1.0 was below the minimum. The ratio is now 2.4 (1.2 × minimum, ASSUMED). The script is a shortcut: vapour pressures from `thermo` plus an activity model fitted so the azeotrope sits at 80 wt% at 203 kPa(a). The effects:
  - the C-301 reboiler goes from 7.8 to 13.3 MW;
  - low-pressure steam goes from 3.64 to 4.46 kWh per kg of product, about 1.9 times the prior-art figure the patent quotes;
  - cooling water rises to 4.49 kWh/kg;
  - DESIGN.md D-011 no longer calls the steam figure conservative; it now says it is uncertain in both directions.
- **R-02, preheater duty:** the E-201 duty is now calculated from 340 K, matching the stream table, so the preheat drops from 2.02 to 1.70 MW.
- **R-03, dissolved CO:** about 5 kmol/h (22 g per kg of product, ASSUMED order of magnitude) leaves V-101 dissolved in the liquid. D-007 now requires the C-101 condenser vent to go to the oxidiser; with that routing the LCI is unchanged.
- **R-04:** `process.yaml` now says `concept` is claimed as the lowest level, not because the evidence supports it.
- **R-05, SRC-4:** the 95 % approach to equilibrium is now marked ASSUMED, and US4299981 is recorded as an unverified lead whose ratio direction is unclear. This uses the review's interim action; I did not read the patent's full text, and that remains a next-stage task in D-014.
- **R-06:** the CO-per-kg wording in D-012 is corrected.
- **R-07:** the oxidiser NOx, column-vent and decomposition exclusions now have ASSUMED per-kg bounds, given in their text. Fugitive emissions are stated as not boundable before P&IDs. The schema has no amount field for these exclusions, so the tool's informational "cut-off unchecked" note stays.

The flowsheet, equipment list, design basis, LCI files and BFD/PFD were updated and regenerated, and each response is logged in PROGRESS.md.

**Checks afterwards**
- **`cheme validate`:** 0 errors. Its 7 warnings are the finding-id format in the review record, which I may not edit.
- **`cheme process streams`:** every block balances.
- **`cheme assess lca --coverage`:** partial screening carbon footprint, mass, element and carbon-origin balances closed, 11 gaps, publishable.
- **`cheme maturity`:** unchanged from the review, calculation maturity none with the claim-exceeds warning.
- **`cheme check`:** the same gates fail as at review time (no P&IDs, layout or datasheets). The design-review gate also now fails because the reviewed files changed.

**Left open:** none of the seven findings. Separately, the new steam and reflux numbers need a fresh independent review to make the design-review gate current. Merge is pending: a human or the reviewer merges, not me.

STATUS: DONE