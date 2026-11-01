---
topic: design
reviewed_commit: 0e26ab3d59169b943f087c3eb2908d43d057334a
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/simulation.yaml, equipment/equipment-list.yaml, lca/, scripts/glycerol_balance.py, runs/20261028-150843-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/glycerol-1
merge: pending
---
# Review: design (concept BFD/PFD and preliminary gate-to-gate LCI, glycerol-1, issue #186)

This is an independent review of branch `case/glycerol-1` at `0e26ab3`, which has 4 commits over `origin/main`.
I re-ran every check myself on that commit instead of relying on the run report.

- `cheme validate`: 17 files, 0 errors, 0 warnings. It compared 2 sheets (BFD, PFD) and 12 lists, with no P&ID cross-checks.
- `cheme check`: the concept gates pass except `layout-plot-plan`. The basic gates `pids-exist` and `design-review` fail, along with the layout, MTO, datasheet and detail gates. These are out of scope at this stage.
- `cheme maturity`: calculation maturity is none. It warns `cheme.maturity-claim-exceeds` on `process.yaml:34`.
- `cheme process streams`: every block and step balance closes, with extents NEUT1 1.160 and NEUT2 0.116 kmol/h.
- `cheme process propagate --check`: no output (nothing stale).
- `cheme assess lca --coverage`: partial screening carbon footprint with 13 gaps, all declared `missing:` with a description. Mass, element and carbon-origin balances close.
- `cheme assess lca --check`: the written outputs are current.
- `git diff --name-only origin/main..HEAD` shows no file outside `processes/glycerol-1/` changed.
- `cheme diff main --list`: 174 added or changed process-model items (BFD and PFD objects, all `added`), no P&ID items.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | process/design-basis.yaml:16-17 | crude glycerol feed | The design basis gives a crude-glycerol composition that the design does not use: glycerol 63.57, methanol 25.0, water 2.0, sodium oleate soap 5.0, FAME 3.0, NaOH 1.43 wt%, with "soap/FAME split and water ASSUMED". The flowsheet S1 and D-004 use glycerol 59.841, methanol 29.332, NaOCH3 2.847, fatty matter 7.98 wt%, and no water ("No water", D-004). A reader who takes the feed from the design basis gets a different feed, with water and NaOH instead of methoxide. | high | open | Replace `composition_wt_percent` and `source_of_values` with the D-004 composition (or point to S1). Keep the water-content question as the open item D-004 already names. |
| 2026-10-28-pfd-lci-review#2 | process/flowsheet.yaml:395-405 (S15), equipment/equipment-list.yaml:29 (E-403), D-009/D-012 | still vacuum system | The vacuum system as specified cannot work, and its utility is missing from the balance and the LCI. E-403 is supposed to condense the stripping steam and evaporated water (about 204 kg/h of water vapour) at the still's 1.5 kPa(a), on cooling water at 298/308 K, giving condensate at 313 K. Water saturates at about 286 K at 1.5 kPa, so cooling water cannot condense it. At that pressure and about 448 K the vapour is roughly 28 000 m3/h (ideal gas), far beyond what the 20 kWh/t "vacuum pumps" (W4) can handle. Glycerol stills normally use steam-jet boosters ahead of the condenser (motive steam is often of the order of the vapour load) or chilled water or refrigeration. That motive steam or refrigeration is a utility of probably the same order as the live steam (0.06-0.3 kg/kg product, ASSUMED order of magnitude), and it is missing from Q7, W4, the energy cross-check in D-012 (885 kWh/t) and `lca/` (no flow). | high | open | Add the vacuum arrangement to D-009/D-012: ejector stages with a motive-steam ratio (sourced or ASSUMED) and their condensers, or a chilled-water condenser with its refrigeration power. Add the motive steam to the balance (S15 and WW grow, and a feed of steam), the duties and the LCI as a flow with its `missing:` background. Correct the S15 conditions. |
| 2026-10-28-pfd-lci-review#3 | process/flowsheet.yaml:359 (S9), :381 (S11), D-007, D-008 | C-201 bottoms, E-301 | The stream temperatures do not fit the boiling behaviour of glycerol-water. S9 is 383 K at 120 kPa(a) with about 7 wt% water on a salt-free basis (about 93 wt% glycerol). Aqueous glycerol of that strength boils near 418-425 K at 1 atm, about 10-14 K above the 410.8 K a 10 K approach leaves to LP steam at 420.8 K. The bottoms would then either hold more water, shifting the load to E-301, or need a higher steam level. Conversely, E-301 at 10 kPa(a) and 403 K would dry the glycerol far below the specified 5 wt% water: the bubble point of 5 wt% water at 10 kPa is roughly 355 K (Raoult estimate, ASSUMED). This shifts water and duty between C-201, E-301 and C-401, but the overall heat demand changes little. | medium | open | Set S9 and S11 temperatures from sourced glycerol-water boiling-point data (or a qualified VLE once core's property-package qualification lands). Check that LP steam at 450 kPa(a) can serve E-201; otherwise raise the level or move E-201 to HP steam. Make the E-301 pressure, temperature and water content consistent. |
| 2026-10-28-pfd-lci-review#4 | equipment/equipment-list.yaml:10-35 | R-101 ... S-402 | The equipment-list notes come from an earlier balance and contradict the flowsheet. Examples: R-101 "2072 kg/h crude + 136 kg/h HCl" (S1 2201.83, S2 145.43); V-102 163 kg/h (S4 181.31); R-102 8.7 kg/h (S6 9.28); C-201 2053 kg/h feed, 510 kg/h methanol (S7 2175.23, S8 673.96); E-201 385 kW (Q1 488.9); E-202 313 kW (Q2 413.6); E-301 1543 kg/h, 73 kW (S9 1501.28, Q3 40.7); E-302 51 kW (Q4 20.1); C-401 1462 kg/h feed (S11 1467.72); S-402 133/78 kg/h (S16 139.02, S12 83.92). The header claims the notes are "from scripts/glycerol_balance.py". | medium | open | Update the notes from the current streams and duties, or refer to stream and duty ids (S7, Q1, ...) instead of repeating numbers (AGENTS.md: the numbers live in the YAML). |
| 2026-10-28-pfd-lci-review#5 | lca/lca.yaml:24-41, DESIGN.md D-013 | allocation | Mass allocation gives the recovered methanol (S8, 674 kg/h) 32 % of everything, including 32 % of the crude-glycerol burden. That methanol is the biodiesel plant's own excess reactant, which arrives in the crude and leaves unchanged; under mass allocation a pass-through is treated like a product. The crude-glycerol background asked for ("with that plant's own allocation, per kg as delivered") already counts that methanol mass, so the per-kg-glycerol result will depend strongly on this choice. The deviation is declared, and no numbers are published yet (all gaps), so this is not high. | medium | open | Before any background is linked, treat the returned methanol (and preferably the fatty layer) as a return to the biodiesel plant, not a co-product: net it off the crude feed, or use system expansion. At least, report the unallocated, economic and substitution variants side by side in D-013. |
| 2026-10-28-pfd-lci-review#6 | process/simulation.yaml:8, process/reactions.yaml (NEUT1), S3 | R-101 heat | The comment says the neutralisation heat in R-101 is "about 65 kW". With 1.160 kmol/h × 55.8 kJ/mol it is 65 MJ/h, about 18 kW. R-102's 1.8 kW is right. NEUT1 also has no `heat_of_reaction`, so nothing calculates the "about 5 K rise" given for S3. 18 kW on 2347 kg/h at an ASSUMED cp of about 2.5 kJ/(kg K) gives about 10 K. | low | open | Correct the comment. Give NEUT1 a heat of reaction (ASSUMED, methoxide plus HCl), and derive S3 from it or mark it as an ASSUMED estimate. |
| 2026-10-28-pfd-lci-review#7 | DESIGN.md:68-72 (D-004), flowsheet.yaml:273 | S1 source | The D-004 text says that the glycerol is "by difference" and also that "the paper determines methanol by difference". Both cannot be by difference, and the fat correction ("the paper's glycerol is by difference, it holds the fat") depends on which one was. I could not read the PDF to check (see Not checked). | low | open | State which quantity Thompson & He measured and which they derived, with the page or table. Re-check the fat subtraction accordingly. |
| 2026-10-28-pfd-lci-review#8 | process.yaml:34-45 | maturity | `maturity: concept` while `cheme maturity` supports none (warning `cheme.maturity-claim-exceeds`). `concept` is the lowest value of the schema enum, and `validation.notes` explains honestly why the sourced and balanced levels fail. The claim is therefore not misleading, but the warning stays. | low | open | Keep the claim. Name the warning in `validation.notes`, and close it when the feed flow basis is accepted as sourced (a rule question already listed in DESIGN.md section 6). |
| 2026-10-28-pfd-lci-review#9 | DESIGN.md section 6, lca/lca.yaml | air emissions | The LCI has no emissions to air. The non-condensable vents of E-302 and the vacuum system carry methanol (S10 is about 10 wt% methanol in the condensate). This is declared as an open item, but there is no placeholder. | low | open | When #2 is fixed, add an ASSUMED vent methanol loss as an elementary flow, or list it as a gap. |
| 2026-10-28-pfd-lci-review#10 | (cheme-as-code tool) | `cheme maturity` model basis | `cheme maturity` prints "V102 equilibrium-stage, predictive, sourced" and "C201/C401 shortcut, predictive, sourced", although no model is declared for them and their outlets are ASSUMED values from the script. The tool output overstates the model basis of three separators. The design files are not affected. | low | open | Report this to cheme-as-code. Do not quote these lines as evidence. |
| 2026-10-28-pfd-lci-review#11 | checks/checks.yaml:76 | template comment | info `cheme.decision-unknown [D-023]`: a template example comment cites D-023, which does not exist here. | low | open | Leave it or reword the example. It is harmless. |

