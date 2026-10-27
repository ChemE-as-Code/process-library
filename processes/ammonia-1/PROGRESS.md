# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-27 | DESIGN.md, PROGRESS.md | Route/boundary memo, D-001..D-021, model and dependency table, source register, open inputs I-01..I-10, missing registry entries, core finding (build crash on HeatingInFurnace / SupplyingThermalEnergy) | #86 first stage: record decisions and gaps |
| 2026-10-27 | lca/lca.yaml, lca/*.csv, lca/dataset.yaml, process/simulation.yaml | Preliminary gate-to-gate LCI per kg NH3; every background declared missing with the activity to link; inventory written; adiabatic reactors declared for the boundary check | #86 scope item 4 |
| 2026-10-27 | process/*.yaml, BFD, PFD, scripts/plant_balance.py, equipment/equipment-list.yaml, process.yaml, plant.yaml | Design basis, materials (11 components, cp to 1500 K), reactions, flowsheet of 7 blocks / 51 steps with recycles, purge recovery, furnace and steam system; balances closed; BFD/PFD generated; 44 equipment items | #86 scope items 1-3, 5: balanced concept PFD |
| 2026-10-27 | (all) | Scaffold from cheme init and the process.yaml template | start of the case |
