---
topic: layout
reviewed_commit: 99f70af9aee7c79188172c8195f8eb4c8e2b48e6
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, checks/checks.yaml, pid/P-01.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 99f70af9aee7c79188172c8195f8eb4c8e2b48e6, relation: depends-on}
  - {path: DESIGN.md, revision: 99f70af9aee7c79188172c8195f8eb4c8e2b48e6, relation: depends-on}
  - {path: process/flowsheet.yaml, revision: 99f70af9aee7c79188172c8195f8eb4c8e2b48e6, relation: analyses}
  - {path: process/simulation.yaml, revision: 99f70af9aee7c79188172c8195f8eb4c8e2b48e6, relation: analyses}
reviewer: Claude (independent review agent; did not author D-061 .. D-064, the layout files, the datasheets or the fixes since ba79cf7)
reviewer_kind: agent
branch: final-pass
merge: pending
---
# Review: layout, tenth review (independent) after review9, D-062 .. D-064

This is an independent layout and datasheet review of branch `final-pass` at 99f70af. It follows
reviews/2026-10-23-layout-review9.md (ba79cf7). It covers:
- the fixes of review9 (D-062: 5dfedb7, 374bfde, 8370ac0, 0660693);
- the merge of the simulation work (#17 D-058, #18 D-059 / D-061; 2f98783, 18ce59b);
- the datasheet pass on the simulated states (D-063: b2ac471, 56f3961);
- the P-01 condensate drains (D-064: 99f70af).

The reviewer designed none of this. cheme-as-code is the global `cheme` (core main). Coordinates
are site metres from `layout/plant-model.yaml`. "Computed" means a scratch scan of the model,
kept outside the repository:
- every declared support member against every pipe it does not serve (gap from the pipe's outer
  surface with insulation to the steel face);
- every declared support member against the members of every other declared support
  (steel against steel).

The datasheet checks recompute the LMTDs and areas of E-1102, E-1103 and E-3104 by hand, and the
E-1102 / E-1103 condensate from the dew point at each cooler's pressure.

`cheme diff origin/main --list` (P&IDs):
- P-01 adds CD-1001 and CD-1002, each with a gate valve, a SteamTrap and an off-page connector;
- E-1102 and E-1103 each get a nozzle N5;
- TIA-1111 is moved;
- the AIR-1002 drawing changes;
- the catalogue gains STEAM_TRAP_SHAPE.

The BFD and PFD change only the S1C / S3C links. No layout file was changed by this review.

Verdict: **no critical or high finding is open**. Every review9 finding is closed. New findings:
- two medium:
  - #1: the condensing part of the MAC coolers is sized at the gas LMTD, which is not
    conservative;
  - #2: seven places where the steel of one support post runs through the steel of another;
- six low (#3 .. #8).

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-23-layout-review10#1 | datasheets | E-1102, E-1103 | The areas 459.1 / 449.8 m2 put the latent duty (E-1102 679 kg/h x 2,406 kJ/kg = 454 kW; E-1103 about 434 kW) at the overall gas LMTD (37.68 / 37.82 K). The sheets call this "ASSUMED: conservative", but it is not. The water condenses only below the dew point, which the reviewer estimates at about 47 C in E-1102 (3.35 mol% at 3.26 bara = 10.9 kPa) and about 52 C in E-1103 (2.3 mol% leaving E-1102 saturated, at 5.85 bara = 13.5 kPa). That is at the cold end, where the air-to-water difference is only 15 .. 20 K. Only the use of the gas-cooler U for the condensing zone is conservative. Reviewer's two-zone estimate for E-1102, F 0.89 and U 160 in both zones:<br>- 111 -> 47 C against CW 27.6 -> 35 C: about 300 m2;<br>- 47 -> 40 C with the latent heat, about 650 kW against CW 25 -> 27.6 C (LMTD about 17 K): about 260 m2;<br>- in all about 560 m2 against 459 m2 (about 20 % short).<br>The CW flows and duties are unaffected. | medium | open | Size E-1102 / E-1103 by zones: desuperheating, then condensing below the dew point, with the zone LMTDs. Use a condensing-zone U from a cited source or leave the area as a `supplier` value of the MAC package, with the zone duties as the enquiry basis. Remove the word "conservative" from the sources. |
| 2026-10-23-layout-review10#2 | layout | declared support posts | Computed: in seven places, steel from two different declared supports occupies the same space (overlap = negative gap between the steel faces). Each place counts as two posts or more on one spot, with one member running through another, which cannot be built that way:<br>- LIN-3001 S2 post-7 column (143.76, 114.8, 0 .. 12.8) through the LIN-4003 S3 post-7 crossbar (143.6 .. 144.6, z 3.3): -0.20 m;<br>- CW-1004 S1 post-1 and CWR-1003 S1 post-3 crossbars (x 57.62 .. 59.44, y 60.62 / 60.64, z 3.48): -0.18 m;<br>- LOX-4003 S1 post-2 and LOX-4003 S3 post-5 crossbars crossing at (130.26 .. 130.29, 109.79, z 3.73): -0.16 m;<br>- LIN-4002 S4 post-2 / post-4 columns (x 144.52) through the LIN-4003 S3 post-3 / post-6 crossbars (z 3.3): -0.10 / -0.05 m;<br>- CWR-3001 S1 post-6 crossbar through the LIN-3001 S1 post-7 column (142.7, 55.35): -0.05 m;<br>- CWR-4002 S1 post-1 crossbar against the GAN-4004 S1 post-1 column (169.4, 62.78): -0.004 m.<br>D-062 (2) found one such place (GOX-4002 S12 post-5) and noted that no rule tests steel against steel. The scan excludes the intended stub SP-6.5 on the GOX-4002 S4 post-1 crossbar (-0.07 m, its own line). | medium | open | Merge each pair into one common support: a single post with a wider crossbar or two levels, declared once and serving both lines. Or move one post along its pipe until it is clear. Ask cheme-as-code for a steel-against-steel rule between different declared supports. |
| 2026-10-23-layout-review10#3 | DESIGN.md / line list | D-064 (2), AIR-1006 | D-064 (2) says the two drains, 679 + 649 kg/h, are "together ... the simulated S1C, 1,398 kg/h". In fact they add up to 1,328 kg/h. The 70 kg/h difference is the Peng-Robinson / IAPWS-95 gap that D-063 (2) records. The line list AIR-1006 note still says "~3.7 bara" for the E-1102 air. The E-1102 datasheet gives 3.26 bara in and 3.21 bara out (K-1101 stage 2, 1.822 per stage). | low | open | Correct the sentence in a new decision: the sheets carry 1,328 kg/h (IAPWS-95) and the simulation 1,398 kg/h (PR). Update the AIR-1006 note to about 3.26 / 3.21 bara (D-063). |
| 2026-10-23-layout-review10#4 | datasheets | 22 datasheets citing "D-063 (n)" | Sources cite `scripts/datasheet_sizing.py D-063 (n)` with the script's section numbers. These do not match the numbered items of DESIGN.md D-063:<br>- the MAC coolers and K-1101 cite (1), which is "Sizing script" in DESIGN.md (the MAC is (2));<br>- K-4101 / E-4101 / E-4102 cite (2) and K-4102 / E-4103 cite (3) (DESIGN.md (5));<br>- E-3101 / E-3102 cite (5) (DESIGN.md (6));<br>- C-3101 cites (6) and C-3102 cites (7) (DESIGN.md (7));<br>- V-2101A/B cite (8) and C-1101 / C-1102 cite (9) (DESIGN.md (3)).<br>A reader who follows "D-063 (n)" to DESIGN.md lands on the wrong item. | low | open | Cite the script section as `datasheet_sizing.py section n` and the decision as `DESIGN.md D-063 (m)`, or renumber the script's sections to DESIGN.md's items. |
| 2026-10-23-layout-review10#5 | datasheets | E-3101 (and the final sheets' header) | The E-3101 datasheet has `operating: {}`: the stream inlet and outlet pressures and temperatures appear only inside the `duty_kw` / `ua_kw_k` source texts. `process_streams` lists S16 at its flowsheet state (C-3102 top, 80.3 K), but the sizing uses S16 after E-3102 at 95.8 K; E-3102 is not in the flowsheet (D-059 open). The `area_m2: supplier` marker gives its reason as `source:`, while E-3102 / E-3103 use `reason:`. The 39 final sheets still begin with the generated "DRAFT datasheet ... remove `draft: true`" comment. | low | open | Add the operating block for the five streams: the D-061 states, S14 / S15 as saturated vapour, and S16 at 95.8 K "after E-3102, ASSUMED". Put the area marker's text under `reason:`. Drop the draft header comment from the final sheets. |
| 2026-10-23-layout-review10#6 | P-01 / layout | CD-1001, CD-1002 | The drains have a gate valve and a float trap, but:<br>- no strainer ahead of the trap, so separator debris goes into the float seat;<br>- no test or blow-down point, and no bypass, so a failed-shut trap floods the separator unseen;<br>- no level indication or alarm on the separators;<br>- the valves and traps carry no tags.<br>In the model, the gate valves sit at 0.33 m and the traps at 0.30 m above grade (centre), with the line running under the shells. That is workable from grade but low for a DN25 trap body. Plan build/layout-plan_crop-36-24-80-56.png, section build/layout-section-x60.2_crop-38-0-52-6.png. | low | open | Add a Y-strainer (or a trap with an integral strainer, stated) and a test valve downstream of each trap. Consider a high-level switch per separator, or leave the drain package to the MAC supplier with these requirements in the E-1102 / E-1103 notes. Tag the manual valves and traps if the project tags drain valves. Raise the trap centre to about 0.4 .. 0.5 m, with the hub below it (ASSUMED). |
| 2026-10-23-layout-review10#7 | process | process/flowsheet.yaml S1C, S3C | D-064 (99f70af) added `links:` to S1C (CD-1001 / CD-1002) and S3C (CWR-1001, LIC-1106) in `process/flowsheet.yaml`. That file belongs to the process-simulation work. The edit is links only: no stream value changed, the PFD / BFD were rebuilt, and process-links passes. It is not a copy-error fix, and D-064 does not say the owner agreed. | low | open | The simulation owner confirms the links, or they are recorded as the owner's change. Otherwise request them from the owner, as D-060 (6) did. |
| 2026-10-23-layout-review10#8 | process | process/flowsheet.yaml S1, S14, S15 | These are flowsheet data for the simulation owner:<br>- (a) The given S1 composition sums to 0.999999. That raises `pydexpi_composition_fractions` warnings on process/BFD.xml and process/PFD.xml, which are new since D-058 (validate 47 warnings).<br>- (b) S14 (cold HP N2) and S15 (cold GOX) carry calculated phase "liquid vf 0" with liquid densities (726 / 1,135 kg/m3), although they are saturated vapour column draws (D-061, D-063 (6)). The E-3101 sheet works around it, but the stored phase and density are wrong for any other use. | low | open | (a) Round one S1 fraction so the sum is 1 (a copy/rounding error). (b) Store S14 / S15 as saturated vapour (vapour fraction 1 given) and refill the properties. Both are for the simulation owner. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-23-layout-review9#1 | GOX-4002 S12 "stubs" 6.6 .. 7.1 m tall on CW / CWR T-post crossbars | medium | closed 374bfde | SP-8.9 / -11.0 / -15.4 / -19.9 are `t_post` from grade (e.g. SP-8.9 at [180.8, 50.4], column 0 .. 10.21 m, crossbar 0.45 m at 10.31 m; model). validate: no `layout-support-stub`. Computed: every declared member is ≥ 0.100 m from every pipe it does not carry; the smallest are the GAN-4004 S1 post-1 and LOX-4003 S3 SP-11.1 crossbars at 0.100 m. The steel-against-steel places found by the same scan: #2. |
| 2026-10-23-layout-review9#2 | lifting study gives no verdict on the B1 crane lifts | low | closed 5dfedb7 | layout/lifting-study.md: K-1101 (heaviest part) 34.65 t, E-1101 / E-1102 13.86 t and E-1103 10.395 t each read "building crane 40 t carries it". `cheme layout lifting --check` exit 0. |
| 2026-10-23-layout-review9#3 | no E-4101 bundle-pull envelope | low | closed 8370ac0 | zones.yaml Z-PULL-E4101 (maintenance, x 158.0 .. 163.5, y 37.1 .. 39.9, z 0 .. 3.2). validate: no clash, steel-in-way or pad-overlap finding. |
| 2026-10-23-layout-review9#4 | free-span messages offer to pin "place it by hand" proposals | low | closed 5dfedb7 | The CW-4001 / CWR-4002 / GAN-4004 warnings now read "no place clear of the other pipes for ... place the support by hand, not by pin". Only CWR-1004 SP-29.7 is still offered for a pin. |
| 2026-10-23-layout-review9#5 | datasheets / CW-3001 on states the flowsheet did not have | low | closed 56f3961 | ee7ec03 (D-061) put the states in the flowsheet; b2ac471 and 56f3961 (D-063) rebuilt the sheets on them:<br>- E-3101 on S7 / S9 / S17 at 13 C (5,242 kW, UA 721.6 kW/K);<br>- K-3101 185.9 / 191.6 kW, KT-3101 198.4 / 192.4 kW, S4C 59.9 C (simulated);<br>- E-3104 83.95 kW (checked here: LMTD 19.55 K, 29.67 m2);<br>- CW-3001 / CWR-3001 notes 7.3 m3/h.<br>DN150 stays until the E-3104 supplier's nozzles (D-060 (6), as review9 proposed). Remaining datasheet points: #1, #4, #5. |
| 2026-10-22-layout-review3#2 | PSV-3114 / PSV-3116 (and PSV-4127 / PSV-4128) tailpipes free above the valves | low | open | Unchanged: the guides wait for the relief reaction forces of the stress analysis (D-050, D-062 (4)). |
| 2026-10-22-layout-review3#3 | layout-operability warnings | low | open | 9, unchanged:<br>- XV-2101A, XV-2102A / B, XV-2103A / B, XV-2111A (TSA);<br>- PV-4109 / PV-4110 (tank roofs);<br>- XV-3105.<br>D-062 (4): mobile-platform access waits for the owner's platform type; the TSA and tank arrangements wait for the suppliers. |
| 2026-10-22-layout-review3#4 | rack free spans and support missing | low | open | free-span 5 (CWR-1004, LOX-3001 S2, CW-4001, CWR-4002, GAN-4004), support-missing 16 (10 accepted). These wait for the stress engineer (D-062 (4)). |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | D-050 / D-062 (4): waits for the vendor drawing; unchanged. |

## Drawing
`cheme validate` at 99f70af:
- P-01: 0 line-through-label, 0 line-crossing, 0 label-overlap, 0 label-far-from-owner,
  0 text-outside-frame, 0 title-text-overflow, 0 line-through-symbol;
- P-02: 0 in each count;
- P-03: 3 line-crossing (accepted in the drawing gate; `drawing-clean` passes), otherwise 0;
- P-04: 1 line-crossing (accepted, as P-03), otherwise 0.

P-01 changed (D-064). Tiles read, `cheme render pid/P-01.xml --png --tiles 3x2 --findings`: A1, A2,
A3, B1, B2, B3. Crops build/P-01_crop-90-105-135-160.png and build/P-01_crop-130-60-175-115.png
were also read.
- CD-1001 / CD-1002 are drawn from the E-1102 / E-1103 nozzles through a gate valve and a trap to
  "to drain" off-page connectors.
- TIA-1111 sits on AIR-1002 downstream of the check valve.
- The two D-064 notes are at B1.

No overlap is seen. The trap symbol (a square with a float) is legible. Its ISO 10628-2 number is
not checked (D-064). P-02 .. P-04 did not change; their tiles were not read.

## Layout
- `cheme layout build --check`: "layout/plant-model.yaml is up to date".
- `cheme layout lifting --check`: exit 0.

`cheme layout report` at 99f70af:
- **Lines:** 78 lines (CD-1001, CD-1002 new), all routed except 4 skipped segments: GAN-3002 and
  LN-3002 (D-028) and the two VNT-3004 breather segments. 0 unrouted.
- **Chains per method:** astar 32 (was 30: the two drains), open 8, pinned 147, rack 14. No
  `direct` and no `rack+direct`.

  | reason | chains |
  |---|---:|
  | local: above the pipe-way | 7 |
  | local: pipe-way | 7 |
  | local: pump run at grade | 4 |
  | local: rack detour too long | 2 |
  | local: rack run too short | 1 |
  | local: short run | 11 |
  | open end | 8 |
  | pinned | 147 |
  | rack: battery limit at a rack end | 13 |
  | rack: longer than local_max_m | 1 |

  The battery-limit rule ends rose 13 -> 15, the two drain hubs (routing.yaml, ASSUMED).
- **Rack fill:** unchanged from review9.

  | rack | 5 m | 6.5 m | 7 m | 8.5 m | 9 m |
  |---|---:|---:|---:|---:|---:|
  | PR1 | 61 % | | 37 % | | 25 % |
  | PR2 | | 6 % | | 6 % | |
  | PR3 | | 38 % | | 43 % | |

- **Model findings per rule:**

  | rule | count |
  |---|---|
  | clash-*, headroom, access-blocked, ladder-clearance, walkway-riser, steel-in-way, support-stub | 0 each |
  | zone-crossing, separation, vent-outlet, wall-penetration, tier | 0 each |
  | escape-ways, escape-travel, landing-width, egress-zone, operator-unknown | 0 each |
  | lifting, laydown, pad-overlap, spacing, building-spacing, zone-source | 0 each |
  | access-enclosed | 1 (accepted) |
  | operability | 9 (review3#3) |
  | free-span | 5 (review3#4) |
  | support-missing | 16, 10 accepted (review3#4) |
  | tray-span | 17 (accepted) |
  | tray-zone | 6 (2 accepted, 4 infos) |
  | tray-separation | 1 (accepted) |
  | nozzle-unconnected | 2 infos (D-028) |

  The 0 for steel-in-way does not test steel against steel (#2).
- **Objects:**
  - 45 equipment items;
  - 69 generated and 147 pinned pipes;
  - 114 generated in-line items;
  - 8 declared platforms;
  - 11 declared and 9 generated structures;
  - 28 declared zones.
- **validate:** 0 errors, 47 warnings:
  - 13 instrument-no-interlock;
  - 12 template-metadata;
  - 9 layout-operability;
  - 5 layout-free-span;
  - 4 line-crossing;
  - 2 titleblock-sheet;
  - 2 pydexpi_composition_fractions (#8).
- **`cheme check`:** every gate passes except `layout-review` (review9 is stale; this record is
  meant to make it current). That includes the detail gates `datasheets`, `layout-detail`,
  `electrical` and `hvac`.
- **`cheme process simulate --check`** (DWSIM 9.0.5): converged, 0 errors.
  - The warnings are the known D-059 deviations: S15 Ar 0.0297, S16 O2 0.0298, S10 Ar 0.0204.
  - S10 / S11 are subcooled against saturated (D-056).
  - The C-3101 / C-3102 condenser-reboiler differs by 286 kW.
  - The info is E2 (not simulated).
  - The values equal the datasheets: K-1101 5,967.85 / 6,308.5 kW, K-4101 2,183.8 / 2,308.4 kW,
    K-4102 218.6 / 237.6 kW, E-3104 83.95 kW, C-3101 3,535.6 kW / R 1.3377 / 94.71 / 99.56 K,
    C-3102 3,250.5 kW / 80.27 / 93.17 K.

**The D-064 drains in the model:**
- E-1102/N5 is at [60.2, 42.0, 0.633] on the shell bottom, 0.65 m east of saddle-2 (59.4). The
  bundle pull is to the west (x 46.2 .. 53.0), clear.
- CD-1001 drops to 0.333 m and runs north under the shell edge (y 42.8) to the hub at
  [60.2, 45.0, 0.3]: gate valve at y 42.98, trap at y 43.72, 3.3 m in all.
- E-1103/N5 is at [67.0, 36.0, 0.633], 0.75 m east of saddle-2 (66.1). The bundle pull is to the
  west (x 54.6 .. 60.5), clear.
- CD-1002 runs east to the hub at [69.0, 36.0, 0.3]: valve at x 67.64, trap at x 68.09, 2.3 m.
- Both are inside B1 at grade, outside the declared escape and maintenance zones in the plan crop.
  They add no clash, operability or support finding.
- The datasheet nozzle locations (N5 bottom, offset 3.2 / 3.0 m, elevation 0.8 m) agree with the
  model: no `datasheet-nozzle-layout` finding.

**Datasheets against D-058 / D-059 / D-061** (39 sheets, all `draft: false`, datasheets gate
passes):
- **Machines.** K-1101 5,968 / 6,309 kW and condensate 1,398.2 kg/h (S1C), K-4101 2,184 / 2,308
  kW, K-4102 218.6 / 237.6 kW, K-3101 185.9 kW gas / 191.6 kW shaft and KT-3101 198.4 / 192.4 kW
  (0.8 kW margin stated on both), S4C 59.9 C, S5B 8.25 bara / -124.7 C: each equals the stream
  table or the simulation run above, with its D-061 / D-063 source.
- **Coolers.** E-3104 83.95 kW / 29.67 m2 checked by hand (LMTD 19.55 K, F 0.9046). E-1102
  LMTD 37.68 K and area 459.1 m2 reproduce the sheet's own method; that method is #1. The
  E-1102 / E-1103 condensate (679 / 649 kg/h) reproduces from saturation at 40 C and
  3.21 / 5.80 bara.
- **Column states.** C-3101 -178.44 / -173.59 C (94.71 / 99.56 K), C-3102 -192.88 / -179.98 C,
  E-3103 3,536 / 3,250 kW, UA 2,296 kW/K, and the GOX 97.0 % (simulated) shown beside the
  99.5 % specification: consistent with D-059.
- **E-3101 / E-3102.** E-3101 warm end at 13 C. The E-3102 duty of 293 kW equals the E-3101
  cold-side surplus (D-061: ~295 kW). E-3102 has a cold-end approach of 10.0 K and a warm-end
  approach of 3.77 K. The ~78 kW refrigeration shortfall, the 99.5 % purity gap and the 27 K
  warm-end difference are stated on the sheets, as open decisions.
- **Units and markers.** Units are stated on every value. Vendor-only values carry `supplier`
  with a reason (except E-3101's area, #5). Calculated values cite the script or the simulation,
  and assumed ones are marked.

PNGs read (build/, rendered at 99f70af):
- build/layout-plan.png (plot plan);
- build/layout-plan_crop-36-24-80-56.png (B1: E-1102 / E-1103 with CD-1001 / CD-1002 and the
  drain hubs);
- build/layout-section-y42_crop-50-0-72-6.png (through E-1102 along its axis, saddles, CD-1001
  under the east end);
- build/layout-section-x60.2_crop-38-0-52-6.png (across E-1102 at the N5 drain: the drop and
  the run north to the hub at 0.3 m);
- the review9 sections build/layout-section-y68.png and build/layout-section-x133.png. Their
  inputs did not change except the support posts of D-062 (2): routing.yaml changed only by the
  drain hubs, structures.yaml only by GOX-4002 S12.

## Checked and fine
- **review9 fixes.** Each one has evidence in the Previous findings above. The GOX-4002 S12
  posts are clear of every pipe they do not carry (computed, ≥ 0.10 m).
- **Pipes against steel.** No declared support member is within 0.1 m of a pipe it does not
  serve, except the two at exactly 0.100 m (computed over 288 supports and 973 pipe runs).
- **Lifting.** 15 lifts, every lane clear. The B1 crane lifts carry their verdict. E-4101 is
  lifted from Z-PAD-A4C (36.96 t needed) and Z-PULL-E4101 is free.
- **Lists.** The line list is updated for CD-1001 / CD-1002 (DN25, PN10, flows from the
  datasheets) and for CW-1002, CW-3001 / CWR-3001, CW-4001, AIR-3002 / -3003 / -3006, WN-1001,
  WN-3002, GOX-4001 and GAN-4001 to the D-061 states. AIR-1006 is the exception (#3).
- **Equipment list.** The notes match the datasheets (K-1101, K-3101, KT-3101, K-4101, E-4101,
  K-4102).
- **Stage gates.** No stage sign-off was written and `checks/status.json` is untouched.

## Not checked
- **Structures.**
  - The structural design of the posts, the VP platforms and the rack bays: for the structural
    engineer.
  - Steel against platform and stair steel: the scan covered support steel only.
- **Pipe stress, free spans and PSV tailpipe guides** (review3#2, #4): for the piping stress
  engineer.
- **The vent and inert study** (zones ASSUMED, D-031): for a competent person.
- **The crane selection** (D-041 (7)): for the crane contractor.
- **Mobile elevating work platform access** to the 9 open valves (D-062 (4)): for piping
  layout and maintenance with the owner.
- **Supplier items.**
  - E-3101's 27 K warm end, the E-3101 / E-3102 / E-3103 areas, the column internals and
    diameters, and the compander matching: for the cold-box and compander suppliers.
  - The MAC separator type and the trap sizing (D-064): for the MAC supplier.
- **Thermodynamics.** The Peng-Robinson fit for O2 / Ar (D-059 limit) and the 99.5 % cycle: for
  the process owner.
- **P&ID tiles of P-02 .. P-04** (unchanged since review9).
