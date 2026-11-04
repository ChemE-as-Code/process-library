# Comparison: rBPM WDE reproduction (Prats Vergel et al. 2025, 4TU v1)

- **Reference:** `source.yaml`: 4TU dataset v1, all four files verified by sha256, and the paper
  (Methods eq. 3 to 10, Fig. 3 to 5).
- **Tolerances:** `tolerances.yaml`, frozen in commit 30d35b7. That commit came after the source
  record (de78f02) and before any comparison run. Its header lists what had been seen before the
  freeze. It has not changed since: `git diff 30d35b7 HEAD -- tolerances.yaml` is empty, and
  run 3 records the same sha256 for the file at the freeze and at the run.
- **Runs:** `uv run --isolated benchmarks/reproductions/vermaas-rbpm-wde/reproduce.py`,
  2026-11-04, Python 3.12.15, numpy 2.2.6, scipy 1.15.3. Versions and inputs are in each record.
  - `reruns/2026-11-04-run-3.json` is the **run of record** for this file. It ran from commit
    b4c8b84 with `dirty: false`, after the review of PR #343. All four inputs were downloaded
    into an empty cache (`cache_state`) and passed their sha256. The record holds the sha256 of
    `reproduce.py`, `source.yaml` and `tolerances.yaml`. The figures it wrote are byte-identical
    to the committed ones.
  - `reruns/2026-11-04-run.json` is the first comparison run. By this account, it used the
    script later committed in 640da890, minus the "informational" block and minus the lines of
    `report()` that print it (the D1 concentration-basis t12 and the WDE 0.999 long-horizon
    time). Its `dirty: true` is because the script was not yet committed. The record holds no
    hash of the script, so this rests on this account.
  - `reruns/2026-11-04-run-2.json` is the same script with the informational block and those
    print lines added after the first run, to explain deviations. It is also `dirty: true` and
    names commit 30d35b7, where the script did not yet exist.
  - Every frozen check is identical in the three records. Run 3 adds the reporting described
    under "Changes after review" below.
  - Two earlier attempts stopped before any comparison: one on a scipy build failure under
    Python 3.15, one on a YAML syntax error in `source.yaml`. Neither produced a number.
- **Order of evidence:** `git log -- benchmarks/reproductions/vermaas-rbpm-wde/` shows source
  record, then tolerances, then script and results. The records cannot prove that no
  uncommitted run happened before the freeze; the claim rests on that order and on this account.

## Result

| Check | Kind | Result under the frozen rule (run 3) |
| --- | --- | --- |
| R1 | reproduction of a measured series | **FAIL**: 5 of 6 current densities pass; 200 mA/cm2 misses by 0.00006 (−0.00177 against a limit of 0.00171) |
| R2 | reproduction of a model trajectory | **FAIL**: 11 of 21 rows pass, 10 within the tolerance and WDE 0.999 by the censored rule. The 20 uncensored rows are within 1.11 % at the grid time and within 0.77 % at the event time. In absolute terms the 10 failing rows miss the limit by up to 3.0 times. |
| D1 | defect verification | **confirmed** in the script, on the event state (event-location error 1.8e-15 pH, below the 0.05 band); **not present** in the published Fig. 5a |
| V1 | validation | **pass** on time to pH 12; the trajectory after pH 10 is not reproduced (pH RMSE 1.0) |

Reproduction and validation are reported separately and not pooled (tolerances.yaml pass_rule).

### R1: WDE vs current density, 1 M KOH, rebuilt from the raw titration sheets

Our values use the paper's equations 3 to 10 with nominal I = j·A, t_CP = 3600 s, c_HCl = 0.1 M,
V_tank = 90 mL, and V_titrate from each sheet.

**Aggregation.** The check uses the mean over every (V0, V1/V2) pair of every run at that
current density ("pooled"). The frozen `tolerances.yaml` says only "WDE mean per current
density", so it does not fix how runs are combined. Pooling is how `reproduce.py` was written
before the first run. But the script was first committed together with the results (640da890),
so that order rests on this account, not on a commit. The replicates are the runs (dates),
three per current density. The pairs of one run share readings and are not independent
replicates (`source.yaml` `wde_method.replicates_clarified`). The mean of the run means and the
sd across them are reported beside the check.

