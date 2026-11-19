# Ethylene and propylene from methanol (MTO)

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A methanol-to-olefins (MTO) plant of the UOP/Hydro and DMTO type, 1800 kt/a of methanol from
methanol-1: the methanol is vaporised and converted at 475 C and 239 kPa(a) over a SAPO-34
catalyst in a fluidised bed, whose coked catalyst circulates to a fluidised-bed regenerator at
650 C where the coke burns off with air; catalyst coolers in both raise HP steam. The reactor is
a conversion step with the per-pass conversion (99.5 %) and the yield structure of a UOP
fluidised-bed example in an open patent (US 7 138 557 B2, Table 1) as selectivities
(`selectivity:`): 33.7 % of the methanol's carbon to ethylene, 44.7 % to propylene, the rest to
butenes, C5+, light paraffins, coke, CO and CO2. The product gas is quenched with water; the
unconverted methanol and the dimethyl ether are stripped from the reaction water and recycled,
which core converges at a tear stream (`tears:`). The gas is compressed in five stages to
2.07 MPa(a) with a caustic wash for its CO2, a three-phase discharge drum and molecular-sieve
dryers, and separated in a
front-end deethaniser, demethaniser, C2 splitter, depropaniser, C3 splitter and debutaniser
(`recovery:` on each, solved by `cheme process propagate`). The reactor's and the regenerator's
steam duties are core's conversion-step duties; the other duties come from an independent
shortcut script, `scripts/balance.py`. Needs cheme-as-code 1.12. DESIGN.md lists the core
features used and the core limits hit.

Headline numbers and their caveats:
- 225 t/h methanol give 33.3 t/h polymer-grade ethylene (99.97 mol%) and 43.7 t/h propylene
  (99.96 mol%), 2.92 kg of methanol per kg of the two (two commercial DMTO units report 2.85 and
  2.97 t/t), plus 10.1 t/h of a C4 olefin cut, 5.0 t/h of C5+ and 4.2 t/h of tail gas. The yields are one patent example's (D-005); the separations
  are ASSUMED recoveries, not rigorous columns (D-010).
- 2.44 t/h of coke burns to 8.93 t/h of fossil CO2 in the regenerator, 0.093 kg per kg of any
  hydrocarbon product with mass allocation (D-007, D-012).
- The utilities are gross upper estimates: no heat integration is counted (the feed is vaporised
  on 80 MW of MP steam, the quench rejects 144 MW to cooling water), the drives are electric
  (22.7 MW) and the 27 MW of HP steam raised is exported without a credit (D-011, D-012). The
  shortcut duties close the plant's energy balance within 1.7 MW of about 290 MW.
- The preliminary LCI links the methanol to methanol-1 and counts the steam as heat; every other
  background is a gap (D-012).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/simulation.yaml` | the heat mode of the adiabatic model step R100 (no simulation run) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts and `balance.py`: the regeneration air, the caustic, every duty but the reactor's and the regenerator's, two stream temperatures, the cross-checks behind the knock-out recoveries and the plant energy balance (D-011) |
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
cheme process propagate --fill  # the reactor, the recycle, the separators and the conversion duties
cheme run scripts/balance.py    # the air, the caustic and the shortcut duties (then propagate again)
cheme process reactors          # the conversion steps: extents, heats of reaction, duties
cheme assess lca --write        # the preliminary LCI
```
