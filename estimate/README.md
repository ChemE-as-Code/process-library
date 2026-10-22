# Estimate

The material take-off of the 3D model and its estimate (skill `mto-estimate`).

| file | what | written by |
|---|---|---|
| `rates.yaml` | the project's unit rates and estimate factors, each with status, source and year (`plantcode schema rates`) | people; the file `plantcode init` writes is an **example** (`example: true`) and prices nothing |
| `mto.csv`, `mto.md` | the take-off of `layout/plant-model.yaml`: pipe by DN, class and insulation, fittings, flanges, valves, steel tonnage, grating, insulation, concrete | `plantcode assess mto --write` |
| `estimate.csv`, `estimate.md` | the take-off priced with `rates.yaml`, then the factors (direct, indirect, contingency) | `plantcode assess estimate --write` |

Never edit `mto.*` or `estimate.*` by hand: rebuild the model (`plantcode layout build`), then
rewrite them. The gate `kind: mto` (`checks/checks.yaml`) checks they are current.
