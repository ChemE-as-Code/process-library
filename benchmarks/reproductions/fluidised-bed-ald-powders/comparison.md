# Comparison: Grillo et al. (2015) fluidised-bed ALD model vs our re-implementation

- **Reference:** `source.yaml`: thesis chapter 7 (open version of CEJ 268 (2015) 384-398),
  sha256 `1b41aef7…b802`; Table 7.4, Eq. 7.25, Fig. 7.3, Fig. 7.4 and the text of p. 199.
- **Tolerances:** `tolerances.yaml`, frozen in commit 38aa2e3f (with `source.yaml`,
  `inputs.yaml` and `digitise.py`) before the first run of `run.py`. Its header records the
  hand estimates made while inspecting the source before the freeze.
- **Run:** `uv run benchmarks/reproductions/fluidised-bed-ald-powders/run.py`, 2026-11-04,
  Python 3.13.16, numpy 2.3.4, scipy 1.16.3, matplotlib 3.10.7, pyyaml 6.0.3; about 10 s.
  Two runs give byte-identical `results/`.
- **Order:** the first run of `run.py` came after the freeze commit. It reported "invalid
  run": our dynamic model's mass balance closed only to -3.1e-3 (frozen limit 1e-3). The cause
  was a bug of ours: the bubble-to-emulsion exchange integral used trapezoid weights while the
  bubble cells lost mass by a cell sum. Fixed (cell sum in both); closure is now 1.6e-12. The
  38 comparisons were the same in that run (the bug moved the profile values by < 1e-5), and
  the tolerances were not touched.
- **Commit history versus this order.** Commits d09d4dde (digitise.py made deterministic),
  89be1291 (model, run and results) and afa3dfdb (write-up) were assembled together after the
  runs and carry the same timestamp. The digitise fix happened after the first run, although
  d09d4dde comes first in the history. The pre-fix run.py and its invalid-run output were not
  committed, so the invalid run is documented only here. What the history does show is that
  the freeze commit 38aa2e3f (14:57:31) comes before all three, and that `source.yaml`,
  `inputs.yaml` and `tolerances.yaml` are unchanged since then.
- **Files written after the run** (review response, 2026-11-04): `tolerances-strict-budget.yaml`
  (a stricter budget, a sensitivity view only, see below) and `addendum.yaml` (corrections to
  `source.yaml` and `inputs.yaml`, and the validity limits used to flag the extension). Neither
  changes the verdict of record.

## Result: PARTIAL under the frozen rule (29 of 38 comparisons pass; G1 and G3 all pass)

| Group | What | Pass |
| --- | --- | --- |
| G1 | minimum saturation time, Eq. 7.25 | 2/2 |
| G2 | transport time scales and Thiele moduli, Table 7.4 | 11/11 |
| G3 | required bed height, values stated in the text | 2/2 |
| G4 | required bed height, digitised Fig. 7.4 | 13/20 |
| G5 | dynamic model: quasi-steady bubble profile, digitised Fig. 7.3 | 1/3 |

29/38 = 76 % is above the 75 % threshold and all G1 and G3 checks pass, so the verdict is
PARTIAL. Internal checks (not comparisons): dynamic utilisation at 19.9 s vs Eq. 7.51,
0.99929 vs 0.99996 (abs 6.7e-4, limit 1e-3, pass); dynamic mass balance 1.6e-12 (pass).

### How firm the PARTIAL verdict is

- **One pass from FAIL.** The rule needs ceil(0.75 x 38) = 29 passes; the run has 29. One
  fewer gives 28/38 = 73.7 %, which is FAIL.
