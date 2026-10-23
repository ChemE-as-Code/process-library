---
topic: layout
reviewed_commit: 898c28040ca957bda37853f81c5481872669cd40
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, checks/checks.yaml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 898c28040ca957bda37853f81c5481872669cd40, relation: depends-on}
  - {path: DESIGN.md, revision: 898c28040ca957bda37853f81c5481872669cd40, relation: depends-on}
reviewer: Claude (independent review agent; did not author D-044..D-050, the layout files or the fixes since 521f5c2)
reviewer_kind: agent
branch: open-points
merge: pending
---
# Review: layout, seventh review (independent) after the fixes of review6 and the open-points round

This is an independent layout review of branch `open-points` at 898c280. It follows
reviews/2026-10-22-layout-review6.md (521f5c2) and covers:
- D-044, the fixes of review6;
- D-045, the nozzle locations on the datasheets;
- D-046, the rebuild with the pipe-end check;
- D-047, the valve access platforms VP-1..VP-9;
- D-048, the rack intermediate steel;
- D-049, the 250 pipe support posts;
- D-050, the points left open.

The reviewer designed none of this. plantcode ran from the core worktree `feat/open-points`
(a39f2fe). No P&ID changed on the branch. Coordinates are site metres from
`layout/plant-model.yaml`.

Distances marked "computed" come from scratch scans of the model, kept outside the repository:
- every ladder rail and cage (racks, CB-1, VP-1 / VP-6, the C-1101 / C-1102 platform ladders)
  against every pipe;
- every vertical pipe against the ring platform walkways;
- every pipe against the VP floors and VP stairs;
- every member of the rack steel against every pipe;
- every member of the support steel against the pipes it does not serve, equipment, envelopes,
  stairs, ladders, VP footprints, buildings, roads and the crane-pad, laydown, keep-clear,
  maintenance and escape zones;
- the clear width along the escape route Z-ESC-CB1 at grade;
- every column at grade against the roads.

No layout file was changed by this review.

Verdict: **not acceptable for a stage sign-off** while #1 (high) is open. Every finding of
review6 is closed, and the scans confirm it: every ladder is at least 0.30 m from any pipe, and
no riser runs through a ring walkway. Operability fell from 27 to 14 and free spans from 21 to
8. Two kinds of new steel bring new problems that no rule reports:
- The valve platform **VP-8 and its stair stand in the central road R2**, and two rack bents
  stand in the road too.
- The new **support posts** stand where they should not:
  - one in the climbing space of the cold box ladders LD0 / LD1;
  - one on the K-4101 crane pad, which a GOX line also crosses at 3.6 m;
  - one each in two laydowns;
  - ten in the cold box escape route;
  - one with its crossbar inside the K-3101 package.

