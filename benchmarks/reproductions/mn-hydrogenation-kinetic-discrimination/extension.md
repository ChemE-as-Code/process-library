# Design extension: a discriminating experiment for models II, III and IV

**HYPOTHETICAL design extension (not validated).** Nothing here has been measured. It uses
our refits of the published models (`comparison.md`), their parameter covariances, and the
measured pure-error standard deviation. Numbers are in `results/comparison.json` under
`extension`; the figure is `results/fig2_discrimination.svg`.

## Question

Which feasible batch run most clearly tells the three competing models apart?

- **Model II** (stepwise, 7 terms): ln(rate) with T x ln(cat) and p x ln(base) interaction
  terms and a quadratic base term. Its apparent activation energy rises with catalyst
  concentration (33 to 52 kJ/mol).
- **Model III** (no interactions, 5 terms): the same without the interaction terms.
- **Model IV** (nonlinear, built on formal kinetics; the abstract calls it the "chemical
  logic" model): first order in substrate, power law in catalyst and base, plus a run-time
  term b6 = -3.7e-5 1/s. The authors call b6 the rate constant for catalyst activation; its
  negative fitted sign means the activity decays with run time.

All three fit the 30 design runs about equally well. They differ in structure, and the
question is where that difference is large compared with what one run can resolve.

## Method

- Response of a proposed run: y = ln(average rate) = ln(alcohol formed / run time),
  mol/(L h), the quantity the models were fitted to. Models II and III predict y directly
  and do not depend on run time; model IV predicts it from its fitted relation with the
  end-of-run substrate and the run time.
- Separation of a pair of models at one run (Buzzi-Ferraris type):
  D = (y_i - y_j)^2 / (2 sigma^2 + s_i^2 + s_j^2). Here sigma = 0.211 is the measured
  pure-error standard deviation of y (six centre runs, SI Table S4; recomputed: 0.2113) and
  s_i is the parameter-uncertainty standard deviation of model i's prediction (from our
  refit covariance; linear propagation, checked by 4000 Monte Carlo draws: within 1.4 %).
  D = 4 means the predictions differ by two combined standard deviations (threshold,
  `inputs.yaml`).
- Search: 70,875 grid conditions inside the studied box (30-100 °C, 10-50 bar,
  0.0625-0.25 mmol/L Mn, 0.0625-12.5 mmol/L KOtBu, run time 2-24 h, substrate at the
  design value 1.255 mol/L). A condition is feasible only if:
  1. every model predicts a final yield of 2-90 % (measurable, not complete);
  2. run time is at most 7.5 h, because model IV as fitted predicts a yield that peaks at
     t = -1/b6 = 7.47 h and then falls, which no batch run can show;
  3. the (temperature, run time) pair lies inside the convex hull of the 30 design runs
     (temperature set points of SI Table S1),
     because run time was confounded with temperature in the design (30 °C runs lasted
     20-28 h, 65 °C runs 8-16 h, 100 °C runs 1.7-22 h) and model IV uses run time as a
     regressor.
  7,357 conditions are feasible.

Constraints 2 and 3 and the finer run-time grid were added after the first run of the
search (2026-11-04), when the first answer turned out to rest on model IV's falling yield
and on a (T, t) pair the design never visited. Both answers are kept as sensitivities.

## Result

**No feasible grid point (70,875-point grid) separates all three models in a single run.**
The best single run (100 °C, 30 bar, 0.25 mmol/L Mn, 0.091 mmol/L KOtBu, 7 h) reaches D = 1.66 for II vs III, the
hardest pair; no feasible grid point reaches D = 4 for all pairs. Up to 12 replicates of
the best single run do not bring all three pairs to D >= 4, because replicates shrink only
the measurement term. Even infinitely many replicates of any feasible grid point give
D_min <= 3.2 (3.17 at the best single run), because parameter uncertainty remains. At run A below, the
II-III separation is capped at D = 6.4 by parameter uncertainty, so D >= 9 is out of reach
there.

**Proposed experiment: two runs at 100 °C and 10 bar H2.**

