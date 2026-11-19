# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | DESIGN.md D-003 to D-011, README, flowsheet Q2/Q7/Q8, scripts/utilities.py, lca/, equipment list, benchmarks, test | Review fixes on PR #494: LP steam less SRC-2's fired feed preheat (50.3 -> 33.3 MW); chiller sized on S20 (0.88 -> 2.73 MW electric) and its condenser in the cooling water; reaction heat compared on SRC-2's feed basis; exported steam renamed product:HPS and left unmapped (it was booked as steam bought in); emission exclusions with the methods that cover their sources; vaporiser and quench heats sized; HCN stabilisation named; source locators and attributions corrected; test parses the stated numbers | review of #494 |
| 2026-11-19 | lca/, benchmarks, DESIGN.md D-011 | Preliminary gate-to-gate LCI per kg acrylonitrile, mass allocation between the three nitriles, propylene, ammonia and acid linked to library producers; two KPIs against IPCC 2006 | step 4 of #460 |
| 2026-11-19 | equipment/equipment-list.yaml, DESIGN.md D-010 | Concept equipment list, one tag per PFD step | step 3 of #460 |
| 2026-11-19 | process/, BFD, PFD, scripts/utilities.py, DESIGN.md D-001 to D-009 | Design basis, materials, reactions, flowsheet (7 blocks, 17 steps) with three design specs, a lean-water tear, component separators and a sourced reactor slate; balance closed, sheets built | concept stage of #460 |
| 2026-11-19 | all | Scaffold from `cheme init` (core 1.12.0) and the process.yaml template | start of acrylonitrile-1 (#460) |
