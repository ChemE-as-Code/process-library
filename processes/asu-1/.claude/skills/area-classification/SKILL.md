---
name: area-classification
description: Declare the zones of the 3D layout in layout/zones.yaml - hazardous areas around flammable releases, oxygen-enriched and oxygen-deficient zones around oxygen and inert vents of an air separation or similar plant, and keep-clear, laydown, maintenance and escape zones - from explicit volumes or release sources with release grade and substance, sized by cheme-as-code's ASSUMED radius table, then check separations and routes against them. Use when adding vents, relief outlets, seals or flanges handling oxygen, inerts or flammables, when a zone or separation finding appears, or before the layout review.
---

# Area classification for the layout

## Purpose and when to use

Put the zones that constrain the layout into `layout/zones.yaml`, so the 3D model shows them,
the router keeps pipes out of the forbidden ones and the separation rules measure against them.
This is a **screening** classification for layout work, not an area classification study: the
radii come from an indicative table marked ASSUMED, and no dispersion is modelled. Use it when
the P&IDs gain vents, relief valves, pump or compressor seals or flanged equipment handling
oxygen, inert gases or flammables; when `cheme validate` or `layout build` report
`layout-zone-crossing` or `layout-separation`; and before the layout review.

## Required inputs and missing inputs

- The placed items and the routed model (skill `layout-yaml`), the P&IDs (vents, relief
  valves, silencers, stacks; `piping/special-items.yaml` for safety valves and silencers), the
  line list (fluids), `DESIGN.md` (the substances, the vent philosophy, the site's wind).
- For each release point: what is released (substance), how often (release grade:
  `continuous`, `primary` - expected in normal operation from time to time, `secondary` - only
  in abnormal operation), and its kind (`vent`, `psv_outlet`, `pump_seal`, `compressor_seal`,
  `flange`, `valve`, `drain`). When the grade is not known, say so (`basis:`) and take the more
  frequent grade.
- The site's area classification standard and any study already done: a real classification
  replaces the table; ask for it.

## Workflow and tools

1. **Explicit zones** (`shape: box | cylinder | sphere`): `keep_clear` (truck loading bays,
   fire-fighting access), `laydown`, `maintenance` (crane and removal areas), `escape`
   (escape routes, kept clear up to `headroom_walkway_m`), and any zone a study gives you as a
   volume (`hazardous` with `zone: 0 | 1 | 2 | 20 | 21 | 22`, `oxygen_enriched`,
   `oxygen_deficient`). `box: [x0, y0, z0, x1, y1, z1]`; a cylinder's `centre` is the centre of
   its base, with `radius` and `height`. Give every zone a `title` and a `basis`.
2. **Zones from sources** (`sources: [{item, release_grade, substance, source_kind?,
   substance_class?}]`): `item` is a placed tag (a stack, silencer or vent: its top; a pump:
   its seal; a compressor or turbine: its seals; a safety valve: its outlet), a nozzle
   `TAG/N1` (a flange) or a line number (its open ends: vents and relief outlets). The
   substance maps to a class (`oxygen`, `inert`, `flammable_gas`, `flammable_liquid`; override
   with `substance_class`) and the table (`domains/safety/data/release-radii.yaml`) gives one
   volume per row of that source kind, grade and class whose kind is the zone's `kind` (and
   zone number, when given), so one zone holds one kind: e.g. a continuous oxygen vent an `oxygen_enriched` sphere of 5 m, an inert
   vent an `oxygen_deficient` sphere of 5 m, an LIN pump seal an `oxygen_deficient` cylinder of
   3 m from grade, a flammable relief outlet zone 1 within 3 m. Every generated volume carries
   `status: ASSUMED` and the row's `basis`.
