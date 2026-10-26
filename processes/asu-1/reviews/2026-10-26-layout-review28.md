---
topic: layout
reviewed_commit: 8ccc3234de6b689b057ce5164e4ad940c7718d29
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, electrical/cable-schedule.csv, equipment/datasheets, equipment/equipment-list.yaml, checks/checks.yaml, control/cause-effect.yaml, control/instrument-list.yaml, lca/lca.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: 8ccc323, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: 8ccc323, relation: depends-on}
  - {path: DESIGN.md, revision: 8ccc323, relation: depends-on}
  - {path: pid/P-04.xml, revision: 8ccc323, relation: analyses}
  - {path: process/flowsheet.yaml, revision: 8ccc323, relation: analyses}
reviewer: independent agent (layout-review28; did not author D-109 .. D-113 or the layout files)
reviewer_kind: agent
branch: claude/keen-lovelace-sd87qc
merge: pending
---
# Review: layout, twenty-eighth review (independent) of the D-109 .. D-113 branch

This is an independent review of branch `claude/keen-lovelace-sd87qc` at 8ccc323. It compares
the branch with origin/main (merge-base 87f65f0) and with layout-review27. These changes matter
for the layout:
- three new trip instruments: FSLL-2117 on P-02 (RG-2001), LSLL-3125 on a new C-3102 tapping I4
  on P-03, and PSHH-4152 on P-04 (GOX-4002). Each one is on its JB in
  `electrical/electrical-list.yaml`;
- the regenerated layout model, cable schedule (MC-JB-A3-1 goes from 36 to 48 pr), lifting
  study, MTO / estimate and LCA manifest.

No layout input file changed: site plan, placement, structures, zones and routing are the same.

