# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-11 | process/BFD.xml, process/PFD.xml, lca/manifest.json, README.md (core pin); library REFERENCE.md, docs/coverage.md (merge) | merged the updated PR #323 branch (73286e26, which carries origin/main at 72546736, core v1.11.0 c21e6c7); BFD/PFD rebuilt by cheme process build (generator 7), lca/ rewritten by cheme assess lca --write (software version only, results unchanged); REFERENCE.md and docs/coverage.md conflicts resolved by keeping main's new rows and this branch's styrene-1 row (tier 2, engineering project; folder counts 62 engineering, 35 manifest-only) | bring PR #324 up to date with main and with #323 so it can merge |
| 2026-11-03 | DESIGN.md, README.md, checks/checks.yaml; library REFERENCE.md, coverage.yaml, docs/coverage.md | decisions D-001 to D-014 (simulation vs script, LLE handling, pilot vs flowsheet vs BREF), open inputs, source register; README for the plant folder; BFD/PFD in the concept gate; library listings say flowsheet (tier 2) | document the concept run |
| 2026-11-03 | lca/mappings.yaml, benchmarks/styrenics.yaml (merge) | merged PR #323 (ethylbenzene-1 concept) so that feed:EB links its lca/dataset.yaml | the link needs that file |
| 2026-11-03 | lca/lca.yaml, lca/ outputs, lca/mappings.yaml, process.yaml, benchmarks/styrenics.yaml; lca/datasets/ removed | flowsheet-derived LCI per kg styrene replaces the Tier 1 dataset (D-013, D-014) | the LCI of the PFD |
| 2026-11-03 | equipment/equipment-list.yaml | 17 items with ASSUMED design data | PFD links resolve |
| 2026-11-03 | plant.yaml, process/flowsheet.yaml, process/simulation.yaml, process/simulation-run.json, process/BFD.xml, process/PFD.xml | flowsheet (3 blocks, 27 steps, 43 material and 13 energy streams); DWSIM run (Peng-Robinson as a recorded substitution) converged, off-gas compression excluded, V-101/V-102/X-101 specified splits, C-303 rigorous; BFD/PFD generated | concept PFD with a simulation cross-check (D-012) |
| 2026-11-03 | process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, scripts/sm_balance.py | design basis (300 kt/a, LVOC BREF facts), 12 components, dehydrogenation and burner reactions, independent balance script (mass closure 1e-8, energy 7 kW of 264 MW) | concept design basis and balance (D-002 to D-011) |
| 2026-11-03 | (all) | scaffold from cheme init (core v1.4.1) around the manifest-only pilot | start of the concept plant folder (#313) |
