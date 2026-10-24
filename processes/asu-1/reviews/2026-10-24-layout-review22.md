---
topic: layout
reviewed_commit: 30d4cf9fd385de658396881b87248e737edc0180
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, equipment/equipment-list.yaml, checks/checks.yaml, control/cause-effect.yaml, control/instrument-list.yaml, lca/lca.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 30d4cf9fd385de658396881b87248e737edc0180, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: 30d4cf9fd385de658396881b87248e737edc0180, relation: depends-on}
  - {path: DESIGN.md, revision: 30d4cf9fd385de658396881b87248e737edc0180, relation: depends-on}
  - {path: pid/P-04.xml, revision: 30d4cf9fd385de658396881b87248e737edc0180, relation: analyses}
  - {path: process/flowsheet.yaml, revision: 30d4cf9fd385de658396881b87248e737edc0180, relation: analyses}
reviewer: Claude (independent review agent; did not author 30d4cf9 or the layout files)
reviewer_kind: agent
branch: stage/basic-control
merge: pending
---
# Review: layout, twenty-second review (independent, confirming) of the D-095 retag

This is a confirming review of commit 30d4cf9 on branch `stage/basic-control`. Its parent is
302b42e. Commit 30d4cf9 (DESIGN.md D-095) retagged three items on P-04 with `cheme rename`:
- FI-4148 -> FIC-4148;
- FIC-4105 -> PIC-4105;
- FV-4105 -> PV-4105.

