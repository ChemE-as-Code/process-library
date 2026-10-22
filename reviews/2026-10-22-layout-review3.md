---
topic: layout
reviewed_commit: f1c29ffed5b2141a00a121a70007a7a596399724
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, piping/routing.yaml, piping/pipe-specs.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml]
basis:
  - {path: equipment/equipment-list.yaml, revision: f1c29ffed5b2141a00a121a70007a7a596399724, relation: depends-on}
  - {path: DESIGN.md, revision: f1c29ffed5b2141a00a121a70007a7a596399724, relation: depends-on}
reviewer: Claude (the agent that made the D-033..D-037 changes)
reviewer_kind: self
branch: layout-detail
merge: pending
---
# Review: layout, third review after example-asu#2 and the detail data

Third layout review of branch `layout-detail` at f1c29ff, against the re-review
reviews/2026-10-21-layout-rereview.md (f2a7582) and its open findings collected in
example-asu#2. **This is a self review**: the reviewer also made the changes it reviews
(D-033 to D-037), because no independent reviewer could be started from this session. It does
not satisfy the gate `layout-review` (human or agent): an independent reviewer has to repeat it
before a stage sign-off. Coordinates are site metres from `layout/plant-model.yaml`; distances
measured with `plantcode show <tag> --layout` or computed from model coordinates (stated).
plantcode ran from the core worktree `feat/layout-detail` (0701c01, 7245c61), which adds the
engineering rules, flat-bottom rack lanes and declared platforms as walking levels for vent
risers.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-22-layout-review3#1 | layout | PT-M-K-1101, B1 | The 6.6 kV cable tray to the MAC motor leaves the PR1 tray tier (11 m) at x 48.2, climbs over the MAC house roof (14 m), drops outside the south wall and enters through the roller door S1 at 6 m (tray points [48.185, 70.4, 11.0] .. [48.185, 49.4, 14.0], [48.185, 20.4, 14.0], [48.185, 20.4, 6.0], [48.185, 30.0, 6.0]): the tray router treats the cladding as closed, cannot use a declared wall opening, and the parked crane bridge at x 48 blocks the hall at that height; nothing reports it. | medium | open | A cable trench or a declared cable entry from B2 to B1 (north wall, below the runway), and a tray router that passes declared openings (plantcode). |
| 2026-10-22-layout-review3#2 | layout | VNT-3002, VNT-3003 | The PSV-3114 / PSV-3116 tailpipes stand 4.5 m free above the valves (53.75 to 58.25 m) on the relief valve platform RV; no guide or support is modelled and the relief reaction acts at the top. | low | open | Guide the tailpipes to a frame on the RV platform; piping stress engineer to size it (D-033 (1)). |
| 2026-10-22-layout-review3#3 | layout | 60 valves, 11 transmitters | 71 `layout-operability` warnings (handwheels and levers more than 1.8 m, transmitters more than 2 m above the floor below them) stay open; D-034 (5) leaves them to the valve-by-valve piping layout. | low | open | Work through the list in detail engineering: move valves to grade or platforms, chain wheels, extension spindles. |
| 2026-10-22-layout-review3#4 | layout | rack lines DN 40-250 | 26 `layout-free-span` warnings (6.1 m bents against 2.1-5.8 m spans by the ASSUMED table); D-034 (6) plans intermediate rack steel. | low | open | Add the stringers to the rack design and model them, or carry small lines on larger ones. |
| 2026-10-22-layout-review3#5 | layout | K-4101, E-4101, K-4102, KT-3101, K-3101, E-2101, E-4102, E-4105A/B, E-4106B | 10 `layout-lifting` warnings: lanes over the 7 m fire wall FW-4101, along the cold box south bracing, and across outlet spools; D-034 (4) records each as a case for the lifting study. | low | open | Lifting study with the crane contractor; confirm spool removal for the lifts. |
| 2026-10-22-layout-review3#6 | layout | CB-1 | 16 casing penetrations (`layout-wall-penetration` info) are not declared as casing openings, so the casing penetration schedule exists only as findings. | low | open | Pin them (`plantcode layout pin CB-1/<LINE>`) into the CB-1 enclosure openings once the cold box vendor confirms the nozzle arrangement. |
| 2026-10-22-layout-review3#7 | layout | AHU-1 ducts | The MAC house supply mains run at 9.3 m along the hall, under the crane runway and inside the hook path of the 40 t crane (build/layout-plan-z0-12_crop-34-20-74-50.png). | low | open | Route the mains along the side walls outside the hook path, or record the lift zones the crane keeps clear (D-037). |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-21-layout-rereview#1 | PSV-3114 / PSV-3116 on the roof walkway, outlets at head height | high | closed c9fc8de | valves on platform RV at [128, 43, 53] / [131, 43, 53], 3.6 m from LD8 (computed); tailpipe outlets at 58.25 m (VNT-3002_S2, VNT-3003_S2 points); no `layout-vent-outlet` finding; build/layout-section-y43_crop-120-48-145-62.png |
| 2026-10-21-layout-rereview#2 | toppling separation CB-1 to B1 basis | medium | closed c9fc8de | D-033 (2) records the structure height (53 m) as the toppling height and why roof items are excluded; `show CB-1 --layout`: B1 54.0 m |
| 2026-10-21-layout-rereview#3 | VNT-4007 zone to grade, VNT-4006 zone overlap | medium | closed c9fc8de | BL at x 171; outlets VNT-4006 [171.0, 64.16, 14.72], VNT-4007 [171.0, 62.2, 14.74], above the PR1 top tier; no vent-outlet finding; the two 5 m zones still overlap high above the rack (no walking level there) |
| 2026-10-21-layout-rereview#4 | separation criteria without sources | low | closed c9fc8de | D-033 (3): O2 outlets >= 15 m from roads (D-025), VNT-4006 16 m from the R5 edge (computed), separation Z-O2-VENTS to R5 >= 10 m; the intake distances recorded as owner-practice deviations to confirm |
| 2026-10-21-layout-rereview#5 | S-2101 outlet below adsorber tops; RG-2003 low over Z-SIEVE | low | closed c9fc8de | S-2101 10 m high; Z-SIEVE 4.5 m high; RG-2003 S9 crosses at 5.3 m |
| 2026-10-21-layout-rereview#6 | CW-3001 over KT-3101 | low | closed c9fc8de | CW-3001 pinned along y 33.6 south of the compander, x 125.5 outside the crane pad |
| 2026-10-21-layout-rereview#7 | LIN-3001 not on its PR1 tier | low | accepted: a 3 m crossing of PR1 to the PR2 junction at the passing elevation under the PR2 tier, not a run along PR1; accepted in gate layout-rules with this reason (D-033 (4)), by the author | `layout-tier` finding accepted in checks/checks.yaml |
| 2026-10-21-layout-rereview#8 | PR2 title and D-026 text stale | low | closed c9fc8de | PR2 / PR3 titles in layout/site-plan.yaml corrected, D-033 (8) |
| 2026-10-21-layout#5 | C-1102 top platform in the WN-1002 vent zone | medium | closed c9fc8de | WN-1002 outlet raised to 27.62 m by a `vents` rule (needs plantcode 0701c01: declared platforms are walking levels for the router); no vent-outlet finding |
| 2026-10-21-layout#8 | GOX lines through fire wall FW-4101 | medium | closed c9fc8de | GOX-4001 over the wall onto the K-4101 top suction N1; GOX-4005 through two declared sleeves SL1 / SL2; no FW-4101 warning |
| 2026-10-21-layout#9 | routes through the B1 cladding outside openings | medium | closed c9fc8de | W2, E1 enlarged, north pipe band N1; no B1 wall-penetration finding |
| 2026-10-21-layout#12 | AIR-1006 over the E-1102 bundle pull | low | closed c9fc8de | AIR-1006 S1 pinned east first along y 35.5 |
| 2026-10-21-layout#13 | cryogenic pumps 6.5 m from their tanks | low | accepted: room for the tank outlet valves, pump removal and outlet flexibility; NPSH in detail engineering (D-033), by the author | unchanged positions |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | still not modelled (vendor arrangement, D-033); AIR-3003 / AIR-3004 enter the casing through its south wall |
| 2026-10-21-layout#16 | GOX-4002 / GOX-4003 on the local pipe-way | low | closed c9fc8de | both now `rack: longer than local_max_m` along x 180.3 / 181.3 at 9.8-10.1 m |

