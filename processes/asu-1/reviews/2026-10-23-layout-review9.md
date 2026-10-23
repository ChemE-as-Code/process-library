---
topic: layout
reviewed_commit: ba79cf7c8dd965f1d568a11fa5447d70b8f230eb
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, checks/checks.yaml]
basis:
  - {path: equipment/equipment-list.yaml, revision: ba79cf7c8dd965f1d568a11fa5447d70b8f230eb, relation: depends-on}
  - {path: DESIGN.md, revision: ba79cf7c8dd965f1d568a11fa5447d70b8f230eb, relation: depends-on}
  - {path: process/flowsheet.yaml, revision: ba79cf7c8dd965f1d568a11fa5447d70b8f230eb, relation: depends-on}
reviewer: Claude (independent review agent; did not author D-055, D-060, the layout files or the fixes since e2c43ea)
reviewer_kind: agent
branch: issue8
merge: pending
---
# Review: layout, ninth review (independent) after review8, D-055 and the issue #8 round (D-060)

This is an independent layout review of branch `issue8` at ba79cf7. It follows
reviews/2026-10-23-layout-review8.md (e2c43ea) and covers:
- D-055 (1) .. (10), the fixes of review8 (15fd70f .. c1890ce, merged to main in a661950);
- D-060 (1) .. (7) on this branch (b75043f .. ba79cf7):
  - the core#66 rebuild;
  - the pinned support proposals;
  - the pump heads;
  - the datasheet markers;
  - the compander / E-3101 analysis (not applied to the flowsheet);
  - the remote operators.

The reviewer designed none of this. cheme-as-code ran from the core worktree `fix/core-66`
(f052dd8). Coordinates are site metres from `layout/plant-model.yaml`. Distances marked
"computed" come from scratch scans of the model, kept outside the repository:
- every support-steel member (declared and generated) against every pipe it does not serve,
  as a clear gap from the pipe's outer surface with insulation to the steel face;
- every declared structure part (members, stair flights and landings) against the equipment
  boxes and against the roads to 5 m;
- every open pipe end against every grating (in plan and in height);
- the equipment boxes pairwise;
- what each `stub` support stands on;
- the free volume either side of the E-4101 package;
- the datasheet weights and dimensions against the equipment list.

`cheme diff main --list`: "No P&ID changed." No layout file was changed by this review.

Verdict: **no critical or high finding is open**. Every review8 finding is closed, and the
scans confirm each fix. New findings: one medium, four low.
- #1 (medium) comes from D-060 (2): four of the new GOX-4002 S12 supports are 6.6 .. 7.1 m
  columns that stand on the crossbars of the cooling-water T-posts. They are declared as
  `stub`s.
