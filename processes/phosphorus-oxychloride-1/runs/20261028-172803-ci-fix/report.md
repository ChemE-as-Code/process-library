I fixed the CI failure and closed every finding in review `2026-10-28-pfd-lci-review` except #5(b). The review had no critical or high findings: #1 was medium, #2–#5 low. There are four commits, nothing outside `processes/phosphorus-oxychloride-1/` changed, and nothing is pushed.

**CI failure (PR #230, commit 0f7c79e):** two library tests failed because the LP steam input (`feed:LPS`) is counted in kWh, but the library build linked it to the shared `steam` entry, which counts kg. I added an override to `lca/mappings.yaml` that links it to the shared `steam-heat` entry instead, as acetone-1, dmf-1 and ethanol-1 do. Locally, `tests/test_export_formats.py` now passes and the steam error is gone from `test_utilities.py`. That test still fails locally, but only on warnings about other processes and benchmarks, because my environment lacks the `cheme-as-code[units]` extra. I could not run the full CI test setup, so CI itself has not confirmed the fix.

**Findings closed:**
- **#1 (POCl3 heat of vaporisation was 20–26 % too low)**, commit 14f3375: `scripts/balance.py` now takes it from the slope of the same vapour pressure the vent condensers use: 34.6 kJ/mol at the boiling point, against 27.5 before. PCl3 values are unchanged. The C-302 reboiler and condenser go from 298.4 to 376.4 kW. LP steam rises from 0.0907 to 0.1105 kWh per kg POCl3 (+22 %), close to the reviewer's estimate. The check is recorded in D-008, and the flowsheet duties (Q4–Q8), equipment notes, `process.yaml`, the BFD/PFD and the LCI are updated.
- **#2 (R-101 reaction heat)**, same commit: the heat of the PCl3 oxidised inside R-101 is now counted per mol of PCl3 rather than per mol of O2. Q1 goes from 2388.7 to 2443.2 kW, and cooling water from 1.17 to 1.20 kWh/kg. D-004 is updated. The mass balance is unchanged.
- **#3 (caustic soda basis)**, commit 7a52242: the LCI text now says the 3.87 g/kg is 50 wt% solution, i.e. 1.93 g NaOH as 100 %.
- **#4 (two text inconsistencies)**, same commit: the functional unit purity is now 99.998 wt%, as in D-002. The phosphorus-mud exclusion now gives the source's 0.2–0.5 wt%, and the wash water is named once.
- **#5(a) (stray D-023 reference)**, same commit: the template comment in `checks/checks.yaml` no longer cites it.

PROGRESS.md has a Response entry for each finding and for the CI fix (commit cec6696).

**Left open:**
- **#5(b) (branch based on an old main):** merging or rebasing origin/main is a branch operation for a maintainer and would bring in files outside this folder. The PR's diff against the merge base already contains only this folder.

**Checks after the changes:**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme process streams`: every block and step balances.
- `cheme assess lca --coverage`: partial screening, 14 gaps, mass and element balances closed. This is the same as at review time.
- `cheme check`: the concept and basic process gates pass. The `design-review` gate now fails because the reviewed files changed, so a fresh independent review is needed. The P&ID, layout and datasheet gates were already failing and are out of scope.
- `cheme maturity`: calculation maturity is still none, and the "concept" claim still gets the exceeds warning (no simulation, specified units).

A merge is pending: the branch is not merged and needs a new review first.

STATUS: DONE