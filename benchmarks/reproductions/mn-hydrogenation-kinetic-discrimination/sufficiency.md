# Data sufficiency: Mn-CNP hydrogenation kinetic models (#341)

P3 case: we checked what data exist before choosing the scope. Checked 2026-11-04.

## What exists

| Item | Where | Licence | Usable for |
| --- | --- | --- | --- |
| Article, version of record (ChemCatChem 2021, 13, 4886) | DOI 10.1002/cctc.202101140; PMC9291086; TU Delft repository | CC BY 4.0 | model definitions (Eqs. 8-20), Table 2 statistics, Table 3 coefficients, Figure 7 kinetics |
| Supporting Information, 30 pages | PMC open-data bucket, `CCTC-13-4886-s001.pdf` (pinned by sha256 in `source.yaml`) | listed under the article's CC BY record; no separate licence line | the full run table and every regression output |
| SI Table S1 | SI page 4 | as above | 30 runs: temperature, catalyst and base concentration, H2 pressure, run time, average rate, yield |
| SI Table S2 | SI page 5 | as above | the transformed regressors the authors fitted (1/T, p, ln cat, ln base) |
| SI Tables S3-S5, S7-S9, S13-S15, S20 | SI pages 7-24 | as above | coefficients with standard errors, RMSE, R2, PRESS, ANOVA (incl. pure error from the centre replicates) for models I to IV |
| SI Tables S6, S10, S16, S21 | SI pages 9-25 | as above | fitted values per run for models I to IV |
| SI Tables S23-S26 | SI pages 28-29 | as above | separate initial-rate runs: Arrhenius points at 50 and 200 ppm catalyst, base and catalyst order series |
| Separate data deposit | none found (4TU.ResearchData, Zenodo, author pages) | - | - |

The publisher's site refuses scripted downloads (HTTP 403) and the PMC web page puts a browser
challenge in front of files. The PMC open-data bucket serves both PDFs directly, with md5
values in its index; `run.py` uses that URL.

## What is missing

- **Time-resolved data.** H2 uptake was logged for every run, but the curves are not
  published. Each design run gives one number, the average rate over its run time. The
  article says model IV's x6 is the time each run took to finish according to the H2
  uptake; the Table S1 times look mixed (shared batch stop times for some groups, different
  near-completion times for the high-yield 100 °C runs). Model IV uses that run time as a
  regressor, so its "deactivation" term cannot be separated from how run times were chosen
  (the authors report high variance inflation for time and substrate).
- **Near-complete runs.** Six runs (7, 10, 13, 14, 15, 21) reached 87-95 % yield. Their
  average rates are only lower bounds on the rate, but the source regressed on them (five
  each in models II and III, four in model IV). We keep the source's data sets.
- **Substrate concentration was not varied.** Every run used 5 mmol in about 4.0 mL
  (1.255 mol/L nominal, range 1.20-1.29 mol/L, reconstructed per run in `inputs.yaml`). Model IV is first order in
  substrate, models II and III have no substrate term; the data cannot tell these apart.
- **End-of-run substrate concentration** (regressor x5 of model IV) was measured by GC in
  the source but is not tabulated. We reconstruct it from rate, time and yield
  (S_end = rate * time * (1 - Y) / Y), which assumes a 100 % mass balance. The SI reports
  mass balances within 90-110 %; at 88-93 % yield a 10 % error in the balance moves
  ln S_end by +0.6 to +0.9, or makes it undefined downwards (`inputs.yaml`). The model IV
  coefficients still reproduce within 0.12 SE, so the effect on the fit is bounded.
- **Measurement error at low yield.** The only replicate information is the six centre runs
  (yields 30-58 %), pure-error standard deviation 0.211 in ln(rate). No replicates exist at
  the low yields (2-6 %) where models II and III differ most.
- **Mass transfer.** The authors infer gas-liquid mass-transfer limitation at 200 ppm
  catalyst from the initial-rate Arrhenius slopes (51 vs 90 kJ/mol). No kLa or stirring data
  exist, so no mass-transfer model can be added.
- **Temperature.** Table S2 regresses on 1/(T + 274.1 K), not 1/(T + 273.15 K); the SI does
  not explain the 0.95 K offset. We use the tabulated values.

## Achievable scope (decided from the above)

1. **Reproduction: achievable in full.** The raw run table and every reported regression
   result are published, so the four regression models can be refitted and compared
   coefficient by coefficient, and the initial-rate kinetics (Figure 7) can be refitted from
   the tabulated points.
2. **Independent validation: not achievable.** No data from another laboratory or a second
   catalyst batch exist. The initial-rate runs are separate experiments by the same
   authors; the article itself compares them with the regression coefficients, and we
   restate that comparison, but it is not independent validation of the regression models.
3. **Design extension: achievable with stated limits.** With the refitted parameter
   covariances and the pure-error standard deviation, the competing predictions and their
   uncertainty can be propagated to any condition inside the studied box. Model IV can be
   used only where its time term means something: run times up to 7.5 h (beyond that its
   yield falls, which a batch cannot show) and (temperature, run time) pairs inside the
   design's own support. Substrate concentration can be changed only as a labelled
   extrapolation.
