# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-03 | plant.yaml, process/flowsheet.yaml, process/simulation.yaml, process/simulation-run.json, process/BFD.xml, process/PFD.xml | flowsheet (3 blocks, 27 steps, 43 material and 13 energy streams); DWSIM run (Peng-Robinson as a recorded substitution) converged, off-gas compression excluded, V-101/V-102/X-101 specified splits, C-303 rigorous; BFD/PFD generated | concept PFD with a simulation cross-check (D-012) |
| 2026-11-03 | process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, scripts/sm_balance.py | design basis (300 kt/a, LVOC BREF facts), 12 components, dehydrogenation and burner reactions, independent balance script (mass closure 1e-8, energy 7 kW of 264 MW) | concept design basis and balance (D-002 to D-011) |
| 2026-11-03 | (all) | scaffold from cheme init (core v1.4.1) around the manifest-only pilot | start of the concept plant folder (#313) |
