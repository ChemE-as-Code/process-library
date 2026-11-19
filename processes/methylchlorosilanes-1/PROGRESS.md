# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | coverage (library coverage.yaml, docs/coverage.md), REFERENCE.md, chemicals registry, benchmarks | provisional coverage rank 139 (wave block 127 to 139), the REFERENCE row, registry entries silicon, methyltrichlorosilane, chlorotrimethylsilane, dichloromethylsilane, two unbound benchmark KPIs with the reason no open range is bound | shared-file rows of a new entry (#522) |
| 2026-11-19 | lca/, process.yaml, README.md, DESIGN.md, tests | preliminary gate-to-gate LCI (methyl chloride linked to chloromethane-1, steam drawn as heat, mass shares of the three silane products, the exported MP steam at share 0), the Atlas manifest, the public README, D-001 to D-012 with the core features used and limits L-1 to L-6, the library test tests/test_methylchlorosilanes_1.py | concept deliverables (#522) |
| 2026-11-19 | process/, scripts/balance.py, equipment/ | materials, reactions and the flowsheet: R201 as a conversion step on the silicon, CY202 and four columns as component separators, the specifications `rate` (60 000 t/a) and `mecl` (6.9152 kg of methyl chloride per kg of silicon at the bed), the methyl chloride loop torn at S2; the balance script's reaction shares, reactor heat with the solids, duties, powers and temperatures; the equipment list (D-001 to D-010) | the routes of US 4 500 724 A, US 2 563 557 and EP 1 957 504 B1 |
| 2026-11-19 | all | scaffold from cheme init (core 1.13.0) | start of the case |
