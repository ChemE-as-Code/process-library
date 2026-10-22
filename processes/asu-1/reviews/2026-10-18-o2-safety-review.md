# Review: oxygen safety (EIGA Doc 13 / 33 / 65 checklist)
Scope: stage basic, sheets P-01..P-04, DESIGN.md D-009..D-014, D-019, D-023, D-024   Reviewer: agent (process engineer, self-review; an independent O2-safety reviewer must repeat it)   Date: 2026-10-18

Basis: EIGA Doc 13 (oxygen pipeline and piping systems), EIGA Doc 33 (cleaning of equipment for
oxygen service), EIGA Doc 65 (safe operation of reboilers/condensers in air separation units).
Checklist items paraphrased from the documents' headings; clause numbers to be added by the
independent reviewer. Limits marked ASSUMED in DESIGN.md are not verified against the documents here.

## Checklist

| # | topic (doc) | requirement (paraphrased) | where in the design | status |
|---|---|---|---|---|
| 1 | Materials (13) | Exempt materials (Monel, copper alloys) where velocity / pressure exceed the limits of SS/CS; velocity limits by pressure | D-009, line list (GOX-4002 ~5 m/s at 31 bara SS), K-4101 Monel/copper (D-002) | ok at concept level; impingement sites see F1 |
| 2 | Impingement sites (13) | Control, throttling and quick-opening valves at high pressure in exempt material; equalize before opening | XV-4116..4119, PV-4111, UV-4103, PV-4101B | closed (F1 S4, F2 S5) |
| 3 | Cleaning (33) | All O2-wetted equipment cleaned for oxygen service, inspected, kept clean (caps, N2 blanket) | D-009 | ok (procedure in detail engineering) |
| 4 | Oil (13/33) | No oil-lubricated equipment in O2 service; oil kept out of process air to the columns | D-012: K-4101 oil-free with dry gas seals and N2 buffer; LOX pumps no oil in wetted parts; compander PDSLL-3115 seal gas permissive | ok |
| 5 | Compressor fire (13) | GOX compressor in fire-safe enclosure, fire detection, trip, isolation and blowdown | D-002, D-013; P-04 TSHH-4104, XV-4117/4118, XV-4116 to VNT-4002/S-4101 | ok; enclosure and deluge not drawn (vendor) |
| 6 | Vents (13) | O2 vents to a safe location: elevated, away from ignition sources, walkways, air intakes; separate from N2/other vents | D-011, D-019; P-03 PSV-3114 "outside cold box, elevated, safe location", VNT-3001; P-04 VNT-4001/4002/4003 notes | ok; vent stack locations to the plot plan, F5 |
| 7 | Hydrocarbon intake (65) | Air intake away from hydrocarbon sources; front-end removal of CO2, N2O, C2H2 | D-006, P-02 AIA-2102/2103 at the adsorber outlet | ok; N2O/C2H2 breakthrough monitoring scope to confirm, F6 |
| 8 | Reboiler submergence (65) | Main condenser kept fully submerged; low-level alarm | D-010, P-03 LICA-3102 on the LP sump | ok |
| 9 | Liquid purge (65) | Continuous LOX withdrawal from the sump >= minimum purge to prevent concentration | P-03 LOX-3001 with FIC-3111 / FV-3111 (low-flow alarm), D-010 | ok (purge rate ASSUMED 0.2 %) |
| 10 | Sump analysis (65) | Hydrocarbon (THC, C2H2) analysis of the sump liquid with alarm and action limits | P-03 AIA-3103 on LOX-3001 at the sump outlet | ok (limits ASSUMED) |
| 11 | Storage analysis (65) | Hydrocarbons in LOX storage that receives the purge | P-04 AIA-4121 on the T-4101 bottom | ok |
| 12 | Dead ends / drains (65) | No liquid dead legs where LOX can boil off and concentrate; drains to a vaporizer, not to pits | P-03 LOX-3002 / HV-3118 to V-3101; D-011 | open, F3 |
| 13 | Relief (13) | Every blocked-in volume relieved; trapped cryogenic liquid has thermal relief | Relief case list (DESIGN.md section 4); PSVs on P-01..P-04 | closed (S5: TSV-4140/4141, PSV-4125/4126 into LOX-4003/LIN-4003) |
| 14 | Isolation (13) | Emergency isolation and DBB at the battery limit | D-013; XV-4119 / XV-4120 | closed (S5: XV-4132/4133, XV-4134/4135) |
| 15 | Off-spec product (13) | Off-spec GAN (O2 trace) diverted before the customer | AIA-3105 -> XV-3105 to VNT-4004, XV-4120 closes | ok |
| 16 | Cold box (65) | Casing purged with dry N2; O2 enrichment of the casing monitored | P-03 UN-3001, PIC-3113 | closed (S5: AIA-3122 on VNT-3004) |