## Drawing
No P&ID in scope and none changed on the branch: `plantcode diff main --list` prints "No P&ID
changed." validate: P-01 0 / 0 / 0 / 0; P-02 0 / 0 / 0 / 0; P-03 0 line-through-label,
3 line-crossing (accepted, checks.yaml), 0 label-overlap, 0 label-far-from-owner; P-04 1
line-crossing (accepted). Tiles not read (no sheet changed).

## Layout
`plantcode layout build --check`: "layout/plant-model.yaml is up to date".

`plantcode layout report` at f1c29ff:
- lines: 76; 73 routed, 3 skipped (GAN-3002, LN-3002, VNT-3004), 0 unrouted.
- chains per method: astar 63, astar_coarse 2, open 23, pinned 3, rack 34, rack+astar_coarse 1;
  no `direct`.
- chains per reason: local: above the pipe-way 14, pipe-way 18, pump run at grade 6, rack detour
  too long 6, rack run too short 2, short run 19; open end 23; pinned 3; rack: across areas 14,
  battery limit at a rack end 14, crosses a road 1, longer than local_max_m 6.
- rack fill: PR1 5 m 58 %, 7 m 46 %, 9 m 21 %; PR2 6.5 m 21 %, 8.5 m 22 %; PR3 6.5 m 48 %,
  8.5 m 32 %.
