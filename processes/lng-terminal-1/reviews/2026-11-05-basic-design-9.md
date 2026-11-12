---
topic: design
reviewed_commit: c257902c911552d23ee8dad1186536102de9488d
scope: [pid/P-01.xml, pid/P-02.xml, pid/P-03.xml, pid/P-04.xml, pid/P-05.xml, pid/P-06.xml, pid/P-07.xml, pid/P-08.xml, equipment/equipment-list.yaml, piping/line-list.yaml, piping/special-items.yaml, control/instrument-list.yaml, control/cause-effect.yaml, control/loops.yaml, control/sequences.yaml, DESIGN.md]
basis:
  - {path: process/flowsheet.yaml, revision: c257902c911552d23ee8dad1186536102de9488d, relation: depends-on}
reviewer: "Claude (independent review agent)"
reviewer_kind: agent
branch: stage/lng-terminal-1-concept
merge: pending
---
# Review: design, eighth follow-up (basic stage P&IDs P-01 to P-08, lists, C&E, loops, sequences)

## Summary

This is the independent follow-up to `2026-11-05-basic-design-8`. It reviews HEAD `c257902c` on
`stage/lng-terminal-1-concept`. I did not write any of this design. The working tree was clean
during the review. The round under review:
- `e71188c1`: HAZOP H-01..H-05 revised to `aedd8dbd` (outside this scope);
- `edf00cf0`: review records design-8 and layout-6, with their adversarial checks in
  `build/adversarial-design-r8.json` and `build/adversarial-layout-r8.json`;
- `c257902c`: the response to both (D-036 design, D-037 layout with D-037.15..17 on the dry jetty
  sump and P-8103; edits to D-009, D-010, D-014, D-016, D-018, D-022, D-023, D-026, D-030, D-033,
  D-034, D-035).

Every commit that closes a finding below (`c257902c`) is HEAD itself.

Review 8 left three mediums and six lows open, plus review 5 #9 (low). At HEAD, judged on the drawn
sheets, `cheme show` and the control files:
- **Review 8 #1 to #7 and #9 are closed.** The carrier is protected by a credited 1oo2 trip at the
  arms' outboard ends (PZT-n181 / n184, PAHH 5.0 barg). The BOG compressors are re-rated to 3 x 31.1
  t/h. P-8102 is re-rated, in stainless steel, Ex d, with CV-8114 / HV-8115 drawn. ZSC / ZSO-4107 are
  drawn. The Berth 1 cooldown, the O2 hold and the margin are written into the sequences. T-8102 has
  the fixed dry-sump pump P-8103.
- Review 8 #8 is superseded by #8 of this record, because the electrical-list motor-starting note is
  unchanged.
- Review 5 #9 stays open. The three accepted findings stay accepted.

The two items of the adversarial check against review 8 are answered, and the reason given for each
is sound. The P&ID parts of layout review 6 #2 are drawn and written: tappings and tie-ins are off
the trestle side, and the N2 push-back has stations, a sequence and an override. Their reasons are
sound, with the residuals #3 and #6 below.

This pass found eight new findings: one high, three mediums and four lows. The high comes from the
P-8102 fix:
1. **#1 (high).** TSL-8102 now sits at the T-8101 floor, below the pump intake. That floor is never
   dry: P-8102 needs ~0.5 m of submergence, and the pit holds up to 0.5 m more of rain before it is
   pumped down. The probe stands under water at 0 degC or above. It cannot see LNG floating on that
   water, so I-801 cannot stop P-8102 pumping LNG into the oily water system, and the foam start it
   carries is delayed.
2. **#2 (medium).** After ESD-1 the berth header and the arms stay connected to the carrier's
   manifold, with only the 15 barg PSVs as their relief. The carrier's piping is taken at 10 barg.
3. **#3 (medium).** SEQ-LINE-EMPTY aborts the N2 displacement when site N2 falls below 5 barg. That
   leaves the leak fed by the rest of the line. The ~4,000 Nm3/h it needs is unconfirmed.
4. **#4 (medium).** LZT-8106 is both the level control of P-8103 and the only sensor of the
   transfer hold and of I-805. One failure defeats all three.
5. **#5 to #8 (low):**
   - #5: the N2 bleeds vent to atmosphere at grade;
   - #6: no pressure on the isolated trestle line;
   - #7: the loop register and the philosophy are behind the sheets;
   - #8: stale texts.

Verdict: **not ready for basic-engineering issue on the design topic**. #1 is an open high. Close #1,
then disposition #2 to #4, recording the reason, before issue. The stage sign-off also needs a
current layout review, a human approver and the HAZOP restamp. That restamp is outside this scope:
there are 20 `hazop-input-changed` warnings. Merge pending.

