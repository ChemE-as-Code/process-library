I've reviewed the branch at `bfcbb6a`. The record is `reviews/2026-10-28-pfd-lci-review.md`, committed as `73e8de6` and not pushed. It has 8 findings, none critical or high: 1 medium and 7 low.

**What I re-ran myself**
- **`cheme validate`:** 0 errors and 1 warning. The warning is that the reactor feed enters at 399 K, below the catalyst's temperature window. The design accepts it with a reason (the feed heats up in the inert section at the tube inlet), and that reason holds.
- **`cheme check`:** every concept and basic process gate passes. The failing gates are P&IDs, layout, datasheets and the design review, all outside this run's scope.
- **`cheme maturity`:** calculation maturity is none. It warns that the claimed design maturity (concept) is higher, but concept is the lowest value the manifest schema allows, so the claim can't be lowered.
- **`cheme process streams` and `propagate --check`:** all 4 blocks and 9 steps balance; propagate has nothing to change.
- **`cheme assess lca --coverage`:** partial screening with 14 gaps, mass balance closed, written files current.

**Hand checks**
- **Numbers match the flowsheet:** yield 93.0 %, 1147 kg methanol per t formaldehyde, formalin at 50.0 wt%, oxygen 6.0 % in the off-gas, blower about 1.58 MW (1.61 MW in the flowsheet), and carbon in = carbon out.
- **Duties are consistent:** reactor, emission-control oxidiser and absorber cooling all agree with the reaction and sensible heats.
- **Plausible for this technology:** 169 kWh/t electricity, about 1.7 t steam export per t, and stack emissions within the EU emission limits.
- **LCI is correct per kg formalin:** amounts follow from the flowsheet, nothing is zero-filled, and no licensed values are used. Every unmapped background is a described gap, and the one override is in this folder's `lca/mappings.yaml`.
- **Sourcing and boundary:** sources carry locators, estimates are marked ASSUMED, nothing is copied from third parties, and nothing changed outside `processes/formaldehyde-1/`.

**Findings**
- **#1, medium:** the exported steam's allocation is chosen without saying so. DESIGN.md says it is "left open", but the generated results put 100 % on the formalin, labelled "mass". The library rule asks for energy or exergy allocation, documented per process, as nitric-acid-1 does. By my rough estimate, energy allocation would move about 19 % of the burden onto the steam.
- **#2–#8, low:**
  - The 0.051 kg CO2-eq headline in `lca/results.md` is only the direct stack CO2, and the file doesn't say so.
  - `process.yaml` doesn't state that the calculation maturity is none.
  - Two header comments in `flowsheet.yaml` contradict the data and DESIGN.md D-009.
  - PROGRESS.md has the wrong step count and misses one commit.
  - DESIGN.md repeats the whole LCI table, which will go stale.
  - The catalyst window in `catalysts.yaml` is marked "given" but includes an assumed pressure bound.
  - The iron fraction assumed for the reactor catalyst looks low.

**Not checked:** I didn't re-read the EU and EPA documents against their cited pages, re-run the balance script, or re-run the library LCI build. The heat of solution of formaldehyde, the biggest term in the cooling duty, is still unsourced; that is already listed as an open input.

A merge is pending: a human or the reviewer has to merge `case/formaldehyde-1`, not its author.

VERDICT: merge