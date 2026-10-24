---
topic: hazop
reviewed_commit: 1082e76d579307a0c731135ea6892fdced4ea23b
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
  - {path: DESIGN.md, revision: 1082e76d579307a0c731135ea6892fdced4ea23b, relation: depends-on}
reviewer: Claude (independent review agent; did not author the HAZOP studies, D-092 or the review1 fixes)
reviewer_kind: agent
branch: stage/basic-hazop
merge: pending
---
# Review: HAZOP of ASU-1 (H-01 .. H-04), first independent review and its fixes

This is an independent review of branch `stage/basic-hazop` at 1082e76. It covers the four draft
HAZOP studies and the proposed risk matrix, checked against the analysed P&IDs, lists, C&E and
DESIGN.md. The first pass ran at 210c008 and raised findings #1 .. #12. The author fixed them in
these commits:
- bfc0922: merge of origin/main (the ChemE-as-Code rename). It merged cleanly, and no HAZOP file
  used the old name;
- aaa3b15: the four studies revised. One credit convention went into every `assessment_basis`,
  the ratings were redone to it, and new scenarios H01-S43, H03-S51, H03-S52 and H04-S75 were
  added;
- 1082e76: D-092 updated and a PROGRESS.md row added.

Only `safety/hazop/**`, D-092 and PROGRESS.md changed. No P&ID, list, flowsheet, design basis,
layout, datasheet or C&E file changed. Every node, scenario, safeguard, rating and action is
`status: proposed`, `by: agent`. No team, session or approval is recorded. A safeguard was
checked against the files whenever a finding depended on it: PIC-3110 / PV-3110B, LICA-3102 and
its low alarm, TSLL-4113 / 4114, SSHH-3108, PDSLL-3115 and the fire wall FW-4101 (D-026, D-030,
layout). The HAZOP tool of core#147 writes the bands with `cheme safety hazop rate`. It reports
every band as current in all four studies.

Recounted from the files, the totals match D-092 (3): 207 scenarios; worst policy band 77 high,
75 medium and 55 low; none very-high after safeguards; 8 very-high before them. Every high
scenario has an action, and every action a scenario names exists.

