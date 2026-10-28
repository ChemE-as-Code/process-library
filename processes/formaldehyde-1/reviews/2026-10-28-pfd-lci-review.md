---
topic: design
reviewed_commit: bfcbb6aa342687cdb5d77de59516d31a4d749f1e
scope: [DESIGN.md, PROGRESS.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/materials.yaml, process/reactions.yaml, process/catalysts.yaml, process/BFD.xml, process/PFD.xml, scripts/formox_balance.py, equipment/equipment-list.yaml, piping/line-list.yaml, lca/]
reviewer: review-agent
reviewer_kind: agent
branch: case/formaldehyde-1
merge: pending
---
# Review: formaldehyde-1 design basis, balanced BFD/PFD and preliminary gate-to-gate LCI (issue #169)

An independent review of the five commits on `case/formaldehyde-1` (`b3c29a2..bfcbb6a`) against
`origin/main`. I re-ran every command myself rather than relying on the run report. The
reviewer did not write the design and changed no design file.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | lca/lca.yaml | allocation of product:STEAM | DESIGN.md D-010 says the allocation of the exported MP steam is "left open". But `lca/lca.yaml` has no `allocation:` block (`lca/dataset.yaml:638` `allocation: {}`), so the generated `lca/results.md` reports `allocation: mass (FORMALIN 100.0%)`. That is a 100/0 split, chosen implicitly and labelled "mass" only because the steam is counted in kWh. The library rule (`docs/system-model.md`, "Exported steam, heat and fuels are co-products ... allocated by energy or exergy (documented per process)") is neither followed nor deviated from on the record. nitric-acid-1 documents the same situation explicitly (`allocation: method: shares`, D-014). The choice matters: by energy the steam (2.02 MJ/kg formalin) against the formalin's heating value (about 8.7 MJ/kg for 0.5 kg HCHO, reviewer's estimate) would take roughly 19 % of the burdens. | medium | open | Record the decision in `lca/lca.yaml` (`allocation:` with method, shares and reason, e.g. shares 1/0 as conservative for the formalin, or energy/exergy) and in D-010, then rerun `cheme assess lca --write`. |
| 2026-10-28-pfd-lci-review#2 | lca/results.md, lca/results.csv | climate total | The generated result files headline 0.0511593 kg CO2-eq per kg formalin as a "partial screening carbon footprint". That figure is only the direct fossil CO2 at the stack: methanol, power, water, the cooling-water heat and the steam are gaps. DESIGN.md D-010 and the run report disclaim it, but `results.md` itself carries no such sentence, and a reader of the Atlas output could take it as the product footprint (cradle-to-gate values for formalin are about an order of magnitude higher). The files are labelled "with gaps", and asu-1 follows the same convention, so this is not high. | low | open | In the `goal:` of `lca/lca.yaml` (which `results.md` and `dataset.yaml` carry), state that the climate total is the direct stack CO2 only and not a footprint, or do not write the result files until the methanol background is linked. |
| 2026-10-28-pfd-lci-review#3 | process.yaml | maturity / validation.notes | `cheme maturity` gives calculation maturity **none** and warns `cheme.maturity-claim-exceeds` (process.yaml:30). `concept` is the lowest value the schema enum allows, so the claim itself cannot be lowered. But `validation.notes` does not say that the calculation maturity is none, nor why: feed flows are assumed, R101 selectivities and R301 conversions are assumed, and the C201 outlets are specified values from the script. | low | open | Add one sentence to `validation.notes`: calculation maturity none (`cheme maturity`), with the failing requirements named. |
| 2026-10-28-pfd-lci-review#4 | process/flowsheet.yaml | header comment lines 7 and 13 | Line 7 calls R101's per-pass conversion and selectivities "sourced", but they are `provenance: assumed` (line 152), derived by the script from BREF targets plus an ASSUMED DME make. Line 13 cites core #364 for aqueous formaldehyde, which contradicts D-009 ("core #364 ... does not apply, formalin is not an electrolyte"). | low | open | Line 7: "derived from sourced plant targets (assumed)"; line 13: drop #364. |
| 2026-10-28-pfd-lci-review#5 | PROGRESS.md | lines 7-8 | The flowsheet entry says "10 steps"; the flowsheet has 9 (M101, K101, M102, E101C, E101H, R101, C201, SPL, R301), as the run report says. Commit b0faf4c (the D-006 note on the heat of solution) has no PROGRESS.md line (AGENTS.md: append every change). | low | open | Correct the count and add the missing line. |
| 2026-10-28-pfd-lci-review#6 | DESIGN.md | D-010 "LCI result" table | DESIGN.md repeats the full inventory (amounts to 6 significant figures). AGENTS.md says DESIGN.md "keeps the decisions, not a second copy of the numbers", and this copy goes stale as soon as `cheme assess lca --write` reruns. D-010 also says the outputs were written by `--inventory --write` to inventory/dataset/gaps, but `results.*` and `uncertainty.csv` (from the full `--write`) are committed too. | low | open | Keep the per-t-HCHO plausibility check and point to `lca/inventory.csv` for the amounts; list all written files. |
| 2026-10-28-pfd-lci-review#7 | process/catalysts.yaml | FEMO window | The window carries `provenance: given`, but its own source string says the pressure upper bound (200 kPa(a)) is ASSUMED, which mixes a sourced and an assumed value under one provenance. | low | open | Split the pressure bound out, or mark the window assumed with the BREF temperature range cited. |
| 2026-10-28-pfd-lci-review#8 | lca/lca.yaml | consumables.femo-catalyst.metals | Fe 0.10 by mass is low for "Fe2(MoO4)3 with excess MoO3". The stoichiometric salt is about 19 wt% Fe and 49 wt% Mo; at a typical Mo/Fe atomic ratio of about 2.5 it is about 13 wt% Fe and 55 wt% Mo (reviewer's arithmetic from the formula). The value is marked ASSUMED and "to be confirmed", and it only matters for the metal-depletion side. | low | open | Use fractions from the stated formula and Mo/Fe ratio, or cite a source. |

