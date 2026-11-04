# Notice

This reproduction uses, without redistributing them, the article

> L. M. Baumgartner, C. I. Koopman, A. Forner-Cuenca, D. A. Vermaas, "Narrow Pressure Stability
> Window of Gas Diffusion Electrodes Limits the Scale-Up of CO2 Electrolyzers", ACS Sustainable
> Chemistry & Engineering 10 (14), 4683-4693 (2022), https://doi.org/10.1021/acssuschemeng.2c00195

published under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), and its supporting
information, `sc2c00195_si_001.pdf` and `sc2c00195_si_002.xlsx`. The supporting-information
files state no licence of their own. They are distributed with the article in the Europe PMC
open-access package, whose record for PMC9006256 gives the licence as CC BY (checked
2026-11-04).

`reproduce.py` downloads the supporting information at run time from Europe PMC (PMC9006256).
This folder holds:

- the files' checksums;
- facts and numbers taken from the article and the supporting information, in our own form and
  with locators. These include every value of the spreadsheet's breakthrough-pressure sheet
  (`deltaP`) and the averaged values of the electrolysis runs used here (sheet `FE`), re-keyed
  as measured values per material in `source.yaml`, the run records in `reruns/` and the tables
  of `comparison.md`;
- numbers derived from them.

It contains none of the source's files, figures, drawings or text, and no copy of a source
table's layout or formatting. The figures in `figures/` are drawn by `reproduce.py` from those
numbers.
