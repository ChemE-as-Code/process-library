# HAZOP team session pack: ASU-1, studies H-01 .. H-04

Prepared by an agent on 2026-10-25 for the project owner (D-102), on the owner's delegation of
2026-10-25 ("resolve all of these issues, make good decisions"). **An agent cannot hold the
session or accept anything in it.** Acceptance is by the people in the session. This pack gives
the owner what is needed to hold it: the roles to fill, an agenda, the decisions to take first,
and how to record what the team decides so that `cheme safety hazop check` sees it.

State when this pack was written (commit of D-102 on `stage/basic-close-open`):

| Study | Title | Nodes | Scenarios | Worst band high | medium | low | Actions | State |
|---|---|---:|---:|---:|---:|---:|---:|---|
| H-01 | Main air compressor and precooling | 9 | 44 | 11 | 14 | 19 | 26 | draft |
| H-02 | Front-end purification (TSA) | 10 | 37 | 13 | 14 | 10 | 14 | draft |
| H-03 | Cold box | 12 | 53 | 23 | 19 | 11 | 23 | draft |
| H-04 | Products, storage and backup supply | 13 | 89 | 39 | 34 | 16 | 30 | draft |
| **All** | | **44** | **223** | **86** | **81** | **56** | **93** | |

"Worst band" follows the matrix's action policy: the highest residual band of a scenario over its
categories, or the initial band where no residual is rated (only H02-S32). No scenario is
very-high after its safeguards; 9 are very-high before them. Every high scenario has a proposed
action. All four studies are current against their analysed inputs (re-stamped in D-102) and
report 0 errors and 0 warnings; they stay drafts because every entry is `status: proposed, by:
agent` and the risk matrix is proposed.

Reports to bring to the session (regenerate before it, `build/` is not committed):

```sh
cheme safety hazop report H-01   # build/hazop/H-01.md and .html; likewise H-02, H-03, H-04
```

## 1. Team roles

Roles only. The owner names the people and enters them in `team:` of each study (see section 4).
No one is named here.

| Role | What the role brings | Needed for |
|---|---|---|
| Facilitator (chair) | Runs the method (IEC 61882), keeps time, independent of the design team | all sessions |
| Scribe | Records the decisions in the study files during the session | all sessions |
| Process engineer | Design intent, flowsheet and simulation (D-061, D-066, D-097, D-103) | all sessions |
| Operations | Start-up, shutdown, tanker unloading, maintenance practice, operator response times | all sessions |
| Instrument and control engineer | Loops, selector and cascade (D-096, D-101), trips, fail positions, alarm credits | all sessions |
| Safety and oxygen-service specialist | Oxygen compatibility, enrichment and deficiency, the risk matrix, LOPA follow-up | all sessions |
| Mechanical engineer | Machines (MAC, booster, compander, K-4101, K-4102), pumps, relief devices, materials | H-01, H-03, H-04 |
| Supplier specialists, as needed | TSA (H-02), cold box and expander (H-03), GOX / GAN compressors and vaporizers (H-04) | the nodes listed |

## 2. Agenda

Estimated at 5 minutes per node plus 4 minutes per scenario: the worksheet is pre-filled, so the
team confirms, changes or deletes rows rather than brainstorming from blank. Add time for any
deviation the team adds. About 18.5 hours of worksheet in all, plus the opening block: plan five
half-day sessions of about 4 hours.

### Session 0: decisions first (about 3 hours)

| Item | Minutes |
|---|---:|
| Introduction, scope, the analysed inputs and the state of each study | 15 |
| Risk matrix: accept, change or replace (section 3.1) | 45 |
| Credit convention for residual likelihoods (section 3.2) | 45 |
| The 9 very-high initial scenarios (section 3.3) | 60 |
| How the high-residual actions will be handled (section 3.4); they are taken node by node | 15 |

### Sessions 1 to 4: node by node

