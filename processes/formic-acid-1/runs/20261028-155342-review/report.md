I've reviewed formic-acid-1 at commit `581976e`, written the record as `reviews/2026-10-28-pfd-lci-review.md` and committed it as `2b37c46`. Nothing was pushed and no design file was changed.

**What I re-ran myself:**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme check`: every concept gate passes except the plot plan, which is outside the issue's scope. The design-review gate now passes with this record, marked "agent-reviewed only".
- `cheme process streams`: every block and step balances; the largest residual is 0.01 kg/h.
- `cheme process propagate --check`: nothing out of date.
- `cheme assess lca --coverage`: the mass, element and carbon balances close (1.3009 kg in and out per kg of product). There are 11 gaps: 8 inputs and utilities not yet linked to any upstream data, each with a description, and 3 emissions the climate method has no factor for.
- `cheme maturity`: reaches no calculation level, so it warns that the `concept` claim is too high. `concept` is the lowest level allowed, and DESIGN.md says this.
- Nothing outside `processes/formic-acid-1/` changed. A plain diff against `origin/main` lists other processes only because main has moved on since the branch started.

**My own arithmetic:** CO yield 92 %, water use 0.483 kg/kg, CO2 72.4 g/kg, hydrolysis 28.9 % per pass (just short of the sourced equilibrium constant), the formic acid recycle loop, the catalyst make-up, and the compressor and pump power all check out. The two-column concentration across the azeotrope works in the right direction. Patent facts are restated in the design's own words with section-level references; I found no copied tables and no licensed values.

**Findings: no critical or high, 1 medium, 6 low.**
- **R-01 (medium):** the column that takes water off the dilute acid (C-301) uses 34 % of the steam, with an assumed reflux ratio of 1.0 that was never checked against the minimum reflux. Near the azeotrope the separation is hard, so the steam figure (3.64 kWh/kg) could be too low as well as too high. It is not the conservative upper bound DESIGN.md calls it.
- **R-02:** the hydrolyser feed preheater duty is worked out from 330 K in the balance script but 340 K in the stream table and DESIGN.md (0.32 MW difference).
- **R-03:** CO dissolved in the reactor liquid is ignored. I estimate about half the vent CO would leave through the methyl formate column's condenser instead of the separator vent. Total CO2 is unchanged if that vent also goes to the oxidiser.
- **R-04:** `process.yaml` does not tell readers that `cheme maturity` reaches no calculation level.
- **R-05:** one patent, US4299981, is quoted with its water/ester ratio range the wrong way round compared with the design. Its full text was not read, and it is the only source for the 95 % approach to equilibrium.
- **R-06:** DESIGN.md D-012 wrongly says the stoichiometric CO figure (0.517 kg/kg) is the amount at 92 % yield.
- **R-07:** the emissions left out of the inventory have no amounts, so the 1 % cut-off cannot be checked.

The merge is pending and is for a human or the reviewer to do, not the design's author.

VERDICT: merge