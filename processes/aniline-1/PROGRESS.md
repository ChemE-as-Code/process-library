# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | DESIGN.md, PROGRESS.md, lca/README.md | decisions D-001..D-013, source register, basis, method and dependency tables, missing registry entries | record of the concept run (issue #148) |
| 2026-10-28 | lca/ | lca.yaml (FU 1 kg aniline, gate-to-gate, backgrounds unmapped, exergy allocation with the steam export), mappings.yaml (no overrides yet), inventory, gaps, dataset, manifest written by cheme assess lca | preliminary gate-to-gate LCI |
| 2026-10-28 | process/flowsheet.yaml, scripts/aniline_balance.py | decanter cooler Q12 (0.48 MW) added | closes the plant energy balance to the pump work |
| 2026-10-28 | equipment/, piping/, process/design-basis.yaml, process.yaml, process/simulation.yaml | lists for the PFD items, design basis, Atlas manifest (internal), R-101 declared adiabatic | concept deliverables |
| 2026-10-28 | process/ (materials, reactions, catalysts, flowsheet, BFD, PFD), scripts/aniline_balance.py, scripts/allocation_exergy.py | components, three reactions, Pd catalyst, balanced flowsheet with recycle, generated BFD/PFD | balanced concept PFD |
| 2026-10-28 | all | scaffold from cheme init and the process.yaml template | start of the case |
