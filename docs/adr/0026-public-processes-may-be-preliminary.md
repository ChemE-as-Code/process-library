# 0026. Public processes may carry LCI mapping gaps, marked preliminary

- **Status:** Accepted, 2026-11-01
- **Deciders:** the owner (implemented by an agent session)
- **Scope:** the LCI pipeline (`scripts/build_lci.py`, `scripts/lci_activities.py`), the benchmark
  coverage warning (`scripts/build_lci.py`, `scripts/build_catalog.py`) and the mapping overrides
  (`schemas/lci-mappings.schema.json`). Supersedes the rule of
  [ADR 0022](0022-lci-gaps-for-unpublished-processes-and-per-process-mappings.md) that a public
  process or a `--public` build fails on a gap; the rest of ADR 0022 stands.

## Context

The owner decided to publish all 50 processes. Under ADR 0022, a public process with an unmapped
exchange was an error, and at that point 34 processes had such exchanges. So the public LCI build
failed, and without that build the Atlas has no LCI download. Most public processes also had fewer
than the two benchmarked KPIs, which failed `--strict`, the mode of the release workflow.

Options considered:

1. **Keep the rule and map everything first.** Holds the gate, but many exchanges have no
   background name the library can verify (no licensed copy has been checked), so publication
   would wait, or the pressure would go to guessed links.
2. **Publish only the processes without gaps.** Holds the gate, but it is not the owner's decision.
3. **Let a public process carry gaps, marked plainly as preliminary.** The owner's decision of
   2026-11-01.

## Decision

- **A gap is never a build failure,** for any process and in any build, `--public` and `--strict`
  included. It is exported unlinked as ADR 0022 describes: never linked to a guess, dropped or
  zero-filled.
- **A process with a gap is preliminary, and says so** in every output, machine-readably:
  `atlas preliminary` and `atlas gaps` on the activity, comment lines, the workbook's `about`
  sheet, `datapackage.json` (`processes[].preliminary`, `gap_count`, `gaps`;
  `activities[].preliminary`, `gaps`), `index.json` (`preliminary`, `gaps`, each activity's
  `preliminary`), `lci/gaps.json` and a caveat. `publication` stays separate: public does not mean
  complete. A market is preliminary when a supplier is.
- **Benchmark gaps stay warnings, also under `--strict`:** a public process with fewer than two
  KPIs is printed as a warning and does not fail the build. A KPI outside its range still fails
  `--strict`.
- **Real errors still fail:** a schema error, an override naming an unknown entry or dataset, a
  unit mismatch, an uncurated free emission, a negative technosphere amount in a cut-off build.
- **An override may name an Atlas producer** (`dataset: {path, product}`), the mappings' form of a
  dataset's `link.dataset`, so an input with no verified background name can link a library plant
  without one being invented. Its unit must match.

## Consequences

- The public build works now, and a public result can be incomplete: an unlinked exchange counts
  no burden, so a preliminary footprint is too low by an unknown amount. The marking has to be read;
  a site that shows these datasets must show it.
- This weakens a quality gate on purpose. `lci/gaps.json` is now the only pressure to map, so it is
  the list to work through.
- `install()` still refuses a database with any gap, and writes nothing, by design. While gaps
  remain, the public database does not install into Brightway with the helper. The openLCA JSON-LD
  carries gaps as flows of their own and can be imported.
- An activity that links a preliminary activity inherits its incompleteness. Only the process
  with the gap, and a market with such a supplier, is marked; the caveat says so.

## Evidence

- Tests in `tests/test_build_lci.py` and `tests/test_benchmarks.py`: the same unmapped feed and
  emission build strictly and publicly, unlinked and marked preliminary in every output; a process
  without gaps is not marked; an override with an unknown entry or dataset, or a wrong unit, still
  fails; the benchmark gap is a warning under `--strict`, and a KPI outside its range still fails.
