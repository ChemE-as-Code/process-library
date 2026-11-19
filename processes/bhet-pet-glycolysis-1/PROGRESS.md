# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | coverage (library coverage.yaml, docs/coverage.md), REFERENCE.md, chemicals/chemicals.yaml, benchmarks/chemical-recycling.yaml | coverage item `bhet` at provisional rank 133 (the wave's place, renumbered on merge), the REFERENCE row, registry slugs `bis-2-hydroxyethyl-terephthalate` and `zinc-acetate`, two KPIs with no open reference | shared rows of issue #516 |
| 2026-11-19 | process.yaml, lca/, README.md | Atlas manifest (public, CC-BY-4.0, concept, unreviewed); preliminary gate-to-gate LCI per kg of BHET, the glycol linked to ethylene-glycol-1, the make-up water to demineralised-water-1, steam as heat, the rest gaps (inventory.csv, gaps.csv, dataset.yaml written by cheme) | issue #516 scope |
| 2026-11-19 | DESIGN.md | source register SRC-1..8, decisions D-001..D-013 (route with rejected alternatives, capacity, batch basis, feeds, glycolysis, quench and oligomers, crops, separations, utilities, wastes, thermal screening, LCI, dedicated train), method table, core limits L-1..L-7, open inputs | record the route, the batch basis, the energy finding and what core could not do |
| 2026-11-19 | process/, equipment/, checks/checks.yaml, plant.yaml | design basis, materials, reactions (GLY, OLF, DEP, DSO, DEG), flowsheet (5 blocks, 18 steps, four design specifications, tears S19, S20, S21, S29), batch recipe (3944.66 kg every 6.248 h, 1268 batches/a), R101's MTT at the glycol's boiling point, BFD/PFD built; equipment list as far as the PFD; the template's accept entry removed | balanced concept PFD of EP 0 723 951 A1 method B (Example 2) |
| 2026-11-19 | all | scaffold from cheme init (core b97a833, v1.13.0) | start of the case (#516) |
