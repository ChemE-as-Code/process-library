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


# Review this section's PR: S2 of ammonia-1 (PR #244), round 1
Review topic for the record: `simulation`.
Branch: stage/basic-simulation (checked out). Earlier sections are merged on main.

## S2 process simulation (branch stage/basic-simulation)
Build the DWSIM model of the whole plant through core (skill `process-simulation`,
`process/simulation.yaml`, `cheme process simulate`), before any P&ID.
- First check that DWSIM starts (`cheme process methods`, a `cheme process simulate --check`);
  if it cannot be started, stop with `STATUS: BLOCKED: DWSIM` and change nothing.
- Choose the thermodynamic model with the skill `thermodynamic-model-selection` (cubic EOS for
  the syngas and the synthesis loop) and record the method-selection facts. State what the aMDEA
  CO2 removal needs; if DWSIM or core cannot represent it, keep it a specified block and say so.
- Every case of the design basis; recycles (synthesis loop, purge recovery, steam system)
  converged; solver, property package and versions recorded.
- Simulated values replace the balance script's specified ones where the simulation covers them,
  as `calculated` (`--fill`), never overwriting given or assumed values; deviations are findings
  in DESIGN.md, not edits.
- Close the energy audit (core's energy check on the converged run).
- Enable the template gate `maturity-balanced` (as the template documents it) and report
  `cheme maturity`. If core#315 keeps the plant below `predictive`, state exactly which
  requirement is unsupported; do not work around it.



At the very end, before the VERDICT line, add one line exactly like `FINDINGS: critical=<n> high=<n> medium=<n> low=<n>` counting only the findings new in this review (not carried ones).
