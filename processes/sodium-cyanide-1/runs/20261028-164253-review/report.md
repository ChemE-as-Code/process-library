I reviewed the sodium-cyanide-1 case at `0000a06` and found nothing critical or high: 2 medium and 5 low findings. The review is committed as `2c9d879` in `reviews/2026-10-28-pfd-lci-review.md`, not pushed. Git warned that the committer name and email were set automatically from the machine; worth checking before you push.

**Checks I re-ran myself:**
- `cheme validate`: 0 errors and 1 warning (the cold converter feed is outside the gauze temperature window).
- `cheme process streams` and `propagate --check`: every block balances and nothing is out of date.
- `cheme check`: the concept-stage gates pass except the plot plan, which was out of scope.
- `cheme maturity`: calculation maturity "none". The `concept` claim in `process.yaml` is the lowest the manifest allows, and the file says so plainly.
- `cheme assess lca --coverage`: a partial carbon footprint with 12 declared gaps, no zero-filled or licensed values, and mass closing at 10.747 kg per kg product.
- Only files under `processes/sodium-cyanide-1/` changed since the branch point.

**What I verified by hand:**
- **Source:** the converter numbers from US 6,596,251 B2 Table 2 run 1 match the patent: O2/NH3 1.15, CH4/NH3 0.98, 62.9 % HCN yield on ammonia, gauze at 994 °C, about 303 kg HCN per h and m² of gauze.
- **Balances:** HCN, NaOH, water, crystalliser cake and carbon all close.
- **Plausibility:** ammonia use (0.437 kg/kg, 78 % overall yield), methane use and the converter gas composition are in the usual range for this technology.
- **Licences:** no third-party tables or passages were copied.

**Medium findings:**
- **#1 Steam export is overstated.** It is reported as 17.8 MW (2.85 kWh/kg) but is really an upper bound. With the source's own feed ratios and yield, the model's converter outlet is 1429 K against the patent's 994 °C gauze, because heat losses aren't modelled. The waste heat boiler and tail gas boiler also have no losses. The export is probably 15–20 % too high. This doesn't change the NaCN footprint now, since all burdens go to NaCN, but it would under the energy or exergy allocation the design intends.
- **#2 Some inputs are missing from the LCI and not listed as gaps:**
  - boiler feed water for about 30 MW of steam (the exported steam is counted only as energy, so its water never enters the inventory);
  - phosphate make-up for the ammonia recovery;
  - the acid that stabilises the refined HCN.

**Low findings:**
- **#3** The neutraliser outlet (0.84 kg NaCN per kg water at 343 K) is above the design's own mother-liquor solubility (0.80), so solids could form before the crystalliser.
- **#4** The stated 1.03 MW power leaves out roughly 1 MW of chiller power for the chilled water.
- **#5** The Pt/Rh gauze is counted as a whole 50 kg charge consumed twice a year, rather than the net metal lost after refining.
- **#6** The design calls the converter-feed warning "accepted", but the acceptance isn't recorded, so it is still a live warning.
- **#7** The LCA tool reports 75.6 % energy closure, which DESIGN.md doesn't mention or explain.

The merge is pending: a human or another reviewer needs to merge `case/sodium-cyanide-1`.

VERDICT: merge