The convention was swept by script: no residual likelihood drops by more than its listed
safeguards allow (relief or passive feature: two orders; any other safeguard: one order), and no
likelihood drops without a safeguard. The sweep found one pattern that it does not cover (#14).

Verdict: **no critical, high or medium finding is open.** Findings #1 .. #12 are closed in
aaa3b15 / 1082e76 (#12 in bfc0922 and aaa3b15). Two new low findings: #13 is a remnant of #12
in H01-S4, and #14 is a double credit in residual entries that lower the severity.

The studies stay `draft` until the owner names the team and the sessions accept the entries.
This agent record does not make any study `reviewed`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-hazop-review1#1 | P-01 / P-03 | H01-S33, C-1102 | PSV-3114 was credited for C-1102 although it is set at about 3.5 barg for C-3102, and the case "WN-1002 blocked and PIC-3110 failed" was not rated. Now H01-S33 credits H01-SG-PIC3110 (2/C -> 2/B). The new H01-S43 rates C-1102 rupture at 4/C high with nothing credited. The new H01-A25 asks for protection independent of WN-1002 and PIC-3110. D-092 (5) is corrected. | high | closed aaa3b15 | - |
| 2026-10-24-hazop-review1#2 | P-03 / P-04 | relief credit | A single relief valve was credited with three orders. The convention now gives at most two orders for a relief device whose listed case covers the cause. H03-S29, H04-S30, H04-S55, H04-S38 and H04-S60 are now 5/B high with actions (H03-A19, H04-A25, H04-A04). H03-S37, H04-S34, S50 and S71 are now D -> B. | medium | closed aaa3b15 | - |
| 2026-10-24-hazop-review1#3 | P-01 / P-03 / P-04 | non-independent credits | H01-S23 credited the I-03 that its cause bypasses, H04-S30 / S55 / S32 / S56 credited the PICA on the transmitter that fails, and H03-S7 credited the TICA-3124 alarm on the faulty measurement. All of these credits are withdrawn and the scenarios re-rated (H01-S23 3/D high with H01-A10; H03-S7 2/D). | medium | closed aaa3b15 | - |
| 2026-10-24-hazop-review1#4 | P-04 | H04-S27, H04-S68 | The likelihood was lowered with no safeguard listed. Both residuals now equal the initial rating (3/D, 4/D high), with actions H04-A22 and H04-A19. | medium | closed aaa3b15 | - |
| 2026-10-24-hazop-review1#5 | P-03 | H03-S25 | PSV-3114 was credited for an HP blow-through outside its listed case. The credit is withdrawn. Only PIC-3110 is credited (one order), so the scenario is 4/C high with H03-A20. | medium | closed aaa3b15 | - |
| 2026-10-24-hazop-review1#6 | P-03 / P-04 | H04-S02, H04-S75 | The sump draw-down from a GOX over-draw was missing. The new H04-S75 rates E-3103 uncovering at people / asset 5/C -> 5/B, crediting the LICA-3102 low alarm only, with H04-A23. H04-S02 now credits nothing for the draw-down. | medium | closed aaa3b15 | - |
| 2026-10-24-hazop-review1#7 | P-03 / P-04 | undeclared trips | Trips that are drawn but missing from the C&E got two orders. They are now limited to one order: H04-S49 4/C, H04-S48 / S70 C -> B, H03-S16 4/C and H03-S18 5/B. All stay with H04-A01 / A02 and H03-A2. | medium | closed aaa3b15 | - |
| 2026-10-24-hazop-review1#8 | P-04 | K-4101 people credit | The people credit rested on a "fire-safe enclosure". It now rests on the fire wall FW-4101 (new H04-SG36, open east side noted), H04-SG27 is retitled, and H04-A24 resolves D-002 against D-026 / D-030. | low | closed aaa3b15 | - |
| 2026-10-24-hazop-review1#9 | all | entry asphyxiation | Entry asphyxiation was rated inconsistently. H01-S36, H02-S35, H03-S47 and H04-S58 now share one basis, 5/C. D-092 (4) now files H04-S36 as an enrichment case. | low | closed aaa3b15 | - |
| 2026-10-24-hazop-review1#10 | P-03 | AIA-3103 | The failure of the only sump analyser was not rated. The new H03-S51 rates it at 5/C high with nothing credited, with H03-A24 (diagnostics, periodic sample, out-of-service rule). | low | closed aaa3b15 | - |
| 2026-10-24-hazop-review1#11 | P-03 | RL / LN trapped liquid | Trapped liquid in the cold box was not rated. The new H03-S52 rates it at 4/C high with nothing credited and routes it to H03-A20 (TSVs tagged and drawn). | low | closed aaa3b15 | - |
| 2026-10-24-hazop-review1#12 | - | housekeeping | The branch is now merged with origin/main (bfc0922), and the H01-SG-VIA1104 title now says its trip is not credited. The missing HAZOP gate in checks/checks.yaml is out of scope for this stage (only safety/**, D-092 and PROGRESS.md may change); it is recorded in D-092 for the stage that adds the gate. | low | closed aaa3b15 | - |
| 2026-10-24-hazop-review1#13 | P-01 | H01-S4 | The residual basis says that "VIA-1104 trips the machine on vibration" and uses that to lower the asset severity 4 -> 3 (3/C medium). Yet H01-SG-VIA1104 is an alarm whose trip is not credited, and that trip is not in the C&E. | low | open | Base the residual on PIC-1103 and the VIA-1104 alarm only, or credit the supplier trip as kind `other` with one order, and re-rate. |
| 2026-10-24-hazop-review1#14 | P-01 / P-04 | H04-S10, H04-S01, H01-S8 (asset) | Some residual entries lower the severity because the safeguard works, and also lower the likelihood by one step. The milder outcome then happens at the frequency of the cause (the matrix's residual likelihood is the frequency of the outcome). Examples: H04-S10 asset 4/D -> 2/C low should be 2/D medium; H04-S01 asset 4/D -> 3/C should be 3/D; H01-S8 3/D -> 2/C low should be 2/D medium. The action policy is not affected: H04-S01 is already high on people, and medium needs no action. | low | open | Where the residual severity is that of the safeguard working, keep the cause likelihood. Rate the safeguard-fails outcome as its own category entry or scenario. Re-run `cheme safety hazop rate --write`. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|

None: no earlier review record covers safety/hazop or safety/risk-matrix.yaml. The first-pass
findings at 210c008 are #1 .. #12 above.
