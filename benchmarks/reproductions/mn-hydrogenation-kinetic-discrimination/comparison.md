# Comparison: published Mn-CNP regression models vs our refits

- **Reference:** `source.yaml` (van Schendel et al., ChemCatChem 2021, 13, 4886,
  doi:10.1002/cctc.202101140; SI file `CCTC-13-4886-s001.pdf`, sha256 `6f872348…652f`).
- **Tolerances:** `tolerances.yaml`, frozen in commit 1fa0e6d (2026-11-04 13:52:57 UTC)
  together with `source.yaml` and `inputs.yaml`. No fit was run before that commit. The
  first comparison run followed it the same afternoon; the file has not changed since
  (`git diff 1fa0e6d HEAD -- tolerances.yaml` is empty).
- **Run:** `uv run benchmarks/reproductions/mn-hydrogenation-kinetic-discrimination/run.py`
  from the repository root, 2026-11-04, Python 3.13.16, numpy 2.3.4, pypdf 5.1.0,
  matplotlib 3.10.7, pyyaml 6.0.3, uv 0.13.0. About 5 s. Every number below is in
  `results/comparison.json`.
- **Method:** the four models of the source refitted to SI Table S2 regressors and
  y = ln(Table S1 rate), with the source's term lists and outlier lists. Models I-III by
  ordinary least squares, model IV by bisquare iteratively reweighted least squares
  (`inputs.yaml`). The initial-rate kinetics by straight lines through SI Tables S23-S26.

## Result: FAIL under the frozen rule (94 of 96 checks pass)

All 35 coefficients of models I to IV are within tolerance, and so are all their standard
errors, every RMSE, R2 and PRESS of models I to III, and all nine checks of the separate
initial-rate kinetics. Two checks fail. Both concern how the source reported a number, not
the fitted model (explanations 1 and 2 below). One of them is in the group the pass rule
requires for "partial", so the verdict under the frozen rule is **fail**, not partial.

### Summary by group

| Group | Checks | Pass | Largest deviation |
| --- | --- | --- | --- |
| data integrity (30 runs, y, pure error) | 3 | 3 | pure-error mean square 0.044638 vs 0.044638 |
| model I, full quadratic, n = 30 | 34 | 34 | x3 coefficient +0.081 (tolerance 1.37, 0.1 SE) |
| models II and III | 38 | 37 | **model II fitted values vs SI Table S10: 0.305 (tolerance 0.02)** |
| model IV, robust, n = 24 | 14 | 13 | **RMSE 0.577 vs 0.657, -12.3 % (tolerance 10 %)** |
| conventional kinetics (Figure 7) | 9 | 9 | Ea at 50 ppm 90.7 vs 90 kJ/mol |

### Models II, III and IV (the competing models used in the design extension)

