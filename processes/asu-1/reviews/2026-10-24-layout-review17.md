---
topic: layout
reviewed_commit: 3b71705531ce22d0aeaa814e63650d178cae22e9
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, equipment/equipment-list.yaml, checks/checks.yaml, control/cause-effect.yaml, control/instrument-list.yaml, lca/lca.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 3b71705531ce22d0aeaa814e63650d178cae22e9, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: 3b71705531ce22d0aeaa814e63650d178cae22e9, relation: depends-on}
  - {path: DESIGN.md, revision: 3b71705531ce22d0aeaa814e63650d178cae22e9, relation: depends-on}
  - {path: process/flowsheet.yaml, revision: 3b71705531ce22d0aeaa814e63650d178cae22e9, relation: analyses}
  - {path: lca/results.md, revision: 3b71705531ce22d0aeaa814e63650d178cae22e9, relation: analyses}
  - {path: estimate/tea.md, revision: 3b71705531ce22d0aeaa814e63650d178cae22e9, relation: analyses}
reviewer: Claude (independent review agent; did not author D-081, the datasheet dimensions, weights or drawings, the LCA mapping or the layout files)
reviewer_kind: agent
branch: feat/datasheet-dimensions-drawings
merge: pending
---
# Review: layout, seventeenth review (independent) of PR #22, datasheet dimensions, weights and drawings

