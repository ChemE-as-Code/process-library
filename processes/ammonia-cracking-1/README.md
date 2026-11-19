# Hydrogen by ammonia cracking

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant that turns ammonia back into hydrogen, the unpacking end of an ammonia
hydrogen-carrier chain. Pressurised liquid ammonia is vaporised against the cracked gas in
E-101, superheated in the convection section of the fired furnace H-101 and cracked over a
nickel catalyst in its tubes R-101, 2 NH3 <=> N2 + 3 H2, to equilibrium at 773 K and 1100 kPa(a),
the basis of Air Products' EP 4 337 600 A1. The cracked gas is cooled and its hydrogen
purified by pressure swing adsorption U-201 (79.4 % recovery, the patent's reference example 2);
the PSA tail gas, with the ammonia the beds retain, is the furnace's only fuel.

`cheme process propagate` solves the material balance: two design specifications (`specs:`,
core ADR 0070) set the ammonia feed for 200 t/d of hydrogen and the combustion air for 2 mol%
oxygen in the flue gas; the equilibrium reactor, the PSA's component split and the burners'
complete combustion give the rest, and propagate writes the convection section's duty.
`scripts/balance.py` gives the tubes' duty, the ammonia vaporiser and the stack temperature that
closes the furnace. Needs cheme-as-code 1.13.0. DESIGN.md lists the core features used and the
core limits hit.

Headline numbers and their caveats:
- Per kg of hydrogen product (99.99 mol%, 1030 kPa(a)): 7.27 kg of ammonia (7.28 per kg of
  H2), 11.96 kg of air, 0.018 kWh of electricity, 0.758 kWh to cooling water, 18.2 kg of flue gas (N2, water vapour, 2 % O2); no
  CO2 on site. JRC EUR 31199 gives 0.137 t of hydrogen per t of ammonia (7.30 kg/kg) for the
  open large-scale design.
- 97.4 % of the ammonia is cracked at equilibrium on ideal-gas data (the patent's example
  implies 97.0 %); 77.4 % of its hydrogen reaches the product, the rest fires the furnace.
- The furnace absorbs 70.9 MW (53.6 MW in the tubes, 17.3 MW superheat) of the tail gas's
  80.1 MW (LHV); the combustion air is preheated to 623 K in the convection section (9.1 MW),
  so the flue gas leaves the radiant section at 993 K, 220 K above the tube outlet, and the
  stack at 492 K. The tubes are not sized: whether they take their duty at that firebox
  temperature is open (D-006). No steam is raised or exported.
- Burner NOx from the ammonia in the tail gas is not estimated (no open factor read); it is an
  open exclusion of the LCI (D-006, D-010). The catalyst and adsorbent replacement is an open
  input, noted in a comment of lca/lca.yaml but not in the dataset; the ammonia's pumping and
  warming before S1 (about 49 kW and 4.1 MW) are outside the boundary (D-003, D-010).
- The hydrogen leaves at the PSA's pressure; compression for a pipeline or trailers is outside
  the boundary (D-001).
- Hazards: toxic ammonia, flammable hydrogen, nitriding and hydrogen attack at 773 K, a furnace
  fired on a swinging tail gas (D-009). The reaction is endothermic: no runaway.

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components (with their ideal-gas data), blocks, steps, streams, design specifications and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/balance.py` | the duties core does not calculate, the fan and the stack temperature (D-008) |
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
cheme process propagate --fill  # the feeds, R-101's equilibrium, the PSA, the burners, Q2
cheme run scripts/balance.py    # the other duties and temperatures (then propagate again)
cheme assess lca --write        # the preliminary LCI
```
