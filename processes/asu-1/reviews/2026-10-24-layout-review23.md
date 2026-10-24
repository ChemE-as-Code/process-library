---
topic: layout
reviewed_commit: e6f59b82d912d0f6538829429b0206a3277f671e
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, equipment/equipment-list.yaml, checks/checks.yaml, control/cause-effect.yaml, control/instrument-list.yaml, lca/lca.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: e6f59b82d912d0f6538829429b0206a3277f671e, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: e6f59b82d912d0f6538829429b0206a3277f671e, relation: depends-on}
  - {path: DESIGN.md, revision: e6f59b82d912d0f6538829429b0206a3277f671e, relation: depends-on}
  - {path: pid/P-04.xml, revision: e6f59b82d912d0f6538829429b0206a3277f671e, relation: analyses}
  - {path: process/flowsheet.yaml, revision: e6f59b82d912d0f6538829429b0206a3277f671e, relation: analyses}
reviewer: Claude (independent review agent; did not author e6f59b8 or the layout files)
reviewer_kind: agent
branch: stage/basic-control
merge: pending
---
# Review: layout, twenty-third review (independent, confirming) of the D-096 instrument PIC-4150

This is a confirming review of commit e6f59b8 on branch `stage/basic-control`, against 30d4cf9
(the commit review22 reviewed). Between them lies 04515c4 (review22 itself) and db47267
(control-review3), neither of which touches this scope. Commit e6f59b8 (DESIGN.md D-096):
- added the instrument function PIC-4150 on P-04. It was copied from PIC-4101 with `cheme
  copy`, placed below GOX-4001 beside FIC-4148, with its measuring line to its own tap on
  GOX-4001 S1 and the copied signal lines removed;
- added PIC-4150 to the instrument list and to junction box JB-A3-2 in the electrical list, and
  rewrote the notes of PIC-4101, PIC-4102, FIC-4148, FIC-3107 and PIC-4105;
- rebuilt `layout/plant-model.yaml` and the cable schedule.

Verdict: **apart from PIC-4150 on JB-A3-2, its cable IC-PIC-4150 and the counts that follow
from them, the layout model is unchanged. No point, route, clash, model finding, tray or
junction box point moved.** Two low findings: the new bubble touches FIC-4148's on P-04, and
the model puts the new transmitter on the PR1 9 m tier where nobody can reach it (as
it already does for FIC-4148 and AI-3104). Nothing blocks the merge.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-layout-review23#1 | P-04 | PIC-4150 | The new bubble (48.75..62.25 mm) touches FIC-4148's (35.25..48.75 mm) edge to edge, and that bubble already touches AI-3104's. In ISA 5.1, bubbles that touch mean one device with several functions, but PIC-4150 has its own transmitter PT-4150 (D-096). The lint does not see this (label-overlap 0). Evidence: build/P-04_crop-30-38-75-66.png (before: build/P-04@30d4cf9_crop-30-38-75-66.png). | low | open | Leave a gap of at least 2 mm between the three bubbles (`cheme move Inst_PIC4150 --offset 3,0`; there is about 2.75 mm free before the GOX-4003 riser at about 65 mm, so AI-3104 / FIC-4148 may have to move left too). |
| 2026-10-24-layout-review23#2 | (layout model) | PIC-4150 | The model has no position for a line-mounted instrument's tap. The cable IC-PIC-4150 starts at [142.654, 64.304, 9.254], the same point as IC-FIC-4148 and IC-AI-3104. That point is on GOX-4001 S1 where the line runs on top of PR1 at 9.25 m. build/layout-section-x142.65_crop-55-0-72-14.png shows nothing to stand on there. No rule checks whether a line-mounted transmitter can be reached (`layout-operability` covers valves and nozzle instruments with `operators:`), and `cheme show PIC-4150 --layout` says it is not on the plot plan. This is not new with PIC-4150 (FIC-4148 and AI-3104 have the same point), but this change adds a third transmitter there. | low | open | State where PT-4150 (and FT-4148, AI-3104's sample point) are tapped and how they are reached: a tap on the GOX-4001 riser near grade, or a remote mount with impulse lines to a stand, as D-040 does for the nozzle instruments. Report the missing rule (reach of line-mounted instruments, and a tap point per instrument instead of one per segment) to cheme-as-code. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|

None open. review22 had no finding and listed none open in this scope. The open findings of
control-review1/2/3 and hazop-review1/2 are outside this scope: their scopes are control/loops,
sequences, philosophy and narrative, DESIGN.md, and safety/hazop, and none of these overlaps
this record's scope.