| Study | Node | Title | Deviations | Scenarios | Minutes |
|---|---|---|---:|---:|---:|
| H-01 | H01-N1 | MAC inlet filter F-1101 and suction duct AIR-1001 | 2 | 3 | 17 |
| H-01 | H01-N2 | Main air compressor K-1101 with intercoolers E-1101 / E-1102 | 3 | 4 | 21 |
| H-01 | H01-N3 | MAC discharge, aftercooler E-1103, AIR-1002 with check valve, blow-off | 5 | 5 | 25 |
| H-01 | H01-N4 | DCAC C-1101 lower section and sump | 5 | 7 | 33 |
| H-01 | H01-N5 | C-1101 upper section, chimney tray and return CHWR-1001 (I-03) | 4 | 6 | 29 |
| H-01 | H01-N6 | Chilled water supply, C-1102 sump, P-1102A/B, CHW-1001 | 5 | 6 | 29 |
| H-01 | H01-N7 | Evaporative cooler C-1102, WN-1001, WN-1002, make-up | 5 | 8 | 37 |
| H-01 | H01-N8 | DCAC cooling water pumps P-1101A/B and CW-1001 | 2 | 3 | 17 |
| H-01 | H01-N9 | MAC cooler condensate drains CD-1001 / CD-1002 | 2 | 2 | 13 |
| H-01 | | **study total** | | **44** | **221** |
| H-02 | H02-N1 | Feed air inlet AIR-1004, XV-2101A/B, XV-2111A/B | 5 | 2 | 13 |
| H-02 | H02-N2 | Adsorber V-2101A/B in adsorption | 4 | 5 | 25 |
| H-02 | H02-N3 | Adsorber outlet AIR-2001, XV-2102A/B, AIA-2102 / AIA-2103 | 3 | 3 | 17 |
| H-02 | H02-N4 | Dust filter F-2101 and AIR-2002 | 4 | 2 | 13 |
| H-02 | H02-N5 | Regeneration gas supply RG-2001, FV-2105, XV-2109 | 4 | 4 | 21 |
| H-02 | H02-N6 | Regeneration heater E-2101 and RG-2002 | 5 | 5 | 25 |
| H-02 | H02-N7 | Adsorber V-2101A/B in regeneration | 3 | 2 | 13 |
| H-02 | H02-N8 | Regeneration and depressurization outlet to S-2101 | 3 | 3 | 17 |
| H-02 | H02-N9 | Switching sequence KS-2101 | 6 | 8 | 37 |
| H-02 | H02-N10 | Isolation, adsorbent change-out and entry | 3 | 3 | 17 |
| H-02 | | **study total** | | **37** | **198** |
| H-03 | H03-N1 | Booster K-3101 with anti-surge recycle | 4 | 5 | 25 |
| H-03 | H03-N2 | Booster aftercooler E-3104 and trim cooler E-3105 | 6 | 7 | 33 |
| H-03 | H03-N3 | Main heat exchanger E-3101 | 4 | 3 | 17 |
| H-03 | H03-N4 | Expansion turbine KT-3101 | 6 | 5 | 25 |
| H-03 | H03-N5 | HP column C-3101 and the GAN draw | 3 | 5 | 25 |
| H-03 | H03-N6 | Rich liquid and LN reflux through E-3102, LIN draw | 5 | 4 | 21 |
| H-03 | H03-N7 | LP column C-3102 pressure and the waste N2 path | 5 | 4 | 21 |
| H-03 | H03-N8 | LP sump and main condenser-reboiler E-3103, GOX draw | 4 | 5 | 25 |
| H-03 | H03-N9 | LOX product and hydrocarbon purge LOX-3001 | 3 | 2 | 13 |
| H-03 | H03-N10 | LOX drain to V-3101 and VNT-3001 | 4 | 4 | 21 |
| H-03 | H03-N11 | Cold box casing, purge UN-3001, breather, heat in-leak | 6 | 6 | 29 |
| H-03 | H03-N12 | Cold box start-up, warm-up and standstill | 3 | 3 | 17 |
| H-03 | | **study total** | | **53** | **272** |
| H-04 | H04-N1 | GOX-4001 suction to K-4101, low select UY-4151, vent PV-4101B | 7 | 12 | 53 |
| H-04 | H04-N2 | K-4101 GOX compressor, coolers, recycle GOX-4003 | 6 | 8 | 37 |
| H-04 | H04-N3 | GOX-4002 discharge and export, blowdown | 7 | 10 | 45 |
| H-04 | H04-N4 | GAN-4001 suction, K-4102, recycle, off-spec divert | 6 | 7 | 33 |
| H-04 | H04-N5 | GAN-4002 export (PIC-4105 cascade), purge take-off UN-3001 | 4 | 6 | 29 |
| H-04 | H04-N6 | T-4101 LOX tank, rundown, boil-off vent, reliefs | 7 | 8 | 37 |
| H-04 | H04-N7 | LOX tanker fill LOX-4004 | 4 | 6 | 29 |
| H-04 | H04-N8 | LOX backup pumps P-4101A/B | 6 | 6 | 29 |
| H-04 | H04-N9 | LOX vaporizers E-4105A/B and PV-4111 | 4 | 6 | 29 |
| H-04 | H04-N10 | T-4102 LIN tank, rundown, boil-off vent, reliefs | 5 | 5 | 25 |
| H-04 | H04-N11 | LIN tanker fill LIN-4004 | 4 | 5 | 25 |
| H-04 | H04-N12 | LIN backup pumps P-4102A/B | 6 | 6 | 29 |
| H-04 | H04-N13 | LIN vaporizers E-4106A/B and PV-4112 | 3 | 4 | 21 |
| H-04 | | **study total** | | **89** | **421** |

