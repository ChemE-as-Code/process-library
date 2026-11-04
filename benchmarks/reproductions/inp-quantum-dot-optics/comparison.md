# Comparison: reported optics of in situ HF treated InP QDs vs our processing of the archived spectra

- **Reference:** `source.yaml` (4TU dataset v1, doi 10.4121/1370d230-bca3-4af4-af06-1a9f168a4b10.v1;
  Chem. Mater. 2022, 34, 10093, open access). Reported values are printed numbers from the text,
  SI captions or figure annotations. None is digitised.
- **Tolerances:** `tolerances.yaml`, frozen in commit 75775d98 with `source.yaml` and `inputs.yaml`,
  before the first comparison run. Unchanged since:
  `git diff 75775d98 HEAD -- benchmarks/reproductions/inp-quantum-dot-optics/tolerances.yaml` is empty.
- **Run:** 2026-11-04, `uv run benchmarks/reproductions/inp-quantum-dot-optics/run.py` from the
  repository root; Python 3.13.16, numpy 2.3.4, scipy 1.16.3, matplotlib 3.10.7, pyyaml 6.0.3
  (uv 0.13.0; transitive packages resolved with `exclude-newer = 2026-11-04T00:00:00Z` from the
  script metadata, added after review). `requires-python` admits 3.12 and 3.13 as the library
  convention sets; only 3.13 was run. 113 archive members fetched by HTTP range request, each checked against CRC-32 and
  sha256. Two consecutive runs gave byte-identical `results/`.
- **Order:** commits 1bf8d659 (sufficiency, mapping) and 75775d98 (freeze) come before the
  run.py commit. The sufficiency inspection printed raw integrals and absorbances; no quantum
  yield was computed by script before the freeze. git shows only this order. run.py and its
  results were first committed together in 0954f953, after the first comparison run and after
  later edits, so the state of the script at the first run is not recorded in git and cannot be
  audited. By the author's own record, the edits after the first run were to diagnostics and
  presentation: a post-hoc sensitivity (no absorbance baseline), no PL peak when the maximum sits
  at the window edge (trap-dominated samples; this sets their FWHM to none, which keeps them out
  of the quality screen, and is not used in any check), implied factors in the contrast table,
  and figure layout; no judged value changed. That claim rests on the author's record, not on
  git. Later cases should commit run.py, or the first-run `comparison.json`, before or at the
  first run.
- **Revisions after review (this file's run):** labels and notes in `inputs.yaml` (no value
  used by a check changed), an aliquot-volume sensitivity and the 330 nm retention in the
  extension, the `exclude-newer` date in the script metadata, and text corrections here and in
  README.md, extension.md and sufficiency.md. A second review relabelled `qy_ref` (a literature
  value the source uses) and `extension.epsilon_330` (a model value the source states) from
  measured to assumed, basis: source-stated, as ADR 0031 reserves measured for the source's
  data; no value changed. The check results are unchanged. `tolerances.yaml` is unchanged.

## Result: FAIL under the frozen rule (15 of 22 checks pass; 4 of 8 primary checks fail)

The four 2021 sessions reproduce well: the whole 150 °C series of Figure 1, the RT and 90 °C bounds,
Figure 4B (three of three independent files), the emission width and two of three lifetimes.
Every primary failure is in the two 2022 PLQY sessions (200 °C, ZnCl2, as-synthesized).

