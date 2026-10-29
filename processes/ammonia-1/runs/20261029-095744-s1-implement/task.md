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


# Your section: S1 concept close-out of ammonia-1
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