The core rules test pipes against these spaces but not structures or support steel.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-23-layout-review7#1 | layout | VP-8, road R2 | The valve access platform VP-8 (PV-4111, D-047, raised to 8.6 m by D-048) stands in the central road R2: its footprint is [179.7, 76.62, 180.9, 78.62], and R2 runs along y 78.5 at 6 m wide, so y 75.5..81.5. Its four HEB300 columns stand on the carriageway. So does its three-flight stair (box [177.9, 77.72, 0, 179.7, 82.94, 9.7]) (computed). R2 is the road on the process north side and the storage south side. East of PR3 it is the only link to the east road R5, and the fire access. Both platform and stair block it at x 177.9..180.9. No rule reports a structure in a road. Plan build/layout-plan_crop-165-66-195-95.png shows VP-8 and its stair across the grey road band. | high | open | Move PV-4111 (and its VP-8 platform) off the road: to the PR3 bay north of R2 like VP-9 (y > 82.5), or onto the rack, worked from a PR3 walkway. Or drop the valve to grade outside the road. Ask plantcode for a rule on structures, stairs, ladders and support posts inside a road (`layout-road-obstruction`). |
| 2026-10-23-layout-review7#2 | layout | PR2/bent-2, PR3/bent-2, road R2 | Both rack crossings of R2 have a bent inside the road. PR2/bent-2 has columns at [140.85, 80.0] and [145.15, 80.0]. PR3/bent-2 has them at [180.35, 80.5] and [183.65, 80.5]. Both are 1.0..1.5 m inside the north road edge (y 81.5) (computed). That leaves about 4.4 m of the 6 m road. The bents are generated at 6 m / 6.25 m spacing from the rack start, and nothing keeps them off the road. This was not raised by the earlier reviews. | medium | open | Place the bents either side of R2 (a 7.5..8 m span over the road with a deeper beam, or a bent at y 74 and y 82.5), or narrow the declared road with a reason. Same rule request as #1. |
| 2026-10-23-layout-review7#3 | layout | P-03/Line_LOX3002_S1/post-1, CB-1/LD0, LD1 | The declared T-post for LOX-3002 S1 (DN 25) is a 12 m HEB200 column from grade at [127.375, 49.25] to 12.18 m. It stands directly north of the caged ladders LD0 (x 126.5, grade to P10) and LD1 (x 127.5, P10 to P20). The cages are y 48.2..48.9 (r 0.35). The column is 0.25 m outside the LD0 cage, in front of the rungs (computed). Its crossbar at 12.08 m runs y 48.75..49.75 and enters the LD1 cage by 0.15 m, 2.1 m above P10 (computed), at the climber's head. LD0 is the second way down from the cold box platforms (Z-ESC-CB1 basis). The `layout-ladder-clearance` rule tests pipes, not steel. Section build/layout-section-y49_crop-120-0-146-16.png. | medium | open | Support LOX-3002 from the P10 / CB-1 steel (a bracket off the north face or the P10 edge beam) instead of a post from grade, or move the post east of x 128.3. Ask plantcode to apply `layout-ladder-clearance` to structures and support steel. |
| 2026-10-23-layout-review7#4 | layout | P-04/Line_GOX4002_S1/post-1, GOX-4002 S1, Z-PAD-A4 | The declared post for GOX-4002 S1 stands at [175.93, 32.44] on the crane pad Z-PAD-A4 ([174, 23, 184, 35]). That is the pad for the heaviest lift: K-4101, 52 t gross at 12.5 m, and E-4102 (lifting study). The pipe it carries (pinned since D-041) crosses the pad's north-west corner at 3.61 m from x 174 to 177.3 at y 32.44. The pad volume is only 1 m high, so no rule saw the pipe. The `layout-lifting` and `-laydown` rules do not check support steel. Of the 10 x 12 m pad, the 3 x 2.6 m corner is lost to outriggers and to the slewing superstructure. Plan build/layout-plan_crop-168-20-190-40.png. | medium | open | Route GOX-4002 S1 north of y 35 before it turns east (or under the pad at grade in a trench), then drop the post. Ask plantcode to test support steel and pipes below the crane's working height against crane pads. |
| 2026-10-23-layout-review7#5 | layout | P-02/Line_RG2002_S3/post-1, P-04/Line_GAN4003_S3/post-1, Z-SIEVE, Z-LAYDOWN-A5N | Two declared posts stand in laydowns. The RG-2002 S3 post (column to 6.7 m) is at [92.0, 34.5], 0.5 m inside the sieve change-out area Z-SIEVE (y 34..38, kept 4.5 m clear for the vacuum truck). The GAN-4003 S3 post (to 9.1 m) is at [176.7, 121.0], 1 m inside Z-LAYDOWN-A5N, the 5 x 9 m laydown for the 3.5 x 3.5 m vaporizer modules (computed). D-049 moved posts out of access spaces and lift lanes, but not out of laydowns. | low | open | Shift both posts along their pipes out of the zones (RG-2002 S3 runs along x 92 from y 42 to 27: a post at y 33.5 or 39), and extend the build's post placement to avoid laydown and crane-pad zones. |
| 2026-10-23-layout-review7#6 | layout | Z-ESC-CB1, posts of AIR-3005 S1, CWR-3001 S1, LIN-3001 S1 | Ten declared posts stand in the escape route Z-ESC-CB1 (x 140.6..143.5, y 11..50.6, from the foot of ST1 to road R1). They are AIR-3005 S1 post-2 / -3, CWR-3001 S1 post-2..-5 and LIN-3001 S1 post-1..-4. The route was declared "kept clear". With the casing bracing and columns, the clear width falls to 1.19 m at y 40.2 and y 45.3, and to 1.35 m at y 45.7 (computed). This is still passable, but the posts are trip and collision points on the way out of the cold box. No rule tests steel in an escape zone. | low | open | Put the posts of these three lines on the casing side (x < 140.6) or as brackets off the CB-1 east columns, or widen the declared route and state the minimum clear width (ASSUMED 1.2 m) it must keep. Ask plantcode to test structures and posts against escape zones. |
| 2026-10-23-layout-review7#7 | layout | P-03/Line_AIR3003_S1/post-1, K-3101 | The declared post for AIR-3003 S1 at [132.11, 37.55] (column to 1.1 m) is 0.25 m from the K-3101 package face (y 37.3). Its 1 m crossbar at 1.22 m runs y 37.05..38.05 and reaches 0.35 m into the K-3101 package box ([130.1, 34.3, 134.1, 37.3, 3.0]) (computed). That is a clash with the machine or its skid. The core clash rules report none: they do not test support steel against equipment. | low | open | Support AIR-3003 S1 from the K-3101 skid or with a one-sided bracket post north of the pipe. Ask plantcode to include support steel in `layout-clash-*`. |
| 2026-10-23-layout-review7#8 | layout | P-03/Line_UN3001_S1/post-2, VP-1 | The UN-3001 S1 support is a stub on the VP-1 floor. The stub stands at [131.1, 61.86] from 5.6 to 10.26 m, 0.1 m inside the west edge and 0.46 m north of the ladder cage. VP-1 is a light 1.95 x 2.0 m valve platform (HEB200 beams, D-047). D-047 and D-049 do not say that it carries a 4.7 m pipe support and its load. The stub also takes part of the space next to the ladder exit. | low | open | Record the load on VP-1 in D-049 (structural engineer) or take the stub to its own post from grade, and keep the standing square in front of PV-3110B free. |
| 2026-10-23-layout-review7#9 | layout | VP-1/ladder-to-P1, VP-6/ladder-to-P1 | Both ladders rise inside their platform footprint (`at: [0.4, 0.4]`), through the floor. Each cage continues 1.1 m above the grating, to 6.7 and 7.0 m, inside the platform. The model shows no floor opening, hatch or self-closing gate. On VP-6 (1.26 x 1.5 m) the cage takes 0.7 x 0.4 m of the floor beside the GAN-4002 / VNT-4007 riser that carries XV-4134 / XV-4135. The ladder-clearance and operability rules both pass. The arrangement is unusual, though: ISO 14122-4 expects a side or through exit at the platform edge with a gate. | low | open | Put the ladders at the platform edge with a side exit and a self-closing gate (ISO 14122-4, ASSUMED), or model the floor opening and its protection, and check the 0.6 m standing square on VP-6 again. |
| 2026-10-23-layout-review7#10 | layout | P-04/Line_LIN4002_S4/post-1..5, LIN-4003 S3 | The five declared posts of LIN-4002 S4 (x 144.52, 5.39 m) have their columns 0.013 m from the insulated LIN-4003 S3, which runs beside them at 3.57 m (computed). The cold line rubs the steel at five points, and LIN-4003 S1 / S3 itself is still listed as open for supports (D-049). | low | open | Carry LIN-4003 on a lower crossbar of the same posts (with cold shoes) and close its open support item with them. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-22-layout-review6#1 | AIR-1004 through the C-1101 walkways, ladder exits and platform-1 cage | high | closed a80fdfd | AIR-1004 drops at 45 deg outside the handrail. Nothing within 0.75 m of any C-1101 ladder rail or cage on platform-1..-4 (computed). No vertical pipe in a C-1101 walkway. Section build/layout-section-y55_crop-62-0-82-30.png. 0 ladder-clearance, 0 walkway-riser. |
| 2026-10-22-layout-review6#2 | CHW-1001 riser through the C-1101 walkways | medium | closed a80fdfd | N4 at 270 deg in the arc gap. The ring scan finds only CW-1001 S6 (r 2.7 at 270 deg, outside the 345..195 arc) and AIR-1002 S3 at r 3.62 (0.21 m outside the handrail). |
| 2026-10-22-layout-review6#3 | PR2 end ladder crossed by LIN-3001 / LOX-3001 | medium | closed a80fdfd | Closest pipe to the PR2 ladder: LOX-3001 S2, 0.78 m from the cage (computed). |
| 2026-10-22-layout-review6#4 | PR3 end ladder and VNT-4002 / VNT-4003 | medium | closed a80fdfd | Closest pipe to the PR3 ladder: GAN-4003 S3, 0.79 m from the cage. Z-LAD-PR3 is declared. One support crossbar (GAN-4003 S3 post-2) ends at x 180.2 on the zone edge, 0.25 m from the cage. |
| 2026-10-22-layout-review6#5 | CW-3001 behind the LD0 rungs | low | closed a80fdfd | CW-3001 S1 is 0.48 m from the LD0 rail (computed). Steel at LD0 / LD1: see #3. |
| 2026-10-22-layout-review6#6 | stale tray-span acceptance reasons | low | closed bd4bbd4 | PT-E-2101 6.6 m and IT-JB-A3-1 16.0 m quote the reported lengths. validate reports no accept-stale. |
| 2026-10-22-layout-review6#7 | LIN-4002 S3 inverted U | low | closed a80fdfd | S3 and S4 are level at 5.39 m from [146.84, 99.996] to [146.228, 125.0] (plant-model points). |
| 2026-10-22-layout-review6#8 | nozzle locations not on the datasheets | low | closed acc433c | C-1101, C-3101, T-4101 / T-4102 and V-2101A/B give face, orientation, offset and elevation with their source. validate compares "datasheet nozzle locations vs layout model" with 0 findings. |
| 2026-10-22-layout-review6#9 | no access to the casing breather PSV-3123 | low | closed a80fdfd | Roof strip RB (frame x 13.8..15, y 1.6..7.2, 53 m) is declared in CB-1 levels. It is entered under the D-031 purge isolation (D-044 (6)). |
| 2026-10-22-layout-review3#2 | PSV-3114 / PSV-3116 tailpipes free 4.5 m above the valves | low | open | D-050 defers the guide to the stress analysis. Not modelled. |
| 2026-10-22-layout-review3#3 | layout-operability warnings | low | open | 14 (was 27): the TSA switching valves XV-2101A, XV-2102A/B, XV-2103A/B and XV-2111A; PV-4109 / PV-4110; XV-4118, XV-4119, XV-4132 and XV-4133; XV-3105; PV-3110A. Each has a reason in D-047, and VP-10..VP-23 remain as generated proposals with review_needed. VP-8 is in the road (#1). |
| 2026-10-22-layout-review3#4 | rack free spans and support missing | low | open | free-span 8 (was 21), support-missing 15 (10 accepted by name in checks.yaml, D-049). The open ones are listed in D-049. Posts that the earlier reviews did not foresee are in #3..#8, #10. |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | D-050: waits for the vendor drawing. |

