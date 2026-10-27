# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-27 | lca/, DESIGN.md D-014, O-6, process.yaml | allocation substitution -> shares 1/0 with a recorded deviation (system model cutoff); Pt/Rh loss as a never-cut consumable (ASSUMED amount), other catalysts as cut-off entries; cradle-to-gate wording, 0.68 kg CO2-eq/kg stated as direct N2O only; outputs rewritten | PR #191 CI (library LCI export refuses substitution); review 2026-10-27-pfd-lci-review #1, #2 |
| 2026-10-27 | lca/ | preliminary gate-to-gate LCI per kg contained HNO3: lca.yaml, inventory, gaps, dataset, coverage; backgrounds unmapped | run scope item 4 (D-014) |
| 2026-10-27 | process.yaml, DESIGN.md | Atlas manifest (internal, concept, unreviewed), source register, basis and method tables, decisions D-001 to D-014, open inputs, missing registry entries | run scope items 1, 3, 5 |
| 2026-10-27 | process/, equipment/, scripts/hno3_balance.py, plant.yaml | design basis, reactions, balanced BFD/PFD (4 blocks, 21 steps, 31 material and 12 energy streams), equipment list, independent balance script | run scope item 2 (D-001 to D-013) |
| 2026-10-27 | (all) | scaffold from cheme init and the process template | start of issue #119 |
