---
topic: layout
reviewed_commit: c257902c
scope: [layout/, piping/routing.yaml, piping/pipe-specs.yaml, electrical/]
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: layout (3D model, routing, buildings, zones, electrical) after the response D-036 / D-037

Scope: `layout/` (site plan, buildings, structures, placement, zones, hvac, the generated
`layout/plant-model.yaml`, the lifting study), `piping/routing.yaml`, `piping/pipe-specs.yaml`
and `electrical/`. Read as basis, not reviewed: `DESIGN.md` D-001 to D-037 (mainly D-018 (p)-(t),
D-034.3, D-036 items 5 / 6 / 11, D-037 items 1-17), the `accept:` block of `checks/checks.yaml`, the
equipment, line and instrument lists, the C&E and sequences where the layout rests on them, the P&IDs
at HEAD as the source of the model, and the adversarial check of the previous round
(`build/adversarial-layout-r8.json`). I did not write this layout.

**Commit.** HEAD `c257902c` on `stage/lng-terminal-1-concept`, working tree clean when I started
(`git status --short` empty). The round is aedd8dbd (response D-034 / D-035), e71188c1 (HAZOP
revised), edf00cf0 (review records design-8 and layout-6) and c257902c (the response: D-036 design,
D-037 layout with D-037.15-17 on the dry jetty sump and P-8103). `git diff --stat edf00cf0 c257902c`:
87 files, among them the layout files (site-plan PR9 / PR10, structures S-HDR and the crossover stubs,
placement P-8103, zones, building, hvac), routing, pipe-specs, electrical, P-01 / P-03 / P-04 / P-05 /
P-06 / P-07 / P-08, the lists, C&E, sequences and the regenerated model. While I worked, other agents
edited `safety/hazop/H-01..H-04` and wrote `reviews/2026-11-05-basic-design-9.md` in the same folder;
the gate results below that depend on those files are marked.

