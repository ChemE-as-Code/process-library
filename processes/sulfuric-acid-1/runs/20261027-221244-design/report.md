I've built a balanced concept PFD and a preliminary gate-to-gate LCI for the sulfur-burning double-contact acid plant. It is all committed in 4 commits on `case/sulfuric-acid-1`, nothing pushed, working tree clean. The mass balance closes in cheme; the energy balance closes only in my own script (`scripts/balance.py`), because cheme has no property model for SO2/SO3 gas or aqueous acid.

**Files produced** (all in `processes/sulfuric-acid-1/`)
- `process/design-basis.yaml`, `materials.yaml`, `reactions.yaml`, `catalysts.yaml`, `simulation.yaml` (only records that the furnace, beds and towers are adiabatic), `flowsheet.yaml`. The BFD and PFD are generated from them: 4 blocks, 22 steps, 41 streams.
- `scripts/balance.py`: the independent heat and material balance behind the tower outlets, temperatures and duties.
- `equipment/equipment-list.yaml` (16 items). No line list: the PFD doesn't need line numbers yet.
- `lca/lca.yaml` plus the generated inventory, gaps, coverage, dataset and manifest files.
- `DESIGN.md` (decisions D-001 to D-013, route and boundary memo, evidence, source register, core dependencies, open inputs), `process.yaml` (status internal, concept, unreviewed), `PROGRESS.md`.

**Balance and check results**
- `cheme validate`: 0 errors, 0 warnings. Every block and step mass balance closes.
- Overall: 129,259 kg/h in against 129,259 kg/h out (+0.32 kg/h). Sulfur closes to +1.3 kg/h (0.01 %).
- Reaction extents: SO2 → SO3 424.85 kmol/h; SO3 absorbed 424.83 kmol/h.
- `cheme process reactors`: bed duties ≈ 0 kW, which confirms my script's adiabatic outlet temperatures (899 / 794 / 735 / 704 K). Every bed is short of equilibrium (ln(Q/K) = −0.06, −0.30, −0.38, −1.22).
- Energy closes to 0.00 kW in the script. Furnace outlet 1402 K, which is beyond the 1000 K range of the heat-capacity fits used.
- `cheme check`: all concept gates pass except the plot plan (layout was out of scope).
- `cheme maturity`: level "none". That is the honest result, since the capacity and feeds are assumed and the beds and towers are specified values; it is the same situation as methanol-1.

**LCI, per kg of 98.5 wt% acid**

| Flow | Amount |
|---|---|
| Sulfur in | 0.323 kg |
| Air in | 2.567 kg |
| Dilution water in | 0.166 kg |
| Electricity in | 0.0545 kWh |
| HP steam out (heat above boiler feed water) | 1.031 kWh, about 1.34 kg steam |
| Heat to cooling water | 0.491 kWh |
| Tail gas out | 2.056 kg |
| SO2 to air | 1.94 g |
| SO3 / acid mist to air | 0.039 g |

- Coverage reports a "partial screening carbon footprint" with 8 gaps and no total. Every purchased input and the steam export is left unmapped, each with a description of the background activity it should connect to.
- The inventory's mass and element balances close against the flowsheet.
- The tool also prints "energy closure 188.8 %". That figure counts only the utilities and leaves out the heat released by burning the sulfur, so it is not a real imbalance.
- Furnace NOx, fugitive SO2 and the pump-tank vent are listed as exclusions until sourced factors exist.

**Sources used:** Speight (2002), read only through the `tech-heavy-chem-sulfuric-acid` skill, for the arrangement and conversion ranges; Ullmann's (doi:10.1002/14356007.a25_635), through the cheme reaction library, for the catalyst temperature window; gas thermodynamic data from the chemicals/thermo packages (Poling, CRC); NBS tables (Wagman 1982) for liquid H2SO4 and water; CoolProp for steam. The JRC fertilisers-and-acids BREF is cited, but I did not read its chapters.

**Key ASSUMED values**
- 1000 t/d H2SO4 at 8000 h/a.
- Pure molten sulfur at 413 K; site air at 298 K and 60 % humidity.
- Burner gas 11.5 mol % SO2.
- Cumulative conversion 63 / 87 / 95 / 99.7 %, chosen within Speight's ranges.
- Bed inlet temperatures 688 / 713 / 708 / 683 K.
- 99.9 % SO3 absorption in each tower; one shared acid header at 343 K.
- HP steam at 4100 kPa(a) and 673 K, from boiler feed water at 378 K supplied by the site.
- Electric blower (isentropic efficiency 0.80); acid heat capacity 1.45 kJ/(kg K); heat of mixing water into strong acid neglected.

**Missing registry entries** in `chemicals/chemicals.yaml`: sulfur, sulfuric acid, sulfur dioxide, sulfur trioxide, and a V2O5 catalyst if catalysts are registered. Until they exist, the feed, the main product and the SO2 emission are only described in notes in `process.yaml`.

**Open inputs and gated steps**
- **Core cannot close the energy balance (core #315, #364).** No property package covers SO2/SO3 gas or aqueous acid, and electrolytes other than NaCl are refused. `cheme process energy` and a DWSIM run are therefore blocked.
- **A cheme 0.8.0 bug should go to core.** `cheme process build` crashes on any step of class `Pumping`. I used the parent class `GeneratingFlow` for the acid pump as a workaround.
- **Open inputs:**
  - capacity and site;
  - sulfur specification;
  - the SO2 and acid-mist emission limit (99.7 % conversion may not meet it);
  - vendor bed conversions and catalyst quantities;
  - the steam-side split between boiler, superheater and economisers;
  - whether the blower is steam-turbine driven;
  - sourced acid properties and the acid dew point at the tower inlets.

**Recommended next stage:**
1. Read the BREF and Ullmann's chapters with exact locators, to source the conversion, absorption and emission figures and get a benchmark to compare against.
2. Decide how to treat the steam co-product (credit against boiler steam, or allocate).
3. Map the backgrounds in the LCA.
4. Basic-engineering flowsheet refinements: separate drying and absorption acid systems, and acid heat-recovery and tail-gas variants.

One housekeeping note: I accidentally wrote a schema dump to the worktree root. Deleting it was refused, so I moved it into this folder's git-ignored `build/` directory; the root is clean. No merge is pending: the branch is committed but not pushed, and no stage was signed off.
