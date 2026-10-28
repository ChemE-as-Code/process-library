# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | process.yaml, DESIGN.md D-016/D-018 | Response 2026-10-28-pfd-lci-review#1 (high): CO2 relabelled 0.472 kg/kg unallocated, 0.433 kg/kg mass-allocated (91.6 %); D-016 says inventory.csv is allocated per FU and dataset.yaml unallocated. Commit 63fe760 | headline figure was mislabelled |
| 2026-10-28 | DESIGN.md D-014/D-018, flowsheet.yaml Q402/Q501/Q503, lca.yaml feed:POWER | Response #2 (medium): "heat-integrated" reboilers corrected to "not modelled, not credited"; refrigeration power and pure-component condenser duties stated as conservative upper estimates (crediting waits for core #315). Commit 63fe760 | reboiler heat appeared from nowhere |
| 2026-10-28 | process.yaml, lca.yaml allocation, DESIGN.md D-015 | Response #3 (medium): disclosed that the CO2 and power per kg are gross because the SHP export carries no burden; the netting/substitution scenario is recorded as open in D-015, not built. Commit 63fe760 | burden of the steam export |
| 2026-10-28 | process.yaml validation.notes | Response #4 (medium): cheme maturity result (none) and the acknowledged maturity-claim-exceeds warning added. Commit 63fe760 | honest manifest |
| 2026-10-28 | DESIGN.md D-018 | Response #5 (low): yield 0.788 kg/kg fresh feed, 0.82 kg/kg ethane. Commit 63fe760 | ambiguous basis |
| 2026-10-28 | DESIGN.md D-018 | Response #6 (low): 8.6-9.8 GJ/t primary, at or below the BREF lower end; comparison softened. Commit 63fe760 | arithmetic |
| 2026-10-28 | lca.yaml emission:CO2 | Response #7 (low): feed CO2 leaves as carbonate in the spent caustic, not the flue. Commit 63fe760 | wrong source text |
| 2026-10-28 | DESIGN.md D-005 | Response #8 (low): uncracked fresh-feed propane in H101 and the H103 H2/C4+ slate described. Commit 63fe760 | disclosure |
| 2026-10-28 | DESIGN.md D-009, lca.yaml feed:CAUSTIC, product:SPENTCAUSTIC | Response #9 (low): 3:1 ratio and feed CO2 marked unsourced ASSUMED; both LCI exchanges flagged upper-bound. Commit 63fe760 | unsourced assumption in the LCI |
| 2026-10-28 | DESIGN.md (open inputs) | Response #10 (low): recorded that the case study is not taken to a concept sign-off (layout-plot-plan out of scope). Commit 63fe760 | gate status |
| 2026-10-28 | DESIGN.md, PROGRESS.md, process.yaml, design-basis.yaml | source register, decisions D-001 to D-018, manifest (internal, concept, unreviewed), design basis | record the route, basis and assumptions |
| 2026-10-28 | lca/lca.yaml, lca/mappings.yaml, lca/* (generated) | preliminary gate-to-gate LCI per kg ethylene, all backgrounds unmapped (gaps), combustion emission estimates from BREF/IPCC | scope item 4; ADR 0022 gaps |
| 2026-10-28 | equipment/equipment-list.yaml | 20 PFD items | resolve the flowsheet links |
| 2026-10-28 | process/flowsheet.yaml, reactions.yaml, materials.yaml, simulation.yaml, BFD/PFD | balanced BFD/PFD of the ethane cracker; propane recycle on its own coil (block CRK3) | scope items 2-3; unique reaction extents (D-005) |
| 2026-10-28 | scripts/balance.py | heat and material balance script (recycles, firebox) | source of the ASSUMED separator values (D-006) |
| 2026-10-28 | all | scaffold from cheme init and the process template | start of ethylene-1 |
