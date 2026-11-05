---
topic: design
reviewed_commit: 75e0b9fc7c32477c754a52e265751ce45466d5f9
scope: [pid/P-01.xml, pid/P-02.xml, pid/P-03.xml, pid/P-04.xml, pid/P-05.xml, pid/P-06.xml, pid/P-07.xml, pid/P-08.xml, equipment/equipment-list.yaml, piping/line-list.yaml, piping/special-items.yaml, control/instrument-list.yaml, control/cause-effect.yaml, control/loops.yaml, control/sequences.yaml, DESIGN.md]
basis:
  - {path: process/flowsheet.yaml, revision: 75e0b9fc7c32477c754a52e265751ce45466d5f9, relation: depends-on}
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: design, follow-up (basic stage P&IDs P-01 to P-08, lists, C&E, loops, sequences)

## Summary

This is the independent follow-up to `2026-11-05-basic-design` (28 findings on `7bcea968`). It
reviews HEAD `75e0b9fc` on `stage/lng-terminal-1-concept`. The author answered the first review
in `589c9ca7` (DESIGN.md D-025). The scope files in the working tree are the same as HEAD; the
only uncommitted change is `layout/plant-model.yaml`, which is outside this scope.

Most of the response holds up on the drawn sheets:
- The critical drain finding is closed. DR-5001 / DR-6001 now carry XV-5161 / XV-6161 between
  the header tee and the relief-outlet tees, and the drum vent stays open.
- The thermal relief that D-017 asks for is drawn on every blockable LNG section reviewed:
  the fill branches, the pump and circulation headers, the crossover, the circulation return,
  each liquid arm and the pumps of the drain drum and the flare KO drum.
- The anti-surge recycles now return upstream of the desuperheater spray, and each discharge
  check valve sits downstream of its recycle tee.
- The tank high-high pressure trip has its own SIS vent valve, XV-1115.

Of the 28 previous findings, 24 are closed by `589c9ca7` and 4 are still open: #4, #12, #23
and #27. None is carried as accepted. Three of the closed findings had parts that are not done
yet. Those parts are split out as new findings: #9 (from #11 and #18) and #10 (from #15).

The set is **not ready for basic-engineering issue** yet. One new **high** finding blocks it,
and it comes from the response itself. The new de-inerting switch on P-04 lets ESD-1 close the
carrier vapour return at both of its valves: ESD-1 closes XV-4131 but does not open XV-4135.
When that happens, every jetty relief outlet discharges into a closed vapour system that
includes the 3.5 barg vapour arm. Previous #4 also stays high. ESD-2 still does not trip ESD-1:
it is only stated in the notes. The new 5 s delay is an on-delay of the whole trip, so it
holds back the pump stop by the same 5 s as the ERS closure.

