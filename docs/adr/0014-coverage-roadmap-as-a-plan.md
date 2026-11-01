# 0014. A ranked coverage roadmap with planned tiers, kept as a plan, not a commitment

- **Status:** Accepted as a working plan, 2026-10-25
- **Scope:** `coverage.yaml`, `schemas/coverage.schema.json`, [coverage.md](../coverage.md)

## Context

The Atlas aims at "all industrial processes", which cannot be tracked as stated. The order in
which processes are added decides which value chains connect first and which LCI gaps close.
Most production volumes are not sourced yet, so a formula-based ranking would rest on invented
numbers.

## Decision

- `coverage.yaml` lists products and processes ranked by **judgement** on four criteria (order of
  magnitude of global volume with its source, GHG and other burdens, value-chain reach, available
  open sources); no formula. Utilities are ranked by reach.
- Each entry has a family of the taxonomy ([0005](0005-chemicals-registry-and-family-taxonomy.md)),
  technology variants (`market_mix` for mixes), the processes that cover it (`covered_by`, with
  the tier each reaches) and a planned entry **tier**: 0 stoichiometric screening, 1 sourced
  conceptual data, 2 flowsheet design (a ChemE-as-Code project). Breadth (tiers 0/1) and depth
  (tier 2) grow in parallel.
- The catalog build writes `coverage.json` with a summary for the Atlas; a test keeps the table in
  docs/coverage.md and the YAML in agreement.
- The "next 10" (`next: true`) is a **working plan, not a commitment**: the order may change, and
  a change goes through `coverage.yaml`.

## Consequences

- Progress can be reported ("N of the top 50 covered, at these tiers").
- The ranking is a judgement and open to dispute; `coverage.json` says so in `summary.basis`.
- Tiers 0 and 1 depend on core's tiered generation and have no library example yet.

## Evidence

- `ca60886`, [#69](https://github.com/ChemE-as-Code/process-library/pull/69) (issue #47, part of the
  LCI gap analysis #43).
- [coverage.md](../coverage.md) ("Next 10 (working plan, accepted 2026-10-25)"),
  `tests/test_registry.py`.
