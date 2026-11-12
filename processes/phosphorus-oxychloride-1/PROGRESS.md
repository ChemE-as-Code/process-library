# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-12 | process/materials.yaml, process/flowsheet.yaml, scripts/balance.py, DESIGN.md D-005/D-012/D-016, process.yaml, equipment list, BFD/PFD, lca/ | Liquid heat capacities of PCl3 (123.6, ASSUMED 0.9 kJ/(kg K)) and POCl3 (138.8, CRC via chemicals 1.5.2); Q3 written by core's conversion-step model: 1912.3 -> 1932.94 kW (+20.6 kW: +36.6 kW loop pump work, -15.95 kW feed warming); cooling water 1.2029 -> 1.2081 kWh/kg | #396: the typed duty was the reaction heat alone; the model warmed the liquids at their ideal-gas heat capacity (cheme.process-duty) |
| 2026-10-28 | branch | Response 2026-10-28-pfd-lci-review#5(b): left open. Merging or rebasing origin/main is a branch operation for the maintainer (this session may not push or change files outside the folder); the PR diff against the merge base already holds only this folder | review #5(b) |
| 2026-10-28 | checks/checks.yaml | Response 2026-10-28-pfd-lci-review#5(a): template comment no longer cites D-023 (commit 7a52242) | review #5(a) |
| 2026-10-28 | lca/lca.yaml, lca/ outputs | Response 2026-10-28-pfd-lci-review#4: functional unit purity 99.998 wt% as D-002; phosphorus-mud exclusion restates SRC-3's 0.2-0.5 wt%, wash water named once (commit 7a52242) | review #4 |
| 2026-10-28 | lca/lca.yaml, lca/ outputs | Response 2026-10-28-pfd-lci-review#3: feed:NAOH says the amount is kg of 50 wt% solution (1.93 g NaOH as 100 % per kg) (commit 7a52242) | review #3 |
| 2026-10-28 | scripts/balance.py, flowsheet Q1, DESIGN.md D-004, equipment list, LCI | Response 2026-10-28-pfd-lci-review#2: R-101 heat counts the PCl3 oxidised in R-101 per mol PCl3; Q1 2388.7 -> 2443.2 kW, product:CW 1.17 -> 1.20 kWh/kg (commit 14f3375) | review #2 |
| 2026-10-28 | scripts/balance.py, flowsheet Q4-Q8, DESIGN.md D-008, equipment list, process.yaml, BFD/PFD, LCI | Response 2026-10-28-pfd-lci-review#1: POCl3 heat of vaporisation from the Clausius-Clapeyron slope of thermo's vapour pressure (34.6 kJ/mol at 378.9 K, was 27.5); Q7/Q8 298.4 -> 376.4 kW, feed:LPS 0.0907 -> 0.1105 kWh/kg; check recorded in D-008 (commit 14f3375) | review #1 |
| 2026-10-28 | lca/mappings.yaml | CI fix: feed:LPS (kWh) mapped to the shared steam-heat entry; the default `steam` entry counts kg and failed the library build (tests test_jsonld_identifiers, test_the_library_builds_strict_with_the_utilities) (commit 0f7c79e) | PR #230 CI |
| 2026-10-28 | lca/ | Preliminary gate-to-gate LCI per kg POCl3 (inventory, gaps, coverage: partial, 11 gaps), lca/mappings.yaml empty on purpose | case scope step 4 (D-012) |
| 2026-10-28 | process.yaml, process/design-basis.yaml, equipment/equipment-list.yaml, DESIGN.md | Route/boundary memo, source register, decisions D-001..D-013, design basis, Atlas manifest (internal), equipment list as far as the PFD requires | case scope steps 1, 3, 5 |
| 2026-10-28 | process/flowsheet.yaml, materials.yaml, reactions.yaml, BFD, PFD, scripts/balance.py | Concept BFD/PFD: P4 chlorination, PCl3 oxidation with recycle, two columns, caustic scrubber; mass balance closed, reactors by cheme propagate | case scope step 2 (D-001..D-010) |
| 2026-10-28 | scaffold | cheme init and the process.yaml template committed | start of issue #135 |
