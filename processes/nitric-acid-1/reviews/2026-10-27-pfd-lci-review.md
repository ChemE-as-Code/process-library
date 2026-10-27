---
topic: design
reviewed_commit: 9a12e031634fb445bc0682c7e7fda2ed895ee353
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/reactions.yaml, process/materials.yaml, process/BFD.xml, process/PFD.xml, equipment/equipment-list.yaml, lca/, scripts/hno3_balance.py, runs/20261027-213524-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/nitric-acid-1
merge: pending
---
# Review: design (concept PFD and preliminary LCI, nitric-acid-1, issue #119)

Independent agent review of the design run of 2026-10-27 (commits e7dbb4b..9a12e03 on
`case/nitric-acid-1`). Everything quoted below was re-run by the reviewer at 9a12e03, not taken
from the run report. Finding labels R-01 ... are given in brackets; the ids follow the
`reviews/README.md` format.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-27-pfd-lci-review#1 | lca/lca.yaml:62 | catalysts, Pt/Rh | [R-01] The Pt/Rh gauze loss and the consumption of gauze, N2O-decomposition and SCR catalysts are known foreground exchanges but appear nowhere in the LCI files: not as a `missing:` flow, not as an `emission_exclusions` / cut-off entry, so `gaps.csv` and `--coverage` (10 gaps) do not show them. They are only mentioned in DESIGN.md D-014 and O-3 (which itself says the precious-metal flow is "never cut off"). The LCI therefore does not describe every gap. | medium | open | Declare them in `lca/lca.yaml` (a catalyst/Pt-loss input declared `missing:` with the activity it should connect to, or an explicit exclusion with reason) and rewrite the outputs with `cheme assess lca --write`, so the gap is in `gaps.csv` and the manifest. |
| 2026-10-27-pfd-lci-review#2 | lca/lca.yaml:25 | boundary, result label | [R-02] Boundary wording is inconsistent: `lca.yaml`, `results.md:5` and `manifest.json:5` say `cradle-to-gate`; D-014, PROGRESS.md, the commit message and `dataset.yaml:14` say gate-to-gate; the goal (line 18) says "Not a carbon footprint" while the generated label is "partial screening carbon footprint" with 0.68 kg CO2-eq/kg. Declaring cradle-to-gate with every background as a gap is the correct tool semantics (gate-to-gate would mean mapping feeds free), but a catalogue reader sees "cradle-to-gate, climate change 0.68 kg CO2-eq/kg", which is the direct N2O only, far below any real cradle-to-gate value (ammonia alone is missing). | medium | open | Keep `boundary: cradle-to-gate` but say in D-014, PROGRESS.md and the lca.yaml goal that it is a cradle-to-gate scope with all backgrounds open (foreground only), and make the goal / dataset description state that 0.68 kg CO2-eq/kg is the direct N2O emission only, not the product footprint. |
| 2026-10-27-pfd-lci-review#3 | process/PFD.xml | PFD layout | [R-03] The generated PFD reads backwards: the oxidation block (burner, waste-heat boiler, cooler-condenser) is at the far right, absorption in the middle and feed preparation at the left, with long return lines crossing most of the sheet (rendered `build/PFD.png`). Not a balance error; the run report acknowledges the auto-layout but the sheet is the published figure. | medium | open | Pin a left-to-right layout (`cheme process layout --view pfd --pin`, then adjust `layout.pfd` in flowsheet.yaml, currently `{}` at line 707) and rebuild. |
| 2026-10-27-pfd-lci-review#4 | process/flowsheet.yaml:239 | V101 | [R-04] `cheme maturity` reports V101 (class `SeparatingByFlash`) as "equilibrium-stage, predictive, sourced", although its outlets are script specifications (D-007) and no property package covers HNO3-water (`props --coverage`, D-012). The model-basis printout overstates this step; the overall level (none) is unaffected. | low | open | Record it in DESIGN.md D-012 as a core finding (maturity infers a predictive flash from the step class without a model or property package) and report it to cheme-as-code. |
| 2026-10-27-pfd-lci-review#5 | process.yaml:35 | maturity | [R-05] `maturity: concept` while `cheme maturity` reaches level none and warns `cheme.maturity-claim-exceeds`. `concept` is the lowest value the library schema allows and the gap is stated honestly in the comment and `validation.notes`, so this is not misleading, but the warning stays. | low | open | Keep as is with the disclosure, or ask the library for an "unassessed/none" value; no design change needed. |
| 2026-10-27-pfd-lci-review#6 | lca/lca.yaml | unabated case | [R-06] The unabated comparison asked for by the issue (7.0 vs 2.5 g N2O/kg, 1.91 vs 0.68 kg CO2-eq/kg) exists only as prose in D-009; it is not an LCI scenario, so it is not in `results.csv` / the manifest. | low | open | Add an LCA scenario overriding the N2O emission to the formed amount (291.7 kg/h, stream S27) if the schema allows, or keep D-009 and cite it in results. |

## Previous findings
None: first review of this process folder (`reviews/` held only README.md before this record).

## Drawing
No P&ID in this stage (out of scope). `cheme validate` prints no `drawing` line for the generated
BFD/PFD; gate `drawing-clean` passes (no P&ID). The PFD was rendered whole
(`build/PFD.png`) and read: no overlapping labels seen at that scale, but the layout finding
#3. The BFD was not rendered.

## Layout
Not in scope (no `layout/` files; layout gates fail as expected for this stage).

