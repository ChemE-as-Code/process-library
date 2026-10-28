# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | DESIGN.md, process.yaml, PROGRESS.md | source register, decisions D-001..D-012 with gated steps; Atlas manifest (internal, concept, unreviewed) | record the route, basis, model basis and open inputs (issue #150) |
| 2026-10-28 | lca/ | preliminary gate-to-gate LCI per kg solid NaCN: every foreground exchange from the flowsheet, backgrounds unmapped (`missing:`), stack CO2 elementary, emission gaps declared; inventory, gaps, dataset, manifest written by `cheme assess lca --write`; process-local `lca/mappings.yaml` | D-012 |
| 2026-10-28 | process/design-basis.yaml, process/simulation.yaml | design basis (6.25 t/h, feeds, products, utilities, assumptions); R-101 declared adiabatic | D-002..D-010; boundary check of the LCI |
| 2026-10-28 | process/*.yaml, BFD, PFD, equipment and line lists, scripts/nacn_balance.py | balanced concept flowsheet: Andrussow converter, waste heat boiler, ammonia recovery and recycle, HCN absorption and refining, neutralisation, crystallisation, drying, tail gas boiler; 5 blocks, 15 steps, 43 streams; lists for the PFD items | D-001..D-011 |
| 2026-10-28 | (all) | scaffold from `cheme init` and the process.yaml template | start of the case |
