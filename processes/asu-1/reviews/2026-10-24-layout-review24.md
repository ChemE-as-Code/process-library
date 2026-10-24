---
topic: layout
reviewed_commit: 33fcaaa73307e73423811facfcfdc5d24ccfbad8
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, equipment/equipment-list.yaml, checks/checks.yaml, control/cause-effect.yaml, control/instrument-list.yaml, lca/lca.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 33fcaaa73307e73423811facfcfdc5d24ccfbad8, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: 33fcaaa73307e73423811facfcfdc5d24ccfbad8, relation: depends-on}
  - {path: DESIGN.md, revision: 33fcaaa73307e73423811facfcfdc5d24ccfbad8, relation: depends-on}
  - {path: pid/P-04.xml, revision: 33fcaaa73307e73423811facfcfdc5d24ccfbad8, relation: analyses}
  - {path: process/flowsheet.yaml, revision: 33fcaaa73307e73423811facfcfdc5d24ccfbad8, relation: analyses}
reviewer: Claude (independent review agent; did not author 33fcaaa or the layout files)
reviewer_kind: agent
branch: stage/basic-control
merge: pending
---
# Review: layout, twenty-fourth review (independent, confirming) of the D-096 PIC-4101 / PIC-4150 swap

This is a confirming review of commit 33fcaaa on branch `stage/basic-control`, against e6f59b8
(the commit review23 reviewed). Between them lie 4bc8e84 (control-review4) and 5918329
(review23 itself), neither of which touches this scope. Commit 33fcaaa (DESIGN.md D-096):
- swapped the tags of the two pressure controllers on P-04 with `cheme rename`. The bubble above
  GOX-4001 (tap on S3, between XV-4117 and K-4101) is now PIC-4150. The bubble below (tap on S1,
  upstream of XV-4117) is now PIC-4101;
- removed the upper bubble's signal line to PV-4101B and kept its signal to the K-4101 guide
  vanes;
- moved the lower bubble clear of FIC-4148 (`cheme move`) and realigned its tap;
- changed the note at PIC-4102 to "K-4101 IGV master (D-096); HH trips K-4101";
- rewrote the instrument-list notes of PIC-4101 and PIC-4150;
- rebuilt `layout/plant-model.yaml` and the cable schedule.

