---
topic: layout
reviewed_commit: 521f5c2070cade0b61027a56a084f9f709fdcf28
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, checks/checks.yaml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 521f5c2070cade0b61027a56a084f9f709fdcf28, relation: depends-on}
  - {path: DESIGN.md, revision: 521f5c2070cade0b61027a56a084f9f709fdcf28, relation: depends-on}
reviewer: Claude (independent review agent; did not author D-039..D-043, the layout files or the fixes since 0530ede)
reviewer_kind: agent
branch: open-points
merge: pending
---
# Review: layout, sixth review (independent) after the fixes of review5

Independent layout review of branch `open-points` at 521f5c2. It follows
reviews/2026-10-22-layout-review5.md (0530ede) and covers the fixes D-039 (review5), D-040
(operability), D-041 (lifting study) and the draft datasheets D-042. The reviewer did not design
the layout or make the fixes. plantcode ran from the core worktree `feat/open-points` (f2718de).
`plantcode diff main --list`: "No P&ID changed" (10 commits on the branch, layout, checks,
datasheets and estimate only). Coordinates are site metres from `layout/plant-model.yaml`.
Distances marked "computed" come from three scratch scans of the model, kept outside the
repository:
- every pipe against every grating surface (platforms, stair treads and landings, tank roof
  platforms), using pipe radius plus insulation and 2.1 m headroom;
- every pipe against every ladder rail and cage, stair stringer and handrail, using the
  closest distance between the segments minus both radii;
- every pipe against every stair box.

No layout file was changed by this review.

