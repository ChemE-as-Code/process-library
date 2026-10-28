## hydrogen-chloride-1: concept-stage report (issue #137)

The design basis, a balanced BFD/PFD and the preliminary gate-to-gate LCI are done and committed in 5 commits on `case/hydrogen-chloride-1`. Nothing is left uncommitted and nothing was pushed. `cheme validate` reports 0 errors and 0 warnings. Every concept gate passes except `layout-plot-plan`, because layout was out of scope. The honest maturity level is **none**: almost every value is assumed. Nothing has been reviewed or signed off, and the branch still needs a review and a human merge.

### Files produced
- **Process design:** `process.yaml` (internal, concept, unreviewed), `process/design-basis.yaml`, `materials.yaml`, `reactions.yaml`, `flowsheet.yaml`, plus the generated `BFD.xml` and `PFD.xml`.
- **Balance script:** `scripts/balance.py`, an independent mass and energy balance.
- **Lists and gates:** the equipment list with the four PFD items (R-101, C-201, C-202, P-201). The line list stays empty until there are P&IDs. `plant.yaml` now declares both diagrams, and `checks.yaml` includes the BFD in the concept file gate.
- **LCA:** `lca/lca.yaml`, `mappings.yaml` (no overrides yet), and the generated `inventory.csv`, `dataset.yaml`, `gaps.csv`, `manifest.json` and `results.*`.
- **Records:** `DESIGN.md` (route and boundary memo, source register, reaction evidence, decisions D-001 to D-013, the steps blocked on core, open inputs) and `PROGRESS.md`.

### Process
Chlorine and wet hydrogen from chlor-alkali-1 (its streams S42 and S44) feed a burner with 10 mol-% excess hydrogen. The furnace raises steam at 1000 kPa(a) and the gas leaves it at 250 °C. A water-cooled graphite falling-film absorber makes 33 wt-% acid, and a tail-gas scrubber takes all the absorption water. The design case is 10 t/h of acid, which is 26.4 kt/a of HCl at 8000 h/a.

### Balance results
- **Mass:** both blocks, all four steps and the Cl, H and O element balances close (block ABS: 10 013.0 kg/h in and out).
- **Furnace:** cheme calculates the furnace outlet (complete conversion, justified because the equilibrium constant is about 2.6e19 at 523 K). cheme's furnace duty, 2267.9 kW released, exactly matches the independent script.
- **Steam export:** 2195 kW, or 1.03 t steam per t HCl, after an assumed 3 % heat loss.
- **Absorber cooling:** 1672 kW, of which 1544 kW is heat of solution.

### LCI per kg HCl (contained in 3.03 kg acid)

| exchange | amount per kg HCl |
|---|---|
| Chlorine gas | 0.980 kg (stoichiometric 0.9724 kg Cl2) |
| Wet hydrogen | 0.0464 kg (0.0315 kg H2) |
| Demineralised water | 2.008 kg |
| Electricity | 0.0017 kWh |
| Cooling | 0.507 kWh |
| Steam exported | 0.665 kWh |
| Vent: hydrogen to air | 2.87 g |
| Vent: HCl to air | 0.33 mg |

- **Balance:** the inventory closes in mass and in each element to 0.00 %.
- **Coverage:** classified "partial screening carbon footprint" with 7 gaps; every background is deliberately left unlinked.
- **Library LCI build:** `build_lci.py --strict` reports 4 gaps for this process and no errors. It exits non-zero, but only because of warnings that come from the build environment and appear for the other processes too.
- **Allocation:** the exported steam gets a share of 0, the same as nitric-acid-1 does. Substitution by boiler steam is kept for comparison only.
- **Inventory keys removed:** I took the `inventory_key`s off the hydrogen and water feeds in `process.yaml`. Otherwise the Atlas build would link the wet hydrogen by wet-gas mass (47 % too much H2) and treat the demineralised water as raw water.

### Sources used
- NIST-JANAF tables for the heats of reaction.
- ATcT and Poling data through `cheme chemistry thermo`.
- US 9 415 364 B2 for the furnace outlet temperature and steam pressure range.
- US 2004/0175323 A1, paragraph [0015], for the 2–15 % hydrogen excess.
- Parker 1965 (NSRDS-NBS 2) heats of dilution, as tabulated on Wikipedia.
- Wikipedia "Hydrochloric acid" for the acid grade and density.
- chlor-alkali-1 for the feed states.

The Ullmann chapter was checked for its identity only. The SGL vendor PDFs and EPA AP-42 section 8.6 could not be read in this environment.

### Key ASSUMED values
- Capacity.
- Hydrogen excess of 10 %.
- Heat loss of 3 %.
- Absorber recovery of 99.5 %.
- Vent HCl of 10 mg/Nm³.
- **Heat of solution of −61.4 kJ/mol:** this drives most of the cooling duty. It is consistent with Parker's values at 1 and 10 mol water per mol HCl, but there is no published point at the product's 4.1.
- Acid heat capacity.
- Power allowance.
- All temperatures and pressures.

### Missing registry and mapping entries (for the consolidated PR)
- **`chemicals.yaml`:** `chlorine`, `hydrogen-chloride`, and a grade for the acid such as `hydrochloric-acid/33`.
- **`lci/mappings.yaml`:**
  - a `chlorine` entry, or a preferred link to chlor-alkali-1
  - a proxy for wet hydrogen counted by mass of wet gas
  - a demineralised-water entry (#45)
  - a biosphere identity for HCl to air
- **Core's flow crosswalk:** H2 and HCl to air.

### Open inputs and steps blocked on core
- **Core #364:** HCl–water is unsupported, so cheme cannot model the absorber, scrubber, acid enthalpy or energy closure. No property package covers chlorine or HCl gas either.
- **Core equilibrium reactor:** it fails to converge when the equilibrium constant is around 1e19 (200 Newton steps), so the furnace is written as a conversion reactor. This is a core finding and I have not filed it.
- **Open inputs:** the burner and absorber data, the real hydrogen excess, the heat of solution from its original source, vent emission factors from AP-42, and the real impurities in the chlor-alkali gases.

### Recommended next stage
Have this concept reviewed. Then source the burner and absorber data, replace the heat-of-solution assumption once core #364 supports HCl–water, and link the LCI backgrounds, starting with chlor-alkali-1's dataset. The basic stage (P&IDs) follows after that.

STATUS: DONE