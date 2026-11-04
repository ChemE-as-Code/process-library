# Comparison: CAU-10-H uptake series (4TU sample 8) vs the article's Figure 7

- **Reference:** `source.yaml`. Article 10.1002/adma.202210050 (published version, TU Delft copy,
  sha256 pinned), Figure 7a and 7b, digitised by us. Data: 4TU 10.4121/22009211 v1, file
  `8 - CAU-10-H.csv` (sha256 pinned), CAU-10-H pellets at 313.000 K.
- **Tolerances:** `tolerances.yaml`, frozen in commit d25eee1 together with `source.yaml` and
  `inputs.yaml`, before `run.py` existed (`run.py` was added in 8d9d7e7).
- **Run:** 2026-11-04T13:55:52Z, `uv run benchmarks/reproductions/mof-water-harvester-cau10/run.py`
  from the repository root, from an empty cache. Python 3.13.16, numpy 2.3.4, scipy 1.16.3,
  matplotlib 3.10.7, pyyaml 6.0.3. Both downloads matched their sha256. Two further runs gave
  byte-identical `results/`.
- **Order:** before the freeze the data file and the figure were only read by eye during data
  inspection (disclosed in the header of `tolerances.yaml`). No computed comparison existed
  before d25eee1.

## Result: PASS under the frozen rule (4 of 4 checks)

| Check | Reference | Ours | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| α, p/p0 at half capacity | 0.1968 (marker H5, digitised ±0.0013) | 0.1972 | +0.0004 | abs 0.005 | pass |
| Δp/p0 between 75 % and 25 % of capacity | 0.0069 (marker H5, digitised ±0.0016) | 0.0074 | +0.0004 | abs 0.004 | pass |
| Marker identification | one CAU-10-H marker within the α tolerance | H5 only; next is H4 at α 0.1781, 0.019 away; H5's two panels agree in K_H (Δlog10 0.000) | - | rule | pass |
| Saturation pressure implied by the file (p/p0 and mmHg columns) | 7325.6 Pa, IAPWS-IF97 at 313.000 K | 7326.1 Pa (same for every point) | +0.007 % | rel 0.5 % | pass |

Total capacity for the descriptors is the uptake at the highest measured p/p0 (0.4246):
16.504 mmol/g, 0.2973 g/g. The 25 %, 50 % and 75 % points lie at p/p0 0.1948, 0.1972 and
0.2022 on the adsorption branch. Deviations are rounded from the unrounded values in
`results/comparison.json`.

What this shows: the published series is the one behind Figure 7's marker H5, and our reading
of it (branch split, capacity, interpolation) gives the article's descriptors within the
digitisation error. It also confirms that the file's relative pressures refer to water at
313.0 K, which is the temperature basis of the sizing.

What it does not show: that sample 8 is H5 is inferred by us (nearest α), not stated in the
article, because Table S7 is not available. The check guards against a wrong match only by
requiring that no other marker is within tolerance. A labelled Table S7 would turn this into a
direct comparison.

## Context comparisons (frozen, outside the pass rule)

| Quantity | Reference | Ours | Note |
| --- | --- | --- | --- |
| Henry constant K_H | 2160 cm3/g (H5, digitised) | not evaluable | definition in SI Section 7 not available; a candidate, q/(p/p0) at the lowest point, gives 1733 cm3/g (-20 %) |
| Step position at 40 °C | 0.15 to 0.165 (in-situ PXRD, other sample) | α 0.197; 10 % to 90 % of capacity between 0.189 and 0.219 | sample 8 steps about 0.03 higher than the PXRD transition |
| Uptake just after the step | 0.32 g/g (Figure 1 powder, other sample, ambient) | 0.277 g/g at p/p0 0.25 | -13 %; pellets, binder content unknown |
| Step at ambient temperature | 0.18 (Figure 1 powder) | 0.182 at 298.15 K | sample 8's α moved by the Dubinin-Polanyi characteristic curve |
| Vapour density at 16 % RH, 40 °C | 8 g/m3 | 8.17 g/m3 | IF97 p_sat, ideal gas |
| Vapour density at 18 % RH, ambient | 4 g/m3 | 4.15 g/m3 at 25 °C | as above |

## Deviations and explanations

1. **α and Δp/p0 (+0.0004 each).** Both are within one marker's digitisation error (±3 px).
   The capacity definition behind Table S7 is unknown. Checked after the run: with a capacity
   10 % lower or higher than ours, α is 0.1968 or 0.1978 (within the ±0.002 that
   `tolerances.yaml` assumed), but Δp/p0 is 0.0057 or 0.0110. The frozen reason gave ±0.002
   for this effect, which **understates the upper side**: had the article used a capacity 10 %
   above the uptake at p/p0 0.4246 (for example a value near saturation, which sample 8 does
   not reach), our Δp/p0 would differ from the marker by +0.0041 and fail the 0.004 tolerance.
   The agreement with H5 at our definition (+0.0004) suggests that the article's capacity is
   close to the uptake at the highest measured point, but that is an inference. The tolerance
   is not changed; a revision would be a new file.
2. **K_H not evaluable.** The article defines K_H in SI Section 7, which could not be obtained
   (publisher returns HTTP 403 to scripted requests; no open copy). The candidate ratio uses
   one point at p/p0 0.0012 and is not a Henry-law fit; it is reported, not compared.
3. **Step higher than the PXRD transition.** The in-situ PXRD (another sample, humidity
   generator, 40 °C) puts the transition at 15 % to 16.5 % RH; sample 8's volumetric isotherm
   steps at 19 % to 22 %. Possible reasons, none tested here: shaping into pellets, sample
   history, humidity calibration of the PXRD cell, or the 30 s equilibration interval of the
   volumetric run. The sizing uses sample 8 only.
4. **Lower plateau than the powder.** 0.277 g/g at the end of the step against 0.32 g/g for the
   powder of Figure 1. Pellets usually contain binder; the content is not stated, so the per-gram
   basis of the sizing is "per gram of pellet".
5. **Low-pressure hysteresis.** On the desorption branch the loading at p/p0 0.03 to 0.07 is 1.7
   to 2 times the adsorption branch's (0.014 against 0.007 g/g at 0.03). The sizing reads the regeneration
   loading from the desorption branch, which is conservative.

## Gaps found (reported, not fixed here)

- SI not available: Table S7 (sample numbering, so the marker cannot be confirmed) and Section 7
  (K_H definition). A copy from the authors or an open SI deposit would close both.
- Only one CAU-10-H isotherm temperature is published as data, so no isosteric heat can be fitted
  and every temperature transfer in the design extension rests on the characteristic-curve
  assumption.
- CAU-10-CH3 is not in the dataset (its isotherm in the article is reproduced from a 2013 paper).
- The figures are not committed (CC BY-SA 4.0 data; README.md). Tolerances were not changed
  after the run.
