I fixed the failed CI check and closed four of the six review findings, in three commits on `case/natural-gas-processing-1`. Nothing is pushed. The review had no critical or high findings, so everything I closed was medium or low. Every change is inside `processes/natural-gas-processing-1/`, and no review or run record was touched.

**CI failure (PR #224), fixed in `e99bec1`.** Two library tests failed because the strict LCI build stopped on this process:
- LP steam was recorded in kWh but linked to the library's steam entry, which counts steam in kg. `lca/mappings.yaml` now points it to the shared `steam-heat` entry, which counts it in kWh.
- Splitting burdens between sales gas and NGL by energy content broke the library's allocation rules unless the reason is recorded. `lca/lca.yaml` now records it: no prices are sourced, so the price-ratio rule can't be used.

The library test suite now passes locally (406 passed), using the same packages as CI.

**Findings closed (`d0f6bee`):**
- **#1 (R-01, refrigeration):** I added a rough enthalpy check of the cold section to DESIGN.md as D-016. It estimates a refrigeration shortfall of about 0.3–2 MW. Covering it would take a propane chiller using up to about 1.5 MW of electricity, which is up to 40 % more than the 3.99 MW in the balance. No chiller is added to the balance; the caveat is now in `process.yaml` and the LCA sensitivity text. The property values in the check are rounded and marked ASSUMED; a real-gas simulation should replace them.
- **#2 (R-02, feed provenance):** The flows and compositions of the raw gas, make-up water and combustion air are now marked `given`, each with its basis. The assumed parts are still named in each source (free water, capacity, excess air). This is recorded as D-015. `cheme maturity` now reaches calculation maturity "sourced", which supports the concept claim, and the over-claim warning is gone.
- **#3 (R-03, fugitive methane):** I recorded a screening amount of 519 t/a (0.1 % of the methane processed, ASSUMED) as a cut-off entry in `lca/lca.yaml`, so the cut-off rule can now be checked against it. This is D-017. It is not added to the inventory, but it would roughly triple the direct greenhouse-gas figure (about 0.020 kg CO2-eq per kg sales gas against 0.0105), and `process.yaml` now says so. The only source cited is Alvarez et al. (2018): methane losses of 2.3 % across the whole US supply chain. I could not confirm the figure for the processing segment alone.
- **#5 (R-05, location):** The LCA location is now `US` instead of `GLO`, and the outputs are regenerated.

The BFD and PFD were rebuilt, and a final commit adds the Response entries to PROGRESS.md.

**Left open (both low):**
- **#4 (R-04):** The Bukacek water-content coefficient still needs checking against a primary or handbook source. I didn't have one I could verify in this session.
- **#6 (R-06):** The sales-gas specification still rests on Wikipedia. No open pipeline tariff has been sourced; it stays on the open-inputs list.

**Re-runs after the changes:**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme check`: the concept and basic process gates pass. P&ID, layout, datasheet and detail gates fail as before; they are outside this stage. `design-review` now fails because the reviewed files changed since the review, so a fresh review is needed.
- `cheme maturity`: calculation maturity "sourced", matching the concept claim.
- `cheme process streams`: every block and step balances.
- `cheme assess lca --coverage`: partial screening carbon footprint, 18 gaps, mass balance closed, publishable.

A merge is pending: the branch needs that new independent review, then a human to merge it.

Sources:
- [Alvarez et al. 2018 (energy.gov copy)](https://www.energy.gov/sites/default/files/2023-12/Ex.%2012.%20Alvarez%202018.pdf)
- [NOAA repository record](https://repository.library.noaa.gov/view/noaa/26223)

STATUS: DONE