# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | DESIGN.md, README.md, process.yaml; library coverage.yaml, docs/coverage.md, REFERENCE.md, chemicals/chemicals.yaml (polystyrene), docs/registry.md, tests/test_registry.py, benchmarks/polymers.yaml, tests/test_polystyrene_1.py | decisions D-001 to D-012 with the source register and core limits L-1 to L-6, the public README and the Atlas manifest; the registry slug polystyrene (repeat unit C8H8, CHEBI:53276); two GPPS KPIs from the POL BREF (styrene inside, energy explained); coverage rank 54 covered by this folder | concept deliverables (#467) |
| 2026-11-19 | lca/lca.yaml, lca/mappings.yaml, lca/ outputs | preliminary gate-to-gate LCI per kg of pellets: styrene to styrene-1, hot oil as heat from natural gas, nitrogen (POL BREF 0.022 kg/kg) to asu-1 with its release, purge and vent to thermal oxidation (gaps); emission exclusions (D-011) | the LCI of the PFD |
| 2026-11-19 | equipment/equipment-list.yaml, process/design-basis.yaml | 13 items with ASSUMED sizes (residence times, no rate law); the design basis with the POL BREF's facts | PFD links resolve; concept gate |
| 2026-11-19 | process/materials.yaml, reactions.yaml, flowsheet.yaml, BFD.xml, PFD.xml, scripts/ps_balance.py | 4 components (polystyrene per repeat unit), the polymerisation (710 kJ/kg), 3 blocks, 13 steps, 20 material and 10 energy streams; specs `rate` (100 kt/a) and `purge` (7 wt% EB in the reactor feed) with the tear S2 solved by propagate; the reactors' duties by core; the independent balance script for the feed temperature and the heats of E-101, E-103 and the pelletiser (D-001 to D-009) | concept PFD |
| 2026-11-19 | (all) | scaffold from cheme init (core 1.12.0, pin 0e85885) | start of the case (#467) |