A suggested split: session 1 H-01 and H-02 (about 7 h, or two half days), session 2 H-03,
sessions 3 and 4 H-04 (N1 to N5 with the instrument and control engineer and the compressor
supplier, then N6 to N13 with operations and the vaporizer supplier).

## 3. Decisions to take first

### 3.1 The risk matrix

`safety/risk-matrix.yaml` (asu-1-5x5-proposed) was drafted by an agent (ASSUMED): five
likelihood classes A to E of one order of magnitude each, five severity grades per category
(people, environment, asset with production loss), four bands, and the action policy (high and
very-high require an action; very-high is not accepted for start-up; medium needs an ALARP
statement). The team either:

- accepts it: `status: accepted` and `accepted_by: <who, and the procedure or session record>`;
- changes it (cells, grades, policy), then accepts it; every band is then looked up again
  (`rate --write`) and the ratings near a changed cell are re-read; or
- replaces it with the operating company's matrix, at its revision, and re-rates.

### 3.2 The credit convention

Each study's `assessment_basis` holds the convention the residual ratings use (a proposal, not a
LOPA): a relief device whose listed case covers the cause, or a passive feature that removes the
path, up to two orders; an alarm with operator response, a control loop, a check valve, an
administrative lock, a trip drawn but not in the C&E, or an interlock without a confirmed SIL,
one order each; nothing for a safeguard that shares a transmitter, valve or logic with the cause
or that the cause defeats, nor for a relief device whose case does not cover the cause. Points
for the team to confirm or revise:

- whether a DCS loop and a trip in the same DCS may both be credited (the studies credit them
  separately where they use different transmitters, e.g. H04-S01);
- the low select UY-4151 (D-101) is treated as common to PIC-4102, FIC-4148 and PIC-4150, so its
  failure is a cause (H04-S02, H04-S75, H04-S87, H04-S88, H04-S89) and it is never a safeguard;
- the conditional order used for the condenser-explosion scenarios (H04-S75, H04-S80, H03-S33):
  without it H04-S80 would be very-high residual;
- whether one order for an elevated vent at a safe location becomes two once the zones owner
  confirms the zone for a release of hours (H04-S76, H04-S83, H04-S88; action H04-A26).

### 3.3 The very-high initial scenarios

All nine are high after their safeguards, none very-high. The team confirms the initial rating,
the safeguards credited and the action, or changes them.

