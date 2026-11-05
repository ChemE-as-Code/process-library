# HAZOP team session pack: co2-electrolysis-bpm-1, studies H-01 and H-02

Prepared by agents on 2026-11-05 for the owner of the #330 pilot skids (DESIGN.md D-030 to
D-032). **This is an agent-prepared draft for a team session. It is not a HAZOP: no session
has been held, and an agent cannot hold one or accept anything in it.** Acceptance is by the
people in the session. This pack gives the owner what is needed to hold it: the roles to fill,
an agenda, the decisions to take first, and how to record what the team decides so that
`cheme safety hazop check` sees it.

| Study | Title | Sheet | Nodes | Scenarios | Worst band high | medium | low | Very-high initial | Actions | State |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| H-01 | Skid A: one-fill anolyte reservoir | P-01 | 8 | 72 | 29 | 33 | 10 | 1 | 47 | draft |
| H-02 | Skid B: KOH dosing, bleed and make-up | P-02 | 9 | 85 | 38 | 28 | 19 | 1 | 47 | draft |
| **All** | | | **17** | **157** | **67** | **61** | **29** | **2** | **94** | |

"Worst band" follows the matrix's action policy: the highest residual band of a scenario over its
categories, or the initial band where no residual is rated. No scenario is very-high after its
safeguards; two are very-high before them (section 3.3). Every high scenario has a proposed
action. Counted per rating instead (every category, initial and residual):

| Study | Initial very-high / high / medium / low | Residual high / medium / low |
|---|---|---|
| H-01 (89 ratings) | 1 / 57 / 26 / 5 | 32 / 44 / 13 |
| H-02 (107 ratings) | 1 / 62 / 29 / 15 | 42 / 39 / 26 |

Both studies are current against their analysed inputs (`cheme safety hazop stamp`: the P&ID,
the equipment, line and instrument lists, control/cause-effect.yaml, loops.yaml,
sequences.yaml, philosophy.md, layout/zones.yaml, the flowsheet, the design basis and the
duties), every band is current (`cheme safety hazop rate` exits 0), and each reports 0 errors and
0 warnings. They stay drafts because every entry is `status: proposed, by: agent` and the risk
matrix is proposed; no human review record covers them.

Several numbers here differ from what each drafting agent reported. The two studies were
drafted apart and then integrated (D-030): the hardware the skids share is now examined alike
and rated by one convention, and 13 scenarios were added so that each study covers what the
other found on the same hardware (section 3.4).

Reports to bring to the session (regenerate before it, `build/` is not committed):

```sh
cheme safety hazop report H-01   # build/hazop/H-01.md and .html; likewise H-02
```

## 1. Team roles

Roles only. The owner names the people and enters them in `team:` of each study (see section 4).
No one is named here.