The instrument list, the electrical list, the `operators:` entry in piping/routing.yaml and the
flowsheet links were changed to match. The BFD, the PFD, the layout model, the cable schedule
and the LCA fingerprints were rebuilt. review21 (f5dad54, which is in HEAD's history) is stale
only because `control/instrument-list.yaml`, `electrical/electrical-list.yaml`,
`layout/plant-model.yaml` and `piping/routing.yaml` changed (`cheme check`, gate
layout-review).

Verdict: **apart from the three retags and the new operator basis text of PV-4105, the layout
model is unchanged. No geometry, route, clash, finding, junction box or cable length moved, and
no layout finding is added.**

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|

No new finding.

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|

None open. review21 had no finding and listed none open in this scope. The open findings of
control-review1/2 and hazop-review1/2 are outside this scope: their scopes are control/loops,
sequences, philosophy and narrative, DESIGN.md, and safety/hazop, and none of these overlaps
this record's scope.

## Drawing
`cheme validate` at 30d4cf9 gives 0 errors and 45 warnings:
- 13 instrument-no-interlock;
- 6 line-crossing;
- 12 template-metadata;
- 2 titleblock-sheet;
- 3 process-energy-balance;
- 9 hazop-input-changed.

The first five groups add up to the same 36 warnings as review21. The 9 new
`hazop-input-changed` warnings come from H-01..H-04, whose analysed inputs
(control/instrument-list.yaml, process/flowsheet.yaml and, for H-04, pid/P-04.xml) changed in
30d4cf9. They belong to the HAZOP owner (re-stamp after reassessment) and not to this layout
scope. Validate gives no warning on any of the three new tags. Counts per sheet:
- P-01: 0 line-through-label, 2 line-crossing (accepted: D-069, D-076), 0 label-overlap,
  0 label-far-from-owner;
- P-02: 0 in every count;
- P-03: 3 line-crossing (accepted), 0 otherwise;
- P-04: 1 line-crossing (accepted, GOX-4003 x Inst_UIC4103_ML), 0 otherwise.

P-04 bubbles, read in crops (P-04 itself is outside this scope; only the retagged labels were
read, not the whole sheet in tiles):
- build/P-04_crop-140-95-180-122.png (scale 14): the bubble reads **PIC 4105**. Its measuring
  line goes to the sensor on GAN-4002 S3, and its dashed signal goes to the actuator of the globe
  valve labelled **PV-4105** (GAN-4002, DN 150).
- build/P-04_crop-25-45-60-70.png (scale 14): the bubble reads **FIC 4148**, beside AI 3104.
- No FI-4148, FIC-4105 or FV-4105 label remains on the sheet: `cheme diff` shows them removed,
  and validate's tags-in-texts cross-check gives no warning.

## Layout
- **`cheme diff 302b42e --list`** (the parent of 30d4cf9):
  ```
  pid/P-04.xml:
  removed GlobeValve FV4105 [FV-4105]: 0 added, 15 removed, 0 modified
  removed ProcessInstrumentationFunction Inst_FI4148 [4148]: 0 added, 21 removed, 0 modified
  removed ProcessInstrumentationFunction Inst_FIC4105 [4105]: 0 added, 23 removed, 0 modified
  added ProcessInstrumentationFunction Inst_FIC4148 [4148]: 21 added, 0 removed, 0 modified
  added ProcessInstrumentationFunction Inst_PIC4105 [4105]: 23 added, 0 removed, 0 modified
  added GlobeValve PV4105 [PV-4105]: 15 added, 0 removed, 0 modified
  changed PipingNetworkSystem Line_GAN4002 [GAN-4002]: 0 added, 0 removed, 4 modified
  process/BFD.xml:
  modified Stream S7 [S7]: 0 added, 0 removed, 1 modified
  modified Stream S9B [S9B]: 0 added, 0 removed, 1 modified
  modified Note cheme_provenance: 0 added, 0 removed, 1 modified
  process/PFD.xml:
  (the same three as the BFD)
  ```
  Each removed item is matched by an added item with the same object counts: 15, 21 and 23. The
  4 modifications to GAN-4002 are its pipes' references to the renamed valve id. The BFD and PFD
  changes are the S7 and S9B link texts (`instrument FIC-4148`, `instrument PIC-4105`) and the
  provenance note.
- **`layout/plant-model.yaml` diff, checked mechanically.** I loaded the model at 302b42e and at
  30d4cf9 and replaced the old tags and ids (FI-4148/FI4148, FIC-4105/FIC4105, FV-4105/FV4105)
  with the new ones in the old model. Then I compared both models object by object (keyed by
  `id`, ignoring list order) and left out `provenance`. The script is
  `cmp_model.py` in the review agent's scratchpad, run with `cheme run`. The only difference is
  `inline[P-04/PV4105].operator.basis`: 'GAN product flow control valve, actuated (D-040)' ->
  'GAN export pressure control valve, actuated (D-040, D-095)'. This follows the routing.yaml
  operator entry, and the operator kind is still `remote_operator`. In detail:
  - PV-4105 keeps the old FV-4105 point [169.4, 58.589, 3.584], its direction, segment
    Line_GAN4002_S3 and every part;
  - JB-A3-2 lists FIC-4148 in place of FI-4148, and JB-A4-1 lists PIC-4105 and PV-4105 in
    place of FIC-4105 and FV-4105. The instrument counts and junction box points are unchanged;
  - cable IC-FIC-4148 = old IC-FI-4148 (15.704 m route, 20 m), IC-PIC-4105 = old IC-FIC-4105
    (6.609 m, 10 m) and IC-PV-4105 = old IC-FV-4105 (6.873 m, 11 m), with the same end points,
    sizes and trays. electrical/cable-schedule.csv matches.

  In `provenance`, besides the changed source and output hashes, `generator_sha256` moved from
  d1f862cf... to edb4fded..., and the BFD/PFD header from ac1b86de... to 1e5e0c8a.... So the
  installed core has moved since review21. Because content is identical apart from the renames,
  this is fingerprint-only (cf. core#132), and `layout build --check` passes under the installed
  core.
- **Leftover old tags:** no file in this scope (layout/, piping/, electrical/, equipment/,
  checks/, P-01..P-03, the C&E) names FI-4148, FIC-4105 or FV-4105. The instrument list keeps
  them only in "Was ..." history notes. The hand-maintained sheet's provenance script
  scripts/draft_P-04.py still uses the old tags, but it is never rerun (P-04 has no `generator`
  in plant.yaml).
- **`cheme layout build --check`:** "layout/plant-model.yaml is up to date".
- **`cheme layout report` at 30d4cf9** (identical to review21):
  - **Lines:** 81, all routed except 4 skipped segments (GAN-3002, LN-3002, D-028; two
    VNT-3004), 0 unrouted. GAN-4002 has 6 segments, 30.7 m, all pinned.
  - **Chains per method:** astar 26, open 8, pinned 166, rack 15. No `direct` and no
    `rack+direct`.
  - **Reasons:** local 26 (above the pipe-way 7, pipe-way 5, pump run at grade 4, rack detour
    1, rack run too short 1, short run 8), open end 8, pinned 166, rack 15 (battery limit at a
    rack end 13, longer than local_max_m 2).
  - **Rack fill:** PR1 61 / 43 / 25 %, PR2 6 / 6 %, PR3 48 / 43 %.
  - **Model findings per rule:** access-enclosed 1, free-span 2, laydown 1, lifting 4,
    nozzle-unconnected 2, operability 1, support-missing 15, tier 1, tray-separation 1,
    tray-span 17, tray-zone 6, plus 15 nozzle-defaulted infos. These are the same items and
    acceptances in checks/checks.yaml as review19..21. There are 0 clash, headroom,
    access-blocked, wall-penetration, vent-outlet and escape findings, and no
    `layout-pipe-disconnected`.
  - **Objects:** 46 equipment items, 61 generated and 166 pinned pipes, 121 in-line items,
    8 platforms, 14 declared and 1 generated structures, 30 zones.
- **PNGs read (rendered at 30d4cf9):**
  - build/layout-plan.png (plot plan): the same site, areas, roads, racks, zones, pads and
    laydowns as review21;
  - build/layout-plan_crop-160-50-180-68.png: PV-4105 sits on the GAN-4002 riser north of
    E-4103 at about (169.4, 58.6), between the other GAN-4002 in-line items, in its old place
    (inside the same hatched A4 zone circles as FV-4105 before; no zone changed);
  - build/layout-section-y68.png (along PR1): tiers and routes as in review21;
  - build/layout-section-x133.png (through CB-1 and the compander): CB-1 steel, stairs and
    platforms as in review21;
  - build/layout-section-x169.4_crop-50-0-68-12.png (along GAN-4002 at PV-4105, looking west):
    GAN-4002 runs level at about 3.6 m from the E-4103 nozzle to the riser. There is no clash
    with the steel or with CW-4002 below;
  - build/layout-section-y58.6_crop-150-0-190-15.png (across GAN-4002 at PV-4105, looking
    north): the GAN-4002 riser at x 169.4 is clear of the PR1 frame and the stair tower.

  PV-4105 is at 3.58 m with a remote operator (D-040). Nothing about its access changed, and no
  `layout-operability` finding names it.

## Checked and fine
- **Stage gates:** `cheme check` before this record: every gate passes except layout-review,
  which fails only because review21/20/19 are stale on the four files above (this record
  replaces them). No sign-off was written, and checks/status.json is untouched.
- **Generated outputs:** `layout build --check` is current. Validate's generator comparison
  gives no `generated-sheet-drift` or `generated-version` warning for the BFD and PFD.
- **Electrical:** the JB-A4-1 instrument count is unchanged (two swapped for two), and the
  electrical gate passes.

## Not checked
- **The 9 `hazop-input-changed` warnings** (H-01..H-04 re-stamp after reassessing D-095) and
  the 3 `process-energy-balance` warnings: outside this layout scope, for the HAZOP and process
  owners.
- **The control content of D-095:** loops.yaml, philosophy, narrative, the FIC-4148 / PIC-4101
  low select on the K-4101 guide vanes, the PV-4105 fail position, and whether PT-4105 sits
  upstream or downstream of PV-4105 (open points in loops.yaml). These belong to the control
  review. On P-04 only the three retagged labels were read; the rest of the sheet was not read
  in tiles.
- Everything review19 lists under "Not checked" (relief sizing, pipe stress and lugs, the CB-1X
  envelope, the S3 -> S4 allowance) stays open as D-091 O1 .. O6.
