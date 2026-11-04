# Notice: third-party material behind this case

No third-party file is committed in this folder. `results/comparison.json`
holds scalar numbers derived by `run.py` from the dataset below: isotherm descriptors, working
capacities, adsorbent masses and heats at eight stated design points, and their bounds. It
carries the same attribution in its `data_source` block. Its `table_s7` section also restates
the numbers of Table S7 row 8 that it compares with (Supporting Information, below).

**Dataset.** Rega, de Lange, Wang, Grancha, van der Veen, "Previously unpublished water
adsorption isotherm data related to the publication: Confined water cluster formation in water
harvesting by metal organic frameworks: CAU-10-H versus CAU-10-CH₃", 4TU.ResearchData,
version 1, 2023, doi:10.4121/22009211.v1. Licence: CC BY-SA 4.0
(https://creativecommons.org/licenses/by-sa/4.0/). File used: `8 - CAU-10-H.csv`. Changes:
interpolated and transformed by `run.py`; the file itself is downloaded at run time and not
redistributed.

**Article.** van der Veen et al., Adv. Mater. 2023, 2210050, doi:10.1002/adma.202210050,
CC BY-NC 4.0. Facts and numbers only, restated with locators in `source.yaml`; Figure 7 marker
positions digitised by our own code. Nothing of the article is reproduced.

**Supporting Information of the article.** `adma202210050-sup-0001-SuppMat.pdf` (37 pages,
sha256 e906a0672c76ed9b03c9ac6d7c7ecd83c6cb7a81b31ddb71e581657b2fe7b59b), from the publisher
only. It states no licence of its own. The repository owner obtained it on 2026-11-04. It is
not committed or redistributed here. Used as facts and numbers only: the definitions of
Section 7 (p. 30) and the values of Table S7 row 8 (p. 31), restated in our own form with
locators in `source.yaml` and `tolerances-si.yaml`. No table, figure or text of it is
reproduced. The second SI file (a zip of crystal structures) was not used.

**Committed, by the owner's decision of 2026-11-04.** The SVG figures and `results/sweep.json`
(the RH sweep resampled at 149 points from the isotherm) are computed by `run.py` and committed
under CC BY 4.0, with the attribution above. The reading behind the decision: the measured
uptakes are facts, which copyright does not protect; CC BY-SA 4.0 attaches its ShareAlike term
only to Adapted Material, that is, use that needs the rightsholder's permission, and a model
calculation or a figure drawn by our own code from the numbers does not; the EU database right
protects investment in obtaining data, not in creating them by measurement. The dataset's authors
are asked to confirm; their answer is recorded here when it arrives. `source.yaml`
(frozen in d25eee1d) describes the earlier plan to hold the figures back; this notice states what is
committed now.
