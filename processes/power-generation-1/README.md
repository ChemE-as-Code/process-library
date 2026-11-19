# Electricity from a natural-gas combined cycle

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A 2x1 F-class natural-gas combined cycle (NGCC) at the operating point of NETL's Case B31A
(Cost and Performance Baseline for Fossil Energy Plants, Revision 4a, DOE/NETL-2023/4320, 2022):
two gas turbine generators with dry low-NOx combustors burn pipeline gas (93.1 mol% methane) in
ambient air at ISO conditions; their exhaust at 625 degC raises steam in two three-pressure
reheat heat recovery steam generators (HRSGs) with an SCR, HP steam at 16.5 MPa and 585 degC and
reheat at 584 degC, and leaves the stacks at 83 degC; a reheat steam turbine exhausts at 50.8 mm
Hg to a surface condenser on a mechanical-draft wet cooling tower. The plant delivers its
electricity, less its own use, to a 345 kV grid.

The gas turbines are one conversion step of cheme-as-code (complete combustion on ideal-gas data,
`reactor: conversion`): `cheme process propagate` calculates their exhaust and, from its energy
balance, the work and losses that leave the machines (483.9 MW, 0.08 % below NETL's), and with
`energy_port` (core ADR 0059) their electrical output after NETL's generator efficiency. Core has
no gas turbine, steam turbine or HRSG model and no water/steam property package, so the steam
loop's states, the steam turbine's power and the condenser's duty come from NETL's stream table
through `scripts/ngcc_balance.py`, which also carries NETL's water balance and auxiliary loads.
Needs cheme-as-code 1.12.0. DESIGN.md lists the core features used and the core limits hit.

Headline numbers and their caveats:
- 725.8 MW net (NETL 727 MW) from 476.6 MW gas turbine and 262.7 MW steam turbine generation less
  13.6 MW own use: 53.57 % net efficiency on HHV, 59.35 % on LHV (NETL 53.6 and 59.4 %), 6,720 kJ
  (HHV) or 0.1285 kg of gas per kWh (D-005 to D-010). These reproduce a published design point;
  they are not a prediction of the machines' performance (L-1, L-2).
- 0.343 kg of fossil CO2 per kWh from the carbon balance (NETL 342 kg/MWh net). NOx, CO, SO2 and
  particulates are NETL's stack rates for this plant's DLN burners and SCR; CH4 and N2O are
  EPA AP-42 factors for natural-gas turbines (D-011). The preliminary gate-to-gate LCI links the
  natural gas, the water and the SCR's ammonia (ammonia-1) in the Atlas build; the raw water is
  a gap.
- Base load at ISO conditions only, 7446 full-load hours a year (NETL's 85 % capacity factor,
  ASSUMED as full-load hours); no part load, start-ups or ambient variation (D-002, L-4).
- The cooling tower is inside the plant: its make-up is 0.905 kg of raw water per kWh, of which
  0.70 kg evaporates (NETL's water balance, D-009).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components with their ideal-gas data, blocks, steps, streams and the combustion reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts and `ngcc_balance.py`: the stack gas, the water/steam loop, the steam turbine generator, the condenser, the cooling tower and the auxiliary loads from NETL's numbers (D-006 to D-010) |
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
cheme validate                    # after every change
cheme check                       # engineering-step gates (--write only at sign-off)
cheme process build               # BFD and PFD from process/*.yaml
cheme process streams             # stream table with provenance, block balances
cheme run scripts/ngcc_balance.py # the stack gas, the steam loop, the auxiliaries (prints its cross-checks)
cheme process propagate --fill    # the gas turbines' exhaust and power (then update the net export Q11, D-010)
cheme assess lca --write          # the preliminary LCI
```