| Scenario | Cause (short) | Initial | Residual | Proposed actions | Owners |
|---|---|---|---|---|---|
| H02-S22 | TI-2114A/B reads high and KS-2101 ends the heating step early | very-high | high | H02-A7, H02-A1 | process engineer (with the TSA supplier); process safety engineer |
| H02-S27 | The adsorption step overruns (timer fault, change-over held) | very-high | high | H02-A1, H02-A13 | process engineer (with the TSA supplier); process safety engineer |
| H03-S29 | PIC-3110 fault or wrong split range closes PV-3110A and PV-3110B | very-high | high | H03-A19 | instrument and control engineer |
| H04-S05 | UIC-4103 / UV-4103 fails (or FT-4148 reads high) at reduced off-take: K-4101 surge | very-high | high | H04-A13, H04-A24 | mechanical engineer; process safety engineer |
| H04-S30 | PV-4109 fails closed or PICA-4109 fails: T-4101 overpressure | very-high | high | H04-A25 | instrument and control engineer |
| H04-S38 | Tanker pressurising gas blows through into T-4101 | very-high | high | H04-A04, H04-A25 | instrument and control engineer; operations |
| H04-S55 | PV-4110 fails closed or PICA-4110 fails, heat leak rise or fire: T-4102 | very-high | high | H04-A25 | instrument and control engineer |
| H04-S60 | Tanker gas blow-through or roll-over in T-4102 | very-high | high | H04-A04, H04-A25 | instrument and control engineer; operations |
| H04-S80 | Reduced make with the customer at the design rate: LP sump boil-down | very-high | high | H04-A23, H04-A28 | instrument and control engineer |

### 3.4 Every high-residual scenario and its proposed action

The action policy requires an action for each of these 86. The team takes them node by node in
sessions 1 to 4, and for each one either accepts the action (status `open`, with an owner and a
due date), changes it, or rejects it with a reason (`rejected`, `response`). Many share an action
(for example H04-A23, H04-A25, H03-A20, H02-A4), which can be decided once.

