# Spray-drying stickiness: maltodextrin droplet drying against dryer residence time

Case study for issue #337 (scope tracker #333). Protocol: ADR 0030 (reference reproductions,
tolerances frozen first). Case layout: ADR 0031 (a reproduction plus a labelled design extension).

**Engineering question.** How does a change in feed solids or inlet humidity alter a droplet's
drying trajectory, relative to the residence time a spray dryer gives it? When is the particle
surface potentially sticky?

**What is here.** We built a receding-interface, radial-diffusion model of an MD12 (maltodextrin
DE 12) droplet. Its properties are those stated in the thesis, with Gordon-Taylor Tg at the
surface and GAB water activity. We compared it with two references:

- **A:** the measured drying of one sessile MD12 droplet, from optical coherence tomography
  (Sewalt et al. 2022, CC BY 4.0).
- **B:** the modelled time to a glassy surface of the thesis model (Sewalt 2024, Table 5.1).

We then ran the same model in a hypothetical pilot spray dryer, changed the inlet humidity and the
feed solids, and overlaid a bounded residence-time window.

## Status

| Item | Status |
| --- | --- |
| Reproduction | **FAIL** under the frozen rule: 8 of 12 scored checks pass. A, measured trajectory: initial d² rate (-9 %) and locking time (+12 %) pass; locked radius (-20 %) fails. B, thesis model: the solids trend passes (ratio 0.237 against 0.221) and 1 of 5 times passes; t_glass is 22-36 % early. Internal checks 3 of 3 pass. See `comparison.md` |
| Independent validation | None. No data independent of the two sources exist for this case |
| Design extension | Hypothetical, not validated (`extension.md`). Feed solids 20 to 40 wt% halves the time to a glassy surface. Inlet humidity 5 to 25 g/kg lengthens it by about 30 % but leaves the dried powder 19-26 K below Tg at the outlet. Coarse 150 µm droplets stay sticky into the 0.6-1.9 s core-pass window |
| Specialist review | Not yet (optional follow-up: a spray-drying and particle-technology specialist) |

## Rerun

From the repository root:

```sh
uv run benchmarks/reproductions/spray-drying-stickiness/run.py
```

The run takes about 15 s. It needs uv only; the dependencies are pinned in the script header.
No dataset exists to download, so the script reads nothing but the three YAML files here. It
writes `results/` deterministically and exits non-zero only if it fails to run; the verdict is
in `results/comparison.json`.

## Files

| File | What |
| --- | --- |
| `source.yaml` | pinned sources (DOIs, repository file URLs with sha256, licences and reuse terms), measurement geometry and conditions, reported results restated as facts with locators |
| `inputs.yaml` | every model input with value, unit, label (measured / reconstructed / assumed) and source or rationale |
| `tolerances.yaml` | acceptance tolerances and the pass rule, frozen in 0f6f7b49 before any run |
| `run.py` | single entry point: model, comparison, extension, figures |
| `results/comparison.json` | every compared quantity, the informational comparisons, post-hoc diagnostics and the verdict |
| `results/extension.json` | dryer balance, residence window, sweep results, equilibrium powder state |
| `results/fig1_oct_trajectory.svg` | case A: model against the measured initial rate, locking time and locked radius; surface and centre concentration |
| `results/fig2_thesis_tglass.svg` | case B: parity plot of t_glass against the thesis model |
| `results/fig3_dryer_stickiness.svg` | extension: surface T - Tg against drying time for both changed inputs and both droplet sizes, with the sticky band and the residence-time window |
| `comparison.md` | run details, result table, deviations and explanations |
| `extension.md` | hypothetical design extension, consequences, extrapolation flags, dryer measurements needed |

## Sources and reuse

- Sewalt, Kalkman, van Ommen, Meesters, van Steijn (2022), Food Research International 157,
  111049, doi:10.1016/j.foodres.2022.111049. CC BY 4.0. We use stated facts and numbers only.
- Sewalt (2024), doctoral thesis, TU Delft, doi:10.4233/uuid:8204cf4d-a5fd-4e20-956c-37aba9bf3dd7.
  No licence is given, and the repository allows personal use only. We restate a selection of
  numbers and model equations as facts, with locators. No text, figure or table is copied, and
  every figure here is drawn by `run.py`.

## Evidence gaps

- **No open data.** Neither source deposits data. The measured trajectory exists as numbers only
  in the paper's text: initial rate, regime times and locked radius. The full d(t) curve is in a
  figure, and we did not digitise it.
- **Time origin.** The OCT time origin is ambiguous by about 9 s.
- **Thesis model readings.** Four parameters are read from garbled print in the thesis model
  (D0, χ, the SMT viscosity units, the sign of the viscosity blend), and the gas velocity of the
  reference case is not stated (reconstructed from the reference's t_full). The 22-36 % bias
  against the thesis model is not explained by any single reading, and the reference's numerics
  and its underlying MSc thesis (Presili 2020) were not available.
- **Falling-droplet-column rows.** These rows of thesis Table 5.1 cannot be reproduced: the
  diameters used are not stated.
- **Locking is not the surface glass transition.** The sessile droplet locks into a viscous,
  non-glassy skin (diagnostic in `comparison.md`). A shell-strength criterion would be needed to
  predict locking; no source gives one for MD12.
- **No (T - Tg)c for MD12.** The stickiness band of the extension is assumed. The thesis late
  bound (4 × t_glass) comes from DE 5-21 collisions at 85-125 °C.
- **No dryer-scale data.** The extension cannot be validated, and wall deposition cannot be
  inferred. `extension.md` lists the measurements needed.
- **Python version.** uv selected Python 3.13.16 within `>=3.12,<3.14`.
- **No equivalent in cheme core.** Core has no single-droplet drying model and no spray-dryer
  unit (with residence time and outlet humidity). This case implements both locally in `run.py`.
