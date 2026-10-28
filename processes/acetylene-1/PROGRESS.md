# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | DESIGN.md, process.yaml, process/design-basis.yaml, lca/mappings.yaml, README.md | source register, decisions D-001..D-014, method/dependency table, open inputs; Atlas manifest (internal, concept, unreviewed); design basis; empty LCI overrides | document the concept design and its evidence (#184) |
| 2026-10-28 | lca/ | preliminary gate-to-gate LCI: lca.yaml (backgrounds unmapped, flue gas elementary, energy allocation), inventory, dataset, gaps, manifest, results written by cheme assess lca; mass, element and carbon balances closed | scope item 4 of #184 (D-013) |
| 2026-10-28 | equipment/equipment-list.yaml, process/simulation.yaml | equipment as far as the PFD needs (19 tags); burner, quench and cooling column declared adiabatic | process links resolve; utility assignment complete |
| 2026-10-28 | process/flowsheet.yaml, materials.yaml, reactions.yaml, BFD/PFD, scripts/balance.py | balanced concept flowsheet: 5 blocks, 26 steps, 61 streams; burner as sourced outlet-composition model; separators and duties from the independent balance | scope items 2-3 of #184 (D-004..D-012) |
| 2026-10-28 | all | scaffold from cheme init and the process manifest template | start of the case |
