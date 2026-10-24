---
topic: layout
reviewed_commit: dcbdc289004ef4ed0e8ddc37d5cc21e531e3c2b7
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, equipment/equipment-list.yaml, checks/checks.yaml, control/cause-effect.yaml, control/instrument-list.yaml, lca/lca.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: dcbdc289004ef4ed0e8ddc37d5cc21e531e3c2b7, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: dcbdc289004ef4ed0e8ddc37d5cc21e531e3c2b7, relation: depends-on}
  - {path: DESIGN.md, revision: dcbdc289004ef4ed0e8ddc37d5cc21e531e3c2b7, relation: depends-on}
  - {path: scripts/psv_reaction.py, revision: dcbdc289004ef4ed0e8ddc37d5cc21e531e3c2b7, relation: analyses}
  - {path: process/flowsheet.yaml, revision: dcbdc289004ef4ed0e8ddc37d5cc21e531e3c2b7, relation: analyses}
  - {path: lca/results.md, revision: dcbdc289004ef4ed0e8ddc37d5cc21e531e3c2b7, relation: analyses}
  - {path: estimate/tea.md, revision: dcbdc289004ef4ed0e8ddc37d5cc21e531e3c2b7, relation: analyses}
reviewer: Claude (independent review agent; did not author D-091, the review19 fixes or the layout files)
reviewer_kind: agent
branch: fix/close-open-review-items
merge: pending
---
# Review: layout, nineteenth review (independent) of D-091 and its fixes

