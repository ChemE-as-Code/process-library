---
topic: hazop
reviewed_commit: c707663dba7e3c42bc9b3519db3e52eeb5070254
scope: [safety/hazop/H-01, safety/hazop/H-02, safety/hazop/H-03, safety/hazop/H-04, safety/risk-matrix.yaml]
basis:
  - {path: pid/P-01.xml, revision: 'sha256:c3b9a332a2200a9738e68801bf15e1f94c58264fbbd1e506c03c7045725ba5af', relation: analyses}
  - {path: pid/P-02.xml, revision: 'sha256:f6b4904d694ef94994fa3c5af7e903503134e9b9415e93794cdb4fe44e33ade6', relation: analyses}
  - {path: pid/P-03.xml, revision: 'sha256:e633f6e71bb6a9926e184eeab53287e44529b4cd209fb0a87cfbbe5a7db09974', relation: analyses}
  - {path: pid/P-04.xml, revision: 'sha256:c06f81101caad81404d0694aa8ba27aad670b2bdfd5e884f0d3f39c1dc66efe5', relation: analyses}
  - {path: control/cause-effect.yaml, revision: 'sha256:b9c8e56cbc49b1b9d9595e39b02fbaa24fdffdf137d402bcd253b329b9299ca5', relation: analyses}
  - {path: control/instrument-list.yaml, revision: 'sha256:328523d1bcb51ae744867889f922f4bf01c619efaf155f01d0e275bffc6b3d2f', relation: analyses}
  - {path: equipment/equipment-list.yaml, revision: 'sha256:7dd6ae258db62812479ac0e0e7c520b82a46de4f02ee2020db2f5d4013870490', relation: analyses}
  - {path: piping/line-list.yaml, revision: 'sha256:3643188e55a2e5b9128b4b6c25a3e8b71bbd07e4fdb3fbe0d47ade72261f1485', relation: analyses}
  - {path: piping/special-items.yaml, revision: 'sha256:8071c9646730d15356f23923163a5416205ea568dbb9592a61fb49e9d19077d0', relation: analyses}
  - {path: process/design-basis.yaml, revision: 'sha256:db3372d4b36b2577ddeab2c14f7ca16db622a3d5d32dddc006ff9a1551ff0281', relation: analyses}
  - {path: process/flowsheet.yaml, revision: 'sha256:0017d59880eecae9cd7e13b285dc48460a928774b6097389b6b253b5717b7d39', relation: analyses}
  - {path: DESIGN.md, revision: c707663dba7e3c42bc9b3519db3e52eeb5070254, relation: depends-on}
reviewer: Claude (independent review agent; did not author the HAZOP studies, D-093, the review1 fixes or the merge)
reviewer_kind: agent
branch: stage/basic-hazop
merge: pending
---
# Review: HAZOP of ASU-1 (H-01 .. H-04), second independent review

