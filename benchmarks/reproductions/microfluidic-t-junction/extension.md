# Design extension: T-junction dimensions for a target droplet volume

> **HYPOTHETICAL design extension. Not validated.** These designs come from inverting the van
> Steijn 2010 model, which is only partially reproduced here (see `comparison.md`). They use the
> model's liquid-droplet branch (corner roundness 0.01 w), which is **not reproduced here**: the
> original validated it at one geometry only, and that series is not in the open replot. The
> fluid pair, its viscosity ratio and the fabrication grid lie partly outside the original's
> experimental range (listed below). No junction was built or tested. Use the numbers to choose
> a starting geometry, not as a specification.

All values below are from `results/comparison.json` (`design_extension`). The inputs and their
labels are in `inputs.yaml` under `design_extension` (revision r1, see its header).

## Question and method

The question: which channel width w, depth h and inlet width ratio w_in/w, together with which
flow-rate ratio q = q_d/q_c and capillary number Ca, give a target droplet volume V while
staying in the regime where the model holds?

The model is linear in q: V/(h w²) = v_fill(w_in/w, h/w) + alpha(w_in/w, h/w, eps) q. For a given
geometry the inversion is therefore exact: q = (V/(h w²) - v_fill)/alpha. `run.py` evaluates
this on an assumed fabrication grid:

- h = 25, 50, 75 or 100 µm;
- w = 50 to 500 µm in 5 µm steps;
- seven inlet ratios from 0.33 to 3.

The squeezing regime is bounded in Ca on both sides, and both bounds depend on q:

- below by gutter leakage: q Ca ≥ 10 beta = 7.4e-4 (Korczyk et al. 2019, Fig. 3);
- above by the transition to jetting: S = Ca (1 + q)² ≤ S_crit = 0.017 (Korczyk et al. 2019,
  pages 6-7 and Fig. 5b).

Both bounds were measured in square channels and are used here as indications. The original's
experiments were at Ca < 0.01 (Nekouei and Vanapalli, Table 1). That is the range they covered,
not a regime boundary, and for q above 0.3 the S-number bound is the tighter one.

The operating Ca is set per design: a factor 2 below the upper bound, Ca_op = S_crit/(2 (1 + q)²).
A design is **feasible** if, at that Ca, it lies inside every blocking bound:

- h/w from 0.11 to 0.48;
- w_in/w from 0.33 to 3;
- q from 0.1 to 10;
- Ca at most 0.01, S at most 0.017, and q Ca at least 7.4e-4.

A feasible design is **nominal** if, in addition:

- q is between 0.5 and 5, and Ca_op is at least a factor 2 above the leaking bound. Together
  these give a design window of q = 0.50 to 3.45;
- it is robust to corner roundness. The roundness of a fabricated junction is not known in
  advance. At the design q, the volume predicted with eps = 0 and with eps = 0.1 w (the two other
  values the original used) must lie within 15 % of the target.

Among the nominal designs, the chosen one gives the highest droplet frequency. The fluid pair is
FC-40 droplets in hexadecane (mu_c = 3.6 mPa s, mu_d = 4.1 mPa s, gamma = 7.3 mN/m, measured by
Korczyk et al. 2019), and the design corner roundness is eps = 0.01 w.

Every feasible design was put back through the forward model. The largest relative deviation
from the target was 2.2e-16, against a tolerance of 1e-9.

## Results for two target volumes

| | D1 | D2 |
| --- | --- | --- |
| Target volume V | 0.50 nL | 2.0 nL |
| Depth h | 25 µm | 50 µm |
| Main channel width w | 115 µm | 170 µm |
| Inlet width w_in (w_in/w) | 38 µm (0.33) | 57 µm (0.33) |
| Aspect ratio h/w | 0.217 | 0.294 |
| v_fill, alpha | 1.105, 0.469 | 1.079, 0.359 |
| Flow-rate ratio q_d/q_c | 0.869 | 0.851 |
| Squeezing-regime Ca window at this q | 8.5e-4 to 4.9e-3 | 8.7e-4 to 5.0e-3 |
| Operating Ca, S | 2.4e-3, 0.0085 | 2.5e-3, 0.0085 |
| q_c, q_d | 0.852, 0.740 µL/min | 2.57, 2.18 µL/min |
| Droplet frequency | 25 s⁻¹ | 18 s⁻¹ |
| Droplet length V/(h w) | 174 µm (1.5 w) | 235 µm (1.4 w) |
| Forward check, predicted V | 0.5000 nL (rel. dev. 2e-16) | 2.000 nL (rel. dev. 0) |
| Corner roundness 0 to 0.1 w: q needed for V | 0.58 to 0.92 | 0.52 to 0.91 |
| Corner roundness 0 to 0.1 w: V made at the design q | 0.49 to 0.57 nL (spread 13 %) | 1.97 to 2.28 nL (spread 14 %) |
| Volume range in the design window (q 0.50 to 3.45) | 0.44 to 0.90 nL | 1.82 to 3.35 nL |
| Volume range over q 0.1 to 10, inside the regime | 0.38 to 1.92 nL | 1.61 to 6.74 nL |
| Regime flags (blocking) | none | none |
| Evidence notes (h/w outside 0.17 to 0.33) | none | none |

