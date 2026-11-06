# 0033. A process's regeneration test runs in its own CI job, marked `engineering`

- **Status:** Accepted, 2026-11-06 (proposed 2026-11-05)
- **Deciders:** the owner (drafted for #330)
- **Scope:** the library's tests and CI (`tests/`, `.github/workflows/validate.yml`, `release.yml`)

## Context

The library's tooling tests run in one job, `library` in `validate.yml` (timeout 15 min), and
again in `release.yml`. They test the library's scripts on fixtures and take about 75 s.

#330 adds the first test that regenerates a whole process design. It copies
`processes/co2-electrolysis-bpm-1` to a temporary directory, runs `cheme run scripts/regen.py`
at 1,000 h and at 10,000 h, and asserts the frozen hand expectations E1 to E9 of
`results/expected.yaml`. Each run drives `cheme process cell`, `duty`, `stack --write`,
`datasheets draft` and `fill`, `process build`, `layout build`, `layout render --png`, the duty
plots and comparisons, `control report` and `validate`. That takes about 230 s on a developer
laptop, and probably two to three times that on a CI runner. It also needs core's `props` extra
(thermo, for the datasheet fill) and its `png` extra (resvg, for the rendered views). The
library job installs only `units`.

Options considered:
- (a) Keep the test in the library job and install `units,props,png` there. The job's 15 min
  would then be at risk, and the catalog and LCI builds after the tests could time out.
- (b) Raise the library job's timeout. Every pull request would wait for the regeneration, even
  one that touches only the LCI pipeline, and the release workflow would carry it too.
- (c) Run the regeneration in its own job with the extras it needs, and keep it out of the
  library and release test runs.
- (d) Skip the regeneration in CI and rely on `cheme check` (gate `skid-regen-current`). That gate
  is informational in the validate job (`continue-on-error`), so a broken regeneration would
  not fail the build.

## Decision

- **A test that regenerates a process design is marked `engineering`** (`pytest.mark.engineering`,
  registered in `tests/conftest.py`). Its fast parts (the committed records against the frozen
  expectations, the frozen-expectations commit before the regeneration commits, no script
  reading `benchmarks/`) stay unmarked and run with the other tests.
- **The `library` job of `validate.yml` and the release workflow deselect it** (`pytest -q tests
  -m "not engineering"`).
- **A job `engineering` in `validate.yml` runs it**: the same pinned core commit as every other
  job (`tests/test_workflows.py`), with the extras `units,props,png`, `ATLAS_REQUIRE_CORE=1` (a
  missing core fails, it does not skip), timeout 40 min, `pytest -q tests -m engineering` with
  the library job's test dependencies (pytest collects every module of `tests/`).
- The first such test is `tests/test_co2_electrolysis_bpm_skids.py` (#330).

## Consequences

- The library job keeps its runtime and its extras; the regeneration fails the build on its own
  job, with its own log.
- Running `pytest -q tests` locally still runs the regeneration when core is installed (about
  4 min); `-m "not engineering"` leaves it out.
- The regeneration's figures need `png` and its datasheet fill `props`; without them the run
  stops on a tool error (`regen.py` exit 1). The test then fails, it does not degrade.
- A second process with a regeneration test adds its test to the same marker; the job's timeout
  may then need raising.

## Evidence

- Accepted by the owner on 2026-11-06.
- On CI the engineering step took about 17.5 min (validate run 42168252735, 2026-11-06, regen
  steps 1 to 25), under the 40 min timeout; the figures above predate steps 20 to 25.
- The tests now also assert E10 (`results/expected-lca.yaml`, the LCA reconciled with the run
  record, `test_regenerated_lca_is_reconciled_e10`); the Context above names E1 to E9, as written.
- `tests/test_co2_electrolysis_bpm_skids.py`, `tests/conftest.py` (the marker),
  `.github/workflows/validate.yml` (jobs `library` and `engineering`),
  `.github/workflows/release.yml`.
- `processes/co2-electrolysis-bpm-1/DESIGN.md` D-022; the runtime is in its PROGRESS.md entry.
- Issue #330 (design spec, section 8: "If the library job's 15 min timeout is at risk, add a
  dedicated job").
