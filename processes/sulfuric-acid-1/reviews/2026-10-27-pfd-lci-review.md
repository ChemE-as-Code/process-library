---
topic: design
reviewed_commit: e19030be935b4d766c506ca290c3e4dba9b008e3
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/materials.yaml, process/reactions.yaml, process/simulation.yaml, scripts/balance.py, equipment/equipment-list.yaml, lca/]
reviewer: review-agent
reviewer_kind: agent
branch: case/sulfuric-acid-1
merge: pending
---

# Independent review: concept PFD and preliminary LCI of sulfuric-acid-1 (issue #175)

Reviewer: independent review agent; did not author the design. Branch `case/sulfuric-acid-1`,
5 commits on `origin/main` (75090ab..e19030b). Review of the design basis, balanced BFD/PFD
and the gate-to-gate LCI; P&IDs and layout are out of the run's scope (task.md) and not reviewed.

## What was re-run (results as observed, not taken from the run report)

| command | result |
|---|---|
| `git diff --name-only origin/main..HEAD` | every changed file is under `processes/sulfuric-acid-1/` |
| `cheme validate` | 18 files, 0 errors, 0 warnings (3 info; the D-023 info is a commented template example in `checks/checks.yaml:76`) |
| `cheme check` | all concept and process gates ok except `layout-plot-plan`; basic/detail gates fail for P&IDs, layout, datasheets and this review (expected at this scope) |
| `cheme maturity` | level none; warning `cheme.maturity-claim-exceeds` for the `concept` claim (R-05) |
| `cheme process streams` | every block and step closes; extents S_COMB 426.13, SO2_OX 424.85, SO3_ABS 424.83 kmol/h |
| `cheme process propagate --check` | no output (no deviation) |
| `cheme assess lca --coverage` | partial screening carbon footprint, 8 gaps, mass/element/carbon balances closed, energy closure 188.8 % (explained in D-013: utilities only) |

## Plausibility checks done by the reviewer (own arithmetic)

- Overall mass: in 13,663.9 (S) + 108,584 (wet air) + 7,010.9 (water) = 129,258.8 kg/h; out
  42,301.1 (acid) + 86,957.7 (stack) = 129,258.8 kg/h. Closed.
- Sulfur: 42,301 x 0.985 / 98.08 = 424.8 kmol/h H2SO4; / 0.997 conversion = 426.1 kmol/h S =
  0.323 kg S/kg acid, matches the stoichiometric 0.322 kg/kg plus the 0.3 % SO2 loss.
- Water: 0.181 kg chemically bound + 0.015 kg free per kg acid = 0.196 kg; air moisture at
  298 K / 60 % RH for ~3,700 kmol/h dry air is ~1.27 t/h = 0.030 kg/kg, leaving 0.166 kg/kg
  dilution water, as in S31.
- Air: 11.5 mol% SO2 -> ~8.7 mol dry air per mol S, ~107 t/h dry air; S1 108.6 t/h wet. Consistent.
- Main blower: 29.7 kg/s at 348 K (drying tower outlet), ratio 1.63, eta_s 0.80, motor 0.96 ->
  ~2.0 MW, matches 2.05 MW. Specific power 0.055 kWh/kg is in the usual range for DCDA plants.
- Bed 1: 11.5 % SO2 x 63 % conversion gives ~210 K adiabatic rise; 688 -> 899 K consistent;
  ln(Q/K) = -0.063 at 899 K is close to equilibrium as expected for the first bed.
- Interbed duties against gas-side sensible heat (Cp ~1.1 kJ/kg K): E-201H 6.56 MW (899 -> 713 K),
  E-202 3.0 MW (794 -> 708 K), E-203H + E-204 9.5 MW (735 -> 453 K), reheat 8.6 MW (348 -> 683 K)
  equals E-201C + E-203C. Consistent.
- Steam total: 43.6 MW / 56.7 t/h = 2,769 kJ/kg = h(4.1 MPa, 673 K) - h(BFW 378 K). Consistent
  in total; the split between exchangers is not (R-01).
- Energy per kg acid: S -> SO2 ~3.0 MJ, SO2 -> SO3 ~1.0 MJ, SO3 absorption ~1.3 MJ, blower
  0.2 MJ ~ 5.5 MJ in; steam 3.7 MJ + cooling water 1.8 MJ out. Plausible.
- SO2 to air: 0.003 x 0.323 x 64.07/32.06 = 1.94 g/kg; 99.9 % would give 0.65 g/kg. Correct.
- Steam export 1.34 t/t acid without acid heat recovery is at the upper end of, but within,
  what sulfur-burning DCDA plants are generally reported to export. Not compared with a
  sourced benchmark in the case (DESIGN.md section 4 says so honestly).

Licences: no web fetches appear in the run's session log; DESIGN.md, lca/ and process.yaml
contain no copied tables, figures or passages; sources are cited as facts. LCI: per 1 kg of
98.5 wt% acid, quantities equal the flowsheet streams divided by 42,301.1 kg/h, no zero-filled
or licensed background; every purchased input and the steam export is an explicit `missing:`
gap with the activity it should connect to.