Verdict: this review raises no critical or high finding of its own. The two high findings of
the parallel control-review6 are carried below as open. There are three medium findings. In #1 the new sump
low-low tapping is placed by default 22 m above the sump. In #3 the new SIL 1 transmitter
PSHH-4152 is out of reach in the model. In #5 two junction boxes are now over their declared
capacity. There are also three low findings.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-26-layout-review28#1 | P-03 / layout | C-3102 I4 (LSLL-3125), I3 (LICA-3102), I1 (PDI-3112) | C-3102 has no `nozzles:` entry for its instrument tappings, so the build places I1, I3 and I4 by default (build info `layout-nozzle-defaulted`: "I1, I3, I4"). It spaces them up the shell. The new LP sump low-low tapping I4 lands at z 41.975 m on the west face (point [126.733, 42.5, 41.975]). C-3102 stands at z 20, height 30, with E-3103 in its sump, so I4 is about 22 m above the sump it must measure. P-03 draws LSLL-3125 and LICA-3102 at the sump (crop build/P-03_crop-280-95-345-160.png). Adding I4 also moved the existing tappings: LICA-3102 (I3) from 39.65 to 35.0 m and PDI-3112 (I1) from 30.35 to 28.025 m, which shortened IC-LICA-3102 from 50 to 46 m and IC-PDI-3112 from 41 to 38 m with no layout change. The I4 transmitter sits in the 0.9 m gap to the west casing wall (bracket end x 126.013, wall at x 126). D-030 says casing instruments are brought out to the north platforms. The model therefore misplaces the SIL 2 sensor of I-14. Its cable length (IC-LSLL-3125, 58 m) and its access point rest on a default. | medium | open | In `layout/equipment-placement.yaml`, give C-3102 I1, I3 and I4 `elevation` and `angle_deg`: the sump tappings near z 20-23 m, on the north side towards P20. Then rebuild the model and the cables. |
| 2026-10-26-layout-review28#2 | layout | C-3102 manways 1-4, davit | The same default placement turned all four C-3102 manways and the top davit from the west face (neck [126.92, 42.5]) to 45 deg north-east (neck [130.471, 43.971]), because I4 now takes the west angle. No decision and no PROGRESS row mentions this. A P&ID tapping should not be able to move manway orientation. | low | open | Fix the manway orientation in the placement (or pin the tapping angles, see #1) and record it with the cold-box internals arrangement. |
| 2026-10-26-layout-review28#3 | P-04 / layout | PSHH-4152 (I-17, SIL 1), PT-4102 | PSHH-4152 senses GOX-4002 S7. The model puts it at the same point as PT-4102, [177.476, 64.16, 9.11], at the south edge of PR1. That point is 3.09 m east of the east edge of VP-5 (x 172.39-174.39, y 62.34-63.54, deck 8.35 m) and 4.96 m north of VP-4. No platform reaches it, and `operators:` declares no `remote_mount` for it. A SIL 1 trip transmitter needs access for proof tests. No rule sees this (see layout-review23#2). | medium | open | Put the PT-4102 / PT-4152 tappings on the S8/S9 run above VP-5 (x 172.4-174.4, 0.62 m north of its edge), or extend VP-5. Alternatively declare `remote_mount` stands on VP-5 with the impulse run, and record which one in D-111. |
| 2026-10-26-layout-review28#4 | P-02 / layout | FSLL-2117 (I-08) | FSLL-2117 is modelled at [90.084, 62.65, 5.695] on the level run of RG-2001 S2, 5.7 m above grade with no platform and no declared operator. The same segment drops to 1 m at the E-2101 inlet (x 90.084, y 55), still between the XV-2109 bypass tee and the heater as D-111 (2) requires. A switch on that drop would be in reach from grade. | low | open | Place the flow element on the vertical drop near E-2101, or declare a `remote_mount`. |
| 2026-10-26-layout-review28#5 | - | JB-A2-1, JB-A3-1, JB-A4-1 | `electrical/electrical-list.yaml` declares `capacity: 24` (instrument cables at most) for each junction box. The cable schedule now gives JB-A2-1 25 field cables (24 on main), JB-A3-1 25 (24) and JB-A4-1 27 (26 already on main). Neither `cheme layout build`, `cheme layout cables --check` nor `cheme validate` reports it. The new instruments pushed two boxes over a declared limit without a decision. | medium | open | Raise the capacity of these boxes with a reason (a larger box, ASSUMED), or add a box per area (for example a separate SIS box, see #6). Report the missing capacity rule to cheme-as-code. |
| 2026-10-26-layout-review28#6 | - | LSLL-3125 / LICA-3102, PSHH-4152 / PIC-4102, FSLL-2117 / TSHH-2107 | The screening LOPA (D-111) credits independent layers. Examples: the LICA-3102 low alarm before I-14 (SIL 2), and PSV-4122 / PIC-4102 around I-17. The SIF sensors share a junction box and multipair home run with the BPCS transmitters: JB-A3-1 / MC-JB-A3-1, JB-A4-1 / MC-JB-A4-1 and JB-A2-1. D-111 defers the separate SIS junction boxes to detail engineering, but the cable schedule, tray fill and MTO are sized as if no SIS boxes will exist, and the electrical list does not say so. | low | open | Add a note to the affected JBs in the electrical list (SIS sensors to move to SIS boxes in detail engineering, ASSUMED), so the tray fill and the estimate are read with that in mind. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-layout-review23#2 | The model has no tap point per line-mounted instrument; no rule checks reach of line-mounted transmitters. | low | open | Still true. PSHH-4152 is modelled at exactly the PT-4102 point, and #3 and #4 are cases the missing rule would have caught. |
| 2026-10-24-layout-review24#1 | The AI-3104 and FIC-4148 bubbles on P-04 are 0.5 mm apart and read as touching. | low | open | Unchanged: build/P-04_crop-10-40-50-80.png still shows the two bubbles touching at the line. |
| 2026-10-24-control-review5#3 | PIC-4101's tap drawn on S2 but modelled on S1. | low | open | PIC-4101 is not in `cheme diff origin/main --list`, so it is unchanged on this branch. |
| 2026-10-26-control-review6#1 | I-14 does not end the over-draw in several causes it is credited for (PV-4101B vents after the K-4101 trip). | high | open | Raised the same day on this branch by the parallel control review; I did not examine it here (outside layout). |
| 2026-10-26-control-review6#2 | On instrument-air loss with power on, nothing stops the running machines against the closed fail positions. | high | open | Parallel control review; not examined here. |
| 2026-10-26-control-review6#3 | I-14 closes FV-3111 and stops the LOX purge, against D-010 (2) and OBJ-3. | medium | open | Parallel control review; not examined here. |
| 2026-10-26-control-review6#4 | Fail positions checked on air loss only, not on a single signal loss. | medium | open | Parallel control review; not examined here. |
| 2026-10-26-control-review6#5 | D-111 asset tolerable frequencies disagree with the proposed risk matrix and D-083. | medium | open | Parallel control review; not examined here. |
| 2026-10-26-control-review6#6 | BPCS layers credited in the LOPA, contrary to the records and the independence rules. | medium | open | Parallel control review; not examined here. My #6 is the cabling side of the same independence question. |
| 2026-10-26-control-review6#7 | I-08 and I-10 are credited for each other and each is left without a SIL. | medium | open | Parallel control review; not examined here. |
| 2026-10-26-control-review6#8 | The seal-gas LOPA row starts optimistic and the trip does not stop the mechanism. | medium | open | Parallel control review; not examined here. |
| 2026-10-26-control-review6#9 | The D-110 ratio limits rest on FT-1101 alone and ignore the liquid draws. | medium | open | Parallel control review; not examined here. |
| 2026-10-26-control-review6#10 | The oxygen-fire trip I-13 is credited against an outcome that ignition already causes. | low | open | Parallel control review; not examined here. |
| 2026-10-26-control-review6#11 | The SIL 2 architectures are not stated, and FV-3111 (a BPCS control valve) is a final element of I-14. | low | open | Parallel control review; not examined here. |
| 2026-10-26-control-review6#12 | The LSLL-3125 tap is drawn above the LICA-3102 tap on P-03. | low | open | Parallel control review. The model has the same problem in a larger form: by default I4 is 7 m above I3 (my #1). |
| 2026-10-26-control-review6#13 | The machine-trip responses in the philosophy do not name the new interlocks. | low | open | Parallel control review; not examined here. |
| 2026-10-26-control-review6#14 | Not every open point in D-109 .. D-111 names its issue. | low | open | Parallel control review; not examined here. |

