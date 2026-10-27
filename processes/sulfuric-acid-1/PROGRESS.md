# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-27 | `process/flowsheet.yaml` layout, `process/PFD.xml` | drying block pinned below the furnace | the generated layout drew it downstream of the absorption block |
| 2026-10-27 | `DESIGN.md`, `process.yaml`, `PROGRESS.md` | route/boundary memo, decisions D-001..D-013, reaction evidence, source register, core dependencies, open inputs; Atlas manifest (internal, concept, unreviewed) | concept stage record (#175) |
| 2026-10-27 | `lca/lca.yaml`, `lca/*` (generated) | preliminary gate-to-gate LCI per kg 98.5 wt% acid: every foreground exchange from the flowsheet, backgrounds unmapped (8 gaps), SO2/SO3 elementary; inventory, coverage and balance written | D-013 |
| 2026-10-27 | `equipment/equipment-list.yaml` | 16 items of the PFD with service and duty notes | flowsheet links resolve (D-006) |
| 2026-10-27 | `process/*.yaml`, `process/BFD.xml`, `process/PFD.xml`, `scripts/balance.py` | design basis, materials, reactions, catalyst, flowsheet (4 blocks, 24 steps), adiabatic modes; BFD/PFD built; all balances closed | D-001..D-010 |
| 2026-10-27 | all | scaffold from `cheme init` and the process template | start of #175 |