## Findings

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-27-pfd-lci-review#1 | DESIGN.md D-008; process.yaml:54; design-basis.yaml:28 | E-202, E-204, E-205, HPS | The steam-side split cannot deliver the stated 673 K export. Superheating 56.7 t/h from saturation at 4.1 MPa (~525 K) to 673 K needs ~6.5 MW, but the only superheater, E-202, has 3.0 MW. The economisers give 14.2 MW where heating BFW from 378 K to saturation needs only ~10.3 MW, so about 4 MW of steam would be raised in them. The total heat (and so the LCI's 1.03 kWh/kg) is right, but process.yaml and the design basis state 673 K / 1.34 kg/kg as a result. D-008 flags it only as "not checked". | medium | open | Rebalance the steam side in `scripts/balance.py`, for example with a superheater after the WHB or bed 1 (and E-201 moved), or a lower export superheat. Until then, mark the 673 K in process.yaml and the design basis as an unchecked target. |
| 2026-10-27-pfd-lci-review#2 | process.yaml:15; DESIGN.md section 3-4 | R201-R204, T301, T302, T101 | The values that set the yield and emissions have no checked source. The bed conversions (63/87/95/99.7 %) come from Speight (2002) as summarised in a skill, which was not read and has no locator. SO3 absorption of 99.9 % per tower and complete drying are bare ASSUMED values. DESIGN.md says this; process.yaml's description ("within the ranges of Speight 2002") does not say the source is second-hand. | medium | open | Read Ullmann's (a25_635) or the LVIC-AAF BREF with locators for the per-bed conversion, overall conversion and absorption efficiency. Until then, say "as summarised in the skill, not checked against the source" in process.yaml. |
| 2026-10-27-pfd-lci-review#3 | DESIGN.md D-006/D-007; scripts/balance.py | E-301, product:CW | The heat of mixing of water into strong acid is neglected and the acid Cp is a constant 1.45 kJ/(kg K) (ASSUMED). Both bias the acid cooler duty, and so the LCI's 0.491 kWh/kg to cooling water, low by an unquantified amount. The drying-tower acid "leaving cooler than it enters" (D-007) is a symptom of this. | low | open | Use a sourced enthalpy-concentration correlation for H2SO4-H2O, or give a bound on the error in D-006 and the CW flow's `source`. |
| 2026-10-27-pfd-lci-review#4 | process/design-basis.yaml:44 | R-201 | The design basis gives bed inlets as 693/713/708/683 K. D-005, the flowsheet (line 415) and the script use 688 K for bed 1 (it was lowered to stay in the catalyst window). | low | open | Correct to 688 K. |
| 2026-10-27-pfd-lci-review#5 | process.yaml:33 | maturity | `maturity: concept` is claimed while `cheme maturity` reports level none (`cheme.maturity-claim-exceeds`). `concept` is the lowest value the schema allows, and the comment and `validation.notes` state the gap honestly, so a reader is not misled. | low | open | Keep the notes. Optionally raise a library issue for a "below concept" value, or accept with a reason. |
| 2026-10-27-pfd-lci-review#6 | lca/lca.yaml:16,33; lca/results.md:5 | LCI boundary | The goal and the commits call the LCI "gate-to-gate", but `boundary: cradle-to-gate` appears in results.md and the dataset with no explanation there. The reason (keeping the purchased inputs as gaps) is only in comments and D-013. | low | open | Say in `goal:` or `dataset:` that the inventory is foreground-only, with the cradle-to-gate key kept so the backgrounds stay gaps. |
| 2026-10-27-pfd-lci-review#7 | lca/lca.yaml (emission:S); lca/gaps.csv | emission:S | A zero flow (S in the tail gas, 0 kg) is declared `missing:` and counted as 1 of the 8 gaps, which inflates the gap count. | low | open | Map it `free` like emission:H2O, or drop it from the stack template. |
| 2026-10-27-pfd-lci-review#8 | lca/lca.yaml emission_exclusions | furnace NOx, fugitive SO2, tank vent | The excluded emissions have no amount, so the 1 % cut-off cannot be checked (`cheme.lca-cutoff-unchecked`). | low | open | Give an order-of-magnitude amount with its source, or keep them as stated exclusions and say so in results. |
| 2026-10-27-pfd-lci-review#9 | lca/lca.yaml product:HPS | HPS | The steam co-product is credited as heat above BFW at 378 K. The deaerator steam, BFW pumping and blowdown at the site are not netted (D-008). This matters when the credit is mapped later. | low | open | State in the HPS `missing:` text that the credit is gross of deaerator steam and BFW pumping. |

No critical or high findings. The route (sulfur burning, 3+1 DCDA, 98.5 wt%, HP steam export,
explicit SO2) and the boundary match the scope of issue #175 and task.md. The balances close
and the numbers are plausible for the technology. Assumptions are marked, and the LCI is
honest about its gaps.

Merge: pending (reviewer does not merge in this run; a human merges after reading R-01 and R-02).