| j / mA cm-2 | Fig. 3a WDE | Fig. 3a sd | ours (pooled) | deviation | limit | pairs (per run) | status | ours, mean of run means (deviation) | sd across run means |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 25 | 0.63847 | 0.03448 | 0.63054 | -0.00792 | 0.00862 | 44 (9/15/20) | pass | 0.63109 (-0.00738) | 0.01361 |
| 50 | 0.82888 | 0.03030 | 0.82325 | -0.00562 | 0.00757 | 39 (15/15/9) | pass | 0.82639 (-0.00249) | 0.02328 |
| 100 | 0.93285 | 0.01184 | 0.93033 | -0.00252 | 0.00296 | 39 (12/15/12) | pass | 0.92982 (-0.00303) | 0.01210 |
| 150 | 0.95867 | 0.00750 | 0.95759 | -0.00108 | 0.00188 | 44 (20/15/9) | pass | 0.95800 (-0.00066) | 0.00216 |
| 200 | 0.96738 | 0.00683 | 0.96561 | -0.00177 | 0.00171 | 36 (15/12/9) | **fail** | 0.96666 (-0.00072) | 0.00817 |
| 250 | 0.97802 | 0.00459 | 0.97818 | +0.00016 | 0.00115 | 33 (9/15/9) | pass | 0.97775 (-0.00027) | 0.00439 |

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
   is within the limit (−0.00072). We do not switch. Choosing the aggregation after seeing which
   one passes would make the check meaningless, so R1 stays FAIL under the pooled reading.
   Pooled and mean-of-means differ because runs contribute different numbers of pairs (9 to 20).
   The published series looks like a mean of run means. Scale our 1 − WDE by the pre-freeze
   factor 0.98774, from the run-3 values:
   - the mean of run means is closer to Fig. 3a than the pooled mean at 5 of 6 current
     densities (all but 100 mA/cm2);
   - at 250 mA/cm2 it equals the published 0.97802;
   - at 200 mA/cm2 it gives 0.96707 against the published 0.96738 (pooled: 0.96603);
   - the published sd at 250 and 200 mA/cm2 (0.00459, 0.00683) is close to the mean of the
     per-run sds times the factor (0.00459, 0.00691). The match is weaker at 150 mA/cm2 and
     below;
   - the published 50 mA/cm2 mean, 0.8288783…, has the repeating tail of a mean of three values.

   This is an explanation, not a rule change. A revised tolerance would be a new file with its
   reason (ADR 0030), and none is made here.
3. **Raw-data irregularities**, as used:
   - 20241007 j100 states 10 mL of electrolyte; 90 mL was used.
   - 20241007 j50 has blank volume fields; 1 mL and 90 mL were used.

   With 10 mL taken literally, that run's WDE would be 0.993 instead of 0.937. The other two
   100 mA/cm2 runs give 0.916 and 0.937, so 90 mL is the consistent reading.
4. **Co-ion split.** The HCO3- share of the co-ion current, C_xover, comes out at 0.60 to 0.81
   (pooled per current density, in the run records). The script default is 0.66, and the paper's
   flux ratio is "about 2". Our per-current-density values scatter around that ratio and do not
   follow a trend with current density, consistent with the paper.

**Verdict:** the published series is reproduced from the raw titration sheets within its error
bars at every current density. Under the frozen rule (a quarter of the published sd) with the
pooled aggregation, 200 mA/cm2 misses by 0.00006, so R1 is recorded as FAIL.

**Design data.** Run 3 also compares this rebuild with the design case's own series
(`processes/co2-electrolysis-bpm-1/data/measured/wde-1m-koh.yaml`, written by its
`scripts/adapt_4tu.py`). It checked 60 values: mean, sd, pairs and carbon fraction per current
density, and mean and pairs per run. All agree to the file's rounding (`design_data_consistency`
in the record). The comparison is not a frozen check.

