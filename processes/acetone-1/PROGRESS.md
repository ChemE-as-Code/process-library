# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-12 | DESIGN.md | source register S4 no longer calls the package values open data: it names chemicals 1.5.2 and, per component, the method `cheme chemistry thermo` used (the packaged CRC table `heat_capacity.CRC_standard_data` for cumene, CHP and phenol; ATcT 1.112 for acetone, CO2 and water; the NIST WebBook data for alpha-methylstyrene), the CRC Handbook as the underlying work (not read) | issue #426: ADR 0037 sweep of the older source registers; text only, no number changes |
| 2026-11-11 | lca/dataset.yaml, lca/manifest.json (regenerated) | rewritten by `cheme assess lca --write` (core v1.11.0) after the process.yaml edit below: the process.yaml input hash only, results unchanged | `cheme assess lca --check` reported the dataset stale (cumene-1 PR #325 brought up to date with main) |
| 2026-11-03 | process.yaml chemistry, lca/mappings.yaml | feed:CUM gets its registry slug (`inventory_key: feed:CUM`, chemical cumene) and is pinned to cumene-1's product:CUMENE (dataset link); the Atlas build no longer reports it as a gap. lca/lca.yaml's `missing:` is left for core's own study (no background there) | cumene-1 became a plant with a flowsheet-derived dataset (process-library#313, cumene-1 D-013) |
| 2026-10-28 | lca/dataset.yaml, lca/manifest.json (regenerated) | CI fix (PR #210, `tests/test_utilities.py` strict library build): `allocation.method` left unset in lca/lca.yaml (mass is the default), so build_lci no longer warns "study allocation 'mass' differs from the dataset's default None"; commit 022313c | CI failure; library-side fix still due (I-10) |
| 2026-10-28 | DESIGN.md D-016, I-11; lca/lca.yaml product:WW | Response to 2026-10-28-pfd-lci-review#1: effluent stated as a lower bound against S1 8.3.5, missing streams named, no unsourced allowance added; commit bed39df | review |
| 2026-10-28 | process/flowsheet.yaml Q10, process/reactions.yaml, DESIGN.md D-011, BFD, PFD, lca/ | Response to 2026-10-28-pfd-lci-review#3: Q10 re-estimated 330 -> 1 260 kW; gas-basis bias and omitted side-reaction heats stated; heats marked CALCULATED in `source` (schema allows given/assumed only); "independent closure" now a consistency check; commit bed39df | review |
| 2026-10-28 | DESIGN.md D-009 | Response to 2026-10-28-pfd-lci-review#4: acetone 0.627 t/t pure, above stoichiometric 0.617, stated with the unmodelled losses and the 1-2 % effect; the loss itself waits for I-05; commit bed39df | review |
| 2026-10-28 | DESIGN.md D-007 | Response to 2026-10-28-pfd-lci-review#5: acid loading marked ASSUMED, S3 abstract range only a pointer; Ullmann's entries already labelled; commit bed39df | review |
| 2026-10-28 | - | Response to 2026-10-28-pfd-lci-review#2 (open): the feed flows are derived from the capacity (assumed), so `cheme maturity` stays at none even with given compositions; idealised compositions (pure cumene, dry air) are not specifications, so they stay assumed and the process.yaml note stands | review |
| 2026-10-28 | - | Response to 2026-10-28-pfd-lci-review#6 (open): `emission_exclusions` take no amount in the lca schema, free flows (N2, O2) take no compartment, and no verified CPC code is to hand; left for the LCA practitioner | review |
| 2026-10-28 | process/flowsheet.yaml, DESIGN.md | oxidation selectivity sourced to US 8,975,444 (92-94 %); build_lci finding I-10 | evidence for D-004 |
| 2026-10-28 | lca/, process.yaml, DESIGN.md | preliminary LCI per kg acetone (mass allocation), every background a gap; manifest internal, concept | issue #132 scope step 4 |
| 2026-10-28 | equipment/equipment-list.yaml | one tag per PFD step | resolve the flowsheet links |
| 2026-10-28 | process/*.yaml, BFD, PFD | design basis, materials, reactions, 5-block / 15-step flowsheet, balances closed | issue #132 scope steps 1-3 |
| 2026-10-28 | all | scaffold from cheme init and the process template | start of the case |
