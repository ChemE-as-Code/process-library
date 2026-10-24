---
topic: layout
reviewed_commit: e1ff49f50439bce98be62ef42aa05b1e1ebdbf51
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, checks/checks.yaml, control/cause-effect.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: e1ff49f50439bce98be62ef42aa05b1e1ebdbf51, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: e1ff49f50439bce98be62ef42aa05b1e1ebdbf51, relation: depends-on}
  - {path: DESIGN.md, revision: e1ff49f50439bce98be62ef42aa05b1e1ebdbf51, relation: depends-on}
  - {path: scripts/datasheet_sizing.py, revision: e1ff49f50439bce98be62ef42aa05b1e1ebdbf51, relation: analyses}
  - {path: process/simulation-run.json, revision: e1ff49f50439bce98be62ef42aa05b1e1ebdbf51, relation: analyses}
  - {path: process/flowsheet.yaml, revision: e1ff49f50439bce98be62ef42aa05b1e1ebdbf51, relation: analyses}
  - {path: process/simulation.yaml, revision: e1ff49f50439bce98be62ef42aa05b1e1ebdbf51, relation: analyses}
reviewer: Claude (independent review agent; did not author D-088, the layout files, the datasheets or the P&ID changes)
reviewer_kind: agent
branch: asu-followup
merge: pending
---
# Review: layout, fourteenth review (independent) after review13, D-088

This is an independent review of branch `asu-followup` at e1ff49f. It covers the fixes for
reviews/2026-10-24-layout-review13.md (106d6fb), five commits:
- c36410f D-088 (2) (simulation run record refreshed);
- 9a21064 D-088 (1) (K-1101 outlet held on the front-end budget, D-079 correction note);
- 5c7ed67 D-088 (3) (S12D deferred to the simulation owner with normalised fractions);
- 8150908 D-088 (4) (I-03 SIF specification basis);
- e1ff49f D-088 (5) (P-03 E-3105 tag).

The reviewer designed none of this. cheme-as-code is the global `cheme` 0.7.0 (core da8c09d,
with #102 / #105). "Computed" means `cheme run scripts/datasheet_sizing.py` at e1ff49f (output not
committed). `git diff 106d6fb..HEAD` touches DESIGN.md, PROGRESS.md, cause-effect.yaml,
instrument-list.yaml, the C-1101 and K-1101 datasheets, plant-model.yaml (two input fingerprints
only), P-03.xml (one text position), simulation-run.json and the sizing script.
process/flowsheet.yaml, process/simulation.yaml, process/design-basis.yaml and
checks/status.json are unchanged.

P&ID changes: P-03 `E3105_TagText` position (66, 124) -> (87, 143.3) only. Not drawn: none.

