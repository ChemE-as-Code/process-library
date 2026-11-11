# Carbon tetrabromide

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant: the hypobromite reactor M101 and the haloform reactor R101 are semi-batches
(`reactor: semibatch`: bromine dosed into the caustic, then acetone into the hypobromite), and
`process/recipe.yaml` holds the batch recipe the cycle time and the flowsheet's year-average
flows come from (`cheme process recipe`, `cheme process reactor-hazards`). The work-up runs on
cheme's solids models: the precipitation CR101 and the reslurry wash W101 are crystallizers
with the liquor's other solutes as spectators, the filter-dryer F-101 (two units) is one recipe
vessel over the steps F101, W101, F102 and D101, and its filtration and drying times and its
steam come from the filter and dryer models (`cheme process crystallizers`; DESIGN.md D-007,
D-008). No balance script. Needs cheme-as-code 1.8.0.

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML; none yet) |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml` | components, blocks, steps and streams: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures and their operations (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `lca/` | goal and scope (`lca.yaml`), this process's mappings, and the preliminary LCI cheme writes |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts (no balance script: every stream is calculated by cheme, D-006) |
| `.claude/skills/` | how an agent works here (not in git: run `cheme skills update` once after cloning) |

## How this repository works

- **This repository holds your plant**: drawings, lists, decisions. It does not hold the tools.
- **The tools come from [`cheme-as-code`](https://github.com/ChemE-as-Code/core)**, installed once on
  your computer (`uv tool install git+https://github.com/ChemE-as-Code/core.git`). Every check,
  drawing and generated file is made by the `cheme` command, so you need it to work here.
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
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year (--svg)
cheme process reactor-hazards   # thermal screening, with the semi-batch's accumulation
cheme process crystallizers     # precipitation, wash, filters and dryer: solubility, crystals, moisture, steam
```
