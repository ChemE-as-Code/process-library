---
topic: design
reviewed_commit: 589e80f152763e10369e68452d66b696353e18ea
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/BFD.xml, process/PFD.xml, equipment/equipment-list.yaml, piping/line-list.yaml, lca/, runs/20261028-150703-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/acetic-anhydride-1
merge: pending
---

# Independent review: acetic anhydride (ketene route), concept PFD and preliminary LCI

Issue #131. Branch `case/acetic-anhydride-1`, commits 630dc55..589e80f (5 commits). The
reviewer did not write the design. No design file was changed by this review.

## What was re-run (2026-10-28, at 589e80f)

- `git diff --name-only origin/main..HEAD`: every one of the 190 changed files is under
  `processes/acetic-anhydride-1/`. Nothing outside the folder changed.
- `cheme validate`: 16 files, 0 errors, 0 warnings. One info names D-023, cited in
  `checks/checks.yaml:76` but missing from DESIGN.md (R-09). No P&ID exists, so the
  list-vs-P&ID cross-checks were skipped.
- `cheme check`: every concept gate passes except `layout-plot-plan` (no layout; out of scope
  for this issue). The basic gates `process-basic`, `process-links`, `pids-valid` and
  `drawing-clean` pass. `pids-exist`, `design-review` (this record), layout, MTO, datasheets,
  electrical and HVAC fail, as expected for a concept case.
- `cheme maturity`: calculation maturity **none**. `sourced.boundary` fails (the feed flows
  are ASSUMED script outputs) and `balanced.model-basis` fails (separator splits and absorber
  conversions are ASSUMED). The process.yaml claim `concept` triggers the warning
  `cheme.maturity-claim-exceeds` (see R-03).
- `cheme process streams`: all 4 blocks and 16 steps close. Plant total 14 892 kg/h in and
  out (7786.1 + 9.72 + 1.82 + 250.4 + 6844.0 in; 6250 + 51.95 + 1192.5 + 7397.7 out).
- `cheme process propagate --check`: no output, exit code 0 (no stale or deviating calculated value).
- `cheme assess lca --coverage`: partial screening carbon footprint. Mass, element and
  carbon-origin balances closed. 14 gap rows: the 11 `missing:` backgrounds, each with a
  description, plus 3 zero-amount uncharacterised emissions. Publication: publishable.
- Rendered `process/PFD.xml` (generated). It is readable and `drawing-clean` passes.

## Plausibility checks (reviewer's own hand calculations)

- **Product**: S19 is 0.99153/0.00847 mol, i.e. 99.5/0.5 wt%, and 6250 kg/h = 50 kt/a at 8000 h. Correct.
- **Acid consumption**: 1.246 kg/kg, against 1.175 kg/kg theoretical for 99.5 wt% product
  (2 AcOH per Ac2O). That is about 94 % overall yield on acid, consistent with 92 % ketene
  selectivity on the cracking half and about 99 % elsewhere. Plausible.
- **Cracker**: 80.8 kmol/h acid to the coil. CRACK 65.12, DECARB 2.71 and KETDEC 1.357 kmol/h
  give 84 % conversion and 0.92 net ketene per mol converted, which reproduces SRC-1. The coil
  duty is 4544 kW. My estimate is about 4.6 MW: about 2.7 MW reaction enthalpy at about
  142 kJ/mol, about 1.3 MW sensible heat 367 to 973 K, and about 0.6 MW dimer dissociation.
- **Dilute acid**: S12 is 39.5 wt% acid, against 38 wt% in SRC-1.
- **Firebox**: natural gas about 3.48 MW LHV plus vent gas about 1.49 MW LHV is 4.96 MW fired,
  so 0.915 efficiency. That matches a 145 K stack rise at 15 % excess air (about 6.6 % stack
  loss) plus 2 % radiation. The high efficiency is consistent with the stated stack
  temperature but implies a convection section that is not described (DESIGN I-05 already says so).
