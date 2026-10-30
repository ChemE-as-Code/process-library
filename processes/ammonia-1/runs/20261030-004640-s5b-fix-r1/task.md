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


# Fix the open findings of the newest review of this section: S5b (PR #257), round 1
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

