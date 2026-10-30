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


# Review this section's PR: S10 of ammonia-1 (PR #276), round 1
Review topic for the record: `layout`.
This section has no stage sign-off: on `VERDICT: approve` merge PR #276 yourself (squash or merge
commit as the earlier sections did) once CI is green; on `VERDICT: fix` do not merge.
Branch: stage/detail-supports (checked out), based on main after the basic sign-off.

## S10 pipe supports (owner request I-009, with core#90)
The 3D model showed about 420 single full-height T-posts. The implement job (decision D-047)
added intermediate rack steel on the small-bore tiers, routed small lines low on sleepers or onto
racks, and rebuilt the layout, MTO and estimate. Claimed: posts 420 -> 252, free-span warnings
73 -> 41, the same 8 lifting findings as at basic sign-off, steel 555.1 -> 672.2 t, bulk estimate
+3.9 %, gates and maturity unchanged, new ASSUMED values listed in D-047.
Check that the claims reproduce (`cheme layout build`, `cheme layout lifting`, `cheme check`,
`cheme maturity`, `cheme validate`), that no gate, rule or acceptance was relaxed or added by an
agent, that new steel and sleeper routes do not create clashes, headroom or access problems (roads,
escape routes, lifting lanes), that the new low points have drains recorded, that the MTO and
estimate are rebuilt from the current model, and that DESIGN.md D-047 states its reasons and
ASSUMED values in our own words. The core routing issue it reports (split lines lose their rack)
is the orchestrator's to file; do not work around it.



At the very end, before the VERDICT line, add one line exactly like `FINDINGS: critical=<n> high=<n> medium=<n> low=<n>` counting only the findings new in this review (not carried ones).