| Scenario | Cause (short) | Initial | Residual | Proposed actions | Owners |
|---|---|---|---|---|---|
| H01-S4 | UIC-1102 fails or UV-1102 sticks closed while the demand falls | high | high | H01-A6 | instrument and control engineer |
| H01-S11 | MAC trip with the AIR-1002 non-return valve failing to close | high | high | H01-A21 | mechanical engineer |
| H01-S13 | LV-1106 sticks closed (or closes on an instrument-air failure) | high | high | H01-A3, H01-A6 | instrument and control engineer |
| H01-S14 | MAC trip while P-1101A/B and P-1102A/B keep running | high | high | H01-A4, H01-A3 | instrument and control engineer; process engineer |
| H01-S15 | FV-1108 fails open or FIC-1108 fails low | high | high | H01-A7, H01-A3 | instrument and control engineer |
| H01-S16 | LV-1106 sticks open or LIC-1106 fails high | high | high | H01-A5, H01-A6 | instrument and control engineer; process engineer |
| H01-S23 | Start-up: MAC loaded with the chimney tray dry, I-03 reset or bypassed | high | high | H01-A10 | operations |
| H01-S24 | LV-1114 fails closed or XV-1115 closes spuriously | high | high | H01-A11 | process engineer |
| H01-S32 | LV-1107 sticks open or LIC-1107 fails low | high | high | H01-A13 | process engineer |
| H01-S36 | Entry into C-1102 with WN-1001 isolated only by PV-3110A | high | high | H01-A15 | operations |
| H01-S43 | WN-1002 obstructed and PIC-3110 fails or its split range is wrong | high | high | H01-A9, H01-A25 | process safety engineer |
| H02-S2 | XV-2101A/B opened on a depressurized bed instead of XV-2111A/B | high | high | H02-A4, H02-A5 | instrument and control engineer; process engineer |
| H02-S10 | AIA-2102 fails low or stale while a breakthrough develops | high | high | H02-A1 | process safety engineer |
| H02-S12 | F-2101 element collapse, rupture, leaking seal or wrong element | high | high | H02-A9 | process engineer |
| H02-S19 | XV-2103A/B of the bed on line opens spuriously | high | high | H02-A3, H02-A4, H02-A5 | instrument and control engineer; process engineer |
| H02-S22 | (see 3.3) | very-high | high | H02-A7, H02-A1 | |
| H02-S24 | XV-2104A/B opens on the bed still at about 5.8 bara | high | high | H02-A4, H02-A5 | instrument and control engineer; process engineer |
| H02-S25 | XV-2104A/B or XV-2112A/B of the bed on line opens spuriously | high | high | H02-A4, H02-A6 | instrument and control engineer |
| H02-S27 | (see 3.3) | very-high | high | H02-A1, H02-A13 | |
| H02-S29 | XV-2103A/B of the bed taken off line opens before depressurization | high | high | H02-A3, H02-A4, H02-A5 | instrument and control engineer; process engineer |
| H02-S32 | Power or instrument-air failure in any step: fail positions not stated (initial only) | high | not rated | H02-A6 | instrument and control engineer |
| H02-S33 | KS-2101 restarts in a default step after a power dip or reset | high | high | H02-A6, H02-A7 | instrument and control engineer; process engineer (with the TSA supplier) |
| H02-S35 | Entry into V-2101A/B or F-2101 with waste N2 present | high | high | H02-A10 | operations / process engineer |
| H02-S36 | Work on an isolated bed while the other runs at 5.9 bara | high | high | H02-A10 | operations / process engineer |
| H03-S1 | UIC-3120 fault or UV-3120 sticking closed at low booster flow | high | high | H03-A2 | instrument and control engineer |
| H03-S9 | E-3104 tube leak while the booster is stopped | high | high | H03-A11 | process engineer |
| H03-S14 | Warm boosted air readmitted to a cold E-3101, abrupt stream changes | high | high | H03-A10, H03-A17 | cold box supplier; process engineer |
| H03-S16 | Expander brake load lost or SIC-3108 nozzle control fails open | high | high | H03-A2 | instrument and control engineer |
| H03-S18 | Compander seal gas lost or low while the lube oil pump runs | high | high | H03-A2 | instrument and control engineer |
| H03-S22 | Long cold standstill: heat leaks into the liquid inventory | high | high | H03-A20 | process engineer |
| H03-S24 | LV-3101 fails closed or LIC-3101 fails low | high | high | H03-A8 | instrument and control engineer |
| H03-S25 | LV-3101 fails open or LIC-3101 fails high: HP sump empties | high | high | H03-A20 | process engineer |
| H03-S29 | (see 3.3) | very-high | high | H03-A19 | |
| H03-S31 | PV-3110B opens fully and diverts the waste N2 to S-3101 | high | high | H03-A19, H03-A1 | instrument and control engineer |
| H03-S33 | FV-3111 fails open or FIC-3111 fails low: more LOX drawn than made | high | high | H03-A4, H03-A3 | process engineer; process safety engineer |
| H03-S34 | Refrigeration deficit: compander trip, XV-3117 closure, cooling lost | high | high | H03-A4 | process engineer |
| H03-S35 | Continuous LOX purge lost and the drain not opened | high | high | H03-A3, H03-A5 | process engineer; process safety engineer |
| H03-S36 | LOX draw stopped with excess refrigeration | high | high | H03-A4 | process engineer |
| H03-S40 | VNT-3001 restricted during a drain | high | high | H03-A6 | process engineer |
| H03-S41 | Repeated LOX drains evaporated to dryness in V-3101 | high | high | H03-A6 | process engineer |
| H03-S45 | Internal cryogenic leak into the perlite | high | high | H03-A14 | cold box supplier |
| H03-S47 | Casing entry or perlite removal with the purge connected | high | high | H03-A15 | operations |
| H03-S48 | Expander to full refrigeration too early at start-up | high | high | H03-A17, H03-A10 | cold box supplier; process engineer |
| H03-S49 | Warm-up started with LOX still in the LP sump | high | high | H03-A16 | operations |
| H03-S50 | Total power failure with the cold box full of liquid | high | high | H03-A1, H03-A16 | instrument and control engineer; operations |
| H03-S51 | AIA-3103 fails low or stale while hydrocarbons or N2O enter | high | high | H03-A24, H03-A3 | process engineer; process safety engineer |
| H03-S52 | Liquid blocked in on RL-3001, LN-3001 or E-3102 passages | high | high | H03-A20 | process engineer |
| H04-S01 | K-4101 trips and PV-4101B fails to open | high | high | H04-A20, H04-A14 | electrical and instrument engineer; process engineer |
| H04-S02 | Low select over-opens the K-4101 vanes (FT-4148 low, UY-4151 or positioner high) | high | high | H04-A23 | instrument and control engineer |
| H04-S04 | Particles or hydrocarbons left in GOX-4001 or XV-4117 | high | high | H04-A13, H04-A18, H04-A24 | mechanical engineer; operations; process safety engineer |
| H04-S05 | (see 3.3) | very-high | high | H04-A13, H04-A24 | |
| H04-S06 | Cooling water to E-4102 / E-4101 lost or reduced | high | high | H04-A12 | process engineer |
| H04-S07 | Ignition inside K-4101 | high | high | H04-A01, H04-A02, H04-A13, H04-A24 | instrument and control engineer; mechanical engineer; process safety engineer |
| H04-S08 | K-4101 dry gas seal buffer gas lost | high | high | H04-A13 | mechanical engineer |
| H04-S12 | Total power failure: compressors and backup pumps lose supply | high | high | H04-A14 | electrical and instrument engineer |
| H04-S14 | Flange or instrument connection leak on GOX-4002 | high | high | H04-A15 | process engineer |
| H04-S19 | UIC-4131 fails or UV-4131 sticks closed at reduced GAN off-take | high | high | H04-A13 | mechanical engineer |
| H04-S20 | FIC-3107 or PIC-4106 fails high: K-4102 draws the HP column down | high | high | H04-A22 | instrument and control engineer |
| H04-S24 | PV-4105 fails or is left closed, or XV-4120 closes: K-4102 blocked outlet | high | high | H04-A06, H04-A14 | electrical and instrument engineer; process engineer |
| H04-S27 | PIC-4105 fails high and raises FIC-3107's set point | high | high | H04-A22 | instrument and control engineer |
| H04-S29 | LOX rundown fills T-4101 unwatched | high | high | H04-A03 | process engineer |
| H04-S30 | (see 3.3) | very-high | high | H04-A25 | |
| H04-S33 | Hydrocarbons concentrate in T-4101 as the LOX boils off | high | high | H04-A07 | process engineer |
| H04-S36 | T-4101 opened after warm-up without purging the oxygen out | high | high | H04-A18 | operations |
| H04-S37 | LOX tanker fill continued past the maximum level | high | high | H04-A03, H04-A04 | operations; process engineer |
| H04-S38 | (see 3.3) | very-high | high | H04-A04, H04-A25 | |
| H04-S44 | Standby LOX pump warm when PIC-4111 starts it | high | high | H04-A08 | instrument and control engineer |
| H04-S49 | PIC-4111 fails or PV-4111 fails open: vaporizer over-rated | high | high | H04-A01, H04-A02 | instrument and control engineer; process safety engineer |
| H04-S54 | LIN rundown fills T-4102 unwatched | high | high | H04-A03 | process engineer |
| H04-S55 | (see 3.3) | very-high | high | H04-A25 | |
| H04-S58 | T-4102 or N2-purged equipment entered without purging to air | high | high | H04-A18 | operations |
| H04-S59 | LIN tanker fill continued past the maximum level | high | high | H04-A03, H04-A04 | operations; process engineer |
| H04-S60 | (see 3.3) | very-high | high | H04-A04, H04-A25 | |
| H04-S61 | LOX unloaded into T-4102 by mistake | high | high | H04-A04, H04-A16 | operations; process engineer |
| H04-S62 | Hose or coupling failure during a transfer | high | high | H04-A04, H04-A19 | operations; process engineer |
| H04-S65 | Standby LIN pump warm when PIC-4112 starts it | high | high | H04-A08 | instrument and control engineer |
| H04-S68 | Seal or flange leak at P-4102A/B | high | high | H04-A19 | process engineer |
| H04-S74 | Seal or flange leak at P-4101A/B | high | high | H04-A19 | process engineer |
| H04-S75 | Low select over-draws at the design make: LP sump boil-down | high | high | H04-A23 | instrument and control engineer |
| H04-S76 | Turndown: PV-4101B vents GOX for hours | high | high | H04-A26 | process engineer |
| H04-S77 | Leak on GOX-4002 or the customer line: PIC-4102 opens the vanes | high | high | H04-A15 | process engineer |
| H04-S79 | Reduced make with the customer at the design rate: GOX over-draw | high | high | H04-A23, H04-A28 | instrument and control engineer |
| H04-S80 | (see 3.3) | very-high | high | H04-A23, H04-A28 | |
| H04-S84 | GAN demand above the design draw at the design make | high | high | H04-A22 | instrument and control engineer |
| H04-S85 | Reduced HP column make with the customer at the design GAN rate | high | high | H04-A22, H04-A28 | instrument and control engineer |
| H04-S86 | Leak on GAN-4002 or the customer line: PIC-4105 raises the draw | high | high | H04-A15 | process engineer |

