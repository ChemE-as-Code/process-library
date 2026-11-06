# Benzyl bromide

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant: the photoreactor R101 is a semi-batch (`reactor: semibatch`, bromine dosed into
excess toluene at 363 K under lamps) whose HBr leaves as it forms by a vent stream
(`batch.vent`, core ADR 0054), saturated with the content's vapour (`vent.vapour`, core ADR
0062), through the reflux condenser E-102, R101's vent condenser whose condensate returns to the
reactor and whose duty is written on its own energy stream (`vent.condenser`), and a brine vent
condenser to the absorber that makes 48 wt% hydrobromic acid; its maximum technical temperature
is given as `hazard.mtt`, and its off-gas system's capacity, against the gas and vapour a cooling
failure releases at the MTSR, as `hazard.vent_capacity` (core ADR 0058). The light-driven rate is
an ASSUMED effective rate law (core has no photochemical rate). The crude is stripped of its
toluene at 15 kPa(a) (ST101, one Rayleigh stage, `still:`, core ADR 0055), then a forerun
(ST102) and the main cut (ST103) are taken at 2 kPa(a) through a packed column on the same still
(`still.column`, Diwekar's batch shortcut, core ADR 0061); the stripped toluene and the forerun
go back to the next batch, 2 % purged, a recycle that `cheme process propagate` converges at its
tear stream S2 (`tears:`, core ADR 0060). The stills' reboilers (Q7, Q9, Q14), the column's
condensers (Q10, Q11) and E-102 (Q4) are written by `cheme process propagate --fill` from the
models (core ADRs 0059, 0061, 0062); the other duties come from `scripts/balance.py`. The
product is 99.85 wt% benzyl bromide in the model, an upper bound (ring-brominated and
condensation by-products are not modelled). `process/recipe.yaml` holds the batch recipe the
cycle time, R-101's vessel and jacket check, the stills' boil-up times and the flowsheet's
year-average flows come from (`cheme process recipe`, `cheme process reactor-hazards`, `cheme
process stills`). Needs cheme-as-code 1.10.0.

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components (with the stills' Antoine constants), blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures, R-101's vessel and jacket, the stills' distil times (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts and `balance.py`: the feeds for 1000 t/a, the brine vent condenser E-103, the absorber water, the mixing and bubble-point temperatures and the duties core does not model, with a cross-check of those it does (D-006, D-009); `still_jacket.py`: the stills' times at the boil-up C-101's wetted jacket allows (D-007) |
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
cheme process propagate --check # the semi-batch with its vent and vent condenser, the stills and the column, mixers, splitter, the recycle's tear and the model duties
cheme process recipe            # batch cycle, bottleneck, batches per year, vessel, jacket, off-gas (--svg)
cheme process reactor-hazards   # thermal screening: accumulation, MTSR over the batch, gas release vs the vent
cheme process stills            # the stills' and the column's cuts, recoveries, residue, boil-up times and duties per batch
cheme run scripts/balance.py    # the feeds for 1000 t/a, the absorber water and the other duties
cheme assess lca --check        # the LCI files current
```

The recycle S2 is converged by `cheme process propagate --fill` itself (core 1.9.0). After a
change that moves the product rate, run `cheme run scripts/balance.py` and `cheme process
propagate --fill` in turn, writing the feeds the script prints into the flowsheet, until the
product S15 is 1000 t/a (a few passes, DESIGN.md D-006).
