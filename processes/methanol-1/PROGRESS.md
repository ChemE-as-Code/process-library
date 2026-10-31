# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-31 | DESIGN.md D-013 | Re-checked the simulation inputs with cheme 1.2.1 (the CI pin since #282): fmt, validate, `process simulate --check` (stops at sim-unavailable) and maturity give the same result as with 1.1.0; review note updated | the CI pin moved after D-013 was written |
| 2026-10-30 | process/simulation.yaml, DESIGN.md D-013 | DWSIM inputs: PR with recorded selection and substitution, specs from D-003..D-010, equilibrium converter at its outlet temperature (core #58), V-102 at the script's let-down temperature, shortcut columns, tears S12/S6; validated and translated offline (`cheme process simulate --check` stops at sim-unavailable); not run, no values filled | independent check of the D-006 script once DWSIM is available |
| 2026-10-27 | DESIGN.md D-005, scripts/loop_balance.py | Approach-to-equilibrium sensitivity 0/10/20 K (optional script argument) | show what the ASSUMED approach moves |
| 2026-10-27 | process.yaml, DESIGN.md | Manifest (internal, concept, unreviewed; registry gaps noted); route/boundary memo, D-001..D-012, reaction/model evidence table, source register, method/dependency table, open inputs I-01..I-08 | #118 first bounded job: design basis to a balanced PFD |
| 2026-10-27 | equipment/equipment-list.yaml, piping/line-list.yaml | 14 equipment items and 19 lines from the PFD, ASSUMED design conditions (D-012) and first-pass DN (D-011, scripts/loop_balance.py) | lists as far as the PFD requires; process links resolve |
| 2026-10-27 | process/*.yaml, BFD, PFD, scripts/loop_balance.py | Design basis, methanol chemistry (cheme library + CH4/N2), flowsheet with compression, recycle loop, equilibrium converter, HP/LP separation, purge, topping and refining columns; balances closed; BFD/PFD generated | concept PFD of the synthesis loop and purification (D-001..D-010) |
