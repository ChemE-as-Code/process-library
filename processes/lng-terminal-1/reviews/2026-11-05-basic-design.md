---
topic: design
reviewed_commit: 7bcea968525c658cc9f53edf9a20b3c493d46273
scope: [pid/P-01.xml, pid/P-02.xml, pid/P-03.xml, pid/P-04.xml, pid/P-05.xml, pid/P-06.xml, pid/P-07.xml, pid/P-08.xml, equipment/equipment-list.yaml, piping/line-list.yaml, piping/special-items.yaml, control/instrument-list.yaml, control/cause-effect.yaml, control/loops.yaml, control/sequences.yaml, DESIGN.md]
basis:
  - {path: process/flowsheet.yaml, revision: 7bcea968525c658cc9f53edf9a20b3c493d46273, relation: depends-on}
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: design (basic stage P&IDs P-01 to P-08, lists, C&E, loops, sequences)

## Summary

An independent engineering review of the eight basic-stage P&IDs of the LNG export terminal and
the lists and control files that go with them, at commit `7bcea968` on
`stage/lng-terminal-1-concept`. The sheets are drawn cleanly. All eight have zero drawing
findings, and the main protection layers are on the sheets. Tanks: independent LZT/PZT trips,
pressure control to the compressors and then to the flare, PSVs to atmosphere, vacuum valves and
make-up gas. In-tank pumps: minimum-flow returns and low-low level trips. Berths: shore ESD
valves, ERS per arm, the ship-shore link and a slow-closure surge philosophy. BOG compressors:
suction drum with a high-high trip, desuperheater, anti-surge per machine and discharge relief.

The set is **not ready for basic-engineering issue**. The most serious problem is on the berth
sheets: the drain line DR-5001 / DR-6001 connects the liquid header to the jetty drain drum with
no valve. As drawn, the header is permanently open to the drum, and through the drum's unvalved
vent to the vapour return. Eight high findings follow:
- several blockable cryogenic sections have no thermal relief, contrary to D-017;
- the hybrid arm has no liquid/vapour interlock;
- ESD-2 closes the ERS valves without stopping the pumps;
- nothing protects the rundown when no tank can take it;
- the drain pumps have no check valve;
- the anti-surge recycle is uncooled.

Merge pending: the critical and high findings must be closed before the stage is signed off.

## Branch diff (`cheme diff main --list`)

Every sheet is new on the branch (no sheet existed on `main`):

```
pid/P-01.xml: (sheet added)   95 plant-item lines (e.g. added SwingCheckValve CV1111 ... PSV1121, PV1110, PV1111, XV-1102/1103/1106-1109/1111-1114)
pid/P-02.xml: (sheet added)   81
pid/P-03.xml: (sheet added)   81
pid/P-04.xml: (sheet added)   81
pid/P-05.xml: (sheet added)   99
pid/P-06.xml: (sheet added)   99
pid/P-07.xml: (sheet added)   81
pid/P-08.xml: (sheet added)   60
process/BFD.xml: (sheet added) 51
process/PFD.xml: (sheet added) 55
```

(each line "added <class> <id> [tag]: n added, 0 removed, 0 modified"; 793 lines in all). The
branch's commits (`git log --oneline -8`): `7bcea968` streams linked to P&ID lines, `d9ba0815`
LCI, `f449a644` datasheets / surge / vapour arm, `b7643cbb` control loops, sequences, philosophy,
`2402922f` basic P&IDs P-01 to P-08, `e0c3b730` concept stage. Each has a reason in its commit
message.

