# Microfluidic T-junction: droplet size from junction geometry

Case study for issue #338 (scope tracker #333), laid out as a reproduction plus a labelled
design extension (ADR 0030, ADR 0031).

**Engineering question:** which channel dimensions and flow-rate ratios give a target droplet
size in the operating regime of the model?

**Model:** the closed-form, fit-free squeezing-regime model of van Steijn, Kleijn and Kreutzer,
Lab Chip 10, 2513 (2010), doi:10.1039/C002625E. The droplet volume is a filling volume plus a
squeezing term linear in q_d/q_c. Both terms are set by w_in/w, h/w and the corner roundness.

| Part | Status |
| --- | --- |
| Reproduction | **partial** under the frozen rule (13 of 15 checks). The model is reproduced: implementation, two independently evaluated squeezing coefficients, and the intercepts and slopes of the published model lines all pass. Agreement with the experiments is reproduced for two of three junction shapes (mean deviation 10 % and 8 %). The shallowest shape (h/w = 0.11) fails: its mean deviation is 25 %, driven by three points below q = 1. |
| Independent validation | none. The experimental points come from the model's own paper. The VOF points of Nekouei and Vanapalli are reported as informational only. |
| Design extension | HYPOTHETICAL (`extension.md`): the model inverted for 0.5 nL and 2.0 nL, a forward check of every design, a changed-input example, four flagged out-of-regime requests, and dimensioned drawings |
| Specialist review | not yet (an optional follow-up with a microfluidics and multiphase-flow specialist) |

Rerun from the repository root (needs `uv`; the reference PDF is downloaded into
`~/.cache/cheme-reproductions/microfluidic-t-junction/`, or under `$XDG_CACHE_HOME`, and its
sha256 is checked):

```sh
uv run benchmarks/reproductions/microfluidic-t-junction/run.py
```

| File | What |
| --- | --- |
| `source.yaml` | pinned sources, availability and reuse terms, the model as restated, the reference figure, and digitised values with method and uncertainty |
| `inputs.yaml` | every input with value, unit, label (measured, reconstructed or assumed) and source or rationale |
| `tolerances.yaml` | acceptance tolerances and pass rule, frozen in `d3c48e12` before the first comparison run |
| `run.py` | single entry point: download and verification, vector extraction of the reference figure, checks, design inversion, figures and drawings |
| `comparison.md` | run details, reference vs ours, verdict, deviations and explanations |
| `extension.md` | the HYPOTHETICAL design extension and its engineering consequence |
| `results/comparison.json` | every compared quantity, the verdict, and the extension results |
| `results/fig_reproduction.svg` | dimensionless volume vs flow-rate ratio: model, the published model lines, experiments, VOF |
| `results/fig_design_map.svg` | required q_d/q_c vs channel width for each inlet ratio, for both target volumes |
| `results/drawing_D1.svg`, `results/drawing_D2.svg` | dimensioned plan views with section A-A of the two chosen junctions |

## Sources and reuse

- **van Steijn 2010** is closed access and was not read. Its authorship and its abstract's
  claims were checked through OpenAlex and PubMed.
- **The equations** are taken from an open replication by Schackart and Kaarj (GitHub, MIT
  licence, commit pinned). They are restated as facts in `source.yaml` and implemented
  independently in `run.py`.
- **The reference figure** is the replot of three of the original's six Fig. 3 series in
  Nekouei and Vanapalli (arXiv:1703.00937v1, arXiv non-exclusive licence). Its marker and line
  coordinates are read from the PDF's vector paths at runtime. Neither the PDF nor its figure
  is redistributed.
- **Korczyk et al. 2019** (Nat. Commun., CC BY 4.0) supplies the leaking-regime bound and the
  measured fluid properties of the design extension.

All figures and drawings are made by our own code.

## Model assumptions

- Squeezing regime (low Ca), with a non-wetting dispersed phase.
- All channels have the same depth.
- A fixed 10 % of the continuous phase bypasses the forming droplet through the corners.
- Corner roundness is 0.1 w for the gas-bubble series and 0.01 w for liquid droplets.
- No viscosity-ratio term.
- Validated ranges (from the original's experiments): h/w from 0.11 to 0.48, w_in/w from 0.33
  to 3, q_d/q_c from 0.1 to 10, and Ca below 0.01.

## Evidence gaps

- The equations could not be checked against the original text. They are checked only for
  internal consistency and against two squeezing coefficients evaluated by a third party.
- Only three of the six series of the original Fig. 3 are available, through a third-party
  replot whose fidelity is not stated. The liquid-droplet series is missing, so the
  liquid-liquid branch (corner roundness 0.01 w) used by the design extension is not
  reproduced here.
- The failure at h/w = 0.11 and q < 1 cannot be attributed with the open sources: it may be
  physics (more gutter bypass in shallow junctions) or a replot artefact.
- No independent experimental data were found. Korczyk et al. 2019 provide data only on
  request.
- The leaking-regime bound was fitted for square channels and is applied to shallow channels
  as an indication only.
