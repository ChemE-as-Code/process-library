# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | coverage (library coverage.yaml, docs/coverage.md), chemicals registry, benchmarks, REFERENCE.md | coverage item lactic-acid at provisional rank 134 (ranks 127 to 139 reserved for this wave), registry entries lactic-acid, glucose, gypsum, corn-steep-liquor and cell-mass, two benchmark KPIs from the BioSTEAM model, the REFERENCE.md row | shared-file rows of a new entry (#517) |
| 2026-11-19 | lca/, process.yaml, README.md, DESIGN.md, tests | preliminary gate-to-gate LCI (quicklime to lime-1, sulfuric acid to sulfuric-acid-1, ethanol to bioethanol-1, steam as heat; glucose syrup and corn steep liquor gaps; the fermenters' cleaning per batch), the Atlas manifest, the public README, D-001 to D-012 with the core features used and limits L-1 to L-8, the folder's tests | concept deliverables (#517) |
| 2026-11-19 | equipment/equipment-list.yaml, process/design-basis.yaml | equipment with first sizes from the flows and the recipe (D-010); the design basis | concept lists |
| 2026-11-19 | process/flowsheet.yaml, process/recipe.yaml | the separations' hand duties (D-009); the cakes' liquid shares set to SRC-1's moistures; the concentrator's water split for 88 wt%; the stripper's overhead kept near 92 wt% ethanol; the purification's power booked on the feed mixer so that no conversion duty carries it; the batch recipe of 16 fermenters (D-003) | first propagate |
| 2026-11-19 | process/ | materials (cell mass and CSL lumps, heat capacities), reactions (SLK, FLA, FAA, FBIO, NEU, ACL, ACA, ACH, EST, HYD), the flowsheet: medium and lime, batch fermenters, centrifuge, acidulation and gypsum filter, four-effect evaporator, esterification, ester column, ethanol column, hydrolysis, stripper, concentrator; four specs and three tears (D-001 to D-008) | the route of the BioSTEAM lactic model and Garrido et al. 2023 |
| 2026-11-19 | all | scaffold from cheme init (core 1.13.0, b97a833) | start of the case |