No critical or high finding.

## Previous findings
None: this is the first review record of formaldehyde-1 (`reviews/` at bfcbb6a held only
README.md).

## Drawing
The BFD and PFD are generated by `cheme process build` from `process/flowsheet.yaml`. `cheme
validate` reports 0 errors and no drawing finding for either sheet. I read the PFD whole
(`build/PFD.png`): 4 blocks, 9 steps and all streams and energy streams labelled, including the
recycle S11 and Q1-Q6, with no tiles. There are no P&IDs (out of scope); `pid/` holds only its
README, and the template's reference sheet was removed.

## Re-run results (at bfcbb6a, by the reviewer)
- `cheme validate`: 17 files, **0 errors, 1 warning**: `cheme.process-catalyst` R101/S6 at 399 K
  below the FEMO window. The reason is accepted in D-005: the feed reaches reaction temperature
  on the hot oil in the inert inlet section of the tubes, which is standard metal-oxide
  practice. The infos are the two template comments citing D-012/D-023 and the FEMO poison
  names, which are not components.
- `cheme check`: every concept and basic process gate passes (design-basis, concept-lists,
  process-concept, process-balances, process-basic, process-links, assumptions-marked,
  pids-valid, drawing-clean). Failing: pids-exist, design-review (this record addresses it),
  the layout family (layout-plot-plan, layout-3d, lifting-study, mto, layout-review,
  layout-detail, electrical, hvac) and datasheets. All the failing gates are out of the run's
  scope.
