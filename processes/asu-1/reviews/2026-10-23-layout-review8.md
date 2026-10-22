---
topic: layout
reviewed_commit: e2c43ea2fc1358b71b4ecc46568c1cd43a04a9cb
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, checks/checks.yaml]
basis:
  - {path: equipment/equipment-list.yaml, revision: e2c43ea2fc1358b71b4ecc46568c1cd43a04a9cb, relation: depends-on}
  - {path: DESIGN.md, revision: e2c43ea2fc1358b71b4ecc46568c1cd43a04a9cb, relation: depends-on}
  - {path: process/flowsheet.yaml, revision: e2c43ea2fc1358b71b4ecc46568c1cd43a04a9cb, relation: depends-on}
reviewer: Claude (independent review agent; did not author D-051..D-054, the layout files or the fixes since 898c280)
reviewer_kind: agent
branch: open-points
merge: pending
---
# Review: layout, eighth review (independent) after the fixes of review7 and the datasheet sizing

This is an independent layout review of branch `open-points` at e2c43ea. It follows
reviews/2026-10-23-layout-review7.md (898c280) and covers:
- D-051 (1) .. (10), the fixes of review7 (commits 97e9db1 .. cca091d);
- D-052, the booster branch in the flowsheet;
- D-053, the datasheet sizing (ba63107). This review checks it against the layout: the nozzle
  locations, the weights and dimensions against the layout model and the lifting study, and
  the pump suction geometry that the sizing uses;
- D-054, the equipment estimate (currency only).

The reviewer designed none of this. plantcode ran from the core worktree `feat/open-points`
(d1a50a7). Coordinates are site metres from `layout/plant-model.yaml`. Distances marked
"computed" come from scratch scans of the model, kept outside the repository:
- every declared structure member, stair, ladder, rack column and support post against the
  roads, the crane-pad, laydown, keep-clear, maintenance and escape zones, and the equipment
  boxes (cylinders checked on their radius);
- every pipe against every support post it does not serve;
- every pipe and steel part inside the escape lane Z-ESC-CB1 to 2.2 m;
- every ladder axis against pipes and posts;
- every open pipe end (vent and relief outlets) against every declared floor;
- the datasheet nozzle locations, weights and dimensions against the model and the list.

No layout file was changed by this review.

Verdict: **no critical or high finding is open**. Every review7 finding is closed, and the
scans confirm each fix. Four medium findings are new:
- #1 is a side effect of the review7#1 fix: the lengthened VP-9 now has the GAN relief outlet
  of PSV-4128 at chest height beside its floor;
- #2..#4 come from the datasheet sizing (D-053) read against the layout:
  - the nozzle locations the layout decided are missing on 12 datasheets, 9 of them now marked
    complete;
  - the E-4101 package is sized as four coolers but laid out as one 1.4 x 6 m shell of 8 t;
  - the LOX / LIN pump suctions stand above the tank outlets.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-23-layout-review8#1 | layout | PSV-4128, GAN-4003 S6, VP-9 | D-051 (2) lengthened VP-9 north to y 89.04 to serve PV-4111 as well. The open outlet of the GAN relief PSV-4128 (GAN-4003 S6, [181.572, 87.636, 9.557]) is now 0.96 m above the VP-9 grating (8.6 m) and 0.46 m east of its floor edge (x 181.11) (computed). Before the change, the floor ended at y 86.54, 1.1 m south of the outlet. The operator at PV-4112 (y 86.1) and PV-4111 (y 88.0) stands 1.5 m from a nitrogen relief outlet at chest height. That is a cold, oxygen-deficient jet. D-051 (2) raised the PSV-4127 tailpipe to 3 m above the grating but left PSV-4128 out. No zone covers the outlet: Z-N2-VENTS does not list it. `layout-vent-outlet` reports nothing, because it does not test an outlet beside a floor. Plan build/layout-plan_crop-170-78-192-96.png. | medium | open | Run the PSV-4128 tailpipe up to 3 m above the VP-9 grating, as for PSV-4127, or turn it away from the floor. Declare the outlet as a source in Z-N2-VENTS. Ask plantcode to make `layout-vent-outlet` test outlets within reach of a floor's edge, not only above it. |
