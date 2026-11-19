# Salicylic acid

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant for salicylic acid, the feed of aspirin, by the one-stage Kolbe-Schmitt
carboxylation of US 4 376 867 A (Example I): molten phenol is neutralised with 50 wt% caustic
soda dosed into it (R-101, `reactor: semibatch`, core ADR 0050), the sodium phenoxide solution
is dried to a powder in a kneader-reactor at ambient pressure and then at 4 kPa(a) to 463 K
(core's dryer, ADR 0057), and CO2 is dosed into the dry powder at 463 K over 5 h and held 1 h
(a semi-batch with a dosed gas, the share not taken up vented, ADR 0054; the dose is what the
source takes up plus the head space's fill at 5 bar):
PhONa + CO2 -> sodium salicylate, with 0.4 % of 4-hydroxybenzoic and 4-hydroxyisophthalic acid.
The crude is cooled to 373 K in the kneader, taken up in about 9 kg of water per kg and acidified with sulfuric acid at 328 K;
the first crop is centrifuged, washed and vacuum-dried at 333 K (below the 76 C where salicylic
acid sublimes), the mother liquor cooled to 298 K for a second crop that goes back to the next
acidification (core's crystallizer with the solubility of salicylic acid in water, ADR 0056),
and the phenol in the liquors is recovered for the next charge. Two design specifications size
the caustic for 1000 t/a and the fresh phenol for the source's charge ratio, and the two
recycles converge at tears (core ADRs 0060, 0070). `process/recipe.yaml` gives the cycle (22.7
h, the kneader the bottleneck), 349.0 batches a year of 2865.51 kg and the vessels; `cheme
process reactor-hazards` screens both semi-batches. Needs cheme-as-code 1.12.0. DESIGN.md
lists the core features used and the core limits hit.

Headline numbers and their caveats:
- Per kg of product: 0.711 kg of fresh phenol (0.681 stoichiometric; 95.5 % overall), 0.675 kg
  of 50 wt% caustic, 0.338 kg of CO2 (0.0073 kg of it vented), 0.429 kg of sulfuric acid, 12.1 kg
  of water, 13.3 kg of sodium sulfate liquor to treatment.
- The salicylate formed per batch is 87.8 % of the phenol charged, the source's 88 % (the CO2
  taken up is calibrated to it); 96.6 % of it is isolated in two crops, against the source's
  85 % first crop and about 95 % with the second crop for the older two-stage crude (D-007).
- The fresh phenol is a lower bound: the source does not account for 1.10 mol of phenol per
  23.2 mol charged, which the model recovers as phenol (D-005).
- The kinetics and every heat of reaction are ASSUMED (no open calorimetry or formation
  enthalpy of the sodium salts). Both semi-batches stay well below their MTTs (MTSR 343.4 K
  against 373.15 K; 464.4 K against an ASSUMED 493.15 K); the carboxylation's dT_ad of 229 K
  makes it dosing-controlled (D-011).
- The gas-solid carboxylation is carried as a liquid semi-batch at one pressure (core limits
  L-1, L-2), and the phenol recovery is a specified 95 % split (D-008).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components, blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures over several steps, the vessels (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | `balance.py`: the duties of the condensers and the kneader's cool-down and the CO2 dose's head-space share, which no core model gives (library ADR 0027) |
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
cheme process propagate --fill  # the feeds (design specifications), the models, the recycles and their duties
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessels, vent (--svg)
cheme process reactor-hazards   # thermal screening of the two semi-batches
cheme process crystallizers     # the crops, the filters and the dryers (the dryers' duties Q2, Q6)
cheme assess lca --write        # the preliminary LCI
```