- #2 .. #5 (low):
  - #2: the lifting study prints a capacity needed above the B1 crane rating, and gives no
    verdict on it;
  - #3: the E-4101 package lost its bundle-pull envelope;
  - #4: the free-span warnings offer to pin proposals that cannot stand where they are;
  - #5: four datasheets and the CW-3001 size rest on states that the flowsheet does not have
    yet (owned by the parallel simulation work).

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-23-layout-review9#1 | layout | GOX-4002 S12 SP-8.9, SP-11.0, SP-15.4, SP-19.9; CW-4001 post-3, CWR-4001 post-4..6 | D-060 (2) pinned five supports for the DN 80 GOX backup tie-in GOX-4002 S12 at 10.4 m. Only SP-6.5 is a real stub: 0.49 m on the GOX-4002 S4 post-1 crossbar at 9.92 m. The other four are `kind: stub` columns 6.62 .. 7.12 m tall at x 180.8 (computed: base / top / what they stand on):<br>- SP-8.9: base 3.79 on the CW-4001 S1 post-3 crossbar, top 10.41;<br>- SP-11.0 / SP-15.4 / SP-19.9: base 3.29 on the CWR-4001 S1 post-4 / -5 / -6 crossbars, top 10.41.<br>Each stands on the end region of a 1 m HEB200 crossbar of a 3.3 / 3.8 m T-post that was laid out for one DN 100 water line. An oxygen line is then carried 7 m higher on that post: the crossbar takes a bending moment, and the T-post a wind and friction moment, that it was not drawn for. The VP-4 east columns (HEB400, x 180.12) stand 0.68 m west of these stubs over the same y range (52.0 .. 59.2). D-060 (2) leaves "that those posts carry the extra load" to the stress engineer. The model calls them stubs, so no rule tests their height or what they stand on. Section build/layout-section-x180.8_crop-44-0-66-12.png. | medium | open | Carry GOX-4002 S12 on brackets off the VP-4 east columns (y 52.0 .. 59.2) and on its own T-posts from grade north of VP-4, kept 0.1 m clear of CW-4001 / CWR-4001, or on a common frame over the water lines. Keep `stub` for short supports on steel that is sized for them. Ask cheme-as-code to report a stub taller than a limit (e.g. 1.5 m, ASSUMED) or one standing on another line's post. |
| 2026-10-23-layout-review9#2 | layout | K-1101 (heaviest part), B1 crane, lifting-study.md | The lifting study now lists the MAC motor (D-055 (7)): 30 t, gross 34.65 t, "needed t" 46.2, under `building B1`, status "building crane". The B1 crane is rated 40 t (layout/building.yaml). The study prints a needed capacity above the crane rating, and gives no verdict on it. The 46.2 t is the gross load divided by the 0.75 chart utilisation of a mobile crane. For an overhead crane, the rated capacity is compared with the gross load: 34.65 t ≤ 40 t, so the lift fits. D-055 (7) says so, but the generated study does not, and E-1101 .. E-1103 have the same blank. | low | open | Ask cheme-as-code to check building-crane lifts against `crane.capacity_t` with the gross load (no mobile-chart utilisation) and print the margin and a pass / fail status. Until then, note the comparison in D-034 / D-055 (7). |
| 2026-10-23-layout-review9#3 | layout | E-4101 | E-4101 became the four-shell intercooler package (D-055 (6), `shape: box`, x 163.5..169.5, y 37.1..39.9, 3.2 m). In this form the model generates no bundle-pull envelope for it. E-4102 and E-4103 still have theirs (E-4102/bundle_pull x 171.75..176.0). Each of the four shells is a removable-bundle shell-and-tube cooler of about 5 m (D-053 (2), D-055 (6)). Today the 6.5 m either side at 0..3.2 m is free (computed: no pipe or steel in x 157.0..163.5 or 169.5..176.0, y 37.1..39.9). Nothing keeps it free, and no rule would see a later route or post there. GOX-4001 runs north-south at x ≈ 162 only 1.5 m west of the package, above 3.2 m. Plan build/layout-plan_crop-155-22-190-52.png. | low | open | Declare a maintenance (keep-clear) zone for the E-4101 bundle pull on the side the package drawing will use, about 5.5 m x 2.8 m x 3.2 m (ASSUMED), and give the stacked pair its lift by Z-PAD-A4C, or record in D-055 (6) that the vendor's package sets the pull. |
| 2026-10-23-layout-review9#4 | layout | CW-4001 S1, CWR-4002 S1, GAN-4004 S1 free-span proposals | The `layout-free-span` warnings for CW-4001 S1, CWR-4002 S1 and GAN-4004 S1 say "proposed support steel: ... (cheme layout pin <id>)". The proposals they name carry "place it by hand" in their own `reason`. They stand in the line beside or below (computed clear gap):<br>- SP-163.2 / SP-166.5 columns -0.07 m into CWR-4001 S1;<br>- SP-7.8 crossbar -0.08 m into GAN-4002 S4;<br>- SP-9.5 column -0.18 m into GAN-4002 S4.<br>Pinning them as offered would declare steel through a pipe. The other generated proposals that cut pipes (AIR-3002 S4, LN-3001 S3, RL-3001 S2, LIN-4003 S1, GOX-4002 S5, GOX-4001 S1) are not offered in a warning text, and D-060 (2) records them all. | low | open | Ask cheme-as-code not to offer `cheme layout pin` for a "place it by hand" proposal in the free-span message. Plant: the five free spans stay under review3#4 (stacked runs, D-060 (2)). |
| 2026-10-23-layout-review9#5 | datasheets / line list | E-3101, K-3101, KT-3101, E-3104 datasheets; CW-3001 / CWR-3001 | Several items marked final do not match the current flowsheet:<br>- **E-3101 datasheet** (`draft: false`, D-060 (4)): its UA and minimum approach rest on cold outlets at 13 C, ASSUMED. The flowsheet still has S7 / S9 / S17 at 25 C, which the datasheet itself says the warm composite cannot reach.<br>- **K-3101 / KT-3101 / E-3104**: these stay on flowsheet states that do not balance the compander. D-060 (6) finds booster - 0.97² x expander = -32 kW.<br>- **CW-3001 / CWR-3001**: the line list gives ~5.1 m3/h at DN 150 (0.08 m/s).<br>The flowsheet changes (S4C / S4D 8.45 bara, S5B 8.25 bara / -124.7 C, S7 / S9 / S17 13 C) are requested in D-060 (6). `process/flowsheet.yaml` belongs to the parallel simulation work (D-058 / D-059), so the items stay inconsistent until then. With the balance, the E-3104 duty becomes 85 kW (~7.4 m3/h). | low | open | After the flowsheet changes: rerun `cheme process props --fill`, `simulate --fill` and `assess lca --write`, then redo the E-3101 composite curves and the K-3101 / KT-3101 / E-3104 datasheets. Size CW-3001 / CWR-3001 for ~7.4 m3/h (DN 50 at about 1 m/s) when the E-3104 supplier gives its nozzles, then update P-03, the line list and the routes together. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-23-layout-review8#1 | PSV-4128 outlet at chest height beside VP-9 | medium | closed 15fd70f | GAN-4003 S6 open end [181.57, 87.64, 13.8]: 5.21 m above the VP-9 grating (8.6 m), 0.46 m off its edge in plan (computed). Source of Z-N2-VENTS (zones.yaml). The zone sphere's underside (10.8 m) is at the walkway headroom (8.6 + 2.2 m). vent-outlet, egress-zone and separation: 0 (validate). The core#66 side-of-floor check (`vent_side_clearance_m` 1.5) finds nothing. Section build/layout-section-x181_crop-75-0-100-16.png, plan build/layout-plan_crop-170-78-192-96.png. |
| 2026-10-23-layout-review8#2 | nozzle locations missing on 12 datasheets | medium | closed e4240c5 | validate compares "datasheet nozzle locations vs layout model" and reports no `datasheet-nozzle-layout` finding. Core f052dd8 also reports missing locations. |
| 2026-10-23-layout-review8#3 | E-4101 sized as four coolers, laid out as one shell | medium | closed 409310e | List / datasheet / model 6 x 2.8 x 3.2 m, 24 t (ASSUMED). Box 3.1 m from FW-4101 and clear of Z-PAD-A4C (y 42) (`show E-4101 --layout`). Lifting study E-4101 24 t from Z-PAD-A4C at 7.91 m, 36.96 t needed, lane clear. No equipment box overlaps (computed). Side effect: #3 (no bundle-pull envelope). |
| 2026-10-23-layout-review8#4 | LOX / LIN pump suctions above the tank outlets | medium | closed 8624d29 | T-4101 / T-4102 on a 0.5 m plinth. LOX-4001 S1 level at 1.0 m from N4; S2 / S3 level to the pump, then down to 0.65 m and level into N1. LIN-4001 the same. No point rises towards a pump (model points). NPSHa +0.34 / +0.31 m on the datasheets. I-01 / I-02 in cause-effect.yaml. Section build/layout-section-y103_crop-115-0-160-14.png. |
| 2026-10-23-layout-review8#5 | PSV-4127 not a zone source | low | closed 15fd70f | GOX-4004 is a source in Z-O2-VENTS. Outlet [181.36, 90.6, 13.8], 1.58 m off VP-9 in plan and 5.21 m above it (computed). separation 0 (the zone edge is 10 m or more from R5, D-055 (2)). |
| 2026-10-23-layout-review8#6 | VP-3 stair foot in the K-4102 box | low | closed cdada11 | Base landing centre [159.55, 52.153], edge y 52.60, 0.90 m from the K-4102 box (y 53.5). No declared structure part in any equipment box (computed). Plan build/layout-plan_crop-145-44-165-62.png. |
| 2026-10-23-layout-review8#7 | eight pipe-to-foreign-post gaps under 0.1 m | low | closed ac9c615 | Smallest declared-steel gap now 0.100 m: GAN-4004 S1 post-1 crossbar to GAN-4003 S4, and LOX-4003 S3 SP-11.1 crossbar to LOX-4003 S1. No declared member under 0.1 m (computed over 258 declared supports). Generated proposals under 0.1 m: #4. |
| 2026-10-23-layout-review8#8 | generated platform ids unstable | low | closed b75043f | Core f052dd8 names the proposals by valve: VP-XV-2101A, -2102A, -2102B, -2103A, -2103B, -2111A, VP-PV-4109, VP-PV-4110, VP-XV-3105 (model, 9 generated structures). |
| 2026-10-23-layout-review8#9 | D-053 datasheet counts | low | closed c1890ce | D-053 / D-055 (10): 39 / 28 / 11, then D-060 (4) drafts 11 -> 4. 39 datasheet files; drafts C-3101, C-3102, E-3102, E-3103 (computed, datasheets gate). |
| 2026-10-23-layout-review8#10 | MAC motor not in the lifting study | low | closed 951b0a1 | K-1101 `lift_weight: 30` (ASSUMED). Study row "K-1101 (heaviest part)", 34.65 t gross under the 40 t B1 crane, lane clear. The study's own verdict on it: #2. |
| 2026-10-22-layout-review3#2 | PSV-3114 / PSV-3116 tailpipes free 4.5 m above the valves | low | open | Unchanged. The guides wait for the relief reaction forces of the stress analysis (D-050). The new PSV-4127 / PSV-4128 tailpipes (5.2 m over VP-9, D-055 (2)) are in the same state. |
| 2026-10-22-layout-review3#3 | layout-operability warnings | low | open | 14 -> 9 (b32f383, D-060 (7)): XV-4118, XV-4119, XV-4132, XV-4133 and PV-3110A are `remote_operator` to VP-4 / VP-5 / VP-1, runs 0.5 .. 2.6 m. Left: XV-2101A, XV-2102A / B, XV-2103A / B, XV-2111A (TSA), PV-4109 / PV-4110 (tank roofs), XV-3105. Each is actuated; per D-040 (4) the actuator and positioner are maintained from a mobile elevating work platform. |
| 2026-10-22-layout-review3#4 | rack free spans and support missing | low | open | free-span 8 -> 5 (8337d35: CWR-1004, LOX-3001 S2, CW-4001, CWR-4002, GAN-4004). support-missing 16 (10 accepted, D-049). The stacked runs need brackets or common frames (stress engineer). The pinned GOX-4002 S12 supports: #1. |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | D-050: waits for the vendor drawing; unchanged. |
| 2026-10-21-layout#1 | PSV-3114 / PSV-3116 outlets inside the casing | high | closed f2a7582 | As recorded in 2026-10-21-layout-rereview: the outlets are on the casing roof. VNT-3002 / VNT-3003 open ends now at 58.25 m, 5.27 m above RF (53 m) (computed). |
| 2026-10-21-layout#2 | CW-3001 / CWR-3001 through the cold box | high | closed f2a7582 | Pinned round the casing (routing.yaml); wall-penetration 0. |
| 2026-10-21-layout#3 | casing too low, WN-3001 over the roof | high | closed f2a7582 | Casing 53 m, WN-3001 inside it; section build/layout-section-x133.png. |
| 2026-10-21-layout#4 | RG-2003 vent near grade | high | closed f2a7582 | S-2101 placed, outlet at 6 m; vent-outlet 0. |
| 2026-10-21-layout#6 | VNT-4006 GOX bleed zone over R5 | medium | closed f2a7582 | Battery limits at x 176; separation 0. |
| 2026-10-21-layout#7 | LOX-3001 not on the oxygen tier | medium | closed f2a7582 | tier 0. |
| 2026-10-21-layout#10 | intake close to and downwind of R4 / R1 | medium | superseded by 2026-10-21-layout-rereview#4 | As recorded in the rereview. |
| 2026-10-21-layout#11 | no escape zones, single ladders above P10 | medium | closed f2a7582 | Z-ESC-CB1 declared; escape-ways, escape-travel 0. |
| 2026-10-21-layout#14 | E-2101 nozzle at grade | low | closed f2a7582 | RG-2001 S2 ends at 1.0 m (the nozzle override). |
| 2026-10-21-layout#17 | PR2 / PR3 lowest tier at the road headroom | low | closed f2a7582 | PR2 / PR3 tiers at 6.5 / 8.5 m; part (b) closed as 2026-10-21-layout-rereview#8 (c9fc8de). |