| 2026-10-23-layout-review8#2 | layout / datasheets | K-1101, E-1103, E-2101, K-3101, KT-3101, K-4101, E-4102, K-4102, E-4103 (complete); C-3102, E-3101, E-3102 (drafts) | 18 items have nozzles placed by a layout override (`layout/equipment-placement.yaml` `nozzles:`, `source: declared` in the model). Only 6 datasheets give those locations (C-1101, C-3101, T-4101/2, V-2101A/B, D-045). The other 12 give none. Nine of them became `draft: false` in ba63107. Examples: <br>- K-1101 interstage N2..N5 on the north face and the discharge N6 on top; <br>- E-1103, E-4102 and E-4103 air / gas nozzles on the shell top, so the bundle can be pulled; <br>- K-4101 N1..N4 on the north side; <br>- K-4102 N2; <br>- E-3101's 10 nozzles. <br>A supplier quoting from these datasheets would put the nozzles where the P&ID draws them, which D-028 rejects (for E-1103 it would block the bundle pull). The validate cross-check compares only the nozzles that carry a location, so it cannot report a missing one. review6#8 was closed for the 6 items only. | medium | open | Add `face`, `orientation_deg`, `offset_m`, `elevation_m` and `location_source` for every declared nozzle on these 12 datasheets, as D-045 did. Ask plantcode to report a datasheet that lacks the location of a nozzle the placement overrides (`datasheet-nozzle-layout` for missing, not only differing, locations). |
| 2026-10-23-layout-review8#3 | layout / datasheets | E-4101 | D-053 (2) sizes E-4101 as four 1-2 shell-and-tube intercoolers: 65.8 + 3 x 73.4 = 286 m2. The layout, the list and the lifting study keep one horizontal shell of 1.4 m x 6 m at 8 t, lifted from Z-PAD-A4C. Its aftercooler E-4102, sized at 73.4 m2, is itself a 1.2 m x 5 m shell of 6 t. So each of the four intercoolers is about the size of E-4102: roughly four times the plan area and about 24 t for the package (ASSUMED by analogy with E-4102, not a vendor figure). The P&ID and the model also carry one cooler with two nozzles, not the eight interstage connections. The layout does not show the package that the datasheet sizes. | medium | open | Either size E-4101 as a package of four shells (envelope, weight and interstage nozzles from the D-053 areas, ASSUMED) in the list and placement, then rebuild and rerun the lifting study, or record in DESIGN.md that the compressor vendor's package replaces the item and that the 1.4 x 6 m envelope is a placeholder. Check the plot space between K-4101, PR1 and Z-PAD-A4C for it. |
| 2026-10-23-layout-review8#4 | layout | P-4101A/B, P-4102A/B, LOX-4001, LIN-4001, T-4101/N4, T-4102/N4 | D-053 (8) computes NPSHa at the tank outlet level as -0.16 m (LOX) and -0.19 m (LIN). The tank outlets N4 are at 0.5 m, and the pump suction nozzles N1 at 0.65 m. The suction lines run level at 0.5 m for 4.8 / 5.3 m, then rise 0.15 m into each pump (LOX-4001 S2 / S3, LIN-4001 S2 / S3, computed from the model points). That is the reverse of the usual cryogenic pump arrangement: the pump below the outlet and the suction falling continuously to the pump, so vapour returns to the tank. Here vapour collects at the pump inlet. The datasheets carry this as a requirement on the low-low level (LIA-4107 / LIA-4108). The layout itself is not changed, and "pumps near their suction source" is met only in plan (6.5 m). Section build/layout-section-y103_crop-115-0-160-14.png. | medium | open | Set the pumps (or their suction nozzles) below the tank outlets: pumps in a shallow pit, or the tanks on a plinth. Slope the suction lines continuously from the tank to the pump with a vent back to the tank. Then rerun the D-053 NPSH calculation. Record the low-low level basis in the interlock list if it stays. |
| 2026-10-23-layout-review8#5 | layout | PSV-4127, GOX-4004 S6, VP-9 | The oxygen relief PSV-4127 (blocked outlet / thermal on the GOX backup vaporizer outlet header, DESIGN.md relief list) now discharges at 11.6 m. That is 3.0 m above the VP-9 grating and 0.25 m east of its floor edge, 1.5 m from PV-4111 (computed). D-051 (2) calls this ASSUMED "as the other O2 relief outlets near walkways". Z-O2-VENTS lists PSV-3114 (VNT-3002) as an O2-rich relief outlet, but not PSV-4127, so no oxygen-enriched zone is drawn around VP-9 and its stair. | low | open | Declare PSV-4127 (GOX-4004 S6 outlet, secondary) as a source in Z-O2-VENTS and check what its zone reaches: the VP-9 floor and stair, and the PR3 walkways. If the zone takes in the platform, raise or turn the outlet. |
| 2026-10-23-layout-review8#6 | layout | VP-3/stair-to-P1, K-4102 | The base landing of the VP-3 stair (centre [159.55, 53.353], 1.8 x 0.9 m, at grade) reaches 0.30 m into the K-4102 package box ([151, 53.5, 0, 159, 58.5, 4.0]) over x 158.65..159.0 (computed). The stair foot faces the package's south side, so whoever steps off it walks against the skid at x < 159. `layout-clash-*` and `layout-steel-in-way` report nothing. This dates from D-047 and was not seen by review7. Plan build/layout-plan_crop-145-44-165-62.png. | low | open | Turn the VP-3 stair (offset or side) so that its foot lands clear of K-4102, at least 0.8 m from the package (ASSUMED walkway). Ask plantcode to test stair landings and flights against equipment boxes. |
| 2026-10-23-layout-review8#7 | layout | support posts | review7#10 was one case of a wider pattern. Eight pipe-to-foreign-post clearances under 0.1 m remain, all present at 898c280 already (computed, pipe outer surface incl. insulation to the steel face): <br>- WN-3002 S2 / GAN-4001 S1 post-1 column 0.020 m; <br>- AIR-2001 S1 / RG-2003 S8 post-1 column 0.042 m; <br>- LIN-3001 S1 / UN-3001 S1 post-1 column 0.046 m; <br>- CWR-1004 S1 / CW-1001 S1 post-1 crossbar 0.047 m; <br>- RG-2001 S2 / AIR-1004 S1 post-1 column 0.060 m; <br>- LIN-4004 S2 / LIN-4003 S2 post-2 and post-3 columns 0.063 / 0.062 m; <br>- CWR-3001 S1 / UN-3001 S1 post-1 column 0.086 m; <br>- LIN-3001 S1 / LOX-3001 S1 post-1 column 0.089 m. <br>LIN-3001 and LIN-4004 are cold lines: they shrink and move on cool-down. | low | open | Shift these posts along their pipes, or carry the passing line on the same post, to a clear gap of at least 0.1 m (ASSUMED; the stress engineer sets the movement). Ask plantcode for a clearance margin in `layout-steel-in-way`. |
| 2026-10-23-layout-review8#8 | layout | generated VP-8 | After the declared VP-8 (PV-4111) was removed, the generated proposals were renumbered. "VP-8" is now the generated proposal for XV-2101A at [88.39, 32.41], and the proposals run VP-8 and VP-10..VP-22, where D-050 / D-051 (10) and review7 still say "VP-10..VP-23". An id that meant a road-blocking platform in review7#1 now names a different object, and the generated ids are not stable from build to build. | low | open | Ask plantcode to keep generated proposal ids stable (keyed to the valve served, e.g. VP-XV2101A) or to skip the ids of declared structures. Correct the range in DESIGN.md at the next layout change. |
| 2026-10-23-layout-review8#9 | datasheets | D-053 | D-053 says "the 38 datasheets", "28 ... draft: false" and "10 stay drafts". There are 39 datasheet files: 28 complete and 11 drafts. The `datasheets` gate lists C-1101, C-1102, C-3101, C-3102, E-3101, E-3102, E-3103, E-4105A/B and E-4106A/B. D-053's open list itself names 11 items. | low | open | Correct the counts in DESIGN.md D-053 (39 datasheets, 11 drafts). |
| 2026-10-23-layout-review8#10 | layout | B1 crane, K-1101 motor | The heaviest maintenance lift in B1 is the MAC motor, ~30 t ASSUMED. It sets the 40 t building crane (`layout/building.yaml`, D-034), but it is not in the lifting study. K-1101 carries no weight (the list gives none for the train), so the study lists only E-1101..E-1103 under the building crane. The gross load at the study's factors would be 30 x 1.1 x 1.05 = 34.7 t, within 40 t. The study does not show this, and the D-053 sizing (5,957 kW shaft, 8.0 MW motor kept) does not revisit the motor weight. | low | open | Give the MAC motor (or the K-1101 heaviest maintenance part) a weight in the list, ASSUMED with its basis, so the lifting study checks it against the B1 crane. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-23-layout-review7#1 | VP-8 and its stair in road R2 | high | closed 80bc810 | No declared structure, stair, ladder or post in R2 (y 75.5..81.5) (computed). PV-4111 at [181.358, 88.0, 8.557] is served from VP-9 ([179.91, 84.54] .. [181.11, 89.04], 8.6 m); its stair box [178.11, 88.14] .. [179.91, 93.356] is north of R2. Side effect of the fix: #1, #5. Plan build/layout-plan_crop-170-78-192-96.png. |
| 2026-10-23-layout-review7#2 | PR2 / PR3 bents inside R2 | medium | closed 803437b | No rack column within R2 (computed). PR2 bents at y 75.2 / 82.4, PR3 at y 75.1 / 82.3; R2 spanned clear. Free spans still 8. |
| 2026-10-23-layout-review7#3 | LOX-3002 S1 post at the LD0 / LD1 ladders | medium | closed fd1c6c9 | Nearest to the LD1 axis: post-1 crossbar 0.95 m; to the LD0 axis: post-2 column 0.97 m (computed); nothing between the ladders. |
| 2026-10-23-layout-review7#4 | GOX-4002 S1 and its post on Z-PAD-A4 | medium | closed 53df332 | The pipe turns north at x 173.5, 0.4 m west of the pad; the post at [173.5, 34.87]. Its crossbar end reaches x 174.1 at 3.3 m, 0.1 m over the pad edge, and the VP-7 column at [182.37, 35.12] reaches 0.03 m into it (computed). Both are negligible for the K-4101 lift east. Plan build/layout-plan_crop-155-22-190-52.png. |
| 2026-10-23-layout-review7#5 | posts in Z-SIEVE and Z-LAYDOWN-A5N | low | closed 306cee6 | No post in any laydown (computed). RG-2002 S3 post at y 39.0; GAN-4003 S3 along y 117, 1 m south of Z-LAD-PR3. |
| 2026-10-23-layout-review7#6 | posts in the cold box escape route | low | closed cbc90b9 | Z-ESC-CB1 is now the 1.25 m lane x 141.2..142.45, y 11..50.6; no pipe or steel in it to 2.2 m, and the link from the ST1 foot (x 140.5..141.2, y 48.7..50.5) is clear (computed). The lane is declared, not widened: the 1.2 m minimum is ASSUMED (D-051 (7)). Plan build/layout-plan_crop-136-8-148-54.png. |
| 2026-10-23-layout-review7#7 | AIR-3003 S1 post into K-3101 | low | closed 306cee6 | Post at [134.5, 37.55], east of the package (x 134.1); crossbar clear of the K-3101 box (computed). |
| 2026-10-23-layout-review7#8 | UN-3001 stub on VP-1 | low | closed 4a4b81e | No support steel on VP-1; UN-3001 S1 posts from grade, nearest 1.14 m from the VP-1 ladder axis (computed). |
| 2026-10-23-layout-review7#9 | VP-1 / VP-6 ladders through the floor | low | closed 4a4b81e | Ladders at [131.4, 60.1] and [170.62, 60.95], 0.2 m outside the south edges; nearest pipe 0.65 m (CW-3001) and 1.14 m (GAN-4002) from the axes (computed). The gate is ASSUMED and not modelled. |
| 2026-10-23-layout-review7#10 | LIN-4003 S3 against the LIN-4002 S4 posts | low | closed c693eab | LIN-4003 S3 is no longer among the pipe-to-post clearances under 0.1 m (computed); other such cases: #7. |
| 2026-10-22-layout-review3#2 | PSV-3114 / PSV-3116 tailpipes free 4.5 m above the valves | low | open | D-050 / D-051 (10): the guide waits for the relief reaction forces of the stress analysis. Not modelled. |
| 2026-10-22-layout-review3#3 | layout-operability warnings | low | open | 14 (unchanged): reasons in D-047; the proposals VP-8 and VP-10..VP-22 stay generated with review_needed (#8). |
| 2026-10-22-layout-review3#4 | rack free spans and support missing | low | open | free-span 8, support-missing 15 (10 accepted by name in checks.yaml, D-049), unchanged. |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | D-050: waits for the vendor drawing. |

