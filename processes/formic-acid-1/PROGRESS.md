# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | lca/mappings.yaml | `feed:LPS` uses the shared `steam-heat` entry (kWh of heat) instead of the registry slug `steam` (kg) | CI (PR #220, library tooling tests): the Atlas build refused the LPS exchange, mapped to `steam` in kg but counted in kWh |
| 2026-10-28 | DESIGN.md, process.yaml, PROGRESS.md | Source register (SRC-1..8), decisions D-001..D-014, Atlas manifest (internal, concept, unreviewed) | Document the concept stage of issue #185 |
| 2026-10-28 | lca/lca.yaml, lca/mappings.yaml, lca/*.csv, dataset.yaml, manifest.json | Preliminary gate-to-gate LCI per kg formic acid 85 wt%, every background unmapped (8 declared gaps + 3 uncharacterised emissions); mass, element and carbon-origin balances closed | Case scope step 4 (D-012) |
| 2026-10-28 | equipment/equipment-list.yaml, piping/line-list.yaml, process/flowsheet.yaml | 16 items of the PFD with duty notes; SP101 link removed (a line branch); line list stays empty until P&IDs | Case scope step 5 |
| 2026-10-28 | process/materials.yaml, reactions.yaml, flowsheet.yaml, simulation.yaml, design-basis.yaml, BFD.xml, PFD.xml, scripts/balance.py | Design basis, 11 components, 6 reactions, 4-block / 17-step PFD with 29 material and 19 energy streams and four recycles, balance script; every block and step balance closes | Case scope steps 1-3 (D-001..D-011) |
| 2026-10-28 | all | Scaffold from cheme init and the process template | Start of formic-acid-1 |