- **Five passes lie within 1.4 percentage points of their 10 % limit** (`comparison.json`
  `verdict_margin`):

  | Check | Deviation | Limit |
  | --- | --- | --- |
  | H*, d_b 4.5 cm, 1 mbar (text, G3, required for PARTIAL) | +9.4 % | 10 % |
  | H* Fig. 7.4a, u_mf 0.01 cm/s, d_b 4 cm | -9.6 % | 10 % |
  | H* Fig. 7.4b, d_b 2 cm | -9.3 % | 10 % |
  | H* Fig. 7.4a, u_mf 2.5 cm/s, d_b 2 cm | -9.2 % | 10 % |
  | H* Fig. 7.4a, u_mf 5 cm/s, d_b 1 cm | -8.6 % | 10 % |

- **The required 1 mbar text check passes on an unquantified allowance.** Its frozen reason is
  "6.5 cm, 2 s.f.; diffusion-dominated K_be". Rounding to 2 s.f. accounts for 0.8 %. The
  rounding of the reconstructed D (tau_ga to 3 s.f., +-0.054 %) moves our H* by 0.03 %
  (7.110-7.114 cm). The rest of the 10 % is the "K_be evaluation" allowance, which the
  tolerance file does not quantify. For scale: if eps_mf, which the source does not state for
  Fig. 7.4, were 0.45 or 0.55 instead of 0.5, our H* would be 7.48 or 6.79 cm (+5.2 % or
  -4.5 %). Matching 6.5 cm would need eps_mf = 0.60 or a diffusivity 20.5 % higher. The
  tolerance was set after a hand estimate of about 7.1 cm (+9.2 %, disclosed in the
  tolerance header); the allowance it rests on is not traceable to a stated uncertainty.
- **The G4 tolerance is wider than its stated budget away from the smallest value.** The
  digitisation uncertainty is +-0.9 cm, 8.6 % of the smallest value (10.4 cm) but 0.4-3 % at
  the other points; 10 % is applied to every point.
- **Not all 38 comparisons are independent.** The two G1 checks are the same formula with the
  inlet scaled by 1000 (identical deviation, +2.56 %). tau_ga at 1 mbar follows from the
  reconstructed D scaled as 1/P, so it tests the source's arithmetic. The two Thiele moduli
  equal sqrt(tau_c/tau_rxn) and sqrt(tau_sa/tau_rxn) with the reported tau_rxn, so they are
  not independent of tau_c and tau_sa. Without these four, 25 of 34 independent comparisons
  pass (73.5 %), below 75 %. The frozen rule counts all 38; this count is information only.
- **Stricter budget (sensitivity view, not the verdict of record).**
  `tolerances-strict-budget.yaml`, written after the run, keeps only the stated rounding,
  the digitisation uncertainty and the rounding of stated inputs, with no allowance for
  K_be evaluation. Under it the result is **FAIL, 17 of 38** (G1 2/2, G2 10/11, G3 1/2,
  G4 4/20, G5 0/3): the 1 mbar text anchor and tau_ga at 1 mbar fail. The tolerance of record
  remains `tolerances.yaml`, and its verdict remains PARTIAL. A reader should weigh the
  PARTIAL label with the points above.

### G1-G3

