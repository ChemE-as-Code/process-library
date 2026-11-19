# General-purpose polystyrene

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: engineering lists as YAML, decisions and progress as
Markdown, the BFD and PFD generated from the flowsheet. Edited by people and by coding agents
(Claude Code), checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A concept-stage plant for 100 kt/a of general-purpose (crystal) polystyrene by continuous bulk
polymerisation of styrene, the process the EU Polymers BREF (2007) describes for GPPS: styrene
from `processes/styrene-1`, mixed with the recovered monomer to a feed with 7 wt% ethylbenzene,
is polymerised by heat in a stirred prepolymeriser R-101 at 403 K that boils under 50 kPa(a)
(its vapour condensed in a reflux condenser and returned) and in three liquid-full stirred tower
reactors R-102 up to 443 K, to 75 % conversion. The solution is heated to 513 K on hot oil and
devolatilised at 4 and 1 kPa(a); the vapours are condensed and recycled, 1.37 % purged to the
thermal oxidiser; the melt is pelletised under water, dried and conveyed to the silos.

cheme-as-code solves the flowsheet: two design specifications (100 kt/a of polymer, 7 wt%
ethylbenzene in the reactor feed) set the fresh styrene and the purge fraction together with the
recycle's tear stream (core ADRs 0060, 0070), and the two conversion reactors write their own
duties (ADR 0059). The devolatilisers, the condenser and the pelletiser are specified splits whose
heats come from `scripts/ps_balance.py`, which also re-solves the mass balance independently.
Needs cheme-as-code 1.12.0. DESIGN.md lists the core features used and the core limits hit.

Headline numbers and their caveats:
- 1.006 kg of styrene per kg of polystyrene, inside the BREF's 0.985 to 1.020 t/t; the purge
  (5.9 g/kg) and the residual monomer (about 520 ppm) are the losses (D-004, D-007).
- The conversions (0.35 and 0.615 per pass) and the devolatilisers' recoveries are ASSUMED
  inside the BREF's ranges: core has no polymerisation kinetics and no polymer-solvent phase
  equilibrium, so the reactors are sized on assumed residence times (D-005, D-007, L-1, L-3).
- Heat: 1.42 MW of polymerisation heat and agitation to cooling water from the reactors, 1.04 MW
  from hot oil to the devolatilisers, 1.11 MW from the vapour condenser, 0.94 MW from the
  pelletiser's water; electricity 660 kW (ASSUMED). Energy 0.49 GJ/t, below the BREF's
  1.08 to 1.80 GJ/t, which counts more than the line's motors and heater (D-012).
- Runaway (hand screening, D-010): if the cooling failed and the remaining styrene polymerised,
  the prepolymeriser's content would rise about 246 K and the towers' outlet about 95 K. The
  prepolymeriser is tempered by its boiling, the liquid-full towers are not: their relief and
  interlocks are design findings for basic engineering.
- The LCI is gate to gate and preliminary: the styrene is linked to styrene-1, the hot oil's heat
  to heat from natural gas, the nitrogen to asu-1; the purge's and vent's oxidation and the
  process water are gaps (D-011).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site, assumptions |
| `process/materials.yaml`, `process/reactions.yaml`, `process/flowsheet.yaml` | components (polystyrene per repeat unit), the polymerisation, blocks, steps, streams, the tear and the design specifications: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `scripts/ps_balance.py` | the independent mass balance, the reactor feed's temperature and the heats of E-101, E-103 and the pelletiser (D-006, D-008, D-009) |
| `equipment/equipment-list.yaml` | the items the PFD links to, with ASSUMED sizes |
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
cheme process propagate --fill  # the specs, the recycle, the reactors and their duties
cheme run scripts/ps_balance.py # the independent balance and the heats core's separators do not give
cheme assess lca --write        # the preliminary LCI
```