### R2: the authors' unmodified model against Fig. 5a, 1 L

200 mA/cm2, 1 M KOH, 5 cm2, C_xover 0.66 and the script's initial concentrations. Neither C_xover
nor the initial concentrations is stated in the paper. The frozen rule compares the last point
of the model's returned grid ("grid") at a 10,000 h horizon. The solver's event time ("event")
is reported beside it, as the rule asks. The grid time is the last grid point before the event,
so it lies up to one interval (1.0001 h) below the event. Plot: `figures/r2-time-to-ph12.svg`.

| WDE | Fig. 5a / h | grid / h | deviation (grid) | status | event / h | deviation (event) |
| --- | --- | --- | --- | --- | --- | --- |
| 0.50 | 32.0 | 32.003 | +0.01 % | pass | 32.230 | +0.72 % |
| 0.60 | 40.3 | 40.004 | -0.73 % | pass | 40.288 | -0.03 % |
| 0.70 | 53.6 | 53.005 | -1.11 % | pass | 53.717 | +0.22 % |
| 0.75 | 64.0 | 64.006 | +0.01 % | pass | 64.459 | +0.72 % |
| 0.80 | 80.0 | 80.008 | +0.01 % | pass | 80.575 | +0.72 % |
| 0.85 | 107.0 | 107.011 | +0.01 % | pass | 107.434 | +0.41 % |
| 0.90 | 160.0 | 161.016 | +0.64 % | fail | 161.150 | +0.72 % |
| 0.91 | 179.0 | 179.018 | +0.01 % | pass | 179.057 | +0.03 % |
| 0.92 | 203.0 | 201.020 | -0.98 % | fail | 201.440 | -0.77 % |
| 0.93 | 230.0 | 230.023 | +0.01 % | pass | 230.217 | +0.09 % |
| 0.94 | 269.0 | 268.027 | -0.36 % | pass | 268.587 | -0.15 % |
| 0.95 | 323.0 | 322.032 | -0.30 % | pass | 322.306 | -0.21 % |
| 0.96 | 404.0 | 402.040 | -0.49 % | fail | 402.879 | -0.28 % |
| 0.97 | 540.0 | 537.054 | -0.55 % | fail | 537.168 | -0.52 % |
| 0.98 | 803.0 | 805.081 | +0.26 % | fail | 805.782 | +0.35 % |
| 0.99 | 1616 | 1611.161 | -0.30 % | fail | 1611.565 | -0.27 % |
| 0.991 | 1787 | 1790.179 | +0.18 % | fail | 1790.676 | +0.21 % |
| 0.992 | 2020 | 2014.201 | -0.29 % | fail | 2014.481 | -0.27 % |
| 0.995 | 3232 | 3222.322 | -0.30 % | fail | 3223.289 | -0.27 % |
| 0.9975 | 6464 | 6446.645 | -0.27 % | fail | 6447.115 | -0.26 % |
| 0.999 | 16363 | ≥ 10000 (horizon) | censored | pass (censored rule) | none within the horizon | – |

**Deviations and explanations**

1. **The uncensored deviations have both signs and are at most 0.77 % at the event time**
   (1.11 % at the grid time), so they are not a parameter offset.
   - The model's event times follow 1/(1 − WDE) closely: about 16.115 h/(1 − WDE) (for example
     32.230 h at 0.50, 1611.565 h at 0.99).
   - The published values at 0.50, 0.75, 0.80 and 0.90 (32, 64, 80, 160) equal 16 h/(1 − WDE)
     exactly, and ours is +0.72 % above each.
   - The published values at 0.99, 0.995 and 0.9975 (1616, 3232, 6464) equal 16.16 h/(1 − WDE)
     exactly, and ours is −0.27 % below each.
   - So the published values look rounded or scaled, not raw output of the script at its
     defaults. That cannot be confirmed from the dataset: the driver script saves no results.
