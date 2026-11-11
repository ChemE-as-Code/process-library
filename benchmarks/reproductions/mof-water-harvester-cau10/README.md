# CAU-10-H water harvester: reproduction and design extension

**Engineering question.** How does inlet humidity affect the adsorbent mass needed to collect a
specified amount of water per cycle?

Issue #334 (P1), scope tracker #333. Protocol: ADR 0030 (reference reproductions, tolerances
frozen first) and ADR 0031 (case studies: a reproduction plus a labelled design extension;
Proposed, merged in #344).

**Answer in one line (hypothetical design, not validated).** For 1 kg of water per cycle at
80 % recovery, a bed of CAU-10-H pellets at 40 °C needs 4.65 kg (7.7 L packed) at inlet RH 0.30
and about 180 kg at RH 0.18 (82 to 242 kg from the measured points either side; 18 to 52 times
the base case). Below RH 0.193 the working capacity is under 10 % of the plateau value and the
design is infeasible; the step runs from RH 0.189 to 0.219, with its inflection at 0.197
(`extension.md`).

## Status

| Item | Status |
| --- | --- |
| Reproduction | Against Figure 7 (`tolerances.yaml`): **pass** (4 of 4 checks): α and Δp/p0(75–25 %) of the 4TU CAU-10-H series against the digitised marker, marker identification, saturation-pressure basis. These checks are not independent: the marker is selected by α, so the α and identification checks are one test; the Δp/p0 tolerance would also admit marker H3; the saturation-pressure check is data integrity, not a reported value. Against Table S7 row 8 of the Supporting Information (`tolerances-si.yaml`): **partial** (3 of 5): sample identity, α (+0.0002) and Δp/p0 (+0.0004) pass, but these α and Δp/p0 checks are not blind; the blind Henry checks fail, slope 8.89 against 6.14 mmol/g (+45 %) and K_H 3159 against 2166 cm3/g (+46 %), with the frozen fit through the origin. A fit with an intercept, reported as a variant, gives 6.138 mmol/g. Our digitised marker H5 agrees with row 8 (`comparison.md`) |
| Independent validation | none (no independent harvester or isotherm data used) |
| Design extension | hypothetical: adsorbent mass, volume and regeneration heat against inlet RH, one changed-input example RH 0.30 → 0.18 (`extension.md`) |
| Specialist review | not yet (optional follow-up: adsorption and cyclic sorption) |

What is reproduced is our reading of the published uptake series. α and Δp/p0 agree with what
the article plots and tabulates for it. The Henry constant does not agree with the frozen
method (`comparison.md`, second part). It is not a validation of the article, and
the sizing is a design calculation built on the series, not a reproduction of anything the
article reports (the article sizes no device).

## Rerun

From the repository root (needs `uv` and network access to data.4tu.nl):

```sh
uv run benchmarks/reproductions/mof-water-harvester-cau10/run.py
```

It downloads the two pinned files into `${XDG_CACHE_HOME:-~/.cache}/cheme-reproductions/mof-water-harvester-cau10/`,
checks their sha256, checks its saturation-pressure code against the IF97 verification values,
and writes `results/comparison.json`, `results/sweep.json` and three SVG figures
(`isotherm_cau10h_313K.svg`, `reproduction_figure7.svg`, `harvester_mass_vs_rh.svg`). Output is
deterministic; the script header pins the direct dependencies and sets `exclude-newer` so the
transitive ones resolve the same way. The script exits non-zero only if it fails (including a
bed temperature more than 0.5 K from the isotherm's, which it does not support); the verdict
is in `comparison.json`.

## Files

| File | What |
| --- | --- |
| `source.yaml` | pinned article and dataset (DOI, version, sha256, licences), sample mapping, reported facts with locators, digitised Figure 7 markers with method and uncertainty |
| `inputs.yaml` | every model input with value, unit, label (measured, reconstructed, assumed) and source or rationale |
| `tolerances.yaml` | acceptance tolerances and pass rule against the digitised Figure 7, frozen in d25eee1 before run.py existed |
| `tolerances-si.yaml` | second comparison, against Table S7 row 8 of the Supporting Information, frozen in ac79bdf6 before any Henry-constant computation |
| `run.py` | single entry point (PEP 723 header, pinned dependencies) |
| `digitise_figure7.py` | our digitiser: re-derives the Figure 7 pixel centres and calibration in `source.yaml` from the pinned PDF (optional; `uv run` it like `run.py`) |
| `results/comparison.json` | every compared quantity under both tolerance files (`reproduction`, `table_s7`), context comparisons, scalar design-extension results with interpolation bounds, and a `data_source` attribution block |
| `results/sweep.json`, `results/*.svg` | full RH sweep and figures (headline: `results/harvester_mass_vs_rh.svg`) |
| `comparison.md` | run details, result table, verdict, deviations, corrections after the freeze |
| `extension.md` | the hypothetical design extension and its flags |
| `sufficiency.md` | what the sources provide, what is missing, and the achievable scope |
| `NOTICE.md` | attribution and licence of the dataset, article and Supporting Information behind the committed numbers |

## Sources and reuse

- Article: van der Veen et al., Adv. Mater. 2023, 10.1002/adma.202210050, CC BY-NC 4.0. Facts and
  numbers only, restated with locators; nothing copied.
- Supporting Information of the article: obtained by the repository owner on 2026-11-04 (the
  publisher refuses scripted requests), not committed; only the Section 7 definitions and the
  Table S7 row 8 numbers are restated, with locators and the file's sha256 (`source.yaml`).
- Data: 4TU.ResearchData 10.4121/22009211 v1 (Rega, de Lange, Wang, Grancha, van der Veen),
  CC BY-SA 4.0. The data file is not committed; it is downloaded at run time.
- **Derived results:** the figures, the 149-point RH sweep and `comparison.json` are computed from
  the data by our own code and published under CC BY 4.0 by the owner's decision of 2026-11-04;
  the reasoning and the attribution are in `NOTICE.md`.
- **Labels.** `inputs.yaml` uses a fourth label, "reference property" (IUPAC molar mass, IAPWS
  water properties), beside ADR 0031's measured, reconstructed and assumed, because those
  values are neither the source's data nor our choice.

## Evidence gaps

`sufficiency.md` is the sufficiency record (ADR 0031); in short:

1. **Supporting Information: obtained late, not open.** Wiley returns HTTP 403 to scripted
   requests and no open copy was found. The owner obtained the SI on 2026-11-04. Table S7 row 8
   now labels sample 8, which matches marker H5, and Section 7 defines K_H. Not stated in the
   SI: whether the Henry fit has an intercept, which R2 is given, and the p0 basis (the row
   implies 7377 Pa, 0.7 % above IF97 at 313.000 K). For this series the intercept alone
   changes the slope by 45 %.
2. **Capacity definition not applicable to this series.** The SI reads total capacity at p/p0
   0.85, and sample 8 ends at 0.4246. With our choice (the uptake at 0.4246), α and Δp/p0
   agree with row 8 within 0.0002 and 0.0004 (not a blind check); this is consistent with, but
   does not show, the same choice by the authors. Row 8 gives 0.92 in a column headed g/g; our
   uptake at p/p0 0.4246 is 0.2973 g/g (16.504 mmol/g). What the 0.92 represents for a series
   ending below 0.85 is an open question to the authors (`comparison.md`). Δp/p0(75–25 %) is sensitive to the capacity: a
   capacity 10 % above ours would give 0.0110 (`comparison.md`, item 1).
3. **CAU-10-CH3 not available as data.** The dataset holds CAU-10-H only; CAU-10-CH3 is out of
   scope.
4. **One isotherm temperature (313 K).** No isosteric heat can be fitted; the regeneration
   temperature (85 °C) and the adsorption enthalpy (47.6 kJ/mol) rest on the Dubinin-Polanyi
   characteristic curve and are flagged as extrapolations.
5. **Pellet composition unknown.** Uptake is per gram of pellet; the plateau is 13 % below the
   article's powder value.
6. **Sparse adsorption branch below the step.** No point was measured between p/p0 0.0836 and
   0.1777, and the uptake rises 48 % between 0.1777 and 0.1903. Design values there carry
   bounds from the measured points either side (`extension.md`).
7. **No kinetics, no heat of adsorption removal, no air-side design.** The mass is an
   equilibrium lower bound; cycle time is an assumption that only scales daily yield.
8. **Packed density, heat capacity and recovery are assumed** (no source); their effect is
   shown in `extension.md`.