This is an independent review of branch `fix/close-open-review-items` at dcbdc28, based on
origin/main 42cb69a. The branch closes the open low items without vendor data or a stress
analysis (owner decision, D-091):
- e4a1678: D-091 (1), the 0.107 kPa front-end overrun accepted (review15#2);
- 0d9f876: D-091 (2), PSV tailpipe screening forces, guide RV-TPG and support RV-TPS
  (review3#2);
- 1b3b8f3: D-091 (3), KT-3101 casing extension CB-1X as an ASSUMED envelope (layout#15);
- 16f1bb0: D-091 (4), the tank erection basis and ASSUMED shape types on the datasheets
  (review18#1, #2; issue process-library#32);
- dcbdc28: the fixes of findings #1 .. #7 below, raised in the first pass of this review at
  16f1bb0.

`git diff 42cb69a..HEAD -- process/` is empty: the simulation owner's files are untouched, and
no P&ID changed. cheme-as-code is the global `cheme` 0.8.0.

Verdict: **no critical, high or medium finding is open.** The seven findings of the first pass
are closed in dcbdc28. The five carried-over items (review18#1, #2, review15#2, review3#2,
layout#15) are closed. Two new low findings: #8, the claim that the DN250 tailpipe friction
keeps the built-up back pressure under 10 % of set does not hold for the PSV-3116 warm bound,
and #9, a Markdown nesting slip at the end of D-091.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-layout-review19#1 | DESIGN.md | D-091 (1) | D-091 (1) said the simulation owner had agreed to accept the 0.107 kPa and meant to write 32.1 kPa in D-089. Nothing in the repository records this. | medium | closed dcbdc28 | Done: the acceptance is now the project owner's decision of 2026-10-24, and nothing in the repository records the simulation owner's view (D-090 (1) only noted it). The simulation owner's statement is open item O4. |
| 2026-10-24-layout-review19#2 | DESIGN.md / piping | VNT-3002, PSV-3114 tailpipe | The 94 K relief case reaches the PN6 tailpipe outside the cold box. That class is carbon steel when warm, which is brittle at about -179 C. | medium | closed dcbdc28 | Done: D-091 (5) makes the VNT-3002 tailpipe outside the cold box SS 304L. The PN6 class text in pipe-specs.yaml and the VNT-3002 note in the line list say so. Modelling it is open item O1. |
| 2026-10-24-layout-review19#3 | DESIGN.md | PSV-3114, PSV-3116 | The built-up back pressure at the DN150 exits (up to 36 % of set) was recorded only as prose, with no tracking. | medium | closed dcbdc28 | Done: D-091 (5) makes the tailpipes DN250 (ASSUMED). The script prints back pressure as a share of set for DN150 and DN250. Relief sizing and the DN250 model are open item O1. See #8 for the friction claim. |
| 2026-10-24-layout-review19#4 | layout | RV-TPS | RV-TPS stood at y 42.7, 0.3 m off the tailpipe axis, so its bearing was eccentric. | low | closed dcbdc28 | Done: RV-TPS is at [129.5, 43.0]. RV-TPG's column continues from it (base 55.3). |
| 2026-10-24-layout-review19#5 | DESIGN.md / layout | AIR-3003, CB-1X | About 3 m of the cold inlet runs above the 3 m casing, not inside it. D-091 (3) did not say so. | low | closed dcbdc28 | Done: D-091 (3) states it. An ASSUMED perlite roof hood and PUR insulation from XV-3117 to the sleeve are decided; neither is modelled (open item O2). |
| 2026-10-24-layout-review19#6 | DESIGN.md / script | PSV-4123, PSV-4124 | The tank PSV rate was called choked flow, but the pressure ratio of 1.54 is below the critical ratio. | low | closed dcbdc28 | Done: D-091 (2) and the bore_flow docstring now call it an upper bound from the choked-flow formula, with the flow subcritical. |
| 2026-10-24-layout-review19#7 | DESIGN.md | local-discharge PSVs, RV-TPG / RV-TPS lugs | Outlet supports of up to 17.2 kN, and the unmodelled guide and bearing lugs, were not tracked. | low | closed dcbdc28 | Done: open items O5 and O6 at the end of D-091, with D-050 pointing to them. |
| 2026-10-24-layout-review19#8 | DESIGN.md | D-091 (5), PSV-3116 (and PSV-3114) DN250 tailpipe | D-091 (5) says the friction of about 4.5 m of straight DN250 pipe adds to the exit back pressure but "the total stays under 10 %". A Fanno-flow estimate of my own (k 1.4, 264.6 mm bore, 4.5 m, Darcy f 0.012 to 0.015, no entry, elbow or expander loss) gives other figures. At the PSV-3116 warm bound (288 K, exit choked at 1.26 bara), the outlet flange sees about 0.87 to 0.94 barg, 12 to 13 % of the 7 barg set. At PSV-3114 warm it is about 0.30 to 0.35 barg, 9 to 10 % of 3.5 barg. The cold cases, the credible relief temperatures from the columns, stay at or below about 3 % (PSV-3116 103 K: 0.19 to 0.23 barg). The DN250 choice is right, and O1 already gives the back pressure with tailpipe friction to the relief sizing. But the sentence states as a result something that the warm bound does not meet. | low | open | Reword D-091 (5): the cold cases stay under about 3 % of set with friction, and the warm bounds reach about 10 % (PSV-3114) and 13 % (PSV-3116). Add to O1 that if the warm case is credible, relief sizing chooses a balanced-bellows valve or a DN300 tailpipe for PSV-3116. |
| 2026-10-24-layout-review19#9 | DESIGN.md | D-091 end, "Remaining open after D-091" | The paragraph follows the last (5) bullet with no blank line. In Markdown it becomes a lazy continuation of the "Model" bullet, and the O1 .. O6 list nests under it. The text is all there, but the rendered list sits inside (5). | low | open | Add a blank line before "Remaining open after D-091". |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-layout-review18#1 | Tank datasheets do not carry the D-081 (10) erection decision | low | closed 16f1bb0 | D-091 (4) (a): the T-4101 / T-4102 datasheet notes carry the field erection and the ~0.5 t heaviest lift (ASSUMED, the tank supplier to confirm). `cheme datasheets drawing --check`: all current. |
| 2026-10-24-layout-review18#2 | List-derived head and support types not marked ASSUMED | low | closed 16f1bb0 | D-091 (4) (b): 17 `head` and 25 `support.type` values are marked `assumed: true`, citing D-028, and no value changed. The layout-derived axis and elevation stay unmarked, as review18 agreed. |
| 2026-10-24-layout-review15#2 | D-089 bound case 32.1 kPa against S3 -> S4 32 kPa (-0.107 kPa) not stated or accepted | low | closed e4a1678 | D-091 (1) accepts it as the project owner's decision of 2026-10-24 (wording corrected in dcbdc28, #1). The reasons: the bound is uncertain by far more than 0.1 kPa, and the effect is 0.74 kW, 0.01 % of the MAC. `process/` is untouched. The simulation owner's restatement or reset is tracked as D-091 O4. |
| 2026-10-22-layout-review3#2 | PSV tailpipes free above the valves | low | closed 0d9f876 | D-091 (2): screening reactions from `cheme run scripts/psv_reaction.py`, which I re-ran and which give the same figures. The guide RV-TPG (crossbar 57.75 m) and the axial support RV-TPS (55.3 m), both on the tailpipe axis y 43.0 since dcbdc28 (plant-model.yaml crossbars x 128.3 .. 130.7, y 43.0). Section crop build/layout-section-y43_crop-124-50-136-60.png shows both T-posts between the tailpipes. Lugs and outlet supports are tracked as O5 and O6. |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | closed 1b3b8f3 | CB-1X is modelled as an ASSUMED envelope (3 m high, AIR-3003 sleeve pinned). The roof hood for the part of AIR-3003 above it (dcbdc28, #5) is O2, and the check against a supplier drawing is O3. No new clash, keep-clear, access or lifting finding. |

## Drawing
`cheme validate` at dcbdc28 gives 0 errors and 33 warnings, the same count as review18. 94 files
were compared, with the same cross-checks, including datasheets and review records.

Counts per sheet:
- P-01: 0 line-through-label, 2 line-crossing (accepted: D-069, D-076), 0 label-overlap, 0
  label-far-from-owner;
- P-02: 0 in every count;
- P-03: 3 line-crossing (accepted), 0 otherwise;
- P-04: 1 line-crossing (accepted), 0 otherwise.

No P&ID changed on the branch, so no tile was read. `cheme datasheets drawing --check`: all 40
current.

## Layout
- `cheme layout build --check`: "layout/plant-model.yaml is up to date". `cheme layout lifting
  --check`: exit 0.
- `cheme layout report` at dcbdc28:
  - **Lines:** 81, all routed except 4 skipped segments (GAN-3002, LN-3002, D-028; two
    VNT-3004), 0 unrouted.
  - **Chains per method:** astar 26, open 8, pinned 166, rack 15. No `direct` and no
    `rack+direct`.
  - **Reasons:** local 26 (above the pipe-way 7, pipe-way 5, pump run at grade 4, rack detour
    1, rack run too short 1, short run 8), open end 8, pinned 166, rack 15 (battery limit at a
    rack end 13, longer than local_max_m 2).
  - **Rack fill:** PR1 61 / 43 / 25 %, PR2 6 / 6 %, PR3 48 / 43 %, the same as review18.
  - **Model findings per rule:** access-enclosed 1, free-span 2, laydown 1, lifting 4,
    nozzle-unconnected 2, operability 1, support-missing 15, tier 1, tray-separation 1,
    tray-span 17, tray-zone 6. These are the same counts as review18 and the same acceptances
    in checks/checks.yaml. There are 0 clash, headroom, access-blocked, wall-penetration,
    vent-outlet and escape findings. The new steel and CB-1X added no finding.
  - **Objects:** 46 equipment items, 61 generated and 166 pinned pipes, 121 in-line items,
    8 platforms, 14 declared and 1 generated structures, 30 zones.
- PNGs read (rendered at dcbdc28):
  - build/layout-plan.png;
  - build/layout-section-y68.png (along PR1);
  - build/layout-section-x133.png (through CB-1 and the compander);
  - build/layout-section-y43_crop-124-50-136-60.png (the RV platform with PSV-3114 and
    PSV-3116, RV-TPS and RV-TPG on one column between the tailpipes).
  The plan and the sections show the same routes, racks, zones, pads and laydowns as review18.
- **Support steel:** the take-off gains +0.561 t of HEB200 over 42cb69a (108.057 to 108.618 t).
  That matches the "+0.56 t" in D-091 (2). Both crossbars end 0.216 m clear of the DN150 OD
  (0.30 m minus 0.084 m), and 0.16 m clear of the DN250 OD.
- **Back pressure figures:** `cheme run scripts/psv_reaction.py` prints the D-091 (5) values:
  DN150 at 8 / 36 % and 14 / 33 % of set, DN250 at 0 / 0 % and 0 / 4 %. Tailpipe friction is
  in #8.

## Checked and fine
- **Material:** PN16 already gives SS 304L for nitrogen and cryogenic service (VNT-3003). The
  PN6 class text and the VNT-3002 / VNT-3003 line-list notes carry D-091 (5). The DN250 sch 10S
  bore (273.0 - 2 x 4.19 = 264.6 mm) is right.
- **D-050** points to D-091 O1 .. O6, and each O-item names an owner.
- **Assess outputs:** `cheme assess mto / estimate / equipment / tea / lca --check` all exit 0.
  `cheme fmt --check` exits 0.
- **Simulation owner's files:** process/flowsheet.yaml, simulation.yaml and
  design-basis.yaml are untouched on the branch.
- **Licence rule:** the API 520 Part II method is cited and paraphrased, and no third-party text
  or table was copied. No commercial downstream product is named.
- **Stage gates:** no sign-off was written, and checks/status.json is untouched.

## Not checked
- **Relief sizing** (rates, orifices, back pressure with friction, the choice between a
  conventional and a balanced-bellows valve): this needs relief sizing in detail engineering
  (O1, and #8).
- **Pipe stress, the lugs, the guide and bearing details, and the local-discharge outlet
  supports:** piping supports and stress, in detail engineering (O5, O6). The steel sizes are
  ASSUMED, for structural detail design.
- **CB-1X envelope, roof hood and AIR-3003 insulation:** no supplier drawing (O2, O3).
- **The S3 -> S4 allowance:** for the simulation owner (O4).
- **Datasheet drawings:** not rendered to PNG; checked through `drawing --check`.
- **P&ID tiles:** none read, since no sheet changed.
