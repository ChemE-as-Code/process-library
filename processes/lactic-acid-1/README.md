# Lactic acid by fermentation

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A plant design kept as plain files in git: engineering lists as YAML, decisions and progress as
Markdown, the BFD and PFD generated from `process/`. Edited by people and by coding agents
(Claude Code), checked by [`cheme-as-code`](https://github.com/ChemE-as-Code/core).

Lactic acid (the PLA monomer) by fermentation of glucose through the gypsum route, the train
that the open BioSTEAM lactic biorefinery models (Bioindustrial-Park, MIT licence) and Garrido,
Cabeza and Falguera (2023, Fermentation 9, 901) describe, here fed with bought-in glucose
syrup:

1. **Fermentation, batch.** The syrup is diluted, fed corn steep liquor, and fermented by
   lactic acid bacteria in 16 fermenters at 323 K. Milk of lime, slaked on site from quicklime,
   holds the pH at 5 to 6, so the acid forms as calcium lactate. Per the BioSTEAM model, 0.76 of
   the glucose goes to lactic acid, 0.07 to acetic acid and 0.02 to cell mass. The broth reaches
   130 g/L in 146 h at 0.89 g/(L h). With a 12 h turnaround, a batch of 1106 t is harvested
   every 9.9 h (`process/recipe.yaml`).
2. **Acidulation.** The cell mass is centrifuged off. Sulfuric acid (93 wt%) turns the calcium
   lactate into lactic acid and gypsum, and the gypsum is filtered off with 20 wt% moisture.
3. **Evaporation.** A four-effect evaporator concentrates the crude acid to about 71 wt%. The
   acetic acid leaves with the water.
4. **Purification through ethyl lactate.** The acid is esterified with ethanol by reactive
   distillation on Amberlyst-15. The ethyl lactate is distilled off the residue of sugar and
   salts, and the ethanol is recovered. The ester is hydrolysed with 12 mol of water per mol,
   the ethanol is stripped and recycled, and the product is concentrated to 88 wt% lactic acid.

Core solves the flowsheet with `cheme process propagate`. Four design specifications set the
glucose syrup (100 000 t/a of lactic acid), the medium water (the titer), the ethanol make-up
(1.5 mol per mol of acid) and the hydrolysis recycle's purge (12 mol of water per mol of
ester); the other feeds follow the syrup (core ADR 0070). Three recycles converge as tears
(ADR 0060). The reactors run on their conversions, and the centrifuge, filter, evaporators and
columns on specified recoveries. The reactors' duties come from core's conversion model
(ADR 0059), the separations' from hand estimates. The batch recipe's year averages are what
the flowsheet carries (ADR 0051), and the fermenters' cleaning per batch enters the LCI (ADR
0053). Needs cheme-as-code 1.13.0. DESIGN.md lists the core limits this entry hit (L-1 to L-8).

## Key numbers (design case, per kg of lactic acid as 100 %, unallocated)

| item | value |
|---|---|
| capacity | 100 000 t/a of lactic acid, 12 500 kg/h in 8000 h; 14 188 kg/h of 88.1 wt% solution |
| glucose | 1.40 kg (as 2.01 kg of 70 wt% syrup); 92 % of the lactic acid formed reaches the product |
| quicklime | 0.42 kg (CaO, lime-1) |
| sulfuric acid | 0.75 kg as 100 % (0.80 kg of 93 wt%) |
| ethanol make-up | 0.011 kg (bioethanol-1) |
| process water | 6.4 kg, plus 0.16 kg for the fermenters' cleaning |
| steam heat | 4.09 kWh (14.7 MJ): LP 3.12, MP 0.97 |
| power | 0.24 kWh |
| gypsum cake | 1.61 kg (20 wt% moisture), not credited |
| wastes | cell mass cake 0.07 kg, ester column residue 0.25 kg (mostly unconverted glucose), wastewater 6.7 kg |

## Files

| path | what |
|---|---|
| `process.yaml` | the Atlas manifest |
| `DESIGN.md` | source register, decisions D-001 to D-012, core features used and limits L-1 to L-8 |
| `process/` | materials, reactions, flowsheet (the source of `BFD.xml` and `PFD.xml`), batch recipe, design basis |
| `equipment/equipment-list.yaml` | equipment with first sizes |
| `lca/` | `lca.yaml` (goal and scope), `mappings.yaml` (links to library producers), the written inventory and dataset |
| `PROGRESS.md` | what changed, when and why |

Hazards (D-012): ethanol in the purification under vacuum, quicklime slaking, concentrated
sulfuric acid, hot concentrated lactic acid, gypsum scaling. The fermentation's heat release is
slow; with the agitators' heat a whole batch without cooling could reach its boiling point, so
an agitator trip on lost cooling is an open safeguard. No HAZOP at this stage.

Issue: ChemE-as-Code/process-library#517.