## Previous findings
None: this is the first review record in `processes/glycerol-1/reviews/` (`ls reviews` listed
README.md only).

## Drawing
There are no P&IDs (`pid/` is empty). The BFD and PFD are generated by `cheme process build`, and `cheme validate` printed no `drawing <sheet>:` count line for them. I did not render or read sheet tiles (see Not checked).

## Checked and fine
- **Route and boundary:** classical HCl acidulation, decanting, neutralisation, methanol recovery, dewatering, vacuum distillation, salt removal and carbon bleaching, gate-to-gate. Fat splitting and synthetic glycerol are kept out, as issue #186 asks. The boundary crossings in DESIGN section 1 match the flowsheet's feeds and products.
- **Balances:** I recomputed them by hand.
  - Glycerol: 1317.6 kg/h in, 1246.25 kg/h in product, recovery 94.6 %. The losses add up: 1.81 to FAL, 1.32 to S10, 6.57 to S15, 59.15 to residue, 2.50 to spent carbon.
  - Methanol: 645.8 kg/h plus 37.2 kg/h from NEUT1, of which 9.07 kg/h goes to FAL, 670.6 kg/h to S8 (99.5 %) and 3.37 kg/h to S10.
  - HCl: 1.1 × 1.160 kmol/h gives 145.4 kg/h of 32 % acid. NaOH: 0.116 kmol/h gives 9.28 kg/h of 50 %.
  - NaCl: 74.6 kg/h = 67.8 + 6.8. Water: about 105.6 kg/h.
  - Fatty matter: 97 % to the fatty layer, 5.27 kg/h to the residue.
  - Salt cake: 90 % of the salt plus 0.25 kg/kg liquor gives 83.9 kg/h.
  - `cheme process streams` closes every block and step.
