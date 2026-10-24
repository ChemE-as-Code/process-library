---
topic: maturity
reviewed_commit: debdc572d3d3ef993c2c3d431dde071e665f91e7
scope: [process/flowsheet.yaml, process/simulation.yaml, process/design-basis.yaml, process.yaml, DESIGN.md]
basis:
  - {path: process/flowsheet.yaml, revision: 'sha256:2e6a47f90612a61e9e806d83cca6e80fbc44a58ccc8a43eb0a2eddd30eaca4a3', relation: analyses}
  - {path: process/design-basis.yaml, revision: 'sha256:0498974de4c64d23299e4a93fc56382beeae4c20493d14612a3c0912288757e0', relation: analyses}
  - {path: process/simulation-run.json, revision: debdc572d3d3ef993c2c3d431dde071e665f91e7, relation: analyses}
  - {path: checks/maturity.json, revision: debdc572d3d3ef993c2c3d431dde071e665f91e7, relation: depends-on}
  - {path: equipment/datasheets, revision: debdc572d3d3ef993c2c3d431dde071e665f91e7, relation: depends-on}
reviewer: Claude (independent review agent; did not author D-099 or its implementation)
reviewer_kind: agent
branch: stage/basic-maturity
merge: pending
---
# Review: calculation maturity of ASU-1 (D-099), second independent review

This is an independent review of the calculation maturity on branch `stage/basic-maturity`
at debdc57. The DESIGN.md part of the scope is decision D-099 and the pointer added under
D-097. The review checks against core's docs/framework/maturity.md (origin/main).

debdc57 records the owner's decision D-099: the design air (30 C, 1.013 bara, 80 % RH,
420 ppm CO2, dry air of the U.S. Standard Atmosphere 1976 / ISO 2533) and the design air rate
(85,840 Nm3/h dry) are the design specification. It marks those values DESIGN SPECIFICATION in
the design basis and makes S1's flow and composition and S4's flow `given`. No number changed.
The claim in process.yaml goes from concept to screening.

Checks run at debdc57:
- `cheme maturity`: **level balanced (supports library maturity screening)**, manifest claims
  screening, review status unreviewed. No `cheme.maturity-claim-exceeds` warning.
  - sourced passes, including `sourced.boundary` (failed in maturity-review1).
  - Every balanced requirement passes. `balanced.energy-closure` (not required) fails on PRD,
    K4101 and K4102, as D-097 (5) explains.
  - Predictive fails on coverage (C1102 excluded) and model basis (V2101 component split).
    property-regime and energy-closure are unsupported in core.
  - The engineering requirements pass, but engineering is not reached below predictive.
  - checks/maturity.json agrees with `cheme maturity --json` except for the commit metadata
    (written just before the commit, with the three files then uncommitted).
- Mapping (maturity.md, "Mapping onto the process-library manifest"): balanced supports
  screening. The claim `screening` matches; basic-engineering would need engineering.
- `cheme validate`: 120 files, 0 errors, 57 warnings (the same groups as before: 13
  instrument-no-interlock, 6 line-crossing, 3 process-energy-balance, 19 review-finding-status,
  2 review-unknown-commit, 12 template-metadata, 2 titleblock-sheet).
