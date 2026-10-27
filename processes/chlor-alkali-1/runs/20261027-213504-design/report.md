The concept stage is complete on `case/chlor-alkali-1` in 6 commits (scaffold, flowsheet, LCI, documents, two small fixes). Nothing is pushed or signed off. `cheme validate` shows 0 errors and 0 warnings. One problem: I accidentally created an untracked file outside the process folder, `build_fs_schema.json` at the worktree root. The hook refused my attempt to delete it, so please delete it yourself; it is not committed.

## Files produced
- **Process model:** `process/flowsheet.yaml` with 7 blocks, 22 steps, 46 material and 15 energy streams, plus the generated `BFD.xml` and `PFD.xml`. Supporting files: `materials.yaml` (17 components), `reactions.yaml` (7 reactions), `cells.yaml`, `simulation.yaml` (only declares the four brine-treatment reactors adiabatic) and `design-basis.yaml`.
- **Balance script:** `scripts/balance.py`, run with `cheme run`. It computes every stream; the values are written into the flowsheet as ASSUMED with the script as source.
- **LCI:** `lca/lca.yaml`, with `inventory.csv`, `dataset.yaml`, `gaps.csv` and `manifest.json` written by cheme.
- **Documents and lists:** `DESIGN.md` (decisions D-001 to D-013, evidence, sources, gated steps, open inputs), `PROGRESS.md`, `process.yaml` (status internal, maturity concept, unreviewed) and `equipment-list.yaml` (19 items, every PFD link resolves).
- **Line list:** left empty on purpose. The PFD has stream numbers, not line numbers; lines and pipe sizes come with the P&IDs.

## Results
- **Balances:** all 7 blocks and 22 steps close in mass. Where reactions are named, they also close in elements and extents. Overall, 47 830 kg/h goes in and 47 830 kg/h comes out.
- **Cell model (`cheme process cell`):** it reproduces the script exactly.
  - 605 cells × 16.19 kA at 3.0 V, current efficiency 0.965.
  - Cl2 formed: 12 502 kg/h; NaOH 14 104 kg/h; H2 368 kg/h.
  - DC power 29 382 kW (2 351 kWh/t Cl2); with rectifier losses, 2 423 kWh AC/t, inside the BREF bipolar range of 2 279–2 865.
  - The thermoneutral voltage is 2.310 V, and the cell gives off 7 041 kW of heat.
- **Energy:** energy balances outside the cell can't be evaluated, because core has no stream enthalpies for brine or caustic.
- **Gates:** every concept gate passes except `layout-plot-plan` (layout is out of scope). `cheme maturity` reports level `none`, the same as methanol-1, because the feed flows are design choices rather than sourced data. `process.yaml` says so.
- **LCI per kg of contained Cl2** (no allocation; Cl2, NaOH and H2 listed as co-products):

| Inputs | Amount | Outputs | Amount |
|---|---|---|---|
| Rock salt | 1.711 kg | Caustic 50 wt-% | 2.240 kg (1.120 kg NaOH) |
| Process water | 0.930 kg | Hydrogen | 29.5 g H2 |
| Demineralised water | 1.124 kg | Wastewater | 0.486 kg (57 g NaCl, 2.9 g Na2SO4) |
| HCl 32 wt-% | 33.9 g | Filter cake | 21.9 g |
| Soda ash | 7.7 g | Spent acid | 24.8 g |
| Sodium sulfite | 0.28 g | CO2 | 2.36 g |
| H2SO4 98 wt-% | 19.1 g | Cooling water heat | 0.865 kWh |
| Electricity | 2.600 kWh | | |
| MP steam | 0.98 kg | | |

  Mass, element and carbon balances close (3.795 kg in = out per 1.008 kg of product gas, the same ratio as the flowsheet). The coverage check classes it as "partial": 15 gaps, because every background is deliberately unmapped and each has a description of the activity it should link to.
- **Plausibility:** salt, steam, auxiliary chemicals, purge (0.33 m³/t) and filter cake all fall inside the BREF Chapter 3 ranges. That is a range check, not a validation.

## Sources
- **EU JRC Chlor-alkali BREF 2014 (DOI 10.2791/13138), read in full:** §2.4.1, §2.5.2–2.5.4, Table 2.4, Tables 3.2–3.12, §4.3.2.2.3, §4.3.2.3.2, §4.3.4.
- **Standard data:** CODATA Key Values (Cox et al. 1989) for heats of reaction; IAPWS steam tables.
- **Ullmann's:** cited but not read in this run.

## Key ASSUMED values
- Capacity 100 kt/a at 8000 h/a.
- Rock salt analysis: 98.8 % NaCl, 0.15 % CaSO4, 0.5 % insolubles.
- Current efficiency 0.965, with the rest of the current forming oxygen (1.8 vol-% O2 in the chlorine); element area 2.7 m².
- Rectifier efficiency 0.97; auxiliary power at the BREF median of 177 kWh/t.
- Evaporator steam economy 1.8; constant heat capacities for all duties outside the cell.
- Brine water activity 0.876; water partial pressure over the catholyte 28 kPa.
- Chemical excesses (soda ash, caustic), ion-exchange regeneration chemicals, spent acid at 75 wt-%.
- Feed brine sulfate 6 g/kg; this sets the purge.

## Missing registry entries (`chemicals/chemicals.yaml`)
chlorine, sodium-hydroxide, sodium-chloride (rock salt), hydrochloric-acid, sulfuric-acid, sodium-carbonate, sodium-sulfite, sodium-sulfate, demineralised water, brine sludge.

## Open inputs and gated steps
- **Open inputs:** a real salt analysis, the membrane vendor's brine specification, cell vendor data, the site (grid, steam source, cooling water), consumer conditions, and the dry chlorine water specification.
- **Gated by core#364:** caustic and chlorine-solubility properties, so energy closure outside the cell isn't possible.
- **`cheme process electrolyte` (core PR #394):** not in the installed cheme 0.8.0, so the brine water activity is an estimate.
- **`checks.yaml`:** still cites D-023, which has no DESIGN.md entry (info only). It was in the scaffold before this run.

## Recommended next stage
1. Upgrade cheme and replace the brine estimate with `cheme process electrolyte`.
2. Get a salt analysis and vendor cell data, so the feeds become sourced and maturity can reach a level.
3. Map the LCI backgrounds and state the allocation study.
4. Then draw the P&IDs, starting with the electrolysis and the brine loop.

A merge is pending: the branch needs an independent review and a human merge.