Verdict: **no critical, high or medium finding is open**. Review13 #2, #4 and #5 are closed with
evidence. Review13#1 is superseded by #2 below (the hold is recorded; only the simulation owner's
S2 answer remains). Review13#3 stays open with the simulation owner. One new low finding (#1).

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-layout-review14#1 | C-1101 datasheet / instrument list | I-03 supplier requirements | D-088 (4) rests the 144 s process safety time on two supplier requirements: LV-1114 fully open passes at most 2 x the normal 34.5 m3/h (69 m3/h), and a vortex breaker in N7 (seal loss at the bore top + 0.05 m). Both are written only in the C-1101 `chimney_tray_sif_basis`, the I-03 notes and DESIGN.md. The LIC-1114 instrument-list entry (the only list entry for LV-1114) still says only "acts on LV-1114 (fail closed)", and the C-1101 nozzle N7 entry names no vortex breaker. The valve and packing enquiries are read from those entries, so a valve sized larger (a usual rangeability margin gives more than 2 x normal) halves the time without anyone seeing the SIF basis. | low | open | Put the 69 m3/h maximum fully-open capacity (D-088 (4)) on the LIC-1114 / LV-1114 entry, and the vortex breaker on the C-1101 N7 nozzle entry (or its notes). |
| 2026-10-24-layout-review14#2 | DESIGN.md / K-1101 datasheet | front-end budget S3 -> S4 | Remainder of review13#1. The hold is now recorded (K-1101 `outlet_pressure`, D-088 (1), D-079 correction note). The budget itself is still short: computed at e1ff49f, section 10, lines 17.1 kPa + bed 8 + F-2101 3 = 28.1 kPa against 28 kPa, margin -0.055 kPa; at the bound 21.1 kPa, margin -4.11 kPa. The D-080 (1) request (S2 ~6.02 bara, ~27 kW, motor 8,121 + 27 kW against 9,000 kW) is unanswered. | low | open | Simulation owner: answer D-080 (1), either S2 ~6.02 bara in flowsheet.yaml / simulation.yaml and a rerun, or the vessel nozzle losses taken inside the bed / F-2101 allowables; then lift the hold. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-layout-review13#1 | front-end budget short 0.06 / 4.1 kPa, K-1101 outlet without the hold | low | superseded by 2026-10-24-layout-review14#2 | 9a21064: K-1101.yaml `outlet_pressure` source carries "HOLD (DESIGN.md D-080 (1), D-088 (1))" with 17.1 / 21.1 kPa, -0.06 / -4.1 kPa, S2 ~6.02 bara, +27 kW, 8,121 + 27 against 9,000 kW, all equal to the computed section 10 and section 1. D-079 now notes 17.4 + 8 + 3 = 28.4 kPa. The S2 raise is the owner's, split off as #2. |
| 2026-10-24-layout-review13#2 | simulation run record stale after D-087 | low | closed c36410f | The sizing script prints "run 2026-10-23T23:43:48Z at 106d6fb; current with process/*.yaml". The run record diff changes only run_at, commit, the flowsheet fingerprint, method, status / iterations (19) and line numbers. `cheme process simulate --check` at e1ff49f: K1101 7,259.77 kW / cooling 7,697.95 / shaft 6,867.74 kW, K4101 2,262.49 kW, K4102 237.669 kW, equal to the record and D-088 (2). D-080 (2) wording corrected. flowsheet.yaml is unchanged since 106d6fb. |
| 2026-10-24-layout-review13#3 | S12D fractions sum 1.0000012; S12D water 143.1 vs TSA 165 kg/h | low | open | Deferred by 5c7ed67 (D-088 (3)): S12D is `assumed` in the owner's flowsheet.yaml. Validate still gives the 2 `pydexpi_composition_fractions` warnings. I recomputed both D-088 (3) rows from S12H 18,486 kg/h + CO2 67.7 kg/h + water with the stated molar masses: flows 18,697 / 18,719 kg/h; every fraction within 1e-7 of the table (O2 0.0504393 against 0.0504394 on the PR row, a rounding to make the row close). The owner's S12D edit is still needed. |
| 2026-10-24-layout-review13#4 | I-03 trip level, process safety time, XV-1115 closing time not stated | low | closed 8150908 | Computed at e1ff49f ("I-03 SIF timing"): liquid area 9.425 m2, inflow 34.5 m3/h, LV-1114 open 68.99 m3/h; 13.5 -> 13.35 m 1.41 m3 in 148 s; 13.35 -> 13.20 m 1.38 m3, PST 144 s, 72 s with the inflow lost. Checked by hand: pi/4 x 4.0^2 x 0.75 = 9.425 m2; (13.35 - 13.2041) x 9.425 = 1.375 m3 / 34.5 m3/h = 143.5 s. SIF response <= 15 s (5 s detection and logic, XV-1115 5 .. 10 s) is inside the 72 s. Stated in the C-1101 `chimney_tray_sif_basis` (ASSUMED, for HAZOP / LOPA / SRS confirmation), the I-03 notes and the LSLL-1115 notes, in agreement. The two supplier requirements it rests on are not yet on the entries the suppliers read: new #1. |
| 2026-10-24-layout-review13#5 | P-03 E-3105 tag across the K-3101 discharge line | low | closed e1ff49f | build/P-03_crop-50-95-120-160.png: "E-3105" below HV-3127 / HV-3128, above "AIR-3002 DN 200", on the exchanger's side of the K-3101 discharge line; before build/P-03@106d6fb_crop-50-95-120-160.png. `cheme show E-3105`: drawn at 78,113.4,88.4,143.3 mm with the tag. P-03 counts unchanged (3 accepted crossings, 0 label-far-from-owner). |
| 2026-10-22-layout-review3#2 | PSV tailpipes free above the valves | low | open | Unchanged: the guides wait for the stress analysis (D-050, D-062 (4)). |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | Unchanged; waits for the vendor drawing (D-050 / D-062 (4)). |

