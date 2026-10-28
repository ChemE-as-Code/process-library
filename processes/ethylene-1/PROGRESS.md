# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | DESIGN.md, PROGRESS.md, process.yaml, design-basis.yaml | source register, decisions D-001 to D-018, manifest (internal, concept, unreviewed), design basis | record the route, basis and assumptions |
| 2026-10-28 | lca/lca.yaml, lca/mappings.yaml, lca/* (generated) | preliminary gate-to-gate LCI per kg ethylene, all backgrounds unmapped (gaps), combustion emission estimates from BREF/IPCC | scope item 4; ADR 0022 gaps |
| 2026-10-28 | equipment/equipment-list.yaml | 20 PFD items | resolve the flowsheet links |
| 2026-10-28 | process/flowsheet.yaml, reactions.yaml, materials.yaml, simulation.yaml, BFD/PFD | balanced BFD/PFD of the ethane cracker; propane recycle on its own coil (block CRK3) | scope items 2-3; unique reaction extents (D-005) |
| 2026-10-28 | scripts/balance.py | heat and material balance script (recycles, firebox) | source of the ASSUMED separator values (D-006) |
| 2026-10-28 | all | scaffold from cheme init and the process template | start of ethylene-1 |