## Drawing
No P&ID changed on the branch. validate counts:
- P-01 and P-02: 0 / 0 / 0 / 0.
- P-03: 3 line-crossing (accepted in the drawing gate).
- P-04: 1 line-crossing (accepted in the drawing gate).

Tiles not read.

## Layout
`plantcode layout build --check`: "layout/plant-model.yaml is up to date".

`plantcode layout report` at 898c280:
- **Lines:** 76 lines and 218 segments. 214 routed, 4 skipped (GAN-3002 and LN-3002 are
  internals, D-028; the two VNT-3004 segments are the casing breather). 0 unrouted.
- **Chains per method:** astar 34, astar_coarse 2, open 8, pinned 139, rack 14. No `direct`.
  139 of 197 chains are now pinned, against 71 at review6. Most routes are no longer the
  router's but the designer's (D-046, D-047). The rules check them all the same.
- **Chains per reason:**

  | reason | chains |
  |---|---:|
  | local: above the pipe-way | 7 |
  | local: pipe-way | 9 |
  | local: pump run at grade | 6 |
  | local: rack detour too long | 2 |
  | local: rack run too short | 1 |
  | local: short run | 11 |
  | open end | 8 |
  | pinned | 139 |
  | rack: battery limit at a rack end | 13 |
  | rack: longer than local_max_m | 1 |

