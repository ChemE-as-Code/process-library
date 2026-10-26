---
topic: layout
reviewed_commit: a793d37d4b397f229afa41db8163fac005b93d9e
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, electrical/cable-schedule.csv, equipment/datasheets, equipment/equipment-list.yaml, checks/checks.yaml, control/cause-effect.yaml, control/instrument-list.yaml, lca/lca.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: a793d37, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: a793d37, relation: depends-on}
  - {path: DESIGN.md, revision: a793d37, relation: depends-on}
  - {path: pid/P-04.xml, revision: a793d37, relation: analyses}
  - {path: process/flowsheet.yaml, revision: a793d37, relation: analyses}
reviewer: Claude (independent layout review agent; did not author D-114, D-115 or the layout files)
reviewer_kind: agent
branch: claude/keen-lovelace-sd87qc
merge: pending
---
# Review: layout, twenty-ninth review (independent), confirming the D-114 layout fixes

This is an independent review of branch `claude/keen-lovelace-sd87qc` at a793d37. It checks the
layout-review28 findings against D-114 (6), commit 0841d30. These are the changes it looks at:
- the placement now gives C-3102 tappings I1 / I3 / I4, and `operators:` gives them
  `remote_mount` stands on CB-1 P20;
- the C-3102 datasheet gives the tapping locations;
- three SIS junction boxes are new (JB-A1-S1, JB-A3-S1, JB-A4-S1), and the heater trips move to
  JB-A2-2;
- PSLL-1116 has a declared point and a cable;
- the model, the cable schedule, the lifting study and the MTO / estimate are regenerated.

a793d37 changed only the HAZOP files and DESIGN.md. Scope and basis are as in layout-review28.

**Verdict.** Of the six layout-review28 findings, four are closed:
- #1, the tappings, now low on the north side;
- #2, the manways back on the west face;
- #5, every junction box within 24 cables;
- #6, the SIS boxes exist.

Two stay open: #3, PSHH-4152 (medium), and #4, FSLL-2117 (low). The decision is recorded in the
instrument list, but neither the model nor `operators:` nor the electrical list's
`instruments:` points carry it.

This record raises 3 new low findings:
- the new C-3102 transmitter stands are modelled inside the cold box casing;
- two new SIS trays are unsupported and their warnings are not accepted;
- the SIS segregation leaves out I-07, I-08 and I-15 / I-16.

