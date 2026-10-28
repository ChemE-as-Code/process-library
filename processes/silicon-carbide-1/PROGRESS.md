# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | lca/lca.yaml, lca/dataset.yaml | CI fix (PR 225, tests/test_utilities.py strict build): allocation written as mass shares SIC 0.80 / MET 0.20 with `allocation.deviation` (no sourced prices); the dataset now carries its method; same results (a468f4d) | core omits `method: mass` from the dataset, so the Atlas build warned twice |
| 2026-10-28 | lca/lca.yaml, process.yaml, DESIGN.md D-010 | Response 2026-10-28-pfd-lci-review#1: the goal and validation.notes say the 2.03 kg CO2-eq/kg and its interval are the direct furnace CO2/CH4 only, not a carbon footprint; electricity, coke, sand, landfill are gaps (a468f4d) | review R-01 |
| 2026-10-28 | lca/lca.yaml, process.yaml, DESIGN.md D-010 | Response #2: CO left a gap of the IPCC method (no project factor invented); its CO2 equivalent by oxidation (44/28, +0.64 kg CO2-eq/kg, 2.67 direct) stated beside the headline (a468f4d) | review R-02 |
| 2026-10-28 | scripts/sic_balance.py, process/flowsheet.yaml, process/simulation.yaml, piping/line-list.yaml, lca/lca.yaml, DESIGN.md D-008 | Response #3: B101 not adiabatic; burn-off energy closed by Q6 21.0 MW to ambient (AMB); FG-101 note: S7 is not a stack sizing basis, dilution air is an open input (a468f4d) | review R-03 |
| 2026-10-28 | DESIGN.md D-006 and source register, process/reactions.yaml | Response #4: the unlocated IPCC 1996 CO factor and the unnamed hot-model conversion removed (a468f4d) | review R-04 |
| 2026-10-28 | process.yaml | Response #5: validation.notes say cheme maturity supports no level yet (a468f4d) | review R-05 |
| 2026-10-28 | process/flowsheet.yaml, DESIGN.md D-008 | Response #6: S9, S10, S10B, S11, S12, S13 at 323.15 K, as broken (a468f4d) | review R-06 |
| 2026-10-28 | (none) | Response #7: left open: the stray `../sc-schema.json` lies outside the repository and this folder, which this run may not touch; delete by hand | review R-07 |
| 2026-10-28 | DESIGN.md, PROGRESS.md, process.yaml | route/boundary memo, decisions D-001..D-010, source register, missing registry entries, open inputs and gated steps; Atlas manifest (internal, concept, unreviewed) | concept record (#179) |
| 2026-10-28 | lca/ | preliminary gate-to-gate LCI per kg crude SiC, mass allocation with metallurgical SiC, every background `missing:`; inventory, gaps, dataset written; mass, element and carbon balance closed; process overrides in lca/mappings.yaml | LCI scope of #179 |
| 2026-10-28 | process/flowsheet.yaml, process/simulation.yaml, scripts/sic_balance.py | ingot cooling heat to ambient (Q5, terminal AMB), burn-off declared adiabatic, flue and dust templates | boundary-utility and unmapped-emission findings of the LCI |
| 2026-10-28 | process/, plant.yaml, equipment/, piping/, scripts/sic_balance.py | design basis, materials, reactions, balanced BFD/PFD (4 blocks, 7 steps), lists; furnace on a labelled specific-energy basis | concept flowsheet |
| 2026-10-28 | all | scaffold from cheme init | start of the case |
