# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-12 | process/flowsheet.yaml (terminal AMBIENT, Q5, step U101, Q1, Q2, R101 energy_port), scripts/balance.py, lca/lca.yaml, DESIGN.md D-006/D-007/D-011/D-014, BFD/PFD, lca/ | Furnace heat loss (3 %, 72.83 kW) is its own stream Q5 to AMBIENT (free in the LCI, 0.0221 kWh/kg HCl); Q2 (BFW pump, burner management, analysers) moved from R101 to its own step U101; Q1 written by core's conversion-step model: 2195.1 -> 2195.05 kW | #396: the model counted neither the loss nor Q2 as the script did (cheme.process-duty) |
| 2026-10-28 | DESIGN.md | route/boundary memo, source register, reaction evidence, D-001..D-013, gated steps, open inputs | concept stage record (#137) |
| 2026-10-28 | lca/, process.yaml | preliminary gate-to-gate LCI per kg HCl (all backgrounds missing), own mappings.yaml without overrides; Atlas manifest internal/concept/unreviewed | issue scope item 4 (D-013) |
| 2026-10-28 | process/, scripts/balance.py, equipment list, plant.yaml | design basis, materials, reactions, flowsheet (SYN, ABS; R101, C201, C202, P201), BFD/PFD built, balance script | balanced concept PFD (D-001..D-012) |
| 2026-10-28 | all | scaffold from cheme init | start of the case |