The record finds nothing critical or high of its own. control-review7's open findings are
carried below. The two high findings of control-review6 are closed.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-26-layout-review29#1 | P-03 / layout | C-3102 I1, I3, I4 stands (PDI-3112, LICA-3102, LSLL-3125) | The tappings are now where they should be, on the north side at z 21.0 (I4), 21.6 (I3) and 23.5 (I1). The base of the bottom head is at z 20, and the tangent line is at 21.05. `operators:` says each impulse line goes "out through the north casing to a stand on CB-1 P20". But the model draws the stands at the nozzle's plan position: I3 at [129.773, 45.385, 20.0 .. 21.3] and I4 at [128.227, 45.385, 20.0 .. 21.3], with the transmitters at y 45.27. For I1 it draws a shell bracket at [130.43, 44.98, 23.2]. The CB-1 north casing wall is at y 47.0 .. 47.2 (origin y 38 + span 9), and P20 is at y 47.2 .. 48.7, deck 20 m. Every stand and transmitter is therefore about 1.6 to 2 m inside the perlite-filled casing, on no floor. The SIL 2 transmitter of I-14 is thus modelled where nobody can reach it, and its cable IC-LSLL-3125 (33 m) starts there. No casing opening is declared for the impulse lines, unlike the process lines, which have sleeves. No rule reports this, because a `remote_mount` counts as reachable. | low | open | Give the three transmitters model points on P20, for example through the electrical list's `instruments:` points (as for AIA-3122 and PSLL-1116), or `length_m` on the operators. Declare the impulse-line sleeve(s) in the CB-1 north-wall openings. Report to cheme-as-code that a `remote_mount` stand is drawn at the nozzle's plan position rather than on the named platform. |
| 2026-10-26-layout-review29#2 | layout | IT-JB-A1-S1, IT-JB-A3-S1 | The new SIS instrument trays raise two `cheme.layout-tray-span` warnings that nobody has accepted: IT-JB-A1-S1 runs 10.6 m and IT-JB-A3-S1 runs 13.5 m level with no steel within 1 m. The trays of the neighbouring BPCS boxes have the same findings, and those are accepted in checks/checks.yaml (IT-JB-A1-1 13.8 m, IT-JB-A3-1 14.0 m). These two are the reason validate's warning count rose from 95 to 97. | low | open | Run the SIS trays on the BPCS boxes' supports (posts or the same steel), and accept them with the same reason and the current lengths. |
| 2026-10-26-layout-review29#3 | - | JB-A2-2, JB-A4-2, SIS multipairs | The SIS segregation of D-114 (6) is incomplete. AIA-2102, the sensor of I-07 (SIL 1, LOPA row 3), and FSLL-2117 (I-08) share JB-A2-2 and MC-JB-A2-2 with FIC-2105. FIC-2105 is the transmitter whose failure is I-08's initiator, the very reason FSLL-2117 exists (H02-A2). TSLL-4113 / TSLL-4114 (I-15 / I-16, SIL 1, row 11) share JB-A4-2 with PIC-4111 / PIC-4112, whose valves are row 11's initiator. The SIS home runs MC-JB-A1-S1, -A3-S1 and -A4-S1 also run in the same instrument trays as the BPCS multipairs to CR-1. That is acceptable at basic engineering, but not stated. | low | open | Move AIA-2102 (and the heater relay's FSLL-2117, if it is in the SIS scope) and TSLL-4113 / TSLL-4114 to SIS boxes, or record why sharing a box with the initiator is accepted. In the electrical list, note that SIS and BPCS home runs share trays until the SIS cabinet is placed (#106). |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-26-layout-review28#1 | C-3102 I1 / I3 / I4 placed by default high on the shell (I4 22 m above the sump). | medium | closed 0841d30 | Placement C-3102 now has I3 75 deg / 1.6 m, I4 105 deg / 1.0 m and I1 60 deg / 3.5 m. The model points are I4 [128.413, 44.69, 21.0], I3 [129.587, 44.69, 21.6] and I1 [130.133, 44.463, 23.5], on the north side with I4 below I3. The datasheet gives the same locations and LSLL-3125's own vapour leg. `layout-nozzle-defaulted` no longer lists C-3102. The stands are a new finding, #1. |
| 2026-10-26-layout-review28#2 | C-3102 manways and davit turned 45 deg north-east by the default tappings. | low | closed 0841d30 | manway-1 neck [126.938, 42.229] -> [126.68, 42.195], on the west face about 7 deg south of west, as before 8ccc323 ([126.92, 42.5]). The davit post is at [127.438, 42.294]. D-114 (6) records it. |
| 2026-10-26-layout-review28#3 | PSHH-4152 modelled at the PT-4102 point, out of reach of VP-5, no operator declared. | medium | open | D-114 (6) and the instrument list say "PT-4152 remote-mounted on a stand on VP-5". However, piping/routing.yaml `operators:` has no entry for it, although the schema takes an instrument tag. The electrical list declares no point for it. The model and IC-PSHH-4152 still start at [177.476, 64.16, 9.11]. |
| 2026-10-26-layout-review28#4 | FSLL-2117 modelled at 5.7 m on RG-2001 S2 with no platform or operator. | low | open | The instrument list now says it is fitted at the 1 m drop at the E-2101 inlet, but IC-FSLL-2117 still starts at [90.084, 62.65, 5.695], with no `instruments:` point and no operator. |
| 2026-10-26-layout-review28#5 | JB-A2-1, JB-A3-1, JB-A4-1 over their declared 24-cable capacity. | medium | closed 0841d30 | The cable schedule now has these field cables per box: JB-A1-1 18, JB-A1-S1 4, JB-A2-1 22, JB-A2-2 6, JB-A3-1 21, JB-A3-2 6, JB-A3-S1 4, JB-A4-1 20, JB-A4-2 4, JB-A4-S1 5, JB-A5-1 9, JB-A5-2 2. All are at most 24. The missing capacity rule stays with cheme-as-code. |
| 2026-10-26-layout-review28#6 | SIF sensors share junction boxes and home runs with the BPCS; no note. | low | closed 0841d30 | JB-A1-S1 (I-03, I-06, I-19), JB-A3-S1 (I-11, I-12, I-14) and JB-A4-S1 (I-13, I-17, the K-4101 ESD valves) are declared with their own multipairs MC-JB-A*-S1. The heater trips are on JB-A2-2, apart from TIC-2104. The remaining gaps are #3. |
| 2026-10-26-control-review6#1 | I-14 does not end the over-draw in several causes it is credited for. | high | closed 0841d30 | I-14 now trips the MAC set and K-4101 and leaves FV-3111 alone (C&E). See control-review7. |
| 2026-10-26-control-review6#2 | On instrument-air loss with power on, nothing stops the running machines. | high | closed 0841d30 | The new I-19 on PSLL-1116, with its cable IC-PSLL-1116 to JB-A1-S1 from a declared point at the B1 north wall. See control-review7. |
| 2026-10-26-control-review6#3 | I-14 closes FV-3111 and stops the LOX purge. | medium | closed 0841d30 | FV-3111 is no longer an I-14 effect (control-review7). |
| 2026-10-26-control-review6#4 | Fail positions checked on air loss only, not on a single signal loss. | medium | closed 0841d30 | D-114 (5) (control-review7). The elements left out are control-review7#5. |
| 2026-10-26-control-review6#5 | D-111 asset tolerable frequencies disagree with the proposed risk matrix and D-083. | medium | open | The targets are unchanged, and D-114's "medium band" statement is wrong (control-review7). |
| 2026-10-26-control-review6#6 | BPCS layers credited in the LOPA, contrary to the records and the independence rules. | medium | open | Row 14 still credits the D-110 clamp (control-review7). |
| 2026-10-26-control-review6#7 | I-08 and I-10 are credited for each other and each is left without a SIL. | medium | open | Row 4 still credits I-10, which shares I-08's relay (control-review7). |
| 2026-10-26-control-review6#8 | The seal-gas LOPA row starts optimistic and the trip does not stop the mechanism. | medium | closed 0841d30 | A redundant seal-gas supply is required of the vendor (control-review7). |
| 2026-10-26-control-review6#9 | The D-110 ratio limits rest on FT-1101 alone and ignore the liquid draws. | medium | closed 0841d30 | Validated air flow and LOX correction (control-review7). The gaps left are control-review7#6. |
| 2026-10-26-control-review6#10 | The oxygen-fire trip I-13 is credited against an outcome that ignition already causes. | low | closed 0841d30 | Row 9 is restated as the escalation (control-review7). |
| 2026-10-26-control-review6#11 | The SIL 2 architectures are not stated, and FV-3111 is a final element of I-14. | low | closed 0841d30 | The architectures are in the C&E notes (control-review7). |
| 2026-10-26-control-review6#12 | The LSLL-3125 tap is drawn above the LICA-3102 tap on P-03. | low | accepted: a P&ID shows the connection, not the elevation; the elevations are in the placement and the datasheet (D-114 (7)); by the author agent on the owner's delegation, agreed by control-review7 | In the model I4 is now at z 21.0, below I3 at 21.6 (#1 closed above). |
| 2026-10-26-control-review6#13 | The machine-trip responses in the philosophy do not name the new interlocks. | low | closed 0841d30 | F-GOXC and F-AIR-POWER-ON (control-review7). |
| 2026-10-26-control-review6#14 | Not every open point in D-109 .. D-111 names its issue. | low | closed 0841d30 | D-114 (8), with #106 opened (control-review7). |
| 2026-10-26-control-review7#1 | The post-trip boil-off from the HP column inventory keeps E-3103 boiling after I-14 stops the air. | medium | open | Raised by the parallel control review on this commit; not examined here. |
| 2026-10-26-control-review7#2 | LOPA row 10 still takes its initiating frequency from the ratio limit that does not cover the cause. | medium | open | Parallel control review; not examined here. |
| 2026-10-26-control-review7#3 | A new ignition modifier replaces each removed credit in rows 3 and 10. | medium | open | Parallel control review; not examined here. |
| 2026-10-26-control-review7#4 | No stated restart after a genuine I-14 trip; F-GOXC `interlocks:` lacks I-19. | low | open | Parallel control review; not examined here. |
| 2026-10-26-control-review7#5 | D-114 (5) leaves out several D-109 elements (XV-3105, XV-3117, ...). | low | open | Parallel control review; not examined here. |
| 2026-10-26-control-review7#6 | The validated air flow's second measurement is untagged; no LIN correction on the GAN clamp. | low | open | Parallel control review; not examined here. |
| 2026-10-26-control-review7#7 | PSLL-1116 (I-19) exists only in lists; no issue for the utility P&ID or the set point. | low | open | Parallel control review. Its layout point [58.0, 50.0, 1.0] is declared ASSUMED in the electrical list. |
| 2026-10-24-control-review5#3 | PIC-4101's tap drawn on S2 but modelled on S1. | low | open | No P&ID changed since 8ccc323 (`cheme diff 8ccc323 --list`: "No P&ID changed"). |
| 2026-10-24-layout-review23#2 | The model has no tap point per line-mounted instrument; no rule checks reach of line-mounted transmitters. | low | open | Still true. layout-review28 #3 and #4 stay open because of it, and the electrical list's `instruments:` points are the available workaround. |
| 2026-10-24-layout-review24#1 | The AI-3104 and FIC-4148 bubbles on P-04 are 0.5 mm apart and read as touching. | low | open | P-04 is unchanged. |

