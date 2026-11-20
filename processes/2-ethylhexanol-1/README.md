# 2-Ethylhexanol

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous oxo-alcohol plant for 2-ethylhexanol after Ruhrchemie's US 4 684 750 A and
US 4 523 036 A. Propylene, carbon monoxide and hydrogen react at 5 MPa and 393 K over rhodium
with the water-soluble ligand TPPTS in an aqueous catalyst phase, CH2=CHCH3 + CO + H2 ->
CH3CH2CH2CHO (95 % n-, 5 % isobutanal). The crude is decanted from the catalyst phase, its
dissolved propylene stripped back by the fresh synthesis gas, and a column of 100 theoretical
plates, heated by the reactor's heat, takes off the isobutanal. n-Butanal condenses with
aqueous caustic at 413 K to 2-ethyl-2-hexenal and water; the organic phase is hydrogenated over
copper in the gas phase and over nickel in the liquid phase, and three columns give the product,
the light ends and the heavies.

`cheme process propagate` solves the whole material balance: five design specifications
(`specs:`, core ADR 0070) set the propylene, synthesis gas, water, caustic and hydrogen feeds,
together with six tear streams (ADR 0060), the conversion steps and nine component separators
(`recovery:`). The plant yields 97.73 % of theory on n-butanal, the 97.74 % of the patent. Needs
cheme-as-code 1.13.0. DESIGN.md lists the core features used and the core limits hit.

Headline numbers and their caveats:
- Per kg of 2-ethylhexanol: 0.713 kg propylene, 0.530 kg synthesis gas (H2/CO about 1:1),
  0.034 kg hydrogen, 3.9 g caustic soda 50 wt%; 0.059 kg isobutanal co-produced, 0.023 kg light
  ends and 0.018 kg heavies to fuel, 0.039 kg off-gas to the fuel gas, 0.154 kg aqueous
  effluent; 0.479 kWh MP steam imported, 0.249 kWh LP steam exported, 1.39 kWh to cooling water,
  0.032 kWh of electricity (with the vacuum pumps).
- The per-pass propylene conversion (90 %), the gas composition and the purges are ASSUMED: no
  open source read gives them (D-004). The crude's n/iso/heavies split, the column's purities,
  the aldol's caustic strength and the overall yield are the patent's.
- The n/iso column runs at a reflux of 50 (1.1 x Underwood's minimum at a relative volatility
  of 1.43), only its organic overhead refluxed; R-101's heat covers its 5.2 MW reboiler, as
  US 4 523 036 A does, and the rest of R-101's 8.7 MW goes to cooling water (D-009).
- No property package of core covers these liquids: every duty comes from `scripts/balance.py`
  on formation enthalpies and constant heat capacities (L-2); the columns are component splits
  (L-5).
- The LCI allocates by mass between 2-ethylhexanol and isobutanal; the synthesis gas has no
  library producer (a gap), and the rhodium and catalyst make-up are open inputs (D-010).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams, design specifications, tears and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/balance.py` | the duties and powers core does not calculate, the mixers' and the compressors' outlet temperatures (D-009) |
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
cheme process propagate --fill  # the feeds, the loops and the recycles
cheme run scripts/balance.py    # the duties, powers and mixer temperatures (copy them into the flowsheet)
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
cheme assess lca --write        # the preliminary LCI
```
