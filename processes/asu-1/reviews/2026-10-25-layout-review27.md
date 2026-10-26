---
topic: layout
reviewed_commit: a6130d6612f3d455244743eaa18bddd8c63c598e
scope: [layout/site-plan.yaml, layout/building.yaml, layout/equipment-placement.yaml, layout/structures.yaml, layout/zones.yaml, layout/hvac.yaml, layout/plant-model.yaml, layout/lifting-study.md, piping/routing.yaml, piping/pipe-specs.yaml, piping/special-items.yaml, piping/line-list.yaml, electrical/electrical-list.yaml, electrical/tray-rules.yaml, electrical/cable-schedule.csv, equipment/datasheets, equipment/equipment-list.yaml, checks/checks.yaml, control/cause-effect.yaml, control/instrument-list.yaml, lca/lca.yaml, pid/P-01.xml, pid/P-02.xml, pid/P-03.xml]
basis:
  - {path: equipment/equipment-list.yaml, revision: a6130d6, relation: depends-on}
  - {path: control/instrument-list.yaml, revision: a6130d6, relation: depends-on}
  - {path: DESIGN.md, revision: a6130d6, relation: depends-on}
  - {path: pid/P-04.xml, revision: a6130d6, relation: analyses}
  - {path: process/flowsheet.yaml, revision: a6130d6, relation: analyses}
reviewer: Claude (independent review agent; did not author D-101 .. D-108 or the layout files)
reviewer_kind: agent
branch: stage/basic-close-open
merge: pending
---
# Review: layout, twenty-seventh review (independent) of the close-open branch

Independent review of branch `stage/basic-close-open` at a6130d6 (the content of 41904e7; the
three commits after it only add review records and PROGRESS rows), against origin/main and
layout-review26. Layout-relevant changes: P-04 drawn (UY-4151 and cascade, D-101, D-105), the
datasheets refilled (D-103), PV-4105 / loops text, and D-108: the K-4101-MV and K-4102-M feeders
got `power_factor: 0.78` (ASSUMED), so the cables are 3C x 150 and 3C x 35 mm2 again; the tray-span
acceptances for PT-SWG-1 and PT-MCC-1 rewritten (a first version said the trays ran along the B2
north wall; I found that false and it was fixed in 41904e7).

Verdict: **no critical, high or medium finding is open.** One low finding (#1).

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-25-layout-review27#1 | - | E-2101 feeder C-E-2101 | Cable margin is thin: 945.5 A load against about 948.8 A derated ampacity of 2 x 4C x 300 mm2 (0.3 %). Disclosed in D-108. | low | accepted: disclosed in D-108 and the heater power (1.13 MW peak) is ASSUMED; the electrical engineer sizes the real cable, and any heater change must recheck it (reviewer, 2026-10-25) | None now; recheck the cable with any E-2101 duty change. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-layout-review24#1 | The AI-3104 and FIC-4148 bubbles on P-04 are 0.5 mm apart and read as touching. | low | open | Not examined here; P-04 changed (FIC-4148 gained signal lines) but no move of AI-3104 is listed in the diff. |
| 2026-10-24-layout-review23#2 | The model has no tap point per line-mounted instrument; no rule checks reach of line-mounted transmitters. | low | open | No change in that area on this branch. |

## Drawing
P-04 is outside this record's scope (see pid-review1). `cheme validate` at the reviewed
state: P-01: 0 line-through-label, 2 line-crossing; P-02: 0, 0; P-03: 0, 3 line-crossing; P-04: 0
line-through-label, 4 line-crossing (all accepted); label-overlap and label-far-from-owner 0 on
every sheet. 0 errors, 60 warnings (known groups).

## Layout
- `cheme layout build --check`: "layout/plant-model.yaml is up to date"; `cheme layout lifting
  --check` current; `cheme layout cables --check` current; `cheme fmt --check` clean.
- `cheme layout report`: methods (chains) astar 26, open 8, pinned 166, rack 15; the reasons per
  chain as in earlier records (13 battery-limit-end racks); no `direct` or `rack+direct` chain.
  Model findings per rule: access-enclosed 1, free-span 2, laydown 1, lifting 4,
  nozzle-unconnected 2, operability 1, tier 1, tray-span 17, tray-zone 6, tray-separation 1, and
  support-missing infos (counts from the `layout build --check` printout); all known from earlier records and accepted or open there. No
  `layout-pipe-disconnected`.
- **Cables and trays (D-108), recomputed:** I = P / (sqrt3 x U x pf). K-4101-MV: 2500 / (1.732 x
  6.6 x 0.78) = 280.4 A -> 3C x 150 mm2. K-4102-M: 315 / 8.917 = 35.3 A -> 3C x 35. E-2101:
  1130 / (1.732 x 0.69) = 945.5 A -> 2 x 4C x 300. Matches electrical/cable-schedule.csv. The
  `electrical` gate passes. Tray fill PT-MCC-1 0.229, PT-SWG-1 0.174, both below 0.3. I did not
  check ampacities against a cable catalogue (not in the repository). pf 0.78 (motor 0.85 x
  efficiency 0.92) is marked ASSUMED and conservative.
- **Tray-span acceptances, against the model:** PT-SWG-1 runs [27.5, 60.5, 3] -> [27.5, 70.5, 3]
  then up to z 12 and east to PR1; PT-MCC-1 the same at x 29 to z 11. B2 is x 20-38, y 50-60, so
  the trays leave its north wall at 0.5 m and run level at 3 m about 10 m north to a riser at the
  PR1 west end. The reasons now say exactly this (brackets for the first metre, then posts at 6 m
  or less and a riser column, ASSUMED, unmodelled). Lint spans 9.5 m and 6.6 m as quoted;
  `cheme.accept-stale`: none.
- Plan and sections read: `build/layout-plan.png` (B2, B1, racks PR1-PR3, storage and vent
  areas, zones, crane pads), `build/layout-section-y68.png` (the PR1 tiers at 5 / 7 / 9 m with
  no collision seen) and `build/layout-section-x132.png` (the cold
  box with its platforms and PR1 / PR2 tiers). I looked for platforms or valves inside casings and
  for trays in zones: the known `layout-access-enclosed` (CB-1 E20) and the accepted tray-zone
  findings are the only ones.
- No layout object moved: the plant-model.yaml diff is the P-04 instrument references, the
  datasheet-derived data and the cable regeneration.

## Checked and fine
- `cheme check --no-write` before this record: 30 of 31 (layout-review only); this record
  replaces the stale layout-review26.
- No third-party content found in the layout files changed; no forbidden names.

## Not checked
- Everything review19 lists under "Not checked" (relief sizing, pipe stress, CB-1X envelope) and
  the real cable catalogue ampacities; structural design of the tray posts and the riser column
  (detail stage).
