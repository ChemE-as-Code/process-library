The design basis, balanced BFD/PFD and preliminary gate-to-gate LCI for the dual-pressure nitric acid plant are done and committed on `case/nitric-acid-1`. The tree is clean and nothing is pushed or merged. `cheme validate` reports 0 errors and 0 warnings. `cheme maturity` reaches level **none**, because the feeds, the burner selectivity and the absorber values are assumed rather than sourced.

## Files produced (4 commits)
- **Basis and manifest:** `process.yaml` (internal, concept, unreviewed, two references) and `process/design-basis.yaml`.
- **Process model:** `process/materials.yaml` (9 components), `process/reactions.yaml` (8 reactions), `process/flowsheet.yaml`, and the generated `BFD.xml`/`PFD.xml`.
- **Other process files:** `process/simulation.yaml` only marks the two reactors as adiabatic. `scripts/hno3_balance.py` is a separate heat-and-material balance script.
- **Lists:** `equipment/equipment-list.yaml` has 18 items. There is no line or instrument list yet; those come with the P&IDs.
- **LCI:** `lca/lca.yaml` plus the generated inventory, gaps, dataset, results and manifest files.
- **Docs:** `DESIGN.md` (source register, basis table, method table, decisions D-001 to D-014, open inputs) and `PROGRESS.md`.

## Balances and checks
- **Flowsheet:** 4 blocks, 21 steps, 31 material and 12 energy streams. Every block and step closes in mass, components and elements, and the reaction extents account for every composition change.
- **Reactors:** cheme calculates the burner, cooler-condenser and tertiary-reactor outlets itself, and they match the script.
- **Energy:** core cannot evaluate it, because no property package covers these streams. The script closes its own energy balance to within 6.7 kW of 62 MW (the 6.7 kW is the pump work).
- **Key figures:**
  - 0.285 t NH3 per t HNO3, with 94.7 % of the ammonia nitrogen ending up as HNO3.
  - Gauze outlet at 1144 K.
  - 29.5 MW of heat to HP steam (about 38 t/h exported).
  - Net shaft power 4.19 MW: the expander's 14.3 MW covers part of the 18.4 MW the two compressors need.
  - 46.7 MW to cooling water.
- **Concept gates:** 6 pass. The only failure is the layout plot plan, which is out of scope.

## LCI per kg contained HNO3 (1.667 kg of 60 wt% acid)

| exchange | amount |
|---|---|
| Ammonia in | 0.2854 kg |
| Air in | 5.120 kg |
| Process water in | 0.337 kg |
| Electricity in | 0.1005 kWh |
| LP steam in | 0.0004 kWh |
| Heat to cooling water | 1.122 kWh |
| HP steam exported (co-product) | 0.708 kWh |
| N2O to air | 2.50 g |
| NO to air | 0.216 g |
| Stack gas | 4.076 kg |

- **Mass balance:** inputs and outputs both total 5.7426 kg. `--balance` closes mass and the Ar, H, N and O balances to within 0.01 %.
- **Coverage:** "partial screening carbon footprint", 10 gaps. All backgrounds are left unmapped, each with a description of the dataset it should link to later.
- **Climate result:** only the plant's direct N2O is counted, 0.68 kg CO2-eq/kg. The unabated alternative would be 7.0 g N2O, or 1.91 kg CO2-eq/kg.
- **Energy closure 57.9 %:** this figure counts only the delivered utilities, not the reaction heat, so it is not a real imbalance.

## Sources
- **IPCC 2006, Vol. 3 Ch. 3, Table 3.3 (p. 3.23):** checked in the PDF. It gives 7 kg N2O/t for medium-pressure combustion plants, which I used as the N2O formed. It gives 2.5 kg/t for plants with tail-gas N2O destruction, which I used as the N2O emitted.
- **EU LVIC-AAF BREF (2007), Chapter 3:** used for the process description only, at the locator in the issue. I did not take any numbers from it.
- **Other:** the core reaction library entry for nitric acid, the nitric acid tech skill, and the open-source property packages (thermo, chemicals, CoolProp).

## Key assumed values
- **Product and capacity:** 1000 t/d contained HNO3 as 60 wt% acid, 8000 h/a.
- **Pressures:** oxidation at 0.5 MPa(a), absorption at 1.13 MPa(a).
- **Burner:** feed at 10 mol% NH3, NO selectivity 0.955. This selectivity is not sourced.
- **Cooler-condenser:** weak acid at 42 wt%.
- **Absorber:** treated as a fixed specification, not a predictive model. Tail gas carries 500 ppmv NOx and 3 % O2, and the raw acid carries 0.5 wt% dissolved NOx.
- **Tail-gas treatment:**
  - SCR removes 90 % of the NOx with no ammonia slip.
  - The N2O destruction is the ratio of the two IPCC defaults (1 − 2.5/7), not a catalyst performance figure.
- **Machine efficiencies:** 0.85, 0.80 and 0.85 for the air compressor, NOx compressor and expander.
- **Heat of mixing of the acid:** −17 kJ/mol HNO3.
- **Compressor drive:** an electric motor covers the train's deficit, rather than a steam turbine.

## Missing chemicals registry entries
`ammonia`, `nitric-acid` (with a 60 wt% grade), `nitrous-oxide`, and `nitric-oxide` or `nitrogen-oxides`.

## Open inputs and blocked steps
- **Blocked:** stream enthalpies and the energy balance, and any predictive model of aqueous acid or reactive absorption. Core #315 is still open. Core #364 was closed today but covers only NaCl–water ("no acids") and is not in the installed cheme 0.8.0.
- **Core bug to report:** `cheme process build` crashes on a `Pumping` step. I worked around it by modelling the weak-acid pump as `TransportingFluids`.
- **Open inputs:**
  - BREF consumption and emission ranges to cross-check these figures.
  - A sourced NO selectivity.
  - Platinum/rhodium gauze losses.
  - Tertiary and SCR catalyst data and permit limits.
  - Construction materials and catalysts for the LCI.
  - Ammonia purity and the site.
  - The choice between a steam turbine and a motor on the compressor train.
- **No unabated case in the flowsheet:** reactor conversions cannot vary by case, so the unabated comparison is worked out in `DESIGN.md` (D-009) instead.
- **PFD layout:** the auto-layout puts the oxidation block at the far right. Pinning the layout is still to do.

## Recommended next stage
Hold a review of this concept PFD and LCI, and check the numbers against the BREF ranges. Then link the backgrounds (ammonia, grid electricity, cooling water, avoided steam). Then add a steam-turbine-drive variant and an unabated sensitivity. After that the work can move to basic engineering (P&IDs and line list).

The stage is not signed off, and the branch still needs a human review and merge.
