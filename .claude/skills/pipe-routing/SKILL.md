---
name: pipe-routing
description: Steer and review the generated pipe routes of the 3D model - routing intent in piping/routing.yaml (rack tiers per service, battery limits, the pipe-way elevation, via points, pins, skips with a reason), iterate with plantcode layout route, report and render --plan/--section, look at the PNGs, fix clashes and pin good routes. Use when lines are unrouted, run the wrong way, clash, or before a layout review or the layout-3d gate.
---

# Pipe routing

## Purpose and when to use

`plantcode layout build` routes one pipe per P&ID segment (DN, insulation, class from the line
list and `piping/pipe-specs.yaml`). The router is deterministic and simple: it goes over the
racks for lines between areas, across roads or longer than `local_max_m`, and runs local lines
at the pipe-way elevation. It knows nothing of stress, drainage, operability or what the
operators need to reach. This skill says how to give it the intent it lacks, how to check the
result, and when to stop iterating and pin. Use it when `plantcode layout report` shows lines
unrouted or `direct`, when routes clash or look wrong in the drawings, and before the layout
review.

## Required inputs and missing inputs

- A built model: placement, site plan with racks, the P&IDs, the line list with DN, `fluid`,
  `insulation`, `from`/`to` (skill `layout-yaml`). A segment with no DN on the P&ID or in the
  line list is routed at DN 50, a line without `insulation` bare: fix the list first (skill
  `lists-sync`).
- `piping/routing.yaml` (`plantcode schema routing`), optional. Without it the defaults apply,
  each ASSUMED: `local_max_m` 15, `local_elevation_m` 3.5 (bottom of pipe), `grade_max_m` 3,
  `rack_reach_m` 50, `rack_detour_factor` 2.5, `spacing_m` 0.1, `headroom_road_m` 6,
  `headroom_walkway_m` 2.2, `grid_m` 0.5.
- Where the utilities come from (cooling water plant, nitrogen header, flare) is design
  information: ask, or record an assumption in `DESIGN.md`, before declaring battery limits.

## Workflow and tools

1. **Read the result first.** `plantcode layout report` lists each line (routed, partly routed,
   skipped, unrouted with the reason), the chains per method (`astar`, `astar_coarse`,
   `astar_fine`, `rack`, `rack+...`, `via`, `open`, `direct`, `pinned`) and per reason (`rack:
   across areas`, `rack: crosses a road`, `local: pipe-way`, `local: pump run at grade`, `local:
   rack run too short`, ...), the battery limit ends and the rack fill. `--json` gives the same
   per line. `direct` and `rack+direct` routes are fallbacks (`review_needed`): treat each as a
   finding; most come from crowded nozzles (give them room with nozzle overrides) or an end
   boxed in by steel and pipes.
2. **Rules, in `piping/routing.yaml` `rules:`**:
   - `tiers`: which service runs on which tier, by `fluids` or line-number prefix (`lines`),
     optionally per `rack`. Typical: large process lines low, utilities and small lines high,
     cold and oxygen lines on their own tier or edge. Without a rule DN 300 and above take the
     lowest tier, the rest the top tier;
   - `battery_limits`: where lines that leave the plot end (`BL`, `CW`, `CWR`, ... ends in the
     line list): `{id, lines: [CW-*, CWR-*], point: [x, y, z]}` or `{id, fluids: [Steam], rack:
     PR1, rack_end: start | end | nearest}`. Without a rule: the line's `from_area`/`to_area`,
     else the free end of the nearest rack, else the site edge;
   - `local_elevation_m` (the pipe-way of an area), `local_max_m` (longer goes to the rack),
     `grade_max_m`, `rack_reach_m`, `spacing_m`, headroom, `gravity_fluids`.
3. **Intent per line or segment** (`lines:`, `{line, segment?}`; a segment by DEXPI id or
   segment number):
   - `rack: PR2` or `tier: 8` to force the rack (and the tier);
   - `via: [[x, y, z], ...]` points the route must pass, in order; `elevation: z` runs it at
     that height;
   - `skip: <reason>` for what is not routed at this stage (field-run small bore, a package's
     internal piping, an item not placed yet). The reason is shown in the report and counts for
     the `layout-3d` gate; "later" is not a reason;
   - `gravity: true` (or the fluid in `gravity_fluids`) checks a continuous fall.
   Vent and relief lines end in a 1 m riser where the P&ID ends them; a silencer or safety
   valve that discharges elsewhere (a vent stack area) is listed in
   `piping/special-items.yaml` and placed in `layout/equipment-placement.yaml` by its tag:
   the line is then routed to it.
