---
topic: layout
reviewed_commit: 235f66ebf03a58181449fb5121552784b7521627
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, checks/checks.yaml, control/cause-effect.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 235f66ebf03a58181449fb5121552784b7521627, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: 235f66ebf03a58181449fb5121552784b7521627, relation: depends-on}
  - {path: DESIGN.md, revision: 235f66ebf03a58181449fb5121552784b7521627, relation: depends-on}
  - {path: scripts/datasheet_sizing.py, revision: 235f66ebf03a58181449fb5121552784b7521627, relation: analyses}
  - {path: process/flowsheet.yaml, revision: 235f66ebf03a58181449fb5121552784b7521627, relation: analyses}
  - {path: process/simulation.yaml, revision: 235f66ebf03a58181449fb5121552784b7521627, relation: analyses}
reviewer: Claude (independent review agent; did not author D-079, D-080, D-083 .. D-087, the layout files, the datasheets or the P&ID changes)
reviewer_kind: agent
branch: asu-followup
merge: pending
---
# Review: layout, thirteenth review (independent) after review12, D-079 / D-080 / D-083 .. D-087

This is an independent review of branch `asu-followup` at 235f66e. It covers the layout, the
datasheets, safety and P&ID consistency. The branch is stacked on `stage/basic-front-end-pressure`
(PR #27). It follows reviews/2026-10-23-layout-review12.md (ac934cd, merged with #26 as 0a6c3cf).
It covers `git diff origin/main...HEAD`:
- 76112cd D-079 (front-end pressure profile, MAC discharge 5.98 bara);
- 35a2d68 (run record);
- fb846a4 (BFD / PFD fingerprint);
- 33c49c0 D-080 (2) (values on the D-079 state);
- b88ff2e D-080 (1) (main air lines DN700);
- b484e0a D-083 (C-1102 blow-by relief case, I-03 SIL 1 screening);
- 2bc2850 D-084 (valves out of reach);
- 70af126 D-085 (supports);
- eb403e7 D-086 (review12 lows);
- ca0c32b (rebuild with core #105);
- 235f66e D-087 (S14 / S15 / S16 props).

The reviewer designed none of this. cheme-as-code is the global `cheme` 0.7.0 (core main with
#102 / #105). Coordinates are site metres from `layout/plant-model.yaml`. "Computed" means
`cheme run scripts/datasheet_sizing.py` at 235f66e (output in build/sizing.txt, not committed).

`cheme diff origin/main --list` (P&IDs):
- P-01: AIR-1004 (3 modified), C-1101 (I4 moved), LSLL-1115 measuring line, WN-1002 label and the
  D-083 note;
- P-02: AIR-1004 (9), AIR-2001 (5), XV-2101A/B and XV-2102A/B DN, the provenance note;
- P-03: HV-3127 / HV-3128 / HV-3129 added, and changes to E-3105 (N5 .. N7), AIR-3002, CHW-3001,
  CHWR-3001, AIR-2002, Tee_AIR2002_B, OPC_AIR2002_in, E-3101 N2 and the TV-3124 label;
- BFD / PFD: S1C, S2, S3, S3L, S3C, S3CU, S12D, E1, Q1 and Q2, plus S14 / S15 / S16 properties
  (generated).

Not drawn: none.

Verdict: **no critical or high finding is open**. All 7 review12 findings are closed with
evidence. So are review3#3 and review3#4. Two parts that are still open are split off as new
findings (#1 from review12#1, #4 from review12#7). In all there are five new low findings and no
critical, high or medium one.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-layout-review13#1 | DESIGN.md / K-1101 datasheet | front-end budget S3 -> S4 | Split from review12#1. D-079 sets S3 -> S4 to 28 kPa, but its own parts add up to 28.4 kPa (17.4 lines + 8 bed + 3 F-2101). The computed DN700 check confirms it is short: section 10, bed B, lines 17.1 kPa + 11 = 28.1 kPa, margin -0.055 kPa. At the bound (every turn and the vessel nozzles counted) the lines take 21.1 kPa, margin -4.11 kPa. D-080 (1) asks the simulation owner to raise S2 to about 6.02 bara (~27 kW at 6.74 kW/kPa), but the request is open. The K-1101 datasheet outlet_pressure (5.98 bara) only says that S2 rises if the suppliers' bed and filter drops exceed ~11 kPa. It does not mention the 0.06 to 4.1 kPa the lines already overrun. The motor margin holds either way: 8,121 + 27 kW against 9,000 kW. | low | open | Simulation owner: answer D-080 (1), either S2 about 6.02 bara or the vessel nozzle losses taken inside the bed / F-2101 allowables. Until then, cite D-080 (1) in the K-1101 outlet_pressure source as a hold. |
| 2026-10-24-layout-review13#2 | process / script | process/simulation-run.json | At HEAD, `cheme run scripts/datasheet_sizing.py` prints "simulation run record: ... run ... at 76112cd; STALE against process/flowsheet.yaml". D-087's `props --fill` (235f66e) changed flowsheet.yaml after the run. D-080 (2) states that the fingerprints match, which was true at 33c49c0 but is not true now. The values themselves still reproduce: `cheme process simulate --check` gives K1101 7,259.77 kW electric / 6,867.74 kW shaft / Q 7,697.95 kW, C1101 -701.38 kW, C1101U -635.31 kW, equal to the record. So every datasheet number on it stands. | low | open | Rewrite the run record from the clean tree (`cheme process simulate`, simulation owner), so that the script that the datasheets cite is not stale again. |
| 2026-10-24-layout-review13#3 | BFD / PFD / flowsheet | S12D composition | New at D-079 (76112cd): S12D mole fractions sum to 1.0000012 (0.92296 + 0.05044 + 0.012265 + 0.012011 + 0.0023252). The current core (pyDEXPI check, tolerance 1e-6) reports `pydexpi_composition_fractions` on BFD.xml and PFD.xml, 2 of the 35 warnings. The origin/main values summed to 0.9999998. The composition source still cites "D-027, D-058, D-059, D-066", not D-079. S12D carries the PR water of S3 (143.1 kg/h), but the TSA load and V-2101A/B are sized on 165.0 kg/h (IAPWS-95, section 8, D-080 (2)). The regeneration gas therefore carries ~22 kg/h less water than the beds desorb. | low | open | Simulation owner: normalise the S12D fractions to 1 within 1e-6 and cite D-079 in the source. Either derive the S12D water from the 165 kg/h the beds are sized for, or record why the PR value is kept. |
| 2026-10-24-layout-review13#4 | C-1101 datasheet / C&E | I-03 (LSLL-1115 -> XV-1115) | Split from review12#7. The relief case and the SIL 1 screening are now recorded (D-083). What a SIL 1 SIF needs for its specification is not stated: the LSLL-1115 trip level within the 0.8 m tray range, the process safety time and the XV-1115 closing time. The tappings sit 0.1 m above the tray floor and N7 draws off at the floor (D-086). The trip level can therefore only be a few centimetres above the draw-off. With LV-1114 failed open, the time from that level to gas break-through into CHWR-1001 depends on the LV-1114 capacity against the 34 m3/h inflow and the tray hold-up, and neither is given. A trip that comes too late means the full 94.5 t/h blow-by case for the minutes until XV-1115 closes. D-083 relies on the C-1102 internals surviving that. | low | open | In the I-03 notes or the C-1101 datasheet, give the trip level (or require one from the packing supplier, e.g. at least x mm above the draw-off top), the tray hold-up between trip and seal loss at the LV-1114 full-open flow, and the required XV-1115 closing time. Confirm them in the HAZOP / LOPA / SRS. |
| 2026-10-24-layout-review13#5 | P-03 | E-3105 tag | D-086 (3) moved the "E-3105" tag west of the K-3101 discharge line, which runs down to E-3104. A process line now stands between the tag and its exchanger, and the tag sits closer to that line and to K-3101 than to E-3105. The lint counts 0 label-far-from-owner. Crop build/P-03_crop-20-60-140-170.png. Before: build/P-03@origin-main_crop-50-95-110-145.png, tag under the symbol. | low | open | Move the E-3105 tag right of or below its symbol (e.g. between HV-3128 and the AIR-3002 DN text), clear of the K-3101 discharge line. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-23-layout-review12#1 | front-end pressure budget not closed; K-1101 outlet without a hold | medium | closed 33c49c0 | D-079 (76112cd) sets S2 5.98 / S3 5.88 / S4 5.6 bara from the cold box back; owner's DN700 (D-079 / D-080). The K-1101 datasheet gives 5.98 bara, 6,868 kW shaft, 7,260 kW electric with D-079 cited, and the motor check is 8,121 kW at 110 % against 9,000 kW (section 1, reproduced). The remaining 0.06 to 4.1 kPa is split off as #1. |
| 2026-10-23-layout-review12#2 | CB-1 AIR-2002 opening still DN500 size | low | closed b88ff2e | structures.yaml line 78: offset 7.65, 0.85 x 0.85 m, sill 7.95 (DN700). `cheme layout report`: no layout-wall-penetration finding; `layout-rules` gate ok. |
| 2026-10-23-layout-review12#3 | LSLL-1115 tapping drawn in the upper bed | low | closed eb403e7 | build/P-01_crop-185-60-320-125.png: the LSLL-1115 measuring line enters C-1101 just below the upper bed, beside the LIC-1114 one, both between the bed and the drawn chimney tray. C-1101 datasheet I4 is at 13.1 m. Still 2 accepted crossings on P-01. |
| 2026-10-23-layout-review12#4 | I3 / I4 below the draw-off, no tray elevations | low | closed eb403e7 | C-1101 datasheet `chimney_tray_elevations` (ASSUMED): floor 13.0, chimney tops 13.8 m; N7 at 13.0 m; I3 / I4 at 13.1 m; downcomer between the range and the tops. N3 at 12.5 m below. The trip-level detail is #4. |
| 2026-10-23-layout-review12#5 | E-3105 drains and vent not drawn | low | closed eb403e7 | `cheme show E-3105`: N5 -> HV-3127 (AIR-3002 S9), N6 -> HV-3128 (CHWR-3001 S2), N7 -> HV-3129 (CHW-3001 S2). Drawn capped (build/P-03_crop-50-95-110-145.png), in the datasheet; validate shows 0 datasheet-nozzle mismatches. |
| 2026-10-23-layout-review12#6 | WN-1002 label over CHWR-1001 | low | closed eb403e7 | build/P-01_crop-300-20-380-90.png: "WN-1002 DN 900" right of the vent, below "to atmosphere (elevated)"; the D-083 note "open vent, no valve: C-1102 relief path" left of it. |
| 2026-10-23-layout-review12#7 | C-1102 blow-by relief case and I-03 SIL | medium | closed b484e0a | Computed: choked S3 air through the DN150 bore, 1,407 kg/(m2 s) x 0.01865 m2 = 94.5 t/h (checked by hand: 588 kPa, 285 K, k 1.4). With the design gas 58,074 kg/h and 851 kg/h evaporated, 153.4 t/h leaves WN-1002 at 2.99 kPa (55.6 m/s). The internals bound 3.3 x (153,408 / 58,925)^2 = 22.4 kPa gives 25.4 kPa(g) against 1 barg. That bound is conservative because the blow-by enters above the packing. Relief case list row (DESIGN.md section 4). I-03 `sil: 1 (screening ...)`. LOPA: CCPS 2001 generic values, both scenarios RRF 10, marked for HAZOP confirmation. Mixture O2 14.9 mol% (checked: 684 + 105 kmol/h O2 in 5,310 kmol/h). The SRS details are split off as #4. |
| 2026-10-22-layout-review3#2 | PSV tailpipes free above the valves | low | open | Unchanged: the guides wait for the stress analysis (D-050, D-062 (4)). |
| 2026-10-22-layout-review3#3 | layout-operability warnings | low | closed 2bc2850 | `cheme layout report`: layout-operability 1, accepted in checks.yaml (XV-3105, D-084 (3), MEWP from grade, ASSUMED owner practice). The 6 TSA valves run on remote operators to VP-TSA-B / VP-TSA-E at 5.9 m (build/layout-plan_crop-85-22-110-45.png, build/layout-section-y39_crop-85-0-110-14.png). PV-4109 / PV-4110 are lowered. escape-* 0, clash 0. |
| 2026-10-22-layout-review3#4 | rack free spans and support missing | low | closed 70af126 | layout-free-span 2 (LOX-3001 S2, LIN-3001 S2) and layout-support-missing 15, all accepted with reasons. `scripts/support_steel_scan.py`: 306 declared supports and platforms, 0 steel pairs overlapping, 0 members within 0.1 m of a pipe they do not serve (1022 runs). |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | Unchanged; waits for the vendor drawing (D-050 / D-062 (4)). |

## Drawing
`cheme validate` at 235f66e: 0 errors, 35 warnings:
- 13 instrument-no-interlock;
- 12 template-metadata;
- 6 line-crossing;
- 2 titleblock-sheet;
- 2 pydexpi_composition_fractions (new, #3).

Review12 counted 47 warnings: 9 operability and 5 free-span are gone, and 2 composition warnings
are added.
- P-01: 0 line-through-label, 2 line-crossing (accepted: CHWR-1001 over CHW-1001, D-069; the
  LSLL-1115 measuring line over CHW-1001, D-076; the reason still holds after D-086 (1)),
  0 label-overlap, 0 label-far-from-owner, 0 text-outside-frame, 0 title-text-overflow,
  0 line-through-symbol.
- P-02: 0 in each count.
- P-03: 3 line-crossing (accepted, unchanged), otherwise 0. The E-3105 tag placement that no rule
  sees is #5.
- P-04: 1 line-crossing (accepted, unchanged), otherwise 0.

The `drawing-clean` gate passes.

Read:
- P-01 crops build/P-01_crop-185-60-320-125.png (C-1101 tray, LIC-1114 / LSLL-1115, LV-1114 F.C.,
  XV-1115 F.C., TV-1105) and build/P-01_crop-300-20-380-90.png (C-1102, WN-1002, D-083 note);
- P-02 tile A1 (`--tiles 2x2`): AIR-2001 DN 700, RG-2002 DN 700, RG-2001 DN 600, XV-2102A,
  XV-2103A, PSV-2108A, E-2101;
- P-03 crops build/P-03_crop-20-60-140-170.png and build/P-03_crop-50-95-110-145.png (with the
  `--rev origin/main` crop): E-3105 N5 .. N7 with HV-3127 / HV-3128 / HV-3129, TICA-3124 /
  TV-3124 F.O., HV-3126 L.O., AIR-3002 DN 200.

Not read: the other tiles. Their changes are DN texts, which validate compares with the line list
(0 DN mismatch) and `cheme.label-literal` (no AIR-line hit).

## Layout
- `cheme layout build --check`: "layout/plant-model.yaml is up to date".
- `cheme layout lifting --check`: exit 0. 15 lifts, every lane clear. K-1101 39.27 t on the 50 t
  B1 crane; K-4101 69.3 t needed from Z-PAD-A4; K-4102 38.5 t from Z-PAD-A4N.

`cheme layout report` at 235f66e:
- **Lines:** 81, all routed except 4 skipped segments (GAN-3002, LN-3002 D-028; two VNT-3004).
  0 unrouted. AIR-1004 133.9 m, AIR-2001 66.8 m, AIR-2002 72.9 m, WN-1002 6.9 m.
- **Chains per method:** astar 26, open 8, pinned 166, rack 15. No `direct` and no
  `rack+direct`.
- **Reasons:**
  - local: above the pipe-way 7, pipe-way 5, pump run at grade 4, rack detour too long 1, rack
    run too short 1, short run 8;
  - open end 8;
  - pinned 166;
  - rack: battery limit at a rack end 13, longer than local_max_m 2.
- **Rack fill:**

  | rack | 5 m | 6.5 m | 7 m | 8.5 m | 9 m |
  |---|---:|---:|---:|---:|---:|
  | PR1 | 61 % | | 43 % (3.45 of 8 m) | | 25 % |
  | PR2 | | 6 % | | 6 % | |
  | PR3 | | 48 % | | 43 % | |

  The PR1 7 m tier went from 47 % to 43 % although AIR-1004 / AIR-2002 grew to DN700. I compared
  the 7 m tier pipes of HEAD and origin/main: they have the same points (AIR-2002 lane y 66.55 ->
  66.65 only). So the change is in the reinstalled core's fill measure, not in the design. Clear
  distances: AIR-2002 to WN-1001 0.19 m, to RG-2001 0.75 m (from the model coordinates).
- **Model findings per rule:**

  | rule | count |
  |---|---|
  | clash-*, headroom, access-blocked, steel-in-way, wall-penetration, vent-outlet, zone-crossing, separation, escape-*, landing-width, egress-zone, operator-unknown, lifting, laydown, pad-overlap, spacing, building-spacing, zone-source | 0 each |
  | operability | 1 (XV-3105, accepted) |
  | free-span | 2 (accepted) |
  | support-missing | 15 infos (accepted) |
  | tier | 1 (WN-1001, accepted D-071 (3)) |
  | access-enclosed | 1 (accepted) |
  | tray-span | 17 (accepted; the IT-JB-A3-1 reason now quotes the current 14.0 m, no accept-stale) |
  | tray-zone | 6 |
  | tray-separation | 1 (accepted) |
  | nozzle-unconnected | 2 infos (D-028) |

- **Objects:** 46 equipment items, 61 generated and 166 pinned pipes, 121 in-line items, 8
  platforms, 13 declared and 1 generated structures, 30 zones.
- **`cheme check`:** every gate passes except `layout-review`, which this record is meant to make
  current.

PNGs read (build/, rendered at 235f66e):
- build/layout-plan.png;
- build/layout-section-y68.png (along PR1);
- build/layout-section-x133.png (rendered, through CB-1 / compander; nothing changed there but the
  AIR-2002 opening);
- build/layout-plan_crop-85-22-110-45.png (TSA area: VP-TSA-B between Z-SIEVE and V-2101B,
  VP-TSA-E east of V-2101A, ladders);
- build/layout-section-y39_crop-85-0-110-14.png (VP-TSA-B at 5.9 m under the valves at 7-8.5 m).

## Checked and fine
- **DN700 Darcy check (D-080 (1)):** bed B AIR-1004 checked by hand. G = 30.86 kg/s, rho 7.21,
  ID ~0.69 m: u 11.4 m/s. K = 20 x 0.75 + 2.8 = 17.8 on 467 Pa gives 8.31 kPa. Friction
  f ~0.0118 x 94.75 / 0.692 x 467 Pa gives 0.75 kPa. In all 9.06 kPa against the script's
  9.05 kPa. The line list notes (AIR-1004 / AIR-2001 / AIR-2002) equal section 10.
- **P&ID DN:** AIR-1004 / AIR-2001 / AIR-2002 read DN 700. Validate's lists-vs-P&IDs and
  datasheet-nozzle cross-checks show 0 mismatches. PSV-1109 / PSV-2108A/B branches unchanged.
  The operating pressure 4.97 barg is well inside the 8 barg design of K-1101, E-1103, C-1101,
  V-2101A/B and F-2101.
- **D-080 (2):** MAC section 1 reproduced: ratio 1.84, 373.3 / 385.7 / 386.2 K; coolers 395.3 /
  605.2 / 557.5 m2; motor check 8,121 kW (+10.8 %). TSA 165 kg/h water (IAPWS-95). The
  pressures, power and the D-083 blow-by bound on the instrument list, the datasheets and the C&E
  agree.
- **D-083:** the bounding choked flow, the vent drop and the zone O2 balance were rechecked by
  hand (above). The LOPA values are labelled ASSUMED with the CCPS (2001) tables and IEC 61511-1
  cited in our own words, and marked for HAZOP / LOPA confirmation. Rejecting a restriction
  orifice has a reason.
- **D-084 / D-085:** checked against the report counts above and the support scan. GOX-4001 S1
  (18.65 m DN500 against 11.9 m) on a CB-1 bracket at mid-length gives ~9.3 m spans, inside the
  table span.
- **D-087:** values marked `calculated`, the source says `phase-constrained`, dG/RT at most
  0.001. Generated fill only, reported in PROGRESS.md.
- **Simulation:** `cheme process simulate --check` reproduces the run record (#2). The 4
  `process-sim-deviation` warnings (S10 / S11 assumed T, p) are the simulation owner's and are
  unchanged.
- **Licence rule:** the new decision and datasheet texts give sources and values in their own
  words. No third-party tables or figures were copied. No commercial downstream product is named.
- **Stage gates:** no stage sign-off was written; `checks/status.json` is untouched.

## Not checked
- **The front-end budget (#1), the run record (#2) and S12D (#3):** for the simulation owner.
- **The suppliers' drops:** adsorber (8 kPa), F-2101 clean / change-out (3 / 5 kPa), E-2101, S-2101,
  FV-2105.
- **I-03 SRS, HAZOP / LOPA confirmation (#4), and the C-1102 internals at 153 t/h:** for the C-1102
  supplier.
- **The chimney tray, downcomer and level range:** for the packing supplier.
- **TSA top piping and valve arrangement (VP-TSA-B / E fit), tank nozzle arrangement for PV-4109 /
  PV-4110, and a PR1 walkway for XV-3105:** for the TSA supplier, the tank supplier and the rack
  designer.
- **Pipe stress, shoes, guides, clips and brackets (D-085), and the PSV tailpipe guides:** for the
  stress engineer and the vessel / tank / cold-box suppliers.
- **The B1 crane girders, crane outriggers and ground bearing:** for the structural engineer and
  the lifting plan.
- **The vent and inert study** (Z-N2-WN1002 with the blow-by mixture): for a competent person.
- **The P&ID tiles not named under Drawing.**
