---
topic: design
reviewed_commit: b83cdb1162efcefdff297f582dde8bb7974d8b3c
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, scripts/balance.py, lca/lca.yaml, lca/mappings.yaml, equipment/equipment-list.yaml]
reviewer: review-agent
reviewer_kind: agent
branch: case/thionyl-chloride-1
merge: pending
---

# Independent review: thionyl-chloride-1 concept PFD and preliminary LCI (issue #138)

This review covers the concept stage of `processes/thionyl-chloride-1/`: route and boundary,
design basis, balanced BFD/PFD, the balance script and the preliminary gate-to-gate LCI.
The design agent wrote all of it in run `20261028-161945-design`. I did not change any design
file.

## What was re-run (at b83cdb1)

| command | result |
|---|---|
| `cheme validate` | 16 files, 0 errors, 0 warnings. Infos: `cheme.decision-unknown` D-023 is a template comment in checks/checks.yaml, not a design reference; dexpi.load cycle notes |
| `cheme check` | concept gates: design-basis, concept-lists, process-concept, process-balances, process-links-concept and assumptions-marked are ok. layout-plot-plan fails (layout is out of scope in the brief). At basic: design-review fails until this record exists; the P&ID, layout, datasheet and electrical gates fail (out of scope) |
| `cheme maturity` | calculation maturity none; `cheme.maturity-claim-exceeds` warning on the claim `concept` (process.yaml:39). The sourced level fails on assumed feeds and on unsourced specified conversions (R101, R102, the R201 node conversion, V201, T201, T301, T401) |
| `cheme process streams` | all 5 blocks and 20 steps ok. The largest residual is 0.02 kg/h (REACT/R201, 7554.64 in, 7554.62 out) |
| `cheme process propagate --check` | no deviation reported |
| `cheme assess lca --coverage` | mass, element and carbon-origin balances closed. 15 gaps: 10 unmapped backgrounds, each with a description, and 5 air emissions with no GWP factor. No climate total ("every contribution a gap"). Publishable |

## Independent checks (mine, not the report's)

- **Scope and boundary.** The route is continuous SCl2 + SO2 + Cl2 over activated carbon,
  followed by distillation. The sulfur chlorides are made inside the boundary from S and Cl2,
  which is justified in D-001 because the still bottoms must be rechlorinated anyway. This
  matches the case notes of the brief and issue #138, which leaves the route open.
- **Changes outside the folder.** Against the merge base cc5624f, nothing outside
  `processes/thionyl-chloride-1/` changed. The `thf-1 => thionyl-chloride-1` renames in
  `git diff origin/main..HEAD` come from `processes/thf-1` being added on main after the branch
  point. They are not deletions made by this branch.
- **Stoichiometry and yields.** Per kg of product: S 0.1357, SO2 0.2738, Cl2 0.5980 kg. The
  stoichiometric minimum is 0.1348, 0.2692 and 0.5960 kg, counting the Cl and S in the 0.3 wt%
  impurities. The excess is explained by the 1 % purge, which loses 1.9 % of the SO2.
  - O2 balance: 0.1 mol% of the Cl2 feed is 1.01 kg/h O2, which equals the O2 in the vent
    (S43). This closes.
  - Scrubber NaOH: 1.2 x (2 SO2 + 2 Cl2 + 4 SOCl2) ≈ 0.99 kmol/h, which matches S40 at
    79.15 kg/h of 50 wt% caustic.
  - Scrubber reactions (thiosulfate and sulfite) are element- and redox-balanced.
- **Utility sums against the energy streams.**
  - LP steam Q3+Q4+Q5+Q9+Q13 = 1582.5 kW
  - cooling water Q1+Q2+Q6+Q7+Q12 = 1880.6 kW
  - brine Q8+Q10 = 444.7 kW
  - power = 17.68 kW
  
  Each total equals its LCI exchange (0.422, 0.501, 0.119 and 0.0047 kWh per kg).
- **Plausibility checks by hand.**
  - Heat of SOCl2 synthesis from textbook gas formation enthalpies: about -108 kJ/mol, against
    -110.6 kJ/mol in reactions.yaml.
  - R101 duty from the formation of liquid S2Cl2 plus sensible heat: about 89 kW (91.3 kW in the
    flowsheet).
  - R102 duty: about 135 kW (127 kW).
  - K-201 power (2.77 t/h, 125 -> 180 kPa, isentropic efficiency 0.70, motor 0.95): about
    15 kW (15.16 kW). Outlet temperature about 296 K (293.6 K).
  - T-201 reboiler: about 475 kW (465 kW).
  - T-301 condenser at reflux ratio 2: 740-830 kW, depending on the SOCl2 latent heat
    (737 kW).
  - Vapour feed S12 and mixed feed S14 are above their dew points; the reactor inlet ratios
    reproduce the stated 2.0 x SO2 and 1.05 x Cl2 excess.
  
  All values are inside concept accuracy.
- **Model honesty.** The patent per-pass conversion (75 %, DE2430631A1) is carried as an
  empirical given value, not a prediction. D-005 states openly that the ideal-gas equilibrium
  would allow nearly full conversion. Gated steps (VLE, liquid enthalpies, electrolyte) are
  named precisely in D-006 and the method table.
- **LCI.**
  - Per 1 kg of S31. Inputs 1.11300 kg = outputs 1.11300 kg, consistent with the flowsheet
    (S1+S2+S3+S40+S41 against S31+S43+S44).
  - No zero-filled or licensed background: every background is `missing:` with the activity it
    should connect to, and gaps.csv lists all 15.
  - `lca/mappings.yaml` is empty with a stated reason; nothing was added to the shared
    `lci/mappings.yaml`. The missing shared-registry entries are listed in D-013.
