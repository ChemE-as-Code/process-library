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


# Your section: S3c of ammonia-1
Branch: stage/basic-pids-loop (checked out). Earlier sections are merged on main.

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


Your part: **S3c (loop)** only; the other parts are separate sections.
