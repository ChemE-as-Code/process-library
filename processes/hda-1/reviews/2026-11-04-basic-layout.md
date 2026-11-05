---
topic: layout
reviewed_commit: 430d2f64a5c966964981c24d5e12c2e842df8707
scope: [layout/, piping/routing.yaml, estimate/, DESIGN.md, PROGRESS.md]
reviewer: review-agent
reviewer_kind: agent
branch: stage/hda-1-basic-layout
merge: pending
---
# Review: layout (3D layout, MTO and class 4 estimate of hda-1, S5, PR #364, re-review round 1)

This is an independent re-review of PR #364 (issue #302) at 430d2f6. It follows the fix commits
64d0bd67 (falling suctions and overheads, item elevations, valve stations at grade, access
spaces), 773f6ede (escape, keep-clear and bundle-removal zones, flange sources, separations)
and 430d2f64 (sourced estimate factors, H-101 factor range, K-102 driver basis, D-027 and
PROGRESS). These commits answer the panel's round-1 findings. The panel's findings had no
record of their own, so they are listed here as #1 to #23 with their resolution. #24 to #27
are new.

The reviewer re-ran the following with cheme 1.4.1 (core main ab9d91e) at 430d2f6:

- `cheme validate`: 44 files, 0 errors, 94 warnings. These are the layout warnings below and
  the four PFD composition warnings already on main (2026-11-03-simulation-closeout#18).
  `cheme.decision-unknown [D-045]` is no longer reported.
- `cheme check`: lifting-study, mto, tea, maturity-balanced, layout-plot-plan, drawing-clean,
  pids-*, process-*, control-complete and layout-detail pass. layout-3d failed only on
  `drawings` (no record of topic layout), and layout-review failed only because no layout
  review existed. This record is that review. design-review fails because the S4 record is no
  longer current; that review belongs to S5r. electrical, hvac and datasheets fail as expected
  (S7, S9).
- `cheme maturity`: calculation maturity stays **balanced**. Predictive fails on model-basis,
  property-regime and formation-data, and engineering on datasheets (unchanged).
- `cheme layout build --check`: the model is up to date. `cheme assess mto|equipment|tea
  --check`: current. `cheme assess estimate --check`: estimate.csv and estimate.md are not
  written because `example: true` stays in rates.yaml (see #21). `cheme assess lca --check`:
  **not current** (#27).
- Own point-by-point reading of all 232 routed segments in `layout/plant-model.yaml`: no point
  is below grade, every pump suction falls from vessel to pump, and the pockets and humps of
  every line were listed (#24).

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-04-basic-layout#1 | P-06 | PG-630 | Panel: the C-203 vacuum overhead dropped to 4.7 m under S-203 and climbed back to E-205, making a 5.6 m liquid pocket. | high | closed 64d0bd67 | Checked: C-203 stands on a 2.5 m foundation. PG-630 points are 16.85, 17.3, 12.8, 12.8, 12.8 and 10.95 m: it rises 0.45 m off the top nozzle, then falls continuously to E-205 T1. There is no pocket. Seen in build/layout-section-x150.png. |
| 2026-11-04-basic-layout#2 | P-02 | AR-116, AR-235, AR-239 | Panel: the quench pump suction had an 8 m high point at the T235 tee. | high | closed 64d0bd67 | Checked: V-101 stands on a 2.0 m foundation. AR-116 S1 runs 2.79 > 2.49 > 1.2 m to T235, and AR-235 and AR-239 run 1.2 > 0.39 m to P-102 and P-102B. The suction falls all the way with no rise. AR-116 goes up to the rack only after the tee (P-04 segment). |
| 2026-11-04-basic-layout#3 | P-01 | PG-106, PG-107, PG-108 | Panel: no flexibility allowance for the hot hydrogen lines. | medium | closed 430d2f64 | D-027 now records a screening estimate: growth 0.14 to 0.17 m, needed legs 13 to 17 m against 1 to 5.5 m as routed. It names the plot space (a loop of about 8 x 8 m at y 95-101, x 44-58, and a 6 m offset east of R-101) and lists the stress check as an S5r open item. This met the panel's minimum fix. The remaining design work is #25. |
| 2026-11-04-basic-layout#4 | layout | bundle pull and access spaces | Panel: 11 access-blocked warnings (bundle pulls, pump and motor spaces) and no bundle-removal provision for the deck condensers. | medium | closed 773f6ede | Checked: `layout-access-blocked` reports 0. MZ-E201, MZ-E203 and MZ-E205 declare bundle removal by puller and crane from named pads, with the reason in D-027. |
| 2026-11-04-basic-layout#5 | layout | valve access, ladder cages, walkway risers | Panel: control valves high with no platform, 55 operability warnings, 8 ladder-clearance and 7 walkway-riser warnings. | medium | superseded by 2026-11-04-basic-layout#26 | Fixed: LV-405, FV-507, LV-506, FV-607 and LV-606 now stand at grade; ladder clearance 8 > 0; walkway risers 7 > 0. The 46 remaining operability warnings are #26. |
| 2026-11-04-basic-layout#6 | layout | equipment elevations | Panel: items stood at z=0, lines ran below grade, and NPSH was poor at V-100 and C-203. | medium | closed 64d0bd67 | Checked in the model: there is no point below grade on any of the 232 segments. Foundations: V-100 2.5 m, V-101 2.0 m, C-203 2.5 m, E-102 0.8 m, reboilers 1.0 m (ASSUMED). The static heads are stated in D-027. NPSH stays an S7 item. |
| 2026-11-04-basic-layout#7 | layout/zones.yaml | escape, keep-clear, flange sources | Panel (layout): no escape or keep-clear zones, and no flange sources on E-101 or R-101. | medium | closed 773f6ede | There are now 5 escape zones (Z-ESC-*), 3 keep-clear zones (KC-*), Z-HAZ-H2LOOP (E-101, R-101 and V-101 flanges) and Z-HAZ-OVHD (column overheads and condenser inlets). The H-101 coil flanges are left out, with the reason given. |
| 2026-11-04-basic-layout#8 | layout/site-plan.yaml | separations basis | Panel: no spacing basis was cited, and the S3b/S5 items had no separations. | medium | closed 773f6ede | The search for an openly readable standard (OISD-STD-118 is sold) is recorded in D-027, and the values stay ASSUMED until the owner's standard and a QRA. New entries: H-101 to PK-201, P-102, S-201..S-203 and Z-HAZ-H2LOOP; ECB-1 to the zones. All pass in the build. |
| 2026-11-04-basic-layout#9 | P-05 | PG-530 | Panel: a free-standing 26 m riser 8 m from C-202. | low | closed 64d0bd67 | It now runs down at 2.8 m from the column axis (x 128.6, y 97.58) to 14.2 m, then crosses to E-203. Clips and guides are a support-design item (D-027). |
| 2026-11-04-basic-layout#10 | P-06 | DP-649 | Panel: a 0.5 m high point in the P-204B suction. | low | closed 64d0bd67 | It is now level at 1.7 m, then drops to 0.34 m. |
| 2026-11-04-basic-layout#11 | P-05, P-06 | CWR-547, CWS-644 | Panel: vent outlets pointed into walking levels. | low | closed 64d0bd67 | `layout-vent-outlet` reports 0 (vents rule). |
| 2026-11-04-basic-layout#12 | PR body | warning counts | Panel: the support-missing and nozzle-unconnected counts were not named. | low | closed 430d2f64 | The PR body and D-027 now name support-missing 108 and nozzle-unconnected 8. These match `cheme layout report`. |
| 2026-11-04-basic-layout#13 | estimate/rates.yaml | indirect, fee, contingency | Panel (estimate): the factors were left as EXAMPLE placeholders. | medium | closed 430d2f64 | Design and engineering 0.30 (Towler and Sinnott 2013, Table 6.3), fee 0.03 and contingency 0.15 (Turton et al. 2012, section 7.3), each with status, source and year, as in ammonia-1. |
| 2026-11-04-basic-layout#14 | estimate/cost-basis.yaml | K-102 driver | Panel: the driver basis was given two incompatible ways. | low | closed 430d2f64 | The factor is now applied to the machine-only cost (ASSUMED), and the motor is counted once, in the allowance. |
| 2026-11-04-basic-layout#15 | estimate/cost-basis.yaml, tea.yaml | stale class-5 text, PK-201 | Panel: the class-5 header and the PK-201 "until S5" text were stale. | low | closed 430d2f64 | The header now reads class 4. PK-201 points to the vendor and S7. D-027 states that the 15 % allowance is unchanged and why. |
| 2026-11-04-basic-layout#16 | estimate/rates.yaml | D-045 reference | Panel: a dangling decision id. | low | closed 430d2f64 | It now reads "its decision 45 in that plant's DESIGN.md". Validate reports no decision-unknown. |
| 2026-11-04-basic-layout#17 | estimate/mto.md, D-027 | concrete quantity | Panel: the concrete understatement was not stated. | low | closed 430d2f64 | D-027 now states that the 87 m3 is the model's foundations only, not a foundation design. |
| 2026-11-04-basic-layout#18 | PR body, D-027 | bare-module change | Panel: "9.99 (was 5.74)" was not like for like. | low | closed 430d2f64 | D-027 and the PR body lead with ISBL 16.81 > 17.59 MEUR and explain the 5.74. |
| 2026-11-04-basic-layout#19 | estimate/cost-basis.yaml | H-101 FBM | Panel (integrity): the source's own MPF conflict (additive against product form) was not disclosed. | medium | closed 430d2f64 | factor_source and D-027 state the conflict and give the reason for the additive base case. FBM 1.81 to 2.88 is carried ASSUMED, with TEA scenario h101-fbm-low (ISBL x 0.923455; own check: 1 - 1 346 271 / 17 588 092 = 0.92346). The MF band choice is justified. |
| 2026-11-04-basic-layout#20 | layout/zones.yaml | zones incomplete | Panel (integrity): no escape or keep-clear zones, and no hydrogen-loop or overhead flange sources. | medium | closed 773f6ede | As #7. |
| 2026-11-04-basic-layout#21 | estimate/rates.yaml | bulk unit rates | Panel (integrity): bulk unit rates and the two erection factors are still placeholders. `example: true` stays and `cheme assess estimate` prices nothing. | medium | open | Disclosed with the search recorded, as in ammonia-1 (its decision 45). The class 4 claim rests on the equipment-factored estimate. The owner or a contractor supplies the rates. Carried to S5r and the owner. |
| 2026-11-04-basic-layout#22 | estimate/tea.yaml | tea-class-stage | Panel: class 4 is claimed while plant.yaml is at the concept stage (warning outside the gate). | low | open | Confirm at the basic sign-off (S5r) that the warning clears and is not accepted. |
| 2026-11-04-basic-layout#23 | piping/routing.yaml | DR-138..DR-652 | Panel: eight drains are skipped to closed-drain hubs, and none is shown up to its hub. | low | open | S5r confirms the skip reason, or routes each drain to a declared hub point. |
| 2026-11-04-basic-layout#24 | P-01, P-02, P-06, P-07 | relief laterals FL-135, FL-331, FL-233, FL-646 and header FL-701 | New. Relief piping has liquid pockets and laterals that rise into the header. FL-701 S1 dips from 6.0 to 4.84 m and rises to 6.16 m at its west dead end (1.16 m pocket). FL-135 (P-07) steps down from 9.05 to 8.08 m and back up (0.97 m pocket); FL-331 does the same from 8.97 to 8.06 m (0.91 m). FL-233 has two 0.95 to 1.0 m pockets. FL-646 leaves its relief valve at 2.0 m, rises to 4.53 m, dips to 4.03 m and rises again into the 6.16 m header. The relief valves of FL-135 (2.8 m), FL-331 (4.6 m) and FL-646 (2.0 m) sit below the header, so condensed liquid drains back onto the valve outlets. A relief system must drain freely to the knock-out drum. The routing notes say only "the flare header's slope is not designed". | medium | open | Add via or elevation intents so that each lateral falls to the header and enters it from the top, with no pocket. Put the relief valves above the header, or record why a valve must stay low and how its outlet is drained. Remove the FL-701 dead-end dip. Then rebuild and re-check the pockets. |
| 2026-11-04-basic-layout#25 | P-01, layout | PG-106, PG-107, PG-108 | New (follows #3). D-027 shows the hot hydrogen lines are not flexible as routed, and names the plot space for loops and offsets. That space is not reserved in the model: there is no maintenance or keep-clear zone at y 95-101, x 44-58 or east of R-101. Later work could occupy it, and the stress check is not done. | medium | open | Declare the reserved loop and offset volumes in zones.yaml, or route the loops now. Run the screening stress check for PG-106, PG-107 and PG-108 in S5r, with the nozzle loads on H-101, R-101 and E-101. |
| 2026-11-04-basic-layout#26 | layout | 46 operability warnings | New (splits #5). Valves and transmitters on rack and pipe-way drops are still out of reach. Examples: PV-604 handwheel at 8.6 m with the floor 2.6 m below, TV-602 at 4.4 m, LV-608 at 4.1 m, and the V-100 N10 transmitter at 3.7 m. Pump-area valves are 0.1 to 0.5 m above the 1.8 m reach. All are listed in D-027 as open, not accepted. | medium | open | S5r and detail piping: bring each station to grade, onto the proposed valve platforms (VP-*), or declare an operator with a reason in routing.yaml operators. |
| 2026-11-04-basic-layout#27 | lca/dataset.yaml | LCA currency | New. 430d2f64 regenerated estimate/mto.csv but not the LCA dataset. `cheme assess lca --check` reports "lca/dataset.yaml is not current": the dataset still records the pre-fix mto.csv hash e9a41a8a against the committed 62a6401e. No gate requires lca-current yet (the lca gate is commented out), but the PR body says the LCA check is current. | low | open | Run `cheme assess lca --write` and commit the regenerated dataset. Correct the PR body. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-27-pfd-lci-review#9 | fuel-gas credit methods side by side | low | open | carried (I-11); outside this PR |
| 2026-11-03-concept-closeout#5 | H-101 bare-module factor 2.5 without a read source | low | closed 430d2f64 | the 2.5 is gone: H-101 now has a Guthrie FBM read from the cited UC OCW slides (b5574bc9), with the source conflict stated and the range 1.81 to 2.88 carried in TEA scenario h101-fbm-low (430d2f64) |
| 2026-11-03-concept-closeout#16 | EUA price from a secondary report | low | open | estimate/tea.yaml EUA source unchanged in this PR |
| 2026-11-03-concept-closeout#18 | ammonia-1 attributes the ISO 6976 methane value to NIST | low | open | outside this PR |
| 2026-11-03-simulation-closeout#18 | composition sums of shortcut-column streams | low | open | 4 pydexpi_composition_fractions warnings at 430d2f6 (core#130) |
| 2026-11-03-simulation-closeout#19 | process/reactions.yaml R101B wording | low | open | process/ not changed by this PR |
| 2026-11-03-simulation-closeout#20 | process.yaml catalog leftovers | low | open | process.yaml not changed by this PR |
| 2026-11-04-basic-psa#12 | superseded scripts/purge_h2_recovery.py kept on HEAD | low | open | file still present at 430d2f6 |
| 2026-11-04-basic-psa#13 | D-024 break-even rounding 0.73 vs 0.735 | low | open | DESIGN.md D-024 still reads "below about 0.73" |
| 2026-11-04-basic-psa#14 | what checks the road clearances (layout-plot-plan vs cheme validate) | low | open | not changed by this PR |
| 2026-11-04-basic-pids#11 | P-204A/B minimum flow | low | open | D-027 now selects a sealless rotary gear pump with an integral casing relief valve, which answers minimum flow and relief in the design text. P-06 still shows a centrifugal pump with no relief valve; the P-06 revision (RotaryPump, relief valve drawn) is the remaining action |
| 2026-11-04-basic-pids#15 | blind header ends as off-page connectors | low | open | P-07 and P-08 not changed (core#151) |
| 2026-11-04-basic-pids#19 | slanted measuring and signal lines | low | open | no P&ID changed by this PR |
| 2026-11-04-basic-pids#28 | 3D model outdated | low | closed 64d0bd67 | plant-model.yaml rebuilt; `cheme layout build --check`: up to date; no layout-model-outdated warning |
| 2026-11-04-basic-control-lists#18 | I-106 reset wording vs start-up | low | closed b5574bc9 | the reset text in control/cause-effect.yaml and step S4 of SEQ-SD-PLANT now name the pumps-stopped leg's start-up bypass, which SEQ-START-RXN step S6 removes once P-102 runs (control/sequences.yaml) |
| 2026-11-04-basic-control-lists#19 | TZ-128 trip signal not drawn on P-01 | low | open | no P&ID changed by this PR |

## Layout

Taken from `cheme layout report` at 430d2f6:

- **Lines:** 232 segments routed. The 8 DR drains are skipped with their reason (#23). None is unrouted.
- **Chains per method:** via 43, astar 38, rack 23, via+astar_coarse 4, open 4,
  rack+astar_coarse 1, astar_coarse 1. There are no `direct` or `rack+direct` routes.
- **Rack fill:** PR-1 tier 6 m 30 %, tier 8 m 18 %; PR-2 tier 7 m 14 %, tier 9 m 23 %.
- **Model findings:**

  | rule | count | status |
  |---|---|---|
  | clashes, headroom, access-blocked, ladder clearance, walkway riser, vent outlet, separation, zone crossing | 0 | |
  | operability | 46 | open, #26 |
  | free-span | 44 | open, support design (S5r/detail) |
  | support-missing | 108 (info) | open, support design (S5r/detail) |
  | nozzle-unconnected | 8 (info) | the skipped drains, #23 |
  | nozzle-defaulted | 3 | |

  No model finding is accepted in checks.yaml.
- **Drawings read:**
  - `build/layout-plan.png`
  - `build/layout-section-x150.png` (C-203, S-203, PK-201)
  - `build/layout-section-y53.png` (along PR-1)
  - `build/layout-section-x78.svg` (V-101, quench pumps)

  The SVGs come from `cheme layout render`. resvg is not installed, so the PNGs were rasterised
  from those SVGs with headless Edge.
- **Seen in the drawings:**
  - Section x=150: PG-630 runs from the column top over S-203 down onto E-205, with no dip.
  - Plan: the hot loop H-101 to R-101 to E-101 and the escape and keep-clear zones.
  - Section y=53: steps in the rack-level lines next to the flare header. Point checks
    confirmed these as the pockets in #24.
- **Lifting study:** 11 heavy lifts. Each has a pad, a clear lane and a laydown. No lane is
  accepted, and there is no build/lifting-acceptance-proposal.md.

## Checked and fine

- The pump suctions of P-101, P-102 and P-102B, P-201..P-204A/B fall continuously from their
  vessel (point check).
- No process or utility point is below grade, so no trench is needed.
- Bundle removal: the deck condenser maintenance volumes are clear.
- Escape routes lead to the roads, away from H-101.
- The new separations all pass in the build.
- Estimate arithmetic:
  - H-101 low-FBM scenario multiplier.
  - ISBL, the PSA multipliers and the class 4 range (20.6 to 44.0 MEUR), re-derived as the panel did.
  - The MF band reasoning for H-101: C about 35 kUSD, below the 200 kUSD limit.
- The rates.yaml factors carry status, source with locator, and year, in our own words.
- `cheme validate` 0 errors; gates lifting-study, mto and tea pass; gate tea is enabled as the
  template documents it (`[prices, no-example, tea-current]`).
- With this record, the remaining `drawings` part of layout-3d and the layout-review gate
  have the record they look for.

## Not checked

- **Pipe stress and supports.** There is no stress model or support design. This needs a
  piping stress engineer in S5r or detail engineering (#25, free spans, support-missing).
- **Structural design.** Steel, foundations and the K-102 block foundation are left to a
  structural engineer at detail engineering.
- **Area classification study.** The zone extents are ASSUMED from the indicative table. The
  site's classification study must replace them.
- **Spacing and QRA.** The separations stay ASSUMED until the owner's standard and a QRA are
  available (D-018, D-027).
- **NPSH and pump datasheets.** These are S7 work.
- **Flare system hydraulics.** Back-pressure is not checked.
- **The Guthrie and Turton sources.** These were not re-read by this reviewer. The panel had
  checked the slide values, and only the stated arithmetic was checked here.
