# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | process/, scripts/, lca/, process.yaml, DESIGN.md, benchmarks | argon as the library's component AR (its LCI pass-through), the burnt-out hydrocarbons as elementary zeros (not free, as ethylene-1), a shorter Atlas title (120 characters), the benchmark in kg of gas per kWh with its explanation in D-001 | build_lci --strict and build_catalog errors |
| 2026-11-19 | lca/, process.yaml, README.md, DESIGN.md, tests | preliminary gate-to-gate LCI per kWh (fossil CO2 from the balance, NETL's stack rates for NOx, CO, SO2 and particulates, AP-42 CH4 and N2O, the SCR's ammonia linked to ammonia-1), the Atlas manifest without an inventory_key on the electricity, the public README, D-001 to D-013 with the core features used and limits L-1 to L-4, the folder's tests | concept deliverables (#469) |
| 2026-11-19 | process/, scripts/ngcc_balance.py, equipment/ | materials with ideal-gas data, the combustion reactions and the flowsheet of NETL Case B31A: the gas turbines as one conversion step (exhaust and power by cheme process propagate), the HRSGs, the steam turbine, the condenser, the cooling tower and the electrical bus on NETL's stream table, water balance and auxiliary loads; equipment list from NETL's major equipment | the route of D-001 on an open, complete design point |
| 2026-11-19 | all | scaffold from cheme init (core 1.12.0, 0e85885) | start of the case |
