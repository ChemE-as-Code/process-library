# Electrical

Electrical rooms, the motor list, junction boxes and the cable trays of the 3D model (skill
`electrical-cabling`).

| file | what | written by |
|---|---|---|
| `electrical-list.yaml` | substations, transformers, rooms (`kind: mcc \| switchgear \| control \| rack_room`, in a building of `layout/building.yaml`), `defaults`, `motors` (power, voltage and room of the motors derived from the driven equipment; `cable_entry` where a motor's cable leaves the tray beside the machine), `feeders`, `junction_boxes`, `instruments` (`cheme schema electrical`) | people |
| `tray-rules.yaml` (optional) | tray widths, depth, fill, power/instrument separation, rack tray tiers, several power trays per rack (`power_trays`, e.g. HV and LV apart) (`cheme schema trays`); every default is ASSUMED | people |
| `cable-schedule.csv`, `cable-schedule.md` | every cable: from, to, size, trays, length | `cheme layout cables --write` |

Example `electrical-list.yaml`:

```yaml
rooms:
  - {id: MCC-1, kind: mcc, building: SUB-1}
  - {id: CR-1, kind: control, building: SUB-1}
motors:                       # derived from pumps, compressors, fans, ...; give what the
  - {driven: P-101A, power_kw: 15, source: vendor data sheet}   # datasheet does not
junction_boxes:               # optional: without them one is proposed per area
  - {tag: JB-101, point: [24.0, 12.5, 1.2], instruments: ["*-1*"]}
```

`cheme layout build` places the trays and cables in `layout/plant-model.yaml`; never edit
the schedule by hand.

## This process (DESIGN.md D-045)

- `electrical-list.yaml`: the host site's 400 V board `SDB-1` and control room `CR-1`, off the
  notional plot to the east (points, no building); the five motors (P-x01, K-x31, P-202; the
  extract fans K-x41 are deleted with the enclosure, D-050) with ASSUMED IEC ratings; the AC
  feeders of the rectifiers U-x01, the PSA packages X-x31 and the oxidisers X-x32; the **48 V DC bus** as its own cable class: one radial cable
  per stack from its own DC output on the rectifier (rooms `DC-x01A` to `D`, kind `mcc` at
  48 V, since core has no DC kind, at 3.1 m: the riser from the cabinet top at 1.35 m is not
  modelled, regen step 24 adds its length to the record, D-045), fed directly, never on the
  rack's AC tray; one junction box
  per skid (JB-101, JB-201) at grade north of its frame, outside the zone 2 (D-047); the points of the actuated valves, the
  transmitters on the skipped DN 15 lines, the gas detectors and the rectifier current signals
  (each one pair in core's model; the rectifier interface needs three or more, open, D-045).
  Every value ASSUMED. The Ex marking of the items in the zones is the owner's decision
  (D-051): motors II 2G Ex db eb IIC T3 Gb, instruments Ex ia IIC T4 Ga with barriers or
  isolators outside the zone, certified IIC gas detectors, 3G/Gc the stated minimum; no
  certification is claimed, the area classification is the competent person's.
- `tray-rules.yaml`: the PR-1 tray tier at 3.25 m (the rack north of the skids since D-047),
  branches at 2.5 m or higher, `rack_reach_m` 5.5 m (keeps the DC cables off the rack), router
  grid 0.25 m; the rest package defaults. Regen step 13 keeps every tray 1 m from the vent and
  flue outlets (`layout/layout-checks.yaml`, D-047).
- `cable-schedule.csv`, `.md`: written by `scripts/regen.py` step 24 (`cheme layout cables
  --write`); at 1,000 h 76 cables (19 power, 8 of them 48 V DC; 57 instrument, with the
  tail-gas trip valves XV-x33 and arrester temperatures TSHH-x33 of P&ID revision B, D-054,
  and the transmitters of revision C, D-065: per skid FIC-x04, PIA-x13, AIA-x14, PIA-x23,
  LIA-x24, PIA-x32), 35 trays; the oxidisers' feeders end at their burner-management panels
  east of the tail gas's east leg (D-065).
