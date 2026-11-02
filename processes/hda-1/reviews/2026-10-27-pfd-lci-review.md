---
topic: design
reviewed_commit: 9af76cff96811003319877bc90009c621fd22271
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/simulation.yaml, process/BFD.xml, process/PFD.xml, equipment/equipment-list.yaml, piping/line-list.yaml, lca/, scripts/hda_balance.py, runs/20261027-212954-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/hda-1
merge: pending
---
# Review: design (concept PFD and preliminary LCI of hda-1, issue #42)

Independent review of the concept run on `case/hda-1` (commits ac221d3..9af76cf against
`origin/main`). Everything below was re-run by the reviewer at 9af76cf, not taken from the run
report. Finding labels R-01 ... are given in the finding text; the ids follow `reviews/README.md`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-27-pfd-lci-review#1 | lca/results.csv:2, process.yaml:74 | LCA total | R-01: every one of the 10 LCA contributions is a gap, yet `lca/results.csv` carries a `total` row with impact `0` and `results.md` shows `0` kg CO2-eq under mass and energy allocation. With `lca: {source: auto}` the library catalog takes that row as authoritative: `scripts/build_catalog.py` run by the reviewer writes `"totals": {"baseline": {"climate-change": 0.0}}` with `"boundary": "cradle-to-gate"` into `processes/hda-1.json`. The Atlas would show benzene from HDA at 0.0 kg CO2-eq per kg, cradle-to-gate: a zero-filled result the task and D-013 say must not exist. | high | open | Until a background is linked, set `lca: {source: none, notes: "foreground LCI only, every background a gap (D-013)"}` in process.yaml; report to core/library tooling that an all-gap category must not get a `total` row of 0 (or that `build_catalog.py` must drop a stated total when the manifest classification has every contribution a gap). |
| 2026-10-27-pfd-lci-review#2 | lca/lca.yaml:19, DESIGN.md:171, process.yaml:62 | system boundary | R-02: the boundary is labelled two ways. `lca.yaml`, `dataset.yaml`, `manifest.json` and `results.md` say `cradle-to-gate`; D-013, PROGRESS.md, process.yaml `validation.notes` and the run report call the same inventory "gate-to-gate". A reader of the dataset sees a cradle-to-gate dataset that has no upstream at all. | medium | open | Keep `cradle-to-gate` (gaps are honest there; the schema's `gate-to-gate` maps feeds free and would hide them) and reword D-013, process.yaml and PROGRESS.md to "cradle-to-gate study, foreground inventory only, every background a gap". |
| 2026-10-27-pfd-lci-review#3 | lca/lca.yaml:55, DESIGN.md:20, 134, 182 | omitted exchanges | R-03: omissions known in DESIGN.md are not declared in the LCA files, so `--coverage` reports "boundary check: no gap found" and the inventory has no emission, wastewater or waste row at all: fugitive emissions of benzene, toluene, CH4 and H2 (I-10); the C-203 vacuum system (ejector motive steam or vacuum-pump power, and, with ejectors, an aromatic-bearing condensate that contradicts "wastewater (none from the process)", I-08); P-102 and the reflux and distillate pumps (each ASSUMED < 5 kW). | medium | open | Declare each in lca.yaml (an `emission_exclusions` entry with its reason or a `missing:` exchange with an order-of-magnitude estimate marked ASSUMED) so gaps.csv and results.md name them; qualify the "no wastewater" statement on the vacuum-system choice. |
| 2026-10-27-pfd-lci-review#4 | DESIGN.md:78-100, 216-217; process/flowsheet.yaml:183 | reactor basis | R-04: the whole reactor basis (inlet >= ~895 K, outlet <= ~980 K, 3.45 MPa, H2/aromatics >= 5, selectivity S = 1 - 0.0036/(1-X)^1.544) rests on Douglas (1988) "recalled, not read", without chapter or equation; the conflict with Speight's 500-600 C is unresolved. The values agree with the reviewer's own knowledge of the Douglas HDA case and are honestly labelled (I-06), so this is not misleading, but the key basis is unverified and `cheme maturity` counts the selectivity as unsourced. | medium | open | Read the source and give chapter/section and equation in DESIGN.md, the flowsheet `source:` and process.yaml `references`; then give the selectivity `provenance: given`. State whether Speight's range refers to catalytic HDA. |
| 2026-10-27-pfd-lci-review#5 | DESIGN.md:90; runs/20261027-212954-design/report.md:23 | reaction heat | R-05: "~7 MW reaction heat" is a unit slip: 167.865 kmol/h x 41.76 MJ/kmol = 7.0 GJ/h = 1.95 MW. The conclusion stands (cheme's -45 kW is 2.3 % of 1.95 MW, and 1.95 MW over ~13.1 kg/s at cp ~3.5 kJ/(kg K) gives the reported 42 K rise), but the comparison is overstated 3.6-fold. | low | open | Write "~1.95 MW (7.0 GJ/h)" in D-005. |
| 2026-10-27-pfd-lci-review#6 | process/flowsheet.yaml:239, 463, 529; DESIGN.md:144 | implicit pumps | R-06: pressure rises without a step: S17 leaves the splitter SPL2 at 3450 kPa(a) from a 3250 kPa(a) inlet (P-102 is in the equipment list and linked, but not a pumping step on the PFD); S23 leaves C-203 (30 kPa(a)) at 150 kPa(a). P-101's power is counted from 30 kPa(a) for the whole 20.5 t/h although only S23 (4.9 t/h) comes from vacuum and S2 is at 150 kPa(a). Effects are < 1 kW; it is a consistency point. | low | open | Add P102 (and a C-203 distillate pump) as steps once the core `Pumping` bug (D-011) is fixed, or note the implicit pumps on the streams; count P-101 from 150 kPa(a) and the distillate pump separately. |
| 2026-10-27-pfd-lci-review#7 | process/flowsheet.yaml:139, 169; process/PFD.xml | PFD symbols | R-07: because of the core build bug (D-011) the fired heater H101 is drawn as a plain heat-exchanger symbol and P101 as a box (`GeneratingFlow`); a reader of the PFD alone cannot see that H-101 is fired. The core bug has no issue number yet. | low | open | File the core bug, cite its number in D-011, revert to `HeatingInFurnace` / `Pumping` once fixed. |
| 2026-10-27-pfd-lci-review#8 | lca/lca.yaml:42-49 | LHV for allocation | R-08: the benzene and biphenyl LHVs are on a gas basis (40.58 MJ/kg) although both leave as liquids (benzene liquid ~40.1 MJ/kg). This shifts the energy-allocation share of benzene by well under 1 percentage point, and the basis is stated. | low | open | Use liquid-phase formation enthalpies for the liquid products, or keep it and say why. |
| 2026-10-27-pfd-lci-review#9 | DESIGN.md:166-169; lca/lca.yaml:31 | fuel-gas credit | R-09: under the proposed substitution the fuel gas (0.275 kg, about 14.9 MJ LHV per kg benzene, 17 times the fired heat) displaces natural gas heat. Once linked, this credit is likely to dominate the footprint and to depend mostly on the site's fuel balance (D-009 itself names burning the purge in H-101 as the usual alternative). | low | open | When backgrounds are linked, show the result under substitution and under energy allocation side by side, and a case with the purge fired in H-101. |
| 2026-10-27-pfd-lci-review#10 | lca/manifest.json:47; lca/results.md | publication | R-10: the LCA outputs say `publication: public`, `publishable: true` while process.yaml says `publication.status: internal`. | low | open | Set the LCA publication to match the manifest (or confirm which one governs) before any public catalog build. |
| 2026-10-27-pfd-lci-review#11 | scripts/hda_balance.py:24 | docstring | R-11: the docstring still says column duties use "saturated feeds", but after the fix recorded in PROGRESS.md they use the arriving feed enthalpy (D-008). | low | open | Correct the docstring. |
| 2026-10-27-pfd-lci-review#12 | checks/checks.yaml | gate layout-plot-plan | R-12: `cheme check`: the concept gate `layout-plot-plan` fails (no site plan, no placement). Layout was outside this run's scope, as the run report says, but the concept stage cannot be signed off with it failing. | low | open | Do the plot plan in a later layout run before any concept sign-off. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|

