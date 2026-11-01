---
topic: layout
reviewed_commit: f5dad54b934ffd22124fc2acf24f1de7b30ce283
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, equipment/equipment-list.yaml, checks/checks.yaml, control/cause-effect.yaml, control/instrument-list.yaml, lca/lca.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: f5dad54b934ffd22124fc2acf24f1de7b30ce283, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: f5dad54b934ffd22124fc2acf24f1de7b30ce283, relation: depends-on}
  - {path: DESIGN.md, revision: f5dad54b934ffd22124fc2acf24f1de7b30ce283, relation: depends-on}
  - {path: scripts/psv_reaction.py, revision: f5dad54b934ffd22124fc2acf24f1de7b30ce283, relation: analyses}
  - {path: process/flowsheet.yaml, revision: f5dad54b934ffd22124fc2acf24f1de7b30ce283, relation: analyses}
  - {path: lca/results.md, revision: f5dad54b934ffd22124fc2acf24f1de7b30ce283, relation: analyses}
  - {path: estimate/tea.md, revision: f5dad54b934ffd22124fc2acf24f1de7b30ce283, relation: analyses}
reviewer: Claude (independent review agent; did not author f5dad54 or the layout files)
reviewer_kind: agent
branch: fix/layout-model-refresh
merge: pending
---
# Review: layout, twenty-first review (independent, confirming) of the generator refresh

This is a confirming review of branch `fix/layout-model-refresh` at f5dad54, based on
origin/main 43f8cf5. Core's layout and flowsheet generator code moved. On main, that made
`layout-model-version` and `generated-version` fail the gates layout-3d, lifting-study,
layout-detail, electrical, hvac, process-balances and process-basic. The branch rebuilds the
BFD, the PFD and the layout model under core main. This is the fingerprint-only regeneration
that a core issue describes: only the generator fingerprint changes, and
the content is the same. review20 is stale only because `layout/plant-model.yaml` is in its
scope (and review19's).

Verdict: **the layout model, its findings and every output derived from it are unchanged; no
layout finding is added.**

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|

No new finding.

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|

None open. review19#8 and #9 were closed in ed0d3b3 (review20), and no earlier finding in this
scope is open.

## Drawing
`cheme validate` at f5dad54 gives 0 errors and 36 warnings: 13 instrument-no-interlock,
6 line-crossing, 12 template-metadata, 2 titleblock-sheet and 3 process-energy-balance. The
`layout-model-version` warning of review20 is gone. The 3 `process-energy-balance` warnings
(PRD, K4101, K4102 in process/flowsheet.yaml) are not caused by this branch, because
process/flowsheet.yaml did not change. They come from the installed core and are a process
matter outside this layout scope. Counts per sheet:
- P-01: 0 line-through-label, 2 line-crossing (accepted: D-069, D-076), 0 label-overlap, 0
  label-far-from-owner;
- P-02: 0 in every count;
- P-03: 3 line-crossing (accepted), 0 otherwise;
- P-04: 1 line-crossing (accepted), 0 otherwise.

No P&ID changed on the branch, so no tile was read.

## Layout
- **Diff:** `git diff --stat origin/main..HEAD` lists three files with one line each:
  - `layout/plant-model.yaml`: `provenance.generator_sha256` only, 1e9a6821... ->
    d1f862cf...;
  - `process/BFD.xml` and `process/PFD.xml`: `generator_sha256` in the `cheme-process` header
    comment only, b4fceb35... -> ac1b86de... In both, `source_sha256` and `output_sha256` are
    unchanged.
- **Independent rebuild:** in a fresh `git worktree add` of origin/main, I ran
  `cheme process build`, `cheme layout build`, `cheme layout lifting --write` and
  `cheme assess mto|estimate|equipment|tea|lca --write`. That rebuild changed only
  `layout/plant-model.yaml`, `process/BFD.xml` and `process/PFD.xml`, and all three are
  byte-identical (`cmp`) to the branch's. The lifting study, take-off, estimates, TEA and LCA
  did not change. The worktree has been removed.
- **Checks on the branch:**
  - `cheme layout build --check`: "layout/plant-model.yaml is up to date".
  - `cheme layout lifting --check`: exit 0.
  - `cheme assess mto|estimate|equipment|tea|lca --check`: all current.
  - `cheme datasheets drawing --check`: every drawing current.
  - `cheme process build` has no `--check`. Validate's generator comparison passes, with no
    `generated-version` or `generated-sheet-drift` warning.
- **Findings against main's model:**
  - `cheme layout report` on main and on the branch gives the same output (`diff` empty).
  - `cheme layout lifting` gives the same output on both.
  - The finding lines of `cheme layout build --check` are identical on both. The last line
    differs: main says "not up to date" (the version error), the branch says "up to date".
- **`cheme layout report` at f5dad54** (the same as review19 and review20):
  - **Lines:** 81, all routed except 4 skipped segments (GAN-3002, LN-3002, D-028; two
    VNT-3004), 0 unrouted.
  - **Chains per method:** astar 26, open 8, pinned 166, rack 15. No `direct` and no
    `rack+direct`.
  - **Reasons:** local 26 (above the pipe-way 7, pipe-way 5, pump run at grade 4, rack detour
    1, rack run too short 1, short run 8), open end 8, pinned 166, rack 15 (battery limit at a
    rack end 13, longer than local_max_m 2).
  - **Rack fill:** PR1 61 / 43 / 25 %, PR2 6 / 6 %, PR3 48 / 43 %.
  - **Model findings per rule:** access-enclosed 1, free-span 2, laydown 1, lifting 4,
    nozzle-unconnected 2, operability 1, support-missing 15, tier 1, tray-separation 1,
    tray-span 17, tray-zone 6. The build also lists 15 nozzle-defaulted. These are the same
    counts and the same acceptances in checks/checks.yaml as review19. There are 0 clash,
    headroom, access-blocked, wall-penetration, vent-outlet and escape findings.
  - **Objects:** 46 equipment items, 61 generated and 166 pinned pipes, 121 in-line items,
    8 platforms, 14 declared and 1 generated structures, 30 zones.
- **PNGs read (rendered at f5dad54):**
  - build/layout-plan.png;
  - build/layout-section-y68.png (along PR1);
  - build/layout-section-x133.png (through CB-1 and the compander).

  All three render without error. They show the same routes, racks, zones, pads, laydowns,
  CB-1 steel and RV platform as review19.

## Checked and fine
- **Stage gates:** `cheme check --no-write` before this record: 30 of 31 pass, and the only
  failure is layout-review (this record). No sign-off was written, and checks/status.json is
  untouched.
- **Generated outputs:** every `--check` above passes, and the rebuild from main reproduces
  the branch byte for byte.

## Not checked
- **The 3 `process-energy-balance` warnings:** a process matter that the core version raises.
  They are left to the process owner.
- Everything review19 lists under "Not checked" (relief sizing, pipe stress and lugs, the
  CB-1X envelope, the S3 -> S4 allowance) stays open as D-091 O1 .. O6.
