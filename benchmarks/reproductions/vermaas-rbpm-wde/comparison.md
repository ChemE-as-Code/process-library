# Comparison: rBPM WDE reproduction (Prats Vergel et al. 2025, 4TU v1)

- **Reference:** `source.yaml`: 4TU dataset v1, all four files verified by sha256, and the paper
  (Methods eq. 3 to 10, Fig. 3 to 5).
- **Tolerances:** `tolerances.yaml`, frozen in commit 30d35b7. That commit came after the source
  record (de78f02) and before any comparison run. Its header lists what had been seen before the
  freeze.
- **Runs:** `uv run --isolated benchmarks/reproductions/vermaas-rbpm-wde/reproduce.py`,
  2026-11-04, Python 3.12, numpy 2.2.6, scipy 1.15.3. Versions and inputs are in each record.
  - `reruns/2026-11-04-run.json` is the first comparison run. It used the script as committed,
    minus the "informational" block. Its `dirty: true` is because the script was not yet
    committed.
  - `reruns/2026-11-04-run-2.json` is the run with that block added after the first run, to
    explain deviations. Every frozen check is identical in the two records.
  - Two earlier attempts stopped before any comparison: one on a scipy build failure under
    Python 3.15, one on a YAML syntax error in `source.yaml`. Neither produced a number.
- **Order of evidence:** `git log -- benchmarks/reproductions/vermaas-rbpm-wde/` shows source
  record, then tolerances, then script and results. The records cannot prove that no
  uncommitted run happened before the freeze; the claim rests on that order and on this account.

## Result

| Check | Kind | Result under the frozen rule |
| --- | --- | --- |
| R1 | reproduction of a measured series | **FAIL**: 5 of 6 current densities pass; 200 mA/cm2 misses by 0.00006 |
| R2 | reproduction of a model trajectory | **FAIL**: 11 of 21 rows pass; every row within 1.1 %, except the censored 0.999 row |
| D1 | defect verification | **confirmed** in the script; **not present** in the published Fig. 5a |
| V1 | validation | **pass** on time to pH 12; the trajectory after pH 10 is not reproduced (pH RMSE 1.0) |

Reproduction and validation are reported separately and not pooled (tolerances.yaml pass_rule).

### R1: WDE vs current density, 1 M KOH, rebuilt from the raw titration sheets

Our values use the paper's equations 3 to 10 with nominal I = j·A, t_CP = 3600 s, c_HCl = 0.1 M,
V_tank = 90 mL, and V_titrate from each sheet. The mean pools every (V0, V1/V2) pair of every run
at that current density, the aggregation fixed in `reproduce.py` before the run.

| j / mA cm-2 | Fig. 3a WDE | Fig. 3a sd | ours (pooled) | deviation | limit | pairs | status | ours, mean of run means |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 25 | 0.63847 | 0.03448 | 0.63054 | -0.00792 | 0.00862 | 44 | pass | 0.63109 |
| 50 | 0.82888 | 0.03030 | 0.82325 | -0.00562 | 0.00757 | 39 | pass | 0.82639 |
| 100 | 0.93285 | 0.01184 | 0.93033 | -0.00252 | 0.00296 | 39 | pass | 0.92982 |
| 150 | 0.95867 | 0.00750 | 0.95759 | -0.00108 | 0.00188 | 44 | pass | 0.95800 |
| 200 | 0.96738 | 0.00683 | 0.96561 | -0.00177 | 0.00171 | 36 | **fail** | 0.96666 |
| 250 | 0.97802 | 0.00459 | 0.97818 | +0.00016 | 0.00115 | 33 | pass | 0.97775 |

Three runs (dates) per current density. Plot: `figures/r1-wde-vs-current-density.svg`.

**Deviations and explanations**

1. **Ours is lower at five of six current densities.** This matches what was seen before the
   freeze. The authors' own calculation for one sheet (20241002, 200 mA/cm2) is reproduced by our
   equations only with a common factor 0.98774 on the co-ion amounts. That factor is equivalent
   to any one of:
   - a titrant 1.2 % weaker than 0.1 M;
   - a tank about 1.1 mL smaller than 90 mL;
   - a passed charge 1.2 % larger than j·A·3600 s.

   The paper states none of these, so we keep the nominal values. At 200 mA/cm2 the factor
   accounts for about 0.0004 of the 0.0018 deviation.
