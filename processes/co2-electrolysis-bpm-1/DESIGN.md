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
Superseded by D-005 and D-006 (2026-11-04): core#137 landed, the measured series exists and
`process/cells.yaml` now has the bench cell.

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
  - The gas is the mean of GC injections 8-13. Their located times vary by run: injection 8 at
    t = 1882-1909 s, injection 13 at 3461-3488 s.
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
- The pressure and the conversion equations are therefore those of the SI. T = 273.15 K is
  ASSUMED: its only hint is the sheet's 22.4 L/mol, the constant of the column rejected here
  (Assumptions). The GC column is not used. The text of the paper (FE CO of 30-40 % with K+)
  agrees with the calculation, not with the column. That is a check of the basis only, not a
  comparison of results (ADR 0032).

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
- The cathode FE sums of the points are 0.93-0.97. A replicate's sum lies between 0.917 and
  1.042, inside core's 1.05, and the sums split by GC export:
  - The 12 runs of the first GC export (20240926-20241016) sum to 0.917-0.947, mean 0.937.
    There the rest, 5-8 % of the current, is no measured product: liquid products (formate)
    are not analysed, and the instruments' calibration error is not propagated.
  - The 5 runs of the second export (20241022-20241025) sum to 0.954-1.042, mean 0.998,
    about 6 % above the first. The three sums above 1 are among them (20241023 j100,
    20241024 j150, 20241025 j250). The flow meter reads about 5 % high before the current
    starts in exactly these runs (irregularities below), so these sums are not read as a
    product balance. One second-export replicate sits in each point but P200, where 20241024
    has no MFM file.
- No carbon balance closes: the GC does not measure CO2. The conversion of the CO2 fed to
  products is 0.6-6.6 %, and the carbon to the anolyte 0.5-1.1 % of the CO2 fed. Both rest on
  the 50 sccm inlet stated for every run, which the meter baseline of the second export
  contradicts.
- The window barely moves the point means of the FE (less than 0.01 against 600-3600 s or
  2700-3600 s; at most 0.009, H2 at 250 mA/cm2). Single runs move more, by up to 0.022
  (20241022 j25, CO, 600-3600 s); 20241023 j50, 20241002 j150, 20241014 j250 and 20241025 j250
  move by 0.011-0.020 there. The
  voltage rises over the hour, most at 250 mA/cm2 (7.22 V over 600-3600 s, 7.58 V over the
  window, 7.87 V over 2700-3600 s), where it also scatters most (sd 0.80 V). The window is stated with every value.

Figures: `figures/polarisation.svg`, `faradaic-efficiency.svg`,
`partial-current-density.svg` and `water-dissociation-efficiency.svg`, from `cheme experiments
electrochem ... --plot figures/`.

Irregularities of the raw data, recorded and not corrected:
- 20241024 j200 has no MFM file, so it has no FE (the point at 200 mA/cm2 has two FE replicates).
- The second GC export (20241022 onwards) gives the amounts without a unit. They are read as ppm
  (GC ReadMe), and they are of the same order as the first export's ppm.
- The meter baseline steps up with the second export. Before the current starts (the mean of
  the readings before injection 2) the meter shows the humidified CO2 feed alone. 50 sccm of
  CO2 saturated at 25 °C should read 51.5 sccm on the CO2-calibrated meter (51.6 sccm of gas,
  mixture factor 1.002). The 12 runs of 20240926-20241016 read 51.53-52.24 sccm. The 5 runs of
  20241022-20241025 read 53.74-54.59 sccm, 4-6 % high, and the 2025 files of no run read
  53.8-55.3 sccm, so the step persists. The data do not say why:
  - A meter offset or span change would pass straight into FE = x Q (eq. 37). The five
    replicates' FE would then be about 5 % high; scaled by the baseline ratio their sums would
    be 0.91-0.99, like the first export's.
  - A real rise of the feed would leave the FE as computed. The stated inlet of 50 sccm, and
    with it the CO2 conversion of these runs, would then be wrong.
  - A calibration change of the GC between the exports would raise the sums but not the meter
    baseline. It does not explain the step on its own.
  No correction is applied: the file keeps the readings and the 50 sccm inlet, and each
  replicate's `source` gives its baseline next to the meter reading.
- 20241022 j25: the MFM file records overnight. Its first hour is used.
- 27 more 1 M KOH files belong to no run of the study. They are listed in the header of the
  measurement file:
  - a second campaign (Jan to Feb 2025, 25-200 mA/cm2, CP, MFM and GC without a titration);
  - 20241023 j250 (CP and GC). Its voltage reaches -10.05 V at 2467 s and stays there from
    2502 s to the end of the record at 2845 s, at the full current (1.263 A). That is very
    likely the potentiostat's compliance limit. Its mean over 1800-2845 s is -9.55 V;
  - four files whose names have no day or another electrolyte spelling: Feb_MFM_j150_1MKOH,
    Jan06_MFM_j50_1KOH, and the pair Feb_MFM_j150_11MKOH (in CP-RawData) and
    Feb_CP_j150_11MKOH (in MFM-RawData; it holds a CP record), with folder and kind swapped.
    The doubled 1 marks a repeat file, as the dataset's 2MKOH/22MKOH/222MKOH.

Reason: the raw files are the measured data (ADR 0032). The SI states the authors' conversion,
and the raw files carry everything it needs, so no correction factor is invented. The second
half of the run keeps the start-up transient out of both voltage and gas. The FE barely depends
on it; the voltage depends on it, and the window is stated with the value.