## Branch diff

`cheme diff origin/main --list`: every sheet is new on the branch. The summary lines are:

```
pid/P-01.xml: (sheet added)
pid/P-02.xml: (sheet added)
pid/P-03.xml: (sheet added)
pid/P-04.xml: (sheet added)
pid/P-05.xml: (sheet added)
pid/P-06.xml: (sheet added)
pid/P-07.xml: (sheet added)
pid/P-08.xml: (sheet added)
process/BFD.xml: (sheet added)
process/PFD.xml: (sheet added)
```

The changes of this round (`cheme diff edf00cf0 --list`):
- **P-01.** FO-1117 is remodelled as a RestrictionOrifice.
- **P-03.** Added: TSL-3124.
- **P-04.**
  - Removed: LNG-5006 / LNG-6006 with their connectors and the tees T4X5 / T4X6.
  - Added: N-4001..N-4004, T4A6 / T4B6 / T4N1 / T4N2, HV-4151..4154, HV-4161 / 4162, FO-4151 / 4152,
    CV-4151 / 4152, PI-4155..4158 and ZSC / ZSO-4107.
  - Changed: LNG-4001 / 4002 / 4003 / 4010, PI-4105 / 4106 and TI-4103 / 4104.
- **P-05 / P-06.** Added: PZT-n181 / n184, T50K / T60K and FO-n118. Changed: LNG-n001, LNG-n006,
  PZT-n103, TI-n104 and PSV-n131.
- **P-07.** Added: TSL-7115.
- **P-08.** Added: P-8103, W-8003, CV-8114 / HV-8115, CV-8116 / HV-8117, LZT-8106 and TSL-8118.
  FO-8107 / FO-8111 are remodelled. Changed: W-8002 and T-8102.
- **BFD / PFD.** S3 changed, with no `generated-sheet-drift`.