- **Duties against the script's basis:** Q1 is about 477 kW by my estimate (reflux 1.0 × 674 kg/h × 1099 kJ/kg plus sensible heat), against 488.9 kW. Q5 is about 417 kW (1255 kg/h × 923 kJ/kg + 73 kg/h × 2380 + sensible), against 415.1 kW. Q3 is about 42 kW against 40.7 kW. Total heat to cooling water is 803 kWh/t. The order of 760-890 kWh/t matches the cross-check D-012 quotes. Its weak points are #2 and #3.
- **Carbon origin:** fossil 263.1 + 2.5 (activated carbon) = 265.6 kg/h, and biogenic 643.6 kg/h, so the biogenic fraction of the crude carbon is 0.710. This matches D-013 and lca.yaml.
- **LCI:**
  - It is per 1 kg GLYC, after allocation. For example, crude 2201.83/1250 × 0.594 = 1.046 kg, and CW 1003.9/1250 × 0.594 = 0.477 kWh.
  - Mass in equals mass out (2490.5 kg/h), and the elements close (`--coverage`).
  - Every background is `missing:`, with a description of the activity to connect: 13 gaps in `lca/gaps.csv`, none zero-filled.
  - There are no licensed background values: `factors.yaml` has no project factors, and the DESNZ open profile is included but not used.
  - `lca/mappings.yaml` is in the folder with no overrides, and the reason is stated.
- **Wastewater shares:** 1.4 wt% methanol and 3.3 wt% glycerol, matching S10 and S15.
- **Provenance and copying:** every stream value is `given` with a source, `assumed` with a D-id, or `calculated` by propagate. The design basis marks its values ASSUMED. Sources are cited with tables or sections and their licence terms in the DESIGN.md register. I found no copied tables, figures or passages: only single facts in the authors' own words.
- **process.yaml:** honest. It states `publication.status: internal` and `validation.status: unreviewed`, and the notes match the tool results. See #8 for the maturity claim.
- **Scope:** nothing outside `processes/glycerol-1/` changed.

## Not checked
- **Thompson & He (2006) values:** the PDF could not be text-extracted in this session (no poppler). The table values in D-004 (16.16 g, 10.96 g, 0.46 g, 7.98 %, 1.20 wt% Na) and the "by difference" statements (#7) are unverified.
- **The other sources:** I did not open Attarbachi et al. 2024, the Molecules 2026 review, RSC Advances 2022 or the NIST WebBook entries. The facts attributed to them were checked for plausibility only.
- **NaCl solubility in glycerol, and VLE and LLE:** these are not qualified in core. My temperature remarks in #3 are rough Raoult estimates from general glycerol-water boiling data.
- **BFD and PFD drawings:** not rendered or read. No P&IDs, layout, datasheets, control or HAZOP exist at this stage.
- **The library-level LCI build** (`scripts/build_lci.py` at the repository root): not re-run.

Merge: pending. #1 and #2 are open high findings.
