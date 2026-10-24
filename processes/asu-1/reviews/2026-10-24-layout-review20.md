---
topic: layout
reviewed_commit: 179b4308fbf87647f83ae3b7daebecc7d913b309
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, equipment/equipment-list.yaml, checks/checks.yaml, control/cause-effect.yaml, control/instrument-list.yaml, lca/lca.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 179b4308fbf87647f83ae3b7daebecc7d913b309, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: 179b4308fbf87647f83ae3b7daebecc7d913b309, relation: depends-on}
  - {path: DESIGN.md, revision: 179b4308fbf87647f83ae3b7daebecc7d913b309, relation: depends-on}
  - {path: scripts/psv_reaction.py, revision: 179b4308fbf87647f83ae3b7daebecc7d913b309, relation: analyses}
  - {path: process/flowsheet.yaml, revision: 179b4308fbf87647f83ae3b7daebecc7d913b309, relation: analyses}
  - {path: lca/results.md, revision: 179b4308fbf87647f83ae3b7daebecc7d913b309, relation: analyses}
  - {path: estimate/tea.md, revision: 179b4308fbf87647f83ae3b7daebecc7d913b309, relation: analyses}
reviewer: Claude (independent review agent; did not author D-092, the LCA change or the layout files)
reviewer_kind: agent
branch: feat/lca-open-data
merge: pending
---
# Review: layout, twentieth review (independent, confirming) of the LCA change D-092

This is a confirming review of branch `feat/lca-open-data` at 179b430, based on origin/main
7a31b2a. The branch replaces the LCA's example factors by open background data (D-092). It
makes review19 stale only because `lca/lca.yaml` is in review19's scope (the construction
take-off of the LCA reads the layout's material take-off). This record checks that the change
does not touch the layout and carries review19's open items forward.

Verdict: **the layout is unaffected; no layout finding is added.** review19#8 and #9 were
closed on main in ed0d3b3 before this branch was merged up to it.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|

No new finding.

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-layout-review19#8 | D-091 (5) claimed the DN250 tailpipe friction keeps the back pressure under 10 % of set, which the PSV-3116 warm bound does not meet | low | closed ed0d3b3 | D-091 (5) now gives the cold cases at about 3 % of set or less and the warm bounds at about 9 to 10 % (PSV-3114) and 12 to 13 % (PSV-3116); O1 adds the balanced-bellows valve or DN300 tailpipe for PSV-3116 if the warm case is credible. |
| 2026-10-24-layout-review19#9 | D-091 open list nested under the last bullet by a missing blank line | low | closed ed0d3b3 | A blank line now precedes "Remaining open after D-091" in DESIGN.md. |

## Drawing
`cheme validate` at 179b430: 0 errors, 34 warnings. That is review19's 33 plus one
`cheme.layout-model-version`, which comes from core's layout code having moved and is the same
on origin/main (no layout file differs). Counts per sheet:
- P-01: 0 line-through-label, 2 line-crossing (accepted: D-069, D-076), 0 label-overlap, 0
  label-far-from-owner;
- P-02: 0 in every count;
- P-03: 3 line-crossing (accepted), 0 otherwise;
- P-04: 1 line-crossing (accepted), 0 otherwise.

No P&ID changed on the branch, so no tile was read.

## Layout
- `git diff --stat origin/main HEAD` over `layout/`, `piping/`, `equipment/`, `electrical/`,
  `pid/`, `control/`, `checks/`, `process/`, `estimate/`, `scripts/` and `plant.yaml` is
  empty. Since review19's dcbdc28, the only changes in asu-1 outside `lca/` are D-091 (5) and
  the open list (ed0d3b3, the fixes of review19#8 and #9), D-092, PROGRESS.md, the AGENTS.md
  row for `lca/factors.yaml` and process.yaml (the ChemE-as-Code name, facets).
- `lca/lca.yaml`: only the background of each flow changed (factor ids, `proxy:`, `missing:`),
  the cooling water and concrete estimates, and the grid-2040 scenario was removed. The
  construction entries keep the same `takeoff`, `category` and `equipment` selectors. The
  take-off quantities in `lca/inventory.csv` are unchanged (steel 597567 kg, pipe 5175.89 m,
  concrete 192.741 m3, grating 511.707 m2, insulation 319.242 m2, the piece counts, equipment
  127000 / 455500 / 98000 kg).
- The layout code of the installed cheme-as-code does not read `lca/`: nothing in the layout
  model depends on the LCA.
- `cheme layout build --check` reports the model not up to date because of
  `layout-model-version` (built by other layout generator code). That holds on origin/main
  too, and the `layout-3d`, `lifting-study`, `layout-detail`, `electrical` and `hvac` gates fail
  there for the same reason. It is not caused by this branch: a `cheme layout build` on main
  fixes it. The model and its findings are those review19 recorded, so its counts and PNGs
  stand. No plan or section was rendered again, because no input of the model changed.

## Checked and fine
- **LCA outputs:** `cheme assess lca --check`: all current.
- **Stage gates:** no sign-off was written, and checks/status.json is untouched.

## Not checked
- **The LCA itself** (the factor mapping, the proxies, the gaps): not a layout matter; it was
  reviewed separately on the pull request.
- **The layout model with the current core:** it needs `cheme layout build` on main
  (`layout-model-version`); the next layout review checks the rebuilt model.
- Everything review19 lists under "Not checked" (relief sizing, pipe stress and lugs, CB-1X
  envelope, the S3 -> S4 allowance) stays open as D-091 O1 .. O6.