None: this is the first review record of hda-1 (`reviews/` held only README.md).

## Drawing
No P&ID in this scope (`pid/` holds only README.md; P&IDs were out of scope). `cheme validate`
prints no `drawing <sheet>:` line, because the drawing rules apply to P&IDs, not to the generated
BFD/PFD. The PFD was rendered (`build/PFD.png`) and read as a whole: all 15 steps, 24 material
and 10 energy streams are present and correctly connected; the energy streams cross the material
lines in many places (generated layout, readable); the symbol issue is R-07. The BFD was not
rendered.

## Checked and fine
- Scope: route (thermal HDA with quench, flash, H2 recycle with purge, stabiliser, benzene and
  toluene columns, toluene recycle, biphenyl by-product) and boundary match the case notes of
  issue #42. `git diff --name-only origin/main..HEAD` changes nothing outside `processes/hda-1/`.
- `cheme validate`: 17 files, 0 errors, 0 warnings (infos: `dexpi.load` reference cycles, a D-023
  in a commented template example of checks.yaml).
- `cheme process streams`: blocks RXN and SEP and all 15 steps balance (largest residual
  0.1 kg/h); extents HDA 167.865, BIPH 2.569 kmol/h. `cheme process propagate --check`: exit 0,
  nothing reported.
- `cheme run scripts/hda_balance.py` re-run: reproduces every duty in the flowsheet (K101 229.7,
  P101 36.5, H101 2956.5, E101 24451, E102 4926 kW, column duties as listed), loop residual
  3.5e-10, purge fraction 0.1114, H2/aromatics 5.000, reactor outlet 936.8 K, FEHE minimum
  approach 53.1 K.
