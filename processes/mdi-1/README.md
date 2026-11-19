# MDI

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for methylene diphenyl diisocyanate (MDI) by the route the EU LVOC BREF
(2017, Chapter 10) describes: aniline (aniline-1) is condensed with 50 wt% formalin
(formaldehyde-1) over hydrochloric acid in a seven-reactor cascade to the methylenedianiline
mixture (MDA, two-ring diamines and their oligomers), neutralised with caustic soda
(chlor-alkali-1), washed, and freed of the excess aniline, which is recycled; the brine is
stripped and goes to wastewater treatment. The MDA is phosgenated as a solution in
monochlorobenzene (MCB) with liquid phosgene from phosgene-1 dissolved in MCB, through a mixing
nozzle and a phosgenation tower; HCl and the excess phosgene are separated, the phosgene is
absorbed in chilled MCB and recycled, and the solvent is distilled off and recycled. The crude MDI
is split by vacuum distillation into monomeric MDI (overhead) and polymeric MDI (bottoms). Part of
the HCl is absorbed in water as the condensation's 30 % acid (the HCl recycle); the rest is
exported as gas. The ratios and conditions are the nameplate examples of two open Covestro
patents (US 10 640 455 B1 for the MDA, US 10 364 214 B1 for the phosgenation). TDI is left for
another entry.

Every flow and composition is calculated by `cheme process propagate`: conversion reactors,
component separators with ASSUMED recovery fractions, five recycles converged at tear streams
and seven design specifications that set the fresh feeds and the two splits from the sourced
ratios (core ADR 0060, ADR 0070). Needs cheme-as-code 1.12.0. DESIGN.md lists the core features
used and the core limits hit.

Headline numbers (design case, 8000 h/a) and their caveats:

- 22.2 t/h of crude MDI (178 kt/a): 4.44 t/h monomeric MDI and 17.75 t/h polymeric MDI, a 1:4
  split taken from the BREF's 2013 production ratio (D-008); 12.0 t/h of HCl gas exported.
- Per kg of crude MDI: 0.740 kg aniline, 0.784 kg phosgene (the BREF's example plant: 0.78),
  0.277 kg of 50 wt% formalin, 0.091 kg of 50 wt% caustic soda, 0.24 g of MCB make-up; 0.574 kg
  of brine (11 wt% NaCl) to treatment.
- The MDA and MDI mixtures are lumped as a two-ring and a three-ring component (D-004); the
  isomers, the by-products and the NCO content of the PMDI are not modelled.
- Every duty is an ASSUMED estimate with its arithmetic in the flowsheet (D-009): 0.98 kWh of
  steam heat per kg of crude MDI, well above the about 0.58 kWh of natural gas burnt on site per
  kg that the ACC 2022 study reports for US plants (phosgene, MDA and MDI together), because no
  heat integration is assumed and the phosgenation's heat release is not counted (no open heat
  of reaction, L-1).
- Phosgene is the dominant hazard: 36.3 t/h go to the phosgenation as a 35 % solution, 18.9
  t/h of it the absorber's recycle. The hazards and what a basic design must add are in D-011.

The LCI is preliminary (lca/lca.yaml): the aniline, formalin, caustic soda and phosgene link
their library producers; the MCB, power, cooling, refrigeration, water and waste treatments are
gaps. Monomeric MDI, polymeric MDI and HCl share the burdens by mass (D-012).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/reactions.yaml`, `process/flowsheet.yaml` | components, reactions, blocks, steps and streams: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/simulation.yaml` | the adiabatic neutraliser |
| `equipment/equipment-list.yaml` | the equipment of the PFD |
| `lca/` | the preliminary LCI (`lca/lca.yaml`, `lca/mappings.yaml`, outputs of `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions with the source register and core limits, change log, stage definitions |
| `.claude/skills/` | how an agent works here (not in git: run `cheme skills update` once after cloning) |

## Working here

```sh
uv tool install 'cheme-as-code[serve] @ git+https://github.com/ChemE-as-Code/core.git'   # once
cheme skills update             # once per clone: installs the agent skills in .claude/skills/
cheme validate                  # after every change
cheme process propagate --check # the balance, recycles and specifications
cheme process streams           # stream table with provenance, block balances
cheme process build             # BFD and PFD from process/*.yaml
cheme assess lca --check        # the LCI outputs are current
cheme check                     # engineering-step gates
```

Licences: data and designs under CC BY 4.0 (`LICENSE-DATA` of the library); skills and scripts
under AGPL-3.0-or-later.
