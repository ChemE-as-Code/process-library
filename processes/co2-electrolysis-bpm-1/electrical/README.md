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
  notional plot to the east (points, no building); the seven motors (P-x01, K-x31, K-x41,
  P-202) with ASSUMED IEC ratings; the AC feeders of the rectifiers U-x01, the PSA packages
  X-x31 and the oxidisers X-x32; the **48 V DC bus** as its own cable class: one radial cable
  per stack from its own DC output on the rectifier (rooms `DC-x01A` to `D`, kind `mcc` at
  48 V, since core has no DC kind, at 3.1 m: the riser from the cabinet top at 1.35 m is not
  modelled, regen step 24 adds its length to the record, D-045), fed directly, never on the
  rack's AC tray; one junction box
  per skid (JB-101, JB-201) outside the zone 2; the points of the actuated valves, the
  transmitters on the skipped DN 15 lines, the gas detectors and the rectifier current signals
  (each one pair in core's model; the rectifier interface needs three or more, open, D-045).
  Every value ASSUMED; no Ex certification is claimed (the Ex rating is the owner's open
  decision, D-031 item 12).
- `tray-rules.yaml`: the PR-1 tray tier at 2.85 m, branches at 2.5 m or higher, `rack_reach_m`
  5.1 m (keeps the DC cables off the rack), router grid 0.25 m; the rest package defaults.
- `cable-schedule.csv`, `.md`: written by `scripts/regen.py` step 24 (`cheme layout cables
  --write`); at 1,000 h 62 cables (21 power, 8 of them 48 V DC; 41 instrument), 40 trays.
