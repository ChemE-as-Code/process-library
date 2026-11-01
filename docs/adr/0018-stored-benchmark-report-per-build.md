# 0018. Store each build's benchmark comparison as benchmarks.json

- **Status:** Accepted, 2026-10-28 (proposed 2026-10-27)
- **Deciders:** the owner (proposed by an agent session, #303)
- **Scope:** the Atlas catalog (`scripts/build_catalog.py`) and the LCI pipeline
  (`scripts/build_lci.py`), `scripts/benchmarks.py`

## Context

The benchmark registry (ADR 0011) is evaluated at build time. Its results end up spread over
`processes/<id>.json` (catalog) and `datapackage.json` (LCI, per dataset). No single file holds
a build's whole comparison, and the release draft builds only the LCI database. #303 asks for the
KPI results to be stored per build, so that a reported comparison (for example ASU-1's O2
recovery of about 83 % against 97.85 %, explained by D-066) can be traced to one build and
commit.

## Decision

- Both builders write `benchmarks.json` (`cheme-as-code/benchmark-report/v1`,
  `benchmarks.report`): the build `mode`, the library commit, every KPI result as a row with its
  `process` and `dataset` (sorted by process, dataset, KPI), and `summary` (counts by status, in
  total and per process).
- The catalog's `<out>/benchmarks.json` is unallocated. The LCI build's
  `<out>/lci/benchmarks.json` adds `allocated` and is listed in `index.json` `files`, so the
  release draft carries it.
- The rows are the ones the build already publishes: a public build's report holds the public
  processes only. The publication rules do not change.

## Consequences

- One file per build shows the comparison, and CI artifacts and release drafts keep it.
- A consumer (the Atlas process page, a paper's table) can read it without walking every process
  file. Showing it on the Atlas page is the website's work (website#37).
- The same results now appear twice in a build (per process and in the report). Both come from
  the same `benchmarks.evaluate` call, so they cannot disagree. `tests/test_benchmarks.py` checks
  that.

## Evidence

- #303 (to-do: "store the benchmark KPI results per build").
- Accepted by the owner on 2026-10-28. The website's public check publishes both reports and
  checks their content (a public build, public processes only): website#88.
- `scripts/benchmarks.py` (`report`), `scripts/build_catalog.py`, `scripts/build_lci.py`,
  `docs/benchmarks.md` ("Where the results go"), `lci/README.md`.
- Tests: `tests/test_benchmarks.py` (`test_both_builds_store_the_benchmark_report`,
  `test_a_public_build_reports_public_processes_only`, `test_report_sorts_and_counts`).