Verdict: **not acceptable for a stage sign-off** while #1 (high) is open. Every finding of
review5 is fixed: the cold box stair stands beside the platforms, P10, the tank roofs and RV
are clear, the vent zones are back, the breather is away from LD4, and the tray-span acceptances
are listed by name. The core#61 rules confirm all of this (0 headroom, landing-width,
egress-zone and zone-source findings), and the lifting study has a clear lane for all 14
maintenance lifts. Those rules still do not look at **ladders** or at **pipes that run
vertically through a walkway**. The scans found that the DCAC top outlet AIR-1004, pinned by
D-039 (2), now drops through the exit of every C-1101 ladder and runs through the ladder cage
at grade. Both rack-end ladders are crossed by lines too.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-22-layout-review6#1 | layout | AIR-1004 S1, C-1101 platform-1..4 and ladders | The DCAC top outlet AIR-1004 (DN600, od 0.61) is pinned, so its route is the designer's choice (D-039 (2)). It runs from the top nozzle at 26.62 m to [72.0, 55.0], then **drops vertically at [72.0, 55.0] from 26.62 to 5.695 m**, then runs north at 5.695 m to [72.0, 63.0]. C-1101 stands at [72, 52]. Its four platforms (6.3, 11.3, 18.8, 23.9 m) are annuli r 2.1..3.1 over 345..195 deg. The only way up is the caged ladder on the north side (ladder_side 90). Each ladder flight is at [72.0, 55.35], rails x 71.775 / 72.225, cage centre y 55.7, r 0.35. The vertical drop takes r 2.695..3.305 at 90 deg (computed). That is 0.4 m of the 1.0 m walkway, and it cuts the handrail (r 3.05..3.1) on all four platforms. It also stands 0.045 m behind the ladder rails of platform-2, -3 and -4 (computed), across the ladder exit: nobody can step from a ladder onto a platform, and there is no toe space behind the rungs. The horizontal leg at 5.695 m (pipe 5.39..6.0 m) runs straight through the platform-1 ladder and cage (y 55.35..56.05, computed overlap 0.66 m): the climb from grade is blocked at 5.4 m. These ladders are the only access and escape for every C-1101 nozzle, PSV-1109 and the level instruments. No clash, headroom, access or escape finding: the clash rule does not test ladders and cages, and the headroom rule does not count a pipe rising through a walkway. Section build/layout-section-y55_crop-64-0-80-28.png (the riser through all four platforms); plan build/layout-plan-z4-10_crop-64-46-80-66.png. | high | open | Take AIR-1004 off the column and the ladder. Run the top outlet to a side away from the ladder (for example 30 or 150 deg), and drop it outside the platform handrail with at least 0.75 m from the ladder and cage (ASSUMED). Keep the 5.7 m leg out of the ladder bay. Ask plantcode to test pipes against ladder rails, cages and the climbing space, and against the walkway they pass through vertically. |
| 2026-10-22-layout-review6#2 | layout | CHW-1001 S6, C-1101 platform-1..3 | The chilled water inlet CHW-1001 S6 (DN150) rises at [74.571, 52.0] from 3.916 to 19.833 m and then turns into nozzle N4 at r 2.234. That is r 2.571 at 0 deg, the middle of the 1.0 m walkway (r 2.1..3.1, arc 345..195). It passes through the gratings of platform-1 (6.3) and platform-2 (11.3), and ends 1.03 m above platform-3 (18.8). It leaves 0.39 m on the shell side and 0.45 m on the handrail side (computed): too narrow to pass to the 345..0 deg end of each platform. D-039 (2) moved the CW inlet N3 to 270 deg for this reason, but did not move this riser. | medium | open | Run the CHW riser outside the platform handrail (r > 3.2) and come in radially at N4, as CW-1001 now does, or put N4 at the end of the arc. Same rule request as #1 (a pipe through a walkway). |
| 2026-10-22-layout-review6#3 | layout | PR2/ladder-end, LIN-3001 S2, LOX-3001 S2 | The PR2 end ladder (generated, base [141.4, 104.6], top 8.5 m, rails to 9.6 m, cage y 104.6..105.3 from 2.3 m) is crossed by the two cold box product lines. LIN-3001 S2 runs north along x 141.732 at 5.426 m, through the cage (computed overlap 0.09 m). That is head height for the climber. LOX-3001 S2 rises at [141.124, 103.626] to 9.522 m and runs north along x 141.124, over the ladder top and through the handhold extension and the cage top (computed overlap 0.15 m). That is the step-off onto the rack. Both routes were re-pinned in this round (D-039 (3), D-040 (3)). Section build/layout-section-x141.4_crop-98-0-120-14.png shows both lines across the cage. | medium | open | Move the ladder to a free bay of PR2, or re-pin LIN-3001 / LOX-3001 S2 west of the ladder (x < 140.9) and under or beside its top. Same rule request as #1. |
| 2026-10-22-layout-review6#4 | layout | PR3/ladder-end, VNT-4002 S3, VNT-4003 S1 | The PR3 end ladder (base [180.9, 118.6], top 8.5 m, cage y 118.6..119.3) has the GOX compressor vent VNT-4002 S3 (DN150) on its axis. The vent runs north at x 180.902, 9.552 m, from y 117.6 to 123.5, through the handhold extension and the cage top (computed overlap 0.43 m), so the exit onto the tier is blocked. The GOX vent VNT-4003 S1 passes 0.01 m from the cage at 5.34 m (computed). VNT-4002 is an oxygen vent. | medium | open | Re-route VNT-4002 S3 off the ladder axis, or move the ladder to the other side of the rack end. Keep VNT-4003 0.75 m from the cage (ASSUMED). |
| 2026-10-22-layout-review6#5 | layout | CB-1/LD0, CW-3001 S1 | CW-3001 S1 (DN150) runs west along y 48.062 at 3.916 m, from x 129.137 to 125.5. Its surface is 0.02 m from the LD0 rails at y 48.2 (computed), across the full width of the ladder. LD0 is the caged ladder from grade to P10, the second way down from the cold box platforms (Z-ESC-CB1 basis). The climber has no toe space behind the rungs at 3.9 m. | low | open | Pass CW-3001 at least 0.2 m behind the rungs (ASSUMED, the usual toe clearance), or move it under P10 east of LD0. |
| 2026-10-22-layout-review6#6 | checks | checks/checks.yaml accept, PT-E-2101, IT-JB-A3-1 | Two named tray-span acceptances no longer describe the tray they accept. PT-E-2101 is accepted as a "15.4 m ... 5 cable-ladder posts" run, but the finding now reports 6.6 m. IT-JB-A3-1 is accepted as 15.5 m with 5 posts, but the finding reports 16.0 m. An acceptance by id stays valid when the tray changes, so a reason can quietly go stale. | low | open | Update both reasons to the current length and number of posts. Ask plantcode to report an acceptance whose quoted length differs from the finding, or to accept up to a stated length. |
| 2026-10-22-layout-review6#7 | layout | LIN-4002 S3 | The LIN pump discharge LIN-4002 S3 makes a 1.2 m inverted U at x 144.52, from 5.39 m up to 6.61 m and down again ([144.52, 99.996, 6.61] to [144.52, 103.59, 6.61]). That is a high point in a cryogenic liquid line, where vapour collects. The rest of the vaporizer headers were made free of high points by D-039 (8). | low | open | Pin S3 level at 5.39 m, or under what it climbs over, or put a vent at the high point on the P&ID. |
| 2026-10-22-layout-review6#8 | datasheets | equipment/datasheets/*.yaml | The draft datasheets list nozzles by name, DN and line only, with no orientation, elevation or projection. The layout decisions that the vessel suppliers must build are therefore on no document that goes to a supplier: C-1101 N3 at 270 deg (D-039 (2)), the T-4101 / T-4102 fill nozzles N1 on the north side of the roof (D-039 (3)), the V-2101A/B nozzle positions along the shell, the C-3101 nozzle directions, and hatch H1. The datasheets and the layout cannot be checked against each other. | low | open | Add the nozzle orientation and elevation from layout/equipment-placement.yaml (or the model) to each datasheet, with the source, before the datasheets go out. |
| 2026-10-22-layout-review6#9 | layout | PSV-3123, CB-1 roof | The casing breather PSV-3123 now sits at the south-east roof corner (zone centre [140, 39, 53.5]). It is about 6 m from the roof walkway RF (y 45.2..47) across the casing roof, which is not a declared walking surface. No way to inspect, test or replace the breather is modelled, and it lies 2 m from the corner (D-039 (4)). | low | open | Declare a short roof walkway or a guarded access strip from RF to the breather, kept outside Z-N2-CASING and worked under the purge isolation of D-031, or state that the breather is serviced from a work platform. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-22-layout-review5#1 | AIR-3005 through the cold box stair ST1 at head height | high | closed 2160cc3 | ST1 box now [134.727, 48.7, 0, 140.5, 50.5, 11.1] (`out: 1.7`). AIR-3005 S1 at y 48.2, 8.254 m: its top at y 48.337 is 0.36 m clear of the stair box. No pipe enters any of the five stair boxes, and no pipe is within 2.1 m above any ST tread or landing (computed). Section build/layout-section-y48_crop-115-0-150-58.png |
| 2026-10-22-layout-review5#2 | lines across P10 at 1.6 m and step-overs | medium | closed 2160cc3 | GOX-4001 at 12.65 m (od 0.508), GAN-4001 at 12.4 m, LOX-3001 at 12.3 m over P10 (grating 10.0), and UN-3001 at 9.03 m under the P10 steel. Nothing within 2.1 m above the P10 grating (computed). No step-over on P10. Plan build/layout-plan-z9-12.5_crop-122-44-145-54.png |
| 2026-10-22-layout-review5#3 | stair flight across hatch H1, LV-3101 / FV-3106 | medium | closed 2160cc3 | P20 (y 47.2..48.7) is free in front of H1, and the ST3 flights are at y 48.7..50.5. LV-3101 / FV-3106 at y 46.6 are not in the operability list. The perlite-retaining valve box is left to the cold box vendor (D-039 (1)). Plan build/layout-plan-z19.5-22_crop-122-44-145-54.png |
| 2026-10-22-layout-review5#4 | VNT-4006 and VNT-4004 zones lost | medium | closed 2a7529c | No layout-zone-source in `layout build --check`. Z-O2-VENTS has a sphere at [171.0, 64.16, 17.11] and Z-N2-VENTS one at [189.0, 116.5, 12.0] (plant-model.yaml zones) |
| 2026-10-22-layout-review5#5 | tank fills over the tank stair landing and roof platform | medium | closed 2160cc3 | Fill nozzles N1 on the north side of the roofs. No pipe within 2.1 m above any T-4101 / T-4102 tread, landing or roof platform (computed). Plan build/layout-plan-z0-3_crop-115-100-160-135.png |
| 2026-10-22-layout-review5#6 | breather zone over the LD4 head | low | closed 2160cc3 | Z-N2-CASING centre [140, 39, 53.5], 16 m from the LD4 head [126.5, 48.2, 53]. No layout-egress-zone finding. Breather access: see #9 |
| 2026-10-22-layout-review5#7 | 0.6 m walk beside the scissor flights | low | closed 2160cc3 | The flights are outside the platforms. The walk between flights is the full 1.5 m platform. No layout-landing-width finding |
| 2026-10-22-layout-review5#8 | wildcard tray-span acceptance, unused LIN-3001 tier entry | low | closed 8f227ff | 17 acceptances by name (checks.yaml lines 226..259), no wildcard, no accept-unused. PT-K-4102-M added in 521f5c2. Two reasons are stale (#6) |
| 2026-10-22-layout-review5#9 | PSV-3114 / PSV-3116 outlet legs across RV | low | closed 2160cc3 | VNT-3002 S1 / VNT-3003 S1 come up through the roof under the valves ([128.4, 43.3] and [130.6, 43.3] to 53.75 m). The outlets S2 rise straight from 53.75 to 58.25 m. No level leg over RV (computed) |
| 2026-10-22-layout-review5#10 | out-and-back loops at the vaporizers, VNT-4003 pocket | low | closed 8f227ff | LOX-4002 S7 and LIN-4002 S7 run from the 1.2 m header straight up to the inlets. The VNT-4003 pocket is kept with a reason in D-039 (8): dry GOX, and a drain would add an O2 release point. LIN-4002 S3 still has a hump (#7) |
| 2026-10-22-layout-review3#2 | PSV-3114 / PSV-3116 tailpipes free 4.5 m above the valves | low | open | No guide in structures.yaml or routing.yaml. D-039 (9) defers it to the stress engineer with the reaction forces. Outlets still at 58.25 m |
| 2026-10-22-layout-review3#3 | layout-operability warnings | low | open | 27 now (was 71): 0 transmitters, 27 valves, all listed in D-040 (6) as needing platforms or relocation. Among them are PV-4109 / PV-4110 (12.6 / 13.7 m), XV-4133 on the GOX BL bleed VNT-4006, and the BL station HV-4129 / HV-4130 / XV-4118 / XV-4119 / XV-4132 (9.4..10.6 m) |
| 2026-10-22-layout-review3#4 | rack free spans | low | open | 21 layout-free-span and 75 layout-support-missing (`layout report`). No intermediate steel |
| 2026-10-22-layout-review3#5 | lifting cases for the lifting study | low | closed 797e8b6 | `plantcode layout lifting`: 14 lifts, every lane clear, gate lifting-study ok. Heaviest K-4101: 52 t gross, 69.3 t chart capacity at 12.5 m from Z-PAD-A4. The crane choice is left to the contractor (D-041 (7)) |
| 2026-10-22-layout-review3#6 | casing penetrations not declared | low | closed fa9d617 | 10 openings in CB-1 (structures.yaml lines 62..71), 0 layout-wall-penetration |
| 2026-10-22-layout-review3#7 | AHU-1 supply mains in the B1 crane hook path | low | closed fa9d617 | MAC-HALL terminals along the walls (y 23.2 / 46.8, x 37.2 / 70.8) at 9.3 m. They are under the crane runways at 10.5 m (y 22.5 / 47.5) and outside the bridge's hook travel |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | Still not modelled. D-039 (9) leaves it to the cold box vendor's drawing |