Rejected:
- Taking the GC sheets' FE column as `faradaic_efficiency`. It is a template with a fixed
  current and flow (above), not the run's FE.
- A single meter correction factor for the file (core's `flow_correction`). The mixture factor
  changes with the composition, from 1.006 at 25 to 1.041 at 250 mA/cm2 (point means; 1.006-1.043
  over the replicates).
- Adding the second campaign's runs as FE replicates. A replicate here holds the voltage, FE
  and WDE of one run, and those runs have no titration. They could be a separate FE series
  later.
- The measured current in place of the nominal one. Core takes one current per point for FE
  and WDE, and the WDE of D-002 is on the nominal current.

Assumptions:
- The cell temperature is 25 °C (ASSUMED, room temperature). The paper and the dataset state
  none. It enters the water vapour share of the gas at saturation (3.13 %, IAPWS-95, about
  0.3 % in Q_gas) and the validity range.
- The meter's sccm are at 0 °C (ASSUMED) and 101.325 kPa. SI eq. 37 gives the pressure. The
  meter's reference temperature is not stated; the only hint is the 22.4 L/mol of the authors'
  FE column, which is rejected above as a template, so it is weak evidence. Every FE scales
  with 1 / T: at 20 °C it would be 6.8 % lower, at 25 °C 8.4 % (common normal conditions of
  thermal meters). The point FE sums would then be 0.87-0.91 or 0.85-0.89, and the bench cell's
  FE CO 0.357 or 0.351 instead of 0.383 (D-006). The data file marks the value ASSUMED with the
  same sensitivity.
- The GC fractions are of the gas that passes the meter (wet basis), as in eq. 39.

## D-006 The bench cell at 200 mA/cm2 in process/cells.yaml (2026-11-04)
Decision: `process/cells.yaml` holds one cell, `bench-cell`.
- Performance: `performance: measured` on the series of D-005.
- Operating point: 1 A on 5 cm2, i.e. 200 mA/cm2. The cell is isothermal at 25 °C (ASSUMED,
  D-005).
- Reactions: CO2R (n = 2) is the overall reaction and WS (n = 2) the side reaction. They take
  their current fractions from the measured FE of CO and H2.
- Membrane: a reverse-bias bipolar membrane. The WDE is the measured one. The co-ion split K+
  0.330 / HCO3- 0.670 is the measured carbon share of the co-ion current at P200 (0.670 +-
  0.082, n 3).
- Operating range: the measured 25-250 mA/cm2.
- Reactions and materials: `process/reactions.yaml` holds CO2R and WS. Their heats of reaction
  come from the CODATA formation enthalpies: dH = 282.98 and 285.83 kJ/mol at 298.15 K, U_tn =
  1.4664 and 1.4812 V. `process/materials.yaml` holds CO2, CO, H2O, H2, O2 and KOH.

`cheme process cell` result (no findings):
- U = 5.367 +- 0.147 V, FE CO 0.383 +- 0.040, FE H2 0.560 +- 0.038 (measured point P200, no
  interpolation). The unassigned current, 5.7 %, becomes heat.
- P = 5.37 W; reaction enthalpy 1.39 W; heat to remove 3.98 W.
- CO 0.200 g/h, H2 0.0211 g/h, O2 0.281 g/h. Electricity 26.9 kWh per kg CO formed (all the
  cell's electricity, not allocated). Voltage efficiency against U_tn 0.27.
- WDE 0.967 +- 0.008. Co-ion current 3.3 % of the current: K+ 0.114 and HCO3- 0.231 umol/s.
  Anolyte hydroxide deficit 0.346 umol/s (1.24e-6 kmol/h).
- The charge, element and energy balances close.

Reason:
- 200 mA/cm2 is the current density of the paper's long-term anolyte stability model, for the
  same 5 cm2 cell in 1 M KOH (Results, Fig. 5). The skid work (#330) starts from that case.
- It is a measured point, so the lookup does not interpolate. Its WDE has three runs. Its
  voltage is steady within a run (sd 0.03-0.07 V in the window), unlike at 250 mA/cm2.

Rejected:
- 250 mA/cm2. Its voltage rises by 0.8-1.8 V from the first to the second half of the hour
  and scatters by 0.8 V between runs. A fourth run at it (20241023) reached -10.05 V at 2467 s
  and held there, very likely at the potentiostat's compliance limit, from 2502 s until the
  record ends at 2845 s (D-005).
- 150 mA/cm2, which has three FE replicates. It is not the paper's design case; the FE at 200
  has two replicates whose sums agree within 0.002.
- Electrode half-reactions in the acidic-cathode form (CO2 + 2 H+ + 2 e- -> CO + H2O at the
  cathode, alkaline anode). They are what the BPM does. But they add up to the overall reaction
  only with the membrane's water dissociation, and core's electrode check refuses them (its
  `dissociation:` takes only components of the overall reaction). The alkaline form has the same
  electrons per extent and the same home electrodes.

Assumptions:
- The bench cell's performance at 200 mA/cm2 is that of the 1 h runs. There is no measurement of
  a longer run in 1 M KOH (the 5 h pH record is in 0.1 M KOH, design basis).
- The FE rest on the meter's 0 °C basis (ASSUMED, D-005). At 20 °C FE CO would be 0.357 and the
  electricity about 28.8 kWh per kg CO. The two FE replicates of P200 (20241002, 20241004) are
  of the first GC export, so the meter baseline step of the second export (D-005) does not
  enter this point.
