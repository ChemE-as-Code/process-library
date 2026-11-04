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

**Deviation from the ADR 0030 layout.** ADR 0030 lists a minimal cheme case (`case/`) among the
files of a reproduction folder. This folder has none. The reference here is not a flowsheet that
a cheme backend can represent: it is the authors' own Python model module and their titration
sheets. So the reproduction is script-based: the pinned `reproduce.py` runs the unmodified
module and the paper's titration equations, and `reruns/` and `figures/` hold what it writes.
The other ADR 0030 rules apply unchanged (pinned source, tolerances frozen first, comparison
with deviations).

Run from a clean environment (needs `uv` and network access to data.4tu.nl):

```sh
uv run --isolated benchmarks/reproductions/vermaas-rbpm-wde/reproduce.py
```

The script caches the downloads in `~/.cache/cheme-as-code/4tu/` (`--cache DIR` for another
place). A download goes to a `.part` file and is renamed into the cache only after its sha256
matches `source.yaml`; a cached file that does not match is downloaded again. Each run extracts
the verified zips into a new temporary folder, so nothing extracted earlier is reused. The
authors' model module runs from that folder in a separate isolated interpreter (`python -I`).
The module is used unmodified: the script imports it from file and calls
`MassBalanceAnode.massBalanceTanks` with the inputs in `source.yaml`. A thin wrapper around
`scipy.integrate.solve_ivp`, inside that interpreter only, keeps the solver's event time and
state, which the authors' result dictionary drops. The authors' `Simulative_script.py` is not
run, because it saves no results.

The script prints the comparison table and exits non-zero when a check fails. It writes a run
record to `reruns/` (never overwriting one) and the plots to `figures/`. The record names the
commit, whether the folder had uncommitted changes before the run wrote anything, the sha256 of
`reproduce.py`, `source.yaml` and `tolerances.yaml`, whether `tolerances.yaml` still equals its
frozen version, and whether each input was downloaded or taken from the cache. With uncommitted
changes it writes no record unless `--allow-dirty` is given (the record is then marked
provisional); `--no-record` writes nothing to the folder. It also compares its R1 rebuild with
the design case's own series (`processes/co2-electrolysis-bpm-1/data/measured/wde-1m-koh.yaml`),
as ADR 0031 requires the two parsers to agree; that comparison is reported, not a frozen check.

**Status (2026-11-04, run of record `reruns/2026-11-04-run-3.json`, detail in `comparison.md`):**

- **R1:** FAIL under the frozen rule. 5 of 6 current densities pass; 200 mA/cm2 misses its limit
  by 0.00006 with the pooled aggregation.
- **R2:** FAIL under the frozen rule. 11 of 21 rows pass: 10 within the tolerance, plus WDE
  0.999 by the censored rule. The 20 uncensored rows are within 0.77 % at the solver's event
  time, small in relative terms. The 10 failing rows miss the absolute limit by up to 3.0 times.
- **D1:** confirmed in the script (on the event state, with the event-location error below the
  band), absent from the published figure.
- **V1:** pass on time to pH 12; the later trajectory is not reproduced.

The script therefore exits 1.
