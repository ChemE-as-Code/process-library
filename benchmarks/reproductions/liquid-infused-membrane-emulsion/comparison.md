# Comparison: liquid-infused membrane entry pressures vs Bazyar et al. (2019)

- **Reference:** `source.yaml` (Langmuir 35 (2019) 9513, doi:10.1021/acs.langmuir.9b01055,
  PMC6750837.1 and its SI; reported results and digitised Figure 4b points).
- **Tolerances:** `tolerances.yaml`, frozen in commit c9b0de3 (2026-11-04 14:54 +01:00) together
  with `source.yaml` and `inputs.yaml`, before the first run of `run.py`.
- **Run:** `uv run benchmarks/reproductions/liquid-infused-membrane-emulsion/run.py` from the
  repository root, 2026-11-04, uv 0.13.0, Python 3.13.16, numpy 2.3.4, matplotlib 3.10.7,
  pyyaml 6.0.3. Output in `results/` (`comparison.json`, `sweep.csv`, three SVG figures).
  Two consecutive runs gave byte-identical results.
- **Source check:** the run downloaded the article XML into the cache, found the pinned sha256
  and found all 16 anchor numbers and the four Table 3 rows in it (`source_check.status: ok`).
- **Order:** no comparison was computed by `run.py` before the freeze. While inspecting the data
  a few values were checked by hand; `tolerances.yaml` says which, and that the tolerances come
  from the measurement resolution and the stated uncertainties.
- **Order of changes after the first run:** after the first run, three changes went into
  `run.py` before this record. We state that none changed any value in the pass rule, but the
  first-run state of `run.py` and its `comparison.json` were not committed (commit a824792
  already holds the changed `run.py`), so git holds no evidence for that statement. (1) The Szyszkowski
  IFT is clipped at zero: this changes only the lower edge of uncertainty bands at 50 % cmc
  CTAB/hexadecane, where the corner of the fit-parameter box gave a negative IFT. (2) Flags were
  added (`tmp_inside_water_entry_band`, `robust_window_empty`). (3) The cache location in
  `comparison.json` is written relative to the cache root, not as an absolute local path. The
  figure labels were also moved. The final run was made from an empty cache; a run with the
  network blocked completed with the same verdict and `source_check` recorded as skipped.

- **Revision after review (2026-11-04):** two reviews led to a second set of changes,
  committed separately from the first results. `tolerances.yaml` is unchanged and the verdict
  is the same (28 of 28). `run.py` now clips the reported lower bound of the IFT bands at 0,
  adds informational columns (IFT deviation in % and in measurement standard deviations, the
  water entry pressures with the measured IFTs, a controller-accuracy flag on the Table 3 bands,
  the 1 mPa s viscosity-basis sensitivity, an operating-pressure flag and a grey region in the
  extension figure), stores the water/oil ratio to 4 decimals, and reads the TMP as two inputs
  (`tmp_flux_case`, `tmp_table3_upper_bound`, both 0.1 bar). In `inputs.yaml` and
  `source.yaml` only labels, notes and the licence record changed; no input value changed.

## Result: PASS under the frozen rule (28 of 28 checks)

The 28 checks are 8 IFTs, 11 digitised-point checks (12 Figure 4b series points, 10 distinct
values; the water point on the hexadecane-infused curve is checked once per fit radius),
5 entry pressures stated in the text, 1 permeability and 3 active-pore fractions.

**The 8 IFT checks are weak.** Their bands come from the corners of the a and b
half-confidence-interval box, without the a-b correlation (the source gives none), widened by
2 measurement standard deviations. They test consistency with the fit's box uncertainty, not
with the measurement: SDS 10 / hexadecane passes at -1.71 mN/m, 11 measurement standard
deviations off. The informative result is the point deviation: all 8 within 1.71 mN/m, 7 within
0.9 mN/m. The lower bound of the CTAB 50 / hexadecane band is shown clipped at 0 (from
-0.12 mN/m before this revision); this does not change the check. `comparison.json` gives each
IFT's deviation in % and in measurement standard deviations (informational).

