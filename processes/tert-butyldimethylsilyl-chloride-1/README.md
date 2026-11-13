# tert-Butyldimethylsilyl chloride (TBSCl)

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant for tert-butyldimethylsilyl chloride (TBSCl), the silylating agent of the TBS
protecting group, by the Grignard route of US 5 068 386 A (Example 3: sodium thiocyanate as the
catalyst, 78 % isolated). tert-Butyl chloride is dosed into magnesium turnings in recycled
THF/n-hexane at 313 K in R101, a semi-batch (`reactor: semibatch`) with an initiation charge and
hold (`dosing.profile`), whose isobutene and isobutane leave by a vent as they form
(`batch.vent`), saturated with the liquid's vapour, through a brine vent condenser that returns
the condensate (`vent.vapour`, `vent.condenser`). The Grignard solution is dosed into
dichlorodimethylsilane with the catalyst in R102, a second semi-batch (the order of addition of
US 5 872 274 A, so that the silane the recycle brings is not set off at once). The magnesium
chloride is filtered, washed and vacuum-dried in a filter-dryer (`solid_separation` with Ruth's
filtration time, `dryer:`); the filtrates are rectified in the batch still ST101 with a 10-stage
column (`still.column`), the solvent with the excess silane recycled (`tears:`) and the TBSCl cut
condensed above its melting point and flaked. `process/recipe.yaml` holds the batch recipe the
cycle (9.86 h, 803.3 batches a year), the vessel sizes, the jacket checks and the flowsheet's
year-average flows come from (`cheme process recipe`, `cheme process reactor-hazards`,
`cheme process stills`, `cheme process crystallizers`).

The thermal screening compares the cooling-failure temperature with the boiling point of the
most volatile component, tert-butyl chloride, 324.1 K: 317.7 K in the Grignard step at a 2.2 %
accumulation of the halide, 309.3 K in the silylation. The kinetics are ASSUMED (the HZDR's
calorimetry of an aryl bromide's Grignard formation in THF as the analogue): ten times slower,
the Grignard step reaches 345 K and boils, and its C4 gases exceed the ASSUMED 100 m3/h vent; a
hundred times slower (a sluggish initiation), 441 K (a design finding: dosing interlocks on the
initiation and the cooling and emergency reliefs sized from calorimetry are required, not yet
designed; DESIGN.md D-011). Water reaching the chlorosilanes (a brine leak) would release HCl.
Needs cheme-as-code 1.11.0. DESIGN.md lists the core features used and the core limits hit.

Two headline numbers carry caveats. The modelled product is 99.58 wt% TBSCl (0.14 wt% THF, 0.20
wt% n-hexane, 0.09 wt% dichlorodimethylsilane), an upper bound on the assay: the siloxane from
moisture, other by-products and the catalyst's residues are not modelled, and no open product
specification was read. The modelled yield is 74.6 % on tert-butyl chloride, below the patent's
78 %, on an ASSUMED share of the side reaction to isobutene and isobutane. THF is linked to
thf-1 and nitrogen to asu-1 in the LCI; magnesium, tert-butyl chloride, dichlorodimethylsilane,
n-hexane and sodium thiocyanate stay gaps with their proxies named (DESIGN.md D-012).

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
| `scripts/` | the generator example |
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
cheme process propagate --fill  # every stream from the feeds (semi-batches, filters, dryer, still, the recycle at its tear)
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessels, jackets, vent (--svg)
cheme process reactor-hazards   # thermal screening of both semi-batches, the gas release against the vent
cheme process stills            # the rectification: cuts, boil-up time, reboiler and condenser duties
cheme process crystallizers     # the filters and the dryer: cake, residual solvent, heat
cheme assess lca --write        # the preliminary LCI
```
