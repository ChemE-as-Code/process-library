# Notice: third-party data used in this case

This case uses numbers from one openly licensed publication. No file, table, figure or text of it
is committed here.

**Source.** Chengtian Cui, Xiaodong Zhang, Meng Qi and Anton A. Kiss, *Control of fully
electrified heat pump assisted distillation process by flash vapor circulation*, Chemical
Engineering Research and Design 220 (2025) 450-460, doi
[10.1016/j.cherd.2025.07.023](https://doi.org/10.1016/j.cherd.2025.07.023). Published open access
under the Creative Commons Attribution 4.0 International licence
([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)).

**What we use.**

- Facts and numbers from the article (specifications, operating conditions, reported results),
  restated in our own form with locators in `source.yaml`.
- Numbers from the supporting-information workbook (Appendix A, `mmc1.xlsx`). `run.py` downloads
  it at runtime from the publisher, checks its sha256 and reads it as data. It is not committed.
  Its own licence is not stated separately and we could not open the publisher page by script to
  check it, so we treat the workbook as a source of facts, cited, and do not redistribute it.
- The figures in `results/` are drawn by our own matplotlib code. All five replot SI values
  (dashed lines and open markers) beside our model's results: the values are replotted, not
  modified. Each figure carries the citation.
- `results/comparison.json` restates SI end values and recomputed integrals beside ours, as
  numbers with their source.

**What is ours.** The model, its code, the fitted parameters, the tuning, every computed result,
the figures and the control-loop P&ID in `case/` (drawn by cheme from our own script, not traced
from the article's figures). These are published under the library's licences (data and figures
CC BY 4.0, code AGPL-3.0-or-later).

The source's authors have not reviewed or endorsed this reproduction.
