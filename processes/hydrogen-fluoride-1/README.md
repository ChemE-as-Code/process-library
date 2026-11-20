# Hydrogen fluoride

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A continuous plant for anhydrous hydrogen fluoride (AHF), about 18 400 t/a, from acid-grade
fluorspar and sulfuric acid, as the EU LVIC-AAF BREF (2007, chapter 6) and US 6 699 455 B2
describe it. The dried spar (97.5 wt% CaF2) is preheated indirectly to 400 C, premixed with feed
acid at 120 C in a screw mixer and reacted in a 20 m x 2.5 m rotary kiln heated by nine
natural-gas combustion chambers in three zones: CaF2 + H2SO4 -> 2 HF + CaSO4, endothermic by
59 kJ/mol. The spar's silica, carbonate, oxides and flotation fatty acids give SiF4, CO2, water
and SO2. The kiln gas is scrubbed with sulfuric acid, which returns to the kiln; oleum binds the
water of that loop. HF is condensed against brine and distilled free of low boilers (SO2, SiF4,
CO2) and high boilers (water, acid). A final scrubber recovers the HF of the vent gas into the
fresh acid, SiF4 becomes 25 wt% fluorosilicic acid, SO2 is scrubbed with caustic, and lime
neutralises the anhydrite's free acid.

How core models it:

- `cheme process propagate` solves the whole flowsheet: the kiln (five reactions), the burners
  (natural gas with air), the oleum hydration, the neutraliser and the two absorbers as
  conversion reactors; the kiln discharge,
  the scrubbers, the condensers and the columns as component splits; two recycles torn (the feed
  acid and the final scrubber acid) and two design specifications: the fresh acid for 1.0 wt%
  free acid in the kiln solids and the oleum for 3.0 wt% water in the feed acid (core ADR 0070).
- The duties are hand balances on the propagated streams with single property values of the
  chemicals and thermo packages (DESIGN.md D-009): no core model covers a solid-gas kiln or the
  associating HF vapour (DESIGN.md L-1, L-2).

Headline numbers and their caveats:

- Per kg of AHF: 2.08 kg of spar, which is 2.03 kg of CaF2, 3 % under the BREF's 2.1-2.2 kg
  CaF2: the model loses fluorine only in the anhydrite's CaF2 and as SiF4, so it is optimistic;
  2.62 kg of H2SO4 equivalent (BREF: 2.6-2.7), 3.63 kg of anhydrite (BREF: about 3.7), 0.225 kWh
  of electricity (BREF middle), 0.30 kg of steam (BREF: 0.15-0.8).
- Natural gas: 4.50 GJ/t burnt (the patent's 189 m3/h in the kiln, a furnace efficiency of 0.478
  on the 2.15 GJ/t the charges absorb, ASSUMED the same for the spar preheater), inside the
  BREF's 4-5 GJ/t for new plants; its CO2 is 0.25 kg per kg of AHF, in the flue gas.
- The kiln's conversions are ASSUMED so that the anhydrite keeps the patent's 0.8 wt% CaF2 and
  1.0 wt% acid; the scrubbers, condenser and columns are ASSUMED splits (no HF-H2O model).
- Refrigeration (1.24 GJ/t) is below the BREF's 2-3 GJ/t, which the BREF does not break down;
  the HF association heat left out of the condensers (up to 747 kW) and the quench, storage and
  dilution cooling the model does not have may explain it (ASSUMED, DESIGN.md D-009).
- The preliminary LCI gives all burdens to the HF: the anhydrite to landfill, the fluorosilicic
  acid burden-free. Fluorspar and refrigeration are gaps (and electricity in `cheme assess
  lca`; the Atlas build links it to the shared grid entry).
- Hazards (DESIGN.md D-012): HF (toxic, corrosive, boils at 19.5 C), oleum, SO2 and SiF4, the
  fired kiln.

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams and reactions: the source of the BFD and PFD |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `safety/` | HAZOP studies and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `.claude/skills/` | how an agent works here (not in git: run `cheme skills update` once after cloning) |

## Commands

```sh
cheme validate                       # lists, flowsheet balances
cheme process propagate --check      # the solved streams are current
cheme process build                  # BFD and PFD from the flowsheet
cheme assess lca --check             # the LCA outputs are current
cheme check --no-write               # the concept gates
```

Licences: data and designs CC BY 4.0, code and scripts AGPL-3.0-or-later (library `LICENSE-DATA`,
`LICENSE`).