The causes are shortened here; the study files and the reports hold the full text, the
safeguards and the rating bases.

### 3.5 Items new in this revision (D-102) for the team's attention

- H04-S87, H04-S88, H04-S89: failures of the drawn low select UY-4151 (output high or frozen,
  output low, reset windup), with action H04-A30 (selector specification and test).
- H03-S53 and action H03-A25: heat in-leak above the expander margin (the 50 kW leak of D-103 is
  ASSUMED; the expander covers about 130 kW).
- H01-S44 and action H01-A26: C-1102 water towards freezing, since the waste N2 is now 9.5 C
  with an adiabatic saturation temperature of about 0.3 C (D-103).
- H04-S24 revised: PV-4105 has no drawn controller since D-101.

## 4. How to record acceptance in the files

Only the scribe edits, during or right after the session, and only what the team decided.

1. **Team.** In each study, fill `team:` with the people present and their roles, e.g.
   `- {name: <name>, role: facilitator}`. Replace the "Team not named" sentence in `notes:` with
   the session dates and the record of attendance.
2. **Risk matrix.** In `safety/risk-matrix.yaml`, set `status: accepted` and
   `accepted_by: <who, and the procedure or session record>`, or replace the file with the
   company's matrix. Update the comment and `notes` that call it a proposal.
