# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | flowsheet, BFD/PFD, lca/, process.yaml, DESIGN.md D-005 D-010 and source register, scripts/formox_balance.py, PROGRESS.md | Audit fixes: steam terminal STEAM renamed MPS (product:MPS) and the `steam-heat` override and `inventory_key` dropped, so the Atlas build reports the export as a gap; source register header and package row (chemicals 1.5.2, thermo 0.6.1, methods, works not read) per ADR 0037; D-005 air CO2 about 2 % of stack CO2, vent 2414 Nm3/t just above the BREF range; flowsheet header no longer calls R101's derived selectivities sourced; balance script prints and comments use the flowsheet's stream ids; this table's step count | the override booked the exported steam as 2.02 MJ steam heat bought in per kg formalin; wording defects; review 2026-10-28-pfd-lci-review #4 and #5 |
| 2026-10-28 | DESIGN.md D-006 | Note on the heat of solution of formaldehyde (commit b0faf4c; line added 2026-11-19) | the largest term of the absorber cooling duty, ASSUMED |
| 2026-10-28 | lca/, DESIGN.md D-010 | Preliminary gate-to-gate LCI per kg formalin 50 wt%: inventory, gaps, dataset, steam override in lca/mappings.yaml (dropped 2026-11-19) | step 4 of #169; backgrounds left as gaps (ADR 0022) |
| 2026-10-28 | process/, BFD, PFD, lists, DESIGN.md, process.yaml | Design basis, Formox flowsheet (4 blocks, 9 steps, 20 streams), conversion reactor with selectivities derived from sourced plant targets (assumed), ECS, balance script, BFD/PFD built, equipment and line lists | concept stage of #169: balanced PFD (D-001 to D-011) |
| 2026-10-28 | all | Scaffold from `cheme init` and the process.yaml template | start of formaldehyde-1 (#169) |
