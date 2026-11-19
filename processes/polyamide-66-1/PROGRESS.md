# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | coverage (library coverage.yaml, docs/coverage.md) | new coverage item polyamide-66 at the provisional rank 138, covered by this folder | issue #521 (ranks 127 to 139 reserved for this wave; renumbered on merge if taken) |
| 2026-11-19 | process.yaml, lca/, README.md | Atlas manifest (public, CC-BY-4.0, concept, unreviewed); preliminary gate-to-gate LCI per kg of pellets, the adipic acid linked to adipic-acid-1, the nitrogen to asu-1, the hot oil as heat from natural gas, the steam as heat, the diamine and the rest gaps (inventory.csv, gaps.csv, dataset.yaml written by cheme) | issue #521 scope |
| 2026-11-19 | DESIGN.md | source register SRC-1..7, decisions D-001..D-013 (route with rejected alternatives, capacity, batch basis, feeds, neutraliser, autoclave, pellets, utilities, wastes, thermal screening, LCI, dedicated train), method table, core limits L-1..L-5, open inputs | record the route, the batch basis, the hazard result and what core could not do |
| 2026-11-19 | process/, scripts/balance.py, equipment/, plant.yaml | design basis, materials (PA66 per repeat unit), reactions (NEUT, POLY), flowsheet (3 blocks, 9 steps, one design specification), batch recipe (5303.03 kg every 5.25 h, 1508.6 batches/a), balance script for Q2, Q3, Q5 to Q7, BFD/PFD built; equipment list as far as the PFD | balanced concept PFD of the batch autoclave route (EU POL BREF 9.2.2.3) |
| 2026-11-19 | all | scaffold from cheme init (core b97a833, v1.13.0) | start of the case (#521) |