## Drawing
No P&ID changed in 0841d30 or a793d37 (`cheme diff 8ccc323 --list`: "No P&ID changed").
`cheme validate` at a793d37 gives 0 errors and 97 warnings, with the same counts per sheet as at
8ccc323:
- P-01: 0 line-through-label, 2 line-crossing (accepted), 0 label-overlap, 0
  label-far-from-owner.
- P-02: 0, 0, 0, 0.
- P-03: 0 line-through-label, 3 line-crossing (accepted), 0, 0.
- P-04: 0 line-through-label, 4 line-crossing (accepted), 0, 0.

`drawing-clean` passes. No sheet was re-rendered.

## Layout
**Model checks.**
- `cheme layout build --check`: "layout/plant-model.yaml is up to date".
- `cheme layout cables --check` and `cheme layout lifting --check` both exit 0.
- The MTO, the estimate and the lifting study carry the new model hash 7a81f369...

**`cheme layout report`.**
- Lines: 78 routed, 3 skipped (GAN-3002 and LN-3002, internal to the double column, D-028; and
  VNT-3004, the casing breather), 0 unrouted.
- Methods (chains): astar 26, open 8, pinned 166, rack 15. There is no `direct` or
  `rack+direct` chain.
- Battery-limit ends: 13.
- Rack fill: PR1 61 / 43 / 25 % at 5 / 7 / 9 m; PR2 6 / 6 %; PR3 48 / 43 %.

