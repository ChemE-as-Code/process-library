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


# Your section: S2 process simulation of ammonia-1, continuation (round 2)
Branch: stage/basic-simulation (checked out). The first S2 session ended BLOCKED on core#57 (a
multi-recycle loop never converged through core v1.0.0). core#57 is fixed in core **v1.0.1**
(`cheme --version` shows 1.0.1; tear iteration with Anderson acceleration, ADR 0033), and the
DEXPI-class `Pumping` crash (core#59) too. Read DESIGN.md D-024/D-025 and PROGRESS.md first: they
say what the first session did, what stayed on the concept model (SYN, PGR, the steam system)
and keep a DWSIM-ready description of the loop and purge-recovery model.

Finish S2 on v1.0.1:
- Model the synthesis loop, the product flash and refrigeration, and the purge recovery in
  `process/simulation.yaml` / the flowsheet as DESIGN.md D-024 describes, and converge the whole
  plant with `cheme process simulate` (every design-basis case); if a part still cannot be
  represented, keep it specified and say exactly why.
- Retune what the first session recorded as deviations where the simulation now covers them
  (e.g. the converter H2/N2 through the process air), as decisions in DESIGN.md, never by
  editing simulated values; the P301 pump may now be a Pumping step (core#59).
- Replace the loop's ASSUMED concept values with `calculated` ones (`--fill`) where covered;
  never overwrite given or assumed values; deviations stay findings.
- Energy audit as far as core supports it (core#60 open: plant closure with component
  separators); `cheme maturity` reported with the exact unsupported requirements (core#315,
  the unsourced feed R-03).
Then the PR body for the whole section (both sessions) in `build/pr-body.md`.

## S2 targets (unchanged, from plan.md)
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