## Drawing
`cheme validate` at e1ff49f: 0 errors, 35 warnings, the same as review13:
- 13 instrument-no-interlock;
- 12 template-metadata;
- 6 line-crossing;
- 2 titleblock-sheet;
- 2 pydexpi_composition_fractions (review13#3).

Counts per sheet:
- P-01: 0 line-through-label, 2 line-crossing (accepted: D-069, D-076), 0 label-overlap,
  0 label-far-from-owner, 0 text-outside-frame, 0 title-text-overflow, 0 line-through-symbol.
- P-02: 0 in each count.
- P-03: 0 line-through-label, 3 line-crossing (accepted, unchanged), 0 label-overlap,
  0 label-far-from-owner, 0 text-outside-frame, 0 title-text-overflow, 0 line-through-symbol.
- P-04: 1 line-crossing (accepted, unchanged), otherwise 0.

The `drawing-clean` gate passes.

Read: P-03 crop build/P-03_crop-50-95-120-160.png and the 106d6fb crop
build/P-03@106d6fb_crop-50-95-120-160.png (E-3105, HV-3127 / HV-3128 / HV-3129, TICA-3124 /
TV-3124 F.O., AIR-3002 DN 200, E-3104). Not read: the other tiles; no other object on P-01 .. P-04
changed since review13.

## Layout
- `cheme layout build --check`: "layout/plant-model.yaml is up to date". Its diff since 106d6fb
  is two input fingerprints (control/instrument-list.yaml, pid/P-03.xml), no geometry.
- `cheme layout lifting --check`: exit 0.

`cheme layout report` at e1ff49f, identical to review13:
- **Lines:** 81, all routed except 4 skipped segments (GAN-3002, LN-3002 D-028; two VNT-3004).
  0 unrouted. AIR-1004 133.9 m, AIR-2001 66.8 m, AIR-2002 72.9 m, WN-1002 6.9 m.
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

PNGs read (rendered at e1ff49f): build/layout-plan.png, build/layout-section-y68.png (along
PR1), build/layout-section-x133.png (rendered; through CB-1 / compander). Nothing in the layout
geometry changed since review13, and the plan and the PR1 section show the same routes.

## Checked and fine
- **D-088 (1):** the K-1101 hold text agrees with the computed section 10 (17.1 / 21.1 kPa,
  -0.055 / -4.11 kPa) and section 1 (8,121.3 kW at 110 %, +10.8 %). 4.11 kPa x 6.74 kW/kPa
  = 27.7 kW.
- **D-088 (2):** run record and unit results (above). The 4 `process-sim-deviation` warnings
  (S10 / S11) are the simulation owner's and unchanged.
- **D-088 (4):** the timing (above); the C-1101 datasheet, the I-03 notes, the LSLL-1115 notes and
  DESIGN.md give the same levels and times. Every assumed value is marked ASSUMED with its basis and
  for HAZOP / LOPA / SRS confirmation. The double failure (inflow lost) is still covered by the
  15 s response.
- **D-088 (5):** the crop (above).
- **Owner files:** flowsheet.yaml, simulation.yaml and design-basis.yaml unchanged; no fill was
  run.
- **Licence rule:** the new texts give values and sources in their own words; no third-party
  table or figure copied; no commercial downstream product named.
- **Stage gates:** no stage sign-off was written; `checks/status.json` is untouched.

## Not checked
- **The front-end budget (#2) and S12D (review13#3):** for the simulation owner.
- **The suppliers' drops:** adsorber, F-2101, E-2101, S-2101, FV-2105.
- **I-03 SRS, HAZOP / LOPA confirmation, the LV-1114 trim and the XV-1115 stroke, surge in
  CHWR-1001 at a 5 s closure:** for the HAZOP team, the valve supplier and the piping engineer.
- **The chimney tray levels, riser fraction, downcomer and the N7 vortex breaker:** for the
  packing supplier.
- **TSA top piping, tank nozzles, PR1 walkway for XV-3105, pipe stress, supports and PSV tailpipe
  guides, B1 crane, vent and inert study:** as in review13, with the same owners.
- **The P&ID tiles not named under Drawing.**
