# Acetaldehyde (Wacker process)

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML) |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml` | components, blocks, steps and streams: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `piping/special-items.yaml` (optional) | tagged piping components: safety valves, silencers, rupture discs (skill `lists-sync`) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts: the source of generated sheets (`generator:` in `plant.yaml`), provenance for the others |
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
cheme fmt                       # canonical XML, stable ids
cheme render [--png] [--crop]   # build/<sheet>[_crop-X0-Y0-X1-Y1].svg (or .png)
cheme render --png --tiles auto # build/<sheet>_tile-A1.png ... to read the whole sheet
cheme show <id or tag>          # where an object and its drawing are in the file
cheme diff main [--list]        # build/diff.html, or one line per changed plant item
cheme check                     # engineering-step gates (--write only at sign-off)
cheme runs list                 # the record of each design session in runs/
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
```