2. **WDE 0.999 needs a horizon above 10,000 h.** With 30,000 h (informational), the model gives
   16,121 h against 16,363 h published (−1.5 %).
3. **The frozen rule is tight on purpose.** One grid interval or 0.1 % was set for identical
   code, which this comparison shows the published sheet is not.
   - In relative terms the agreement is close: within 0.77 % at the event time for every
     uncensored row, and −1.5 % at WDE 0.999 with the 30,000 h horizon.
   - In absolute terms the misses are not small against the limit. The 10 failing rows miss by
     1.0 to 3.0 times the limit (0.97: 2.95 h against 1.00 h; 0.99 and 0.995: 3.0 times).
   - The relative deviations are below the effect of a ±0.001 change in WDE at 0.99 (±10 %).

**Verdict:** FAIL under the frozen rule. The published Fig. 5a values are not raw output of the
published script at its defaults. They agree with it within 0.77 % at the event time for the
20 uncensored rows, and within 1.5 % at WDE 0.999 with a longer horizon.

### D1: is the pH stop event volume-dependent?

**Defect location.** `Model_rBPM_stability_crossover_pHstop.py`, `massBalanceTanks`:
- The state vector is moles: the right-hand side forms `c = n / V_tank`, and the result
  dictionary divides every species by `V_tank`.
- The terminal event computes `pH = -log10(y[4])`, the logarithm of the H+ *amount*.
- At V_tank ≠ 1 L that is pH − log10(V_tank / 1 L).

**Behaviour**, unmodified, at WDE 0.95, 200 mA/cm2, 1 M KOH, C_xover 0.66. The classification
uses the state at the solver's located event (run 3). The last grid sample of the result
dictionary, which the first two records used, is shown beside it.

| V_tank | event / h | pH (14 + log10 c_OH) at the event | pH (−log10 c_H) at the event | last grid sample / h | pH (OH-) at that sample | sampling error (pH change over the last interval) | concentration-basis time to pH 12 / h (informational) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 L | 322.306 | 12.000 | 12.000 | 322.032 | 12.020 | 0.0725 | 322.305 |
| 10 L | 2908.581 | **13.000** | 13.000 | 2908.291 | 13.000 | 0.0013 | 3223.009 |

**Classification: confirmed.** At 10 L the script stops at pH 13.00, not 12, which is 10 % early.
- **Proviso of the frozen rule.** The band of 0.05 separates the outcomes only if the error in
  locating the stop stays below it.
  - At the located event, the event function (−log10 n_H − 12) is within 1.8e-15 pH of zero at
    both volumes.
  - At 1 L the event time agrees with the concentration-basis crossing of the model without the
    stop to 0.002 h.
- **Grid samples.** On the last grid samples the proviso fails at 1 L: the sampling error of
  0.0725 pH is larger than the band. The script reports that reading as `unresolved`. So the
  "confirmed" of the first two records was right in substance, but the reading they used could
  not support it.
- **H+ state.** At 1 L it agrees with the OH- state to better than 1e-10 pH at the event, so
  the second suspicion is rejected: H+ is resolved although it is far below `atol`.

**The published figure does not carry the defect.**
- In the Fig. 5a source-data sheet, the 10 L column is exactly 10 × the 1 L column in 19 of 21
  rows (e.g. 323 → 3230). The two exceptions:
  - WDE 0.50 reads 321 against 10 × 32 = 320, and its 100 L cell (3210) follows the 10 L cell;
  - WDE 0.98, below.
- The concentration-basis time at 10 L (3223 h) is 10.0 × the 1 L time, matching that scaling.
- The unmodified stop event matches the 10 L column in only 6 of 21 rows, the censored ones.
- So the published 10 L and 100 L values were not produced by running the pH-stop script at
  those volumes. They are consistent with the correct concentration basis.
- The defect matters to anyone who reuses the script at another volume.

**Irregularity in the published sheet.**
- In the source-data sheet, the Fig5a 10 L cell at WDE 0.98 reads 1616. That is the 1 L value
  at WDE 0.99; ten times the 1 L value at 0.98 would be 8030.
