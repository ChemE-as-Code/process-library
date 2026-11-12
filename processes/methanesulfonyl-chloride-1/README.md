# Methanesulfonyl chloride

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant for methanesulfonyl chloride (mesyl chloride, CH3SO2Cl) from methanesulfonic acid
and thionyl chloride, after the procedure of Organic Syntheses (Coll. Vol. 4, p. 571): thionyl
chloride is dosed over 4 h into the acid at 368 K, CH3SO3H + SOCl2 -> CH3SO2Cl + SO2 + HCl, and
both gases leave as they form. The reactor R101 is a semi-batch (`reactor: semibatch`) whose SO2
and HCl leave by a vent (`batch.vent`) saturated with the liquid's thionyl chloride and product
vapour (`vent.vapour`), through a brine vent condenser that returns the condensate
(`vent.condenser`, core ADR 0062) to a caustic scrubber. The crude is distilled at 4 kPa(a) in a
batch still with an 8-stage column (`still.column`, core ADR 0061): first the excess thionyl
chloride as a forerun, nine tenths of it recycled to the next dose (a recycle torn at S3 and
converged by core, ADR 0060), then the product, so that the pot and the heated wall stay below
the 115 C the source sets for the product. `process/recipe.yaml` gives the cycle (9.53 h, R-101
the bottleneck), 831 batches a year of 1203 kg for 1000 t/a on a dedicated train, R-101's vessel
(1.6 m3) and the still's boil-up times; the models write their duties (core ADR 0059); the
screening (`cheme process reactor-hazards`) compares the gas release with R-101's vent capacity
of 400 m3/h. DESIGN.md lists the core features used and the core limits hit.

What to know before using a number:
- The reaction's kinetics and heat are ASSUMED: no open calorimetry exists. The rate is sized to
  the source's hold time; the heat, +65 kJ/mol, is endothermic by analogy with two computed
  acid-to-acid-chloride conversions (D-005). With an endothermic reaction a cooling failure does
  nothing; the hazard is the gas: a dose accumulated while the heating has failed releases about
  1280 m3/h when it reacts, 3.2 times the vent, and R-101's jacket alone cannot supply the heat
  the dosing needs (about 80 kW at the peak against at most 21 kW), so an external heating loop
  E-105 is part of the design. These are design findings for basic engineering (D-009, D-014).
- The yield, 97.2 % of theory on the acid, is a model result and an upper bound; the only open
  example, 1.5 mol in the laboratory, reports 71-83 % (D-006).
- The product, 99.95 wt% with 530 ppm thionyl chloride, is an upper bound of a shortcut column
  on an ideal liquid, with no measured VLE behind it (D-007).
- The LCI is preliminary and gate-to-gate: methanesulfonic acid has no library producer and
  stays a gap with a recorded proxy; thionyl chloride, caustic soda and nitrogen are linked to
  thionyl-chloride-1, chlor-alkali-1 and asu-1 (D-012).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components (with the still's vapour-pressure lines), blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures, R-101's vessel and jacket, the still's boil-up times (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts and `balance.py`: the feeds for 1000 t/a with the recycle, the scrubber's caustic, the still's stream temperatures and the duties core's models do not write (D-006) |
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
cheme process propagate --fill  # the semi-batch with its vent, the stills with the column, the recycle tear, the scrubber (with their duties)
cheme run scripts/balance.py    # the feeds for 1000 t/a, the caustic and the other duties (then propagate again)
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessel, jacket, vent (--svg)
cheme process reactor-hazards   # thermal and gas-release screening of the semi-batch
cheme process stills            # the still and its column: forerun, product, residue, boil-up times, duties
cheme assess lca --write        # the preliminary LCI
```
