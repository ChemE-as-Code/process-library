# 0011. A benchmark registry of KPIs with cited open reference ranges, evaluated in both builds

- **Status:** Accepted, 2026-10-25
- **Scope:** `benchmarks/<family>.yaml`, `schemas/benchmarks.schema.json`, `scripts/benchmarks.py`

## Context

A dataset can pass every structural check and still be implausible: a unit slip of a factor of
1000 in power, a missing utility. Published inventories are judged against the state of the
art (specific energy, yield, emissions). Ranges taken from memory or padded around a single
value would give false confidence, and copying tables from sources would breach
[0013](0013-licences-and-no-third-party-content.md).

## Decision

- One registry file per process family, `benchmarks/<family>.yaml`
  (`cheme-as-code/benchmarks/v1`). A KPI has a title, a unit and either reference ranges from
  **cited open sources** (BREFs, IEA, peer-reviewed reviews, statistics; manufacturer literature
  only when nothing else states the conditions) with the conditions they hold for, or a recorded
  `no_open_reference` saying what was searched and when. Never an invented range.
- `datasets:` binds KPIs to an LCI dataset as expressions over its exchange keys. The rules live
  in `scripts/benchmarks.py`, used by **both** builders, so the catalog and the LCI database
  report the same statuses (`inside`, `outside`, `explained`, `no-reference`, `unchecked`).
- A value outside its range without an explanation, a KPI that cannot be evaluated, and a public
  process with fewer than two KPIs are warnings, so `--strict` fails.

## Consequences

- Implausible inventories are caught before publication, and users see where a dataset sits.
- Unit conversion needs core (`foundation.units`); without it KPIs are `unchecked` and strict
  builds fail, so builds and CI install core.
- Comparison is on the unallocated basis only; conditions are not compared by the build, the
  person binding a dataset must choose a matching reference.
- Each new public process needs sourcing work before it can pass strict builds.

## Evidence

- `b21ac1f` "Benchmark registry: KPIs with sourced reference ranges, evaluated in both builds"
  and `2b3896a` review fixes, [#72](https://github.com/ChemE-as-Code/process-library/pull/72) (issue #48).
- [benchmarks.md](../benchmarks.md), `scripts/benchmarks.py` (`MIN_KPIS = 2`),
  `tests/test_benchmarks.py`.
