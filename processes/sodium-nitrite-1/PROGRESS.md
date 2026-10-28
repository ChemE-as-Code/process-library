# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | lca/mappings.yaml, lca/lca.yaml | CI fix (a4b5336): feed:LPS -> `steam-heat` (kWh, not kg of `steam`); allocation as mass shares 0.86226/0.13774 (`method: shares`) so the dataset carries its default method; NH3/NO2 elementary. Atlas build over the library: 0 errors, 0 warnings (cutoff and substitution) | PR #227 library tooling tests failed |
| 2026-10-28 | scripts/balance.py, flowsheet Q6, Q7, PFD, LCI, D-010 | Response 2026-10-28-pfd-lci-review#1 (a4b5336): E-301 duty from effect balances incl. feed sensible heat, condensate feed preheat and BPE 20/8 K; economy 1.69 instead of 1.8; Q6 1 245 -> 1 402 kW, Q7 2 974 -> 2 692 kW; LP steam 0.634 -> 0.688 kWh/kg allocated | review finding (medium) |
| 2026-10-28 | DESIGN.md D-010 | Response #2 (a4b5336): E-301 backward feed; effect 1 at 398 K/120 kPa(a) heated by WHB and 450 kPa(a) LP steam (22.6 K driving force), effect 2 under vacuum (~63 kPa(a)); S12 state kept | review finding (medium) |
| 2026-10-28 | DESIGN.md D-005, D-013, process.yaml | Response #3 (a4b5336): SRC-3's 2.8 % N2O (with its nitrogen inconsistency) recorded as conflicting evidence; N2O sensitivity 1.4 % vs 2.8 % (1.47 vs about 2.63 kg CO2-eq/kg); factor-2 uncertainty stated | review finding (medium) |
| 2026-10-28 | DESIGN.md basis table, D-010 | Response #4 (a4b5336): recycle reworded: no effect on the external mass balance, about 20 % of the E-301 evaporation | review finding (low) |
| 2026-10-28 | scripts/balance.py, flowsheet S4, Q1, Q3, D-005, D-011 | Response #5 (a4b5336): S4 at the blower outlet 317.7 K; R101 duty 1 964.2 -> 2 005.2 kW (cheme equal), Q1 1 927.6 kW, Q3 83.1 kW | review finding (low) |
| 2026-10-28 | scripts/balance.py, flowsheet S8, Q4, D-010 | Response #6 (a4b5336): T-201 adiabatic with Na2CO3 heat of solution, S8 344.7 K; C201 cools it, Q4 1 733 -> 2 074 kW | review finding (low) |
| 2026-10-28 | DESIGN.md D-005 | Response #7 (a4b5336): why the NaNO2 yield per NH3 and the WHB steam differ from SRC-3's example; which SRC-3 figures are used where | review finding (low) |
| 2026-10-28 | lca/lca.yaml | Response #8 (a4b5336): emission:NH3 and emission:NO2 elementary to air (0 kg) instead of free; they now count as gaps in climate change (no GWP), 10 gaps | review finding (low) |
| 2026-10-28 | process.yaml | Response #9 (a4b5336): per-kg notes labelled "before allocation" and updated | review finding (low) |
| 2026-10-28 | DESIGN.md D-008 | Response #10 (a4b5336): no DOI found for the J. Chem. Eng. Data review; the three solubility values marked unverified | review finding (low) |
| 2026-10-28 | DESIGN.md section 3 | Response #11 (a4b5336): oxidation degree target stated as the balance value (about 0.53), not exceeding what the nitrate specification allows | review finding (low) |
| 2026-10-28 | DESIGN.md D-013, lca/lca.yaml feed:SODA | Response #12 (a4b5336): note to check that a linked soda-ash background treats the carbonate carbon as bound in the product | review finding (low) |
| 2026-10-28 | equipment list, flowsheet, lca.yaml, PFD | dryers retagged D-301/D-401 -> DR-301/DR-401 | cheme read the tags as decision ids (cheme.decision-unknown) |
| 2026-10-28 | DESIGN.md | IPCC N2O default confirmed (EPA 2013, CDM MP49); solubility plausibility of the concentrate | source audit |
| 2026-10-28 | DESIGN.md, PROGRESS.md, process.yaml | route memo, source register, evidence, basis and method tables, D-001..D-013, open inputs, registry gaps; Atlas manifest (internal, concept, unreviewed) | issue #168 stage: design basis to preliminary LCI |
| 2026-10-28 | lca/ | preliminary gate-to-gate LCI per kg NaNO2, mass allocation with NaNO3, every background a gap; inventory, coverage written | D-013 |
| 2026-10-28 | process/, equipment/, scripts/balance.py, BFD, PFD | design basis, materials, reactions, flowsheet (4 blocks, 11 steps), balance script, equipment list; BFD and PFD generated | D-001..D-012 |
| 2026-10-28 | all | scaffold from cheme init and the process.yaml template | start of the case |
