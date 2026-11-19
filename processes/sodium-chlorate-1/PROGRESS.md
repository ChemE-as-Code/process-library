# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | process/flowsheet.yaml, DESIGN.md, lca/, equipment-list, tests | the returned liquor's reheat booked: Q7 (1802.18 kW, S5 321.18 K to 343.15 K at M201), Q4 9368.13 kW, cooling water 2.42 kWh/kg; P3's dissipation and the plant balance stated; liquid-ring vacuum pumps, steam 58 kg/t explained; the cell gas's water vapour, the bleed's chloride, the hypochlorite at the crystallizer against the BREF's H2O2 and the unwashed cake's dichromate sized; SRC-5 per ADR 0037; D-012 and the condensate citation to what the sources say; electricity gap only in cheme assess lca, the H2 warning recorded; stale numbers in cells, reactions and design basis; benchmark note on the auxiliaries; tests read the extents from the streams; rank 116 | review of PR #542 |
| 2026-11-19 | lca/, process.yaml, README.md, DESIGN.md, tests | preliminary gate-to-gate LCI (the BREF's auxiliaries as consumables per year, mass allocation to the hydrogen used, salt, water, steam and consumables linked to library producers, electricity and dichromate gaps), the Atlas manifest, the public README, the source register SRC-1 to SRC-5, D-001 to D-012, core limits L-1 to L-6, the folder's tests | concept deliverables (#512) |
| 2026-11-19 | equipment/equipment-list.yaml, process/design-basis.yaml | ten items with the sizes the models and hand balances give; the design basis with every assumption marked | concept lists |
| 2026-11-19 | process/ | materials, reactions, cells and the flowsheet: salt dissolver, cells (HYPO) and reaction tanks (CHEM, OXY) whose extents equal the cell model's, gas separator, liquor coolers with heat recovery, vacuum crystallizer with centrifuge, bleed, fluidised-bed dryer, hydrogen split; loop torn at S6 with the specifications rate and liquor; energy streams from cheme process cell and core's crystallizer and dryer; BFD and PFD built (D-004 to D-009) | the route of the BREF LVIC-S 2007 section 7.13 and US 5 419 818 A |
| 2026-11-19 | all | scaffold from cheme init (core 1.12.0, pin 0e85885) | start of the case |