| Check | Reference | Ours | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| tau_sat_min, P_TMA = 100 mbar | 18 s | 18.46 s | +2.6 % | rel 5 % | pass |
| tau_sat_min, P_TMA = 0.1 mbar | 5 h | 5.13 h | +2.6 % | rel 10 % | pass |
| tau_em, 1.013 bar | 0.91 s | 0.914 s | +0.5 % | rel 5 % | pass |
| tau_b, 1.013 bar | 0.42 s | 0.420 s | +0.1 % | rel 5 % | pass |
| tau_int, 1.013 bar | 5e-2 s | 4.63e-2 s | -7.3 % | rel 20 % | pass |
| tau_int, 1 mbar | 2.6e-3 s | 2.64e-3 s | +1.6 % | rel 10 % | pass |
| tau_ga, 1 mbar | 9.25e-7 s | 9.22e-7 s | -0.3 % | rel 5 % | pass |
| tau_c, 1.013 bar | 1.6e-3 s | 1.58e-3 s | -1.5 % | rel 10 % | pass |
| tau_c, 1 mbar | 1.15e-5 s | 1.146e-5 s | -0.4 % | rel 10 % | pass |
| tau_sa, 1.013 bar | 2.43e-5 s | 2.424e-5 s | -0.2 % | rel 10 % | pass |
| tau_sa, 1 mbar | 1.39e-5 s | 1.389e-5 s | -0.1 % | rel 10 % | pass |
| Thiele phi*, 1.013 bar | 8 | 7.94 | -0.8 % | rel 20 % | pass |
| Thiele phi*, 1 mbar | 1.56 | 1.561 | +0.1 % | rel 10 % | pass |
| H*, d_b 4.5 cm, u_mf 5 cm/s, 1.013 bar | about 100 cm | 103.3 cm | +3.3 % | rel 10 % | pass |
| H*, d_b 4.5 cm, 1 mbar | 6.5 cm | 7.11 cm | +9.4 % | rel 10 % | pass |

### G4: required bed height H* for eta* = 0.9999 (Fig. 7.4, digitised), cm

| u_mf | d_b = 1 cm | 2 cm | 3 cm | 4 cm |
| --- | --- | --- | --- | --- |
| 0.01 cm/s | 24.9 / 16.3 (-34.7 %) fail | 71.4 / 54.7 (-23.4 %) fail | 131.9 / 111.2 (-15.7 %) fail | 203.5 / 183.9 (-9.6 %) pass |
| 0.1 cm/s | 19.2 / 16.0 (-16.3 %) fail | 54.7 / 53.7 (-1.7 %) pass | 100.6 / 108.9 (+8.3 %) pass | 155.0 / 179.9 (+16.1 %) fail |
| 2.5 cm/s | 14.4 / 11.8 (-18.1 %) fail | 40.7 / 37.0 (-9.2 %) pass | 74.6 / 72.0 (-3.5 %) pass | 114.7 / 115.5 (+0.7 %) pass |
| 5 cm/s | 10.4 / 9.52 (-8.6 %) pass | 29.1 / 28.6 (-1.7 %) pass | 53.0 / 54.3 (+2.6 %) pass | 81.1 / 85.7 (+5.7 %) pass |
| 1 mbar (envelope) | 0.680 / 0.523 (-23.1 %) fail | 1.92 / 1.74 (-9.3 %) pass | 3.51 / 3.52 (+0.1 %) pass | 5.40 / 5.80 (+7.4 %) pass |

Each cell: reference / ours (deviation). Tolerance rel 10 % throughout. Figure:
`results/fig1-required-bed-height.svg`.

### G5: dynamic model, bubble-phase TMA at t = 19.9 s (Fig. 7.3, digitised)

| z/H | Reference | Ours | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| 0.1 | 0.462 | 0.408 | -0.054 | abs 0.03 | fail |
| 0.2 | 0.214 | 0.167 | -0.047 | abs 0.03 | fail |
| 0.4 | 0.046 | 0.028 | -0.017 | abs 0.03 | pass |

Figure: `results/fig2-bubble-profile.svg`. Our dynamic profile and the quasi-steady
exponential nearly coincide (the emulsion concentration is 7e-4 of the inlet).

The counted values are from the N_z = 400 grid, which is biased high by the first-order upwind
error (see Grid and solver). Corrected values, for information (`comparison.json`
`supplementary.G5_corrected_for_upwind_error`): Richardson extrapolation of N_z = 400 and 200
gives 0.404, 0.164 and 0.027 at z/H = 0.1, 0.2 and 0.4, in agreement with the analytic
quasi-steady profile C_em + (1 - C_em) exp(-9.07 z/H) (0.404, 0.164, 0.027). Deviations
-0.058, -0.050 and -0.018: the same statuses (1/3 within abs 0.03), with slightly larger
misses.

## Deviations and explanations

