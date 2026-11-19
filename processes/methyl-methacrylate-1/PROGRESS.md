# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | library: coverage.yaml, docs/coverage.md, REFERENCE.md, chemicals/chemicals.yaml, benchmarks/oxygenates.yaml, tests/test_methyl_methacrylate_1.py | new coverage item (provisional rank 119), REFERENCE row, registry entries methyl-methacrylate and hydrogen-cyanide, two KPIs with no_open_reference, a test reading the folder's files | the shared rows of a new entry (issue #477) |
| 2026-11-19 | lca/ | preliminary gate-to-gate LCI per kg MMA: every foreground exchange from the flowsheet, acetone-1, methanol-1 and sulfuric-acid-1 linked in lca/mappings.yaml, HCN and the weak acid water gaps, tail gas CO2 and SO2 elementary; written by `cheme assess lca --write` | D-012 |
| 2026-11-19 | DESIGN.md, README.md, process.yaml | source register SRC-1..7, decisions D-001..D-013, core limits L-1..L-4; Atlas manifest (public, CC-BY-4.0, concept, unreviewed) | record the route, basis and model basis (issue #477) |
| 2026-11-19 | process/*.yaml, BFD, PFD, equipment list, scripts/mma_balance.py | balanced concept flowsheet: ACH synthesis, amidation and conversion, esterification and stripping, purification, SAR furnace, waste heat boiler, gas cleaning, contact plant and absorbers; 6 blocks, 17 steps, 43 streams; two tears and three design specs; duties and furnace fuel from the script | D-001..D-010 |
| 2026-11-19 | (all) | scaffold from `cheme init` and the process.yaml template | start of the case |
