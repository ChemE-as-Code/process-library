# HAZOP team session pack: co2-electrolysis-bpm-1, studies H-01 and H-02

Prepared by agents on 2026-11-05 for the owner of the #330 pilot skids (DESIGN.md D-030 to
D-032). **This is an agent-prepared draft for a team session. It is not a HAZOP: no session
has been held, and an agent cannot hold one or accept anything in it.** Acceptance is by the
people in the session. This pack gives the owner what is needed to hold it: the roles to fill,
an agenda, the decisions to take first, and how to record what the team decides so that
`cheme safety hazop check` sees it.

| Study | Title | Sheet | Nodes | Scenarios | Worst band high | medium | low | Very-high initial | Actions | State |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| H-01 | Skid A: one-fill anolyte reservoir | P-01 | 8 | 77 | 39 | 30 | 8 | 1 | 52 | draft |
| H-02 | Skid B: KOH dosing, bleed and make-up | P-02 | 9 | 92 | 50 | 28 | 14 | 1 | 55 | draft |
| **All** | | | **17** | **169** | **89** | **58** | **22** | **2** | **107** | |

"Worst band" follows the matrix's action policy: the highest residual band of a scenario over its
categories, or the initial band where no residual is rated. No scenario is very-high after its
safeguards; two are very-high before them (section 3.3). Every high scenario has a proposed
action. Counted per rating instead (every category, initial and residual):

| Study | Initial very-high / high / medium / low | Residual high / medium / low |
|---|---|---|
| H-01 (97 ratings) | 1 / 65 / 26 / 5 | 45 / 41 / 11 |
| H-02 (118 ratings) | 1 / 73 / 29 / 15 | 56 / 43 / 19 |

Both studies are current against their analysed inputs (`cheme safety hazop stamp`: the P&ID,
the equipment, line and instrument lists, control/cause-effect.yaml, loops.yaml,
sequences.yaml, philosophy.md, layout/zones.yaml, the flowsheet, the design basis and the
duties), every band is current (`cheme safety hazop rate` exits 0), and each reports 0 errors and
0 warnings. They stay drafts because every entry is `status: proposed, by: agent` and the risk
matrix is proposed; no human review record covers them.