1. **Bubble-emulsion exchange (main cause of the G4 and G5 failures).** Since Eq. 7.52 gives
   H* = (u_b/K_be) ln[u_b delta/(u0 (1 - eta*))] and the log term does not depend on K_be, H* is
   exactly proportional to u_b/K_be. At d_b = 1-2 cm the source's exchange is weaker than
   Table 7.1 (p. 178) gives when we evaluate it; at d_b = 3-4 cm and low u_mf it is stronger.
   The G4 differences depend on d_b and change sign, from -35 % to +16 %; a single factor on
   K_be cannot explain them. The digitised Fig. 7.3 profile decays as
   exp(-7.71 z/H); ours decays as exp(-9.07 z/H) (H K_be/u_b with K_be = 21.6 1/s,
   u_b = 0.243 m/s, H = 0.102 m), so the source's K_be/u_b is about 15 % lower. In Fig. 7.4a
   the source's curves grow more slowly with bubble size than ours: between 1 and 4 cm, H*
   rises 8.2-fold (u_mf = 0.01 cm/s) and 7.8-fold (5 cm/s) in the source, against 11.3-fold
   and 9.0-fold in ours, so the curves cross near d_b = 2-3 cm. The difference is largest
   where diffusion dominates the exchange (low u_mf, 1 mbar). Using the Table 7.1
   correlations and the Fig. 7.4 caption as printed, we cannot identify the source's choice
   (how u_b or the diffusive term depend on d_b). Possible causes are a different u_b in the
   exchange term, a different effective bubble size in K_be, or a different diffusivity in the
   simulations behind the figures. None of them is stated, so we did not test them against the
   reference.
2. **tau_em interpretation.** Eq. 7.19 as printed gives 1.83 s; Table 7.4's 0.91 s is the
   interstitial-gas residence time with the factor eps_mf. We used the latter (decided while
   inspecting the source, recorded in `inputs.yaml` before the freeze).
3. **Diffusivity reconstructed, not computed.** D_TMA-N2 = 2.409e-5 m2/s at 500 K, 1.013 bar
   comes from the reported tau_ga, so tau_ga at 1.013 bar is not a check. Our Wilke-Lee
   estimate with the stated collision diameter gives 2.398e-5 m2/s (-0.5 %), so the
   reconstruction agrees with the method the source names. All agglomerate-scale time scales
   (tau_c, tau_sa, both pressures) then agree within 1.5 %. This supports the source's
   diffusivity formulas (Eqs. 7.12-7.15, tortuosity 1/eps) as we read them.
4. **1 mbar text anchor at +9.4 %.** It passes, but only just. The digitised Fig. 7.4b gives
   6.37-6.50 cm at 4.5 cm, so the text value and the figure agree with each other, and ours is
   higher. This is the same exchange difference as in item 1, here at large d_b.
5. **Lumped kinetics and the emulsion slip.** The Travis rate expressions are not in the
   chapter. Our first-order site-balance kinetics are fitted to the reported tau_rxn only.
   They leave an emulsion concentration of about 7e-4 of the inlet in the quasi-steady
   period, where Eqs. 7.51 and 7.52 assume zero. At mid-pulse our outlet slip is 7.4e-4
   against 4.2e-5 from Eq. 7.51 (18 times larger); 60 % of it leaves with the emulsion gas,
   and the bubble outlet is 8.2e-4 rather than exp(-9.07) = 1.2e-4 (`dynamic_base.mid_pulse`).
   The internal check `dynamic_vs_qss_eta` compares eta in absolute terms (limit 1e-3) while
   1 - eta_qss is 4e-5, so it passes despite this 18-fold difference in slip: it checks only
   that the two utilisations agree to 0.1 %. A future case should compare 1 - eta in relative
   or log terms, or compare C_b(H) - C_em with the profile. The bubble profile (G5) is
   affected by C_em only at the 1e-3 level.
