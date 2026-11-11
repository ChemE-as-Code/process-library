# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-06 | DESIGN.md | SRC-3 no longer calls the package values open data: it names chemicals 1.5.2 and thermo 0.6.1, the packaged CRC tables, and thermo's DIPPR_PERRY_8E correlation (Perry's 8th ed., not read) behind bromine's liquid density at 293 K, used as a single fact under library ADR 0037; no number changed | maintainer decision, ADR 0037 |
| 2026-11-06 | process.yaml, tests | `publication: {status: public, license: CC-BY-4.0}`, the maintainer's decision that every library entry is public (ADR 0036); the entry's test asserts public; lca/manifest.json and lca/dataset.yaml fingerprints of process.yaml renewed | publication policy |
| 2026-11-05 | process.yaml, DESIGN.md, process/ | review of #379: T101's heat stated as about 3 kJ per kg (0.1 kW, about 5 K in the still pot; it was written as 3 J), not counted; the avoided PBr5 credited to the reaction temperature above 100 C, not the bromine excess (D-001, description); flowsheet header names R101's 0.9999 target; `publication.status: internal`, publication left to the maintainers' own change (CONTRIBUTING) | reviewer findings; tests/test_phosphorus_tribromide_1.py |
| 2026-11-05 | process.yaml, lca/, benchmarks | Atlas manifest (concept, unreviewed); preliminary gate-to-gate LCI per kg PBr3, bromine and nitrogen linked to bromine-1 and asu-1, the other backgrounds gaps (inventory.csv, gaps.csv, dataset.yaml written by cheme); two KPIs with no_open_reference | issue #134 scope |
| 2026-11-05 | DESIGN.md | source register, decisions D-001..D-013 (dedicated train, batch basis, jacket-limited dosing, hazard result, distillation as a split to revisit with core#165), method table, lessons L-1..L-7 for core, open inputs | record the route, the batch basis, the hazard result and what core could not do |
| 2026-11-05 | process/, scripts/balance.py, equipment/ | design basis, materials, reactions, semi-batch flowsheet (2 blocks, 4 steps, 14 streams) with the heel as a recycle, batch recipe (cycle 11.26 h, 703.6 batches/a of 1421.23 kg), R-101 sized 1 m3 with its jacket checked; BFD/PFD built; equipment list as far as the PFD | balanced concept PFD of the second semi-batch entry |
| 2026-11-05 | all | scaffold from cheme init (core 1.7.0) | start of the case |
