# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-01 | lca/*, scripts/allocation_exergy.py, process.yaml, DESIGN.md D-015, I-09 | Preliminary gate-to-gate LCI per kg methanol, exergy allocation among MEOH, MPS, FUELGAS (MPS 1394.0 kJ/kWh, saturated vapour; the first value 1152.7 was evaluated on the liquid root); purge not a co-product (I-09 closed: it returns to the plant's own reformer fuel), kept as a free exchange; dataset generated; `lca.source: auto`; inventory keys of SYNGAS components, MPS and FUELGAS removed; registry notes updated | #308: methanol-1 had no LCI dataset; independent review |
| 2026-10-27 | DESIGN.md D-005, scripts/loop_balance.py | Approach-to-equilibrium sensitivity 0/10/20 K (optional script argument) | show what the ASSUMED approach moves |
| 2026-10-27 | process.yaml, DESIGN.md | Manifest (internal, concept, unreviewed; registry gaps noted); route/boundary memo, D-001..D-012, reaction/model evidence table, source register, method/dependency table, open inputs I-01..I-08 | #118 first bounded job: design basis to a balanced PFD |
| 2026-10-27 | equipment/equipment-list.yaml, piping/line-list.yaml | 14 equipment items and 19 lines from the PFD, ASSUMED design conditions (D-012) and first-pass DN (D-011, scripts/loop_balance.py) | lists as far as the PFD requires; process links resolve |
| 2026-10-27 | process/*.yaml, BFD, PFD, scripts/loop_balance.py | Design basis, methanol chemistry (cheme library + CH4/N2), flowsheet with compression, recycle loop, equilibrium converter, HP/LP separation, purge, topping and refining columns; balances closed; BFD/PFD generated | concept PFD of the synthesis loop and purification (D-001..D-010) |