| Quantity | Reference | Ours | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| II intercept | 57.28 ± 14.22 | 57.16 ± 14.17 | -0.12 | 1.42 | pass |
| II x1 (1/T) | -19523 ± 4674 K | -19484 ± 4658 K | +39 | 467 | pass |
| II x2 (p) | 0.068951 ± 0.014934 1/bar | 0.068924 ± 0.014922 | -2.7e-5 | 1.5e-3 | pass |
| II x3 (ln cat) | 6.0532 ± 1.6052 | 6.0382 ± 1.6003 | -0.015 | 0.16 | pass |
| II x4 (ln base) | -2.6974 ± 0.776 | -2.6892 ± 0.7738 | +0.008 | 0.078 | pass |
| II x1·x3 | -1601.3 ± 529.8 K | -1597.4 ± 528.1 K | +3.9 | 53 | pass |
| II x2·x4 | 0.0057967 ± 0.00217 | 0.0057934 ± 0.0021686 | -3.3e-6 | 2.2e-4 | pass |
| II x4² | -0.24092 ± 0.054258 | -0.24036 ± 0.054085 | +5.6e-4 | 5.4e-3 | pass |
| II RMSE / R2 / PRESS | 0.387 / 0.984 / 5.1862 | 0.3867 / 0.9842 / 5.1840 | -0.08 % / +0.0002 / -0.04 % | 2 % / 0.002 / 2 % | pass |
| II fitted values, 26 runs (SI Table S10) | - | max 0.305 | 0.305 | 0.02 | **fail** |
| III intercept | 16.705 ± 3.40 | 16.689 ± 3.390 | -0.016 | 0.34 | pass |
| III x1 (1/T) | -4936.9 ± 382.1 K | -4936.7 ± 382.0 K | +0.2 | 38 | pass |
| III x2 (p) | 0.040648 ± 0.0061137 | 0.040652 ± 0.0061119 | +3.9e-6 | 6.1e-4 | pass |
| III x3 (ln cat) | 1.3553 ± 0.160 | 1.3516 ± 0.1593 | -0.0037 | 0.016 | pass |
| III x4 (ln base) | -2.1133 ± 0.82233 | -2.1067 ± 0.8198 | +0.0066 | 0.082 | pass |
| III x4² | -0.21516 ± 0.057568 | -0.21471 ± 0.057397 | +4.5e-4 | 5.8e-3 | pass |
| III RMSE / R2 / PRESS | 0.413 / 0.979 / 6.1608 | 0.4132 / 0.9786 / 6.1585 | +0.06 % / -0.0004 / -0.04 % | 2 % / 0.002 / 2 % | pass |
| III fitted values, 25 rows (SI Table S16) | - | max 0.0016 | 0.0016 | 0.02 | pass |
| IV intercept | 31.554 ± 4.036 | 31.400 ± 3.641 | -0.15 (SE -9.8 %) | 1.01 (SE 15 %) | pass |
| IV Ea (b1) | 39.307 ± 7.560 kJ/mol | 39.122 ± 6.795 kJ/mol | -0.18 (SE -10.1 %) | 1.89 (SE 15 %) | pass |
| IV x2 (p) | 0.035241 ± 0.0092655 | 0.034907 ± 0.0082567 | -3.3e-4 (SE -10.9 %) | 2.3e-3 | pass |
| IV x3 (ln cat) | 1.5982 ± 0.27672 | 1.5893 ± 0.2485 | -0.009 (SE -10.2 %) | 0.069 | pass |
| IV x4 (ln base) | 1.0932 ± 0.07059 | 1.0887 ± 0.0633 | -0.0045 (SE -10.3 %) | 0.018 | pass |
| IV x6 (time) | -3.70e-5 ± 8.84e-6 1/s | -3.718e-5 ± 7.99e-6 1/s | -1.8e-7 (SE -9.6 %) | 2.2e-6 | pass |
| IV RMSE | 0.657 | 0.5765 (weighted) | -12.3 % | 10 % | **fail** |
| IV fitted values, 24 runs (SI Table S21) | - | max 0.023 | 0.023 | 0.05 | pass |

Model I (34 checks, all pass): every coefficient within 0.1 SE, SEs within 0.5 %, RMSE
0.5149 vs 0.515, R2 0.9827 vs 0.983, PRESS 22.884 vs 22.8951, fitted values within 0.0011.

### Separate initial-rate kinetics (SI Tables S23-S26, article Figure 7)

| Quantity | Reference | Ours | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| Ea, 50 ppm catalyst | 90 ± 7 kJ/mol, r2 0.96 | 90.7 ± 7.5 kJ/mol, r2 0.961 | +0.7 / +0.5 / +0.001 | 1 / 1 / 0.006 | pass |
| Ea, 200 ppm catalyst | 51 ± 4 kJ/mol, r2 0.96 | 51.2 ± 4.2 kJ/mol, r2 0.962 | +0.2 / +0.2 / +0.002 | 1 / 1 / 0.006 | pass |
| base order, low base (4 points) | ~2.5 | 2.49 | -0.01 | 0.15 | pass |
| base order, high base (5 points) | ~0 | 0.06 | +0.06 | 0.15 | pass |
| catalyst order (6 points) | ~1.5 | 1.55 | +0.05 | 0.15 | pass |
| data integrity: y vs SI y columns | - | max 4.5e-6 | - | 1e-4 | pass |
| data integrity: pure-error MS (runs 1-5, 11) | 0.044638 | 0.044638 | 0.00 % | 1 % | pass |

