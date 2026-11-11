# Ethylbenzene by liquid-phase zeolite alkylation

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A concept-stage plant kept as plain files in git: 400 kt/a ethylbenzene from benzene and
ethylene, alkylation on a fixed-bed zeolite in the liquid phase, transalkylation of the
polyethylbenzenes, benzene recycle, benzene, EB and PEB columns and a flux-oil by-product.
Design basis, materials, reactions with their evidence, flowsheet, generated BFD and PFD, a DWSIM
simulation, an independent balance script and an LCI derived from the flowsheet. No P&IDs,
HAZOP, layout or estimate yet (concept scope of issue #313).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/reactions.yaml`, `process/reaction-evidence.yaml` | components (with the model compounds), reactions, the evidence and model basis behind them |
| `process/flowsheet.yaml` | blocks, steps and streams: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/simulation.yaml`, `process/simulation-run.json` | the DWSIM model and its last run (`cheme process simulate`) |
| `scripts/eb_balance.py` | the independent heat and material balance the simulation is checked against (`cheme run scripts/eb_balance.py`) |
| `equipment/equipment-list.yaml` | the items the PFD links |
| `lca/` | goal and scope (`lca.yaml`) and the generated inventory and dataset (`cheme assess lca --write`) |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions (with the BREF comparison, D-015), change log, stage definitions |
| `.claude/skills/` | how an agent works here (not in git: run `cheme skills update` once after cloning) |

## How it is built and how far it goes

- **Simulation status.** DWSIM 9.0.5 with Peng-Robinson solves the whole plant, but core has not
  qualified that property package for aromatics, so the simulation is an *unqualified
  cross-check* of `scripts/eb_balance.py`, not validated data (D-006, D-014). Reactor heat and
  column duties agree within about 1 %; two mixer temperatures do not (open input I-07).
- **Reaction model.** All ethylene converted (ASSUMED); its shares to EB and polyethylbenzenes
  from a patent lab example at a different benzene/ethylene ratio; flux oil 4.3 kg/t, the BREF
  midpoint, modelled as pentaethylbenzene; transalkylation conversion ASSUMED (D-005).
- **LCI.** `lca/dataset.yaml` is derived from the flowsheet and is this process's LCI in the
  library (it replaced the hand-written Tier 1 dataset of the earlier manifest-only pilot, D-013).
  All burdens go to the ethylbenzene; flux oil and exported steam get none and no credit. Every
  background is still a gap, so no impact result is claimed.
- **Cross-check with the EU LVOC BREF (2017, chapter 5).** Benzene 0.737 t/t, steam 521 kWh/t and
  heat recovered as steam 742 kWh/t sit inside the BREF's ranges; ethylene 0.267 t/t is 0.7 %
  above its range because of the flux-oil model compound; electricity 6.4 kWh/t is far below,
  because only the feed pumps are modelled (D-015, `benchmarks/styrenics.yaml`).

## Linking

The product's inventory key is `product:ethylbenzene` (registry slug `ethylbenzene`), the same
key the Tier 1 dataset had; `styrene-1` links it explicitly in its `lca/mappings.yaml`. Benzene
and ethylene stay reported mapping gaps: their suppliers are not chosen (`lca/mappings.yaml`).

## Working here

The tools come from [`cheme-as-code`](https://github.com/ChemE-as-Code/core); install it once
(see its README), run `cheme skills update` once in this folder, then:

```sh
cheme validate                  # after every change
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
cheme process simulate --check  # DWSIM run, compared with the flowsheet (needs the DWSIM image)
cheme run scripts/eb_balance.py # the independent balance
cheme assess lca --coverage     # the LCI and its gaps
```

Data and designs here are under CC BY 4.0 (`LICENSE-DATA` of the library), scripts under
AGPL-3.0-or-later.
