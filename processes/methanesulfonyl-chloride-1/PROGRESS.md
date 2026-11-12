# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-13 | process/, scripts/balance.py, equipment/, lca/, DESIGN.md, README.md, process.yaml, plant.yaml, shared files, tests | New Tier 2 concept entry (issue #159) on core v1.11.0: thionyl chloride dosed into methanesulfonic acid at 368 K (semi-batch with an SO2/HCl vent, its vapour and the brine vent condenser E-102), caustic scrubber, batch vacuum still with an 8-stage column (forerun recycled at the tear S3, product), recipe 1203.4 kg every 9.531 h (831 batches/a, 1000 t/a); rate law ASSUMED and sized to the source's 3.5 h hold (k 7.5e-5 m3/(kmol s) at 368 K), heat +65 kJ/mol ASSUMED by analogy; screening with hazard.mtt 388.15 K (the source's 115 C wall limit) and vent capacity 400 m3/h, k/10 and k/100 on scratch copies; design findings: an accumulated dose (1280 m3/h), water ingress beyond 15 kg/h, R-101's jacket against the endothermic dosing (heating loop E-105); preliminary LCI with thionyl chloride, caustic and nitrogen linked to thionyl-chloride-1, chlor-alkali-1 and asu-1, methanesulfonic acid a gap with a proxy; registry entries methanesulfonyl-chloride and methanesulfonic-acid, coverage rank 113 (provisional), REFERENCE.md and docs/coverage.md rows; tests/test_methanesulfonyl_chloride_1.py | issue #159 scope |
