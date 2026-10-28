I fixed the CI failure and closed six of the seven review findings. Everything is committed in two commits (`a468f4d` changes, `d78dad9` PROGRESS.md responses) and not pushed. The newest review, `2026-10-28-pfd-lci-review`, had **no critical or high findings**, so I worked through the medium and low ones that were quick.

**CI (PR 225):** the failing test, `tests/test_utilities.py::test_the_library_builds_strict_with_the_utilities`, gave two allocation warnings for `lca/dataset.yaml`. The cause is that core leaves `method: mass` out of the dataset it generates, and nothing explained why prices weren't used. `lca/lca.yaml` now gives the allocation as `method: shares` with SIC 0.80 and MET 0.20 (the mass split, so the numbers don't change) plus an `allocation.deviation` saying no prices have been sourced. I ran the CI's pytest command locally with core pinned to the same commit, and that test now passes. I didn't re-run the full suite.

**Findings closed:**
- **#1 (medium):** the LCA goal (`lca/lca.yaml`) and `process.yaml` notes now say plainly that 2.03 kg CO2-eq/kg and its interval cover only the direct furnace CO2 and CH4. It is not a carbon footprint: electricity (7.7 kWh/kg), coke, sand and landfill are still gaps.
- **#2 (medium):** CO stays outside the climate method rather than getting a factor we made up. Its CO2 equivalent if it oxidises (44/28 kg per kg, +0.64 kg/kg, 2.67 kg/kg in total) is now stated next to the headline in DESIGN.md D-010.
- **#3 (medium):** the burn-off step B101 is no longer treated as adiabatic. A new energy stream, Q6, sends 21.0 MW to ambient, calculated by `scripts/sic_balance.py` from heat capacities I assumed. The note on flue line FG-101 now says the flue gas figures can't be used to size the stack, ducts or fans, and DESIGN.md lists hood dilution air as an open input.
- **#4 (low):** I removed the two comparisons that had no locator (the IPCC 1996 CO factor and the unnamed hot-model study).
- **#5 (low):** the `process.yaml` notes now say `cheme maturity` supports no level yet.
- **#6 (low):** the sorting outlets and the streams after them (S9–S13) are now at 323.15 K, so sorting no longer cools the material for free.

**Left open:** #7 (low). The stray `/Users/arturschweidtmann/Developer/test/wt/sc-schema.json` is still there. It's outside the repository and this folder, which I wasn't allowed to touch, so it needs deleting by hand.

**Checks after the changes:**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme process streams`: every block and step balances.
- `cheme assess lca --coverage`: still a partial screening result with the same 9 gaps.
- `cheme maturity`: still calculation maturity none, with a warning that the `concept` claim is higher than that, as before.
- `cheme check`: all concept gates pass except the plot plan, which is out of scope. `design-review` now fails because the reviewed files changed, so a new independent review is needed.

The merge is pending: it needs that new review, then a human or the reviewer to merge.

STATUS: DONE