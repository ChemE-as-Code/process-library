I've written the review record `reviews/2026-10-28-pfd-lci-review.md` for HEAD `97a50b6` and committed it as `56e2023`; nothing is pushed. It has 13 findings: 3 medium, 10 low, none critical or high. The task asked for ids R-01…; the record uses the ids `reviews/README.md` and `cheme validate` require (`2026-10-28-pfd-lci-review#n`), and R-nn = #nn.

**Commands I re-ran myself:**
- `cheme validate`: 0 errors, 0 warnings, including after adding the record.
- `cheme process streams`: every block and step balances; overall 4911.9 kg/h in and out.
- `cheme process propagate --check`: clean.
- `cheme assess lca --coverage`: mass, element and carbon balances close; 11 gaps, each with a description.
- `cheme maturity`: calculation maturity is "none", and it warns that the `concept` claim in `process.yaml` goes beyond the evidence.
- `cheme check`: all concept gates pass except the plot plan; the P&ID, layout and datasheet gates fail because those were out of scope for this run.

**What holds up:**
- **Route and boundary:** the conventional route (roasting with KOH, leach, membrane-cell oxidation, crystallisation, KOH recovery) matches the issue, and alternatives are rejected with reasons.
- **Numbers I recomputed by hand:** stoichiometry, theoretical consumption, Mn and K yields, the cell current and energy balance, and the reaction heats and cell voltages all match what the files report.
- **LCI:** it is per kg of product, and 3.9295 kg in equals 3.9297 kg out. Nothing is zero-filled and there are no licensed values; overrides are only in `lca/mappings.yaml`.
- **Copying and scope:** no third-party content is copied, and nothing outside the process folder changed.

**Medium findings:**
- **#1, roaster fuel too low:** the roaster heat counts only the boiling of water. The KOH arrives as a 50 wt% solution, and the heat needed to separate it from that water is left out, yet the leach step takes credit for that same heat when KOH redissolves. As a result the fired heat is about 25–30 % too low (about 0.99 kWh/kg instead of roughly 1.25).
- **#2, cell efficiency optimistic:** the cells are sized at 1000 A/m², which is the patent's cathode current density, applied as if it were the whole cell's. An 85 % current efficiency together with 90 % conversion per pass at that density is optimistic, so the largest electricity item is probably understated.
- **#3, source locators too coarse:** patent facts are cited only to "Description" or "Claims", not to column and line as the issue asks.

**Low findings:** potassium permanganate crystallising inside the cells contradicts the flowsheet, the filter "wash" uses unrealistically much water, permanganate breaks down in the evaporator, the maturity notes, no main product in the manifest, the H2 emission labelled "fossil", the provenance of the formation-enthalpy data, the dryer step still named `D501`, no table of sourced versus assumed values, and the plot-plan gate not deferred anywhere.

I did not re-read the patents or the NBS tables; that is listed under "Not checked" in the record. A merge is pending: a human has to review and merge the branch.

VERDICT: merge