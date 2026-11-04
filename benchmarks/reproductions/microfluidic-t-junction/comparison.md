# Comparison: van Steijn 2010 T-junction model vs the published size-versus-flow-ratio data

- **Reference:** `source.yaml`. The original article (Lab Chip 2010, doi:10.1039/C002625E) is
  closed and was not read. The model equations come from an open restatement (Schackart and
  Kaarj, replication repository at commit `1b5c864`). The reference figure is the replot of the
  original Fig. 3 data in Nekouei and Vanapalli, arXiv:1703.00937v1, Fig. 5 (sha256 `e79589ae…`).
  Its marker and line coordinates were read from the PDF's vector paths.
- **Tolerances:** `tolerances.yaml`, frozen in commit `d3c48e12` (2026-11-04 14:52:06 +01:00)
  together with `source.yaml` and `inputs.yaml`.
- **Order:** the first run of `run.py` wrote `results/` at 14:54 the same day, after the freeze
  commit. Before the freeze, the digitised coordinates were printed and two squeezing
  coefficients were estimated by hand to check how the equations read (stated in the header of
  `tolerances.yaml`). No deviation between model and data was computed before the freeze. The
  repository cannot prove that no uncommitted run happened earlier, so this claim rests on the
  commit order.
- **Run:** `uv run benchmarks/reproductions/microfluidic-t-junction/run.py` from the repository
  root, on 2026-11-04, with Python 3.13.16, numpy 2.3.4, matplotlib 3.10.7, pyyaml 6.0.3,
  pypdf 5.1.0 and uv 0.13.0. Two runs gave byte-identical `results/`. The final run used an
  empty cache (`XDG_CACHE_HOME` set to a new directory), so the PDF was downloaded and verified
  again.

## Result: PARTIAL under the frozen rule (13 of 15 checks pass)

The model is reproduced: the implementation check, both independently evaluated squeezing
coefficients, and all six intercept and slope checks pass. The published agreement with the
experiments is reproduced for two of the three junction shapes. For the shallowest shape
(w_in/w = 0.67, h/w = 0.11) both of its checks fail. Under the pass rule, that makes the result
**partial**.

### Model checks

| Check | Reference | Ours | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| Closed-form filling volume vs geometric construction (1020 points) | – | – | max rel 7.1e-16 | rel 1e-12 | pass |
| Digitisation rerun from the pinned PDF vs `source.yaml` | 25 markers, 3 lines | identical | 0.000 | abs 0.002 | pass |
| alpha, w_in/w = 1, h/w = 0.33, eps = 0 (Nekouei p. 18) | 1.8 | 1.764 | -0.036 | abs 0.05 | pass |
| alpha, w_in/w = 1, h/w = 1, eps = 0 (Nekouei p. 18) | 1.15 | 1.149 | -0.001 | abs 0.005 | pass |
| Intercept v_fill, 0.33 / 0.33 | 1.036 | 1.066 | +0.030 | abs 0.15 | pass |
| Slope alpha, 0.33 / 0.33 | 0.555 | 0.531 | -4.3 % | rel 10 % | pass |
| Intercept v_fill, 0.67 / 0.11 | 1.229 | 1.141 | -0.088 | abs 0.15 | pass |
| Slope alpha, 0.67 / 0.11 | 1.593 | 1.700 | +6.7 % | rel 10 % | pass |
| Intercept v_fill, 1.33 / 0.17 | 1.338 | 1.288 | -0.050 | abs 0.15 | pass |
| Slope alpha, 1.33 / 0.17 | 3.079 | 3.202 | +4.0 % | rel 10 % | pass |

Here v = V/(h w²) and q = q_d/q_c. The geometry columns give w_in/w and h/w. The reference
lines are the dashed model lines of the replot. Their intercept is extrapolated to q = 0 from
the extracted end points.

The slope checks also confirm the corner roundness of the bubble series. With eps = 0, the
slopes would be 0.281, 1.380 and 2.761, which deviate by -49 %, -13 % and -10.3 %. All three
would fail. With eps = 0.1 w, the value recorded for the original's bubble series, all three
pass.

### Model vs experiment (the published comparison)

