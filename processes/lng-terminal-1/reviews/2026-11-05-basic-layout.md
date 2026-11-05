---
topic: layout
reviewed_commit: 0603eeede7baabb23b2531f8ae632569a0050058
scope: [layout/, piping/routing.yaml]
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: layout (3D model, routing, buildings, zones, lifting) of the layout pass of 2026-11-05

Scope: `layout/` (site plan, buildings, placement, zones, hvac, the generated
`layout/plant-model.yaml`, the lifting study) and `piping/routing.yaml`. Read as basis, not
reviewed: `electrical/electrical-list.yaml`, `electrical/tray-rules.yaml`, the `accept:` entries
of `checks/checks.yaml` for layout rules, `DESIGN.md` D-007, D-011 to D-021, D-025, D-026.

**Commit.** HEAD is `0603eeed` (the task named `75e0b9fc`; `0603eeed` is the HAZOP revision
committed on top of it). The layout pass is **not committed**: every reviewed file is a working
tree change on top of `0603eeed` (`git status`: `layout/*.yaml`, `piping/routing.yaml`,
`checks/checks.yaml` modified, `layout/building.yaml`, `layout/hvac.yaml`, `electrical/*`
untracked). This record reviews that working tree; see #18.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-layout#1 | layout/building.yaml, layout/zones.yaml | B-PLAT (TR-5, MCC-2, RR-2), AHU-2, LA-5102 / LA-6102 | The platform substation B-PLAT, with the 630 kVA transformer TR-5, MCC-2 and the rack room, stands on the loading platform 23.5 m from the vapour arm LA-5102 (`cheme show LA-5102 --layout`) and 7 m north of the Berth 2 manifold zone 1 (Z-HA-MANIFOLD-B2, y 872-902). D-018 says the loading point is ≥ 200 m from ignition sources (S-05, "200 m ignition-free radius") and inside the 200 m vapour-arm safety zone (S-01). `layout/zones.yaml` line 83 itself says "no ignition source" in that zone, but models it only on the water below the deck (z -30 to -6), so nothing on the deck is ever checked against it. The only measured separation is LA-5101 to T-2101 (500 m). The building is not classified, pressurised or gas-detected in the model, and its notes say only that the classification "may require" a pressurised room. Its outdoor-air louvre LV1 is in the west wall, facing the Berth 2 carrier 10.5 m away (Z-SHIP-B2-M east edge x 1129). | high | open | Take the transformer and MCC out of the 200 m radius. One option is a trestle substation on PR2 more than 200 m north of LA-5102/LA-6102 (y ≥ ~1085), with 400 V feeders of about 250 m to the platform motors and HPUs, which are Ex rated. If a building has to stay on the platform, record it in DESIGN.md as a deviation from D-018 and S-05, with its basis: a pressurised Ex p room, gas detection at the intake with trip, and the intake away from the ship side. Add a site-plan separation that measures the 200 m from both vapour arms to every substation, transformer and non-Ex building. |
| 2026-11-05-basic-layout#2 | layout/building.yaml, layout/site-plan.yaml | B-PLAT, road R5, Z-LAY-A4NW, Z-PAD-A4W / Z-PAD-A4E | The jetty road R5 ends at (1141, 925), 6 m wide (x 1138-1144), at the north edge of the platform. B-PLAT stands across that end: x 1139.5-1146, y 909-923, 2 m south of the road end. East of it, PR2's west edge is at x ~1146.1 at y 920, so there is no gap. Vehicles, the mobile crane for the arm lifts (69.3 t needed, lifting study) and fire-fighting vehicles can reach the deck only through the 8 m laydown strip Z-LAY-A4NW (x 1131-1139), and not at all while it holds arm parts. Nothing reaches the east crane strip Z-PAD-A4E except under PR2. The lifting study marks the arm lifts "lane clear" but does not check how the crane gets to its pad. | high | open | Keep the road end and a 6 m vehicle lane onto the deck clear, to both crane strips and to the drain drums. Move B-PLAT (see #1) or turn the laydown into a declared road. Declare the platform roadway in the site plan so the crane pads have a connected road. |
| 2026-11-05-basic-layout#3 | layout/building.yaml, layout/site-plan.yaml, layout/zones.yaml | B-SUB (SWG-1, MCC-1, control room CR-1), AI-4133 / AI-4134, XV-4131/4132/4135/4136, PR1/PR2/PR3 junction | The substation and control building B-SUB is occupied (CR-1). It stands 4 m off PR2's east edge at the PR1/PR2/PR3 junction (building x 1106, rack edge x 1102), which carries 2 x DN 800 LNG, 2 x DN 750 vapour return, the flare header and the rundown. It is 2.5 m from the analyser shelter of AI-4133/4134 (electrical-list point x 1103.5, y 2890.5-2892, sampling carrier vapour), which is not modelled and has no zone. It is about 15 m from the actuated vapour switching valves XV-4131/4132/4135/4136 (model points x 1089.4-1090.9, y 2886-2891.5). Spills reach the impoundment sump T-8101 along the troughs of this junction (D-018). The building comment says "outside every hazardous zone". That is true only because `layout/zones.yaml` declares no zone for rack flanges and valves, the analyser shelter or the spill troughs. No building siting or LNG spill dispersion and radiation basis (CSA Z276 / NFPA 59A exclusion zones) is cited for an occupied building. | high | open | Site the control room and switchgear from a consequence basis: an LNG spill on the rack and the troughs, a vapour release at the analyser shelter and at the valves. Record that basis in DESIGN.md. In practice, move B-SUB well away from the rack junction and the troughs, and the analyser shelter away from the building. Declare zones for the analyser shelter, the rack valve stations and the spill troughs (sources in `layout/zones.yaml`). Add separations B-SUB to PR1/PR2 and B-SUB to the analyser shelter. |
| 2026-11-05-basic-layout#4 | layout/equipment-placement.yaml, checks/checks.yaml, piping/routing.yaml | T-2101 / T-3101 roof; HV-n151..n152, HV-n161..n165, FV-n111x, PSV-n133A-C; P-n101A-D, P-n102 | The tank-top pump platform does not exist in the model. Yet the accepted `layout-operability` findings rest on it: HV?15*, HV?16* (new this pass), FV*, and PSV* "tank-roof platform". So do the in-tank pump lifting and laydown accepts ("tank-top pump-removal crane", "laid down on the tank-top pump platform"). They cite D-011 and D-007, which describe neither a platform nor a roof crane. The tank in the model has one spiral stair, landing at 42.2 m at the south-west (stair-landing, roof-platform at 45.8 m). There is no roof walkway to the crown, no pump platform and no second way off the roof. The pump column heads stand at 56 m, but the roof valves are routed at 58.4-61.6 m (HV-2151A 61.38 m, HV-2161 61.63 m, FV-2111C 60.88 m). Even from a 56 m platform they are 2.4-5.6 m up, beyond the 1.8 m reach. The vacuum valves PSV-2133A-C stand at the dome edge (y 3071, 51.8-52.1 m), about 90 m round the roof from the stair head. Because no floor exists there, the build proposes VP-HV-2151A, VP-HV-2161 and others: 60 m platforms on stairs from grade inside the tank (`VP-HV-2161`, stair box from z 0 at x 941.9, y 3026.5). | high | open | Declare the tank-top structures: the pump platform around the column heads (with the pump-removal davit or crane and its laydown), the roof walkway from the stair head, and the relief/vacuum valve platform at the north-east edge, as structures mounted on the tank with their levels. Add a second way off the roof, remote from the stair. Pin the roof piping so each manual valve is within reach of those levels. Rebuild, and drop the operability, lifting and laydown accepts that the model then satisfies. Record the tank-top access, the pump removal and the escape in DESIGN.md (tank contractor scope, ASSUMED). |
| 2026-11-05-basic-layout#5 | layout/site-plan.yaml, layout/zones.yaml | roads R3, R6; area A2; Z-PAD-A2E, Z-LAY-A2E | R3 (x 1115, y 2955-3098) and its spur R6 (to y 2912) connect to no other road. R3 stops 20 m short of R2: PR3's east leg (y 3103-3117) lies between them. R6 is separated from R1/R5 by PR2 (x 1088-1102). B-SUB's only declared road access (switchgear delivery door N1, fire access) therefore leads nowhere. The BOG compressor area A2 has no road at all. It is closed in by PR1 (south), PR3 (east), the PR6 east leg (north) and T-2101 with PR6 (west). The crane pad Z-PAD-A2E is "reached from road R3 under PR3", a road crossing under a rack that is not declared (no portal bents, no headroom check; R2 under PR4 is declared that way). | medium | open | Join R3 to R2 and R6 to R1/R5 with declared crossings under PR3 and PR2: road points, `bent_spacing_m` so the bents stand either side, headroom ≥ 6 m under the bottom-tier steel. Or bring a road into A2. Give every crane pad a connected road. Record fire access to A2 from two sides (skill layout-yaml step 4). |
| 2026-11-05-basic-layout#6 | layout/zones.yaml, layout/site-plan.yaml | Z-SZ-B2 / Z-SZ-B1, Z-SHIP-B1-*, Z-SHIP-B2-* | Each berth's 200 m safety zone around its vapour arm (TIG Rev 3: no other vessel while transferring) holds the other berth's carrier: Z-SHIP-B1-M starts 44 m east of LA-5102. With Berth 1 on the east face of the same T-head (D-019, ASSUMED), loading at one berth with a carrier alongside the other contradicts the zone as it is written in `layout/zones.yaml`. No basis for simultaneous operations at the two berths is recorded. | medium | open | State in D-019 / D-018 whether the TIG zone excludes the terminal's own second berth (simultaneous loading and berthing), with its source. Otherwise move Berth 1, or limit operations to one carrier alongside during transfer. |
| 2026-11-05-basic-layout#7 | piping/routing.yaml | LNG-2001, LNG-3001 (6 segments each), LNG-2023/2024/2025, LNG-3023/3024/3025, LNG-1001 (2), LNG-1003 (2), BOG-1001 (1); BOG-6003 (via+direct) | `cheme layout report`: 11 `direct` chains and 1 `via+direct` chain, neither pinned nor accepted. Every fallback route counts as a finding (skill review 4a). The tank-roof pump headers and minimum-flow returns run straight at 58-62 m, above the 56 m pump heads (section y=3026), with 20-30 m level runs and no support (LNG-2023 25.5 m, LNG-2025 29.5 m, `layout-support-missing`). | medium | open | Route the roof headers along the pump platform of #4 (pins at platform level, onto PR5/PR6). Route LNG-1003 and BOG-6003 with `via` intent. Rebuild until `direct` is 0, or accept each remaining chain with its reason. |
| 2026-11-05-basic-layout#8 | piping/routing.yaml (no piping/pipe-specs.yaml) | all cold lines; LNG-4001/4002, BOG-4001/4002 | The model insulates every cold line with the 80 mm default (section y=2400: thin rings on the DN 800 and DN 750 lines). The line list says "PIR 200 mm" and D-012 specifies 200 mm on DN 800 and 150 mm on DN 750. The outside diameters, rack lanes, clearances, the pinned battery-limit and junction centrelines (written as "tier + outside radius") and the take-off are all built on the wrong OD. | medium | open | Add `piping/pipe-specs.yaml` with the D-012 thicknesses (and a cold class). Rebuild and re-pin the centrelines that rest on a tier, so they rest on the new OD. Then re-run the rack fill and the clash checks. |
| 2026-11-05-basic-layout#9 | layout/plant-model.yaml (rule `layout-free-span` / `-support-missing`) | every LNG line, e.g. LNG-2001 DN 800, LNG-1003 DN 900, LNG-2021 DN 150 | The span screening classes every LNG line as gas. Every finding reads "for DN … gas", for example "LNG-2001 (LNG-2001, DN 800) runs 21.3 m … > 12.8 m span for DN 800 gas", and no finding anywhere uses a liquid span. LNG is a liquid of ~450 kg/m3, so the allowed spans are shorter. The 14 free-span warnings and 80 support-missing infos therefore understate the runs that need supports, and the PR4 bents at 17 m rely on the intermediate steel for the DN 900 rundown. | medium | open | Report to cheme-as-code (the span rule takes the class from the fluid's name and does not recognise "LNG" as a liquid). Meanwhile, give the LNG lines a liquid class in `piping/pipe-specs.yaml` if the schema allows it, and re-screen. |
| 2026-11-05-basic-layout#10 | checks/checks.yaml | `layout-free-span:*`, `layout-tray-span:*` | Two wildcard accepts cover every present and future finding of a rule: free-span (existing) and tray-span (new this pass, 37 findings). Any new long span (a new route, a re-pinned line after #8) is accepted without anyone seeing it. There is also an unused accept, `layout-laydown:laydown-FL-8101` (`cheme.accept-unused`). | medium | open | Replace the wildcards with patterns limited to the reviewed runs (by line or tray prefix), or with ids. Remove the unused entry. |
| 2026-11-05-basic-layout#11 | layout/zones.yaml | escape routes: A2, A4 loading platform, tank roofs, trestle | `layout/zones.yaml` declares no `escape` zone, and there is no `layout/structures.yaml`. The escape, headroom-over-walkway and egress rules therefore had nothing to check, which is why they show 0. Several places have no stated way out. The BOG area is closed in by racks and crossed by the low corridor at 2.0-3.6 m (BOG-7002 at 2.0 m, FL-7002 at 3.6 m, FL-7003 at 3.0 m, y 2975-2979), which stands at about head height for anyone walking there. The platform's only land route is the 2 km trestle (no escape-to-sea point, no second route). The tank roofs have a single stair (#4). | medium | open | Declare escape routes as `escape` zones: out of A2 on at least two sides, the trestle walkway, the platform's muster and escape point. Lift the low corridor above 2.2 m where it crosses them, or add declared step-overs. Record the escape philosophy in DESIGN.md. |
| 2026-11-05-basic-layout#12 | layout/site-plan.yaml, piping/routing.yaml | PR2 (trestle), PR1; LNG-4001/4002, BOG-4001/4002, LNG-1001 | No space is reserved for the thermal contraction of the 2.45 km cryogenic lines. For stainless steel cooled to -162 degC that is about 2.9 mm/m, or ~7 m per loading line (ASSUMED material). The trestle and PR1 are straight runs with no loop bays, and the 14 m rack width is not shown to hold loops of DN 800 lines. D-021 item 7 leaves loops off the P&IDs; the layout still has to hold them. | medium | open | Decide the contraction concept: expansion loops (with the bay spacing and rack widening each loop needs), bellows, or Invar/low-expansion pipe. Record it in DESIGN.md, and reserve the loop bays in the site plan before the trestle width is fixed. |
| 2026-11-05-basic-layout#13 | layout/plant-model.yaml (generated structures), layout/zones.yaml | 98 proposed VP-* platforms; VP-XV-5131 / VP-XV-5133 / VP-XV-6131 ... at the berth faces; LA-51xx / LA-61xx | 98 generated valve access platforms are unpinned, with `review_needed`. Some are not buildable: the tank-roof ones (#4), and the berth-face ones, for example VP-XV-5131, which is 18.33 m of fixed steel with a 7-flight stair at x 1131.7-1136.2 between the arm risers and the ship edge. The ERS valves are part of the arm and move with it (D-021 item 8), and the arms' operating envelope (22 m, D-014) is not declared as a keep-clear zone. So the model cannot see fixed steel in the arm's swing. | medium | open | Declare each arm's operating envelope as a `keep_clear` zone from the vendor's envelope (ASSUMED until then). Reject the VP proposals for valves that are actuated or part of the arm. Decide the rest one by one: pin, operator, or move the valve. |
| 2026-11-05-basic-layout#14 | DESIGN.md (basis of the layout files) | B-SUB, B-PLAT, SS-1/SS-2, the per-rack lane plan, battery limits at the carrier manifolds, FG-1001 at PR4 north | DESIGN.md has no entry for this pass. Nothing records the two electrical buildings and their siting, the platform substation chosen against 400 V trestle feeders, the 69 kV supply, the lane plan per rack (written only in `piping/routing.yaml`), the new battery limits, or the HVAC basis. AGENTS.md asks for every decision and assumption to be recorded in DESIGN.md with its reason. | medium | open | Add a decision (D-027 or the next free number) for the layout and electrical pass, with the measured distances (`cheme show … --layout`) and every ASSUMED value. |
| 2026-11-05-basic-layout#15 | layout/building.yaml | B-SUB comment | The comment says B-SUB is "> 100 m from the BOG compressors". The measured distance is 91.0 m to K-7101C (`cheme show K-7101C --layout`). | low | open | Quote the measured value. |
| 2026-11-05-basic-layout#16 | layout/zones.yaml, checks/checks.yaml | Z-PAD-A3, accept `layout-lifting:FL-8101` | The crane pad basis and the FL-8101 accept say the stack and tip are handled by "the derrick's own hoist (D-017)". D-017 says nothing about a hoist. S-02 gives the derrick but not its maintenance means. | low | open | Record the flare tip maintenance (derrick hoist, ASSUMED) in DESIGN.md and cite that entry. |
| 2026-11-05-basic-layout#17 | layout/zones.yaml, layout/equipment-placement.yaml | T-8101, T-8102, the trestle drip trays and tank-area troughs (D-018) | The spill containment that D-018 relies on is not in the model: the troughs along PR1 and the trestle drip trays draining to T-8101. Neither the 6 m deep sump T-8101 (between T-2101 and PR1) nor the jetty sump T-8102 has a zone or a separation, although both collect cold flashing LNG. | low | open | Model the troughs and the trays as keep-clear volumes under the racks. Give both sumps a zone (secondary source), and check the separations to B-SUB and to B-PLAT. |
| 2026-11-05-basic-layout#18 | reviews/ (this record) | reviewed_commit `0603eeed` | The reviewed layout files are uncommitted on top of `0603eeed`. Once the author commits them, the scope files differ from `reviewed_commit`, so the `layout-3d` and `layout-review` gates will read this record as out of date. | low | open | Commit the layout pass as its own change. Then have the next layout review (or the record that closes this one's findings) name that commit as `reviewed_commit`. Do not edit this record after it is committed. |

