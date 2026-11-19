# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | process/, lca/, DESIGN.md, README.md, process.yaml, equipment/, tests, benchmarks, REFERENCE.md, docs/coverage.md | review of PR #500: the rates of SRC-1's appendix operating-cost sheet used (8959 kg/h of pure ethanol, FERM 0.9416; 27 681 kg/h of 150 psig steam, the feed now MPS; natural gas 35.13 MMBtu/h as HHV, 667.75 kg/h; cooling-tower water as Q11, CW 13 981 kW), SRC-1's caustic, enzymes, acid, lime, urea and yeast as LCI consumables, the scrubber water linked as deionised water (proxy) and the stated gaps matched to the strict build, S34's duplicate state merged (core now calculates the burner duty; L-5 withdrawn), Q8 with its sensible heat, the vent saturated at 305 K, the evaporator to 55 wt%, SRC-3 with the package methods and works, boiling points sourced, locators and the DDGS shortfall on one basis | confirmed review findings on PR #500 |
| 2026-11-19 | lca/, process.yaml, README.md, DESIGN.md, tests | preliminary gate-to-gate LCI (natural gas, steam as heat and power linked; corn and scrubber water gaps; biogenic and fossil CO2 apart; mass allocation by the WBCSD rule on SRC-1's prices), the Atlas manifest, the public README, D-001 to D-012 with the core features used and limits L-1 to L-5, the folder's tests | concept deliverables (#468) |
| 2026-11-19 | process/, equipment/equipment-list.yaml, design-basis.yaml | lumped corn components, the hydrolysis, fermentation and burner reactions, the dry-grind flowsheet of SRC-1 (5 blocks, 21 steps), four recycles converged at tears, the beer and backset design specifications, the dryer model, utilities from SRC-1; the equipment list and the design basis | the dry-grind route of NREL/TP-580-28893 (D-001 to D-010) |
| 2026-11-19 | all | scaffold from cheme init (core 1.12.0) | start of the case (#468) |
