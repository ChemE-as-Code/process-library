# Bioethanol (corn dry grind)

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

Fuel ethanol from corn by the dry-grind process, on the basis of the open USDA-ARS/NREL dry-mill
model (McAloon et al. 2000, NREL/TP-580-28893): 633 dry short tons of corn a day are cleaned and
hammer-milled, slurried with recycled condensate, liquefied at 88 C with alpha-amylase, mixed
with backset, cooked at 110 C and saccharified at 60 C with glucoamylase. Yeast ferments the
glucose in four continuous cascade fermentors (46 h, 32-34 C) to a beer of 9 wt% ethanol; the CO2
is water-scrubbed and vented. A beer column takes the ethanol to 45 wt%, a rectifier to 91 wt%
and vapour-phase molecular sieves to 99.55 wt%: 9.00 t/h, 71 300 t/a in 7920 h. Decanters split
the whole stillage into wet cake and thin stillage; part of the thin stillage goes back as
backset, the rest is evaporated to a syrup, and a natural-gas dryer makes DDGS from the wet cake
and syrup. The plant discharges no liquid.

Core propagates the whole flowsheet from the corn: conversion reactors (`reactor: conversion`),
component separators with specified recoveries (`recovery:`, core ADR 0070), the dryer to a
residual moisture (`dryer:`), four recycles converged at tears (`tears:`, ADR 0060) and two design
specifications (`specs:`, ADR 0070): the scrubber's make-up water for the beer's 9 wt% and the
backset share for 15 % of the mash. Needs cheme-as-code 1.12.0. DESIGN.md lists the core
features used and the core limits hit.

Headline numbers and their caveats:
- Yield: 8959 kg/h of ethanol, the source's stated rate, 113.67 gal per dry short ton of corn at
  68 F (the source's appendix: 113.68; its p. 2 rounds to 114), 0.374 kg per kg of dry corn. The
  fermentation's conversion (94.2 % of the glucose to ethanol) is calibrated to it; 3 % to
  glycerol and acetate is ASSUMED (D-005).
- Per kg of ethanol: 3.13 kg of corn (15 % moisture), 0.98 kg of DDGS, 0.96 kg of biogenic CO2,
  1.70 kWh of steam (150 psig), 0.074 kg of natural gas (1.03 kWh LHV), 0.23 kWh of power and
  1.55 kWh to cooling water. Steam, gas and cooling water are the rates the source's appendix
  states, power its p. 24 figure with its area shares, split between the users by ASSUMED shares
  (D-009).
- The separations are specified recoveries chosen for the source's stated compositions (45 and
  91 wt% ethanol, 35 wt% wet cake, 55 wt% syrup), not rigorous ethanol-water VLE: core has no
  property package for corn mash or ethanol-water (D-007, L-1).
- The zero-discharge water balance needs 9.3 t/h of make-up (1.03 kg/kg), 4.0 % above the source's
  8.9 t/h, which it puts on the CO2 scrubber; a real plant takes part of it as live steam and
  cleaning water (D-006).
- The DDGS is 4.2 % below the source's 9205 kg/h: yeast growth, enzymes, urea and lime are not in
  the balance (D-008, L-3).
- Hazards reasoned in D-011: ethanol (flammable), CO2 in the fermentation area (asphyxiation),
  grain dust, dryer fires; the continuous fermentation is not a runaway hazard.
- The preliminary LCI allocates by mass between ethanol (50.5 %) and DDGS (the WBCSD rule on the
  source's prices); the fermentation CO2 is biogenic, the dryer's CO2 fossil; the source's
  caustic, sulfuric acid, lime, urea, enzymes and yeast (39 g per kg of ethanol) are consumables;
  the corn, the enzymes and the yeast are gaps (D-012).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | lumped corn components, blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts (none needed yet: core propagates the whole balance) |
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
cheme process propagate --fill  # the reactors, separators, dryer, recycles and specifications from the feeds
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
cheme assess lca --write        # the preliminary LCI
```