## Deviations and explanations

1. **SI Table S10 belongs to the first-stage fit, not to the reported model II.** The
   fitted values in SI Table S10 are reproduced to 0.0026 by the model II terms fitted to
   all 30 runs (`sensitivity.si_fitted_value_tables_vs_first_stage_fit_on_30_runs`), i.e.
   the fit before the four outliers were removed. The coefficients of SI Table S7 (and
   article Table 3) are those of the 26-run refit, which we reproduce within 0.1 SE. The
   table and the coefficients therefore describe two different fits. This is a source
   inconsistency; our model II matches the reported coefficients, which is what the design
   extension uses. The frozen check compares with Table S10, so it fails.
2. **Model IV RMSE and SEs: robust scale convention.** Our coefficients agree within
   0.12 SE, but our SEs are 9.6-10.9 % smaller and our RMSE 12.3 % smaller than MATLAB's.
   The seven ratios correspond to one scale factor of 1.11 to 1.14 on the residual
   standard deviation: MATLAB's robust fit estimates sigma with its own robust formula,
   while we use the bisquare-weighted residual mean square (`inputs.yaml`). The unweighted
   RMSE of our fit is 0.618 (-5.9 %). The SE check passes at 15 %; the RMSE check (10 %)
   fails. If MATLAB's larger sigma is the right one, the prediction bands of model IV in the
   extension are about 10 % too narrow; this does not change which runs are selected.
3. **Model III outlier list.** The SI text lists runs 7, 16, 20, 22, 28, 30 as removed; SI
   Table S16 has 25 rows including run 28. Our 24-run fit (text list) reproduces every row of
   Table S16 to 0.0016, including run 28, so Table S16 lists the 24-run model's prediction
   for run 28 as well. The text list is correct. The 25-run alternative (sensitivity) gives
   different coefficients (x1 -5188 K, RMSE 0.461) and does not reproduce Table S16 (0.34).
4. **Regressor rounding.** Refitting with x3 and x4 computed from the raw Table S1 levels
   instead of the rounded Table S2 values moves model II's x1 coefficient by 1.4 % and model
   III's x4 coefficient by 8 % (sensitivity `raw_levels`); the Table S2 values reproduce the
   source, so the authors fitted the rounded values. Table S2 also uses 1/(T + 274.1 K).
5. **Reproduced but not compared:** apparent activation energies from the refits: model II
   33.4, 45.7 and 51.8 kJ/mol at 0.0625, 0.157 and 0.25 mmol/L catalyst (through its
   T x ln cat term), model III 41.0 kJ/mol, model IV 39.1 kJ/mol. The initial-rate runs give
   90.7 kJ/mol at 50 ppm and 51.2 kJ/mol at 200 ppm. Model II's interaction term makes the
   apparent activation energy rise with catalyst concentration, while the initial-rate runs
   show it falling; the article reads the initial-rate drop as mass-transfer limitation. We
   record this contrast but do not resolve it.

## What the comparison does and does not show

It shows that the published coefficients, standard errors and statistics of models I to IV
follow from the published run table with the stated term and outlier lists. It does not show
that any of the models is right. All four are regressions on the same 30 runs, and models II
to IV fit them about equally well (RMSE 0.39, 0.41, 0.58-0.66 in ln rate against a
pure-error standard deviation of 0.21). That is why the extension asks which new run would
separate them.
