# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-27 | lca/lca.yaml, lca/ outputs, DESIGN.md D-013 | exported default allocation energy (LHV) with `allocation.deviation`, substitution and mass compared; `dataset.system_model: cutoff` | PR #189 CI: the library LCI build refused `allocation: substitution` (not exportable as one activity per co-product) and warned that it did not follow the hierarchy |
| 2026-10-27 | process.yaml, lca/, DESIGN.md, process/flowsheet.yaml, process/BFD.xml, process/PFD.xml, scripts/hda_balance.py | response to review 2026-10-27-pfd-lci-review (see Responses below); commits d4740fd, 462bacc | close the high and the quick medium/low findings |
| 2026-10-27 | DESIGN.md, process.yaml, PROGRESS.md, checks/checks.yaml | route/boundary memo, decisions D-001 to D-013, evidence table, source register, method/dependency table, open inputs, missing registry entries; Atlas manifest (internal, concept, unreviewed); BFD/PFD files in the concept gate | document the concept run (issue #302) |
| 2026-10-27 | lca/ | preliminary gate-to-gate LCI per kg benzene, every background open (10 gaps), substitution proposed; balance closed | step 4 of the run |
| 2026-10-27 | scripts/hda_balance.py, process/flowsheet.yaml, equipment list | C-202/C-203 reboiler duties from the arriving feed enthalpy (2300 and 650 kW); overall energy closure 0.25 % | energy check found the feeds taken at their bubble point |
| 2026-10-27 | equipment/equipment-list.yaml, piping/line-list.yaml | 18 items, 24 lines with ASSUMED design conditions and DN | lists as far as the PFD requires |
| 2026-10-27 | process/*.yaml, process/BFD.xml, process/PFD.xml, scripts/hda_balance.py | design basis, materials, reactions, flowsheet (2 blocks, 15 steps, 24 + 10 streams), independent balance script; generated BFD/PFD | concept design to a balanced PFD |
| 2026-10-27 | (all) | scaffold from cheme init and the process.yaml template | start of hda-1 |

## Responses to reviews

### Review 2026-10-27-pfd-lci-review (reviewed commit 9af76cf)

| finding | response | commit |
|---|---|---|
| #1 (high) all-gap LCA total 0 would reach the catalog | process.yaml `lca: {source: none, notes: ...}` until a background is linked (the catalog builder reads lca/ only with `auto`); the core/tooling behaviour (an all-gap `total` row of 0) recorded in D-011 as a finding to report. Closed. | d4740fd |
| #2 (medium) boundary labelled two ways | `cradle-to-gate` kept in lca.yaml; DESIGN.md (header, memo now "plant boundary (battery limits)", D-013), process.yaml summary and notes, lca.yaml comment and goal say "cradle-to-gate study, foreground inventory only, every background a gap". Earlier PROGRESS rows left as written (log). Closed. | d4740fd |
| #3 (medium) known omissions not declared | lca.yaml: `emission_exclusions` fugitive-leaks (not estimated, not claimed negligible, I-10) and no-process-effluent (dry vacuum pump on C-203, ASSUMED, D-008); `cutoff` C-203 vacuum power and small-pump power, each ~15 kW (ASSUMED); outputs rewritten, `--coverage` lists all four. "No wastewater" qualified on the vacuum choice in the memo and D-008. Closed. | d4740fd |
| #5 (low) reaction heat unit slip | D-005: "~1.95 MW (7.0 GJ/h), i.e. 2.3 %". Closed. | d4740fd |
| #6 (low) implicit pumps | noted on S17 and S23 (`source`) and in D-010; the P-101 count from 30 kPa(a) is stated as an over-estimate under 1 kW that stands in for the distillate pump; steps to add once the core Pumping bug (D-011) is fixed. Closed (the "note" option of the proposed action). | d4740fd, 462bacc |
| #8 (low) gas-basis LHV | kept, reason in lca.yaml and D-013 (same basis as the fuel gas; a liquid basis moves benzene's share by ~0.2 points). Closed. | d4740fd |
| #10 (low) LCA publication vs manifest | explained in D-013: the LCA field is cheme's source-licence verdict (may be published); process.yaml `publication.status: internal` governs. Closed. | d4740fd |
| #11 (low) docstring | corrected to the arriving feed enthalpy. Closed. | 462bacc |
| #4 (medium) Douglas values recalled, not read | open: needs the book at its locator (I-06); not verifiable in this run, the values stay labelled recalled/unsourced. | - |
| #7 (low) PFD symbols, core bug unfiled | open: filing the core issue is an outward action for a maintainer; D-011 describes the bug. | - |
| #9 (low) fuel-gas credit side by side | open: only meaningful once backgrounds are linked (I-11). | - |
| #12 (low) layout-plot-plan gate fails | open: the plot plan is a later layout run, before any concept sign-off. | - |

Follow-up (2026-10-27, after PR #189 CI failed): the exported default allocation is now energy (LHV) with `allocation.deviation`; substitution and mass are computed for comparison (D-013). #8 and #10 still hold as answered (energy share of benzene 71.5 %). #9 stays open but `results.md` now lists energy (used), mass and substitution side by side, the substitution row "not applicable" until its backgrounds exist. #1 re-checked: process.yaml `lca.source: none` unchanged. Commit 6a30bc4. Re-run: `cheme check` (design-review now stale: changed since 9af76cf, needs a new independent review; layout, P&ID and datasheet gates fail as before), `cheme maturity` (level none, claim concept, as recorded in the review), `cheme process streams` (every step balanced), `cheme assess lca --coverage` (partial screening, 8 gaps, all omissions declared).

## 2026-11-01 First DWSIM simulation (D-014)

`cheme process simulate --fill` (core v1.2.1, DWSIM 9.0.5, Peng-Robinson) of the whole plant converged (11 iterations, tears S9, S15, S23). The script's assumed stream values and duties are now calculated, except C-201's Q5/Q6 and the design targets (S21 flow and purity, feed values). R-101 is given as two toluene-keyed reactions (HDA, HDABP), the same extents as the D-005 selectivity. C-202 uses R = 1.3 x DWSIM's Rmin (2.18). C-203 is rigorous. The deviations that stay (implicit-pump pressures, S21 subcooling, C-201 off-gas temperature) are listed in D-014. Then `cheme process propagate --fill`, `cheme assess lca --write`, `cheme process build`, `cheme fmt`, `cheme validate` (0 errors), `cheme maturity` (level none as before; `predictive.property-regime` fails: package not qualified, core#315).

## 2026-11-02 IDAES cross-check of the feed section (D-015)

IDAES backend (core v1.4.0 + core#124): M100 + P101 converged with IDAES ideal VLE on the pre-merge flowsheet (commit 118c0de7; IPOPT optimal, 3 iterations), after the root cause of the earlier non-convergence was fixed in core#124 (smooth VLE had no solution for the pure-toluene liquid S1; BT_ideal liquid heat capacities read 1000x too small). Deviations against the script and DWSIM in D-015 (S3 +1.17 K, pump rise neglected by the script; Q1 -2.7 %, different suction pressure). After merging D-014 the plant's simulation is DWSIM's; IDAES now refuses every boundary because DWSIM's S23 carries biphenyl traces. Peng-Robinson in IDAES still does not converge on S1.
