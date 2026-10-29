I've finished the concept stage for alumina-1 (issue #178): a design basis, a balanced BFD/PFD, and a preliminary gate-to-gate inventory (LCI) per kg of alumina. Everything is committed on `case/alumina-1` in five commits; nothing is pushed. `cheme validate` reports 0 errors and 0 warnings, and every concept gate passes except the out-of-scope plot plan. The main caveat: caustic soda use and steam use are probably underestimated. Both are explained below.

**What was built**
- **Plant:** 3000 t/d smelter-grade alumina (99.0 % Al₂O₃, 0.40 % Na₂O), 8400 h/a, both ASSUMED.
- **Route:** Guinean gibbsitic bauxite → grinding and pre-desilication → digestion at 418 K with flash heat recovery → settler, 6-stage counter-current washing, residue filter presses → seeded precipitation with seed recycle → hydrate filtration → spent-liquor evaporation and caustic make-up → natural-gas gas suspension calciner.
- **Files:**
  - `process/`: design basis, materials, reactions (8), flowsheet, simulation specs; the BFD and PFD generated with `cheme process build`.
  - `scripts/bayer_balance.py`: my own balance script, which solves all the recycles; the flowsheet values come from it.
  - Equipment list (19 items) and line list (32 lines); `lca/` (inventory, gaps, dataset, `mappings.yaml`); `DESIGN.md` (D-001 to D-010 and a source register); `PROGRESS.md`; `process.yaml` (internal, concept, unreviewed).
- **Liquor model:** cheme cannot handle caustic aluminate liquors yet, so the liquor is modelled as NaOH + NaAlO₂ + water. Digestion and precipitation are set by ASSUMED alumina-to-caustic ratios rather than calculated.

**Balance results**
- All 6 blocks and 19 steps balance, and the 8 reactions balance by extents.
- The script's whole-plant element balance (Al, C, Ca, Fe, H, N, Na, O, Si, Ti) closes, and the recycle loop closes.
- Spent-liquor circulation is 2006 t/h, about 16 t per t of alumina.

**Inventory per kg alumina**

| Exchange | Amount |
|---|---|
| Bauxite (wet) | 2.193 kg |
| Quicklime | 0.052 kg |
| Caustic soda, 50 % solution | 0.031 kg (0.0155 kg NaOH) |
| Fresh water | 0.134 kg |
| Natural gas | 0.056 kg |
| Air (no burden) | 1.110 kg |
| Electricity | 0.152 kWh |
| MP steam heat | 0.462 kWh |
| LP steam heat | 0.210 kWh |
| Heat to cooling water | 0.567 kWh |
| Bauxite residue cake | 0.758 kg (0.530 kg dry) |
| CO₂ to air (fossil, calciner) | 0.154 kg |

- **Mass check:** inputs 3.5767 kg = outputs 3.5767 kg. `cheme assess lca --balance` reports mass, element and carbon-origin balances closed.
- **Coverage:** "partial screening carbon footprint", because all 10 background datasets are left unmapped as declared gaps (none set to 0) — that was the brief for this stage.
- Calciner pollutants (NOx, CO, SO₂, dust) and liquor tank vents are declared as exclusions, not estimated.

**Values to treat with caution**
- **Caustic soda, 15.5 kg NaOH/t:** probably well below refinery practice. Only the sodium lost to the desilication product, the residue liquor and the product is counted; spills and impurity purges are not.
- **Steam, 2.4 GJ/t:** probably low. Total delivered energy is about 5.8 GJ/t against the IAI 2019 global average of about 10.5 GJ/t (which includes high-temperature digestion and older plants). Here steam is 0.9 times the calciner energy, where an ICSOBA paper puts it nearer 1.6 times.
- **Bauxite and residue are lower than the IAI averages** (2.685 t bauxite and 1.22 t residue per t alumina) because the chosen ore is high grade.

**Sources used**
- Bauxite assay: Zainudeen et al. 2023, Heliyon 9:e19070 (CC BY 4.0), Tables 5 and 6. Full text read.
- IAI 2019 LCI report: §3.4 (bauxite and residue per t alumina, bauxite moisture), §3.11.2.2 Table 4 (electricity 547 MJ/t), §3.11.2.3 (lime about 52 kg/t). Full text read.
- ICSOBA 2017 paper AA22 (calciner about 2.72 GJ/t) and 2024 paper AA05 (digestion at 145–150 °C, energy split): abstracts only; the PDF text could not be extracted.
- Formation enthalpies are recalled from the NBS tables and Robie & Hemingway, marked ASSUMED and not checked.

**Key ASSUMED values:** spent caustic 250 g/L, ratio 0.70 after digestion and 0.38 spent; 98 % of the gibbsite dissolved; liquor density 1.30 kg/L; washing (6 stages, wash ratio 1.6, cake 70 % solids); seed 250 g/L; hydrate cake 8 % water; calciner 2.8 GJ/t; heat recovery parameters; bauxite moisture 10 %.

**Gated steps and maturity**
- `cheme maturity` gives calculation maturity "none": feed flows are solved from the ASSUMED capacity, and the conversions and splits are assumptions rather than sourced values. The `concept` claim in `process.yaml` is therefore flagged as exceeding the evidence.
- Waiting on core: liquor chemistry and gibbsite solubility (core #364 and #365), gibbsite calcination energy (`cheme process furnace` refuses it; core #370 covers limestone only), and energy closure (no property package for these liquors and solids).

**Missing registry entries (for the consolidated PR)**
- `chemicals/chemicals.yaml`: alumina, bauxite, quicklime, caustic soda 50 %, bauxite residue.
- `lci/mappings.yaml`: bauxite, quicklime, sodium hydroxide 50 % (or a link to chlor-alkali-1), residue treatment.
- Taxonomy: there is no `alumina` family, so I used `aluminium` (same ISIC 2420).

**Open inputs:** a sourced liquor specification and soda-loss breakdown, a steam balance for a low-temperature refinery, calciner emission factors, flocculant and other reagents, and a fuller bauxite assay. The BFD's auto-layout is cluttered and its positions are not pinned yet.

**Recommended next stage:** an independent review of the BFD/PFD and inventory, then source the caustic losses and steam balance, connect the background datasets, and estimate the calciner emissions.

Merge pending: the branch needs a review and a merge by a human or the reviewer; no sign-off was written.

STATUS: DONE