# Benzyl chloroformate

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant: the phosgenator R101 is a semi-batch (`reactor: semibatch`) into whose benzyl
alcohol phosgene gas is dosed, partly absorbed (`dosing.absorbed`), with the HCl leaving by a
vent as it forms (`batch.vent`); the crude is degassed in the same vessel (a batch still,
`still:`), and `process/recipe.yaml` holds the batch recipe over the three steps of that vessel
(`units:`), from which the cycle time, the vessel, the vent's peak rate and the flowsheet's
year-average flows come (`cheme process recipe`, `cheme process reactor-hazards`, `cheme process
stills`). The models write the duties of R101 and the degassing (core ADR 0059), and the
R101's duty holds the heat of solution of the dosed phosgene (ADR 0063); the screening compares
the gas a cooling failure releases with the vent's capacity (ADR 0058). It needs cheme-as-code
1.10 (core ADRs 0054, 0055, 0057, 0058, 0059, 0063).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML; none yet) |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml` | components, blocks, steps and streams: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/reactions.yaml` | the phosgenation, its two side reactions and the scrubber's reactions |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedure and its operations (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | goal and scope (`lca.yaml`), mappings, and the inventory and dataset `cheme assess lca --write` writes |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions (with the core features used and the core limits hit), change log, stage definitions |
| `scripts/` | generator scripts (no balance script: every stream is calculated by cheme) |
| `.claude/skills/` | how an agent works here (not in git: run `cheme skills update` once after cloning) |

## How this repository works

- **This repository holds your plant**: drawings, lists, decisions. It does not hold the tools.
- **The tools come from [`cheme-as-code`](https://github.com/ChemE-as-Code/core)**, installed once on
  your computer (`uv tool install git+https://github.com/ChemE-as-Code/core.git`). Every check,
  drawing and generated file is made by the `cheme` command, so you need it to work here. The CI
  in `.github/workflows/` installs it too.
- **Licences.** This folder is part of the ChemE-as-Code process library. Its data and designs are
  under CC BY 4.0 (`LICENSE-DATA`, unless `process.yaml` states otherwise); its skills and scripts
  are under AGPL-3.0-or-later (`LICENSE`), like the ChemE-as-Code tools.
- **The skills in `.claude/skills/` are not in git.** They come with cheme-as-code: run
  `cheme skills update` once in this folder after cloning, so that Claude Code finds them here. Run
  it again after upgrading (`uv tool upgrade cheme-as-code`); `cheme skills status` shows which are
  out of date. A skill you changed here is kept, but only on your machine.
- The CI needs the secrets named in `.github/workflows/validate.yml`.

## Working here

```sh
uv tool install 'cheme-as-code[serve] @ git+https://github.com/ChemE-as-Code/core.git'   # once (see the cheme-as-code README)
cheme git-setup                 # once per clone: readable P&ID diffs + pre-commit hook
cheme skills update             # once per clone: installs the agent skills in .claude/skills/
cheme status                    # where the plant stands: sheets, findings, gates, sign-offs
cheme validate                  # after every change
cheme check                     # engineering-step gates (--write only at sign-off)
cheme process build             # BFD and PFD from process/*.yaml
cheme process propagate --fill  # every stream from the feeds (semi-batch with vent, still, scrubber), and the duties of R101 and T101
cheme process streams           # stream table with provenance, block balances
cheme process recipe            # batch cycle, vessel and jacket, vent's peak rate and gas per batch (--svg)
cheme process reactor-hazards   # thermal screening: accumulation, MTSR over the batch, gas release against the vent
cheme process stills            # the degassing: gas, time and duty per batch
cheme assess lca --write        # the preliminary LCI
```
