# Copper(I) chloride

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant for copper(I) chloride (cuprous chloride) by the wet chlorination of copper in a
sodium chloride brine (US 3 030 178 A, run as a batch): chlorine is dosed below the surface of a
hot brine over excess copper in R-101, a semi-batch (`reactor: semibatch`) with the chlorine as
an absorbed gas dose (`dosing.absorbed`); the copper heel kept in R-101 and the tenth of the
mother liquor that makes up the next brine are recycles converged by core's `tears:`. The liquor
is diluted with about seven volumes of deoxygenated water in P-101, where CuCl precipitates (a
crystallizer with the brine's other solutes as spectators and a solubility `measured_in` the
mother liquor); the agitated filter-dryer F-101 is one recipe vessel over six steps (filtration,
an acid reslurry wash, an ethanol wash, vacuum drying under nitrogen) with Ruth filtration times
and core's dryer. `process/recipe.yaml` holds the batch recipe the cycle time (9.37 h, 846 batches
a year), the vessel sizes, the jacket check and the flowsheet's year-average flows come from
(`cheme process recipe`, `cheme process reactor-hazards`, `cheme process crystallizers`). R101
writes its heat at its `energy_port`. The thermal screening finds a small rise (MTSR 354.2 K
against an MTT of 373.1 K, also at a hundred times slower rates); the chlorine's breakthrough to
the vent scrubber and the reduction's end point are the design findings (DESIGN.md D-011).
Needs cheme-as-code 1.9.0. DESIGN.md lists the core features used and the core limits hit.

Two headline numbers carry caveats. The modelled product is 99.8 wt% CuCl, an ASSUMED upper
bound: the model has no oxidation by air, and the only open specification is at least 98 wt%.
The yield is 77.6 % on copper, set by an ASSUMED solubility of CuCl in the diluted brine (a power
law through two open data points, DESIGN.md D-006): 22.3 % of the copper leaves dissolved with
the brine to copper recovery outside the boundary.

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
cheme process propagate --fill  # every stream from the feeds (semi-batch, recycles, crystallizers, filters, dryer)
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessels (--svg)
cheme process reactor-hazards   # thermal screening of the semi-batch
cheme process crystallizers     # precipitation, acid wash, filters and dryer: solubility, crystals, moisture, steam
cheme assess lca --write        # the preliminary LCI
```