These are unchanged from layout-review28.

**Model findings per rule:**
- access-enclosed 1 (CB-1 E20, accepted D-038 (1));
- free-span 2;
- laydown 1;
- lifting 4;
- nozzle-unconnected 2 (D-028);
- operability 1 (XV-3105);
- support-missing 15 (info);
- tier 1;
- tray-separation 1;
- tray-span 19 (17 accepted; IT-JB-A1-S1 and IT-JB-A3-S1 new and not accepted, #2);
- tray-zone 6.

There is no `layout-pipe-disconnected` and no clash. No pipe route, platform or structure moved.
The model changed only in:
- the C-3102 tappings, stands and manways;
- the junction boxes, the cables and the instrument trays.

**Cables and boxes.** The field cables per box are in the layout-review28#5 evidence above. The
new and changed cables are:
- IC-LSLL-3125: 33 m to JB-A3-S1 (was 58 m);
- IC-PSHH-4152: 29 m to JB-A4-S1;
- IC-FSLL-2117: 29 m to JB-A2-2;
- IC-PSLL-1116: 7 m to JB-A1-S1.

The SIS multipairs are MC-JB-A1-S1 10 pr, MC-JB-A3-S1 10 pr and MC-JB-A4-S1 20 pr, all routed
to CR-1. The `electrical` gate passes.

**Plan and sections read.**
- `build/layout-plan.png`: areas A1 .. A5 and V1, racks PR1 .. PR3, B1 / B2, the cold box,
  crane pads, laydowns and zones, as at layout-review28.
- `build/layout-section-y68.png`: the PR1 tiers at 5 / 7 / 9 m, with no collision seen.
- `build/layout-section-x129.png`: the C-3101 / C-3102 stack in CB-1 with P10 .. P40, RF and the
  north stair tower.
- `build/layout-section-x129_crop-39-18-50-25.png` and
  `build/layout-section-x128.3_crop-38-16-52-26.png`: the C-3102 sump region at P20. They are
  too coarse to show the 0.12 m transmitters. The stand positions in #1 are taken from the model
  coordinates against the CB-1 extents in layout/structures.yaml.

**Distances.** Measured from the model coordinates and the structures.yaml extents:
- the I3 / I4 stands are 1.6 m inside the north casing face (y 45.385 against 47.0);
- the C-3102 manway-1 flange is 0.62 m from the west casing wall (x 126.621 against 126).

## Checked and fine
- `cheme check --no-write` before this record: every gate passes except `layout-review` (this
  record is meant to close it) and `issues-basic` / `issues-detail` (open issues, outside the
  layout).
- The C-3102 datasheet nozzles I1 / I3 / I4 (face, orientation, elevation) match the placement
  and the model.
- The PSLL-1116 point and cable are plausible for an IA header leaving at the B1 north wall
  (ASSUMED until the utilities are laid out).
- The heater trips FSLL-2117, TSHH-2107 and TSHH-2116 are on JB-A2-2, apart from TIC-2104 on
  JB-A2-1, as D-114 (6) says.
- I found no third-party content in the changed layout and electrical files.

## Not checked
- The HAZOP revision (hazop-review7) and the control content (control-review7).
- The SIS architecture, the cabinet location and the real junction-box sizes (detail
  engineering: the instrument and electrical engineers).
- Everything layout-review19 lists under "Not checked": relief sizing, pipe stress, supports,
  structural design and the area classification study (the respective discipline engineers).