| Role | What the role brings | Needed for |
|---|---|---|
| Facilitator (chair) | Runs the method (IEC 61882), keeps time, independent of the design team | all sessions |
| Scribe | Records the decisions in the study files during the session | all sessions |
| Process engineer | Electrolysis and anolyte chemistry, the duty model, the sizing basis (D-007 to D-015), the GDE pressure window (#332) | all sessions |
| Instrument and control engineer | Loops, trips I-101 to I-106 and I-201 to I-208, fail positions, the pH measurement and its offset | all sessions |
| Electrical engineer | The 48 V DC bus (not drawn), the rectifiers, reverse current, earthing, the Ex equipment | N2, N9 and the session 0 Ex decision |
| Mechanical / package engineer | The diaphragm compressors, the PSA and oxidiser packages (black boxes, D-012), the metering pump, relief | N4 to N7 |
| Operations / pilot plant operator | Fill, drain, the weekly T-202 refill, the hose work, maintenance and the stack lift (D-023) | all sessions |
| Process safety / HSE | Gas detection, area classification, CO, H2 and KOH exposure, the risk matrix, LOPA follow-up | all sessions |
| Vendor specialists, as needed | Stack (MEA), PSA, oxidiser, compressor and rectifier vendors | the nodes listed above |

## 2. Agenda

Estimated, as for asu-1, at 5 minutes per node plus 4 minutes per scenario: the worksheet is
pre-filled, so the team confirms, changes or deletes rows rather than brainstorming from blank.
Add time for any deviation the team adds. About 12 hours of worksheet in all, plus the opening
block of about 3 hours: plan five half-day sessions.

### Session 0: decisions first (about 3 hours)

| Item | Minutes |
|---|---:|
| Introduction: scope, the analysed inputs, the state of each study, what an agent draft is and is not | 15 |
| Risk matrix: accept, change or replace (section 3.1) | 40 |
| Credit and rating convention for both studies (section 3.2) | 40 |
| The two very-high initial scenarios and PV-x31's fail position (section 3.3) | 30 |
| Where the studies rate the same hazard differently, and why (section 3.4) | 15 |
| The owner decisions open from #330 (section 3.6) | 30 |
| How the high-residual actions will be handled (section 3.5); they are taken node by node | 10 |

### Sessions 1 to 4: node by node

H-02's nodes N2 to N6 and N9 are the same hardware as H-01's with 2xx tags. Take them after
H-01 and confirm only where Skid B differs; the estimate below does not count that saving.

| Study | Node | Title | Deviations | Scenarios | Minutes |
|---|---|---|---:|---:|---:|
| H-01 | H01-N1 | Anolyte loop: T-101, P-101, E-111, the stack anode side | 11 | 17 | 73 |
| H-01 | H01-N2 | Stacks E-101A to D, rectifier U-101, the 48 V bus | 6 | 8 | 37 |
| H-01 | H01-N3 | Cathode CO2 feed: FV-102, recycle CO2-102, humidification W-101 | 7 | 8 | 37 |
| H-01 | H01-N4 | Cathode gas outlet: CG-101, separator V-121, condensate, PV-121 | 7 | 11 | 49 |
| H-01 | H01-N5 | Gas conditioning: K-131, CG-103, PSA X-131, CO product, PV-131 | 9 | 8 | 37 |
| H-01 | H01-N6 | Tail gas and vents: oxidiser X-132, reservoir vent O2V-101 | 8 | 9 | 41 |
| H-01 | H01-N8 | Anolyte fill and end-of-campaign drain at T-101 | 6 | 6 | 29 |
| H-01 | H01-N9 | Enclosure: fan K-141, gas detection AIA-141 / AIA-142, zone Z-HAZ-A | 4 | 5 | 25 |
| H-01 | | **study total** | **58** | **72** | **328** |
| H-02 | H02-N1 | Anolyte loop: T-201, P-201, E-211, the stack anode side | 9 | 11 | 49 |
| H-02 | H02-N2 | Stacks E-201A to D, rectifier U-201, the 48 V bus | 8 | 8 | 37 |
| H-02 | H02-N3 | Cathode CO2 feed: FV-202, recycle CO2-202, humidification W-201 | 8 | 8 | 37 |
| H-02 | H02-N4 | Cathode gas outlet: CG-201, separator V-221, condensate, PV-221 | 6 | 10 | 45 |
| H-02 | H02-N5 | Gas conditioning: K-231, CG-203, PSA X-231, CO product, PV-231 | 7 | 8 | 37 |
| H-02 | H02-N6 | Tail gas and vents: oxidiser X-232, O2V-201, breather KV-202 | 9 | 12 | 53 |
| H-02 | H02-N7 | KOH dosing, bleed and make-up: T-202, P-202, BL-201 / FV-203, W-202 / LV-201 | 12 | 15 | 65 |
| H-02 | H02-N8 | Anolyte fill and end-of-campaign drain at T-201 | 8 | 8 | 37 |
| H-02 | H02-N9 | Enclosure: fan K-241, gas detection AIA-241 / AIA-242, zone Z-HAZ-B | 5 | 5 | 25 |
| H-02 | | **study total** | **72** | **85** | **385** |

A suggested split: session 0 the decisions (about 3 h); session 1 H01-N1 to N4 (about 3.3 h,
with the stack vendor); session 2 H01-N5 to N9 and H02-N1 (about 3.0 h, with the package
vendors); session 3 H02-N2 to N6 (about 3.5 h, shorter where H-01's decisions carry over);
session 4 H02-N7 to N9 (about 2.1 h, with operations for the dosing and the refill).

## 3. Decisions to take first

### 3.1 The risk matrix

`safety/risk-matrix.yaml` (co2-bpm-1-5x5-proposed) was drafted by an agent (ASSUMED) in the
structure of asu-1's matrix: five likelihood classes A to E of one order of magnitude each, five
severity grades per category (people, environment, asset with production loss) with money
values scaled one order below asu-1's for a pilot of two 20 ft skids, four bands, and the action
policy (high and very-high require an action; very-high is not accepted for start-up; medium
needs an ALARP statement). The team either:

- accepts it: `status: accepted` and `accepted_by: <who, and the procedure or session record>`;
- changes it (cells, grades, policy), then accepts it; every band is then looked up again
  (`rate --write`) and the ratings near a changed cell are re-read; or
- replaces it with the operating company's matrix, at its revision, and re-rates.

### 3.2 The credit and rating convention

Each study's `assessment_basis` holds the credit convention the residual ratings use (a
proposal, not a LOPA): a passive feature that removes the path, up to two orders; an alarm with
operator response, a check valve, a fail position, a written sequence step, or a trip of the
C&E whose SIL is not confirmed (every trip here, `sil: null`), one order each; nothing for a
safeguard that shares a transmitter, valve or logic with the cause or that the cause defeats,
nor for a relief device, since none is drawn on either P&ID. A regulatory loop is never a
safeguard, only its alarm with the operator's response.

When the two drafts were integrated (D-030), these rating rules were applied to both alike. The
team confirms or changes each; a change applies to both studies.

- **Initial likelihood is that of the cause**, as the matrix's notes say: a flange leak in the
  enclosure is D (a few times in the pilot's life), not lowered for the chance that a person is
  present. That is a conditional modifier for a LOPA, not for this matrix.
- **A utility upset is E**, the matrix's own example: the loss of instrument air, of cooling
  water at the battery limit, a CO2 supply run-out. A single instrument, valve or equipment
  failure is D.
- **A routine operating task is E**: the fill, the drain and their hose work (H01-S801, S803;
  H02-S802, S803). Work at the stack interval (the lift, opening the loop, the DC terminals) is
  D. H02-S712, the weekly 5 M KOH refill overfill, is rated 4/D on loss of sight; rated on the
  more frequent burn it would be 3/E, high either way.
- **A release of cathode gas, CO or CO2 into the enclosure is people severity 4** (a fatality),
  as the matrix names it, wherever it occurs: a seal blown by overpressure (H01-S305,
  H02-S303), the train opened with CO in it (H01-S409, H02-S408), the inventory left after a
  power loss (H01-S904, H02-S905), a head-space explosion of the reservoir after a gas
  breakthrough (H01-S403, H02-S605). A DC arc on the bus is severity 4 too (H01-S203, H02-S204).
- **An alarm that sees the damage only after it has happened is not credited for it**: the
  separator high level alarm LIC-x22 sees the anolyte only after the GDEs have flooded
  (H01-S105, S404; H02-S108, S403).
- **The gas trip takes one order** where it stops the source once the release is detected
  (I-x03 stops the current, closes FV-x02 and stops K-x31): H01-S401, S402, S409, S501, S502,
  S506; H02-S401, S402, S408, S410, S501, S502, S506. Where two detector trips act together
  they take one order as a pair. **I-x04 is not credited against the rectifier as an ignition
  source**: it trips the DC output, not the cabinet's own supply (H01-S207, H02-S206).
- **A switched-off rectifier is not an isolation**: the permissive `U-x01 off` of SEQ-x-DRAIN
  takes no credit for work at the DC terminals (H01-S205, H02-S208).

### 3.3 The very-high initial scenarios

Both are high after their safeguards, none very-high. They are the same hazard on the two
skids, and both rest on an open point of control/philosophy.md: PV-x31's proposed fail-closed
position on the loss of instrument air, with the positive-displacement compressor K-x31 still
running (it is electric) and no relief, no high-high pressure trip and no trip on low
instrument air drawn. The governing relief scenario of the K-x31 discharge is this blocked
outlet (named only; no sizing). The team decides PV-x31's fail position with the PSA vendor
first: the rating follows from it.

| Scenario | Cause (short) | Initial | Residual | Proposed actions | Owners |
|---|---|---|---|---|---|
| H01-S502 | PV-131 fails closed on loss of instrument air with K-131 and X-131 running | very-high | high | H01-A501 | process safety / HSE |
| H02-S501 | PV-231 closes (air loss, PIC-231 fault) or the CO receiver is closed while K-231 runs | very-high | high | H02-A501 | process safety / HSE |

### 3.4 Where the two studies rate the same hazard differently

After the integration every pair of scenarios on shared hardware has the same initial and
residual band, except these, where the design differs and the basis says why:

| Skid A | Skid B | Bands (residual) | Why they differ |
|---|---|---|---|
| H01-S308 | H02-S305 | medium / low | Back-flow into the supplies: on Skid A the humidification water W-101 path has no alarm and sets the rating; on the CO2 path alone both credit the FIC-x02 low flow alarm |
| H01-S503 | H02-S503 | high / medium | Back-flow from the PSA through the stopped K-x31: Skid A stops daily in D-A-ONOFF (likelihood D), Skid B does not run that duty (C) |
| H01-S802 | H02-S801 | medium / high | Wrong KOH delivered to the fill: SEQ-A-FILL S1 says "fresh 1 M KOH only", SEQ-B-FILL has no such step, and Skid B keeps 5 M KOH at the skid |
| H01-S117 | H02-S807 | medium / high | Opening the anolyte side: SEQ-A-DRAIN rinses the loop (S3), SEQ-B-DRAIN does not |
| H01-S403 | H02-S605 | high / high | Cathode above the anolyte, gas breakthrough: same band; Skid A's anolyte pressure drifts with the T-101 level (D), Skid B's level is held by LIC-201 (C) |
| H01-S607, S608 | H02-S606, S607 | low / low | O2 at the vent and a blocked vent: same band, the codes differ with the vent detail |

What the integration changed, for the team to check against the files:

- H-01, rated again: S105 and S404 (the LIC-122 alarm no longer credited for the flooding),
  S117 and S206 (stack-interval work D), S203 (a DC arc, people 4/C), S205 (no credit for
  `U-101 off`), S301 and S302 (a loss of CO2 is asset 2, recoverable, as on Skid B; S301 E),
  S305 (people 4, the PIC-121 alarm too slow, as H02-S303), S502 (an asset rating added).
- H-02, rated again: S105, S107, S403 (utility upsets E), S109 (the low-low level stops the
  pump, not the splash), S201 (D, the TIC-211 alarm credited), S205 (D), S206 (I-204 not
  credited), S306 (asset 3, the carbonate of all four stacks), S308, S401, S402, S408, S501,
  S502, S503, S506, S601, S603, S605, S801 to S803, S806, S901, S903 to S905 (the rules of
  section 3.2); S206, S402 and S502 also got a rating for the category H-01 rates (asset,
  people, asset).
- Added to H-01, mirroring H-02: S208 (uneven current share on the parallel bus), S410 (air
  drawn in under vacuum), S411 (K-131 stops with the current on), S507 (the PSA opened with
  adsorbed CO), S508 (K-131 cooling lost); actions H01-A112 (SIL screening, as H02-A104) and
  H01-A506; H01-A102, A401, A402, A503 extended.
- Added to H-02, mirroring H-01: S111 (E-211 plate leak), S409 (LIC-222 fails low), S410
  (PV-221 sticks closed), S508 (K-231 diaphragm), S610 (oxidiser relit on an accumulated
  mixture), S611 (hot flue), S612 (anolyte mist at O2V-201), S808 (T-201 under vacuum at the
  drain); safeguard H02-SG-N6-FG-HEIGHT; actions H02-A505 (gas trips isolate the PSA, as
  H01-A505) and H02-A506; H02-A602 and A603 extended. H-02's actions now carry owner roles, as
  H-01's do.

### 3.5 Every high-residual scenario and its proposed action

The action policy requires an action for each of these 67. The team takes them node by node in
sessions 1 to 4, and for each one either accepts the action (status `open`, with an owner and a
due date), changes it, or rejects it with a reason (`rejected`, `response`). Many share an action
(for example H01-A106 / H02-A706, the eyewash and shower; H01-A501 / H02-A501, the compressor
relief; H01-A103 / H02-A401, the pressure difference across the GDE), which can be decided once
for both skids. The owners are roles the drafting agents proposed; the owner assigns them.

| Scenario | Cause (short) | Initial | Residual | Proposed actions | Owners |
|---|---|---|---|---|---|
| H01-S105 | P-101 driven to full speed | high | high | H01-A103 | process engineer |
| H01-S110 | Leak from the anolyte loop | high | high | H01-A106 | process safety / HSE |
| H01-S115 | H2 crosses the bipolar membrane into the anolyte | high | high | H01-A110 | process safety / HSE |
| H01-S202 | The current is switched off (daily in D-A-ONOFF, a trip, a power loss) with CO and H2 still at the cathodes | high | high | H01-A201 | electrical engineer |
| H01-S203 | Short circuit across the stack terminals or the 48 V bus | high | high | H01-A202 | electrical engineer |
| H01-S205 | A stack's DC connections undone with the bus live, or with the stacks still charged after the current off | high | high | H01-A202 | electrical engineer |
| H01-S303 | W-101 lost at the battery limit, or HV-104 set too low or knocked | high | high | H01-A302 | process engineer |
| H01-S305 | The CO2 supply's pressure regulation at the battery limit fails open and FV-102 opens further | high | high | H01-A303 | process safety / HSE |
| H01-S307 | A leak of the CO2 feed CO2-101 or of the recycle CO2-102 into the enclosure | high | high | H01-A305 | process safety / HSE |
| H01-S402 | The PIC-121 pressure transmitter fails low | high | high | H01-A401, H01-A303 | instrument and control engineer; process safety / HSE |
| H01-S403 | The cathode back-pressure above the anolyte pressure at the stacks, which is not measured | high | high | H01-A103, H01-A110 | process engineer; process safety / HSE |
| H01-S404 | PV-121 goes to its fail-open position on loss of instrument air, or the PIC-121 transmitter fails high | high | high | H01-A402 | process engineer |
| H01-S406 | The LIC-122 level transmitter fails low | high | high | H01-A403 | instrument and control engineer |
| H01-S407 | LV-122 sticks open or the LIC-122 transmitter fails high | high | high | H01-A404 | process engineer |
| H01-S408 | More K+ crosses the bipolar membrane than assumed | high | high | H01-A302 | process engineer |
| H01-S501 | X-131 stops or closes its feed valves while K-131 keeps running | high | high | H01-A501 | process safety / HSE |
| H01-S502 | PV-131 goes to its proposed fail-closed position on loss of instrument air, with K-131 and X-131 running | very-high | high | H01-A501 | process safety / HSE |
| H01-S503 | K-131 stops with X-131 at pressure | high | high | H01-A502 | mechanical / package engineer |
| H01-S506 | A flange or fitting leak on CO-101, PV-131 or the product side of X-131 inside the enclosure | high | high | H01-A505, H01-A902 | instrument and control engineer; process safety / HSE |
| H01-S601 | X-132 flame-out, cold catalyst or ignition failure while X-131 sends tail gas | high | high | H01-A601 | mechanical / package engineer |
| H01-S602 | X-132 relit, or its catalyst recovers, with an H2-rich mixture accumulated in its chamber after a flame-out | high | high | H01-A602 | mechanical / package engineer |
| H01-S604 | AIR-101 lost or reduced | high | high | H01-A601 | mechanical / package engineer |
| H01-S606 | An H2-in-O2 mixture leaves O2V-101 and is ignited at the outlet | high | high | H01-A110, H01-A603 | process safety / HSE |
| H01-S801 | The operator does not stop the fill at the working level; LIA-101 has no high alarm | high | high | H01-A801, H01-A106 | instrument and control engineer; process safety / HSE |
| H01-S803 | A hose or coupling at KOH-101 or SP-101 fails, or is disconnected with liquid in it, during a transfer | high | high | H01-A106, H01-A803 | operations; process safety / HSE |
| H01-S805 | SEQ-A-DRAIN drains the whole reservoir to the site effluent; its acceptance is not stated | high | high | H01-A805 | process safety / HSE |
| H01-S901 | K-141 fails or trips after SEQ-A-START S1 started it, or is not started | high | high | H01-A901, H01-A112 | process safety / HSE |
| H01-S902 | A cathode gas or CO leak away from the single AIA-141, or AIA-141 failed | high | high | H01-A902 | process safety / HSE |
| H01-S904 | Loss of electric power | high | high | H01-A904 | process engineer |
| H02-S108 | FIC-201 transmitter fails reading low | high | high | H02-A401, H02-A101 | instrument and control engineer; process engineer |
| H02-S109 | Leak from the loop | high | high | H02-A706 | process safety / HSE |
| H02-S110 | H2 crosses the bipolar membrane into the anolyte and degasses into the T-201 head space | high | high | H02-A601, H02-A102 | instrument and control engineer; process safety / HSE |
| H02-S203 | U-201 is switched off (stop, trip, power loss) with H2 and CO still at the cathodes | high | high | H02-A201 | electrical engineer |
| H02-S204 | A short across the bus or the stack terminals in operation | high | high | H02-A202 | electrical engineer |
| H02-S208 | A stack is disconnected, or a terminal re-made, with U-201 only switched off and the stacks still charged | high | high | H02-A204 | electrical engineer |
| H02-S303 | The CO2 supply's pressure regulator at the battery limit fails open with FV-202 open | high | high | H02-A302 | process safety / HSE |
| H02-S306 | HV-204 set too low or closed by hand, W-201 supply lost, or the rotameter FI-203 misread | high | high | H02-A305 | process engineer |
| H02-S308 | A leak of CO2-201, FV-202 or its flanges, or of the supply hose at the frame, inside the skid enclosure | high | high | H02-A306 | process safety / HSE |
| H02-S402 | PIC-221 transmitter fails reading low | high | high | H02-A402, H02-A401 | instrument and control engineer; process engineer |
| H02-S403 | PV-221 fails open on loss of instrument air or PIC-221 reads high | high | high | H02-A401, H02-A403 | mechanical / package engineer; process engineer |
| H02-S409 | The LIC-222 level transmitter fails low | high | high | H02-A404 | instrument and control engineer |
| H02-S406 | LV-222 sticks open or LIC-222 fails reading high | high | high | H02-A405 | process engineer |
| H02-S407 | K+ crossing the bipolar membrane meets the CO2 at the cathode: K2CO3 / KHCO3 precipitate | high | high | H02-A406, H02-A401 | process engineer |
| H02-S501 | PV-231 closes (air loss, PIC-231 fault) or the CO receiver is closed while K-231 runs | very-high | high | H02-A501 | process safety / HSE |
| H02-S502 | The PSA package X-231 closes its outlets while K-231 runs | high | high | H02-A501, H02-A502 | mechanical / package engineer; process safety / HSE |
| H02-S506 | A leak at a flange of X-231, PV-231 or CO-201 (0.99 CO at 5 bar(a)) inside the enclosure | high | high | H02-A505, H02-A901 | instrument and control engineer; process safety / HSE |
| H02-S601 | X-232 loses its flame or its catalyst stops working while the PSA sends the tail gas | high | high | H02-A602 | mechanical / package engineer |
| H02-S610 | X-232 relit, or its catalyst recovers, with an H2-rich mixture accumulated in its chamber after a flame-out | high | high | H02-A602 | mechanical / package engineer |
| H02-S602 | The combustion air AIR-201 is lost at the battery limit | high | high | H02-A602 | mechanical / package engineer |
| H02-S604 | H2 crosses the bipolar membrane and leaves with the anode O2 through O2V-201 | high | high | H02-A601 | process safety / HSE |
| H02-S605 | The cathode is above the anolyte pressure and cathode gas breaks through into the anolyte | high | high | H02-A601, H02-A401 | process engineer; process safety / HSE |
| H02-S702 | The AIC-201 probe drifts high | high | high | H02-A701, H02-A702 | instrument and control engineer; process engineer |
| H02-S703 | The AIC-201 setpoint, alarm and trip set on the concentration basis while the probe reads activity pH | high | high | H02-A702 | process engineer |
| H02-S704 | The AIC-201 probe reads low | high | high | H02-A701 | instrument and control engineer |
| H02-S707 | KOH-204 is blocked while the positive-displacement metering pump P-202 strokes on | high | high | H02-A703, H02-A706 | mechanical / package engineer; process safety / HSE |
| H02-S709 | FV-203 sticks open or FIC-203 fails reading low | high | high | H02-A704, H02-A708 | process engineer; process safety / HSE |
| H02-S710 | LV-201 sticks open or LIC-201 fails reading low | high | high | H02-A705, H02-A706 | instrument and control engineer; process safety / HSE |
| H02-S712 | The weekly refill through KOH-202 / HV-205 from a drum or IBC pump is not stopped in time | high | high | H02-A707, H02-A706 | operations; process safety / HSE |
| H02-S714 | The P-202 diaphragm ruptures, or a fitting of KOH-203 / KOH-204 leaks at up to 4 bar(a) | high | high | H02-A706 | process safety / HSE |
| H02-S801 | The fill through KOH-201 delivers 5 M KOH or the 45-50 wt% merchant grade instead of 1 M | high | high | H02-A801 | operations |
| H02-S802 | The fill through HV-202 from a tanker or IBC pump is not stopped at the 50 L working volume | high | high | H02-A705, H02-A801 | instrument and control engineer; operations |
| H02-S803 | A hose coupling at KOH-201 or SP-201 is disconnected with liquid in it, or the hose fails | high | high | H02-A706, H02-A801 | operations; process safety / HSE |
| H02-S806 | SEQ-B-DRAIN sends the 50 L at pH 13.7 to the site effluent with no agreed acceptance | high | high | H02-A708 | process safety / HSE |
| H02-S807 | SEQ-B-DRAIN empties T-201 only: no drains or flushing of the stacks, pump and cooler | high | high | H02-A802, H02-A706 | process engineer; process safety / HSE |
| H02-S901 | A secondary-grade leak of cathode gas or tail gas at a flange inside the enclosure | high | high | H02-A901, H02-A104 | process safety / HSE |
| H02-S903 | K-241 stops during operation | high | high | H02-A903 | process safety / HSE |
| H02-S905 | Loss of electric power | high | high | H02-A905 | process engineer |

The causes are shortened here; the study files and the reports hold the full text, the
safeguards and the rating bases.

### 3.6 Owner decisions open from #330 that the studies depend on

- **Skid A's pH trip margin** (D-018): I-101 trips at pH 12.0, the threshold itself, with no
  margin; a trip at 12.2 needs the reservoir sized to it (about 1,176 L), which changes the
  frozen sizing basis (H01-S113, H01-A108). On Skid B I-201 trips at 12.2; its weakness is that
  it shares the AIC-201 probe with the dose trim (H02-S702, H02-A701).
- **The Ex rating** of the electrical items inside the zones (K-x41, P-x01, K-x31, P-202,
  instruments; ASSUMED Ex-rated today) with an area classification by a competent person
  (H01-A903, H01-A204; H02-A902, H02-A206).
- **The fail positions** proposed in control/philosophy.md, PV-x31 first (section 3.3), and
  PV-x21's fail-open, which lets the still running K-x31 pull a vacuum on the cathodes on the
  loss of instrument air (H01-S404, H02-S403; H01-A402, H02-A403).
- **The safe state on a loss of power** (F-POWER, open): a UPS for the gas detection, the fan and
  the alarms, and a purge or vent of the cathode gas train that works without power (H01-A904,
  H02-A905).
- **The enclosure and its ventilation** are ASSUMED and not sized; the fan has no running signal
  (H01-A901, H02-A903). Every gas-in-enclosure rating rests on them.
- **The CO2 supply interface** at the battery limit (pressure regulation, relief, cold gas), not
  drawn (H01-A303, A304; H02-A302, A304).
- **The site effluent** acceptance of the spent anolyte and Skid B's bleed (H01-A805, H02-A708).

### 3.7 Hazards judged not applicable, or only partly

The spec's list of hazards to examine is covered in both studies, except:

- **Skid B's dosing, bleed and make-up, the 5 M KOH, the breather KV-202, I-207 and I-208** do
  not exist on Skid A, which runs on one fill of 1 M KOH (H-01 has no node N7). 5 M KOH appears
  in H-01 only as a wrong delivery (H01-S802).
- **Overheating by an anolyte heater**: none is drawn on either skid and TIC-x11 can only cool;
  the low temperature side is studied (H01-S109, H02-S107).
- **CO2 vaporisation inside the skid**: the liquefied CO2 storage and vaporiser are beyond the
  battery limit (D-016); only cold gas or liquid at the tie-in is studied (H01-S306, H02-S304).
- **Hydrostatic head and the tank height at long campaigns** apply to Skid A only (H01-S106,
  H01-A104: 3.47 m and about 0.34 bar on the anode side at 10,000 h); Skid B's T-201 stays 50 L
  at any duration (D-010), recorded as a note on H02-N1-D6.
- **The on/off and part-load duties** run on Skid A's hardware only (D-013); they are a mode of
  H-01, not of H-02.
- **The anolyte refill at the end of the campaign** is Skid A's exchange; on Skid B the end of a
  campaign is SEQ-B-DRAIN and a fresh fill (H02-N8).
- **Back-flow through KOH-204** is not credible as drawn (the highest T-202 level, about 0.69 m,
  is below KOH-204's entry at the top of T-201, about 0.71 m); kept as a low scenario with an
  action to confirm (H02-S706, H02-A703).
- **Deviations with no credible cause** say so in their `notes`: H-01 anolyte reverse flow, CO
  product back-flow and the loss of the CO2-102 recycle (its consequence is H01-S301).

## 4. How to record acceptance in the files

Only the scribe edits, during or right after the session, and only what the team decided.

1. **Team.** In each study, fill `team:` with the people present and their roles, e.g.
   `- {name: <name>, role: facilitator}`, replacing the `to be named` entries. Replace the
   "Agent-prepared draft ... no session has been held" sentences in `notes:` (and the header
   comment) with the session dates and the record of attendance.
2. **Risk matrix.** In `safety/risk-matrix.yaml`, set `status: accepted` and
   `accepted_by: <who, and the procedure or session record>`, or replace the file with the
   company's matrix. Update the comment and `notes` that call it a proposal.
3. **Nodes, deviations, scenarios, safeguards and ratings.** For each entry the team accepts, set
   `status: accepted` and `by: <the team, or the person and session>`. Change the text or the
   codes first where the team changes them, and give the basis; delete an entry the team rejects
   (its id is never reused). A rating's `band:` is never edited by hand. Where a decision is
   taken for both skids (section 3.5), record it in both studies.
4. **Actions.** For each action the team keeps, set `status: open`, an `owner` (a person or a
   role the owner assigns) and `due: YYYY-MM-DD`; for one it rejects, `status: rejected` with the
   reason in `response`. An action is `closed` only later, with `response` saying how, by its
   owner. The plant changes (P&IDs, control, layout) follow the actions after the session,
   never before.
5. **Bands and check.** After the edits:
   ```sh
   cheme safety hazop rate H-01 --write      # likewise H-02
   cheme safety hazop check H-01             # likewise H-02: 0 errors; 'assessed' once all is accepted
   cheme validate
   ```
   A study is `assessed` when it is complete, current and every entry is accepted. If an analysed
   input changes before that, `check` reports `hazop-input-changed`: reassess the touched nodes,
   then `cheme safety hazop stamp <id> --write`.
6. **Human review.** A person who did not author the studies reviews them:
   ```sh
   cheme safety hazop review H-01 --write    # reviews/<date>-hazop-H-01.md, likewise H-02
   ```
   The reviewer fills in `reviewer` (their name) with `reviewer_kind: human` under
   `topic: hazop`, writes the findings and commits the record. With a current human review the
   studies become `reviewed`. The commented gates `hazop-basic` and `hazop-review` of
   `checks/checks.yaml` are then uncommented (safety/README.md).
7. **Reports.** `cheme safety hazop report <id>` regenerates `build/hazop/<id>.md` and `.html`
   for the minutes.

Nothing in this pack is an approval. An agent-written review record (`reviewer_kind: agent`)
does not count as the human review.
