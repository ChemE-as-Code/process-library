# ASU-1 (500 t/d GOX)

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`plantcode`](https://github.com/process-intelligence-research/plantcode).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML) |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts kept for provenance |
| `.claude/skills/` | how an agent works here |

## Working here

```sh
uv tool install plantcode           # once (see the plantcode README while it is private)
plantcode git-setup                 # once per clone: readable P&ID diffs + pre-commit hook
plantcode validate                  # after every change
plantcode fmt                       # canonical XML, stable ids
plantcode render [--png] [--crop]   # build/<sheet>[_crop-X0-Y0-X1-Y1].svg (or .png)
plantcode show <id or tag>          # where an object and its drawing are in the file
plantcode diff main [--list]        # build/diff.html, or one line per changed plant item
plantcode check                     # engineering-step gates (--write only at sign-off)
```
