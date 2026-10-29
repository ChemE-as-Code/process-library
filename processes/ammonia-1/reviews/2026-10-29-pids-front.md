---
topic: pids-front
reviewed_commit: d95ef58124538d5a16f0f1993ece4d436593b708
scope: [pid/P-101.xml, pid/P-102.xml, pid/P-103.xml, pid/P-104.xml, equipment/equipment-list.yaml, piping/line-list.yaml, piping/special-items.yaml, control/instrument-list.yaml, control/cause-effect.yaml, process/flowsheet.yaml, plant.yaml, DESIGN.md]
reviewer: review-agent
reviewer_kind: agent
branch: stage/basic-pids-front
merge: pending
---

# Review: S3a front-end P&IDs of ammonia-1 (PR #246, issue #86), round 1

Independent review of the S3a section of `runs/plan.md`: the P&IDs of blocks REF and SHF
(feed gas, desulphurisation, primary and secondary reforming, waste-heat recovery, HT/LT shift).
The gates are pids-exist, pids-valid (0 errors), drawing-clean, process-basic and
process-links, and every section of the PFD must be on a sheet. Reviewed at d95ef58, 4 commits
on main c225f48.

## What changed (`cheme diff origin/main --list`, 280 lines; excerpt)

```
pid/P-101.xml: (sheet added)
added SwingCheckValve CV1005: 10 added, 0 removed, 0 modified
added GlobeValve FV1002 [FV-1002]: 10 added, 0 removed, 0 modified
added GlobeValve FV1006 [FV-1006]: 10 added, 0 removed, 0 modified
added ProcessInstrumentationFunction Inst_FZ1007 [1007]: 19 added, 0 removed, 0 modified
added ActuatingSystem Inst_US1001_System [XV-1001]: 6 added, 0 removed, 0 modified
added PipingNetworkSystem Line_NG1004 [NG-1004]: 22 added, 0 removed, 0 modified
added Vessel R100 [R-100]: 24 added, 0 removed, 0 modified
added Vessel V101 [V-101]: 24 added, 0 removed, 0 modified
added BallValve XV1001 [XV-1001]: 10 added, 0 removed, 0 modified
...
pid/P-102.xml: (sheet added)
pid/P-103.xml: (sheet added)
pid/P-104.xml: (sheet added)
```

The other changed files: the lists (`sheet:` on 22 equipment items, E-106 retyped; 51 lines;
44 instruments; new `piping/special-items.yaml`), `control/cause-effect.yaml` (I-101 to I-104,
proposed), 36 `line:` links in `process/flowsheet.yaml` (links only, no stream value changed),
the regenerated BFD, PFD and `layout/plant-model.yaml` (no layout input file changed), D-027,
PROGRESS.md, the four provenance scripts `scripts/draft_P-10x.py` and the run record.

## Checks re-run (at d95ef58)

