---
topic: design
reviewed_commit: dbd50333906344d4adb2614d303edd3c92c37699
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/cells.yaml, process/reactions.yaml, process/simulation.yaml, scripts/balance.py, lca/, equipment/equipment-list.yaml, runs/20261027-213504-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/chlor-alkali-1
merge: pending
---
# Review: design (concept PFD and preliminary gate-to-gate LCI, issue #121)

Independent review of the membrane-cell chlor-alkali case produced by a design agent
(commits 31c3055..dbd5033 on `case/chlor-alkali-1`). Every command below was re-run by the
reviewer at `dbd5033`; the run report was not trusted.

Ids in the table are `<file stem>#<n>` as `reviews/README.md` requires; the run's aliases
R-01.. are given in brackets.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-27-pfd-lci-review#1 | lca/results.md:15-25 | mass allocation | (R-01) The generated allocation comparison gives Cl2 a mass share of 30.6 %: 1.008 / (1.008 + 2.240 + 0.043), i.e. it counts the water of the 50 wt-% caustic solution and of the wet hydrogen as co-product mass. On a 100 % NaOH and dry H2 basis the share is about 46 %. The allocation actually used is `none`, so the inventory is not wrong, but a reader or a later study that picks "mass" from this table gets a share that is off by a factor of 1.5. | medium | open | State in `lca/lca.yaml` `allocation.source` and in DESIGN.md D-013 that any mass allocation must use contained Cl2, 100 % NaOH and dry H2 (1.000 : 1.120 : 0.0295 kg), not product-stream mass. Report to cheme-as-code that `mass` uses stream mass including solvent water. |
| 2026-10-27-pfd-lci-review#2 | lca/results.md:9-25 | climate-change column | (R-02) The allocation table prints `0` kg CO2-eq for the `mass` and `none (used)` rows, although every contribution is a gap ("no total" two lines above). DESIGN.md section 6 explains this, but results.md is the file a reader opens. | low | open | Report to cheme-as-code (the table should print "no total" when every exchange is a gap); until then, point to DESIGN.md section 6 from lca/README.md. |
| 2026-10-27-pfd-lci-review#3 | lca/lca.yaml:84 | emission:CO2 | (R-03) Mineral CO2 to air (2.36 g/kg Cl2) is declared `missing:` like a background, although it is an elementary flow that the configured method (`ipcc2021-gwp100` in lca/factors.yaml) characterises directly once `elementary: {compartment: air, origin: fossil}` is given. The same holds for the other emissions (`cheme.lca-flow-identity` info: no receiving compartment). | low | open | Give the elementary compartment and origin for emission:CO2 (and the water compartment for NaCl and Na2SO4). CO2 then carries its GWP of 1 instead of being a gap. |
| 2026-10-27-pfd-lci-review#4 | lca/lca.yaml:88-92 | emission_exclusions | (R-04) The four cut-off exclusions have no amounts, so the 1 % mass rule cannot be checked (`cheme.lca-cutoff-unchecked`). The cited BREF range for H2 venting (up to 14 kg H2/t Cl2) is about half of the hydrogen product, so "cut off" depends entirely on the D-008 statement that no H2 is vented. | low | open | Give an ASSUMED kg/a for each exclusion (e.g. H2 vented at start-up and upsets) or say in the reason that the BREF range is for plants without an H2 consumer and does not apply. |
| 2026-10-27-pfd-lci-review#5 | process/flowsheet.yaml:293-303 | C401 | (R-05) `cheme maturity` lists C401 as "equilibrium-stage, predictive, sourced" because its class is `SeparatingByFlash`, but its outlet (20 mg/kg Cl2 at 55 kPa(a)) is a specified split from scripts/balance.py based on BREF 2.5.4 (DESIGN.md D-005, section 3). The maturity report therefore overstates this step. The plant level stays `none`, so no claim depends on it. | low | open | Declare C401's model as a specified/component split (as for S101 and C502), or report the classification to cheme-as-code. |
| 2026-10-27-pfd-lci-review#6 | process.yaml:35 | maturity | (R-06) `maturity: concept` against `cheme maturity` level none (`cheme.maturity-claim-exceeds`, warning). `concept` is the lowest value the schema allows, and both the comment and `validation.notes` say so honestly, so a reader is not misled. | low | accepted: the schema has no level below concept; the gap is disclosed in process.yaml and DESIGN.md section 5 (review-agent) | none; revisit when feeds are sourced |
| 2026-10-27-pfd-lci-review#7 | process.yaml:76 | references | (R-07) Ullmann's (Schmittinger et al. 2011) is listed under `references` although DESIGN.md section 4 says it was "not read in this run" and nothing rests on it. | low | open | Remove it from `references` or mark it as background reading not used for any value. |
| 2026-10-27-pfd-lci-review#8 | runs/20261027-213504-design/run.yaml:46; checks/checks.yaml:76 | decision ids | (R-08) `cheme.decision-unknown` infos: D-101 (the old saturator tag) is still in the run record, and D-023 in the scaffold's checks.yaml has no DESIGN.md entry. | low | open | Leave the run record as it is (it is a record); fix or remove the D-023 reference in checks.yaml. |
| 2026-10-27-pfd-lci-review#9 | DESIGN.md D-004; scripts/balance.py | EL-301 / T-301 | (R-09) All 605 elements are put in one DC circuit, about 1.8 kV DC at 16.2 kA. Plants of this size usually split the cell room into several electrolysers, each with its own rectifier and a lower circuit voltage. This does not change the balance, but it matters for T-301 and for the equipment count. | low | open | State in D-004 that the circuit split (number of electrolysers and rectifiers) is open and that it does not affect the per-kg figures. |
| 2026-10-27-pfd-lci-review#10 | equipment/equipment-list.yaml:32 | C-401 | (R-10) The vacuum dechlorination tower runs at 55 kPa(a) and its material note says "full vacuum", but the design condition gives only 2 barg. | low | open | Give the design pressure as "2 barg / full vacuum" (D-012 rule plus vacuum). |
| 2026-10-27-pfd-lci-review#11 | worktree root | build_fs_schema.json | (R-11) An untracked schema dump left by the design run at the library root, outside the process folder. It is not committed, so the branch is clean. | low | open | Delete the file before merging (housekeeping, not a design change). |

