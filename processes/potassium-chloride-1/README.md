# Potassium chloride

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for potassium chloride (muriate of potash), one train of 150 t/h of KCl
crystal (1.2 Mt/a), from crushed sylvinite ore by hot leaching and vacuum cooling
crystallisation, as the Brazil Potash technical report summary (2024) and US 4 412 838 A describe
it. The ore (27.3 wt% KCl, below 4 mm) is leached in two agitated stages with mother liquor at
about 90 C: the brine, near saturation in NaCl, takes up the sylvite and leaves the halite.
Cyclones, a hot thickener and a filter send the salt tailings to the pile. The hot brine is cooled
to about 45 C in seven vacuum stages, where 28 % of its KCl crystallises; the flashed water is
condensed and returned as dilution water so that the NaCl stays dissolved. Centrifuges and a
gas-fired dryer give the product; the mother liquor, less a small purge to deep-well injection,
is heated by the stages' own vapour (as far as the brine's boiling-point elevation allows) and
by LP steam and goes back to the leach.

How core models it:

- `cheme process propagate` solves the whole loop: the leach as a conversion of sylvite (and a
  little halite) into the brine, a solid separation for the tailings, core's crystallizer (KCl
  with NaCl as a spectator, an adiabatic flash, centrifuge) and dryer, two tears (the mother
  liquor and the condensate) and two design specifications: the ore for 150 t/h of crystal and
  the make-up water for the hot brine's 14.19 wt% KCl.
- The duties are enthalpy balances on the propagated streams with thermo's latent heats and solid
  heat capacities that close around the loop; the vapour heat recovery is limited by the brine's
  boiling-point elevation (core's Pitzer model of NaCl-H2O, `cheme process electrolyte`, the
  KCl's share ASSUMED); the dryer is core's model (`cheme process crystallizers`).

Headline numbers and their caveats:

- 4.0 t of ore, 0.31 t of make-up water, 1.80 GJ of LP steam, 0.23 GJ of fired heat and 141.3 kWh
  per t of product; 3.15 t of salt tailings per t; KCl recovery 90.8 % (the Brazil Potash
  figure, to which the leach's dissolution is set). The steam is 1.2 times the Brazil Potash
  report's hot-leach steam per t (D-008).
- The hot brine's KCl and the crystallizer's per-pass yield (0.2685, the equilibrium on the same
  line) are ASSUMED: no open solubility data of the KCl-NaCl-water system were read, so they come
  from an open cavern-brine analysis (Encanto PFS 2017) and the patent's statement that the KCl
  solubility doubles between 20 and 110 C. The patent's own example forms 1.5-1.7 times more
  crystal per kg of feed and K, so the brine circulation and the steam are probably high (DESIGN.md
  D-004, D-007, L-3).
- Heats of solution and crystallisation, the ejectors' steam and heat losses are left out and
  sized in D-009; the mother liquor needs 368 K to hold the leach at 363 K here, against the about
  115 C of the Brazil Potash report: on these counts the steam is a lower bound (D-008, D-009, L-2).
- The electricity is ASSUMED from the Brazil Potash report's process load list per t (Table 128);
  reagents without an amount read (flocculant, anti-caking agent) are left out (D-008, D-009).
- The preliminary LCI has one product; the ore, the tailings and the brine purge are gaps; the
  electricity and the cooling water are gaps in `cheme assess lca`, and the Atlas build links them
  to the shared grid entry and cooling-tower utility (D-010).
- Hazards (D-011): hot brine and steam, vacuum vessels, the dryer's gas burners, dust, rotating
  machinery, corrosion by hot chloride brine, the tailings pile and brine injection; no reaction.

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams and the dissolutions: the source of the BFD and PFD |
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
cheme process propagate --fill  # the loop, leach, tailings, crystallizer, dryer, specs and tears
cheme process crystallizers     # the tailings separation, crystallizer, centrifuge and dryer
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
cheme assess lca --write        # the preliminary LCI
```

Needs cheme-as-code 1.13.0. DESIGN.md lists the sources, the decisions, the core features used
and the core limits (L-1 to L-5).
