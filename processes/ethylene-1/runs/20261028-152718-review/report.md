I reviewed `case/ethylene-1` at commit `4b05909` and wrote the record to `reviews/2026-10-28-pfd-lci-review.md`. It is committed as `883f27e` and not pushed. No design files were changed, and `cheme validate` still shows 0 errors and 0 warnings with the record added.

**What I re-ran myself**
- **`cheme validate`:** 0 errors, 0 warnings.
- **`cheme process streams`:** every block and step balance closes, and no value is out of date.
- **`cheme process propagate --check`:** nothing to change.
- **`cheme check`:**
  - All the concept-stage process gates pass.
  - The P&ID, layout, datasheet and review gates fail. They were outside this run's scope, but one of them (`layout-plot-plan`) is a concept gate, so it would block a concept sign-off.
- **`cheme maturity`:** the calculation maturity is **none**, and it warns that the `concept` claim exceeds the evidence.
- **`cheme assess lca --coverage`:** a partial screening carbon footprint with 14 gaps, each with a description. Mass, element and carbon balances close.
- **Scope of the change:** nothing outside `processes/ethylene-1/` was touched.

By hand, the plant mass balance closes (971,288 kg/h in, 971,290 kg/h out). I also recomputed these, and each matches the stated value:
- ethane conversion: 70.1 %
- firebox: 611 MW fired at 15 % excess air
- flue CO2: 59.1 t/h
- steam raised: 416 t/h
- compressor power: about 42 MW against the stated 40.6 MW

The route and boundary match the issue. Dropping fuel oil as a co-product is a stated and justified deviation. No third-party content was copied, and the LCI has no zero-filled or licensed background values.

**Findings**
- **#1 (R-01), high:** the headline CO2 figure is labelled wrongly. 0.433 kg CO2 per kg ethylene is the mass-allocated value (ethylene carries 91.6 %), but `process.yaml` line 54 and `DESIGN.md` D-016 and D-018 call it unallocated. The unallocated figure is 0.472 kg/kg. `lca/inventory.csv` is also allocated per kg; only `lca/dataset.yaml` is unallocated.
- **#2 (R-02), medium:** the refrigeration numbers don't hang together. The C2 splitter and demethaniser reboilers are called "heat-integrated", but their duties are missing and nothing is credited against the refrigeration load. As a result the refrigeration machines need 78 MW, about twice the cracked-gas compressor, which is unusual for an ethane cracker.
- **#3 (R-03), medium:** the exported high-pressure steam (2.47 kWh per kg ethylene) carries no burden. The fuel that raises it, and its CO2, are charged entirely to the hydrocarbon products, and the compressor drives are charged as grid power on top. Neither caveat is stated next to the CO2 figure.
- **#4 (R-04), medium:** the `process.yaml` notes don't mention that the calculation maturity is "none" or the maturity warning. `concept` is the lowest level the manifest allows, so the claim itself can't go lower.
- **#5 to #10, low:**
  - the 0.788 kg/kg yield is per kg of fresh feed, not per kg of ethane;
  - an arithmetic slip in the primary-energy comparison in D-018;
  - the CO2 emission's source text says it includes the feed CO2, which actually leaves in the spent caustic;
  - simplifications in the propane recycle coil;
  - an unsourced 3:1 NaOH-to-CO2 ratio;
  - the failing `layout-plot-plan` concept gate.

**Not checked:** I did not re-read the cited BREF tables against the document; I only checked the numbers for plausibility. The separation-train energy balance can't be evaluated until core #315 qualifies a property package for light hydrocarbons. I looked at the PFD only as an overview render.

Merge is pending: the branch has one open high finding, and the author can close it by relabelling the CO2 figure.

VERDICT: fix