# Phosphorus tribromide

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant: the brominator R101 is a semi-batch (`reactor: semibatch`, molten phosphorus and
bromine dosed together into a PBr3 heel, its maximum technical temperature given as
`hazard.mtt`), and `process/recipe.yaml` holds the batch recipe the cycle time, the vessel
size, the jacket check and the flowsheet's year-average flows come from (`cheme process
recipe`, `cheme process reactor-hazards`). The heel is a recycle that `scripts/balance.py`
converges, and the vacuum distillation is a specified split there until core has a batch
distillation (core#165).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures, R-101's vessel and jacket (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts and `balance.py`, the heel recycle, the still's split and the duties (D-006) |
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
cheme process propagate --check # the semi-batch, the heel split and the red-phosphorus step
cheme process recipe            # batch cycle, bottleneck, batches per year, vessel and jacket (--svg)
cheme process reactor-hazards   # thermal screening, with the semi-batch's accumulation
cheme run scripts/balance.py    # the heel recycle, the still's split and the duties
cheme assess lca --check        # the LCI files current
```