The working tree held uncommitted edits by a concurrent agent to P-02 to P-06. These change only
the off-page connector texts (e.g. "to LNG-4001 (P-04)" becomes "to trestle line A (P-04)"). The
renders below are of the working tree. The engineering content is the same as at `7bcea968`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-design#1 | P-05, P-06 | DR-5001 / DR-6001, D-5101 / D-6101, BOG-5002 / BOG-6002 | The DN 100 drain from the liquid header LNG-5001 (tee T50D) to D-5101 has no valve (`cheme show DR-5001`: pipe, tee T50P, pipe, nozzle). D-5101's vent BOG-5002 also has no valve and ties into BOG-5001. While loading, the header (up to ~9 barg) therefore flows continuously into the drum and then into the vapour return, the tank vapour header and D-7101. PSV-5131 discharges to the same place the header is already open to, so it protects nothing. | critical | open | Put a block valve (fail-closed XV or locked-closed manual pair) on DR-5001 segment S1, between the header tee and the PSV-5131 outlet tee T50P, so that the relief outlet stays open to the drum. Do the same on DR-6001 (P-06). Add the drain step's valve to SEQ-LOAD S6. |
| 2026-11-05-basic-design#2 | P-05, P-06 | P-5101 / P-6101, LNG-5005/5006, LNG-6005/6006 | The jetty drain pumps have no discharge check valve, no suction or discharge isolation and no minimum-flow return. They discharge into the platform crossover LNG-4003, which carries circulation or loading pressure. A stopped pump lets LNG flow back into D-5101/D-6101, which then overflows into the vapour return through BOG-5002. | high | open | Add a check valve and an isolation valve on each discharge, an isolation valve on each suction (with a drain/vent between them), and a minimum-flow return to the drum. |
| 2026-11-05-basic-design#3 | P-05, P-06 | LA-5103 / LA-6103, XV-5123 / XV-5125, XV-6123 / XV-6125 | The hybrid arm's liquid isolation XV-5123 and vapour isolation XV-5125 are both operator HS valves with no interlock. Opening both connects the liquid header (pump shut-off ~9 barg) to the vapour arm LA-5102 (design 3.5 barg), D-7101 (3.5 barg) and the tank vapour space (0.29 barg). SEQ-LOAD S4 opens XV-5123 with no permissive on XV-5125. | high | open | Add position switches to both valves and a permissive interlock (only one of the two may be open) in control/cause-effect.yaml, plus a mechanical interlock or spectacle blind. Add "XV-5125 closed" to the SEQ-LOAD S4 permissives. |
| 2026-11-05-basic-design#4 | P-05, P-06 | I-503 / I-603, XV-5131..5144, ZS-5151..5154 | ESD-2 closes XV-5101 and all eight ERS ball valves but does not stop the loading pumps and does not initiate ESD-1 (I-501). Its notes say "after ESD-1", but the logic does not enforce it. ERS valves close in seconds, and the D-023 surge estimate covers only XV-5101 at 25 s. The instrument list has the ZS-515x stage-1 ESD-1, but ZS-515x is not a cause of I-501. All XVs fail closed on instrument-air failure, which is a further fast-closure case with the pumps running. | high | open | Make I-503/I-603 trip I-501/I-601 first (pumps stopped, XV-5101 closing) and then close the ERS valves after a set delay. Add the ZS stage-1 signals to the I-501 logic. State the ERS closure time and include ERS closure and instrument-air failure in the surge analysis (D-023). |
| 2026-11-05-basic-design#5 | P-01 | LNG-1002 / LNG-1004, LNG-1001 (T-3101 part) / LNG-1003; XV-1102, XV-1103, XV-1106..1109 | Blocked-in DN 900 LNG sections with no thermal relief. One runs from XV-1102 to XV-1106/XV-1107, the other from XV-1103 to XV-1108/XV-1109. The XV fails closed and is closed by I-201/I-203, while the selection valves fail in their last position. PSV-1121 sits upstream of both XVs. This contradicts D-017 ("thermal relief valves on every blocked-in cryogenic section"). | high | open | Add a thermal relief valve to the BOG header on each fill branch downstream of XV-1102 and XV-1103, and list them in piping/special-items.yaml. |
| 2026-11-05-basic-design#6 | P-02, P-03, P-04 | LNG-2001 / LNG-3001, LNG-4001/4002 upstream of XV-4101/4102, LNG-4006, LNG-2002/3002, LNG-4005/4009 | The tank-end loading headers are blockable with no thermal relief: from the pump-column check valves to XV-4101/XV-4102 (closed by ESD-1, fail closed), XV-4106, XV-4105 and XV-2123/XV-3123. The circulation header LNG-2002 behind its check valve and the circulation return LNG-4005/4009 (between XV-4105 and XV-2123/XV-3123) are blockable too. PI-2117 is the only item on the header. | high | open | Add thermal relief valves (to the tank or the BOG header) on each blockable section: the pump header of each tank, the crossover, and the circulation return between XV-4105 and the tank valves. List them in special-items. |
| 2026-11-05-basic-design#7 | P-05, P-06 | LA-5101/5103/5104 (LA-6101/6103/6104): XV-5121/5124/5123 to XV-5131/5134/5133; hybrid riser XV-5123/XV-5125/XV-5133 | Each liquid arm (16 inch, ~35 m) is trapped between its fail-closed arm isolation valve and its fail-closed inboard ERS valve. That happens on instrument-air failure, and whenever the arm is isolated full of LNG after ESD-2. No thermal relief is drawn. The hybrid riser can be blocked between three valves. | high | open | Add a thermal relief valve per arm section (to D-5101 or the vapour line), or show it as part of the arm package with a note and list it. Confirm cavity relief of the ERS ball valves with the vendor. |
| 2026-11-05-basic-design#8 | P-01 | I-101, I-201/I-203/I-301/I-303; XV-1102, XV-1103, XV-1111..1114 | Nothing protects the rundown when no tank can take it. I-101 closes the battery-limit valves only when both tanks are at LAHH. I-201/I-203 (I-301/I-303) close one fill valve each, and XV-1102/XV-1103 both fail closed on instrument-air failure. With one tank tripped and the other's fill closed (or Phase 1 with one tank), the rundown header is dead-headed against four trains. Its only relief is the DN 25 thermal valve PSV-1121. | high | open | Add an interlock: both XV-1102 and XV-1103 closed (position switches), or both tanks LAHH / PAHH, closes XV-1111..1114 and sends a trip to the trains. Record in DESIGN.md how the trains' rundown is protected against a closed battery limit. |
| 2026-11-05-basic-design#9 | P-07 | BOG-7008/7009/7010, UV-7104A/B/C, TI-7107 | The anti-surge recycle takes discharge gas (~-49 degC) back to each machine's own suction downstream of D-7101, with no cooler and no spray. At full recycle (SEQ-BOG-START S1 "start on full recycle") the suction temperature climbs steadily towards conditions the low-temperature machine is not designed for. No high discharge temperature trip exists (TI-7107 only indicates). | high | open | Return the recycle upstream of the desuperheater spray TV-7103 / D-7101 so that it is quenched, or add a recycle cooler. Add a high discharge (or suction) temperature trip (TZT) to the C&E. |
| 2026-11-05-basic-design#10 | P-07 | CV-7122A/B/C, recycle tee T7QA | The recycle take-off is downstream of the discharge check valve (`K7101A_N2 -> CV7122A -> T7QA`). The recycle loop therefore includes the common discharge header, which slows the anti-surge response on a trip. | medium | open | Move each discharge check valve downstream of the recycle tee. |
| 2026-11-05-basic-design#11 | P-07 | K-7101A/B/C discharge, BOG-7002 | A compressor has a suction XV but only a check valve on its discharge. The installed spare cannot be isolated from the 6 bar header for maintenance, and there is no vent, blowdown or N2 purge per machine. BOG-7002 has no battery-limit ESD or isolation valve. | medium | open | Add discharge block valves, a depressurising / vent connection to the flare and an N2 purge per machine, and a battery-limit isolation (ESD) valve on BOG-7002. |
| 2026-11-05-basic-design#12 | P-07, C&E | I-702, UZ-7121B/C, K-7101A/B/C | I-702 is written for K-7101A only. B and C are covered by a note, and `cheme validate` reports UZ-7121B/C with no interlock (cheme.instrument-no-interlock). No other compressor trips are listed: suction low pressure, discharge high pressure, seal gas, motor. | medium | open | Add I-702B/C (VZ-7110B/C) and the basic-stage machine trips, or a C&E entry that refers to the vendor protection package by tag. |
| 2026-11-05-basic-design#13 | P-01, P-07 | PV-1111, BOG-1009, I-204 / I-304 | The make-up gas against tank vacuum comes from the compressor discharge BOG-7002. However, the vacuum trip I-204 stops all three compressors while it opens PV-1111. The make-up then depends on gas flowing back from the trains' fuel-gas system, and DESIGN.md does not state or size this. | medium | open | Give the make-up gas an independent source (e.g. trains' fuel gas or an LNG vaporiser) with its own line, or state the trains' supply and its capacity against full-rate withdrawal in D-017. |
| 2026-11-05-basic-design#14 | P-01, C&E | PV-1110 (PIC-1110, I-203/I-303); PV-1111 (PIC-1111, I-204/I-304) | The tank high-high and low-low pressure trips act through the same valves the regulatory loops use (cheme.control-shared-element), so the trip and the control loop are not independent. | medium | open | Give the trip its own final element (e.g. a separate SIS-actuated flare valve and make-up valve), or credit only the PSVs and vacuum valves and record that in DESIGN.md for the SIL study. |
| 2026-11-05-basic-design#15 | P-02, P-03 | PSV-2131A/B, PSV-2133A/B, PSV-3131A/B, PSV-3133A/B | Each 225,000 m3 tank has two DN 250 pressure PSVs and two vacuum valves, with no installed spare and no inlet isolation or changeover. No capacity is shown against the governing case: loss of the BOG compressors while loading (45.6 t/h return plus the rundown displacement) or rollover. The vacuum valves are set at -0.5 kPa(g), which equals the design vacuum, so they reach full capacity beyond the design vacuum. | medium | open | Size the tank relief (pressure and vacuum) for the governing cases and draw N+1 valves with locked-open, interlocked isolation. Set the vacuum valves less negative than the design vacuum. |
| 2026-11-05-basic-design#16 | P-02, P-03 | LZT-2102 / LZT-3102, I-201 / I-301, XV-2123 / XV-3123 | Overfill protection rests on one servo gauge, which also drives LALL (I-202) and I-101. I-201 closes only the fill XV-1102. The circulation return XV-2123 and the jetty drain return through the circulation loop can still fill a tank at LAHH. | medium | open | Add an independent high-high level (separate gauge, voting with LT-2101), and make I-201/I-301 also close XV-2123/XV-3123. |
| 2026-11-05-basic-design#17 | P-01, P-04, P-05, P-06 | PSV-1121, PSV-4111, PSV-4112, PSV-5131, PSV-6131 | These valves are set at 15.5 barg. That is above the 15 barg design of the lines and arms (D-023), LA-5101/5103/5104 and D-5101/D-6101 (equipment list). PSV-5131/6131 are called surge relief, but the estimated surge peak is 8.9 barg (D-023), so they would not lift on surge. | medium | open | Set the valves at or below the design pressure, or raise the stated design pressure to the Class 150 rating and record it. Restate the relief case of PSV-5131/6131 (thermal only, or surge with a set pressure below the peak). |
| 2026-11-05-basic-design#18 | P-05, P-06, P-08 | N-8001 / N-8002, HV-5151 | N2 enters the LNG header through a single ball valve and a check valve, from a 7 barg uninsulated header into a line that runs at up to ~9 barg, so LNG can flow back into the N2 system. SEQ-LOAD S2 reads O2 "at the arm vents", but no arm vents, drains or purge outlets are drawn. The N2 users of D-020 (tank inerting, pump columns, compressor seal gas, trestle line purge) are not drawn either. | medium | open | Use a double block and bleed or a removable spool on each N2 tie-in to LNG. Draw the arm vent and drain connections and the purge outlet route. Draw the D-020 N2 users, or limit D-020 to what is drawn. |
| 2026-11-05-basic-design#19 | P-04, P-08 | BOG-4001/4002, BOG-1001, FL-8001 | D-017 and S-02 send carrier de-inerting and cool-down vapour to the storage and loading flare, and the FL-8001 notes say "carrier de-inerting joining on P-08". No such line is drawn. The vapour return enters the tank vapour header with no valves, so inert or warm vapour would reach the tank vapour space and the compressors to the trains. | medium | open | Draw a de-inerting line from the vapour return (berth or tank end) to FL-8001 with isolation valves, plus an analyser on the vapour return to switch it. Correct the FL-8001 note. |
| 2026-11-05-basic-design#20 | P-08 | D-8101, LIC-8101, P-8101A/B | The flare knock-out drum has only LIC-8101, with no final element drawn and no independent high-high level, so liquid carry-over to FL-8101 is unprotected (validate: LIC-8101 notes a trip but no interlock exists). P-8101A/B have no suction isolation and no minimum flow. | medium | open | Add an independent high-high level on D-8101 with a C&E entry, draw the pump start/stop, and add suction isolation and minimum flow to the pumps. |
| 2026-11-05-basic-design#21 | P-05, P-06 | D-5101 / D-6101, LIC-5111 / LIC-6111 | The jetty drain drum receives the header drains and the relief from PSV-5131, but has only LIC-5111 (its notes say "high-high level alarm"). It has no independent high-high level, and an overfull drum spills into the vapour return through BOG-5002. | medium | open | Add an independent high-high level and a C&E entry (stop the drain, alarm). Write LIC-5111/6111 into the C&E, or reword their notes (cheme.instrument-no-interlock). |
| 2026-11-05-basic-design#22 | control/sequences.yaml | SEQ-LOAD, SEQ-HOLD; XV-4105, XV-2123, XV-4106, XV-5122, XV-5125 | SEQ-LOAD has no line-up step from holding. SEQ-HOLD leaves XV-4105 and XV-2123 open, so line B would send loading flow back into the tank. XV-4106 (tank-end crossover, needed for FIC-4102 at 6,000 m3/h from T-2101 pumps only) and the vapour arm isolation XV-5122 are never opened, and S4 opens XV-5123 without XV-5125 closed. | medium | open | Add a line-up step with permissives: XV-4105 and XV-2123 closed, XV-4106 and XV-4103 open, XV-5122 open, XV-5125 closed, and the spray supply (P-2102) running. |
| 2026-11-05-basic-design#23 | DESIGN.md, P-05/P-06, line list | D-009, D-014, D-023; LA-5102/5103; BOG-5001 | The design case contradicts itself. At 12,000 m3/h the hybrid arm runs as the third liquid arm (D-014, SEQ-LOAD S4), which leaves one vapour arm of ~23.5 t/h (D-023) against the 45.6 t/h return that the trestle vapour lines and the BOG compressors are sized for. The BOG-5001 notes say the hybrid is the second vapour path at high return. | medium | open | Choose one design case (3 liquid arms with a limited return, or 2 + 2 at a reduced rate) and make D-009, D-014, D-023, the line list notes, SEQ-LOAD and the compressor sizing agree. |
| 2026-11-05-basic-design#24 | P-02, P-03 | P-2101A-D, P-2102, P-3101A-D, P-3102 | Each in-tank pump column has a check valve but no isolation valve, and no column vent or N2 purge connection. A pump cannot be lifted out while the loading header is in service. | medium | open | Add an isolation valve and a vent/N2 purge connection on each pump column discharge. |
| 2026-11-05-basic-design#25 | control/instrument-list.yaml | UZ-5131..5144, UZ-6131..6144 | The notes say the ERS valves close "on ESD-1 / ESD-2 (C&E I-501, I-503)", but I-501/I-601 do not close them (only I-503/I-603 do). | low | open | Correct the notes, or the C&E, to the intended ESD-1 / ESD-2 split. |
| 2026-11-05-basic-design#26 | P-07 | PSV-7105 | The relief case is "blocked outlet of D-7101" at 2.5 barg. BOG-1001 has no valves and is open to the tanks, whose PSVs lift at 0.29 barg, so D-7101 cannot reach 2.5 barg in that case. | low | open | Restate the governing case (fire on an isolated D-7101, if it can be isolated) or justify the valve. |
| 2026-11-05-basic-design#27 | equipment list | D-8101 | The notes (and datasheet) name "PV-2111/3111 to flare". No such tags exist; the flare valve is PV-1110. | low | open | Correct the tag in the equipment list and the D-8101 datasheet. |
| 2026-11-05-basic-design#28 | P-02, P-03, P-08 | T-8102, FL-8101, TI-2105 | Not drawn: rainwater removal from the jetty sump T-8102, the flare pilot ignition and flame-front system, and the tank bottom heating that the TI-2105/TI-3105 notes refer to. | low | open | Draw them, or record them in D-021.7 as not shown at basic. |

