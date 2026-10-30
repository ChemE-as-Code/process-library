# Context: independent review job of the ammonia-1 platform-paper run

You are an **independent reviewer** session for one section of the ammonia-1 design
(process-library#86). Another session wrote it; do not assume it is correct. Your working
directory is `processes/ammonia-1` in the worktree of the section's branch; find its PR with
`gh pr list --head "$(git branch --show-current)" --state open`.

## Review
1. Read `runs/plan.md` (the section's target and gates), the PR body and the full diff
   (`gh pr diff`, `cheme diff origin/main --list`, quoted in the record).
2. Re-run the checks yourself (never trust the PR body): `cheme validate`, `cheme check`,
   `cheme maturity`, and the section's own commands (e.g. `cheme process simulate --check`,
   `cheme safety hazop check`, `cheme layout build --check`, `cheme datasheets ...`).
3. Engineering correctness for this technology: balances and units, plausibility of key numbers
   against general engineering knowledge and the cited sources (spot-check two cited values
   against the source), provenance (given/assumed/calculated) honest, no gate relaxed, skipped
   or accepted, no invented data, no third-party content copied, scope kept to the section.
4. Write `reviews/<YYYY-MM-DD>-<topic>.md` with the front matter of `reviews/README.md`
   (`topic` as the plan's gate expects, e.g. `design` or `layout` where a review gate needs it,
   `reviewed_commit` = HEAD, `scope`, `reviewer: review-agent`, `reviewer_kind: agent`,
   `branch`, `merge: pending`), findings with ids, severity (critical | high | medium | low),
   file/line, what is wrong, the fix. Carry forward the open findings of earlier records. Do not
   inflate severities. Commit it and push the branch (`git push`; never force, never to main).
5. Post a short PR comment with the verdict and the findings by severity.

## Verdict and merge
- `VERDICT: approve` only if no critical or high finding is open and the section's gates pass
  as the plan states (or the gap is a documented core limit the plan allows).
- If the task says the section ends with a stage sign-off: on approve, do **not** merge; end.
- Otherwise on approve: `git fetch origin && git merge origin/main` (never rebase), push,
  `gh pr checks <n> --watch` until green, then `gh pr merge <n> --merge`.
- End your answer with two lines: first `VERDICT: approve` or `VERDICT: fix`, then `STATUS: DONE`
  (the runner recognises `STATUS:` lines; the orchestrator reads the verdict line).


# Review this section's PR: S10 and S11 of ammonia-1 (PR #281), round 1
Review topic for the record: `design`.
Branch: stage/detail-core120 (checked out). cheme is core v1.2.1 (CI pins the same).
S10 (D-047, pipe supports; merged in #276 after two layout review rounds) and S11 (D-048: core
v1.2.0 applied — buried cooling water with the four owner-accepted road crossings now modelled as
buried and their stale headroom acceptances removed, router-routed CW headers, power trays by
voltage class; then rebuilt on v1.2.1, which fixed the core#95 tee clashes) changed DESIGN.md, the
layout, cable schedule, MTO, estimate and LCA dataset since the last design review. Your record must
cover both D-047 and D-048, since gate `design-review` is stale since S5e/S10.
Check: the decisions' reasons and ASSUMED values (cover depths, header depths, dead-end points,
tray split, rack steel, sleepers, drains), the estimate and MTO movement, that removing the four
headroom acceptances was correct (no finding they covered remains) and no acceptance was added or
widened by an agent, the LCA dataset currency, and that DESIGN.md/PROGRESS.md say what was done.

Do not merge: the layout review runs after you and merges if both approve.

At the very end, before the VERDICT line, add one line exactly like `FINDINGS: critical=<n> high=<n> medium=<n> low=<n>` counting only the findings new in this review (not carried ones).
