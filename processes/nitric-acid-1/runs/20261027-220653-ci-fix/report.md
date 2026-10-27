I fixed the CI error this folder controlled, but CI will still fail. With allocation fixed, the library's strict LCI build now stops on five unmapped flows, and those can only be added outside `processes/nitric-acid-1/`. The review had no critical or high findings; I closed the four medium/low ones that needed a change. Three commits are on `case/nitric-acid-1`, not pushed.

**Why CI failed:** the library's LCI export refuses `allocation: substitution` in `lca/dataset.yaml`. Allocation is now `shares`: all burdens go to the acid, and the exported HP steam leaves with no burden and no credit. The departure from the library's rule (energy or exergy for exported steam) is recorded in the file with its reason. Neither method works here: the acid has no energy content, and no property package can give the acid's exergy. The system model is now `cutoff`. Commit d2f0e57.

**Still blocking CI:** I ran the strict build locally. It rejects:
- `feed:NH3`: the chemicals registry has no ammonia entry.
- `feed:LPS`: the library's `steam` mapping is per kg, this exchange is per kWh.
- `emission:NO`, `emission:HNO3` and `consumable:pt-rh-gauze-loss`: no entries in `lci/mappings.yaml`.

The build exports every `lca/dataset.yaml` and has no way to accept an unmapped flow, so these need entries in `chemicals/` and `lci/mappings.yaml`. I recorded this as open input O-6 in DESIGN.md.

**Findings closed:**
- **#1 (medium):** the Pt/Rh gauze loss is now in the LCI as a flow with no background yet. Its amount, 0.15 g/t HNO3 (50 kg/a), is my own marked ASSUMED estimate, not from a source. The gauze service and the two other catalysts are listed as cut-off entries with unknown amounts. The Pt loss now appears in `gaps.csv` (10 gaps).
  - **Side effect:** the LCI's element balance went from closed to "not assessable", because the tool gives the Pt entry no composition. The mass balance still closes. This is noted in D-014 as something to raise with cheme-as-code.
- **#2 (medium):** `lca.yaml`, D-014 and `process.yaml` now say cradle-to-gate with every background open. They also say 0.68 kg CO2-eq/kg is the plant's direct N2O emission only, not the product's footprint. (d2f0e57)
- **#3 (medium):** the PFD layout is pinned left to right (feed preparation → oxidation → absorption → tail-gas treatment → stack) and rebuilt. I looked at the rendered sheet; the long lines left are real recycles. (282ae69)
- **#4 (low):** the maturity printout's overstatement for V-101 is recorded in D-012 as a tool issue to report. (e1679a6)
- **#6 (low):** the LCA schema's scenarios can only swap factors, not change an emission amount, so the unabated case can't be a scenario. The LCA goal now quotes it (7.0 vs 2.5 g N2O/kg, 1.91 vs 0.68 kg CO2-eq/kg) and cites D-009.

**Left open:** #5 (low): `maturity: concept` stays with its disclosure, as the review allowed, because it is the lowest value the schema permits.

**Re-runs after the changes:**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme check`: the concept gates pass as before. `design-review` now fails as stale, because the files the review covered have changed, so it needs a fresh review.
- `cheme maturity`: level none, the same as before.
- `cheme process streams`: every block and step closes.
- `cheme assess lca --coverage`: partial screening carbon footprint, 10 gaps, publishable.

Response entries for the CI fix and #1–#6 are in PROGRESS.md. A merge is pending: the branch needs the library mapping work for green CI and a new review.
