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


# Your job: fix the S10 review findings of ammonia-1 (PR #276, branch stage/detail-supports)
Branch: stage/detail-supports (checked out). cheme is core v1.1.0. Read the review record
`reviews/2026-10-30-layout-s10.md` and the PR comment. Fix by design, not by acceptance:
- s10#1 (high): move the PC-1083 route at least the required clearance off V-401's platform-1
  ladder; the ladder-clearance warning that main does not have must be gone.
- s10#2 (medium): put the new low-point drains and the CO2-1142 vent drain pot where the design
  tracks them (P&IDs P-106, P-107, P-113 with `cheme pid` tooling, line list), and state in D-047
  where the CO2-1142 dip drains to and how it is kept from freezing (ASSUMED where no source).
- s10#3 (low): restore K-501's motor tray to the side away from its lane if a cable entry or
  routing intent allows it, else say why.
- s10#4 (low): record pedestrian/vehicle crossings over the new low runs (crossing steps or
  sleepers in the layout where the model has them, else listed in D-047) and add the sleepers to
  the take-off if the MTO can carry them, else say so.
- s10#5 (low): not yours (a design review follows the next job); leave it.
Rebuild layout, MTO and estimate; `cheme validate` 0 errors; `cheme check`; update D-047 and
PROGRESS.md; commit; `build/pr-comment.md` with what was fixed and how.
Never accept a finding. Final line: STATUS: DONE or STATUS: BLOCKED: <reason>.