## Drawing
`cheme validate` at 8ccc323: 0 errors, 95 warnings. The counts per sheet:
- P-01: 0 line-through-label, 2 line-crossing (accepted), 0 label-overlap, 0
  label-far-from-owner.
- P-02: 0, 0, 0, 0.
- P-03: 0 line-through-label, 3 line-crossing (accepted), 0, 0.
- P-04: 0 line-through-label, 4 line-crossing (accepted), 0, 0.

On every sheet text-outside-frame, title-text-overflow and line-through-symbol are 0.
`drawing-clean` passes.

I rendered and read the regions of the new instruments:
- `build/P-02_crop-155-100-215-150.png`: FSLL-2117 under TSHH-2107 at E-2101, clear.
- `build/P-03_crop-280-95-345-160.png`: LSLL-3125 at the C-3102 sump between PDI-3112 and
  LICA-3102, clear.
- `build/P-04_crop-220-30-285-80.png`: PSHH-4152 on GOX-4002 below PIC-4102, clear.

I did not sweep the full sheets in tiles (see Not checked).

`cheme diff origin/main --list`:
- P-02: added Inst_FSLL2117; RG-2001 (1 added).
- P-03: added Inst_LSLL3125; C-3102 (4 added, nozzle I4).
- P-04: added Inst_PSHH4152; PIC-4102, TSHH-4104, TSLL-4113 and TSLL-4114 (1 modified each,
  the trip notes); GOX-4002 (1 added).