- `cheme process simulate --check`: no stale record. It exits 1 on 11
  `process-sim-deviation` warnings (S5, S5B, S10, S11, S12A, S12B, S12C, S16, S17, E2, E3,
  E3102: assumed values against the simulation). None is on S1 or S4, and all were there
  before debdc57 (one of them is maturity-review1#9).
- `cheme layout build --check` and `cheme layout lifting --check`: up to date.
- `cheme check --no-write`: 31 of 31 gates ok.

Verdict: **no critical, high or medium finding is open.** The change marks exactly the values
the decision covers. Two new low findings (#10, #11). #9 stays open (low).

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-maturity-review2#10 | - | V-2101A/B datasheets, co2_load_kg_h | The source text still reads "the design basis 420 ppm CO2 on dry air, ASSUMED". Since D-099 the 420 ppm is the design specification. The value (67.66 kg/h) and its `assumed: true` (a sizing estimate) are unaffected. | low | open | Reword the source to "420 ppm CO2, the design specification (D-099)" in both datasheets at their next revision. |
| 2026-10-24-maturity-review2#11 | - | flowsheet.yaml, case `design` | The case description reads "30 C ambient, 94 % O2 recovery (ASSUMED)". The design basis gives ~83 % since D-066 and says 94 % was dropped. Pre-existing, not changed by debdc57. | low | open | Change the description to the D-066 recovery (~83 %, ASSUMED) and name the design air as the D-099 design specification. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-maturity-review1#1 | S1 tagged `given` on values marked ASSUMED. | high | closed f16c503 | Still closed: at debdc57 S1 is `given` only because D-099, an owner decision, fixes the design air and its rate; design-basis.yaml now marks them DESIGN SPECIFICATION, as maturity-review1 asked. |
| 2026-10-24-maturity-review1#9 | S17 kept at 13 C against the simulated 7.2 C. | low | open | No change in debdc57; the action of maturity-review1 stands. |
| 2026-10-24-control-review5#1 | PIC-4101 set-point window not stated. | medium | closed 02753fc | DESIGN.md D-096 states the window, the GOX / waste N2 split at turndown and VNT-4003 for the zones owner (PROGRESS row of 02753fc). Listed because DESIGN.md is in both scopes; control content not re-reviewed here. |
| 2026-10-24-control-review5#2 | Junction boxes did not follow the PIC-4101 / PIC-4150 swap. | low | closed 02753fc | PROGRESS row of 02753fc (IC-PIC-4101 on JB-A3-2, IC-PIC-4150 on JB-A4-1). |
| 2026-10-24-control-review5#3 | PIC-4101's tap drawn on S2 but modelled on S1. | low | open | No commit names it; P-04 unchanged in debdc57. |
| 2026-10-24-control-review5#4 | Residual stale control texts. | low | closed 02753fc | PROGRESS row of 02753fc ("stale texts corrected"). |
| 2026-10-24-control-review5#5 | H-04 hand-over incomplete. | low | closed 02753fc | D-096 "For the HAZOP owner (H-04)" revised in 02753fc; H-04 reassessed in 169dc8b / 5e263b4 (hazop-review3). |

## Checked and fine
- **What changed to the design specification:** in design-basis.yaml the air composition, a
  new `water_and_co2_design_specification` (H2O at 80 % RH / 30 C, CO2 420 ppm), the rate
  85,840 Nm3/h, the conditions, `site.design_ambient_degc` and
  `site.atmospheric_pressure_bara`. These are what D-097 (1) named for the owner.
- **What stays ASSUMED:** the traces (moved to `trace_contaminants_ASSUMED`, values
  unchanged), the minimum ambient, elevation, air quality, seismic and wind, location, the
  capacity margins and turndown, and every entry under `assumptions`, including the ~83 % O2
  recovery. S1's pressure (1.01 bara, suction after intake losses) stays assumed, and S4's
  split into S5 / S4B and its D-027 composition stay assumed. The old key
  `contaminants_ASSUMED` is referenced nowhere else (DESIGN.md D-097 names it historically).
- **S4 flow `given`:** D-097 (1) asked that the ASSUMED mark on S4 be removed with the owner
  decision, and 110,870 kg/h is the CO2-free dry part of the specified rate. Justified.
- **S1 sources, recomputed:** the dry set 78.084 + 20.9476 + 0.934 + 0.042 = 100.0076 mol%,
  renormalised and scaled by (1 - 0.03354), gives N2 0.754594, O2 0.202435, Ar 0.009026,
  CO2 0.000406, as written. Water: 0.8 x 4.247 kPa (IAPWS-95 p_sat at 30 C, 4.2470 kPa) /
  101.3 kPa = 0.033540. 85,810 Nm3/h / 22.414 x ~28.96 kg/kmol is about 110,870 kg/h, plus
  71 kg/h CO2 and 2,394 kg/h water gives 113,335 kg/h. The sources name D-099, the standard
  and IAPWS-95.
- **process.yaml:** comment, validation notes and the chemistry air note agree with the
  report; the library README row says screening, balanced, not independently reviewed.
- **TEA / LCA:** only feed:AIR's provenance changed (assumed to given); the LCA fingerprint of
  flowsheet.yaml matches the file. The `mto` and `lca` gates pass.
- **BFD / PFD:** regenerated; `process-balances` and `process-basic` pass, and the sheets carry
  the new source texts.
- **D-099 text:** it matches the files, states what stays ASSUMED, that the rate is the
  owner's choice with the recovery still ASSUMED (D-066), and the maturity result. The D-097
  pointer is one line and does not rewrite D-097.

## Not checked
- core's own maturity rules (they are core's).
- That the owner made the decision: D-099 records it as made by the user, the project owner;
  an agent review cannot confirm it beyond that record.
- The HAZOP consequences (see hazop-review4).