## Drawing
`cheme validate` at e6f59b8 gives 0 errors and 45 warnings, the same groups as review22:
- 13 instrument-no-interlock;
- 6 line-crossing;
- 12 template-metadata;
- 2 titleblock-sheet;
- 3 process-energy-balance;
- 9 hazop-input-changed.

The 9 `hazop-input-changed` warnings still name the hashes from before 30d4cf9 (H-01..H-04 not
re-stamped). They are for the HAZOP owner. Validate gives no warning on PIC-4150, and the
instruments-list-vs-P&ID cross-check finds the new tag on both sides. Counts per sheet:
- P-01: 0 line-through-label, 2 line-crossing (accepted: D-069, D-076), 0 label-overlap,
  0 label-far-from-owner;
- P-02: 0 in every count;
- P-03: 3 line-crossing (accepted), 0 otherwise;
- P-04: 1 line-crossing (accepted, GOX-4003 x Inst_UIC4103_ML), 0 otherwise. PIC-4150 adds no
  drawing finding.

P-04 around PIC-4150 (P-04 itself is outside this scope; only this region was read, not the
whole sheet in tiles):
- build/P-04_crop-30-38-75-66.png (scale 10):
  - the bubble reads **PIC 4150**;
  - its green measuring line runs straight up to its own point on GOX-4001, east of
    FIC-4148's tap, and crosses no line or label;
  - the label "GOX-4001 DN 500" is clear of it;
  - none of the copied signal lines are left;
  - the bubble touches FIC-4148's (finding #1).
- build/P-04@30d4cf9_crop-30-38-75-66.png: the before picture. Only the new bubble and its
  measuring line differ.
- build/P-04_crop-15-20-135-90.png and build/P-04_crop-45-22-110-50.png (context): see
  "Not checked" for the PIC-4101 signal still drawn into K-4101.

## Layout
- **`cheme diff 30d4cf9 --list`**:
  ```
  pid/P-04.xml:
  added ProcessInstrumentationFunction Inst_PIC4150 [4150]: 21 added, 0 removed, 0 modified
  changed PipingNetworkSystem Line_GOX4001 [GOX-4001]: 1 added, 0 removed, 0 modified
  ```
  The 21 objects are the same count as FIC-4148's function. The one object added to GOX-4001
  is the new sensing location on S1. The P-04 git diff has 285 insertions and no deletions. The
  BFD and PFD do not change.
- **`layout/plant-model.yaml` diff** (git diff 30d4cf9..e6f59b8, read in full, 38 lines):
  - provenance: the source hashes of the instrument list, the electrical list and P-04, and
    output_sha256. `generator_sha256` is unchanged (edb4fded...), so the installed core is the
    one review22 used;
  - `junction_boxes[JB-A3-2].instruments` gains PIC-4150 (6 instruments, capacity 24). The
    point [146.0, 60.0, 1.2] is unchanged;
  - a new cable **IC-PIC-4150**: PIC-4150 -> JB-A3-2, 1 pr x 1.5 mm2, 12 mm OD, no trays,
    route 15.704 m, length 20 m. Its ends are the same as IC-FIC-4148's (finding #2);
  - the basis text of the home run **MC-JB-A3-2** changes from "5 pairs in use" to "6 pairs in
    use". Its size, trays (IT-CR-1, IT-PR1-1..6, IT-JB-A3-2), route 145.6 m and length 156 m
    are unchanged;
  - `cabling`: cables 136 -> 137, instrument 125 -> 126, instruments 116 -> 117, cable
    length 6508 -> 6528 m. Trays 44, tray length 870.959 m, junction boxes 9 and power 11
    are unchanged.

  No hunk touches equipment, pipes, in-line items, platforms, structures, zones, trays or
  findings.
- **Cable schedule:**
  - `electrical/cable-schedule.csv` gains one row, IC-PIC-4150 (JB-A3-2, 1 pr x 1.5 mm2,
    15.7 m route, 20 m). It is identical in form to IC-FIC-4148.
  - `cable-schedule.md` gains the same row, and its header names the new model output
    b8f54c1769dd, which matches output_sha256.
  - The summary row "instrument 1 pr x 1.5 mm2" goes from 85 cables / 2567 m to 86 / 2587 m,
    exactly +1 cable and +20 m. No other row changes.
