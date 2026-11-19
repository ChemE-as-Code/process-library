# Polyvinyl chloride

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

Suspension PVC (S-PVC) from vinyl chloride monomer, the process the EU Polymers BREF (2007)
describes in its chapter 5, with the charge of US 6 825 288 B2, Example 1. Four 130 m3
autoclaves take the batches in turn. Each is charged with demineralised water and the
suspending agent, evacuated, and charged with VCM (fresh from vcm-1 and recovered) and a
peroxydicarbonate initiator. It is heated to 330.15 K on its jacket, and the VCM polymerises in
its droplets until the pressure drops at 90 % conversion (`reactor: batch`, core ADRs 0050,
0059). A short-stop is added and the unreacted VCM is vented to a gas holder. The slurry is
dropped to a buffer tank with the autoclave's rinse water. From there it is stripped
continuously with live steam to below 1 g of VCM per t of resin, cooled, dewatered in a decanter
centrifuge and dried in a fluid bed on LP steam (core's solid separation and dryer, ADR 0057).
The VCM of the venting and the stripper is compressed and condensed, and 99.8 % of it returns to
the charge: core converges that recycle at a tear stream (ADR 0060), and the venting, the
stripper and the recovery are component separators (ADR 0070).

`process/recipe.yaml` gives the cycle: 7.66 h per autoclave, a batch every 1.9145 h, 4179
batches a year of 41 794 kg, 175 kt/a. It also gives the autoclave's jacket check
(`cheme process recipe`). The heat-up's time and heat are worked by hand from the charge,
because core heats the end-of-batch content when nothing is dosed (D-003, L-6). `cheme process reactor-hazards` screens the closed batch. Needs
cheme-as-code 1.12.0. DESIGN.md lists the core features used and the core limits hit.

Headline numbers and their caveats:
- 0.997 kg of fresh VCM per kg of resin. 1.11 kg is charged; 0.11 kg is recovered and recycled,
  and 0.22 g goes to the vent incinerator (D-004, D-006).
- The rate is ASSUMED: zero order, calibrated so that the patent's charge reaches 90 % in 3.71 h
  at its mean heat removal (17 250 MJ/h). The heat of polymerisation is the patent's 1539.7
  kJ/kg (D-005).
- The jacket and the cooled baffles remove 3.89 MW, the duty the patent shows for them, against
  the model's 5.44 MW peak. The zero-order rate puts that peak at the start of the batch, where
  the patent's reflux condenser is not yet running, so the recipe's jacket check warns and the
  warning stays open: the rate's profile is front-loaded, while the patent's heat release rises
  through the batch (D-005, D-008). Later in the batch the reflux condenser takes 26 to 45 % of
  the heat. Core's closed batch has none, so all of the heat is booked to chilled water (L-3).
- Thermal screening: dT_ad 227.5 K and an MTSR of 557.7 K, against an MTT of 357.1 K. The MTT is
  the temperature at which the charge's vapour pressure reaches the ASSUMED relief set pressure
  of 1700 kPa(a). If the cooling fails at the start, the mass reaches the MTT in about 11.5 min.
  Short-stop injection, emergency cooling, agitation on emergency power and a controlled
  emergency vent to the recovery are therefore design requirements. There is no criticality
  class without a TD24 (D-010).
- Steam is 0.91 t/t of resin (the BREF's example plant uses 0.879 t/t) and thermal energy
  2.0 GJ/t (BREF 2 to 3 GJ/t). Electricity is 139 kWh/t without the chiller. Wastewater is
  1.28 t/t (BREF 1 to 4 m3/t). All three cross-checks are in D-008.
- The preliminary LCI links the VCM to vcm-1. The suspending agent, the initiator, the
  short-stop, the chilled water and the vent treatment are gaps, and so is the dryer's VCM to
  air, which has no biosphere flow identity yet: six gaps (D-011).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams and the polymerisation: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, the autoclave's unit procedure over four steps on four autoclaves, its vessel, jacket and the heat-up's time by hand (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
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
cheme process propagate --fill  # the batch, the separators, the VCM recycle, the centrifuge and dryer
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessel, jacket (--svg)
cheme process reactor-hazards   # thermal screening of the polymerisation
cheme process crystallizers     # the centrifuge and the dryer: cake, moisture, the dryer's duty
cheme assess lca --write        # the preliminary LCI
```
