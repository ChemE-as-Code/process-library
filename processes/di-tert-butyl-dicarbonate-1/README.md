# Di-tert-butyl dicarbonate

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant for di-tert-butyl dicarbonate (Boc2O, Boc anhydride) by the one-pot phosgene route
of EP 0 256 559 A2: potassium tert-butoxide suspended in recovered hexane with DABCO takes up CO2
and then phosgene gas in one semi-batch at 278 K (`reactor: semibatch` with two gas doses,
`dosing.absorbed`, and a vent for the CO2 and isobutene, `batch.vent`); the slurry is degassed
and the hexane stripped and recycled in core's batch stills; the Boc2O melt is washed free of KCl
with warm water and distilled at 0.13 kPa(a) from a liquid-paraffin heel (a still with a forerun
and a main cut). Both recycles, the hexane and the heel, are tear streams that `cheme process
propagate` converges; the semi-batch's and the stills' duties come from their models
(`energy_port`). `process/recipe.yaml` holds the batch recipe the cycle time (10.41 h, R-101 the
bottleneck), R-101's size and jacket check, the vent's load per batch and the flowsheet's
year-average flows come from (`cheme process recipe`, `cheme process reactor-hazards`, `cheme
process stills`). What core cannot calculate, the wash's phase split, the scrubbed vent's split
and the heats the models leave out, is in `scripts/balance.py` under the library's
balance-output contract. Needs cheme-as-code 1.9.0. DESIGN.md lists the core features used and the
core limits hit.

Three headline numbers carry caveats. The modelled yield is 89.4 % on the alkoxide, below the
91.0 % the patent's Example 1 gives by mass (its purity not stated), which bounds it from above.
The modelled product is 99.98 wt% Boc2O, an upper bound: di-tert-butyl carbonate, the tricarbonate
and the other by-products are not modelled. The thermal screening is on ASSUMED rate laws: the
MTSR (279.9 K) lies far below the decomposition limit (333.15 K); the risk is the dissolved
phosgene, which a cooling failure strips into the CO2 it releases (0.11 kg/h at the design rate).
At a hundred times slower rates 36.6 % of the phosgene accumulates, the CO2 a cooling failure
releases exceeds the vent's 50 m3/h and carries about 7 kg/h of phosgene to the scrubber (a
design finding, DESIGN.md D-011, D-014).

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
| `scripts/` | `balance.py` (the wash and vent splits and the duties core leaves out, `cheme run scripts/balance.py`), generator scripts |
| `.claude/skills/` | how an agent works here (not in git: run `cheme skills update` once after cloning) |

## How this repository works

- **This repository holds your plant**: drawings, lists, decisions. It does not hold the tools.
- **The tools come from [`cheme-as-code`](https://github.com/ChemE-as-Code/core)**, installed once on
  your computer (`uv tool install git+https://github.com/ChemE-as-Code/core.git`). Every check,
  drawing and generated file is made by the `cheme` command, so you need it to work here.
- **Licences.** This folder is part of the ChemE-as-Code process library. Its data and designs are
  under CC BY 4.0 (`LICENSE-DATA`, unless `process.yaml` states otherwise); its skills and scripts
  are under AGPL-3.0-or-later (`LICENSE`), like the ChemE-as-Code tools. Its publication status is
  in `process.yaml` (internal until a maintainer decides otherwise).
