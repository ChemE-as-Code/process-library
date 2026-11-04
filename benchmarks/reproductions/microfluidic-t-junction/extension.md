# Design extension: T-junction dimensions for a target droplet volume

> **HYPOTHETICAL design extension. Not validated.** These designs come from inverting the van
> Steijn 2010 model, which is only partially reproduced here (see `comparison.md`). The fluid
> pair and fabrication grid are assumed. No junction was built or tested. Use the numbers to
> choose a starting geometry, not as a specification.

All values below are from `results/comparison.json` (`design_extension`). The inputs and their
labels are in `inputs.yaml` under `design_extension`.

## Question and method

The question: which channel width w, depth h and inlet width ratio w_in/w, together with which
flow-rate ratio q = q_d/q_c, give a target droplet volume V while staying in the regime where
the model holds?

The model is linear in q: V/(h w²) = v_fill(w_in/w, h/w) + alpha(w_in/w, h/w, eps) q. For a given
geometry the inversion is therefore exact: q = (V/(h w²) - v_fill)/alpha. `run.py` evaluates
this on an assumed fabrication grid:

- h = 25, 50, 75 or 100 µm;
- w = 50 to 500 µm in 5 µm steps;
- seven inlet ratios from 0.33 to 3.

A design is **feasible** if it lies inside every validity bound:

- h/w from 0.11 to 0.48;
- w_in/w from 0.33 to 3;
- q from 0.1 to 10;
- Ca at most 0.01;
- q Ca at least 10 beta = 7.4e-4, the leaking bound of Korczyk et al. 2019.

A feasible design is **nominal** if q is also between 0.5 and 5.

Among the nominal designs, the chosen one gives the highest droplet frequency at the operating
capillary number Ca = 0.003. The fluid pair is FC-40 droplets in hexadecane (mu_c = 3.6 mPa s,
mu_d = 4.1 mPa s, gamma = 7.3 mN/m, measured by Korczyk et al. 2019), and the corner roundness
is eps = 0.01 w.

Every feasible design was put back through the forward model. The largest relative deviation
from the target was 2.2e-16, against a tolerance of 1e-9.

## Results for two target volumes

| | D1 | D2 |
| --- | --- | --- |
| Target volume V | 0.50 nL | 2.0 nL |
| Depth h | 25 µm | 50 µm |
| Main channel width w | 85 µm | 135 µm |
| Inlet width w_in (w_in/w) | 28 µm (0.33) | 45 µm (0.33) |
| Aspect ratio h/w | 0.294 | 0.370 |
| v_fill, alpha | 1.079, 0.359 | 1.053, 0.258 |
| Flow-rate ratio q_d/q_c | 4.710 | 4.424 |
| q_c, q_d at Ca = 0.003 | 0.776, 3.65 µL/min | 2.46, 10.9 µL/min |
| Droplet frequency | 122 s⁻¹ | 91 s⁻¹ |
| Droplet length V/(h w) | 235 µm (2.8 w) | 296 µm (2.2 w) |
| Forward check, predicted V | 0.5000 nL (rel. dev. 0) | 2.000 nL (rel. dev. 0) |
| Volume range over q = 0.1 to 10 | 0.20 to 0.84 nL | 0.98 to 3.31 nL |
| Regime flags | none | none |

Number of designs found:

- **V1 (0.50 nL):** 71 feasible and 51 nominal designs. All need h = 25 µm, with w from 55 to
  125 µm and q from 0.28 to 8.1. A 50 µm-deep junction cannot make 0.5 nL inside the validated
  range: the narrowest width it allows (h/w at most 0.48) is 105 µm, and its filling volume
  alone is already larger than 0.5 nL.
- **V2 (2.0 nL):** 249 feasible and 174 nominal designs, at h = 25 or 50 µm with w from 55 to
  225 µm. The best 25 µm-deep option (w = 145 µm, q = 4.97) gives 55 s⁻¹, against 91 s⁻¹ at
  50 µm.

