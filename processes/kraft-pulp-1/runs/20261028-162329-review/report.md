The branch needs fixes before it can merge: the published climate result (kg CO2-eq per kg of pulp) misstates fossil CO2. I wrote the review to `reviews/2026-10-28-pfd-lci-review.md` and committed it as `60f2d0e`, reviewing HEAD `8412c2e`. It was not pushed.

**What I re-ran myself**
- **`cheme validate`:** 0 errors, 0 warnings. It still says that after adding the review.
- **`cheme check`:** all six concept-stage gates pass. The P&ID, layout and datasheet gates fail, which is normal at this early stage. The `design-review` gate now passes because of this record.
- **`cheme maturity`:** calculation maturity is "none", and it warns that the claimed maturity `concept` is higher than the evidence supports.
- **`cheme process streams`:** every block and step balances.
- **`cheme process propagate --check`:** clean.
- **Balance script:** `scripts/kraft_balance.py` gives the same flowsheet when re-run.
- **`cheme assess lca --coverage`:** a partial screening carbon footprint with 17 gaps. Every gap has a description, and no background value is filled with zero or taken from a licensed database.

I hand-checked the main figures and they look right for a modern bleached softwood kraft mill: 44 % yield, 1.69 t black liquor solids, 913 kWh generated and 650 kWh used, 11.6 GJ process heat and 1.5 GJ kiln fuel, all per air-dry tonne. Nothing outside `processes/kraft-pulp-1/` changed. I found no third-party content copied in.

**Findings (1 high, 2 medium, 8 low)**
- **#1, high:** `lca/results.md`, `results.csv` and `manifest.json` report 0.0499 kg CO2-eq per kg pulp as fossil emissions. The inventory's own fossil CO2 from the kiln's natural gas is 0.0823 kg/kg. The results also show 0.0084 kg of fossil carbon in the pulp, which is all wood carbon. The cause is in core, not this case: it applies the plant-wide 2.1 % fossil share to every CO2 emission instead of each emission's declared origin. Only `DESIGN.md` says this; nothing in `lca/` warns a reader. The fix is to raise it with core and either withhold or clearly caveat the number.
- **#2, medium:** issue #180 asks the run to check core issues #364, #365 and #370 at startup and record the core commit. That wasn't done, yet `DESIGN.md` still names these issues as the reasons the energy balance and the kiln energy calculation were not done.
- **#3, medium:** treating the lime-kiln calcination CO2 as biogenic has no source with a locator.
- **Low (#4–#11):**
  - `process.yaml`'s notes don't state that the calculation maturity is "none".
  - The steam basis per kg of black liquor solids is ambiguous, because the simplified liquor composition is carbon-rich.
  - The heats of reaction were recalled from memory, and for calcination the stated formation enthalpies give 179.0 rather than the 178.3 kJ/mol entered.
  - The 20.7 % energy closure printed by the LCA check is unexplained.
  - The unit basis for the chlorine dioxide and sulfuric acid inputs is ambiguous.
  - Route alternatives (sulfite, soda, mechanical) are not compared.
  - The generated PFD is hard to read.
  - The author edited files with shell commands that `AGENTS.md` forbids. They reported this themselves, I re-checked the content, and I accepted it.

The merge is still pending: a human or the reviewer merges it once #1 is closed.

VERDICT: fix