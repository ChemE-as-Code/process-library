# Reverse-bias bipolar-membrane CO2 electrolysis: reference reproduction

Reproduction of the water dissociation efficiency (WDE) measurements and the anolyte pH model of
Prats Vergel, Vermaas, Burdyny et al. (Nature Chemical Engineering 2025) from their 4TU dataset,
for issue #329 (tracker core#136). Protocol: ADR 0030.

This folder is the held-out check. `processes/co2-electrolysis-bpm-1/` is the design case. It may
use the measured R1 series as design data (ADR 0031), and it uses none of the comparison results
here.

| Check | What | Kind |
| --- | --- | --- |
| R1 | WDE vs current density in 1 M KOH, rebuilt from the raw titration sheets, against Fig. 3a | reproduction of a measured series |
| R2 | the authors' unmodified model against their Fig. 5a, 1 L | reproduction of a model trajectory |
| D1 | is the pH stop event of the authors' script volume-dependent? | defect verification |
| V1 | the authors' model, with inputs from separate measurements, against the measured pH of Fig. 3c | validation |

The model output is the time until the anolyte pH falls below 12, the authors' stability
criterion. This reproduction makes no claim about when the Ni anode corrodes.

| File | What |
| --- | --- |
| `source.yaml` | pinned dataset and paper, file-to-figure map, method, reproduction and validation split, raw-data irregularities |
| `tolerances.yaml` | acceptance tolerances, committed alone before the first comparison run |
| `reproduce.py` | the one command: download, verify checksums, rebuild, run, compare |
| `comparison.md` | results, deviations and explanations |
| `reruns/` | run records (inputs, versions, every compared number) |
| `figures/` | plots written by `reproduce.py` from the run (R1, R2/D1, V1) |
| `NOTICE.md` | attribution of the dataset |

Run from a clean environment (needs `uv` and network access to data.4tu.nl):

```sh
uv run --isolated benchmarks/reproductions/vermaas-rbpm-wde/reproduce.py
```

The script caches the downloads in `~/.cache/cheme-as-code/4tu/` and refuses any file whose
sha256 differs from `source.yaml`. It runs the authors' model module from its own extracted
folder in a separate isolated interpreter (`python -I`). The module is used unmodified: the
script imports it from file and calls `MassBalanceAnode.massBalanceTanks` with the inputs in
`source.yaml`. The authors' `Simulative_script.py` is not run, because it saves no results. The
script writes a run record to `reruns/` and prints the comparison table, and it exits non-zero
when a check fails.

**Status (2026-11-04, `comparison.md`):**

- **R1, R2:** FAIL under the frozen rules, both by small margins (detail in `comparison.md`).
- **D1:** confirmed in the script, absent from the published figure.
- **V1:** pass on time to pH 12; the later trajectory is not reproduced.

The script therefore exits 1.
