# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | PROGRESS.md | Response entries for review 2026-10-28-pfd-lci-review (below) | review responses |
| 2026-10-28 | scripts/balance.py, process/flowsheet.yaml, equipment list, DESIGN.md D-008/D-014, BFD/PFD, lca/ | Response #1 (high): reactor and flash balanced separately; the specified V-102 split needs 11.2 MW, supplied from the reactor circuit by new flash heater E-102 (energy stream Q13 R101 -> V102); Q03 = reactor cooling to CW only (6.6 of 17.7 MW); D-008 corrected; steam, CW and LCI unchanged, adiabatic-flash penalty (+0.19 kWh/kg steam) recorded; O-9 added. Commit 34f3d03 | review #1 |
| 2026-10-28 | process.yaml | Response #2 (medium): N2 and CH4 feedstock rows removed; H2 kept as a minor `reactant` with a note naming methanol and CO as the feedstocks. Registry entries remain a separate library PR. Commit 34f3d03 | review #2 |
| 2026-10-28 | DESIGN.md D-003, evidence table | Response #3 (low): unread S2 no longer carries the D-003 reason or the propionic basis; S1's examples are the stated facts, D-004 stays ASSUMED. Commit 34f3d03 | review #3 |
| 2026-10-28 | process/flowsheet.yaml S06, scripts/balance.py | Response #4 (low): S06 378.7 K from the M101 enthalpy balance (balance.py prints T_S06_K). Commit 34f3d03 | review #4 |
| 2026-10-28 | process/flowsheet.yaml S18, DESIGN.md D-006, equipment list V-201 | Response #5 (low): S18 titled by composition (methyl acetate-rich); D-006 states the decanter split is not checked against LLE (re-check with core #315, O-7). Commit 34f3d03 | review #5 |
| 2026-10-28 | DESIGN.md Results | Response #6 (low): gap count corrected to 8. Commit 34f3d03 | review #6 |
| 2026-10-28 | DESIGN.md "Stage gates" | Response #8 (low): concept gate layout-plot-plan recorded as open on purpose for this bounded case; concept stage not signed off. Commit 34f3d03 | review #8 |
| 2026-10-28 | DESIGN.md D-013 | Response #9 (low): one statement of the boundary: gate-to-gate foreground, cradle-to-gate declared because every feed is to be linked. Commit 34f3d03 | review #9 |
| 2026-10-28 | lca/README.md, DESIGN.md D-013 | Response #10 (low): the generated 0 total/uncertainty means "no total"; core presentation issue still to report to cheme-as-code. Commit 34f3d03 | review #10 |
| 2026-10-28 | process.yaml maturity | Response #7 (low): left open; the `maturity-claim-exceeds` warning needs sourced split values or a human acceptance, disclosure kept. No commit | review #7 |
| 2026-10-28 | DESIGN.md | Route/boundary memo, source register S1-S9, reaction/model evidence, D-001..D-013, results per kg, method/dependency table, open inputs O-1..O-8, library items | #128 first bounded run |
| 2026-10-28 | lca/lca.yaml, lca/mappings.yaml, lca/*.csv, dataset.yaml | Preliminary gate-to-gate LCI per kg glacial acid, all backgrounds missing (gaps), mass and element balances closed | D-013 |
| 2026-10-28 | process/*.yaml, BFD, PFD, equipment list, scripts/balance.py, process.yaml | Design basis, materials, lumped reactions, flowsheet (scrubbing, reaction and flash, light ends with decanter, drying, heavy ends), recycles, balances closed; 17 equipment items | balanced concept PFD (D-001..D-012) |
| 2026-10-28 | all | Scaffold from cheme init and the process.yaml template | start of the case |
