# BHET by PET glycolysis

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant that recycles post-consumer PET to its monomer, bis(2-hydroxyethyl) terephthalate
(BHET), by method B of EP 0 723 951 A1 (Example 2): washed bottle flake, fresh and recovered
ethylene glycol (2 kg per kg PET), zinc acetate and the wet recycled oligomers are heated in
R-101, their water (4.3 wt% of the charge) distilled off on the way, and held 2 h at the glycol's
reflux at 470 K (a conversion step: 87 % of the repeat units to BHET, 13 % left as oligomers, a
little DEG). The hot glycolysate is filtered of the non-PET solids and run into the second mother
liquor of the batch before last (held in T-304) at 343 K, where the oligomers precipitate and are filtered off, 90 % of them back
to the next charge. The liquor is cooled to 288 K for the crude BHET, which is redissolved in
6 kg of hot water per kg at 353 K, recrystallised at 288 K, centrifuged and vacuum-dried at
343 K (core's crystallizer and dryer, ADRs 0056, 0057, 0076). The first mother liquor, with the
dryer's condensate and the reactor's heat-up distillate, is distilled and both the water and the glycol (with the BHET and catalyst it holds) are recycled.
Four design specifications size the flake for 5000 t/a, the fresh glycol, the catalyst and the
make-up water, and four recycles converge at tears (core ADRs 0060, 0070).
`process/recipe.yaml` gives the cycle (6.248 h, set by the dryer, the reactor's 6 h close behind), 1268
batches a year of 3944.66 kg, and sizes the dryer; `cheme process reactor-hazards` screens the
reactor. Needs cheme-as-code 1.13.0. DESIGN.md lists the core features used and the core limits
hit.

Headline numbers and their caveats:
- Per kg of BHET: 0.776 kg of washed flake (0.756 stoichiometric; 97.7 % of the repeat units to
  dried BHET), 0.315 kg of fresh glycol (0.244 stoichiometric), 0.06 g of zinc acetate, 0.32 kg of
  make-up water; 7.9 kWh of steam heat, of which 6.7 kWh is the dewatering column's reboiler;
  1.05 kWh of chilled-water cooling; 0.10 kg of purges to incineration and 0.31 kg of water to
  wastewater treatment. The dried BHET is 99.8 wt%.
- The water route distils about 6 kg of water per kg of BHET: the column dominates the energy, as
  Luo et al. (2023) find for their water-antisolvent case; vapour recompression or crystallising
  from the glycol (D-001, D-009) would cut it.
- The conversion split, both crystallisation yields and every heat of reaction are ASSUMED from
  the patent's worked example and two open solubility points (no open kinetics, calorimetry or
  solubility curve, D-005, D-007). The reactor runs at reflux with no exotherm (dT_ad 0 K, MTSR at
  the MTT); its hazards are the hot glycol, steam and the quench (D-011).
- The LCI is preliminary. In the Atlas LCI the glycol, the make-up water, the steam, power,
  cooling water and the wastewater are linked; six exchanges are gaps: the flake's sorting and
  washing, the catalyst, chilled water and the incineration of the three purges. Core's own
  `cheme assess lca` has no background here and lists all 13 exchanges as unmapped
  (lca/gaps.csv; D-012).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures over several steps, the dryer's vessel (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
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
cheme validate                  # after every change
cheme check                     # engineering-step gates (--write only at sign-off)
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
cheme process propagate --fill  # the feeds (design specifications), the models, the recycles and their duties
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessels, vent (--svg)
cheme process reactor-hazards   # thermal screening of the glycolysis R101 (a conversion step at reflux)
cheme process crystallizers     # the quench, the crops, the filters and the dryer (its duties Q6, Q12)
cheme assess lca --write        # the preliminary LCI
```
