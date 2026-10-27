I built a balanced design basis → BFD/PFD → gate-to-gate LCI for the 1,500 t/d natural-gas ammonia plant. It is all committed on `case/ammonia-1` (4 commits, tree clean, not pushed). `cheme maturity` reaches **no level**, mainly because the natural-gas composition is a placeholder I assumed, not a sourced one.

**Files produced**
- `process/design-basis.yaml`, `process.yaml` (status `internal`, maturity `concept`, `unreviewed`), `plant.yaml` with the BFD and PFD declared.
- `process/materials.yaml` (11 components, heat capacities fitted to 1500 K), `process/reactions.yaml`, `process/flowsheet.yaml` (7 blocks, 51 steps, 101 streams), and the generated `process/BFD.xml` and `PFD.xml`.
- `process/simulation.yaml`: only declares which reactors are adiabatic; it is not a simulation model.
- `scripts/plant_balance.py`: my independent balance of the whole plant, using cheme's own equilibrium and enthalpy functions.
- `equipment/equipment-list.yaml` (44 items); `lca/lca.yaml` plus the generated inventory, gaps and dataset files; `DESIGN.md` (decisions D-001 to D-021); `PROGRESS.md`.
- No line list (that comes with the P&IDs) and no P&ID sheets.

**Balance and check results**
- `cheme validate`: 0 errors, 0 warnings. All 7 block and 51 step balances close on mass, components and elements.
- cheme calculates the reactor outlets and agrees with my script: primary reformer duty 68,388 kW (script 68,386 kW), and every adiabatic reactor comes out under 2 kW.
- Concept gates: 6 pass; only the plot plan fails, and layout is out of scope.
- Design case: process gas 29.5 t/h, fuel gas 8.2 t/h; converter outlet 17.8 mol% NH3; purge 0.737 %; 12 mol% inerts at the converter inlet; 148 t/h steam raised, of which 55.1 t/h is exported; 35.2 MW electricity.

**LCI, per kg NH3**

| Exchange | Amount |
|---|---|
| Natural gas (process + fuel) | 0.6034 kg (0.4721 + 0.1313) |
| Air | 3.723 kg |
| Demineralised water | 1.623 kg |
| Electricity | 0.563 kWh |
| Heat to cooling water | 2.104 kWh |
| MP steam exported (co-product) | 0.881 kg |
| Boiler blowdown | 0.047 kg |
| Fossil CO2 to air | 1.563 kg (vent 1.173, stack 0.390) |

- The inventory balances: 5.94962 kg in against 5.94970 kg out; cheme reports mass, element and carbon balances closed.
- Every background is left unlinked, with a description of the activity it should connect to; nothing is set to zero and no licensed values are used.
- Furnace NOx, CO, CH4 and N2O are not quantified, because I had no sourced emission factor. cheme warns about this for the furnace (H-101), and the warning is left standing.

**Sources used**
- The issue's proposed brief.
- cheme's reaction library (which cites Ullmann's and Twigg's Catalyst Handbook).
- Component data from the chemicals/thermo packages, the ChemSep interaction parameters inside thermo, and IAPWS steam tables.
- The ammonia tech skill's conditions table, for plausibility only.
- I did not read the BREF, IEA, Lee or Mayer documents and took no numbers from them; they are listed as design-visible references only.

**Key ASSUMED values**
- Feed gas: CH4 91 / C2H6 4 / C3H8 1 / CO2 1 / N2 3 mol%.
- Reforming: steam-to-carbon 3.0; primary reformer outlet 1083 K at 35 bar(a); approach to equilibrium 10 K in the reformers and shifts, 15 K in the converter.
- CO2 removal (activated MDEA): 500 ppmv CO2 left in the gas, 1.0 MJ/kg CO2 regeneration heat.
- Loop: 146–155 bar(a), separator at 263 K.
- Purge recovery: 90 % of the hydrogen and 99 % of the ammonia recovered.
- Furnace stack at 423 K; one steam level at 46 bar(a) / 673 K; all compressors and pumps electric; compressor efficiency 0.78; refrigeration at 0.55 of Carnot.

**Missing chemicals-registry entries** (for the consolidated PR): `ammonia` (with a refrigerated liquid grade), `natural-gas`, `ethane`, `propane`, a demineralised `water` grade, an MP `steam` grade at 46 bar(a) / 673 K, and optionally `flue-gas`.

**Open inputs and gated steps**
- I-01: a sourced natural-gas composition. This is what keeps maturity at none.
- I-02 to I-10: freezing the brief with the owner, site conditions, sourced approaches or kinetics, CO2-removal licensor data, furnace and other emissions, purge-recovery vendor data, electric versus steam-turbine drives, and background datasets.
- Gated on core #315 (checked open today): stream properties, energy closure in core, and a rigorous simulation.
- Core bug: `cheme process build` crashes on the DEXPI classes `HeatingInFurnace` and `SupplyingThermalEnergy`. I worked around it by using other classes; the details are in DESIGN.md section 4.

**Recommended next stage:** freeze a sourced feed and the brief (I-01, I-02) and gather the reaction evidence for the approaches to equilibrium. Then rerun the script and take sourced furnace emission factors. After that, an independent review of this concept PFD and LCI, before P&IDs or linking backgrounds.

Nothing is signed off; no review or merge has happened yet, so a merge is pending.
