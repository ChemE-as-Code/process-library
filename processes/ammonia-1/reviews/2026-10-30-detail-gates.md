---
topic: detail-gates
reviewed_commit: e8283d99a93cebb7734211132bc17ddf1d48ed77
scope: [layout/, electrical/, piping/routing.yaml, checks/checks.yaml, estimate/mto.csv, estimate/mto.md, DESIGN.md, PROGRESS.md]
reviewer: review-agent
reviewer_kind: agent
branch: stage/detail-gates
merge: pending
---

# Detail gates review of S9, round 1

This record reviews PR #264 (`stage/detail-gates`), section S9 of runs/plan.md, at e8283d9. The
PR is stacked on `stage/basic-layout` (PR #257, open). The section's target is to take the
detail-stage gates as far as they go and to report pass or fail per gate. Since the base, there
are three engineering commits (d58ee64 CW routing D-038, 077c83f electrical and HVAC D-039,
5247884 datasheets gate `require:` enabled) and the run record.

## What changed

```
$ cheme diff origin/stage/basic-layout --list
No P&ID changed.
```

Files: DESIGN.md (D-038, D-039), PROGRESS.md, checks/checks.yaml (datasheets `require:`),
electrical/electrical-list.yaml (new), electrical/cable-schedule.* (new), layout/building.yaml
(new), layout/hvac.yaml (new), layout/structures.yaml (new, VP-TV-1306),
layout/equipment-placement.yaml (four CW nozzle overrides), piping/routing.yaml (CW battery
limits, header routes, branch depths and vias, AM-1062), and the regenerated plant-model,
lifting-study and mto files.

## Checks re-run by the reviewer

| command | result |
|---|---|
| `cheme validate` | 0 errors, 239 warnings (as the PR states) |
| `cheme check --stage detail` | layout-detail FAIL (4 `layout-headroom`, buried CW header road crossings); electrical FAIL (8 `layout-tray-fill`); hvac ok; control-complete ok; datasheets FAIL (dimensions 51, weights and nozzle schedules 52); issues-detail n/a. Basic: layout-3d FAIL (the same 4 headroom findings), lifting-study FAIL (12), maturity-balanced FAIL, design-review and layout-review stale |
| `cheme maturity` | calculation maturity none; unchanged by this PR |
| `cheme layout build --check` | "layout/plant-model.yaml is not up to date" in this environment (cheme 1.0.1). The input hashes and generator hash are identical, and two rebuilds here are byte-identical to each other. They differ from the committed file in support posts and in rounding of coordinates and lengths. Findings are unchanged. See #6 |
| `cheme layout build` findings | the same 4 headroom, 8 tray-fill and 19 tray-span warnings as the PR reports |
| `gh pr checks 264` | green |

The PR body's per-gate table matches what I found. No gate was relaxed, skipped or accepted. The
datasheets `require:` line is the template's commented detail requirement, enabled because the
section's target names that gate (runs/plan.md). That tightens the gate.

## Engineering checks

- **Cited values (spot checks).** `fluid_power_kw` is K-101 8567.9, K-501 12722.9, K-701 11128.2
  and K-102 260.0 kW, and `shaft_power_kw` is P-301A 1539.5 kW. These equal the datasheets'
  values and sources (equipment/datasheets/*.yaml). S28 is 74,528.4 kg/h [C] in
  `cheme process streams`. The line list gives CWS-1144 and CWR-1145 as DN 1400 and
  CWS-1052 and CWR-1053 as DN 700.
- **HVAC arithmetic.** 1.2 x 1.006 x 10 / 3600 = 0.00335 kW per m3/h, so 298 m3/h per kW is
  correct. SWG-1 has 5960 m3/h in about 1260 m3, about 4.7 air changes per hour. Each AHU's
  capacity covers its rooms (12,000 against 9,840, 8,000 against 5,960 m3/h).
- **P-302 estimate.** 30.5 t/h of reflux is 74,528 / 44.01 x 18.015. S28 is 5 mol % water, so
  the CO2 is 1657 kmol/h and the reflux 29.9 t/h, about 2 % less. That is immaterial at 7.6 kW;
  noted, not a finding.
- **Electrical load.** The motors sum to about 38.1 MW connected, with the spare P-301B
  included. With about 36.6 MW running at pf 0.9 (about 41 MVA), 2 x 50 MVA with one standby
  is consistent. Currents in the schedule use pf x efficiency of about 0.78.
- **Water weight in D-038.** pi/4 x 1.4^2 x 1000 = 1539 kg/m, which agrees with "1.5 t/m".
- **CW battery limits.** Supply west and return east, a reverse return as P-114 draws it. The
  header routes are given because of the stated core limit (a chain with a battery limit at
  both ends). I checked the routes against routing.yaml.
- **Provenance.** Every new voltage, rating, depth, load and size is marked ASSUMED, with a
  source or a reason. No third-party content was copied, and no new external source is cited.
- **Scope.** This is layout, electrical and HVAC work for the detail gates. No P&ID, list or
  process file changed.

## Findings

New in this round:

| id | file:line | what is wrong | severity | status | fix |
|---|---|---|---|---|---|
| 2026-10-30-detail-gates#1 | piping/routing.yaml:355-374; DESIGN.md D-038; layout/lifting-study.csv | **This PR makes two basic-stage gates worse on the branch it merges into.** layout-3d passes on `stage/basic-layout` and fails here, on the 4 buried road-crossing headroom findings. lifting-study goes from 8 to 12 findings: the motor branch trays of K-101, K-102, K-103 and K-701 now run over the machines and block the overhead lift. The headroom findings are false positives of a core rule (v1.0.0 `model_rules.headroom` has no buried case). Neither the author nor this review accepts them (runs/plan.md). The lifting findings are real obstructions. Merged into `stage/basic-layout` before its sign-off, this PR would block that sign-off on layout-3d, which passes today. | medium | open | Merge order: merge S9 only after the basic sign-off is on main, then retarget the PR to main. Do not merge it into `stage/basic-layout` while that branch waits for its sign-off. Open a core issue for buried pipes under roads. For the four lifting findings, enter the motor cable from the side away from the lift (a tray rule, a structure or a local cable riser), or list them in the lifting acceptance proposal with their reason. |
| 2026-10-30-detail-gates#2 | piping/routing.yaml:333-354; layout/plant-model.yaml:26479, :26496, :26530; DESIGN.md D-038 | **Some "buried" CW branches are not buried in the model.** CWS-1063 (DN 400) runs 8.5 m at +0.2 m centreline at x 208.2, y 108.5-117, which puts it on grade across the PR-1 strip. CWS-1052 (DN 700) rises to -0.3 m centreline twice, so its top is above grade, at x 205-207 and at x 219.6. CWS-1085 (DN 500) runs at -0.8 m, with about 0.55 m cover. D-038 states 1.8 m for all branches, and the model counts these lines as routed. The PR body names this only as open item 4, and D-038 does not record it. | medium | open | Give the crossing branches vias at a second depth (lanes and crossings at different levels below the 1.8 m runs, clear of the 3.0 m headers). Or record the depth exceptions in D-038 with the reason, and say how the rack strip stays passable. |
| 2026-10-30-detail-gates#3 | layout/plant-model.yaml:24358-24382 (CWS-1091, CWR-1092); DESIGN.md D-038 (last sentence) | **CW supply and return of K-101, K-501 and K-701 share one nozzle point, so the two routes overlap.** CWS-1091 and CWR-1092 both end at [181.377, 42.146, 6.0], and each makes an up-and-over loop to 6.9 m through the other. That is not a physical arrangement, yet layout-detail counts both lines as routed. D-038 leaves them "as they are". | medium | open | Separate the CW inlet and outlet with nozzle overrides in layout/equipment-placement.yaml, as this PR already did for E-203, E-302, E-402 and E-701. Then re-route and rebuild. |
| 2026-10-30-detail-gates#4 | DESIGN.md D-039 ("274 cables"); PR body | **The cable count is misstated.** electrical/cable-schedule.csv has 180 cables: 11 power, 158 instrument pairs and 11 multicores from RR-1 to the junction boxes. D-039 and the PR body say 274. | low | open | Correct D-039 to 180 cables, by kind. |
| 2026-10-30-detail-gates#5 | electrical/electrical-list.yaml:144-162; electrical/cable-schedule.md | **The motor ratings and catalogue cable sizes understate what the electrical design will need, so the tray fill is a lower bound.** Motor ratings equal the gas power, with no mechanical loss and no motor margin; a nameplate is usually about 10 % above shaft power. P-302A/B are fed at 400 V over about 400 m on 4C x 2.5 mm2, a voltage drop of about 15 % running. The 10 kV feeders of 35 mm2 do not withstand a fault level of about 20+ kA from 50 MVA transformers. | low | open | Say in D-039 that the tray fill is a lower bound. Have the electrical design size the cables on voltage drop and short-circuit withstand. Consider a local LV supply for the far pumps. |
| 2026-10-30-detail-gates#6 | layout/plant-model.yaml (provenance `output_sha256`) | **The committed model does not reproduce here.** `cheme layout build --check` reports it out of date with identical source and generator hashes, and two rebuilds here agree with each other. The differences are support posts and the third decimal of coordinates. Gate findings are unchanged, and the run toolchain is core v1.0.0 against cheme 1.0.1 here. | low | open | Record the cheme version in the run record. If CI or the sign-off job builds with another version, rebuild there before the sign-off so that `--check` is clean. |
| 2026-10-30-detail-gates#7 | electrical/electrical-list.yaml:121-130; layout/building.yaml; layout/hvac.yaml | **The substation yard and the control room's gas protection are not placed.** SS-1, with its 150 kV intake and 2 x 50 MVA oil transformers, is attributed to ECB-1, but the four rooms fill the building and no transformer yard (fire separation, access) is in the layout. The control room's outdoor air (LV-IN, east wall, about 6 m from a rack that carries NH3) has no NH3 detection or damper trip in the C&E. building.yaml defers both to the occupied building assessment. | low | open | Add the transformer yard as an area or zone in A-900, or state in D-039 that it is outside the model. Raise the HVAC-intake NH3 detection and isolation as an action for the C&E and the occupied building assessment. |

## Previous findings

Open findings of earlier records whose scope overlaps this one (DESIGN.md, layout/). This PR
does not address them, apart from what is noted.

| id | finding | severity | status | evidence at e8283d9 |
|---|---|---|---|---|
| 2026-10-29-design#1 | S5 targets not met: lifting-study and maturity-balanced fail, no class 4 estimate | high | open | Finding of the base PR #257, waiting for the owner's decisions. Re-run here: lifting-study FAIL (now 12, see #1) and maturity-balanced FAIL. This PR does not touch it. It blocks the basic sign-off, not this section. |
| 2026-10-30-layout-s5b-r3#1 | E-301 and V-701 lanes clear only by a pipe over the pad | medium | open | zones.yaml unchanged |
| 2026-10-30-layout-s5b-r3#2 | proposal gives the withdrawn licence reason | low | open | unchanged |
| 2026-10-30-layout-s5b-r3#3 | DW-1073 undrained pocket and unsupported risers | low | open | routing unchanged there |
| 2026-10-30-design-s5b-r3#1 | D-035 says no bulk estimate is written | low | open | design topic |
| 2026-10-30-design-s5b-r3#2 | mixed factor bases, small-project D&E | low | open | design topic |
| 2026-10-30-design-s5b-r3#3 | "40 kW" without a locator | low | open | design topic |
| 2026-10-30-design-s5b#2 | steam-system package sensitivity unexplained | medium | open | design topic |
| 2026-10-30-design-s5b#5 | PR #257 body is the S5 round-0 text | low | open | base PR |
| 2026-10-30-layout-r3#1 | Z-HAZ-FUEL misses the fuel and tail-gas valve trains | medium | open | zones.yaml unchanged |
| 2026-10-29-layout#3 | take-off without pipe classes or insulation, utility piping left out | medium | open | utility CW piping is now in the take-off; classes and insulation are still missing |
| 2026-10-29-layout#5 | ladder, cage and walkway access defects | medium | open | warnings still reported |
| 2026-10-29-layout#6 | toppling criterion dropped for area racks, untracked | medium | open | plant.yaml has no `issues:` |
| 2026-10-29-layout#7 | blocked bundle pulls and valves out of reach untracked | low | open | E-701 T1 moved out of the pull space and TV-1306 given a platform; the rest is unchanged |
| 2026-10-29-layout#8 | hand-corrected pinned routes step up and down | low | open | unchanged |
| 2026-10-29-concept#1 | X-601 32 m from A-900 without a separation criterion | medium | open | A-900 now holds ECB-1 with the control room, so this now concerns an occupied building |
| 2026-10-29-concept#2 | TEA: DMW, BD, CW free without `free:` | low | open | not in this scope |
| 2026-10-29-concept#3 | steam credit omits the avoided carbon cost | low | open | not in this scope |
| 2026-10-29-concept#4 | ETS price from a secondary source | low | open | not in this scope |
| 2026-10-27-pfd-lci-review#3 | natural-gas composition and supply pressure not sourced | medium | open | maturity sourced-boundary still fails |
| 2026-10-27-pfd-lci-review#5 | block reaction extents not unique | low | open | not in this scope |
| 2026-10-29-simulation#1 | maturity-balanced fails on model-basis | medium | open | `cheme maturity`: model-basis fail |
| 2026-10-29-simulation#2 | D-026 maturity list omits energy closure | low | open | not in this scope |
| 2026-10-29-simulation#3 | R102B/R201/R202 bed residual duties | low | open | not in this scope |
| 2026-10-29-simulation#4 | adjust/design-spec core limit without a core issue | low | open | not in this scope |
| 2026-10-29-pids-front#1 | SM-1038/SM-1040 risers smaller than downcomers | medium | open | no P&ID changed |
| 2026-10-29-pids-front#2 | I-101 does not close the tail-gas XV-1105 | medium | open | no P&ID changed |
| 2026-10-29-pids-front#3 | no V-201 low-low blow-by protection | medium | open | no C&E change |
| 2026-10-29-pids-front#4 | CW velocity basis | low | open | not in this scope (the CW lines are now routed with their list DN) |
| 2026-10-29-pids-front#5 | FV-1108 carries PZ-1108's loop number | low | open | no P&ID changed |
| 2026-10-29-pids-front#6 | E-203/E-105 notes give concept duties | low | open | not in this scope |
| 2026-10-29-pids-mid#1 | TV-1601 couples LTS and methanator inlet temperatures | medium | open | no P&ID changed |
| 2026-10-29-pids-mid#2 | rich solvent flashes after LV-1405 | medium | open | no P&ID changed |
| 2026-10-29-pids-mid#3 | S37 link vs M501 sheet | low | open | not in this scope |
| 2026-10-29-pids-mid#4 | FIC-1407 signal line along the AM-1060 pipe | low | open | no P&ID changed |
| 2026-10-29-pids-mid#5 | final elements carry other loops' numbers | low | open | no P&ID changed |
| 2026-10-29-pids-mid#6 | relief coverage of C-301 and R-401/E-402 not stated | low | open | not in this scope |
| 2026-10-29-pids-loop#1 | E-502 riser SM-1101 smaller than downcomer | medium | open | no P&ID changed |
| 2026-10-29-pids-loop#2 | tube-rupture cases not listed | medium | open | not in this scope (see also hazop-r2#1, relief#1) |
| 2026-10-29-pids-loop#3 | loop equipment notes carry pre-simulation values | low | open | not in this scope |
| 2026-10-29-pids-loop#4 | PSV-2210 silencer only in connector text | low | open | no P&ID changed |
| 2026-10-29-control-lists#2 | no front-end pressure / K-501 capacity control | medium | open | not in this scope |
| 2026-10-29-control-lists#1 | start permissives require trips reset while causes present | medium | open | not in this scope |
| 2026-10-29-control-lists#3 | FIC-2106 LP steam setpoint basis | low | open | not in this scope |
| 2026-10-29-control-lists#4 | SEQ-TRIP-FE abort and reset inconsistent | low | open | not in this scope |
| 2026-10-29-control-lists#5 | AIC-1804 setpoint marked calculated | low | open | not in this scope |
| 2026-10-29-control-lists#6 | `sed -i` edits to loops.yaml | low | open | not in this scope |
| 2026-10-30-datasheets#1 | high-pressure gas exchanger areas from gas-service rows (upper bounds) | medium | open | datasheets unchanged |
| 2026-10-30-datasheets#2 | E-502 cold-end approach 0.67 K | medium | open | datasheets unchanged |
| 2026-10-30-datasheets#3 | sheets made final with open fields | medium | open | gate datasheets now fails on its detail requirement (5247884) |
| 2026-10-30-datasheets#4 | datasheet notes copy pre-simulation list values | low | open | unchanged |
| 2026-10-30-datasheets#5 | `duty_kw` of adiabatic beds is the fill residual | low | open | unchanged |
| 2026-10-30-datasheets#6 | coil bank orientation list vs layout | low | open | warnings still reported |
| 2026-10-30-datasheets#7 | equipment-list assumed values marked only in the header | low | open | unchanged |
| 2026-10-30-datasheets#8 | datasheets written by a script | low | open | unchanged |
| 2026-10-30-hazop-r2#1 | tube rupture of E-302 and E-105/E-201 missing from the HAZOP | medium | open | safety/ unchanged |
| 2026-10-30-relief#1 | three tube-rupture cases not listed | medium | open | relief study unchanged |
| 2026-10-30-relief#2 | power-failure load includes the K-101 air | medium | open | relief study unchanged |
| 2026-10-30-relief#3 | full-open Kv assumes a linear characteristic | low | open | relief study unchanged |

## Not covered

- Cable sizing, protection, fault levels and motor starting. The schedule's sizes are
  catalogue values for tray fill only (see #5).
- Civil design of the buried CW: cover under roads, sleeves, thrust blocks, cathodic protection.
- The occupied building assessment of ECB-1 (blast, toxic ingress), beyond #7.
- The process, estimate and safety sides, which this PR does not change.

## Verdict

**approve** (do not merge: stacked on `stage/basic-layout`). The section reached its target.
Every detail gate was taken as far as the core allows, and pass or fail is reported honestly.
hvac and control-complete pass. layout-detail and electrical fail on stated core limits
(no buried case in the headroom rule; one power tray tier per rack). datasheets fails because
the vendor and mechanical data are missing. Nothing was relaxed or accepted. No critical or
high finding is new. The one open high (2026-10-29-design#1) belongs to the base PR and blocks
the basic sign-off, not this section. The medium findings #1 to #3 should be answered before
S9 is merged. Per #1, merge S9 only after the basic sign-off is on main.
