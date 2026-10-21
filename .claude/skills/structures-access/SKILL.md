---
name: structures-access
description: Decide what stands on a steel structure and how people reach it - frames in layout/structures.yaml (levels, bracing, stairs, ladders, enclosures such as a cold box casing or fire wall), equipment mounted on their levels, access platforms and ladders for manways, valves and instruments above 2.5 m, escape routes and maintenance envelopes. Use when an item is elevated, a platform is proposed (review_needed), a cold box or enclosure is modelled, or access findings appear.
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
   the casing's purge, breather and manholes on the P&ID and their access on the frame. An
   enclosure is not a pipe obstacle (pipes pass through the casing); a fire wall's separation
   distances go in `separations:` of the site plan.
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
     `layout/zones.yaml` (kept clear of pipes up to the walkway headroom);
   - headroom on platforms and walkways at least 2.1 to 2.2 m (`headroom_walkway_m`).
5. **Maintenance envelopes.** Keep the generated `bundle_pull` (in front of an exchanger's
   channel), `motor_removal` and pump `access` boxes free of steel, pipes and other items
   (`layout-access-blocked`); add `maintenance` and `laydown` zones for crane access, removal
   routes and laydown areas. Look at them in a plan (`plantcode layout render --plan --png`) and
   a section through the structure (`--section x=.. --png`).

## Validation and failure handling

- `plantcode validate` (schemas, levels, footprints); `plantcode layout build` (clashes with
  steel, blocked access, headroom); `plantcode layout report` (platforms `review_needed`,
  objects generated, pinned or declared).
- Gate `layout-3d` requirement `mounted`: every item above grade on a building or structure
  level, or stacked on another item.
- A frame that fails its schema (spans, levels, a stair to an unknown level) names the line;
  fix it before building (the build refuses invalid layout files).

## Outputs and provenance

`layout/structures.yaml`, the `mount:` and `access:` of the placements, zones for escape and
maintenance; the rebuilt `layout/plant-model.yaml`. Structures, stairs and ladders are
`source: declared`; generated platforms stay `generated` with `review_needed` until pinned or
declared. Record the access philosophy and the assumed sections in `DESIGN.md`.

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
