---
name: structures-access
description: Decide what stands on a steel structure and how people reach it - frames in layout/structures.yaml (levels, bracing, stairs, ladders, enclosures such as a cold box casing or fire wall with their openings), equipment mounted on their levels, access platforms and ladders for manways, valves and instruments, escape (two ways down, travel to a stair), crane pads, lifting lanes and laydown, and maintenance envelopes. Use when an item is elevated, a platform is proposed (review_needed), a cold box or enclosure is modelled, or access, escape, operability, lifting or wall penetration findings appear.
---

# Structures and access

## Purpose and when to use

Put elevated equipment on structures that exist in the model, and give every place a person
must reach a platform, a ladder or a stair and a way out. `plantcode layout build` generates the
steel from `layout/structures.yaml` (columns, beams, bracing, gratings, handrails, stairs,
ladders with cages, enclosure walls), the access platforms of vertical items from their
`access:` (or proposals), and the maintenance envelopes (bundle pull, motor removal, pump
access). Use this skill when an item stands above grade, when the build proposes platforms
(`review_needed`), when modelling a cold box, enclosure or fire wall, and before the layout
review.

## Required inputs and missing inputs

- The placement and the equipment list with dimensions (skill `layout-yaml`), the P&IDs (the
  nozzles, manways and in-line valves the model places).
- What must be reached and how often: operating valves, control valves, instruments, sample
  points, manways, relief valves, davits. The P&ID shows the items; the frequency and the
  operating philosophy are design information: ask, or write an assumption into `DESIGN.md`.
- Section sizes are defaults by span (HEB200 .. HEB500, L100x10 bracing, ASSUMED); they are
  placeholders for the structural design, not results.

## Workflow and tools

1. **When an item goes on a structure.** On a structure: items that must be elevated for the
   process (an overhead condenser draining by gravity to its drum, a reboiler under its column,
   NPSH for a pump below a vessel), items stacked with others, groups that share access. On a
   building level: items that need weather protection or a crane. At grade: pumps,
   compressors, heavy and vibrating machines, tanks. A column or tank stands on its own
   foundation or skirt, with platforms on its shell, not on a frame.
2. **A frame** (`layout/structures.yaml`, `plantcode schema structures`): `origin` (south-west
   corner before rotation), `rotation_deg` (0/90/180/270), `spans_x`/`spans_y` (bays, typically
   6 to 8 m), `levels: [{id, elevation, kind: deck | platform, extent?}]` (a platform covers only
   its `extent` in frame coordinates), `bracing` (`x` or `k`, per side; leave a side open for
   access and bundle pulls), `stairs: [{id, from: grade, to, side}]`, `ladders: [{id, from, to,
   at, facing}]`, `enclosure: {walls, height, material}` for a cold box casing (`casing`) or a
   fire or blast wall (`fire_wall`). Items on it: `mount: {structure: S-1, level: L1}` with `z`
   at the level's elevation; `plantcode validate` checks the level and the footprint, the build
   reports `layout-clash-equipment-steel` (an item through a member).
