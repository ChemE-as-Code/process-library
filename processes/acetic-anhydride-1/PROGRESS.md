# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | lca/lca.yaml, process.yaml | steam without inventory_key; zero CO/C2H4/ketene emissions elementary instead of free | the library's strict LCI build refused both (unit mismatch, uncurated free emission) |
| 2026-10-28 | DESIGN.md, PROGRESS.md, lca/README.md | decisions D-001 to D-014, source register, open inputs | record the concept run (issue #131) |
| 2026-10-28 | lca/ | preliminary gate-to-gate LCI per kg acetic anhydride; 11 backgrounds declared missing; inventory written, mass/element/carbon balance closed | scope step 4 (D-014) |
| 2026-10-28 | process.yaml | manifest: internal, concept, unreviewed, references | scope step 1 |
| 2026-10-28 | process/, scripts/ac2o_balance.py, BFD, PFD, equipment and line lists | design basis, materials, reactions, flowsheet (4 blocks, 16 steps), balance script, lists | balanced BFD/PFD (D-001 to D-013) |
| 2026-10-28 | all | scaffold from cheme init and the process template | start of the case |
