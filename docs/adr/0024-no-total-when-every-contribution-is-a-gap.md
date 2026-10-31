# 0024. Give no total, with the reason, when every contribution to a category is a gap

- **Status:** Proposed, 2026-10-30
- **Deciders:** the owner (proposed by an agent session, #250)
- **Scope:** the Atlas catalog (`scripts/build_catalog.py`, `scripts/routes.py`): LCA totals,
  headline footprints and route footprints

## Context

14 of the 33 processes with an LCA headline in the catalog showed a footprint of exactly
0 kg CO2-eq (13 at the audit of 2026-10-29, #250; glycerol-1 since). The Atlas reads this as
"no footprint". Six of them are cradle-to-gate studies, so 0 cannot be a result.

The cause is in how results reach the catalog, not in the studies:

- In all 14 studies every exchange is a gap. Their backgrounds are declared `missing:`
  (preliminary inventories, site not chosen), and the plant's direct emissions are not
  greenhouse gases (water, nitrogen, oxygen, SO2, chlorine; outside GWP100). No characterised
  contribution exists. The gaps are listed in `lca/gaps.csv`.
- core (1.1.0, the version CI pins) still writes a `total` row of 0 to `lca/results.csv` for
  such a category. Its own `lca/results.md` says "no total (every contribution a gap)" for the
  same category (core `LcaReport.comparability`: a category with gaps and no contribution has
  no total, never 0).
- The catalog took the `total` row as authoritative and never read `lca/gaps.csv`. Only
  processes with scenario records (`lca/scenarios/*.json`) had their gap-only totals dropped,
  and none of the 14 has scenario records.

The same reading found two more faults in `_lca`:

- core writes the product carbon footprint breakdown (`fossil`, `biogenic_carbon`,
  `product_carbon`, ...) as rows of category `pcf` in mixed units (kg CO2-eq, kg C, kg CO2).
  The catalog treated `pcf` as an impact category. It summed the lines into a meaningless
  "total" (glycerol-1 -1.37, kraft-pulp-1 0.31, urea-1 0.40) and listed them as
  contributions. Their empty status also made the `factors_status` "mixed".
- With no contribution at all, `factors_status` was "published": an empty set of statuses is a
  subset of {PUBLISHED, EPD}.

The options were: (a) fix core so that it writes no total row, and wait for a pinned core
release, or (b) apply core's own rule in the catalog from the files core already writes. We
chose (b) now; (a) remains a follow-up for core, and the catalog rule stays correct after it.

## Decision

- A category of a scenario has **no total** when `lca/gaps.csv` lists for it at least one gap
  that leaves a burden unknown and `lca/results.csv` has no contribution row for it. Gaps of
  reasons `elementary-uncharacterised` and `biosphere-uncharacterised` (core's
  `OUTSIDE_METHOD`: the flow is outside the method) do not count. The catalog leaves the
  category out of `lca.totals` and records it in `lca.not_computed`
  (`{scenario: {category: {reason: "every-contribution-a-gap", gaps: <exchanges>}}}`).
- A category without such gaps keeps its total, **also when it is 0**: that is a real zero.
  A category with contributions keeps its total, and its gaps stay listed beside it, as before.
- The catalog summary's `lca` headline and the route footprint in `routes.json` give
  `value: null` and `not_computed: "every-contribution-a-gap"`. A consumer (the Atlas,
  website#96) shows "not computed" with the reason, never 0.
- `pcf` rows are not an impact category. They go to `lca.pcf` (the baseline lines, each
  `{key, basis, value, unit}`) and never into `categories`, `totals`, `contributions` or the
  factor status. A withheld LCA loses `lca.pcf` with its totals.
- `factors_status` is `none` when not one contribution was characterised.

## Consequences

- The Atlas no longer shows 0 for these 14 processes. Their value is null with the reason.
  Their footprint remains unknown until their backgrounds are linked (per process, in
  `lca/lca.yaml`; a foreground decision of each process's DESIGN.md, not of this ADR).
- `lca.not_computed`, `lca.pcf`, `headline.not_computed` and the `factors_status` value `none`
  are additive. A consumer that reads `value` must handle null; it already had to for a
  process without a total.
- `pcf` disappears from `lca.categories` and `lca.totals` (glycerol-1, kraft-pulp-1, urea-1). A
  consumer that showed it there showed a sum of mixed units.
- kraft-pulp-1 and urea-1 move from `mixed` to `published` factors, because the PCF rows no
  longer count.
- The rule depends on `lca/gaps.csv`. A study without that file, or one written by a core that
  writes none, keeps the stated total (also 0): the catalog cannot tell a gap-only 0 from a
  real zero without it.
- Follow-up for core: write no `total` row (or an empty one) in `lca/results.csv` for a category
  whose every contribution is a gap, so that `results.csv` agrees with `results.md`.
  `lca/uncertainty.csv` gives the same category a deterministic 0 and a 0 .. 0 interval. The
  route footprint does not use the interval when the value is null.

## Evidence

- `scripts/build_catalog.py` (`_not_computed`, `_lca`, `_publish`, the summary headline),
  `scripts/routes.py` (`_footprint`).
- Tests: `tests/test_build_catalog.py` (`test_a_category_whose_every_contribution_is_a_gap_has_no_total`,
  `test_a_real_zero_stays_zero`, `test_a_category_with_contributions_keeps_its_total_beside_its_gaps`,
  `test_the_pcf_breakdown_is_not_an_impact_category`,
  `test_the_shipped_library_reports_no_gap_only_total_as_zero`), `tests/test_routes.py`
  (`test_a_gap_only_footprint_is_null_with_its_reason`).
- #250; core `chemeascode/domains/assessment/lca/report.py` (`comparability`, the `total`
  row of `results.csv`, `PCF_CATEGORY`) and `impacts.py` (`OUTSIDE_METHOD`, `real_gaps`) at
  c2a45135.