Merge pending. The two high findings (#1 below and previous #4) must be closed before the stage
is signed off.

## Branch diff since the previous review (`cheme diff 7bcea968 --list`)

Commits since the reviewed `7bcea968`: `fde19351` (HAZOP studies H-01..H-05, outside this
scope), `589c9ca7` (the design-review and HAZOP response, D-025) and `75e0b9fc` (the previous
review record). Only the P&IDs changed among the sheets (`process/BFD.xml` and `PFD.xml` are
unchanged). There are 622 plant-item lines; per sheet they are:

```
pid/P-01.xml:  51  (19 added, 21 changed, 9 moved, 2 removed: BOG-1009 make-up from P-07 removed;
                    added FG-1001, FO-1117, FL-1001 + XV-1115/UZ-1115, PSV-1122/1123 with BOG-1010/1011, ZSC-1102/1103)
pid/P-02.xml: 109  (38 added, 61 changed, 5 moved, 5 modified: HV-2151A-D/2152, HV-2161..2165 + BOG-2011..2015,
                    PSV-2131C, PSV-2133C, PSV-2141/2142 + LNG-2031/2032, LZT-2106; CV-2121A-D/2122 modified)
pid/P-03.xml: 109  (the same for T-3101)
pid/P-04.xml:  49  (28 added, 16 changed, 5 moved: PSV-4113/4114 + BOG-4015/4016, BOG-4013/4014,
                    XV-4131/4132/4135/4136 with HS, AI-4133/4134)
pid/P-05.xml:  78  (37 added, 34 changed, 6 moved, 1 modified: XV-5161/HS-5161, CV-5116, HV-5115/5117/5119,
                    FO-5118, PSV-5118, PSV-5171/5173/5174 + DR-5003..5007, LZT-5112, ZSC-5123/5125,
                    HV-5152/5153 + N-5001; DR-5001 modified)
pid/P-06.xml:  78  (the same for Berth 1)
pid/P-07.xml: 116  (40 added, 60 changed, 9 moved, 7 removed: BOG-1009/BOG-7010 and recycle tees removed;
                    XV-7123A-C, XV-7125A-C, XV-7130 with UZ, TZT-7112A-C, HV-7124A-C + FL-7003..7005, BOG-7012)
pid/P-08.xml:  32  (15 added, 15 changed, 2 moved: LZT-8105, HV-8106A/B, FO-8107 + LNG-8005,
                    PSV-8109 + LNG-8006, BOG-4013 and FL-7003 inlets)
```

The commit message of `589c9ca7` gives a reason for every change, and D-025 lists them. No
changed item is `not drawn`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-design-2#1 | P-04, P-05, P-06, C&E | XV-4131 / XV-4135 (XV-4132 / XV-4136), I-501 / I-601, I-511 / I-611; BOG-4001 / BOG-5001, D-5101, PSV-4111, PSV-5131, PSV-5171/5173/5174, PSV-5118, LA-5102 | The new de-inerting switch lets the vapour return be closed at both of its valves. ESD-1 (I-501 / I-601) closes the flare valve XV-4131 / XV-4132 (fail closed) but does not open the tank-side valve XV-4135 / XV-4136. While I-511 has XV-4135 closed (de-inerting, gassing-up and cool-down), an ESD-1 therefore leaves BOG-4001 closed at both valves. This includes the ESD-1 test that SEQ-LOAD S3 makes "before cooldown", exactly in that period. The closed system then takes all the jetty relief: the D-5101 vent BOG-5002, the outlets of PSV-5131 / 5171 / 5173 / 5174 / 5118 (through D-5101) and probably PSV-4111 (BOG-4011 "to BOG-4001". The PSV sits on the trestle and, unlike BOG-4015/4016, no tank-side tie-in is stated). These are set at 15 barg, and the system includes the vapour arm LA-5102 (design 3.5 barg, equipment list) and the carrier's vapour manifold. The "make-before-break" is only in the notes of I-511 and the P-04 sheet note. No position switch is drawn on XV-4131 / XV-4135, the C&E has no condition "XV-4131 open", and nothing defines the switch back (I-511 `latching: false`, `reset: automatic`). The return can therefore break before it makes. | high | open | Do not close XV-4131 / XV-4132 on ESD-1, or have I-501 / I-601 open XV-4135 / XV-4136 first (both fail open anyway). Add position switches on XV-4131/4132/4135/4136 and write the make-before-break in both directions into I-511 / I-611 as logic (XV-4135 may close only with ZSO-4131 open, XV-4131 may close only with ZSO-4135 open). Alternatively, give the berth side of the switch its own relief to the flare. Put the switching steps into SEQ-LOAD S1 to S3. |
| 2026-11-05-basic-design-2#2 | P-05, P-06, C&E | I-504 / I-505 (I-604 / I-605), XV-5123 / XV-5125, ZSC-5123 / ZSC-5125 | The hybrid-arm "permissives" are written as trips on the valve in service. The cause is ZSC-5125 "open" and the effect is to close XV-5123, with `latching: false`. During loading the hybrid runs as a liquid arm at ~4,000 m3/h with XV-5123 open. A spurious or failed ZSC-5125 signal, or an attempt to open XV-5125, then closes the liquid arm under full flow: a fast closure, surge in the header and arm, and the 12,000 m3/h forced through two arms by FIC-4101/4102. The reverse case closes the vapour path. | medium | open | Write I-504/505 (I-604/605) as start permissives on the open command (XV-5123 may open only with XV-5125 proven closed, and the reverse), not as trips on the open valve. Keep the key interlock, and use a closed-position switch on each valve. |
| 2026-11-05-basic-design-2#3 | P-04, control/sequences.yaml | XV-4106, SEQ-LOAD S0, SEQ-HOLD S1, LNG-4006 / LNG-4005 | SEQ-LOAD S0 now opens the tank-end crossover XV-4106 (fail last), but no step closes it again: neither SEQ-LOAD S6 nor SEQ-HOLD S1. On P-04 both the crossover LNG-4006 and the circulation-return take-off LNG-4005 sit at the tank end, upstream of FV/XV-4101 and FV/XV-4102. With XV-4106 open in holding, the P-2102 flow takes the short path LNG-2002, line A, XV-4106, line B, LNG-4005, XV-4105 back to the tank. The 2.45 km trestle lines are not circulated, so they warm up and take vapour before the next loading. | medium | open | Add "XV-4106 close" to SEQ-HOLD S1 (and to SEQ-LOAD S6), and add "XV-4106 closed" to the SEQ-HOLD permissives or to its complete condition. |
| 2026-11-05-basic-design-2#4 | P-01, C&E | XV-1106/1107/1108/1109 (HS, fail last), I-102, PI-1104, LNG-1001 | I-102 now protects the rundown when both fill ESD valves are closed. It does not see a branch closed by its selection valves: ZSC-1102 reads "not closed" while both XV-1106 and XV-1107 are shut, for example during a top/bottom fill change. In Phase 1, or with the other tank tripped, the rundown header is then dead-headed against the trains, the same consequence as previous #8. The header has only PI-1104 and the DN 25 thermal valve PSV-1121. | medium | open | Add a rundown header high-high pressure trip (PZT on LNG-1001) to I-102, or count a branch as available only when its ESD valve and one of its selection valves are proven open. Make the top/bottom change make-before-break. |
| 2026-11-05-basic-design-2#5 | control/loops.yaml, DESIGN.md, control/instrument-list.yaml | PIC-1111; D-007, D-017; TZT-7112A-C, ZS-5151..5154 | Text left behind after D-025. PIC-1111 still says "admitting compressed BOG", "Make-up from the compressor discharge" and "vacuum relief at -0.5 kPa(g)" (now FG-1001 and -0.3 kPa(g)). D-017 still says "Tank vacuum: make-up from the BOG discharge". The TZT-7112A-C notes say "C&E entry by the orchestrator" instead of I-703A-C. The ZS-5151 notes name only I-503, although I-501 now also takes their stage-1 signal. | low | open | Update the PIC-1111 purpose, alarm response, target source and rationale, and D-017 (or point it to D-025). Replace "C&E entry by the orchestrator" with I-703A/B/C, and add I-501 to the ZS-515x / ZS-615x notes. |
| 2026-11-05-basic-design-2#6 | control/sequences.yaml | SEQ-LOAD S2 to S5; P-2101A; HV-5151 / HV-5152 / HV-5153 | SEQ-LOAD never starts P-2101A: S4 starts P-2101B/C/D, and S5 stops D, C, B and A. Three pumps make 9,000 m3/h, not the 12,000 m3/h of the S4 set points (D-011). S2 opens and closes only HV-5151 of the new double block and bleed. The second block HV-5152 and the bleed HV-5153 are not operated, so the N2 cannot reach the header and the bleed is never opened after the purge. | low | open | Start P-2101A in S3 or S4, or state which pump runs the cooldown. In S2, open HV-5151 and HV-5152 with HV-5153 closed. After the purge, close both blocks and open the bleed HV-5153. |
| 2026-11-05-basic-design-2#7 | P-08 | P-8101A/B, LNG-8001 | The KO drum pumps now have suction isolation, a common minimum flow and thermal relief. They still have no discharge isolation, only the check valves CV-8102A/B, so neither pump can be maintained while the other runs. | low | open | Add a discharge isolation valve per pump downstream of its check valve, with the thermal relief PSV-8109 kept on the common section. |
| 2026-11-05-basic-design-2#8 | P-02, P-03, line list | HV-2161..2165, HV-3161..3165, BOG-2011..2015, BOG-3011..3015 | The pump-column vents that close previous #24 are blind-flanged ball valves "to atmosphere at the roof". A column holds LNG at tank pressure, and venting it before a pump is lifted releases methane at the tank roof. | low | open | Route the column vents to the tank vapour space or BOG-1001 (with the N2 hose connection kept for purging), or state the venting procedure and the vendor's arrangement in D-021. |
| 2026-11-05-basic-design-2#9 | P-07, P-08, DESIGN.md | D-020; K-7101A/B/C; N-8001 | Split from previous #11 and #18; their main parts are closed. D-020 still lists N2 for "seal gas and blanketing" and the purge of the arms and lines. The only N2 users drawn are the two berth tie-ins. The P-07 note defers the N2 purge per machine to "detail engineering". Tank inerting and the trestle purge are neither drawn nor listed as not shown. | low | open | Draw the N2 purge connection of each compressor and the trestle and tank inerting points, or list them in D-021.7 as not shown at basic and limit D-020 to what is drawn. |
| 2026-11-05-basic-design-2#10 | special-items, DESIGN.md | PSV-2131A-C/2133A-C, PSV-3131A-C/3133A-C, PSV-5131/6131, FO-1117 | Split from previous #15 (its N+1 and vacuum set point are closed). No relief device is sized against its governing case yet. One case is new with D-025: gas blow-by from the trains' fuel gas through FO-1117 with PV-1111 failed open. | medium | accepted: relief sizing is a detail-stage calculation; D-025 records the cases (tank fire, rollover, utility failure with both vents closed, the surge analysis). Add the FO-1117 blow-by case to that list. By Claude (independent review agent), for the human reviewer to confirm at sign-off | Size the relief in detail engineering. Add the FO-1117 blow-by case to the D-025 list and to the PSV-2131 / PSV-3131 relief cases in special-items. |
| 2026-11-05-basic-design-2#11 | P-04, C&E | AI-4133 / AI-4134, I-511 / I-611, BOG-4013, FL-8001 | I-511 sends vapour with "high N2/O2" to the storage and loading flare header. That header also carries hydrocarbons (PV-1110, XV-1115, PSV-7105/7111). No O2 limit is stated above which the carrier's vapour is accepted neither by the flare nor by the tanks. | low | open | State the O2 limit for vapour to the flare (inert-gas quality) in D-017 or D-025. Above it, close the berth's vapour return to the flare and require the carrier to vent on board (terminal rules); keep the AI-4133 trip logic separate for N2 (flare) and O2 (reject). |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-design#1 | DR-5001 / DR-6001 header drain without a valve; drum open to the vapour return | critical | closed 589c9ca7 | `cheme show DR-5001`: T50D, then XV5161, then T50P (the PSV-5131 outlet), then T50Q/T50U/T50X/T50R (the relief outlets), then D-5101 N1, all DN 150; DR-6001 is the same (T60D, XV6161, T60P). XV-5161 fails closed and is opened only in SEQ-LOAD S6; the vent BOG-5002 stays open. Crop `build/P-05_crop-0-40-120-200.png`. |
| 2026-11-05-basic-design#2 | Drain pump without check valve, isolation or minimum flow | high | closed 589c9ca7 | P-05/P-06: HV-5115 suction; discharge with the minimum-flow take-off FO-5118 to the drum and the vent HV-5119, then CV-5116, then PSV-5118, then HV-5117 to LNG-5006 (crop above, LNG-5006 notes). |
| 2026-11-05-basic-design#3 | Hybrid arm liquid/vapour isolations not interlocked | high | closed 589c9ca7 | ZSC-5123/5125 drawn, I-504/I-505 (I-604/I-605) in the C&E, key interlock in the P-05 note, SEQ-LOAD S0 complete on XV-5125 closed. How the interlock is written is a new finding: #2 of this record. |
| 2026-11-05-basic-design#4 | ESD-2 does not stop the pumps or initiate ESD-1; ERS closure not in the surge case | high | open | Only partly answered. I-503/I-603 now stop the pumps and I-501 takes ZS stage 1, but ESD-2 still does not trip ESD-1: I-501's logic has no `interlock: I-503` condition. I-503 therefore leaves out I-501's XV-4101/4102, XV-5161 and XV-4131 closures and the ship-shore trip XS-5100 (the carrier's ESD). The `delay: 5 s` of I-503 is, by the schema, the on-delay of the whole trip. It holds back the pump stop and the XV-5101 closure as well as the ERS closure, and the ERS valves then close together with the pump stop, not 5 s after it. The ERS closure time and the surge analysis are deferred in D-025, which is acceptable at basic. The C&E sequence is not. Proposed: add `{interlock: I-503, state: tripped}` to I-501's `any`. Take the delay off I-503 and close the ERS valves in a separate interlock whose cause is I-503 tripped with a 5 s on-delay (the same for Berth 1). |
| 2026-11-05-basic-design#5 | Fill branches downstream of XV-1102/1103 blockable without thermal relief | high | closed 589c9ca7 | P-01: PSV-1122 on LNG-1002 below XV-1102 and PSV-1123 on LNG-1001 between XV-1103 and the LNG-1003 tee, both to BOG-1001 (BOG-1010/1011); listed in special-items. |
| 2026-11-05-basic-design#6 | Tank-end headers, crossover and circulation return without thermal relief | high | closed 589c9ca7 | P-02/P-03: PSV-2141/3141 on LNG-2001/3001 and PSV-2142/3142 on LNG-2002/3002 into the tank. P-04: PSV-4113 on LNG-4006 and PSV-4114 on LNG-4005 between XV-4105 and the tank valves, both to the tank side of the vapour switch (BOG-4015/4016). |
| 2026-11-05-basic-design#7 | Liquid arm sections trapped between arm valve and ERS without thermal relief | high | closed 589c9ca7 | P-05/P-06: PSV-5171/5174 on the LA-5101/5104 risers above XV-5121/5124, and PSV-5173 on the hybrid riser between XV-5123, XV-5125 and XV-5133, into DR-5001 downstream of XV-5161 (DR-5003..5005). ERS cavity relief is left for the vendor in special-items. |
| 2026-11-05-basic-design#8 | Rundown dead-headed when no tank can take it | high | closed 589c9ca7 | ZSC-1102/1103 drawn; I-102 (both closed) closes XV-1111..1114, and its notes and D-025 send the train trip through the BL interface. The selection-valve gap is new finding #4. |
| 2026-11-05-basic-design#9 | Anti-surge recycle uncooled; no high discharge temperature trip | high | closed 589c9ca7 | `cheme show BOG-1001 --sheet pid/P-07.xml`: T7R0 and T7R1 (recycles), then T7P1 (PSV-7105), then T7S1 (spray), then TT-7103, then D-7101; the recycles are quenched. TZT-7112A-C sense BOG-7002 S1 and trip through I-703A-C. |
| 2026-11-05-basic-design#10 | Discharge check valve upstream of the recycle tee | medium | closed 589c9ca7 | `cheme show BOG-7002`: K7101A N2, then T7QA (recycle), then CV7122A, then T7XA (vent), then XV7123A, then the header. B and C are the same. |
| 2026-11-05-basic-design#11 | No discharge isolation, vent or N2 purge per machine; no BL ESD on BOG-7002 | medium | closed 589c9ca7 | XV-7123A-C (fail closed), HV-7124A-C to FL-7003..7005, then the flare, and XV-7130 (I-704) on BOG-7002 S6. The N2 purge, still "detail engineering" in the P-07 note, is split into new #9. |
| 2026-11-05-basic-design#12 | I-702 for K-7101A only; no other compressor trips | medium | open | I-702A/B/C are now in the C&E, and I-703A/B/C add the discharge temperature trips. The rest of the finding still stands. I-702 covers "vibration, bearings (API 670)" only: no suction low pressure, discharge high pressure (the PSV-7111 case is "blocked outlet with the compressors running"), seal gas, lube or motor trip, and no reference to a vendor package that has them. Nothing stops a running machine when its fail-closed suction valve XV-7121x closes. On an instrument-air failure all three close with the machines running, while the recycles (fail open) return upstream of D-7101, outside the isolated suction. Validate reports the UZ-7121/7123/7125 and UZ-7130 functions in no interlock (10 infos). |
| 2026-11-05-basic-design#13 | Make-up gas depends on the compressors that I-204 stops | medium | closed 589c9ca7 | P-01: FG-1001 from the trains' fuel gas, then FO-1117, then PV-1111, into BOG-1001; BOG-1009 removed from P-01/P-07. D-025 defers the fuel-gas capacity, which is acceptable at basic. |
| 2026-11-05-basic-design#14 | Tank PAHH/PALL trips act through the control valves | medium | closed 589c9ca7 | I-203/I-303 open XV-1115 on FL-1001 (bypass of PV-1110, UZ-1115). I-204/I-304 no longer act on PV-1111, so PIC-1111 is regulatory only and the vacuum valves are the last protection (D-025.1). The control-shared-element infos are now only the compressor stop shared with PIC-7101 and LV-7102 with I-802. |
| 2026-11-05-basic-design#15 | Tank PSVs and vacuum valves: no spare, no capacity, vacuum set at the design vacuum | medium | closed 589c9ca7 | P-02/P-03: PSV-2131A/B/C and PSV-2133A/B/C (N+1, interlocked locked-open inlet isolation in the note), vacuum set -0.3 kPa(g). The capacity part is split into new #10 (accepted). |
| 2026-11-05-basic-design#16 | Overfill protection on one gauge; I-201 does not close the circulation return | medium | closed 589c9ca7 | LZT-2106/3106 drawn with their own nozzles; I-201/I-301 trip 1oo2 and close XV-1102 and XV-2123 (XV-1103 and XV-3123 for T-3101); I-101 votes both pairs. |
| 2026-11-05-basic-design#17 | Relief set at 15.5 barg above the 15 barg design; PSV-5131 case | medium | closed 589c9ca7 | special-items: every LNG relief valve at 15.0 barg. The PSV-5131/6131 case is restated as surge on a fast ERS / ESD-2 closure and thermal, sized from the detail surge analysis. |
| 2026-11-05-basic-design#18 | N2 into LNG through one valve; arm vents and D-020 users not drawn | medium | closed 589c9ca7 | P-05/P-06: HV-5151, bleed HV-5153 to atmosphere, HV-5152, check valve. The P-05 note puts arm vents, drains, purge outlet and O2 sample point in the arm package, and D-025 defers them (acceptable). The D-020 users are split into new #9. |
| 2026-11-05-basic-design#19 | No de-inerting line to the flare; vapour return unvalved into the tanks | medium | closed 589c9ca7 | P-04: BOG-4013/4014 with XV-4131/4132 to D-8101 (FL-8001, P-08), XV-4135/4136 to BOG-1001, AI-4133/4134; FL-8001 notes corrected. The blocking that the new switch allows is new finding #1. |
| 2026-11-05-basic-design#20 | D-8101 without an independent high-high level; pumps without isolation or minimum flow | medium | closed 589c9ca7 | P-08: LZT-8105 (own nozzle) and I-802 (start P-8101B, close LV-7102); HV-8106A/B, FO-8107 on LNG-8005 to the drum, PSV-8109. Discharge isolation is new #7. |
| 2026-11-05-basic-design#21 | D-5101 without an independent high-high level | medium | closed 589c9ca7 | LZT-5112/6112 drawn, I-506/I-606 close XV-5161/6161; the LIC-5111/6111 notes are reworded. |
| 2026-11-05-basic-design#22 | SEQ-LOAD without a line-up from holding | medium | closed 589c9ca7 | SEQ-LOAD S0 closes XV-4105/2123/3123, opens XV-4106/4103/5122, closes XV-5161 and starts P-2102, and is complete on XV-5125 closed. The open XV-4106 left into holding is new #3. |
| 2026-11-05-basic-design#23 | Design case contradiction: 3 liquid arms leave one vapour arm (~23.5 t/h) against the 45.6 t/h return | medium | open | Not answered by D-025. D-014, SEQ-LOAD S4 (the hybrid opened as liquid), D-023 and the BOG-5001 notes still combine three liquid arms with a 45.6 t/h design return. That return is about twice one arm's capacity, and D-010 sizes the compressors and the DN 750 trestle lines for it. |
| 2026-11-05-basic-design#24 | Pump columns without isolation or vent | medium | closed 589c9ca7 | P-02/P-03: HV-2151A-D/HV-2152 above the check valves, column vents HV-2161..2165 (BOG-2011..2015), pressure-equalising check valves. The vent destination is new #8. |
| 2026-11-05-basic-design#25 | UZ-5131.. notes name I-501 | low | closed 589c9ca7 | instrument list UZ-5131 / UZ-6131: "Closes on ESD-2 (C&E I-503), not on ESD-1"; the P-05 note agrees. |
| 2026-11-05-basic-design#26 | PSV-7105 case "blocked outlet" impossible | low | closed 589c9ca7 | special-items PSV-7105: fire on D-7101 and the suction header, with the reason the blocked outlet cannot occur. |
| 2026-11-05-basic-design#27 | D-8101 notes name PV-2111/3111 | low | open | The equipment list is corrected (PV-1110 and XV-1115), but `equipment/datasheets/D-8101.yaml` line 130 still reads "tank pressure control (PV-2111/3111 to flare)". The datasheet was redrafted in 589c9ca7. |
| 2026-11-05-basic-design#28 | T-8102 rainwater, flare pilots, tank bottom heating not drawn | low | closed 589c9ca7 | P-08 note: T-8102 is emptied by a portable pump once TSL-8104 confirms no LNG; the pilot ignition and flame-front generator are part of the site flare derrick package (S-02). D-025 lists tank bottom heating as not done at basic. |

## Drawing

`cheme validate` drawing lines at `75e0b9fc`:

- P-01 to P-06 and P-08: 0 line-through-label, 0 line-crossing, 0 label-overlap,
  0 label-far-from-owner, 0 text-outside-frame, 0 title-text-overflow, 0 line-through-symbol.
- P-07: 0 line-through-label, 0 line-crossing (+2 accepted: BOG-7001 x BOG-7009 and
  BOG-7002 x FL-7004, `checks/checks.yaml`, reason D-025, a topological minimum for the
  three-machine recycle and vent layout), all other counts 0.

Rendered: `cheme render pid/P-0x.xml --png --scale 4`, giving the full sheets `build/P-01.png`
to `build/P-08.png`. I read all eight. I also read the crop `build/P-05_crop-0-40-120-200.png`
(scale 8) to confirm the order of the drain-pump valves and of XV-5161. Doubtful topology was
settled with `cheme show`: DR-5001, DR-6001, BOG-4001 (P-04), K-7101A, BOG-7002 and BOG-1001
(P-07). Fail positions were read from the `FailAction` of every ActuatingSystem on the eight
sheets and compared with control/loops.yaml and the instrument-list notes.

## Mechanical checks (non-layout)

- `cheme validate`: 0 errors, 84 warnings. All the warnings are outside this scope.
  - Layout (`cheme.layout-*`).
  - HAZOP: 27 `cheme.hazop-input-changed`, because the studies still stamp the pre-D-025
    sheets. 4 `cheme.hazop-unknown-tag` for BOG-1009 in safety/hazop/H-04, which 589c9ca7
    removed.
  - Non-layout infos in scope:
    - 15 `cheme.instrument-no-interlock`. UZ-1115, UZ-7121/7123/7125 A-C and UZ-7130 are
      effects (as XV-tags) of I-203/I-303, I-701..I-704, a naming convention, but see #12.
      LIC-5111/6111 and LIC-8101 are matched on "starts and stops"; LI-8103 likewise.
    - 7 `cheme.control-shared-element`: the compressor stop with PIC-7101 and LV-7102 with
      I-802, meant.
    - 22 `cheme.control-logic-text`: sequence text, acceptable at basic.
    - 12 `cheme.offpage-mismatch`: accepted under D-021.4.
    - 2 `cheme.line-crossing`: the accepted P-07 crossings.
    - 4 `cheme.generator-undeclared`: D-021, the scripts are provenance.
    - 3 `cheme.accept-unused`: layout accept entries.
- `cheme check --stage basic`:
  - ok: design-basis, concept-lists, process-concept, process-balances, process-links-concept,
    process-basic, process-links, assumptions-marked, pids-valid, drawing-clean, pids-exist,
    issues-concept, issues-basic, tank-protection-on-pid, berth-arms-on-pid,
    bog-compressors-on-pid;
  - FAIL design-review: the previous record is stale since 7bcea968. This record replaces it;
    the gate stays blocked while #1 and previous #4 (high) are open;
  - FAIL layout-3d, lifting-study, mto, layout-review: layout scope, not reviewed here.

## Checked and fine

- Fail positions agree between the sheets, control/loops.yaml and the instrument list:
  - fail closed: the ESD/ERS valves, the berth arm and drain valves, XV-1115, XV-4131/4132,
    XV-7121/7123 A-C and XV-7130, PV-1110/PV-1111, TV-7103 and LV-7102;
  - fail open: XV-4135/4136, XV-7125A-C, UV-7104A-C and the minimum-flow FVs;
  - fail last: FV-4101/4102 and the HS selection and crossover valves.
- On an instrument-air failure, the vapour return stays open to the tanks through XV-4135/4136,
  so new finding #1 is an ESD case, not an air-failure case. The arms and the header are then
  relieved to D-5101, and the tripped compressors relieve to the tank system through their
  open recycles.
- XV-1115 is energise-to-trip, fail closed, with its own accumulator. D-025 gives the reason:
  a fail-open vent together with the fail-closed make-up would depressurise the tanks. The
  reason is sound. The SIL study must credit the energise-to-trip design (line monitoring,
  the accumulator) and keep the tank PSVs as the last layer.
- Each tripped compressor is isolated at suction and discharge (I-701, I-702x, I-703x) and keeps
  its relief path through the recycle, which XV-7125x keeps open. PSV-7111 sits between
  XV-7123x and XV-7130, so it covers the discharge header closed by I-704 or on air failure.
- Each relief outlet on the berths ties in downstream of XV-5161 / XV-6161. The tank-end PSV-4113
  and PSV-4114 tie in on the tank side of the vapour switch.
- Line DNs, the instrument list and special-items agree with the sheets (validate cross-checks:
  lines and DN, instruments, piping items, interlocks against lists and P&IDs, 0 findings).
- I-101, I-102, I-201 (1oo2), I-202 and I-204/I-304 act on the right valves and drives for their
  causes. I-802 closing LV-7102 is backed by I-701 if D-7101 fills.

## Not checked

- The 3x3 tiles were not read one by one. I read the full sheets at A3 legibility and one P-05
  crop. P-06 and P-03 were compared with P-05 and P-02 on the full-sheet renders and the
  identical diff counts, not object by object.
- The sizing of relief and PSVs, vacuum valves and the drain drums; the surge transient with the
  ERS closure time; the trains' fuel-gas capacity for the make-up; insulation and heat ingress;
  pump and compressor curves (detail stage, vendor; see #10).
- The HAZOP studies (safety/hazop) are being restamped by another agent and were not reviewed;
  their 27 `hazop-input-changed` warnings show that they do not yet describe the D-025 sheets.
- process/flowsheet.yaml was used as a basis only. The datasheets were checked only for
  previous #27.
- Fire and gas, area classification, materials and spec breaks, and the vendor packages (arms
  and ERS cavity relief, compressor seal gas and lube oil, the flare pilots).
- Layout, routing and the 3D model (separate layout review).
