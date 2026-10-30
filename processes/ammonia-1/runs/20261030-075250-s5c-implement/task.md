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


# Your section: S5c of ammonia-1
Branch: stage/basic-layout (checked out). Earlier sections are merged on main.

## S5c basic close-out with the owner's decisions (on stage/basic-layout, PR #257; interventions I-006)
The branch now holds S5, S5b, S6-S8 (via main) and S9 (#264 merged into it). The owner (a
human, the project owner) decided on 2026-10-30, recorded as I-006 in `runs/interventions.md`:
- **Lifting:** the owner accepts the 8 lanes H-101, E-104, E-402, K-501, E-501, E-502, E-505,
  E-504 with the lifting plan's reason in `build/lifting-acceptance-proposal.md` (regenerate it
  if missing). Record the acceptance the way `cheme layout lifting` documents, with accepted_by
  `owner (I-006, 2026-10-30)` and the reason. The other lanes (cable trays over K-101, K-102,
  K-103, K-701 added in S9, and any other) are **not** accepted: clear them by design (tray route
  or elevation, crane pad on the free side, lift lane); if core cannot do it (core#73), stop and
  say so precisely.
- **Buried cooling-water road crossings:** the owner accepts the 4 `cheme.layout-headroom`
  findings of the buried DN 1400 headers under roads R-5/R-6 (reason: buried crossing in a sleeve
  under the road; core#70), accepted_by `owner (I-006, 2026-10-30)`.
- **Feed specification:** this is a paper case study; the owner approves a *representative*
  feed specification. Give the natural gas (S1), process and combustion air (S12, S61) and
  water feeds (S26, S70) a representative composition and conditions with provenance `given`
  and a published source (a representative pipeline natural gas, standard dry air, demineralised
  water), with the owner's approval (I-006) named in the source note; flows follow from the
  design capacity in the design basis (say so in the source). If the composition changes the
  gas, rerun `cheme process simulate --fill` and carry the effects. S5b saw the boiler duty jump
  130 -> 197.5 MW with the EBTF gas and reverted (D-034): find and explain the cause before
  accepting a change of that size; if you cannot, choose a representative published lean gas
  close to the current one.
- **Furnace H-101 model basis:** give the fuel combustion a sourced model basis (complete
  combustion of the fuel with excess air is standard design practice: cite a published source
  for it) so `maturity-balanced` passes; likewise any other step `cheme maturity` names.
- **Risk matrix:** the owner allows an assumed matrix. Replace the example 4x4 in
  `safety/risk-matrix.yaml` with a project matrix close to industry practice (e.g. 5x5,
  order-of-magnitude frequency bands per year, severity for people, environment, asset,
  reputation), written in our own words with the published practice it follows cited, marked
  ASSUMED, `example: false`, accepted_by `owner (I-006, 2026-10-30), assumed for the paper case`.
  Re-rate the HAZOP with `cheme safety hazop rate --write`; HAZOP entries stay `status: proposed`.
- **Estimate:** look up online a published cost index (CEPCI, value and year), published bulk
  unit rates and installation/factor-method factors (open literature, textbooks, public cost
  guides), each in `estimate/rates.yaml` with status, source (URL/DOI, locator) and year, in our
  own words. Equipment costs from the sized datasheets. Bring the estimate to class 4 (state the
  accuracy range and what is ASSUMED), rebuild `cheme assess estimate --write`, update the TEA.
- **Datasheets:** fill the main dimensions the detail gate `datasheets` reports missing
  (`cheme datasheets fill`, sized from the simulation, provenance on every value).
Then: rebuild layout, MTO, estimate; `cheme validate` 0 errors; `cheme check` (all stages) and
`cheme maturity`, report each gate. STATUS: DONE when every basic gate except the two review
gates passes, else BLOCKED with the exact remaining requirement. The reviews after this job are
the basic reviews (topics `design`, `layout`), then the basic sign-off and merge.