## Previous findings

None: this is the first review record of this plant (`ls reviews/` shows only README.md).

## Drawing

`cheme validate --skip-generators` drawing lines:

- P-01: 0 line-through-label, 0 line-crossing, 0 label-overlap, 0 label-far-from-owner, 0 text-outside-frame, 0 title-text-overflow, 0 line-through-symbol
- P-02 to P-08: the same, all 0.

Rendered: `cheme render pid/P-0x.xml --png --tiles auto` (3x3 tiles A1-C3 per sheet) and the
full sheets `build/P-01.png` ... `build/P-08.png`. I read every full sheet, plus tile P-02 A1 and
the crop `build/P-05_crop-10-120-200-215.png` (scale 8) to confirm the unvalved drain DR-5001
and the pump-column valves. I settled doubtful connections with `cheme show`: DR-5001, LNG-5005,
LNG-5006, BOG-7008, K-7101A, HV-5151, and the item order on BOG-7002 S1.

## Mechanical checks (non-layout)

- `cheme validate`: 1 error, outside this scope. It is `cheme.hazop-schema` in
  safety/hazop/H-03/study.yaml, which another agent is writing.
- Non-layout infos in scope: 7 `cheme.instrument-no-interlock` (LIC-5111, LIC-6111, UZ-7121A/B/C,
  LIC-8101, LI-8103; see #12, #20, #21), 8 `cheme.control-shared-element` (#14), 22
  `cheme.control-logic-text` (sequence text; acceptable at basic), 12 `cheme.offpage-mismatch`
  (all accepted under D-021.4), 4 `cheme.generator-undeclared` (scripts are provenance,
  D-021).
- `cheme check --stage basic`:
  - ok: pids-valid, drawing-clean, process-basic, process-links, tank-protection-on-pid,
    berth-arms-on-pid, bog-compressors-on-pid, issues-basic;
  - FAIL design-review (this record answers it once its critical/high findings are closed);
  - FAIL layout-3d, lifting-study, mto, layout-review (layout scope, not reviewed here).

## Checked and fine

- Fail positions on the sheets agree with control/loops.yaml: the ESD and ERS valves fail
  closed, the minimum-flow FVs and anti-surge UVs fail open, FV-4101/4102 fail in their last
  position, and PV-1110/PV-1111, TV-7103 and LV-7102 fail closed.
- C&E tags resolve against the lists and sheets (validate cross-check).
- In-tank pump protection: a minimum-flow return per pump (FV fails open, ~30 %), the low-low
  level trip (I-202/I-302) and a column check valve.
- Tank instrumentation: radar LT, independent servo LZT, LTD profile for rollover, multipoint
  TI, annular-space TI, independent PZT; top/bottom fill selection from AI-1102 against LTD.
- Tank pressure cascade: compressors, then PV-1110 to the flare, then PSVs to atmosphere; vacuum
  cascade: make-up, then trip, then vacuum valves (D-017). The arrangement is sound; see #13 to
  #15 for independence and sizing.
- Berths: a shore ESD valve with surge-limited closure, a strainer with PDI, the header
  back-pressure trip (I-502), ERS valves either side of the coupler on every arm, the ship-shore
  link XS-5100/6100, envelope monitoring per arm. The thermal relief of the 2.45 km loading lines
  (PSV-4111/4112) is present.
- BOG: suction drum with LIC and an independent LZT trip (I-701), desuperheater TIC-7103 failing
  closed, anti-surge controller per machine, suction XV per machine, discharge PSV-7111 to the
  flare, PSV-7105 on the suction.
- Line DNs on the sheets agree with the line list (validate cross-check, 0 findings).
  Velocities: 3.4 m/s at DN 800/900, ~9 m/s on the DN 750 vapour return.

## Not checked

- Most individual tiles were not read one by one; I read the full sheets instead, which are
  legible at A3. Tiles read: P-02 A1, plus one P-05 crop.
- Relief and PSV sizing, the surge transient, vacuum valve capacity, insulation and heat-ingress
  numbers, and pump and compressor curves (detail stage, vendor).
- process/flowsheet.yaml was used as a basis only; its balances were not re-derived.
- Fire and gas, the area classification, materials and spec breaks, and the vendor packages
  (arms, ERS, compressor seal gas and lube oil). The HAZOP (safety/hazop) is being written
  concurrently and was not reviewed.
- Layout, routing and the 3D model (separate layout review).
