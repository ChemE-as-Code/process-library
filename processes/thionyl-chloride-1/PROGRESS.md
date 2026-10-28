# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | lca/mappings.yaml | CI fix: `feed:LPS` (kWh) mapped to the shared `steam-heat` entry instead of the default `steam` (kg); the strict library build and `test_jsonld_identifiers` failed on the unit (41e6e8d) | PR #234 CI `library` job |
| 2026-10-28 | scripts/balance.py, process/flowsheet.yaml, equipment list, DESIGN.md D-007, BFD/PFD, lca/ | Response R-01 (medium, closed): T-201 bottoms at the Raoult bubble point of the lights-free crude at 125 kPa(a), 350.12 K (was 345 K); Q9 471.01 kW, Q13 678.05 kW; LP steam 0.4219 kWh/kg (b1877e7) | review 2026-10-28-pfd-lci-review#1 |
| 2026-10-28 | PROGRESS.md | Response R-02 (low, closed): the plant balance of run 20261028-161945-design is 3778.01 kg/h in (S1+S2+S3) against 3778.00 kg/h out (S31+S25), not the 3805.00/3804.99 kg/h of its report; the run record stays unedited (this entry) | review #2 |
| 2026-10-28 | process/reactions.yaml, process/flowsheet.yaml, DESIGN.md D-005 | Response R-03 (low, closed): R201 uses its own reaction SCL2_FORM_R201 with conversion 0.95, provenance assumed, source D-005 (the step-level override cannot carry provenance); D-005 states the effective per-pass SCl2 conversion, 67.9 % (b1877e7) | review #3 |
| 2026-10-28 | process.yaml | Response R-04 (low, closed): validation.notes name cheme.maturity-claim-exceeds and say `concept` is the schema floor (b1877e7) | review #4 |
| 2026-10-28 | DESIGN.md D-004 | Response R-05 (low, closed): dissolved-O2 simplification stated; chlorinator off-gas vent to K-201 suction or T-401 required on the P&IDs (b1877e7) | review #5 |
| 2026-10-28 | DESIGN.md D-010, Open inputs | Response R-06 (low, closed): T-201 feed/bottoms interchange, SO2 vaporiser off steam and reactor heat to LP steam listed as open heat-integration items; no LCI scenario yet (b1877e7) | review #6 |
| 2026-10-28 | process.yaml, DESIGN.md Open inputs | Response R-07 (low, partly closed): Ullmann wording aligned to "not read"; reading SRC-4/SRC-5 in full is an open input. Finer patent locators (column/example numbers) left open: the patents were not re-read in this session (b1877e7) | review #7 |
| 2026-10-28 | lca/lca.yaml | Response R-08 (low, partly closed): CPC 2.1 34231 added (third-party crosswalk, to verify against UNSD). Left open: free flows O2/H2O cannot take a compartment (schema refuses `elementary` on `free`); flow identities for Cl2 and the sulfur chlorides wait for the shared-files PR (D-013) (b1877e7) | review #8 |
| 2026-10-28 | DESIGN.md, PROGRESS.md | source register, decisions D-001..D-013, method/dependency table, open inputs | record the route, assumptions and gated steps of the concept stage |
| 2026-10-28 | process.yaml, lca/ | Atlas manifest (internal, concept, unreviewed); preliminary gate-to-gate LCI per kg SOCl2 with every background unmapped (inventory.csv, gaps.csv, dataset.yaml written by cheme) | issue #138 scope step 4 |
| 2026-10-28 | process/, scripts/balance.py, equipment/ | design basis, materials, reactions, flowsheet with 5 blocks, 20 steps, 50 streams; BFD/PFD built; equipment list as far as the PFD | balanced concept PFD (mass, component, element balances closed in cheme) |
| 2026-10-28 | all | scaffold from cheme init and the process template | start of the case |
