I've fixed the CI failure and closed most of the review findings, in five commits on `case/iodine-1`. Nothing is pushed, and every change is inside `processes/iodine-1/`. The review had no critical or high findings, so I worked on the three mediums and the quick lows.

**CI (PR #233).** Both failing runs had the same cause. The library build matched the LP steam feed, which is counted in kWh of heat, to the shared `steam` entry, which is counted in kg, and refused the mismatch. I added an override in `lca/mappings.yaml` that uses the `steam-heat` entry instead, as acetone-1 does. The full library test suite now passes locally (412 passed).

**Findings closed**
- **#1 (medium):** D-005 no longer calls the air ratio "conservative". The Henry-constant check is now described as an upper bound for fresh water, and chloride complexation of iodine (I2Cl-) is named as an open factor alongside I3-. The I2Cl- constant is still unsourced. The air ratio is now part of the gated T-201 sizing in D-007. I added a sensitivity: at twice the air ratio the fan needs about 200 kW, which adds about 0.8 kWh per kg (+17 % power).
- **#2 (medium):** each `missing:` in `lca/lca.yaml` now says which background activity it needs. I reran `cheme assess lca --write`, so `gaps.csv` and `dataset.yaml` carry these descriptions.
- **#3 (medium):** the 90 % recovery is now described as calibrated to the patent (US 2013/0243684 A1), not as a check. This is fixed in `process.yaml`, the design basis, the DESIGN.md basis table and D-006.
- **#4:** M-301 design temperature raised to 175 °C, above the steam jacket's 148 °C.
- **#6:** SRC-2 is now cited as US Bureau of Mines, and the SRC-5 pH wording is corrected.
- **#8:** the iodine emission now has a release height (`non-urban-high-stack`, assumed). The carbon origin it is forced to carry is noted as a schema limitation.
- **#9:** the absorber's low liquid rate is recorded as a check for when T-202 is sized.
- **#10:** the DESIGN.md method table now lists M301 as specified values from the balance script, and notes that `cheme maturity` misreports it.
- **#11:** a new decision, D-013, lists the gates outside the scope of issue #145 and states that no sign-off is claimed.

**Findings left open**
- **#5 (partly done):** the melter-vent exclusion now gives an upper bound for HCl (0.46 kg/h). The iodine bound needs a vent design that doesn't exist yet. The LCA schema also has no amount field for an emission exclusion, so the cut-off check still can't run.
- **#7:** adding paragraph or line locators means reading the patents again at that level. I didn't do that, and I didn't want to write locators I hadn't checked.
- **Core-side parts of #8 and #10:** the identity for iodine in the LCA emission list and the maturity misreport are core issues. I didn't file them, because that is outside this folder.

**Checks after the changes**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme process streams`: every block and step balances.
- `cheme assess lca --coverage`: partial screening, with 11 gaps that now carry descriptions.
- `cheme maturity`: unchanged. It supports no level against the claimed `concept`, as D-012 already discloses.
- `cheme check`: fails the same out-of-scope gates as before. `design-review` is now also stale, because the reviewed files changed.

A Response entry for each finding is in PROGRESS.md, with its commit. Merge is pending: the response commits need a re-review, and a human has to merge.

STATUS: DONE