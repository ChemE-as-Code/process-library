# Notice: third-party data used in this case

**Source.** Robin K. A. van Schendel, Wenjun Yang, Evgeny A. Uslamin, Evgeny A. Pidko,
"Utilizing Design of Experiments Approach to Assess Kinetic Parameters for a Mn Homogeneous
Hydrogenation Catalyst", *ChemCatChem* 2021, 13(23), 4886-4896,
doi:10.1002/cctc.202101140, and its Supporting Information (`CCTC-13-4886-s001.pdf`).

**Licence.** The article is published open access under the Creative Commons Attribution 4.0
International licence (CC BY 4.0, https://creativecommons.org/licenses/by/4.0/). The SI file is
part of the same PMC open-access record (PMC9291086.1, licence code "CC BY") but carries no
licence line of its own. We treat the numbers taken from it as facts with attribution.

**What is restated here, in our own form.**

- `source.yaml`: the design factors and levels, the model forms and outlier lists, the
  reported statistics (RMSE, R2, PRESS, pure-error mean square) and the estimate and standard
  error of every coefficient of models I to IV (SI Tables S3, S7, S13, S20; article Tables 2
  and 3), and the reported activation energies and reaction orders (article Figure 7 and
  text). Restated as data with locators; no table layout, text or figure is copied.
- `comparison.md`: the same reported numbers, set against our refits.

**What is read at runtime and not redistributed.** The SI file itself, including the run table
(SI Tables S1, S2), the fitted-value tables (S6, S10, S16, S21) and the initial-rate points
(S23-S26). `run.py` downloads it from the pinned URL and checks its sha256.

**What is redrawn.** All figures in `results/` are drawn by `run.py` with our own matplotlib
code from these numbers and our refits:

- `fig1_parity.svg`: measured y from SI Tables S1/S2 and SI fitted values (S10, S16, S21)
  against our refits.
- `fig2_discrimination.svg`: design-run levels from SI Tables S1/S2; all curves are our
  refitted models.
- `fig3_conventional_kinetics.svg`: initial-rate points from SI Tables S23-S26 with our
  straight-line fits.

Each figure carries a one-line data credit. Changes made: data refitted and replotted by us;
nothing in the figures is traced from the article.