The last volume range needs Ca between 7.4e-3 and 0.01 at q = 0.1, and between 7.4e-5 and
1.4e-4 at q = 10. At both ends the regime window is a factor 2 wide or less, so the design
window is the range to plan with.

Number of designs found:

- **V1 (0.50 nL):** 79 feasible and 32 nominal designs, all at h = 25 µm, with w from 55 to
  125 µm. A 50 µm-deep junction cannot make 0.5 nL inside the validated range: the narrowest
  width it allows (h/w at most 0.48) is 105 µm, and its filling volume alone is already larger
  than 0.5 nL. 13 designs inside the q and Ca windows were rejected as too sensitive to corner
  roundness. The best of them (w = 110 µm, w_in/w = 0.33, q = 1.21, 23 s⁻¹) would make 0.49 to
  0.58 nL over the roundness band.
- **V2 (2.0 nL):** 273 feasible and 113 nominal designs, at h = 25, 50 or 75 µm with w from 55
  to 225 µm. The best 25 µm-deep option (w = 220 µm, q = 0.80) gives 12 s⁻¹, against 18 s⁻¹ at
  50 µm. 38 designs were rejected for corner-roundness sensitivity.

`results/fig_design_map.svg` shows the required q against w for every inlet ratio at the chosen
depths, with the validated q band and the design window. Dashed curve sections are rejected for
corner-roundness sensitivity. `results/drawing_D1.svg` and `results/drawing_D2.svg` are
dimensioned plan views, drawn to scale from these values. Each shows w, w_in, the predicted
droplet, the flow rates, a section A-A with the depth, and the corner-roundness volume band.

**Why both designs sit near q = 1.** At fixed geometry the frequency is q_d/V, which rises with
q Ca. The S-number bound caps Ca at S_crit/(1 + q)², so the highest frequency allowed by the
bound scales as q/(1 + q)², which peaks at q = 1. The narrow inlet (w_in/w = 0.33) has the
smallest squeezing coefficient, so it reaches the target at q near 1 in the narrowest channel
that is still robust to corner roundness. At larger q the narrow inlet is the most sensitive to
corner roundness (dashed in the design map), and wider inlets give lower frequencies.

**What changed from the first version.** The first version fixed Ca = 0.003 for every design and
treated Ca < 0.01 as the squeezing limit. Its designs (w_in/w = 0.33 at q = 4.7 and 4.4) had
S = 0.098 and 0.088, about 5 times S_crit, so they were in the jetting regime by the Korczyk et
al. criterion. They also moved by 38 % and 46 % in volume if the corner roundness was 0.1 w
instead of 0.01 w. Both are excluded now. The highest frequency inside the regime is about 5
times lower than the first version reported (25 s⁻¹ instead of 122 s⁻¹ for 0.5 nL).

The bubble series closest to these designs (w_in/w = 0.33, h/w = 0.33) agreed with its
experiments within 14 % at every point. That agreement was obtained with gas bubbles at
eps = 0.1 w. It supports the model form at this inlet ratio, not the eps = 0.01 w liquid branch
the designs use.

## Changed-input example: the target volume changed on a fixed junction

**Input changed:** the target volume, from V1 = 0.5 nL to V2 = 2.0 nL, with junction D1 kept
and only the pumps adjusted.

**Result:** q would have to rise from 0.87 to 10.5, outside the validated range of 0.1 to 10
(flagged). At q = 10.5 the squeezing regime leaves only Ca = 7.0e-5 to 1.3e-4. The design rule's
Ca (6.4e-5) falls below the leaking bound (flagged), and q_c would drop from 0.85 to
0.022 µL/min, giving about 2 droplets per second. The droplet would be 696 µm long (6.0 w)
instead of 174 µm. At this q the corner roundness matters much more: the q needed ranges from
7.1 to 11.1 over eps = 0 to 0.1 w, and at q = 10.5 the volume would be 1.91 to 2.79 nL (spread
40 %). Inside its design window D1 makes only 0.44 to 0.90 nL.

