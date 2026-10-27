# Benchmarks

Every published dataset is checked against **independent reference ranges** for its key
performance indicators (KPIs): specific energy, yield, specific emissions, water and catalyst
use. The aim is to catch an implausible inventory before publication, and to show users where a
dataset sits relative to the state of the art (process-library#48, part of the LCI gap analysis
#43).

The registry is `benchmarks/<family>.yaml`, one file per process family of
`taxonomy/families.yaml` (schema `schemas/benchmarks.schema.json`,
`cheme-as-code/benchmarks/v1`). The rules live in `scripts/benchmarks.py`, which both builders
use, so the catalog and the LCI database report the same results.

## A KPI and its references

A KPI has a title, a unit (`kWh/t`, `GJ/t`) and either reference ranges or a recorded
`no_open_reference`:

```yaml
kpis:
  specific-power-gox:
    title: Specific electric power per t of gaseous oxygen product
    unit: kWh/t
    references:
      - id: air-liquide-yango-2017
        range: [400, 600]
        basis: unallocated
        conditions: {purity: 99.5 to 99.8 % O2, pressure: up to 42 barg, capacity: 330 to 770 t/d oxygen, year: 2017}
        source: {citation: "...", url: "...", locator: "p. 8", kind: manufacturer, accessed: "2026-10-25"}
  cooling-duty-gox:
    title: Cooling-water duty (heat rejected) per t of gaseous oxygen product
    unit: GJ/t
    no_open_reference: "No open source found ... (what was searched, and when)"
```

- **Ranges are facts from cited open sources**, recorded in our own form (CLAUDE.md): EU BREFs
  (BAT-AEL and BAT-AEPL tables, reuse with attribution), IEA reports, peer-reviewed reviews and
  government statistics. `source.kind` says which. Manufacturer literature is used only when no
  other open source states the conditions, and it is marked `kind: manufacturer` with a note.
- **Never invent a range.** A KPI without an open source records `no_open_reference`: what was
  searched and when. It is still computed and shown, with status `no-reference`. Do not turn a
  single literature value into a range by adding a margin.
- **Conditions** are what the source states the range for (technology, product, purity,
  pressure, capacity, region, year). A specific power at 30 barg cannot be compared with one at
  atmospheric delivery. The build does not compare conditions. The person who binds a dataset
  chooses a reference whose conditions match, and writes the dataset's own `conditions` beside
  it so the reader can see any difference.
- **Units.** A range is recorded in the KPI's unit. If the source uses another unit, convert it
  and state the conversion in the reference's `note`. Converting per Nm3 to per t needs a
  density, which is a modelling step and not a unit conversion.
- **Basis.** `unallocated` only for now: the whole process's exchange per unit of the named
  product, as the literature reports specific consumptions. The LCI build also records each
  KPI's allocated value (see below), but it is not compared with a range yet.

## Evaluating a dataset

`datasets:` binds the KPIs to an LCI dataset by process and dataset id. Each KPI is an
expression over the dataset's exchange keys:

```yaml
datasets:
  - process: asu-1
    dataset: asu-1-500-t-d-gox
    conditions: {purity: ">= 99.5 mol% O2", pressure: 30 barg, capacity: 500 t/d GOX}
    kpis:
      specific-power-gox: {expression: feed:POWER / product:GOXP, per: product:GOXP, reference: air-liquide-yango-2017}
      cooling-duty-gox: {expression: product:CW / product:GOXP, per: product:GOXP}
```

- An expression has exchange keys, numbers, `+ - * /` and brackets. Put spaces around the
  operators, because a key may contain `-`. The dataset's `basis` (for example 1 h of
  operation) cancels in a ratio.
- **Units come from the exchanges.** `feed:POWER / product:GOXP` is in kWh/kg. It is converted
  to the KPI's unit by core's `foundation.units` (`convert_units`, through Pint), which is the
  package's single unit system. Adding exchanges of different units is an error. Without core
  installed (`cheme-as-code[units]`), a KPI whose unit differs from its expression's unit is
  `unchecked`. That is a warning, so `--strict` builds need core.
- `per` names the product the KPI refers to. It must be a `product:` exchange of the dataset;
  otherwise the build warns. `build_lci.py` records `allocated`, the value times that product's
  allocation share. A KPI that is not per unit of a product (a recovery, a yield) has no `per`. ASU-1's GOX carries about 70 % of the burdens under exergy
  allocation, so 502 kWh/t unallocated becomes about 352 kWh/t allocated.

Each result has a status:

| status | meaning | build |
|---|---|---|
| `inside` | within the chosen reference's range | passes |
| `outside` | outside it, no explanation | warning: `--strict` fails |
| `explained` | outside it, with an `out_of_range_reason` | passes; the reason is shown |
| `no-reference` | the KPI records `no_open_reference` | passes |
| `unchecked` | not computable here (missing exchange, unit not convertible, core missing) | warning |

