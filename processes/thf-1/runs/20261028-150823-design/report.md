## THF-1 (BDO cyclodehydration): concept run report

The design basis, the balanced BFD/PFD and the preliminary gate-to-gate LCI are done and committed on `case/thf-1` in 4 commits; the working tree is clean. `cheme validate` reports 0 errors and 0 warnings, and every LCA output is current. The design maturity cheme supports is **none**, so the "concept" claim in `process.yaml` is a label, explained in its notes. Most key values are ASSUMED and the separation values come from a property model core has not qualified for THF/water. Nothing was pushed. No merge is pending: no review or sign-off was made, and the branch needs a human review first.

### Files produced
- **Process files:** `process.yaml` (internal, concept, unreviewed, `lca.source: none`), `process/design-basis.yaml`, `materials.yaml` (5 components), `reactions.yaml` (2 reactions), `flowsheet.yaml` (2 blocks, 10 steps, 15 material and 10 energy streams), and the generated `BFD.xml` and `PFD.xml`.
- **Balance script:** `scripts/thf_balance.py` is my own independent heat and material balance. It uses the NRTL activity model in the thermo package with the published ChemSep THF/water parameters.
- **Lists:** `equipment/equipment-list.yaml` has 13 items. There are no line or instrument lists because there are no P&IDs.
- **LCI:** `lca/lca.yaml` and `lca/mappings.yaml` (no overrides, but it notes what each exchange should link to later), plus the generated inventory, gaps, dataset and manifest files.
- **Docs:** `DESIGN.md` (decisions D-001 to D-011, evidence, source register, open inputs) and `PROGRESS.md`.

### Design
- **Reaction:** 1,4-butanediol (BDO) is dehydrated at 145 °C and 130 kPa(a) with 2 wt% p-toluenesulfonic acid (p-TSA) in the liquid. The reactor sits under a short rectifying column (reactive distillation). The overhead condensate is 80 wt% THF, which matches the patent's 78–80 wt%.
- **Heavies bleed:** a bleed of 117.7 kg/h removes the heavies and the acid.
- **Pressure-swing distillation:** a low-pressure column at 110 kPa(a) and a high-pressure column at 800 kPa(a). The model's azeotrope is 95.3 wt% THF at 1 atm and 88.2 wt% at 8 bar.
- **Recycle and heat integration:** 8.2 t/h is recycled between the columns. The high-pressure condenser reboils the low-pressure column, which saves 22% of the steam.

### Balances
- **Flowsheet:** every step and block closes its mass balance, and the reactor's element balance is checked by validate.
- **LCI:** mass, C, H, O and S close; the largest residual is 0.01%, on sulfur.
- **Energy:** the script's overall energy balance closes to 0.01%.
- **Library LCI build:** `build_lci.py --strict`, run into a scratch folder, passes and reports the 8 gaps unlinked rather than as errors.

### LCI per kg THF
| Exchange | Amount |
|---|---|
| BDO | 1.2674 kg (the stoichiometric minimum is 1.2492) |
| p-TSA | 0.38 g |
| MP steam | 3.07 MJ |
| LP steam | 0.53 MJ |
| Electricity | 0.98 Wh |
| Heat to cooling water | 3.54 MJ |
| Process water to treatment (80 ppm THF) | 0.249 kg |
| Heavies bleed to incineration | 18.8 g |

All 8 backgrounds are left unmapped as gaps, never set to 0, so there is no impact result. The data quality rating is 2.33.

### Sources used
- **Main source:** patent US 9284289 B2 (Mitsubishi Chemical) for the reactor temperature, acid concentration, water window, reactive-distillation setup, condensate composition and by-products.
- **Reaction context:** Hunter, Ehrenberger and Savage 2006 (doi:10.1021/jo061017o, abstract only) on reversibility and equilibrium yields in hot water; Li and Chen 2019 (doi:10.3390/ma12132092, CC BY) for catalyst alternatives.
- **Data:** the ChemSep NRTL parameters and the `chemicals` package for formation enthalpies, and PubChem for the identity of the heavy by-product.
- **Weak cross-check only:** an engineering forum thread on the azeotrope at 1 atm and 8 bar.
- **Not read:** the Ullmann THF chapter is recorded as a lead only.

### Key ASSUMED values
- 50 kt/a and 8000 h/a.
- Product purity 99.95 wt% THF.
- THF selectivity 0.995, with the heavies (lumped as the BDO dimer ether) held at 30 wt% in the reactor.
- Column pressures, distillates 0.03 mol/mol away from each azeotrope, and reflux 1.3 × minimum with a floor of 0.3.
- Steam levels 1000 and 450 kPa(a), and pump efficiency 0.6.

### Gated steps
Core issue #315 is open as core-archive#315 (last updated 2026-10-27). In cheme 0.8.0 the NRTL model is qualified only for ethanol/water, so three steps cannot run in cheme:
- the simulation (`process simulate`);
- the property fill and core energy closure (`props --fill`);
- the energy check of the liquid-phase reactor.

### Open inputs
- **Liquid–liquid split (I-04):** NRTL predicts that THF and water split into two liquids in a temperature range that may overlap the low-pressure column's stripping section. This needs a rigorous column check.
- **Reaction data:** no kinetics were found to size the reactor (I-03), and the selectivity and heavies rate have no source (I-02).
- **BDO recovery (I-05):** the bleed loses 0.94% of the BDO feed; recovering it is not designed.
- **Emissions:** vents and fugitive emissions are excluded with reasons, not estimated.
- **Dataset classification:** the CPC code for THF is not set (an info finding, not an error).

### Missing registry entries (for the consolidated PR)
- `chemicals/chemicals.yaml` needs `1-4-butanediol`, `tetrahydrofuran` and `p-toluenesulfonic-acid`.
- `lci/mappings.yaml` needs technosphere entries for those three, plus a treatment entry for incinerating hazardous liquid waste.

### Recommended next stage
1. Check the THF/water NRTL model against measured equilibrium data near 100 and 800 kPa, and run rigorous columns including the liquid–liquid check.
2. Find a source for the selectivity and heavies formation, starting with the Ullmann chapter.
3. Decide whether to recover BDO from the bleed.
4. After the registry PR, map the LCI backgrounds.
5. Then an independent design review before basic engineering.

STATUS: DONE