## Re-run results (at 9a12e03)
- `cheme validate`: 17 files, 0 errors, 0 warnings (infos only: the template's example
  `D-023` in a comment of `checks/checks.yaml:76`, DEXPI loader cycles). Compared 2 sheets
  (BFD, PFD) and 12 lists; list-vs-P&ID cross-checks skipped (no P&ID).
- `cheme check`: concept gates design-basis, concept-lists, process-concept,
  process-balances, process-links-concept, assumptions-marked ok; layout-plot-plan fails
  (out of scope); basic/detail gates pids-exist, design-review, layout-*, mto, datasheets fail
  (out of scope or this review). Matches the run report.
- `cheme maturity`: level none; sourced.boundary fails (feeds assumed), balanced.model-basis
  fails (conversions and absorber outlets assumed), balances evaluable and closed ok;
  claim-exceeds warning (#5). Matches the report and process.yaml.
- `cheme process propagate --check` and `cheme process streams`: every block (PREP, OX, ABS,
  TGT) and all 21 steps close; reaction extents explain every composition change.
- `cheme run scripts/hno3_balance.py` (writes only `build/`): mass in = out 239 274.6 kg/h;
  N balance 0; energy in/out -61 825.7 / -61 832.4 kW (6.7 kW = pump work); 0.2854 t NH3/t
  HNO3; N to HNO3 0.947; N2O formed 291.7 kg/h, emitted 104.2 kg/h. Reproduces D-010.
- `cheme assess lca --coverage`: partial screening carbon footprint, 10 gaps (6 unmapped
  backgrounds, 4 uncharacterised NOx/NH3/HNO3 emissions), mass and element balances closed,
  energy closure 57.9 % (delivered utilities only; explained in D-014), publishable.

## Checked and fine
- **Scope and boundary**: dual-pressure Ostwald route, liquid NH3/air/demin water in, 60 wt% acid,
  treated tail gas and HP steam out, storage/BFW/cooling tower outside (D-001) match issue #119's
  case note and the run scope. `git diff --name-only origin/main..HEAD` touches only
  `processes/nitric-acid-1/`. No P&ID, layout, HAZOP or TEA was attempted.
- **Balances and plausibility** (reviewer's own hand checks against general engineering
  knowledge): NO selectivity 0.955 at medium pressure and N efficiency 94.7 % give 0.285 t
  NH3/t HNO3 (stoichiometric 0.270), within the usual 0.28-0.29; burner feed 10 mol% NH3,
  O2/NH3 = 1.87, adiabatic rise to 1144 K (871 degC, within the 750-920 degC of S4); tail gas
  O2 3.0 mol% after absorption checked from the extents (413 kmol/h O2 in, 231 consumed);
  untreated N2O 1100 ppmv; water 0.4 mol% in the tail gas equals saturation at 303 K and
  1100 kPa; weak acid 42 wt% and V101 gas 0.9 mol% water consistent with saturation over weak
  acid; machine powers re-derived by hand (K-101 ~12 MW, K-102 ~6.3 MW, X-101 ~14.4 MW, expander
  outlet ~420 K); economiser and boiler duties and approaches (E-103, E-104, E-106 > 30 K)
  consistent; HP steam 29.5 MW = 38 t/h from BFW at 378 K (0.92 t/t gross, all exported with a
  motor drive); cooling water 46.7 MW (~96 m3/t at 10 K); overall heat of reaction ~79 MW
  balances steam + cooling water + stack sensible heat to a few MW.
- **Sources**: IPCC 2006 Vol. 3 Ch. 3 Table 3.3 defaults (7 kg N2O/t medium-pressure, 2.5 kg/t
  with tail-gas N2O destruction) used as stated and cited with locator; AR6 GWP100 273 for N2O;
  JANAF formation enthalpies standard values; every other key value (selectivity, pressures,
  absorber specifications, efficiencies, heat of mixing, CW/steam levels) marked ASSUMED in
  design-basis.yaml, reactions.yaml and DESIGN.md. The BREF is honestly declared "not re-read,
  no number taken" (O-1).
- **Copying**: no third-party table, figure or passage found in DESIGN.md, process.yaml, the YAML
  or the script; tables are cited by name and locator only; PFD/BFD generated by cheme.
- **LCI**: per 1 kg contained HNO3 (1.667 kg of 60 wt% acid); inputs 5.7426 kg = outputs 5.7426
  kg, stack components sum to the stack stream; every amount traces to a flowsheet stream; no
  background value, no licensed data, no zero-filled background (zero NH3/NO2/HNO3 emissions
  are flowsheet values of the design case, documented); every unmapped background carries a
  description of the activity to connect.
- **Equipment list**: design pressures and temperatures follow D-013's rule (checked for E-101,
  K-101, K-102, C-101, E-102, E-103, E-104, R-102, C-102).
- **process.yaml**: internal, unreviewed, maturity disclosure honest (see #5); report.md
  figures agree with the re-runs.

## Not checked
- The BREF ranges (S2) and the IPCC page locator were not opened by the reviewer; the numbers
  were checked against the reviewer's knowledge of Table 3.3 only.
- Thermodynamic accuracy of the script's enthalpies (ideal-gas, assumed heat of mixing and acid
  heat capacity) beyond the energy closure; no rigorous HNO3-H2O-NOx model exists in core.
- The BFD drawing; PFD only at whole-sheet scale, no tiles.
- Flammability margin of the 10 mol% NH3-air mixture at 463 K and 510 kPa(a) (human judgement,
  D-005).
- Materials of construction (first indications only, D-013).
