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
- Nested plant roots per skid (library ADR 0033 structure): every library tool would need to
  change, and the measured series would be referenced across folders.
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
added; the uncertainty of WDE is reported as a band instead (next stage, `--uncertainty`).

Reason: the simplest skid, with no chemicals handled during the run; the closed form makes
the duration dependence exact (ADR 0043).

Rejected: probing the duty at a trial volume and scaling in the library (the spec's fallback):
core computes the exact volume itself now.

Assumptions: the measured WDE and co-ion split hold over the whole campaign and across the
changing electrolyte (not supported by measurement, D-014).

## D-010 Skid B: continuous KOH dosing, bleed and make-up at a steady state (2026-11-04)
Decision: Skid B holds 50 L (ASSUMED: about 4.5 min hold-up at the 11.2 L/min recirculation,
for O2 disengagement) at the ASSUMED setpoints 0.5 mol/L OH- and 0.25 mol/L carbon by
continuous dosing of 5 M KOH (density 1.22 kg/L ASSUMED), a bleed to the site effluent and
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
- K-x31 compresses to 600 kPa(a); the PSA X-x31 delivers 0.90 of the CO formed at 0.99 mol/mol
  dry (H2 the rest) at 500 kPa(a), returns 0.95 of the unreacted CO2 to the cathode feed and
  sends the rest with the water to the oxidiser X-x32, which burns CO and H2 with twice the
  stoichiometric air (reactions COX, HOX): no CO or H2 is vented;
- the stack heat (cheme process stack) is removed by the cooler E-x11 to cooling water
  (isothermal model);
- the power: the stacks' AC power (DC over the rectifier efficiency 0.95, ASSUMED), and
  ESTIMATES until `cheme datasheets fill` gives the pump and compressor powers: the pumps at
  efficiency 0.3 (dosing 0.1, 300 kPa), the compressor adiabatic (kappa 1.3, efficiency 0.5),
  the PSA 0.5 kWh per kg CO delivered (TBD vendor);
- the temperatures and pressures of the streams are design conditions, ASSUMED.
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
--compare`, next stage); at fixed recovery equal CO formed is equal CO delivered.

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
scripts/regen.py's (next stage, step 14): core does not check the electrolyte state.

Reason: both skids run far beyond the measured 1 h and electrolyte.

Assumptions: none beyond the measured conditions.

## D-015 Skid envelope and feasibility (2026-11-04)
Decision: each skid is one 20 ft frame, 6.06 x 2.44 m in plan with 2.20 m usable height above
the deck (ASSUMED). A skid is feasible when every item fits that envelope in plan and height;
the height is checked by scripts/regen.py from the layout model (next stage), because core's
layout checks containment in plan only.

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
  flowsheet; the current is 80 A (4 x 20 A, cheme process stack);
- trips per skid: pH low-low at 12.2 (concentration basis) trips the rectifier (the end of the
  campaign on Skid A), level low-low trips the rectifier and stops the pump (Skid B on an
  independent LIA-202), CO or H2 detected trips the rectifier, closes the CO2, stops the
  compressor and starts the fan, the stack outlet temperature high-high and the recirculation
  flow low-low trip the rectifier; on Skid B the dose and the bleed are interlocked off with the
  current off (I-207, a permissive) and the day tank's low-low level stops the dosing pump;
- sequences per skid: fill, start-up, the response to a trip, the end-of-run drain;
- fail positions proposed: cooling water open, CO2 closed, cathode back-pressure open,
  condensate, make-up and bleed closed, product closed (open point).

Reason: the duty model holds the stacks at the measured operating point; the loops hold the
skid there, and the trips stop the current before the anolyte, the cooling or the flow leaves
it. The model doses and bleeds only with the current on (D-010).

Assumptions: every trip value and alarm margin (ASSUMED), the fail positions, SIL not screened.
The pH basis: the probe reads activity pH, the model concentration-basis pH (core ADR 0043):
the values need an offset or a calibration before use (control/philosophy.md).

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
  north (to the gas packages); north the PSA, the oxidiser, the rectifier and the fan. Skid B
  the same, with the day tank T-202 and the metering pump P-202 at the west end.
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