No changed item is `not drawn`.

## Layout
**Model checks.**
- `cheme layout build --check`: "layout/plant-model.yaml is up to date".
- `cheme layout cables --check`, `cheme layout lifting --check` and `cheme fmt --check` all exit
  0.

**`cheme layout report`.**
- Methods (chains): astar 26, open 8, pinned 166, rack 15. There is no `direct` or
  `rack+direct` chain.
- Skipped lines: GAN-3002 and LN-3002 (internal to the double column, D-028) and VNT-3004 (the
  casing breather).
- Battery-limit ends: 13.
- Rack fill: PR1 61 / 43 / 25 % at 5 / 7 / 9 m; PR2 6 / 6 %; PR3 48 / 43 %.

**Model findings per rule** (the same as layout-review27, all known and accepted or open there):
access-enclosed 1, free-span 2, laydown 1, lifting 4, nozzle-unconnected 2, operability 1
(XV-3105), support-missing 15 (info), tier 1, tray-separation 1, tray-span 17, tray-zone 6. There
is no `layout-pipe-disconnected` finding and no clash.

**What the regenerated model changes.**
- the provenance hashes;
- the C-3102 tappings and manways (#1, #2);
- three new field cables: IC-FSLL-2117 45 m to JB-A2-1, IC-LSLL-3125 58 m to JB-A3-1 and
  IC-PSHH-4152 31 m to JB-A4-1;
- MC-JB-A3-1: 31 pairs in use plus 20 % spare gives 37.2, so 48 pr; I checked the arithmetic;
- the instrument tray fill: IT-PR1-3 38 %, IT-PR1-4 37 %, IT-JB-A3-1 9 %. These are below the
  tray limit; the `electrical` gate passes.

No pipe route, platform or structure moved.

**Plan and sections read.**
- `build/layout-plan.png`: areas, racks PR1-PR3, B1 / B2, the cold box, crane pads, zones.
- `build/layout-section-y68.png`: the PR1 tiers at 5 / 7 / 9 m, with no collision seen.
- `build/layout-section-x129.png`: the C-3102 / C-3101 stack in CB-1 with P10-P40, RF and the
  north stair tower. The column base is at 20 m and the default tappings are high on the shell
  (#1).
- `build/layout-section-y64.2_crop-160-0-190-15.png`: GOX-4002 at 9.1 m along the PR1 south edge
  with VP-5 (8.35 m) to the west of the PT-4102 / PSHH-4152 point (#3).

**Distances.** I measured them from the model coordinates and the structures.yaml extents
(VP-4, VP-5, CB-1). `cheme show FSLL-2117 --layout` does not apply, because instruments are not
plot-plan items.

## Checked and fine
- `cheme check --no-write` before this record: every gate passes except `layout-review` (this
  record is meant to close it) and `issues-basic` / `issues-detail` (open issues #56, #57, #60,
  #61, #79, outside layout).
- The cable lengths of the new instruments are plausible for their JB positions.
- JB assignments match the instrument areas.
- The 48 pr multipair size follows the 20 % spare rule.
- The lifting study and the MTO / estimate changed only their model hash.
- The C-3102 datasheet gained nozzle I4, consistent with P-03.
- I found no third-party content in the changed layout and electrical files.

## Not checked
- Full tile sweeps of P-02, P-03 and P-04: only the changed regions were read.
- The HAZOP and C&E content itself; it is covered by hazop-review6.
- The SIS architecture and real JB sizes (detail engineering, the instrument and electrical
  engineers).
- Everything layout-review19 lists under "Not checked": relief sizing, pipe stress, supports,
  structural design and the area classification study (the respective discipline engineers).
