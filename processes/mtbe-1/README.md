# Methyl tert-butyl ether

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for MTBE from the isobutene of a C4 raffinate and methanol by catalytic
(reactive) distillation, the column of the open simulation study of Murat, Mohamed and Bhatia
(2003): C4H8 + CH3OH <=> (CH3)3COCH3 on an acidic ion-exchange resin (6400 kg on stages 3 to 10
of 17), 11 bar, reflux ratio 7, methanol and the vaporised raffinate both fed to stage 10. The
reaction removes the isobutene from the C4 as MTBE forms and leaves at the bottom. The C4
overhead carries the excess methanol; a water wash takes it out (US 5 336 841 A, US 4 918 243 A)
and a low-pressure methanol column returns it to the column. The washed raffinate-2 goes back to
the C4 supplier.

`cheme process propagate` solves the whole material balance: two design specifications
(`specs:`, core ADR 0070) set the fresh methanol for the column's 206 mol/s and the make-up
water for the wash ratio, together with two tear streams (ADR 0060), the conversion step of the
reactive zone and three component separators (`recovery:`). Needs cheme-as-code 1.13.0.
DESIGN.md lists the core features used and the core limits hit.

Headline numbers and their caveats:
- About 500 kt/a of MTBE product (62.3 t/h), 99.10 wt% MTBE with 0.90 wt% C4; 99.5 % of the
  isobutene converted (the source's model).
- Per kg of product: 0.634 kg isobutene (taken out of 1.781 kg of raffinate-1, whose 1.147 kg of
  inert C4 return as raffinate-2 but for 0.009 kg that leaves in the MTBE), 0.360 kg methanol,
  0.0040 kg make-up water; 0.631 kWh MP steam, 0.245 kWh LP steam, 0.934 kWh to cooling water,
  0.0038 kWh electricity.
- C-101's condenser (49.7 MW) and reboiler (39.3 MW) are the source's values; the raffinate
  vaporiser (13.0 MW) is the largest other duty. No heat integration.
- The column is a conversion step and a component split: core has no reactive-distillation
  model, and no property package covers these strongly non-ideal liquids (L-1, L-2). The wash
  and methanol column's splits are ASSUMED within the patents' figures.
- A closely similar column (Jacobs and Krishna's: same butenes feed, 8000 kg of catalyst, 4 %
  more methanol) has three steady states (Svandova et al. 2007); whether this one does is
  unchecked. Start-up and control are reasoned in D-009 as a precaution, not screened.
- The LCI subdivides the raffinate: only its isobutene carries a burden (linked to
  butadiene-1's raffinate-1), the inert C4 and the raffinate-2 are outside the system; the
  0.009 kg/kg of inert C4 in the product is a declared cut-off (D-010).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components (with their ideal-gas data), blocks, steps, streams, design specifications, tears and the reaction: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/simulation.yaml` | the reactive zone declared adiabatic (its heat stays in the column) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/balance.py` | the duties and powers core does not calculate (D-008) |
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
cheme process propagate --fill  # the feeds, the recycles and the column's split
cheme run scripts/balance.py    # the duties and powers outside the column
cheme process reactors          # the reactive zone's extent
cheme assess lca --write        # the preliminary LCI
```
