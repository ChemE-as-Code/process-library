# Data sufficiency: CAU-10-H water harvester (#334)

What the reproduction and the design extension need, what exists, and the scope that follows
(ADR 0031). Pins, hashes and licences are in `source.yaml`.

| Needed for | Exists? | Where, licence | Consequence |
| --- | --- | --- | --- |
| Uptake series of CAU-10-H at one temperature | yes, one sample (8, pellets, 313 K) | 4TU.ResearchData 10.4121/22009211 v1, CC BY-SA 4.0 | reproduction and sizing use it; downloaded at run time, not committed |
| Figure 7 descriptors (α, Δp/p0, K_H) for CAU-10-H | as a figure only | article 10.1002/adma.202210050, CC BY-NC 4.0, TU Delft open copy | digitised by us (`digitise_figure7.py`), ±3 px, ±6 px for covered markers |
| Which Figure 7 marker is sample 8 (Table S7) | no | Supporting Information, publisher only; HTTP 403 to scripted requests | marker inferred by nearest α; α check and identification are one test (`comparison.md`) |
| Definition of total capacity | no | not in the article text; SI not obtained | uptake at the highest measured p/p0 assumed; Δp/p0 is sensitive to it |
| Definition of K_H (SI Section 7) | no | as above | K_H not evaluable; a candidate ratio is reported only |
| Adsorption points between p/p0 0.0836 and 0.1777 | no | not measured in the series | design values in that gap reported with bounds |
| CAU-10-CH3 data | no | the article reproduces its isotherm from a 2013 paper | out of scope |
| Isotherms at a second temperature | no | only 313 K for sample 8 | no isosteric heat; temperature transfers flagged as extrapolations |
| Pellet composition (binder) | no | not stated | uptake per gram of pellet |
| Kinetics, heat of adsorption, air-side data | no | not in the sources | equilibrium lower bound on mass; heat a lower bound |

Searched for an open copy of the Supporting Information (2026-11-04): OpenAlex open-access
locations, Europe PMC (no PMC copy), HAL, KU Leuven Lirias and the TU Delft repository (article
only). None was found.

**Achievable scope.** A reproduction of the two Figure 7 descriptors of one CAU-10-H series
against our digitisation, with the marker identified by α (not by label); and a hypothetical
equilibrium sizing at 313 K inside the measured RH range, with interpolation bounds where the
series is sparse. Independent validation is not achievable with these sources.
