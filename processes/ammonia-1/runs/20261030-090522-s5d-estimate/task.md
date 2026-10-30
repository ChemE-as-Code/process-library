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


# Your job: S5d-estimate of ammonia-1 (branch stage/basic-layout, PR #257; owner decision I-006b)
Branch: stage/basic-layout (checked out). The owner asked for one more focused attempt (cap USD 10)
to bring the capital estimate from class 5 to class 4 with sourced data found online. S5c (D-044)
kept `estimate/rates.yaml` as the example because it found no open bulk unit rates and the
correlations lacked factors for Cr-Mo, refractory-lined and >140 barg equipment. Read D-044,
`estimate/`, the skills `mto-estimate` and `tea` first.

Do (web search and fetch for every value; our own words; source with URL/DOI and exact locator;
year; status; mark ASSUMED where a judgement is applied):
1. Cost index: a published CEPCI value (latest annual you can cite) and the base year of each
   correlation, so every cost is escalated with a cited ratio.
2. Equipment costs: open, citable correlations (textbooks with published equations, government
   or university cost reports, e.g. NETL/DOE baseline methodology, open-access papers) including
   **material factors** (Cr-Mo, stainless, clad) and **pressure factors** up to the loop pressure,
   and a sourced approach for refractory-lined vessels and fired heaters/reformers.
3. Bulk/installation: a sourced factor method (e.g. detailed installation factors per equipment
   class for piping, instruments, electrical, civil, structural, insulation, paint, erection) in
   place of unit rates where open unit rates do not exist; take-off quantities stay from the MTO.
4. Put them in `estimate/rates.yaml` (status, source, year), rebuild `cheme assess estimate
   --write`, update the TEA. State the estimate class per AACE 18R-97 definition criteria (cite),
   its accuracy range, and what drives it; if class 4 is still not justified, say exactly which
   input is missing.
Do not change the layout, the flowsheet or the lifting work (a separate job does lifting).
`cheme validate` 0 errors; commit (decision D-045 in DESIGN.md, PROGRESS.md); write
`build/pr-comment.md` (short summary for the PR). Final line: STATUS: DONE or STATUS: BLOCKED: <reason>.
