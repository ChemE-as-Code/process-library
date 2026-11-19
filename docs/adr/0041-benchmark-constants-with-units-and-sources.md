# 0041. A benchmark binding may name constants with a unit and a source

- **Status:** Proposed, 2026-11-19
- **Deciders:** the owner, as the library's maintainer (drafted by an agent session for issue #272)
- **Scope:** the benchmark registry: `schemas/benchmarks.schema.json` (a binding's `constants`),
  `scripts/benchmarks.py` (expressions, used by `build_lci.py` and `build_catalog.py`) and the
  KPI results in `datapackage.json`, `processes/<id>.json` and `benchmarks.json`. It extends
  [ADR 0011](0011-benchmark-registry-with-cited-ranges.md) and leaves its rules unchanged.

## Context

ADR 0011 binds a KPI to an LCI dataset as an expression over the dataset's exchange keys, with
units taken from the exchanges. A number in an expression has no unit. That is enough for a
specific power (`feed:POWER / product:GOXP`, kWh/kg) or a mass ratio, but not for an energy KPI
of a dataset whose fuel is a mass exchange: ammonia-1's natural gas `feed:NG` is in kg and its
steam export `product:STEAM` in kg, and its four energy KPIs (net and gross specific energy,
natural gas feed plus fuel, steam export, in GJ/t) need the gas's heating value and the steam's
enthalpy (#272, found binding ammonia-1 in #271 and #304). Written as `feed:NG * 49.0858 /
product:NH3` the value is right but the unit is kg/kg, so the KPI could not convert to GJ/t and
was `unchecked`; adding `feed:POWER` (kWh) to it was an error. The energy KPIs were therefore
compared only in the run report (`processes/ammonia-1/runs/benchmark-kpis.md`), outside the
strict builds.

Options considered:

- **Numbers with units in expressions** (`feed:NG * 49.0858 MJ/kg`): the shortest, but the
  number's meaning and source would sit in a comment or nowhere, and the same value would be
  repeated in every KPI that uses it.
- **A heating value on the dataset's exchange** (an LHV property read as `lhv(feed:NG)`): the
  value would travel with the dataset, but it changes core's `lci_dataset` contract and every
  dataset writer, and a steam enthalpy above a chosen make-up water state is a benchmark
  convention rather than a property of the exchange.
- **Named constants of the binding**, each with a value, a unit, a provenance and a source,
  used as `const:<name>`: no change to the datasets or to core, the source recorded once next to
  the value, and the unit checked like an exchange's.

## Decision

- A binding in `benchmarks/<family>.yaml` may have **`constants`**: by name (a slug), a `value`,
  a `unit`, a `provenance` (`calculated` from the process's own files, `sourced` from a cited
  publication, or `assumed`) and a `source` with a locator (file and section, or citation and
  page); a `note` is optional. An expression uses one as `const:<name>`.
- A constant's unit is units joined by `*` and `/`, each one of kg, kWh, m, m2, m3, g, t, kJ, MJ,
  GJ, MWh, mol, kmol (`benchmarks.UNIT_SPELLING`). The registry check (`benchmarks.load`, an
  error in both builds) refuses an unreadable unit and a `const:` the binding does not define.
- A constant belongs to its binding: it describes that dataset's stream (the gas composition,
  the steam state). A unit conversion (3.6 MJ/kWh) is never a constant.
- **Terms that are added or subtracted are converted to the first term's unit** through core's
  `foundation.units` (so `feed:NG * const:ng-lhv + feed:POWER` is in MJ); units that do not
  convert (kWh and kg) stay an error, and without core such a KPI is `unchecked`, as any
  conversion is under ADR 0011.
- Every KPI result whose expression uses constants carries them (`constants`: each with its
  value, unit, provenance and source) in `datapackage.json`, the catalog and `benchmarks.json`,
  so a reader can redo the number. The field is additive; the registry and report schema ids
  stay `cheme-as-code/benchmarks/v1` and `cheme-as-code/benchmark-report/v1`.
- ammonia-1's four energy KPIs are bound with two constants, the natural gas LHV (49.0858 MJ/kg)
  and the MP steam enthalpy above the make-up water (3.09848 MJ/kg), both `calculated` by the
  blind KPI job (`processes/ammonia-1/scripts/benchmark_kpis.py`). They reproduce its values
  (26.97, 30.13, 28.01 and 3.16 GJ/t) and are `explained` against the BREF and IEA ranges with
  the design decisions behind them (D-014, D-015, D-016).

## Consequences

- Energy KPIs of mass-based datasets are compared in the strict builds, not only in run
  reports, and the heating value or enthalpy they rest on is published with them.
- The constant is the binder's statement about the dataset, not a value the dataset carries: if
  the design's gas composition or steam conditions change, the constant must be recomputed by
  hand; nothing checks it against the dataset. A heating value carried on the exchange (core's
  contract) would remove that drift and remains a possible later step.
- Conventions stay in the binding: ammonia-1's electricity counts as delivered energy and its
  steam at its enthalpy, stated in the binding's `conditions` and the reasons; a KPI on another
  convention needs another expression, not another constant.
- Adding terms in different but convertible units is no longer an error, so a binder who meant
  kWh electric plus MJ of fuel gets the sum without a warning; the unit check still refuses
  dimensionally different terms.

## Evidence

- Issue #272; the blind KPI values in `processes/ammonia-1/runs/benchmark-kpis.md` (#304).
- `schemas/benchmarks.schema.json` (`constants`, `$defs/constant`), `scripts/benchmarks.py`
  (`constant_units`, `constants_used`, `compute`, `evaluate`), `benchmarks/ammonia.yaml`
  (the ammonia-1 binding), `docs/benchmarks.md`.
- `tests/test_benchmarks.py`: `test_constant_units_are_read_from_known_units`,
  `test_a_constant_carries_its_unit_into_the_expression`,
  `test_added_terms_convert_to_the_first_terms_unit`,
  `test_without_core_adding_different_units_names_core`, `test_constant_problems`,
  `test_ammonia_energy_kpis_are_bound_with_their_constants`.
