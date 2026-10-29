# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | PROGRESS.md | Response to 2026-10-28-pfd-lci-review: closed #1, #2, #5, #6, #7, #9; open #3, #4, #8 (below); re-ran cheme check (concept gates pass except layout-plot-plan, out of scope; design-review now stale, as expected), cheme maturity (none, claim-exceeds warning unchanged), cheme process streams (all blocks and steps close), cheme assess lca --coverage (8 gaps, balances closed) | revision after the independent review |
| 2026-10-28 | process.yaml | CI fix: chemistry.inputs was empty (schema minItems 1, library catalog build error in tests/test_registry.py); the consumed steam (registry slug) moved from utilities to inputs with role utility until the BDO registry entry exists. Catalog build re-run locally: no error. Commit ba2ac43 | PR #213 CI |
| 2026-10-28 | DESIGN.md D-007, process.yaml | Response #1: D-007 and the process.yaml description state that the LP column duties assume one homogeneous liquid while NRTL predicts two; unverified until a VLLE check (I-04). Commit ba2ac43 | review finding #1 (medium) |
| 2026-10-28 | DESIGN.md D-007 | Response #2: steam range stated: lower bound at 1.3 x Rmin about -4 % total steam (hand estimate), screening range 3.6 MJ/kg -5 %/+30 % (the +30 % ASSUMED). Commit 5e0e557 | review finding #2 |
| 2026-10-28 | equipment/equipment-list.yaml, DESIGN.md D-010 | Response #5: E-206 11 barg, E-202 5.5 barg (steam side), other side in the notes; R-101 heating side 11 barg / 205 C in its notes; D-010 per-side rule. Commit 3d03231 | review finding #5 |
| 2026-10-28 | DESIGN.md D-005 | Response #6: THF dissolved in the bleed stated as neglected (< 0.1 % of the product, not calculated). Commit 3d03231 | review finding #6 |
| 2026-10-28 | DESIGN.md | Response #7: patent re-read in full: DHF 37-327 ppm (Examples and Comparative Examples 2-1 to 2-3), BDO <= 10 ppm in Example 1-4 (500 L reactor, 400 L charge); locators and source register corrected. Commit 5e0e557 | review finding #7 |
| 2026-10-28 | checks/checks.yaml, control/cause-effect.yaml | Response #9: template comments no longer cite D-023 / D-012; the cheme.decision-unknown infos are gone. Commit 3d03231 | review finding #9 |
| 2026-10-28 | (open) | Left open: #3 (adding the 25 kW auxiliaries to feed:POWER needs new energy ports on flowsheet steps, which would upset the energy balances matched to the script; stays a declared cutoff until the pumps are drawn at basic engineering), #4 (needs a sourced feed and capacity basis and a sourced selectivity, I-02), #8 (needs the BDO, THF and p-TSA registry entries outside this folder, in the consolidated PR) | review findings #3, #4, #8 (low) |
| 2026-10-28 | DESIGN.md, PROGRESS.md | route/boundary memo, decisions D-001 to D-011, LCI summary, evidence table, source register, method/dependency table, open inputs I-01 to I-12, missing registry entries | document the concept run (issue #126) |
| 2026-10-28 | process.yaml, lca/lca.yaml, lca/mappings.yaml, lca/ outputs | Atlas manifest (internal, concept, unreviewed, lca.source none); preliminary gate-to-gate LCI per kg THF, every background a gap (8), no overrides; mass and C/H/O/S balances closed; library LCI build --strict passes with the gaps | step 4 of the run |
| 2026-10-28 | process/*.yaml, process/BFD.xml, process/PFD.xml, scripts/thf_balance.py, equipment/equipment-list.yaml, plant.yaml | design basis, materials (5 components), reactions (2), flowsheet (2 blocks, 10 steps, 15 + 10 streams), independent NRTL balance script, generated BFD/PFD, 13 equipment items | concept design to a balanced PFD |
| 2026-10-28 | (all) | scaffold from cheme init and the process.yaml template | start of thf-1 |
