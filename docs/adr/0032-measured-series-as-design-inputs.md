# 0032. A process may use measured series from a pinned dataset; reproduction results stay held out

- **Status:** Proposed, 2026-11-04
- **Deciders:** the owner (to accept); drafted for #329
- **Scope:** library structure (benchmarks and process folders), evaluation protocol; extends ADR 0030

## Context

ADR 0030 keeps reference reproductions in `benchmarks/reproductions/<id>/`. Their expected
results are held out from the design jobs that work in `processes/<id>/`, and a reproduction
result "is never used as design data in a process folder". That fits a model reproduction, such
as the IDAES HDA tutorial, where the design is independent of the reference.

The CO2 electrolysis case (#329, tracker core#136) is different. Its design is meant to rest on
the measured experiment that is also reproduced:
- the water dissociation efficiency series of a published bipolar-membrane cell, rebuilt from
  the dataset's raw titration sheets;
- the later pilot-skid sizing of #330, which needs that series as its cell performance.

ADR 0031 (case studies, #333) covers a reproduction plus a labelled hypothetical design
extension inside the benchmark folder, and repeats that a case's results are not design data.
This case needs more than an extension in the benchmark: a full process folder (skids, P&IDs,
layout, LCA in #330 and #331) whose cell performance is the measured experiment itself.

Issue #329 asked for both the reproduction and the design case in
`processes/co2-electrolysis-bpm-1`. Options considered:

- (a) Everything in the process folder. The held-out comparison would then sit where design
  jobs read.
- (b) Everything in `benchmarks/reproductions/`. The design would have no measured data of its
  own, or would read the held-out folder.
- (c) A split. The comparison stays in the benchmark, and the process folder computes its own
  measured series from the same pinned raw data.

## Decision

- **Measured data may be design inputs.** A process folder may hold measured series computed
  from a pinned, openly licensed dataset as design data. The dataset is pinned by DOI, version
  and sha256 of the files used, and its attribution is in the folder's `NOTICE.md`.
- **The series is computed in the process folder**, by a script there, from the raw data, with
  `provenance: calculated`. The script states its method in `DESIGN.md`. It does not read
  `benchmarks/`, and it does not copy the published result values the reproduction compares
  against.
- **The comparison stays in the benchmark.** `benchmarks/reproductions/<id>/` keeps the
  comparison with the published results, any validation against held-back conditions, and the
  model reproductions, under ADR 0030 (tolerances frozen first). These results are not design
  data, as before.
- **Agreement is not validation of the design.** A process that uses such a series may cite the
  reproduction's existence. It does not cite the reproduction's agreement as validation of the
  design, because the design and the reproduction share their raw inputs.
- **The reproduction declares the split** in its `source.yaml` (`split.design_inputs`): which
  series may be design inputs, and which results may not.

## Consequences

- Experiment-grounded processes can be designed from measured data without breaking the
  held-out protocol.
- Raw-data parsing exists twice: in the benchmark's `reproduce.py` and in the process folder's
  adapter. The duplication is deliberate, so the design never imports the held-out folder. The
  two must agree on the same inputs. `reproduce.py` compares its R1 rebuild with the process
  folder's data file and writes the result to each run record (`design_data_consistency`;
  consistent in `reruns/2026-11-04-run-3.json`). The check runs on the benchmark side, so the
  design still never reads `benchmarks/`. It is reported, not a frozen check, and CI does not
  run it.
- The vermaas-rbpm-wde reproduction has no `case/` (ADR 0030 lists one). Its reference is the
  authors' Python model and titration sheets, which no cheme backend represents, so it is
  script-based (`reproduce.py`, `reruns/`, `figures/`). Its README records the deviation.
- Compatible with ADR 0031: what crosses into the process folder is the measured series
  computed from raw data, never a reproduction or extension result. The vermaas-rbpm-wde folder
  predates ADR 0031 and keeps its own layout (`reproduce.py` instead of `run.py`, `reruns/`
  instead of `results/`, cache in `~/.cache/cheme-as-code/4tu/`).
- No checker enforces that a process script does not read `benchmarks/`. A follow-up could add
  a test.
- Issue #329's folder name is kept for the design case. The reproduction lives in
  `benchmarks/reproductions/vermaas-rbpm-wde/`.

## Evidence

- `benchmarks/reproductions/vermaas-rbpm-wde/`: `source.yaml` `split`, tolerances frozen in
  30d35b7.
- `processes/co2-electrolysis-bpm-1/`: `scripts/adapt_4tu.py`, `data/measured/wde-1m-koh.yaml`,
  `DESIGN.md` D-002.
- Issue #329, tracker core#136.
