I've built the concept design and preliminary gate-to-gate LCI for hydrogen peroxide by the anthraquinone process (issue #170): design basis, a balanced BFD/PFD, equipment and line lists, and an inventory with every background left unmapped. All of it is committed in 4 commits on `case/hydrogen-peroxide-1`. `cheme validate` gives 0 errors and 0 warnings, and the PFD balances in every block and step. The main limits: energy closure can't be checked in cheme yet, and `cheme maturity` reaches no level because all feeds and separator specs are my assumptions.

**Design basis (all ASSUMED):** 50 kt/a H2O2 (100 %) sold as a 50 wt% solution, 8000 h/a. Hydrogen enters as a boundary feed and could come from `hydrogen-1` or as by-product from `chlor-alkali-1`. The working solution is 2-ethylanthraquinone in a C9 aromatic / diisobutylcarbinol solvent mixture.

**Flowsheet:** 5 blocks, 18 steps, 36 material and 11 energy streams, with the recycles closed (working-solution loop, distillate back to the extraction, recovered solvent). The two reactors are fixed-conversion models that cheme solves itself. Separator outlets and duties come from `scripts/hp_balance.py`.

| Per tonne of H2O2 | This design | Range in the EU LVOC BREF 2017 |
|---|---|---|
| Hydrogen | 63.5 kg (stoichiometric 59.3) | 60–70 kg |
| Air | 4215 Nm3 | 3300–4600 Nm3 |
| Demineralised water | 1.19 t | 1–2 m3 |
| Electricity | 355 kWh | — |
| Total energy | about 3.6 GJ | 2.9–5.7 GJ |
| Waste water | 0.41 t, 0.15 kg organic carbon | 0.1–3 m3 |
| Make-ups | quinone 1.0 kg, solvent 2.5 kg, alumina 6 kg | 0.7–1.6, 2–5, 4–20 kg |

The concentrator reboiler needs 1.71 GJ/t, above the BREF's 0.3–1.5 GJ/t, because I assumed no heat recovery; vapour recompression is the obvious fix later.

**LCI (per 1 kg of 50 wt% product):**
- **Inputs:** H2 0.0318 kg, demineralised water 0.596 kg, steam used directly 0.117 kg, electricity 0.177 kWh, LP steam heat 0.237 kWh.
- **Outputs:** heat to cooling water 1.23 kWh, off-gas 2.26 kg (VOC 4.9e-5 kg), H2 vented 3.2e-4 kg, waste water 0.205 kg, spent alumina 0.0045 kg.
- **Consumables outside the flowsheet**, assumed within BREF ranges: nitric acid, caustic soda, activated carbon, ion-exchange resin, palladium.
- **Balances:** mass closes (43 433 kg/h in and out) and every element closes within 0.01 %. cheme still reports the element balance "not assessable", because the consumables have no composition.
- **Gaps:** 23, all backgrounds missing, each with a description of the activity it should link to; cheme classes the result as partial.
- **Library LCI build:** `scripts/build_lci.py --strict` exits 1, but the cause is the environment, not this process. It lists 15 gaps for this process and no errors. The only warning left for it is "cut-off criteria not checked" (missing core extra), and the same warning appears for every process.
- **Overrides in `lca/mappings.yaml`:** LP steam counted as heat in kWh, as `nitric-acid-1` does. I also turned off automatic supplier linking for H2 and direct steam, because the build was otherwise picking `chlor-alkali-1` for H2 and `ammonia-1` for steam on its own. Choosing the real supplier is your call.

**Files produced:** in `processes/hydrogen-peroxide-1/`: `process/` (design basis, materials, reactions, flowsheet, generated BFD.xml and PFD.xml), `scripts/hp_balance.py`, the equipment and line lists, `lca/` (lca.yaml, mappings.yaml and the generated outputs), `process.yaml`, `plant.yaml`, `DESIGN.md` (D-001 to D-013 plus a source register) and `PROGRESS.md`. No P&ID was drawn, and there was no template reference sheet to remove.

**Sources:**
- **Main source:** the EU LVOC BREF 2017 (doi:10.2760/77304), chapter 12. Each value is cited by section or table in my own words; no tables copied.
- **Reaction heats:** NIST WebBook formation enthalpies.
- **Identities:** PubChem.
- **Not read:** Ullmann's and Campos-Martin 2006 are listed as leads only.

**Key assumed values:**
- 45 % of the quinone hydrogenated per pass (the BREF says below 60 %).
- Complete oxidation, 30 % excess oxygen, 1 % of the hydrogen vented.
- 97 % of the H2O2 recovered into a 40 wt% crude.
- Reflux ratio 0.3.
- Off-gas VOC 20 mg C/Nm3.
- Oxidation heat 77.5 kJ/mol from the BREF; hydrogenation heat −110.3 kJ/mol worked out from that, not measured.
- No H2O2 decomposition beyond what the catalyst destroys.
- Fugitive and storage solvent losses not modelled.

**Missing from the shared chemicals registry** (for the consolidated PR): hydrogen-peroxide (with a 50 wt% grade), 2-ethylanthraquinone, the C9 aromatic solvent, diisobutylcarbinol, activated alumina, demineralised water, nitric acid, sodium hydroxide, activated carbon, ion-exchange resin, palladium catalyst. Biosphere identities are also missing for trimethylbenzene, diisobutylcarbinol and hydrogen emitted to air.

**Open inputs and blocked steps:**
- **Energy balance:** no property package in core covers the working solution or aqueous H2O2 (core #315).
- **Extraction:** it is a specified split; an equilibrium calculation needs sourced parameters for this system (core #369).
- **Core bug:** `cheme process build` 0.8.0 crashes on a step of class `Pumping`. I used `TransportingFluids` for P-101 as a workaround; this should be reported to core.
- **Choices for you:** the hydrogen and steam suppliers, and the site.
- **Data still needed:** working-solution data (quinone loading, solvent ratio, water solubility) and H2O2 decomposition losses.

**Recommended next stage:** get a review, then decide the suppliers and link the backgrounds once the registry entries exist. After that, the heat-recovery case for the concentrator and a 70 wt% product case. Then rerun the extraction and energy balances once core #369 and #315 support this system.

Merge pending: the branch is 4 commits ahead of `main`, with no review and no stage sign-off.

STATUS: DONE