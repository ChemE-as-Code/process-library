# Gas-diffusion-electrode pressure window: reference reproduction

This folder reproduces the flow-by pressure window of seven commercial gas diffusion electrodes,
and the maximum electrode height that follows from it, from Baumgartner, Koopman, Forner-Cuenca
and Vermaas (ACS Sustainable Chem. Eng. 2022). The inputs are the tabulated breakthrough
pressures in the paper's supporting information. Issue #332, tracker core#136. Protocol: ADR 0030
(Proposed), with one deviation: there is no `case/` folder. The model is a plain-Python data
reproduction with no cheme flowsheet, the situation in which ADR 0031 notes that the
HDA layout (`case/` with a `plant.yaml`) does not fit.

The issue is a separate follow-up to the bipolar-membrane benchmark (#329), and its result does
not depend on that benchmark or on the other #136 issues. No process folder uses these results.
The spatial question (does the local differential pressure stay inside the window along a tall
channel with flow?) is scoped, not implemented, in `scoping.md`. That question concerns the cell
interior, not the 3D plant layout.

| Check | What | Kind |
| --- | --- | --- |
| R1 | window dp* = dp_L* − dp_G* per coated GDE, against the sheet and the text | reproduction of tabulated values |
| R2 | the window's propagated spread, against the text's 14 mbar | reproduction |
| R3 | the paper's height conversions (40, 80 and 50 mbar to 41, 81 and 51 cm) | reproduction |
| K1 | the paper's height claims, on the reproduced windows | claim classification |
| K2 | the electrolysis operating differential pressures against the open-circuit window | consistency |

The sign convention is the paper's, dp = p_L − p_G. The width of the window is the same in
either convention.

| File | What |
| --- | --- |
| `source.yaml` | pinned paper and SI files (sha256 per file), definitions, method, cell geometry, file map, published values and claims with locators, split |
| `tolerances.yaml` | acceptance rules and constants, committed alone before the first comparison run |
| `reproduce.py` | the one command: download, verify checksums, rebuild, compare, plot, record |
| `comparison.md` | results, deviations, the hydrostatic-applicability check, verdict |
| `scoping.md` | an optional spatial solver, scoped for one question; not implemented |
| `reruns/` | run records (inputs, versions, every compared number) |
| `figures/` | `pressure-vs-elevation.svg` (SGL 39BC, 1 m electrode) and `h-max-per-gde.svg`, drawn by `reproduce.py` |
| `NOTICE.md` | attribution of the article and its supporting information |

Run from a clean environment (needs `uv` and network access to www.ebi.ac.uk):

```sh
uv run --isolated benchmarks/reproductions/baumgartner-gde-pressure-window/reproduce.py
```

The script caches the download in `~/.cache/cheme-as-code/europepmc/PMC9006256/`. It extracts
only the two pinned members of the zip and refuses any file whose sha256 differs from
`source.yaml`. It writes a run record to `reruns/` and the figures to `figures/`, prints the
comparison, and exits non-zero when R1, R2 or R3 fails.

**Status (2026-11-04, `comparison.md`):**

- **R1:** FAIL under the frozen rule. All 7 GDE windows reproduce exactly. For the uncoated
  SGL 39BC, the spreadsheet carries Sample 2 of SI Table S3 (67 mbar), and the frozen check
  compared it against the table's mean (62 mbar). The two published copies are consistent; this
  is not a data error in the source.
- **R2, R3:** pass. The paper's heights use water density; with the 1 M KHCO3 used in the
  measurements they are about 6 % lower.
- **K1:**
  - the 40 to 80 mbar range is supported;
  - "below 51 cm for every material above 50 % FE_CO" is contradicted for 3 of 5 materials
    (59 to 74 cm), though it lies within the authors' error;
  - H23C6 above 1 m is supported, and above 200 cm only at nominal values.
- **K2:** every 200 mA/cm2 run sat near the gas-breakthrough end of its window, none more than
  one 10 mbar step outside.

The script therefore exits 1.