**Verdict.** Both highs of review 6 are closed on the model.
- **Header bay (#1).** The DN 800 assembly now stands on the portal frame PR10 with no foot in the
  recess. Every run in the bay has supports in the model, and both crossovers rest on declared stubs
  either side of their valves. The aisle S-HDR has a stair and a caged ladder outside the recess, and
  the build generates no structure.
- **Trestle drain-down (#2).** The trestle-side tappings and the drain pump tie-ins are gone (T50K /
  T60K lie downstream of XV-n101 on the model). SEQ-LINE-EMPTY bounds the drain-down at ~36 m3 / ~3.5
  h, and T-8102 holds 170 + 40 = 210 of 257 m3, dry, with P-8103.
- **Adversarial check.** Its two missed highs are answered: the 240 min PFP and fire-tested valves of
  Class 150 (d) / (e), and the dry sump with its LAH hold and LAHH trip.
- **My screening.** It reproduces D-037.13 at every D-018 receptor class within ~0.1 kW/m2. The one
  exception is the arm-position walks, which I put higher (#6).

The fresh pass finds no new critical or high. It finds four mediums:
- **#1:** the DN 800 valve and strainer bodies with their actuators do not fit the 0.8 m aisle and the
  2.2 m between PR10's tiers as drawn, and nothing gives the shore ESD valves a removal path;
- **#2:** the header bay is drawn with centreline crossover takeoffs, which P-04 and the drain-down
  bound do not have. The author records that the frame must be rearranged for the drawn intent;
- **#3:** rain falling on LNG in T-8102 during the drain-down boils LNG at up to ~3.5 kg/s. That
  vapour is in no fire basis and puts the hulls at 10-13 kW/m2;
- **#4:** the whole-arm lift rests on an ASSUMED floating crane. This supersedes review 1 #2 and
  review 5 #9, as the adversarial check asked.

It also finds two lows (#5 cabling at the jetty sump, #6 screening statements and rule records).

No critical or high finding is open in this record or carried from an earlier one, so from the layout
side the arrangement can go to basic engineering with the mediums tracked. A merge is pending; it is
for a human or the reviewer, not the author.

## Findings
| id | area | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-layout-7#1 | A4 header bay (site-plan.yaml PR10, structures.yaml S-HDR, D-037.1 (c), D-037.15 (i)) | XV-5101 / XV-6101, SR-5102 / SR-6102 on LNG-5001 / LNG-6001 S1, the aisle S-HDR, the lifting study | **Envelopes.** The model places XV-n101 at x 1160.5 and SR-n102 at x 1159.5, 1.0 m apart on centres (`build/rev7_hdr.py`). The berth headers lie at y 858.9 / 861.1, 2.2 m apart, and the 0.8 m aisle runs between them (y 859.6-860.4), with 0.09 m between the aisle and each header's 80 mm insulation. The valves are 0.25 m symbols: cheme-as-code 1.7.0 places in-line items along the route and draws no body (D-029.18). At real size (vendor, ASSUMED) the arrangement does not fit. A DN 800 ball valve is ~1.5-2 m face to face with a ~1.5-1.7 m body, and a DN 800 T-strainer is larger, so the two cannot stand 1.0 m apart. Both berths' bodies sit at the same x, so they narrow the aisle from both sides to ~0.6 m or less. **Actuators.** With the stem up, an ESD actuator on a 4.99 m centreline reaches ~7 m, into PR10's top-tier beams (bottom ~6.7 m; beam mid-4 at x 1160.7 is 0.2 m from XV-n101). With the stem horizontal, it projects into the aisle. **Removal.** The beam at x 1160.7 and LNG-4001 / 4002 S7 (7.61 m, x 1158.4-1162) stand directly above XV-n101, so a vertical valve lift is blocked. The lifting study has no row for the valves. D-037.11 calls them "a few tonnes"; a DN 800 ESD ball valve with its actuator is ~8-15 t (ASSUMED). The strainer basket path through the gap x 1158.6-1160.7 does check out (~2 x 3 m clear). The rule set sees none of this. | medium | open | Stagger XV-n101 and SR-n102 along the 9.5 m header run (each berth's pair at a different x, valve clear of the top-tier beams), state the actuator orientation and the clear aisle width at each item with vendor envelopes, and record the valve removal path (lateral along the bottom tier to a lifting gap, or a top-tier beam made removable) with a lifting-study row from Z-PAD-A4E. Report the missing in-line envelopes to cheme-as-code. |
| 2026-11-05-basic-layout-7#2 | A4 header bay crossovers (routing.yaml LNG-4010 / LNG-4003 pins, D-036.11 (b), D-037.15 (k), D-037.16 (d)) | T4A4 / T4B4 (LNG-4003, DN 250), T4A5 / T4B5 (LNG-4010, DN 800), S-HDR | **The contradiction.** P-04, the line notes and the drain-down bound take both crossovers off the bottom of the loading lines. The layout draws them at the run centreline on PR10's top tier (x 1156.1 / 1158.4, 7.61 m). D-037.16 (d) calls this a modelling limitation, but D-037.15 (k) and 16 (d) themselves say that for this header bay it is "a rearrangement, not a modelling choice". A bottom takeoff of LNG-4010 puts the DN 800 crossover over the 4.5 m aisle with ~1.3-1.6 m headroom, and LNG-4003 below the beam it rests on. So the drawn frame and aisle cannot carry the takeoffs the P&ID requires. **Consequence for the bound.** For LNG-4010 (equal tee) the centreline branch has its invert at the run's invert, so nothing is lost. LNG-4003 is the crossover SEQ-LINE-EMPTY uses first. Its branch invert sits 0.27 m above the run's, which at the ~0.16 % fall of D-036.11 leaves a wedge of ~11 m3 per line (my integration of the segment area over ~170 m). Built as drawn, that wedge drains to the leak. The drain-down becomes ~47 m3 against the 40 m3 kept (the sump still holds it, 217 of 257 m3), and the leak is fed ~1.3 h longer, past the 240 min of PFP (Class 150 (d), ~0.5 h in hand). The author records the rearrangement for "the next layout pass", so medium, not high. | medium | open | Before the layout is issued, either draw the rearrangement D-037.15 (k) sketches (aisle shortened to XV-n101 / SR-n102, crossovers west of it on stubs from the bottom-tier beams with their valves ~2 m above the aisle), checked against #1. Or make LNG-4010 / XV-4107, whose centreline tee drains, the displacement path of SEQ-LINE-EMPTY, and record that the DN 250 takeoff may stay at the centreline (design owner, P-04). Report the missing tee orientation to cheme-as-code. |
| 2026-11-05-basic-layout-7#3 | A9 jetty sump T-8102 (zones.yaml Z-HA-SUMP-T8102 basis, D-037.15 (a), D-018 (s)) | T-8102 during the trestle drain-down in rain; P-8103, LZT-8106, TSL-8104 in the floor pocket | **Boil-off.** D-037.15 (a) makes "no LNG on standing water" binding, partly because "the boil-off of LNG on water and its higher burning rate are not in the vapour and fire basis". It then credits rain falling on LNG already in the sump during the ~3.5 h drain-down for lowering the volume. That is true of the volume. By D-037's own ~610 kJ/kg given up and ~510 kJ/kg latent heat, every kg of rain boils ~1.2 kg of LNG. At the ASSUMED 250 mm in 24 h on ~1,006 m2 (2.9 kg/s of water), the sump produces ~3.5 kg/s of vapour, three to four times the ~1 kg/s feed. My screening (`build/rev7_screen.py`) burns it at the sump: the hulls see 13.0 / 12.3 kW/m2 against 8, and 9.7 / 9.2 at half that rain. The catwalk sees 78, and the S-HDR aisle 5.0. The sump and its collector vapour alone give 6.3 / 6.0. **Ice.** The water freezes and sinks in LNG (~1.1 m3 of ice per m3 of rain, ~46 m3 in the design storm). It fills the floor pocket that holds P-8103's bowl, LZT-8106's stilling pipe and TSL-8104, so the dry-sump means is out of service until the ice melts. That is on the safe side for the next transfer (LAH / LAHH permissives), but it is not stated. This is a combined case (a seal leak during heavy rain at a wet coastal site), not a missing safeguard, so medium. | medium | open | Add the rain-driven boil-off at T-8102 during the drain-down to the fire and vapour basis (D-018 (s), D-037.13), screen it against the hulls and the catwalk, and pass it to the siting study as a named case with SC-1 / SC-2. Or show that the carriers are off the berth before it matters. State the ice in the pocket and the recovery of P-8103 / LZT-8106 / TSL-8104 after a spill in rain (design owner, marine engineer). |
| 2026-11-05-basic-layout-7#4 | A4 crane access for the arms (zones.yaml Z-PAD-A4W / -A4E, lifting-study.csv, D-037.11) | LA-5101..5104, LA-6101..6104 (40-45 t, 69.3 t of chart capacity at 6.3-13.0 m, up to 678 tm) | Successor of review 1 #2 (high, disputed closure) and review 5 #9 (low). The strips are now positions for a ~100 t class crane for D-5101 / D-6101 and arm parts. Whole arms are lifted by a floating sheerleg crane in the berth pocket with no carrier alongside (ASSUMED, the arm vendor's plan). That is credible industry practice. Nothing in the model or the lifting study shows it: the eight arm rows are still the nearest-pad rows from strips the record now says cannot take the lift, and they read "lane clear". The cover design over the bays is open with the structural engineer. The arrangement is not shown to work for the one heavy lift the original high was about. It is deferred with a stated reason to the vendor and the crane contractor, so medium. | medium | open | Arm vendor and crane contractor: confirm the floating crane's outreach over the arm risers (~15-20 m), the pocket depth and the mooring for it. Mark the eight arm rows of the lifting study as "floating crane, not this pad" in its notes until cheme-as-code can declare a floating crane (report it). Structural engineer: the covers for the ~100 t class. |
| 2026-11-05-basic-layout-7#5 | A4 / A9 cabling of the jetty sump (electrical-list.yaml JB-A4-2, checks.yaml accepts `layout-tray-span:PT-M-P-8103`, `layout-tray-zone:PT-M-P-8103+Z-HA-MANIFOLD-B2`, cable schedule) | C-M-P-8103 (VSD-fed, 3 kW), IC-LZT-8106 (I-805), IC-TSL-8104 / IC-TSL-8118 (I-808) | **The accepts.** Both P-8103 accepts are item-specific and quote the current 203.0 m. The route they state, though, is not in the model, and part of it conflicts with the project's own rules. In the model, PT-M-P-8103 runs from B-JET at 4 m along x 1131.6 beside the trestle. It then runs at 2 m down PR9's centre and through the header bay at y 861. From y 857 to 811 it runs at x 1159.6, west of the catwalk (x 1161-1166) over open water, and onto the sump cover at 2 m (`build/layout-plan_crop-1150-800-1180-830.png`). The stated route is PR2's and PR9's LV trays (PR9's tray PT-PR9-1 ends at y 874.5), then a catwalk handrail tray "with TSL-8104's". No such tray exists: IC-TSL-8104, IC-TSL-8118 and IC-LZT-8106 run 122-135 m from the sump to JB-A4-2 at the platform's north-east corner with no tray. **Separation.** A VSD-fed power cable in one tray with the SIS inputs of I-805 / I-808, the lockout of that same pump, goes against the power / instrument separation of `electrical/tray-rules.yaml`. **Fire.** The three SIS cables cross the header bay's 240 min fire zone. They are fail-safe on a burnt cable only if I-805 trips on a bad LZT-8106 signal, which is not stated. | low | open | Give the catwalk two trays (or a divided tray) for the P-8103 feeder and the sump instruments, state fire-resistant cable for LZT-8106 / TSL-8104 / TSL-8118 as D-035.5 does for the ESD cables, and confirm I-805's bad-signal action. Report the missing PR9-PR10 rack link to cheme-as-code (the tool cannot join them, D-037.16 (c)). |
| 2026-11-05-basic-layout-7#6 | screening statements and records (D-037.6, D-037.13, D-018 (t); site-plan.yaml / zones.yaml; control files) | deck walks from the arm work positions, the north-edge water curtain, the arm-position occupancy rule | **Walk values.** D-037.13 states 11.7 / 11.0 kW/m2 for the walks past 10 m. I take the review 6 walk paths (west or east edge, then the north edge) and burn the collector vapour at the nearest dry outlet downstream. That gives 15.4 (B2-A4) and 15.1 (B1-A4) (`build/rev7_check.py`). Along R9, the natural walk from the Berth 2 arms to W1, it gives 24.4. These are stated residuals either way, and the curtain's coverage (x 1130-1180, y 899-925) includes R9's north end. **Records.** The fixed water curtain is recorded only in DESIGN.md (D-018 (t), D-033.7, D-037.6): no zone, site-plan note or fire-protection list in the layout files holds it. The occupancy rule that keeps people off the arm positions during a steady transfer is, like review 6 #14's rule, in no control file. | low | open | Correct the D-037.13 walk rows (vapour at the nearest dry outlet; the R9 walk). Record the water curtain as a layout requirement (a zone note or a site-plan entry with its coverage), and carry both occupancy rules into SEQ-LOAD or the operating philosophy (design owner). |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-layout#2 | Road R5 blocked by B-PLAT; no crane access to the platform | high | superseded by 2026-11-05-basic-layout-7#4 | Road access by R9 / R10 and the strips exist. The whole-arm lift is reassigned to an ASSUMED floating crane that the model does not show (D-037.11). Carried as a medium, as the adversarial check asked, so the high is no longer closed on a condition rated low. |
| 2026-11-05-basic-layout#9 | Span screening classes LNG as gas | medium | open | Unchanged (pipe-specs.yaml notes); 22 free-span and 33 support-missing, each accepted by id. |
| 2026-11-05-basic-layout#13 | Unbuildable generated VP-* platforms | medium | closed e11eb12a | Disputed closure judged on the model. The VP-XV-4107 recurrence of review 6 is gone: `cheme layout report` gives structures declared 8, generated 0, platforms 0. XV-4107 / XV-4103 are declared remote operators maintained by exchange (routing.yaml). The recurrence was answered in c257902c. |
| 2026-11-05-basic-layout-2#3 | No flare radiation basis at B-SUB | medium | open | B-SUB unmoved; the derrick owner's contour is still owed (D-037.14). |
| 2026-11-05-basic-layout-2#5 | DN 800 / 900 LNG lines at 80 mm insulation | medium | open | The model still has LNG-5001 / LNG-6001 and LNG-4010 at 80 mm (`build/rev7_hdr.py`); pipe-specs.yaml unchanged. |
| 2026-11-05-basic-layout-2#6 | Loop bays unsized, loops not routed | medium | open | Unchanged; the stress engineer's. |
| 2026-11-05-basic-layout-2#8 | Dome-edge valves out of reach; XV-2123 / XV-3123 differ | medium | open | Roof nozzle platform still tank supply, not modelled (accept `operability:P-01/XV110[6-9]`). |
| 2026-11-05-basic-layout-2#10 | Oil-filled transformers inside B-SUB; no 69 kV bay or route | medium | open | Unchanged (D-037.14). |
| 2026-11-05-basic-layout-2#13 | PSV / vacuum valve inlet isolations at foot level | low | accepted: locked-open isolations operated only for valve change-out; in-line item placement not settable in cheme-as-code 1.7.0 (D-029.18); accepted by the author in f5d925f6, reviewers 6 and 7 concur | Unchanged. |
| 2026-11-05-basic-layout-2#14 | No site wind basis | low | open | `process/design-basis.yaml` has no wind, rainfall or ground entry. Those bases are ASSUMED in DESIGN.md (D-037.3, D-037.9) only. |
| 2026-11-05-basic-layout-2#15 | Drain and KO pump suction valves below deck or grade | low | accepted: model artefact of the in-line item placement of cheme-as-code 1.7.0 (D-029.18); accepted by the author in f5d925f6, reviewers 6 and 7 concur | Accepts `HV??1[57]` / `HV8106?` current. |
| 2026-11-05-basic-layout-3#4 | T-8102 without level, water removal or access | medium | closed c257902c | On P-08 and in the model are LZT-8106 (guided-wave radar in a stilling pipe to the pocket), P-8103 (vertical line-shaft pump, its motor at (1163.5, 809.7) on the cover) with W-8003 / CV-8116 / HV-8117, and TSL-8104 / TSL-8118 (1oo2 lockout I-808). The C&E has I-805 to I-808 (LAH 0.50 m hold, LAHH 0.60 m ESD-1); gate `dry-sump-pump-on-pid` ok. Access is from A9 with no transfer, the pump pulled by davit. HV-8117 stands 0.77 m outside the rim at 1.04 m. Residual: #3 of this record. |
| 2026-11-05-basic-layout-3#7 | Both roof exits beside the PSV outlets | medium | open | Roof clearing on high tank pressure still only in D-031.8; level plan `build/layout-level-S-T2101-TOP-PP_crop-875-2975-1010-3110.png` unchanged. |
| 2026-11-05-basic-layout-3#9 | Riser towers: clearance, members at the drops, 13 m posts | medium | open | Unchanged; left to the tank contractor. |
| 2026-11-05-basic-layout-3#10 | Accept reasons that do not match the model; FL-8101 lifting row | low | accepted: (a)-(c) fixed in 79d5c7ad; (d) the FL-8101 row cannot be marked as an unplanned lift in cheme-as-code 1.7.0 and the stack is maintained by the derrick hoist (D-027.14, D-031.11); accepted by the author in 79d5c7ad, reviewers 6 and 7 concur | Unchanged. |
| 2026-11-05-basic-layout-4#4 | Roads in the trough band, no fire approach, no fire protection | medium | closed 709fcf20 | Disputed closure (adversarial r8) judged on the model. It stood only if the pads passed the run-out. Now they do, as grated pits (review 6 #3 closed below). R1, the fire approach, is 7.34 kW/m2 in my design fire (D-037.13: 7.3), so the closure holds. |
| 2026-11-05-basic-layout-4#5 | Both ways off the platform at one corner; muster point exposed | medium | closed aedd8dbd | Disputed closure judged on the model: closed for pool fires at the way-off points. My best way, worst case, is 5.04 kW/m2 (NW manifold bay, header-class vapour; with the drain-rate vapour its items warrant, ~4.1 as before). It is 4.8 or less for every other bay, and the header bay is 1.44 / 1.53. Muster 0.17, every Berth 2 bay at once 1.15. The walks are review 6 #5 (closed below, values in #6 of this record); the release-point fire is review 6 #6. |
| 2026-11-05-basic-layout-5#6 | B-SUB at 69.7 m from the trough; intake gas detection only in DESIGN.md | medium | open | Still no detector, damper tag or C&E line (`control/instrument-list.yaml`, `cause-effect.yaml`: no AHU-1 intake trip). It weighs more now, because B-SUB is declared the temporary refuge (building.yaml, D-037.5) and its gas-tightness rests on that trip. Design owner. |
| 2026-11-05-basic-layout-5#9 | Crane strips over the tray bays | low | superseded by 2026-11-05-basic-layout-7#4 | D-037.11 reassigns the strips to a ~100 t class crane and the arms to a floating crane; the covers stay with the structural engineer. |
| 2026-11-05-basic-layout-6#1 | Header bay not buildable or operable as drawn | high | closed c257902c | PR10 bents at x 1151.5 / 1163.0, columns at y ~857.35 / 862.65 outside the recess (y 857.5-862.3). Supports in the model on every run in the bay: LNG-4001 / 4002 S5-S7 on PR10 mid-1..4 / stringers at 7 m and PR9 bent-4; LNG-5001 / 6001 S1 on PR10 at 4.5 m; LNG-4010 / LNG-4003 on stubs HB-LNG4010-1/-2 and HB-LNG4003-1/-2, two each, either side of the valve (`build/rev7_hdr.py`). Aisle S-HDR at 4.5 m (x 1154.82-1163.4) with a dog-leg stair east and a caged ladder west, both outside the recess. No generated structure. The N2 tees sit at y 864.4 and T50K at y 869.2, north of the bay; no post stands in the bay. The XV41?? accept is narrowed. Section `build/layout-section-x1159.5_crop-852--4.5-870-9.5.png`. New matter: #1, #2. |
| 2026-11-05-basic-layout-6#2 | Trestle drain-down unbounded, sump overflow onto the deck and water | high | closed c257902c | On P-04 / the model the DN 25 tappings are gone (PI-4105 / TI-4103 clamp-on at (1157.1-1157.7, 857.9)). LNG-5006 / LNG-6006 end at T50K / T60K on LNG-5001 / 6001 downstream of XV-n101 (flow from the drop at x 1162 west through XV-n101 at x 1160.5, then north). SEQ-LINE-EMPTY with N-4001 / N-4002, ~4,000 Nm3/h, gives a leak fed ~3.5 h, ~36 m3 (D-036.11 (b)). T-8102: 170 + 40 = 210 of 257 m3 (28.27 m2 x 9.09 m below the -3.91 m inlet, checked), dry by P-8103. PFP 240 min (Class 150 (d)). Open holds, honest as stated: the site N2 rate, the crossover actuator package and its fail position (P-04), the MEWP duty. New matter: #2, #3. |
| 2026-11-05-basic-layout-6#3 | Drip pads cannot pass the run-out; burning overflow at grade | medium | closed c257902c | Zones are now grated pits. My check, (q^2/g)^(1/3): critical depth 1.04 m in the 1.2 m XV-4101 gutter at 4.0 m3/s and 1.08 m in the 0.6 m XV-1102 gutter at 2.10 m3/s, so the XV-1102 pit stands at -0.33 m. The momentum balance of the lateral run-out entering the trough at 2.92 m normal depth gives 3.41 m: -0.20 m at x 1053 (pit -0.12 m with the drowned 1.2 m gutter at ~1.0 m/s) and +0.13 m at XV-4105, inside the 0.3 m kerb. No overflow at grade; R1 7.34. |
| 2026-11-05-basic-layout-6#4 | B-SUB occupants: no walk within 5 kW/m2, no refuge | medium | closed c257902c | Refuge declared with its basis in `layout/building.yaml`. My walk S1 -> R11 -> R1 -> R4 to the muster point: 6.39 in the design fire, 1.59 / 1.14 with the basin and the E / W pads only, 0.26 with the basin alone. The building is at 3.14, door S1 at 3.09. The gas-tight trip is review 5 #6 (open). |
| 2026-11-05-basic-layout-6#5 | Deck walks to the open way over 5 kW/m2 | medium | closed c257902c | D-037.6 records the north-edge water curtain as an ASSUMED requirement with its coverage, corrects the D-035.9 rows, and states the walk as a residual. Residual values and records: #6. |
| 2026-11-05-basic-layout-6#6 | Release-point fire and drift-off pool | medium | closed c257902c | Named siting-study cases SC-1 / SC-2. Basic-design position stated: no shelter at the arms (inside every bay's near field), and ESD-1 on confirmed detection for the design owner (D-037.7). My seal-leak and pool values do not change it. |
| 2026-11-05-basic-layout-6#7 | T-8102 caisson in the tidal zone | medium | open | Concept recorded (double wall, monitored annulus, anchorage for ~2.2 MN), zones basis and D-037.8. The design is still the marine engineer's hold, and the tank-type stair is still drawn on T-8102 (section `build/layout-section-x1163.5_crop-795--15-935-25.png`). |
| 2026-11-05-basic-layout-6#8 | T-8101 shaft, ground basis, pit cover, P-8102 head | medium | closed c257902c | Ground basis ASSUMED (groundwater at grade, ~39 MN; pi x 64 x 19.5 x 10 kN/m3 = 39.2 MN checked), shaft concept, grated cover only over the south 3 x 16 m strip, fixed foam (zones basis). P-8102 re-rated 50 m3/h at 44 m for the 19.5 m pit (D-036 item 3). The basis lives in DESIGN.md / zones.yaml, not in design-basis.yaml (review 2 #14). |
| 2026-11-05-basic-layout-6#9 | Item drip tray detectors not on the P&IDs | medium | closed c257902c | TSL-3124 (P-03) and TSL-7115 (P-07), gate `line-empty-and-sump-level-on-pid` ok; cabled IC-TSL-3124 to JB-T3101 (98 m) and IC-TSL-7115 to JB-K7101 (66 m). |
| 2026-11-05-basic-layout-6#10 | ERS channels A / B in common trays | medium | closed c257902c | Model: PT-PR2-B-2 carries C-F-ERS-5100A / 6100A, PT-PR2-C-2 carries C-F-ERS-5100B / 6100B; channel B ends at F-ERS-n100B, 2.5 m from the HPU panel. Accept `layout-tray-rack:PR2` (three power trays) item-specific. |
| 2026-11-05-basic-layout-6#11 | PSV-1122 inlet on PR6 against Class 150 (a); welded-run notes | low | open | Exception stated in Class 150 (f). The line list carries the weld notes on LNG-4001 / 4002 / 4003 / 4010 only, not on the Class 150 (a) / (b) tank-area and riser lines (design owner). |
| 2026-11-05-basic-layout-6#12 | Jetty-head ESD stations cabled to the platform boxes | low | closed c257902c | HS-n100B / n107B to JB-JH at the B-JET north door (5-6 m cables, cable schedule); IT-JB-JH accept item-specific. |
| 2026-11-05-basic-layout-6#13 | Model and accept hygiene | low | closed c257902c | 0 `accept-unused`, 0 `accept-stale`. XV41?? narrowed to `XV41[03][1256]`, PT-HPU-5100 reason current, Z-PAD-A4E span 4.75 m, site-plan header-bay comments 4.7 / 3.7. The rack fill now reports PR9 4.5 m 56 % and PR10 7 m 99 %; PR9's 7 m tier (four pinned DN 800) is still unreported, as is the tank-type stair (both reported to cheme-as-code). The outlet geometry is a detail note. |
| 2026-11-05-basic-layout-6#14 | South-end occupancy rule in notes only; PDI-n102 local | low | open | No occupancy rule in `control/sequences.yaml`, `control/philosophy.md` or `process/narrative.md` (grep). PDI-n102 still local (design owner, D-037.12). |

Adversarial-check items raised against review 6 (`build/adversarial-layout-r8.json`), judged on the model:
- **Missed high, header-bay fire protection.** Answered. Class 150 (d) puts PFP / a jacket for 240 min
  of pool fire on PR10, PR9's south bay (y 857-874.5), every line, the valve bodies, actuators,
  switches, cables and strainer covers. Class 150 (e) requires fire-tested valves (API 607 / ISO 10497)
  and, since D-037.15 (c), a crossover actuator package qualified to stroke after 60 min of fire. My
  seal-leak fire (1 kg/s, 17.5 MW at the bay) gives PR9's south bay 40.4, PR9 north of y 874.5 7.7, the
  PR2 end 1.8, the ways off 0.4, the hulls 1.8 / 2.0 and the muster point 0.03, so the 240 / 60 min
  split holds. The duration (~3.5 h against 240 min) holds only with the bottom-of-line takeoffs (#2).
- **Missed high, T-8102 rain / dry sump.** Answered by the fixed dry-sump pump P-8103 with the LAH
  hold and the LAHH ESD-1 trip. T-8102 now holds the design spill with no rain allowance (210 of 257
  m3). What the binding basis leaves out, rain falling on LNG already in the sump, is #3.
- **Missed medium, the operator declarations.** Answered. XV-5101 / XV-6101 are within reach of S-HDR
  (4.99 m on the aisle's 4.5 m floor). XV-4103 / XV-4107 are declared remote operators maintained by
  exchange from a MEWP on Z-LAY-A4SE (outreach ~8.6 / ~10.9 m from x 1167). That MEWP duty is left open
  for the operating owner.
- **Disputed closures.**
  - Review 1 #2, crane access: upheld as a gap and now superseded by #4 (medium).
  - Review 4 #4, R1 fire approach: closed holds, since the pits pass the flow.
  - Review 4 #5, walks: closed for pool fires at the way-off points, walks in #6.
  - Review 1 #13, generated platforms: closed holds, with 0 generated structures.

Items left open with a reason, judged against the rating standard:
- **Release-point fire SC-1 / drift-off pool SC-2 and ESD on detection.** Honestly carried, and
  closed here as review 6 #6, because the basic-design position is stated.
- **Site N2 4,000 Nm3/h, the crossover actuator package and its fail position, the MEWP duty.**
  Stated holds with owners. The pipe spec states plainly that the case returns to the siting study if
  no package qualifies. These are honest at the level the author gives them; #2 is the part that
  belongs to the layout.
- **Caisson, shaft, covers, PFP products, water curtain, Kitimat rainfall, P-8103 vendor data.**
  Deferred to their engineers with a reason; none hides a hazard the layout must answer, except the
  rain boil-off (#3), which no deferral mentions.
- **Bottom-of-line takeoffs ("known modelling limitation", D-037.16 (d)).** Partly mislabelled: the
  author's own text says the header bay must be rearranged. Rated medium as #2, because the
  rearrangement is sketched and an alternative exists.

Accepts in `checks/checks.yaml` (layout rules). Each names its items or a pattern limited to named
tags; none is a rule wildcard, and none is stale or unused.

New entries:
- support-missing: LNG-n006 S4, N-400[12] S1, BOG5002, LNG5007, LNG6007, DR5006, DR6007, FL7003 S2,
  W8002 S1;
- tier: DR-n005 @ PR9;
- tray-span: IT-JB-JH, PT-UPS-?-?, PT-MCC-2-?, PT-PR2-PR3-?, PT-M-P-8103;
- tray-zone: PT-M-P-8103;
- tray-rack: PR2;
- the narrowed operability `XV41[03][1256]`.

All are item-specific and true on the model, with one exception. The two P-8103 accepts describe a
cable route the model does not hold, and part of it would put a VSD-fed power cable in the SIS
instruments' tray (#5).

## Site-wide radiation screening (my check of D-037.13)
- Script `build/rev7_screen.py` (with `build/rev7_check.py`), written for this review from the
  D-018 statement and the zones as they stand, not from the author's r11 / r12 or review 6's rev6
  scripts. The method is the point source q = 1.2 x 0.35 x 0.078 x 50 MJ/kg x A / (4 pi R^2), tau 1,
  plan distance R >= 1 m. Troughs and gutters are 0.25 m line elements of 1.365 MW/m2 times their
  width; collector vapour is 0.35 x m_v x 50 MJ/kg at a point.
- Volumes and flows:
  - tank area: run-out 4.0 m3/s (D-034.3); every open leg, both gutters (the XV-4101 gutter at 1.2 m),
    the 201 m2 basin and the worse of the two pit clusters;
  - platform: one bay (cells of the bays as zones.yaml subdivides them, 29.7-36 m2), the 28.27 m2 sump,
    and 1.05 kg/s of vapour (1.7 kg/s for the header bay, at any bay outlet it backs up to) at the
    sump or the worst dry outlet downstream;
  - drain-down: 1 kg/s for ~3.5 h at the header bay (D-036.11 (b)).
- **Tank-area design fire.** My values, with the criterion in brackets:
  - tanks and towers (8): T-2101 4.11 and T-3101 1.09; S-RT2101 4.40 and S-RT3101 1.28;
  - racks (8): PR6 north 7.95 (my footprint from y 2980; D-037: 6.0); PR6 east leg to x 1060 7.80;
    PR5 1.29; PR2 south of y 2910 6.80; PR3 east 7.39; PR4 north of y 3273 7.52;
  - buildings: B-SUB 3.14, S1 3.09, B-ANA 3.65 (5); TX bays 2.74 (8);
  - roads (8): R1 7.34; R11 5.96; R4 0.58; R12 7.42; R2 east 7.43; R8 east 7.07. R2 west is 6.95 to
    x 1050 and 8.36 at x 1060, at the trough band's edge (D-037: 7.0), so the band's limit is a choice,
    not a failure;
  - stand-offs (8): crane pads and laydowns at the tanks 3.51; Z-LAY-A8W 6.33;
  - escape and muster: Z-ESC-A2N-W 4.92, Z-ESC-A2N 4.22, stair towers 2.27 (5); Z-ESC-A1-MUSTER
    0.49 (1.6);
  - process equipment (8): K-7101A / B / C 7.55 / 8.45 / 10.55 (water spray, D-035.3); D-7101 4.88;
  - junction boxes (8): JB-PR1 5.38, JB-A2-2 7.11, JB-K7101 6.21, JB-A1-1 4.90, JB-T2101 3.43,
    JB-T3101 1.08, JB-TR-N 2.89, JB-IA 2.65.

  Over their criterion and stated as residuals: JB-A8-1 56.7, R3 14.3, R6 16.0, R13 26.1, R8 west
  11.9, the R5 stub 18.9, Z-PAD-A2E 21.0, Z-LAY-A2E 39.4. These are the D-037.13 values.
- **B-SUB walk:** 6.39 in the design fire; 1.59 at the refuge exit (basin and pads), 0.26 with the
  basin alone.
- **Platform, one bay.**
  - ways off: best way 1.44-5.04 (5.04 at the NW Berth 2 manifold bay, the B2-M8 case, ~4.1 with
    drain-rate vapour); W1 / W2 per bay in the script output;
  - muster point / boat route: 0.17 / 0.17 at most; 1.15 / 1.14 with every Berth 2 bay at once;
  - HPU-5100 / HPU-6100: at most 7.87 / 7.74;
  - JB-A4-1 / JB-A4-2: at most 7.82 / 7.69;
  - ERS channel B boxes B2 / B1: 9.17 / 9.02, for the B2-A4 / B1-A4 arm bays. The author's
    one-bay row gives 7.0 / 6.7, and its two-bay sensitivity 10.3 / 9.3. My value is over 8 with the
    vapour at the nearest dry outlet. These boxes stand 2.5 m south of the HPU panels by D-037.10, and
    D-037.15 (j) leaves moving them north to the electrical engineer. Recorded here as a note, not a
    new finding: the A-channel panel beside each box is at 7.9 / 7.7 for the same fire, so one channel
    survives at the criterion's margin;
  - JB-JH 0.17;
  - hulls: in the near field of their own berth's bays (D-018 (e)); sump and vapour alone 6.29 / 5.96
    (8).
- **Seal-leak fire, drain-down:** see the adversarial-check item above. **Rain on LNG in the sump:**
  #3. **Deck walks:** #6.

## Drawing
Not part of this layout review. No P&ID was reviewed; the P&IDs serve only as the source of the model.
For reference, the `cheme validate` count lines at HEAD are all 0. The accepted ones are P-04
`0 line-crossing (+2 accepted)`, P-07 `(+2 accepted)` and P-08 `(+1 accepted)`.

## Layout
Commands run at HEAD c257902c from the plant folder with core 1.7.0
(`/Users/arturschweidtmann/Developer/LNG/.venv17/bin/cheme`):
- `cheme layout build --check`: `layout/plant-model.yaml is up to date`.
- `cheme validate` (clean tree): `93 file(s): 0 error(s), 20 warning(s)`. All 20 warnings are HAZOP
  `hazop-input-changed`, outside this scope. The layout model findings are infos with their accept
  reasons. There are no `accept-unused`, `accept-stale` or `review-*` findings.
- `cheme check --stage detail`, run while other agents were editing `safety/hazop/H-01..H-04` and
  writing `reviews/2026-11-05-basic-design-9.md`:
  - every layout gate ok: layout-plot-plan, layout-3d, lifting-study, mto, layout-detail,
    electrical, hvac, the `*-on-pid` gates including `dry-sump-pump-on-pid` and
    `line-empty-and-sump-level-on-pid`;
  - fails: pids-valid (2 errors, from those uncommitted HAZOP edits; a later
    `validate --only 'cheme.hazop-*'` shows them in the working tree), design-review (outside scope)
    and layout-review (layout-6 names aedd8dbd; this record at c257902c replaces it).
- `cheme layout report` (the task's `cheme layout route report` is not a 1.7.0 command; `cheme layout
  report` is the report):
  - lines: 151 lines and 317 segments, all routed; none skipped; 0 unrouted;
  - chains per method: astar 40, astar_coarse 2, open 8, pinned 208, rack 10, via 8. There are no
    `direct` and no `rack+direct` chains;
  - chains per reason: pinned 208; local pipe-way 17; above the pipe-way 11; intent via 8; short run
    9; open end 8; pump run at grade 3; rack longer than local_max_m 5; rack battery limit at a rack
    end 4; rack run too short 1; no rack in reach 1; rack crosses a road 1. Battery-limit ends: rule
    15, rack end 1;
  - rack fill: PR1 46 / 27 %; PR2 28 / 26 %; PR3 10 / 24 %; PR4 33 %; PR5 16 / 6 %; PR6 21 / 10 %;
    PR8 4 %; PR9 4.5 m 56 %, its 7 m tier not reported; PR10 4.5 m 40 %, 7 m 99 %;
  - model findings per rule, all accepted or info: operability 55, tray-span 45, support-missing 33
    (info), free-span 22, tray-zone 14, lifting 12, tier 5, tray-separation 3, escape-ways 2,
    escape-travel 2, laydown 2, and tray-rack 1 (validate);
  - these are 0: clash-*, headroom, access-blocked, zone-crossing, separation, spacing,
    building-spacing, wall-penetration, vent-outlet, access-enclosed / -unconnected,
    ladder-clearance, walkway-riser, landing-width, egress-zone, operator-unknown, pad-overlap,
    zone-source, support-stub, steel-in-way and pipe-disconnected. Zero means only that nothing
    declared was hit; #1 and #2 trip none of them;
  - objects: equipment declared 36; inline generated 213; pipes generated 109 / pinned 208;
    structures declared 8 and generated 0; zones declared 113; platforms 0; penetrations 0; supports
    7,886; cables 256 (power 27, instrument 229), none missing.
- Rules missing from cheme-as-code, for the cases no rule sees: real in-line item envelopes (body,
  face to face, actuator) against walkways and steel (#1); tee orientation for bottom-of-line takeoffs
  (#2); a rack link between two racks whose strips do not touch (PR9 / PR10, #5); pinned routes in the
  rack fill (PR9's 7 m tier).

Rendered and read (all under the plant folder, `build/`):
- `build/layout-plan.png`: the whole site, unchanged in layout.
- `build/layout-plan_crop-1140-850-1172-872.png`: the platform's south end, showing:
  - PR10 with its four columns outside the recess;
  - S-HDR between the berth headers, with the dog-leg stair east and the ladder west;
  - XV-n101 and SR-n102 1.0 m apart at the same x for both berths (#1);
  - the crossovers on the top-tier beams;
  - the drum bays and PR9's columns on the kerbs;
  - the PT-M-P-8103 branch through the bay (#5).
- `build/layout-plan_crop-1150-800-1180-830.png`: A9, showing:
  - T-8102 with the tank-type stair artefact;
  - P-8103 at the cover's south edge;
  - W-8003 east at 0.8 m, with CV-8116 / HV-8117 at and outside the rim, the riser to 2.6 m and the
    T-post at x 1170.1 to the battery limit at x 1174, A9's east edge 1174.5;
  - the modelled feeder tray west of the catwalk over the water (#5).
- `build/layout-level-S-T2101-TOP-PP_crop-875-2975-1010-3110.png` and
  `build/layout-level-S-T3101-TOP-PP_crop-735-2975-870-3110.png`: the pump decks, column-head zones,
  PSV zones and roof walkways, unchanged.
- `build/layout-section-y2997_crop-870--8-1120-62.png`: from T-2101 across PR6 and JB-PR1's drop to
  the BOG area and PR3. There is nothing at grade under PR6.
- `build/layout-section-y2945_crop-870--8-1120-62.png`: along PR1 from the tank area to the
  PR1 / PR2 / PR3 junction where the trestle starts: the trough from x 975, the XV-4105 and XV-4101 /
  4102 / 4106 pits at their new depths, and the PR6 and PR3 joints.
- `build/layout-section-x1163.5_crop-795--15-935-25.png`: jetty head, showing:
  - T-8102 to -13 m with P-8103 on the cover (and the stair artefact);
  - the catwalk S-CW-A9 at +0.3 m over the catwalk collector;
  - the south collector and the HDR chamber;
  - PR10 with the S-HDR stair east of its east bent;
  - D-6101, the B1M collector, PR9 and the PR2 end.
  The jetty muster point Z-ESC-A4-MUSTER (x 1113-1131, y 1118-1130, at B-JET) is unchanged and lies
  off this section line. It is screened above (0.17 at most).
- `build/layout-section-x1159.5_crop-852--4.5-870-9.5.png`: through SR-n102. The loading lines at
  7.61 m (y 857.9 / 862.1), the berth headers at 4.99 m (y 858.9 / 861.1), the 0.8 m aisle floor at
  4.5 m between them, the 3.4 m recess below, and the feeder tray at 2 m crossing the bay (#1, #5).
- `build/layout-section-x1095_crop-2880--8-3260-18.png`: along the re-routed collector from the PR1
  junction under PR3 / PR4 past R7 and R2 to the corner at y 3237.5.
- `build/layout-section-y3237.5_crop-960--21-1110-14.png`: the west leg into the 19.5 m basin
  (stair artefact inside it).
- `build/layout-section-x1050_crop-2930--3-3065-18.png`: PR1 with the pits and the trough zone,
  K-7101C / B / A in their seal zones, and the PR6 east leg.

Measured (`cheme show <tag> --layout`):
- P-8103: T-8102 0.0 m (centres 2.3 m), S-CW-A9 14.0 m, S-HDR 49.7 m, PR10 47.4 m, B-JET 296.0 m.
- T-8102: S-CW-A9 9.0 m, PR10 42.4 m, PR9 51.4 m, D-6101 51.6 m, PR2 75.2 m, R10 86.0 m, B-JET
  290.9 m.
- B-SUB: R8 2.0 m, PR7 1.0 m, R11 7.0 m, R3 45.1 m, PR3 63.0 m, PR2 63.8 m, PR1 70.1 m, B-ANA
  84.6 m, K-7101C 110.8 m.

## Checked and fine
- **Site geometry against D-013 and the task basis.** T-2101 (929.4, 3025.8) to LA-5102 (1137, 884)
  is 2,152 m ("about 2.1 km"). T-2101 to FL-8101 (1484.9, 3102.8) is 561 m at 82 deg ("about 560 m
  east"). Unchanged.
- **Model against the P&IDs at HEAD.** The model is current (`build --check`). The layout-3d and
  `*-on-pid` gates pass. The new P-08 items are in the model: P-8103, W-8003, CV-8116, HV-8117.
  LNG-5006 / 6006 end downstream of XV-n101. N-4001..4004 are at PR1, with the inner blocks at grade
  reach over the pit and the trough.
- **PR10 / S-HDR.**
  - The frame does not block a way off (the ways start at y 925).
  - Crane reach from Z-PAD-A4E to the bay is ~9-12 m.
  - The stair and ladder land outside the recess. From the ladder foot a walk runs north under PR9
    between the drum and manifold bays to R10.
  - Headroom on the aisle is 2.5 m to the top-tier lines.
  - The strainer basket gap (x 1158.6-1160.7, ~3 m in y) is clear.
- **P-8103 and W-8003.**
  - Static head ~16 m from the pocket (-13.5 m) to the 2.6 m high point matches the ~20 m rating.
  - The riser drains back through CV-8116's hole and the overhead run falls to the free drop.
  - HV-8117 is within reach of A9.
  - Nothing stands above the pump; the modelled tray ends 1.3 m north of it.
  - The motor is Ex d in the sump's zone 2.
  - A9 and the catwalk are kept clear in transfers.
- **Pits and gutters.** Hydraulics reproduced (review 6 #3 above). The burning surfaces are unchanged
  in the screening.
- **Refuge.** B-SUB 3.1 kW/m2, the exit walk 1.6 or less after the trough phase.
- **Hazardous areas and ignition sources.** No tray, junction box or HPU stands in a zone other than
  the 14 accepted tray-zone entries. B-JET, JB-JH and the UPS rooms are outside every zone and 200 m
  or more from the arms.
- **Electrical rooms and trays.** The electrical and hvac gates are ok. The ERS channels are in
  separate trays, PR2 carries three power trays on brackets (accept item-specific), and the jetty-head
  stations are on JB-JH.
- **Racks and trestle.** Nothing on the trestle changed except the tank-end N2 stations. LNG-4001 /
  4002 are routed 2,205 / 2,352 m.

## Not checked
- **The area classification itself** (CSA C22.1 / IEC 60079-10-1, competent person). Every zone is
  ASSUMED screening.
- **The LNG spill siting study** (CSA Z276 / NFPA 59A, cited by number only): SC-1, SC-2, the
  drain-down and its rain-driven boil-off (#3), the vapour dispersion. My screening is an
  order-of-magnitude check. Competent person.
- **Vendor envelopes and weights** of the DN 800 ESD valves, strainers and actuator packages (#1), and
  their fire-stroke qualification. Valve vendor.
- **Structural and stress:** PR10's 11.5 m stringer span with four DN 800 lines and two ESD valves,
  the crossover stubs, the B1M cover under the S-HDR stair and PR10's east bent, the A9 T-post and the
  davit, and pipe stress and loops. Structural, stress and marine engineers.
- **Marine:** the caisson, the frost-free pocket, the deck level, the collectors against the wave
  crest, and the floating crane's mooring (#4). Marine engineer.
- **Civil:** the T-8101 shaft, the Kitimat design rainfall, the jetty drain outfall. Civil engineer.
- **Fire protection:** the PFP products and ratings, the water curtain, the A2 water spray, foam.
  Fire protection engineer.
- **Pinned routes:** not every one of the 208 was read vertex by vertex. I read the header bay, PR9,
  PR10, W-8003, the PR1 pits and N2 stations, the basin, and the BOG area.
- **The estimate and the MTO** (they leave out the civil quantities, D-037.14), the HAZOP (20
  warnings; studies being edited by another agent) and the design review gate: outside this scope.
