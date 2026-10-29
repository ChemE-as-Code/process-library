# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | lca/dataset.yaml, lca/README.md | `allocation.method: mass` written out in the generated dataset (cheme omits the default, `build_lci.py --strict` read it as None and warned); workaround documented | CI of PR #209 (tooling tests: test_the_library_builds_strict_with_the_utilities) |
| 2026-10-28 | DESIGN.md D-002, D-005, D-007, D-008, source register; process/design-basis.yaml | US 4,485,261 A re-read: equilibrium ratios' basis not stated, weight basis ASSUMED from its weight-basis prior art, mole-basis miss stated; US 7,309,403 B2 and US 2,206,584 A read, locators recorded; claims still resting on SR-1 abstract and SR-8 summary marked unverified | review #4, #5 (medium) |
| 2026-10-28 | DESIGN.md D-014, lca/README.md, lca/lca.yaml, lca/* (generated), process/reactions.yaml, checks/checks.yaml | MMA/TMA product cases stated (identical per kg under mass allocation); `0` totals explained as "no total"; steam exchange sources carry the upper-estimate caveat; unregistered secondary citation dropped; template decision id D-023 removed | review #3, #6 (medium), #9, #10, #11 (low) |
| 2026-10-28 | DESIGN.md D-006, D-011 | energy cross-check restated on a consistent (liquid) basis, wastewater heat named, cooler left open; column model-basis overstatement of `cheme maturity` noted for core | review #8, #7 (low) |
| 2026-10-28 | process/flowsheet.yaml S1/S2, BFD/PFD, checks/maturity.json, lca/* (generated), DESIGN.md D-006 | boundary feed flows and compositions `given` as the study's design specification; `cheme maturity` reaches balanced, written; concept claim within cap | review #2 (medium) |
| 2026-10-28 | process.yaml, DESIGN.md D-013 | unregistered chemicals (methanol, ammonia, MMA, DMA, TMA) out of `chemistry`, named in `validation.notes`; library catalog build exits 0 | review 2026-10-28-pfd-lci-review#1 (high) |
| 2026-10-28 | DESIGN.md, PROGRESS.md | route/boundary memo, source register, decisions D-001..D-014, open inputs, method table | record of the concept stage |
| 2026-10-28 | lca/lca.yaml, lca/mappings.yaml, lca/* (generated) | preliminary gate-to-gate LCI per kg DMA, mass allocation, all backgrounds unmapped gaps; inventory, gaps, dataset written | scope step 4 (D-014) |
| 2026-10-28 | process/simulation.yaml | R-101 declared adiabatic (no DWSIM run) | LCA boundary check |
| 2026-10-28 | process/design-basis.yaml, process.yaml, equipment/equipment-list.yaml | design basis, manifest (internal, concept), 11 PFD items | scope steps 1 and 5 |
| 2026-10-28 | process/materials.yaml, reactions.yaml, catalysts.yaml, flowsheet.yaml, BFD/PFD | balanced flowsheet: equilibrium converter (cheme), recycle loop and sharp-split train (scripts/mass_balance.py) | scope steps 2 and 3 |
| 2026-10-28 | (all) | scaffold from cheme init and the process template | start of the case |

## Review responses: reviews/2026-10-28-pfd-lci-review.md

| finding | severity | response | commit | state |
|---|---|---|---|---|
| #1 | high | Response: the five unregistered chemicals are out of `chemistry` and named with their inventory keys in `validation.notes` (as ammonia-1); `scripts/build_catalog.py` exits 0. Registry entries stay for the registry PR (outside this folder, D-013). | 8c42651 | closed |
| #2 | medium | Response: S1/S2 flow and composition `given` as the study's design specification (D-002/D-003, themselves ASSUMED); `cheme maturity` reaches balanced, checks/maturity.json written; claim `concept` within the cap; the wrong run-report statement corrected in D-006. | e5361f9 | closed |
| #3 | medium | Response: D-014 and lca/README.md state that per kg MMA (#171) and per kg TMA the inventory equals the per-kg-DMA one under mass allocation. | 9d2358a | closed |
| #4 | medium | Response: US 4,485,261 A re-read; it does not state the basis of its equilibrium ratios. Weight basis recorded as an ASSUMED inference from its weight-basis prior art, with the mole-basis consequence (D-005, design basis). A second source with a stated basis is still wanted (O-1). | fdea259 | closed (benchmark remains weak) |
| #5 | medium | Response: US 7,309,403 B2 and US 2,206,584 A read, locators in the register; D-007/D-008 checked against them. D-002 (SR-1 abstract) and the C-102 reflux (SR-8) marked unverified. | fdea259 | closed |
| #6 | medium | Response: D-014 and lca/README.md say the `0` totals mean "no total"; the generated output itself is a core issue (to report). | 9d2358a | closed here, core issue open |
| #7 | low | Response: noted in D-011 for core. | e5361f9 | closed here, core issue open |
| #8 | low | Response: cross-check restated on a consistent basis in D-006. The wastewater cooler is not added (flowsheet change left for the next stage, O-3). | e5361f9 | partly closed |
| #9 | low | Response: MPS/LPS exchange sources carry "upper estimate, no heat integration (D-009)". No open benchmark found yet. | 9d2358a | closed |
| #10 | low | Response: the secondary citation through US 7,754,921 dropped from reactions.yaml. | 9d2358a | closed |
| #11 | low | Response: template D-023 in checks.yaml replaced by a placeholder. | 9d2358a | closed |

After the responses: `cheme validate` 0 errors, 0 warnings; `cheme check` concept gates ok except
layout-plot-plan (out of scope), design-review fails until a new review of this branch; `cheme
maturity` balanced; `cheme process streams` all balances ok; `cheme assess lca --coverage` partial
screening carbon footprint, 7 gaps, outputs current. Merge pending a re-review.
