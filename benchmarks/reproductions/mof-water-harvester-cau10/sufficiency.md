# Data sufficiency: CAU-10-H water harvester (#334)

What the reproduction and the design extension need, what exists, and the scope that follows
(ADR 0031). Pins, hashes and licences are in `source.yaml`.

| Needed for | Exists? | Where, licence | Consequence |
| --- | --- | --- | --- |
| Uptake series of CAU-10-H at one temperature | yes, one sample (8, pellets, 313 K) | 4TU.ResearchData 10.4121/22009211 v1, CC BY-SA 4.0 | reproduction and sizing use it; downloaded at run time, not committed |
| Figure 7 descriptors (α, Δp/p0, K_H) for CAU-10-H | as a figure in the article; tabulated in SI Table S7 since 2026-11-04 (next row) | article 10.1002/adma.202210050, CC BY-NC 4.0, TU Delft open copy | digitised by us (`digitise_figure7.py`), ±3 px, ±6 px for covered markers |
| Which Table S7 row is sample 8, and its tabulated descriptors | yes, since 2026-11-04 | Supporting Information Table S7, p. 31, row 8; publisher only (HTTP 403 to scripted requests), obtained by the owner, not committed | second comparison against the authors' values under `tolerances-si.yaml`; row 8 matches marker H5 (`comparison.md`) |
| Definition of total capacity | yes, but not applicable to sample 8 | SI Section 7, p. 30: read at p/p0 0.85 | sample 8 ends at 0.4246; uptake at the highest measured p/p0 still assumed; what the authors used for this series is not stated |
| Definition of K_H (SI Section 7) | yes | as above: linear fit on p/p0 0 to 0.1, K_H = slope R T / p0 | evaluated under `tolerances-si.yaml`; whether the fit has an intercept is not stated |
| Adsorption points between p/p0 0.0836 and 0.1777 | no | not measured in the series | design values in that gap reported with bounds |
| CAU-10-CH3 data | no | the article reproduces its isotherm from a 2013 paper | out of scope |
| Isotherms at a second temperature | no | only 313 K for sample 8 | no isosteric heat; temperature transfers flagged as extrapolations |
| Pellet composition (binder) | no | not stated | uptake per gram of pellet |
| Kinetics, heat of adsorption, air-side data | no | not in the sources | equilibrium lower bound on mass; heat a lower bound |

Searched for an open copy of the Supporting Information (2026-11-04): OpenAlex open-access
locations, Europe PMC (no PMC copy), HAL, KU Leuven Lirias and the TU Delft repository (article
only). None was found. The repository owner then obtained the SI from the publisher
(2026-11-04; sha256 in `source.yaml`); it is used for facts and numbers only and is not
committed.

**Achievable scope.** A reproduction of the two Figure 7 descriptors of one CAU-10-H series
against our digitisation (`tolerances.yaml`), and a comparison of the same series with the
values the authors tabulate for it, Henry constant included (`tolerances-si.yaml`); and a
hypothetical equilibrium sizing at 313 K inside the measured RH range, with interpolation
bounds where the series is sparse. Independent validation is not achievable with these sources:
Table S7 row 8 is computed by the authors from the same series.
