# Caprolactam

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for caprolactam, the monomer of polyamide 6, by the conventional route
(DESIGN.md D-001): cyclohexanone is oximated counter-currently at 363 K with the hydroxylammonium
sulfate solution of the library's `hydroxylamine-1` (its whole output), ammonia neutralising the
acid: (NH3OH)2SO4 + 2 C6H10O + 2 NH3 -> 2 C6H11NO + (NH4)2SO4 + 2 H2O. The oxime melt is
rearranged in oleum (32 wt% SO3, 1.17 kg per kg) in a circulating loop at 388 K, the Beckmann
rearrangement giving caprolactam at an ASSUMED 98.9 % yield (transferred from a staged DSM
experiment). The acid mixture and liquid ammonia go into a
circulating ammonium sulfate solution: the crude lactam separates, is extracted with benzene,
back-extracted into water, evaporated and distilled under vacuum. The neutraliser's solution, the
oximation liquor and the raffinate give ammonium sulfate crystals, whose condensate dilutes the
neutraliser. The route was chosen against DSM's HPO process and the gas-phase Beckmann
rearrangement on a zeolite (D-001).

The three reactors are cheme-as-code conversion steps whose duties core computes from formation
enthalpies (ADR 0059); the separators are specified splits; the benzene, back-extraction water
and condensate recycles converge at tear streams (ADR 0060), with the feeds and the condensate
split set by design specifications (ADR 0070); a balance script closes the energy balance of
every other step. Needs cheme-as-code 1.12.0.
DESIGN.md lists the sources (SRC-1 to SRC-14), the core features used and the core limits hit.

Headline numbers and their caveats (per kg of caprolactam, 100.1 kt/a at 8000 h/a):
- Feeds: 0.897 kg cyclohexanone, 2.931 kg hydroxylammonium sulfate solution (0.300 kg NH2OH),
  0.640 kg ammonia, 1.267 kg oleum, 1.8 g benzene make-up.
- Co-product: 2.478 kg ammonium sulfate crystals. 1.82 kg/kg is formed from the rearrangement's
  acid, inside the 1.7 to 1.9 an open patent states; the rest comes from the oximation.
- Heat: 5.8 and 12.0 MW released in the rearrangement and the neutraliser, calculated without the
  heats of solution in oleum and water (their split is not reliable, their sum is). The
  oximation's 3.5 MW is only an upper bound: no formation enthalpy of hydroxylammonium sulfate
  was found, and the heat left out could take it to about zero. The evaporators, the dryer and
  the column take 1.84 kWh of steam and the plant rejects 3.79 kWh to cooling water; three
  effects, the recoveries, the dryer and all power are ASSUMED.
- The LCI is preliminary: economic allocation at an ASSUMED relative price (85.2 % to the
  caprolactam); cyclohexanone and oleum have no library producer and are gaps.
- Hazards for the next stage (not assessed here): oleum and SO3, the strongly exothermic
  rearrangement at loss of cooling or circulation, ammonia, and benzene as the extraction
  solvent (DESIGN.md O-8).

| path | what |
|---|---|
| `process.yaml` | the Atlas manifest: title, chemistry, maturity, review status, references |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, assumptions |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components (molecular salts, liquid heat capacities), blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml` | equipment list (concept, no P&ID yet) |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates |
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
cheme process propagate --fill  # the reactors, separators, recycles and the reactors' duties from the feeds
cheme assess lca --write        # the preliminary LCI
```