| Check | Quantity (sample) | Reported | Ours | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | PLQY, 150 °C 5 min (F1-150-05) | ca. 40 % | 42.4 % | +2.4 pp | 5 pp | pass |
| P2 | PLQY, 150 °C 60 min (F1-150-60) | 55 % | 55.9 % | +0.9 pp | 5.5 pp | pass |
| P3 | PLQY, RT, all four aliquots | < 5 % | max 2.5 % | - | bound | pass |
| P4 | PLQY, 90 °C, all four aliquots | < 5 % | max 3.9 % | - | bound | pass |
| P5 | PLQY, 200 °C 60 min (F1-200-60), Fig. 1F label | 67 % | 58.8 % | -8.2 pp | 6.7 pp | **fail** |
| P6 | PLQY, 200 °C, max of series | > 70 % | 65.2 % | - | bound | **fail** |
| P7 | PLQY, 200 °C + ZnCl2 (F1-200Z) | 85 % | 70.4 % | -14.6 pp | 8.5 pp | **fail** |
| P8 | PLQY, as synthesized (F1-AS), Fig. 1F label | < 0.2 % | 0.23 % | - | bound | **fail** |
| X1 | PLQY, 150 °C washed (text) | 64 % | 65.7 % | +1.7 pp | 6.4 pp | pass |
| X2 | same files, Figure 4B label | 54 % | 65.7 % | +11.7 pp | 5.4 pp | fail (pair passes: X1) |
| S1 | first-exciton peak, before (F1-150-00) | 476 nm | 476.8 nm | +0.8 nm | 3 nm | pass |
| S2 | first-exciton peak, 5 min (F1-150-05) | 463 nm | 457.0 nm | -6.0 nm | 3 nm | **fail** |
| S3 | red shift 5 → 60 min | red shift | +11.2 nm | - | ≥ 1 nm | pass |
| S4 | PL FWHM, 150 °C 60 min | ~70 nm | 65.5 nm | -6.4 % | 10 % | pass |
| S5 | PL FWHM, 150 °C 60 min | ~300 meV | 283 meV | -5.6 % | 10 % | pass |
| S6 | PLQY, heat-up, in situ HF (Fig. 4B) | 55 % | 53.3 % | -1.7 pp | 5.5 pp | pass |
| S7 | PLQY, heat-up, pure InF3 (Fig. 4B) | 45 % | 44.8 % | -0.2 pp | 5 pp | pass |
| S8 | PLQY, hot injection, pure InF3 (Fig. 4B) | 26 % | 26.8 % | +0.8 pp | 5 pp | pass |
| S9 | PLQY, pure InF3 S9 series, max | up to 28 % | 22.9 % | -5.1 pp | 5 pp | **fail** |
| S10 | average lifetime, as synthesized | 29 ns | 38.2 ns | +32 % | 15 % | **fail** |
| S11 | average lifetime, 200 °C | 107 ns | 102.8 ns | -4.0 % | 15 % | pass |
| S12 | average lifetime, 200 °C + ZnCl2 | 138 ns | 142.0 ns | +2.9 % | 15 % | pass |
| S13 | integrating-sphere PLQY (S19) | 84 % | 84.0 % | 0.0 pp | 8.4 pp | pass |

Count: 8 primary + 13 secondary + the pair = 22 units, 15 pass. The pair passes as one unit
because X1 passes and X2 fails, as `pair_rule` foresaw. The frozen `pair_rule` rests on a false
premise: it says the reported 64 % and 54 % cannot both lie within the band, but the two bands
overlap (57.6-70.4 % for X1, 48.6-59.4 % for X2), so a value from 57.6 % to 59.4 % would pass
both, and `run.py`, following the rule's wording, would then count the pair as failed. This
run is unaffected: 65.7 % lies only in the X1 band. `tolerances.yaml` is left unchanged
(ADR 0030). The checked values are in
`results/comparison.json`. Per-sample values (`results/sample_metrics.csv`,
`results/local/details.json`) and the figure `results/fig_plqy_time.svg` are git-ignored and
regenerated by `run.py` (licence decision pending, `results/NOTICE.md`).

## Deviations and explanations

