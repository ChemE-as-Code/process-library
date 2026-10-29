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


# Review this section's PR: S3a of ammonia-1 (PR #246), round 1
Review topic for the record: `pids-front`.
Branch: stage/basic-pids-front (checked out). Earlier sections are merged on main.

## S3a / S3b / S3c P&IDs (branches stage/basic-pids-front, -mid, -loop)
Draft complete P&IDs (DEXPI 2.0.1, skills `pid-draft`, `pid-design-*`, `dexpi-xml`) from the
simulated PFD, `cheme validate` clean at error level, lists updated with every sheet:
- S3a (front): feed gas, desulphurisation, primary and secondary reforming, waste-heat recovery,
  HT/LT shift.
- S3b (mid): aMDEA CO2 removal, methanation, synthesis-gas compression.
- S3c (loop): synthesis loop, converter, refrigeration, ammonia separation and storage interface,
  purge-gas recovery, steam and BFW system and the main utilities headers.
Off-page connectors consistent across sheets; render and look at each sheet; gates pids-exist,
pids-valid, drawing-clean, process-basic, process-links.


Your part: **S3a (front)** only; the other parts are separate sections.


At the very end, before the VERDICT line, add one line exactly like `FINDINGS: critical=<n> high=<n> medium=<n> low=<n>` counting only the findings new in this review (not carried ones).
