# Acrylonitrile (SOHIO propylene ammoxidation)

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: engineering lists as YAML, decisions and progress as
Markdown, the BFD and PFD generated from the flowsheet. Edited by people and by coding agents
(Claude Code), checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for 15 t/h (120 kt/a) of acrylonitrile by the SOHIO process: propylene,
ammonia and air (1/1.2/9.8 mol) react over a bismuth molybdate catalyst in a fluidised bed at
713 K and 200 kPa(a), whose cooling coils and effluent boiler raise HP steam. The effluent is
quenched with sulfuric acid, which takes the unconverted ammonia as ammonium sulfate; the
nitriles are absorbed in chilled water, recovered overhead in an extractive recovery column, and
separated into HCN, acrylonitrile and acetonitrile; the lean water returns to the absorber. The
absorber off-gas and a heads cut are burnt in a thermal oxidiser with a waste-heat boiler.
Propylene, ammonia and sulfuric acid come from `propylene-pdh-1`, `ammonia-1` and
`sulfuric-acid-1`. Needs cheme-as-code 1.12.0. DESIGN.md lists the sources, the decisions, the
core features used and the core limits hit.

Headline numbers and their caveats:
- The reactor is a conversion step with the product slate of an open catalyst patent
  (US 6 596 897 B1: 97.5 % propylene conversion, 79.7 % single-pass acrylonitrile yield), not
  kinetics (D-004). It gives 0.999 kg propylene and 0.485 kg ammonia per kg product, below the
  IPCC 2006 default of 1.09 t/t, which rests on the 2003 plants of the EU BREF.
- cheme's design specifications solve the propylene feed for the product rate, the acid for a 5 %
  excess over the unconverted ammonia, and the lean-water split for the absorber's water rate,
  with the recycle converged (core ADRs 0060, 0070).
- The quench, absorber and columns are component separators with ASSUMED splits: no property
  package covers the nitrile/water system (L-1). Product 99.75 wt%, overall recovery 99.5 %.
- Reactor duty 56.8 MW (cheme, ideal gas), net of heating the feed in the bed. With the feed at
  the reactor temperature the reaction heat is 913 MJ per kmol acrylonitrile, 13-16 % above the
  open design of Li, Dimian and Kiss (2025), mostly from the ASSUMED burning of the surplus
  ammonia; without it the two agree (D-004). HP steam raised 4.73 kWh per kg; LP steam
  2.22 kWh per kg (that design's hot utility less its fired feed preheat) and cooling water
  3.67 kWh per kg are lumps scaled from it (D-009); power 0.44 kWh per kg, with the absorber
  water chiller sized on this design's water rate.
- Co-products per kg: HCN 0.036 kg, acetonitrile 0.039 kg, quench liquor 0.24 kg (about 28 wt%
  ammonium sulfate). Fossil CO2 0.46 kg/kg (reactor and oxidiser). The preliminary LCI allocates
  by mass (93.0 % to acrylonitrile, D-011).
- Hazards: acrylonitrile and HCN are toxic and flammable; liquid HCN self-polymerises unless
  acid-stabilised and acrylonitrile polymerises explosively with strong alkali, and neither
  stabiliser is modelled or screened (D-007); the reactor feed is a flammable
  propylene/ammonia/air mixture and start-up passes through the explosive range (EPA-450/4-84-007a);
  cheme's screening bound for the fluid bed, complete combustion of the propylene over the whole
  feed's heat capacity, is about 2150 K (the ammoxidation alone about 1270 K), so its cooling
  coils and trips carry its safety. No HAZOP yet.

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml`, `process/catalysts.yaml` | components with their ideal-gas data, blocks, steps, streams, specs and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml` | the equipment of the PFD with concept design data |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `scripts/utilities.py` | the effluent boiler's duty, the air compressor's and the chiller's power, and the LP steam and cooling-water lumps, which core does not calculate (D-009) |
| `checks/checks.yaml` | engineering-step gates |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `.claude/skills/` | how an agent works here (not in git: run `cheme skills update` once after cloning) |

## How this repository works

- **This repository holds the plant**: drawings, lists, decisions. It does not hold the tools,
  which come from [`cheme-as-code`](https://github.com/ChemE-as-Code/core).
- **Licences.** This folder is part of the ChemE-as-Code process library. Its data and designs are
  under CC BY 4.0 (`LICENSE-DATA`); its skills and scripts are under AGPL-3.0-or-later
  (`LICENSE`). It is public (`publication` in `process.yaml`: public, CC-BY-4.0).
- **The skills in `.claude/skills/` are not in git.** Run `cheme skills update` once in this
  folder after cloning.

## Working here

```sh
cheme validate                  # after every change
cheme check                     # engineering-step gates (--write only at sign-off)
cheme process propagate --fill  # the specs, the separators, the recycle and the conversion duties
cheme run scripts/utilities.py  # E-101's duty, K-101's and the chiller's power, the lumps (then update Q1, Q2, Q5, Q7, Q8)
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
cheme assess lca --write        # the preliminary LCI
```