- **`cheme layout build --check`:** "layout/plant-model.yaml is up to date".
- **`cheme layout report` at e6f59b8** (identical to review22):
  - **Lines:** 81, all routed except 4 skipped segments (GAN-3002, LN-3002, D-028; two
    VNT-3004), 0 unrouted. GOX-4001 has 4 segments, 102.4 m, all pinned.
  - **Chains per method:** astar 26, open 8, pinned 166, rack 15. No `direct` and no
    `rack+direct`.
  - **Reasons:** local 26 (above the pipe-way 7, pipe-way 5, pump run at grade 4, rack detour
    1, rack run too short 1, short run 8), open end 8, pinned 166, rack 15 (battery limit at a
    rack end 13, longer than local_max_m 2).
  - **Rack fill:** PR1 61 / 43 / 25 %, PR2 6 / 6 %, PR3 48 / 43 %.
  - **Model findings per rule:** access-enclosed 1, free-span 2, laydown 1, lifting 4,
    nozzle-unconnected 2, operability 1, support-missing 15, tier 1, tray-separation 1,
    tray-span 17, tray-zone 6, plus 15 nozzle-defaulted infos. These are the same items, and
    the same acceptances in checks/checks.yaml, as in review19..22. There are 0 clash,
    headroom, access-blocked, wall-penetration, vent-outlet and escape findings, and no
    `layout-pipe-disconnected`.
  - **Objects:** 46 equipment items, 61 generated and 166 pinned pipes, 121 in-line items,
    8 platforms, 14 declared and 1 generated structures, 30 zones.
- **PNGs read (rendered at e6f59b8):**
  - build/layout-plan.png (plot plan): the same site, areas, roads, racks, zones, pads and
    laydowns as review22;
  - build/layout-plan_crop-130-55-160-72.png (PR1 / PR2 east of the cold box, JB-A3-2 at
    (146, 60)): GOX-4001 S1 runs along PR1 at y 64.3 from x 134.1 to 155.2, and JB-A3-2 sits
    south of it. No new object is drawn: the model has no instrument symbol, only the cable
    end;
  - build/layout-section-y68.png (along PR1): tiers and routes as in review22;
  - build/layout-section-x133.png (through CB-1 and the compander): CB-1 steel, stairs and
    platforms as in review22;
  - build/layout-section-x142.65_crop-55-0-72-14.png (across PR1 at the PIC-4150 cable end,
    looking west): GOX-4001 (DN 500) is at y 64.3, z 9.25 on the PR1 9 m tier. There is no
    platform or walkway within reach (finding #2).

## Checked and fine
- **Stage gates:** `cheme check` before this record: every gate passes except layout-review.
  That gate fails only because review22/21/20 (and older) are stale on
  control/instrument-list.yaml, electrical/electrical-list.yaml and layout/plant-model.yaml;
  this record replaces them. The electrical gate (a cable to every instrument, fill and
  separation) passes with the new cable. No sign-off was written, and checks/status.json is
  untouched.
- **Lists:** PIC-4150 is in the instrument list (sheet P-04) and on JB-A3-2. JB-A3-2 has 6 of
  24 places used.
- **Generated outputs:** `layout build --check` is current, and the cable schedule names the
  current model output.

## Not checked
- **Outside this scope, for the control review:** on P-04, PIC-4101's dashed signal line still
  runs from PV-4101B's actuator, through the PIC-4101 bubble, and into the K-4101 casing at the
  inlet guide vanes (build/P-04_crop-45-22-110-50.png). D-096 says PIC-4101 now acts on
  PV-4101B only and the vanes belong to PIC-4102's low select. The drawn output to the vanes
  still shows the D-019 split range. Its notes in the instrument list say the vane output is
  PIC-4150's, but nothing on the sheet says so. This is unchanged by e6f59b8 and is control
  and P&ID content, so it is not a finding of this record.
- **The control content of D-096:** loops, sequences, philosophy, narrative, the low select,
  the cascade PIC-4105 -> FIC-3107, the fail positions and the open points in D-096. These
  belong to the control review.
- **The 9 `hazop-input-changed` warnings** (H-01..H-04 to be re-stamped after reassessment)
  and the 3 `process-energy-balance` warnings: outside this layout scope, for the HAZOP and
  process owners.
- **P-04** was not read in tiles. Only the PIC-4150 and PIC-4101 regions were read.
- Everything review19 lists under "Not checked" (relief sizing, pipe stress and lugs, the CB-1X
  envelope, the S3 -> S4 allowance) stays open as D-091 O1 .. O6.
