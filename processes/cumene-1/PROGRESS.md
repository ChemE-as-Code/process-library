# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-11 | process/BFD.xml, process/PFD.xml (generated), lca/lca.yaml, lca/mappings.yaml, lca/ outputs (generated), README.md; acetone-1 lca/dataset.yaml and lca/manifest.json (generated) | origin/main merged (core v1.11.0, c21e6c7): BFD/PFD rebuilt with generator 7; supplier candidates main added since (btx-1 for benzene, propylene-pdh-1 for propylene) named in the gap notes and mappings, keys unchanged; LCA rewritten (input hashes and notes only, results unchanged); acetone-1's dataset rewritten for its process.yaml hash | bring PR #325 up to date with main |
| 2026-11-03 | process.yaml, README.md, DESIGN.md D-012 to D-014; benchmarks/aromatics.yaml, REFERENCE.md, coverage.yaml; acetone-1 process.yaml and lca/mappings.yaml | manifest rewritten for the plant (maturity concept, validation notes on the unqualified simulation, lca.source none); benchmark bound to the new dataset; acetone-1's feed:CUM linked to product:CUMENE | the pilot became a plant folder (#313) |
| 2026-11-03 | lca/lca.yaml, lca/dataset.yaml (generated), lca/mappings.yaml, scripts/allocation_exergy.py; lca/datasets/ removed | flowsheet-derived LCI per kg cumene, exergy allocation (cumene 97.1 %), 6 gaps, omissions declared; Tier 0 dataset retired | D-013 |
| 2026-11-03 | equipment/equipment-list.yaml, piping/line-list.yaml, scripts/line_sizes.py | 13 items, 27 lines with ASSUMED design conditions and DN | concept lists (D-014) |
| 2026-11-03 | process/simulation.yaml, process/simulation-run.json, process/flowsheet.yaml, process/BFD.xml, process/PFD.xml | DWSIM run of the whole plant (converged; benzene loop closed at the drum; TIPB surrogate; C-204 rigorous; LP steam 250 kPa(a)); values filled, BFD/PFD built | D-011 |
| 2026-11-03 | process/*.yaml, scripts/cumene_balance.py, DESIGN.md D-001 to D-010 | design basis, materials, reaction evidence and route selection, reactions, flowsheet (2 blocks, 18 steps, 29 + 14 streams), independent balance script | concept design to a balanced PFD (#313) |
| 2026-11-03 | (all) | scaffold from cheme init (core v1.4.1) | start of the plant folder |
