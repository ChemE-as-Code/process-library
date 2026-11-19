# Sodium chlorate

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for sodium chlorate crystal, 50 000 t/a, by electrolysis of salt brine in
undivided cells, as the EU LVIC-S BREF (2007, section 7.13) and US 5 419 818 A describe it. Solid
salt is dissolved in the recycled mother liquor and the crystallizer's condensate and joins the
circulating electrolyte (about 121 g/L NaCl and 565 g/L NaClO3). 400 cells with titanium anodes
and steel cathodes, with sodium dichromate in the liquor, run at 70 C, 2.5 kA/m2 and 3.0 V. The
chlorine formed at the anode hydrolyses at once to hypochlorous acid and hypochlorite, which
disproportionate to chlorate in the reaction tanks; hydrogen forms at the cathode. Overall
NaCl + 3 H2O -> NaClO3 + 3 H2. A side stream is crystallised under vacuum, heated with the cells'
own heat, centrifuged and dried in a fluidised bed; 69 % of the hydrogen goes to users.

How core models it:

- `process/cells.yaml` and `cheme process cell` (core ADR 0023): the cells' Faraday, charge and
  energy balance from the current efficiency 0.95 (BREF), the voltage and the oxygen side
  reaction. 4771 DC kWh per t of chlorate formed, 14.6 MW of heat (48 % of the power, the BREF
  says about half), 59.5 kg of hydrogen per t (the BREF: 60), 2.2 mol% oxygen in it (the BREF:
  2-2.5 %).
- `cheme process propagate` solves the whole loop: the cells and the reaction tanks as conversion
  reactors whose extents equal the cell's, a component separator for the cell gas, core's
  crystallizer (one solute with NaCl and the active chlorine as spectators, evaporation,
  centrifuge, energy balance) and dryer, the recycle torn at the cell feed and two design
  specifications: the salt for 6250 kg/h of crystal and the water for 565 g/L of chlorate in the
  cell feed (core ADRs 0025, 0056, 0057, 0060, 0070).
- The reaction tanks (about 650 m3) are sized by hand from the open third-order rate constant of
  Spasojevic et al. (2018) at pH 6.4 (DESIGN.md D-007).

Headline numbers and their caveats:

- Salt 0.550 kg, water 0.545 kg and electricity 5.20 kWh per kg of product, each inside or at the
  edge of the BREF's ranges (benchmarks/inorganic-chemicals.yaml).
- The crystallizer's yield is ASSUMED: no open solubility data of NaClO3 in the chloride liquor
  were read, so the mother liquor is taken to leave with the feed's chlorate-to-water ratio
  (D-008, L-5). The liquor density (1.40 kg/L), the cell voltage within the BREF's range and the
  oxygen share are ASSUMED too.
- Heats of solution and dilution are left out; the cells' heat of reaction is on the solid salts
  (D-006, L-2).
- The BREF's auxiliary chemicals (HCl, NaOH, dichromate, soda ash, H2O2, nitrogen) are LCA
  consumables, not streams (D-010). The preliminary LCI allocates 3.9 % to the hydrogen used, by
  mass; electricity and dichromate are gaps (D-011).
- Hazards (D-012): hydrogen with oxygen in the cell gas, the hydrogen vent, chlorine on a pH drop,
  sodium chlorate as an oxidiser with organic dust, hexavalent chromium, the DC cell line.

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams and reactions: the source of the BFD and PFD |
| `process/cells.yaml` | the chlorate cells (`cheme process cell`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `safety/` | HAZOP studies and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
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
cheme process propagate --fill  # the loop, the cells and tanks, crystallizer, dryer, specs and tear
cheme process cell              # the cells' Faraday, charge and energy balance
cheme process crystallizers     # the crystallizer, centrifuge and dryer
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
cheme assess lca --write        # the preliminary LCI
```

Needs cheme-as-code 1.12.0. DESIGN.md lists the sources, the decisions, the core features used
and the core limits hit.
