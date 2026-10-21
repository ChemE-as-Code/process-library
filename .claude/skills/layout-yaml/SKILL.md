---
name: layout-yaml
description: Edit the 3D layout in layout/ - site plan (areas, roads, pipe racks), buildings (levels, column grid) and equipment placement - keeping tags consistent with the equipment list and clear of clashes, then check with plantcode validate. Use when placing, moving or resizing equipment, adding a building, area, road or rack, or when plantcode validate reports plantcode.layout-* findings.
---

# Editing the 3D layout

## Purpose and when to use

Edit the 3D layout in `layout/` and keep it consistent with the equipment list and clear of
clashes. Use it when placing, moving or resizing equipment, or adding a building, area, road
or rack.

## Required inputs and missing inputs

Three optional files, explained in `layout/README.md`; their schemas are
`plantcode schema site_plan`, `plantcode schema building` and `plantcode schema placement`.
Coordinates are metres, x east, y north, z up, origin at the site's south-west corner.

1. **Read first**: `layout/site-plan.yaml` for the site box and what is already taken (areas,
   roads, racks), `layout/building.yaml` for building outlines and level elevations, and
   `equipment/equipment-list.yaml` for the tags and types.

A dimension not known yet may be estimated: mark it `notes: ASSUMED ...` (step 2).

## Workflow and tools

2. **Placing equipment** (`layout/equipment-placement.yaml`):
   - one entry per equipment-list tag, spelled exactly as in the list (`plantcode.layout-unknown-tag`
     otherwise); every listed item should get one (`layout-not-placed` is reported as info).
     Silencers, vent stacks' relief valves and other items of `piping/special-items.yaml` may be
     placed too, by their tag (they are not reported as not placed);
   - `position` is the centre of the footprint and the **bottom** elevation: `[x, y, 0]` at
     grade; in a building give `building` and `level` and set `z` to that level's `elevation`
     (`layout-level`, 0.05 m tolerance), and keep the whole footprint inside the building and the
   item's height within the level's clear height;
   - pick the shape that bounds the item: `vertical_cylinder` for tanks and columns,
     `horizontal_cylinder` for drums and shell-and-tube exchangers (axis along x before
     `rotation_deg`), `box` for pumps, skids and plate exchangers; round shapes take
     `size: {diameter, height}` / `{diameter, length}` / `{diameter}`, only a box takes
     `size: [dx, dy, dz]`;
   - dimensions you do not know yet are fine to estimate: say so (`notes: ASSUMED ...`), and
     record the layout basis in `DESIGN.md`.
3. **Avoiding clashes** (`plantcode.layout-clash`): plantcode compares the boxes around each
   shape after rotation. Leave maintenance and access space - about 1 m around pumps, a
   tube-bundle pull length in front of a shell-and-tube exchanger - even though plantcode only
   flags real intersections. Keep equipment off roads and out of buildings it is not placed
   in. Pumps may stand at grade **under** a pipe rack, the usual arrangement in a rack-type plot
   plan, as long as their top stays at least 0.5 m below the lowest tier; anything taller goes
   beside the rack. Put a pump close to its suction source (a tank or vessel it draws from):
   a long suction line costs NPSH, and for a reciprocating pump also brings pulsation.
   Buildings must not stand on roads or overlap each other, and a rack may cross a building
   only with its lowest tier above the building's top.
4. **Site plan**: give every area a road: trucks must reach loading areas, and the process
   area needs fire-fighting access, ideally from more than one side. Areas are `[x0, y0, x1, y1]` with x0 < x1, y0 < y1 and should not overlap
   (`layout-area-overlap`); split a plot into adjacent areas instead of nesting them. Everything
   stays inside `site.width` x `site.depth` (`layout-outside-site`).
5. **Racks and lines**: lines between areas, or longer than 30 m, need a rack route
   (`plantcode.layout-line-route`): extend or add a rack so both ends are within `rack_reach`
   (default: the 30 m unsupported length) of it and the racks touch. Vent and relief lines count: place the silencers and
   relief valves (from `piping/special-items.yaml`) or give the line `to_area: <vent area>`.
   Use the `layout-line-length` estimates for line lengths, never guess them.
6. **Spacing criteria** (toppling radius, distances to tanks, roads, the boundary) go into
   `separations:` of `site-plan.yaml` (see `layout/README.md`), so validate measures them
   (`plantcode.layout-separation`). Model a cold box or fire wall as a building with its height,
   or a tagged box. Quote **measured** distances in `DESIGN.md`: `plantcode show <tag> --layout`
   prints them; never write a distance you have not measured.
7. **Buildings** turn only in steps of 90 degrees, about their `origin` corner. Column grid
   offsets are along the building's own x and y and must lie within its width and depth.

## Validation and failure handling

8. **Check**: run `plantcode validate`; it ends with `compared: ...` naming `layout` among the
   cross-checks when the layout rules ran. Fix every `plantcode.layout-*` error; a `yaml.schema`
   error names the line. Then look at it: `plantcode serve` and open **Layout 3D**, where
   clashing items show red and the findings are listed beside the model.

## Outputs and provenance

The edited `layout/*.yaml` files; the layout basis, assumed dimensions and measured distances
go into `DESIGN.md`.

9. When a tag changes in the equipment list or on a P&ID, change it here too, in the same
   commit.

## Required human judgment

Maintenance and access space, pump positions and spacing criteria are design choices:
plantcode only flags real intersections and measures the `separations:` you give it.

## References

- `layout/README.md`; `plantcode schema site_plan`, `building`, `placement`
- `plantcode show <tag> --layout`, `plantcode serve` (**Layout 3D**)