Verdict: **the layout model changes only in the two instrument cables' start points, which
are swapped, and in the lengths and totals that follow from them. No point of equipment, pipe,
in-line item, platform, structure, zone, tray or junction box moved, and no route, clash or model
finding changed.** review23 #1 is closed for the bubble it was about. Its remaining part (AI-3104
touching FIC-4148) is carried as new finding #1. review23 #2 stays open. One new low finding
(#2): the junction-box assignments were not swapped with the tags, so both cables now run to the
far junction box (+39 m). Nothing blocks the merge.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-layout-review24#1 | P-04 | AI-3104, FIC-4148 | This is the part of review23 #1 that 33fcaaa did not fix. AI-3104's bubble (21.25..34.75 mm) and FIC-4148's (35.25..48.75 mm, both at y 54.25..61.75) are 0.5 mm apart, so at line width they read as touching (build/P-04_crop-15-20-110-75.png, build/P-04_crop-30-44-72-74.png). In ISA 5.1, touching bubbles mean one device with several functions, but AT-3104 and FT-4148 are separate devices. The lint does not see this (label-overlap 0). This was there before e6f59b8. | low | open | Move AI-3104 left by at least 1.5 mm (`cheme move Inst_AI3104 --offset -2,0`) so that the gap is at least 2 mm, and check its tap and the "03 E-3101" off-page text on the left. |
| 2026-10-24-layout-review24#2 | (layout model) | PIC-4101, PIC-4150 | `electrical/electrical-list.yaml` was not changed by the swap. JB-A3-2 (146, 60) still lists PIC-4150, and JB-A4-1 (166, 57.5) still lists PIC-4101. The cable start points moved with the tags: IC-PIC-4101 now starts at the S1 tap [142.654, 64.304, 9.254] and runs to JB-A4-1 (route 34.9 -> 38.2 m, length 40 -> 44 m). IC-PIC-4150 now starts at the S3 tap [162.0, 35.942, 10.562] and runs to JB-A3-2 (route 15.7 -> 49.4 m, length 20 -> 55 m). The cable total rises from 6528 to 6567 m. Each transmitter is now wired to the far junction box. JB-A3-2's note ("product analysers and GOX flow east of the cold box") fits the S1 tap with FT-4148 and AT-3104, not the S3 tap at the machine. | low | open | Swap the two tags between JB-A3-2 and JB-A4-1 in the electrical list, then rebuild the model and the cable schedule. The lengths should return to 20 m and 40 m, and the total to 6528 m. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-layout-review23#1 | The new lower bubble (then PIC-4150) touched FIC-4148's bubble on P-04. | low | closed 33fcaaa | The lower bubble, now PIC-4101 (`cheme show PIC-4101`: 50.25..63.75 x 62.25..69.75 mm), sits 1.5 mm right of and 0.5 mm below FIC-4148 (35.25..48.75 x 54.25..61.75), so they no longer touch. It is 1.25 mm clear of the GOX-4003 riser at about 65 mm. Its measuring line runs straight from its own S1 tap (57.0, 45.0) to its top node (57.0, 62.25) and crosses nothing. Crops: build/P-04_crop-30-44-72-74.png and build/P-04_crop-15-20-110-75.png; before: build/P-04@e6f59b8_crop-15-20-110-75.png. The AI-3104 / FIC-4148 contact named in the same finding is not fixed. It is split off as 2026-10-24-layout-review24#1. |
| 2026-10-24-layout-review23#2 | The model has no tap point per line-mounted instrument. The S1 cable start at 9.25 m on PR1 cannot be reached, and no rule checks the reach of line-mounted transmitters. | low | open | The issue is unchanged by 33fcaaa, which moves the S1 point from PIC-4150 to PIC-4101. Three transmitters still share [142.654, 64.304, 9.254] on PR1 (PIC-4101, FIC-4148, AI-3104). PIC-4150 now has the old PIC-4101 point [162.0, 35.942, 10.562], on GOX-4001 S3. build/layout-section-x162_crop-28-0-44-14.png shows that line running at about 10.6 m above the K-4101 area with no platform or walkway under it. `cheme show PIC-4150 --layout`: "not on the plot plan". No rule reports this. |

No other finding of an overlapping scope is open. The open findings of control-review1..4 and
hazop-review1/2 are outside this scope: their scopes are control/loops, sequences, philosophy,
narrative, DESIGN.md and safety/hazop, and none of these overlaps this record's scope.

## Drawing
`cheme validate` at 33fcaaa gives 0 errors and 45 warnings, the same groups as review23:
- 13 instrument-no-interlock;
- 6 line-crossing;
- 12 template-metadata;
- 2 titleblock-sheet;
- 3 process-energy-balance;
- 9 hazop-input-changed.

The swap adds no warning. The instruments-list-vs-P&ID cross-check finds both tags on both
sides. Counts per sheet:
- P-01: 0 line-through-label, 2 line-crossing (accepted: D-069, D-076), 0 label-overlap,
  0 label-far-from-owner;
- P-02: 0 in every count;
- P-03: 3 line-crossing (accepted), 0 otherwise;
- P-04: 1 line-crossing (accepted, GOX-4003 x Inst_UIC4103_ML), 0 otherwise.

`cheme diff e6f59b8 --list`:
```
pid/P-04.xml:
changed ProcessInstrumentationFunction Inst_PIC4101 [PIC-4101]: 0 added, 4 removed, 9 modified
changed ProcessInstrumentationFunction Inst_PIC4102 [PIC-4102]: 0 added, 0 removed, 1 modified
changed ProcessInstrumentationFunction Inst_PIC4150 [PIC-4150]: 2 added, 0 removed, 9 modified
changed PipingNetworkSystem Line_GOX4001 [GOX-4001]: 1 added, 1 removed, 0 modified
changed PlantModel PlantModel1: 0 added, 0 removed, 1 modified
```
The P-04 git diff (read in full, `-U0`) matches this list:
- the two sensing locations are swapped (PT-4101 to S1, PT-4150 to S3);
- the drawing groups are swapped by id;
- the removed signal PolyLine is (81.25, 30) -> (49.2, 36), the line to PV-4101B;
- the lower bubble moved from (55.5, 58.0) to (57.0, 66.0), and its sense point from x 55.5 to
  57.0;
- the PIC-4102 note text changed;
- the diagram's group order changed.

Nothing else on the sheet moved.

P-04 around the GOX suction (P-04 itself is outside this scope; only these regions were read,
not the whole sheet in tiles):
- build/P-04_crop-15-20-110-75.png (scale 6), before: build/P-04@e6f59b8_crop-15-20-110-75.png:
  - the upper bubble reads **PIC 4150**. Its measuring line goes down to the S3 tap east of
    XV-4117, and its dashed signal still runs into the K-4101 casing at the guide vanes;
  - the dashed line from PV-4101B's actuator is gone. PV-4101B is now drawn with no signal (see
    "Not checked");
  - the lower bubble reads **PIC 4101**, with its tap on S1 west of the GOX-4003 tee, clear of
    FIC-4148 and of the riser;
  - AI-3104 and FIC-4148 still touch (finding #1).
- build/P-04_crop-30-44-72-74.png (scale 10): the PIC-4101 bubble, its measuring line and the
  gaps quoted above.
- build/P-04_crop-45-22-110-50.png (scale 8): PIC-4150 and its signal to K-4101. No line runs
  through the bubble.
- build/P-04_crop-225-20-300-42.png, before: build/P-04@e6f59b8_crop-225-20-300-42.png: the note
  at PIC-4102 reads "K-4101 IGV master (D-096); HH trips K-4101" (was "K-4101 load (with
  PIC-4101); HH trips K-4101"). It is shorter than before and stays clear of the bubble and of
  the GOX-4002 label below.

## Layout
- **`layout/plant-model.yaml` diff** (`git diff e6f59b8 33fcaaa`, read in full, 20 lines):
  - provenance: the source hashes of the instrument list and P-04, and output_sha256 (now
    d29e24d66177...). `generator_sha256` is unchanged (edb4fded...), so the installed core is the
    one review23 used. The electrical-list hash is unchanged;
  - **IC-PIC-4101**: from_point [162.0, 35.942, 10.562] -> [142.654, 64.304, 9.254]; route
    34.92 -> 38.204 m; length 40 -> 44 m; still to JB-A4-1;
  - **IC-PIC-4150**: from_point [142.654, 64.304, 9.254] -> [162.0, 35.942, 10.562]; route
    15.704 -> 49.42 m; length 20 -> 55 m; still to JB-A3-2 (finding #2);
  - `cabling.cable_length_m` 6528 -> 6567. Cables 137, junction boxes 9, trays 44 and tray
    length 870.959 m are unchanged.

  No hunk touches equipment, pipes, in-line items, platforms, structures, zones, trays, junction
  box points or members, or findings. The two start points are swapped exactly, as expected.
- **Cable schedule:**
  - `electrical/cable-schedule.csv` changes only the rows IC-PIC-4101 (34.9/40 -> 38.2/44) and
    IC-PIC-4150 (15.7/20 -> 49.4/55);
  - `cable-schedule.md` changes the same two rows. Its header names model output d29e24d66177,
    which matches output_sha256;
  - the summary row "instrument 1 pr x 1.5 mm2" goes from 86 cables / 2587 m to 86 / 2626 m
    (+39 m = +4 + 35). No other row changes.
- **`cheme layout build --check`:** "layout/plant-model.yaml is up to date".
- **`cheme layout report` at 33fcaaa** (identical to review23):
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
    tray-span 17, tray-zone 6, plus 15 nozzle-defaulted infos. These are the same items, and the
    same acceptances in checks/checks.yaml, as in review19..23. There are 0 clash, headroom,
    access-blocked, wall-penetration, vent-outlet and escape findings, and no
    `layout-pipe-disconnected`.
  - **Objects:** 46 equipment items, 61 generated and 166 pinned pipes, 121 in-line items,
    8 platforms, 14 declared and 1 generated structures, 30 zones.
- **PNGs read (rendered at 33fcaaa):**
  - build/layout-plan.png (plot plan): the same site, areas, roads, racks, zones, pads and
    laydowns as review23;
  - build/layout-section-y68.png (along PR1): tiers and routes as in review23;
  - build/layout-section-x133.png (through CB-1 and the compander): CB-1 steel, stairs and
    platforms as in review23;
  - build/layout-section-x162_crop-28-0-44-14.png (across GOX-4001 S3 at the IC-PIC-4150 start,
    looking west): GOX-4001 rises at y about 29 and runs east at about 10.6 m. There is no
    platform or walkway under the point at y 35.9 (review23 #2).

## Checked and fine
- **Stage gates:** `cheme check` before this record: every gate passes except layout-review.
  That gate fails only because review23/22/21 (and older) are stale on
  control/instrument-list.yaml and layout/plant-model.yaml; this record replaces them. The
  electrical gate (a cable to every instrument, fill and separation) passes. No sign-off was
  written, and checks/status.json is untouched.
- **Lists:** the instrument list has both tags on P-04. The new notes match the sheet: PT-4101 on
  S1 upstream of XV-4117, with its signal to PV-4101B not drawn; PT-4150 on S3, with its signal
  drawn to the guide vanes. The PIC-4102 note on the sheet agrees with the instrument list
  ("holds the pipeline pressure on the K-4101 inlet guide vanes").
- **Generated outputs:** `layout build --check` is current, and the cable schedule names the
  current model output.

## Not checked
- **Outside this scope, for the control review:** PV-4101B on P-04 now has no signal line at all,
  although PIC-4101 acts on it (build/P-04_crop-15-20-110-75.png). D-096 records this as open
  ("Drawing the low select, the cascade and PIC-4101's signal to PV-4101B"), and the instrument
  list says "The signal to PV-4101B is not drawn". This is P&ID and control content, so it is
  not a finding of this record.
- **The control content of D-096 and control-review4:** loops, sequences, philosophy,
  narrative, the low select, the cascade, the fail positions and the open points. These belong
  to the control review.
- **The 9 `hazop-input-changed` warnings** (H-01..H-04 to be re-stamped; D-096 lists what the
  H-04 owner must reassess) and the 3 `process-energy-balance` warnings: outside this layout
  scope, for the HAZOP and process owners.
- **P-04** was not read in tiles. Only the GOX-suction region (15..110 x 20..75 mm) and the note
  at PIC-4102 were read.
- Everything review19 lists under "Not checked" (relief sizing, pipe stress and lugs, the CB-1X
  envelope, the S3 -> S4 allowance) stays open as D-091 O1 .. O6.