## Findings
| # | sheet | item | finding | severity | proposed action |
|---|---|---|---|---|---|
| F1 | P-04 | XV-4116, XV-4118, XV-4119, PV-4111, UV-4103 | Valves at 31 bara GOX are drawn as plain ball/globe valves; their impingement-site material (Monel / copper alloy body and trim) is not stated on the P&ID or a valve list. | high | Add the material note to the line list / valve data; keep throttling (PV, UV) as globe valves in exempt material. |
| F2 | P-04 | XV-4118, XV-4119, XV-4120 | No pressure-equalizing bypass around the high-pressure ESD valves; opening a ball valve against 30 bar differential causes adiabatic compression downstream. DBB at the BL drawn as one valve. | high | Add a small equalizing bypass (globe, exempt material) around XV-4118/XV-4119 with a start permissive on dP; draw the second block valve and bleed at both BLs. |
| F3 | P-04 | T-4101 outlet, LOX-4001 | No isolation valve at the tank outlet and none at the pump suctions: a pump cannot be isolated for maintenance, and the tank has no remote shut-off on a line break. | medium | Add a fail-closed tank outlet valve and manual suction/discharge block valves per pump, plus a cool-down/vent return to the tank. |
| F4 | P-03, P-04 | trapped liquid sections | TSVs on blocked-in liquid sections (LOX-3001 between FV-3111 and the tank inlet, LOX-4002 between check valve and vaporizer inlet valve, LIN equivalents) are listed in the relief case list but not drawn. | medium | Draw TSVs when isolation valves of F3 are added. |
| F5 | P-04 | VNT-4001..4005 | Vent outlets carry "safe location" notes only; their positions relative to the air intake (F-1101) and to each other are not yet in the layout. | medium | Place vent stacks in layout/ and check distances to F-1101 and walkways. |
| F6 | P-02 | AIA-2102/2103 | It is not stated which components are measured after the adsorbers (CO2 only, or also N2O / C2H2 breakthrough). | low | State the analyzer components in the instrument list. |
| F7 | P-03 | cold box casing | No O2 analyzer on the casing purge exhaust (O2 enrichment from a leak). | low | Add AI on the casing breather outlet. |

## Status of the findings (S5, 2026-10-18)

| # | status | where it was closed |
|---|---|---|
| F1 | closed (S4) | impingement-site materials on GOX-4002 in the line list (commit 521473c) |
| F2 | closed (S5) | equalizing bypasses HV-4129/HV-4130 (S4); true DBB at both BLs: GOX XV-4119 + XV-4132, bleed XV-4133 to VNT-4006; GAN XV-4120 + XV-4134, bleed XV-4135 to VNT-4007 (D-013) |
| F3 | closed (S5) | fail-closed XV-4136 / XV-4137 at the tank outlets; manual suction and discharge block valves per pump; cool-down / min-flow returns LOX-4003 / LIN-4003 to the tank vapour space (D-014) |
| F4 | closed (S5) | TSV-4140 / TSV-4141 on LOX-3001 / LIN-3001 (FV-3111 to the new tank inlet valve); PSV-4125 / PSV-4126 cover LOX-4002 / LIN-4002 from the check valves to the vaporizer inlet valves and now relieve into the return lines; vacuum breakers PSV-4142 / PSV-4143 |
| F5 | closed (S5) | layout/site-plan.yaml vent area V1, ~190 m downwind of F-1101 (D-025) |
| F6 | closed (S6) | instrument list: AIA-2102 measures CO2 and N2O (two-channel NDIR), AIA-2103 the H2O dew point; C2H2 not continuous at the TSA outlet (held far beyond CO2 breakthrough, CO2 is the leading indicator), measured in the LP sump (AIA-3103) and LOX tank (AIA-4121) |
| F7 | closed (S5) | casing breather VNT-3004 / PSV-3123 with AIA-3122 (P-03) |

References: the findings cite EIGA Doc 13 (oxygen pipeline and piping systems: impingement
velocity, valve materials, pressure equalization, isolation), Doc 33 (cleaning for oxygen
service) and Doc 65 (reboiler/condenser operation: liquid purge, hydrocarbon limits, analyzers)
at document level only. Clause numbers are not given here because the documents are not in the
repository and the clause numbering changes between editions; they are to be added from the
edition the client specifies (open item, not a guess).

## Checked and fine
- No oil-lubricated machine in O2 service; compander oil isolated by seal gas permissive (D-012, PDSLL-3115).
- LP column relief PSV-3114 and all O2-rich vents end at "to atm." arrows with "safe location" notes.
- Hydrocarbon protection chain: submergence (LICA-3102), purge (FIC-3111), sump analysis (AIA-3103), storage analysis (AIA-4121), drain to vaporizer V-3101.
- GOX compressor: suction vent separate from the blowdown and from the tank vent (D-019).

## Not checked
- Clause-by-clause compliance and numerical limits of EIGA 13/33/65 (documents not in the repository).
- Velocity/pressure curves for each O2 line (only the main export line is quoted).
- Vendor packages: K-4101 seal gas system, enclosure, deluge; LOX pump seals.
