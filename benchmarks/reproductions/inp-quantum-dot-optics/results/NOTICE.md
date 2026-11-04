# Notice: data behind the computed values in this folder

The numbers in `comparison.json`, `details.json` and `sample_metrics.csv`, and the figures
`fig_*.svg`, are computed by `run.py` from the archived measurements of:

R. F. Ubbink, G. Almeida, H. Iziyi, I. du Fossé, R. Verkleij, S. Ganapathy, E. R. H. van Eck,
A. J. Houtepen. Data underlying the article: A Water-free In Situ HF Treatment of InP Quantum
Dots. 4TU.ResearchData, version 1, 2023. doi 10.4121/1370d230-bca3-4af4-af06-1a9f168a4b10.v1.
Licence: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/).

No data file, data row or spectrum of the dataset is included here. The files hold only values
we computed: quantum yields, peak positions and widths, lifetimes, contrasts, and single
absorbance values at stated wavelengths (387, 330 and 450 nm, and the 680-700 nm baseline) that
enter those calculations. The figures plot these computed values, drawn by our own code. Plots
of the spectra themselves go to `local/`, which git ignores; they are a view of the dataset, not
our result.

**Committed, by the owner's decision of 2026-11-04.** `comparison.json` (the checks, the verdict
and aggregates), `details.json` (per-sample values behind the bound checks, diagnostics, contrast
values, quality-screen membership, extension rows), `sample_metrics.csv` (one row per sample) and
the figures, under CC BY 4.0 with the attribution above. The reading behind the decision: the
computed values are facts, which copyright does not protect; CC BY-NC-SA 4.0 attaches its
NonCommercial and ShareAlike terms only to Adapted Material, that is, use that needs the
rightsholder's permission, and values and figures computed by our own code do not; the EU
database right protects investment in obtaining data, not in creating them by measurement.
`sample_metrics.csv` with `../mapping.csv` covers nearly every sample of the dataset, so the
dataset's authors are asked to confirm that it may be published under CC BY 4.0; their answer is
recorded here when it arrives. `../source.yaml` (`reuse_terms`, frozen in 75775d98) describes the
plan to commit per-sample values and figures, which this follows.

The reported numbers compared against come from the article (Chem. Mater. 2022, 34, 10093,
doi 10.1021/acs.chemmater.2c02800, CC BY 4.0) and its supporting information, restated as
facts in `../source.yaml`.
