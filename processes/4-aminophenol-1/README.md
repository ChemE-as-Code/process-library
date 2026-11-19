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
  rest keeps the catalyst. The mass settles under nitrogen and the acid aqueous layer is drained.
- **Strip still R-102.** 15 % of the liquor is boiled off with the dissolved nitrobenzene (back
  to the next charge); the acid is neutralised with ammonia.
- **Aniline still R-103.** The aniline is distilled off with water; it separates in V-102 into
  crude aniline (a co-product) and water saturated with aniline (back to the next charge). The
  liquor is treated with activated carbon and filtered hot.
- **Crystallisers K-101, K-102, centrifuge C-101, dryer D-101.** The 4-aminophenol crystallises
  at 283 K; the mother liquor is concentrated under vacuum for a second crop; both crops are
  washed with cold water and dried under vacuum at 333 K. The ammonium sulfate liquor goes to
  wastewater treatment.

| | |
|---|---|
| batch | 1073 kg of dried 4-aminophenol every 8.5 h, 932 batches a year on a dedicated train |
| product | 99.5 wt% 4-aminophenol, 0.34 wt% ammonium sulfate (model; the patent: 99.1 %) |
| yield | 82.1 % of the nitrobenzene (model; the patent: 79 % over two crops) |
| per kg product | 1.366 kg nitrobenzene, 0.048 kg hydrogen, 1.173 kg 98 % acid, 0.399 kg ammonia; 0.163 kg crude aniline |
| wastewater | 6.82 kg/kg, 23 wt% ammonium sulfate |
| energy per kg | 5.48 kWh LP steam, 6.15 kWh to cooling water, 0.60 kWh to chilled water, 0.26 kWh power |
| vessels | R-101 and R-102 20 m3, R-103 16 m3 glass-lined, D-101 3.15 m3 (sized by the recipe) |
| thermal screening | dosed hydrogen: MTSR 358.6 K against an MTT of 373.1 K (376.5 K with 100 times slower reactions); the charge holds 130 K of adiabatic rise if hydrogen keeps flowing on a cooling failure |

## How it is modelled

The flowsheet (`process/flowsheet.yaml`) is calculated by cheme-as-code: the semi-batch
hydrogenation from assumed rate laws calibrated to the patent's aniline, the phase splits, the
two batch stills on relative volatilities estimated from solubilities and vapour pressures, the
neutralisation, the crystallisations and the wash from the solubility of 4-aminophenol in water,
the dryer, three recycles and three design specifications (capacity, the charge's water, the
hydrogen for 88 % conversion). The recipe (`process/recipe.yaml`) gives the cycle and sizes the
vessels; `cheme process reactor-hazards` screens the hydrogenation. Every decision, source and
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
