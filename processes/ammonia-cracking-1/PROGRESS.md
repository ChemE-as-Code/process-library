# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | lca/, process.yaml, README.md, DESIGN.md, equipment/, tests | preliminary gate-to-gate LCI (ammonia to ammonia-1, electricity and cooling water through the shared proxies, burner NOx an open exclusion), the Atlas manifest, the public README, D-001 to D-010 with the core features used and limits L-1 to L-5, the equipment list, the folder's test | concept deliverables (#519) |
| 2026-11-19 | process/flowsheet.yaml, scripts/balance.py | energy streams: R-101's duty Q1, the vaporiser Q4, the trim cooler Q3 and the fan W1 from the script, the convection duty Q2 written by propagate through H101's `energy_port`, the stack temperature that closes the furnace (D-008) | the duties core does not calculate |
| 2026-11-19 | process/ | materials with ideal-gas data to 1500 K, the cracking equilibrium and the two combustion reactions, the flowsheet: two design specifications (200 t/d hydrogen, 2 mol% O2 in the flue gas), R101 at equilibrium at 773.15 K and 1100 kPa(a), the PSA as a component separator (79.4 % hydrogen recovery) (D-003 to D-006) | EP 4 337 600 A1 reference example 2 (SRC-1) |
| 2026-11-19 | all | scaffold from cheme init (core 1.13.0) | start of the case |
