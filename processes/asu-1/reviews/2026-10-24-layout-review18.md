---
topic: layout
reviewed_commit: 896fbda4f5147b16e879dfa060a117cb59d83f56
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, equipment/equipment-list.yaml, checks/checks.yaml, control/cause-effect.yaml, control/instrument-list.yaml, lca/lca.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 896fbda4f5147b16e879dfa060a117cb59d83f56, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: 896fbda4f5147b16e879dfa060a117cb59d83f56, relation: depends-on}
  - {path: DESIGN.md, revision: 896fbda4f5147b16e879dfa060a117cb59d83f56, relation: depends-on}
  - {path: process/flowsheet.yaml, revision: 896fbda4f5147b16e879dfa060a117cb59d83f56, relation: analyses}
  - {path: lca/results.md, revision: 896fbda4f5147b16e879dfa060a117cb59d83f56, relation: analyses}
  - {path: estimate/tea.md, revision: 896fbda4f5147b16e879dfa060a117cb59d83f56, relation: analyses}
reviewer: Claude (independent review agent; did not author D-081 (10), the review17 fixes, the datasheets, the drawings or the layout files)
reviewer_kind: agent
branch: feat/datasheet-dimensions-drawings
merge: pending
---
# Review: layout, eighteenth review (independent) of PR #22, the review17 fixes and the tank lifting decision

