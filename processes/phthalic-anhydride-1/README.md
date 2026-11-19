# Phthalic anhydride

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for phthalic anhydride (PA) by gas-phase oxidation of o-xylene with air over
V2O5/TiO2, the route US EPA AP-42 section 6.5 describes and the BASF and Süd-Chemie catalyst
patents run: air at 4 Nm3/h per tube is blown to 155 kPa(a), preheated on HP steam, and o-xylene
is evaporated into it at 80 g/Nm3; one multitubular reactor of 15 000 tubes, cooled by molten
salt at about 633 K, converts 99.9 % of it (79.0 % to PA, C8H10 + 3 O2 -> C8H4O3 + 3 H2O; maleic
anhydride, benzoic acid, CO and CO2 beside). The salt's 14.4 MW raise HP steam; a gas cooler
raises LP steam. Switch condensers desublime the PA at 333 K and melt it out on hot oil; the
crude is held at 523 K and distilled under vacuum (light ends, then the pure PA overhead, whose
condenser raises LP steam). The off-gas, about 1 vol% CO with maleic anhydride, is burnt in a
regenerative thermal oxidiser. Needs cheme-as-code 1.12.0. DESIGN.md lists the core features
used and the core limits hit.

Headline numbers and their caveats:
- 5055 kg/h of 99.99 wt% PA melt (about 40.4 kt/a), 1.053 kg per kg of o-xylene (0.9495 kg
  o-xylene per kg). The reactor's 1.102 kg/kg is at the conservative end of the sources (an
  ESCAPE-15 flowsheet's 1.10, an Air Products patent's 78 % selectivity, laboratory tubes'
  113.5-115 wt%); the selectivities are ASSUMED inside them (D-005).
- The CO share is set so that the off-gas carries AP-42's uncontrolled 151 kg CO per t, and the
  switch condensers' 97 % recovery so that it carries 62 kg of PA, maleic anhydride and benzoic
  acid per t against AP-42's 69 (D-005, D-007): a 1970s emission basis, conservative for a
  modern plant.
- The reactor duty is core's conversion-step model; the other duties (exchangers, switch
  condensers, columns) are hand calculations, because no property package of core covers phthalic
  or maleic anhydride (D-006 to D-009, limits L-1 to L-3).
- Per kg of PA: 2.86 kWh HP and 1.24 kWh LP steam exported, 1.02 kWh HP steam taken back,
  0.26 kWh electricity, 0.81 kWh to cooling water, 0.705 kg fossil CO2 at the stack. The steam
  carries no burden in the preliminary LCI (conservative for PA, D-012).
- The reactor feed is inside the flammable range of o-xylene in air and the reaction can run
  away at the hot spot: noted for basic engineering and the HAZOP (D-011).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml`, `process/simulation.yaml` | components with their ideal-gas data, blocks, steps, streams, reactions and the oxidiser's adiabatic mode: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts (none used yet) |
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
cheme process propagate --fill  # the mixer, the reactor and oxidiser, the separators and R101's duty
cheme process reactors          # reaction extents, duties, distance from equilibrium
cheme assess lca --write        # the preliminary LCI
```
