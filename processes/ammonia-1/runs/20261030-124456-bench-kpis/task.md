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


# Your job: compute the final design's key performance indicators (ammonia-1, blind)
The ammonia-1 design (process-library#86) is final on `main`: concept and basic stages signed
off. You compute ten KPIs from the design's own files, **without looking up any literature value
for them**: do not search the web or any file for reference/benchmark values of ammonia plants, do
not read any `benchmarks/` file or the `benchmark/ammonia` branch. This is a blind evaluation; the
comparison is done by someone else afterwards.

Working directory: `processes/ammonia-1` on branch `bench/ammonia-1-kpis` (from main).
First check the LCI dataset is current (`cheme assess lca --check`); if it is stale, rebuild it
with `cheme assess lca --write` and commit that alone ("regenerated, no design change").

For each KPI give: the value in the unit, how it is computed (which streams, exchanges, duties,
heating values, with their file locations), the boundary choices you made, and the design
decisions (D-numbers in DESIGN.md) that drive the value. Where the LCI dataset (`lca/dataset.yaml`
and its exchanges) can express the KPI, also give an **expression over the dataset's exchange
keys** (`feed:X / product:NH3` style, spaces around operators) and its `per` product; where it
cannot (no exchange), say so.

KPIs (per t of ammonia product unless stated):
1. specific-energy-net [GJ/t, LHV]: natural gas as feed and fuel plus imported energy minus
   exported energy (steam, power).
2. specific-energy-gross [GJ/t, LHV]: feed plus fuel plus electricity, without the credit for
   exported steam.
3. natural-gas-feed-plus-fuel [GJ/t, LHV]: natural gas to the process plus natural gas fired;
   no electricity or steam.
4. process-co2 [t/t]: CO2 formed in reforming and shift and removed from the synthesis gas
   (vented, used or captured); flue-gas CO2 not included.
5. direct-co2-total [t/t]: all CO2 to air from process and combustion, no CO2 used or stored.
6. steam-net-export [GJ/t, export positive]: steam leaving the boundary minus steam imported.
7. synthesis-loop-pressure [bar]: operating pressure at the converter inlet (say gauge/absolute).
8. synthesis-conversion-per-pass [%]: share of synthesis gas entering the converter converted to
   ammonia in one pass (state your basis: moles of H2+N2, or total gas).
9. nox-concentration-reformer [mg/m^3, as NO2, dry, normal conditions]: in the primary reformer
   flue gas (state the O2 reference if any).
10. nox-emission-factor [kg/t, as NO2]: from all combustion sources.
Where the design does not determine a value (e.g. NOx not modelled), say "not determined by the
design" and why, rather than estimating from literature.

Write the result to `runs/benchmark-kpis.md` (a table plus a section per KPI) and commit it.
Do not push. Final line: STATUS: DONE or STATUS: BLOCKED: <reason>.
