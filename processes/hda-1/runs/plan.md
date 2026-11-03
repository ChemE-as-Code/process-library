# hda-1 full-design campaign: plan

Issue: process-library#302. Goal: take hda-1 (thermal toluene hydrodealkylation to benzene,
100 kt/a) from its concept state to a complete design, the way processes/ammonia-1 was taken
(its `runs/plan.md` and `runs/orchestration/prompts/sections.md` are the model, and ammonia-1's
files are the worked example of every deliverable): simulation, basic engineering with the 3D
layout and the class 4 estimate, HAZOP, datasheets, relief, and the detail gates as far as they
go. Written 2026-11-03 at the start of section S1.

## Orchestration

The campaign is run by Claude Code workflows. Each section is a workflow step that starts an
implementation job, followed by independent review jobs. There is no budget, key-batch or
cost-cap machinery and no `jobs.py` runner, unlike ammonia-1. The orchestration pauses between
sections to stay within the session limits. A job does its section on its branch, commits,
pushes and opens a PR ("Refs #302"). It never pushes to `main`, never force-pushes, never
rebases and never signs off its own stage. Reviews and merges are separate jobs. A stage
sign-off (`cheme check --stage <s> --write --review <record>`) is the last commit of the
section's branch and counts once merged.

## Starting point (not redone)

hda-1 on `main` at the start of S1 (merge of #319, f5af9991): concept stage, 2 blocks and 15
steps, 18 equipment items, 24 lines, decisions D-001 to D-015, open inputs I-01 to I-12, a
preliminary LCI, and review `reviews/2026-10-27-pfd-lci-review.md` (#4, #7, #9 and #12 open).
- Simulation: a converged whole-plant DWSIM run (D-014) with Peng-Robinson. The package is not
  qualified for aromatics with H2/CH4 (core#315), and C-201's duties stay from the balance
  script.
- IDAES cross-check of the feed section (D-015). On the current flowsheet IDAES can simulate no
  part of the plant: it has no biphenyl, no two-sided exchanger and no column.
- Earlier sessions: `runs/2026102*`.

## Versions (fixed for the campaign)

- core / `cheme`: **v1.4.1** (`cheme 1.4.1 (pyDEXPI 2.1.0)`), the version library CI pins.
  Nothing is installed or upgraded during the campaign. A core limit is reported precisely
  (in DESIGN.md and the PR), never worked around by relaxing a check.
- DWSIM: **9.0.5** in the Docker image `cheme-dwsim:9.0.5`.
- Skills: the bundled skills of v1.4.1 (`cheme skills update` in `processes/hda-1`; not in git).
- Windows worktrees can show CRLF noise in `fmt` and golden checks; Linux CI is the judge.

## Sections and the gates each must pass

One branch `stage/hda-1-<topic>` from `origin/main` per section and one worktree each.

| S | section | branch | gates and deliverables |
|---|---|---|---|
| S1 | Concept close-out | `stage/hda-1-concept-closeout` | all concept gates (design-basis, concept-lists, process-concept, process-balances, process-links-concept, assumptions-marked, layout-plot-plan, issues-concept); the open review findings closed or carried with a reason; I-01..I-12 resolved or ASSUMED/carried with a reason; BFD/PFD rebuilt with v1.4.1; plot plan; class 5 estimate and screening TEA (`estimate/tea.yaml`); **concept sign-off** (by the sign-off job, not the implementer) |
| S2 | Simulation close-out | `stage/hda-1-basic-simulation` | `cheme process simulate --check` converged for every design-basis case; recycles converged; the D-014 deviations resolved or kept with a reason (implicit pumps, product cooler I-12, stabiliser model); `process-balances` on simulated values; energy audit closed; template gate `maturity-balanced` enabled and evaluated; `cheme maturity` reported with the exact unsupported requirement (core#315, sourced boundary, R101 model basis) |
| S3 | P&IDs | `stage/hda-1-basic-pids` (one or more jobs) | DEXPI 2.0.1 P&IDs of the whole PFD; pids-exist, pids-valid (0 errors), drawing-clean, process-basic, process-links; off-page connectors consistent; every sheet rendered and looked at |
| S4 | Control and lists | `stage/hda-1-basic-control-lists` | equipment, line and instrument lists complete and linked (validate clean); loops, sequences, interlocks, cause and effect (`cheme control report` clean); narrative and philosophy; PFD current |
| S5 | 3D layout, MTO, class 4 estimate | `stage/hda-1-basic-layout` | layout-3d (every DN25+ process line routed or skipped with a reason, every elevated item mounted), zones, lifting study, mto, template gate `tea` enabled; class 4 estimate from datasheet sizes |
| S5r | Basic reviews and sign-off | (on S5's branch) | design review and layout review (`reviewer_kind: agent`), all basic gates; **basic sign-off** |
| S6 | HAZOP | `stage/hda-1-basic-hazop` | HAZOP of all P&IDs rated against `safety/risk-matrix.yaml`; `cheme safety hazop check` clean; actions closed or carried with owner and reason |
| S7 | Datasheets | `stage/hda-1-detail-datasheets` | gate `datasheets`: every equipment-list item, sized from the simulation, provenance on every value |
| S8 | Relief | `stage/hda-1-detail-relief` | relief scenarios for every relief device (skill `relief-scenarios`), governing case and required capacity per device; what core cannot size stated; template gate `relief-on-pid` |
| S9 | Detail gates | `stage/hda-1-detail-gates` | detail gates as far as they go (control-complete, layout-detail, electrical, hvac, datasheets, issues-detail), pass/fail reported per gate |

A gate is never relaxed, skipped or accepted to get further. A template gate is enabled
(uncommented, as the template documents it) where the section names it; that is not a
relaxation. A plant-specific gate added by a job is listed in its PR.

## Rules for every job

- Library `CLAUDE.md` and `processes/hda-1/AGENTS.md`. No third-party tables, figures or text.
  Facts go in our own words with the source and its exact locator. Estimates are ASSUMED with
  the reason. No value or source is invented: real, citable data come from web search or fetch.
- Each change is a row in `PROGRESS.md`; each decision is a DESIGN.md entry (next free D-number).
- Commits in logical steps with the trailer `Co-Authored-By: Claude Opus 5.5
  <noreply@anthropic.com>`. Before finishing: `cheme validate`, `cheme check`, `cheme maturity`;
  push the branch and open the PR.
- Stop and report (do not work around) when DWSIM cannot be started, when core needs a fix,
  when the design brief would change, or when a gate would have to be relaxed.

## Records

- `PROGRESS.md` (changes), `DESIGN.md` (decisions), `reviews/` (review records and responses).
- `runs/<run-id>/` where a job records its session with `cheme runs record`.
- PR bodies: what was done against each gate with check results and numbers, sources,
  ASSUMED values added, open items.