- **Licences.** DESIGN.md and the `source:` fields restate facts in their own words, with
  patent identifiers. I found no copied passages, tables or figures.
  Ullmann (licensed) is marked as not read.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | process/flowsheet.yaml:389 (S22); DESIGN.md D-007; scripts/balance.py:208 | T-201 / T-301 | **R-01.** The degasser removes SO2 and Cl2 completely (sharp split), but its bottoms condition conflicts with the plant's own Raoult model. At 345 K the lights-free crude (82 mol% SOCl2, 18 mol% SCl2) has a bubble pressure of only about 100 kPa, below the 125 kPa column pressure. By Raoult, about 1.5-2 mol% SO2/Cl2 (some 30-50 kg/h) would stay in S22. T-301 has no lights outlet or vent, so these lights would end up in the distillate, which conflicts with the 99.7 wt% product (D-002). Balances still close, but the purification as modelled is not consistent with its stated basis. | medium | open | Either set the T-201 bottoms at or above the crude bubble point at 125 kPa (about 352 K) and recompute Q9, or carry a residual SO2/Cl2 in S22 and give T-301 a lights vent back to M-202 or to T-401. State the choice in D-007 and D-008. |
| 2026-10-28-pfd-lci-review#2 | runs/20261028-161945-design/report.md:20 | plant balance | **R-02.** The run report gives the plant mass balance as "3805.00 kg/h in against 3804.99 kg/h out (product plus purge)". The flowsheet gives S1+S2+S3 = 3778.01 kg/h against S31+S25 = 3778.00 kg/h. The balance does close; the report's figure is wrong. Run records may not be edited. | low | open | Record the correct figure in PROGRESS.md, or in the next run's report. Do not edit the run record. |
| 2026-10-28-pfd-lci-review#3 | process/flowsheet.yaml:247; process/reactions.yaml:43 | R-201 | **R-03.** The cheme conversion reactor applies 75 % to the SCl2 entering R-201 only; SCl2 formed in the reactor from S2Cl2 passes through unconverted. The effective per-pass conversion of all SCl2 is therefore about 68 % (0.157 / 0.231 mol per mol feed). That is still inside DE2430631A1's 50-80 %, but not the 75 % that D-005 and process.yaml imply. Separately, the node-level `conversion: {SCL2_FORM: 0.95}` has no provenance, and `cheme maturity` reports it as such. | low | open | Add one sentence to D-005 on the effective conversion. Give the node conversion `provenance: assumed` and a `source` (D-005), as reactions.yaml already does for the others. |
| 2026-10-28-pfd-lci-review#4 | process.yaml:39 | maturity | **R-04.** `cheme maturity` warns `cheme.maturity-claim-exceeds`: the evidence supports no design maturity, yet `concept` is claimed. `concept` is the lowest value in the schema enum, and validation.notes already say "cheme maturity reaches no level", so a reader is not misled. | low | open | Keep the claim. Name the warning id in validation.notes, so the Atlas reader sees that the claim is the schema floor and not an evidenced level. |
| 2026-10-28-pfd-lci-review#5 | process/flowsheet.yaml:376-377 (S10, S11); DESIGN.md D-004/D-006 | R-101 / R-102 | **R-05.** The O2 from the chlorine is carried dissolved in the liquid chlorinator outlets (0.03-0.06 mol%), while D-006/D-007 treat O2 as insoluble elsewhere. Real liquid-phase chlorinators need an off-gas vent for inerts and unreacted Cl2. The overall balance is unaffected, since the O2 reaches the same purge either way. | low | open | Note the simplification in D-004. Show a chlorinator vent (to K-201 suction or T-401) when the P&IDs are drawn. |
| 2026-10-28-pfd-lci-review#6 | DESIGN.md D-010, Open inputs | heat integration | **R-06.** Several duties in the utility inventory could largely be avoided, so the LCI utilities per kg sit at the upper end. The crude is chilled to 263 K on brine and then reheated by steam in T-201 (465 kW) with no feed/bottoms exchanger. Liquid SO2 at 298 K is vaporised with 425 K LP steam (104 kW). The reactor heat at 473 K (387 kW) goes to cooling water. Only the reactor-heat option is listed as open. | low | open | List the crude/degassed-crude interchange and the SO2 vaporiser on cooling water or recovered heat as open heat-integration items in D-010. Optionally add an LCI scenario. |
| 2026-10-28-pfd-lci-review#7 | DESIGN.md source register; process.yaml references | SRC-1..SRC-6 | **R-07.** The patent locators are coarse ("description", "abstract"). SRC-4 and SRC-5 were read at abstract or search-summary level only, yet support cross-checks in D-007 and D-008; this is labelled honestly. process.yaml calls Ullmann "not read in full", while DESIGN.md says "not read". | low | open | Where the text allows, add column or example numbers. Align the Ullmann wording to "not read". Before any value comes to rest on SRC-4/5 alone, read their full text. |
| 2026-10-28-pfd-lci-review#8 | lca/lca.yaml:70 | LCI dataset | **R-08.** `--coverage` infos: emission:H2O and emission:O2 have no receiving compartment, Cl2/SOCl2/SCl2/S2Cl2 have no flow identity, and the dataset has no CPC class. The cut-off flows (activated carbon, iron) have no amount, so the 1 % rule cannot be checked. All of this is disclosed (D-012, D-013) and does not affect the inventory. | low | open | Give the free flows `elementary.compartment: air`. Add the CPC class. Carry the flow identities in the consolidated shared-files PR (D-013). |

No critical or high findings. The balances close and the LCI is consistent with the flowsheet
and honestly gapped. Sources are cited and assumptions are marked.

## Merge

Merge pending: a human or the reviewer merges `case/thionyl-chloride-1`, not its author. No
stage sign-off is part of this review.
