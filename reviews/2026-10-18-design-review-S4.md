# Review: design review, stage S4 (P-01..P-04 basic P&IDs)
Scope: main, commits 96f44a7 (S3 review fixes) and 6fb6470 (P-04); all sheets and lists   Reviewer: agent (self-review; an independent review should follow)   Date: 2026-10-18

## Method
- `plantcode validate --fail-on warning`: 0 errors, 0 warnings; compared 4 sheets, 5 lists, cross-checks
  equipment / lines / instruments vs P&IDs.
- `plantcode check`: all concept and basic gates pass once this record and the O2 safety review exist.
- `plantcode diff 217d3a9 --list`: every changed item belongs to the S3 review fixes or to P-04; reasons in
  PROGRESS.md, D-003, D-023, D-024.
- Full-sheet PNG renders of P-02, P-03, P-04 looked at.

## Findings
| # | sheet | item | finding | severity | proposed action |
|---|---|---|---|---|---|
| 1 | P-04 | O2 safety F1..F7 | See reviews/2026-10-18-o2-safety-review.md (equalizing bypasses, impingement materials, tank outlet and pump isolation, TSVs). | high | Fix before stage sign-off. |
| 2 | P-04 | UIC-4103 | Measuring line from the K-4101 package (I2) to the bubble runs a long way down past E-4101 and crosses the recycle line. | low | Move the bubble or show the anti-surge transmitters (FT on the suction, PT on suction and discharge) on the lines. |
| 3 | P-04 | PIC-4102, PIC-4106, TSLL-4113/4114, TSHH-4104 | Outputs (cascade to K-4101, K-4102 trips, pump trips) are in the instrument list notes but not drawn as signal lines. | low | Draw trip signals or add an interlock reference note per bubble. |
| 4 | P-04 | PSV-4125, PSV-4126 | Pump discharge PSVs end in arrows "to T-4101/T-4102" instead of a drawn return line to the tank vapour space. | low | Draw the return lines when F3 of the O2 review adds the pump isolation. |
| 5 | P-04 | E-4101 | Intercoolers drawn as one loop (GOX-4005) for all stages, without CW connections (vendor package). | low | Keep; vendor P&ID to be referenced. |
| 6 | P-03 | C-3101 | No pressure indication on the HP column (only PSV-3116); no PI at the HP top for the condenser temperature difference. | low | Add PI on C-3101 (optional item from the S3 review). |
| 7 | P-02 | V-2101A/B, RG-2002 | Optional S3 items open: PDI across the adsorbers, TSHH on RG-2002 downstream of E-2101. | low | Add in the next P-02 change. |
| 8 | P-02 | OPC_RG2001 note | "from P-03 WN-3002 (RG-2001)" crosses the FIC-2105 measuring line. | low | Move the note left/up. |
| 9 | P-01 | line labels | P-01 still uses the stacked label form (generator not switched to LABEL_ROW); not reported as crossed, not rechecked here. | low | Check P-01 with --crop; switch if needed. |

## Status of the findings (S6, 2026-10-18)
| # | status | how |
|---|---|---|
| 1 | closed | O2 review F1..F7 closed in S5/S6, see the status table in the O2 safety review |
| 2 | partly closed | FI-4148 now on GOX-4001 at the K-4101 suction as UIC-4103 input (D-024); the long UIC-4103 measuring line is kept, signal lines with the C&E matrix in detail engineering |
| 3 | closed | trip outputs written beside TSHH-4104, PIC-4102, TSLL-4113/4114 and the new LALL trips (D-024) |
| 4 | closed | PSV-4125 / PSV-4126 relieve into the drawn returns LOX-4003 / LIN-4003 |
| 5 | accepted | vendor package, vendor P&ID referenced in detail engineering |
| 6 | closed | PI-3121 on the HP column top (P-03) |
| 7 | closed | PDI-2115A/B on the adsorbers, TSHH-2116 on RG-2002 (P-02) |
| 8 | open (cosmetic) | not rechecked in S6 |
| 9 | closed | P-01 label tidy after crop check (S-1101, E-1101/E-1102 CW/CWR) |

## Checked and fine
- Off-page continuity: GOX-4001, GAN-4001 (P-03 E-3101 -> P-04 K-4101/K-4102), LOX-3001 (P-03 FV-3111 -> P-04 T-4101), LIN-3001 (P-03 -> T-4102), UN-3001 (P-04 GAN-4002 -> P-03 PV-3113), RG-2001 (P-03 -> P-02) carry the same line numbers and DN on both sheets.
- S3 findings 1-4 fixed: line labels on one row (P-02, P-03), PSV-3114/3116 discharge arrows, K-3101 anti-surge (AIR-3006, UV-3120, UIC-3120) and discharge check valve, AIA-3103 on LOX-3001, LIC-3101 on the HP sump, E-3101 tag at the exchanger.
- Check valves on all pump and compressor discharges (P-4101A/B, P-4102A/B, K-4101, K-4102, K-3101).
- Relief device for every case in the relief case list except the TSVs and vacuum breakers (O2 review F4).
- DN consistent along every line (validate dn-mismatch clean); line list DNs match the sheets.

## Not checked
- Layout (layout/) against the new P-04 equipment and vent stacks.
- Hydraulics: pump heads, NPSH of P-4101/P-4102, vaporizer duties beyond the equipment list values.
- P-01 drawing at crop level after the S2 review.
