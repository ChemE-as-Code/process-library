# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | lca/lca.yaml, lca/mappings.yaml, lca/* (generated) | Preliminary gate-to-gate LCI per kg HBr in 48 wt-% acid: every foreground exchange from the flowsheet, all backgrounds `missing:` (8 gaps), vent emissions, declared exclusions; mass, Br and H close (D-012) | issue #130 scope step 4 |
| 2026-10-28 | DESIGN.md, process.yaml | Route/boundary memo, source register, reaction and model evidence, decisions D-001..D-012, results, gated steps, open inputs and missing registry entries; Atlas manifest (internal, concept, unreviewed) | issue #130 scope steps 1, 3, 5 |
| 2026-10-28 | process/flowsheet.yaml, simulation.yaml, BFD/PFD | R102 finishing bed as an adiabatic ideal-gas equilibrium reactor instead of an unsourced conversion override (Br2 3.6e-12 mol/mol out) | model basis rests on data (cheme maturity) |
| 2026-10-28 | process/*.yaml, scripts/balance.py, equipment/equipment-list.yaml, BFD/PFD | Design basis, materials, reaction, catalyst; BFD (3 blocks) and PFD (7 steps, 12 material and 6 energy streams) with closed balances; independent balance script; PFD equipment list | issue #130 scope step 2 |
| 2026-10-28 | all | Scaffold from `cheme init` and the process.yaml template | start of the case |
