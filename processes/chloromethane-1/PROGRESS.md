# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-12 | DESIGN.md | source register S4 no longer calls the package values open data: it names chemicals 1.5.2, ATcT 1.112 (`ATCT_G`) for the formation enthalpies, the packaged CRC table `heat_capacity.CRC_standard_data` for the entropies and `Cp_data_Poling` for the cp polynomials, with the CRC Handbook and Poling's 5th ed. as the underlying works (not read) | issue #426: ADR 0037 sweep of the older source registers; text only, no number changes |
| 2026-10-28 | DESIGN.md, process.yaml | route/boundary memo, source register S1-S9, decisions D-001 to D-014, open items I-01 to I-08; Atlas manifest (internal, concept, unreviewed, honest notes) | issue #151 concept run |
| 2026-10-28 | lca/lca.yaml, lca/mappings.yaml, lca/*.csv, dataset.yaml, manifest.json | preliminary gate-to-gate LCI per kg methyl chloride: 9 exchanges, all backgrounds gaps with the activity to link; mass, element and carbon balances closed | scope item 4 (D-013, D-014) |
| 2026-10-28 | equipment/equipment-list.yaml | 10 tags, one per PFD step | process links resolve (D-012) |
| 2026-10-28 | process/*.yaml, process/BFD.xml, process/PFD.xml, plant.yaml, scripts/balance.py | design basis, materials (with ideal-gas data), reactions, flowsheet (4 blocks, 12 steps, two recycles, purge), generated BFD/PFD | balanced concept PFD (D-001 to D-011) |
| 2026-10-28 | (scaffold) | cheme init and the process template | start of chloromethane-1 |