- **Direct CO2**: 15.61 kmol/h CH4 from natural gas plus 12.10 kmol/h carbon in the vent gives
  27.7 kmol/h, i.e. 1219.6 kg/h or 0.195 kg/kg. Matches the inventory.
- **Utilities**:
  - E-101: about 0.72 MW estimated, 731 kW in the flowsheet.
  - C-201: (R+1)·D·ΔHvap plus feed heating gives about 0.70 MW; flowsheet 686 kW.
  - C-202: 2·6250 kg/h × 0.40 MJ/kg gives 1.39 MW; flowsheet 1370 kW.
  - K-301 isothermal work at 0.35 efficiency gives 33.3 kW. P-301 gives about 31 kW at 100 kg/kg ketene.
  - All reproduced within a few percent.
- **Line sizes**: DN300 (S6, 20 m/s), DN600 (S7, 30 m/s), DN350 (S11) and DN40/50 liquids
  reproduce from the stated velocities.
- **LCI per FU**: every amount in `lca/inventory.csv` equals the stream or duty sum divided by
  6250 kg/h (AA, TEP, NH3, NG, POWER, LPS, MPS, CW, BRINE, RESIDUE, WW, CO2 checked).
  `lca/factors.yaml` holds no project factors, and the only characterisation is the packaged
  IPCC GWP100. No licensed values were found. `lca/mappings.yaml` exists and is empty on
  purpose; it lists the candidate shared entries.
- **Sources**: SRC-1 and SRC-2 carry section-level locators in DESIGN.md and in the
  `source:` fields. The facts are restated in the authors' own words. No table, figure or
  passage is copied. Ullmann is listed as unread and is not used.

## Findings

Ids follow `reviews/README.md` (`<record>#<n>`). R-nn in the item column is the short name the
text uses: R-01 is `#1`, and so on.