An explanation is required for every value outside its range. It is written as
`out_of_range_reason` on the KPI in the binding (`benchmarks/<family>.yaml`), so the build can
check it. When the process's DESIGN.md records the decision behind the value, the reason names
that decision (for example `D-066 in processes/asu-1/DESIGN.md`) instead of repeating it; the
explanation may live in DESIGN.md or a dataset note, but the link to it is always the
`out_of_range_reason`. A reason left on a value that is now inside is reported as stale. A KPI
with `no_open_reference` has no range, so an `out_of_range_reason` on it is a registry error.

**Coverage.** In a library with a `benchmarks/` folder, every public process with an LCI dataset
needs at least two KPIs, each with a source or a recorded `no_open_reference`. Otherwise both
builds warn. A binding that names no dataset of the library (for example after a rename) is a
warning too, and so is a binding under a family that the process's `process.yaml` does not list
in `families`.

## Where the results go

- `build_lci.py`: per dataset in `datapackage.json`, `benchmarks`: each KPI with `value`,
  `allocated`, `status`, the chosen `reference` (range, conditions, source) or
  `no_open_reference`, and the `reason` of an explained value.
- `build_catalog.py`: per process in `processes/<id>.json`, `benchmarks` (the same results,
  unallocated, each with its `dataset` id); in `catalog.json`, the summary's `benchmarks` counts
  them by status. The Atlas process page shows the position in the range (website#37).
- Both builders also write **`benchmarks.json`** (`cheme-as-code/benchmark-report/v1`,
  `benchmarks.report`), the stored report of the build: every result of the library in one list
  (`results`, each row with its `process` and `dataset`, sorted), the counts by status in total
  and per process (`summary`), the build `mode` and the library commit. The catalog's
  (`<out>/benchmarks.json`) is unallocated; the LCI build's (`<out>/lci/benchmarks.json`, listed
  in `index.json`) adds `allocated`. A public build holds the public processes only. CI keeps the
  public catalog's report with the catalog artifact, and the release draft keeps the LCI build's
  (#50), so a comparison a paper reports can be traced to one commit (#85).

Both additions are additive: no existing field changes.

## ASU-1

| KPI | ASU-1 | reference | status |
|---|---|---|---|
| specific power per t GOX | 502 kWh/t (99.5 % O2, 30 barg, 500 t/d, external compression) | 400 to 600 kWh/t, Air Liquide Yango standard ASU (99.5 to 99.8 % O2, up to 42 barg, 330 to 770 t/d, internal compression), brochure 2017 | inside |
| O2 recovery | 82.8 % | 97.85 %, typical state-of-the-art cryogenic ASU at 99.5 % O2, Pfaff and Kather 2009, p. 496 (a single value) | explained (D-066: no argon column, simulated double column) |
| cooling-water duty per t GOX | 1.85 GJ/t | no open reference found (2026-10-25) | no-reference |

The power reference is a manufacturer's published specification. It is independent of the
library but not peer reviewed. It is the only open source found that states a range for
high-purity oxygen at pipeline pressure. Open peer-reviewed figures exist for near-atmospheric
delivery (Pfaff and Kather 2009, Energy Procedia 1:495–502, about 0.25 kWh per kg O2 at
99.5 %), but they do not apply at 30 barg and are single values. A BREF, IEA or peer-reviewed
range for pressurised high-purity oxygen should replace or join it when one is found. The
brochure does not say whether its figure covers the whole plant's power per t O2 or how
co-products count; `basis: unallocated` is our reading of it.

The O2 recovery reference is a single typical value, recorded as a zero-width range, so every
dataset's recovery needs its own explanation until a source states a range. ASU-1's 82.8 % is
well below it: the simulated double column without an argon column needs more air for 99.5 %
GOX (DESIGN.md D-066, which revised the concept's 94 % of D-018).

`tests/fixtures/benchmarks/asu-1-mis-scaled.yaml` is a deliberately wrong copy of the dataset,
with the power in Wh labelled kWh. Its 501,700 kWh/t falls outside the range, so the strict LCI
build and the strict catalog build fail on it (`tests/test_benchmarks.py`).

## Adding benchmarks for a process

1. Find the family's file, or add `benchmarks/<family>.yaml` (the family must be in
   `taxonomy/families.yaml`).
2. Add the KPIs the family is judged by, with ranges from open sources and their conditions, or
   a `no_open_reference` that says what was searched and when.
3. Bind the process's dataset: an expression per KPI, `per` its product, and the reference whose
   conditions match.
4. Build with `--strict`. A value outside its range is either a data error to fix or a real
   difference to explain in `out_of_range_reason`.
