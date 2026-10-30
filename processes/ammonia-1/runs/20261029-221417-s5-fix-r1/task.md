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


# Fix the open findings of the newest review of this section: S5 (PR #257), round 1
Branch: stage/basic-layout (checked out). Earlier sections are merged on main.

## S5 3D layout, MTO and class 4 estimate (branch stage/basic-layout)
3D layout (skills `layout-yaml`, `pipe-routing`, `structures-access`, `area-classification`):
every DN25 and larger process line routed, zones declared, gates layout-3d, lifting-study, mto;
MTO and class 4 estimate (`cheme assess mto`, `cheme assess estimate`, skill `mto-estimate`) and
TEA updated; enable the template gate `tea` as documented.

## S5r basic reviews and sign-off (on stage/basic-layout)
Two independent review jobs: a design review (topic `design`, the P&IDs, lists, control and
simulation of S2-S4) and a layout review (topic `layout`). Then the basic sign-off job and the
merge job.

