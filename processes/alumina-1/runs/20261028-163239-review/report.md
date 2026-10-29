I found no critical or high problems with alumina-1. The balances close, and the inventory per kg of alumina matches the flowsheet. One medium finding should be fixed before the inventory is published.

The review is in `reviews/2026-10-28-pfd-lci-review.md`, committed as 5bd19c4 against HEAD a6f61ad. It is not pushed. The `design-review` gate in `cheme check` now passes.

**What I re-ran myself**
- `cheme validate`: 0 errors and 0 warnings. Two notes about missing decisions D-012 and D-023 come from commented-out template lines and don't matter.
- `cheme check`: every concept gate passes except the plot plan, which is outside this stage. The basic-stage gates fail as expected, with no P&IDs or layout yet.
- `cheme maturity`: calculation maturity "none", and a warning that the `concept` claim in `process.yaml` goes beyond the evidence. The file explains this honestly.
- `cheme process streams`: all 6 blocks and 19 steps balance. `cheme process propagate --check`: nothing out of date.
- `cheme assess lca --coverage`: 10 background gaps, each with a description and none set to 0. Mass, element and carbon balances close (3.5767 kg in and out).
- Only files under `processes/alumina-1/` changed since the branch point. A plain diff against `origin/main` also shows other cases deleted, but only because main has moved on since this branch was made.

**Hand checks.** The numbers hang together:
- Alumina recovery is 91.7 %.
- Sodium make-up matches the losses: about 1930 kg/h lost, 1935 kg/h made up.
- Precipitation yield is 81 g/L, which agrees with the assumed liquor ratios.
- Combustion air and flue gas both check.
- The heats of reaction are arithmetically correct.
- The heat duties of E-401, R-401 and E-501 check.
- Lime, electricity, natural gas and CO₂ per tonne match the cited sources.

I found no copied third-party tables or text and no licensed database values.

**Findings**
- **#1 (medium):** The design notes say the steam heat (2.42 GJ/t) is probably too low and the caustic make-up (15.5 kg NaOH/t) is only a lower bound. Neither warning appears in the inventory files or in `process.yaml`, so anyone using the dataset would not see it.
- **#2 (low):** The calciner energy rests on two conference papers read only at abstract level, with no page or table reference.
- **#3 (low):** The E-101 heater duty includes heating the bauxite and lime slurry, but stream S8 is still shown at 373 K. The slurry is also counted as starting at 298 K instead of 353 K. The net error is a few MW, under 5 % of the steam.
- **#4 (low):** The formation enthalpies are marked "recalled, not checked" and have no table references. My spot check found them consistent.
- **#5 (low):** The maturity warning is explained in `process.yaml` but stays.
- **#6 (low):** Flowsheet step `T501` links to tag T-502, and step `M501` to T-501. The links are correct, but the names invite mistakes later.
- **#7 (low):** The excluded calciner pollutants and tank vents have no amounts, so the 1 % cut-off can't be checked.

The merge is pending and needs a human or a reviewer, not the author.

VERDICT: merge