- **Rack fill:**

  | rack | tier | fill |
  |---|---|---:|
  | PR1 | 5 m | 61 % |
  | PR1 | 7 m | 37 % |
  | PR1 | 9 m | 25 % |
  | PR2 | 6.5 m | 6 % |
  | PR2 | 8.5 m | 6 % |
  | PR3 | 6.5 m | 38 % |
  | PR3 | 8.5 m | 48 % |

  PR2 carries only LOX-3001 / LIN-3001 now, on 2 m intermediate steel on both tiers.
- **Model findings per rule:**

  | rule | count |
  |---|---|
  | clash-* | 0 |
  | headroom | 0 |
  | access-blocked | 0 |
  | ladder-clearance | 0 |
  | walkway-riser | 0 |
  | access-enclosed | 1 (E20, accepted) |
  | zone-crossing, separation, vent-outlet, wall-penetration, tier | 0 each |
  | escape-ways, escape-travel, landing-width, egress-zone, operator-unknown | 0 each |
  | lifting, laydown, pad-overlap, spacing, building-spacing, zone-source | 0 each |
  | operability | 14 (review3#3) |
  | free-span | 8 (review3#4) |
  | support-missing | 15, 10 of them accepted (review3#4) |
  | tray-span | 17, each accepted by name |
  | tray-zone | 6: 2 accepted, 4 infos for the N2 zones |
  | tray-separation | 1 (accepted) |
  | nozzle-unconnected | 2 infos |
  | layout-line-length | 16 infos |

  The 0 counts for clash, laydown, lifting and escape do not cover support steel or
  structures in roads and zones: #1..#7.
- **Objects:**
  - 45 equipment items;
  - 75 generated and 139 pinned pipes;
  - 8 declared platforms;
  - 12 declared structures: CB-1, FW-TR, FW-4101 and VP-1..VP-9;
  - 14 generated structures: the VP-10..VP-23 proposals, not in the take-off;
  - 250 declared and 29 generated support posts or stubs.
- **validate:** 0 errors, 55 warnings. The non-layout ones are 15 instrument-no-interlock,
  12 template-metadata and 2 titleblock-sheet (P&ID scope, not this review). There is no
  datasheet-nozzle-layout finding and no accept-stale.
- **`plantcode check`:** every concept and basic gate passes except `layout-review` (review6 is
  stale). The detail gate `datasheets` fails: 39 drafts, as intended (D-042).
- **`plantcode layout lifting`:** 14 maintenance lifts, every lane clear. K-4101 has 52 t gross
  at 12.5 m from Z-PAD-A4, needing a 69.3 t chart capacity. There is no crane chart (D-041 (7)).
  The pad itself is not checked for posts and pipes (#4).

PNGs read (build/, rendered at 898c280):
- build/layout-plan.png (plot plan);
- build/layout-plan_crop-165-66-195-95.png (R2 at PR3: VP-8 and its stair on the road, VP-9
  north of it, PR3 bent-2 in the road band, #1, #2);
- build/layout-section-y49_crop-120-0-146-16.png (CB-1 north face: the LOX-3002 post column
  from grade to 12 m beside the LD0 / LD1 ladders, AIR-3005 under P10, the casing bracing, #3);
- build/layout-section-y55_crop-62-0-82-30.png (C-1101 north side: AIR-1004 dropping outside
  the platforms, the posts of the CW / CWR lines, review6#1);
- build/layout-plan_crop-168-20-190-40.png (Z-PAD-A4: GOX-4002 S1 across the north-west corner
  of the pad with its post, VP-7 and its stair east of the pad, #4);
- build/layout-section-y68.png (along PR1: tiers and intermediate steel);
- build/layout-section-x135.png (through the cold box and PR1);
- build/layout-plan_crop-136-8-148-54.png (the escape route east of CB-1 with the CWR-3001,
  AIR-3005 and LIN-3001 posts, #6).

## Checked and fine
- **Ladders.** Every ladder in the model (PR1..PR3 ends, CB-1 LD0..LD4, VP-1, VP-6, C-1101 and
  C-1102 platform ladders) is at least 0.30 m from any pipe. The closest is VP-1 to the
  CW-3001 riser, at 0.30 m (computed).
- **VP floors and stairs.**
  - No pipe within 2.1 m above any VP grating, except the risers that each VP serves (VP-6:
    GAN-4002 S6 / VNT-4007 S1 through the floor at [171.0, 62.2]).
  - Four lines cross the VP-2 stair box at 7.0..9.5 m: WN-3003, GOX-4001, GAN-4004 and
    VNT-4003. They pass under the top flight and landing and 3.6 m above landing-0, so they
    leave the headroom on every flight.
- **Rack steel.** No pipe enters a rack member (computed). The CHW-1001 and AIR-1004 drops are
  off the new beams (D-048).
- **Operability.** The 13 resolved valves have a floor within reach. FV-2105 and PV-3113 are on
  risers at grade, and their low points are dry gas (D-047).
- **Datasheets and layout.** The nozzle locations agree with the model (validate cross-check).
  H1 goes with the casing penetration schedule (D-045).
- **Escape routes.** Clear width stays at least 1.19 m (#6). Each VP above 6 m has a stair, and
  VP-1 / VP-6 have a ladder below 6 m (D-047 criterion).

## Not checked
- Structural design of the VP platforms, the 250 posts and their footings, the 112 t of
  intermediate rack steel, the VP-1 stub load and the RB strip: structural engineer.
- Pipe stress, the post positions against the stress analysis, the AIR-1004 drop guide and the
  tailpipe guides: piping stress engineer.
- The vent and inert study (zones ASSUMED, D-031), the crane selection and lifting plan
  (D-041 (7)), fire access against the site's fire plan (R2 with #1 / #2): competent persons,
  crane contractor, fire engineer.
- The 14 open operability valves one by one, and the generated proposals VP-10..VP-23, which
  stay out of the design.
- The cost estimate and take-off (581 t steel) beyond their currency with the model.
- P&ID tiles.
