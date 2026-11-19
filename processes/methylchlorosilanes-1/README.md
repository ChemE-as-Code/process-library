# Methylchlorosilanes (direct process)

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for 60 000 t/a of dimethyldichlorosilane (Me2SiCl2), the base monomer of the
silicones, by the direct (Mueller-Rochow) process. Methyl chloride from chloromethane-1, fresh
and recovered, is vaporised and fluidises a bed of ground metallurgical silicon with a copper
catalyst at 573 K and 400 kPa(a), the conditions of US 4 500 724 A. 95 % of the silicon and half
of the methyl chloride convert per pass (`reactor: conversion` on the silicon). The crude holds
84 wt% Me2SiCl2, 7 % MeSiCl3, 3 % Me3SiCl, 1.5 % MeHSiCl2 and 4.5 % of a high-boiling residue,
a distribution ASSUMED inside the open ranges. Cooling coils in the bed raise MP steam, and
cyclones return the fines. The crude gas is cooled; the methyl chloride is recovered in a column
at about 90 psig, which condenses it on cooling water (US 2 563 557), and recycled. Three
columns then split the crude into a residue, a light silanes cut, a MeSiCl3 cut and the
product. The last split separates two silanes that boil 4 K apart (relative volatility 1.17,
EP 1 957 504 B1).

cheme-as-code solves the whole mass balance: the reactor as a conversion step, the cyclones and
the columns as component separators with a specified split, the silicon solved for 60 000 t/a
and the fresh methyl chloride for the bed's ratio by design specifications, and the methyl
chloride loop at a tear stream (core ADRs 0060, 0070). `scripts/balance.py` gives every duty:
core cannot give the reactor's, because silicon is a solid and Me2SiCl2 has no formation
enthalpy in its data. Needs cheme-as-code 1.13.0. DESIGN.md lists the core features used and
the core limits hit.

Headline numbers and their caveats:
- 0.276 kg of silicon (0.218 by stoichiometry) and 0.963 kg of methyl chloride per kg of
  Me2SiCl2, with 0.087 kg of a MeSiCl3 cut and 0.063 kg of a light silanes cut as co-products.
  The conversions and the crude distribution are ASSUMED inside the ranges of the open sources
  (D-003, D-004).
- The bed releases about 239 kJ per mol of silicon (4.6 MW), taken by cooling coils that raise
  0.62 kWh of MP steam per kg. It rests on an ASSUMED formation enthalpy of Me2SiCl2; no open
  value was found (D-005).
- The MeSiCl3/Me2SiCl2 split needs 93 theoretical stages at a reflux of 94 for 99.5 wt%
  Me2SiCl2. EP 1 957 504 B1 states 200 or more for a commercial split. Its reboilers take 43 %
  of the 0.95 kWh of steam drawn per kg (D-008, D-009).
- 0.030 kWh of electricity and 1.04 kWh of heat to cooling water per kg (D-009).
- Wastes per kg: 55 g of high-boiling residue, 15 g of spent contact mass (silicon with about
  9 wt% copper) and 20 g of vent gas to the site's thermal oxidiser (D-006 to D-008).
- The preliminary LCI shares the burdens by mass between the three silane products and gives
  none to the exported steam. Methyl chloride is linked to chloromethane-1; silicon and copper
  are gaps (D-012).
- Hazards: the strongly exothermic bed (about 1250 K without cooling), methyl chloride (a
  flammable gas under pressure), chlorosilanes (flammable, and they release HCl with water) and
  silicon dust (D-011).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams, design specifications and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts and `balance.py`: the reaction shares, the reactor's heat and every other duty, power and temperature core's models do not give (D-004, D-005, D-009) |
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
cheme process propagate --fill  # every flow, the specifications, the methyl chloride loop
cheme run scripts/balance.py    # the reaction shares, every duty and power (then update the flowsheet)
cheme assess lca --write        # the preliminary LCI
```
