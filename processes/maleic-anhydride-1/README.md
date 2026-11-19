# Maleic anhydride

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for 25 000 t/a of maleic anhydride from n-butane. Liquid butane is vaporised
and mixed with compressed humid air to 1.8 mol% butane at 239 kPa(a), the feed of the pilot
reactor of US 7 589 217 B2. A multitubular fixed-bed reactor with a vanadium phosphorus oxide
(VPO) catalyst, its shell cooled by molten salt at 675 K, converts 81 % of the butane, 69.5 % of
it to maleic anhydride (C4H10 + 3.5 O2 -> C4H2O3 + 4 H2O) and the rest to CO, CO2, acetic and
acrylic acid (`reactor: conversion`). The salt raises HP steam; the reactor gas is cooled to
423 K in a second steam generator and enters an absorber, where lean dibutyl phthalate takes up
99.4 % of the anhydride (US 4 118 403 A), its heat removed by pump-around coolers. The rich
solvent is stripped under vacuum, the crude distilled under vacuum to the product, and the lean
solvent cooled and returned. The off-gas, with the unconverted butane and the CO, and the
plant's liquid wastes are burnt in a recuperative thermal oxidiser (the lean off-gas preheated
against the flue gas) whose waste-heat boiler raises more HP steam.

cheme-as-code solves the whole mass balance: the reactor and the oxidiser as conversion steps
with their duties (core ADR 0059), the absorber, the stripper and the column as component
separators with a specified split, the butane and air solved for 25 000 t/a and the solvent
make-up for the circulation ratio by design specifications, and the solvent loop at a tear
stream (core ADRs 0060, 0070). `scripts/balance.py` gives the compressor, the coolers', reboilers'
and condensers' heats and the mixing temperatures, which need liquid data no property package of
core covers. Needs cheme-as-code 1.12.0. DESIGN.md lists the core features used and the core
limits hit.

Headline numbers and their caveats:
- 1.068 kg of butane per kg of anhydride (55.5 mol% overall), close to the 1.061 kg/kg of US
  5 688 970 A's once-through example. Conversion and selectivity are patent figures from a
  pilot tube; the acid by-products' selectivities and the CO/CO2 split are ASSUMED (D-004).
- 1.07 kWh of electricity per kg, 0.97 of it the air compressor (D-010).
- 8.38 kWh of HP steam raised per kg (salt cooler, gas cooler, oxidiser) and 1.01 drawn back
  for the reboilers, which are upper bounds without a lean/rich interchanger (D-006, D-010).
- 1.98 kWh of heat to cooling water per kg, 0.79 of it from the absorber's pump-around coolers
  (D-007, D-010).
- The oxidiser's off-gas is lean (about a third of its lower flammable limit) and would burn
  only to about 743 K as it comes; a recuperator preheating it for a 1073 K chamber is ASSUMED,
  and the start-up and pilot fuel is not modelled (D-009).
- 1.45 kg of fossil CO2 per kg to the stack. The preliminary LCI gives all burdens to the
  anhydride and none to the exported steam; most backgrounds are gaps (D-012).
- The feed, 1.8 mol% butane, lies above butane's lower flammable limit (1.4 vol%): the feed
  train and the reactor heads are the plant's main hazard, with the reactor's hot spot and the
  molten salt (D-011).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components with their ideal-gas data, blocks, steps, streams, design specifications and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts and `balance.py`: the air ratio, the compressor, the temperatures and duties core's models do not give (D-003, D-010) |
| `.claude/skills/` | how an agent works here (not in git: run `cheme skills update` once after cloning) |

## How this repository works

- **This repository holds your plant**: drawings, lists, decisions. It does not hold the tools.
- **The tools come from [`cheme-as-code`](https://github.com/ChemE-as-Code/core)**, installed once on
  your computer (`uv tool install git+https://github.com/ChemE-as-Code/core.git`). Every check,
  drawing and generated file is made by the `cheme` command, so you need it to work here.
- **Licences.** This folder is part of the ChemE-as-Code process library. Its data and designs are
  under CC BY 4.0 (`LICENSE-DATA`, unless `process.yaml` states otherwise); its skills and scripts
  are under AGPL-3.0-or-later (`LICENSE`), like the ChemE-as-Code tools. It is public
  (`publication` in `process.yaml`: public, CC-BY-4.0).
- **The skills in `.claude/skills/` are not in git.** They come with cheme-as-code: run
  `cheme skills update` once in this folder after cloning, so that Claude Code finds them here.

## Working here

```sh
cheme validate                  # after every change
cheme check                     # engineering-step gates (--write only at sign-off)
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
cheme process propagate --fill  # every flow, the specifications, the solvent loop, the reactor and oxidiser duties
cheme run scripts/balance.py    # the compressor, the other temperatures and duties (then propagate again)
cheme assess lca --write        # the preliminary LCI
```
