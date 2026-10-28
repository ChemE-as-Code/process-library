# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | process/flowsheet.yaml, PFD, BFD, scripts/eg_balance.py, equipment list, lca/, DESIGN.md, process.yaml, checks/checks.yaml | revision after the review 2026-10-28-pfd-lci-review: E-101 feed preheat (E100) and glycol feed heater (E401) modelled, steam import 3.95 GJ/t MEG (was 1.62), sensitivity, consumables declared, gate scope and maturity claim recorded (39 material, 24 energy streams; 17 equipment items) | close the review's high finding, and the medium and low ones where quick (responses below) |
| 2026-10-28 | DESIGN.md, PROGRESS.md, process.yaml | source register, decisions D-001 to D-011, honest maturity notes | record the route, basis, evidence and gated steps (#172) |
| 2026-10-28 | lca/lca.yaml, lca/mappings.yaml, lca/*.csv, dataset.yaml | preliminary gate-to-gate LCI per kg MEG, every background a declared gap; inventory and coverage written | scope item 4 of the run (D-010) |
| 2026-10-28 | equipment/equipment-list.yaml | 16 PFD items with balance values | lists as far as the PFD requires (D-009) |
| 2026-10-28 | process/*.yaml, BFD, PFD, scripts/eg_balance.py | design basis, materials, reactions, balanced flowsheet (37 material, 22 energy streams), BFD/PFD built | concept flowsheet (D-001 to D-008) |
| 2026-10-28 | all | scaffold from cheme init | start of the case |

## Responses to review 2026-10-28-pfd-lci-review

| finding | response | commit |
|---|---|---|
| #1 (high) EO loop energy, steam overstated | Closed. Feed side of the E-101 feed/effluent exchanger modelled as step E100 (feed gas 333 -> 483 K, 64.5 MW, Q24; new stream S38, S5 now 483 K). Steam raised = reaction heat less the gas heating across R-101 (83.5 - 17.2 = 66.3 MW). Trim cooler 24.8 MW. MP steam import, LCI feed:MPS, D-008 and process.yaml updated: 3.95 GJ/t MEG (was 1.62). | f243f12, b00677a, 0e764e7 |
| #2 (medium) glycol feed heating missing | Closed. Glycol reactor feed heater E401/E-401 (MP steam, 384 -> 423 K, 15.2 MW, Q23; new stream S39). S23 and S31 take the 393 K of S30 (a splitter has no duty). D-008 records why MP steam rather than effluent heat (no double count with the hydration heat credit). | f243f12, 0e764e7 |
| #3 (medium) unsourced product split, optimistic case | Partly closed. Sensitivity added to eg_balance.py and D-005 (relative rate 2/3 x selectivity 85/80 %): ethylene 0.596-0.662 kg/kg MEG, MEG share 92.0-88.6 %, steam 2.6-4.1 GJ/t. The relative rate is still unsourced; an LCA scenario would need a second flowsheet case (left open). | f243f12, 0e764e7 |
| #4 (medium) consumables only in a comment | Closed. Silver catalyst counted as a consumable (ASSUMED 0.2 kg/t EO, gap, disposal to silver recovery); K2CO3 make-up and moderator declared `cutoff:`. All three now listed as limitations. Side effect: element and carbon-origin balances not assessable (core takes no consumable composition from lca.yaml, D-010). | b00677a, 0e764e7 |
| #5 (low) purge CO2 factor | Closed. Text corrected to about 2.2 kg CO2/kg purge (0.60 kg C/kg). | b00677a |
| #6 (low) maturity claim warning | Closed as an accepted warning with its reason (D-012, process.yaml validation.notes). | 0e764e7 |
| #7 (low) heavies below BREF range | Closed by sensitivity: D-005 gives the residue at the BREF lower bound (55 kg/h, 1.1 g/kg MEG) and its effect (none material on split and allocation). The glycol bleed stream is still not modelled. | 0e764e7 |
| #8 (low) concept gate cannot pass | Closed. layout-plot-plan marked `applies: false` with the scope reason (D-001, D-012); the concept gates now all pass or are n/a. | 0e764e7 |
