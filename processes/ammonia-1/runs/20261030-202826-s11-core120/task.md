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


# Your job: S11 ammonia-1 on core v1.2.0 (branch stage/detail-core120; owner decision I-008)
Branch: stage/detail-core120 (checked out), from main after S10 (D-047, supports).
cheme is core v1.2.0 (installed; the same version library CI pins). Three core fixes made at the
owner's request apply to this plant:
- core#70 (ADR 0036): a line or segment in `piping/routing.yaml` can be `buried` (`true` or
  `{cover_m, basis}`); buried runs get a soil-cover check (`cheme.layout-buried-cover`, road
  cover `rules.road_cover_m`) instead of road headroom and above-grade clash findings.
- core#71 (ADR 0037): `power_trays: [{rack, trays}]` in `electrical/tray-rules.yaml` gives a rack
  several power trays (a count, or a voltage class per tray: `hv`, `lv`, `any`).
- core#72: a line with battery limits at both ends (the cooling-water headers) is now routed
  along a rack instead of staying unrouted.

Do, by design (skills `pipe-routing`, `layout-yaml`, `electrical-cabling`, `mto-estimate`; run
`cheme skills update` first, keep local changes, report them):
1. Cooling water: the owner accepted four buried cooling-water road crossings (I-006). Declare
   those runs `buried` with a cover and its basis (ASSUMED where no source), so the model says
   what the acceptance says. If a road-headroom finding then no longer exists, its acceptance is
   stale: remove only that acceptance entry and list it in the PR body; never add or widen one.
2. Let the router route the cooling-water headers (no longer unrouted); check their branches,
   clashes, the lifting lanes (`cheme layout lifting`, no lane reopened) and the supports count.
3. Electrical: clear the 8 tray-fill/separation findings (detail gate `electrical`) with
   `power_trays` on the affected racks, split by voltage class; rebuild the cable schedule
   (`cheme layout cables --write`).
4. Rebuild layout, cable schedule, MTO, estimate, LCA dataset (`cheme assess lca --write`; the S10
   round-2 review s10-r2#1 found the cable schedule and LCA dataset not current) and the TEA if it
   moves; draw a cap or blind on the new DW-1073 drain valve on P-106 (s10-r2#3); `cheme validate` 0 errors; `cheme check`
   (report every gate) and `cheme maturity`; report what changed in numbers.
5. DESIGN.md decision (next free D-number), PROGRESS.md; commit in logical steps;
   `build/pr-body.md`.
Never accept a finding; never relax a gate or rule. Do not touch the datasheet weights/nozzles
(not this job). Final line: STATUS: DONE or STATUS: BLOCKED: <reason>.