This is an independent review of branch `stage/basic-hazop` at c707663. It checks the fixes
for the two low findings that hazop-review1 left open, and the merge of origin/main. Three
commits came after hazop-review1 (1082e76):
- bacc295: H-01 and H-04 revised for hazop-review1#13 and #14;
- 575447f: the HAZOP decision's counts set to 78 high / 75 medium / 54 low;
- c707663: merge of origin/main, which brought the LCA decision D-092 (process-library#35).
  The HAZOP decision was renumbered from D-092 to D-093 in DESIGN.md and PROGRESS.md.

No P&ID, list, flowsheet, design basis, layout, datasheet or C&E file changed. The analysed
inputs still hash to the revisions in every study's `analysed:`. Every node, scenario,
safeguard, rating and action is still `status: proposed`, `by: agent`, and nothing is
accepted or approved.

Checks run at c707663:
- `cheme safety hazop check`: H-01 .. H-04 are all `draft`, each with 0 errors and 0 warnings.
  The only info is `hazop-unresolved`: 104 / 77 / 109 / 148 proposals, 438 in total.
- `cheme safety hazop rate H-01` .. `H-04` (read-only): every band is `current`. Every band
  in the files comes from that tool.
- `cheme validate`: 0 errors, 39 warnings. origin/main also gives 0 errors and 39 warnings.
- `cheme check --no-write`: seven gates fail, the same seven on the branch and on a fresh
  worktree of origin/main (43f8cf5). layout-3d, lifting-study, layout-detail, electrical and
  hvac fail on `layout-model-version`. process-balances and process-basic fail on
  `cheme.generated-version` (BFD / PFD). All seven are pre-existing on main and outside this
  stage. The branch fails no gate that main passes.

**Recount from the files.** For each category the rule takes the residual where one is given,
else the initial. A scenario's band is the worst of its categories. The result is 207
scenarios: H-01 11 / 14 / 18, H-02 13 / 14 / 10, H-03 23 / 19 / 10, H-04 31 / 28 / 16, total
**78 high / 75 medium / 54 low**. None is very-high after safeguards, and 8 are very-high
before them. These numbers match the D-093 (3) table, and so do its counts of nodes (44),
deviations (190), safeguards (101), actions (86) and proposals (438). Every high scenario
has at least one action.

**Merge resolution.** DESIGN.md runs D-091, then D-092 (LCA), then D-093 (HAZOP).
`git diff origin/main -- processes/asu-1/DESIGN.md` adds only the D-093 section; D-092 is
unchanged. Outside reviews/, every "D-092" left refers to the LCA: AGENTS.md, lca/*,
PROGRESS.md and the D-092 heading. None points at the HAZOP. PROGRESS.md keeps all 200 rows
of origin/main and all 201 rows of the branch side. The branch's two HAZOP rows now read
D-093 in place of D-092, which is the only change to them.

**hazop-review1#13** is closed in bacc295. H01-S4 now credits only PIC-1103 as one control
layer (asset 4/D -> 4/C, high, H01-A6), and its basis says that the VIA-1104 trip is not
credited. The other VIA-1104 bases (H01-S1, S5, S6, S41) now say "alarm, trip not credited".
None of them lowered a severity on the trip.

**hazop-review1#14** is closed for the three entries it named, in bacc295. H01-S8 asset is
now 2/D medium, H04-S01 asset 3/D high and H04-S10 asset 2/D medium. In each, the safeguard
lowers the severity only, and the likelihood stays that of the cause. A script then swept
every residual entry for a lowered severity together with a lowered likelihood. It found one
entry left, H04-S07 asset (#1).

hazop-review1#1 .. #12 were closed before hazop-review1 was committed (aaa3b15, 1082e76,
bfc0922). No regression was found at c707663: the bands are current, and the sweep is clean
except for #1.

Verdict: **no critical, high or medium finding is open.** hazop-review1#13 and #14 are
closed. Two new low findings are open: #1, the last instance of the hazop-review1#14
pattern, and #2, a missing PROGRESS.md row.

The four studies stay `draft` until a human team accepts the proposals. That means the
owner names the team, accepts or replaces the matrix, and the sessions accept, change or
delete each entry. After that the bands are rated again and a human review record is
written. This agent record does not make any study `assessed` or `reviewed`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-hazop-review2#1 | P-04 | H04-S07 (asset) | The residual asset entry is 5/C -> 4/B ("the trip and blowdown limit the fire to the machine"). The TSHH-4104 trip (not in the C&E, one order) and the blowdown both lower the severity (5 -> 4) and also lower the likelihood by one order. The outcome with the trip working happens at the frequency of the cause, so this should be 4/C (high). The outcome with the trip failing is 5/B (high). Either way the scenario becomes high, not medium, and the D-093 totals become 79 high / 74 medium / 54 low. The action policy is not affected, because H04-S07 already has H04-A01, A02, A13 and A24. | low | open | Re-rate H04-S07 asset to 4/C, or to 5/B with the trip credited for the likelihood only. Run `cheme safety hazop rate H-04 --target H04-S07 --write`, then update the D-093 (3) counts. |
| 2026-10-24-hazop-review2#2 | - | PROGRESS.md | bacc295 and 575447f (re-ratings for hazop-review1#13 and #14, new D-093 totals) have no PROGRESS.md row. AGENTS.md asks for a row with every change. The newest HAZOP change row still gives the earlier totals of 77 / 75 / 55. | low | open | Add a row for the hazop-review1#13 / #14 revision with the new totals, together with the #1 fix. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-24-hazop-review1#13 | H01-S4: the residual lowered the severity on the VIA-1104 trip, which is neither credited nor in the C&E. Now 4/C high: PIC-1103 is credited as one layer, the severity stays 4, and the action is H01-A6. The VIA-1104 bases say alarm. | low | closed bacc295 | H-01 study.yaml H01-S4 residual; `cheme safety hazop rate H-01` current |
| 2026-10-24-hazop-review1#14 | Severity and likelihood lowered for the same safeguard. The named entries are now H01-S8 2/D medium, H04-S01 asset 3/D high and H04-S10 asset 2/D medium, and the D-093 counts are updated (575447f). The remaining instance is #1. | low | closed bacc295 | H-01 / H-04 study.yaml; sweep by script; `cheme safety hazop rate H-04` current |