| Check | Reference | Ours | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| IFT SDS 10 / hexadecane [mN/m] | 25.5 | 23.79 | -1.71 | in [19.34, 26.13] | pass |
| IFT SDS 50 / hexadecane | 12.8 | 12.80 | +0.00 | in [2.42, 19.01] | pass |
| IFT SDS 10 / K101 | 47.6 | 47.74 | +0.14 | in [45.09, 50.15] | pass |
| IFT SDS 50 / K101 | 31.8 | 31.43 | -0.37 | in [27.36, 34.99] | pass |
| IFT CTAB 10 / hexadecane | 12.2 | 11.99 | -0.21 | in [7.17, 15.29] | pass |
| IFT CTAB 50 / hexadecane | 3.3 | 3.75 | +0.45 | in [0.00, 7.82] | pass |
| IFT CTAB 10 / K101 | 47.7 | 46.81 | -0.90 | in [42.10, 50.36] | pass |
| IFT CTAB 50 / K101 | 29.8 | 29.76 | -0.04 | in [21.30, 36.06] | pass |
| LEP water / hexadecane-infused, SDS fit radius [bar], digitised | 0.342 | 0.345 | +0.003 | abs 0.037 | pass |
| LEP water / hexadecane-infused, CTAB fit radius, digitised | 0.342 | 0.351 | +0.009 | abs 0.037 | pass |
| LEP water / K101-infused, digitised | 0.599 | 0.601 | +0.002 | abs 0.037 | pass |
| LEP SDS 10 / hexadecane-infused, digitised | 0.282 | 0.287 | +0.005 | abs 0.037 | pass |
| LEP SDS 10 / K101-infused, digitised | 0.518 | 0.525 | +0.007 | abs 0.037 | pass |
| LEP SDS 50 / hexadecane-infused, digitised | 0.158 | 0.154 | -0.004 | abs 0.037 | pass |
| LEP SDS 50 / K101-infused, digitised | 0.351 | 0.345 | -0.006 | abs 0.037 | pass |
| LEP CTAB 10 / hexadecane-infused, digitised | 0.150 | 0.147 | -0.003 | abs 0.0205 | pass |
| LEP CTAB 10 / K101-infused, digitised | 0.518 | 0.514 | -0.004 | abs 0.037 | pass |
| LEP CTAB 50 / hexadecane-infused, digitised | 0.047 | 0.046 | -0.001 | abs 0.0205 | pass |
| LEP CTAB 50 / K101-infused, digitised | 0.330 | 0.327 | -0.003 | abs 0.037 | pass |
| LEP SDS 50 / hexadecane-infused (text) | 0.15 | 0.154 | +0.004 | abs 0.027 | pass |
| LEP CTAB 50 / hexadecane-infused (text) | 0.05 | 0.046 | -0.004 | abs 0.0105 | pass |
| LEP SDS 50 / K101-infused under hexadecane, gamma12 + gamma23 (text) | 0.26 | 0.259 | -0.001 | abs 0.010 | pass |
| LEP CTAB 50 / K101-infused under hexadecane, gamma12 + gamma23 (text) | 0.15 | 0.153 | +0.003 | abs 0.010 | pass |
| LEP hexadecane / K101-infused (text) | 0.08 | 0.096 | +0.016 | abs 0.027 | pass |
| Oil permeability, emulsion run SDS 10 / K101-infused [Darcy] | 1.74e-4 | 1.738e-4 | -0.13 % | rel 2 % | pass |
| Active pore fraction, LLD cycle 1 | 0.31 | 0.313 | +0.003 | abs 0.01 | pass |
| Active pore fraction, LLD cycle 2 | 0.47 | 0.467 | -0.003 | abs 0.01 | pass |
| Active pore fraction, LLD cycle 3 | 0.55 | 0.547 | -0.003 | abs 0.01 | pass |

What the pass shows: the source's equations, as we restated them from its text, give its
reported numbers back from its reported inputs. It is numerical agreement with the source's
own model and fits. It is not validation, and it is not independent: the entry-pressure curves
use radii the authors fitted to the same LEP points.

## Model against the paper's own observations (reported, not in the pass rule)

Threshold rule at TMP = 0.1 bar: water is predicted in the permeate when the TMP is at or above
the water entry pressure. The dry membrane is taken as hexadecane-filled, and the K101-infused
membrane as covered by a hexadecane layer (`inputs.yaml` configuration_rules). Observed water
fractions come from source Table 3.

| Emulsion | Membrane | Water entry [bar] (band) | Predicted water at 0.1 bar | Observed water fraction | Agrees |
| --- | --- | --- | --- | --- | --- |
| SDS 10 | dry | 0.287 (0.224-0.330) | no | 0 | yes |
| SDS 50 | dry | 0.154 (0.031-0.239) | no | 0.2 | no (0.1 bar inside band) |
| CTAB 10 | dry | 0.147 (0.086-0.194) | no | 0 | yes |
| CTAB 50 | dry | 0.046 (0-0.099) | yes | 0.5 | yes |
| SDS 10 | K101-infused | 0.392 (0.323-0.441) | no | 0 | yes |
| SDS 50 | K101-infused | 0.259 (0.130-0.350) | no | 0.05 | **no** |
| CTAB 10 | K101-infused | 0.254 (0.189-0.306) | no | 0 | yes |
| CTAB 50 | K101-infused | 0.153 (0.102-0.210) | no | 0.25 | **no** (0.1 bar within one controller accuracy of the band) |

- 5 of 8 cases are classified correctly. Both 10 % cmc emulsions give no water on both
  membranes, as observed.
- The model does not explain the water through the K101-infused membrane with SDS 50: the
  low edge of the band, 0.130 bar, is 30 mbar above the TMP. For CTAB 50 the case is weaker.
  The low edge, 0.1024 bar, is only 2.4 mbar above 0.1 bar, which is less than the 5.5 mbar
  controller accuracy (`tmp_within_one_controller_accuracy_of_band` in `comparison.json`). That
  edge is also degenerate: at that corner of the fit box the water/hexadecane IFT comes out
  negative and is clipped to zero, so the edge is just 2 gamma23 / (r + hci). The authors give
  the same argument only as a reason for *less* water. A lower actual TMP (the source says at
  most 0.1 bar) would widen the gap.
