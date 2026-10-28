# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | DESIGN.md, PROGRESS.md | Route/boundary memo, decisions D-001 to D-014, model evidence, source register, open inputs and missing registry entries | #180 concept stage record |
| 2026-10-28 | lca/ | Preliminary gate-to-gate LCI per kg air-dry pulp: every flowsheet exchange, backgrounds declared missing with the activity to connect, export credited by substitution (missing), biogenic/fossil CO2 apart; outputs written; local mappings.yaml | #180 step 4 |
| 2026-10-28 | process/flowsheet.yaml, scripts/kraft_balance.py | Lime kiln burner as its own step K902 (combustion gas S50, heat Q20) | keep fossil and biogenic carbon from mixing in one reactive step (D-012) |
| 2026-10-28 | process/, scripts/kraft_balance.py, equipment/equipment-list.yaml, process.yaml | Design basis, lumped materials and reactions, independent balance, flowsheet (10 blocks, 16 steps), BFD/PFD built, equipment for the PFD links | #180 steps 1-3 |
| 2026-10-28 | all | Scaffold from cheme init | new case kraft-pulp-1 |
