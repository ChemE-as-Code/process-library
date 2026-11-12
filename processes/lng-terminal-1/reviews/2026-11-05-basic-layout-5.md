---
topic: layout
reviewed_commit: 709fcf20
scope: [layout/, piping/routing.yaml, piping/pipe-specs.yaml, electrical/]
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: layout (3D model, routing, buildings, zones, electrical) after the response D-033

Scope: `layout/` (site plan, buildings, structures, placement, zones, hvac, the generated
`layout/plant-model.yaml`, the lifting study), `piping/routing.yaml`, `piping/pipe-specs.yaml`
and `electrical/`. Read as basis, not reviewed: `DESIGN.md` D-001 to D-033 (mainly D-013, D-016,
D-018, D-021, D-031, D-032, D-033), the `accept:` block of `checks/checks.yaml`, the equipment
list, the line list, the special items, the instrument list, the P-01 to P-08 sheets where the
model takes its items from, and the adversarial check of the previous round
(`build/adversarial-layout-r6.json`). I did not write this layout.

**Commit.** HEAD `709fcf20` on `stage/lng-terminal-1-concept`. The round is 79d5c7ad (response
D-030 / D-031), d80ce66c (HAZOP revised), c0554145 (review records design-6 and layout-4) and
709fcf20 (the response: D-032, D-033, and edits to D-016, D-018, D-023, D-026, D-030, D-031; 38
files changed against c0554145, among them `layout/zones.yaml`, `site-plan.yaml`,
`equipment-placement.yaml`, `building.yaml`, `structures.yaml`, the electrical list and cable
schedule, the T-8101 / T-8102 datasheets, P-05 / P-06 and the accepts). My working tree had no
change of mine in the scope. Other agents had uncommitted HAZOP edits and a design review record
in the folder while I worked. They are not part of what I reviewed.

