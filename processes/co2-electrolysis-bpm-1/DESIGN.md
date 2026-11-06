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

Changed by D-052 (owner, 2026-11-06): the cell at 25 °C and the meter at 0 °C and 101.325 kPa
are kept (still ASSUMED); the dataset authors are asked for the meter's reference, and the
-6.8 / -8.4 % FE at 20 / 25 °C is carried as a stated capacity band.

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

## D-007 Two pilot skids as two trains and two cases in one folder (2026-11-04)
Decision: #330 designs two CO2-to-CO pilot skids from one design basis in this folder.
- Train A (1xx tags, Skid A) and train B (2xx tags, Skid B) are both in
  `process/flowsheet.yaml`. Case `skid-a` (default) runs train A, case `skid-b` train B; the
  other train is idle there (zero flow). The terminals are shared, with one port per train.
- Both skids use `pilot-cell` of `process/cells.yaml`: the bench cell scaled 20x to 100 cm2 at
  the same 200 mA/cm2, its performance looked up in the measured series (ASSUMED: the per-area
  performance transfers from 5 to 100 cm2).
- The stacks STK-A and STK-B (`stacks:`) are sized by `cheme process stack` (core ADR 0044);
  their skid duties D-A and D-B are in `process/duties.yaml` (core ADR 0043).
- The cell is not linked to a flowsheet step: the idle train has zero flow in the other case,
  and the cell's Faraday balance would then not match its stream.
