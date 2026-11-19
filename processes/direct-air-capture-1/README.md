# Carbon dioxide by direct air capture (KOH solvent, calcium loop)

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant that takes CO2 out of the air by the liquid-solvent process published by Keith
et al. (2018, Joule 2, 1573) and re-evaluated by NETL (2022, DOE/NETL-2021/2864). Ambient air is
blown through cross-flow contactors wetted with aqueous potassium hydroxide, which captures
74.5 % of its CO2 as potassium carbonate. In fluidised pellet reactors slaked lime precipitates
the carbonate as CaCO3 pellets and regenerates the KOH. A steam slaker dries the pellets with the
heat of slaking the hot quicklime, and an oxy-fired fluidised bed calciner at 900 C, fired with
natural gas in 95.6 wt% oxygen, releases the CO2 together with the fuel's CO2. The off-gas is
compressed to 15.1 MPa and dried. This entry takes grid power and burns gas only in the calciner
(Keith et al.'s scenario C); the on-site gas turbine of their baseline is outside it.

Every material stream is the steady state of `scripts/dac_balance.py`, which closes the KOH and
calcium loops by stoichiometry from the published capture fraction, conversions, carry-overs and
make-ups; core checks the mass and element balances of every step and builds the BFD and PFD.
Core has no electrolyte, crystallisation or gas-liquid mass-transfer model for this chemistry,
so the loops are not iterated by `cheme process propagate` (DESIGN.md L-1 to L-4). Needs
cheme-as-code 1.13.0.

Headline numbers and their caveats (per kg of the CO2 product, 97.0 wt% CO2):
- 0.756 kg of CO2 from the air (112.2 t/h from 251 000 t/h of air) and 0.244 kg from burning
  0.079 kg of natural gas (5.23 GJ LHV per t of air CO2) in 0.345 kg of oxygen; 77.6 % of the
  product's carbon comes from the air (D-007, D-011).
- 0.235 kWh of grid power (310 kWh per t of air CO2, from Keith et al.'s per-unit figures; their
  scenario C states 366 kWh/t with the oxygen plant and without this entry's missing slaker
  power credit) (D-009). The CO2 train's cooling (0.261 kWh, hand estimate) goes to the
  contactor basins, where the air takes it up with the evaporation: no cooling tower (D-003,
  D-009).
- 3.67 kg of process water, mostly the 4.7 t evaporated per t of CO2 captured at 20 C and
  64 % RH, which depends strongly on the climate and on the heat rejected to the contactors
  (D-003); 13.5 g of KOH and 20.2 g of CaCO3 seed make-up scaled from NETL, 28.8 g of filter
  cake purge and 0.124 kg of liquor bleed (D-005).
- The liquor's density, the complete causticisation, the purge cake, the bleed and the hand
  energy balances are ASSUMED; the product holds 1.5 wt% N2 and 1.5 wt% O2 from the oxidant and
  is not a 99.95 mol% pipeline grade (D-008).
- The preliminary LCI books the air's CO2 as a resource (`Carbon dioxide, in air`); oxygen is
  linked to asu-1, natural gas, KOH, limestone, the purge's landfill, the process water (a
  conservative proxy) and the condensate's and the bleed's treatment to shared entries. It
  makes no net-removal claim: storage and the backgrounds are not assessed (D-011).

## What is here

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams and the reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `scripts/dac_balance.py` | the steady-state balance every material stream cites (`cheme run scripts/dac_balance.py`, `--yaml` for the streams) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists (equipment with first sizes; lines and instruments with the P&IDs) |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
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
cheme validate                       # after every change
cheme check                          # engineering-step gates (--write only at sign-off)
cheme run scripts/dac_balance.py     # the balance; --yaml prints the streams
cheme process build                  # BFD and PFD from process/*.yaml
cheme process streams                # stream table with provenance, block balances
cheme assess lca --write             # the preliminary LCI
```
