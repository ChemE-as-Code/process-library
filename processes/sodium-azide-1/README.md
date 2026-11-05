# Sodium azide

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant on the hydrazine / methyl nitrite route: the methyl nitrite generator R101 and the
azide reactor R102 are semi-batches with gas vents (`batch.vent`, `dosing.absorbed`), the
methanol strip and concentration ST101 a batch still, the precipitation CR101 a crystallizer with
spectator solutes, and the filter-dryer F-101 four steps in one vessel (F101, W101, F102, D101).
`process/recipe.yaml` holds the batch recipe the cycle time, the vessel sizes, the jacket checks,
the filtration and drying times and the flowsheet's year-average flows come from (`cheme process
recipe`, `cheme process reactor-hazards`). The mother-liquor and methanol recycles are tear
streams converged over `cheme process propagate` (DESIGN.md D-006). **It needs cheme-as-code
1.8** (core main 7334d7c or later; core ADRs 0054 to 0057): the library's pinned 1.7.0 rejects
its vents, still, spectators and dryer.

**Hazards.** Sodium azide, hydrazine and methyl nitrite are highly toxic; any acid turns azide
into hydrazoic acid (toxic, explosive), and azide forms explosive heavy-metal azides with copper
and lead. DESIGN.md D-015 lists what the design rests on.

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures, the vessels of R-101, R-102 and F-101 (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts; no balance script (every unit is calculated by core) |
| `.claude/skills/` | how an agent works here (not in git: run `cheme skills update` once after cloning) |

## How this repository works

- **This repository holds your plant**: drawings, lists, decisions. It does not hold the tools.
- **The tools come from [`cheme-as-code`](https://github.com/ChemE-as-Code/core)**, installed once on
  your computer (`uv tool install git+https://github.com/ChemE-as-Code/core.git`). Every check,
  drawing and generated file is made by the `cheme` command, so you need it to work here. The CI
  of the process library installs it too.
- **Licences.** This folder is part of the ChemE-as-Code process library. Its data and designs are
  under CC BY 4.0 (`LICENSE-DATA`, unless `process.yaml` states otherwise); its skills and scripts
  are under AGPL-3.0-or-later (`LICENSE`), like the ChemE-as-Code tools.
- **The skills in `.claude/skills/` are not in git.** They come with cheme-as-code: run
  `cheme skills update` once in this folder after cloning, so that Claude Code finds them here. Run
  it again after upgrading (`uv tool upgrade cheme-as-code`); `cheme skills status` shows which are
  out of date. A skill you changed here is kept, but only on your machine.

## Working here

```sh
uv tool install 'cheme-as-code[serve] @ git+https://github.com/ChemE-as-Code/core.git'   # once (see the cheme-as-code README)
cheme git-setup                 # once per clone: readable P&ID diffs + pre-commit hook
cheme skills update             # once per clone: installs the agent skills in .claude/skills/
cheme status                    # where the plant stands: sheets, findings, gates, sign-offs
cheme validate                  # after every change
cheme check                     # engineering-step gates (--write only at sign-off)
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
cheme process propagate --check # the semi-batches, the still, the crystallizer, the filter-dryer
cheme process reactors          # the semi-batches: accumulation, cooling failure, vents
cheme process stills            # the batch still: cuts, residue, boil-up time and energy
cheme process crystallizers     # the precipitation, the filters and the dryer
cheme process recipe            # batch cycle, bottleneck, batches per year, vessels and jackets (--svg)
cheme process reactor-hazards   # thermal screening, with the semi-batches' accumulation
cheme assess lca --check        # the LCI files current
```
