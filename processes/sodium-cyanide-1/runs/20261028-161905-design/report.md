I've built the sodium-cyanide-1 concept case: design basis, a balanced BFD/PFD and a preliminary gate-to-gate LCI, all committed on `case/sodium-cyanide-1` in 5 commits (last one `aff4b69`). `cheme validate` shows 0 errors and one warning I accepted. Calculation maturity is "none", which is what this evidence can support. No P&IDs were drawn.

**Files produced**
- `process.yaml`: internal, concept, unreviewed.
- `process/design-basis.yaml`, `materials.yaml`, `reactions.yaml`, `catalysts.yaml`, `simulation.yaml` (marks the converter adiabatic).
- `process/flowsheet.yaml`: 5 blocks, 15 steps, 43 streams; `BFD.xml` and `PFD.xml` are generated from it.
- `scripts/nacn_balance.py`: my independent script for the separation outlets and duties.
- `equipment/equipment-list.yaml` (14 items) and `piping/line-list.yaml` (23 lines).
- `lca/lca.yaml` and `lca/mappings.yaml`, plus the inventory, gaps, dataset, manifest and results files that `cheme assess lca --write` produced.
- `DESIGN.md` (source register, decisions D-001 to D-012, open inputs) and `PROGRESS.md`.

**Results**
- **Balances:** every block and step closes in mass, components and elements (`cheme process streams`).
- **Converter:**
  - Its outlet is calculated by cheme: 7.47 mol% HCN, 2.32% NH3, 22.5% H2O, 11.1% H2, 3.3% CO.
  - It is adiabatic at 1429 K; cheme reports a duty of 0.06 kW, so the energy balance closes.
  - All five reactions are short of equilibrium, so the set conversions are reachable.
- **Capacity:** 6.25 t/h of solid product (98% NaCN), from 3.13 t/h methane, 2.73 t/h ammonia and 10.1 t/h of 50% caustic. Recycling ammonia lifts the overall ammonia yield to 78%.
- **Energy:**
  - Steam: the waste heat boiler raises 15.2 MW and the tail gas boiler 15.4 MW. The plant uses 12.9 MW of this and exports 17.8 MW.
  - Power is 1.03 MW.
  - Cooling water carries 17.7 MW and chilled water 4.8 MW.
- **LCI per kg of product:**
  - Inputs: 0.501 kg natural gas, 0.437 kg ammonia, 1.620 kg 50% caustic, 0.164 kWh power.
  - Outputs: 2.85 kWh steam export (co-product), 2.84 kWh to cooling water, 0.766 kWh to chilled water, 2.22 kg process water to treatment, and 7.53 kg flue gas carrying 0.493 kg fossil CO2.
  - Mass closes at 10.747 kg in and out. I checked carbon (0.3748 kg) and nitrogen (0.3598 kg) by hand against the flowsheet.
  - cheme calls the element balance "not assessable" only because the platinum-rhodium (Pt/Rh) gauze consumable has no composition.
  - The result is labelled a "partial screening carbon footprint" with 12 gaps: the 8 backgrounds, all deliberately left unmapped, and the 4 zero-flow stack trace gases (CO, H2, HCN, NH3), which the GWP method can't characterise. No zeros or licensed values stand in for any of them.
- **Gates:** 6 of 7 concept gates pass; the plot-plan gate fails because layout was out of scope.
- **Library check:** the library catalog build in strict mode runs cleanly with the new folder. pytest isn't installed here, so the library tests did not run.

**Sources** (all facts restated in my own words with locators)
- US 6,596,251 B2: the HCN yield on ammonia and the air and methane ratios to ammonia (Table 2, run 1); gauze type and temperature range; quench outlet range; HCN at 2–3 wt% in the absorber and over 99.5 wt% after refining.
- US 4,847,062 A: by-product ratios from a commercial converter gas (Example 1); crystalliser at 70 °C and 100 mm Hg; mother liquor composition; cake moisture range; 50% caustic.
- cheme's built-in thermodynamic data.
- Ullmann's was not read (it is licensed), and EPA, Western Australian EPA and BREF searches gave no usable numbers.

**Key ASSUMED values**
- Capacity: 50 kt/a over 8000 h.
- Product spec: 98% NaCN, 1% free NaOH, 1% water.
- Feeds: natural gas taken as pure methane; argon counted as nitrogen.
- Ammonia: 99% recycled; stripping steam of 10 kg per kg ammonia, which has no source.
- HCN recovery: 99.9%, with 0.05% lost to the purge.
- Crystalliser:
  - Cake holds 10% liquor.
  - Mother liquor at 0.80 kg NaCN per kg water.
  - Single-effect evaporation.
- Tail gas boiler: complete combustion with 15% excess air.
- Power lump: 400 kW for pumps, vacuum pumps, centrifuge, dryer, briquetting and boiler fan.
- Gauze charge: 50 kg replaced twice a year.
- LCA allocation: all burdens on NaCN, because the chemical exergy of NaCN isn't sourced yet. This departs from the library's exergy rule and is recorded as such.

**Missing from `chemicals/chemicals.yaml`** (for the consolidated PR): `sodium-cyanide`, `hydrogen-cyanide`, `ammonia`, `sodium-hydroxide` (50% solution grade), `platinum`, `rhodium`.

**Open inputs and gated steps**
- **No property model:** cheme 0.8.0 has no qualified property package for HCN at converter temperature, for HCN/ammonia absorption in water, or for the NaCN/NaOH solution (core #364 and #315 per the issue). So `props` and `simulate` were not run, and the energy balance of the separations can't be checked in core.
- **Crystalliser model:** cheme's crystalliser model handles one solute and refuses the free NaOH, so those outlets come from my script.
- **Core issue status:** I couldn't read core #364/#365 from here; `gh` couldn't resolve them.
- **Emissions not estimated:** equipment leaks, tail gas boiler NOx and CO, crystalliser vent and dryer dust, flaring, storage.
- **Not quantified:** phosphate and HCN-stabiliser acid make-up; platinum loss per kg HCN.
- **Accepted warning:** the cold converter feed (349 K) lies outside the gauze temperature window. That window applies to the gauze itself, not to the gas entering it.

**Recommended next stage**
1. Source the converter basis and the downstream recoveries (Ullmann's, the EPA cyanide background document).
2. Once core supports electrolytes and solids for this system, replace the absorber, stripper and crystalliser values with cheme models.
3. Source boiler emission factors and the NaCN exergy, then map the backgrounds, pinning ammonia-1 and chlor-alkali-1 explicitly.
4. Then P&IDs and a HAZOP.

Nothing was pushed; the branch still needs a review and a merge by someone else, so a merge is pending.

STATUS: DONE