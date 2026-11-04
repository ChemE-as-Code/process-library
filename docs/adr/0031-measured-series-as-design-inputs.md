# 0031. A process may use measured series from a pinned dataset; reproduction results stay held out

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
  two must agree on the same inputs, which the benchmark records.
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
