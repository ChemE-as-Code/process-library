# Liquid-infused membrane for oil-in-water emulsions: selective operating window

**Engineering question:** at what transmembrane pressures can the dispersed oil of an
oil-in-water emulsion permeate selectively through a liquid-infused membrane?

Issue #340 (P3, data sufficiency first), scope-expansion tracker #333. Protocol: ADR 0030.
Folder layout: a reproduction plus a labelled design extension (ADR 0031).

Source: Bazyar, van de Beek and Lammertink, Langmuir 35 (2019) 9513-9520,
doi:10.1021/acs.langmuir.9b01055 (open access, CC BY-NC-ND; PMC6750837.1 with SI). The case
is pressure-controlled dead-end filtration in a 25 mm cell. The membrane is PVDF (mean pore
radius 1.78 um, 134 um thick), either dry or infused with Krytox GPL 101 (K101). The feed is
5 wt% hexadecane in water with SDS or CTAB at 10 or 50 % of the cmc, at TMP up to 0.1 bar. The
observed permeating phase is oil only at 10 % cmc, and oil with some water at 50 % cmc.

## Status

| Item | Status |
| --- | --- |
| Reproduction | **pass** under the frozen rule: 28 of 28 checks. Covers 8 IFTs, 10 digitised and 5 stated entry pressures, the emulsion-run permeability and 3 LLD active-pore fractions (`comparison.md`) |
| Model against the source's own observations | 5 of 8 Table 3 cases classified correctly at 0.1 bar. Water through the K101-infused membrane at 50 % cmc is not explained. Reported, not in the pass rule; same source, so not independent |
| Independent validation | none (no independent data) |
| Design extension | hypothetical (`extension.md`): pore radius halved |
| Specialist review | not yet (optional follow-up: membrane separation and interfacial transport) |

## Result in brief

- The threshold (Young-Laplace) model with the source's fits reproduces its entry pressures to
  within 0.016 bar. Oil enters the K101-infused membrane at 0.08 bar (measured; 0.096 bar
  model). Water enters at 0.39 bar (SDS 10) down to 0.15 bar (CTAB 50) under a hexadecane layer.
  The dry membrane passes oil at any TMP, and water from 0.29 bar (SDS 10) down to 0.046 bar
  (CTAB 50).
- Selective operation is supported by both model and observation for the 10 % cmc emulsions
  at TMP up to 0.1 bar. At 50 % cmc water leaked through both membranes. For the K101-infused
  membrane this happened even though 0.1 bar is below the model's water entry pressure. The
  model window is an upper estimate there.
- Area, for the one case with flux data (K101-infused, SDS 10, 0.1 bar): 4.7 m2 per m3/h of
  feed. This is a batch, supply-limited figure; the open pores could pass 51 times more oil.
- Hypothetical: halving the pore radius doubles the window (0.20 to 0.43 bar tolerable TMP
  variation) and halves the permeation capacity. It cannot change selectivity, because the
  water/oil entry ratio stays 4.1.
- Crossflow module sizing is not achievable from these data. `extension.md` lists the eight
  missing pieces of information.

## Rerun

From the repository root (needs uv; fetches the article XML once into
`~/.cache/cheme-reproductions/liquid-infused-membrane-emulsion/`; offline, the source check is
recorded as skipped):

```sh
uv run benchmarks/reproductions/liquid-infused-membrane-emulsion/run.py
```

## Files

| File | What |
| --- | --- |
| `sufficiency.md` | what data exist, where, under what terms, what is missing, and the scope decided from it |
| `source.yaml` | pinned source (DOI, PMC version, sha256 of XML, SI and figure image), reuse terms, reported results restated with locators, digitised Figure 4b points with method and uncertainty |
| `inputs.yaml` | every model input with value, unit, label (measured, reconstructed, assumed) and source or rationale |
| `tolerances.yaml` | acceptance tolerances and pass rule, frozen in c9b0de3 before the first run |
| `run.py` | single entry point (PEP 723); checks, sweep, area estimate, extension, figures |
| `results/comparison.json` | every compared quantity, the verdict, informational results, sweep summary, area, extension |
| `results/sweep.csv` | state (none, selective, breakthrough) of each case against TMP, 1 mbar steps |
| `results/entry_pressure_vs_concentration.svg` | entry pressure against surfactant concentration, model and digitised measurements |
| `results/operating_window.svg` | selective window against TMP for the 8 cases, with observed water fractions |
| `results/extension_pore_radius.svg` | hypothetical: window against pore radius |
| `comparison.md` | run details, result table, verdict, deviations |
| `extension.md` | operating window, area estimate, hypothetical extension, crossflow information needs |

## Evidence gaps

- No raw data are published. The 10 Figure 4b points were digitised by us from a
  400 x 174 px image (0.015 bar uncertainty).
- The TMP of each emulsion run is stated only as at most 0.1 bar.
- There is one flux record (SDS 10, K101-infused). There is no flux-pressure curve and no
  water flux after breakthrough.
- The fit parameters come without covariance, so the uncertainty bands are box bounds and
  wider than the true fit uncertainty.
- The fitted curvature radii come from the same LEP data they are compared with. The entry
  pressure checks test our implementation, not the physics.
- The article PDF could not be fetched by script (bot check). The XML full text was used
  instead.