`results/fig_design_map.svg` shows the required q against w for every inlet ratio at the chosen
depths, with the validated q band and the q window from 0.5 to 5. `results/drawing_D1.svg` and
`results/drawing_D2.svg` are dimensioned plan views, drawn to scale from these values. Each
shows w, w_in, the predicted droplet, the flow rates, and a section A-A with the depth.

Both chosen designs use the narrowest validated inlet (w_in/w = 0.33). At fixed Ca, the
frequency rises with q w h. A narrow inlet has a small squeezing coefficient, so a given volume
needs a higher q, which means more dispersed-phase flow per droplet cycle. The design therefore
sits at the edge of the validated inlet range. The closest reproduced series (w_in/w = 0.33,
h/w = 0.33, gas bubbles) agreed with its experiments within 14 % at every point.

## Changed-input example: the target volume changed on a fixed junction

**Input changed:** the target volume, from V1 = 0.5 nL to V2 = 2.0 nL, with junction D1 kept
and only the pumps adjusted.

**Result:** q would have to rise from 4.71 to 27.9, outside the validated range of 0.1 to 10
(flagged). The droplet would be 941 µm long (11 w) instead of 235 µm. Within the validated q
range, D1 can make only 0.20 to 0.84 nL.

The reverse request fails as well. Junction D2 asked for 0.5 nL would need V/(h w²) = 0.55,
below its filling volume of 1.05. That is physically impossible, because the tip that fills
the junction before pinch-off is already larger than the target. D2 makes no droplet smaller
than 0.98 nL.

**Engineering consequence:** droplet volume scales with h w² of the junction. The flow-rate
ratio only trims it within a factor of about 3.4 to 4.2 (the validated q range). A factor of 4
in target volume therefore needs a new junction, not new pump settings.

## Out-of-regime requests (flagged, not designed)

| Request | Outcome | Flag |
| --- | --- | --- |
| F1: V = 0.02 nL with the assumed fabrication grid | no feasible design | the smallest droplet inside the validated range is 0.079 nL (h = 25 µm, w = 55 µm, w_in/w = 0.33, q = 0.1); a shallower mould or another break-up regime is needed |
| F2: V2 from D2 at 1000 droplets per second | requires Ca = 0.033 (q_c = 27 µL/min) | above the squeezing limit Ca = 0.01: shear starts to break the thread, and the model over-predicts the size; D2 reaches about 300 s⁻¹ at Ca = 0.01 |
| F3: V2 in a square channel, h = w = 100 µm, w_in = w | model returns q = 0.98 | h/w = 1 is outside the validated range 0.11 to 0.48; in square channels, gutter leakage makes the size depend on Ca at low Ca (Korczyk et al. 2019) |
| F4: D1 operated at Ca = 1e-4 (q_c = 0.026 µL/min) | model returns the same q = 4.71 | q Ca = 4.7e-4 is below 10 beta = 7.4e-4: leaking regime, so droplets will be larger than predicted and sensitive to the flow rate |

## Assumptions and limits

- The model has no viscosity-ratio term. FC-40 in hexadecane has mu_d/mu_c = 1.14, slightly
  above 1. According to Nekouei and Vanapalli, the size starts to grow with viscosity ratio
  above 1. The assumed limit for flagging is 1.5.
- The leaking bound beta = 7.4e-5 was fitted for square channels and one fluid pair. Here it
  is used as an indicative bound for shallow channels.
- The validity bounds come from the ranges covered by the original's experiments (as restated
  by secondary sources), not from a stated validity statement of the original.
- eps = 0.01 w assumes sharp, well-made corners. At D1 a corner roundness of 0.1 w would raise
  alpha and lower the q needed. `run.py` does not explore this.
- The h = 25 µm minimum and the 5 µm width step are assumptions about fabrication.
- Droplet length is estimated as V/(h w), which holds for droplets longer than w.
