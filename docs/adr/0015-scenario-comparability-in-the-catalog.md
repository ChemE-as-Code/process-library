# 0015. Carry core's scenario comparability verdict and factor scope into the catalog

- **Status:** Proposed, 2026-10-26
- **Deciders:** the owner (proposed by an agent session, core#306)
- **Scope:** the Atlas catalog (`scripts/build_catalog.py`), LCA scenarios

## Context

The catalog publishes each process's LCA scenarios from core's records
(`lca/scenarios/<id>.json`). Until now it carried `comparable` and `dropped`, which say only
whether an exchange the baseline characterises is a gap in the scenario. Two scenarios without
gaps could still rest on electricity factors that measure different things: ASU-1's UK baseline
(DESNZ, at the consumer with T&D and well-to-tank) against NL and DE on EEA ENER038 (direct
emissions per kWh of gross generation). Core now records, per scenario, a verdict from the
factors' structured scope (core `docs/framework/lci-comparison-basis.md`, core#306):
`like-for-like`, `proxy` or `not comparable`, with the reasons and the dimensions compared, and
the scope of each linked exchange.

## Decision

- Each catalog scenario carries `comparability` as core wrote it (`verdict`, `reasons`,
  `compared`) and `boundary` (the study's system boundary), beside the existing
  `functional_unit` and `allocation`. Each link carries `scope` (null: not declared).
- A record written before core#306 has no verdict: `comparability` is null, which a consumer
  (the Atlas, the viewer) shows as "not assessed", never as like-for-like.
- `comparable` keeps its meaning (gaps only); the verdict is a separate field.

## Consequences

- The Atlas can show the verdict, the functional unit, the allocation and the boundary beside
  every scenario number; a `not comparable` scenario must not be presented as a country
  comparison.
- The fields are additive; consumers that ignore them are unaffected.
- The verdict exists only in records regenerated with core after core#318; until then it is null.

## Evidence

- `scripts/build_catalog.py` (`_scenarios`, `LINK_FIELDS`), `tests/test_build_catalog.py`.
- core#306, core#318; ASU-1 decision D-110 (`processes/asu-1/DESIGN.md`).
