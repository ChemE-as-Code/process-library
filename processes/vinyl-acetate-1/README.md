# Vinyl acetate monomer

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for vinyl acetate monomer by gas-phase acetoxylation of ethylene, after
Wacker's patents US 8 765 995 B2 and US 8 410 307 B2: ethylene, acetic acid and oxygen react
over a palladium-gold catalyst with potassium acetate in a multitubular fixed bed R-101 cooled
by boiling water, C2H4 + CH3COOH + 0.5 O2 -> CH2=CHOOCCH3 + H2O, while part of the ethylene
burns to CO2. The effluent is condensed and decanted in a preliminary dewatering column at loop
pressure; the cycle gas is scrubbed with recycle acetic acid, 0.3 % of it purged, a third of it
washed with water and freed of CO2 on hot potassium carbonate, and recompressed. An azeotropic
column with a decanter and a dewatering column with the product side draw give 99.99 wt% vinyl
acetate and the recycle acid.

`cheme process propagate` solves the whole material balance: four design specifications
(`specs:`, core ADR 0070) set the ethylene, oxygen and acid feeds and the CO2 slip for 200 kt/a
and the source's reactor feed (65 mol% ethylene, 12.3 mol% acetic acid, 8.6 mol% oxygen),
together with three tear streams (ADR 0060), the conversion reactor and six component
separators (`recovery:`). It writes R-101's heat from the ideal-gas data (ADR 0059): 23.7 MW,
raised as LP steam that covers all but 6.18 MW of the plant's steam. Needs cheme-as-code 1.12.0.
DESIGN.md lists the core features used and the core limits hit.

Headline numbers and their caveats:
- Per kg of vinyl acetate: 0.370 kg ethylene, 0.703 kg acetic acid, 0.299 kg oxygen, 0.022 kg
  wash water; 0.0995 kg CO2 vented, 13 g of purge gas to the thermal oxidiser, 0.280 kg aqueous
  effluent; 0.247 kWh of imported LP steam, 1.38 kWh to cooling water, 0.045 kWh of electricity.
- The conversions per pass (9.61 % of the ethylene to vinyl acetate, 0.95 % burnt) come from the
  space-time yield, space velocity and 91.0 % selectivity of the patent's pilot tubes (D-004);
  88.1 % of the ethylene ends in the product once the purge and the CO2 vent are counted.
- Every vapour is the ideal-gas monomer of the formation enthalpies R-101's duty uses: the heats
  of vaporization are the differences of the packaged liquid and gas formation enthalpies
  (D-008). Acetic acid's association in the vapour is left out (L-2).
- The LCI leaves the catalyst's replacement as an open gap (no open rate) and cuts off the
  carbonate's K2CO3 make-up and the product's inhibitor with their amounts (D-010).
- The separators' splits, the purge and the columns' boil-ups are ASSUMED (D-005 to D-008); no
  property package of core covers these liquids, so every duty but R-101's comes from
  `scripts/balance.py` on an ideal-gas and constant-heat-capacity basis (L-1, L-2).
- The flammability of the 8.6 mol% oxygen feed and the reactor's thermal runaway are reasoned
  in D-009, not screened: core's screening needs kinetics the open sources do not give (L-3).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components (with their ideal-gas data), blocks, steps, streams, design specifications, tears and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/balance.py` | the duties and powers core does not calculate, the mixers' and the compressor's outlet temperatures (D-008) |
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
cheme process propagate --fill  # the feeds, the loop, the recycles and R-101's duty
cheme run scripts/balance.py    # the other duties and powers (then propagate again: Q1 follows)
cheme process reactors          # R-101's extents and duty
cheme assess lca --write        # the preliminary LCI
```
