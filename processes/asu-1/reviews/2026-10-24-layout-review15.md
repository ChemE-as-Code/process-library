---
topic: layout
reviewed_commit: 468ad5a62b14486d46d9ad2909dcafb434766325
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, checks/checks.yaml, control/cause-effect.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 468ad5a62b14486d46d9ad2909dcafb434766325, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: 468ad5a62b14486d46d9ad2909dcafb434766325, relation: depends-on}
  - {path: DESIGN.md, revision: 468ad5a62b14486d46d9ad2909dcafb434766325, relation: depends-on}
  - {path: scripts/datasheet_sizing.py, revision: 468ad5a62b14486d46d9ad2909dcafb434766325, relation: analyses}
  - {path: process/simulation-run.json, revision: 468ad5a62b14486d46d9ad2909dcafb434766325, relation: analyses}
  - {path: process/flowsheet.yaml, revision: 468ad5a62b14486d46d9ad2909dcafb434766325, relation: analyses}
  - {path: process/simulation.yaml, revision: 468ad5a62b14486d46d9ad2909dcafb434766325, relation: analyses}
  - {path: estimate/tea.md, revision: 468ad5a62b14486d46d9ad2909dcafb434766325, relation: analyses}
reviewer: Claude (independent review agent; did not author D-089, D-090, the layout files, the datasheets or the P&IDs)
reviewer_kind: agent
branch: asu-d090
merge: pending
---
# Review: layout, fifteenth review (independent) after review14, D-089 and D-090

