# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | lca/, process.yaml, README.md, DESIGN.md, equipment/, tests | preliminary gate-to-gate LCI (ethylene to ethylene-1, acetic acid to acetic-acid-1, oxygen to asu-1, LP steam as heat), the Atlas manifest, the public README, D-001 to D-010 with the core features used and limits L-1 to L-5, the equipment list, the folder's tests | concept deliverables (#479) |
| 2026-11-19 | process/flowsheet.yaml, scripts/balance.py | energy streams: R-101's heat raises LP steam for T-101, the CO2 regenerator, C-202 and C-201 (Q1 written by propagate through `energy_port`), the feed/effluent exchanger, the condensers, coolers and drives from the script (D-008) | the duties core does not calculate |
| 2026-11-19 | process/ | materials with ideal-gas data, the two reactions, the flowsheet: four design specifications for the product rate and the reactor feed of US 8 765 995 B2 Table 2, three tears, five component separators (D-003 to D-007) | Wacker's route and work-up (SRC-1, SRC-2) |
| 2026-11-19 | all | scaffold from cheme init (core 1.12.0) | start of the case |
