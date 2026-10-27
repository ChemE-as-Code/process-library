---
topic: design
reviewed_commit: adfad09f75080018ffd074c7ec4084395d4d7182
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/furnaces.yaml, process/flowsheet.yaml, process/simulation.yaml, scripts/solvay_balance.py, equipment/equipment-list.yaml, piping/line-list.yaml, lca/lca.yaml, lca/results.md, lca/gaps.csv]
reviewer: review-agent
reviewer_kind: agent
branch: case/soda-ash-1
merge: pending
---

# Independent review: soda-ash-1 BFD/PFD and preliminary LCI (issue #177)

Reviewer: an independent agent that did not write the case. This is a review only; no design
file was changed.

## What was reviewed and re-run

`git log --oneline origin/main..HEAD` lists 6 commits (from the scaffold 64c953a to the run
record adfad09). `git diff --name-only origin/main..HEAD` shows changes **only under
`processes/soda-ash-1/`**.

I re-ran every command myself at adfad09 instead of relying on `runs/20261027-221326-design/report.md`:

| command | result |
|---|---|
| `cheme validate` | 17 files, 0 errors, 0 warnings; info only (`cheme.decision-unknown` for D-601, D-012, D-023; DEXPI loader cycles) |
| `cheme check` | every concept gate passes except `layout-plot-plan` (out of scope for this case); basic gates `pids-exist`, `design-review`, layout, mto and datasheets fail as expected for a concept case |
| `cheme maturity` | `level: none`; `maturity-claim-exceeds` warning (claims concept); fails `sourced-boundary` and `balanced-model-basis` because every feed and conversion is assumed |
| `cheme process streams` | 6 blocks and 12 steps balance; extents CALC 410.7, COMB 270.3, SLAKE 410.7, CARB 782.3, BICARB 391.2, DIST 391.2 kmol/h |
| `cheme process propagate --check` | clean, no output |
| `cheme assess lca --coverage` | partial screening carbon footprint, 11 gaps (10 missing backgrounds + NH3 uncharacterised); mass, element and carbon-origin balances closed |
| `cheme run scripts/solvay_balance.py` | reproduces every stream and duty of `flowsheet.yaml` |
| `cheme process furnace KILN` | specific-energy fallback, 4.0 GJ/t x 26.55 t/h lime = 29.5 MW, matches 3648 kg/h coke at 29.11 MJ/kg |

The report's claims (0 errors, balances closed, 13.299 kg in = out per kg product, maturity
none vs claimed concept) are confirmed.

## Engineering checks (my own hand calculations)

- **Route and boundary** match #177: classical Solvay process with explicit CaCl2 waste and kiln
  CO2, kept apart from trona and the Hou process; gate-to-gate foreground from purified brine
  to light ash at the calciner outlet (D-001, DESIGN.md section 1).
- **Stoichiometry**: NaCl in 1071.7 kmol/h, NaHCO3 782.3 kmol/h -> sodium utilisation 0.73;
  Na2CO3 391.16 kmol/h = 41.46 t/h = 99.5 % of 41,667 kg/h. Ca(OH)2 410.7 kmol/h / 391.2 kmol/h
  needed = 1.05 excess lime. CaCl2 1.04 t/t (theory 1.047 t/t). NH3/NaCl in S11 = 1.10.
  Residual NaCl to the waste 0.40 t/t, consistent with 0.73 utilisation less the product's 0.5 %.
- **CO2 balance**: kiln 681 kmol/h (calcination 410.7 + coke 270.3, 719 kg/t), calciner
  391.2 kmol/h; towers fix 782.3; vent 290 kmol/h = 306 kg/t. Kiln gas 36.6 mol% CO2, plausible
  for a mixed-feed shaft kiln. Kiln O2 excess 297.3/270.3 = 1.10.
- **Heats of reaction**: SLAKE, CARB, BICARB and DIST are consistent with the formation
  enthalpies quoted next to them; CALC is not quite (R-04).
