---
topic: hazop
reviewed_commit: 5e263b4644508408ebedcef7d3c64b9bef5b72b9
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
  - {path: process/design-basis.yaml, revision: 'sha256:db3372d4b36b2577ddeab2c14f7ca16db622a3d5d32dddc006ff9a1551ff0281', relation: analyses}
  - {path: process/flowsheet.yaml, revision: 'sha256:0e6abb0456355c67feffb8c71aba3b1d04fdbe50b93f1f3b623b0a3c25835b7a', relation: analyses}
  - {path: DESIGN.md, revision: 5e263b4644508408ebedcef7d3c64b9bef5b72b9, relation: depends-on}
reviewer: Claude (independent review agent; did not author the HAZOP studies, D-098 or the review3 fixes)
reviewer_kind: agent
branch: stage/basic-maturity
merge: pending
---
# Review: HAZOP of ASU-1 (H-01 .. H-04), third independent review

This is an independent review of branch `stage/basic-maturity` at 5e263b4. It covers the
HAZOP reassessment for D-095 / D-096 and the D-097 flowsheet (169dc8b), and the fixes for this
review's seven findings (5e263b4, D-098). The findings were raised on 169dc8b. They are
recorded here with the commit that closed them.

Commit 5e263b4 changed H-04 by stable id. No other entry was rewritten:
- new scenarios H04-S79 .. S86 and a new deviation H04-N5-LK;
- revised causes and notes for H04-S02, S27, S75 and S77, and a revised residual for S76;
- new actions H04-A28 and A29, and an extended H04-A15 and A23;
- `control/loops.yaml` and `control/sequences.yaml` added as analysed inputs of H-04.

It also updated the H-03 design-intent texts for the revised simulation values (f16c503:
booster 59.9 C / 185.9 kW, waste N2 7.2 C with the 2 K warm end met). All four studies were
re-stamped and re-rated. The PIC-4101 note in the instrument list now mentions the turndown
venting. No P&ID, C&E, line list, equipment list or design basis changed.

Every node, scenario, safeguard, rating and action is still `status: proposed`, `by: agent`.
A script walked every `status` and `by` field in the four studies and found none other.
Nothing is accepted or approved.

Checks run at 5e263b4:
- `cheme safety hazop check`: H-01 .. H-04 are all `draft`, each with 0 errors and 0
  warnings. The only info is `hazop-unresolved`: 104 / 77 / 109 / 163 proposals, 453 in
  total. The only staleness reported is that of hazop-review2, which this record replaces.
- `cheme safety hazop rate H-01` .. `H-04` (read-only): every band is `current` (0 entries
  not current in each). Every band in the files comes from that tool.
- `cheme validate`: 0 errors, 57 warnings. None is `hazop-input-changed`. The other groups:
  13 instrument-no-interlock, 6 line-crossing, 12 template-metadata, 2 titleblock-sheet,
  3 process-energy-balance, and 21 review-finding-status / review-unknown-commit warnings on
  control-review1/2. Those two records name commits from before a squash merge. They are
  pre-existing and outside this scope.

**Recount from the files.** For each category the rule takes the residual where one is
given, else the initial. A scenario's band is the worst of its categories. The result is 218
scenarios: **86 high / 78 medium / 54 low**. None is very-high after safeguards, and 9 are
very-high before them. Every high scenario has at least one action. These figures match
D-098.

Verdict: **no critical, high or medium finding is open.** All seven findings are closed in
5e263b4. For #1, the rating differs from the one proposed, and the reason is recorded (see
the table). No new finding.

