# Paracetamol by semi-batch acetylation of 4-aminophenol in aqueous acetic acid

A concept-stage batch plant for 2000 t/a of paracetamol (acetaminophen), part of the
ChemE-as-Code process library (issue
[#481](https://github.com/ChemE-as-Code/process-library/issues/481)). Not reviewed.

## Route

4-Aminophenol is acetylated with acetic anhydride in water acidified with acetic acid, the route
of US 3 917 695 A (Mallinckrodt):

- **Dissolver M-101.** The aminophenol is dissolved at 358 K in fresh water and half of the last
  batch's mother liquor, stirred with activated carbon, polish-filtered (F-100) and cooled to
  313 K.
- **Acetylator R-101.** Acetic anhydride (1.15 mol per mol, from acetic-anhydride-1) is dosed
  over 2.5 h at 313 K on chilled water; the anhydride's excess hydrolyses to acetic acid. The
  mass is then heated to 358 K and digested, and cooled to 293 K: the paracetamol crystallises.
- **Centrifuge C-101.** The crystals are spun off, washed with cold water and spun dry; half of
  the mother liquor goes to T-101 for the next charge, the other half to wastewater treatment.
- **Dryer D-101.** Conical vacuum dryer at 343 K, to 0.2 wt% volatiles.

| | |
|---|---|
| batch | 2516 kg of dried paracetamol every 9.97 h, 795 batches a year on a dedicated train |
| product | 99.8 wt% paracetamol (crude; the pharmacopoeial recrystallisation is outside the boundary) |
| yield | 82.0 % of theory on 4-aminophenol (model; the patent's comparable example: 84.8 %) |
| per kg product | 0.878 kg 4-aminophenol, 0.950 kg acetic anhydride, 3.15 kg water, 0.035 kg activated carbon |
| wastewater | 3.97 kg/kg, 16 wt% acetic acid and 5.5 wt% paracetamol |
| vessels | R-101 25 m3 glass-lined, D-101 8 m3 (sized by the recipe) |
| thermal screening | MTSR 313.6 K against an MTT of 373.15 K; 317.1 K with 100 times slower reactions |

## How it is modelled

The flowsheet (`process/flowsheet.yaml`) is calculated by cheme-as-code: the semi-batch and the
digestion from assumed rate laws, the crystallisation and the wash from the solubility of
paracetamol in water (Jimenez and Martinez 2006) with the acetic acid's effect calibrated to the
patent's Example 1, the centrifuge, the dryer and the recycle. `scripts/balance.py` scales the
feeds to 2000 t/a. The recipe (`process/recipe.yaml`) gives the cycle and sizes the vessels;
`cheme process reactor-hazards` screens the dosing. Every decision, source and assumption is in
[DESIGN.md](DESIGN.md).

## Run

```sh
cheme validate
cheme process propagate --check
cheme process recipe
cheme process reactor-hazards
cheme run scripts/balance.py
cheme assess lca --check
```

## Limits

Kinetics, the heat of acetylation and the centrifuge and dryer data are assumed; the
4-aminophenol, water, utilities and wastewater treatment are LCI gaps. No P&IDs, layout, HAZOP or
cost estimate yet.