Every change has its reason in D-036 / D-037 and in PROGRESS.md. No changed plant item is
`not drawn`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-05-basic-design-9#1 | P-08, C&E I-801, instrument list TSL-8102 / LI-8103, equipment list and datasheets P-8102 / T-8101 | TSL-8102 at the floor of a pit that always holds water; LNG pumped to the oily water system | D-036 put TSL-8102's tip "at the pit floor, below the pump intake", so that "LNG on a dry pit trips before the pump can draw it" (I-801 notes). But T-8101 is never dry at its floor. P-8102 needs "~0.5 m minimum submergence" (P-8102 datasheet), so its stop level, set by LI-8103, keeps water above the intake. The T-8101 notes allow "100 m3 (0.5 m) of rain ... before it is pumped down". So ~0.5-1 m of water always stands on the floor, and the probe sits under it at 0 degC or above. It cannot reach a low-temperature set point while LNG floats on that water. Spill case: the tank-area design spill (2,400 m3) lands on that water. LI-8103 is a radar on the top surface, so it reads the pool and starts or keeps P-8102 running. The pump draws the water from below until the water / LNG interface reaches the intake, and then pumps LNG up W-8002 into the site oily water system (50 m3/h). I-801, the only safeguard named against that ("keeps LNG out of the oily water system"), stays blind until the water round the probe has frozen and cooled. The motor is not de-energised before the vapour reaches it, and the high-expansion foam that I-801 starts (D-018) is delayed by the same mechanism. The fix that closed review 8 #3 introduced this, following that review's own proposal. P-8103 has the right arrangement for the same duty: a low-temperature probe in the discharge head, 1oo2 with the pocket probe (D-037.17). The tank-area sump also contradicts the binding basis that D-037.15 (a) restored for T-8102, "no LNG on standing water". T-8101 receives every tank-area spill onto standing water, falling ~13 m from the trough inlet, and no stated basis covers the boil-off, the burning rate or a rapid phase transition there. This is a wrong safeguard against a credible hazard: high. | high | open | Give I-801 a detection that sees LNG in a wet pit, voted 1oo2 so that either opens the feeder. Use a fast-response low-temperature probe in the P-8102 riser or discharge upstream of CV-8114, as TSL-8118 on P-8103, and a probe at the stop level or on LI-8103's surface, not at the floor. Add an LI-8103 rate-of-rise or high-high inhibit of P-8102: a spill rises metres in minutes, rain millimetres. Start the T-8101 foam from detection that is not under water (low temperature or gas at the pit rim, from the F&G system). Either keep T-8101 dry as T-8102 (floor pocket, pump with its submergence in the pocket) or state the basis that accepts LNG on its standing water, with the boil-off and rapid-phase-transition case for the siting study. |
| 2026-11-05-basic-design-9#2 | P-05 / P-06, special items PSV-n131 / n171 / n173 / n174, C&E I-501 / I-502, SEQ-ESD, DESIGN.md D-016 / D-036.11 (g) | Berth header and arms blocked in against the carrier's manifold after ESD-1 | ESD-1 closes XV-n101, and the carrier closes its ESD valve. The arm isolations XV-n121 / n123 / n124 and the ERS valves stay open: I-501 does not close them, and only ESD-2 (I-507) does. So one liquid-full section runs from XV-n101 to the carrier's valve: the berth header, the three liquid arms, the ERS and the carrier's manifold spool. Its only relief is PSV-n131 and PSV-n171 / n173 / n174, all set at 15.0 barg into D-n101 (special items). The uninsulated arms warm, and that section reaches the PSV set pressure. D-036 now states the carrier's manifold and cargo piping design at 10 barg (D-016, ASSUMED). The shore relief therefore lets the carrier spool reach ~15-16.5 barg after an ordinary ESD-1. D-036.11 (g) leaves it "for the compatibility study" because "the arms are drained in SEQ-LOAD S6". That reason does not hold: after ESD-1 the restart is from S3, with no drain (SEQ-ESD), and the section can stay blocked in for hours. One more sign of the problem: PZT-n181 / n184 (5.0 barg) will trip I-502 again on the warming section after every ESD-1. Medium: the carrier probably has relief of its own, but the shore design sets the pressure of a section shared with it. | medium | open | Relieve or vent the blocked-in section below the carrier's design pressure. Either: open XV-n161 to D-n101 once XV-n101 is proven closed after ESD-1 (C&E I-n01, SEQ-ESD S2), so the header and arms vent to the vapour return; or set the arm and header thermal reliefs below 10 barg; or confirm the carrier-side relief in the compatibility study as a hold. Say how I-n02 is reset in that state. |
| 2026-11-05-basic-design-9#3 | P-04, SEQ-LINE-EMPTY (permissives, S2, S3, abort), DESIGN.md D-036.5 / D-036.11 (b) / (c), line list N-4001 / N-4002 | N2 push-back: abort on low N2, unconfirmed N2 rate, line pressure in S3 | The drain-down bound (~3.5 h, ~36 m3, which closes the P&ID part of layout review 6 #2) rests on ~4,000 Nm3/h of site N2 for ~2.5 h. That rate is a hold with the trains' utility owner (D-036.11 (b)). (a) The abort condition "PI-4155 below 5 barg" closes the N2 blocks. The line then stays full and connected to the tank, so the leak is fed by the rest of the ~1,030 m3 at ~1 kg/s. At 1 kg/s, T-8102's 47 m3 margin above the 210 m3 budget lasts ~6 h, and with the 40 m3 drain-down allowance ~11 h. A site N2 system that cannot hold 5 barg at 4,000 Nm3/h therefore turns the bounded case back into the unbounded one of layout review 6 #2, by procedure. Below choking the orifice still passes N2 at a reduced rate (5 barg against ~2.7 barg in the line). CV-4151 already prevents reverse flow. (b) No fallback is stated if the confirmed N2 rate is lower: no time against N2 rate, and no limit for the PFP's 240 min. My check: the orifice, the ~450 m3/h of liquid and the ~3.7 bar(a) reproduce at Cd 0.62. At 2,000 Nm3/h the displacement takes ~4.6 h, which exceeds the 240 min PFP basis. T-8102 still holds the extra volume (~225 of 257 m3). (c) S3 keeps HV-4151 / 4152 open with XV-4105 / XV-2123 / XV-4103 closed "at ~2.7 barg". The station has an orifice but no pressure regulator, so the isolated line rises to the site N2 pressure (~7 barg) and pushes the dead legs and the film into the leak at that pressure. Medium: a sequence and design-basis defect in a recorded abnormal procedure, not a missing safeguard while N2 is available. | medium | open | Change the abort: on low N2 pressure continue at the reduced rate while PI-4156 stays above the line pressure, and abort only on reverse flow or a tank limit. State the displacement time and the leak volume against the N2 rate actually confirmed, and the minimum rate that keeps the 240 min PFP and the T-8102 budget. Make that minimum the hold's acceptance value (also as an issue, review 5 #9). In S3 add a pressure control (regulator or PCV) downstream of FO-n15x, or correct the text to the site N2 pressure and check the leak at it. |
| 2026-11-05-basic-design-9#4 | P-08, C&E I-805 / I-806 / I-807, SEQ-LOAD S0 / S4, instrument list LZT-8106 | One transmitter for the dry-sump control, the transfer hold and the I-805 trip | LZT-8106 starts and stops P-8103 (I-806 / I-807), gives the LAH transfer hold of SEQ-LOAD S0 / S4 and is the only cause of I-805. A transmitter that fails low or freezes does three things at once: P-8103 never starts, which is the initiating event for water on the sump floor; the hold never sounds; and I-805 never trips. The safeguard and the initiating event then share one device, so I-805 is not independent of the control failure it protects against. Taken with P-8103 being "no safety function" (I-806 notes), the "no LNG on standing water" basis rests on one sensor. D-037.16 (b) leaves a second transmitter to the SIL screening (H-06). It is medium: the sump only fills with water over hours of rain, and TSL-8104 still locks the pump out on LNG. | medium | open | Give I-805 and the LAH hold their own level device, independent of LZT-8106: a second radar, or a level switch at the pocket rim and at 0.60 m. Alarm a deviation between the two. Keep LZT-8106 for P-8103's control. |
| 2026-11-05-basic-design-9#5 | P-04, line list N-4003 / N-4004, D-036.11 (c) | N2 station bleeds HV-4161 / HV-4162 open to atmosphere at grade | Between transfers the inner blocks HV-4151 / HV-4153 hold the loading line, at up to ~12 barg at shut-off, and the DN 25 bleed between the blocks is open "to atmosphere", vented at 2.5 m at the PR1 joint in the tank area (D-037.15 (g)). A passing cryogenic ball valve then vents LNG continuously at grade, a release point that no zone or drip collection is stated for. It is low: the flow through a passing seat is small and frost shows it. | low | open | Route the bleeds to the vapour return or the flare header with the bleed valve kept open, or keep them closed with a pressure gauge between the blocks, read on rounds and before SEQ-LINE-EMPTY. Declare the release source in the zones if they stay open to air. |
| 2026-11-05-basic-design-9#6 | P-04, instrument list PI-4105 / PI-4106, SEQ-ESD S2, SEQ-LINE-EMPTY | Isolated trestle line pressure not measured | After ESD-1, LNG-4001 / LNG-4002 between XV-410x and XV-n101 / XV-4107 / XV-4103 are blocked in and warm towards PSV-4111 / 4112 (15 barg). Since D-036 their only pressure instruments are the clamp-on PI-4105 / 4106. Those are "deleted, never tapped" if no clamp-on sensor qualifies at -160 degC. No gauge sits between the N2 inner block and the line either (PI-4156 is upstream of CV-4151). SEQ-LINE-EMPTY then starts with the line pressure unknown: N2 at 7 barg enters only below that, and the leak rate depends on it. | low | open | Add a pressure gauge on the line side of HV-4151 / HV-4153 (tank end, over the PR1 collection, not in the header bay), and use it in the SEQ-LINE-EMPTY permissive and in SEQ-ESD S2. |
| 2026-11-05-basic-design-9#7 | control/loops.yaml, control/philosophy.md, instrument list LIC-5111 / LIC-6111, C&E | Loop register and philosophy behind the sheets | (a) The drawn controllers LIC-5111 / LIC-6111 / LIC-8101 and the P-8103 level duty are not in `control/loops.yaml` (D-037.17 (i), deferred). The permissive of LIC-5111 (start only with XV-5101 open and the flow established) exists only in instrument-list notes. Nothing stops P-5101 when ESD-1 closes XV-5101; it then dead-heads on its minimum flow, inside the 15 barg design. (b) `control/philosophy.md` names SEQ-HOLD, SEQ-LOAD, SEQ-BOG-START and SEQ-ESD only. It has nothing on SEQ-LINE-EMPTY, SEQ-FILL-CHANGE, the I-n01 output override, the carrier protection I-n02 at the arms, or the dry jetty sump. F-LINK does not cover a carrier closure whose link signal is lost. | low | open | Register LIC-5111 / 6111 / 8101 and the P-8103 level control, with their permissives, in loops.yaml. Bring the philosophy up to the sequences and the C&E: a failure entry for a trestle-side leak after ESD-1, and one for the carrier closure without the link signal. |
| 2026-11-05-basic-design-9#8 | datasheets P-5101 / P-6101, electrical list (motor-starting note), process/design-basis.yaml, C&E I-801 notes | Stale or inconsistent texts after D-036 | (a) The P-5101 / P-6101 datasheets still say "empties the jetty drain drum ... into the platform crossover (~445 kPa(a))" and "to the circulation return line". The pump now returns into the berth header downstream of XV-n101 in the S3 cooldown, so the basis of its 445 kPa(a) discharge is no longer stated. (b) The electrical list's motor-starting note keeps "the 1.4 MW compressors and the 0.64 MW in-tank" pumps; they are now 1.85 MW and 1.05 MW (the residual of review 8 #8 (b)). (c) `process/design-basis.yaml` still gives only "delivery 350 kPa(a) at the ship manifold". The carrier's 10 barg design pressure, the interface limit that I-n02 rests on, is in D-016 only (review 8 #1 asked for it in the design basis too). (d) The I-801 notes describe a dry pit (see #1). | low | open | Correct the P-n101 datasheets (discharge into the berth header in S3, its pressure there), the electrical motor-starting note, and the design basis (carrier manifold design pressure, ASSUMED, S-01). Correct the I-801 notes with #1. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-11-05-basic-design-8#1 | Re-rated pumps' shut-off against the carrier; PZT-n103 without a set point | medium | closed c257902c | **Drawn.** `cheme show PZT-5181`: it senses LNG-5011 S1 (LA5101_N2 -> XV-5131 -> XV-5141). Tiles `build/P-05_tile-B1.png` / `B2.png` and `build/P-06_tile-B1.png` / `B2.png`: PZT-n181 / n184 sit between the arm end and the inboard ERS valve. **C&E I-502 / I-602:** any of PZT-n181 / n184 at PAHH 5.0 barg (1oo2), PZT-n103 at 7.0 barg as an uncredited backstop; pumps stop, carrier tripped, XV-n101 closed. **Bound reproduced:** 2 x 445 x (2,160 x 3.4 + 250 x 6.8) / t = 322 kPa (25 s) / 268 kPa (30 s), so 5.0 + 3.2 + 0.1 = 8.3 barg, against 10 barg (D-016, ASSUMED). The normal pressure at the arm end is ~2.5-3.0 barg; on the header it is 5.2-5.5 barg (S3 647.9 kPa(a)), so 7.0 barg on the header is not a spurious trip. My check of one carrier manifold valve closing alone, with two arms still flowing on the pump curve: the header settles at ~7.3 barg, below 10 barg, and the backstop trips. The bound for an effective closure shorter than the stroke is recorded for H-01 and the compatibility study (D-036.11 (a)). That is a deferred surge analysis with a stated owner, so no finding. **Residuals:** the design-basis entry (#8 (c)) and the post-ESD blocked-in section (#2). |
| 2026-11-05-basic-design-8#2 | BOG compressors 3 x 27 t/h against the 56.5 t/h case | medium | closed c257902c | Equipment list K-7101A-C: 31.1 t/h, two machines for the 56.5 t/h, the third as spare. Datasheets and the electrical list: 1,850 kW. D-009 / D-010 carry correction notes. My polytropic check (108 -> 600 kPa(a), 133 K, k 1.33, 0.78) gives ~1.65 MW gas power, against D-036's 1,609 kW. D-7101 is at ~0.93 m/s. |
| 2026-11-05-basic-design-8#3 | Submersible P-8102 on the floor of T-8101 | medium | closed c257902c | (a) 44 m (26.6 + 10.2 + 7) and 10.0 kW reproduce, the shut-off ~57 m is inside the 10 barg design, motor 15 kW. (b) SS, -170 degC. (c) Ex d IIA T3, zone 1; I-801 opens the feeder, latching. (d) CV-8114 / HV-8115 drawn on W-8002 (`build/P-08_tile-C1.png`). **Residual:** the tip "below the pump intake" that this review asked for is blind in the wet pit, the new high #1. |
| 2026-11-05-basic-design-8#4 | Loading pump rating without margin | low | closed c257902c | SEQ-LOAD S4 states the reduced rate (~10,900 m3/h) and what the operator does. The motors are 1,050 kW (datasheet P-2101A, electrical list line 48). |
| 2026-11-05-basic-design-8#5 | XV-4107 without position proof | low | closed c257902c | ZSC-4107 / ZSO-4107 drawn on XV-4107 (`build/P-04_tile-A3.png`). They are used in SEQ-LOAD S0 / S3 (ZSO), SEQ-HOLD S1 and SEQ-ESD S1 (ZSC), and in SEQ-ESD S2 (discrepancy). |
| 2026-11-05-basic-design-8#6 | Berth 1 cooldown line-up | low | closed c257902c | The SEQ-LOAD header and the S3 action name line B / FIC-4102 at 500 m3/h in auto as the Berth 1 cooldown path, with FV-4101 closed in manual, so the tests that close XV-4107 do not cut it. |
| 2026-11-05-basic-design-8#7 | O2 hold on a timer; reset condition; fast-loop isolation | low | closed c257902c | I-511 logic: the hold ends once AI-4133 has seen O2 above 1 vol % and back below for 5 min, or on the operator's release after 1.5 line volumes. The I-514 reset condition is in SEQ-LOAD S1. The fast-loop isolation is a proven-closed permissive of the S1 leak test. |
| 2026-11-05-basic-design-8#8 | Stale texts after D-034 | low | superseded by 2026-11-05-basic-design-9#8 | Done: D-009 / D-010 / D-014 corrected; LA-5102 / LA-6102 at 52.5 t/h; no "I-{n}03" left in the C&E; S3 at 647.9 kPa(a). Not done: the electrical motor-starting note ("1.4 MW compressors, 0.64 MW in-tank", electrical-list.yaml line 188), carried in #8. |
| 2026-11-05-basic-design-8#9 | T-8102 water removal during a transfer | low | closed c257902c | P-8103 is drawn in T-8102, with W-8003, CV-8116 (drain-back hole) / HV-8117, TSL-8118 on the head and LZT-8106 (`build/P-08_tile-C2.png`). C&E I-805..I-808. LAH 0.50 m is the transfer hold (SEQ-LOAD S0 / S4). Gate `dry-sump-pump-on-pid` ok. **Residual:** one transmitter for everything (#4). |
| 2026-11-05-basic-design-5#9 | Deferred safety inputs not registered as issues, holds or TQs | low | open | `cheme issues --all`: still one issue (#362), no hold or TQ. D-036.10 says none can be opened from the design session. The N2 rate of #3 is a further hold for it. |
| 2026-11-05-basic-design-3#5 | LIC-8101 duty/standby drawn as a chain through HS-8101A | low | accepted: the standby no longer depends on the chain for the hazard; I-802 starts both pumps on LZT-8105 and I-803 stops both; availability of the level band only. By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged: the KO drum pumps and I-802 / I-803 are as before (`build/P-08_tile-B1.png` / `B2.png`). Only FO-8107 is remodelled as an orifice. |
| 2026-11-05-basic-design-3#6 | PZT-7113 1oo1 stops every running compressor | low | accepted: a spurious trip sends the BOG to the flare, a production and flaring loss with no hazard; the voting is left to the SIL screening (now hold H-06). By Claude (independent review agent), for the human reviewer to confirm at sign-off | Unchanged: PZT-7113 (`build/P-07_tile-A1.png`) and I-705A-C. |
| 2026-11-05-basic-design-2#10 | No relief device sized against its governing case | medium | accepted: relief sizing is a detail-stage calculation; D-025 records the cases, and D-026.8, D-026.14, D-028, D-030, D-032, D-034 and D-036 add the FO-1117 blow-by, the D-7101 fire, the air-failure residual, the spurious ERS closure, the XV-4101 / 4102 / 4107 residual, the open rundown blocked-outlet case and the 31.1 t/h compressors. By Claude (independent review agent), for the human reviewer to confirm at sign-off | The PSV-n131 cases are unchanged. The post-ESD set pressure against the carrier is #2, a set-pressure question, not a sizing one. |

