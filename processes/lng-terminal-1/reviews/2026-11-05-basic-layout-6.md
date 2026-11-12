---
topic: layout
reviewed_commit: aedd8dbd
scope: [layout/, piping/routing.yaml, piping/pipe-specs.yaml, electrical/]
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: layout (3D model, routing, buildings, zones, electrical) after the response D-035

Scope: `layout/` (site plan, buildings, structures, placement, zones, hvac, the generated
`layout/plant-model.yaml`, the lifting study), `piping/routing.yaml`, `piping/pipe-specs.yaml`
and `electrical/`. Read as basis, not reviewed: `DESIGN.md` D-001 to D-035 (mainly D-013, D-016,
D-018 (h)-(o), D-034.3, D-035), the `accept:` block of `checks/checks.yaml`, the equipment, line
and instrument lists, the T-8101 / T-8102 / P-8102 datasheets, the P&IDs at HEAD as the source of
the model, and the adversarial check of the previous round (`build/adversarial-layout-r7.json`).
I did not write this layout.

**Commit.** HEAD `aedd8dbd` on `stage/lng-terminal-1-concept`, working tree clean when I started
(`git status --short` empty). The round is 709fcf20 (response D-032 / D-033), fd540b21 (HAZOP
revised), 0bb82928 (review records design-7 and layout-5) and aedd8dbd (the response: D-034 with the
loading hydraulics and the governing spill flows D-034.3, D-035 with the screening
`build/r10_screen.py`, and edits to D-008, D-011, D-013, D-016, D-018, D-023, D-024, D-026, D-032,
D-033). `cheme diff 0bb82928 aedd8dbd --list`: P-04 (LNG-4010, XV-4107 / UZ-4107, tees T4A5 / T4B5,
moved T4A4 / T4B4 and the line A / B ends), P-05 / P-06 (HS-n100A-C, HS-n107A-C, HS-n109,
UY-n135..n138), P-08 (W-8001 removed, P-8102, T-8101 nozzles, LI-8103, TSL-8102), BFD / PFD
streams. The layout files are not in the item diff.

**Verdict.** The response answers most of review 5 on the model: the HPUs and the platform and
PR1 junction boxes are out of the fire bands (my values 6.0 / 5.7 / 6.1 / 5.7 and 5.3 kW/m2), the
BOG compressors have a receptor class and a recorded water spray, the basin has a fire approach
(R12 7.4, Z-LAY-A8W 6.3), the tank-area muster point exists (0.49), the datum is tied to chart
datum, and the governing flows of D-034.3 are carried into the trough (3.22 m at x 975, my Manning
2.92 m at 4.0 m3/s), the basin (2,400 m3 at -7.56 m) and the platform (two outlets per bay, header
bay, 257 m3 sump). My own screening reproduces D-035.9 within 0.1-0.2 kW/m2 at every receptor class
of D-018. For the pool fires, one way off holds 5 kW/m2 for every platform fire, so the disputed
closure of review 4 #5 now holds on model evidence.

The fresh pass finds two highs:
- #1: the header bay, the arrangement at the centre of D-035.1, is not buildable or operable as
  drawn. No steel carries the DN 800 header assembly south of PR9's last bent. The only steel there
  is unreviewed build output standing inside the 3.4 m recess, and the ESD valves, strainers and
  tappings have no access.
- #2: an unisolable leak on the trestle side drains up to ~1,020 m3 per line into a sump with 87 m3
  left. The response itself states that the LNG then leaves over the kerbs onto the deck and the
  water. No safeguard bounds this.

It finds eight mediums:
- #3: the drip pads cannot pass the run-out flow into their gutters, so the burning overflow at
  grade puts R1, the fire approach, at 13-31 kW/m2;
- #4: the B-SUB occupants have no walk to the muster point within 5 kW/m2 and no declared refuge;
- #5: the deck walks;
- #6: the release-point fire and the drift-off pool;
- #7: the T-8102 caisson in the tidal zone;
- #8: the T-8101 shaft;
- #9: the tray detectors;
- #10: the ERS channel A / B common routing.

It also finds four lows. With two highs open, the layout should not be issued for basic engineering
yet. A merge is pending; it is for a human or the reviewer, not the author.

