# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-27 | lca/lca.yaml, lca/ outputs, DESIGN.md D-013 | CI fix: allocation `none` -> `shares` by mass of the contained products, with `allocation.deviation` (6086d5a) | PR #194 CI: the library build cannot export `none` for a multi-output dataset. The strict build now reaches the exchange mappings and still fails on entries only `lci/mappings.yaml` can supply (DESIGN.md section 7) |
| 2026-10-27 | Response 2026-10-27-pfd-lci-review#1 | Closed: shares on contained Cl2, NaOH 100 % and dry H2 (46.5/52.1/1.4 %), stated in `allocation.source`, the lca.yaml comment and D-013; core's stream-mass basis reported in DESIGN.md section 7 (6086d5a) | review |
| 2026-10-27 | Response 2026-10-27-pfd-lci-review#2 | Closed: lca/README.md points to DESIGN.md section 6; results.md now has a value (the mineral CO2 only), which section 6 explains (6086d5a) | review |
| 2026-10-27 | Response 2026-10-27-pfd-lci-review#3 | Closed for CO2: `elementary: {compartment: air, origin: fossil}`, characterised with GWP 1. NaCl and Na2SO4 to water stay `missing:` because no open characterisation is packaged (6086d5a) | review |
| 2026-10-27 | Response 2026-10-27-pfd-lci-review#4 | Closed (reason option): the cl2-vents exclusion says the BREF H2 upper range is for plants without an H2 consumer, which D-008 excludes. No amounts given (6086d5a) | review |
| 2026-10-27 | Response 2026-10-27-pfd-lci-review#5 | Open: `Stripping` and `Desorbing` are not DEXPI 2.0.1 classes, so C401 stays `SeparatingByFlash`. The maturity classification is reported to cheme-as-code in DESIGN.md section 7 (6086d5a) | review |
| 2026-10-27 | Response 2026-10-27-pfd-lci-review#7 | Closed: Ullmann's removed from process.yaml references and marked as background reading in DESIGN.md section 4 (e3d269d, 6086d5a) | review |
| 2026-10-27 | Response 2026-10-27-pfd-lci-review#8 | Closed: the D-023 example in checks/checks.yaml is now a placeholder. D-101 stays in the run record, which is not edited (e3d269d) | review |
| 2026-10-27 | Response 2026-10-27-pfd-lci-review#9 | Closed: D-004 says the electrolyser/rectifier split is open and does not change the per-kg figures (6086d5a) | review |
| 2026-10-27 | Response 2026-10-27-pfd-lci-review#10 | Closed: C-401 notes give 2 barg / full vacuum (e3d269d) | review |
| 2026-10-27 | DESIGN.md, PROGRESS.md, process.yaml, process/design-basis.yaml, equipment/equipment-list.yaml | Route/boundary memo, decisions D-001..D-013, evidence, source register, methods and gated steps; design basis; Atlas manifest (internal); 19 PFD equipment items | Concept stage of issue #121 |
| 2026-10-27 | lca/ | Preliminary gate-to-gate LCI per kg contained Cl2, co-products unallocated, every background declared missing; inventory, dataset, gaps, coverage written | Scope item 4 of the run (D-013) |
| 2026-10-27 | process/*.yaml, BFD, PFD, scripts/balance.py | Balanced flowsheet (7 blocks, 22 steps, 61 streams), materials, reactions, cells.yaml checked by cheme process cell | Scope item 2 (D-004..D-010) |
| 2026-10-27 | (all) | Scaffold from cheme init and the process.yaml template | Start of case chlor-alkali-1 |
