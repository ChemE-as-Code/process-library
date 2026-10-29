The review of `case/thf-1` at 4a44d70 is committed as `reviews/2026-10-28-pfd-lci-review.md` (commit 72981cc, not pushed). It has 9 findings, 1 medium and 8 low, and none critical or high. I changed no design files.

**What I re-ran myself:**
- **`cheme validate`:** 0 errors, 0 warnings.
- **`cheme check`:** the concept-stage gates I expected to pass do pass. `layout-plot-plan` fails, but layout was out of this run's scope. The basic-stage gates fail because there are no P&IDs, layout or review yet.
- **`cheme maturity`:** no level is reached, and it warns that the `concept` claim is higher than the evidence supports. `concept` is the lowest value the schema allows, and `process.yaml` explains the gap honestly.
- **`cheme process streams` and `cheme process propagate --check`:** every block and step balance closes, and nothing is out of date.
- **`cheme assess lca --coverage`:** 8 gaps, each with a description of what it should link to. The mass, element and carbon balances close, and the data quality score is 2.33.
- **Scope:** every changed file is inside `processes/thf-1/`.

**Hand checks:**
- **Feed and yield:** 87.90 kmol/h of BDO (1,4-butanediol) gives a yield of 0.9856 mol/mol. The water of reaction balances (1564.7 kg/h formed, 1564.6 kg/h leaving), and the bleed's heavies match the side-reaction rate exactly.
- **Distillation columns:** the THF balance around the high-pressure column closes, and the azeotrope compositions are plausible.
- **Energy:** the main duties and the pump power agree with my rough estimates. Steam is 3.6 MJ per kg THF, which is plausible for this technology.
- **LCI per kg THF:** mass in and out is 1.26777 against 1.26776 kg. No value is set to zero and no licensed data is used.
- **Patent:** a spot-check of US 9284289 B2 confirmed the operating ranges used for the reactor.
- **Licences:** I found no copied third-party content.

**Findings:**
- **#1 (medium):** the design's own thermodynamic model predicts two liquid phases in the range where the low-pressure column's stripping section runs. The column duties were calculated assuming one liquid phase. The design lists this as open input I-04, but neither decision D-007 nor `process.yaml` mentions it.
- **#2 to #9 (low):**
  - Both columns sit at an assumed reflux floor of 0.3, so most of the steam figure comes from an assumption rather than a calculation.
  - About 25 kW of known small-pump and agitator power is cut off. That is four times the electricity the LCI includes.
  - The maturity warning above.
  - The steam-side design pressures of E-206 and E-202 break the design's own rule.
  - The reactor bleed carries no dissolved THF.
  - Two citations of the patent may be wrong: "the 500 L example" and "17-327 ppm".
  - The catalog entry is missing the main feed and product, because the chemicals registry has no entries for them yet.
  - Two template comments cite decision ids that don't exist, which `cheme validate` reports on every run.

The merge is pending: by the rules of this folder, a human or the reviewer merges the branch, not its author.

VERDICT: merge