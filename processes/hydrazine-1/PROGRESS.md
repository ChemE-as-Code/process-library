# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-29 | process.yaml chemistry feed:N2F | grade named: nitrogen/gan-8barg-10ppm (gaseous site/pipeline N2, D-015), so the Atlas links the GAN market and refuses ASU-1's LIN instead of warning "several Atlas producers"; no balance or LCI amount changed; main merged | library CI tests/test_utilities.py strict LCI build |
| 2026-10-28 | Response 2026-10-28-pfd-lci-review#2 | D-015: N2 sweep of the R-101/V-101 headspaces (S04, 634 kg/h, O2 at most 8 mol% in the vent, ASSUMED target below an unsourced LOC, I-04); vent and NH3/MEK make-up rebalanced, BFD/PFD rebuilt, LCI regenerated with feed:N2F as a gap; commit dd9831e | O2-rich, MEK-bearing headspace |
| 2026-10-28 | Response 2026-10-28-pfd-lci-review#1 | C-401 steam stated as a lower bound in D-010, Q05, lca.yaml feed:MPS and process.yaml; high variant (reflux 2.5, hydrolysis 25-75 kJ/mol) 4 300-4 858 kW, +18 % MP steam, in scripts/balance.py; a computed LCA scenario needs a second flowsheet case (I-02); commit dd9831e | review finding (medium) |
| 2026-10-28 | Response 2026-10-28-pfd-lci-review#3 | D-004 and process.yaml: H2O2 per kg N2H4 at yields 0.81/0.85/0.95 (1.317/1.255/1.123 kg); I-01 stays open (Hayashi et al. 1976 not read); commit dd9831e | review finding (low) |
| 2026-10-28 | Response 2026-10-28-pfd-lci-review#4 | lca.yaml feed:H2O2: quantity is the 70 wt% solution mass (0.803 kg H2O2 100 % per kg hydrate), mapping must convert; commit dd9831e | review finding (low) |
| 2026-10-28 | Response 2026-10-28-pfd-lci-review#5 | D-010 and Q08: R-101 cooling restated as an order-of-magnitude estimate (liquid NH3 feed about -0.5 MW, dissolution heat not counted); commit dd9831e | review finding (low) |
| 2026-10-28 | Response 2026-10-28-pfd-lci-review#7 | DESIGN.md S5: per-species NIST WebBook locators by CAS; values still not re-fetched (stated); commit dd9831e | review finding (low) |
| 2026-10-28 | Response 2026-10-28-pfd-lci-review#8 | new open item I-11 (materials for H2O2/hydrazine service); R-101 note points to it; commit dd9831e | review finding (low) |
| 2026-10-28 | Response 2026-10-28-pfd-lci-review#9 | process.yaml lca.notes: the results.csv total 0 is not a zero footprint; the cheme-as-code report is still to be filed (generated file not edited); commit dd9831e | review finding (low) |
| 2026-10-28 | Response 2026-10-28-pfd-lci-review#6 | left open: the cheme.maturity-claim-exceeds warning needs a human to accept it (or a sourced capacity basis) | review finding (low) |
| 2026-10-28 | CI (PR 235) | no failed run to read: every run for the branch was queued; the CI steps re-run locally (fmt --check, validate, lca --check, build_lci --strict, tests, catalog) show no hydrazine-1 error | task step |
| 2026-10-28 | DESIGN.md S9, D-007, I-05; process/flowsheet.yaml S41; process.yaml; BFD, PFD, lca/ (regenerated) | US 4,725,421 added: supports the MEK overhead composition, gives the lower-water hydrolysis alternative; library tests (412) pass with hydrazine-1 | evidence for D-007 |
| 2026-10-28 | DESIGN.md, PROGRESS.md | route and boundary memo, source register S1-S8, decisions D-001 to D-014, results, open items I-01 to I-10 (incl. core finding I-08, registry entries I-09) | issue #141 scope steps 3, 5 |
| 2026-10-28 | lca/, process.yaml, process/flowsheet.yaml | preliminary LCI per kg hydrazine hydrate, every background a gap; manifest internal, concept; regeneration steam split heater/column (same total) | issue #141 scope step 4 |
| 2026-10-28 | process/*.yaml, BFD, PFD, equipment list, scripts/balance.py | design basis, materials, reactions, 4-block / 11-step flowsheet, balances closed; one equipment tag per PFD step | issue #141 scope steps 1-2 |
| 2026-10-28 | all | scaffold from cheme init and the process template | start of the case |
