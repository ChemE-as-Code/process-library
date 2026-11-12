---
topic: layout
reviewed_commit: 546486794c289ec5c16600356c90c5adf782a1f7
scope: [layout/, piping/routing.yaml, piping/pipe-specs.yaml, electrical/]
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: layout (3D model, routing, buildings, zones, electrical) after the response D-027

Scope: `layout/` (site plan, buildings, structures, placement, zones, hvac, the generated
`layout/plant-model.yaml`, the lifting study), `piping/routing.yaml`, `piping/pipe-specs.yaml`
and `electrical/`. Read as basis, not reviewed: `DESIGN.md` D-001 to D-027, the `accept:`
entries of `checks/checks.yaml`, `piping/line-list.yaml` and `equipment/equipment-list.yaml`.
I did not write this layout.

**Commit.** HEAD `54648679` ("P&IDs, BFD/PFD and 3D model rebuilt with core 1.7.0"), on
`stage/lng-terminal-1-concept`, rebased on `origin/main` (19 commits ahead), clean working
tree. The rebase rewrote the earlier ids: the working tree that 2026-11-05-basic-layout
reviewed on `0603eeed` was committed as `fa3304be` (layout pass), and the response to that
review is `e11eb12a` (DESIGN.md D-027). `0603eeed` is no longer an ancestor of HEAD, which is
why `cheme check` fails `layout-review` on the earlier record. HEAD itself changes only the
P&ID drawings (actuators moved off the pipes), the BFD/PFD and the provenance digests of
`layout/plant-model.yaml`: no route, placement or list changed.