- **Duties**: kiln gas compressor 1859 kmol/h, 101 -> 350 kPa, eta 0.75: my estimate 2.6 MW vs
  2.62 MW given. Calciner: decomposition 14.7 MW + cake water evaporation ~7 MW + sensible
  ~3 MW + 10 % losses ~27.5 MW vs 28.2 MW given. Absorber (22 MW) and tower (21 MW) cooling are
  of the expected order. Saturation water contents of S12, S15 and S5C are consistent with
  their temperatures.
- **Consumptions per t soda ash vs general knowledge of Solvay plants**: salt 1.50 t (typical
  ~1.5-1.8), limestone 1.08 t (typical ~1.1-1.5), coke 88 kg, live steam 1.88 t, distiller waste
  11.2 t, vented CO2 306 kg, power 112 kWh: all inside or at the optimistic edge of the usual
  ranges; DESIGN.md D-006 says so itself.
- **LCI**: per 1 kg light soda ash, every exchange from a flowsheet terminal with its stream id;
  inputs 13.299 kg = outputs 13.299 kg; no zero-filled background, every background `missing:`
  with the activity it should link to; `factors.yaml` carries only the packaged open DESNZ
  profile (no licensed values); kiln pollutants excluded with a reason, not set to 0.
- **Sources and licences**: no third-party tables, figures or passages found; values cited
  are single facts in own words (BREF kiln heat-use range, formation enthalpies, cross-check
  ranges). Estimates are marked ASSUMED throughout the YAML and DESIGN.md.
- **Maturity**: `process.yaml` claims `concept`, the lowest value the manifest schema allows,
  with `validation.status: unreviewed` and notes that say every parameter is assumed. Honest,
  though `cheme maturity` supports no level (R-06).