3. **Nodes, deviations, scenarios, safeguards and ratings.** For each entry the team accepts, set
   `status: accepted` and `by: <the team, or the person and session>`. Change the text or the
   codes first where the team changes them, and give the basis; delete an entry the team rejects
   (its id is never reused). A rating's `band:` is never edited by hand.
4. **Actions.** For each action the team keeps, set `status: open`, an `owner` (a person or a
   role the owner assigns) and `due: YYYY-MM-DD`; for one it rejects, `status: rejected` with the
   reason in `response`. An action is `closed` only later, with `response` saying how, by its
   owner.
5. **Bands and check.** After the edits:
   ```sh
   cheme safety hazop rate H-01 --write      # likewise H-02, H-03, H-04
   cheme safety hazop check                  # 0 errors; state 'assessed' once all is accepted
   cheme validate
   ```
   A study is `assessed` when it is complete, current and every entry is accepted. If an analysed
   input changes before that, `check` reports `hazop-input-changed`: reassess the touched nodes,
   then `cheme safety hazop stamp <id> --write`.
6. **Human review.** A person who did not author the studies reviews them:
   ```sh
   cheme safety hazop review H-01 --write    # reviews/<date>-hazop-H-01.md, likewise for the others
   ```
   The reviewer fills in `reviewer` (their name) with `reviewer_kind: human` under
   `topic: hazop`, writes the findings and commits the record. With a current human review the
   studies become `reviewed`. The stage gates (`kind: hazop`, `kind: review` with
   `require_kind: [human]`, safety/README.md) can then be added to `checks/checks.yaml`.
7. **Reports.** `cheme safety hazop report <id>` regenerates `build/hazop/<id>.md` and `.html`
   for the minutes.

Nothing in this pack is an approval. The agent-written review records (`reviewer_kind: agent`)
do not count as the human review.
