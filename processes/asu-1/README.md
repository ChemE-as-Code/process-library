# ASU-1 (500 t/d GOX)

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; most of it has had
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
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts: the source of generated sheets (`generator:` in `plant.yaml`), provenance for the others |
| `.claude/skills/` | how an agent works here (not in git: run `cheme skills update` once after cloning) |

## LCA results and what they compare

Per 1 t GOXP (pipeline GOX at 30 barg), cradle-to-gate, exergy allocation between GOX, GAN, LOX
and LIN; a partial screening carbon footprint (18 gaps in construction, maintenance,
consumables and end-of-life credits, listed in `lca/gaps.csv`). The values are those of
`lca/results.md` (`cheme assess lca --write`), which governs. Only the electricity and the
cooling water change between the scenarios; construction, transport and materials stay on the
UK (DESNZ) factors in all three.

| scenario | electricity background | kg CO2e per t GOXP | comparability with the baseline |
|---|---|---|---|
| baseline | UK grid, DESNZ 2026: at the consumer, T&D and well-to-tank included (proxy for an undecided site, D-092) | 66.7 | reference |
| nl-grid | NL, EEA ENER038 2024: direct emissions per kWh of gross generation | 88.3 | **not comparable** (basis differs) |
| de-grid | DE, EEA ENER038 2024: direct emissions per kWh of gross generation | 104.7 | **not comparable** (basis differs) |

The NL and DE values are screening sensitivities of the grid, not like-for-like country
footprints, and nothing here has independent industrial validation (DESIGN.md D-107, D-110).
The verdicts follow core's comparison basis; the generated records carry them once
regenerated after it is merged.

## Working here

```sh
uv tool install cheme-as-code           # once (see the cheme-as-code README)
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
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
```
