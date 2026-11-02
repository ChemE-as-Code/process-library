# 0029. Give no total, with the reason, when every contribution to a category is a gap

- **Status:** Proposed, 2026-10-30
- **Deciders:** the owner (proposed by an agent session, #250)
- **Scope:** the Atlas catalog (`scripts/build_catalog.py`, `scripts/routes.py`): LCA totals,
  headline footprints and route footprints. Builds on
  [ADR 0026](0026-public-processes-may-be-preliminary.md), whose rule (a headline `value` of null
  with `not_computed: true` where nothing was characterised) stands unchanged; this ADR adds
  the reason, takes the gap-only categories out of the totals and covers the PCF lines, the
  route footprint and `factors_status`.

## Context

The audit of 2026-10-29 (#250) found 13 processes whose LCA headline in the catalog was exactly
0 kg CO2-eq; glycerol-1 followed. A recount on the shipped `lca/results.csv` and `lca/gaps.csv`
files (core 1.2.1, 2026-11-01) finds **21 processes** whose headline category (climate-change,
baseline) has gaps and not one contribution: acetaldehyde-1, acetic-acid-1, acetone-1,
aniline-1, bromine-1, chloromethane-1, dmf-1, ethanol-1, glycerol-1, hda-1, hydrazine-1,
hydrogen-bromide-1, hydrogen-chloride-1, hydrogen-peroxide-1, isobutene-1, methylamines-1,
phosphorus-oxychloride-1, potassium-permanganate-1, sulfuric-acid-1, thf-1 and
thionyl-chloride-1. 18 of them publish their values and showed 0; hydrazine-1, thf-1 and
thionyl-chloride-1 are withheld (`values_withheld`) and showed no value. The Atlas reads 0 as
"no footprint", but a study with unlinked backgrounds has an unknown footprint, not a zero one.

The cause is in how results reach the catalog, not in the studies:

- In all 21 studies every exchange of the category is a gap. Their backgrounds are declared `missing:`
  (preliminary inventories, site not chosen), and the plant's direct emissions are not
  greenhouse gases (water, nitrogen, oxygen, SO2, chlorine; outside GWP100). No characterised
  contribution exists. The gaps are listed in `lca/gaps.csv`.
- core (1.1.0, and still 1.2.1 at 8042b71, the version CI pins now) writes a `total` row of 0 to `lca/results.csv` for
  such a category. Its own `lca/results.md` says "no total (every contribution a gap)" for the
  same category (core `LcaReport.comparability`: a category with gaps and no contribution has
  no total, never 0).
- The catalog took the `total` row as authoritative and never read `lca/gaps.csv`. Only
  processes with scenario records (`lca/scenarios/*.json`) had their gap-only totals dropped,
  and none of the 21 has scenario records.
- Since this ADR was proposed, [ADR 0026](0026-public-processes-may-be-preliminary.md)
  (website#96) gave the catalog headline `value: null` and `not_computed: true` when the
  baseline total is exactly 0 and no flow contributes. That covers the headline of these 21
  processes, because a gap-only category has no contribution and a total of 0. It does not
  remove the 0 from `lca.totals` in `processes/<id>.json` (nor in the other scenarios), does not
  say why there is no value, and does not reach the route footprint in `routes.json`, the PCF
  lines or `factors_status`.

The same reading found two more faults in `_lca`:

- core writes the product carbon footprint breakdown (`fossil`, `biogenic_carbon`,
  `product_carbon`, ...) as rows of category `pcf` in mixed units (kg CO2-eq, kg C, kg CO2).
  The catalog treated `pcf` as an impact category. It summed the lines into a meaningless
  "total" (glycerol-1 -1.37, kraft-pulp-1 0.31, urea-1 0.40) and listed them as
  contributions. Their empty status also made the `factors_status` "mixed".
- With no contribution at all, `factors_status` was "published": an empty set of statuses is a
  subset of {PUBLISHED, EPD}.

The options were: (a) fix core so that it writes no total row, and wait for a pinned core
release, or (b) mirror core's every-contribution-a-gap rule in the catalog from the files core already writes. We
chose (b) now; (a) remains a follow-up for core, and the catalog rule stays correct after it.

## Decision

- A category of a scenario has **no total** when `lca/gaps.csv` lists for it at least one gap
  that leaves a burden unknown and `lca/results.csv` has no contribution row for it. Gaps of
  reasons `elementary-uncharacterised` and `biosphere-uncharacterised` (core's
  `OUTSIDE_METHOD`: the flow is outside the method) do not count. The catalog leaves the
  category out of `lca.totals` and records it in `lca.no_total`
  (`{scenario: {category: {reason: "every-contribution-a-gap", gaps: <number of distinct
  exchanges>}}}`). ADR 0026's `lca.not_computed` (the list of baseline categories without a
  footprint) includes the baseline categories of `lca.no_total`. Only this case of core's `LcaReport.comparability` is mirrored; its other
  case (a scenario that loses exchanges the baseline characterises: "not comparable") is not,
  and does not bear on the baseline headline.
- A category without such gaps keeps its total in `lca.totals`, also when it is 0. ADR 0026
  still applies to it: a baseline 0 with no contributing flow has no footprint on the headline
  (reason `nothing-characterised`). A category with contributions keeps its total, and its gaps
  stay listed beside it, as before.
- The catalog summary's `lca` headline keeps ADR 0026's `value: null` and `not_computed: true`
  and adds `not_computed_reason`: `every-contribution-a-gap` (this ADR) or
  `nothing-characterised` (ADR 0026's case without gaps). The route footprint in `routes.json`
  follows the same rule with the same three fields. A consumer (the Atlas, website#96) shows
  "not computed" with the reason, never 0.
- `pcf` rows are not an impact category. They go to `lca.pcf` (the baseline lines, each
  `{key, basis, value, unit}`) and never into `categories`, `totals`, `contributions` or the
  factor status. A withheld LCA loses `lca.pcf` and `lca.no_total` (its gap counts come
  from `lca/gaps.csv`) with its totals; its headline carries `values_withheld`, not
  `not_computed`.
- A PCF line in the unit of its basis category (kg CO2-eq: fossil, biogenic, including,
  excluding, ...) is a part of that category's total. When the baseline has no total for that
  category (this ADR or ADR 0026), **every** line in that unit gets `value: null` and
  `not_computed` with the reason. This includes the lines derived from the product's carbon content (`withdrawal`,
  `withdrawal_other`, and any other kg CO2-eq line): the catalog does not know which of core's
  kg CO2-eq lines depend on the missing backgrounds, so it nulls them all (conservative). For
  glycerol-1 this nulls fossil 0, including -1.07551, withdrawal -1.01201 and withdrawal_other
  -0.0634975; its carbon contents in kg C (product 0.390089, biogenic 0.276199, fossil 0.11389) stay. Lines in other
  units (kg C carbon contents, kg CO2 flows) describe the product and the plant and keep their
  values.
- `factors_status` is `none` when not one contribution was characterised.

## Consequences

- The Atlas no longer shows 0 for the 18 published ones of these 21 processes. Their value is null with the reason.
  Their footprint remains unknown until their backgrounds are linked (per process, in
  `lca/lca.yaml`; a foreground decision of each process's DESIGN.md, not of this ADR).
- `lca.no_total`, `lca.pcf`, `not_computed_reason` (headline and route footprint), the route
  footprint's `not_computed` and the `factors_status` value `none` are additive; ADR 0026's
  fields keep their form. A consumer that reads `value` must handle null; it already had to for a
  process without a total.
- `pcf` disappears from `lca.categories` and `lca.totals` (glycerol-1, kraft-pulp-1, urea-1). A
  consumer that showed it there showed a sum of mixed units.
- glycerol-1 shows its PCF impact lines (fossil 0, including -1.08 kg CO2-eq from the biogenic
  withdrawal alone) as not computed; its carbon contents stay.
- kraft-pulp-1 and urea-1 move from `mixed` to `published` factors, because the PCF rows no
  longer count.
- The rule depends on `lca/gaps.csv`. A study without that file, or one written by a core that
  writes none, keeps the stated total (also 0) in `lca.totals`: the catalog cannot tell a
  gap-only 0 from a real zero without it. Its headline still has no value under ADR 0026.
- Follow-up for core: write no `total` row (or an empty one) in `lca/results.csv` for a category
  whose every contribution is a gap, so that `results.csv` agrees with `results.md`.
  `lca/uncertainty.csv` gives the same category a deterministic 0 and a 0 .. 0 interval. The
  route footprint does not use the interval when the value is null.

## Evidence

- `scripts/build_catalog.py` (`_gap_only`, `_not_computed`, `_not_computed_reason`, `_lca`,
  `_publish`, the summary headline),
  `scripts/routes.py` (`_footprint`).
- Tests: `tests/test_build_catalog.py` (`test_a_category_whose_every_contribution_is_a_gap_has_no_total`,
  `test_a_zero_without_gaps_keeps_its_total_but_is_no_footprint`, `test_a_category_with_contributions_keeps_its_total_beside_its_gaps`,
  `test_the_pcf_breakdown_is_not_an_impact_category`,
  `test_the_pcf_impact_lines_of_a_gap_only_category_are_unknown`,
  `test_the_shipped_library_reports_no_gap_only_total_as_zero`), `tests/test_routes.py`
  (`test_a_gap_only_footprint_is_null_with_its_reason`).
- #250; core `chemeascode/domains/assessment/lca/report.py` (`comparability`, the `total`
  row of `results.csv`, `PCF_CATEGORY`) and `impacts.py` (`OUTSIDE_METHOD`, `real_gaps`) at
  c2a45135 (1.1.0) and 8042b71 (1.2.1, unchanged in these parts).