| id | file / line | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | lca/lca.yaml:63-69; lca/dataset.yaml:481-486 (and CH4, C2H4, KET entries); lca/inventory.csv | R-01 emission:CO, CH4, C2H4, KET | The published dataset carries CO, CH4, ethylene and ketene to air as `amount: 0.0`, `provenance: calculated`. `emission_exclusions: furnace-pollutants` in the same file says these are *not estimated, not claimed negligible*. A dataset user sees a calculated zero, not a gap. The zero is an artefact of the complete-combustion model (D-010), not a calculation of the emission. | medium | open | Drop the four zero-amount elementary flows from `flows:` (the exclusion already covers them), or keep them only once I-05 gives a sourced estimate. If the Atlas build needs them, mark them as not estimated rather than `calculated` 0. Regenerate with `cheme assess lca --write`. |
| 2026-10-28-pfd-lci-review#2 | process/flowsheet.yaml (V301 vent S15); equipment/equipment-list.yaml; DESIGN.md D-007 | R-02 absorber vent / K-301 | The balance sets acid and anhydride vapour in the absorber vent to zero. At 25 kPa(a) and 45 °C over 88 wt% crude, saturation is roughly 2 kPa of organics: about 8 mol% of the vent, of order 50-70 kg/h or about 1 % of product. SRC-2 gives 10-60 wt% for an unscrubbed vent. The design therefore depends on a vent scrubber, or on returning the seal fluid, that is in no flowsheet step, equipment item or line. I-03 records the issue but not the missing item. | medium | open | Add a vent scrubber, or a K-301 seal-fluid return, as a step and equipment item (ASSUMED recovery). Alternatively, carry the vapour loss in S15/S17, so that the acid consumption and the vent-carbon CO2 include it. State the sensitivity in D-007. |
| 2026-10-28-pfd-lci-review#3 | process.yaml:32-45 (`maturity`, `validation.notes`) | R-03 maturity claim | `cheme maturity` gives calculation maturity **none**, and the `concept` claim raises `cheme.maturity-claim-exceeds`. `concept` is the lowest enum value, so the claim itself is unavoidable. However, `validation.notes` does not say that the evidence supports no level (sourced.boundary and balanced.model-basis fail). The report says it; the catalog-facing manifest does not. | medium | open | Add one sentence to `validation.notes`: "cheme maturity: calculation maturity none (feed flows and separator/absorber specifications ASSUMED); concept is the lowest claimable level." |
| 2026-10-28-pfd-lci-review#4 | process/flowsheet.yaml:204 | R-04 R101 selectivity | The sourced SRC-1 values (conversion 0.84, ketene 0.92) and the ASSUMED CH4 split share one `provenance: assumed` record. The provenance therefore understates the sourced part, and `balanced.model-basis` cannot credit the cracking coil. | low | open | Give the conversion and ketene selectivity `provenance: given` with source "US 4,455,439, Example". Keep the CH4/decomposition split assumed, e.g. in a separate per-reaction spec, if core 0.8.0 allows it given the bug in D-012. |
| 2026-10-28-pfd-lci-review#5 | DESIGN.md D-009; process/flowsheet.yaml Q12 | R-05 C-401 steam | 3.0 MJ LP steam per kg water (979 kW) is unsourced. It is the largest assumed energy item (about 26 % of steam). No range or sensitivity is given, and an azeotropic dehydration of 40 wt% acid can be well above this figure depending on whether extraction comes first. Already open as I-02. | low | open | Give a range from an open source (patent or review on extraction plus azeotropic dehydration of dilute acetic acid), with a locator, or state the LCI's sensitivity to ±50 %. |
| 2026-10-28-pfd-lci-review#6 | equipment/equipment-list.yaml:20-21, 17-18, 33 | R-06 E-102, F-101, K-301 | E-102 is SS316L at a 725 °C design temperature; 316L is not normally rated that hot, and the hot end needs a high-temperature grade or a separate quench/first cooler. F-101 has a 750 °C design, only 50 K above the fluid outlet; the tube metal of a fired coil runs hotter. K-301, a liquid-ring vacuum pump, is typed `CentrifugalCompressor`. All are ASSUMED concept values. | low | open | Split E-102 into a hot-gas cooler (high-temperature alloy) and the CW/brine condensers, or note the hot-end grade as open. Base the F-101 design temperature on tube metal temperature. Use a fitting type for K-301, or note the substitution. |
| 2026-10-28-pfd-lci-review#7 | process.yaml:60; lca/lca.yaml (product:BRINE) | R-07 BRINE slug | -10 °C brine is listed under the registry slug `chilled-water`, a warmer service with a higher COP. If the Atlas ever links by slug, as it does for CW and WW (D-014), it would understate the refrigeration burden. | low | open | Drop the slug and keep the note "no registry entry for -10 °C brine", or add a refrigeration entry. |
| 2026-10-28-pfd-lci-review#8 | process.yaml:42; DESIGN.md D-014; lca/gaps.csv | R-08 gap counts | The manifest says 11 gaps, D-014 says 10 (library build) and `lca/gaps.csv` has 14 rows (11 missing plus 3 uncharacterised zero emissions). Each count is right for its own tool, but a reader cannot reconcile them. | low | open | State which count is meant, e.g. "11 unmapped backgrounds (lca/gaps.csv also lists 3 uncharacterised zero emissions; the library build reports 10 because CW/WW link by slug)". This resolves together with R-01. |
| 2026-10-28-pfd-lci-review#9 | checks/checks.yaml:76 | R-09 D-023 | A commented-out example in the template's checks file cites D-023, which this DESIGN.md does not have (`cheme.decision-unknown`, info). It comes from the scaffold, not from the design. | low | open | Remove the example comment, or reword it so it no longer cites a decision id. |

No critical or high findings. The route (acetic acid cracking with TEP, NH3 neutralisation,
reactive absorption, two-column distillation, dilute acid recovery) and the boundary (acetic
acid as a boundary feed, no blending with carbonylation data) match issue #131. The mass,
component and element balances close. Key values are sourced or marked ASSUMED, and every
unmapped background is a described gap, not a zero. Energy closure is evaluable only in
`scripts/ac2o_balance.py` (core #315), which is honestly stated.

## Previous findings

None (first review of this case).
