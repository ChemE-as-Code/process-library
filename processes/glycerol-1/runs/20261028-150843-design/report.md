I've taken glycerol-1 from design basis to a balanced BFD/PFD and a preliminary gate-to-gate LCI, all committed on `case/glycerol-1` (3 commits, not pushed). `cheme validate` shows 0 errors and 0 warnings. A merge is pending: the branch has not been reviewed.

**Files produced** (all in `processes/glycerol-1/`):
- **Process:** `process/design-basis.yaml`, `materials.yaml`, `reactions.yaml`, `flowsheet.yaml` (5 blocks, 9 steps, 34 streams), `simulation.yaml` (only marks the two reactors as having no heating or cooling), and the generated `BFD.xml` and `PFD.xml`.
- **Balance script:** `scripts/glycerol_balance.py`, an independent mass and energy balance with each assumed parameter tied to a decision in DESIGN.md.
- **Lists and docs:** `equipment/equipment-list.yaml` (15 items), `process.yaml` (`publication.status: internal`, maturity `concept`, `unreviewed`), `DESIGN.md` (route memo, decisions D-001 to D-013, method and dependency table, source register, missing registry entries, open items), `PROGRESS.md`.
- **LCI:** `lca/lca.yaml`, `lca/mappings.yaml` (no overrides), and the written inventory files (`inventory.csv`, `gaps.csv`, `dataset.yaml`, `manifest.json`, results files).

**Route and balance results**
- **Route:** HCl acidulation, fatty-layer decanting, NaOH neutralisation, methanol column, vacuum dewatering, vacuum still at 1.5 kPa(a) with live steam, salt centrifuge, activated carbon bleaching, product cooler.
- **Scale:** 2,202 kg/h crude glycerol gives 1,250 kg/h glycerol at 99.7 wt% (10,000 t/a). Glycerol recovery is 94.6 %.
- **Co-products and wastes:** 674 kg/h methanol and 181 kg/h fatty layer go back to the biodiesel plant. Wastes are 84 kg/h salt cake, 55 kg/h still residue, 5 kg/h spent carbon and 241 kg/h wastewater.
- **Balances:** every block and step closes on mass, and on components using the reaction extents. Mass and C/H/O/Na/Cl close to within 0.01 % in both the script and `cheme assess lca --balance` (2,490.5 kg/h in and out).
- **Gates:** concept is 6 ok and 1 fail (the plot plan, which is out of scope).
- **`cheme maturity`:** reaches no level yet, so the `concept` claim in `process.yaml` draws a warning. The "balanced" level fails because separator outputs are specified values rather than a sourced model. The "sourced" level fails because the feed flows are assumed: the reagent flows are design results, so they can never be "given".

**Energy (estimated by the script, ASSUMED):** per tonne of product, 756 kWh of steam heat (424 LP, 332 HP), 105 kg of live steam, 50 kWh of power and 803 kWh to cooling water, about 885 kWh/t in total. That is the same order as a planned 99.7 % refinery quoted at about 1,000 kWh/t (cited in Attarbachi et al. 2024).

Energy closure is the gated step. `cheme process energy` finds every block not evaluable, and no property package covers glycerol, methanol, water or NaCl. It needs core #315 (polar mixture enthalpies), #364 (which covers aqueous NaCl only) and #365 (salt crystallisation). Extraction (#369) is not used.

**LCI (per kg refined glycerol)**
- 13 exchanges, every background left unmapped: crude 1.046 kg, HCl 32 % 0.069 kg, NaOH 50 % 0.0044 kg, activated carbon 0.0012 kg, live steam 0.062 kg, LP heat 0.252 kWh, HP heat 0.197 kWh, power 0.030 kWh, cooling water 0.477 kWh, plus salt, still residue, spent carbon and wastewater.
- These amounts are after mass allocation; glycerol's share is 0.594. The allocation choice is recorded as a deviation from the library's preferred method, because no prices were sourced.
- Biogenic carbon fraction of the crude is 0.710.
- `--coverage` rates it a partial screening carbon footprint with 13 gaps.
- The inventory boundary flows equal the flowsheet's boundary streams.
- The strict library LCI build lists all 13 glycerol exchanges as gaps with no errors. It still exits 1, partly from warnings for other processes in this environment, and partly from one glycerol warning: the dataset core writes leaves out the allocation method when it is mass.

**Sources**
- **Feed composition:** Thompson & He (2006), Appl. Eng. Agric. 22(2), Tables 1, 3, 5 and 6, soybean oil. Recorded as given: glycerol 59.8 %, methanol 29.3 %, catalyst 2.85 %, fatty matter 7.98 %. Table 5's carbon content is inconsistent with this composition; that is flagged in DESIGN.md.
- **Industrial front end, feed variability, bleaching and energy comparisons:** Attarbachi et al. (2024), IECR, CC BY 4.0.
- **Still pressure, water and salt limits, pH and temperature limits:** Molecules review (2026), section 4.1.
- **Traded grade 99.5–99.7 %:** RSC Advances review (2022).
- Ullmann was not read.

**Key ASSUMED values:** 10 % excess HCl; 97 % of fatty matter to the decanted layer; methanol recovery 99.5 % at 99.5 wt%, reflux ratio 1.0; dewatering to 5 % water; still at 1.5 kPa(a) and 448 K, live steam 0.10 kg/kg, 95 % of glycerol to distillate; 90 % of salt removed as crystals; carbon 2 kg/t; power 50 kWh/t; glycerol heat of vaporisation 85 kJ/mol; capacity and 8,000 h/a.

**Missing registry entries** (for the consolidated shared PR): glycerol (USP grade), crude glycerol, methanol, hydrochloric acid 32 %, sodium hydroxide 50 %, activated carbon, sodium chloride (salt cake), fatty matter, and a glycerol family. There are also no shared LCI mapping entries yet for crude glycerol, caustic soda, activated carbon and the three waste treatments.

**Open inputs:** water and ash content of an industrial feed, plus a high-ash second case; separator models; NaCl solubility in glycerol; prices for allocation; vent and tank methanol emissions; heat recovery from the glycerol condenser.

**Recommended next stage:** add sourced prices and an economic or substitution sensitivity, and a second feed case. Once core #315 and #364 qualify these mixtures, replace the specified splits with modelled ones to reach "balanced" and evaluate energy closure. Then do a human review of this branch and merge it.

STATUS: DONE