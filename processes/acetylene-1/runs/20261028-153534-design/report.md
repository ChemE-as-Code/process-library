I built the acetylene-1 concept case on branch `case/acetylene-1`: a balanced BFD/PFD, a preliminary gate-to-gate LCI and the design documentation. Everything is committed in 8 commits, nothing pushed, working tree clean. `cheme validate` shows 0 errors and 0 warnings.

## Files produced
- **Process model:** `process/flowsheet.yaml` (5 blocks, 26 steps, 61 streams), `materials.yaml`, `reactions.yaml` and `simulation.yaml` (marks the burner, quench and cooling column adiabatic). BFD/PFD built with `cheme process build`. `process/design-basis.yaml` holds the basis.
- **Independent balance:** `scripts/balance.py` computes the burner extents, quench water circuit, compression, solvent (NMP) recovery with its recycle, fired heater and all duties.
- **LCI:** in `lca/`: `lca.yaml` and `mappings.yaml` (one override: steam counted in kWh uses the shared `steam-heat` entry, as hda-1 does), plus the generated inventory, dataset, gaps, manifest and results.
- **Documentation:** `process.yaml` (internal, concept, unreviewed), `DESIGN.md` (source register, decisions D-001 to D-014, method/dependency table, open inputs), `PROGRESS.md`, README, and an equipment list of 19 tags. No line list: there are no P&IDs yet.

## Results
- **Balances:** every block and step closes in `cheme process streams`.
- **Burner:** cheme solves the burner from its conversions and reproduces the script (acetylene mole fraction 0.055612 in both).
- **Checks against the patents** (results, not inputs):

| quantity | this design | patent |
|---|---|---|
| O2 / natural gas | 0.602 vol/vol | 0.58–0.75 (US5824834A examples) |
| flame temperature | 1970 K (adiabatic) | about 1700 °C (US8975460B2) |
| quench-water purge | 2.72 kg/kg | 2.67 m³/t (US5824834A) |
| soot sludge | 0.46 kg/kg | 0.44 kg/kg (US5824834A) |

- **Product:** acetylene 99.55 mol%; 98.0 % of the acetylene formed reaches the product.
- **Energy:** core's fired-heater duty (25.8 MW to a 433 K stack) is consistent with the 23.0 MW used plus 10 % casing loss. My plant-level energy check closes within about 0.3 %, once the latent heat of the reaction water condensed in the quench is counted.
- **Gates:** all 6 applicable concept checks pass; the plot plan fails (out of scope). `cheme maturity` reaches no calculation level, the same as phosgene-1, because feeds, conversions and separator splits are assumed.
- **LCI per kg acetylene, unallocated:**
  - Inputs: natural gas 4.73 kg, oxygen 5.58 kg, NMP 2.0 g, electricity 1.52 kWh, MP steam 1.10 kWh.
  - Heat to cooling water: 17.7 kWh. 82 % of it is quench heat, which is not recovered.
  - Outputs: syngas co-product 5.76 kg, purge water 2.70 kg, soot sludge 0.46 kg, fossil CO2 to air 1.19 kg.
- **LCI balance:** mass closes (+0.99 of 98,416 kg/h), and C, H, N, O, Ar and carbon origin all close.
- **LCI coverage:** `--coverage` classifies it as a partial screening carbon footprint with 15 gaps. All backgrounds are deliberately unmapped; no impact numbers are claimed.
- **Library build:** the strict LCI build (`build_lci.py --strict`) over the whole library passes, with acetylene-1's 10 gaps exported unlinked. The catalog build also succeeds.

## Sources
All are BASF patents, read in full text online and used as facts only:
- **US8975460B2:** cracked-gas composition, 600 °C preheat, flame temperature.
- **US5824834A:** feed ratios, acetylene-to-soot ratio, process water.
- **US11459281B2:** quench temperature, dissolved gases in the quench water, 99.31 % removal by vacuum degassing at 400 mbar.
- **US10059640B2:** NMP washing and stripping conditions, solvent loading, 1.4 bar acetylene partial-pressure limit.

The Ullmann chapter and Zhang 2022 were not read (licensed; site down), and the MDPI mechanism paper was not accessible. No value from them is used.

## Key ASSUMED values
- Capacity 6250 kg/h (50 kt/a at 8000 h).
- Feed gas 98 % CH4; oxygen 99.5 %.
- Higher hydrocarbons split 0.7 diacetylene / 0.3 benzene; residual O2 0.1 %.
- Compression to 11 bar(a).
- NMP recovery splits, solvent loading 20 Nm³/m³, 3 wt% water in lean solvent, NMP loss 2 g/kg.
- Desorption heat 25 kJ/mol.
- Fired heater: 85 % efficiency, 10 % natural-gas support fuel.
- Allowances for the precipitator and vacuum pump.
- Energy (LHV) allocation gives acetylene only 27.0 % of the burdens; mass allocation would give 14.8 %, and economic allocation (reportedly used by Zhang 2022) much more. This choice moves the result by a factor of two or more and needs deciding with the study's goal.

## Missing registry entries (for the consolidated shared-files PR)
- `chemicals/chemicals.yaml`: acetylene, natural-gas, synthesis-gas, carbon-monoxide, n-methyl-2-pyrrolidone, carbon-black, diacetylene.
- No acetylene family exists; I used olefins and syngas.
- `lci/mappings.yaml`: NMP, soot-sludge incineration, spent-solvent incineration.
- Elementary-flow identities for acetylene, diacetylene, benzene and NMP to air.

## Open inputs and gated steps
- **Burner energy balance:** core cannot evaluate it. There is no data for solid carbon, and the diacetylene and benzene heat capacities are fitted only to 1000 K.
- **Quench water and NMP section:** no qualified property model exists (core #315), so the splits are specified, not predicted.
- **Other open inputs:** NOx from the fired heater, site, number of burner trains, product specifications, a source audit of Ullmann for specific consumptions, and heat recovery from the 91.6 MW quench duty.

## Recommended next stage
An independent review of the concept PFD and LCI, then:
- the source audit, to replace the assumed consumptions;
- mapping the backgrounds once the registry entries exist (asu-1 oxygen, steam boiler, cooling tower, wastewater utilities);
- a heat-integration study of the quench heat.

A merge is pending: the branch needs review, and a human or the reviewer merges it.

STATUS: DONE