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


# Review this section's PR: S5e of ammonia-1 (PR #257), round 1
Review topic for the record: `design`.
This section ends with a stage sign-off: on `VERDICT: approve` do **not** merge.
Branch: stage/basic-layout (checked out). Earlier sections are merged on main.

## S5e lifting lanes with motor cable entry points (on stage/basic-layout, PR #257; I-007)
cheme is now core v1.1.0 (installed; the same version CI pins): a motor's `cable_entry` in
`electrical/electrical-list.yaml` ends its tray beside the machine (core#73, ADR 0035; skill
`electrical-cabling`). S5c (D-041) left gate `lifting-study` failing on the lanes of K-101,
K-102, K-103 and K-701, blocked by their motor trays; the owner did not accept these and asked
to clear them by design (I-007). Also, three lanes the owner accepted in I-006 (K-501, E-504,
E-505) picked up extra blockers in S9 (K-501 motor tray, E-504 instrument tray, E-505 cooling-water
lines of E-503): clear those extra blockers by design too where possible, and otherwise say so;
the acceptance covers only the blockers named in the original proposal.
1. Run `cheme skills update` for the skills changed in 1.1.0 (keep local changes, report them).
2. Give cable entry points to K-101, K-102, K-103, K-701 and K-501 (side away from the lift lane,
   real terminal-box side where the datasheet says), rebuild `cheme layout build`, then
   `cheme layout lifting`; fix the remaining tray/line blockers by routing intents, pad or lane
   changes. Never accept a lane yourself.
3. Rebuild cable schedule (`cheme layout cables --write`), MTO and estimate if quantities moved;
   `cheme validate` 0 errors; `cheme check` and `cheme maturity`; DESIGN.md decision (next free
   D-number) and PROGRESS.md; commit; `build/pr-comment.md` short summary.
STATUS: DONE when every basic gate except the two review gates passes, else BLOCKED with the
exact remaining requirement. The basic reviews (topics `design`, `layout`), sign-off and merge follow.



At the very end, before the VERDICT line, add one line exactly like `FINDINGS: critical=<n> high=<n> medium=<n> low=<n>` counting only the findings new in this review (not carried ones).
