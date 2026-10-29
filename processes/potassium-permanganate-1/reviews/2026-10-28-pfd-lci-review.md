---
topic: design
reviewed_commit: 97a50b6d133b56f3a0af3ea5761273ec36ed001f
scope: [DESIGN.md, process.yaml, process/, lca/, scripts/kmno4_balance.py, equipment/equipment-list.yaml, piping/line-list.yaml]
reviewer: review-agent
reviewer_kind: agent
branch: case/potassium-permanganate-1
merge: pending
---
# Review: design basis, balanced BFD/PFD and preliminary LCI (potassium permanganate, issue #146)

Independent review of the design agent's run 20261028-162126-design (commits 3ce86b9..97a50b6
on `case/potassium-permanganate-1`). The review ids `R-01 ... R-13` of the task are the record
ids `2026-10-28-pfd-lci-review#1 ... #13` below (R-nn = #nn). No design file was changed.

Re-run by the reviewer at 97a50b6 (not taken from the run report):

- `cheme validate`: 17 files, 0 errors, 0 warnings (infos only: unsourced cell performance,
  cell heat of reaction at 298 K, template comments citing D-023/D-012).
- `cheme check`: all concept gates ok except `layout-plot-plan`; basic/detail gates fail on
  missing P&IDs, layout, datasheets and this review (out of the run's declared scope).
- `cheme maturity`: calculation maturity **none**; `cheme.maturity-claim-exceeds` warning
  (process.yaml claims `concept`); review status unreviewed.
- `cheme process streams`: 5 blocks and 10 steps balance (reactive by extents); overall
  4911.9 kg/h in and out.
- `cheme process propagate --check`: no output, exit 0.
- `cheme assess lca --coverage`: partial screening carbon footprint, 11 gaps (10 unmapped
  backgrounds + H2 outside the method), mass, element and carbon-origin balances closed;
  `cheme assess lca --check`: generated LCA files current.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | scripts/kmno4_balance.py:223-233, process/flowsheet.yaml:519 (Q1) | R-201 fired heat | R-01. The roaster duty charges only the latent heat of pure water for the ~1236 kg/h evaporated, but the KOH enters as 50 wt% solution (S2, S4) and the OX/REDKM heats use KOH(s); the enthalpy of separating ~22 kmol/h KOH from its water (integral heat of solution, of the order of 40-55 kJ/mol) is not charged, while the leach (line 230-233) credits the KOH(s) dissolution heat of -57.6 kJ/mol. Inconsistent enthalpy basis: Q1 is understated by roughly 0.25-0.35 MW before losses, ~25-30 % (0.99 -> ~1.25 kWh/kg in the LCI). The same differential term is missing in E-601 (13 -> 50 wt% KOH). | medium | open | add the KOH heat of solution at the feed and product concentrations (sourced) to q_r201 and q_e601, rerun the balance, update Q1/Q8, D-009 and the LCI |
| 2026-10-28-pfd-lci-review#2 | process/cells.yaml:24-25, DESIGN.md:106-122 (D-006) | EL-401 | R-02. The cell is sized with one active area at 1000 A/m2, but SRC-1's 500-1500 A/m2 is a **cathode** current density; the current efficiency is set by the anode current density and manganate mass transfer. With 90 % conversion per pass the anolyte leaves at 0.6 wt% K2MnO4 (S14), where 1000 A/m2 at the anode would far exceed a plausible manganate limiting current. CE 0.85 together with 90 % per pass at 1000 A/m2 is internally optimistic, so the rectifier power (0.546 of 0.696 kWh/kg, the largest electricity item) is probably low. D-006 flags CE as unsourced but not this coupling. | medium | open | state anode and cathode areas/current densities separately, record in D-006 that CE falls with per-pass conversion, and give a CE sensitivity (e.g. 0.6-0.9) for the DC energy in DESIGN.md/lca results |
| 2026-10-28-pfd-lci-review#3 | DESIGN.md:18-27, process/cells.yaml:24-34, process/reactions.yaml, process/design-basis.yaml | source locators | R-03. Patent facts are located only as "Description", "Background", "Claims" or "cell design"; issue #146 asks for exact section/page/table locators. The patents have column:line numbering in their PDFs (only one fact, the grind size, cites a claim number), so the HTML argument in DESIGN.md:16 does not justify the coarse locators. | medium | open | add column:line (or claim/example number) to every numeric fact taken from US 5,660,712, US 5,011,672 and US 3,986,941 |
| 2026-10-28-pfd-lci-review#4 | process/flowsheet.yaml:408 (S14), process/cells.yaml:39, DESIGN.md D-007 | EL-401 / X-501 | R-04. The cell liquor carries 5.5 wt% KMnO4 at 333 K in 12.5 wt% KOH, against 1.5 wt% at 303 K in the mother liquor; cells.yaml itself says KMnO4 partly crystallises in the anolyte, but the flowsheet carries it dissolved to X-501 and charges the whole crystallisation heat to Q6. Contradiction between files; small effect on Q5/Q6 only. | low | open | reconcile: note the in-cell crystallisation in D-007 (or move its heat to Q5) and cite solubility data when available |
| 2026-10-28-pfd-lci-review#5 | process/flowsheet.yaml:375 (S11), DESIGN.md D-005 | F-301 wash | R-05. The whole evaporator condensate (3779 kg/h) is the "displacement wash" of a cake holding ~180 kg/h liquid, about 20 cake-liquid volumes, at a stated 90 % solute recovery. It is in effect leach dilution water routed through the filter. | low | open | describe it as such in D-005, or send the excess condensate to M-301 and keep a realistic wash ratio |
| 2026-10-28-pfd-lci-review#6 | process/flowsheet.yaml:298 (S4), DESIGN.md D-004/D-008 | E-601 | R-06. The concentrate carries 5.8 wt% KMnO4 in 50 wt% KOH at 413 K. The permanganate reduction assumed in the roaster (REDKM) would already happen in the evaporator (O2 in the vapour, manganate/MnO2 fouling). No effect on the Mn balance. | low | open | note in D-008 as a basic-engineering item (evaporator materials and fouling) |
| 2026-10-28-pfd-lci-review#7 | process.yaml:35-47 | maturity | R-07. `maturity: concept` while `cheme maturity` gives calculation maturity none and warns `cheme.maturity-claim-exceeds`; the schema has no lower level and the validation notes are candid, but they do not say that cheme rates the evidence below the claim (lca/manifest.json also uses the "concept (sourced screening)" tolerance basis). | low | open | add to validation.notes that `cheme maturity` evaluates to none and the concept claim exceeds the evidence because the schema has no lower level |
| 2026-10-28-pfd-lci-review#8 | process.yaml:48-58 | chemistry | R-08. The manifest declares no main product and none of the ore, KOH or lime inputs (no registry entries); a catalogue reader sees a process with water and air in and wastewater and hydrogen out. The notes explain it. | low | open | add the registry entries in the consolidated PR (as DESIGN.md lists) and declare KMnO4 as main-product |
| 2026-10-28-pfd-lci-review#9 | lca/lca.yaml (emission:H2), lca/inventory.csv | emission:H2 | R-09. The vented cathode hydrogen is reported as "air, fossil" (cheme default); it comes from water, so the origin label is wrong (no effect on the carbon balance). | low | open | give the H2 emission a non-fossil origin if the schema allows, otherwise note it in lca/README.md |
| 2026-10-28-pfd-lci-review#10 | process/reactions.yaml:49, DESIGN.md:26-27 | thermochemical data | R-10. WATER_SPLIT's heat is `provenance: given` (CODATA) although SRC-8 says the value was recalled, like the NBS values marked ASSUMED. The reviewer recomputed the heats from the stated formation values (OX -112.6, REDKM -172.0, ELEC +334.9 kJ; dG(ELEC) 266.8 kJ -> 1.383 V) and they match the NBS values as known to the reviewer, but neither of us re-read the tables. | low | open | re-read the tables, add table locators, then mark all of them given (or WATER_SPLIT assumed until then) |
| 2026-10-28-pfd-lci-review#11 | process/flowsheet.yaml:230, process/PFD.xml | DR-501 | R-11. After the retag D-501 -> DR-501 the flowsheet step is still `D501` (PFD label "D501", ports `D501.*`, Q10 `LPS.d501`), so the PFD shows a tag that is not in the equipment list. | low | open | rename the step to DR501 and rebuild the BFD/PFD |
| 2026-10-28-pfd-lci-review#12 | DESIGN.md | basis table | R-12. Issue #146's handoff asks for a basis table marking each value sourced / proposed / missing; the information is spread over the source register, D-001..D-011 and the design basis, but there is no such table. | low | open | add a short basis table (value, status sourced/assumed/missing, source locator) to DESIGN.md |
| 2026-10-28-pfd-lci-review#13 | checks/checks.yaml | layout-plot-plan | R-13. The concept gate `layout-plot-plan` fails (no site plan or placement); DESIGN.md declares layout out of scope, but the gate is not deferred anywhere. | low | open | defer it explicitly (issue in plant.yaml or a note in PROGRESS.md) or add a plot plan in the next stage |

## Previous findings
None: this is the first review record of this process (reviews/ held only README.md).

## Drawing
No P&ID in this scope (`pid/` empty). `cheme validate` printed no `drawing <sheet>:` line for the
generated BFD/PFD. `build/PFD.png` (full sheet) read: all 23 streams and 11 energy streams
are drawn with their ids; long energy-stream and recycle lines cross block frames, which is
acceptable for a generated PFD; the dryer shows `D501` (finding #11). BFD not rendered.

## Checked and fine
- **Scope and route**: the conventional two-stage route (KOH roasting of MnO2 ore, leach with
  lime silicate removal, membrane-cell oxidation, cooling crystallisation, KOH recovery) is
  the industrial route the issue's notes point to; alternatives are rejected with reasons
  (D-001). Boundary ore-at-gate to dried KMnO4 is stated in the design basis, D-001 and
  lca.yaml.
- **Nothing outside `processes/potassium-permanganate-1/` changed**
  (`git diff --name-only origin/main..HEAD`).
- **Stoichiometry and yields**: overall 2 MnO2 + 2 KOH + O2 -> 2 KMnO4 + H2 balances; theory
  0.550 kg MnO2 and 0.355 kg KOH per kg KMnO4 confirmed; Mn to product 88.6 % (=0.989 x 0.550 /
  0.614) and K 76 % follow from roaster X 0.90 and the 3 % purge; KOH/MnO2 to the roaster
  = 2.5 mol/mol (575 + 664 kg/h KOH vs 768 kg/h MnO2); OX extent 3.97 kmol/h = 0.90 x 8.83/2.
- **Cells**: Faraday check by hand: 169.6 Ah/kg, at 2.5 V and CE 0.85 0.499 kWh DC/kg formed;
  thermoneutral 1.735 V and reversible 1.38 V recomputed; H2 (9.96 kg/h) and O2 (11.85 kg/h)
  consistent with the current and the 15 % side reaction; rectifier and auxiliaries give
  0.696 kWh/kg.
- **Other duties** (order of magnitude recomputed): crystalliser 0.96 MW (30.6 t/h x 3.4 x 30 K
  plus crystallisation heat, endothermic dissolution sign correct), leach 0.68 MW, evaporator
  1.40 MW (3779 kg/h at economy 1.8), dryer 72 kW; double-effect concentration to 50 wt% KOH
  with 450 kPa(a) steam is feasible with the last effect under vacuum.
- **LCI**: per kg KMnO4, each exchange tied to a stream id; inputs 3.9295 = outputs 3.9297 kg/kg
  (recomputed from inventory.csv); every unmapped background is `missing:` with a description,
  none zero-filled, no licensed values (factors.yaml is the open DESNZ profile; no ecoinvent
  values); per-process overrides only in `lca/mappings.yaml` (utility units); exclusions
  declared with reasons; dust declared as not estimated (D-011). `boundary: cradle-to-gate`
  with all backgrounds missing is explained in the lca.yaml header and dataset.yaml says
  gate-to-gate foreground.
- **Assumptions marked**: every stream value is `provenance: assumed` with a source pointing to
  the script and a decision; design basis assumptions say ASSUMED.
- **Copyright**: no table, figure or passage of the patents or other sources is copied; facts
  are restated with the source named.
- **Run report honesty**: the report states calculation maturity none, the unsourced CE, the
  heredoc deviation from AGENTS.md and that no merge is pending.

## Not checked
- The cited patents and the NBS/CODATA tables were not re-read by the reviewer (no access in
  this session); source facts were compared with general engineering knowledge only.
- Industrial benchmarks (DC energy, KOH and ore consumption per t of KMnO4) were not compared
  with an open dataset; Ullmann (SRC-6) and the full text of SRC-5 remain unaudited.
- Solubility of KMnO4/K2MnO4 in KOH liquors (finding #4) not checked against data.
- P&IDs, layout, HAZOP, datasheets, TEA: not produced in this run (basic/detail gates fail).
- BFD drawing not rendered; `scripts/kmno4_balance.py` read only around the energy section and
  its outputs compared with the flowsheet, not line by line.
