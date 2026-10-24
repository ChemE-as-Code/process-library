---
topic: hazop
reviewed_commit: debdc572d3d3ef993c2c3d431dde071e665f91e7
scope: [safety/hazop/H-01, safety/hazop/H-02, safety/hazop/H-03, safety/hazop/H-04, safety/risk-matrix.yaml]
basis:
  - {path: pid/P-01.xml, revision: 'sha256:c3b9a332a2200a9738e68801bf15e1f94c58264fbbd1e506c03c7045725ba5af', relation: analyses}
  - {path: pid/P-02.xml, revision: 'sha256:f6b4904d694ef94994fa3c5af7e903503134e9b9415e93794cdb4fe44e33ade6', relation: analyses}
  - {path: pid/P-03.xml, revision: 'sha256:e633f6e71bb6a9926e184eeab53287e44529b4cd209fb0a87cfbbe5a7db09974', relation: analyses}
  - {path: pid/P-04.xml, revision: 'sha256:cc86ce6eb26c5538d2b8ab45b112487b67da31ba3be554395b075fe3a1541374', relation: analyses}
  - {path: control/cause-effect.yaml, revision: 'sha256:b9c8e56cbc49b1b9d9595e39b02fbaa24fdffdf137d402bcd253b329b9299ca5', relation: analyses}
  - {path: control/instrument-list.yaml, revision: 'sha256:faa49c1f80b17ec93d52133f0e027cb54446579b9511f38da9f70c19e5113ba8', relation: analyses}
  - {path: control/loops.yaml, revision: 'sha256:579c00924933d285fb6ed9ecd2e5e298c07c85e7d5072ddebd218d4e10486263', relation: analyses}
  - {path: control/sequences.yaml, revision: 'sha256:f576a5b3fb45996ccf19bde07cfda0268c70eeb2cab5b1a167a9034beee36778', relation: analyses}
  - {path: equipment/equipment-list.yaml, revision: 'sha256:7dd6ae258db62812479ac0e0e7c520b82a46de4f02ee2020db2f5d4013870490', relation: analyses}
  - {path: piping/line-list.yaml, revision: 'sha256:3643188e55a2e5b9128b4b6c25a3e8b71bbd07e4fdb3fbe0d47ade72261f1485', relation: analyses}
  - {path: piping/special-items.yaml, revision: 'sha256:8071c9646730d15356f23923163a5416205ea568dbb9592a61fb49e9d19077d0', relation: analyses}
  - {path: process/design-basis.yaml, revision: 'sha256:0498974de4c64d23299e4a93fc56382beeae4c20493d14612a3c0912288757e0', relation: analyses}
  - {path: process/flowsheet.yaml, revision: 'sha256:2e6a47f90612a61e9e806d83cca6e80fbc44a58ccc8a43eb0a2eddd30eaca4a3', relation: analyses}
  - {path: DESIGN.md, revision: debdc572d3d3ef993c2c3d431dde071e665f91e7, relation: depends-on}
reviewer: Claude (independent review agent; did not author the HAZOP studies, D-099 or the re-stamp)
reviewer_kind: agent
branch: stage/basic-maturity
merge: pending
---
# Review: HAZOP of ASU-1 (H-01 .. H-04), fourth independent review

This is an independent review of branch `stage/basic-maturity` at debdc57. It covers the
HAZOP part of D-099: the design basis and the flowsheet, analysed inputs of all four studies,
changed in provenance and wording only (the design air and its rate are now the design
specification; no number changed).

Commit debdc57 changed the studies as follows. No other entry was rewritten:
- H01-N1 `design_intent`: the design air (30 C, 80 % RH, 1.013 bara, 85,840 Nm3/h dry) and
  CO2 420 ppm are named the design specification (D-099); the traces (THC 5 ppm as CH4,
  C2H2 50 ppb, N2O 0.33 ppm) and the -5 C minimum ambient stay ASSUMED;
- the `analysed:` revisions of process/design-basis.yaml and process/flowsheet.yaml in H-01 ..
  H-04 re-stamped. The other inputs are unchanged.

No scenario, cause, consequence, safeguard, rating, band or action changed. A search of the
four studies finds no scenario basis that cited the design air or its rate as ASSUMED.
Every entry is still `status: proposed`, `by: agent`; none is accepted.

Checks run at debdc57:
- `cheme safety hazop check`: H-01 .. H-04 are all `draft`, each with 0 errors and 0
  warnings. The only info is `hazop-unresolved`: 104 / 77 / 109 / 163 proposals. The only
  staleness reported is that of hazop-review3, which this record replaces.
- `cheme safety hazop rate H-01` .. `H-04` (read-only): exit 0 for each, every band current.
- `cheme safety hazop stamp` (read-only): every analysed input unchanged against its recorded
  revision. The sha256 of design-basis.yaml (0498974d...) and flowsheet.yaml (2e6a47f9...)
  match the files at debdc57.
- `cheme validate`: 0 errors, 57 warnings, none `hazop-input-changed`; the same groups as at
  hazop-review3.

**Recount.** No rating changed, so the hazop-review3 count stands: 218 scenarios, 86 high /
78 medium / 54 low, 9 very-high before safeguards, none after, every high with an action.

Verdict: **no critical, high or medium finding is open.** No new finding.

The four studies stay `draft` until a human team accepts the proposals; this agent record
does not make any study `assessed` or `reviewed`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|

None.

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-hazop-review3#1 | Over-draw at reduced make without a failure. | high | closed 5e263b4 | H04-S79 / S80 and H04-A28 unchanged at debdc57. |
| 2026-10-24-hazop-review3#2 | PIC-4102's own failure not analysed. | medium | closed 5e263b4 | H04-S82 / S83 and H04-A29 unchanged. |
| 2026-10-24-hazop-review3#3 | Loop failure and normal demands mixed in H04-S27. | medium | closed 5e263b4 | H04-S27, S84, S85 unchanged. |
| 2026-10-24-hazop-review3#4 | GAN header leak had no containment deviation. | medium | closed 5e263b4 | H04-N5-LK / S86 unchanged. |
| 2026-10-24-hazop-review3#5 | loops.yaml / sequences.yaml not analysed inputs of H-04. | medium | closed 5e263b4 | Both still in H-04's `analysed:` at their current sha256. |
| 2026-10-24-hazop-review3#6 | H04-S76 people residual took two orders. | low | closed 5e263b4 | Unchanged, `rate` current. |
| 2026-10-24-hazop-review3#7 | Masking argument applied unevenly. | low | closed 5e263b4 | Unchanged. |

## Checked and fine
- **H01-N1 intent:** agrees with design-basis.yaml at debdc57 (DESIGN SPECIFICATION on the
  conditions, rate and CO2; ASSUMED on the traces and the minimum ambient) and with D-099 (4).
- **Re-stamp:** made after the change, with the ratings looked up again by `rate --write`;
  only the two revision lines per study changed.
- **Status fields:** no `accepted` status in any study.

## Not checked
- The HAZOP consequences of a site survey that changes the design air: D-099 makes that a new
  decision, to be reassessed then.
- HAZOP team, sessions, matrix acceptance and the human review record: outside what an agent
  can do.
