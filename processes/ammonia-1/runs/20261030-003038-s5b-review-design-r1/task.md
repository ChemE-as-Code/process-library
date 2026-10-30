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


# Review this section's PR: S5b of ammonia-1 (PR #257), round 1
Review topic for the record: `design`.
This section ends with a stage sign-off: on `VERDICT: approve` do **not** merge.
Branch: stage/basic-layout (checked out). Earlier sections are merged on main.

## S5b basic close-out (on stage/basic-layout, PR #257; added 2026-10-30, interventions O-032)
S5 stopped after three review rounds with the high finding `2026-10-29-design#1` open and two
basic gates failing (`lifting-study`, `maturity-balanced`). Close them by engineering work, never
by accepting, relaxing or moving a gate. Read the review records in `reviews/` (newest `design`
and `layout`), `PROGRESS.md` and `build/pr-comment.md` first.
1. **maturity-balanced** (skills `process-design`, `reaction-evidence-search`, `reactions`,
   `process-simulation`): give the natural-gas feed flow and composition with provenance `given`
   and a published source; give each reactor's model basis (R-100, R-102A, H-101 and any other
   step `cheme maturity` names) from published sources: a sourced conversion or approach to
   equilibrium, or observations in `process/reaction-evidence.yaml` that cover it, or a declared
   equilibrium/Gibbs model whose data are given. Look sources up online; record each fact with
   URL/DOI and locator in our own words. Where a sourced value differs from the current one,
   change it, rerun `cheme process simulate --fill` and carry the effects (stream table, PFD,
   duties used by datasheets, TEA). Run `cheme maturity` until it reaches `balanced`, or say
   exactly which requirement no published source covers.
2. **lifting-study** (skills `layout-yaml`, `structures-access`, `pipe-routing`): run
   `cheme layout lifting`; resolve every lane by design: crane pads within reach, laydowns,
   moving or re-pinning lines that block a lane, relocating items where the plot plan allows, a
   crane chart that carries the lift. Do not accept findings. If lanes remain that only an
   erection-sequence acceptance can clear, list them in `build/lifting-acceptance-proposal.md`
   (item, blocking object, the lifting plan's reason) for the owner and do not write them into
   any accepted list.
3. **Class 4 estimate** (skill `mto-estimate`, `tea`): replace the example values of
   `estimate/rates.yaml` with published, sourced rates and factors (cost index with year and
   source, bulk unit rates, installation factors), each with status and source; equipment
   costs from sized items (for the major items you may run `cheme datasheets draft`/`fill`
   here; S7 completes the datasheets). State the class, its accuracy range and what is
   ASSUMED. Rebuild the take-off and estimate, update the TEA.
4. Close or answer the other open review findings where quick; carry the rest with a reason.
Rebuild layout, MTO and estimate; `cheme validate` 0 errors; `cheme check --stage basic` and
report each gate. End with STATUS: DONE when both gates pass, else BLOCKED with the exact
remaining requirement. The reviews after this job are the S5r reviews (topics `design`, `layout`).



At the very end, before the VERDICT line, add one line exactly like `FINDINGS: critical=<n> high=<n> medium=<n> low=<n>` counting only the findings new in this review (not carried ones).
