I built the iodine-1 case: design basis, a balanced BFD/PFD and a preliminary gate-to-gate LCI, all committed in 4 commits on `case/iodine-1`. `cheme validate` reports 0 errors and 0 warnings. Nothing was pushed and nothing outside `processes/iodine-1/` was touched. No stage is signed off and no merge is pending: the branch still needs a review.

**Route.** I chose iodine from natural brine over caliche because the brine's feed iodine content is sourced; I found no open primary source for caliche leach compositions. Brine with 300 mg/kg iodide (Oklahoma Woodward-type) is acidified with the plant's own recycled acid, oxidised with chlorine, and the iodine is blown out into a closed air loop with a 5 % purge. It is absorbed into an HI/H2SO4 liquor with SO2, freed again with chlorine, filtered, melted under sulfuric acid and flaked. The spent brine is neutralised with caustic and reinjected.

**Files**
- **Process:** `process/design-basis.yaml`, `materials.yaml`, `reactions.yaml` (10 reactions), `flowsheet.yaml`, `simulation.yaml` (reactors adiabatic), generated `BFD.xml` and `PFD.xml`.
- **Balance script:** `scripts/iodine_balance.py`, which solves the two recycles (the air loop, and filtrate plus spent melter acid back to the brine).
- **Lists and manifest:** `equipment/equipment-list.yaml` (11 items), `process.yaml` (internal, concept, unreviewed).
- **Records:** `DESIGN.md` (source register, basis and method tables, decisions D-001 to D-012), `PROGRESS.md`.
- **LCA:** `lca/lca.yaml`, `lca/mappings.yaml` (no overrides yet), `inventory.csv`, `gaps.csv`, `dataset.yaml`, `results.*`, `manifest.json`.

**Balances**
- Every block and step closes on mass and the reactor element balances are consistent. Plant in = out = 466,939.4 kg/h.
- `cheme assess lca --balance` closes mass and every element (largest residual 0.01 %, sulfur); iodine is 138.58 kg/h in and out.
- Overall recovery is 90.0 %, leaving 29.8 mg/kg iodine in the spent brine. This matches a patent's statement of 90 % recovery leaving about 30 mg/L (US 2013/0243684).
- Brine pH after acidification is about 2.4 (an ideal estimate).
- `cheme check`: all concept gates pass except the plot plan, which is out of scope.
- `cheme maturity` supports no level, so the `concept` claim exceeds it (warning `cheme.maturity-claim-exceeds`). Concept is already the lowest level the manifest allows, and aniline-1 has the same result, because every flow and conversion is assumed.

**LCI per kg iodine**

| Exchange | Amount |
|---|---|
| Brine | 3,695 kg |
| Chlorine | 0.614 kg |
| SO2 | 0.281 kg |
| Sulfuric acid 98.5 % | 0.203 kg |
| Caustic soda 50 % | 1.137 kg |
| Process water | 8.90 kg |
| Air | 28.9 kg |
| Electricity | 4.79 kWh (80 % is the reinjection pump) |
| LP steam | 0.065 kWh |
| Cooling water | 0.022 kWh |
| Spent brine to reinjection | 3,704 kg |
| Vent | 30.5 kg, including 0.325 kg CO2 from the brine alkalinity and 0.25 g iodine |

Ten background exchanges are left unmapped on purpose, each with a description of the activity to link later. Iodine to air is a gap because the climate method has no factor for it. The result class is "partial screening".

**Sources:** the Oklahoma Geological Survey iodine page, the 1987 Minerals Yearbook (US Bureau of Mines), patents US 2013/0243684, US 4,282,324, US 1,897,031 and US 9,994,448, Sander's Henry's-law compilation (CC BY), and the chlor-alkali-1 and sulfuric-acid-1 product streams. The heats of reaction come from NBS formation enthalpies that I recalled rather than re-read, so they are marked ASSUMED. Ullmann (licensed) was not read, and the EPA iodine chapter is a scanned PDF I could not read.

**Key ASSUMED values**
- Capacity 1,000 t/a at 8,000 h/a; product 99.8 wt% iodine.
- Brine: 10 wt% NaCl, alkalinity 2 meq/kg, 313 K.
- Chlorine 5 % in excess; 98 % of iodide oxidised; 92 % of iodine blown out; 130 Nm³ air per m³ brine. A check against the Henry's-law constant gives a stripping factor of about 3.7, so this air rate is conservative.
- Absorber takes up 99.5 %; SO2 2 % in excess; absorber bleed at 10 wt% HI.
- Precipitation 99.5 % / 99 %; filter cake 10 % liquid; melter acid 0.2 kg per kg iodine.
- Reinjection at 3,100 kPa(a), the least certain number and it sets most of the electricity.

**Missing registry entries** (for the consolidated chemicals PR): iodine, chlorine, sodium hydroxide, sulfuric acid, sulfur dioxide, and a natural/spent brine entry.

**Open inputs and gated steps**
- Brine salinity, alkalinity, temperature, H2S and bromide have no source.
- The blow-out and absorber splits, the solid iodine, and the energy closure need electrolyte and solids support in core (#364 and #365 in the issue). `gh` could not open those issues on `ChemE-as-Code/core`. Today core handles only aqueous NaCl, and `cheme process energy` cannot evaluate this flowsheet.
- Not estimated: equipment leaks, the melter vent, and storage/unloading vents.
- Core bug: `cheme process build` crashes on the DEXPI step class `Pumping`. I used `TransportingFluids` for the reinjection pump instead; this should be reported to core.

**Recommended next stage:** get a sourced brine analysis and sourced yields (EPA chapter, Ullmann), then size the two towers once core has the electrolyte model. After that, map the backgrounds (chlor-alkali-1, sulfuric-acid-1, a brine wellfield and reinjection dataset, grid power) and run an independent review.

STATUS: DONE