- model findings per rule: clash-* 0, headroom 0, access-blocked 0, zone-crossing 0,
  separation 0, vent-outlet 0, escape-ways 0, escape-travel 0, spacing 0 (KT-3101 / K-3101
  declared, D-033 (7)), wall-penetration 16 info (casing, #6), tier 2 (accepted: LIN-3001,
  RG-2001 jog), operability 71 (#3), free-span 26 (#4), lifting 10 (#5), laydown 0,
  support-missing 63 info, tray-separation 1 (accepted, D-036), duct 0, HVAC capacity 0.
- platforms 8 declared, stairs ST1..ST5 and ladders LD0..LD8 declared, no access proposal
  `review_needed`; 9 junction boxes declared.
- cabling: 131 cables (12 power, 119 instrument), 46 tray runs, ~987 m of tray; HVAC: 2 units,
  52 ducts, 43 terminals.

PNGs read (build/, rendered at f1c29ff):
- build/layout-plan.png (plot plan)
- build/layout-section-x129.png (through the cold box, looking west: casing 53 m, stair landings,
  the tailpipes above the roof and their zones)
- build/layout-section-y68_crop-120-0-190-14.png (across PR1 east of the cold box, tiers and the
  tray tier)
- build/layout-section-y43_crop-120-48-145-62.png (cold box roof: RV platform, PSV-3114 /
  PSV-3116, tailpipes to 58.25 m, the 3 m relief zones above the walkway headroom)
- build/layout-plan-z0-12_crop-34-20-74-50.png (MAC house level plan: AHU-1, supply and extract
  rows, K-1101, coolers)
- build/layout-plan_crop-15-20-80-75.png (B2, trays from B2 to PR1, the MAC motor tray)

## Checked and fine
- example-asu#2: every high and medium finding closed in the model (see Previous findings); the
  new basic gate layout-rules (vent outlets, wall penetrations, tiers, escape, spacing) passes.
- Separations: CB-1 to B1 54.0 m (>= 53 m), CB-1 to FW-4101 19.9 m, B2 88 m from CB-1 (`show
  CB-1 --layout`); validate reports no layout-separation finding.
- Cold box access: stairs on the east side from grade to the roof, ladders at both ends, every
  CB-1 floor with two ways down; C-1101 / C-1102 platforms within 7.5 m of their ladders.
- Every clad building has its ventilation (gate hvac), every motor and instrument a cable in
  trays (gate electrical); the take-off is current (gate mto).

## Not checked
- Independence: this record is the author's; an independent reviewer (agent or human) has to
  repeat the review for the gate layout-review and before any sign-off.
- Pipe stress, supports, tailpipe reaction forces; structural design of CB-1, the RV platform,
  FW-4101, the racks and their tray steel: piping stress and structural engineers.
- The vent and inert study (every zone still ASSUMED, D-031); the lifting study (D-034).
- Electrical design (load list, cable sizing, protection) and the HVAC heat load (D-036, D-037).
- The 3D viewer was not used; the operability list was not reviewed valve by valve.