No critical or high findings.

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|

None: this is the first review record of this process.

## Drawing
The only sheets are the generated `process/BFD.xml` and `process/PFD.xml` (built by
`cheme process build` from the YAML). `cheme validate` prints no `drawing <sheet>:` count line
for them (0 errors, 0 warnings; gate `drawing-clean` ok). The sheets were not rendered or read
in tiles (see Not checked). There are no P&IDs: they are out of scope for this run, and gate
`pids-exist` fails as expected.

## Commands re-run (at dbd5033)
- `cheme validate`: 18 files, 0 errors, 0 warnings. Infos: decision-unknown D-023 and D-101
  (#8), cell-unsourced (CE and side reaction ASSUMED, as declared), cell-temperature
  (dH at 298 K). Compared: BFD, PFD and 12 lists. Lists against P&IDs were skipped because
  there are no P&IDs.
- `cheme check`: every concept gate passes (design-basis, concept-lists, process-concept,
  process-balances, assumptions-marked) except `layout-plot-plan` (layout is out of scope).
  The basic and detail gates that fail (pids-exist, design-review, layout-*, lifting, mto,
  datasheets, electrical, hvac) are all outside this run's scope. `design-review` should pass
  once this record is committed.
- `cheme maturity`: level none. sourced.boundary fails because the feed flows are design
  choices. balanced.model-basis fails because the splits are specified and ASSUMED. Mass
  balances evaluable and closed. Manifest claim warning: #6.
- `cheme process streams`: all 7 blocks and 22 steps close in mass. Reactive extents agree,
  e.g. CHLORALKALI 176.317 kmol/h and WATER_SPLIT 3.197 kmol/h in ELY/EL301.
- `cheme process propagate --check`: exit 0, no output (nothing to propagate, no conflict).
- `cheme assess lca --coverage`: partial screening carbon footprint, 15 gaps, every one
  declared `missing:` with a description. Mass, element and carbon-origin balances closed;
  publication: public, publishable.

## Checked and fine
- **Scope and boundary** match issue #121 and the run task: membrane route; an explicit
  saleable-product boundary (dry Cl2 gas at 400 kPa(a), 50 wt-% NaOH, wet H2); the cell-room
  boundary is described separately and warned as not comparable (D-001, section 1); brine
  purification, dechlorination, purge, Cl2 drying and compression, and evaporation are all
  inside. Co-products are listed and not allocated, and the H2 double-counting risk is noted
  (lca.yaml HCl and allocation notes).
- **Cell, checked by hand.** 2F / M(Cl2) / CE x 3.0 V = 2.350 kWh DC per kg Cl2, and 2.423 kWh
  AC at a rectifier efficiency of 0.97. 605 x 2.7 m2 x 6 kA/m2 = 9.80 MA, matching the
  365.4 kmol/h of electrons. Cathode H2 = total current/2F (182.7 kmol/h). O2 =
  3.197 kmol/h, which is 1.78 vol-% in Cl2 and inside BREF 0.5-2.0. NaOH 14 104 kg/h, giving
  44 076 kg/h of 32 wt-% catholyte. Isothermal heat of 7.04 MW, consistent with
  (3.0 - 2.31) V plus the O2 side reaction.
- **Catholyte water.** 4.0 mol H2O per mol Na+ through the membrane, cathode consumption,
  water in the H2 and 0.15 t/t rinse add up to about 14.1 t/h of DM water, matching
  feed:DMW 14 054 kg/h.
- **Wet gas saturation.** Water activity 0.876 x 70.18 kPa at 115 kPa gives 22.8 wt-% water,
  i.e. 290 kg/t condensate; the same method at 85 degC gives about 200 kg/t, which matches the
  BREF figure the design quotes. H2 at 35 degC carries 14 g water per 29.5 g H2, matching the
  43.4 g product gas.
- **Drying.** 98 -> 75 wt-% acid absorbs 5.7 kg water per t Cl2, matching the water in Cl2
  saturated at 20 degC (about 5.4 g/kg).
- **Compressor and steam.** Compressor 246 kW: about 170 kW isothermal for a pressure ratio of
  about 4, plausible for two stages at 0.75. Steam: 8.75 t/h at economy 1.8 for 15.75 t/h of
  water evaporated (32 -> 50 wt-%), i.e. 0.625 t/t NaOH. Brine heater: 142 t/h x 3.3 x 15 K =
  1.96 MW, equal to 3.5 t/h of MP steam. MPS 6 858 kWh/h is the latent heat of 12.25 t/h at
  10 bar(a).
- **Salt and sulfate.** Salt 1.711 t/t against 1.65 stoichiometric plus the purge NaCl.
  Sulfate in (CaSO4 in salt and oxidised sulfite, about 3.0 g Na2SO4/kg Cl2) equals the purge
  (2.9 g/kg), consistent.
- **Plausibility.** Every consumption above lies inside the BREF 2014 chapter 3 ranges quoted
  in DESIGN.md section 3, and the design calls this a range check, not a validation. 3.0 V at
  6 kA/m2 is at the good end of zero-gap performance, sourced to BREF 4.3.2.3.2 and
  specified, not predicted.
- **LCI mass balance.** Recomputed from lca/inventory.csv: inputs 3.8264 kg = outputs
  3.8264 kg per kg contained Cl2 (3.795 kg per kg product gas). Plant totals are 47 830 kg/h
  of feeds, which matches the flowsheet. The LCI is per functional unit (1 kg contained Cl2,
  `kg_per_unit` 1.008185 from S42). No background value is zero-filled and no licensed
  database value appears: factors.yaml has no factors beyond the open DESNZ profile include,
  and every background is `missing:` with the activity it should link to. CHW is `free` with
  the reason (chiller power is counted in the auxiliaries). The zero-amount emission keys are
  `free` with reasons.
- **Provenance.** Every stream value is `assumed` with scripts/balance.py as the source (208
  entries). Every input in the script and DESIGN.md is either sourced with a BREF section or
  table locator, or marked ASSUMED. Gated steps (energy closure, electrolyte properties) are
  named with their core issues (core#364, PR #394).
- **Licences.** DESIGN.md, the design basis and lca.yaml use BREF facts and ranges in their own
  words with section and table locators. No tables, figures or passages are copied, and no
  third-party drawings are present. The BFD and PFD are generated from our own YAML.
- **Honesty.** process.yaml (`publication.status: internal`, `validation.status: unreviewed`)
  states level none, the specified cell, the gated energy balance and the missing chemicals
  registry entries.
- **Changes outside the folder.** `git diff --name-only origin/main..HEAD` lists only paths
  under `processes/chlor-alkali-1/`.

## Not checked
- Rendering of the generated BFD/PFD sheets: not rendered or read in tiles. Validate's lint
  reports nothing for them.
- Re-running `scripts/balance.py` to confirm it reproduces the committed stream values
  byte-for-byte. Spot checks of the cell, water, steam, drying and sulfate balances agree
  (above).
- Energy closure of the steps outside the cell (not evaluable in core, core#364). The duties
  rest on constant heat capacities (D-006). The evaporator duty and the cell heat split were
  only checked for order of magnitude.
- The BREF locators themselves (section and table numbers) were not opened by the reviewer.
  The figures quoted are consistent with general chlor-alkali knowledge.
- P&IDs, layout, HAZOP, datasheets, TEA: out of scope for this stage.
