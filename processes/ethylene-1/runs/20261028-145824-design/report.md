I built the ethane steam cracker case through to a balanced BFD/PFD and a preliminary gate-to-gate LCI. `cheme validate` reports 0 errors and 0 warnings, the LCI balances, and everything is committed on `case/ethylene-1` in three commits: scaffold `0859ac6`, flowsheet `8936571`, LCI and documents `f06b203`. Nothing is pushed.

**Route:** I chose ethane rather than naphtha. The issue recommends ethane unless there is a traceable naphtha assay, and I found none. Ethane needs only real molecules, not pseudocomponents. The cost is that propylene is minor (2.6 % of the ethylene) and there is **no pyrolysis fuel oil**: the BREF lists no C7+ yield for ethane, so I did not invent one. This departs from the case notes' co-product list on purpose (D-001).

## Files produced
- **Basis and manifest:** `process.yaml` (internal, concept, unreviewed) and `process/design-basis.yaml`.
- **Process model:** `process/materials.yaml`, `reactions.yaml`, `flowsheet.yaml` and `simulation.yaml` (only declares three reactors adiabatic). The BFD and PFD are generated: 7 blocks, 26 steps, 69 streams.
- **Balance script:** `scripts/balance.py` converges the ethane and propane recycles and the furnace firebox heat balance.
- **LCI:** `lca/lca.yaml` and an empty `lca/mappings.yaml` (no overrides needed yet). The generated `inventory.csv`, `gaps.csv`, `dataset.yaml` and `manifest.json` are written and current.
- **Lists and documents:** `equipment/equipment-list.yaml` (20 items; no line list, as there are no P&IDs), `DESIGN.md` (source register and decisions D-001 to D-018), `PROGRESS.md`.

## Results
- **Reactors are calculated by cheme.** The furnace conversions are derived from the sourced yields (≈70 % ethane conversion). `cheme process reactors` reproduces my script's duties: ethane coils 372.2 MW, propane recycle coil 9.5 MW, firebox −586.6 MW.
- **Plant figures:** 125 t/h ethylene from 158.6 t/h fresh ethane, with 66.0 t/h ethane recycled. Ultimate yield is 0.788 kg ethylene per kg ethane. Furnaces fire 611 MW, or 17.6 GJ/t ethylene. Compressor shaft power is 119 MW, or 3.4 GJ/t.
- **LCI per kg ethylene (unallocated):**

| Exchange | Amount |
|---|---|
| Ethane | 1.161 kg |
| Natural gas make-up | 0.0705 kg |
| NaOH 10 % solution | 0.092 kg |
| Boiler feed water | 0.015 kg |
| Electricity | 0.871 kWh |
| MP steam | 0.339 kWh |
| LP steam | 0.336 kWh |
| HP steam export | 2.47 kWh |
| Cooling water | 2.73 kWh |
| Propylene / crude C4 / pyrolysis gasoline | 0.026 / 0.035 / 0.031 kg |
| Fossil CO2 | 0.433 kg |
| NOx / CO / dust | 0.39 / 0.19 / 0.027 g |
| Spent caustic / blowdown | 0.095 / 0.015 kg |

- **LCI balance:** mass, element and carbon-by-origin balances close. Carbon in is 133.5 t/h; out is 117.3 t/h in products plus 16.1 t/h in the flue gas.
- **Gaps:** there are 14, all deliberate, each naming the background activity to link later, several of them library processes:

| Exchange | Background to link later |
|---|---|
| NaOH | chlor-alkali-1 |
| MP/LP steam (and the steam export) | utility-steam-ng-boiler |
| Cooling water | utility-cooling-tower |
| Blowdown, spent caustic | utility-wwtp |

- **Check results:**
  - `cheme check`: the concept process gates pass. The layout, P&ID, review and datasheet gates fail; they are out of scope.
  - `cheme maturity`: does not reach "balanced", because the separators use assumed splits and the feed is assumed. The `process.yaml` claim is honest about this.
  - The library catalog build shows no findings for ethylene-1.

## Sources used
- **EU BREF on large volume organic chemicals (2017), doi:10.2760/77304:** Table 3.3 (once-through ethane and propane yields), Tables 3.4 and 13.1 (NOx, CO and dust), §3.3.4 (energy), §3.2.2.4 (separation schemes).
- **IPCC 2006 Guidelines, Vol. 2, Table 2.3:** CH4 and N2O factors. I took these from memory of the table and did not re-fetch them, so check them before relying on them.
- **Ullmann's "Ethylene":** cited as the issue's lead only; I did not read it.

## Key assumed values
- Capacity 1000 kt/a at 8000 h/a.
- Feed 96.8 mol% ethane.
- Coil outlet 840 °C, 200 kPa(a); 0.30 kg dilution steam per kg feed.
- Cracked-gas compressor to 36 bar, isentropic efficiency 0.78.
- All separation splits, purities and reflux ratios.
- Hydrogenation selectivity 80/20.
- Refrigeration at 60 % of Carnot.
- 15 % excess air.
- NOx at the upper end of the new-furnace emission limit (100 mg/Nm³).
- Compressors shown as electric drives, with the HP steam as a gross export. A real cracker would use steam turbines and net most of it (D-015).

## Registry entries missing from `chemicals/chemicals.yaml`
ethylene, propylene, ethane, natural-gas, sodium-hydroxide, crude C4 / 1,3-butadiene, pyrolysis-gasoline, nitrogen-oxides, carbon-monoxide, dinitrogen-monoxide.

## Open inputs and gated steps
- **Gated on core #315:** the energy balance of the separation train and real column design. No core property package covers C2+ hydrocarbons, so only the reactor and firebox energy is checked by core. The LCI's "energy closure 57.8 %" counts utilities only, not fuel heating value, so it is not a heat-balance result.
- **Needed as inputs:** a sourced ethane spec and capacity, hydrogenation catalyst selectivities, a coke make for decoking emissions, fugitive VOC (needs P&IDs), sulphur doping and SO2.
- **Decisions for a person:** the allocation method (mass is proposed) and the drive choice.

**Recommended next stage:** link the LCI backgrounds, library processes first, and decide the allocation. Then go to basic engineering of the separation train with simulated columns once core #315 qualifies a light-hydrocarbon package.

Merge pending: the branch is not reviewed or merged, and no stage was signed off.

STATUS: DONE