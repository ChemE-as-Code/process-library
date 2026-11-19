# Polyamide 66

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant for polyamide 66 (nylon 6,6) by melt polycondensation of AH (nylon) salt in an
autoclave, the cycle the EU POL BREF (2006, section 9.2.2.3) describes. Adipic acid
(`adipic-acid-1`) is slurried in water and molten hexamethylenediamine is dosed into it at 338 K
(R-101, `reactor: semibatch`, core ADR 0050): the neutralisation gives a 52 wt% AH salt solution
with a 0.52 % excess of the diamine, which makes up what the steam strips later. The autoclave
R-201 then evaporates water to 70 wt% salt at about 383 K, heats the mass on hot oil to 548 K
while the salt polycondenses (AHSALT -> repeat unit + 2 H2O) and the steam is bled off at a
constant 1750 kPa(a), lets the pressure down and finishes the melt; the melt is pressed out as
strands, quenched in water and cut to pellets. The vapours are condensed and go with the
stripped diamine to biological wastewater treatment. One design specification sizes the acid
for 8000 t/a, the water and the diamine following it (core ADR 0070). `process/recipe.yaml`
gives the cycle (5.25 h, the autoclave the bottleneck), 1508.6 batches a year of 5303.03 kg and
the dissolver; `cheme process reactor-hazards` screens the neutraliser and the autoclave. Needs
cheme-as-code 1.13.0. DESIGN.md lists the core features used and the core limits hit.

Headline numbers and their caveats:
- Per kg of pellets: 0.644 kg of adipic acid, 0.515 kg of hexamethylenediamine (together 1.159
  kg, about 0.6 % below the BREF's 1.165 to 1.167 t of salt per t, which carries the plants'
  yield losses), 1.064 kg of water, all evaporated again; 1.223 kg of condensate with 2.69 g of
  diamine (from the BREF's COD before treatment, D-010).
- Heat 0.804 kWh/kg from hot oil (2.90 MJ/kg) and 0.058 kWh/kg of LP steam, power 0.059 kWh/kg:
  about 3.3 MJ/kg delivered, inside the BREF's batch PA66 range of 3.3 to 7.7 GJ/t (Table 9.8).
  The evaporation of the solution water (about 1 kg per kg) dominates the heat.
- The autoclave's phase times, its steam-bleed pressure, the conversion (0.995 of the amide
  links, Mn about 22 600 g/mol) and the melt's 0.2 wt% residual water are ASSUMED: the BREF
  names the phases and the final 275 C but gives no times, pressure or molar mass (D-003,
  D-006).
- The neutralisation's heat and rate are ASSUMED (no open calorimetry): MTSR 338.6 K against an
  MTT of 373.15 K. The polycondensation's heat is Steppan's apparent amidation enthalpy (Nisoli
  et al. 2004). The autoclave runs at its boiling point by design; its hazard is the pressure
  (relief an open input, D-011).
- Core has no step-growth model that removes the water while the salt polycondenses (core limit
  L-1): the autoclave is a specified concentration, a conversion step and a specified steam
  bleed, whose evaporation heats come from `scripts/balance.py`.

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures over several steps, the dissolver's vessel (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | `balance.py`: the warming, the evaporation heats, the condenser's and the strand quench's duties, which no core model gives (library ADR 0027) |
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
cheme process propagate --fill  # the feeds (design specification), the models and their duties
cheme run scripts/balance.py    # the duties core does not write (Q2, Q3, Q5 to Q7)
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessels
cheme process reactor-hazards   # thermal screening of the neutraliser and the autoclave
cheme assess lca --write        # the preliminary LCI
```
