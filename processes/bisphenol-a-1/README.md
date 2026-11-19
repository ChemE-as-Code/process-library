# Bisphenol A

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for bisphenol A (BPA, 4,4'-isopropylidenediphenol), the monomer of
polycarbonate and epoxy resins, by the route the GE, Dow, Mitsubishi and Mitsui patents describe:
phenol and acetone at 10 mol/mol (with the recycled mother liquor) pass three fixed beds of a
sulfonated polystyrene-divinylbenzene resin promoted with 2-mercaptoethylamine, 333 K in and
353 K out; 69 % of the acetone reacts per pass, 94.9 % of it to p,p-BPA
(2 C6H6O + C3H6O -> C15H16O2 + H2O), the rest to the o,p-isomer and heavier by-products. The
effluent goes without a distillation to a vacuum crystallizer at 318 K and 5 kPa(a), where dosed
water, the unreacted acetone and some phenol evaporate and carry off the heat; the 1:1 adduct of
BPA with phenol crystallises, is filtered, washed with polished phenol, melted and stripped of
phenol under vacuum. The mother liquor is isomerised over resin and recycled, 5 % of it purged
to a still that recovers its phenol. Phenol and acetone come from the library's cumene-phenol
plant `acetone-1`. Needs cheme-as-code 1.13.0. DESIGN.md lists the core features used and the
core limits hit.

Headline numbers and their caveats:
- 8750 kg/h of 99.96 wt% BPA melt (70 kt/a in 8000 h): 0.863 kg phenol and 0.264 kg acetone
  per kg (95.5 % and 96.3 % of the stoichiometric amounts). The losses are the still's residue,
  in which the cracking back to phenol is not modelled (conservative), and the wastewater.
- The selectivities and the 69 % acetone conversion are a laboratory example (US 4 391 997 A)
  transferred to the plant's recycled feed, the crystallizer's yield of 75 % is ASSUMED (no open
  solubility of the adduct read), and the product's purity counts only the liquor left in the
  washed cake, not impurities taken into the crystals: an upper bound (D-005, D-007, D-009).
- The beds run almost adiabatic: core's conversion-step model shows the reaction heat itself
  gives the 20 K ascending profile, the interstage coolers take 32 kW (D-005). The crystallizer's
  1.53 MW (core's crystallizer energy balance) are matched by hand to the latent heat of what
  evaporates, which sets the 1300 kg/h water dose (D-007).
- The recycle is solved by core at two tears with three design specifications (the capacity, the
  reactor's phenol ratio and the adduct's 0.6 kg/kg phenol wash) (D-010).
- Per kg of BPA: 0.129 kWh LP and 0.385 kWh HP steam, 0.038 kWh electricity (ASSUMED
  allowances), 0.464 kWh to cooling water, 0.149 kg demineralised water, 0.232 kg phenolic
  wastewater and 0.044 kg of residue to incineration. The column and still duties are hand
  calculations: no property package of core covers BPA or the adduct (D-011, L-3).
- Phenol is toxic and corrosive and is handled molten; BPA dust is explosible (EU risk
  assessment: 0.012 g/l); the condensation is mildly exothermic (screening: dT_ad 31.6 K):
  noted for basic engineering and the HAZOP (D-013).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml`, `process/simulation.yaml` | components with their liquid heat capacities, blocks, steps, streams, tears and design specifications, reactions and the isomeriser's adiabatic mode: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts (none used yet) |
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
cheme process propagate --fill  # the recycle, the specs, the reactors, crystallizer and filter
cheme process crystallizers     # the crystallizer's and the filter's balances and duty
cheme process reactor-hazards   # thermal screening of the reactors
cheme assess lca --write        # the preliminary LCI
```