**Verdict.** The response closes 17 of the 18 earlier findings on model evidence, and accepts
one as a tool limitation (#9). The two stated deviations are acceptable as modelling
workarounds. The layout is **not ready to issue for basic engineering**. Two new findings are
high: the in-tank pump removal path that the accepted lifting and laydown findings rest on is
ruled out by the model's geometry (#1), and the LNG impoundment sump stands 5 m from the riser
rack, 8 m from the main rack and 15.6 m from tank 1 (#2). Eight new findings are medium and
five are low. A merge is pending; it should wait until #1 and #2 are closed.

## Findings
| id | area | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-layout-2#1 | A1 tank roofs (layout/structures.yaml, checks/checks.yaml, DESIGN.md D-027.7) | P-2101A-D, P-2102, P-3101A-D, P-3102; T-2101 / T-3101 `lift_weight`; accepts `layout-lifting:T-[23]101`, `layout-laydown:laydown-T-[23]101`, `layout-lifting:P-[23]101?`, `layout-laydown:laydown-P-[23]101?` | Ten pump lifts and four laydowns are accepted on "a 10 t pump-removal gantry crane over the pump wells [that] ... sets it down on the platform and lowers it to grade with the same crane". The model rules this out. (a) The pump platform deck is x 930.5-961.0 (structures.yaml extent), while the T-2101 shell is at x 975.4 (centre 929.4, radius 46). The deck edge is 14.4 m inside the shell and about 10 m above the dome there, so a gantry over the wells at x 941-953 cannot reach outside the shell to lower anything to grade. (b) The equipment list gives T-2101 / T-3101 `lift_weight: 12` t ("in-tank pump with its column cable reel"). The lifting study makes that 13.86 t gross and 18.48 t needed, which is more than the 10 t gantry. (c) At grade there is no drop zone or laydown for a lowered pump. The obvious side, east of the shell where the pump columns are, is taken by the PR6 riser rack 5.6 m off the shell (`cheme show T-2101 --layout`) and by the sump T-8101 (#2). No mobile crane pad is declared at grade either; from road R1, 45.8 m off the shell, a lift to the columns would mean roughly 90-100 m radius at ~65 m hook height. The response to 2026-11-05-basic-layout#4 therefore leaves pump removal, the most frequent heavy maintenance lift of the terminal, without a feasible path, and the accepts that rest on it are not supported. | high | open | Decide the pump removal concept with the tank and pump vendors (ASSUMED until then) and model it. One option is a roof crane on a runway that reaches past the shell edge, with a declared drop zone and a laydown at grade that are kept clear of PR6, PR1 and the sump. The other is a large mobile crane at grade, with its pad, its access road and its radius, hook height and capacity in the lifting study. Make the crane capacity cover the declared `lift_weight`. Rewrite the four accepts and D-027.7 to the chosen concept. |
| 2026-11-05-basic-layout-2#2 | A1 impoundment (layout/equipment-placement.yaml, layout/zones.yaml, layout/site-plan.yaml) | T-8101, Z-HA-SUMP-T8101, PR6, PR1, T-2101 | The LNG spill impoundment sump T-8101 (centre 968, 2968, 6 m deep) collects a 10 min spill of one loading line (D-018). It stands 5.0 m from the PR6 riser rack, which carries the T-2101 roof piping: the DN 800 pump header, the fill lines and the vapour header. It is 8.0 m from PR1, which carries both loading lines, both vapour returns and the circulation lines, and 15.6 m from the T-2101 shell (`cheme show T-8101 --layout`). The only separations declared for it are B-SUB ≥ 150 m and the 3 m zone 2. A pool fire or vapour cloud at the sump would therefore engulf the riser and the main rack, and expose the tank roof piping and the outer tank. The sump is meant to take spills away from the tanks and racks, and here it brings them to their junction. No thermal radiation or dispersion basis (CSA Z276 / NFPA 59A) is cited for the position. | high | open | Move the impoundment basin away from the tanks, PR1 and the riser racks, to a distance set by a pool fire radiation and vapour dispersion screening (CSA Z276 / NFPA 59A, cited by number). Re-route the troughs Z-KC-TROUGH-* to it. Declare separations from the sump to T-2101, T-3101, PR1, PR5 and PR6 with that basis, and record the siting in DESIGN.md (D-018). |
| 2026-11-05-basic-layout-2#3 | A6 / A3 (layout/site-plan.yaml, layout/building.yaml) | B-SUB (control room CR-1), FL-8101 derrick | The re-siting of B-SUB (D-027.4) brought the occupied control and switchgear building east, to 316.0 m from the flare derrick. The site boundary is 314.3 m from the derrick (`cheme show FL-8101 --layout`), and the 5.0 kW/m2 that D-018 and S-10 give is the fence-line value. The derrick also carries the trains' flares, which are outside this scope (D-001). Nothing measures or limits the flare radiation at B-SUB: there is no separation B-SUB to FL-8101 and no radiation basis. A continuously occupied building at about the fence-line distance may see far more than the levels usually allowed for unprotected personnel. | medium | open | Get the flare radiation contour of the derrick (all four flares at their governing case) or a screening estimate. Add a separation B-SUB to FL-8101 with that basis. If the contour reaches B-SUB, move it back west or south, which also bears on the siting distances of D-027.4. |
| 2026-11-05-basic-layout-2#4 | A2 (piping/routing.yaml, layout/zones.yaml, DESIGN.md D-027.12) | BOG-7002 S1-S6, road R7, Z-PAD-A2E | D-027.12 gives the BOG area's east way out as road R7. Between the compressor row and R7 / the crane pad Z-PAD-A2E, the discharge header BOG-7002 (DN 300, 80 mm insulation) runs north-south at a 2.0 m centreline along x 1059.5 from y 3012 to 2978 (model points). Its underside is at about 1.76 m, which makes a 34 m barrier at head height (plan `build/layout-plan-z0-3_crop-1005-2955-1090-3062.png`, section `build/layout-section-x1050_crop-2925--2-3065-20.png`). The "no-walk strip" covers only y 2975-2979, so this run is outside it. Operators at the machines reach R7 only by ducking under or climbing over the header. The escape rules saw nothing, because no escape zone is declared on the east side. | medium | open | Raise the header run so it clears 2.2 m (or ≥ 2.1 m under the insulation), or route it west of the machines. Otherwise declare step-over platforms. Declare the east way out as an escape zone, so the headroom rule checks it. |
| 2026-11-05-basic-layout-2#5 | piping/pipe-specs.yaml, piping/line-list.yaml | LNG-1001 / 1002 / 1003 / 1004 (DN 900 rundown and fills), LNG-2001 / LNG-3001 (DN 800 pump headers), LNG-4006 (DN 800 crossover) | Only the trestle lines LNG-4001 / 4002 and BOG-4001 / 4002 get the D-012 thicknesses. Every other cold line takes 80 mm, including the DN 900 rundown header (1,040 m on PR4 and PR1) and the DN 800 lines of the same loading service, for which D-012 says 200 mm. Their outside diameters are about 0.24 m too small. That flows into the lanes and clearances on PR1, PR4, PR5 and PR6, the raised-shoe tier accept of BOG-1001, the rack fill (PR1 tier 7 m 46 %) and the take-off. | medium | open | Give the line list an insulation type with a thickness for the DN 800 and DN 900 LNG lines (200 mm per D-012, or the value of a stated basis) and for the large vapour lines. Rebuild, re-pin the centrelines that rest on a tier, and re-run the rack fill. |
| 2026-11-05-basic-layout-2#6 | PR2 trestle (layout/zones.yaml Z-LOOP-01..12, piping/routing.yaml) | LNG-4001 / 4002, BOG-4001 / 4002 | The loop bays are 16 x 16 m, ~150 m apart, and their size is ASSUMED with no estimate behind it. A guided-cantilever screening of a DN 800 loop gives about 25 m legs. That takes 2.9 mm/m (D-027.13) over 150 m, so ~0.44 m per loop and ~0.22 m per leg, E ~195 GPa, and a displacement stress range of ~170 MPa (ASSUMED austenitic steel). Four lines nested in one bay need more still. The lines are also not routed through the bays: the model runs them straight. So the ~1.5 km of DN 750 / 800 pipe and ~100 large elbows of the loops are missing from the lengths, the take-off, the heat ingress and the trestle structure. | medium | open | Size the loops with the stress engineer (or a screening calculation recorded in DESIGN.md) before the trestle width and the bay piling are fixed. Enlarge Z-LOOP-* to suit. Route or pin the four lines through the bays, so the MTO and estimate carry them. |
| 2026-11-05-basic-layout-2#7 | checks/checks.yaml | accepts `layout-tray-span:PT-M-*`, `layout-tray-span:IT-JB-*`, `piping/line-list.yaml#layout-line-route:*` | The free-span wildcard is gone (2026-11-05-basic-layout#10), but three accepts still cover a whole family or rule, present and future. `PT-M-*` and `IT-JB-*` cover 33 of the 38 tray-span findings. Their reason ("brackets off the riser and rack columns and short posts") does not fit the longest runs. PT-M-K-7101B runs 51.5 m at 18 m elevation along x 1041 across the BOG area and then drops 17 m to the skid; PT-M-K-7101C runs 40 m and PT-M-K-7101A 26.5 m the same way. IT-JB-K7101 runs 41 m. PT-M-P-8101A / B run 51 m and 36.8 m at 15.5 m across the sterile flare area A3. There are no columns there, and an 18 m tray needs its own structure (or a trench or buried route, which A3's radiation favours). `layout-line-route:*` accepts every present and future line-route estimate. Its eight current findings are routed (`cheme layout report`), but a new unroutable line would be accepted unseen. | medium | open | Declare cable support steel (a tray rack across A2, posts, or a trench or buried route, buried across A3) and rebuild, or accept the A2 / A3 trays one by one with a reason that fits them. Replace `layout-line-route:*` by the eight ids. |
| 2026-11-05-basic-layout-2#8 | A1 tank roofs (piping/routing.yaml operators, checks/checks.yaml `layout-operability:P-0?/XV*`) | XV-1106, XV-1107, XV-1108, XV-1109 (52.3 m), XV-2123 (51.5 m), XV-3123 (12.7 m) | The tank fill, bottom-fill and circulation return valves sit at the dome edge (nozzles N1, N2, N8 at r ≈ 40 m, x ≈ 966), 5 m below and 5.4 m outside the pump platform. The floor below them is grade, 52 m down (`layout-operability` findings). They are actuated, and rollover control and ESD rest on them. The accept says they are "maintained from the rack, the platform or a mobile elevating work platform". No such platform reaches 52 m over a dome edge, and no roof platform is declared at these nozzles. The same in-line valve also sits differently on the two identical tanks: XV-2123 is on the T-2101 roof and XV-3123 at 12.7 m on PR5. | medium | open | Declare a roof nozzle platform at the fill and circulation nozzles, reached from the roof walkways, or move the nozzles under the pump platform. Place XV-2123 / XV-3123 alike. Narrow the `XV*` accept to the valves really maintained from the racks, with the arm ERS valves kept by their own pattern. |
| 2026-11-05-basic-layout-2#9 | A1 tank roofs (layout/zones.yaml) | pump column heads P-n101A-D / P-n102, column vents BOG-n011..n015 (HV-n161..n165), roof nozzles | The only roof zone is Z-HA-TANK-PSV, around the relief outlets at 62.6 m. The column heads (cable penetration seals, head plates, flanged discharges) and the column vents have no zone. Yet the line list says the column vent "releases N2 with traces of methane at the tank roof, inside the roof hazardous area" (BOG-2011, D-026.9, H-02 A3). The 6.6 kV pump junction boxes on the head plates, the motor trays and the pump-removal crane all stand there, so the `layout-tray-zone` rule and the Ex selection have nothing to check against. | medium | open | Declare zones from sources at the column heads and column vents (and the roof manholes and nozzle flanges), as the area-classification table gives them (ASSUMED until the classification). Rebuild, and accept or fix the tray-zone findings that appear. |
| 2026-11-05-basic-layout-2#10 | A6 (electrical/electrical-list.yaml, layout/building.yaml) | TR-1 / TR-2 (69 / 6.6 kV, 10 MVA), TR-3 / TR-4 (1.6 MVA), B-SUB 30 x 20 m | SS-1 puts two 10 MVA 69 / 6.6 kV transformers and two 1.6 MVA transformers "in B-SUB". The same 600 m2 building also holds the 6.6 kV switchgear, MCC-1, the control room CR-1 and its rack room. Oil-filled transformers of that size normally stand outdoors in bays, with fire walls, oil containment and separation from occupied rooms. The two 69 kV incomers also need a switchyard or cable termination, and a route from the site grid. None of this is on the plot, and the building area has not been checked against what it holds. | medium | open | Add outdoor transformer bays (fire walls, oil pits) and the 69 kV incomer bay beside B-SUB, with their separations from CR-1, or record dry-type units with their basis. Size B-SUB from a room list (switchgear line-ups, MCC, UPS and batteries, CR-1, rack room, HVAC). Route the 69 kV supply to the plot edge. |
| 2026-11-05-basic-layout-2#11 | layout/structures.yaml, estimate/mto.md | S-T2101-TOP, S-T3101-TOP | The modelling artefact of the tank-top platforms (one level of a 96 x 96 m frame on four 57.4 m corner columns outside the shell, D-027.7) is carried into the take-off as real steel. Structure HEB500 is 16 members, 691.2 m, 129.3 t (`estimate/mto.md`). The roof stools, walkways, the gantry crane and the stair towers' real steel are not separated from it. The file's closing note also says the platforms are "modelled as unclad building levels (layout/building.yaml)", which contradicts the structures it declares. | low | open | Exclude the artefact frames from the MTO and estimate (or replace them with an allowance for the tank-top steel from the tank supply), and correct the note. Report to cheme-as-code that a structure cannot stand on an item (the missing rule or feature behind the workaround). |
| 2026-11-05-basic-layout-2#12 | layout/zones.yaml, checks/checks.yaml `layout-escape-ways:S-T[23]101-TOP/PP` | Z-ESC-Tn-ROOF-SE, Z-ESC-Tn-ROOF-N, S-ESC-Tn | The escape accept says the platform's two ways down are the roof walkways. In the model neither walkway meets the platform. ROOF-SE ends at y 3013, while the deck starts at y 3016.5, a 3.5 m gap. ROOF-N lies at x 927-930, while the deck starts at x 930.5 and ends at y 3044, so they only touch at a corner, 0.5 m apart. ROOF-N ends at y 3071.5, and the S-ESC landing starts at y 3072.2 (level plan `build/layout-level-S-T2101-TOP-PP_crop-875-2975-985-3080.png`). The T-3101 roof is the same. | low | open | Extend the walkway zones to meet the deck and the stair tower landing, so the model shows the connection the accept describes. |
| 2026-11-05-basic-layout-2#13 | A1 tank roofs (piping/routing.yaml) | HV-2134A-C / HV-3134A-C (57.596 m), HV-2135A-B / HV-3135A-B (57.564 m) | D-027.7 puts the relief and vacuum valve inlet isolations "within 1.8 m of the floor". The DN 250 valve centres are 0.16-0.20 m above the 57.4 m deck, so the valve bodies straddle the grating and the handles are at foot level. | low | open | Lift the floor locally (a step) or pin the inlet spool so the valve centre is ~0.8-1.2 m above the deck, with the PSV and its tailpipe above it. |
| 2026-11-05-basic-layout-2#14 | DESIGN.md (basis of layout/hvac.yaml, layout/zones.yaml) | AHU-1 / AHU-2 intakes, tank PSV outlets, analyser vent | There is still no prevailing wind or wind rose in DESIGN.md. The B-SUB intake faces east, towards the derrick, and the B-JET intake faces west. Neither choice, nor the relief and analyser vent positions, can be checked against the wind. | low | open | Record the site wind basis (seasonal directions, with its source). Then check the air intakes upwind of the vents, the derrick and the tank roofs. |
| 2026-11-05-basic-layout-2#15 | checks/checks.yaml `layout-operability:P-0[56]/HV??1[57]`, `P-08/HV8106?` | HV-5115, HV-6115, HV-8106A, HV-8106B (-0.1 m), HV-5117 (7.2 m) | Four valves are modelled 0.1 m below the deck or grade. The accepts say they are worked "from grade" or will be "at the pump nozzles at deck level" at detail engineering. The model shows neither. These are the jetty drain pump suctions and the KO drum pump suctions. | low | open | Pin the suction spools so the valves sit above the deck or grade at the pump nozzles. Then drop the two accepts. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-layout#1 | B-PLAT (TR-5, MCC-2) inside the 200 m ignition-free radius of the arms | high | closed e11eb12a | B-PLAT removed. TR-5, MCC-2 and RR-2 are in B-JET (building.yaml): 206.6 m from LA-5104, 210.5 m from LA-6104, 218.6 m from LA-5102 (`cheme show B-JET --layout`, `cheme show LA-5102 --layout`). Eight separations "LA-n10x to B-JET ≥ 200 m" are in site-plan.yaml, and validate gives 0 `layout-separation`. B-JET is 10.3 m from PR2; see Not checked for the trestle. |
| 2026-11-05-basic-layout#2 | Road R5 end blocked by B-PLAT; no crane access to the deck strips | high | closed e11eb12a | Roads R9 (to Z-PAD-A4W) and R10 (under the PR2 end between its bents, to Z-PAD-A4E) are declared. Laydown Z-LAY-A4NW is west of R9. `layout-headroom` 0. Lifting study: all eight arms "lane clear". |
| 2026-11-05-basic-layout#3 | Occupied B-SUB 4 m off the rack junction, beside the analyser and the valve station, no zones there | high | closed e11eb12a | B-SUB is east of R3: 63.0 m from PR3, 63.8 m from PR2, 70.1 m from PR1, 84.6 m from B-ANA, 110.8 m from K-7101C, 189.0 m from T-8101 (`cheme show B-SUB --layout`). Zones Z-HA-PR1-VALVES, -PR2-VALVES, -ANALYSER, -SUMP-T8101 / -T8102 and the troughs are declared, with seven separations. The consequence study is still owed (Not checked); the new flare distance is #3 of this record. |
| 2026-11-05-basic-layout#4 | No tank-top pump platform, roof walkway or second way off the roof; valves beyond reach; VP stairs inside the tank | high | closed e11eb12a | S-T2101-TOP / S-T3101-TOP PP at 57.4 m; walkways Z-ESC-Tn-ROOF-S / -SE / -N; north stair towers S-ESC-Tn; the PSVs, vacuum valves and their inlet isolations are on the deck; no HV-n15x / n16x operability finding; no VP-* structure (report: `structures:declared 4`, none generated). Level plans `build/layout-level-S-T2101-TOP-PP_crop-875-2975-985-3080.png` and `build/layout-level-S-T3101-TOP-PP_crop-735-2975-850-3080.png`. Split: the pump removal crane and laydown are not feasible as modelled, now 2026-11-05-basic-layout-2#1 (open). The walkway gaps are #12 and the valve heights #13. |
| 2026-11-05-basic-layout#5 | Roads R3 / R6 not connected; no road into A2; Z-PAD-A2E reached under an undeclared crossing | medium | closed e11eb12a | One network in site-plan.yaml: R3 to R2 under the PR3 east leg between its bents, R6 to R5 under PR2, R7 into A2 to Z-PAD-A2E, R8 to B-SUB (plan crop `build/layout-plan_crop-860-2900-1210-3090.png`). `layout-headroom` 0. The east exit is blocked at head height by a pipe: #4 of this record. |
| 2026-11-05-basic-layout#6 | Each berth's 200 m zone holds the other berth's carrier; no SIMOPS basis | medium | closed e11eb12a | D-027.5 states the basis: two carriers alongside, one transferring, the other under terminal control in the zone (ASSUMED reading of S-01, to be confirmed by the TERMPOL / TIG review). zones.yaml Z-SZ-B1 / B2 say the same. |
| 2026-11-05-basic-layout#7 | 11 `direct` and 1 `via+direct` chains, roof headers unsupported | medium | closed e11eb12a | `cheme layout report`: astar 46, astar_coarse 3, open 8, pinned 181, rack 9, via 8, with no `direct` and no `via+direct`. Posts on the pump platform are declared (RS-T2101-3, RS-T3101-3, -4). The remaining support-missing infos (66) are the dome-edge spans, accepted as info (D-027.7). |
| 2026-11-05-basic-layout#8 | 80 mm insulation on every cold line, against 200 / 150 mm in D-012 | medium | closed e11eb12a | `piping/pipe-specs.yaml`: 200 mm on LNG-4001 / 4002 and 150 mm on BOG-4001 / 4002. Trestle section `build/layout-section-y2342_crop-1095-0-1145-20.png` shows the thicker rings. The other DN 800 / 900 LNG lines are still at 80 mm: #5 of this record. |
| 2026-11-05-basic-layout#9 | Span screening classes LNG as gas | medium | accepted: cheme-as-code takes liquid or gas from the fluid name, and pipe-specs has no field to override it; the support design spans the LNG lines as liquid at detail engineering (D-027.10). Accepted by the author in e11eb12a; this reviewer concurs, provided the report to cheme-as-code is filed (none is cited yet) | Every free-span finding still reads "DN … gas"; the schema has no class override. |
| 2026-11-05-basic-layout#10 | Wildcard accepts free-span:* and tray-span:*; an unused accept | medium | closed e11eb12a | Twelve free-span entries cover the 16 findings by id or narrow pattern (no `cheme.accept-stale`). The unused `laydown-FL-8101` is gone (no `cheme.accept-unused`). The tray-span families and `layout-line-route:*` are still too wide: #7 of this record. |
| 2026-11-05-basic-layout#11 | No escape zones; low BOG corridor; single way off the platform and roofs | medium | closed e11eb12a | Z-ESC-A2S (under PR1 to R1), Z-ESC-A4S (muster and escape-to-sea), and the tank roof walkways are declared. The low corridor y 2975-2979 is a no-walk strip (D-027.12). Residuals: #4 (east exit) and #12 (walkway gaps). |
| 2026-11-05-basic-layout#12 | No space for cold contraction of the 2.45 km lines | medium | closed e11eb12a | Z-LOOP-01..12 keep-clear bays east of the trestle, and D-027.13. Their size and routing: #6 of this record. |
| 2026-11-05-basic-layout#13 | 98 VP-* proposals, some unbuildable; arm envelopes not declared | medium | closed e11eb12a | No generated structure (report). Operators are declared in routing.yaml (remote, chain wheel, extension spindle). Z-KC-ARMS-B1 / -B2 keep-clear zones are declared (section `build/layout-section-y888_crop-1110--14-1200-42.png`). |
| 2026-11-05-basic-layout#14 | No DESIGN.md entry for the layout pass | medium | closed e11eb12a | D-027 items 1-16. |
| 2026-11-05-basic-layout#15 | B-SUB comment "> 100 m" against 91.0 m measured | low | closed e11eb12a | The comment now says 110 m, and 110.8 m is measured. |
| 2026-11-05-basic-layout#16 | FL-8101 accept cites a derrick hoist that D-017 does not give | low | closed e11eb12a | D-027.14 records the hoist (ASSUMED); the Z-PAD-A3 basis and the accept cite it. |
| 2026-11-05-basic-layout#17 | Spill troughs and sumps not modelled, no zone or separation | low | closed e11eb12a | Z-KC-TROUGH-PR1 / -PR2 / -SUMP, Z-HA-SUMP-T8101 / -T8102, separation B-SUB to T-8101 ≥ 150 m (189.0 m measured). The trestle drip trays are not modelled (axis-parallel zones, D-027.4). The sump's own position: #2 of this record. |
| 2026-11-05-basic-layout#18 | Reviewed files uncommitted on 0603eeed | low | closed fa3304be | The layout pass was committed as fa3304be (after the rebase) and the response as e11eb12a. This record names HEAD 54648679 as `reviewed_commit`. |

## Drawing
Not part of this layout review. No P&ID was reviewed; the P&IDs serve only as the source of the
model. For reference, the `cheme validate` count lines at HEAD are all 0. The accepted ones are
P-04 `0 line-crossing (+2 accepted)`, P-07 `(+2 accepted)` and P-08 `(+1 accepted)`.

## Layout
Commands run at HEAD 54648679, from the plant folder, with core 1.7.0:
- `cheme layout build --check`: `layout/plant-model.yaml is up to date`.
- `cheme validate`: `82 file(s): 0 error(s), 23 warning(s)`. All 23 warnings are
  `hazop-input-changed` (outside this scope). Every layout model finding is reported as info
  with its accept reason. There is no `accept-unused`, no `accept-stale` and no `review-*`.
- `cheme check --stage detail`: ok layout-plot-plan, layout-3d, lifting-study, mto,
  layout-detail, electrical, hvac, control-complete, datasheets and the on-sheet gates. FAIL
  design-review (the three design records name pre-rebase commits; outside this scope) and
  FAIL layout-review (2026-11-05-basic-layout names 0603eeed, not an ancestor of HEAD; this
  record replaces it).
- `cheme diff main --list`: 1,054 lines. All are P&ID and BFD/PFD items, the eight sheets
  and both process diagrams being added on the branch. The layout files are not in the item
  diff.

`cheme layout report`:
- Lines: every line is routed and none is skipped (BOG-1004 is routed now). Unrouted: 0.
- Chains per method: astar 46, astar_coarse 3, open 8, pinned 181, rack 9, via 8. There are
  no `direct` and no `rack+direct` chains.
- Chains per reason: pinned 181; local pipe-way 21; local above the pipe-way 10; local short
  run 9; intent via 8; open end 8; local pump run at grade 4; rack battery limit at a rack
  end 4; rack longer than local_max_m 4; local rack run too short 3; local no rack in reach
  1; local rack detour too long 1; rack crosses a road 1. Battery-limit ends: rule 16, rack
  end 1.
- Rack fill: PR1 7 m 46 % / 10 m 28 %; PR2 31 % / 26 %; PR3 10 % / 24 %; PR4 7 m 33 %;
  PR5 12 m 16 % / 14 m 6 %; PR6 21 % / 10 %. PR1 and PR4 are understated by #5.
- Model findings per rule (all accepted): operability 54, support-missing 66 (info),
  tray-span 38, free-span 16, lifting 13, laydown 10, tray-zone 6, tier 4, tray-separation 3,
  escape-ways 2, escape-travel 2, clash-pipe-steel 1 (DR-5006 through the PR2 bay-256
  stringer, a DN 25 small-bore take-off). These are 0: the other clash-* rules, headroom,
  access-blocked, zone-crossing, separation, spacing, building-spacing, wall-penetration,
  vent-outlet, access-enclosed / -unconnected, ladder-clearance, walkway-riser,
  landing-width, egress-zone, operator-unknown, pad-overlap, zone-source, support-stub,
  steel-in-way and pipe-disconnected. Several zeros mean only that nothing was declared:
  #4, #9.
- Objects: equipment declared 35, inline generated 198, pipes generated 127 / pinned 181,
  structures declared 4 (no generated VP-*), zones declared 58.

The two stated deviations:
- **Tank-top platform as one level of a frame on four 57.4 m corner columns** (D-027.7,
  structures.yaml): acceptable as a modelling workaround. A cheme-as-code structure cannot
  stand on an item, and a post on the dome intersects the tank solid. The columns stand
  outside the shell (1.8 m from the sump T-8101, clear of PR6, the stairs and the roads), and
  no rule result that matters rests on them other than the escape accepts. Conditions: the
  take-off must not carry the frame (#11), and the walkways must really meet the deck (#12).
  The deviation does not cover the pump removal (#1).
- **Column-head valves on chain wheels and extension spindles** instead of within 1.8 m of
  the floor: acceptable. HV-n151A-D / HV-n152 are at 60.0 m, 2.6 m above the 57.4 m deck.
  They are worked only when a pump is taken out of service, with a chain wheel. The column
  vents HV-n161..n165 are opened only after an N2 displacement, with an extension spindle.
  Both are within 6 m and infrequent, and the model answers all twenty: none appears in
  `layout-operability`. The piping stays at 60 m to keep 2.1 m headroom over the deck, which
  is the stated reason.

Accepts in `checks/checks.yaml` (layout rules), my view of each:
- `lifting:T-[23]101`, `laydown:laydown-T-[23]101`, `lifting:P-[23]101?`,
  `laydown:laydown-P-[23]101?`: not supported (#1).
- `lifting:FL-8101`, `lifting:D-5101`, `lifting:D-6101`: real reasons (the derrick hoist per
  D-027.14; one flanged spool in the lane).
- `operability:P-0?/XV*`: a class reason (actuated, no manual duty) that is real for the rack
  and arm valves, but it does not answer the maintenance access of the roof valves (#8).
  `FV*`, `TV*`, `PV1110`, `PV1111`, `PV8132`, `FO*`: real reasons.
- `operability:P-0[56]/HV??1[57]`, `P-08/HV8106?`: they defer to detail engineering what a pin
  can show now (#15).
- `line-route:*`: whole-rule wildcard (#7).
- Free-span entries (12): one per finding or a narrow pattern, each with its location; the
  quoted lengths are current (no accept-stale).
- `tier:P-04/Line_LNG6006_S1@PR2` (10.6 m, current), `tier:P-01/Line_BOG1001_S[568]@PR6`
  (raised shoes): real reasons. The second rests on 80 mm on BOG-1001 (#5).
- `clash-pipe-steel:P-05/Line_DR5006_S1+PR2/bay-256/stringer-7-1-2`: real (field-run small
  bore).
- `escape-ways` / `escape-travel:S-T[23]101-TOP/PP`: real reason (the frame artefact; tank roof
  travel against the site standard, ASSUMED), but see #12.
- `tray-separation` (2), `tray-zone` (4): real reasons (cover plates; Ex glands, ASSUMED until
  the classification).
- `tray-span:PT-HPU-5100`, `PT-F-SS2-?`, `PT-MCC-2`, `IT-RR-2`, `*-PR?-PR?`: real reasons.
  `PT-M-*`, `IT-JB-*`: too wide, and the reason does not fit the A2 / A3 runs (#7).

Rendered and read (all under the plant folder):
- `build/layout-plan.png`: the whole site. The tank area, BOG area and flare in the north;
  the 2 km trestle with the twelve loop bays; B-JET at the trestle about 200 m north of the
  platform; the 200 m circles at the berths.
- `build/layout-plan_crop-860-2900-1210-3090.png`: T-2101, the BOG area, B-SUB and the road
  network. The sump T-8101 sits between the T-2101 shell, PR6 and PR1 (#2). The corner
  columns of the S-T2101-TOP frame are visible outside the shell, and R7 / R8 are joined to R3.
- `build/layout-level-S-T2101-TOP-PP_crop-875-2975-985-3080.png` and
  `build/layout-level-S-T3101-TOP-PP_crop-735-2975-850-3080.png`: the pump platform decks,
  the five column heads, the PSV zone 1 circles at the deck's west edge, the walkways that
  stop short of the deck (#12), and the roof headers to PR6 / PR5 past the deck's east edge.
- `build/layout-section-y3030_crop-870--5-1110-75.png` and
  `build/layout-section-y3030_crop-915-38-1000-68.png`: from the tank across the BOG area to
  the trestle junction. Dome to 56 m, deck at 57.4 m, column-head piping at 60 m, PSV
  tailpipes to 62.6 m (zone 1 from ~59.6 m, above the deck headroom), the drops on PR6 to its
  12 / 14 m tiers, PR1 and PR3 at 7 / 10 m. The deck ends 14 m inside the shell (#1).
- `build/layout-section-y888_crop-1110--14-1200-42.png`: the jetty head. Arm risers to 22 m,
  the arm keep-clear boxes between the risers and the ship envelopes, the PR2 head frame and
  the platform piping at 3-4 m, the drain drums and pumps on the deck.
- `build/layout-section-x1050_crop-2925--2-3065-20.png` and
  `build/layout-plan-z0-3_crop-1005-2955-1090-3062.png`: the BOG compressors. Suction and
  discharge piping at 1.5-2 m round the machines, with BOG-7002 at 2.0 m between the row and
  the crane pad (#4). PR1 and the PR6 east leg at the ends.
- `build/layout-section-y2342_crop-1095-0-1145-20.png`: trestle cross-section at loop bay 4.
  DN 800 lines on the 7 m tier and DN 750 lines on the 10 m tier with the D-012 insulation,
  the power tray at 13.5 m, and the loop bay drawn as an empty box east of the rack, with no
  loop routed in it (#6).

Measured (`cheme show <tag> --layout`): B-JET to LA-5104 206.6 m, to LA-5102 218.6 m, to PR2
10.3 m, to R5 2.3 m. B-SUB to K-7101C 110.8 m, B-ANA 84.6 m, PR3 63.0 m, PR2 63.8 m, PR1
70.1 m, T-8101 189.0 m, FL-8101 316.0 m. T-2101 to PR6 5.6 m, R1 45.8 m, R2 46.2 m, A2
34.6 m. K-7101C to T-2101 76.5 m. T-8101 to PR6 5.0 m, PR1 8.0 m, T-2101 15.6 m. FL-8101 to
the site boundary 314.3 m, to PR3 54.1 m. LA-5102 to PR2 9.1 m, R9 15.5 m.

## Checked and fine
- Site geometry against D-013: T-2101 (929.4, 3025.8) to LA-5102 (1137, 884) is ~2,152 m at
  ~174 deg (D-013: 2,147 m at 174 deg). T-2101 to FL-8101 is ~561 m at ~82 deg (D-013:
  561 m at 82 deg, "about 560 m east"). PR2 runs ~1,983 m at ~178 deg (D-013: 1,982 m at
  178 deg).
- Separations of the site plan are kept, with 0 `layout-separation`. Tank to tank is 48 m
  shell to shell against 46 m (NFPA 59A practice, cited only), tank to BOG compressors 76.5 m
  against 30 m, and the arms to B-JET ≥ 206.6 m against 200 m.
- The 200 m ignition-free radius at the berths: nothing non-Ex is declared on the platform
  (HPUs and drain pump motors are Ex, ASSUMED). The marine zones stay on the water, and the
  deck is measured by separation, as D-027.3 records.
- Roads: one connected network with crossings under PR2 and PR3 between bents, crane pads in
  A2 and A4 on roads, and fire access to A2 from the east (R7) and the south (R1). The east
  way out on foot is blocked by #4.
- Rack arrangement: liquid low and vapour high, the riser racks' 12 / 14 m tiers above
  PR1 / PR3, the R2 portal under PR4, and fill ≤ 46 %.
- Platform: R9 / R10 to both crane strips, laydowns at the four corners, the muster point
  and escape-to-sea station at the south edge, and the arm keep-clear zones with no fixed
  steel in them. Lifting study: arms "lane clear"; the drain drums are blocked only by their
  own inlet spools (accepted).
- Electrical: one cable to every motor and instrument (gate `electrical` ok), the jetty fed at
  6.6 kV to B-JET with 400 V platform feeders of ~220-240 m, the instrument home runs to RR-2,
  and the B-SUB cable bridge PR7 with its bents clear of R3.
- Buildings: B-ANA is in its own zone 2 beside the vapour switch station. B-JET is outside
  every hazardous zone and outside the 200 m radius. The B-SUB intake (east) and exhaust
  (south) are 13 m apart; the wind basis is #14.
- Consistency with the P&IDs at HEAD: the model is current (`layout build --check`), HEAD's
  sheet changes are drawing-only (actuators and measuring lines), and every line of the line
  list is routed. The operators declared in routing.yaml name P&ID valves that exist (0
  `layout-operator-unknown`).

## Not checked
- The area classification itself (CSA C22.1 / IEC 60079-10-1, competent person). Every zone
  is the ASSUMED screening table, and no Ex selection may rest on it.
- Building siting and the LNG spill radiation and dispersion exclusion zones (CSA Z276 /
  NFPA 59A) for B-SUB, B-JET, B-ANA and the sumps. Flare radiation (#3) needs the derrick
  owner's flare study. Both need a consequence study by a competent person.
- The trestle lines next to B-JET (10.3 m): a release from the trestle (drip trays, loop bay
  flanges if any) against the non-Ex building. Part of the consequence study.
- Pipe stress, anchors, guides, the loop design (#6) and surge loads on the trestle and the
  tank roof piping: piping stress engineer.
- Structural design of the racks, the trestle, the cable bridge, the tank roof steel and the
  pump platform (tank contractor), and of B-JET's piled deck and the marine structures:
  structural and marine engineers.
- Crane selection, the ground and deck bearing, and the in-tank pump removal method (#1):
  lifting contractor and the pump vendor.
- Fire protection (fire water ring main, monitors, deluge, high-expansion foam at the sump):
  not in the model.
- Cable sizing, voltage drop on the ~1.9 km 6.6 kV and ~240 m 400 V feeders, and the
  transformer and switchgear rooms (#10): electrical engineer. HVAC sizing: HVAC engineer.
- The estimate: `estimate/rates.yaml` was not reviewed, and the take-off carries #6 and #11.
- Every one of the 181 pinned routes vertex by vertex. I read the tank roofs, the riser
  drops, the BOG area, the trestle section, the jetty head and the B-JET links.
- The HAZOP (23 `hazop-input-changed` warnings) and the three design review gates: outside
  this scope.
