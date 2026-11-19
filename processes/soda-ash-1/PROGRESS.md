# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-19 | DESIGN.md §4, lca/mappings.yaml | registry text brought up to date: only sodium-bicarbonate (and optional brine and light-soda-ash grades) still missing; "(no registry slug yet)" dropped from feed:LST, feed:COKE, feed:NH3; mappings header boilerplate about natural gas replaced | stale since #251 (audit) |
| 2026-11-19 | process/reactions.yaml | CALC source text quotes calcite at -1206.9 kJ/mol, which reproduces the stated 178.3 kJ/mol (value unchanged) | closes review R-04 (audit) |
| 2026-11-19 | process.yaml, DESIGN.md D-006 | EMEP/EEA 2.B.7 reference: dead 2019 eea.europa.eu URL (HTTP 410) replaced by the 2016 edition with DOI 10.2800/247535, one edition throughout; LCA outputs rewritten with the pinned core | provenance (audit, R-05 in part) |
| 2026-11-01 | process.yaml, lca/dataset.yaml, lca/manifest.json, process/*.yaml | entry made public; LCI gaps marked preliminary; credit and citation (f6b265e6) | library made public, CC-BY-4.0 |
| 2026-11-01 | README.md, AGENTS.md, DESIGN.md, scripts/solvay_balance.py, .claude/skills/ | licence and AI-notice wording; skill copies taken out of git (2adf056d) | public readiness (#299) |
| 2026-10-31 | process.yaml | `chemistry:` names the new registry slugs limestone, metallurgical-coke, sodium-chloride, ammonia, sodium-carbonate (6826bb01, cfd62123) | registry entries added (#251) |
| 2026-10-27 | DESIGN.md, PROGRESS.md | route/boundary memo, decisions D-001..D-010, evidence, missing registry entries, open inputs | concept record (#177) |
| 2026-10-27 | lca/ | preliminary gate-to-gate LCI per kg light soda ash, every background `missing:`; inventory, gaps and dataset written; mass/element/carbon balance closed | LCI scope of #177 |
| 2026-10-27 | process/, plant.yaml, equipment/, piping/, scripts/solvay_balance.py | design basis, materials, reactions, kiln basis (furnace fallback), balanced BFD/PFD (6 blocks, 12 steps), lists | concept flowsheet |
| 2026-10-27 | all | scaffold from cheme init | start of the case |
