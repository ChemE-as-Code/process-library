# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | coverage (library coverage.yaml, docs/coverage.md), REFERENCE.md, chemicals registry | coverage item `direct-air-capture` at provisional rank 135 (the dac variant of carbon-capture), the REFERENCE row, the registry grade carbon-dioxide/dense-151bara-97 | shared-file rows of a new entry (#518) |
| 2026-11-19 | lca/, process.yaml, README.md, DESIGN.md, tests | preliminary gate-to-gate LCI per kg of CO2 product (the air's CO2 a resource, the product 77.6 % air carbon; oxygen to asu-1, gas, KOH, limestone and landfill to shared entries; water and condensate gaps), the Atlas manifest, the public README, D-001 to D-012 with the core limits L-1 to L-6, the folder's tests | concept deliverables (#518) |
| 2026-11-19 | equipment/equipment-list.yaml, process/design-basis.yaml, checks/checks.yaml | equipment with first counts and sizes from Keith et al. 2018 and NETL 2022 (D-010); the design basis; the assumptions gate with grep (no `python` on the gate's path) | concept lists |
| 2026-11-19 | process/, scripts/dac_balance.py | materials (KOH-K2CO3 liquor as an inventory, calcium solids, methane), reactions (ABS, CAUST, SLAKE, CALC, COMB with Keith et al.'s enthalpies), the flowsheet: contactors, pellet reactors, lime mix tank, steam slaker, oxy-fired calciner, CO2 compression; every material stream from the closed-form balance script (ADR 0027); power from Keith et al.'s Table 1; hand estimates for the CO2 train's cooling and the calciner's heat beyond the calcination; BFD and PFD built | the route of Keith et al. 2018, scenario C (D-001 to D-009) |
| 2026-11-19 | all | scaffold from cheme init (core 1.13.0, pin b97a833) | start of the case (#518) |