6. **Source densities not mutually consistent.** rho_b = 130 kg/m3 with eps_mf = 0.5 implies an
   agglomerate density of about 170 kg/m3 in the expanded bed, while Eq. 7.2 gives 47 kg/m3.
   We keep the batch surface fixed (`inputs.yaml` q_sites). This affects only the dynamic
   model's site density per agglomerate volume, not G1-G4.

## Not evaluable (gaps, not passes)

- Saturation time 46.4 s of the full dynamic model (Fig. 7.3): the TMA inlet concentration
  is not stated. We reconstructed P_TMA,in = 40 mbar from that time, so our 45.7 s (99 % mean
  coverage) is not a check.
- Cumulative CH4 of about 1.5 per TMA (Fig. 7.1a, p. 194): this needs the Travis rate
  expressions nu_1 to nu_3 and their parameters, which the chapter does not give (Table 7.3,
  p. 187, gives the coverage balances and generation terms).
- tau_rxn (Table 7.4): kinetic, used as an input.
- The nano-porous gamma-alumina case (Fig. 7.5, 7.6; Eq. 7.45): K_gp, eps_0 and d_b for
  Fig. 7.6 are not stated; not attempted.

## Digitisation check (after the run)

Rerunning `digitise.py` from a clean cache showed that its first version was not
deterministic. Two tick labels "0" of Fig. 7.4a matched one search window, and one was picked
in set order. The script now asserts a single match. The `source.yaml` values were read with
the x-axis label, which lies at the curves' common origin; the fixed script reproduces them
exactly. They were read with label centres rounded to whole points (within the stated
+-0.5 pt). Without rounding (`digitise.py --unrounded`) the Fig. 7.4 reference values change by
at most 0.9 %, Fig. 7.3 is unchanged, and no check changes status (G4 stays 13/20).
`source.yaml` was not edited.

## Grid and solver

N_z = 400, N_r = 40 against N_z = 200, N_r = 20: t99 45.747 s vs 45.747 s; C_b/C_in at
z/H = 0.1, 0.408 vs 0.412. The first-order upwind bubble grid reduces the exchange exponent:
per cell it applies a factor 1/(1 + a) with a = 9.07/400 = 0.0227, and ln(1 + a)/a = 0.989, so
the exponent is about 1.1-1.2 % too small at N_z = 400 (an earlier version of this file said
"under 1 %"). The counted G5 values are therefore biased high by about 0.004 at z/H = 0.1; the
corrected values are given under G5. No status changes.

## Corrections after review

Recorded in `addendum.yaml`, since `source.yaml` and `inputs.yaml` are frozen with the
tolerances:

- Titles as published: the article is "Modeling the precursor utilization in atomic layer
  deposition on nanostructured materials in fluidized bed reactors"; the thesis is
  "Aggregation Phenomena in Atomic Layer Deposition: Bridging Macro and Nano".
- Reuse terms: the repository cover page permits download and distribution only for strictly
  personal use without consent, and the journal copyright (Elsevier) may apply to chapter 7.
  digitise.py downloads for the user's own research use and redistributes nothing.
- Literature index: the four "AlOx on titania" papers were found by a title search (the index
  has no substrate field). It missed Valdesueiro et al. 2015 (TMA/H2O on TiO2 at 1 atm) and
  King et al. 2007 (in situ mass spectrometry of outlet TMA; ch. 7 ref. [6]). Neither was
  examined; both are candidate validation sources. A newer index version (v4, 2025-12-17)
  exists and was not consulted.
- Locators: chapter 7 reuses table and figure numbers. "Table 7.1" here is p. 178 (not the
  gamma-alumina table on p. 199); "Fig. 7.1" for CH4 is p. 194.
- Input labels: a fourth label "reported" is used; R and N_A are reference constants, M_TMA is
  reconstructed, and S_BET, rho_b and n_max are reported model parameters, not measured.

Tolerances were not changed after the run.
