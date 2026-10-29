## sodium-nitrite-1: design basis, balanced BFD/PFD and preliminary LCI (issue #168)

The concept design, balanced BFD/PFD and preliminary gate-to-gate LCI are done and committed. Mass and element balances close everywhere. `cheme maturity` still reports calculation maturity **none**, the same as hydrogen-chloride-1, and every LCI background is left as an open gap. Branch `case/sodium-nitrite-1` has 7 commits (`97dcee7`…`1ebde59`), the tree is clean, nothing is pushed and no stage is signed off.

**Route:** ammonia is burnt with air (10.3 mol-% NH3) over a Pt/Rh gauze at about 1.3 bar. A waste heat boiler cools the gas to 200 °C, and its steam (1.89 MW) runs the first stage of the liquor evaporator. The gas is then absorbed in towers in series with a 20 wt-% soda ash solution. The nitrite liquor goes through a double-effect evaporator, a vacuum cooling crystalliser at 55 °C, a centrifuge and a dryer to give **2,500 kg/h NaNO2 (99.0 wt-%), 20 kt/a**. Most of the mother liquor is recycled; a purge (671 kg/h) is converted with nitric acid to **NaNO3, 399 kg/h, sold as co-product**, and the NO this releases goes back to the absorbers.

**NO/NO2 ratio control:** the share of the nitrogen oxides oxidised to NO2 is held near 0.5, slightly below rather than above, because NO in excess favours nitrite. The handles are the oxidation volume's residence time and temperature, the secondary air, and the NO returned from the nitrate step. The balance gives 0.537, which matches a 20:1 nitrite:nitrate ratio.

### Files produced
- **Process:** `process.yaml` (internal, concept, unreviewed), `process/design-basis.yaml`, `materials.yaml`, `reactions.yaml`, `flowsheet.yaml` (4 blocks, 11 steps, 42 streams), and the generated `BFD.xml` and `PFD.xml`.
- **Balance and lists:** `scripts/balance.py` (an independent mass/energy balance) and `equipment/equipment-list.yaml` (13 items).
- **LCI:** `lca/lca.yaml` and `lca/mappings.yaml` (no active overrides, candidates listed), plus the generated `inventory.csv`, `dataset.yaml`, `gaps.csv`, `results.*` and `manifest.json`.
- **Records:** `DESIGN.md` (route memo, source register, evidence, basis and method tables, decisions D-001…D-013, open inputs, missing registry entries) and `PROGRESS.md`.
- **Unchanged:** the line list is still empty, since the PFD needs none, and there are no P&IDs.

### Results
- **Balances:** `cheme validate` reports 0 errors and 0 warnings. `cheme process streams` shows all 4 blocks and 11 steps OK, with the absorber and nitrate step balanced by elements over their reactions. The plant balance is 13,118.55 kg/h in and out, and N, H, O, Ar, Na and C all close.
- **Burner:** cheme calculates the outlet stream, and its duty (1,964.2 kW) matches the independent script.
- **Gates:** `cheme check` passes 6 of the concept gates; the only failure is the layout plot plan, which is out of scope.
- **Atlas catalog:** `build_catalog.py` builds with this process and gives no warnings for it.

### LCI per kg NaNO2 (after mass allocation, 86.2 % to NaNO2)

| exchange | amount per kg NaNO2 |
|---|---|
| Ammonia | 0.2346 kg |
| Soda ash | 0.7465 kg |
| Nitric acid 60 wt-% | 0.0826 kg |
| Electricity | 0.0654 kWh |
| LP steam | 0.634 kWh |
| Cooling water | 1.898 kWh |
| Surplus condensate | 0.267 kg |
| CO2 (from the soda ash) | 0.310 kg |
| N2O | 4.24 g |
| NO | 2.12 g |

- **Balance check:** the inventory closes in mass and elements, and a hand check against the flowsheet agrees (inputs 4.5246 kg equal outputs).
- **Gaps:** there are 8, all reported and none set to 0. Ammonia, soda ash, nitric acid, electricity, steam, cooling water and condensate have no background yet, and NO has no climate factor.
- **Partial result:** the direct emissions alone give 1.47 kg CO2-eq/kg, 79 % of it from N2O. This is not the product's carbon footprint, because no backgrounds are included.

### Sources
- **Read in full:** US 2 032 699 (absorption in soda solution, liquor and mother-liquor compositions, crystallisation temperatures) and US 12 565 427 B2 (burner feed ratio, gauze temperature and pressure, boiler outlet temperature).
- **From search summaries only:**
  - US 2 013 984 (nitrite converted to nitrate with nitric acid, NO returned).
  - The IPCC 2006 default of 5 kg N2O per tonne of nitric acid for atmospheric-pressure plants, confirmed through an EPA 2013 report and a CDM panel document.
  - NaNO2 solubility points.
- **Tool output:** gas-phase thermodynamic data printed by `cheme chemistry thermo`.
- **Identity only, not read:** the Ullmann chapter.
- **Not verified:** the NBS enthalpies of formation of the dissolved salts are values I recalled. They are flagged in DESIGN.md as to be checked against the tables.

### Key ASSUMED values
- Capacity of 2,500 kg/h.
- NO selectivity 0.97. This is optimistic: US 12 565 427 calculates 92 % for its burner.
- N2O formation of 1.4 % of the ammonia, carried over from the nitric-acid IPCC default.
- NaNO2:NaNO3 of 20:1 by mass; US 2 032 699 reports 40:1.
- 99.5 % of the NOx absorbed. This leaves 670 ppmv NOx in the tail gas with no abatement, which a modern permit would not allow.
- Centrifuge cake liquid 0.05 kg/kg, evaporator economy 1.8, dryer efficiency 0.5, and the electric loads other than the air blower.
- Mass allocation is used because no product prices were found.

### Missing registry entries (for the consolidated PR)
- **Chemicals:** `sodium-nitrite`, `sodium-nitrate`, `ammonia`, `sodium-carbonate`, `nitric-acid` (with a 60 % grade), `nitrous-oxide`, `nitric-oxide`.
- **LCI mappings:** a nitric-acid entry per kg of 60 % solution.
- **Elementary-flow list:** NO to air.

### Open inputs and steps blocked by core
- **Liquor thermodynamics (core #364):** the absorber, evaporator and crystalliser duties are estimates, and cheme cannot check their energy balance. Core supports NaCl–water only, and `props` and `simulate` refuse these streams.
- **Crystallisation (core #365 / PR #395):** core's crystalliser is predictive for a single salt only. This mother liquor holds three salts, so specified splits are kept.
- **Core issue status:** I could not open core #364 or #365 with `gh`, so their state comes from the issue comments.
- **Open inputs:**
  - Burner selectivity and N2O formation.
  - Choice of tail-gas abatement.
  - Solubility data for NaNO2–NaNO3–Na2CO3–water.
  - Product prices.
  - Platinum loss from the gauze, dryer dust and start-up emissions.
  - Confirmation of the NBS values.
- **Checks not run:** `build_lci.py` needs `openpyxl` and pytest is not installed in this environment.

### Recommended next stage
1. Run an independent design review.
2. Choose tail-gas NOx abatement and add an N2O-cutting catalyst scenario.
3. Add a caustic-absorbent scenario.
4. Link backgrounds to ammonia-1, soda-ash-1 and nitric-acid-1 once their registry slugs exist.
5. Rerun the duties when core gains electrolyte support.

A merge is pending: the branch needs review, and a human merges it.

STATUS: DONE