- In the same row the 1 L (803) and 100 L (80300 = 100 × 803) cells agree with each other, so
  one cell of the sheet looks inconsistent.
- We have not checked whether the plotted Fig. 5a point shows the same value, and we do not know
  the cause.

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

The V1 reason in the frozen `tolerances.yaml` says "a different effective WDE over 4 h". The
measured record is 5 h long (0.0003 to 5.0003 h); the 4 h is the caption's failure time. The
frozen file is not edited for this. The wording has no effect on the rule, which uses the
measured times as they are.

## Gaps

- The pressure, temperature and flow inputs of the pH model (degassing coefficient, tank area)
  are script constants with no stated source. They were used as given.
- C_xover for Fig. 5a and the horizon used for its highest-WDE rows are not stated in the paper.
- The 0.1 M to 3 M KOH and CsOH titration values exist only as images. They were not
  transcribed, and V1 uses the published Fig. 4a and 4c values instead.

## Changes after review (PR #343), 2026-11-04

The review of PR #343 found gaps between the frozen rules and what the script reported, and
statements in this file that the evidence did not support. `tolerances.yaml` is unchanged. No
verdict rule was changed; every frozen check gives the same result in run 3 as in runs 1 and 2.
What changed:

- **R2 event time.** The frozen R2 rule asks for the event time "reported beside" the grid time.
  The first two records did not report it, because the authors' result dictionary drops it.
  `reproduce.py` now keeps the solver's returned object through a thin wrapper around
  `scipy.integrate.solve_ivp`, inside the isolated runner only; the authors' module is
  unmodified. The grid time still decides pass or fail. The earlier reading "at most 1.1 %"
  rested on grid times, which lie up to one interval below the event. Recomputed from the event
  times, the uncensored rows are within 0.77 %, and rows shown before as +0.01 % are +0.03 to
  +0.72 %.
- **D1 on the event state, with the proviso applied.** The first two records classified on the
  last grid sample. Its sampling error at 1 L (0.0725 pH) is above the 0.05 band, so the
  rule's proviso ("provided that error stays below the band") failed for that reading. D1 now
  classifies on the located event state and reports the event-location error and the
  grid-sample reading beside it. The classification is unchanged ("confirmed"); the grid-sample
  reading alone would be "unresolved".
- **R1 wording.** The earlier text said the pooled aggregation was "fixed before the run". The
  frozen file does not fix it, and the script was committed only with the results. The text now
  says so. R1 stays FAIL under the pooled reading. The mean of run means, the sd across run
  means and the number of runs are reported beside it, with the evidence that the published
  series is a mean of run means. `source.yaml` gained a dated clarification that the runs, not
  the pairs, are the replicates.
- **R2 summary wording.** "Within 1.1 % throughout" dropped the censored 0.999 row. It is now
  qualified, and the misses of the absolute limit (up to 3.0 times) are stated.
- **D1 irregularity wording.** The Fig5a WDE 0.98 entry is described as an inconsistent cell of
  the source-data sheet, with the 100 L cell (80300) that points to it, not as a transcription
  error. The WDE 0.50 row is added. Both are in `source.yaml` irregularities.
- **Run provenance.** The account of run 1 now names the lines of `report()` that it also
  lacked. Run 3 is from a clean commit with fresh downloads. The script now:
  - records the sha256 of `reproduce.py`, `source.yaml` and `tolerances.yaml`, the freeze
    commit, whether `tolerances.yaml` equals its frozen content, and the cache state;
  - takes the dirty state before it writes figures;
  - writes no record from a dirty tree unless `--allow-dirty` is given;
  - extracts the verified zips fresh on every run;
  - downloads to `.part` files that are renamed only after the sha256 check.
- **Design-data consistency.** ADR 0032 said the benchmark records that the two raw-data parsers
  agree; it did not. Run 3 now compares the R1 rebuild with the design data file and records
  the result.
- **V1 wording.** The note above on "over 4 h" in the frozen V1 reason is new.
