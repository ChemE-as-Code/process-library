---
topic: design
reviewed_commit: ea4cc4fa24d86bd1c5cdd376bf460e418387e375
scope: [DESIGN.md, process.yaml, plant.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/catalysts.yaml, process/flowsheet.yaml, process/simulation.yaml, equipment/equipment-list.yaml, lca/, runs/20261028-145903-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/methylamines-1
merge: pending
---

# Independent review: methylamines-1 concept PFD and preliminary LCI (issue #171, with #166)

Branch `case/methylamines-1`, 7 commits on `origin/main` (35a02b9..ea4cc4f). Concept stage only:
design basis, balanced BFD/PFD with recycles, equipment list, gate-to-gate LCI per kg DMA. No
P&ID or layout was in scope, so the failing basic/detail gates for those are expected. I did not
write this design and changed no design file.

## What I re-ran (at ea4cc4f)

| command | result |
|---|---|
| `git diff --name-only origin/main..HEAD` | every changed file is under `processes/methylamines-1/` |
| `cheme validate` | 18 files, 0 errors, 0 warnings; infos: `cheme.decision-unknown` D-023 (checks.yaml:76), `cheme.catalyst-poison` (SIAL) |
| `cheme check` | concept gates ok except `layout-plot-plan` (out of scope); `design-review` fails (this record); P&ID, layout, datasheet gates fail (out of scope) |
| `cheme maturity` | `sourced` **fail** (`sourced.boundary`: S1/S2 flow and composition not `given` with a source), `balanced` pass, `predictive` fail; **calculation maturity: none**; warning `cheme.maturity-claim-exceeds` at process.yaml:23 |
| `cheme process streams` | every block and step balance ok; RXN extents MMA_SYN 189.06, DMA_SYN 124.66, TMA_SYN 27.07 kmol/h |
| `cheme process propagate --check` | no output, exit 0 (no stale or conflicting calculated values) |
| `cheme assess lca --coverage` | partial screening carbon footprint, 7 gaps, each with a description; mass, element and carbon-origin balance closed |
| `scripts/build_catalog.py --library <root> --out build/catalog` | **exit 1**: 5 errors, all from this process (`unknown chemical` methanol, ammonia, methylamine, dimethylamine, trimethylamine) |

## Checks done by hand

- **Stoichiometry and plant balance.** 2000 kg/h MMA (64.40 kmol/h), 4400 kg/h DMA (97.60), 1600 kg/h TMA
  (27.07): NH3 = 189.07 kmol/h = 3220 kg/h; methyl groups = 340.8 kmol/h = 10 920 kg/h methanol; reaction
  water 340.8 kmol/h = 6140 kg/h. Matches S1, S2, S23 and the LCI balance (14 140 in / 14 140 out kg/h).
- **Recycle loop.** Converter N/C: N = 1031.7 NH3 + 49.5 TMA + 94.8 MMA = 1176 kmol/h; methyl C = 344.7
  MeOH + 94.8 + 3 x 49.5 = 588 kmol/h; N/C = 2.00 as stated. S10 = 842.6 NH3 + 49.5 TMA = 17 276 kg/h,
  5.5 mol% TMA, as stated. Outlet amines 4945/4400/4526 kg/h = 35.6/31.7/32.6 wt %; methanol
  conversion per pass 340.8/344.7 = 98.9 %. All consistent.
- **Reaction heat and adiabatic rise.** Gas-phase heats from the ATcT data in materials.yaml give
  about 2.5 MW; with about 9.6 kg/s and cp about 2.9 kJ/(kg K) the rise is about 90 K vs 88 K
  modelled (625 -> 713 K). Plausible; inlet and outlet inside the sourced 350-450 C window.
- **Duties.** Steam 27 779 (MP) + 8038 (LP) = 35 817 kW; heat to cooling water 38 254 kW. C-101
  condenser 9.0 MW is consistent with R = 1 on about 890 kmol/h NH3-rich distillate. E-101 12.3 MW
  is consistent with vaporising about 34.5 t/h of NH3/methanol/amines. Specific steam is about
  4.5 kWh (16 GJ) per kg amines without heat integration: high, and the design says so (D-009).
- **LCI.** Mass allocation share of DMA 0.55; every per-kg value in lca/inventory.csv reproduces
  from the plant flows (e.g. methanol 10 920.3 x 0.55 / 4400 = 1.365 kg). No zero-filled or licensed
  background value: every background is `missing:` with the activity it should connect to;
  overrides live in the folder's `lca/mappings.yaml` (NH3F, MPS, LPS) and methanol stays a gap.
  lca/factors.yaml is the packaged open profile.
- **Sources and licences.** Source register with locators and read status; values are facts
  (conditions, an equilibrium point) in our own words; no copied tables, figures or passages found
  in DESIGN.md, design-basis.yaml, reactions.yaml, catalysts.yaml or narrative.md.
- **Route and boundary vs issue.** Route (silica-alumina amination with NH3/TMA/MMA recycle and
  NH3 / TMA-extractive / dehydration / MMA-DMA / methanol columns) matches the issue thread; methanol
  and ammonia are boundary feeds from methanol-1 and ammonia-1, co-production with #166 avoids double
  counting as the issue asks. But see R-03 on the separate product cases.

## Findings

Ids follow reviews/README.md (`<file stem>#<n>`); R-01 ... R-11 in the summary are #1 ... #11.

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | process.yaml:30-38 | chemistry slugs | `chemistry` uses five slugs that are not in `chemicals/chemicals.yaml` (methanol, ammonia, methylamine, dimethylamine, trimethylamine). `scripts/build_catalog.py` then exits 1 with five `unknown chemical` errors, all from this process; `.github/workflows/validate.yml:97,100` runs that build, so merging this branch breaks the library's CI. The "PENDING REGISTRY" comment and D-013 document the gap but do not stop the failure. CONTRIBUTING step 3 asks for new registry entries in the same change; ammonia-1 instead leaves unregistered chemicals out of `chemistry` and names them in a note. | high | open | Either add the five registry entries (CAS, InChIKey, ChEBI; anhydrous liquefied grades) in this PR, or, like ammonia-1, drop the unregistered entries from `chemistry` and record them in a note until the registry PR lands. Re-run `build_catalog.py` to exit 0. |
| 2026-10-28-pfd-lci-review#2 | process.yaml:23; runs/20261028-145903-design/report.md | maturity claim | process.yaml claims `maturity: concept`, but `cheme maturity` finds calculation maturity **none** (`sourced.boundary` fails: S1/S2 flow and composition are `assumed`, not `given` with a source) and warns `cheme.maturity-claim-exceeds`. CONTRIBUTING step 2 caps the claim by that evaluation, and there is no `checks/maturity.json`. The run report says `cheme maturity` "stops at balanced", which is wrong: it stops at none. The engineering content is concept level, so the gap is in provenance, not substance. | medium | open | Give S1/S2 flow and composition `provenance: given` with source "design basis capacity and slate (D-002, D-003), stoichiometric" (the capacity is a design specification, kept ASSUMED in design-basis.yaml), re-run `cheme maturity` to reach balanced and write `checks/maturity.json`; or lower the claim. Fix the statement in DESIGN/PROGRESS (the run record is not edited). |
| 2026-10-28-pfd-lci-review#3 | lca/lca.yaml:19-23 | functional unit | This is the case of issue #171 (methylamine), and the issue thread asks to "preserve separate product cases" when co-producing with #166. The only functional unit is 1 kg DMA, and nowhere is an MMA (or TMA) result stated. Under mass allocation the per-kg inventory of MMA equals that of DMA, but a reader of #171 has to work that out. | medium | open | Add a statement (DESIGN D-014 and lca/README.md) that under mass allocation the inventory per kg MMA and per kg TMA is identical to the per-kg-DMA one, or add an MMA functional unit or scenario so that #171 has its own product case. |
| 2026-10-28-pfd-lci-review#4 | DESIGN.md:98-117 (D-005) | equilibrium check basis | The only validation of the reaction model compares the model's **mass** fractions (0.326/0.302/0.372) with SR-2's 0.288/0.279/0.433, whose basis is "by weight, as far as the summary shows". If SR-2 gives mole fractions, the model's mole fractions (0.447/0.285/0.268) miss TMA by about 16 points, not 6, and the recycle flows and steam that follow from them would be much further off. The basis of the one benchmark is not confirmed. | medium | open | Read the passage of US 4,485,261 A and record its basis (weight or mole), temperature and N/C with the locator; restate the deviation in D-005 and design-basis.yaml. |
| 2026-10-28-pfd-lci-review#5 | DESIGN.md:47,52-54 | source read status | Decisions rest on sources that were not read: SR-6 (separation sequence and caustic dosing, D-008), SR-7 (NH3-TMA constant-boiling mixture, the basis of the TMA recycle in D-007) and SR-8 are "search summary only (not fetched)"; SR-1 is abstract only and is the source of the "demand is DMA" claim behind the slate (D-002). The register is honest about this, but the issue asks for numerical inputs with exact locators, and a search snippet is not a locator. | medium | open | Fetch and summarise US 7,309,403 B2 and US 2,206,584 A with section locators (or find another open source for the NH3-TMA azeotrope); until then mark D-007 and D-008 as resting on unverified summaries. |
| 2026-10-28-pfd-lci-review#6 | lca/results.csv:2; lca/results.md (Allocation table) | zero totals | Every exchange is a gap, but results.csv has `baseline,climate-change,...,total,...,0` with no status, and the results.md allocation table shows `0` kg CO2-eq for mass (used) and none. The headline row correctly says "no total", but a machine reader of the CSV or a reader of the allocation table sees a zero footprint. These are generated by cheme (`assess lca --write`). | medium | open | Report to core (a total with every contribution a gap should be empty or flagged, not 0). Until then, say in lca/README.md that the 0 in results.csv and the allocation table means "no total". |
| 2026-10-28-pfd-lci-review#7 | process/flowsheet.yaml (C101-C105); `cheme maturity` model basis | column model basis | `cheme maturity` lists C101-C105 as "shortcut, predictive, sourced" and passes `balanced.model-basis`, although the columns have no model: their outlets are ASSUMED sharp-split stream values from scripts/mass_balance.py (D-006, D-008). DESIGN.md is correct, but the tool output that the report quotes overstates the basis. | low | open | Report to core (Distilling steps without specs should not be classed as sourced shortcut models); note it in D-011. |
| 2026-10-28-pfd-lci-review#8 | DESIGN.md:126-128 (D-006); stream S23 | energy cross-check | The cross-check "steam 35.8 + reaction 2.5 = 38.3 MW rejected, within 0.1 MW" uses the gas-phase heat of reaction, while the feeds enter liquid and the products and water leave liquid. On a liquid basis the heat of reaction is roughly 3.4 MW (reviewer estimate from heats of vaporisation), and the wastewater leaves at 393 K, carrying about 0.7 MW that is in neither CW nor any duty. The close agreement is fortuitous. Hot wastewater to biological treatment also needs a cooler, which would add about 2 % to the CW exchange of the LCI. | low | open | Restate the cross-check on a consistent basis. Add a wastewater cooler duty, or cool S23 within an existing duty, and state it. |
| 2026-10-28-pfd-lci-review#9 | lca/lca.yaml (feed:MPS, feed:LPS); DESIGN.md D-009 | steam figure caveat | Specific steam (about 4.5 kWh/kg amines) is not compared with any published consumption, and the "upper estimate, no heat integration" caveat sits only in D-009, not in the source text of the steam exchanges, which travels with the dataset. | low | open | Add "upper estimate, no heat integration (D-009)" to the MPS and LPS exchange sources; benchmark against an open specific consumption when one is found (O-3). |
| 2026-10-28-pfd-lci-review#10 | process/reactions.yaml:8 | uncited source | "Corbin et al. 1997 as cited in US 7,754,921" names a patent that is in neither the source register nor `references:`. | low | open | Add US 7,754,921 to the register with its read status and locator, or drop the citation. |
| 2026-10-28-pfd-lci-review#11 | checks/checks.yaml:76 | stale decision id | Cites D-023, which DESIGN.md does not have (`cheme.decision-unknown` info; a leftover from the template). | low | open | Point it at the matching decision or remove the reference. |

## Previous findings

None (first review of this process).

## Summary

The balance is sound: I reproduced the stoichiometry, the recycle loop, the N/C ratio, the
per-pass distribution, the reaction heat, the adiabatic rise and every per-kg LCI value. The
design is open about its assumptions, gaps and method limits, and nothing outside the process
folder changed. One finding is high: R-01 (#1), the unregistered chemical slugs that make the
library catalog build, and so CI, fail on merge. The medium findings are about honesty and
traceability: a maturity claim above what `cheme maturity` supports (R-02), no MMA product case
for #171 (R-03), an unconfirmed basis for the one equilibrium benchmark (R-04), decisions resting
on unread sources (R-05), and zero totals in the generated LCA results (R-06). None of them breaks the balance.

Merge is pending: #1 must be closed first.
