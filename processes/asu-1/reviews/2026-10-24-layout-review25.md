---
topic: layout
reviewed_commit: 02753fc6b9900d41c2883db3a67ae0c192702cbb
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, equipment/equipment-list.yaml, checks/checks.yaml, control/cause-effect.yaml, control/instrument-list.yaml, lca/lca.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 02753fc6b9900d41c2883db3a67ae0c192702cbb, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: 02753fc6b9900d41c2883db3a67ae0c192702cbb, relation: depends-on}
  - {path: DESIGN.md, revision: 02753fc6b9900d41c2883db3a67ae0c192702cbb, relation: depends-on}
  - {path: pid/P-04.xml, revision: 02753fc6b9900d41c2883db3a67ae0c192702cbb, relation: analyses}
  - {path: process/flowsheet.yaml, revision: 02753fc6b9900d41c2883db3a67ae0c192702cbb, relation: analyses}
reviewer: Claude (independent review agent; did not author 02753fc or the layout files)
reviewer_kind: agent
branch: stage/basic-control
merge: pending
---
# Review: layout, twenty-fifth review (independent, confirming) of the junction-box swap

This is a confirming review of commit 02753fc on branch `stage/basic-control`, against 33fcaaa
(the commit review24 reviewed). Between them lie 835968f (control-review5) and 2e9b4f9
(review24 itself); both only add review records. Commit 02753fc:
- swapped PIC-4101 and PIC-4150 between JB-A3-2 and JB-A4-1 in `electrical/electrical-list.yaml`
  (review24 #2);
- rebuilt `layout/plant-model.yaml` and the cable schedule;
- changed only text elsewhere: `control/loops.yaml`, `control/sequences.yaml`,
  `process/narrative.md`, DESIGN.md (D-094, D-096) and PROGRESS.md.

No P&ID changed (P-04 included).

Verdict: **the layout model changes only in the two junction boxes' instrument lists and in the
two instrument cables' destinations, lengths and the cable total, exactly as review24 #2
proposed. IC-PIC-4101 now runs to JB-A3-2 (20 m) and IC-PIC-4150 to JB-A4-1 (40 m), and the total
is back at 6528 m. No point of equipment, pipe, in-line item, platform, structure, zone, tray or
junction box moved, and no route, clash or model finding changed.** review24 #2 is closed.
review24 #1 (AI-3104 / FIC-4148 on P-04) and review23 #2 stay open, unchanged. No new finding.
Nothing blocks the merge.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|

No new finding.

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-layout-review24#1 | The AI-3104 and FIC-4148 bubbles on P-04 are 0.5 mm apart and read as touching (one device in ISA 5.1). | low | open | P-04 is unchanged by 02753fc (`git diff --stat 33fcaaa 02753fc` lists no `pid/` file; `cheme diff 33fcaaa --list`: "No P&ID changed."). `cheme show AI-3104 --sheet pid/P-04.xml` still gives the bubble at 21.25,54.25,34.75,61.75 mm, so the gap to FIC-4148 (35.25..48.75) is still 0.5 mm. The proposed action (`cheme move Inst_AI3104 --offset -2,0`) is still open. |
| 2026-10-24-layout-review24#2 | The junction boxes did not follow the PIC-4101 / PIC-4150 swap, so both cables ran to the far junction box (+39 m). | low | closed 02753fc | `electrical/electrical-list.yaml`: JB-A3-2 now lists [AI-3104, FIC-4148, PIC-4101, AIA-3122, TICA-3124, TV-3124] and JB-A4-1 lists PIC-4150 in place of PIC-4101. In `layout/plant-model.yaml`, IC-PIC-4101 goes from [142.654, 64.304, 9.254] to JB-A3-2 [146.0, 60.0, 1.2]: route 38.204 -> 15.704 m, length 44 -> 20 m. IC-PIC-4150 goes from [162.0, 35.942, 10.562] to JB-A4-1 [166.0, 57.5, 1.2]: route 49.42 -> 34.92 m, length 55 -> 40 m. `cabling.cable_length_m` 6567 -> 6528. These are the values review24 expected. |
| 2026-10-24-layout-review23#2 | The model has no tap point per line-mounted instrument. The S1 cable start at 9.25 m on PR1 cannot be reached, and no rule checks the reach of line-mounted transmitters. | low | open | Unchanged by 02753fc. The cable start points are the same as at 33fcaaa: PIC-4101, FIC-4148 and AI-3104 still share [142.654, 64.304, 9.254] on PR1, and PIC-4150 is still at [162.0, 35.942, 10.562] on GOX-4001 S3. No rule reports it. |

No other finding of an overlapping scope is open. The open findings of control-review1..5 and
hazop-review1/2 are outside this scope: their scopes are control/loops, sequences, philosophy,
narrative, DESIGN.md and safety/hazop, and none of these overlaps this record's scope.

## Drawing
`cheme validate` at 02753fc gives 0 errors and 45 warnings, the same groups as review24:
- 13 instrument-no-interlock;
- 6 line-crossing;
- 12 template-metadata;
- 2 titleblock-sheet;
- 3 process-energy-balance;
- 9 hazop-input-changed.

Counts per sheet (unchanged):
- P-01: 0 line-through-label, 2 line-crossing (accepted: D-069, D-076), 0 label-overlap,
  0 label-far-from-owner;
- P-02: 0 in every count;
- P-03: 3 line-crossing (accepted), 0 otherwise;
- P-04: 1 line-crossing (accepted, GOX-4003 x Inst_UIC4103_ML), 0 otherwise.

`cheme diff 33fcaaa --list`:
```
No P&ID changed.
```
`git diff --stat 33fcaaa 02753fc` lists DESIGN.md, PROGRESS.md, control/loops.yaml,
control/sequences.yaml, electrical/cable-schedule.csv, electrical/cable-schedule.md,
electrical/electrical-list.yaml, layout/plant-model.yaml, process/narrative.md and the two review
records control-review5 and layout-review24. No sheet was rendered for this record: no sheet
changed.

## Layout
- **`layout/plant-model.yaml` diff** (`git diff 33fcaaa 02753fc`, read in full, 30 lines):
  - provenance: only the electrical-list hash (ed31f8a1... -> 740e42a4...) and output_sha256
    (d29e24d66177... -> 5521083ccbe2...) change. `generator_sha256` (edb4fded...) and every other
    source hash are unchanged, so the installed core is the one review24 used;
  - **JB-A3-2** `instruments`: PIC-4150 -> PIC-4101; **JB-A4-1** `instruments`: PIC-4101 ->
    PIC-4150. Their points, areas, rooms and parts are unchanged;
  - **IC-PIC-4101**: refs and `to` JB-A4-1 -> JB-A3-2; to_point [166.0, 57.5, 1.2] ->
    [146.0, 60.0, 1.2]; route 38.204 -> 15.704 m; length 44 -> 20 m; from_point unchanged;
  - **IC-PIC-4150**: refs and `to` JB-A3-2 -> JB-A4-1; to_point [146.0, 60.0, 1.2] ->
    [166.0, 57.5, 1.2]; route 49.42 -> 34.92 m; length 55 -> 40 m; from_point unchanged;
  - `cabling.cable_length_m` 6567 -> 6528. Cables 137, junction boxes 9, trays 44 and tray
    length 870.959 m are unchanged.

  No hunk touches equipment, pipes, in-line items, platforms, structures, zones, trays,
  junction-box points or findings.
- **Cable schedule:**
  - `electrical/cable-schedule.csv` changes only the rows IC-PIC-4101 (JB-A4-1, 38.2/44 ->
    JB-A3-2, 15.7/20) and IC-PIC-4150 (JB-A3-2, 49.4/55 -> JB-A4-1, 34.9/40);
  - `cable-schedule.md` changes the same two rows. Its header names model output 5521083ccbe2,
    which matches output_sha256;
  - the summary row "instrument 1 pr x 1.5 mm2" goes from 86 cables / 2626 m back to
    86 / 2587 m (-39 m = -24 - 15). No other row changes.
- **`cheme layout build --check`:** "layout/plant-model.yaml is up to date".
- **`cheme layout report` at 02753fc** (identical to review24):
  - **Lines:** 81, all routed except 4 skipped segments (GAN-3002, LN-3002, D-028; two
    VNT-3004), 0 unrouted. GOX-4001 has 4 segments, 102.4 m, all pinned.
  - **Chains per method:** astar 26, open 8, pinned 166, rack 15.
  - **Reasons:** local 26 (above the pipe-way 7, pipe-way 5, pump run at grade 4, rack detour
    1, rack run too short 1, short run 8), open end 8, pinned 166, rack 15 (battery limit at a
    rack end 13, longer than local_max_m 2).
  - **Rack fill:** PR1 61 / 43 / 25 %, PR2 6 / 6 %, PR3 48 / 43 %.
  - **Model findings per rule:** access-enclosed 1, free-span 2, laydown 1, lifting 4,
    nozzle-unconnected 2, operability 1, support-missing 15, tier 1, tray-separation 1,
    tray-span 17, tray-zone 6, plus 15 nozzle-defaulted infos. These are the same items, and the
    same acceptances in checks/checks.yaml, as in review19..24. There are 0 clash, headroom,
    access-blocked, wall-penetration, vent-outlet and escape findings, and no
    `layout-pipe-disconnected`.
  - **Objects:** 46 equipment items, 61 generated and 166 pinned pipes, 121 in-line items,
    8 platforms, 14 declared and 1 generated structures, 30 zones.
- **PNGs read (rendered at 02753fc):**
  - build/layout-plan.png (plot plan): the same site, areas, roads, racks, zones, pads and
    laydowns as review24;
  - build/layout-section-y68.png (along PR1): tiers and routes as in review24;
  - build/layout-section-x133.png (through CB-1 and the compander): CB-1 steel, stairs and
    platforms as in review24;
  - build/layout-plan_crop-135-30-175-70.png (scale 1:100, the GOX suction and both junction
    boxes): JB-A3-2 at (146, 60) and JB-A4-1 at (166, 57.5) stand where they did, with their
    trays IT-JB-A3-2 / IT-JB-A4-1 unchanged. The instrument field cables have no trays
    (`trays: []`) and are not drawn, so the plan cannot show the swap; the model diff above is
    the evidence.

  The plan and the sections are unchanged against 33fcaaa: the only geometry-bearing change in
  the model is two cable end points, and cables without trays are not drawn.

## Checked and fine
- **Stage gates:** `cheme check` before this record: every gate passes except layout-review.
  That gate fails only because review24/23/22 (and older) are stale on
  electrical/electrical-list.yaml and layout/plant-model.yaml (and review23 and older also on
  control/instrument-list.yaml); this record replaces them. layout-3d, layout-rules,
  lifting-study, electrical and drawing-clean pass. No sign-off was written, and
  checks/status.json is untouched.
- **Junction-box fit:** JB-A3-2's note ("product analysers and GOX flow east of the cold box")
  now matches its members: PIC-4101 sits with FT-4148 and AT-3104 at the S1 tap. JB-A4-1 ("GOX
  and GAN compressors") now takes PIC-4150 at the S3 tap by K-4101. JB-A3-2 still has 6
  members and JB-A4-1 has 26 expanded members, as before, so no capacity changed.
- **DESIGN.md D-096** now says "PIC-4101 on JB-A3-2 with FIC-4148, PIC-4150 on JB-A4-1", which
  agrees with the electrical list and the model.
- **Zones (layout/zones.yaml, unchanged):** D-096 now records as open that a turndown vent
  through PV-4101B makes VNT-4003 a normal-operation O2 release, for the zones owner (D-031).
  VNT-4003 ends at S-4102, which is already a `primary` oxygen source of Z-O2-V1 ("expected in
  normal operation from time to time"). That grade covers an occasional turndown vent. Only its
  comment ("suction vent on trip / start-up") is now incomplete. Should the set-point window
  (control-review5 #1) make the vent run for long periods at turndown, the grade becomes
  `continuous`, and the zone has to be rechecked then. This is not a finding of this record:
  the D-096 open point and the D-031 vent study cover it.
- **Generated outputs:** `layout build --check` is current, and the cable schedule names the
  current model output.

## Not checked
- **The control content of 02753fc** (the PIC-4101 set-point window, the loops, sequences and
  narrative texts, the H-04 hand-over) belongs to the control and HAZOP reviews.
- **The 9 `hazop-input-changed` warnings** and the 3 `process-energy-balance` warnings: outside
  this layout scope, for the HAZOP and process owners.
- **P-04** was not rendered or read again: it did not change. review24's crops still apply.
- Everything review19 lists under "Not checked" (relief sizing, pipe stress and lugs, the CB-1X
  envelope, the S3 -> S4 allowance) stays open as D-091 O1 .. O6.
