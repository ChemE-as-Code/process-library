# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | scripts/aa_balance.py, process/flowsheet.yaml, BFD.xml, PFD.xml, equipment-list.yaml, DESIGN.md, README.md, process.yaml, lca/*, benchmarks/oxygenates.yaml | Review of PR #527: liquid heat capacity no longer divided by 1000 and liquids referenced by chemicals' Hfg - Hfl (T-301 12.0 MW, C-401 13.4/13.3, C-404 4.3/4.7 MW); C-402's boil-up from the acetic acid stripping minimum x 1.25 (1.86/1.91 MW, was 0.56 at reflux 3); LP steam 19.6 MW, 1.57 kWh/kg; cooling water 34.4 MW; the 830 ml reflux read per hour marked ASSUMED (2.56 kg/kg); SRC-6 names thermo's methods and their works; propylene flammability and thawing statements sourced; process air free; README run block for this continuous plant; three benchmark KPIs | Confirmed review findings on PR #527 |
| 2026-11-19 | lca/lca.yaml, lca/mappings.yaml, lca/*.csv, dataset.yaml, manifest.json, scripts/allocation_exergy.py | Preliminary gate-to-gate LCI per kg of glacial acrylic acid; HP steam export allocated by exergy; propylene linked to propylene-pdh-1, toluene to btx-1, reboiler steam as heat from steam; the rest gaps | D-012 |
| 2026-11-19 | DESIGN.md, README.md, process.yaml, design-basis.yaml, equipment-list.yaml, checks/checks.yaml | Source register SRC-1..8, decisions D-001..D-013, core limits L-1..L-6, Atlas manifest (public, CC-BY-4.0, concept, unreviewed); the PFD rounding warning accepted (L-5) | Document the concept stage of issue #475 |
| 2026-11-19 | process/materials.yaml, reactions.yaml, flowsheet.yaml, simulation.yaml, BFD.xml, PFD.xml, scripts/aa_balance.py | 12 components, 11 reactions, 5-block / 13-step PFD with the toluene recycle at the tear S21; reactors and separators calculated by propagate, feeds and separator duties from the balance script | D-001..D-011 |
| 2026-11-19 | all | Scaffold from cheme init | Start of acrylic-acid-1 (issue #475) |
