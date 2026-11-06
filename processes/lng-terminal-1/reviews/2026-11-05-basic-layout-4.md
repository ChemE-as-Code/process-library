---
topic: layout
reviewed_commit: 79d5c7ad
scope: [layout/, piping/routing.yaml, piping/pipe-specs.yaml, electrical/]
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: layout (3D model, routing, buildings, zones, electrical) after the response D-031

Scope: `layout/` (site plan, buildings, structures, placement, zones, hvac, the generated
`layout/plant-model.yaml`, the lifting study), `piping/routing.yaml`, `piping/pipe-specs.yaml`
and `electrical/`. Read as basis, not reviewed: `DESIGN.md` D-001 to D-031 (mainly D-013,
D-016, D-018, D-027, D-029, D-031), the `accept:` block of `checks/checks.yaml`, the equipment
list, the P-08 sheet note on the sumps, and the adversarial check of the previous round
(`build/adversarial-layout-r5.json`). I did not write this layout.

**Commit.** HEAD `79d5c7ad` ("response to design review 5 and layout review 3 with their
adversarial checks") on `stage/lng-terminal-1-concept`, clean working tree. The round is
f5d925f6 (response D-028 / D-029), 94e503de (HAZOP revised), 262683b4 (review records design-5
and layout-3) and 79d5c7ad (the response: D-030, D-031 and edits to D-016, D-018, D-023,
D-026, D-028, D-029; 39 files changed against 262683b4, among them `layout/zones.yaml`,
`site-plan.yaml`, `structures.yaml`, `equipment-placement.yaml`, `electrical-list.yaml`, the
lifting study, the MTO and the accepts).

**Verdict.** The response closes the high of 2026-11-05-basic-layout-3 (#1, the jetty trough
under the muster point) and both highs of its adversarial check on model evidence. The muster
point and the boat route are now 101 m / 113 m from the jetty sump edge (0.6 / 0.5 kW/m2 with
the tilt allowance). The open tank-area troughs are 34.8 m from both shells and 63 m from both
riser towers, and my own line-source integration reproduces every D-031 number (7.0 / 5.3 / 4.8
/ 3.4 / 3.5 kW/m2). The six-box ship envelopes bound the stated hulls. Five more findings of
review 3 are closed, one is accepted, and three stay open (all medium). The fresh pass finds one
new high (#1). The re-route puts the collection beside the shells and under the riser towers
into enclosed channels. D-031 sizes those channels for the liquid only and leaves the vapour
open, but the NFPA 59A provision it relies on also requires sizing for the vapour formed. By my
screening, the drawn 0.6 x 1.3 m section cannot pass that vapour. So the safeguard that answers
the previous high is not shown to work. The pass also finds five new medium and three new low
findings. The layout is **not ready to issue for basic engineering** while #1 is open. A merge
is pending and should wait until #1 is closed.

## Findings
| id | area | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-layout-4#1 | A1 riser racks PR5 / PR6, A4 platform (layout/zones.yaml, D-018, D-031.1 / .2) | Z-KC-CHANNEL-PR6, Z-KC-CHANNEL-PR5, Z-KC-CHANNEL-JETTY / -W / -E, S-RT2101 / S-RT3101, T-2101 / T-3101 | The collection beside the shells and under the riser towers is now a covered, sealed channel, 0.6 x 1.3 m (box z -1.3-0), about 100 m long, with a single vent at its downstream end into the open PR1 trough. D-031 justifies it with the NFPA 59A provision for enclosed drainage channels (cited by number). That provision requires the channel to be sized for the expected liquid flow and also for the expected vapour formation. D-031 sizes the liquid only: 1.67 m3/s runs ~1.0 m deep at 2.9 m/s (I confirm this by Manning, n 0.013, 1 % fall). That leaves 0.2-0.3 m, about 0.18 m2, of vapour space, and D-031 calls the vapour formation and the vent arrangement "open". My screening, ASSUMED: LNG boils on the warm concrete. A conduction-limited flux of about 20-50 kW/m2, averaged over the first minute, acts on ~2.6 m of wetted perimeter over ~80-100 m. That forms ~10-20 kg/s of cold vapour, ~5-11 m3/s at ~1.8 kg/m3. Through 0.18 m2 this is ~30-60 m/s, and the pressure drop over the channel reaches several kPa, about the weight of a 0.2 m cover slab. The channel cannot pass this vapour to its downstream vent. It must take the spill in through open inlets at the riser drops, so the vapour and the liquid pushed back by it leave there: beside the shell (12.6 m) and under S-RT2101 / S-RT3101, the critical area the channel exists to clear. Covers could also lift there. Z-ESC-A2N passes 14 m east of those inlets. The jetty collectors (1.0 x 1.2 m, ~75 m, vented only at the catwalk) are less marginal at about 11 m/s, but they too are unsized for vapour. This is the safeguard that answers 2026-11-05-basic-layout-3 #2 (raised to high by its adversarial check). As drawn and recorded it is not shown to work, so the high exposure at the shell and the riser tower is not yet closed. The deferral is of a dimension that the basic layout sets (the keep-clear section), not of a detail. | high | open | Record a vapour-formation screening for each enclosed channel in D-031.1: heat flux basis, vapour rate, vapour space and the vent area and positions. Then size the section from it, for example a larger vapour space or a wider channel, with vents only where they discharge outside the critical area. Or replace the enclosed channels with open troughs routed away from the shells and towers (the inlets at the drops then become open sumps that drain away), and screen them as the other legs. Model the inlets and vents as release sources. |
| 2026-11-05-basic-layout-4#2 | A1 / A2 / A6 (layout/zones.yaml, site-plan.yaml separations) | Z-KC-TROUGH-PR1 / -PR2 / -PR3, B-SUB, Z-KC-TX-BAYS, roads R3 / R6 / R7 / R2 | Every tank-area spill now converges at the PR1 / PR2 / PR3 junction and runs 220 m north under PR3 / PR4 in an open trough. That trough is 69.7 m from B-SUB (the occupied control room) and 69.7 m from the oil-filled transformer bays, a non-Ex ignition source (my box distances). D-018 keeps 150 m from the basin to B-SUB "for the cold vapour cloud until the dispersion study". The open trough carries the same 1,000 m3 design spill, and its wetted area (~684 m x 2.6 m) boils off more vapour than the 201 m2 basin. Yet it is held only to the 50 m radiation separation. My own screening, ASSUMED: a ground-level line source of ~0.05-0.1 kg/(m s) in F stability at 2 m/s gives roughly 50-100 % of the LFL at 70 m. So the occupied building and its transformer bays may lie inside the dispersion distance that the design's own interim basis exists to protect. The troughs are also still keep-clear volumes and not release sources. This was the proposed action of 2026-11-05-basic-layout-3 #2 and it is not done. So the culvert crossings of R6, R7 and R2 (vehicles), R3 / R8 traffic and the trays over the troughs are never checked against a zone. B-ANA stands 8.2 m from the PR2 trough. | medium | open | Apply the D-018 vapour basis to the open troughs as well as to the basin. Either keep B-SUB and the transformer bays at the 150 m interim distance from every open trough leg, or record why 70 m is acceptable (a dispersion screening of the trough line source, intake gas detection with a damper trip, the building's ignition control) until the siting study. Declare the open troughs and culverts as secondary release sources (zone 2 at grade) as the sumps are, so that roads, trays and buildings are checked against them. |
| 2026-11-05-basic-layout-4#3 | A1 / A8 spill collection (layout/zones.yaml, D-018, D-031.1) | Z-KC-TROUGH-PR1 / -PR3 / -SUMP / -SUMP-N, T-8101 | The gravity path from PR1's west end (x 760) to the basin is ~684 m: 335 m on PR1, 220 m on PR3 / PR4, 110 m west, 19 m north. D-031 sizes the 0.6 m section at a 1 % fall, which over that length is a 6.8 m drop. The basin pit is 6 m deep, so the trough would reach it below its floor. At half that fall the 0.6 x 1.2 m trough runs full at ~1.5 m3/s, below the 1.67 m3/s design flow. In the model every leg is 1.2 m deep throughout (section `build/layout-section-x1095_crop-2860--10-3200-40.png`), and D-031 leaves the fall to "the terrain, civil detail", with z = 0 everywhere (D-013). The trough was also narrowed from 1.6 m to 0.6 m on the centreline of 14 m racks. A release at a rack edge 7 m off the centreline, at a 7 / 10 m tier, lands on grade, and nothing records the paved, kerbed catchment falling to the trough. The arrangement is therefore not shown to be drainable as drawn. | medium | open | Record a longitudinal profile (invert levels at the junction, the culverts and the basin inlet) against the basin depth, and the section and fall that carry 1.67 m3/s with freeboard. Deepen the basin inlet or the basin if needed. Record the paved catchment under PR1 / PR2 / PR3 / PR4 that falls to the trough. |
| 2026-11-05-basic-layout-4#4 | A1 / A2 / A6 roads and fire access (site-plan.yaml, D-018, D-031.1 residuals) | R1, R3, R5, R6, R7, R8, R2; PR1 / PR3 / PR4 / PR7 steel and trays | D-031 states as a residual that the roads beside the trough legs lie inside the 8 kW/m2 band and that "a trough fire is approached from the other roads of the ring". My integration of the open legs (x 1.2 tilt) gives: R3 12-17 kW/m2 along its whole length, R8 12.7 at its junction with R3, R1 32.5 at its east end, R7 and R2 above 200 at their culverts. For the PR3 / PR4 leg no other road exists. Its west side is the BOG area, and its east side is R3, which is itself in the band. R8 off R3 is the only road to B-SUB. So a trough fire there cuts the control building's road access and leaves the fire brigade no approach below the D-018 criterion for fire roads. Nothing records fire protection for the open troughs (high-expansion foam is noted only for the sumps). The fire protection of the rack steel and the tray tiers of PR1 / PR3 / PR4, which stand directly over an open LNG trough, is not recorded either. PR3 / PR7 carry every power and instrument cable out of B-SUB. | medium | open | Correct the residual in D-031.1: name the approach to each trough leg (or add one, for example a road on the west side of PR3 / PR4, or a second access to B-SUB from the east or south). Record the trough fire protection (foam, or covered sections with fire stops) and the passive fire protection of the rack steel and the B-SUB tray route over the troughs, ASSUMED until the fire protection design. |
| 2026-11-05-basic-layout-4#5 | A4 loading platform (layout/zones.yaml Z-ESC-A4N, Z-ESC-A4-SEA, D-027, D-031.3) | Z-ESC-A4N, Z-ESC-A4-SEA, road R5, LA-5104, Z-HA-MANIFOLD-B2, Berth 2 hull | The move clears the sump, but it puts both ways off the platform at the same corner. The first way is the trestle road R5, starting at (1141, 925). The second is the muster point, life rafts and boat ladder at x 1130.5-1137, y 913.5-924.5. Both then run beside the same trestle: the boat route Z-ESC-A4-SEA is 0.7-1.4 m off the trestle road's edge for 145 m. D-027 placed the second way off "remote from the trestle end". A fire at the platform's north end or the trestle end (the PR2 landing with the DN 800 / 750 lines), or a vapour cloud drifting north from the Berth 2 manifold, now blocks both. A trestle rupture over the water near the platform spills onto the boat route (the marine transfer case left to the siting study). The muster point is screened only against the sump fire, at 1.6 kW/m2. It is 17.5 m from the liquid arm LA-5104, 11.5 m from the Berth 2 manifold zone 1 and 10.3 m from the Berth 2 hull, which are the release points of the event that makes people muster. The boat lane runs 4.6 m off the Berth 2 hull for ~120 m to the stern, where the stern and breast lines are (mooring not modelled). | medium | open | Keep the north-west muster point as the assembly point beside R5. Add escape-to-sea stations (life rafts and ladders) at the south-west and south-east corners: by my screening the south-west corner is 54.5 m from the sump centre, ~2.2 kW/m2 incl. tilt, below the 5 kW/m2 escape value. Then the second way off no longer starts where the first one does. Screen the muster point against an arm / manifold release (a jet or flash fire at LA-5104 or the ship manifold, ASSUMED rate), or record it as a temporary refuge with a water curtain. Have the marine engineer confirm the boat lane against the mooring line layout. |
| 2026-11-05-basic-layout-4#6 | A6 (layout/zones.yaml Z-KC-TX-BAYS, building.yaml, site-plan.yaml roads) | TR-1 / TR-2 bays, B-SUB door S1, road R8 | The bays (x 1165-1195, y 2920-2945) now lie south of B-SUB. The only roads near them are R8 along B-SUB's north side and R3, which is 45 m west. No road, hardstanding or lifting lane reaches the bays for delivering or replacing a 10 MVA oil-filled transformer (tens of tonnes, ASSUMED) or for fighting a transformer fire. The bays are not in the equipment list, so the lifting rule cannot see them. The building's escape door S1 is on the south wall at x ~1180, 10 m from the bays. During a transformer fire, the building is left with only its north doors N1 / N2. | medium | open | Give the bays a road and a hardstanding from R3 or R8 (for example a spur along A6's west or south side), with a transformer delivery lane. Move S1 to the west wall, or record that the fire wall on the building side shields it. Add the bays' access to D-031.9. |
| 2026-11-05-basic-layout-4#7 | screening statements (layout/zones.yaml, D-031, P-08 note, equipment list) | Z-ESC-A2N-W, Z-KC-TROUGH-JETTY, T-8101 / Z-HA-SUMP-T8101, P-08 note | Three statements do not match the calculation or the model. (a) The Z-ESC-A2N-W basis says "5 kW/m2 or less (incl. x 1.2 tilt) along it". D-031 itself, and my integration, give 5.6 kW/m2 at its east end (1032, 3015), above the escape criterion, on the only A2 exit that no trough blocks. (b) D-031.2 and the Z-KC-TROUGH-JETTY basis give "below 1 kW/m2 at both carriers" for the catwalk trough. Side-on at 24.0 m (Z-SHIP-B1-4) and 28.5 m (Z-SHIP-B2-5), the 39 m line source gives 4.3 and 3.2 kW/m2 incl. tilt. That is still below 8, and the declared 17 m separations hold. (c) The P-08 note ("tank area and trestle troughs"), the T-8101 service and the Z-HA-SUMP-T8101 title still name trestle troughs, which D-018 / D-031.5 removed. | low | open | Start Z-ESC-A2N-W farther west (or shield its first metres) so that the route meets 5 kW/m2 incl. tilt, or state the exceedance. Correct the catwalk trough figures. Align the P-08 note and the T-8101 texts with D-018 (design owner for P-08). |
| 2026-11-05-basic-layout-4#8 | A1 pump removal (accept `layout-lifting:P-2101[A-D]`, D-031.7) | P-2101B / D, P-2101A, P-2102 | The SIMOPS basis says the far pumps are lifted "along the deck's north-south axis between the pump rows, never over a running pump's head". The column heads stand in two north-south rows at x 941 (A, B) and x 953 (C, D), and the axis between them, x 947, holds the circulation pump P-2102 at (947, 3040). P-2102 runs in holding, when a maintenance lift would be made. The radial line from B (941, 3020) to the crane on Z-PAD-T2101N passes ~2.6 m from A's head and ~1.6 m from P-2102's. So the stated path is not clear of running pumps. | low | open | State the lift path that the geometry allows (pumps on the path stopped and isolated, or a slew sequence that keeps the load off P-2102 and the running pump heads) in D-031.7 and the accept. |
| 2026-11-05-basic-layout-4#9 | A9 sump deck (layout/structures.yaml S-CW-A9) | S-CW-A9, A9, TSL-8104 | The sump deck is a dead end. Its only way back is the 39 m catwalk, which carries the open spill trough on its centreline (section `build/layout-section-x1163.5_crop-790--15-935-45.png`). A9 has no ladder to the water and no life-saving station. The catwalk ladders run "from grade" to a 0.3 m walkway, which is an artefact of modelling a piled catwalk as a grade structure. The TSL-8104 field cable runs on the catwalk handrail beside the open trough. A9 is entered only occasionally (portable pump, foam, inspection), and not during a transfer. | low | open | Add an escape ladder and a life ring at A9's south edge, and record in D-031.6 that A9 and the catwalk are kept clear during transfers. Route the TSL-8104 cable on the side away from the trough, or in fire-resistant cable. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-layout#1 | B-PLAT substation inside the 200 m loading-point radius | high | closed e11eb12a | Unchanged at HEAD. B-JET is 206.6 m or more from every arm, and the eight separations give 0 `layout-separation`. |
| 2026-11-05-basic-layout#2 | Road R5 blocked by B-PLAT; no crane access to the platform | high | closed e11eb12a | R9 / R10 unchanged. Lifting study: all eight arms "lane clear". Z-LAY-A4NW is shortened to 6.5 x 10.5 m by the muster point, and still no laydown finding for the arms. |
| 2026-11-05-basic-layout#3 | B-SUB 4 m off PR2 | high | closed e11eb12a | `cheme show B-SUB --layout`: PR3 63.0 m, PR2 63.8 m, PR1 70.1 m, K-7101C 110.8 m. The troughs at 69.7-70.5 m are new matter: #2 of this record. |
| 2026-11-05-basic-layout#4 | Tank-top pump platform missing | high | closed e11eb12a | Level plans `build/layout-level-S-T2101-TOP-PP_crop-875-2975-1010-3110.png`, `-S-T3101-TOP-PP_crop-735-2975-870-3110.png`. |
| 2026-11-05-basic-layout#5 | Roads not one network | medium | closed e11eb12a | Unchanged. The fire-access consequence of the troughs is #4 of this record. |
| 2026-11-05-basic-layout#6 | Safety zone of one berth holds the other carrier | medium | closed e11eb12a | D-027.5 basis unchanged. |
| 2026-11-05-basic-layout#7 | Direct route chains | medium | closed e11eb12a | Report: no `direct`, no `rack+direct`. |
| 2026-11-05-basic-layout#8 | 80 mm insulation on the trestle lines | medium | closed e11eb12a | `pipe-specs.yaml` 200 / 150 mm on LNG-4001 / 4002 and BOG-4001 / 4002. The other lines: 2026-11-05-basic-layout-2#5. |
| 2026-11-05-basic-layout#9 | Span screening classes LNG as gas | medium | open | D-031.14 carries it as open: no report to cheme-as-code is filed. Every free-span finding still reads "gas" (`cheme validate`, 27 free-span / 23 support-missing, each accepted by its own id). |
| 2026-11-05-basic-layout#10 | Wildcard free-span / tray-span accepts | medium | closed e11eb12a | Unchanged, no rule wildcard. See Layout. |
| 2026-11-05-basic-layout#11 | No escape zones | medium | closed e11eb12a | 12 escape zones are declared at HEAD, among them the new Z-ESC-A4N, -A4-SEA, -A2N-W, -A2N. |
| 2026-11-05-basic-layout#12 | No contraction space on the trestle | medium | closed e11eb12a | Z-LOOP-01..12. Sizing: 2026-11-05-basic-layout-2#6. |
| 2026-11-05-basic-layout#13 | Unbuildable generated VP-* platforms | medium | closed e11eb12a | Report: structures declared 7, none generated. |
| 2026-11-05-basic-layout#14 | No DESIGN.md entry for the layout pass | medium | closed e11eb12a | D-027, D-029, D-031. |
| 2026-11-05-basic-layout#15 | B-SUB comment distance | low | closed e11eb12a | 110.8 m measured, as stated. |
| 2026-11-05-basic-layout#16 | Derrick hoist not in D-017 | low | closed e11eb12a | D-027.14. |
| 2026-11-05-basic-layout#17 | Spill containment not in the model | low | closed e11eb12a | Troughs, channels and both sumps are declared. Their adequacy is #1 to #3 of this record. |
| 2026-11-05-basic-layout#18 | Reviewed files uncommitted | low | closed fa3304be | This record names the committed HEAD 79d5c7ad. |
| 2026-11-05-basic-layout-2#1 | In-tank pump removal path ruled out by the model | high | closed f5d925f6 | Pads Z-PAD-Tn101N now 34 x 26 m (D-031.7). Lifting study: P-n101A-D at 61.1-74.7 m radius, 9.24 t needed. |
| 2026-11-05-basic-layout-2#2 | Impoundment sump T-8101 at the riser rack and tank (closure disputed by the adversarial check) | high | closed 79d5c7ad | Basin: `cheme show T-8101 --layout` gives T-2101 117.9 m, R2 56.0 m, PR4 100.0 m, PR3 122.4 m, PR6 123.0 m, all ≥ 49.2 m (tilt), 0 `layout-separation`. The disputed conveyance path no longer runs under PR6 / S-RT2101 as an open trough. Open troughs are 34.8 m from the shells (7.0 / 5.3 kW/m2, my integration). The enclosed channel that replaces it beside the shell is #1 of this record. |
| 2026-11-05-basic-layout-2#3 | No flare radiation basis at B-SUB | medium | open | D-031.14: the derrick owner's contour is still owed. B-SUB 316.0 m from FL-8101, against 314.3 m to the fence. The bays now south of B-SUB are no nearer the flare. |
| 2026-11-05-basic-layout-2#4 | East way out of A2 blocked by BOG-7002 | medium | closed f5d925f6 | Unchanged, `layout-headroom` 0. |
| 2026-11-05-basic-layout-2#5 | DN 800 / 900 LNG lines at 80 mm insulation | medium | open | `piping/pipe-specs.yaml` unchanged in 79d5c7ad. D-031.14 defers it (re-pinning ~30 routes). Rack fill PR1 7 m 46 %, PR4 33 % still understated. |
| 2026-11-05-basic-layout-2#6 | Loop bays unsized, loops not routed | medium | open | Unchanged. D-031.14 leaves it to the stress engineer's loop design. |
| 2026-11-05-basic-layout-2#7 | Family accepts for tray spans and line routes | medium | closed f5d925f6 | Unchanged. The FV / TV patterns are now narrowed too (see 2026-11-05-basic-layout-3#10). |
| 2026-11-05-basic-layout-2#8 | Dome-edge valves out of reach; XV-2123 / XV-3123 differ | medium | open | D-031.13 / .14: the roof nozzle platform is still tank supply and not modelled. The accepts `XV110[6-9]` / `XV[23]123` rest on it. |
| 2026-11-05-basic-layout-2#9 | No zones at the column heads | medium | closed f5d925f6 | Z-HA-Tn101-COLHEADS unchanged. |
| 2026-11-05-basic-layout-2#10 | Oil-filled transformers inside B-SUB; no 69 kV bay or route | medium | open | The bays are re-sited (D-031.9). The B-SUB room sizing and the 69 kV route are still the electrical engineer's (D-031.14). The bays' road access is #6 of this record. |
| 2026-11-05-basic-layout-2#11 | Artefact frame in the take-off | low | closed f5d925f6 | HEA100 row 11.543 t priced at 0 (`estimate/mto.md`). |
| 2026-11-05-basic-layout-2#12 | Roof walkways do not meet the deck | low | closed f5d925f6 | Level plans as above. |
| 2026-11-05-basic-layout-2#13 | PSV / vacuum valve inlet isolations at foot level | low | accepted: locked-open isolations operated only for valve change-out; in-line item placement is not settable in cheme-as-code 1.7.0 (D-029.18); accepted by the author in f5d925f6, this reviewer concurs | Unchanged. The PSVs stay at the crown (D-031.8). |
| 2026-11-05-basic-layout-2#14 | No site wind basis | low | open | D-031.14: no source in the register. The muster point (#5), the PSV exits and the trough vapour (#2) still cannot be checked against the wind. |
| 2026-11-05-basic-layout-2#15 | Drain and KO pump suction valves below deck or grade | low | accepted: model artefact of the in-line item placement of cheme-as-code 1.7.0 (D-029.18); accepted by the author in f5d925f6, this reviewer concurs | Accepts `HV??1[57]` / `HV8106?` unchanged and current. |
| 2026-11-05-basic-layout-3#1 | Jetty spill trough under the muster point and escape-to-sea station | high | closed 79d5c7ad | Z-ESC-A4S is removed. The collectors run under the deck along the faces and the south edge (Z-KC-CHANNEL-JETTY / -W / -E), and the open trough runs on the catwalk (x 1163.2-1163.8, y 816-855). The new muster point Z-ESC-A4N is 100.9 m from the sump edge (0.6 kW/m2 incl. tilt, my calculation; separation 60 m met). Plan `build/layout-plan_crop-1080-790-1240-1080.png`, sections `build/layout-section-x1163.5_crop-790--15-935-45.png`, `build/layout-section-y919_crop-1040--15-1250-45.png`. The new location's own defect is #5. |
| 2026-11-05-basic-layout-3#2 | Tank-area trough under PR6 and S-RT2101, 11.8 m from the shell | medium | superseded by 2026-11-05-basic-layout-4#1 | The open collector is re-routed under PR1 / PR3 / PR4 (34.8 m from both shells, 63 m from both towers; separations ≥ 32 m met). Under PR5 / PR6 the collection is an enclosed channel whose vapour sizing is #1 (high, as the adversarial check rated this item). The undeclared zones on the troughs from its proposed action are #2. |
| 2026-11-05-basic-layout-3#3 | Trestle drainage concept (2 km uphill tray) | medium | closed 79d5c7ad | D-018 / D-031.5: no tray on the welded trestle run. The shore end drains to the PR2 trough and the platform to T-8102. A rupture over the water is the siting study's marine case. T-8102 holds ~200 m3 against ~33 m3. |
| 2026-11-05-basic-layout-3#4 | T-8102 without level, water removal or access | medium | open | The access part is done: catwalk S-CW-A9 (x 1161-1166, y 824-855, 6.8 t HEB200 in the MTO), with TSL-8104 cabled along it to JB-A4-2 (cable schedule 73.4 m). The level transmitter, the high alarm and the fixed water removal are still open on P-08 (D-031.6). The rain margin of ~170 m3 (T-8102 notes) has no rainfall basis. |
| 2026-11-05-basic-layout-3#5 | Sump siting criteria not conservative (muster value, flame tilt) | medium | closed 79d5c7ad | The muster point takes 1.6 kW/m2 and every sump limit carries x 1.2 (D-018). I checked: 8 / 5 / 1.6 kW/m2 at 28.6 / 36.2 / 64.0 m from the T-8102 centre and 57.2 m for the basin. Measured: muster 100.9 m, boat route 113.0 m, Z-SHIP-B2-5 24.8 m, Z-SHIP-B1-5 26.2 m, Z-SHIP-B1-4 27.3 m from the sump edge (≥ 24.6 m). 0 `layout-separation`. |
| 2026-11-05-basic-layout-3#6 | Pump removal: hook height, pad size, stair, lift over live plant, bearing | medium | closed 79d5c7ad | (a) The ~70 m hook is recorded (D-031.7, accept). (b) Pad 34 x 26 m, its west edge 8.6 m east of S-ESC-T2101 (x 931.4), with the stair foot outside. (d) 250 kPa ASSUMED. The lift-over-live-plant basis of (c) does not fit the pump layout, and is raised again as #8. |
| 2026-11-05-basic-layout-3#7 | Both roof exits beside the PSV outlets | medium | open | D-031.8 checked: 12.7 kg/s x 50 MJ/kg x 0.2 = 127 MW radiated. Heskestad gives L = 0.235 x 635,000^0.4 ≈ 49 m, centred ~87 m up, so 8.7-10.1 kW/m2 at the exits and 6-7 at the east edge (my point-source check). The argument holds: an ignited relief exposes the whole deck, so an east exit alone would not lower the exposure. The real safeguard is clearing the roof on the tank high-pressure alarm, which D-031 states but nothing in the alarm or operating basis records. The east way off waits for the roof nozzle platform. Open, medium, honestly stated. |
| 2026-11-05-basic-layout-3#8 | Transformer bays facing the AHU-1 intake | medium | closed 79d5c7ad | Z-KC-TX-BAYS is at x 1165-1195, y 2920-2945, 10 m south of B-SUB (separation met). LV1 (east wall, y ~2967.5) is ~22 m away and does not face the bays. A6 is extended to y 2918. Their access and the south door are #6. |
| 2026-11-05-basic-layout-3#9 | Riser towers: clearance to the tank, members at the drops, 13 m posts | medium | open | (c) is fixed: L58 on both towers, with RS-Tn101-LNGn001 / -LNGn002 now 1.4-1.7 m posts on it (structures.yaml, section `build/layout-section-y3030_crop-870--5-1110-75.png`). (b) is a 15 % allowance (`estimate/rates.yaml` steel-riser-tower, 329.7 t HEB500). (a) is unchanged: 0.6 m (levels) and 1.0 m (columns) to the outer tank, left to the tank contractor. |
| 2026-11-05-basic-layout-3#10 | Accept reasons that do not match the model; FL-8101 lifting row | low | accepted: (a)-(c) fixed in 79d5c7ad (pump trays on roof stools, the A2 / A3 feeders stated as trays in the model, FV / TV narrowed to FV-4101 / FV-4102 / TV-7103); (d) the FL-8101 row cannot be marked as an unplanned lift in cheme-as-code 1.7.0 and the stack is maintained by the derrick hoist (D-027.14, D-031.11); accepted by the author in 79d5c7ad, this reviewer concurs | `checks/checks.yaml` lines 326-327, 415-426. 0 `accept-unused` / `accept-stale`. |
| 2026-11-05-basic-layout-3#11 | A2 east escape route across the crane pad | low | closed 79d5c7ad | D-031.12 and the Z-ESC-A2E basis record the lift-time ways out (A2S and the new A2N, under permit). |
| 2026-11-05-basic-layout-3#12 | No zones at the dome-edge nozzles and manholes | low | closed 79d5c7ad | Z-HA-T2101-DOMEEDGE / -T3101-DOMEEDGE from N1 / N2 / N3 / N8 (level plans). The manholes are not model items and go with 2026-11-05-basic-layout-2#8. |

Adversarial-check items raised against 2026-11-05-basic-layout-3 (`build/adversarial-layout-r5.json`), judged on the model:
- **Escape to sea through the sump's radiation (missed high):** answered. The muster point
  Z-ESC-A4N is at the north-west corner, and the boat route Z-ESC-A4-SEA (x 1123.5-1133, y
  925-1070, z -12 to -9.8) runs north between the trestle and the Berth 2 hull. They are
  100.9 m and 113.0 m from the T-8102 edge: 0.60 and 0.48 kW/m2 incl. tilt (point source,
  my calculation). The new location's defects are #5.
- **Tank-area trough under PR6 and S-RT2101 (missed high, and the disputed closure of
  2026-11-05-basic-layout-2#2):** the open collector now runs under PR1 / PR3 / PR4 and is
  ≥ 34.8 m from the shells. Under PR5 / PR6 the collection is an enclosed channel. The open
  part is answered. The enclosed part is not shown to work: #1 (high).
- **Berth 2 ship envelope (note):** answered. I sampled each hull (centre (1095.5, 887) /
  (1215.1, 887), heading 173.5 deg, 315 x 55 m) on a 1 m grid, 17,696 points per hull. Every
  point lies inside its six boxes (two points on a box edge at the boxes' 0.1 m rounding). The
  hulls are 3.16 m / 3.08 m off the platform, 27.6 m / 28.3 m from the sump edge, and 10.3 m
  (Berth 2) from the muster point.

## Line-source screening of D-031 (my check)
- Input: q' = chi_r x m'' x dHc x w = 0.35 x 0.078 kg/(m2 s) x 50 MJ/kg x 0.6 m = 0.819 MW/m
  radiated. D-031 gives 0.82, correct. The point-source kernel 1/(4 pi r2) is integrated along
  the axis of each open leg (Z-KC-TROUGH-PR1 / -PR2 / -PR3 / -SUMP / -SUMP-N), all legs
  burning, x 1.2 tilt. The infinite-line limit is q = 1.2 q'/(4 d): 8 kW/m2 at 30.7 m and
  5 kW/m2 at 49.1 m. D-031's 32 m and 50 m are conservative roundings.
- Results, my value against D-031: T-2101 shell 7.03 (7.0), T-3101 5.34 (5.3), S-RT2101 4.8
  (4.8), S-RT3101 3.4 (3.4), B-SUB 3.5 (3.5), transformer bays 3.4 (not stated), Z-PAD-T2101N
  3.3 and Z-LAY-T2101N 3.5 (3.3-3.8), Z-ESC-A2N-W 5.6 at (1032, 3015) (5.6), Z-ESC-A2N 4.5
  (4.5). Not stated in D-031: K-7101C 11.2, Z-PAD-A2E 21, B-ANA 27.6, R3 16.6, R8 12.7,
  R1 32.5 (#4).
- Plausibility: a 0.6 m wide LNG fire is ~2.8 m tall (Thomas correlation, m'' 0.078). As a
  vertical strip of ~150 kW/m2 seen side-on at 34.8 m it gives ~6 kW/m2, which agrees with the
  line source. The method is adequate for screening at these distances.
- Catwalk trough: D-6101 4.5 kW/m2 at its centre (D-031: 6.1 to its footprint, conservative),
  D-5101 3.2, LA-6101 2.0, LA-5101 1.3. Carriers 3.2-4.3, not "below 1" (#7).

## Drawing
Not part of this layout review. No P&ID was reviewed, and the P&IDs serve only as the source of
the model. For reference, the `cheme validate` count lines at HEAD are all 0. The accepted ones
are P-04 `0 line-crossing (+2 accepted)`, P-07 `(+2 accepted)` and P-08 `(+1 accepted)`.

## Layout
Commands run at HEAD 79d5c7ad, from the plant folder, with core 1.7.0:
- `cheme layout build --check`: `layout/plant-model.yaml is up to date`.
- `cheme validate`: `86 file(s): 0 error(s), 25 warning(s)`. All 25 warnings are
  `hazop-input-changed` (outside this scope). Every layout model finding is info with its
  accept reason. There is no `accept-unused`, no `accept-stale` and no `review-*`.
- `cheme check --stage detail`: ok for layout-plot-plan, layout-3d, lifting-study, mto,
  layout-detail, electrical, hvac, control-complete, datasheets, the issues gates and the
  on-sheet gates. FAIL design-review (design-5 names f5d925f6, with files changed since;
  outside this scope). FAIL layout-review (layout-3 names f5d925f6, with layout files changed
  since): this record, at 79d5c7ad, replaces it.
- `cheme diff main --list`: 1,062 lines, all P&ID and BFD/PFD items on the branch. The layout
  files are not in the item diff.

`cheme layout report`:
- Lines: every line is routed, none is skipped, and 0 are unrouted.
- Chains per method: astar 45, astar_coarse 3, open 8, pinned 181, rack 9, via 9. There are
  no `direct` and no `rack+direct` chains.
- Chains per reason: pinned 181; local pipe-way 21; local above the pipe-way 10; intent via 9;
  local short run 9; open end 8; local pump run at grade 4; rack battery limit at a rack end
  4; rack longer than local_max_m 4; local rack run too short 3; local no rack in reach 1;
  rack crosses a road 1. Battery-limit ends: rule 16, rack end 1.
- Rack fill: PR1 7 m 46 % / 10 m 27 %; PR2 31 % / 26 %; PR3 10 % / 24 %; PR4 7 m 33 %;
  PR5 12 m 16 % / 14 m 6 %; PR6 21 % / 10 %; PR8 7 m 4 %. PR1 and PR4 are understated
  (2026-11-05-basic-layout-2#5).
- Model findings per rule, all accepted: operability 54, tray-span 37, free-span 27,
  support-missing 23 (info), tray-zone 14, lifting 12, tier 4, tray-separation 3,
  escape-ways 2, escape-travel 2, laydown 2, clash-pipe-steel 1. These are 0: the other
  clash-* rules, headroom, access-blocked, zone-crossing, separation, spacing,
  building-spacing, wall-penetration, vent-outlet, access-enclosed / -unconnected,
  ladder-clearance, walkway-riser, landing-width, egress-zone, operator-unknown, pad-overlap,
  zone-source, support-stub, steel-in-way and pipe-disconnected. Zero means only that nothing
  declared was hit. No rule checks the vapour capacity of an enclosed channel (#1), the
  remoteness of two ways off from each other (#5), road access to an outdoor transformer bay
  (#6), or a trough as a release source against buildings and roads (#2). These rules are
  missing from cheme-as-code.
- Objects: equipment declared 35, inline generated 198, pipes generated 127 / pinned 181,
  structures declared 7 (the new catwalk S-CW-A9, with no generated VP-*), zones declared 85.

Accepts in `checks/checks.yaml` (layout rules), my view of each group. Each names its items, or
a pattern limited to named tags, and none is a rule wildcard:
- `lifting:T-[23]101`, `laydown:laydown-T-[23]101`, `lifting:D-5101` / `D-6101`: real and
  current (72.6 m quoted, which matches the study).
- `lifting:P-[23]101[A-D]`: real, with the hook of ~70 m now stated. The SIMOPS path does not
  fit the pump layout (#8).
- `operability`: XV110[23], XV111[1-5], XV41??, XV7121?, the ERS pattern, PV1110, PV1111,
  PV8132, FO*, FV410[12], TV7103: real class or item reasons. `XV110[6-9]` / `XV[23]123`
  rest on the unmodelled roof nozzle platform (2026-11-05-basic-layout-2#8).
  `HV??1[57]` / `HV8106?`: accepted (#15 of review 2).
- `line-route` (8), `tier` (2 entries, 4 findings), `clash-pipe-steel` (1): real.
- Free spans (27) and support-missing (23): one per finding or a pattern limited to named
  lines, each with a location and a reason. The quoted lengths are current. Three reasons
  (LNG-4008, N-8001, BOG-1011) still say a post would stand "in the spill trough". The
  keep-clear volumes they mean (the PR6 channel and the narrowed PR1 trough) are still there,
  so the reasons still hold.
- `escape-ways` / `escape-travel`: real (a tool limitation); #7 of review 3 applies.
- `tray-separation` (2), `tray-zone` (5 entries, 14 findings): real.
- `tray-span`: per-tray reasons, now matching the model (trays in the model, buried in
  detail). `*-PR?-PR?` is limited to the joint link trays.

Rendered and read (all under the plant folder, `build/`):
- `build/layout-plan.png`: the whole site.
- `build/layout-plan_crop-700-2860-1220-3240.png`: both tanks, the open trough along PR1, the
  enclosed channels under PR5 / PR6 (x 846 / 988), the collector under PR3 / PR4 at x 1095
  past R7 and R2, the west leg at y 3165 into the basin, the enlarged pads and the moved
  laydowns north of the tanks, Z-ESC-A2N, A6 with B-SUB and the bays.
- `build/layout-plan_crop-990-2925-1210-3130.png`: the BOG area with Z-ESC-A2S across the PR1
  trough, Z-ESC-A2E to R7, Z-ESC-A2N-W / -A2N to R2, the junction, R3 / R8, B-SUB, and the
  bays south of it with no road to them (#4, #6).
- `build/layout-level-S-T2101-TOP-PP_crop-875-2975-1010-3110.png` and
  `build/layout-level-S-T3101-TOP-PP_crop-735-2975-870-3110.png`: the pump decks, the PSV
  zone 1 at the west edge between the exits (review 3 #7), the new dome-edge zones at N1 / N2 /
  N3 / N8, the pads 8.6 m east of the stair towers, and no tray on the deck.
- `build/layout-section-y3030_crop-870--5-1110-75.png`: tank to the riser tower and PR3. The
  header at ~60 m on the new L58, the DN 800 drop to PR6 at 12-14 m, the tower's east stair,
  A2N beside it, and PR3 with the trough at x 1095.
- `build/layout-section-x988_crop-2930--10-3230-62.png`: along PR6 and S-RT2101 to the
  basin. The enclosed channel at grade y 2945-3046 under the drops, the levels L22-L58, the
  laydown, R2, and the trough's last leg into T-8101 (#1).
- `build/layout-section-x1095_crop-2860--10-3200-40.png`: along the re-routed collector. The
  trough at a constant 1.2 m depth from y 2872 to 3165, under PR2, PR7, PR6, the PR3 / PR4
  corner and PR8 (#3).
- `build/layout-section-x1163.5_crop-790--15-935-45.png`: the jetty head and A9. T-8102 pit,
  the catwalk walkway at +0.3 m over the trough (y 824-855), the enclosed collector under the
  south edge, D-6101 and the PR2 end tiers (#9).
- `build/layout-section-y919_crop-1040--15-1250-45.png` and
  `build/layout-plan_crop-1080-790-1240-1080.png`: the new muster box at x 1130.5-1137 beside
  the Berth 2 hull envelope and the PR2 end, the boat route between the hull boxes and the
  trestle road, the six-box envelopes on both sides, and the catwalk to A9 (#5).
- `build/layout-section-y3017_crop-960--3-1130-25.png`: the BOG area. PR6 with the channel at
  x 988, the A2N-W route at 0-2.2 m clear of steel, the K-7101A package with its seal zone, and
  PR3 with the trough.

Measured (`cheme show <tag> --layout`, or my box distances from the declared zones): T-8102 to
D-6101 50.6 m, D-5101 51.4 m, LA-6101 60.9 m, PR2 74.3 m, R10 85.0 m, S-CW-A9 8.0 m, B-JET
289.9 m. T-8101 to T-2101 117.9 m, R2 56.0 m, PR8 7.1 m, PR4 100.0 m, PR6 123.0 m. T-2101 to
S-RT2101 0.6 m, S-ESC-T2101 0.4 m, PR6 5.6 m, PR1 27.8 m, R1 45.8 m, R2 46.2 m. B-SUB to R8
2.0 m, R3 45.1 m, PR3 63.0 m, PR2 63.8 m, PR1 70.1 m, K-7101C 110.8 m. Troughs: PR1 trough to
both shells 34.8 m, PR3 trough to B-SUB and to the bays 69.7 m, PR2 trough to B-ANA 8.2 m.
Muster point Z-ESC-A4N to Z-HA-MANIFOLD-B2 11.5 m, LA-5104 17.5 m, Z-LAY-A4NW 1.0 m, the
Berth 2 hull 10.3 m. Boat route to the Berth 2 hull 4.6 m.

## Checked and fine
- Site geometry against D-013 and the task basis. T-2101 (929.4, 3025.8) to LA-5102 (1137,
  884) is 2,152 m at 174.5 deg (D-013: 2,147 m at 174 deg, "about 2.1 km"). T-2101 to FL-8101
  (1484.9, 3102.8) is 561 m at 82 deg ("about 560 m east"). D-031 changed neither.
- The point-source screening of both sumps with the x 1.2 tilt (28.6 / 36.2 / 64.0 m for
  T-8102, 57.2 m for T-8101). Every separation in `site-plan.yaml` holds, with 0
  `layout-separation`.
- The Manning sizing of D-031 for the liquid alone: 1.0 m deep at 2.9 m/s, 1.74 m3/s, in the
  0.6 m channel at 1 %.
- The ship envelopes (see the adversarial items). T-8102 moved 2.5 m east onto the
  centreline of the water between the hulls.
- The pump removal pads and laydowns: clear of the stair towers, the riser towers, the
  channel and A2N, with the boom assembly on R2 under permit recorded.
- The riser tower top level L58 and the short posts. The north bay is widened so that the
  north-west column clears BOG-1001.
- Electrical: JB-A8-1 moved 17 m west of the trough's last leg, outside the basin zone. The
  TSL-8104 cable runs on the catwalk (73.4 m). The four new P&ID switches ZSC-2123 / 3123 and
  ZSO-5122 / 6122 are cabled. B-SUB's LV1 does not face the bays, and LV2 (exhaust) does.
- Ignition sources near the berths: B-JET stays ≥ 206.6 m from every arm. A9 and the catwalk
  hold no electrical equipment other than TSL-8104 and its cable.
- Consistency with the P&IDs at HEAD: the model is current after the P-02 / P-03 / P-05 /
  P-06 changes of 79d5c7ad, every line is routed, and the operators name existing valves (0
  `layout-operator-unknown`).
- MTO: catwalk 6.8 t HEB200 and riser towers 329.7 t HEB500 (`estimate/mto.md`). The 15 %
  allowance is applied to that row only.

## Not checked
- The area classification itself (CSA C22.1 / IEC 60079-10-1, competent person). Every zone
  is the ASSUMED screening table, and no Ex selection may rest on it.
- The LNG spill siting study (CSA Z276 / NFPA 59A thermal radiation and vapour dispersion
  exclusion zones, cited by number only) for both sumps, the open troughs, the enclosed
  channels, the buildings and the marine transfer area. My dispersion and vapour-formation
  estimates (#1, #2) are order-of-magnitude screenings, not that study. Competent person.
- The civil drainage design: terrain, trough profile, culverts, paving falls (#3). Civil
  engineer.
- The mooring layout (S-09 is not modelled), the berthing approach, and the rescue boat lane
  beside the hull (#5). Marine engineer and the TERMPOL review.
- Crane selection, load charts, ground bearing and the in-tank pump lift plan. Crane
  contractor and pump vendor.
- Pipe stress, riser guides and anchors, the loop design, surge loads. Piping stress
  engineer. Structural design of the riser towers, racks, PR8, the trestle, the catwalk and
  the A9 deck. Structural and marine engineers.
- Fire protection (foam, fire water, passive protection of the rack steel and trays over the
  troughs, #4). Fire protection engineer.
- Cable sizing and voltage drop, the transformer bay design, B-SUB room sizing, the 69 kV
  route. Electrical engineer. HVAC sizing and the intake gas detection. HVAC engineer.
- The estimate beyond the two steel rows named above.
- Every one of the 181 pinned routes vertex by vertex. I read the tank roofs, the riser
  drops, the north apron, the trough route, the basin, the BOG area, the jetty head and A9.
- The HAZOP (25 `hazop-input-changed` warnings) and the design review gates: outside this
  scope.
