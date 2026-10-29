I reviewed bromine-1 at `84c088c` and committed the record as `reviews/2026-10-28-pfd-lci-review.md` in `d58b523` (not pushed). No critical or high findings: three medium and three low.

**What I re-ran myself:**
- **`cheme validate`:** 0 errors, 0 warnings.
- **`cheme check`:** the six concept gates pass. The plot-plan gate fails because layout is outside the issue's scope.
- **`cheme maturity`:** calculation maturity is "none". It also warns that the `concept` claim in `process.yaml` goes beyond that.
- **`cheme process streams`:** every block and step balances.
- **`cheme process propagate --check`:** nothing reported.
- **`cheme assess lca --coverage`:** a partial screening result with 10 gaps, each described. Mass and element balances close.
- **`scripts/balance.py`:** reproduces every stream value in the flowsheet.

**Checked and fine:**
- **Route and boundary** match issue #136.
- **Nothing outside `processes/bromine-1/` changed.**
- **Hand checks:** chlorine (0.5705 kg/kg), bromine recovery, lime, the brine charge balance, the tower water and energy balances, the condenser duty, pump power and drying acid all add up.
- **Source facts:** I re-read US 4 719 096, and the cited figures are in it: chlorine 0.55–0.60 lb/lb, steam 5.2–5.7 lb/lb, tail brine 50–200 ppm bromide, recovery 95–96 %. The model's steam is 2 % above that range, and the design says so.
- **LCI:** per kg of product and consistent with the flowsheet (249.932 kg in = out). There are no zero-filled or licensed values, every background is a described gap, and nothing third-party is copied.

**Findings:**
- **R-01 (medium):** the tail brine drops from 382.59 K to 375 K across the neutraliser T-107 with no duty or vent. Neutralisation should warm it slightly. If the drop is meant as a flash, about 9 t/h of water vapour is missing from the mass balance and the LCI.
- **R-02 (medium):** the neutralised brine leaves at 300 kPa(a) from a tank designed for 0.5 barg. That needs a transfer pump of about 50–60 kW, which is neither in the equipment list nor in the power figure. The plant's electricity is about 40 % low.
- **R-03 (medium):** the published `validation.notes` in `process.yaml` never says that the evidence supports no maturity level. That is only in a YAML comment, which is not published.
- **R-04 (low):** the formation enthalpies behind the heats of reaction were recalled rather than re-read, and have no table or page locator. My own recollection agrees with every value, and the arithmetic is right.
- **R-05 (low):** the brine's sodium content and how close it sits to salt saturation are not stated; both depend on the assumed calcium. The steam result's sensitivity to the assumed heat capacity is not given either.
- **R-06 (low):** the bromine taken from the ground brine is not a separate resource exchange in the LCI. The six emission exclusions have no amounts, so the 1 % cut-off cannot be checked.

Not checked: US 4 725 425, the Arkansas Geological Survey page and the Wikipedia pages (I only re-read US 4 719 096). Speciation and salt saturation can't be checked because no property model covers this brine. P&IDs and layout don't exist yet.

The merge of `case/bromine-1` is pending.

VERDICT: merge