---
topic: layout
reviewed_commit: 6f4280902ec39e5b24cd3861f6bccf6775bc29bb
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, equipment/datasheets, checks/checks.yaml, pid/P-01.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 6f4280902ec39e5b24cd3861f6bccf6775bc29bb, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: 6f4280902ec39e5b24cd3861f6bccf6775bc29bb, relation: depends-on}
  - {path: DESIGN.md, revision: 6f4280902ec39e5b24cd3861f6bccf6775bc29bb, relation: depends-on}
  - {path: scripts/datasheet_sizing.py, revision: 6f4280902ec39e5b24cd3861f6bccf6775bc29bb, relation: analyses}
  - {path: process/flowsheet.yaml, revision: 6f4280902ec39e5b24cd3861f6bccf6775bc29bb, relation: analyses}
  - {path: process/simulation.yaml, revision: 6f4280902ec39e5b24cd3861f6bccf6775bc29bb, relation: analyses}
reviewer: Claude (independent review agent; did not author D-065 .. D-071, the layout files, the datasheets or the P&ID changes)
reviewer_kind: agent
branch: pass-d066
merge: pending
---
# Review: layout, eleventh review (independent) after review10, D-065 .. D-071

This is an independent layout, datasheet and P&ID-consistency review of branch `pass-d066` at
6f42809. It follows reviews/2026-10-23-layout-review10.md (99f70af) and covers:
- the review10 fixes (D-065: 1a593e1, 484a97c, aadf709, 648d75f, d9c45da, 8bbc3a1, c2c3649);
- the simulation owner's D-066 / D-067 (9e136c6, eb0000d), as the basis;
- the four follow-up commits: D-068 lists and datasheets (e4b9852), D-070 9.0 MW MAC motor
  (dddd7db), D-069 E-3105 and the chilled-water loop (c0dafe8), D-071 waste-N2 path (6f42809).

The reviewer designed none of this. cheme-as-code is the global `cheme`. Coordinates are site
metres from `layout/plant-model.yaml`. "Computed" means the reviewer's own hand check or
`cheme run scripts/datasheet_sizing.py` / `scripts/support_steel_scan.py` run at 6f42809
(output kept in build/, not committed).