This is an independent review of branch `feat/datasheet-dimensions-drawings` (PR #22) at 896fbda.
It covers the five commits since review17 (6a3356c):
- 591dc5d: owner decision D-081 (10), the field-erected tanks out of the lifting study;
- 0b950c8: review17#1, list-derived datasheet sizes and weights marked ASSUMED;
- 981cc14: review17#2, C-1101 N7 service text;
- 96895d3: review17#3, D-081 (5) supersedes the D-041 (6) erection weights;
- 896fbda: review17#4, "datasheet final" is not an issue status.

The rest of the branch is as review17 found it. `git diff origin/main..HEAD -- pid/ process/`
is empty, and `cheme diff origin/main --list` reports "No P&ID changed". Since 6a3356c no file
in `layout/` (other than the generated model and lifting study), `piping/` or `pid/` changed.
cheme-as-code is the global `cheme` 0.8.0 (pyDEXPI 2.1.0).

Verdict: **no critical, high or medium finding is open**. All four review17 findings are closed.
The owner's tank decision is applied consistently in the equipment list, the model, the lifting
study, `checks/checks.yaml` and DESIGN.md. There are two new low findings: #1 the tank
datasheets do not carry the decision, and #2 the list-derived head and support types are still
unmarked. Review15#2, review3#2 and layout#15 stay open, unchanged.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-layout-review18#1 | datasheets | T-4101, T-4102 | The datasheets do not carry the D-081 (10) decision. D-081 (10) says the 0.5 t roof-fitting lift is "ASSUMED (owner's figure, the tank supplier confirms it)". The equipment list notes now say "Field-erected plate by plate, never lifted whole: its heaviest crane lift is a roof fitting ... ~0.5 t (lift_weight, D-081 (10))". But `equipment/datasheets/T-4101.yaml` and `T-4102.yaml` still have the old list notes, and their `weights` has only `empty` (26 / 35 t). The tank supplier reads the datasheet, so it is never asked to confirm the figure. K-1101's datasheet does name its `lift_weight` (34 t motor) in the source of its empty weight. | low | open | Add the field erection and the 0.5 t heaviest lift (ASSUMED, D-081 (10), "supplier to confirm") to the notes, or to the `weights.empty` source, of both tank datasheets. Then rerun `cheme datasheets drawing --write` if the drawing changes. |
| 2026-10-24-layout-review18#2 | datasheets | 25 datasheets, `dimensions.head` / `dimensions.support.type` | 0b950c8 marked the numeric list values as ASSUMED, but the shape choices copied from the same ASSUMED list are still unmarked. These are 17 `head` values (ellipsoidal_2_1, cone_roof) and 25 `support.type` values (skirt, saddles, legs, base_plate, none), each with source "cheme datasheets fill: equipment/equipment-list.yaml dimensions...". The list header says its dimensions are ASSUMED (D-028), and the README rule covers every value not calculated or given. The values from the layout model (axis_deg, support elevation, stands_on) are the plant's own placement decisions and are fine as they are. | low | open | Add `assumed: true`, citing D-028, to the list-derived `head` and `support.type` of the 25 datasheets, or state in D-081 (1) why the shape types are given rather than assumed. Core suggestion as in review17#1: `fill --dimensions` carries the list's ASSUMED status. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-layout-review17#1 | List-derived dimensions and 31 empty weights not marked ASSUMED on datasheets and drawings | medium | closed 0b950c8 | `git diff 6a3356c 0b950c8 -- equipment/datasheets/*.yaml` adds exactly 140 `assumed: true` lines and changes only `source` texts: 109 sizes (D-028) and 31 weights (D-034). No value line changed. A script over all 40 datasheets finds every numeric `dimensions` / `weights` value flagged `assumed` except the layout-model axis and elevation values. E-1102.svg prints "OD 1.6*" and "12 t*", and T-4101.svg prints "26 t*". `datasheets drawing --check`: all 40 current. The unmarked categorical types are split off as #2. |
| 2026-10-24-layout-review17#2 | C-1101 N7 service truncated on the drawing | low | closed 981cc14 | The C-1101.yaml N7 `service` is "Draw-off, vortex breaker" (24 characters). C-1101.svg contains the texts "Draw-off, vortex breaker" and "CHWR-1001". The full requirement (seal-loss level 13.20 m = N7 bore top + 0.05 m, D-088 (4)) is in the datasheet `notes`. D-081 (9) no longer claims the long text is on the schedule. |
| 2026-10-24-layout-review17#3 | D-041 (6) erection weights not reconciled with D-081 (5) | low | closed 96895d3 | D-081 (5) is headed "amends D-034 (1), D-041 (6)" and says its weights supersede D-041 (6) and govern the lifting study and the basis for the construction lifting plan. It explains the C-1102 (+44 %, 12 against 8 mm) and V-2101A/B (+24 %, 100 N/mm2 at 250 C) gaps. The basis is the vessel as set, without packing or adsorbent, and the supplier's shipping weight replaces both. D-041 (6) now reads "(weights superseded by D-081 (5))". The lifting study rows (C-1102 36 t, V-2101A/B 61 t) already used the D-081 (5) weights. |
| 2026-10-24-layout-review17#4 | "datasheet final" on DRAFT outlines | low | closed 896fbda | D-081 (3) and equipment/datasheets/README.md now say that "datasheet final" is the completeness status (`draft: false`), not an issue or approval, and that the outlines are DRAFT, for enquiry. They record that cheme-as-code 0.8.0 has no drawing status field, and that `draft: true` would take the datasheets out of the `datasheets` gate. I agree that this is the plant-side fix available. The core suggestion stands. |
| 2026-10-24-layout-review15#2 | D-089 bound case 21.1 + 8 + 3 = 32.1 kPa against S3 -> S4 32 kPa (-0.107 kPa) not stated or accepted | low | open | Unchanged at 896fbda: `process/` is untouched on this branch, and the finding is for the simulation owner. |
| 2026-10-22-layout-review3#2 | PSV tailpipes free above the valves | low | open | Unchanged: the guides wait for the stress analysis (D-050, D-062 (4)). |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | Unchanged; waits for the vendor drawing (D-050 / D-062 (4)). |

## Drawing
`cheme validate` at 896fbda gives 0 errors and 33 warnings, the same count as review17. 93 files
were compared, with the same cross-checks, including "datasheet dimensions vs equipment list"
and "datasheet nozzles vs P&IDs".

Counts per sheet:
- P-01: 0 line-through-label, 2 line-crossing (accepted: D-069, D-076), 0 label-overlap, 0
  label-far-from-owner;
- P-02: 0 in every count;
- P-03: 3 line-crossing (accepted), 0 otherwise;
- P-04: 1 line-crossing (accepted), 0 otherwise.

The `drawing-clean` gate passes. No P&ID changed, so no P&ID tile was read.

`cheme datasheets drawing --check`: all 40 datasheet SVGs are current. I checked the SVG texts
of C-1101 (N7 service, CHWR-1001, "datasheet final"), E-1102 ("OD 1.6*", "12 t*") and T-4101
("26 t*").

## Layout
- `cheme layout build --check`: "layout/plant-model.yaml is up to date". Since review17 the
  model changed only in its equipment-list fingerprint and `lift_weight: 0.5` on T-4101 and
  T-4102.
- `cheme layout lifting --check`: exit 0. The study no longer has the T-4101 (26 t, no crane
  pad) and T-4102 (35 t, no laydown) rows. K-1101 remains as its 34 t motor (heaviest part,
  building B1).

`cheme layout report` at 896fbda:
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
  - accepted, as in review17: operability 1 (XV-3105), free-span 2, support-missing 15 infos,
    tier 1 (WN-1001, D-071 (3)), access-enclosed 1, tray-span 17, tray-separation 1;
  - tray-zone 6 (2 warnings for P-4101A/B in Z-O2-SEALS, 4 infos) and nozzle-unconnected 2
    infos (D-028), as in review17;
  - **lifting 4 and laydown 1** (review17: 5 and 2). The findings are F-1101 and C-1102 with no
    crane pad, the V-2101A/B lanes blocked, and C-1102 with no laydown. All five are accepted
    in checks/checks.yaml as shop-built erection lifts (D-034, D-081 (5)). The T-4101 lifting and
    T-4102 laydown findings are gone, and so are their acceptances. No acceptance was left
    without a finding, since validate reports no stale acceptance.
- **Objects:** 46 equipment items, 61 generated and 166 pinned pipes, 121 in-line items,
  8 platforms, 13 declared and 1 generated structures, 30 zones.

PNGs read (rendered at 896fbda):
- build/layout-plan.png;
- build/layout-section-y68.png (along PR1);
- build/layout-section-x133.png (through CB-1 / compander).

They show the same routes, racks, structures, zones, crane pads and laydown areas as review17.
The tank area A5 keeps its pads (Z-PAD-A5, Z-PAD-A5N) and laydowns for the vaporizers, and the
tanks now need none.

**Tank lifting decision, consistency:** a grep finds the tanks as crane lifts nowhere outside
the review records.
- equipment-list.yaml: header and both tank notes say `lift_weight` 0.5 t ASSUMED, D-081 (10).
- plant-model.yaml: `lift_weight: 0.5` on both tanks.
- lifting-study.md / .csv: no tank row.
- checks.yaml: the two acceptances are removed, and the comment cites D-081 (10).
- DESIGN.md: D-081 (5) now names only the shop-built rows ("five findings") and points to (10).
  D-081 (10) records the owner decision with its reason, the 0.5 t basis, the 5 t threshold
  and who handles plate lifts. D-041 (6) still says the tanks are field-erected, which agrees.

The empty weights (26 / 35 t) stay for the LCA and the datasheets. `assess mto / estimate / lca
--check` are current, and 591dc5d changed only their fingerprints. The one gap is that the tank
datasheets do not carry the decision (#1).

## Checked and fine
- **0b950c8 changed no value:** the diff of all datasheet YAMLs has only `source` and
  `assumed: true` lines (140 each), as its message says.
- **Assess outputs:** `cheme assess mto / estimate / equipment / tea / lca --check` all exit 0.
- **Gates:** `cheme check --no-write` at 896fbda passes 30 gates. Only `layout-review` fails,
  because review17 is out of date by checks/checks.yaml, the datasheets and the list. This record
  closes it.
- **CI steps, run locally from the repository root** (the steps of .github/workflows/validate.yml):
  - per process: `cheme fmt --check` (exit 0), `cheme validate` (0 errors) and `cheme check
    --no-write`, as above;
  - pytest: 74 passed;
  - `build_catalog.py`: full 1 process (2 warnings, no BFD / PFD preview rendered), `--public`
    0 processes;
  - `build_lci.py --strict`: 4 activities from 1 process, into the scratchpad `ci-r18`.
- **Stage gates:** no stage sign-off was written, and `checks/status.json` is untouched.
- **Licence rule:** no third-party text was added, and no commercial downstream product is named.

## Not checked
- **The 0.5 t roof-fitting figure:** the owner's ASSUMED value, for the tank supplier to confirm.
  Plate handling during tank erection is the tank erector's.
- **Vessel, column and tank design, and the erection lifts of the shop-built items:** for the
  vessel suppliers and the construction lifting plan, as in review17.
- **Datasheet drawings:** none rendered to PNG in this review. They were checked through `drawing
  --check`, validate and the SVG texts named under Drawing.
- **TSA top piping, tank nozzles, PR1 walkway for XV-3105, pipe stress, supports and PSV
  tailpipe guides, B1 crane, vent and inert study:** as in review16 and review17, with the same
  owners.
- **P&ID tiles:** none read, since no sheet changed.