1. **2022 sessions (P5, P6, P7).** Baseline-corrected OD at 387 nm (from `results/sample_metrics.csv`,
   which `run.py` regenerates and which is not committed while the licence decision is pending;
   these values are not in `comparison.json`):
   F1-200-05 0.084, F1-200-30 0.105, F1-200-60 0.071, F1-200-60W 0.119, F1-200Z 0.047. The
   offsets at 680-700 nm, which our frozen rule subtracts, are -0.003 to -0.009 OD.
   - *P5 and P7 (the two low-OD samples): absorbance baseline, a plausible cause.* F1-200-60
     (OD 0.071, offset -0.007) and F1-200Z (OD 0.047, offset -0.007) sit at or below the lower
     edge of the stated ~0.1. At OD 0.05 the offset changes the absorbed fraction by about 15 %. A
     post-hoc variant without the absorbance baseline (not judged; `results/local/details.json`,
     `diagnostics.posthoc_no_absorbance_baseline_pct`) gives 64.0 % for 200 °C 60 min (within
     67 ± 6.7) and 80.8 % for ZnCl2 (within 85 ± 8.5). For the 150 °C series it gives 52.3 %
     (60 min) and 39.9 % (5 min), so P1 and P2 would still pass. Low OD does not reliably cause a
     failure: the heat-up sample F4-HU-HF (OD 0.051, offset -0.005) passes S6 under the frozen
     rule (53.3 % against 55 %). The authors' baseline handling is not stated, so this offers an
     explanation but does not identify their procedure. The ZnCl2 sample is also flagged for its
     file name (60 min) against the stated 5 min.
   - *P6: unexplained.* The series maximum is F1-200-60W at 65.2 %. It lies inside the
     0.05-0.15 window with a small offset (-0.003); without the baseline it gives 65.8 %, still
     below 70 %. The highest post-hoc value in the series is 67.1 %. Figure 1E (inspected, not
     digitised) plots the three unwashed 200 °C points below 70 % and only the washed 200 °C
     point above it. The source's ">70 %" therefore most likely refers to the washed sample,
     F1-200-60W, which is the sample our P6 maximum already uses (`source.yaml` records "which
     aliquot is not stated", which remains true of the text). The failure stands and its cause
     is not identified.
2. **Refractive index (all PLQYs).** We correct for toluene against ethanol, (1.497/1.361)² = 1.21.
   Without it, every PLQY falls by 17 % (150 °C 60 min: 46.2 %). With it, the 150 °C series and
   Figure 4B agree, so the authors most likely applied it. For the 200 °C samples a hexadecane
   index (1.434) would lower our values by a further 8 %, so it does not explain P5-P7.
3. **As synthesized (P8).** 0.23 % against "< 0.2 %". The value is dominated by weak trap emission
   rising towards the 700 nm end of the record and by solvent Raman near 400-440 nm. A constant
   PL baseline (sensitivity variant) gives 0.09 %. The bound is sensitive to a baseline that the
   source does not state; the conclusion's "< 0.1 %" and Figure 1A's "< 1 %" bracket our value.
4. **Washed 150 °C sample (X1, X2).** One archived measurement carries two reported values: 64 %
   in the text and 54 % in Figure 4B (stored there under a file name saying "heat_up"). Our 65.7 %
   matches the text. Figure 4B's value may belong to another measurement that is not archived,
   or be a labelling error. We cannot tell which.
5. **First-exciton peak at 5 min (S2).** Etching flattens the band. Our smoothed local maximum lies
   at 457 nm; the text says 463 nm. The 5 min band is broad and shallow, and a peak-picking rule
   on a 21-point smoothed spectrum moves it by several nm. The before-treatment peak (476.8 nm) and
   the later red shift (to 468 nm at 60 min, 474.5 nm after washing) agree. The Figure 1C inset
   value of 469 nm (not judged) fits our 60 min peak (468.2 nm) better than the washed one.
6. **S9 maximum (S9).** 22.9 % at 30 min against "up to 28 %", just outside the 5 pp band. The 30 min
   aliquot has a scatter offset of 0.026 OD (precipitating InF3 or QDs). Figure 4B's hot-injection
   InF3 sample, from another session, gives 26.8 %. "Up to 28 %" may refer to that sample or to
   one not archived.
7. **As-synthesized lifetime (S10).** 38 ns against 29 ns. That record ends at 498 ns and has a
   fast component (5.6 ns) that our fit, with no instrument-response deconvolution, resolves
   poorly (reduced chi-squared 1.8). The intensity-weighted average depends strongly on the fit
   window here. The two long-lived samples (S11, S12) agree within 4 %.

## Diagnostics (not judged)

- Octylamine alone: 0.53 % against 0.34 % for the heated control (same session). This is
  consistent with "barely affects".
- In situ HCl and HBr (700 eq): 1.3 % and 1.6 %. In situ HF at the same dose: 28.6 %. This is
  consistent with the statement that only HF raises the PLQY. HCl and HBr come from other
  sessions than HF.
- Organic acids against the control: acetic +1.2 pp, hexanoic +1.8 pp, palmitic +0.5 pp,
  2-hexyldecanoic +0.1 pp. Small acids sit within the stated 1-2 %. All come from sessions other
  than the control.
- Triethylamine: PLQY 52.3 % against 49.8 % without it, with absorbance at 330 nm 0.27 against
  0.16 (control 0.43). Less InP is lost for the same PLQY, as stated, but across two sessions.
- Dose series S4 (absorbance only): A(330 nm) falls from 0.41 at 660 eq to 0.09 at 1100 eq.
  There are no PL files, so the stated optimum of 850-1000 eq cannot be checked.
- Integrating sphere (S13): the scan "EmScan8" has the larger scatter integral and is taken as
  the blank. The absorbed fraction is 0.23.

## Mapping verification

The internal file name in every absorbance header matches `mapping.csv` (0 mismatches). Every
sample with a reference was recorded with the same slits, step, dwell, repeats and correction
flags as its reference, on the same day. Of 61 rows, 8 are marked "AMBIGUOUS" or "NO REFERENCE"
in `mapping.csv` (F1-150-60W, F4-HI-HF, the four 200 °C rows, F1-200Z, S6-BZF-10). Another 41
carry milder notes, for example reused files, references linked by date, or conditions taken
from the Methods.

Tolerances were not changed after the run. A follow-up that learns the authors' baseline and
integration settings (specialist or author contact) should re-run against the same `tolerances.yaml`.
