# Context: fix job of the ammonia-1 platform-paper run

You are a headless agent session revising one section of the ammonia-1 design after an
independent review (process-library#86). Your working directory is `processes/ammonia-1` on the
section's branch. Read `runs/plan.md` and the newest review record in `reviews/`.

- Close every **critical and high** finding first, then medium/low where quick. Never edit or
  delete a review record or a run record. For each finding: the change and its commit, appended
  as a "Response" entry in PROGRESS.md.
- Same rules as implementation jobs: AGENTS.md, library CLAUDE.md (sources, ASSUMED), never relax,
  skip or accept a gate or finding, report core limits instead of working around them, no
  invented data.
- Re-run `cheme validate`, `cheme check`, `cheme maturity` and the section's own checks; commit
  everything; write a short PR comment text to `build/pr-comment.md` (findings closed, left open
  and why). You cannot push and must not merge.
- Final line: `STATUS: DONE` or `STATUS: BLOCKED: <reason>`.


# Fix the open findings of the newest review of this section: S6 (PR #38), round 1
Branch: stage/basic-hazop (checked out). Earlier sections are merged on main.

## S6 HAZOP (branch stage/basic-hazop)
HAZOP of all P&IDs (skills `hazop-study`, `hazop-equipment-causes`, `hazop-assessment`,
`safeguard-crediting`): nodes, deviations, causes, consequences, safeguards, actions; rated with
`cheme safety hazop rate` against `safety/risk-matrix.yaml`; everything stays `status: proposed`
(AGENTS.md); `cheme safety hazop check` clean; actions closed or carried with an owner and reason.

