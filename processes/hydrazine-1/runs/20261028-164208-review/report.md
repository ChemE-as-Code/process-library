I've reviewed the hydrazine-1 concept PFD and preliminary LCI at `ff431c6`. There are no critical or high findings, so the branch can be merged; it has 2 medium and 7 low findings. The review record is `reviews/2026-10-28-pfd-lci-review.md`, committed as `ed902da` and not pushed. I changed no design files. `cheme validate` gives 0 errors and 0 warnings with the record included, and the pre-commit hook passed.

**What I re-ran myself:**
- **`cheme validate`:** 0 errors, 0 warnings.
- **`cheme check`:** every concept and basic process gate passes. The gates that fail are for P&IDs, layout, datasheets and the design review itself, none of which belong to a concept PFD/LCI.
- **`cheme maturity`:** calculation maturity "none", with a warning that `process.yaml`'s claim of "concept" goes beyond the evidence. `process.yaml` says this openly, and "concept" is the lowest level the schema allows.
- **`cheme process propagate --check`:** nothing stale.
- **`cheme process streams`:** all 4 blocks and 11 steps balance.
- **`cheme assess lca --coverage`:** mass, element and carbon balances close. There are 16 gaps, each with a description of the background it needs, and no licensed values.

**Checks by hand:**
- **Stoichiometry:** all six reactions balance and reproduce the stated reaction rates.
- **Balances:** ammonia, hydrazine and the hydrolysis water loop all close, and the boundary is 6 888.4 kg/h in and out.
- **Inputs per kg hydrazine:** 1.255 kg H2O2 and 1.128 kg NH3.
- **Steam:** about 13 kg per kg hydrazine hydrate.
- **Key source:** I fetched US 6,605,265 Example 1, the largest LCI driver, myself. Its flows and the 10 500 kg/h of regeneration steam at 18 bar(a) match DESIGN.md.
- **Copied content:** none found.
- **Changes outside the folder:** none since the branch point. The branch is behind main, though, so it needs main merged in before it goes in.

**Medium findings:**
- **#1:** the hydrolysis column steam (C-401) is a hand estimate that DESIGN.md itself calls a lower bound. It still enters the LCI as a single central value, with no scenario showing the higher case.
- **#2:** the reactor and decanter vent is about 59 mol% oxygen and carries MEK and ammonia vapour. No decision on inerting or a nitrogen sweep is recorded. A sweep would also change the vent mass and the LCI.

**Low findings:**
- **#3:** the 85 % azine yield is conservative against the patent's continuous example (about 95 %), and no LCI scenario covers it.
- **#4:** the H2O2 feed is counted as kg of 70 % solution; this needs saying so a later background mapping doesn't get it wrong by a factor of 0.7.
- **#5:** the reactor cooling estimate treats all ammonia as gas, so calling it a lower bound isn't shown to hold.
- **#6:** the maturity warning above.
- **#7:** the NIST formation enthalpies have no per-value locator.
- **#8:** the equipment list points to the wrong open item (I-06).
- **#9:** the generated `lca/results.csv` shows a total of 0 kg CO2-eq even though every contribution is a gap. This comes from the `cheme` tool, not the design, and needs reporting there.

I did not render the generated BFD/PFD drawings, re-run `scripts/balance.py`, or re-fetch the other patents; the record lists these under "Not checked". The merge is pending.

VERDICT: merge