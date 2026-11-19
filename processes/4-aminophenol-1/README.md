# 4-Aminophenol by batch hydrogenation of nitrobenzene in dilute sulfuric acid

A concept-stage batch plant for 1000 t/a of 4-aminophenol (p-aminophenol), the feed of the
library's paracetamol-1, part of the ChemE-as-Code process library (issue
[#506](https://github.com/ChemE-as-Code/process-library/issues/506)). Not reviewed.

## Route

Nitrobenzene is hydrogenated over platinum on carbon in dilute sulfuric acid with a surfactant,
the route of US 3 383 416 A (Benner) and US 4 307 249 A (Mallinckrodt). The N-phenylhydroxylamine
formed rearranges in the acid to 4-aminophenol (the Bamberger rearrangement), or is reduced on to
aniline:

- **Hydrogenator R-101.** Water, 98 % acid, the recycled distillates and fresh nitrobenzene go
  onto the nitrobenzene layer kept from the last batch, which holds the catalyst. Hydrogen is
  dosed at 358 K and about 104 kPa(a) over 5.5 h until 88 % of the nitrobenzene is reduced: the
  rest keeps the catalyst. The mass is cooled to 333 K and settles under nitrogen, and the acid
  aqueous layer is drained.
- **Strip still R-102.** 15 % of the liquor is boiled off with the dissolved nitrobenzene (back
  to the next charge); the acid is neutralised with ammonia to about pH 6.
- **Aniline still R-103.** The aniline is distilled off with water while process water is fed
  to hold the level, so the 4-aminophenol stays dissolved; the distillate separates in V-102
  into crude aniline (a co-product) and water saturated with aniline (back to the next charge).
  The liquor is treated with activated carbon at pH 6 and filtered hot.
- **Crystalliser K-101, centrifuge C-101, dryer D-101.** The liquor is brought to pH 7.2 and the
  4-aminophenol crystallises at 283 K; the crystals are washed with cold water and dried under
  vacuum at 333 K. The ammonium sulfate liquor goes to an ammonium sulfate recovery.

| | |
|---|---|
| batch | 1209 kg of dried 4-aminophenol every 9.58 h, 827 batches a year on a dedicated train |
| product | 99.6 wt% 4-aminophenol, 0.20 wt% ammonium sulfate (model; the patent: 99.1 %) |
| yield | 79.4 % of the fresh nitrobenzene (model, an upper bound; the patent isolated 73 to 78 %, and found 6 % more in the filtrate of its first run) |
| per kg product | 1.415 kg nitrobenzene, 0.050 kg hydrogen, 1.215 kg 98 % acid, 0.413 kg ammonia; 0.159 kg crude aniline |
| ammonium sulfate liquor | 11.2 kg/kg, 14 wt% ammonium sulfate, to recovery |
| energy per kg | 5.86 kWh LP steam, 7.38 kWh to cooling water, 1.07 kWh to chilled water, 0.48 kWh power |
| vessels | R-101, R-102 and R-103 25 m3 glass-lined, D-101 3.15 m3 (sized by the recipe) |
| thermal screening | dosed hydrogen: MTSR 358.6 K against an MTT of 373.1 K (376.5 K with 100 times slower reactions); the charge holds 130 K of adiabatic rise if hydrogen keeps flowing on a cooling failure |

## How it is modelled

The flowsheet (`process/flowsheet.yaml`) is calculated by cheme-as-code: the semi-batch
hydrogenation from assumed rate laws calibrated to the patent's aniline, the phase splits, the
two batch stills on relative volatilities estimated from solubilities and vapour pressures, the
neutralisation, the crystallisation and the wash from the solubility of 4-aminophenol in water,
the dryer, three recycles and four design specifications (capacity, the charge's water, the
hydrogen for 88 % conversion, the water fed to the aniline still). The heats the models leave
out (sensible heats, the vessels' metal) come from `scripts/balance.py`, so every heat flow is on
an energy stream. The recipe (`process/recipe.yaml`) gives the cycle and sizes the vessels;
`cheme process reactor-hazards` screens the hydrogenation. Every decision, source and
assumption is in [DESIGN.md](DESIGN.md).

## Hazards

Hydrogen with a platinum catalyst (fire, explosion: nitrogen purges before and after the
hydrogen); a strongly exothermic reduction whose hydrogen is fed on demand, so a cooling or
agitation failure must shut the hydrogen off; the N-phenylhydroxylamine intermediate, which can
accumulate and decompose (calorimetry needed); toxic nitrobenzene and aniline; hot sulfuric
acid; ammonia. See DESIGN.md D-011.

## Life cycle inventory

A preliminary gate-to-gate inventory per kg of 4-aminophenol (`lca/`), the crude aniline
allocated by mass. The sulfuric acid, hydrogen, ammonia and nitrogen are linked to the library's
sulfuric-acid-1, hydrogen-1, ammonia-1 and asu-1; the nitrobenzene and the other backgrounds are
open gaps.

## Licence

CC BY 4.0 (the library's `LICENSE-DATA`); the patents and data sources are cited in DESIGN.md,
nothing is copied from them.
