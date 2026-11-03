# Styrene by dehydrogenation of ethylbenzene

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A concept-stage plant: 300 kt/a styrene monomer by adiabatic dehydrogenation of ethylbenzene
with superheated steam over iron oxide, in two radial beds with interstage reheat. The off-gas
fires the steam superheater; the crude styrene is fractionated under vacuum with ethylbenzene
recycle, benzene, toluene and tar as by-products. The PO/SM co-production route is not modelled.

## What is here

| path | what |
|---|---|
| `process/design-basis.yaml` | capacity, feeds, products, utilities, the assumptions with their LVOC BREF sections |
| `process/materials.yaml`, `process/reactions.yaml` | 12 components, dehydrogenation and burner reactions |
| `process/flowsheet.yaml` | blocks, steps and streams: the source of the generated `process/BFD.xml` and `process/PFD.xml` (`cheme process build`) |
| `process/simulation.yaml`, `process/simulation-run.json` | the DWSIM model and its recorded run |
| `scripts/sm_balance.py` | the independent heat and material balance the simulation is checked against |
| `equipment/equipment-list.yaml` | the 17 items the PFD links to |
| `lca/lca.yaml`, `lca/dataset.yaml` | goal and scope; the flowsheet-derived LCI (`cheme assess lca --write`) |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions with reasons, change log, stage definitions |

## How far it goes

- **Balanced and simulated, not validated.** Mass, component and element balances close
  (`cheme validate`); the script closes energy to 7 kW in 264 MW. DWSIM converges on the whole
  plant except the off-gas compression, but with Peng-Robinson as a recorded substitution that
  core has not qualified for aromatics with water and hydrogen (core#315). Reactor section,
  superheater and three columns agree with the script within about 3 %; the EB/styrene splitter
  needs 29 % more steam in DWSIM (DESIGN.md D-012).
- **Water/aromatics separation is specified, not predicted.** Water and the aromatics are taken as
  immiscible; the aromatics dissolved in the condensate come from their aqueous solubilities
  (PubChem). Peng-Robinson's flash cannot represent the split, so the separator, knock-out drum
  and decanter are specified splits in the DWSIM model (D-008, D-012).
- **Yields are assumed.** Conversion (0.40 per bed) and selectivities are chosen inside the LVOC
  BREF's ranges; there is no rate law, so the beds are not sized (D-005).
- **The LCI** is per kg styrene, cradle-to-gate with the foreground only; its backgrounds are
  linked by the library's LCI build (ethylbenzene to ethylbenzene-1, steam to
  utility-steam-ng-boiler). Mass allocation between styrene, benzene and toluene (D-013).

## The pilot it replaces

Until 2026-11-03 this was a manifest-only entry with a hand-written Tier 1 dataset of LVOC BREF
midpoints (chapter 5). Its facts are now the cross-check: ethylbenzene, by-products, steam and the
effluent of the flowsheet fall inside the BREF's ranges; the fuel (928 kWh/t, almost all off-gas)
is below the BREF's 1100-2900 kWh/t, and the superheater CO2 is 73 kg/t against the pilot's 292.
DESIGN.md D-014 has the comparison and why the Tier 1 dataset was removed (it stays in git
history).

## Not counted yet (TODO)

Off-gas aromatics recovery, heat recovery from the effluent, coke and its CO/CO2, gums, spent
solvents, fugitive, vacuum-vent and storage emissions, vacuum systems and fans (cut off), catalyst
ageing. The open inputs are listed in DESIGN.md.

## Working here

The tools come from [`cheme-as-code`](https://github.com/ChemE-as-Code/core) (the library CI pins
v1.4.1). Run `cheme skills update` once in this folder after cloning; then `cheme validate`,
`cheme process build`, `cheme process streams`, `cheme process simulate --check` (needs the
DWSIM container) and `cheme run scripts/sm_balance.py`. Data and designs are under CC BY 4.0
(`LICENSE-DATA`), scripts under AGPL-3.0-or-later.
