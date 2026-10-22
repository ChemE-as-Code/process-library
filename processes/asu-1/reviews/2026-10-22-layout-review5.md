---
topic: layout
reviewed_commit: 0530ede8e3c4f0ec18109a55ba1d587180dcaa8b
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 0530ede8e3c4f0ec18109a55ba1d587180dcaa8b, relation: depends-on}
  - {path: DESIGN.md, revision: 0530ede8e3c4f0ec18109a55ba1d587180dcaa8b, relation: depends-on}
reviewer: Claude (independent review agent; did not author D-025..D-038, the layout files or the fixes in 0530ede)
reviewer_kind: agent
branch: layout-detail
merge: pending
---
# Review: layout, fifth review (independent) of the detail branch

Independent layout review of branch `layout-detail` at 0530ede (the fixes of the fourth review,
D-038), after reviews/2026-10-22-layout-review4.md (13e07b4). The reviewer did not design the
layout or make the fixes. plantcode ran from the core worktree `feat/layout-detail` (dc5b342).
Coordinates are site metres from `layout/plant-model.yaml`; distances measured with
`plantcode show <tag> --layout` or computed from the model coordinates quoted (stated as
computed: a scan of every pipe against every grating, tread and landing box of the model, pipe
radius plus insulation, 2.1 m walkway headroom). No layout file was changed by this review.