| | Run A: tests the interaction terms (II vs III) | Run B: tests the run-time term (IV vs II, III) |
| --- | --- | --- |
| Temperature | 100 °C | 100 °C |
| H2 pressure | 10 bar | 10 bar |
| Mn-CNP | 0.25 mmol/L (about 200 ppm, S/Mn 5000) | 0.099 mmol/L (about 80 ppm) |
| KOtBu | 0.133 mmol/L (about 0.01 mol% of substrate) | 12.5 mmol/L (1 mol%) |
| Run time | 7 h | 2 h |
| Model II: y, 95 % band (parameters + measurement) | -4.56 [-5.27, -3.85]; 0.0105 mol/(L h); yield 5.8 % | -3.62 [-4.23, -3.01]; 0.027 mol/(L h); yield 4.3 % |
| Model III | -5.61 [-6.31, -4.90]; 0.0037 mol/(L h); yield 2.0 % | -3.45 [-4.07, -2.83]; 0.032 mol/(L h); yield 5.1 % |
| Model IV | -4.50 [-5.28, -3.72]; 0.0111 mol/(L h); yield 6.2 % | -1.08 [-1.64, -0.51]; 0.34 mol/(L h); yield 54 % |
| D (II, III) | **4.23** | 0.15 |
| D (II, IV) | 0.01 | **36.1** |
| D (III, IV) | 4.26 | **30.7** |

Taking each pair's better run, the two-run design separates every pair with D >= 4.23.

### Physical reading

- **Run A** sits where model II's interaction terms matter most: high temperature and
  high catalyst (its T x ln(cat) term raises the apparent activation energy at high
  catalyst), low pressure and low base (its p x ln(base) term). Model II predicts a rate
  2.9 times model III's. The base level, 0.133 mmol/L, lies between the design levels 0.0625
  and 6.28 mmol/L, where neither model has data and the two quadratic base terms bend
  differently. This is inside the studied range but in a gap of the design. By leverage it
  is a hidden extrapolation: h = 0.50 for model III against a largest design leverage of
  0.45 (run 29), and 0.571 for model II against 0.569. For model IV it is inside (0.36
  against 0.54).
- **Run B** asks whether the average rate depends on how long the run lasts. Models II and
  III say no: average rates from 2 h and 20 h runs are the same. Model IV says the catalyst
  loses activity with a time constant of about 7.5 h, so a 2 h run at high base should give
  an average rate 11 to 13 times the ones models II and III predict (54 % vs 4-5 % yield).
  A 2 h run at 100 °C is within the design's support (run 13 lasted 1.67 h), and its
  leverage is below each model's largest design leverage (model IV 0.53 against 0.54).
- **Reaction times.** At run A's condition models II and III predict 50 % yield after 60 h
  and 171 h, if read as constant rates. Model IV as fitted never reaches 50 % (peak 6.2 % at
  7.5 h); in its refitted integrated reading (below) yield levels off at 4.1 % within the
  first hour. A long run at run A's
  condition would therefore also separate the models, but not inside the measurable,
  in-support window.

### What the result depends on

- **Measurement resolution at low yield.** Run A's predicted yields are 2.0-6.2 %, and the
  2 % lower bound of the measurable window is active for model III. The resolution sigma =
  0.21 comes from replicates at 30-58 % yield. If it were 0.4 at 2-6 % yield, D for II vs
  III at run A would fall to about 2.2. Before running A, replicate GC yields at
  low conversion (or follow H2 uptake, about 0.1-0.3 mmol per vial) to check sigma.
- **Model IV reading.** The coefficients were fitted to the average-rate form, which treats
  the run time as a regressor. Inserted unchanged into the integrated rate law of the
  source's Eq. 14 (dP/dt = g0 exp(b6 t) S), they do not reproduce the data: RMSE 1.25 in y
  against 0.54 for the as-fitted form (both root mean square over the 24 runs, max |r| 2.24
  against 1.22). Our earlier sensitivity used them that way; its D values are withdrawn.
  Refitted by nonlinear least squares to the same 24 runs, the integrated form fits better
  (RMSE 0.36, max |r| 0.81), but only by letting the catalyst die within about 0.3 h
  (b6 = -9.7e-4 1/s). Every run is then read as finished long before it was stopped, the
  final yield fixes only g0/|k|, and the intercept and b6 are not separately identifiable
  (correlation -1.00, intercept SE about 1e6). Linear prediction variances are then
  meaningless, so we compute no D values for this reading and give point predictions only:
  4.1 % yield at run A (between models III and II, 2.0 and 5.8 %), 58 % at run B (models II
  and III 4-5 %), 5.5 % at the best single run. Run B therefore still separates model IV
  from models II and III under either reading; run A tests only II against III. The fact
  that the refit prefers a catalyst that is dead within the first hour supports the reading
  that the run-time term reflects how run times were chosen, which is what run B tests.
