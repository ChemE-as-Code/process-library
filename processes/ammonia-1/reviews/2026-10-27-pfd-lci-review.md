---
topic: design
reviewed_commit: ab23125f9cc99834f63315b331e0db9da3a7b2b3
scope: [DESIGN.md, process.yaml, plant.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/simulation.yaml, process/narrative.md, equipment/equipment-list.yaml, lca/, scripts/plant_balance.py, runs/20261027-212934-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/ammonia-1
merge: pending
---
# Review: design (concept PFD and preliminary gate-to-gate LCI, issue #86)

An independent agent reviewed the five commits on `case/ammonia-1` (`7c07c13..ab23125`)
against `origin/main`. I did not write the design. Every command below was re-run by me at
`ab23125`; the run report's figures were not taken on trust. Finding numbers R-01 ... map to
the ids `2026-10-27-pfd-lci-review#n`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-27-pfd-lci-review#1 | lca | `lca/results.md`, `lca/results.csv`; DESIGN.md:219; runs/20261027-212934-design/report.md | R-01: DESIGN.md D-020 says "no impact result is claimed (the generated results.md is a placeholder with all gaps)". But the generated `results.md` and `results.csv` report **1.563 kg CO2-eq per kg NH3** as a "partial screening carbon footprint", and `cheme assess lca --coverage` repeats it. The figure is only the plant's direct fossil CO2 (vent plus stack). It leaves out the natural-gas supply chain (including methane leakage), the 0.563 kWh/kg of electricity, the steam credit and the other backgrounds, so it is not a footprint of the product. The words "with gaps" and "partial" are there, but the record and the generated output contradict each other. With `lca: source: auto` in process.yaml, a catalog could also pick the number up as the result. | medium | open | Correct D-020 and the run report to say what is actually published: a direct-emissions-only figure, labelled as gate-to-gate direct CO2 and not a carbon footprint. Alternatively, keep `results.*` from being harvested as an impact result until the backgrounds are linked (I-10). |
| 2026-10-27-pfd-lci-review#2 | lca | `lca/lca.yaml:51-56`; `lca/inventory.csv` emission:CH4/CO/H2/NH3/C2H6/C3H8; H-101 | R-02: Six emissions to air stand in the inventory at **0 kg** with provenance `assumed`. The zeros come from modelling choices: complete combustion (D-014), no co-absorption of H2/CH4 in the aMDEA CO2 vent (D-009), and no slip or fugitives. They are not a known absence. CH4 is even characterised (GWP 29.8 times 0) in `results.csv`, so it shows as covered and not as a gap. `cheme assess lca --coverage` still warns `cheme.lci-emissions-incomplete [H-101]` (no `emission_estimates` and no `emission_exclusions`). The run report (line 31) says "nothing is set to zero". D-020/I-07 do describe the missing furnace NOx/CO/CH4/N2O, but the CO2-vent CH4/H2 slip is not named in the CH4/H2 source texts. | medium | open | Add `emission_exclusions` (or sourced `emission_estimates`) for H-101 and the C-301 vent, each naming I-07, so these flows appear in `gaps.csv` and not as characterised zeros. Name the vent co-absorption in the CH4/H2 source texts. Correct the run report sentence. |
| 2026-10-27-pfd-lci-review#3 | process | `process/design-basis.yaml` feeds; `process/flowsheet.yaml:365` (S1) | R-03: Issue #86's brief requires the natural-gas composition and supply pressure to be "given, with a source". The design uses an ASSUMED benchmark lean gas (CH4 91 / C2H6 4 / C3H8 1 / CO2 1 / N2 3 mol%, 4500 kPa(a)), declared openly in D-004 and I-01 and marked "not Rotterdam pipeline gas". This is honest, but the feed drives every LCI figure (gas per kg NH3, CO2) and blocks `cheme maturity` at every level (`maturity-sourced-boundary`). The issue's done-when (`balanced`) is not reached. | medium | open | Before the next stage, take a published Dutch H-gas quality (composition, pressure, sulfur) with its source, set S1 to `given`, rerun `scripts/plant_balance.py` and regenerate the LCI. |
| 2026-10-27-pfd-lci-review#4 | process.yaml | `process.yaml:38-49` | R-04: `maturity: concept` is the lowest value the schema allows (`schemas/process.schema.json`), and D-019 explains it, but `cheme maturity` puts the plant at **level none** and warns `cheme.maturity-claim-exceeds`. `validation.notes` lists the reasons (assumed feed, specified separators) but never says that the checked maturity is none. An Atlas reader sees only "concept". | low | open | Add one sentence to `validation.notes`: "`cheme maturity` reaches no level (feed not sourced; separators specified); concept is the lowest manifest value (D-019)." |
| 2026-10-27-pfd-lci-review#5 | process | `cheme process streams`, block REF | R-05: The block-level reaction extents of REF are not the sum of its step extents. The block reports CH4_COMB 0 kmol/h, although step H101 inside it burns 495.9 kmol/h. It also reports H2_OX 1573.7 against R102A's 486.5, and SMR 1996.6 against 887.6 + 613.0. The reaction set (reforming, shift, H2 oxidation, combustion) is linearly dependent, so the block extents are not unique. Mass, component and element balances close, so this is a reporting artefact, but a reader of the stream table can be misled. | low | open | Report to cheme-as-code (core) that block extents should be summed from the steps, or flagged as non-unique when the reaction set is dependent. Optionally add a note in DESIGN.md D-006. |

## Previous findings
None: this is the first review of this process (`reviews/` held only README.md, and
`grep -h '| open |' reviews/*.md` found nothing before this record).

## Drawing
No P&ID in scope (`pid/` empty; P&IDs are out of this stage's scope, D-018). `process/BFD.xml`
and `process/PFD.xml` are generated by `cheme process build`. `cheme validate` printed no
`drawing` line for them and no `generated-sheet-drift` or `cheme.generated-edited` finding. The
generated sheets were not rendered or read tile by tile (see Not checked).

## Checked and fine
- **Scope of the change**: `git diff --name-only origin/main..HEAD` touches only
  `processes/ammonia-1/` (190 files). The commits each carry a reason, and PROGRESS.md and
  DESIGN.md cover them.
- **Re-run at ab23125**: `cheme validate`: 17 files, 0 errors, 0 warnings. It compared BFD,
  PFD and 12 lists, with no list-vs-P&ID cross-check (no P&ID). The infos are the DEXPI
  port-cycle notes and `cheme.decision-unknown [D-023]` from the template comment in
  `checks/checks.yaml:76`, which is harmless. `cheme check`: every concept gate passes except
  `layout-plot-plan`. At basic, `pids-exist`, `design-review`, the layout gates and `mto`
  fail; `datasheets` fails at detail. All of these are outside this stage's scope (D-018),
  and `design-review` is closed by this record. `cheme maturity`: level none, claim
  exceeds (R-04). `cheme process propagate --check`: no change or deviation. `cheme process
  streams`: all 7 blocks and 51 steps `ok` on mass. The largest residuals are 2.4 kg/h
  (SYN, E501, V201), explained in D-006 by the molar masses. `cheme assess lca --coverage`:
  mass, element and carbon-origin balances closed at 5 %; 11 gaps, each described (6
  backgrounds `missing:` with the activity they should link to, 5 uncharacterised
  zero-flow emissions).
- **Route and boundary** match issue #86, option A: SMR with an air-fed secondary reformer,
  Rotterdam area, 1500 t/d, CO2 vented, no urea or storage. The second, loop-only scope is
  declined with a reason (section 1). No benchmark values were used (source register),
  which respects the issue's blind-benchmark rule.
- **Plausibility** (my own estimates, general engineering knowledge, not from the cited
  sources):
  - Carbon: the assumed gas has 0.706 kg C per kg. 0.6034 kg NG per kg NH3 then gives
    1.561 kg CO2, plus about 0.003 kg from the air, which matches the 1.563 kg inventoried.
  - Gas use: the gas LHV is about 46.1 MJ/kg, so the gas fed is about 27.8 GJ/t NH3 (process
    feed 21.8, fuel 6.1). There is also 2.0 GJ/t of electricity and an MP-steam export of
    0.88 t/t. That is plausible for a conventional SMR plant with electric drives.
  - Compressors: from the stream flows, I estimate 8.5 MW for the process-air compressor
    (67.3 t/h, 4 stages to 3600 kPa(a), eta 0.78) and 12.5 MW for the synthesis-gas
    compressor (about 7400 kmol/h, 3 stages to 14,600 kPa(a)). D-016 gives 8.6 and 12.5 MW.
  - Steam: steam to carbon 3.0 gives about 93.7 t/h of process steam (D-015: 92.8 t/h).
  - Flue gas: S61 + S2 + S59 = S67 (176.4 t/h).
  - Other indicators are in the usual ranges for this technology: converter 3.4 to 17.8 mol%
    NH3 at about 151 bar, 12 % inerts, purge 0.74 %, secondary-reformer CH4 slip 0.26 mol%
    wet, LTS CO 0.28 mol% wet, radiant efficiency 56 %, process CO2 1.17 t/t, total direct
    CO2 1.56 t/t.
- **Provenance**: the feed, conditions, approaches, splits, recoveries and efficiencies are
  marked ASSUMED in the design basis, the flowsheet (`[A]`) and DESIGN.md. Reactor outlets
  are `[C]` by cheme's equilibrium and conversion models. D-006 states openly that the
  script's flash and duty methods are not qualified (core #315).
- **LCI**: it is per 1 kg NH3. Every exchange traces to a flowsheet terminal (the `streams`
  column of `inventory.csv`). The inventory balances (in 5.94962 kg, out 5.94970 kg). No
  background is zero-filled and no licensed value is used: `factors.yaml` holds only the
  IPCC AR6 GWP100 profile, cited. The steam credit is by substitution, with a reason (D-021).
- **Licences**: DESIGN.md, the design basis, narrative.md and process.yaml are in the authors'
  own words. Facts are cited (thermo/chemicals, IAPWS, cheme reaction library, the skill's
  conditions table). No tables, figures or passages are copied, and nothing from a paid
  standard is used: ISO 12213-2 is explicitly not used.

## Not checked
- The rendered BFD/PFD drawings (not read tile by tile). They are generated, and validate
  reports no drawing findings.
- `scripts/plant_balance.py` was not re-run and its code was not read line by line. I checked
  its outputs only through cheme's balances and the hand estimates above. Energy closure is
  not evaluable in core (core #315), so the duties, the steam raised (148 t/h) and the
  cooling-water heat (2.10 kWh/kg) remain unchecked by any tool.
- The equipment list's 44 items were not compared one by one with the PFD (the
  `process-links` gate passes).
- Comparison with the held-back benchmark (`benchmarks/ammonia.yaml`, issue #86 section 2):
  not visible to this review, by design.
- P&IDs, layout, HAZOP and datasheets: not in this stage's scope.
