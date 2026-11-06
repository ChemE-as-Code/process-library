# Methyltriphenylphosphonium bromide

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant for methyltriphenylphosphonium bromide, the precursor of the Wittig methylenation
reagent, by the quaternisation of triphenylphosphine with methyl bromide in toluene (issue #133).
Liquid methyl bromide is dosed into the PPh3 solution in a closed pressure vessel at 333 K
(`reactor: semibatch`, R101); the salt precipitates and is put into crystals by a crystallizer
with the dissolved PPh3 and methyl bromide as spectators (CR101); the excess methyl bromide is
swept to the site's thermal oxidiser; the agitated filter-dryer F-101 is one recipe vessel over
its filtration, reslurry wash, re-filtration and drying (Ruth filtration times, core's dryer to a
residual moisture); and the toluene is recovered in core's batch still C-101 and reused.
`process/recipe.yaml` holds the batch recipe the cycle time, the vessel sizes, the jacket check
and the flowsheet's year-average flows come from (`cheme process recipe`, `cheme process
reactor-hazards`, `cheme process crystallizers`, `cheme process stills`). Needs cheme-as-code
1.8.0. DESIGN.md lists the core features used and the core limits hit.

Key numbers: 1057.10 kg per batch, a 10.20 h cycle (the filter-dryer the bottleneck), 776.6
batches and 820.9 t a year. Thermal screening: 14.7 % of the methyl bromide accumulates, the
MTSR is 339.1 K, and the MTT of the closed vessel is 431.0 K, a hand value (the temperature at its
relief's set pressure, DESIGN.md D-011). The headline yield (98.5 % on PPh3) and assay (99.87 wt%)
are ASSUMED upper bounds: no open source of this route gives either, and impurities such as
triphenylphosphine oxide are not modelled. The Org. Synth. procedure the route is usually cited
from could not be read.

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML; none yet) |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, reactions, blocks, steps and streams: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures and their operations (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `lca/` | goal and scope (`lca.yaml`), this process's mappings, and the preliminary LCI cheme writes |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts (no balance script: every stream but two hand splits is calculated by cheme) |
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
cheme process propagate --fill  # every stream from the feeds (semi-batch, crystallizers, filters, dryer, still)
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessels (--svg)
cheme process reactor-hazards   # thermal screening of the semi-batch
cheme process crystallizers     # precipitation, wash, filters and dryer: solubility, crystals, moisture, steam
cheme process stills            # the toluene recovery: distillate, residue, boil-up time and energy
cheme assess lca --write        # the preliminary LCI
```

The recycled toluene (S3, S11) is a tear stream: after a change upstream, re-converge it with the
fresh feeds by successive substitution over `cheme process propagate --fill` (DESIGN.md D-006).
