I finished S9 on `stage/detail-gates` in three commits. Only `hvac` and `control-complete` pass among the detail gates; `layout-detail`, `electrical` and `datasheets` fail, and `layout-detail` and `electrical` fail on core v1.0.0 limits. This branch also breaks the basic gate `layout-3d`, which passed on `stage/basic-layout`. The tree is clean, `cheme validate` shows 0 errors (239 warnings, up from 204), and the PR description is in `build/pr-body.md`.

| gate | result | why |
|---|---|---|
| layout-detail | **fails** | Every line is now routed or skipped (248 of 258 segments; the other 10 are the furnace ducts skipped in S5). Before, the 20 cooling-water lines were unrouted. It fails on 4 road headroom findings for the buried DN 1400 cooling-water headers crossing roads R-5 and R-6. The core's headroom rule counts a pipe under a road at −3.7 m as too low; it has no notion of buried pipes. |
| electrical | **fails** | Every motor and instrument has a cable in trays: 274 rows in `electrical/cable-schedule.*`. It fails on 8 tray-fill findings: the main-rack power tray is 53–54 % full against a 30 % limit, because it carries the 10 kV cables of the three large compressors. The core allows only one power tray per rack, so the second tray the finding asks for can't be declared. |
| hvac | passes | Two air handling units ventilate the new building's four rooms, with no duct findings. It only passed before because there was no building. |
| control-complete | passes | No change. |
| datasheets | **fails** | I turned on the template's detail-stage requirements (dimensions, weights, nozzle schedule, drawings), which the plan allows. It now fails because 51–52 items lack main dimensions, weights and nozzle schedules; that data has to come from mechanical design or vendors. |
| issues-detail | n/a | `plant.yaml` declares no issues. |

None of these findings was accepted, relaxed or skipped. The instrument list is complete: validate finds no list-vs-P&ID problems, and all 122 instruments are placed and cabled.

**What I added:**
- **Cooling water (D-038):**
  - The DN 1400 headers and 18 branches are buried along the main rack, at depths I assumed.
  - The header routes are written into `piping/routing.yaml` by hand, because the router can't route a line with battery limits at both ends.
  - Some cooling-water nozzles were turned in the layout only (P&IDs unchanged), so three temperature control valves sit above grade, and one exchanger's bundle-pull space is clear.
  - One valve access platform, VP-TV-1306, was added.
- **Electrical (D-039):** an electrical and control building in the reserved area (10 kV switchgear, 400 V MCC, rack room, control room), the substation and transformers, and 11 motor ratings.
  - Compressor and fan ratings use the datasheets' calculated gas power.
  - The P-302A/B reflux pump rating (7.6 kW) is my own estimate.
  - All are marked ASSUMED.

**Effect on basic gates:**
- **layout-3d** now fails on the same 4 buried road-crossing findings.
- **lifting-study** still fails, now with 12 findings instead of 8. The new ones come from motor cable trays the build runs over K-101, K-102, K-103 and K-701, and there is no way to give a motor's cable entry point.

**Decisions for the reviewer:**
- **The 4 buried road crossings:** accept them with a reason (for example "buried crossing in a sleeve under the road"), or ask for elevated crossings. I rejected elevated crossings: a 10 m DN 1400 riser on each side of each road, only to suit the rule.
- **The power tray on the main rack:** it needs a core change, or a decision to accept the fill.

**Other open items:**
- 19 trays run more than 6 m with no steel near them.
- Near x 205–216 some buried branches rise to about grade where they cross each other.
- The cooling-water supply and return nozzles of K-101, K-501 and K-701 sit at the same point in the model.
- The junction boxes are the build's proposals and need the instrument engineer's decision.

A merge is pending: the branch needs review, and merges into `stage/basic-layout`.

STATUS: DONE