- **Model IV covariance at MATLAB's robust sigma** (0.6572 instead of 0.5765, variance
  x 1.30; `comparison.md` explanation 2): runs A and B, the best single run and the two-run
  D_min of 4.23 are unchanged; run A's D(III, IV) falls from 4.26 to 3.81, and run B still
  separates that pair at D = 28.8.
- **Hidden extrapolation (leverage).** Run A exceeds the largest design leverage for models
  II and III (above); the run-B-type test outside the (T, t) hull below has model IV
  leverage 0.61 against 0.54. The best single run is inside for all three models (0.29-0.31).
- **Without constraint 3** the best single run moves to 30 °C, 20 bar, 0.25 mmol/L Mn,
  12.5 mmol/L KOtBu, 7 h (D = 1.69), a (T, t) pair the design never visited; a
  run-B-type test outside the hull would be 60 °C, 20 bar, 2 h (D 46 and 41).
- **Without constraint 2** the best single run is 100 °C, 20 bar, 0.25 mmol/L Mn,
  0.41 mmol/L KOtBu, 16 h (D = 1.78) and rests on model IV's falling yield.
- **Measurement sigma 0.1 or 0.4** leaves the best single run at 100 °C and 0.25 mmol/L Mn
  with 0.09-0.13 mmol/L KOtBu (D_min 2.6 and 0.76).
- **Existing design runs.** Evaluated the same way (with their own run times, within
  model IV's time limit), the best existing run (run 21) gives D_min = 0.27. The 30 runs
  were not designed to separate these models, and they do not.
- **Mass transfer.** The article infers gas-liquid mass-transfer limitation at 200 ppm
  catalyst from the initial-rate runs. Run A's predicted rates (0.004-0.011 mol/(L h)) are
  60 to 190 times below the fastest design run (0.69 mol/(L h), run 13), so H2 supply is
  unlikely to limit it. Run B under model IV (0.34 mol/(L h)) is within the design's rate
  range, but at 10 bar instead of 50 bar; a mass-transfer limitation there would lower the
  rate and push the result towards models II and III.

## Changed input: half the substrate concentration (extrapolation)

Substrate was not varied in the design, so this is outside the studied range. At run A's
condition with 0.63 mol/L acetophenone instead of 1.255 mol/L:

| | Model II | Model III | Model IV |
| --- | --- | --- | --- |
| Average rate | 0.0105 mol/(L h) (unchanged) | 0.0037 mol/(L h) (unchanged) | 0.0056 mol/(L h) (halved) |
| Yield after 7 h | 11.7 % (doubled) | 4.1 % (doubled) | 6.2 % (unchanged) |

Models II and III have no substrate term (zero order), so the same rate gives twice the
yield. Model IV is first order in substrate, so its rate halves and its yield stays the same.
The pairwise separation changes accordingly: II vs IV rises from D = 0.01 to 1.4, III vs IV
falls from 4.3 to 0.6, II vs III is unchanged (4.2). The substrate order is a real
structural difference between the models, but at this condition halving the substrate
moves model IV's prediction onto model III's, so the change does not help. A substrate
series would need its own design, and any result from it is an extrapolation of all three
models.

The best run allowed one step beyond the studied bounds (120 °C, 0.5 mmol/L Mn, twice the
substrate, 30 bar, 0.091 mmol/L KOtBu, 3 h; extrapolated in temperature, catalyst and
substrate) still reaches only D_min = 3.97 in a single run.

## Status

Hypothetical. No run has been made. The two proposed runs are within the studied box and
the design's (T, t) support. Run A lies in a gap of the base levels and near the
yield-detection floor, and it is a hidden extrapolation by leverage: it exceeds model III's
largest design leverage (0.50 against 0.45) and, marginally, model II's (0.571 against
0.569). A result at run A therefore tests the models where they are least constrained by
data, which is also why they differ there. The models are regressions of average rates, not mechanistic
models, and the separation is computed for them as published. Specialist review (catalysis,
kinetic experiment design): not yet.
