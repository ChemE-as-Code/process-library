---
topic: control-lists
reviewed_commit: 74e46623c678a30f2e1ca0bb05e6ec75cff8be54
scope: [control/loops.yaml, control/sequences.yaml, control/cause-effect.yaml, control/philosophy.md, process/narrative.md, control/instrument-list.yaml, pid/P-109.xml, pid/P-113.xml, DESIGN.md]
reviewer: review-agent
reviewer_kind: agent
branch: stage/basic-control-lists
merge: pending
---

# Review: S4 control and lists of ammonia-1 (PR #255, issue #86), round 1

This is an independent review of section S4 of `runs/plan.md`. The target is: the lists complete
and linked (validate clean); control loops, sequences, interlocks and cause and effect, with
`cheme control report` clean; and the PFD current. I reviewed commit 74e4662, which is 3 commits
on top of main 2bef879: 10ebc30 (P&ID and list alignment), 410bbc7 (control records) and
74e4662 (run record).

## What changed (`cheme diff origin/main --list`)

```
pid/P-109.xml:
removed ProcessInstrumentationFunction Inst_AI1804 [1804]: 0 added, 19 removed, 0 modified
added ProcessInstrumentationFunction Inst_AIC1804 [1804]: 19 added, 0 removed, 0 modified
changed PlantModel PlantModel1: 0 added, 0 removed, 1 modified
pid/P-113.xml:
changed PlantModel PlantModel1: 0 added, 0 removed, 1 modified
```

Other files changed: `control/loops.yaml` (+755 lines, 38 loops), `control/sequences.yaml`
(5 sequences), `control/cause-effect.yaml` (I-101 to I-107 completed; I-104 no longer opens
LV-1307), `control/philosophy.md`, `process/narrative.md`, `control/instrument-list.yaml`
(AIC-1804), `layout/plant-model.yaml` (P&ID hashes only), DESIGN.md D-030, PROGRESS.md and the
run record. The scope matches the section. The flowsheet and the PFD did not change.

## Checks re-run

- `cheme validate`: 0 errors, 238 warnings. Apart from the `cheme.layout-*` warnings (S5) and the
  S2/S3 carry-overs, no `equipment-*`, `line-*`, `instrument-*`, `piping_items` or
  `process-link*` finding is reported. Every sheet has drawing counts of 0.
- `cheme validate --only 'cheme.control-*'`: 0 errors, 0 warnings, 4 info
  (`cheme.control-logic-text`, sequences.yaml:44, 138, 193, 265). These are the start-up
  nitrogen, the front-end vent to flare (x2) and the converter start-up heater, none of which
  is drawn.
- `cheme control report`: 0 errors, 0 warnings, 4 info. All five control files are "drafted".
- `cheme check`: the basic gates that are S4's pass (process-basic, process-links, pids-valid,
  drawing-clean, pids-exist), and so does the detail gate control-complete. The gates that fail
  belong to other sections: design-review, layout-3d, lifting-study, mto, maturity-balanced,
  layout-review, layout-detail, electrical and datasheets. These results match the PR body.
- The target "`cheme control report` without findings" is **not fully met**: 4 info findings
  remain. The PR says so and does not hide them. Each one names a P&ID connection that is truly
  missing, and rewording them into operator notes would only hide the gap. I accept this as
  honest reporting of a P&ID gap. It is not a relaxed gate: none of the plan's gates counts
  info-level findings, and control-complete passes.

## Engineering spot checks

I checked these values against `cheme process streams`:

- FIC-1002 setpoint 29,508.3 kg/h = S3 [C]. FIC-1110 165,407 kg/h = S62 [C]. TIC-1803
  493.843 K = S42 [C]. FIC-1905 1693.02 kg/h = S50 [C]. The setpoints marked calculated are
  calculated in the flowsheet. The setpoints marked assumed (S6, S12, S11, S18, S20 and others)
  are [A] there.
- Ratios: S6/S3 = 92,833.6/29,508.3 = 3.146 and S12/S3 = 67,184.1/29,508.3 = 2.277, both as
  written. The start-up step values agree with these ratios: 27,850/8,850 = 3.147.
- AIC-1109 O2 1.69 mol% = S66 O2 0.0169069 (wet basis). AIC-1804 H2/N2 0.634735/0.211061 = 3.007.
- FIC-1407 1313 m3/h: S28 carries about 72.9 t/h of CO2, and 72.9 x 18 m3/t = 1312 m3/h.
- FIC-2106: 386.8 kW / 2120 kJ/kg = 656.8 kg/h. h_fg of water at 450 kPa(a), about 421 K, is
  about 2120 kJ/kg (steam tables). The basis is checked in L1 below.
