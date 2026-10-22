---
topic: layout
reviewed_commit: 13e07b49c663004a56bf73008a69c0a1c1741728
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 13e07b49c663004a56bf73008a69c0a1c1741728, relation: depends-on}
  - {path: DESIGN.md, revision: 13e07b49c663004a56bf73008a69c0a1c1741728, relation: depends-on}
reviewer: Claude (independent review agent; did not author D-025..D-037 or the layout files)
reviewer_kind: agent
branch: layout-detail
merge: pending
---
# Review: layout, fourth review (independent) of the detail branch

Independent layout review of branch `layout-detail` at 13e07b4 (the rebuild with solid tank
stairs and davits), after the self review reviews/2026-10-22-layout-review3.md (f1c29ff). The
reviewer did not design the layout. plantcode ran from the core worktree `feat/layout-detail`
(a698adf). Coordinates are site metres from `layout/plant-model.yaml`; distances measured with
`plantcode show <tag> --layout` or computed from the model coordinates quoted (stated as
computed). No file was changed by this review.

Verdict: **not acceptable for a stage sign-off** while #1 and #2 (high) are open. The plot plan,
separations, rack allocation and vent area are sound; the faults are in the detail now
modelled: the cold box access is inside the casing, and the generated tank stairs and roof
platforms sit at the tank relief and vent outlets without any rule seeing them.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-22-layout-review4#1 | layout | CB-1 P10..P40, LD0..LD8, ST1..ST5 | The cold box access platforms P10/P20/P30/P40 (frame extent y 7.2-9, site y 45.2-47.0; e.g. CB-1/P10/grating centre [133.5, 46.1, 9.985], 15.0 x 1.8 m) and all caged ladders LD0..LD8 (base y 46.6, e.g. LD0 [126.5, 46.6, 0]) lie INSIDE the casing: CB-1/wall-north is centred y 47.1 (47.0-47.2), wall-west x 125.9, wall-south y 37.9, `enclosure: {walls: all, height: 53, material: casing}`. That volume is perlite-filled and N2-purged (D-030, notes in structures.yaml): nobody can stand there in operation. The stair tower ST1..ST5 is outside the east face (ST1 box x 141.0-142.8, y 38.5-44.3) and meets no platform (platforms start at y 45.2 and behind the east wall). So the "two ways down from every platform" (D-030 (1), D-032 #11, D-033 (6)) is not real: the roof RF/RV (inside Z-N2-CASING) has one way down (the stair tower) and the faces where the lines leave the casing (north wall, 4-12 m, e.g. UN-3001 at [131.1, 47.1, 10.4], GOX-4001 at 12.1 m) have no platform outside. No rule reports it: escape-ways, escape-travel, access-blocked and vent-outlet are all 0 because the checks accept walking levels inside an enclosure. Section build/layout-section-x129.png. | high | open | Move the access platforms and ladders outside the casing (north face y 47.2-49.0 or cantilevered all round, as D-030 intends: "valves and instruments are brought out to the casing platforms"), join each stair-tower landing to its platform, keep two ways down from the roof; ask plantcode for a rule that refuses platforms, ladders and valves inside a casing or perlite enclosure. |
| 2026-10-22-layout-review4#2 | layout | T-4101 PSV-4123 / PV-4109, T-4102 PSV-4124 / PV-4110 | The generated tank stairs and roof platforms (new solids in 13e07b4) sit at the tank relief and vent outlets. T-4101: the PSV-4123 tailpipe (VNT-4001 S5) ends at [129.194, 112.0, 9.123] pointing up, inside the plan footprint of the stair landing T-4101/stair-landing (centre [129.194, 111.535, 9.748], 0.92 x 1.0 m, rot 353.7 deg; outlet 0.46 m from its centre, 0.63 m below the grating, computed): an O2 relief discharges into the landing that is the only way onto the roof. The continuous LOX boil-off vent PV-4109 (VNT-4001 S2) ends at [124.704, 112.0, 11.855], 1.8 m above the roof platform T-4101/roof-platform ([127.882, 111.681, 10.06]) and 3.2 m from it; its 5 m continuous O2-enriched zone (Z-O2-VENTS) covers the roof platform, the landing and the top of the stair. T-4102: PSV-4124 tailpipe outlet [154.594, 112.0, 10.898] is 0.95 m beside and 0.98 m below the landing ([154.522, 112.948, 11.877], computed); PV-4110 continuous N2 vent at 14.05 m over the roof platform (12.19 m), Z-N2-VENTS covers both. No layout-vent-outlet finding: the rule (and layout-operability, which reports PV-4109 with "the floor below it is 11.5 m down") does not count the generated tank roof platforms and stairs as walking levels. Section build/layout-section-y112_crop-110-0-165-22.png, plan build/layout-plan_crop-110-85-195-135.png. | high | open | Turn the relief tailpipes away from the stair (on the far side of the roof, discharge up to at least 2.2 m + zone radius above the roof platform and landing, as done for PSV-3114/3116 by D-033 (1)); raise the boil-off vents the same way or move the roof access out of the zones; ask plantcode to treat generated tank stairs, landings and roof platforms as walking levels in the vent-outlet and operability rules. |
| 2026-10-22-layout-review4#3 | layout | UV-3120, PSV-3119, XV-3117, AIR-3002 check valve, LV-3101, FV-3106 | Six in-line items are placed inside the cold box casing footprint (x 126-141, y 38-47): warm compander valves UV-3120 anti-surge [132.9, 45.17, 2.11], PSV-3119 [134.21, 38.41, 3.11], XV-3117 [134.5, 38.53, 4.84], the AIR-3002 swing check valve [132.97, 46.1, 3.11], and the control valves LV-3101 [138.0, 42.5, 26.21] and FV-3106 [138.6, 42.5, 28.21] in mid-casing. A relief valve that must be tested, an anti-surge valve and an ESD valve of the compander cannot sit in the perlite; cold control valves are reached through extended bonnets at the casing face, not 4.5 m inside it. None of them has an operability finding. | medium | open | Route the compander lines AIR-3002 / AIR-3006 so their valves stand outside the south casing wall next to K-3101 / KT-3101 (pin the routes); place LV-3101 / FV-3106 at the casing face with a declared casing opening and an outside platform (with #1); a plantcode check for valves inside a casing enclosure. |
| 2026-10-22-layout-review4#4 | layout | VNT-4004, trays IT-PR1-5, IT-PR1-8 | The DN150 off-spec GAN divert vent VNT-4004 (XV-3105, the whole GAN-4001 flow on high O2) discharges at [140.133, 64.794, 10.136], on top of PR1 at the PR1/PR2 junction, 0.86 m below and 0.81 m beside the instrument tray IT-PR1-5 (y 65.6, z 11.0; computed). Its 5 m O2-deficient zone (centre z 10.1) fills the PR1 tiers 5/7/9 m and both tray lanes over x 135-145, where cable pulling and rack maintenance take place (build/layout-section-y68.png). D-025 places VNT-4004 in the vent area V1; D-029 (3) moves only the "small vents" to their items. Likewise IT-PR1-8 (y 65.6, z 11.0) passes 4.0 m from the VNT-4006 GOX bleed outlet [171.0, 64.16, 14.717] (computed), inside Z-O2-VENTS, while D-036 says no zone reaches cables. | medium | open | Take VNT-4004 to V1 over PR1 / PR3 (as VNT-4002 / VNT-4003) or raise its outlet above the tray tier plus the zone radius; record the trays inside O2 / inert zones in D-036 (cable sheath and gland selection) or move the tray lane. |
| 2026-10-22-layout-review4#5 | layout | PT-M-K-4101, K-4101 | The 6.6 kV tray to the GOX compressor motor leaves PR1 at [169.153, 66.4, 11.0], climbs to 12 m and runs 37.4 m south across A4 with no structure under it to [169.153, 29.0, 12.0], then drops vertically onto K-4101 (centre 166.5, 29.0, footprint 161.5-171.5 x 26-32, top 5 m) to 5.4 m. It hangs directly above the 45 t compressor inside the fire wall FW-4101, in the vertical lift that D-034 (4) relies on ("vertical lift above the wall, then slewing over its open east side"). The lifting rule does not look at trays, so the K-4101 lifting warning names only FW-4101. | medium | open | Bring the MV cable in at grade or in a trench from the open east side of FW-4101 (or along the wall top to the motor end), out of the lift envelope; add tray support steel to the model for any tray run off the racks; ask plantcode to include trays in the lifting lane check. |
| 2026-10-22-layout-review4#6 | layout | B2, B1 | The substation and control building B2 (x 20-38, y 50-60) stands 2.0 m from the MAC house B1 (`show B2 --layout`: B1 2.0 m), next to an 8 MW compressor house with its lube oil system and ~85 dB(A) inside (building.yaml notes), and 4.0 m from PR1. No separation B2 to B1 is declared in site-plan.yaml, and D-036 argues the location only from the O2 / inert zones. An occupied control room 2 m from the compressor house needs either a fire-rated (and acoustic) wall on that face or distance. | medium | open | Declare and justify a separation B2-B1 (fire and noise) in site-plan.yaml and D-036, or move B2 west / north; state the wall rating if it stays. |
| 2026-10-22-layout-review4#7 | layout | Z-PAD-A5, PR2, E-4105A/B | Crane pad Z-PAD-A5 (box x 133-143, y 88-100) overlaps the PR2 footprint (x 141-145, its west column line at x 141) by 2 m, and stands on the far side of PR2 from the LOX vaporizers it serves (E-4105A at x 165, E-4105B at x 170, y 95): every lift slews over PR2, its 6.5 / 8.5 m tiers and the 10.5 m trays (the lifting warnings name LOX-4002 and GOX-4004 only). | medium | open | Move the pad east of PR2 (open ground x 146-160, y 88-100) or north beside the vaporizers; keep pads off rack footprints (a plantcode check would help). |
| 2026-10-22-layout-review4#8 | layout | Z-N2-CASING | The casing breather zone is still centred at [127, 46, 50.5], the casing roof of D-030; D-032 (#3) raised the casing and roof walkway RF to 53 m, so the breather (on the roof) is 2.5 m above the zone centre and the zone reaches only 2.5 m above the roof instead of 5 m (to 55.5 m, under the 55.2 m headroom line of RF it is meant to cover). | low | open | Set the centre to the breather position on the 53 m roof (or derive the zone from PSV-3123 placed as a special item). |
| 2026-10-22-layout-review4#9 | layout | LOX-4002 S5, LIN-4002 S7, step-overs | LOX-4002 S5 leaves the PR2 tier: points [130.794, 101.496, 9.63] -> [141.16, 101.496, 8.61] -> [141.16, 95.0, 8.61] -> [141.16, 95.0, 9.63] -> [163.02, 95.0, 9.63] -> [163.02, 95.0, 5.7]: a 21.9 m run at 9.63 m across open ground off any rack with no support steel, and two high points in a LOX line (vapour pockets) around a 1 m dip onto the rack. LIN-4002 S7 loops 2.5 m out and back at 5.68 m. A heuristic scan of the model by the reviewer (legs over 1 m that reverse within three legs) flags 38 out-and-back jogs, some of them ordinary step-overs, e.g. VNT-4003 S1 (O2 vent: low points collect debris and condensate) and CW-1003 S1. | low | open | Pin LOX-4002 along PR2 / a sleeper way to the vaporizers without high points (or slope it and vent the high points on the P&ID); review the step-overs in the cryogenic and oxygen lines in the piping layout. |
| 2026-10-22-layout-review4#10 | layout | B2 transformers TR-1, TR-2 | TR-1 (33/6.6 kV, 16 MVA) and TR-2 (2.5 MVA) "stand outdoors on its west side (not modelled)" (D-036). The strip west of B2 is 8.0 m to the edge of road R4 (`show B2 --layout`), and the switchgear delivery roller door D2 is on that same west face: an oil-filled 16 MVA transformer with its fire separation or wall, oil pit and access does not fit there with D2 kept clear. | low | open | Model the transformer yard (footprints, fire walls or separation, oil containment, access) and move D2 or the yard. |
| 2026-10-22-layout-review4#11 | layout | B1 level RF | The B1 roof level title says "overhead crane runway below, 32 t ASSUMED" while the crane is 40 t (building.yaml `crane: {capacity_t: 40}`, D-034 (2)). | low | open | Correct the title. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-22-layout-review3#1 | MV tray to K-1101 over the B1 roof and in through roller door S1 | medium | open | unchanged at 13e07b4: PT-M-K-1101 points [48.185, 70.4, 11.0] .. [48.185, 49.4, 14.0], [48.185, 20.4, 14.0], [48.185, 20.4, 6.0], [48.185, 30.0, 5.278]; build/layout-plan_crop-15-20-85-75.png |
| 2026-10-22-layout-review3#2 | PSV-3114 / PSV-3116 tailpipes free 4.5 m above the valves | low | open | no guide in the model; outlets still at 58.25 m (zone centres [128, 43, 58.25], [131, 43, 58.25]) |
| 2026-10-22-layout-review3#3 | 71 layout-operability warnings | low | open | still 71 (`layout report`); note #3 above: six valves inside the casing are not even in the list |
| 2026-10-22-layout-review3#4 | rack free spans | low | open | now 25 layout-free-span warnings (was 26) after the rebuild; no intermediate steel modelled |
| 2026-10-22-layout-review3#5 | 10 lifting cases for the lifting study | low | open | still 10 layout-lifting warnings; see #5 and #7 above for what the rule does not see |
| 2026-10-22-layout-review3#6 | casing penetrations not declared | low | open | now 12 layout-wall-penetration infos on CB-1 (was 16), none pinned; the schedule still exists only as findings |
| 2026-10-22-layout-review3#7 | AHU-1 supply mains in the B1 crane hook path | low | open | layout/hvac.yaml unchanged since f1c29ff |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | still not modelled |