- One command regenerates everything that depends on the campaign duration:
  `cheme run scripts/regen.py --duration H` (D-009 to D-011; spec #330 section 6). Core is
  reached only through `scripts/_core.py` (the `--json` output of its commands); input files
  are changed only by targeted edits that refuse any other change (`scripts/_yamledit.py`) or
  by core's own writers (`cheme process stack --write`).

Reason: one folder keeps one measured series, one cell, one product specification and one
rerun command for both designs, and the library's tools (CI discovery, LCI, catalogue,
balance-script check) assume one plant root per process. Two cases give each skid its own
functional unit for the LCA (#331).

Rejected:
- Nested plant roots per skid (`skids/<x>/plant.yaml`, an alternative of the #330 design that
  no library ADR records; library ADR 0033 is the engineering CI job): every library tool would
  need to change, and the measured series would be referenced across folders.
- Two top-level process folders: the cell, the series and the product specification would be
  duplicated.
- Two trains in one case: one LCA dataset would mix both skids.

Assumptions: the area scale-up; a 25 °C anolyte held by the cooler (ASSUMED).

## D-008 Product specification and CO recovery (2026-11-04)
Decision: `process/design-basis.yaml` `capacity.pilot_skid`: 0.100 kg/h CO delivered at the
skid boundary, at >= 0.99 mol/mol dry and 5.0 bar(a), with 0.90 of the CO formed recovered by
the gas conditioning. All ASSUMED pilot choices. `scripts/regen.py` copies the product duty
into `stacks[].product` (step 2); core sizes the stacks for rate / recovery formed
(`product.recovery`, core ADR 0044 amendment) and reports the output formed and delivered.

Reason: 0.100 kg/h gives 28 cells of 100 cm2, four stacks of seven on a 48 V bus (about 3 kW
DC), a pilot scale. Skid A at 1000 h fits a 20 ft frame and at 10,000 h does not: the crossing
is a reported result, not a target (D-015).

Rejected: a delivered rate equal to the rate formed (recovery 1): the PSA loses CO to its tail
gas, and the stacks would be undersized.

Assumptions: the rate, purity, pressure and recovery are ASSUMED (no customer or vendor).

## D-009 Skid A: one fill that lasts the campaign (2026-11-04)
Decision: Skid A is filled once with fresh 1 M KOH and runs at 200 mA/cm2 without dosing,
bleed, make-up or degassing until the anolyte reaches the pH threshold 12 (D-003) at the end
of the campaign H. The duty D-A states `reservoir.size: to_horizon`: `cheme process stack
--write` writes the exact volume that reaches H (V = V0 Q(H) / Q*, rounded up to 4
significant figures, core ADR 0044 amendment), so V is proportional to H. No time margin is
added; the uncertainty of WDE is reported as a band instead (`regen.py --uncertainty`, D-022).
With no time margin the pH low-low trip I-101 sits at the threshold itself, so that it does not
end the campaign before H (D-018).

Results (`results/scenarios/<H>h/record.json`): 1165.15 L exact, 1166 L written at 1,000 h
(T-101 D 1.074 x H 1.611 m); 11651.5 L, 11660 L at 10,000 h (D 2.313 x H 3.470 m); the end
state at either duration about 0.400 mol/L carbon and 0.803 mol/L K+ (pH 12.02). KOH 0.649 kg
per kg CO delivered at both. With WDE one sd lower (0.9585) the reservoir sized at the mean
reaches pH 12 after 804 h of the 1,000 h, and the volume to the horizon is 1451 L (+24.5 %);
one sd higher, 880 L (-24.5 %).

Reason: the simplest skid, with no chemicals handled during the run; the closed form makes
the duration dependence exact (ADR 0043).

Rejected: probing the duty at a trial volume and scaling in the library (the spec's fallback):
core computes the exact volume itself now.

Assumptions: the measured WDE and co-ion split hold over the whole campaign and across the
changing electrolyte (not supported by measurement, D-014).

## D-010 Skid B: continuous KOH dosing, bleed and make-up at a steady state (2026-11-04)
Decision: Skid B holds 50 L (ASSUMED: about 4.5 min hold-up at the 11.2 L/min recirculation,
for O2 disengagement) at the ASSUMED setpoints 0.5 mol/L OH- and 0.25 mol/L carbon (design
basis `capacity.pilot_skid.skid_b_setpoints`, with provenance; regen reads them there) by
continuous dosing of 5 M KOH (concentration and density 1.22 kg/L ASSUMED), a bleed to the site effluent and
make-up water. `scripts/regen.py` (step 6) sets the rates from the steady-state balance:
- bleed b = Cx (1 - WDE) N I / (F C_T), so the carbon that enters leaves with the bleed;
- dose = [b [K+] + (1 - Cx)(1 - WDE) N I / F] / 5 M, with [K+] from the setpoints' charge
  balance (concentration basis, the anolyte model's constants);
- make-up = b - dose, corrected once from the probe run's volume drift.
Cx is the duty's carbon share: for a measured cell the duty takes the titration's share
(0.66978 at P200), while `cheme process cell` reports the membrane block's rounded 0.670; the
setpoints are then held exactly. The 5 M day tank T-202 is refilled weekly (`refill_interval`
168 h, core ADR 0044 amendment), so its size does not grow with H. There is no bleed tank.

Reason: continuous dosing has a closed-form steady state (residence time V / b, about 27 h)
and no dosing chatter. The setpoints keep the ionic strength about 1.25 mol/L, inside the
anolyte model's 1.5.

Rejected: threshold (on/off) dosing: thousands of switches over 10,000 h and no closed form.

Assumptions: dosing, bleed and make-up are open-loop in the model (the AIC-201 trim is not
simulated) and run while the current is on; the KOH use depends on the setpoints. Dosing does
not save KOH against Skid A: it uses more per kg CO (reported unsoftened in the results).

Results: bleed 1.8661 L/h, dose 2.0959 mol/h (0.41918 L/h of 5 M), make-up 1.4469 L/h,
residence time 26.8 h; at H pH 13.699, 0.500 mol/L OH-, 0.250 mol/L carbon, ionic strength
1.250 mol/L, 50.0 L, at both durations. T-201 D 0.376 x H 0.564 m and T-202 D 0.448 x H 0.538 m
(84.5 L, refilled 6 times in 1,000 h, 60 times in 10,000 h) do not change with H; the dosed,
bled and make-up totals scale x 10. KOH per kg CO delivered: 1.167 dosed plus 0.028 (1,000 h)
or 0.0028 (10,000 h) for the 50 L fill, against Skid A's 0.649 and the floor of 0.648 per kg
delivered (0.583 per kg formed): dosing does not save KOH; it costs 1.8 times Skid A's.

## D-011 Campaign-averaged KOH fill and spent anolyte; the anolyte in the flowsheet (2026-11-04)
Decision: `scripts/skid_balance.py` writes every stream value per hour from core's duty totals
over the committed horizon H.
- KOH-FILL is the initial fill over H, SPENT the final inventory over H (campaign-averaged
  streams, because LCA consumables cannot be per case).
- The cation and carbon routes (initial, dosed, bled, through the membrane, final) are core's
  totals by route (core ADR 0044 amendment); the script asserts that K and C close to 1e-9
  relative, so the reservoir's balance is not closed by difference.
- The dissolved carbon is lumped as K2CO3 and the free hydroxide as KOH (the HCO3- share is
  below 2.1 % of the carbon at pH >= 12); K and C are exact, the speciation stays the duty
  model's.
- The recirculation loop is at the campaign's mean state: Skid A the mean of the initial and
  final reservoir (exact at constant fluxes and volume), Skid B the steady state.
- The water: the fill and the anolyte at 1.05 kg/L, the make-up water at 0.997 kg/L (ASSUMED);
  the water of the spent anolyte and the bleed by balance, shared by their volumes.

Reason: the flowsheet's balances (tolerance abs 1e-5 kg/h) close by construction, and the LCA
reads one stream per consumable.

Rejected: a per-campaign batch flowsheet (no case structure for it in the LCA).

Assumptions: the densities; the lumping of the carbon.

## D-012 Gas conditioning, CO2 recycle, tail-gas oxidation and the stream conditions (2026-11-04)
Decision: the cathode gas conditioning is a black box at the concept stage:
- the cathode is fed with 10 sccm/cm2 of CO2 (the bench ratio, at the meter's 0 °C basis,
  D-005), humidified with the water the cathode consumes (hydrogen evolution) and leaves with;
  the duty model holds the anolyte volume, so no net water crosses the membrane (ASSUMED);
- V-x21 separates the condensate, which carries the K+ that crossed to the cathode as K2CO3 at
  an ASSUMED 1 mol/kg (the salt precipitation risk of the cathode is not modelled), and passes
  the gas saturated at 25 °C and 110 kPa(a);
- K-x31 compresses to the product pressure plus the PSA's loss (design basis
  `psa_pressure_loss`, 1 bar ASSUMED): 600 kPa(a); the PSA X-x31 delivers 0.90 of the CO
  formed at 0.99 mol/mol dry (H2 the rest) at the design basis' 500 kPa(a) (both pressures
  written into the flowsheet by `scripts/skid_balance.py`, and the compressor power estimate
  from them), returns 0.95 of the unreacted CO2 to the cathode feed and
  sends the rest with the water to the oxidiser X-x32, which burns CO and H2 with twice the
  stoichiometric air (reactions COX, HOX): no CO or H2 is vented;
- the stack heat (cheme process stack) is removed by the cooler E-x11 to cooling water
  (isothermal model); the stacks return the anolyte at the cell temperature (25 degC,
  `process/cells.yaml`), and the cooler outlet S114 / S214 is the cell temperature less the
  stack heat over the loop flow at cp 3.95 kJ/(kg K) (ASSUMED, about 1 M KOH): 2.9 K at
  2.23 kW and 705.6 kg/h, so TIC-x11 holds 295.27 K. The stated 2 K before did not balance
  the cooler duty (1.5 kW at 2 K);
- the power: the stacks' AC power (DC over the rectifier efficiency 0.95, ASSUMED), and
  ESTIMATES until `cheme datasheets fill` gives the pump and compressor powers: the pumps at
  efficiency 0.3 (dosing 0.1, 300 kPa), the compressor adiabatic (kappa 1.3, efficiency 0.5),
  the PSA 0.5 kWh per kg CO delivered (TBD vendor);
- the other temperatures and pressures of the streams are design conditions, ASSUMED.
- The cooling water terminal CW is a product-side utility terminal (heat leaves the process
  to it), as core's energy streams run; the spec listed it with the feeds.

Reason: a pilot skid buys the gas conditioning as a package; the absolute kWh/kg and the vented
CO2 depend on these assumptions, the A-versus-B and duration comparisons do not.

Rejected: venting the PSA tail gas (CO is toxic, H2 flammable).

Assumptions: every value above; FE H2 0.56 makes about 1.46 mol H2 per mol CO, so the tail gas
is mostly H2 and CO2.

## D-013 The comparison duties on Skid A's hardware (2026-11-04)
Decision: D-A-ONOFF (24 h period, half on, starting on) and D-A-PART (12 h at 200 and 12 h at
100 mA/cm2, both measured points, steps) run at STK-A's arrangement by naming the stack
(`stack: STK-A`, core ADR 0044 amendment) on D-A's reservoir volume (copied by regen, step 7)
with a horizon of 3 H. They are compared with D-A at equal CO formed (`cheme process duty
--compare`, regen step 12); at fixed recovery equal CO formed is equal CO delivered.

Results (half of D-A's campaign CO, 55.96 kg at 1,000 h): on/off reaches it in 992 h (9,992 h at
10,000 h) with the charge, energy, hydroxide deficit and final pH of D-A within 1e-3; part load
reaches it in 716 h with 7.6 % more charge, 1.47 times the hydroxide deficit and 1.3 % less
energy (U and FE of the two measured points); at D-A's whole campaign CO the part-load duty
reaches pH 12 first (969.5 h, 75.9 of 111.9 kg: `cheme.duty-target-not-reached`). D-A against
D-B at equal CO: equal charge and energy, KOH dosed only in D-B (58.8 kg at 1,000 h).

Reason: the arrangement is stated once (the stack), and the horizon leaves room for the
threshold to end a duty before the target.

Rejected: restating `cells_in_series` and `stacks` in the comparison duties (the spec's
fallback): core now takes them from the stack.

Assumptions: dosing would run while off, so Skid B is not compared on/off.

## D-014 Conditional invariants (2026-11-04)
Decision: FE, WDE, U and kWh/kg are called invariant of the duration only where the current
density, the temperature, the electrolyte state and the time on stream stay inside the
measured conditions (1 h runs in fresh 1 M KOH, carbon below about 0.01 mol/L). Otherwise the
results say "held constant by assumption, not supported by measurement". The check is
scripts/regen.py's (step 14): core does not check the electrolyte state.
- Current density: core's hours outside the measured 25-250 mA/cm2 of the schedule.
- Temperature: the duty model is isothermal by assumption; the condition is that the cooler
  E-x11 removes the stack heat (flowsheet Q105, Q205 against `cheme process stack`) at the
  measured series' 25 degC (both ASSUMED).
- Electrolyte state: the duty's OH- and dissolved carbon against fresh 1 M KOH after its 1 h
  run (OH- >= 0.9769 mol/L, carbon <= 0.00926 mol/L from the measured WDE and carbon share).
- Time on stream: the duty's hours against the 1 h runs.

Results: the current density and the temperature hold; the electrolyte and the time on stream
fail on both skids (Skid A outside from 23.1 h, 976.9 h of 1,000, and from 231 h at 10,000 h,
the closed form's 23.1 h x 10; Skid B from about 1.1 h, 999 h, its crossing inside the first
sample interval, so at 10,000 h, sampled every 42 h, it reads 2.0 h; 999 h beyond the
measured hour), so FE, WDE, U and kWh/kg are "held constant by assumption,
not supported by measurement" in every record and report. Each margin (OH- and carbon) is
interpolated between the samples on its own and the hours outside either are united: the
minimum of the two is not linear between the samples, and interpolating it put Skid A's exit
about 1 h early and made it depend on the sampling (D-023).

Reason: both skids run far beyond the measured 1 h and electrolyte.

Assumptions: none beyond the measured conditions.

## D-015 Skid envelope and feasibility (2026-11-04)
Decision: each skid is one 20 ft frame, 6.06 x 2.44 m in plan with 2.20 m usable height above
the deck (ASSUMED). A skid is feasible when every item fits that envelope in plan and height;
the height is checked by scripts/regen.py from the layout model (step 13, D-021), because
core's layout checks containment in plan only.

Results: Skid A is feasible at 1,000 h and not at 10,000 h ("Skid A cannot meet the 10,000 h
duty within the skid envelope": T-101 tops out 1.27 m above the envelope; its shell still fits
the frame in plan, while its ladder cage and the hose valves HV-102, HV-103 stand beyond the
frame's west edge, reported as details, D-021). At the measured mean the longest campaign
whose reservoir fits 2.20 m is about 2,550 h. Skid B is feasible at both.

Reason: the tank of Skid A grows with the campaign (V proportional to H, D-009).

Assumptions: the envelope and the tanks' H/D are ASSUMED.

## D-016 CO2 source (2026-11-04)
Decision: merchant liquefied CO2, a fossil industrial by-product (ASSUMED, conservative), for
the LCA of #331. An owner decision: it drives the climate result.

Assumptions: site NL (ASSUMED).

## D-017 The skid P&IDs P-01 and P-02: generated, what they show and leave out (2026-11-04)
Decision: Skid A is drawn on P-01, Skid B on P-02, both generated (`plant.yaml` `generator:`)
by `scripts/draft_P-01.py` and `draft_P-02.py` from one drawing module `scripts/_skid_pid.py`
(core's authoring API `chemeascode.domains.piping.authoring`, skill pid-draft). The frames are
committed files (`pid/frames/P-0x.xml`, the empty sheets `cheme sheet new` wrote), so
`cheme regen` works in a copy without git; change the script and `cheme regen`, never the XML.
- Every PFD step is an equipment item and every material stream a line (the flowsheet streams
  link their line, `links:`). A manifold to the four stacks is one line to the last stack with
  a branch line (suffix A to D) to each of the others; the list says which.
- DEXPI 2.0.1 has no class for an electrolyser stack, a black-box package or a rectifier: the
  stacks E-x01A to D, the packages X-x31 and X-x32 and the rectifiers U-x01 are
  `ProcessEquipment` in the P&IDs and the equipment list (`type` must be the drawn class); the
  service and notes say what each is. The stacks were `Electrolyser` and the packages
  `CustomEquipment` before (stage 2); `cheme process stack` does not read the type.
- Added to the equipment list for the control: the rectifier U-x01 (the final element of
  JIC-x01 and of the trips) and an enclosure extract fan K-x41 (ASSUMED enclosed skids,
  started on gas detection). Both are drawn without a process connection; the DC bus is not
  drawn.
- Nominal diameters (ASSUMED): the anolyte loop DN 25 (11.2 L/min, about 0.3 m/s), the vents
  DN 25, the cathode gas and the small liquid lines DN 15.
- Skid B: the 5 M KOH dose enters the reservoir top from the day tank T-202 and the metering
  pump P-202; the make-up water enters on level (LV-201); the bleed (FV-203, FIC-203) leaves
  from the reservoir bottom by a branch of the drain line upstream of its isolation valve
  (gravity, about 1.9 L/h: a metering pump is the alternative, open). The flowsheet draws the
  bleed from T-201 (S223); the P&ID is the same source.
- The four stacks are fed in parallel by four manifolds, which cannot be drawn without
  crossings: with the anolyte manifolds above and below the stack row, each cathode gas
  manifold crosses one of them three times (six crossings per sheet, accepted in the gate
  drawing-clean of checks/checks.yaml until the design review confirms or redraws).
- Left out at the concept stage (open, for the HAZOP and the relief study): relief devices
  (K-x31 is a positive-displacement compressor; the cathode gas train), vents and drains
  beyond the ones operation needs, double block and bleed, the speed signals of FIC-x01 and
  AIC-201 to their pumps (the pairings are in control/loops.yaml), the stack vendor's own
  connections.

Reason: one module draws both skids the same way, so they differ only where the design does
(Skid B's dosing, make-up and bleed); a generated sheet stays current with its script, and the
validate drift check finds a hand edit.

Rejected: hand-maintained sheets (two sheets of the same skid would drift apart); a stack
drawn once as "typical of four" (each stack is a listed item that the P&ID must show).

Assumptions: the nominal diameters, the fan and the enclosures, the gravity bleed.

Changed by D-050: the skids are open and naturally ventilated; the extract fans K-x41 are
deleted from the lists, the control and the layout (the drawing module still draws them until
P-01 and P-02 are regenerated with the P&ID revision).

## D-018 Control of the skids: loops, trips and sequences (2026-11-04)
Decision: `control/loops.yaml`, `control/cause-effect.yaml`, `control/sequences.yaml` and
`control/philosophy.md` hold the control of both skids (1xx Skid A, case skid-a; 2xx Skid B,
case skid-b), PROPOSED for the HAZOP:
- loops per skid: FIC-x01 recirculation (pump speed), TIC-x11 anolyte at the stack inlet
  (cooling water), JIC-x01 stack current (rectifier), FIC-x02 fresh CO2, PIC-x21 cathode
  back-pressure, LIC-x22 condensate, PIC-x31 product pressure, the pH (AI-101 with AAL on
  Skid A, which has nothing to manipulate on pH); Skid B adds AIC-201 trimming the P-202 dose
  around the duty's rate (feedforward from the current), FIC-203 bleed and LIC-201 make-up;
- setpoints that are a case value name their stream, so validate keeps them in step with the
  flowsheet; `scripts/regen.py` (step 9) writes them, the stack currents (JIC-x01, from `cheme
  process stack`: 80 A, 4 x 20 A) and the AIC-201 pH setpoint (D-B at H, pH 13.70), so no
  calculated setpoint is a hand copy;
- the back-pressure loops PIC-x21 and PIC-x31 act direct: a rising pressure upstream of the
  valve opens it (PIC-x21 was reverse, which would close the fail-open PV-x21 as the cathode
  pressure rose);
- trips per skid: pH low-low trips the rectifier: on Skid A at the pH 12 threshold itself
  (I-101, concentration basis), on Skid B at 12.2 (far below its 13.7 setpoint); level low-low
  trips the rectifier and stops the pump (Skid B on an independent LIA-202), CO or H2 detected
  trips the rectifier, closes the CO2, stops the compressor and starts the fan, the stack
  outlet temperature high-high and the recirculation flow low-low trip the rectifier; on
  Skid B the dose and the bleed are interlocked off with the current off (I-207, a permissive)
  and the day tank's low-low level stops the dosing pump;
- Skid A's pH trip is at the threshold, not above it: T-101 is sized to reach pH 12 at H with no
  time margin (D-009), so a trip at 12.2 would end every campaign early (at about 992 h of
  1,000 h by the closed form, 0.8 % of the CO lost; 9,918 h of 10,000 h). A campaign ends
  normally at H (SEQ-A-STOP, pH 12.02 at the measured WDE); the trip acts only when the WDE is
  below the measured one or the run overruns H. A margin above the threshold would need the
  reservoir sized to the trip value (about 1,176 L for 12.2), which changes the frozen sizing
  basis (E2); left as an owner decision for the HAZOP. AI-101's low alarm at 12.5 (about 27 h
  before H) is the notice to plan the stop;
- sequences per skid: fill, start-up, the normal stop at H (SEQ-x-STOP), the response to a
  process trip (SEQ-x-TRIP: current off, the CO2 purge kept), the response to a gas detection
  trip (SEQ-x-GAS: the gas trips close FV-x02 and stop K-x31, so the cathode gas train stays
  isolated with its CO and H2 until the leak is found and the trips reset, then it is purged to
  the oxidiser), the end-of-run drain after any of the three;
- fail positions proposed: cooling water open, CO2 closed, cathode back-pressure open,
  condensate, make-up and bleed closed, product closed (open point).

Reason: the duty model holds the stacks at the measured operating point; the loops hold the
skid there, and the trips stop the current before the anolyte, the cooling or the flow leaves
it. The model doses and bleeds only with the current on (D-010).

Assumptions: every trip value and alarm margin (ASSUMED), the fail positions, SIL not screened.
The pH basis: the probe reads activity pH, the model concentration-basis pH (core ADR 0043):
the values need an offset or a calibration before use (control/philosophy.md).

Changed by D-050 and D-051: CO or H2 detected no longer starts a fan (there is none on the open
skid); the rectifier trip opens its AC feeder at SDB-1.

## D-019 Skid layout: plot, frames, placement, zones and routing (2026-11-04)
Decision: a notional pilot plot (ASSUMED, `layout/site-plan.yaml`): 32 x 16 m, two process
areas A-100 (Skid A) and A-200 (Skid B), an access road R-1 along the south for the KOH and CO2
deliveries, and a one-tier utility rack PR-1 (2.8 m) along the skids for the site tie-ins.
- Frames (`layout/structures.yaml`): SKID-A and SKID-B, each one 20 ft frame of the envelope
  (D-015), 6.06 x 2.44 m, deck 0.15 m above grade (UPN 140 on HEB 140 corner posts), two
  access steps per frame at remote corners outside the hazardous zone (south side at the west
  end, east end at its north corner), so that the deck has two ways off.
- Placement (`layout/equipment-placement.yaml`): every item on the deck of its frame, sized
  from the equipment list only (the model's `size_from: list`; no `size:` in the placement, so
  a regenerated tank is drawn at its new size). Skid A keeps the frame's west 2.44 m for T-101
  alone: at 10,000 h the tank's D 2.31 m still fits the frame width and no other item stands
  in that circle; the growth then fails on height (D-015). Rows across the frame: south the
  anolyte pump, cooler, separator and compressor; the middle the four stacks, turned so that
  their anolyte connections face south (to the pump and cooler) and their gas connections
  north (to the gas packages); north the PSA, the oxidiser, the fan and, at the east end, the
  rectifier. Skid B the same, with the day tank T-202 and the metering pump P-202 at the west
  end.
- The rectifier U-x01 (a non-Ex cabinet of about 3 kW, the skid's main ignition source) stands
  outside its skid's zone 2: at the east end, more than 1 m from the zone sources X-x32,
  E-x01D and K-x31 (it stood 0.55 m from X-x32 before, inside the zone). The extract fan K-x41
  took its place inside the zone: as the fan of a hazardous enclosure it is Ex-rated for zone 2
  (ASSUMED), as are the motors of P-x01, K-x31 and P-202 there. Open with the area
  classification.
- Stack access: the stacks are 0.18 m units lifted out upwards by hand once their connections
  are undone; `process/cells.yaml` stacks[].access gives 0.3 m of hand room at their ends and
  sides (ASSUMED), and regen (step 13) checks that no other item stands in it, because core
  sizes the stack footprint with the access but draws no envelope for it. The spec's 1.0 m at
  the ends (removal along the axis) and 0.8 m at the sides cannot be met in a 20 ft frame by any
  arrangement: four stacks with those clearances need 15.5 m2, more than the 14.8 m2 frame
  (deviation from the spec, D-023).
- Outlines of the items `cheme process stack` does not size (pumps, cooler, separator,
  compressor, packages, rectifier, fan) are ASSUMED in the equipment list (`assumed: true`),
  until vendor drawings; the stacks' and tanks' are the tool's.
- Zones (`layout/zones.yaml`, ASSUMED screening): one zone 2 per skid from the flanges of the
  stacks, the separator, the compressor (a diaphragm compressor: no shaft seal on the gas
  side, so flanges, 1 m, not a 3 m compressor seal), the PSA (CO) and the oxidiser; radii from
  core's indicative table, not an area classification.
- Routing (`piping/routing.yaml`): the DN 25 lines are routed (anolyte loops, KOH fill, spent
  anolyte drain, O2 vents, oxidiser flues), the DN 15 lines are skipped as skid small bore run
  by the fabricator at the concept stage. The anolyte supply and return manifolds at the
  stacks are laid out by hand (pinned routes); every route that ends on a reservoir is left to
  the router, because the reservoir and its nozzles change with the campaign. The KOH fill and
  the spent anolyte drain end at hose connections at the frame's west end (battery limit
  points), for a tanker or IBCs on the road. The O2 vents and the flues rise until a 1 m sphere
  clears every walking level (ASSUMED radius): to about 3.4 m, above the 2.35 m envelope top
  (fitted at site, reported apart by the envelope check).
- The package equipment spacing table is switched off in the site plan (`criteria:
  spacing_table: false`): inside a 20 ft frame the spacing is the fabricator's. Accepted in
  `checks/checks.yaml` for the layout review: the plot-plan pump access space (1 m all round)
  of P-101, P-201, P-202, and two lines under 2.1 m over the deck (AN-104 to the reservoir
  top, KOH-101 to its hose connection): the skid is worked from grade along its long sides.
Measured (`cheme show --layout`, 1,000 h): X-131 to X-231 14 m between footprints (separation
6 m, D-019); T-101 to its nearest item X-131 0.9 m; items top 1.95 m (X-x31) under the 2.35 m
envelope top on both skids.

Reason: the layout carries the sizes of the regenerated equipment (E8) and makes the
envelope check concrete: the items of each frame, their bounding boxes, against the frame.

Rejected: an enclosure (casing walls) around each frame: it would make the deck and the
items "inside a casing" (not operable, ways down not counted) for a skid that is ventilated
and opened for work; the enclosure stays an assumption of the control (K-x41, D-017).

Assumptions: the plot, areas, road, rack, frame sections, deck height, steps, outlines,
arrangement, zones, pipe-way elevation, vent radius and hose connection points (all ASSUMED).
Core limitations met: the tank family draws a roof handrail and a ladder on any tank, also on
a 1 m skid tank (to 2.89 m at 1,000 h); they are reported apart, not counted in the envelope.

Changed by D-047 (layout review 2026-11-05-layout): the rows are rearranged (the stacks along the frame's south edge, the rectifier at the north-east corner), the tail-gas oxidiser X-x32 stands off the frame outside the zone and is no zone source, the utility rack PR-1 runs north of the skids, and the 0.15 m deck has no guard rail.

Changed by D-050 and D-051: the owner decided an open, naturally ventilated skid (no enclosure,
the extract fan K-x41 deleted) and the Ex marking of the items in the zones (motors II 2G Ex db
eb IIC T3 Gb, instruments Ex ia IIC T4 Ga); the area classification stays the competent
person's.

## D-020 Draft datasheets regenerated by scripts/regen.py, per case (2026-11-04)
Decision: while a datasheet is a draft (`draft: true`), `scripts/regen.py` (step 10) removes
it and drafts it again from the model as it now is, after `cheme layout build`, then runs
`cheme process stack --write` (pump inputs) and `cheme datasheets fill --case skid-a` for the
1xx tags and `--case skid-b` for the 2xx tags. Train B's drafts are drafted in a temporary
copy whose default case is skid-b and copied back. A datasheet completed by hand (no
`draft: true`) is kept.

Reason: in core 1.5.0 `cheme datasheets draft` reads the default case only and never touches
an existing datasheet, and `cheme datasheets fill` never overwrites a value the datasheet
gives: kept drafts carried train B's conditions from case skid-a (zero flows) and, after a
campaign change, the old tank size (at 10,000 h T-101 stayed D 1.074 m beside the list's
2.313 m, cheme.datasheet-dimension-mismatch).

Rejected: editing the drafts' values in place (a second copy of core's draft logic).

Assumptions: none; a core option `draft --case` and a refresh of tool-copied values would
replace this.

## D-021 Envelope check and the scenario figures (2026-11-04)
Decision: `scripts/regen.py` step 13 checks each skid against its envelope (D-015) from the
layout model: the union of the bounding boxes of the items mounted on its frame against the
frame's plan and the deck plus the 2.20 m usable height, plus core's "is not inside
structure" findings and any clash error of an item on the frame (an item that no longer fits
beside the others). The generated details of an item (a tank's roof handrail and ladder) and
the pipes above the envelope (vent and flue risers) are listed apart, not counted: they are
fitted or cut at site. A failing skid is reported with the sentence "Skid A cannot meet the
10,000 h duty within the skid envelope" and its reasons; the run does not stop. The figures
of a scenario (figures/skids/<H>h: plan, a section across the reservoir and one along the
frame per skid, SVG and PNG; figures/duty/<H>h; figures/compare/<H>h) are written by the run;
a `--scratch` run copies them back, so the 10,000 h figures are committed while the model
stays at the 1,000 h design.

Results: at 1,000 h both skids fit (items top 1.95 m under 2.35 m, 0.40 m left; the tank
T-101 D 1.074 x H 1.611 m). At 10,000 h Skid A does not: T-101 (D 2.313 x H 3.47 m) stands
1.27 m above the envelope and its ladder meets the deck's handrail; its shell still fits the
frame in plan, but its ladder cage and the hose valves HV-102 and HV-103 stand beyond the
frame's west edge (listed in the record's `details_outside_plan`, not counted, as the details
above the envelope); Skid B is unchanged (at both durations the ladder cage of T-201 reaches
0.34 m beyond the frame's north edge and the hose valve HV-203 its west edge, details). The
generated details are checked in plan too: the
parts of each item (their own extent, not the item's bounding box) and the inline items of the
skid's sheet against the frame.

Reason: core checks containment in a structure in plan only (D-015).

Assumptions: the envelope and the tanks' H/D (D-015).

## D-022 Results, records, resize report and uncertainty of the skids (2026-11-05)
Decision: `scripts/regen.py` ends every run with its results as files (steps 14 to 19, scripts
`_results.py` for the arithmetic and the figures):
- `results/scenarios/<H>h/record.json`, the calculation record of one scenario: the sha256 of
  the hand-maintained inputs regen never writes (`inputs_sha256`) and of the model files after
  the run (`model_sha256`), core's version, the condensed duty, stack and comparison results,
  per skid the values, the duty `run_fingerprint`, the sizing inputs of the resize causes
  (`sizing_basis`), the feasibility with its reasons and sentences, the details beyond the
  envelope, and the invariants (D-014). Deterministic (no time stamp or git HEAD, no
  install-dependent core commit; floats to 10 significant figures), so `--check` compares
  bytes.
- `results/resize-1000h-10000h.{json,md}`, written once both design scenarios have a record:
  41 rows (quantity and skid) with both values, changed or not, its rule, the calculated cause
  (its inputs from the records' `sizing_basis`, so it follows an input change) and the frozen
  hand value of `results/expected.yaml` with tolerance and status; the errata of the frozen file
  (`results/expected-errata.yaml`); the P&IDs' sha256 and the stack dimensions as the unchanged
  artefacts; and README.md's results table (between its regen markers). Result: 0 hand checks
  failed, no rule broken.
- `--uncertainty`: core propagates no measurement scatter (design core gap C2), so in temporary
  copies only the pilot cell becomes `performance: specified` at the P200 mean, at mean +- 1 sd
  of WDE, of FE CO and of U one at a time (the sample sd over the replicates), and at the 20 degC
  meter basis (FE x 273.15 / 293.15, D-005); the stack report and D-A at the committed volume
  give the cells, kWh/kg, the volume to the horizon and how long the design reservoir lasts,
  and Skid B's rates follow from the step-6 closed form. A specified cell's duty must name its
  product, so the copies add `product: CO` to the duties. The co-ion split is the membrane
  block's 0.670 there (the measured cell's duty uses the titration's 0.66978), so the bounding
  runs are compared with the specified mean, not with the measured run; Skid B's rates take
  the carbon share each bounding duty ran at and D-B's dosing concentration, not literals. Written to
  `results/scenarios/<H>h/uncertainty.json` and two figures drawn by the script
  (`figures/skids/<H>h/uncertainty-ranges.svg`, `uncertainty-ph-band.svg`). A run without
  `--uncertainty` removes a stale `uncertainty.json` (step 10 has removed its figures).
- `--record` writes the ADR 0020 session record (`cheme runs record --kind manual --slug
  regen-<H>h --report-file results/resize-1000h-10000h.md`), apart from the calculation record.
- `--check` (gate `skid-regen-current`) regenerates every design scenario in a temporary copy
  and compares the records, the resize report, the README table, the scenario's figures and,
  at the design duration, the model files (with `control/loops.yaml`) and datasheets.
- Step 13 now leaves out the validate findings that `checks/checks.yaml` accepts with a reason
  (the twelve P&ID manifold crossings), as `cheme check` does.

Results (both scenarios): see D-009, D-010, D-013 to D-015 and the README table. Uncertainty
(one sd at a time): WDE moves Skid A's volume and Skid B's dose by -24.5 % / +24.5 %, and with
WDE one sd low the reservoir sized at the mean reaches pH 12 at 80 % of the campaign (804 of
1,000 h); FE CO one sd low, or the 20 degC meter basis, needs 32 cells (4 x 8) and raises
kWh/kg by 11.7 % and 7.3 %; U moves kWh/kg by -2.7 % / +2.7 % and not the cells. Core issues met
(not fixed here): `cheme datasheets fill` fails on NPSH (P-x01, P-202: "flash failed") and leaves
the coolers' duty TBD (water is outside the property package); a specified cell's duty refuses
without `product:`.

Reason: the results are reviewable as files, the hand expectations are checked by the library
test `tests/test_co2_electrolysis_bpm_skids.py` on the committed records (fast) and on a fresh
regeneration of both scenarios (with core), and a stale result fails the gate. The
regeneration test takes about 4 min on a laptop (5 min for the whole library suite with it)
and needs core's `props` and `png` extras, so it is marked `engineering` and runs in its own CI
job (library ADR 0033), not in the 15 min library job. `regen.py --check` takes about 5.5 min.

Rejected: Monte Carlo over the measured scatter (core gap C2; the bounding runs show the
direction and size of each parameter's effect, which a single design reservoir needs); a time
margin on Skid A (D-009: the band is reported instead).

Assumptions: the sd over three (U, WDE) or two (FE) replicates is a weak estimate of the scatter;
one parameter at a time leaves out their combination.

## D-023 Review of #330: what the regeneration now derives, checks and records (2026-11-05)
Decision: the verified review findings of #330 are fixed in the design, not around it:
- Infeasible is a result, never a tool error: a skid duty that ends before H (threshold,
  minimum inventory) or is infeasible no longer stops `scripts/skid_balance.py`; its rates are
  over the hours it ran and the output's `notes` say so, which regen records as errors (step 9);
  a balance that cannot be made at all (a refused duty) is a finding too, the flowsheet left as
  it was. The infeasibility sentences name the check that failed (the envelope, or the duty).
- Step 6 takes N I from the probe's charge over its operating time, not over H: a probe at stale
  rates that ends early gave rates too low by the ratio and never recovered (checked: from a dose
  of 0.05 L/h, one run writes the rates of the committed design).
- The record hashes only the hand-maintained inputs regen never writes (`inputs_sha256`); the
  files it writes are hashed after the run (`model_sha256`), so a fresh regeneration is its own
  fixed point and `--check` is clean right after it. The record carries core's version, not
  the commit: a local and a git install of the same core gave different bytes. The installed
  commit is printed and kept in the run summary (build/), and a version other than the one the
  expectations were frozen for is a warning.
- Single sources: the pH threshold of every duty (the comparison duties too) and the stacks'
  operating hours are synced from the design basis (steps 2, 3); the product pressure and the
  PSA's pressure loss give the compressor discharge and the product pressure of the flowsheet
  and the compressor power estimate (skid_balance); Skid B's setpoints are design-basis values
  with provenance; the anolyte density is the recirculation pump's of `process/cells.yaml`; the
  anolyte temperatures follow the cell temperature and the stack heat (D-012); the calculated
  setpoints of `control/loops.yaml` and README's results table are written by regen; the
  resize causes and the uncertainty runs take their inputs from the run, not from literals.
- The scripts read core's duty and comparison JSON through mapped, checked fields in
  `scripts/_core.py` (a renamed field stops the run with a message naming it).
- The frozen file `results/expected.yaml` states that the duties run at the rounded Cx 0.670;
  they run at the titration's 0.66978. ADR 0030 forbids editing a frozen file, so the
  correction is a new file, `results/expected-errata.yaml`, printed in the resize report; the
  values and tolerances stand (the bias is inside every tolerance). The library test now also
  asserts that the frozen files are unchanged since their freezing commit.
- Control: PIC-x21 direct; Skid A's pH trip at the threshold; the normal stop and the gas-trip
  path as sequences (D-018). P-02: the day tank T-202 has a breather KV-202 (an atmospheric tank
  filled weekly and drawn continuously). Layout: the rectifiers outside the zone, the stack
  access checked (D-019); details beyond the frame in plan reported (D-021).

Deviation from the spec: the stack access of `process/cells.yaml` is 0.3 m at the ends and sides
(a vertical hand lift of the 0.18 m stack), not the spec's 1.0 m and 0.8 m, which no arrangement
of four stacks in a 20 ft frame can give (D-019). Owner decisions left open: a trip margin above
Skid A's threshold (it needs a larger reservoir than the frozen sizing basis), the Ex rating of
the electrical items inside the zones (area classification).

Reason: each finding was a value restated by hand that a change of its source would leave
stale without a check, a result reported wrongly, or a design error (control, layout, P&ID).

Assumptions: cp 3.95 kJ/(kg K) of the anolyte, the PSA pressure loss 1 bar, the 0.3 m stack
access, the fan's Ex rating (all ASSUMED).

Changed by D-047: the stacks are no longer lifted out vertically by hand; they stand at the frame's south edge within 0.6 m reach and slide out at deck level onto a deck-height trolley (regen step 13 checks reach and slide lane).

Changed by D-051: the Ex rating of the electrical items inside the zones is decided (the owner,
2026-11-06); the fan's Ex rating no longer applies (no fan, D-050).

## D-024 LCA scope: functional unit, CO the only product, the H2, O2 and CO2 dispositions (2026-11-05)
Decision: `lca/lca.yaml` (#331, part of it; the spec's D-016) is a climate-change-only screening
and an LCI of both skids per kg CO delivered, for the 1,000 h design campaign:
- functional unit 1 kg of CO contained in the product at >= 0.99 mol/mol dry (the rest H2) and
  5.0 bar(a) at the skid boundary; `kg_per_unit` 1.000727 kg of product gas per kg of CO, 1 / w_CO
  of the product stream that `scripts/skid_balance.py` writes (regen step 20 syncs it);
- cradle to gate, NL (ASSUMED, design basis `site`), 2026; `case: skid-a` (Skid A is the study's
  dataset `lca/dataset.yaml`; Skid B is its own case dataset and the `skid-b` scenarios, D-027);
  operation 8,000 h/a (the design basis' operating hours) and a 10 year life (ASSUMED);
- **allocation none**: the cathode's H2 is burnt with the PSA tail gas in the oxidiser X-x32
  (D-012) and the anode O2 is vented, so CO is the only product. The O2 is an emission without
  burden and, under cut-off, without credit;
- the CO2 is merchant liquefied CO2 of fossil origin (D-016, ASSUMED): the feed is a
  `fossil-point-source` without an open factor (a gap), and the vented CO2 is a fossil emission
  characterised by ipcc2021-gwp100;
- the oxidisers X-132 and X-232 are adiabatic (`process/simulation.yaml`): the heat of COX and
  HOX leaves with the flue gas, no utility serves them (core's boundary check asked for this or
  an energy stream); the tanks' emissions are excluded (aqueous KOH and K2CO3, not volatile);
- the replaced stack parts are study-level consumables, the same for both skids (identical
  stacks): 28 x 100 cm2 every 4,000 h (`stacks[].replacement.interval`, ASSUMED), so every 0.5
  years at 8,000 h/a, as the bipolar membrane (0.20 kg/m2 ASSUMED), the cathode's Ag (100 nm,
  the design basis' reference cell, at the bulk density 10.49 g/cm3: 1.049 g/m2, ASSUMED dense
  film), the cathode's carbon-paper gas-diffusion layer (Sigracet 39BB, 0.10 kg/m2 ASSUMED:
  about 0.3 mm with its microporous layer, no datasheet value used) and the Ni foam anode
  (0.35 kg/m2 ASSUMED), each with a disposal (membrane to incineration, a gap; Ag to a refiner
  and Ni to scrap recycling, burden-free under cut-off; the carbon paper burnt off at the
  refiner, a gap whose fossil carbon is not counted). regen writes their amounts from the stack
  report and `process/cells.yaml`.

Reason: the comparison of the skids needs both inventories on one functional unit, and the
H2 and O2 leave the skids as no product.

Rejected: an H2 co-product (allocation by mass or LHV): no H2 separation is designed (D-026
reports the shares as a sensitivity); counting the product gas, not the contained CO (the 0.07 %
H2 would be counted as CO).

Assumptions: the life, the areal masses, the replacement interval, the site (ASSUMED).

## D-025 Reconciliation of the LCI with the duty run (E10) (2026-11-05)
Decision: every operating amount of both datasets comes from the flowsheet values
`scripts/skid_balance.py` writes from the same duty run that sized the equipment, and regen
step 20 (`scripts/_lca.py`) checks it into `results/scenarios/<H>h/lca.json` at both durations
(the spec's D-017):
- the sources of every flowsheet value the duty fills now cite the run, "duty D-A (run
  72329dd4b8605abe)": the fingerprint the duty-sized tanks T-101, T-201 and T-202 carry and the
  record's `run_fingerprint`; `lca/manifest.json` fingerprints `process/flowsheet.yaml`;
- per kg CO, the datasets equal the record's duty totals over the CO delivered (rel 1e-6):
  energy over the rectifier efficiency plus the auxiliaries, the fill and the dose (KOH 100 %, from
  the exchanges' compositions), the fill solution's mass (the initial volume at the
  recirculation pump's density), the dosing solution, the bleed's and the final inventory's K
  and C, the spent inventory's share of the anolyte water that leaves (the final volume over the
  final volume and the bleed), the condensate's K and Skid B's make-up water (its water less
  Skid A's); `cheme assess lca-cases` agrees within its six printed digits (rel 1e-5). The fast
  test recomputes every duty value from the record, not from `lca.json`;
- the spent inventory's and the bleed's mass over the duty's volumes lie between 0.997 and
  1.35 kg/L (ASSUMED band, water to a concentrated KOH and K2CO3 solution): 1.057 (Skid A) and
  1.051 kg/L (Skid B). The water balance, not the volume, sets those masses, so this is where a
  density or volume error would show;
- a run stream whose flow (or a Q stream's duty) has no source, or a source without the run, is
  uncited; a step 20 error fails regen (exit 4) and `--check`;
- K closes (fill + dose = bleed + spent + condensate) and C by origin (CO2 fed = C in the CO +
  the anolyte + the condensate + the vent) on the datasets' compositions, and in core's
  `cheme assess lca --balance --json` (Skid B's in a copy that studies case skid-b);
- the hand values of `results/expected-lca.yaml` (frozen in their own commit before the LCA was
  first computed, `tests/lca_formulas.py`): per kg CO 34.558 kWh (Skid A; 31.405 of it the
  stacks' AC) and 34.562 kWh (Skid B, with the dosing pump), 3.537 kg CO2 fed and 1.712 kg vented,
  the carbon fed 0.444 to the product, 0.058 to the anolyte, 0.014 to the condensate and 0.484
  to the vent; KOH 0.649 (A), 0.0278 + 1.167 (B, 1,000 h);
- the replaced membrane area is the 28 cells times 100 cm2, at `stacks[].replacement.interval`.
`results/expected.yaml` stays as frozen (ADR 0030); E10 is the new file. Tests: E10 in
`tests/test_co2_electrolysis_bpm_skids.py` (fast on the committed records, `engineering` on a
regeneration).

Results: both skids reconcile at 1,000 h and 10,000 h, the largest relative difference 1.6e-8
(the flowsheet's 10 significant figures); K and C close to below 2e-8.

Reason: the LCA rests on the design only if its amounts are the design's, traceably.

Deviation from the spec: the KOH exchanges count the solutions, as the flowsheet carries them
(core counts a feed by its stream); the KOH 100 % basis is their composition, compared with the
duty totals, and the Atlas mapping converts by the mass fraction (D-027). The spec puts the fill
water in `feed:WATER`: here the solutions' dilution water (11.50 kg per kg CO in Skid A's fill,
0.49 + 3.91 kg in Skid B's fill and dose at 1,000 h) is part of the KOH gaps, because core counts
each solution as one exchange, and splitting the fill into KOH and water would change the #330
flowsheet. `lca.json` states it at the water factor (`solution_water`: 0.0022 and 0.0008 kg CO2e
per kg CO) and the ranking uses the totals with it (D-026); the Atlas proxies count it as
deionised water. Core reports the element
and carbon balances `not-assessable` while the replaced parts have no composition (a consumable
takes none): K and C are asserted on the exchanges that have one.

Assumptions: none beyond the design's.

## D-026 Backgrounds, scenarios, sensitivities and the ranking rule (2026-11-05)
Decision (the spec's D-018): open backgrounds only, no ecoinvent:
- `lca/factors.yaml` includes `ember-2025` (Ember Yearly Electricity Data, release 2026-09-15,
  data 2025, CC BY 4.0; life cycle, generation-based, no T&D, mixed GWP basis) and
  `desnz-ghg-2026` (2026 v1.2, OGL-3.0, GB, AR4/AR5); one category, climate change, with the
  plant's CO2 by ipcc2021-gwp100 (AR6). The NL grid is `ember-2025:electricity-nl` (a proxy for
  the supply at the consumer). The water is DESNZ's mains water per m3 over 1000 kg/m3, a proxy
  for NL demineralised water (`water-supply-gb-kg`). Mixed vintages: a screening, partial carbon
  footprint (core: "partial screening carbon footprint");
- `missing:` with the reason for the merchant CO2, KOH, the neutralisation of the spent anolyte,
  the bleed and the condensate, the cooling water service, the membrane and its incineration,
  the Ag, the carbon paper and its burning at the refiner, and the Ni foam (DESNZ's construction
  metals factor is steel-dominated: not used for nickel); construction is cut off (D-027). 13
  gaps per skid, listed with their quantities (Skid A's dose and bleed at 0, so 11 non-zero);
- the neutralisation of the carbonate wastes releases their carbon as CO2: 7.2 % of the fossil
  CO2 fed, 0.254 kg CO2 per kg CO for either skid (15 % on top of the vent's 1.712 kg, 2.4 % of
  the total). It is fixed by stoichiometry but part of the treatment gaps, stated in their
  reasons and in `lca.json` (`carbonate_co2`), not counted;
- scenarios: `skid-b` (case skid-b); the Ember grids of the EU-27, DE, FR and the world for
  Skid A and, with `case: skid-b`, Skid B (core accepts `case` with `factors`); the DESNZ UK grid
  as a cross-basis check. The Ember pairs differ in no dimension, but every mix scenario also
  declares the UK water a proxy for its geography, so core's verdict is "proxy" (the texts in
  `lca.yaml` and `factors.yaml` say so);
- sensitivities by `scripts/lca_sensitivity.py` into `lca/`: the membrane life (1,000, 4,000,
  20,000 h, ASSUMED levels; inventory only), the H2 co-product, the electricity mix, the duration;
- **ranking rule**: Skid A is ranked against Skid B only if every flow that distinguishes them
  has a documented factor (ADR 0029). They are KOH, the alkaline wastes and construction, and
  none has one: "ranking not determined" (`lca/ranking.json`), with the break-even KOH factor
  on the totals with the solutions' water. The reading is built from the signs (which skid has
  the higher total, more KOH, more waste, the larger tanks) and the tank volumes from the
  record, not typed in.

Results (1,000 h, per kg CO, kg CO2e characterised, the gaps excluded): Skid A 10.479 (electricity
8.766, vent CO2 1.712, water 0.0005), Skid B 10.482 (8.767, 1.712, 0.003). Electricity mixes A / B:
EU-27 8.99 / 8.99, DE 13.26 / 13.26, FR 3.14 / 3.14, world 17.61 / 17.62; DESNZ UK 8.08 (not
comparable). The Ember electricity pairs differ in no scope dimension; the verdicts read "proxy"
only through the UK water factor. Electricity is the largest characterised flow (84 %), the
vented CO2 the second (16 %): the spec expected the vent possibly largest; at 34.6 kWh/kg it is
not. Membrane life: 0.0028, 0.00069 and 0.00014 m2 of membrane per kg CO (0.0029, 0.00073 and
0.00015 g Ag; 0.28, 0.069 and 0.014 g carbon paper; 0.97, 0.24 and 0.049 g Ni), impact not
computable (gaps; core's scenarios cannot vary
a consumable's amount, gap C4). H2: the tail gas carries 0.116 kg H2 per kg CO; recovered, it would
take 10.4 % of the burden by mass or 58.0 % by LHV (CODATA: CO 282.98 kJ/mol, H2 241.826 kJ/mol);
substitution missing. Duration: Skid B's KOH 1.195 kg/kg at 1,000 h and 1.170 at 10,000 h, Skid
A's 0.649 at both; the totals do not change. Ranking: with the solutions' water, Skid A totals
10.4808 and Skid B 10.4830 kg CO2e/kg (B higher by 0.0023: higher in electricity and the
separately fed water, lower in the solutions' water, equal in the vent CO2; core's totals alone
differ by 0.0036). Skid B uses 1.84 times the KOH and 1.57 times the alkaline waste, so the
break-even KOH factor is negative (-0.0041 kg CO2e/kg KOH): no KOH or treatment factor reverses
the order; only Skid A's larger tanks (1.46 m3 against 0.15 m3; construction, not stated per
case) could.

Reason: an open, publishable screening that states what it cannot rank.

Deviation from the spec: the electricity-mix verdicts are "proxy", not "like-for-like" (the water
background); the Ni foam has no proxy (a steel-dominated factor would understate nickel).

Assumptions: the Ember factor at generation stands in for the consumer's; the water proxy.

## D-027 Exports: both designs' datasets, the mappings, construction (2026-11-05)
Decision:
- Skid B's dataset is core's `cheme assess lca --write --case skid-b` (core ADR 0045), in
  `lca/datasets/co2-electrolysis-to-co-two-0.1-kg-h-pilot-skids-reverse-bias-bpm-28-cells-of-100-cm2-each-skid-b.yaml`
  (its id, title "..., case skid-b" and uuid name the case, `parent` the study dataset's uuid);
  regen step 20 writes it, the gate `lca-case-dataset-current` checks it (library ADR 0034);
- the Atlas build exports both (workbook, openLCA JSON-LD, multifunctional): the case dataset's
  activity is named "<title>, case skid-b" (library ADR 0034, `scripts/build_lci.py`); the
  replaced parts are exported unlinked, so Brightway's `install()` refuses the database until
  they are mapped;
- `lca/mappings.yaml` overrides (ADR 0022): CO2 to `carbon-dioxide-liquid`, the KOH fill and
  dose to the solution proxies `potassium-hydroxide-1m` and `-5m` (registry slug
  `potassium-hydroxide`), the spent anolyte, bleed and condensate to `wastewater` (their
  neutralisation not represented); the new shared entries in `lci/mappings.yaml` carry ecoinvent
  3.11 names, recorded "not checked: no ecoinvent licence" (ADR 0017); `process.yaml` gives the
  inventory keys;
- construction is a `cutoff:` entry, open: core 1.5.0 selects construction by equipment tag,
  not by case, so Skid B's dataset would carry Skid A's frames and its duty-sized reservoir;
- the KOH proxies count the solution as KOH 100 % and deionised water (`water`) by the
  datasets' compositions, which `tests/test_lci_case_datasets.py` compares (rel 1e-6); the
  multifunctional JSON is tested for both datasets like the workbook and the JSON-LD package;
`publication.status` was internal then, so `build_lci.py --public` left the process out; it is
public since D-048.

Deviation from the spec: the file is named by core's dataset id (from the flowsheet title), not
`co2-electrolysis-bpm-1-skid-b.yaml`; the spec's fallback (a scratch copy with `case: skid-b`) is
not used, core does it.

Open (#331 stays open): multi-category impacts; the ecoinvent 3.11 run and the mapping check; the
A against B ranking (factors for KOH, CO2 supply, membrane, Ag, Ni, PP, caustic treatment);
construction impacts; the H2 co-product alternative; the biogenic CO2 or higher-recycle case; the
membrane-life impact; a factor for the GDE's carbon paper; the fossil CO2 of the neutralised
carbonate wastes (counted once the treatment has a factor); the CPC code of the dataset.

## D-030 HAZOP of the pilot skids: two agent-prepared drafts, integrated (2026-11-05)
Decision: the skids of #330 get two HAZOP studies, drafted by agents for a team session that
has not been held (safety/README.md, safety/hazop/SESSION.md):
- **H-01 "Skid A: one-fill anolyte reservoir"** on P-01 and **H-02 "Skid B: KOH dosing, bleed
  and make-up"** on P-02, each started with `cheme safety hazop init`. A node number means the
  same part of either skid: N1 anolyte loop, N2 stacks and DC supply, N3 cathode CO2 feed, N4
  cathode gas outlet, N5 gas conditioning, N6 tail gas and vents, N7 Skid B's dosing, bleed and
  make-up (none on Skid A), N8 fill and drain, N9 the enclosure. The modes come from the
  sequences and the duties (start-up, normal, Skid A's on/off and part-load duties, Skid B's
  dosing, the end-of-campaign exchange, stop, trip and gas trip, utility failure, maintenance
  with the hand lift of D-023).
- The risk matrix `safety/risk-matrix.yaml` is a proposal in asu-1's structure (5 x 5, four
  bands, one cell table, high and very-high require an action), the money one order below
  asu-1's for a pilot of two 20 ft skids, `status: proposed`.
- Every node, scenario, safeguard, rating and action is `status: proposed, by: agent` (a
  deviation has no status field in the hazop-study schema; the scenarios under it carry it);
  the team is roles only. Bands come only from `cheme safety hazop rate --write`.
- The two studies were drafted apart, then integrated: the 58 pairs of scenarios on the hardware
  both skids share were compared, and the ratings brought onto one convention (SESSION.md
  section 3.2: the initial likelihood is that of the cause; a utility upset and a routine hose
  task E, a single failure D; a release into the enclosure people 4; an alarm seen only after
  the damage not credited; the gas trip one order; I-x04 not credited against the rectifier; a
  switched-off rectifier no isolation). 13 scenarios were added so that each study covers what
  the other found on the same hardware, two actions were added on each side, and H-02's
  actions got owner roles as H-01's have. Where a pair still differs, the design differs and
  the basis says why (SESSION.md section 3.4).
- The integrated drafts were then reviewed against the plant as drawn and their own credit
  rules, and the verified findings fixed (SESSION.md section 3.4, "What the review changed"):
  12 scenarios added for hazards the drawings show and no scenario covered (the start-up purge
  of SEQ-x-START S2 with no outlet, back-flow through the unguarded recycle CO2-x02 and its
  loss, flashback along the tail gas, the oxidiser X-x32 as an ignition source the gas trips
  leave running, and on Skid B the dosing pump with no isolation from its day tank and the
  calibration of the shared AIC-201 probe), 7 deviations added, and 32 scenarios re-rated or
  corrected where a residual credited a safeguard the cause defeats (the operator and I-x05
  acting through the failed rectifier regulation, I-x04 against the motors it starts or leaves
  running, the SEQ-B-GAS entry rule against a detector reading clear, an alarm with no time to
  act), counted one final element twice, broke the utility-upset rule, or misdescribed the
  plant or a sequence. Bands went from 67 to 89 high-residual scenarios; all have an action.
- The analysed inputs are stamped: the P&ID, the equipment, line and instrument lists,
  control/cause-effect.yaml, loops.yaml, sequences.yaml, philosophy.md, layout/zones.yaml, the
  flowsheet, the design basis and the duties. The draft datasheets are read, not stamped. The
  studies analyse the design in place, at 1,000 h: in the 10,000 h scenario, which regen builds
  in a scratch copy, the equipment list, loops, flowsheet and duties differ, and its record
  (results/scenarios/10000h/record.json, regenerated) now lists the eight resulting
  hazop-input-changed warnings. They are true: the 10,000 h design has not been studied beyond
  what the scenarios say about its 11,660 L reservoir (H01-S106). Each warning carries the
  study's file, line and recorded revision, so a re-stamp, or an edit that moves a study's
  `analysed:` block (its header comment), changes the record: regenerate it
  (`cheme run scripts/regen.py --duration 10000 --uncertainty --scratch <dir>`) and commit it
  with the study, or `skid-regen-current` fails (SESSION.md section 4). They are not accepted
  in checks/checks.yaml, since the same entry would be an unused acceptance in the 1,000 h
  design itself.
- The gate `hazop-current` (`kind: hazop`, `require: [inputs-current, no-example]`) passes on
  the drafts and fails once an analysed input changes until the touched nodes are reassessed and
  re-stamped. It is new to this process: asu-1 has no HAZOP gate yet and its SESSION.md adds
  the gates only after its session and review. Here the house gates for an assessed and
  reviewed HAZOP (as in safety/README.md, with `reviewed`) are written out, commented, in
  checks/checks.yaml, to be uncommented once the session and a human review are recorded.

| Study | Nodes | Deviations | Scenarios | Worst band high / medium / low | Very-high initial | Actions |
|---|---:|---:|---:|---|---:|---:|
| H-01 | 8 | 62 | 77 | 39 / 30 / 8 | 1 | 52 |
| H-02 | 9 | 79 | 92 | 50 / 28 / 14 | 1 | 55 |

Both report `draft`, 0 errors and 0 warnings, every band current; no scenario is very-high
after its safeguards and every high scenario has an action.

Reason: the skids differ in their tags, their sheet and Skid B's dosing, so one study per
sheet keeps each study's stamps, report and acceptance with its skid; the same hazard on the
same hardware must not be rated two ways. Before the integration, for example, the CO2 supply
regulator failing open was rated people 3/C, low after an alarm, on Skid A and 4/C, high, on
Skid B, and an enclosure leak D on Skid A and C on Skid B.

Rejected:
- One study for both skids: two sheets, two sets of tags and inputs in one file, and Skid B's
  node N7 without a counterpart; the team would accept for both skids at once.
- H-02 referring to H-01 for the shared nodes instead of analysing them: each skid's tags must
  resolve, and the team accepts each skid's scenarios.
- Leaving the two drafts' ratings as written: contradictory ratings of the same hazard.

Assumptions: the matrix, its grades and the credit convention (all ASSUMED, for the team); the
skid enclosure and its fan, which every gas-in-enclosure rating rests on (ASSUMED, not sized).

Changed by D-050: the skids are open, with no enclosure and no fan. Node N9 and the causes and
ratings that assume an enclosure are to be revised as proposals by their stable ids (never
accepted by an agent) and the studies re-stamped; until then gate `hazop-current` fails.

## D-031 The HAZOP actions the drafting agents consider most important (2026-11-05)
Decision: of the 107 proposed actions, these are the ones to decide first, for both skids at
once where the hardware is shared (SESSION.md section 3.5 lists every high scenario with its
action). Relief devices are named by their governing scenario only, never sized here (skill
`relief-scenarios`).
1. **Relief and pressure protection of the compressor discharge** (H01-A501, H02-A501,
   H02-A502): governing scenario the blocked outlet with the positive-displacement K-x31 at full
   stroke, PV-x31 failing closed on the loss of instrument air (H01-S502, H02-S501, the two
   very-high initial scenarios) or X-x31 closing its feed (H01-S501, H02-S502). Also a discharge
   high-high pressure trip, a trip on low instrument air, K-x31 interlocked with X-x31, and
   PV-x31's fail position decided with the PSA vendor.
2. **Overpressure of the cathode side and the CO2 supply interface** (H01-A303, H01-A401,
   H02-A302, H02-A402): governing scenario the supply regulator at the battery limit failing
   open with FV-x02 open (H01-S305, H02-S303); a cathode high-high trip independent of PIC-x21,
   and U-x01 tripped when K-x31 stops (H01-S411, H02-S401).
3. **An H2-in-O2 analyser on the reservoir vent O2V-x01** that trips U-x01, a decision on
   sweeping the head space, a flame arrester, earthing of the PP tank (H01-A110, H01-A603,
   H02-A601): H2 crossing the membrane or cathode gas breaking through ends in the reservoir
   head space (H01-S115, S403, S606; H02-S110, S604, S605).
4. **The pressure difference across the GDE** measured at the stack inlet against PIC-x21, with
   alarm and trip at the window of #332 (H01-A103, H02-A401; H01-S105, S403; H02-S108, S403).
5. **The gas detection study**: number, location, set points and voting of the CO and H2
   detectors, the vents and the CO product side, personal monitors; and the gas trips made to
   isolate the PSA, whose CO inventory stays connected to a leak today (H01-A902, H01-A505,
   H02-A901, H02-A505).
6. **KOH exposure**: an eyewash and safety shower at the west-end hose connections and the
   stack row, PPE, a written hose transfer procedure; on Skid B spray shields and a bund at
   T-202 / P-202 and the written weekly refill with a high level alarm on LIA-203 (H01-A106,
   H01-A803, H02-A706, H02-A707).
7. **The safe state on a loss of power**: a UPS for the gas detection, the fan and the alarms,
   and a purge or vent of the cathode gas train without power (H01-A904, H02-A905).
8. **The enclosure ventilation** proven (running or air-flow signal as a permissive) and sized,
   and CO2 / O2-depletion detection at low level (H01-A901, H01-A305, H02-A903, H02-A306).
9. **The 48 V DC bus** designed and drawn: overcurrent protection per stack, shrouded and
   drip-protected terminals, an unearthed bus with insulation monitoring, lockable isolation
   and a discharge point (H01-A202, H02-A202 to A204).
10. **Oxidiser supervision and burner management** with a pre-purge before every light-off or
    re-light (H01-A601, H01-A602, H02-A602).
11. **The pH trips**: I-201 its own probe, AIC-201 calibrated against titration (H02-A701,
    H02-A702); Skid A's I-101 margin, an owner decision (H01-A108).
12. **The Ex rating** of the items in zone 2 with an area classification (H01-A903, H01-A204,
    H02-A902, H02-A206), an open owner decision of #330.
13. **A SIL screening / LOPA** of every trip before any is credited beyond one order (H01-A112,
    H02-A104).
14. **The oxidiser X-x32 as an ignition source** of the enclosure: stopped with its tail gas
    by the gas trips, or moved outside the enclosure and zone; and the tail gas protected
    against flashback (H01-A906, H02-A906, H01-A605, H02-A604; H01-S906, S610; H02-S906,
    S613). Found in the review; a flame cannot be Ex-rated, so item 12 does not cover it.
15. **The recycle CO2-x02 guarded** by a check valve and a shut-off closed by the trips, and
    included in the gas-trip isolation: today X-x31 can blow down into the cathodes past the
    only check valve (H01-A507, H02-A507; H01-S509, H02-S509).
16. **A flow path for the start-up purge** of SEQ-x-START S2, which today pressurises the
    cathodes at every start against the stopped K-x31 (H01-A307, H02-A307; H01-S309, H02-S309).
17. **DC isolation independent of the rectifier**, so that a trip removes the current even
    when the rectifier's regulation is the fault (H01-A205, H02-A207; H01-S201, H02-S201).
18. **Maintainable dosing on Skid B**: an isolation valve between T-202 and P-202 and a
    written AIC-201 calibration with I-201 on its own probe (H02-A709, H02-A710, H02-A701;
    H02-S716, S717).

Close behind: reverse current at every switch-off (H01-A201, H02-A201), PV-x21's fail-open
letting K-x31 pull a vacuum (H01-A402, H02-A403), Skid A's back-flow from the PSA on its daily
stops (H01-A502), the dosing line's check valve and P-202's relief (H02-A703), an independent
high-high level in V-x21 (H01-A403, H02-A404).

Reason: these answer the scenarios that stay high with people severity 4, the two very-high
initial ones, and the gaps that recur across many scenarios.

The plant is not changed: the P&IDs, control and layout stay as #330 drew them, and these are
actions for the design team after the team session (spec of the HAZOP stage).

Assumptions: the ranking is the drafting agents' judgement for the team, not a LOPA result.

Changed by the owner's decisions of 2026-11-06: item 8 (the enclosure ventilation) falls away
with the open skid (D-050), which keeps the gas detectors, adds personal CO monitors and a CO2
check at grade and the low points; item 7's UPS no longer feeds a fan (D-050); item 12 (the Ex
rating) is decided in D-051, the area classification still the competent person's; item 14's
"ignition source of the enclosure" reads "of the zone" (D-050; the oxidiser is outside it since
D-047); item 17 (DC isolation independent of the rectifier) is decided in principle in D-051 (a
lockable isolator or DC contactor outside the zone, the DC never broken under load inside it),
its design and drawing still open with the DC bus.

## D-032 What the HAZOP drafts found missing, and what they judged not applicable (2026-11-05)
Decision: the studies analyse the plant as drawn; what it does not have is an action, never a
safeguard.
- Not drawn on either skid: a relief device; an H2-in-O2 measurement on O2V-x01; a pressure on
  the anolyte side (the pressure difference across the GDE is not known); a heater (TIC-x11 only
  cools); an eyewash or safety shower; a detector at the vents; CO2 or O2-depletion detection;
  a running signal of the fan K-x41; a UPS; the 48 V DC bus; a per-stack current or voltage.
  On Skid A: one level instrument on T-101 for the alarm and the trip (H01-A107), no high level
  for the fill (H01-A801). On Skid B: no check valve on KOH-204, no high level alarm on LIA-203,
  no written refill of T-202, no flush step in SEQ-B-DRAIN.
- Found in the review, on both skids: no valve or check valve on the recycle CO2-x02 and no
  check valve on W-x01; no check valve, flame arrester or shut-off on the tail gas TG-x01; no
  DC contactor or breaker independent of the rectifier; no trip that stops the oxidiser X-x32;
  no outlet for the cathode purge of SEQ-x-START S2 while K-x31 is stopped; SEQ-A-DRAIN, like
  SEQ-B-DRAIN, drains the tank only. On Skid B: no valve between T-202 and P-202 and no drain
  on T-202; no written handling of the AIC-201 probe that I-201 shares.
- Kept in the safeguard registers but credited by no scenario: the fail positions (they appear
  as causes), PIC-x31's low pressure alarm, I-207 (a permissive) and I-208 (it acts only when
  T-202 is already empty).
- Not applicable, or only partly (SESSION.md section 3.7): the dosing, bleed, make-up and the
  5 M KOH on Skid A (only as a wrong delivery, H01-S802); an anolyte heater; CO2 vaporisation
  inside the skid (beyond the battery limit, D-016; cold gas at the tie-in only); the tank
  height at long campaigns on Skid B (T-201 stays 50 L, D-010); the on/off and part-load duties
  on Skid B (D-013); back-flow through KOH-204 as drawn (a low scenario with an action to
  confirm, H02-S706).

Reason: a safeguard the files do not show cannot be credited (skill `safeguard-crediting`), and
a hazard the skid cannot have is recorded with its reason rather than left out silently.

Assumptions: the drawn levels of T-202 and the KOH-204 entry (about 0.69 m and 0.71 m), the
vent outlet heights of D-019, the zone screening of layout/zones.yaml (all ASSUMED).

Changed by D-050: the fan K-x41 and its running signal are no longer missing; the open skid has
no fan. CO2 and O2-depletion at low level are checked by the operator with a portable meter
(SEQ-x-START S1, SEQ-x-GAS S1), not by a fixed detector.

## D-040 The 3D model of the 1,000 h design to the layout-3d gate: routes, pins, proposals, details (2026-11-05)
Decision: the committed model (`layout/plant-model.yaml`, `cheme layout build`, core 1.5.0)
meets every requirement of gate `layout-3d` that the model itself can meet: model current,
nozzles resolved (93 nozzles: 41 from the P&ID side, 52 overridden, none by default), every
item above grade mounted on its frame's deck, routed or skipped, no clash, zones declared. The
`drawings` requirement is met by a layout review record that cites the plot plan and two
sections; that record is written by a reviewer who did not build the model (spec item 9), not
here.
- Routes: all 28 DN 25 lines of the line list (the process lines of the gate's `min_dn: 25`)
  are routed, 41 of the 99 P&ID segments; the 42 DN 15 lines (58 segments) are skipped with the
  reason of D-019 (skid small bore, run by the fabricator). 0 unrouted, 0 `direct` fallbacks.
- Pins (`cheme layout pin`, `piping/routing.yaml`): every route of Skid B (its equipment, T-201
  and T-202 included, is the same at both durations: the resize report's rows "invariant of
  duration" and "fixed by setpoint"), and on Skid A every route that does not end on T-101 (the
  manifolds of D-019, AN-102, FG-101): 36 pinned chains. The five routes that end on T-101
  (AN-101, AN-104 S4, KOH-101, SP-101, O2V-101) stay generated, because the reservoir and its
  nozzles change with the campaign (D-009, D-019): a pinned route would stay where the 1,000 h
  tank had its nozzle and break at 10,000 h (`layout-pipe-disconnected`). AN-104 S4 takes a via
  point instead (D-042).
- The hose couplings (battery-limit points of KOH-x01 and SP-x01) move from 0.2 m outside the
  frame's west edge to 0.15 m inside it: the hose valves HV-102, HV-103 and HV-203 then stand
  inside the frame in plan (HV-203 stood 0.43 m beyond it, at 20.066 m against the edge at
  20.5 m). On Skid A both couplings stand where the router leaves T-101's fill and drain
  nozzles (0.3 m out along their 145 degree axis, y 9.296 m) and at their elevations, so each
  line runs straight west to its coupling: KOH-101 at 1.324 m (generated with the coupling at
  0.9 m it doubled back over the deck, 2.19 m of pipe for a 0.9 m run, with 1.1 m of pipe on
  the hose side of HV-102; now 0.58 m, HV-102 0.29 m from the coupling) and SP-101 level at
  0.30 m. T-101's drain N5 and pump suction N4 stand 0.15 m above its floor (overrides in
  `layout/equipment-placement.yaml`; N4 from the P&ID side stood 0.011 m above P-101's suction),
  T-201's drain N5 0.10 m (0.25 m above grade, so HV-203's flanges clear the deck), and Skid
  B's drain coupling stands on the drain's level run at 0.25 m: neither drain line rises to
  its coupling any more (SP-101 rose 0.09 m to 0.4 m, SP-201 0.2 m, so the tanks could not
  drain by gravity below that; the heel that stays: D-043). The couplings sit behind the deck's
  guard rail (top rail 1.25 m above grade, mid rail 0.85 m): the KOH fill couplings above it
  (Skid A, 1.324 m) or between the rails (Skid B, 0.9 m), the drains below the mid rail;
  reached through or over the rail from grade. Whether the skid has a removable rail section
  there is the fabricator's (open, D-042).
- Transmitter stands: core puts an instrument connection's transmitter on a stand 0.6 m out
  from its flange. From the P&ID side, LT-201 (LIC-201) stood 0.24 m beyond the frame's north
  edge, LT-203 (LIA-203) on the metering pump P-202, AT-201 and LT-202 on one spot, LT-101 and
  AT-101 on one spot inside the 0.3 m side access of E-101A. Nozzle overrides in
  `layout/equipment-placement.yaml` (T-101 N6 40 deg, N7 320 deg; T-201 N6 315, N7 0, N10 270;
  T-202 N3 90; angles in each tank's own frame, elevations from the P&ID) put every stand inside
  its frame, on its own spot, clear of the items, pipes and stack access. No P&ID change.
- At 1,000 h no generated detail stands beyond a frame in plan any more (the record's
  `details_outside_plan` is empty for both skids). What stays above the 2.35 m envelope top, and
  may: the roof handrail and the ladder of T-101 to 2.886 m (core's tank family draws them on any
  tank, also on a 1.07 m skid tank that has no roof walkway; the fabricator's tank has none, or a
  removable rail, D-019), and the open vent and flue risers O2V-101 3.428 m, O2V-201 3.381 m,
  FG-101 and FG-201 3.417 m, raised by the ASSUMED 1 m vent sphere (D-019), fitted at site. At
  10,000 h the infeasible Skid A keeps its details beyond the frame (T-101 D 2.313 m): a result,
  reported in the record, not fixed (D-015, D-021).
- Proposals of the build, decided: the two ladders at the free ends of the utility rack PR-1
  (to its 2.8 m tier) are pinned (`layout/site-plan.yaml`). No platform, no valve access
  platform and no support steel is proposed (no nozzle or valve above 2.5 m, no free span over
  the DN 25 span); the build places no pipe support (`supports: []`: the shoe the base model
  had on SP-201 S2 went with that route's reroute, and no other run needs one), so the skid
  piping's supports are the fabricator's. The 30 step-overs the build proposes over the low DN
  25 runs on the decks (14 on SKID-A, 16 on SKID-B; step-over-28 and -29 of KOH-201 and SP-201
  share one point) are **not adopted**: the skid is worked from grade along its long sides and its 0.15 m deck is
  stepped onto, not walked across between the rows (D-019); a 0.8 m wide stair over each 0.2 m
  manifold would itself block the stack and pump access. Core 1.5.0 proposes a step-over wherever
  a pipe whose top is within 0.75 m crosses a grating and has no way to decline one, so they stay
  in the model as generated proposals (`review_needed`), drawn dashed; the take-off's
  `step-over` group is therefore not skid steel (for the MTO, spec item 4). Core's headroom
  rule skips a pipe on a deck altogether while a step-over is proposed on it, so the step-overs
  this record does not adopt hide headroom findings. Two runs are under the 2.1 m headroom
  over Skid A's deck and accepted in `checks/checks.yaml` with the reason of D-019 (the deck is
  not a walkway): KOH-101 at 1.32 m to its hose coupling (1.16 m clear, reported), and AN-104
  S4, rerouted (D-042) along the header at 0.6 m (0.43 m clear) and over T-101's top at 2.10 to
  2.23 m (about 1.9 m clear). AN-104 S4 is not reported by core 1.5.0 only because its low leg
  makes core propose step-over-13 on it (box 7.74 to 8.54 x 7.63 to 9.26 m, in front of
  E-101A); deleting that proposal from the model makes core report it (checked on a copy). Its
  acceptance is kept, so the finding stays accepted with its reason if the proposal goes.
- Structures and access (skill `structures-access`), checked on the model: each frame has two
  ways off its deck, the steps ST-x1 (south side, west end) and ST-x2 (east end), remote and
  outside the zone (no `layout-escape-*` finding); core draws a 1.1 m guard rail with mid rail
  and toe plate round each deck, broken at the steps (at 0.15 m a fall needs no guard rail by
  the usual rule of 0.5 m, to be confirmed by the site standard: the rails are kept as drawn); every manual
  valve (HV-x01 at 0.30 m, HV-x02 at 0.90 m, HV-x03 at 0.27 to 0.32 m above grade) and every
  transmitter (1.35 m) is within reach of the deck or of grade (no `layout-operability`
  finding); the motor removal envelopes of P-x01, K-x31, K-x41 and P-202 are free; the pump access
  boxes of P-101, P-201 and P-202 stay accepted as in D-019 (a 1 m box round a pump does not fit a
  2.44 m frame). The stack hand lift: D-042.

Rejected: pinning the routes that end on T-101 (they would break at 10,000 h); suppressing the
step-overs by raising the manifolds above 0.9 m (the stack connections sit at 0.20 and 0.28 m);
an enclosure round the frame (D-019).

Assumptions: the hose coupling points, the drain and suction nozzle elevations, the
transmitter positions, the rack ladders and the decline of the step-overs (all ASSUMED, for
the layout review).

Changed by D-047: the guard rail core draws on the 0.15 m deck is deleted in the design (kept in the model, left out of regen's checks), Skid A's KOH fill coupling stands at 1.0 m, the manifolds and every pinned route of the rearranged rows are new (36 pinned chains again).

Changed by D-050: the fans K-141 and K-241 and their motor removal envelopes are deleted.

## D-041 The plans and sections of the skids: core's A1 sheet cropped to the drawing (2026-11-05)
Decision: `scripts/regen.py` step 10 renders per scenario into `figures/skids/<H>h/` the plot
plan of the whole plot (`layout-plan.svg/.png`, core's A1 sheet as written: the 32 x 16 m plot
fills it at 1:50) and per skid its plan and four sections: across the reservoir and across the
first stack (x, looking west; the stack's hand-lift lane to the south side, D-042), along the
stack row and along the whole frame (y, looking north), named
`layout-plan-skid-<k>` and `layout-section-<x|y>-skid-<k>-<reservoir|stack|stacks|frame>` so
that a layout review record can cite them by the names core's `drawings` requirement looks for.
Each is core's `cheme layout render --crop` sheet with only its frame changed
(`scripts/_figures.py`): the viewBox cut to the drawing's clip region plus a margin, the grid
bubbles of the lines through the drawing moved along their line to its edge, the scale bar,
north arrow and title block moved into a strip under it, the title naming the view and saying
"A1 sheet cropped to the drawing", and the PNG rasterised from that SVG by resvg (the library
core's `--png` uses) at 10 px per sheet millimetre.

Deviation from the spec (item 7, "crop to the skid so the drawing fills the sheet"): core 1.5.0
draws every view on an A1 sheet at the largest standard scale that fits, and its largest is
1:50, so a 9 x 5 m skid view fills about a fifth of the sheet's width however tight the `--crop`;
there is no option for a larger scale or a smaller sheet. Cropping the sheet keeps the drawing
exactly as core drew it, at a true 1:50 (one SVG unit is one sheet millimetre, the scale bar is
core's), on a sheet that fits it. No `.glb` is committed: core 1.5.0 exports glTF and STL only
from the viewer's Layout 3D page in a browser, not headless; README says how to open the model
(`cheme serve`, `cheme export-static build/snapshot`).

Rejected: rasterising core's PNG and cutting it (4 px per mm, too coarse); redrawing the views
in the script (a second drawing code).

Assumptions: none (presentation only).

## D-042 The stacks' hand lift: column and carry lane checked by regen (2026-11-05)
Decision: a stack (0.18 x 0.176 x 0.18 m, top 0.33 m above grade) is replaced by hand: its
connections undone, it rises out of its seat and is carried across the frame to its south long
side, the aisle at grade where the access step ST-x1 is (the north side holds the 1.95 m gas
packages). `scripts/regen.py` step 13 checks per stack, against every solid of the model
(item bodies and their generated parts, pipes with their outside diameter, steel, trays,
supports; not the deck grating and not the step-overs, D-040):
- the **lift column**, the stack's plan grown by the side hand room of `process/cells.yaml`
  (0.3 m, ASSUMED, D-023) across its axis, from the stack's top up to the carry height plus the
  stack's height: nothing may cross it (an envelope reason, the skid infeasible otherwise);
- the **carry lane**, as wide as the column, from the column to just beyond the frame's south
  edge: the carry height is the top of the highest solid in it, reported with the next ones
  (record `skids.<k>.stack_lift`).
Results at 1,000 h, both skids: every lift column clear. The carry height is 1.125 m above the
deck (1.275 m above grade) for every stack, set by the deck's guard rail on the south edge
(D-040); without it, by the supply header AN-x03 S1 at 0.767 m (stacks A to C) and the separator
V-x21 at 0.761 m (stack D). The return riser AN-104 S4 rose at the tee 0.17 m in front of
E-101A to 1.93 m, in that stack's lane (carry 1.97 m); a via point at x 7.95 m makes it run west
along the header first and rise outside the lane. The stand of T-101's pH transmitter AT-101
(N7) is turned out of that lane too (D-040). At 10,000 h (scratch) the grown T-101 (D 2.313 m)
adds two reasons to Skid A's infeasibility: its anchor chair stands in E-101A's side access,
and T-101, HV-101 and AN-101 cross E-101A's lift column; Skid B is unchanged.
Open (for the layout review and the fabricator): whether a person at grade can hand a stack
over a 1.275 m rail at about 1.1 m reach, or the rail needs a removable section at the stack
row, or the stacks are lifted from the deck. The stack's mass is the estimate of D-043 only:
17.1 kg (outline 0.0057 m3 x 3000 kg/m3, ASSUMED), carried as 0.02 t in the equipment list,
the model and the datasheets (rounded up to 5 kg); the vendor's stack mass is still needed.

Reason: core sizes a stack's footprint with its access but models no lift envelope; the hand
lift of D-023 was asserted, not checked.

Assumptions: the hand room 0.3 m (D-023), the carry to the south side (all ASSUMED).

Superseded by D-047: the lift column and carry lane check is replaced by the reach and slide-lane check of the stacks at the frame's south edge (record `skids.<k>.stack_removal`).

## D-043 The lifting study: item weights, the skids as units, T-101 drained and full (2026-11-05)
Decision: the lifting study has two parts, both regenerated by `scripts/regen.py` and compared
by `--check`:
- `layout/lifting-study.csv` and `.md`, core's `cheme layout lifting --write` (regen step 23):
  every listed item of `heavy_lift_t` (5 t, package default, ASSUMED) or more, with its pad,
  lane and laydown. It lists **no item** at either duration: the heaviest listed item is the
  PSA package X-x31 at 0.435 t (ASSUMED) at 1,000 h, and T-101 empty is 0.085 t at 1,000 h and
  0.385 t at 10,000 h. The gate `lifting-study` passes on that (no unaccepted `-lifting` or
  `-laydown` finding, the study current).
- `layout/lifting-study-units.csv` and `.md` (step 23, `scripts/_lifting.py`): the lifts core's
  study cannot express, worked out with core's criteria and arithmetic (read from `cheme layout
  lifting --json`) on the committed model: each skid as a 20 ft unit, drained and with its
  tanks full, and T-101 alone, drained and full.

Weights (regen step 21, `layout/lifting-basis.yaml`, all ASSUMED: no vendor weight exists).
Every listed item's empty weight is written into the equipment list's `dimensions.weight`
(the key once by hand, its value by regen), so the model, core's study and the datasheets
carry it (core 1.5.0's datasheet draft copies the weight into `weights.empty` and
`type_specific.weight_t` without the list's `assumed` flag; regen step 10 sets
`assumed: true` on both in every draft datasheet whose list dimensions are assumed, all 28):
the outline volume of the list times a bulk density per kind (stacks 3000, pumps and
compressors with motor 1000, plate packs 1500, the separator pot 600, the fans and the rectifier
cabinet 500, the gas packages 400 kg/m3), a tank's shell, bottom and flat roof at 10 mm of PP
(905 kg/m3) plus 25 % for fittings, rounded up to 5 kg (a stack 17.1 kg, listed as 0.02 t). A
unit lift adds the frame's members as core draws them (its perimeter UPN140, corner posts and
guard rail, 0.53 t) at core's take-off mass per metre of each section, its deck grating at
35 kg/m2, a **base frame** that core does not draw at 40 kg/m2 of the footprint (0.59 t a
skid: cross-members and grating bearers about every 0.7 m, which a 2.44 m deck needs, lifting
lugs or corner fittings, the stiffening of a perimeter lifted at its corners; ASSUMED, the
fabricator's structural design replaces it; the first study had none, so the drawn perimeter
and rails stood for the frame) and 15 % of the items, the drawn frame and the grating for
what neither the list nor the model weighs (piping, valves, instruments, cable, bolting, drip
tray); the access steps ST-x1/x2 travel loose. A full tank
holds its outline volume (pi/4 D^2 H) at the anolyte density of the stack sizing (1050 kg/m3,
P-x01) or the dosing density of D-B (1.22 kg/L, T-202). A **drained** tank keeps its heel:
gravity empties it only down to the highest point of its drain line (regen reads it from the
model) or, with no drain, to its lowest outlet, and the heel is in every drained lift. T-101
drains through N5 at 0.15 m above its floor, level to its coupling: 0.136 m3, 0.143 t; T-201
through N5 at 0.10 m: 0.012 t; T-202 has no drain on P-02 and empties at best to its outlet N2
to P-202 (0.054 m): 0.010 t. (In the first study the drain lines rose to couplings at 0.4 m,
which would have left 0.25 m in each tank, 0.24 t in T-101, and the drained weights carried no
heel at all; D-040.)

Lift method and places (`layout/zones.yaml`, ASSUMED): the only vehicle access is the road R-1,
and the utility rack PR-1 (2.8 m tier) runs between the road and both skids along the whole
plot, so the skids are set and removed by a mobile crane standing on the road: crane pads CP-A
and CP-B opposite each skid (reach the package default 30 m), the laydown LD-R on the road
between them (a skid's trailer bed, 6.6 x 3 m), and LD-A1 at grade west of Skid A for T-101
(3.1 x 2.8 m, it also holds the 10,000 h tank). A load below `heavy_lift_t` that is not a skid
(T-101 alone) goes by hoist or forklift over the frame's west end onto LD-A1, carried at most
at 2.1 m (`carry_limit_m`, ASSUMED: the walkway headroom; a forklift or a hoist on a portable
gantry). Above it the study marks the lane blocked for that method (a crane lift), regen
warns, and the library test fails at 1,000 h; the first study only reported the carry height. Core draws the
road over the zones on the plot plan; regen step 10 now draws the road group first (only the
order of core's two SVG groups changes, `scripts/_figures.py roads_under_zones`), so the pads
and LD-R show on `layout-plan.png`.

Results at 1,000 h (`layout/lifting-study-units.md`):

| lift | weight t | method | needed t (radius) | lift / hook height m | lane, laydown |
|---|---:|---|---:|---:|---|
| Skid A unit, T-101 drained | 3.261 | mobile crane from CP-A | 5.02 (7.22 m) | 3.95 / 10.395 | clear (over PR-1 and its trays), LD-R |
| Skid A unit, T-101 full (not permitted) | 4.651 | mobile crane from CP-A | 7.16 (7.22 m) | 3.95 / 10.395 | clear, LD-R |
| T-101 drained (heel 0.143 t) | 0.228 | hoist or forklift | | carry 1.936 (limit 2.1) | over HV-102 (1.436 m), the deck rail (1.275 m), JB-101 (1.2 m); LD-A1 |
| T-101 full (not permitted) | 1.617 | hoist or forklift | | carry 1.936 | as drained |
| Skid B unit, tanks drained | 3.112 | mobile crane from CP-B | 4.79 (7.22 m) | 3.95 / 10.384 | clear, LD-R |
| Skid B unit, tanks full (not permitted) | 3.259 | mobile crane from CP-B | 5.02 (7.22 m) | 3.95 / 10.384 | clear, LD-R |

A drained skid is about 3.1 to 3.3 t (items 1.13 to 1.15 t, drawn frame steel 0.53 t, deck
grating 0.52 t, base frame 0.59 t, allowance 0.33 t, heel 0.02 to 0.14 t): below
`heavy_lift_t`, but a 6 m frame is lifted as a unit, so a crane (or a truck-mounted crane of
that class) is named for it. Every lift passes over the utility rack and the cable trays on it
and between it and the frames (D-045), which set the lift height (3.45 m + 0.5 m clearance;
3.3 m over the bare rack before the trays); the vent and flue risers (to 3.43 m, fitted at
site, D-040) set the skid's height in the hook height. Full lifts are the bound, not a lift:
the tanks are drained before a skid or T-101 is moved (procedure ASSUMED, for the lifting
plan). With every weight doubled, a drained skid would still need about 10 t of chart
capacity at 7.2 m at 1,000 h. T-101's drained carry rose from 1.775 to 1.936 m when its fill
line was straightened to run at the nozzle's 1.324 m (HV-102's lever, D-040).

At 10,000 h (scratch, `results/scenarios/10000h/record.json` key `lifting`): Skid A drained
4.125 t (T-101 empty 0.385 t and its heel 0.662 t: 0.15 m of a 2.313 m tank), with T-101 full
**18.77 t** (15.31 t of anolyte; 28.9 t chart capacity at 7.23 m, hook 12.054 m); T-101 alone
drained 1.047 t, its carry to LD-A1 over the trays PT-M-P-101 (2.95 m) and IT-JB-101 at 3.45 m,
**lane blocked** for a hoist or forklift (above the 2.1 m limit); T-101 alone full 15.69 t, a
crane lift (24.2 t needed, hook 10.67 m); and the drained skid has **no laydown**: with T-101's
ladder and details beyond the frame it is 6.81 x 2.83 m in plan (the plan of its own solids,
the cable tray runs taken off), larger than LD-R. Other reasons the 10,000 h Skid A is not a
20 ft unit (D-015); reported, not fixed. Skid B is unchanged.

HAZOP: the equipment list (weights only) and `layout/zones.yaml` (the pads and laydowns, outside
the hazardous zones) are analysed inputs of H-01 and H-02. `cheme safety hazop check` showed
only those two changed; no node's design intent, cause or safeguard depends on them (a lift is
made with the skid shut down, drained and gas-free; the stack hand lift's open item H01-A203
still needs the vendor's stack mass: the 17 kg here is an estimate, not that mass). No entry
added; both studies re-stamped (`cheme safety hazop stamp H-0x --write`), gate `hazop-current`
passes.

Rejected: lowering `heavy_lift_t` so that core's own study lists the skid items (every item on
a skid would need a crane lane over the skid's own pipes, which is not how they are handled);
lifting T-101 by crane over PR-1 (its lane is blocked by the rack at 2.8 m above its 1.76 m
top); a crane pad north or between the skids (no vehicle can get past the rack).

Open (lifting plan, fabricator, owner): the crane and its load chart (no
`layout/crane-chart.yaml`), outrigger spread and ground bearing on the 3 m road, the skid's
lifting points and spreader, the road closure, lifts over the live rack; the deck rail at the
west end, which T-101 must clear (removable section, as for the stacks, D-042); vendor weights
for every item; the skid's structural base frame and its weight (the 40 kg/m2 above); for the
P&IDs (not changed here): a bottom drain or a pump-out connection on T-101, T-201 and T-202
(none is drawn; a heel stays below each outlet, and T-202 has no drain at all), the
drain-before-lift sequence (SEQ-x-DRAIN ends on "LIA-x01 empty", which the drain cannot reach).

Assumptions: every weight and density above, the base frame, the heels, the pads, laydowns
and their sizes, the 15 % allowance, the 2.1 m carry limit, the drain-before-lift rule (all
ASSUMED).

Changed by D-047: the crane pads are 8 x 6.5 m hardstanding between the road and the skids with the rack moved north, T-101 alone is a crane lift from CP-A to the road laydown LD-R (LD-A1 deleted), X-x32 is no longer in the skid's unit lift; the results are D-047's.

Changed by D-053 (owner, 2026-11-06): the ASSUMED weights are accepted for basic engineering;
the open "vendor weights for every item" is narrowed to vendor weights of X-x31, X-x32, K-x31,
U-x01 and the stacks before detail engineering, each skid weighed at its factory acceptance
test before the first lift, and the lifting plan sized on at least the doubled-weight bound,
recomputed at the 5.47 m radius of D-047 (D-053). The P&ID items of the open list (T-x01 bottom
outlets, the drain-before-lift sequence) are the owner's anolyte draining decision, made with
the P&ID revision. The fans' 0.035 t each leave the unit lifts (D-050).

## D-044 The material take-off of the 1,000 h model; no estimate (2026-11-05)
Decision: `cheme assess mto --write` (regen step 22) writes `estimate/mto.csv` and `.md` from the
committed model; the gate `mto` (`mto-current`) passes. Totals at 1,000 h, as core counts them:
pipe 38.624 m (all DN 25, bare, 41 pipes), 40 elbows (37 x 90 deg, two 35 deg and one 20 deg
bend), 12 tees, 48 weld-neck flanges and 48 gasket sets, 6 DN 25 ball valves, steel 7.72 t,
grating 75.749 m2. At 10,000 h (record key `take_off`): pipe 45.577 m, 48 elbows, steel
7.72 t, grating 75.749 m2.
- **Every elbow can be built.** Core counts each bend of a route as a weld-in fitting. A DN 25
  long-radius elbow is 38 mm centre to end, so a leg needs 38 mm at a route's end and 76 mm
  between two elbows. The routes of the first take-off had 8 elbows on legs shorter than
  that (AN-102 and AN-202: a 25 mm jog and a 17 mm rise into the cooler's top nozzle, from
  below; AN-101: an 11 mm step between T-101's suction nozzle and P-101's; SP-101: 46 and
  89 mm legs and a 125 deg bend where the drain rose to its coupling), which inflated the
  count to 51. AN-102 and AN-202 are now pinned over the nozzle and down into it (one run
  with the 25 mm offset as a 2.3 deg skew, the fabricator's single offset), T-101's N4 and N5
  stand at P-101's suction level and the couplings on the lines' axes (D-040): every leg is
  81 mm or longer between elbows and 70 mm or longer at an end (regen's model, checked on
  every pipe). Core 1.5.0 has no minimum-leg rule: a route change can bring a short leg back,
  so the layout review should look for one.

How to read it:
- **Step-overs are not skid steel.** The `step-over` group (0.421 t of RHS50x50, 32.416 m2 of
  grating) is the 30 proposed step-overs that are not adopted (D-040); core 1.5.0 counts them
  and has no way to decline them. Without them: steel 7.289 t, grating 42.533 m2.
- **The rack dominates the steel**: PR-1's eight bents (HEB300 columns 5.242 t, HEB200 beams
  0.736 t) are core's default sections by span (ASSUMED placeholders, skill structures-access)
  for a notional one-tier rack that carries no modelled pipe; the skid frames are 1.06 t
  (UPN140 0.544, HEB140 posts 0.04, toe plates 0.127, guard rails 0.349 t), the access steps
  0.148 t and the rack ladders 0.103 t. The skid frames are what core draws: the perimeter,
  the corner posts and the guard rail; the cross-members, grating bearers and lifting points
  are not drawn and not counted (the lifting study carries them as an ASSUMED base frame,
  D-043).
- **What it leaves out**: the 42 DN 15 lines (skipped, D-019), the hose couplings, small-bore
  vents, drains and instrument connections, the in-line items on DN 15 lines (control valves
  among them), olets, all pipe supports (the build places none, D-040), cable and trays (core's take-off
  counts neither; the cables and trays are D-045's), the packages' own internals and all concrete (the skids stand on the plot without
  modelled foundations). The 48 flanges are core's count at the valves and the piped nozzles.

No estimate: `estimate/rates.yaml` is still core's example (`example: true`, currency XXX) and
the project has no documented cost basis (no quotation, cost database, published index or
handbook named with its edition and year). The unit rates and factors are therefore not
written and `cheme assess estimate` is not run (it would price nothing); `cheme assess
equipment` (CAPCOST) is not run either: it needs a CEPCI value with its source in
`estimate/cost-basis.yaml`, and most items (stacks, packages, rectifier) have no correlation.
When a cost basis exists, add the rates with their source and status and the gate's `rates`
and `estimate-current` requirements.

The LCA now depends on the take-off: core's `cheme assess lca` lists `estimate/mto.csv` among
its report inputs once the file exists, so both LCA datasets (`lca/dataset.yaml` and Skid B's
`lca/datasets/*-skid-b.yaml`) record its sha256 in their provenance, beside the equipment
list's. The screening does not use the take-off (construction is cut off in `lca/lca.yaml`),
but any change of the take-off makes the gates `lca` and `lca-case-dataset-current` stale
(checked on a copy: one line appended to `mto.csv` made both report `cheme.lca-dataset-stale`).
Regen runs the LCA (step 20) after the take-off (step 22), so a regenerated folder is current;
a hand edit of the model or the take-off needs a regen run, not only `cheme assess mto`.

Assumptions: the take-off's quantities are the model's (ASSUMED sections and outlines, D-019,
D-040); none added here.

Changed by D-047: the take-off of the rearranged model (pipe 36.195 m, 30 elbows, steel 8.456 t of which 7.571 t adopted, concrete 0.456 m3) is D-047's.

## D-045 Electrical: the electrical list, tray rules, cables in trays, the 48 V DC bus, the Ex assumption (2026-11-05)
Decision: `electrical/electrical-list.yaml` and `electrical/tray-rules.yaml` (hand-authored,
hashed regen inputs) give the plant's cabling to `cheme layout build` (regen step 10); regen
step 24 writes the cable schedule `electrical/cable-schedule.csv` and `.md` with `cheme layout
cables --write` and puts its summary into the record (`cabling`). The gate `electrical`
(`model-current`, `cables`, `trays`) passes. All values ASSUMED (no electrical load list, no
vendor data, no host-site standard).
- **Rooms**: the host site's 400 V board `SDB-1` and control room `CR-1`, off the notional plot
  east of PR-1 (`point`s, no building: the plot has none, D-019), the cables along PR-1 from its
  east end like the site tie-ins.
- **Loads**: seven motors (P-x01 0.18 kW, K-x31 0.37 kW, K-x41 0.25 kW, P-202 0.12 kW: the next
  IEC size above the flowsheet's estimates Q102/Q103, or assumed where nothing is sized; no
  datasheet gives a rating); AC feeders U-x01 4.1 kW (power factor 0.95: the rectifier's AC
  input on the same basis as its DC outputs, 4 x 48 V x 20 A = 3.84 kW DC over the efficiency
  0.95 of `process/cells.yaml` = 4.04 kW, rounded up; its operating duty is flowsheet Q101,
  3.164 kW, at about 37.6 V a stack; first written as 3.2 kW from Q101, below the DC rating
  the stack cables carry; 6.2 A, the cable size unchanged), X-x31 0.1 kW
  (Q104, 0.8), X-x32 0.5 kW (no flowsheet power: fan, igniter, burner management, 0.8). No heater
  exists (TIC-x11 only cools, D-032). Cable entries beside P-x01 (west) and K-x41 (south), so
  no tray drops into a stack's carry lane (D-042).
- **48 V DC bus, its own cable class**: one radial cable per stack (8) from its own DC output
  on the rectifier (overcurrent protection per stack in the cabinet, the HAZOP's D-031 item 9),
  rated 20 A (the stack current) at the 48 V bus rating. Core 1.5.0 has no DC class, so it is
  expressed with what core has: each output is a room of kind `mcc` at 48 V (`DC-x01A` to `D`,
  0.25 m apart on the router grid). Their points are **not on the cabinet**: they stand at
  3.1 m, 1.75 m above the cabinet top (1.35 m), 0.05 m north of its north face, DC-x01A also
  0.25 m west of it (first described as "at the cabinet top"). Points at the cabinet top were
  tried: core then runs the direct-fed DC trays at 1.35 to 2.35 m over the deck and out beyond
  the frame's north edge, under the walkway headroom. So the riser from the cabinet to 3.1 m
  (one tray for the four cables on a real skid) is not modelled: core's clash, fill and
  separation checks do not see it, and core's cable lengths leave it out. Regen step 24 adds
  it from the model (the plan distance from the cabinet's top face to the point plus the
  rise; record `cabling.dc_riser_m` and `dc_route_with_riser_m`): 1.80 m a cable, 2.005 m for
  DC-x01A, 14.81 m over the eight, so the DC cable is about 96 m rather than core's 81 m. Each
  stack is a feeder at 48 V
  with `power_kw` 0.96 (48 V x 20 A) and `power_factor` 0.57735 = 1/sqrt(3), which turns core's
  three-phase current P / (sqrt(3) U pf) into the DC current P / U = 20 A (it is no power
  factor); `rack_reach_m` 5.1 m reaches every AC load (the farthest terminal 4.95 m from PR-1)
  but not the DC outputs (5.25 m), so core feeds the DC cables directly from the rectifier
  ("no rack in reach" in the schedule) and they never share the rack's AC power tray. Each DC
  cable has a tray of its own (core gives every branch its own tray; on a real skid the four
  would share one). The size core prints, 4C x 2.5 mm2 of its 0.6/1 kV AC table, is a tray-fill
  placeholder: a DC cable is two-core or two single cores, and at 48 V the voltage drop governs:
  the longest, C-DC-E201B, runs 7.5 m in its tray and 1.8 m up the riser, 13 m with core's
  slack and terminations (route x 1.05 + 2 x 1.5 m), and 2 x 13 m x 7.41 ohm/km x 20 A is
  3.9 V, 8.0 % of 48 V at 2.5 mm2 (6 % on core's 10 m without the riser): the size is the
  electrical design's.
- **Instruments**: 39 field devices (17 on JB-101, 22 on JB-201), each a single-pair field
  cable; 14 placed from what their P&ID functions measure, 25 by points in the list: the
  actuated valves and transmitters on the DN 15 lines (skipped in the routing, D-019, so the
  model places neither their segments nor their in-line valves), the CO and H2 detectors
  (locations open with the gas detection study, D-031 item 5) and JIC-x01, the rectifier's
  current signal and run/trip command. Core gives every field device one pair; for JIC-x01
  that undercounts: one pair cannot carry the 4-20 mA current signal, the run command and the
  trip, and the trip is the final element of every interlock of its skid (I-x01 to I-x06),
  which the safety I/O may need on its own cable, apart from the BPCS junction box (CR-1 is
  "PLC and safety I/O", every interlock `sil: null`). With three pairs for each rectifier and
  the 20 % spare, JB-101 needs about 23 pairs and JB-201 about 29: the 24- and 36-pair home
  runs still hold, only the field cable count and its pairs are low (open, below). Motor start
  and stop and P-101's speed reference are wired at the host site's board SDB-1 and its drive,
  off the plot, so no field control cable is listed for them. One junction box per skid on the frame's south edge west
  of the stack row (0.8 m, outside the zone 2, the stacks' carry lanes and below the rail
  T-101 is lifted over), a 24-pair and a 36-pair home run to CR-1 along PR-1's instrument lane.
- **Trays**: PR-1 carries no modelled pipe, so the trays use its 2.8 m tier: tier 2.85 m (core
  checks a tray as a capsule of half its width round its bottom centreline, so a tray resting
  on the beam at 2.8 m reads as a clash: 2.85 m is the lowest tier that does not; core then
  generates a 50 mm column stub and a second HEB200 beam per bent overlapping the rack's own, a
  model artefact core's take-off does not count); branches at 2.5 m or higher; router grid
  0.25 m. Every tray is 100 mm wide (fill 2 % to 23 %), power and instrument trays keep 0.3 m,
  no tray-fill, -separation, -voltage, -span or clash finding.

Results at 1,000 h: 62 cables (21 power: 7 motors, 6 AC feeders, 8 DC; 41 instrument: 39 field,
2 multipair), 0 without a cable, 0 unrouted, 40 trays 182.0 m, cable 731 m (436 m of power
cable, 81 m of it DC, without the 14.81 m of DC riser core does not count; 295 m instrument). At 10,000 h (scratch): 62 cables, 739 m; the grown
T-101 now meets the cabling too: IT-JB-101 runs through T-101's shell (JB-101 stands in the
grown tank) and PT-M-P-101 through AN-101 (reported in the record, not fixed).

Ex assumption (ASSUMED; no certification is claimed): the electrical items in each skid's zone 2
(the motors of P-x01, K-x31, K-x41, the PSA package X-x31, the stacks' DC terminals, the
transmitters, valves and gas detectors there) are of equipment group II, gas group IIC (H2),
category 3G, and the cables entering the zone are armoured with glands certified for it; the
rectifiers and the junction boxes stand outside the zone. The 12 trays that drop into the zone
to a load in it (`layout-tray-zone`: the K-x31 and K-x41 branches and the eight DC trays; the
PSA's tray ends 1.5 m above its zone source, over the package top) are accepted in `checks/checks.yaml` with that assumption. The Ex rating stays the
owner's open decision of #330 (D-031 item 12) with the area classification; the oxidiser X-x32
is a flame and cannot be Ex-rated (D-031 item 14).

What the trays change in the layout (regen steps 13 and 23):
- The trays over the frames run at 2.5 to 3.95 m, above the 2.35 m envelope: like the vent
  risers they are site-fitted (11 on Skid A, 12 on Skid B, reported by step 13, not counted in
  the envelope). Two DC trays leave a frame's edge by up to 0.1 m (east) and 0.06 m (north).
  IT-JB-201, Skid B's instrument home run, drops at PR-1 to 2.1 m (bottom; core keeps it 0.3 m
  below the 2.5 m power branches) and runs at 2.1 m from the rack across the grade aisle
  between PR-1 and Skid B (y 4.2 to 7.45 m, 2.75 m along with a 0.25 m jog): the aisle where
  the stacks are carried out (D-042) and the pumps are maintained from grade (D-019), at
  exactly the 2.1 m headroom with no margin. It rises to 2.5 m only for its last 0.25 m over
  the frame, so step 13, which looks at the trays over a frame only, does not see the aisle
  run. For the layout review (open, below): accept 2.1 m there or raise the run above the
  power branches (2.9 m). IT-JB-101 crosses Skid A's aisle at 2.35 m, the power trays at
  2.85 or 3.35 m.
- The stacks' hand lift (D-042) passes under what hangs over its lane above the envelope top
  (the trays); the carry height stays 1.125 m above the deck and every lift column is clear.
- A skid's unit lift takes the tray runs over its frame off first (their cables disconnected
  at the frame edge); the runs between PR-1 and the frame and the trays on the rack stay, so
  the lift height over PR-1 rises from 3.3 to 3.95 m and the hook height to 10.395 m (Skid A)
  and 10.384 m (Skid B); both lanes stay clear. The trays do not change T-101's drained carry
  (1.936 m, set by HV-102 on its fill line, D-043).

Rejected: a building or container for an electrical room on the plot (no basis for one on a
notional plot, and it would change the plot plan, the lifting lanes and the take-off); the DC
cables as ordinary 400 V feeders (they would run on the rack's AC tray); `power_trays` classes
for the DC bus (core's classes are by the 1 kV LV/HV limit: 48 V and 400 V are both `lv`); one
DC cable per skid to a DC box at the stack row (the per-stack protection would stand in the
zone 2).

Open (for the electrical engineer, with the HAZOP actions): the load list and every rating;
cable sizing (voltage drop at 48 V first), protection, earthing, the DC bus design and
isolation (D-031 items 9 and 17), the UPS (item 7); the skid's own cabling, which a fabricator
runs inside the frame or under the deck within the envelope (core routes every branch at
`branch_elevation_m` and cannot run a tray under a deck); the host site's real supply point and
control room; the junction boxes' and detectors' final locations; the DC riser from each
rectifier cabinet (not modelled, above) and the rectifier's rating and nameplate; the
rectifier interface JIC-x01 (at least three pairs, the trip possibly on its own cable to the
safety I/O, above); IT-JB-201's 2.1 m run over the south grade aisle (for the layout review).

Changed by D-047: the rack, the rooms' points and the junction boxes move north of the skids, `rack_reach_m` is 5.5 m, the DC trays run from the rectifier at the north-east corner to the stacks at the south edge and no longer enter the zone; a regen check keeps every tray 1 m from the vent and flue outlets.

Changed by D-050 and D-051: five motors (the extract fans K-x41 and their cables are deleted
with the enclosure); the Ex assumption above is replaced by the owner's Ex decision (D-051:
motors II 2G Ex db eb IIC T3 Gb, instruments Ex ia IIC T4 Ga with barriers or isolators outside
the zone, IIC gas detectors, 3G/Gc the stated minimum, armoured cables and IIC glands, the DC
drops to the stacks protected as review 2026-11-05-layout-r2 #6 asks). The open items stand,
but the DC isolation is decided in principle there.

## D-046 The 3D results in the record, the regeneration of the 3D artefacts, their tests (2026-11-05)
Decision: regen step 25 (after step 13, numbered after the existing steps) writes the scenario's
3D results into the record's `layout` block, at every duration: from `cheme layout report
--json` the process lines of DN 25 and above routed, skipped with their reason or unrouted (a
warning), the smaller lines by status, the route methods (a `direct` fallback is a warning), the
model rule finding counts and the generated / pinned / declared counts; from step 13's `cheme
validate --json` every `cheme.layout-clash*` finding with its level and whether
`checks/checks.yaml` accepts it; and per skid the items' top against the envelope. With the
record's `lifting` (step 23) and `cabling` (step 24) these are the scenario's clashes, heights
and lifts; at 10,000 h they are reported for the infeasible Skid A and never fail the run (exit
0). The record was so far the only place where the 10,000 h model's results survive (its model
files stay in the `--scratch` copy, D-021), and its clashes were only in finding texts.
- **Every generated 3D artefact is regenerated and compared** (audit of steps 10 and 21 to 25):
  the model `layout/plant-model.yaml`, the take-off `estimate/mto.*`, both lifting studies
  `layout/lifting-study*.*` and the cable schedule `electrical/cable-schedule.*` are written by
  `--duration H` and compared by `--check` at the design duration (`MODEL_FILES`); the plot
  plan, plans and sections (`figures/skids/<H>h/`) and the record at both durations. A drift
  test in a copy (a line appended to `estimate/mto.md` and to the cable schedule, a value of the
  record's `layout` block changed) made `regen.py --check --duration 1000` report exactly those
  three files (exit 3). The hand-authored intent (`layout/*.yaml` but the model,
  `piping/routing.yaml` with its pins, `layout/lifting-basis.yaml`, the electrical list and the
  tray rules) is input: hashed in the record (`inputs_sha256`), never written.
- **Results.** 1,000 h: 28 of 28 DN 25 lines routed (0 skipped, 0 unrouted; the 42 DN 15 lines
  skipped, D-019), methods 36 pinned, 3 astar, 1 via, 1 open end, no direct; 0 clash findings;
  both skids' items top 1.95 m against the 2.35 m envelope. 10,000 h (scratch): 28 of 28 routed,
  no direct (two segments on core's coarse grid, one of them through its via); 4 clash findings, none accepted (T-101's ladder
  rail through the SKID-A deck handrail, an error; AN-101 through E-101A, whose suction nozzle
  N4 the grown tank brings to 0.24 m from the stack; trays IT-JB-101 through T-101's shell and
  PT-M-P-101 through AN-101, warnings); Skid A's top 3.62 m, 1.27 m above the envelope; Skid B
  unchanged; the lifts as in D-043 (Skid A no laydown, 18.77 t with T-101 full, T-101 drained
  lane blocked for a hoist or forklift).
- **Tests** (`tests/test_co2_electrolysis_bpm_skids.py`): E8 now names what it covers (T-101,
  T-201, T-202 and the eight stacks, at both durations). `assert_layout` checks the records'
  layout block: at 1,000 h every DN 25+ line of the line list routed, no direct route, no clash
  finding (accepted or not), both skids inside the envelope height, every permitted unit lift
  with a laydown and either a clear crane lane or a hoist or forklift carry no higher than the
  basis's carry limit (the first test accepted any carry height, so a blocked carry could not
  fail it); at 10,000 h Skid A's clash, height, missing laydown and T-101's blocked carry
  reported. It runs on the committed records (fast) and on the regenerated ones (marker
  `engineering`). The engineering run also runs core's gates `layout-3d`, `lifting-study`
  (`lifting-current`), `mto` (`mto-current`) and `electrical` on the regenerated 1,000 h folder
  and compares the model, take-off, lifting studies and cable schedule with the committed bytes.

Deviation: `cheme check` 1.5.0 has no option to run chosen gates, so the test writes a
`checks/checks.yaml` holding one gate (with the file's own acceptances) into its temporary copy
and runs `cheme check --no-write` once per gate. The `drawings` requirement of `layout-3d` is
left out there: it needs a layout review record (spec item 9, gate `layout-review`), which an
independent reviewer writes; once that record is committed the requirement can be put back.

HAZOP: this change touches no analysed input of H-01 or H-02 (only scripts, the records and the
documentation); `cheme safety hazop check` reports no `hazop-input-changed` at 1,000 h, so the
studies are not re-stamped. The 10,000 h scratch run reports `hazop-input-changed` for the
equipment list, loops, flowsheet and duties, as before: the studies analyse the 1,000 h design.

Rejected: failing the 10,000 h run on its clashes (the infeasible scenario is a result, D-023);
a separate 3D results file per scenario (the record is already the scenario's calculation
record, compared by `--check`); counting only unaccepted clashes as clashes at 1,000 h (an
accepted clash is still a clash; there are none).

## D-047 The layout review fixes: stacks at the frame edge, ignition sources out of the zones, the rack north (2026-11-05)
Decision: the eight high and medium findings of the agent layout review
`reviews/2026-11-05-layout.md` (verdict fix, #1 to #8) are fixed in the layout, and each fix is
checked by regen or core where a check can be made; what needs a P&ID change is an open item
below (the spec forbids P&ID changes at this stage). The review record itself is not edited, so
gate `layout-review` now reports it stale: the changed layout needs the next review round. The
four low findings (#9 to #12) are not in this round; #9 (IT-JB-201's 2.1 m aisle run) disappears
with the rack's move, #10 is partly covered by the vent rule below. New project file
`layout/layout-checks.yaml` (hand-authored, hashed regen input) holds the criteria of the new
regen step 13 checks.

1. **Stacks within reach (#1).** The rows are rearranged (`layout/equipment-placement.yaml`):
   the four stacks stand in one row along the frame's south long side, 0.11 m in from its edge
   (Skid A x 9.30 to 10.74 m, Skid B 24.45 to 25.89 m, y 7.70 m), with the pump and the cooler
   west of them on the same edge; the separator in the middle, the PSA and the compressor on the
   north side. Every stack connection is on the stack's north end plate (anolyte in at 0.225 m,
   out at 0.28 m) or on its top (the DN 15 CO2 inlet and cathode gas outlet), so nothing stands
   between the stack and a person at grade at the edge. The stack is no longer lifted by hand:
   with its connections undone it slides out south over the frame edge at deck level onto a
   deck-height trolley or lift table (ASSUMED handling aid, the fabricator's procedure). Regen
   step 13 replaces the lift column and carry lane of D-042 by two checks (`stack_removal`,
   each a feasibility reason when it fails): the stack's far end plate within `reach_m` 0.6 m of
   the standing position (0.15 m behind the frame edge, the ankles; the review's criterion and its
   NIOSH reading, not re-checked here), and its slide lane, as wide as the stack, from the stack
   to 0.3 m beyond the edge and from the deck to the stack top plus 0.05 m, free of every solid
   but the stack's own parts and the deleted rail (item 8). Result at both durations, both skids:
   reach 0.438 m for every stack (far face 0.288 m from the edge), every slide lane clear. The
   stacks' 0.3 m hand room of `process/cells.yaml` stays checked as before. The stack mass is
   still the estimate (17.1 kg, D-043); the vendor's mass and handling instruction are open (HAZOP
   H01-A203, H01-A206, H02-A205, H02-A208).
2. **The oxidiser out of the zone (#2).** X-x32, an open flame, stands off the frame on its own
   0.15 m concrete plinth at grade east of its skid (X-132 at x 14.0, X-232 at 29.0 m, y 8.3 m),
   beyond the east access step, 3.0 m or more from the outline of every zone source; it is no
   longer a zone source in `layout/zones.yaml`. Its tail gas TG-x01 (DN 15, not routed) is
   ASSUMED to leave the PSA through a flame arrester at X-x31's outlet, inside X-x31's own zone,
   and to be all-welded from there to the burner, so no flanged joint of it stands outside the
   declared zone. No position on the frame met the radius-plus-margin rule of item 3 for both the
   rectifier and the oxidiser beside a stack row within reach (the stacks, separator, compressor
   and PSA fill the 3.6 m east of the reservoir's reserved circle). The oxidiser is therefore no
   longer part of the 20 ft unit: the unit lifts lose its 0.145 t, the plinths and foundations
   are the take-off's 0.456 m3 of concrete. Its flue FG-x01 rises straight from its top to
   3.217 m (no walking level near it), pinned.
3. **Margin to the source outlines (#3).** Regen step 13 checks every ignition source of
   `layout/layout-checks.yaml` (U-101, U-201, X-132, X-232) against every sphere of every
   hazardous zone: the distance from its outline to the outline of the sphere's source item (to
   the point of a nozzle source) must be at least the sphere's radius plus 0.5 m (an error
   finding when short). The rectifier stands at the frame's north-east corner: least clearance
   1.550 m (U-x01 to K-x31; V-x21 1.57 m, E-x01D 1.58 m) against the 1.5 m required, on both
   skids; X-x32 more than 3 m. Declaring the sources at the flanges was not chosen: the package
   flanges are not known, and the outline rule bounds them.
4. **Drain and vent of the anolyte loop (#4).** The supply header runs level at 0.225 m from
   the cooler's lower east connection (E-x11 N2 moved to the cooler's east face, its inlet N1 to
   the upper west face), so AN-x03 S1 no longer rises above the cooler: the loop's high point on
   the supply side is the cooler's own top channel, and the 0.9 m loop over the header is gone.
   AN-204 S4 is pinned along the header's level and over T-201 at 0.96 m, 0.08 m above its inlet
   (it rose to 1.18 m), falling into the tank's gas space; AN-104 S4 still rises over T-101 to
   2.228 m and falls into its top nozzle (generated, T-101 changes with the campaign), its high
   point vented through the tank. The low point of each loop is the supply header's east end,
   stack D's stub, below the tank drain (0.30 / 0.25 m): it cannot drain to the tank by gravity.
   **Open (P&ID, not changed here):** a low-point drain at the east end of each supply header and
   a high-point vent at each cooler's anolyte outlet, both into SEQ-x-DRAIN before a stack is
   opened (HAZOP H01-A111, H02-A802, now H01-A206, H02-A208).
5. **Trays clear of the vent outlets (#5).** Regen step 13 checks every cable tray against the
   open end of every `FG-*` and `O2V-*` line: no tray within 1.0 m (the vent sphere radius,
   ASSUMED) of the outlet, and none above it within 1.0 m in plan (its plume), a warning
   otherwise; the record's `layout.vent_tray_clearance` lists them. The DC trays now run from the
   rectifier at the north-east corner to the stacks at the south edge, nowhere near a flue
   (FG-x01 is 2.8 m east of the frame). To keep the O2 vents' clearance, T-201's vent N2 moved
   to the tank's west edge (O2V-201 at x 22.275 m), the metering pump P-202 north of its day
   tank (T-202's level connection N3 turned east for its transmitter stand) and P-201's cable
   entry 0.225 m east of the motor's middle. Result at 1,000 h and 10,000 h: none. The flue
   temperature (150 degC, ASSUMED, S111) and the oxidiser's design temperature stay the
   vendor's (open).
6. **Hardstanding for the crane, the rack north of the skids (#6).** The utility rack PR-1 moves
   from between the road and the skids to their north side (y 13.5 m, `layout/site-plan.yaml`),
   its tier raised to 3.2 m (trays at 3.25 m; core's tray legs then run at 2.5 m or 4.0 m, never
   at the 2.1 m they took under a 2.85 m tier). The crane pads CP-A and CP-B are now 8 x 6.5 m
   of hardstanding from the plot edge over the road and 3.5 m north of it (to 1 m from the
   frame, clear of the south access steps), with no rack in the lift lane. The skids' unit lifts
   (Skid A drained 3.091 t, gross 3.57 t, 4.76 t of chart capacity at 5.47 m, 19.5 t m; Skid B
   2.943 t, 4.53 t at 5.47 m) have clear lanes and LD-R on the road as laydown. The outrigger
   spread and ground bearing are the lifting plan's (no crane chart), but the plot now reserves
   the space. The site's 400 V board SDB-1 and control room CR-1 stay off the plot at the rack's
   east end; the junction boxes JB-x01 stand at grade north of each frame (outside every zone,
   beside the instrument lane to the rack), and `rack_reach_m` is 5.5 m: the AC loads are within
   it, the stacks' DC points (5.8 m) beyond it, so the 48 V DC cables stay off the rack's AC
   tray as before (D-045).
7. **T-101 off the plot (#7).** T-101 alone is a crane lift from CP-A, on the same basis as the
   skid lifts (`method: crane` in `layout/lifting-basis.yaml`, `scripts/_lifting.py`): drained
   0.228 t with its 0.143 t heel at 5.74 m, lane clear, onto a trailer on LD-R, and by the road
   off the plot; LD-A1 is deleted. The tray branch to P-101's motor crosses the lane at 2.5 m;
   it is site-fitted and swung off first (`off_first`, as the trays over a frame before a unit
   lift). The ground between the road and the skids is now free, so a forklift reaches the frames
   too. **Open (P&ID):** a bottom drain or pump-out on T-101 to remove the heel (D-043).
8. **The deck guard rail and the hose couplings (#8).** The 0.15 m deck has no guard rail and no
   toe plate (fall height under 0.5 m, EN ISO 14122-3 as the review cites it, to be confirmed by
   the host site's standard). Core 1.5.0 draws a rail, mid rail, toe plate and posts on every
   deck edge and has no option to leave them out, so they stay in the model and its drawings and
   are listed as `deleted_steel` in `layout/layout-checks.yaml`: the stack removal check leaves
   them out, the T-101 lift is a crane lift over them, and the take-off counts them (0.471 t,
   below). The KOH fill couplings stand at the frame's west edge (0.15 m in) at a working height:
   Skid A's moved from 1.324 to 1.0 m (KOH-101 falls from T-101's N3 to it), Skid B's at 0.9 m.
   The drain couplings stay low (0.30 / 0.25 m), because the tanks drain by gravity: a drain at
   working height needs a pump-out (the P&ID item of 7). Not modelled, for the fabricator: a drip
   tray or bund under the hose station and a spray shield (HAZOP D-031 item 3, H01-A106).

Take-off at 1,000 h (`estimate/mto.md`): pipe 36.195 m DN 25 (38.624 m before), 30 elbows (40),
12 tees, 48 flanges and gasket sets, 6 ball valves; steel 8.456 t, of which the not-adopted
step-overs 0.414 t (30 proposals, D-040) and the deleted deck rail and toe plates 0.471 t, so
7.571 t adopted; PR-1 6.726 t of it (HEB300 columns 5.99 t, longer at the 3.2 m tier); grating
74.149 m2 (42.533 m2 without the step-overs); concrete 0.456 m3 (the oxidisers' foundations and
plinths, the first concrete in the take-off). Every elbow can still be built: shortest leg
between two elbows 0.094 m, at an end 0.045 m (AN-201's pinned suction), against the 76 / 38 mm
of D-044. Cabling (`electrical/cable-schedule.md`): 62 cables (21 power, 8 of them 48 V DC; 41
instrument), 0 without a cable, 40 trays 190.7 m, cable 851 m; no tray-zone finding but the two
compressor motor branches (accepted as before; the DC and fan trays no longer drop into a zone),
the ten acceptances that no longer name a finding removed from `checks/checks.yaml`. Routes: 28
of 28 DN 25 lines (36 pinned chains, 3 astar, 1 via, 1 open end), 0 clash findings. 10,000 h
(scratch, record): one clash (T-101's ladder rail through the deck rail, an error; the three
others of D-046 are gone with the rearrangement), Skid A's top 3.62 m, Skid A drained 3.955 t
without a laydown (its plan beyond the frame), T-101 alone drained 1.047 t, now a crane lift with
a clear lane; reach, slide lanes, ignition clearances and vent clearances as at 1,000 h.

HAZOP: `layout/zones.yaml` (an analysed input of H-01 and H-02) changed. `cheme safety hazop
check` reported only that input; the change matters to H01-S206 / H02-S206 (the stack handling)
and H01-S906 / H02-S906 (the oxidiser as an ignition source), so four actions are added as
proposals (H01-A206, H01-A907, H02-A208, H02-A907) and linked to those scenarios; no rating is
changed (the team re-rates). Both studies re-stamped, gate `hazop-current` passes.

Rejected: a 0.6 m standing strip on the deck along the old middle row (it costs the frame width
the rows need) and a davit or trolley beam over it (a lift at 1.2 m reach is still a lift at that
reach); keeping X-x32 on the frame at its east end (within 1.5 m of the stack row or the
compressor wherever it stands); declaring the zone sources at assumed flange positions; a
removable rail section instead of no rail (a rail a 0.15 m deck does not need); keep-clear zones
round the vent outlets for the tray router (they would also forbid the vent's own pipe, and move
with T-101 at 10,000 h).

Assumptions: the rearrangement, the stack connections on the north end plate and the top, the
deck-height trolley, the 0.6 m reach and 0.15 m ankle offset, the 0.5 m ignition margin, the 1.0 m
vent clearance, the flame arrester and all-welded tail gas line, the plinth, the rack's new
place and height, the hardstanding, the coupling heights, the deleted rail (all ASSUMED).

Changed by D-050 to D-053 (the owner's decisions of 2026-11-06): with the extract fans deleted
the unit lifts are Skid A 3.051 t and Skid B 2.903 t drained, and the cabling 60 cables in 36
trays (D-050); the rectifier, the zones and the ignition margins are unchanged; the doubled-weight
bound at 5.47 m is D-053's.

## D-048 Publication: public under CC-BY-4.0 (2026-11-06)
Decision: the process is public (`publication.status: public`, licence CC-BY-4.0), as ADR 0036
makes the default; the owner decided this on 2026-11-06.

Why it was internal: #373 made it public on 2026-11-05 by an edit of `process.yaml` alone.
`process.yaml` is a fingerprinted input of `lca/manifest.json`, both datasets and the 11
`lca/scenarios/*.json`, so the public build (`scripts/publication.py` `lca_withheld`) found a
stale run manifest and withheld the footprint. The website's `check-public.mjs` then reads every
text of a withheld footprint that pairs a number with CO2 as a possible leak and failed 37 times:
the Ember attribution, `goal`, `technology`, the scenario records' `title`, and one `data_year`.
None of them states a footprint value; #378 made the process internal again.

The fix is the order of the change, not the text: the status and the LCA outputs are changed in
one commit. `cheme assess lca --write`, `--write --case skid-b` and `cheme assess lca-scenarios
--write` (core 1.10.0) change only the `process.yaml` fingerprint in those 14 files; no number
changes. The footprint is not withheld for a licence: both backgrounds are open (ember-2025
CC-BY-4.0, desnz-ghg-2026 OGL-3.0) and core marks them publishable. It is published as what it
is, a partial climate-only screening with its 13 gaps (ADR 0026, D-026).

Consequence: any later edit of `process.yaml`, the flowsheet, `lca/lca.yaml` or the factors is
committed together with the regenerated LCA outputs (`scripts/regen.py` does both); otherwise
the public footprint is withheld again and the public check fails.

## D-050 Open, naturally ventilated skids: no enclosure, no extract fan (2026-11-06)
Decision: the owner delegated the open decisions of #330 on 2026-11-06 ("make reasonable
decisions and move on"); this one comes first, because the Ex rating, the zones and HAZOP node
N9 depend on it. Both skids are **open and naturally ventilated**:
- no enclosure, casing walls or roof over the gas train; at most a rain canopy over the
  rectifier U-x01 and the junction box JB-x01, both outside the zone. Whether any roof over the
  gas train is acceptable is the competent person's to judge with the area classification;
- the extract fans K-141 and K-241 are deleted: from the equipment list, the electrical list
  (two motors and their cables), the placement, the lifting basis, the datasheets, the cause
  and effect (I-x03, I-x04 no longer start a fan; their titles name the place at the skid), the
  sequences (SEQ-x-START S1, SEQ-x-TRIP's abort, SEQ-x-GAS S1 and its abort), the instrument
  services of AIA-x41/x42, the philosophy (F-GAS, F-POWER), the narrative and the comments of
  `layout/zones.yaml`, `layout/equipment-placement.yaml` and `checks/checks.yaml`;
- kept: the CO detectors AIA-x41 at the compressor and the PSA and the H2 detectors AIA-x42
  high over the stack row and the PSA (locations ASSUMED, for the gas detection study, D-031
  item 5); added as operating practice: a personal CO monitor for everyone at the skid
  (H01-A902) and a CO2 (and O2) check at grade and at the low points round the skid with a
  portable meter before work and after a gas trip (SEQ-x-START S1, SEQ-x-GAS S1).

Why: the zones of D-019, the ignition margins of D-047 and the south slide-out of the stacks
all assume an open skid. In the open, H2 is buoyant and disperses quickly; an enclosure would
trap it under its roof and turn a CO leak into a confined toxic atmosphere. Making an enclosure
safe would need extraction sized for the release, proven running, on a UPS and of "good"
availability (IEC 60079-10-1), disproportionate at 0.1 kg/h of CO.

Rejected: an enclosed skid. It needs the zones re-classified from the ventilation, U-x01 moved
outside or purged (IEC 60079-2), a panel along the stack row, the fan's discharge declared a
release point, and the ventilation proven and on a UPS.

Consequence: results at 1,000 h (regen): each skid's items lose the fan's 0.035 t (Skid A
drained 3.051 t, was 3.091 t; Skid B 2.903 t, was 2.943 t; 4.70 and 4.47 t of chart capacity at
5.47 m); the cable schedule has 60 cables (19 power, 8 of them 48 V DC; 41 instrument), 36 trays
175.7 m, cable 793 m (was 62, 40 trays, 851 m); routes, clashes, envelope heights and the
take-off are unchanged. An open skid outdoors in the Netherlands needs winter protection of the
1 M KOH loop (D-052, H01-A105). The drawing module `scripts/_skid_pid.py` still draws K-x41 on
P-01 and P-02 until both sheets are regenerated once with the P&ID revision of the owner's other
decisions; until then `cheme validate` warns `cheme.equipment-not-listed` for K-141 and K-241.
HAZOP: node N9 ("the enclosure") and the causes and ratings that assume an enclosure are to be
revised as proposals by their stable ids, for the team (skill hazop-review; an agent never
accepts), and both studies re-stamped; until then gate `hazop-current` fails.

Open: the gas detection study (number, location, set points, voting; D-031 item 5); the canopy
and any roof, for the competent person.

## D-051 Ex protection in the screening zones (2026-11-06)
Decision (the owner, 2026-11-06; ASSUMED until the area classification, no certification is
claimed): inside the screening zones Z-HAZ-A and Z-HAZ-B (`layout/zones.yaml`, zone 2):
- **motors** (P-x01, K-x31, P-202 and any other): II 2G Ex db eb IIC T3 Gb (Ex eb acceptable),
  their non-electrical ignition sources to EN ISO 80079-36/-37 (the compressor's and the
  pumps' mechanical parts);
- **transmitters, analysers, positioners and solenoids**: intrinsically safe, Ex ia IIC T4 Ga,
  with their barriers or isolators outside the zone (in JB-x01 or at CR-1);
- **gas detectors**: certified for gas group IIC;
- **minimum stated**: 3G / EPL Gc, the minimum for zone 2 (IEC 60079-14, ATEX 2014/34/EU);
- **the PSA package X-x31**: delivered with the vendor's ATEX assembly assessment;
- **the PP tanks** T-101, T-201, T-202: earthed and bonded against electrostatic charge to IEC
  TS 60079-32-1;
- **cables**: armoured, entering the zone through IIC-certified glands. The DC drops to the
  stacks (review 2026-11-05-layout-r2 #6): armoured cable, IIC glands and shrouded, IP-rated
  stack terminals;
- **the rectifier** U-x01 (a non-Ex cabinet outside the zone): its AC supply isolated at SDB-1
  on gas detection (the U-x01 trip of I-x03 and I-x04 opens its feeder, H01-A204); the DC is
  never broken under load inside the zone: a lockable isolator or a DC contactor stands outside
  the zone, at the rectifier (H01-A205, H02-A207).
The markings are stated in the hand-maintained sources (equipment list, electrical list and
instrument list notes), from which the draft datasheets take the notes.

Why: the zones are screening only. Equipment of EPL Gb stays valid if the competent person's
classification makes any part zone 1, and with five small motors on the two skids the cost is
small. Gas group IIC is set by H2 (the cathode gas is about 56 mol% H2). Temperature class T1
would cover H2 and CO by their autoignition temperatures; T3 for the motors and T4 for the
instruments are a cheap margin.

Rejected: 3G / Gc only (kept as the stated minimum, not the specification); moving the loads
out of the zone (the pumps and the compressor stand at their process).

Consequence: no P&ID or layout change. The acceptances of the compressor motors' tray drops into
the zones (`checks/checks.yaml`, `layout-tray-zone`) now give this decision as their reason, not
"Ex rating open". D-019, D-023, D-031 items 12 and 17 and D-045 point here. HAZOP H01-A903,
H01-A204, H02-A902 and H02-A206 are to be revised as proposals with the HAZOP revision of D-050.

Open (cannot be settled here): the area classification by a competent person (IEC 60079-10-1;
H01-A204, H02-A206); the operator's explosion protection document under 1999/92/EC (in the
Netherlands, the Arbobesluit); the initial and periodic inspection (IEC 60079-14, -17); the
stacks themselves, which have no Ex certificate: their terminals need the competent person's
assessment; the certificates of every item, and the design and drawing of the DC isolation with
the 48 V DC bus (D-031 item 9).

## D-052 Cell and meter temperatures; the stack outlet held at 25 °C (2026-11-06)
Decision (the owner, 2026-11-06):
- the cell temperature stays 25 °C and the meter's reference 0 °C and 101.325 kPa (both
  ASSUMED, D-005); the email to the dataset authors asks for the meter's make and reference
  conditions, and only their answer settles it;
- the -6.8 / -8.4 % of every FE at a 20 / 25 °C meter reference is carried as a stated
  capacity band (README; `uncertainty.json` "FE at the 20 degC meter basis": 32 cells, 4 x 8,
  28.82 kWh/kg). If the authors answer 20 or 25 °C, the stacks are re-sized to 4 x 8 cells by
  regen (8 x 5.37 V = 43 V, inside the 48 V bus), with the rectifier, the DC cables and T-101's
  volume (about +14 %, V proportional to N I) following, and a new frozen expectations commit;
- the pilot holds the stack outlet at 25 °C as its operating setpoint (TIC-x11, D-014's
  temperature condition). For the open skid (D-050) the cooler E-x11 is served by a tempered
  water unit (heating and cooling) off the skid, outside the zone, instead of cooling water
  only; with a low-temperature alarm and frost protection of the anolyte loop when idle (the
  on/off duty D-A-ONOFF stands 12 h a day, H01-A105). The P&ID, line list, loops and C&E change
  is made with the P&ID revision of the owner's other decisions;
- FIC-x02 is specified in mass units (kg/h, as `control/loops.yaml` has it); where it is a
  thermal mass flow controller, its gas and reference conditions go on its datasheet
  (`control/instrument-list.yaml` notes).

Why: the evidence for 0 °C is the authors' 22.4 L/mol and the usual convention of "sccm" on a
thermal mass flow meter (0 °C and 101.325 kPa, as in SEMI E12 and DIN 1343's normal
conditions); it is weak, but a re-size on a guess would move the cells, the rectifier, the DC
cables, the reservoir, the LCA and the frozen expectations at once. A warmer cell would leave
the measured series (D-014). A cooling-water-only cooler cannot hold 25 °C in a Dutch winter on
an open skid, nor keep an idle loop from freezing.

Rejected: switching the meter basis to 20 or 25 °C now; sizing for the worse case now; a
warmer cell.

Consequence: no change to the duty, the stacks, the records or the frozen expectations. TIC-x11
keeps its setpoint (295.27 K at the cooler outlet, D-012).

Open (cannot be settled here): the meter's actual reference conditions (the dataset authors);
the tempered-water unit's heating and cooling duty and its frost protection (vendor).

## D-053 The ASSUMED weights for basic engineering; vendor weights, weighing and the lifting plan (2026-11-06)
Decision (the owner, 2026-11-06): the ASSUMED weights of `layout/lifting-basis.yaml` (D-043)
are accepted for basic engineering. Before detail engineering, vendor weights are required for
the PSA X-x31, the oxidiser X-x32, the compressor K-x31, the rectifier U-x01 and the stacks
(entered under `vendor:` with their source; regen step 21 writes them into the equipment list).
Each skid is weighed at its factory acceptance test before its first lift. The lifting plan, by
an appointed person (ISO 12480-1), uses at least the doubled-weight bound.

The bound at the 5.47 m radius of the crane pads of D-047 (the bound of D-043, about 10 t at
7.2 m, was for the old pads). Capacity needed = weight x dynamic factor x (1 + rigging fraction)
/ chart utilisation, linear in the weight, so doubling the weight doubles it: Skid A drained
2 x 3.051 t, 2 x 4.698 = **9.40 t** of chart capacity at 5.47 m (38.6 t m); Skid B drained 2 x
2.903 t, 2 x 4.470 = **8.94 t** (36.7 t m); T-101 alone drained 2 x 0.351 = 0.70 t at 5.74 m
(`layout/lifting-study-units.md`, 1,000 h).

Why: a drained skid of about 2.9 to 3.1 t is well within a small mobile crane, so the
estimates are good enough to reserve the pads, lanes and laydown; the items that carry most of
the uncertainty are vendor packages.

Rejected: a contingency factor in `scripts/_lifting.py` (the doubled bound and the FAT weighing
cover it without a second set of numbers); waiting for the vendor weights before basic
engineering.

Consequence: text only; no weight, record or study changes.

Open (cannot be settled here): the crane, its load chart, the outrigger spread and the ground
bearing on the hardstanding; the base frame's lifting points and its weight (the fabricator,
D-043); the vendor weights themselves.

