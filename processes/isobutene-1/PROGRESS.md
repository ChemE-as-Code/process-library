# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | DESIGN.md, process.yaml | D-005 C8 locator, D-001 attribution and I-09, purity caveat (32fd8c9) | review 2026-10-28-pfd-lci-review #1, #4, #5 |
| 2026-10-28 | process/flowsheet.yaml, BFD, PFD, lca/, D-009, design basis, equipment list, process.yaml | Q7 to LP steam, Q18 30 kW H-101 fan/hot-oil power replaces a cut-off; LCA regenerated (17d08e4) | review 2026-10-28-pfd-lci-review #2, #3 |
| 2026-10-28 | lca/lca.yaml | allocation `method` left at its default (mass) (088ef37) | CI: the Atlas build warned that the study method differs from the dataset's (none written for the default) |
| 2026-10-28 | DESIGN.md, PROGRESS.md | route/boundary memo, decisions D-001 to D-011, source register, open inputs I-01 to I-08 | record the concept basis (issue #165) |
| 2026-10-28 | process.yaml, lca/lca.yaml, lca/mappings.yaml, lca/*.csv | Atlas manifest (internal), foreground LCI per kg isobutene, mass allocation, 8 background gaps; `cheme assess lca --write` | preliminary gate-to-gate LCI (D-011) |
| 2026-10-28 | process/design-basis.yaml, materials.yaml, reactions.yaml, flowsheet.yaml, BFD, PFD, equipment list, scripts/ib_balance.py | design basis, 6 components, 3 reactions, balanced flowsheet (3 blocks, 18 steps, 30 streams, 17 duties), BFD/PFD generated, 16 equipment items | concept PFD of MTBE cracking (D-001 to D-010) |
| 2026-10-28 | (all) | scaffold from `cheme init` and the process template | start of isobutene-1 |

## Responses to review 2026-10-28-pfd-lci-review

- **CI (PR #204, library tooling tests)**: `lca/lca.yaml` no longer sets `allocation.method: mass`
  (the schema default); cheme writes no method into `lca/dataset.yaml` for the default, so the
  strict Atlas build no longer warns. Result unchanged. Commit 088ef37.
- **#1** (low, closed): D-005 now places the C8 figure in Example 1 (Table 6) of US 8,633,345 B2
  (C8/isobutene about 0.0005 mol/mol); Example 2 reports no C8; 0.001 kept ASSUMED. Commit 32fd8c9.
- **#2** (low, closed): Q7 (C-201 reboiler) moved from MP to LP steam in `process/flowsheet.yaml`
  (27 K approach > 10 K minimum); D-009, design basis, equipment list, manifest and the LCA
  follow (MP 1.16 MJ, LP 1.29 MJ per kg isobutene before allocation). Commit 17d08e4.
- **#3** (low, closed): the H-101 fan and hot-oil power is an energy stream Q18 (30 kW, ASSUMED)
  from POWER to H101 instead of an LCA cut-off; feed:POWER is 45.8 kW. Commit 17d08e4.
- **#4** (low, closed): D-001 attributes the route to the run's task; new open item I-09 for the
  issue's comparison of C4 separation cases with on-purpose production. Commit 32fd8c9.
- **#5** (low, closed): `process.yaml` description says pure MTBE feed, linear butenes and C5 not
  modelled (D-003), next to the 99.97 wt% purity. Commit 32fd8c9.
- **#6** (low, open): the concept gate `layout-plot-plan` and the basic/detail gates still fail;
  a plot plan, or a human accepting the gate as out of scope for this library case, is needed
  before a concept sign-off.
- **#7** (low, open): `cheme maturity` still reaches no level (unsourced capacity and MTBE assay,
  I-01); the `maturity: concept` claim and its note stay as the review proposes.