Several numbers here differ from what each drafting agent reported. The two studies were
drafted apart and then integrated (D-030): the hardware the skids share is now examined alike
and rated by one convention, and 13 scenarios were added so that each study covers what the
other found on the same hardware (section 3.4). A review of the integrated drafts then found
plant-as-drawn hazards no scenario covered and residual ratings that broke the studies' own
credit rules; 12 scenarios were added and 32 re-rated or corrected (section 3.4, "What the
review changed").

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
Add time for any deviation the team adds. About 13 hours of worksheet in all, plus the opening
block of about 3 hours: plan five half-day sessions.

### Session 0: decisions first (about 3 hours)

| Item | Minutes |
|---|---:|
| Introduction: scope, the analysed inputs, the state of each study, what an agent draft is and is not | 15 |
| Risk matrix: accept, change or replace (section 3.1) | 40 |
| Credit and rating convention for both studies (section 3.2) | 40 |
| The two very-high initial scenarios and PV-x31's fail position (section 3.3) | 30 |
| Where the studies rate the same hazard differently, and why (section 3.4) | 15 |
| The owner decisions from #330, decided on 2026-11-06, to confirm (section 3.6) | 30 |
| How the high-residual actions will be handled (section 3.5); they are taken node by node | 10 |

### Sessions 1 to 4: node by node

H-02's nodes N2 to N6 and N9 are the same hardware as H-01's with 2xx tags. Take them after
H-01 and confirm only where Skid B differs; the estimate below does not count that saving.

| Study | Node | Title | Deviations | Scenarios | Minutes |
|---|---|---|---:|---:|---:|
| H-01 | H01-N1 | Anolyte loop: T-101, P-101, E-111, the stack anode side | 11 | 17 | 73 |
| H-01 | H01-N2 | Stacks E-101A to D, rectifier U-101, the 48 V bus | 6 | 8 | 37 |
| H-01 | H01-N3 | Cathode CO2 feed: FV-102, recycle CO2-102, humidification W-101 | 8 | 9 | 41 |
| H-01 | H01-N4 | Cathode gas outlet: CG-101, separator V-121, condensate, PV-121 | 7 | 11 | 49 |
| H-01 | H01-N5 | Gas conditioning: K-131, CG-103, PSA X-131, CO product, PV-131 | 10 | 10 | 45 |
| H-01 | H01-N6 | Tail gas and vents: oxidiser X-132, reservoir vent O2V-101 | 9 | 10 | 45 |
| H-01 | H01-N8 | Anolyte fill and end-of-campaign drain at T-101 | 6 | 6 | 29 |
| H-01 | H01-N9 | Enclosure: fan K-141, gas detection AIA-141 / AIA-142, zone Z-HAZ-A | 5 | 6 | 29 |
| H-01 | | **study total** | **62** | **77** | **348** |
| H-02 | H02-N1 | Anolyte loop: T-201, P-201, E-211, the stack anode side | 9 | 11 | 49 |
| H-02 | H02-N2 | Stacks E-201A to D, rectifier U-201, the 48 V bus | 8 | 8 | 37 |
| H-02 | H02-N3 | Cathode CO2 feed: FV-202, recycle CO2-202, humidification W-201 | 9 | 9 | 41 |
| H-02 | H02-N4 | Cathode gas outlet: CG-201, separator V-221, condensate, PV-221 | 6 | 10 | 45 |
| H-02 | H02-N5 | Gas conditioning: K-231, CG-203, PSA X-231, CO product, PV-231 | 10 | 10 | 45 |
| H-02 | H02-N6 | Tail gas and vents: oxidiser X-232, O2V-201, breather KV-202 | 10 | 13 | 57 |
| H-02 | H02-N7 | KOH dosing, bleed and make-up: T-202, P-202, BL-201 / FV-203, W-202 / LV-201 | 13 | 17 | 73 |
| H-02 | H02-N8 | Anolyte fill and end-of-campaign drain at T-201 | 8 | 8 | 37 |
| H-02 | H02-N9 | Enclosure: fan K-241, gas detection AIA-241 / AIA-242, zone Z-HAZ-B | 6 | 6 | 29 |
| H-02 | | **study total** | **79** | **92** | **413** |

A suggested split: session 0 the decisions (about 3 h); session 1 H01-N1 to N4 (about 3.3 h,
with the stack vendor); session 2 H01-N5 to N9 and H02-N1 (about 3.3 h, with the package
vendors); session 3 H02-N2 to N6 (about 3.8 h, shorter where H-01's decisions carry over);
session 4 H02-N7 to N9 (about 2.3 h, with operations for the dosing and the refill).

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
- **A safeguard that acts through the failed device is not credited**: the operator answers the
  TIC-x11 alarm through JIC-x01 and U-x01, and I-x05 trips the same U-x01, so neither counts
  against a fault of the current regulation (H01-S201, H02-S201) until the DC can be removed
  independently (H01-A205, H02-A207).
- **A trip that leaves the ignition source live is not credited against it**: I-x04 starts
  K-x41, leaves P-x01 and the oxidiser X-x32 running (H01-S903, S906; H02-S902, S906), as it
  is not credited against the rectifier.
- **Two trips on one final element count once**: I-102 and I-106 both act on U-101 through the
  same unscreened logic (H01-S111, as H01-S101 counts I-105 once).
- **A procedure that rests on the reading the cause falsifies is not credited**: the entry rule
  of SEQ-B-GAS against a detector that reads clear (H02-S904).
- **An alarm is credited only where the operator has the time and a written response**: the
  LIC-201 low alarm on the 50 L reservoir that empties in minutes is not (H02-S109); the
  TIC-111 alarm on the 1166 L T-101, which heats at about 1.7 K/h, is (H01-S107).

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

After the integration and the review every pair of scenarios on shared hardware has the same
initial and residual band, except these, where the design or the cause differs and the basis
says why:

| Skid A | Skid B | Bands (initial; residual) | Why they differ |
|---|---|---|---|
| H01-S503 | H02-S503 | high / high; high / medium | Back-flow from the PSA through the stopped K-x31: Skid A stops daily in D-A-ONOFF (likelihood D), Skid B does not run that duty (C) |
| H01-S802 | H02-S801 | high / high; medium / high | Wrong KOH delivered to the fill: SEQ-A-FILL S1 fills one tank with "fresh 1 M KOH only" (one letter); SEQ-B-FILL S1 has a written instruction too ("Fresh 1 M KOH in T-201, 5 M KOH in T-202") but fills both tanks with both strengths in the same step, with 5 M KOH kept at the skid, so it is not credited |
| H01-S806 | H02-S808 | medium / low; low / low | T-x01 under vacuum at the drain with the vent blocked: asset 3 for the 1166 L T-101, asset 2 for the 50 L T-201 |
| H01-S905 | H02-S904 | high / high; medium / high | After a gas trip: H01-S905's cause is a continuing leak the detectors see, so the entry rule of SEQ-A-GAS takes one letter; H02-S904's cause is a detector reading clear while CO remains, which defeats the entry rule. The two causes apply to both skids: the team may want each on both |
| H01-S607, S608 | H02-S606, S607 | medium / low; low / low | O2 at the vent and a blocked vent: the codes differ with the vent detail |

Same band, different codes, for the team to note: H01-S509 / H02-S509 (back-flow through the
recycle) and H01-S610 / H02-S613 (flashback along the tail gas) are D on Skid A for its daily
stops and C on Skid B, high on both.

H-02 also records, as H-01 does (H01-N5-D6), the CO product back-flow from the consumer as a
deviation without a scenario (H02-N5-D8): no check valve is drawn on CO-x01 and the consumer's
pressure is not stated, a question for the team.

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

What the review of the drafts changed (DESIGN.md D-030), for the team to check against the
files:

- **Added, on both skids** (H01 / H02): S309, the start-up purge of SEQ-x-START S2 with K-x31
  still stopped, which has no outlet and pressurises the cathodes at every start (actions
  H01-A307, H02-A307); S509, back-flow from X-x31 through the recycle CO2-x02, which has no
  valve and bypasses the check valve on CG-x03 (H01-A507, H02-A507); S510, a loss of the
  recycle that the FIC-x02 alarm does not see (H01-A301, H02-A301 extended); H01-S610 /
  H02-S613, flashback along the tail gas TG-x01 to the running oxidiser (H01-A605, H02-A604);
  S906, the oxidiser X-x32 as an ignition source the gas trips leave running (H01-A906,
  H02-A906).
- **Added to H-02 only**: S716, P-202 opened with no isolation from the full day tank, and
  S717, the AIC-201 probe calibrated with I-201 on the same probe (H02-A709, H02-A710); the CO
  product back-flow deviation H02-N5-D8; the W-201 back-flow path in S305; the gas-trip purge
  slug in S603; the trip with P-201 stopped in S605.
- **Re-rated, residual no longer crediting a safeguard the cause defeats or one final element
  twice**: H01-S111 (low to medium), S117 (medium to high), S201 (low to high, H01-A205), S903
  (medium to high); H02-S109 asset (low to medium), S201 (low to high, H02-A207), S709 asset
  (low to medium), S902 and S904 (medium to high).
- **Re-rated on the utility-upset rule (E)**: H01-S308 and H02-S305 (a CO2 run-out, both now
  high, with the W-x01 path), H01-S405 and H02-S405 (LV-x22 fails closed on air loss, both now
  high), H02-S708 and S711 (FV-203 and LV-201 on air loss, low to medium).
- **Re-rated otherwise**: H01-S603 and H02-S603 (the purge slug sets the rating: medium to
  high, with a people rating); H02-S605 (the trip case, D as H01-S403); H02-S804 (D as Skid A,
  with the environment category and action H02-A803); H01-S801 (the overfill path as drawn,
  with an asset rating).
- **Corrected text**: H01-S107 (about 1.7 K/h on the 1166 L, not 0.45 K/min); H01-S305 and
  H02-S303 (FIC-x02 closes FV-x02 on a higher supply pressure: the cathode reaches it only with
  FV-x02 already wide open, as at start-up, or a second failure); H01-S403 (the trip after
  I-102 or I-106); H01-S503 and H02-S503 (the check valve does not guard CO2-x02); H01-S607
  (no manway is drawn); H01-S905 (I-104 named); H02-S609 and S712 (the start-up fill of T-202
  in SEQ-B-FILL S1); H02-S705 and the safeguard H02-SG-N7-SEQ-STOP-P202 (SEQ-B-STOP S1 does
  not close FV-203); H02-S801 (SEQ-B-FILL S1 does have an instruction); the safeguard
  H01-SG-N2-DRAIN-PERM (SEQ-A-DRAIN drains the tank only).

### 3.5 Every high-residual scenario and its proposed action

The action policy requires an action for each of these 89. The team takes them node by node in
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
| H01-S117 | A stack's anolyte connections, the pump or the cooler undone with the loop not drained: SEQ-A-DRAIN empties T-101 only | high | high | H01-A106, H01-A111 | process safety / HSE; operations |
| H01-S201 | JIC-101 or the rectifier U-101's regulation fails high (the alarm response and I-105 both act through U-101) | high | high | H01-A205 | electrical engineer |
| H01-S202 | The current is switched off (daily in D-A-ONOFF, a trip, a power loss) with CO and H2 still at the cathodes | high | high | H01-A201 | electrical engineer |
| H01-S203 | Short circuit across the stack terminals or the 48 V bus | high | high | H01-A202 | electrical engineer |
| H01-S205 | A stack's DC connections undone with the bus live, or with the stacks still charged after the current off | high | high | H01-A202 | electrical engineer |
| H01-S303 | W-101 lost at the battery limit, or HV-104 set too low or knocked | high | high | H01-A302 | process engineer |
| H01-S305 | The CO2 supply's pressure regulation at the battery limit fails open while FV-102 stands wide open (the start-up purge, or a second failure in operation) | high | high | H01-A303 | process safety / HSE |
| H01-S307 | A leak of the CO2 feed CO2-101 or of the recycle CO2-102 into the enclosure | high | high | H01-A305 | process safety / HSE |
| H01-S308 | The CO2 supply runs empty or is isolated, or W-101 loses pressure, with FV-102 or HV-104 open (no check valves) | high | high | H01-A306 | process engineer |
| H01-S309 | SEQ-A-START S2 purges the cathodes with K-131 stopped: no outlet, the cathodes pressurised at every start | high | high | H01-A307 | process engineer |
| H01-S402 | The PIC-121 pressure transmitter fails low | high | high | H01-A401, H01-A303 | instrument and control engineer; process safety / HSE |
| H01-S403 | The cathode back-pressure above the anolyte pressure at the stacks, which is not measured (also after I-102 or I-106 with P-101 stopped) | high | high | H01-A103, H01-A110 | process engineer; process safety / HSE |
| H01-S404 | PV-121 goes to its fail-open position on loss of instrument air, or the PIC-121 transmitter fails high | high | high | H01-A402 | process engineer |
| H01-S405 | LV-122 closes on loss of instrument air, sticks closed, or CD-101 is blocked | high | high | H01-A403 | instrument and control engineer |
| H01-S406 | The LIC-122 level transmitter fails low | high | high | H01-A403 | instrument and control engineer |
| H01-S407 | LV-122 sticks open or the LIC-122 transmitter fails high | high | high | H01-A404 | process engineer |
| H01-S408 | More K+ crosses the bipolar membrane than assumed | high | high | H01-A302 | process engineer |
| H01-S501 | X-131 stops or closes its feed valves while K-131 keeps running | high | high | H01-A501 | process safety / HSE |
| H01-S502 | PV-131 goes to its proposed fail-closed position on loss of instrument air, with K-131 and X-131 running | very-high | high | H01-A501 | process safety / HSE |
| H01-S503 | K-131 stops with X-131 at pressure | high | high | H01-A502 | mechanical / package engineer |
| H01-S506 | A flange or fitting leak on CO-101, PV-131 or the product side of X-131 inside the enclosure | high | high | H01-A505, H01-A902 | instrument and control engineer; process safety / HSE |
| H01-S509 | K-131 stops, or a PSA fault, with X-131 at pressure: back-flow through the unguarded recycle CO2-102 | high | high | H01-A507 | process engineer |
| H01-S601 | X-132 flame-out, cold catalyst or ignition failure while X-131 sends tail gas | high | high | H01-A601 | mechanical / package engineer |
| H01-S602 | X-132 relit, or its catalyst recovers, with an H2-rich mixture accumulated in its chamber after a flame-out | high | high | H01-A602 | mechanical / package engineer |
| H01-S603 | H2-rich tail gas after a CO2 loss, or the SEQ-A-GAS S3 purge slug, to X-132 | high | high | H01-A601 | mechanical / package engineer |
| H01-S604 | AIR-101 lost or reduced | high | high | H01-A601 | mechanical / package engineer |
| H01-S606 | An H2-in-O2 mixture leaves O2V-101 and is ignited at the outlet | high | high | H01-A110, H01-A603 | process safety / HSE |
| H01-S610 | The tail gas flow falls away with X-132 still burning: flashback along TG-101 | high | high | H01-A605 | mechanical / package engineer |
| H01-S801 | The operator does not stop the fill at the working level; LIA-101 has no high alarm | high | high | H01-A801, H01-A106 | instrument and control engineer; process safety / HSE |
| H01-S803 | A hose or coupling at KOH-101 or SP-101 fails, or is disconnected with liquid in it, during a transfer | high | high | H01-A106, H01-A803 | process safety / HSE; operations |
| H01-S805 | SEQ-A-DRAIN drains the whole reservoir to the site effluent; its acceptance is not stated | high | high | H01-A805 | process safety / HSE |
| H01-S901 | K-141 fails or trips after SEQ-A-START S1 started it, or is not started | high | high | H01-A901, H01-A112 | process safety / HSE |
| H01-S902 | A cathode gas or CO leak away from the single AIA-141, or AIA-141 failed | high | high | H01-A902 | process safety / HSE |
| H01-S903 | An H2-rich release ignited by the motor of K-141, P-101 or K-131 (I-104 starts K-141, leaves P-101 running) | high | high | H01-A903 | owner / electrical engineer |
| H01-S904 | Loss of electric power | high | high | H01-A904 | process engineer |
| H01-S906 | An H2-rich release reaches the running oxidiser X-132, which the gas trips do not stop | high | high | H01-A906, H01-A204 | process safety / HSE |
| H02-S108 | FIC-201 transmitter fails reading low | high | high | H02-A401, H02-A101 | process engineer; instrument and control engineer |
| H02-S109 | Leak from the loop | high | high | H02-A706 | process safety / HSE |
| H02-S110 | H2 crosses the bipolar membrane into the anolyte and degasses into the T-201 head space | high | high | H02-A601, H02-A102 | process safety / HSE; instrument and control engineer |
| H02-S201 | JIC-201 or the rectifier U-201's regulation fails high (the alarm response and I-205 both act through U-201) | high | high | H02-A207 | electrical engineer |
| H02-S203 | U-201 is switched off (stop, trip, power loss) with H2 and CO still at the cathodes | high | high | H02-A201 | electrical engineer |
| H02-S204 | A short across the bus or the stack terminals in operation | high | high | H02-A202 | electrical engineer |
| H02-S208 | A stack is disconnected, or a terminal re-made, with U-201 only switched off and the stacks still charged | high | high | H02-A204 | electrical engineer |
| H02-S303 | The CO2 supply's pressure regulator at the battery limit fails open with FV-202 open | high | high | H02-A302 | process safety / HSE |
| H02-S305 | The CO2 supply runs out or is isolated, or W-201 loses pressure, with FV-202 or HV-204 open (no check valves) | high | high | H02-A303 | process engineer |
| H02-S306 | HV-204 set too low or closed by hand, W-201 supply lost, or the rotameter FI-203 misread | high | high | H02-A305 | process engineer |
| H02-S308 | A leak of CO2-201, FV-202 or its flanges, or of the supply hose at the frame, inside the skid enclosure | high | high | H02-A306 | process safety / HSE |
| H02-S309 | SEQ-B-START S2 purges the cathodes with K-231 stopped: no outlet, the cathodes pressurised at every start | high | high | H02-A307 | process engineer |
| H02-S402 | PIC-221 transmitter fails reading low | high | high | H02-A402, H02-A401 | instrument and control engineer; process engineer |
| H02-S403 | PV-221 fails open on loss of instrument air or PIC-221 reads high | high | high | H02-A401, H02-A403 | process engineer; mechanical / package engineer |
| H02-S405 | LV-222 closes on loss of instrument air, sticks, or CD-201 is blocked | high | high | H02-A404 | instrument and control engineer |
| H02-S409 | The LIC-222 level transmitter fails low | high | high | H02-A404 | instrument and control engineer |
| H02-S406 | LV-222 sticks open or LIC-222 fails reading high | high | high | H02-A405 | process engineer |
| H02-S407 | K+ crossing the bipolar membrane meets the CO2 at the cathode: K2CO3 / KHCO3 precipitate | high | high | H02-A406, H02-A401 | process engineer |
| H02-S501 | PV-231 closes (air loss, PIC-231 fault) or the CO receiver is closed while K-231 runs | very-high | high | H02-A501 | process safety / HSE |
| H02-S502 | The PSA package X-231 closes its outlets while K-231 runs | high | high | H02-A501, H02-A502 | process safety / HSE; mechanical / package engineer |
| H02-S506 | A leak at a flange of X-231, PV-231 or CO-201 (0.99 CO at 5 bar(a)) inside the enclosure | high | high | H02-A505, H02-A901 | instrument and control engineer; process safety / HSE |
| H02-S509 | K-231 stops, or a PSA fault, with X-231 at pressure: back-flow through the unguarded recycle CO2-202 | high | high | H02-A507 | process engineer |
| H02-S601 | X-232 loses its flame or its catalyst stops working while the PSA sends the tail gas | high | high | H02-A602 | mechanical / package engineer |
| H02-S610 | X-232 relit, or its catalyst recovers, with an H2-rich mixture accumulated in its chamber after a flame-out | high | high | H02-A602 | mechanical / package engineer |
| H02-S602 | The combustion air AIR-201 is lost at the battery limit | high | high | H02-A602 | mechanical / package engineer |
| H02-S603 | H2-rich tail gas after a CO2 loss, product CO to the tail, or the SEQ-B-GAS S3 purge slug, to X-232 | high | high | H02-A602 | mechanical / package engineer |
| H02-S604 | H2 crosses the bipolar membrane and leaves with the anode O2 through O2V-201 | high | high | H02-A601 | process safety / HSE |
| H02-S605 | The cathode above the anolyte (K-231 stopped, PV-221 closed, or a trip that stops P-201 with the purge held at 1.1 bar(a)) | high | high | H02-A601, H02-A401, H02-A604 | process safety / HSE; process engineer; mechanical / package engineer |
| H02-S613 | The tail gas flow falls away with X-232 still burning: flashback along TG-201 | high | high | H02-A604 | mechanical / package engineer |
| H02-S702 | The AIC-201 probe drifts high | high | high | H02-A701, H02-A702 | instrument and control engineer; process engineer |
| H02-S703 | The AIC-201 setpoint, alarm and trip set on the concentration basis while the probe reads activity pH | high | high | H02-A702 | process engineer |
| H02-S704 | The AIC-201 probe reads low | high | high | H02-A701 | instrument and control engineer |
| H02-S707 | KOH-204 is blocked while the positive-displacement metering pump P-202 strokes on | high | high | H02-A703, H02-A706 | mechanical / package engineer; process safety / HSE |
| H02-S709 | FV-203 sticks open or FIC-203 fails reading low | high | high | H02-A704, H02-A708 | process engineer; process safety / HSE |
| H02-S710 | LV-201 sticks open or LIC-201 fails reading low | high | high | H02-A705, H02-A706 | instrument and control engineer; process safety / HSE |
| H02-S712 | The weekly refill through KOH-202 / HV-205 from a drum or IBC pump is not stopped in time | high | high | H02-A707, H02-A706 | operations; process safety / HSE |
| H02-S714 | The P-202 diaphragm ruptures, or a fitting of KOH-203 / KOH-204 leaks at up to 4 bar(a) | high | high | H02-A706 | process safety / HSE |
| H02-S716 | P-202 or KOH-203 opened with no isolation from the 84.5 L of 5 M KOH in T-202 | high | high | H02-A709, H02-A706 | mechanical / package engineer; process safety / HSE |
| H02-S717 | The AIC-201 probe pulled or calibrated with the current on: the dose trim and I-201 lost together | high | high | H02-A710, H02-A701 | instrument and control engineer |
| H02-S801 | The fill through KOH-201 delivers 5 M KOH or the 45-50 wt% merchant grade instead of 1 M | high | high | H02-A801 | operations |
| H02-S802 | The fill through HV-202 from a tanker or IBC pump is not stopped at the 50 L working volume | high | high | H02-A705, H02-A801 | instrument and control engineer; operations |
| H02-S803 | A hose coupling at KOH-201 or SP-201 is disconnected with liquid in it, or the hose fails | high | high | H02-A706, H02-A801 | process safety / HSE; operations |
| H02-S806 | SEQ-B-DRAIN sends the 50 L at pH 13.7 to the site effluent with no agreed acceptance | high | high | H02-A708 | process safety / HSE |
| H02-S807 | SEQ-B-DRAIN empties T-201 only: no drains or flushing of the stacks, pump and cooler | high | high | H02-A802, H02-A706 | process engineer; process safety / HSE |
| H02-S901 | A secondary-grade leak of cathode gas or tail gas at a flange inside the enclosure | high | high | H02-A901, H02-A104 | process safety / HSE |
| H02-S902 | An H2-rich leak ignited by a motor in the zone that I-204 starts or leaves running | high | high | H02-A902, H02-A901 | owner / electrical engineer; process safety / HSE |
| H02-S903 | K-241 stops during operation | high | high | H02-A903 | process safety / HSE |
| H02-S904 | Entry after a gas trip when the single detector reads clear but CO remains at the leak | high | high | H02-A904 | operations |
| H02-S905 | Loss of electric power | high | high | H02-A905 | process engineer |
| H02-S906 | An H2-rich release reaches the running oxidiser X-232, which the gas trips do not stop | high | high | H02-A906, H02-A206 | process safety / HSE |

The causes are shortened here; the study files and the reports hold the full text, the
safeguards and the rating bases.

### 3.6 Owner decisions from #330 that the studies depend on (decided 2026-11-06)

The owner delegated these decisions on 2026-11-06 ("make reasonable decisions and move on");
they are recorded in DESIGN.md D-050 to D-058. Every one of them is **decided by the owner on
2026-11-06, to be confirmed by the team**: the studies were revised by an agent on 2026-11-06 to
the plant as now drawn, every revised or added entry `status: proposed`, `by: agent`, and both
studies re-stamped against the changed inputs. The team re-assesses the revised entries in the
session. The revision moved these residual bands (worst category), all proposals:

| Study | Scenario | Residual | Why (decision) |
|---|---|---|---|
| H-01 / H-02 | H01-S117; H02-S807 | high -> medium | the new SEQ-x-DRAIN drains and flushes the loop (D-055) |
| H-01 / H-02 | H01-S207, H02-S206 | medium -> low | the rectifier on a plinth off the frame, AC isolated on gas detection (D-051, D-057) |
| H-01 / H-02 | H01-S601, S602; H02-S601, S610 | high -> medium | the burner management trip I-x10 closes XV-x33 (D-054) |
| H-01 / H-02 | H01-S610; H02-S613 | high -> medium / low | the detonation arrester, the check valve and the trip valve on TG-x01 (D-054) |
| H-01 / H-02 | H01-S901, S904; H02-S901, S905 | high -> medium | the open, naturally ventilated skid (D-050) |
| H-01 / H-02 | H01-S903; H02-S902 | high -> low | the Ex marking in the zone and the open skid (D-050, D-051) |
| H-01 / H-02 | H01-S906; H02-S906 | high -> low | the oxidiser outside the zone in open air (D-047, D-057) |
| H-01 / H-02 | H01-S611; H02-S614 (new) | medium | a flame held on the arrester, I-x09 (D-054) |
| H-02 | H02-S809 (new) | high | the pump-out of T-202's 5 M KOH heel (D-055), action H02-A706 |

H-01 now has 78 scenarios (worst residual 31 high, 36 medium, 11 low) and 54 actions; H-02 94
scenarios (43 high, 33 medium, 18 low) and 57 actions. The tables of sections 3.1 to 3.5 are
those of the 2026-11-05 drafts; where a scenario above moved, the study file holds the current
rating.

- **Skid A's pH trip margin** (D-018): **decided by the owner on 2026-11-06** (DESIGN.md D-058):
  I-101 trips at pH 12.2, 0.2 above the criterion pH 12, and T-101 is sized to reach the trip
  value at H (1,176 L written, D 1.077 x H 1.615 m); pH 12 stays the reported stability
  criterion and the frozen expectations stand with erratum X-2 (H01-S113, H01-A108, revised as
  proposals). Still open: the margin against the probe's uncertainty once AI-101 is calibrated
  (H01-A109) and the SIL screening (H01-A112). On Skid B I-201 trips at 12.2; its weakness is
  that it shares the AIC-201 probe with the dose trim (H02-S702, H02-A701).
- **The Ex rating** of the electrical items inside the zones: **decided by the owner on
  2026-11-06** (DESIGN.md D-051): motors (P-x01, K-x31, P-202) II 2G Ex db eb IIC T3 Gb,
  instruments Ex ia IIC T4 Ga with barriers outside the zone, certified IIC gas detectors, 3G/Gc
  the stated minimum, the rectifier's AC isolated at SDB-1 on gas detection and the DC never
  broken under load inside the zone. Still open, for a competent person: the area
  classification, the explosion protection document and the inspection (H01-A903, H01-A204;
  H02-A902, H02-A206). The study entries are revised as proposals for the team (H01-S903,
  H02-S902 and the actions above).
- **The fail positions** proposed in control/philosophy.md, PV-x31 first (section 3.3), and
  PV-x21's fail-open, which lets the still running K-x31 pull a vacuum on the cathodes on the
  loss of instrument air (H01-S404, H02-S403; H01-A402, H02-A403).
- **The safe state on a loss of power** (F-POWER, open): a UPS for the gas detection and the
  alarms (no fan since D-050), and a purge or vent of the cathode gas train that works without power (H01-A904,
  H02-A905).
- **The enclosure and its ventilation**: **decided by the owner on 2026-11-06** (DESIGN.md
  D-050): the skids are open and naturally ventilated, with no enclosure and no extract fan
  (K-x41 deleted); at most a rain canopy over the rectifier and the junction boxes; the CO and
  H2 detectors stay, with personal CO monitors and a CO2 check at grade and the low points
  (H01-A901, H01-A902, H02-A903). Node N9 of both studies is rewritten for the open skid and
  every gas-in-enclosure cause and rating revised ("at the open skid", the fan's credits
  removed), as proposals for the team.
- **The CO2 supply interface** at the battery limit (pressure regulation, relief, cold gas), not
  drawn (H01-A303, A304; H02-A302, A304).
- **The site effluent** acceptance of the spent anolyte and Skid B's bleed (H01-A805, H02-A708).
- **The oxidiser X-x32 inside the enclosure and zone**: stopped with its tail gas by the gas
  trips, or moved outside (H01-A906, H02-A906); a flame cannot be Ex-rated. The oxidiser stands
  outside the zone since D-047, and the tail gas's protection is **decided by the owner on
  2026-11-06** (DESIGN.md D-054, P&ID revision B): an in-line detonation arrester FA-x33 for
  unstable detonation (EN ISO 16852, IIC, protected side towards X-x31), a check valve and the
  fail-closed trip valve XV-x33 at X-x31's outlet inside the zone, the arrester's temperature
  TSHH-x33 tripping XV-x33 (I-x09), the gas trips and the oxidiser's burner management trip
  (I-x10) closing it, TG-x01 all-welded to the burner; the vendor's burner arrester and burner
  management the second barrier (H01-A605, H01-A907, H02-A604, H02-A907; H01-S610, H02-S613).
  Still open: the arrester's type examination for the actual tail gas and its burning time
  (vendor). The entries are revised as proposals for the team (H01-S601, S602, S610 and the
  new S611; H02-S601, S610, S613 and the new S614).
- **The ignition sources' places** (layout review 2026-11-05-layout-r2 #1, #3): **decided by the
  owner on 2026-11-06** (DESIGN.md D-057): the rectifier U-x01 leaves the frame for a plinth at
  grade north-east of it (3.23 m from the nearest zone source with its flanges, against the
  1.5 m of the screening rule), the oxidiser X-x32 moves south-east, 2 m or more from the east
  step's foot, and TG-x01 runs about 12 m at 0.30 m on sleeper posts to its east face. The zones
  do not change; H01-S207 / H02-S206 (the rectifier) and H01-S906 / H02-S906 (the oxidiser)
  are re-rated as proposals for the team.
- **Draining the anolyte loop and the tanks**: **decided by the owner on 2026-11-06** (DESIGN.md
  D-055, P&ID revision B): a capped low-point drain DR-x01 on the supply header, a capped vent
  AV-x11 on the cooler, a capped camlock pump-out on T-101, T-201 and T-202, and SEQ-x-DRAIN
  venting, draining, pumping out the heel and flushing (H01-A111, H01-A206, H02-A208, H02-A802;
  H01-S117, S804, H02-S807 revised and H02-S809 added as proposals).
- **The cell temperature on the open skid**: **decided by the owner on 2026-11-06** (DESIGN.md
  D-052, D-056): the cooler on a tempered-water unit off the skid that also heats, with a
  low-temperature alarm on TIC-x11 and frost protection when idle (H01-A105, H02-A103). The
  studies now name TWS-x01 and TWR-x01 (H01-S107, S109, S116; H02-S105, S107, S111, revised as
  proposals).
- **The DC isolation independent of the rectifier**, which every trip and the current-runaway
  scenario rest on (H01-A205, H02-A207). Decided in principle by the owner (D-051): a lockable
  isolator or DC contactor outside the zone; its design and drawing stay open with the DC bus.

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
- **Deviations with no credible cause** say so in their `notes`: the anolyte reverse flow on
  Skid A (H01-N1-D4) and the CO product back-flow on both skids (H01-N5-D6, H02-N5-D8), which
  waits for the consumer's pressure. The loss of the recycle CO2-x02, recorded without a cause
  in the first draft, is now H01-S510 and H02-S510.

## 4. How to record acceptance in the files

Only the scribe edits, during or right after the session, and only what the team decided.

1. **Team.** In each study, fill `team:` with the people present and their roles, e.g.
   `- {name: <name>, role: facilitator}`, replacing the `to be named` entries. Replace the
   "Agent-prepared draft ... no session has been held" sentences in `notes:` (and the header
   comment) with the session dates and the record of attendance. Keep the header comment the
   same number of lines, or regenerate the 10,000 h record afterwards (step 5): its
   `hazop-input-changed` warnings carry the line numbers of the `analysed:` block.
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
   then `cheme safety hazop stamp <id> --write`. The 10,000 h scenario record
   (`results/scenarios/10000h/record.json`) lists the studies' `hazop-input-changed` warnings in
   that scenario's copy with their file, line and recorded revision, so after a re-stamp, or an
   edit that moves the `analysed:` block, regenerate it and commit it with the studies, or the
   gate `skid-regen-current` fails on a file the scribe did not touch:
   ```sh
   cheme run scripts/regen.py --duration 10000 --uncertainty --scratch /tmp/s10000   # the record
   cheme run scripts/regen.py --check                                                # exit 0
   ```
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