Verdict: **not acceptable for a stage sign-off** while #1 (high) is open. The fixes of review4
work in plan: the cold box platforms, stair and ladders are now outside the casing, the tank
outlets are clear of the tank stairs, the compander valves stand at grade outside the casing,
the MV cables, B2, the transformer yard and the pads are sound. The new access steel was not
checked against the pipes that leave the casing on the same face: the pinned booster suction
AIR-3005 runs through the only cold box stair at head height, the 10 m platform is crossed by
four lines between the stair and the ladders, and the JT valve hatch is behind a stair flight.
The headroom rule only looks at roads and escape zones at grade, so none of this is reported.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-22-layout-review5#1 | layout | AIR-3005 S1, CB-1 stair ST1 | The booster suction AIR-3005 (DN250, od 0.273, pinned in piping/routing.yaml by 0530ede) runs east at 8.254 m along y 48.2 from [133.414, 48.2, 8.254] to [142.6, 48.2, 8.254], straight through the stair tower ST1 (box [134.727, 47.2, 0, 140.5, 49.0, 11.1]). Pipe bottom 8.117 m, pipe y 48.063..48.337 (computed). It passes 1.45 m above the mid landing CB-1/ST1/landing-1 (centre [140.05, 48.1, 6.652], 0.9 x 1.8 m) and less than 2.1 m above the treads of the top ~1 m of flight-1 (band y 48.15..48.95, 3.33 to 6.67 m). It also crosses the outer handrail CB-1/ST1/flight-2/handrail-b (y 48.05, 50 mm, from [139.6, 48.05, 7.667] to [135.627, 48.05, 11.0]) at about x 138.9 with about 0.01 m overlap (computed). ST1 is the only stair of the 53 m cold box and the primary escape route from every platform. Anyone climbing to the landing has to stoop under a DN250 line. No clash, headroom or escape finding: the headroom rule checks only roads and escape zones at grade (core `model_rules.py`, rule `headroom`). Sections build/layout-section-y48_crop-128-4-144-24.png, build/layout-section-y48_crop-115-0-150-58.png. | high | open | Re-pin AIR-3005 clear of the stair box: run it east at or above 11.5 m above P10 headroom, or round the west end. Keep 2.1 m (ASSUMED) above every tread nosing and landing. Ask plantcode to apply walkway headroom to declared and generated stairs, landings and platforms. |
| 2026-10-22-layout-review5#2 | layout | CB-1 P10, GOX-4001, GAN-4001, UN-3001, LOX-3001 | The 10 m access platform P10 (grating top 10.0, x 126..141, y 47.2..48.7) is the only way from the stair head (ST1 arrives at x 135.6) to the west ladders LD0 / LD1 (x 126.5 / 127.5, y 48.2), the second way down. Four lines that leave the north casing face cross it on that route (computed). GOX-4001 S1 is DN500 at x 134.1, z 12.062, with its bottom 1.81 m above the grating. GAN-4001 S1 is DN250 at x 133.1, z 11.71, bottom 1.57 m. UN-3001 S1 is at x 131.1, z 10.39, top 0.36 m above the grating (generated step-over-4, `review_needed`). LOX-3001 S1 is at x 129.0, z 10.52, 0.45 m above (step-over-2, deck 10.70, `review_needed`). An operator walking to the ladders, or escaping to them when the stair side is blocked, ducks under two lines at 1.6 to 1.8 m and climbs over two step-overs on a 1.5 m wide platform. escape-ways and escape-travel are 0 because no rule checks platform headroom. Plan build/layout-plan-z9.9-12.2_crop-124-44-143-52.png. | medium | open | Lift GOX-4001 and GAN-4001 so their bottoms are at least 2.1 m above P10 (penetrations at or above about 12.4 m), or bring them out above P10 and drop them clear of the platform. Lower UN-3001 / LOX-3001 under the P10 steel, or accept the step-overs with a reason after review. Same rule request as #1. |
| 2026-10-22-layout-review5#3 | layout | LV-3101, FV-3106, hatch H1, stair ST3 | The JT valves sit 0.4 m inside the north casing wall at the access hatch H1: LV-3101 at [138.0, 46.6, 20.657] and FV-3106 at [138.6, 46.6, 21.2]. H1 is on the north side with offset 2.1 from the east end, so x 137.7..138.9, sill 20.3, top 21.5. D-038 (3) says they are "worked from P20 outside". The stair flight CB-1/ST3/flight-0 starts on P20 at [139.6, 47.25, 20.0] and rises west to [135.627, 47.25, 23.333] in the band y 47.25..48.05, directly against the casing face. In front of the hatch (x 137.7..138.9) its treads are at 20.6..21.6 m (computed), that is across the hatch opening itself. Nobody can stand on P20 in front of H1, and the extended bonnets and actuators cannot be removed through it. A hatch into the perlite also needs a perlite-retaining valve box or sleeve, which is not modelled. The operability rule sees the valves 0.6 m in plan from P20 and reports nothing. Supersedes review4#3 for these two valves (the compander valves of review4#3 are fixed, see Previous findings). | medium | open | Move H1 and the valves west of the stair (x < 135), or move the stair flights off the hatch. Model the cold valve box at the wall. Ask plantcode to count stair flights as obstructions of the operating space in front of a valve. |
| 2026-10-22-layout-review5#4 | layout | Z-O2-VENTS VNT-4006, Z-N2-VENTS VNT-4004 | Since 0530ede the two large vents of review4#4 have no zone volume. `plantcode layout build --check` warns `layout-zone-source`: "source VNT-4006: line VNT-4006 has no open end" and the same for VNT-4004. Both are now pinned routes (piping/routing.yaml lines 75, 105) ending in open air. The model's Z-O2-VENTS holds only VNT-4001, VNT-3001 and VNT-3002, and Z-N2-VENTS has no VNT-4004 (`plant-model.yaml` zones). `plantcode validate` does not repeat the build warning and gate layout-3d still passes. So the GOX battery limit bleed, a primary O2 release, and the off-spec GAN divert (the whole GAN-4001 flow) are missing from the plot plan, from the vent-outlet rule and from the tray-zone rule. D-038 (4)'s "no vent-outlet finding" covers neither of them. The geometry is fine, computed by hand: VNT-4006 outlet [171.0, 64.16, 17.11] is 6.1 m above the PR1 trays at 11 m, and VNT-4004 outlet [189.0, 116.5, 12.0] is in V1. | medium | open | Name the outlets so the zones resolve (a placed outlet tag or nozzle), or ask plantcode to treat the free end of a pinned vent route as an open end. Make validate (or gate layout-3d) carry `layout-zone-source`. Rebuild and confirm 0 vent-outlet and tray-zone findings with the two zones present. |
| 2026-10-22-layout-review5#5 | layout | LOX-3001 S2 at T-4101, LIN-3001 S2 at T-4102 | The tank fill lines cross the tank roof access. LOX-3001 S2 runs [130.48, 112.0, 9.522] up to 11.022, then west to [126.48, 112.0, 11.022] and down into the roof nozzle (DN40 plus 50 mm insulation). It crosses the T-4101 stair landing (centre [129.194, 111.535, 9.748], top 9.77) at 1.18 m and runs along the roof platform (centre [127.882, 111.681, 10.06], top 10.08) 0.87 m above it (computed). That is waist height on the only way onto the LOX tank roof (PV-4109, PSV-4123, the level and pressure instruments). LIN-3001 S2 at 13.426 m crosses the edge of T-4102/roof-platform (top 12.21) 1.14 m above it (computed). No rule reports it, because tank stairs and roof platforms count as walking levels only in the vent-outlet rule. Section build/layout-section-y112_crop-110-0-165-22.png. | medium | open | Bring the fill lines onto the roof on the side away from the stair and platform (the west nozzles, as done for N2 / N3 by D-038 (2)), or run them under the platform steel. Keep 2.1 m headroom or a proper step-over on the tank access. |
| 2026-10-22-layout-review5#6 | layout | Z-N2-CASING, LD4, RF-out | The casing breather zone is now correctly centred at the breather, [127, 46, 53.5], r 5 m, 0.5 m above the roof walkway RF. That centre is 2.3 m (computed) from the head of the caged ladder LD4 ([126.5, 48.2, 53.0]), which is the roof's second way down, and covers the west 4 m of the new landing RF-out. The stair head (ST5 at x 135.6) is outside the zone. A person escaping the roof by the ladder starts in the O2-deficient zone. The zone basis relies on an O2 monitor and an isolated purge for roof access, which does not help in an upset. | low | open | Put the breather PSV-3123 at the east or south end of the roof (or on a short stack above RF headroom plus the radius), away from LD4, or move LD4 to the other end. |
| 2026-10-22-layout-review5#7 | layout | CB-1 ST1..ST5 | The stacked stair is a scissor arrangement: every flight arrives at x 135.6 in the band next to the casing (y 47.25..48.05), and the next flight starts at x 139.6 in the same band. At each platform the user walks 4 m east beside the rising flight, in the strip between its outer stringer and handrail (y 48.05) and the platform edge (y 48.7), about 0.6 m clear (computed). That is the minimum walkway width, not the 0.8 m usual for a main access and escape route (ASSUMED), and it is the only route to the next flight, the hatch H1 and the west half of each platform. | low | open | Widen the platforms over the stair bay to at least 2.2 m, or turn the stair into a true switchback with landings at both ends outside the platform width. |
| 2026-10-22-layout-review5#8 | checks | checks/checks.yaml accept | The new acceptance `layout/plant-model.yaml#layout-tray-span:*` is a wildcard. It accepts every present and future tray-span finding, including long runs such as IT-JB-A2-1 (30.8 m) and PT-M-P-4101A (19.8 m), with one reason. The rereview#7 acceptance of the LIN-3001 tier finding no longer names a finding (`plantcode.accept-unused`). | low | open | List the accepted tray-span ids, or accept by prefix per area with the post spacing basis. Remove the unused LIN-3001 tier entry. |
| 2026-10-22-layout-review5#9 | layout | RV, VNT-3002 S2, VNT-3003 S1 | The PSV-3114 / PSV-3116 outlet legs run level across the relief valve platform RV at 53.75 m, 0.67 m above its grating (computed: VNT-3002 S2 at [128.0, 43.0, 53.75], VNT-3003 S1 last leg [130.6, 44.171, 53.75] to [130.6, 43.3, 53.75]), before rising to 58.25 m. They are knee-high obstacles on the platform where the valves are tested and removed. | low | open | Turn the outlet elbows up directly at the valves, or lower the legs under the RV grating. |
| 2026-10-22-layout-review5#10 | layout | LIN-4002 S7, LOX-4002 S7, VNT-4003 S1 | Out-and-back jogs remain after the LOX-4002 fix. LIN-4002 S7 still loops 2.5 m out and back at 5.68 m ([162.34, 125.09] to [162.34, 127.59] to [167.34, 127.59] to [167.34, 125.59]). LOX-4002 S7 loops 2.5 m north round E-4105A at 4.0 m ([162.5, 95.0] to [162.5, 97.5] to [168.0, 97.5] to [168.0, 95.0]). The O2 vent VNT-4003 S1 dips from 10.286 to 9.162 m and back to 10.286 m, a low point in an oxygen vent. Supersedes the remaining part of review4#9 (the LOX-4002 high points are fixed). | low | open | Pin the vaporizer branches straight and the VNT-4003 rack transition without a pocket, or drain and justify the low point on the P&ID. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-22-layout-review4#1 | CB-1 platforms and ladders inside the casing, stair tower joined to none | high | closed 0530ede8e3c4f0ec18109a55ba1d587180dcaa8b | P10..P40 and RF-out at y 47.2..48.7 outside the north wall (y 47.0..47.2), e.g. CB-1/P10/grating centre [133.5, 47.95, 9.985], 15 x 1.5 m. ST1..ST5 from grade to RF-out (ST1 box [134.727, 47.2, 0, 140.5, 49.0, 11.1]), LD0..LD4 at y 48.2. Only `layout-access-enclosed` left is E20, the E-3102 support deck, accepted. Escape route Z-ESC-CB1 from the stair foot. Section build/layout-section-y48_crop-115-0-150-58.png. Obstructions of the new access: #1, #2, #3, #7 |
| 2026-10-22-layout-review4#2 | tank relief and vent outlets at the tank stairs | high | closed 0530ede8e3c4f0ec18109a55ba1d587180dcaa8b | PSV-4123 outlet [120.806, 112.0, 10.4] is 8.4 m from the T-4101 landing. PV-4109 outlet [122.2, 112.0, 13.413] is 5.7 m in plan from the roof platform. PSV-4124 [145.406, 112.0, 12.6] and PV-4110 [146.071, 112.0, 13.911] are more than 7 m from the T-4102 landing and platform (computed). 0 layout-vent-outlet. Section build/layout-section-y112_crop-110-0-165-22.png |
| 2026-10-22-layout-review4#3 | valves inside the casing | medium | superseded by 2026-10-22-layout-review5#3 | Fixed at grade outside the casing: AIR-3002 check valve [136.2, 36.0, 1.0], PSV-3119 [136.2, 32.5, 1.5], UV-3120 [137.7, 34.5, 1.0], XV-3117 [134.216, 37.55, 1.5]. LV-3101 / FV-3106 at hatch H1 cannot be reached (#3) |
| 2026-10-22-layout-review4#4 | VNT-4004 in PR1, IT-PR1-8 in the VNT-4006 zone | medium | closed 0530ede8e3c4f0ec18109a55ba1d587180dcaa8b | VNT-4004 pinned to V1, outlet [189.0, 116.5, 12.0]. VNT-4006 outlet at 17.11 m, 6.1 m above the PR1 trays (computed). Both zones are now missing from the model (#4) |
| 2026-10-22-layout-review4#5 | MV tray over K-4101 in its lift path | medium | closed 0530ede8e3c4f0ec18109a55ba1d587180dcaa8b | No PT-M-K-4101 in the model. Feeder K-4101-MV to a pit at [169.0, 71.9] and a trench (electrical-list.yaml). The K-4101 lifting finding names FW-4101 only |
| 2026-10-22-layout-review4#6 | B2 2 m from B1 without a declared separation | medium | closed 0530ede8e3c4f0ec18109a55ba1d587180dcaa8b | Separation B2-B1 2 m declared with the REI 120 south wall and no openings facing B1 (site-plan.yaml, D-038 (6)). `show B2 --layout`: B1 2.0 m, FW-TR 1.0 m, R4 8.0 m. No layout-building-spacing finding. The fire and noise assessment stays open in D-038 |
| 2026-10-22-layout-review4#7 | crane pad Z-PAD-A5 on PR2 | medium | closed 0530ede8e3c4f0ec18109a55ba1d587180dcaa8b | Z-PAD-A5 box [157, 83, 177, 91], 12 m east of PR2 (x 145) and 1.5 m off R2 (y 75.5..81.5). No pad-overlap and no E-4105A/B lifting finding |
| 2026-10-22-layout-review4#8 | Z-N2-CASING centre below the roof | low | closed 0530ede8e3c4f0ec18109a55ba1d587180dcaa8b | Centre [127, 46, 53.5]. See #6 for its position against LD4 |
| 2026-10-22-layout-review4#9 | LOX-4002 high points, out-and-back jogs | low | superseded by 2026-10-22-layout-review5#10 | LOX-4002 S1..S5 level at 4.0 m without high points. The jogs remain (#10) |
| 2026-10-22-layout-review4#10 | transformer yard not modelled | low | closed 0530ede8e3c4f0ec18109a55ba1d587180dcaa8b | Z-TR1 [13, 50.5, 19, 56.2], Z-TR2 [13.5, 57.2, 18.5, 60], fire wall FW-TR (REI 120, 5 m), B2 west wall REI 90, switchgear door D2 moved to the north wall |
| 2026-10-22-layout-review4#11 | B1 roof title 32 t | low | closed 0530ede8e3c4f0ec18109a55ba1d587180dcaa8b | building.yaml B1 RF: "Roof (overhead crane runway below, 40 t ASSUMED)" |
| 2026-10-22-layout-review3#1 | MV tray to K-1101 over the B1 roof | medium | closed 0530ede8e3c4f0ec18109a55ba1d587180dcaa8b | No PT-M-K-1101 in the model. K-1101 is `skip`ped in electrical-list.yaml: MV cable through the B2 cable cellar and a 2 m trench into the B1 floor trench (D-038 (5)) |
| 2026-10-22-layout-review3#2 | PSV-3114 / PSV-3116 tailpipes free 4.5 m above the valves | low | open | No guide in structures.yaml or routing.yaml. Outlets still at 58.25 m. See also #9 |
| 2026-10-22-layout-review3#3 | layout-operability warnings | low | open | Still 71 (`layout report`). The rule misses LV-3101 / FV-3106 behind the stair (#3) |
| 2026-10-22-layout-review3#4 | rack free spans | low | open | 23 layout-free-span and 69 layout-support-missing; no intermediate steel; LOX-4002 S5 runs 23.5 m at 4 m over open ground without steel |
| 2026-10-22-layout-review3#5 | lifting cases for the lifting study | low | open | 8 layout-lifting (E-2101, KT-3101, K-3101, K-4101, E-4101, E-4102, K-4102, E-4106B) |
| 2026-10-22-layout-review3#6 | casing penetrations not declared | low | open | 12 layout-wall-penetration infos on CB-1, none pinned. Only the hatch H1 is declared |
| 2026-10-22-layout-review3#7 | AHU-1 supply mains in the B1 crane hook path | low | open | AHU-1 / MAC-HALL in layout/hvac.yaml unchanged (0530ede changed only the AHU-2 note) |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | Still not modelled. D-038 (3) now puts XV-3117 "in the expander's casing extension", which the model does not have |

