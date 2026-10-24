---
topic: maturity
reviewed_commit: 5e263b4644508408ebedcef7d3c64b9bef5b72b9
scope: [process/flowsheet.yaml, process/simulation.yaml, process/design-basis.yaml, process.yaml, DESIGN.md]
basis:
  - {path: process/flowsheet.yaml, revision: 'sha256:0e6abb0456355c67feffb8c71aba3b1d04fdbe50b93f1f3b623b0a3c25835b7a', relation: analyses}
  - {path: process/simulation-run.json, revision: 5e263b4644508408ebedcef7d3c64b9bef5b72b9, relation: analyses}
  - {path: checks/maturity.json, revision: 5e263b4644508408ebedcef7d3c64b9bef5b72b9, relation: depends-on}
  - {path: equipment/datasheets, revision: 5e263b4644508408ebedcef7d3c64b9bef5b72b9, relation: depends-on}
reviewer: Claude (independent review agent; did not author D-097, the simulation or the review1 fixes)
reviewer_kind: agent
branch: stage/basic-maturity
merge: pending
---
# Review: calculation maturity of ASU-1 (D-097), first independent review

This is an independent review of the calculation maturity on branch `stage/basic-maturity`
at 5e263b4. The DESIGN.md part of the scope is decision D-097. The review checks against core's
docs/framework/maturity.md (origin/main). Its eight findings were raised on 169dc8b. They are
recorded here with the commit that closed them. The fixes are in f16c503, which also
regenerated the simulation, the BFD and PFD, checks/maturity.json, the TEA and the LCA.
5e263b4 changes only the HAZOP and the instrument-list note.

Checks run at 5e263b4:
- `cheme maturity`: **level none**. The only failing requirement below balanced is
  `sourced.boundary`: the S1 flow and composition are `assumed`. Every balanced requirement
  passes. `balanced.energy-closure` (not required) fails on PRD, K4101 and K4102.
  - Predictive fails on coverage (C1102 excluded) and model basis (V2101 component split).
    property-regime and energy-closure are unsupported in core.
  - property-package, stream-properties and exchangers pass. property-package passes on the
    recorded substitution; exchangers passes with E3101's declared 2 K, which it meets at
    2.00 K.
  - The engineering requirements pass.
  - The claim `concept` gives the warning `cheme.maturity-claim-exceeds`. concept is the
    lowest value the manifest schema allows, so that warning is expected, and D-097 records
    it.
- `cheme validate`: 0 errors, 57 warnings (none in this scope beyond the 3
  process-energy-balance warnings that D-097 explains).
- `cheme check --no-write`: process-balances, process-calculated-current and process-basic
  pass.

