# Review: basic engineering close-out (S6)
Scope: stage basic, sheets P-01..P-04, lists, layout/, DESIGN.md D-001..D-026, branch s6-basic-closeout
Reviewer: process engineering agent (Claude)   Date: 2026-10-18

`plantcode validate`: 12 files, 0 errors, 0 warnings (info only: E-3103 not placed because it sits
inside C-3102; two literal trip notes on TSLL-4113/4114). Compared: 4 sheets, 8 lists (design basis,
equipment, lines, instruments, checks, site plan, building, placement), cross-checks equipment /
lines / instruments vs P&IDs and layout. `plantcode check`: all concept and basic gates ok.

## Findings
| # | sheet | item | finding | severity | proposed action |
|---|---|---|---|---|---|
| 1 | P-04 | UIC-4103, FI-4148 | The FI-4148 -> UIC-4103 signal and the trip outputs (LALL, TSLL, TSHH) are written as notes, not drawn as signal lines. | low | Draw signal lines with the cause and effect matrix in detail engineering. |
| 2 | P-04 | GOX-4004, GAN-4003 | No check valves on the backup risers; justified in D-024 (risers rated for header pressure, PV tight shut-off, no check valve flutter site in 30 bar GOX). | low | Confirm in HAZOP. |
| 3 | P-04 | LALL notes | The LALL trip notes sit beside the TSLL bubbles, not beside LIA-4107/4108 (no free space at the tank edge); the LIN note runs close to PV-4112. | low | Move with the next P-04 drawing tidy. |
| 4 | P-04 | HV-4146/4147 | Tanker fill block valves are manual; a tanker-bay ESD (remote closing) is common practice for LOX transfer. | medium | Decide in HAZOP; would become XV with fail-close. |
| 5 | layout | cold box | The cold box enclosure is not an equipment-list item; its ~50 m height is represented by the stacked C-3101/C-3102 placements only. | low | Add a cold box structure tag (or building) in detail engineering. |
| 6 | P-02 | OPC_RG2001 note | S4 finding 8 (note crosses the FIC-2105 measuring line) not rechecked. | low | Check with --crop. |
| 7 | all | sizes | Tank, rack, building and equipment dimensions are ASSUMED; hydraulics (NPSH of P-4101/4102, pump heads) not calculated. | medium | Vendor data and hydraulic calculations in detail engineering. |

## Checked and fine
- Process: double column without argon column, air/O2 ratio 5.2 with recovery 94 % (D-018), GOX via
  oil-free external compressor (D-002), GAN 9 bara via K-4102, backup supply on header low pressure
  (D-014), storage volumes: LOX 219 m3 net / 250 working, LIN 372 m3 net / 400 working / ~440 gross (D-017).
- O2 safety: materials and cleaning (D-009), no oil in O2 service (D-012), hydrocarbon protection
  (continuous LOX purge, AIA-3103 sump, AIA-4121 tank, AIA-2102 CO2/N2O after TSA; O2 review F1..F7
  closed), relief case list with perlite-tank wording corrected, vents separated per pressure level
  (D-019) and grouped downwind of the MAC intake (D-025), equalizing bypasses on GOX ESD valves,
  K-4101 in the open behind a fire wall, LOX tank distances and concrete fill pad (D-026).
- P-04 after the S5 findings: FI-4148 at the K-4101 suction, FQI-4149 at the GOX BL, LOX-4004 /
  LIN-4004 tanker fill (hose coupling, check valve, TSV, block valve, nozzle N6), LALL pump trips,
  PV-4101A resolved as IGV output A, LIN-3001 off-page label. Full sheet and crops of both fill
  lines and the GOX BL rendered and read: no overlaps of symbols or labels.
- Lists in step with the four sheets (validate cross-checks), layout tags match the equipment list,
  MAC house B1 contains K-1101 and E-1101/1102/1103 with level L0, racks clear of equipment.

## Not checked
- P-01..P-03 not re-rendered in this stage (no changes since their crop checks in S5).
- Hydraulics, relief valve sizing, cold box structural design, noise study.
- Signal lines / C&E matrix (detail engineering).