## Findings
| id | area | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-layout-6#1 | A4 header bay (zones.yaml Z-HA-TRAY-HDR, site-plan.yaml PR9, routing.yaml J-Berth1/2-liquid, D-035.1) | LNG-4001 S4-S6, LNG-4002 S4-S6, LNG-5001 S1-S2, LNG-6001 S1-S2, LNG-4010, LNG-4003; XV-5101, XV-6101, SR-5102, SR-6102, XV-4107, XV-4103, PI-4105 / 4106, TI-4103 / 4104, PDI-5102 / 6102; generated VP-XV-4107 | The header bay is not buildable or operable as drawn. (a) Support: PR9's bents stand at y 891.5 / 883 / 874.5 / 866, and the header bay lies at y 857.5-862.3. The model's last supports of the four DN 800 lines are on PR9/bent-4 at y 866 (`build/rev6_hdr_supports.py`). South of it, every line runs with no declared support: the loading lines at 7.6 m (LNG-4001 jogs 4 m east to x 1156.5, LNG-4002 7.5 m east to x 1161.5), the 4.6 m vertical junction drops carrying XV-5101 at 6.1 m and SR-5102 at 5.1 m (and XV-6101 / SR-6102), the returns at 3.0 m and 5.5 m back to y 866, LNG-4010 with XV-4107 and LNG-4003 with XV-4103. That is ~25 m of DN 800 per berth with an ESD valve and a strainer, all over a recess whose floor is at -3.4 m. No rule sees it: the segments are short, so no free-span finding fires. (b) The only steel in the bay is build output. One part is the generated valve access platform VP-XV-4107 (`structures: generated 1`, x 1157-1159, y 859.2-860.4, floor 7.14 m), whose columns and stair foot stand at deck level inside the recess. The other part is generated T-posts of N-8001 / N-8002 / LNG-5006 at (1155.2, 860.3), (1157.4, 860.3) and (1155.6, 862.0), also inside the recess. Both N2 tie-ins cross the bay at 1.5 m (section `build/layout-section-x1158.5_crop-852--4.5-870-9.5.png`). (c) Access: the shore ESD valves (with ZSC-n101, the SIS transfer-state input), the strainers (whose local PDI-n102 must be read, and whose baskets must be pulled at 5.1 m above the deck, 8.5 m above the bay floor) and the DN 25 tappings have no declared access. The accept `layout-operability:P-04/XV41??` says these valves are "maintained from the rack", which is not true for XV-4103 / XV-4107: no rack stands there. The lifting study has no row for the valves or strainers. The arrangement that answers the previous high therefore exists only as pipe centrelines. | high | open | Extend PR9 (or put a portal frame over the bay) with bents outside the recess, and carry the assembly on declared supports that keep their feet out of the bay floor. Declare and review a fixed access platform with a stair, outside the recess, for XV-5101 / XV-6101, SR-5102 / SR-6102, XV-4107, XV-4103, the tappings and the PDIs. Either turn the strainers horizontal or record their removal path and the crane reach from Z-PAD-A4E. Take the N2 tie-ins and their posts out of the bay. Correct the XV41?? accept reason. Rebuild, so that no generated structure is left. |
| 2026-11-05-basic-layout-6#2 | A4 / trestle residual (D-034.3, D-035.1 (d), D-035.14 (a), (g); zones.yaml Z-HA-SUMP-T8102) | LNG-4001 / LNG-4002 (~1,020 / ~1,030 m3), PI-4105 / 4106, TI-4103 / 4104, LNG-5006 / 6006 with CV-n116 / HV-n117, the stem and bonnet seals of XV-4107 / XV-4103 / XV-n101, T-8102 | The leak sources left upstream of XV-n101 cannot be isolated from the platform. They are the DN 25 tappings in the header bay, the drain pump returns, which tee into LNG-4003 on line A / B's side of XV-4103 through flanged check valves and isolation valves in the manifold bays (CV-5116 at (1146.2, 882.5), HV-5117 at (1145.3, 885.6); CV-6116 / HV-6117 likewise), and the valve stem and bonnet seals. After ESD-1 each source drains its whole trestle line, ~1,020 m3, by gravity. The response's own numbers in D-035.14 (g): the sump has 87 m3 left after the 170 m3 spill, a DN 80 leak fills it in ~1 h and a 1 kg/s seal leak in ~11 h, and then "the LNG rises in the catwalk collector ... and leaves over the kerbs onto the deck and the water". The sump has no fixed pump, and its portable pump may run only once TSL-8104 reads no LNG. No safeguard is designed to bound the duration: the N2 displacement back to the tanks is ASSUMED, unsized and timeless, and is left to the design owner. LNG overflowing onto the jetty deck and the water beside two moored carriers, for hours, is a credible event with no safeguard. A deferral that leaves the hazard unanswered is not a medium under the rating standard. The same unbounded duration undercuts the basis of the 60 min PFP rating of PR9 and the PR2 end: D-035.14 (a) bases it on a fire fed for ~60 s and then for minutes. | high | open | Bound the drain-down in the basic design. (a) Move the tappings and the drain pump tie-ins to downstream of XV-n101, or remove them, so that only stem and bonnet seals remain upstream. (b) Define the means and the time to empty an isolated trestle line (for example, N2 displacement from the platform end back to the tanks: N2 rate, pressure, availability and time; or a pump-back route), and put it in D-034.3 / D-016 and the sequences. (c) Size T-8102, the collectors and the PFP duration for the drain-down until that means completes, or have the siting study show that the overflow case is tolerable before issue. |
| 2026-11-05-basic-layout-6#3 | A1 / A2 drip pads at PR1 (zones.yaml Z-HA-CATCH-*, Z-KC-GUTTER-*; D-035.2) | pads XV-4101, XV-4102, XV-4105, XV-4106, XV-1102; gutters XV4101 / XV1102 | D-035.2 checks the gutters' normal depth: 1.54 m at 4.0 m3/s and 0.87 m at 2.10 m3/s. It does not check the step from pad to gutter. A kerbed pad at grade drains into the 0.6 m end of its gutter. A broad-crested weir needs 2.49 m of head to pass 4.0 m3/s through 0.6 m (XV-4101 pad) and 1.62 m to pass 2.10 m3/s (XV-1102 pad). Even the pads that drain straight into the trough need 0.70 / 0.77 / 0.56 m of head along their 4.0 / 3.5 / 5.6 m edges (XV-4102 / XV-4105 / XV-4106). Every pad therefore overflows its kerbs at the D-034.3 flow, and the LNG spreads at grade beside PR1, a burning surface that is not screened. I screened a burning overflow at the XV-4101 pad on top of the design fire, at 50 / 100 / 200 m2 (`build/rev6_screen.py`). It gives R1, the fire approach, 13.2 / 19.2 / 31.1 kW/m2 (criterion 8), R11 9.1 / 12.3 / 18.6, JB-PR1 6.0 / 7.0 / 9.1, and Z-ESC-A2N-W, the way out that no trough fire blocks, 5.8 / 6.8 / 8.7 (criterion 5). | medium | open | Size each pad's inlet for its D-034.3 flow. Options are a grated drop inlet over a pit the full width of the pad, a gutter that runs under the whole pad, or the trough moved under the loading valve station. Alternatively, screen the overflow area as part of the design fire. |
| 2026-11-05-basic-layout-6#4 | A6 / tank-area muster (zones.yaml Z-ESC-A1-MUSTER, D-018 (j), D-035.9) | B-SUB (doors S1, N1 / N2), R11, R1, R8, R3, R2, R4 | D-018 (j) names Z-ESC-A1-MUSTER as the assembly point of A6 too. In the design fire (every open leg, the basin and the worse pad cluster) no walk from B-SUB reaches it within 5 kW/m2. S1 -> R11 -> R1 -> R4 peaks at 6.26 kW/m2 at (1053, 2901), with ~260 m above 5. N1 -> R8 -> R3 -> R2 -> R4 crosses the R2 culvert over the trough, at over 300 kW/m2. The A2 walk (A2N -> R2 west -> R4) does hold: 4.38 at most. No temporary refuge is declared for B-SUB: neither DESIGN.md nor building.yaml nor hvac.yaml uses the word. The building sees 3.1 kW/m2 and has the intake gas trip of D-035.10. | medium | open | Declare B-SUB (or its control room) a temporary refuge for the design fire, with its basis: radiation, gas-tight intake and trip, overpressure, duration and the later evacuation route. Or name a second assembly point east or south of A6 that is reached within 5 kW/m2 (for example on R11 south of the bays), and screen it. |
| 2026-11-05-basic-layout-6#5 | A4 deck walks (D-018 (k), (o), D-035.9, D-035.12) | walks from the arm work positions to the open way: B2-A4, B1-A4, the header bay fire | Remainder of 2026-11-05-basic-layout-5#11. With the D-035 fires I take the walk past the first 10 m, as D-035.14 (e) does (`build/rev6_walks.py`). B2-A4 (the open way is W2, since W1 sees 5.73) gives 11.7 kW/m2 on the walk from the Berth 2 arms to W2 across the north edge. B1-A4 gives 11.0 from the Berth 1 arms to W1. The header bay fire, with its 1.7 kg/s backed-up vapour burnt at a dry arm-bay outlet (D-035.14 (f)), gives 8.4 / 8.5 on the walks from either berth's arms to either way. D-035.9 states 6.2 / 5.9 "over its first ~10 m" for the first two and has no walk row for the header bay. The answer is a residual: the fire protection engineer "considers" a north-edge water curtain, but it is not recorded as a requirement. The adversarial check rated this kind of understatement medium, and review 5 #3 (b) was medium too. | medium | open | Record the water curtain or radiation shielding along the north edge (and at the arm work positions) as an ASSUMED requirement, with its coverage. Or give the work positions a walk that keeps 5 kW/m2 for the fires it serves. Correct the D-035.9 walk rows, with the vapour at the dry outlets. |
| 2026-11-05-basic-layout-6#6 | A4 release-point fire and drift-off pool (D-018 (m), D-035.14 (b), (d)) | platform ways off W1 / W2, HPUs | For pool fires the ways off meet D-018 (e). For the release-point fire they do not. A flash fire at the header rate (~24 kg/s, burnt 415 MW, my point source) gives W1 / W2 47 / 28 kW/m2 at the LA-5104 base, 24 / 41 at LA-6104 and 8.9 / 9.3 at the header bay, for the ~60 s to closure (30 s detection plus the closure time, D-034.3); the muster point sees 0.6-0.8. The drift-off pool (D-035.14 (d)) puts both ways off over 5 for minutes. Carrying both to the siting study, with D-018 (m) stating that "one way off per fire" holds for pool fires only, is an honest deferral and is rated medium. It needs a tracked item, because the 30 s detection time is a design choice that sets the duration. | medium | open | Carry both cases to the siting study as named cases. In the basic design, state whether the arm work positions need a shielded shelter or a shorter detection time (gas or flame detection at the bays, ESD on detection rather than on confirmation), with the basis. |
| 2026-11-05-basic-layout-6#7 | A9 jetty sump and collectors against the tides (D-013, D-035.8, D-035.14 (k); zones.yaml Z-HA-SUMP-T8102, Z-KC-CHANNEL-JETTY*) | T-8102 (bottom -13.0 m = -1.0 m CD), collectors (+8.1 to +10.4 m CD), header bay floor (-3.4 m = +8.6 m CD) | Remainder of 2026-11-05-basic-layout-5#10 once the datum is fixed. T-8102 is now a sealed, anchored caisson whose bottom is 7.7 m below extreme high water. It holds LNG inside a wall with seawater on the other side, which means thermal shock, ice growth and an RPT path if that wall cracks. Empty, it has ~2.2 MN of uplift at EHW (pi x 3^2 x 7.7 m x 10 kN/m3). The collectors and the header bay floor stand inside the surge and wave-crest allowance that sets the deck level. All of this is carried to the marine engineer with a stated rationale, which makes medium the honest rating. The model also draws the tank type's spiral stair down T-8102's outside to -13 m (section `build/layout-section-x1163.5_crop-795--15-935-25.png`), an artefact that also counts in the take-off. | medium | open | Marine engineer: a caisson concept (wall, insulation, anchorage, inspection) or a shallower sump above EHW, with the green-water check of the open bay outlets, before the deck level is fixed. Keep it as a hold in D-035.13. |
| 2026-11-05-basic-layout-6#8 | A8 basin T-8101 (equipment list, zones.yaml Z-HA-SUMP-T8101, P-8102 datasheet, D-034.8, D-035.2) | T-8101 (16 m, 19.5 m deep), P-8102, the pit cover | The bottom of the 19.5 m shaft is at ~-4.2 m CD, ~7.5 m below the mean sea level of S-01, ~370 m from the shore. `process/design-basis.yaml` has no groundwater or geotechnical basis, so the "tanked shaft (civil, ASSUMED)" has no stated ground level to be designed against. Against a groundwater table near grade, the empty shaft carries ~30-40 MN of uplift, and the LNG-cooled walls stand in saturated ground (frost heave). The "pit cover" that carries P-8102's head, LI-8103 and TSL-8102 (equipment list, D-034.8; P-8102 modelled on it at (986, 3232.5)) is not defined. Its extent bears on the open 201 m2 burning surface that is screened, on the high-expansion foam and on any confined vapour space under it. P-8102 is still rated for the 12.5 m pit: the datasheet says "~36 m from the 12.5 m pit floor" and the equipment list notes say the same, ~7 m short of static head (design owner, D-035.12). Deferred to civil with a rationale: medium. | medium | open | Add a groundwater and geotechnical basis (ASSUMED until the site investigation) and the shaft concept (diaphragm wall or caisson, base anchorage, thermal break). Define the cover as a partial grated deck with the open area kept, and state how foam reaches the pit. Re-rate P-8102 for 19.5 m. |
| 2026-11-05-basic-layout-6#9 | A1 / A2 item drip trays (zones.yaml Z-HA-TRAY-XV3123 / -TV7103, D-035.7) | low-temperature detectors in the XV-3123 and TV-7103 trays | Remainder of 2026-11-05-basic-layout-5#2. The holding times are now at LNG density: 22.5 min, and 18.5 min with TV-7103's tray deepened to 0.6 m. PFP is recorded for the near fields. The tray concept, however, rests on detection within 10 min. The detectors and their alarm are still not on P-03 / P-07 at HEAD (the P&ID diff of aedd8dbd does not touch either sheet), and no instrument tag exists. Without them, a leak overflows the tray after 18-22 min, from 11-13 m, onto grade where nothing is collected (a stated residual). | medium | open | Design owner: put the tray low-temperature detectors with their alarm on P-03 / P-07 and in the instrument list, and cable them (JB-T3101 / JB-A2-2). |
| 2026-11-05-basic-layout-6#10 | electrical, ERS supplies (electrical-list.yaml F-ERS-*, cable schedule, D-016, D-032.2, D-034.2) | C-F-ERS-5100A / B, C-F-ERS-6100A / B, PT-PR2-*, the HPU control panels | Channel A and channel B of every ERS valve now have their own UPS. Their feeders share the PR2 power trays (PT-PR2-2..11 in the cable schedule) and end at the same north-corner HPU panel. The electrical list says that separating them "is the electrical engineer's, the model routes both on PR2". D-032.2's residual, both channels lost within the ESD-1 response, rests on "two independent faults". With common routing it becomes one cause: a tray fire or mechanical damage. Losing both channels closes every ERS valve of the berth at full flow before the pumps stop, which D-034.2 puts at ~22.6 barg, above the 15 barg design, and makes it a PSV-n131 relief case. The deferral is stated, so medium. | medium | open | Route channel A and channel B in separate trays (or with a fire barrier) along PR2 and on the platform, to separate panels or terminations, and record this as a requirement of D-032.2. Otherwise re-state the residual as a single-cause case. |
| 2026-11-05-basic-layout-6#11 | A1 PR6 thermal relief (zones.yaml Z-HA-TRAY-PSV1122, pipe-specs.yaml Class 150 (a)) | PSV-1122 on BOG-1010 / LNG-1002; line list notes | Remainder of 2026-11-05-basic-layout-5#1. The pipe class now forbids tappings on PR6 north of y 2952 and puts the DN 25 relief inlets at the PR1 joint. The model keeps PSV-1122's inlet at y 2997 on PR6 (in-line placement is not settable in 1.7.0), held in a 1 x 1 x 0.3 m tray: the drawn plant contradicts its own pipe class (section `build/layout-section-y2997_crop-972--1-1006-19.png`). The line list does not yet carry the welded-run requirement: no "weld" note except on LNG-4010. | low | open | Re-pin BOG-1010's take-off to the PR1 joint when the router allows it, or state the exception in the Class 150 note. Design owner: carry the welded-run note into the line list notes of the lines named in Class 150 (a) / (b). |
| 2026-11-05-basic-layout-6#12 | electrical, jetty-head ESD stations (electrical-list.yaml HS-n100B / HS-n107B, cable schedule) | IC-HS-5100B / 5107B (197 m), IC-HS-6100B / 6107B (239 m) | The jetty-head push buttons at the B-JET north door are cabled to the platform boxes JB-A4-1 / JB-A4-2, 200-240 m south, and from there back to RR-2 in B-JET. The schedule shows no tray for these cables. Because the inputs are normally closed and de-energise-to-trip, a burnt cable trips; but the jetty-head station then depends on the platform box and an untrayed 200 m field cable along the trestle. | low | open | Wire the jetty-head stations to RR-2 (or to a jetty-head box) in B-JET, and route any trestle cable in the PR2 instrument tray. |
| 2026-11-05-basic-layout-6#13 | model and accept hygiene (checks/checks.yaml, plant-model.yaml, site-plan.yaml, zones.yaml) | accepts and texts | (a) Nine `cheme.accept-unused` infos: free-span P-05 DR5006 / BOG5002 and P-06 DR6007 / LNG6007; tier P-04 LNG6006@PR2; clash DR5006+PR2 stringer; tray-zone IT-JB-PR1; tray-span IT-JB-PR1; tray-span PT-M-P-[56] (the last is the truncated id). (b) Stale reasons: `operability:P-04/XV41??` ("maintained from the rack", see #1) and `tray-span:PT-HPU-5100` ("across the platform deck"; the HPU is now at the north-west corner). (c) The covers of D-035.11 span "the 3.25 m bays", but Z-PAD-A4E lies over B1-MAN bays of 6.25 x 4.75 m. (d) The rack-fill report gives PR9's 5 m tier 11 % and no 7 m tier, although four DN 800 lines are pinned on PR9: the report undercounts pinned routes. (e) site-plan.yaml quotes 1.5 kW/m2 at W1 / W2 for the header bay, which holds only with its vapour burnt at the sump; with the backed-up vapour at a dry outlet it is 4.65 / 4.53 (D-035.14 (f); mine 4.68 / 3.65). (f) The tank type's spiral stair is drawn inside T-8101 and on T-8102. (g) The W and B1M collectors straddle bay boundaries (W x 1139.75-1141.25 at the arm / manifold kerb x 1140.5), so a 1.5 x 1.5 m outlet lies only half over its collector: a slot outlet or a moved collector is needed at detail. | low | open | Delete the unused accepts. Correct the two reasons, the cover span, the site-plan comments and the zones basis. Report the PR9 fill and the tank-type stair to cheme-as-code. Note the outlet geometry for detail design. |
| 2026-11-05-basic-layout-6#14 | A4 south-end occupancy rule (D-018 (o), D-035.14 (e); zones.yaml Z-LAY-A4SW / -A4SE notes) | P-5101 / P-6101, the drum bays, the header bay valves and strainers, the south laydowns | The rule that the south end (y < 876) is not a work position while either berth transfers is what keeps every header-fed fire away from people there. My walks from P-5101 / P-6101 to the open way see 25-107 / 8-723 kW/m2 for the bay fires around them. The rule is recorded only in zone notes and in DESIGN.md. No control file holds it: neither `control/sequences.yaml` SEQ-LOAD nor `process/narrative.md` mentions it. It also conflicts with the local strainer indicators PDI-5102 / 6102, which an operator reads during a transfer. | low | open | Put the rule into SEQ-LOAD (a permissive or an operator step) or into the operating philosophy, and transmit PDI-n102 to the control system so that nobody needs to be at the south end during a transfer (design owner). |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-layout#1 | B-PLAT substation inside the 200 m loading-point radius | high | closed e11eb12a | 0 `layout-separation`; T-8102 to B-JET 290.9 m (`cheme show T-8102 --layout`). |
| 2026-11-05-basic-layout#2 | Road R5 blocked by B-PLAT; no crane access to the platform | high | closed e11eb12a | Disputed by the adversarial check. I read the closure as conditional. The roads and the strips exist and all eight arm lifts are "lane clear" in `layout/lifting-study.csv`. The strips stand over the A4W / A4E bays, and the cover design that makes them crane positions is still open as 2026-11-05-basic-layout-5#9 (below). |
| 2026-11-05-basic-layout#3 | B-SUB 4 m off PR2 | high | closed e11eb12a | `cheme show B-SUB --layout`: PR3 63.0, PR2 63.8, PR1 70.1 m. |
| 2026-11-05-basic-layout#4 | Tank-top pump platform missing | high | closed e11eb12a | Level plans `build/layout-level-S-T2101-TOP-PP_crop-875-2975-1010-3110.png`, `build/layout-level-S-T3101-TOP-PP_crop-735-2975-870-3110.png`, unchanged. |
| 2026-11-05-basic-layout#5 | Roads not one network | medium | closed e11eb12a | R11, R12 / R13 join the network. |
| 2026-11-05-basic-layout#6 | Safety zone of one berth holds the other carrier | medium | closed e11eb12a | D-027.5 basis unchanged. |
| 2026-11-05-basic-layout#7 | Direct route chains | medium | closed e11eb12a | Report: no `direct`, no `rack+direct`. |
| 2026-11-05-basic-layout#8 | 80 mm insulation on the trestle lines | medium | closed e11eb12a | LNG-4001 / 4002 at 200 mm in the model. |
| 2026-11-05-basic-layout#9 | Span screening classes LNG as gas | medium | open | Unchanged (pipe-specs.yaml notes). 22 free-span and 36 support-missing, each accepted by id. |
| 2026-11-05-basic-layout#10 | Wildcard free-span / tray-span accepts | medium | closed e11eb12a | No rule wildcard; `*-PR?-PR?` is limited to the joint link trays. |
| 2026-11-05-basic-layout#11 | No escape zones | medium | closed e11eb12a | 16 escape zones, the new Z-ESC-A1-MUSTER among them. |
| 2026-11-05-basic-layout#12 | No contraction space on the trestle | medium | closed e11eb12a | Z-LOOP-01..12 unchanged. Sizing is 2026-11-05-basic-layout-2#6. |
| 2026-11-05-basic-layout#13 | Unbuildable generated VP-* platforms | medium | closed e11eb12a | The VP platforms of that round stay gone. The model again holds one generated structure, VP-XV-4107, inside the header bay: new matter, in #1 of this record. |
| 2026-11-05-basic-layout#14 | No DESIGN.md entry for the layout pass | medium | closed e11eb12a | D-035. |
| 2026-11-05-basic-layout#15 | B-SUB comment distance | low | closed e11eb12a | K-7101C 110.8 m measured. |
| 2026-11-05-basic-layout#16 | Derrick hoist not in D-017 | low | closed e11eb12a | D-027.14. |
| 2026-11-05-basic-layout#17 | Spill containment not in the model | low | closed e11eb12a | Troughs, pads, gutters, trays, bays, the header bay, the collectors and both sumps are declared zones. |
| 2026-11-05-basic-layout#18 | Reviewed files uncommitted | low | closed fa3304be | Clean tree at aedd8dbd. |
| 2026-11-05-basic-layout-2#1 | In-tank pump removal path ruled out by the model | high | closed f5d925f6 | Lifting study: P-n101A-D at 61.1-74.7 m, 9.24 t needed. |
| 2026-11-05-basic-layout-2#2 | Impoundment sump T-8101 at the riser rack and tank | high | superseded by 2026-11-05-basic-layout-4#1 | T-8101 is 166.2 m from T-2101 and 90.0 m from PR4, with 0 `layout-separation`. |
| 2026-11-05-basic-layout-2#3 | No flare radiation basis at B-SUB | medium | open | B-SUB unmoved; the derrick owner's contour is still owed (D-035.13). |
| 2026-11-05-basic-layout-2#4 | East way out of A2 blocked by BOG-7002 | medium | closed f5d925f6 | `layout-headroom` 0. |
| 2026-11-05-basic-layout-2#5 | DN 800 / 900 LNG lines at 80 mm insulation | medium | open | The model has LNG-5001 / LNG-6001 (DN 800 berth headers) and the new DN 800 crossover LNG-4010 at 80 mm. pipe-specs.yaml is unchanged. |
| 2026-11-05-basic-layout-2#6 | Loop bays unsized, loops not routed | medium | open | Unchanged; the stress engineer's. |
| 2026-11-05-basic-layout-2#7 | Family accepts for tray spans and line routes | medium | closed f5d925f6 | Per-tray and per-line entries. |
| 2026-11-05-basic-layout-2#8 | Dome-edge valves out of reach; XV-2123 / XV-3123 differ | medium | open | The roof nozzle platform is still tank supply and not modelled. |
| 2026-11-05-basic-layout-2#9 | No zones at the column heads | medium | closed f5d925f6 | Z-HA-Tn101-COLHEADS in the level plans. |
| 2026-11-05-basic-layout-2#10 | Oil-filled transformers inside B-SUB; no 69 kV bay or route | medium | open | B-SUB room sizing and the 69 kV route are still the electrical engineer's (D-035.13). |
| 2026-11-05-basic-layout-2#11 | Artefact frame in the take-off | low | closed f5d925f6 | Unchanged. |
| 2026-11-05-basic-layout-2#12 | Roof walkways do not meet the deck | low | closed f5d925f6 | Level plans as above. |
| 2026-11-05-basic-layout-2#13 | PSV / vacuum valve inlet isolations at foot level | low | accepted: locked-open isolations operated only for valve change-out; in-line item placement not settable in cheme-as-code 1.7.0 (D-029.18); accepted by the author in f5d925f6, this reviewer concurs | Unchanged. |
| 2026-11-05-basic-layout-2#14 | No site wind basis | low | open | No source; design-basis.yaml has none. |
| 2026-11-05-basic-layout-2#15 | Drain and KO pump suction valves below deck or grade | low | accepted: model artefact of the in-line item placement of cheme-as-code 1.7.0 (D-029.18); accepted by the author in f5d925f6, this reviewer concurs | Accepts `HV??1[57]` / `HV8106?` current. |
| 2026-11-05-basic-layout-3#1 | Jetty spill trough under the muster point and escape-to-sea station | high | closed 79d5c7ad | No open trough on the platform or the catwalk. Muster on A7 at 0.96 kW/m2 with every bay of a berth burning (my value). |
| 2026-11-05-basic-layout-3#2 | Tank-area trough under PR6 and S-RT2101 | medium | superseded by 2026-11-05-basic-layout-4#1 | As in review 5. |
| 2026-11-05-basic-layout-3#3 | Trestle drainage concept | medium | closed 79d5c7ad | No tray on the trestle (D-018). The drain-down of a line onto the platform is new matter (#2). |
| 2026-11-05-basic-layout-3#4 | T-8102 without level, water removal or access | medium | open | Still no level indication or high alarm on P-08. D-035.14 (j) asks the design owner for one: an ~18 h transfer leaves only the 93 mm rain allowance. |
| 2026-11-05-basic-layout-3#5 | Sump siting criteria not conservative | medium | closed 79d5c7ad | Tilt x 1.2 and 1.6 kW/m2 at the muster points, applied in my screening. |
| 2026-11-05-basic-layout-3#6 | Pump removal: hook height, pad size, stair, lift over live plant, bearing | medium | closed 79d5c7ad | Lifting study unchanged for the in-tank pumps. |
| 2026-11-05-basic-layout-3#7 | Both roof exits beside the PSV outlets | medium | open | The roof clearing on high tank pressure is still only in D-031.8. |
| 2026-11-05-basic-layout-3#8 | Transformer bays facing the AHU-1 intake | medium | closed 79d5c7ad | LV1 on the east wall; the bays south of B-SUB. |
| 2026-11-05-basic-layout-3#9 | Riser towers: clearance to the tank, members at the drops, 13 m posts | medium | open | `cheme show T-2101 --layout`: S-RT2101 0.6 m, unchanged; left to the tank contractor. |
| 2026-11-05-basic-layout-3#10 | Accept reasons that do not match the model; FL-8101 lifting row | low | accepted: (a)-(c) fixed in 79d5c7ad; (d) the FL-8101 row cannot be marked as an unplanned lift in cheme-as-code 1.7.0 and the stack is maintained by the derrick hoist (D-027.14, D-031.11); accepted by the author in 79d5c7ad, this reviewer concurs | The new stale reasons are #13 of this record. |
| 2026-11-05-basic-layout-3#11 | A2 east escape route across the crane pad | low | closed 79d5c7ad | D-031.12. |
| 2026-11-05-basic-layout-3#12 | No zones at the dome-edge nozzles and manholes | low | closed 79d5c7ad | Z-HA-Tn101-DOMEEDGE. |
| 2026-11-05-basic-layout-4#1 | Enclosed channels beside the shells not sized for the vapour | high | closed 709fcf20 | No channel under PR5 / PR6 (section `build/layout-section-y2997_crop-870--8-1120-62.png`). |
| 2026-11-05-basic-layout-4#2 | Open troughs not release sources; B-SUB and the bays at 69.7 m | medium | superseded by 2026-11-05-basic-layout-5#6 | As in review 5. |
| 2026-11-05-basic-layout-4#3 | Trough not drainable as drawn (fall, basin depth, catchment) | medium | closed 709fcf20 | Re-sized for D-034.3 in aedd8dbd. My Manning check: 2.92 m at 4.0 m3/s and 1.61 m at 2.10 m3/s, at 0.5 % in 0.6 m. Profile -3.22 / -3.82 / -4.07 / -4.71 / -5.28 / -5.77 m. Basin: 2,400 m3 stands at -7.56 m in the 19.5 m pit (201 m2 x 11.94 m). The pad inlets are new matter (#3). |
| 2026-11-05-basic-layout-4#4 | Roads in the trough band, no fire approach, no fire protection | medium | closed 709fcf20 | R1 7.18, R11 5.87, R8 east 6.93, R2 6.95 / 7.43, R12 7.43 (my screening). |
| 2026-11-05-basic-layout-4#5 | Both ways off the platform at one corner; muster point exposed | medium | closed aedd8dbd | Disputed closure of the adversarial check, now shown for the D-034.3 flows on the model (`build/rev6_screen.py`). Every bay burns with two outlets, the sump and 1.05 kg/s of collector vapour at its worst dry outlet. Best way worst case 4.51 kW/m2 (B2-M7), apart from B2-M8 at 5.24 if every bay is taken as header-fed. B2-M8 holds no LNG item on the model (only the N2 valve HV-5151 over it), so the author's drain-rate vapour applies: about 4.1. Header bay 3.65 (W2), with its 1.7 kg/s vapour at the worst dry outlet. Muster 0.96 with every bay of a berth burning. The release-point fire is excluded by D-018 (m) and tracked as #6. |
| 2026-11-05-basic-layout-4#6 | Transformer bays without road or lane; escape door S1 beside them | medium | closed 709fcf20 | R11 and Z-LAY-TX unchanged; S1 at 2.95 kW/m2 (mine). |
| 2026-11-05-basic-layout-4#7 | Screening statements and texts that do not match | low | superseded by 2026-11-05-basic-layout-5#7 | See review 5 #7 below. |
| 2026-11-05-basic-layout-4#8 | Pump removal path over P-2102 | low | closed aedd8dbd | The accept `lifting:P-2101[A-D]` now says that P-2102, at (947, 3040) on the lift axis, is stopped and isolated for the lift, with holding circulation from P-3102. The model has P-2102 there. |
| 2026-11-05-basic-layout-4#9 | Sump deck A9 a dead end; cable beside the open trough | low | closed aedd8dbd | `layout/structures.yaml` S-CW-A9 notes: escape ladder to the water and life ring at A9's south edge, a marine engineer's item the model cannot draw. TSL-8104 runs beside the enclosed collector. |
| 2026-11-05-basic-layout-5#1 | Welded-run basis not binding; DN 25 reliefs without collection | medium | closed aedd8dbd | pipe-specs.yaml Class 150 (a)-(c) binding; Z-HA-TRAY-PSV1121 / 1122 / 1123 / 4111 / 4113 declared; alone they give 1.1 kW/m2 or less at the receptors (D-035.6). Residual: #11. |
| 2026-11-05-basic-layout-5#2 | Item drip trays: holding times, detection, overflow, near-field fire | medium | superseded by 2026-11-05-basic-layout-6#9 | (a) is corrected at LNG density and (d) has PFP recorded in the zones basis. (b), the detectors, is still not on the P&IDs: #9. |
| 2026-11-05-basic-layout-5#3 | BOG compressors in the design fire's 8 kW/m2 band | medium | closed aedd8dbd | D-018 (i) and the water spray of D-035.3 are recorded. Mine at the package outlines: 7.51 / 8.38 / 10.42 (D-035: 7.4 / 8.3 / 10.3). FL-7002 / FL-7003 are pinned over the trough at 11.4 / 11.6 m (`piping/routing.yaml`). The Z-ESC-A2N-W basis is corrected. |
| 2026-11-05-basic-layout-5#4 | Basin out of reach of any road; PR8 cables; P-8102 at grade | medium | closed aedd8dbd | R12 and Z-LAY-A8W at 7.43 / 6.33 kW/m2 (mine); `cheme show T-8101 --layout`: R13 25.6 m, R12 57.0 m. P-8102 is submersible on the pit cover (P-08 changed in aedd8dbd). PR8 carries only fail-safe basin circuits. Residuals (shaft, cover, pump head): #8. |
| 2026-11-05-basic-layout-5#5 | Platform JBs in the tray bays; JB-PR1 | medium | closed aedd8dbd | JB-A4-1 (1134.5, 924) and JB-A4-2 (1175.5, 924) at 6.10 / 5.75 kW/m2 at most; JB-PR1 (999.5, 2996) at 5.34, outside Z-LAY-A2E; HPU-5100 / 6100 at 6.02 / 5.75 (mine). Fire-resistant ESD / ERS / ERC cable recorded (D-035.5). |
| 2026-11-05-basic-layout-5#6 | B-SUB at 69.7 m from the trough; intake gas detection only in DESIGN.md | medium | open | Now recorded as a layout requirement in `layout/hvac.yaml` AHU-1 (2oo3 detectors, damper trip). There is still no instrument tag, damper tag or C&E line (design owner, D-035.10). The 69.7 m stays on the siting study's list. |
| 2026-11-05-basic-layout-5#7 | Stale texts (P-08 note, T-8101 service, D-033.7 values) | low | closed aedd8dbd | No "trestle" in `scripts/draft_P-08.py`; the T-8101 service is "LNG spill impoundment sump (tank area)"; D-033.7 corrected in place. |
| 2026-11-05-basic-layout-5#8 | No UPS A / B; ESD push buttons not cabled | low | closed aedd8dbd | UPS-A / UPS-B in B-JET with F-ERS-n100A / B. HS-n100B / C and HS-n107B / C are in the cable schedule; the A stations are wired inside B-SUB (D-035.5 (c)). Residuals: #10 (common routing) and #12 (B station cabling). |
| 2026-11-05-basic-layout-5#9 | Crane strips over the tray bays | low | open | D-035.11 declares the covers (grating on beams) but leaves their design with the structural engineer; review 1 #2's closure is conditional on it. Its design case, "~70 t mobile crane, ~70 t on one outrigger", is low. The lifting study needs 69.3 t of chart capacity at 9.4-13.0 m radius (moments up to 678 tm, LA-6104), which takes a much larger crane class with larger outrigger loads. Z-PAD-A4W is 6.5 m wide. The crane contractor confirms. |
| 2026-11-05-basic-layout-5#10 | Jetty pit datum against the tides | low | closed aedd8dbd | D-013 corrected: deck +12.0 m CD (ASSUMED); ship envelopes to -12.2 m; Z-ESC-A4-SEA -12.2 to -3.1 m; Z-SZ-B1 / -B2 tops at -5.3 m (`layout/zones.yaml`). The caisson that results is new matter (#7). |
| 2026-11-05-basic-layout-5#11 | Deck walk to the open way not screened | low | superseded by 2026-11-05-basic-layout-6#5 | Screened in D-035.9, and still over 5 on the north-edge walks (#5). |

