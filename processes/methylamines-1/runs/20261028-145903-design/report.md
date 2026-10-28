I've finished the concept stage for methylamines-1: a design basis, a balanced BFD/PFD with all recycles, and a preliminary gate-to-gate LCI per kg DMA. Everything is in 7 commits on `case/methylamines-1`; the tree is clean and nothing is pushed. `cheme validate` reports 0 errors and 0 warnings, and every concept gate passes except the plot plan, since layout was out of scope.

**Files produced**
- `process.yaml`: internal, concept, unreviewed, with references.
- `process/`: `design-basis.yaml`, `materials.yaml` (6 components), `reactions.yaml` (MMA, DMA and TMA formation, each reversible), `catalysts.yaml` (silica-alumina), `flowsheet.yaml` (4 blocks, 13 steps, 23 material and 13 energy streams), `simulation.yaml` (it only marks the converter adiabatic), and the generated `BFD.xml` and `PFD.xml`.
- `scripts/mass_balance.py`: my own balance script, which solves the recycle loop, the five columns and the duties.
- `equipment/equipment-list.yaml` (11 items), `DESIGN.md` (decisions D-001 to D-014, a source register, open inputs O-1 to O-8, a method table, the next stage) and `PROGRESS.md`.
- `lca/lca.yaml` and `lca/mappings.yaml`, plus the generated inventory, gaps, dataset and manifest.

**Design and balance results**
- **Plant:** 8 t/h of anhydrous amines (2.0 MMA, 4.4 DMA, 1.6 TMA), fed with 10,920 kg/h methanol and 3,220 kg/h ammonia. It discharges 6,140 kg/h of wastewater.
- **Converter:** cheme's equilibrium model reproduces my script's converter outlet to six digits. Inlet 625 K, outlet 713 K, methanol conversion 98.9 % per pass.
- **Recycles:** ammonia 842.6, TMA 49.5, MMA 94.8 and methanol 3.9 kmol/h, giving a converter feed of 34.5 t/h.
- **Balances:** every block and step balance closes. In the plant balance mass is 14,140.2 in and 14,140.0 kg/h out, and C, H, N and O each close to under 0.01 %.
- **Energy:** steam 35.8 MW plus about 2.5 MW of reaction heat matches the 38.3 MW rejected to cooling water.
- **Model error:** checked against a published equilibrium point (US 4,485,261: 400 °C, ammonia-to-methanol ratio 2.0), the model under-predicts TMA, 0.37 against 0.43 by weight. This affects the recycle flows and duties, not the net feeds, which follow from stoichiometry.

**LCI per kg DMA (mass allocation over the three amines)**

| Exchange | Amount |
|---|---|
| Methanol | 1.365 kg |
| Ammonia | 0.402 kg |
| Electricity | 0.0033 kWh |
| MP steam | 3.47 kWh |
| LP steam | 1.00 kWh |
| Heat to cooling water | 4.78 kWh |
| Wastewater | 0.768 kg |
| Co-product MMA | 0.455 kg |
| Co-product TMA | 0.364 kg |

- `cheme assess lca --balance` closes mass and every element.
- The coverage report classes the result as "partial screening": 7 unmapped backgrounds, each described in `lca.yaml`, and no impact result is claimed.
- No direct air emissions are modelled. Leaks, vents, storage tanks and combustion are listed as exclusions with reasons; the catalyst, the caustic dosing and a heavier-amine purge are listed as cut-off flows with unknown amounts.
- The library LCI build reports methanol as a gap, as the LCI-gaps ADR intends. The `--strict` build still exits 1 in my environment, because of cut-off and benchmark warnings that hit every process (core's package isn't installed there) plus one allocation warning of ours (under Tooling problems).

**Sources:** five patents read in summary (US 4,485,261, US 4,283,254, US 3,387,032, US 7,435,855, US 2,206,584), plus US 7,309,403 and CN 1229328C from search summaries only. Of the Corbin et al. 1997 review (doi:10.1016/S0920-5861(97)00003-5) I could read only the abstract. Thermo data come from the chemicals/thermo packages via cheme. Ullmann was not accessible. Nothing was copied.

**Key ASSUMED values:** capacity and product split (25/55/20 wt%), N/C ratio 2.0 (mol nitrogen per mol methyl carbon), the 440 °C outlet and 2.2 MPa, perfect (sharp) column splits, reflux ratios, extraction water 1 kg/kg feed, 100 ppm methanol in the wastewater, steam levels, and no by-products. There is no heat integration beyond the feed/effluent exchanger, so the steam figures are upper estimates.

**Missing registry entries (for the consolidated PR):** `methanol`, `ammonia`, `methylamine`, `dimethylamine` and `trimethylamine` in `chemicals/chemicals.yaml`, and a `methanol` entry in `lci/mappings.yaml`. `process.yaml` already uses these slugs and is marked PENDING REGISTRY, so the library's registry check will flag them until they are added.

**Tooling problems to report**
- `cheme process build` crashes on steps of class `Pumping` or `SupplyingThermalEnergy`. I used `ProcessStep` and `Evaporating` instead.
- The `dataset.yaml` that cheme writes leaves out `method: mass`, so the library build warns that the allocation differs from the default.
- I could not open core issues #315 and #364 with `gh`, so their current state is unchecked.

**Gated and open steps**
- Predictive simulation and vapour-liquid equilibrium: no property package covers this amine/ammonia/methanol/water system. This is why `cheme maturity` stops at "balanced".
- `sourced.boundary` fails because the feed flows follow from the assumed capacity.
- Open inputs: equilibrium data across temperatures, the ammonia-TMA azeotrope composition, catalyst space velocity and life, by-products, caustic dosing and product specifications.

**Recommended next stage:**
1. Source equilibrium and azeotrope data and refit the model.
2. Do a pinch / heat-integration study and update the steam figures in the LCI.
3. Select a property method (NRTL with sourced binary pairs) for the columns.
4. After the registry PR, map the backgrounds to the methanol-1 and ammonia-1 datasets.

A merge is pending: the branch needs review by someone other than me, and no stage has been signed off.

STATUS: DONE