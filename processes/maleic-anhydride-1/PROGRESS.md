# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | coverage (library coverage.yaml, docs/coverage.md) | coverage rank 116 -> 117 | vinyl-acetate-1 (#504) merged first and took 116; ranks stay contiguous (merge of main into #523) |
| 2026-11-19 | process/flowsheet.yaml, scripts/balance.py, equipment/, lca/, DESIGN.md, process.yaml, README.md, tests, benchmarks, coverage | review of PR #523: the absorber's 2476 kW to pump-around coolers E-306 (Q10, cooling water 1.190 to 1.983 kWh/kg); F-501 a recuperative oxidiser (the off-gas burns only to about 743 K as it comes); the draught fan its own step K502 after the boiler (Q9 8363 to 8117 kW, steam 8.46 to 8.38 kWh/kg); the stripper's and column's heat balances closed (Q4 2027 to 1859 kW); n-butane 58.124 g/mol and Tb 272.65 K (CRC), CO2's Tb source; SRC-6 with methods and works not read; the benchmark's reason restated after US 5 688 970 A's line-30 figure; rank 116; the LCI regenerated | the review's findings 1 to 12 |
| 2026-11-19 | lca/, process.yaml, README.md, DESIGN.md, tests | preliminary gate-to-gate LCI (steam drawn linked as heat, the exported steam at share 0), the Atlas manifest, the public README, D-001 to D-012 with the core features used and limits L-1 to L-5, the folder's tests | concept deliverables (#478) |
| 2026-11-19 | process/, scripts/balance.py, equipment/ | materials, reactions and the flowsheet: R201 and the oxidiser R501 as conversion steps with their duties, A301, T302 and C401 as component separators, the specifications `rate` (25 000 t/a) and `solvent` (4.8 kg/kg), the solvent loop torn at S17; the balance script's compressor, heats and temperatures; the equipment list (D-001 to D-010) | the routes of US 7 589 217 B2 and US 4 118 403 A |
| 2026-11-19 | all | scaffold from cheme init (core 1.12.0) | start of the case |
