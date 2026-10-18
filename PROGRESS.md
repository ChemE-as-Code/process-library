# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-18 | pid/P-02.xml, DESIGN.md | P-02 drawn (scripts/draft_P-02.py): V-2101A/B, E-2101, F-2101, S-2101, 8 switching valves, AIR-1004/AIR-2001/AIR-2002/RG-2001..2003, 7 instruments; D-022 | stage S2, ahead of plan |
| 2026-10-18 | pid/P-01.xml, lists, DESIGN.md | S2: P-01 drawn (scripts/draft_P-01.py): F-1101, K-1101 with E-1101/E-1102/E-1103, blow-off UV-1102 + S-1101, check valve, PSV-1109, DCAC C-1101, evaporative cooler C-1102, P-1101A/B, P-1102A/B, 14 lines, 10 instrument loops with signal lines to TV/LV/FV/UV; silencers and PSVs moved from equipment/instrument lists to D-020 (DEXPI piping components) | stage S2 |
| 2026-10-18 | DESIGN.md, lists, checks | S1 review fixes: VNT-4001 split into VNT-4001/4002/4003 with S-4101/S-4102, GOX suction vent PV-4101B (split range PIC-4101), PSV-3114/3116/1109, compander seal gas PDSLL-3115 and oil mist (D-012), expander -118 C / 215 kW / 940 kg/h liquid, refill-time decision D-017, recovery sensitivity D-018, relief case list, ESD XV-4116..4120, AIA-4121, AIR-3005, WN-3002/3003, UN-3001, WN-1001 DN700, LICA-3102 in D-010; checks: exact tag greps, relief-case-list gate | independent review of stage concept |
| 2026-10-18 | pid/P-01..P-04.xml | title block: ASU-1, ASSUMED coastal site, section per sheet, rev A for review, approval fields empty (scripts/fix_titleblock.py) | template data from pyDEXPI was on the frames |
| 2026-10-18 | checks/checks.yaml | ASU gates: O2-safety philosophy, hydrocarbon protection, relief philosophy (concept); O2 safety review, analyzer/purge and relief devices on P&IDs (basic) | ASU-specific stage gates |
| 2026-10-18 | equipment, line, instrument lists | 41 equipment items, 37 main lines with concept DN, 46 key instrument functions for P-01..P-04 | stage concept; not-on-pid warnings expected until sheets are drafted (D-015) |
| 2026-10-18 | plant.yaml, process/design-basis.yaml, DESIGN.md, pid/P-01..P-04.xml | S1 concept: design basis, process description, block flow, main-stream balance, decisions D-001..D-016; sheets declared, empty frames | stage concept |