- Plausibility (reviewer's own hand checks): toluene 1.241 kg/kg benzene against the
  stoichiometric 1.180 (+5 %: biphenyl and aromatics in fuel gas), typical for HDA; selectivity
  0.9694 at X = 0.75 recomputed; biphenyl 2.57 kmol/h = half the benzene lost; recycle
  compressor power recomputed at ~235 kW (ratio 1.108, k ~1.35, efficiency 0.75) and its outlet
  ~324 K; P-101 power ~36 kW recomputed; adiabatic rise 42 K consistent with 1.95 MW; fuel-gas
  mass (CH4 formed and fed, H2 lost, 258 kg/h aromatics) and its LHV ~54 MJ/kg recomputed; H2
  utilisation ~56-58 % plausible without H2 recovery; benzene column reflux 1.28 against an
  Underwood minimum of ~0.95 at alpha ~2.4; steam levels give positive approaches (MP 471 K vs
  448 K, HP 526 K vs 479 K); the vacuum on C-203 is justified by the biphenyl bottoms
  temperature.
- Heats of reaction (-41.8 and +15.0 MJ/kmol) agree with standard gas-phase formation
  enthalpies.
- `cheme maturity`: level none; process.yaml claims `concept` (warning
  `cheme.maturity-claim-exceeds`). The schema has no lower level, and process.yaml's comment and
  `validation.notes` say plainly that the evidence reaches no level and why (methanol-1
  precedent): honest. `validation.status: unreviewed` is correct.
- Every key design value is either calculated or marked ASSUMED with a D-number (design basis,
  flowsheet `provenance`, equipment and line notes); the D-005 open point on biphenyl slightly
  beyond equilibrium (ln(Q/K) = +0.14) is disclosed.
- LCI: per 1 kg benzene (functional unit), every exchange is traceable to a flowsheet stream;
  mass in 1.30672 = out 1.30672 kg (rechecked: 15518.3 + 815.7 = 12500 + 401.0 + 3260.5 + 172.5
  kg/h, less 0.02 kg/h); `--coverage` mass, element and carbon-origin closed; all 10 backgrounds
  are `missing:` with a description of the activity to link; no numbers from licensed databases
  (`factors.yaml` holds only the packaged open profile, no factor is used); allocation shares
  71.5 % (energy) and 76.5 % (mass) recomputed. Excluding H-101's combustion emissions is
  consistent with a per-MJ heat background.
- Licences: no third-party table, figure or passage found in DESIGN.md, process.yaml, the YAML
  files or the script; the route sketch is the author's own; IDAES flowsheet values are not used
  (feeds, scale and specs differ); Douglas and Speight are cited for facts only.
- `cheme check`: concept gates design-basis, concept-lists, process-concept, process-balances,
  process-links-concept and assumptions-marked ok; layout-plot-plan fails (R-12); design-review
  fails until this record is committed.

## Not checked
- The BFD rendering, and the generated PFD XML beyond its rendering.
- The Peng-Robinson flash and column results themselves (no qualified package in core): only
  their internal consistency and plausibility were checked; stage numbers, column diameters and
  reactor volume are not calculated by the design, so they were not reviewed.
- Douglas (1988) and Speight (2011) at their locators (R-04): the reviewer did not read them.
- Equipment and line list design pressures, temperatures and DN beyond a spot check (they are
  ASSUMED first-pass values); materials for hot hydrogen service (I-09).
- `runs/20261027-212954-design/session.jsonl.gz` was not opened; whether a full agent session log
  may be published under the library licences is for the maintainers (methanol-1 commits one too).