## Previous findings
None to carry forward. No earlier record has a scope overlapping `layout/` or
`piping/routing.yaml`: the two design reviews (2026-11-05-basic-design, -design-2) cover only
the P&IDs, lists, control files and DESIGN.md (`grep -h '^scope:' reviews/*.md`).

## Drawing
Not part of this layout review: no P&ID was changed by the layout pass. For reference, the
`cheme validate` count lines are all 0 (P-07: `0 line-crossing (+2 accepted)`).

## Layout
Commands run (working tree on `0603eeed`):
- `cheme layout build --check`: `layout/plant-model.yaml is up to date`.
- `cheme validate`: `78 file(s): 0 error(s), 41 warning(s)`. The warnings are none of layout:
  interlock-unknown-tag 18, control-unknown-tag 2, hazop-input-changed 20,
  datasheet-drawing-stale 1. There is one info, `cheme.accept-unused` for
  `layout-laydown:laydown-FL-8101`.
- `cheme check --stage detail`: ok layout-plot-plan, lifting-study, mto, layout-detail, electrical,
  hvac. FAIL layout-3d and layout-review (no layout record, which this record supplies), FAIL
  design-review and control-complete (outside this scope).
- `cheme diff main --list`: 1,036 lines, all P&ID items (sheets added on the branch, 11
  commits main..HEAD). The layout files are not in the item diff, and their changes are
  uncommitted (`git diff --stat`: routing.yaml +259/-, zones.yaml 14, site-plan.yaml 2,
  equipment-placement.yaml 5, checks.yaml +14).