The four studies stay `draft` until a human team accepts the proposals. That means the owner
names the team, accepts or replaces the matrix, and the sessions accept, change or delete
each entry. After that the bands are rated again and a human review record is written. This
agent record does not make any study `assessed` or `reviewed`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-hazop-review3#1 | P-04 | H04-S02 / S75 / S77 | An over-draw needs no failure. The FIC-4148 limit is fixed at the design make (D-096), so at a reduced make with the customer taking the design rate, the vanes open above the make. | high | closed 5e263b4 | New H04-S79 (asset 3/E, high, nothing credited) and H04-S80 (people and asset 5/D very-high initial, 5/C high residual, LICA-3102 one order). New action H04-A28 asks for ratio limits, and A23 is extended. The S77 note is corrected. The reviewer proposed 5/E initial and 5/D residual for S80. The author applied the conditional order for "hydrocarbon present", as in H04-S75 and H03-S33, and recorded the alternative in S80's note for the team. The convention is consistent across the study, and the scenario ends high with actions, so this is accepted as justified. The team decides. |
| 2026-10-24-hazop-review3#2 | P-04 | H04-S13, PIC-4102 | PIC-4102's own failure was not analysed. | medium | closed 5e263b4 | New H04-S82 (PT-4102 low: high-high trip defeated, PSV-4122 two orders, 4/D -> 4/B medium) and H04-S83 (PT-4102 high: GOX vented for hours, people 3/D -> 3/C, asset 2/D -> 2/C). New action H04-A29 (independent transmitter for the trip, deviation alarm, PSV-4122 case at vanes open). SG05 is not credited in S82, which is correct. |
| 2026-10-24-hazop-review3#3 | P-04 | H04-S27 | A loop failure and normal demands were mixed under one D rating. | medium | closed 5e263b4 | S27 is now the loop failure only. New H04-S84 (demand above design, clamp credited one order, 3/E -> 3/D) and H04-S85 (reduced HP make, clamp is the cause, 3/E -> 3/E) both point to H04-A22 and, for S85, A28. |
| 2026-10-24-hazop-review3#4 | P-04 | H04-N5 | The GAN header leak had no containment deviation. | medium | closed 5e263b4 | New H04-N5-LK / H04-S86 (people 4/C high, nothing credited), parallel to S77. H04-A15 now covers GAN-4002 (clamp alarm, LIN backup start while K-4102 runs, flow balance). |
| 2026-10-24-hazop-review3#5 | P-04 | H-04 analysed inputs | The control the scenarios rest on is only in loops.yaml / sequences.yaml, which were not analysed inputs. | medium | closed 5e263b4 | Both are now in H-04's `analysed:` with their sha256, matching the files at 5e263b4. Drawing the low select and the cascade on P-04 stays open as a D-096 point. Whether H-01 .. H-03 also depend on them is left to the team; their scenarios were not reassessed against those files. |
| 2026-10-24-hazop-review3#6 | P-04 | H04-S76 | The people residual took two orders for a vent zone set for trips only. The PIC-4101 / PIC-3110 split was stated but not rated. | low | closed 5e263b4 | The S76 residual is now 3/D high, one order until H04-A26 is answered. New H04-S81 (asset 2/E medium, A26). The instrument-list note of PIC-4101 states the turndown venting. |
| 2026-10-24-hazop-review3#7 | P-04 | H04-S02 / S75 | The masking argument was applied unevenly. | low | closed 5e263b4 | The causes now name only FT-4148 reading low and the failures after the selector at the design make. The note explains the masking of PIC-4102 high and PT-4150 high, and how this changes at a reduced make (S79 / S80). The ratings are unchanged. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-hazop-review2#1 | H04-S07 asset residual lowered severity and likelihood on the same safeguard. | low | closed 169dc8b | In study.yaml the H04-S07 asset residual is 4/C (high), and `rate` reports it current. |
| 2026-10-24-hazop-review2#2 | A PROGRESS.md row was missing for the hazop-review1 #13 / #14 revision. | low | closed 169dc8b | PROGRESS.md has the row ("row added later, for bacc295 and 575447f"). 169dc8b and 5e263b4 each add their own row. |

## Checked and fine
- **Analysed inputs:** the sha256 of every `analysed:` path in the four studies matches the
  file at 5e263b4. validate gives no `hazop-input-changed`.
- **H-03 intents:** the booster outlet (59.9 C, 185.9 kW) and waste N2 (7.2 C, 2 K warm end)
  agree with process/flowsheet.yaml and with D-097 at f16c503. The K-3101 and E-3104
  datasheets give the same 59.93 C and 126.1 kW.
- **Safeguard references:** S80 credits H04-SG37 (LICA-3102), S82 credits H04-SG10
  (PSV-4122), S76 and S83 credit H04-SG28 (the vents). Each is a defined safeguard of H-04.
  Where the cause shares a transmitter or a controller with a safeguard (SG05 in S82, the low
  select in S79, the clamp in S85), that safeguard is not credited.
- **Action coverage:** every high scenario has an action. A28 and A29 are new. A15 and A23
  are extended without losing their earlier scope.

## Not checked
- The control design itself (loops.yaml and sequences.yaml content, the ratio limits of
  H04-A28, the anti-windup) belongs to the control review.
- Relief sizing for the S82 case (PSV-4122 with the guide vanes fully open) is H04-A29's to
  confirm.
- HAZOP team, sessions, matrix acceptance and the human review record: outside what an agent
  can do.
