# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | scripts/balance.py, process/, lca/, DESIGN.md, process.yaml, README.md, equipment list, design basis, tests | review of PR #526: the salting in calibrated at SRC-1 Example 1's 10 to 15 C (k -0.2182, yield 75.5 %, the feeds rescaled); M-101's heat-up and cool-down times from a jacket estimate, its metal in Q1/Q2; Q7 (R-101's metal, the crystals' redissolution) and Q8 (E-101, D-101's cool-down); the recipe's hand-off at M-101's transfer and 0.4 h for the heat of crystallisation, R-101 now the bottleneck (2602.10 kg every 10.30 h); the decolourising sulfite and hydrosulfite as consumables; the adiabatic rise 38 K and the 330 K permissive; the source register's thermo methods; the LCI's link status; the LCA outputs regenerated | review findings |
| 2026-11-19 | process.yaml, README.md, DESIGN.md, lca/, tests | the Atlas manifest, the public README, D-001 to D-013 with the sources SRC-1 to SRC-8, the core features used and limits L-1 to L-6; preliminary gate-to-gate LCI (acetic anhydride to acetic-anhydride-1, the activated carbon per batch); tests/test_paracetamol_1.py | concept deliverables (#481) |
| 2026-11-19 | process/recipe.yaml, equipment/equipment-list.yaml, process/design-basis.yaml | the batch recipe (2516.47 kg every 9.965 h, the dryer the bottleneck, R-101 25 m3 and its chilled-water jacket checked), the equipment list and the design basis (D-002, D-003, D-009) | the batch basis |
| 2026-11-19 | process/, scripts/balance.py | materials, reactions (ACET, HYD) and the flowsheet: dissolver, semi-batch R101 and digestion R102, cooling crystallisation CR101, centrifuge F101/W101/F102, dryer D101, the mother-liquor recycle at the tear S16; the acetic acid's salting in calibrated to US 3 917 695 A Example 1; the feeds scaled to 2000 t/a (D-001, D-004 to D-008) | the route of US 3 917 695 A |
| 2026-11-19 | all | scaffold from cheme init (core 1.12.0) | start of the case |
