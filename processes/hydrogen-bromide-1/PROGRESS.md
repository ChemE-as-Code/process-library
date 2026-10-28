# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | PROGRESS.md | Response to review 2026-10-28-pfd-lci-review: #1 (medium) left open: the HBr integral heat of solution still needs reading at source (NBS tables, Wagman et al. 1982 or Parker 1965) before Q4 and the LCI are re-run; not a quick fix (D-009, gate core#364) | review responses |
| 2026-10-28 | PROGRESS.md | Response to review #8 (low) left open by design: the `maturity-claim-exceeds` disclosure stays in process.yaml until the feeds and absorber recoveries are sourced, as the review proposes | review responses |
| 2026-10-28 | process.yaml, equipment/equipment-list.yaml | Response to review #7 (low): R-101's 300 degC design temperature applies to the chamber shell and jacket; the burner tube gets its own (TBD) at the datasheet stage (commit 9eebaf5) | review responses |
| 2026-10-28 | DESIGN.md SRC-9, D-007, process/flowsheet.yaml, process.yaml, BFD/PFD | Response to review #6 (low): IF97 cited as IAPWS R7-97(2012) region 4 Eq. 30/31 with values computed by CoolProp 8.0.0 IF97; LPS saturation corrected 420.8 -> 421.1 K; Hydrogen bromide Wikipedia URL and IAPWS as their own references. SRC-6 remains a search summary (#1) (commit 9eebaf5) | review responses |
| 2026-10-28 | DESIGN.md D-008, process/flowsheet.yaml S9 | Response to review #4 (low): weak acid S9 flows by gravity, C-202 stacked above C-201 with about 2 m of liquid leg (ASSUMED); pump rejected (commit 9eebaf5) | review responses |
| 2026-10-28 | DESIGN.md section 3 | Response to review #5 (low): dHr unit corrected to kJ per mol extent (MJ per kmol) (commit 77e5b89) | review responses |
| 2026-10-28 | lca/lca.yaml, DESIGN.md D-012, D-013, lca/* (generated) | Response to review #2 (medium): the R-102 activated carbon make-up and spent carbon are `cutoff:` flows of 130 kg/a each (ASSUMED from bed volume at GHSV 1 000 1/h and a yearly change-out), checked by the 1 % mass rule (0.0008 %), instead of an exclusion without an amount (commit 77e5b89) | review responses |
| 2026-10-28 | lca/lca.yaml, lca/mappings.yaml, lca/* (generated) | Response to review #3 (low) and CI fix: Br2 to air declared elementary, not free; feed:LPS mapped to `steam-heat` (kWh) for the Atlas build. The tooling tests had refused the dataset (LPS steam slug in kg against a kWh exchange; free Br2 not in pass_through) (commit be4b902) | PR #229 CI, review responses |
| 2026-10-28 | lca/lca.yaml, lca/mappings.yaml, lca/* (generated) | Preliminary gate-to-gate LCI per kg HBr in 48 wt-% acid: every foreground exchange from the flowsheet, all backgrounds `missing:` (8 gaps), vent emissions, declared exclusions; mass, Br and H close (D-012) | issue #130 scope step 4 |
| 2026-10-28 | DESIGN.md, process.yaml | Route/boundary memo, source register, reaction and model evidence, decisions D-001..D-012, results, gated steps, open inputs and missing registry entries; Atlas manifest (internal, concept, unreviewed) | issue #130 scope steps 1, 3, 5 |
| 2026-10-28 | process/flowsheet.yaml, simulation.yaml, BFD/PFD | R102 finishing bed as an adiabatic ideal-gas equilibrium reactor instead of an unsourced conversion override (Br2 3.6e-12 mol/mol out) | model basis rests on data (cheme maturity) |
| 2026-10-28 | process/*.yaml, scripts/balance.py, equipment/equipment-list.yaml, BFD/PFD | Design basis, materials, reaction, catalyst; BFD (3 blocks) and PFD (7 steps, 12 material and 6 energy streams) with closed balances; independent balance script; PFD equipment list | issue #130 scope step 2 |
| 2026-10-28 | all | Scaffold from `cheme init` and the process.yaml template | start of the case |
