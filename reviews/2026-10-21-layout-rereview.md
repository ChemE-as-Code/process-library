---
topic: layout
reviewed_commit: f2a7582600d526daa29e75514995110c1196010f
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/plant-model.yaml, piping/routing.yaml, piping/pipe-specs.yaml]
basis:
  - {path: equipment/equipment-list.yaml, revision: f2a7582600d526daa29e75514995110c1196010f, relation: depends-on}
  - {path: DESIGN.md, revision: f2a7582600d526daa29e75514995110c1196010f, relation: depends-on}
reviewer: Claude (independent review agent)
reviewer_kind: agent
branch: layout-3d
merge: pending
---
# Review: layout, re-review after the fixes of D-032

Independent re-review of the 3D layout on branch `layout-3d` at f2a7582 ("Layout: fixes after
the independent layout review"), against the previous record reviews/2026-10-21-layout.md
(51f918d, committed as 04a1f2c) and DESIGN.md D-032. plantcode itself changed between the two
reviews (routes go round enclosures a line only passes, placed relief valves end their inlet
line, rack lanes are reached from the passing elevation). The reviewer did not author the layout.
Coordinates are site metres (x east, y north, z up), taken from `layout/plant-model.yaml`;
distances measured with `plantcode show <tag> --layout` where a tag exists, otherwise computed
from model coordinates and stated as computed.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-21-layout-rereview#1 | layout | PSV-3114, PSV-3116, CB-1 roof walkway RF, LD8 | The relief valves now stand ON the 1.8 m wide roof walkway RF (deck 53.0 m, y 45.2-47.0): PSV-3114 bbox x 127.6-128.4, y 45.8-46.4, PSV-3116 x 130.6-131.4, leaving about 0.6 m passage either side; their inlet pipes run across the walkway at 53.75 m (VNT-3002 x 127.06-127.6, VNT-3003 x 129.0-130.6, both at y 45.8), and the outlets end at 54.75 m, 1.75 m above the deck, i.e. at head height of a person on the walkway (build/layout-section-y46_crop-120-44-145-58.png). The O2-rich (PSV-3114, 3 m) and inert (PSV-3116, 3 m) relief zones cover the walkway, and the new second ladder LD8 lands at [127.5, 46.6] (computed from frame [1.5, 8.6]), 0.7 m from PSV-3114. D-011: relief outlets elevated above platforms, away from walkways and escape routes. | high | open | Move the valves off the walkway (e.g. onto the casing roof south of it, or a dedicated relief platform) and extend the tailpipes to at least ~3 m above the highest walking level plus the zone radius, pointing away from the ladders; re-check LD4 / LD8 and the roof zones. |
| 2026-10-21-layout-rereview#2 | layout | CB-1, B1, site-plan separation | The toppling separation CB-1 to B1 was not updated with the casing: site-plan.yaml still reasons "1 x height (50.5 m casing + roof walkway)" = 53 m, but the casing is now 53 m (`show CB-1 --layout`: top 53 m), the roof walkway handrail reaches ~54.1 m and the relief valves and tailpipes 54.5 / 54.75 m. By the rule stated in D-026 (3) / D-030 (5) the radius is now ~55-56 m against 54.0 m measured; D-032 (#3) changes the basis to "the casing roof" without saying why. | medium | open | Either move CB-1 (or B1) to keep 1 x the full height including the roof items, or record in DESIGN.md why the casing roof alone is the toppling height, and update the separation's reason text. |
| 2026-10-21-layout-rereview#3 | layout | VNT-4007, VNT-4006 | Moving the battery limit to x 176 brought the GAN DBB bleed VNT-4007 down to 4.58 m above grade at [176.0, 57.87] (was 10.1 m on the rack): its O2-deficient sphere (5 m) reaches grade, about 4.2 m wide at head height (computed), in the A4 operating area beside the GOX-4002 / GAN-4002 runs, 6 m from E-4103 (build/layout-plan_crop-155-45-195-75.png). The GOX bleed VNT-4006 at 8.5 m sits 0.8 m south of PR1 and its O2 zone overlaps the GAN bleed zone. | medium | open | Take both bleeds up above the PR1 top tier (or route them into the vent rack PR3 to V1) so the zones stay above walking levels; rebuild and re-check the zones. |
| 2026-10-21-layout-rereview#4 | layout | F-1101, R4, R1, Z-O2-VENTS, R5 | The separations added for #6 and #10 are fitted to the layout rather than to a criterion: F-1101 to R4 min 10 m against 10.0 m measured (no basis for 10 m beyond "intake elevated"), and Z-O2-VENTS to R5 min 3 m while D-025 and the site-plan notes require O2 vent outlets >= 15 m from roads (the VNT-4006 outlet is 11.0 m from the R5 edge, computed). The intake-upwind-of-roads issue of #10 is now declared and measured, but its acceptance rests on an ASSUMED intake height not shown in the model (F-1101 is an 8 m box). | low | open | State the criteria with a source (EIGA Doc 65 practice for intakes, D-025 for O2 vents to roads) and either meet them or record the deviation as a decision in DESIGN.md; model the intake opening height of F-1101. |
| 2026-10-21-layout-rereview#5 | layout | S-2101, V-2101A/B, Z-SIEVE, RG-2003 | S-2101 is placed (outlet 6 m) 4.0 m from V-2101A and V-2101B (measured), whose tops are at 6.5 m: the outlet is below the adsorber tops and its 5 m O2-deficient zone reaches the west ends of both adsorber tops (top nozzles and valves) and the edge of the change-out laydown Z-SIEVE. RG-2003 (DN600) now runs at 3.8 m across Z-SIEVE (y 35.4, x 84.6-90 and y 33.2, x 90-101), above the 3 m zone box but low for a vacuum truck (build/layout-plan_crop-75-25-110-50.png). | low | open | Raise the S-2101 outlet above the adsorber tops and any top platform (e.g. 10 m) or move it further west; route RG-2003 clear of the change-out area or raise Z-SIEVE to the truck height and re-route. |
| 2026-10-21-layout-rereview#6 | layout | CW-3001, KT-3101 | The new route of CW-3001 round the cold box runs at 3.92 m along y 35.06 from x 124.1 to 130.1, directly over the expander KT-3101 (x 127-130, y 34.3-37.3, top 3.0 m): 0.8 m above the machine, in the way of lifting its cold end / rotor. | low | open | Give CW-3001 a via south of the compander (y < 34) or above the lifting height. |
| 2026-10-21-layout-rereview#7 | layout | LIN-3001, PR1 | LIN-3001 reaches PR1 at 5.43 m and runs x 138.6-141.6 between the 5 m water tier and the 7 m tier before rising to the PR2 6.5 m tier; the PR1 rule puts liquid nitrogen on the 9 m tier. A short run, but not on its tier and among the CW lines. | low | open | Force the tier for the PR1 part or accept with a reason. |
| 2026-10-21-layout-rereview#8 | layout | PR2 title, DESIGN.md D-026 (2) | Split from 2026-10-21-layout#17 (b): the PR2 title in site-plan.yaml and D-026 (2) still say PR2 carries GOX-4004 / GAN-4003; in the model both run via PR3 (GOX-4004 at x 181.36, GAN-4003 at x 181.14, z 8.56). | low | open | Correct the PR2 title and D-026 / D-029 text, or route the risers over PR2 as stated. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-21-layout#1 | PSV-3114 / PSV-3116 outlets inside the cold box casing | high | closed f2a7582 | PSV-3114 / PSV-3116 placed on RF at 53 m; VNT-3002 rises inside the casing from [126.56, 46.0, 44.3] to the valve, outlet [128.0, 46.1, 54.75]; VNT-3003 from C-3101 N7 at 18.8 m to [131.0, 46.1, 54.75]; both outside the casing (53 m). The new placement has its own defect: 2026-10-21-layout-rereview#1 |
| 2026-10-21-layout#2 | CW-3001 / CWR-3001 through the cold box | high | closed f2a7582 | CW-3001 now via x 124.14 (west of the casing), CWR-3001 via x 143.71 (east); the wall-crossing check of the model routes finds no CW / CWR crossing of CB-1 (only cold box process lines and the compander lines). New side effect: rereview#6 |
| 2026-10-21-layout#3 | casing too low, WN-3001 over the roof | high | closed f2a7582 | enclosure height 53 m, RF at 53 m; WN-3001 top of pipe 51.63 + 0.41 = 52.03 m, inside the casing (build/layout-section-x133.5.png). Toppling separation not updated: rereview#2 |
| 2026-10-21-layout#4 | RG-2003 vent at 1.78 m above grade | high | closed f2a7582 | S-2101 placed at [83, 36], outlet 6 m; RG-2003 ends at the silencer inlet [83.6, 35.4, 3.0]; zone Z-N2-VENTS takes S-2101 (centre z 6). Remaining issues: rereview#5 |
| 2026-10-21-layout#5 | C-1102 top platform inside the continuous WN-1002 zone | medium | open | unchanged: WN-1002 zone centre [55, 61, 24.42], r 5, platform 21.0 m; left open by D-032 |
| 2026-10-21-layout#6 | VNT-4006 GOX bleed zone over road R5 | medium | closed f2a7582 | battery limits moved to x 176; VNT-4006 outlet [176.0, 63.2, 8.5], zone edge 6.0 m from the R5 edge (computed), separation Z-O2-VENTS to R5 declared, no layout-separation finding. Criterion and new GAN bleed position: rereview#3, rereview#4 |
| 2026-10-21-layout#7 | LOX-3001 not on the oxygen tier | medium | closed f2a7582 | LOX-3001 on PR1 at 9.07 m and on PR2 at 8.57 m (8.5 m oxygen tier); build/layout-section-y90_crop-130-0-160-12.png shows LOX-3001 on 8.5 m, LIN-3001 on 6.5 m |
| 2026-10-21-layout#8 | FW-4101 penetrated by GOX lines, E-4101 outside, open side to R5 | medium | open | unchanged: GOX-4001 through the west wall at [160.5, 29.0, 2.5], GOX-4005 through the north wall at x 164.0 / 167.9, z 3.7 (model routes); left open by D-032 |
| 2026-10-21-layout#9 | routes through the B1 cladding outside the openings | medium | open | unchanged: the same nine crossings (AIR-1001 west z 4.21, AIR-1002 north, AIR-1003 east y 31.3, six CW / CWR north at z 3.84); left open by D-032 |
| 2026-10-21-layout#10 | intake F-1101 close to and downwind of R4 / R1 | medium | superseded by 2026-10-21-layout-rereview#4 | separations F-1101 to R4 (>= 10 m, measured 10.0 m) and to R1 (>= 15 m, measured 17.0 m) now declared and measured; the remaining question is the basis of the criteria |
| 2026-10-21-layout#11 | no escape zones, single ladders above P10 | medium | closed f2a7582 | ladders LD5..LD8 at the west end give every platform two ways down; escape zone Z-ESC-CB1 [141, 11, 0, 143.5, 38, 2.2] from ST1 to R1, no zone-crossing finding. LD8 top next to PSV-3114: rereview#1 |
| 2026-10-21-layout#12 | AIR-1006 over the E-1102 bundle pull | low | open | unchanged: AIR-1006 at 3.86 m along y 42, x 47-55.6 |
| 2026-10-21-layout#13 | cryogenic pumps 6.5 m from their tanks | low | open | unchanged (T-4101 to P-4101A/B 6.5 m) |
| 2026-10-21-layout#14 | E-2101 nozzle at grade | low | closed f2a7582 | E-2101 N1 override on the west face; RG-2001 S2 now ends at [90.5, 55.0, 1.0] |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | unchanged: KT-3101 0.7 m south of CB-1 (measured), compander lines through the south casing wall |
| 2026-10-21-layout#16 | GOX-4002 / GOX-4003 on the local pipe-way | low | open | unchanged: GOX-4002 along x 180.3 at 3.61 m (`local: rack detour too long`) to the new BL at [176.0, 63.2, 9.5] |
| 2026-10-21-layout#17 | PR2 / PR3 lowest tier at the road headroom; D-026 text | low | closed f2a7582 | PR2 and PR3 tiers 6.5 / 8.5 m (site-plan.yaml, routing.yaml rules), rack fill reported on 6.5 / 8.5 m; part (b), the D-026 text, is split to 2026-10-21-layout-rereview#8 |

## Drawing
No P&ID is in scope and none changed on the branch: `plantcode diff main --list` prints "No P&ID
changed." Changes since the previous review (`git diff --stat 51f918d f2a7582`): DESIGN.md
(D-032), PROGRESS.md, layout/equipment-placement.yaml, layout/plant-model.yaml,
layout/site-plan.yaml, layout/structures.yaml, layout/zones.yaml, piping/routing.yaml and the
previous review record (04a1f2c). layout/building.yaml is unchanged since 51f918d.

## Layout
`plantcode layout build --check`: "layout/plant-model.yaml is up to date".

`plantcode layout report` at f2a7582:
- lines: 76; 73 routed, 3 skipped (GAN-3002, LN-3002, VNT-3004, reasons as before), 0 unrouted.
- chains per method: astar 68, astar_fine 1, open 23, rack 32, rack+astar_coarse 2; no `direct`,
  no `rack+direct`.
- chains per reason: local: above the pipe-way 14, local: pipe-way 21, local: pump run at grade 5,
  local: rack detour too long 9, local: rack run too short 2, local: short run 18, open end 23,
  rack: across areas 14, rack: battery limit at a rack end 15, rack: crosses a road 1,
  rack: longer than local_max_m 4; battery limit ends: battery limit rule 19.
- rack fill: PR1 tier 5 m 4.90 of 8 m (61 %), 7 m 3.65 of 8 m (46 %), 9 m 2.02 of 8 m (25 %);
  PR2 tier 6.5 m 0.86 of 4 m (21 %), 8.5 m 0.88 of 4 m (22 %); PR3 tier 6.5 m 1.44 of 3 m (48 %),
  8.5 m 1.02 of 3 m (34 %).
- model findings per rule: plantcode.layout-nozzle-unconnected 2 (info, the skipped double
  column internals); layout-clash-* 0, -headroom 0, -access-blocked 0, -zone-crossing 0,
  -separation 0 (`plantcode validate` reports no layout-separation either).
- platforms review_needed: 0 (8 declared).
- objects: equipment declared 45, inline generated 110, pipes generated 214, platforms declared 8,
  structures declared 2, zones declared 13.

PNGs read (all under build/, rendered at f2a7582):
- build/layout-plan.png (plot plan)
- build/layout-plan_crop-155-45-195-75.png (new battery limit at x 176, VNT-4006 / VNT-4007 zones, R5)
- build/layout-plan_crop-75-25-110-50.png (S-2101, RG-2003, V-2101A/B, Z-SIEVE)
- build/layout-section-x133.5.png (section through the cold box, depth 16 m: casing 53 m, PSVs on the roof, WN-3001 inside)
- build/layout-section-y46_crop-120-44-145-58.png (roof walkway with PSV-3114 / PSV-3116, outlets 1.75 m above the deck, zones)
- build/layout-section-x100_crop-50-0-80-12.png (section across PR1 at x 100, tiers 5 / 7 / 9 m)
- build/layout-section-y90_crop-130-0-160-12.png (section across PR2: LOX-3001 on 8.5 m, LIN-3001 on 6.5 m)

Wall and enclosure crossings were checked by intersecting every model route with the B1 walls
(and their openings), the CB-1 casing walls and the FW-4101 walls: CB-1 is now crossed only by
cold box process lines and the compander lines; FW-4101 and B1 crossings are unchanged (#8, #9).

## Checked and fine
- The four high findings of the previous review are fixed in the model (see Previous findings),
  with new, smaller issues from the fixes listed as rereview#1..#8.
- Model current, every process line DN >= 25 routed or skipped with a reason, no fallback
  routes, rack fill below 65 %.
- Separations measured and met as declared: CB-1 to B1 54.0 m (>= 53 m as declared, see
  rereview#2), F-1101 to R4 10.0 m and R1 17.0 m, T-4101 values as before; no
  `layout-separation` finding.
- Oxygen lines on their tiers: GOX-4001 and LOX-3001 on PR1 9 m, LOX-3001 on PR2 8.5 m.
- Cold box access: two ways down from every platform (ST1 / LD0 to P10, LD1..LD4 east, LD5..LD8
  west), escape zone Z-ESC-CB1 kept clear.
- Unchanged items checked in the previous review (tank capacities, pump orientation, nozzle
  overrides, maintenance zones, zones marked ASSUMED) remain as recorded there.

## Not checked
- Pipe stress, flexibility and supports (cold box penetrations, the new CW-3001 / CWR-3001 runs,
  the GOX battery limit risers): piping stress engineer, detail engineering.
- Structural design of CB-1 at 53 m with the relief valves on the roof, the toppling question
  (rereview#2), FW-4101, racks and B1: structural engineer.
- The oxygen and inert vent study and the area classification: every zone is still an ASSUMED
  screening volume; relief discharge reaction forces and dispersion of the PSV-3114 / PSV-3116
  outlets on the roof: competent person (EIGA guidance), D-031.
- Oxygen velocity and material rules on the rerouted GOX lines; hydraulics and NPSH: process
  engineer.
- Valve and instrument access item by item; the 3D viewer (`plantcode serve`) was not used.
- P&IDs (not in scope, none changed) and validate warnings outside the layout scope.
