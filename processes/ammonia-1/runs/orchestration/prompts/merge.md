# Context: merge job after a stage sign-off (ammonia-1 platform-paper run)

You are a reviewer-side session. The stage branch checked out here was approved by an independent
agent review and then signed off by an author-side session. Find the PR with
`gh pr list --head "$(git branch --show-current)" --state open`.

1. Check that the commits after the approving review's `reviewed_commit` change only
   `checks/status.json` (and run records under `runs/`). Anything else: do not merge, comment on
   the PR, end with `VERDICT: fix`.
2. `cheme check --stage <stage>` passes; `git fetch origin && git merge origin/main` (never
   rebase), push (never force, never to main), `gh pr checks <n> --watch` until green.
3. `gh pr merge <n> --merge`. Comment that the stage sign-off is now on `main`.
4. End with two lines: `VERDICT: approve` (merged) or `VERDICT: fix` (not merged, with the reason), then
   `STATUS: DONE`.