## Findings

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| R-01 (2026-10-27-pfd-lci-review#1) | lca/results.md:14, lca/results.csv | LCA headline | The only number the LCA reports is 0.306 kg CO2-eq/kg, with a Monte Carlo 95 % interval of 0.21-0.45. That is the direct vent CO2 alone: 10 of 12 burdened exchanges are gaps, including steam (1.88 t/t + 2.43 GJ/t), coke, limestone, brine and power. A cradle-to-gate footprint for Solvay ash is several times larger. The file does say "partial screening" and "with gaps", but with `process.yaml` `lca: {source: auto}` a catalogue reader can take 0.306 (and its tight interval) as the product footprint. Nothing in `process.yaml` or `lca/` says in plain words that it is the direct process emission only. | medium | open | State in `process.yaml` `validation.notes` (and the `lca.yaml` goal) that the reported value is the direct (scope-1 process) CO2 only and not a carbon footprint, and that the interval covers only the vent CO2 amount. Or hold the LCA out of the catalogue until the backgrounds are mapped. |
| R-02 (2026-10-27-pfd-lci-review#2) | DESIGN.md D-006; process/reactions.yaml:30 | sodium utilisation and other D-006 parameters | Every parameter that sets the raw-material and waste flows of the LCI is unsourced: sodium utilisation 0.73, NH3/NaCl 1.10, excess lime 5 %, cake moisture, NH3 losses. The "about 70-75 %" range is credited to "the Solvay literature" with no locator, and the two named leads (Ullmann, LVIC-S BREF) were not read. Limestone (1.08 t/t) and salt (1.50 t/t) sit below the author's own cross-checks (USGS 1.4 and 1.7 t/t). This is marked ASSUMED and called optimistic, so it does not mislead, but it biases the inventory low. | medium | open | Next stage: source each D-006 parameter with a locator (LVIC-S BREF soda ash chapter, Ullmann). Until then, add a sensitivity case (e.g. utilisation 0.70, excess lime 10-20 %) or state the direction of the bias in `process.yaml` notes. |
| R-03 (2026-10-27-pfd-lci-review#3) | DESIGN.md D-006 (energy sanity check) | total energy 9.7 GJ/t | The total adds quantities on different bases: kiln fuel LHV (2.55 GJ/t), the condensing duty of the live steam (4.3 GJ/t = QD 49.8 MW, not the steam's enthalpy above feed water, ~5.0 GJ/t), HP-steam heat delivered (2.43 GJ/t, not boiler fuel) and power (0.4 GJ/t, not primary). It then compares that sum with a 9.7-13.6 GJ/t range whose basis is not stated, and calls the result "at the low end". On a consistent basis the figure would move. | low | open | State the basis of each term and of the literature range, or drop the comparison until the range is traced to its primary source. |
| R-04 (2026-10-27-pfd-lci-review#4) | process/reactions.yaml:9 | CALC heat of reaction | The stated formation enthalpies (CaCO3 -1207.6, CaO -635.1, CO2 -393.5 kJ/mol) give +179.0 kJ/mol, but the file gives 178300 J/mol. 178.3 corresponds to calcite at about -1206.9 kJ/mol. The effect is small (no energy balance uses it yet). | low | open | Correct the CaCO3 value in the source text or the result. Check all values against the NBS table as D-007 already plans. |
| R-05 (2026-10-27-pfd-lci-review#5) | DESIGN.md D-006; process.yaml:61-67 | cross-check sources | The USGS Minerals Yearbook 1992 and the "literature review" behind 9.7-13.6 GJ/t are used in D-006 but are not in `process.yaml` `references:`, and DESIGN.md gives no locator or URL for them (only the run report has links). The EMEP/EEA link is to the 2019 edition in `process.yaml` but to the 2016 edition in the run report. | low | open | Add both sources to `references:` with locators, cite one EMEP/EEA edition consistently, and mark the energy range as secondary or untraced. |
| R-06 (2026-10-27-pfd-lci-review#6) | process.yaml:32-46 | maturity / validation notes | `cheme maturity` gives `level: none` and warns `maturity-claim-exceeds`. `concept` is the schema's lowest value and the notes are candid, but they do not mention that the checked evidence supports no level. | low | open | Add one sentence to `validation.notes` saying that `cheme maturity` supports no level until feeds and conversions are sourced. |
| R-07 (2026-10-27-pfd-lci-review#7) | equipment/equipment-list.yaml:34; process/flowsheet.yaml:277-283; piping/line-list.yaml | tag D-601 | The distiller's tag D-601 matches the decision-id pattern, so `cheme validate` reports `cheme.decision-unknown [D-601]` four times. The flowsheet comment "D-006: heater..." sits right above `ref: D-601`, so decision ids and the equipment tag are easy to confuse. | low | open | Retag the distiller (e.g. C-601 / T-601) with `cheme rename` across the lists and the flowsheet, or accept the info finding with a reason. |
| R-08 (2026-10-27-pfd-lci-review#8) | lca/lca.yaml (DSW, kiln pollutants) | water and air emissions | The largest environmental burden of the Solvay route, the dissolved CaCl2 (1.04 t/t) and NaCl (0.40 t/t) of the distiller waste, appears only inside the `missing:` text of `product:DSW`. Kiln CO, NOx, SO2 and dust are excluded with no amount (`cheme.lca-cutoff-unchecked`). Both gaps are described, so this is complete as a gap list, but no amount is given for them. | low | open | When the backgrounds are mapped, give the DSW discharge as elementary flows to water (or a dataset that carries them), and an amount for the kiln pollutants from the lime BREF ranges so the cut-off rule can be checked. |
| R-09 (2026-10-27-pfd-lci-review#9) | process/flowsheet.yaml (E101), equipment-list E-101 | kiln gas washer | E-101 is a "washer-cooler (direct contact)" but has no wash-water inlet or blowdown, so kiln dust removal and its water and sludge are not in the balance or the LCI. | low | open | Either call E-101 an indirect cooler at this stage, or add the wash water and blowdown streams (to the DSW or a separate waste), with an ASSUMED dust load. |

No critical or high findings. The balances close and are reproduced by an independent script.
The LCI is per functional unit and matches the flowsheet. Every gap is declared and none is
zero-filled. Nothing outside `processes/soda-ash-1/` changed.

## Previous findings

None (first review of this case).

## Merge

`case/soda-ash-1` is not merged; `merge: pending`. The medium findings R-01 and R-02 should be
fixed or accepted by a human before the case is listed in the catalogue. They do not block the
merge.