- Controller actions and fail positions are plausible: AIC-1804 is direct, because a high H2/N2
  calls for more air. FV-1006 steam fails open and FV-1002/FV-1201 fail closed. The damper fails
  open. The shift bypasses fail closed, which gives a cooler bed. TV-1803 is the cold-side
  bypass of E-501, so failing open gives a cooler converter feed. The level valves between
  pressure levels fail closed. The ratio, cascade and mode transitions are consistent.
- I-104: dropping LV-1307 as the trip element is correct, because a trip acting on the loop's
  own valve is not independent of that loop. This closes the trip-element part of
  pids-front#3.
- Provenance: the new numbers are either linked to a stream or marked ASSUMED in D-030. No
  setpoint, delay or bypass timer is presented as data. No SIL was written, so S6 keeps it.
- Sources: the strategy is attributed to skill `control-loops` (after Toghraei). The narrative
  and philosophy text is the project's own. I found no copied third-party text, table or figure.

## Findings

| id | file / line | finding | severity | status | fix |
|---|---|---|---|---|---|
| 2026-10-29-control-lists#1 | control/sequences.yaml:19, 111, 163 | Start permissives require trips to be reset while their causes are still present. SEQ-START-REF asks for I-101 "reset" before step S1, but I-101 trips on process steam low-low flow (FZ-1007) and no steam flows until S3. I-101 is latching with manual reset, so it cannot be reset at that point, and the sequence can never start. The C&E bypass text for I-101 ("healthy before feed gas is admitted, because steam is established first") assumes the trip is armed later, which contradicts the permissive. SEQ-START-CO2R (I-105, empty sump) and SEQ-START-SYN (I-107, empty separator) have the same conflict: their start-up bypasses are granted at step S1 or S5 entry, after the permissive has already required the reset. | medium | open | Make the permissive the trip's output state (XV-1001 / XV-1406 / XV-1904 closed, first-out acknowledged) and not "reset". Then either reset I-101 in S3 once the steam flow is above the trip point (and say so in the I-101 `reset`/`bypass`), or grant the I-105/I-107 start-up bypass as a permissive step before S1. |
| 2026-10-29-control-lists#2 | DESIGN.md:777, control/loops.yaml, control/philosophy.md | No loop controls the front-end pressure or the capacity of K-501. The front end makes gas at the rate FIC-1002 sets, and K-501 takes it with only anti-surge control (UIC-1703). Nothing balances the two, and no front-end vent is drawn (D-030). Normal operation therefore has no inventory control between the front end and the loop. On a K-501 trip (F-K501), in SEQ-SD-PLANT S2 and in SEQ-TRIP-FE S3, the front end is blocked in at load until PSVs lift, and after I-103 the gas keeps flowing at FIC-1002's last output. D-030 rejects "a loop pressure controller on the make-up (K-501 capacity) without a turndown case to size it", but a capacity or pressure loop does not need a turndown case to exist. It also leaves the front-end pressure out of the "open" list altogether. | medium | open | Name the front-end pressure strategy in D-030 and in philosophy.md. The usual answer is K-501 speed or suction-pressure control with a front-end vent PIC to flare at start-up and on upsets. List it as an open P&ID item with the vent (or as a plant.yaml issue before the basic gate). Correct the rejection reason. |
| 2026-10-29-control-lists#3 | control/loops.yaml:657 | The FIC-2106 LP steam setpoint of 657 kg/h divides Q29 by the latent heat at saturation (2120 kJ/kg). The LP header, however, is let down from MP steam at 4600 kPa(a) and 673 K through PV-2206, with no desuperheater drawn. Isenthalpic let-down gives about 3200 kJ/kg, so the steam condensing to saturated liquid at 450 kPa(a) gives up about 2580 kJ/kg, which is about 540 kg/h. The value is ASSUMED and labelled, but the stated basis is not that of the drawn system. | low | open | State the steam condition (saturated, which implies an open desuperheater, or let-down superheated) in D-030, and recompute or note the difference. |
| 2026-10-29-control-lists#4 | control/sequences.yaml:355, 359 | SEQ-TRIP-FE aborts into SEQ-SD-PLANT, whose permissives need FIC-1002 in auto and FIC-1006 in cascade. SEQ-TRIP-FE S1 has just put FIC-1002 in manual, so those permissives cannot be met. SEQ-TRIP-FE is entered on I-105 or I-106, but its reset condition checks only I-101 to I-103. | low | open | Give SEQ-SD-PLANT a path from the tripped state (or abort to a hold step), and include I-105 and I-106 in the reset condition. |
| 2026-10-29-control-lists#5 | control/loops.yaml:491 | The AIC-1804 setpoint is 3.0 with provenance `calculated`, but 3.0 is the stoichiometric target, rounded from the simulated 3.007. | low | open | Mark it `assumed` (design target, stoichiometric) and cite 3.007 as the simulated check, or use 3.007. |
| 2026-10-29-control-lists#6 | (process) | Two edits to control/loops.yaml were made with `sed -i` and a script, which breaks AGENTS.md's "Edit and Write only" rule. The PR body discloses this, the committed file validates, and I found no damage in the diff. | low | open | No change to the file is needed. Keep to Edit/Write in the fix round. |