- `cheme maturity`: calculation maturity **none**; design maturity claimed concept, warning
  `maturity-claim-exceeds` (finding #3).
- `cheme process streams`: all 4 blocks and 9 steps close. Boundary mass is 34 991.1 + 11 474.6 + 3711 =
  50 176.7 kg/h in = 20 000 + 30 176.7 out.
- `cheme process propagate --check`: exit 0, nothing to change.
- `cheme assess lca --coverage`: partial screening, 14 gaps (9 exchanges without a background,
  5 emissions outside the climate method), mass balance closed, energy closure 75.9 %
  (utilities only, as D-010 says), publishable. `cheme assess lca --check`: all written files
  current. `cheme impact`: nothing to review.

## Checked and fine
- **Scope and route**: these match issue #169's case notes. Fe-Mo partial oxidation with excess
  air and off-gas recycle, absorption to 50 wt% (inside the 37-55 wt% range), catalytic ECS,
  methanol as a boundary feed with the methanol-1 link noted. Silver-route data are not mixed
  in. Nothing outside `processes/formaldehyde-1/` changed (`git diff --name-only
  origin/main..HEAD`: 192 files, all inside the folder).
- **Hand checks of the balance**, all reproduced by the reviewer:
  - Methanol 11 474.6 kg/h = 358.1 kmol/h. HCHO in the product is 333.0 kmol/h, so the yield is
    93.0 % and the use is 1147 kg/t HCHO. Formalin S14 recomputes to 50.0 wt% HCHO and
    0.28 wt% methanol.
  - O2: fresh air carries 251.5 kmol/h O2, the reactor consumes 187 kmol/h, and the vent
    leaves 64.5 kmol/h, which is 6.0 % of about 1070 kmol/h vent. Vent volume is about
    2400 Nm3/t HCHO.
  - Reactor inlet is 8.5 % methanol and 9.7 % O2: below the 10.9 % O2 limit cited from EPA91
    and with an O2/MeOH ratio of 1.14, above stoichiometric.
  - Blower: isentropic power from 100.5 to 150 kPa(a) at 301.6 K, divided by 0.75 and 0.95,
    gives about 1.58 MW against 1.61 MW in the flowsheet. Total power 169 kWh/t.
  - R101 duty 10.14 MW is about equal to the reaction heat at 298 K (FORMOX about 14.7 MW plus
    HCHO to CO about 1.4 MW) less the sensible heating of the gas from 399 to 553 K (about
    6 MW).
  - R301 duty 1.08 MW is consistent with the combustion of 20.3 kmol/h CO plus the organics
    less the heating of the vent from 303 to 423 K.
  - Absorber cooling 13.1 MW is consistent with gas sensible heat (about 3.5 MW), water
    condensation (about 4.2 MW) and heat of solution (about 5.7 MW).
  - Carbon: 4301 kg C/h in = 4021 kg C/h in the product + 280 kg C/h at the stack.
- **Plausibility for the technology**: yield 93 % and conversion above 99 % sit in the metal-oxide
  ranges. Electricity 169 kWh/t, steam export about 1.7 t/t (4.04 GJ/t, below the upper bound
  set by the reaction heat) and stack HCHO, TVOC and CO concentrations are all reasonable.
  ΔH(FORMOX) from formation data is -150 kJ/mol against the cited -159 kJ/mol; the difference
  is noted.
- **Provenance**: every key value is either given with a source and locator (BREF LVOC 2017
  section and table, EPA-450/4-91-012 page, NIST) or marked ASSUMED, in the design basis,
  `flowsheet.yaml`, `reactions.yaml`, the `lca.yaml` source strings and the balance script's
  INPUTS. Script values entered as `assumed` cite the script. The open inputs (heat of solution,
  yield split, energy closure gated on core #315) are stated.
- **Licences**: no third-party table, figure or passage was found. DESIGN.md restates single
  facts with locators, and the Ullmann chapter is marked as a lead with no value taken.
  `lca/factors.yaml` holds only the packaged open profile, and no licensed background value
  appears.
- **LCI**:
  - The functional unit is 1 kg formalin. Every exchange equals its flowsheet stream divided
    by 20 000 kg/h. Consumables are BREF rate × 80 000 t/a / 160 000 t/a formalin = 3e-5 kg/kg.
    NOx is 10 mg/Nm3 × 23 946 Nm3/h = 1.197e-5 kg/kg.
  - No exchange is zero-filled: every unmapped background is `missing:` with a description of
    the activity to link, and is listed in `gaps.csv`.
  - The recyclable catalyst disposals are free under cut-off, which is consistent with the
    system model.
  - The one per-process override is in `lca/mappings.yaml` (steam-heat), not in the shared
    file.
  - Fugitives, storage and wastewater are excluded, each with a reason and a source.
- **process.yaml**: `publication.status: internal`, `validation.status: unreviewed`, maturity
  concept (the lowest enum value), and the notes say honestly what core does and does not
  check (apart from finding #3).
- **Lists**: the equipment list (10 items) and the line list match the PFD links
  (process-links gate passes).

## Not checked
- The BREF LVOC 2017 and EPA91 locators and values were not re-read against the PDFs in this
  review; they were checked for internal consistency and plausibility only. The BREF's own
  pairing of a 91-94 % yield with 1135-1151 kg/t is not exactly consistent: 91 % would be
  about 1172 kg/t. The design's 93 % / 1147 kg/t sits inside both ranges.
- `scripts/formox_balance.py` was read (inputs and enthalpy functions), not re-run. Its outputs
  were checked by the hand balances above.
- The heat of solution of formaldehyde (62 kJ/mol, ASSUMED, the largest term of the cooling duty):
  still to be sourced, an open input of D-006.
- The library LCI build (`scripts/build_lci.py --strict`) was not re-run.
- Flammability margin of the reactor feed (9.7 % O2 against the limiting oxygen concentration of
  methanol): the cited 10.9 % limit is taken at face value. This belongs to the HAZOP at
  basic engineering.
- Line sizes and design pressures in the lists (ASSUMED concept values, D-011).
