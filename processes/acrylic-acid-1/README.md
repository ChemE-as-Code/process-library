# Acrylic acid

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for 100 kt/a of glacial acrylic acid by two-stage catalytic oxidation of
propylene with air and steam. Propylene (from `propylene-pdh-1`) is oxidised to acrolein over a
Mo-Bi mixed oxide at 583 K in a multitubular reactor cooled by molten salt, whose after-cooling
zone keeps the gas below 260 C; secondary air and steam are added and the acrolein is oxidised to
acrylic acid over a Mo-V oxide at 538 K. Feed ratios, temperatures, conversions and yields follow
the examples of US 4 873 368 A (Mitsubishi Petrochemical). The salt raises HP steam for export.
The gas is cooled and quenched in inhibited water to a 55 wt% aqueous acid; the off-gas goes to a
catalytic oxidiser. Water is removed by azeotropic distillation with toluene at 180 mmHg (US 5 910
607 A, Example 1), acetic acid and toluene in a second vacuum column (the toluene back to the
first), and the glacial acid is distilled at 8 kPa(a), with hydroquinone in the columns and 200 ppm
MEHQ in the product.

Both reactors are conversion steps of core (the first with its reported selectivities), the
separators are component splits (`recovery:`), the toluene recycle is a tear that propagate
converges, and core writes the reactors' duties from the heats of reaction. An independent script
(`scripts/aa_balance.py`) sizes the feeds and gives the temperatures and duties no core model
gives. DESIGN.md lists the sources, every decision and the core limits hit.

Headline numbers and their caveats:
- 0.686 kg of propylene feed per kg of product; 85.6 % of the propylene fed ends as product (the
  reactors 87.8 %, US 4 873 368 A, Example 5; the rest lost in the side draw, the heavy ends and
  the off-gas, D-005, D-008, D-009). The by-products are lumped as CO2 and acetic acid.
- The reactors release 35.2 MW (2.82 kWh per kg), raised as HP steam; the columns take 18.3 MW of
  LP steam (1.46 kWh per kg), most of it the dehydration column at the source's toluene reflux
  (D-008, D-010). Duties rest on ideal-gas and pure-liquid data without heats of mixing.
- The separator splits are ASSUMED to meet the compositions US 5 910 607 A states (D-007, D-008).
- Hazards: the feed lies in propylene's flammable range, acrolein is very toxic, acrylic acid
  polymerises violently (1077 kJ/kg, Arkema data sheet) without inhibitor and oxygen (D-013).
- Preliminary gate-to-gate LCI, the export steam allocated by exergy (acrylic acid 83.6 %);
  propylene linked to propylene-pdh-1, toluene to btx-1, most other backgrounds gaps (D-012).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components (with their ideal-gas data), blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/simulation.yaml` | the catalytic oxidiser declared adiabatic |
| `equipment/equipment-list.yaml` | the equipment of the PFD with its duties |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | `aa_balance.py`: the feeds for 100 kt/a, the temperatures and duties core's models do not give; `allocation_exergy.py`: the exergies of the LCA allocation |
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
cheme process propagate --fill  # the semi-batches, the stills, the recycles and their duties from the feeds
cheme run scripts/balance.py    # the feeds, the absorber, the other temperatures and duties (then propagate again)
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessel, jacket, vent (--svg)
cheme process reactor-hazards   # thermal screening of the two semi-batches
cheme process stills            # the strip and the rectification: cuts, purity, recovery, boil-up time, duties
cheme assess lca --write        # the preliminary LCI
```