## Drawing
No P&ID changed on the branch (`plantcode diff main --list`). validate: P-01 0 / 0 / 0, P-02
0 / 0 / 0, P-03 3 line-crossing (accepted), P-04 1 line-crossing (accepted). Tiles not read.

## Layout
`plantcode layout build --check`: "layout/plant-model.yaml is up to date", 0 layout-zone-source.

`plantcode layout report` at 521f5c2:
- lines: 76. 73 routed and 3 skipped: GAN-3002 and LN-3002 (internals, D-028) and VNT-3004
  (the casing breather). 0 unrouted.
- chains per method: astar 41, astar_coarse 2, open 20, pinned 71, rack 30. No `direct`.
- chains per reason: local: above the pipe-way 9, pipe-way 11, pump run at grade 6, rack
  detour too long 3, rack run too short 2, short run 12; open end 20; pinned 71; rack: across
  areas 10, battery limit at a rack end 13, crosses a road 1, longer than local_max_m 6.
- rack fill: PR1 5 m 55 %, 7 m 34 %, 9 m 21 %; PR2 6.5 m 21 %; PR3 6.5 m 48 %, 8.5 m 18 %.
- model findings per rule:
  - clash-* 0 (but see #1, #3, #4), headroom 0 (but see #1, #2), access-blocked 0;
  - access-enclosed 1 (E20, accepted), zone-crossing 0, separation 0, vent-outlet 0;
  - wall-penetration 0, tier 0, escape-ways 0, escape-travel 0, landing-width 0,
    egress-zone 0, operator-unknown 0, lifting 0, laydown 0, pad-overlap 0, spacing 0,
    building-spacing 0, zone-source 0;
  - operability 27 (review3#3), free-span 21 and support-missing 75 (review3#4);
  - tray-span 17 (each accepted by name, #6), tray-zone 2 warnings (accepted, LOX pump
    motors) and 4 infos (N2 zones), tray-separation 1 (accepted), nozzle-unconnected 2 info.
- objects: 45 equipment, 143 generated and 71 pinned pipes, 8 declared platforms, 3
  structures, 26 zones. No step-over on a walking level outside the casing. The two step-overs
  that remain are on the E20 deck inside the casing.
- validate: 0 errors, 81 warnings.
- `plantcode check`: every concept and basic gate passes except `layout-review` (review5 is
  stale at 521f5c2). In the detail stage, `datasheets` fails (39 drafts, D-042, as intended).
- `plantcode layout lifting`: 14 maintenance lifts with a crane and a clear lane (E-1101,
  E-1102 and E-1103 by the B1 crane; the others from pads Z-PAD-A2, -A3S, -A4, -A4C, -A4N,
  -A5 and -A5N). No crane chart, as intended (D-041 (7)).

PNGs read (build/, rendered at 521f5c2):
- build/layout-plan.png (plot plan: areas, racks, pads, zones, the tank area and V1)
- build/layout-section-y48_crop-115-0-150-58.png (north face: stair ST1..ST5 beside the
  platforms, AIR-3005 under P10 outside the stair)
- build/layout-plan-z9-12.5_crop-122-44-145-54.png (P10 level: no line across the platform)
- build/layout-plan-z19.5-22_crop-122-44-145-54.png (P20 level: H1 with LV-3101 / FV-3106,
  stair outside the platform)
- build/layout-section-y55_crop-64-0-80-28.png (C-1101 north side: AIR-1004 dropping through
  all four platforms, #1)
- build/layout-plan-z4-10_crop-64-46-80-66.png (C-1101 at 4..10 m: AIR-1004 leg north over
  the ladder, CHW-1001 riser, #1, #2)
- build/layout-section-x141.4_crop-98-0-120-14.png (PR2 end ladder crossed by LIN-3001 and
  LOX-3001, #3)
- build/layout-section-x181_crop-112-0-128-14.png (PR3 end ladder and VNT-4002, #4)
- build/layout-plan-z0-3_crop-115-100-160-135.png (tank area: fill lines on sleepers, tank
  stairs south-west, pumps)

## Checked and fine
- Cold box access: the stair stands outside the platforms, each flight lands on the platform
  edge, and the platforms in front of the casing are free. H1 has standing space on P20. No
  pipe is in any stair box, and nothing is within 2.1 m above P10..P40, RF, RV or RF-out
  (computed).
- Tanks: tank stairs, landings and roof platforms are clear (computed). The LOX / LIN tanker
  fill valves HV-4146 / HV-4147 are at 1.0 m on sleepers from the truck bay to the tanks, and
  do not cross the tank stair feet in the south-west.
- O2 / N2 vents: every vent has its zone (Z-O2-VENTS 6 spheres, Z-N2-VENTS 7, V1). 0
  vent-outlet and 0 egress-zone findings. VNT-4006 is 6.1 m above the PR1 trays.
- Operability: 0 transmitters out of reach. The declared chain wheels (BV-P1101A/B, HV-3118,
  HV-4138 / HV-4139) are on manual isolation valves in infrequent use only. Extension spindles
  and remote operators are within 6 m, as the core rule checks them (D-040).
- Lifting: every maintenance lift has a pad, a radius and a clear lane, and the erection lifts
  are listed separately with their ASSUMED weights (D-041 (6)).
- HVAC: the MAC-HALL mains follow the walls under the crane runways.
- Separations and spacing: no layout-separation, spacing or building-spacing finding.
- Datasheets: one draft per equipment item. Values carry a source or `assumed: true`, and 66
  are TBD. The diameters and heights match the equipment list that the layout uses (T-4101
  7.4 x 10.4 m checked).

## Not checked
- Structural design of the north-face stair tower (now 1.7 m out on the unbraced face), the
  platforms, the racks and the ladder supports: structural engineer.
- Pipe stress, supports, the tailpipe guides and the AIR-1004 support once it is re-routed:
  piping stress engineer.
- The vent and inert study (zones ASSUMED, D-031), crane selection and the lifting plan
  (D-041 (7)), fire and noise of B1 / B2: competent persons, crane contractor, fire engineer.
- Escape travel distances from the C-1101 / C-1102 platforms against the site standard (the
  rule criteria are package values).
- The 75 support-missing infos and the 27 operability warnings one by one. The cost
  estimate (D-043) is outside the layout scope.
