---
topic: maturity
reviewed_commit: 41904e7ae9b79d425d3d629a2ee20a819c728aed
scope: [process/flowsheet.yaml, process/simulation.yaml, process/design-basis.yaml, process.yaml, DESIGN.md]
basis:
  - {path: process/simulation-run.json, revision: 41904e7ae9b79d425d3d629a2ee20a819c728aed, relation: analyses}
  - {path: checks/maturity.json, revision: 41904e7ae9b79d425d3d629a2ee20a819c728aed, relation: depends-on}
  - {path: equipment/datasheets, revision: 41904e7ae9b79d425d3d629a2ee20a819c728aed, relation: depends-on}
reviewer: Claude (independent review agent; did not author D-101 .. D-108 or their implementation)
reviewer_kind: agent
branch: stage/basic-close-open
merge: pending
---
# Review: calculation maturity of ASU-1, third independent review (D-103, D-104, D-108)

Independent review of branch `stage/basic-close-open` (pushed as origin `stage/basic-close-open`) at 41904e7, against origin/main. Changes
in scope: the 50 kW cold-box heat leak as model step HL3101 (ASSUMED), S16B -> HL3101 -> S16C,
S17 now calculated from the simulation, the Peng-Robinson substitution accepted, the two
cold-box balances reconciled (D-104), and the DESIGN.md entries D-101 .. D-108.

Checks run at 41904e7:
- `cheme maturity`: **level balanced (supports library maturity screening)**, claim screening,
  review status unreviewed. No `cheme.maturity-claim-exceeds`. sourced and every balanced
  requirement pass. `balanced.energy-closure` (not required) fails on PRD, K4101 and K4102 as
  in review2. Predictive fails on coverage (C1102 excluded), model basis (V2101 component
  split), property regime and energy closure (unsupported in core). engineering requirements
  pass, but engineering is not reached below predictive.
- `cheme validate`: 122 files, 0 errors, 60 warnings (known groups: line-crossing,
  template-metadata, titleblock-sheet, process-energy-balance, review-finding-status /
  review-unknown-commit on control-review1/2).
- `cheme process simulate` was not run (told not to); the record process/simulation-run.json is
  current (predictive.current ok).
- DESIGN.md: D-100 .. D-108 each appear once and in order.
- `cheme check --no-write` before this record: 30 of 31 (layout-review only).

Verdict: **no critical, high or medium finding is open.** The claim stays screening; D-103 keeps
the 50 kW leak declared ASSUMED. No new finding.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|

No new finding.

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-maturity-review1#9 | S17 kept at 13 C against the simulated 7.2 C. | low | closed d449bae | S17 is now `calculated` at 9.488 C (`cheme process streams`), only its flow and pressure stay assumed. |
| 2026-10-24-maturity-review2#10 | V-2101A/B datasheet source text still says the 420 ppm CO2 is ASSUMED. | low | closed 3c55549 | V-2101A.yaml now reads "420 ppm CO2, the design specification, D-099". |
| 2026-10-24-maturity-review2#11 | Case description says 94 % O2 recovery. | low | closed d449bae | flowsheet.yaml case `design`: "~83 % O2 recovery (D-066, ASSUMED)". |
| 2026-10-24-control-review5#3 | PIC-4101's tap drawn on S2 but modelled on S1. | low | open | Not touched on this branch. |

## Checked and fine
- The heat leak is a declared ASSUMED value (50 kW), not data; S16C and S17 are `calculated`
  and S16C's source names HL3101. The simulation's property package substitution (Peng-Robinson)
  is recorded and accepted with a reason in D-103; `predictive.property-package` ok.
- `checks/maturity.json` agrees with `cheme maturity` at this commit.
- D-104 states that the two balances (~75 kW governs vs ~130 kW) differ and names which one
  governs; the claims do not exceed the evidence.

## Not checked
- core's maturity rules and the simulator itself (not rerun).
- The 50 kW leak value against a vendor figure (ASSUMED, flagged).