The reverse request fails as well. Junction D2 asked for 0.5 nL would need V/(h w²) = 0.35,
below its filling volume of 1.08. That is physically impossible, because the tip that fills
the junction before pinch-off is already larger than the target. D2 makes no droplet smaller
than 1.61 nL inside the regime, or 1.82 nL inside its design window.

**Engineering consequence:** droplet volume scales with h w² of the junction. Inside the design
window the flow-rate ratio only trims it by a factor of about 2 (0.44 to 0.90 nL for D1, 1.82
to 3.35 nL for D2). A factor of 4 in target volume therefore needs a new junction, not new pump
settings. Pushing the pumps to high q also forces a very low Ca, which costs throughput and
moves the junction towards the leaking regime.

## Out-of-regime requests (flagged, not designed)

| Request | Outcome | Flag |
| --- | --- | --- |
| F1: V = 0.02 nL with the assumed fabrication grid | no feasible design | the smallest droplet inside the validated range is 0.079 nL (h = 25 µm, w = 55 µm, w_in/w = 0.33, q = 0.1), and it needs Ca between 7.4e-3 and 0.01 to stay in the regime; a shallower mould or another break-up regime is needed |
| F2: V2 from D2 at 1000 droplets per second | requires Ca = 0.14 (q_c = 141 µL/min), S = 0.47 | S is 27 times S_crit and Ca is above the original's experimental range: a thread forms (jetting) and the model does not apply. At the S-number bound (Ca = 5.0e-3) D2 reaches about 36 s⁻¹ |
| F3: V2 in a square channel, h = w = 100 µm, w_in = w | model returns q = 0.98 | h/w = 1 is outside the validated range 0.11 to 0.48; in square channels, gutter leakage makes the size depend on Ca at low Ca (Korczyk et al. 2019) |
| F4: D1 operated at Ca = 1e-4 (q_c = 0.035 µL/min) | model returns the same q = 0.87 | q Ca = 8.7e-5 is below 10 beta = 7.4e-4: leaking regime, so droplets will be larger than predicted and sensitive to the flow rate |

## Inputs outside the reproduced range

These apply to every design above (`inputs_outside_reproduced_range` in `comparison.json`):

- **Liquid-liquid branch, eps = 0.01 w.** Not reproduced here. The original validated it at one
  geometry only (w_in/w = 1, h/w = 0.48), and that series is not in the open replot. The
  replicators report that the original's liquid-droplet line is steeper than the equations
  give, and that the original's experimental points lie closer to the line the equations give
  (content.tex, Results, "Figure O3"). The corner-roundness band above bounds the effect of eps
  but not of other differences between liquid droplets and bubbles.
- **Viscosity ratio 1.14.** The original's experiments covered 0.01 to 0.1 (Nekouei and
  Vanapalli, Table 1). The model has no viscosity-ratio term. Nekouei and Vanapalli's VOF
  simulations find the size does not vary appreciably below a ratio of 1 and increases above
  it, so the droplets are expected to be somewhat larger than predicted. This is an
  extrapolation.
- **Ca.** The operating Ca of the original's experiments is not known (closed source); only
  Ca < 0.01 is reported.
- **Regime bounds.** beta and S_crit were fitted in square channels and are applied to shallow
  channels (h/w 0.22 and 0.29) as indications. The factor-2 margins are assumed.
- **Short droplets.** At q near 1 the droplets are 1.4 to 1.5 w long. Korczyk et al. note that
  for such short droplets shear during the filling stage should be included, which this model
  does not do.

Both chosen designs have h/w inside the range this reproduction confirmed (0.17 to 0.33). A
design with h/w outside it would carry a non-blocking evidence note.

## Assumptions and limits

- The leaking bound beta = 7.4e-5 and S_crit = 0.017 were fitted for square channels and one
  fluid pair.
- The validity bounds come from the ranges covered by the original's experiments (as restated
  by secondary sources), not from a stated validity statement of the original.
- The 15 % corner-roundness band and the factor-2 Ca margins are design choices, not physics.
- The h = 25 µm minimum and the 5 µm width step are assumptions about fabrication.
- Droplet length is estimated as V/(h w), which holds for droplets longer than w.
