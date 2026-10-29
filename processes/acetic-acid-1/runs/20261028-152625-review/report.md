I reviewed the acetic-acid-1 case and committed the record as `reviews/2026-10-28-pfd-lci-review.md` (commit a0c866c, not pushed). It covers HEAD 89e6c44 and changes no design files. There is one high finding still open, so the branch needs a fix before it is merged.

I re-ran all the checks myself:
- **`cheme validate`:** 0 errors, 0 warnings.
- **Mass and element balances:** every block and step closes, and my own hand checks of the CO, N2, CH4, H2, water and propionic acid balances agree.
- **`cheme maturity`:** reaches no level, and warns that the `concept` claim in `process.yaml` is higher than the evidence supports. `concept` is the lowest level the schema allows and the file says so openly.
- **`cheme check`:** of the concept gates, only `layout-plot-plan` fails. The P&ID, layout, datasheet and design-review gates of the later stages also fail, which is expected for this run.
- **`cheme assess lca --coverage`:** classed as partial, with 8 gaps; balances close; nothing filled with zero and no licensed values.

Scope matches issue #128, nothing outside `processes/acetic-acid-1/` changed, and I found no copied third-party content. The numbers are plausible for this route: 99.1 % yield on methanol, 96.7 % on CO, and by-products at about 1 % each, taken from the cited patent.

The brief's R-01 to R-10 appear in the record under the ids the repository requires (`2026-10-28-pfd-lci-review#1` to `#10`).

| id | severity | finding |
|---|---|---|
| R-01 | **high** | The flash drum V-102 is described as adiabatic, but its specified split cannot happen without added heat. Using the design's own constants (my check script is `build/review_flash.py`), it needs 11.2 MW that nothing supplies. `scripts/balance.py` combines the reactor and flash into one cooling duty (6.6 MW), which hides the gap, and the plant-wide energy check in DESIGN.md D-008 cannot catch it. The steam figure in the LCI (0.452 kWh/kg) is short by roughly 40 %. |
| R-02 | medium | `process.yaml` lists H2, N2 and CH4 (trace components of the CO gas) as the only feedstocks; methanol and CO are missing because the chemicals registry lacks them. |
| R-03 | low | A source registered as unread (Jones 2000) is still cited as a reason in decisions D-003 and D-004. |
| R-04 | low | The reactor feed is given as 403 K; mixing the incoming streams gives about 379 K. |
| R-05 | low | The decanter's "aqueous" phase is about 70 wt% methyl acetate, and the phase split is not checked. |
| R-06 | low | DESIGN.md says 9 gaps; the tool reports 8. |
| R-07 | low | The `concept` maturity claim triggers the warning above. |
| R-08 | low | The concept gate `layout-plot-plan` fails. |
| R-09 | low | `lca.yaml` says cradle-to-gate while DESIGN.md and the dataset say gate-to-gate. |
| R-10 | low | The generated LCI results print a total of 0 with an interval of 0 to 0, which reads as a zero footprint when every contribution is a gap. |

A merge is pending; it needs R-01 fixed in its own commit, then a new review.

VERDICT: fix