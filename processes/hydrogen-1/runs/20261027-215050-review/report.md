I've written the review in `reviews/2026-10-27-pfd-lci-review.md` and committed it as `1da21a1` (not pushed). It reviews commit `84db928` on `case/hydrogen-1` and has 8 findings: none critical or high, 2 medium and 6 low. I changed no design files.

**What I re-ran myself**
- **Validation:** `cheme validate` gives 0 errors and 0 warnings, both before and after adding the review.
- **Balances:** `cheme process streams` shows all 6 blocks and 25 steps balanced, and `propagate --check` has nothing to change.
- **Balance script:** `cheme run scripts/h2_balance.py` reproduces every flow, duty and the CO2 split quoted in the design notes and the LCI.
- **`cheme maturity`:** level none, with a warning that `process.yaml` claims more than the evidence supports (R-03).
- **`cheme assess lca --coverage`:** "partial screening", with 6 deliberately unmapped background gaps. Mass, element and carbon balances close.
- **`cheme check`:** the plot plan, P&IDs, layout and datasheets gates fail. All of those were outside this run's scope (R-08).

**Hand checks**
- **Steam and hydrogen:** the steam-to-carbon ratio is 3.00, and the hydrogen made matches the PSA feed within 0.1 %.
- **Water and air:** water closes, and excess air comes out at 10 %.
- **Duties:** the steam drum, E-201, the convection section, fans and pump all agree with steam tables.
- **Overall energy:** an energy balance on a lower-heating-value basis closes to about 0.5 MW in 457 MW.
- **Plausibility:** the figures are plausible for a steam-exporting reformer by general engineering knowledge:
  - 6.1 % methane slip and 0.88 PSA recovery;
  - 0.45 m³ natural gas per m³ hydrogen, which is about 12.9 GJ per 1000 m³ once the export steam is credited;
  - 10.1 kg CO2 per kg hydrogen at the stack.
- **Licences and sources:** I found no copied third-party content and no licensed or zero-filled background values. Every assumed value is marked as such and nothing outside `processes/hydrogen-1/` changed.

**Medium findings**
- **R-01:** the export steam (10.55 kg per kg hydrogen) gets no allocation, so `lca/results.md` puts all 10.10 kg CO2 on hydrogen. The README and design notes say this, but `results.md` read alone does not.
- **R-02:** unburnt methane, CO, ethane, propane and hydrogen are exported as "0 kg, calculated" instead of emission estimates or declared exclusions. NOx and N2O are missing. The climate effect is negligible.

**Low findings**
- **R-03:** the maturity claim exceeds what `cheme maturity` supports. The manifest explains why: `concept` is the schema's lowest level.
- **R-04:** the economizer coil description in D-010 doesn't match the coil order in the script.
- **R-05:** the plant figures are not compared with a cited benchmark.
- **R-06:** the condensate stripper vent is missing from the LCI's open items.
- **R-07:** natural gas is registered as methane in `process.yaml`.
- **R-08:** the out-of-scope gates listed above.

The brief asked for finding ids R-01 to R-08. `cheme validate` only accepts ids of the form `<file name>#n`, so the record uses `2026-10-27-pfd-lci-review#1` to `#8` with the R labels in the finding text.

Not checked: I didn't render or look at the generated BFD and PFD, didn't re-read issue #117 itself (I took the scope from the run's task file), and couldn't verify the reference details without network access.

A merge is pending: a human or the reviewer must merge the branch, not its author.

VERDICT: merge
