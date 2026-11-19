# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | lca/, process.yaml, README.md, DESIGN.md, equipment/, design basis, tests | preliminary gate-to-gate LCI (propylene to propylene-pdh-1, hydrogen to hydrogen-1, caustic soda to chlor-alkali-1, MP steam as heat; mass allocation with the isobutanal, the exported LP steam without burden; the synthesis gas a gap), the Atlas manifest, the public README, D-001 to D-010 with the core features used and limits L-1 to L-5, the equipment list, the folder's tests | concept deliverables (#511) |
| 2026-11-19 | process/flowsheet.yaml, scripts/balance.py | energy streams: R-101's heat to C-102's reboiler (Q1, Q17), R-301's LP steam to the rest of it, R-302's feed heater and export, MP steam to E-301 and the three columns, condensers and coolers to cooling water, compressors and pumps; the mixers' and compressors' outlet temperatures (D-009) | the duties core does not calculate (L-2) |
| 2026-11-19 | process/ | materials, the nine reactions, the flowsheet: five design specifications (product rate, CO/propylene ratio, crude water, caustic strength, hydrogen in the vapour feed), six tears, eleven component separators (D-003 to D-007); BFD and PFD built | Ruhrchemie's route of US 4 684 750 A and US 4 523 036 A (SRC-1, SRC-2) |
| 2026-11-19 | all | scaffold from cheme init (core 1.13.0) | start of the case (#511) |
