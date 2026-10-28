I reviewed `case/hydroxylamine-1` at `6e550ac` and found 11 issues: 3 medium, 8 low, none critical or high. The review is committed as `311a4d4` in `reviews/2026-10-28-pfd-lci-review.md` and not pushed. Git filled in the commit author from your username and hostname, so check that identity before pushing.

**What I re-ran**
- `cheme validate`: 0 errors and 0 warnings, both before and after adding the review record.
- `cheme check`: all concept gates pass except the plot plan, which is out of scope. The design-review gate failed before this record. The basic and detail gates (P&IDs, layout, datasheets) are not expected at concept stage.
- `cheme maturity`: the evidence supports no maturity level. `process.yaml` claims `concept`, which triggers a warning, but `concept` is the lowest value the schema allows and the file says so openly.
- `cheme process streams`: every block and step balances on mass and reaction extents. `cheme process propagate --check` reports nothing out of date.
- `scripts/has_balance.py` reproduces every stream and duty in the flowsheet.
- `cheme assess lca --coverage`: a partial screening carbon footprint. The 13 unlinked upstream sources are all listed as gaps with a description. Nothing is zero-filled and no licensed database values are used. Mass in equals mass out per kg NH2OH (11.3675 kg).

My own hand checks of the burner and cascade balances, H2 use, product composition, reaction heats and utilities per kg all agree with the design. The yields are plausible for this technology: 84% of the ammonia nitrogen ends up as NH2OH, and the N2O works out to about 7.5 kg per tonne of caprolactam, inside the IPCC default range. Nothing outside `processes/hydroxylamine-1/` changed, and I found no copied third-party content.

**Medium findings**
- **#1, `process/reactions.yaml:15`:** the burner's heat of reaction is given per mol NH3 (−226,600 kJ/kmol). The schema wants it per reaction as written (4 NH3), so the value is 4× too small; its own source note says −906 kJ per 4 NH3. Nothing uses it today, but the burner heat will come out wrong once cheme evaluates reactor heats.
- **#2, the NO emission of 33.7 g per kg NH2OH:** that is about 2 mol% NO in the flue gas, which no permitted plant could vent. It rests on an assumed 30% purge with no abatement and no flammability basis for the loop gas. It doesn't change the CO2-eq number, but it would dominate any acidification or eutrophication result.
- **#3, `lca/results.md`:** the headline reads "per 1 kg PROD … 7.08 kg CO2-eq" with a "total" row. In fact it is only the plant's direct N2O, per kg NH2OH (9.78 kg of solution), not a product footprint. `process.yaml`, where an Atlas page would read it, doesn't say so.

**Low findings:** wrong HNO3 amount in the D-005 text; the condensate route departs from the DOMO patent without a recorded decision; the waste-heat boiler (E-101) lists no steam-side design pressure; tight cooling-water approach on the hydrogenation cascade (R-201); D-001 credits the route to the issue rather than the job brief; a foam-suppression wording slip in D-007; the balance script prints 0 K for one stream; the PFD is very wide.

The task asked for R-01… ids, but `reviews/README.md` and `cheme validate` require `<record>#n`, so I used that format and put the R-number in each finding's text. No stage is signed off. A merge is pending and needs a human or the reviewer.

VERDICT: merge