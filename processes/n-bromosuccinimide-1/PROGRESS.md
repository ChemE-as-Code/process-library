# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-05 | process/, scripts/balance.py, DESIGN.md, lca/ | review fixes: second-order rate law and post-reaction to 0.999 conversion (accumulation 3.75 %, MTSR 278.9 K, cycle 5.30 h, 1495 batches/a of 334.41 kg); the dilution and deprotonation heat in M-101 (Q1 10.8 kW, Q2 5.3 kW); R-101 sized by the recipe (2 m3) and its agitator on its own stream; rinses as a per-batch consumable; D-013 dedicated train; sources reworded; core 1.7.0 | review of #370 |
| 2026-11-05 | process.yaml, lca/ | Atlas manifest (public, concept, unreviewed); preliminary gate-to-gate LCI per kg NBS, bromine and caustic linked to bromine-1 and chlor-alkali-1, the other backgrounds gaps (inventory.csv, gaps.csv, dataset.yaml written by cheme) | issue #140 scope |
| 2026-11-05 | DESIGN.md | source register, decisions D-001..D-012, method/dependency table, lessons L-1..L-5 for core#158, open inputs | record the route, the batch basis, the hazard result and what core could not do |
| 2026-11-05 | process/, scripts/balance.py, equipment/ | design basis, materials, reactions, semi-batch flowsheet (3 blocks, 8 steps, 16 streams), batch recipe (cycle 5 h, 1584 batches/a), BFD/PFD built; equipment list as far as the PFD | balanced concept PFD of the first batch entry (core#158 packages 1 and 2) |
| 2026-11-05 | all | scaffold from cheme init and the process template | start of the case |
