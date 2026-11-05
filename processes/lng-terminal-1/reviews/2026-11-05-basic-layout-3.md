---
topic: layout
reviewed_commit: f5d925f6b9112898b43cde87311ec7d6dde48dd5
scope: [layout/, piping/routing.yaml, piping/pipe-specs.yaml, electrical/]
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: layout (3D model, routing, buildings, zones, electrical) after the response D-029

Scope: `layout/` (site plan, buildings, structures, placement, zones, hvac, the generated
`layout/plant-model.yaml`, the lifting study), `piping/routing.yaml`, `piping/pipe-specs.yaml`
and `electrical/`. Read as basis, not reviewed: `DESIGN.md` D-001 to D-029 (mainly D-013,
D-016, D-018, D-027, D-029), the `accept:` block of `checks/checks.yaml`, the equipment list,
the line list, the P-08 sheet note on T-8102, the HAZOP H-05 actions on the sumps, and the
adversarial check of the previous round (`build/adversarial-layout.json`). I did not write
this layout.

**Commit.** HEAD `f5d925f6` ("response to design review 4 and layout review 2 with their
adversarial checks") on `stage/lng-terminal-1-concept`, clean working tree. The round is
54648679 (core 1.7.0 regeneration), a00658de (review records design-4 and layout-2) and
f5d925f6 (the response: D-028, D-029 and edits to D-016, D-018, D-020, D-023, D-025, D-026,
D-027; 40 files changed against a00658de).

**Verdict.** The response closes both highs of 2026-11-05-basic-layout-2 on model evidence.
The in-tank pumps now have a feasible removal concept: a mobile crane on a pad north of each
tank, at 61-73 m radius. The basin T-8101 is 117.9 m from the T-2101 shell and at least 100 m
from every rack. It also answers the two missed highs of the adversarial check: there are
riser towers S-RT2101 / S-RT3101, and T-8102 is moved off the platform. The other answers
close or accept five more earlier findings, and seven earlier findings stay open, all medium
or low. The fresh pass finds one new high. The covered jetty spill trough that D-029 added
runs under the platform muster point and escape-to-sea station (#1). The jetty sump was sited
30 m from that muster point for this very spill. The pass also finds eight new medium and
three new low findings. The layout is **not ready to issue for basic engineering** while #1
is open. A merge is pending and should wait until #1 is closed.

## Findings
| id | area | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-layout-3#1 | A4 / A9 loading platform and sump deck (layout/zones.yaml) | Z-KC-TROUGH-JETTY, Z-ESC-A4S, T-8102 | The covered spill trough from the platform drip trays to the jetty sump (box x 1160.2-1161.8, y 815-865, z -0.8-0) runs for 8 m under the muster point and escape-to-sea station Z-ESC-A4S (x 1145.5-1166.5, y 855.5-863.5). It leaves the platform at the south edge where the rescue boat ladder goes down to the water (section `build/layout-section-x1161_crop-790--15-935-45.png`, plan `build/layout-plan_crop-1060-720-1260-960.png`). D-018 / D-029 site the sump 30 m or more from the muster point (39.5 m measured) so that a sump fire does not reach the people mustering. But the same spill reaches the sump by flowing in this trough under the muster point. A spill at the arms or manifolds is the event that makes people muster: an arm or flange failure until ESD closure, ~30 s at ~4,000 m3/h (ASSUMED, D-014 / D-016), is ~30 m3 of LNG. During that event the trough gives off cold vapour, which is denser than air. The vapour comes out under the deck and over the water, at the muster point and at the escape-to-sea landing, and an ignited trough burns there. No zone is declared on the trough, so the model sees nothing. This is a safeguard (the muster and the escape to sea) placed on the spill path that it must stay away from. | high | open | Route the jetty trough away from the muster and escape-to-sea station. For example, run it from the drip trays at both faces along the platform's south-east or south-west edge, outside Z-ESC-A4S, and onto the sump deck catwalk. Or move the muster point and the rescue boat landing away from the trough's exit (to a platform corner upwind, once a wind basis exists). Declare a separation from the trough to Z-ESC-A4S, and record it in D-018 / D-029. |
| 2026-11-05-basic-layout-3#2 | A1 tank area (layout/zones.yaml, D-018, D-029.2) | Z-KC-TROUGH-SUMP, PR6, S-RT2101, T-2101, R2 | The re-siting moves the basin away from the tank. The spill now reaches the basin along a ~240 m covered trough (x 987.2-988.8, y 2945.8-3183). It collects the PR1 and the trestle spills at x 988 and runs north under the PR6 centreline and under the riser tower S-RT2101, which carries all of T-2101's roof piping drops. It passes 11.8 m from the T-2101 shell for ~107 m, 9 m from JB-T2101 and 13 m from the pump laydown Z-LAY-T2101N. It then crosses R2 in a culvert (section `build/layout-section-x984_crop-2930--10-3230-62.png`). The D-018 radiation screening covers only the basin. Nothing screens the conveyance path, which carries the same 1,000 m3 design spill past the tank and the riser structure. The troughs are keep-clear volumes, not hazardous zones, although the sumps they feed are zone 2. NFPA 59A treats enclosed drainage channels for LNG specially (cited by number only). A covered trough and a road culvert have to be shown to be sized for the liquid flow and the vapour formation, or they are not allowed. If the trough is not such a channel, a trough fire beside the shell and under the riser tower is the exposure that 2026-11-05-basic-layout-2#2 rated high. | medium | open | Route the collection away from the tank and the riser tower, for example east of PR6 or under PR4 north to A8, so that the trough under PR6 serves only PR6. Otherwise record in D-018 why the PR6 route is acceptable: the trough's enclosure and sizing against NFPA 59A, its fall, the vapour venting of the culvert under R2, and a radiation screening of a trough fire at the shell and at S-RT2101. Declare the troughs as secondary release sources (zone 2) as the sumps are. |
| 2026-11-05-basic-layout-3#3 | PR2 trestle (D-018, layout/zones.yaml Z-KC-TROUGH-PR2) | trestle drip trays, T-8101 | D-018 and Z-KC-TROUGH-PR2 drain the trestle drip trays to T-8101 at the shore end. That makes a gravity path of ~2.4 km: 1.98 km of trestle, then the PR2 and PR1 troughs, then the PR6 trough. D-013 says the real tank area is ~12 m above the jetty deck datum, so the trays would have to drain uphill from the platform end (the model has z = 0 everywhere). Even on level ground, a 2 km open tray with no intermediate collection gives off a vapour cloud along its whole length and reaches the basin late. Nothing in the model or in DESIGN.md shows the fall, the tray section or the collection points of the trestle drainage. | medium | open | State the trestle spill concept in D-018: local drip trays draining to the nearer end (the jetty sump, or collection pits at intervals along the trestle), with the fall that the terrain allows. Size T-8101 / T-8102 for the spill each one actually collects. |
| 2026-11-05-basic-layout-3#4 | A9 sump deck (P-08 note, equipment list T-8102) | T-8102, TSL-8104 | The re-sited jetty sump stands on its own piled deck at sea, 31 m south of the platform. It has only a low-temperature switch TSL-8104. It has no level measurement and no fixed water removal: the P-08 note says "rainwater is removed by a portable pump once TSL-8104 confirms no LNG". The drip trays under both berths' arms and manifolds drain into it, so it collects the rain from that catchment. Nothing alarms when it fills, and the D-018 basis has no rainfall figure. A rain-filled sump loses its spill volume, and LNG on water gives rapid phase transitions and an overflow onto the sea between the moored carriers. The catwalk that a portable pump, foam and an inspection would need is only described ("along the sump deck catwalk"). No structure or walkway reaches A9 in the model. HAZOP H-05 proposes the same action (A12, status proposed). | medium | open | Give T-8102 a level transmitter with a high alarm and a fixed water removal that is interlocked off on low temperature (as P-8102 / I-801 for the basin), with its discharge route. Or record a covered sump with a rain-shed basis. Model the catwalk from the platform to A9 as a structure with its access, and route the sump's cables to JB-A4-2 on it. |
| 2026-11-05-basic-layout-3#5 | D-018 sump siting basis (layout/site-plan.yaml separations) | T-8102 to Z-ESC-A4S, Z-SHIP-B1/B2, LA-n101/n104; T-8101 to B-SUB | The screening limits are ASSUMED and are to be replaced by the CSA Z276 / NFPA 59A siting study, as recorded. Two points of the interim basis are not conservative. (a) The muster point is given the 5 kW/m2 escape-route value. A muster point is where people stay, and the usual criterion is about 1.6 kW/m2 for continuous exposure (API 521 practice). By the D-018 point source, the muster point at ~43.5 m from the sump centre sees ~2.9 kW/m2, and 1.6 kW/m2 needs ~58 m. (b) The point source ignores flame tilt. A solid-flame check of the 8 m sump fire is about 10-20 % above it at ~30 m. The jetty sump margins are 1-3 m: 24.0-25.7 m measured against the 23 m minimum to both carriers. | medium | open | Use a continuous-exposure criterion for the muster point (or move it, which also serves #1). Screen the jetty sump with a tilted solid flame at the design wind, and keep a margin on the carrier separations until the siting study replaces the screening. |
| 2026-11-05-basic-layout-3#6 | A1 pump removal (layout/zones.yaml Z-PAD-Tn101N, lifting study, accept `layout-lifting:P-[23]101[A-D]`) | Z-PAD-T2101N / -T3101N, S-ESC-T2101 / -T3101, LNG-2001 / LNG-3001 | The concept is feasible in principle, but the model understates or omits what the crane needs. (a) The hook height is taken from the 2 m column-head plate (P-2101A `height: 2.0`), so the study gives 65.8-66.5 m. The pump being pulled is ~6 m long (Z-LAY-T2101N basis), which puts the hook at ~70 m above the 60.8-61.5 m lift height. (b) The pad is 24 x 22 m. It has to take a large luffing-jib crawler at 61-73 m radius and ~70 m hook, its superlift tail swing and its boom assembly. The apron is 42 m deep, with no assembly area. The escape stair tower S-ESC-T2101 (the second way off the roof) stands 4.6 m west of the pad, with its stair and foot on the pad side. (c) The far pumps (P-n101B/D, 73 m) are lifted over the live pump header LNG-2001 S1-S4 and the column-head piping of the running pumps. The accept says this, but no lift-path restriction or SIMOPS basis is recorded. (d) There is no ground bearing basis, although the pad is 10 m off the tank's foundation. | medium | open | Give the pump's real length to the lifting study (or a lift-height override) and quote the hook height. Enlarge the pad, or declare the crane's assembly and superlift area clear of S-ESC-Tn and its foot. Keep the stair exit outside the crane's exclusion zone. Record in D-029.1 the lift-over-live-plant basis (header in service, load path, drop protection) and the pad's bearing, ASSUMED until the crane contractor. |
| 2026-11-05-basic-layout-3#7 | A1 tank roofs (layout/zones.yaml Z-ESC-Tn-ROOF-*, accept `layout-escape-*:S-T[23]101-TOP/PP`) | S-T2101-TOP / S-T3101-TOP, PSV-n131A-C outlets | Both ways off the pump platform leave from its west edge. The SE walkway enters at the south-west corner (930.5, 3016.5) and the N walkway at the north-west corner (930.5-931, 3043-3044). The three tank PSV outlets are at (932.4-938.4, 3032.8, 62.6 m) on that same edge, 10-15 m from both exits in plan and ~5 m above the deck. The column heads where people work are at x 941-953 (level plans `build/layout-level-S-T2101-TOP-PP_crop-875-2975-1000-3110.png`, `-S-T3101-TOP-PP_crop-735-2975-860-3110.png`). On a relief to atmosphere, which is the overpressure case that sends people off the roof, and above all if it is ignited, every way out passes near the outlets. The east side, towards the riser tower, has no way off. The north walkway joins the deck over only a 1 m length of its west edge. | medium | open | Move the PSVs and vacuum valves to the deck edge opposite the exits, or add a way off the deck's east side that is remote from them: for example a walkway down the dome to the riser tower top level L46 and its stairs. Quote the radiation of an ignited PSV release at the exits (ASSUMED relief rate) in D-027.7. |
| 2026-11-05-basic-layout-3#8 | A6 (layout/building.yaml, layout/hvac.yaml, layout/zones.yaml) | B-SUB LV1 / AHU-1, Z-KC-TX-BAYS (TR-1 / TR-2) | The new outdoor bays for the two oil-filled 10 MVA transformers and the 69 kV incomer (x 1203-1223) stand 8 m east of B-SUB's east wall (x 1195). That wall holds LV1, the only outdoor-air intake of the occupied control room's AHU-1. LV1 was turned east "away from the plant" before the bays existed. A transformer fire or oil fire then sends its smoke into the control room's air supply. The bays also lie outside A6, about 290 m from the flare derrick, nearer than the 314 m fence line that the B-SUB separation uses. Nothing measures them. | medium | open | Move LV1 to a wall away from the bays, or move the bays north or south of the building. Give the intake smoke and gas detection with a damper trip (detail). Add a separation from the bays to B-SUB's intake with its basis, and extend A6 over the bays. |
| 2026-11-05-basic-layout-3#9 | A1 riser towers (layout/structures.yaml S-RT2101 / S-RT3101) | S-RT2101, S-RT3101, RS-Tn101-*, T-2101 / T-3101 | The towers answer the missed high, but three points remain. (a) The tower stands 0.6 m (levels) and 1.0 m (columns at y 3019.5) off the concrete outer tank (`cheme show T-2101 --layout`: S-RT2101 0.6 m). This leaves no room for the tank's base slab edge, its wall buttresses or wall-mounted items, its inspection access or the differential settlement between the tank and the tower. (b) The tower's y grid was chosen clear of the drops (notes: grid at y 3008 / 3019.5 / 3034.6 / 3044, drops at 3012.3 / 3017.8 / 3030.9 / 3039 / 3042). So no member stands at any DN 800 / 900 / 750 drop. The guides and the vertical support of a ~46 m cryogenic riser are not shown, and the DN 800 drop at x ~985 is mid-bay (section `build/layout-section-y3030_crop-870--5-1110-75.png`). (c) The tower stops at 46 m while the roof runs cross at 59-60 m, so the header supports RS-Tn101-LNG2001 / -LNG2002 are 13.4-13.7 m posts on the top beam. | medium | open | Agree the tower's clearance to the outer tank with the tank contractor (foundation, buttresses, settlement) and move the tower east if needed. Add the guide and riser-support members at the drops (or record them as secondary steel with a tonnage allowance). Extend the tower to the roof crossing level instead of the 13 m posts. |
| 2026-11-05-basic-layout-3#10 | checks/checks.yaml accepts, lifting study | accepts `layout-tray-span:PT-M-P-[23]10[12]*`, `PT-M-K-7101[ABC]`, `IT-JB-K7101`, `PT-M-P-8101[AB]`, `IT-JB-A3-1`, `layout-operability:P-0?/FV*`, `P-0?/TV*`; FL-8101 row of the lifting study | Some accept reasons describe an arrangement that the model does not show. (a) The in-tank pump trays rise at x 981.98 / 975.48 from 17 m to 56.5 m, 10.5 m above the tower top, and then run 15-21 m at 56.5 m over the dome edge to the deck edge at x 961 (`plant-model.yaml` PT-M-P-2101A-D, PT-M-P-2102). The accept says they are "hung from the platform deck steel", but the deck ends at x 961. (b) The A2 / A3 feeders are accepted as "buried duct bank", while the model, the cable schedule lengths and the MTO carry trays at 18 m / 15.5 m. (c) `P-0?/FV*` and `P-0?/TV*` still accept any future FV or TV valve on any sheet. (d) The lifting study lists a 92.4 t lift of FL-8101 at 129 m hook from Z-PAD-A3 with "lane clear". D-029.1 says this is not the method, yet the row is what makes the gate pass for the stack. | low | open | Give the pump trays steel (the extended riser tower of #9, roof stools as for the piping) and say so in the accept. Record a buried route for the A2 / A3 feeders in the electrical list or in the take-off notes. Narrow FV / TV to the present tags. Accept the FL-8101 row with its reason (the derrick hoist, D-027.14) instead of letting a lift that nobody plans close the item. |
| 2026-11-05-basic-layout-3#11 | A2 (layout/zones.yaml) | Z-ESC-A2E, Z-PAD-A2E | The new east escape route (x 1058-1083, y 2993-2997) runs across the crane pad Z-PAD-A2E (x 1062-1082, y 2988-3012) (plan `build/layout-plan_crop-1005-2930-1125-3065.png`). During a compressor lift the first way out of A2 lies inside the crane's outrigger and exclusion area, which leaves only Z-ESC-A2S under PR1. | low | open | Route Z-ESC-A2E along the pad's north or south edge outside the outrigger footprint, or record the lift-time escape arrangement (A2S only, permit) in D-029.10. |
| 2026-11-05-basic-layout-3#12 | A1 tank roofs (layout/zones.yaml) | XV-1106..1109, XV-2123 dome-edge nozzles, roof manholes | The roof zones of D-029.15 cover only the column heads (1 m). The flanged fill, bottom-fill and circulation valves and nozzles at the dome edge (r ~40 m, 51-52 m), and the roof manholes, are release sources of the same grade and have no zone. This is the remaining part of the proposed action of 2026-11-05-basic-layout-2#9. The roof nozzle platform those valves will need (#8 of review 2) will stand in an unclassified area in the model. | low | open | Declare zones from sources at the dome-edge nozzles and manholes (table row flange / valve, ASSUMED) together with the roof nozzle platform. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-layout#9 | Span screening classes LNG as gas | medium | open | D-027.10 / D-029.8 now record the condition as open: no report to cheme-as-code is filed, so the conditional acceptance of 2026-11-05-basic-layout-2 has lapsed. Every span finding still reads "gas" (`cheme validate`). The 27 free-span and 23 support-missing accepts are each by id with their own reasons, so none relies silently on the gas class. But LNG runs between the liquid and the gas span (for DN 800 roughly 9-10 m against 12.8 m, by weight ratio) are not reported at all. Proposed: file the report, or re-screen the LNG runs off the racks as liquid by a recorded calculation. |
| 2026-11-05-basic-layout-2#1 | In-tank pump removal path ruled out by the model | high | closed f5d925f6 | The gantry crane is dropped. Mobile crane pads Z-PAD-T2101N / -T3101N (24 x 22 m) north of each tank, reached from R2, `crane_reach_m: 80`. Lifting study: P-n101A-D at 61.2-73.3 m radius, 9.24 t needed, laydown Z-LAY-Tn101N (12 x 14 m). The 12 t pump-and-reel row is stated as 18.48 t needed. The concept is feasible for a large luffing-jib crawler; what the model still understates is #6 of this record. |
| 2026-11-05-basic-layout-2#2 | Impoundment sump T-8101 at the riser rack and tank | high | closed f5d925f6 | T-8101 at (980, 3190) in A8: 117.9 m from T-2101, 100.0 m from PR4, 122.4 m from PR3, 123.0 m from PR6, 173.7 m from PR5, 56.0 m from R2, 265.6 m from A6 (`cheme show T-8101 --layout`). Separations 45 m / 150 m declared, 0 `layout-separation`. The pool fire screening (D-018) is checked: 274 MW radiated, 8 kW/m2 at 52.2 m and 5 kW/m2 at 66.1 m from the centre. The conveyance trough is #2 of this record. |
| 2026-11-05-basic-layout-2#3 | No flare radiation basis at B-SUB | medium | open | A separation B-SUB to FL-8101 ≥ 314 m is added (316.0 m measured). It restates the fence-line distance and does not measure the radiation. The derrick owner's contour of all four flares is still owed (D-029.9 "Open"). The new transformer bays are nearer the derrick still (#8). |
| 2026-11-05-basic-layout-2#4 | East way out of A2 blocked by BOG-7002 at head height | medium | closed f5d925f6 | BOG-7002 is pinned at 2.6 m (routing.yaml via [1059.5, 3011.5 / 2981.5, 2.6]). Escape zone Z-ESC-A2E is declared, and `layout-headroom` is 0. Section `build/layout-section-y2995_crop-1005--2-1125-20.png` shows the route clear at 0-2.2 m. The route crosses the crane pad: #11 of this record. |
| 2026-11-05-basic-layout-2#5 | DN 800 / 900 LNG lines at 80 mm insulation | medium | open | `piping/pipe-specs.yaml` is unchanged: `cold (PIR)` is 80 mm for every line other than LNG-4001 / 4002 and BOG-4001 / 4002. D-029.11 defers it to the insulation specification. The rack fill (PR1 7 m 46 %, PR4 33 %) is still understated. |
| 2026-11-05-basic-layout-2#6 | Loop bays unsized, loops not routed | medium | open | D-029.12 screening checked: L = sqrt(3 x 195 GPa x 0.813 m x 0.22 m / 170 MPa) = 24.8 m. The bays are 26 m x 20 m (zones Z-LOOP-01..12). That covers the innermost loop only: three nested DN 750 / 800 loops with 150-200 mm insulation add roughly 5 m. The lines are still not routed through the bays, so the ~2.4 km and the elbows are missing from the MTO. |
| 2026-11-05-basic-layout-2#7 | Family accepts for tray spans and line routes | medium | closed f5d925f6 | One entry per tray (19 tray-span ids or tray-specific patterns) and eight `layout-line-route` ids. No rule wildcard is left, and 0 `accept-unused` / `accept-stale`. The reasons that do not match the model are #10 of this record. |
| 2026-11-05-basic-layout-2#8 | Dome-edge fill and circulation valves out of reach; XV-2123 / XV-3123 differ | medium | open | D-029.14 "Open". The roof nozzle platform is not modelled, and the `XV110[6-9]` / `XV[23]123` accepts rest on it. The asymmetry is a P&ID matter: P-02 and P-03 put the valve on different segments, against D-015's identical trains. |
| 2026-11-05-basic-layout-2#9 | No zones at the column heads and vents | medium | closed f5d925f6 | Z-HA-T2101-COLHEADS / Z-HA-T3101-COLHEADS (zone 2, 56-59 m) are declared. The 10 pump-tray ends inside them are accepted with Ex glands (`layout-tray-zone` 14). The dome-edge nozzles and manholes are split off as #12 of this record. |
| 2026-11-05-basic-layout-2#10 | Oil-filled transformers inside B-SUB; no 69 kV bay or route | medium | open | Z-KC-TX-BAYS (20 x 30 m) is reserved east of B-SUB and the TR-1 / TR-2 notes are corrected. The room-list sizing of B-SUB and the 69 kV route are still open (D-029.16 "partly open"). The bays' siting against the AHU-1 intake is #8 of this record. |
| 2026-11-05-basic-layout-2#11 | Artefact frame in the take-off | low | closed f5d925f6 | The frame is HEA100: own MTO row 11.543 t (691.2 m, `estimate/mto.md`), priced at 0 in `estimate/rates.yaml` (`steel-tank-top-artefact`). The structures note is corrected. |
| 2026-11-05-basic-layout-2#12 | Roof walkways do not meet the deck or the landing | low | closed f5d925f6 | ROOF-SE x 918-931.5 / y 3010-3017.5 overlaps the deck's south-west corner. ROOF-N x 927.8-931 / y 3043-3073 overlaps the deck's west edge over 1 m and reaches the 42.2 m landing of S-ESC-T2101 (y 3072.2). Same on T-3101 (level plans). The siting of both exits on the PSV side is #7 of this record. |
| 2026-11-05-basic-layout-2#13 | PSV / vacuum valve inlet isolations at foot level | low | accepted: locked-open isolations operated only for valve change-out; cheme-as-code 1.7.0 places in-line items along the route by its own rule and the routing schema cannot set them (D-029.18); the detail piping design lifts the spools. Accepted by the author in f5d925f6; this reviewer concurs | HV-n134x / n135x are still 0.16-0.20 m above the deck; they are within reach, so there is no operability finding. |
| 2026-11-05-basic-layout-2#14 | No site wind basis | low | open | D-029.18: no source is in the register yet. The intakes (#8), the PSV exits (#7) and the muster point (#1, #5) still cannot be checked against the wind. |
| 2026-11-05-basic-layout-2#15 | Drain pump and KO pump suction valves 0.1 m below deck or grade | low | accepted: model artefact of the in-line item placement of cheme-as-code 1.7.0, which the routing schema cannot set (D-029.18); the valves sit at the pump nozzles in the detail piping design. Accepted by the author in f5d925f6; this reviewer concurs | Accepts `layout-operability:P-0[56]/HV??1[57]` and `P-08/HV8106?` are unchanged and current. |

Adversarial-check items raised against 2026-11-05-basic-layout-2 (`build/adversarial-layout.json`), judged on the model:
- **No riser structure for the 36-48 m drops:** answered by S-RT2101 / S-RT3101 (x 976-996.5,
  levels 22 / 30 / 38 / 46 m, stairs and caged ladders), real terminal steel in the take-off.
  The tower exists and carries the roof runs at the dome edge on its 46 m beam. Its clearance
  to the tank, the missing members at the drops and the 13 m posts are #9 of this record.
- **T-8102 siting:** answered. A9 at (1161, 812): 50.6 m from D-6101, 61.3 m from LA-6101,
  74.2 m from PR2, 85.0 m from R10 (`cheme show T-8102 --layout`), and the carrier
  separations hold (0 `layout-separation`). The new defects are the trough under the muster
  point (#1), the water removal and access (#4) and the screening margins (#5).
- **Trays across the pump deck:** answered. No tray crosses the deck in the 57.3-61.3 m level
  plans, and the trays run at 56.5 m under the grating with 56.8 m entries. What carries them
  beyond the deck edge is #10.
- **Escape walkways not connected:** answered (#12 of review 2, closed above). The walkways
  are connected but badly placed: #7.
- **The 66 support-missing notes:** answered. 129 declared posts, T-posts and stubs plus 8
  riser tower posts (`structures.yaml`). Support-missing is now 23 and free-span 27, and each
  is accepted by its own id or by a narrow named pattern with an item-specific reason.
- **Span-rule accept on an unfiled core report:** the condition is not met, so
  2026-11-05-basic-layout#9 is carried as open above. D-029.8 says the same.

## Drawing
Not part of this layout review. No P&ID was reviewed, and the P&IDs serve only as the source of
the model. For reference, the `cheme validate` count lines at HEAD are all 0. The accepted
ones are P-04 `0 line-crossing (+2 accepted)`, P-07 `(+2 accepted)` and P-08 `(+1 accepted)`.

## Layout
Commands run at HEAD f5d925f6, from the plant folder, with core 1.7.0:
- `cheme layout build --check`: `layout/plant-model.yaml is up to date`.
- `cheme validate`: `84 file(s): 0 error(s), 25 warning(s)`. All 25 warnings are
  `hazop-input-changed` (outside this scope). Every layout model finding is info with its
  accept reason. There is no `accept-unused`, no `accept-stale` and no `review-*`.
- `cheme check --stage detail`: ok for layout-plot-plan, layout-3d, lifting-study, mto,
  layout-detail, electrical, hvac, control-complete, datasheets, the issues gates and the
  on-sheet gates. FAIL design-review (design-4 names 54648679, with files changed since;
  outside this scope). FAIL layout-review (layout-2 names 54648679, with layout files changed
  since): this record, at f5d925f6, replaces it.
- `cheme diff main --list`: 1,058 lines, all P&ID and BFD/PFD items on the branch. The layout
  files are not in the item diff.

`cheme layout report`:
- Lines: every line is routed, none is skipped, and 0 are unrouted. New lines: W-8002 (163.2 m
  on PR8) from the basin pump P-8102.
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
  declared was hit. No rule sees a keep-clear trough under an escape zone (#1), an escape
  zone over a crane pad (#11), an intake facing a transformer bay (#8) or a pad beside an
  escape stair (#6). These rules are missing from cheme-as-code.
- Objects: equipment declared 35, inline generated 198, pipes generated 127 / pinned 181,
  structures declared 6 (two tank-top frames, two riser towers, two escape stair towers, with
  no generated VP-*), zones declared 67.

Accepts in `checks/checks.yaml` (layout rules), my view of each group:
- `lifting:T-[23]101`, `laydown:laydown-T-[23]101`: real, item-specific reasons (a
  field-erected tank, whose pump rows are the real lifts).
- `lifting:P-[23]101[A-D]`: real concept, but the quoted ~66 m hook is understated (#6).
- `lifting:D-5101`, `D-6101`: real (only their own inlet spools are in the lane).
- `operability:` XV110[23], XV111[1-5], XV41??, XV7121?, the ERS pattern, PV1110, PV1111,
  PV8132, FO*: real class or item reasons. `XV110[6-9]` / `XV[23]123` rest on the
  unmodelled roof nozzle platform, which is open as 2026-11-05-basic-layout-2#8. `FV*` /
  `TV*` are too wide (#10). `HV??1[57]` / `HV8106?`: accepted (#15 above).
- `line-route`: eight ids, each with its reason. Current.
- Free spans (27) and support-missing (23): one per finding or a pattern limited to named
  lines, each with a location and a reason (corner steel, small bore, crane strip, roof
  stools). The quoted lengths are current (no accept-stale).
- `tier` (2 entries, 4 findings), `clash-pipe-steel` (1): real.
- `escape-ways` / `escape-travel`: real (a tool limitation). The walkways are now connected,
  but #7 applies.
- `tray-separation` (2), `tray-zone` (7 entries, 14 findings): real (cover plates, Ex glands,
  ASSUMED until the classification).
- `tray-span`: per-tray reasons. The pump trays and the A2 / A3 "buried" ones do not match
  the model (#10). The others are real.

Rendered and read (all under the plant folder, `build/`):
- `build/layout-plan.png`: the whole site. The tank area, A8 north of R2, A3 and the flare,
  B-SUB with the transformer bay east of it, the 2 km trestle with the twelve loop bays, B-JET,
  the platform with the 200 m circles, and A9 south of the platform.
- `build/layout-plan_crop-870-2930-1010-3230.png`: T-2101, the north apron with
  Z-PAD-T2101N, Z-LAY-T2101N and S-ESC-T2101 beside the pad, the trough along x 988 from PR1
  under PR6 across the apron and R2 into T-8101, PR8, and P-8102 at the basin edge (#2, #6).
- `build/layout-level-S-T2101-TOP-PP_crop-875-2975-1000-3110.png` and
  `build/layout-level-S-T3101-TOP-PP_crop-735-2975-860-3110.png`: the pump decks, the
  column-head zones, the PSV zone 1 spheres at the deck's west edge between the two walkway
  connections (#7), the walkways overlapping the deck corners, and no tray on the deck.
- `build/layout-section-y3030_crop-870--5-1110-75.png`: tank to the BOG area. The deck at
  57.4 m, the header at 60 m to the drop at x ~985 inside PR6, the riser tower's labelled
  levels L22-L46 with no member in the section at the drop (#9), the east stair, PR6 tiers
  12 / 14 m, PR1 / PR3 beyond.
- `build/layout-section-x984_crop-2930--10-3230-62.png`: north-south through PR6, S-RT2101,
  the apron, R2 and the basin. The riser tower columns at the four grid lines to 46 m, the
  drops between them, the trough at grade along the whole length into the basin, PR8 at 7 m,
  and the basin with its zone 2 (#2).
- `build/layout-section-x1161_crop-790--15-935-45.png` and
  `build/layout-plan_crop-1060-720-1260-960.png`: the jetty head and A9. The Berth 1 arms to
  22 m with the manifold zone, the PR2 end at 7 / 10 m, the drain drum and pump, the muster
  box at the south edge, and the trough under it running 50 m south to T-8102 on its deck
  (#1). The ship envelopes on both sides of A9, 24-26 m off the sump.
- `build/layout-section-y2995_crop-1005--2-1125-20.png` and
  `build/layout-plan_crop-1005-2930-1125-3065.png`: the BOG compressors. Z-ESC-A2E at
  0-2.2 m clear of BOG-7002 (2.6 m) and the FL-700x lines, running over Z-PAD-A2E (#11). The
  seal zones, R7 under PR3, and PR1 with its valve zone to the south.

Measured (`cheme show <tag> --layout`): T-2101 to S-RT2101 0.6 m, S-ESC-T2101 0.4 m, PR6
5.6 m, R1 45.8 m, R2 46.2 m, A8 89.8 m. T-8101 to T-2101 117.9 m, R2 56.0 m, PR4 100.0 m,
PR3 122.4 m, PR6 123.0 m, PR5 173.7 m, PR8 7.1 m, A6 265.6 m. T-8102 to D-6101 50.6 m,
D-5101 51.0 m, LA-6101 61.3 m, PR2 74.2 m, R10 85.0 m, B-JET 289.6 m. B-SUB to K-7101C
110.8 m, B-ANA 84.6 m, PR3 63.0 m, PR2 63.8 m, PR1 70.1 m, R8 2.0 m. FL-8101 to B-SUB
316.0 m, the site boundary 314.3 m, PR3 54.1 m. LA-5102 to B-JET 218.6 m, PR2 9.1 m, R9
15.5 m, A9 59.5 m.

## Checked and fine
- Site geometry against D-013 and the task basis: T-2101 (929.4, 3025.8) to LA-5102 (1137,
  884) is ~2,152 m at ~174.5 deg (D-013: 2,147 m at 174 deg, "about 2.1 km"). T-2101 to
  FL-8101 (1484.9, 3102.8) is ~561 m at ~82 deg (D-013: 561 m at 82 deg, "about 560 m
  east"). D-029 changed neither.
- Pool fire screening arithmetic of D-018 (point source, as stated): basin 784 MW / 274 MW,
  52.2 m and 66.1 m; jetty sump 196 MW / 68.6 MW, 26.1 m and 33.0 m. All the declared
  separations hold, with 0 `layout-separation`.
- Basin services: P-8102 at the pit edge (rainwater, low-temperature interlock per the
  equipment list), W-8002 on PR8 to the PR4 battery limit, and JB-A8-1 outside the basin zone
  (18 m from the centre). Cables to MCC-1 / CR-1 run over PR7 / PR3 / PR4 / PR8 (cable
  schedule).
- BOG area east exit: headroom over Z-ESC-A2E is kept (section y2995), and the south exit
  Z-ESC-A2S is unchanged.
- Tank roofs: no tray crosses the deck, the column-head zones are declared, and the
  column-head valves are reachable with their declared operators (no HV-n15x / n16x
  operability finding).
- Ignition sources near the berths: B-JET stays outside 200 m of all eight arms (218.6 m
  from LA-5102). A9 holds no electrical equipment other than TSL-8104.
- Accepts: no rule wildcard is left, every accept names its items, and the quoted lengths
  are current.
- Consistency with the P&IDs at HEAD: the model is current, every line of the line list is
  routed, the operators name existing valves (0 `layout-operator-unknown`), and the new P-08
  items (P-8102, W-8002, LI-8103, TSL-8102, PZT-8123A-C) are placed and cabled.

## Not checked
- The area classification itself (CSA C22.1 / IEC 60079-10-1, competent person). Every zone
  is the ASSUMED screening table, and no Ex selection may rest on it.
- The LNG spill siting study (CSA Z276 / NFPA 59A thermal radiation and vapour dispersion
  exclusion zones) for both sumps, the troughs, the buildings and the marine transfer area.
  The vapour dispersion of the 1,000 m3 design spill towards the trains (A5, ~430 m) and R2.
  The flare radiation contour at B-SUB and at the transformer bays. All need a competent
  person.
- The mooring layout (S-09 is not modelled): whether the A9 piles and the catwalk conflict
  with the breast and spring line dolphins between the two berths, and the berthing
  approach. Marine engineer.
- Crane selection, load charts, ground bearing of Z-PAD-Tn101N next to the tank foundation,
  and the in-tank pump lift plan: crane contractor and the pump vendor (#6).
- Pipe stress, the riser guides and anchors on S-RTn101, the loop design, and surge loads on
  the trestle and the tank roof piping: piping stress engineer. Structural design of the riser
  towers, the racks, PR8, the trestle and the A9 sump deck: structural and marine engineers.
- Fire protection (fire water, monitors, high-expansion foam at both sumps): not in the
  model.
- Cable sizing and voltage drop: for example the 461 m 400 V feeder to P-8102 on 4C x
  2.5 mm2, the ~2 km 6.6 kV feeders, and the 69 kV route. B-SUB room sizing and the
  transformer bay design. Electrical engineer. HVAC sizing: HVAC engineer.
- The estimate (`estimate/rates.yaml`) beyond the artefact row.
- Every one of the 181 pinned routes vertex by vertex. I read the tank roofs, the riser
  drops, the north apron, the basin, the BOG area, the jetty head and A9.
- The HAZOP (25 `hazop-input-changed` warnings) and the design review gates: outside this
  scope.