4. **Iterate on the lines you changed only**: `plantcode layout route --line L [--line M]`
   reroutes those and keeps every other route of the committed model; `plantcode layout build`
   reroutes all (needed after a placement change). Lines route in order of DN, largest first:
   a small line that clashes may need a via, a large one moves everything after it.
5. **Look at it.** `plantcode layout render --plan --png` (plot plan), `--z 2,6` (a band of
   elevations), `--section y=68 --depth 8 --png` (across a rack), `--section x=.. --crop
   X0,Y0,X1,Y1 --png` (around one item). Read the PNGs in `build/`: lines through items, lines
   at grade across walkways, lines in front of manways, bundle-pull or motor-removal space,
   lines over a road below the headroom, too many bends, dead legs, a lane jumping across the
   rack. `plantcode serve` (Layout 3D) shows the same in 3D with the findings.
6. **Fix clashes** (`plantcode.layout-clash-pipe`, `-clash-pipe-equipment`, `-clash-pipe-steel`,
   `-headroom`, `-access-blocked`, `-zone-crossing`): each finding names both objects and a
   `box`. Prefer, in this order: move the item or turn the nozzle (skill `layout-yaml`), give a
   tier rule, add a via, change the pipe-way elevation. Rebuild after each step. A clash that is
   real but intended (a line resting on its own support steel) is accepted in the `layout-3d`
   gate with a reason, never silently left.
7. **Pin what is good.** `plantcode layout pin LINE` (or a pipe id) copies the route into
   `piping/routing.yaml` (`route:`, `source: pinned`): later builds take it as it is, so a
   reviewed route stays reviewed. Pin a route only after looking at it; re-pin or delete the
   pin when its ends move (`layout build` keeps a pinned route even when it no longer fits).

## Validation and failure handling

- `plantcode validate` checks `piping/routing.yaml` against its schema and the model rules on
  the committed model; `plantcode layout build --check` says whether the model is current.
- Unrouted reasons and what to do: `<tag> is not placed` (place it, or skip the line with the
  reason); `both ends are open` (a vent between two open ends: check the P&ID); `it starts or
  ends at <tee/line>, which no route reaches` (route the run first, or fix the topology);
  `connector ...: line ... is not in the line list` (add the line).
- The `layout-3d` gate (`plantcode check --stage basic`) fails while a process line of DN 25
  and above is neither routed nor skipped, or a clash or headroom finding is not accepted; the
  `layout-detail` gate requires every line, utilities included.

## Outputs and provenance

`piping/routing.yaml` (rules, intent, pins) and the rebuilt `layout/plant-model.yaml`, both
committed. Every pipe records its `method`, `reason` and `source` (`generated` or `pinned`);
assumed rules (tier allocation, battery limit points, pipe-way elevation) are marked ASSUMED in
`routing.yaml` `notes:` with their basis in `DESIGN.md`.

## Required human judgment

The router does not decide, and you must not pretend it did:

- tier allocation, rack width and spare space, which lines may share a support;
- pipe stress and flexibility (expansion loops, hot and cold lines), supports and anchors;
- drainage and venting (low-point drains, pockets in two-phase and gravity lines), slug flow;
- operability and maintenance: valve and instrument access, spectacle blinds, removal spools;
- safety: oxygen-line velocity and material rules, cryogenic lines and their insulation, relief
  and vent outlets, lines over escape routes.

A route without a clash finding is only geometrically free. The layout review (skill `review`)
records which routes were checked by whom.

## References

- `plantcode schema routing`, `layout/README.md`, `docs/framework/layout-model.md` (the router)
- `plantcode layout build | route | pin | report | render`, `plantcode serve` (Layout 3D)
- skills `layout-yaml`, `structures-access`, `review`
