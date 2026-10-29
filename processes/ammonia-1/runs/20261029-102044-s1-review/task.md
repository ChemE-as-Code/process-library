NOTE: an earlier session on this task ended before finishing (it stopped without a final STATUS line). Its partial work may be in this working directory (uncommitted files, commits, a pushed branch or an open PR): inspect git status, git log origin/main..HEAD and `gh pr list --head $(git branch --show-current)` first, reuse what is sound, and continue to the full deliverable.

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
- Final line of your answer: `VERDICT: approve` or `VERDICT: fix`.


# Review this section's PR: S1 concept close-out of ammonia-1 (PR #241)
This section ends with a stage sign-off: on `VERDICT: approve` do **not** merge; the sign-off and merge jobs follow. Review topic for the record: `concept`.
Branch: stage/concept-closeout (checked out).

## S1 concept close-out (branch stage/concept-closeout; ends with the concept sign-off)
Close the concept stage of ammonia-1.
- Run `cheme skills status`; update outdated bundled skills that are not locally modified
  (`cheme skills update`), and say which.
- Close or carry, each with a reason, the open findings R-01..R-05 of
  `reviews/2026-10-27-pfd-lci-review.md` (R-03: the natural-gas composition and supply pressure;
  source them from an open, citable reference for the brief's site or, if none exists, keep them
  ASSUMED with the reason and the effect on `cheme maturity`).
- Resolve the open inputs I-01..I-10 in DESIGN.md, or keep each ASSUMED with a reason.
- Rebuild the BFD/PFD with this core (`cheme process build`) so no generated-version finding is left.
- Plot plan: `layout/site-plan.yaml` and `layout/equipment-placement.yaml` for the 44 items with
  areas, roads, racks and the spacing criteria as `separations:` (skill `layout-yaml`), gate
  `layout-plot-plan`.
- Economics: the decision the next stage needs, an AACE class 5 capital estimate, sourced prices
  of the main feeds and products, and a screening TEA with the dominant premises
  (`estimate/tea.yaml`, skill `tea`).
- All concept gates must pass. Do not sign off yourself: the review and sign-off jobs follow.
