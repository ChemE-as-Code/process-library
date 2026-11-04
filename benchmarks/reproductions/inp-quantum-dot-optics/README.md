# InP quantum dots: treatment records and optical quality

Case study for issue #342 (tracker #333, priority P3). Protocol: ADR 0030 (reproduction, tolerances
frozen first). Folder layout: ADR 0031 (a reproduction plus a labelled design extension; status
Proposed, merged to main in PR #344 after this branch was cut, so it is not yet on this branch).
The case depends on ADR 0031: it has no cheme case (`case/`), which ADR 0030 lists, because the
model is a spectrum analysis that no cheme unit covers.

**Engineering question.** Which recorded treatment conditions of InP quantum dots can be linked to
measurable changes in their optical spectra?

**Source.** Ubbink et al., "A Water-Free In Situ HF Treatment for Ultrabright InP Quantum Dots",
Chem. Mater. 2022, 34, 10093 (open access, CC BY 4.0). Underlying data: 4TU.ResearchData, doi
10.4121/1370d230-bca3-4af4-af06-1a9f168a4b10.v1 (CC BY-NC-SA 4.0). The data are downloaded at
runtime and are not committed (see `source.yaml`, reuse terms).

## Status

| Item | Status |
| --- | --- |
| Reproduction | **fail** under the frozen rule: 15 of 22 checks pass. All four primary failures (P5-P8: 200 °C, ZnCl2, as synthesized) are in the two 2022-03 PLQY sessions. The secondary failures are S2 (5 min peak position, 2021-12-08), S9 (InF3 series, 2022-01-10) and S10 (as-synthesized lifetime, 2022-03-22), and X2 inside a passing pair. The 150 °C series of Figure 1E, the RT and 90 °C bounds, Figure 4B, the emission width and the 2022-10 sphere PLQY (S13) pass. See `comparison.md`. |
| Independent validation | none (the only data are the authors' own measurements) |
| Design extension | hypothetical, not validated (`extension.md`) |
| Specialist review | not yet (optional follow-up: nanocrystal processing and optical spectroscopy) |

**Answer within the evidence.** Within one measurement session, with one factor varied, these
recorded conditions give PLQY changes larger than the measurement band:

- treatment temperature (RT and 90 °C below 4 %, 150 °C 42-56 %);
- treatment time at 150 °C (0 to 5 min, and 5 to 60 min);
- reagent (heated control or octylamine below 1 %, in situ HF 55 %);
- benzoyl fluoride dose at 180 min (700 eq 29 %, 1400 eq 55 %; the octylamine amount for the
  700 eq sample, SI Figure S7, is not stated, so the amine may also differ);
- synthesis route under pure InF3 (hot injection 27 %, heat-up 45 %);
- InF3 treatment time;
- washing at 150 °C (60 min 55.9 %, washed 65.7 %; sample identity flagged, the washed files
  are also the Figure 4B sample, see Evidence gaps).

Temperature and time also shift the first-exciton peak (blue shift on etching, then about 11 nm
red shift) and narrow the emission (to about 283 meV). The other contrasts in the data cross
measurement sessions and also change dose, solvent or sample identity: 150 against 200 °C, ZnCl2,
in situ HF against InF3 on hot-injection QDs, the acid identity, and triethylamine. They are
confounded and are not attributed to the treatment. The optical data say nothing about surface
chemistry as a cause, and nothing about scale-up. Table: `results/comparison.json`, `contrasts`.

## Rerun

From the repository root (needs uv and network access to data.4tu.nl; about 1 MB is fetched):

```sh
uv run benchmarks/reproductions/inp-quantum-dot-optics/run.py
uv run benchmarks/reproductions/inp-quantum-dot-optics/run.py --verify-archive   # optional: stream the full 3.47 GB archive once and check its sha256
```

The cache lives in `${XDG_CACHE_HOME:-~/.cache}/cheme-reproductions/inp-quantum-dot-optics/`. The
script exits non-zero only when it fails; the verdict is in `results/comparison.json`.

## Files

| File | What |
| --- | --- |
| `sufficiency.md` | P3 check: what data exist, terms, gaps, scope chosen (before any comparison) |
| `mapping.csv` | every optical file mapped to sample, treatment, conditions and coumarin 102 reference; ambiguities flagged |
| `source.yaml` | pinned dataset (version, archive md5 and sha256, 113 members with sha256), licences, reported results with locators |
| `inputs.yaml` | every analysis input, labelled measured, reconstructed or assumed |
| `tolerances.yaml` | checks, tolerances, pair rule and pass rule; frozen in 75775d98 before the first run |
| `run.py` | single entry point (PEP 723); fetch, verify, process, compare, write results |
| `comparison.md` | run details, result table, verdict, deviations and explanations |
| `extension.md` | hypothetical design extension: treatment time for a blue-pumped conversion layer |
| `results/comparison.json` | every compared quantity, diagnostics, contrasts, quality screen, extension |
| `results/sample_metrics.csv` | per-sample derived metrics, sensitivity variants and confounder flags |
| `results/fig_plqy_time.svg` | computed PLQY against treatment time, with reported values and tolerances |
| `results/fig_quality_screen.svg` | PLQY against emission FWHM by measurement session, base and varied thresholds |
| `results/fig_extension.svg` | retained absorbance, PLQY and batches per m² (hypothetical) |
| `results/NOTICE.md` | attribution of the dataset behind the computed values in `results/` |
| `results/local/` | git-ignored: a plot of the processed spectra for local inspection (CC BY-NC-SA data) |

## Quality screen (deliverable 2)

Base criteria: PLQY ≥ 50 % and band-edge FWHM ≤ 300 meV (the source's typical width). 8 samples
meet them, from five sessions. With the OD window of the Methods (0.05-0.15 at 387 nm) added,
7 remain: F1-200Z drops out at OD 0.047. Tightening the width to 250 meV leaves none. Raising the
PLQY to 70 % leaves only F1-200Z, whose PLQY is the least certain (see comparison.md). Full grid:
`results/comparison.json`, `quality_screen`.

Confounders seen per sample: measurement session (10 PLQY sessions, 2021-02 to 2022-03, plus the sphere
in 2022-10), stock batch (never recorded), OD at excitation outside 0.05-0.15 (14 samples), scatter
offsets in the absorbance (RT aliquots, one InF3 aliquot), trap-dominated emission, reused or
renamed files, and missing treatment conditions (Figure 4B heat-up HF file).

## Evidence gaps

- The authors' baseline, integration range and refractive-index handling are not stated. The
  low-OD 2022 samples (P5, P7) are sensitive to them; the P6 failure is not explained by them
  (comparison.md, item 1).
- Reuse of the derived per-sample values (`results/sample_metrics.csv`) under CC BY 4.0 rests on
  our reading that they are computed facts, not an adaptation of the CC BY-NC-SA dataset
  (`results/NOTICE.md`). ADR 0031 covers raw files only. Owner confirmation is open.
- Measurement solvent for aliquots, aliquot dilution and redispersion volumes are not stated.
- There is no stock-batch identifier and no replicate of any condition.
- The Figure 4B "hot injection in situ HF" files are the washed 150 °C sample, which carries two
  reported values (64 % in the text, 54 % in Figure 4B).
- The 200 °C series mixes two internal names (HF130, HF140). The ZnCl2 file name says 60 min while
  the Methods say 5 min. The 200 °C decay predates its PLQY session.
- There is no reference for the benzoyl-fluoride-only sample (S6). The dose series (S4) has no
  PL files. There is no instrument response for the decays.
- CI does not check this folder (ADR 0030).
