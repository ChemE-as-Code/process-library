# HYPOTHETICAL design extension (not validated): treatment time for a blue-pumped colour-conversion layer

This is a design calculation built on the measured 150 °C series (one session, 2021-12-08). It is
not a reproduction, nothing in the source tests it, and it must not be used as design data.
Numbers are in `results/comparison.json` under `extension`. The figure is `results/fig_extension.svg`.

## Question

A display layer converts a 450 nm blue pump to green with in situ HF treated InP cores. The layer
is to absorb 90 % of the pump (absorbance 1.0 at 450 nm). How much untreated QD stock does each
square metre need, and what fraction of the blue photons comes out green, when the treatment at
150 °C is stopped after 5 min instead of 60 min?

## Model (inputs.yaml, `extension`)

- Material retained: absorbance at 450 nm of an aliquot over that of the 0 min aliquot, at equal
  dilution (assumed; Figure 1C is labelled absolute absorbance). The extinction coefficient of the
  untreated QDs at 450 nm is 0.45 cm⁻¹ µM⁻¹ (stated at 330 nm) scaled by the measured 450/330 nm
  ratio: 9.3 × 10⁴ M⁻¹ cm⁻¹ per QD.
- Starting QDs per area: n = A₄₅₀ / (1000 · ε₄₅₀ · R₄₅₀) mol cm⁻², with R₄₅₀ the retained fraction.
  Standard batch: 41 nmol QDs (Methods).
- Blue-to-green photon yield: (1 − 10^−A₄₅₀) × PLQY. This ignores reabsorption, scattering,
  outcoupling and any change of the QDs in a solid matrix.

## Result

| Treatment at 150 °C | PLQY | A(450 nm) retained | Starting QDs per m² | 41 nmol batches per m² | Blue → green |
| --- | --- | --- | --- | --- | --- |
| 60 min (base) | 55.9 % | 34.6 % | 310 µmol | 7550 | 50.3 % |
| 5 min (changed input) | 42.4 % | 36.4 % | 295 µmol | 7190 | 38.2 % |
| 0 min (untreated, for scale) | 0.09 % | 100 % | 107 µmol | 2620 | 0.08 % |

**Engineering consequence.** Etching removes about 64 % of the 450 nm absorbance within the first
5 min. After that the absorbance barely changes (36.4 % → 34.6 % retained), while the PLQY rises
from 42 % to 56 %. Stopping at 5 min therefore saves only 4.8 % of the starting stock per square
metre and costs 12.2 percentage points of blue-to-green conversion. That is about a quarter of
the green output (38.2 against 50.3 photons per 100 blue photons). In the measured range, the
extra 55 min at 150 °C costs reactor time and almost no material. The material cost of the
treatment is set in the first minutes, and in this data set by the dose, not by the time.

## Flags (out of range, extrapolation, evidence)

- One run, one session, no replicate. The 30 and 60 min PLQYs differ by 1.8 pp, below the 5 pp
  measurement band, so a trend between 30 and 60 min is not resolved.
- Equal dilution of aliquots is assumed, not documented. If the 5-60 min aliquots were diluted
  differently from the 0 min aliquot, the retained fraction and the stock per m² change in
  proportion. The washed sample is excluded because its redispersion volume is unknown.
- The layer absorbance at 540 nm would be about 0.18-0.21 for A₄₅₀ = 1. Reabsorption of the
  green emission is therefore not negligible, and the conversion values are upper bounds.
- Solution PLQY is taken for a solid layer. Film formation, ligand loss and matrix effects are
  outside the data.
- Temperatures other than 150 °C, other doses, ZnCl2, or stock and batch sizes beyond 41 nmol
  are extrapolation. The source itself notes that the gaseous HF makes kinetics and scale-up
  hard to control. No scale-up claim is made.
- The extinction coefficient comes from a model (Maxwell-Garnett), as the source states. Its
  uncertainty passes directly into the stock per m², but not into the 5 against 60 min comparison.
