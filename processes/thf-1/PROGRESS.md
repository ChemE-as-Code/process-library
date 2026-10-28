# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | DESIGN.md, PROGRESS.md | route/boundary memo, decisions D-001 to D-011, LCI summary, evidence table, source register, method/dependency table, open inputs I-01 to I-12, missing registry entries | document the concept run (issue #126) |
| 2026-10-28 | process.yaml, lca/lca.yaml, lca/mappings.yaml, lca/ outputs | Atlas manifest (internal, concept, unreviewed, lca.source none); preliminary gate-to-gate LCI per kg THF, every background a gap (8), no overrides; mass and C/H/O/S balances closed; library LCI build --strict passes with the gaps | step 4 of the run |
| 2026-10-28 | process/*.yaml, process/BFD.xml, process/PFD.xml, scripts/thf_balance.py, equipment/equipment-list.yaml, plant.yaml | design basis, materials (5 components), reactions (2), flowsheet (2 blocks, 10 steps, 15 + 10 streams), independent NRTL balance script, generated BFD/PFD, 13 equipment items | concept design to a balanced PFD |
| 2026-10-28 | (all) | scaffold from cheme init and the process.yaml template | start of thf-1 |