Verdict: **no critical, high or medium finding is open.** #1 to #8 are closed in f16c503.
For #1, the fix took the "S1 back to assumed" route, so the level drops to none and the claim
to concept. That is honest: no recorded decision fixes the design air. One new low finding
(#9).

The owner still has to make two decisions. The first: fix the design air (30 C, 80 % RH,
1.013 bara, CO2 420 ppm, the rate) as a design specification. Then remove the ASSUMED marks
in design-basis.yaml and on S4. The level becomes balanced (screening) with that. The
second: accept the Peng-Robinson substitution in simulation.yaml. An agent can make neither.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-24-maturity-review1#1 | - | S1 flow / composition | S1 was tagged `given` on values that D-058, the design basis and S4 mark ASSUMED. | high | closed f16c503 | S1 flow and composition are `provenance: assumed` with "ASSUMED (D-066, D-097)" sources. D-097 (1) withdraws the D-058 claim and names the owner decision. design-basis.yaml is unchanged and still ASSUMED. The TEA and LCA now show feed:AIR as assumed (tea.md, inventory.csv, results.md; the `given` key is gone from dataset.yaml). The level is none, the claim is concept, and process.yaml, the validation notes and the library README say so. |
| 2026-10-24-maturity-review1#2 | - | method_selection | `is_polar: false` with water a component. | medium | closed f16c503 | `is_polar: true`, `interaction_parameters_available: true`, and a `substitution` text giving the reason and the limitation (water 10-13 % low, D-058; adsorbers on IAPWS-95, D-080), marked as for the owner to accept. maturity reports property-package ok on the substitution. |
| 2026-10-24-maturity-review1#3 | - | E3101 warm end | The products left 1.1 K above the main air; 0.37 K least approach, no min_approach declared. | medium | closed f16c503 | F2101 is now a heater to 15 C, which returns the heat of adsorption (ASSUMED ~3 K, 96.9 kW). S4A is simulated at 15.0 C. E3101 declares `min_approach` 2 K (D-061, assumed), and the least approach is 2.00 K (288.15 / 286.15 K). predictive.exchangers passes. The cold-box heat leak is still not modelled, and D-097 records that as open: the flowsheet has no step to carry it. |
| 2026-10-24-maturity-review1#4 | - | S1 composition source | CO2 420 ppm was cited to D-058. | low | closed f16c503 | The source now reads "CO2 420 ppm (design basis, contaminants ASSUMED; D-097)". D-097 (1) states that D-058 uses the D-027 set. |
| 2026-10-24-maturity-review1#5 | - | V2101 energy imbalance | The 100.8 kW sink was not recorded. | low | closed f16c503 | D-097 gives V2101 100.8 kW, of which F2101 returns 96.9 kW (110,870 kg/h x ~1.04 kJ/kg K x 3 K). The simulation.yaml comment says the same. |
| 2026-10-24-maturity-review1#6 | - | S4 / S4F / S12A | The stream table was internally inconsistent (S4 15 C against S4A 11.9 C; S12A 1.10 against S12H 1.15 bara). | low | closed f16c503 | S4 (assumed 15 C) now agrees with the simulated S4A (15.0 C), and F2101 carries the 12 -> 15 C step as a modelled duty. D-097 explains the S12A / S12H pressure as an assumed line drop. The same kind remains for S17, see #9. |
| 2026-10-24-maturity-review1#7 | - | S12D | S12D mixed the heating-step and cycle-average bases. | low | closed f16c503 | Comments on S12D and in D-097 mark it "for the balance only". RG-2003 is sized at 200 C. |
| 2026-10-24-maturity-review1#8 | - | process.yaml, chemistry note | The comment blamed only the property regime, and the air figure was wrong. | low | closed f16c503 | The comment now names coverage (C1102), V2101, energy closure and the regime, and says that basic-engineering needs the engineering level. The air figure reads 85,810 Nm3/h dry / 85,840 with the CO2. |
| 2026-10-24-maturity-review1#9 | - | S17, E-2101 datasheet | The simulated waste N2 leaves E3101 at 7.2 C (simulation-run.json S17, and S12A filled at 7.2 C). The flowsheet keeps S17 at the assumed 13 C (`kept`), so the stream table shows 13 C on S17 and 7.2 C on S12A, its split product. The E-2101 datasheet is sized on the 13 C inlet: 987 kW for the gas, inside the 1,130 kW peak. The simulated heating step needs about 1,020 kW. D-097 states the 7.2 C and its cause (the missing ~75 kW heat leak), so this is the same kind as #6, not an error. | low | open | When the heat leak is modelled (D-097 open point), re-check S17 against 13 C. Until then, add a note on S17 that its 13 C is the D-061 design value and the simulation gives 7.2 C, and keep the E-2101 duty basis at the D-061 13 C with the 1,130 kW peak as margin. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|

None in this scope. The HAZOP findings (hazop-review3) and the layout findings are in their own
records.

## Checked and fine
- **Provenance:** no S1 value is `given`. A search of the flowsheet, the TEA and the LCA files
  for feed:AIR `given` finds nothing. design-basis.yaml is unchanged from origin/main.
- **Simulation:** one DWSIM run (fingerprint a44c551149eb0c7c), converged. Every calculated
  stream value carries that fingerprint, and process-calculated-current passes.
  - Booster: K3101 outlet 59.93 C, 185.9 kW, E3104 126.1 kW. The K-3101 and E-3104
    datasheets give the same values.
  - E-3101 datasheet: 15 C airs and 13 C products, which agrees with the simulation spec.
  - CW: +15 kW, from the booster aftercooler at the warmer suction. The TEA and LCA follow
    (10,721 kWh/h; climate change 66.7205 kg CO2-eq per t GOX).
- **F2101 as a heater:** it has no energy stream, so its 96.9 kW appears in no utility or
  in the LCA. That is correct for a heat that physically comes from the adsorption.
- **D-097 text:** it matches the files. It records the level none, the claim at concept, the
  open owner decisions and the remaining predictive blockers.

## Not checked
- core's own maturity rules (they are core's).
- The HAZOP consequences of the revised values (see hazop-review3).
- The cold-box heat leak model, which is not yet built.
