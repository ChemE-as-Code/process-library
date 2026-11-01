---
topic: design
reviewed_commit: 89e6c44a1c4a4161ce4a147e4a92f4633fc2de99
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/BFD.xml, process/PFD.xml, scripts/balance.py, lca/, equipment/equipment-list.yaml, runs/20261028-150743-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/acetic-acid-1
merge: pending
---
# Review: design (concept PFD and preliminary LCI of acetic-acid-1, issue #128)

Independent review of the branch `case/acetic-acid-1` (5 commits on `origin/main`, 6bf7b84 ..
89e6c44): design basis, materials, reactions, balanced BFD/PFD, equipment list, preliminary
gate-to-gate LCI, DESIGN.md and the run record. No design file was changed by this review.
The brief's ids R-01 ... R-10 are the ids `2026-10-28-pfd-lci-review#1` ... `#10` below, in
the same order (the repository's id rule, `cheme.review-finding-id`).

Commands re-run by the reviewer at 89e6c44:

- `cheme validate`: 16 files, 0 errors, 0 warnings (infos only: `dexpi.load` reference cycles,
  `cheme.decision-unknown D-023` from the template comment in checks/checks.yaml:76).
- `cheme check`: concept gates ok except `layout-plot-plan` (#8); basic and detail gates fail
  (no P&IDs, layout, datasheets, design review): outside this run's scope.
- `cheme maturity`: calculation maturity none; `cheme.maturity-claim-exceeds` warning on
  process.yaml:33 (#7); review status unreviewed.
- `cheme process streams`: every block (RXN, SCR, PUR) and step closes; reactor extents CARB
  999.7, WGS 8.0, MEOH_CH4 9.0, PROP 0.405 kmol/h.
- `cheme process propagate --check`: exit 0, nothing reported.
- `cheme assess lca --coverage`: partial screening carbon footprint, 8 gaps, mass, element and
  carbon-origin balance closed, publishable.
- Reviewer scratch check `build/review_flash.py` (run with `cheme run`, using only the constants
  and streams of `scripts/balance.py`): V-102 enthalpy in 38.5 MW, out 49.7 MW, so the
  specified split needs 11.2 MW of heat (latent of S10 22.8 MW); mixer M101 outlet from its
  enthalpy balance 378.7 K.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | DESIGN.md D-008; scripts/balance.py:196-204; process/flowsheet.yaml:507 (Q03) | V-102, R-101, Q03, feed:MPS | (R-01) V-102 is an "adiabatic flash" (flowsheet.yaml:181, D-008), but its specified split does not close adiabatically. With balance.py's own heat capacities and latent heats, cooling 411 t/h of reactor liquid from 463 to 413 K cannot evaporate the specified 162 t/h of S10: 11.2 MW is missing. balance.py lumps the reactor and the flash into one duty (`R101_cooling`), so the shortfall is hidden: Q03 = 6.6 MW is really about 17.8 MW of reactor cooling minus 11.2 MW of heat the flash never receives. The global check in D-008 ("steam plus power = heat rejected minus reaction heat") holds whatever the split, so it cannot catch this. Consequences: D-008's statement that the flash vapour carries 32.7 of the 37.7 MW of reaction heat is wrong. The light-ends duties and the LCI steam (0.452 kWh/kg) rest on 11.2 MW (about 0.19 kWh/kg, about 40 % of the steam) that no utility supplies. One of two things must change: a heat source (flash heater or reactor-cooler integration) or less flash vapour, which puts more duty on the C-201 reboiler. Either way the steam and cooling-water figures in the LCI shift. | high | open | Compute the reactor and the flash separately in balance.py. Either (a) choose the flash split so that V-102 is adiabatic and close C-201 on its reboiler, or (b) declare a flash heater or reactor heat recovery with its own duty and utility. Report Q03 as reactor cooling only, correct D-008 and the Results table, then regenerate lca/ (`cheme assess lca --write`). |
| 2026-10-28-pfd-lci-review#2 | process.yaml:52-59 | chemistry.inputs | (R-02) The Atlas manifest lists hydrogen, nitrogen and methane, the minor components of the CO gas (0.3, 1.0 and 0.2 mol%), as the process's only `feedstock` inputs. Methanol and carbon monoxide, the actual feedstocks, are missing because the chemicals registry has no entry for them. A catalogue reader sees acetic acid made from H2, N2 and CH4. The notes explain it, but a listing shows the chemical, not the note. | medium | open | Remove the minor-component feedstock rows, or make them clearly secondary. Raise the registry entries (methanol, carbon-monoxide, acetic-acid, methyl-iodide, propionic-acid; DESIGN.md "Library items to add later") as a separate library PR and list the real feedstocks once they exist. |
| 2026-10-28-pfd-lci-review#3 | DESIGN.md D-003, D-004, source register S2 | S2 (Jones 2000) | (R-03) S2 is registered as not read (publisher 403; one statement seen in a search-engine excerpt). It is still cited as a reason in D-003 ("low water reduces the drying load and the water-gas shift (S2 per route description)") and as the order-of-magnitude basis of the 500 ppm(wt) propionic acid make in D-004. An unread source must not carry a decision. The propionic value is marked ASSUMED, but the D-003 reason reads as sourced. | low | open | Read S2 (it is an open-access Platinum Metals Review article) and give a page locator, or drop it from the D-003 reason and base the low-water argument on S1's examples (the CO2 make it reports). Keep D-004 ASSUMED with S1's 290-390 ppm as the reported fact. |
| 2026-10-28-pfd-lci-review#4 | process/flowsheet.yaml (S06) | S06, M101 | (R-04) The reactor feed S06 is given 403.15 K (assumed). The enthalpy balance of mixer M101's inlet streams, with balance.py's constants, gives 378.7 K. Duties are not affected, because balance.py takes the inlet streams at their own temperatures, but the stream table shows a temperature the design does not support. | low | open | Set S06's temperature from the mixer balance (about 379 K, provenance assumed with balance.py as the source), or remove the value. |
| 2026-10-28-pfd-lci-review#5 | process/flowsheet.yaml (S17, S18); DESIGN.md D-006 | V-201 decanter | (R-05) S18 is titled "Decanter light (aqueous) phase", but the specified composition is about 70 wt% methyl acetate and 22 wt% water. The heavy phase S17 is about 54 wt% CH3I and 44 wt% methyl acetate. Nothing checks that this liquid-liquid split exists: at these methyl acetate contents the decanter may be close to a single phase. The balance and LCI are unaffected, because both phases return to the reactor. Column and decanter sizing is affected. | low | open | State in D-006 that the decanter split is not checked against liquid-liquid equilibrium. Re-check it with an LLE model once one is qualified (O-7), or rename S18 by its composition. |
| 2026-10-28-pfd-lci-review#6 | DESIGN.md "Results (design case)" | LCI classification | (R-06) DESIGN.md says "Classification: partial (9 gaps ...)". `cheme assess lca --coverage` and lca/gaps.csv report 8 gaps (gaps.csv has 9 lines including its header). | low | open | Correct the count to 8. |
| 2026-10-28-pfd-lci-review#7 | process.yaml:33 | maturity | (R-07) `maturity: concept` gives `cheme.maturity-claim-exceeds`: the evidence supports no design maturity. concept is the lowest value the schema allows, and the comment and `validation.notes` disclose calculation maturity none, so the claim is honest about its limits. The warning remains until the reactor and separators rest on sourced specified values (`cheme.maturity-sourced-boundary`, `-balanced-model-basis`). | low | open | Keep the disclosure. Either give the CO gas and capacity a source and give the split values sources to reach `sourced`, or have a human accept the warning with this reason. |
| 2026-10-28-pfd-lci-review#8 | checks/checks.yaml (layout-plot-plan) | concept gates | (R-08) The concept-stage gate `layout-plot-plan` fails: there is no layout/site-plan.yaml or equipment-placement.yaml. This bounded run (design basis to PFD to LCI) did not aim at a plot plan, but the concept stage cannot be signed off while the gate fails. The basic and detail gates (pids-exist, layout-3d, lifting-study, mto, datasheets, design-review, ...) also fail; they are outside this run. | low | open | Either add the plot plan in the next run, or record in DESIGN.md/PROGRESS.md that the concept gate is open on purpose for this library case. Do not sign off the concept stage until then. |
| 2026-10-28-pfd-lci-review#9 | lca/lca.yaml:20; DESIGN.md D-013 | boundary | (R-09) lca.yaml has `boundary: cradle-to-gate`, and results.md prints it. DESIGN.md (D-013, Route and boundary memo), the commit message and lca/dataset.yaml call the LCI gate-to-gate. Both readings can be defended: the foreground is gate-to-gate and the study becomes cradle-to-gate once backgrounds are linked. The files should say one thing. | low | open | Add one sentence to D-013: the foreground inventory is gate-to-gate, and lca.yaml declares cradle-to-gate because every feed is to be linked to its background. |
| 2026-10-28-pfd-lci-review#10 | lca/results.md (Uncertainty), lca/results.csv | climate-change total | (R-10) Every contribution is a gap and the main table correctly shows "no total". The generated uncertainty table still prints deterministic 0, interval 0 .. 0, and results.csv has impact 0 for the total. Out of context this reads as a zero footprint. This is generated output (not editable here) and a core presentation issue, not a design error. | low | open | Report it to cheme-as-code (suppress the Monte Carlo row and the total when every contribution is a gap). Until then, say in lca/README.md that the 0 means "no total". |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|

None: this is the first review record of acetic-acid-1 (`reviews/` held only README.md at
89e6c44).

## Drawing

No P&ID exists. `cheme validate` printed no `drawing <sheet>:` count line: the BFD and PFD are
generated sheets, and the drawing rules apply to P&IDs. I rendered `build/PFD.png`
(`cheme render process/PFD.xml --png`) and read it at overview scale only. Steps, the SCR, RXN
and PUR blocks, terminals and stream numbers are present. The long recycle lines S12 to S19 run
under the sheet, so the sheet is wide but readable. Tiles were not read (see Not checked).

## Checked and fine

- **Scope and boundary** match issue #128: liquid-phase methanol carbonylation, low-water Ir/Ru
  (Cativa type), gate-to-gate from the methanol and CO battery limits to glacial acid. The
  methanol feed is linked to methanol-1 S18. CO production, storage, flare and utilities are
  outside the boundary (D-001).
- **Nothing outside `processes/acetic-acid-1/` changed** (`git diff --name-only origin/main..HEAD`).
- **Mass, component and element balances** close for every block and step (`cheme process
  streams`). I recomputed by hand from the stream table:
  - CO: 1033.4 kmol/h fed, 1008.1 consumed (CARB + WGS + PROP), 25.3 in S23. This matches
    S23 (56.4 kmol/h, 44.9 mol% CO).
  - N2 (10.5), CH4 (2.1 + 9.0 = 11.1) and H2 (3.15 + 8.0 - 9.0 - 0.81 = 1.34 kmol/h) match S23.
  - Water: 0.9 kmol/h with the methanol plus 1.4 net from the reactions gives 41.4 kg/h,
    which is the product's 691 ppm(wt) of 60 t/h.
  - Propionic acid: 30 kg/h formed, which is 500 ppm(wt); 3 kg/h (50 ppm) stays in the product
    and 27 kg/h leaves in S22 (33 wt%).
  - Product: 99.92 wt% acid, inside the limits of D-002.
- **Plausibility** against general knowledge of the technology: yield 99.1 % on methanol and
  96.7 % on CO (the low-water Ir process is reported above 99 % and in the mid-90s % on CO).
  CO2 and CH4 make are each about 1 % of carbonylation. Reactor 463 K and 29 bar(a). Steam
  1.63 MJ/kg (about 0.8 t MP steam per t) is in the low range for this route, but see #1. The
  C-202 duty (about 14 MW) and the C-203 duty (about 13 MW) agree with my own estimates from
  their reflux ratios and latent heats. Power (7.9 kWh/t) is flagged as an underestimate (D-010).
- **Heat of reaction** checked from formation enthalpies: -484.3 + 239.2 + 110.5 = -134.6 kJ/mol.
- **Sources and ASSUMED marking**: key values are sourced to US 6,140,535 with a locator
  (Examples 1-5, operating ranges) or marked ASSUMED in design-basis.yaml, the flowsheet
  provenance and DESIGN.md. The source register gives the read status and reuse terms honestly.
  I found no copied tables, figures or passages: the patent's ranges are given as numbers in
  the design's own words.
- **LCI**:
  - The inventory is per 1 kg HAC, with every exchange tied to its stream or duty ids.
  - Mass in 61,621.9 kg/h against 61,621.8 out; elements close (`--coverage`: closed).
  - No zero-filled and no licensed background values: factors.yaml has `factors: []`, and the
    only included profile is the open desnz-ghg-2026.
  - All 8 unmapped backgrounds are in gaps.csv, each with a description of the activity to link.
  - lca/mappings.yaml holds the only per-process override (`feed:MPS` -> `steam-heat`), with a
    reason.
  - Catalyst losses are left out explicitly (O-6), not set to zero. The methyl iodide make-up
    is honestly limited to the off-gas slip.
- **The run report** (`runs/20261028-150743-design/report.md`) matches what I re-ran (0 errors,
  0 warnings, maturity none, unreviewed, merge pending). Its energy "rough check" is the global
  check that cannot see #1.

## Not checked

- I did not re-read the full text of US 6,140,535 to verify each quoted range (CO2 0.63-0.98 %,
  CH4 0.81-1.02 %, H2 0.06-0.86 vol%, 17.3-20.3 mol/(l h)). I took them as stated in the
  register.
- No property package covers the system, so the column, flash, decanter and scrubber splits
  (D-006) were checked only for plausibility, not rigorously (see #1 and #5). Rigorous design
  needs core's property-package qualification.
- PFD and BFD: I did not do a tile sweep or a label-level reading, and did not render the BFD.
- I did not review the equipment list beyond `cheme validate` and `cheme check`
  (process-links ok). There are no P&IDs, layout, datasheets, control files or HAZOP yet.
- I did not check the library catalogue and LCI build (`build_lci.py`) output for this
  process.
