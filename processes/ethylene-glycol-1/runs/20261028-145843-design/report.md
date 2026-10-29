The ethylene-glycol-1 case is done to concept stage: a design basis, a balanced BFD/PFD and a preliminary gate-to-gate LCI, all committed on `case/ethylene-glycol-1` (4 commits, not pushed). `cheme validate` shows 0 errors and 0 warnings. A merge is pending: the branch needs a human review, and no stage was signed off.

## Files produced
- **Process files:** `process.yaml` (internal, maturity concept, unreviewed), `process/design-basis.yaml`, `materials.yaml` (12 components), `reactions.yaml` (6 reactions), `flowsheet.yaml`, `simulation.yaml`, and the generated `BFD.xml` and `PFD.xml`.
- **Balance script:** `scripts/eg_balance.py`, an independent balance in plain Python that produces the stream table.
- **Lists and records:** `equipment/equipment-list.yaml` (16 items), `DESIGN.md` (source register and decisions D-001 to D-011), `PROGRESS.md`.
- **LCI:** `lca/lca.yaml`, `lca/mappings.yaml`, and the written inventory: `inventory.csv`, `gaps.csv`, `dataset.yaml`, `results.*`, `manifest.json`, `uncertainty.csv`.

## Process and balance results
- **Route:** a glycols-only plant (no high-purity EO product). Ethylene and oxygen react to EO over a silver catalyst, with methane as the inert diluent gas. EO is absorbed in water and stripped; CO2 is removed from part of the recycle gas with hot potassium carbonate, and 0.15 % of the recycle gas is purged to fuel gas. EO is then hydrated with 20 mol water per mol EO, the water is removed in a 4-effect evaporator and a drying column, and three vacuum columns give MEG, DEG and TEG. Basis: 50 t/h MEG.
- **Flowsheet:** 6 blocks, 21 steps, 37 material and 22 energy streams. Every block and step balance closes in cheme, and both reactors pass the element and extent check. The balance script closes to 0.04 kg/h out of 71.3 t/h.
- **Checks against the EU BREF ranges:**
  - Ethylene 761 kg/t EO (range 700–850), oxygen 755 kg/t EO (range 600–1100), CO2 351 kg/t EO.
  - The crude glycols are 92.0 wt% MEG, at the top of the 75–92 % range.
  - 1.68 t MEG per t ethylene (Shell's vendor figure for conventional plants is 1.53–1.70).
- **Energy (a lumped estimate):** the EO reactor gives off 83.5 MW, all used inside the plant. On top of that the plant imports 22.5 MW of MP steam (1.62 GJ/t MEG) and uses 0.135 kWh/kg power and 3.43 kWh/kg cooling water.
- **`cheme check`:** concept stage 6 ok, 1 fail (the plot plan, out of scope).
- **`cheme maturity`:** reaches no calculation level, because the feeds are assumed rather than sourced and the separations are specified rather than predicted. This matches methanol-1, and the manifest says so.

## LCI results (per kg MEG, mass allocation, MEG share 92.0 %)
- **Inputs:** ethylene 0.548 kg, oxygen 0.543 kg, methane 0.0093 kg, water 0.212 kg, MP steam 0.414 kWh, power 0.124 kWh.
- **Outputs:**
  - Products: MEG 1 kg, plus DEG 0.083 kg and TEG 0.0036 kg.
  - Wastes: purge 0.024 kg, bleed 0.028 kg, heavy residue 0.00027 kg; cooling water 3.16 kWh.
  - Emissions: CO2 0.253 kg, CH4 0.00036 kg, C2H4 0.00036 kg.
- **Balances:** mass, element and carbon-origin balances all close.
- **Gaps:** 11, every one declared `missing:` with the background activity it should link to later.
- **Direct emissions only:** 0.264 kg CO2-eq per kg MEG. This is partial; every background is still a gap.
- **Library LCI build (`build_lci.py --strict`):** no errors for this process and 6 reported gaps. It exits 1 overall because of warnings that every process in the library gets in this environment. `lca/mappings.yaml` holds one override, which only changes the steam exchange's unit to kWh of heat, as soda-ash-1 does.

## Sources
- **Main source:** the EU BREF on large volume organic chemicals (JRC 2017, JRC109279), chapter 7, printed pp. 361–377, Tables 7.2–7.6.
- **Cross-check only:** Shehata et al. 2024, Sci. Rep., CC BY. No values taken; its duties contradict each other.
- **Library:** asu-1 for the oxygen purity.
- **Vendor claim:** Shell OMEGA, used only for the yield cross-check.

## Key ASSUMED values
- Reactor feed 30 % ethylene, 8 % O2, 1 % CO2; per-pass conversion 9 % at 85 % selectivity (inside the BREF ranges).
- Purge 0.15 %, and 90 % of the CO2 removed from the gas sent to the carbonate unit.
- **Glycol split:** 20 mol water per mol EO. The rate of EO with a glycol is taken as 2.0 times its rate with water. That ratio is not from any source — I couldn't reach the kinetics papers.
- 0.5 % of the recycle water is bled off.
- **Energy:** all energy parameters (evaporator economy 3.2, reflux ratios, 3.0 GJ/t CO2 regeneration heat, hydration heat −95 kJ/mol) are assumed.
- **Emissions:** CO2 vent untreated, carrying 0.5 kg CH4 and 0.5 kg C2H4 per t EO.
- **Basis:** capacity 50 t/h and 8000 h/a.

## Missing registry entries (for the consolidated PR)
- **`chemicals/chemicals.yaml`:** ethylene, ethylene-oxide, ethylene-glycol (with a fibre grade), diethylene-glycol, triethylene-glycol; possibly ethane, potassium-carbonate and a glycol-heavies mixture.
- **`lci/mappings.yaml`:** ethylene, the glycols as products, treatment of the heavy glycol residue, combustion of the purge gas, and a biosphere identity for ethylene to air.

## Open inputs and gated steps
- **Core #315:** no property package covers the EO-water-glycol liquids or the loop gas. That blocks stream enthalpies, energy closure, a predictive DWSIM simulation, and a simulator energy balance for the EO reactor.
- **Kinetics:** the hydration split rests on the assumed rate ratio until sourced kinetics replace it.
- **Not modelled:** the residue (0.37 kg/t EO) sits below the BREF range because the EO section's glycol purges are not modelled. EO vents, fugitive emissions, aldehydes and the chlorinated catalyst additive are declared exclusions in the LCI.
- **Left out of the LCI:** the catalyst (about 0.2 kg/t EO) and carbonate make-up, until their compositions are known.
- **Core bug found:** in `_reactor_rules` (`model.py`), the selectivity check overwrites the reaction lookup `declared` with a list. Any later reactor that uses `selectivity:` then sees no reactions and fails validation. I worked around it by giving the EO reactor per-reaction conversions; it needs reporting to core (I did not comment on any issue).

## Recommended next stage
1. Source the hydration kinetics and real utility data (Ullmann, open papers or theses).
2. Once #315 qualifies a polar activity-coefficient package, run `props --fill` and `simulate` for the energy balance.
3. Map the backgrounds after the registry PR: the asu-1 dataset for oxygen, utility-steam-ng-boiler and utility-cooling-tower.
4. Then an independent design review on the branch.

STATUS: DONE