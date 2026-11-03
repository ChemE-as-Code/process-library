---
topic: design
reviewed_commit: 347a0e119a18e17b7e6af70f50f0de3b38a18647
scope: [DESIGN.md, PROGRESS.md, runs/plan.md, equipment/equipment-list.yaml, estimate/, layout/site-plan.yaml, layout/equipment-placement.yaml, layout/plant-model.yaml, process/BFD.xml, process/PFD.xml, process/flowsheet.yaml, process/simulation.yaml, scripts/concept_sizing.py]
reviewer: review-agent
reviewer_kind: agent
branch: stage/hda-1-concept-closeout
merge: pending
---
# Review: design (concept close-out of hda-1, PR #320, re-review round 1)

Independent re-review of PR #320 (issue #302) at 347a0e1, after the fix commits 1f55357,
7276a96 and 347a0e1 that answer the panel's round-1 findings. Re-run by the reviewer with
core v1.4.1 at 347a0e1:

- `cheme validate`: 23 files, 0 errors, 4 warnings. The warnings are `pydexpi_composition_fractions`
  on S19, S20 and S22 in the BFD and PFD. The same 4 warnings appear on `origin/main` (f5af999),
  so this PR did not introduce them (see #17).
- `cheme check --stage concept`: every concept gate passes (design-basis, concept-lists,
  process-concept, process-balances, process-links-concept, assumptions-marked, layout-plot-plan;
  issues-concept n/a).
- `cheme maturity`: calculation maturity none, claim concept exceeds it. This is the same on
  `origin/main`. The failing requirements (sourced boundary, R101 model basis, property regime)
  belong to S2 (gate maturity-balanced) in runs/plan.md (see #17).
- `estimate/tea.md` was read against D-019. LCOP is 880.9 EUR/t, and the decision turns at a
  toluene price of 501.1 EUR/t. The scenario NPVs for 2019 to 2025, the Spearman coefficient of
  +0.93 and the class 5 high case of 908.6 EUR/t all match the D-019 table. The steam CO2 factor
  was recomputed and holds: 3.6/0.90 x 802.7/890.7 x 0.0561 = 0.2022 t/MWh. Total CO2 is
  14.5 kt/a. The methane conversion was also recomputed and holds: 890.7/16.0425 = 55.521 MJ/kg.
- core#129 (correlated prices, multi-component sources in the report, fired-heater factors,
  drive correlation) and process-library#321 (the ammonia-1 citation of the heat of combustion)
  exist and are open.
- Plot plan: `build/layout-plan.svg` holds all 18 equipment tags and the 5 area tags. The reviewer
  tried to view it in a browser, but the Playwright navigation timed out. The author's viewing
  note in D-018 therefore stands on the author's own check, and the geometry rests on the gate
  and on the distances measured with `cheme show`.

Verdict: **approve**. No critical or high finding is open, and every concept gate passes. The
concept sign-off itself is for a person, not for this review.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-03-concept-closeout#1 | equipment/equipment-list.yaml | C-201 | The note said "38 theoretical stages", copied from C-202. D-017 and the sizing script use 8 ASSUMED stages. Now: "8 theoretical stages ASSUMED (the DWSIM shortcut gives 3.0 ...)". The grep finds no other copied stage note: C-202 has 38 and C-203 has none. | medium | closed 1f553573 | - |
| 2026-11-03-concept-closeout#2 | estimate/tea.yaml, DESIGN.md D-019 | P(meets) | P(meets) sampled toluene against a fixed benzene threshold. The tea.yaml decision comment and D-019 now say it is not a spread probability and not the decision result. The core limit is stated precisely (no correlated price inputs, no threshold tied to a price key: core#129). Spread scenarios for 2019 to 2025 from the same DS-045409 flows are tabulated against the break-even. | medium | closed 7276a96f | - |
| 2026-11-03-concept-closeout#3 | DESIGN.md D-019 | spread proxy | D-019 now says that an import/export unit-value difference is not a traded spread and that one year is weak evidence. The multi-year series has been added, and the conclusion is worded as conditional on the proxy. | low | closed 347a0e11 | - |
| 2026-11-03-concept-closeout#4 | estimate/tea.yaml | carbon boundary | Steam is now charged with the site boiler's CO2: emission sources steam-boiler, steam-boiler-lp and steam-boiler-hp at 0.2022 t/MWh, checked. CO2 is 10.8 EUR/t of benzene. | low | closed 7276a96f | - |
| 2026-11-03-concept-closeout#5 | estimate/cost-basis.yaml, tea.yaml | H-101 factor | The 2.5 is kept ASSUMED. The printed Turton Appendix A tables could not be read, so the fix's stated alternative applies: the factor is stated as likely low for alloy tubes at 42 barg, and the missing package factors are filed as core#129. This is a valid carry. | low | open | take fbm, fp and fm from Turton Appendix A with the locator at the class 4 estimate (S5) |
| 2026-11-03-concept-closeout#6 | estimate/tea.yaml, cost-basis.yaml | K-101 drive | The uncovered allowance now names the explosion-proof motor of about 300 kW and its starter. The size_source says "shaft power (DWSIM duty)". | low | closed 7276a96f | - |
| 2026-11-03-concept-closeout#7 | layout/site-plan.yaml, DESIGN.md D-018 | H-101 spacing and wind | An H-101 to E-101 separation of 15 m is declared, and the measured 26.8 m passes. D-018 records the S to SW wind point for the layout review, together with I-05. It also says no openly readable spacing guideline with a locator was found. | low | closed 1f553573 | the wind-rose point stays in D-018 and I-05 for the layout review |
| 2026-11-03-concept-closeout#8 | estimate/tea.yaml | methane heat of combustion (hda-1) | Now cites the NIST WebBook value -890.7 +/- 0.4 kJ/mol (Pittam and Pilcher 1972, ID C74828). The conversion is 0.055521, and the LHV/GCV ratio is 802.7/890.7. Both were checked. | low | closed 7276a96f | - |
| 2026-11-03-concept-closeout#9 | estimate/tea.yaml | consumption bands | The site-total band premise is now stated in feed:POWER, feed:FUEL and D-019, and feed:POWER is now ASSUMED. | low | closed 7276a96f | - |
| 2026-11-03-concept-closeout#10 | DESIGN.md D-019 | 5.5 EUR/t precision | D-019 gives the like-for-like alternatives for 2025: +38.6 EUR/t for both imports and -134.7 EUR/t for both exports. Both are also run as scenarios, with NPVs of -128 and -280 MEUR. | low | closed 347a0e11 | - |
| 2026-11-03-concept-closeout#11 | estimate/tea.md, DESIGN.md D-019 | H2 source in report row | D-019 names the European Hydrogen Observatory source next to the feed:H2MU row. The renderer limit is reported in core#129. | low | closed 347a0e11 | - |
| 2026-11-03-concept-closeout#12 | DESIGN.md D-019 | contingency | D-019 now says that the 20 % is a class 4 contingency, low for class 5, and that the class 5 range covers the difference. | low | closed 347a0e11 | - |
| 2026-11-03-concept-closeout#13 | equipment/equipment-list.yaml | C-201 (integrity lens) | Same defect as #1. | low | superseded by 2026-11-03-concept-closeout#1 | - |
| 2026-11-03-concept-closeout#14 | equipment/equipment-list.yaml, DESIGN.md D-017 | E-101 second shell | The two shells are now stacked (ASSUMED), so the D 1.6 m x 9 m footprint covers both. The stacked height comes at layout-3d. The estimate (2 x 654 m2) and the layout are consistent. | low | closed 1f553573 | - |
| 2026-11-03-concept-closeout#15 | DESIGN.md D-018 | plot plan not viewed | The SVG was viewed by the author, and the observations are recorded in D-018. The reviewer confirmed that the SVG holds all 18 items. The reviewer's own browser view failed with a Playwright timeout, so the visual check is the author's. | low | closed 347a0e11 | look at the plan again at the layout review |
| 2026-11-03-concept-closeout#16 | estimate/tea.yaml | EUA source | The 74 EUR/t is still taken from a secondary report of ESMA's figure, labelled secondary and ASSUMED, and cross-checked against Instrat's 73.43 EUR/t. The fix allowed leaving it, and it does not move the decision. | low | open | cite the ESMA annual report on EU carbon markets, or the EEX auction results, with a locator at the next TEA revision |
| 2026-11-03-concept-closeout#17 | process/flowsheet.yaml, process.yaml | maturity and composition sums | This was not introduced by the PR (it is identical on origin/main). `cheme maturity` supports no design maturity against the concept claim, because of the sourced boundary on S1 and S4, the unsourced R101 conversions and the property regime. `cheme validate` also warns that the S19, S20 and S22 mole fractions miss 1 by up to 1.7e-4. | low | open | S2 (simulation close-out, gate maturity-balanced): source the feeds, the R101 basis (see #4 of 2026-10-27) and normalise the stream compositions |
| 2026-11-03-concept-closeout#18 | processes/ammonia-1/estimate/tea.yaml | methane heat of combustion (ammonia-1) | This is split from #8. ammonia-1 still attributes the ISO 6976 value of 890.63 kJ/mol to NIST. It is filed as process-library#321 and is outside this PR. | low | open | fix in process-library#321 |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-27-pfd-lci-review#4 | Douglas reactor-basis values recalled, not read from the book | medium | open | carried (D-016 I-06): no open copy or openly licensed source with a locator was found; `cheme maturity` fails maturity-balanced-model-basis for R101; for S2 |
| 2026-10-27-pfd-lci-review#7 | PFD symbols: H101 and P101 drawn as the wrong class (core build bug) | low | closed d5267c55 | P101 `Pumping`, H101 `HeatingInFurnace` with core v1.4.1; BFD/PFD rebuilt; validate has no generated-version finding |
| 2026-10-27-pfd-lci-review#9 | fuel-gas credit methods side by side | low | open | carried (D-016 I-11): needs linked LCA backgrounds, the LCA practitioner's decision |
| 2026-10-27-pfd-lci-review#12 | concept gate layout-plot-plan fails | low | closed ae80dcef | plot plan written (D-018); `cheme check --stage concept` passes layout-plot-plan |
