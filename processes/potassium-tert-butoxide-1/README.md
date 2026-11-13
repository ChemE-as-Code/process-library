# Potassium tert-butoxide

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant for potassium tert-butoxide (KOtBu) from potassium metal and an excess of dry
tert-butanol, the classic route (Organic Syntheses, Coll. Vol. 4, 132 and Coll. Vol. 5, 1060;
Wikipedia): molten potassium is dosed into the alcohol at 348 K in R101, a semi-batch
(`reactor: semibatch`) whose hydrogen leaves by a vent as it forms (`batch.vent`), saturated with
the alcohol's vapour, through a vent condenser that returns the condensate (`vent.vapour`,
`vent.condenser`); the solution is stripped of most of the alcohol in the batch still ST101
(`still:` with the charge's heat-up and the vessel's metal) down to the 1:1 solvate, and the paste
is vacuum-dried at 433 K under nitrogen in the paddle dryer D101 (`dryer:`). The alcohol is
recycled, the loop converged at its tear (`tears:`). The make-up comes from `tert-butanol-1` as
the azeotrope with water and is dried past it in a molecular-sieve unit (a specified split from
`scripts/makeup_drying.py`: core has no adsorption model). `process/recipe.yaml` holds the batch
recipe the cycle (6.586 h, 1202 batches a year), the vessel sizes, the jacket check and the
flowsheet's year-average flows come from (`cheme process recipe`, `cheme process reactor-hazards`,
`cheme process stills`, `cheme process crystallizers`).

The thermal screening compares the cooling-failure temperature, 350.1 K at a 3.1 % accumulation of
the dispersed metal, with the alcohol's boiling point (355.45 K), and the hydrogen it releases
with the liquid's vapour (133.4 m3/h; 179.2 m3/h, 0.90 of it, at its largest early in the dosing)
with an ASSUMED vent capacity of 200 m3/h (no vent sized yet). The kinetics are ASSUMED: at a ten times slower rate the MTSR is 366.9 K, above the boiling
point, and the alcohol would boil with its hydrogen in a cooling failure (a design finding:
dosing interlocks on the agitator, the cooling and the hydrogen flow, and an emergency relief
sized from calorimetry are required, not yet designed; DESIGN.md D-011). Hydrogen and the
reaction of potassium with water are the plant's main hazards.
Needs cheme-as-code 1.10.0. DESIGN.md lists the core features used and the core limits hit.

Two headline numbers carry caveats. The modelled product is 99.47 wt% KOtBu (0.23 wt% KOH, 0.30
wt% tert-butanol), an upper bound on the assay: the metal's sodium, moisture picked up in handling
and any decomposition are not modelled, and no open product specification was read. The modelled
yield is 99.5 % on potassium and 89.5 % on the tert-butanol bought, on ASSUMED losses (the vent's
alcohol, the purge, the sieve's regeneration). The LCI's `product:KOTBU` is the feed
`di-tert-butyl-dicarbonate-1` links kg for kg (DESIGN.md D-014); potassium metal stays a gap.

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML; none yet) |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, reactions, blocks, steps and streams: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures and their operations (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `lca/` | goal and scope (`lca.yaml`), this process's mappings, and the preliminary LCI cheme writes |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | the make-up dehydration's balance script `makeup_drying.py` (library ADR 0027) and the generator example |
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
cheme run scripts/makeup_drying.py  # the sieve unit's split and duties (values cited in the flowsheet)
cheme process propagate --fill  # every other stream from the feeds (semi-batch, still, dryer, the recycle at its tear)
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessels, vent (--svg)
cheme process reactor-hazards   # thermal screening of the semi-batch, the gas release against the vent
cheme process stills            # the alcohol strip: path, boil-up time, duty
cheme process crystallizers     # the dryer: residual alcohol, steam
cheme assess lca --write        # the preliminary LCI
```
