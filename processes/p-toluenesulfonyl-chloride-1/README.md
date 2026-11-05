# p-Toluenesulfonyl chloride

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant for p-toluenesulfonyl chloride (tosyl chloride) by the salt-modified
chlorosulfonation of toluene (DE 1 912 956 A1): the chlorosulfonator R101 and the drown-out
quench Q101 are semi-batches (`reactor: semibatch`) whose HCl leaves by a vent as it forms
(`batch.vent`); the precipitation CR101 and the two reslurry washes are crystallizers with the
acid liquor's other solutes as spectators; the Nutsche filter F-101 is one recipe vessel over
five steps with Ruth filtration times, and the paddle dryer DR-101 is core's dryer to a residual
moisture. `process/recipe.yaml` holds the batch recipe the cycle time, the vessel sizes, the
jacket checks, the scrubber load per batch and the flowsheet's year-average flows come from
(`cheme process recipe`, `cheme process reactor-hazards`, `cheme process crystallizers`).
Needs cheme-as-code 1.8.0. DESIGN.md lists the core features used and the core limits hit.

Two headline numbers carry caveats. The modelled product is 99.7 wt% p-TsCl, an upper bound:
the cake's retention of the o-TsCl oil is not modelled (DESIGN.md L-4), and the source's crude
has 90 % para. The modelled yield is 78.8 % on toluene, above the patent's 77 % para in its
crude (an ASSUMED better conversion, D-005); calibrated to the patent, it would be about 76 %.

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
| `scripts/` | generator scripts (no balance script: every stream is calculated by cheme) |
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
cheme process propagate --fill  # every stream from the feeds (semi-batches, crystallizers, filters, dryer)
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessels, vents (--svg)
cheme process reactor-hazards   # thermal screening of the two semi-batches
cheme process crystallizers     # precipitation, washes, filters and dryer: solubility, crystals, moisture, steam
cheme assess lca --write        # the preliminary LCI
```