This is an independent review of branch `asu-d090` at 468ad5a. The branch is stacked on
`stage/basic-front-end-margin` (PR #30), and both are on top of main 5788cb7. It covers four
commits since review14 (9804084) that touch the plant:
- 543e898 D-089 (front-end budget 32 kPa, S3 5.92 / S2 6.02 bara, S12D on the simulated water);
- bfe0422 D-089 (simulation run record from the clean tree);
- 98218e4 D-090 (1) (lists, datasheets, electrical list, layout model on the D-089 state);
- 468ad5a D-090 (2) (equipment estimate, TEA and LCA rerun).

Merge commits d671dfd / 5788cb7 (PR #25, TEA) arrived from main and are not reviewed here.
cheme-as-code is the global `cheme` 0.7.0 (core main, pyDEXPI 2.1.0). "Computed" means
`cheme run scripts/datasheet_sizing.py` at 468ad5a (output not committed).
process/flowsheet.yaml, process/simulation.yaml and process/design-basis.yaml change only in the
D-089 commits (the simulation owner's). checks/status.json is unchanged.

`cheme diff main --list`: no P&ID item changed. process/BFD.xml and process/PFD.xml change in
the provenance note, energy flows (E1, E4, E5, Q1 .. Q5) and stream states only (D-089).
`git diff main HEAD -- pid/` is empty. Not drawn: none.

Verdict: **no critical, high or medium finding is open**. Review14#2 and review13#3 are closed.
Review14#1 stays open. There are two new low findings: #1, a generated output that is not
current, and #2, the rounding remainder of the D-089 budget.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-layout-review15#1 | layout | layout/lifting-study.md | Generated output not current. 98218e4 rebuilt layout/plant-model.yaml (two cable `basis` texts and input fingerprints), so the model's output_sha256 went from 2c068fe9... to ddd97ca3.... layout/lifting-study.md still quotes 2c068fe9.... `cheme layout lifting --check` at 468ad5a exits 1 ("layout/lifting-study.md is not current"). A trial `--write`, reverted afterwards, changes only that fingerprint line, so no lift value moves. No gate and no validate rule catches this, so `cheme check` passes. | low | open | Run `cheme layout lifting --write` and commit it on its own (fingerprint only), with a PROGRESS.md row. |
| 2026-10-24-layout-review15#2 | DESIGN.md / flowsheet S2, S3 | front-end budget at the bound | D-089 sets S3 -> S4 to 32 kPa with "the DN700 main air lines ... at their bound, 21.1 kPa". The S3 source in flowsheet.yaml says the same. But 21.1 + bed 8 + F-2101 3 = 32.1 kPa. Computed section 10: "the bound 21.1 kPa: margin -0.107 kPa" (routed lines 16.9 kPa: +4.06 kPa). D-090 (1) records this as "noted, not acted on" (~0.7 kW at the MAC, below the accuracy of the ASSUMED allowables). Neither D-089 nor the flowsheet source says that the bound is covered only to within 0.1 kPa, and nobody has accepted the shortfall. | low | open | Simulation owner, on PR #30: either state in D-089 and the S3 source that the bound case is 32.1 kPa, covered to within 0.1 kPa (accepted, with the reason), or set S3 -> S4 to 32.1 kPa (S2 ~6.021 bara). |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-layout-review14#2 | front-end budget short at S3 -> S4 28 kPa (-0.055 / -4.11 kPa), D-080 (1) unanswered, K-1101 on HOLD | low | closed 98218e4 | 543e898 (D-089) answers D-080 (1): S3 -> S4 32 kPa, S3 5.92 / S2 6.02 bara in flowsheet.yaml. 98218e4 lifts the hold: K-1101.yaml `outlet_pressure` 6.02 bara citing D-089. Computed section 10: routed DN700 16.9 + 8 + 3 = 27.9 kPa against 32 kPa, +4.06 kPa. The remaining -0.107 kPa at the bound is split off as new #2. |
| 2026-10-24-layout-review13#3 | S12D fractions sum 1.0000012; S12D water 143.1 vs TSA 165 kg/h | low | closed 543e898 | S12D in flowsheet.yaml: 18,696 kg/h, N2 0.9230308 + O2 0.0504434 + Ar 0.0122656 + H2O 0.0119348 + CO2 0.0023254 = 1.0000000. 18,486 + 142.1 + 67.7 = 18,695.8 kg/h. Validate no longer gives the 2 `pydexpi_composition_fractions` warnings (35 -> 33). The water basis is resolved by D-089: the simulated 142.1 kg/h is used for the balance, and the beds stay sized on 165 kg/h. V-2101A/B state this margin (0.7 % above IAPWS-95 163.9 kg/h at 5.92 bara, 16 % above PR 142.1 kg/h), which agrees with computed section 8 ("water 163.9 kg/h (flowsheet x_H2O 0.00206, PR: 142.1 kg/h)"). |
| 2026-10-24-layout-review14#1 | LV-1114 2 x normal capacity limit and N7 vortex breaker not on the entries the suppliers read | low | open | Unchanged at 468ad5a. The LIC-1114 instrument-list entry still names only "LV-1114 (fail closed)", and C-1101 nozzle N7 (DN150, side, 13.0 m) names no vortex breaker. The C-1101 `chimney_tray_sif_basis` now gives "2 x the normal 34.4 m3/h (69 m3/h, a rating requirement on its trim)", and computed I-03 gives LV-1114 full open 68.88 m3/h. |
| 2026-10-22-layout-review3#2 | PSV tailpipes free above the valves | low | open | Unchanged: the guides wait for the stress analysis (D-050, D-062 (4)). |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | Unchanged; waits for the vendor drawing (D-050 / D-062 (4)). |

## Drawing
`cheme validate` at 468ad5a gives 0 errors and 33 warnings:
- 13 instrument-no-interlock;
- 12 template-metadata;
- 6 line-crossing;
- 2 titleblock-sheet.

The 2 `pydexpi_composition_fractions` warnings of review14 are gone (review13#3).

Counts per sheet:
- P-01: 0 line-through-label, 2 line-crossing (accepted: D-069, D-076), 0 label-overlap,
  0 label-far-from-owner, 0 text-outside-frame, 0 title-text-overflow, 0 line-through-symbol.
- P-02: 0 in each count.
- P-03: 0 line-through-label, 3 line-crossing (accepted, unchanged), 0 label-overlap,
  0 label-far-from-owner, 0 text-outside-frame, 0 title-text-overflow, 0 line-through-symbol.
- P-04: 1 line-crossing (accepted, unchanged), otherwise 0.

The `drawing-clean` gate passes. No P&ID changed since review14, so no tile was read (see Not
checked).

## Layout
- `cheme layout build --check`: "layout/plant-model.yaml is up to date". Its diff since bfe0422
  is five input fingerprints (instrument, electrical, equipment and line lists,
  special-items) and two cable `basis` texts (C-M-P-1101A, C-M-P-1102A, from the electrical
  list). No geometry changed.
- `cheme layout lifting --check`: **exit 1**, lifting-study.md not current (new #1).

`cheme layout report` at 468ad5a, identical to review14:
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

PNGs read (rendered at 468ad5a): build/layout-plan.png, build/layout-section-y68.png (along
PR1) and build/layout-section-x133.png (through CB-1 / compander). They show the same routes,
racks, structures and zones as in review14. Nothing in the layout geometry changed.

## Checked and fine
- **D-089 results against the run record:** `cheme process simulate --check` at 468ad5a gives
  K1101 7,287.56 kW / cooling 7,728.05 / shaft 6,894.03 kW, C1101 -699.498 kW, C1101U
  -634.277 kW, K4101 2,262.49 kW, K4102 237.669 kW. These equal D-089, D-090 (1) and the sizing
  script, which reports "run ... at 543e898; current with process/*.yaml". The S10 / S11
  `process-sim-deviation` warnings are the simulation owner's and unchanged.
- **Notes on D-089 in D-090 (3):** these are the two low findings of the D-089 review.
  - +27.8 kW electric (7,287.56 - 7,259.77) and +26.3 kW shaft (6,894.03 - 6,867.74) are right.
  - S2 H2O is 0.0112061 in flowsheet.yaml, so the section 3 table's 1.11 mol% should read
    1.12, as D-090 (3) says.
  - D-089 itself is left to PR #30's owner, which is correct.
- **D-090 (1) against computed values:**
  - **K-1101:** ratio 1.844 per stage, gas power 6,909.9 kW; 7,640.5 kW pro rata at
    90,000 Nm3/h, 7,411.3 kW motor output, 8,152.4 kW at 110 % against 9,000 kW (+10.4 %).
  - **MAC coolers:**
    - E-1101: 1,941 kW, 396.1 m2, CW 167.9 m3/h.
    - E-1102: 2,877 kW, 607 m2 by zones, 808.1 kg/h condensed, 248.9 m3/h.
    - E-1103: 2,797 kW, 557.4 m2 by zones, 726.4 kg/h condensed, 242.0 m3/h.
    - In all 7,614.2 kW.
  - **C-1101:** S3C / S3CU 411.5 / 228.3 kg/h; F 0.953 Pa^0.5.
  - **C-1102 loop:** 39.55 m3/h, 697.55 kW; P-1102 rating 111.2 % of the loop.
  - **Pumps:** P-1101A/B 33.28 / 34.13 m, 30.13 / 30.91 kW; P-1102A/B 77.97 / 78.06 m,
    12.46 / 12.47 kW.
  - **Blow-by:** bound 95.1 t/h; WN-1002 3.01 kPa + 22.6 kPa = 25.6 kPa(g) against 1 barg
    (3.9 x).
  - **I-03:** 148 / 144 / 72 s unchanged; inflow 34.44 m3/h.
  - **Front end:** +4.06 / -0.107 kPa (#2).
  - **Agreement:** the K-1101, E-1101 .. E-1103, C-1101, V-2101A/B, P-1101A/B and P-1102A/B
    datasheets, the equipment-list notes (K-1101, C-1101, P-1102A) and the electrical-list
    entries (K-1101, P-1101A, P-1102A) carry these values. The B pumps are "as A".
  - **Stale values:** a grep for 5.98 / 5.88 / 7,260 / 6,868 / 8,121 finds them only as "was"
    or "D-079" history.
- **TR-1:** (7.29 + 2.26 + 0.24 + 1.4) MW / 0.9 = 12.4 MVA, 78 % of 16 MVA; the rating is
  unchanged.
- **D-090 (2):** `cheme assess equipment --check`, `assess tea --check` and `assess lca --check`
  report their outputs current. TEA power 10,436.9 + 27.8 = 10,464.7 kWh/h.
- **Owner files:** flowsheet.yaml, simulation.yaml and design-basis.yaml are unchanged by D-090
  (98218e4, 468ad5a). `cheme process props --check` writes nothing; its warnings (H2O outside
  the property method's range, S4C temperature) are unchanged.
- **Gates:** `cheme check --no-write` passes 30 gates and fails only `layout-review`, which
  waited for this record.
- **Repository CI, run locally from the worktree root:**
  - `cheme fmt --check` exit 0, `cheme validate` exit 0 (0 errors);
  - library pytest: 74 passed;
  - build_catalog: 1 process (warnings: no preview for P-04, BFD, PFD); `--public`: 0 processes;
  - build_lci `--strict`: 4 activities from 1 process, written to the session scratchpad
    `ci-d090`.
- **Licence rule:** the new texts give values and sources in their own words. No third-party
  table or figure is copied and no commercial downstream product is named.
- **Stage gates:** no stage sign-off was written, and `checks/status.json` is untouched.

## Not checked
- **D-089 itself** (flowsheet, simulation specs, BFD / PFD content): the review of PR #30.
  Only the values D-090 takes from it were compared.
- **The suppliers' pressure drops** (adsorber, F-2101, E-2101, S-2101, FV-2105): D-089 open
  item. Above the ~11 kPa assumed, S2 rises at ~6.9 kW/kPa.
- **TEA and LCA premises:** the D-082 premises and the LCA factors (still the example). Only
  the rerun currency and the power delta were checked.
- **I-03 SRS, HAZOP / LOPA, LV-1114 trim, XV-1115 stroke, chimney tray levels, N7 vortex
  breaker:** for the HAZOP team, the valve supplier and the packing supplier.
- **TSA top piping, tank nozzles, PR1 walkway for XV-3105, pipe stress, supports and PSV
  tailpipe guides, B1 crane, vent and inert study:** as in review14, with the same owners.
- **P&ID tiles:** none read, since no sheet changed.
