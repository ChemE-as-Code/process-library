# Iodomethane

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant for iodomethane (methyl iodide) from methanol, red phosphorus and iodine (CN
114195616 B, Examples 1-3). The reactor R101 is a semi-batch (`reactor: semibatch`): iodine is
dosed over 10 h into a slurry of red phosphorus in methanol at 313 K, the end mass's measured
temperature at total reflux, given as `hazard.mtt`. The red phosphorus is a solid reactant in the liquid
model. The iodomethane that the vents carry past the brine condenser leaves by a vent stream
(`batch.vent`, core ADR 0054) to an activated-carbon adsorber. The crude is distilled off the
phosphorous acid residue in the same vessel by a batch still, ST101 (`still:`, core ADR 0055, a
constant relative volatility), washed with sodium thiosulfate solution and water, and dried. Then
it is distilled in C-104 with its column K-104, ST102: core's batch rectification (`still.column`,
core ADR 0061, Diwekar's shortcut, 5 theoretical stages at a reflux ratio of 2, ASSUMED) on
Raoult's law, the charge heated to its bubble point in the model (`still.heat_up`, ADR 0063). The
washes and the drying are specified splits in `scripts/balance.py`. `process/recipe.yaml` holds
the batch recipe that gives the cycle time, R-101's vessel, jacket check and warming time, the
stills' boil-up times and the flowsheet's year-average flows (`cheme process recipe`, `cheme
process reactor-hazards`, `cheme process stills`). The semi-batch's and the stills' models write
their duties Q2, Q3, Q8 and the column's condenser Q10 (`energy_port`, `still.condenser_port`,
core ADRs 0059, 0061), and the screening gives the MTSR over
the batch and compares the gas released at a cooling failure with R-101's vent capacity of 20
m3/h (`hazard.vent_capacity`, core ADR 0058). Needs cheme-as-code 1.10.0. DESIGN.md lists the core
features used and the core limits hit.

Four headline numbers carry caveats:
- The yield, 95.01 % of theory on the iodine, is a model result inside the patent's 95-96 % (no
  basis stated). It is an ASSUMED upper bound: the losses not modelled only lower it, the
  residue's share rests on an assumed relative volatility and the final still's on its assumed
  end (D-007, D-013, D-016).
- The product's 99.86 wt% is core's batch rectification on an ideal liquid at 5 assumed stages
  and a reflux ratio of 2. A rigorous column on the same liquid would give at least this (core
  ADR 0061); the real liquid (an azeotrope of iodomethane with methanol, not sourced) may give
  less. It lies above the patent's measured 99.5-99.7 %, so it is a finding, not a design claim:
  the specification stays the patent's. One still stage would give 99.40 wt% (D-010, D-016).
- The accumulation, 2.28 %, follows from an ASSUMED rate law. The reactor runs at its boiling
  point, so a cooling failure takes it above the MTT (MTSR 322.6 K against 313.15 K). The reflux
  condenser takes the boil-off, 26 to 53 kW (D-006). A loss of agitation during the dose would
  accumulate undissolved iodine, which the 2.28 % does not cover (D-006 (g)).
- The by-product is phosphorous acid, not the phosphoric acid the patent writes (D-004).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components (with the stills' Antoine constants), blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures over several steps, R-101's vessel and jacket, the stills' distil times (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts and `balance.py`: the feeds for 500 t/a, the washes' and the drying's splits, the vent fraction, the mixed temperatures, the duties core's models do not write and the powers (D-008 to D-012) |
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
cheme process propagate --fill  # the semi-batch, the stills (with their duties Q2, Q3, Q8, Q10), the thiosulfate step and the mixers from the feeds
cheme run scripts/balance.py    # the feeds, the washes' splits, the vent fraction and the other duties (then propagate again)
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessel, jacket, vent (--svg)
cheme process reactor-hazards   # thermal screening of the semi-batch
cheme process stills            # the batch stills: distillate, residue, boil-up time
cheme assess lca --write        # the preliminary LCI
```
