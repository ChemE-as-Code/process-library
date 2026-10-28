I reviewed the glycerol-1 case at `0e26ab3`; the branch should not be merged yet. There are two open high findings, three medium and six low. The record is `reviews/2026-10-28-pfd-lci-review.md`, committed as `e67aadf` and not pushed. I changed no design files.

**Checks I re-ran on that commit:**
- `cheme validate`: 0 errors, 0 warnings, both before and after adding the review.
- Every block and step balance closes. `cheme process propagate --check` finds nothing stale.
- `cheme assess lca --coverage` rates the LCI a partial screening carbon footprint. It has 13 gaps, each described, none filled with 0, and no licensed values. Mass, element and carbon-origin balances close.
- `cheme maturity` puts the calculation maturity at none, so the `concept` claim in `process.yaml` draws a warning. `concept` is the lowest level available, and the notes explain the warning honestly.
- `cheme check`: the concept gates pass except the plot plan; the later-stage gates fail because that work has not started.
- Nothing outside `processes/glycerol-1/` changed.

I also recomputed the glycerol, methanol, acid, caustic, salt, water and carbon balances and the main duties by hand. They match.

**High findings:**
- **#1 Wrong feed in the design basis.** `process/design-basis.yaml:17` gives a crude-glycerol composition (63.6 % glycerol, 25 % methanol, 2 % water, soap, NaOH) that the design does not use. The flowsheet and D-004 use 59.8 % glycerol, 29.3 % methanol, sodium methoxide and fatty matter, with no water.
- **#2 The still's vacuum system cannot work as specified.** E-403 is supposed to condense about 204 kg/h of water vapour at 1.5 kPa(a) on cooling water at 298 K. Water only condenses at about 286 K at that pressure. A real still would need steam-jet boosters or chilled water, and that steam or refrigeration is missing from the duties, the energy cross-check and the LCI.

**Medium findings:**
- **#3 Inconsistent temperatures.** At the stated composition the methanol column bottoms would boil near 418–425 K, not 383 K, which is above what the LP steam can reach. The dewatering evaporator at 403 K and 10 kPa(a) would dry the glycerol well below its 5 % water target.
- **#4 Stale equipment list.** Its notes come from an earlier balance; for example the C-201 reboiler is listed at 385 kW against 488.9 kW in the flowsheet.
- **#5 Allocation.** Mass allocation charges 32 % of all burdens, including the crude glycerol, to the recovered methanol. That methanol is the biodiesel plant's own excess passing through. The choice is declared, and no results are published yet.

**Low findings:** a wrong reactor heat comment (65 kW should be about 18 kW), an ambiguous "by difference" statement in D-004, the maturity warning, no methanol vent emissions, a tool-output quirk in `cheme maturity`, and a template leftover in `checks/checks.yaml`.

**Not checked:** I could not open the Thompson & He PDF, so the feed values in D-004 are unverified. I did not read the other sources or render the BFD and PFD.

The merge is pending.

VERDICT: fix