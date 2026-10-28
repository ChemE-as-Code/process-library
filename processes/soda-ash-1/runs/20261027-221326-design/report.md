The Solvay case is done through a balanced BFD/PFD and a preliminary gate-to-gate LCI, all committed on `case/soda-ash-1` in 5 commits. Nothing is pushed and nothing is signed off. `cheme validate` reports 0 errors and 0 warnings. Every design parameter is assumed, so the numbers are concept estimates rather than sourced data.

## Files produced (in `processes/soda-ash-1/`)
- `process.yaml`: status internal, maturity concept, validation unreviewed, references listed.
- `process/`: design basis, materials, reactions, kiln basis (`furnaces.yaml`), `simulation.yaml` (only declares the kiln, slaker and distiller adiabatic), `flowsheet.yaml`, and the generated BFD/PFD.
- `scripts/solvay_balance.py`: the independent balance every stream comes from.
- Equipment list (12 items) and line list (22 lines).
- `lca/lca.yaml` plus the written inventory, gaps, dataset, results and manifest.
- `DESIGN.md` (decisions D-001 to D-010) and `PROGRESS.md`.
- P&IDs, layout, HAZOP, cost and datasheets were left alone, as scoped.

## Balance, check and LCI results
- **Flowsheet:** 6 blocks, 12 steps, 27 material and 10 energy streams. Every block and step balances.
  - Reaction extents (kmol/h): calcination 410.7, coke combustion 270.3, slaking 410.7, carbonation 782.3, bicarbonate calcination 391.2, distiller reaction 391.2.
  - Element balances close to below 1e-11 kmol/h.
- **Per tonne of soda ash:**
  - Inputs: brine 5.78 t (1.50 t NaCl), limestone 1.08 t, coke 87.6 kg, ammonia 2.0 kg, process water 3.48 t, LP steam 1.88 t, calciner heat (HP steam) 2.43 GJ, electricity 112 kWh.
  - Outputs: distiller waste 11.19 t (1.04 t CaCl2), vent 1.11 t containing 306 kg CO2, cooling water 1.47 kWh of heat per kg.
- **Gates:** `cheme check --stage concept` passes 6 gates. The one failure is the plot plan, which is layout and out of scope.
- **Maturity:** `cheme maturity` says the evidence supports no level, while the manifest claims concept. That is because nothing is sourced; methanol-1 is in the same position.
- **LCI per kg of light soda ash:** 18 foreground exchanges.
  - 10 backgrounds are declared missing, each naming the dataset it should connect to later. Ambient air is free.
  - Vent CO2 (fossil) and NH3 are emissions to air; the distiller waste is a waste sent to settling ponds.
  - The result is labelled "partial screening carbon footprint" with 11 gaps.
  - `cheme assess lca --balance` closes: mass +0.00 %, every element within 0.01 %, carbon by origin closed.
  - Against the flowsheet, 13.299 kg goes in and 13.299 kg comes out per kg of product.

## Sources
- JRC lime BREF 2013, Table 2.23: kiln heat use, taken through cheme's packaged table.
- NBS tables (Wagman 1982): formation enthalpies. I used recalled values, marked ASSUMED until someone checks them against the table.
- Cross-checks only, not design inputs:
  - [EMEP/EEA guidebook, soda ash](https://eea.europa.eu/publications/emep-eea-guidebook-2016/part-b-sectoral-guidance-chapters/2-industrial-processes/2-b-chemical-industry/2-b-7-soda-ash): 200–300 kg CO2 vented per tonne; our 306 kg/t is just above.
  - [USGS 1992 soda ash](https://search.library.wisc.edu/digital/AFYIUSH2IKTZTI8Q/text/ALOUQVPS7OISSP86): 1.7 t salt and 1.4 t limestone per tonne. Our figures are lower, which suggests the assumptions are optimistic.
  - A [secondary review](https://repositorio.ufscar.br/bitstreams/bd70b811-cf1d-471a-a253-22deda182af1/download): 9.7–13.6 GJ/t total energy; ours is about 9.7 GJ/t, the low end.
- The Ullmann chapter and the 2007 large-volume inorganics BREF (LVIC-S) are cited as leads but were not read in this run.

## Key ASSUMED values
- 1000 t/d, 8000 h/a, product 99.5 % Na2CO3.
- Brine 26 wt% NaCl; limestone 96 % CaCO3; coke 89 % C.
- Kiln: 4.0 GJ/t lime, 95 % calcination, air excess 1.10.
- Towers: sodium utilisation 0.73; NH3/NaCl 1.10 mol/mol.
- Cake 15 wt% liquid; wash water 0.3 kg/kg dry cake; ammonia losses 2.0 kg/t; lime 5 % over stoichiometry.
- Compressor efficiency 0.75; auxiliary power 35 kWh/t.

## Missing chemicals registry entries
sodium-carbonate (with a light-ash grade), sodium-chloride or a brine grade, limestone or calcium-carbonate, coke, ammonia, calcium-chloride. Optional internal intermediates: calcium oxide, calcium hydroxide, sodium bicarbonate, ammonium chloride.

## Open inputs and gated steps
- **Kiln energy balance:** it needs Cantera, which won't build for cheme's Python 3.15. My attempt to install it into cheme's tool environment failed and changed nothing. Until then the kiln uses the labelled fallback (a published heat use per tonne of lime).
- **Electrolyte liquors:** core #364 only covers aqueous NaCl, so the absorber, towers and distiller can't be simulated, and the sodium utilisation is specified rather than predicted.
- **Energy balances:** `cheme process energy` can't evaluate any, because no property package covers these liquors and solids. The duties are estimates from my script.
- **Inputs still needed:**
  - Sourced values with exact page or table locators for every parameter in D-006.
  - Kiln emissions: CO, NOx, SO2 and dust are declared excluded, not set to zero.
  - The CaCl2 discharge represented as emissions to water.
  - Site, grid and steam supply, which decide the backgrounds.
  - ISIC/CPC classification for the dataset.

## Recommended next stage
Run a source audit first: record the reaction evidence (salt solubility data, plant figures from the BREF and Ullmann) and replace the assumptions in D-006 with sourced values. Then re-run the kiln once Cantera is available, and map the LCI backgrounds once the site is chosen. A human review and merge of `case/soda-ash-1` is pending; no stage has been signed off.
