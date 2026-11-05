# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-05 | pid/P-01 to P-08, scripts/draft_*.py, lists, control/cause-effect.yaml, control/sequences.yaml, control/loops.yaml, equipment list and datasheets D-7101, D-8101, P-8101A/B, checks/checks.yaml, DESIGN.md D-026 | response to review 2026-11-05-basic-design-2 and the disputed closures: ESD-2 trips ESD-1, ERS by I-507/I-607; make-before-break vapour return switch with ZSO-4131/4132/4135/4136 (I-511..513, I-611..613), relief outlets on the tank side; hybrid-arm permissives; PZT-1105 in I-102; ZSC-1102/1103 tied to their valves; tank relief inlet isolations HV-n134/n135A-C; ZSO-7121A-C and PZT-7113 (I-705A-C), vendor trips in I-702; PSV-7105 and FL-7001 removed; HV-8108A/B, LIC-8101 start/stop by signal, I-803; arm line-ups and O2 limit (D-026); sequences corrected | review 2026-11-05-basic-design-2 |
| 2026-11-05 | layout/, piping/routing.yaml, electrical/, estimate/ | 3D layout pass: routes pinned to a lane plan, no clashes; buildings B-SUB, B-PLAT, HVAC; electrical list and cable schedule; lifting study; MTO and estimate (example rates) | detail-stage layout gates |
| 2026-11-05 | safety/hazop/H-01..H-05 | HAZOP revised to 589c9ca7 (all entries proposed) | HAZOP follow-up |
| 2026-11-05 | pid/, lists, control/, DESIGN.md D-025 | response to review 2026-11-05-basic-design (28 findings) and the HAZOP actions | review 2026-11-05-basic-design |
| 2026-11-05 | safety/hazop/H-01..H-05 | HAZOP studies drafted, five nodes groups, 74 actions proposed | detail stage |
| 2026-11-05 | lca/ | LCA per tonne of LNG loaded, average case, energy allocation of the returned BOG (D-024) | detail stage |
| 2026-11-05 | equipment/datasheets/ | datasheets for 35 items, sizes from scripts/terminal_sizing.py (D-022) | detail stage |
| 2026-11-05 | control/loops.yaml, sequences.yaml, philosophy.md, cause-effect.yaml | control: 20 loops, 4 sequences, philosophy, C&E | basic stage S4 |
| 2026-11-05 | pid/P-01 to P-08, scripts/draft_*.py, scripts/lng_pid.py, scripts/build_lists.py, piping/line-list.yaml, control/instrument-list.yaml, piping/special-items.yaml, control/cause-effect.yaml, checks/checks.yaml, DESIGN.md D-021 | basic stage P&IDs: rundown and fill, two tanks with in-tank pumps, trestle lines, two berths with 4 arms and ERS each, BOG compressors, flare and utilities; 126 lines, 140 instruments, 15 relief devices, 18 interlocks; plant-specific on-sheet gates; line numbers kept across sheets | issue #362 basic stage S2-S3 |
| 2026-11-05 | process/*.yaml, BFD, PFD, scripts/terminal_sizing.py, scripts/site_frame.py, equipment, line and instrument lists, cause-effect, layout/site-plan.yaml, layout/equipment-placement.yaml, DESIGN.md D-001 to D-020, process.yaml | concept stage: design basis from LNG Canada public facts (source register S-01 to S-13), sizing on GERG-2008 (CoolProp), balanced flowsheet in three cases (average, loading, holding), 37 equipment items, plot plan on the measured site geometry | issue #362 concept stage |