3. **Air separation and other oxygen and inert plants**:
   - oxygen-enriched zones around GOX/LOX vents, oxygen relief outlets, oxygen compressor seals
     and LOX pump seals: no ignition sources, no oil or grease, no combustible materials
     (asphalt, wood) in them, and keep them away from air intakes, roads and buildings;
   - oxygen-deficient zones around nitrogen, argon and waste-gas vents, cold box casing
     breathers and LIN/LAR pump seals: cold inert vapour collects at grade and in pits and
     trenches; vents go above platforms and away from walkways and escape routes;
   - the main air intake upwind of every vent (the prevailing wind is a design assumption in
     `DESIGN.md`), with the distance measured (`cheme show <tag> --layout`) and declared as a
     `separation:` in the site plan (`from: <intake>, to: <zone id>, min_m: ...`);
   - liquid spills (LOX, LIN) spread at grade: keep drains, trenches and kerbs in mind.
4. **Separations against zones**: a site-plan separation may name a zone id (`from: Z-O2-VENT,
   to: R-1, min_m: 15, basis: ...`); `cheme layout build` measures it
   (`layout-separation`). Routes through `keep_clear`, `laydown`, `maintenance` and `escape`
   zones are avoided by the router; `layout-zone-crossing` reports what crosses a zone. Cable
   trays inside an oxygen-enriched or hazardous zone are `layout-tray-zone` (the zone kinds in
   `avoid_zones` of `electrical/tray-rules.yaml`): an ignition source and a combustible cable
   sheath in an oxygen zone, or equipment not rated for a hazardous area. A vent or relief
   zone that reaches a walking level is `layout-vent-outlet`; the walking levels include the
   generated ones (a tank's spiral stair, its landing and roof platform, stair landings,
   step-overs), and an outlet directly under a walking surface is a finding even without a
   zone. Platforms and ladders inside a casing are no walking levels: a casing breather's
   zone covers the roof walkway, not the platforms inside.
5. **Look at the zones**: `cheme layout render --plan --png` (zones are drawn with their
   ids), a section through a vent area (`--section x=.. --png`), and `cheme serve`
   (Layout 3D: zones as transparent volumes). Check that every vent and relief outlet of the
   P&IDs has a zone or a reason why not.

## Validation and failure handling

- `cheme validate` checks the file against `cheme schema zones` (a zone needs a shape or
  sources, a hazardous shape a zone number); `cheme layout build` reports
  `cheme.layout-zone-source` for a source it cannot find (an unplaced tag, a nozzle the P&ID
  lacks, a line without open ends), a substance not in the table, or a source the table has no
  row of the zone's kind for: place the item, fix the name, set `source_kind` /
  `substance_class`, or give an explicit volume with its basis.
- Gate `layout-3d` requires `layout/zones.yaml` with at least one zone; it does not judge the
  extents.

## Outputs and provenance

`layout/zones.yaml` (`source: declared` zones; volumes from sources are `generated` with
`status: ASSUMED` and the table row's basis), the separations naming zones in
`layout/site-plan.yaml`, and the zone basis in `DESIGN.md` (substances, grades, wind, the
standard to be applied). Never present a table radius as a classification result.

## Required human judgment

The radius table is indicative and ASSUMED: it ignores release rates, pressure, ventilation,
obstructions, wind and the site's standard. An area classification (IEC 60079-10-1 / -10-2, EI
15 or the site's code for flammables; EIGA guidance and a vent study for oxygen and inert gases)
must be made or reviewed by a **competent person**, who replaces or confirms each zone and signs
the record. Until then every zone stays ASSUMED, the layout review lists it under "Not checked"
or as a finding, and no equipment selection (Ex ratings) may rest on it. Dispersion and
consequence modelling are out of scope here; their results come in as explicit volumes.

## References

- `cheme schema zones`, `layout/README.md`, `docs/framework/layout-model.md` (zones)
- the radius table `domains/safety/data/release-radii.yaml` (bundled with cheme-as-code),
  `domains/safety/area_classification.py`
- skills `layout-yaml`, `structures-access`, `review`