- `cheme validate`: 29 files, **0 errors**, 110 warnings. The PR body says 106. The 4 extra are
  `cheme.generator-undeclared` (info level in the text output, counted in the JSON) for the
  provenance scripts. That is expected for hand-maintained sheets, so it is not a finding. The
  rest are `cheme.layout-*` warnings (layout is S5's) and the known K601
  `process-energy-balance` from S2. Drawing lint is 0 on every count for P-101 to P-104.
  `equipment-not-on-pid` lists only items of S3b/S3c, so every REF/SHF item is drawn.
- `cheme check`: pids-exist, pids-valid, drawing-clean, process-basic and process-links are
  **ok**. design-review, layout-3d, lifting-study, mto, maturity-balanced and layout-review fail,
  as on main. They belong to later sections and none of them was relaxed.
- `cheme maturity`: calculation maturity none, unchanged from S2 (sourced-boundary and
  model-basis; finding 2026-10-29-simulation#1).
- Rendered P-101 to P-104 (`cheme render --png`) and looked at each sheet whole. The sheets are
  legible, the off-page texts name the other sheet or item, and the flue-gas coil order matches
  the duties and temperatures.

## Engineering assessment

- **Line sizes**: I recomputed the first-pass DN from the design-case stream table with the
  stated ideal-gas basis:
  - NG-1001 (S1, 37.7 t/h at 4500 kPa(a), 288 K): 0.32 m3/s, about 142 mm at 20 m/s, so DN 150 is right.
  - PG-1006 (S8, 122 t/h at 4250 kPa(a), 773 K, M about 17.9): 2.9 m3/s, about 430 mm, so DN 450 is right.
  - PA-1030 (S12): about 1.14 m at 15 m/s, so DN 1200 is right.
  - SM-1005 (S6): about 0.27 m at 30 m/s, so DN 300 is right.
  - CA-1011 (S61): about 1.8 m, so DN 1800 is right.
  - FL-1014 (S65, 1323 K): about 4.0 m, so DN 4000 is right.
  - PC-1048 (S25): about 0.11 m at 1.5 m/s, so DN 125 is right.

  The exceptions are the waste-heat-boiler risers (#1) and the cooling-water velocity (#4).
- **Spot-check of the cited values** (no new external source in this section; the values come
  from D-014/D-015 and the S2 stream table):
  - E-106 288 -> 523 K (D-014) matches S61/S63.
  - The 1323 K bridgewall matches S65.
  - The E-105 duty used for the downcomer (Q10 74.0 MW) and the E-203 duty in the CW note (Q16 34.7 MW) are the simulated values.
- **Provenance**: the velocities, circulation ratios and the DN with no stream behind them are
  marked ASSUMED in D-027 and in the line notes. PSV set pressures and relief cases are left
  empty with the reason, not guessed. The trips are proposed for S4/S6.
- **Licences**: the sheets are generated from our own scripts with cheme's catalogue shapes. No
  third-party content was found.
- **Scope**: kept to S3a. The flowsheet edit is links only. The E-106 retype changes S1's list
  and is recorded in D-027. The equipment class matches the drawing.
- **Control and trips**: the basic loops are drawn and sensible:
  - feed flow, with steam-to-carbon ratio;
  - fuel pressure reset by the reformer outlet temperature;
  - excess air by O2 on the air flow;
  - draft on the ID fan;
  - process air on suction throttle, with anti-surge blow-off and PSV upstream of the discharge check valve;
  - HTS inlet temperature by the WHB hot bypass;
  - separator level;
  - cooler outlet temperature.

  Two of the four proposed trips have gaps a HAZOP will raise; it is better to record them now
  (#2, #3).

## Findings

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-29-pids-front#1 | P-103 | `piping/line-list.yaml` SM-1038, SM-1040 | The waste-heat-boiler risers are smaller than their downcomers: SM-1038 is DN 300 against BW-1037 DN 450, and SM-1040 is DN 125 against BW-1039 DN 200. The note says "DN ASSUMED as BW-1037", which is not what was entered. At the stated circulation ratio 5 and MP steam (about 4.6 MPa), E-105 (Q10 74.0 MW) sends about 45 kg/s of steam with about 180 kg/s of water up the riser. That is about 2.1 m3/s, or about 30 m/s in DN 300. E-201 (Q13 12.2 MW) gives about 28 m/s in DN 125. A natural-circulation riser carries the two-phase volume and is normally at least as large as the downcomer. At these sizes the circulation the downcomers are sized for would not establish. | medium | open | Size the risers on the homogeneous two-phase volume at the drum pressure, at a riser velocity of a few m/s (ASSUMED). That gives about DN 600 or more for SM-1038 and DN 300 for SM-1040, or several risers. Then `cheme set` the DN on P-103 and update the notes. |
| 2026-10-29-pids-front#2 | P-101, P-102 | `control/cause-effect.yaml` I-101; P-101 T1001 | I-101 (process steam low-low) closes XV-1001 and XV-1204, but not the tail-gas trip valve XV-1105. Because the fuel split T1001 is downstream of XV-1001, XV-1001 also cuts the natural-gas fuel, which is not written in I-101 or D-027. The tail-gas burners (FG-1010, 2.8 t/h) then keep firing the radiant box with no process flow through R-101. That is the classic tube-overheating case. | medium | open | Add `{tag: XV-1105, action: close}` to I-101 (or "initiates I-102"), still proposed. Write in D-027/I-101 notes that XV-1001 is upstream of the fuel split and is therefore also the main fuel isolation. The HAZOP (S6) and burner management can then confirm or change this. |
| 2026-10-29-pids-front#3 | P-104 | `control/cause-effect.yaml` I-104; V-201 | I-104 uses the control valve LV-1307 of LIC-1307 as its final element. A failure of the LIC-1307 loop is the most likely cause of high level, so the trip is not independent of it. Its other effect is an alarm on the cause tag itself. The opposite case is not covered at all: no low-low level protection against gas blow-by from V-201 (3100 kPa(a), H2-rich) through PC-1048 into the condensate stripper in U-801. That case is often the governing relief case of the downstream system. | medium | open | Record in I-104's notes and in D-027's open items that LV-1307 is not independent. Name the blow-by case (V-201 low-low level, gas breakthrough into U-801) as an open item for S4/S6/S8, or propose an LZ low-low closing an independent XV on PC-1048. Do not invent its tag numbers on the sheet before the control work. |
| 2026-10-29-pids-front#4 | P-103, P-104 | `piping/line-list.yaml` header; CWS/CWR-1041/1042, -1052/1053 | The stated liquid velocity basis is 1.5 m/s, but the CW lines are sized at about 2 m/s. CWS-1052 at Q16 34.7 MW and 10 K rise carries 0.83 m3/s, which is 2.2 m/s in DN 700 (DN 850 at 1.5 m/s). CWS-1041 at Q2 6.0 MW runs at 2.0 m/s in DN 300. 2 m/s is a normal CW velocity, but the basis as written does not reproduce the numbers. | low | open | State the CW velocity (for example 2 m/s ASSUMED) in the line-list header and in D-027, or resize to the stated basis. |
| 2026-10-29-pids-front#5 | P-102 | `control/instrument-list.yaml:28`; line-list CA-1013 note; P-102 FV1108 | The combustion-air damper of FIC-1110 is tagged FV-1108. Loop number 1108 already belongs to PZ-1108 (furnace pressure trip), so the final element carries another loop's number. | low | open | `cheme rename FV-1108 FV-1110 --tag` (or the tag form that `cheme rename` documents), then update the instrument-list service text and the CA-1013 note. Then run `cheme fmt` and `cheme validate`. |
| 2026-10-29-pids-front#6 | - | `equipment/equipment-list.yaml` E-203, E-105 notes | The notes still give the concept duties: E-203 31.2 MW against the simulated Q16 34.7 MW, and E-105 73.5 MW against Q10 74.0 MW. The S3a line list already uses the simulated values, so two files of this branch disagree. This dates from S2, but S3a touched these entries. | low | open | Update the duties in the notes to the simulated values, or point to the energy stream (Q10, Q16), so the list does not keep a second copy of the numbers. |

## Previous findings

| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-29-simulation#1 | maturity-balanced fails on model-basis (assumed conversions, sourceable) | medium | open | reaction-evidence.yaml and flowsheet values unchanged on this branch; `cheme maturity` still fails model-basis |
| 2026-10-29-simulation#2 | D-026 maturity list omits energy-closure; "not a core limit" too strong | low | open | D-026 unchanged (only D-027 appended) |
| 2026-10-29-simulation#3 | R102B/R201/R202 bed residual duties about 0.9 MW | low | open | simulation.yaml unchanged |
| 2026-10-29-simulation#4 | adjust/design-spec core limit without a core issue; E-107/S66 | low | open | unchanged |
| 2026-10-29-concept#1 | X-601 32 m from A-900 without a separation criterion | medium | open | layout input files unchanged (only the generated plant-model.yaml) |
| 2026-10-29-concept#2 | TEA: DMW, BD, CW free without `free:` | low | open | estimate/tea.yaml unchanged |
| 2026-10-29-concept#3 | steam credit omits the avoided carbon cost | low | open | estimate/tea.yaml unchanged |
| 2026-10-29-concept#4 | ETS price cited from a secondary source | low | open | estimate/tea.yaml unchanged |
| 2026-10-27-pfd-lci-review#3 | R-03: natural-gas composition and supply pressure not sourced | medium | open | S1 still ASSUMED |
| 2026-10-27-pfd-lci-review#5 | R-05: block reaction extents not unique | low | open | unchanged |

## Not drawn yet (accepted for this revision, recorded in D-027)

These are open in D-027 for S4, S5 and S8, and are not findings at this revision:

- relief on the reformers, converters and waste heat boilers (design pressures not set);
- H-101 burner management;
- block and bypass valves at the control valves;
- vents, drains and sample points;
- the K-101 intercoolers and drive;
- the stack;
- U-801.

## Verdict

No critical or high finding is open. The five S3a gates pass on my re-run, and every REF/SHF
item and step is on a sheet. **Approve**; merge to `main`. Findings #1 to #3 should be closed
before the basic design review (S5r). #2 and #3 are inputs to S4/S6.
