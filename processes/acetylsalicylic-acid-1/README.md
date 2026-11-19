# Acetylsalicylic acid

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant for acetylsalicylic acid (aspirin) on the acetic-acid route of US 2 731 492 A and
US 2 987 539 A: salicylic acid and a sulfuric acid make-up are charged into the mother liquor
recycled from the last batch in the glass-lined R-101 and heated to 358 K; acetic anhydride
(from `acetic-anhydride-1`) is dosed over 1.5 h, C7H6O3 + (CH3CO)2O -> C9H8O4 + CH3COOH
(`reactor: semibatch`, core ADR 0050); the batch is cooled to 293 K and the aspirin crystallises
(core's crystallizer with the dissolved anhydride, salicylic acid and catalyst as spectators,
ADR 0056). The agitated filter-dryer F-101 filters it, reslurries the cake in recovered acetic
acid, filters again and dries it at 333 K under vacuum (ADR 0057). 60 % of the combined liquors
go back to the next charge, the rest with the dryer's condensate to the vacuum batch still C-301
(ADR 0055), whose acetic acid is the next wash and a co-product to the acetic anhydride plant;
its residue is incinerated. Core converges both recycles at tear streams (ADR 0060), the models
write their duties (ADRs 0059, 0063), `process/recipe.yaml` gives the cycle (11.57 h, the
filter-dryer the bottleneck), 684.8 batches a year of 1710.65 kg (1171 t/a), R-101's 5 m3 vessel
and its jacket check (`cheme process recipe`), and `cheme process reactor-hazards` screens the
dosing. Needs cheme-as-code 1.12.0. DESIGN.md lists the sources, the decisions, the core
features used and the core limits hit.

Headline numbers and their caveats:
- Yield 94.8 % of theory on the salicylic acid, product 99.85 wt% aspirin: model results on a
  solubility derived from US 2 731 492 A, Example I (0.0998 kg per kg of liquor at 293 K); the
  loss is the aspirin the still residue carries (5.0 %). US 2 987 539 A reports 88 % of
  tablet-grade aspirin (93 % with its salicylic acid recovery, not modelled here) (D-007, D-009).
- Per kg of aspirin: 0.807 kg salicylic acid, 0.627 kg acetic anhydride, 0.88 g sulfuric acid;
  0.351 kg recovered acetic acid (94.1 wt%, the rest anhydride) and 0.084 kg still residue.
- The heat of reaction, -29.0 kJ/mol, is Hess's law on NIST WebBook data; the kinetics are
  ASSUMED (no open kinetics or calorimetry). Screening: dT_ad 46.6 K, at most 19.5 % of the
  anhydride accumulated, MTSR 365.5 K against the MTT of 391.2 K (acetic acid's boiling point).
  With a 100 times slower reaction, as without the catalyst, the MTSR is 400.6 K, above the MTT: a
  design finding (the dosing interlocked with the catalyst charge and the heat flow), and the
  reason the anhydride is dosed rather than charged (an all-in batch reaches about 404.8 K)
  (D-005, D-011).
- Filtration, wash and drying data are ASSUMED (no open cake data); the drying is the bottleneck.
- The preliminary LCI links acetic anhydride, sulfuric acid and nitrogen to library producers;
  salicylic acid (Kolbe-Schmitt) is a gap with a recorded proxy. Economic allocation at ASSUMED
  relative prices gives the aspirin 96.6 % of the burdens (D-012).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components (with the still's Antoine lines), blocks, steps, streams and the reaction: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures over several steps, R-101's vessel and jacket, the filter-dryer's and the still's times (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts (none needed: core's models give every balance value) |
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
cheme process propagate --fill  # the semi-batch, the crystallizers, filters, dryer, still and the recycles
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessels, jacket (--svg)
cheme process reactor-hazards   # thermal screening of the dosing
cheme process crystallizers     # crystallisation, wash, filters and the dryer's duty
cheme process stills            # the vacuum still: distillate, residue, boil-up time, duty
cheme assess lca --write        # the preliminary LCI
```
