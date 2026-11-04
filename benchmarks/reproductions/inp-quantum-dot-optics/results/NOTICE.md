# Notice: data behind the computed values in this folder

The numbers in `comparison.json` and `sample_metrics.csv`, and the figures `fig_*.svg`, are
computed by `run.py` from the archived measurements of:

R. F. Ubbink, G. Almeida, H. Iziyi, I. du Fossé, R. Verkleij, S. Ganapathy, E. R. H. van Eck,
A. J. Houtepen. Data underlying the article: A Water-free In Situ HF Treatment of InP Quantum
Dots. 4TU.ResearchData, version 1, 2023. doi 10.4121/1370d230-bca3-4af4-af06-1a9f168a4b10.v1.
Licence: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/).

No data file, data row or spectrum of the dataset is included here. The files hold only values
we computed: quantum yields, peak positions and widths, lifetimes, contrasts, and single
absorbance values at stated wavelengths (387, 330 and 450 nm, and the 680-700 nm baseline) that
enter those calculations. The figures plot these computed values, drawn by our own code. Plots
of the spectra themselves go to `local/`, which git ignores.

We read these computed values as facts with attribution, not as an adaptation of the dataset,
and publish them with the library under CC BY 4.0. This reading is ours. The licence also
covers database rights, and ADR 0031 covers raw files only. Owner confirmation that such
derived values may be published under CC BY 4.0 is open (README.md, Evidence gaps). If it is
not given, `sample_metrics.csv` should be reduced to derived results or removed.

The reported numbers compared against come from the article (Chem. Mater. 2022, 34, 10093,
doi 10.1021/acs.chemmater.2c02800, CC BY 4.0) and its supporting information, restated as
facts in `../source.yaml`.
