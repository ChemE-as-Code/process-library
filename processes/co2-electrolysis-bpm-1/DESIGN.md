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
  film) and the Ni foam anode (0.35 kg/m2 ASSUMED), each with a disposal (membrane to
  incineration, a gap; Ag to a refiner and Ni to scrap recycling, burden-free under cut-off).
  The carbon paper of the GDE is not counted (open). regen writes their amounts from the stack
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
  the exchanges' compositions), the dosing solution, the bleed's and the final inventory's K and C,
  the condensate's K and Skid B's make-up water (its water less Skid A's); `cheme assess
  lca-cases` agrees within its six printed digits (rel 1e-5);
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
duty totals, and the Atlas mapping converts by the mass fraction (D-027). Core reports the element
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
  the Ag and the Ni foam (DESNZ's construction metals factor is steel-dominated: not used for
  nickel); construction is cut off (D-027). 11 gaps per skid, listed with their quantities;
- scenarios: `skid-b` (case skid-b); the Ember grids of the EU-27, DE, FR and the world for
  Skid A and, with `case: skid-b`, Skid B (core accepts `case` with `factors`); the DESNZ UK grid
  as a cross-basis check;
- sensitivities by `scripts/lca_sensitivity.py` into `lca/`: the membrane life (1,000, 4,000,
  20,000 h, ASSUMED levels; inventory only), the H2 co-product, the electricity mix, the duration;
- **ranking rule**: Skid A is ranked against Skid B only if every flow that distinguishes them
  has a documented factor (ADR 0029). They are KOH, the alkaline wastes and construction, and
  none has one: "ranking not determined" (`lca/ranking.json`), with the break-even KOH factor.

Results (1,000 h, per kg CO, kg CO2e characterised, the gaps excluded): Skid A 10.479 (electricity
8.766, vent CO2 1.712, water 0.0005), Skid B 10.482 (8.767, 1.712, 0.003). Electricity mixes A / B:
EU-27 8.99 / 8.99, DE 13.26 / 13.26, FR 3.14 / 3.14, world 17.61 / 17.62; DESNZ UK 8.08 (not
comparable). The Ember electricity pairs differ in no scope dimension; the verdicts read "proxy"
only through the UK water factor. Electricity is the largest characterised flow (84 %), the
vented CO2 the second (16 %): the spec expected the vent possibly largest; at 34.6 kWh/kg it is
not. Membrane life: 0.0028, 0.00069 and 0.00014 m2 of membrane per kg CO (0.0029, 0.00073 and
0.00015 g Ag; 0.97, 0.24 and 0.049 g Ni), impact not computable (gaps; core's scenarios cannot vary
a consumable's amount, gap C4). H2: the tail gas carries 0.116 kg H2 per kg CO; recovered, it would
take 10.4 % of the burden by mass or 58.0 % by LHV (CODATA: CO 282.98 kJ/mol, H2 241.826 kJ/mol);
substitution missing. Duration: Skid B's KOH 1.195 kg/kg at 1,000 h and 1.170 at 10,000 h, Skid
A's 0.649 at both; the totals do not change. Ranking: Skid B is higher in every characterised flow
(+0.0036 kg CO2e/kg: its dosing pump and make-up water) and uses 1.84 times the KOH and 1.57 times
the alkaline waste, so the break-even KOH factor is negative (-0.0066 kg CO2e/kg KOH): no KOH or
treatment factor reverses the order; only Skid A's larger reservoir (construction, not stated per
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
  not by case, so Skid B's dataset would carry Skid A's frames and its 1.46 m3 reservoir.
`publication.status` stays internal: `build_lci.py --public` leaves the process out.

Deviation from the spec: the file is named by core's dataset id (from the flowsheet title), not
`co2-electrolysis-bpm-1-skid-b.yaml`; the spec's fallback (a scratch copy with `case: skid-b`) is
not used, core does it.

Open (#331 stays open): multi-category impacts; the ecoinvent 3.11 run and the mapping check; the
A against B ranking (factors for KOH, CO2 supply, membrane, Ag, Ni, PP, caustic treatment);
construction impacts; the H2 co-product alternative; the biogenic CO2 or higher-recycle case; the
membrane-life impact; the GDE's carbon paper; the CPC code of the dataset.
