The concept design and the preliminary gate-to-gate LCI are done and committed on `case/hydrogen-1` in three commits (scaffold, flowsheet, LCI). The flowsheet closes in mass, components and elements, and the inventory closes against it. Everything rests on assumed values, so `cheme maturity` reports level none. Nothing is pushed, and a merge is pending: the branch needs review by someone other than me.

**Files produced** (`processes/hydrogen-1/`)
- `process.yaml` (`publication.status: internal`, maturity concept, unreviewed), `plant.yaml`, `process/design-basis.yaml`.
- `process/materials.yaml` (10 components with ideal-gas data fitted over 280–1500 K), `reactions.yaml`, `catalysts.yaml`, `simulation.yaml` (only declares the shift converter adiabatic).
- `process/flowsheet.yaml` with the generated `BFD.xml` and `PFD.xml`: 6 blocks, 25 steps, 46 streams. It includes the hydrogen recycle to desulfurisation, the process condensate recycle, the tail gas as furnace fuel and steam export.
- `scripts/h2_balance.py`: an independent heat and mass balance script, run with `cheme run`.
- `equipment/equipment-list.yaml` with 17 items. The line list is left empty: lines come with the P&IDs.
- `lca/`: `lca.yaml`, `inventory.csv`, `dataset.yaml`, `gaps.csv`, `results.*`, `manifest.json` and a project `README.md`.
- `DESIGN.md` (decisions D-001 to D-014) and `PROGRESS.md`.

**Balance, check and LCI results**
- `cheme validate`: 0 errors, 0 warnings. `cheme process streams`: every block and step is "ok" for mass, components and elements.
- cheme's own equilibrium reactors reproduce the script's reformer and shift outlets to about 5 significant figures.
- Energy as far as core supports it:
  - Reformer duty is 102,026 kW from cheme against 102,025 kW from the script.
  - The furnace gives −102,025 kW to the tubes, so the radiant section balances.
  - The shift converter comes out at 0.03 kW, i.e. adiabatic as designed.
  - Block energy balances can't be evaluated: no core property package covers gas containing water, steam or flue gas (core #315).
- Plant figures from the script:
  - Natural gas in: 455 MW (LHV), which is 180 MJ per kg of hydrogen.
  - Methane slip: 6.1 mol% dry.
  - Carbon in equals carbon out.
- `cheme check`: all concept gates pass except the plot plan, which is out of scope.
- LCI per kg of hydrogen:
  - In: 3.217 kg natural gas feedstock, 0.617 kg natural gas fuel, 15.66 kg demineralised water, 30.89 kg air, 0.164 kWh electricity.
  - Out: 10.55 kg export steam, 0.210 kg blowdown, 3.30 kWh to cooling water.
  - Fossil CO2 at the stack: 10.10 kg, of which 8.47 kg is process CO2 (feedstock carbon) and 1.63 kg combustion CO2 (trim fuel). The two are kept apart by giving the feedstock and the fuel separate natural-gas feeds.
- `--balance`: mass and every element close (largest residual: carbon at −0.01 %).
- `--coverage` classifies it as "partial screening" with 6 deliberate gaps. Each gap names the background activity it should link to later.
- The 10.10 kg CO2-eq shown in `results.md` is direct stack CO2 only, not a footprint of hydrogen.

**Sources used**
- The core reaction library entries `steam_reforming` and `ht_shift` (citing Ullmann's and Twigg, *Catalyst Handbook*, 2nd ed., 1989). I used their stoichiometry and catalyst windows but did not read the underlying texts myself.
- Thermochemical data from ATcT, CRC and thermo via `cheme chemistry thermo`; water and steam from CoolProp (IAPWS-IF97).
- I copied no third-party content and did not look for published answers.

**Key ASSUMED values**
- 100,000 Nm³/h of 99.9 mol% hydrogen at 2850 kPa(a).
- Natural gas: 93 % CH4, 3.5 % C2H6, 0.7 % C3H8, 1.3 % CO2, 1.5 % N2.
- Steam-to-carbon ratio 3.0.
- Reformer 893 → 1143 K at 3.2 MPa, equilibrium approach −10 K.
- High-temperature shift adiabatic from 623 K, approach +10 K.
- PSA hydrogen recovery 0.88.
- Furnace: 10 % excess air, no air preheat, 1273 K leaving the radiant section, 423 K stack.
- Steam at 4.3 MPa and 673 K; blowdown 1 %; hydrogen recycle 0.03 mol per mol of natural gas.
- Machine efficiencies 0.70–0.75.

**Missing registry entries** (for the consolidated PR): natural gas, carbon monoxide, ethane, propane and demineralised water in `chemicals/chemicals.yaml`.

**Open inputs and gated steps**
- **Properties (core #315):** stream enthalpies, flashes and a predictive simulation wait on it.
- **PSA (core #368 / PR #398):** needs a cited or vendor recovery figure.
- **Core bug:** `cheme process build` 0.8.0 crashes on the step classes `Pumping` and `GeneratingSteam`. I worked around it with `GeneratingFlow` and `Evaporating`.
- **LCI items still missing:**
  - Furnace emissions (NOx, CO, CH4/N2O slip, particulates) need sourced factors, so the `lci-emissions-incomplete` warning stays.
  - Consumables (catalysts, ZnO, adsorbents) and construction are not included.
  - The export steam has no allocation or system expansion yet.
  - All backgrounds are unmapped.
- **Sourced inputs:** sulfur content of the natural gas, a sourced gas composition, and a reaction-evidence file with reported methane slips and shift approaches.
- **Feasibility checks:** carbon formation, pinch analysis, and whether a pre-reformer or air preheat pays.

**Recommended next stage:** start with the reaction-evidence search and a sourced natural gas and PSA basis. Then add the furnace emission estimates and map the backgrounds, decide how to treat the export steam, and run sensitivities on steam-to-carbon ratio, reformer outlet temperature and air preheat. After that, move to basic engineering (datasheets, then P&IDs).
