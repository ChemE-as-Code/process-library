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


# Your job: S10 pipe supports of ammonia-1 (branch stage/detail-supports; owner decision I-009)
Branch: stage/detail-supports (checked out), from main (basic signed off, tag nh3-run-final).
cheme is core v1.1.0.

Problem: `cheme layout build` generates **420 single full-height support posts** (`t_post`,
HEB200 from grade to the pipe) for 83 lines, wherever an off-rack run spans more than the
ASSUMED maximum unsupported length and no steel is near: median 7.9 m, 166 above 8 m, max
15.3 m; PG-1126 (DN 40 inert vent, ~100 m) alone has 54, then PG-1109 and CO2-1142 (27 each),
AL-1124 (24), DW-1073 (22). All are `review_needed`. They are unrealistic and inflate the MTO
steel and the estimate. The core-side fix is core#90 (not yours; do not work around core).

Do, by design (skills `pipe-routing`, `layout-yaml`, `structures-access`, `mto-estimate`):
1. Set a sourced `max_unsupported_length` (site plan) per DN if you can find an open, citable
   span table (cite it, our own words; else keep core's ASSUMED table and say so).
2. Route long small-bore and utility lines (vents, drains, chemicals, water, inert gas) along the
   racks or existing structures with routing intents (`rack`, `tier`, `via`, `elevation`), group
   parallel runs, bring lines low (sleeper elevation) where they run at grade, and shorten
   off-rack legs; use existing steel (rack, structures, platforms) where the build lets you.
3. Rebuild (`cheme layout build`), then report the post count, heights and the lines that still
   need posts and why; keep 0 clashes and every basic gate passing (`cheme check`), and do not
   reopen the lifting lanes (check `cheme layout lifting`).
4. Rebuild MTO and estimate (`cheme assess mto --write`, `cheme assess estimate --write`), update
   the TEA if it moves; report the steel tonnage before/after.
5. DESIGN.md decision (next free D-number), PROGRESS.md; `cheme validate` 0 errors; commit in
   logical steps; `build/pr-body.md`.
Never accept a finding. Final line: STATUS: DONE or STATUS: BLOCKED: <reason>.