2. **Aggregation.** With the mean of the three run means instead of the pooled pairs, 200 mA/cm2
   is within the limit (−0.00072). We do not switch: the pooled rule was fixed before the run, and
   choosing the aggregation that passes would make the check meaningless. Pooled and mean-of-means
   differ because runs contribute different numbers of pairs (9 to 20).
3. **Raw-data irregularities**, as used:
   - 20241007 j100 states 10 mL of electrolyte; 90 mL was used.
   - 20241007 j50 has blank volume fields; 1 mL and 90 mL were used.

   With 10 mL taken literally, that run's WDE would be 0.993 instead of 0.937. The other two
   100 mA/cm2 runs give 0.916 and 0.937, so 90 mL is the consistent reading.
4. **Co-ion split.** The HCO3- share of the co-ion current, C_xover, comes out at 0.60 to 0.81
   (pooled per current density, in the run records). The script default is 0.66, and the paper's
   flux ratio is "about 2". Our per-current-density values scatter around that ratio and do not
   follow a trend with current density, consistent with the paper.

**Verdict:** the published series is reproduced from the raw titration sheets to well within its
error bars at every current density. Under the frozen rule (a quarter of the published sd),
200 mA/cm2 misses by 0.00006, so R1 is recorded as FAIL.

### R2: the authors' unmodified model against Fig. 5a, 1 L

200 mA/cm2, 1 M KOH, 5 cm2, C_xover 0.66 and the script's initial concentrations. Neither C_xover
nor the initial concentrations is stated in the paper. Times are the last point of the model's
returned grid, at a 10,000 h horizon. Plot: `figures/r2-time-to-ph12.svg`.

| WDE | Fig. 5a / h | ours / h | deviation | status |
| --- | --- | --- | --- | --- |
| 0.50 | 32.0 | 32.0 | +0.01 % | pass |
| 0.60 | 40.3 | 40.0 | -0.73 % | pass (within 1 h) |
| 0.70 | 53.6 | 53.0 | -1.11 % | pass (within 1 h) |
| 0.75 / 0.80 / 0.85 | 64.0 / 80.0 / 107.0 | 64.0 / 80.0 / 107.0 | +0.01 % | pass |
| 0.90 | 160.0 | 161.0 | +0.64 % | fail |
| 0.91 | 179.0 | 179.0 | +0.01 % | pass |
| 0.92 | 203.0 | 201.0 | -0.98 % | fail |
| 0.93 | 230.0 | 230.0 | +0.01 % | pass |
| 0.94 / 0.95 | 269.0 / 323.0 | 268.0 / 322.0 | -0.36 / -0.30 % | pass (within 1 h) |
| 0.96 / 0.97 | 404.0 / 540.0 | 402.0 / 537.1 | -0.49 / -0.55 % | fail |
| 0.98 | 803.0 | 805.1 | +0.26 % | fail |
| 0.99 / 0.991 / 0.992 | 1616 / 1787 / 2020 | 1611.2 / 1790.2 / 2014.2 | -0.30 / +0.18 / -0.29 % | fail |
| 0.995 / 0.9975 | 3232 / 6464 | 3222.3 / 6446.6 | -0.30 / -0.27 % | fail |
| 0.999 | 16363 | ≥ 10000 (horizon) | censored | pass (censored rule) |

**Deviations and explanations**

1. **Deviations have both signs and are at most 1.1 %**, so they are not a parameter offset.
   - Most published values are whole hours. The rows at 0.99, 0.995 and 0.9975 are exact 1:2:4
     multiples (1616, 3232, 6464), i.e. proportional to 1/(1 − WDE).
   - Our model gives nearly that ratio (1611.2, 3222.3, 6446.6), but not exactly.
   - This points to rounded or scaled published values rather than raw model output. That cannot
     be confirmed from the dataset: the driver script saves no results.
2. **WDE 0.999 needs a horizon above 10,000 h.** With 30,000 h (informational), the model gives
   16,121 h against 16,363 h published (−1.5 %).
