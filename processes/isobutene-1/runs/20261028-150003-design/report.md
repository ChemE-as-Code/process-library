# isobutene-1 (MTBE cracking): concept run report

The balanced flowsheet, the generated BFD/PFD and the preliminary foreground LCI are done and committed. Mass, component and element balances all close. The heat-and-material balance is a hand-specified estimate, not a simulation, because cheme has no property package for this mixture yet. `cheme maturity` therefore reports no level, which is the same as hda-1.

## Files produced
- **Manifest and design basis:** `process.yaml` (internal, maturity concept, unreviewed, notes on what was and wasn't validated) and `process/design-basis.yaml`.
- **Process model:**
  - `process/materials.yaml`: 6 components with ideal-gas data from `cheme chemistry thermo`.
  - `process/reactions.yaml`: 3 reactions, MTBE cracking plus the side reactions to DME and to the C8 dimer.
  - `process/flowsheet.yaml`: 3 blocks, 18 steps, 30 material and 17 energy streams.
  - `process/BFD.xml` and `PFD.xml`, generated.
- **Balance script:** `scripts/ib_balance.py`, an independent balance using set separation fractions, simplified duty estimates and first-pass line sizes.
- **Lists:** `equipment/equipment-list.yaml` (16 items) and `piping/line-list.yaml` (22 lines).
- **LCI:** `lca/lca.yaml` and `lca/mappings.yaml` (unit overrides only), plus the outputs written by `cheme assess lca --write`.
- **Records:** `DESIGN.md` (route and boundary memo, decisions D-001 to D-011, source register, open inputs I-01 to I-08) and `PROGRESS.md`.

## Results
- **Validation:** `cheme validate` reports 0 errors and 0 warnings. `cheme process streams` shows every block and step balanced.
- **Reactor:** extents are 112.27 kmol/h cracking, 1.12 to DME and 0.11 to the C8 dimer. cheme's reactor duty (1970.08 kW) matches the script's 1970.1 kW.
- **Equilibrium:** cheme gives ln K = 6.81 and ln(Q/K) = −3.34 at 553 K. The design's 0.90 conversion is limited by the catalyst, not by equilibrium (equilibrium would give about 0.995).
- **Product and yield:**
  - Isobutene at 6250 kg/h, 99.97 wt%; methanol in the product is 26 ppm(w).
  - MTBE feed is 1.587 kg per kg of product, a 99.0 mol% yield.
  - Methanol co-product is 0.567 kg/kg at 99.55 wt%.
- **Utilities per kg isobutene, before allocation:**

  | Utility | Amount |
  |---|---|
  | MP steam | 1.98 MJ |
  | LP steam | 0.48 MJ |
  | Fired heat | 1.26 MJ |
  | Cooling water | 3.05 MJ |
  | Electricity | 0.0025 kWh |
- **Gates (`cheme check`):** all concept gates pass except the plot plan (out of scope). No sign-off was written.
- **LCI, per kg isobutene, mass allocation (isobutene share 63.1%):**
  - MTBE 1.0004 kg, MP steam 0.347 kWh, LP steam 0.083 kWh, fired heat 0.221 kWh, cooling water 0.535 kWh, power 0.0016 kWh, demineralised water 4.5 g, wastewater 4.9 g.
  - There are 8 gaps, each with a description of the background it should link to.
  - `--coverage` reports the mass, element and carbon-origin balances closed and an energy closure of 0.0%.
  - Unallocated check against the flowsheet: 9960.29 kg/h in and 9960.29 kg/h out.

## Sources
- **US 8,633,345 B2 (Evonik):** the main source. It gives the operating ranges for temperature, pressure, conversion and space velocity, the catalyst type, the reflux ratios and pressures from Example 2, and the effluent composition (Table 11) that set the by-product rates.
- **`chemicals`/`thermo`:** thermodynamic data.
- **CODATA:** heating values.
- **Ullmann (Butenes):** cited for route context only; no numbers taken from it.

## Key assumed values
- Capacity 50 kt/a over 8000 h, at a generic site.
- Pure MTBE feed.
- Reactor at 553 K and 0.9 MPa, conversion 0.90 per pass.
- By-products per kmol MTBE converted: 0.010 kmol DME and 0.001 kmol C8.
- Separation specifications from D-007, notably 2.5 wt% methanol over the isobutene column and 14 wt% methanol in the MTBE recycle.
- Wash water at 0.15 kg per kg of crude isobutene, with a 5% purge.
- Mass allocation (D-011) is my proposal; an LCA practitioner needs to confirm it.

## Registry entries missing (for the consolidated PR)
- `chemicals/chemicals.yaml` needs isobutene, MTBE, methanol, dimethyl ether and diisobutene.
- The shared `lci/mappings.yaml` has no MTBE or methanol entry.
- I could not run the library's LCI build script locally because a Python package (`openpyxl`) was missing, so the mapping overrides are checked by name only.

## Open inputs and gated steps
- **Simulation (core #315):** no qualified property package covers MTBE/methanol/water/C4, so `props --fill` and `simulate --fill` can't run. Predictive simulation and enthalpy-based energy closure are blocked until it is fixed.
- **Not sourced:**
  - A traceable capacity and feed assay.
  - Catalyst life (the catalyst is left out of the LCI, about 3 t/a assumed).
  - Impurities in technical-grade MTBE.
- **Not estimated or not done:** fugitive emissions (they need P&IDs) and heat integration.

## Recommended next stage
1. Rerun the column and wash splits with NRTL/UNIQUAC and sourced binary parameters once core #315 lands.
2. Add the reaction evidence file (`process/reaction-evidence.yaml`) and look for a sourced capacity and MTBE assay.
3. Link the LCI backgrounds, including methanol from methanol-1.
4. Then review the flowsheet and LCI and move to basic engineering.

All work is committed on `case/isobutene-1` (4 commits ahead of `main`, not pushed). A review and a merge by a human are pending.

STATUS: DONE