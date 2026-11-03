# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-03 | equipment/equipment-list.yaml, DESIGN.md D-011, D-012 | 18 items with ASSUMED design conditions, every PFD link resolved; core findings listed | concept lists |
| 2026-11-03 | process/flowsheet.yaml, simulation.yaml, simulation-run.json, BFD.xml, PFD.xml, plant.yaml, checks/checks.yaml, scripts/eb_balance.py, DESIGN.md D-014 | flowsheet (2 blocks, 16 steps, 25 + 12 streams); DWSIM run of the whole plant converged (Peng-Robinson, unqualified); reactor heat and columns within about 1 % of the script, mixers M101/M103 13 to 16 K hotter (I-07); BFD/PFD generated | balanced PFD and simulation (issue #313) |
| 2026-11-03 | process/design-basis.yaml, materials.yaml, reactions.yaml, reaction-evidence.yaml, scripts/eb_balance.py, DESIGN.md D-001 to D-010 | design basis (400 kt/a, ASSUMED), five components with model compounds for PEB and flux oil, four lumped reactions, reaction evidence (BREF chapter 5, US5493065A Example 7) with the model basis, independent balance script (benzene 0.7374 t/t, ethylene 0.2669 t/t, flux oil 4.3 kg/t) | concept design basis and reaction model (issue #313) |
| 2026-11-03 | (all) | scaffold from cheme init (core v1.4.1) next to the manifest-only pilot | start of the plant folder |
