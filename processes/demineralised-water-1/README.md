# Demineralised water

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A site utility plant that makes 50 m3/h of demineralised water from fresh surface water. The
raw water is pumped through dual-media pressure filters, whose backwash takes 2.8 % of the
filtered water, and through cartridge filters to a high-pressure pump. A two-stage reverse
osmosis of brackish-water elements in a 2:1 array recovers 75 % of the water at 12.5 bar(a).
The feed pressure is estimated from the element's tested permeability. The permeate, about
9 mg/kg of dissolved solids, is polished in two mixed beds, one in service, to below 0.1 uS/cm.
Every 72 h a bed is regenerated in place with 5 wt-% hydrochloric acid (33 wt-% acid from
hydrogen-chloride-1) and 4 wt-% caustic soda (50 wt-% from chlor-alkali-1). The effluent is
neutralised with trim acid and joins the filter backwash and the RO concentrate in a sump that
drains to the site's biological wastewater treatment.

Core has no membrane or ion-exchange model, so the RO and the mixed beds are component
separators with specified splits (core ADR 0070). Core calculates every flow from the feeds,
solves the raw water for the product rate with a design specification, and writes the heat of
the neutralisation (a conversion step). The splits, regenerant doses, rinse water, feed pressure
and pump powers come from `scripts/balance.py`. Needs cheme-as-code 1.12.0. DESIGN.md lists the
core features used and the core limits hit.

Headline numbers and their caveats:
- Per m3 of product: 1.38 m3 of raw water, 0.063 kg of 33 wt-% hydrochloric acid, 0.046 kg of
  50 wt-% caustic soda, 0.98 kWh per m3 of electricity (0.56 of it the RO pump) and 0.38 m3 of
  wastewater with 0.72 kg of salts (D-005 to D-007).
- The dissolved solids are lumped as 500 mg/kg of NaCl. Hardness, alkalinity, silica and CO2
  are not carried, though they set the RO's scaling limit and the beds' anion load (L-2). The
  72 h run and the rinse volumes are ASSUMED (D-005).
- The design is at 25 degC. Colder water needs a higher RO feed pressure (D-004).
- All wastewater goes to biological treatment, which does not remove the salt. That is the
  LCI's conservative choice, since RO concentrate often goes to a sewer under a permit (D-006).
- The library links its `water` inputs to this plant's market by default (prefer_atlas). The
  shared vocabulary already read those inputs as deionised water (D-008).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams, specifications and the neutralisation: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts and `balance.py`: the RO's salt passage and feed pressure, the filters' backwash share, the mixed beds' regenerants and rinse water, the trim acid and the pump powers (D-003 to D-007) |
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
cheme run scripts/balance.py    # splits, regenerants, feed pressure, pump powers (then propagate again)
cheme process propagate --fill  # every flow from the feeds; the specs set the raw water and the regeneration water
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
cheme process reactors          # the neutralisation and its heat
cheme assess lca --write        # the preliminary LCI
```