## Items raised against review 8 by its adversarial check

I judged these on the drawn sheets and the control files at HEAD
(`build/adversarial-design-r8.json`).

1. **Missed medium: P-2102 / P-3102 at 10 barg behind one check valve.** Answered. The equipment
   list and both datasheets give 15 barg, for the pump, column, discharge head and minimum-flow tee
   (D-036.4). With the shut-off at ~12.2 barg at the pump, a passing CV-2122 / CV-3122 is no longer an
   overpressure case, and no relief is needed. The reason is sound.
2. **Missed low: the spray source text.** Answered. The SEQ-LOAD S0 operator text and the I-205 /
   I-305 and I-n01 notes now say that the spray comes from the loading header back through LNG-2002.
   P-2102 is held on its check valve on minimum flow, so it takes over without a restart. The reason is
   sound.

## P&ID parts of layout review 6 #2 (trestle drain-down) and its check

The P&ID parts are answered. The status of layout review 6 #2 itself is for the next layout review.
- **(a) Sources.**
  - T4X5 / T4X6 are gone from P-04 (`cheme diff edf00cf0`).
  - LNG-5006 / 6006 end at T50K / T60K downstream of XV-n101 and SR-n102 (`cheme show LNG-5001`:
    XV5101 -> SR5102 -> T50N -> T50K; tiles `build/P-05_tile-B1.png`, `build/P-06_tile-B1.png`), with
    CV-n116 / HV-n117 on them.
  - PI-4105 / 4106 and TI-4103 / 4104 are clamp-on / strap-on in the instrument list. The sheet note
    reads "Trestle side of XV-5101 / -6101: welded, no tapping".
  - The reason is sound. The residual, no line pressure, is #6.