Note: review8 left the ten 2026-10-21-layout findings above out of its Previous findings
(`cheme.review-previous-missing` on review8). They are listed here with the statuses that
earlier records gave them.

## Drawing
No P&ID changed since e2c43ea (`cheme diff main --list`: "No P&ID changed"). validate counts:
- P-01: 0 line-through-label, 0 line-crossing, 0 label-overlap, 0 label-far-from-owner.
- P-02: 0 / 0 / 0 / 0.
- P-03: 3 line-crossing (accepted in the drawing gate; `drawing-clean` passes), otherwise 0.
- P-04: 1 line-crossing (accepted, as P-03), otherwise 0.

Tiles not read (no sheet changed).

## Layout
- `cheme layout build --check`: "layout/plant-model.yaml is up to date".
- `cheme layout lifting --check`: current, exit 0. A fresh `cheme layout lifting` leaves
  `layout/lifting-study.md` unchanged (model sha256 ab86fab1...).

`cheme layout report` at ba79cf7:
- **Lines:** 76 lines, all routed except 4 skipped segments: GAN-3002 and LN-3002 (double-column
  internals, D-028) and the two VNT-3004 casing breather segments. 0 unrouted.
- **Chains per method:** astar 30, open 8, pinned 147, rack 14. No `direct` and no
  `rack+direct`. Compared with review8: astar_coarse 2 -> 0, pinned 139 -> 147 (LOX-4001,
  LIN-4001 and GOX-4005 pinned in D-055).
