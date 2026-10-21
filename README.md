# ASU-1 (500 t/d GOX)

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`plantcode`](https://github.com/ChemE-as-Code/core).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML) |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml` | components, blocks, steps and streams: the source of the generated BFD and PFD (`process/*.xml`, `plantcode process build`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `piping/special-items.yaml` (optional) | tagged piping components: safety valves, silencers, rupture discs (skill `lists-sync`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts: the source of generated sheets (`generator:` in `plant.yaml`), provenance for the others |
| `.claude/skills/` | how an agent works here |

## Working here

```sh
uv tool install plantcode           # once (see the plantcode README while it is private)
plantcode git-setup                 # once per clone: readable P&ID diffs + pre-commit hook
plantcode status                    # where the plant stands: sheets, findings, gates, sign-offs
plantcode validate                  # after every change
plantcode fmt                       # canonical XML, stable ids
plantcode render [--png] [--crop]   # build/<sheet>[_crop-X0-Y0-X1-Y1].svg (or .png)
plantcode render --png --tiles auto # build/<sheet>_tile-A1.png ... to read the whole sheet
plantcode show <id or tag>          # where an object and its drawing are in the file
plantcode diff main [--list]        # build/diff.html, or one line per changed plant item
plantcode check                     # engineering-step gates (--write only at sign-off)
plantcode process build             # BFD and PFD from process/*.yaml
plantcode process streams           # stream table with provenance, block balances
```
