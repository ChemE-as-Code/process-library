# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | lca/mappings.yaml, lca/lca.yaml, lca/* (generated) | feed:STEAM uses the shared `steam-heat` entry (kWh); allocation.deviation states why energy, not the price ratio | PR #224 CI: strict Atlas LCI build failed on the steam unit and the allocation hierarchy |
| 2026-10-28 | DESIGN.md, process.yaml, process/design-basis.yaml, PROGRESS.md | route/boundary memo, source register, decisions D-001..D-014, results, gated steps; manifest (internal, concept, unreviewed) and design basis | issue #181 concept stage |
| 2026-10-28 | lca/lca.yaml, lca/mappings.yaml, lca/* (generated) | preliminary gate-to-gate LCI per kg sales gas, energy allocation with the NGL, backgrounds missing, AP-42 1.4 heater emissions; inventory written | D-014 |
| 2026-10-28 | process/flowsheet.yaml (Q13) | demethaniser reboiler heat recorded as internal cold-box integration | boundary check (T401 had no energy stream) |
| 2026-10-28 | process/*.yaml, BFD, PFD, scripts/balance.py, equipment/equipment-list.yaml, plant.yaml | scaffold; sourced feed (Bullin and Krouskop 2009, Barnett well 2); balanced BFD/PFD (6 blocks, 19 steps, 34 material and 13 energy streams); PFD equipment list | D-001..D-013 |