`cheme layout report`:
- Lines: 147. 146 are routed; BOG-1004 is skipped with a reason. Unrouted: 0.
- Chains per method: astar 66, astar_coarse 3, direct 11, open 24, pinned 85, rack 13, via 8,
  via+direct 1. The 12 fallback chains are #7.
- Chains per reason: pinned 85, local above the pipe-way 28, open end 24, local pipe-way 21,
  local short run 13, local rack run too short 10, intent via 9, rack longer than local_max_m 9,
  local pump run at grade 4, rack battery limit at a rack end 4, local rack detour too long 3,
  local no rack in reach 1. Battery-limit ends: rule 19, rack end 1.
- Rack fill: PR1 7 m 39 % / 10 m 18 %; PR2 26 % / 32 %; PR3 11 % / 25 %; PR4 7 m 33 %; PR5
  12 m 16 % / 14 m 6 %; PR6 21 % / 21 %. These are understated by the 80 mm insulation (#8).
- Model findings by rule: operability 129, support-missing 80 (info), tray-span 37,
  free-span 14, lifting 13, laydown 10, tray-zone 4, tray-separation 2, tier 1. All accepted
  in `checks/checks.yaml`; #4, #9 and #10 question what rests on those accepts. These are 0:
  clash-*, headroom, buried-cover, access-blocked, zone-crossing, separation, spacing,
  wall-penetration, vent-outlet, escape-*, access-enclosed/-unconnected, ladder-clearance,
  egress-zone, pad-overlap, steel-in-way, pipe-disconnected. Several of the zeros mean only that
  nothing was declared to check against (#1, #11, #13).
- Objects: equipment declared 35, inline generated 184, pipes generated 219 / pinned 85,
  structures generated 98 (VP-*, all `review_needed`, #13), zones declared 28. Review needed
  (generated, not pinned): 24.

Accepted model findings added in this pass, and my view of each:
- `operability:P-0[23]/HV?16?`: not supported (#4).
- `operability:P-0[56]/HV??19`, `HV??53`, `P-07/HV7124?`: reasonable at this stage.
  HV-7124A-C sit 0.3 m above reach, on the vendor's step.
- `lifting:D-6101`, `tier:P-04/Line_LNG6006_S1@PR2` (10.6 m, quoted length current):
  reasonable.
- `tray-separation:PT-PR1-*+IT-PR[56]-1`, `tray-zone:PT-M-P-[56]101+Z-HA-JETTY-DRAIN` and
  `PT-M-P-8101?+Z-HA-FLARE-KO`: reasonable (Ex cable glands, metal divider), ASSUMED until the
  area classification.
- `tray-span:*`: too wide (#10).

Rendered and read (all under the plant folder):
- `build/layout-plan.png`: the full plot plan, legible only for the arrangement. The tanks,
  BOG area, flare and trains sit north; the 2 km trestle runs south to the T-head; the 200 m
  circle is drawn at the platform.
- `build/layout-plan_crop-700-2860-1150-3130.png`: tank and BOG area. Two 92 m tanks at
  140 m centres (shell to shell 48 m). PR5/PR6 risers 3.6 m / 5.6 m off the shells. R3 and R6
  are visibly not joined to R1/R2 (#5).
- `build/layout-plan_crop-1070-2865-1145-2925.png`: B-SUB beside the PR2/PR1 junction and the
  XV-4131..4136 valve station (#3).
- `build/layout-plan_crop-1115-850-1195-935.png`: loading platform. Arms on both faces,
  manifold zones, crane strips, laydowns. B-PLAT stands across the end of road R5 (#1, #2).
- `build/layout-section-x929.png`: the full extent, not legible at A1. Read with
  `build/layout-section-x929_crop-2925-0-3075-70.png` (depth 140 m, which includes the PR5/PR6
  risers): the tank shell to 42.2 m, the dome to 56 m, the spiral stair landing at 42.2 m, the
  riser towers, PR1 tiers 7/10 m with the riser racks at 12/14 m above, the PSV zones on the
  north-east roof.
- `build/layout-section-y890.png`: full width, read with
  `build/layout-section-y890_crop-1110--12-1200-42.png` (depth 40 m): arm risers to 22 m,
  manifold zone-1 boxes, ship envelopes 1 m off the faces, the 18.3 m VP stairs beside the
  arms (#13), the PR2 head and the drain drums, T-8102 below the deck.
- `build/layout-section-y3026_crop-900-30-1000-70.png`: the T-2101 roof. Valves at 58-62 m,
  and the proposed VP and support posts from grade through the tank (#4, #7).
- `build/layout-section-y2400_crop-1095-0-1135-22.png`: trestle cross-section. DN 800 lines on
  the 7 m tier, DN 750 vapour lines and N2 on the 10 m tier, the power tray at 13.5 m, 80 mm
  insulation (#8).

Measured (`cheme show <tag> --layout`): LA-5102 to B-PLAT 23.5 m, to PR2 9.1 m; K-7101C to
B-SUB 91.0 m, to T-2101 76.5 m (≥ 30 m, D-018); T-2101 to B-SUB 166.4 m, to R1 45.8 m (≥ 15 m),
to PR6 5.6 m; T-3101 to PR5 3.6 m, to R4 35.4 m. Tank shell to shell 48 m (≥ 46 m
separation; centres 140 m, diameter 92 m).

## Checked and fine
- Tank spacing: 48 m shell to shell against the 46 m separation (NFPA 59A practice, D-018).
  The tanks have roads on three sides (R1, R2, R4) at more than 35 m.
- Tank to BOG compressors: 76.5 m (≥ 30 m). Flare: T-2101 to FL-8101 561 m (D-013) against
  300 m. A3 is kept sterile, with the D-8101 crane pad limited to the drum and conditional on
  the flare being out of service.
- Ship envelopes: 315 x 55 m (S-01 maximum carrier) at both faces, 1 m off the platform. The
  Berth 1 envelope clears PR2 by about 7 m at the trestle head. The certified 345 m (S-04,
  permit limit) is not the design carrier.
- Rack arrangement: liquid low and vapour high on every rack. The riser racks' 12/14 m tiers
  cross PR1/PR3 above their steel. The R2 crossing under PR4 has a portal (17 m bents). Rack fill
  ≤ 39 % leaves room for the Phase 2 lines already included.
- BOG area: recycles west of the machines, the discharge header and vents in the low corridor,
  and the crane lanes from Z-PAD-A2E clear (lifting study "lane clear" for K-7101A-C and D-7101).
  Motor removal is kept east.
- Lifting study: every item of 5 t or more has a crane pad, a clear lane and a laydown, or an
  accept. D-5101/D-6101 are blocked only by their own inlet spools (accepted).
- Hazardous zones from sources resolve (no `layout-zone-source`). The BOG seal zones are far
  from B-SUB (91 m).
- HVAC of B-SUB: the intake on the east wall faces away from the racks, with the exhaust 13 m
  away in the south wall.

## Not checked
- The area classification itself: every zone is the ASSUMED screening table. A competent
  person must classify to CSA C22.1 / IEC 60079-10-1, and the TERMPOL/TIG safety zones must be
  confirmed. No Ex selection may rest on these zones.
- Building siting, LNG spill thermal radiation and vapour dispersion exclusion zones (CSA
  Z276 / NFPA 59A), for the impounding areas, the sumps and the occupied buildings. Needs a
  consequence study by a competent person (#3).
- Pipe stress, supports, anchors, expansion loops (#12), surge loads on the trestle: piping
  stress engineer.
- Structural design of the racks, the trestle, the riser towers and the platform steel; the
  marine structures (dolphins, fenders, mooring; S-09 not modelled): structural and marine
  engineers.
- The crane selection, the ground and deck bearing, the floating crane option for the arms:
  lifting contractor.
- Fire protection (monitors, hydrants, deluge, fire water ring main), gangway tower, escape
  craft: not in the model.
- Prevailing wind (not in DESIGN.md), so the air intakes upwind of the vents were not checked.
- The electrical and HVAC designs themselves (cable sizing, loads, voltage drop on the
  2.1 km 6.6 kV feeders, AHU sizing): electrical and HVAC engineers. Only their effect on
  the layout was looked at.
- The estimate: `estimate/rates.yaml` is still the example file.
- Every one of the 85 pinned routes one by one. I read the pins of the BOG area, the trestle
  ends and the platform, and the sections above; I did not trace each pinned route
  vertex by vertex.