`cheme diff 841c44a --list` (P&IDs, against the merge of #23 before the four commits):
- P-01 adds LIC-1114, LV-1114 (with actuator), CHWR-1001, CHW-3001, CHWR-3001, their off-page
  connectors and the tees Tee_CHW1001_E3105 / Tee_CHWR1001_E3105; C-1101 gains N7 and I3,
  C-1102 gains N5 and changes N1 / N2; WN-1001 / WN-1002 and CHW-1001 change;
- P-03 adds E-3105, TICA-3124, TV-3124 (with actuator), CHW-3001, CHWR-3001 and their
  connectors; AIR-3002 gains segment S7; E-3104, CW-3001 / CWR-3001, WN-1001, WN-3003,
  PV-3110A / B, S-3101 and Tee_WN3002_WN change;
- BFD / PFD: link data only (S1C, S3CU, S4D, S4E, step E3105).

Verdict: **no critical or high finding is open**. Every review10 finding is closed. New findings:
- five medium:
  - #1: the LP-top pressure check of D-071 leaves out the regeneration-gas path;
  - #2: the main air lines exceed the D-016 velocity limit at the D-066 flow, and D-068 did not
    check them;
  - #3: the E-3105 chilled-water drop runs over the K-4102 crane pad;
  - #4: the chimney tray has no overflow route and no blow-by protection;
  - #5: the B1 crane has 0.73 t of margin on an assumed motor weight;
- nine low (#6 .. #14).

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-23-layout-review11#1 | DESIGN.md / scripts | D-071 (2), RG-2001 .. RG-2003, E-2101, V-2101A/B, S-2101 | D-071 says "the LP column top pressure of 1.30 bara holds", but section 11 of the sizing script checks only the C-1102 path (WN-3002 -> WN-1001 -> PV-3110A -> C-1102 -> WN-1002). The regeneration gas, 18,486 kg/h (D-066, +13 %), also leaves E-3101 at about 115 kPa(a) (S17, 1.15 bara) and goes to the atmosphere. Its path:<br>- RG-2001 DN500, routed 131.2 m, ~21 m/s cold;<br>- E-2101;<br>- RG-2002 DN600, 52 m, ~23 m/s at 200 C;<br>- the adsorber bed in regeneration and the switching valves;<br>- RG-2003 DN600, 73.6 m;<br>- silencer S-2101.<br>That leaves about 13.7 kPa in all. The reviewer's rough Darcy estimate for the three lines alone is about 7 kPa (routed lengths, ~10 elbows each, K 0.75). That leaves only ~6-7 kPa for the heater, the bed, the valves and the silencer. No decision, datasheet or script gives an allowable for any of them (searched: DESIGN.md, the V-2101A and E-2101 datasheets). If the regeneration path needs more, the LP top must rise, or the regeneration flow falls short. | medium | open | Add the regeneration path to scripts/datasheet_sizing.py section 11 on the routed lengths. Put allowable pressure drops for E-2101, V-2101A/B in regeneration and S-2101 into their datasheets, as was done for C-1102 (3.3 kPa). Record in D-071 whether the 1.30 bara holds for both paths. |
| 2026-10-23-layout-review11#2 | line list | AIR-2001, AIR-2002, AIR-1005, AIR-1006 | D-016 sets gas lines at ≤ 20 m/s (waste / regeneration ≤ 25 m/s near atmospheric). D-068 (9) re-checked the waste-N2, GOX-4001, AIR-3002 / -3003 and water lines at the D-066 flow, but not the main air lines. Computed with DN as the diameter, the D-016 / script convention:<br>- AIR-2002 DN500: 110,870 kg/h at 5.6 bara, 15 C, rho ~6.8 kg/m3: ~23 m/s;<br>- AIR-2001 DN500: ~23 m/s;<br>- MAC interstage hot legs AIR-1005 DN900 (184 kPa(a), 99 C) ~29 m/s and AIR-1006 DN700 (326 kPa(a), 111 C) ~28 m/s.<br>At 98,060 kg/h (before D-066), AIR-2001 / -2002 ran at about 20.5 m/s. The drop of AIR-2001 / AIR-2002 / F-2101 adds to the MAC discharge pressure (5.8 bara). | medium | open | Re-check the main air lines at the D-066 flow in section 10, and either grow AIR-2001 / AIR-2002 (DN600) or record the deviation with its pressure drop in a decision. Mark AIR-1005 / AIR-1006 as the MAC supplier's sizing, with the D-066 flow as the enquiry basis. |
| 2026-10-23-layout-review11#3 | layout | CHW-3001 / CHWR-3001, Z-PAD-A4N | The pinned drops of CHW-3001 (x 146.6, z 2.35) and CHWR-3001 (x 147.0, z 2.7) run south from PR1 (y 64.9 / 64.5) to E-3105 (y 26.6 / 26.2), 38 m in the open. Between y 42 and 50 they cross the west strip of the crane pad Z-PAD-A4N (box x 146 .. 158, y 42 .. 50, z 0 .. 1), 0.6 / 1.0 m inside its edge (piping/routing.yaml lines 278-279; zones.yaml line 125). K-4102 is lifted from that pad by a mobile crane needing 38.5 t (layout/lifting-study.md). The pad box is only 1 m high, so no clash, pad or lifting rule fires, yet a crane carrier, outrigger or counterweight swing at 2.35-2.7 m meets the pipes. The runs also have no supports (support-missing infos of 50.4 / 52.6 m, #14). Plan build/layout-plan.png. | medium | open | Route the drops west of x 146 (outside the pad), or take them on sleepers or posts clear of the pad. Ask cheme-as-code for a rule that tests pipes and steel above a crane pad's footprint up to the crane's swing height. |
| 2026-10-23-layout-review11#4 | P-01 / datasheets | C-1101 chimney tray, LIC-1114 / LV-1114, C-1102 | The new closed loop rests on one level loop between a 5.7 bara column and an atmospheric tower (C-1102 design 1 barg):<br>- (a) **Blow-by.** If the tray loses its seal (LIC-1114 fails, LV-1114 sticks open), air blows into C-1102. The reviewer's rough estimate for choked flow through a DN150 opening at 5.7 bara is ~80-90 t/h, more than the 58 t/h design gas of C-1102. D-069 leaves this open.<br>- (b) **Overflow.** LV-1114 fails closed (instrument-air failure). Neither the C-1101 datasheet nor D-069 says where the 34.4 m3/h then goes: no overflow from the tray to the lower section is specified. A flooded upper bed risks water carryover into AIR-1004 and the TSA.<br>- (c) The chimney tray is not shown on the C-1101 symbol on P-01 (the mist eliminator is). | medium | open | (b) Specify the chimney-tray overflow (downcomer) to the lower section and its capacity in the C-1101 datasheet. (a) Add an independent low-low tray level (LSLL) closing a tight-shut valve in CHWR-1001 to control/cause-effect.yaml, and size the C-1102 blow-by relief case before the HAZOP. (c) Draw the tray internal. |
| 2026-10-23-layout-review11#5 | layout | B1 crane, K-1101 motor | The 40 t B1 crane carries the 9 MW motor at 39.27 t with the allowances: 0.73 t (1.8 %) to spare (layout/lifting-study.md line 9). The 34 t is ASSUMED, pro rata to the rating from an ASSUMED ~30 t (D-070 (4)). That margin is far smaller than the uncertainty of a pro-rata weight. D-070 already says a motor above 34.6 t needs a 50 t crane. The crane size drives the B1 crane girders, columns and roof height. | medium | open | Get the motor supplier's weight before the B1 structural design, or carry the 50 t crane until then, and record which in D-070. |
| 2026-10-23-layout-review11#6 | electrical / datasheets | K-4101 motor | The K-4101 datasheet (D-068 (3)) says the 2.3 MW motor is 5 % short of the API 617 110 % (2,414 kW). It runs at 2,262 kW electric, 98 % of its rating, yet the electrical list (K-4101, K-4101-MV) and the TR-1 sum still carry 2,300 kW with no margin. | low | open | Carry the next motor size in the lists (ASSUMED, until the vendor confirms), or record a decision that accepts 2.3 MW with the vendor's confirmation as a hold. |
| 2026-10-23-layout-review11#7 | DESIGN.md / P-03 | E-3105 (and E-3104), TV-3124 | D-067 / D-069 say a tube leak "cannot put water into the dry air": the water side is ~3.5 bara (E-3105 datasheet) against 8.45 bara air. That holds only while the booster runs. When the compander or the MAC is stopped and AIR-3002 depressurises, the return line's static head (C-1102 top ~20 m) still keeps the water side at ~2-3.5 bara. TV-3124 fails open, so a leaking E-3105 can wet the dry air ahead of E-3101 during a standstill. E-3105 also has no water-side isolation for maintenance (no block valve on CHWR-3001 by design), so working on it stops the loop and the DCAC upper section. | low | open | State the standstill case in D-069. Isolate the chilled water to E-3105 on a compander trip (a tight-shut valve on CHW-3001 and a drain or vent on the return, closed only with the air side pressurised or the cooler drained), or rely on a moisture check of AIR-3002 / E-3101 before restart, stated. Reconsider a locked-open return valve with a thermal relief for maintenance. |
| 2026-10-23-layout-review11#8 | layout / datasheet | E-3105 nozzles | equipment-placement.yaml puts:<br>- air in / out (N1 / N2) on the shell top only 0.9 m apart (3.6 / 4.5 m from the front end of a 5 m shell);<br>- the tube-side chilled water (N3 / N4) on the shell's south side at 2.2 / 4.0 m.<br>Shell-side air counter-current to tube-side water needs the shell nozzles at opposite ends, and the tube-side nozzles on the channel and return heads. With the bundle pulled to the west, the channel is at the west end. The E-3105 datasheet passes these locations on as the enquiry basis. | low | open | Place N1 / N2 at the two ends of the shell and N3 / N4 on the heads (or state a U-tube with both water nozzles on the west channel), and update the datasheet nozzle locations. |
| 2026-10-23-layout-review11#9 | layout | Z-N2-V1B, PR3 north end | Z-N2-V1B (sphere at (190, 114, 8), r 10 m) reaches beyond V1 (x ≥ 182) to x 180 at 6-10 m height. That takes in the PR3 north end: the step-off from the PR3 end ladder (base (180.9, 118.6), Z-LAD-PR3) onto the 8.5 m tier at ~(182, 118, 8.5) lies 9.0 m from the centre. The ladder itself is 10.2 m away in plan, 0.2 m outside. D-071 (4)'s control ("V1 fenced, entry with a personal O2 monitor") does not cover PR3, which stands outside V1. The rules report nothing because the rack tier is not a walkway. Plan build/layout-plan_crop-160-95-200-135.png. | low | open | Extend the access control to the PR3 north end (sign, O2 monitor, no work on PR3 during a bypass), or limit the zone by the vent study. |
| 2026-10-23-layout-review11#10 | line list / DESIGN.md / scripts | WN-3003, AIR-1006 | Figures that disagree:<br>- WN-3003 line-list note: "DN600: 46 m/s and 18 kPa ... DN900 ... 3.3 kPa". D-071 (2) table and script section 11 give 20.3 / 3.63 kPa. The D-071 text says "at DN600 the line alone would take 24 kPa"; 24 kPa is WN-3002 + WN-3003 (3.57 + 20.3), not the line alone.<br>- The AIR-1006 note still says "679 kg/h condensate drained to CD-1001"; it is 767 kg/h (D-068 (2), CD-1001 note).<br>- Script section 10 prints a line "AIR-3007" that does not exist (AIR-3002 is kept through E-3105, D-069 (1)). | low | open | Correct the WN-3003 and AIR-1006 notes and the D-071 sentence in a new decision. Rename the script's label to AIR-3002 (after E-3105). |
| 2026-10-23-layout-review11#11 | datasheets | E-4101, E-4102, K-3101, KT-3101, K-1101, E-1103 | review10#4 is fixed in its own terms, but the D-068 rework mixed the mappings. The script headers now read "section 2 (DESIGN.md D-068 (3))" and "section 4 (DESIGN.md D-068 (4))", while 23 citations still read "section 2 (DESIGN.md D-063 (5))" (E-4101 / E-4102 / K-4101) and 5 read "section 4 (DESIGN.md D-063 (4))" (K-3101, KT-3101). Ten "section 1 (DESIGN.md D-063 (2))" citations sit beside fifteen "section 1 (DESIGN.md D-068 (2))". Some values under the old citation are slightly stale, e.g. the E-4101 stage 1 discharge 362.02 K against the script's 361.98 K. | low | open | Cite the current header of each section (or both decisions), and refresh the values printed by the current script. |
| 2026-10-23-layout-review11#12 | layout | CWR-4002, LIN-3001 S1 post-2 | The rebuild moved the generated rack lane of CWR-4002 on the PR1 5 m tier from y 68.949 to 69.218 (plant-model at 841c44a vs 6f42809). `scripts/support_steel_scan.py` now finds the LIN-3001 S1 post-2 column at (141.98, 69.4) 0.025 m from the CWR-4002 pipe; D-065 (5) had none within 0.1 m. No clash rule fires. | low | open | Pin the CWR-4002 lane where it was, or move the post. Rerun the scan after every rack change. |
| 2026-10-23-layout-review11#13 | P-01 | TV-1105, LV-1114 labels | The "TV-1105" tag text stands right beside the new LV-1114 actuator, nearer to it than to TV-1105 on CHW-1001, and "F.C." stands to the left of both. A reader can take the LV-1114 actuator for TV-1105. The lint counts 0 label-far-from-owner. Crop build/P-01_crop-205-90-265-125.png. | low | open | Move the TV-1105 tag to the right of its valve and put "F.C." against the LV-1114 actuator. |
| 2026-10-23-layout-review11#14 | layout | CHW-3001, CHWR-3001, CHWR-1001 supports | 5 new support-missing infos:<br>- P-03 CHW-3001 S1 50.4 m and CHWR-3001 S1 52.6 m level at 2.35 / 2.7 m;<br>- P-01 CHWR-1001 S2 21.7 m, CHWR-3001 S1 15.0 m, CHW-3001 S1 3.2 m.<br>The DN50 lines pinned on PR1 at y 64.5 / 64.9, z 5.03 do not change the reported PR1 5 m fill (4.90 of 8 m, 61 %, as at review10), so the rack model does not count them on the tier. D-069 lists the supports as open. | low | open | Declare the supports (sleepers or T-posts for the grade runs, intermediate rack steel or a larger carrier line on PR1), and check that the pinned DN50 runs sit in a counted tier lane. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-23-layout-review10#1 | E-1102 / E-1103 condensing duty at the gas LMTD | medium | closed 484a97c | D-065 (2): two-zone sizing in script section 1. At 6f42809 (D-068 flows), computed: E-1102 dew point 47.24 C, zone 1 324.7 m2 (LMTD 41.69 K, F 0.948), zone 2 271.7 m2 (integrated dT 17.33 K), total 596.4 m2. E-1103 557.6 m2. These equal the datasheets and D-068 (2). |
| 2026-10-23-layout-review10#2 | support steel through other supports' steel | medium | closed d9c45da | `cheme run scripts/support_steel_scan.py`: "0 steel pairs below 0.0 m" over 265 declared supports and platforms. The one new pipe-to-steel near place is #12. |
| 2026-10-23-layout-review10#3 | D-064 drain sum, AIR-1006 pressures | low | closed aadf709 | D-065 (3); the AIR-1006 note reads ~3.26 / 3.21 bara. Its condensate figure went stale again with D-068: #10. |
| 2026-10-23-layout-review10#4 | datasheet citations to D-063 items | low | closed 1a593e1 | Script headers and citations read "section n (DESIGN.md D-0xx (m))". The D-068 rework mixed them again: #11. |
| 2026-10-23-layout-review10#5 | E-3101 operating block, draft headers | low | closed 648d75f | E-3101 carries the five passes. The final sheets carry the four-line "Final (`draft: false`)" header (e.g. C-1101.yaml lines 1-4). |
| 2026-10-23-layout-review10#6 | drain traps without strainer, test point, tags | low | closed 8bbc3a1 | HV-1112 / HV-1113 and ST-1112 / ST-1113 on P-01 (tile A2: HV-1113 / ST-1113 legible); integral strainer and test valve in the CD-1001 / CD-1002 notes; trap centres 0.5 m (D-065 (6)). |
| 2026-10-23-layout-review10#7 | S1C / S3C links added without the owner | low | closed 9e136c6 | The simulation owner's D-066 / D-067 commit rewrote process/flowsheet.yaml and kept the S1C (CD-1001 / CD-1002) and S3C (CWR-1001, LIC-1106) links. Its message records "D-065 (7) requests done". The later link-only edits (S3CU, S4D, S4E, E3105) are within this pass's rules. |
| 2026-10-23-layout-review10#8 | S1 sum, S14 / S15 stored as liquid | low | closed 9e136c6 | validate at 6f42809: no `pydexpi_composition_fractions` warning. S14 phase "vapor, ASSUMED (D-065 (7), D-066)" (flowsheet.yaml line 614). |
| 2026-10-22-layout-review3#2 | PSV tailpipes free above the valves | low | open | Unchanged: the guides wait for the stress analysis (D-050, D-062 (4)). |
| 2026-10-22-layout-review3#3 | layout-operability warnings | low | open | 9, unchanged (XV-2101A, XV-2102A / B, XV-2103A / B, XV-2111A, PV-4109, PV-4110, XV-3105). PV-3110B now has a remote operator (D-071 (3)) and no finding. |
| 2026-10-22-layout-review3#4 | rack free spans and support missing | low | open | free-span 5, the same lines (CWR-1004, LOX-3001 S2, CW-4001, CWR-4002, GAN-4004). support-missing 21, of which 10 accepted; the 5 new ones are #14. |
| 2026-10-21-layout#15 | KT-3101 casing extension not modelled | low | open | Unchanged; waits for the vendor drawing (D-050 / D-062 (4)). |

## Drawing
`cheme validate` at 6f42809:
- P-01: 0 line-through-label, 1 line-crossing (CHWR-1001 over CHW-1001, accepted in
  checks/checks.yaml with the D-069 pocket reason), 0 label-overlap, 0 label-far-from-owner,
  0 text-outside-frame, 0 title-text-overflow, 0 line-through-symbol;
- P-02: 0 in each count;
- P-03: 3 line-crossing (accepted, unchanged), otherwise 0;
- P-04: 1 line-crossing (accepted, unchanged), otherwise 0.

The `drawing-clean` gate passes.

Tiles read (`cheme render ... --png --tiles 3x2 --findings`):
- P-01: A2 (C-1101 with N7 / LIC-1114 / LV-1114 F.C., the accepted crossing at (250, 116)), A3
  (C-1102 with CHWR-1001 into N5 at the distributor, CW-1003 make-up, WN-1002 DN 900, WN-1001
  DN 1000), B2 (the CHW-3001 tee on CHW-1001 upstream of TV-1105), B3 (P-1102A/B, the
  CHW-3001 / CHWR-3001 connectors);
- P-03: A1 (E-3105 between E-3104 and the PSV-3119 tee, TICA-3124 on AIR-3002 S2, TV-3124 F.O.
  on the supply), B1 (E-3104 with CW-3001 / CWR-3001, the CHW-3001 / CHWR-3001 connectors
  to / from P-01);
- crop build/P-01_crop-205-90-265-125.png (#13).

P-01 A1 / B1 and P-03 A2 / A3 / B2 / B3 were not read: they did not change except the WN-1001
and WN-3003 DN texts, which validate compares with the line list (0 DN mismatch).

Engineering checks on the changed sheets:
- AIR-3002 runs K-3101 -> E-3104 (S1) -> E-3105 (S7) -> PSV tee (S2), all DN200, as the line
  list says, and E-3105 sits upstream of PSV-3119, which still protects it.
- TICA-3124 actuates TV-3124 on CHW-3001 through its actuating system (`cheme show TICA-3124`).
- CHW-3001 / CHWR-3001 are DN50 on both sheets.
- No valve sits on CHWR-3001 (#7). There is no isolation on the E-3105 or E-3104 water side,
  which is the plant's style for its coolers at this stage.

## Layout
- `cheme layout build --check`: "layout/plant-model.yaml is up to date".
- `cheme layout lifting --check`: exit 0.

`cheme layout report` at 6f42809:
- **Lines:** 81, all routed except the 4 skipped segments (GAN-3002, LN-3002, D-028; the two
  VNT-3004 breather segments). 0 unrouted. New: CHW-3001 (157.1 m), CHWR-3001 (152.8 m) and
  CHWR-1001 (78.7 m); WN-1001 95.5 m, WN-3003 116.6 m.
- **Chains per method:** astar 31, open 8, pinned 153, rack 15. No `direct` and no
  `rack+direct`.

  | reason | chains |
  |---|---:|
  | local: above the pipe-way | 7 |
  | local: pipe-way | 7 |
  | local: pump run at grade | 4 |
  | local: rack detour too long | 2 |
  | local: rack run too short | 1 |
  | local: short run | 10 |
  | open end | 8 |
  | pinned | 153 |
  | rack: battery limit at a rack end | 13 |
  | rack: longer than local_max_m | 2 |

- **Rack fill:**

  | rack | 5 m | 6.5 m | 7 m | 8.5 m | 9 m |
  |---|---:|---:|---:|---:|---:|
  | PR1 | 61 % (4.90 of 8 m; #14) | | 44 % (was 37 %, WN-1001 DN1000) | | 25 % |
  | PR2 | | 6 % | | 6 % | |
  | PR3 | | 48 % (was 38 %, WN-3003 DN900) | | 43 % | |

- **Model findings per rule:**

  | rule | count |
  |---|---|
  | clash-*, headroom, access-blocked, ladder-clearance, walkway-riser, steel-in-way, support-stub | 0 each |
  | zone-crossing, separation, vent-outlet, wall-penetration | 0 each |
  | escape-ways, escape-travel, landing-width, egress-zone, operator-unknown | 0 each |
  | lifting, laydown, pad-overlap, spacing, building-spacing, zone-source | 0 each |
  | tier | 1 (WN-1001 3.0 m under the 7 m tier, accepted in checks.yaml with the D-071 (3) reason; the reviewer agrees: the riser is boxed in by bent 17, AIR-2002 and WN-3003) |
  | access-enclosed | 1 (accepted) |
  | operability | 9 (review3#3) |
  | free-span | 5 (review3#4) |
  | support-missing | 21, 10 accepted (review3#4, #14) |
  | tray-span | 17 (accepted) |
  | tray-zone | 6 (2 accepted, 4 infos) |
  | tray-separation | 1 (accepted) |
  | nozzle-unconnected | 2 infos (D-028) |

  The pad-overlap 0 does not test pipes above a crane pad's 1 m box (#3). The steel-in-way 0
  does not test the CWR-4002 / post near place (#12).
- **Objects:**
  - 46 equipment items (E-3105 new);
  - 71 generated and 153 pinned pipes;
  - 116 generated in-line items;
  - 8 declared platforms;
  - 11 declared and 9 generated structures;
  - 30 declared zones (Z-N2-V1B, Z-N2-WN1002 new).
- **validate:** 0 errors, 46 warnings:
  - 13 instrument-no-interlock;
  - 12 template-metadata;
  - 9 layout-operability;
  - 5 layout-free-span;
  - 5 line-crossing (P-01 1, P-03 3, P-04 1);
  - 2 titleblock-sheet.

  The 2 `pydexpi_composition_fractions` warnings of review10 are gone (9e136c6).
- **`cheme check`:** every gate passes except `layout-review` (this record is meant to make it
  current). That includes `layout-3d`, `layout-rules`, `lifting-study`, `mto`, `lca`,
  `electrical`, `hvac`, `datasheets` and `drawing-clean`.

PNGs read (build/, rendered at 6f42809):
- build/layout-plan.png (plot plan);
- build/layout-plan_crop-120-20-150-45.png (E-3104 / E-3105, the CHW-3001 / CHWR-3001 drops
  and their run west under the compander lift lane);
- build/layout-plan_crop-160-95-200-135.png (V1: S-3101 with Z-N2-V1 and Z-N2-V1B, the
  WN-3003 DN900 arrival, PR3 north end);
- build/layout-plan_crop-30-50-80-75.png (C-1102, WN-1001 / WN-1002, Z-N2-WN1002);
- build/layout-section-y68.png (along PR1: WN-1001 DN1000 on the 7 m tier from x ~59 to the
  riser near x 133; the DN50 chilled-water lines on the 5 m tier; the Z-N2-WN1002 sphere
  22.8 .. 35.8 m over C-1102);
- build/layout-section-x133.png (through the compander and the cold box: E-3104 / E-3105 at
  grade south of K-3101, AIR-3002 risers, CB-1).

**Measured (`cheme show E-3105 --layout`):**
- E-3104 1.6 m (centres 2.5 m), K-3101 5.8 m, KT-3101 5.9 m;
- CB-1 9.6 m, road R1 16.6 m, PR1 35.5 m.

**Zones:**
- Z-N2-WN1002: the sphere (55, 60, 29.33), r 6.5 m, has its bottom at 22.8 m on the axis. At
  the shell radius (2.25 m) it is at 23.23 m, 0.03 m above the 2.2 m headroom over the 21.0 m
  top platform. The vent rule passes, but only just.
- Z-N2-V1B: see #9.

## Checked and fine
- **D-066 / D-067 values in the lists and datasheets** against the sizing-script run and the
  simulation figures it quotes:
  - K-1101: 113,329 kg/h; 6,763 kW gas; DWSIM 6,747 kW shaft / 7,133 kW electric; 7,478 kW
    pro rata at 90,000 Nm3/h; 7,254 kW output; 7,979 kW at 110 %; +12.8 % on 9.0 MW.
  - F-1101 rated 90,000 Nm3/h; AIR-1001 17.6 m/s.
  - E-1101 1,892 kW / 391.8 m2; E-1102 2,799 kW / 596.4 m2 / 767.3 kg/h; E-1103 2,754 kW /
    557.6 m2 / 734.3 kg/h. In all 7,445 kW against Q1 7,560 kW.
  - C-1101 710 / 640 kW, 34.4 m3/h chilled water at 10 -> 26 C (9.562 kg/s), liquid load
    2.74 m3/(m2 h).
  - C-1102 703 kW, 856 / 1,173 kg/h evaporated, make-up 619 / 937 kg/h; F 0.906 Pa^0.5;
    allowable 3.3 kPa in the datasheet.
  - V-2101A/B: water 170.2 kg/h (PR 147.3), CO2 67.7 kg/h. E-2101: 987 kW gas, 1.13 MW peak.
  - E-3104 126.1 kW / 12.41 K / 63.5 m2 / 10.9 m3/h; E-3105 63.3 kW / 7.21 K / 54.8 m2 /
    5.44 m3/h (48.5 kW at the 18.5 C alarm).
  - E-3101 5,835 kW, 2 K warm end, UA ~1,796 kW/K. E-3102 304.1 / 312.7 kW, UA 45 kW/K.
  - C-3101 Rmin 1.20, R 1.391, Nmin 15.9; C-3102 Ar/O2 Nmin 10.9.
  - Purities 99.71 / 99.81 % and 0.2 ppm.
  - P-1102A/B 44 m3/h, 75.7 m, NPSHa 11.8 m, 12.1 kW, 15 kW motor.
- **Waste-N2 hydraulics** (D-071 (2)). The C-1102 path reproduces from the script and the
  reviewer's hand check (DN1000: rho ~1.27 kg/m3, 16.2 m/s, ~1.7 kPa; DN700 33.6 m/s,
  7.5 kPa). The budget is 130 - 2.1 - 12.9 = 115; - 3.57 - 1.66 = 109.8; - 4.7 PV-3110A =
  105; - 3.3 C-1102 - 0.44 WN-1002 = 101.3 kPa(a): it closes. The regeneration path is #1.
- **Electrical** (D-070).
  - TR-1 connected 13.6 MVA: (9,000 + 2,300 + 315) / (0.9 x 0.96) + 2,500 kVA, x 0.85.
  - Running ~12.3 MVA.
  - DOL start ~62 MVA against 200 MVA short-circuit: ~24 % dip. A reduced-voltage start is
    recorded.
  - The cable schedule is current (`electrical` gate).
- **Lifting:**
  - 15 lifts, every lane clear; K-1101 at 39.27 t on the B1 crane (#5).
  - E-3105 (3.5 t, ASSUMED) is not a heavy lift.
  - The E-3104 / E-3105 bundle pulls to the west are free in the plan crop.
- **Routing changes** (D-071 (3)):
  - AIR-2002 lane moved to y 66.5;
  - VP-1 0.35 m west, with PV-3110B on a remote operator;
  - the WN-3003 DN900 PR3 down-leg is clear of VNT-4002 / VNT-4003;
  - no clash.
- **Stage gates:** no stage sign-off was written and `checks/status.json` is untouched.

## Not checked
- **`cheme process simulate --check`** was not rerun. The simulation values were taken from
  process/simulation-run.json as the sizing script prints them.
- **Hydraulics and vendors:**
  - the regeneration-path hydraulics (#1), beyond the reviewer's rough estimate;
  - the cold-box waste-passage drops (12.9 kPa), PV-3110A / B sizing, and C-1102 / S-3101 at
    58 t/h: for the vendors (D-071 open).
- **The C-1102 blow-by relief case and the chimney-tray protection (#4):** for process safety
  and the HAZOP.
- **Packing wetting** in the C-1101 upper section and C-1102 (2.5-2.7 m3/(m2 h)): for the
  packing supplier.
- **The motor starting study, the single-line diagram, MV cable sizing and the motor weights:**
  for the electrical engineer and the motor supplier.
- **Structures:** the structural design of the B1 crane, the posts, the VP platforms and the
  rack bays: for the structural engineer.
- **Pipe stress, free spans, supports of the new chilled-water runs and the PSV tailpipe
  guides:** for the piping stress engineer.
- **The vent and inert study** (Z-N2-V1B, Z-N2-WN1002 ASSUMED screening, D-031): for a
  competent person.
- **The P&ID tiles not named under Drawing.**