## Previous findings

| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-29-pids-loop#1 | E-502 riser SM-1101 smaller than downcomer | medium | open | line list unchanged |
| 2026-10-29-pids-loop#2 | tube-rupture cases of E-504, E-503, E-701, E-502 not listed | medium | open | D-029/D-030 unchanged on this |
| 2026-10-29-pids-loop#3 | loop equipment notes carry pre-simulation values | low | open | equipment list unchanged |
| 2026-10-29-pids-loop#4 | PSV-2210 silencer only in connector text | low | open | P-113 change is the LIC note only |
| 2026-10-29-pids-front#1 | SM-1038/SM-1040 risers smaller than downcomers | medium | open | unchanged |
| 2026-10-29-pids-front#2 | I-101 does not close the tail-gas XV-1105; fuel cut not written | medium | open | I-101 effects still XV-1001, XV-1204 (cause-effect.yaml:11-14); S4 edited I-101 without addressing it |
| 2026-10-29-pids-front#3 | I-104 uses LV-1307 as its trip element; no V-201 LL blow-by protection | medium | open (partly closed) | trip element removed in 410bbc7 (closed); the V-201 low-low blow-by protection is still absent, and LIC-1307 failing closed is the only layer |
| 2026-10-29-pids-front#4 | CW velocity basis 1.5 m/s written, about 2 m/s used | low | open | unchanged |
| 2026-10-29-pids-front#5 | FV-1108 carries PZ-1108's loop number | low | open | loops.yaml FIC-1110 uses FV-1108 as its final element; still mismatched |
| 2026-10-29-pids-front#6 | E-203/E-105 notes give concept duties | low | open | unchanged |
| 2026-10-29-simulation#1 | maturity-balanced fails on model-basis | medium | open | `cheme check` maturity-balanced FAIL |
| 2026-10-29-simulation#2 | D-026 maturity list omits energy closure | low | open | unchanged |
| 2026-10-29-simulation#3 | R102B/R201/R202 bed residual duties about 0.9 MW | low | open | unchanged |
| 2026-10-29-simulation#4 | adjust/design-spec core limit without a core issue | low | open | unchanged |
| 2026-10-29-concept#1 | X-601 32 m from A-900 without a separation criterion | medium | open | unchanged |
| 2026-10-29-concept#2 | TEA: DMW, BD, CW free without `free:` | low | open | unchanged |
| 2026-10-29-concept#3 | steam credit omits the avoided carbon cost | low | open | unchanged |
| 2026-10-29-concept#4 | ETS price from a secondary source | low | open | unchanged |
| 2026-10-27-pfd-lci-review#3 | natural-gas composition and supply pressure not sourced | medium | open | still ASSUMED |
| 2026-10-27-pfd-lci-review#5 | block reaction extents not unique | low | open | unchanged |

## Verdict

No critical or high finding is open. On my re-run, the S4 targets pass as the plan states them:
validate is clean and the lists are linked, there are 38 loops, 5 sequences, the completed C&E,
the narrative and the philosophy, and the PFD is current. The one exception is the 4
`control-logic-text` info findings. They point at P&ID connections that are honestly listed
open in D-030, and no gate counts them. The two new medium findings are a sequence-logic
conflict and a missing front-end pressure strategy. Both are fixable in the records and D-030,
and they should be closed before the basic design review (S5r) and the HAZOP (S6). They do not
block the merge of this section.

VERDICT: approve
