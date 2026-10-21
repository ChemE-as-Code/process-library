# Layout

The 3D layout of the plant, as three optional YAML files. `plantcode validate` checks them
against their schemas and each other; `plantcode serve` shows them in 3D (Layout 3D in the
viewer). The skill `.claude/skills/layout-yaml` says how to edit them.

| file | schema | holds |
|---|---|---|
| `site-plan.yaml` | `plantcode schema site_plan` | site boundary, plot areas, roads, pipe racks |
| `building.yaml` | `plantcode schema building` | buildings and structures, their levels and column grid |
| `equipment-placement.yaml` | `plantcode schema placement` | where each equipment-list item stands, and its shape |

Coordinates are metres in the site frame: **x east, y north, z up**, origin at the south-west
corner of the site. Rotations are degrees, counterclockwise seen from above.

- An **area** is a box `[x0, y0, x1, y1]`; kind `process`, `utilities`, `storage`, `road`,
  `reserved` or `building`. Areas should not overlap (roads may).
- A **road** or **rack** is a centreline `points: [[x, y], ...]` with a `width`; a rack has tier
  elevations `levels: [z, ...]`.
- A **building** is a rectangle `width` (along its x) by `depth` (along its y) from its
  south-west corner `origin: [x, y]`, turned by `rotation_deg` (0, 90, 180, 270) about that
  corner. `levels` are floors, platforms or roofs (`elevation`, `height`); `frame.grid_x` /
  `grid_y` are column lines as offsets from the origin.
- A **placement** puts an equipment tag at `position: [x, y, z]`: the centre of its footprint,
  `z` the bottom. `shape` is `box` (`size: [dx, dy, dz]`), `vertical_cylinder`
  (`size: {diameter, height}`), `horizontal_cylinder` (`size: {diameter, length}`, axis along x
  before rotation) or `sphere` (`size: {diameter}`). An item inside a building names its
  `building` and `level`; its `z` is then the level's elevation.

Rules (`plantcode.layout-*`): `outside-site`, `clash` (equipment boxes intersect, equipment in a
building it is not placed in, equipment on a road, equipment reaching up into a rack's tiers,
buildings on roads, under racks or overlapping each other), `unknown-tag`, `not-placed` (info),
`level` (also items taller than their level), `area-overlap` (warning), `duplicate` (warning),
`line-route` (warning), `line-length` and `line-unrouted` (info), `separation` (warning).
A level without `height` reaches up to the next level (a top floor: 4 m); a building without
levels counts as 6 m high. Numbers must be finite and ids not empty.

Example (uncomment into the three files):

```yaml
# layout/site-plan.yaml
# site: {name: Plot 1, width: 60, depth: 40}
# areas:
#   - {id: A-100, title: Process area, box: [10, 18, 46, 38], kind: process}
# roads:
#   - {id: R-1, title: Main road, points: [[0, 13], [60, 13]], width: 6}
# racks:
#   - {id: PR-1, title: Main pipe rack, points: [[10, 20], [46, 20]], width: 4, levels: [5, 7]}
# notes: ASSUMED - plot dimensions not yet confirmed.

# layout/building.yaml
# buildings:
#   - id: B-1
#     title: Process building
#     origin: [26, 26]
#     width: 14
#     depth: 10
#     levels:
#       - {id: GF, title: Ground floor, elevation: 0, height: 5, kind: floor}
#       - {id: PF, title: Platform, elevation: 5, height: 4, kind: platform}
#     frame: {grid_x: [0, 7, 14], grid_y: [0, 5, 10]}

# layout/equipment-placement.yaml
# equipment:
#   - {tag: P-101, position: [16, 24.5, 0], shape: box, size: [2.0, 0.8, 1.0]}
#   - {tag: E-101, position: [34, 31, 5], shape: horizontal_cylinder,
#      size: {diameter: 0.8, length: 5}, building: B-1, level: PF}
```

**Lines and racks.** Each line of `piping/line-list.yaml` whose ends (`from`, `to`: placed
tags, area ids or other line numbers; or `from_area` / `to_area` for an end that is not placed,
such as a vent area) lie in different areas or more than `max_unsupported_length` (default 30 m)
apart must be carried by racks: each end within `rack_reach` of a rack centreline (default:
`max_unsupported_length`, since the run from an end to the rack is unsupported pipe), the racks
connected (`layout-line-route`). Carried lines get a length estimate along the racks
(`layout-line-length`, info).

**Separations and keep-clear radii.** State spacing criteria as data, not only in `DESIGN.md`
prose, and they are measured (`layout-separation`):

```yaml
# separations:                     # in layout/site-plan.yaml
#   - {from: CB-3101, to: K-4101, min_factor_of_height: 1, reason: toppling, basis: D-026}
#   - {from: T-4101, to: site-boundary, min_m: 8, basis: D-026}
#   - {from: T-4101, to: R-1, min_m: 8, measure: footprint}
```

`from`/`to` are placed tags, area, building, road or rack ids, or `site-boundary`;
`min_factor_of_height` multiplies the height of the taller of the two (`height_of: from|to`
to choose). Distances are between footprints (`measure: centre` between centres).
`plantcode show <tag> --layout` prints measured distances to quote in `DESIGN.md`. Model an
enclosure you measure from -- a cold box, a fire or blast wall -- as a building with a level of
its height (and place the items inside it with `building:`), or as a tagged box placement.