Adversarial-check items raised against 2026-11-05-basic-layout-5 (`build/adversarial-layout-r7.json`), judged on the model:
- **Missed high, the platform spill basis.** The bays no longer hold the spill; they pass it, with
  two 1.5 x 1.5 m outlets per bay. My weir check gives 0.47 m of head at 3.33 m3/s over the 6 m
  perimeter, and Cd 0.6 gives 6.0 m3/s at 1 m. The collectors are 1.5 m wide, 0.60 m deep at 1 %
  (my Manning). The header bay is 36 m2 and 3.4 m deep. T-8102 holds 257 m3 below its inlet, against
  ~170 m3. The pool-fire screening holds (review 4 #5 above). The basis is therefore answered in
  hydraulics and radiation. The header bay as built, and the drain-down of the trestle line behind
  it, are not: #1 and #2.
- **Disputed closure of review 4 #5.** Re-shown for the D-034.3 flows: closed aedd8dbd above.
- **Disputed closure of review 1 #2.** Upheld as conditional: the cover design and the crane class
  are open as review 5 #9.
- **Tank-area spill basis.** Answered. Run-out 4.0 m3/s; trough 3.22 m deep at x 975 with 0.30 m
  freeboard; the rundown at x 979 runs 1.61 m deep; T-8101 19.5 m deep with 1.79 m to the inlet. The
  remaining gaps are the pad inlets (#3) and the shaft (#8).
- **Pit datum against chart datum.** Answered (review 5 #10 closed). The caisson is #7.
- **HPUs and JBs, JB-PR1.** Answered on the model (review 5 #5 closed). Each arm's ERC
  accumulator is ASSUMED, from the arm vendor.
- **Tank-area muster point.** Z-ESC-A1-MUSTER at 0.49 kW/m2, and the A2 walk to it at 4.38 or less.
  For B-SUB the walk fails: #4.
- **Rating comments.** Review 5 #2 (d) is now covered by PFP within 10 m of the XV-3123 tray and on
  the PR6 east leg x 1020-1036. Review 5 #11 is carried as a medium (#5), as the check asked.

Items the response leaves open with a reason, judged against the rating standard:
- **Release-point fire and drift-off pool** carried to the siting study. Honest at medium, and
  tracked as #6. I reproduce the magnitudes: W1 / W2 47.1 / 28.4 kW/m2 for 415 MW at the LA-5104
  base.
- **South-end occupancy rule.** A real safeguard, but held only in notes: #14, low, because the rule
  itself is sound.
- **PR9 passive fire protection.** The requirement is recorded with its rating basis, and the
  product is deferred to the fire protection engineer. That deferral is honest. The 60 min basis is
  not bounded once the trestle drain-down feeds a header-bay fire, which is part of #2.
- **Trestle inventory ~1,020 m3 per line.** Under-rated. D-035.14 (g) rates it medium and hands the
  emptying to the design owner, but the deferral leaves a credible overflow onto the deck and the
  water with no safeguard. I rate it high (#2).

## Site-wide radiation screening (my check of D-035.9)
- Script `build/rev6_screen.py`, written for this review from the D-018 statement, not from the
  author's r8 / r9 / r10 scripts or review 5's rev5 scripts. The walks are in `build/rev6_walks.py`.
  Geometry comes from `layout/zones.yaml` and the built model (bboxes, buildings, junction boxes,
  roads, racks). The method is the point source q = 1.2 x 0.35 x 0.078 x 50 MJ/kg x A / (4 pi R^2),
  with tau 1 and plan distance; troughs and gutters are 0.25 m elements of 0.82 MW/m; the vapour
  flames are 0.35 x m_v x 50 MJ/kg.
- **Tank-area design fire.** Every open leg, both gutters, the basin (201 m2) and the worse of the two
  pad clusters. My values (criterion; D-035.9 in brackets):
  - tanks and towers (8): shells T-2101 4.09 (4.1) and T-3101 1.09 (1.1); S-RT2101 4.38 (4.4) and
    S-RT3101 1.28 (1.3);
  - racks (8): PR6 north 5.94 (5.9); PR6 east leg to x 1060 7.78 (7.8); PR2 south of y 2910
    6.71 (6.7); PR3 east 7.39 (7.4); PR4 north of y 3273 7.56 (7.6); PR5 1.29;
  - buildings: B-SUB 3.12 (3.1) and S1 2.95 (5); B-ANA 3.61 (3.6) (5); TX bays 2.72 (2.7) (8);
  - roads (8): R1 7.18 (7.1); R11 5.87 (5.8); R8 east 6.93 (6.9); R2 west / east 6.95 / 7.43
    (6.9 / 7.4); R4 0.58 (0.6); R12 7.43 (7.5);
  - stand-offs (8): Z-LAY-A8W 6.33 (6.4); crane pads and laydowns at the tanks 1.3-3.5 (3.5);
  - escape and muster: Z-ESC-A2N-W 4.89 (4.8) and Z-ESC-A2N 4.22 (4.2) (5); Z-ESC-A1-MUSTER
    0.49 (0.49) (1.6); stair towers 2.27 / 0.89 (5);
  - process equipment (8): K-7101A / B / C outlines 7.51 / 8.38 / 10.42 (7.4 / 8.3 / 10.3);
    D-7101 4.86 (4.8);
  - junction boxes (8): JB-PR1 5.34 (5.4); JB-A2-2 7.09 (7.1); JB-K7101 6.16 (6.2); JB-A1-1 4.88
    (5.0); JB-T2101 3.41; JB-T3101 1.08; JB-TR-N 2.86; JB-IA 2.64.

  Over their criterion and stated as residuals in D-035: R3 14.3, R6 15.8, the R5 stub 18.7 and R8
  west 11.9; R13 26.1 (26.8); JB-A8-1 56.7 (63.9, fail-safe circuits); the PR6 east-leg PFP band
  35.6; A2E 22.2 and A2S (blocked by design). Not D-018 receptors, but over 8: Z-PAD-A2E 21.0 and
  Z-LAY-A2E 38.5, the compressor crane pad and laydown beside PR3.
- **Overflow sensitivity at the XV-4101 pad:** see #3.
- **Platform**, per bay, with the sump and the collector vapour at the sump or at the worst dry
  outlet downstream (1.05 kg/s; 1.7 kg/s for the header bay, D-035.14 (f)):
  - ways off: best way 1.45-4.51 for every bay except B2-M8, which is 5.24 with header-class vapour
    and about 4.1 with the drain-rate vapour its items warrant (see review 4 #5 above); header bay
    W1 / W2 4.68 / 3.65;
  - muster point and boat route: 0.11-0.17; every bay of a berth 0.96 / 0.95;
  - HPU-5100 / HPU-6100 / JB-A4-1 / JB-A4-2: at most 6.02 / 5.75 / 6.10 / 5.71 (8);
  - PR9: 14-426, and the PR2 end 5-129, against 1.84 / 0.70 from the sump alone (D-035.14 (a)
    confirmed);
  - hulls in the bays' near field: 4-25. With the header bay's backed-up vapour burnt at a dry
    arm-bay outlet, the Berth 2 hull sees 11.4 (D-035: 6.97 with the vapour at the sump). That is
    near field of the same kind as D-018 (e), not a new receptor failure.
- **Deck walks:** see #5. **Release-point fire:** see #6.

## Drawing
Not part of this layout review. No P&ID was reviewed; the P&IDs serve only as the source of the
model. For reference, the `cheme validate` count lines at HEAD are all 0. The accepted ones are
P-04 `0 line-crossing (+2 accepted)`, P-07 `(+2 accepted)` and P-08 `(+1 accepted)`.

## Layout
Commands run at HEAD aedd8dbd from the plant folder with core 1.7.0
(`/Users/arturschweidtmann/Developer/LNG/.venv17/bin/cheme`):
- `cheme layout build --check`: `layout/plant-model.yaml is up to date`.
- `cheme validate`: `90 file(s): 0 error(s), 29 warning(s)`. All 29 warnings are HAZOP:
  `hazop-input-changed` and `hazop-unknown-tag`, outside this scope. The layout model findings are
  infos with their accept reasons. There are 9 `accept-unused` infos (#13), and no `accept-stale`
  or `review-*`.
- `cheme check --stage detail`: every gate ok except design-review (outside scope) and
  layout-review (layout-5 names 709fcf20; this record at aedd8dbd replaces it).
- `cheme diff 0bb82928 aedd8dbd --list`: P-04 / P-05 / P-06 / P-08, BFD and PFD, as listed above.
  The model is current with them.

`cheme layout report`:
- Lines: 146 lines and 310 segments, all routed; none skipped; 0 unrouted.
- Chains per method: astar 39, astar_coarse 3, open 8, pinned 201, rack 10, via 8. There are no
  `direct` and no `rack+direct` chains.
- Chains per reason: pinned 201; local pipe-way 17; local above the pipe-way 11; intent via 8;
  local short run 9; open end 8; local pump run at grade 3; rack longer than local_max_m 5; rack
  battery limit at a rack end 4; local rack run too short 1; local no rack in reach 1; rack crosses
  a road 1. Battery-limit ends: rule 15, rack end 1.
- Rack fill: PR1 46 / 27 %; PR2 28 / 26 %; PR3 10 / 24 %; PR4 33 %; PR5 16 / 6 %; PR6 21 / 10 %;
  PR8 4 %; PR9 5 m 11 %, with the 7 m tier not reported (#13 (d)). PR1 and PR4 are understated
  (2026-11-05-basic-layout-2#5).
- Model findings per rule, all accepted or info: operability 54, tray-span 42, support-missing 36
  (info), free-span 22, tray-zone 13, lifting 12, tier 3, tray-separation 3, escape-ways 2,
  escape-travel 2, laydown 2.
- These are 0: the clash-* rules, headroom, access-blocked, zone-crossing, separation, spacing,
  building-spacing, wall-penetration, vent-outlet, access-enclosed / -unconnected,
  ladder-clearance, walkway-riser, landing-width, egress-zone, operator-unknown, pad-overlap,
  zone-source, support-stub, steel-in-way and pipe-disconnected. Zero means only that nothing
  declared was hit: the header bay assembly (#1) trips none of them.
- Objects: equipment declared 35; inline generated 199; pipes generated 109 / pinned 201;
  structures declared 7 and generated 1 (VP-XV-4107, review_needed, #1); zones declared 113;
  platforms 0; penetrations 0.
- Rules missing from cheme-as-code, for the cases no rule sees:
  - a run with no support after its last rack bent when its segments are short, or when in-line
    items hang on it (#1);
  - generated steel or posts standing inside a recessed zone volume (#1);
  - a pad's inlet capacity (#3);
  - a walk to a muster point through a radiation field (#4);
  - pinned routes in the rack fill (#13).

Accepts in `checks/checks.yaml` (layout rules). Each names its items, or a pattern limited to named
tags; none is a rule wildcard. Item-specific and true on the model are:
- the lifting accepts (T-n101, P-n101A-D with the P-2102 isolation, D-5101 / D-6101 with the PR9 lane);
- the free-span and support-missing entries;
- `tier:BOG1001@PR6`;
- the tray entries;
- the escape entries for the tank tops.

Not true or not current are `operability:P-04/XV41??` for XV-4103 / XV-4107 (#1, #13),
`tray-span:PT-HPU-5100` (#13) and the nine unused entries (#13).

Rendered and read (all under the plant folder, `build/`):
- `build/layout-plan.png`: the whole site.
- `build/layout-plan_crop-1125-845-1185-930.png`: the platform, showing:
  - PR9 between the B2-MAN and B1-MAN bays;
  - the header bay at the south end with the junction drops;
  - the drum bays, the crane strips over the bays, the laydowns;
  - the HPUs and the JBs at the north corners;
  - R9 / R10 and the starts of W1 / W2.
- `build/layout-level-S-T2101-TOP-PP_crop-875-2975-1010-3110.png` and
  `build/layout-level-S-T3101-TOP-PP_crop-735-2975-870-3110.png`: the pump decks, column-head zones,
  PSV zones and roof walkways, unchanged.
- `build/layout-section-y2997_crop-870--8-1120-62.png`: from T-2101 across PR6, JB-PR1's tray drop
  at x 999.5, the BOG area (K-7101B) and the PR3 trough. There is nothing at grade under PR6.
- `build/layout-section-y2997_crop-972--1-1006-19.png`: PR6 with the PSV-1122 tray zone on the 12 m
  tier and the IT-JB-PR1 drop (#11).
- `build/layout-section-x1163.5_crop-795--15-935-25.png`: jetty head, showing:
  - T-8102 to -13 m, below the marine safety-zone tops at -5.3 m, with the tank-type stair artefact (#7);
  - the catwalk S-CW-A9 at +0.3 m over the enlarged collector;
  - the south collector and the header bay recess;
  - the junction drops and D-6101;
  - the PR2 end.
- `build/layout-section-x1158_crop-850--6-905-12.png`: along PR9 and the header bay.
  `build/layout-section-x1158.5_crop-852--4.5-870-9.5.png` is the close-up: the DN 800 assembly south
  of PR9's bent-4 with no steel, the VP-XV-4107 columns and stair and the N2 T-posts standing at deck
  level inside the 3.4 m recess (#1).
- `build/layout-section-x1095_crop-2880--8-3260-18.png`: along the re-routed collector, from the PR1
  junction under PR3 / PR4 past R7 and R2 to the corner at y 3237.5 and PR8.
- `build/layout-section-y3237.5_crop-960--21-1110-14.png`: the west leg into the 19.5 m basin, the
  trough zones to -5.8 m, and the tank-type stair drawn inside the basin (#13).
- `build/layout-section-x1050_crop-2930--3-3065-18.png`: the BOG compressor area, showing PR1 with
  the pads and the trough zone, K-7101C / B / A in their seal zones, and the PR6 east leg.

Measured (`cheme show <tag> --layout`):
- T-2101: S-RT2101 0.6 m, S-ESC-T2101 0.4 m, PR6 5.6 m, PR1 27.8 m, R2 46.2 m, R12 50.4 m.
- T-8101: PR8 6.0 m, R13 25.6 m, R12 57.0 m, PR4 90.0 m, R2 103.5 m, T-2101 166.2 m.
- T-8102: S-CW-A9 9.0 m, PR9 51.4 m, D-6101 51.6 m, D-5101 53.1 m, PR2 75.2 m, R10 86.0 m,
  B-JET 290.9 m.
- B-SUB: R8 2.0 m, R11 7.0 m, R3 45.1 m, PR3 63.0 m, PR2 63.8 m, PR1 70.1 m, B-ANA 84.6 m,
  K-7101C 110.8 m.

## Checked and fine
- **Site geometry against D-013 and the task basis.** T-2101 (929.4, 3025.8) to LA-5102 (1137, 884)
  is 2,152 m at 174.5 deg ("about 2.1 km"). T-2101 to FL-8101 (1484.9, 3102.8) is 561 m at 82 deg
  ("about 560 m east"). The datum correction of D-035.8 is consistent through the site-plan header,
  the zones and the equipment list. T-8102's bottom at -1.0 m CD and the collector inverts at
  +8.1 m CD are 1.4 m above EHW.
- **Model against the P&IDs at HEAD.** The model is current. LNG-4010 with XV-4107 and the moved
  tees T4A4 / T4B4 / T4A5 / T4B5 are routed into the header bay (pinned), with the sheet junctions
  J-Berth1 / 2-liquid at the top of the drops. Every in-line item that D-035.1 names lies inside
  Z-HA-TRAY-HDR in plan (`build/rev6_platform.py`), and no LNG flanged item of the loading lines
  remains between the ways off.
- **PR9.** Lanes x 1152.45 / 1153.95 at 7.6 m and x 1152.45 / 1154.05 at 5.5 m, with 0.3-0.5 m
  between the insulated DN 800 lines; supports every ~2.1 m from y 891.5 to 866. PR9 does not block
  a way off: it ends at y 900, the ways start at y 925, R10 passes under the PR2 end between its
  bents. Its columns stand on the bay kerbs at x 1151.35 / 1157.15. It narrows D-5101's and
  D-6101's lifting lanes, as accepted with the spool removal.
- **Moved items and re-pinned routes.** The moved D-5101 / P-5101 and the re-pinned BOG-6001,
  BOG-6003, N2 tie-ins and drain pump returns clash with nothing (0 clash-*). LNG-5006 at 6.4 m
  clears LNG-4002 at y 865.5.
- **Platform hydraulics.** Outlet weir and orifice capacity, the 1.5 m collector at 1 % (0.60 m
  at 3.33 m3/s), the header bay volume of 122 m3 (36 m2 x 3.4 m), and T-8102's 257 m3 below the inlet
  (28.3 m2 x 9.09 m) all check out.
- **Basin.** 2,400 m3 at 201 m2 stands 11.94 m deep, at -7.56 m, 1.79 m below the -5.77 m inlet. The
  XV-4101 gutter's normal depth is 1.54 m (the inlet is #3).
- **DN 25 relief trays.** Z-HA-TRAY-PSV1121 / 1122 / 1123 / 4111 / 4113 are declared at the items.
  Alone they give 1.1 kW/m2 or less at the receptors (D-035.6). PSV-1121's tray stands 1 m north of
  R7's edge, a residual road.
- **Re-sited HPUs and JBs.** They are outside every zone, laydown, crane strip and R9 / R10, and
  outside the 8 kW/m2 band of every bay (values above). UPS A / B are in B-JET with separate
  feeders, and the platform push buttons are on short cables to the corner JBs.
- **Tank-area muster point.** Z-ESC-A1-MUSTER at (684-698, 3004-3016), west of R4 and inside the
  site, at 0.49 kW/m2; the walk from A2N along R2 west is at 4.38 or less.
- **Escape on the platform.** W1 / W2 and the crossing Z-ESC-A4-X stay clear of the Z-LOOP volumes
  and of every tray zone. B-JET and the muster point lie outside both 200 m safety zones.
- **Hazardous areas and ignition sources.** No tray, junction box or HPU stands in a zone other than
  the accepted Ex entries (tray-zone 13, all accepted). B-JET is the only non-Ex building on the
  jetty and is 200 m or more from every arm (0 `layout-separation`).
- **Electrical rooms and trays.** The electrical, hvac and layout-detail gates are ok. PR8 carries
  only the basin's own circuits.
- **BOG area.** FL-7002 / FL-7003 rise west of the trough and cross it at 11.4 / 11.6 m. No line
  crosses a trough below the 7 m tier.

## Not checked
- **The area classification itself** (CSA C22.1 / IEC 60079-10-1, competent person). Every zone is
  ASSUMED screening.
- **The LNG spill siting study** (CSA Z276 / NFPA 59A thermal radiation and vapour dispersion
  exclusion zones, cited by number only). It covers the release-point fire, the drift-off pool, the
  trestle drain-down (#2, #6), the B-SUB vapour distance and the marine transfer area. My screening is
  an order-of-magnitude check, not that study. Competent person.
- **Civil:** the groundwater and geotechnics of the 19.5 m shaft, the trough excavation beside the
  rack foundations, the real terrain under the profile, and snow and ice in the open troughs (no
  climate basis beyond the design ambient). Civil engineer.
- **Marine:** the deck level, the caisson, the piled deck, the catwalk, the collectors under the deck
  against the wave crest, the boat landing and the mooring (#7). Marine engineer and the TERMPOL
  review.
- **Structural and stress:** PR9, the header-bay support and platform steel (#1), the grating covers
  and crane outrigger loads (review 5 #9), pipe stress, loops and surge loads. Structural and stress
  engineers, crane contractor.
- **Fire protection:** the A2 water spray, the PFP of PR9 / the PR2 end and the PR5 joint, the
  north-edge curtain, foam and fire water. Fire protection engineer.
- **Electrical engineering:** cable sizing, the separation of the UPS channels (#10), the transformer
  bays, the B-SUB rooms and the 69 kV route. Electrical engineer.
- **Pinned routes:** not every one of the 201 was read vertex by vertex. I read the platform and the
  header bay, PR9, the PR2 end, the tank-area pads and trough, PR6 at PSV-1122, the basin and PR8,
  and the BOG area.
- **The estimate and the MTO**, which do not include the civil quantities of the troughs, bays,
  collectors and pits, as D-035.13 states.
- **The HAZOP** (29 warnings) and the design review gate: outside this scope.