This is an independent review of branch `feat/datasheet-dimensions-drawings` (PR #22) at 3b71705.
The branch contains main up to 58c2063 (review16 and PR #31 merged). It covers the whole
change against origin/main: 99 files, mostly `equipment/datasheets/*.yaml` and new `*.svg`.
The commits are:
- 2c3894a (D-066 on its branch, now D-081): main dimensions, empty weights and outline drawings;
- 3071c34: merge of main (D-066 .. D-090);
- 2b5bf20: `plant.yaml` requires cheme-as-code >= 0.8;
- 9def5e6: E-3103 `housed_in` C-3102;
- e96555a: empty weights of the erected-once items (D-081 (5)), lifting rows accepted;
- c4eae4e: D-081 (6) .. (8), the PR #22 checklist;
- 0561b70: review14#1 fix (LV-1114 limit, C-1101 N7 vortex breaker);
- fb29263, 435d616, 3b71705: fixes for the five points of the PR #22 review (drain stubs and
  E-3105 nozzle positions; LCA carbon steel before stainless; D-081 (1), (3), (8) text).

`git diff origin/main..HEAD -- pid/ process/` is empty: no P&ID and no flowsheet changed, and
`cheme diff origin/main --list` reports "No P&ID changed". The layout model changed only in
input fingerprints and the new `weight` in seven equipment `dimensions`: no geometry, route
or nozzle moved. cheme-as-code is the global `cheme` 0.8.0 (pyDEXPI 2.1.0).

The five PR #22 review points were raised on the pull request, not in a record. Their state:
- drain stubs on the 0.3 m default and E-3105 nozzles misplaced: fixed in fb29263;
- LCA `SS*` before `*CS*`: fixed in 435d616;
- D-081 (1) stale: fixed in 3b71705;
- exchanger channel and bonnet not drawn: deferred in D-081 (3), with the model's lengths and a
  core suggestion;
- undrawn nozzles: deferred in D-081 (8), which lists them all.

I agree with both deferrals. No datasheet field holds a channel length without misstating the
T-T or the overall length. The nozzles in (8) are generator defaults (`basis: pid`), not
decisions.

Verdict: **no critical or high finding is open**. Review14#1 is closed. There are four new
findings: #1 is medium and #2 .. #4 are low. Review15#2, review3#2 and layout#15 stay open,
unchanged.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-layout-review17#1 | datasheets | 31 empty weights; overall dimensions of all 39 sized items | The list's values are not marked ASSUMED on the datasheets or drawings. The equipment list says every dimension is ASSUMED at basic engineering (header, D-028). It says the same of every weight (D-034 typical sizes, D-081 (5)). `cheme datasheets fill --dimensions` copied these values without `assumed: true`. Only the model-read T-T and support heights and the eight D-081 (5) weights carry the flag. So 31 empty weights (E-1101 12 t, K-4101 45 t, E-4101 24 t, ...) print with no `*`, for example "12 t" on E-1102.svg and "52 t*" on C-1101.svg. So do the outside diameters and overall lengths and heights, for example "OD 4" on C-1101 and "OD 1.6", "8 overall" on E-1102. The README rule is: "mark every value you have not calculated or been given `assumed: true`". The supplier drawings show a guess as data. | medium | open | Add `assumed: true` with the source (D-028 sizes, D-034 / D-081 (5) weights) to the filled `dimensions` and `weights` of each datasheet; fill keeps hand-written values. Rerun `cheme datasheets drawing --write`. Core suggestion: `fill --dimensions` carries the list's ASSUMED status. |
| 2026-10-24-layout-review17#2 | datasheets | C-1101 N7 | The C-1101.svg nozzle schedule truncates the N7 service to "Chimney tray chilled-wate…". The drawing therefore shows neither the vortex breaker nor the line, since CHWR-1001 was replaced by the service text. D-081 (9) says the vortex breaker is "shown on the nozzle schedule of the drawing". The datasheet YAML carries the full text, which is why review14#1 is closed. | low | open | Give N7 a service text that fits the column, such as "CHWR-1001, vortex breaker" (25 characters, the width that shows). Keep the full requirement in a note or `notes`. Regenerate the drawing and correct D-081 (9) if needed. |
| 2026-10-24-layout-review17#3 | DESIGN.md | D-041 (6) vs D-081 (5) | Two decisions give different ASSUMED erection weights for the same items, and neither refers to the other. D-041 (6): C-1101 ~55, C-1102 ~25, V-2101A/B ~49 t each (thin-shell formula, x 1.3 including internals), F-1101 "weight TBD". D-081 (5): 52, 36, 61 and 10 t (Sinnott dead weight, x 1.15, no internals). D-081 (5) says it amends D-034 (1) but not D-041 (6). C-1102 differs by 44 % and V-2101A/B by 24 %. | low | open | Add to D-081 (5) that it amends D-041 (6), and say which basis the construction lifting plan should use (with or without internals). The D-041 text stays as history. |
| 2026-10-24-layout-review17#4 | datasheets | all 40 drawings, title block | Each generated drawing shows "datasheet final" in the title block, from `draft: false` of the datasheet. D-081 (3) calls the outlines "DRAFT" (schematic nozzle stubs and saddles, undrawn nozzles, no channel). A supplier may read "final" as an issued document. | low | open | Plant: state in D-081 (3) and the datasheet README that "final" is the datasheet's completeness status, not an issue or approval. Core suggestion: print the drawing's own DRAFT status next to it. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-layout-review14#1 | LV-1114 2 x normal capacity limit and N7 vortex breaker not on the entries the suppliers read | low | closed 0561b70 | In control/instrument-list.yaml, LIC-1114 now states that LV-1114 fully open passes at most 2 x 34.4 = 69 m3/h, with no larger trim (D-088 (4), D-090, ASSUMED for the SRS). The equipment/datasheets/C-1101.yaml N7 `service` reads "Chimney tray chilled-water draw-off, with a vortex breaker (required: ... D-088 (4))". The layout model was rebuilt (fingerprint only, `layout build --check` current). The truncated drawing text is split off as #2. |
| 2026-10-24-layout-review15#2 | D-089 bound case 21.1 + 8 + 3 = 32.1 kPa against S3 -> S4 32 kPa (-0.107 kPa) not stated or accepted | low | open | Unchanged at 3b71705: process/flowsheet.yaml S3 still reads "S4 5.6 bara + 32 kPa to E-3101 (DN700 lines at their bound 21.1 kPa ...)". This branch may not touch the flowsheet; it is for the simulation owner. |
| 2026-10-22-layout-review3#2 | PSV tailpipes free above the valves | low | open | Unchanged: the guides wait for the stress analysis (D-050, D-062 (4)). |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | Unchanged; waits for the vendor drawing (D-050 / D-062 (4)). |

## Drawing
`cheme validate` at 3b71705 gives 0 errors and 33 warnings, the same set as review16. 92
files were compared, including the cross-checks "datasheets vs equipment list, datasheet nozzle
locations vs layout model, datasheet dimensions vs equipment list, datasheet nozzles vs
P&IDs".

Counts per sheet:
- P-01: 0 line-through-label, 2 line-crossing (accepted: D-069, D-076), 0 label-overlap, 0
  label-far-from-owner;
- P-02: 0 in every count;
- P-03: 3 line-crossing (accepted), 0 otherwise;
- P-04: 1 line-crossing (accepted), 0 otherwise.

The `drawing-clean` gate passes. No P&ID changed, so no P&ID tile was read.

Datasheet drawings: `cheme datasheets drawing --check` reports all 40 SVGs current, and validate
gives no `datasheet-drawing-stale`. I read rendered PNGs of C-1101, C-3102, E-1102, E-3105,
T-4101 and V-2101A:
- **E-3105:** N3 / N4 at the channel and the floating-head ends; N5 drain (+1.5 m) and N6 drain
  (-2.3 m, under the west head) at the bottom; N7 vent (+2.4 m) on top.
- **E-1102:** N5 drain stub 0.167 m under the shell.
- **C-3102:** drawn on C-3101 at +20 m, with N1 / N4 / N5 marked † as D-081 (8) says.
- **C-1101:** N7 with its service truncated (#2).
- **T-4101:** cone roof, base +0.5 m.

## Layout
- `cheme layout build --check`: "layout/plant-model.yaml is up to date". The model diff against
  main is the instrument-list and equipment-list fingerprints, plus `weight` added to F-1101,
  K-1101, C-1101, C-1102, V-2101A/B (and the tanks through the list).
- `cheme layout lifting --check`: exit 0.

`cheme layout report` at 3b71705, identical to review16 except for the lifting and laydown
rows:
- **Lines:** 81, all routed except 4 skipped segments (GAN-3002 and LN-3002, D-028; two
  VNT-3004). 0 unrouted.
- **Chains per method:** astar 26, open 8, pinned 166, rack 15. No `direct` and no
  `rack+direct`.
- **Reasons:**
  - local: above the pipe-way 7, pipe-way 5, pump run at grade 4, rack detour too long 1, rack
    run too short 1, short run 8;
  - open end 8;
  - pinned 166;
  - rack: battery limit at a rack end 13, longer than local_max_m 2.
- **Rack fill:**

  | rack | 5 m | 6.5 m | 7 m | 8.5 m | 9 m |
  |---|---:|---:|---:|---:|---:|
  | PR1 | 61 % | | 43 % | | 25 % |
  | PR2 | | 6 % | | 6 % | |
  | PR3 | | 48 % | | 43 % | |

- **Model findings per rule:**
  - 0 each: clash-*, headroom, access-blocked, wall-penetration, vent-outlet, zone-crossing,
    separation, escape-*, landing-width, egress-zone, operator-unknown, pad-overlap, spacing,
    building-spacing, zone-source;
  - accepted, as in review16: operability 1 (XV-3105), free-span 2, support-missing 15 infos,
    tier 1 (WN-1001, D-071 (3)), access-enclosed 1, tray-span 17, tray-separation 1;
  - tray-zone 6 (2 warnings P-4101A/B in Z-O2-SEALS, 4 infos), as in review16; nozzle-unconnected 2 infos (D-028);
  - **lifting 5 and laydown 2, new on this branch:** F-1101, C-1102 and T-4101 have no crane
    pad; the V-2101A/B lanes are blocked; C-1102 and T-4102 have no laydown. All seven are
    accepted in checks/checks.yaml as erection lifts for the construction lifting plan (D-034,
    D-081 (5)). I agree: D-034 / D-041 (6) already took these items out of the maintenance
    study, and the weights only made them visible to the rule.
- **Objects:** 46 equipment items, 61 generated and 166 pinned pipes, 121 in-line items,
  8 platforms, 13 declared and 1 generated structures, 30 zones.

PNGs read (rendered at 3b71705):
- build/layout-plan.png;
- build/layout-section-y68.png (along PR1);
- build/layout-section-x133.png (through CB-1 / compander).

They show the same routes, racks, structures, zones, crane pads and laydown areas as in review16.

## Checked and fine
- **Weights, datasheet vs list:** a script compared all 40 datasheets with
  equipment/equipment-list.yaml. Every `weights.empty` equals the list's `dimensions.weight`;
  E-3103 has none, on purpose (D-081 (5)). Validate gives no `datasheet-dimension-mismatch`.
- **D-081 (5) weights recomputed with the stated relations:**
  - C-1101: e = 0.8 x 4000 / (2 x 0.85 x 125 - 0.8) + 3 = 18.1 mm, shell 47.6 t + skirt 5 = 52 t;
  - C-1102: 12 mm minimum, 31.8 t + 4 = 36 t;
  - V-2101A/B: 24.3 -> 25 mm, about 62 t by my arithmetic against the stated 61 t, inside the
    accuracy of the ASSUMED inputs;
  - T-4101: inner plate 9.6 t, outer 12.65 t, x 1.15 = 25.6 -> 26 t.
  K-1101 89 t is above its 34 t `lift_weight`, as it must be.
- **Nozzle positions from the model:** E-3105 N3 -2.2, N4 +2.3, N5 +1.5, N6 -2.3 (west,
  orientation 180) and N7 +2.4 m match the `point`s in layout/plant-model.yaml against the
  centre x 133.0. The drain flange faces are at 0.633 m, 0.167 m under the 0.8 m shell
  underside.
- **LCA mapping:** with `*CS*` before `SS*`, the 40 list materials split into 20 CS, 10 SS and
  9 aluminium items plus E-3103 (no weight). No item falls through the three globs now that
  the catch-all `*` is gone. Construction CS 455.5 t, SS 98 t, aluminium 127 t. lca/results.md
  shows construction 0.688, maintenance 0.163 and total 142.851 kg CO2-eq/t GOX, as D-081 (5)
  says. `cheme assess mto / estimate / equipment / tea / lca --check` all report current.
- **Gates:** `cheme check --no-write` passes 30 gates and fails only `layout-review`, which
  waited for this record (review16 was out of date by the datasheets and lists).
- **CI steps, run locally from the repository root:**
  - `cheme fmt --check`, `cheme validate` (0 errors) and `cheme check --no-write` per process;
  - pytest: 74 passed;
  - `build_catalog.py`: full 1 process, `--public` 0 processes;
  - `build_lci.py --strict`: 4 activities, into the scratchpad `ci-pr22`.
- **Stage gates:** no stage sign-off was written, and `checks/status.json` is untouched.
- **Licence rule:** the weight method is cited (Sinnott, C&R Vol. 6) in our own words, with
  no copied table. No commercial downstream product is named.

## Not checked
- **Vessel, column and tank design** (thickness, heads, skirt and saddle design, tank plate
  schedule): for the vessel and tank suppliers. The weights stay ASSUMED.
- **Exchanger channel and bonnet lengths and the undrawn nozzle orientations** (D-081 (3),
  (8)): for a later nozzle orientation pass with the piping study.
- **Erection lifts** (cranes, pads, lanes for C-1101, C-1102, F-1101, V-2101A/B and the
  tanks): the construction lifting plan by the crane contractor.
- **Datasheet drawings not opened:** the 34 not listed under Drawing were checked only
  through `drawing --check` and validate.
- **TSA top piping, tank nozzles, PR1 walkway for XV-3105, pipe stress, supports and PSV
  tailpipe guides, B1 crane, vent and inert study:** as in review16, with the same owners.
- **P&ID tiles:** none read, since no sheet changed.
