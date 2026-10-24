---
topic: layout
reviewed_commit: 94ece68be6122dab9c07781e23c2afa13e9e2bec
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, checks/checks.yaml, control/cause-effect.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 94ece68be6122dab9c07781e23c2afa13e9e2bec, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: 94ece68be6122dab9c07781e23c2afa13e9e2bec, relation: depends-on}
  - {path: DESIGN.md, revision: 94ece68be6122dab9c07781e23c2afa13e9e2bec, relation: depends-on}
  - {path: scripts/datasheet_sizing.py, revision: 94ece68be6122dab9c07781e23c2afa13e9e2bec, relation: analyses}
  - {path: process/simulation-run.json, revision: 94ece68be6122dab9c07781e23c2afa13e9e2bec, relation: analyses}
  - {path: process/flowsheet.yaml, revision: 94ece68be6122dab9c07781e23c2afa13e9e2bec, relation: analyses}
  - {path: process/simulation.yaml, revision: 94ece68be6122dab9c07781e23c2afa13e9e2bec, relation: analyses}
  - {path: estimate/tea.md, revision: 94ece68be6122dab9c07781e23c2afa13e9e2bec, relation: analyses}
reviewer: Claude (independent review agent; did not author D-089, D-090, review15's fix, the layout files, the datasheets or the P&IDs)
reviewer_kind: agent
branch: asu-d090
merge: pending
---
# Review: layout, sixteenth review (independent) after review15

This is an independent review of branch `asu-d090` at 94ece68. It covers the two commits since
review15 (468ad5a):
- 4beb522, the review15 record and its PROGRESS.md row (no plant file);
- 94ece68, layout/lifting-study.md rewritten by `cheme layout lifting --write` (review15#1),
  with its PROGRESS.md row.

`git diff --stat 468ad5a..94ece68`: PROGRESS.md (+2), layout/lifting-study.md (1 line changed),
reviews/2026-10-24-layout-review15.md (new). The only change to lifting-study.md is the model
fingerprint in its header line: output_sha256 `2c068fe9...` -> `ddd97ca3...`. No lift row, no
radius, load or capacity changed. cheme-as-code is the global `cheme` 0.7.0 (pyDEXPI 2.1.0).

`git diff 468ad5a 94ece68 -- pid/ process/ equipment/ control/ piping/ electrical/` is empty, so
no P&ID, list, datasheet or flowsheet changed. `cheme diff main --list` is as in review15 (no
P&ID item changed). Not drawn: none.

Verdict: **no critical, high or medium finding is open**. Review15#1 is closed. Review15#2,
review14#1, review3#2 and layout#15 stay open, unchanged. No new finding.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|

No new finding.

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-layout-review15#1 | layout/lifting-study.md not current after the 98218e4 model rebuild (fingerprint only) | low | closed 94ece68 | 94ece68 changes only the header line of layout/lifting-study.md: output_sha256 2c068fe9... -> ddd97ca3..., the value of layout/plant-model.yaml. `cheme layout lifting --check` at 94ece68 exits 0 (it exited 1 at 468ad5a). `cheme layout build --check`: "layout/plant-model.yaml is up to date". No lift value moved. |
| 2026-10-24-layout-review15#2 | D-089 bound case 21.1 + 8 + 3 = 32.1 kPa against S3 -> S4 32 kPa (-0.107 kPa) not stated or accepted | low | open | Unchanged at 94ece68: the S3 source in process/flowsheet.yaml still reads "S4 5.6 bara + 32 kPa ... (DN700 lines at their bound 21.1 kPa ...; adsorber bed ~8 and F-2101 ~3 kPa)", and DESIGN.md is not changed since 468ad5a. For the simulation owner on PR #30. |
| 2026-10-24-layout-review14#1 | LV-1114 2 x normal capacity limit and N7 vortex breaker not on the entries the suppliers read | low | open | Unchanged at 94ece68: the LIC-1114 entry in control/instrument-list.yaml names "LV-1114 (fail closed)" only, and C-1101 nozzle N7 (DN150, side) in equipment/datasheets/C-1101.yaml names no vortex breaker; both are still only in the C-1101 `chimney_tray_sif_basis` text. |
| 2026-10-22-layout-review3#2 | PSV tailpipes free above the valves | low | open | Unchanged: the guides wait for the stress analysis (D-050, D-062 (4)). |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | Unchanged; waits for the vendor drawing (D-050 / D-062 (4)). |

## Drawing
`cheme validate` at 94ece68 gives 0 errors and 33 warnings, as in review15:
- 13 instrument-no-interlock;
- 12 template-metadata;
- 6 line-crossing;
- 2 titleblock-sheet.

Counts per sheet: P-01 2 line-crossing (accepted: D-069, D-076), P-02 0, P-03 3 line-crossing
(accepted), P-04 1 line-crossing (accepted); 0 in every other count on every sheet. The
`drawing-clean` gate passes. No P&ID changed, so no tile was read.

## Layout
- `cheme layout build --check`: "layout/plant-model.yaml is up to date". The model is not
  changed since 468ad5a.
- `cheme layout lifting --check`: exit 0, lifting-study.md current (review15#1 closed).

`cheme layout report` at 94ece68, identical to review15:
- **Lines:** 81, all routed except 4 skipped segments (GAN-3002, LN-3002 D-028; two VNT-3004).
  0 unrouted. AIR-1004 133.9 m, AIR-2001 66.8 m, AIR-2002 72.9 m.
- **Chains per method:** astar 26, open 8, pinned 166, rack 15. No `direct` and no
  `rack+direct`.
- **Reasons:** local: above the pipe-way 7, pipe-way 5, pump run at grade 4, rack detour too
  long 1, rack run too short 1, short run 8; open end 8; pinned 166; rack: battery limit at a
  rack end 13, longer than local_max_m 2.
- **Rack fill:**

  | rack | 5 m | 6.5 m | 7 m | 8.5 m | 9 m |
  |---|---:|---:|---:|---:|---:|
  | PR1 | 61 % | | 43 % | | 25 % |
  | PR2 | | 6 % | | 6 % | |
  | PR3 | | 48 % | | 43 % | |

- **Model findings per rule:** clash-*, headroom, access-blocked, steel-in-way, wall-penetration,
  vent-outlet, zone-crossing, separation, escape-*, landing-width, egress-zone, operator-unknown,
  lifting, laydown, pad-overlap, spacing, building-spacing, zone-source 0 each; operability 1
  (XV-3105, accepted); free-span 2 (accepted); support-missing 15 infos (accepted); tier 1
  (WN-1001, accepted D-071 (3)); access-enclosed 1 (accepted); tray-span 17 (accepted);
  tray-zone 6; tray-separation 1 (accepted); nozzle-unconnected 2 infos (D-028).
- **Objects:** 46 equipment items, 61 generated and 166 pinned pipes, 121 in-line items,
  8 platforms, 13 declared and 1 generated structures, 30 zones.

PNGs read (rendered at 94ece68): build/layout-plan.png, build/layout-section-y68.png (along
PR1) and build/layout-section-x133.png (through CB-1 / compander). They show the same routes,
racks, structures, zones, crane pads and laydown areas as in review15.

## Checked and fine
- **Scope of the change:** `git log 468ad5a..HEAD` lists only 4beb522 (review15) and 94ece68
  (lifting study). No plant file other than layout/lifting-study.md changed.
- **review15#1 fix:** done in its own commit with a PROGRESS.md row, as review15 proposed; the
  new fingerprint equals the model's output_sha256.
- **Gates:** `cheme check --no-write` passes 30 gates and fails only `layout-review`, which
  waited for this record (review15 was out of date by layout/lifting-study.md).
- **Stage gates:** no stage sign-off was written, and `checks/status.json` is untouched.
- **Licence rule:** this record gives values in its own words; no third-party content and no
  commercial downstream product is named.

## Not checked
- **D-089 itself** (flowsheet, simulation specs, BFD / PFD content): the review of PR #30.
- **Sizing, TEA and LCA:** not rerun; no input changed since review15, which checked them.
- **The suppliers' pressure drops, I-03 SRS, HAZOP / LOPA, LV-1114 trim, XV-1115 stroke,
  chimney tray levels, N7 vortex breaker:** for the HAZOP team, the valve supplier and the
  packing supplier.
- **TSA top piping, tank nozzles, PR1 walkway for XV-3105, pipe stress, supports and PSV
  tailpipe guides, B1 crane, vent and inert study:** as in review15, with the same owners.
- **Crane selection:** no load chart is given; the lifting contractor chooses the crane against
  the capacity needed in layout/lifting-study.md.
- **P&ID tiles:** none read, since no sheet changed.
