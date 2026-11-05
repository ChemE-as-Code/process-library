# Acetyl chloride

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant for acetyl chloride from acetic acid and phosphorus trichloride (CS 272 248 B2,
Example 1). The reactor R101 is a semi-batch (`reactor: semibatch`, PCl3 dosed into acetic acid
at 313 K) whose HCl, and the acetyl chloride vapour that passes the brine vent condenser, leave
by a vent stream (`batch.vent`, core ADR 0054) to a water scrubber. Its maximum technical
temperature, the boiling point of acetyl chloride, is given as `hazard.mtt`. The reaction mass
settles in the same vessel into an upper acetyl chloride phase and a lower crude phosphorous acid
phase; the split D101 is calibrated to the source and given by `scripts/balance.py` (core has no
liquid-liquid model for these liquids). The upper phase is distilled in a batch still, ST101,
which core integrates as one Rayleigh stage (`still:`, core ADR 0055). The rectification in the
column on top of it, K101, is a specified split until core has a batch column with reflux
(core#173). `process/recipe.yaml` holds the batch recipe that gives the cycle time, R-101's
vessel, jacket check and warming time, the still's boil-up time and the flowsheet's
year-average flows (`cheme process recipe`, `cheme process reactor-hazards`, `cheme process
stills`). Needs cheme-as-code 1.8.0. DESIGN.md lists the core features used and the core limits
hit.

Three headline numbers carry caveats:
- The yield, 92.4 % of theory on the acetic acid and the PCl3, is a model result; no open source
  states one. It is an upper bound, since the losses not modelled only lower it (D-008).
- The product, 99.84 wt% with 0.16 wt% PCl3 (about 370 ppm P), has no source either. One still
  stage alone gives 97.3 wt%, and a low-phosphorus grade needs the chlorine treatment of
  US 4 209 460 A, which is not modelled (D-007, D-008).
- The model's HCl, 1.7 kg a batch from the acid's water, is a lower bound: the source's lower
  phase holds 6 wt% HCl, about 39 kg a batch at this scale (D-010).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components (with the still's Antoine constants), blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures over several steps, R-101's vessel and jacket, the still's distil time (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts and `balance.py`: the feeds for 2000 t/a, the phase split, the column's split, the scrubber water, the mixed temperatures and the duties (D-006) |
| `.claude/skills/` | how an agent works here (not in git: run `cheme skills update` once after cloning) |

## How this repository works

- **This repository holds your plant**: drawings, lists, decisions. It does not hold the tools.
- **The tools come from [`cheme-as-code`](https://github.com/ChemE-as-Code/core)**, installed once on
  your computer (`uv tool install git+https://github.com/ChemE-as-Code/core.git`). Every check,
  drawing and generated file is made by the `cheme` command, so you need it to work here.
- **Licences.** This folder is part of the ChemE-as-Code process library. Its data and designs are
  under CC BY 4.0 (`LICENSE-DATA`, unless `process.yaml` states otherwise); its skills and scripts
  are under AGPL-3.0-or-later (`LICENSE`), like the ChemE-as-Code tools. Its publication status is
  in `process.yaml` (internal until a maintainer decides otherwise).
- **The skills in `.claude/skills/` are not in git.** They come with cheme-as-code: run
  `cheme skills update` once in this folder after cloning, so that Claude Code finds them here.

## Working here

```sh
cheme validate                  # after every change
cheme check                     # engineering-step gates (--write only at sign-off)
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
cheme process propagate --fill  # the semi-batch, the still, the mixers and the scrubber from the feeds
cheme run scripts/balance.py    # the feeds, the phase split, the column's split and the duties (then propagate again)
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessel, jacket, vent (--svg)
cheme process reactor-hazards   # thermal screening of the semi-batch
cheme process stills            # the batch still: distillate, residue, boil-up time
cheme assess lca --write        # the preliminary LCI
```
