# Oxalyl chloride

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: DEXPI 2.0.1 P&IDs in `pid/`, engineering lists as
YAML, decisions and progress as Markdown. Edited by people and by coding agents (Claude Code),
checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

A batch plant for oxalyl chloride by Bayer's one-pot route (US 4 341 720 A, Examples 19 and 20):
phosphorus trichloride is chlorinated to phosphorus pentachloride in the heel kept from the last
batch (PCl5 suspended in POCl3 with 2,4-dimethylpyridine), then anhydrous oxalic acid suspended
in recycled POCl3 is dosed in: (COOH)2 + 2 PCl5 -> (COCl)2 + 2 POCl3 + 2 HCl, while part of the
acid decomposes to CO and CO2. Both reactions are semi-batches in one reactor-still R-101
(`reactor: semibatch`, core ADR 0050); the chlorine is a dosed gas taken up with its heat of
solution (ADR 0063). The HCl, CO and CO2 leave by a vent (`batch.vent`, ADR 0054) that carries the
liquid's oxalyl chloride and POCl3 vapour through a chilled-water vent condenser, whose
condensate returns (`vent.vapour`, `vent.condenser`, ADR 0062), to a water absorber making 30 wt%
hydrochloric acid; the tail gas goes to the site's thermal oxidiser. The crude is then stripped off
the heel at 15 kPa(a) in the same vessel (a batch still, `still:`, ADR 0055) and rectified at
atmospheric pressure in C-201 with a 15-stage column at reflux 6 (`still.column`, ADR 0061): a
product cut, an off-cut that goes into the next still charge, and POCl3, part of which suspends
the next acid, the rest a co-product. Core converges the heel, the POCl3 and the off-cut
recycles at two tear streams (`tears:`, ADR 0060), and the models write every duty they compute
(ADR 0059), with the vessels' metal (ADR 0063). `process/recipe.yaml` gives the cycle (26.01 h,
R-101 the bottleneck), 304.5 batches a year of 1642.1 kg, R-101's 16 m3 vessel and its jacket
check (`cheme process recipe`); `cheme process reactor-hazards` screens both semi-batches and
compares the gas a cooling failure releases with R-101's vent capacity of 450 m3/h. Needs cheme-as-code 1.11.0. DESIGN.md lists the core features
used and the core limits hit.

Headline numbers and their caveats:
- The yield, 77.7 % of theory on the oxalic acid, is a model result below the source's 84.2 %
  isolated: the selectivity is calibrated to the oxalyl chloride in the source's crude (85.0 %),
  and 6.8 % of the acid's worth of oxalyl chloride passes the vent condenser to the absorber,
  which cannot run colder without freezing POCl3 (274.33 K) on its wall (D-006, D-010).
- The kinetics are ASSUMED (no open kinetics or calorimetry). The chlorine is dosed over 8 h so
  that R-101's jacket on cooling water removes the chlorination's heat (D-003). Both
  cooling-failure temperatures stay below the boiling points of the vented mass (MTSR 335.1 K
  against 358.8 K, 334.0 K against 367.0 K). The gas a cooling failure releases is 0.79 of the
  vent's capacity. Two design findings for the next stage come from a 100 times slower
  reaction: the acid's gas at a cooling failure is then 1.51 times the vent's capacity, and the
  chlorine that accumulates (7.65 %) makes the mass boil chlorine at 333 K, which the vent
  carries past the absorber (D-011).
- The product, 99.50 wt% with 0.43 wt% POCl3, rests on an ideal liquid and a Clausius-Clapeyron
  line for oxalyl chloride's vapour pressure (no open Antoine fit or VLE data; D-007, D-008).
- The stills' boil-ups are what their jackets give at the stills' ends, and the vessels' metal
  (ASSUMED masses) is counted in the heat (D-007 to D-009).
- The plant makes 2.67 kg of POCl3 and 2.76 kg of 30 wt% hydrochloric acid per kg of product.
  The preliminary LCI allocates economically at ASSUMED relative prices (58.0 % to the oxalyl
  chloride); all burdens to the product is the conservative bound (D-012).

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML); none yet |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml`, `process/reactions.yaml` | components (with the stills' Antoine lines and the gases' ideal-gas data), blocks, steps, streams and reactions: the source of the generated BFD and PFD (`process/*.xml`, `cheme process build`) |
| `process/recipe.yaml` | the batch recipe: batch size, unit procedures over several steps, R-101's vessel and jacket, the strip's and the rectification's times (`cheme process recipe`) |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `lca/` | the preliminary gate-to-gate LCI (`lca/lca.yaml`, `lca/mappings.yaml`; the rest written by `cheme assess lca --write`) |
| `checks/checks.yaml` | engineering-step gates; `checks/status.json` their result at the last stage sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | generator scripts and `balance.py`: the feeds for 500 t/a, the absorber's water and split, the temperatures and duties core's models do not give, the MTTs (D-004, D-009, D-010, D-011) |
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
cheme process propagate --fill  # the semi-batches, the stills, the recycles and their duties from the feeds
cheme run scripts/balance.py    # the feeds, the absorber, the other temperatures and duties (then propagate again)
cheme process recipe            # batch cycle: occupancy, bottleneck, batches per year, vessel, jacket, vent (--svg)
cheme process reactor-hazards   # thermal screening of the two semi-batches
cheme process stills            # the strip and the rectification: cuts, purity, recovery, boil-up time, duties
cheme assess lca --write        # the preliminary LCI
```
