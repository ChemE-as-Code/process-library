# Biodiesel (FAME)

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for biodiesel (fatty acid methyl esters) by base-catalysed transesterification
of refined soybean oil, the route of the NREL report by Van Gerpen et al. (2004,
NREL/SR-510-36244): the oil reacts with methanol (6 mol per mol of oil) and sodium methoxide
(0.25 wt% of the oil, as its 25 wt% solution in methanol) in two stirred tanks in series at 333 K,
triglyceride + 3 CH3OH -> 3 methyl esters + glycerol, with the glycerol decanted after each
reactor. The esters are flashed at 50 kPa(a) to recover their methanol, washed once with warm
water acidified with hydrochloric acid and dried under vacuum. The glycerol phases are
neutralised with hydrochloric acid and stripped of methanol in a column at atmospheric
pressure, which leaves crude glycerol of about 87 wt%; the recovered, dry methanol is recycled.

Core solves the flowsheet with `cheme process propagate`: the oil feed for 32 420 t/a of
biodiesel and the fresh methanol for the 6:1 ratio are design specifications (`specs:`, core
ADR 0070), with the catalyst, wash water and acids following the oil; the methanol recycle is a
converged tear (`tears:`, ADR 0060); the reactors and neutralisations run on their conversions,
the decanters, flash, wash settler, dryer and glycerol column on specified recoveries (component
separators, ADR 0070), and the conversion steps' duties come from the heats of reaction and the
liquids' heat capacities (ADR 0059). Needs cheme-as-code 1.12.0. DESIGN.md lists the core
features used and the core limits hit.

Headline numbers and their caveats (per kg of biodiesel, unallocated):
- 1.005 kg of oil and 0.108 kg of methanol (0.101 fresh, 0.0075 in the catalyst solution), close
  to the stoichiometric 0.996 and 0.108 kg of the source's mass balance; 0.120 kg of crude
  glycerol (86.6 wt% glycerol). The conversions (90 % and 97 % of the rest, 99.7 % overall) are
  ASSUMED design values, not a kinetic result (D-005, L-2).
- The product has 0.03 wt% total glycerol (ASTM D6751: at most 0.24) and 0.02 wt% water; it rests
  on ASSUMED decanter, wash and dryer splits, as no liquid-liquid model for
  FAME-glycerol-methanol is qualified in core (D-006, D-007, L-1).
- 0.134 kWh of LP-steam heat, 0.120 kWh to cooling water and 0.017 kWh of power, without heat
  integration (D-009, L-6). The flash, dryer and column duties are hand estimates (D-009, L-4).
- 1.15 kg of wash water to treatment, one wash at the source's 1 gallon per gallon (D-007).
- The preliminary LCI allocates by mass (89.3 % to the biodiesel); the soybean oil and the
  sodium methoxide are gaps with recorded proxies, the methanol linked to methanol-1 and the
  acid to hydrogen-chloride-1 (D-011).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components (lumps with their liquid heat capacities), blocks, steps, streams, design specifications, the recycle tear and the reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists (equipment with first sizes; lines and instruments with the P&IDs) |
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
cheme process propagate --fill  # the feeds for the specs, the recycle, the reactors, separators and their duties
cheme assess lca --write        # the preliminary LCI
```
