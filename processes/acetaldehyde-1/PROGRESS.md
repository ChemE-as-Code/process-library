# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-12 | DESIGN.md | source register SRC-7 no longer calls the package values "open software data" under MIT: it names chemicals 1.5.2 / thermo 0.6.1 and, per component, the method `cheme chemistry thermo` used (formation enthalpies: ATcT 1.112 `ATCT_G` for ten components, the packaged CRC table `heat_capacity.CRC_standard_data` for acetic acid and crotonaldehyde, the Yaws table for 2-chloroacetaldehyde; entropies: the CRC table except YAWS for 2-chloroacetaldehyde and crotonaldehyde; cp: `Cp_data_Poling`, thermo TRCIG fits, a JOBACK estimate), and the CRC Handbook (2014 edition), Yaws' Thermophysical Properties of Chemicals and Hydrocarbons (2nd ed., 2014) and Poling 5th ed. as underlying works (not read) | issue #426: ADR 0037 sweep of the older source registers (missed in the first pass because the row said "open software data"); text only, no number changes |
| 2026-10-28 | lca/ (lca.yaml, mappings.yaml, inventory, coverage) | preliminary gate-to-gate LCI per kg acetaldehyde, every background unmapped (13 gaps), mass/element/carbon balances closed | issue #183 scope item 4 |
| 2026-10-28 | DESIGN.md, process.yaml, process/design-basis.yaml, equipment and line lists | source register, decisions D-001..D-012, Atlas manifest (internal), design basis, 17 equipment items and 26 lines from the PFD | issue #183 scope items 1, 3, 5 |
| 2026-10-28 | process/materials.yaml, reactions.yaml, flowsheet.yaml, BFD, PFD, scripts/acet_balance.py | concept PFD of the one-stage Wacker process (3 blocks, 16 steps, 33 material and 11 energy streams), mass and element balances closed in cheme | issue #183: balanced PFD as the basis of the preliminary LCI |
