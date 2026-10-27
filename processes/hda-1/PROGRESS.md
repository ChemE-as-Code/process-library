# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-27 | DESIGN.md, process.yaml, PROGRESS.md, checks/checks.yaml | route/boundary memo, decisions D-001 to D-013, evidence table, source register, method/dependency table, open inputs, missing registry entries; Atlas manifest (internal, concept, unreviewed); BFD/PFD files in the concept gate | document the concept run (issue #42) |
| 2026-10-27 | lca/ | preliminary gate-to-gate LCI per kg benzene, every background open (10 gaps), substitution proposed; balance closed | step 4 of the run |
| 2026-10-27 | scripts/hda_balance.py, process/flowsheet.yaml, equipment list | C-202/C-203 reboiler duties from the arriving feed enthalpy (2300 and 650 kW); overall energy closure 0.25 % | energy check found the feeds taken at their bubble point |
| 2026-10-27 | equipment/equipment-list.yaml, piping/line-list.yaml | 18 items, 24 lines with ASSUMED design conditions and DN | lists as far as the PFD requires |
| 2026-10-27 | process/*.yaml, process/BFD.xml, process/PFD.xml, scripts/hda_balance.py | design basis, materials, reactions, flowsheet (2 blocks, 15 steps, 24 + 10 streams), independent balance script; generated BFD/PFD | concept design to a balanced PFD |
| 2026-10-27 | (all) | scaffold from cheme init and the process.yaml template | start of hda-1 |
