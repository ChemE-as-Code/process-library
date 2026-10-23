---
topic: layout
reviewed_commit: ac934cd6d2f863fc665276673fb6e30f352f25f8
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, checks/checks.yaml, control/cause-effect.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: ac934cd6d2f863fc665276673fb6e30f352f25f8, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: ac934cd6d2f863fc665276673fb6e30f352f25f8, relation: depends-on}
  - {path: DESIGN.md, revision: ac934cd6d2f863fc665276673fb6e30f352f25f8, relation: depends-on}
  - {path: scripts/datasheet_sizing.py, revision: ac934cd6d2f863fc665276673fb6e30f352f25f8, relation: analyses}
  - {path: process/flowsheet.yaml, revision: ac934cd6d2f863fc665276673fb6e30f352f25f8, relation: analyses}
  - {path: process/simulation.yaml, revision: ac934cd6d2f863fc665276673fb6e30f352f25f8, relation: analyses}
reviewer: Claude (independent review agent; did not author D-072 .. D-078, the layout files, the datasheets or the P&ID changes)
reviewer_kind: agent
branch: pass-d066
merge: pending
---
# Review: layout, twelfth review (independent) after review11, D-072 .. D-078

This is an independent layout, datasheet and P&ID-consistency review of branch `pass-d066` at
ac934cd. It follows reviews/2026-10-23-layout-review11.md (6f42809, recorded in b9f1970) and
covers the merge of origin/main (#24, beac40d) and the seven fix commits:
- 6c542ec D-072 (regeneration-gas path);
- 3103b9f D-073 (main air lines, front-end pressure budget);
- 98015a5 D-074 (chilled-water runs off the K-4102 pad, supports, LIN-3001 post, PR3 north end);
- 6c881e9 D-075 (B1 crane 50 t, K-4101 motor 2.5 MW);
- b3353ae D-076 (LSLL-1115 / XV-1115, chimney-tray overflow, tray drawn, labels);
- 7dd0bd2 D-077 (E-3105 standstill, HV-3126, nozzles);
- ac934cd D-078 (figures and citations).

The reviewer designed none of this. cheme-as-code is the global `cheme`. Coordinates are site
metres from `layout/plant-model.yaml`. "Computed" means `cheme run scripts/datasheet_sizing.py`
or `cheme run scripts/support_steel_scan.py` run at ac934cd (output kept in build/, not committed).

`cheme diff 6f42809 --list` (P&IDs):
- P-01 adds LSLL-1115, XV-1115 with its actuating system; C-1101 gains I4 and the chimney tray;
  CHWR-1001 gains XV-1115; LV-1114 actuator and TV-1105 labels move; shape catalogue +4;
- P-02: AIR-2001 / AIR-2002 DN600, RG-2001 DN600, RG-2002 / RG-2003 DN700 with their tees,
  valves (XV-2102A/B, XV-2103A/B, XV-2104A/B, XV-2109, FV-2105), nozzles (E-2101, F-2101,
  V-2101A/B, S-2101) and connectors;
- P-03 adds HV-3126 (L.O.) on CHWR-3001; AIR-2002 / RG-2001 DN, E-3101 nozzle, tees.

Verdict: **no critical or high finding is open**. All 14 review11 findings are closed with
evidence. Two parts of them that were not done are split off as new open findings (#1, #7). New
findings: two medium (#1, #7) and five low (#2 .. #6).

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-23-layout-review12#1 | DESIGN.md / datasheets | AIR-1004, AIR-2001, AIR-2002, K-1101, flowsheet S2 .. S4 | The front-end pressure budget is not closed. D-073 (3) shows that the routed lines from C-1101 to E-3101 take 33.5 kPa at DN600, before the adsorber bed and F-2101; section 10 of the script reproduces it (AIR-1004 to V-2101B 17.9 kPa, AIR-2001 5.8 / 7.0 kPa, AIR-2002 6.75 + 3.05 kPa). The flowsheet allows 10 kPa for S3 -> S4 for all of these together. D-073 (4) / (5) pass this to the simulation owner and the owner, which is the right owner. But the K-1101 datasheet, the MAC enquiry basis, still gives the outlet pressure as 5.8 bara (S2) with no hold or note pointing to D-073. The enquiry would therefore go out about 25-35 kPa short, worth about 170-240 kW (6.94 kW/kPa, section 10). The 9.0 MW motor still has margin (7,979 kW at 110 % + ~260 kW is below 9,000 kW), so this is not a safety issue. | medium | open | Simulation owner: set the S2 .. S4 pressures from D-073. Owner: decide DN600 / DN700. Until then, mark the K-1101 outlet pressure (and the V-2101A/B and F-2101 drops in adsorption) as a hold citing D-073 in the datasheets. |
| 2026-10-23-layout-review12#2 | layout | CB-1 casing opening AIR-2002 | The CB-1 penetration schedule in layout/structures.yaml (line 79) still declares the AIR-2002 opening for DN500: offset 7.75, 0.65 x 0.65 m, sill 7.95. With AIR-2002 at DN600 (D-073), the build places the penetration at (132.91, 47.1, 8.31) outside the declared opening and proposes offset 7.7, 0.75 x 0.75 m (plant-model.yaml line 101540, `review_needed: true`). New `cheme.layout-wall-penetration` info, CB-1/wall-north-15 (review11 counted 0). The layout-rules gate passes because it is an info. The cold-box vendor's sleeve schedule is taken from this list. | low | open | Update the AIR-2002 opening from the build's penetration (`cheme layout pin CB-1/AIR-2002`) and rebuild. |
| 2026-10-23-layout-review12#3 | P-01 | LSLL-1115 tapping on C-1101 | On P-01 the LSLL-1115 measuring line enters C-1101 inside the upper packed bed (at y 92 mm), above the LIC-1114 tapping and well above the drawn chimney tray. D-076 (1) and the layout put I4 beside I3 at 13.0 m on the chimney tray (equipment-placement lines 49-51; C-1101 datasheet I4). A reader of the P&ID would take the low-low switch as measuring in the bed. Crop build/P-01_crop-185-80-300-125.png. | low | open | Move the I4 nozzle and the LSLL-1115 measuring line down to the tray, beside LIC-1114 (the accepted crossing then needs its id and reason checked again). |
| 2026-10-23-layout-review12#4 | layout / datasheet | C-1101 I3, I4, N7, chimney tray | The level tappings I3 (LIC-1114) and I4 (LSLL-1115) are at 13.0 m. The chimney-tray draw-off N7 is at 13.4 m, 0.4 m higher. The tray floor elevation is not given anywhere (searched: the C-1101 datasheet, equipment-placement.yaml, D-069 / D-076). A tray-level tapping 0.4 m below the draw-off would be under the tray floor, in the gas below the tray, where it cannot see the tray level. Then LSLL-1115 could not detect a lost seal. The relation may only be a placement shorthand, but nothing states it. | low | open | State the chimney-tray floor and chimney-top elevations in the C-1101 datasheet. Put I3 / I4 between them (low tapping at the tray floor, high tapping below the chimney top) and N7 at the tray floor. Or record why the present elevations are right. |
| 2026-10-23-layout-review12#5 | P-03 / datasheet | E-3105 shell-side drain, water-side drain and vent | D-077 (1) makes a dry E-3105 shell-side low-point drain the restart permissive that protects E-3101. D-077 (2) has the water side drained "at E-3105 (the supplier's drain and vent)" before maintenance. Neither the shell drain nor the water-side drain and vent is drawn on P-03 (`cheme show E-3105`: nozzles N1 .. N4 only), and the E-3105 datasheet has no nozzle for them. A check that a procedure relies on needs a drawn, valved drain. | low | open | Draw the shell-side low-point drain (valve, capped or to a drain) and the water-side drain and vent on P-03, add the nozzles to the datasheet and placement, or record in a decision why they stay with the supplier. |
| 2026-10-23-layout-review12#6 | P-01 | WN-1002 label | On tile A3 the "WN-1002 DN 900" text stands left of the C-1102 vent, directly over the CHWR-1001 riser that enters the C-1102 top. It is about 10 mm from the vent line and closer to CHWR-1001, which has no label on that stretch. The lint counts 0 label-far-from-owner. Tile build/P-01_tile-A3.png. | low | open | Move the WN-1002 label beside the vent line above C-1102 (e.g. right of it, below the "to atmosphere" arrow). |
| 2026-10-23-layout-review12#7 | DESIGN.md / C-1102 | C-1102 blow-by relief case, I-03 SIL | Split from review11#4 (a). The bound is now computed: 91.6 t/h choked through the DN150 bore (script, "CHWR-1001 blow-by bound"), against 58.1 t/h design gas of C-1102 (design 1 barg). The SIF I-03 (LSLL-1115 -> XV-1115) is drawn with `sil: null`. Whether C-1102 / WN-1002 pass the blow-by without exceeding the design pressure, or the SIF is credited (and at which SIL), is still open (D-076 open). | medium | open | HAZOP / LOPA: decide the relief case (WN-1002 open vent capacity at 91.6 t/h against the C-1102 design pressure) and the SIL of I-03 before the basic-engineering sign-off. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-23-layout-review11#1 | regeneration-gas path missing from the LP-top check | medium | closed 6c542ec | Script section 11 at ac934cd: tee at 115 - 3.57 = 111.4 kPa(a); bed B lines DN600 / DN700 / DN700 4.56 kPa + allowables FV-2105 1.5, E-2101 1.0, V-2101A/B 1.5, S-2101 1.0 = 9.56 of 10.1 kPa, margin 0.55 kPa (bed A 4.4 kPa). The allowables are in the E-2101 / V-2101A / V-2101B datasheets, special-items S-2101 and the FIC-2105 instrument note. The P-02 DN texts read DN600 / DN700 (tile A1), with 0 DN mismatch in validate. |
| 2026-10-23-layout-review11#2 | AIR-2001 / AIR-2002 over 20 m/s; MAC interstage legs | medium | closed 3103b9f | Section 10: DN600 16.0 / 13.9 m/s (DN as the diameter). The line list marks AIR-1005 / AIR-1006 as MAC supplier sizing (D-073 (2)). The unclosed pressure budget is split off as #1. |
| 2026-10-23-layout-review11#3 | CHW-3001 / CHWR-3001 over the K-4102 crane pad | medium | closed 98015a5 | build/layout-plan_crop-125-20-165-70.png: the pair comes down at x 144.5 / 144.8, west of Z-PAD-A4N (x 146 .. 158), and runs at 2.7 m on posts (section build/layout-section-x144.6_crop-20-0-75-12.png). The crane-swing rule is requested from cheme-as-code (D-074 (1)); that request belongs to the tool, not this plant. |
| 2026-10-23-layout-review11#4 | chimney tray: blow-by, overflow, not drawn | medium | closed b3353ae | (b) the C-1101 datasheet `chimney_tray_overflow` gives 38 m3/h to the lower section; (c) the tray is drawn (crop build/P-01_crop-185-80-300-125.png); (a) LSLL-1115 / XV-1115 F.C. drawn and in C&E I-03. The relief case and SIL are split off as #7; the tapping drawing and elevations are #3 / #4. |
| 2026-10-23-layout-review11#5 | B1 crane 0.73 t margin | medium | closed 6c881e9 | building.yaml crane capacity_t 50. `cheme layout lifting`: K-1101 39.27 t against 50 t, "building crane 50 t carries it". |
| 2026-10-23-layout-review11#6 | K-4101 motor 2.3 MW without margin | low | closed 6c881e9 | electrical-list K-4101 power_kw 2500, assumed, D-075. TR-1 13.7 MVA (D-075 (2)). The `electrical` gate passes. |
| 2026-10-23-layout-review11#7 | E-3105 standstill leak path, no maintenance isolation | low | closed 7dd0bd2 | C&E I-04 (compander trip closes TV-3124). HV-3126 L.O. on CHWR-3001 on P-03 (tile B1). Restart permissive in D-077 (1). The undrawn drain it relies on is #5. |
| 2026-10-23-layout-review11#8 | E-3105 nozzles not counter-current | low | closed 7dd0bd2 | One-pass floating head (D-077 (3)). N1 / N2 at opposite shell ends, N4 east head / N3 west channel. validate cross-checks the datasheet nozzle locations against the layout model: no finding. |
| 2026-10-23-layout-review11#9 | Z-N2-V1B reaches PR3 north end | low | closed 98015a5 | D-074 (4): sign, O2 monitor, no work on PR3 north of y 105 during a bypass (zones.yaml basis). |
| 2026-10-23-layout-review11#10 | WN-3003 / AIR-1006 / D-071 figures, AIR-3007 label | low | closed ac934cd | WN-3003 note 20.3 kPa / 3.6 kPa. AIR-1006 note 767 kg/h. D-078 (1) corrects D-071's "24 kPa". No "AIR-3007" in the script; section 10 prints "AIR-3002 (to E-3105)" / "(after E-3105)". |
| 2026-10-23-layout-review11#11 | mixed datasheet citations | low | closed ac934cd | 0 "D-063 (5))" citations in E-4101 / E-4102 / K-4101. Section 2 values equal the run: stage 1 discharge 361.98 K, E-4102 439.71 kW. |
| 2026-10-23-layout-review11#12 | LIN-3001 post 0.025 m from CWR-4002 | low | closed 98015a5 | `cheme run scripts/support_steel_scan.py`: 294 declared supports and platforms, 0 steel pairs below 0.0 m, 0 pipe-support members below 0.1 m from a pipe they do not serve (1017 runs). |
| 2026-10-23-layout-review11#13 | TV-1105 / LV-1114 labels | low | closed b3353ae | Crop build/P-01_crop-185-80-300-125.png: "TV-1105" under its own valve, "F.C." beside the LV-1114 actuator. |
| 2026-10-23-layout-review11#14 | chilled-water runs unsupported | low | closed 98015a5 | 16 T-posts under the P-03 pair, posts pinned on P-01 (D-074 (2), D-076 (4)). The remaining CHWR-3001 P-01 3.5 m support-missing info is carried in review3#4. |
| 2026-10-22-layout-review3#2 | PSV tailpipes free above the valves | low | open | Unchanged: the guides wait for the stress analysis (D-050, D-062 (4)). |
| 2026-10-22-layout-review3#3 | layout-operability warnings | low | open | 9, unchanged (XV-2101A, XV-2102A / B, XV-2103A / B, XV-2111A, PV-4109, PV-4110, XV-3105). |
| 2026-10-22-layout-review3#4 | rack free spans and support missing | low | open | free-span 5, the same lines (CWR-1004, LOX-3001 S2, CW-4001, CWR-4002, GAN-4004). support-missing 17 (was 21): the chilled-water ones are gone except P-01 CHWR-3001 S1, 3.5 m ("no place clear of the other pipes"). |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | Unchanged; waits for the vendor drawing (D-050 / D-062 (4)). |

## Drawing
`cheme validate` at ac934cd: 0 errors, 47 warnings.
- P-01: 0 line-through-label, 2 line-crossing, 0 label-overlap, 0 label-far-from-owner,
  0 text-outside-frame, 0 title-text-overflow, 0 line-through-symbol. Both crossings are
  accepted in checks/checks.yaml:
  - CHWR-1001 over CHW-1001 (D-069 pocket reason);
  - new: the LSLL-1115 measuring line over CHW-1001 (D-076). The reason holds for the line as
    drawn, but the tapping position is #3.
- P-02: 0 in each count.
- P-03: 3 line-crossing (accepted, unchanged), otherwise 0.
- P-04: 1 line-crossing (accepted, unchanged), otherwise 0.

The `drawing-clean` gate passes.

Tiles read:
- P-01 (`--tiles 3x2 --findings`):
  - A2: C-1101 with the chimney tray, LIC-1114 / LV-1114 F.C., the LSLL-1115 line, TV-1105 /
    TIC-1105 and the two accepted crossings;
  - A3: XV-1115 F.C. upstream of the CHWR-3001 tee, C-1102, WN-1002 (#6);
  - crop build/P-01_crop-185-80-300-125.png.
- P-02 (`--tiles 2x2`): A1, with AIR-2001 DN 600, RG-2002 DN 700, RG-2001 DN 600, FV-2105,
  XV-2103A, E-2101.
- P-03 (`--tiles 3x2 --findings`):
  - A1: AIR-2002 DN 600, E-3105 with TICA-3124 / TV-3124 F.O.;
  - B1: E-3104, HV-3126 L.O. on CHWR-3001, the CHW-3001 / CHWR-3001 connectors.

Not read: P-01 A1 / B1 / B2 / B3, P-02 A2 / B1 / B2, P-03 A2 / A3 / B2 / B3. Their changes are DN
texts and tees, which validate compares with the line list (0 DN mismatch) and `cheme.label-literal`
(0).

Engineering checks on the changed sheets:
- `cheme show LSLL-1115` senses at C1101_I4 and actuates XV-1115 through
  XV1115_ActuatingSystem. XV-1115 is a ball valve on CHWR-1001 between LV-1114 and the CHWR-3001
  tee, so the E-3105 return stays open to C-1102 as D-076 says.
- `cheme show HV-3126`: a ball valve in CHWR-3001 S1, labelled L.O.
- I-03 and I-04 are in control/cause-effect.yaml with matching tags and sheets. Both have
  `sil: null` (#7 for I-03; I-04 is stated as not a SIF).

## Layout
- `cheme layout build --check`: "layout/plant-model.yaml is up to date".
- `cheme layout lifting --check`: exit 0. Lifting: 15 lifts, every lane clear. K-1101
  39.27 t on the 50 t B1 crane. K-4102 from Z-PAD-A4N 38.5 t needed, lane clear.

`cheme layout report` at ac934cd:
- **Lines:** 81, all routed except the 4 skipped segments (GAN-3002, LN-3002, D-028; the two
  VNT-3004 breather segments). 0 unrouted. RG-2001 131.2 m, RG-2002 52.1 m, RG-2003 74.3 m,
  AIR-2001 66.8 m, AIR-2002 72.7 m, CHW-3001 152.1 m, CHWR-3001 150.2 m, CHWR-1001 78.7 m.
- **Chains per method:** astar 29, open 8, pinned 155, rack 15. No `direct` and no
  `rack+direct`.

  | reason | chains |
  |---|---:|
  | local: above the pipe-way | 7 |
  | local: pipe-way | 6 |
  | local: pump run at grade | 4 |
  | local: rack detour too long | 2 |
  | local: rack run too short | 1 |
  | local: short run | 9 |
  | open end | 8 |
  | pinned | 155 |
  | rack: battery limit at a rack end | 13 |
  | rack: longer than local_max_m | 2 |

- **Rack fill:**

  | rack | 5 m | 6.5 m | 7 m | 8.5 m | 9 m |
  |---|---:|---:|---:|---:|---:|
  | PR1 | 61 % (4.90 of 8 m) | | 47 % (3.75 of 8 m; was 44 %, AIR-2002 DN600) | | 25 % |
  | PR2 | | 6 % | | 6 % | |
  | PR3 | | 48 % | | 43 % | |

- **Model findings per rule:**

  | rule | count |
  |---|---|
  | clash-*, headroom, access-blocked, ladder-clearance, walkway-riser, steel-in-way, support-stub | 0 each |
  | zone-crossing, separation, vent-outlet | 0 each |
  | escape-ways, escape-travel, landing-width, egress-zone, operator-unknown | 0 each |
  | lifting, laydown, pad-overlap, spacing, building-spacing, zone-source | 0 each |
  | wall-penetration | 1 info (AIR-2002 into CB-1, new: #2) |
  | tier | 1 (WN-1001 3.0 m under the 7 m tier, accepted, D-071 (3)) |
  | access-enclosed | 1 (accepted) |
  | operability | 9 (review3#3) |
  | free-span | 5 (review3#4) |
  | support-missing | 17 infos (review3#4) |
  | tray-span | 17 (accepted) |
  | tray-zone | 6 (2 accepted, 4 infos) |
  | tray-separation | 1 (accepted) |
  | nozzle-unconnected | 2 infos (D-028) |

- **Objects:**
  - 46 equipment items;
  - 69 generated and 155 pinned pipes;
  - 118 generated in-line items;
  - 8 declared platforms;
  - 11 declared and 9 generated structures;
  - 30 declared zones.
- **validate:** 0 errors, 47 warnings:
  - 13 instrument-no-interlock;
  - 12 template-metadata;
  - 9 layout-operability;
  - 5 layout-free-span;
  - 6 line-crossing (P-01 2, P-03 3, P-04 1);
  - 2 titleblock-sheet.

  The one more than review11 is the accepted LSLL-1115 crossing.
- **`cheme check`** (before this record): every gate passes except `layout-review`, which this
  record is meant to make current.

PNGs read (build/, rendered at ac934cd):
- build/layout-plan.png (plot plan);
- build/layout-plan_crop-125-20-165-70.png (cold box, E-3104 / E-3105, the chilled-water pair
  at x 144.5 / 144.8 with its posts, Z-PAD-A4N, K-4102);
- build/layout-section-y68.png (along PR1);
- build/layout-section-x133.png (through the compander, E-3104 / E-3105 and the cold box CB-1);
- build/layout-section-x144.6_crop-20-0-75-12.png (the chilled-water drop from the PR1 5 m tier
  and the run south at 2.7 m on its T-posts; the T-post crossbars top out at 2.57 m under the DN50
  pair at 2.7 m, leaving room for shoes. The shoe height is for the stress engineer).

**Support steel:** `scripts/support_steel_scan.py`, 294 declared supports and platforms: 0 steel
pairs below 0.0 m and 0 members within 0.1 m of a pipe they do not serve.

## Checked and fine
- **D-072:** the hydraulics reproduce from the script (above). Velocities are inside D-016's
  25 m/s (14.3 / 17.7 / 18.5 m/s). The Ergun screening, 0.78 kPa for an ASSUMED 1.5 m bed, is
  inside the 1.5 kPa allowable. The double count of FV-2105 / S-2101 (an extra K in the line and
  an allowable as well) is conservative.
- **D-073:** the line table equals section 10. The 33.5 kPa is the bed-B path (17.9 + 5.8 + 9.8).
  The 6.94 kW/kPa is pro rata to ln(p2/p1) of E1. AIR-1004 at DN600 runs at 15.6 m/s, inside
  D-016.
- **D-075 TR-1:** (9,000 + 2,500 + 315) / (0.9 x 0.96) + 2,500 = 16.2 MVA, x 0.85 = 13.7 MVA,
  under 16 MVA.
- **D-076:** the blow-by bound 1364 kg/(m2 s) x 0.01865 m2 = 91.6 t/h (script). The overflow of
  38 m3/h = (34.4 + 0.24) x 1.1.
- **D-077:** with R = (30 - 15) / (20 - 10) = 1.5 and P = 10 / 20 = 0.5, the 1-2 F-factor has no
  real solution, so one pass is needed. The nozzle swap and the AIR-3002 S7 pin at 2.5 m under the
  compander lane are in the model. K-3101 stays on Z-PAD-A3S in the lifting study.
- **Licence rule (#24):** the new decisions and datasheet texts cite sources and give values in
  their own words. No copied third-party tables or figures were found in the changed files.
- **Stage gates:** no stage sign-off was written, and `checks/status.json` is untouched.

## Not checked
- **`cheme process simulate --check`** was not rerun. The simulation values were taken as the
  sizing script prints them. The flowsheet's S12A at 1.10 bara against the 111.4 kPa(a) tee
  (D-072 open) is for the simulation owner.
- **The front-end pressure profile (#1):** for the simulation owner and the owner.
- **The suppliers' drops:** E-2101, the adsorbent bed in both steps, S-2101, F-2101 and FV-2105.
- **The C-1102 blow-by relief case and the SIL of I-03 (#7):** for the HAZOP / LOPA.
- **The chimney tray and downcomer design:** for the packing supplier.
- **The E-3105 floating head, drain and vent:** for the supplier (#5).
- **The motor weights and the K-4101 motor rating:** for the motor and compressor suppliers.
- **The B1 50 t crane girders and runway:** for the structural engineer.
- **Pipe stress, shoes and guides of the new posts, and the PSV tailpipe guides:** for the stress
  engineer.
- **The crane outrigger and swing envelope around Z-PAD-A4N:** no rule tests it. The chilled-water
  pair is 1.2 m west of the pad edge, measured from the plan only. The lifting plan (competent
  person) must confirm the outrigger spread.
- **The vent and inert study** (Z-N2-V1B, Z-N2-WN1002, D-031): for a competent person.
- **The P&ID tiles not named under Drawing.**
