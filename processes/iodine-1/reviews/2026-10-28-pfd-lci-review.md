---
topic: design
reviewed_commit: 9ed2c76f075aad4367d92b06dbf86f95c0536be3
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/simulation.yaml, process/BFD.xml, process/PFD.xml, equipment/equipment-list.yaml, scripts/iodine_balance.py, lca/, PROGRESS.md, runs/20261028-162105-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/iodine-1
merge: pending
---
# Review: design (iodine-1 concept PFD and preliminary LCI, issue #145)

Independent agent review of the branch `case/iodine-1` (commits 3f75583..9ed2c76) against
origin/main (merge base cc5624f). The reviewer did not write the design and changed no design
file. Every command below was re-run by the reviewer at 9ed2c76.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | DESIGN.md:139-144 | D-005, T-201 air ratio | DESIGN.md calls the 130 Nm3/m3 air ratio "conservative" (and the run report repeats it), based on a stripping factor of about 3.7 from the fresh-water Henry constant (SRC-11; the arithmetic checks out: 1.5e-2 mol/(m3 Pa) at 313 K, K_gl 0.026, 144 m3/m3). The check only names salting-out (which raises volatility) and triiodide. It leaves out chloride complexation of iodine (I2Cl-) in a brine with about 1.9 mol/kg chloride. That complex lowers the free I2 and so the effective stripping factor: with a formation constant of the order of 1-2 kg/mol (the reviewer's recollection, to be verified), the factor drops to about 1. A stripping factor near 1 cannot give 92 % stripping at any number of stages. So "conservative" is not supported. The value itself is marked ASSUMED, the balance is unaffected, and it sets about 17 % of the power (K-201). | medium | open | Drop "conservative". Present the Henry check as a fresh-water upper bound, name chloride complexation as an open factor next to I3-, and add the air ratio to the gated T-201 sizing (D-007). Optionally give the K-201 power at 2x the air ratio as a sensitivity. |
| 2026-10-28-pfd-lci-review#2 | lca/lca.yaml:33-113, lca/gaps.csv | every `missing:` background | All 10 unmapped backgrounds carry the same `missing:` text, "background not mapped yet (preliminary LCI)". So gaps.csv, results.md and the dataset (the published gap list) give no description of what each gap needs. The activity to connect is only in the `source:` prose of lca.yaml. D-011 says the flows carry "`missing:` with the activity to connect", which is not what the files contain. | medium | open | Put a short description of the activity to connect in each `missing:` (e.g. "chlorine gas, membrane chlor-alkali (chlor-alkali-1 CL2); not mapped yet"), then rerun `cheme assess lca --write`. |
| 2026-10-28-pfd-lci-review#3 | process.yaml:286-292, DESIGN.md:53,164, design-basis.yaml:390 | overall recovery 90 % | The 90 % recovery and 29.8 mg/kg left are presented as agreeing with or matching US 2013/0243684 A1 (90 % recovery, about 30 mg/L returned). But the 90 % is the product of ASSUMED yields that were chosen (98 % x 92 % x 99.5 % x 99.5 % x 99 % with recycles). The 30 mg/kg then follows by arithmetic from 300 mg/kg x (1 - 0.90). This is calibration to the patent, not an independent check. A reader of the Atlas validation notes may take it as evidence that the model is validated. (The reviewer confirmed that the patent background does state "approximately 300 mg/L or greater" and "for 90% recovery ... perhaps 30 mg/L".) | medium | open | Reword in process.yaml validation.notes, the DESIGN.md basis table and D-006, and the design basis: "yields chosen within sourced ranges so that the overall recovery equals the 90 % that SRC-3 states" (calibrated, not a check). |
| 2026-10-28-pfd-lci-review#4 | equipment/equipment-list.yaml:33 | M-301 | Design temperature 145 °C is below the saturation temperature of the LP steam that heats its jacket (450 kPa(a), 420.8 K = 147.7 °C, design-basis.yaml:48). The "+25 K over operating" rule of D-010 was applied to the 393 K melt, not to the heating medium. | low | open | Set the M-301 design temperature to at least the steam saturation temperature plus margin (e.g. 175 °C), or state the jacket and shell design temperatures separately. |
| 2026-10-28-pfd-lci-review#5 | lca/lca.yaml:139-158, flowsheet.yaml:457 (S19) | melter vent, exclusions | The balance sends all of the cake's HCl into the spent melter acid (S19: 1.2 wt% HCl in about 66 wt% H2SO4 at 393 K) and no iodine to a vent. Iodine's vapour pressure near its melting point is of the order of 10 kPa, and HCl is poorly retained by hot concentrated H2SO4. The three exclusions (fugitive leaks, melter vent, storage/unloading) carry no amount, so the cut-off rule cannot be checked (`cheme.lca-cutoff-unchecked`). This is disclosed as open, hence low. | low | open | Give each exclusion an upper-bound amount in kg/a (e.g. the melter vent at the HCl of S17 and iodine saturation of the vent gas), so the 1 % rule is checked. Design the melter vent scrubber in the next stage. |
| 2026-10-28-pfd-lci-review#6 | process/design-basis.yaml:346, process.yaml:288-289 | SRC-2 attribution | The design basis and the Atlas validation notes cite "USGS Minerals Yearbook 1987". The 1987 yearbook is a US Bureau of Mines publication, as the DESIGN.md source register (SRC-2) correctly says, and it was read only as a search-result extract. In addition, the SRC-5 row of the register calls pH 3 the "lower limit for full liberation", while D-004 (correctly, from the patent's wording) calls it the upper pH limit. | low | open | Write "US Bureau of Mines, Minerals Yearbook 1987" in both files. Read the chapter page (p. 466) or label the fact as from an extract. Make the SRC-5 wording "pH about 3 (the highest pH for complete liberation)". |
| 2026-10-28-pfd-lci-review#7 | DESIGN.md:26-29 | SRC-3..SRC-6 locators | The patent facts were taken from Google Patents "machine summaries", and the locators are section-level only ("Background", "description and claims 1-6"). The reviewer spot-checked SRC-3 (300 mg/L, 90 %/30 mg/L, lime) and SRC-5 (pH about 3, chlorine equivalent to iodine, 0.50-0.54 V end point, 90-100 % blown out "without excessive air"): both are correct. | low | open | Add paragraph or column/line locators for each fact used (e.g. US 2013/0243684 A1 [0003]-[0005]; US 1,897,031 page and line numbers). |
| 2026-10-28-pfd-lci-review#8 | lca/lca.yaml:117-118 | emission:I2 | The iodine emission is characterised as "air, fossil" (the default origin) and has no subcompartment. A carbon origin is meaningless for I2, and its identity is not in the crosswalk (`cheme.lca-flow-identity`). | low | open | Give `elementary.subcompartment` (the loop purge is a stack release) and, if the schema allows, no carbon origin for non-carbon flows. Otherwise note it as a core limitation. |
| 2026-10-28-pfd-lci-review#9 | equipment/equipment-list.yaml:19, DESIGN.md:186-188 | P-202 / T-202 liquid rate | 30 m3/h of absorbent against about 62,000 m3/h of loop gas (L/G of about 0.43 kg/kg). For a packed tower of roughly 3 m diameter at a typical gas velocity, that is a wetting rate of about 4 m3/(m2 h), below the usual minimum wetting rate of random packings. This affects only P-202 power (4 kW), so it does not touch the balance. | low | open | Check the absorber liquid rate against the minimum wetting rate when T-202 is sized. Raise the circulation or choose a packing or contactor suited to low liquid rates. |
| 2026-10-28-pfd-lci-review#10 | process/flowsheet.yaml:204-214 | M301 model basis | `cheme maturity` lists M301 (class SeparatingByPhaseSeparation) as "equilibrium-stage, predictive, sourced", although its outlets S19/S20 are ASSUMED values from scripts/iodine_balance.py. This misreport comes from the core's inference, not from the design. It overstates the model basis of one step to a reader of the maturity report. | low | open | Report it to core. Meanwhile, list M301 as "specified (script values)" in the DESIGN.md method table, which today names only T-201, F-301 and M-301 together as specified splits, consistently. |
| 2026-10-28-pfd-lci-review#11 | checks/checks.yaml | gates | `cheme check` fails `layout-plot-plan` (concept) and, of the basic and detail gates, `pids-exist`, `design-review`, `layout-3d`, `lifting-study`, `mto`, `layout-review`, `layout-detail`, `electrical`, `hvac` and `datasheets`. All are outside issue #145's scope (route, design basis, BFD/PFD, preliminary LCI; DESIGN.md run record), and no stage sign-off is claimed. `design-review` is answered by this record. | low | open | Either record the out-of-scope gates as such (a plant.yaml issue, or a note in STAGES.md/DESIGN.md), or have a human accept them for this case study. No sign-off is possible until then. |

## Previous findings
None: this is the first review record of iodine-1 (`reviews/` held only README.md).

## Drawing
No P&ID exists (`pid/` holds only its README), so `cheme validate` prints no `drawing <sheet>:`
line. The BFD and PFD are generated by `cheme process build` from the YAML. `cheme validate`
compared both sheets with 0 errors and 0 warnings (only `dexpi.load` cycle infos). The reviewer
rendered `build/PFD.png` (scale 2) and read it as a whole. The blocks OXD, BLO, REC and NEU, the
11 steps, the 24 material streams and Q1-Q6 are present and labelled. Long recycle and utility
lines (S14, S16, S19, S22, Q1-Q5) cross the sheet, as is usual for the generated layout; no
`layout.pfd` positions are pinned. This is not a finding at concept stage. No tiles were read.

## Checked and fine
- **Scope and boundary.** The route (natural iodide brine, blowing-out: acidification,
  chlorination, air blow-out, SO2/HI absorption, chlorine precipitation, filtration, melting
  under H2SO4, flaking, neutralisation and reinjection) and the boundary (wellfield and
  reinjection wells outside; chlorine and caustic from chlor-alkali-1, acid from sulfuric-acid-1)
  match #145. The choice of brine over caliche is reasoned in D-001.
- **Nothing outside the folder.** `git diff --name-only origin/main...HEAD` lists only files
  under `processes/iodine-1/`. The two-dot diff shows thf-1 "deleted" only because origin/main
  moved on after the branch point.
- **`cheme validate`.** 17 files, 0 errors, 0 warnings. Infos: `cheme.decision-unknown D-023`,
  which comes from a commented template example in checks/checks.yaml:76 and is harmless.
- **Process tools.** `cheme process streams` shows every block and step balanced on mass with
  extents. `cheme process propagate --check` runs clean with nothing to report.
- **Balance script.** `cheme run scripts/iodine_balance.py` reproduces the flowsheet values:
  plant in 466 939.411 kg/h, out 466 939.407 kg/h; recovery 0.9002; free acid 3.84 mmol/kg,
  pH about 2.4.
- **Stoichiometry, checked by hand.**
  - Chlorine 0.614 kg/kg (two oxidations of about 0.28 kg/kg each, plus 5 % excess on the total
    iodide). S2 is 0.576 kmol/h against 1.05 x (0.5455 + 0.0025).
  - SO2 0.281 kg/kg: (ABS 0.499 + CLSA 0.038) x 1.02 = 0.548 kmol/h.
  - Caustic 71 kg/h NaOH = 1.78 kmol/h. This equals the H+ from SO2 (4 per SO2) plus the fresh
    acid, minus the alkalinity of 0.924 kmol/h.
  - CO2 40.7 kg/h = the alkalinity.
  - Iodine: in 138.58 kg/h, product 124.75 kg/h, spent brine 13.80 kg/h, vent 0.03 kg/h.
  - Loop gas water at 6.8 mol% is consistent with 313 K saturation over brine.
  - K-201 (about 98 kW hydraulic/0.7 for 17 m3/s at 4 kPa), P-401 (0.121 m3/s at 3000 kPa/0.75
    gives about 484 kW), melter steam and flaker duties all reproduce within a few per cent.
  - Henry-constant arithmetic of D-005 (SRC-11) is correct; its interpretation is finding #1.
- **Plausibility.** About 3.7 t of brine per kg of iodine is what 300 mg/kg and 90 % recovery
  imply. Chlorine and SO2 are slightly above stoichiometry. The power is dominated by
  reinjection, and the ASSUMED reinjection pressure is flagged as the least known value. All of
  this is plausible for this technology.
- **Sourcing.** Every key value is sourced or ASSUMED: the design basis and flowsheet mark
  ASSUMED values and give a source for each stream value. Ullmann (licensed) was not used for
  values. No third-party table, figure or passage was found copied. The facts are restated, and
  SRC-11 is CC BY.
- **LCI per functional unit.**
  - FU 1 kg iodine. Per-FU mass in 3735.52 kg = out 3735.52 kg; the LCI is consistent with the
    flowsheet (S1, S2+S14, S11, S18, S22, S12, S10, S24, S7, Q1-Q6, divided by 125 kg/h).
  - `cheme assess lca --coverage`: mass, element and carbon-origin balances closed. The result
    class "partial screening" is honest.
  - No zero-filled and no licensed background. lca/factors.yaml uses only the open packaged
    profile.
  - Every unmapped background is in gaps.csv (10 plus the uncharacterised I2); the quality of
    their descriptions is finding #2.
  - lca/mappings.yaml has no overrides, and says why.
  - product:SPENT notes that the injection pump is in the foreground (avoids double counting
    when the background is mapped).
- **Maturity.** process.yaml claims `concept`, and `cheme maturity` supports none
  (`cheme.maturity-claim-exceeds` warning). concept is the lowest value the schema allows. The
  shortfall is disclosed in D-012 and in a process.yaml comment, and `validation.status:
  unreviewed` is set. This is honest.
- **Run record.** The run report agrees with what the reviewer re-ran (0 errors, balances,
  LCI numbers, gates).

## Not checked
- Thermodynamic correctness of the stripping and absorption splits, speciation (I-/I3-/I2Cl-,
  HOCl, HSO4-) and the energy balance: gated in core (electrolytes #364, solids #365). No
  qualified model exists in this core.
- The SRC-1, SRC-2, SRC-4, SRC-6 and SRC-11 pages were not re-read; only SRC-3 and SRC-5 were
  spot-checked.
- Heats of reaction in process/reactions.yaml (NBS values recalled by the author, ASSUMED).
- Equipment materials (FRP, linings, Hastelloy flaker) beyond plausibility; no corrosion review.
- P&IDs, layout, HAZOP, datasheets, TEA: none exist (outside #145's scope).
- The PFD drawing was read as a whole only, not in tiles.
- `cheme diff main --list` lists only added objects (a new process folder: the BFD and PFD
  streams S1-S24, sources, sinks, templates); no modified plant item exists to trace.

Merge: pending. No critical or high finding is open; the medium findings #1-#3 should be fixed
before the case is published in the Atlas.