The closed and accepted findings that review4 spot-checked stay closed at 0530ede: rereview#1
(PSV-3114/3116 on RV, outlets 58.25 m), rereview#3 (VNT-4007 outlet 14.74 m; VNT-4006 now 17.11
m), rereview#5, layout#5 (WN-1002 outlet 27.62 m, zone visible in build/layout-section-y68.png),
layout#8 / #9 (no FW-4101 or B1 wall-penetration finding), layout#16. The rereview#7 acceptance
(LIN-3001 layout-tier) no longer has a finding: no layout-tier finding is reported at all (#8).

## Drawing
No P&ID in scope and none changed on the branch since review4. validate: P-01 0 / 0 / 0 / 0, P-02
0 / 0 / 0 / 0, P-03 0 line-through-label, 3 line-crossing (accepted), P-04 0 line-through-label,
1 line-crossing (accepted). Tiles not read.

## Layout
`plantcode layout build --check`: "layout/plant-model.yaml is up to date", with 2
`layout-zone-source` warnings (#4) and the accepted `layout-access-enclosed` (E20).

`plantcode layout report` at 0530ede:
- lines: 76. 73 routed, 3 skipped (GAN-3002 and LN-3002, internal of the double column, D-028;
  VNT-3004, the casing breather), 0 unrouted. 214 of 218 segments.
- chains per method: astar 51, astar_coarse 2, open 20, pinned 41, rack 31, rack+astar_coarse 1;
  no `direct`.
- chains per reason: local: above the pipe-way 9, pipe-way 13, pump run at grade 6, rack detour
  too long 7, rack run too short 2, short run 16; open end 20; pinned 41; rack: across areas 13,
  battery limit at a rack end 14, crosses a road 1, longer than local_max_m 4.
- rack fill: PR1 5 m 58 %, 7 m 42 %, 9 m 21 %; PR2 6.5 m 21 %, 8.5 m 14 %; PR3 6.5 m 48 %,
  8.5 m 34 %.
- model findings per rule: clash-* 0, headroom 0 (but see #1, #2, #5), access-blocked 0,
  access-enclosed 1 (E20, accepted), zone-crossing 0, separation 0, vent-outlet 0 (but see #4),
  escape-ways 0 and escape-travel 0, spacing 0, wall-penetration 12 info (review3#6), tier 0,
  operability 71 (review3#3), free-span 23 and support-missing 69 (review3#4), lifting 8
  (review3#5), laydown 0, tray-span 17 (all accepted by a wildcard, #8), tray-zone 2 (accepted,
  LOX pump motor trays), tray-separation 1 (accepted, D-036), nozzle-unconnected 2 info (D-028).
- platforms 8 declared, CB-1 levels P10, E20, P20, P30, P40, RF, RV, RF-out. Stairs ST1..ST5
  pinned from the proposals, ladders LD0..LD4. 4 generated step-overs `review_needed` (two on P10,
  #2; two on the E20 deck inside the casing, not a walking level). The E20-out access proposal is
  not pinned (E20 accepted as no access level).
- validate: 0 errors, 135 warnings. `plantcode check`: every basic gate passes except
  `layout-review` (review4 is stale at 0530ede); detail gate `datasheets` fails (no datasheets).

PNGs read (build/, rendered at 0530ede):
- build/layout-plan.png (plot plan)
- build/layout-section-y68.png (along PR1, looking north: tiers, trays at 11 m, the VNT-4007 and
  WN-1002 zones; no VNT-4006 zone drawn, #4)
- build/layout-section-x129.png (through the cold box, looking west: casing to 53 m, P10..P40
  and RF-out outside the north wall, the roof zones, PR1 frame)
- build/layout-section-y48_crop-115-0-150-58.png (along the north face: platforms, the scissor
  stair ST1..ST5, AIR-3005 through ST1, #1, #7)
- build/layout-section-y48_crop-128-4-144-24.png (crop of ST1 / ST2 / ST3: AIR-3005 across the
  flights, GOX-4001 / GAN-4001 over P10, #1, #2)
- build/layout-plan-z9.9-12.2_crop-124-44-143-52.png (level plan of P10: the stair, the lines
  crossing the platform, the ladders at the west end, #2)
- build/layout-plan_crop-120-30-150-55.png (cold box and compander: valve station at grade,
  AIR-3005 round the east face, escape zone Z-ESC-CB1)
- build/layout-section-y112_crop-110-0-165-22.png (through T-4101 / T-4102: tank stairs, the
  outlets on the west side, LOX-3001 / LIN-3001 over the stair heads, #5)
- build/layout-plan_crop-5-20-85-75.png (A1: B1, B2, FW-TR, Z-TR1 / Z-TR2, trays into B2)
- build/layout-plan_crop-110-80-195-135.png (A5 and V1: tanks, pumps, vaporizers, pads)
- build/layout-plan_crop-100-15-180-75.png (A3 / A4: cold box, FW-4101, K-4101, pads)

## Checked and fine
- Separations (validate): no layout-separation or building-spacing finding. CB-1 to B1 toppling
  separation kept. B2 to B1 is declared at 2 m with the REI 120 wall (`show B2 --layout`: B1
  2.0 m, R4 8.0 m, PR1 4.0 m).
- Casing access: no platform, ladder or valve that people use is inside the casing. The E20
  acceptance is reasoned (support deck, no access level).
- Tank vents: all four tank outlets are on the far side from the stairs and their 5 m zones are
  clear of the landings and roof platforms (computed above).
- Compander: anti-surge, relief, check and ESD valves at 1.0..1.5 m above grade outside the south
  casing wall, beside K-3101 / KT-3101. The PSV-3119 air tailpipe goes to 3.5 m.
- MV cables: no tray over K-1101 or K-4101 or in their lift lanes. The transformer yard has a
  fire wall, bunds and road access, and the switchgear door is off the yard face.
- Crane pads off racks and roads. Laydowns unchanged. Rack fill below 60 % on every tier.
- Escape route Z-ESC-CB1 from the ST1 foot along the east face to R1; no pipe in it below 2.2 m
  (headroom 0; AIR-3005 crosses it at 8.25 m).
- Vent area V1 and O2 outlets: VNT-4004 now discharges in V1 at 12 m; the large GOX vents
  silenced in V1.

## Not checked
- Structural design: the four platforms, the stair tower and the 53 m roof landing are
  cantilevered off the north face, which is unbraced (`bracing: north: none`, "rely on the
  stiffened casing panels"). The stair, platform and wind loads on that face need the
  structural engineer's check. Also CB-1, RV, FW-4101, FW-TR and the racks.
- Pipe stress, supports, tailpipe and vent reaction forces, tray support steel: piping stress
  and structural engineers.
- The vent and inert study (every zone ASSUMED, D-031), the lifting study (D-034), the B1 / B2
  fire and noise assessment and the transformer oil fire protection (D-038 (6), (7)): competent
  person, crane contractor, fire engineer, electrical engineer.
- The trench routes of the K-1101 and K-4101 MV cables (not in the model or the cable schedule
  length).
- LOX spill containment and drainage at T-4101 and the truck bay (not modelled).
- The 71 operability warnings one by one, the 69 support-missing infos, the 3D viewer.
- The DESIGN.md decision D-038 was read against the model; the process basis behind it was not
  re-derived.