- **(b) Means.**
  - Both N2 stations are drawn (`build/P-04_tile-A2.png`, `B2.png`). Each has: SB, outer block,
    PI-415x, FO-415x, PI-415x, CV-415x, bleed, inner block, then tee T4A6 / T4B6 on the trestle side of
    XV-4101 / 4102.
  - SEQ-LINE-EMPTY has the line-up for either line. The return runs through FV-410x, the tank-end
    crossover where needed, then XV-4105 / XV-2123 (checked against the drawn tank-end tees,
    `build/P-04_tile-B1.png`).
  - The I-n01 / I-n06 output override is defined in both bypass fields.
  - My numbers reproduce the design's. The choked flow through 39 mm at 8 bar(a) and Cd 0.62 is ~1.39
    kg/s (~4,000 Nm3/h). That gas occupies ~450 m3/h at 3.7 bar(a) and ~113 K, which is the liquid
    returned. Gravity drainage of a half-full DN 800 at 0.16 % is ~1,000 m3/h, so the bottom-of-line
    drain path is not the limit.
  - The bottom-of-line intent of T4A4 / T4B4 / T4A5 / T4B5 is on the P-04 note and in the line notes.
    The model limitation (centreline tees, cheme-as-code 1.7.0) is recorded in D-037.16 (d). The
    reason is sound.
  - Where the N2 ends up is stated: at the end it reaches the receiving tank's vapour, the BOG
    compressors and the fuel gas. A few thousand Nm3 of N2 is no hazard there.
  - Overpressure of the line being emptied: site N2 (7 barg) is below the 15 barg design and
    PSV-4111 / 4112.
  - Residuals: the abort and the N2 rate (#3), and the bleeds (#5).
- **(c) Bound.** T-8102 is 170 + 40 = 210 of 257 m3 with no rain allowance, and the PFP is 240 min
  (D-037.2). That is the layout's. #3 gives the N2-rate sensitivity.

## Drawing

`cheme validate` drawing lines at `c257902c`:

- P-01, P-02, P-03, P-05, P-06: every rule 0 (line-through-label, line-crossing, label-overlap,
  label-far-from-owner, text-outside-frame, title-text-overflow, line-through-symbol,
  line-through-valve, line-on-pipe, line-not-orthogonal).
- P-04: 0 line-crossing (+2 accepted: BOG-4011 x LNG-4002 and BOG-4015 x LNG-4002, D-026.11),
  all other counts 0.
- P-07: 0 line-crossing (+2 accepted, D-025), all other counts 0.
- P-08: 0 line-crossing (+1 accepted, D-026.11), all other counts 0.

The accepted crossings are unchanged since review 8, and I agree with their reasons.

Tiles rendered with `cheme render pid/<sheet>.xml --png --tiles auto` (3x3 at scale 8) for P-01, P-03,
P-04, P-05, P-06, P-07 and P-08:
- P-04: A1-C3, all nine read. The N2 stations are in A2 / B2. The bottom-of-line note is in B3.
  PI-4105 / TI-4103 and PI-4106 / TI-4104 sit between the crossover tees in A3 / B3, and ZSC / ZSO-4107
  are in A3.
- P-05: A1, A2, B1, B2, B3, C1 and C2 read. T50K is downstream of XV-5101 and SR-5102 (B1).
  PZT-5181 / 5184 are on the arm side of XV-5131 / XV-5134 (B1 / B2). The note line "PZT-5181 / 5184
  1oo2 5.0 barg: C&E I-502" is in C1 / C2.
- P-06: B1 and B2 read. They mirror P-05.
- P-08: A2, B1, B2, B3, C1, C2 and C3 read. P-8103 with W-8003, TSL-8118, CV-8116 / HV-8117,
  LZT-8106 and TSL-8104 is in C2. P-8102 with CV-8114 / HV-8115, TSL-8102 and LI-8103 is in C1.
- P-07: A1 read. TSL-7115 is on TV-7103.
- P-01 / P-03, crops: `build/P-01_crop-290-50-400-110.png` (FO-1117 as an orifice) and
  `build/P-03_crop-180-190-300-250.png` (TSL-3124 on XV-3123).

No overlap or ambiguous tag was seen in what was read. The clamp-on PI-4105 / 4106 are drawn with
the ordinary bubble, and only the sheet note says "no tapping". That is acceptable at basic.

## Mechanical checks (non-layout)

- `cheme validate`:
  - 93 files, 0 errors, 20 warnings. All 20 are `cheme.hazop-input-changed` in safety/hazop (H-01..H-05
    against P-01, P-03..P-08, the C&E and the sequences), outside this scope. The 9
    `hazop-unknown-tag` of review 8 are gone.
  - The last line compares 10 sheets and 25 lists. It cross-checks equipment, lines and DN,
    instruments, piping items, interlocks, control records, tags in texts, HAZOP, layout,
    datasheets and review records. None reports an error or warning in scope.
- `cheme check --stage basic`, before this record:
  - FAIL design-review: review 8 "changed since aedd8dbdc3c5".
  - FAIL layout-review, outside this scope.
  - Every other gate ok. That includes the new `line-empty-and-sump-level-on-pid`,
    `n2-station-and-carrier-manifold-protection-on-pid` and `dry-sump-pump-on-pid`.
- `cheme control report`: 0 errors, 0 warnings. The sequences and the C&E are "drafted, changed
  since the review of aedd8dbd". The philosophy is "no review record covers it" (#7).
- `cheme validate --only 'cheme.review-*'` after writing this record: 0 errors.

## Checked and fine

- **PZT-n103 at 7.0 barg against normal operation and surge.**
  - Normal on the header is 5.2-5.5 barg at 12,000 m3/h, lower at reduced rates (FV throttling
    upstream) and in cooldown. A pump start in S4 does not approach 7.0 barg.
  - A carrier closure with the link working is answered by I-n01 first. As an uncredited backstop it
    trips on a single manifold-valve closure (~7.3 barg, my estimate), which is the intent.
- **I-n02 at the arms.**
  - 1oo2, with the carrier tripped through the link, so a lost signal to the shore is covered.
  - An arm not connected reads ~0, leaving 1oo1, alarmed.
  - Credited for the link-lost case only, not for a shore closure ahead of the pump stop (I-804
    notes). That is consistent with D-016.
- **I-n01 output override.**
  - Per valve and key-protected.
  - Permitted only with every loading pump proven stopped and XV-5101 / XV-6101 proven closed.
  - Removed by the SIS after S3, after 8 h or on a lost permissive, and defined in both I-501 and
    I-601.
  - A stopped in-tank pump adds no source (bubble-point siphon).
- **P-8103 and I-805..I-808.**
  - Duty: 20 m3/h at 20 m, 2.4 kW at an efficiency of 0.45 (reproduced), design 5 barg against a
    ~26 m shut-off.
  - Logic: I-806 permits only with TSL-8104, TSL-8118 and I-808 healthy; I-807 has priority; I-808 is
    1oo2 on the feeder, latching.
  - I-805 is a cause of both I-501 and I-601, so either transferring carrier is tripped through its own
    link.
  - TSL-8104's tip at 0.40 m (above the start level, below the rim) sees LNG on the pocket water.
- **CV-8116 drain-back hole.** The column and the head drain back through the bowl, since a column of
  ~14 m cannot hold against the atmosphere. The hole drains only the ~0.02 m3 riser spool. Reverse
  flow from a free-discharging jetty drain is not possible. The added cycling (~18 an hour) is the
  vendor's to confirm.
- **P-8102 / W-8002.** CV-8114 then HV-8115 above the cover, SS to HV-8115 (line list).
- **BOG compressors and circulation pumps.** See review 8 #2 and adversarial item 1. The spray in
  loading comes from the loading header; P-2102 runs on minimum flow.
- **P-5101 / P-6101 into the berth header.** The 445 kPa(a) discharge exceeds the header pressure in
  the S3 cooldown (500 m3/h from P-2102, FV-4101 throttling). The CV-n116 / HV-n117 and minimum flow
  are unchanged. D-5101 is emptied before S4, so PSV-5131's surge relief meets an empty drum during a
  transfer.
- **Drip tray detectors.** TSL-3124 on XV-3123 (P-03) and TSL-7115 on TV-7103 (P-07), alarm only.
- **Flowsheet.** S3 is 647.9 kPa(a), the berth header pressure at XV-n101, quoted the same in the
  PZT-n103 notes. process-basic passes.

## Not checked

- Tiles not read:
  - P-05 A3 and C3;
  - P-06 A1-A3, B3 and C1-C3 (they mirror P-05);
  - P-08 A1 and A3;
  - P-01, P-03 and P-07 beyond the crops and tile named above;
  - P-02 (no change since `709fcf20`).
- Transient analyses, for the designer and the vendors (holds H-01, H-02):
  - the carrier closure with an effective closure time shorter than its stroke;
  - the pump trip and run-down at I-n02;
  - the two-phase N2 displacement.

  My surge figures use the slow-closure estimate of D-023.
- Vendor data: the arm-end transmitter, the clamp-on PI qualification, P-8103 (line-shaft bearings
  dry at start, VSD range against the ~16 m static, start count) and the P-8102 motor certificate.
- The site N2 capacity and its back-up, for the trains' utility owner (#3).
- The SIL screening (H-06): I-n02, I-805, I-808 and I-801.
- Outside this scope:
  - the layout, routing, 3D model, PFP, the T-8102 / T-8101 civil design and the layout-review gate;
  - the HAZOP studies (20 warnings, for their owner to restamp against `c257902c`);
  - `process/narrative.md`;
  - the electrical design beyond the motor entries named above, area classification, and the fire and
    gas system (including what else starts the T-8101 foam).