3. **Cold boxes and enclosures.** Model a cold box as a structure with an `enclosure` (casing
   walls all round, the casing's height) and the columns, exchangers and separators inside it
   mounted or standing at grade inside its footprint; stacked columns stand on each other. Keep
   the casing's purge, breather and manholes on the P&ID and their access on the frame. The
   walls are obstacles for lines passing by and passable for a line with an end inside; every
   pipe that meets a wall outside a declared opening is a model `penetration` with the opening
   it would need (finding `layout-wall-penetration`: info for a casing penetration, a warning
   for a fire wall, a building's cladding, a line passing through or one running in the wall).
   Declare the openings you accept (`enclosure: {..., openings: [{id, side, offset, width,
   height, sill, kind: opening}]}`, offset along the side from its left end seen from outside,
   sill above grade; or `plantcode layout pin OWNER/LINE`): the walls are cut around them. A
   fire wall's separation distances go in `separations:` of the site plan.
4. **Platforms and ladders of vertical items.** The build proposes a platform for every nozzle
   and in-line valve more than 2.5 m above the item's base (`review_needed: true`, `serves:`
   lists them). For each proposal decide: needed (operating or maintenance access), reachable
   otherwise (a structure next to it, a mobile platform for rare tasks), or wrong (a nozzle
   placed by default: give its real position first). Then `plantcode layout pin TAG/platform-1`
   or declare `access: {platforms: [{elevation, arc_deg, width}], ladder_side}` in the
   placement. An item reached from a structure (a column inside a cold box, whose valves and
   instruments are brought out to the casing platforms) declares `access: {platforms: [],
   notes: <how it is reached>}`: no platforms of its own, nothing proposed. Rules of thumb (check them against the site's standard and the local
   regulations, ASSUMED until then):
   - manways, operating valves, control valves, instruments read in the field and sample points
     above about 2.5 m get a platform; rarely used items may be reached by a mobile platform;
   - a ladder over 3 m has a cage (drawn) or a fall-arrest system; long climbs are broken by
     rest platforms (often every 6 to 9 m); offset ladders between platforms;
   - a stair, not a ladder, where people carry tools or work often, and as the main access to a
     structure's working levels;
   - every platform and deck has two ways out where the travel distance or the hazard (oxygen,
     inert vents, flammables) requires it; escape routes are declared as `escape` zones in
     `layout/zones.yaml` (kept clear of pipes up to the walkway headroom). The rules check it:
     `layout-escape-ways` (a structure floor with fewer than two **declared** ways down:
     proposals count once pinned; an item's platform whose far end is more than `dead_end_m`,
     7.5 m, along it from its only ladder), `layout-escape-travel` (a floor at 6 m or more, or in
     regular use, without a declared stair, or a point of it more than `stair_travel_m`, 25 m,
     from its nearest stair);
   - valves and instruments within reach: `layout-operability` flags a manual handwheel or lever
     more than 1.8 m (a transmitter more than 2 m) above the nearest floor below it within
     0.6 m in plan; valves inside a closed casing are left out (extension spindles). Give it a
     platform, move it, or record a chain wheel;
   - headroom on platforms and walkways at least 2.1 to 2.2 m (`headroom_walkway_m`).
5. **Access proposals on structures and racks.** The build proposes (`source: generated`,
   `review_needed: true`, with a `reason`) a stair for every structure level at 6 m or higher,
   or in regular use (`use: regular`; a deck's default), that has no stair down, stacked on the
   frame's declared stair; a caged ladder while a floor (levels at one elevation whose extents
   touch) has fewer than two ways down; a caged ladder at each free end of a rack, to its top
   tier; and a step-over where a low pipe (top within 0.75 m) crosses an escape route or a
   grating. Decide each one like a platform: pin it (`plantcode layout pin S-1/stair-to-L2`,
   `S-1/ladder-to-L2`, `RACK/ladder-start`), declare something else (a stair on another side,
   `ladders: []` on a rack reached from a structure), or move the pipe. Step-overs follow the
   route: raise or reroute the pipe rather than accept many of them. Guard rails are drawn with
   a top rail, a mid rail, a toe plate and posts. The rules are ASSUMED defaults: check them
   against the site's standard and the local regulations.
6. **Maintenance envelopes.** Keep the generated `bundle_pull` (in front of an exchanger's
   channel), `motor_removal` and pump `access` boxes free of steel, pipes and other items
   (`layout-access-blocked`); add `maintenance` and `laydown` zones for crane access, removal
   routes and laydown areas. Look at them in a plan (`plantcode layout render --plan --png`) and
   a section through the structure (`--section x=.. --png`).
7. **Lifting.** Give heavy items their `weight` (t) in the equipment list's `dimensions`. An
   item of `heavy_lift_t` (5 t) or more needs a crane: inside a building its overhead crane
   (`crane: {capacity_t}` at least the item's weight), outside a `crane_pad` zone (`kind:
   crane_pad`, a box where the mobile crane stands, with its `reach_m`) within reach, with the
   lane from the pad over the item clear above the item's top (no pipes, racks, steel or roofs:
   `layout-lifting`), and a `laydown` zone within reach that holds the item's footprint
   (`layout-laydown`). Items inside a closed casing are left out.
8. **Criteria.** The values above (operator height and reach, dead end, stair travel, heavy
   lift, crane reach, lane margin and clearance) are package defaults, ASSUMED. Where the site's
   standard says otherwise, put its values under `criteria:` in `layout/site-plan.yaml` and
   cite the standard in `DESIGN.md`.

## Validation and failure handling

- `plantcode validate` (schemas, levels, footprints); `plantcode layout build` (clashes with
  steel, blocked access, headroom); `plantcode layout report` (platforms `review_needed`,
  objects generated, pinned or declared).
- Gate `layout-3d` requirement `mounted`: every item above grade on a building or structure
  level, or stacked on another item.
- `layout-escape-*`, `-operability`, `-lifting`, `-laydown`, `-wall-penetration` findings: fix
  the cause, or accept the finding with the reason (an operating philosophy, a mobile crane
  plan) and record it in the layout review.
- A frame that fails its schema (spans, levels, a stair to an unknown level) names the line;
  fix it before building (the build refuses invalid layout files).

## Outputs and provenance

`layout/structures.yaml`, the `mount:` and `access:` of the placements, rack `ladders` in the
site plan, zones for escape and maintenance; the rebuilt `layout/plant-model.yaml`. Structures,
stairs and ladders are `source: declared`; generated platforms, stairs, ladders and step-overs
stay `generated` with `review_needed` until pinned or declared. Record the access philosophy and the assumed sections in `DESIGN.md`.

## Required human judgment

Structural design (loads, member sizes, connections, foundations, vibration of machine
supports), the access and escape philosophy, and compliance with the local regulations on
ladders, platforms, handrails and escape routes are engineering decisions for a competent
person; the model only places the geometry and flags clashes. Every proposed platform is a
question, not an answer: decide it and record the decision.

## References

- `plantcode schema structures`, `plantcode schema placement` (`mount`, `access`),
  `layout/README.md`, `docs/framework/layout-model.md` (structures, platforms, envelopes)
- skills `layout-yaml`, `pipe-routing`, `area-classification`, `review`
