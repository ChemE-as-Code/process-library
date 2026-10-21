# Datasheets

One YAML file per equipment-list item: `equipment/datasheets/<TAG>.yaml`, schema
`plantcode schema datasheet`. They are the detail-stage deliverable: the `datasheets` gate in
`checks/checks.yaml` fails until every item of `equipment/equipment-list.yaml` has a valid one.

`plantcode validate` checks each file against the schema and the equipment list:
`plantcode.datasheet-not-listed` (a tag not in the list), `plantcode.datasheet-mismatch` (design
pressure or temperature, or type, other than the list says), `plantcode.datasheet-name` (file not
named after its tag). Change a value in the datasheet and the list in the same commit.

- `operating` and `design`: conditions, by key with the unit in the name (`pressure_barg`,
  `temperature_degc`, `flow_kg_h`, ...). `design.pressure_barg` and `design.temperature_degc`
  must match the list's `design_pressure_barg` / `design_temperature_degc`.
- A value is a number or text, or `{value, unit, assumed, source}`: mark every value you have not
  calculated or been given `assumed: true`, and say where it comes from in `source` (the design
  basis, a `DESIGN.md` decision).
- `sizing_basis`: the figures the item is sized from, each with its `reference`.
- `type_specific`: fields of the equipment type (a pump's NPSH, a vessel's volume, ...).

Example, `equipment/datasheets/P-101A.yaml`:

```yaml
tag: P-101A
type: CentrifugalPump
service: Feed pump
operating:
  flow_m3_h: {value: 12.5, unit: m3/h, source: process/design-basis.yaml capacity}
  suction_pressure_barg: 0.3
  discharge_pressure_barg: {value: 6.0, unit: barg, assumed: true, source: DESIGN.md D-004}
  temperature_degc: 25
design:
  pressure_barg: 10
  temperature_degc: 80
materials:
  casing: 1.4408
  impeller: 1.4408
  seal: {value: single mechanical seal, assumed: true}
sizing_basis:
  - {parameter: rated flow, value: "110 % of normal", reference: DESIGN.md D-004}
  - {parameter: differential head, value: {value: 62, unit: m, assumed: true}, reference: DESIGN.md D-005}
type_specific:
  npsh_available_m: {value: 4.5, unit: m, assumed: true}
  driver_kw: 5.5
notes: One of two (A/B), one running, one standby.
```