The closed and accepted findings that review3 lists were spot-checked at 13e07b4 and stay
closed: rereview#1 (PSV-3114/3116 on RV, outlets 58.25 m, but see #2 of review3 and #1 here for
the roof access), rereview#3 (VNT-4006 / VNT-4007 outlets 14.72 / 14.74 m), rereview#5 (S-2101
zone centre z 10.0), layout#5 (WN-1002 outlet 27.62 m), layout#8 / #9 (no FW-4101 or B1
wall-penetration finding), layout#16 (GOX-4003 `rack`), rereview#7 accepted (LIN-3001
layout-tier, the only tier finding left; the RG-2001 acceptance is gone and so is its finding).

## Drawing
No P&ID in scope and none changed on the branch (`git diff main...HEAD -- pid` empty).
validate: P-01 0 line-through-label, 0 line-crossing, 0 label-overlap, 0 label-far-from-owner;
P-02 0 / 0 / 0 / 0; P-03 0 line-through-label, 3 line-crossing (accepted, checks.yaml), 0, 0;
P-04 0 line-through-label, 1 line-crossing (accepted), 0, 0. Tiles not read (no sheet changed).

## Layout
`plantcode layout build --check`: "layout/plant-model.yaml is up to date".

`plantcode layout report` at 13e07b4:
- lines: 76; 73 routed, 3 skipped (GAN-3002, LN-3002 internal of the double column, D-028;
  VNT-3004 casing breather), 0 unrouted; 214 of 218 segments.
