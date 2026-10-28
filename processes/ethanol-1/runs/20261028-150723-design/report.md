The concept design for ethanol-1 is finished: a design basis, a BFD/PFD where every block and step balances, and a preliminary gate-to-gate LCI with every background left unmapped. Everything is committed on `case/ethanol-1` in four commits (be0c48d…845488e); the working tree is clean and nothing is pushed. The scaffold commit leaves out the scaffold's `process/` files, the lists and `plant.yaml`; they arrive filled in the second commit.

**Files produced** (all in `processes/ethanol-1/`)
- `process/`: `design-basis.yaml`, `materials.yaml` (7 components), `reactions.yaml` (main hydration reaction, ether and butene side reactions), `catalysts.yaml`, `flowsheet.yaml` (3 blocks, 20 steps, 33 material and 12 energy streams), `simulation.yaml` (only marks the reactor adiabatic), and the generated `BFD.xml` and `PFD.xml`.
- `scripts/balance.py`: my own balance script. It solves the 4 recycle loops to 1e-6 kg/h and estimates the duties.
- The equipment list (14 items) and line list (29 lines, first-pass pipe sizes).
- `DESIGN.md` (source register, decisions D-001 to D-013), `PROGRESS.md`, `process.yaml` (internal, concept, unreviewed).
- `lca/lca.yaml` and `lca/mappings.yaml`, plus the generated inventory, gaps, dataset, results and manifest files.
- I removed nothing from the template; the folder has no P&ID sheet.

**Balance and check results**
- **Validation:** `cheme validate` gives 0 errors and 0 warnings.
- **Balances:** every block and step balance closes. Overall: in 8,076 kg/h ethylene + 8,473 kg/h water = out 12,502 kg/h ethanol + 646 kg/h off-gas + 3,401 kg/h wastewater (16,549.5 kg/h each side).
- **Reactor:** cheme calculates its outlet. The energy balance closes at the adiabatic outlet temperature of 540.9 K (residual −0.3 kW). Hydration reaches 66 % of its equilibrium quotient (ideal gas), so 5 % conversion per pass is feasible.
- **Yield:** 94 % of the ethylene ends up as ethanol product. Recycle gas is 20 times the fresh feed; inerts settle at 7.3 mol% in the loop.
- **Duties:** reactor feed/effluent exchanger 41.1 MW recovered; HP steam 4.6 MW; LP steam 17.9 MW, of which the ethanol concentrating column takes 16.6 MW; cooling water 27.6 MW; power 0.69 MW.
- **Stage gates:** the concept gates pass except the plot plan, which is out of scope.
- **Maturity:** `cheme maturity` stays below the "sourced" and "balanced" levels, as it should. The feed is assumed rather than sourced, the selectivities are assumed, and two separators (the scrubber and the molecular sieve) have no basis source.

**LCI per kg of anhydrous ethanol**

| Exchange | Amount |
|---|---|
| Ethylene | 0.646 kg |
| Make-up water | 0.678 kg |
| Electricity | 0.055 kWh |
| HP steam (as heat) | 0.371 kWh |
| LP steam (as heat) | 1.430 kWh |
| Heat to cooling water | 2.21 kWh |
| Off-gas to site fuel gas | 0.052 kg |
| Wastewater | 0.272 kg |
| Phosphoric acid / caustic soda / catalyst / molecular sieve | 1.0 / 0.82 / 0.15 / 0.06 g |

- All 16 exchanges are declared gaps, each with a description of the background activity it should connect to; `--coverage` rates the result as "partial screening".
- The dataset closes in mass, C, H and O (residual 0.09 kg C/h on 6,915 kg C/h). The consumables' element balance can't be checked (see the core bugs below).
- The library's LCI build runs with no errors and reports 10 gaps for ethanol-1. To get there, I pointed both steam exchanges at the shared `steam-heat` entry in `lca/mappings.yaml`: cheme counts steam in kWh and the registry's `steam` is in kg, so the build refused it otherwise.
- **Defaults to check:** in that build, water, power, cooling water and wastewater are linked through their registry slugs and the library's shared mappings, not left as gaps. So of the 16 exchanges declared missing in `lca.yaml`, the library build counts 10 as gaps.

**Sources used** (facts restated in my own words, locators in DESIGN.md)
- US 4003952: conversion of 4–5 % per pass, diethyl ether as the main by-product, crude ethanol strength.
- US 5349096 (BP): operating window 225–280 °C, 3–10 MPa, water/ethylene 0.15–0.50; test data at 6,895 kPa, 240 → 260 °C.
- US 4329520: seen only in a search summary, not opened; to verify.
- NIST WebBook water vapour pressure; component data via `cheme chemistry thermo`.
- Ullmann's Ethanol chapter: listed but not audited.

**Key assumed values**
- 100,000 t/a at 8,000 h; polymer-grade ethylene (99.9 mol%) delivered at 7,300 kPa.
- Water/ethylene 0.35; reactor inlet 513 K at 7,050 kPa (both inside the patent windows).
- Selectivity 0.97 ethanol, 0.01 ether, 0.005 butenes per mol of ethylene converted.
- Every separator split; purge 0.1 % of the scrubbed gas; wastewater blowdown 10 % of the water loop.
- Concentrating column reflux ratio 3; 93 wt% ethanol to the sieve; 18 % of the sieve feed ethanol returned from regeneration.
- Consumable rates (orders of magnitude; no open source found); compressor efficiency 0.75.

**Missing chemical registry entries** (for the shared PR): ethanol (with an anhydrous grade), ethylene, ethane, diethyl ether, 1-butene, phosphoric acid, sodium hydroxide, a fuel-gas entry, HP and LP steam grades, and the catalyst and 3A sieve consumables. Shared `lci/mappings.yaml` will also need technosphere entries for ethylene, phosphoric acid, caustic soda, the catalyst and the sieve.

**Open inputs and gated steps**
- **Energy closure:** separator, column and exchanger energy can't be evaluated in core; no property package covers ethylene/water/ethanol (core #315).
- **Molecular sieve:** modelled as a fixed split; adsorption is gated by core #368.
- **Fermentation:** noted as the dominant route but not designed; core #365 would gate it.
- **Process inputs still needed:** real selectivities and acid loss rate, catalyst life and volume, product specification (the balance leaves about 170 ppm ether in the product).
- **Core bugs found:**
  - `cheme process build` crashes on a `Pumping` step; I used `TransportingFluids` for the pump instead.
  - A `Heating` step isn't treated as pass-through by `propagate`.
  - The `lca` schema has no `composition` field for consumables, so their element balance can't be checked.

**Recommended next stage**
- Simulate the ethanol concentrating column alone with NRTL in DWSIM; core benchmarks NRTL for ethanol-water. This checks the column's steam use, the largest inventory item.
- Source the selectivities and the acid make-up rate.
- Then link the LCI backgrounds, starting with ethylene.

No merge is pending: the branch is unpushed and not reviewed, and no stage was signed off.

STATUS: DONE