- **Chains per reason:**

  | reason | chains |
  |---|---:|
  | local: above the pipe-way | 7 |
  | local: pipe-way | 7 |
  | local: pump run at grade | 4 |
  | local: rack detour too long | 2 |
  | local: rack run too short | 1 |
  | local: short run | 9 |
  | open end | 8 |
  | pinned | 147 |
  | rack: battery limit at a rack end | 13 |
  | rack: longer than local_max_m | 1 |

- **Rack fill:** unchanged from review8.

  | rack | 5 m | 6.5 m | 7 m | 8.5 m | 9 m |
  |---|---:|---:|---:|---:|---:|
  | PR1 | 61 % | | 37 % | | 25 % |
  | PR2 | | 6 % | | 6 % | |
  | PR3 | | 38 % | | 43 % | |

- **Model findings per rule:**

  | rule | count |
  |---|---|
  | clash-*, headroom, access-blocked, ladder-clearance, walkway-riser, steel-in-way | 0 each |
  | access-enclosed | 1 (E20, accepted) |
  | zone-crossing, separation, vent-outlet, wall-penetration, tier | 0 each |
  | escape-ways, escape-travel, landing-width, egress-zone, operator-unknown | 0 each |
  | lifting, laydown, pad-overlap, spacing, building-spacing, zone-source | 0 each |
  | operability | 9 (review3#3) |
  | free-span | 5 (review3#4, #4) |
  | support-missing | 16, 10 accepted (review3#4) |
  | tray-span | 17, each accepted by name |
  | tray-zone | 6: 2 accepted, 4 infos |
  | tray-separation | 1 (accepted) |
  | nozzle-unconnected | 2 infos (C-3101 N3 / N4, D-028) |
  | layout-line-length | 16 infos |

  Gaps in the 0 counts: the 0 for steel-in-way does not test what a `stub` stands on or how
  tall it is (#1); the 0 for maintenance does not cover E-4101 (#3).
- **Objects:**
  - 45 equipment items;
  - 67 generated and 147 pinned pipes;
  - 8 declared platforms;
  - 11 declared structures: CB-1, FW-TR, FW-4101, VP-1..VP-7, VP-9;
  - 9 generated platform proposals, `VP-<valve>`;
  - support steel: 251 declared T-posts, 7 declared stubs, 24 generated T-posts and
    5 generated stubs (proposals, `review_needed`).
- **validate:** 0 errors, 46 warnings:
  - 13 instrument-no-interlock;
  - 12 template-metadata;
  - 9 layout-operability;
  - 5 layout-free-span;
  - 4 line-crossing;
  - 2 titleblock-sheet;
  - 1 review-previous-missing (review8; this record lists the ids, and with it validate gives
    45 warnings).
- **`cheme check`:** every concept and basic gate passes except `layout-review` (review8 is
  stale; this record is meant to make it current). The detail gate `datasheets` fails on the
  4 drafts C-3101, C-3102, E-3102 and E-3103, which wait for D-059.
- **`cheme layout lifting`:**
  - 15 lifts, every lane clear;
  - heaviest mobile lift: K-4101, 45 t (51.98 t gross at 12.5 m from Z-PAD-A4), 69.3 t chart
    capacity needed;
  - E-4101: 24 t, 36.96 t needed at 7.91 m;
  - K-1101 motor: 34.65 t gross under the 40 t B1 crane (#2);
  - no crane chart (D-041 (7)).

**Datasheets against the layout, the list and the lifting study** (computed):
- Every `weight_t`, `diameter_m`, `height_m`, `length_m` and `width_m` on the 39 datasheets
  equals the equipment list's `dimensions` (no difference found), which the model and the
  lifting study use.
- Nozzle locations: no `datasheet-nozzle-layout` finding, missing or differing.
- The LOX / LIN pump heads (D-060 (5)) take their static head from the model:
  - T-4101/N4 at 1.0 m to E-4105A/N1 at 4.0 m;
  - the gas-line losses along the routed GOX-4004 / GAN-4003.

  Both are consistent with the current routes.
- Final datasheets on states the flowsheet does not have yet: #5.

**Remote operators (D-060 (7)):** the five declared operators are within the 6 m limit
(no operator-unknown, operability 9). XV-4118 is the GOX ESD block and XV-4133 the fail-open
bleed. Their override and air set reach a pedestal on VP-4 / VP-5. Per D-040 (4) the
actuator, solenoid and limit switches are maintained from a mobile elevating work platform.
Where that platform stands among the posts and stubs at x 176 .. 181, y 52 .. 66 is not
modelled (Not checked).

PNGs read (build/, rendered at ba79cf7):
- build/layout-plan.png (plot plan);
- build/layout-section-y68.png (along PR1);
- build/layout-section-x133.png (through the cold box and PR1);
- build/layout-section-y103.png and build/layout-section-y103_crop-115-0-160-14.png (LOX / LIN
  pumps; suctions falling to the pumps, review8#4);
- build/layout-plan_crop-170-78-192-96.png and build/layout-section-x181_crop-75-0-100-16.png
  (VP-9 with the PSV-4127 / PSV-4128 tailpipes to 13.8 m and their zones above the walkway
  headroom; review8#1, #5);
- build/layout-plan_crop-145-44-165-62.png (VP-3 stair foot clear of K-4102, review8#6);
- build/layout-plan_crop-155-22-190-52.png (E-4101 package, FW-4101, Z-PAD-A4C, GOX-4005
  through the sleeves; review8#3, #3);
- build/layout-section-x166.5_crop-25-0-50-12.png (K-4101, the 7 m fire wall, GOX-4005 through
  its sleeve at 3.66 m onto the E-4101 package top at 3.5 m);
- build/layout-section-x180.8_crop-44-0-66-12.png (GOX-4002 S12 stubs on the CW / CWR T-posts
  beside VP-4, #1).

## Checked and fine
- **Roads.** No declared structure part (members, stair flights, landings) in R1..R5 below
  5 m (computed).
- **Equipment.** No declared structure part in any equipment box. No two equipment boxes
  overlap, including the new E-4101 package and the plinth tanks (computed).
- **Declared supports.** Every declared support member is 0.10 m or more from every pipe it
  does not carry (computed). The seven D-060 (2) pins add no clash: clash 0, steel-in-way 0.
- **Open ends.** No open end lies within reach of a declared floor below the walkway headroom
  plus the zone radius (computed). The near cases:
  - VNT-3002 / VNT-3003 at 58.25 m, 5.27 m over RF;
  - PSV-4127 / PSV-4128 at 13.8 m, 5.21 m over VP-9;
  - AIR-1004 S2 at 26.46 m, 2.56 m above C-1101 platform-4 and 1.2 m off it in plan (the DCAC
    top vent; no O2 or inert zone; vent-outlet 0).

  The VNT-4001 / VNT-4005 ends beside VP-PV-4109 / VP-PV-4110 are next to generated
  proposals only, not declared floors.
- **Process.** No P&ID changed; D-060 does not touch the flowsheet (D-058 / D-059 ownership
  kept).

## Not checked
- Structural design:
  - the VP platforms;
  - the T-posts carrying the GOX-4002 S12 stubs (#1);
  - the rack bays, footings and the 0.5 m tank plinths.

  Who: structural engineer.
- Pipe stress, the post positions against thermal movement, and the tailpipe guides of
  PSV-3114 / PSV-3116 / PSV-4127 / PSV-4128. Who: piping stress engineer.
- The vent and inert study (zones ASSUMED, D-031). Who: competent person.
- The crane selection and lifting plan (D-041 (7)). Who: crane contractor.
- Access for a mobile elevating work platform to the actuated valves of D-040 (4) and
  D-060 (7). Who: piping layout / maintenance.
- The compressor package arrangement of K-4101 / E-4101 (#3). Who: compressor vendor.
- The thermal and hydraulic calculations of D-060 (4) .. (6) themselves. Only their use of
  layout data and their consistency with the flowsheet were checked (#5).
- P&ID tiles.