**Verdict.** The response closes the high of 2026-11-05-basic-layout-4 (#1). It closes the
missed high of its adversarial check (the muster point inside the drip-tray fire) on model
evidence, and four of its mediums (#3 to #6). Two findings of review 4 are carried into new
findings of this record (#2 into #6, #7 into #7). Two of its lows stay open (#8, #9). I wrote my
own site-wide screening (`build/rev5_fire.py`, `build/rev5_jetty.py`) and ran it from the zones
as they stand. It reproduces the D-033.9 table to within 0.1-0.2 kW/m2 at every receptor class
of D-018. The one exception is the jetty hull receptors, where I take the envelope boxes and so
get the higher values. The fresh pass finds no critical and no high. It finds six mediums and
five lows. Three of the mediums are about what the screening table leaves out:
- the basis for removing the collection at the risers (#1);
- the item drip trays that were added (#2);
- the BOG compressors, which stand in the design fire's 8 kW/m2 band (#3).

Two more mediums come from the moves of this round: the basin moved out of reach of any road
(#4), and the platform junction boxes now stand in the new drip-tray bays (#5). The last medium
is the B-SUB vapour distance, which is carried honestly (#6). With no critical or high open, the
layout can be issued for basic engineering, carrying the mediums below. A merge is pending; it
is for a human or the reviewer, not the author.

## Findings
| id | area | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-layout-5#1 | A1 riser racks PR5 / PR6, riser towers, PR3 (D-018, D-033.1, D-033.11) | PSV-1122 (T1022 on LNG-1002), PSV-1121, PSV-1123, PSV-4111, PSV-4113; riser runs LNG-1001 / 1002 / 1004, LNG-2001 / 2002, LNG-3001 / 3002, LNG-4005 / 4009 | D-033.1 removes the collection beside the shells because "the model's in-line items show" that the riser runs are welded, with no leak source. The in-line items cannot show that. D-021 item 7 leaves the low-point drains, the vents of the long lines and the instrument root valves off the P&IDs, so the model has none of them, and nothing in the line list or `pipe-specs.yaml` records an all-welded requirement for these runs (no "weld" anywhere in `piping/`). On the model the risers do hold a flanged leak source. The DN 25 thermal relief branch of PSV-1122 tees off the DN 900 fill line LNG-1002 at 12.5 m on PR6's west lane, at (982, 2997). That is ~14 m from the T-2101 shell, beside S-RT2101 (section `build/layout-section-y2997_crop-965--3-1005-20.png`). D-033.1 says detail design moves its inlet to the PR1 joint; D-033.11 instead keeps it at the item with a drip tray. Neither the tray nor a zone 2 is declared for PSV-1122, PSV-1123 (PR1 west, x 900), PSV-4111 or PSV-4113. PSV-1121 is not covered at all: it is the thermal relief of the DN 900 rundown header at (1088.6, 3000, 9.0) on PR3's west edge, 6.1 m from the trough, and it is not in the D-033.11 list, with no pad, tray or zone. A leak at these points falls to grade where nothing is collected. Beside the risers, that grade is next to the outer tank (the exposure of review 3 #2). | medium | open | Make the basis binding where detail design will read it: in the line list notes and the pipe class of the riser runs, state that they are all-welded between the dome edge and the PR1 joint, with no flanged joint, drain, vent or instrument tapping. State also that the low-point drains of the riser runs sit at the PR1 joint over the trough or a pad. Move PSV-1122's inlet to the PR1 joint over the trough, as D-033.1 first said. Declare the drip trays and the zone 2 of every DN 25 thermal relief, and add PSV-1121. |
| 2026-11-05-basic-layout-5#2 | A1 / A2 item drip trays (layout/zones.yaml Z-HA-TRAY-XV3123 / -TV7103, D-018 (g), D-033.11 (a)(i) and (c)) | XV-3123 on PR5, TV-7103 on the PR6 east leg over D-7101 | (a) The holding times are computed at water density. 3 m3 of LNG at ~450 kg/m3 is 1.35 t, which lasts 22.5 min at the stated 1 kg/s (not ~50 min). 1.6 m3 is 12.3 min of the 3.5 t/h spray flow (not ~27 min). The stated values match 1,000 kg/m3 (`build/rev5_hyd.py`). (b) The response rests on the operator seeing the leak, but the low-temperature detectors in the trays are not on the P&IDs (D-033.10, design owner). (c) An overflow falls from 11-12 m onto grade where nothing is collected: PR1 west beside the T-3101 riser foot, and the BOG area at D-7101. (d) Each tray holds a pool fire inside a rack: XV-3123's tray lies at ~11.3 m under PR5's 12 / 14 m tiers, with the DN 900 rundown and the DN 800 header to T-3101, and TV-7103's lies at 10.8-13.6 m directly over the BOG suction drum D-7101. An LNG fire of 6 m2 is ~8 m tall, so it engulfs the tiers above. By my point source the tray fires give 16 kW/m2 at the PR5 edge and 13 kW/m2 at D-7101. The table screens them only at distant receptors (A2N 1.1). D-033.11 (b) / (h) drop PR5 from the PFP extents ("needs none") and stop the PR6 east-leg PFP at x 1060, so no fire protection is recorded for these near fields. | medium | open | Correct the holding times at LNG density, and size each tray for the time to detect and isolate. Put the low-temperature detector and its alarm on P-03 / P-07, which is a prerequisite of the tray concept. Record PFP (or deluge) for the PR5 joint bays and for the PR6 east leg over D-7101, or give each tray a drained downcomer to a pad at grade. If TV-7103 moves onto PR3 (design owner), its tray goes over the trough. |
| 2026-11-05-basic-layout-5#3 | A2 BOG compressors (D-018 receptor list, D-033.11 (a)(ii), Z-ESC-A2N-W basis) | K-7101A / B / C, D-7101, FL-7002 / FL-7003 | My screening of the design fire (every open trough leg with the gutters, the basin and the east pad cluster; `build/rev5_a2.py`) gives these values at the compressor packages: K-7101A 6.9, K-7101B 7.7 and K-7101C 9.5 kW/m2 (8.1 for K-7101C without the pads). Most of A2 south of y 3002 is above 5 kW/m2, rising to 15-20 kW/m2 at its south edge. Two consequences follow. (a) Equipment: the BOG compressors hold flammable gas and lie above 8 kW/m2, but D-018 lists no receptor class for process equipment and D-033.7 records no protection for them. The compressor relief and vent lines FL-7002 (DN 200) and FL-7003 rise at 3.3-3.6 m over the PR3 trough at y ~2976, inside a ~2.8 m trough flame (`build/rev5_lowcross.py`). (b) Escape: D-033.11 states that "the 18-28 m from the compressor packages to it lie in the area at 5.1-5.7 kW/m2". On my numbers an operator at K-7101C starts at 9.5 and at K-7101B at 7.7, and walks 30-40 m to Z-ESC-A2N-W. The way itself (4.9) meets the criterion. The walk to it is understated. | medium | open | Add process equipment with flammable inventory (the compressor packages, D-7101) as a receptor class at 8 kW/m2 to D-018, and record deluge or PFP for K-7101A-C and the low flare risers over the trough (D-033.7, ASSUMED until the fire protection design). Correct the D-033.11 / Z-ESC-A2N-W statement to the values at the packages. If the criterion is to hold for the walk too, shield it or give the compressor row a way out to the north-west that starts at the packages. |
| 2026-11-05-basic-layout-5#4 | A8 impoundment basin after its move (site-plan.yaml roads and PR8, equipment list P-8102, D-033.7 approach list, D-033.11 (a)(ii)) | T-8101, P-8102, PR8, JB-A8-1, R2 | The basin moved to (990, 3237.5). `cheme show T-8101 --layout` gives R2 at 103.5 m, and no road, hardstanding or lane reaches A8. D-033.7 names "R2 and R4" as the fire approach to the west leg and the basin, but the leg lies 111 m north of R2 and R4 is ~280 m away. That is beyond monitor reach, so the basin and the west leg have no approach in the sense of D-018 (d). The same applies to foam replenishment and to maintenance of the pump and instruments. PR8 now runs 17 m south of the west leg and joins PR4 over the trough. My screening gives it ~14-15 kW/m2 along its run and over 600 at its east end, and it carries every cable of P-8102, LI-8103 and TSL-8102. P-8102 is still listed as a 1.5 t vertical in-line pump at grade (`variant: vertical_inline`). A pump at grade cannot draw water out of the 10.5 m pit; D-033.3 carries this to the design owner. | medium | open | Give A8 a road spur and hardstanding from R2 (or R4), outside the 8 kW/m2 band of the basin and the west leg. Name it in D-033.7 as the approach to the basin and the west leg. Record fire-resistant cable or buried duct for the PR8 cables. Change P-8102 to a submersible or vertical-turbine pump in the pit, with a lift-out davit (equipment list and P-08, design owner). |
| 2026-11-05-basic-layout-5#5 | A4 platform electrical (electrical/electrical-list.yaml junction_boxes, D-016, D-033.4 / .7) | JB-A4-1 (1147.5, 880.5, 1.2), JB-A4-2 (1161.0, 880.5, 1.2), JB-PR1 | Both platform junction boxes stand inside the new manifold drip-tray bays: JB-A4-1 in Z-HA-TRAY-B2-MAN and JB-A4-2 in Z-HA-TRAY-B1-MAN, the bays where the platform design spill lands and burns (`build/rev5_jb.py`). Their notes still say "outside the manifold zone". They carry all of a berth's field circuits ("*-5*" / "*-6*"): ESD, ERS, the berth O2 analyser, TSL-8104 and the shore valve switches. The emergency release couplers are energise-to-release (D-016), so a fire at the bay that destroys the box takes away the arms' emergency release in the event that may need it. The ESD / F&G cable protection of D-033.7 covers only the tank-area route over the trough. Minor: JB-PR1 (1070, 2956) stands inside the laydown Z-LAY-A2E. No rule sees either case, because the zones stop at 1.0 m and the boxes sit at 1.2 m. | medium | open | Move JB-A4-1 / JB-A4-2 out of every tray bay (for example to the north edge beside the HPUs, outside the bays and crane strips) and correct their notes. Record fire-resistant cable (IEC 60331, cited by number only) for the ESD / ERS / ERC circuits on the platform in D-033.7. Move JB-PR1 off the laydown. |
| 2026-11-05-basic-layout-5#6 | A6 B-SUB (site-plan.yaml separations, layout/hvac.yaml, D-018, D-033.2 (d)) | B-SUB, TR-1 / TR-2 bays, Z-KC-TROUGH-PR3 | This is the remainder of 2026-11-05-basic-layout-4#2. The trough release sources are now declared (Z-HA-TROUGH-*), but B-SUB and the bays stay 69.7 m from the PR3 / PR4 leg, against the 150 m that D-018 keeps from the basin for the cold vapour. D-033.2 (d) carries this to the siting study with a reason I find sound. My numbers: lined at 1.81 kW/m2 mean over the first minute, the whole 510 m of open trough forms ~5.8 kg/s at the design flow, ~0.011 kg/(m s), about a fifth to a tenth of my review-4 bare-concrete line source. The trough also holds liquid only while the spill flows. Medium is therefore the honest rating. But the interim safeguard it rests on, gas detection at the B-SUB intake LV1 with a damper trip, is recorded only in DESIGN.md. `layout/hvac.yaml` says the intake gas detection is "detail engineering", and no instrument exists for it. | medium | open | Record the LV1 gas detectors and the damper trip as ASSUMED requirements in `layout/hvac.yaml` and in the instrument list or C&E (design owner). Record the transformer-bay ignition-source review with the electrical engineer. Keep the 69.7 m on the siting study's list. |
| 2026-11-05-basic-layout-5#7 | texts (P-08 note, equipment list, DESIGN.md D-033.7 / .10) | T-8101, P-08 note, datasheets T-8101 / T-8102, residual road values | This is the remainder of 2026-11-05-basic-layout-4#7 (c). The P-08 note (scripts/draft_P-08.py line 276) and the T-8101 service in the equipment list still read "tank area and trestle troughs" / "(tank area and trestle)". D-018 and D-033.2 removed the trestle tray and the PR2 trough. D-033.10 says the T-8101 / T-8102 datasheets warn until they follow the equipment list, but 709fcf20 already updated them (10.5 m; 6 / 9.5 m) and validate shows no `datasheet-dimension-*`. Several D-033.7 residual values predate D-033.11; with the east pads my values are R5 stub 18.7 (stated 15.2), R6 15.8 (13.6), R3 14.3 (13.7) and R8 west 11.9 (11.5). The table row of D-033.9 gives them as a range and stays right. | low | open | Align the P-08 note and the T-8101 service (design owner, P-08). Update D-033.7 / D-033.10 to the values and the datasheet state at HEAD. |
| 2026-11-05-basic-layout-5#8 | electrical (electrical-list.yaml, cable schedule, D-016 / D-032.2) | UPS A / UPS B, HS-5100 / 5107 / 6100 / 6107 | D-032.2 feeds channel A of every ERS solenoid from UPS A and channel B from UPS B, on separate distribution. The electrical list names no UPS (TR-3's notes name "UPS" as one load), and nothing shows the two supplies reaching the platform HPUs. The hard-wired ESD-1 / ESD-2 push buttons HS-5100 / HS-5107 / HS-6100 / HS-6107 (jetty head and platform) are field devices with no cable in `electrical/cable-schedule.csv`. The motor-control HS tags of P-08 are cabled. The electrical gate passes because it does not count these tags. | low | open | Add UPS A / UPS B and their separate feeders to B-JET / the HPUs in the electrical list, ASSUMED. Give the push buttons points and junction boxes so they are cabled. |
| 2026-11-05-basic-layout-5#9 | A4 crane strips (layout/zones.yaml Z-PAD-A4W / -A4E, D-033.10) | Z-PAD-A4W over Z-HA-TRAY-B2-MAN, Z-PAD-A4E over Z-HA-TRAY-B1-MAN, LA-5101..6104 lifts | The crane strips overlap the manifold tray bays by 6.0 m (A4W x 1140.5-1146.5) and 7.5 m (A4E x 1162-1169.5). Both are 1.0 m recessed LNG bays with open floor outlets and the collectors -W / -B1M under them. The 45 t arm lifts (69.3 t capacity needed) are planned from these strips. D-033.10 carries "load-bearing covers over the drip tray bays inside the crane strips" to the structural engineer. A cover that bears outrigger loads and also lets drips into the bay is a design conflict, not a detail. The item is honestly stated, but no finding tracked it. | low | open | Place the crane's outrigger positions outside the bays (the strips' north part, y 895-900, and the deck between the rows), or record the cover type (grating on beams) and its load with the arm vendor's lift plan. |
| 2026-11-05-basic-layout-5#10 | A9 / A4 jetty pits (zones.yaml Z-HA-SUMP-T8102, Z-KC-CHANNEL-JETTY*, Z-SZ-B1 / B2, ship envelopes) | T-8102 (pit to -9.5 m), collectors to -3.91 m | The deck datum's height above the water has no basis. The ship envelopes take the waterline at -12 m (ASSUMED). The marine safety zones are drawn on the water from -6 m down, and the 9.5 m sump pit reaches into that volume (section `build/layout-section-x1163.5_crop-795--15-935-30.png`). With the -12 m waterline the pit bottom is 2.5 m above the water. Kitimat's tidal range is not in the source register. If high water stands above -9.5 m, the sump sits in the tidal zone (buoyancy, water ingress, LNG on water). D-033.10 carries the pit to the marine engineer, but not this conflict of datums. | low | open | Record the deck level above HAT and the design water levels (source register), make the Z-SZ volumes and the ship waterline agree, and check the sump bottom and the collector inverts against HAT with freeboard (marine engineer). |
| 2026-11-05-basic-layout-5#11 | A4 platform deck (D-018 (e), D-033.5) | travel from the berth work positions to the starts of W1 / W2 | D-018 (e) and the screening judge each way off over its own length, and those values hold. My best-way worst case is 4.83 kW/m2 (B2-M8, W2), the same as D-033's 4.8. The walk on the deck to the way that a given fire leaves open is not screened. For a fire at the north Berth 2 arm bay (B2-A4), an operator at the Berth 2 arms must cross the north edge under PR2 to the W2 start. That walk passes ~24 m from the bay (~8 kW/m2), and the W1 start beside it sees 6.9. For B1-A4 the W2 start sees 6.0 and the R10 crossing under PR2 ~20. | low | open | Record the platform evacuation route from each work position to the start of each way off (D-033.5). Give the north-edge crossing a water curtain, or a route that keeps 5 kW/m2 for the fires it serves. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-layout#1 | B-PLAT substation inside the 200 m loading-point radius | high | closed e11eb12a | B-JET separations to all eight arms still met (0 `layout-separation`); T-8102 to B-JET 290.9 m. |
| 2026-11-05-basic-layout#2 | Road R5 blocked by B-PLAT; no crane access to the platform | high | closed e11eb12a | Lifting study: all eight arms "lane clear" from Z-PAD-A4W / -A4E. Their overlap with the tray bays is #9 of this record. |
| 2026-11-05-basic-layout#3 | B-SUB 4 m off PR2 | high | closed e11eb12a | `cheme show B-SUB --layout`: PR3 63.0, PR2 63.8, PR1 70.1 m. |
| 2026-11-05-basic-layout#4 | Tank-top pump platform missing | high | closed e11eb12a | Level plans `build/layout-level-S-T2101-TOP-PP_crop-875-2975-1010-3110.png`, `build/layout-level-S-T3101-TOP-PP_crop-735-2975-870-3110.png`. |
| 2026-11-05-basic-layout#5 | Roads not one network | medium | closed e11eb12a | R11 now links R1 / R5 with R8, so B-SUB has a second road. |
| 2026-11-05-basic-layout#6 | Safety zone of one berth holds the other carrier | medium | closed e11eb12a | D-027.5 basis unchanged. |
| 2026-11-05-basic-layout#7 | Direct route chains | medium | closed e11eb12a | Report: no `direct`, no `rack+direct`. |
| 2026-11-05-basic-layout#8 | 80 mm insulation on the trestle lines | medium | closed e11eb12a | `pipe-specs.yaml` 200 / 150 mm unchanged. |
| 2026-11-05-basic-layout#9 | Span screening classes LNG as gas | medium | open | Unchanged. The free-span accept block still says every line is screened "as gas", 26 free-span / 23 support-missing, each accepted by id. No report to cheme-as-code is recorded. |
| 2026-11-05-basic-layout#10 | Wildcard free-span / tray-span accepts | medium | closed e11eb12a | No rule wildcard. `*-PR?-PR?` stays limited to the joint link trays. |
| 2026-11-05-basic-layout#11 | No escape zones | medium | closed e11eb12a | 15 escape zones, among them the new Z-ESC-A4-MUSTER, -A4-SEA, -A4-E1 / -E2 / -X. |
| 2026-11-05-basic-layout#12 | No contraction space on the trestle | medium | closed e11eb12a | Z-LOOP-01..12 unchanged. Sizing: 2026-11-05-basic-layout-2#6. |
| 2026-11-05-basic-layout#13 | Unbuildable generated VP-* platforms | medium | closed e11eb12a | Structures declared 7, none generated. |
| 2026-11-05-basic-layout#14 | No DESIGN.md entry for the layout pass | medium | closed e11eb12a | D-033. |
| 2026-11-05-basic-layout#15 | B-SUB comment distance | low | closed e11eb12a | K-7101C 110.8 m measured. |
| 2026-11-05-basic-layout#16 | Derrick hoist not in D-017 | low | closed e11eb12a | D-027.14. |
| 2026-11-05-basic-layout#17 | Spill containment not in the model | low | closed e11eb12a | Troughs, gutters, pads, item trays, tray bays, collectors and both sumps are declared zones. |
| 2026-11-05-basic-layout#18 | Reviewed files uncommitted | low | closed fa3304be | This record names the committed HEAD 709fcf20. |
| 2026-11-05-basic-layout-2#1 | In-tank pump removal path ruled out by the model | high | closed f5d925f6 | Lifting study: P-n101A-D at 61.1-74.7 m from the 34 x 26 m pads, 9.24 t needed. |
| 2026-11-05-basic-layout-2#2 | Impoundment sump T-8101 at the riser rack and tank | high | superseded by 2026-11-05-basic-layout-4#1 | I agree with the adversarial check: review 4 should not have marked it closed, because its disputed part (the collection beside the shell and under S-RT2101) was carried as -4#1. The basin siting part holds: T-8101 is 166.2 m from T-2101, 90.0 m from PR4, 103.5 m from R2 and 170.5 m from PR6, with 0 `layout-separation`. -4#1 is closed in 709fcf20 (below); what remains is #1 of this record. |
| 2026-11-05-basic-layout-2#3 | No flare radiation basis at B-SUB | medium | open | B-SUB unmoved (316 m from FL-8101 against 314.3 m to the fence). The derrick owner's contour is still owed (D-031.14, carried by D-033.10). |
| 2026-11-05-basic-layout-2#4 | East way out of A2 blocked by BOG-7002 | medium | closed f5d925f6 | `layout-headroom` 0. A trough fire blocks A2E by design (#3 of this record). |
| 2026-11-05-basic-layout-2#5 | DN 800 / 900 LNG lines at 80 mm insulation | medium | open | `pipe-specs.yaml` unchanged in 709fcf20. Rack fill PR1 7 m 46 %, PR4 33 % still understated. |
| 2026-11-05-basic-layout-2#6 | Loop bays unsized, loops not routed | medium | open | Unchanged; the stress engineer's. |
| 2026-11-05-basic-layout-2#7 | Family accepts for tray spans and line routes | medium | closed f5d925f6 | Unchanged, per-tray and per-line entries. |
| 2026-11-05-basic-layout-2#8 | Dome-edge valves out of reach; XV-2123 / XV-3123 differ | medium | open | The roof nozzle platform is still tank supply and not modelled. D-033.1 now also puts the dome-edge drip trays on it, so more rests on this open item. |
| 2026-11-05-basic-layout-2#9 | No zones at the column heads | medium | closed f5d925f6 | Z-HA-Tn101-COLHEADS in the level plans. |
| 2026-11-05-basic-layout-2#10 | Oil-filled transformers inside B-SUB; no 69 kV bay or route | medium | open | The bays now have road R11 and the hardstanding Z-LAY-TX (review 4 #6, closed). B-SUB room sizing and the 69 kV route are still the electrical engineer's. |
| 2026-11-05-basic-layout-2#11 | Artefact frame in the take-off | low | closed f5d925f6 | Unchanged. |
| 2026-11-05-basic-layout-2#12 | Roof walkways do not meet the deck | low | closed f5d925f6 | Level plans as above. |
| 2026-11-05-basic-layout-2#13 | PSV / vacuum valve inlet isolations at foot level | low | accepted: locked-open isolations operated only for valve change-out; in-line item placement is not settable in cheme-as-code 1.7.0 (D-029.18); accepted by the author in f5d925f6, this reviewer concurs | Unchanged. |
| 2026-11-05-basic-layout-2#14 | No site wind basis | low | open | No source in the register. The B-SUB vapour carry (#6) and the muster siting still cannot be checked against the wind. |
| 2026-11-05-basic-layout-2#15 | Drain and KO pump suction valves below deck or grade | low | accepted: model artefact of the in-line item placement of cheme-as-code 1.7.0 (D-029.18); accepted by the author in f5d925f6, this reviewer concurs | Accepts `HV??1[57]` / `HV8106?` current. |
| 2026-11-05-basic-layout-3#1 | Jetty spill trough under the muster point and escape-to-sea station | high | closed 79d5c7ad | No trough remains on the platform or the catwalk (Z-KC-CHANNEL-JETTY-CW is enclosed into the sump). The muster point is on A7. |
| 2026-11-05-basic-layout-3#2 | Tank-area trough under PR6 and S-RT2101 | medium | superseded by 2026-11-05-basic-layout-4#1 | As in review 4. |
| 2026-11-05-basic-layout-3#3 | Trestle drainage concept | medium | closed 79d5c7ad | No tray on the welded trestle run; the PR2 trough is removed too (D-033.2). The stale texts are #7. |
| 2026-11-05-basic-layout-3#4 | T-8102 without level, water removal or access | medium | open | Access done (S-CW-A9). Level, high alarm and fixed water removal with a low-temperature trip are still not on P-08 (D-033.10). With ~129 mm of rain margin and no rainfall basis, "kept pumped down" cannot yet be done. |
| 2026-11-05-basic-layout-3#5 | Sump siting criteria not conservative | medium | closed 79d5c7ad | The x 1.2 tilt and 1.6 kW/m2 at the muster point are applied everywhere (my screening). |
| 2026-11-05-basic-layout-3#6 | Pump removal: hook height, pad size, stair, lift over live plant, bearing | medium | closed 79d5c7ad | (c) carried as 2026-11-05-basic-layout-4#8. |
| 2026-11-05-basic-layout-3#7 | Both roof exits beside the PSV outlets | medium | open | Unchanged. The roof clearing on the tank high-pressure alarm is still only in D-031.8; no alarm, sequence or operating record holds it. |
| 2026-11-05-basic-layout-3#8 | Transformer bays facing the AHU-1 intake | medium | closed 79d5c7ad | LV1 on the east wall at y 2967.5, the bays south of B-SUB. |
| 2026-11-05-basic-layout-3#9 | Riser towers: clearance to the tank, members at the drops, 13 m posts | medium | open | (a) unchanged: `cheme show T-2101 --layout` S-RT2101 0.6 m, left to the tank contractor. |
| 2026-11-05-basic-layout-3#10 | Accept reasons that do not match the model; FL-8101 lifting row | low | accepted: (a)-(c) fixed in 79d5c7ad; (d) the FL-8101 row cannot be marked as an unplanned lift in cheme-as-code 1.7.0 and the stack is maintained by the derrick hoist (D-027.14, D-031.11); accepted by the author in 79d5c7ad, this reviewer concurs | 0 `accept-unused` / `accept-stale`. |
| 2026-11-05-basic-layout-3#11 | A2 east escape route across the crane pad | low | closed 79d5c7ad | D-031.12. |
| 2026-11-05-basic-layout-3#12 | No zones at the dome-edge nozzles and manholes | low | closed 79d5c7ad | Z-HA-Tn101-DOMEEDGE in the level plans. |
| 2026-11-05-basic-layout-4#1 | Enclosed channels beside the shells not sized for the vapour | high | closed 709fcf20 | Z-KC-CHANNEL-PR5 / -PR6 are gone from `layout/zones.yaml` and the model. Section `build/layout-section-y2997_crop-870--5-1120-70.png` shows nothing at grade under PR6 or S-RT2101. I reproduce D-033.1's screening of the removed channel (45.7 kW/m2 bare, 1.31 m / 0.97 m Manning depths). The basis of the removal, "welded, no leak source", is new matter: #1 of this record. |
| 2026-11-05-basic-layout-4#2 | Open troughs not release sources; B-SUB and the bays at 69.7 m | medium | superseded by 2026-11-05-basic-layout-5#6 | Z-HA-TROUGH-PR1 / -PR3 / -SUMP, Z-HA-CATCH-* and the item trays are declared zones (0 tray or escape route in them, apart from the stated culverts and the A2S crossing). The remaining 69.7 m carry is #6. |
| 2026-11-05-basic-layout-4#3 | Trough not drainable as drawn (fall, basin depth, catchment) | medium | closed 709fcf20 | My Manning check: 1.31 m deep at 0.5 % for 1.67 m3/s in 0.6 m. Profile arithmetic over 510 m: -1.61 / -2.21 / -2.46 / -3.10 / -3.67 / -4.16 m, all consistent. T-8101 is 10.5 m deep (equipment list, datasheet, zone): 4.97 m of spill, standing at -5.53 m, 1.37 m below the inlet. Drip pads with spray shields replace the rack-edge catchment. Zone boxes `Z-KC-TROUGH-*` -2.25 / -3.70 / -4.20 m. |
| 2026-11-05-basic-layout-4#4 | Roads in the trough band, no fire approach, no fire protection | medium | closed 709fcf20 | R1 (y 2901) 7.2 and R11 5.9 kW/m2 in the design fire by my screening. R8 east of x 1130 6.9, R2 west of x 1050 6.95 and east of x 1130 7.4. The approaches are named and the residual roads are stated. FP is recorded ASSUMED in D-033.7 / .11 (h). The basin's approach after its move is new matter: #4. |
| 2026-11-05-basic-layout-4#5 | Both ways off the platform at one corner; muster point exposed | medium | closed 709fcf20 | Muster point Z-ESC-A4-MUSTER on A7 (x 1113-1131, y 1118-1130). Two ways start 20 m apart at the north-edge corners with PR2 between them (R5 and Z-ESC-A4-E1 / -E2 / -X). My screening per bay (27 bays, sump and collector vapour flame at the sump or at the worst dry outlet downstream): best way worst 4.83 (B2-M8, W2), XO 4.04 / 4.14. Muster 0.16 for the worst single bay; 1.06 / 1.19 with every Berth 2 / Berth 1 bay burning. Boat route 0.15, now 71 m north of the Berth 2 hull envelope. Plan `build/layout-plan_crop-1080-790-1240-1150.png`, section `build/layout-section-y1119_crop-1080--14-1170-16.png`. The walk on the deck to the ways is #11. |
| 2026-11-05-basic-layout-4#6 | Transformer bays without road or lane; escape door S1 beside them | medium | closed 709fcf20 | R11 runs along the bays' south side and north to R8. Z-LAY-TX (x 1165-1195, y 2904-2920) lies between R11 and the bays. S1 is on the west wall at y ~2960 (`layout/building.yaml`), 2.95 kW/m2 by my screening, and the walk from S1 or N2 to R11 / R8 east stays at 3.2 kW/m2 or less. |
| 2026-11-05-basic-layout-4#7 | Screening statements and texts that do not match | low | superseded by 2026-11-05-basic-layout-5#7 | (a) Z-ESC-A2N-W now ends at x 1022: 4.89 kW/m2 by my screening. (b) The catwalk trough is removed. (c) is still open: #7. |
| 2026-11-05-basic-layout-4#8 | Pump removal path over P-2102 | low | open | Neither D-033 nor the accept `layout-lifting:P-2101[A-D]` changed. Its reason still states a lift "along the deck's north-south axis between the rows, no load over a running pump's head", and P-2102 stands on that axis at (947, 3040). The accept's reason is not true on the model. |
| 2026-11-05-basic-layout-4#9 | Sump deck A9 a dead end; cable beside the open trough | low | open | D-033.4 records that the catwalk and A9 are kept clear during transfers, and the catwalk trough is now an enclosed collector, so the TSL-8104 cable no longer runs beside an open trough. The escape ladder and life ring at A9's south edge are not added (`structures.yaml` S-CW-A9: two ladders "from grade" only). |

Adversarial-check items raised against 2026-11-05-basic-layout-4 (`build/adversarial-layout-r6.json`), judged on the model:
- **Disputed closure of 2026-11-05-basic-layout-2#2:** upheld. It reads "superseded by
  2026-11-05-basic-layout-4#1" above, which D-033.8 (a) also asks for. The basin siting part
  holds on the measured distances.
- **Missed high, the muster point within the drip-tray fire:** answered on model evidence. The
  trays are modelled as 27 bays of at most 36 m2 (Z-HA-TRAY-B2-ARMS / -B2-MAN / -B1-ARMS /
  -B1-MAN / -XO, recessed 1.0-2.4 m). The muster point, life rafts and boat landing are on the
  B-JET deck A7, 214 m from the nearest bay, at 0.16 kW/m2 for the worst bay fire and 1.19 with
  every Berth 1 bay burning (my screening). The two ways off start at opposite corners. The
  remaining low on the walk across the deck is #11.
- **Notes:** the PR5 channel 10.3 m from T-3101 is removed with the channel. B-ANA sees 3.6
  kW/m2 now that the PR2 trough is gone (my value; D-033: 3.6). The "PR6 west tier" release
  source is answered by the welded-run claim, whose basis is #1.

## Site-wide radiation screening (my check of D-033.9)
- Scripts `build/rev5_fire.py` (tank area) and `build/rev5_jetty.py` (platform), written from
  the D-018 statement and not from the author's `r8_screen.py`. Geometry is read from
  `zones.yaml`, `site-plan.yaml`, `structures.yaml`, `building.yaml` and the placement.
  Point source per unit of burning surface, 0.35 x 0.078 kg/(m2 s) x 50 MJ/kg = 1.365 MW/m2
  radiated. Troughs and gutters are lines of 0.25 m elements of 0.82 MW/m. Tilt x 1.2, tau = 1,
  plan distance.
- Tank area, the design fire. Every open leg (PR1 from x 975, PR3 / PR4 to y 3237.5, the west
  leg) burns with both gutters, the basin (201 m2) and the worse of the two pad clusters. My
  value, then D-033.9 in brackets:
  - shells T-2101 4.09 (4.1), T-3101 1.09 (1.1);
  - S-RT2101 4.38 (4.4), S-RT3101 1.28 (1.3);
  - PR6 north of y 2990 5.94 (5.9);
  - PR6 east leg to x 1060 7.78 (7.8);
  - PR2 south of y 2910 6.71 (6.7);
  - PR3 east leg from x 1130 7.39 (7.4);
  - PR4 north of y 3273 7.56 (7.6);
  - B-SUB 3.12 (3.1), door S1 2.95;
  - B-ANA 3.61 (3.6), TX bays 2.72 (2.7);
  - roads R1 7.18 (7.1), R11 5.87 (5.8), R8 x ≥ 1130 6.93 (6.9), R2 6.95 / 7.43 (6.9 / 7.4), R4 0.58 (0.6);
  - crane pads / laydowns 3.5 (3.5);
  - Z-ESC-A2N-W 4.89 (4.8), Z-ESC-A2N 4.22 (4.2);
  - stair towers 2.27 / 0.89 (2.3 / 0.9).

  Over their criterion and stated as residuals in D-033: the PFP bands on PR6 at the joint (47-413)
  and on the PR6 east leg x 1060-1088 (35.6); R3 14.3, R6 15.8, the R5 stub 18.7 and R8 west of
  x 1130 11.9; the culverts on R7 and R2 (over 600); A2S, which crosses the trough; A2E 22.2.
  Not in the table: PR8 (14-627, #4), K-7101A-C (6.9-9.5, #3) and D-7101 4.7.
- Item trays alone: XV-3123 (6 m2) gives at most 0.5 kW/m2 at any receptor of D-018 but 16 at
  the PR5 edge. TV-7103 (4 m2) gives 1.08 at A2N, as D-033 states, but 13 at D-7101 (#2). The
  DN 25 PSV trays are not declared and could not be screened (#1).
- Platform: one bay at a time with the sump (28.3 m2) and the collector vapour flame (0.67
  kg/s, 11.7 MW radiated) at the sump or at the worst dry outlet downstream on the same
  collector. Best way worst 4.83 (B2-M8, W2); XO 4.04 (W1) / 4.14 (W2). Muster 0.16; 1.06 / 1.19
  with every Berth 2 / Berth 1 bay burning. Boat route 0.15. The sump with its vapour alone
  gives W1 0.36, W2 0.38 and the hull envelope boxes 5.8 / 5.3 (D-033: boxes 2.4-5.8). The drums
  D-5101 / D-6101 and the hulls at their own manifold see 20-205 kW/m2 from the adjacent bays;
  that is the near field which D-033.7 gives to deluge and the carriers' own protection, as
  D-018 (e) states.
- Vapour of the enclosed jetty collectors (`build/rev5_hyd.py`): 1.11 m3/s runs 0.40 m deep
  (Manning, 1 %). Lined (k 0.05 W/(m K), 120 kg/m3, 840 J/(kg K)), the flux is 1.81 kW/m2 mean
  over the first minute. Over 71.5 m / 106 m this forms 0.45 / 0.67 kg/s, giving with the
  displaced gas 1.69 / 1.84 m/s and ~4 / ~7 Pa. On bare concrete it would be 17 kg/s, 13 m/s and
  ~0.4 kPa, still below the cover weight. The collectors work even unlined. D-033.11 is
  confirmed.

## Drawing
Not part of this layout review. No P&ID was reviewed; the P&IDs serve only as the source of the
model. For reference, the `cheme validate` count lines at HEAD are all 0. The accepted ones are
P-04 `0 line-crossing (+2 accepted)`, P-07 `(+2 accepted)` and P-08 `(+1 accepted)`.

## Layout
Commands run at HEAD 709fcf20, from the plant folder, with core 1.7.0:
- `cheme layout build --check`: `layout/plant-model.yaml is up to date`.
- `cheme validate`: `88 file(s): 0 error(s), 17 warning(s)`. All 17 warnings are
  `hazop-input-changed` (outside this scope). The layout model findings are infos with their
  accept reasons. There is no `accept-unused`, `accept-stale`, `review-*` or
  `datasheet-dimension-*`.
- `cheme check --stage detail`: every gate ok except two. FAIL design-review (design-6 names
  79d5c7ad and files changed since; outside this scope). FAIL layout-review (layout-4 names
  79d5c7ad and layout files changed since): this record, at 709fcf20, replaces it.
- `cheme diff main --list`: 1,076 lines. All ten sheets are added on the branch (P-01 to P-08,
  BFD, PFD). The layout files are not in the item diff.

`cheme layout report`:
- Lines: every line is routed, none is skipped, and 0 are unrouted.
- Chains per method: astar 45, astar_coarse 3, open 8, pinned 181, rack 9, via 9. There are no
  `direct` and no `rack+direct` chains.
- Chains per reason: pinned 181; local pipe-way 21; local above the pipe-way 10; intent via 9;
  local short run 9; open end 8; local pump run at grade 4; rack battery limit at a rack end 4;
  rack longer than local_max_m 4; local rack run too short 3; local no rack in reach 1; rack
  crosses a road 1. Battery-limit ends: rule 16, rack end 1.
- Rack fill: PR1 7 m 46 % / 10 m 27 %; PR2 31 % / 26 %; PR3 10 % / 24 %; PR4 7 m 33 %; PR5 12 m
  16 % / 14 m 6 %; PR6 21 % / 10 %; PR8 7 m 4 %. PR1 and PR4 are understated
  (2026-11-05-basic-layout-2#5).
- Model findings per rule, all accepted: operability 54, tray-span 37, free-span 26 (W-8002's
  PR8 corner span went with the move), support-missing 23 (info), tray-zone 14, lifting 12,
  tier 4, tray-separation 3, escape-ways 2, escape-travel 2, laydown 2, clash-pipe-steel 1.
- These are 0: the other clash-* rules, headroom, access-blocked, zone-crossing, separation,
  spacing, building-spacing, wall-penetration, vent-outlet, access-enclosed / -unconnected,
  ladder-clearance, walkway-riser, landing-width, egress-zone, operator-unknown, pad-overlap,
  zone-source, support-stub, steel-in-way and pipe-disconnected. Zero means only that nothing
  declared was hit.
- Rules missing from cheme-as-code, for the cases no rule sees:
  - equipment or junction boxes standing inside a drip tray or pad volume whose zone stops below
    them (#5);
  - a crane pad overlapping a hazardous tray volume (#9);
  - a release source with no zone, here the DN 25 PSVs (#1);
  - radiation from a declared burning surface at equipment (#2, #3);
  - road access to an area (#4).
- Objects: equipment declared 35, inline generated 198, pipes generated 127 / pinned 181,
  structures declared 7, zones declared 104.

Accepts in `checks/checks.yaml` (layout rules), my view of each group. Each names its items, or
a pattern limited to named tags, and none is a rule wildcard:
- `lifting:T-[23]101`, `laydown:laydown-T-[23]101`, `lifting:D-5101` / `D-6101`: real and
  current.
- `lifting:P-[23]101[A-D]`: the hook and pad parts are real. Its SIMOPS lift-path sentence is
  not true on the model (2026-11-05-basic-layout-4#8, open).
- `operability`: real class or item reasons. `XV[23]123` quotes XV-3123 at 12.7 m, where the
  model has 12.2 m (cosmetic). `XV110[6-9]` / `XV[23]123` rest on the unmodelled roof nozzle
  platform (2026-11-05-basic-layout-2#8).
- Free spans and support-missing (one per finding or a pattern limited to named lines): the
  reasons changed in 709fcf20 are current. LNG-4008 and N-8001 do stand at Z-KC-TROUGH-PR1.
  BOG-1004 is now "PR6's north-east corner". BOG-1011's reason names the trough "east of x 975",
  where the post would not stand, but its post-is-not-worth-its-steel reason holds.
- `line-route` (8), `tier` (2 entries, 4 findings), `clash-pipe-steel` (1), `escape-ways` /
  `escape-travel`, `tray-separation`, `tray-zone` (14), `tray-span`: real and unchanged.

Rendered and read (all under the plant folder, `build/`):
- `build/layout-plan.png`: the whole site.
- `build/layout-plan_crop-700-2860-1220-3270.png`: both tanks and the riser racks with no
  channel under them, the PR1 trough from the PR6 joint, the PR3 / PR4 leg to y 3237.5, the west
  leg into T-8101 in A8 with PR8 and P-8102, R2 103.5 m south of A8 with no road into it (#4),
  R1 / R11 at y 2901, A6 with B-SUB, the bays, Z-LAY-TX and R11's north leg.
- `build/layout-plan_crop-1080-790-1240-1150.png`: the platform with the tray bays and crane
  strips, the catwalk and A9, the trestle with R5 west and W2 east of PR2, the crossing Z-ESC-A4-X,
  the muster point north of B-JET on A7, the boat route west of it, and the hull envelopes and
  the 200 m safety zones.
- `build/layout-level-S-T2101-TOP-PP_crop-875-2975-1010-3110.png` and
  `build/layout-level-S-T3101-TOP-PP_crop-735-2975-870-3110.png`: the pump decks are unchanged.
  The pump-platform and dome-edge drip trays of D-033.1 are not in the model (tank supply,
  2026-11-05-basic-layout-2#8).
- `build/layout-section-y2997_crop-870--5-1120-70.png`: from T-2101 across PR6 and the BOG area
  (K-7101B) to PR3 and the trough. Nothing stands at grade under PR6.
- `build/layout-section-y2997_crop-965--3-1005-20.png`: PR6 at PSV-1122. The DN 25 relief branch
  BOG-1010 rises off the DN 900 LNG-1002 on the 12 m tier, with no tray drawn (#1).
- `build/layout-section-x1163.5_crop-795--15-935-30.png`: jetty head. The sump pit to -9.5 m,
  the catwalk walkway at +0.3 m over Z-KC-CHANNEL-JETTY-CW (-2.3 to -3.91 m), the south
  collector, the B1M collector under the Berth 1 manifold bays, D-6101, the PR2 end tiers, and
  the safety-zone volume from -6 m that the pit reaches into (#10).
- `build/layout-section-y885_crop-1120--6-1190-25.png`: across the platform. Arm bays recessed
  1.5 m with the riser pedestals in them, manifold bays 1.0 m, the four row collectors (-W, -XO,
  -B1M, -E) under them, and the arm envelopes and manifold zone 1 boxes.
- `build/layout-section-y1119_crop-1080--14-1170-16.png`: the muster point on A7, R5's gap, the
  crossing Z-ESC-A4-X under PR2's 7 m tier and E2, and the boat route on the water.
- `build/layout-section-x1095_crop-2880--12-3260-20.png`: along the re-routed collector from
  the junction under PR2's valve zone, PR7, the PR6 east leg and PR4's R2 portal, to the corner
  at y 3237.5 and PR8. The low flare risers stand at y ~2976 (#3).
- `build/layout-section-y3232_crop-960--13-1110-12.png`: the west leg into the 10.5 m basin
  wall, P-8102 at grade at the pit edge, PR8, and PR4 with the trough under it (#4).
- `build/layout-section-x1050_crop-2895--3-3070-20.png`: the BOG compressor area, PR1 with the
  pad and trough zones, K-7101C / B / A, the A2E crossing, the discharge and flare headers, and
  the PR6 east leg (#3).

Measured (`cheme show <tag> --layout`):
- T-2101: S-RT2101 0.6 m, S-ESC-T2101 0.4 m, PR6 5.6 m, PR1 27.8 m, R2 46.2 m, R1 74.8 m.
- T-8101: P-8102 3.6 m, PR8 6.0 m, PR4 90.0 m, R2 103.5 m, T-2101 166.2 m, PR6 170.5 m.
- T-8102: S-CW-A9 9.0 m, D-6101 51.6 m, D-5101 52.4 m, PR2 75.2 m, R10 86.0 m, B-JET 290.9 m.
- B-SUB: R8 2.0 m, R11 7.0 m, R3 45.1 m, PR3 63.0 m, PR2 63.8 m, PR1 70.1 m, B-ANA 84.6 m,
  K-7101C 110.8 m.

## Checked and fine
- Site geometry against D-013 and the task basis. T-2101 (929.4, 3025.8) to LA-5102 (1137, 884)
  is 2,152 m at ~174.5 deg (D-013: 2,147 m at 174 deg, "about 2.1 km"). T-2101 to FL-8101
  (1484.9, 3102.8) is 561 m at 82 deg ("about 560 m east"). D-033 changed neither.
- The removed channels and the PR2 trough are gone from the zones and the model. The only
  flanged in-line items on PR5 / PR6 / the riser towers are PSV-1122 (#1) and TV-7103 on the
  east leg (#2) (`build/rev5_inline.py`, `build/rev5_riserlines.py`). PR1 west of x 975 holds
  only XV-3123 and PSV-1123. PR2's north end holds only the vapour valves XV-4131 / 4132 / 4135
  / 4136.
- Every drip pad lies under its flanged items (XV-1102 / 1103, XV-4105 + PSV-4114, XV-4106,
  FV / XV-4101, FV / XV-4102). PSV-4112, 0.6 m from the trough edge, drips into it. Both gutters
  meet the trough.
- Trough crossings: R7 and R2 at culverts inside Z-HA-TROUGH-PR3 (stated vehicle entry control),
  A2S on a grated crossing (blocked by design, A2N is the way out). No other road or escape route
  crosses a trough or pad. No tray runs below 6 m over a trough (`build/rev5_lowcross.py`).
- PR8 between PR4's bents at y 3212 / 3229, with no PR8 column in the trough (its bent 0 is
  omitted; the first column is at x 1087.1). JB-A8-1 is outside the basin zone. P-8102 is
  0.6 m outside the basin's zone 2.
- R11 under PR2 between its bents at y 2897 / 2905. It runs 2 m clear of the analyser zone, under
  the PR2 valve zone (which starts at 6 m), along Z-LAY-TX and north to R8. The R1 / R4 south
  end at y 2901 and A2S extended to it.
- Platform: bay volumes 36 / 35.75 / 35.6 / 33.6 m3 against the ~33 m3 design spill. The
  collector inverts fall to the sump. T-8102 holds ~159 m3 below its inlet (28.3 m2 x 5.6 m).
  No liquid seals remain. XO is clear of R10 (0.5 m) and of PR2's end bents.
- Ways off: W1 / W2 start 20 m apart; E1 / E2 / X lie clear of the Z-LOOP volumes (6-12.5 m) and
  of every tray zone. B-JET and the muster point are outside both 200 m safety zones (boat route
  235 m from LA-5102). The B-JET north door N1 opens onto the muster point.
- B-SUB: the escape door S1 on the west wall south of PR7 (y ~2960); doors N1 / N2 on R8. A walk
  from either to R11 stays at 3.2 kW/m2 or less in the design fire.
- Basin and trough hydraulics and the basin depth (see -4#3 above). The jetty collector vapour
  sizing (see the screening above).
- Electrical: the new P-05 / P-06 instruments AI-5126 / AI-6126 and ZSC-5101 / ZSC-6101 are
  cabled (JB-A4-1 / -2). The electrical, hvac and layout-detail gates are ok. The bays' delivery
  hardstanding is outside every zone.
- Consistency with the P&IDs at HEAD: the model is current after the P-05 / P-06 changes of
  709fcf20 (`cheme diff c0554145 709fcf20 --list`: instruments only). Every line is routed, and
  the operators name existing valves (0 `layout-operator-unknown`).
- The lifting study and laydowns are unchanged except the model hash. D-5101 / D-6101 "lane
  blocked" are accepted with spool removal.

## Not checked
- The area classification itself (CSA C22.1 / IEC 60079-10-1, competent person). Every zone is
  the ASSUMED screening table, and no Ex selection may rest on it.
- The LNG spill siting study (CSA Z276 / NFPA 59A thermal radiation and vapour dispersion
  exclusion zones, cited by number only) for the troughs, the basin, the trays, the sump, the
  buildings and the marine transfer area. It includes the rupture of a welded riser or trestle
  run, which D-018 gives to that study. My screenings are order-of-magnitude checks, not that
  study. Competent person.
- The civil drainage design and the real terrain under the trough profile. Civil engineer.
- The mooring layout, the berthing approach, the boat landing on A7, the W2 walkway and the
  piled structures (deck, catwalk, sump deck, collectors under the deck), with the deck level
  above HAT (#10). Marine engineer and the TERMPOL review.
- Crane selection, load charts, ground bearing, outrigger loads on the platform deck (#9) and
  the in-tank pump lift plan. Crane contractor, structural engineer and pump vendor.
- Pipe stress, the loop design and surge loads; the structural design of racks, towers, PR8,
  the trestle and the jetty structures. Stress and structural engineers.
- Fire protection: foam, fire water, deluge, PFP and cable fire resistance (#2, #3, #5). Fire
  protection engineer.
- Cable sizing, the UPS and its distribution (#8), the transformer bay design, B-SUB room sizing
  and the 69 kV route. Electrical engineer. HVAC sizing and the intake gas detection (#6). HVAC
  engineer.
- Every one of the 181 pinned routes vertex by vertex. I read the tank roofs, the riser racks and
  towers, the PR1 junction, the trough route, the basin and PR8, the BOG area, the platform, the
  trestle north end, A7 and A9.
- The estimate and the MTO (the civil quantities of D-033.8 (d) are not in them, as stated).
- The HAZOP (17 `hazop-input-changed` warnings) and the design review gate: outside this scope.
