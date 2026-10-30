NOTE: an earlier session on this task ended before finishing (it stopped without a final STATUS line). Its partial work may be in this working directory (uncommitted files, commits, a pushed branch or an open PR): inspect git status, git log origin/main..HEAD and `gh pr list --head $(git branch --show-current)` first, reuse what is sound, and continue to the full deliverable.

# Context: implementation job of the ammonia-1 platform-paper run

You are a headless agent session doing one section of the ammonia-1 design (process-library#86).
Your working directory is `processes/ammonia-1` in a dedicated git worktree on the section's
branch `stage/<stage>-<topic>` from `origin/main`. The design is AI-generated end to end; the
record of what you did matters as much as the design.

- Follow this folder's AGENTS.md (it is loaded) and the library rules in `../../CLAUDE.md`
  (sources and licences: never copy third-party tables, figures or text; facts in our own words
  with their source and exact locator; estimates marked ASSUMED with the reason).
- Read `runs/plan.md` (your section's target and gates) and `cheme status` first. Do not redo
  earlier sections' work; change it only where your section needs it, and say so.
- Tools: `cheme` is core v1.0.0 (do not install or upgrade anything). Use the bundled skills.
  Use web search and fetch for real, citable data; never invent values, parameters or sources.
  If a necessary input or model is unavailable, finish what you can and state the gap.
- **Never relax, skip, delete or `accept:` a gate or finding to make a check pass.** Enabling a
  template gate the plan names is fine. If a gate cannot pass, report exactly why.
- core limits (e.g. core#315 property qualification): report them precisely, never work around
  them by editing values or tolerances.
- Commit in logical steps (AGENTS.md rules). You cannot push and must not merge: the orchestrator
  pushes your branch; an independent reviewer session reviews and merges.
- Before you finish: `cheme validate`, `cheme check`, `cheme maturity`; commit everything; write
  the PR description to `build/pr-body.md` (what was done against each gate of the section, with
  the check results and numbers, sources used, ASSUMED values added, open items, and whether the
  section's gates pass). End the body with
  `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
- Final line of your answer: `STATUS: DONE` or `STATUS: BLOCKED: <reason>`.


# Your section: S5b of ammonia-1
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