- Ranking holds: for the four 50 % cmc cases, rising water entry pressure matches falling
  observed water fraction exactly (CTAB 50 dry 0.046 bar / 0.5; CTAB 50 K101 0.153 / 0.25;
  SDS 50 dry 0.154 / 0.2; SDS 50 K101 0.259 / 0.05). The entry pressure orders the leakage,
  but a sharp threshold does not predict whether water leaks.
- Plausible causes, not tested here: pores that have lost K101 (LLD suggests only about 45 %
  of the infusion liquid is retained after pure hexadecane flow, active pore fraction 0.55
  after cycle 3, and the source reports hexadecane-filled patches in the used K101-infused
  membrane); pores larger than the fitted curvature radius (largest pore radius
  1.92 um against 1.63 to 1.82 um fitted); pressure spikes when the feed chamber is refreshed;
  water carried with coalescing oil.
- The bands come from the corners of the reported a, b and r half-confidence intervals. The
  source gives no covariance, so the bands are wider than the true fit uncertainty. For SDS
  with hexadecane, the half-interval of a is 40 % of a.

## Deviations and explanations

1. **IFT SDS 10 / hexadecane, -1.71 mN/m (-6.7 %).** This is the largest IFT deviation. It is
   inside the band only because the fit's a has a wide interval. It comes from the fit (eq 2
   with Table 2 values): we use the published parameters, not the data. The other seven IFTs lie
   within 0.9 mN/m. Sensitivity (informational): with the measured 25.5 mN/m instead of the
   fit, the SDS 10 water entry pressures rise by 0.021 bar, from 0.287 to 0.307 bar (dry) and
   from 0.392 to 0.412 bar (K101-infused). With the measured IFTs the other six cases move by
   at most 0.006 bar (`water_entry_with_measured_table_s2_ift`).
2. **Hexadecane entry into the K101-infused membrane, model 0.096 bar against 0.08 bar
   measured (+0.016 bar).** This passes within one 22 mbar pressure step. Note that 0.08 bar
   with gamma23 = 8.7 mN/m implies a curvature radius of 2.18 um. That is larger than the
   largest pore radius from porometry (1.92 um). The fitted 1.82 um radius therefore puts the
   oil entry slightly too high. In the window this makes the lower bound conservative by about
   0.016 bar.
3. **Combined-interface radius.** The 0.26 and 0.15 bar values are reproduced with the
   hexadecane-infused fit radii (1.66 and 1.63 um), as the source's wording implies (`inputs.yaml`).
   With the K101 fit radius (1.82 um) they would be 0.236 and 0.137 bar (`comparison.json`,
   informational). The physical choice is open; the window uses the text-backed reading.
4. **Water point on the hexadecane-infused curve.** One digitised value (0.342 bar) serves
   both series because the markers overlap. The two fit radii give 0.345 and 0.351 bar.
5. **Digitised overlap at 10 % cmc on K101.** Both markers were read as one value, 0.518 bar.
   The model gives 0.525 (SDS) and 0.514 bar (CTAB).
6. **CTAB cmc.** Solutions were made with Table 1's 0.92 mol/m3. The SI's 0.74 mol/m3 (from the
   hexadecane IFT series) is not used. With 0.74 mol/m3, CTAB 50 would be 0.37 mol/m3.
7. **Densities.** The SI lists surfactant-solution densities of 0.867 to 0.997 g/cm3. Values
   below water's are implausible for solutions with less than 0.15 wt% surfactant, so they are
   not used; water density is used instead (`inputs.yaml`). They enter only the creaming estimate
   and the oil volume fraction.

## Other computed quantities (no reported counterpart)

- Dry-membrane porosity implied by kappa = phi r^2 / 24 with r = 1.78 um: 0.213, if the SI
  Table S3 permeabilities are on a hexadecane (3.2 mPa s) basis. SI p. S7 states that 1 mPa s
  was used; if so, the porosity is 0.68 (`inputs.yaml` lld.viscosity_basis_stated). The active
  fractions are ratios and are unaffected.
- Stokes creaming, SDS 10 (0.06 to 19.85 um/s, delta rho 270 kg/m3, 1 mPa s): implied droplet
  diameters of 0.64 and 11.6 um. The lower value matches the start of the measured distribution
  in source Figure 5 (about 0.5 um). The upper value lies in the sparse tail; it is not checked.
- Water entry with the aqueous phase directly on K101 (the LEP experiment): 0.525 (SDS 10),
  0.345 (SDS 50), 0.514 (CTAB 10) and 0.327 bar (CTAB 50).

## Gaps

- No raw data. Figure 4b was digitised from a 400 x 174 px image (uncertainty 0.015 bar).
- The TMP of each run is not given beyond "at most 0.1 bar".
- One flux record only (SDS 10, K101-infused). No flux-pressure curve exists in the source.
