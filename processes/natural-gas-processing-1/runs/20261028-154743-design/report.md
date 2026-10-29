I built the concept-stage natural-gas-processing-1 design: a sourced feed, a balanced BFD/PFD and a preliminary gate-to-gate LCI. `cheme validate` shows 0 errors and 0 warnings. Everything is committed in 4 commits on `case/natural-gas-processing-1`. Nothing is pushed, no stage is signed off, and the branch is waiting for review and a human merge.

**Feed and route**
- **Feed:** Barnett shale gas, well 2, from Bullin & Krouskop (2009), Table 1: 81.2 % methane, 11.8 % ethane, 5.2 % propane, 0.3 % CO2, 1.5 % N2. The paper reports no H2S, so the plant has no sulfur recovery.
- **Route:** inlet separator → MDEA amine unit (CO2 to 50 ppmv) → TEG dehydration plus molecular-sieve driers → turbo-expander NGL recovery → expander-driven booster plus electric residue compressor. Flash gases and a small residue-gas draw fire the TEG reboiler and the sieve regeneration heater.
- **Mol sieves:** I added them although the brief lists only TEG. Glycol drying alone is not dry enough for the cryogenic section.

**Files produced**
- `process/flowsheet.yaml`, `materials.yaml`, `reactions.yaml` (fuel combustion only) and `design-basis.yaml`; BFD and PFD generated (6 blocks, 19 steps, 47 streams).
- `scripts/balance.py`, the split-based balance every stream comes from. Run it with `cheme run scripts/balance.py`.
- `lca/lca.yaml`, `lca/mappings.yaml` (no overrides) and the generated inventory, dataset, gaps and coverage files.
- Equipment list (17 tags), `process.yaml` (status internal, maturity concept, unreviewed), `DESIGN.md` (decisions D-001 to D-014 and a source register) and `PROGRESS.md`. The line list stays empty because there are no P&IDs.

**Balance results**
- All 6 blocks and 19 steps close in cheme, including the element balance of the fired heaters. Plant in = out = 99,395.5 kg/h.
- **Products:** sales gas 68,709.5 kg/h (83.7 MMscf/d, 96.7 % methane, heating value about 1003 Btu/scf, inside the usual 1035 ± 5 % band). NGL 27,258.5 kg/h (58 wt-% ethane, 41 wt-% propane). Overall recovery is 90.0 % of the ethane and 97.95 % of the propane.
- **Utilities:** electricity 3,986 kW (3,672 kW of it for the residue compressor), LP steam 1,078 kW, cooling water 6,850 kW, fired heat 1,027 kW.
- **Emissions:** CO2 905 kg/h (627 kg/h is reservoir CO2 vented with the acid gas), methane 3.05 kg/h.

**LCI results** (per kg sales gas, energy allocation with the NGL by heating value, sales gas share 72.2 %)
- **Inputs:** raw gas 1.0245 kg, electricity 0.0419 kWh, steam 0.0113 kWh, cooling water 0.0720 kWh.
- **Outputs:** CO2 9.51 g, methane 0.032 g, NOx 2.3 mg, NGL co-product 0.397 kg.
- **Balance:** the dataset's mass balance closes against the flowsheet (99,400.4 kg/h including 4.9 kg/h of consumables; residual −0.015 kg/h). C, H, N and O also close, but cheme reports the element balance as "not assessable" because the MDEA, TEG and sieve consumables have no composition.
- **Classification:** partial screening carbon footprint. Direct emissions are 0.0105 kg CO2-eq/kg, and 18 exchanges are gaps (every background is left unmapped, with a description of what it should link to). Grid electricity is the biggest gap: it outweighs the direct emissions at any grid factor above about 0.25 kg CO2-eq/kWh.

**Sources**
- Bullin & Krouskop (2009), open copy on bre.com: feed composition and the Barnett line-up.
- EPA Natural Gas STAR glycol lessons-learned paper: 3 US gal TEG per lb of water, about 1 scf of gas absorbed per gallon, about 90 % recovered by the flash tank.
- EPA AP-42 section 1.4, Tables 1.4-1 and 1.4-2: heater combustion factors, which I checked in the PDF. Section 5.3 for the list of emission sources.
- US 11,473,837 B2, Background: ethane and propane recovery ranges for this expander process.
- Wikipedia "Natural-gas processing": sales-gas specification, used as a discovery source only.
- The water-content correlation (Bukacek) is only partly verified: one coefficient is still quoted from memory. This is marked in the source register.

**Key ASSUMED values:** capacity 100 MMscf/d; inlet 6000 kPa(a) and 40 °C; free water 1 bbl/MMscf; CO2 50 ppmv; MDEA 45 wt-% and its loadings; reboiler steam 1.0 lb per gallon of amine; lean TEG 99 %; sieve regeneration parameters; cold-separator split; expander and compressor efficiencies; 80 % heater efficiency; amine, TEG and sieve losses.

**Missing registry entries** (for the consolidated PR): natural gas (raw and pipeline grades), NGL or ethane/propane, MDEA, TEG, zeolite molecular sieve, demineralised water, an LP steam grade, produced water. There is also no taxonomy family for natural gas processing, so I used `fuels`.

**Open inputs and gated steps**
- **Open inputs:** the full feed analysis (C4+, H2S, mercury), the receiving pipeline's tariff, the site and its grid, and the choice between electric and gas-turbine drive.
- **Energy balances:** no property package in cheme covers these mixtures, so stream enthalpies, phases, energy closure and the cold-box duty are not calculated (core #315). Duties are ideal-gas or rule-of-thumb estimates.
- **Amine chemistry:** needs electrolyte support (core #364). The TEG–water system is also gated under core #315.
- **Molecular sieve:** core can now calculate these beds, but no sourced natural-gas isotherms were found, so the split stays specified.
- **Equipment-leak methane:** excluded until P&IDs exist; it could be of the same order as the direct CO2.
- **cheme maturity:** calculation maturity is "none", so the concept claim in `process.yaml` raises a warning that the claim exceeds the evidence.
- **cheme check:** all process gates pass. The concept layout-plot-plan gate and the P&ID, review, layout and datasheet gates fail because they were out of scope.

**Recommended next stage:** obtain a full feed analysis and a sourced property package (or a qualified Peng-Robinson/GERG package from core), then simulate the NGL and compression sections to replace the assumed splits and duties. Estimate leak methane once P&IDs exist, and link the electricity, steam and raw-gas backgrounds.

STATUS: DONE