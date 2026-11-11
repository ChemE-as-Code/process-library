# Comparison: CAU-10-H uptake series (4TU sample 8) vs the article's Figure 7 and Table S7

Two comparisons, each under its own frozen file: against our digitisation of Figure 7
(`tolerances.yaml`, **pass**, first part below), and against the values the authors tabulate
for the same sample in Table S7 of the Supporting Information (`tolerances-si.yaml`,
**partial**: the Henry constant fails, [second part](#second-comparison-sample-8-vs-table-s7-row-8)).

- **Reference:** `source.yaml`. Article 10.1002/adma.202210050 (early-view version of record,
  pages 1 to 13 of 13, TU Delft copy, sha256 pinned), Figure 7a and 7b, digitised by us
  (`digitise_figure7.py` re-derives the pixel centres and the calibration from the pinned PDF). Data: 4TU 10.4121/22009211 v1, file
  `8 - CAU-10-H.csv` (sha256 pinned), CAU-10-H pellets at 313.000 K.
- **Tolerances:** `tolerances.yaml`, frozen in commit d25eee1 together with `source.yaml` and
  `inputs.yaml`, before `run.py` existed (`run.py` was added in 8d9d7e7).
- **Run:** 2026-11-04T14:16:29Z, `uv run benchmarks/reproductions/mof-water-harvester-cau10/run.py`
  from the repository root, from an empty cache. Python 3.13.16, numpy 2.3.4, scipy 1.16.3,
  matplotlib 3.10.7, pyyaml 6.0.3; transitive dependencies fixed by `exclude-newer =
  2026-11-04T00:00:00Z` in the script header. Both downloads matched their sha256, and `p_sat`
  matched the IF97 verification values (Table 35, 300 K, 500 K, 600 K) to better than 1e-8. A
  second run gave byte-identical `results/`. The verdict and every compared value are unchanged
  from the first run (2026-11-04T13:55:52Z, commit 8d9d7e7); the later runs only add design
  outputs (below and `extension.md`).
- **Order:** before the freeze the data file and the figure were only read by eye during data
  inspection (disclosed in the header of `tolerances.yaml`). No computed comparison existed
  before d25eee1.

## Result: PASS under the frozen rule of `tolerances.yaml` (4 of 4 checks)

| Check | Reference | Ours | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| α, p/p0 at half capacity | 0.1968 (marker H5, digitised ±0.0013) | 0.1972 | +0.0004 | abs 0.005 | pass |
| Δp/p0 between 75 % and 25 % of capacity | 0.0069 (marker H5, digitised ±0.0016) | 0.0074 | +0.0004 | abs 0.004 | pass |
| Marker identification | one CAU-10-H marker within the α tolerance | H5 only; next is H4 at α 0.1781, 0.019 away; H5's two panels agree in K_H (Δlog10 0.000) | - | rule | pass |
| Saturation pressure implied by the file (p/p0 and mmHg columns) | 7325.6 Pa, IAPWS-IF97 at 313.000 K | 7326.1 Pa (same for every point) | +0.007 % | rel 0.5 % | pass |

**The four checks are not four independent agreements.** The marker is chosen as the one
nearest the computed α, and the α check then compares α with that same marker: the α check and
the marker identification are one test (a CAU-10-H marker lies within 0.0004 of our α, and no
other within the tolerance). The Δp/p0 check does not single out H5 either: H3 (0.0101,
deviation +0.0027) would also pass the 0.004 tolerance; H1, H2 and H4 would not. The
saturation-pressure check is a data-integrity check of the file's temperature basis, not a
reproduction of a reported value. The independent evidence is therefore: one marker within
0.0004 of our α, and a Δp/p0 consistent with that marker (and with one other).

Total capacity for the descriptors is the uptake at the highest measured p/p0 (0.4246):
16.504 mmol/g, 0.2973 g/g. The 25 %, 50 % and 75 % points lie at p/p0 0.1948, 0.1972 and
0.2022 on the adsorption branch. Deviations are rounded from the unrounded values in
`results/comparison.json`.

What this shows: the descriptors we compute from the published series (branch split, capacity,
interpolation) are consistent with Figure 7's marker H5 within digitisation error, with the
marker selected by α. It also confirms that the file's relative pressures refer to water at
313.0 K, which is the temperature basis of the sizing.

What it does not show: under this file, that sample 8 is H5 is inferred by us (nearest α), not
stated in the article. The check guards against a wrong match only by requiring that no other
marker is within tolerance. Table S7, obtained since, labels sample 8 and confirms H5
(second part, digitisation check); this first verdict is kept as computed.

## Context comparisons (frozen, outside the pass rule)

| Quantity | Reference | Ours | Note |
| --- | --- | --- | --- |
| Henry constant K_H | 2160 cm3/g (H5, digitised) | not evaluable | as frozen: definition in SI Section 7 not available; a candidate, q/(p/p0) at the lowest point, gives 1733 cm3/g (-20 %). That candidate is on a cm3(STP)/g basis and is not the Section 7 quantity (q R T / p, about 15.8 times larger for the same ratio), so its -20 % says nothing about agreement. Now evaluated under `tolerances-si.yaml` (second part) |
| Step position at 40 °C | 0.15 to 0.165 (in-situ PXRD, other sample) | α 0.197; 10 % to 90 % of capacity between 0.189 and 0.219 | sample 8 steps about 0.03 higher than the PXRD transition |
| Uptake just after the step | 0.32 g/g (Figure 1 powder, other sample, ambient) | 0.277 g/g at p/p0 0.25 | -13 %; pellets, binder content unknown |
| Step at ambient temperature | 0.18 (Figure 1 powder) | 0.182 at 298.15 K | sample 8's α moved by the Dubinin-Polanyi characteristic curve |
| Vapour density at 16 % RH, 40 °C | 8 g/m3 | 8.17 g/m3 | IF97 p_sat, ideal gas |
| Vapour density at 18 % RH, ambient | 4 g/m3 | 4.15 g/m3 at 25 °C | as above |

## Deviations and explanations

1. **α and Δp/p0 (+0.0004 each).** Both are within one marker's digitisation error (±3 px;
   ±6 px for H5, see item 6).
   SI Section 7 reads total capacity at p/p0 0.85, which sample 8 does not reach; what the
   authors used for this series is not stated (sentence updated after the SI was obtained;
   written under `tolerances.yaml` as "the capacity definition behind Table S7 is unknown").
   Checked after the run: with a capacity
   10 % lower or higher than ours, α is 0.1968 or 0.1978 (within the ±0.002 that
   `tolerances.yaml` assumed), but Δp/p0 is 0.0057 or 0.0110. The frozen reason gave ±0.002
   for this effect, which **understates the upper side**: had the article used a capacity 10 %
   above the uptake at p/p0 0.4246 (for example a value near saturation, which sample 8 does
   not reach), our Δp/p0 would differ from the marker by +0.0041 and fail the 0.004 tolerance.
   The agreement with H5 at our definition (+0.0004) suggests that the article's capacity is
   close to the uptake at the highest measured point, but that is an inference. The tolerance
   is not changed; a revision would be a new file.
2. **K_H not evaluable** under `tolerances.yaml`. The article defines K_H in SI Section 7,
   which could not be obtained when that file was frozen (publisher returns HTTP 403 to
   scripted requests; no open copy). The candidate ratio uses one point at p/p0 0.0012 and is
   not a Henry-law fit; it is reported, not compared. It is in cm3(STP)/g, not on the Section 7
   basis (q R T / p0 per unit p/p0), on which the same ratio is about 27 500 cm3/g. The context item stays as frozen; the
   SI has since been obtained and K_H is compared under `tolerances-si.yaml` (second part).
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
6. **Digitisation of covered markers (found after the freeze).** In panel a, H5 (and H1, H2,
   H4) lie partly under markers of other materials, so only part of the circle outline is
   visible; in panel b, H5's centre moves by up to 6 px between search variants
   (`digitise_figure7.py`). We now state ±6 px for these centres (±0.0032 in Δp/p0, ±0.0027 in
   α; `source.yaml` `uncertainty_occluded_after_freeze`). The frozen tolerance reasons assumed
   ±3 px; both deviations (+0.0004) remain well inside either figure. The tolerances are not
   changed.

## Second comparison: sample 8 vs Table S7 row 8

- **Reference:** Supporting Information of 10.1002/adma.202210050
  (`adma202210050-sup-0001-SuppMat.pdf`, 37 pages, sha256 `e906a067…7b59b`), Table S7 row 8
  (p. 31) and Section 7 (p. 30). Scripted requests to the publisher return HTTP 403; the
  repository owner obtained the file on 2026-11-04. It is not committed; the numbers used are
  restated in `source.yaml` (`paper.supporting_information`) and `tolerances-si.yaml`. Row 8
  names the 4TU dataset, CAU-10-H and 313 K.
- **Tolerances:** `tolerances-si.yaml`, frozen in its own commit (ac79bdf6) before `run.py`
  computed any Henry constant or read the file. `tolerances.yaml` is unchanged, and its verdict
  (pass, above) is reported beside this one in `results/comparison.json` (`table_s7`).
- **Blindness (disclosed in `tolerances-si.yaml`).** The α and Δp/p0 checks are **not blind**:
  our values (0.19719, 0.00739) were already published under `tolerances.yaml` when Table S7
  was read and the tolerances were set, so their outcome was foreseeable. The Henry slope and
  K_H checks are blind: neither the Section 7 fit slope nor the Section 7 K_H had been computed
  by us; a single-point cm3(STP) ratio (1733 cm3/g, a different quantity) had been published
  under `tolerances.yaml`. The digitisation check is not blind.
- **Run:** 2026-11-04T22:24:40Z, same command and environment as above, data read from the
  cache (sha256 checked). Two consecutive
  runs gave byte-identical `results/`. Apart from the new `table_s7` section, the only change
  in `results/` is `inputs_sha256` of `source.yaml` and `inputs.yaml`, which were edited
  (corrections below); every computed value under `tolerances.yaml` is unchanged.
  Rerun after review (2026-11-04): the sample-identity items now read the file number, the
  Metadata.txt entry number and the dataset's numbering rule from the fetched files, the
  digitisation budgets are parsed from the frozen rule, and the capacity definition in
  `results/` is our own restatement. No check value, tolerance or verdict changed.
- **Method (frozen):** least squares through the origin on the 9 adsorption points with
  0 < p/p0 ≤ 0.1 (p/p0 0.0012 to 0.0836; the next point is at 0.1777); K_H = slope R T / p0 with
  T = 313.000 K, p0 = 7325.6 Pa (IAPWS-IF97), R = 8.314462618 J/(mol K), in cm3/g.

### Result: PARTIAL under `tolerances-si.yaml` (3 of 5 checks pass; both Henry checks fail)

| Check | Table S7 row 8 | Ours | Deviation | Tolerance | Blind | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Sample identity | 4TU 10.4121/22009211, CAU-10-H, 313 K, row 8 | file `8 - CAU-10-H.csv` (number 8 from the fetched file name); Metadata.txt entry 8 (number read from its CAU-10-H heading), CAU-10-H pellets, 313.000 K; Metadata.txt states that its numbering is the Table S7 position | - | rule | - | pass |
| α | 0.197 | 0.19719 | +0.00019 | abs 0.001 | no | pass |
| Δp/p0(75–25 %) | 0.007 | 0.00739 | +0.00039 | abs 0.001 | no | pass |
| Henry slope | 6.14 mmol/g | 8.8915 mmol/g | +44.8 % | rel 3 % | yes | **fail** |
| K_H | 2166 cm3/g | 3158.7 cm3/g | +45.8 % | rel 4 % | yes | **fail** |

Verdict under `tolerances.yaml`, reported unchanged: **pass** (4 of 4).

### Variants (outside the pass rule, stated in `tolerances-si.yaml` before the run)

| Variant | Slope (mmol/g) | K_H (cm3/g) | Slope dev. | K_H dev. | R2 uncentred | R2 centred |
| --- | --- | --- | --- | --- | --- | --- |
| Frozen method: through the origin, 0 < p/p0 ≤ 0.1 | 8.8915 | 3158.7 | +44.8 % | +45.8 % | 0.9395 | 0.6525 |
| With intercept (0.1575 mmol/g), same points | 6.1376 | 2180.4 | −0.04 % | +0.66 % | 0.9933 | 0.9616 |
| Bound p/p0 < 0.1 | 8.8915 | 3158.7 | +44.8 % | +45.8 % | 0.9395 | 0.6525 |
| p0 implied by row 8 (7377.1 Pa, +0.70 % vs IF97), slope of the frozen method | 8.8915 | 3136.6 | +44.8 % | +44.8 % | - | - |

The bound variant is identical because no adsorption point lies between p/p0 0.0836 and 0.1.

### Deviations and explanations (found after the run; method and tolerances not changed)

1. **Henry slope and K_H, +45 %.** In the fit window the series does not pass through the
   origin: the uptake is 0.093 mmol/g at p/p0 0.0012, and q/(p/p0) falls from 77 to
   7.6 mmol/g across the nine points. A line through the origin is therefore steeper than the
   points' own trend. The fit with an intercept reproduces the tabulated slope to 0.04 %
   (6.1376 against 6.14). This suggests that the authors fitted with an intercept, which the
   equation stated in Section 7 does not contain. That is our inference from the variant,
   made after the run. The frozen method is not changed and the two checks fail as frozen. The
   frozen reason expected the unstated fit details (intercept or not, bound, weighting) to stay
   within 3 %. For this series the intercept alone moves the slope by 45 %, so that judgement
   was wrong.
2. **p0 basis, +0.7 %.** The row's slope and K_H imply p0 = R T slope / K_H = 7377 Pa
   (7376.7 Pa with the SI's R = 8.314), 0.70 % above IF97 at 313.000 K. IF97 gives that pressure
   at 313.13 K. The SI does not state its p0 source. The intercept variant's K_H (+0.66 %) is
   within this basis difference. Combining the intercept slope with the row's p0 gives
   6.1376 × R T / 7377.1 Pa = 2165 cm3/g. That is arithmetic on two reported variants, not a
   variant computed by `run.py`.
3. **R2 not reproduced.** Row 8 gives 0.9562. Ours: 0.9616 with intercept (centred), 0.9395
   through the origin (uncentred), 0.6525 through the origin (centred). None agrees to the
   stated four decimals. Not explained here; R2 is context and has no verdict.
4. **α and Δp/p0 (+0.00019, +0.00039).** Both are within the table rounding (±0.0005) and
   follow from our capacity choice (the uptake at p/p0 0.4246). These checks are not blind
   (above).

### Digitisation check (beside the verdict, not blind): pass

Our Figure 7 marker H5 against row 8: α 0.19675 vs 0.197 (−0.00025, tolerance 0.0018);
Δp/p0 0.00694 vs 0.007 (−0.00006, tolerance 0.0037); log10 K_H 3.3343 (2159 cm3/g) vs 3.3357
(2166 cm3/g), −0.0014 in both panels (tolerance 0.0171). Our digitisation agrees with the
authors' tabulated values. Row 8's values place sample 8 at marker H5, the marker picked by
nearest α under `tolerances.yaml`. The frozen α and log10 K_H budgets use the uncovered ±3 px,
although `source.yaml` gives ±6 px for H5 in panel b (±0.0027 in α, ±0.033 in log10 K_H); the
deviations (−0.00025, −0.0014) are inside either figure, so the outcome does not depend on it.
`run.py` reads the three budgets from the frozen rule text.

### Total capacity (context, no verdict): an open question to the authors

Row 8 gives a total capacity of 0.92 in a column headed g/g, and Section 7 reads total
capacity at p/p0 0.85. Sample 8's series ends at p/p0 0.4246, where its uptake is
16.504 mmol/g, that is 0.2973 g/g; 16.504 / 18.015 = 0.916. We do not know what the 0.92
represents for a series that ends below 0.85, or at which relative pressure it was read for
this sample. We record this as a question for the authors, not as a finding.

## Corrections after the freeze

Found in review; descriptive fields only. No reference value, pixel centre, calibration, input
value or tolerance changed, and `tolerances.yaml` is untouched. The frozen text is in d25eee1.

| File | Field | Frozen text | Corrected |
| --- | --- | --- | --- |
| `source.yaml` | `paper.version` | "published version (Adv. Mater. 2023, 36(12), e2210050)" | early-view version of record, pages 1 to 13 of 13, later assigned to 36(12) e2210050; locators follow that pagination |
| `source.yaml` | `sample_mapping...branches` | 35 adsorption, 54 desorption points | 38 and 51 (as `comparison.json` `measured_series` has always reported) |
| `source.yaml` | K_H of steep-step materials | p. 10 | p. 11 (p. 10 holds Figure 7 only) |
| `source.yaml` | `reference_figure` | no digitiser committed; ±3 px for every marker | `script: digitise_figure7.py`; ±6 px for covered markers and H5 (added field) |
| `inputs.yaml` | labels | IUPAC molar mass, IF97 p_sat, h_fg and c_p of water "measured"; `branch_split` "measured" | "reference property" (a fourth label, README); `branch_split` "assumed" (processing rule) |
| `inputs.yaml` | `interpolation` rationale | "both branches are monotonic" | adsorption branch monotonic; desorption branch monotonic below p/p0 0.1855 only, and read only there; gap 0.0836 to 0.1777 stated |
| `inputs.yaml` | IF97 check | stated, not run | now run at every start (`run.py` `check_p_sat`) |
| `inputs.yaml` | adsorption enthalpy | no uncertainty | assumed ±10 % range, effect reported |
| `inputs.yaml` | bed temperature, changed RH | rationale only | the 0.5 K limit is enforced; the changed RH's measured segment is named |
| `inputs.yaml` | `negligible_working_capacity_fraction` rationale | 10 % of the working capacity "at the highest measured RH" (0.4246) | "at the top of the sweep (RH 0.42)", which is what `run.py` has always used; value unchanged |

Second round, 2026-11-04, after the SI was obtained (descriptive fields only; no reference
value, pixel centre, calibration, input value or tolerance changed; both tolerance files
untouched):

| File | Field | Frozen text | Corrected |
| --- | --- | --- | --- |
| `source.yaml` | `paper.supporting_information` | status "not obtained"; Table S7 and Section 7 not available | obtained by the owner on 2026-11-04, file names and sha256, not committed; Section 7 definitions and Table S7 row 8 restated as facts with locators |
| `source.yaml` | `descriptor_definitions` (K_H, total capacity) | K_H definition not available; total capacity not defined | pointers to SI Section 7 (fit on p/p0 0 to 0.1; capacity read at p/p0 0.85) |
| `source.yaml` | `sample_mapping.other_cau10_h` | five CAU-10-H data sets in Figure 7; row of sample 8 unknown | Table S7 lists six CAU-10-H rows; row 8 is sample 8; five markers found, two rows nearly coincide (inference) |
| `source.yaml` | `identification_of_sample_8` | inferred by nearest α | confirmed by Table S7 row 8: marker H5 |
| `inputs.yaml` | `total_capacity_for_descriptors` rationale | "Table S7 is not available" | SI defines it at p/p0 0.85, which sample 8 does not reach; value and label (assumed) unchanged |

## Gaps found (reported, not fixed here)

- SI not available when `tolerances.yaml` was frozen. Closed on 2026-11-04: the owner obtained
  it (second part). Still open: the SI does not state whether the Henry fit has an intercept,
  which R2 is given, the source of p0 (row 8 implies 7377 Pa, 0.7 % above IF97 at 313.000 K),
  or where total capacity was read for a series that ends below p/p0 0.85.
- Only one CAU-10-H isotherm temperature is published as data, so no isosteric heat can be fitted
  and every temperature transfer in the design extension rests on the characteristic-curve
  assumption.
- CAU-10-CH3 is not in the dataset (its isotherm in the article is reproduced from a 2013 paper).
  Tolerances were not changed after the run.
