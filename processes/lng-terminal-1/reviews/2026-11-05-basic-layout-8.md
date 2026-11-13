---
topic: layout
reviewed_commit: ae718797
scope: [layout/, piping/routing.yaml, piping/pipe-specs.yaml, electrical/]
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-basic
merge: pending
---
# Review: layout (3D model, routing, buildings, zones, electrical) after the response D-040

Scope: `layout/` (site plan, buildings, structures, placement, zones, hvac, the generated
`layout/plant-model.yaml`, the lifting study), `piping/routing.yaml`, `piping/pipe-specs.yaml` and
`electrical/`. Read as basis, not reviewed:
- `DESIGN.md` D-001 to D-040, mainly D-018 (p)-(w), D-034.3, D-036 item 5, D-038, D-039 and D-040.1-14;
- the `accept:` block of `checks/checks.yaml`;
- the equipment, line and instrument lists, the C&E and sequences where the layout rests on them;
- the P&IDs at HEAD as the source of the model;
- the adversarial check of review 7 (`build/adversarial-layout-r9.json`) and the round-10 layout
  check as D-040.11-14 answer it.

I did not write this layout.

**Commit.** HEAD `ae718797` on `stage/lng-terminal-1-basic`, branched from main `0b155d62` (PR #432).
The working tree was clean when I started (`git status --short` empty). The round is:
- 6f57c6c2, migration to core 1.11.0 (D-038);
- fd39c222, fix round 10 (D-039 design, D-040 layout, including D-040.11-14). This is the last
  commit that touches `layout/site-plan.yaml`, `layout/structures.yaml` and `layout/zones.yaml`;
- 1dd46636 and ae718797, the response to the round-10 design check (D-039.9). In this scope they
  touch the electrical list, the cable schedule, the accepts and the regenerated model.

`git diff --stat 0b155d62 ae718797` over this scope gives 16 files. Among them are site-plan (PR10
re-declared, PR11 / PR12 / PR13 new), structures (S-HDR, HB-* stubs and posts), zones (lift paths
Z-MNT-*, deck and floating crane pads, Z-KC-CURTAIN-N), routing, pipe-specs (Class 150 (g)), the
electrical list (JB-A9, JB-SUB) and the model. The commands ran with core 1.11.0
(`/Users/arturschweidtmann/Developer/LNG/.venv111/bin/cheme`). Other agents worked in the same
folder meanwhile; one wrote `reviews/2026-11-05-basic-design-10.md`.

**Verdict.** The header bay now stands at real size on the model.
- **Review 7's #1 and #2 are closed**, and so is the high its adversarial check made of them.
  - The DN 800 shore ESD valves, strainers and crossover valves have declared envelopes and vertical
    lift paths. My own envelope check (`build/rev8_env.py`) finds 0 clashes against steel, pipes,
    trays and floors; the nearest gap is 0.10 m (XV-4107 body to its cradle beam).
  - Both crossovers leave the bottom of the low runs.
  - Every run in the bay rests on steel that reaches the deck, with spans of 11.0 m or less.
- **Review 7's #4-#6 are closed.**
  - #4: the arm lifts are made from declared floating crane pads and have lifting-study rows.
  - #5: the sump cables run in two trays through JB-A9.
  - #6: the water curtain is a zone, and the occupancy rules are in SEQ-LOAD S4.
- **Review 5 #6 is closed:** the B-SUB intake gas trip is drawn (AT-8141A/B/C, UZ-8142..8144, I-811).
- **Review 7's #3 is superseded by #1 here.** D-040.12 rescoped the rain case honestly: rain on the
  *governing* platform spill in T-8102, with a carrier alongside. That is no longer a drain-down side
  case.
- **My screening reproduces the D-040 table.** Every value in the tank area matches within 0.05
  kW/m2. The platform values are within ~0.1, except the items noted under #7.

The fresh pass finds no critical or high. It finds two mediums:
- **#1, T-8102 in rain.** The jetty sump's hull criterion holds only dry and in light rain: 8 kW/m2
  at 5-8 mm/h with the pool alone. The design storm leaves ~20 m3 of rain water under a drain-down's
  falling LNG. Both are carried to the siting study as SC-3, honestly. The fixed foam that T-8101
  has, and that D-040.12 names as an option, is still undecided for T-8102.
- **#2, W-8002.** The line list and D-039.1 (e) state that W-8002 is "laid to fall to the battery
  limit" as its freeze protection. The model holds it level for 100 m on PR8, with a 0.9 m hump
  before the battery limit, so ~0.8 m3 of water stands in it.

It also finds seven lows (#3-#9), on these points:
- the header bay's kerb margins;
- PR11 / PR13 cable support and catwalk headroom;
- the header bay field cables, which run without a tray;
- the B-SUB intake detectors, placed downstream of their damper;
- margin items stated as "met";
- the header bay lifts and MEWP access;
- accept hygiene.

No critical or high finding is open in this record or carried from an earlier one. From the layout
side, the arrangement can go to basic engineering with the mediums tracked. A merge is pending; it
is for a human or the reviewer, not the author.

## Findings
| id | area | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-layout-8#1 | A9 jetty sump T-8102 in rain (zones.yaml Z-HA-SUMP-T8102 basis, site-plan.yaml separations T-8102 -> Z-SHIP-*, D-040.3 / .12, D-018 (s) / (v)) | T-8102 pool fire with rain boil-off; rain water under a drain-down; fixed foam | **Hulls in rain.** My screening (`build/rev8_screen.py`) reproduces D-040.12. The inputs: the 28.3 m2 pool burning, rain boiling 610/510 kg of LNG per kg of rain on the ~1,006 m2 catchment, the D-018 point source x 1.2. Results: <br>- hull boxes Z-SHIP-B2-5 / B1-5 at 28.8 / 30.2 m: 4.5 / 4.1 kW/m2 dry; 11.5 / 10.4 at 10.4 mm/h with the pool alone, 13.6 / 12.4 with the 1.05 kg/s collector vapour; 8 kW/m2 is reached at 5.2 mm/h with the pool alone and 2.1 mm/h with the vapour; <br>- the turned 315 x 55 m hulls the boxes bound, which stand 31.6 / 32.3 m from the sump centre: 9.5 / 9.1 at 10.4 mm/h; 8 kW/m2 at 7.7 mm/h with the pool alone and 4.5 mm/h with the vapour. <br>The collector vapour is a first-minute value, so the hours-long case is the pool alone: 5-8 mm/h, a moderate rain at a wet coastal site. The governing 170-210 m3 pool lasts 3.7-9 h with the carrier alongside. **Water under LNG.** In the design rain, ~20 m3 of unfrozen rain water stands in the sump under a drain-down's falling LNG, which the binding basis "no LNG on standing water" rules out (D-018 (s)). **Rating.** Both are named honestly as SC-3 for the siting study, with options and the H-05 restamp. They are not hidden, so the rating is medium. But the basic layout still states the T-8102 hull separations (site-plan 24.6 m, "8 kW/m2 or less") without the rain limit. Its main option, fixed high-expansion foam (T-8101 has it, D-037.9), is not decided. And the design basis has no rain intensity to judge it by (review 2 #14). | medium | open | Design owner with the fire protection engineer: decide fixed high-expansion foam on T-8102 (as T-8101), or the remote sump of D-040.12 (i), at basic design rather than after the siting study. Civil: put a Kitimat rain intensity basis (IDF) into `process/design-basis.yaml`, and state the T-8102 hull limit as a rain intensity in the separation reasons. Hand SC-3 to the siting study with the turned-hull distances and the standing-water RPT case. |
| 2026-11-05-basic-layout-8#2 | A8 / PR8: the P-8102 riser and run (line list W-8002 notes, D-039.1 (e)); A9 W-8003 (D-037.17) | W-8002 S1 (DN 100) on PR8; W-8003 S1 overhead | **The basis.** The freeze protection of the T-8101 rainwater line is that the riser drains back through CV-8114's hole and "the run on PR8 is laid to fall to the battery limit (ASSUMED, layout) ... no heat tracing" (line list, D-039.1 (e); design ambient -20 degC). **The model.** The route is router-made (method `rack`, no pin in `piping/routing.yaml`): (986.0, 3232.5) up to 7.97 m, down to 7.06 m on PR8, then level at 7.06 m for 100.8 m to x 1086.79. There it rises again to 7.97 m and drops to the battery limit at 7.06 m (`build/rev8_model.pkl`). So the PR8 run is a trap between two high points. It cannot drain back through the riser or forward to the battery limit, and ~0.8 m3 of water stands in it. **Consequence.** It freezes or bursts, P-8102 cannot empty the pit, and rain collects on the T-8101 floor. The LAH hold and the I-809 LAHH trip keep transfers safe. Outside transfers, though, the rundown-spill residual of D-039.1 (h), LNG onto standing water, then lasts until the line is thawed and repaired. W-8003's overhead run on A9 is likewise level at 2.6 m for 7.8 m. **Rating.** The drawn plant contradicts a stated safeguard. Independent level trips back it, so medium. | medium | open | Pin W-8002 in `piping/routing.yaml` with a continuous fall from the riser's high point to the battery limit, with no hump at PR4's joint (lower the BL-oily-water point, or bring the run in under PR4's tier). Otherwise trace it and say so in the line list. Give W-8003's overhead run a fall to its free drop. |
| 2026-11-05-basic-layout-8#3 | A4 header bay recess (zones.yaml Z-HA-TRAY-HDR x 1155-1162.5, y 857.5-862.3; D-040.14 (a)) | XV-5101 / XV-6101, SR-6102, XV-4107 at real envelope | My envelope check (`build/rev8_env.py`, D-040 envelopes) puts these beyond the kerb lines: XV-6101 body 0.30 m north, XV-5101 body 0.10 m south, SR-6102 run flange 0.03 m north, XV-4107 body 0.05 m and actuator 0.25 m west. The leak points (bonnet joints, stem seals, strainer flanges) lie inside the recess, but within 0.0-0.5 m of its kerb at up to 5 m above the deck. A drip or a spray deflected by wind lands on the deck, by PR10's columns and the S-HDR stair. D-040.14 (a) leaves the margin to PR10's structural design. That is a stated deferral with no hidden hazard, so low. | low | open | With PR10's structural design (marine engineer), either widen the recess under the lanes (moving the kerbs and PR10's columns), or fit drip lips / spray shields on the bonnet joints and strainer flanges that turn leaks into the recess. State the margin. |
| 2026-11-05-basic-layout-8#4 | A4 / A9 cable racks PR11, PR12, PR13 (site-plan.yaml; D-040.5, D-040.11) | PT-PR11-1/-2, IT-PR11-1/-2, links PT-PR11-PR13 / IT-PR11-PR13, PR13 catwalk leg | **PR11's tray tier.** It has steel only at its two bents (y 864.0 / 856.55). D-040.11 removed the stringers and mid beam, so the power and instrument trays span 7.45 m between them. PR12's trays also cantilever 1.5 m south of y 864 to the link at y 862.5. The tray rule's span is 6 m (ASSUMED), but the tool does not check rack-tier trays. **The links.** PR11 to PR13 drops 5.0 m (power, x 1152.84) and 6.0 m (instrument, x 1150.56), both at y 855.55, with no steel within 1 m. PR11's south bent is 1.0 m north, and PR13's posts stop at 2.6 m. **PR13's catwalk leg.** In the model its west posts stand at x 1160.85 (1160.70-1161.00), outside the catwalk deck (x 1161.0). The site plan says "on the walkway's edges". Its beams leave 2.1 m over the catwalk walkway, the only way to and from A9, against the 2.2 m of every escape zone. These are support and access details; the cables are fire-resistant and their loss is safe, so low. | low | open | Give PR11's tray tier a mid support or a tray-carrying stringer on its west column line (clear of line A, 0.14 m), and riser steel for the two link drops. Put PR13's west posts on brackets off the catwalk edge beam, as declared. Raise PR13's beam level so 2.2 m stays clear over the walkway, or state 2.1 m against the site standard. Report the unchecked rack-tier and vertical tray spans to cheme-as-code. |
| 2026-11-05-basic-layout-8#5 | A4 header bay instrument cabling (cable schedule; Class 150 (d) / (e) / (g)) | IC-XV-5101 / IC-ZSC-5101 (105 m), IC-XV-6101 / IC-ZSC-6101 (87 m), IC-XV-4107 / IC-ZSC-4107 / IC-ZSO-4107 (93 m), IC-XV-4103 (90 m), IC-PDI-5102 / 6102, IC-PI-4105 / 4106, IC-TI-4103 / 4104 (89-99 m) | **The cables.** In the model and the schedule, every header bay field cable runs 80-105 m to JB-A4-1 / JB-A4-2 at the platform's north corners with `trays: []`. Among them are the SIS outputs to the shore ESD valves, and the opening command of XV-4103 / XV-4107 that SEQ-LINE-EMPTY S1 needs within ~0.5 h of a header bay fire. Their route is stated only in words (Class 150 (e): "the cables up to the package are inside the 240 min jacket"). For the sump, review 7 #5 made the same point and JB-A9 answered it. The instrument trays already pass the bay: IT-PR11, IT-PR12 and IT-PR9-1. **Rating.** XV-n101 fail closed on a burnt cable, and the fire-resistant cable is stated, so low. | low | open | Route these cables in the PR11 / PR12 / PR9 instrument trays to a junction box outside the header bay fire's near field. Or declare a header bay JB, as JB-A9. State the fire-resistant run and the XV-4103 / XV-4107 command's survival time. |
| 2026-11-05-basic-layout-8#6 | A6 B-SUB refuge intake (instrument list AT-8141A/B/C, UZ-8142; layout/hvac.yaml AHU-1; C&E I-811) | AT-8141A/B/C at (1193.5, 2967-2968, 3.5), UZ-8142 at (1194.5, 2967.5), AHU-1 at (1187, 2969) | **The arrangement.** The detectors stand "in the LV1 intake duct downstream of the louvre", 1 m inside the gas-tight damper they close. The duct from LV1 to AHU-1 is ~5.5 m long, ~1 s of transit at 20,000 m3/h. Detection, the 2oo3 vote and a spring-return closure take ~10-20 s (ASSUMED). The fan stops first, but the building still takes a few tens to ~100 m3 of outdoor air at the cloud's concentration before the damper seats. **The basis.** No ingress or transit-time basis is stated for the temporary refuge (D-037.5), and the order of detector and damper is the reverse of the usual practice. Dilution in the 3,000 m3 building keeps this far from a hazard the basic design must answer, so low. | low | open | HVAC and F&G vendors, design owner: put the detectors at the louvre face, upstream of the damper. State the closure time and the ingress it allows against the refuge's volume and the switchgear's ignition sources. |
| 2026-11-05-basic-layout-8#7 | screening statements (DESIGN.md D-040.8 table, D-040.14 (c); site-plan.yaml separations Z-HA-TRAY-HDR -> Z-SHIP-*) | the platform's margin items and the header bay to hull rows | **Margin items.** D-040.14 (c) calls the following "margin items for the siting study", while the D-040.8 table rows still read "met". My values (author's in brackets): <br>- worst best way off 5.22 (5.13) at the northernmost Berth 2 manifold bay row (W2 5.22, W1 6.28), against 5; <br>- HPU-5100 8.08 (8.03) and JB-A4-1 8.04 (7.99), against 8; <br>- ERS channel B boxes 9.44 / 9.07, against 8. <br>**Header bay to hull.** The separations quote "7.0 / 6.8 on the hull" with the bay's 1.7 kg/s vapour at the sump. The same case's ways-off rows (D-035.14 (f)) burn that vapour at a backed-up dry outlet. Burnt at the Berth 2 arm-bay outlets, the turned hulls see 17.7 / 12.7. That is the same near-field class as an arm-bay fire (D-033.7), so it is no new hazard, but the statement is one-sided. | low | open | Correct the D-040.8 rows and the two separation reasons to state these as exceedances or residuals for the siting study. Alternatively move HPU-5100 / JB-A4-1 ~1-2 m north-west and the ERS channel B boxes beside the channel A panels, so the rows are met. |
| 2026-11-05-basic-layout-8#8 | A4 header bay maintenance and lifts (zones.yaml Z-PAD-A4SE / -A4SW, Z-PAD-B2-FC / -B1-FC, Z-MNT-*; D-040.1, .4, .13, .14 (b)) | MEWP to XV-4107 / XV-4103 tops and the strainer covers; lifts over live lines; floating crane in the other berth's safety zone; deck pads | **(a) MEWP reach.** The basket must pass over S-HDR (handrail 5.6 m) and between the XV-n101 actuators. It then has to drop ~4 m within ~3.5 m into the slot between the strainer bodies (2.5 m apart) and the low runs' insulation (2.4 m apart), at 11-13 m from the pad. No machine class or reach diagram shows that a ~16 m articulating boom can do this. **(b) Lifts over live lines.** The XV-4107 lift (12 t at 14.3 m), the actuator packages and the D-6101 lift (18 t) slew over the berth headers and low runs. Those lines are full of LNG with "no transfer" only. Unlike the in-tank pump lifts (accept `layout-lifting:P-2101[A-D]`), no dropped-object or SIMOPS basis is stated. **(c) Floating crane.** Z-PAD-B2-FC / -B1-FC lie ~50-70 m from the other berth's vapour arm, inside its 200 m marine safety zone (Z-SZ-B1 / -B2, TIG Rev 3: no other vessel during a transfer). The lifting basis requires "no transfer at that berth" only. Radiation from the other berth's bays is 6.0 / 5.7 kW/m2, so that is not the issue. **(d) Deck pads.** The 7.0 x 9.0 m pads over the collector covers are left to the crane contractor and marine engineer (D-040.14 (b)). These are maintenance plans and holds, not hazards of the drawn plant, so low. | low | open | MEWP contractor: a reach diagram with a named machine class for XV-4107, XV-4103 and the strainer covers. Otherwise declare a removable access frame between the lanes. Lifting contractor: state the SIMOPS basis for lifts over the live berth headers and low runs (lines depressured / warmed, or a load path clear of them). Marine / terminal: state that a floating-crane arm lift needs both berths without transfer, or the exemption under the TIG. |
| 2026-11-05-basic-layout-8#9 | accept hygiene (checks/checks.yaml) | `control-unresolved:loops.20-22` (gate control-complete), `layout-clash-tray:PT-PR13-1+PR11/bent-1/col-0` | **Control-unresolved accepts.** The six accepts on LIC-5111 / LIC-6111 / LIC-8101 are item-specific and true. They sit, though, on `control-complete`, a detail-stage gate, and say the values are "to be replaced ... at detail design". So they make the detail gate pass without the values it exists to require. **PR13 clash accept.** Its reason says the two strips "meet at y 856.9-857.0". Since D-040.11 the model has PR13 on y 856.05 (posts 855.3 / 856.8) and PR11's south bent at y 856.55. The reason is otherwise right: the tray passes PR11's south-east column on a bracket. | low | open | Track the LIC start / stop levels as an issue or hold for the detail gate, not as an accept on it, or limit the accept to the basic stage. Bring the PR13 accept's geometry text up to date. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-layout#2 | Road R5 blocked by B-PLAT; no crane access to the platform | high | superseded by 2026-11-05-basic-layout-7#4 | Its successor is closed below: the floating crane pads and the arm rows of the lifting study. |
| 2026-11-05-basic-layout#9 | Span screening classes LNG as gas | medium | open | Unchanged (pipe-specs.yaml notes; the free-span finding still reads "DN 800 gas"); 22 free-span and 33 support-missing, each accepted by id. |
| 2026-11-05-basic-layout-2#3 | No flare radiation basis at B-SUB | medium | open | B-SUB unmoved (separation 314 m to FL-8101); the derrick owner's contour is still owed. |
| 2026-11-05-basic-layout-2#5 | DN 800 / 900 LNG lines at 80 mm insulation | medium | open | The model still has LNG-5001 / LNG-6001 / LNG-4010 at 80 mm and LNG-4003 at 80 mm. It now constrains the header bay: the crossover shoe stubs' top (0.61 m) is set to the 80 mm insulation of LNG-4010 (1.10 - 0.41 - 0.08 m). At 200 mm the insulation would sit below the stub top and closer to the cradle beams, so the bay's support heights depend on this finding. |
| 2026-11-05-basic-layout-2#6 | Loop bays unsized, loops not routed | medium | open | Unchanged; the stress engineer's. |
| 2026-11-05-basic-layout-2#8 | Dome-edge valves out of reach; XV-2123 / XV-3123 differ | medium | open | Unchanged; accept `operability:P-01/XV110[6-9]`, roof nozzle platform tank supply. |
| 2026-11-05-basic-layout-2#10 | Oil-filled transformers inside B-SUB; no 69 kV bay or route | medium | open | Unchanged: the bays Z-KC-TX-BAYS are reserved, with no 69 kV route. |
| 2026-11-05-basic-layout-2#13 | PSV / vacuum valve inlet isolations at foot level | low | accepted: locked-open isolations operated only for valve change-out; in-line item placement not settable in cheme-as-code (D-029.18); accepted by the author in f5d925f6, reviewers 6, 7 and 8 concur | Unchanged under core 1.11. |
| 2026-11-05-basic-layout-2#14 | No site wind basis | low | open | `process/design-basis.yaml` has no wind, rainfall or ground entry. It weighs more now, because the rain intensity governs SC-3 (#1 of this record). |
| 2026-11-05-basic-layout-2#15 | Drain and KO pump suction valves below deck or grade | low | accepted: model artefact of the in-line item placement of cheme-as-code (D-029.18); accepted by the author in f5d925f6, reviewers 6, 7 and 8 concur | The accepts `HV??1[57]` / `HV8106?` are current. |
| 2026-11-05-basic-layout-3#7 | Both roof exits beside the PSV outlets | medium | open | Level plans `build/layout-level-S-T2101-TOP-PP_crop-875-2975-1010-3110.png` and `-T3101-` unchanged; roof clearing on high tank pressure only in D-031.8. |
| 2026-11-05-basic-layout-3#9 | Riser towers: clearance, members at the drops, 13 m posts | medium | open | Unchanged; the tank contractor's. |
| 2026-11-05-basic-layout-3#10 | Accept reasons that do not match the model; FL-8101 lifting row | low | accepted: (a)-(c) fixed in 79d5c7ad; (d) the FL-8101 row cannot be marked as an unplanned lift in cheme-as-code and the stack is maintained by the derrick hoist (D-027.14, D-031.11); accepted by the author in 79d5c7ad, reviewers 6, 7 and 8 concur | Unchanged. |
| 2026-11-05-basic-layout-5#6 | B-SUB intake gas detection only in DESIGN.md | medium | closed fd39c222 | On P-08 and in the lists: AT-8141A/B/C (2oo3 at 25 % LFL), UZ-8142 / UZ-8143 / UZ-8144, C&E I-811. Gate `refuge-intake-gas-trip-on-pid` ok; cabled to JB-SUB at CR-1 (1dd46636). The placement of the detectors relative to their damper is #6 of this record. |
| 2026-11-05-basic-layout-5#9 | Crane strips over the tray bays | low | superseded by 2026-11-05-basic-layout-7#4 | The strips are part-lift strips Z-MNT-A4W / -A4E; #4 is closed below. |
| 2026-11-05-basic-layout-6#1 | Header bay not buildable or operable as drawn | high | closed fd39c222 | The adversarial check disputed the c257902c closure, with reason: it rested on symbols. It is closed now on buildability at real size. Lanes y 858.2 / 861.8: <br>- the low runs at 2.51 m on PR10's 1.9 m tier; <br>- the berth headers at 4.99 m on its 4.5 m tier, under open sky; <br>- the returns at x 1163.4, outside the recess; <br>- PR10's bents at x 1147.5 / 1152.45 / 1157.4 / 1162.35, columns at y 857.35 / 862.65, none in the recess (y 857.5-862.3); <br>- the drops on PR11 with base posts HB-LNG4001-D / -4002-D. <br>`build/rev8_env.py` finds 0 clashes for every real body, actuator, cover, basket path and lift-to-sky. Sections `build/layout-section-x1155.75_...`, `-y858.2_...`, `-x1161.1_...`, `-y860_...`, `-x1153.95_...`, `-x1158.9_...`. |
| 2026-11-05-basic-layout-6#7 | T-8102 caisson in the tidal zone | medium | open | The marine engineer's hold. The tank-type stair is still drawn inside T-8102 (`build/layout-section-x1163.5_crop-798--15-870-12.png`). |
| 2026-11-05-basic-layout-6#11 | PSV-1122 inlet on PR6 against Class 150 (a); welded-run notes | low | open | The line list carries the welded-run notes on LNG-4001 / LNG-4002 only (grep), not on the Class 150 (a) / (b) tank-area and riser lines (design owner). |
| 2026-11-05-basic-layout-6#14 | South-end occupancy rule in notes only; PDI-n102 local | low | closed fd39c222 | SEQ-LOAD S4 operator text and `control/philosophy.md` lines 98-101 hold the rules. PDI-n102 is transmitted with a PDAH (D-039.6 (a), instrument list). |
| 2026-11-05-basic-layout-7#1 | Header bay valve and strainer envelopes, actuators, removal | medium | closed fd39c222 | **Envelopes and paths.** Declared in zones.yaml (Z-MNT-XV5101 / -XV6101 / -SR5102 / -SR6102 / -XV4107 / -XV4103). In my check the nearest gaps are 0.15 m (XV-n101 bodies to the S-HDR floor beams), 0.25 m (strainers to PR10 bent-2) and 0.10 m (XV-4107 to its cradle beam). Every lift path is clear to the sky. **Berth 1 run.** 7.3 m (x 1163.4 to 1156.1), with 4.86 m straight between the LR tangents for the 1.6 m valve and the 2.2 m strainer. **Lifts.** The D-040 lift table (13.9 t gross at most, 18.5 t needed at 75 %) from Z-PAD-A4SE. Its residual plans are #8 of this record. |
| 2026-11-05-basic-layout-7#2 | Crossovers drawn at the run centreline, against P-04 and the drain-down bound | medium | closed fd39c222 | Pins in routing.yaml drop from the low runs' axis at 2.51 m to 1.10 m (LNG-4010) and 0.83 m (LNG-4003). The branch inverts are below the runs', so the ~11 m3 wedge is gone, and SEQ-LINE-EMPTY keeps XV-4103 first. The tee orientation is still not recorded by cheme-as-code (reported). |
| 2026-11-05-basic-layout-7#3 | Rain boil-off at T-8102 during the drain-down | medium | superseded by 2026-11-05-basic-layout-8#1 | D-040.12 rescoped it to every pool (the governing platform spill) and found the standing rain water. My values in #1. |
| 2026-11-05-basic-layout-7#4 | Whole-arm lift rests on an ASSUMED floating crane the model does not show | medium | closed fd39c222 | Crane pads on the water Z-PAD-B2-FC / -B1-FC (22 x 38 m, reach 25 m). The lifting study's eight arm rows are from them: 20.2-21.9 m, 46-52 t gross, 61.6-69.3 t at 75 %, lane clear, laydowns Z-LAY-A4NW / -A4NE. The vendor, mooring and pocket holds are named (D-040.10). The safety-zone condition is #8 (c) of this record. |
| 2026-11-05-basic-layout-7#5 | Sump cabling: stated route not in the model; VSD feeder with SIS inputs | low | closed fd39c222 | C-M-P-8103 runs in PT-PR2-B-*, PT-PR9-*, PT-PR12-1, PT-PR11-*, PT-PR13-1 (393 m). MC-JB-A9 runs in IT-PR2-*, IT-PR9-1, IT-PR12-1, IT-PR11-*, IT-PR13-1 (388 m), 1.04 m from the power tray on PR13. JB-A9 at (1160.5, 821.0) is 9.5 m from the sump centre, outside its zone. A bad LZT-8119 signal is a hold (D-039.4). The rack spans are #4 of this record. |
| 2026-11-05-basic-layout-7#6 | Walk values, water curtain and occupancy records | low | closed fd39c222 | D-040.6 corrects the walk rows. The curtain is the keep-clear zone Z-KC-CURTAIN-N with its coverage, and the occupancy rules are in SEQ-LOAD S4. |

**Earlier findings already closed and still holding.** I re-checked these against the model. They
were closed in earlier records and need no carrying:
- review 1: #1, #3-#8, #10-#18 (e11eb12a, fa3304be);
- review 2: #1, #4, #7, #9, #11, #12 (f5d925f6);
- review 3: #1, #3, #5, #6, #8, #11, #12 (79d5c7ad), and #4 (c257902c);
- review 4: #1, #3, #6 (709fcf20), #4 (709fcf20) and #5 (aedd8dbd);
- review 5: #1, #3, #4, #5, #7, #8, #10 (aedd8dbd);
- review 6: #2-#6, #8-#10, #12, #13 (c257902c).

These were superseded and their successors are closed or carried above: review 2 #2, review 3 #2,
review 4 #2 and #7, review 5 #2 and #11.

Review 4 #4 (R1, the fire approach) holds: R1 is 7.34 kW/m2 in my design fire. Review 4 #5 (the
ways off) holds for the pool fires at the way-off points, but the worst best way is now 5.22, over 5
(#7 of this record).

**Adversarial-check items raised against review 7** (`build/adversarial-layout-r9.json`), judged on
the model:
- **Missed high: #1 and #2 as one high (an unbuildable header bay that contradicts P-04).** Answered.
  The real-size arrangement is drawn and checked, and the bottom takeoffs are built. The dispute
  over the rating is moot now that both are closed.
- **Missed medium: the Berth 1 run length.** Answered: 7.3 m, with 4.86 m straight.
- **Missed medium: strainer type.** Answered. SR-n102 are T-type strainers on P-05 / P-06; the model
  item is `Strainer`, no longer `ConicalStrainer`, and gate `permanent-shore-strainers-on-pid` is ok.
- **Missed low: pocket water.** Answered as a stated basis (D-040.7 (c)). Its larger sibling, ~20 m3
  of rain water under a drain-down, is in #1.
- **Disputed closure, review 6 #4.** It was conditional on review 5 #6, which is now closed.

**Round-10 layout check (answered in D-040.11-14):**
- **North-end steel of the header bay (D-040.11).** Closed on the model.
  - PR9's bent at y 866 and PR11's bents at y 864 / 856.55 are built (rack parts in the model).
  - PR12 has no steel of its own.
  - Support gaps along the paths (`build/rev8_spans.py`): line A 2.1, 2.0, 1.45, 11.0 to
    HB-LNG4001-D, then 1.35 m; line B 2.1, 2.0, then 7.75 m to HB-LNG4002-D; the berth headers
    4.95 m on PR10 and 7.8 / 5.5 m to PR9's bent.
  - The LNG-4002 S5 maximum is the 19.1 m junction span at path 4.4 m, as the accept says.
  - What is left is the tray support of PR11 (#4).
- **Rain on every T-8102 pool and SC-3 (D-040.12).** Reproduced. It is honestly carried; #1 holds
  the basic-design decisions left.
- **Strainer and crossover access by MEWP (D-040.13).** Closed on a MEWP duty that no reach
  diagram supports yet (#8 (a)).
- **Crane pads and floating crane (D-040.4, D-040.14 (b)).** Declared and in the lifting study. The
  pad footprint and the other berth's safety zone are #8 (c), (d).

**Items left open with a reason, against the rating standard:**
- **D-040.14 (a), recess margins.** A stated deferral to PR10's structural design: low (#3).
- **D-040.14 (b), deck pads.** The crane contractor's and marine engineer's: low (#8).
- **D-040.14 (c), margin items.** Honest in 14 (c), but the D-040.8 table still says "met": low (#7).
- **D-040.10: vendor envelopes and fire-stroke qualification, floating crane class and mooring,
  PR10 / PR11 / PR13 steel, the returns' stress, SC-3 and the pocket RPT, the curtain's design, the
  Kitimat rainfall, the tool reports.** Each is deferred to a named discipline with a reason. None
  hides a hazard the layout must answer, except the parts of SC-3 that are basic-design choices
  (foam on T-8102, the rain basis), which #1 carries as a medium.
- **D-039.9 (j): a SEQ-LINE-EMPTY abort held longer than ~0.45 h feeds the header bay leak past the
  240 min PFP of PR10 / PR11 / S-HDR (to ~6.5 h).** Stated as a residual of hold H-07 for the
  siting study, with the abort causes made unlikely by the permissive and the N2 back-up. From the
  layout side, the PFP scope of Class 150 (g) is the bound this residual exceeds. The statement is
  honest; the rating belongs to the design review.

**Accepts in `checks/checks.yaml`.** Each names its findings by id, or by a pattern limited to named
tags; none is a rule wildcard. Validate reports none stale and none unused. The round-10 accepts:
- **`layout-free-span:P-04/Line_LNG4002_S5`.** True: the 19.1 m span is at the PR1 / PR2 / PR3
  junction, and the bay spans are 2.0 / 7.7 m. The accept states honestly that it cannot see a
  longer bay span below 19.1 m.
- **The new P-04 / P-07 drawing crossings (N-4002, LNG-4008, DR-7001, FL-7002 x 2).** Item-specific
  topological reasons, checked against D-038.3 / D-039.9 (i). The six carrier connections stay
  unaccepted warnings, outside the drawing-clean rules.
- **`layout-clash-pipe-steel:P-05/Line_LNG5001_S1+PR10/bent-1/col-0`, `layout-rack-fill:PR10@1.9`.**
  True on the model: the north leg rests at the column head, and the 1.9 m tier carries only two
  1.21 m lanes.
- **`layout-clash-tray:PT-PR13-1+PR11/bent-1/col-0`.** True, with stale geometry text (#9).
- **The six `control-unresolved` accepts.** Item-specific, but placed on the detail gate they defer
  to (#9).
- **The restated D-5101 / D-6101 lifting accepts and the strip names in the support accepts.** True
  on the model. The P-8103 tray-span accept quotes 9.5 m, which is current.

## Site-wide radiation screening (my check of D-040.8 and .12)
The scripts are `build/rev8_screen.py` and `build/rev8_screen2.py`. I wrote them for this review from
the D-018 statement and the zones and model as they stand, not from the author's r15 / r16 or review
7's rev7 scripts.

**Method.**
- Point source q = 1.2 x 0.35 x 0.078 x 50 MJ/kg x A / (4 pi R^2), with tau 1 and plan distance
  R >= 1 m.
- Burning surfaces are divided into 0.25-0.5 m cells. A vapour flow m_v burns as 1.2 x 0.35 x m_v x
  50 MJ/kg at a point.
- Every receptor is sampled on a 0.5-2 m grid, or along its centreline and both edges.

**Sources.**
- Tank area, the D-034.3 run-out:
  - every open trough leg (Z-KC-TROUGH-PR1 / -PR3 / -SUMP);
  - both gutters, including the 1.2 m XV-4101 gutter;
  - the 201 m2 basin;
  - the worse pit cluster burning together (XV-4101 / 4106 / 4102, or XV-1102 / 4105).
- Platform: each bay as zones.yaml subdivides it, with the 28.3 m2 sump and 1.05 kg/s of collector
  vapour. For the header bay the vapour is 1.7 kg/s. The vapour burns at the sump or at the worst
  dry outlet downstream; for the header bay, at any outlet its back-up reaches.
- Seal leak (D-036 item 5): 1 kg/s at the header bay.
- Rain: the T-8102 pool plus rain boil-off, as in #1.

**Tank-area design fire, kW/m2, with the criterion in brackets:**
- tanks and towers (8): T-2101 4.11 and T-3101 1.07; S-RT2101 4.41 and S-RT3101 1.26;
- racks (8):
  - PR6 north 7.95 and PR6 east leg to x 1060 7.81;
  - PR5 1.29;
  - PR2 south of y 2910 6.80;
  - PR4 north of y 3273 7.57;
- buildings: B-SUB 3.14, its west wall with door S1 3.14, B-ANA 3.65 (5); TX bays 2.74 (8);
- roads (8): R1 7.34, R11 5.97, R12 7.48, R4 0.58. R2 is 6.96 to x 1050 and 8.37 to x 1060, at the
  trough band's edge;
- stand-offs (8): Z-PAD-T2101N 3.39, Z-LAY-A8W 6.37;
- escape and muster: Z-ESC-A2N-W 4.92, Z-ESC-A2N 4.23 (5); Z-ESC-A1-MUSTER 0.49 (1.6);
- process equipment (8): K-7101A / B / C 7.55 / 8.45 / 10.55 (water spray, D-035.3); D-7101 4.89;
- junction boxes (8): JB-PR1 5.38, JB-A2-2 7.11, JB-K7101 6.21, JB-A1-1 4.91, JB-T2101 3.31,
  JB-T3101 1.06, JB-TR-N 2.66, JB-IA 2.61, JB-SUB 2.94.

These equal the D-040.8 values. Over their criterion, as the stated residuals or by design (roads
and ways that cross the trough band, D-033 (d) / (e)): JB-A8-1 60.3, R3 14.3, R6 14.7, R8 11.6,
R13 26.8, R2 and R7 at their trough crossings, Z-ESC-A2S / -A2E, Z-PAD-A2E 20.5, Z-LAY-A2E 35.8.

**Platform, one bay.**
- ways off: the best way is 5.22 at worst (northernmost B2 manifold row; the author has 5.13, #7).
  It is 4.98 for the B2-A4 arm bay and 4.56 for the header bay with its vapour at any backed-up
  outlet;
- muster point / boat route: 0.17 / 0.17; B-JET 0.19; JB-JH 0.17;
- HPU-5100 / 6100: 8.08 / 7.77; JB-A4-1 / -2: 8.04 / 7.72;
- ERS channel B boxes: 9.44 / 9.07; channel A panels: 7.66 / 7.38 (#7);
- deck pads Z-PAD-A4SE / -A4SW: 2.80 / 2.13 from the sump and vapour alone, in the near field in a
  bay fire. They are used only with no transfer;
- floating crane pads with the other berth's bay burning: 5.99 / 5.74;
- S-HDR: 2.44 from the sump and vapour alone;
- JB-A9: 62.6 in the sump fire (its own instruments' near field, loss safe);
- hulls: in their own arm bays' near field (D-033.7). With the header bay's vapour at a backed-up
  arm-bay outlet they see 17.7 / 12.7 (#7).

**Seal-leak fire, 1 kg/s at the header bay:**
- PR9 40.4, PR11 99, PR13 156, PR2 end 1.81 (8);
- W2 0.39, R5 0.37 (5);
- hulls 1.60 / 1.68 (8);
- muster 0.02 (1.6);
- Z-PAD-A4SE 27.8.

This reproduces review 7 and the 240 min PFP scope of Class 150 (g).

**T-8102 in rain:**

| rain mm/h | boil-off kg/s | hull boxes B2 / B1, pool alone | + 1.05 kg/s | + 1.7 kg/s | turned hulls B2 / B1, pool alone |
|---:|---:|---|---|---|---|
| 0 | 0 | 4.5 / 4.1 | 6.6 / 6.0 | 7.9 / 7.2 | 3.7 / 3.6 |
| 2 | 0.67 | 5.8 / 5.3 | 7.9 / 7.2 | 9.2 / 8.4 | 4.8 / 4.6 |
| 5 | 1.67 | 7.8 / 7.1 | 9.9 / 9.0 | 11.3 / 10.2 | 6.5 / 6.2 |
| 10.4 | 3.48 | 11.5 / 10.4 | 13.6 / 12.4 | 14.9 / 13.5 | 9.5 / 9.1 |
| 20 | 6.68 | 17.9 / 16.3 | 20.1 / 18.2 | 21.4 / 19.4 | 14.9 / 14.3 |

The box values equal D-040.12. The 8 kW/m2 crossing is at 5.2 mm/h (box, pool alone), 2.1 mm/h (box,
with the collector vapour) and 7.7 mm/h (turned hull, pool alone). Distances from the sump centre:
hull boxes 28.8 / 30.2 m, turned hulls 31.6 / 32.3 m.

## Drawing
Not part of this layout review. No P&ID was reviewed; the P&IDs serve only as the source of the model.
For reference, the `cheme validate` count lines at HEAD:
- P-01, P-02 and P-03: all 0.
- P-04: `0 line-crossing (+3 accepted)`.
- P-05 and P-06: `3 offpage-not-on-edge` each. These are the carrier connections LNG-n011 / n013 /
  n014, left as warnings by D-039.9 (i).
- P-07: `(+6 accepted)`.
- P-08: `(+1 accepted)`.

## Layout
Commands run at HEAD ae718797 from the plant folder with core 1.11.0:
- `cheme layout build --check`: `layout/plant-model.yaml is up to date`. Its findings are the
  accepted ones listed below.
- `cheme validate`: `95 file(s): 0 error(s), 38 warning(s)`.
  - 32 warnings are HAZOP `hazop-input-changed` (H-01 to H-05, outside this scope; the restamp is the
    study owner's, D-038.5).
  - 6 are `offpage-not-on-edge` on P-05 / P-06.
  - The layout model findings are infos with their accept reasons. There are no `accept-unused`,
    `accept-stale` or `review-*` findings.
- `cheme check --stage detail`:
  - every layout gate is ok: layout-plot-plan, layout-3d, lifting-study, mto, layout-detail,
    electrical, hvac;
  - every `*-on-pid` gate is ok, including the new `dry-tank-area-sump-on-pid`,
    `independent-sump-trip-level-and-n2-station-limits-on-pid`, `permanent-shore-strainers-on-pid`
    and `refuge-intake-gas-trip-on-pid`;
  - it fails design-review (outside this scope) and layout-review (layout-7 names c257902c; this
    record at ae718797 replaces it).
- `cheme layout report`. The task's `cheme layout route report` is not a 1.11 command: `cheme layout
  route` takes no `report` argument, and `cheme layout report` is the report.
  - lines: every line routed, 317 of 317 segments, 0 skipped, 0 unrouted;
  - chains per method: astar 40, astar_coarse 2, open 8, pinned 208, rack 10, via 8. There are no
    `direct` and no `rack+direct` chains;
  - chains per reason: pinned 208; local pipe-way 17; above the pipe-way 11; intent via 8; short run
    9; open end 8; pump run at grade 3; rack longer than local_max_m 5; rack battery limit at a rack
    end 4; rack run too short 1; no rack in reach 1; rack crosses a road 1. Battery-limit ends: rule
    15, rack end 1;
  - rack fill:
    - PR1 46 / 27 %; PR2 28 / 26 %; PR3 10 / 24 %; PR4 33 %; PR5 16 / 6 %; PR6 21 / 10 %; PR8 4 %;
    - PR9 4.5 m 56 % (its 7 m tier, with the loading lines pinned, is still not reported);
    - PR10 1.9 m 105 %, accepted: the crossovers are counted along the section (true, two 1.21 m
      lanes on 5.0 m);
    - PR11 7 m 30 %;
  - model findings per rule, all accepted or info: operability 55, tray-span 45, support-missing 33
    (info), free-span 22, tray-zone 13 (the P-8103 one withdrawn), lifting 12, tier 5,
    tray-separation 3, escape-ways 2, escape-travel 2, laydown 2, clash-pipe-steel 1, clash-tray 1,
    rack-fill 1, and tray-rack 1 (validate);
  - these are 0: headroom, access-blocked, zone-crossing, separation, spacing, building-spacing,
    wall-penetration, vent-outlet, access-enclosed / -unconnected, ladder-clearance,
    walkway-riser, landing-width, egress-zone, operator-unknown, pad-overlap, zone-source,
    support-stub, steel-in-way and pipe-disconnected. Zero means only that nothing declared was hit.
    #2, #3, #4 and #6 trip none of them;
  - objects:
    - equipment declared 36; inline generated 215;
    - pipes generated 109 / pinned 208;
    - structures declared 8 and generated 0; platforms 0; zones declared 124;
    - supports 7,878; support steel 223;
    - trays 142; junction boxes 17;
    - cables 269 (power 27, instrument 242), none missing.
- **Rules missing from cheme-as-code**, for the cases no rule sees:
  - in-line item envelopes (the D-040 workaround is zones plus `build/rev8_env.py`) and the tee
    orientation;
  - a pipe's fall or drainability against a stated self-draining requirement (#2);
  - tray spans on rack tiers and on vertical links (#4);
  - a floating crane type in the lifting study;
  - pinned routes in the rack fill (PR9's 7 m tier).

**Rendered and read** (all under the plant folder, `build/`):
- `build/layout-plan.png`: the whole site; unchanged except the platform's south end.
- `build/layout-plan_crop-1140-850-1175-872.png`: the header bay in plan:
  - PR10's four bents outside the recess;
  - the low runs and berth headers stacked on lanes y 858.2 / 861.8, and the returns at x 1163.4;
  - PR11 / PR12 north-west of the bay;
  - S-HDR with its stair north-east;
  - PR13 along the south edge and onto the catwalk;
  - the in-line symbols at the tool's pitch: XV-4107 / XV-4103 at the drops' foot, XV-n101 /
    SR-n102 at x 1161.9 / 1160.9.
- `build/layout-section-y858.2_crop-1144--4-1172-10.png`: lane A (Berth 2) from the drop at x 1151
  (on HB-LNG4001-D) along the 2.51 m low run with both bottom takeoffs to the return, back west at
  4.99 m. The lift paths stand above 5.5 m. The recess is 3.4 m deep under it.
- `build/layout-section-y860_crop-1144--4-1172-10.png`: between the lanes. XV-4107's crossover is at
  1.10 m and XV-4103's at 0.83 m, each with its lift path. S-HDR's floor at 4.5 m runs x 1159.75-1164.25
  with its posts and a stair east.
- `build/layout-section-x1155.75_crop-852--4-870-9.png`: across the DN 800 crossover's U on its two
  stubs, with nothing over its lift path.
- `build/layout-section-x1158.9_crop-852--4-872-10.png`: across XV-4103's U, the strainer lift paths
  and S-HDR's west end beam; D-6101 to the north.
- `build/layout-section-x1161.1_crop-852--4-870-10.png`: through XV-n101. The low runs are at 2.51 m,
  the berth headers at 4.99 m and the aisle at 4.5 m between them; the lift paths are open. PR13's
  power tray is at 2.7 m south of the bay.
- `build/layout-section-x1153.95_crop-852--4-872-10.png`: line B's drop on HB-LNG4002-D; PR11's two
  bents, with the tray tier spanning 7.45 m between them (#4); PR13's first bent and the drops of
  the cable links.
- `build/layout-section-x1163.5_crop-798--15-870-12.png`: the jetty head:
  - T-8102 to -13 m with P-8103 on the cover (the stair artefact still inside);
  - the catwalk with PR13's canopy at 2.6 m (bents ~4.4 m apart) and its branch over the sump;
  - the catwalk collector;
  - S-HDR and D-6101 at the north end.
- `build/layout-section-x986_crop-3195--22-3260-12.png`: the T-8101 pit:
  - P-8102 on the cover strip, with W-8002 up to 7.97 m and onto PR8 (#2);
  - PR8's end bent and the feeder branch.
  The floor pocket is not modelled (civil, D-039.1).
- `build/layout-section-x953_crop-2930--5-3110-65.png`: T-2101 (92 m, 56 m), the column heads on
  the 57.4 m pump platform, and PR1 with its 7 / 10 m tiers and tray tier.
- `build/layout-section-y2945_crop-870--8-1120-62.png`: along PR1 from the tank area to the PR1 /
  PR2 / PR3 junction where the trestle starts, with the trough and pits; unchanged.
- `build/layout-level-S-T2101-TOP-PP_crop-875-2975-1010-3110.png` and
  `build/layout-level-S-T3101-TOP-PP_crop-735-2975-870-3110.png`: the pump decks, column-head zones,
  PSV zones and roof walkways; unchanged (review 3 #7).
- `build/layout-section-y3000_crop-1010--3-1100-20.png`: the BOG compressor area across K-7101B,
  the discharge header, Z-PAD-A2E and PR3; unchanged.

**Measured** (`cheme show <tag> --layout`):
- T-8102: P-8103 0.0 m, S-CW-A9 9.0 m, PR13 5.6 m, S-HDR 44.2 m, PR10 42.5 m, D-6101 51.6 m, R10
  86.0 m, B-JET 290.9 m.
- P-8102: T-8101 0.0 m, PR8 8.7 m, R13 27.0 m, R12 60.7 m.
- D-6101: PR9 1.0 m, PR10 4.1 m, PR11 4.0 m, S-HDR 5.9 m, LA-6101 8.5 m, R10 31.6 m.

## Checked and fine
- **Site geometry.** T-2101 (929.4, 3025.8) to LA-5102 (1137, 884) is 2,152 m ("about 2.1 km");
  T-2101 to FL-8101 (1484.9, 3102.8) is 561 m at 82 deg ("about 560 m east"). Unchanged.
- **Model against the P&IDs at HEAD.**
  - The model is current (`build --check`), and the layout-3d and `*-on-pid` gates pass.
  - The new P&ID items are in the model: SR-n102 as `Strainer`; LZT-8119, TSL-8104 / 8118 and
    LZT-8106 on JB-A9; HS-8103, LZT-8113, TSL-8102 / 8120 and AT-8124 on JB-A8-1; AT-8141A/B/C and
    UZ-8142..8144 on JB-SUB.
  - The in-line order on LNG-n001 S1 is XV-n101 then SR-n102, as on P-05 / P-06.
- **Header bay at real size.** All of these hold:
  - envelopes, lift paths and supports as above;
  - XV-n101's solenoids, reset and ZSC-n101 are 1.0-1.8 m above the S-HDR floor, 0.55 m from its
    handrail;
  - PDI-n102 is transmitted;
  - S-HDR has one stair, a 4.5 m dead end and occasional use, with the stair foot (x 1164.25-1166.05,
    y 864.1) 1.4 m from the D6101 bay kerb and outside Z-PAD-A4SE;
  - no foot stands in the recess;
  - the 1.9 m tier carries only the two low runs.
- **T-8101 / P-8102.**
  - The pump and pocket are re-rated (50 m3/h at 45 m, VSD in MCC-1 with its filter). The pump is
    lifted by davit from the cover strip and taken 27 m to R13.
  - The cables are in PR8's trays (C-M-P-8102 526 m, MC-JB-A8-1 521 m).
  - Each PR8 circuit's state on a burnt cable is named (D-039.9 (e)).
  - Its rainwater line is #2.
- **Jetty sump cabling.** The VSD feeder and the SIS multicore are in separate trays 1.04 m apart.
  JB-A9 stands outside the 6 m zone, and its loss is safe.
- **Hazardous areas and ignition sources.**
  - No tray, junction box or HPU stands in a zone other than the 13 accepted tray-zone entries.
  - The P-8103 branch over the sump runs at 2.7 m, above the zone's 1.0 m top.
  - B-JET, JB-JH and the UPS rooms are outside every zone and 200 m or more from the arms.
  - The floating crane pads are 6.0 / 5.7 kW/m2 from the other berth's bays (their safety-zone
    condition is #8 (c)).
- **Trays.** Fill is at most a few % on the platform racks. Power / instrument separation is kept
  (PR11 3.8 m, PR13 1.04 m). The ERS channels stay in separate PR2 trays. The tray-rack accept on
  PR2 is current.
- **Buildings and HVAC.** The hvac gate is ok. B-SUB's intake trip is drawn and in the C&E (I-811),
  with its placement in #6. B-JET is unchanged.
- **Racks and trestle.** Nothing on the trestle changed. LNG-4001 / 4002 are routed 2,213 / 2,357 m.
  PR9's lanes are unchanged.

## Not checked
- **The area classification itself** (CSA C22.1 / IEC 60079-10-1, competent person). Every zone is
  ASSUMED screening.
- **The LNG spill siting study** (CSA Z276 / NFPA 59A, cited by number only): SC-1, SC-2, SC-3, the
  pocket and standing-water RPT, the vapour dispersion. My screening is an order-of-magnitude check.
  Competent person.
- **Vendor data:** the DN 800 ESD valves, strainers and actuator packages (envelopes, weights,
  fire-stroke qualification); the MEWP and crane charts; the floating crane class. Valve vendor,
  MEWP and crane contractors.
- **Structural and stress:** PR10, PR11 (including the longitudinal bracing of its two bents), PR13
  and the posts on the catwalk and collector covers; the 180 deg returns, the drops on their base
  posts, cold contraction and anchors; the deck pads' outrigger loads. Structural, stress and marine
  engineers.
- **Marine:** the caisson, the deck level, the floating crane's mooring and pocket depth. Marine
  engineer.
- **Civil:** the T-8101 shaft and floor pocket, the Kitimat rainfall, the jetty drain outfall.
  Civil engineer.
- **Fire protection:** PFP products and ratings, foam on T-8101 / T-8102, the water curtain. Fire
  protection engineer.
- **HVAC detail:** the damper closure times and the refuge's ingress (#6). HVAC and F&G vendors.
- **Pinned routes.** Not every one of the 208 was read vertex by vertex. I read the header bay, PR9
  to PR13, W-8002, W-8003, the PR1 pits and the N2 stations, the basin and the BOG area.
- **Outside this scope:** the estimate and the MTO, the HAZOP (32 restamp warnings; studies owned by
  another agent) and the design review gate. `cheme diff main --list` was run, but the local `main`
  is older than 0b155d62 and lists whole sheets as added, so I used `git diff --stat 0b155d62
  ae718797` over this scope instead.
