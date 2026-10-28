# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | DESIGN.md | D-013: the gates outside #145's scope recorded; no sign-off claimed | review 2026-10-28-pfd-lci-review #11 |
| 2026-10-28 | lca/ | Each `missing:` names the activity to connect; emission:I2 subcompartment non-urban-high-stack (origin noted as core limitation); melter-vent exclusion with an HCl upper bound; `cheme assess lca --write` rerun | review 2026-10-28-pfd-lci-review #2, #8, #5 (partly) |
| 2026-10-28 | DESIGN.md, process.yaml, process/design-basis.yaml, equipment/equipment-list.yaml | Air-ratio check restated as a fresh-water upper bound with I2Cl- named, gated and a 2x sensitivity (D-005, D-007); 90 % recovery labelled as calibrated to SRC-3, not a check; SRC-2 as US Bureau of Mines; SRC-5 pH wording; M-301 design 175 °C; T-202 wetting-rate check; M301 listed as specified | review 2026-10-28-pfd-lci-review #1, #3, #4, #6, #9, #10 |
| 2026-10-28 | lca/mappings.yaml | Override `feed:LPS: use steam-heat` (steam counted as heat delivered, kWh) | PR #233 CI: the library Atlas build mapped the `steam` slug (per kg) to the kWh exchange and refused the unit (tests test_export_formats, test_utilities) |
| 2026-10-28 | lca/ | Preliminary gate-to-gate LCI: lca.yaml (FU 1 kg iodine, backgrounds unmapped with the activity to link), mappings.yaml (no overrides yet), inventory/gaps/dataset written; LCI mass and element balance closed | #145 scope step 4 (D-011) |
| 2026-10-28 | process.yaml, DESIGN.md | Atlas manifest (internal, concept, unreviewed), source register, basis and method tables, D-001..D-012, missing registry entries | #145 scope steps 1, 3, 5 |
| 2026-10-28 | process/, equipment/ | Design basis, materials, reactions, flowsheet (4 blocks, 11 steps, 24 material streams, air-loop and acid recycles), BFD/PFD built, equipment list; all balances close | #145 scope steps 1, 2 (D-001..D-010) |
| 2026-10-28 | all | Scaffold from cheme init and the process template | start of #145 |

## Responses to review 2026-10-28-pfd-lci-review

The review had no critical or high finding. Medium findings #1-#3 are closed, as are the quick
low ones; #5 is answered in part and #7 is left open. The review record itself is not edited.
The closing statuses are for the next reviewer to confirm.

| finding | response | commit |
|---|---|---|
| CI (PR #233) | library tooling tests failed: the Atlas build mapped feed:LPS (kWh) through the `steam` slug (kg). lca/mappings.yaml overrides it with `steam-heat`; the library test suite passes locally (412 passed) | 71b74c3 |
| #1 (medium) | D-005 no longer calls the air ratio conservative: the Henry check is a fresh-water upper bound, I3- and I2Cl- complexation named (the I2Cl- constant unsourced), air ratio gated with T-201 in D-007, K-201 at 2x the air ratio as a sensitivity (about 200 kW, +0.8 kWh/kg); basis table updated | d4d0a34 |
| #2 (medium) | every `missing:` in lca/lca.yaml names the activity to connect; gaps.csv, results.md, dataset.yaml rewritten by `cheme assess lca --write`; D-011 wording aligned | 0db31f0 |
| #3 (medium) | 90 % recovery is labelled as calibrated to SRC-3, not a check, in the process.yaml validation notes, design basis, DESIGN.md basis table and D-006 | d4d0a34 |
| #4 (low) | M-301 design temperature 175 °C (steam saturation about 148 °C plus margin), jacket design pressure noted; D-010 rule states the heating medium | d4d0a34 |
| #5 (low, partly) | melter-vent exclusion gives an HCl upper bound (all of S17's HCl, 0.46 kg/h, 3.7 g/kg). Still open: the iodine bound needs the vent flow, and the lca schema's emission exclusion has no amount field, so `cheme.lca-cutoff-unchecked` stays | 0db31f0 |
| #6 (low) | SRC-2 cited as US Bureau of Mines, Minerals Yearbook 1987 (from a search-result extract) in process.yaml and the design basis; SRC-5 pH wording corrected | d4d0a34 |
| #7 (low, open) | paragraph or line locators need the patents read again at paragraph level. That was not done in this run, and locators that were not checked against the text would be guesses | - |
| #8 (low) | emission:I2 given `subcompartment: non-urban-high-stack` (ASSUMED); the meaningless default carbon origin noted as a schema/core limitation. Still open in core: the crosswalk has no I2 identity | 0db31f0 |
| #9 (low) | T-202 wetting-rate check recorded in D-005 and the equipment list note, for when T-202 is sized | d4d0a34 |
| #10 (low) | DESIGN.md method table lists step M301 as specified (script values) and names the `cheme maturity` misreport as a core inference. The report to core is outside this folder and is not filed | d4d0a34 |
| #11 (low) | D-013 records the gates outside #145's scope and that no sign-off is claimed; a human decides on acceptance | 39f620f |
