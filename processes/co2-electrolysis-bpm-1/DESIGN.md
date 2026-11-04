# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.

## D-001 Scope of the concept stage: the measured bench cell first (2026-11-04)
Decision: The folder starts as the measured reference cell of Prats Vergel et al. (2025):
- its configuration (process/design-basis.yaml, capacity.reference_cell);
- the WDE series in 1 M KOH (data/measured/wde-1m-koh.yaml);
- a cross-section (figures/cell-cross-section.svg).

The pilot-skid duty, the two skid designs and the LCA come later (#330, #331, tracker core#136).

Reason: issue #329 asks for the measured case before the model is generalised. The later steps
take their cell performance from these data.

Rejected:
- Fixing a pilot-skid duty now. It would be a number without a basis before the dynamic and
  sizing tools exist (core#138, core#139).

Assumptions: none beyond the paper's stated configuration.

## D-002 WDE from the raw titration sheets with the paper's equations (2026-11-04)
Decision: scripts/adapt_4tu.py evaluates every 1 M KOH sheet of the current-density study.
- Raw data: the 4TU raw-data zip, pinned by sha256.
- Equations: Methods eq. 3 to 10. K+ lost = (V0 − V2)·c_HCl·V_tank/V_titrate; carbon gained =
  (V2 − V1)·c_HCl·V_tank/V_titrate; WDE = 1 − F·(n_K + n_C)/(j·A·t_CP).
- Constants: c_HCl = 0.1 M, V_tank = 90 mL, t_CP = 3600 s, A = 5 cm2.
- Pairing: every "before" titration (V0) is paired with every "after" pair (V1, V2) of a sheet,
  as the authors' sheets do.
- Aggregation: pooled over the three runs at each current density.
  - The replicates are the three runs (dates).
  - The pairs of one run share their V0 and V1/V2 readings, so `n_pairs` is not a count of
    independent replicates. The pooled sd (over pairs) is not a run-to-run sd.
  - The per-run means are listed in the data file. A use that needs run-to-run scatter takes it
    from those three means (clarified 2026-11-04, review of PR #343).

Two sheets deviate in their headers, and the nominal values are used. 20241007 j100 states 10 mL
of electrolyte, and 20241007 j50 leaves the field blank; 90 mL and 1 mL are used, and the data
file notes both.

Reason: the raw sheets are the measured data. The published figure values are a result and
belong to the held-out reproduction.

Rejected:
- Taking the published Fig. 3a values as design data. They are results to be reproduced, not
  inputs (ADR 0032).
- Applying the 1.2 % factor the authors' own sheet calculation implies. The paper does not
  state it, and the reproduction reports it.

Assumptions:
- Nominal titrant strength, tank volume and run time. The paper states them; there are no
  per-run measurements of them.

## D-003 Stability criterion: anolyte pH 12 as a stated threshold (2026-11-04)
Decision: The anolyte is "stable" while its pH stays above 12, the authors' criterion. It is
reported as time to that threshold, never as a predicted corrosion onset of the Ni anode.

Reason: The paper defines stability by that pH and links it to Ni corrosion. The dataset holds
no corrosion measurement.

Rejected:
- Calling the threshold time a corrosion lifetime.

Assumptions:
- pH 12 is adequate for a Ni anode (ASSUMED, after the authors). #330 states the threshold
  used for the skid.

## D-004 No process/cells.yaml until the cell balance has measured inputs (2026-11-04)
Decision: The cell balance (`cheme process cell`, schema cheme/electrochemical-cells/v1) is not
written yet.
- It needs a Faradaic efficiency and a cell voltage.
- Those come from the GC, mass-flow and chronopotentiometry raw data, whose processing is
  core#137.

Reason: the v1 contract refuses a cell without them. Writing round values from the paper's text
would present unprocessed estimates as design data.

Rejected:
- A cells.yaml with ASSUMED FE and voltage now. It would be replaced as soon as #137 lands and
  would invite use in between.

Assumptions: none.

## D-005 The measured series from the raw CP, MFM, GC and titration files (2026-11-04)
Decision: `scripts/adapt_4tu.py` writes `experiments/electrochemistry/rbpm-1m-koh.yaml`
(schema cheme/electrochemical-measurements/v1). Core's `cheme experiments electrochem` computes
the voltage, Faradaic efficiencies (FE) and WDE per point from it.
- Runs: the 18 titration sheets of the current-density study (D-002), three per current density
  from 25 to 250 mA/cm2. Each is paired with the CP, MFM and GC files of the same date and current
  density. The replicates are these runs.
- Window: the second half of the 1 h run, t = 1800-3600 s after the current start.
  - The voltage is the mean of the chronopotentiometry samples in it.
  - The gas is the mean of GC injections 8-13 (t = 1896-3476 s).
- Voltage sign: the CP files give the cell voltage and the current negative (the
  potentiostat's sign for a cathodic working electrode). The file states the voltage positive,
  U = -U_file. It is the terminal voltage, not
  iR-corrected (voltage_basis: cell).
- FE basis (SI Note 5, eq. 37-39):
  - FE_i = z F P Q_gas c_i / (R T I), with P = 101325 Pa.
  - The meter is calibrated for CO2. The mixture flow is Q_gas = Q_MFM C_mix / C_CO2 with
    1 / C_mix = sum c_i / C_i. The factors are 0.74 (CO2), 1.00 (CO), 1.01 (H2) and 0.79 (H2O),
    with the gas saturated with water.
  - Q_MFM is the mean of the 30 s of readings before each injection, as the SI says.
  - c_i are the GC mole fractions (ppm, GC ReadMe). The CO2 share is the balance.
  - Each replicate's `outlet_flow` is Q_gas (factor 1.006-1.043), and its fractions are the
    flow-weighted means of the injections. So the FE core computes is the mean of the
    injections' FE. The meter reading and the factor are in each replicate's `source`.
- Injection times: one export of the GC files has no injection times (20240926-20241016). The
  injections are therefore located in the MFM record. Each one leaves a step there (more than
  4 sccm, from the sample drawn) every 303-330 s, the first at the current start (GC ReadMe:
  injection 2 at t = 0). Where the GC export has clock times (20241022 onwards), the steps lie
  2-3 s after them.
- Current: the nominal j A for FE and WDE, as in D-002. The CP current is 1.1-1.6 % above it, so
  the FE at the measured current would be lower by that share.
- WDE: the titration of a replicate is the mean of the sheet's V0 readings and of its (V1, V2)
  pairs. WDE is linear in the volumes, so it equals the per-run mean over every V0 x pair of
  `data/measured/wde-1m-koh.yaml`; the script refuses any difference. The point mean is the mean
  of the three runs, and the sd is from run to run (D-002). The pooled means in
  wde-1m-koh.yaml weight the runs by their pairs and differ by up to 0.003.

The FE basis finding. The GC sheets of the first export carry an FE column: CO about 54 % for
20241007 j100 (GC_13). The raw data give 31.2 % there, a factor 1.73. The column is no measured
FE of the run:
- It is 2 F c_CO Q / (V_m I) with V_m = 22.4 L/mol, exactly.
- I is a fixed 0.25 A (0.05 A for injections 1-3) and Q a fixed 47.5 sccm (48.4), with no
  mixture correction ("MFM deviation" 1). These are the same in every file, whatever the
  current density.
- 0.25 A is the current of the 50 mA/cm2 runs only. At 100 mA/cm2 the run current is 0.5 A
  (CP file 0.507 A). The mixture flow in the window is 54.9 sccm (meter reading 53.9 sccm x
  1.018). Column / ours = (0.5 / 0.25) x (47.5 / 54.9) x (22.414 / 22.4) = 1.73. At 250 mA/cm2
  the column reads 129-166 % CO alone (injections 4-13).
- The first hand estimate (about 29 %, with 52 sccm and 273.15 K) was right in kind: 29.6 %
  with that flow. The rest is the meter reading in the window, 30 s before each injection
  (53.9 sccm), and the mixture factor.
- The pressure and the conversion equations are therefore those of the SI, with T = 273.15 K
  as in the sheet's 22.4 L/mol. The GC column is not used. The text of the paper (FE CO of 30-40 % with K+) agrees with the
  calculation, not with the column. That is a check of the basis only, not a comparison of
  results (ADR 0032).

Results (mean +- sd (n), cathode FE sum, `cheme experiments electrochem`):

| j / mA cm-2 | U / V | FE CO | FE H2 | FE sum | WDE | HCO3- share of co-ions |
|---|---|---|---|---|---|---|
| 25 | 3.09 +- 0.02 (3) | 0.404 +- 0.097 (3) | 0.528 +- 0.078 (3) | 0.932 +- 0.020 (3) | 0.631 +- 0.014 (3) | 0.72 +- 0.13 (3) |
| 50 | 3.42 +- 0.01 (3) | 0.349 +- 0.041 (3) | 0.594 +- 0.041 (3) | 0.943 +- 0.014 (3) | 0.826 +- 0.023 (3) | 0.63 +- 0.13 (3) |
| 100 | 4.03 +- 0.06 (3) | 0.301 +- 0.068 (3) | 0.660 +- 0.112 (3) | 0.961 +- 0.046 (3) | 0.930 +- 0.012 (3) | 0.69 +- 0.09 (3) |
| 150 | 4.62 +- 0.14 (3) | 0.375 +- 0.009 (3) | 0.596 +- 0.048 (3) | 0.971 +- 0.046 (3) | 0.958 +- 0.002 (3) | 0.80 +- 0.04 (3) |
| 200 | 5.37 +- 0.15 (3) | 0.383 +- 0.040 (2) | 0.560 +- 0.038 (2) | 0.943 +- 0.002 (2) | 0.967 +- 0.008 (3) | 0.67 +- 0.08 (3) |
| 250 | 7.58 +- 0.80 (3) | 0.353 +- 0.030 (3) | 0.622 +- 0.038 (3) | 0.974 +- 0.058 (3) | 0.978 +- 0.004 (3) | 0.70 +- 0.10 (3) |

The findings: one info, `electrochem-validity`, that the temperature range is derived from the
assumed cell temperature. There is no `fe-sum-low` or `fe-sum-high`.
- The cathode FE sums are 0.93-0.97. The rest, 3-7 % of the current, is no measured product.
  Liquid products (formate) are not analysed, and the instruments' calibration error is not
  propagated. A replicate's sum lies between 0.917 and 1.042; the three above 1 are of the
  second GC export (20241023 j100, 20241024 j150, 20241025 j250), inside core's 1.05.
- No carbon balance closes: the GC does not measure CO2. The conversion of the CO2 fed to
  products is 0.6-6.6 %, and the carbon to the anolyte 0.5-1.1 % of the CO2 fed.
- The window barely moves the FE (less than 0.01 against 600-3600 s or 2700-3600 s). The
  voltage rises over the hour, most at 250 mA/cm2 (7.22 V over 600-3600 s, 7.58 V over the
  window, 7.87 V over 2700-3600 s), where it also scatters most (sd 0.80 V). The window is stated with every value.

Figures: `figures/polarisation.svg`, `faradaic-efficiency.svg`,
`partial-current-density.svg` and `water-dissociation-efficiency.svg`, from `cheme experiments
electrochem ... --plot figures/`.

Irregularities of the raw data, recorded and not corrected:
- 20241024 j200 has no MFM file, so it has no FE (the point at 200 mA/cm2 has two FE replicates).
- The second GC export (20241022 onwards) gives the amounts without a unit. They are read as ppm
  (GC ReadMe), and they are of the same order as the first export's ppm.
- 20241022 j25: the MFM file records overnight. Its first hour is used.
- 25 more 1 M KOH files belong to no run of the study. They are listed in the header of the
  measurement file: a second campaign (Jan to Feb 2025, 25-200 mA/cm2, CP, MFM and GC without a
  titration), 20241023 j250 (CP and GC; the run stops at 2845 s, at -9.5 V), and two MFM files
  whose names have no day or spell the electrolyte 1KOH.

Reason: the raw files are the measured data (ADR 0032). The SI states the authors' conversion,
and the raw files carry everything it needs, so no correction factor is invented. The second
half of the run keeps the start-up transient out of both voltage and gas. The FE barely depends
on it; the voltage depends on it, and the window is stated with the value.

Rejected:
- Taking the GC sheets' FE column as `faradaic_efficiency`. It is a template with a fixed
  current and flow (above), not the run's FE.
- A single meter correction factor for the file (core's `flow_correction`). The mixture factor
  changes with the composition, from 1.006 at 25 to 1.042 at 250 mA/cm2.
- Adding the second campaign's runs as FE replicates. A replicate here holds the voltage, FE
  and WDE of one run, and those runs have no titration. They could be a separate FE series
  later.
- The measured current in place of the nominal one. Core takes one current per point for FE
  and WDE, and the WDE of D-002 is on the nominal current.

Assumptions:
- The cell temperature is 25 °C (ASSUMED, room temperature). The paper and the dataset state
  none. It enters the water vapour share of the gas at saturation (3.13 %, IAPWS-95, about
  0.3 % in Q_gas) and the validity range.
- The meter's sccm are at 0 °C and 101.325 kPa. SI eq. 37 gives the pressure, and the authors'
  own sheet arithmetic uses 22.4 L/mol. The meter's reference temperature is not stated; at
  20 °C every FE would be 6.8 % lower.
- The GC fractions are of the gas that passes the meter (wet basis), as in eq. 39.