3. **The frozen rule is tight on purpose.** One grid interval or 0.1 % was set for identical code,
   which this comparison shows the published sheet is not. Agreement is within 1.1 % throughout,
   below the effect of a ±0.001 change in WDE at 0.99 (±10 %).

**Verdict:** FAIL under the frozen rule. The published Fig. 5a values are not raw output of the
published script at its defaults; they agree with it within 1.1 %.

### D1: is the pH stop event volume-dependent?

**Defect location.** `Model_rBPM_stability_crossover_pHstop.py`, `massBalanceTanks`:
- The state vector is moles: the right-hand side forms `c = n / V_tank`, and the result
  dictionary divides every species by `V_tank`.
- The terminal event computes `pH = -log10(y[4])`, the logarithm of the H+ *amount*.
- At V_tank ≠ 1 L that is pH − log10(V_tank / 1 L).

**Behaviour**, unmodified, at WDE 0.95, 200 mA/cm2, 1 M KOH, C_xover 0.66:

| V_tank | stop / h | pH (14 + log10 c_OH) at stop | pH (−log10 c_H) at stop | concentration-basis time to pH 12 / h (informational) |
| --- | --- | --- | --- | --- |
| 1 L | 322.0 | 12.020 | 12.020 | 322.3 |
| 10 L | 2908.3 | **13.000** | 13.000 | 3223.0 |

**Classification: confirmed.** At 10 L the script stops at pH 13.00, not 12, which is 10 % early.
The H+ state agrees with the OH- state to three decimals, so the second suspicion is rejected:
H+ is resolved despite being far below `atol`.

**The published figure does not carry the defect.**
- The Fig. 5a 10 L column is exactly 10 × the 1 L column in 19 of 21 rows (e.g. 323 → 3230).
  The two exceptions are WDE 0.50 (321 against 320) and the WDE 0.98 entry below.
- The concentration-basis time at 10 L (3223 h) is 10.0 × the 1 L time, matching that scaling.
- The unmodified stop event matches the 10 L column in only 6 of 21 rows, the censored ones.
- So the published 10 L and 100 L values were not produced by running the pH-stop script at
  those volumes. They are consistent with the correct concentration basis.
- The defect matters to anyone who reuses the script at another volume.

**Irregularity in the published sheet.** Fig. 5a, 10 L, WDE 0.98 reads 1616.0. That is the 1 L
value at WDE 0.99. Ten times the 1 L value at 0.98 would be 8030.

### V1: validation against the measured pH of Fig. 3c

The authors' model without stop condition at 20 mL, 0.1 M KOH, 100 mA/cm2, 5 cm2.
- WDE 0.9646 ± 0.0026 is the Fig. 4a value at 0.1 M; the paper quotes 96.5 %.
- C_xover 0.779 ± 0.030 comes from Fig. 4c at 0.1 M.
- Neither input comes from Fig. 3c.

Plot: `figures/v1-ph-validation.svg`.

| Quantity | Measured | Model, nominal | Model envelope (inputs ± 2 sd) |
| --- | --- | --- | --- |
| time to pH 12 | 1.47 h | 1.54 h | 1.30 to 1.87 h |

**Status: pass.** The measured time to the stated threshold lies within the prediction's input
uncertainty. The model needed no fitting to Fig. 3c.

**Not validated: the trajectory after about 2.5 h (pH below about 10).** The pH RMSE over the
measured 5 h is 1.0.
- The measured pH levels off near 8.3 after about 3.5 h; the model keeps falling to about 6.3.
- 8.3 is close to the bicarbonate point, (pK1 + pK2)/2 = 8.35, which would fit CO2 leaving the
  anolyte faster than the model's degassing term allows.
- The caption also reports cell failure within 4 h, so current may have changed during the
  plateau.
- Neither explanation was tested here.
- **Consequence for design use:** the model's time to pH 12 is supported at this condition, but
  the simulated pH below about 10 is not.

## Gaps

- The pressure, temperature and flow inputs of the pH model (degassing coefficient, tank area)
  are script constants with no stated source. They were used as given.
- C_xover for Fig. 5a and the horizon used for its highest-WDE rows are not stated in the paper.
- The 0.1 M to 3 M KOH and CsOH titration values exist only as images. They were not
  transcribed, and V1 uses the published Fig. 4a and 4c values instead.