| Series (w_in/w, h/w) | Points | Mean abs. rel. deviation | Max abs. rel. deviation | Tolerance (mean / point) | Status |
| --- | --- | --- | --- | --- | --- |
| 0.33, 0.33 | 3 | 10.1 % | 13.5 % | 15 % / 30 % | pass / pass |
| 0.67, 0.11 | 8 | 24.7 % | 62.4 % | 15 % / 30 % | **fail / fail** |
| 1.33, 0.17 | 5 | 8.0 % | 16.7 % | 15 % / 30 % | pass / pass |

Point by point for the failing series (model minus experiment, relative to experiment):

| q | v (experiment, digitised) | v (model) | Deviation |
| --- | --- | --- | --- |
| 0.339 | 1.208 | 1.717 | +42 % |
| 0.569 | 1.298 | 2.108 | +62 % |
| 0.978 | 1.925 | 2.804 | +46 % |
| 1.387 | 3.804 | 3.499 | -8 % |
| 2.947 | 6.490 | 6.151 | -5 % |
| 4.098 | 7.117 | 8.108 | +14 % |
| 5.223 | 9.176 | 10.021 | +9 % |
| 7.269 | 12.129 | 13.499 | +11 % |

All point-by-point values are in `results/comparison.json` under
`reproduction.model_vs_experiment`. The engineering figure is `results/fig_reproduction.svg`. It
shows our model lines, the replot's dashed lines, the digitised experiments and the VOF points.

### Informational, not in the pass rule

Nekouei and Vanapalli's own VOF simulations (filled symbols in their Fig. 5) differ from the
model by a mean of 12.1 %, 5.3 % and 9.0 % for the three series. These are a third-party
numerical prediction, not measurements, so they are not counted as independent validation.

## Deviations and explanations

1. **Low-q points of the shallow junction (cause of the failure).** At q < 1 the three measured
   bubbles in the h/w = 0.11 junction are only 6 % to 69 % larger than the filling volume
   (v_fill = 1.14). The model adds 0.58 to 1.66 to v_fill there. Above q = 1.4 the same series
   agrees within 14 %. Its mean deviation over those five points is 9.5 %, computed after the
   run for diagnosis only; the verdict does not change. Two explanations are possible, and the
   open sources cannot separate them:
   - The physics differs at low q. In a very shallow junction, more continuous phase may bypass
     the forming bubble than the fixed 10 % the model assumes. That would shorten the squeezing
     stage. Korczyk et al. 2019 show that gutter leakage depends on the flow conditions.
   - The replot misrepresents the original. Two of the three low points have exactly the same
     vertical coordinate as the start points of the replot's dashed lines, which may point to an
     artefact of the replot. The original figure, which would settle this, is closed.
2. **Geometry reading.** The replot's legend and the replication script agree on (0.67, 0.11)
   and (1.33, 0.17), while the replot's body text swaps the two depths. We tested the swapped
   reading after the run, for diagnosis only. It does not rescue the 0.67 series (mean 20.7 %,
   max 55 %) and it makes the 1.33 series fail (mean 12.1 %, max 23 %, slope +10 % against the
   line). The legend reading is kept.
3. **Model lines.** Our intercepts differ from the replot's lines by -0.09 to +0.03, and our
   slopes by -4 % to +7 %. Nekouei and Vanapalli do not say how they evaluated the lines
   (rounding of h/w, eps, or reading values off the original's chart). These differences are
   within the frozen tolerances.
4. **Closed original.** The equations were not checked against the original text. They are
   consistent in three ways: the filling volume agrees with its geometric construction; R_pinch
   follows from the neck-width relation the restatement gives; and alpha follows from
   integrating the receding-interface equation. Two squeezing coefficients evaluated by a third
   party also agree to their reported digits. The restatement reports a misplaced bracket in
   the original's Fig. 2a for w_in > w. We use the bracketing that matches the geometry, and it
   enters only the 1.33 series.

## Gaps

- The original article (equations, Fig. 3 with all six series, experimental details such as
  fluids, Ca and channel dimensions) is closed and was not accessed. Only three of its six
  Fig. 3 series are available, through the replot. The liquid-droplet series (w_in/w = 1,
  h/w = 0.48) is not among them.
- The fidelity of the replot to the original is not stated and cannot be checked.
- Raw data of Korczyk et al. 2019 are available only on request (not obtained).
- Library CI does not check this folder (ADR 0030).

The tolerances were not changed after the run. A comparison with the original Fig. 3, if it
becomes accessible, should be run against the same `tolerances.yaml`.
