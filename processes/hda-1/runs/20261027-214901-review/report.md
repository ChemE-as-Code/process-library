I've reviewed the HDA case at commit `9af76cf` and committed the record as `reviews/2026-10-27-pfd-lci-review.md` (`d5ee71c`, not pushed). One finding is high, so the branch needs a fix before it can merge; the merge is pending.

**What I re-ran myself**
- **Validation:** `cheme validate` gives 0 errors and 0 warnings, and still does after the review was added. Nothing outside `processes/hda-1/` changed.
- **Balances:** `cheme process streams` shows every block and step balanced, and `propagate --check` reports nothing.
- **Balance script:** re-running `scripts/hda_balance.py` reproduces every duty and loop result. Examples: reactor outlet 936.8 K, minimum approach in the feed/effluent exchanger 53.1 K, purge fraction 0.1114.
- **Hand checks:** toluene use of 1.241 kg per kg benzene (5 % above the 1.180 the reaction equation requires), the selectivity value, compressor and pump power, the fuel gas mass and heating value, reflux against its minimum, and the steam temperature margins all look plausible for thermal HDA.
- **Maturity:** `cheme maturity` reaches no level, while `process.yaml` claims `concept`. That is the lowest level the manifest allows, and its notes say plainly why the evidence falls short, so the claim is honest.
- **LCI:** it is per 1 kg benzene and mass closes (1.30672 kg in and out). All 10 background links are left open with a description of what to connect, and no licensed values are used.
- **Licences:** I found no copied third-party content.

**Findings**
- **R-01, high:** all 10 LCA contributions are gaps, but `lca/results.csv` still has a `total` row of 0. I ran the library's catalog build (`scripts/build_catalog.py`) and it publishes `climate-change: 0.0` for hda-1, labelled cradle-to-gate. The Atlas would therefore show benzene at 0 kg CO2-eq per kg. Fix: set `lca: {source: none}` in `process.yaml` until a background is linked, and report the 0 total to the tooling.
- **R-02, medium:** the boundary is called "cradle-to-gate" in the LCA files but "gate-to-gate" in DESIGN.md (D-013), `process.yaml` and PROGRESS.md.
- **R-03, medium:** some known omissions appear only in DESIGN.md, not in the LCA files, so the coverage check reports no boundary gap. They are fugitive emissions, the vacuum system of the toluene column (including possible wastewater from it) and the small pumps.
- **R-04, medium:** the whole reactor basis relies on Douglas (1988) "recalled, not read", with no chapter or equation given. The values match standard knowledge, but they are unverified, and the disagreement with Speight's temperature range is unresolved.
- **R-05 to R-12, low:**
  - "~7 MW reaction heat" in DESIGN.md is a unit slip; it is about 1.95 MW, and the conclusion drawn from it still holds.
  - Two streams rise in pressure without a pump step on the flowsheet.
  - Because of a bug in `cheme process build`, the fired heater appears on the PFD as an ordinary heat exchanger.
  - The energy allocation uses gas-phase heating values for liquid products.
  - The fuel gas credit will probably dominate the footprint once backgrounds are linked.
  - The LCA outputs say "public" while `process.yaml` says "internal".
  - A comment in the balance script is out of date.
  - The concept-stage plot plan gate fails, because layout was out of this run's scope.

VERDICT: fix