## Drawing
No P&ID changed since 898c280. validate counts:
- P-01 and P-02: 0 / 0 / 0 / 0.
- P-03: 3 line-crossing (accepted in the drawing gate).
- P-04: 1 line-crossing (accepted in the drawing gate).

Tiles not read.

## Layout
`plantcode layout build --check`: "layout/plant-model.yaml is up to date".
`plantcode layout lifting --check`: current, exit 0. A fresh `plantcode layout lifting` is
identical to `layout/lifting-study.md` (model sha256 c4126ab6...).

`plantcode layout report` at e2c43ea:
- **Lines:** 76 lines, 214 segments routed, 4 skipped (GAN-3002 and LN-3002 are double-column
  internals, D-028; the two VNT-3004 segments are the casing breather). 0 unrouted.
- **Chains per method:** astar 34, astar_coarse 2, open 8, pinned 139, rack 14. No `direct`.
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
  | PR3 | 8.5 m | 43 % (48 % at review7; GAN-4003 S3 no longer runs along it) |

- **Model findings per rule:**

  | rule | count |
  |---|---|
  | clash-*, headroom, access-blocked, ladder-clearance, walkway-riser, steel-in-way | 0 each |
  | access-enclosed | 1 (E20, accepted) |
  | zone-crossing, separation, vent-outlet, wall-penetration, tier | 0 each |
  | escape-ways, escape-travel, landing-width, egress-zone, operator-unknown | 0 each |
  | lifting, laydown, pad-overlap, spacing, building-spacing, zone-source | 0 each |
  | operability | 14 (review3#3) |
  | free-span | 8 (review3#4) |
  | support-missing | 15, 10 of them accepted (review3#4) |
  | tray-span | 17, each accepted by name |
  | tray-zone | 6: 2 accepted, 4 infos |
  | tray-separation | 1 (accepted) |
  | nozzle-unconnected | 2 infos (C-3101 N3 / N4, D-028) |
  | layout-line-length | 16 infos |

  The 0 for vent-outlet does not cover an outlet beside a floor (#1); the 0 for clash and
  steel-in-way does not cover stair landings against equipment (#6) or small gaps (#7).
- **Objects:**
  - 45 equipment items;
  - 75 generated and 139 pinned pipes;
  - 8 declared platforms;
  - 11 declared structures: CB-1, FW-TR, FW-4101, VP-1..VP-7 and VP-9;
  - 14 generated proposals: VP-8 and VP-10..VP-22 (#8);
  - 280 support posts in the model, of which the declared ones were scanned.
- **validate:** 0 errors, 55 warnings: 15 instrument-no-interlock, 14 layout-operability,
  12 template-metadata, 8 layout-free-span, 4 line-crossing, 2 titleblock-sheet. There is no
  datasheet-nozzle-layout finding.
- **`plantcode check`:** every concept and basic gate passes except `layout-review` (review7 is
  stale). The detail gate `datasheets` fails on 11 drafts (#9).
- **`plantcode layout lifting`:** 14 maintenance lifts, every lane clear. The heaviest is K-4101,
  45 t (51.98 t gross at 12.5 m from Z-PAD-A4), needing 69.3 t chart capacity. There is no
  crane chart (D-041 (7)).

**Datasheets against the layout and the lifting study** (computed):
- Weights: every `weight_t` on a datasheet equals the list and the model `dimensions.weight`,
  and the lifting study uses those same values. For E-4101 the sized content does not fit
  them (#3); the MAC motor has no weight at all (#10).
- Dimensions: `diameter_m` / `height_m` on the column datasheets equal the model.
- Nozzle locations on the 6 datasheets that carry them: all 36 nozzles agree with the model in
  face, orientation, offset and elevation. The 12 items without them: #2.
- The pump NPSH of D-053 rests on the model's nozzle elevations: #4.

PNGs read (build/, rendered at e2c43ea):
- build/layout-plan.png (plot plan);
- build/layout-plan_crop-170-78-192-96.png (VP-9 with PV-4111 / PV-4112, PSV-4127 / PSV-4128
  at its east edge, R2 clear, #1, #5, review7#1 / #2);
- build/layout-plan_crop-145-44-165-62.png (VP-3 stair foot against the K-4102 package, #6);
- build/layout-section-y103_crop-115-0-160-14.png (LOX / LIN pumps at grade, suction lines at
  0.5 m rising into the pumps, #4);
- build/layout-plan_crop-155-22-190-52.png (Z-PAD-A4 with GOX-4002 S1 west of it, review7#4);
- build/layout-plan_crop-136-8-148-54.png (escape lane Z-ESC-CB1, review7#6);
- build/layout-section-y68.png (along PR1);
- build/layout-section-x133.png (through the cold box and PR1).

## Checked and fine
- **Roads.** No declared structure, stair, ladder, rack column or post in R1..R5 to 5 m
  (computed).
- **Zones.** No declared steel in a laydown, maintenance or escape zone, and none on a crane pad
  beyond the two edge contacts of review7#4 (computed). The PR3 end column stands at the edge of
  Z-LAD-PR3, as the ladder's own support.
- **Ladders.** Every VP and CB-1 ladder axis is at least 0.52 m from any pipe or post (LD0 to
  CW-3001) (computed).
- **Datasheets.** Weights and dimensions agree with the model and the lifting study (above).
- **Process.** D-052 changes no layout item; the booster branch adds no line.

## Not checked
- Structural design of the VP platforms (VP-9 now 4.5 m long on HEB300), the 7.2 / 7.14 m rack
  bays over R2, the posts and footings: structural engineer.
- Pipe stress, post positions against thermal movement (#7), the tailpipe guides: piping stress
  engineer.
- The vent and inert study (zones ASSUMED, D-031), the zones of PSV-4127 / PSV-4128 (#1, #5):
  competent person.
- The crane selection and lifting plan (D-041 (7)), the B1 crane against the motor weight (#10):
  crane contractor.
- The compressor package arrangement of K-4101 / E-4101 (#3): compressor vendor.
- The thermal and hydraulic sizing of D-053 itself (only its use of layout data was checked).
- The cost estimate (D-054) beyond its currency.
- P&ID tiles.