- chains per method: astar 63, astar_coarse 2, open 23, pinned 3, rack 34, rack+astar_coarse 1;
  no `direct`.
- chains per reason: local: above the pipe-way 13, pipe-way 18, pump run at grade 6, rack detour
  too long 7, rack run too short 2, short run 19; open end 23; pinned 3; rack: across areas 14,
  battery limit at a rack end 14, crosses a road 1, longer than local_max_m 6.
- rack fill: PR1 5 m 58 %, 7 m 46 %, 9 m 21 %; PR2 6.5 m 21 %, 8.5 m 22 %; PR3 6.5 m 48 %,
  8.5 m 34 %.
- model findings per rule: clash-* 0, headroom 0, access-blocked 0, zone-crossing 0,
  separation 0, vent-outlet 0 (but see #2), escape-ways 0 and escape-travel 0 (but see #1),
  spacing 0, wall-penetration 12 info (review3#6), tier 1 (LIN-3001, accepted), operability 71
  (review3#3), free-span 25 (review3#4), lifting 10 (review3#5), laydown 0, support-missing 65
  info, nozzle-unconnected 2 info (C-3101 N3 / N4, the skipped internals, D-028),
  tray-separation 1 (accepted, D-036 cover plate).
- platforms 8 declared (plus generated tank roof platforms and stairs), stairs ST1..ST5 and
  ladders LD0..LD8 declared; no access proposal `review_needed`.
- `plantcode check`: every basic gate passes except `layout-review` (before this record:
  review3 is `self` and older records are stale); detail gate `datasheets` fails (no datasheets).

PNGs read (build/, rendered at 13e07b4):
- build/layout-plan.png (plot plan)
- build/layout-section-y68.png (along PR1, looking north: tiers, trays at 11 m, the VNT-4004
  zone over x 135-145, the VNT-4006 / 4007 zones at x 166-176)
- build/layout-section-x129.png (through the cold box, looking west: casing to 53 m, platforms
  P10..P40 inside the casing line, the roof zones, PR1 frame)
- build/layout-section-y112_crop-110-0-165-22.png (through T-4101 / T-4102: tank stairs,
  landings, the vent and relief outlets and their zones)
- build/layout-plan_crop-100-15-180-75.png (A3 / A4: cold box, FW-4101, K-4101, crane pad,
  escape zone, BL bleeds)
- build/layout-plan_crop-110-85-195-135.png (A5 and V1: tanks, pumps, vaporizers, pads,
  truck bay, silencers)
- build/layout-plan_crop-15-20-85-75.png (A1: B1, B2, intake, trays into B1 and B2)

## Checked and fine
- Separations (measured): CB-1 to B1 54.0 m (>= 53), CB-1 to FW-4101 19.9 m, K-4101 to CB-1
  21.4 m; T-4101 to B1 77.9 m, to K-4101 > 15 m (FW-4101 80.8 m), roads R3 24.3 m / R2 26.8 m,
  boundary 34.3 m; validate reports no layout-separation finding.
- Plot arrangement: intake F-1101 at the upwind south-west corner, vent area V1 at the
  downwind north-east corner (~190 m), O2 silencers 7.5 m stacks, the large GOX vents and the
  waste N2 surplus routed on PR1 / PR3 to V1; fire roads on all four sides of the process row.
- Rack tiers by service (D-029): water 5 m, air / waste N2 7 m, O2 / N2 / cryogenic top tier;
  fill below 60 % on every tier; one tier exception accepted with a reason.
- GOX compressor K-4101 in the open behind FW-4101 with the crane pad on the open east side;
  GOX-4005 through declared sleeves only.
- Cold box roof relief valves on their own platform with tailpipes to 58.25 m (rereview#1).
- Every clad building ventilated (gate hvac), every motor and instrument cabled (gate
  electrical); the material take-off current (gate mto).

## Not checked
- Pipe stress, supports, tailpipe and vent reaction forces; tray support steel; structural
  design of CB-1, the RV platform, FW-4101, the racks: piping stress and structural engineers.
- The vent and inert study (every zone ASSUMED, D-031) and the lifting study (D-034): competent
  person and crane contractor.
- Electrical design (load list, cable sizes, transformer yard, cable cellar and wall entries of
  B2) and the HVAC heat load (D-036, D-037): electrical and HVAC engineers.
- LOX spill containment and drainage at T-4101 and the truck bay (not modelled).
- The 71 operability warnings one by one, the 65 support-missing infos, the 3D viewer.
- The DESIGN.md decisions D-025..D-037 were read against the model; the process basis behind
  them (sizes, weights, duties, all ASSUMED) was not re-derived.
